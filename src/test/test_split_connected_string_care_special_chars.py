#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 split_connected_string 函数的 care_special_chars 参数功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.service.common.connector_manager import split_connected_string

def test_care_special_chars_parameter():
    """
    测试 care_special_chars 参数的功能
    """
    print("=== 测试 care_special_chars 参数功能 ===\n")
    
    # 测试用例：包含特殊字符的字符串
    test_cases = [
        "FJ031-01（1300）、28018-7（2）",
        "孙洪（041501）、雷利冬、胡炽浩",
        "26012（1）、28018-7（2）、522001（26）",
        "孙洪(041501)、张三-001",
        "项目A-编号1、项目B-编号2"
    ]
    
    for i, test_string in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_string}")
        print("-" * 50)
        
        # 默认模式（care_special_chars=True）
        result_default = split_connected_string(test_string)
        print(f"默认模式 (care_special_chars=True):")
        print(f"  结果: {result_default}")
        print(f"  类型: {type(result_default[0]) if result_default else 'Empty'}")
        
        # 不关注特殊字符模式（care_special_chars=False）
        result_no_care = split_connected_string(test_string, care_special_chars=False)
        print(f"不关注特殊字符 (care_special_chars=False):")
        print(f"  结果: {result_no_care}")
        print(f"  类型: {type(result_no_care[0]) if result_no_care else 'Empty'}")
        
        print()

def test_edge_cases():
    """
    测试边界情况
    """
    print("=== 测试边界情况 ===\n")
    
    edge_cases = [
        ("", "空字符串"),
        ("纯汉字内容", "纯汉字，无特殊字符"),
        ("PureEnglishText", "纯英文，无特殊字符"),
        ("1234567890", "纯数字，无特殊字符"),
        ("项目A、项目B、项目C", "普通连接符，无特殊字符"),
        ("特殊符号!@#$%", "特殊符号但非目标特殊字符"),
    ]
    
    for test_string, description in edge_cases:
        print(f"测试: {description}")
        print(f"字符串: '{test_string}'")
        
        try:
            result_default = split_connected_string(test_string)
            result_no_care = split_connected_string(test_string, care_special_chars=False)
            
            print(f"  默认模式: {result_default}")
            print(f"  不关注特殊字符: {result_no_care}")
            print(f"  结果是否相同: {result_default == result_no_care}")
            
        except Exception as e:
            print(f"  错误: {e}")
        
        print()

def test_force_extract_numbers_with_care_special_chars():
    """
    测试 force_extract_numbers 与 care_special_chars 的组合
    """
    print("=== 测试 force_extract_numbers 与 care_special_chars 组合 ===\n")
    
    test_cases = [
        "吴慧敏(051703)、021137,081601",
        "文林101409向文静林桂涛",
        "FJ031ABC456DEF789",
        "12345、67890、13579"
    ]
    
    for test_string in test_cases:
        print(f"测试字符串: {test_string}")
        print("-" * 40)
        
        # 四种组合模式
        combinations = [
            (False, True, "普通模式 + 关注特殊字符"),
            (False, False, "普通模式 + 不关注特殊字符"),
            (True, True, "强制数字提取 + 关注特殊字符"),
            (True, False, "强制数字提取 + 不关注特殊字符")
        ]
        
        for force_extract, care_special, description in combinations:
            result = split_connected_string(
                test_string, 
                force_extract_numbers=force_extract, 
                care_special_chars=care_special
            )
            print(f"  {description}:")
            print(f"    结果: {result}")
            print(f"    类型: {type(result[0]) if result else 'Empty'}")
        
        print()

def test_backward_compatibility():
    """
    测试向后兼容性
    """
    print("=== 测试向后兼容性 ===\n")
    
    # 这些调用应该与之前的行为完全一致
    test_cases = [
        "雷利冬、胡炽浩",
        "项目A、项目B、项目C",
        "FJ031-01（1300）、28018-7（2）"
    ]
    
    for test_string in test_cases:
        print(f"测试字符串: {test_string}")
        
        # 旧的调用方式（不传 care_special_chars 参数）
        result_old_style = split_connected_string(test_string)
        
        # 新的调用方式（显式传 care_special_chars=True）
        result_new_style = split_connected_string(test_string, care_special_chars=True)
        
        print(f"  旧调用方式: {result_old_style}")
        print(f"  新调用方式: {result_new_style}")
        print(f"  结果一致: {result_old_style == result_new_style}")
        print()

def main():
    """
    主测试函数
    """
    print("开始测试 split_connected_string 的 care_special_chars 参数功能\n")
    
    test_care_special_chars_parameter()
    test_edge_cases()
    test_force_extract_numbers_with_care_special_chars()
    test_backward_compatibility()
    
    print("=== 测试完成 ===")
    print("\n功能说明:")
    print("1. care_special_chars=True (默认): 检测特殊字符，返回相应格式")
    print("2. care_special_chars=False: 跳过特殊字符检测，始终返回 List[str]")
    print("3. 保持向后兼容性，默认行为不变")
    print("4. 可与 force_extract_numbers 参数组合使用")

if __name__ == "__main__":
    main()
