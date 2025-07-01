"""
训练指南生成器测试

测试TrainingGuideGenerator的各种功能，包括：
- 基本功能测试
- 权重计算测试
- 配置文件集成测试
- 数据结构验证测试
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.service.evaluation_analysis.training_guide_generator import TrainingGuideGenerator
from src.entity.evaluation.training_guide import TrainingGuide, BusinessObjectTrainingGuide, TrainingRecommendation
from src.entity.evaluation.analysis_result import AnalysisResult
from src.entity.evaluation.analysis_result import QualityMetrics
from src.entity.evaluation.enums import Priority, RecommendationType


class TestTrainingGuideGenerator(unittest.TestCase):
    """训练指南生成器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 测试配置
        self.test_config = {
            'recommendation': {
                'training_guide': {
                    'weight_calculation': {
                        'failure_rate_weight': 0.6,
                        'score_impact_weight': 0.4
                    },
                    'weight_thresholds': {
                        'high_priority': {'min_weighted_score': 70.0},
                        'medium_priority': {'min_weighted_score': 40.0, 'max_weighted_score': 69.9},
                        'low_priority': {'max_weighted_score': 39.9}
                    },
                    'recommendation_types': {
                        'training_focus': {
                            'trigger_conditions': {'min_failure_rate': 30.0, 'min_failure_count': 5}
                        },
                        'prompt_optimization': {
                            'trigger_conditions': {'max_failure_rate': 50.0, 'min_score_impact': 20.0}
                        }
                    },
                    'sample_records': {
                        'max_records_per_rule': 10,
                        'text_truncate_length': 200,
                        'include_context': True
                    }
                }
            },
            'training_guide': {
                'failure_threshold': 5,
                'similarity_threshold': 0.7,
                'max_examples': 3
            }
        }
        
        # 创建生成器
        self.generator = TrainingGuideGenerator(self.test_config)
        
        # 创建模拟的分析结果
        self.mock_analysis_result = Mock(spec=AnalysisResult)
        self.mock_analysis_result.analysis_timestamp = datetime.now()
        
        # 创建模拟的质量指标
        quality_metrics = Mock(spec=QualityMetrics)
        quality_metrics.failure_rate = 0.3  # 30%失败率
        self.mock_analysis_result.quality_metrics = quality_metrics
        
        # 创建模拟的评估记录
        self.mock_evaluation_records = self._create_mock_evaluation_records()
    
    def _create_mock_evaluation_records(self):
        """创建模拟的评估记录"""
        records = []
        
        # 成功记录
        for i in range(7):
            record = Mock()
            record.id = f"success_{i}"
            record.business_object = "updateCargo"
            record.rule_id = "rule_001"
            record.status = "success"
            record.score = 100
            record.question = f"成功问题 {i}"
            record.expected_answer = f"期望答案 {i}"
            record.actual_answer = f"实际答案 {i}"
            records.append(record)
        
        # 失败记录 - updateCargo - rule_001
        for i in range(5):
            record = Mock()
            record.id = f"failed_uc_001_{i}"
            record.business_object = "updateCargo"
            record.rule_id = "rule_001"
            record.status = "failed"
            record.score = 60
            record.question = f"失败问题 updateCargo {i}"
            record.expected_answer = f"期望答案 {i}"
            record.actual_answer = f"错误答案 {i}"
            
            # 模拟评估对象
            evaluation = Mock()
            evaluation.failure_reason = "JSON属性不匹配"
            evaluation.similarity_score = 0.6
            record.evaluation = evaluation
            
            records.append(record)
        
        # 失败记录 - searchCargo - rule_002
        for i in range(3):
            record = Mock()
            record.id = f"failed_sc_002_{i}"
            record.business_object = "searchCargo"
            record.rule_id = "rule_002"
            record.status = "failed"
            record.score = 70
            record.question = f"失败问题 searchCargo {i}"
            record.expected_answer = f"期望答案 {i}"
            record.actual_answer = f"错误答案 {i}"
            
            # 模拟评估对象
            evaluation = Mock()
            evaluation.failure_reason = "JSON格式无效"
            evaluation.similarity_score = 0.8
            record.evaluation = evaluation
            
            records.append(record)
        
        return records
    
    def test_initialization_with_config(self):
        """测试生成器的配置初始化"""
        # 验证配置正确读取
        self.assertEqual(self.generator.failure_rate_weight, 0.6)
        self.assertEqual(self.generator.score_impact_weight, 0.4)
        self.assertEqual(self.generator.high_priority_threshold, 70.0)
        self.assertEqual(self.generator.medium_priority_min, 40.0)
        self.assertEqual(self.generator.max_sample_records, 10)
        self.assertEqual(self.generator.text_truncate_length, 200)
    
    def test_weight_analysis_calculation(self):
        """测试权重分析计算"""
        # 测试高优先级
        result = self.generator._calculate_weight_analysis(80.0, 90.0)  # 80*0.6 + 90*0.4 = 84.0
        self.assertEqual(result, "high")
        
        # 测试中优先级
        result = self.generator._calculate_weight_analysis(50.0, 60.0)  # 50*0.6 + 60*0.4 = 54.0
        self.assertEqual(result, "medium")
        
        # 测试低优先级
        result = self.generator._calculate_weight_analysis(20.0, 30.0)  # 20*0.6 + 30*0.4 = 24.0
        self.assertEqual(result, "low")
    
    def test_generate_training_guide_basic(self):
        """测试基本的训练指南生成"""
        guide = self.generator.generate_training_guide(
            self.mock_analysis_result, 
            self.mock_evaluation_records
        )
        
        # 验证基本结构
        self.assertIsInstance(guide, TrainingGuide)
        self.assertEqual(guide.total_records, len(self.mock_evaluation_records))
        self.assertEqual(guide.total_failures, 8)  # 5 + 3 失败记录
        self.assertGreater(guide.overall_failure_percentage, 0)
        
        # 验证业务对象指南
        self.assertIn("updateCargo", guide.business_object_guides)
        self.assertIn("searchCargo", guide.business_object_guides)
        
        # 验证updateCargo的建议
        uc_guide = guide.business_object_guides["updateCargo"]
        self.assertEqual(uc_guide.total_records, 12)  # 7成功 + 5失败
        self.assertEqual(uc_guide.failure_count, 5)
        self.assertGreater(len(uc_guide.recommendations), 0)
    
    def test_business_object_analysis(self):
        """测试业务对象分析"""
        business_guides = self.generator._analyze_business_objects(self.mock_evaluation_records)
        
        # 验证updateCargo
        uc_guide = business_guides["updateCargo"]
        self.assertEqual(uc_guide.business_object, "updateCargo")
        self.assertEqual(uc_guide.total_records, 12)
        self.assertEqual(uc_guide.failure_count, 5)
        self.assertAlmostEqual(uc_guide.failure_percentage, 5/12*100, places=1)
        
        # 验证searchCargo
        sc_guide = business_guides["searchCargo"]
        self.assertEqual(sc_guide.business_object, "searchCargo")
        self.assertEqual(sc_guide.total_records, 3)
        self.assertEqual(sc_guide.failure_count, 3)
        self.assertEqual(sc_guide.failure_percentage, 100.0)
    
    def test_rule_failure_analysis(self):
        """测试规则失败分析"""
        uc_records = [r for r in self.mock_evaluation_records if r.business_object == "updateCargo"]
        uc_failed = [r for r in uc_records if r.status == "failed"]
        
        recommendations = self.generator._analyze_rule_failures("updateCargo", uc_records, uc_failed)
        
        # 应该有一个针对rule_001的建议
        self.assertEqual(len(recommendations), 1)
        
        rec = recommendations[0]
        self.assertEqual(rec.rule_id, "rule_001")
        self.assertEqual(rec.business_object, "updateCargo")
        self.assertEqual(rec.failure_count, 5)
        self.assertAlmostEqual(rec.failure_percentage, 5/12*100, places=1)
        
        # 验证新增字段
        self.assertIsInstance(rec.failure_type_distribution, dict)
        self.assertIsInstance(rec.failure_type_percentage, dict)
        self.assertIsInstance(rec.score_percentage, float)
        self.assertIn(rec.weight_analysis, ["high", "medium", "low"])
    
    def test_failure_type_distribution(self):
        """测试失败类型分布计算"""
        # 创建具有不同失败类型的记录
        records = []
        failed_records = []
        
        # 添加相同rule的记录，不同失败类型
        for i, failure_reason in enumerate(["JSON属性不匹配", "JSON属性不匹配", "JSON格式无效"]):
            record = Mock()
            record.id = f"test_{i}"
            record.business_object = "testObject"
            record.rule_id = "test_rule"
            record.status = "failed"
            record.score = 50
            
            evaluation = Mock()
            evaluation.failure_reason = failure_reason
            evaluation.similarity_score = 0.5
            record.evaluation = evaluation
            
            records.append(record)
            failed_records.append(record)
        
        recommendations = self.generator._analyze_rule_failures("testObject", records, failed_records)
        rec = recommendations[0]
        
        # 验证失败类型分布
        expected_distribution = {"JSON属性不匹配": 2, "JSON格式无效": 1}
        self.assertEqual(rec.failure_type_distribution, expected_distribution)
        
        # 验证失败类型百分比
        expected_percentage = {"JSON属性不匹配": 66.7, "JSON格式无效": 33.3}
        for key, value in expected_percentage.items():
            self.assertAlmostEqual(rec.failure_type_percentage[key], value, places=1)
    
    def test_json_serialization(self):
        """测试JSON序列化"""
        guide = self.generator.generate_training_guide(
            self.mock_analysis_result, 
            self.mock_evaluation_records
        )
        
        # 测试to_dict方法
        guide_dict = guide.to_dict()
        self.assertIsInstance(guide_dict, dict)
        
        # 测试JSON序列化
        json_str = json.dumps(guide_dict, ensure_ascii=False)
        self.assertIsInstance(json_str, str)
        
        # 测试反序列化
        parsed_dict = json.loads(json_str)
        self.assertEqual(parsed_dict["total_records"], guide.total_records)
    
    def test_summary_generation(self):
        """测试摘要生成"""
        guide = self.generator.generate_training_guide(
            self.mock_analysis_result, 
            self.mock_evaluation_records
        )
        
        # 验证摘要存在且非空
        self.assertIsInstance(guide.summary, str)
        self.assertGreater(len(guide.summary), 0)
        
        # 验证摘要包含关键信息
        self.assertIn("失败率", guide.summary)
        self.assertIn("建议", guide.summary)
    
    def test_configuration_fallbacks(self):
        """测试配置回退机制"""
        # 创建缺少配置的生成器
        minimal_config = {}
        generator = TrainingGuideGenerator(minimal_config)
        
        # 验证默认值
        self.assertEqual(generator.failure_rate_weight, 0.6)
        self.assertEqual(generator.score_impact_weight, 0.4)
        self.assertEqual(generator.high_priority_threshold, 70.0)
        self.assertEqual(generator.max_sample_records, 10)
        self.assertEqual(generator.text_truncate_length, 200)
    
    def test_empty_records_handling(self):
        """测试空记录处理"""
        empty_records = []
        
        guide = self.generator.generate_training_guide(
            self.mock_analysis_result, 
            empty_records
        )
        
        # 验证空记录情况下的处理
        self.assertEqual(guide.total_records, 0)
        self.assertEqual(guide.total_failures, 0)
        self.assertEqual(guide.overall_failure_percentage, 0)
        self.assertEqual(len(guide.business_object_guides), 0)
    
    def test_recommendation_type_determination(self):
        """测试建议类型确定逻辑"""
        # 测试不同的失败场景
        
        # 高失败次数，低相似度 -> 训练
        rec_type, description = self.generator._determine_recommendation_type(
            failure_count=10, 
            similarity_score=0.3, 
            failure_types=["语义不匹配"]
        )
        self.assertEqual(rec_type, RecommendationType.TRAINING)
        
        # 高失败次数，高相似度，格式错误 -> 提示词
        rec_type, description = self.generator._determine_recommendation_type(
            failure_count=10, 
            similarity_score=0.8, 
            failure_types=["JSON格式无效"]
        )
        self.assertEqual(rec_type, RecommendationType.PROMPT)
        
        # 低失败次数，高相似度 -> 提示词
        rec_type, description = self.generator._determine_recommendation_type(
            failure_count=2, 
            similarity_score=0.8, 
            failure_types=["偶发错误"]
        )
        self.assertEqual(rec_type, RecommendationType.PROMPT)


class TestTrainingGuideIntegration(unittest.TestCase):
    """训练指南集成测试"""
    
    def setUp(self):
        """集成测试准备"""
        # 使用真实的配置文件路径（如果存在）
        config_path = "src/config/evaluation_analysis_settings.yml"
        
        if os.path.exists(config_path):
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            # 使用测试配置
            self.config = {
                'recommendation': {
                    'training_guide': {
                        'weight_calculation': {'failure_rate_weight': 0.6, 'score_impact_weight': 0.4},
                        'weight_thresholds': {
                            'high_priority': {'min_weighted_score': 70.0},
                            'medium_priority': {'min_weighted_score': 40.0},
                        }
                    }
                }
            }
        
        self.generator = TrainingGuideGenerator(self.config)
    
    def test_config_file_integration(self):
        """测试配置文件集成"""
        # 验证配置正确加载
        self.assertIsInstance(self.generator.failure_rate_weight, float)
        self.assertIsInstance(self.generator.score_impact_weight, float)
        self.assertIsInstance(self.generator.high_priority_threshold, float)
        
        # 验证权重总和为1（如果配置正确）
        weight_sum = self.generator.failure_rate_weight + self.generator.score_impact_weight
        self.assertAlmostEqual(weight_sum, 1.0, places=2)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {
                "analysis_result": {"quality_metrics": {"failure_rate": 0.25}},
                "evaluation_records": [
                    {
                        "id": "test_1",
                        "business_object": "testBO",
                        "rule_id": "test_rule",
                        "status": "failed",
                        "score": 60,
                        "question": "测试问题",
                        "expected_answer": "期望答案",
                        "actual_answer": "实际答案",
                        "evaluation": {"failure_reason": "测试失败", "similarity_score": 0.5}
                    }
                ]
            }
            json.dump(test_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # 模拟真实的分析结果和记录
            analysis_result = Mock()
            analysis_result.analysis_timestamp = datetime.now()
            
            quality_metrics = Mock()
            quality_metrics.failure_rate = 0.25
            analysis_result.quality_metrics = quality_metrics
            
            # 创建简单的评估记录
            record = Mock()
            record.id = "test_1"
            record.business_object = "testBO"
            record.rule_id = "test_rule"
            record.status = "failed"
            record.score = 60
            record.question = "测试问题"
            record.expected_answer = "期望答案"
            record.actual_answer = "实际答案"
            
            evaluation = Mock()
            evaluation.failure_reason = "测试失败"
            evaluation.similarity_score = 0.5
            record.evaluation = evaluation
            
            # 生成训练指南
            guide = self.generator.generate_training_guide(analysis_result, [record])
            
            # 验证结果
            self.assertIsInstance(guide, TrainingGuide)
            self.assertGreater(len(guide.summary), 0)
            
            # 验证可以序列化
            guide_dict = guide.to_dict()
            json_str = json.dumps(guide_dict, ensure_ascii=False)
            self.assertIsInstance(json_str, str)
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 