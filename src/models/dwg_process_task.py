"""
DWG处理任务数据模型

这个SB模型用于追踪DWG文件的处理任务，艹！
"""

from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DWGProcessTask(Base):
    """DWG文件处理任务模型"""

    __tablename__ = 'dwg_process_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    task_id = Column(String(64), unique=True, nullable=False, index=True, comment='任务唯一ID')
    dwg_url = Column(Text, nullable=False, comment='DWG文件下载地址')
    dwg_filename = Column(String(255), comment='原始文件名')
    local_path = Column(Text, comment='本地保存路径')
    file_size = Column(BigInteger, comment='文件大小（字节）')

    status = Column(String(32), nullable=False, default='pending', index=True,
                    comment='状态: pending/downloading/processing/completed/failed')
    current_step = Column(String(64), comment='当前步骤')
    progress = Column(Integer, default=0, comment='进度百分比（0-100）')
    error_message = Column(Text, comment='错误信息')

    config_name = Column(String(64), default='default', comment='使用的配置名称')
    config_id = Column(Integer, index=True, comment='配置ID（关联autocad_config表）')
    autocad_task_log_id = Column(Integer, comment='关联的AutoCAD任务日志ID')

    callback_url = Column(Text, comment='完成后回调地址')
    callback_status = Column(String(32), comment='回调状态: pending/success/failed')
    callback_retry_count = Column(Integer, default=0, comment='回调重试次数')

    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<DWGProcessTask(task_id='{self.task_id}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'dwg_url': self.dwg_url,
            'dwg_filename': self.dwg_filename,
            'local_path': self.local_path,
            'file_size': self.file_size,
            'status': self.status,
            'current_step': self.current_step,
            'progress': self.progress,
            'error_message': self.error_message,
            'config_name': self.config_name,
            'config_id': self.config_id,
            'autocad_task_log_id': self.autocad_task_log_id,
            'callback_url': self.callback_url,
            'callback_status': self.callback_status,
            'callback_retry_count': self.callback_retry_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
