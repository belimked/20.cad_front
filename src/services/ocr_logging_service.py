"""
OCR日志记录服务

负责记录OCR识别的性能数据和结果

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.ocr_recognition_log import OCRRecognitionLog, OCRPreprocessingPerformance


class OCRLoggingService:
    """OCR日志记录服务"""

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def create_recognition_log(
        self,
        config_id: Optional[int] = None,
        task_log_id: Optional[int] = None,
        target_text: str = "",
        found: bool = False,
        matched_text: Optional[str] = None,
        confidence: Optional[float] = None,
        matched_version: Optional[str] = None,
        position_x: Optional[int] = None,
        position_y: Optional[int] = None,
        total_time: float = 0.0,
        screenshot_time: Optional[float] = None,
        preprocessing_time: Optional[float] = None,
        ocr_time: Optional[float] = None,
        merge_time: Optional[float] = None,
        preprocessing_methods: Optional[List[str]] = None,
        preprocessing_count: int = 0,
        ocr_results_summary: Optional[Dict] = None,
        total_texts_found: int = 0,
        unique_texts_count: int = 0,
        screenshot_dir: Optional[str] = None,
        screenshots_saved: int = 0,
        status: str = 'success',
        error_message: Optional[str] = None
    ) -> OCRRecognitionLog:
        """
        创建OCR识别日志记录

        Args:
            config_id: 配置ID
            task_log_id: 任务日志ID
            target_text: 目标文本
            found: 是否找到
            matched_text: 匹配到的文本
            confidence: 置信度
            matched_version: 匹配的预处理版本
            position_x: X坐标
            position_y: Y坐标
            total_time: 总耗时（秒）
            screenshot_time: 截图耗时（秒）
            preprocessing_time: 预处理总耗时（秒）
            ocr_time: OCR总耗时（秒）
            merge_time: 合并耗时（秒）
            preprocessing_methods: 预处理方法列表
            preprocessing_count: 预处理图像数量
            ocr_results_summary: OCR结果汇总
            total_texts_found: 总文本数量
            unique_texts_count: 唯一文本数量
            screenshot_dir: 截图目录
            screenshots_saved: 保存的截图数量
            status: 状态
            error_message: 错误信息

        Returns:
            创建的日志记录
        """
        import json

        log = OCRRecognitionLog(
            config_id=config_id,
            task_log_id=task_log_id,
            target_text=target_text,
            found=found,
            matched_text=matched_text,
            confidence=confidence,
            matched_version=matched_version,
            position_x=position_x,
            position_y=position_y,
            total_time=total_time,
            screenshot_time=screenshot_time,
            preprocessing_time=preprocessing_time,
            ocr_time=ocr_time,
            merge_time=merge_time,
            preprocessing_methods=json.dumps(preprocessing_methods) if preprocessing_methods else None,
            preprocessing_count=preprocessing_count,
            ocr_results_summary=json.dumps(ocr_results_summary) if ocr_results_summary else None,
            total_texts_found=total_texts_found,
            unique_texts_count=unique_texts_count,
            screenshot_dir=screenshot_dir,
            screenshots_saved=screenshots_saved,
            status=status,
            error_message=error_message
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def add_preprocessing_performance(
        self,
        recognition_log_id: int,
        method_name: str,
        method_order: int,
        processing_time: float,
        ocr_time: float,
        total_time: float,
        texts_found: int = 0,
        target_found: bool = False,
        max_confidence: Optional[float] = None,
        avg_confidence: Optional[float] = None,
        image_path: Optional[str] = None,
        image_size_kb: Optional[int] = None
    ) -> OCRPreprocessingPerformance:
        """
        添加预处理方法性能记录

        Args:
            recognition_log_id: 识别日志ID
            method_name: 预处理方法名
            method_order: 执行顺序
            processing_time: 预处理耗时
            ocr_time: OCR耗时
            total_time: 总耗时
            texts_found: 识别到的文本数量
            target_found: 是否找到目标文本
            max_confidence: 最高置信度
            avg_confidence: 平均置信度
            image_path: 图像路径
            image_size_kb: 图像大小（KB）

        Returns:
            创建的性能记录
        """
        performance = OCRPreprocessingPerformance(
            recognition_log_id=recognition_log_id,
            method_name=method_name,
            method_order=method_order,
            processing_time=processing_time,
            ocr_time=ocr_time,
            total_time=total_time,
            texts_found=texts_found,
            target_found=target_found,
            max_confidence=max_confidence,
            avg_confidence=avg_confidence,
            image_path=image_path,
            image_size_kb=image_size_kb
        )

        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)

        return performance

    def get_recognition_logs(
        self,
        config_id: Optional[int] = None,
        task_log_id: Optional[int] = None,
        target_text: Optional[str] = None,
        found: Optional[bool] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[OCRRecognitionLog]:
        """
        查询OCR识别日志

        Args:
            config_id: 配置ID筛选
            task_log_id: 任务日志ID筛选
            target_text: 目标文本筛选
            found: 是否找到筛选
            status: 状态筛选
            limit: 返回数量限制

        Returns:
            日志列表
        """
        query = self.db.query(OCRRecognitionLog)

        if config_id is not None:
            query = query.filter(OCRRecognitionLog.config_id == config_id)

        if task_log_id is not None:
            query = query.filter(OCRRecognitionLog.task_log_id == task_log_id)

        if target_text is not None:
            query = query.filter(OCRRecognitionLog.target_text.like(f'%{target_text}%'))

        if found is not None:
            query = query.filter(OCRRecognitionLog.found == found)

        if status is not None:
            query = query.filter(OCRRecognitionLog.status == status)

        return query.order_by(OCRRecognitionLog.created_at.desc()).limit(limit).all()

    def get_preprocessing_performance(
        self,
        recognition_log_id: int
    ) -> List[OCRPreprocessingPerformance]:
        """
        获取指定识别日志的预处理性能记录

        Args:
            recognition_log_id: 识别日志ID

        Returns:
            性能记录列表
        """
        return self.db.query(OCRPreprocessingPerformance).filter(
            OCRPreprocessingPerformance.recognition_log_id == recognition_log_id
        ).order_by(OCRPreprocessingPerformance.method_order).all()

    def get_method_statistics(
        self,
        method_name: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取指定预处理方法的统计数据

        Args:
            method_name: 预处理方法名
            limit: 统计最近N条记录

        Returns:
            统计信息字典
        """
        records = self.db.query(OCRPreprocessingPerformance).filter(
            OCRPreprocessingPerformance.method_name == method_name
        ).order_by(OCRPreprocessingPerformance.created_at.desc()).limit(limit).all()

        if not records:
            return {
                'method_name': method_name,
                'total_count': 0
            }

        total_count = len(records)
        total_processing_time = sum(r.processing_time for r in records)
        total_ocr_time = sum(r.ocr_time for r in records)
        total_texts_found = sum(r.texts_found for r in records)
        target_found_count = sum(1 for r in records if r.target_found)

        confidences = [r.max_confidence for r in records if r.max_confidence is not None]

        return {
            'method_name': method_name,
            'total_count': total_count,
            'avg_processing_time': total_processing_time / total_count,
            'avg_ocr_time': total_ocr_time / total_count,
            'avg_total_time': (total_processing_time + total_ocr_time) / total_count,
            'avg_texts_found': total_texts_found / total_count,
            'target_found_rate': target_found_count / total_count,
            'avg_max_confidence': sum(confidences) / len(confidences) if confidences else None,
            'min_confidence': min(confidences) if confidences else None,
            'max_confidence': max(confidences) if confidences else None
        }
