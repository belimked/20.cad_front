"""
AutoCAD 自动化工作流程 - 数据库配置版

支持从数据库读取配置参数

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import win32com.client
import pywintypes
import psutil
import time
from typing import Optional, Dict, Any
import json

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
from src.models.autocad_config import AutoCADConfig


class ConfigurableAutoCADWorkflow:
    """
    基于数据库配置的 AutoCAD 自动化工作流程

    支持从数据库读取所有配置参数
    """

    def __init__(self, config: Optional[AutoCADConfig] = None,
                 config_name: Optional[str] = None,
                 config_id: Optional[int] = None):
        """
        初始化工作流程

        Args:
            config: 配置对象（直接传入）
            config_name: 配置名称（从数据库查询）
            config_id: 配置ID（从数据库查询）
        """
        self.acad = None
        self.current_doc = None
        self.current_file = None
        self.task_log_id = None

        # 加载配置
        if config:
            self.config = config
        else:
            db = SessionLocal()
            try:
                service = AutoCADConfigService(db)
                self.config = service.get_config(config_id=config_id, config_name=config_name)
                if not self.config:
                    raise ValueError(f"Config not found: id={config_id}, name={config_name}")
            finally:
                db.close()

        print(f"✅ 已加载配置: {self.config.config_name}")
        print(f"   描述: {self.config.description}")

    def run(self, dwg_file_path: Optional[str] = None) -> bool:
        """
        运行完整的自动化流程

        Args:
            dwg_file_path: DWG 文件路径（可选，默认使用配置中的路径）

        Returns:
            True 表示成功，False 表示失败
        """
        # 确定文件路径
        file_path = dwg_file_path or self.config.dwg_file_path
        if not file_path:
            print("❌ 错误：未指定 DWG 文件路径")
            return False

        print("\n" + "=" * 80)
        print("AutoCAD 自动化工作流程（数据库配置）")
        print("=" * 80)
        print(f"配置: {self.config.config_name}")
        print(f"文件: {file_path}")
        print("=" * 80)

        # 记录任务开始
        db = SessionLocal()
        try:
            service = AutoCADConfigService(db)
            task_log = service.log_task_start(
                config_id=self.config.id,
                task_name=f"Process {Path(file_path).name}",
                dwg_file=file_path
            )
            self.task_log_id = task_log.id
        except Exception as e:
            print(f"⚠️ 警告：无法记录任务日志: {e}")
        finally:
            db.close()

        try:
            # 步骤 1: 关闭并打开
            if not self.step1_close_and_open_cad(file_path):
                self._log_task_end('failed', '步骤1失败：无法打开CAD和文件')
                return False

            # 步骤 2: 验证加载
            if not self.step2_verify_file_loaded():
                self._log_task_end('failed', '步骤2失败：文件未正确加载')
                return False

            # 步骤 3: 执行菜单操作
            if self.config.menu_operations:
                if not self.step3_execute_operations():
                    print("\n⚠️ 警告：菜单操作失败（但文件已成功打开）")

            print("\n" + "=" * 80)
            print("✅ 自动化流程完成！")
            print("=" * 80)

            self._log_task_end('success')
            return True

        except Exception as e:
            print(f"\n❌ 流程失败: {e}")
            self._log_task_end('failed', str(e))
            return False

    def step1_close_and_open_cad(self, dwg_file_path: str) -> bool:
        """步骤 1: 关闭并打开 CAD"""
        print("\n" + "▶" * 40)
        print("步骤 1: 关闭现有 CAD 并打开指定文件")
        print("▶" * 40)

        # 验证文件
        dwg_path = Path(dwg_file_path)
        if not dwg_path.exists():
            print(f"❌ 文件不存在: {dwg_file_path}")
            return False

        self.current_file = str(dwg_path.absolute())
        print(f"📄 目标文件: {self.current_file}")

        # 关闭现有进程
        if self.config.force_close_existing:
            print("\n🔍 检查现有 AutoCAD 进程...")
            closed_count = self._close_all_autocad_processes()
            if closed_count > 0:
                print(f"✅ 已关闭 {closed_count} 个 AutoCAD 进程")
                print("⏳ 等待 3 秒...")
                time.sleep(3)

        # 启动 AutoCAD
        print(f"\n🚀 启动 AutoCAD...")
        try:
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acad.Visible = True
            print("✅ AutoCAD 已启动")

            # 等待就绪（使用配置的时间）
            print(f"⏳ 等待 AutoCAD 初始化（最多 {self.config.startup_wait_time} 秒）...")
            max_checks = int(self.config.startup_wait_time / self.config.startup_check_interval)

            for i in range(max_checks):
                try:
                    _ = self.acad.Name
                    print(f"  ✅ 已就绪（{(i + 1) * self.config.startup_check_interval:.1f} 秒后）")
                    break
                except:
                    print(f"  ⏳ 等待中... ({(i + 1) * self.config.startup_check_interval:.1f}/{self.config.startup_wait_time} 秒)")
                    time.sleep(self.config.startup_check_interval)

            # 额外等待
            if self.config.post_startup_wait > 0:
                print(f"⏳ 额外等待 {self.config.post_startup_wait} 秒...")
                time.sleep(self.config.post_startup_wait)

            # 打开文件（使用配置的重试参数）
            print(f"\n📂 打开文件...")
            for attempt in range(self.config.file_open_max_retries):
                try:
                    self.current_doc = self.acad.Documents.Open(self.current_file)
                    print(f"✅ 文件已打开: {self.current_doc.Name}")
                    return True
                except Exception as e:
                    if attempt < self.config.file_open_max_retries - 1:
                        print(f"  ⚠️ 尝试 {attempt + 1}/{self.config.file_open_max_retries} 失败: {e}")
                        print(f"  ⏳ 等待 {self.config.file_open_retry_delay} 秒后重试...")
                        time.sleep(self.config.file_open_retry_delay)
                    else:
                        raise e

        except Exception as e:
            print(f"❌ 失败: {e}")
            return False

    def step2_verify_file_loaded(self) -> bool:
        """步骤 2: 验证文件加载"""
        print("\n" + "▶" * 40)
        print("步骤 2: 验证文件已加载")
        print("▶" * 40)

        print(f"⏳ 最大等待: {self.config.verification_wait_time} 秒")
        print(f"🔄 检查间隔: {self.config.verification_check_interval} 秒")

        start_time = time.time()
        check_count = 0

        while time.time() - start_time < self.config.verification_wait_time:
            check_count += 1
            elapsed = time.time() - start_time

            print(f"\n🔍 检查 #{check_count} (已用时: {elapsed:.1f}秒)...")

            try:
                # 检查进程
                if not self._is_autocad_running():
                    print("❌ AutoCAD 进程已关闭")
                    return False
                print("  ✅ AutoCAD 进程运行中")

                # 检查文档
                doc_name = self.current_doc.Name
                print(f"  ✅ 文档打开: {doc_name}")

                # 检查模型空间
                entity_count = self.current_doc.ModelSpace.Count
                print(f"  ✅ 模型空间实体数: {entity_count}")

                print("\n✅ 文件验证成功！")
                return True

            except:
                print(f"  ⏳ 等待中...")
                time.sleep(self.config.verification_check_interval)

        print(f"\n❌ 超时：{self.config.verification_wait_time} 秒内未加载")
        return False

    def step3_execute_operations(self) -> bool:
        """步骤 3: 执行菜单操作"""
        print("\n" + "▶" * 40)
        print("步骤 3: 执行菜单操作")
        print("▶" * 40)

        try:
            operations = json.loads(self.config.menu_operations) if isinstance(
                self.config.menu_operations, str) else self.config.menu_operations

            if not operations:
                print("  （无配置的操作）")
                return True

            for i, op in enumerate(operations, 1):
                print(f"\n📋 操作 {i}/{len(operations)}: {op.get('type')}")

                if op.get('type') == 'command':
                    # 执行AutoCAD命令
                    command = op.get('command', '')
                    self.current_doc.SendCommand(f"._{command} ")
                    print(f"  ✅ 已执行命令: {command}")

                    wait_time = op.get('wait_time', 1.0)
                    time.sleep(wait_time)

                elif op.get('type') == 'menu':
                    # 点击菜单项
                    menu_path = op.get('path', [])
                    if not menu_path:
                        print(f"  ⚠️ 跳过：菜单路径为空")
                        continue

                    # 使用SendKeys模拟菜单操作
                    # 例如：["帮助(H)", "欢迎屏幕(W)"] -> Alt+H, W
                    try:
                        import win32api
                        import win32con

                        # 提取快捷键字母
                        keys = []
                        for menu_item in menu_path:
                            # 提取括号中的快捷键，如 "帮助(H)" -> "H"
                            if '(' in menu_item and ')' in menu_item:
                                shortcut = menu_item[menu_item.rfind('(')+1:menu_item.rfind(')')]
                                keys.append(shortcut)
                            else:
                                # 如果没有括号，尝试用第一个字母
                                keys.append(menu_item[0] if menu_item else '')

                        if keys:
                            # 激活AutoCAD窗口
                            import win32gui
                            hwnd = win32gui.FindWindow(None, None)
                            # 查找AutoCAD窗口
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
                                time.sleep(0.3)

                                # 发送Alt+第一个键打开菜单
                                import win32com.client
                                shell = win32com.client.Dispatch("WScript.Shell")

                                # Alt+第一个键
                                shell.SendKeys(f"%{keys[0]}")
                                time.sleep(0.3)

                                # 后续的键
                                for key in keys[1:]:
                                    shell.SendKeys(key)
                                    time.sleep(0.2)

                                print(f"  ✅ 已点击菜单: {' > '.join(menu_path)}")
                            else:
                                print(f"  ⚠️ 未找到AutoCAD窗口")

                        wait_time = op.get('wait_time', 1.0)
                        time.sleep(wait_time)

                    except Exception as e:
                        print(f"  ❌ 菜单点击失败: {e}")

                else:
                    print(f"  ⚠️ 跳过：未知操作类型 '{op.get('type')}'")

            print("\n✅ 菜单操作完成")
            return True

        except Exception as e:
            print(f"❌ 菜单操作失败: {e}")
            return False

    def _close_all_autocad_processes(self) -> int:
        """关闭所有 AutoCAD 进程"""
        closed_count = 0
        try:
            # COM 关闭
            try:
                acad = win32com.client.GetActiveObject("AutoCAD.Application")
                acad.Quit()
                closed_count += 1
                time.sleep(2)
            except:
                pass

            # 强制关闭
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                        proc.terminate()
                        proc.wait(timeout=5)
                        closed_count += 1
                except:
                    pass
        except:
            pass

        return closed_count

    def _is_autocad_running(self) -> bool:
        """检查 AutoCAD 是否运行"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'acad.exe' in proc.info['name'].lower():
                    return True
            except:
                pass
        return False

    def _log_task_end(self, status: str, error_message: Optional[str] = None):
        """记录任务结束"""
        if not self.task_log_id:
            return

        db = SessionLocal()
        try:
            service = AutoCADConfigService(db)
            service.log_task_end(
                log_id=self.task_log_id,
                status=status,
                error_message=error_message
            )
        except:
            pass
        finally:
            db.close()

    def cleanup(self):
        """清理资源"""
        self.acad = None
        self.current_doc = None


def main():
    """主函数 - 使用数据库配置运行"""

    print("=" * 80)
    print("AutoCAD 自动化工作流程 - 数据库配置版")
    print("=" * 80)

    # 选项 1: 使用默认配置
    workflow = ConfigurableAutoCADWorkflow(config_name='default')

    # 选项 2: 使用指定配置ID
    # workflow = ConfigurableAutoCADWorkflow(config_id=1)

    # 可以覆盖配置中的文件路径
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    try:
        success = workflow.run(dwg_file_path=dwg_file)

        if success:
            print("\n🎉 成功！")
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
