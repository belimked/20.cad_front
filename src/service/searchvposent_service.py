#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_project_name, normalize_material_type_name, normalize_material_code_name, \
    normalize_draw_id, normalize_gcsx_id,normalize_zts_id
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

            if "statusInfo" in question_dict:
                raw_status = question_dict["statusInfo"]
                if any(s in raw_status for s in ["待提交", "不可提交", "可提交", "还未提交", "仍未提交"]):
                    item['answer']["status"] = normalize_zts_id(raw_status)
                elif any(s in raw_status for s in
                         ["待审核", "待审", "已审核", "已驳回", "驳回的", "审核不通过", "审核通过", "还没审核的"]):
                    item['answer']["auditStatus"] = normalize_zts_id(raw_status)
            
            if 'priceAdjustmentInfo' in question_dict:
                item['answer']['priceAdjustment'] = question_dict['priceAdjustmentInfo']

            time_range = question_dict.get('timeRange')
            if time_range:
                if 'deliveryDateConstraint' in question_dict:
                    item['answer']['deliveryDate'] = f"{time_range}"
                elif 'deliveryAction' in question_dict:
                    item['answer']['deliveryDate'] = f"{time_range}"
                
                if 'submitDateConstraint' in question_dict:
                    item['answer']['submitDate'] = f"{time_range}"
                elif 'submitAction' in question_dict:
                    item['answer']['submitDate'] = f"{time_range}"

                if 'auditDateConstraint' in question_dict:
                    item['answer']['auditDate'] = f"{time_range}"
                elif 'auditAction' in question_dict:
                    item['answer']['auditDate'] = f"{time_range}"

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
def get_searchvposent_service():
    """
    获取货单结算审核单查询服务实例
    
    Returns:
        SearchVposentService实例
    """
    return SearchVposentService.get_instance() 
