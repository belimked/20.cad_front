"""
建议引擎

基于失败分析和质量指标生成改进建议
"""

import logging
from typing import Dict, List, Any
from collections import Counter

from src.entity.evaluation.failure_pattern import FailureAnalysis, FailureType
from src.entity.evaluation.quality_metrics import QualityMetrics
from src.entity.evaluation.analysis_result import Recommendation


class RecommendationEngine:
    """建议引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化建议引擎
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.recommendation_config = config.get('recommendation', {})
        self.knowledge_base = self.recommendation_config.get('knowledge_base', {})
        self.logger = logging.getLogger(__name__)
    
    def generate_recommendations(self, 
                               failure_analysis: FailureAnalysis,
                               quality_metrics: QualityMetrics) -> List[Recommendation]:
        """
        生成改进建议
        
        Args:
            failure_analysis: 失败分析结果
            quality_metrics: 质量指标
            
        Returns:
            改进建议列表
        """
        self.logger.info("开始生成改进建议")
        
        recommendations = []
        
        # 基于失败模式的建议
        failure_recommendations = self._generate_failure_based_recommendations(failure_analysis)
        recommendations.extend(failure_recommendations)
        
        # 基于质量指标的建议
        quality_recommendations = self._generate_quality_based_recommendations(quality_metrics)
        recommendations.extend(quality_recommendations)
        
        # 基于性能的建议
        performance_recommendations = self._generate_performance_based_recommendations(quality_metrics)
        recommendations.extend(performance_recommendations)
        
        # 去重和优先级排序
        recommendations = self._deduplicate_and_prioritize(recommendations)
        
        # 限制建议数量
        max_recommendations = self.recommendation_config.get('generation', {}).get('max_recommendations', 10)
        recommendations = recommendations[:max_recommendations]
        
        self.logger.info(f"生成了 {len(recommendations)} 条改进建议")
        return recommendations
    
    def _generate_failure_based_recommendations(self, failure_analysis: FailureAnalysis) -> List[Recommendation]:
        """基于失败模式生成建议"""
        recommendations = []
        
        # 针对主要失败模式生成建议
        top_patterns = failure_analysis.get_top_failure_patterns(3)
        
        for pattern in top_patterns:
            # 从知识库获取对应的建议
            pattern_recommendations = self._get_knowledge_base_recommendations(pattern.pattern_type)
            
            # 添加基于失败模式的具体建议
            for kb_rec in pattern_recommendations:
                recommendation = Recommendation(
                    priority=kb_rec.get('priority', 'medium'),
                    category=kb_rec.get('category', '质量改进'),
                    title=kb_rec.get('title', ''),
                    description=self._customize_description(kb_rec.get('description', ''), pattern),
                    expected_impact=kb_rec.get('expected_impact', ''),
                    implementation_effort=kb_rec.get('implementation_effort', 'medium')
                )
                recommendations.append(recommendation)
            
            # 如果是严重级别的失败，添加紧急建议
            if pattern.severity.value == 'critical':
                urgent_recommendation = Recommendation(
                    priority='high',
                    category='紧急修复',
                    title=f"紧急处理{pattern.pattern_name}问题",
                    description=f"该问题影响了{pattern.count}个案例（{pattern.percentage:.1f}%），需要立即处理",
                    expected_impact="显著提升系统稳定性和用户体验",
                    implementation_effort='high'
                )
                recommendations.append(urgent_recommendation)
        
        return recommendations
    
    def _generate_quality_based_recommendations(self, quality_metrics: QualityMetrics) -> List[Recommendation]:
        """基于质量指标生成建议"""
        recommendations = []
        
        # 成功率相关建议
        if quality_metrics.success_rate < 0.5:
            recommendations.append(Recommendation(
                priority='high',
                category='质量改进',
                title='提升整体成功率',
                description=f'当前成功率仅为{quality_metrics.success_rate:.1%}，需要全面检查系统配置和数据质量',
                expected_impact='大幅提升系统可用性',
                implementation_effort='high'
            ))
        elif quality_metrics.success_rate < 0.7:
            recommendations.append(Recommendation(
                priority='medium',
                category='质量优化',
                title='优化成功率',
                description=f'当前成功率为{quality_metrics.success_rate:.1%}，还有提升空间',
                expected_impact='提升用户满意度',
                implementation_effort='medium'
            ))
        
        # 分数分布相关建议
        avg_score = quality_metrics.score_distribution.mean
        if avg_score < 70:
            recommendations.append(Recommendation(
                priority='medium',
                category='答案质量',
                title='提升答案准确性',
                description=f'平均分数仅为{avg_score:.1f}分，需要改进答案质量',
                expected_impact='提升答案准确性20-30%',
                implementation_effort='medium'
            ))
        
        # 完美分数率相关建议
        if quality_metrics.perfect_score_rate < 0.1:
            recommendations.append(Recommendation(
                priority='medium',
                category='精确度优化',
                title='提升完美答案比例',
                description=f'完美分数率仅为{quality_metrics.perfect_score_rate:.1%}，需要提升答案精确度',
                expected_impact='显著提升高质量答案比例',
                implementation_effort='medium'
            ))
        
        # JSON有效性相关建议
        if quality_metrics.json_valid_rate < 0.95:
            recommendations.append(Recommendation(
                priority='high',
                category='格式规范',
                title='强化JSON格式验证',
                description=f'JSON有效率为{quality_metrics.json_valid_rate:.1%}，需要改进输出格式控制',
                expected_impact='消除格式错误问题',
                implementation_effort='low'
            ))
        
        return recommendations
    
    def _generate_performance_based_recommendations(self, quality_metrics: QualityMetrics) -> List[Recommendation]:
        """基于性能指标生成建议"""
        recommendations = []
        
        avg_time = quality_metrics.performance_metrics.average_time_per_question
        
        # 处理时间相关建议
        if avg_time > 10:
            recommendations.append(Recommendation(
                priority='medium',
                category='性能优化',
                title='优化处理性能',
                description=f'平均处理时间为{avg_time:.2f}秒，建议优化模型推理速度',
                expected_impact='提升响应速度50%以上',
                implementation_effort='high'
            ))
        elif avg_time > 5:
            recommendations.append(Recommendation(
                priority='low',
                category='性能调优',
                title='进一步优化响应时间',
                description=f'平均处理时间为{avg_time:.2f}秒，可进一步优化',
                expected_impact='提升用户体验',
                implementation_effort='medium'
            ))
        
        # 基于业务对象表现的建议
        underperforming_objects = self._find_underperforming_business_objects(quality_metrics)
        for obj_name in underperforming_objects:
            recommendations.append(Recommendation(
                priority='medium',
                category='业务对象优化',
                title=f'优化{obj_name}业务对象处理',
                description=f'{obj_name}业务对象的表现低于平均水平，需要针对性优化',
                expected_impact='提升特定业务场景的处理效果',
                implementation_effort='medium'
            ))
        
        return recommendations
    
    def _get_knowledge_base_recommendations(self, failure_type: FailureType) -> List[Dict[str, Any]]:
        """从知识库获取建议"""
        failure_type_key = failure_type.value
        return self.knowledge_base.get(failure_type_key, [])
    
    def _customize_description(self, base_description: str, pattern) -> str:
        """定制化建议描述"""
        # 在基础描述中添加具体的失败模式信息
        customized = base_description
        if hasattr(pattern, 'count') and hasattr(pattern, 'percentage'):
            customized += f"（当前该问题影响了{pattern.count}个案例，占{pattern.percentage:.1f}%）"
        return customized
    
    def _find_underperforming_business_objects(self, quality_metrics: QualityMetrics) -> List[str]:
        """找出表现不佳的业务对象"""
        underperforming = []
        
        overall_success_rate = quality_metrics.success_rate
        threshold = overall_success_rate * 0.8  # 低于总体成功率80%的认为表现不佳
        
        for obj_name, metrics in quality_metrics.quality_by_business_object.items():
            if metrics['success_rate'] < threshold:
                underperforming.append(obj_name)
        
        return underperforming
    
    def _deduplicate_and_prioritize(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """去重和优先级排序"""
        # 按标题去重
        unique_recommendations = []
        seen_titles = set()
        
        for rec in recommendations:
            if rec.title not in seen_titles:
                unique_recommendations.append(rec)
                seen_titles.add(rec.title)
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        unique_recommendations.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return unique_recommendations 