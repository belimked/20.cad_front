#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import unittest
import random
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 导入被测试模块
from src.service.cargo_update_service import generate_cargo_update_data, get_cargo_update_service

class TestCargoUpdateService(unittest.TestCase):
    """
    货单更新服务测试类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.business_object = 'updateCargo'
        self.sample_count = 5
        self.variations_per_rule = 2
    
    def test_generate_cargo_update_data(self):
        """
        测试生成货单更新数据
        """
        print(f"\n======== 测试 updateCargo 业务对象数据生成 ({self.sample_count}条) ========")
        
        # 生成数据
        cargo_data = generate_cargo_update_data(
            self.business_object, self.sample_count, self.variations_per_rule
        )
        
        # 断言数据不为空
        self.assertIsNotNone(cargo_data)
        print(f"  生成数据条数: {len(cargo_data)}")
        
        # 断言数据格式正确
        for i, data in enumerate(cargo_data):
            self.assertIn('question', data)
            self.assertIn('answer', data)
            
            # 打印第一条数据作为示例
            if i == 0:
                print(f"\n  示例问题: {data['question']}")
                print(f"  示例答案: {data['answer']}")
    
    def test_cargo_update_special_processing(self):
        """
        测试货单更新服务中的特殊元素处理
        """
        print(f"\n======== 测试 updateCargo 特殊元素处理 ========")
        
        # 生成一条测试数据
        cargo_data = generate_cargo_update_data(
            self.business_object, 1, 1
        )
        
        # 断言数据不为空
        self.assertIsNotNone(cargo_data)
        self.assertGreater(len(cargo_data), 0)
        
        # 获取第一条数据
        test_data = cargo_data[0]
        
        # 检查特定字段是否存在
        self.assertIn('question', test_data)
        self.assertIn('answer', test_data)
        
        # 打印数据内容
        print(f"\n  问题数据: {test_data['question']}")
        print(f"  答案数据: {test_data['answer']}")
        
        # 检查项目和供应商字段是否存在且不含XX
        if '项目' in test_data['question']:
            self.assertNotIn('项目XX', test_data['question'])
        
        if '供应商' in test_data['question']:
            self.assertNotIn('供应商XX', test_data['question'])

def main():
    # 运行所有测试
    unittest.main()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 