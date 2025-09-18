#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_project_name,normalize_number_name,normalize_zts_id
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.rule_logic import get_rule_components
from src.service.common.connector_manager import split_connected_string
import os
import json

# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')

class SubmitVposentService(BaseGenerationService):
    """
    货单结算审核单提交服务类，用于根据规则生成货单结算审核单提交的问题和答案
    继承自BaseGenerationService基础类
    """
    
    # 定义业务对象类型常量
    BUSINESS_OBJECT = 'submitvposent'
    
    def __init__(self):
        """
        初始化货单结算审核单提交服务
        """
        super().__init__()
    
    def post_process_data(self, data, answer_elements):
        """后处理生成的数据，确保规则和字段关联正确"""
        # 获取回答元素定义（如果answer_elements是字符串）
        if isinstance(answer_elements, str):
            _, _, answer_elements_dict = get_rule_components(answer_elements)
            answer_elements = answer_elements_dict

        # 获取answerElements列表
        answer_elements_list = answer_elements.get('answerElements', [])
        
        for item in data:
            # 初始化所有英文字段为空字符串
            for element in answer_elements_list:
                field_name = element.get('name', '')
                if field_name:
                    # 检查是否是静态字段
                    if element.get('isStatic') == '是':
                        static_value = element.get('staticValue', '无')
                        item['answer'][field_name] = static_value
                    else:
                        # 动态字段初始化为空字符串
                        item['answer'][field_name] = ""
            
            # 设置基础操作和对象
            item['answer']['operation'] = "提交审核"
            
            # 处理对象字段的特殊逻辑
            item['answer']['object'] = "货单结算审核单"
            
            # 处理项目信息
            if 'projectInfo' in item['question']:
                item['answer']['project'] = split_connected_string(normalize_project_name(item['question']['projectInfo']))
            
            # 处理审核单号
            if 'auditNumber' in item['question']:
                item['answer']['objectNumber'] = split_connected_string(normalize_number_name(item['question']['auditNumber']))
            
            # 处理送货单号
            if 'deliveryNumber' in item['question']:
                item['answer']['deliveryNumber'] = split_connected_string(item['question']['deliveryNumber'])
            
            # 处理提交状态
            if 'submitStatus' in item['question']:
                item['answer']['objectSubmitStatus'] = normalize_zts_id(item['question']['submitStatus'])
            else:
                item['answer']['objectSubmitStatus'] = "待提交"
            
            # 处理价格调整
            if 'priceAdjustment' in item['question']:
                item['answer']['materialTotalPriceDifference'] = item['question']['priceAdjustment']
            
            # 处理发货时间（组合字段）
            if ('deliveryAction' in item['question'] or 'objectDeliveryTime' in item['question']) and 'timeRange' in item['question']:
                item['answer']['deliveryTime'] = f"{item['question']['timeRange']}"

            # 处理收货时间（组合字段）
            if ('receiveAction' in item['question'] or 'objectReceiveTime' in item['question']) and 'timeRange' in item['question']:
                item['answer']['receiveTime'] = f"{item['question']['timeRange']}"


        return data
    
    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 submitvposent 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

# 获取服务实例的便捷函数
def get_submitvposent_service():
    """
    获取货单结算审核单提交服务实例
    
    Returns:
        SubmitVposentService实例
    """
    return SubmitVposentService.get_instance()

# 便捷方法，使用变种生成服务创建
def generate_submitvposent_data(business_object: str = SubmitVposentService.BUSINESS_OBJECT,
                               total_samples: int = 10,
                               variations_per_rule: int = 2,
                               ruleids: str = None) -> List[Dict]:
    """
    生成货单结算审核单提交数据
    
    Args:
        business_object: 业务对象名称，默认为submitvposent
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数，默认2
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    submitvposent_service = get_submitvposent_service()

    # 调用生成方法
    return submitvposent_service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=ruleids
    ) 
