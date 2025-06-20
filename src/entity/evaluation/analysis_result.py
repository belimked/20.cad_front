"""
分析结果数据结构

定义评估分析的最终结果数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional

from .quality_metrics import QualityMetrics
from .failure_pattern import FailureAnalysis
from .training_guide import TrainingGuide


@dataclass
class EvaluationMetadata:
    """评估元数据"""
    
    file_path: str
    file_size_mb: float
    generation_time: datetime
    source_files: List[str]
    merged_record_count: int
    processing_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'file_path': self.file_path,
            'file_size_mb': self.file_size_mb,
            'generation_time': self.generation_time.isoformat(),
            'source_files': self.source_files,
            'merged_record_count': self.merged_record_count,
            'processing_type': self.processing_type
        }


@dataclass
class Recommendation:
    """改进建议数据结构"""
    
    priority: str  # "high", "medium", "low"
    category: str  # "训练数据", "模型配置", "评估流程"
    title: str
    description: str
    expected_impact: str
    implementation_effort: str  # "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'priority': self.priority,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'expected_impact': self.expected_impact,
            'implementation_effort': self.implementation_effort
        }


@dataclass
class AnalysisResult:
    """评估分析结果综合数据结构"""
    
    # 基本信息
    file_path: str
    analysis_timestamp: datetime
    processing_time: float
    
    # 元数据
    metadata: EvaluationMetadata
    
    # 质量指标
    quality_metrics: QualityMetrics
    
    # 失败分析
    failure_analysis: FailureAnalysis
    
    # 改进建议
    recommendations: List[Recommendation]
    
    # 关键洞察
    key_insights: List[str]
    
    # 训练指南（可选）
    training_guide: Optional[TrainingGuide] = None
    
    # 对比基准（可选）
    baseline_comparison: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'file_path': self.file_path,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'processing_time': self.processing_time,
            'metadata': self.metadata.to_dict(),
            'quality_metrics': self.quality_metrics.to_dict(),
            'failure_analysis': self.failure_analysis.to_dict(),
            'recommendations': [rec.to_dict() for rec in self.recommendations],
            'key_insights': self.key_insights,
            'baseline_comparison': self.baseline_comparison
        }
        
        # 如果存在训练指南，添加到结果中
        if self.training_guide:
            result['training_guide'] = self.training_guide.to_dict()
            
        return result
    
    def get_executive_summary(self) -> Dict[str, Any]:
        """生成执行摘要"""
        return {
            'overall_quality_grade': self.quality_metrics.get_quality_grade(),
            'success_rate': self.quality_metrics.success_rate,
            'total_questions': self.quality_metrics.total_questions,
            'average_score': self.quality_metrics.score_distribution.mean,
            'main_failure_reason': self.failure_analysis.most_common_failure,
            'critical_issues_count': len(self.failure_analysis.get_critical_patterns()),
            'high_priority_recommendations': len([r for r in self.recommendations if r.priority == 'high']),
            'top_insights': self.key_insights[:3]
        }
    
    def get_actionable_items(self) -> List[Dict[str, Any]]:
        """获取可执行的改进项目"""
        actionable = []
        
        # 高优先级建议
        for rec in self.recommendations:
            if rec.priority == 'high':
                actionable.append({
                    'type': 'recommendation',
                    'priority': rec.priority,
                    'title': rec.title,
                    'category': rec.category,
                    'effort': rec.implementation_effort
                })
        
        # 严重失败模式
        for pattern in self.failure_analysis.get_critical_patterns():
            actionable.append({
                'type': 'critical_issue',
                'priority': 'high',
                'title': f"解决{pattern.pattern_name}问题",
                'category': '质量改进',
                'description': pattern.description,
                'affected_count': pattern.count
            })
        
        return actionable
    
    def compare_with_baseline(self, baseline: 'AnalysisResult') -> Dict[str, float]:
        """与基准进行对比"""
        comparison = {
            'success_rate_change': self.quality_metrics.success_rate - baseline.quality_metrics.success_rate,
            'score_mean_change': self.quality_metrics.score_distribution.mean - baseline.quality_metrics.score_distribution.mean,
            'perfect_score_rate_change': self.quality_metrics.perfect_score_rate - baseline.quality_metrics.perfect_score_rate,
            'average_time_change': self.quality_metrics.performance_metrics.average_time_per_question - baseline.quality_metrics.performance_metrics.average_time_per_question
        }
        
        # 更新对比基准
        self.baseline_comparison = comparison
        
        return comparison


@dataclass
class BatchAnalysisResult:
    """批量分析结果"""
    
    # 基本信息
    analysis_timestamp: datetime
    total_files_analyzed: int
    total_processing_time: float
    
    # 各个文件的分析结果
    file_results: List[AnalysisResult]
    
    # 合并统计
    aggregated_metrics: QualityMetrics
    aggregated_failure_analysis: FailureAnalysis
    
    # 文件间对比
    file_comparisons: Dict[str, Dict[str, float]]
    
    # 综合建议
    consolidated_recommendations: List[Recommendation]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'total_files_analyzed': self.total_files_analyzed,
            'total_processing_time': self.total_processing_time,
            'file_results': [result.to_dict() for result in self.file_results],
            'aggregated_metrics': self.aggregated_metrics.to_dict(),
            'aggregated_failure_analysis': self.aggregated_failure_analysis.to_dict(),
            'file_comparisons': self.file_comparisons,
            'consolidated_recommendations': [rec.to_dict() for rec in self.consolidated_recommendations]
        }
    
    def get_best_performing_file(self) -> Optional[AnalysisResult]:
        """获取表现最佳的文件"""
        if not self.file_results:
            return None
        
        return max(self.file_results, key=lambda x: x.quality_metrics.success_rate)
    
    def get_trend_analysis(self) -> Dict[str, List[float]]:
        """获取趋势分析"""
        if len(self.file_results) < 2:
            return {}
        
        # 按时间排序
        sorted_results = sorted(self.file_results, key=lambda x: x.metadata.generation_time)
        
        trends = {
            'success_rates': [r.quality_metrics.success_rate for r in sorted_results],
            'average_scores': [r.quality_metrics.score_distribution.mean for r in sorted_results],
            'perfect_score_rates': [r.quality_metrics.perfect_score_rate for r in sorted_results],
            'response_times': [r.quality_metrics.performance_metrics.average_time_per_question for r in sorted_results]
        }
        
        return trends 