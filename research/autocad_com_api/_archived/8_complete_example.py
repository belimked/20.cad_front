"""
完整的 AutoCAD 自动化流程示例

整合所有步骤：
01. 关闭现有 CAD，打开指定 DWG 文件
02. 验证文件已加载（sleep 等待）
03. 打开 CAD 指定菜单

Author: CAD Auto Processor Team
Date: 2025-10-24

依赖安装:
pip install pywin32 psutil pywinauto
"""

import sys
import os
from pathlib import Path

# 导入我们创建的模块
# 由于在同一目录，直接导入
try:
    from autocad_workflow import AutoCADWorkflow
    from menu_automation import AutoCADMenuController
except ImportError:
    # 如果无法导入，说明模块文件名不同，提供说明
    print("❌ 无法导入模块")
    print("请确保以下文件在同一目录:")
    print("  - 6_autocad_workflow.py (包含 AutoCADWorkflow)")
    print("  - 7_menu_automation.py (包含 AutoCADMenuController)")
    sys.exit(1)


class CompleteAutoCADAutomation:
    """
    完整的 AutoCAD 自动化流程

    集成了:
    - 进程管理（关闭/启动）
    - 文件操作（打开/验证）
    - UI 自动化（菜单操作）
    """

    def __init__(self, dwg_file_path: str):
        """
        初始化自动化流程

        Args:
            dwg_file_path: DWG 文件的完整路径
        """
        self.dwg_file_path = dwg_file_path
        self.workflow = AutoCADWorkflow()
        self.menu_controller = AutoCADMenuController()

    def run(self, menu_operations: list = None) -> bool:
        """
        运行完整的自动化流程

        Args:
            menu_operations: 菜单操作列表，每项格式为:
                - {"type": "menu", "path": ["文件", "打开"]}
                - {"type": "command", "command": "ZOOM"}

        Returns:
            True 表示成功，False 表示失败
        """
        print("\n" + "=" * 80)
        print("AutoCAD 完整自动化流程")
        print("=" * 80)
        print(f"📄 目标文件: {self.dwg_file_path}")
        print("=" * 80)

        try:
            # ========================================
            # 阶段 1: 关闭并打开 CAD
            # ========================================
            print("\n" + "▶" * 40)
            print("阶段 1/3: 关闭现有 CAD 并打开指定文件")
            print("▶" * 40)

            if not self.workflow.step1_close_and_open_cad(self.dwg_file_path, force_close=True):
                print("\n❌ 阶段 1 失败：无法打开 CAD 和文件")
                return False

            print("\n✅ 阶段 1 完成")

            # ========================================
            # 阶段 2: 验证文件已加载
            # ========================================
            print("\n" + "▶" * 40)
            print("阶段 2/3: 验证文件已加载")
            print("▶" * 40)

            if not self.workflow.step2_verify_file_loaded(max_wait_time=30, check_interval=2.0):
                print("\n❌ 阶段 2 失败：文件未正确加载")
                return False

            print("\n✅ 阶段 2 完成")

            # ========================================
            # 阶段 3: UI 自动化（菜单操作）
            # ========================================
            if menu_operations:
                print("\n" + "▶" * 40)
                print("阶段 3/3: 执行菜单操作")
                print("▶" * 40)

                # 连接到 AutoCAD 窗口（UI Automation）
                if not self.menu_controller.connect_to_autocad(timeout=10):
                    print("\n⚠️ 警告：无法连接到 AutoCAD 窗口进行 UI 操作")
                    print("     COM API 操作已完成，但 UI 自动化失败")
                    return True  # COM 部分成功，UI 失败不算完全失败

                # 等待窗口就绪
                self.menu_controller.wait_for_idle(timeout=10)

                # 执行菜单操作
                success_count = 0
                for i, operation in enumerate(menu_operations, 1):
                    print(f"\n📋 操作 {i}/{len(menu_operations)}")

                    op_type = operation.get("type")

                    if op_type == "menu":
                        # 点击菜单
                        menu_path = operation.get("path", [])
                        if self.menu_controller.click_menu(menu_path):
                            success_count += 1
                        else:
                            print(f"⚠️ 菜单操作失败: {menu_path}")

                    elif op_type == "command":
                        # 执行命令
                        command = operation.get("command", "")
                        if self.menu_controller.execute_command_via_keyboard(command):
                            success_count += 1
                        else:
                            print(f"⚠️ 命令执行失败: {command}")

                    else:
                        print(f"⚠️ 未知操作类型: {op_type}")

                print(f"\n✅ 阶段 3 完成：{success_count}/{len(menu_operations)} 个操作成功")

            # ========================================
            # 完成
            # ========================================
            print("\n" + "=" * 80)
            print("✅ 自动化流程全部完成！")
            print("=" * 80)

            print("\n📊 流程摘要:")
            print(f"  ✅ 文件已打开: {Path(self.dwg_file_path).name}")
            print(f"  ✅ 文件已验证: 模型空间已加载")
            if menu_operations:
                print(f"  ✅ 菜单操作: {success_count}/{len(menu_operations)} 成功")

            return True

        except Exception as e:
            print(f"\n❌ 自动化流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # 清理资源
            self.workflow.cleanup()

    def cleanup(self):
        """清理所有资源"""
        self.workflow.cleanup()


# ============================================================
# 主程序和配置
# ============================================================

def main():
    """主函数 - 配置并运行自动化流程"""

    print("=" * 80)
    print("AutoCAD 完整自动化流程配置")
    print("=" * 80)

    # ========================================
    # 配置 1: DWG 文件路径
    # ========================================
    # ⚠️ 请修改为实际的 DWG 文件路径
    dwg_file = r"C:\path\to\your\drawing.dwg"

    # 检查文件是否存在
    if not os.path.exists(dwg_file):
        print("\n❌ DWG 文件不存在")
        print(f"当前配置路径: {dwg_file}")
        print("\n请修改脚本中的 dwg_file 变量为实际路径:")
        print('  dwg_file = r"C:\\实际路径\\your_drawing.dwg"')
        print("\n示例:")
        print('  dwg_file = r"C:\\Users\\YourName\\Documents\\test.dwg"')
        input("\n按 Enter 键退出...")
        return

    print(f"\n✅ 目标文件: {dwg_file}")

    # ========================================
    # 配置 2: 菜单操作（可选）
    # ========================================
    # 定义要执行的菜单操作

    # 示例 1: 不执行任何菜单操作（仅打开文件）
    menu_operations = None

    # 示例 2: 执行命令
    # menu_operations = [
    #     {"type": "command", "command": "ZOOM"},
    #     {"type": "command", "command": "E"},  # ZOOM Extents
    # ]

    # 示例 3: 点击菜单（需要根据 AutoCAD 版本和语言调整）
    # menu_operations = [
    #     {"type": "menu", "path": ["工具", "选项"]},  # 中文版
    #     # {"type": "menu", "path": ["Tools", "Options"]},  # 英文版
    # ]

    # 示例 4: 混合操作
    # menu_operations = [
    #     {"type": "command", "command": "ZOOM"},
    #     {"type": "command", "command": "E"},
    #     {"type": "menu", "path": ["工具", "选项"]},
    # ]

    print("\n📋 菜单操作配置:")
    if menu_operations:
        for i, op in enumerate(menu_operations, 1):
            print(f"  {i}. {op}")
    else:
        print("  无（仅打开和验证文件）")

    # ========================================
    # 确认并执行
    # ========================================
    print("\n" + "=" * 80)
    print("准备执行自动化流程")
    print("=" * 80)
    print("\n⚠️ 警告：")
    print("  - 此脚本将关闭所有运行中的 AutoCAD 进程")
    print("  - 请确保已保存所有未保存的工作")
    print("  - 建议先在测试环境中运行")

    response = input("\n是否继续？(y/n): ")
    if response.lower() != 'y':
        print("\n取消执行")
        return

    # ========================================
    # 运行自动化流程
    # ========================================
    automation = CompleteAutoCADAutomation(dwg_file)

    try:
        success = automation.run(menu_operations=menu_operations)

        if success:
            print("\n🎉 自动化流程成功完成！")
            print("\n💡 您现在可以：")
            print("  - 在 AutoCAD 窗口中查看已打开的文件")
            print("  - 手动操作 AutoCAD")
            print("  - 继续开发其他自动化步骤")
        else:
            print("\n❌ 自动化流程失败")
            print("\n🔧 故障排查建议：")
            print("  1. 确认 AutoCAD 已正确安装")
            print("  2. 确认 DWG 文件路径正确")
            print("  3. 检查 AutoCAD 版本兼容性（建议 2014+）")
            print("  4. 查看上面的错误信息")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        automation.cleanup()
        input("\n按 Enter 键退出...")


if __name__ == "__main__":
    main()
