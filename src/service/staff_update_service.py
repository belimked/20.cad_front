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
    
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据，确保personName和projectFrom字段的映射
        
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
            
            # 特殊处理：根据问题内容设置operation字段
            # 检查问题中是否包含添加/安排相关词汇
            question_text = str(question_data)
            if any(keyword in question_text for keyword in ["添加", "安排"]):
                answer_data['operation'] = "添加"
            # 检查问题中是否包含删除/撤销/移除相关词汇
            elif any(keyword in question_text for keyword in ["删除", "撤销", "移除"]):
                answer_data['operation'] = "删除"
            
            # 特殊处理：确保personName字段映射
            if 'personName' in question_data:
                answer_data['personName'] = question_data['personName']
            
            # 特殊处理：确保projectFrom字段映射到personProject
            if 'projectFrom' in question_data:
                # 处理projectFrom字段，去掉"从"前缀
                project_value = question_data['projectFrom']
                if project_value.startswith('从'):
                    project_value = project_value[1:]
                
                # 去掉结尾的"项目"或"工程"等后缀
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
            
            # 特殊处理：如果有roleType字段，确保映射到roleInfo
            if 'roleType' in question_data:
                answer_data['roleInfo'] = question_data['roleType']
            
            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', '')
            })
        
        return variations
        
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