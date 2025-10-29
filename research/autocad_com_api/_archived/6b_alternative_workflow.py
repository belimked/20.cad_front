"""
AutoCAD 自动化工作流程 - 备用方案

如果自动启动失败，请使用此脚本
要求：AutoCAD 必须已经手动启动

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client
import pywintypes
import time
import os
from pathlib import Path


def open_file_in_running_cad(dwg_file_path: str) -> bool:
    """
    在已运行的 AutoCAD 中打开文件

    Args:
        dwg_file_path: DWG 文件路径

    Returns:
        True 表示成功，False 表示失败
    """
    print("=" * 60)
    print("在运行中的 AutoCAD 打开文件")
    print("=" * 60)

    # 验证文件
    dwg_path = Path(dwg_file_path)
    if not dwg_path.exists():
        print(f"❌ 文件不存在: {dwg_file_path}")
        return False

    abs_path = str(dwg_path.absolute())
    print(f"📄 目标文件: {abs_path}")

    try:
        # 连接到已运行的 AutoCAD
        print("\n🔍 连接到运行中的 AutoCAD...")
        acad = win32com.client.GetActiveObject("AutoCAD.Application")

        print(f"✅ 已连接到 AutoCAD {acad.Version}")
        print(f"   当前打开文档数: {acad.Documents.Count}")

        # 打开文件（带重试）
        print(f"\n📂 打开文件...")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                doc = acad.Documents.Open(abs_path)
                print(f"✅ 文件已打开: {doc.Name}")

                # 验证文件加载
                print(f"\n🔍 验证文件...")
                print(f"   文件名: {doc.Name}")
                print(f"   完整路径: {doc.FullName}")

                try:
                    entity_count = doc.ModelSpace.Count
                    print(f"   模型空间实体数: {entity_count}")
                except:
                    print(f"   ⚠️ 无法获取实体数")

                print(f"\n✅ 完成！")
                return True

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠️ 尝试 {attempt + 1}/{max_retries} 失败: {e}")
                    print(f"  ⏳ 等待 3 秒后重试...")
                    time.sleep(3)
                else:
                    raise e

    except pywintypes.com_error as e:
        error_code = e.args[0]
        print(f"\n❌ COM 错误 ({error_code}): {e.args[1]}")

        if error_code == -2147221005:
            print("\n💡 AutoCAD 未运行")
            print("   请先手动启动 AutoCAD，然后重新运行此脚本")
        else:
            print(f"\n💡 错误代码说明:")
            print(f"   {error_code}: {e.args[1]}")

        return False

    except Exception as e:
        print(f"\n❌ 打开文件失败: {e}")
        return False


def main():
    """主函数"""

    # 配置文件路径
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    # 检查文件
    if not os.path.exists(dwg_file):
        print("=" * 60)
        print("❌ 文件不存在")
        print("=" * 60)
        print(f"当前路径: {dwg_file}")
        print("\n请修改脚本中的 dwg_file 变量")
        input("\n按 Enter 键退出...")
        return

    print("\n⚠️ 重要提示：")
    print("  1. 请先手动启动 AutoCAD")
    print("  2. 不需要打开任何文件")
    print("  3. 确保 AutoCAD 窗口可见")

    input("\n确认 AutoCAD 已启动后，按 Enter 键继续...")

    # 打开文件
    success = open_file_in_running_cad(dwg_file)

    if success:
        print("\n🎉 成功！")
        print("\n💡 提示：")
        print("  - 文件已在 AutoCAD 中打开")
        print("  - 可以在 AutoCAD 窗口中查看")
        print("  - 按 Enter 键退出此脚本（AutoCAD 会继续运行）")
    else:
        print("\n❌ 失败")
        print("\n🔧 故障排查：")
        print("  1. 确认 AutoCAD 已启动")
        print("  2. 确认文件路径正确")
        print("  3. 确认文件未被占用")
        print("  4. 尝试手动在 AutoCAD 中打开文件")

    input("\n按 Enter 键退出...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
