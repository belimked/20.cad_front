#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService
import random
import re

class ContractSearchService(BaseGenerationService):
    """
    合同搜索服务类，用于根据规则生成合同搜索的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'searchContract'
    
    def __init__(self):
        """
        初始化合同搜索服务
        """
        super().__init__()
    
    def process_dict_replacement(self, element_name, current_value, dict_mapping, dict_item):
        """
        重写字典替换处理方法，增加对特定字典的处理
        
        Args:
            element_name: 元素名称
            current_value: 当前值
            dict_mapping: 字典映射
            dict_item: 字典项
            
        Returns:
            处理后的值，None表示未处理
        """
        # 首先调用父类方法，尝试基本处理
        result = super().process_dict_replacement(element_name, current_value, dict_mapping, dict_item)
        if result:
            return result
            
        # 处理业务单号字典（适用于contractNumber和materialCode）
        if 'businessNumbers' in dict_mapping and 'XX' in current_value:
            business_number = dict_item.get('number', "")
            if business_number:
                # 替换XX部分为业务单号
                new_value = current_value.replace('XX', business_number)
                print(f"替换业务单号: {element_name} 从 {current_value} 到 {new_value}")
                return new_value
                
        return None

    def extract_supplier_name(self, supplier_info: str) -> str:
        """
        从供应商信息中提取真正的供应商名称
        
        Args:
            supplier_info: 原始供应商信息字符串
            
        Returns:
            提取出的供应商名称
        """
        # 使用单一的正则表达式替换掉所有可能的前缀和后缀
        # 前缀: 供应商(是)? 或 厂家(是)? 或 是
        # 后缀: 的 或 供应商 或 厂家
        supplier = re.sub(r'^供应商(是)?|^厂家(是)?|(供应商|厂家|的)$|^是|(的)$', '', supplier_info)
        return supplier.strip()
        
    def generate_answer(self, question_data: Dict, answer_elements: Dict, base_elements: List) -> Dict:
        """
        重写生成答案数据的方法，处理静态值
        
        Args:
            question_data: 问题数据
            answer_elements: 回答元素数据
            base_elements: 基础元素数据列表
            
        Returns:
            答案数据
        """
        # 获取回答元素列表
        answer_elements_list = answer_elements.get('answerElements', [])
        
        # 过滤掉非字典对象，确保base_elements中的元素都是字典
        valid_base_elements = []
        for item in base_elements:
            if isinstance(item, dict):
                valid_base_elements.append(item)
            else:
                print(f"警告: base_elements中包含非字典元素: {item}")
        
        # 获取基础元素名称到数据的映射
        base_data_map = {item.get('name', ''): item for item in valid_base_elements if item.get('name')}
        
        # 存储生成的答案
        answer_data = {}
        
        # 调试信息：打印问题数据和基础元素
        print(f"\n生成答案数据 - 问题数据: {question_data}")
        print(f"有效基础元素: {valid_base_elements}")
        
        # 处理每个回答元素
        for element in answer_elements_list:
            element_name = element.get('name', '')
            is_static = element.get('isStatic', '否') == '是'
            
            print(f"\n处理回答元素: {element_name}, 是否静态: {is_static}")
            
            if is_static:
                # 如果是静态值，直接使用静态值
                static_value = element.get('staticValue', '')
                answer_data[element_name] = static_value
                print(f"  设置静态值: {static_value}")
            else:
                # 非静态值，关联到基础元素
                relate_to_base = element.get('relateToBase', '无')
                print(f"  关联到基础元素: {relate_to_base}")
                
                if relate_to_base != '无':
                    # 处理基础元素的关联
                    if '|' in relate_to_base:
                        # 多个可能的关联，选择第一个有值的
                        for relate_option in relate_to_base.split('|'):
                            if ',' in relate_option:
                                # 组合关联，需要多个基础元素都有值
                                base_element_nums = relate_option.split(',')
                                all_present = True
                                for base_element_num in base_element_nums:
                                    base_name = next((item.get('name') for item in valid_base_elements if item.get('number') == base_element_num), None)
                                    if not base_name or base_name not in question_data:
                                        all_present = False
                                        break
                                if all_present:
                                    # 组合值的处理逻辑，这里简化为用第一个值
                                    base_name = next((item.get('name') for item in valid_base_elements if item.get('number') == base_element_nums[0]), None)
                                    if base_name and base_name in question_data:
                                        answer_data[element_name] = question_data[base_name]
                                        print(f"  设置组合值(第一个): {question_data[base_name]}")
                                    break
                            else:
                                # 单个基础元素关联
                                base_name = next((item.get('name') for item in valid_base_elements if item.get('number') == relate_option), None)
                                if base_name and base_name in question_data:
                                    answer_data[element_name] = question_data[base_name]
                                    print(f"  设置单个值(多选一): {question_data[base_name]}")
                                    break
                    else:
                        # 单个基础元素关联
                        if ',' in relate_to_base:
                            # 组合关联
                            base_elements_list = relate_to_base.split(',')
                            base_names = []
                            for base_element in base_elements_list:
                                base_name = next((item.get('name') for item in valid_base_elements if item.get('number') == base_element), None)
                                if base_name and base_name in question_data:
                                    base_names.append(question_data[base_name])
                            if base_names:
                                answer_data[element_name] = " ".join(base_names)
                                print(f"  设置组合值: {' '.join(base_names)}")
                        else:
                            # 单个基础元素
                            base_name = next((item.get('name') for item in valid_base_elements if item.get('number') == relate_to_base), None)
                            print(f"  查找基础元素: 编号={relate_to_base}, 名称={base_name}")
                            
                            if base_name and base_name in question_data:
                                # 特殊处理supplier字段
                                if element_name == "supplier" and base_name == "supplierInfo":
                                    supplier_info = question_data[base_name]
                                    print(f"处理supplier字段，原始值: '{supplier_info}'")
                                    
                                    # 检查supplierInfo是否包含"XX"占位符
                                    if "XX" in supplier_info:
                                        # 在测试数据生成时，我们可以使用一些模拟的供应商名称
                                        mock_suppliers = [
                                            "湖南装饰材料有限公司", 
                                            "安徽五金制品有限公司",
                                            "泰山石材有限公司", 
                                            "佛山陶瓷有限公司",
                                            "长沙水泥制品有限公司",
                                            "云南铝材有限公司", 
                                            "南京混凝土制品有限公司"
                                        ]
                                        # 随机选择一个供应商替换XX
                                        mock_supplier = random.choice(mock_suppliers)
                                        supplier_info = supplier_info.replace("XX", mock_supplier)
                                        print(f"  将XX替换为模拟供应商: '{mock_supplier}'")
                                    
                                    # 从supplierInfo中提取供应商名称
                                    supplier = self.extract_supplier_name(supplier_info)
                                    print(f"  最终提取的供应商名称: '{supplier}'")
                                    
                                    # 如果提取的供应商名为空，打印警告
                                    if not supplier:
                                        print(f"警告: 从'{supplier_info}'中提取供应商名称失败")
                                    
                                    answer_data[element_name] = supplier
                                else:
                                    answer_data[element_name] = question_data[base_name]
                                    print(f"  设置普通值: {question_data[base_name]}")
                            else:
                                print(f"  未找到对应的基础元素或问题数据中不存在该字段")
            
            # 如果没有设置值，默认为空字符串
            if element_name not in answer_data:
                answer_data[element_name] = ""
                print(f"  未设置值，使用默认空字符串")
        
        print(f"\n生成的答案数据: {answer_data}")
        return answer_data
    
    def generate_contract_search_data(self, business_object: str = BUSINESS_OBJECT, 
                                   total_samples: int = 200, 
                                   variations_per_rule: int = 2) -> List[Dict]:
        """
        生成合同搜索数据
        
        Args:
            business_object: 业务对象名称，默认为searchContract
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)

    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        重写为一个规则生成多个变种数据的方法，确保使用ContractSearchService的generate_answer方法
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            answer_elements: 回答元素数据
            num_variations: 变种数量，默认2
            
        Returns:
            变种数据列表
        """
        variations = []
        
        # 生成指定数量的变种
        for _ in range(num_variations):
            # 生成问题数据
            question_data = self.generate_question(rule, base_elements)
            
            # 获取基础元素列表
            base_data_list = base_elements.get('baseDataList', [])
            
            # 生成答案数据 - 使用ContractSearchService的generate_answer方法
            answer_data = self.generate_answer(question_data, answer_elements, base_data_list)
            
            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', '')
            })
        
        return variations

# 获取服务实例的便捷函数
get_contract_search_service = ContractSearchService.get_instance

# 便捷方法，使用create_specific_generator创建
generate_contract_search_data = BaseGenerationService.create_specific_generator(
    ContractSearchService, 
    'generate_contract_search_data', 
    ContractSearchService.BUSINESS_OBJECT
)

# 使用示例
if __name__ == "__main__":
    try:
        # 直接测试正则表达式处理供应商信息
        test_suppliers = [
            "供应商湖南装饰材料有限公司",
            "湖南装饰材料有限公司供应商",
            "湖南装饰材料有限公司的",
            "供应商是湖南装饰材料有限公司",
            "湖南装饰材料有限公司厂家",
            "厂家湖南装饰材料有限公司",
            "是湖南装饰材料有限公司的",
            "湖南装饰材料有限公司",  # 纯名称
            "供应商是安徽五金制品有限公司的"  # 添加一个带"的"后缀的测试用例
        ]
        
        print("\n=== 供应商名称提取测试 ===")
        service = ContractSearchService()
        for i, supplier_info in enumerate(test_suppliers):
            print(f"\n测试 {i+1}: '{supplier_info}'")
            supplier = service.extract_supplier_name(supplier_info)
            print(f"  提取结果: '{supplier}'")
        
        # 生成searchContract的合同搜索数据
        contract_search_data = generate_contract_search_data(total_samples=10, variations_per_rule=2)
        print(f"\n生成的数据数量: {len(contract_search_data)}")
        
        # 打印第一条数据
        if contract_search_data:
            print("\n示例数据:")
            print(f"问题: {contract_search_data[0]['question']}")
            print(f"答案: {contract_search_data[0]['answer']}")
            
            # 检查是否有包含supplierInfo的数据
            for item in contract_search_data:
                if 'supplierInfo' in item['question']:
                    print(f"\n包含supplierInfo的数据:")
                    print(f"问题 supplierInfo: {item['question']['supplierInfo']}")
                    print(f"答案 supplier: {item['answer']['supplier']}")
                    break
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 