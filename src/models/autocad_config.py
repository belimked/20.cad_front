"""
AutoCAD 自动化配置模型

存储 AutoCAD 工作流程的配置参数

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from src.utils.database import Base


class AutoCADConfig(Base):
    """AutoCAD 自动化配置表"""

    __tablename__ = 'autocad_config'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    config_name = Column(String(100), unique=True, nullable=False, comment='配置名称')
    description = Column(String(500), comment='配置描述')

    # CAD 程序配置
    autocad_exe_path = Column(String(500), comment='AutoCAD 可执行文件路径')
    autocad_version = Column(String(50), comment='AutoCAD 版本（如 2014, 2021）')

    # 文件配置
    dwg_file_path = Column(String(1000), comment='DWG 文件路径')
    force_close_existing = Column(Boolean, default=True, comment='是否强制关闭现有 CAD 进程')

    # 延迟配置（秒）
    startup_wait_time = Column(Float, default=10.0, comment='启动等待时间（秒）')
    startup_check_interval = Column(Float, default=1.0, comment='启动检查间隔（秒）')
    post_startup_wait = Column(Float, default=2.0, comment='启动后额外等待时间（秒）')
    file_open_retry_delay = Column(Float, default=3.0, comment='文件打开重试延迟（秒）')
    file_open_max_retries = Column(Integer, default=3, comment='文件打开最大重试次数')
    verification_wait_time = Column(Float, default=30.0, comment='文件验证最大等待时间（秒）')
    verification_check_interval = Column(Float, default=2.0, comment='文件验证检查间隔（秒）')

    # 菜单操作配置
    menu_operations = Column(Text, comment='菜单操作配置（JSON格式）')
    # 格式示例：
    # [
    #   {"type": "command", "command": "ZOOM", "wait_time": 1.0},
    #   {"type": "menu", "path": ["工具", "选项"], "wait_time": 1.5}
    # ]

    # OCR 图像预处理配置（新增）
    ocr_preprocessing_methods = Column(Text, comment='OCR预处理方法列表（JSON格式）')
    # 格式示例：["binary_adaptive", "high_contrast", "denoise_bilateral"]
    # null 或 空数组 = 使用推荐方法

    ocr_preprocessing_params = Column(Text, comment='OCR预处理参数配置（JSON格式）')
    # 格式示例：
    # {
    #   "binary_adaptive_block_size": 11,
    #   "clahe_clip_limit": 3.0,
    #   "canny_threshold1": 50
    # }

    # 状态字段
    is_active = Column(Boolean, default=True, comment='是否激活')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return f"<AutoCADConfig(id={self.id}, name='{self.config_name}')>"

    def to_dict(self):
        """转换为字典"""
        import json

        menu_ops = None
        if self.menu_operations:
            try:
                menu_ops = json.loads(self.menu_operations)
            except:
                menu_ops = []

        # 解析OCR预处理配置
        ocr_methods = None
        if self.ocr_preprocessing_methods:
            try:
                ocr_methods = json.loads(self.ocr_preprocessing_methods)
            except:
                ocr_methods = None

        ocr_params = None
        if self.ocr_preprocessing_params:
            try:
                ocr_params = json.loads(self.ocr_preprocessing_params)
            except:
                ocr_params = {}

        return {
            'id': self.id,
            'config_name': self.config_name,
            'description': self.description,
            'autocad_exe_path': self.autocad_exe_path,
            'autocad_version': self.autocad_version,
            'dwg_file_path': self.dwg_file_path,
            'force_close_existing': self.force_close_existing,
            'timing': {
                'startup_wait_time': self.startup_wait_time,
                'startup_check_interval': self.startup_check_interval,
                'post_startup_wait': self.post_startup_wait,
                'file_open_retry_delay': self.file_open_retry_delay,
                'file_open_max_retries': self.file_open_max_retries,
                'verification_wait_time': self.verification_wait_time,
                'verification_check_interval': self.verification_check_interval,
            },
            'menu_operations': menu_ops,
            'ocr_preprocessing': {
                'methods': ocr_methods,
                'params': ocr_params,
            },
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AutoCADTaskLog(Base):
    """AutoCAD 任务执行日志表"""

    __tablename__ = 'autocad_task_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    config_id = Column(Integer, comment='配置ID（关联 autocad_config.id）')
    task_name = Column(String(200), comment='任务名称')

    # 执行信息
    dwg_file = Column(String(1000), comment='处理的 DWG 文件')
    status = Column(String(50), comment='状态：success, failed, running')
    error_message = Column(Text, comment='错误信息')

    # 时间统计
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    duration_seconds = Column(Float, comment='执行时长（秒）')

    # 详细日志
    execution_log = Column(Text, comment='执行日志（详细）')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<AutoCADTaskLog(id={self.id}, task='{self.task_name}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_id': self.config_id,
            'task_name': self.task_name,
            'dwg_file': self.dwg_file,
            'status': self.status,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'execution_log': self.execution_log,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
