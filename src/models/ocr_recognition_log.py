"""
OCR识别日志模型

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DECIMAL, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.utils.database import Base


class OCRRecognitionLog(Base):
    """OCR识别日志表"""

    __tablename__ = 'ocr_recognition_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联信息
    config_id = Column(Integer, nullable=True, comment='关联的配置ID')
    task_log_id = Column(BigInteger, nullable=True, comment='关联的任务日志ID')

    # 识别信息
    target_text = Column(String(100), nullable=False, comment='目标文本')
    found = Column(Boolean, nullable=False, default=False, comment='是否找到目标文本')
    matched_text = Column(String(200), nullable=True, comment='匹配到的文本')
    confidence = Column(DECIMAL(5, 4), nullable=True, comment='置信度 (0-1)')
    matched_version = Column(String(50), nullable=True, comment='匹配到的预处理版本')
    position_x = Column(Integer, nullable=True, comment='位置X坐标')
    position_y = Column(Integer, nullable=True, comment='位置Y坐标')

    # 时间统计
    total_time = Column(DECIMAL(10, 3), nullable=False, comment='总耗时(秒)')
    screenshot_time = Column(DECIMAL(10, 3), nullable=True, comment='截图耗时(秒)')
    preprocessing_time = Column(DECIMAL(10, 3), nullable=True, comment='预处理总耗时(秒)')
    ocr_time = Column(DECIMAL(10, 3), nullable=True, comment='OCR识别总耗时(秒)')
    merge_time = Column(DECIMAL(10, 3), nullable=True, comment='结果合并耗时(秒)')

    # 预处理统计
    preprocessing_methods = Column(Text, nullable=True, comment='使用的预处理方法(JSON数组)')
    preprocessing_count = Column(Integer, default=0, comment='预处理图像数量')

    # 识别统计
    ocr_results_summary = Column(Text, nullable=True, comment='OCR识别结果汇总(JSON)')
    total_texts_found = Column(Integer, default=0, comment='总共识别到的文本数量')
    unique_texts_count = Column(Integer, default=0, comment='去重后的唯一文本数量')

    # 文件信息
    screenshot_dir = Column(String(500), nullable=True, comment='截图保存目录')
    screenshots_saved = Column(Integer, default=0, comment='保存的截图数量')

    # 元数据
    status = Column(String(20), nullable=False, default='success', comment='状态: success/failed/partial')
    error_message = Column(Text, nullable=True, comment='错误信息')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')

    # 关系
    preprocessing_performances = relationship("OCRPreprocessingPerformance", back_populates="recognition_log", cascade="all, delete-orphan")


class OCRPreprocessingPerformance(Base):
    """预处理方法性能日志表"""

    __tablename__ = 'ocr_preprocessing_performance'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    recognition_log_id = Column(BigInteger, ForeignKey('ocr_recognition_logs.id', ondelete='CASCADE'), nullable=False, comment='关联的识别日志ID')

    # 方法信息
    method_name = Column(String(50), nullable=False, comment='预处理方法名称')
    method_order = Column(Integer, nullable=False, comment='执行顺序')

    # 性能指标
    processing_time = Column(DECIMAL(10, 3), nullable=False, comment='预处理耗时(秒)')
    ocr_time = Column(DECIMAL(10, 3), nullable=False, comment='OCR识别耗时(秒)')
    total_time = Column(DECIMAL(10, 3), nullable=False, comment='总耗时(秒)')

    # 识别结果
    texts_found = Column(Integer, default=0, comment='识别到的文本数量')
    target_found = Column(Boolean, default=False, comment='是否找到目标文本')
    max_confidence = Column(DECIMAL(5, 4), nullable=True, comment='最高置信度')
    avg_confidence = Column(DECIMAL(5, 4), nullable=True, comment='平均置信度')

    # 文件信息
    image_path = Column(String(500), nullable=True, comment='预处理图像路径')
    image_size_kb = Column(Integer, nullable=True, comment='图像大小(KB)')

    # 元数据
    created_at = Column(DateTime, default=func.now(), comment='创建时间')

    # 关系
    recognition_log = relationship("OCRRecognitionLog", back_populates="preprocessing_performances")
