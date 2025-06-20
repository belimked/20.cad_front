"""
评估分析实体模块

包含评估数据分析相关的数据结构和模型定义
"""

from .evaluation_record import EvaluationRecord
from .analysis_result import AnalysisResult, BatchAnalysisResult, EvaluationMetadata, Recommendation
from .failure_pattern import FailurePattern, FailureAnalysis
from .quality_metrics import QualityMetrics

__all__ = [
    'EvaluationRecord',
    'AnalysisResult',
    'BatchAnalysisResult', 
    'EvaluationMetadata',
    'Recommendation',
    'FailurePattern',
    'FailureAnalysis',
    'QualityMetrics'
] 