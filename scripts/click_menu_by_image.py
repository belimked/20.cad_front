"""
使用图像识别点击AutoCAD菜单

适用于无法通过pywinauto找到的自绘菜单
需要提前截取菜单图标

Usage:
    1. 手动截取"依云"菜单图标，保存为 menu_icons/依云.png
    2. 运行此脚本

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
import win32com.client


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


def click_menu_by_image(menu_icon_path: str, confidence=0.8):
    """
    使用图像识别点击菜单

    Args:
        menu_icon_path: 菜单图标图片路径
        confidence: 匹配置信度 (0.0-1.0)

    Returns:
        True表示成功，False表示失败
    """
    try:
        import pyautogui
    except ImportError:
        print("❌ 缺少pyautogui库")
        print("请安装: pip install pyautogui pillow opencv-python")
        return False

    icon_path = Path(menu_icon_path)
    if not icon_path.exists():
        print(f"❌ 图标文件不存在: {icon_path}")
        return False

    print(f"🔍 搜索图标: {icon_path.name}")
    print(f"   置信度: {confidence}")

    # 查找AutoCAD窗口并激活
    windows = find_autocad_window()
    if windows:
        hwnd, title = windows[0]
        print(f"✅ 找到窗口: {title}")
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)

    # 在屏幕上查找图标
    try:
        location = pyautogui.locateOnScreen(str(icon_path), confidence=confidence)

        if location:
            # 计算中心点
            center_x = location.left + location.width // 2
            center_y = location.top + location.height // 2

            print(f"✅ 找到图标位置: ({center_x}, {center_y})")
            print(f"   区域: left={location.left}, top={location.top}, "
                  f"width={location.width}, height={location.height}")

            # 移动鼠标并点击
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            time.sleep(0.2)
            pyautogui.click()

            print("✅ 已点击图标")
            return True
        else:
            print("❌ 未找到图标")
            print("\n可能的原因:")
            print("  1. 图标被遮挡或不可见")
            print("  2. 图标颜色/样式与截图不同")
            print("  3. 屏幕分辨率/缩放比例不同")
            print("  4. 置信度设置过高")
            print("\n建议:")
            print("  1. 确保AutoCAD窗口在前台")
            print("  2. 重新截取图标（确保清晰）")
            print("  3. 降低置信度（如0.7）")
            return False

    except Exception as e:
        print(f"❌ 图像识别失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD 菜单图像识别点击工具")
    print("=" * 80)

    # 检查menu_icons目录
    icons_dir = project_root / "menu_icons"
    if not icons_dir.exists():
        print(f"\n⚠️ 图标目录不存在，正在创建: {icons_dir}")
        icons_dir.mkdir(parents=True)

    # 列出可用图标
    icon_files = list(icons_dir.glob("*.png"))
    if not icon_files:
        print(f"\n❌ 未找到图标文件")
        print(f"\n请按以下步骤准备图标:")
        print(f"  1. 启动AutoCAD并打开DWG文件")
        print(f"  2. 使用截图工具（Win+Shift+S）截取"依云"菜单图标")
        print(f"  3. 保存为: {icons_dir / '依云.png'}")
        print(f"  4. 重新运行此脚本")
        return

    print(f"\n✅ 找到 {len(icon_files)} 个图标文件:")
    for i, icon_file in enumerate(icon_files, 1):
        print(f"  {i}. {icon_file.name} ({icon_file.stat().st_size / 1024:.1f} KB)")

    # 选择图标
    if len(icon_files) == 1:
        selected_icon = icon_files[0]
        print(f"\n自动选择: {selected_icon.name}")
    else:
        choice = input(f"\n请选择图标编号 (1-{len(icon_files)}): ").strip()
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(icon_files):
                print("❌ 无效选择")
                return
            selected_icon = icon_files[idx]
        except ValueError:
            print("❌ 无效输入")
            return

    # 设置置信度
    confidence_input = input("\n请输入匹配置信度 (0.0-1.0，默认0.8): ").strip()
    confidence = float(confidence_input) if confidence_input else 0.8

    print(f"\n" + "=" * 80)
    print("开始搜索并点击...")
    print("=" * 80)

    # 执行点击
    success = click_menu_by_image(str(selected_icon), confidence)

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
