"""
问题缩减专项分析器

扩展现有的evaluation_analysis框架，为问题缩减功能提供专门的评估报告生成功能。
重用现有的质量指标计算器和报告生成器，提供缩减效果统计、规则应用频率分析和质量分布分析。
"""

import json
import logging
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .quality_metrics_calculator import QualityMetricsCalculator
from .evaluation_analyzer import EvaluationAnalyzer
from src.service.common.question_reduction import evaluate_reduction_quality


class QuestionReductionAnalyzer:
    """问题缩减专项分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化问题缩减分析器
        
        Args:
            config: 配置字典，如果为None则使用默认配置
        """
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        
        # 重用现有的质量指标计算器
        self.quality_calculator = QualityMetricsCalculator(self.config)
        
        self.logger.info("问题缩减专项分析器初始化完成")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "analysis": {
                "quality_assessment": {
                    "score_thresholds": {
                        "excellent": 0.9,
                        "good": 0.7,
                        "fair": 0.5,
                        "poor": 0.3
                    }
                }
            },
            "reporting": {
                "include_charts": True,
                "include_recommendations": True
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def analyze_reduction_data(self, reduction_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析问题缩减数据
        
        Args:
            reduction_data: 问题缩减数据列表，每个元素包含original_question, reduced_question等字段
            
        Returns:
            分析结果字典
        """
        self.logger.info(f"开始分析问题缩减数据，数据量: {len(reduction_data)}")
        
        # 1. 缩减效果统计
        reduction_stats = self._analyze_reduction_effectiveness(reduction_data)
        
        # 2. 规则应用频率分析
        rule_analysis = self._analyze_rule_application(reduction_data)
        
        # 3. 缩减质量分布
        quality_distribution = self._analyze_quality_distribution(reduction_data)
        
        # 4. 生成改进建议
        recommendations = self._generate_recommendations(reduction_stats, rule_analysis, quality_distribution)
        
        # 5. 汇总分析结果
        analysis_result = {
            "analysis_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_samples": len(reduction_data),
                "analyzer_version": "1.0.0"
            },
            "reduction_effectiveness": reduction_stats,
            "rule_application_analysis": rule_analysis,
            "quality_distribution": quality_distribution,
            "recommendations": recommendations,
            "summary": self._generate_summary(reduction_stats, quality_distribution)
        }
        
        self.logger.info("问题缩减数据分析完成")
        return analysis_result
    
    def _analyze_reduction_effectiveness(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析缩减效果"""
        reduction_rates = []
        length_reductions = []
        
        for item in data:
            original = item.get("original_question", "")
            reduced = item.get("reduced_question", "")
            
            if original and reduced:
                original_len = len(original)
                reduced_len = len(reduced)
                
                if original_len > 0:
                    reduction_rate = (original_len - reduced_len) / original_len
                    reduction_rates.append(reduction_rate)
                    length_reductions.append(original_len - reduced_len)
        
        if not reduction_rates:
            return {"error": "没有有效的缩减数据"}
        
        return {
            "average_reduction_rate": round(statistics.mean(reduction_rates), 3),
            "median_reduction_rate": round(statistics.median(reduction_rates), 3),
            "max_reduction_rate": round(max(reduction_rates), 3),
            "min_reduction_rate": round(min(reduction_rates), 3),
            "std_reduction_rate": round(statistics.stdev(reduction_rates) if len(reduction_rates) > 1 else 0, 3),
            "average_length_reduction": round(statistics.mean(length_reductions), 1),
            "total_samples": len(reduction_rates),
            "reduction_rate_distribution": self._calculate_distribution(reduction_rates)
        }
    
    def _analyze_rule_application(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析规则应用频率"""
        rule_counter = Counter()
        rule_combinations = Counter()
        reduction_level_counter = Counter()
        
        for item in data:
            # 从reduction_stats中提取规则信息
            stats = item.get("reduction_stats", {})
            applied_rules = stats.get("applied_rules", [])
            reduction_level = stats.get("reduction_level", "unknown")
            
            # 统计单个规则
            for rule in applied_rules:
                rule_counter[rule] += 1
            
            # 统计规则组合
            if applied_rules:
                rule_combo = tuple(sorted(applied_rules))
                rule_combinations[rule_combo] += 1
            
            # 统计缩减级别
            reduction_level_counter[reduction_level] += 1
        
        return {
            "most_used_rules": dict(rule_counter.most_common(10)),
            "rule_application_frequency": dict(rule_counter),
            "popular_rule_combinations": dict(rule_combinations.most_common(5)),
            "reduction_level_distribution": dict(reduction_level_counter),
            "total_rule_applications": sum(rule_counter.values()),
            "unique_rules_count": len(rule_counter)
        }
    
    def _analyze_quality_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析缩减质量分布"""
        quality_scores = {
            "reduction_rate": [],
            "key_info_retention_rate": [],
            "semantic_similarity": [],
            "readability_score": [],
            "overall_quality": []
        }
        
        quality_categories = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for item in data:
            original = item.get("original_question", "")
            reduced = item.get("reduced_question", "")
            
            if original and reduced:
                # 使用我们之前实现的评估函数
                quality_result = evaluate_reduction_quality(original, reduced)
                
                for metric, score in quality_result.items():
                    if metric in quality_scores:
                        quality_scores[metric].append(score)
                
                # 分类质量等级
                overall_score = quality_result.get("overall_quality", 0)
                if overall_score >= 0.9:
                    quality_categories["excellent"] += 1
                elif overall_score >= 0.7:
                    quality_categories["good"] += 1
                elif overall_score >= 0.5:
                    quality_categories["fair"] += 1
                else:
                    quality_categories["poor"] += 1
        
        # 计算各指标的统计信息
        quality_stats = {}
        for metric, scores in quality_scores.items():
            if scores:
                quality_stats[metric] = {
                    "mean": round(statistics.mean(scores), 3),
                    "median": round(statistics.median(scores), 3),
                    "std": round(statistics.stdev(scores) if len(scores) > 1 else 0, 3),
                    "min": round(min(scores), 3),
                    "max": round(max(scores), 3)
                }
        
        return {
            "quality_metrics_statistics": quality_stats,
            "quality_categories": quality_categories,
            "quality_category_percentages": {
                category: round(count / len(data) * 100, 1) if data else 0
                for category, count in quality_categories.items()
            },
            "total_evaluated_samples": len(data)
        }
    
    def _calculate_distribution(self, values: List[float], bins: int = 5) -> Dict[str, int]:
        """计算数值分布"""
        if not values:
            return {}
        
        min_val, max_val = min(values), max(values)
        if min_val == max_val:
            return {f"{min_val:.2f}": len(values)}
        
        bin_width = (max_val - min_val) / bins
        distribution = {}
        
        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = min_val + (i + 1) * bin_width
            
            if i == bins - 1:  # 最后一个区间包含最大值
                count = sum(1 for v in values if bin_start <= v <= bin_end)
            else:
                count = sum(1 for v in values if bin_start <= v < bin_end)
            
            bin_label = f"{bin_start:.2f}-{bin_end:.2f}"
            distribution[bin_label] = count
        
        return distribution
    
    def _generate_recommendations(self, reduction_stats: Dict[str, Any], 
                                rule_analysis: Dict[str, Any], 
                                quality_distribution: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于缩减效果的建议
        avg_reduction = reduction_stats.get("average_reduction_rate", 0)
        if avg_reduction < 0.3:
            recommendations.append("缩减效果偏低，建议调整缩减策略或增加更激进的缩减规则")
        elif avg_reduction > 0.8:
            recommendations.append("缩减率过高，可能影响信息完整性，建议适当降低缩减强度")
        
        # 基于质量分布的建议
        quality_cats = quality_distribution.get("quality_category_percentages", {})
        poor_percentage = quality_cats.get("poor", 0)
        if poor_percentage > 20:
            recommendations.append(f"有{poor_percentage}%的样本质量较差，建议优化缩减算法")
        
        excellent_percentage = quality_cats.get("excellent", 0)
        if excellent_percentage > 80:
            recommendations.append("缩减质量优秀，可以考虑应用到更多场景")
        
        # 基于规则应用的建议
        unique_rules = rule_analysis.get("unique_rules_count", 0)
        if unique_rules < 3:
            recommendations.append("使用的缩减规则种类较少，建议增加更多样化的缩减策略")
        
        if not recommendations:
            recommendations.append("整体缩减效果良好，继续保持当前策略")
        
        return recommendations
    
    def _generate_summary(self, reduction_stats: Dict[str, Any], 
                         quality_distribution: Dict[str, Any]) -> str:
        """生成分析摘要"""
        avg_reduction = reduction_stats.get("average_reduction_rate", 0)
        total_samples = reduction_stats.get("total_samples", 0)
        
        quality_cats = quality_distribution.get("quality_category_percentages", {})
        good_quality_percentage = quality_cats.get("excellent", 0) + quality_cats.get("good", 0)
        
        summary = f"""
问题缩减分析摘要：
- 分析样本数量：{total_samples}
- 平均缩减率：{avg_reduction:.1%}
- 高质量缩减比例：{good_quality_percentage:.1%}
- 整体评估：{'优秀' if good_quality_percentage > 80 else '良好' if good_quality_percentage > 60 else '需要改进'}
        """.strip()
        
        return summary
    
    def generate_report(self, reduction_data: List[Dict[str, Any]], 
                       output_path: Optional[str] = None) -> str:
        """
        生成完整的评估报告
        
        Args:
            reduction_data: 问题缩减数据
            output_path: 输出文件路径，如果为None则返回报告内容
            
        Returns:
            报告内容或文件路径
        """
        analysis_result = self.analyze_reduction_data(reduction_data)
        
        # 生成报告内容
        report_content = self._format_report(analysis_result)
        
        if output_path:
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.info(f"评估报告已保存到: {output_path}")
            return output_path
        else:
            return report_content
    
    def _format_report(self, analysis_result: Dict[str, Any]) -> str:
        """格式化报告内容"""
        timestamp = analysis_result["analysis_metadata"]["timestamp"]
        total_samples = analysis_result["analysis_metadata"]["total_samples"]
        
        report = f"""
# 问题缩减质量评估报告

**生成时间**: {timestamp}
**分析样本数**: {total_samples}

## 执行摘要

{analysis_result["summary"]}

## 缩减效果分析

{self._format_reduction_effectiveness(analysis_result["reduction_effectiveness"])}

## 规则应用分析

{self._format_rule_analysis(analysis_result["rule_application_analysis"])}

## 质量分布分析

{self._format_quality_distribution(analysis_result["quality_distribution"])}

## 改进建议

{self._format_recommendations(analysis_result["recommendations"])}

---
*报告由问题缩减专项分析器生成*
        """.strip()
        
        return report
    
    def _format_reduction_effectiveness(self, stats: Dict[str, Any]) -> str:
        """格式化缩减效果部分"""
        return f"""
- **平均缩减率**: {stats.get('average_reduction_rate', 0):.1%}
- **中位数缩减率**: {stats.get('median_reduction_rate', 0):.1%}
- **平均长度缩减**: {stats.get('average_length_reduction', 0):.1f} 字符
- **缩减率标准差**: {stats.get('std_reduction_rate', 0):.3f}
        """.strip()
    
    def _format_rule_analysis(self, analysis: Dict[str, Any]) -> str:
        """格式化规则分析部分"""
        most_used = analysis.get("most_used_rules", {})
        level_dist = analysis.get("reduction_level_distribution", {})
        
        rules_text = "\n".join([f"  - {rule}: {count}次" for rule, count in list(most_used.items())[:5]])
        levels_text = "\n".join([f"  - {level}: {count}次" for level, count in level_dist.items()])
        
        return f"""
**最常用规则**:
{rules_text}

**缩减级别分布**:
{levels_text}

- **总规则应用次数**: {analysis.get('total_rule_applications', 0)}
- **使用的规则种类**: {analysis.get('unique_rules_count', 0)}
        """.strip()
    
    def _format_quality_distribution(self, distribution: Dict[str, Any]) -> str:
        """格式化质量分布部分"""
        categories = distribution.get("quality_category_percentages", {})
        
        return f"""
**质量等级分布**:
- 优秀 (≥90%): {categories.get('excellent', 0):.1f}%
- 良好 (70-89%): {categories.get('good', 0):.1f}%
- 一般 (50-69%): {categories.get('fair', 0):.1f}%
- 较差 (<50%): {categories.get('poor', 0):.1f}%

**评估样本数**: {distribution.get('total_evaluated_samples', 0)}
        """.strip()
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """格式化建议部分"""
        return "\n".join([f"- {rec}" for rec in recommendations])
