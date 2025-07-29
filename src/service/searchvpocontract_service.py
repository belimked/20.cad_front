#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import (
    normalize_project_name, 
    normalize_material_type_name, 
    normalize_object_status_name,
    normalize_meterialsfrompo_id,
    normalize_gcsx_id,
    normalize_draw_id
)
from src.service.common.generation_service_factory import get_generation_service, GenerationServiceFactory

class SearchVPOContractService(BaseGenerationService):
    """
    合同信息审核单查询服务
    """
    
    BUSINESS_OBJECT = 'searchvpocontract'

    def __init__(self):
        """
        初始化合同信息审核单查询服务
        """
        super().__init__()

    def post_process_data(self, data: list, answer_elements=None) -> list:
        """
        后处理生成的数据，实现 searchvpocontract 的核心业务逻辑。
        """
        if not data:
            return []
        
        if answer_elements is None:
            answer_elements = self.get_answer_elements()
        
        answer_elements_list = answer_elements.get('answerElements', [])
        
        for item in data:
            item['answer'] = {element['name']: element.get('staticValue') if element.get('isStatic') == '是' else None for element in answer_elements_list}
            
            question_dict = item.get('question', {})
            elements = item.get('elements', [])

            # --- Logic based on searchvpocontract rules ---
            item['answer']['operation'] = "查询"
            item['answer']['object'] = "合同信息审核单"
            
            if 'projectInfo' in question_dict:
                item['answer']['projects'] = normalize_project_name(question_dict['projectInfo'])
            if  'materialType' in question_dict:
                item['answer']['materialType'] = normalize_material_type_name(question_dict['materialType'])
            if 'businessNumber' in question_dict:
                item['answer']['businessNumbers'] = (question_dict['businessNumber'])
            if 'auditStatus' in question_dict:
                item['answer']['auditStatus'] = normalize_object_status_name(question_dict['auditStatus'])
            if  'reviewContent' in question_dict:
                item['answer']['reviewContent'] = (question_dict['reviewContent'])
            
            time_range = question_dict.get('timeRange')
            if time_range:
                if '09' in elements: #创建时间
                    item['answer']['creationTime'] = time_range
                if '10' in elements: #审核时间
                    item['answer']['auditTime'] = time_range
                if 'submitDatePrefix' in question_dict or 'submitAction' in question_dict: #审核时间
                    item['answer']['creationTime'] = time_range
                if 'auditDatePrefix' in question_dict or 'auditAction' in question_dict: #审核时间
                    item['answer']['auditTime'] = time_range

            if 'materialCode' in question_dict:
                item['answer']['materialCode'] = normalize_meterialsfrompo_id(question_dict['materialCode'])
            if 'engineeringProperties' in question_dict:
                item['answer']['engineeringProperties'] = normalize_gcsx_id(question_dict['engineeringProperties'])
            if  'processDrawing' in question_dict:
                item['answer']['processDrawing'] = normalize_draw_id(question_dict['processDrawing'])

        return data

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 searchvpocontract 数据的顶层方法。
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
        """
        return get_generation_service(cls.BUSINESS_OBJECT, cls)

def generate_searchvpocontract_data(total_samples: int = 10, variations_per_rule: int = 2, rule_ids: list = None):
    """
    生成合同信息审核单查询数据的便捷方法。
    """
    service = SearchVPOContractService.get_instance()
    return service.generate_data(
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        rule_ids=rule_ids
    ) 
