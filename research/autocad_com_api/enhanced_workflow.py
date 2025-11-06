"""
增强型 AutoCAD 工作流 - 支持完整的前置/主流程/后置操作

支持的操作类型：
- command: 执行 AutoCAD 命令
- menu: OCR 识别并点击菜单/按钮
- input: 键盘输入
- screenshot_extract: OCR 提取信息并保存到变量
- system_command: 执行系统命令
- directory_cleanup: 清理/删除目录
- file_monitor: 监控文件生成
- mineru_recognition: MinerU PDF 识别（提取图号/表格/技术要求）

Author: CAD Auto Processor Team
Date: 2025-11-04
Updated: 2025-11-05 (Added MinerU integration)
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
import subprocess
from typing import Optional, Dict, Any, List, Tuple
import json
import re
import glob
from datetime import datetime

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
from src.models.autocad_config import AutoCADConfig
from src.utils.image_processing import preprocess_images
from src.utils.step_logger import StepLogger, NullStepLogger

# 延迟导入（避免缺少依赖时整个模块加载失败）
pyautogui = None
requests = None
ImageGrab = None
Image = None
pywinauto_Application = None
pywinauto_find_windows = None


def _ensure_dependencies():
    """确保所有依赖已加载"""
    global pyautogui, requests, ImageGrab, Image, pywinauto_Application, pywinauto_find_windows

    if pyautogui is None:
        import pyautogui as _pyautogui
        pyautogui = _pyautogui

    if requests is None:
        import requests as _requests
        requests = _requests

    if ImageGrab is None:
        from PIL import ImageGrab as _ImageGrab
        from PIL import Image as _Image
        ImageGrab = _ImageGrab
        Image = _Image

    if pywinauto_Application is None:
        from pywinauto import Application
        from pywinauto.findwindows import find_windows
        pywinauto_Application = Application
        pywinauto_find_windows = find_windows


class EnhancedWorkflow:
    """
    增强型 AutoCAD 工作流

    支持：
    - 前置操作（system_command, directory_cleanup）
    - 主流程操作（command, menu, input, screenshot_extract）
    - 后置操作（file_monitor, system_command）
    - 变量系统（保存和引用提取的值）
    """

    def __init__(self, config: Optional[AutoCADConfig] = None,
                 config_name: Optional[str] = None,
                 config_id: Optional[int] = None,
                 task_id: Optional[str] = None,
                 task_service: Optional['DWGTaskService'] = None):
        """
        初始化增强工作流

        Args:
            config: 配置对象
            config_name: 配置名称
            config_id: 配置ID
            task_id: 任务ID
            task_service: 任务服务
        """
        self.acad = None
        self.current_doc = None
        self.current_file = None
        self.task_log_id = None
        self.dwg_task_id = task_id
        self.dwg_task_service = task_service

        # 初始化步骤日志记录器
        if task_id and task_service:
            self.step_logger = StepLogger(task_id, task_service)
        else:
            self.step_logger = NullStepLogger()

        # 变量存储（用于保存 OCR 提取的值）
        self.variables = {}

        # 窗口缓存
        self.cached_window_rect = None
        self.cached_hwnd = None

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

        # 确保依赖已加载
        _ensure_dependencies()

    def run(self, dwg_file_path: Optional[str] = None) -> bool:
        """
        运行完整的自动化流程

        Args:
            dwg_file_path: DWG 文件路径

        Returns:
            是否成功
        """
        # 确定文件路径
        file_path = dwg_file_path or self.config.dwg_file_path
        if not file_path:
            print("❌ 错误：未指定 DWG 文件路径")
            return False

        print("\n" + "=" * 80)
        print(f"增强型 AutoCAD 工作流")
        print("=" * 80)
        print(f"配置: {self.config.config_name}")
        print(f"文件: {file_path}")
        print("=" * 80)

        try:
            # 解析配置
            operations = self._parse_operations()
            if not operations:
                print("⚠️  没有配置任何操作")
                return False

            print(f"\n📋 总共 {len(operations)} 个操作")

            # 执行所有操作
            for i, operation in enumerate(operations, 1):
                print(f"\n{'▶' * 40}")
                print(f"步骤 {i}/{len(operations)}: {operation.get('description', operation.get('type'))}")
                print(f"{'▶' * 40}")

                success = self._execute_operation(operation, file_path)

                if not success:
                    # 检查是否必需
                    if operation.get('required', True):
                        print(f"❌ 必需步骤失败，终止流程")
                        return False
                    else:
                        print(f"⚠️  可选步骤失败，继续执行")

                # 等待时间
                wait_time = operation.get('wait_time', 0)
                if wait_time > 0:
                    print(f"⏳ 等待 {wait_time} 秒...")
                    time.sleep(wait_time)

            print("\n" + "=" * 80)
            print("✅ 工作流执行完成！")
            print("=" * 80)
            return True

        except Exception as e:
            print(f"\n❌ 工作流执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()

    def _parse_operations(self) -> List[Dict[str, Any]]:
        """
        解析配置中的操作列表

        Returns:
            操作列表
        """
        if not self.config.menu_operations:
            return []

        operations = json.loads(self.config.menu_operations) if isinstance(
            self.config.menu_operations, str) else self.config.menu_operations

        # 支持两种格式：
        # 1. 扁平列表: [{"type": "command"}, ...]
        # 2. 分阶段: {"pre_operations": [...], "main_operations": [...], "post_operations": [...]}

        if isinstance(operations, dict):
            # 分阶段格式
            all_ops = []
            all_ops.extend(operations.get('pre_operations', []))
            all_ops.extend(operations.get('main_operations', []))
            all_ops.extend(operations.get('post_operations', []))

            # 初始化变量
            variables = operations.get('variables', {})
            for var_name, var_info in variables.items():
                self.variables[var_name] = var_info.get('default', 0)

            return all_ops
        else:
            # 扁平列表格式
            return operations

    def _execute_operation(self, operation: Dict[str, Any], dwg_file_path: str) -> bool:
        """
        执行单个操作

        Args:
            operation: 操作配置
            dwg_file_path: DWG 文件路径

        Returns:
            是否成功
        """
        op_type = operation.get('type')

        try:
            if op_type == 'system_command':
                return self._execute_system_command(operation)
            elif op_type == 'directory_cleanup':
                return self._execute_directory_cleanup(operation)
            elif op_type == 'command':
                return self._execute_autocad_command(operation, dwg_file_path)
            elif op_type == 'menu':
                return self._execute_menu_click(operation)
            elif op_type == 'input':
                return self._execute_input(operation)
            elif op_type == 'screenshot_extract':
                return self._execute_screenshot_extract(operation)
            elif op_type == 'file_monitor':
                return self._execute_file_monitor(operation)
            elif op_type == 'mineru_recognition':
                return self._execute_mineru_recognition(operation)
            else:
                print(f"⚠️  未知操作类型: {op_type}")
                return False

        except Exception as e:
            print(f"❌ 操作执行异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_system_command(self, operation: Dict[str, Any]) -> bool:
        """执行系统命令"""
        command = operation.get('command', '')
        ignore_error = operation.get('ignore_error', False)

        with self.step_logger.log_step("执行系统命令") as step:
            step.add_metadata({
                "command": command,
                "ignore_error": ignore_error
            })

            print(f"  💻 系统命令: {command}")

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                step.add_metadata({
                    "return_code": result.returncode,
                    "stdout": result.stdout[:500] if result.stdout else None,  # 限制长度
                    "stderr": result.stderr[:500] if result.stderr else None
                })

                if result.returncode == 0 or ignore_error:
                    print(f"  ✅ 命令执行完成")
                    step.add_metadata({"success": True})
                    return True
                else:
                    print(f"  ❌ 命令执行失败: {result.stderr}")
                    step.add_metadata({"success": False, "error": "命令返回非零退出码"})
                    return False

            except Exception as e:
                if ignore_error:
                    print(f"  ⚠️  命令执行异常（已忽略）: {e}")
                    step.add_metadata({"exception": str(e), "ignored": True})
                    return True
                else:
                    print(f"  ❌ 命令执行异常: {e}")
                    step.add_metadata({"error": str(e)})
                    raise  # 继续传播异常

    def _execute_directory_cleanup(self, operation: Dict[str, Any]) -> bool:
        """清理目录"""
        path = operation.get('path', '')
        create_if_not_exist = operation.get('create_if_not_exist', False)

        with self.step_logger.log_step("清理目录") as step:
            step.add_metadata({
                "path": path,
                "create_if_not_exist": create_if_not_exist
            })

            print(f"  🗑️  清理目录: {path}")

            try:
                path_obj = Path(path)
                deleted_files_count = 0
                deleted_dirs_count = 0

                if path_obj.exists():
                    # 删除所有文件
                    import shutil
                    for item in path_obj.iterdir():
                        if item.is_file():
                            item.unlink()
                            print(f"     删除文件: {item.name}")
                            deleted_files_count += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            print(f"     删除目录: {item.name}")
                            deleted_dirs_count += 1
                    print(f"  ✅ 目录已清空")
                    step.add_metadata({
                        "deleted_files": deleted_files_count,
                        "deleted_dirs": deleted_dirs_count
                    })

                if create_if_not_exist and not path_obj.exists():
                    path_obj.mkdir(parents=True, exist_ok=True)
                    print(f"  ✅ 目录已创建")
                    step.add_metadata({"created": True})

                step.add_metadata({"success": True})
                return True

            except Exception as e:
                print(f"  ❌ 目录清理失败: {e}")
                step.add_metadata({"error": str(e)})
                raise  # 继续传播异常

    def _execute_autocad_command(self, operation: Dict[str, Any], dwg_file_path: str) -> bool:
        """执行 AutoCAD 命令（首次执行时打开文件）"""
        method = operation.get('method', 'keyboard')
        text = operation.get('text', '')

        with self.step_logger.log_step("执行AutoCAD命令") as step:
            step.add_metadata({"method": method, "command_text": text})

            # 如果 AutoCAD 未启动，先打开文件
            if self.acad is None:
                print(f"  📂 打开 AutoCAD 文件...")
                if not self._open_autocad_file(dwg_file_path):
                    step.add_metadata({"error": "打开文件失败"})
                    return False

            # 执行命令
            if method == 'keyboard':
                try:
                    # 激活窗口并检查结果
                    if not self._activate_autocad_window():
                        print("  ⚠️  窗口激活失败，跳过键盘输入")
                        step.add_metadata({"error": "窗口激活失败"})
                        return False

                    print(f"  ⌨️  键盘输入命令: {text}")
                    time.sleep(0.5)

                    pyautogui.typewrite(text, interval=0.1)
                    time.sleep(0.5)

                    pyautogui.press("enter")
                    print(f"  ✅ 命令已执行")
                    step.add_metadata({"success": True})
                    return True
                except Exception as e:
                    print(f"  ❌ 命令执行失败: {e}")
                    step.add_metadata({"error": str(e)})
                    raise  # 继续传播异常，让 StepLogger 记录堆栈
            else:
                print(f"  ⚠️  不支持的命令方法: {method}")
                step.add_metadata({"error": f"不支持的方法: {method}"})
                return False

    def _execute_menu_click(self, operation: Dict[str, Any]) -> bool:
        """OCR 识别并点击菜单/按钮"""
        method = operation.get('method', 'ocr')
        text = operation.get('text', '')

        with self.step_logger.log_step("OCR识别并点击菜单") as step:
            step.add_metadata({"method": method, "target_text": text})

            if method != 'ocr':
                print(f"  ⚠️  不支持的菜单方法: {method}")
                step.add_metadata({"error": f"不支持的方法: {method}"})
                return False

            print(f"  🔍 OCR 识别按钮: {text}")

            # 截图
            image = self._capture_autocad_window()
            if image is None:
                step.add_metadata({"error": "截图失败"})
                return False

            # OCR 识别
            position = self._find_text_position(image, text)
            if not position:
                print(f"  ❌ 未找到按钮: {text}")
                step.add_metadata({"error": f"未找到按钮: {text}"})
                return False

            # 点击
            x, y = position
            print(f"  🖱️  点击位置: ({x}, {y})")
            step.add_metadata({"click_position": {"x": x, "y": y}})

            pyautogui.moveTo(x, y, duration=0.3)
            time.sleep(0.2)
            pyautogui.click()

            print(f"  ✅ 按钮已点击")
            step.add_metadata({"success": True})
            return True

    def _execute_input(self, operation: Dict[str, Any]) -> bool:
        """键盘输入"""
        text = operation.get('text', '')
        wait_before_enter = operation.get('wait_before_enter', 0)
        enter_count = operation.get('enter_count', 1)
        wait_between_enters = operation.get('wait_between_enters', 0.5)

        with self.step_logger.log_step("键盘输入") as step:
            step.add_metadata({
                "input_text": text,
                "wait_before_enter": wait_before_enter,
                "enter_count": enter_count
            })

            print(f"  ⌨️  输入文本: {text}")

            try:
                # 输入文本
                pyautogui.typewrite(text, interval=0.1)

                # 等待
                if wait_before_enter > 0:
                    time.sleep(wait_before_enter)

                # 回车
                for i in range(enter_count):
                    pyautogui.press("enter")
                    if i < enter_count - 1 and wait_between_enters > 0:
                        time.sleep(wait_between_enters)

                print(f"  ✅ 输入完成")
                step.add_metadata({"success": True})
                return True

            except Exception as e:
                print(f"  ❌ 输入失败: {e}")
                step.add_metadata({"error": str(e)})
                raise  # 继续传播异常

    def _execute_screenshot_extract(self, operation: Dict[str, Any]) -> bool:
        """OCR 提取信息并保存到变量"""
        target_pattern = operation.get('target_pattern', '')
        save_to = operation.get('save_to', '')

        with self.step_logger.log_step("OCR提取信息") as step:
            step.add_metadata({
                "target_pattern": target_pattern,
                "save_to": save_to
            })

            print(f"  📸 OCR 提取信息")
            print(f"     模式: {target_pattern}")
            print(f"     保存到: {save_to}")

            try:
                # 截图
                image = self._capture_autocad_window()
                if image is None:
                    step.add_metadata({"error": "截图失败"})
                    return False

                # OCR 识别
                ocr_results = self._ocr_image(image)
                if not ocr_results:
                    step.add_metadata({"error": "OCR识别失败"})
                    return False

                # 提取文本
                all_text = "\n".join([item.get('text', '') for item in ocr_results.get('data', [])])
                step.add_metadata({"ocr_text_length": len(all_text)})

                # 正则匹配
                match = re.search(target_pattern, all_text)
                if match:
                    value = match.group(1)
                    self.variables[save_to] = int(value) if value.isdigit() else value
                    print(f"  ✅ 提取成功: {save_to} = {self.variables[save_to]}")
                    step.add_metadata({
                        "success": True,
                        "extracted_value": self.variables[save_to]
                    })
                    return True
                else:
                    print(f"  ⚠️  未匹配到信息")
                    step.add_metadata({"error": "正则匹配失败", "ocr_text_preview": all_text[:200]})
                    return False

            except Exception as e:
                step.add_metadata({"error": str(e)})
                raise  # 继续传播异常

    def _execute_file_monitor(self, operation: Dict[str, Any]) -> bool:
        """监控文件生成"""
        watch_path = operation.get('watch_path', '')
        file_pattern = operation.get('file_pattern', '*.pdf')
        expected_count_variable = operation.get('expected_count_variable', '')
        check_interval = operation.get('check_interval', 2)
        max_wait_time = operation.get('max_wait_time', 600)
        stable_duration = operation.get('stable_duration', 10)

        with self.step_logger.log_step("监控文件生成") as step:
            step.add_metadata({
                "watch_path": watch_path,
                "file_pattern": file_pattern,
                "check_interval": check_interval,
                "max_wait_time": max_wait_time,
                "stable_duration": stable_duration
            })

            print(f"  👀 监控文件生成")
            print(f"     路径: {watch_path}")
            print(f"     模式: {file_pattern}")

            # 获取期望数量
            expected_count = 0
            if expected_count_variable and expected_count_variable in self.variables:
                expected_count = self.variables[expected_count_variable]
                print(f"     期望数量: {expected_count}")
                step.add_metadata({"expected_count": expected_count})

            try:
                # 监控
                start_time = time.time()
                last_count = 0
                stable_start_time = None

                while True:
                    elapsed = time.time() - start_time

                    # 检查超时
                    if elapsed > max_wait_time:
                        print(f"  ⚠️  监控超时（{max_wait_time}秒）")
                        step.add_metadata({
                            "timeout": True,
                            "elapsed_time": elapsed,
                            "last_file_count": last_count
                        })
                        break

                    # 统计文件
                    files = list(Path(watch_path).glob(file_pattern))
                    current_count = len(files)

                    # 检查是否稳定
                    if current_count == last_count:
                        if stable_start_time is None:
                            stable_start_time = time.time()
                        elif time.time() - stable_start_time >= stable_duration:
                            # 稳定了足够长时间
                            print(f"  ✅ 文件生成稳定: {current_count} 个文件")

                            # 验证数量
                            count_match = True
                            if expected_count > 0 and current_count != expected_count:
                                print(f"  ⚠️  数量不匹配: 期望{expected_count}，实际{current_count}")
                                count_match = False

                            self.variables['actual_generated_files'] = current_count

                            step.add_metadata({
                                "success": True,
                                "final_count": current_count,
                                "count_match": count_match,
                                "total_elapsed_time": time.time() - start_time
                            })
                            return True
                    else:
                        print(f"  📁 当前文件数: {current_count}")
                        stable_start_time = None
                        last_count = current_count

                    time.sleep(check_interval)

                # 超时后仍返回 True（根据原始逻辑）
                return True

            except Exception as e:
                step.add_metadata({"error": str(e)})
                raise  # 继续传播异常

    def _open_autocad_file(self, dwg_file_path: str) -> bool:
        """打开 AutoCAD 文件（简化版）"""
        with self.step_logger.log_step("打开AutoCAD文件") as step:
            step.add_metadata({
                "dwg_file_path": dwg_file_path,
                "force_close_existing": self.config.force_close_existing
            })

            print(f"  🚀 启动 AutoCAD...")

            # 关闭现有进程
            if self.config.force_close_existing:
                self._close_all_autocad_processes()
                step.add_metadata({"closed_existing_processes": True})

            # 启动 AutoCAD
            acad_exe = self.config.autocad_exe_path or r"C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"
            step.add_metadata({"autocad_exe_path": acad_exe})

            try:
                subprocess.Popen([acad_exe, dwg_file_path], shell=False)
                print(f"  ✅ AutoCAD 已启动")
            except Exception as e:
                print(f"  ❌ 启动失败: {e}")
                step.add_metadata({"error": f"启动失败: {str(e)}"})
                raise  # 继续传播异常

            # 等待连接
            wait_time = self.config.startup_wait_time or 10
            print(f"  ⏳ 等待 AutoCAD 启动...")
            step.add_metadata({"startup_wait_time": wait_time})
            time.sleep(wait_time)

            try:
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                print(f"  ✅ 已连接到 AutoCAD")
                step.add_metadata({"com_connection": "success"})

                if self.acad.Documents.Count > 0:
                    self.current_doc = self.acad.ActiveDocument
                    print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                    step.add_metadata({
                        "success": True,
                        "document_name": self.current_doc.Name,
                        "document_count": self.acad.Documents.Count
                    })
                    return True
                else:
                    self.current_doc = self.acad.Documents.Open(dwg_file_path)
                    print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                    step.add_metadata({
                        "success": True,
                        "document_name": self.current_doc.Name,
                        "opened_manually": True
                    })
                    return True

            except Exception as e:
                print(f"  ❌ 连接失败: {e}")
                step.add_metadata({"error": f"连接失败: {str(e)}"})
                raise  # 继续传播异常

    def _capture_autocad_window(self) -> Optional[Any]:
        """截取 AutoCAD 窗口"""
        try:
            import win32gui

            hwnd = self._find_target_window()
            if not hwnd:
                print("  ❌ 未找到窗口")
                return None

            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect

            image = ImageGrab.grab(bbox=(left, top, right, bottom))
            return image

        except Exception as e:
            print(f"  ❌ 截图失败: {e}")
            return None

    def _find_target_window(self) -> Optional[int]:
        """
        查找 AutoCAD 窗口（支持 pywinauto 和原生 win32gui）

        Returns:
            窗口句柄 (hwnd)，如果未找到返回 None
        """
        try:
            # 优先使用 pywinauto 查找（更可靠）
            if pywinauto_find_windows is not None:
                windows = pywinauto_find_windows(title_re=".*AutoCAD.*")
                if windows:
                    return windows[0]

            # 降级到 win32gui（兼容性）
            import win32gui

            def enum_windows_callback(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and 'AutoCAD' in title:
                        param.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)

            return windows[0] if windows else None

        except Exception as e:
            print(f"  ❌ 查找窗口失败: {e}")
            return None

    def _ocr_image(self, image: Any) -> Optional[Dict]:
        """OCR 识别图像"""
        try:
            from io import BytesIO
            import base64

            # 转换为 base64
            buffered = BytesIO()
            image.save(buffered, format='PNG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            # OCR 请求
            url = f"{self.config.umi_ocr_service_url}{self.config.umi_ocr_api_path}"
            data = {
                "base64": img_base64,
                "options": {
                    "ocr.limit_side_len": self.config.umi_ocr_limit_side_len or 2880,
                    "data.format": "dict"
                }
            }

            response = requests.post(url, json=data, timeout=self.config.umi_ocr_timeout or 30)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 100:
                    return result

            return None

        except Exception as e:
            print(f"  ❌ OCR 失败: {e}")
            return None

    def _find_text_position(self, image: Any, target_text: str) -> Optional[Tuple[int, int]]:
        """查找文本位置"""
        ocr_results = self._ocr_image(image)
        if not ocr_results:
            return None

        for item in ocr_results.get('data', []):
            text = item.get('text', '')
            if target_text in text or text in target_text:
                box = item.get('box', [])
                if box and len(box) >= 4:
                    x = (box[0][0] + box[2][0]) // 2
                    y = (box[0][1] + box[2][1]) // 2

                    # 转换为屏幕坐标
                    import win32gui
                    hwnd = self._find_target_window()
                    if hwnd:
                        rect = win32gui.GetWindowRect(hwnd)
                        return (rect[0] + x, rect[1] + y)

        return None

    def _activate_autocad_window(self, max_retries: int = 3) -> bool:
        """
        激活 AutoCAD 窗口（增强版，三种激活方法）

        激活策略（按优先级尝试）：
        0. Alt 键模拟 + SetForegroundWindow（最推荐，成功率最高）
        1. pywinauto 的 set_focus（备选）
        2. 直接 win32gui.SetForegroundWindow（兜底）

        Args:
            max_retries: 最大重试次数（默认 3 次）

        Returns:
            True 表示激活成功，False 表示所有方法都失败
        """
        with self.step_logger.log_step("激活AutoCAD窗口") as step:
            _ensure_dependencies()  # 确保 pywinauto 已加载

            step.add_metadata({"max_retries": max_retries})

            for attempt in range(max_retries):
                try:
                    # 先查找窗口句柄（统一查找一次）
                    hwnd = self._find_target_window()
                    if not hwnd:
                        print(f"  ❌ 未找到 AutoCAD 窗口")
                        if attempt < max_retries - 1:
                            time.sleep(0.5)
                        continue

                    step.add_metadata({"window_handle": hwnd, "attempt": attempt + 1})

                    # 方法 0: Alt 键模拟激活（最推荐，成功率最高）
                    try:
                        import win32api
                        import win32con
                        import win32gui

                        # 先恢复窗口（如果最小化）
                        try:
                            win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                            time.sleep(0.05)
                        except:
                            pass

                        # 模拟按下 Alt 键（触发系统允许前台切换）
                        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                        time.sleep(0.05)  # 短暂延迟确保按键生效

                        # 激活窗口
                        result = win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.05)

                        # 释放 Alt 键
                        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

                        # 验证是否成功（检查前台窗口）
                        foreground_hwnd = win32gui.GetForegroundWindow()
                        if foreground_hwnd == hwnd:
                            print(f"  ✅ 窗口已激活 (Alt+SetForegroundWindow)")
                            step.add_metadata({"method": "alt_setforeground", "success": True})
                            return True
                        else:
                            print(f"  ⚠️  Alt 键激活失败: 前台窗口不匹配")
                            step.add_metadata({"alt_error": "foreground_mismatch"})
                    except ImportError as e_import:
                        print(f"  ⚠️  Alt 键激活失败: {e_import} (缺少 win32api/win32gui)")
                        step.add_metadata({"alt_error": f"ImportError: {str(e_import)}"})
                    except Exception as e_alt:
                        print(f"  ⚠️  Alt 键激活失败: {e_alt}")
                        step.add_metadata({"alt_error": str(e_alt)})

                    # 方法 1: 使用 pywinauto（备选）
                    if pywinauto_Application is not None:
                        try:
                            app = pywinauto_Application().connect(handle=hwnd)
                            window = app.window(handle=hwnd)
                            window.set_focus()
                            print(f"  ✅ 窗口已激活 (pywinauto)")
                            step.add_metadata({"method": "pywinauto", "success": True})
                            return True
                        except Exception as e_pwa:
                            print(f"  ⚠️  pywinauto 激活失败: {e_pwa}")
                            step.add_metadata({"pywinauto_error": str(e_pwa)})
                            # 继续尝试方法 2

                    # 方法 2: 直接 SetForegroundWindow（兜底方案）
                    try:
                        import win32gui
                        win32gui.SetForegroundWindow(hwnd)
                        print(f"  ✅ 窗口已激活 (win32gui)")
                        step.add_metadata({"method": "win32gui", "success": True})
                        return True
                    except ImportError:
                        print(f"  ⚠️  win32gui 不可用")
                        step.add_metadata({"win32gui_error": "ImportError"})
                    except Exception as e_w32:
                        print(f"  ⚠️  win32gui 激活失败: {e_w32}")
                        step.add_metadata({"win32gui_error": str(e_w32)})

                except Exception as e:
                    print(f"  ⚠️  激活窗口失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                # 重试前等待
                if attempt < max_retries - 1:
                    time.sleep(0.5)

            step.add_metadata({"success": False, "all_retries_failed": True})
            return False

    def _close_all_autocad_processes(self):
        """关闭所有 AutoCAD 进程"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=5)
            time.sleep(2)
        except:
            pass

    def _execute_mineru_recognition(self, operation: Dict[str, Any]) -> bool:
        """执行 MinerU PDF 识别"""
        pdf_directory = operation.get('pdf_directory', '')
        pdf_pattern = operation.get('pdf_pattern', '*.pdf')

        with self.step_logger.log_step("MinerU识别PDF") as step:
            step.add_metadata({
                "pdf_directory": pdf_directory,
                "pdf_pattern": pdf_pattern,
                "mineru_api_url": getattr(self.config, 'mineru_api_url', None),
                "batch_size": getattr(self.config, 'mineru_batch_size', None)
            })

            print(f"  🔍 MinerU 批量识别 PDF")
            print(f"     目录: {pdf_directory}")
            print(f"     模式: {pdf_pattern}")

            # 检查是否启用
            if not getattr(self.config, 'mineru_enabled', False):
                print(f"  ⚠️  MinerU 未启用（配置：mineru_enabled=False）")
                step.add_metadata({"skipped": True, "reason": "MinerU未启用"})
                return True  # 跳过但不失败

            try:
                # 延迟导入 MinerU 服务（避免循环导入）
                from src.services.mineru_service import MinerUService

                # 创建数据库会话
                db = SessionLocal()
                try:
                    mineru_service = MinerUService(
                        config=self.config,
                        task_id=self.dwg_task_id,
                        db_session=db
                    )

                    # 批量识别
                    result = mineru_service.batch_recognize_pdfs(pdf_directory, pdf_pattern)

                    print(f"  ✅ 识别完成")
                    print(f"     总文件数: {result.get('total_files', 0)}")
                    print(f"     成功: {result.get('success_count', 0)}")
                    print(f"     失败: {result.get('failed_count', 0)}")

                    step.add_metadata({
                        "success": True,
                        "total_files": result.get('total_files', 0),
                        "success_count": result.get('success_count', 0),
                        "failed_count": result.get('failed_count', 0)
                    })

                    return result.get('success', False)

                finally:
                    db.close()

            except Exception as e:
                print(f"  ❌ MinerU 识别失败: {e}")
                step.add_metadata({"error": str(e)})
                raise  # 继续传播异常

    def cleanup(self):
        """清理资源"""
        if self.config.close_cad_after_completion and self.acad:
            try:
                self.acad.Quit()
            except:
                pass

        self.acad = None
        self.current_doc = None
