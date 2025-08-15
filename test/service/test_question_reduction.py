#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问题缩减功能专项测试模块

测试覆盖：
1. 基础缩减函数单元测试
2. 高级缩减功能集成测试  
3. 评估指标功能测试
4. 边界情况和异常处理测试
"""

import unittest
import sys
import os
from typing import Dict, Any

# 添加项目根路径到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# 导入问题缩减模块
from src.service.common.question_reduction import (
    normalize_experiment_id,
    extract_company_shortname,
    extract_engineering_keywords,
    normalize_time_expressions,
    advanced_simplify_question,
    evaluate_reduction_quality
)


class TestBasicReductionFunctions(unittest.TestCase):
    """基础缩减函数单元测试"""
    
    def test_normalize_experiment_id(self):
        """测试实验编号标准化功能"""
        # 正常情况
        result = normalize_experiment_id("找一下实验03以及实验41")
        # 验证结果包含两个实验编号且去除了噪声词
        self.assertIn("实验03", result)
        self.assertIn("实验41", result)
        self.assertNotIn("找一下", result)

        # 不同连接词
        result = normalize_experiment_id("实验01和实验02")
        self.assertIn("实验01", result)
        self.assertIn("实验02", result)
        
        # 空字符串
        self.assertEqual(normalize_experiment_id(""), "")
        
        # 单个实验编号
        self.assertEqual(
            normalize_experiment_id("实验03"),
            "实验03"
        )
    
    def test_extract_company_shortname(self):
        """测试公司名称简化功能"""
        # 正常情况
        result = extract_company_shortname("广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司")
        self.assertIn("百聚鑫钢构", result)
        self.assertIn("紧鑫五金", result)
        self.assertNotIn("有限公司", result)
        self.assertNotIn("广东", result)

        # 单个公司
        result = extract_company_shortname("深圳市腾讯科技有限公司")
        self.assertIn("腾讯科技", result)
        self.assertNotIn("有限公司", result)
        self.assertNotIn("深圳市", result)
        
        # 空字符串
        self.assertEqual(extract_company_shortname(""), "")
    
    def test_extract_engineering_keywords(self):
        """测试工程属性关键词提取功能"""
        # 正常情况
        result = extract_engineering_keywords("工程属性70mm钢板（Q345B）钢制件")
        self.assertIn("70mm钢板", result)
        
        # 空字符串
        self.assertEqual(extract_engineering_keywords(""), "")
        
        # 无工程属性
        self.assertEqual(
            extract_engineering_keywords("普通文本"),
            "普通文本"
        )
    
    def test_normalize_time_expressions(self):
        """测试时间表达标准化功能"""
        # 正常情况
        self.assertEqual(
            normalize_time_expressions("提交日在最近五天"),
            "近5天提交"
        )
        
        # 订单时间
        result = normalize_time_expressions("订单下单时间在最近五天订单预审单")
        self.assertIn("近5天", result)
        self.assertIn("下单的预审单", result)
        
        # 空字符串
        self.assertEqual(normalize_time_expressions(""), "")


class TestAdvancedSimplifyQuestion(unittest.TestCase):
    """高级缩减功能集成测试"""
    
    def test_basic_level_reduction(self):
        """测试基础级别缩减"""
        original = "找一下实验03以及实验41的相关信息"
        result = advanced_simplify_question(original, reduction_level='basic')
        
        # 基础级别应该有一定的缩减效果
        self.assertLess(len(result), len(original))
        self.assertIsInstance(result, str)
    
    def test_advanced_level_reduction(self):
        """测试高级级别缩减"""
        original = "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息"
        result = advanced_simplify_question(original, reduction_level='advanced')

        # 高级级别应该有更好的缩减效果
        self.assertLess(len(result), len(original))
        self.assertIn("百聚鑫钢构", result)
        # 检查是否包含紧鑫相关内容（可能被部分处理）
        self.assertTrue("紧鑫" in result or "5金" in result)
    
    def test_aggressive_level_reduction(self):
        """测试激进级别缩减"""
        original = "查看一下提交日在最近五天的订单预审单信息"
        result = advanced_simplify_question(original, reduction_level='aggressive')
        
        # 激进级别应该有最大的缩减效果
        self.assertLess(len(result), len(original))
        self.assertIn("近5天", result)
    
    def test_return_stats(self):
        """测试统计信息返回"""
        original = "找一下实验03以及实验41"
        result = advanced_simplify_question(original, return_stats=True)
        
        # 验证返回结构
        self.assertIsInstance(result, dict)
        self.assertIn("result", result)
        self.assertIn("stats", result)
        
        stats = result["stats"]
        self.assertIn("original_length", stats)
        self.assertIn("final_length", stats)
        self.assertIn("reduction_rate", stats)
        self.assertIn("applied_rules", stats)
    
    def test_empty_input(self):
        """测试空输入处理"""
        result = advanced_simplify_question("")
        self.assertEqual(result, "")
        
        # 测试统计信息
        result_with_stats = advanced_simplify_question("", return_stats=True)
        self.assertEqual(result_with_stats["result"], "")
    
    def test_invalid_reduction_level(self):
        """测试无效缩减级别"""
        with self.assertRaises(ValueError):
            advanced_simplify_question("测试文本", reduction_level='invalid')


class TestEvaluateReductionQuality(unittest.TestCase):
    """评估指标功能测试"""
    
    def test_basic_evaluation(self):
        """测试基础评估功能"""
        original = "找一下实验03以及实验41的相关信息"
        reduced = "实验03、实验41"
        
        result = evaluate_reduction_quality(original, reduced)
        
        # 验证返回结构
        self.assertIsInstance(result, dict)
        expected_keys = [
            "reduction_rate",
            "key_info_retention_rate", 
            "semantic_similarity",
            "readability_score",
            "overall_quality"
        ]
        for key in expected_keys:
            self.assertIn(key, result)
            self.assertIsInstance(result[key], float)
            self.assertGreaterEqual(result[key], 0.0)
            self.assertLessEqual(result[key], 1.0)
    
    def test_perfect_retention(self):
        """测试完美保持情况"""
        original = "实验03"
        reduced = "实验03"
        
        result = evaluate_reduction_quality(original, reduced)
        
        # 完全相同的文本应该有高相似度
        self.assertEqual(result["reduction_rate"], 0.0)
        self.assertEqual(result["key_info_retention_rate"], 1.0)
        self.assertGreater(result["semantic_similarity"], 0.8)
    
    def test_high_reduction_rate(self):
        """测试高缩减率情况"""
        original = "请帮我查找一下关于实验03以及实验41的详细相关信息内容"
        reduced = "实验03、41"
        
        result = evaluate_reduction_quality(original, reduced)
        
        # 应该有较高的缩减率
        self.assertGreater(result["reduction_rate"], 0.5)
        # 关键信息应该基本保持
        self.assertGreater(result["key_info_retention_rate"], 0.5)
    
    def test_empty_inputs(self):
        """测试空输入处理"""
        # 空原文
        result = evaluate_reduction_quality("", "测试")
        for value in result.values():
            self.assertEqual(value, 0.0)

        # 空缩减文本（函数设计为空输入返回全0）
        result = evaluate_reduction_quality("测试", "")
        for value in result.values():
            self.assertEqual(value, 0.0)

        # 都为空
        result = evaluate_reduction_quality("", "")
        for value in result.values():
            self.assertEqual(value, 0.0)
    
    def test_key_info_retention(self):
        """测试关键信息保持率"""
        # 包含数字和公司名
        original = "广东腾讯科技有限公司的实验03项目"
        reduced = "腾讯科技实验03"

        result = evaluate_reduction_quality(original, reduced)

        # 关键信息（数字03、公司名腾讯科技）应该被保持
        self.assertGreaterEqual(result["key_info_retention_rate"], 0.5)


class TestBoundaryAndEdgeCases(unittest.TestCase):
    """边界情况和异常处理测试"""
    
    def test_special_characters(self):
        """测试特殊字符处理"""
        special_text = "测试@#$%^&*()文本123"
        result = advanced_simplify_question(special_text)
        self.assertIsInstance(result, str)
    
    def test_very_long_text(self):
        """测试超长文本处理"""
        long_text = "测试文本" * 100
        result = advanced_simplify_question(long_text)
        self.assertIsInstance(result, str)
        self.assertLessEqual(len(result), len(long_text))
    
    def test_unicode_characters(self):
        """测试Unicode字符处理"""
        unicode_text = "测试文本🚀📊💡"
        result = advanced_simplify_question(unicode_text)
        self.assertIsInstance(result, str)
    
    def test_mixed_language(self):
        """测试中英文混合文本"""
        mixed_text = "查找project ABC的实验data"
        result = advanced_simplify_question(mixed_text)
        self.assertIsInstance(result, str)


def run_comprehensive_test():
    """运行全面测试"""
    print("=" * 60)
    print("问题缩减功能专项测试")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestBasicReductionFunctions,
        TestAdvancedSimplifyQuestion,
        TestEvaluateReductionQuality,
        TestBoundaryAndEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果统计
    print("\n" + "=" * 60)
    print("测试结果统计:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
