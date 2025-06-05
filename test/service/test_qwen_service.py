#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试千问服务功能
"""

from src.service.qwen_service import generate_qwen_data
from src.service.common.config import ConfigService
import os
import json
from datetime import datetime
import traceback

# 获取配置服务实例
config_service = ConfigService()

# 定义QwenFormatConverter类
class QwenFormatConverter:
    """
    将原始数据格式转换为千问训练数据格式的转换器
    """
    
    def convert_data_to_qwen(self, data_list, business_object):
        """
        将原始数据转换为千问格式
        
        Args:
            data_list: 原始数据列表
            business_object: 业务对象类型
            
        Returns:
            转换后的千问格式数据列表
        """
        qwen_data = []
        
        for item in data_list:
            question_data = item.get('question', {})
            answer_data = item.get('answer', {})
            
            # 构建用户问题文本
            if isinstance(question_data, dict) and 'text' in question_data:
                user_content = f"### 查询问题\n{question_data.get('text', '')}"
            else:
                # 对于searchContract等业务对象，问题数据直接是字典形式，需要转换
                question_str = " ".join([f"{k}：{v}" for k, v in question_data.items() if v])
                user_content = f"### 查询问题\n{question_str}"
            
            # 构建助手回答文本
            if isinstance(answer_data, dict) and 'text' in answer_data:
                assistant_content = answer_data.get('text', '')
            else:
                # 对于searchContract等业务对象，回答数据直接是字典形式，需要转换
                # 只包含非空的字段
                answer_elements = [f"{k}：{v}" for k, v in answer_data.items() if v]
                assistant_content = "\n".join(answer_elements) if answer_elements else "未找到符合条件的数据"
            
            # 创建千问格式数据项
            qwen_item = {
                "messages": [
                    {"role": "user", "content": user_content},
                    {"role": "assistant", "content": assistant_content}
                ]
            }
            
            qwen_data.append(qwen_item)
            
        return qwen_data

# 验证功能函数
def verify_qwen_file(file_path):
    """
    验证生成的千问格式文件
    
    Args:
        file_path: 文件路径
    """
    if os.path.exists(file_path):
        print(f"✓ 千问文件生成成功！")
        
        # 验证文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
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

def verify_original_file(file_path, business_object):
    """
    验证生成的原始数据文件
    
    Args:
        file_path: 文件路径
        business_object: 业务对象类型
    """
    if os.path.exists(file_path):
        print(f"✓ 原始数据文件生成成功！")
        
        # 验证文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_count = len(data)
            print(f"✓ 原始数据文件包含 {data_count} 条数据")
            
            # 检查第一条数据
            if data:
                first_item = data[0]
                question = first_item.get('question', {})
                answer = first_item.get('answer', {})
                
                print("\n原始数据示例:")
                print(f"业务类型: {business_object}")
                print(f"问题数据: {question}")
                print(f"答案数据: {answer}")
                
                print("\n✓ 原始数据格式正确")
    else:
        print(f"✗ 原始数据文件生成失败！")

def test_generate_qwen_data_for_searchStaff():
    """
    测试生成searchStaff千问训练数据功能
    """
    print("开始测试searchStaff千问服务...")
    
    try:
        # 生成searchStaff的千问训练数据，使用配置文件中的参数
        business_object = 'searchStaff'
        params = config_service.get_test_params(business_object)
        total_samples = params.get('total_samples', 50)
        variations_per_rule = params.get('variations_per_rule', 10)
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        verify_qwen_file(qwen_file)
        
        # 验证原始格式文件是否生成
        print(f"\n验证生成的原始数据文件: {original_file}")
        verify_original_file(original_file, business_object)
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()
        
def test_generate_qwen_data_for_updateStaff():
    """
    测试生成updateStaff千问训练数据功能
    """
    print("\n开始测试updateStaff千问服务...")
    
    try:
        # 生成updateStaff的千问训练数据，使用配置文件中的参数
        business_object = 'updateStaff'
        params = config_service.get_test_params(business_object)
        total_samples = params.get('total_samples', 5)
        variations_per_rule = params.get('variations_per_rule', 1)
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        verify_qwen_file(qwen_file)
        
        # 验证原始格式文件是否生成
        print(f"\n验证生成的原始数据文件: {original_file}")
        verify_original_file(original_file, business_object)
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()

def test_generate_qwen_data_for_updateCargo():
    """
    测试生成updateCargo千问训练数据功能
    """
    print("\n开始测试updateCargo千问服务...")
    
    try:
        # 生成updateCargo的千问训练数据，使用配置文件中的参数
        business_object = 'updateCargo'
        params = config_service.get_test_params(business_object)
        total_samples = params.get('total_samples', 5)
        variations_per_rule = params.get('variations_per_rule', 1)
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        verify_qwen_file(qwen_file)
        
        # 验证原始格式文件是否生成
        print(f"\n验证生成的原始数据文件: {original_file}")
        verify_original_file(original_file, business_object)
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()

def test_generate_qwen_data_without_original():
    """
    测试生成千问训练数据但不生成原始数据的功能
    """
    print("\n开始测试不生成原始数据的千问服务...")
    
    try:
        # 生成searchStaff的千问训练数据，但不生成原始数据，使用配置文件中的参数
        business_object = 'searchStaff'
        params = config_service.get_no_original_test_params()
        total_samples = params.get('total_samples', 2)
        variations_per_rule = params.get('variations_per_rule', 1)
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种，且不生成原始数据...")
        qwen_file, original_file = generate_qwen_data(business_object, total_samples, variations_per_rule, save_original=False)
        
        # 验证qwen格式文件是否生成
        print(f"\n验证生成的千问格式文件: {qwen_file}")
        verify_qwen_file(qwen_file)
        
        # 验证原始数据文件应该为None
        print(f"\n验证原始数据文件是否为None: {original_file}")
        if original_file is None:
            print(f"✓ 原始数据文件为None，符合预期！")
        else:
            print(f"✗ 原始数据文件不为None，不符合预期！")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        traceback.print_exc()

def test_generate_qwen_data_for_searchContract():
    """
    测试生成searchContract类型的千问格式数据
    """
    print("\n开始生成searchContract千问格式数据...")
    
    # 获取配置服务实例
    config_service = ConfigService()
    
    # 获取配置参数
    business_object = 'searchContract'
    params = config_service.get_test_params(business_object)
    total_samples = params.get('total_samples', 50)
    variations_per_rule = params.get('variations_per_rule', 10)
    
    # 使用contract_search_service生成数据
    from src.service.contract_search_service import generate_contract_search_data
    
    try:
        # 生成数据
        original_data = generate_contract_search_data(total_samples=total_samples, variations_per_rule=variations_per_rule)
        
        # 调试信息：检查supplier字段
        supplier_fields = [item.get('answer', {}).get('supplier', '') for item in original_data]
        non_empty_supplier_count = sum(1 for s in supplier_fields if s)
        print(f"\n生成的原始数据中:")
        print(f"总数据条数: {len(original_data)}")
        print(f"非空supplier字段数: {non_empty_supplier_count}")
        print(f"空supplier字段数: {len(original_data) - non_empty_supplier_count}")
        
        # 检查supplierInfo字段
        supplier_info_fields = [item.get('question', {}).get('supplierInfo', '') for item in original_data]
        has_supplier_info_count = sum(1 for s in supplier_info_fields if s)
        print(f"supplierInfo字段存在的数据条数: {has_supplier_info_count}")
        
        # 打印第一个带有supplierInfo的样例
        if has_supplier_info_count > 0:
            for i, item in enumerate(original_data):
                if item.get('question', {}).get('supplierInfo', ''):
                    print("\n样例数据:")
                    print(f"问题: {item['question']}")
                    print(f"回答: {item['answer']}")
                    print(f"supplierInfo: {item['question'].get('supplierInfo', '')}")
                    print(f"supplier: {item['answer'].get('supplier', '')}")
                    break
        
        # 将数据转换为千问格式并保存
        converter = QwenFormatConverter()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 定义输出路径
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(root_dir, 'outputs', 'data')
        
        # 确保输出目录存在
        os.makedirs(os.path.join(output_dir, 'qwen'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'original'), exist_ok=True)
        
        # 临时保存原始数据
        original_file_path = os.path.join(output_dir, 'original', f'{business_object}_{total_samples}_{timestamp}.json')
        with open(original_file_path, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, ensure_ascii=False, indent=4)
        print("原始数据已临时保存")
        
        # 转换为千问格式并保存
        qwen_data_path = os.path.join(output_dir, 'qwen', f'{business_object}_{total_samples}_{timestamp}.jsonl')
        converted_data = converter.convert_data_to_qwen(original_data, business_object)
        
        with open(qwen_data_path, 'w', encoding='utf-8') as f:
            for item in converted_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # 重命名文件以反映实际数据量
        actual_count = len(original_data)
        new_qwen_file_path = os.path.join(output_dir, 'qwen', f'{business_object}_{actual_count}_{timestamp}.jsonl')
        new_original_file_path = os.path.join(output_dir, 'original', f'{business_object}_{actual_count}_{timestamp}.json')
        
        os.rename(qwen_data_path, new_qwen_file_path)
        os.rename(original_file_path, new_original_file_path)
        
        print(f"写入了 {actual_count} 条记录到千问格式文件")
        print(f"文件已重命名为反映实际数据量: {os.path.basename(new_qwen_file_path)}")
        print(f"原始数据文件已重命名为反映实际数据量: {os.path.basename(new_original_file_path)}")
        print(f"千问格式数据已保存到 {new_qwen_file_path}")
        
        # 验证生成的千问格式数据
        print(f"\n验证生成的千问格式文件: {new_qwen_file_path}")
        verify_qwen_file(new_qwen_file_path)
        
        # 验证生成的原始数据
        print(f"\n验证生成的原始数据文件: {new_original_file_path}")
        verify_original_file(new_original_file_path, business_object)
        
        print("测试数据生成完成！")
        
    except Exception as e:
        print(f"生成千问格式数据时出错: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # 测试生成searchStaff的千问训练数据
    test_generate_qwen_data_for_searchStaff()
    
    # 测试生成updateStaff的千问训练数据
    test_generate_qwen_data_for_updateStaff()
    
    # 测试生成updateCargo的千问训练数据
    test_generate_qwen_data_for_updateCargo()
    
    # 测试生成千问数据但不生成原始数据
    test_generate_qwen_data_without_original()
    
    # 测试生成searchContract类型的千问格式数据
    test_generate_qwen_data_for_searchContract() 