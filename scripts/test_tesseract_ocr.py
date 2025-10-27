"""
使用Tesseract OCR测试AutoCAD菜单识别

Tesseract对中文UI小字体识别效果最好！

Usage:
    python scripts/test_tesseract_ocr.py

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import win32gui
import win32ui
import win32con
from ctypes import windll
import numpy as np
from PIL import Image


def find_autocad_window():
    """查找AutoCAD窗口"""
    windows = []

    def enum_callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'AutoCAD' in title or 'acad' in title.lower():
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(enum_callback, None)
    return windows


def capture_window(hwnd):
    """截取指定窗口"""
    # 激活窗口
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    except:
        pass

    # 获取窗口位置和大小
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # 创建设备上下文
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 截图
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result == 0:
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # 转换为PIL Image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img, (left, top)


def test_tesseract(text):
    """测试Tesseract OCR识别"""
    try:
        import pytesseract
        import cv2
        import pyautogui
    except ImportError as e:
        print(f"❌ 缺少必要的库: {e}")
        print("\n请安装:")
        print("  pip install pytesseract opencv-python pyautogui")
        print("\n还需要安装Tesseract引擎:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  务必安装中文语言包 chi_sim.traineddata")
        return False

    # 查找AutoCAD窗口
    windows = find_autocad_window()
    if not windows:
        print("❌ 未找到AutoCAD窗口")
        print("请先启动AutoCAD")
        return False

    hwnd, title = windows[0]
    print(f"✅ 找到窗口: {title}")

    # 截取窗口
    print("📸 截取窗口...")
    result = capture_window(hwnd)
    if not result:
        print("❌ 截图失败")
        return False

    image, window_offset = result
    print(f"✅ 截图成功: {image.width}x{image.height}")

    # 转换为numpy数组
    img_array = np.array(image)

    # 转换为灰度图
    print("🔄 转换为灰度图...")
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Tesseract识别
    print(f"🔍 使用Tesseract OCR识别文字...")
    print(f"   语言: 中文+英文 (chi_sim+eng)")

    try:
        data = pytesseract.image_to_data(gray, lang='chi_sim+eng',
                                          output_type=pytesseract.Output.DICT)

        # 统计识别结果
        n_boxes = len(data['text'])
        valid_count = sum(1 for t in data['text'] if t.strip())

        print(f"✅ 识别到 {valid_count} 个文本区域")

        # 显示所有识别到的文字
        print(f"\n【调试】所有识别到的文字 (前30个):")
        print("=" * 80)
        debug_count = 0
        for i in range(n_boxes):
            if data['text'][i].strip() and data['conf'][i] > 0:
                debug_count += 1
                if debug_count <= 30:
                    conf = int(data['conf'][i])
                    print(f"  {debug_count}. '{data['text'][i]}' (置信度:{conf}%)")

        print("=" * 80)

        # 查找指定文本
        print(f"\n🔍 查找文本: '{text}'")

        found = False
        for i in range(n_boxes):
            recognized_text = data['text'][i]
            confidence = int(data['conf'][i])

            if not recognized_text.strip() or confidence < 0:
                continue

            # 完全匹配
            if text in recognized_text:
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]

                center_x = x + w // 2
                center_y = y + h // 2

                screen_x = window_offset[0] + center_x
                screen_y = window_offset[1] + center_y

                print(f"\n✅ 找到匹配文本: '{recognized_text}' (置信度:{confidence}%)")
                print(f"   窗口内位置: ({center_x}, {center_y})")
                print(f"   屏幕位置: ({screen_x}, {screen_y})")

                # 询问是否点击
                do_click = input("\n是否点击该位置? (y/n，默认n): ").strip().lower()
                if do_click == 'y':
                    pyautogui.moveTo(screen_x, screen_y, duration=0.3)
                    time.sleep(0.2)
                    pyautogui.click()
                    print("✅ 已点击")

                found = True
                break

        if not found:
            print(f"❌ 未找到文本: '{text}'")
            print("\n可能的原因:")
            print("  1. 菜单不可见或被遮挡")
            print("  2. 文字太小或模糊")
            print("  3. 输入的文字不准确")
            return False

        return True

    except pytesseract.TesseractNotFoundError:
        print("❌ 未找到Tesseract引擎")
        print("\n请下载并安装Tesseract:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  推荐版本: tesseract-ocr-w64-setup-5.3.x.exe")
        print("\n安装后确保:")
        print("  1. 选中中文语言包 (chi_sim)")
        print("  2. 将安装路径添加到系统PATH，或设置环境变量:")
        print("     pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        return False

    except Exception as e:
        print(f"❌ 识别失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("Tesseract OCR 测试工具 - 中文UI小字体识别专家")
    print("=" * 80)

    # 检查依赖
    print("\n检查依赖...")
    try:
        import pytesseract
        print("✅ pytesseract 已安装")
    except ImportError:
        print("❌ pytesseract 未安装")
        print("   pip install pytesseract")

    try:
        import cv2
        print("✅ opencv-python 已安装")
    except ImportError:
        print("❌ opencv-python 未安装")
        print("   pip install opencv-python")

    try:
        import pyautogui
        print("✅ pyautogui 已安装")
    except ImportError:
        print("❌ pyautogui 未安装")
        print("   pip install pyautogui")

    # 输入要查找的文本
    text = input("\n请输入要查找的菜单文本 (如'依云'，直接回车默认'依云'): ").strip()
    if not text:
        text = "依云"

    print(f"\n" + "=" * 80)
    print("开始测试...")
    print("=" * 80)

    # 执行测试
    success = test_tesseract(text)

    print("\n" + "=" * 80)
    if success:
        print("✅ 测试成功！")
    else:
        print("❌ 测试失败")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 键退出...")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
