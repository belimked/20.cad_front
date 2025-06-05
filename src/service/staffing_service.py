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
    
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据，增加对人员查询特定字段的处理
        
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
            answer_data['object'] = "人员安排"
            
            # 设置operation字段为固定值"查询"
            answer_data['operation'] = "查询"
            
            # 特殊处理：确保personName字段映射
            if 'personName' in question_data:
                answer_data['personName'] = question_data['personName']
            
            # 特殊处理：确保projectName字段映射到personProject
            if 'projectName' in question_data:
                # 处理projectName字段，去掉项目后缀
                project_value = question_data['projectName']
                suffixes = ["项目", "工程"]
                for suffix in suffixes:
                    if project_value.endswith(suffix):
                        project_value = project_value[:-len(suffix)]
                        break
                
                answer_data['personProject'] = project_value
            
            # 特殊处理：如果有staffId字段，确保映射到personJobNumber
            if 'staffId' in question_data:
                # 将"工号XXXX"格式处理为纯工号数字
                staff_id = question_data['staffId']
                if staff_id.startswith('工号'):
                    staff_id = staff_id[2:]  # 去掉"工号"前缀
                answer_data['personJobNumber'] = staff_id
            
            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', '')
            })
        
        return variations
    
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
        # 生成基础数据
        data = self.generate_data(business_object, total_samples, variations_per_rule)
        
        # 确保至少有一定数量的数据
        if len(data) < 8:
            # 如果数据不足8条，复制现有数据以达到8条
            current_count = len(data)
            needed = max(8 - current_count, 0)
            
            for i in range(needed):
                # 复制已有数据（如果有的话）
                if current_count > 0:
                    copy_idx = i % current_count
                    data.append(data[copy_idx].copy())  # 深拷贝
        
        # 确保所有数据的operation都是"查询"
        for item in data:
            item['answer']['operation'] = "查询"
        
        return data


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