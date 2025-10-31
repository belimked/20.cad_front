"""
AutoCAD Batch Plot (bplot) 自动化研究

研究目标：
1. 打开CAD文件
2. 验证加载完成
3. 执行 bplot 命令
4. （可选）自动化对话框操作

Author: CAD Auto Processor Team
Date: 2025-10-31
"""

import win32com.client
import pywintypes
import psutil
import time
import subprocess
from pathlib import Path
from typing import Optional


class BplotWorkflow:
    """bplot命令自动化工作流"""

    def __init__(self):
        self.acad = None
        self.current_doc = None
        self.current_file = None

    def run(self, dwg_file_path: str) -> bool:
        """
        运行bplot工作流

        Args:
            dwg_file_path: DWG文件路径

        Returns:
            True 表示成功，False 表示失败
        """
        print("\n" + "=" * 80)
        print("AutoCAD Batch Plot 自动化研究")
        print("=" * 80)
        print(f"文件: {dwg_file_path}")
        print("=" * 80)

        try:
            # 步骤 1: 打开CAD和文件
            if not self.step1_open_cad_file(dwg_file_path):
                return False

            # 步骤 2: 验证文件加载
            if not self.step2_verify_loaded():
                return False

            # 步骤 3: 执行 bplot 命令
            if not self.step3_execute_bplot():
                return False

            print("\n✅ bplot命令已执行！")
            print("   请在AutoCAD窗口中查看批量打印对话框")
            print("   （后续操作需手动完成，或继续研究自动化方案）")

            return True

        except Exception as e:
            print(f"\n❌ 流程失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def step1_open_cad_file(self, dwg_file_path: str) -> bool:
        """步骤 1: 打开CAD和文件"""
        print("\n" + "▶" * 40)
        print("步骤 1: 打开CAD和文件")
        print("▶" * 40)

        # 验证文件
        dwg_path = Path(dwg_file_path)
        if not dwg_path.exists():
            print(f"❌ 文件不存在: {dwg_file_path}")
            return False

        self.current_file = str(dwg_path.absolute())
        print(f"📄 文件: {self.current_file}")

        # 关闭现有进程
        print("\n🔍 检查现有 AutoCAD 进程...")
        if self._is_autocad_running():
            closed_count = self._close_all_autocad_processes()
            print(f"✅ 已关闭 {closed_count} 个进程")
        else:
            print("  ✅ 没有运行中的AutoCAD进程")

        # 启动 AutoCAD 并打开文件
        print(f"\n🚀 启动 AutoCAD...")
        acad_exe = r"C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

        # 检查路径
        if not Path(acad_exe).exists():
            # 尝试其他常见路径
            common_paths = [
                r"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe",
                r"C:\Program Files (x86)\Autodesk\AutoCAD 2014\acad.exe",
            ]
            for path in common_paths:
                if Path(path).exists():
                    acad_exe = path
                    break
            else:
                print(f"❌ 无法找到AutoCAD可执行文件")
                return False

        print(f"  📂 AutoCAD: {acad_exe}")

        # 启动进程
        try:
            process = subprocess.Popen(
                [acad_exe, self.current_file],
                shell=False
            )
            print(f"  ✅ 进程已启动 (PID: {process.pid})")
        except Exception as e:
            print(f"  ❌ 启动失败: {e}")
            return False

        # 初始化COM
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except:
            pass

        # 等待AutoCAD启动并连接COM
        print(f"\n  ⏳ 等待 AutoCAD 启动...")
        wait_time = 30.0  # 最多等待30秒
        check_interval = 2.0
        max_checks = int(wait_time / check_interval)

        for i in range(max_checks):
            try:
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                print(f"  ✅ 已连接到 AutoCAD (用时: {(i + 1) * check_interval:.1f} 秒)")
                print(f"     版本: {self.acad.Name}")
                break
            except Exception as e:
                if i == 0 or i == max_checks - 1:
                    print(f"     等待中... ({(i + 1) * check_interval:.1f}/{wait_time} 秒)")
                time.sleep(check_interval)
        else:
            # 尝试Dispatch方式
            try:
                self.acad = win32com.client.Dispatch("AutoCAD.Application")
                print(f"  ✅ 已通过Dispatch连接")
            except:
                print(f"  ❌ 无法连接到AutoCAD COM")
                return False

        # 额外等待确保文件加载
        print(f"  ⏳ 等待文件加载完成...")
        time.sleep(5)

        # 验证文档打开
        try:
            if self.acad.Documents.Count > 0:
                self.current_doc = self.acad.ActiveDocument
                print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                return True
            else:
                # 尝试打开文件
                print(f"  ⏳ 通过COM打开文件...")
                self.current_doc = self.acad.Documents.Open(self.current_file)
                print(f"  ✅ 文件已打开: {self.current_doc.Name}")
                return True
        except Exception as e:
            print(f"  ❌ 文件打开失败: {e}")
            return False

    def step2_verify_loaded(self) -> bool:
        """步骤 2: 验证文件加载"""
        print("\n" + "▶" * 40)
        print("步骤 2: 验证文件加载")
        print("▶" * 40)

        max_wait = 30  # 最多等待30秒
        check_interval = 2

        for i in range(int(max_wait / check_interval)):
            try:
                # 检查进程
                if not self._is_autocad_running():
                    print("❌ AutoCAD 进程已关闭")
                    return False

                # 检查文档
                doc_name = self.current_doc.Name
                print(f"  ✅ 文档: {doc_name}")

                # 检查模型空间
                entity_count = self.current_doc.ModelSpace.Count
                print(f"  ✅ 模型空间实体数: {entity_count}")

                print("\n✅ 文件验证成功！")
                return True

            except Exception as e:
                print(f"  ⏳ 等待加载... ({(i + 1) * check_interval}/{max_wait} 秒)")
                time.sleep(check_interval)

        print(f"\n❌ 验证超时")
        return False

    def step3_execute_bplot(self) -> bool:
        """步骤 3: 执行 bplot 命令"""
        print("\n" + "▶" * 40)
        print("步骤 3: 执行 bplot 命令")
        print("▶" * 40)

        try:
            # 方式1：使用SendCommand发送命令
            print("  📝 发送命令: BPLOT")
            print("     (._BPLOT + 空格 + 回车)")

            # 发送 bplot 命令
            # 使用 ._ 前缀确保使用英文命令（兼容中文AutoCAD）
            self.current_doc.SendCommand("._BPLOT ")

            # 等待对话框打开
            print("\n  ⏳ 等待批量打印对话框打开...")
            time.sleep(3)

            print("\n  ✅ bplot 命令已发送")
            print("     如果对话框未打开，可能需要:")
            print("     1. 增加等待时间")
            print("     2. 手动激活AutoCAD窗口")
            print("     3. 检查是否有其他对话框阻止")

            # 可选：尝试激活AutoCAD窗口
            try:
                import win32gui
                def find_autocad_window(hwnd, param):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if 'AutoCAD' in title or 'acad' in title.lower():
                            param.append(hwnd)
                    return True

                windows = []
                win32gui.EnumWindows(find_autocad_window, windows)

                if windows:
                    win32gui.SetForegroundWindow(windows[0])
                    print(f"\n  ✅ 已激活AutoCAD窗口")
            except Exception as e:
                print(f"  ⚠️  激活窗口失败: {e}")

            return True

        except Exception as e:
            print(f"  ❌ 执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _is_autocad_running(self) -> bool:
        """检查 AutoCAD 是否运行"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def _close_all_autocad_processes(self) -> int:
        """关闭所有 AutoCAD 进程"""
        closed_count = 0
        try:
            # COM关闭
            try:
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                acad.Quit()
                closed_count += 1
                time.sleep(2)
            except:
                pass

            # 强制终止
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                        closed_count += 1
                except:
                    pass

            # 等待关闭
            time.sleep(2)

        except Exception as e:
            print(f"  ⚠️ 关闭过程出错: {e}")

        return closed_count

    def cleanup(self):
        """清理资源"""
        self.acad = None
        self.current_doc = None


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("AutoCAD Batch Plot (bplot) 自动化研究")
    print("=" * 80)

    # 测试文件路径（修改为你的实际文件）
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    # 创建工作流
    workflow = BplotWorkflow()

    try:
        success = workflow.run(dwg_file_path=dwg_file)

        if success:
            print("\n🎉 成功！")
            print("\n下一步研究方向:")
            print("1. 自动选择布局")
            print("2. 自动设置打印机/绘图仪")
            print("3. 自动设置输出路径")
            print("4. 自动点击'发布'按钮")
        else:
            print("\n❌ 失败")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        workflow.cleanup()
        input("\n按 Enter 键退出...")


if __name__ == "__main__":
    main()
