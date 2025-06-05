#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.rule_logic import get_rule_components

class MaterialService(BaseGenerationService):
    """
    材料服务类，用于根据规则生成材料查询的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'searchMaterial'
    
    def __init__(self):
        """
        初始化材料服务
        """
        super().__init__()
    
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据，增加对材料查询特定字段的处理
        
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
            
            # 生成答案数据
            answer_data = self.generate_answer(question_data, answer_elements, base_elements)
            
            # 设置object字段为固定值
            answer_data['object'] = "材料"
            
            # 设置operation字段为固定值"查询"
            answer_data['operation'] = "查询"
            
            # 特殊处理：确保materialCode字段映射
            if 'materialCode' in question_data:
                answer_data['materialCode'] = question_data['materialCode']
            
            # 特殊处理：确保materialType字段映射
            if 'materialType' in question_data:
                answer_data['materialType'] = question_data['materialType']
            
            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', '')
            })
        
        return variations
    
    def post_process_data(self, data: List[Dict], business_object: str) -> List[Dict]:
        """
        对生成的数据进行后处理，处理材料查询的特定业务逻辑
        
        Args:
            data: 生成的数据列表
            business_object: 业务对象名称
            
        Returns:
            处理后的数据列表
        """
        # 获取回答元素定义
        _, _, answer_elements = get_rule_components(business_object)
        
        # 对每条数据应用材料查询特定的字段填充逻辑
        for item in data:
            # 设置通用字段
            item['answer']['operation'] = "查询"
            item['answer']['object'] = "材料"
            
            # 处理关联字段
            for element in answer_elements.get('answerElements', []):
                element_name = element.get('name')
                # 关联字段处理
                if element.get('relateToBase') != "无":
                    base_number = element.get('relateToBase')
                    # 特殊处理materialCode字段
                    if element_name == 'materialCode' and 'materialCode' in item['question']:
                        item['answer'][element_name] = item['question']['materialCode']
                    # 特殊处理materialType字段
                    elif element_name == 'materialType' and 'materialType' in item['question']:
                        item['answer'][element_name] = item['question']['materialType']
                    # 特殊处理materialProcessDrawing字段（材料工艺图查询的情况）
                    elif element_name == 'materialProcessDrawing' and 'materialProcessQuery' in item['question']:
                        item['answer'][element_name] = "材料工艺图链接: https://example.com/drawings/123"  # 示例值
            
            # 根据问题类型设置特定字段
            if 'materialStatusQuery' in item['question']:
                # 材料状态查询，确保materialStatus字段有值
                if not item['answer'].get('materialStatus') and 'materialCode' in item['question']:
                    item['answer']['materialStatus'] = "已入库"  # 示例值
            
            if 'materialPropertyQuery' in item['question']:
                # 材料属性查询，确保materialEngineeringProperties字段有值
                if not item['answer'].get('materialEngineeringProperties') and 'materialCode' in item['question']:
                    item['answer']['materialEngineeringProperties'] = "厚度:2mm,宽度:1m,长度:2m"  # 示例值
        
        return data
    
    def generate_material_data(self, business_object: str = BUSINESS_OBJECT, 
                              total_samples: int = 200, 
                              variations_per_rule: int = 2,
                              variation_service = None) -> List[Dict]:
        """
        生成材料查询数据
        
        Args:
            business_object: 业务对象名称，默认为searchMaterial
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            
        Returns:
            生成的数据列表
        """
        # 调用基类的通用方法
        return self.generate_business_data(business_object, total_samples, variations_per_rule, variation_service)


# 获取服务实例的便捷函数
get_material_service = MaterialService.get_instance

# 便捷方法，使用变种生成服务创建
def generate_material_data(business_object: str = MaterialService.BUSINESS_OBJECT, 
                          total_samples: int = 10, 
                          variations_per_rule: int = 2) -> List[Dict]:
    """
    生成材料查询数据
    
    Args:
        business_object: 业务对象名称，默认为searchMaterial
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    variation_service = GenerationServiceFactory.create_variation_service()
    material_service = get_material_service()
    
    # 调用生成方法，传递变种服务实例
    return material_service.generate_material_data(
        business_object, 
        total_samples, 
        variations_per_rule,
        variation_service  # 传递变种服务实例
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchMaterial的材料查询数据
        material_data = generate_material_data(total_samples=10, variations_per_rule=2)
        print(f"\n生成的数据数量: {len(material_data)}")
        
        # 打印第一条数据
        if material_data:
            print("\n示例数据:")
            print(f"问题: {material_data[0]['question']}")
            print(f"答案: {material_data[0]['answer']}")
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 