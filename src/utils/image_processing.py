"""
图像预处理工具

用于提高OCR识别准确率的图像预处理函数

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, List
from pathlib import Path


def preprocess_images(image: Image.Image, save_dir: str = None, base_name: str = "screenshot") -> Dict[str, Image.Image]:
    """
    对原始图像进行多种预处理，生成不同版本用于OCR识别

    Args:
        image: PIL Image对象
        save_dir: 保存图片的目录（可选）
        base_name: 文件基础名称

    Returns:
        字典，包含不同预处理版本的图像
        {
            'original': 原始图像,
            'binary': 纯黑白图像,
            'high_contrast': 高对比度图像,
            'high_brightness': 高亮度图像
        }
    """
    # 转换为numpy数组
    img_array = np.array(image)

    # 如果是RGBA，转换为RGB
    if img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

    # 转换为灰度图（用于后续处理）
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # 结果字典
    results = {}

    # 1. 原始图像
    results['original'] = image.copy()

    # 2. 纯黑白图像（二值化）
    # 使用自适应阈值，对不同光照条件更鲁棒
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    results['binary'] = Image.fromarray(binary)

    # 3. 高对比度图像
    # 方法：直方图均衡化
    high_contrast = cv2.equalizeHist(gray)
    # 再增强一次对比度
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    high_contrast = clahe.apply(high_contrast)
    results['high_contrast'] = Image.fromarray(high_contrast)

    # 4. 高亮度图像
    # 方法：增加亮度和对比度
    high_brightness = cv2.convertScaleAbs(gray, alpha=1.3, beta=50)  # alpha控制对比度，beta控制亮度
    results['high_brightness'] = Image.fromarray(high_brightness)

    # 如果指定了保存目录，保存所有图像
    if save_dir:
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        for version, img in results.items():
            filename = f"{base_name}_{version}.png"
            filepath = save_path / filename
            img.save(str(filepath))
            print(f"  💾 已保存: {filepath}")

    return results


def preprocess_for_ocr(image: Image.Image, method: str = 'original') -> Image.Image:
    """
    对图像进行单一预处理

    Args:
        image: PIL Image对象
        method: 预处理方法 ('original', 'binary', 'high_contrast', 'high_brightness')

    Returns:
        预处理后的PIL Image对象
    """
    if method == 'original':
        return image.copy()

    # 转换为numpy数组
    img_array = np.array(image)

    # 如果是RGBA，转换为RGB
    if img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

    # 转换为灰度图
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    if method == 'binary':
        # 纯黑白
        result = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    elif method == 'high_contrast':
        # 高对比度
        result = cv2.equalizeHist(gray)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        result = clahe.apply(result)
    elif method == 'high_brightness':
        # 高亮度
        result = cv2.convertScaleAbs(gray, alpha=1.3, beta=50)
    else:
        raise ValueError(f"Unknown method: {method}")

    return Image.fromarray(result)


def combine_ocr_results(results: List[Dict]) -> List[Dict]:
    """
    合并多次OCR识别结果，去重并选择最高置信度

    Args:
        results: OCR结果列表，每个结果是一个包含text、score、box的字典列表

    Returns:
        合并后的结果列表，按置信度排序
    """
    # 使用字典存储，key为文本内容，value为最佳结果
    merged = {}

    for result_list in results:
        for item in result_list:
            text = item.get('text', '').strip()
            if not text:
                continue

            score = item.get('score', 0)

            # 如果这个文本还没见过，或者当前置信度更高，则更新
            if text not in merged or score > merged[text].get('score', 0):
                merged[text] = item

    # 转换为列表并按置信度排序
    result = list(merged.values())
    result.sort(key=lambda x: x.get('score', 0), reverse=True)

    return result


def get_preprocessing_methods() -> List[str]:
    """
    获取所有支持的预处理方法

    Returns:
        方法名称列表
    """
    return ['original', 'binary', 'high_contrast', 'high_brightness']


def test_preprocessing():
    """测试图像预处理功能"""
    import win32gui
    import win32ui
    import win32con
    from ctypes import windll

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
        print("❌ 未找到AutoCAD窗口")
        return

    hwnd, title = windows[0]
    print(f"✅ 找到窗口: {title}")

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

    print(f"✅ 截图成功: {width}x{height}")

    # 进行预处理并保存
    save_dir = "screenshots/test"
    print(f"\n🔄 开始图像预处理...")
    results = preprocess_images(image, save_dir=save_dir, base_name="test")

    print(f"\n✅ 完成！生成 {len(results)} 种预处理图像:")
    for version in results.keys():
        print(f"  - {version}")


if __name__ == "__main__":
    test_preprocessing()
