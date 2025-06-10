#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成模块
"""

from typing import Tuple, List, Dict, Any, Optional
import json
from datetime import datetime

# 从公共服务模块导入函数
from src.service.qwen_api_service import generate_dialogs_and_raw_data, get_rule_codebase

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
    # 调用公共服务模块的函数
    return generate_dialogs_and_raw_data(
        business_object=business_object,
        total_samples=total_samples,
        variations_per_rule=variations_per_rule,
        ruleids=ruleids
    ) 