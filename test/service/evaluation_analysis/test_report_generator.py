"""
测试报告生成器
"""

import os
import tempfile
import pytest
from unittest.mock import Mock
from datetime import datetime

from src.service.evaluation_analysis.report_generator import ReportGenerator
from src.entity.evaluation.analysis_result import AnalysisResult, EvaluationMetadata, Recommendation
from src.entity.evaluation.quality_metrics import QualityMetrics, ScoreDistribution, PerformanceMetrics, QualityInsights
from src.entity.evaluation.failure_pattern import FailureAnalysis, FailurePattern, SeverityLevel, FailureType


class TestReportGenerator:
    """报告生成器测试"""
    
    def setup_method(self):
        """测试前的设置"""
        self.config = {
            'reporting': {
                'charts': {
                    'figure_size': {
                        'width': 12,
                        'height': 8
                    }
                }
            }
        }
        self.generator = ReportGenerator(self.config)
    
    def create_mock_analysis_result(self):
        """创建模拟分析结果"""
        # 创建分数分布
        score_distribution = ScoreDistribution(
            score_ranges={'0-20': 100, '21-40': 200, '41-60': 500, '61-80': 800, '81-100': 400},
            percentiles={'p50': 80.0, 'p90': 95.0, 'p95': 98.0, 'p99': 99.5},
            mean=75.5,
            median=80.0,
            std_dev=15.2
        )
        
        # 创建性能指标
        performance_metrics = PerformanceMetrics(
            total_processing_time=120.5,
            average_time_per_question=0.35,
            min_processing_time=0.1,
            max_processing_time=2.5,
            time_percentiles={'50': 0.3, '90': 0.8, '95': 1.2, '99': 2.0}
        )
        
        # 创建质量洞察
        quality_insights = QualityInsights(
            high_quality_patterns=["详细回答", "准确信息"],
            low_quality_patterns=["JSON格式错误", "信息不完整"],
            improvement_recommendations=["改进数据生成", "增强格式验证"],
            best_practice_examples=[{"example": "优秀回答示例"}]
        )
        
        # 创建质量指标
        quality_metrics = QualityMetrics(
            total_questions=2000,
            successful_responses=1200,
            failed_responses=800,
            success_rate=0.6,
            score_distribution=score_distribution,
            perfect_score_count=400,
            perfect_score_rate=0.2,
            json_valid_count=1700,
            json_valid_rate=0.85,
            average_response_length=150.5,
            min_response_length=50,
            max_response_length=500,
            performance_metrics=performance_metrics,
            quality_by_business_object={
                'searchStaff': {
                    'success_rate': 0.45,
                    'average_score': 65.2,
                    'total_records': 800
                },
                'updateCargo': {
                    'success_rate': 0.85,
                    'average_score': 88.7,
                    'total_records': 600
                },
                'searchContract': {
                    'success_rate': 0.72,
                    'average_score': 78.3,
                    'total_records': 600
                }
            },
            quality_by_rule={'rule1': {'success_rate': 0.8}, 'rule2': {'success_rate': 0.6}},
            quality_insights=quality_insights
        )
        
        # 创建失败分析
        failure_patterns = [
            FailurePattern(
                pattern_type=FailureType.JSON_MISMATCH,
                pattern_name="JSON属性不匹配",
                description="生成的JSON结构与期望不符",
                count=750,
                percentage=0.75,
                severity=SeverityLevel.CRITICAL,
                examples=[{"错误": "属性名错误"}, {"错误": "数据类型不匹配"}],
                improvement_suggestions=["检查JSON结构", "验证属性映射"],
                related_rule_ids=["rule1", "rule2"],
                related_business_objects=["searchStaff", "updateCargo"]
            ),
            FailurePattern(
                pattern_type=FailureType.FORMAT_ERROR,
                pattern_name="格式错误",
                description="输出格式不正确",
                count=50,
                percentage=0.05,
                severity=SeverityLevel.MAJOR,
                examples=[{"错误": "缺少必要字段"}, {"错误": "语法错误"}],
                improvement_suggestions=["验证输出格式", "添加格式检查"],
                related_rule_ids=["rule3"],
                related_business_objects=["searchContract"]
            )
        ]
        
        failure_analysis = FailureAnalysis(
            total_failed_count=800,
            total_success_count=1200,
            failure_rate=0.4,
            patterns=failure_patterns,
            most_common_failure="JSON属性不匹配",
            failure_by_business_object={"searchStaff": 400, "updateCargo": 200, "searchContract": 200},
            failure_by_rule_id={"rule1": 300, "rule2": 450, "rule3": 50}
        )
        
        # 创建评估元数据
        metadata = EvaluationMetadata(
            file_path="/test/evaluation_file.json",
            file_size_mb=36.5,
            generation_time=datetime.now(),
            source_files=["train_data_v1.json"],
            merged_record_count=2000,
            processing_type="evaluation_analysis"
        )
        
        # 创建建议
        recommendations = [
            Recommendation(
                priority="high",
                category="训练数据",
                title="修复JSON属性不匹配问题",
                description="主要失败原因是JSON属性不匹配，需要调整数据生成逻辑",
                expected_impact="可提升成功率20-30%",
                implementation_effort="medium"
            ),
            Recommendation(
                priority="medium",
                category="质量监控",
                title="加强数据验证",
                description="增加更多的数据验证规则",
                expected_impact="减少格式错误",
                implementation_effort="low"
            )
        ]
        
        # 创建分析结果
        analysis_result = AnalysisResult(
            file_path="/test/evaluation_file.json",
            analysis_timestamp=datetime.now(),
            processing_time=120.5,
            metadata=metadata,
            quality_metrics=quality_metrics,
            failure_analysis=failure_analysis,
            recommendations=recommendations,
            key_insights=[
                "成功率仅为60%，需要改进",
                "searchStaff业务对象表现最差",
                "JSON属性不匹配是主要问题"
            ]
        )
        
        return analysis_result
    
    def test_report_generator_initialization(self):
        """测试报告生成器初始化"""
        assert self.generator.config == self.config
        assert hasattr(self.generator, 'logger')
    
    def test_create_success_failure_pie_chart(self):
        """测试成功失败饼图生成"""
        analysis_result = self.create_mock_analysis_result()
        
        chart_base64 = self.generator._create_success_failure_pie_chart(analysis_result.quality_metrics)
        
        assert chart_base64.startswith('data:image/png;base64,')
        assert len(chart_base64) > 100  # 确保有实际内容
    
    def test_create_score_distribution_chart(self):
        """测试分数分布图生成"""
        analysis_result = self.create_mock_analysis_result()
        
        chart_base64 = self.generator._create_score_distribution_chart(analysis_result.quality_metrics)
        
        assert chart_base64.startswith('data:image/png;base64,')
        assert len(chart_base64) > 100
    
    def test_create_business_object_chart(self):
        """测试业务对象表现图生成"""
        analysis_result = self.create_mock_analysis_result()
        
        chart_base64 = self.generator._create_business_object_chart(analysis_result.quality_metrics)
        
        assert chart_base64.startswith('data:image/png;base64,')
        assert len(chart_base64) > 100
    
    def test_generate_charts(self):
        """测试图表生成流程"""
        analysis_result = self.create_mock_analysis_result()
        
        charts = self.generator._generate_charts(analysis_result)
        
        assert 'success_failure_pie' in charts
        assert 'score_distribution' in charts
        assert 'business_object_performance' in charts
        
        for chart in charts.values():
            if chart:  # 某些图表可能为空
                assert chart.startswith('data:image/png;base64,')
    
    def test_generate_html_content(self):
        """测试HTML内容生成"""
        analysis_result = self.create_mock_analysis_result()
        charts = {
            'success_failure_pie': 'data:image/png;base64,test123',
            'score_distribution': 'data:image/png;base64,test456',
            'business_object_performance': 'data:image/png;base64,test789'
        }
        
        html_content = self.generator._generate_html_content(analysis_result, charts)
        
        assert '<!DOCTYPE html>' in html_content
        assert '评估分析报告' in html_content
        assert '60.0%' in html_content  # 成功率
        assert '2,000' in html_content  # 总问题数
        assert '75.5' in html_content  # 平均分数
        assert 'test123' in html_content  # 图表数据
    
    def test_generate_html_report(self):
        """测试完整HTML报告生成"""
        analysis_result = self.create_mock_analysis_result()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = self.generator.generate_html_report(analysis_result, temp_dir)
            
            # 验证文件存在
            assert os.path.exists(report_path)
            assert report_path.endswith('.html')
            
            # 验证文件内容
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<!DOCTYPE html>' in content
                assert '评估分析报告' in content
                assert 'searchStaff' in content  # 业务对象名称


if __name__ == "__main__":
    # 简单的测试运行
    test = TestReportGenerator()
    test.setup_method()
    
    print("测试报告生成器...")
    
    # 测试图表生成
    analysis_result = test.create_mock_analysis_result()
    
    print("✓ 生成成功失败饼图")
    pie_chart = test.generator._create_success_failure_pie_chart(analysis_result.quality_metrics)
    
    print("✓ 生成分数分布图")
    dist_chart = test.generator._create_score_distribution_chart(analysis_result.quality_metrics)
    
    print("✓ 生成业务对象表现图")
    business_chart = test.generator._create_business_object_chart(analysis_result.quality_metrics)
    
    print("✓ 生成完整HTML报告")
    with tempfile.TemporaryDirectory() as temp_dir:
        report_path = test.generator.generate_html_report(analysis_result, temp_dir)
        print(f"  报告已生成: {report_path}")
    
    print("所有测试通过！") 