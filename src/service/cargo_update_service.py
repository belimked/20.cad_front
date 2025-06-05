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

    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据，增加对货单特定字段的处理
        
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
            answer_data['object'] = "货单信息审核单"
            
            # 根据问题中的关键字设置operation字段
            # 通过检查rule的id或ruleId判断类型，规则命名通常包含规则类型信息
            rule_id = str(rule.get('id', '')) + str(rule.get('ruleId', ''))
            question_str = str(question_data)
            
            if 'add' in rule_id.lower() or '添加' in rule_id or '创建' in rule_id:
                answer_data['operation'] = "添加"
            elif 'delete' in rule_id.lower() or 'remove' in rule_id.lower() or '删除' in rule_id or '撤销' in rule_id:
                answer_data['operation'] = "删除"
            elif 'update' in rule_id.lower() or 'modify' in rule_id.lower() or '修改' in rule_id or '更新' in rule_id:
                answer_data['operation'] = "修改"
            # 如果规则ID不包含操作信息，则通过问题内容来判断
            elif any(keyword in question_str for keyword in ["添加", "创建", "新增"]):
                answer_data['operation'] = "添加"
            elif any(keyword in question_str for keyword in ["删除", "撤销", "移除", "取消"]):
                answer_data['operation'] = "删除"
            elif any(keyword in question_str for keyword in ["修改", "更新", "变更", "调整", "改变"]):
                answer_data['operation'] = "修改"
            else:
                # 默认设置为更新操作
                answer_data['operation'] = "修改"
            
            # 确保其他字段正确映射
            # 例如：货单号、货物名称等
            if 'cargoId' in question_data:
                answer_data['cargoId'] = question_data['cargoId']
            
            if 'cargoName' in question_data:
                answer_data['cargoName'] = question_data['cargoName']
            
            # 确保project字段有值
            if 'projectName' in question_data:
                # 直接使用projectName作为project字段值
                answer_data['project'] = question_data['projectName']
            elif 'project' in question_data:
                answer_data['project'] = question_data['project']
            elif 'projectInfo' in question_data:
                # 从projectInfo中提取项目名称
                project_info = question_data['projectInfo']
                # 处理可能的格式：项目XX、XX项目等
                if project_info.startswith("项目"):
                    answer_data['project'] = project_info[2:].strip()
                elif "项目" in project_info:
                    answer_data['project'] = project_info.split("项目")[0].strip()
                else:
                    # 直接使用整个项目信息
                    answer_data['project'] = project_info.strip()
            else:
                # 从base_elements中获取项目信息
                projects = base_elements.get('projects', [])
                if projects and len(projects) > 0:
                    # 随机选择一个项目
                    project = random.choice(projects)
                    answer_data['project'] = project.get('name', "默认项目")
                else:
                    answer_data['project'] = "默认项目"
            
            # 确保supplier字段有值，优先从问题中提取供应商信息
            if 'supplierInfo' in question_data:
                # 从supplierInfo中提取供应商名称
                supplier_info = question_data['supplierInfo']
                # 常见的供应商信息格式：
                # "供应商是XXX"、"XXX供应商"、"是XXX的"等
                if "供应商是" in supplier_info:
                    supplier_name = supplier_info.split("供应商是")[1].split("的")[0].strip()
                    answer_data['supplier'] = supplier_name
                elif "供应商" in supplier_info:
                    parts = supplier_info.split("供应商")
                    if parts[0]:
                        answer_data['supplier'] = parts[0].strip()
                    elif len(parts) > 1:
                        answer_data['supplier'] = parts[1].strip()
                elif "的" in supplier_info:
                    supplier_name = supplier_info.split("的")[0].strip()
                    if supplier_name:
                        answer_data['supplier'] = supplier_name
                else:
                    # 直接使用整个信息作为供应商名称
                    answer_data['supplier'] = supplier_info.strip()
            elif 'supplierName' in question_data:
                answer_data['supplier'] = question_data['supplierName']
            elif 'supplier' in question_data:
                answer_data['supplier'] = question_data['supplier']
            else:
                # 如果问题中完全没有供应商信息，使用默认供应商
                answer_data['supplier'] = "未知供应商"
            
            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', '')
            })
        
        return variations
    
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