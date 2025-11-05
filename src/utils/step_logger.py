"""
任务步骤日志记录器

使用方法：
    from src.utils.step_logger import StepLogger

    # 初始化
    logger = StepLogger(task_id="task_123", task_service=task_service)

    # 使用上下文管理器记录步骤
    with logger.log_step("打开文件") as step:
        # 执行业务逻辑
        open_file()

        # 可选：添加元数据
        step.add_metadata({"file_path": "/path/to/file.dwg"})

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Dict, Any
import traceback


class StepLogger:
    """
    任务步骤日志记录器

    功能：
    - 自动记录步骤开始/完成时间
    - 自动计算执行时长
    - 自动捕获和记录异常堆栈
    - 支持元数据记录
    """

    def __init__(self, task_id: str, task_service: Any):
        """
        初始化日志记录器

        Args:
            task_id: 任务ID
            task_service: 任务服务实例（提供 add_task_step 和 update_task_step 方法）
        """
        self.task_id = task_id
        self.task_service = task_service
        self._step_counter = 0
        self._current_step_id = None
        self._current_metadata = {}

    def _next_step_order(self) -> int:
        """获取下一个步骤序号"""
        self._step_counter += 1
        return self._step_counter

    @contextmanager
    def log_step(self, step_name: str, initial_metadata: Optional[Dict[str, Any]] = None):
        """
        上下文管理器：自动记录步骤执行

        Args:
            step_name: 步骤名称
            initial_metadata: 初始元数据

        Yields:
            self: 允许在执行过程中添加元数据

        使用示例：
            with logger.log_step("执行命令") as step:
                result = execute_command()
                step.add_metadata({"command": "ZOOM E"})
        """
        step_order = self._next_step_order()
        started_at = datetime.now()
        self._current_metadata = initial_metadata or {}

        # 记录步骤开始
        try:
            step_id = self.task_service.add_task_step(
                task_id=self.task_id,
                step_name=step_name,
                step_order=step_order,
                status='running',
                started_at=started_at,
                step_metadata=self._current_metadata
            )
            self._current_step_id = step_id
        except Exception as e:
            # 记录日志失败不应中断业务逻辑
            print(f"  ⚠️  记录步骤开始失败: {e}")
            step_id = None

        try:
            # 执行业务逻辑
            yield self

            # 记录步骤成功
            if step_id:
                completed_at = datetime.now()
                duration = (completed_at - started_at).total_seconds()

                try:
                    self.task_service.update_task_step(
                        step_id=step_id,
                        status='completed',
                        completed_at=completed_at,
                        duration_seconds=duration,
                        step_metadata=self._current_metadata
                    )
                except Exception as e:
                    print(f"  ⚠️  更新步骤状态失败: {e}")

        except Exception as e:
            # 记录步骤失败（含异常堆栈）
            if step_id:
                completed_at = datetime.now()
                duration = (completed_at - started_at).total_seconds()

                # 获取完整的异常堆栈
                error_message = ''.join(
                    traceback.format_exception(type(e), e, e.__traceback__)
                )

                # 添加异常信息到元数据
                self._current_metadata['exception_type'] = type(e).__name__
                self._current_metadata['exception_message'] = str(e)

                try:
                    self.task_service.update_task_step(
                        step_id=step_id,
                        status='failed',
                        error_message=error_message,
                        completed_at=completed_at,
                        duration_seconds=duration,
                        step_metadata=self._current_metadata
                    )
                except Exception as update_error:
                    print(f"  ⚠️  记录步骤失败信息出错: {update_error}")

            # 继续传播异常
            raise

        finally:
            # 清理当前步骤状态
            self._current_step_id = None
            self._current_metadata = {}

    def add_metadata(self, metadata: Dict[str, Any]):
        """
        添加元数据到当前步骤

        Args:
            metadata: 要添加的元数据字典
        """
        if self._current_step_id:
            self._current_metadata.update(metadata)

    def log_simple_step(self, step_name: str, status: str = 'completed',
                       message: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """
        记录简单步骤（无需上下文管理器）

        用于记录不需要捕获异常的简单步骤

        Args:
            step_name: 步骤名称
            status: 步骤状态（completed/failed）
            message: 步骤消息
            metadata: 元数据
        """
        step_order = self._next_step_order()

        try:
            self.task_service.add_task_step(
                task_id=self.task_id,
                step_name=step_name,
                step_order=step_order,
                status=status,
                message=message,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                duration_seconds=0.0,
                step_metadata=metadata or {}
            )
        except Exception as e:
            print(f"  ⚠️  记录简单步骤失败: {e}")


# 空上下文管理器（当 task_service 为 None 时使用）
class NullStepLogger:
    """空日志记录器（不记录任何内容）"""

    @contextmanager
    def log_step(self, step_name: str, initial_metadata: Optional[Dict[str, Any]] = None):
        """空上下文管理器"""
        yield self

    def add_metadata(self, metadata: Dict[str, Any]):
        """空操作"""
        pass

    def log_simple_step(self, step_name: str, status: str = 'completed',
                       message: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """空操作"""
        pass
