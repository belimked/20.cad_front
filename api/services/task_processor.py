"""
DWG任务处理器

这个SB服务负责处理整个DWG文件的完整流程，艹！
包括：下载文件 → 调用AutoCAD工作流 → 记录日志
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.services.file_downloader import FileDownloader
from src.utils.database import SessionLocal
from src.services.task_service import DWGTaskService
from research.autocad_com_api.configurable_workflow_9 import ConfigurableAutoCADWorkflow


class TaskProcessor:
    """任务处理器"""

    def __init__(self, download_dir: str = "downloads"):
        """
        初始化任务处理器

        Args:
            download_dir: 下载目录
        """
        self.download_dir = Path(download_dir)
        self.downloader = FileDownloader(download_dir=str(self.download_dir))

    async def process_task(self, task_id: str):
        """
        处理任务（完整流程）

        Args:
            task_id: 任务ID
        """
        db = SessionLocal()
        task_service = DWGTaskService(db)

        try:
            # ============================================================================
            # 步骤0: 获取任务信息
            # ============================================================================
            print(f"\n{'=' * 80}")
            print(f"开始处理任务: {task_id}")
            print(f"{'=' * 80}")

            task = task_service.get_task(task_id)
            if not task:
                print(f"❌ 任务不存在: {task_id}")
                return

            # 记录步骤
            step_order = 0

            # ============================================================================
            # 步骤1: 下载文件
            # ============================================================================
            step_order += 1
            print(f"\n▶ 步骤{step_order}: 下载DWG文件")

            step = task_service.add_step_log(
                task_id=task_id,
                step_name="下载DWG文件",
                step_order=step_order,
                status='running',
                message=f"正在从 {task.dwg_url} 下载文件"
            )

            # 更新任务状态
            task_service.update_task_status(
                task_id=task_id,
                status='downloading',
                current_step='下载文件',
                progress=10
            )

            # 进度回调
            def on_download_progress(downloaded: int, total: int):
                if total > 0:
                    percent = int((downloaded / total) * 30) + 10  # 10-40%
                    task_service.update_task_status(
                        task_id=task_id,
                        progress=percent
                    )

            # 执行下载
            success, local_path, error = await self.downloader.download(
                url=task.dwg_url,
                filename=task.dwg_filename,
                progress_callback=on_download_progress
            )

            if not success:
                # 下载失败
                task_service.update_step_log(
                    step_id=step.id,
                    status='failed',
                    error_message=error
                )
                task_service.update_task_status(
                    task_id=task_id,
                    status='failed',
                    error_message=f"下载失败: {error}"
                )
                print(f"❌ 下载失败: {error}")
                return

            # 下载成功
            file_size = Path(local_path).stat().st_size
            task_service.update_step_log(
                step_id=step.id,
                status='completed',
                message=f"文件已保存到: {local_path}",
                metadata={'local_path': local_path, 'file_size': file_size}
            )
            task_service.update_task(
                task_id=task_id,
                local_path=local_path,
                file_size=file_size
            )
            print(f"✅ 下载成功: {local_path}")

            # ============================================================================
            # 步骤2: 执行AutoCAD工作流
            # ============================================================================
            step_order += 1
            print(f"\n▶ 步骤{step_order}: 执行AutoCAD工作流")

            step = task_service.add_step_log(
                task_id=task_id,
                step_name="执行AutoCAD工作流",
                step_order=step_order,
                status='running',
                message="正在启动AutoCAD工作流"
            )

            # 更新任务状态
            task_service.update_task_status(
                task_id=task_id,
                status='processing',
                current_step='执行AutoCAD工作流',
                progress=40
            )

            # 在同步环境中运行AutoCAD工作流
            # 注意：AutoCAD COM API不支持异步，需要在线程池中运行
            workflow_success = await asyncio.to_thread(
                self._run_autocad_workflow,
                local_path,
                task.config_name,
                task_id,
                task_service
            )

            if not workflow_success:
                # 工作流失败
                task_service.update_step_log(
                    step_id=step.id,
                    status='failed',
                    error_message="AutoCAD工作流执行失败"
                )
                task_service.update_task_status(
                    task_id=task_id,
                    status='failed',
                    error_message="AutoCAD工作流执行失败"
                )
                print(f"❌ AutoCAD工作流执行失败")
                return

            # 工作流成功
            task_service.update_step_log(
                step_id=step.id,
                status='completed',
                message="AutoCAD工作流执行完成"
            )
            print(f"✅ AutoCAD工作流执行完成")

            # ============================================================================
            # 步骤3: 完成任务
            # ============================================================================
            step_order += 1
            print(f"\n▶ 步骤{step_order}: 任务完成")

            task_service.add_step_log(
                task_id=task_id,
                step_name="任务完成",
                step_order=step_order,
                status='completed',
                message="所有步骤执行完成"
            )

            # 更新任务状态
            task_service.update_task_status(
                task_id=task_id,
                status='completed',
                current_step='已完成',
                progress=100
            )

            print(f"\n{'=' * 80}")
            print(f"✅ 任务处理完成: {task_id}")
            print(f"{'=' * 80}")

        except Exception as e:
            print(f"\n❌ 任务处理异常: {e}")
            import traceback
            traceback.print_exc()

            # 更新任务状态为失败
            task_service.update_task_status(
                task_id=task_id,
                status='failed',
                error_message=f"处理异常: {str(e)}"
            )

        finally:
            db.close()

    def _run_autocad_workflow(
        self,
        dwg_file_path: str,
        config_name: str,
        task_id: str,
        task_service: DWGTaskService
    ) -> bool:
        """
        运行AutoCAD工作流（同步）

        Args:
            dwg_file_path: DWG文件路径
            config_name: 配置名称
            task_id: 任务ID
            task_service: 任务服务

        Returns:
            是否成功
        """
        try:
            # 创建工作流实例
            workflow = ConfigurableAutoCADWorkflow(config_name=config_name)

            # 更新进度：50%（开始执行）
            task_service.update_task_status(
                task_id=task_id,
                progress=50
            )

            # 运行工作流
            success = workflow.run(dwg_file_path=dwg_file_path)

            # 更新进度：90%（执行完成）
            task_service.update_task_status(
                task_id=task_id,
                progress=90
            )

            # 保存AutoCAD任务日志ID
            if workflow.task_log_id:
                task_service.update_task(
                    task_id=task_id,
                    autocad_task_log_id=workflow.task_log_id
                )

            return success

        except Exception as e:
            print(f"AutoCAD工作流异常: {e}")
            import traceback
            traceback.print_exc()
            return False


# ============================================================================
# 测试代码
# ============================================================================

async def test_processor():
    """测试任务处理器"""
    # 创建测试任务
    db = SessionLocal()
    task_service = DWGTaskService(db)

    task = task_service.create_task(
        dwg_url="https://example.com/test.dwg",
        config_name="default"
    )

    print(f"创建测试任务: {task.task_id}")

    db.close()

    # 处理任务
    processor = TaskProcessor()
    await processor.process_task(task.task_id)


if __name__ == "__main__":
    asyncio.run(test_processor())
