#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any
from src.service.common import (
    get_base_elements, get_available_base_elements,
    get_answer_elements, get_available_answer_elements,
    get_business_rules, get_available_business_rules
)

class RuleLogicService:
    """
    规则逻辑服务类，用于整合基础元素、回答元素和业务规则数据，
    并提供按规则复杂度排序等功能
    """
    
    def __init__(self):
        """
        初始化规则逻辑服务
        """
        pass
    
    def get_rule_components(self, business_object: str) -> Tuple[Dict, Dict, Dict]:
        """
        获取指定业务对象的三个数据集合：基础元素、业务规则和回答元素
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            包含三个数据集合的元组：(基础元素, 业务规则, 回答元素)
        """
        # 获取基础元素数据
        base_elements_data = get_base_elements(business_object)
        
        # 获取业务规则数据
        business_rules_data = get_business_rules(f"{business_object}Rules")
        
        # 获取回答元素数据
        answer_elements_data = get_answer_elements(business_object)
        
        return (base_elements_data, business_rules_data, answer_elements_data)
    
    def get_sorted_rules(self, business_object: str) -> List[Dict]:
        """
        获取按codecount排序的规则集合
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            按codecount降序排列的规则列表
        """
        # 获取业务规则数据
        business_rules_data = get_business_rules(f"{business_object}Rules")
        
        # 提取规则列表
        rules = business_rules_data.get('rulesMap', [])
        
        # 按codecount降序排序
        sorted_rules = sorted(rules, key=lambda x: x.get('codecount', 0), reverse=True)
        
        return sorted_rules

# 单例模式
_instance = None

def get_rule_logic_service() -> RuleLogicService:
    """
    获取规则逻辑服务的单例实例
    
    Returns:
        RuleLogicService实例
    """
    global _instance
    if _instance is None:
        _instance = RuleLogicService()
    return _instance

# 便捷方法
def get_rule_components(business_object: str) -> Tuple[Dict, Dict, Dict]:
    """
    获取指定业务对象的三个数据集合的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        包含三个数据集合的元组：(基础元素, 业务规则, 回答元素)
    """
    return get_rule_logic_service().get_rule_components(business_object)

def get_sorted_rules(business_object: str) -> List[Dict]:
    """
    获取按codecount排序的规则集合的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        按codecount降序排列的规则列表
    """
    return get_rule_logic_service().get_sorted_rules(business_object)

# 使用示例
if __name__ == "__main__":
    # 获取searchStaff的规则组件
    base_elements, business_rules, answer_elements = get_rule_components('searchStaff')
    print(f"基础元素数量: {len(base_elements.get('baseDataList', []))}")
    print(f"业务规则数量: {len(business_rules.get('rulesMap', []))}")
    print(f"回答元素数量: {len(answer_elements.get('answerElements', []))}")
    
    # 获取排序后的规则列表
    sorted_rules = get_sorted_rules('searchStaff')
    print("排序后的规则列表:")
    for rule in sorted_rules:
        print(f"规则ID: {rule.get('id')}, 名称: {rule.get('name')}, 复杂度: {rule.get('codecount')}") 