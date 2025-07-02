#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.generation_service_factory import get_generation_service


class SearchvpopofromService(BaseGenerationService):
    def __init__(self):
        super().__init__()
        self.BUSINESS_OBJECT = 'searchvpopofrom'

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        Generates searchvpopofrom data.
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

    def post_process_data(self, data, answer_elements=None):
        if not data:
            return []

        if answer_elements is None:
            answer_elements = self.get_answer_elements()

        answer_elements_list = answer_elements.get('answerElements', [])

        for item in data:
            # Dynamically initialize the answer dictionary from answer_elements.json
            item['answer'] = {element['name']: element.get('staticValue') if element.get('isStatic') == '是' else None for element in answer_elements_list}
            
            question_dict = item.get('question', {})

            # --- Logic based on searchvposent_service.py pattern (question_dict driven) ---
            if 'project' in question_dict:
                item['answer']['projects'] = question_dict['project']
            if 'materialType' in question_dict:
                item['answer']['materialType'] = question_dict['materialType']
            if 'orderNumber' in question_dict:
                item['answer']['businessNumbers'] = question_dict['orderNumber']
            if 'orderStatus' in question_dict:
                item['answer']['orderStatus'] = question_dict['orderStatus']
            if 'confirmStatus' in question_dict:
                item['answer']['confirmStatus'] = question_dict['confirmStatus']
            if 'preSettlementStatus' in question_dict:
                item['answer']['preSettlementStatus'] = question_dict['preSettlementStatus']
            if 'materialCode' in question_dict:
                item['answer']['materialCode'] = question_dict['materialCode']
            if 'engineeringProperties' in question_dict:
                item['answer']['engineeringProperties'] = question_dict['engineeringProperties']
            if 'processDrawing' in question_dict:
                item['answer']['processDrawing'] = question_dict['processDrawing']
            if 'relatedInvoice' in question_dict:
                item['answer']['relatedInvoiceNumber'] = question_dict['relatedInvoice']
            if 'relatedDeliveryNote' in question_dict:
                item['answer']['relatedDeliveryNoteNumber'] = question_dict['relatedDeliveryNote']

            # Composite field: orderTime
            order_time_parts = []
            if 'orderDatePrefix' in question_dict:
                order_time_parts.append(question_dict['orderDatePrefix'])
            if 'timeRange' in question_dict:
                order_time_parts.append(question_dict['timeRange'])
            if 'orderAction' in question_dict:
                order_time_parts.append(question_dict['orderAction'])
            if order_time_parts:
                item['answer']['orderTime'] = "".join(order_time_parts)

            # Composite field: preSettlementAmount
            amount_parts = []
            if 'amount' in question_dict:
                amount_parts.append(question_dict['amount'])
            if 'amountCondition' in question_dict:
                amount_parts.append(question_dict['amountCondition'])
            if amount_parts:
                item['answer']['preSettlementAmount'] = "".join(amount_parts)

        return data

    @classmethod
    def get_instance(cls):
        return get_generation_service(cls.BUSINESS_OBJECT, cls)


def get_searchvpopofrom_service():
    """
    Gets the instance of the SearchvpopofromService.
    
    Returns:
        An instance of SearchvpopofromService.
    """
    return SearchvpopofromService.get_instance() 