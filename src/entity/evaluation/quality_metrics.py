"""
质量指标数据结构

定义评估质量分析的数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class ScoreDistribution:
    """分数分布数据结构"""
    
    score_ranges: Dict[str, int]  # 分数段分布，如 {"90-100": 122, "80-89": 605}
    percentiles: Dict[str, float]  # 百分位数，如 {"p50": 80.0, "p90": 95.0}
    mean: float
    median: float
    std_dev: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'score_ranges': self.score_ranges,
            'percentiles': self.percentiles,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev
        }


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    
    total_processing_time: float
    average_time_per_question: float
    min_processing_time: float
    max_processing_time: float
    
    # 性能分布
    time_percentiles: Dict[str, float]  # 如 {"p50": 4.2, "p90": 5.3}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_processing_time': self.total_processing_time,
            'average_time_per_question': self.average_time_per_question,
            'min_processing_time': self.min_processing_time,
            'max_processing_time': self.max_processing_time,
            'time_percentiles': self.time_percentiles
        }


@dataclass
class QualityInsights:
    """质量洞察数据结构"""
    
    # 高质量特征
    high_quality_patterns: List[str]
    
    # 低质量特征
    low_quality_patterns: List[str]
    
    # 改进建议
    improvement_recommendations: List[str]
    
    # 最佳实践案例
    best_practice_examples: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'high_quality_patterns': self.high_quality_patterns,
            'low_quality_patterns': self.low_quality_patterns,
            'improvement_recommendations': self.improvement_recommendations,
            'best_practice_examples': self.best_practice_examples
        }


@dataclass
class QualityMetrics:
    """质量指标综合数据结构"""
    
    # 基本统计
    total_questions: int
    successful_responses: int
    failed_responses: int
    success_rate: float
    
    # 分数相关指标
    score_distribution: ScoreDistribution
    perfect_score_count: int
    perfect_score_rate: float
    
    # JSON有效性
    json_valid_count: int
    json_valid_rate: float
    
    # 响应长度统计
    average_response_length: float
    min_response_length: int
    max_response_length: int
    
    # 性能指标
    performance_metrics: PerformanceMetrics
    
    # 按业务对象分组的质量指标
    quality_by_business_object: Dict[str, Dict[str, float]]
    
    # 按规则分组的质量指标
    quality_by_rule: Dict[str, Dict[str, float]]
    
    # 质量洞察
    quality_insights: QualityInsights
    
    # 时间序列数据（如果有多个时间点的数据）
    quality_trends: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_questions': self.total_questions,
            'successful_responses': self.successful_responses,
            'failed_responses': self.failed_responses,
            'success_rate': self.success_rate,
            'score_distribution': self.score_distribution.to_dict(),
            'perfect_score_count': self.perfect_score_count,
            'perfect_score_rate': self.perfect_score_rate,
            'json_valid_count': self.json_valid_count,
            'json_valid_rate': self.json_valid_rate,
            'average_response_length': self.average_response_length,
            'min_response_length': self.min_response_length,
            'max_response_length': self.max_response_length,
            'performance_metrics': self.performance_metrics.to_dict(),
            'quality_by_business_object': self.quality_by_business_object,
            'quality_by_rule': self.quality_by_rule,
            'quality_insights': self.quality_insights.to_dict(),
            'quality_trends': self.quality_trends
        }
    
    def get_quality_grade(self) -> str:
        """获取质量等级"""
        if self.success_rate >= 0.9 and self.score_distribution.mean >= 85:
            return "优秀"
        elif self.success_rate >= 0.7 and self.score_distribution.mean >= 70:
            return "良好"
        elif self.success_rate >= 0.5 and self.score_distribution.mean >= 60:
            return "一般"
        else:
            return "需要改进"
    
    def get_top_performing_business_objects(self, limit: int = 3) -> List[str]:
        """获取表现最佳的业务对象"""
        # 按成功率排序
        sorted_objects = sorted(
            self.quality_by_business_object.items(),
            key=lambda x: x[1].get('success_rate', 0),
            reverse=True
        )
        return [obj[0] for obj in sorted_objects[:limit]]
    
    def get_underperforming_rules(self, threshold: float = 0.5) -> List[str]:
        """获取表现不佳的规则"""
        underperforming = []
        for rule_id, metrics in self.quality_by_rule.items():
            if metrics.get('success_rate', 1.0) < threshold:
                underperforming.append(rule_id)
        return underperforming 