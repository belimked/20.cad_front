"""
DWG任务步骤日志数据模型

这个SB模型记录任务的每一个步骤，艹！
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, JSON
from datetime import datetime

try:
    from src.utils.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class DWGTaskStep(Base):
    """任务步骤日志模型"""

    __tablename__ = 'dwg_task_steps'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    task_id = Column(String(64), ForeignKey('dwg_process_tasks.task_id', ondelete='CASCADE'),
                     nullable=False, index=True, comment='关联任务ID')
    step_name = Column(String(128), nullable=False, comment='步骤名称')
    step_order = Column(Integer, nullable=False, index=True, comment='步骤顺序')

    status = Column(String(32), nullable=False, index=True,
                    comment='状态: running/completed/failed')
    message = Column(Text, comment='步骤消息')
    error_message = Column(Text, comment='错误信息')
    step_metadata = Column(JSON, comment='步骤元数据（JSON格式）')

    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')
    duration_seconds = Column(DECIMAL(10, 3), comment='执行时长（秒）')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    def __repr__(self):
        return f"<DWGTaskStep(task_id='{self.task_id}', step='{self.step_name}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'step_name': self.step_name,
            'step_order': self.step_order,
            'status': self.status,
            'message': self.message,
            'error_message': self.error_message,
            'step_metadata': self.step_metadata,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': float(self.duration_seconds) if self.duration_seconds else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
