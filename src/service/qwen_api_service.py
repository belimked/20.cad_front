#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
千问API服务模块 - 提供API和测试代码共用的功能
"""

import json
import os
import random
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any, Tuple, Optional

# 导入各种数据生成服务
from src.service.cargo_update_service import generate_cargo_update_data
from src.service.cargo_search_service import generate_search_cargo_data
from src.service.staffing_update_service import generate_update_staffing_data
from src.service.staffing_service import generate_staffing_data
from src.service.contract_search_service import generate_search_contract_data
from src.service.search_po_service import generate_search_order_data
from src.service.rule_logic import get_rule_components, get_sorted_rules, format_question_by_codebase, \
    format_answer_to_cn

# --- 动态服务导入 ---
from src.service.common.generation_service_factory import get_generation_service
from src.service.cargo_update_service import CargoUpdateService
from src.service.cargo_search_service import CargoSearchService
from src.service.summary_cargo_service import SummaryCargoService
from src.service.summary_po_service import SummaryPoService
from src.service.update_contract_service import UpdateContractService
from src.service.staffing_update_service import StaffingUpdateService
from src.service.staffing_service import StaffingService
from src.service.contract_search_service import ContractSearchService
from src.service.search_po_service import SearchPOService
from src.service.submitvpopo_service import SubmitVpopoService
from src.service.submitvposent_service import SubmitVposentService
from src.service.vpocontractclone_service import VpoContractCloneService
from src.service.searchvpopo_service import SearchvpopoService
from src.service.searchvposent_service import SearchVposentService
from src.service.vpo.searchvpopofrom_service import SearchvpopofromService
from src.service.vpo.searchvposentfrom_service import SearchvposentfromService
from src.service.searchvpocontract_service import SearchVPOContractService

# --- 服务类映射 ---
SERVICE_CLASS_MAP = {
    'updateCargo': CargoUpdateService,
    'searchCargo': CargoSearchService,
    'summaryCargo': SummaryCargoService,
    'summaryPo': SummaryPoService,
    'updateContract': UpdateContractService,
    'updateStaff': StaffingUpdateService,
    'searchStaff': StaffingService,
    'searchContract': ContractSearchService,
    'searchPo': SearchPOService,
    'submitvpopo': SubmitVpopoService,
    'submitvposent': SubmitVposentService,
    'vpocontractclone': VpoContractCloneService,
    'searchvpopo': SearchvpopoService,
    'searchvposent': SearchVposentService,
    'searchvpopofrom': SearchvpopofromService,
    'searchvposentfrom': SearchvposentfromService,
    'searchvpocontract': SearchVPOContractService,
}


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


def save_to_jsonl(data: List[Dict], output_dir: str, filename: str = None) -> str:
    """
    将数据保存为JSONL格式
    
    Args:
        data: 要保存的数据列表
        output_dir: 输出目录路径
        filename: 文件名，如果为None，则自动生成
        
    Returns:
        保存的文件完整路径
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 如果没有指定文件名，则使用当前时间生成
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qwen_data_{timestamp}.jsonl"

    # 完整的文件路径
    file_path = os.path.join(output_dir, filename)

    # 将数据写入JSONL文件
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    return file_path


def analyze_data(raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析数据统计信息
    
    Args:
        raw_data: 原始数据列表
        
    Returns:
        统计信息字典
    """
    # 提取所有rule_id
    rule_ids = [item.get('rule_id', '') for item in raw_data]
    rule_id_counts = Counter(rule_ids)

    # 获取rule_name与rule_id的映射
    rule_names = {}
    for item in raw_data:
        rule_id = item.get('rule_id', '')
        if rule_id and rule_id not in rule_names:
            rule_names[rule_id] = item.get('rule_name', f'规则{rule_id}')

    # 格式化规则分布统计
    rule_distribution = [
        {"rule_id": rule_id, "rule_name": rule_names.get(rule_id, f'规则{rule_id}'), "count": count}
        for rule_id, count in rule_id_counts.items()
    ]

    # 按数量降序排序
    rule_distribution.sort(key=lambda x: x["count"], reverse=True)

    return {
        "total_count": len(raw_data),
        "rule_distribution": rule_distribution
    }


def generate_dialogs_and_raw_data(
        business_object: str,
        total_samples: int = 100,
        variations_per_rule: int = 2,
        ruleids: Optional[str] = None,
        keyword: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    生成对话数据和原始数据
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串
        keyword: 关键字过滤
        
    Returns:
        包含对话数据和原始数据的元组
    """
    collected_dialogs = []
    collected_raw_data = []

    # 处理关键字列表
    keywords = []
    if keyword and isinstance(keyword, str):
        keywords = [k.strip() for k in keyword.split(',') if k.strip()]

    try:
        # --- 重构：使用服务工厂动态获取服务 ---
        service_class = SERVICE_CLASS_MAP.get(business_object)
        if not service_class:
            raise ValueError(f"不支持的业务对象 '{business_object}'")

        service = get_generation_service(business_object, service_class)
        if not service:
            raise ValueError(f"无法为业务对象 '{business_object}' 创建服务实例")

        data = service.generate_data(
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            rule_ids=ruleids
        )
        # --- 结束重构 ---

        # 处理生成的数据
        for data_item in data:
            # 获取该样本对应的规则codebase
            codebase = get_rule_codebase(business_object, data_item)

            codevalue = data_item.get('combo_value', f"{business_object}_{data_item.get('rule_id', '')}")
            # 格式化问题
            formatted_question = format_question_by_codebase(data_item['question'], codevalue, business_object)
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

            # 如果有关键字过滤，检查是否匹配（所有关键词都要匹配）
            should_collect = True
            if keywords:
                all_matched = True
                for k in keywords:
                    if k.lower() not in formatted_question.lower():
                        all_matched = False
                        break

                if not all_matched:
                    should_collect = False

            # 收集符合条件的数据
            if should_collect:
                collected_dialogs.append(dialog_json)
                collected_raw_data.append({
                    "business_object": business_object,
                    "rule_id": data_item.get('rule_id', ''),
                    "rule_name": data_item.get('rule_name', ''),
                    "question": data_item['question'],
                    "answer": data_item['answer'],
                    "codebase": codebase,
                    "formatted_question": formatted_question,
                    "formatted_answer": formatted_answer,
                    "combo_value": codevalue
                })

        return collected_dialogs, collected_raw_data

    except Exception as e:
        print(f"生成数据时发生错误: {e}")
        raise


def generate_and_save_data(
        business_object: str,
        total_samples: int = 100,
        variations_per_rule: int = 2,
        ruleids: Optional[str] = None,
        keyword: Optional[str] = None,
        output_dir: str = "outputs/data"
) -> Dict[str, Any]:
    """
    生成数据并保存到文件
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串
        keyword: 关键字过滤
        output_dir: 输出目录
        
    Returns:
        包含生成数据信息的字典
    """
    # 生成数据
    dialogs, raw_data = generate_dialogs_and_raw_data(
        business_object=business_object,
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        ruleids=ruleids,
        keyword=keyword
    )

    # 创建时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存对话数据
    dialogs_filename = f"{business_object}_dialogs_{timestamp}.jsonl"
    dialogs_file_path = save_to_jsonl(dialogs, output_dir, dialogs_filename)

    # 保存原始数据
    raw_filename = f"{business_object}_raw_{timestamp}.jsonl"
    raw_file_path = save_to_jsonl(raw_data, output_dir, raw_filename)

    # 分析数据统计信息
    stats = analyze_data(raw_data)

    # 获取前5条数据作为示例
    examples = dialogs[:5] if len(dialogs) >= 5 else dialogs

    # 返回结果
    return {
        "status": "success",
        "message": f"成功生成{len(dialogs)}条训练数据",
        "files": {
            "dialogs_file": dialogs_file_path,
            "raw_file": raw_file_path
        },
        "statistics": stats,
        "examples": examples
    }
