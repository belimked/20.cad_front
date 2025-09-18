#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成合同克隆数据服务
"""

import os
import re
from typing import List, Dict, Any
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.generation_service_factory import GenerationServiceFactory
from src.service.common.tools import normalize_project_name
from src.service.rule_logic import get_rule_components
from src.service.common.connector_manager import split_connected_string
# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')


class VpoContractCloneService(BaseGenerationService):
    """
    合同克隆服务类，用于根据规则生成合同克隆的问题和答案
    继承自BaseGenerationService基础类
    """

    BUSINESS_OBJECT = "vpocontractclone"

    def __init__(self):
        """
        初始化合同克隆服务
        """
        super().__init__()

    def post_process_data(self, data, answer_elements=None):
        """
        后处理方法，处理生成的数据
        
        Args:
            data: 要处理的数据
            answer_elements: 答案元素定义，可选
            
        Returns:
            处理后的数据
        """
        # 获取回答元素定义
        if answer_elements is None:
            _, _, answer_elements = get_rule_components(self.BUSINESS_OBJECT)
        answer_elements_list = answer_elements.get('answerElements', [])

        # 如果是单个字典，包装成列表以便统一处理
        if isinstance(data, dict):
            data = [data]

        for item in data:
            # 初始化所有答案字段
            for element in answer_elements_list:
                field_name = element.get('name')
                if field_name:
                    if element.get('isStatic') == '是':
                        item['answer'][field_name] = element.get('staticValue', '无')
                    else:
                        item['answer'][field_name] = ""

            # 1. 处理操作类型
            question_str = str(item.get("question", ""))
            if "批量" in question_str:
                item["answer"]["operation"] = "批量克隆合同单价"
            else:
                item["answer"]["operation"] = "克隆合同单价"
            # question = item['question']
            # 2. 设置其他默认值
            item["answer"]["object"] = "合同信息审核单"
            item["answer"]["supplierGroup"] = "无"
            item["answer"]["materialType"] = "常规附件"


            if 'targetProjects' in item['question']:
                item["answer"]["targetProjects"] = split_connected_string(item['question']['targetProjects'])
            if 'targetAll' in item['question']:
                item["answer"]["targetProjects"] = '其他所有项目'

            if ',' in item['question']['sourceProject'] or '，' in item['question']['sourceProject']:
                item["answer"]['sourceProject'] = item['question']['sourceProject'][:item['question']['sourceProject'].find('，')]
                item["question"]['sourceProject'] = item['question']['sourceProject'][:item['question']['sourceProject'].find('，')]
            else:
                item["answer"]['sourceProject'] = split_connected_string(item['question']['sourceProject'])

        return data

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 vpocontractclone 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

    def generate_vpocontractclone_data(self, business_object: str = BUSINESS_OBJECT,
                                       total_samples: int = 100,
                                       variations_per_rule: int = 5,
                                       variation_service=None,
                                       ruleids: str = None) -> List[Dict]:
        """
        生成合同克隆数据
        
        Args:
            business_object: 业务对象名称，默认为vpocontractclone
            total_samples: 总样本数，默认100
            variations_per_rule: 每个规则的变种数，默认5
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
            
        Returns:
            生成的数据列表
        """
        return self.generate_business_data(business_object, total_samples, variations_per_rule, variation_service,
                                           ruleids)


# 获取服务实例的便捷函数
def get_vpocontractclone_service():
    """
    获取合同克隆服务实例
    
    Returns:
        VpoContractCloneService实例
    """
    return VpoContractCloneService.get_instance()


def generate_vpocontractclone_data(business_object: str = VpoContractCloneService.BUSINESS_OBJECT,
                                   total_samples: int = 100,
                                   variations_per_rule: int = 5,
                                   ruleids: str = None) -> List[Dict]:
    """
    生成合同克隆数据
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    variation_service = GenerationServiceFactory.create_variation_service()
    vpocontractclone_service = get_vpocontractclone_service()
    return vpocontractclone_service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=ruleids
    )
