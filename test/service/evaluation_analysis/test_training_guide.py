"""
训练指南功能测试

测试训练指南生成器的基本功能
"""

import unittest
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.service.evaluation_analysis.training_guide_generator import TrainingGuideGenerator


class TestTrainingGuide(unittest.TestCase):
    """训练指南测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_config = {
            'recommendation': {
                'training_guide': {
                    'weight_calculation': {
                        'failure_rate_weight': 0.6,
                        'score_impact_weight': 0.4
                    },
                    'weight_thresholds': {
                        'high_priority': {'min_weighted_score': 70.0},
                        'medium_priority': {'min_weighted_score': 40.0, 'max_weighted_score': 69.9}
                    },
                    'sample_records': {
                        'max_records_per_rule': 10,
                        'text_truncate_length': 200
                    }
                }
            },
            'training_guide': {
                'failure_threshold': 5,
                'similarity_threshold': 0.7,
                'max_examples': 3
            }
        }
        
        self.generator = TrainingGuideGenerator(self.test_config)
    
    def test_generator_initialization(self):
        """测试生成器初始化"""
        self.assertIsNotNone(self.generator)
        self.assertEqual(self.generator.failure_rate_weight, 0.6)
        self.assertEqual(self.generator.score_impact_weight, 0.4)
        self.assertEqual(self.generator.high_priority_threshold, 70.0)
    
    def test_weight_calculation(self):
        """测试权重计算"""
        # 测试高优先级 (80*0.6 + 90*0.4 = 84.0)
        result = self.generator._calculate_weight_analysis(80.0, 90.0)
        self.assertEqual(result, "high")
        
        # 测试中优先级 (50*0.6 + 60*0.4 = 54.0)
        result = self.generator._calculate_weight_analysis(50.0, 60.0)
        self.assertEqual(result, "medium")
        
        # 测试低优先级 (20*0.6 + 30*0.4 = 24.0)
        result = self.generator._calculate_weight_analysis(20.0, 30.0)
        self.assertEqual(result, "low")
    
    def test_config_defaults(self):
        """测试配置默认值"""
        minimal_generator = TrainingGuideGenerator({})
        
        # 验证默认值
        self.assertEqual(minimal_generator.failure_rate_weight, 0.6)
        self.assertEqual(minimal_generator.score_impact_weight, 0.4)
        self.assertEqual(minimal_generator.max_sample_records, 10)
        self.assertEqual(minimal_generator.text_truncate_length, 200)


if __name__ == '__main__':
    print("开始运行训练指南测试...")
    unittest.main(verbosity=2) 