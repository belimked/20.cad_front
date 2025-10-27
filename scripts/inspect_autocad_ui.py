"""
AutoCAD UI结构检查工具

用于诊断pywinauto无法找到特定菜单项的问题
检查AutoCAD窗口的完整UI树结构

Usage:
    1. 启动AutoCAD
    2. 运行此脚本
    3. 查看生成的UI结构报告

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import win32gui
from pywinauto import Desktop
from pywinauto.findwindows import ElementNotFoundError
import json


def find_autocad_windows():
    """查找所有AutoCAD窗口"""
    windows = []

    def enum_callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'AutoCAD' in title or 'acad' in title.lower():
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(enum_callback, None)
    return windows


def dump_ui_tree(element, depth=0, max_depth=10):
    """递归导出UI树结构"""
    if depth > max_depth:
        return {"_note": "达到最大深度"}

    try:
        info = {
            "class_name": element.class_name(),
            "control_type": element.element_info.control_type,
            "name": element.window_text(),
            "enabled": element.is_enabled(),
            "visible": element.is_visible(),
        }

        # 获取子控件
        try:
            children = element.children()
            if children:
                info["children"] = []
                for child in children[:50]:  # 限制最多50个子控件，避免太大
                    child_info = dump_ui_tree(child, depth + 1, max_depth)
                    info["children"].append(child_info)

                if len(children) > 50:
                    info["_note"] = f"子控件过多（{len(children)}个），仅显示前50个"
        except:
            pass

        return info

    except Exception as e:
        return {"_error": str(e)}


def search_control_by_text(element, search_text, results=None, depth=0, max_depth=10):
    """搜索包含特定文本的控件"""
    if results is None:
        results = []

    if depth > max_depth:
        return results

    try:
        text = element.window_text()
        if search_text in text:
            results.append({
                "text": text,
                "class_name": element.class_name(),
                "control_type": element.element_info.control_type,
                "depth": depth,
                "enabled": element.is_enabled(),
                "visible": element.is_visible(),
            })

        # 递归搜索子控件
        try:
            children = element.children()
            for child in children:
                search_control_by_text(child, search_text, results, depth + 1, max_depth)
        except:
            pass

    except Exception as e:
        pass

    return results


def main():
    """主函数"""
    print("=" * 80)
    print("AutoCAD UI结构检查工具")
    print("=" * 80)

    # 查找AutoCAD窗口
    print("\n[步骤 1/4] 查找AutoCAD窗口...")
    windows = find_autocad_windows()

    if not windows:
        print("❌ 未找到AutoCAD窗口")
        print("请先启动AutoCAD，然后重新运行此脚本")
        return

    print(f"✅ 找到 {len(windows)} 个AutoCAD窗口:")
    for i, (hwnd, title) in enumerate(windows, 1):
        print(f"  {i}. {title} (HWND={hwnd})")

    # 选择窗口
    if len(windows) > 1:
        choice = input("\n请选择窗口编号 (1-{}): ".format(len(windows)))
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

    # 使用pywinauto连接
    print("\n[步骤 2/4] 连接窗口...")
    try:
        desktop = Desktop(backend="uia")
        app_window = desktop.window(handle=hwnd)
        print("✅ 已连接到窗口")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 搜索特定文本
    search_text = input("\n请输入要搜索的菜单文本 (如'依云'，直接回车跳过): ").strip()

    if search_text:
        print(f"\n[步骤 3/4] 搜索包含 '{search_text}' 的控件...")
        results = search_control_by_text(app_window, search_text)

        if results:
            print(f"✅ 找到 {len(results)} 个匹配的控件:")
            for i, result in enumerate(results, 1):
                print(f"\n  [{i}] 控件信息:")
                print(f"      文本: {result['text']}")
                print(f"      类名: {result['class_name']}")
                print(f"      类型: {result['control_type']}")
                print(f"      深度: {result['depth']}")
                print(f"      可用: {result['enabled']}")
                print(f"      可见: {result['visible']}")
        else:
            print(f"❌ 未找到包含 '{search_text}' 的控件")
            print("\n可能的原因:")
            print("  1. 文本不匹配（大小写、空格、特殊字符）")
            print("  2. 控件不在UI树中（可能是图像/自绘菜单）")
            print("  3. 控件深度超过搜索限制（当前max_depth=10）")

    # 导出完整UI树
    print("\n[步骤 4/4] 导出UI树结构...")
    try:
        ui_tree = dump_ui_tree(app_window, max_depth=5)

        # 保存到文件
        output_file = project_root / "autocad_ui_tree.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ui_tree, f, ensure_ascii=False, indent=2)

        print(f"✅ UI树已保存到: {output_file}")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.1f} KB")

    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()

    # 尝试列出顶层菜单栏
    print("\n[额外检查] 查找菜单栏...")
    try:
        # 尝试查找MenuBar控件
        menu_bars = []
        try:
            menu_bar = app_window.child_window(control_type="MenuBar")
            if menu_bar.exists():
                menu_bars.append(menu_bar)
                print("✅ 找到MenuBar控件")

                # 列出菜单项
                menu_items = menu_bar.children()
                print(f"   菜单项数量: {len(menu_items)}")
                for i, item in enumerate(menu_items[:20], 1):  # 最多显示20个
                    try:
                        text = item.window_text()
                        ctrl_type = item.element_info.control_type
                        print(f"   {i}. {text} ({ctrl_type})")
                    except:
                        pass
        except ElementNotFoundError:
            print("⚠️ 未找到MenuBar控件")
            print("   可能AutoCAD使用的是Ribbon界面而不是传统菜单栏")

    except Exception as e:
        print(f"❌ 查找菜单栏失败: {e}")

    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)
    print("\n建议:")
    print("  1. 查看生成的 autocad_ui_tree.json 文件了解完整UI结构")
    print("  2. 如果未找到目标控件，可能需要:")
    print("     - 使用图像识别 (pyautogui)")
    print("     - 使用键盘快捷键")
    print("     - 使用AutoCAD命令行")


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
