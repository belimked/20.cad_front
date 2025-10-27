"""
测试局域网Umi-OCR服务

测试地址: http://10.3.19.121:1224/
验证接口是否返回坐标信息

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import json
import base64
import time
import win32gui
import win32ui
import win32con
from ctypes import windll
from PIL import Image
import io


# Umi-OCR服务地址
UMI_OCR_URL = "http://10.3.19.121:1224/api/ocr"


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


def call_umi_ocr(image):
    """
    调用Umi-OCR API识别图像

    Args:
        image: PIL Image对象

    Returns:
        识别结果字典
    """
    # 转换图片为base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 准备请求数据
    data = {
        "base64": img_base64,
    }

    # 发送POST请求
    try:
        response = requests.post(UMI_OCR_URL, json=data, timeout=30)
        result = response.json()
        return result
    except Exception as e:
        print(f"❌ 调用Umi-OCR失败: {e}")
        return None


def test_umi_ocr_api(search_text):
    """测试Umi-OCR API"""
    print("=" * 80)
    print("Umi-OCR API 测试工具")
    print("=" * 80)
    print(f"服务地址: {UMI_OCR_URL}")

    # 测试连接
    print("\n🔍 测试API连接...")
    try:
        response = requests.get("http://10.3.19.121:1224/")
        print(f"✅ 连接成功: {response.text.strip()}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

    # 查找AutoCAD窗口
    print("\n🔍 查找AutoCAD窗口...")
    windows = find_autocad_window()
    if not windows:
        print("❌ 未找到AutoCAD窗口")
        print("请先启动AutoCAD")
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

    # 调用Umi-OCR
    print(f"\n🔍 调用Umi-OCR识别...")
    ocr_result = call_umi_ocr(image)

    if not ocr_result:
        return False

    # 显示完整响应
    print("\n📋 完整API响应:")
    print("=" * 80)
    print(json.dumps(ocr_result, ensure_ascii=False, indent=2))
    print("=" * 80)

    # 检查响应格式
    if ocr_result.get('code') != 100:
        print(f"\n❌ 识别失败，状态码: {ocr_result.get('code')}")
        return False

    data = ocr_result.get('data', [])
    if not data:
        print("\n❌ 未识别到任何文字")
        return False

    print(f"\n✅ 识别到 {len(data)} 个文本区域")
    print(f"⏱️ 识别耗时: {ocr_result.get('time', 0):.2f} 秒")

    # 显示所有识别到的文字
    print(f"\n【调试】所有识别到的文字 (前30个):")
    print("=" * 80)
    for i, item in enumerate(data[:30], 1):
        text = item.get('text', '')
        score = item.get('score', 0)
        box = item.get('box', [])

        print(f"  {i}. '{text}' (置信度:{score:.2f})")

        if box and len(box) >= 4:
            # 显示坐标格式
            print(f"     box: 左上{box[0]} 右上{box[1]} 右下{box[2]} 左下{box[3]}")

    print("=" * 80)

    # 查找指定文本
    print(f"\n🔍 查找文本: '{search_text}'")

    found = False
    for item in data:
        text = item.get('text', '')
        score = item.get('score', 0)
        box = item.get('box', [])

        if search_text in text:
            print(f"\n✅ 找到匹配文本: '{text}' (置信度:{score:.2f})")

            if box and len(box) >= 4:
                # 计算中心点
                center_x = (box[0][0] + box[2][0]) // 2
                center_y = (box[0][1] + box[2][1]) // 2

                # 转换为屏幕坐标
                screen_x = window_offset[0] + center_x
                screen_y = window_offset[1] + center_y

                print(f"   Box坐标: {box}")
                print(f"   窗口内位置: ({center_x}, {center_y})")
                print(f"   屏幕位置: ({screen_x}, {screen_y})")

                found = True
                break
            else:
                print(f"⚠️ 未找到box坐标信息")

    if not found:
        print(f"❌ 未找到文本: '{search_text}'")
        return False

    return True


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("Umi-OCR API 接口验证")
    print("=" * 80)

    # 输入要查找的文本
    text = input("\n请输入要查找的菜单文本 (如'依云'，直接回车默认'依云'): ").strip()
    if not text:
        text = "依云"

    print(f"\n" + "=" * 80)
    print("开始测试...")
    print("=" * 80)

    # 执行测试
    success = test_umi_ocr_api(text)

    print("\n" + "=" * 80)
    if success:
        print("✅ 测试成功！")
        print("\n验证结果:")
        print("  ✅ Umi-OCR服务可用")
        print("  ✅ 返回box坐标信息")
        print("  ✅ 中文识别正常")
        print("  ✅ 可以集成到工作流程")
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
