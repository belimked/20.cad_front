#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_project_name, normalize_material_type_name, normalize_material_code_name, \
    normalize_draw_id, normalize_gcsx_id
from src.service.common.generation_service_factory import get_generation_service, GenerationServiceFactory
from src.service.rule_logic import get_rule_components
import os
import json

# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')

class SearchVposentService(BaseGenerationService):
    """
    货单结算审核单查询服务
    """
    
    BUSINESS_OBJECT = 'searchvposent'

    def __init__(self):
        """
        初始化货单结算审核单查询服务
        """
        super().__init__()

    def _get_status_type(self, status_text: str) -> str:
        """根据状态文本判断是提交状态还是审核状态"""
        submit_keywords = ["待提交", "不可提交", "不可以提交", "可提交", "还未提交", "仍未提交"]
        audit_keywords = ["待审核", "待审", "已审核", "已驳回", "审核不通过", "审核通过", "还没审核的", "驳回的"]
        
        if any(keyword in status_text for keyword in submit_keywords):
            return "提交状态"
        if any(keyword in status_text for keyword in audit_keywords):
            return "审核状态"
        return ""

    def post_process_data(self, data: list, answer_elements=None) -> list:
        """
        后处理生成的数据，实现 searchvposent 的核心业务逻辑。
        判断逻辑完全基于 question_dict 的内容。
        """
        if not data:
            return []
        
        if answer_elements is None:
            answer_elements = self.get_answer_elements()
        
        answer_elements_list = answer_elements.get('answerElements', [])
        
        for item in data:
            item['answer'] = {element['name']: element.get('staticValue') if element.get('isStatic') == '是' else None for element in answer_elements_list}
            
            question_dict = item.get('question', {})

            # --- Logic based on new, standardized English keys ---
            item['answer']['operation'] = "查询"
            item['answer']['object'] = "货单结算审核单"
            
            if 'projectInfo' in question_dict:
                item['answer']['projects'] = normalize_project_name(question_dict['projectInfo'])
            if 'materialType' in question_dict:
                item['answer']['materialType'] = normalize_material_type_name(question_dict['materialType'])
            if 'auditNumber' in question_dict:
                item['answer']['businessNumbers'] = question_dict['auditNumber']
            if 'deliveryNumber' in question_dict:
                item['answer']['deliveryNoteNumbers'] = question_dict['deliveryNumber']
            if 'orderNumber' in question_dict:
                item['answer']['orderNumbers'] = question_dict['orderNumber']
            if 'materialCode' in question_dict:
                item['answer']['materialNumbers'] = normalize_material_code_name(question_dict['materialCode'])
            if 'drawingInfo' in question_dict:
                item['answer']['processDiagrams'] = normalize_draw_id(question_dict['drawingInfo'])
            if 'engineeringProperties' in question_dict:
                item['answer']['engineeringProperties'] = normalize_gcsx_id(question_dict['engineeringProperties'])
            
            if 'statusInfo' in question_dict:
                item['answer']['status'] = self._get_status_type(question_dict['statusInfo'])
            
            if 'priceAdjustmentInfo' in question_dict:
                item['answer']['priceAdjustment'] = question_dict['priceAdjustmentInfo']

            time_range = question_dict.get('timeRange')
            if time_range:
                if 'deliveryDateConstraint' in question_dict:
                    item['answer']['deliveryDate'] = f"{question_dict['deliveryDateConstraint']}{time_range}"
                elif 'deliveryAction' in question_dict:
                    item['answer']['deliveryDate'] = f"{time_range}{question_dict['deliveryAction']}"
                
                if 'submitDateConstraint' in question_dict:
                    item['answer']['submitDate'] = f"{question_dict['submitDateConstraint']}{time_range}"
                elif 'submitAction' in question_dict:
                    item['answer']['submitDate'] = f"{time_range}{question_dict['submitAction']}"

                if 'auditDateConstraint' in question_dict:
                    item['answer']['auditDate'] = f"{question_dict['auditDateConstraint']}{time_range}"
                elif 'auditAction' in question_dict:
                    item['answer']['auditDate'] = f"{time_range}{question_dict['auditAction']}"

        return data

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 searchvposent 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

    @classmethod
    def get_instance(cls):
        """
        获取服务的单例实例。
        这个方法会调用工厂函数，如果实例不存在，则创建并注册它。
        """
        return get_generation_service(cls.BUSINESS_OBJECT, cls)

    def generate_submitvposent_data(self, business_object: str = BUSINESS_OBJECT,
                                   total_samples: int = 200,
                                   variations_per_rule: int = 2,
                                   variation_service=None,
                                   ruleids: str = None) -> List[Dict]:
        """
        生成货单结算审核单提交数据
        
        Args:
            business_object: 业务对象名称，默认为submitvposent
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
            
        Returns:
            生成的数据列表
        """
        # 调用基类的通用方法
        return self.generate_business_data(business_object, total_samples, variations_per_rule, variation_service, ruleids)

def generate_searchvposent_data(total_samples: int = 10, variations_per_rule: int = 2, rule_ids: list = None):
    """
    生成货单结算审核单查询数据的便捷方法。
    """
    service = SearchVposentService.get_instance()
    return service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=rule_ids
    )

# 获取服务实例的便捷函数
def get_submitvposent_service():
    """
    获取货单结算审核单提交服务实例
    
    Returns:
        SubmitVposentService实例
    """
    return SearchVposentService.get_instance()

# 便捷方法，使用变种生成服务创建
def generate_submitvposent_data(business_object: str = SearchVposentService.BUSINESS_OBJECT,
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
    variation_service = GenerationServiceFactory.create_variation_service()
    submitvposent_service = get_submitvposent_service()

    # 调用生成方法，传递变种服务实例
    return submitvposent_service.generate_submitvposent_data(
        business_object,
        total_samples,
        variations_per_rule,
        variation_service,  # 传递变种服务实例
        ruleids             # 传递规则ID过滤字符串
    ) 
