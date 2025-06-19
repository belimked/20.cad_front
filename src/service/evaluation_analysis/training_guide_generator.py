#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练指南生成器

根据评估结果生成训练指南，包括:
1. 分析每个业务对象的失败类型
2. 按rule_id汇总问题数据
3. 判断是应该训练还是改进提示词
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter

from src.entity.evaluation.analysis_result import AnalysisResult
from src.entity.evaluation.training_guide import (
    TrainingGuide,
    BusinessObjectTrainingGuide,
    TrainingRecommendation,
    RecommendationType,
    Priority
)


class TrainingGuideGenerator:
    """训练指南生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化训练指南生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.training_config = config.get('training_guide', {})
        # 失败次数阈值，超过此值建议训练
        self.failure_threshold = self.training_config.get('failure_threshold', 5)
        # 相似度阈值，低于此值建议训练，高于此值建议改进提示词
        self.similarity_threshold = self.training_config.get('similarity_threshold', 0.7)
        # 示例数量
        self.max_examples = self.training_config.get('max_examples', 3)
        self.logger = logging.getLogger(__name__)
    
    def generate_training_guide(self, analysis_result: AnalysisResult, evaluation_records: List[Any]) -> TrainingGuide:
        """
        生成训练指南
        
        Args:
            analysis_result: 分析结果
            evaluation_records: 评估记录列表
            
        Returns:
            训练指南对象
        """
        self.logger.info("开始生成训练指南")
        
        # 创建训练指南基本结构
        guide = TrainingGuide(
            total_records=len(evaluation_records),
            total_failures=len([r for r in evaluation_records if r.status == 'failed']),
            overall_failure_percentage=analysis_result.quality_metrics.failure_rate * 100
        )
        
        # 按业务对象分析
        business_object_guides = self._analyze_business_objects(evaluation_records)
        guide.business_object_guides = business_object_guides
        
        # 生成总体摘要
        guide.summary = self._generate_summary(guide)
        
        self.logger.info(f"训练指南生成完成，包含{len(guide.business_object_guides)}个业务对象的分析")
        return guide
    
    def _analyze_business_objects(self, evaluation_records: List[Any]) -> Dict[str, BusinessObjectTrainingGuide]:
        """
        分析每个业务对象的情况
        
        Args:
            evaluation_records: 评估记录列表
            
        Returns:
            按业务对象分类的训练指南字典
        """
        # 按业务对象分组
        business_objects = defaultdict(list)
        for record in evaluation_records:
            business_objects[record.business_object].append(record)
        
        business_object_guides = {}
        
        # 分析每个业务对象
        for bo_name, bo_records in business_objects.items():
            failed_records = [r for r in bo_records if r.status == 'failed']
            
            # 创建业务对象指南
            bo_guide = BusinessObjectTrainingGuide(
                business_object=bo_name,
                total_records=len(bo_records),
                failure_count=len(failed_records),
                failure_percentage=len(failed_records) / len(bo_records) * 100 if bo_records else 0
            )
            
            # 分析规则失败情况
            rule_recommendations = self._analyze_rule_failures(bo_name, bo_records, failed_records)
            bo_guide.recommendations = rule_recommendations
            
            business_object_guides[bo_name] = bo_guide
        
        return business_object_guides
    
    def _analyze_rule_failures(self, business_object: str, bo_records: List[Any], 
                              failed_records: List[Any]) -> List[TrainingRecommendation]:
        """
        分析规则失败情况
        
        Args:
            business_object: 业务对象名称
            bo_records: 该业务对象的所有记录
            failed_records: 该业务对象的失败记录
            
        Returns:
            训练建议列表
        """
        recommendations = []
        
        # 按规则ID分组
        rule_failures = defaultdict(list)
        for record in failed_records:
            if hasattr(record, 'rule_id') and record.rule_id:
                rule_failures[record.rule_id].append(record)
        
        # 分析每个规则
        for rule_id, rule_failed_records in rule_failures.items():
            # 计算该规则的失败记录占该规则总记录的百分比
            rule_total_records = [r for r in bo_records if hasattr(r, 'rule_id') and r.rule_id == rule_id]
            failure_percentage = len(rule_failed_records) / len(rule_total_records) * 100 if rule_total_records else 0
            
            # 收集失败类型
            failure_types = []
            for record in rule_failed_records:
                if (hasattr(record, 'evaluation') and record.evaluation and 
                    hasattr(record.evaluation, 'failure_reason') and record.evaluation.failure_reason):
                    failure_types.append(record.evaluation.failure_reason)
            
            # 统计最常见的失败类型
            failure_type_counter = Counter(failure_types)
            most_common_failures = [f[0] for f in failure_type_counter.most_common(3)]
            
            # 计算平均相似度分数
            similarity_scores = []
            for record in rule_failed_records:
                if (hasattr(record, 'evaluation') and record.evaluation and 
                    hasattr(record.evaluation, 'similarity_score')):
                    similarity_scores.append(record.evaluation.similarity_score)
            
            avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
            
            # 确定建议类型
            rec_type, description = self._determine_recommendation_type(
                len(rule_failed_records), 
                avg_similarity,
                most_common_failures
            )
            
            # 为高失败率设置高优先级
            priority = Priority.HIGH if failure_percentage > 50 else (
                Priority.MEDIUM if failure_percentage > 20 else Priority.LOW
            )
            
            # 选择代表性示例
            examples = []
            for record in rule_failed_records[:self.max_examples]:
                example = {
                    'id': record.id,
                    'question': record.question,
                    'expected_answer': record.expected_answer,
                    'actual_answer': record.actual_answer,
                    'failure_reason': record.evaluation.failure_reason if (hasattr(record, 'evaluation') and 
                                                                        record.evaluation and 
                                                                        hasattr(record.evaluation, 'failure_reason')) else "未知",
                    'similarity_score': record.evaluation.similarity_score if (hasattr(record, 'evaluation') and 
                                                                           record.evaluation and 
                                                                           hasattr(record.evaluation, 'similarity_score')) else 0
                }
                examples.append(example)
            
            # 创建建议
            recommendation = TrainingRecommendation(
                rule_id=rule_id,
                business_object=business_object,
                failure_count=len(rule_failed_records),
                failure_percentage=failure_percentage,
                failure_types=most_common_failures,
                similarity_score=avg_similarity,
                recommendation_type=rec_type,
                description=description,
                priority=priority,
                examples=examples
            )
            
            recommendations.append(recommendation)
        
        # 按失败次数排序
        recommendations.sort(key=lambda x: x.failure_count, reverse=True)
        
        return recommendations
    
    def _determine_recommendation_type(self, 
                                     failure_count: int, 
                                     similarity_score: float,
                                     failure_types: List[str]) -> Tuple[RecommendationType, str]:
        """
        根据失败次数和相似度决定建议类型
        
        Args:
            failure_count: 失败次数
            similarity_score: 相似度分数
            failure_types: 失败类型列表
            
        Returns:
            建议类型和描述
        """
        # 检查失败类型中是否包含结构性问题
        has_structural_issue = any(("结构" in ft or "格式" in ft or "JSON" in ft) for ft in failure_types)
        
        # 决定建议类型
        if failure_count < self.failure_threshold:
            # 失败次数少，可能是个例
            return RecommendationType.PROMPT, f"失败次数较少({failure_count}次)，建议检查提示词完善度"
        
        if has_structural_issue:
            # 存在结构性问题，优先考虑改进提示词
            return RecommendationType.PROMPT, f"存在结构或格式问题，建议优化提示词以明确输出格式要求"
        
        if similarity_score < self.similarity_threshold:
            # 相似度低，需要训练
            return RecommendationType.TRAINING, f"相似度较低({similarity_score:.2f})，建议增加此类场景的训练样本"
        else:
            # 相似度高但仍然失败，考虑改进提示词
            return RecommendationType.PROMPT, f"相似度较高({similarity_score:.2f})但仍然失败，建议优化提示词"
    
    def _generate_summary(self, guide: TrainingGuide) -> str:
        """
        生成总体摘要
        
        Args:
            guide: 训练指南
            
        Returns:
            摘要文本
        """
        # 获取所有建议
        all_recommendations = guide.get_all_recommendations()
        
        # 统计不同类型的建议
        training_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.TRAINING])
        prompt_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.PROMPT])
        both_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.BOTH])
        
        # 获取高优先级建议
        high_priority = guide.get_high_priority_recommendations()
        
        # 获取失败率最高的业务对象
        worst_bo = None
        worst_rate = 0
        for bo_name, bo_guide in guide.business_object_guides.items():
            if bo_guide.failure_percentage > worst_rate:
                worst_rate = bo_guide.failure_percentage
                worst_bo = bo_name
        
        # 生成摘要
        summary = f"评估分析发现共有{guide.total_failures}个失败案例(占比{guide.overall_failure_percentage:.1f}%)。"
        summary += f"分析生成了{len(all_recommendations)}条训练建议，其中需要训练的有{training_count}条，"
        summary += f"需要改进提示词的有{prompt_count}条，两者都需要的有{both_count}条。"
        
        if high_priority:
            summary += f"有{len(high_priority)}条高优先级建议需要立即处理。"
        
        if worst_bo:
            summary += f"'{worst_bo}'业务对象的失败率最高，达到{worst_rate:.1f}%，需要重点关注。"
        
        return summary 