#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""人员安排服务模块 - 基于规则生成人员安排查询的问题和答案"""

import os
import json
from typing import Dict, List
from src.service.rule_logic import get_rule_components
from src.service.common.tools import normalize_project_name
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.connector_manager import split_connected_string

# 获取项目根目录
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "entity")

class StaffingService(BaseGenerationService):
    """
    人员安排服务类，用于根据规则生成人员安排的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'searchStaff'
    
    def __init__(self):
        # 调用父类的初始化方法
        super().__init__()

    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        根据规则生成多个数据变种
        
        Args:
            rule: 规则字典
            base_elements: 基础元素字典
            answer_elements: 回答元素字典
            num_variations: 生成的变种数量
            
        Returns:
            生成的变种列表
        """
        variations = []
        
        # 提取规则中的codeList
        code_list = self._extract_code_list(rule)
        
        for i in range(num_variations):
            # 生成基础的问题和答案结构
            question_data = {}
            answer_data = {}
            
            # 根据规则生成问题数据
            # 这里需要根据具体的规则类型来生成不同的问题
            rule_type = rule.get('type', '')
            
            # 根据规则的codeList来决定生成什么类型的问题
            if '04' in code_list and '02' in code_list:
                # 人员项目查询: 根据人员姓名查询项目
                question_data = {
                    'personProjectQuery': f"查询{rule.get('name', '人员')}的项目安排",
                    'personName': rule.get('name', '张三')
                }
                answer_data = {
                    'personName': question_data['personName'],
                    'personProject': f"{question_data['personName']}的项目安排"
                }
            elif '05' in code_list and '03' in code_list:
                # 项目人员查询: 根据项目查询人员
                question_data = {
                    'projectPersonQuery': f"查询项目的人员安排",
                    'projectName': rule.get('projectName', '测试项目')
                }
                answer_data = {
                    'projectName': question_data['projectName'],
                    'roleInfo': f"{question_data['projectName']}的负责人"
                }
            else:
                # 默认的人员查询
                question_data = {
                    'personName': rule.get('name', '张三'),
                    'queryType': '人员安排查询'
                }
                answer_data = {
                    'personName': question_data['personName']
                }

            # 特殊处理项目字段 - 如果问题中有projectName，映射到答案的personProject
            if 'projectName' in question_data:
                # 使用工具函数标准化项目名称
                project_value = normalize_project_name(question_data['projectName'])
                answer_data['personProject'] = project_value

            # 特殊处理：如果有staffId字段，确保映射到personJobNumber
            if 'staffId' in question_data:
                # 使用工具函数标准化工号
                staff_id = normalize_staff_id(question_data['staffId'])
                answer_data['personJobNumber'] = staff_id

            # 添加到变种列表
            variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', ''),
                'code_list': code_list  # 添加codeList，便于后续处理
            })
        
        return variations
    
    def _extract_code_list(self, rule):
        """从rule中提取codeList并处理成列表格式"""
        if not rule:
            return []
            
        code_list_value = rule.get('codeList', [])
        # 如果codeList是字符串，拆分成列表
        if isinstance(code_list_value, str):
            # 如果包含分号，则按分号拆分
            if ';' in code_list_value:
                code_list = []
                for code_item in code_list_value.split(';'):
                    code_list.append(code_item)
                return code_list
            # 否则直接作为单个元素的列表返回
            return [code_list_value]
            
        # 如果已经是列表，检查每个元素是否需要进一步拆分
        result = []
        for item in code_list_value:
            if ';' in item:
                result.extend(item.split(';'))
            else:
                result.append(item)
                
        return result
    
    def _get_rule_by_id(self, rule_id):
        """根据规则ID获取规则信息"""
        if not hasattr(self, '_rules_cache'):
            # 初始化规则缓存
            self._rules_cache = {}
            try:
                # 从searchStaffRules.json加载规则
                rules_file_path = os.path.join(ENTITY_DIR, 'relationship', 'searchStaffRules.json')
                with open(rules_file_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                
                # 缓存规则，以rule_id为键
                for rule in rules_data:
                    rule_id_value = rule.get('rule_id')
                    if rule_id_value:
                        self._rules_cache[rule_id_value] = rule
            except Exception as e:
                print(f"加载规则时出错: {e}")
                return None
        
        # 从缓存中获取规则
        return self._rules_cache.get(rule_id)
    
    def post_process_data(self, data, answer_elements):
        """后处理生成的数据，确保规则和字段关联正确"""
        # 获取回答元素定义（如果answer_elements是字符串）
        if isinstance(answer_elements, str):
            _, _, answer_elements_dict = get_rule_components(answer_elements)
            answer_elements = answer_elements_dict
         
        for item in data:
            # 先从item中获取code_list
            code_list = item.get('code_list', [])
            rule_id = item.get('rule_id')
            
            # 如果code_list为空，尝试从rule中提取
            if not code_list:
                rule = self._get_rule_by_id(rule_id)
                if rule:
                    code_list = self._extract_code_list(rule)
                    # 将code_list保存回item中，以便后续处理
                    item['code_list'] = code_list
            
            # print(f"处理数据, rule_id: {rule_id}, code_list: {code_list}")
            
            # 设置基础操作和对象
            item['answer']['operation'] = "查询"
            item['answer']['object'] = "人员安排"
            
            # 处理关联字段
            for element in answer_elements.get('answerElements', []):
                element_name = element.get('name')
                element_base_number = element.get('relateToBase')
                
                # 关联字段处理，确保只有在规则的codeList中包含对应编码时才处理
                if element.get('relateToBase') != "无":
                    # 特殊处理personName字段 - 只要问题中有personName就复制到答案中
                    if element_name == 'personName' and 'personName' in item['question']:
                        item['answer'][element_name] = item['question']['personName']
                    # 特殊处理personProject字段 - 只要问题中有projectName就设置personProject，不依赖code_list
                    elif element_name == 'personProject' and 'projectName' in item['question']:
                        project_value = normalize_project_name(item['question']['projectName'])
                        item['answer'][element_name] = project_value
                    # 特殊处理roleInfo字段（项目人员查询的情况），只在codeList包含05和03时处理
                    elif element_name == 'roleInfo' and 'projectPersonQuery' in item['question'] and '05' in code_list and '03' in code_list:
                        item['answer'][element_name] = f"{item['question']['projectName']}"  # 示例值
            
            # 根据问题类型和code_list设置通用字段
            # 确保personName字段从问题复制到答案 - 不管code_list中是否有04
            if 'personName' in item['question']:
                item['answer']['staffName'] = split_connected_string(item['question']['personName'], force_extract_numbers=True)
            
            # 确保projectName字段映射到personProject - 不管code_list中是否有05
            if 'projectName' in item['question']:
                project_value = normalize_project_name(item['question']['projectName'])
                item['answer']['personProject'] = split_connected_string(project_value)
            
            # 根据问题类型和codeList设置特定字段
            if 'projectInfo' in item['question']:
                # 人员项目查询，确保personProject字段有值
                item['answer']['personProject'] = f"{item['question']['projectInfo']}"  # 示例值
            
            if 'projectPersonQuery' in item['question'] and 'projectName' in item['question'] and '05' in code_list and '03' in code_list:
                # 项目人员查询，确保roleInfo字段有值
                if not item['answer'].get('roleInfo'):
                    item['answer']['roleInfo'] = f"{item['question']['projectName']}"  # 示例值
            
            # 移除临时的code_list字段，保持数据干净
            if 'code_list' in item:
                del item['code_list']
        
        return data
    
    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 searchStaff 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )


# 获取服务实例的便捷函数
get_staffing_service = StaffingService.get_instance

# 便捷方法，使用变种生成服务创建
def generate_staffing_data(business_object: str = StaffingService.BUSINESS_OBJECT, 
                          total_samples: int = 10, 
                          variations_per_rule: int = 2,
                          ruleids: str = None) -> List[Dict]:
    """
    生成人员安排数据
    
    Args:
        business_object: 业务对象名称，默认为searchStaff
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    staffing_service = get_staffing_service()
    
    # 调用生成方法
    return staffing_service.generate_data(
        total_samples=total_samples, 
        variations_per_rule=variations_per_rule,
        rule_ids=ruleids
    )

def clear_rules_cache():
    """
    清理模块级别的规则缓存
    """
    # 由于 _rules_cache 是实例级别的缓存，这里暂时只记录日志
    # 实际的缓存会在实例重新创建时自动清理
    import logging
    logging.info("StaffingService: 规则缓存已标记为需要清理")

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
