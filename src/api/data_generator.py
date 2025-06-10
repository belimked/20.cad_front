#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成模块
"""

from typing import Tuple, List, Dict, Any, Optional
import json
from datetime import datetime

# 导入各种数据生成服务
from src.service.cargo_update_service import generate_cargo_update_data
from src.service.cargo_search_service import generate_search_cargo_data
from src.service.staffing_update_service import generate_update_staffing_data
from src.service.staffing_service import generate_staffing_data
from src.service.contract_search_service import generate_search_contract_data
from src.service.search_po_service import generate_search_order_data
from src.service.rule_logic import get_rule_components, get_sorted_rules, format_question_by_codebase, format_answer_to_cn

def get_rule_codebase(business_object: str, data: Dict[str, Any]) -> str:
    """
    根据数据中的rule_id找到对应的规则codebase
    
    Args:
        business_object: 业务对象
        data: 包含rule_id的数据字典
        
    Returns:
        对应的规则codebase，如果没有找到则返回空字符串
    """
    sorted_rules = get_sorted_rules(business_object)

    # 直接通过rule_id匹配对应的规则
    if 'rule_id' in data:
        for rule in sorted_rules:
            if rule.get('id') == data['rule_id']:
                return rule.get('codebase', '')

    # 如果没有找到匹配的规则，返回空字符串
    return ""

def generate_training_data(
    business_object: str,
    total_samples: int = 100,
    variations_per_rule: int = 2,
    ruleids: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    生成训练数据
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
        
    Returns:
        包含对话数据和原始数据的元组
    """
    collected_dialogs = []
    collected_raw_data = []

    try:
        # 根据业务对象选择对应的数据生成函数
        if business_object == 'searchContract':
            data = generate_search_contract_data(business_object, total_samples, variations_per_rule, ruleids)
        elif business_object == 'updateStaff':
            data = generate_update_staffing_data(business_object, total_samples, variations_per_rule, ruleids)
        elif business_object == 'updateCargo':
            data = generate_cargo_update_data(business_object, total_samples, variations_per_rule, ruleids)
        elif business_object == 'searchStaff':
            data = generate_staffing_data(business_object, total_samples, variations_per_rule, ruleids)
        elif business_object == 'searchCargo':
            data = generate_search_cargo_data(business_object, total_samples, variations_per_rule, ruleids)
        elif business_object == 'searchPo':
            data = generate_search_order_data(business_object, total_samples, variations_per_rule, ruleids)
        else:
            raise ValueError(f"不支持的业务对象 '{business_object}'")

        # 处理生成的数据
        for data_item in data:
            # 获取该样本对应的规则codebase
            codebase = get_rule_codebase(business_object, data_item)

            # 格式化问题
            formatted_question = format_question_by_codebase(data_item['question'], codebase, business_object)

            # 格式化答案
            formatted_answer = format_answer_to_cn(data_item['answer'], business_object)

            # 创建包含问题和答案的JSON对象
            dialog_json = {
                "messages": [
                    {
                        "role": "user",
                        "content": formatted_question
                    },
                    {
                        "role": "assistant",
                        "content": formatted_answer
                    }
                ]
            }

            # 添加到结果列表
            collected_dialogs.append(dialog_json)
            
            # 保存原始数据
            collected_raw_data.append({
                "business_object": business_object,
                "rule_id": data_item.get('rule_id', ''),
                "rule_name": data_item.get('rule_name', ''),
                "question": data_item['question'],
                "answer": data_item['answer'],
                "codebase": codebase,
                "formatted_question": formatted_question,
                "formatted_answer": formatted_answer,
                "combo_value": data_item.get('combo_value', f"{business_object}_{data_item.get('rule_id', '')}")
            })

        return collected_dialogs, collected_raw_data

    except Exception as e:
        # 记录错误并重新抛出，以便在API中捕获
        print(f"生成训练数据时发生错误: {e}")
        raise 