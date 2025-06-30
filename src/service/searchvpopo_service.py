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
    def __init__(self, trace_id=None, biz_name='searchvpopo'):
        super().__init__()
        self.BUSINESS_OBJECT = 'searchvpopo'

    def post_process_data(self, data, answer_elements=None):
        """
        Process the generated data.
        This is a placeholder and should be implemented by the subclass.
        """
        if not isinstance(data, list):
            data = [data]

        for item in data:
            elements = item.get("elements", [])
            question = item.get("question", {})

            answer = {
                "operation": "查询",
                "object": "订单预结算审核单",
                "projects": [],
                "materialType": [],
                "businessNumbers": [],
                "status": None,
                "orderDate": None,
                "submitDate": None,
                "auditDate": None,
                "priceDateRule": None,
                "materialCode": [],
                "engineeringProperties": [],
                "processDrawing": []
            }

            if "04" in elements:
                projects = question.get("项目", "")
                if isinstance(projects, list):
                    answer["projects"] = [normalize_project_name(p) for p in projects]
                else:
                    answer["projects"] = [normalize_project_name(projects)]
            if "05" in elements:
                answer["materialType"] = question.get("材料类型", "")
            if "06" in elements:
                business_numbers = question.get("单号", "")
                if isinstance(business_numbers, list):
                    answer["businessNumbers"] = business_numbers
                else:
                    answer["businessNumbers"] = [business_numbers]
            if "07" in elements:
                raw_status = question.get("状态", "")
                if any(s in raw_status for s in ["待提交", "不可提交", "可提交", "还未提交", "仍未提交"]):
                    answer["status"] = "提交状态"
                elif any(s in raw_status for s in ["待审核", "待审", "已审核", "已驳回", "审核不通过", "审核通过", "还没审核的"]):
                    answer["status"] = "审核状态"
            
            time_range = question.get("时间范围", "")
            
            if "08" in elements and "11" in elements:
                answer["orderDate"] = question.get("下单时间引导词", "") + time_range
            elif "11" in elements and "12" in elements:
                answer["orderDate"] = time_range + question.get("下单动作", "")

            if "09" in elements and "11" in elements:
                answer["submitDate"] = question.get("提交时间引导词", "") + time_range
            elif "11" in elements and "13" in elements:
                answer["submitDate"] = time_range + question.get("提交动作", "")
                
            if "10" in elements and "11" in elements:
                answer["auditDate"] = question.get("审核时间引导词", "") + time_range
            elif "11" in elements and "14" in elements:
                answer["auditDate"] = time_range + question.get("审核动作", "")

            if "15" in elements:
                answer["priceDateRule"] = question.get("行情价日期", "")
            if "16" in elements:
                answer["materialCode"] = question.get("材料编号", [])
            if "17" in elements:
                answer["processDrawing"] = question.get("工艺图", [])
            if "18" in elements:
                answer["engineeringProperties"] = question.get("工程属性代码", [])

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