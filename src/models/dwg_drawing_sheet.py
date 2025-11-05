"""
DWG 图纸图号数据模型

用于存储 CAD 图纸的图号信息，关联 DWG 文件和 PDF 文件

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from datetime import datetime

try:
    from src.utils.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class DWGDrawingSheet(Base):
    """DWG图纸图号关联表"""

    __tablename__ = 'dwg_drawing_sheets'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联信息
    task_id = Column(String(64), nullable=False, index=True, comment='关联任务ID')
    dwg_filename = Column(String(255), comment='DWG文件名')
    pdf_filename = Column(String(255), index=True, comment='PDF文件名')
    pdf_path = Column(String(1000), comment='PDF文件完整路径')

    # 图号信息
    sheet_number = Column(String(100), index=True, comment='图号')
    sheet_title = Column(String(255), comment='图纸标题')
    version = Column(String(50), comment='版本号')
    scale = Column(String(50), comment='比例')
    drawing_date = Column(Date, comment='绘图日期')

    # 元数据
    page_number = Column(Integer, comment='页码（如果PDF是多页）')
    recognition_confidence = Column(Float, comment='识别置信度（0-1）')
    extraction_source = Column(String(50), default='mineru', comment='提取来源: mineru/manual/other')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<DWGDrawingSheet(id={self.id}, sheet_number='{self.sheet_number}', pdf='{self.pdf_filename}')>"

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'dwg_filename': self.dwg_filename,
            'pdf_filename': self.pdf_filename,
            'pdf_path': self.pdf_path,
            'sheet_number': self.sheet_number,
            'sheet_title': self.sheet_title,
            'version': self.version,
            'scale': self.scale,
            'drawing_date': self.drawing_date.isoformat() if self.drawing_date else None,
            'page_number': self.page_number,
            'recognition_confidence': self.recognition_confidence,
            'extraction_source': self.extraction_source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
