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
from typing import Optional, Dict, Any
import json

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
from src.models.autocad_config import AutoCADConfig


class ConfigurableAutoCADWorkflow:
    """
    基于数据库配置的 AutoCAD 自动化工作流程

    支持从数据库读取所有配置参数
    """

    def __init__(self, config: Optional[AutoCADConfig] = None,
                 config_name: Optional[str] = None,
                 config_id: Optional[int] = None):
        """
        初始化工作流程

        Args:
            config: 配置对象（直接传入）
            config_name: 配置名称（从数据库查询）
            config_id: 配置ID（从数据库查询）
        """
        self.acad = None
        self.current_doc = None
        self.current_file = None
        self.task_log_id = None

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

            print("\n" + "=" * 80)
            print("✅ 自动化流程完成！")
            print("=" * 80)

            self._log_task_end('success')
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

        self.current_file = str(dwg_path.absolute())
        print(f"📄 目标文件: {self.current_file}")

        # 关闭现有进程
        if self.config.force_close_existing:
            print("\n🔍 检查现有 AutoCAD 进程...")
            if self._is_autocad_running():
                closed_count = self._close_all_autocad_processes()
                print(f"✅ 关闭流程完成（处理了 {closed_count} 个进程）")
            else:
                print("  ✅ 没有运行中的AutoCAD进程")

        # 启动 AutoCAD（带重试机制）
        print(f"\n🚀 启动 AutoCAD...")
        max_start_retries = 3
        for start_attempt in range(max_start_retries):
            try:
                # 清理可能残留的COM对象引用
                if start_attempt > 0:
                    print(f"  [重试 {start_attempt}/{max_start_retries}]")
                    try:
                        import pythoncom
                        pythoncom.CoUninitialize()
                        time.sleep(1)
                        pythoncom.CoInitialize()
                    except:
                        pass

                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                self.acad.Visible = True
                print("✅ AutoCAD 已启动")
                break

            except Exception as e:
                if start_attempt < max_start_retries - 1:
                    print(f"  ⚠️ 启动失败: {e}")
                    print(f"  ⏳ 等待 5 秒后重试...")
                    time.sleep(5)
                else:
                    print(f"❌ 启动失败（已重试{max_start_retries}次）: {e}")
                    return False
        else:
            print("❌ 无法启动 AutoCAD")
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

                        success = self._click_menu_by_ocr(text)
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

    def _click_menu_by_ocr(self, text: str) -> bool:
        """使用OCR文字识别点击菜单（最智能方案）"""
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

        # 导入OCR库（优先EasyOCR，更轻量）
        try:
            import easyocr
            ocr_type = 'easyocr'
        except ImportError:
            try:
                from paddleocr import PaddleOCR
                ocr_type = 'paddleocr'
            except ImportError:
                print(f"  ❌ 缺少OCR库，请安装以下之一:")
                print(f"     pip install easyocr  (推荐，更简单)")
                print(f"     pip install paddleocr paddlepaddle")
                return False

        print(f"  查找文本: '{text}'")

        try:
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
                print(f"  ❌ 未找到AutoCAD窗口")
                return False

            hwnd, title = windows[0]

            # 激活窗口
            try:
                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.5)
            except Exception as e:
                # SetForegroundWindow可能失败（窗口已在前台），继续执行
                print(f"  ⚠️ 激活窗口失败（可能已在前台），继续执行")

            # 截取窗口
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
            if result == 0:
                saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            image = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # 清理资源
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            print(f"  截图完成: {width}x{height}")

            # OCR识别
            img_array = np.array(image)

            if ocr_type == 'easyocr':
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

                # 查找匹配的文本
                for detection in result:
                    box = detection[0]
                    recognized_text = detection[1]
                    confidence = detection[2]

                    if text in recognized_text:
                        # 计算中心点
                        x_coords = [point[0] for point in box]
                        y_coords = [point[1] for point in box]
                        center_x = int(sum(x_coords) / len(x_coords))
                        center_y = int(sum(y_coords) / len(y_coords))

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        print(f"  ✅ 找到文本: '{recognized_text}' (置信度:{confidence:.2f})")
                        print(f"  位置: ({screen_x}, {screen_y})")

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

                    if text in recognized_text:
                        # 计算中心点
                        x_coords = [point[0] for point in box]
                        y_coords = [point[1] for point in box]
                        center_x = int(sum(x_coords) / len(x_coords))
                        center_y = int(sum(y_coords) / len(y_coords))

                        # 转换为屏幕坐标
                        screen_x = left + center_x
                        screen_y = top + center_y

                        print(f"  ✅ 找到文本: '{recognized_text}' (置信度:{confidence:.2f})")
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

    def cleanup(self):
        """清理资源"""
        self.acad = None
        self.current_doc = None


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
