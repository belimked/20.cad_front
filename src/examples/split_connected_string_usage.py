#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
split_connected_string 函数使用示例
演示 care_special_chars 参数的用法
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.service.common.connector_manager import split_connected_string

def main():
    """
    演示 split_connected_string 函数的各种用法
    """
    print("=== split_connected_string 函数使用示例 ===\n")
    
    # 示例1：包含特殊字符的字符串
    print("1. 包含特殊字符的字符串处理")
    print("-" * 40)
    
    text1 = "FJ031-01（1300）、28018-7（2）"
    print(f"原字符串: {text1}")
    
    # 默认模式：关注特殊字符
    result1_default = split_connected_string(text1)
    print(f"默认模式 (care_special_chars=True): {result1_default}")
    print(f"返回类型: List[Dict[str, str]]")
    
    # 不关注特殊字符模式
    result1_no_care = split_connected_string(text1, care_special_chars=False)
    print(f"不关注特殊字符 (care_special_chars=False): {result1_no_care}")
    print(f"返回类型: List[str]")
    print()
    
    # 示例2：不包含特殊字符的字符串
    print("2. 不包含特殊字符的字符串处理")
    print("-" * 40)
    
    text2 = "雷利冬、胡炽浩、张三"
    print(f"原字符串: {text2}")
    
    # 两种模式结果相同
    result2_default = split_connected_string(text2)
    result2_no_care = split_connected_string(text2, care_special_chars=False)
    print(f"默认模式: {result2_default}")
    print(f"不关注特殊字符: {result2_no_care}")
    print(f"结果相同: {result2_default == result2_no_care}")
    print()
    
    # 示例3：与 force_extract_numbers 参数组合使用
    print("3. 与 force_extract_numbers 参数组合使用")
    print("-" * 40)
    
    text3 = "吴慧敏(051703)、021137,081601"
    print(f"原字符串: {text3}")
    
    # 四种组合
    combinations = [
        (False, True, "普通模式 + 关注特殊字符"),
        (False, False, "普通模式 + 不关注特殊字符"),
        (True, True, "强制数字提取 + 关注特殊字符"),
        (True, False, "强制数字提取 + 不关注特殊字符")
    ]
    
    for force_extract, care_special, description in combinations:
        result = split_connected_string(
            text3, 
            force_extract_numbers=force_extract, 
            care_special_chars=care_special
        )
        print(f"{description}: {result}")
    print()
    
    # 示例4：实际应用场景
    print("4. 实际应用场景")
    print("-" * 40)
    
    # 场景1：需要解析名称和编号
    scenario1 = "项目A-001（重要）、项目B-002（普通）"
    print(f"场景1 - 项目管理: {scenario1}")
    result_parsed = split_connected_string(scenario1)
    print(f"解析结果: {result_parsed}")
    for i, item in enumerate(result_parsed):
        print(f"  项目{i+1}: 名称='{item['name']}', 编号='{item['code']}'")
    print()
    
    # 场景2：只需要简单分割
    scenario2 = "项目A-001（重要）、项目B-002（普通）"
    print(f"场景2 - 简单分割: {scenario2}")
    result_simple = split_connected_string(scenario2, care_special_chars=False)
    print(f"分割结果: {result_simple}")
    for i, item in enumerate(result_simple):
        print(f"  项目{i+1}: '{item}'")
    print()
    
    # 示例5：性能对比（当不需要解析特殊字符时）
    print("5. 性能优化建议")
    print("-" * 40)
    print("当你只需要简单分割字符串，不需要解析特殊字符时：")
    print("- 使用 care_special_chars=False 可以跳过特殊字符检测")
    print("- 始终返回 List[str] 格式，处理更简单")
    print("- 避免不必要的字符解析，提高性能")
    print()
    
    print("=== 使用建议 ===")
    print("1. 默认情况下使用 care_special_chars=True（默认值）")
    print("2. 当确定不需要解析特殊字符时，设置 care_special_chars=False")
    print("3. 可以与 force_extract_numbers 参数组合使用")
    print("4. 保持向后兼容性，现有代码无需修改")

if __name__ == "__main__":
    main()
