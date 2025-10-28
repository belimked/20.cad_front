#!/usr/bin/env python3
"""
测试图像预处理方法

快速测试新的预处理方法和参数变体

Author: CAD Auto Processor Team (老王优化版)
Date: 2025-10-28
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.image_processing import (
    preprocess_images,
    get_recommended_methods,
    get_method_description
)
from PIL import Image


def test_with_screenshot():
    """使用AutoCAD截图测试预处理方法"""
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll

    print("=" * 80)
    print("图像预处理方法测试")
    print("=" * 80)

    # 查找AutoCAD窗口
    windows = []
    def enum_callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'AutoCAD' in title or 'acad' in title.lower():
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(enum_callback, None)

    if not windows:
        print("\n❌ 未找到AutoCAD窗口")
        print("   请先打开AutoCAD")
        return

    hwnd, title = windows[0]
    print(f"\n✅ 找到窗口: {title}")

    # 截取窗口
    print("\n📸 截取窗口...")
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

    print(f"✅ 截图成功: {width}x{height}")

    # 获取推荐方法
    methods = get_recommended_methods()
    print(f"\n📋 当前推荐方法:")
    for method in methods:
        desc = get_method_description(method)
        print(f"  - {method}: {desc}")

    # 进行预处理
    save_dir = "screenshots/test_preprocessing"
    print(f"\n🔄 开始图像预处理...")
    print(f"💾 保存目录: {save_dir}")

    results = preprocess_images(
        image,
        save_dir=save_dir,
        base_name="test"
    )

    print(f"\n✅ 完成！生成 {len(results)} 种预处理图像:")
    for i, (method, img) in enumerate(results.items(), 1):
        desc = get_method_description(method)
        print(f"  {i}. {method}: {desc}")

    print(f"\n📂 图像已保存到: {save_dir}")
    print("=" * 80)


def test_with_file(image_path: str):
    """使用指定图像文件测试预处理方法"""
    print("=" * 80)
    print("图像预处理方法测试（从文件）")
    print("=" * 80)

    img_file = Path(image_path)
    if not img_file.exists():
        print(f"\n❌ 文件不存在: {image_path}")
        return

    print(f"\n📁 读取图像: {img_file.name}")
    image = Image.open(img_file)
    print(f"✅ 图像尺寸: {image.size[0]}x{image.size[1]}")

    # 获取推荐方法
    methods = get_recommended_methods()
    print(f"\n📋 当前推荐方法:")
    for method in methods:
        desc = get_method_description(method)
        print(f"  - {method}: {desc}")

    # 进行预处理
    save_dir = f"screenshots/test_{img_file.stem}"
    print(f"\n🔄 开始图像预处理...")
    print(f"💾 保存目录: {save_dir}")

    results = preprocess_images(
        image,
        save_dir=save_dir,
        base_name=img_file.stem
    )

    print(f"\n✅ 完成！生成 {len(results)} 种预处理图像:")
    for i, (method, img) in enumerate(results.items(), 1):
        desc = get_method_description(method)
        print(f"  {i}. {method}: {desc}")

    print(f"\n📂 图像已保存到: {save_dir}")
    print("=" * 80)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 使用命令行参数指定的文件
        image_path = sys.argv[1]
        test_with_file(image_path)
    else:
        # 使用AutoCAD截图
        test_with_screenshot()


if __name__ == "__main__":
    main()
