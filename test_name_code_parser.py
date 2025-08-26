#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试姓名工号解析功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.service.common.connector_manager import ConnectorManager

def test_name_code_formats():
    """测试四种姓名工号格式的解析"""
    
    manager = ConnectorManager()
    
    print("=== 姓名工号格式解析测试 ===\n")
    
    # 测试用例：四种不同格式
    test_cases = [
        # 格式1：姓名（工号）
        "吴慧敏（051703）",
        
        # 格式2：（工号）姓名  
        "（051703）吴慧敏",
        
        # 格式3：工号-姓名
        "051703-吴慧敏",
        
        # 格式4：姓名-工号
        "吴慧敏-051703",
        
        # 英文括号格式
        "吴慧敏(051703)",
        
        # 复杂工号格式
        "张三（FJ051703）",
        "李四-ABC123",
        "王五（2024001）",
        
        # 边界情况
        "纯姓名",
        "123456",
        "混合ABC123内容",
    ]
    
    print("1. 单个格式解析测试：")
    for i, test_case in enumerate(test_cases, 1):
        result = manager._parse_and_format_item(test_case)
        print(f"  测试{i}: {test_case}")
        print(f"  结果: {result.replace(chr(10), ' | ')}")  # 将换行符替换为 | 便于显示
        print()
    
    print("\n2. 连接字符串拆分测试：")

    # 测试连接字符串的拆分
    connected_test_cases = [
        "吴慧敏（051703）、张三-ABC123、李四(2024001)",
        "（051703）吴慧敏，张三-ABC123",
        "吴慧敏-051703、李四（2024001）、王五-FJ123",
    ]

    for i, test_case in enumerate(connected_test_cases, 1):
        print(f"  连接测试{i}: {test_case}")
        result = manager.split_and_format_names(test_case)
        print(f"  拆分结果:")
        for j, item in enumerate(result):
            print(f"    项目{j+1}: {item.replace(chr(10), ' | ')}")
        print()

if __name__ == "__main__":
    test_name_code_formats()
