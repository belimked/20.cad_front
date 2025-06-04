#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试千问服务功能
"""

from src.service.qwen_service import generate_qwen_data
import os
import json

def test_generate_qwen_data():
    """
    测试生成千问训练数据功能
    """
    print("开始测试千问服务...")
    
    try:
        # 生成searchStaff的千问训练数据，使用较小的样本数进行测试
        business_object = 'searchStaff'
        total_samples = 5
        variations_per_rule = 2
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        output_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证文件是否生成
        print(f"\n验证生成的文件: {output_file}")
        if os.path.exists(output_file):
            print(f"✓ 文件生成成功！")
            
            # 读取文件内容并验证格式
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"✓ 文件包含 {len(lines)} 条数据")
                
                # 检查第一条数据的格式
                if lines:
                    first_record = json.loads(lines[0])
                    
                    # 验证messages结构
                    if 'messages' in first_record and len(first_record['messages']) == 2:
                        print("✓ 数据格式正确，包含用户和助手消息")
                        
                        # 验证用户消息包含指令和问题
                        user_msg = first_record['messages'][0]
                        if user_msg['role'] == 'user' and '### 指令：' in user_msg['content'] and '### 查询问题' in user_msg['content']:
                            print("✓ 用户消息格式正确，包含指令和查询问题")
                        
                        # 验证助手消息是有效的JSON
                        assistant_msg = first_record['messages'][1]
                        if assistant_msg['role'] == 'assistant':
                            try:
                                answer_json = json.loads(assistant_msg['content'])
                                print("✓ 助手消息格式正确，包含有效的JSON响应")
                                print("\n示例数据:")
                                print(f"问题: {user_msg['content'].split('### 查询问题')[-1].strip()}")
                                print(f"答案: {assistant_msg['content']}")
                            except json.JSONDecodeError:
                                print("✗ 助手消息不是有效的JSON")
                    else:
                        print("✗ 数据格式不正确，缺少预期的消息结构")
        else:
            print(f"✗ 文件未生成: {output_file}")
    
    except Exception as e:
        import traceback
        print(f"\n测试过程中发生错误: {e}")
        traceback.print_exc()
    
    print("\n千问服务测试完成！")

if __name__ == "__main__":
    test_generate_qwen_data() 