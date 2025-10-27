"""
图像预处理工具 - 增强版

用于提高OCR识别准确率的图像预处理函数
支持多种预处理方法：灰度化、二值化、降噪、RGB通道分离、边缘检测等

Author: CAD Auto Processor Team
Date: 2025-10-27
Updated: 2025-10-27 - 新增多种预处理方法
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re


# ============================================================================
# 预处理方法注册表
# ============================================================================

# 所有支持的预处理方法
PREPROCESSING_METHODS = [
    'original',           # 原始图像
    'grayscale',         # 灰度化
    'binary_adaptive',   # 自适应二值化（原binary）
    'binary_otsu',       # Otsu自动阈值二值化
    'binary_global',     # 全局阈值二值化
    'high_contrast',     # 高对比度（CLAHE）
    'high_brightness',   # 高亮度
    'denoise_gaussian',  # 高斯降噪
    'denoise_median',    # 中值滤波降噪
    'denoise_bilateral', # 双边滤波降噪
    'denoise_nlm',       # 非局部均值降噪
    'rgb_red',           # 红色通道
    'rgb_green',         # 绿色通道
    'rgb_blue',          # 蓝色通道
    'edge_canny',        # Canny边缘检测
    'edge_sobel',        # Sobel边缘检测
    'edge_laplacian',    # Laplacian边缘检测
]


# ============================================================================
# 核心预处理函数
# ============================================================================

def preprocess_images(
    image: Image.Image,
    save_dir: Optional[str] = None,
    base_name: str = "screenshot",
    methods: Optional[List[str]] = None,
    params: Optional[Dict] = None
) -> Dict[str, Image.Image]:
    """
    对原始图像进行多种预处理，生成不同版本用于OCR识别

    Args:
        image: PIL Image对象
        save_dir: 保存图片的目录（可选）
        base_name: 文件基础名称
        methods: 要使用的预处理方法列表（None=使用推荐方法）
        params: 预处理参数字典（可选）

    Returns:
        字典，包含不同预处理版本的图像
        {
            'original': 原始图像,
            'grayscale': 灰度图像,
            'binary_adaptive': 自适应二值化,
            'binary_otsu': Otsu二值化,
            ...
        }
    """
    # 默认参数
    default_params = {
        # 二值化参数
        'binary_adaptive_block_size': 11,
        'binary_adaptive_c': 2,
        'binary_global_threshold': 127,
        # CLAHE参数
        'clahe_clip_limit': 3.0,
        'clahe_tile_size': (8, 8),
        # 亮度调整参数
        'brightness_alpha': 1.3,
        'brightness_beta': 50,
        # 降噪参数
        'gaussian_kernel': (5, 5),
        'median_kernel': 5,
        'bilateral_d': 9,
        'bilateral_sigma_color': 75,
        'bilateral_sigma_space': 75,
        'nlm_h': 10,
        'nlm_template_window': 7,
        'nlm_search_window': 21,
        # 边缘检测参数
        'canny_threshold1': 50,
        'canny_threshold2': 150,
        'sobel_ksize': 3,
        'laplacian_ksize': 3,
    }

    # 合并用户参数
    if params:
        default_params.update(params)
    params = default_params

    # 默认使用推荐方法（对OCR最有效的）
    if methods is None:
        methods = [
            'original',
            'grayscale',
            'binary_adaptive',
            'binary_otsu',
            'high_contrast',
            'high_brightness',
            'denoise_bilateral',
            'edge_canny',
        ]

    # 转换为numpy数组并统一格式
    img_array = _prepare_image(image)

    # 获取RGB和灰度图（供后续处理使用）
    rgb = img_array
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # 结果字典
    results = {}

    # 遍历所有方法
    for method in methods:
        try:
            if method == 'original':
                results['original'] = image.copy()

            elif method == 'grayscale':
                results['grayscale'] = Image.fromarray(gray)

            elif method == 'binary_adaptive':
                binary = cv2.adaptiveThreshold(
                    gray, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    params['binary_adaptive_block_size'],
                    params['binary_adaptive_c']
                )
                results['binary_adaptive'] = Image.fromarray(binary)

            elif method == 'binary_otsu':
                _, binary = cv2.threshold(
                    gray, 0, 255,
                    cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                results['binary_otsu'] = Image.fromarray(binary)

            elif method == 'binary_global':
                _, binary = cv2.threshold(
                    gray,
                    params['binary_global_threshold'],
                    255,
                    cv2.THRESH_BINARY
                )
                results['binary_global'] = Image.fromarray(binary)

            elif method == 'high_contrast':
                # 直方图均衡化
                contrast = cv2.equalizeHist(gray)
                # CLAHE增强
                clahe = cv2.createCLAHE(
                    clipLimit=params['clahe_clip_limit'],
                    tileGridSize=params['clahe_tile_size']
                )
                contrast = clahe.apply(contrast)
                results['high_contrast'] = Image.fromarray(contrast)

            elif method == 'high_brightness':
                brightness = cv2.convertScaleAbs(
                    gray,
                    alpha=params['brightness_alpha'],
                    beta=params['brightness_beta']
                )
                results['high_brightness'] = Image.fromarray(brightness)

            elif method == 'denoise_gaussian':
                denoised = cv2.GaussianBlur(
                    gray,
                    params['gaussian_kernel'],
                    0
                )
                results['denoise_gaussian'] = Image.fromarray(denoised)

            elif method == 'denoise_median':
                denoised = cv2.medianBlur(
                    gray,
                    params['median_kernel']
                )
                results['denoise_median'] = Image.fromarray(denoised)

            elif method == 'denoise_bilateral':
                denoised = cv2.bilateralFilter(
                    gray,
                    params['bilateral_d'],
                    params['bilateral_sigma_color'],
                    params['bilateral_sigma_space']
                )
                results['denoise_bilateral'] = Image.fromarray(denoised)

            elif method == 'denoise_nlm':
                denoised = cv2.fastNlMeansDenoising(
                    gray,
                    None,
                    params['nlm_h'],
                    params['nlm_template_window'],
                    params['nlm_search_window']
                )
                results['denoise_nlm'] = Image.fromarray(denoised)

            elif method == 'rgb_red':
                red_channel = rgb[:, :, 0]
                results['rgb_red'] = Image.fromarray(red_channel)

            elif method == 'rgb_green':
                green_channel = rgb[:, :, 1]
                results['rgb_green'] = Image.fromarray(green_channel)

            elif method == 'rgb_blue':
                blue_channel = rgb[:, :, 2]
                results['rgb_blue'] = Image.fromarray(blue_channel)

            elif method == 'edge_canny':
                edges = cv2.Canny(
                    gray,
                    params['canny_threshold1'],
                    params['canny_threshold2']
                )
                results['edge_canny'] = Image.fromarray(edges)

            elif method == 'edge_sobel':
                sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=params['sobel_ksize'])
                sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=params['sobel_ksize'])
                sobel = np.sqrt(sobelx**2 + sobely**2)
                sobel = np.uint8(np.clip(sobel, 0, 255))
                results['edge_sobel'] = Image.fromarray(sobel)

            elif method == 'edge_laplacian':
                laplacian = cv2.Laplacian(gray, cv2.CV_64F, ksize=params['laplacian_ksize'])
                laplacian = np.uint8(np.clip(np.abs(laplacian), 0, 255))
                results['edge_laplacian'] = Image.fromarray(laplacian)

            else:
                print(f"  ⚠️ 未知的预处理方法: {method}")

        except Exception as e:
            print(f"  ❌ 预处理方法 {method} 失败: {e}")
            continue

    # 保存图像
    if save_dir:
        _save_images(results, save_dir, base_name)

    return results


def preprocess_for_ocr(
    image: Image.Image,
    method: str = 'original',
    params: Optional[Dict] = None
) -> Image.Image:
    """
    对图像进行单一预处理

    Args:
        image: PIL Image对象
        method: 预处理方法名称
        params: 预处理参数字典（可选）

    Returns:
        预处理后的PIL Image对象
    """
    if method not in PREPROCESSING_METHODS:
        raise ValueError(f"未知的预处理方法: {method}。支持的方法: {PREPROCESSING_METHODS}")

    # 复用批量处理函数（DRY原则）
    results = preprocess_images(image, methods=[method], params=params)

    return results.get(method, image.copy())


# ============================================================================
# OCR结果合并
# ============================================================================

def combine_ocr_results(results: List[List[Dict]]) -> List[Dict]:
    """
    合并多次OCR识别结果，去重并选择最高置信度

    Args:
        results: OCR结果列表，每个结果是一个包含text、score、box的字典列表

    Returns:
        合并后的结果列表，按置信度排序
    """
    # 使用字典存储，key为规范化后的文本，value为最佳结果
    merged = {}

    for result_list in results:
        for item in result_list:
            text = item.get('text', '').strip()
            if not text:
                continue

            # 文本规范化（用于去重）
            normalized = _normalize_text(text)
            score = item.get('score', 0)

            # 如果这个文本还没见过，或者当前置信度更高，则更新
            if normalized not in merged or score > merged[normalized].get('score', 0):
                merged[normalized] = item

    # 转换为列表并按置信度排序
    result = list(merged.values())
    result.sort(key=lambda x: x.get('score', 0), reverse=True)

    return result


# ============================================================================
# 辅助函数
# ============================================================================

def _prepare_image(image: Image.Image) -> np.ndarray:
    """
    准备图像：统一转换为RGB格式的numpy数组

    Args:
        image: PIL Image对象

    Returns:
        RGB格式的numpy数组
    """
    img_array = np.array(image)

    # 处理不同的图像格式
    if len(img_array.shape) == 2:
        # 灰度图 → RGB
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    elif len(img_array.shape) == 3:
        if img_array.shape[-1] == 4:
            # RGBA → RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        elif img_array.shape[-1] == 1:
            # 单通道 → RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[-1] == 3:
            # 已经是RGB，无需转换
            pass
        else:
            raise ValueError(f"不支持的图像通道数: {img_array.shape[-1]}")
    else:
        raise ValueError(f"不支持的图像维度: {img_array.shape}")

    return img_array


def _normalize_text(text: str) -> str:
    """
    文本规范化：用于OCR结果去重

    规范化规则：
    - 移除括号内容: "帮助(H)" → "帮助"
    - 移除空格
    - 转为小写（可选）

    Args:
        text: 原始文本

    Returns:
        规范化后的文本
    """
    # 移除括号及其内容
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\{[^}]*\}', '', text)

    # 移除空格
    text = text.replace(' ', '')

    # 移除常见标点符号
    text = text.replace(':', '').replace('：', '')

    return text.strip()


def _save_images(
    results: Dict[str, Image.Image],
    save_dir: str,
    base_name: str
) -> None:
    """
    保存预处理后的图像到磁盘

    Args:
        results: 预处理结果字典
        save_dir: 保存目录
        base_name: 文件基础名称
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    for version, img in results.items():
        filename = f"{base_name}_{version}.png"
        filepath = save_path / filename
        img.save(str(filepath))
        print(f"  💾 已保存: {filepath}")


def get_preprocessing_methods() -> List[str]:
    """
    获取所有支持的预处理方法

    Returns:
        方法名称列表
    """
    return PREPROCESSING_METHODS.copy()


def get_recommended_methods() -> List[str]:
    """
    获取推荐的预处理方法（对OCR效果最好的）

    Returns:
        推荐方法列表
    """
    return [
        'original',
        'binary_adaptive',
        'binary_otsu',
        'high_contrast',
        'denoise_bilateral',
    ]


def get_method_description(method: str) -> str:
    """
    获取预处理方法的描述

    Args:
        method: 方法名称

    Returns:
        方法描述
    """
    descriptions = {
        'original': '原始图像，未经处理',
        'grayscale': '灰度化，转换为单通道灰度图',
        'binary_adaptive': '自适应二值化，适合光照不均',
        'binary_otsu': 'Otsu自动阈值二值化，适合双峰分布',
        'binary_global': '全局阈值二值化，简单快速',
        'high_contrast': '高对比度增强（CLAHE），适合低对比度图像',
        'high_brightness': '高亮度调整，适合暗色主题',
        'denoise_gaussian': '高斯降噪，保留边缘',
        'denoise_median': '中值滤波降噪，去除椒盐噪声',
        'denoise_bilateral': '双边滤波降噪，保边+平滑',
        'denoise_nlm': '非局部均值降噪，效果最好但速度慢',
        'rgb_red': '红色通道，提取红色信息',
        'rgb_green': '绿色通道，提取绿色信息',
        'rgb_blue': '蓝色通道，提取蓝色信息',
        'edge_canny': 'Canny边缘检测，细线条',
        'edge_sobel': 'Sobel边缘检测，粗轮廓',
        'edge_laplacian': 'Laplacian边缘检测，全方向',
    }
    return descriptions.get(method, '未知方法')


# ============================================================================
# 测试函数
# ============================================================================

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

    # 进行预处理并保存（使用所有方法）
    save_dir = "screenshots/test_all_methods"
    print(f"\n🔄 开始图像预处理（使用所有方法）...")

    results = preprocess_images(
        image,
        save_dir=save_dir,
        base_name="test",
        methods=PREPROCESSING_METHODS  # 使用所有方法
    )

    print(f"\n✅ 完成！生成 {len(results)} 种预处理图像:")
    for method in results.keys():
        desc = get_method_description(method)
        print(f"  - {method}: {desc}")


if __name__ == "__main__":
    test_preprocessing()
