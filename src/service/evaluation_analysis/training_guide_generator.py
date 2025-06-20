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
import json
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
        
        # 从配置文件读取训练指南权重设置
        recommendation_config = config.get('recommendation', {})
        training_guide_config = recommendation_config.get('training_guide', {})
        
        # 权重计算配置
        weight_calc_config = training_guide_config.get('weight_calculation', {})
        self.failure_rate_weight = weight_calc_config.get('failure_rate_weight', 0.6)
        self.score_impact_weight = weight_calc_config.get('score_impact_weight', 0.4)
        
        # 权重阈值配置
        weight_thresholds = training_guide_config.get('weight_thresholds', {})
        self.high_priority_threshold = weight_thresholds.get('high_priority', {}).get('min_weighted_score', 70.0)
        self.medium_priority_min = weight_thresholds.get('medium_priority', {}).get('min_weighted_score', 40.0)
        self.medium_priority_max = weight_thresholds.get('medium_priority', {}).get('max_weighted_score', 69.9)
        
        # 建议类型触发条件
        rec_types_config = training_guide_config.get('recommendation_types', {})
        self.training_min_failure_rate = rec_types_config.get('training_focus', {}).get('trigger_conditions', {}).get('min_failure_rate', 30.0)
        self.prompt_max_failure_rate = rec_types_config.get('prompt_optimization', {}).get('trigger_conditions', {}).get('max_failure_rate', 50.0)
        
        # 样例记录配置
        sample_config = training_guide_config.get('sample_records', {})
        self.max_sample_records = sample_config.get('max_records_per_rule', 10)
        self.text_truncate_length = sample_config.get('text_truncate_length', 200)
        
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
        
        try:
            # 记录输入数据基本信息
            self.logger.info(f"分析结果时间戳: {analysis_result.analysis_timestamp}")
            self.logger.info(f"评估记录数量: {len(evaluation_records)}")
            
            # 检查评估记录的基本结构
            if evaluation_records:
                sample_record = evaluation_records[0]
                self.logger.debug(f"样本记录结构: {', '.join(dir(sample_record))}")
                self.logger.debug(f"样本记录ID: {getattr(sample_record, 'id', 'N/A')}")
                self.logger.debug(f"样本记录状态: {getattr(sample_record, 'status', 'N/A')}")
            
            # 创建训练指南基本结构
            failed_records = [r for r in evaluation_records if hasattr(r, 'status') and r.status == 'failed']
            self.logger.info(f"失败记录数量: {len(failed_records)}")
            
            # 计算失败率
            failure_rate = 0
            if hasattr(analysis_result, 'metrics') and analysis_result.metrics:
                # 从metrics字段获取成功率，然后计算失败率
                success_rate = getattr(analysis_result.metrics, 'success_rate', 0)
                failure_rate = (1 - success_rate) * 100
                self.logger.info(f"从分析结果metrics计算的失败率: {failure_rate}% (成功率: {success_rate * 100}%)")
            elif hasattr(analysis_result, 'quality_metrics') and analysis_result.quality_metrics:
                failure_rate = getattr(analysis_result.quality_metrics, 'failure_rate', 0) * 100
                self.logger.info(f"分析结果中的失败率: {failure_rate}%")
            else:
                failure_rate = len(failed_records) / len(evaluation_records) * 100 if evaluation_records else 0
                self.logger.info(f"手动计算的失败率: {failure_rate}%")
            
            guide = TrainingGuide(
                total_records=len(evaluation_records),
                total_failures=len(failed_records),
                overall_failure_percentage=failure_rate
            )
            
            # 按业务对象分析
            self.logger.info("开始按业务对象分析失败记录")
            business_object_guides = self._analyze_business_objects(evaluation_records)
            guide.business_object_guides = business_object_guides
            
            # 记录业务对象分析结果
            for bo, bo_guide in business_object_guides.items():
                self.logger.info(f"业务对象 '{bo}': 总记录 {bo_guide.total_records}, 失败 {bo_guide.failure_count}, "
                               f"失败率 {bo_guide.failure_percentage:.1f}%, 建议数 {len(bo_guide.recommendations)}")
            
            # 生成总体摘要
            self.logger.info("生成训练指南摘要")
            guide.summary = self._generate_summary(guide)
            
            # 验证训练指南是否可以正确序列化为JSON
            self._validate_json_serializable(guide)
            
            self.logger.info(f"训练指南生成完成，包含{len(guide.business_object_guides)}个业务对象的分析")
            return guide
            
        except Exception as e:
            import traceback
            self.logger.error(f"生成训练指南时发生错误: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def _validate_json_serializable(self, guide: TrainingGuide) -> None:
        """
        验证训练指南是否可以正确序列化为JSON
        
        Args:
            guide: 训练指南对象
        
        Raises:
            ValueError: 如果序列化失败
        """
        try:
            # 转换为字典
            guide_dict = guide.to_dict()
            self.logger.debug(f"训练指南字典结构: {list(guide_dict.keys())}")
            
            # 尝试序列化为JSON
            json_str = json.dumps(guide_dict, ensure_ascii=False)
            
            # 尝试反序列化，确保格式正确
            json.loads(json_str)
            
            self.logger.info("训练指南可以正确序列化为JSON")
        except Exception as e:
            self.logger.error(f"训练指南序列化为JSON失败: {str(e)}")
            
            # 尝试逐步序列化各个部分，找出问题所在
            try:
                # 基本属性
                basic_dict = {
                    "total_records": guide.total_records,
                    "total_failures": guide.total_failures,
                    "overall_failure_percentage": guide.overall_failure_percentage,
                    "summary": guide.summary
                }
                json.dumps(basic_dict)
                self.logger.debug("基本属性可以正确序列化")
                
                # 时间戳
                timestamp_dict = {"timestamp": guide.timestamp.isoformat()}
                json.dumps(timestamp_dict)
                self.logger.debug("时间戳可以正确序列化")
                
                # 检查每个业务对象
                for bo, bo_guide in guide.business_object_guides.items():
                    try:
                        bo_dict = bo_guide.to_dict()
                        json.dumps(bo_dict)
                        self.logger.debug(f"业务对象 '{bo}' 可以正确序列化")
                    except Exception as bo_error:
                        self.logger.error(f"业务对象 '{bo}' 序列化失败: {str(bo_error)}")
                        
                        # 检查业务对象的基本属性
                        try:
                            basic_bo_dict = {
                                "business_object": bo_guide.business_object,
                                "total_records": bo_guide.total_records,
                                "failure_count": bo_guide.failure_count,
                                "failure_percentage": bo_guide.failure_percentage
                            }
                            json.dumps(basic_bo_dict)
                            self.logger.debug(f"业务对象 '{bo}' 基本属性可以正确序列化")
                        except Exception as basic_bo_error:
                            self.logger.error(f"业务对象 '{bo}' 基本属性序列化失败: {str(basic_bo_error)}")
                        
                        # 检查每个建议
                        for i, rec in enumerate(bo_guide.recommendations):
                            try:
                                rec_dict = rec.to_dict()
                                json.dumps(rec_dict)
                                self.logger.debug(f"业务对象 '{bo}' 的建议 {i} 可以正确序列化")
                            except Exception as rec_error:
                                self.logger.error(f"业务对象 '{bo}' 的建议 {i} 序列化失败: {str(rec_error)}")
                                
                                # 检查建议的各个字段
                                problem_fields = []
                                for field, value in rec_dict.items():
                                    try:
                                        json.dumps({field: value})
                                    except:
                                        problem_fields.append(f"{field}: {type(value)}")
                                
                                if problem_fields:
                                    self.logger.error(f"问题字段: {', '.join(problem_fields)}")
            
            except Exception as detail_error:
                self.logger.error(f"详细诊断失败: {str(detail_error)}")
            
            raise ValueError(f"训练指南序列化为JSON失败: {str(e)}")
    
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
            # 业务对象名称从original_data中获取
            business_object = getattr(record, 'business_object', None) or \
                            (record.original_data.business_object if hasattr(record, 'original_data') and 
                             hasattr(record.original_data, 'business_object') else 'unknown')
            business_objects[business_object].append(record)
        
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
            # rule_id从original_data中获取
            rule_id = getattr(record, 'rule_id', None) or \
                     (record.original_data.rule_id if hasattr(record, 'original_data') and 
                      hasattr(record.original_data, 'rule_id') else None)
            if rule_id:
                rule_failures[rule_id].append(record)
        
        # 分析每个规则
        for rule_id, rule_failed_records in rule_failures.items():
            # 计算该规则的失败记录占该规则总记录的百分比
            rule_total_records = [r for r in bo_records if 
                                (getattr(r, 'rule_id', None) == rule_id or
                                 (hasattr(r, 'original_data') and hasattr(r.original_data, 'rule_id') and 
                                  r.original_data.rule_id == rule_id))]
            failure_percentage = len(rule_failed_records) / len(rule_total_records) * 100 if rule_total_records else 0
            
            # 收集失败类型
            failure_types = []
            for record in rule_failed_records:
                failure_reason = None
                if (hasattr(record, 'evaluation') and record.evaluation and 
                    hasattr(record.evaluation, 'failure_reason')):
                    failure_reason = record.evaluation.failure_reason
                elif hasattr(record, 'failure_reason'):
                    failure_reason = record.failure_reason
                
                if failure_reason:
                    failure_types.append(failure_reason)
            
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
                # 获取失败原因
                failure_reason = "未知"
                if (hasattr(record, 'evaluation') and record.evaluation and 
                    hasattr(record.evaluation, 'failure_reason')):
                    failure_reason = record.evaluation.failure_reason or "未知"
                elif hasattr(record, 'failure_reason'):
                    failure_reason = record.failure_reason or "未知"
                
                # 获取相似度分数
                similarity_score = 0
                if (hasattr(record, 'evaluation') and record.evaluation and 
                    hasattr(record.evaluation, 'similarity_score')):
                    similarity_score = record.evaluation.similarity_score or 0
                
                example = {
                    'id': record.id,
                    'question': record.question,
                    'expected_answer': record.expected_answer,
                    'actual_answer': record.actual_answer,
                    'failure_reason': failure_reason,
                    'similarity_score': similarity_score
                }
                examples.append(example)
            
            # 计算失败类型分布
            failure_type_distribution = dict(failure_type_counter)
            total_failures = len(rule_failed_records)
            failure_type_percentage = {
                fail_type: round((count / total_failures) * 100, 1) 
                for fail_type, count in failure_type_distribution.items()
            } if total_failures > 0 else {}
            
            # 计算该rule失败记录的分数占比
            # 获取该业务对象所有该rule的记录的总分
            rule_all_scores = [r.score for r in rule_total_records if hasattr(r, 'score')]
            rule_failed_scores = [r.score for r in rule_failed_records if hasattr(r, 'score')]
            
            total_rule_score = sum(rule_all_scores) if rule_all_scores else 0
            failed_rule_score = sum(rule_failed_scores) if rule_failed_scores else 0
            
            score_percentage = round((failed_rule_score / total_rule_score) * 100, 1) if total_rule_score > 0 else 0.0
            
            # 权重分析：基于失败率和分数占比
            weight_analysis = self._calculate_weight_analysis(failure_percentage, score_percentage)
            
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
                examples=examples,
                
                # 新增字段
                failure_type_distribution=failure_type_distribution,
                failure_type_percentage=failure_type_percentage,
                score_percentage=score_percentage,
                weight_analysis=weight_analysis
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_weight_analysis(self, failure_percentage: float, score_percentage: float) -> str:
        """
        计算权重分析
        
        Args:
            failure_percentage: 失败率百分比
            score_percentage: 分数占比百分比
            
        Returns:
            权重分析结果: high/medium/low
        """
        # 权重计算：失败率和分数占比的加权平均
        weighted_score = failure_percentage * self.failure_rate_weight + score_percentage * self.score_impact_weight
        
        if weighted_score >= self.high_priority_threshold:
            return "high"
        elif weighted_score >= self.medium_priority_min:
            return "medium"
        else:
            return "low"
    
    def _determine_recommendation_type(self, 
                                     failure_count: int, 
                                     similarity_score: float,
                                     failure_types: List[str]) -> Tuple[RecommendationType, str]:
        """
        根据失败次数和相似度分数确定建议类型
        
        Args:
            failure_count: 失败次数
            similarity_score: 相似度分数
            failure_types: 失败类型列表
            
        Returns:
            建议类型和描述
        """
        # 检查是否有常见的格式错误
        format_errors = any(ft and ('格式' in ft or 'JSON' in ft or '结构' in ft) for ft in failure_types)
        
        # 根据失败次数和相似度确定建议类型
        if failure_count >= self.failure_threshold:
            # 失败次数较多
            if similarity_score < self.similarity_threshold:
                # 相似度较低，建议训练
                if format_errors:
                    return RecommendationType.BOTH, "存在大量格式错误且相似度低，建议同时改进提示词和增加训练样本"
                else:
                    return RecommendationType.TRAINING, "相似度较低，建议增加训练样本提高模型理解"
            else:
                # 相似度较高，但仍有较多失败，建议改进提示词
                if format_errors:
                    return RecommendationType.PROMPT, "格式错误较多，建议在提示词中强调输出格式要求"
                else:
                    return RecommendationType.PROMPT, "相似度较高但仍有失败，建议优化提示词增强稳定性"
        else:
            # 失败次数较少
            if similarity_score < self.similarity_threshold:
                # 相似度较低，建议轻度训练
                return RecommendationType.TRAINING, "少量失败但相似度较低，建议适当增加训练样本"
            else:
                # 失败少且相似度高，可能是偶发问题
                return RecommendationType.PROMPT, "少量失败且相似度高，可能是偶发问题，建议微调提示词"
    
    def _generate_summary(self, guide: TrainingGuide) -> str:
        """
        生成训练指南总体摘要
        
        Args:
            guide: 训练指南对象
            
        Returns:
            摘要文本
        """
        # 获取所有建议
        all_recommendations = guide.get_all_recommendations()
        
        # 统计各类建议数量
        training_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.TRAINING])
        prompt_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.PROMPT])
        both_count = len([r for r in all_recommendations if r.recommendation_type == RecommendationType.BOTH])
        
        # 统计各优先级建议数量
        high_priority_count = len([r for r in all_recommendations if r.priority == Priority.HIGH])
        medium_priority_count = len([r for r in all_recommendations if r.priority == Priority.MEDIUM])
        low_priority_count = len([r for r in all_recommendations if r.priority == Priority.LOW])
        
        # 获取高优先级建议
        high_priority_recs = guide.get_high_priority_recommendations()
        
        # 生成摘要
        summary_parts = []
        
        # 总体情况
        summary_parts.append(f"评估结果显示总体失败率为{guide.overall_failure_percentage:.1f}%（{guide.total_failures}/{guide.total_records}）。")
        
        # 建议分布
        if all_recommendations:
            summary_parts.append(f"共生成{len(all_recommendations)}条改进建议，其中需要训练的有{training_count}条，"
                               f"需要改进提示词的有{prompt_count}条，两者都需要的有{both_count}条。")
            summary_parts.append(f"按优先级分布：高优先级{high_priority_count}条、中优先级{medium_priority_count}条、"
                               f"低优先级{low_priority_count}条。")
        
        # 高优先级问题
        if high_priority_recs:
            bo_rule_pairs = [f"{r.business_object}的规则{r.rule_id}" for r in high_priority_recs[:3]]
            summary_parts.append(f"发现{len(high_priority_recs)}个高优先级问题，主要集中在{', '.join(bo_rule_pairs)}"
                               f"{'等' if len(high_priority_recs) > 3 else ''}。")
        else:
            summary_parts.append("未发现高优先级问题。")
        
        # 主要业务对象情况
        worst_bo = None
        worst_failure_rate = 0
        for bo, bo_guide in guide.business_object_guides.items():
            if bo_guide.failure_percentage > worst_failure_rate:
                worst_failure_rate = bo_guide.failure_percentage
                worst_bo = bo
        
        if worst_bo and worst_failure_rate > 20:
            summary_parts.append(f"表现最差的业务对象是{worst_bo}，失败率为{worst_failure_rate:.1f}%，建议优先改进。")
        
        # 组合摘要
        return " ".join(summary_parts) 