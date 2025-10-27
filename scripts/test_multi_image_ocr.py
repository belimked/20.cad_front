"""
测试图像预处理和多次OCR识别

验证图像预处理功能是否能提高OCR识别成功率

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
from PIL import Image
from datetime import datetime

from src.utils.image_processing import preprocess_images, combine_ocr_results


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
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
    except:
        pass

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
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return img, (left, top)


def call_umi_ocr(image, version_name):
    """调用Umi-OCR识别单个图像"""
    import requests
    import base64
    import io

    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    umi_ocr_url = "http://10.3.19.121:1224/api/ocr"
    response = requests.post(
        umi_ocr_url,
        json={
            "base64": img_base64,
            "options": {
                "ocr.limit_side_len": 2880,
                "data.format": "dict"
            }
        },
        timeout=30
    )

    result = response.json()

    if result.get('code') != 100:
        return None

    data = result.get('data', [])

    # 添加版本标记
    for item in data:
        item['_version'] = version_name

    return data


def test_multi_image_ocr(search_text):
    """测试多图像OCR识别"""
    print("=" * 80)
    print("多图像预处理OCR测试")
    print("=" * 80)

    # 查找AutoCAD窗口
    print("\n🔍 查找AutoCAD窗口...")
    windows = find_autocad_window()
    if not windows:
        print("❌ 未找到AutoCAD窗口")
        return False

    hwnd, title = windows[0]
    print(f"✅ 找到窗口: {title}")

    # 截取窗口
    print("\n📸 截取窗口...")
    result = capture_window(hwnd)
    if not result:
        print("❌ 截图失败")
        return False

    image, window_offset = result
    print(f"✅ 截图成功: {image.width}x{image.height}")

    # 生成预处理图像
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshots_dir = project_root / "screenshots" / f"test_{timestamp}"
    base_name = "test_window"

    print(f"\n💾 保存截图到: {screenshots_dir}")
    print(f"🔄 生成预处理图像...")

    preprocessed_images = preprocess_images(
        image,
        save_dir=str(screenshots_dir),
        base_name=base_name
    )

    print(f"✅ 已生成 {len(preprocessed_images)} 种预处理图像")

    # 对每种预处理图像进行OCR
    print(f"\n🔍 对每种预处理图像进行OCR识别...")
    print("=" * 80)

    all_ocr_results = []
    ocr_stats = {}

    for version, processed_img in preprocessed_images.items():
        print(f"\n📋 处理 [{version}] 版本...")

        start_time = time.time()
        ocr_data = call_umi_ocr(processed_img, version)
        elapsed = time.time() - start_time

        if not ocr_data:
            print(f"  ❌ OCR识别失败")
            ocr_stats[version] = {'count': 0, 'time': elapsed, 'found': False}
            continue

        print(f"  ✅ 识别到 {len(ocr_data)} 个文本区域，耗时: {elapsed:.2f}秒")

        # 检查是否包含目标文本
        found_target = any(search_text in item.get('text', '') for item in ocr_data)
        ocr_stats[version] = {'count': len(ocr_data), 'time': elapsed, 'found': found_target}

        if found_target:
            print(f"  🎯 找到目标文本 '{search_text}'")

        # 显示前5个结果
        print(f"  前5个识别结果:")
        for i, item in enumerate(ocr_data[:5], 1):
            text = item.get('text', '')
            score = item.get('score', 0)
            marker = "🎯" if search_text in text else "  "
            print(f"    {marker}{i}. '{text}' (置信度:{score:.2f})")

        all_ocr_results.append(ocr_data)

    # 统计分析
    print("\n" + "=" * 80)
    print("📊 OCR识别统计")
    print("=" * 80)
    for version, stats in ocr_stats.items():
        found_marker = "✅" if stats['found'] else "❌"
        print(f"{found_marker} [{version:20s}] 识别数: {stats['count']:4d}  "
              f"耗时: {stats['time']:.2f}s  "
              f"目标: {'找到' if stats['found'] else '未找到'}")

    # 合并结果
    if not all_ocr_results:
        print("\n❌ 所有预处理版本均未识别到文字")
        return False

    print(f"\n🔄 合并 {len(all_ocr_results)} 次OCR结果...")
    merged_results = combine_ocr_results(all_ocr_results)
    print(f"✅ 合并后共 {len(merged_results)} 个唯一文本")

    # 显示合并后的结果
    print(f"\n【合并结果】前20个（按置信度排序）:")
    print("=" * 80)
    for i, item in enumerate(merged_results[:20], 1):
        text = item.get('text', '')
        score = item.get('score', 0)
        version = item.get('_version', 'unknown')
        marker = "🎯" if search_text in text else "  "
        print(f"{marker}{i:2d}. [{version:20s}] '{text}' (置信度:{score:.2f})")

    # 查找目标文本
    print(f"\n🔍 查找目标文本: '{search_text}'")
    print("=" * 80)

    found = False
    for item in merged_results:
        text = item.get('text', '')
        if search_text in text:
            score = item.get('score', 0)
            version = item.get('_version', 'unknown')
            box = item.get('box', [])

            print(f"\n✅ 找到匹配文本: '{text}'")
            print(f"   置信度: {score:.2f}")
            print(f"   来源: [{version}] 版本")
            if box and len(box) >= 4:
                center_x = (box[0][0] + box[2][0]) // 2
                center_y = (box[0][1] + box[2][1]) // 2
                print(f"   位置: ({center_x}, {center_y})")

            found = True
            break

    if not found:
        print(f"❌ 未找到目标文本: '{search_text}'")

    print("\n" + "=" * 80)
    return found


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD 多图像预处理OCR测试工具")
    print("=" * 80)
    print("\n测试说明:")
    print("  1. 截取AutoCAD窗口")
    print("  2. 生成4种预处理图像（原始/纯黑白/高对比度/高亮度）")
    print("  3. 对每种图像进行OCR识别")
    print("  4. 合并所有结果，选择最佳匹配")
    print("  5. 所有图像保存在 screenshots/ 目录")

    # 输入要查找的文本
    text = input("\n请输入要查找的菜单文本 (如'依云'，直接回车默认'依云'): ").strip()
    if not text:
        text = "依云"

    print(f"\n" + "=" * 80)
    print("开始测试...")
    print("=" * 80)

    # 执行测试
    success = test_multi_image_ocr(text)

    print("\n" + "=" * 80)
    if success:
        print("✅ 测试成功！找到目标文本")
        print("\n优势:")
        print("  - 多种预处理方式提高识别成功率")
        print("  - 自动选择最高置信度的结果")
        print("  - 保存所有图像便于调试分析")
    else:
        print("❌ 测试失败：未找到目标文本")
        print("\n建议:")
        print("  - 检查 screenshots/ 目录中的预处理图像")
        print("  - 尝试调整图像预处理参数")
        print("  - 确认目标文本在窗口中可见")
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
