#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_project_name,normalize_number_name
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.rule_logic import get_rule_components
import os
import json

# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')

class SubmitVpopoService(BaseGenerationService):
    """
    预结算审核单提交服务类，用于根据规则生成预结算审核单提交的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'submitvpopo'
    
    def __init__(self):
        """
        初始化预结算审核单提交服务
        """
        super().__init__()
    
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

            # 如果code_list为空，暂时跳过（这个逻辑在基类中已经处理）
            # if not code_list:
            #     rule = self._get_rule_by_id(rule_id)
            #     if rule:
            #         code_list = self._extract_code_list(rule)
            #         # 将code_list保存回item中，以便后续处理
            #         item['code_list'] = code_list

            # 设置基础操作和对象
            item['answer']['operation'] = "提交审核"
            
            # 处理对象字段的特殊逻辑
            if 'objectType' in item['question']:
                object_type = item['question']['objectType']
                if object_type == "订单":
                    item['answer']['object'] = "订单预结算审核单"
                else:
                    item['answer']['object'] = object_type
            else:
                item['answer']['object'] = "订单预结算审核单"
            
            # 处理项目信息
            if 'projectInfo' in item['question']:
                item['answer']['project'] = normalize_project_name(item['question']['projectInfo'])
            
            # 处理审核单号
            if 'auditNumber' in item['question']:
                item['answer']['objectNumber'] =normalize_number_name(item['question']['auditNumber'])
            
            # 处理提交状态
            # if 'submitStatus' in item['question']:
            #     item['answer']['objectStatus'] = item['question']['submitStatus']
            # else:
            item['answer']['objectStatus'] = "待提交"
            
            # 处理下单时间（组合字段）
            if 'orderTimePrefix' in item['question'] and 'timeRange' in item['question']:
                item['answer']['objectOrderTime'] = f"{item['question']['timeRange']}"
            elif 'timeRange' in item['question'] and 'orderAction' in item['question']:
                item['answer']['objectOrderTime'] = f"{item['question']['timeRange']}{item['question']['orderAction']}"
            
            # 移除临时的code_list字段，保持数据干净
            if 'code_list' in item:
                del item['code_list']

        return data
    
    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 submitvpopo 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

# 获取服务实例的便捷函数
def get_submitvpopo_service():
    """
    获取预结算审核单提交服务实例
    
    Returns:
        SubmitVpopoService实例
    """
    return SubmitVpopoService.get_instance()

# 便捷方法，使用变种生成服务创建
def generate_submitvpopo_data(business_object: str = SubmitVpopoService.BUSINESS_OBJECT,
                             total_samples: int = 10,
                             variations_per_rule: int = 2,
                             ruleids: str = None) -> List[Dict]:
    """
    生成预结算审核单提交数据
    
    Args:
        business_object: 业务对象名称，默认为submitvpopo
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    submitvpopo_service = get_submitvpopo_service()

    # 调用生成方法
    return submitvpopo_service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=ruleids
    ) 
