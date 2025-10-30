"""
AutoCAD 自动化工作流程 - 数据库配置版

支持从数据库读取配置参数

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import win32com.client
import pywintypes
import psutil
import time
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
from src.models.autocad_config import AutoCADConfig
from src.utils.image_processing import preprocess_images, combine_ocr_results


class ConfigurableAutoCADWorkflow:
    """
    基于数据库配置的 AutoCAD 自动化工作流程

    支持从数据库读取所有配置参数
    """

    def __init__(self, config: Optional[AutoCADConfig] = None,
                 config_name: Optional[str] = None,
                 config_id: Optional[int] = None,
                 task_id: Optional[str] = None,
                 task_service: Optional['DWGTaskService'] = None):
        """
        初始化工作流程

        Args:
            config: 配置对象（直接传入）
            config_name: 配置名称（从数据库查询）
            config_id: 配置ID（从数据库查询）
            task_id: DWG任务ID（用于记录步骤日志）
            task_service: DWG任务服务（用于记录步骤日志）
        """
        self.acad = None
        self.current_doc = None
        self.current_file = None
        self.task_log_id = None
        self.dwg_task_id = task_id  # DWG任务ID
        self.dwg_task_service = task_service  # DWG任务服务

        # 缓存窗口坐标（用于连续OCR操作）
        self.cached_window_rect = None  # (left, top, right, bottom)
        self.cached_hwnd = None  # 窗口句柄

        # 加载配置
        if config:
            self.config = config
        else:
            db = SessionLocal()
            try:
                service = AutoCADConfigService(db)
                self.config = service.get_config(config_id=config_id, config_name=config_name)
                if not self.config:
                    raise ValueError(f"Config not found: id={config_id}, name={config_name}")
            finally:
                db.close()

        print(f"✅ 已加载配置: {self.config.config_name}")
        print(f"   描述: {self.config.description}")

    def run(self, dwg_file_path: Optional[str] = None) -> bool:
        """
        运行完整的自动化流程

        Args:
            dwg_file_path: DWG 文件路径（可选，默认使用配置中的路径）

        Returns:
            True 表示成功，False 表示失败
        """
        # 确定文件路径
        file_path = dwg_file_path or self.config.dwg_file_path
        if not file_path:
            print("❌ 错误：未指定 DWG 文件路径")
            return False

        print("\n" + "=" * 80)
        print("AutoCAD 自动化工作流程（数据库配置）")
        print("=" * 80)
        print(f"配置: {self.config.config_name}")
        print(f"文件: {file_path}")
        print("=" * 80)

        # 步骤 0: 清理输出目录（如果启用）
        if self.config.output_dir_cleanup_enabled:
            if not self._cleanup_output_directory():
                print("⚠️ 警告：输出目录清理失败（继续执行）")

        # 记录任务开始
        db = SessionLocal()
        try:
            service = AutoCADConfigService(db)
            task_log = service.log_task_start(
                config_id=self.config.id,
                task_name=f"Process {Path(file_path).name}",
                dwg_file=file_path
            )
            self.task_log_id = task_log.id
        except Exception as e:
            print(f"⚠️ 警告：无法记录任务日志: {e}")
        finally:
            db.close()

        try:
            # 步骤 1: 关闭并打开
            if not self.step1_close_and_open_cad(file_path):
                self._log_task_end('failed', '步骤1失败：无法打开CAD和文件')
                return False

            # 步骤 2: 验证加载
            if not self.step2_verify_file_loaded():
                self._log_task_end('failed', '步骤2失败：文件未正确加载')
                return False

            # 步骤 3: 执行菜单操作
            if self.config.menu_operations:
                if not self.step3_execute_operations():
                    print("\n⚠️ 警告：菜单操作失败（但文件已成功打开）")

            # 步骤 4: 监控输出文件生成（如果提取到了文件数量）
            if hasattr(self, 'extracted_data') and 'total_pages' in self.extracted_data:
                try:
                    total_pages = int(self.extracted_data['total_pages'])
                    print(f"\n📋 检测到提取的文件数量: {total_pages}")

                    # 启动文件监控（支持多种文件格式）
                    monitoring_success = self.monitor_output_files(
                        expected_count=total_pages,
                        check_interval=1.0,  # 每秒检查一次
                        max_wait_time=600.0,  # 最多等待10分钟
                        file_pattern="*.*"  # 监控所有文件（包括PDF/DWF/PLT等）
                    )

                    if not monitoring_success:
                        print("\n⚠️ 警告：输出文件监控超时或失败")
                except (ValueError, TypeError) as e:
                    print(f"\n⚠️ 警告：无法解析文件数量: {e}")

            print("\n" + "=" * 80)
            print("✅ 自动化流程完成！")
            print("=" * 80)

            self._log_task_end('success')

            # 检查是否需要关闭CAD进程
            if self.config.close_cad_after_completion:
                print("\n📋 配置启用任务完成后关闭CAD")
                print("▶" * 40)
                print("关闭 AutoCAD 进程")
                print("▶" * 40)

                closed_count = self._close_all_autocad_processes()
                print(f"✅ CAD进程已关闭（处理了 {closed_count} 个进程）")
            else:
                print("\n📋 配置未启用任务完成后关闭CAD，保持CAD运行")

            return True

        except Exception as e:
            print(f"\n❌ 流程失败: {e}")
            self._log_task_end('failed', str(e))
            return False

    def step1_close_and_open_cad(self, dwg_file_path: str) -> bool:
        """步骤 1: 关闭并打开 CAD"""
        print("\n" + "▶" * 40)
        print("步骤 1: 关闭现有 CAD 并打开指定文件")
        print("▶" * 40)

        # 验证文件
        dwg_path = Path(dwg_file_path)
        if not dwg_path.exists():
            print(f"❌ 文件不存在: {dwg_file_path}")
            return False

        print(f"📄 原始文件: {dwg_file_path}")

        # 检查是否需要复制到工作目录
        if self.config.copy_to_working_dir and self.config.working_directory:
            print(f"\n📋 配置启用文件复制到工作目录")
            print(f"   工作目录: {self.config.working_directory}")

            # 创建工作目录（如果不存在）
            working_dir = Path(self.config.working_directory)
            working_dir.mkdir(parents=True, exist_ok=True)

            # 复制文件到工作目录
            import shutil
            working_file_path = working_dir / dwg_path.name
            print(f"   正在复制文件...")
            print(f"   源: {dwg_path}")
            print(f"   目标: {working_file_path}")

            try:
                shutil.copy2(str(dwg_path), str(working_file_path))
                file_size = working_file_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   ✅ 文件已复制 ({file_size:.2f} MB)")

                # 使用工作目录中的文件
                self.current_file = str(working_file_path.absolute())
                print(f"   📂 将使用工作目录中的文件")
            except Exception as e:
                print(f"   ❌ 复制文件失败: {e}")
                print(f"   ⚠️  将使用原始文件路径")
                self.current_file = str(dwg_path.absolute())
        else:
            # 不复制，直接使用原始文件
            self.current_file = str(dwg_path.absolute())

        print(f"🎯 最终使用文件: {self.current_file}")

        # 关闭现有进程
        if self.config.force_close_existing:
            print("\n🔍 检查现有 AutoCAD 进程...")
            if self._is_autocad_running():
                closed_count = self._close_all_autocad_processes()
                print(f"✅ 关闭流程完成（处理了 {closed_count} 个进程）")
            else:
                print("  ✅ 没有运行中的AutoCAD进程")

        # 启动 AutoCAD（带重试机制和多种启动策略）
        print(f"\n🚀 启动 AutoCAD...")
        max_start_retries = 3

        # 在开始前初始化COM
        try:
            import pythoncom
            pythoncom.CoInitialize()
            print("  ✅ COM 已初始化")
        except:
            pass

        # 定义多种启动策略
        startup_strategies = [
            ('DispatchEx', 'win32com.client.DispatchEx', '创建新的AutoCAD实例'),
            ('EnsureDispatch', 'win32com.client.gencache.EnsureDispatch', '确保类型库并创建实例'),
            ('Subprocess+GetObject', 'subprocess+GetActiveObject', '先用subprocess启动再连接'),
            ('Dispatch', 'win32com.client.Dispatch', '标准Dispatch方式')
        ]

        for start_attempt in range(max_start_retries):
            # 重试前清理
            if start_attempt > 0:
                print(f"\n  [重试 {start_attempt}/{max_start_retries}]")
                print("  🧹 清理COM缓存...")

                try:
                    import pythoncom
                    pythoncom.CoUninitialize()
                    time.sleep(2)
                    pythoncom.CoInitialize()
                    print("  ✅ COM 已重新初始化")
                except Exception as e:
                    print(f"  ⚠️ COM清理警告: {e}")

                # 再次检查是否有残留进程
                if self._is_autocad_running():
                    print("  ⚠️ 发现残留进程，再次关闭...")
                    self._close_all_autocad_processes()
                    time.sleep(3)

                print(f"  ⏳ 等待 5 秒后重试...")
                time.sleep(5)

            # 尝试每种启动策略
            for strategy_name, strategy_method, strategy_desc in startup_strategies:
                try:
                    print(f"  尝试 {start_attempt + 1}/{max_start_retries} - 策略: {strategy_name}")
                    print(f"    💡 {strategy_desc}")

                    if strategy_method == 'subprocess+GetActiveObject':
                        # 策略3: 先用subprocess启动AutoCAD.exe，再连接
                        import subprocess

                        # 查找AutoCAD可执行文件
                        acad_exe = self.config.autocad_exe_path or r"C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

                        print(f"    🔧 启动进程: {acad_exe}")
                        subprocess.Popen([acad_exe], shell=False)

                        print(f"    ⏳ 等待AutoCAD启动（10秒）...")
                        time.sleep(10)

                        # 连接到已启动的实例
                        print(f"    🔌 连接到运行中的实例...")
                        self.acad = win32com.client.GetActiveObject("AutoCAD.Application")

                    elif strategy_method == 'win32com.client.DispatchEx':
                        # 策略1: DispatchEx - 强制创建新实例
                        self.acad = win32com.client.DispatchEx("AutoCAD.Application")

                    elif strategy_method == 'win32com.client.gencache.EnsureDispatch':
                        # 策略2: EnsureDispatch - 确保类型库
                        self.acad = win32com.client.gencache.EnsureDispatch("AutoCAD.Application")

                    else:
                        # 策略4: 标准Dispatch
                        self.acad = win32com.client.Dispatch("AutoCAD.Application")

                    # 设置可见并验证
                    self.acad.Visible = True
                    _ = self.acad.Name  # 测试访问

                    print(f"    ✅ 成功！使用策略: {strategy_name}")
                    print(f"✅ AutoCAD 已启动 (版本: {self.acad.Name})")
                    break

                except Exception as e:
                    print(f"    ⚠️ 策略失败: {e}")
                    self.acad = None
                    continue

            # 检查是否成功启动
            if self.acad is not None:
                break

        # 所有策略都失败
        if self.acad is None:
            print(f"\n❌ 所有启动策略均失败（已尝试 {len(startup_strategies)} 种方法 × {max_start_retries} 次重试）")
            print("\n📋 可能的原因和解决方案：")
            print("   1. AutoCAD未正确安装或COM接口未注册")
            print("      解决：重新安装AutoCAD或以管理员身份运行注册")
            print("   2. 权限不足")
            print("      解决：以管理员身份运行API服务")
            print("   3. AutoCAD许可证问题")
            print("      解决：检查AutoCAD许可证是否有效")
            print("   4. 防病毒软件阻止")
            print("      解决：将AutoCAD和Python添加到白名单")
            return False

        # 等待就绪（使用配置的时间）
        try:
            print(f"⏳ 等待 AutoCAD 初始化（最多 {self.config.startup_wait_time} 秒）...")
            max_checks = int(self.config.startup_wait_time / self.config.startup_check_interval)

            for i in range(max_checks):
                try:
                    _ = self.acad.Name
                    print(f"  ✅ 已就绪（{(i + 1) * self.config.startup_check_interval:.1f} 秒后）")
                    break
                except:
                    print(f"  ⏳ 等待中... ({(i + 1) * self.config.startup_check_interval:.1f}/{self.config.startup_wait_time} 秒)")
                    time.sleep(self.config.startup_check_interval)

            # 额外等待
            if self.config.post_startup_wait > 0:
                print(f"⏳ 额外等待 {self.config.post_startup_wait} 秒...")
                time.sleep(self.config.post_startup_wait)

            # 打开文件（使用配置的重试参数）
            print(f"\n📂 打开文件...")
            for attempt in range(self.config.file_open_max_retries):
                try:
                    self.current_doc = self.acad.Documents.Open(self.current_file)
                    print(f"✅ 文件已打开: {self.current_doc.Name}")
                    return True
                except Exception as e:
                    if attempt < self.config.file_open_max_retries - 1:
                        print(f"  ⚠️ 尝试 {attempt + 1}/{self.config.file_open_max_retries} 失败: {e}")
                        print(f"  ⏳ 等待 {self.config.file_open_retry_delay} 秒后重试...")
                        time.sleep(self.config.file_open_retry_delay)
                    else:
                        raise e

        except Exception as e:
            print(f"❌ 失败: {e}")
            return False

    def step2_verify_file_loaded(self) -> bool:
        """步骤 2: 验证文件加载"""
        print("\n" + "▶" * 40)
        print("步骤 2: 验证文件已加载")
        print("▶" * 40)

        print(f"⏳ 最大等待: {self.config.verification_wait_time} 秒")
        print(f"🔄 检查间隔: {self.config.verification_check_interval} 秒")

        start_time = time.time()
        check_count = 0

        while time.time() - start_time < self.config.verification_wait_time:
            check_count += 1
            elapsed = time.time() - start_time

            print(f"\n🔍 检查 #{check_count} (已用时: {elapsed:.1f}秒)...")

            try:
                # 检查进程
                if not self._is_autocad_running():
                    print("❌ AutoCAD 进程已关闭")
                    return False
                print("  ✅ AutoCAD 进程运行中")

                # 检查文档
                doc_name = self.current_doc.Name
                print(f"  ✅ 文档打开: {doc_name}")

                # 检查模型空间
                entity_count = self.current_doc.ModelSpace.Count
                print(f"  ✅ 模型空间实体数: {entity_count}")

                print("\n✅ 文件验证成功！")
                return True

            except:
                print(f"  ⏳ 等待中...")
                time.sleep(self.config.verification_check_interval)

        print(f"\n❌ 超时：{self.config.verification_wait_time} 秒内未加载")
        return False

    def step3_execute_operations(self) -> bool:
        """步骤 3: 执行菜单操作"""
        print("\n" + "▶" * 40)
        print("步骤 3: 执行菜单操作")
        print("▶" * 40)

        try:
            operations = json.loads(self.config.menu_operations) if isinstance(
                self.config.menu_operations, str) else self.config.menu_operations

            if not operations:
                print("  （无配置的操作）")
                return True

            for i, op in enumerate(operations, 1):
                print(f"\n📋 操作 {i}/{len(operations)}: {op.get('type')}")

                # 检查是否是连续的OCR菜单操作
                is_current_ocr_menu = (op.get('type') == 'menu' and op.get('method') == 'ocr')
                is_next_ocr_menu = False
                if i < len(operations):
                    next_op = operations[i]
                    is_next_ocr_menu = (next_op.get('type') == 'menu' and next_op.get('method') == 'ocr')

                if op.get('type') == 'command':
                    # 执行AutoCAD命令
                    command = op.get('command', '')
                    self.current_doc.SendCommand(f"._{command} ")
                    print(f"  ✅ 已执行命令: {command}")

                    wait_time = op.get('wait_time', 1.0)
                    time.sleep(wait_time)

                elif op.get('type') == 'menu':
                    # 点击菜单项
                    method = op.get('method', 'auto')  # 默认自动判断

                    if method == 'image':
                        # 方式3：使用图像识别（适合自绘菜单）
                        print(f"  [模式] 图像识别")
                        icon_path = op.get('icon_path', '')
                        confidence = op.get('confidence', 0.8)

                        if not icon_path:
                            print(f"  ⚠️ 跳过：未指定图标路径")
                            continue

                        success = self._click_menu_by_image(icon_path, confidence)
                        if not success:
                            print(f"  ⚠️ 图像识别失败")

                    elif method == 'ocr':
                        # 方式4：使用OCR文字识别（最智能）
                        print(f"  [模式] OCR文字识别")
                        text = op.get('text', '')

                        if not text:
                            print(f"  ⚠️ 跳过：未指定文本")
                            continue

                        # 传递是否有下一个OCR菜单操作的信息
                        success = self._click_menu_by_ocr(text, keep_menu_open=is_next_ocr_menu)
                        if not success:
                            print(f"  ⚠️ OCR识别失败")

                    else:
                        # 自动判断模式（keyboard/mouse）
                        menu_path = op.get('path', [])
                        if not menu_path:
                            print(f"  ⚠️ 跳过：菜单路径为空")
                            continue

                        # 判断使用键盘还是鼠标方式
                        # 如果菜单项有快捷键标识(H)，使用键盘
                        # 否则使用pywinauto鼠标点击
                        has_shortcut = any('(' in item and ')' in item for item in menu_path)

                        if has_shortcut:
                            # 方式1：使用快捷键（适合有(H)标识的菜单）
                            print(f"  [模式] 键盘快捷键")
                            self._click_menu_by_keyboard(menu_path)
                        else:
                            # 方式2：使用鼠标点击（适合无快捷键的菜单）
                            print(f"  [模式] 鼠标点击")
                            self._click_menu_by_mouse(menu_path)

                    wait_time = op.get('wait_time', 1.0)
                    time.sleep(wait_time)

                elif op.get('type') == 'screenshot_extract':
                    # 方式5：全屏截图+OCR文本提取（用于提取动态数据）
                    print(f"  [模式] 截图文本提取")
                    target_pattern = op.get('target_pattern', '')
                    save_to = op.get('save_to', 'extracted_value')
                    required = op.get('required', False)

                    if not target_pattern:
                        print(f"  ⚠️ 跳过：未指定提取模式")
                        continue

                    # 执行全屏OCR提取
                    success, extracted_value = self._screenshot_and_extract(target_pattern, save_to)

                    if success:
                        print(f"  ✅ 提取成功: {save_to} = {extracted_value}")
                    else:
                        print(f"  ⚠️ 提取失败: 未找到匹配的文本")
                        if required:
                            print(f"  ❌ 该字段为必填项，操作失败")
                            return False

                    wait_time = op.get('wait_time', 1.0)
                    time.sleep(wait_time)

                else:
                    print(f"  ⚠️ 跳过：未知操作类型 '{op.get('type')}'")

            print("\n✅ 菜单操作完成")
            return True

        except Exception as e:
            print(f"❌ 菜单操作失败: {e}")
            return False

    def _click_menu_by_keyboard(self, menu_path: list) -> bool:
        """使用键盘快捷键点击菜单"""
        try:
            import win32gui
            import win32com.client

            # 提取快捷键字母
            keys = []
            for menu_item in menu_path:
                # 提取括号中的快捷键，如 "帮助(H)" -> "H"
                if '(' in menu_item and ')' in menu_item:
                    shortcut = menu_item[menu_item.rfind('(')+1:menu_item.rfind(')')]
                    keys.append(shortcut)

            if not keys:
                print(f"  ⚠️ 未找到快捷键")
                return False

            # 查找AutoCAD窗口
            def find_autocad_window(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'AutoCAD' in title or 'acad' in title.lower():
                        param.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(find_autocad_window, windows)

            if not windows:
                print(f"  ⚠️ 未找到AutoCAD窗口")
                return False

            # 激活窗口
            win32gui.SetForegroundWindow(windows[0])
            time.sleep(0.3)

            # 发送快捷键
            shell = win32com.client.Dispatch("WScript.Shell")

            # Alt+第一个键打开菜单
            shell.SendKeys(f"%{keys[0]}")
            time.sleep(0.3)

            # 后续的键
            for key in keys[1:]:
                shell.SendKeys(key)
                time.sleep(0.2)

            print(f"  ✅ 已点击菜单: {' > '.join(menu_path)}")
            return True

        except Exception as e:
            print(f"  ❌ 键盘方式失败: {e}")
            return False

    def _click_menu_by_mouse(self, menu_path: list) -> bool:
        """使用鼠标点击菜单（适合无快捷键的菜单）"""
        try:
            from pywinauto import Desktop
            from pywinauto.findwindows import ElementNotFoundError
            import win32gui

            # 查找AutoCAD窗口
            def find_autocad_window(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'AutoCAD' in title or 'acad' in title.lower():
                        param.append((hwnd, title))
                return True

            windows = []
            win32gui.EnumWindows(find_autocad_window, windows)

            if not windows:
                print(f"  ⚠️ 未找到AutoCAD窗口")
                return False

            hwnd, title = windows[0]
            print(f"  找到窗口: {title} (HWND={hwnd})")

            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)

            # 使用pywinauto连接窗口
            try:
                desktop = Desktop(backend="uia")
                app_window = desktop.window(handle=hwnd)

                # 逐级查找并点击菜单
                current_menu = app_window
                for i, menu_name in enumerate(menu_path):
                    print(f"  [{i+1}/{len(menu_path)}] 查找菜单: {menu_name}")

                    # 尝试多种控件类型和搜索策略
                    menu_item = None
                    search_strategies = [
                        # 策略1: MenuItem精确匹配
                        {"title": menu_name, "control_type": "MenuItem"},
                        # 策略2: Button精确匹配（Ribbon界面）
                        {"title": menu_name, "control_type": "Button"},
                        # 策略3: TabItem精确匹配（选项卡）
                        {"title": menu_name, "control_type": "TabItem"},
                        # 策略4: MenuItem模糊匹配
                        {"title_re": f".*{menu_name}.*", "control_type": "MenuItem"},
                        # 策略5: Button模糊匹配
                        {"title_re": f".*{menu_name}.*", "control_type": "Button"},
                        # 策略6: 仅通过标题搜索（不限控件类型）
                        {"title": menu_name},
                        # 策略7: 模糊标题搜索（不限控件类型）
                        {"title_re": f".*{menu_name}.*"},
                    ]

                    for strategy_idx, strategy in enumerate(search_strategies, 1):
                        try:
                            test_item = current_menu.child_window(**strategy)
                            if test_item.exists():
                                menu_item = test_item
                                ctrl_type = strategy.get('control_type', '任意类型')
                                match_type = '精确' if 'title' in strategy else '模糊'
                                print(f"  ✅ [策略{strategy_idx}] 找到控件: {menu_item.window_text()} ({ctrl_type}/{match_type})")
                                break
                        except:
                            continue

                    if menu_item:
                        try:
                            menu_item.click_input()
                            time.sleep(0.5)
                            current_menu = menu_item
                        except Exception as e:
                            print(f"  ⚠️ 点击失败: {e}")
                            # 尝试其他点击方式
                            try:
                                menu_item.click()
                                time.sleep(0.5)
                                current_menu = menu_item
                                print(f"  ✅ 使用备用点击方式成功")
                            except Exception as e2:
                                print(f"  ❌ 备用点击也失败: {e2}")
                                return False
                    else:
                        print(f"  ❌ 所有策略均未找到: {menu_name}")
                        print(f"  提示: 运行 scripts/inspect_autocad_ui.py 检查UI结构")
                        return False

                print(f"  ✅ 已点击菜单: {' > '.join(menu_path)}")
                return True

            except Exception as e:
                print(f"  ❌ pywinauto操作失败: {e}")
                return False

        except ImportError:
            print(f"  ❌ 缺少pywinauto库，请安装: pip install pywinauto")
            return False
        except Exception as e:
            print(f"  ❌ 鼠标方式失败: {e}")
            return False

    def _click_menu_by_image(self, icon_path: str, confidence: float = 0.8) -> bool:
        """使用图像识别点击菜单（适合自绘菜单）"""
        try:
            import pyautogui
            import numpy as np
            import cv2
            import win32gui
        except ImportError:
            print(f"  ❌ 缺少必要的库，请安装: pip install pyautogui opencv-python numpy")
            return False

        # 解析路径（支持相对路径）
        icon_file = Path(icon_path)
        if not icon_file.is_absolute():
            # 相对于项目根目录
            project_root = Path(__file__).parent.parent.parent
            icon_file = project_root / icon_path

        if not icon_file.exists():
            print(f"  ❌ 图标文件不存在: {icon_file}")
            return False

        print(f"  图标: {icon_file.name}")
        print(f"  置信度: {confidence}")

        try:
            # 激活AutoCAD窗口
            def find_autocad_window(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'AutoCAD' in title or 'acad' in title.lower():
                        param.append((hwnd, title))
                return True

            windows = []
            win32gui.EnumWindows(find_autocad_window, windows)

            if windows:
                hwnd, title = windows[0]
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)

            # 读取图标（处理中文路径）
            with open(icon_file, 'rb') as f:
                file_bytes = np.frombuffer(f.read(), np.uint8)

            icon_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            if icon_img is None:
                print(f"  ❌ 无法解码图像文件")
                return False

            # 转换为RGB
            icon_img_rgb = cv2.cvtColor(icon_img, cv2.COLOR_BGR2RGB)

            # 在屏幕上查找图标
            location = pyautogui.locateOnScreen(icon_img_rgb, confidence=confidence)

            if location:
                center_x = location.left + location.width // 2
                center_y = location.top + location.height // 2

                print(f"  ✅ 找到图标位置: ({center_x}, {center_y})")

                # 移动鼠标并点击
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                time.sleep(0.2)
                pyautogui.click()

                print(f"  ✅ 已点击图标")
                return True
            else:
                print(f"  ❌ 未找到图标（置信度{confidence}）")
                print(f"  提示: 尝试降低置信度或重新截取图标")
                return False

        except Exception as e:
            print(f"  ❌ 图像识别失败: {e}")
            return False

    def _click_menu_by_ocr(self, text: str, keep_menu_open: bool = False) -> bool:
        """
        使用OCR文字识别点击菜单（最智能方案）

        Args:
            text: 要查找的菜单文本
            keep_menu_open: 如果为True，点击后不移动鼠标（保持菜单展开状态，用于连续菜单操作）

        Returns:
            是否成功
        """
        # ============================================================================
        # 初始化日志记录和文件管理
        # ============================================================================
        import time as time_module
        from src.utils.ocr_file_manager import OCRFileManager
        from src.services.ocr_logging_service import OCRLoggingService

        # 时间记录
        total_start_time = time_module.time()
        screenshot_time = 0.0
        preprocessing_time = 0.0
        ocr_time = 0.0
        merge_time = 0.0

        # 日志记录初始化
        recognition_log_id = None
        ocr_logging_service = None
        preprocessing_performance_data = []  # 存储每个方法的性能数据

        # OCR结果统计
        found = False
        matched_text = None
        confidence = None
        matched_version = None
        position_x = None
        position_y = None
        total_texts_found = 0
        unique_texts_count = 0
        screenshot_dir = None
        screenshots_saved = 0

        try:
            import pyautogui
            import numpy as np
            import win32gui
            import win32ui
            import win32con
            from ctypes import windll
            from PIL import Image
        except ImportError:
            print(f"  ❌ 缺少必要的库")
            return False

        # 导入OCR库（优先级：Umi-OCR > Tesseract > EasyOCR > PaddleOCR）
        # Umi-OCR基于PaddleOCR，识别质量最好且无需安装
        ocr_type = None
        umi_ocr_base_url = None
        umi_ocr_api_url = None
        umi_ocr_timeout = 30

        # 优先尝试Umi-OCR（局域网HTTP服务）
        # 从配置读取 Umi-OCR 服务地址
        if self.config.umi_ocr_enabled:
            try:
                import requests

                # 从配置获取 Umi-OCR 地址
                umi_ocr_base_url = self.config.umi_ocr_service_url or "http://10.3.19.121:1224"
                umi_ocr_api_path = self.config.umi_ocr_api_path or "/api/ocr"
                umi_ocr_timeout = self.config.umi_ocr_timeout or 30
                umi_ocr_limit_side_len = self.config.umi_ocr_limit_side_len or 2880

                # 拼接完整API URL
                if not umi_ocr_base_url.endswith('/'):
                    umi_ocr_base_url += '/'
                if umi_ocr_api_path.startswith('/'):
                    umi_ocr_api_path = umi_ocr_api_path[1:]
                umi_ocr_api_url = umi_ocr_base_url.rstrip('/') + '/' + umi_ocr_api_path.lstrip('/')

                # 测试Umi-OCR服务是否可用
                test_url = umi_ocr_base_url.rstrip('/') + '/'
                test_response = requests.get(test_url, timeout=2)
                if test_response.status_code == 200:
                    ocr_type = 'umi-ocr'
                    print(f"  ✅ 使用Umi-OCR服务: {umi_ocr_api_url}")
                    print(f"     超时设置: {umi_ocr_timeout}秒")
                    print(f"     图像边长限制: {umi_ocr_limit_side_len}px")
            except Exception as e:
                print(f"  ⚠️ Umi-OCR服务连接失败: {e}")
                print(f"     尝试连接: {umi_ocr_base_url if umi_ocr_base_url else 'N/A'}")
                pass  # Umi-OCR不可用，尝试其他方案

        # 备选方案：本地OCR库
        if not ocr_type:
            try:
                import pytesseract
                ocr_type = 'tesseract'
            except ImportError:
                try:
                    import easyocr
                    ocr_type = 'easyocr'
                except ImportError:
                    try:
                        from paddleocr import PaddleOCR
                        ocr_type = 'paddleocr'
                    except ImportError:
                        print(f"  ❌ 缺少OCR库，请安装以下之一:")
                        print(f"     推荐：使用局域网Umi-OCR服务 (http://10.3.19.121:1224/)")
                        print(f"     或安装本地OCR库:")
                        print(f"       pip install pytesseract  (中文UI识别佳)")
                        print(f"       pip install easyocr  (轻量)")
                        print(f"       pip install paddleocr paddlepaddle  (最准确但体积大)")
                        return False

        print(f"  查找文本: '{text}'")

        try:
            # ============================================================================
            # 查找并定位 AutoCAD 窗口
            # ============================================================================
            # 查找AutoCAD窗口
            def find_autocad_window(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'AutoCAD' in title or 'acad' in title.lower():
                        param.append((hwnd, title))
                return True

            # 判断是否需要重新查找窗口和获取坐标
            # 只在第一次OCR时查找窗口，后续都使用缓存坐标（保持菜单展开）
            need_refresh_window = self.cached_window_rect is None

            if need_refresh_window:
                # 第一次OCR，需要查找并激活窗口
                windows = []
                win32gui.EnumWindows(find_autocad_window, windows)

                if not windows:
                    print(f"  ❌ 未找到AutoCAD窗口")
                    return False

                hwnd, title = windows[0]
                self.cached_hwnd = hwnd

                # 激活窗口（仅第一次OCR）
                try:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.5)
                    print(f"  ✅ 已激活AutoCAD窗口")
                except Exception as e:
                    print(f"  ⚠️ 激活窗口失败（可能已在前台），继续执行")

                # 获取窗口坐标并缓存
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                self.cached_window_rect = (left, top, right, bottom)
                print(f"  📍 窗口位置: ({left}, {top}) - ({right}, {bottom})")
            else:
                # 后续OCR操作，使用缓存坐标（保持菜单展开状态）
                hwnd = self.cached_hwnd
                left, top, right, bottom = self.cached_window_rect
                print(f"  ℹ️  使用缓存坐标（保持菜单展开）")
                print(f"  📍 坐标: ({left}, {top}) - ({right}, {bottom})")

            # ============================================================================
            # 截取屏幕区域（而不是窗口内容）
            # ============================================================================
            # 使用 PIL ImageGrab 截取屏幕区域（包含弹出菜单）
            from PIL import ImageGrab

            screenshot_start_time = time_module.time()
            image = ImageGrab.grab(bbox=(left, top, right, bottom))
            screenshot_time = time_module.time() - screenshot_start_time

            width = right - left
            height = bottom - top
            print(f"  截图完成: {width}x{height}（耗时: {screenshot_time:.3f}秒）")

            # ============================================================================
            # 文件管理：创建截图目录并执行清理
            # ============================================================================
            # 初始化文件管理器
            file_manager = OCRFileManager(
                base_dir=self.config.ocr_screenshot_base_dir or "screenshots",
                timestamp_format=self.config.ocr_screenshot_timestamp_format or "%Y%m%d_%H%M%S",
                cleanup_enabled=self.config.ocr_file_cleanup_enabled or False,
                cleanup_strategy=self.config.ocr_file_cleanup_strategy or "archive",
                archive_dir=self.config.ocr_file_archive_dir,
                retention_days=self.config.ocr_file_retention_days or 7
            )

            # 执行文件清理（如果启用）
            if file_manager.cleanup_enabled:
                print(f"\n  🧹 执行文件清理...")
                cleanup_stats = file_manager.cleanup_old_files()
                print(f"     删除: {cleanup_stats['deleted']}")
                print(f"     归档: {cleanup_stats['archived']}")
                print(f"     跳过: {cleanup_stats['skipped']}")
                print(f"     错误: {cleanup_stats['errors']}")

            # 创建新的截图目录
            screenshots_dir_path = file_manager.get_screenshot_dir(create_new=True)
            screenshot_dir = str(screenshots_dir_path)
            base_name = "autocad_window"

            print(f"\n  💾 保存截图到: {screenshot_dir}")
            print(f"  🔄 生成预处理图像...")

            # 从配置中读取预处理方法和参数
            preprocessing_methods = None
            preprocessing_params = None

            if self.config.ocr_preprocessing_methods:
                try:
                    preprocessing_methods = json.loads(self.config.ocr_preprocessing_methods)
                    print(f"  📋 使用配置的预处理方法: {preprocessing_methods}")
                except:
                    print(f"  ⚠️ 配置的预处理方法格式错误，使用默认推荐方法")

            if self.config.ocr_preprocessing_params:
                try:
                    preprocessing_params = json.loads(self.config.ocr_preprocessing_params)
                    print(f"  ⚙️ 使用配置的预处理参数: {len(preprocessing_params)} 项")
                except:
                    print(f"  ⚠️ 配置的预处理参数格式错误，使用默认参数")

            # ============================================================================
            # 图像预处理
            # ============================================================================
            preprocessing_start_time = time_module.time()

            # 生成所有预处理版本并保存
            preprocessed_images = preprocess_images(
                image,
                save_dir=screenshot_dir,
                base_name=base_name,
                methods=preprocessing_methods,  # None = 使用推荐方法
                params=preprocessing_params     # None = 使用默认参数
            )

            preprocessing_time = time_module.time() - preprocessing_start_time
            screenshots_saved = len(preprocessed_images)
            print(f"  ✅ 已生成 {screenshots_saved} 种预处理图像（耗时: {preprocessing_time:.3f}秒）")

            # ============================================================================
            # OCR识别（支持Umi-OCR优先）
            # ============================================================================
            img_array = np.array(image)

            if ocr_type == 'umi-ocr':
                # 使用Umi-OCR HTTP服务（首选，基于PaddleOCR，识别质量最佳）
                # 多线程并行识别所有预处理版本（性能优化）
                print(f"\n  🔍 使用Umi-OCR识别（多线程并行处理 {len(preprocessed_images)} 种预处理图像）...")

                all_ocr_results = []  # 存储所有OCR结果
                import threading
                from concurrent.futures import ThreadPoolExecutor, as_completed

                # 线程锁（保护共享数据）
                results_lock = threading.Lock()

                def process_single_image(version_and_img, method_order):
                    """处理单个预处理图像的OCR识别（线程函数）"""
                    version, processed_img = version_and_img

                    # 记录当前方法的性能
                    method_start_time = time_module.time()
                    method_ocr_time = 0.0
                    method_processing_time = 0.0

                    try:
                        import requests
                        import base64
                        import io

                        # 预处理时间（图像编码）
                        encoding_start_time = time_module.time()
                        buffered = io.BytesIO()
                        processed_img.save(buffered, format="PNG")
                        img_base64 = base64.b64encode(buffered.getvalue()).decode()
                        method_processing_time = time_module.time() - encoding_start_time

                        # OCR识别
                        method_ocr_start_time = time_module.time()
                        response = requests.post(
                            umi_ocr_api_url,
                            json={
                                "base64": img_base64,
                                "options": {
                                    "ocr.limit_side_len": umi_ocr_limit_side_len,
                                    "data.format": "dict"
                                }
                            },
                            timeout=umi_ocr_timeout
                        )
                        method_ocr_time = time_module.time() - method_ocr_start_time

                        result = response.json()

                        if result.get('code') != 100:
                            print(f"    ⚠️ [{version}] 识别失败，状态码: {result.get('code')}")
                            return {
                                'version': version,
                                'method_order': method_order,
                                'success': False,
                                'data': [],
                                'perf': {
                                    'method_name': version,
                                    'method_order': method_order,
                                    'processing_time': method_processing_time,
                                    'ocr_time': method_ocr_time,
                                    'total_time': time_module.time() - method_start_time,
                                    'texts_found': 0,
                                    'target_found': False,
                                    'matched_text': None,
                                    'max_confidence': None,
                                    'avg_confidence': None,
                                    'image_path': f"{screenshot_dir}/{base_name}_{version}.png",
                                    'image_size_kb': int(len(buffered.getvalue()) / 1024)
                                }
                            }

                        data = result.get('data', [])
                        if not data:
                            print(f"    ⚠️ [{version}] 未识别到任何文字")
                            return {
                                'version': version,
                                'method_order': method_order,
                                'success': False,
                                'data': [],
                                'perf': {
                                    'method_name': version,
                                    'method_order': method_order,
                                    'processing_time': method_processing_time,
                                    'ocr_time': method_ocr_time,
                                    'total_time': time_module.time() - method_start_time,
                                    'texts_found': 0,
                                    'target_found': False,
                                    'matched_text': None,
                                    'max_confidence': None,
                                    'avg_confidence': None,
                                    'image_path': f"{screenshot_dir}/{base_name}_{version}.png",
                                    'image_size_kb': int(len(buffered.getvalue()) / 1024)
                                }
                            }

                        print(f"    ✅ [{version}] 识别到 {len(data)} 个文本区域，OCR耗时: {method_ocr_time:.3f}秒")

                        # 统计置信度
                        confidences = [item.get('score', 0) for item in data if item.get('score')]
                        max_conf = max(confidences) if confidences else None
                        avg_conf = sum(confidences) / len(confidences) if confidences else None

                        # 检查是否找到目标文本
                        method_target_found = False
                        method_matched_text = None
                        best_match_confidence = 0

                        for item in data:
                            item_text = item.get('text', '')
                            item_confidence = item.get('score', 0)

                            if text in item_text:
                                method_target_found = True
                                if item_confidence > best_match_confidence:
                                    best_match_confidence = item_confidence
                                    method_matched_text = item_text

                        # 添加版本标记到每个结果
                        for item in data:
                            item['_version'] = version

                        # 显示前5个识别结果
                        print(f"    前5个识别结果:")
                        for i, item in enumerate(data[:5], 1):
                            recognized_text = item.get('text', '')
                            conf = item.get('score', 0)
                            print(f"      {i}. '{recognized_text}' (置信度:{conf:.2f})")

                        return {
                            'version': version,
                            'method_order': method_order,
                            'success': True,
                            'data': data,
                            'perf': {
                                'method_name': version,
                                'method_order': method_order,
                                'processing_time': method_processing_time,
                                'ocr_time': method_ocr_time,
                                'total_time': time_module.time() - method_start_time,
                                'texts_found': len(data),
                                'target_found': method_target_found,
                                'matched_text': method_matched_text,
                                'max_confidence': max_conf,
                                'avg_confidence': avg_conf,
                                'image_path': f"{screenshot_dir}/{base_name}_{version}.png",
                                'image_size_kb': int(len(buffered.getvalue()) / 1024)
                            }
                        }

                    except Exception as e:
                        print(f"    ❌ [{version}] OCR识别失败: {e}")
                        return {
                            'version': version,
                            'method_order': method_order,
                            'success': False,
                            'data': [],
                            'perf': {
                                'method_name': version,
                                'method_order': method_order,
                                'processing_time': method_processing_time,
                                'ocr_time': method_ocr_time,
                                'total_time': time_module.time() - method_start_time,
                                'texts_found': 0,
                                'target_found': False,
                                'matched_text': None,
                                'max_confidence': None,
                                'avg_confidence': None,
                                'image_path': f"{screenshot_dir}/{base_name}_{version}.png",
                                'image_size_kb': 0
                            }
                        }

                # 使用线程池并行处理所有预处理图像
                parallel_start_time = time_module.time()
                max_workers = self.config.umi_ocr_max_workers or 8  # 从配置读取，默认8
                # 限制线程数在合理范围（1-16）
                max_workers = max(1, min(max_workers, 16))
                # 不超过实际预处理图像数量
                max_workers = min(len(preprocessed_images), max_workers)
                print(f"  🚀 启动 {max_workers} 个并发线程...")

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # 提交所有任务
                    futures = {}
                    for idx, (version, processed_img) in enumerate(preprocessed_images.items(), 1):
                        future = executor.submit(process_single_image, (version, processed_img), idx)
                        futures[future] = version

                    # 收集结果（按完成顺序）
                    completed = 0
                    for future in as_completed(futures):
                        completed += 1
                        version = futures[future]
                        try:
                            result = future.result()
                            print(f"\n  📋 完成 [{completed}/{len(preprocessed_images)}] {result['version']} 版本")

                            # 线程安全地添加结果
                            with results_lock:
                                preprocessing_performance_data.append(result['perf'])
                                if result['success'] and result['data']:
                                    all_ocr_results.append(result['data'])
                                    ocr_time += result['perf']['ocr_time']

                        except Exception as e:
                            print(f"    ❌ [{version}] 线程执行失败: {e}")

                parallel_time = time_module.time() - parallel_start_time
                print(f"\n  ✅ 并行识别完成！总耗时: {parallel_time:.3f}秒 (平均单个: {parallel_time/len(preprocessed_images):.3f}秒)")
                print(f"  🎯 性能提升: {len(preprocessed_images)}x 并发请求")

                # ============================================================================
                # 合并OCR结果
                # ============================================================================
                if not all_ocr_results:
                    print(f"\n  ❌ 所有预处理版本均未识别到文字")
                    # 创建失败日志
                    total_time = time_module.time() - total_start_time
                    self._log_ocr_recognition(
                        target_text=text,
                        found=False,
                        total_time=total_time,
                        screenshot_time=screenshot_time,
                        preprocessing_time=preprocessing_time,
                        ocr_time=ocr_time,
                        merge_time=0.0,
                        preprocessing_methods=preprocessing_methods,
                        preprocessing_count=len(preprocessed_images),
                        total_texts_found=0,
                        unique_texts_count=0,
                        screenshot_dir=screenshot_dir,
                        screenshots_saved=screenshots_saved,
                        preprocessing_performance_data=preprocessing_performance_data,
                        status='failed',
                        error_message='所有预处理版本均未识别到文字'
                    )
                    return False

                merge_start_time = time_module.time()
                print(f"\n  🔄 合并 {len(all_ocr_results)} 次OCR结果...")
                merged_results = combine_ocr_results(all_ocr_results)
                merge_time = time_module.time() - merge_start_time

                # 统计OCR结果
                total_texts_found = sum(len(r) for r in all_ocr_results)
                unique_texts_count = len(merged_results)

                print(f"  ✅ 合并后共 {unique_texts_count} 个唯一文本（原始: {total_texts_found}，耗时: {merge_time:.3f}秒）")

                # 显示合并后的高置信度结果（前10个）
                print(f"\n  【调试】合并后的识别结果 (前10个，按置信度排序):")
                for i, item in enumerate(merged_results[:10], 1):
                    recognized_text = item.get('text', '')
                    conf = item.get('score', 0)
                    version = item.get('_version', 'unknown')
                    print(f"    {i}. '{recognized_text}' (置信度:{conf:.2f}, 来源:{version})")

                # ============================================================================
                # 保存OCR识别结果到txt文件
                # ============================================================================
                try:
                    txt_file_path = Path(screenshot_dir) / f"{base_name}_ocr_results.txt"
                    with open(txt_file_path, 'w', encoding='utf-8') as f:
                        # 写入标题和统计信息
                        f.write("=" * 80 + "\n")
                        f.write("OCR识别结果\n")
                        f.write("=" * 80 + "\n\n")

                        f.write(f"目标文本: '{text}'\n")
                        f.write(f"识别时间: {time_module.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"预处理方法数: {len(preprocessed_images)}\n")
                        f.write(f"总识别文本数: {total_texts_found}\n")
                        f.write(f"唯一文本数: {unique_texts_count}\n")
                        f.write(f"总耗时: {time_module.time() - total_start_time:.3f}秒\n")
                        f.write("\n" + "=" * 80 + "\n\n")

                        # 写入每个预处理方法的识别结果
                        f.write("【各预处理方法识别详情】\n\n")
                        for idx, result_list in enumerate(all_ocr_results, 1):
                            if result_list:
                                version = result_list[0].get('_version', f'method_{idx}')
                                f.write(f"[{idx}] {version} - 识别到 {len(result_list)} 个文本\n")
                                f.write("-" * 80 + "\n")
                                for i, item in enumerate(result_list, 1):
                                    recognized_text = item.get('text', '')
                                    conf = item.get('score', 0)
                                    f.write(f"  {i}. '{recognized_text}' (置信度: {conf:.2f})\n")
                                f.write("\n")

                        f.write("=" * 80 + "\n\n")

                        # 写入合并后的唯一文本（按置信度排序）
                        f.write("【合并后的唯一文本】（按置信度排序）\n\n")
                        for i, item in enumerate(merged_results, 1):
                            recognized_text = item.get('text', '')
                            conf = item.get('score', 0)
                            version = item.get('_version', 'unknown')
                            box = item.get('box', [])

                            f.write(f"{i}. '{recognized_text}'\n")
                            f.write(f"   置信度: {conf:.2f}\n")
                            f.write(f"   来源: {version}\n")
                            if box and len(box) >= 4:
                                f.write(f"   位置: {box}\n")
                            f.write("\n")

                    print(f"\n  💾 OCR结果已保存到: {txt_file_path}")

                except Exception as e:
                    print(f"\n  ⚠️ 保存OCR结果失败: {e}")
                    # 不影响主流程，继续执行

                # ============================================================================
                # 查找匹配文本（智能匹配策略）
                # ============================================================================
                print(f"\n  🔍 查找文本: '{text}'")
                found = False

                # 收集所有匹配的候选项
                exact_matches = []      # 完全匹配（text == recognized_text）
                contains_matches = []   # 包含匹配（text in recognized_text）
                fuzzy_matches = []      # 模糊匹配（编辑距离、去空格等）

                for item in merged_results:
                    recognized_text = item.get('text', '')
                    conf = item.get('score', 0)
                    box = item.get('box', [])
                    version = item.get('_version', 'unknown')

                    if not recognized_text.strip():
                        continue

                    # 匹配策略分级
                    # 1. 完全匹配（最高优先级）
                    if text == recognized_text:
                        exact_matches.append((item, conf, 'exact'))
                        continue

                    # 2. 包含匹配（text in recognized_text）
                    if text in recognized_text:
                        contains_matches.append((item, conf, 'contains'))
                        continue

                    # 3. 去除空格后匹配
                    clean_target = text.replace(' ', '')
                    clean_recognized = recognized_text.replace(' ', '')
                    if clean_target == clean_recognized:
                        exact_matches.append((item, conf, 'exact_no_space'))
                        continue
                    elif clean_target in clean_recognized:
                        contains_matches.append((item, conf, 'contains_no_space'))
                        continue

                    # 4. 反向匹配（recognized_text in text）
                    if recognized_text in text:
                        fuzzy_matches.append((item, conf, 'reverse'))
                        continue

                    # 5. 编辑距离匹配
                    def levenshtein_distance(s1, s2):
                        if len(s1) < len(s2):
                            return levenshtein_distance(s2, s1)
                        if len(s2) == 0:
                            return len(s1)
                        previous_row = range(len(s2) + 1)
                        for i, c1 in enumerate(s1):
                            current_row = [i + 1]
                            for j, c2 in enumerate(s2):
                                insertions = previous_row[j + 1] + 1
                                deletions = current_row[j] + 1
                                substitutions = previous_row[j] + (c1 != c2)
                                current_row.append(min(insertions, deletions, substitutions))
                            previous_row = current_row
                        return previous_row[-1]

                    distance = levenshtein_distance(text, recognized_text)
                    if distance <= min(2, len(text) // 2):
                        fuzzy_matches.append((item, conf, f'levenshtein_{distance}'))

                # 按优先级和置信度选择最佳匹配
                best_match = None
                match_type = None

                # 优先级1: 完全匹配，按置信度排序
                if exact_matches:
                    exact_matches.sort(key=lambda x: x[1], reverse=True)
                    best_match = exact_matches[0]
                    match_type = '完全匹配'
                    print(f"  ✅ 找到 {len(exact_matches)} 个完全匹配，选择置信度最高的")

                # 优先级2: 包含匹配，按置信度排序
                elif contains_matches:
                    contains_matches.sort(key=lambda x: x[1], reverse=True)
                    best_match = contains_matches[0]
                    match_type = '包含匹配'
                    print(f"  ✅ 找到 {len(contains_matches)} 个包含匹配，选择置信度最高的")

                # 优先级3: 模糊匹配，按置信度排序
                elif fuzzy_matches:
                    fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
                    best_match = fuzzy_matches[0]
                    match_type = '模糊匹配'
                    print(f"  ✅ 找到 {len(fuzzy_matches)} 个模糊匹配，选择置信度最高的")

                # 显示所有候选项（调试用）
                if exact_matches or contains_matches or fuzzy_matches:
                    print(f"\n  【匹配候选项】")
                    if exact_matches:
                        print(f"  完全匹配 ({len(exact_matches)}个):")
                        for idx, (item, conf, mtype) in enumerate(exact_matches[:3], 1):
                            print(f"    {idx}. '{item.get('text', '')}' (置信度:{conf:.2f}, 类型:{mtype})")
                    if contains_matches:
                        print(f"  包含匹配 ({len(contains_matches)}个):")
                        for idx, (item, conf, mtype) in enumerate(contains_matches[:3], 1):
                            print(f"    {idx}. '{item.get('text', '')}' (置信度:{conf:.2f}, 类型:{mtype})")
                    if fuzzy_matches:
                        print(f"  模糊匹配 ({len(fuzzy_matches)}个):")
                        for idx, (item, conf, mtype) in enumerate(fuzzy_matches[:3], 1):
                            print(f"    {idx}. '{item.get('text', '')}' (置信度:{conf:.2f}, 类型:{mtype})")

                # 执行点击
                if best_match:
                    item, conf, mtype = best_match
                    recognized_text = item.get('text', '')
                    box = item.get('box', [])
                    version = item.get('_version', 'unknown')

                    if box and len(box) >= 4:
                        # 智能计算点击位置：点击目标文本实际所在的区域
                        # 而不是整个识别文本的中心

                        # 1. 找到目标文本在识别文本中的位置
                        target_index = recognized_text.find(text)
                        if target_index == -1:
                            # 如果直接查找失败，尝试去除空格后查找
                            clean_recognized = recognized_text.replace(' ', '')
                            clean_target = text.replace(' ', '')
                            target_index = clean_recognized.find(clean_target)
                            if target_index == -1:
                                target_index = 0  # 找不到就用开头

                        # 2. 计算bbox的宽度和高度
                        bbox_left = box[0][0]
                        bbox_top = box[0][1]
                        bbox_right = box[2][0]
                        bbox_bottom = box[2][1]
                        bbox_width = bbox_right - bbox_left
                        bbox_height = bbox_bottom - bbox_top

                        # 3. 计算目标文本的起始位置比例和长度比例
                        recognized_len = len(recognized_text)
                        target_len = len(text)

                        # 目标文本起始位置的比例（0.0 - 1.0）
                        start_ratio = target_index / recognized_len if recognized_len > 0 else 0.0
                        # 目标文本长度的比例
                        length_ratio = target_len / recognized_len if recognized_len > 0 else 1.0

                        # 4. 计算目标文本中心的x坐标
                        # 目标文本中心 = 起始位置 + 长度的一半
                        target_center_ratio = start_ratio + length_ratio / 2.0
                        center_x = int(bbox_left + bbox_width * target_center_ratio)
                        center_y = int((bbox_top + bbox_bottom) / 2)

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        # 记录匹配信息
                        found = True
                        matched_text = recognized_text
                        confidence = conf
                        matched_version = version
                        position_x = screen_x
                        position_y = screen_y

                        print(f"\n  ✅ 最佳匹配: '{recognized_text}'")
                        print(f"     匹配类型: {match_type} ({mtype})")
                        print(f"     目标文本: '{text}'")
                        print(f"     位置索引: 第{target_index}个字符")
                        print(f"     置信度: {confidence:.2f}")
                        print(f"     来源版本: [{version}]")
                        print(f"     点击坐标: ({screen_x}, {screen_y})")

                        # 移动鼠标并点击
                        pyautogui.moveTo(screen_x, screen_y, duration=0.3)
                        time.sleep(0.2)
                        pyautogui.click()

                        if keep_menu_open:
                            print(f"  ℹ️  保持菜单展开状态（连续菜单操作）")
                            print(f"  ℹ️  鼠标停留在: ({screen_x}, {screen_y})")
                        else:
                            print(f"  ✅ 已点击文本")

                        # 记录成功的OCR识别日志
                        total_time = time_module.time() - total_start_time
                        self._log_ocr_recognition(
                            target_text=text,
                            found=True,
                            matched_text=matched_text,
                            confidence=confidence,
                            matched_version=matched_version,
                            position_x=position_x,
                            position_y=position_y,
                            total_time=total_time,
                            screenshot_time=screenshot_time,
                            preprocessing_time=preprocessing_time,
                            ocr_time=ocr_time,
                            merge_time=merge_time,
                            preprocessing_methods=preprocessing_methods,
                            preprocessing_count=len(preprocessed_images),
                            total_texts_found=total_texts_found,
                            unique_texts_count=unique_texts_count,
                            screenshot_dir=screenshot_dir,
                            screenshots_saved=screenshots_saved,
                            preprocessing_performance_data=preprocessing_performance_data,
                            status='success'
                        )
                        return True

                # 未找到匹配文本
                print(f"  ❌ 未找到文本: '{text}'")

                # 记录失败的OCR识别日志
                total_time = time_module.time() - total_start_time
                self._log_ocr_recognition(
                    target_text=text,
                    found=False,
                    total_time=total_time,
                    screenshot_time=screenshot_time,
                    preprocessing_time=preprocessing_time,
                    ocr_time=ocr_time,
                    merge_time=merge_time,
                    preprocessing_methods=preprocessing_methods,
                    preprocessing_count=len(preprocessed_images),
                    total_texts_found=total_texts_found,
                    unique_texts_count=unique_texts_count,
                    screenshot_dir=screenshot_dir,
                    screenshots_saved=screenshots_saved,
                    preprocessing_performance_data=preprocessing_performance_data,
                    status='partial',
                    error_message='识别成功但未找到目标文本'
                )
                return False

            elif ocr_type == 'tesseract':
                # 使用Tesseract OCR（推荐，对中文UI小字体识别最好）
                print(f"  使用Tesseract OCR识别...")
                try:
                    import pytesseract
                    import cv2

                    # 转换为灰度图以提高识别率
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

                    # 使用中文+英文识别，获取详细信息（包括坐标）
                    # config: lang=chi_sim+eng, output with bounding boxes
                    data = pytesseract.image_to_data(gray, lang='chi_sim+eng',
                                                      output_type=pytesseract.Output.DICT)

                    # 统计识别到的文本数量
                    n_boxes = len(data['text'])
                    valid_count = sum(1 for t in data['text'] if t.strip())

                    if valid_count == 0:
                        print(f"  ❌ 未识别到任何文字")
                        return False

                    print(f"  识别到 {valid_count} 个文本区域")

                    # 调试输出：显示所有识别到的文字
                    print(f"  【调试】所有识别到的文字:")
                    debug_count = 0
                    for i in range(n_boxes):
                        if data['text'][i].strip() and data['conf'][i] > 0:
                            debug_count += 1
                            if debug_count <= 20:  # 只显示前20个
                                conf = int(data['conf'][i])
                                print(f"    {debug_count}. '{data['text'][i]}' (置信度:{conf}%)")

                    # 查找匹配的文本（使用模糊匹配）
                    found = False
                    for i in range(n_boxes):
                        recognized_text = data['text'][i]
                        confidence = int(data['conf'][i])

                        if not recognized_text.strip() or confidence < 0:
                            continue

                        # 模糊匹配策略（与EasyOCR相同的4种策略）
                        match = False
                        # 1. 完全匹配
                        if text in recognized_text:
                            match = True
                        # 2. 去除空格后匹配
                        elif text.replace(' ', '') in recognized_text.replace(' ', ''):
                            match = True
                        # 3. 反过来匹配
                        elif recognized_text in text:
                            match = True
                        # 4. 字符相似度匹配
                        else:
                            def levenshtein_distance(s1, s2):
                                if len(s1) < len(s2):
                                    return levenshtein_distance(s2, s1)
                                if len(s2) == 0:
                                    return len(s1)
                                previous_row = range(len(s2) + 1)
                                for i, c1 in enumerate(s1):
                                    current_row = [i + 1]
                                    for j, c2 in enumerate(s2):
                                        insertions = previous_row[j + 1] + 1
                                        deletions = current_row[j] + 1
                                        substitutions = previous_row[j] + (c1 != c2)
                                        current_row.append(min(insertions, deletions, substitutions))
                                    previous_row = current_row
                                return previous_row[-1]

                            distance = levenshtein_distance(text, recognized_text)
                            if distance <= min(2, len(text) // 2):
                                match = True
                                print(f"  [模糊匹配] 编辑距离:{distance}, 原文:'{text}', 识别:'{recognized_text}'")

                        if match:
                            # 获取边界框坐标
                            x = data['left'][i]
                            y = data['top'][i]
                            w = data['width'][i]
                            h = data['height'][i]

                            # 智能计算点击位置
                            target_index = recognized_text.find(text)
                            if target_index == -1:
                                clean_recognized = recognized_text.replace(' ', '')
                                clean_target = text.replace(' ', '')
                                target_index = clean_recognized.find(clean_target)
                                if target_index == -1:
                                    target_index = 0

                            recognized_len = len(recognized_text)
                            target_len = len(text)
                            start_ratio = target_index / recognized_len if recognized_len > 0 else 0.0
                            length_ratio = target_len / recognized_len if recognized_len > 0 else 1.0
                            target_center_ratio = start_ratio + length_ratio / 2.0

                            # 计算目标文本中心点
                            center_x = int(x + w * target_center_ratio)
                            center_y = y + h // 2

                            # 转换为屏幕坐标
                            screen_x = left + center_x
                            screen_y = top + center_y

                            print(f"  ✅ 找到文本: '{recognized_text}' (置信度:{confidence}%)")
                            print(f"  位置: ({screen_x}, {screen_y})")

                            # 移动鼠标并点击
                            pyautogui.moveTo(screen_x, screen_y, duration=0.3)
                            time.sleep(0.2)
                            pyautogui.click()

                            print(f"  ✅ 已点击文本")
                            return True

                    print(f"  ❌ 未找到文本: '{text}'")
                    return False

                except Exception as e:
                    print(f"  ❌ Tesseract识别失败: {e}")
                    print(f"  提示: 确保已安装Tesseract引擎和中文语言包")
                    print(f"    下载地址: https://github.com/UB-Mannheim/tesseract/wiki")
                    return False

            elif ocr_type == 'easyocr':
                # 使用EasyOCR（推荐）
                print(f"  使用EasyOCR识别...")
                reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                result = reader.readtext(img_array)

                if not result:
                    print(f"  ❌ 未识别到任何文字")
                    return False

                print(f"  识别到 {len(result)} 个文本区域")

                # 调试输出：显示所有识别到的文字
                print(f"  【调试】所有识别到的文字:")
                for i, detection in enumerate(result[:10], 1):  # 只显示前10个
                    recognized_text = detection[1]
                    confidence = detection[2]
                    print(f"    {i}. '{recognized_text}' (置信度:{confidence:.2f})")

                # 查找匹配的文本（使用模糊匹配）
                found = False
                for detection in result:
                    box = detection[0]
                    recognized_text = detection[1]
                    confidence = detection[2]

                    # 模糊匹配策略
                    match = False
                    # 1. 完全匹配
                    if text in recognized_text:
                        match = True
                    # 2. 去除空格后匹配
                    elif text.replace(' ', '') in recognized_text.replace(' ', ''):
                        match = True
                    # 3. 反过来匹配（识别到的包含搜索的）
                    elif recognized_text in text:
                        match = True
                    # 4. 字符相似度匹配（允许1-2个字符差异）
                    else:
                        # 计算编辑距离
                        def levenshtein_distance(s1, s2):
                            if len(s1) < len(s2):
                                return levenshtein_distance(s2, s1)
                            if len(s2) == 0:
                                return len(s1)
                            previous_row = range(len(s2) + 1)
                            for i, c1 in enumerate(s1):
                                current_row = [i + 1]
                                for j, c2 in enumerate(s2):
                                    insertions = previous_row[j + 1] + 1
                                    deletions = current_row[j] + 1
                                    substitutions = previous_row[j] + (c1 != c2)
                                    current_row.append(min(insertions, deletions, substitutions))
                                previous_row = current_row
                            return previous_row[-1]

                        distance = levenshtein_distance(text, recognized_text)
                        # 允许1-2个字符差异
                        if distance <= min(2, len(text) // 2):
                            match = True
                            print(f"  [模糊匹配] 编辑距离:{distance}, 原文:'{text}', 识别:'{recognized_text}'")

                    if match:
                        # 智能计算点击位置
                        target_index = recognized_text.find(text)
                        if target_index == -1:
                            clean_recognized = recognized_text.replace(' ', '')
                            clean_target = text.replace(' ', '')
                            target_index = clean_recognized.find(clean_target)
                            if target_index == -1:
                                target_index = 0

                        recognized_len = len(recognized_text)
                        target_len = len(text)
                        start_ratio = target_index / recognized_len if recognized_len > 0 else 0.0
                        length_ratio = target_len / recognized_len if recognized_len > 0 else 1.0
                        target_center_ratio = start_ratio + length_ratio / 2.0

                        # EasyOCR的box是4个点的坐标列表
                        x_coords = [point[0] for point in box]
                        y_coords = [point[1] for point in box]
                        bbox_left = min(x_coords)
                        bbox_right = max(x_coords)
                        bbox_top = min(y_coords)
                        bbox_bottom = max(y_coords)
                        bbox_width = bbox_right - bbox_left

                        # 计算目标文本中心点
                        center_x = int(bbox_left + bbox_width * target_center_ratio)
                        center_y = int((bbox_top + bbox_bottom) / 2)

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        print(f"  ✅ 找到文本: '{recognized_text}' (置信度:{confidence:.2f})")
                        print(f"     目标: '{text}'")
                        print(f"     位置: 第{target_index}个字符")
                        print(f"     点击位置: ({screen_x}, {screen_y})")

                        # 移动鼠标并点击
                        pyautogui.moveTo(screen_x, screen_y, duration=0.3)
                        time.sleep(0.2)
                        pyautogui.click()

                        print(f"  ✅ 已点击文本")
                        return True

            else:  # paddleocr
                # 使用PaddleOCR
                print(f"  使用PaddleOCR识别...")
                ocr = PaddleOCR(use_textline_orientation=True, lang='ch')
                result = ocr.ocr(img_array, cls=True)

                if not result or not result[0]:
                    print(f"  ❌ 未识别到任何文字")
                    return False

                # 查找匹配的文本
                for line in result[0]:
                    box = line[0]
                    recognized_text = line[1][0]
                    confidence = line[1][1]

                    # 模糊匹配
                    match = False
                    if text in recognized_text:
                        match = True
                    elif text.replace(' ', '') in recognized_text.replace(' ', ''):
                        match = True
                    elif recognized_text in text:
                        match = True

                    if match:
                        # 智能计算点击位置
                        target_index = recognized_text.find(text)
                        if target_index == -1:
                            clean_recognized = recognized_text.replace(' ', '')
                            clean_target = text.replace(' ', '')
                            target_index = clean_recognized.find(clean_target)
                            if target_index == -1:
                                target_index = 0

                        recognized_len = len(recognized_text)
                        target_len = len(text)
                        start_ratio = target_index / recognized_len if recognized_len > 0 else 0.0
                        length_ratio = target_len / recognized_len if recognized_len > 0 else 1.0
                        target_center_ratio = start_ratio + length_ratio / 2.0

                        # PaddleOCR的box是4个点的坐标列表
                        x_coords = [point[0] for point in box]
                        y_coords = [point[1] for point in box]
                        bbox_left = min(x_coords)
                        bbox_right = max(x_coords)
                        bbox_top = min(y_coords)
                        bbox_bottom = max(y_coords)
                        bbox_width = bbox_right - bbox_left

                        # 计算目标文本中心点
                        center_x = int(bbox_left + bbox_width * target_center_ratio)
                        center_y = int((bbox_top + bbox_bottom) / 2)

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        print(f"  ✅ 找到文本: '{recognized_text}' (置信度:{confidence:.2f})")
                        print(f"     目标: '{text}'")
                        print(f"     位置: 第{target_index}个字符")
                        print(f"     点击位置: ({screen_x}, {screen_y})")

                        # 移动鼠标并点击
                        pyautogui.moveTo(screen_x, screen_y, duration=0.3)
                        time.sleep(0.2)
                        pyautogui.click()

                        print(f"  ✅ 已点击文本")
                        return True

            print(f"  ❌ 未找到文本: '{text}'")
            return False

        except Exception as e:
            print(f"  ❌ OCR识别失败: {e}")
            import traceback
            traceback.print_exc()
            return False


    def _close_all_autocad_processes(self) -> int:
        """关闭所有 AutoCAD 进程"""
        closed_count = 0
        try:
            # 第1步：COM 正常关闭
            print("  [1/4] 尝试COM方式关闭...")
            try:
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                acad.Quit()
                closed_count += 1
                print("  ✅ COM关闭成功")
                time.sleep(2)
            except:
                print("  ⚠️ 没有活动的COM对象")

            # 第2步：强制终止进程
            print("  [2/4] 检查并终止残留进程...")
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                        print(f"  终止进程 PID={proc.pid}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        closed_count += 1
                except:
                    pass

            # 第3步：等待进程完全关闭
            print("  [3/4] 等待进程完全关闭...")
            max_wait = 10  # 最多等待10秒
            for i in range(max_wait):
                if not self._is_autocad_running():
                    print(f"  ✅ 进程已完全关闭（等待{i+1}秒）")
                    break
                print(f"  ⏳ 等待进程关闭... ({i+1}/{max_wait}秒)")
                time.sleep(1)
            else:
                print("  ⚠️ 进程可能仍在运行")

            # 第4步：清理COM缓存
            print("  [4/4] 清理COM缓存...")
            try:
                import pythoncom
                pythoncom.CoUninitialize()
                time.sleep(0.5)
                pythoncom.CoInitialize()
                print("  ✅ COM缓存已清理")
            except:
                print("  ⚠️ COM缓存清理失败（可能无影响）")

        except Exception as e:
            print(f"  ⚠️ 关闭过程出错: {e}")

        return closed_count

    def _is_autocad_running(self) -> bool:
        """检查 AutoCAD 是否运行"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def _log_task_end(self, status: str, error_message: Optional[str] = None):
        """记录任务结束"""
        if not self.task_log_id:
            return

        db = SessionLocal()
        try:
            service = AutoCADConfigService(db)
            service.log_task_end(
                log_id=self.task_log_id,
                status=status,
                error_message=error_message
            )
        except:
            pass
        finally:
            db.close()

    def _log_ocr_recognition(
        self,
        target_text: str,
        found: bool,
        total_time: float,
        screenshot_time: float,
        preprocessing_time: float,
        ocr_time: float,
        merge_time: float,
        preprocessing_methods: list,
        preprocessing_count: int,
        total_texts_found: int,
        unique_texts_count: int,
        screenshot_dir: str,
        screenshots_saved: int,
        preprocessing_performance_data: list,
        status: str = 'success',
        error_message: str = None,
        matched_text: str = None,
        confidence: float = None,
        matched_version: str = None,
        position_x: int = None,
        position_y: int = None
    ):
        """
        记录OCR识别日志（包括性能数据）

        这个SB方法负责把所有识别数据写入数据库，艹！
        """
        try:
            from src.services.ocr_logging_service import OCRLoggingService
            from src.utils.database import SessionLocal

            db = SessionLocal()
            try:
                logging_service = OCRLoggingService(db)

                # 创建主OCR识别日志
                recognition_log = logging_service.create_recognition_log(
                    config_id=self.config.id if self.config else None,
                    task_log_id=self.task_log_id,
                    target_text=target_text,
                    found=found,
                    matched_text=matched_text,
                    confidence=confidence,
                    matched_version=matched_version,
                    position_x=position_x,
                    position_y=position_y,
                    total_time=total_time,
                    screenshot_time=screenshot_time,
                    preprocessing_time=preprocessing_time,
                    ocr_time=ocr_time,
                    merge_time=merge_time,
                    preprocessing_methods=preprocessing_methods,
                    preprocessing_count=preprocessing_count,
                    total_texts_found=total_texts_found,
                    unique_texts_count=unique_texts_count,
                    screenshot_dir=screenshot_dir,
                    screenshots_saved=screenshots_saved,
                    status=status,
                    error_message=error_message
                )

                # 创建每个预处理方法的性能记录
                for perf_data in preprocessing_performance_data:
                    logging_service.add_preprocessing_performance(
                        recognition_log_id=recognition_log.id,
                        method_name=perf_data['method_name'],
                        method_order=perf_data['method_order'],
                        processing_time=perf_data['processing_time'],
                        ocr_time=perf_data['ocr_time'],
                        total_time=perf_data['total_time'],
                        texts_found=perf_data['texts_found'],
                        target_found=perf_data['target_found'],
                        matched_text=perf_data.get('matched_text'),
                        max_confidence=perf_data.get('max_confidence'),
                        avg_confidence=perf_data.get('avg_confidence'),
                        image_path=perf_data.get('image_path'),
                        image_size_kb=perf_data.get('image_size_kb')
                    )

                print(f"\n  📊 OCR日志已记录 (ID: {recognition_log.id})")
                print(f"     总耗时: {total_time:.3f}秒")
                print(f"     截图: {screenshot_time:.3f}秒")
                print(f"     预处理: {preprocessing_time:.3f}秒")
                print(f"     OCR: {ocr_time:.3f}秒")
                print(f"     合并: {merge_time:.3f}秒")
                print(f"     方法数: {preprocessing_count}")
                print(f"     识别文本数: {total_texts_found} → {unique_texts_count}（去重后）")

            finally:
                db.close()

        except Exception as e:
            print(f"  ⚠️ OCR日志记录失败: {e}")
            # 不抛出异常，避免影响主流程

    def _screenshot_and_extract(self, target_pattern: str, save_to: str) -> tuple:
        """
        全屏截图并使用OCR提取指定模式的文本

        Args:
            target_pattern: 正则表达式模式，如 "共 (\\d+) 页"
            save_to: 保存变量名

        Returns:
            (成功标志, 提取的值)

        这个SB方法用于截图并提取动态文本（比如总页数），艹！
        """
        import time as time_module
        import re

        print(f"  🔍 提取模式: {target_pattern}")

        # 初始化时间统计变量
        screenshot_time = 0.0
        ocr_time = 0.0

        try:
            import pyautogui
            import numpy as np
            from PIL import ImageGrab
        except ImportError:
            print(f"  ❌ 缺少必要的库")
            return (False, None)

        # 检查OCR类型（优先Umi-OCR）
        ocr_type = None
        umi_ocr_api_url = None
        umi_ocr_timeout = 30
        umi_ocr_limit_side_len = 2880

        # 优先尝试Umi-OCR
        if self.config.umi_ocr_enabled:
            try:
                import requests

                umi_ocr_base_url = self.config.umi_ocr_service_url or "http://10.3.19.121:1224"
                umi_ocr_api_path = self.config.umi_ocr_api_path or "/api/ocr"
                umi_ocr_timeout = self.config.umi_ocr_timeout or 30
                umi_ocr_limit_side_len = self.config.umi_ocr_limit_side_len or 2880

                if not umi_ocr_base_url.endswith('/'):
                    umi_ocr_base_url += '/'
                if umi_ocr_api_path.startswith('/'):
                    umi_ocr_api_path = umi_ocr_api_path[1:]
                umi_ocr_api_url = umi_ocr_base_url.rstrip('/') + '/' + umi_ocr_api_path.lstrip('/')

                # 测试服务
                test_url = umi_ocr_base_url.rstrip('/') + '/'
                test_response = requests.get(test_url, timeout=2)
                if test_response.status_code == 200:
                    ocr_type = 'umi-ocr'
                    print(f"  ✅ 使用Umi-OCR: {umi_ocr_api_url}")
            except Exception as e:
                print(f"  ⚠️ Umi-OCR不可用: {e}")
                pass

        # 备选OCR库
        if not ocr_type:
            try:
                import pytesseract
                ocr_type = 'tesseract'
                print(f"  ✅ 使用Tesseract OCR")
            except ImportError:
                try:
                    import easyocr
                    ocr_type = 'easyocr'
                    print(f"  ✅ 使用EasyOCR")
                except ImportError:
                    print(f"  ❌ 无可用的OCR引擎")
                    return (False, None)

        try:
            # ============================================================================
            # 全屏截图
            # ============================================================================
            print(f"\n  📸 执行全屏截图...")
            screenshot_start_time = time_module.time()

            # 截取整个屏幕
            image = ImageGrab.grab()
            width, height = image.size
            screenshot_time = time_module.time() - screenshot_start_time

            print(f"  ✅ 截图完成: {width}x{height} (耗时: {screenshot_time:.3f}秒)")

            # ============================================================================
            # 图像预处理（和菜单OCR一样）
            # ============================================================================
            print(f"\n  🎨 图像预处理...")
            preprocessing_start_time = time_module.time()

            # 获取预处理配置
            preprocessing_methods = None
            preprocessing_params = {}

            if self.config.ocr_preprocessing_methods:
                try:
                    preprocessing_methods = json.loads(self.config.ocr_preprocessing_methods)
                except:
                    preprocessing_methods = None

            if self.config.ocr_preprocessing_params:
                try:
                    preprocessing_params = json.loads(self.config.ocr_preprocessing_params)
                except:
                    preprocessing_params = {}

            # 执行预处理
            from src.utils.image_processing import preprocess_images
            preprocessed_images = preprocess_images(
                image,
                methods=preprocessing_methods,
                params=preprocessing_params
            )

            preprocessing_time = time_module.time() - preprocessing_start_time
            print(f"  ✅ 预处理完成: 生成 {len(preprocessed_images)} 个版本 (耗时: {preprocessing_time:.3f}秒)")

            # ============================================================================
            # OCR识别（对所有预处理版本）
            # ============================================================================
            print(f"\n  🔍 OCR识别中...")
            ocr_start_time = time_module.time()

            all_ocr_results = []  # 存储所有版本的OCR结果（保留版本信息）
            all_ocr_data = []  # 存储所有版本的原始数据（供combine_ocr_results使用）

            if ocr_type == 'umi-ocr':
                # 使用Umi-OCR - 批量识别所有预处理版本
                try:
                    import requests
                    import base64
                    import io
                    from concurrent.futures import ThreadPoolExecutor, as_completed

                    max_workers = self.config.umi_ocr_max_workers or 8

                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = {}
                        for version, processed_img in preprocessed_images.items():
                            # 编码图像
                            buffered = io.BytesIO()
                            processed_img.save(buffered, format="PNG")
                            img_base64 = base64.b64encode(buffered.getvalue()).decode()

                            # 提交OCR任务
                            future = executor.submit(
                                requests.post,
                                umi_ocr_api_url,
                                json={
                                    "base64": img_base64,
                                    "options": {
                                        "ocr.limit_side_len": umi_ocr_limit_side_len,
                                        "data.format": "dict"
                                    }
                                },
                                timeout=umi_ocr_timeout
                            )
                            futures[future] = version

                        # 收集结果
                        for future in as_completed(futures):
                            version = futures[future]
                            try:
                                response = future.result()
                                result = response.json()

                                if result.get('code') == 100:
                                    data = result.get('data', [])
                                    # 保存原始字典数据（供combine_ocr_results使用）
                                    all_ocr_data.append(data)
                                    # 保存带版本信息的结果（供保存文本文件使用）
                                    texts = [item.get('text', '') for item in data if item.get('text')]
                                    all_ocr_results.append({
                                        'version': version,
                                        'texts': texts,
                                        'count': len(data)
                                    })
                                    print(f"    [{version}] 识别到 {len(data)} 个文本")
                            except Exception as e:
                                print(f"    [{version}] 识别失败: {e}")

                    # 合并所有识别结果（去重）
                    from src.utils.image_processing import combine_ocr_results
                    all_recognized_texts = combine_ocr_results(all_ocr_data)
                    print(f"  ✅ 合并后识别到 {len(all_recognized_texts)} 个唯一文本")

                except Exception as e:
                    print(f"  ❌ Umi-OCR请求失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return (False, None)

            elif ocr_type == 'tesseract':
                # 使用Tesseract
                try:
                    import pytesseract
                    import cv2

                    img_array = np.array(image)
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

                    # 获取文本数据
                    data = pytesseract.image_to_data(gray, lang='chi_sim+eng',
                                                      output_type=pytesseract.Output.DICT)

                    n_boxes = len(data['text'])
                    for i in range(n_boxes):
                        if data['text'][i].strip() and data['conf'][i] > 0:
                            all_recognized_texts.append(data['text'][i])

                    print(f"  ✅ 识别到 {len(all_recognized_texts)} 个文本区域")

                except Exception as e:
                    print(f"  ❌ Tesseract识别失败: {e}")
                    return (False, None)

            elif ocr_type == 'easyocr':
                # 使用EasyOCR
                try:
                    import easyocr

                    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
                    img_array = np.array(image)
                    result = reader.readtext(img_array)

                    all_recognized_texts = [detection[1] for detection in result]
                    print(f"  ✅ 识别到 {len(all_recognized_texts)} 个文本区域")

                except Exception as e:
                    print(f"  ❌ EasyOCR识别失败: {e}")
                    return (False, None)

            ocr_time = time_module.time() - ocr_start_time
            print(f"  ⏱️  OCR耗时: {ocr_time:.3f}秒")

            # ============================================================================
            # 使用正则表达式提取目标文本
            # ============================================================================
            print(f"\n  🔎 查找匹配文本...")

            # 编译正则表达式
            pattern = re.compile(target_pattern)

            # 调试：显示前20个识别结果
            if len(all_recognized_texts) > 0:
                print(f"  【调试】前20个识别结果:")
                for i, item in enumerate(all_recognized_texts[:20], 1):
                    text = item.get('text', '')
                    conf = item.get('score', 0)
                    print(f"    {i}. '{text}' (置信度:{conf:.2f})")

            # 查找匹配
            extracted_value = None
            matched_text = None

            for item in all_recognized_texts:
                text = item.get('text', '')
                match = pattern.search(text)
                if match:
                    matched_text = text
                    # 如果有捕获组，提取第一个捕获组
                    if match.groups():
                        extracted_value = match.group(1)
                    else:
                        extracted_value = match.group(0)

                    print(f"\n  ✅ 找到匹配!")
                    print(f"     完整文本: '{matched_text}'")
                    print(f"     提取值: '{extracted_value}'")
                    break

            # ============================================================================
            # 保存截图和OCR文本到文件（无论是否找到匹配都保存，方便调试）
            # ============================================================================
            screenshot_saved_path = None
            ocr_text_saved_path = None
            screenshots_saved_count = 0

            try:
                # 确定保存目录
                screenshot_base_dir = self.config.ocr_screenshot_base_dir
                if not screenshot_base_dir:
                    screenshot_base_dir = 'data'

                timestamp_format = self.config.ocr_screenshot_timestamp_format or '%Y%m%d_%H%M%S'
                timestamp_str = datetime.now().strftime(timestamp_format)
                screenshot_dir = Path(screenshot_base_dir) / timestamp_str

                # 创建目录
                screenshot_dir.mkdir(parents=True, exist_ok=True)

                # 保存所有预处理版本的截图（和菜单OCR一样）
                print(f"\n  💾 保存截图...")
                base_name = f"fullscreen_extract_{save_to}"

                for version, processed_img in preprocessed_images.items():
                    screenshot_filename = f"{base_name}_{version}.png"
                    screenshot_path = screenshot_dir / screenshot_filename
                    processed_img.save(str(screenshot_path))
                    screenshots_saved_count += 1
                    if screenshot_saved_path is None:
                        screenshot_saved_path = str(screenshot_dir)  # 保存目录

                print(f"  ✅ 已保存 {screenshots_saved_count} 张截图到: {screenshot_saved_path}/")

                # 保存OCR识别的所有文本到txt文件
                ocr_text_filename = f"{base_name}_ocr.txt"
                ocr_text_path = screenshot_dir / ocr_text_filename

                with open(str(ocr_text_path), 'w', encoding='utf-8') as f:
                    f.write(f"全屏OCR识别结果\n")
                    f.write(f"=" * 80 + "\n")
                    f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"目标模式: {target_pattern}\n")
                    if matched_text:
                        f.write(f"匹配文本: {matched_text}\n")
                        f.write(f"提取值: {extracted_value}\n")
                    else:
                        f.write(f"匹配结果: 未找到匹配\n")
                    f.write(f"预处理版本: {len(preprocessed_images)} 个\n")
                    f.write(f"=" * 80 + "\n\n")

                    # 保存每个版本的识别结果
                    if all_ocr_results:
                        f.write(f"各预处理版本识别结果:\n")
                        f.write("-" * 80 + "\n")
                        for result in all_ocr_results:
                            version = result['version']
                            texts = result['texts']
                            f.write(f"\n[{version}] 识别到 {len(texts)} 个文本:\n")
                            for i, text in enumerate(texts, 1):
                                f.write(f"  {i}. {text}\n")
                        f.write("\n" + "=" * 80 + "\n\n")

                    f.write(f"合并后的唯一文本 (共 {len(all_recognized_texts)} 条):\n")
                    f.write("-" * 80 + "\n")
                    for i, item in enumerate(all_recognized_texts, 1):
                        text = item.get('text', '')
                        conf = item.get('score', 0)
                        f.write(f"{i:4d}. {text} (置信度: {conf:.2f})\n")

                ocr_text_saved_path = str(ocr_text_path)
                print(f"  💾 已保存OCR文本: {ocr_text_saved_path}")

            except Exception as e:
                print(f"  ⚠️ 保存文件失败: {e}")
                import traceback
                traceback.print_exc()
                # 不影响主流程

            # 检查是否找到匹配
            if not extracted_value:
                print(f"\n  ❌ 未找到匹配的文本")
                print(f"  ℹ️  提示: 请查看保存的OCR文本文件检查识别结果")
                return (False, None)

            # 保存到实例变量（用于后续引用）
            if not hasattr(self, 'extracted_data'):
                self.extracted_data = {}
            self.extracted_data[save_to] = extracted_value

            total_time = time_module.time() - screenshot_start_time
            print(f"\n  📊 总耗时: {total_time:.3f}秒")

            # ============================================================================
            # 保存到OCR识别日志数据库
            # ============================================================================
            try:
                from src.services.ocr_logging_service import OCRLoggingService
                from src.utils.database import SessionLocal

                db = SessionLocal()
                try:
                    logging_service = OCRLoggingService(db)

                    # 构建提取结果的JSON
                    extracted_data_json = json.dumps({save_to: extracted_value}, ensure_ascii=False)

                    # 创建OCR识别日志
                    recognition_log = logging_service.create_recognition_log(
                        config_id=self.config.id if self.config else None,
                        task_log_id=self.task_log_id,
                        target_text=target_pattern,  # 保存正则表达式
                        found=True,
                        matched_text=matched_text,  # 保存完整匹配的文本
                        confidence=None,  # 全屏截图没有单个文本的置信度
                        matched_version='fullscreen_extract',  # 标记为全屏提取
                        position_x=None,  # 全屏提取没有具体坐标
                        position_y=None,
                        total_time=total_time,
                        screenshot_time=screenshot_time,
                        preprocessing_time=preprocessing_time,  # 保存预处理时间
                        ocr_time=ocr_time,
                        merge_time=0.0,
                        preprocessing_methods=json.dumps(preprocessing_methods) if preprocessing_methods else None,
                        preprocessing_count=len(preprocessed_images),  # 保存预处理版本数量
                        total_texts_found=len(all_recognized_texts),
                        unique_texts_count=len(all_recognized_texts),
                        screenshot_dir=str(screenshot_dir) if screenshot_saved_path else None,
                        screenshots_saved=screenshots_saved_count,  # 保存截图数量
                        status='success',
                        error_message=None,
                        ocr_results_summary=extracted_data_json  # 【关键】在这里保存提取的数据
                    )

                    print(f"  💾 已保存到OCR日志 (ID: {recognition_log.id})")
                    print(f"     提取数据: {extracted_data_json}")
                    if screenshot_saved_path:
                        print(f"     截图目录: {screenshot_saved_path}/")
                        print(f"     截图数量: {screenshots_saved_count} 张")
                        print(f"     文本文件: {ocr_text_saved_path}")

                finally:
                    db.close()

            except Exception as e:
                print(f"  ⚠️ 保存OCR日志失败: {e}")
                # 不影响主流程，继续执行

            return (True, extracted_value)

        except Exception as e:
            print(f"  ❌ 截图提取失败: {e}")
            import traceback
            traceback.print_exc()
            return (False, None)

    def _cleanup_output_directory(self) -> bool:
        """
        清理输出目录

        根据配置清理输出目录，支持备份选项

        Returns:
            True 表示成功，False 表示失败

        这个SB方法在流程开始时清理输出目录，艹！
        """
        import shutil
        from datetime import datetime

        output_dir = self.config.output_dir_path
        if not output_dir:
            print("  ⚠️ 未配置输出目录路径")
            return False

        print("\n" + "▶" * 40)
        print("步骤 0: 清理输出目录")
        print("▶" * 40)
        print(f"📁 输出目录: {output_dir}")

        try:
            output_path = Path(output_dir)

            # 检查目录是否存在
            if not output_path.exists():
                print(f"  ℹ️  输出目录不存在，无需清理")
                return True

            # 统计文件数量
            file_count = 0
            total_size = 0
            for item in output_path.rglob('*'):
                if item.is_file():
                    file_count += 1
                    try:
                        total_size += item.stat().st_size
                    except:
                        pass

            if file_count == 0:
                print(f"  ℹ️  输出目录为空，无需清理")
                return True

            print(f"  📊 待清理: {file_count} 个文件 ({total_size / 1024 / 1024:.2f} MB)")

            # 备份（如果启用）
            if self.config.output_dir_backup_before_cleanup:
                backup_path_str = self.config.output_dir_backup_path
                if not backup_path_str:
                    # 默认备份到同级目录
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path_str = str(output_path.parent / f"{output_path.name}_backup_{timestamp}")

                backup_path = Path(backup_path_str)

                print(f"\n  💾 备份到: {backup_path}")

                try:
                    # 创建备份
                    if backup_path.exists():
                        print(f"  ⚠️  备份目录已存在，跳过备份")
                    else:
                        shutil.copytree(output_path, backup_path)
                        backup_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
                        print(f"  ✅ 备份完成: {backup_size / 1024 / 1024:.2f} MB")

                except Exception as e:
                    print(f"  ❌ 备份失败: {e}")
                    return False

            # 清理目录
            print(f"\n  🧹 开始清理...")

            deleted_count = 0
            error_count = 0

            for item in output_path.rglob('*'):
                if item.is_file():
                    try:
                        item.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"  ⚠️  删除失败: {item.name} ({e})")
                        error_count += 1

            # 删除空目录
            for item in sorted(output_path.rglob('*'), key=lambda p: len(str(p)), reverse=True):
                if item.is_dir() and not any(item.iterdir()):
                    try:
                        item.rmdir()
                    except:
                        pass

            print(f"  ✅ 清理完成: 删除 {deleted_count} 个文件")
            if error_count > 0:
                print(f"  ⚠️  失败: {error_count} 个文件")

            return True

        except Exception as e:
            print(f"  ❌ 清理失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cleanup(self):
        """清理资源"""
        self.acad = None
        self.current_doc = None

    def monitor_output_files(
        self,
        expected_count: int,
        output_directory: Optional[str] = None,
        check_interval: float = 1.0,
        max_wait_time: float = 300.0,
        file_pattern: str = "*.*"
    ) -> bool:
        """
        监控输出目录文件生成进度

        每隔指定时间检查输出目录的文件数量，并记录到步骤日志中

        Args:
            expected_count: 预期文件数量
            output_directory: 输出目录路径（默认使用配置中的路径）
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒）
            file_pattern: 文件匹配模式

        Returns:
            True 表示文件生成完成，False 表示超时或失败
        """
        import time
        from pathlib import Path

        print("\n" + "▶" * 40)
        print("监控输出文件生成进度")
        print("▶" * 40)

        # 确定输出目录
        if not output_directory:
            output_directory = self.config.output_dir_path

        if not output_directory:
            print("❌ 错误：未配置输出目录")
            return False

        output_path = Path(output_directory)
        if not output_path.exists():
            print(f"❌ 错误：输出目录不存在: {output_directory}")
            return False

        print(f"📂 监控目录: {output_directory}")
        print(f"🎯 预期文件数: {expected_count}")
        print(f"⏱️  检查间隔: {check_interval}秒")
        print(f"⏰ 最大等待: {max_wait_time}秒")
        print(f"📄 文件模式: {file_pattern}")

        # 记录起始步骤日志
        if self.dwg_task_service and self.dwg_task_id:
            step_name = "监控输出文件生成"
            step_order = 100  # 这个步骤在后面

            try:
                step_log = self.dwg_task_service.add_step_log(
                    task_id=self.dwg_task_id,
                    step_name=step_name,
                    step_order=step_order,
                    status='running',
                    message=f"开始监控，预期文件数: {expected_count}",
                    metadata={
                        'expected_count': expected_count,
                        'output_directory': str(output_path),
                        'check_interval': check_interval,
                        'file_pattern': file_pattern
                    }
                )
                print(f"✅ 已创建步骤日志 (ID: {step_log.id})")
            except Exception as e:
                print(f"⚠️ 创建步骤日志失败: {e}")

        # 开始监控
        start_time = time.time()
        check_count = 0
        last_file_count = -1

        while True:
            check_count += 1
            elapsed = time.time() - start_time

            # 检查超时
            if elapsed >= max_wait_time:
                print(f"\n❌ 超时：已等待 {elapsed:.1f}秒，超过最大等待时间 {max_wait_time}秒")

                # 记录超时日志
                if self.dwg_task_service and self.dwg_task_id:
                    try:
                        self.dwg_task_service.add_step_log(
                            task_id=self.dwg_task_id,
                            step_name="监控输出文件生成",
                            step_order=step_order + check_count,
                            status='failed',
                            message=f"监控超时，已等待 {elapsed:.1f}秒",
                            metadata={
                                'check_count': check_count,
                                'current_file_count': last_file_count,
                                'expected_count': expected_count,
                                'elapsed_seconds': elapsed
                            }
                        )
                    except Exception as e:
                        print(f"⚠️ 记录超时日志失败: {e}")

                return False

            # 统计文件数量（递归搜索所有子目录）
            try:
                # 使用 rglob 递归搜索（而不是 glob）
                files = list(output_path.rglob(file_pattern))
                current_file_count = len(files)

                # 调试信息：首次检查时显示文件列表
                if check_count == 1 and current_file_count > 0:
                    print(f"\n  📋 找到的文件（前5个）:")
                    for f in files[:5]:
                        print(f"     - {f.relative_to(output_path)}")
                    if len(files) > 5:
                        print(f"     ... 还有 {len(files) - 5} 个文件")
            except Exception as e:
                print(f"❌ 读取目录失败: {e}")
                import traceback
                traceback.print_exc()
                current_file_count = 0

            # 只在文件数量变化时输出
            if current_file_count != last_file_count:
                percentage = (current_file_count / expected_count * 100) if expected_count > 0 else 0
                print(f"\n🔍 检查 #{check_count} (已用时: {elapsed:.1f}秒)")
                print(f"   📊 文件数量: {current_file_count}/{expected_count} ({percentage:.1f}%)")

                # 记录到步骤日志
                if self.dwg_task_service and self.dwg_task_id:
                    try:
                        self.dwg_task_service.add_step_log(
                            task_id=self.dwg_task_id,
                            step_name="监控输出文件生成",
                            step_order=step_order + check_count,
                            status='running',
                            message=f"检查 #{check_count}: {current_file_count}/{expected_count} 个文件",
                            metadata={
                                'check_count': check_count,
                                'current_file_count': current_file_count,
                                'expected_count': expected_count,
                                'percentage': round(percentage, 2),
                                'elapsed_seconds': round(elapsed, 2)
                            }
                        )
                    except Exception as e:
                        print(f"⚠️ 记录步骤日志失败: {e}")

                last_file_count = current_file_count

            # 检查是否完成
            if current_file_count >= expected_count:
                print(f"\n✅ 完成！文件生成数量达到预期: {current_file_count}/{expected_count}")
                print(f"⏱️  总耗时: {elapsed:.1f}秒")
                print(f"📊 检查次数: {check_count}")

                # 记录完成日志
                if self.dwg_task_service and self.dwg_task_id:
                    try:
                        self.dwg_task_service.add_step_log(
                            task_id=self.dwg_task_id,
                            step_name="监控输出文件生成",
                            step_order=step_order + check_count + 1,
                            status='completed',
                            message=f"监控完成，已生成 {current_file_count} 个文件",
                            metadata={
                                'total_checks': check_count,
                                'final_file_count': current_file_count,
                                'expected_count': expected_count,
                                'total_elapsed_seconds': round(elapsed, 2)
                            }
                        )
                    except Exception as e:
                        print(f"⚠️ 记录完成日志失败: {e}")

                return True

            # 等待下次检查
            time.sleep(check_interval)



def main():
    """主函数 - 使用数据库配置运行"""

    print("=" * 80)
    print("AutoCAD 自动化工作流程 - 数据库配置版")
    print("=" * 80)

    # 选项 1: 使用默认配置
    workflow = ConfigurableAutoCADWorkflow(config_name='default')

    # 选项 2: 使用指定配置ID
    # workflow = ConfigurableAutoCADWorkflow(config_id=1)

    # 可以覆盖配置中的文件路径
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    try:
        success = workflow.run(dwg_file_path=dwg_file)

        if success:
            print("\n🎉 成功！")
        else:
            print("\n❌ 失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        workflow.cleanup()
        input("\n按 Enter 键退出...")


if __name__ == "__main__":
    main()
