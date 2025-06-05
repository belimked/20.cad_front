#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
import random
import math
from src.service.rule_logic import get_rule_components, get_sorted_rules
from src.service.common.base_generation_service import BaseGenerationService

class StaffUpdateService(BaseGenerationService):
    """
    人员安排更新服务类，用于根据规则生成人员安排更新的问题和答案
    继承自BaseGenerationService基础类
    """
    
    def __init__(self):
        """
        初始化人员安排更新服务
        """
        super().__init__()
    
    def process_special_elements(self, question_data: Dict, elements_with_dict: Dict) -> Dict:
        """
        重写特殊元素处理方法，处理字典替换逻辑
        
        Args:
            question_data: 问题数据
            elements_with_dict: 需要特殊处理的元素
            
        Returns:
            处理后的问题数据
        """
        # 处理需要字典替换的元素
        for element_name, data in elements_with_dict.items():
            element = data['element']
            dict_list = data['dict_list']
            
            # 目前值，可能包含XX占位符
            current_value = question_data.get(element_name, "")
            
            # 遍历字典列表
            for dict_mapping in dict_list:
                from src.service.common import get_dict_by_element_mapping
                
                # 获取字典数据
                dict_data = get_dict_by_element_mapping(dict_mapping, 1, True)
                if dict_data and len(dict_data) > 0:
                    dict_item = dict_data[0]
                    
                    # 针对项目字典处理
                    if 'projects' in dict_mapping and 'XX' in current_value:
                        project_name = dict_item.get('projectname', "")
                        if project_name:
                            # 替换XX为实际项目名称
                            new_value = current_value.replace('XX', project_name)
                            question_data[element_name] = new_value
                            print(f"替换字典数据: {element_name} 从 {current_value} 到 {new_value}")
                    
                    # 针对其他字典类型的处理可以在这里添加
        
        return question_data
    
    def generate_staff_update_data(self, business_object: str, total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """
        生成人员安排更新数据
        
        Args:
            business_object: 业务对象名称，如 updateStaff
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)

# 单例模式
_instance = None

def get_staff_update_service() -> StaffUpdateService:
    """
    获取人员安排更新服务的单例实例
    
    Returns:
        StaffUpdateService实例
    """
    global _instance
    if _instance is None:
        _instance = StaffUpdateService()
    return _instance

# 便捷方法
def generate_staff_update_data(business_object: str, total_samples: int = 10, 
                         variations_per_rule: int = 2) -> List[Dict]:
    """
    生成人员安排更新数据的便捷方法
    
    Args:
        business_object: 业务对象名称，如 updateStaff
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数量，默认2
        
    Returns:
        生成的数据列表
    """
    return get_staff_update_service().generate_staff_update_data(
        business_object, total_samples, variations_per_rule
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成updateStaff的人员安排更新数据
        staff_update_data = generate_staff_update_data('updateStaff', 10, 2)
        print(f"\n生成的数据数量: {len(staff_update_data)}")
        
        # 打印第一条数据
        if staff_update_data:
            print("\n示例数据:")
            print(f"问题: {staff_update_data[0]['question']}")
            print(f"答案: {staff_update_data[0]['answer']}")
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 