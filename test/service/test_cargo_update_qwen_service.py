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
from src.service.qwen_service import generate_qwen_data, format_question_updateCargo
from src.service.cargo_update_service import generate_cargo_update_data

class TestCargoUpdateQwenService(unittest.TestCase):
    """
    货单更新千问服务测试类
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        self.business_object = 'updateCargo'
        self.sample_count = 5
        self.variations_per_rule = 2
    
    def test_format_question_updateCargo(self):
        """
        测试格式化updateCargo问题数据
        """
        print(f"\n======== 测试 updateCargo 问题格式化 ========")
        
        # 构造几个测试问题数据
        test_data = [
            {
                "操作": "对比以下送货单的件数，并计算附加费用",
                "项目": "盛和湾区大厦项目",
                "供应商": "耀皮供应商",
                "送货单号": "送货单号26012（1）、28018-7（2）、522001（26）、524021（5）"
            },
            {
                "操作": "对比以下送货单的重量，并计算附加费用",
                "项目": "正中科学园项目",
                "供应商": "贵州普恩林供应商",
                "送货单号": "送货单号FJ031-01（1300）、FJ024-01（12045）"
            },
            {
                "操作": "审核通过以下货单",
                "项目": "深圳湾超级总部基地项目",
                "供应商": "XX供应商",
                "对象单号": "单号ABC-123（100）"
            }
        ]
        
        # 测试每个数据的格式化结果
        for i, data in enumerate(test_data):
            formatted = format_question_updateCargo(data)
            print(f"\n测试数据 {i+1}:")
            print(f"  原始数据: {data}")
            print(f"  格式化结果: {formatted}")
            
            # 断言格式化结果不为空
            self.assertIsNotNone(formatted)
            self.assertNotEqual("", formatted)
            
            # 断言格式化结果包含关键数据
            for key, value in data.items():
                if isinstance(value, str) and value:
                    self.assertIn(value, formatted)
    
    def test_generate_updateCargo_qwen_data(self):
        """
        测试生成updateCargo的千问格式数据
        """
        print(f"\n======== 测试 updateCargo 千问数据生成 ({self.sample_count}条) ========")
        
        # 生成千问数据
        qwen_file, original_file = generate_qwen_data(
            self.business_object, self.sample_count, self.variations_per_rule
        )
        
        # 断言文件生成成功
        self.assertIsNotNone(qwen_file)
        self.assertTrue(os.path.exists(qwen_file))
        print(f"  生成的千问文件: {qwen_file}")
        
        # 断言原始数据文件生成成功
        self.assertIsNotNone(original_file)
        self.assertTrue(os.path.exists(original_file))
        print(f"  生成的原始文件: {original_file}")
        
        # 检查文件内容
        with open(qwen_file, 'r', encoding='utf-8') as f:
            qwen_lines = f.readlines()
            qwen_count = len(qwen_lines)
            print(f"  千问文件中包含 {qwen_count} 条记录")
            
            # 解析第一条记录并打印
            if qwen_count > 0:
                try:
                    first_record = json.loads(qwen_lines[0])
                    print("\n  示例记录:")
                    print(f"  用户输入: {first_record['messages'][0]['content']}")
                    print(f"  助手回答: {first_record['messages'][1]['content']}")
                except Exception as e:
                    print(f"  解析记录时出错: {e}")
        
        # 检查原始数据文件内容
        with open(original_file, 'r', encoding='utf-8') as f:
            try:
                original_data = json.load(f)
                print(f"\n  原始数据包含 {len(original_data)} 条记录")
                
                # 打印第一条记录
                if len(original_data) > 0:
                    print("\n  原始数据示例:")
                    print(f"  问题: {original_data[0]['question']}")
                    print(f"  答案: {original_data[0]['answer']}")
            except Exception as e:
                print(f"  解析原始数据时出错: {e}")

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