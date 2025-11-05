"""
DWG 识别结果数据模型

存储 MinerU PDF 识别的详细结果

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

from sqlalchemy import Column, Integer, String, Text, BigInteger, Float, DateTime
from sqlalchemy.dialects.mysql import JSON
from datetime import datetime

try:
    from src.utils.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class DWGRecognitionResult(Base):
    """MinerU PDF识别结果表"""

    __tablename__ = 'dwg_recognition_results'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联信息
    task_id = Column(String(64), nullable=False, index=True, comment='关联任务ID')
    pdf_filename = Column(String(255), index=True, comment='PDF文件名')
    pdf_path = Column(String(1000), comment='PDF文件完整路径')

    # 识别内容
    markdown_content = Column(Text, comment='Markdown格式全文内容')
    content_list = Column(JSON, comment='MinerU返回的结构化内容列表')
    table_data = Column(JSON, comment='表格数据（JSON数组）')
    technical_requirements = Column(Text, comment='技术要求文本')

    # 识别状态
    status = Column(String(32), default='pending', index=True, comment='pending/processing/completed/failed')
    error_message = Column(Text, comment='错误信息')

    # 性能指标
    processing_time_seconds = Column(Float, comment='处理耗时（秒）')
    file_size_bytes = Column(BigInteger, comment='文件大小（字节）')
    page_count = Column(Integer, comment='页数')

    # 元数据
    mineru_api_version = Column(String(50), comment='MinerU API 版本')
    parse_method = Column(String(20), comment='使用的解析方法')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<DWGRecognitionResult(id={self.id}, pdf='{self.pdf_filename}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'pdf_filename': self.pdf_filename,
            'pdf_path': self.pdf_path,
            'status': self.status,
            'error_message': self.error_message,
            'processing_time_seconds': self.processing_time_seconds,
            'file_size_bytes': self.file_size_bytes,
            'page_count': self.page_count,
            'mineru_api_version': self.mineru_api_version,
            'parse_method': self.parse_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
