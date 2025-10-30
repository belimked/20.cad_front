"""
DWG任务服务

这个SB服务负责管理DWG处理任务的CRUD操作，艹！
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from src.models.dwg_process_task import DWGProcessTask
from src.models.dwg_task_step import DWGTaskStep


class DWGTaskService:
    """DWG任务服务类"""

    def __init__(self, db: Session):
        self.db = db

    def generate_task_id(self) -> str:
        """
        生成唯一任务ID

        格式: task_YYYYmmdd_HHMMSS_随机6位
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = uuid.uuid4().hex[:6]
        return f"task_{timestamp}_{random_suffix}"

    def create_task(
        self,
        dwg_url: str,
        config_name: str = 'default',
        callback_url: Optional[str] = None
    ) -> DWGProcessTask:
        """
        创建新任务

        Args:
            dwg_url: DWG文件下载地址
            config_name: 配置名称
            callback_url: 完成后回调地址

        Returns:
            创建的任务对象
        """
        # 从URL提取文件名
        dwg_filename = dwg_url.split('/')[-1] if '/' in dwg_url else 'unknown.dwg'

        task = DWGProcessTask(
            task_id=self.generate_task_id(),
            dwg_url=dwg_url,
            dwg_filename=dwg_filename,
            status='pending',
            progress=0,
            config_name=config_name,
            callback_url=callback_url,
            callback_status='pending' if callback_url else None
        )

        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def get_task(self, task_id: str) -> Optional[DWGProcessTask]:
        """
        根据task_id获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务对象，如果不存在返回None
        """
        return self.db.query(DWGProcessTask).filter_by(task_id=task_id).first()

    def update_task(
        self,
        task_id: str,
        **kwargs
    ) -> Optional[DWGProcessTask]:
        """
        更新任务

        Args:
            task_id: 任务ID
            **kwargs: 要更新的字段

        Returns:
            更新后的任务对象
        """
        task = self.get_task(task_id)
        if not task:
            return None

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        self.db.commit()
        self.db.refresh(task)

        return task

    def update_task_status(
        self,
        task_id: str,
        status: Optional[str] = None,
        current_step: Optional[str] = None,
        progress: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[DWGProcessTask]:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态（可选，不传则不更新状态）
            current_step: 当前步骤
            progress: 进度百分比
            error_message: 错误信息

        Returns:
            更新后的任务对象
        """
        update_data = {}

        if status is not None:
            update_data['status'] = status

        if current_step is not None:
            update_data['current_step'] = current_step
        if progress is not None:
            update_data['progress'] = progress
        if error_message is not None:
            update_data['error_message'] = error_message

        # 更新时间戳（仅在传递了status参数时）
        if status is not None:
            if status == 'downloading' or status == 'processing':
                task = self.get_task(task_id)
                if task and not task.started_at:
                    update_data['started_at'] = datetime.now()
            elif status in ['completed', 'failed']:
                update_data['completed_at'] = datetime.now()

        return self.update_task(task_id, **update_data)

    def list_tasks(
        self,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[List[DWGProcessTask], int]:
        """
        查询任务列表（分页）

        Args:
            status: 过滤状态
            page: 页码（从1开始）
            size: 每页大小

        Returns:
            (任务列表, 总数)
        """
        query = self.db.query(DWGProcessTask)

        # 状态过滤
        if status:
            query = query.filter_by(status=status)

        # 统计总数
        total = query.count()

        # 分页
        offset = (page - 1) * size
        tasks = query.order_by(desc(DWGProcessTask.created_at))\
                    .offset(offset)\
                    .limit(size)\
                    .all()

        return tasks, total

    # ============================================================================
    # 步骤日志操作
    # ============================================================================

    def add_step_log(
        self,
        task_id: str,
        step_name: str,
        step_order: int,
        status: str = 'running',
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DWGTaskStep:
        """
        添加步骤日志

        Args:
            task_id: 任务ID
            step_name: 步骤名称
            step_order: 步骤顺序
            status: 状态
            message: 消息
            metadata: 元数据

        Returns:
            创建的步骤对象
        """
        step = DWGTaskStep(
            task_id=task_id,
            step_name=step_name,
            step_order=step_order,
            status=status,
            message=message,
            step_metadata=metadata,
            started_at=datetime.now()
        )

        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)

        return step

    def update_step_log(
        self,
        step_id: int,
        status: str,
        message: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[DWGTaskStep]:
        """
        更新步骤日志

        Args:
            step_id: 步骤ID
            status: 状态
            message: 消息
            error_message: 错误信息
            metadata: 元数据

        Returns:
            更新后的步骤对象
        """
        step = self.db.query(DWGTaskStep).filter_by(id=step_id).first()
        if not step:
            return None

        step.status = status
        if message is not None:
            step.message = message
        if error_message is not None:
            step.error_message = error_message
        if metadata is not None:
            step.step_metadata = metadata

        # 完成时更新时间和时长
        if status in ['completed', 'failed']:
            step.completed_at = datetime.now()
            if step.started_at:
                duration = (step.completed_at - step.started_at).total_seconds()
                step.duration_seconds = duration

        self.db.commit()
        self.db.refresh(step)

        return step

    def get_task_steps(self, task_id: str) -> List[DWGTaskStep]:
        """
        获取任务的所有步骤

        Args:
            task_id: 任务ID

        Returns:
            步骤列表
        """
        return self.db.query(DWGTaskStep)\
                    .filter_by(task_id=task_id)\
                    .order_by(DWGTaskStep.step_order)\
                    .all()
