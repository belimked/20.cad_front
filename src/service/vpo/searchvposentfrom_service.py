#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.generation_service_factory import get_generation_service
from src.service.common.tools import normalize_project_name, normalize_yjs_id, normalize_cklx_id, \
    normalize_draw_id, normalize_meterialsfrompo_id,normalize_zts_id
class SearchvposentfromService(BaseGenerationService):
    """
    货单查询服务
    """
    
    BUSINESS_OBJECT = 'searchvposentfrom'

    def __init__(self):
        super().__init__()

    def post_process_data(self, data: list, answer_elements=None) -> list:
        if not data:
            return []
        
        if answer_elements is None:
            answer_elements = self.get_answer_elements()
        
        answer_elements_list = answer_elements.get('answerElements', [])
        
        for item in data:
            item['answer'] = {element['name']: element.get('staticValue') if element.get('isStatic') == '是' else None for element in answer_elements_list}
            
            question_dict = item.get('question', {})

            if 'projectInfo' in question_dict:
                item['answer']['projects'] = question_dict['projectInfo']
            if 'materialType' in question_dict:
                item['answer']['materialType'] = normalize_cklx_id(question_dict['materialType'])
            if 'invoiceNumber' in question_dict:
                item['answer']['businessNumbers'] = question_dict['invoiceNumber']
            if 'deliveryNoteNumber' in question_dict:
                item['answer']['deliveryNoteNumbers'] = question_dict['deliveryNoteNumber']
            if 'receiptStatus' in question_dict:
                item['answer']['receiptStatus'] = normalize_zts_id(question_dict['receiptStatus'])
            if 'settlementStatus' in question_dict:
                item['answer']['settlementStatus'] = normalize_yjs_id(question_dict['settlementStatus'])
            if 'relatedOrder' in question_dict:
                item['answer']['relatedOrderNumber'] = question_dict['relatedOrder']
            if 'materialCode' in question_dict:
                item['answer']['materialCode'] = normalize_meterialsfrompo_id(question_dict['materialCode'])
            if 'processDrawing' in question_dict:
                item['answer']['processDrawing'] = normalize_draw_id(question_dict['processDrawing'])
            if 'engineeringProperties' in question_dict:
                item['answer']['engineeringProperties'] = question_dict['engineeringProperties']

            # Composite time fields
            delivery_time_parts = []
            if 'deliveryDatePrefix' in question_dict:
                delivery_time_parts.append(question_dict['deliveryDatePrefix'])
                if 'timeRange' in question_dict:
                    delivery_time_parts.append(question_dict['timeRange'])
                if 'deliveryAction' in question_dict:
                    delivery_time_parts.append(question_dict['deliveryAction'])
                if delivery_time_parts:
                    item['answer']['deliveryTime'] = question_dict['timeRange']

            receipt_time_parts = []
            if 'receiptDatePrefix' in question_dict:
                receipt_time_parts.append(question_dict['receiptDatePrefix'])
                if 'timeRange' in question_dict:
                    receipt_time_parts.append(question_dict['timeRange'])
                if 'receiptAction' in question_dict:
                    receipt_time_parts.append(question_dict['receiptAction'])
                if receipt_time_parts:
                    item['answer']['receiptTime'] = "".join(receipt_time_parts)

            # Composite amount field
            amount_parts = []
            if 'amount' in question_dict:
                amount_parts.append(question_dict['amount'])
                if 'amountCondition' in question_dict:
                    amount_parts.append(question_dict['amountCondition'])
                if amount_parts:
                    item['answer']['settlementAmount'] = question_dict['amountCondition']

        return data

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

    @classmethod
    def get_instance(cls):
        return get_generation_service(cls.BUSINESS_OBJECT, cls)

def get_searchvposentfrom_service():
    return SearchvposentfromService.get_instance() 
