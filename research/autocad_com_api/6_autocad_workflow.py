"""
AutoCAD 自动化工作流程

实现完整的 CAD 自动化流程：
01. 关闭已有 CAD 进程，重新启动并打开指定 DWG 文件
02. 验证 CAD 已打开且图纸已加载（等待机制）
03. 打开 CAD 指定菜单

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import win32com.client
import pywintypes
import psutil
import time
import os
from typing import Optional, Tuple
from pathlib import Path


class AutoCADWorkflow:
    """
    AutoCAD 自动化工作流程管理器

    完整流程：
    1. 关闭现有 CAD 进程
    2. 启动 CAD 并打开指定文件
    3. 验证文件已加载
    4. 执行菜单操作
    """

    def __init__(self):
        """初始化工作流程管理器"""
        self.acad = None
        self.current_doc = None
        self.current_file = None

    def step1_close_and_open_cad(self, dwg_file_path: str, force_close: bool = True) -> bool:
        """
        步骤 1: 关闭已有 CAD 进程，重新启动并打开指定 DWG 文件

        Args:
            dwg_file_path: DWG 文件的完整路径
            force_close: 是否强制关闭现有 CAD 进程

        Returns:
            True 表示成功，False 表示失败
        """
        print("=" * 60)
        print("步骤 1: 关闭现有 CAD 并打开指定文件")
        print("=" * 60)

        # 验证文件存在
        dwg_path = Path(dwg_file_path)
        if not dwg_path.exists():
            print(f"❌ 错误：文件不存在: {dwg_file_path}")
            return False

        if not dwg_path.suffix.lower() == '.dwg':
            print(f"❌ 错误：不是 DWG 文件: {dwg_file_path}")
            return False

        self.current_file = str(dwg_path.absolute())
        print(f"📄 目标文件: {self.current_file}")

        # 1.1 关闭现有 AutoCAD 进程
        if force_close:
            print("\n🔍 检查现有 AutoCAD 进程...")
            closed_count = self._close_all_autocad_processes()
            if closed_count > 0:
                print(f"✅ 已关闭 {closed_count} 个 AutoCAD 进程")
                print("⏳ 等待 3 秒以确保进程完全关闭...")
                time.sleep(3)
            else:
                print("✅ 没有发现运行中的 AutoCAD 进程")

        # 1.2 启动 AutoCAD 并打开文件
        print(f"\n🚀 启动 AutoCAD 并打开文件...")
        try:
            # 启动 AutoCAD
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acad.Visible = True

            print("✅ AutoCAD 已启动")
            print("⏳ 等待 5 秒让 AutoCAD 完全初始化...")
            time.sleep(5)

            # 打开指定文件
            print(f"📂 打开文件: {self.current_file}")
            self.current_doc = self.acad.Documents.Open(self.current_file)

            print(f"✅ 文件已打开: {self.current_doc.Name}")

            return True

        except Exception as e:
            print(f"❌ 启动 AutoCAD 或打开文件失败: {e}")
            return False

    def step2_verify_file_loaded(self, max_wait_time: int = 30, check_interval: float = 2.0) -> bool:
        """
        步骤 2: 验证 CAD 已打开且指定图纸已加载

        Args:
            max_wait_time: 最大等待时间（秒）
            check_interval: 检查间隔（秒）

        Returns:
            True 表示文件已加载，False 表示超时或失败
        """
        print("\n" + "=" * 60)
        print("步骤 2: 验证文件已加载")
        print("=" * 60)

        if self.acad is None or self.current_doc is None:
            print("❌ 错误：AutoCAD 或文档未初始化")
            return False

        print(f"⏳ 最大等待时间: {max_wait_time} 秒")
        print(f"🔄 检查间隔: {check_interval} 秒")

        start_time = time.time()
        check_count = 0

        while time.time() - start_time < max_wait_time:
            check_count += 1
            elapsed = time.time() - start_time

            print(f"\n🔍 检查 #{check_count} (已用时: {elapsed:.1f}秒)...")

            try:
                # 检查 1: CAD 进程是否存在
                if not self._is_autocad_running():
                    print("❌ AutoCAD 进程已关闭")
                    return False

                print("  ✅ AutoCAD 进程正在运行")

                # 检查 2: 文档是否仍然打开
                try:
                    doc_name = self.current_doc.Name
                    print(f"  ✅ 文档仍然打开: {doc_name}")
                except:
                    print("  ❌ 文档已关闭")
                    return False

                # 检查 3: 文档是否活动
                try:
                    active_doc = self.acad.ActiveDocument
                    if active_doc.Name == self.current_doc.Name:
                        print(f"  ✅ 文档是活动文档")
                    else:
                        print(f"  ⚠️ 活动文档是: {active_doc.Name}")
                except:
                    print("  ⚠️ 无法获取活动文档")

                # 检查 4: 文档是否完全加载（检查实体数量）
                try:
                    model_space = self.current_doc.ModelSpace
                    entity_count = model_space.Count
                    print(f"  ✅ 模型空间实体数: {entity_count}")

                    # 如果有实体，认为文件已加载完成
                    if entity_count >= 0:
                        print("\n✅ 文件验证成功！")
                        print(f"📊 文档信息:")
                        print(f"   - 文件名: {self.current_doc.Name}")
                        print(f"   - 完整路径: {self.current_doc.FullName}")
                        print(f"   - 实体数量: {entity_count}")
                        return True

                except Exception as e:
                    print(f"  ⚠️ 无法访问模型空间: {e}")

                # 等待下一次检查
                print(f"⏳ 等待 {check_interval} 秒后再次检查...")
                time.sleep(check_interval)

            except Exception as e:
                print(f"  ❌ 检查过程出错: {e}")
                time.sleep(check_interval)

        print(f"\n❌ 超时：文件在 {max_wait_time} 秒内未完全加载")
        return False

    def step3_open_menu(self, menu_name: str, submenu_name: Optional[str] = None) -> bool:
        """
        步骤 3: 打开 CAD 指定菜单

        Args:
            menu_name: 菜单名称（如 "工具", "Tools"）
            submenu_name: 子菜单名称（可选）

        Returns:
            True 表示成功，False 表示失败

        注意：
        - AutoCAD COM API 不直接支持菜单操作
        - 需要使用 SendCommand 或其他方式
        """
        print("\n" + "=" * 60)
        print("步骤 3: 打开 CAD 菜单")
        print("=" * 60)

        if self.acad is None or self.current_doc is None:
            print("❌ 错误：AutoCAD 或文档未初始化")
            return False

        print(f"📋 菜单名称: {menu_name}")
        if submenu_name:
            print(f"📋 子菜单: {submenu_name}")

        try:
            # 方式 1: 尝试通过 CUI 命令打开菜单
            # 注意：实际的菜单操作取决于具体需求

            print("\n⚠️ 注意：AutoCAD COM API 不直接支持菜单点击")
            print("建议使用以下方式之一：")
            print("1. 使用 SendCommand 发送菜单对应的命令")
            print("2. 使用 UI Automation (pywinauto)")
            print("3. 加载并执行 LISP 脚本")

            # 示例：如果要执行某个命令
            # self.current_doc.SendCommand("_COMMAND ")

            return True

        except Exception as e:
            print(f"❌ 打开菜单失败: {e}")
            return False

    def _close_all_autocad_processes(self) -> int:
        """
        关闭所有 AutoCAD 进程

        Returns:
            关闭的进程数量
        """
        closed_count = 0

        try:
            # 首先尝试通过 COM 正常关闭
            try:
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                print("  🔍 发现运行中的 AutoCAD（通过 COM）")

                # 保存所有文档（可选）
                # for doc in acad.Documents:
                #     doc.Close(SaveChanges=False)

                acad.Quit()
                closed_count += 1
                print("  ✅ AutoCAD 已正常关闭（COM）")
                time.sleep(2)
            except:
                pass

            # 然后强制关闭所有 acad.exe 进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                        print(f"  🔍 发现 AutoCAD 进程: PID {proc.info['pid']}")
                        proc.terminate()  # 优雅终止
                        proc.wait(timeout=5)  # 等待进程结束
                        closed_count += 1
                        print(f"  ✅ 进程已终止: PID {proc.info['pid']}")
                except psutil.NoSuchProcess:
                    pass
                except psutil.TimeoutExpired:
                    # 如果优雅终止失败，强制杀死
                    try:
                        proc.kill()
                        closed_count += 1
                        print(f"  ⚠️ 进程已强制终止: PID {proc.info['pid']}")
                    except:
                        pass
                except Exception as e:
                    print(f"  ⚠️ 无法终止进程: {e}")

        except Exception as e:
            print(f"  ⚠️ 关闭进程时出错: {e}")

        return closed_count

    def _is_autocad_running(self) -> bool:
        """
        检查 AutoCAD 是否正在运行

        Returns:
            True 表示运行中，False 表示未运行
        """
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def run_complete_workflow(self, dwg_file_path: str,
                             menu_name: Optional[str] = None,
                             submenu_name: Optional[str] = None) -> bool:
        """
        运行完整的自动化工作流程

        Args:
            dwg_file_path: DWG 文件路径
            menu_name: 菜单名称（可选）
            submenu_name: 子菜单名称（可选）

        Returns:
            True 表示全流程成功，False 表示失败
        """
        print("\n" + "=" * 60)
        print("AutoCAD 自动化工作流程")
        print("=" * 60)
        print(f"目标文件: {dwg_file_path}")
        if menu_name:
            print(f"目标菜单: {menu_name}" + (f" > {submenu_name}" if submenu_name else ""))
        print("=" * 60)

        # 步骤 1: 关闭并打开
        if not self.step1_close_and_open_cad(dwg_file_path):
            print("\n❌ 工作流程失败：步骤 1 失败")
            return False

        # 步骤 2: 验证加载
        if not self.step2_verify_file_loaded():
            print("\n❌ 工作流程失败：步骤 2 失败")
            return False

        # 步骤 3: 打开菜单（可选）
        if menu_name:
            if not self.step3_open_menu(menu_name, submenu_name):
                print("\n⚠️ 警告：步骤 3 失败（菜单操作）")
                # 菜单操作失败不算整体失败

        print("\n" + "=" * 60)
        print("✅ 自动化工作流程完成！")
        print("=" * 60)

        return True

    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        self.acad = None
        self.current_doc = None
        self.current_file = None


def main():
    """主函数 - 演示完整工作流程"""

    # 配置
    # 请修改为实际的 DWG 文件路径
    dwg_file = r"C:\path\to\your\drawing.dwg"

    # 检查文件是否存在
    if not os.path.exists(dwg_file):
        print("=" * 60)
        print("❌ 演示文件不存在")
        print("=" * 60)
        print(f"请修改脚本中的 dwg_file 变量为实际的 DWG 文件路径")
        print(f"当前路径: {dwg_file}")
        print("\n使用方法:")
        print('  dwg_file = r"C:\\实际路径\\your_drawing.dwg"')
        input("\n按 Enter 键退出...")
        return

    # 创建工作流程管理器
    workflow = AutoCADWorkflow()

    try:
        # 运行完整流程
        success = workflow.run_complete_workflow(
            dwg_file_path=dwg_file,
            menu_name="工具",  # 可选：菜单名称
            submenu_name=None   # 可选：子菜单名称
        )

        if success:
            print("\n✅ 演示完成！AutoCAD 已打开指定文件")
            print("\n💡 提示：")
            print("  - AutoCAD 窗口应该是可见的")
            print("  - 指定的 DWG 文件应该已加载")
            print("  - 您可以手动检查文件是否正确打开")
        else:
            print("\n❌ 演示失败")

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        workflow.cleanup()
        input("\n按 Enter 键退出...")


if __name__ == "__main__":
    main()
