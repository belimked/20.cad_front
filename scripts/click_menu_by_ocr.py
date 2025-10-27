"""
使用OCR识别AutoCAD菜单文本并点击

自动识别屏幕上的文字，找到指定菜单并点击
支持中文识别

Usage:
    python scripts/click_menu_by_ocr.py

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time
import win32gui
import win32ui
import win32con
from ctypes import windll


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
    """截取指定窗口的截图"""
    try:
        from PIL import Image
    except ImportError:
        print("❌ 缺少PIL库")
        print("请安装: pip install pillow")
        return None

    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

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
        # 备用方法
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


def ocr_and_find_text(image, search_text, method='paddleocr'):
    """
    使用OCR识别图像中的文字并查找指定文本

    Args:
        image: PIL Image对象
        search_text: 要查找的文本
        method: OCR方法 ('paddleocr'或'easyocr')

    Returns:
        匹配文本的坐标列表 [(x, y, w, h), ...]
    """
    import numpy as np

    if method == 'paddleocr':
        try:
            from paddleocr import PaddleOCR
        except ImportError:
            print("❌ 缺少paddleocr库")
            print("请安装: pip install paddleocr")
            return []

        print(f"🔍 使用PaddleOCR识别文字...")

        # 初始化OCR（中文+英文）
        ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

        # 转换为numpy数组
        img_array = np.array(image)

        # 执行OCR
        result = ocr.ocr(img_array, cls=True)

        if not result or not result[0]:
            print("⚠️ 未识别到任何文字")
            return []

        print(f"✅ 识别到 {len(result[0])} 个文本区域")

        # 查找匹配的文本
        matches = []
        for line in result[0]:
            box = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text = line[1][0]  # 识别的文字
            confidence = line[1][1]  # 置信度

            # 检查是否包含搜索文本
            if search_text in text:
                # 计算边界框
                x_coords = [point[0] for point in box]
                y_coords = [point[1] for point in box]
                x = int(min(x_coords))
                y = int(min(y_coords))
                w = int(max(x_coords) - x)
                h = int(max(y_coords) - y)

                matches.append({
                    'text': text,
                    'box': (x, y, w, h),
                    'center': (x + w // 2, y + h // 2),
                    'confidence': confidence
                })

                print(f"  ✅ 找到匹配: '{text}' (置信度:{confidence:.2f}) at ({x}, {y})")

        return matches

    elif method == 'easyocr':
        try:
            import easyocr
        except ImportError:
            print("❌ 缺少easyocr库")
            print("请安装: pip install easyocr")
            return []

        print(f"🔍 使用EasyOCR识别文字...")

        # 初始化OCR（中文+英文）
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)

        # 转换为numpy数组
        img_array = np.array(image)

        # 执行OCR
        result = reader.readtext(img_array)

        if not result:
            print("⚠️ 未识别到任何文字")
            return []

        print(f"✅ 识别到 {len(result)} 个文本区域")

        # 查找匹配的文本
        matches = []
        for detection in result:
            box = detection[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text = detection[1]
            confidence = detection[2]

            # 检查是否包含搜索文本
            if search_text in text:
                # 计算边界框
                x_coords = [point[0] for point in box]
                y_coords = [point[1] for point in box]
                x = int(min(x_coords))
                y = int(min(y_coords))
                w = int(max(x_coords) - x)
                h = int(max(y_coords) - y)

                matches.append({
                    'text': text,
                    'box': (x, y, w, h),
                    'center': (x + w // 2, y + h // 2),
                    'confidence': confidence
                })

                print(f"  ✅ 找到匹配: '{text}' (置信度:{confidence:.2f}) at ({x}, {y})")

        return matches

    else:
        print(f"❌ 不支持的OCR方法: {method}")
        return []


def click_text_by_ocr(text, ocr_method='paddleocr'):
    """
    使用OCR识别并点击指定文本

    Args:
        text: 要查找的文本
        ocr_method: OCR方法

    Returns:
        True表示成功，False表示失败
    """
    try:
        import pyautogui
    except ImportError:
        print("❌ 缺少pyautogui库")
        print("请安装: pip install pyautogui")
        return False

    # 查找AutoCAD窗口
    windows = find_autocad_window()
    if not windows:
        print("❌ 未找到AutoCAD窗口")
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

    # OCR识别
    matches = ocr_and_find_text(image, text, method=ocr_method)

    if not matches:
        print(f"❌ 未找到文本: '{text}'")
        print("\n可能的原因:")
        print("  1. 文本不可见或被遮挡")
        print("  2. OCR识别错误")
        print("  3. 文本样式特殊（如艺术字）")
        return False

    # 选择第一个匹配（如果有多个）
    if len(matches) > 1:
        print(f"\n⚠️ 找到 {len(matches)} 个匹配，选择第一个")

    match = matches[0]

    # 计算屏幕坐标（窗口偏移 + 相对坐标）
    screen_x = window_offset[0] + match['center'][0]
    screen_y = window_offset[1] + match['center'][1]

    print(f"📍 点击位置: 窗口({match['center'][0]}, {match['center'][1]}) -> 屏幕({screen_x}, {screen_y})")

    # 移动鼠标并点击
    pyautogui.moveTo(screen_x, screen_y, duration=0.3)
    time.sleep(0.2)
    pyautogui.click()

    print(f"✅ 已点击: '{match['text']}'")
    return True


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD 菜单OCR识别点击工具")
    print("=" * 80)

    # 检查依赖
    print("\n检查OCR库...")
    has_paddleocr = False
    has_easyocr = False

    try:
        import paddleocr
        has_paddleocr = True
        print("✅ PaddleOCR 已安装")
    except ImportError:
        print("⚠️ PaddleOCR 未安装")

    try:
        import easyocr
        has_easyocr = True
        print("✅ EasyOCR 已安装")
    except ImportError:
        print("⚠️ EasyOCR 未安装")

    if not has_paddleocr and not has_easyocr:
        print("\n❌ 未安装任何OCR库")
        print("\n请选择安装以下之一:")
        print("  1. PaddleOCR (推荐，速度快，中文识别好)")
        print("     pip install paddleocr")
        print("\n  2. EasyOCR (通用性好，支持多种语言)")
        print("     pip install easyocr")
        return

    # 选择OCR方法
    if has_paddleocr and has_easyocr:
        print("\n可用的OCR方法:")
        print("  [1] PaddleOCR (推荐)")
        print("  [2] EasyOCR")
        choice = input("\n请选择 (1-2，默认1): ").strip()
        ocr_method = 'easyocr' if choice == '2' else 'paddleocr'
    elif has_paddleocr:
        ocr_method = 'paddleocr'
    else:
        ocr_method = 'easyocr'

    print(f"\n使用OCR方法: {ocr_method}")

    # 输入要查找的文本
    text = input("\n请输入要查找的菜单文本 (如'依云'): ").strip()
    if not text:
        print("❌ 文本不能为空")
        return

    print(f"\n" + "=" * 80)
    print("开始识别并点击...")
    print("=" * 80)

    # 执行OCR识别并点击
    success = click_text_by_ocr(text, ocr_method)

    if success:
        print("\n" + "=" * 80)
        print("✅ 成功！")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 失败")
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
