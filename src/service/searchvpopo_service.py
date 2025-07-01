#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List
from src.service.common.base_generation_service import BaseGenerationService
from src.service.common.tools import normalize_project_name
from src.service.common.generation_service_factory import GenerationServiceFactory
import os


# 直接定义实体目录路径
ENTITY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'entity')

class SearchvpopoService(BaseGenerationService):
    def __init__(self):
        super().__init__()
        self.BUSINESS_OBJECT = 'searchvpopo'

    def generate_data(self, total_samples: int = 100, variations_per_rule: int = 1, rule_ids: list = None) -> list:
        """
        生成 searchvpopo 数据的顶层方法。
        """
        return self.generate_business_data(
            business_object=self.BUSINESS_OBJECT,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=rule_ids
        )

    def post_process_data(self, data, answer_elements=None):
        if not isinstance(data, list):
            data = [data]

        for item in data:
            question_dict = item.get("question", {})

            answer = {
                "operation": "查询", "object": "订单预结算审核单", "projects": None, "materialType": None,
                "businessNumbers": None, "status": None, "orderDate": None, "submitDate": None,
                "auditDate": None, "priceDateRule": None, "materialCode": None, "engineeringProperties": None,
                "processDrawing": None
            }

            if "projectInfo" in question_dict:
                projects = question_dict["projectInfo"]
                answer["projects"] = normalize_project_name(projects)
            
            if "materialType" in question_dict:
                answer["materialType"] = question_dict["materialType"]

            if "businessNumber" in question_dict:
                business_numbers = question_dict["businessNumber"]
                answer["businessNumbers"] =  business_numbers

            if "statusInfo" in question_dict:
                raw_status = question_dict["statusInfo"]
                if any(s in raw_status for s in ["待提交", "不可提交", "可提交", "还未提交", "仍未提交"]):
                    answer["status"] = "提交状态"
                elif any(s in raw_status for s in ["待审核", "待审", "已审核", "已驳回", "审核不通过", "审核通过", "还没审核的"]):
                    answer["status"] = "审核状态"
            
            time_range = question_dict.get("timeRange", "")
            
            if "orderDateConstraint" in question_dict:
                answer["orderDate"] = question_dict["orderDateConstraint"] + time_range
            elif "orderAction" in question_dict:
                answer["orderDate"] = time_range + question_dict["orderAction"]

            if "submitDateConstraint" in question_dict:
                answer["submitDate"] = question_dict["submitDateConstraint"] + time_range
            elif "submitAction" in question_dict:
                answer["submitDate"] = time_range + question_dict["submitAction"]
                
            if "auditDateConstraint" in question_dict:
                answer["auditDate"] = question_dict["auditDateConstraint"] + time_range
            elif "auditAction" in question_dict:
                answer["auditDate"] = time_range + question_dict["auditAction"]

            if "marketPriceRule" in question_dict:
                answer["priceDateRule"] = question_dict["marketPriceRule"]
            if "materialCode" in question_dict:
                answer["materialCode"] = question_dict["materialCode"]
            if "drawingInfo" in question_dict:
                answer["processDrawing"] = question_dict["drawingInfo"]
            if "propertyCode" in question_dict:
                answer["engineeringProperties"] = question_dict["propertyCode"]

            item['answer'] = answer

        return data

    def generate_searchvpopo_data(self, business_object: str = 'searchvpopo',
                                 total_samples: int = 200,
                                 variations_per_rule: int = 2,
                                 variation_service=None,
                                 ruleids: str = None) -> List[Dict]:
        """
        生成查询订单预结算审核单数据
        
        Args:
            business_object: 业务对象名称，默认为searchvpopo
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
            
        Returns:
            生成的数据列表
        """
        # 调用基类的通用方法
        return self.generate_business_data(business_object, total_samples, variations_per_rule, variation_service, ruleids)

    @classmethod
    def get_instance(cls):
        return get_generation_service(cls.BUSINESS_OBJECT, cls)

# 获取服务实例的便捷函数
def get_searchvpopo_service():
    """
    获取查询订单预结算审核单服务实例
    
    Returns:
        SearchvpopoService实例
    """
    return SearchvpopoService.get_instance()

# 便捷方法，使用变种生成服务创建
def generate_searchvpopo_data(business_object: str = 'searchvpopo',
                             total_samples: int = 100,
                             variations_per_rule: int = 1,
                             ruleids: str = None) -> List[Dict]:
    """
    生成查询订单预结算审核单数据
    
    Args:
        business_object: 业务对象名称，默认为searchvpopo
        total_samples: 总样本数，默认100
        variations_per_rule: 每个规则的变种数，默认1
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        生成的数据列表
    """
    # 获取服务实例
    variation_service = GenerationServiceFactory.create_variation_service()
    searchvpopo_service = get_searchvpopo_service()

    # 调用生成方法，传递变种服务实例
    return searchvpopo_service.generate_searchvpopo_data(
        business_object,
        total_samples,
        variations_per_rule,
        variation_service,  # 传递变种服务实例
        ruleids             # 传递规则ID过滤字符串
    ) 
