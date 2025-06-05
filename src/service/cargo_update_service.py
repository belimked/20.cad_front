#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
from src.service.common.base_generation_service import BaseGenerationService
import random

class CargoUpdateService(BaseGenerationService):
    """
    货单更新服务类，用于根据规则生成货单更新的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'updateCargo'
    
    def __init__(self):
        """
        初始化货单更新服务
        """
        super().__init__()
    
    def process_dict_replacement(self, element_name, current_value, dict_mapping, dict_item):
        """
        重写字典替换处理方法，增加对业务单号字典的处理
        
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
            
        # 处理业务单号字典
        if 'businessNumbers' in dict_mapping and 'XX' in current_value:
            business_number = dict_item.get('number', "")
            if business_number:
                # 替换XX部分为业务单号
                new_value = current_value.replace('XX', business_number)
                
                # 如果有YY部分，随机生成数量
                if 'YY' in new_value:
                    quantity = random.randint(1, 100)  # 随机生成1-100的数量
                    new_value = new_value.replace('YY', str(quantity))
                    
                print(f"替换业务单号: {element_name} 从 {current_value} 到 {new_value}")
                return new_value
                
        return None
    
    def generate_cargo_update_data(self, business_object: str = BUSINESS_OBJECT, 
                                 total_samples: int = 200, 
                                 variations_per_rule: int = 2) -> List[Dict]:
        """
        生成货单更新数据
        
        Args:
            business_object: 业务对象名称，默认为updateCargo
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        return self.generate_data(business_object, total_samples, variations_per_rule)


# 获取服务实例的便捷函数
get_cargo_update_service = CargoUpdateService.get_instance

# 便捷方法，使用create_specific_generator创建
generate_cargo_update_data = BaseGenerationService.create_specific_generator(
    CargoUpdateService, 
    'generate_cargo_update_data', 
    CargoUpdateService.BUSINESS_OBJECT
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成updateCargo的货单更新数据
        cargo_data = generate_cargo_update_data(total_samples=10, variations_per_rule=2)
        print(f"\n生成的数据数量: {len(cargo_data)}")
        
        # 打印第一条数据
        if cargo_data:
            print("\n示例数据:")
            print(f"问题: {cargo_data[0]['question']}")
            print(f"答案: {cargo_data[0]['answer']}")
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 