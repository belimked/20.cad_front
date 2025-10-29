"""
使用百度OCR API识别菜单文本并点击

在线OCR方案，识别率高，支持中文
需要百度AI开放平台账号和API Key

申请地址：https://ai.baidu.com/tech/ocr/general

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
import base64
import requests


def capture_window(hwnd):
    """截取指定窗口的截图"""
    try:
        from PIL import Image
    except ImportError:
        print("❌ 缺少PIL库")
        return None

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


def baidu_ocr(image, api_key, secret_key):
    """
    使用百度OCR识别图像中的文字

    Args:
        image: PIL Image对象
        api_key: 百度API Key
        secret_key: 百度Secret Key

    Returns:
        识别结果列表
    """
    import io

    # 获取access_token
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"

    try:
        response = requests.get(token_url, timeout=10)
        access_token = response.json()['access_token']
    except Exception as e:
        print(f"❌ 获取access_token失败: {e}")
        return None

    # 将图片转为base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # 调用OCR API
    ocr_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'image': img_base64,
        'access_token': access_token
    }

    try:
        response = requests.post(ocr_url, headers=headers, data=data, timeout=30)
        result = response.json()

        if 'words_result' in result:
            return result['words_result']
        else:
            print(f"❌ OCR识别失败: {result.get('error_msg', '未知错误')}")
            return None

    except Exception as e:
        print(f"❌ 调用OCR API失败: {e}")
        return None


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


def click_text_by_baidu_ocr(text, api_key, secret_key):
    """
    使用百度OCR识别并点击指定文本

    Args:
        text: 要查找的文本
        api_key: 百度API Key
        secret_key: 百度Secret Key

    Returns:
        True表示成功，False表示失败
    """
    try:
        import pyautogui
    except ImportError:
        print("❌ 缺少pyautogui库")
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

    # 百度OCR识别
    print(f"🔍 使用百度OCR识别...")
    ocr_result = baidu_ocr(image, api_key, secret_key)

    if not ocr_result:
        return False

    print(f"✅ 识别到 {len(ocr_result)} 个文本区域")

    # 调试输出
    print(f"【调试】所有识别到的文字:")
    for i, item in enumerate(ocr_result[:20], 1):
        print(f"  {i}. '{item['words']}'")

    # 查找匹配的文本（百度OCR不返回位置，需要手动定位）
    for item in ocr_result:
        if text in item['words']:
            print(f"\n⚠️ 找到文本: '{item['words']}'")
            print("⚠️ 但百度通用OCR不返回坐标位置")
            print("建议：")
            print("  1. 使用百度高精度OCR（支持位置）")
            print("  2. 或使用本地OCR方案")
            return False

    print(f"❌ 未找到文本: '{text}'")
    return False


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD 菜单百度OCR识别工具")
    print("=" * 80)

    print("\n⚠️ 注意：百度通用OCR不返回文字位置坐标")
    print("建议使用百度高精度OCR或位置识别API")
    print("\n申请地址: https://ai.baidu.com/tech/ocr/general")

    # 输入API凭证
    api_key = input("\n请输入百度API Key: ").strip()
    if not api_key:
        print("❌ API Key不能为空")
        return

    secret_key = input("请输入百度Secret Key: ").strip()
    if not secret_key:
        print("❌ Secret Key不能为空")
        return

    # 输入要查找的文本
    text = input("\n请输入要查找的菜单文本 (如'依云'): ").strip()
    if not text:
        print("❌ 文本不能为空")
        return

    print(f"\n" + "=" * 80)
    print("开始识别...")
    print("=" * 80)

    # 执行识别
    success = click_text_by_baidu_ocr(text, api_key, secret_key)

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
