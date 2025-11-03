"""
AutoCAD Batch Plot (bplot) 全自动化工作流

研究目标：
1. 打开CAD文件
2. 验证加载完成
3. 执行 bplot 命令
4. OCR 识别并点击"选择批量打印图纸"按钮
5. 键盘输入 all 并回车
6. 再次截图，提取选中图纸数量和总页数信息

Author: CAD Auto Processor Team
Date: 2025-11-02
"""

from __future__ import annotations  # 延迟类型注解评估

import win32com.client
import pywintypes
import psutil
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, List
import re

# 延迟导入（避免缺少依赖时整个模块加载失败）
pyautogui = None
requests = None
ImageGrab = None
Image = None


def _ensure_dependencies():
    """确保所有依赖已加载"""
    global pyautogui, requests, ImageGrab, Image

    if pyautogui is None:
        try:
            import pyautogui as _pyautogui
            pyautogui = _pyautogui
            print("  ✅ 已加载 pyautogui")
        except ImportError as e:
            print(f"  ❌ pyautogui 未安装: {e}")
            print(f"     请运行: pip install pyautogui")
            raise

    if requests is None:
        try:
            import requests as _requests
            requests = _requests
            print("  ✅ 已加载 requests")
        except ImportError as e:
            print(f"  ❌ requests 未安装: {e}")
            print(f"     请运行: pip install requests")
            raise

    if ImageGrab is None:
        try:
            from PIL import ImageGrab as _ImageGrab
            from PIL import Image as _Image
            ImageGrab = _ImageGrab
            Image = _Image
            print("  ✅ 已加载 PIL (Pillow)")
        except ImportError as e:
            print(f"  ❌ Pillow 未安装: {e}")
            print(f"     请运行: pip install pillow")
            raise


class BplotAutoWorkflow:
    """bplot命令全自动化工作流"""

    def __init__(self, umi_ocr_url: str = "http://127.0.0.1:11224/api/ocr"):
        self.acad = None
        self.current_doc = None
        self.current_file = None
        self.umi_ocr_url = umi_ocr_url
        self.screenshot_dir = Path("screenshots/bplot_auto")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # 检查依赖
        print("\n🔍 检查依赖库...")
        try:
            _ensure_dependencies()
            print("✅ 所有依赖已就绪\n")
        except ImportError as e:
            print(f"\n❌ 依赖检查失败: {e}")
            raise

    def run(self, dwg_file_path: str) -> bool:
        """
        运行bplot自动化工作流

        Args:
            dwg_file_path: DWG文件路径

        Returns:
            True 表示成功，False 表示失败
        """
        print("\n" + "=" * 80)
        print("AutoCAD Batch Plot 全自动化工作流")
        print("=" * 80)
        print(f"文件: {dwg_file_path}")
        print("=" * 80)

        try:
            # 步骤 1: 打开CAD和文件
            if not self.step1_open_cad_file(dwg_file_path):
                return False

            # 步骤 2: 验证文件加载
            if not self.step2_verify_loaded():
                return False

            # 步骤 3: 执行 bplot 命令
            print(f"\n{'🔹' * 40}")
            print(">>> 准备执行步骤 3...")
            print(f"{'🔹' * 40}")
            if not self.step3_execute_bplot():
                print("❌ 步骤 3 失败，终止流程")
                return False
            print(f"\n{'✅' * 40}")
            print(">>> 步骤 3 完成，准备进入步骤 4...")
            print(f"{'✅' * 40}")

            # 步骤 4: OCR识别并点击"选择批量打印图纸"按钮
            print(f"\n{'🔹' * 40}")
            print(">>> 准备执行步骤 4（OCR识别）...")
            print(f"{'🔹' * 40}")
            if not self.step4_click_select_button():
                print("❌ 步骤 4 失败，终止流程")
                return False
            print(f"\n{'✅' * 40}")
            print(">>> 步骤 4 完成")
            print(f"{'✅' * 40}")

            # 步骤 5: 输入 all 并回车
            if not self.step5_input_all():
                return False

            # 步骤 6: 截图并提取图纸信息
            sheet_info = self.step6_extract_sheet_info()
            if sheet_info:
                print(f"\n✅ 成功提取图纸信息:")
                print(f"   选中图纸: {sheet_info['selected_sheets']}")
                print(f"   总页数: {sheet_info['total_pages']}")

            print("\n🎉 bplot自动化流程完成！")
            return True

        except Exception as e:
            print(f"\n❌ 流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step1_open_cad_file(self, dwg_file_path: str) -> bool:
        """步骤 1: 打开CAD和文件"""
        print("\n" + "▶" * 40)
        print("步骤 1: 打开CAD和文件")
        print("▶" * 40)

        # 验证文件
        dwg_path = Path(dwg_file_path)
        if not dwg_path.exists():
            print(f"❌ 文件不存在: {dwg_file_path}")
            return False

        self.current_file = str(dwg_path.absolute())
        print(f"📄 文件: {self.current_file}")

        # 关闭现有进程
        print("\n🔍 检查现有 AutoCAD 进程...")
        if self._is_autocad_running():
            closed_count = self._close_all_autocad_processes()
            print(f"✅ 已关闭 {closed_count} 个进程")
        else:
            print("  ✅ 没有运行中的AutoCAD进程")

        # 启动 AutoCAD 并打开文件
        print(f"\n🚀 启动 AutoCAD...")
        acad_exe = r"C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

        # 检查路径
        if not Path(acad_exe).exists():
            common_paths = [
                r"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe",
                r"C:\Program Files (x86)\Autodesk\AutoCAD 2014\acad.exe",
            ]
            for path in common_paths:
                if Path(path).exists():
                    acad_exe = path
                    break
            else:
                print(f"❌ 无法找到AutoCAD可执行文件")
                return False

        print(f"  📂 AutoCAD: {acad_exe}")

        # 启动进程
        try:
            process = subprocess.Popen([acad_exe, self.current_file], shell=False)
            print(f"  ✅ 进程已启动 (PID: {process.pid})")
        except Exception as e:
            print(f"  ❌ 启动失败: {e}")
            return False

        # 初始化COM
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except:
            pass

        # 等待AutoCAD启动并连接COM
        print(f"\n  ⏳ 等待 AutoCAD 启动...")
        wait_time = 30.0
        check_interval = 2.0
        max_checks = int(wait_time / check_interval)

        for i in range(max_checks):
            try:
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                print(f"  ✅ 已连接到 AutoCAD (用时: {(i + 1) * check_interval:.1f} 秒)")
                print(f"     版本: {self.acad.Name}")
                break
            except Exception as e:
                if i == 0 or i == max_checks - 1:
                    print(f"     等待中... ({(i + 1) * check_interval:.1f}/{wait_time} 秒)")
                time.sleep(check_interval)
        else:
            try:
                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                print(f"  ✅ 已通过Dispatch连接")
            except:
                print(f"  ❌ 无法连接到AutoCAD COM")
                return False

        # 额外等待确保文件加载
        print(f"  ⏳ 等待文件加载完成...")
        time.sleep(5)

        # 验证文档打开
        try:
            if self.acad.Documents.Count > 0:
                self.current_doc = self.acad.ActiveDocument
                print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                return True
            else:
                print(f"  ⏳ 通过COM打开文件...")
                self.current_doc = self.acad.Documents.Open(self.current_file)
                print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                return True
        except Exception as e:
            print(f"  ❌ 文件打开失败: {e}")
            return False

    def step2_verify_loaded(self) -> bool:
        """步骤 2: 验证文件加载"""
        print("\n" + "▶" * 40)
        print("步骤 2: 验证文件加载")
        print("▶" * 40)

        max_wait = 30
        check_interval = 2

        for i in range(int(max_wait / check_interval)):
            try:
                if not self._is_autocad_running():
                    print("❌ AutoCAD 进程已关闭")
                    return False

                doc_name = self.current_doc.Name
                print(f"  ✅ 文档: {doc_name}")

                entity_count = self.current_doc.ModelSpace.Count
                print(f"  ✅ 模型空间实体数: {entity_count}")

                print("\n✅ 文件验证成功！")
                return True

            except Exception as e:
                print(f"  ⏳ 等待加载... ({(i + 1) * check_interval}/{max_wait} 秒)")
                time.sleep(check_interval)

        print(f"\n❌ 验证超时")
        return False

    def step3_execute_bplot(self) -> bool:
        """步骤 3: 执行 bplot 命令"""
        print("\n" + "▶" * 40)
        print("步骤 3: 执行 bplot 命令")
        print("▶" * 40)

        try:
            print("  📝 准备发送 BPLOT 命令...")

            # 方法1: 尝试使用 PostCommand（非阻塞）
            command_sent = False
            try:
                print("     尝试方法1: PostCommand (非阻塞)")
                self.acad.PostCommand("._BPLOT ")
                print("  ✅ PostCommand 发送成功")
                command_sent = True
            except AttributeError:
                print("     PostCommand 不可用")
            except Exception as e:
                print(f"     PostCommand 失败: {e}")

            # 方法2: 键盘模拟输入（跳过SendCommand，因为它会阻塞）
            if not command_sent:
                print("     尝试方法2: 键盘模拟输入（SendCommand会阻塞，跳过）")
                try:
                    # 激活窗口
                    print("     激活AutoCAD窗口...")
                    self._activate_autocad_window()
                    time.sleep(1)

                    # 模拟键盘输入 bplot
                    print("     键盘输入: bplot")
                    pyautogui.typewrite("bplot", interval=0.1)
                    time.sleep(1.0)  # 增加等待时间，确保AutoCAD接收完输入

                    print("     按下回车键")
                    pyautogui.press("enter")
                    time.sleep(0.5)

                    print("  ✅ 键盘输入完成")
                    command_sent = True
                except Exception as e:
                    print(f"  ❌ 键盘输入失败: {e}")
                    import traceback
                    traceback.print_exc()

            if not command_sent:
                print("  ❌ 所有方法都失败，无法发送BPLOT命令")
                return False

            print("\n  ⏳ 等待批量打印对话框打开...")
            time.sleep(5)  # 等待对话框完全打开

            # 激活AutoCAD窗口（确保对话框在前台）
            print("  🔄 激活 AutoCAD 窗口...")
            self._activate_autocad_window()

            print("\n  ✅ bplot 命令执行完成")
            return True

        except Exception as e:
            print(f"  ❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step4_click_select_button(self) -> bool:
        """步骤 4: OCR识别并点击"选择批量打印图纸"按钮"""
        print("\n" + "▶" * 40)
        print("步骤 4: OCR识别并点击按钮")
        print("▶" * 40)

        # 截图
        print("  📸 截取AutoCAD窗口...")
        screenshot_path = self.screenshot_dir / f"bplot_dialog_{int(time.time())}.png"
        image = self._capture_autocad_window()
        if image is None:
            print("  ❌ 截图失败")
            return False

        image.save(screenshot_path)
        print(f"  💾 截图已保存: {screenshot_path}")

        # OCR识别
        print("  🔍 OCR识别按钮位置...")
        button_texts = [
            "设置批量打印图纸表",  # AutoCAD 2014 中文版
            "选择批量打印图纸",
            "选择图纸",
            "图纸表",
            "Select Drawings",
            "Add Sheets"
        ]

        for button_text in button_texts:
            position = self._find_text_position(image, button_text)
            if position:
                x, y = position
                print(f"  ✅ 找到按钮: '{button_text}' at ({x}, {y})")

                # 点击按钮
                print(f"  🖱️  点击按钮...")
                pyautogui.moveTo(x, y, duration=0.3)
                time.sleep(0.2)
                pyautogui.click()
                time.sleep(1)

                print(f"  ✅ 按钮已点击")
                return True

        print(f"  ❌ 未找到目标按钮")
        return False

    def step5_input_all(self) -> bool:
        """步骤 5: 输入 all 并回车"""
        print("\n" + "▶" * 40)
        print("步骤 5: 输入 all 并回车")
        print("▶" * 40)

        try:
            print("  ⌨️  输入: all")
            pyautogui.typewrite("all", interval=0.1)
            time.sleep(0.5)

            print("  ⏎  按下回车键")
            pyautogui.press("enter")
            time.sleep(2)

            print("  ✅ 输入完成")
            return True

        except Exception as e:
            print(f"  ❌ 输入失败: {e}")
            return False

    def step6_extract_sheet_info(self) -> Optional[Dict[str, str]]:
        """步骤 6: 截图并提取图纸信息"""
        print("\n" + "▶" * 40)
        print("步骤 6: 提取图纸信息")
        print("▶" * 40)

        # 截图
        print("  📸 截取AutoCAD窗口...")
        screenshot_path = self.screenshot_dir / f"bplot_info_{int(time.time())}.png"
        image = self._capture_autocad_window()
        if image is None:
            print("  ❌ 截图失败")
            return None

        image.save(screenshot_path)
        print(f"  💾 截图已保存: {screenshot_path}")

        # OCR识别全部文本
        print("  🔍 OCR识别文本...")
        ocr_results = self._ocr_image(image)
        if not ocr_results:
            print("  ❌ OCR识别失败")
            return None

        # 提取文本
        all_text = "\n".join([item.get('text', '') for item in ocr_results.get('data', [])])
        print(f"\n  📄 识别到的文本:\n{all_text}\n")

        # 解析信息
        sheet_info = {}

        # 查找"选中图纸:"后面的数字
        match_selected = re.search(r'选中图纸[:\s]*(\d+)', all_text)
        if match_selected:
            sheet_info['selected_sheets'] = match_selected.group(1)
            print(f"  ✅ 选中图纸: {sheet_info['selected_sheets']}")

        # 查找总页数 (可能的格式: "共 N 页", "Total: N", "N sheets")
        patterns = [
            r'共\s*(\d+)\s*页',
            r'Total[:\s]*(\d+)',
            r'(\d+)\s*sheets',
            r'页数[:\s]*(\d+)'
        ]
        for pattern in patterns:
            match_total = re.search(pattern, all_text, re.IGNORECASE)
            if match_total:
                sheet_info['total_pages'] = match_total.group(1)
                print(f"  ✅ 总页数: {sheet_info['total_pages']}")
                break

        if not sheet_info:
            print("  ⚠️  未能提取到图纸信息")
            return None

        return sheet_info

    def _find_target_window(self) -> Optional[int]:
        """
        查找目标窗口（优先BPLOT对话框，其次AutoCAD主窗口）

        Returns:
            窗口句柄(hwnd)，如果未找到则返回None
        """
        try:
            import win32gui

            # 收集所有可见窗口
            windows = []

            def enum_windows_callback(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows.append((hwnd, title))
                return True

            win32gui.EnumWindows(enum_windows_callback, None)

            # 打印所有AutoCAD相关窗口（用于调试）
            autocad_windows = [(hwnd, title) for hwnd, title in windows
                              if 'autocad' in title.lower() or 'acad' in title.lower()
                              or '批量' in title or 'plot' in title.lower() or '发布' in title]
            if autocad_windows:
                print(f"  🔍 发现 {len(autocad_windows)} 个AutoCAD相关窗口:")
                for hwnd, title in autocad_windows:
                    print(f"     - {title}")

            # 优先级1：查找BPLOT对话框
            bplot_keywords = [
                '批量打印',
                'Batch Plot',
                'Publish',
                '发布',
                'Plot',
            ]

            # 先找BPLOT对话框
            for hwnd, title in windows:
                for keyword in bplot_keywords:
                    if keyword.lower() in title.lower():
                        print(f"  ✅ 匹配BPLOT对话框: '{title}'")
                        return hwnd

            # 如果没找到对话框，查找AutoCAD主窗口
            for hwnd, title in windows:
                if 'AutoCAD' in title or 'acad' in title.lower():
                    print(f"  ⚠️  未找到BPLOT对话框，使用AutoCAD主窗口: '{title}'")
                    return hwnd

            return None

        except Exception as e:
            print(f"  ⚠️  查找窗口失败: {e}")
            return None

    def _capture_autocad_window(self) -> Optional[Image.Image]:
        """截取AutoCAD窗口（优先查找BPLOT对话框）"""
        try:
            import win32gui

            target_hwnd = self._find_target_window()

            if not target_hwnd:
                print("  ❌ 未找到AutoCAD相关窗口")
                return None

            # 获取窗口标题（用于日志）
            title = win32gui.GetWindowText(target_hwnd)
            print(f"  ✅ 截图目标窗口: '{title}'")

            # 获取窗口位置
            rect = win32gui.GetWindowRect(target_hwnd)
            left, top, right, bottom = rect
            print(f"  📐 窗口坐标: left={left}, top={top}, right={right}, bottom={bottom}")
            print(f"  📐 窗口尺寸: {right-left}x{bottom-top}")

            # 截图
            image = ImageGrab.grab(bbox=(left, top, right, bottom))
            return image

        except Exception as e:
            print(f"  ❌ 截图失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _ocr_image(self, image: Image.Image) -> Optional[Dict]:
        """使用Umi-OCR识别图像"""
        try:
            # 压缩图片以加快OCR速度
            from io import BytesIO

            # 获取原始尺寸
            width, height = image.size
            print(f"     原始图片尺寸: {width}x{height}")

            # 如果图片太大，进行压缩
            max_size = 1920  # 最大边长
            if width > max_size or height > max_size:
                # 计算缩放比例
                scale = min(max_size / width, max_size / height)
                new_width = int(width * scale)
                new_height = int(height * scale)

                print(f"     压缩图片到: {new_width}x{new_height}")
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 转换为字节
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='PNG', optimize=True)
            img_byte_arr.seek(0)

            file_size = len(img_byte_arr.getvalue()) / 1024  # KB
            print(f"     图片大小: {file_size:.1f} KB")

            # 发送OCR请求（增加超时时间）
            print(f"     发送 OCR 请求...")
            files = {'image': ('screenshot.png', img_byte_arr, 'image/png')}
            response = requests.post(self.umi_ocr_url, files=files, timeout=60)  # 增加到60秒

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 100:
                    print(f"     ✅ OCR 成功，识别到 {len(result.get('data', []))} 个文本块")
                    return result
                else:
                    print(f"  ❌ OCR失败: {result.get('data', 'Unknown error')}")
                    return None
            else:
                print(f"  ❌ OCR请求失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"  ❌ OCR异常: {e}")
            return None

    def _find_text_position(self, image: Image.Image, target_text: str) -> Optional[Tuple[int, int]]:
        """在图像中查找文本位置并返回屏幕坐标"""
        ocr_results = self._ocr_image(image)
        if not ocr_results:
            return None

        # 查找匹配的文本
        for item in ocr_results.get('data', []):
            text = item.get('text', '')
            if target_text in text or text in target_text:
                # 获取边界框
                box = item.get('box', [])
                if box and len(box) >= 4:
                    # 计算中心点（相对于窗口的坐标）
                    x = (box[0][0] + box[2][0]) // 2
                    y = (box[0][1] + box[2][1]) // 2

                    # 转换为屏幕坐标
                    import win32gui
                    hwnd = self._find_target_window()
                    if hwnd:
                        rect = win32gui.GetWindowRect(hwnd)
                        screen_x = rect[0] + x
                        screen_y = rect[1] + y
                        print(f"     文本位置: 窗口坐标({x}, {y}) → 屏幕坐标({screen_x}, {screen_y})")
                        return (screen_x, screen_y)

        return None

    def _activate_autocad_window(self):
        """激活AutoCAD窗口（或BPLOT对话框）"""
        try:
            import win32gui
            hwnd = self._find_target_window()
            if hwnd:
                title = win32gui.GetWindowText(hwnd)
                win32gui.SetForegroundWindow(hwnd)
                print(f"  ✅ 已激活窗口: '{title}'")
            else:
                print(f"  ⚠️  未找到可激活的窗口")
        except Exception as e:
            print(f"  ⚠️  激活窗口失败: {e}")

    def _is_autocad_running(self) -> bool:
        """检查 AutoCAD 是否运行"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def _close_all_autocad_processes(self) -> int:
        """关闭所有 AutoCAD 进程"""
        closed_count = 0
        try:
            # COM关闭
            try:
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                acad.Quit()
                closed_count += 1
                time.sleep(2)
            except:
                pass

            # 强制终止
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                        closed_count += 1
                except:
                    pass

            time.sleep(2)

        except Exception as e:
            print(f"  ⚠️ 关闭过程出错: {e}")

        return closed_count

    def cleanup(self):
        """清理资源"""
        self.acad = None
        self.current_doc = None


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("AutoCAD Batch Plot (bplot) 全自动化工作流测试")
    print("=" * 80)

    # 测试文件路径（修改为你的实际文件）
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    # 创建工作流
    workflow = BplotAutoWorkflow()

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
