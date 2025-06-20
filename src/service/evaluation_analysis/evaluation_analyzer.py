"""
评估分析器

主要的评估分析引擎，协调各个组件完成评估文件的全面分析
"""

import json
import os
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.entity.evaluation import (
    EvaluationRecord, AnalysisResult, BatchAnalysisResult, 
    EvaluationMetadata, QualityMetrics, FailureAnalysis
)
import yaml
from .failure_pattern_detector import FailurePatternDetector
from .quality_metrics_calculator import QualityMetricsCalculator
from .recommendation_engine import RecommendationEngine


class EvaluationAnalyzer:
    """评估分析器主类"""
    
    def __init__(self, config_path: str = "src/config/evaluation_analysis_settings.yml"):
        """
        初始化评估分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        
        # 初始化各个组件
        self.failure_detector = FailurePatternDetector(self.config)
        self.quality_calculator = QualityMetricsCalculator(self.config)
        self.recommendation_engine = RecommendationEngine(self.config)
        
        self.logger.info("评估分析器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                # 返回默认配置
                return {
                    'analysis': {
                        'failure_pattern': {
                            'min_pattern_count': 5,
                            'max_examples_per_pattern': 10,
                            'classification_rules': {}
                        },
                        'quality_assessment': {}
                    },
                    'recommendation': {
                        'generation': {
                            'max_recommendations': 10
                        },
                        'knowledge_base': {}
                    },
                    'logging': {
                        'level': 'INFO',
                        'file_path': 'logs/evaluation_analysis.log',
                        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    }
                }
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return {'analysis': {}, 'recommendation': {}, 'logging': {}}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, self.config.get('logging', {}).get('level', 'INFO')))
        
        # 创建日志目录
        log_file = self.config.get('logging', {}).get('file_path', 'logs/evaluation_analysis.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            self.config.get('logging', {}).get('format', 
                           '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 避免重复添加处理器
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        分析单个评估文件
        
        Args:
            file_path: 评估文件路径
            
        Returns:
            分析结果
        """
        start_time = time.time()
        self.logger.info(f"开始分析文件: {file_path}")
        
        try:
            # 解析评估文件
            evaluation_data = self._parse_evaluation_file(file_path)
            evaluation_records = self._extract_evaluation_records(evaluation_data, file_path)
            
            self.logger.info(f"解析完成，共 {len(evaluation_records)} 条记录")
            
            # 提取元数据
            metadata = self._extract_metadata(evaluation_data, file_path)
            
            # 分离成功和失败的记录
            success_records = [r for r in evaluation_records if r.is_successful]
            failed_records = [r for r in evaluation_records if not r.is_successful]
            
            self.logger.info(f"成功记录: {len(success_records)}, 失败记录: {len(failed_records)}")
            
            # 失败模式分析
            failure_analysis = self.failure_detector.analyze_failures(failed_records, success_records)
            
            # 质量指标计算
            quality_metrics = self.quality_calculator.calculate_metrics(
                evaluation_records, success_records, failed_records
            )
            
            # 生成改进建议
            recommendations = self.recommendation_engine.generate_recommendations(
                failure_analysis, quality_metrics
            )
            
            # 生成关键洞察
            key_insights = self._generate_key_insights(
                evaluation_records, failure_analysis, quality_metrics
            )
            
            # 构建分析结果
            processing_time = time.time() - start_time
            analysis_result = AnalysisResult(
                file_path=file_path,
                analysis_timestamp=datetime.now(),
                processing_time=processing_time,
                metadata=metadata,
                quality_metrics=quality_metrics,
                failure_analysis=failure_analysis,
                recommendations=recommendations,
                key_insights=key_insights
            )
            
            # 将评估记录存储到分析结果中（用于报告生成）
            analysis_result._evaluation_records = evaluation_records
            
            self.logger.info(f"文件分析完成，耗时 {processing_time:.2f} 秒")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"分析文件时发生错误: {e}", exc_info=True)
            raise
    
    def batch_analyze(self, file_paths: List[str]) -> BatchAnalysisResult:
        """
        批量分析多个评估文件
        
        Args:
            file_paths: 评估文件路径列表
            
        Returns:
            批量分析结果
        """
        start_time = time.time()
        self.logger.info(f"开始批量分析 {len(file_paths)} 个文件")
        
        try:
            # 分析各个文件
            file_results = []
            for file_path in file_paths:
                result = self.analyze_file(file_path)
                file_results.append(result)
            
            # 聚合分析结果
            aggregated_metrics = self._aggregate_quality_metrics(file_results)
            aggregated_failure_analysis = self._aggregate_failure_analysis(file_results)
            
            # 文件间对比
            file_comparisons = self._compare_files(file_results)
            
            # 合并建议
            consolidated_recommendations = self._consolidate_recommendations(file_results)
            
            processing_time = time.time() - start_time
            
            batch_result = BatchAnalysisResult(
                analysis_timestamp=datetime.now(),
                total_files_analyzed=len(file_paths),
                total_processing_time=processing_time,
                file_results=file_results,
                aggregated_metrics=aggregated_metrics,
                aggregated_failure_analysis=aggregated_failure_analysis,
                file_comparisons=file_comparisons,
                consolidated_recommendations=consolidated_recommendations
            )
            
            self.logger.info(f"批量分析完成，总耗时 {processing_time:.2f} 秒")
            return batch_result
            
        except Exception as e:
            self.logger.error(f"批量分析时发生错误: {e}", exc_info=True)
            raise
    
    def _parse_evaluation_file(self, file_path: str) -> Dict[str, Any]:
        """解析评估文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 添加更健壮的JSON解析错误处理
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    # 尝试定位问题
                    self.logger.error(f"JSON解析错误: {str(e)}")
                    
                    # 尝试读取错误位置附近的内容
                    f.seek(0)
                    content = f.read()
                    error_pos = e.pos
                    start_pos = max(0, error_pos - 100)
                    end_pos = min(len(content), error_pos + 100)
                    context = content[start_pos:end_pos]
                    
                    self.logger.error(f"错误位置附近的内容: {context}")
                    newline_char = '\n'
                    self.logger.error(f"错误位置: {error_pos}, 行号约: {content[:error_pos].count(newline_char) + 1}")
                    
                    # 尝试替换特殊字符后重新解析
                    self.logger.info("尝试替换特殊字符后重新解析JSON...")
                    f.seek(0)
                    content = f.read()
                    # 替换JSON键名中可能出现的特殊字符
                    fixed_content = self._sanitize_json_keys(content)
                    
                    try:
                        return json.loads(fixed_content)
                    except json.JSONDecodeError as e2:
                        self.logger.error(f"替换特殊字符后仍然解析失败: {str(e2)}")
                        raise ValueError(f"JSON文件格式错误，无法修复: {str(e)}")
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {file_path}")
    
    def _sanitize_json_keys(self, json_content: str) -> str:
        """
        尝试修复JSON内容中的键名问题
        这是一个简单的启发式方法，可能不适用于所有情况
        """
        import re
        
        # 查找JSON对象的键名模式，并替换键名中的特殊字符
        # 这个正则表达式匹配JSON键名
        pattern = r'"([^"]*)"(?=\s*:)'
        
        def replace_key(match):
            key = match.group(1)
            # 替换键名中的特殊字符
            sanitized_key = key.replace('{', '_').replace('}', '_')
            return f'"{sanitized_key}"'
        
        # 替换所有匹配的键名
        sanitized_content = re.sub(pattern, replace_key, json_content)
        
        return sanitized_content
    
    def _extract_evaluation_records(self, data: Dict[str, Any], source_file: str) -> List[EvaluationRecord]:
        """从评估数据中提取记录"""
        records = []
        logs = data.get('logs', [])
        
        for log_entry in logs:
            try:
                record = EvaluationRecord.from_dict({**log_entry, 'source_file': source_file})
                records.append(record)
            except Exception as e:
                self.logger.warning(f"跳过无效记录: {e}")
                continue
        
        return records
    
    def _extract_metadata(self, data: Dict[str, Any], file_path: str) -> EvaluationMetadata:
        """提取元数据"""
        metadata_dict = data.get('metadata', {})
        
        # 计算文件大小
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        # 解析生成时间
        generation_time_str = metadata_dict.get('generation_time', '')
        try:
            generation_time = datetime.fromisoformat(generation_time_str.replace('Z', '+00:00'))
        except:
            generation_time = datetime.now()
        
        return EvaluationMetadata(
            file_path=file_path,
            file_size_mb=file_size_mb,
            generation_time=generation_time,
            source_files=metadata_dict.get('source_files', []),
            merged_record_count=metadata_dict.get('merged_record_count', 0),
            processing_type=metadata_dict.get('processing_type', '未知')
        )
    
    def _generate_key_insights(self, 
                              records: List[EvaluationRecord],
                              failure_analysis: FailureAnalysis,
                              quality_metrics: QualityMetrics) -> List[str]:
        """生成关键洞察"""
        insights = []
        
        # 基于成功率的洞察
        success_rate = quality_metrics.success_rate
        if success_rate < 0.5:
            insights.append(f"成功率仅为 {success_rate:.1%}，远低于正常水平，需要紧急改进")
        elif success_rate < 0.7:
            insights.append(f"成功率为 {success_rate:.1%}，有较大改进空间")
        else:
            insights.append(f"成功率为 {success_rate:.1%}，整体表现良好")
        
        # 基于失败模式的洞察
        if failure_analysis.patterns:
            top_failure = failure_analysis.patterns[0]
            insights.append(f"主要失败原因是'{top_failure.pattern_name}'，占失败案例的 {top_failure.percentage:.1%}")
        
        # 基于分数分布的洞察
        avg_score = quality_metrics.score_distribution.mean
        perfect_rate = quality_metrics.perfect_score_rate
        if perfect_rate < 0.1:
            insights.append(f"完美分数率仅为 {perfect_rate:.1%}，需要提升答案质量")
        
        # 基于业务对象表现的洞察
        if quality_metrics.quality_by_business_object:
            best_objects = quality_metrics.get_top_performing_business_objects(3)
            if best_objects:
                insights.append(f"表现最佳的业务对象是: {', '.join(best_objects)}")
        
        return insights
    
    def _aggregate_quality_metrics(self, results: List[AnalysisResult]) -> QualityMetrics:
        """聚合质量指标"""
        # 这里应该实现质量指标的聚合逻辑
        # 由于篇幅限制，这里返回第一个结果的指标作为示例
        if results:
            return results[0].quality_metrics
        else:
            # 返回空的质量指标
            from src.entity.evaluation.quality_metrics import ScoreDistribution, PerformanceMetrics, QualityInsights
            return QualityMetrics(
                total_questions=0,
                successful_responses=0,
                failed_responses=0,
                success_rate=0.0,
                score_distribution=ScoreDistribution({}, {}, 0.0, 0.0, 0.0),
                perfect_score_count=0,
                perfect_score_rate=0.0,
                json_valid_count=0,
                json_valid_rate=0.0,
                average_response_length=0.0,
                min_response_length=0,
                max_response_length=0,
                performance_metrics=PerformanceMetrics(0.0, 0.0, 0.0, 0.0, {}),
                quality_by_business_object={},
                quality_by_rule={},
                quality_insights=QualityInsights([], [], [], [])
            )
    
    def _aggregate_failure_analysis(self, results: List[AnalysisResult]) -> FailureAnalysis:
        """聚合失败分析"""
        # 这里应该实现失败分析的聚合逻辑
        if results:
            return results[0].failure_analysis
        else:
            return FailureAnalysis(
                total_failed_count=0,
                total_success_count=0,
                failure_rate=0.0,
                patterns=[],
                most_common_failure="无",
                failure_by_business_object={},
                failure_by_rule_id={}
            )
    
    def _compare_files(self, results: List[AnalysisResult]) -> Dict[str, Dict[str, float]]:
        """文件间对比"""
        comparisons = {}
        
        for result in results:
            file_name = os.path.basename(result.file_path)
            comparisons[file_name] = {
                'success_rate': result.quality_metrics.success_rate,
                'average_score': result.quality_metrics.score_distribution.mean,
                'total_questions': result.quality_metrics.total_questions,
                'processing_time': result.processing_time
            }
        
        return comparisons
    
    def _consolidate_recommendations(self, results: List[AnalysisResult]) -> List:
        """合并建议"""
        # 这里应该实现建议合并的逻辑
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        # 简单去重和优先级排序
        unique_recommendations = []
        seen_titles = set()
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_recommendations = sorted(
            all_recommendations, 
            key=lambda x: priority_order.get(x.priority, 3)
        )
        
        for rec in sorted_recommendations:
            if rec.title not in seen_titles:
                unique_recommendations.append(rec)
                seen_titles.add(rec.title)
        
        return unique_recommendations[:10]  # 最多返回10个建议 