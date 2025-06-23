"""
质量指标计算器

计算评估记录的各种质量指标，包括分数分布、性能指标和质量洞察
"""

import json
import logging
import statistics
from collections import Counter, defaultdict
from typing import Dict, List, Any
import numpy as np

from src.entity.evaluation.evaluation_record import EvaluationRecord
from src.entity.evaluation.quality_metrics import (
    QualityMetrics, ScoreDistribution, PerformanceMetrics, QualityInsights
)


class QualityMetricsCalculator:
    """质量指标计算器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化质量指标计算器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.quality_config = config.get('analysis', {}).get('quality_assessment', {})
        self.logger = logging.getLogger(__name__)
    
    def calculate_metrics(self, 
                         all_records: List[EvaluationRecord],
                         success_records: List[EvaluationRecord],
                         failed_records: List[EvaluationRecord]) -> QualityMetrics:
        """
        计算综合质量指标
        
        Args:
            all_records: 所有评估记录
            success_records: 成功的评估记录
            failed_records: 失败的评估记录
            
        Returns:
            质量指标
        """
        self.logger.info(f"开始计算质量指标，总记录数: {len(all_records)}")
        
        # 基本统计
        total_questions = len(all_records)
        successful_responses = len(success_records)
        failed_responses = len(failed_records)
        success_rate = successful_responses / total_questions if total_questions > 0 else 0.0
        
        # 分数分布计算
        score_distribution = self._calculate_score_distribution(success_records)
        
        # 完美分数统计
        perfect_score_count = len([r for r in success_records if r.score == 100])
        perfect_score_rate = perfect_score_count / successful_responses if successful_responses > 0 else 0.0
        
        # JSON有效性统计
        json_valid_count = self._calculate_json_validity(all_records)
        json_valid_rate = json_valid_count / total_questions if total_questions > 0 else 0.0
        
        # 响应长度统计
        response_lengths = self._calculate_response_lengths(success_records)
        
        # 性能指标计算
        performance_metrics = self._calculate_performance_metrics(all_records)
        
        # 按业务对象分组的质量指标
        quality_by_business_object = self._calculate_quality_by_business_object(all_records)
        
        # 按规则分组的质量指标
        quality_by_rule = self._calculate_quality_by_rule(all_records)
        
        # 质量洞察生成
        quality_insights = self._generate_quality_insights(
            all_records, success_records, failed_records
        )
        
        quality_metrics = QualityMetrics(
            total_questions=total_questions,
            successful_responses=successful_responses,
            failed_responses=failed_responses,
            success_rate=success_rate,
            score_distribution=score_distribution,
            perfect_score_count=perfect_score_count,
            perfect_score_rate=perfect_score_rate,
            json_valid_count=json_valid_count,
            json_valid_rate=json_valid_rate,
            average_response_length=response_lengths['average'],
            min_response_length=response_lengths['min'],
            max_response_length=response_lengths['max'],
            performance_metrics=performance_metrics,
            quality_by_business_object=quality_by_business_object,
            quality_by_rule=quality_by_rule,
            quality_insights=quality_insights
        )
        
        self.logger.info(f"质量指标计算完成，成功率: {success_rate:.2%}")
        return quality_metrics
    
    def _calculate_score_distribution(self, success_records: List[EvaluationRecord]) -> ScoreDistribution:
        """计算分数分布"""
        if not success_records:
            return ScoreDistribution({}, {}, 0.0, 0.0, 0.0)
        
        scores = [record.score for record in success_records]
        
        # 分数段统计
        score_ranges = self._group_scores_by_ranges(scores)
        
        # 百分位数计算
        percentiles = {}
        for p in [25, 50, 75, 90, 95]:
            percentiles[f'p{p}'] = np.percentile(scores, p)
        
        # 基本统计
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        return ScoreDistribution(
            score_ranges=score_ranges,
            percentiles=percentiles,
            mean=mean_score,
            median=median_score,
            std_dev=std_dev
        )
    
    def _group_scores_by_ranges(self, scores: List[int]) -> Dict[str, int]:
        """按分数段分组"""
        ranges = {
            '90-100': (90, 100),
            '80-89': (80, 89),
            '70-79': (70, 79),
            '60-69': (60, 69),
            '50-59': (50, 59),
            '40-49': (40, 49),
            '30-39': (30, 39),
            '20-29': (20, 29),
            '10-19': (10, 19),
            '0-9': (0, 9)
        }
        
        range_counts = {}
        for range_name, (min_score, max_score) in ranges.items():
            count = len([s for s in scores if min_score <= s <= max_score])
            if count > 0:  # 只记录有数据的分数段
                range_counts[range_name] = count
        
        return range_counts
    
    def _calculate_json_validity(self, records: List[EvaluationRecord]) -> int:
        """计算JSON有效性 - 优先使用新的json_valid字段"""
        valid_count = 0
        
        for record in records:
            # 优先使用新的json_valid字段
            if hasattr(record, 'json_valid'):
                try:
                    if record.json_valid:
                        valid_count += 1
                    continue
                except (AttributeError, TypeError):
                    pass
            
            # 回退到传统方法：尝试解析actual_answer
            try:
                json.loads(record.actual_answer)
                valid_count += 1
            except (json.JSONDecodeError, TypeError):
                continue
                
        return valid_count
    
    def _calculate_response_lengths(self, success_records: List[EvaluationRecord]) -> Dict[str, float]:
        """计算响应长度统计"""
        if not success_records:
            return {'average': 0.0, 'min': 0, 'max': 0}
        
        lengths = [len(record.actual_answer) for record in success_records]
        
        return {
            'average': statistics.mean(lengths),
            'min': min(lengths),
            'max': max(lengths)
        }
    
    def _calculate_performance_metrics(self, records: List[EvaluationRecord]) -> PerformanceMetrics:
        """计算性能指标"""
        if not records:
            return PerformanceMetrics(0.0, 0.0, 0.0, 0.0, {})
        
        processing_times = [record.processing_time for record in records]
        
        # 时间百分位数
        time_percentiles = {}
        for p in [25, 50, 75, 90, 95]:
            time_percentiles[f'p{p}'] = np.percentile(processing_times, p)
        
        return PerformanceMetrics(
            total_processing_time=sum(processing_times),
            average_time_per_question=statistics.mean(processing_times),
            min_processing_time=min(processing_times),
            max_processing_time=max(processing_times),
            time_percentiles=time_percentiles
        )
    
    def _calculate_quality_by_business_object(self, records: List[EvaluationRecord]) -> Dict[str, Dict[str, float]]:
        """按业务对象计算质量指标"""
        business_objects = defaultdict(list)
        
        # 按业务对象分组
        for record in records:
            business_objects[record.business_object].append(record)
        
        quality_by_object = {}
        for obj_name, obj_records in business_objects.items():
            success_records = [r for r in obj_records if r.is_successful]
            
            # 计算该业务对象的指标
            success_rate = len(success_records) / len(obj_records) if obj_records else 0.0
            avg_score = statistics.mean([r.score for r in success_records]) if success_records else 0.0
            avg_time = statistics.mean([r.processing_time for r in obj_records]) if obj_records else 0.0
            
            quality_by_object[obj_name] = {
                'success_rate': success_rate,
                'average_score': avg_score,
                'average_processing_time': avg_time,
                'total_records': len(obj_records)
            }
        
        return quality_by_object
    
    def _calculate_quality_by_rule(self, records: List[EvaluationRecord]) -> Dict[str, Dict[str, float]]:
        """按规则计算质量指标"""
        rules = defaultdict(list)
        
        # 按规则ID分组
        for record in records:
            if record.rule_id:
                rules[str(record.rule_id)].append(record)
        
        quality_by_rule = {}
        for rule_id, rule_records in rules.items():
            success_records = [r for r in rule_records if r.is_successful]
            
            # 计算该规则的指标
            success_rate = len(success_records) / len(rule_records) if rule_records else 0.0
            avg_score = statistics.mean([r.score for r in success_records]) if success_records else 0.0
            avg_time = statistics.mean([r.processing_time for r in rule_records]) if rule_records else 0.0
            
            quality_by_rule[rule_id] = {
                'success_rate': success_rate,
                'average_score': avg_score,
                'average_processing_time': avg_time,
                'total_records': len(rule_records)
            }
        
        return quality_by_rule
    
    def _generate_quality_insights(self, 
                                  all_records: List[EvaluationRecord],
                                  success_records: List[EvaluationRecord],
                                  failed_records: List[EvaluationRecord]) -> QualityInsights:
        """生成质量洞察"""
        
        # 高质量特征分析
        high_quality_patterns = self._analyze_high_quality_patterns(success_records)
        
        # 低质量特征分析
        low_quality_patterns = self._analyze_low_quality_patterns(failed_records)
        
        # 改进建议
        improvement_recommendations = self._generate_improvement_recommendations(
            all_records, success_records, failed_records
        )
        
        # 最佳实践案例
        best_practice_examples = self._find_best_practice_examples(success_records)
        
        return QualityInsights(
            high_quality_patterns=high_quality_patterns,
            low_quality_patterns=low_quality_patterns,
            improvement_recommendations=improvement_recommendations,
            best_practice_examples=best_practice_examples
        )
    
    def _analyze_high_quality_patterns(self, success_records: List[EvaluationRecord]) -> List[str]:
        """分析高质量特征 - 利用新的记录字段"""
        patterns = []
        
        if not success_records:
            return patterns
        
        # 分析高分记录的特征
        high_score_records = [r for r in success_records if r.score >= 90]
        
        if high_score_records:
            # 分析业务对象分布
            business_objects = Counter([r.business_object for r in high_score_records])
            most_common_obj = business_objects.most_common(1)
            if most_common_obj:
                patterns.append(f"业务对象'{most_common_obj[0][0]}'在高分案例中出现频率最高")
            
            # 新增：分析规则名称分布
            rule_names = [r.rule_name for r in high_score_records 
                         if hasattr(r, 'rule_name') and r.rule_name]
            if rule_names:
                rule_name_counter = Counter(rule_names)
                top_rule = rule_name_counter.most_common(1)[0]
                patterns.append(f"表现最佳的规则是'{top_rule[0]}'，在高分案例中出现 {top_rule[1]} 次")
            
            # 新增：分析关键词匹配模式
            keywords = [r.matched_keyword for r in high_score_records 
                       if hasattr(r, 'matched_keyword') and r.matched_keyword]
            if keywords:
                keyword_counter = Counter(keywords)
                top_keyword = keyword_counter.most_common(1)[0]
                patterns.append(f"最有效的关键词是'{top_keyword[0]}'，在高分案例中出现 {top_keyword[1]} 次")
            
            # 分析响应时间特征
            response_times = [r.processing_time for r in high_score_records]
            avg_time = statistics.mean(response_times)
            patterns.append(f"高分案例的平均处理时间为 {avg_time:.2f} 秒")
            
            # 分析响应长度特征
            response_lengths = [len(r.actual_answer) for r in high_score_records]
            avg_length = statistics.mean(response_lengths)
            patterns.append(f"高分案例的平均响应长度为 {avg_length:.0f} 字符")
            
            # 新增：分析JSON有效性
            json_valid_records = [r for r in high_score_records 
                                 if hasattr(r, 'json_valid') and r.json_valid]
            if json_valid_records:
                json_valid_rate = len(json_valid_records) / len(high_score_records)
                patterns.append(f"高分案例的JSON有效率为 {json_valid_rate:.1%}")
        
        return patterns
    
    def _analyze_low_quality_patterns(self, failed_records: List[EvaluationRecord]) -> List[str]:
        """分析低质量特征 - 利用新的记录字段"""
        patterns = []
        
        if not failed_records:
            return patterns
        
        # 分析失败记录的特征
        business_objects = Counter([r.business_object for r in failed_records])
        most_problematic = business_objects.most_common(1)
        if most_problematic:
            patterns.append(f"业务对象'{most_problematic[0][0]}'的失败率最高，失败 {most_problematic[0][1]} 次")
        
        # 新增：分析问题规则
        rule_names = [r.rule_name for r in failed_records 
                     if hasattr(r, 'rule_name') and r.rule_name]
        if rule_names:
            rule_name_counter = Counter(rule_names)
            problem_rule = rule_name_counter.most_common(1)[0]
            patterns.append(f"最有问题的规则是'{problem_rule[0]}'，失败 {problem_rule[1]} 次")
        
        # 新增：分析问题关键词
        keywords = [r.matched_keyword for r in failed_records 
                   if hasattr(r, 'matched_keyword') and r.matched_keyword]
        if keywords:
            keyword_counter = Counter(keywords)
            problem_keyword = keyword_counter.most_common(1)[0]
            patterns.append(f"最有问题的关键词是'{problem_keyword[0]}'，失败 {problem_keyword[1]} 次")
        
        # 分析处理时间
        processing_times = [r.processing_time for r in failed_records]
        if processing_times:
            avg_time = statistics.mean(processing_times)
            patterns.append(f"失败案例的平均处理时间为 {avg_time:.2f} 秒")
        
        # 新增：分析常见错误模式
        detailed_analyses = [r.detailed_analysis for r in failed_records 
                           if hasattr(r, 'detailed_analysis') and r.detailed_analysis]
        if detailed_analyses:
            # 分析错误类型分布
            error_types = []
            for analysis in detailed_analyses:
                if '条件值不一致' in analysis:
                    error_types.append('字段值不匹配')
                elif '条件数量不一致' in analysis:
                    error_types.append('字段数量不一致')
                elif 'JSON解析失败' in analysis:
                    error_types.append('JSON格式错误')
                elif '低位错误' in analysis:
                    error_types.append('低级别匹配错误')
                    
            if error_types:
                error_counter = Counter(error_types)
                most_common_error = error_counter.most_common(1)[0]
                patterns.append(f"最常见的错误类型是'{most_common_error[0]}'，出现 {most_common_error[1]} 次")
        
        return patterns
    
    def _generate_improvement_recommendations(self, 
                                            all_records: List[EvaluationRecord],
                                            success_records: List[EvaluationRecord],
                                            failed_records: List[EvaluationRecord]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于成功率的建议
        success_rate = len(success_records) / len(all_records) if all_records else 0.0
        
        if success_rate < 0.5:
            recommendations.append("成功率过低，需要全面检查模型配置、训练数据质量和评估标准")
        elif success_rate < 0.7:
            recommendations.append("成功率有待提升，建议优化训练数据和调整模型参数")
        
        # 基于分数分布的建议
        if success_records:
            scores = [r.score for r in success_records]
            avg_score = statistics.mean(scores)
            
            if avg_score < 70:
                recommendations.append("平均分数偏低，建议提升答案质量和准确性")
            
            perfect_count = len([s for s in scores if s == 100])
            perfect_rate = perfect_count / len(scores)
            
            if perfect_rate < 0.1:
                recommendations.append("完美分数率较低，需要提升答案的精确度")
        
        # 基于处理时间的建议
        if all_records:
            processing_times = [r.processing_time for r in all_records]
            avg_time = statistics.mean(processing_times)
            
            if avg_time > 10:
                recommendations.append("平均处理时间过长，建议优化模型推理性能")
        
        return recommendations
    
    def _find_best_practice_examples(self, success_records: List[EvaluationRecord]) -> List[Dict[str, Any]]:
        """找出最佳实践案例"""
        examples = []
        
        # 找出完美分数的案例
        perfect_records = [r for r in success_records if r.score == 100]
        
        # 按处理时间排序，选择最快的几个
        if perfect_records:
            sorted_records = sorted(perfect_records, key=lambda x: x.processing_time)
            
            # 选择前3个作为最佳实践
            for record in sorted_records[:3]:
                examples.append({
                    'id': record.id,
                    'business_object': record.business_object,
                    'rule_id': record.rule_id,
                    'score': record.score,
                    'processing_time': record.processing_time,
                    'question_preview': record.question[:100] + '...' if len(record.question) > 100 else record.question,
                    'answer_preview': record.actual_answer[:200] + '...' if len(record.actual_answer) > 200 else record.actual_answer
                })
        
        return examples 