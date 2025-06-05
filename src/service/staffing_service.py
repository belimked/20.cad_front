#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService

class StaffingService(BaseGenerationService):
    """
    人员安排服务类，用于根据规则生成人员安排的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'searchStaff'
    
    def __init__(self):
        """
        初始化人员安排服务
        """
        super().__init__()
    
    def generate_staffing_data(self, business_object: str = BUSINESS_OBJECT, 
                              total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """
        生成人员安排数据
        
        Args:
            business_object: 业务对象名称，默认为searchStaff
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)


# 获取服务实例的便捷函数
get_staffing_service = StaffingService.get_instance

# 便捷方法，使用create_specific_generator创建
generate_staffing_data = BaseGenerationService.create_specific_generator(
    StaffingService, 
    'generate_staffing_data', 
    StaffingService.BUSINESS_OBJECT
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的人员安排数据
        staffing_data = generate_staffing_data(total_samples=10, variations_per_rule=2)
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