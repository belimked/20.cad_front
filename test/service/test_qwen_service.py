#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试千问服务功能
"""

from src.service.qwen_service import generate_qwen_data
import os
import json

def test_generate_qwen_data_for_searchStaff():
    """
    测试生成searchStaff千问训练数据功能
    """
    print("开始测试searchStaff千问服务...")
    
    try:
        # 生成searchStaff的千问训练数据，使用较小的样本数进行测试
        business_object = 'searchStaff'
        total_samples = 5
        variations_per_rule = 1
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        if os.path.exists(qwen_file):
            print(f"✓ 千问文件生成成功！")
            
            # 验证文件内容
            with open(qwen_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data_count = len(lines)
                print(f"✓ 千问文件包含 {data_count} 条数据")
                
                # 检查第一条数据
                if lines:
                    first_data = json.loads(lines[0])
                    user_content = first_data.get('messages', [])[0].get('content', '')
                    assistant_content = first_data.get('messages', [])[1].get('content', '')
                    
                    print("\n示例数据:")
                    print(f"用户问题: {user_content.split('### 查询问题')[-1].strip()}")
                    print(f"助手回答: {assistant_content}")
                    
                    print("\n✓ 千问数据格式正确")
        else:
            print(f"✗ 千问文件生成失败！")
            
        # 验证原始格式文件是否生成
        print(f"\n验证生成的原始数据文件: {original_file}")
        if os.path.exists(original_file):
            print(f"✓ 原始数据文件生成成功！")
            
            # 验证文件内容
            with open(original_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_count = len(data)
                print(f"✓ 原始数据文件包含 {data_count} 条数据")
                
                # 检查第一条数据
                if data:
                    first_item = data[0]
                    question = first_item.get('question', {})
                    answer = first_item.get('answer', {})
                    
                    print("\n原始数据示例:")
                    print(f"问题数据: {question}")
                    print(f"答案数据: {answer}")
                    
                    print("\n✓ 原始数据格式正确")
        else:
            print(f"✗ 原始数据文件生成失败！")
    except Exception as e:
        import traceback
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        
def test_generate_qwen_data_for_updateStaff():
    """
    测试生成updateStaff千问训练数据功能
    """
    print("\n开始测试updateStaff千问服务...")
    
    try:
        # 生成updateStaff的千问训练数据，使用较小的样本数进行测试
        business_object = 'updateStaff'
        total_samples = 5
        variations_per_rule = 1
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        if os.path.exists(qwen_file):
            print(f"✓ 千问文件生成成功！")
            
            # 验证文件内容
            with open(qwen_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data_count = len(lines)
                print(f"✓ 千问文件包含 {data_count} 条数据")
                
                # 检查第一条数据
                if lines:
                    first_data = json.loads(lines[0])
                    user_content = first_data.get('messages', [])[0].get('content', '')
                    assistant_content = first_data.get('messages', [])[1].get('content', '')
                    
                    print("\n示例数据:")
                    print(f"用户问题: {user_content.split('### 查询问题')[-1].strip()}")
                    print(f"助手回答: {assistant_content}")
                    
                    print("\n✓ 千问数据格式正确")
        else:
            print(f"✗ 千问文件生成失败！")
            
        # 验证原始格式文件是否生成
        print(f"\n验证生成的原始数据文件: {original_file}")
        if os.path.exists(original_file):
            print(f"✓ 原始数据文件生成成功！")
            
            # 验证文件内容
            with open(original_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_count = len(data)
                print(f"✓ 原始数据文件包含 {data_count} 条数据")
                
                # 检查第一条数据
                if data:
                    first_item = data[0]
                    question = first_item.get('question', {})
                    answer = first_item.get('answer', {})
                    
                    print("\n原始数据示例:")
                    print(f"问题数据: {question}")
                    print(f"答案数据: {answer}")
                    
                    print("\n✓ 原始数据格式正确")
        else:
            print(f"✗ 原始数据文件生成失败！")
    except Exception as e:
        import traceback
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()

def test_generate_qwen_data_without_original():
    """
    测试生成千问训练数据但不生成原始数据的功能
    """
    print("\n开始测试不生成原始数据的千问服务...")
    
    try:
        # 生成searchStaff的千问训练数据，但不生成原始数据
        business_object = 'searchStaff'
        total_samples = 2
        variations_per_rule = 1
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种，且不生成原始数据...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule, save_original=False)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        if os.path.exists(qwen_file):
            print(f"✓ 千问文件生成成功！")
        else:
            print(f"✗ 千问文件生成失败！")
            
        # 验证原始数据文件应该为None
        print(f"\n验证原始数据文件是否为None: {original_file}")
        if original_file is None:
            print(f"✓ 原始数据文件为None，符合预期！")
        else:
            print(f"✗ 原始数据文件不为None，不符合预期！")
    except Exception as e:
        import traceback
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # 测试生成searchStaff的千问训练数据
    test_generate_qwen_data_for_searchStaff()
    
    # 测试生成updateStaff的千问训练数据
    test_generate_qwen_data_for_updateStaff()
    
    # 测试生成千问数据但不生成原始数据
    test_generate_qwen_data_without_original() 