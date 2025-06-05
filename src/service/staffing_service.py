#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
import random
import math
from src.service.rule_logic import get_rule_components, get_sorted_rules
from src.service.common.base_generation_service import BaseGenerationService

class StaffingService(BaseGenerationService):
    """
    人员安排服务类，用于根据规则生成人员安排的问题和答案
    继承自BaseGenerationService基础类
    """
    
    def __init__(self):
        """
        初始化人员安排服务
        """
        super().__init__()
    
    def generate_staffing_data(self, business_object: str, total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """
        生成人员安排数据
        
        Args:
            business_object: 业务对象名称，如 searchStaff
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)

# 单例模式
_instance = None

def get_staffing_service() -> StaffingService:
    """
    获取人员安排服务的单例实例
    
    Returns:
        StaffingService实例
    """
    global _instance
    if _instance is None:
        _instance = StaffingService()
    return _instance

# 便捷方法
def generate_staffing_data(business_object: str, total_samples: int = 10, 
                         variations_per_rule: int = 2) -> List[Dict]:
    """
    生成人员安排数据的便捷方法
    
    Args:
        business_object: 业务对象名称，如 searchStaff
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数量，默认2
        
    Returns:
        生成的数据列表
    """
    return get_staffing_service().generate_staffing_data(
        business_object, total_samples, variations_per_rule
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的人员安排数据
        staffing_data = generate_staffing_data('searchStaff', 10, 2)
        print(f"\n生成的数据数量: {len(staffing_data)}")
        
        # 打印第一条数据
        if staffing_data:
            print("\n示例数据:")
            print(f"问题: {staffing_data[0]['question']}")
            print(f"答案: {staffing_data[0]['answer']}")
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 