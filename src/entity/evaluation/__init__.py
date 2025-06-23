"""
评估分析实体模块

包含评估分析相关的数据结构定义
"""

from .evaluation_record import (
    EvaluationRecord, 
    EvaluationDetail, 
    PromptInfo, 
    OriginalData
)
from .analysis_result import AnalysisResult, BatchAnalysisResult, Recommendation
from .failure_pattern import FailurePattern, FailureAnalysis, FailureType, SeverityLevel
from .quality_metrics import QualityMetrics, ScoreDistribution, PerformanceMetrics, QualityInsights
from .training_guide import TrainingGuide, BusinessObjectTrainingGuide, TrainingRecommendation, RecommendationType, Priority

# 元数据类
class EvaluationMetadata:
    def __init__(self, file_path, file_size_mb, generation_time, source_files, merged_record_count, processing_type):
        self.file_path = file_path
        self.file_size_mb = file_size_mb
        self.generation_time = generation_time
        self.source_files = source_files
        self.merged_record_count = merged_record_count
        self.processing_type = processing_type
    
    def to_dict(self):
        """转换为字典"""
        return {
            'file_path': self.file_path,
            'file_size_mb': self.file_size_mb,
            'generation_time': self.generation_time.isoformat() if hasattr(self.generation_time, 'isoformat') else str(self.generation_time),
            'source_files': self.source_files,
            'merged_record_count': self.merged_record_count,
            'processing_type': self.processing_type
        }

__all__ = [
    'EvaluationRecord',
    'EvaluationDetail',
    'PromptInfo',
    'OriginalData',
    'EvaluationMetadata',
    'AnalysisResult',
    'BatchAnalysisResult',
    'Recommendation',
    'FailurePattern',
    'FailureAnalysis',
    'FailureType',
    'SeverityLevel',
    'QualityMetrics',
    'ScoreDistribution',
    'PerformanceMetrics',
    'QualityInsights',
    'TrainingGuide',
    'BusinessObjectTrainingGuide',
    'TrainingRecommendation',
    'RecommendationType',
    'Priority'
] 