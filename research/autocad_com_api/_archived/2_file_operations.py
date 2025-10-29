"""
AutoCAD 文件操作示例

演示如何打开、保存、关闭 DWG 文件

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client
import os
import time
from pathlib import Path
from typing import Optional


class AutoCADFileOps:
    """AutoCAD 文件操作类"""

    def __init__(self, acad_app):
        """
        初始化文件操作

        Args:
            acad_app: AutoCAD Application 对象
        """
        self.acad = acad_app
        self.documents = acad_app.Documents

    def open_file(self, file_path: str, read_only: bool = False) -> Optional[object]:
        """
        打开 DWG 文件

        Args:
            file_path: DWG 文件路径
            read_only: 是否以只读模式打开

        Returns:
            AcadDocument 对象或 None
        """
        # 转换为绝对路径
        abs_path = os.path.abspath(file_path)

        # 检查文件是否存在
        if not os.path.exists(abs_path):
            print(f"❌ 文件不存在: {abs_path}")
            return None

        try:
            print(f"\n📂 打开文件: {abs_path}")
            print(f"   只读模式: {read_only}")

            # 打开文件
            if read_only:
                doc = self.documents.Open(abs_path, True)  # 第二个参数表示只读
            else:
                doc = self.documents.Open(abs_path)

            print(f"✅ 文件已打开: {doc.Name}")
            print(f"   模型空间对象数: {doc.ModelSpace.Count}")
            print(f"   图层数: {doc.Layers.Count}")
            print(f"   活动状态: {doc.Active}")

            return doc

        except Exception as e:
            print(f"❌ 打开文件失败: {e}")
            return None

    def save_document(self, doc, new_path: Optional[str] = None) -> bool:
        """
        保存文档

        Args:
            doc: AcadDocument 对象
            new_path: 新路径（另存为），None 表示保存

        Returns:
            True 表示成功，False 表示失败
        """
        try:
            if new_path:
                # 另存为
                abs_path = os.path.abspath(new_path)
                print(f"\n💾 另存为: {abs_path}")
                doc.SaveAs(abs_path)
                print(f"✅ 文件已另存为: {abs_path}")
            else:
                # 保存
                print(f"\n💾 保存文件: {doc.Name}")
                doc.Save()
                print(f"✅ 文件已保存")

            return True

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

    def close_document(self, doc, save_changes: bool = True) -> bool:
        """
        关闭文档

        Args:
            doc: AcadDocument 对象
            save_changes: 是否保存更改

        Returns:
            True 表示成功，False 表示失败
        """
        try:
            doc_name = doc.Name
            print(f"\n🗙 关闭文件: {doc_name}")
            print(f"   保存更改: {save_changes}")

            doc.Close(save_changes)
            print(f"✅ 文件已关闭")
            return True

        except Exception as e:
            print(f"❌ 关闭失败: {e}")
            return False

    def close_all_documents(self, save_changes: bool = False) -> int:
        """
        关闭所有打开的文档

        Args:
            save_changes: 是否保存更改

        Returns:
            关闭的文档数量
        """
        count = self.documents.Count
        print(f"\n🗙 关闭所有文档（共 {count} 个）...")

        closed_count = 0
        while self.documents.Count > 0:
            try:
                doc = self.documents.Item(0)
                doc.Close(save_changes)
                closed_count += 1
            except:
                break

        print(f"✅ 已关闭 {closed_count} 个文档")
        return closed_count

    def get_document_info(self, doc) -> dict:
        """
        获取文档详细信息

        Args:
            doc: AcadDocument 对象

        Returns:
            文档信息字典
        """
        try:
            info = {
                "name": doc.Name,
                "path": doc.Path if doc.Path else "未保存",
                "full_name": doc.FullName if doc.Path else "未保存",
                "active": doc.Active,
                "read_only": doc.ReadOnly,
                "saved": doc.Saved,
                "model_space_count": doc.ModelSpace.Count,
                "paper_space_count": doc.PaperSpace.Count,
                "layers_count": doc.Layers.Count,
                "blocks_count": doc.Blocks.Count,
                "layouts_count": doc.Layouts.Count,
            }
            return info
        except Exception as e:
            return {"error": str(e)}

    def list_all_documents(self):
        """列出所有打开的文档"""
        count = self.documents.Count
        print(f"\n📋 打开的文档列表（共 {count} 个）:")

        if count == 0:
            print("   （无打开的文档）")
            return

        for i in range(count):
            doc = self.documents.Item(i)
            status = "✅ 活动" if doc.Active else "  "
            saved = "💾" if doc.Saved else "✏️ "
            print(f"   {i+1}. {status} {saved} {doc.Name}")

    def activate_document(self, doc) -> bool:
        """
        激活文档

        Args:
            doc: AcadDocument 对象

        Returns:
            True 表示成功
        """
        try:
            doc.Activate()
            print(f"✅ 已激活文档: {doc.Name}")
            return True
        except Exception as e:
            print(f"❌ 激活失败: {e}")
            return False


def demo_file_operations():
    """演示文件操作"""
    print("\n" + "=" * 60)
    print("AutoCAD 文件操作示例")
    print("=" * 60)

    # 连接到 AutoCAD
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        print(f"✅ 已连接到 AutoCAD {acad.Version}")
    except:
        try:
            acad = win32com.client.Dispatch("AutoCAD.Application")
            acad.Visible = True
            print("✅ AutoCAD 已启动")
        except Exception as e:
            print(f"❌ 无法连接到 AutoCAD: {e}")
            return

    # 创建文件操作对象
    file_ops = AutoCADFileOps(acad)

    # 演示：列出当前打开的文档
    file_ops.list_all_documents()

    # 演示：打开文件（需要提供实际的文件路径）
    # 这里仅作演示，实际使用时需要替换为真实路径
    test_file = r"C:\path\to\your\test.dwg"  # 替换为实际路径

    if os.path.exists(test_file):
        # 打开文件
        doc = file_ops.open_file(test_file)

        if doc:
            # 获取文档信息
            info = file_ops.get_document_info(doc)
            print("\n📋 文档信息:")
            for key, value in info.items():
                print(f"   {key}: {value}")

            # 演示：另存为
            new_file = test_file.replace(".dwg", "_copy.dwg")
            file_ops.save_document(doc, new_file)

            # 演示：关闭文档
            time.sleep(2)  # 等待2秒
            file_ops.close_document(doc, save_changes=False)
    else:
        print(f"\n⚠️ 测试文件不存在: {test_file}")
        print("   请修改 test_file 变量为实际的 DWG 文件路径")

    # 最后列出文档状态
    file_ops.list_all_documents()

    print("\n✅ 演示完成")


if __name__ == "__main__":
    demo_file_operations()
    input("\n按 Enter 键退出...")
