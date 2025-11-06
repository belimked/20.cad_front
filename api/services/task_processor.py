"""
DWG任务处理器

这个SB服务负责处理整个DWG文件的完整流程,艹！
包括：下载文件 → 调用AutoCAD工作流 → 记录日志
"""

import sys
import importlib.util
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

# 延迟导入AutoCAD工作流（避免在非Windows环境导入失败）
ConfigurableAutoCADWorkflow = None
BplotWorkflow = None
EnhancedWorkflow = None


def _load_autocad_workflow():
    """延迟加载标准AutoCAD工作流模块"""
    global ConfigurableAutoCADWorkflow
    if ConfigurableAutoCADWorkflow is None:
        # 使用新的文件名（已重命名，不再以数字开头）
        workflow_path = project_root / "research" / "autocad_com_api" / "configurable_workflow.py"
        spec = importlib.util.spec_from_file_location("configurable_workflow", workflow_path)
        workflow_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow_module)
        ConfigurableAutoCADWorkflow = workflow_module.ConfigurableAutoCADWorkflow
    return ConfigurableAutoCADWorkflow


def _load_bplot_workflow():
    """延迟加载增强型工作流模块（支持前置/后置操作）"""
    global EnhancedWorkflow
    if EnhancedWorkflow is None:
        # 使用增强型工作流，支持：
        # - 前置操作（system_command, directory_cleanup）
        # - 主流程操作（command, menu, input, screenshot_extract）
        # - 后置操作（file_monitor, system_command）
        # - 变量系统
        workflow_path = project_root / "research" / "autocad_com_api" / "enhanced_workflow.py"
        spec = importlib.util.spec_from_file_location("enhanced_workflow", workflow_path)
        workflow_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow_module)
        EnhancedWorkflow = workflow_module.EnhancedWorkflow
    return EnhancedWorkflow


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
            workflow_success, output_dir = await asyncio.to_thread(
                self._run_autocad_workflow,
                local_path,
                task.config_name,
                task_id,
                task_service,
                bool(task.use_bplot)  # 传递 use_bplot 标志
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
            # 步骤3: PDF 识别和转换（新增）
            # ============================================================================
            if output_dir:  # 只有当有输出目录时才执行
                step_order += 1
                print(f"\n▶ 步骤{step_order}: PDF 识别和转换")

                step = task_service.add_step_log(
                    task_id=task_id,
                    step_name="PDF 识别和转换",
                    step_order=step_order,
                    status='running',
                    message="正在识别 PDF 文件并提取图号信息"
                )

                # 更新任务状态
                task_service.update_task_status(
                    task_id=task_id,
                    status='processing',
                    current_step='PDF 识别和转换',
                    progress=70
                )

                # 在线程池中运行 PDF 识别（MinerU 服务是同步的）
                pdf_success = await asyncio.to_thread(
                    self._recognize_and_convert_pdfs,
                    output_dir,
                    task.config_name,
                    task_id,
                    task_service
                )

                if not pdf_success:
                    # PDF 识别失败（失败继续策略：记录警告，不中断流程）
                    task_service.update_step_log(
                        step_id=step.id,
                        status='warning',
                        message="PDF 识别失败或跳过，主流程继续"
                    )
                    print(f"⚠️  PDF 识别失败或跳过，主流程继续")
                else:
                    # PDF 识别成功
                    task_service.update_step_log(
                        step_id=step.id,
                        status='completed',
                        message="PDF 识别和转换完成"
                    )
                    print(f"✅ PDF 识别和转换完成")
            else:
                print(f"⚠️  未获取到输出目录，跳过 PDF 识别")

            # ============================================================================
            # 步骤4: 完成任务（原步骤3）
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
        task_service: DWGTaskService,
        use_bplot: bool = False
    ) -> tuple:
        """
        运行AutoCAD工作流（同步）

        Args:
            dwg_file_path: DWG文件路径
            config_name: 配置名称
            task_id: 任务ID
            task_service: 任务服务
            use_bplot: 是否使用bplot工作流

        Returns:
            (success, output_dir): 成功标志和输出目录
        """
        try:
            if use_bplot:
                # 使用增强型工作流（支持前置/后置操作）
                print(f"  🔀 路由到增强型工作流（EnhancedWorkflow）")
                print(f"  📝 使用配置: {config_name}")
                WorkflowClass = _load_bplot_workflow()

                # 增强型工作流：支持完整的前置/主流程/后置操作
                # 新特性：
                # - system_command: 执行系统命令（关闭进程、清理目录等）
                # - directory_cleanup: 目录清理
                # - file_monitor: 文件生成监控
                # - 变量系统: 保存和引用OCR提取的值
                workflow = WorkflowClass(
                    config_name=config_name,  # 使用传入的配置名
                    task_id=task_id,
                    task_service=task_service
                )
            else:
                # 使用标准配置工作流
                print(f"  🔀 路由到标准配置工作流")
                WorkflowClass = _load_autocad_workflow()

                # 创建工作流实例，传递 task_service 和 task_id
                workflow = WorkflowClass(
                    config_name=config_name,
                    task_id=task_id,
                    task_service=task_service
                )

            # 更新进度：55%（开始执行，40-70%区间）
            task_service.update_task_status(
                task_id=task_id,
                progress=55
            )

            # 运行工作流
            success = workflow.run(dwg_file_path=dwg_file_path)

            # 更新进度：70%（CAD执行完成，为PDF识别预留70-90%空间）
            task_service.update_task_status(
                task_id=task_id,
                progress=70
            )

            # 保存AutoCAD任务日志ID（两个工作流都支持）
            if hasattr(workflow, 'task_log_id') and workflow.task_log_id:
                task_service.update_task(
                    task_id=task_id,
                    autocad_task_log_id=workflow.task_log_id
                )

            # 获取输出目录（用于后续PDF识别）
            output_dir = None
            if hasattr(workflow, 'output_dir') and workflow.output_dir:
                # 优先使用 workflow 实例的 output_dir
                output_dir = workflow.output_dir
            elif hasattr(workflow, 'config') and workflow.config:
                # 从配置中获取输出目录（注意字段名是 output_dir_path）
                if hasattr(workflow.config, 'output_dir_path') and workflow.config.output_dir_path:
                    output_dir = workflow.config.output_dir_path
                elif hasattr(workflow.config, 'output_dir') and workflow.config.output_dir:
                    output_dir = workflow.config.output_dir

            return (success, output_dir)

        except Exception as e:
            print(f"AutoCAD工作流异常: {e}")
            import traceback
            traceback.print_exc()
            return (False, None)

    def _recognize_and_convert_pdfs(
        self,
        output_dir: str,
        config_name: str,
        task_id: str,
        task_service: DWGTaskService
    ) -> bool:
        """
        识别和转换 PDF 文件（同步）

        Args:
            output_dir: PDF 输出目录
            config_name: 配置名称
            task_id: 任务ID
            task_service: 任务服务

        Returns:
            是否成功（失败不中断主流程）
        """
        try:
            # 1. 验证输出目录
            if not output_dir:
                print(f"  ⚠️  未指定 PDF 输出目录，跳过识别")
                return False

            output_path = Path(output_dir)
            if not output_path.exists():
                print(f"  ⚠️  输出目录不存在: {output_dir}")
                return False

            # 2. 检查 PDF 文件
            pdf_files = list(output_path.glob('*.pdf'))
            if not pdf_files:
                print(f"  ⚠️  输出目录无 PDF 文件: {output_dir}")
                return False

            print(f"  📋 发现 {len(pdf_files)} 个 PDF 文件")

            # 3. 获取 AutoCAD 配置（包含 MinerU 配置）
            from src.services.autocad_config_service import AutoCADConfigService
            from src.utils.database import SessionLocal

            config_db = SessionLocal()
            try:
                config_service = AutoCADConfigService(config_db)
                autocad_config = config_service.get_config(config_name=config_name)

                if not autocad_config:
                    print(f"  ⚠️  配置不存在: {config_name}")
                    return False
            finally:
                config_db.close()

            # 4. 检查是否启用 PDF 识别
            mineru_enabled = getattr(autocad_config, 'mineru_enabled', True)
            if not mineru_enabled:
                print(f"  ⚠️  MinerU 识别未启用，跳过")
                return False

            # 5. 创建 MinerU 服务并执行识别
            from src.services.mineru_service import MinerUService
            from src.utils.database import SessionLocal

            # 创建独立数据库会话（避免线程冲突）
            mineru_db = SessionLocal()
            try:
                mineru_service = MinerUService(
                    config=autocad_config,
                    task_id=task_id,
                    db_session=mineru_db
                )

                print(f"  🔍 开始 PDF 识别和转换...")

                # 更新进度：75%（识别开始）
                task_service.update_task_status(
                    task_id=task_id,
                    progress=75
                )

                # 批量识别 PDF（包含自动重组织）
                result = mineru_service.batch_recognize_pdfs(
                    pdf_directory=str(output_path),
                    pdf_pattern='*.pdf'
                )

                # 更新进度：90%（识别完成）
                task_service.update_task_status(
                    task_id=task_id,
                    progress=90
                )

                # 6. 输出统计信息
                if result.get('success'):
                    print(f"  ✅ PDF 识别完成:")
                    print(f"     - 总文件数: {result['total_files']}")
                    print(f"     - 成功识别: {result['success_count']}")
                    print(f"     - 失败: {result['failed_count']}")

                    # 重组织统计
                    if 'reorganize_stats' in result:
                        reorg = result['reorganize_stats']
                        print(f"  📁 PDF 文件重组织:")
                        print(f"     - 成功转换: {reorg.get('completed', 0)}")
                        print(f"     - 跳过: {reorg.get('skipped', 0)}")
                        print(f"     - 转换目录: {reorg.get('convert_directory', 'N/A')}")

                    return True
                else:
                    print(f"  ⚠️  PDF 识别失败: {result.get('message', 'Unknown error')}")
                    return False

            finally:
                mineru_db.close()

        except Exception as e:
            print(f"  ⚠️  PDF 识别异常: {e}")
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
