"""
自动截取AutoCAD窗口并提取菜单图标

自动激活AutoCAD窗口并截图，然后让用户选择菜单区域

Usage:
    python scripts/capture_menu_icon.py

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
    """
    截取指定窗口的截图

    Args:
        hwnd: 窗口句柄

    Returns:
        PIL Image对象
    """
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

    print(f"   窗口位置: ({left}, {top})")
    print(f"   窗口大小: {width} x {height}")

    # 创建设备上下文
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 截图（使用PrintWindow，即使窗口被遮挡也能截图）
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)

    if result == 0:
        print("⚠️ PrintWindow失败，尝试BitBlt方法")
        # 备用方法：BitBlt（需要窗口在前台且不被遮挡）
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

    return img


def interactive_crop(image, output_path):
    """
    交互式裁剪图片（使用matplotlib）

    Args:
        image: PIL Image对象
        output_path: 输出路径

    Returns:
        True表示成功，False表示失败
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.widgets import RectangleSelector
    except ImportError:
        print("❌ 缺少matplotlib库")
        print("请安装: pip install matplotlib")
        return False

    print("\n" + "=" * 80)
    print("交互式裁剪")
    print("=" * 80)
    print("操作说明:")
    print("  1. 在图片上按住鼠标左键拖动，框选菜单图标区域")
    print("  2. 松开鼠标后，关闭窗口即可保存")
    print("  3. 如果不满意，可以重新框选（最后一次为准）")
    print("=" * 80)

    crop_coords = [None]  # 使用列表保存坐标，以便在回调中修改

    def onselect(eclick, erelease):
        """选择区域回调"""
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)

        # 确保坐标顺序正确
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        crop_coords[0] = (x1, y1, x2, y2)
        print(f"\n✅ 已选择区域: ({x1}, {y1}) -> ({x2}, {y2})")
        print(f"   大小: {x2-x1} x {y2-y1}")

    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image)
    ax.set_title("框选菜单图标区域（拖动鼠标框选，然后关闭窗口）", fontsize=14, pad=20)
    ax.axis('off')

    # 创建矩形选择器
    selector = RectangleSelector(
        ax, onselect,
        useblit=True,
        button=[1],  # 左键
        minspanx=5, minspany=5,
        spancoords='pixels',
        interactive=True,
        props=dict(facecolor='red', edgecolor='red', alpha=0.3, fill=True)
    )

    plt.tight_layout()
    plt.show()

    # 裁剪并保存
    if crop_coords[0]:
        x1, y1, x2, y2 = crop_coords[0]
        cropped = image.crop((x1, y1, x2, y2))
        cropped.save(output_path)
        print(f"\n✅ 已保存裁剪的图标: {output_path}")
        print(f"   大小: {cropped.width} x {cropped.height}")
        return True
    else:
        print("\n⚠️ 未选择区域，已取消")
        return False


def simple_crop_prompt(image, output_path):
    """
    简单的坐标输入裁剪（如果matplotlib不可用）

    Args:
        image: PIL Image对象
        output_path: 输出路径

    Returns:
        True表示成功，False表示失败
    """
    print("\n" + "=" * 80)
    print("手动输入裁剪坐标")
    print("=" * 80)
    print(f"图片大小: {image.width} x {image.height}")
    print("\n请先查看完整截图，找到菜单图标的位置坐标")
    print("然后输入裁剪区域的四个坐标值")
    print("=" * 80)

    try:
        x1 = int(input("左上角 X 坐标: ").strip())
        y1 = int(input("左上角 Y 坐标: ").strip())
        x2 = int(input("右下角 X 坐标: ").strip())
        y2 = int(input("右下角 Y 坐标: ").strip())

        # 验证坐标
        if x1 >= x2 or y1 >= y2:
            print("❌ 坐标无效（左上角必须在右下角左上方）")
            return False

        if x1 < 0 or y1 < 0 or x2 > image.width or y2 > image.height:
            print("❌ 坐标超出图片范围")
            return False

        # 裁剪并保存
        cropped = image.crop((x1, y1, x2, y2))
        cropped.save(output_path)
        print(f"\n✅ 已保存裁剪的图标: {output_path}")
        print(f"   大小: {cropped.width} x {cropped.height}")
        return True

    except ValueError:
        print("❌ 输入无效")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD 菜单图标自动截取工具")
    print("=" * 80)

    # 检查依赖
    try:
        from PIL import Image
    except ImportError:
        print("\n❌ 缺少必要的库")
        print("请安装: pip install pillow pywin32")
        return

    # 查找AutoCAD窗口
    print("\n[步骤 1/4] 查找AutoCAD窗口...")
    windows = find_autocad_window()

    if not windows:
        print("❌ 未找到AutoCAD窗口")
        print("请先启动AutoCAD，然后重新运行此脚本")
        return

    print(f"✅ 找到 {len(windows)} 个AutoCAD窗口:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"  {i}. {title} (HWND={hwnd})")

    # 选择窗口
    if len(windows) > 1:
        choice = input(f"\n请选择窗口编号 (1-{len(windows)}): ").strip()
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(windows):
                print("❌ 无效选择")
                return
        except ValueError:
            print("❌ 无效输入")
            return
    else:
        idx = 0

    hwnd, title = windows[idx]
    print(f"\n✅ 选择窗口: {title}")

    # 截取窗口
    print("\n[步骤 2/4] 截取窗口截图...")
    image = capture_window(hwnd)

    if not image:
        print("❌ 截图失败")
        return

    print(f"✅ 截图成功")
    print(f"   大小: {image.width} x {image.height}")

    # 保存完整截图
    full_screenshot_dir = project_root / "screenshots"
    full_screenshot_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    full_screenshot_path = full_screenshot_dir / f"autocad_full_{timestamp}.png"
    image.save(full_screenshot_path)
    print(f"✅ 完整截图已保存: {full_screenshot_path}")

    # 裁剪菜单图标
    print("\n[步骤 3/4] 裁剪菜单图标...")

    icons_dir = project_root / "menu_icons"
    icons_dir.mkdir(exist_ok=True)

    icon_name = input("\n请输入菜单名称（如'依云'）: ").strip()
    if not icon_name:
        icon_name = "menu"

    output_path = icons_dir / f"{icon_name}.png"

    # 尝试使用matplotlib交互式裁剪
    try:
        import matplotlib.pyplot as plt
        success = interactive_crop(image, output_path)
    except ImportError:
        print("\n⚠️ matplotlib未安装，使用手动输入坐标方式")
        print("（建议安装matplotlib以获得更好的体验: pip install matplotlib）")
        success = simple_crop_prompt(image, output_path)

    if success:
        print("\n[步骤 4/4] 完成!")
        print("=" * 80)
        print("✅ 菜单图标已准备好")
        print("=" * 80)
        print(f"\n图标路径: {output_path}")
        print("\n下一步:")
        print("  1. 运行图像识别工具测试点击")
        print("     python scripts\\click_menu_by_image.py")
        print("  2. 或将图标路径添加到配置中使用")
    else:
        print("\n❌ 裁剪失败")


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
