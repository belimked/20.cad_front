#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService

class StaffUpdateService(BaseGenerationService):
    """
    人员安排更新服务类，用于根据规则生成人员安排更新的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'updateStaff'
    
    def __init__(self):
        """
        初始化人员安排更新服务
        """
        super().__init__()
    
    def generate_staff_update_data(self, business_object: str = BUSINESS_OBJECT, 
                                 total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """
        生成人员安排更新数据
        
        Args:
            business_object: 业务对象名称，默认为updateStaff
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)


# 获取服务实例的便捷函数
get_staff_update_service = StaffUpdateService.get_instance

# 便捷方法，使用create_specific_generator创建
generate_staff_update_data = BaseGenerationService.create_specific_generator(
    StaffUpdateService, 
    'generate_staff_update_data', 
    StaffUpdateService.BUSINESS_OBJECT
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成updateStaff的人员安排更新数据
        staff_update_data = generate_staff_update_data(total_samples=10, variations_per_rule=2)
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