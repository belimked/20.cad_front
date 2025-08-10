#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问题文本缩减工具模块

提供智能的问题文本缩减功能，包括：
- 实验编号标准化
- 公司名称简化
- 工程属性关键词提取
- 时间表达标准化
- 高级缩减整合功能

作者: Claude 4.0 sonnet
创建时间: 2025-08-10
"""

import re
from typing import Dict, List, Any, Optional, Union
from collections import Counter


def normalize_experiment_id(text: str, keywords: List[str] = None) -> str:
    """
    标准化实验编号，处理连接词并统一格式
    
    Args:
        text: 原始实验编号文本，如"实验03以及实验41"
        keywords: 要移除的关键词列表，默认为["找一下", "去除"]
        
    Returns:
        标准化后的实验编号，如"实验03，实验41"
    """
    if not text or not text.strip():
        return ""
    
    if keywords is None:
        keywords = ["找一下", "去除"]
    
    # 移除噪声关键词
    result = text
    for keyword in keywords:
        result = result.replace(keyword, "")
    
    # 使用connector_manager处理连接词
    try:
        from src.service.common.connector_manager import split_connected_string, join_names_smart
        
        # 分离连接的实验编号
        parts = split_connected_string(result.strip())
        
        # 如果成功分离，重新用标准连接符连接
        if isinstance(parts, list) and len(parts) > 1:
            return join_names_smart(parts)
        else:
            return result.strip()
            
    except ImportError:
        # 如果导入失败，使用简单的字符串替换作为备选
        result = result.replace("以及", "，").replace("和", "，")
        return result.strip()


def extract_company_shortname(text: str, keywords: List[str] = None) -> str:
    """
    提取公司简称，去除行政区前缀和企业后缀
    
    Args:
        text: 原始公司名称文本，如"广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司"
        keywords: 要移除的关键词列表，默认为行政区和企业后缀
        
    Returns:
        简化后的公司名称，如"百聚鑫钢构，紧鑫五金"
    """
    if not text or not text.strip():
        return ""
    
    if keywords is None:
        # 行政区前缀
        administrative_prefixes = ["广东省", "广东", "东莞市", "深圳市", "上海市", "北京市", 
                                 "江苏省", "江苏", "浙江省", "浙江", "山东省", "山东"]
        # 企业后缀
        company_suffixes = ["有限公司", "股份有限公司", "公司", "集团", "股份公司", "企业"]
        keywords = administrative_prefixes + company_suffixes
    
    try:
        from src.service.common.connector_manager import split_connected_string, join_names_smart
        
        # 首先分离多个公司名称
        parts = split_connected_string(text.strip())
        
        if isinstance(parts, list):
            # 处理每个公司名称
            processed_parts = []
            for part in parts:
                # 移除行政区前缀和企业后缀
                result = part
                for keyword in keywords:
                    result = result.replace(keyword, "")
                processed_parts.append(result.strip())
            
            # 重新连接
            return join_names_smart([p for p in processed_parts if p])
        else:
            # 单个公司名称处理
            result = text
            for keyword in keywords:
                result = result.replace(keyword, "")
            return result.strip()
            
    except ImportError:
        # 备选方案：简单字符串处理
        result = text
        for keyword in keywords:
            result = result.replace(keyword, "")
        result = result.replace("和", "，")
        return result.strip()


def extract_engineering_keywords(text: str, keywords: List[str] = None) -> str:
    """
    智能提取工程属性关键词，保留核心材质信息
    
    Args:
        text: 原始工程属性文本，如"工程属性70mm钢板（Q345B）钢制件"
        keywords: 要移除的关键词列表，默认为工程属性前缀和后缀
        
    Returns:
        提取的关键词，如"70mm钢板"
    """
    if not text or not text.strip():
        return ""
    
    if keywords is None:
        # 前缀关键词
        prefixes = ["工程属性", "包含", "材料", "是", "工", "程", "属", "性"]
        # 后缀关键词
        suffixes = ["钢制件", "制件", "构件", "材料"]
        keywords = prefixes + suffixes
    
    result = text
    
    # 移除前缀和后缀关键词
    for keyword in keywords:
        result = result.replace(keyword, "")
    
    # 去除括号内容，如（Q345B）
    result = re.sub(r'[（(][^）)]*[）)]', '', result)
    
    # 使用正则表达式提取关键材质信息：数字+单位+材质名
    # 匹配模式如：70mm钢板、50cm钢材、100mm板材等
    material_pattern = r'(\d+\w*(?:mm|cm|m)?(?:钢板|钢材|板材|材料|钢|板))'
    matches = re.findall(material_pattern, result)
    
    if matches:
        # 如果找到匹配的材质信息，返回第一个
        return matches[0].strip()
    else:
        # 如果没有找到特定模式，检查是否包含"工程属性"
        if "工程属性" in text:
            # 只有明确包含"工程属性"时才返回清理后的文本
            result = re.sub(r'\s+', '', result)
            result = re.sub(r'[，。、]+', '', result)
            return result.strip() if result.strip() else text
        else:
            # 否则返回原文本，不做处理
            return text


def normalize_time_expressions(text: str, keywords: List[str] = None) -> str:
    """
    标准化时间表达，重组语序并简化表达
    
    Args:
        text: 原始时间表达文本，如"提交日在最近五天"、"订单下单时间在最近五天订单预审单"
        keywords: 要移除的关键词列表，默认为时间前缀
        
    Returns:
        标准化后的时间表达，如"最近五天提交"、"近5天下单的预审单"
    """
    if not text or not text.strip():
        return ""
    
    if keywords is None:
        keywords = ["提交日在", "订单下单时间在", "下单时间在", "时间在", "日在"]
    
    result = text
    
    # 移除时间前缀
    for keyword in keywords:
        result = result.replace(keyword, "")
    
    # 数字标准化：中文数字转阿拉伯数字
    number_mapping = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
        "六": "6", "七": "7", "八": "8", "九": "9", "十": "10"
    }
    
    for chinese_num, arabic_num in number_mapping.items():
        result = result.replace(chinese_num, arabic_num)
    
    # 时间表达简化：最近N天 → 近N天
    result = result.replace("最近", "近")
    
    # 使用正则表达式重组语序
    # 匹配模式：(近N天|过去N天)(其他内容)
    time_pattern = r'(近\d+天|过去\d+天|最近\d+天)'
    time_match = re.search(time_pattern, result)
    
    if time_match:
        time_expr = time_match.group(1)
        # 移除时间表达，获取剩余内容
        remaining = result.replace(time_expr, "").strip()
        
        # 处理剩余内容
        if "订单预审单" in remaining:
            remaining = remaining.replace("订单预审单", "下单的预审单")
        elif not remaining:
            remaining = "提交"
        
        # 重组：时间表达 + 动作
        return f"{time_expr}{remaining}"
    
    return result.strip()


def advanced_simplify_question(
    question_text: str,
    reduction_level: str = 'basic',
    custom_rules: Optional[Dict] = None,
    return_stats: bool = False
) -> Union[str, Dict[str, Any]]:
    """
    高级问题精简，支持多级缩减策略和配置化规则

    Args:
        question_text: 原始问题文本
        reduction_level: 缩减级别，可选值：'basic', 'advanced', 'aggressive'
        custom_rules: 自定义缩减规则配置，可启用/禁用特定类型的缩减
        return_stats: 是否返回统计信息，默认False只返回缩减后文本

    Returns:
        缩减后的问题文本，或包含统计信息的字典（当return_stats=True时）

    Examples:
        >>> advanced_simplify_question("找一下实验03以及实验41", "advanced")
        "实验03、实验41"

        >>> advanced_simplify_question("广东百聚鑫钢构有限公司", "advanced")
        "百聚鑫钢构"
    """
    # 参数验证
    if not question_text or not question_text.strip():
        return "" if not return_stats else {"result": "", "stats": {}}

    valid_levels = ['basic', 'advanced', 'aggressive']
    if reduction_level not in valid_levels:
        raise ValueError(f"reduction_level must be one of {valid_levels}, got: {reduction_level}")

    # 默认配置
    default_rules = {
        "enable_time_expressions": True,
        "enable_engineering_keywords": True,
        "enable_company_shortname": True,
        "enable_experiment_id": True,
        "enable_material_type": True,
        "enable_basic_simplify": True,
        "aggressive_keywords": ["查看", "查找", "搜索", "获取", "显示", "列出"]
    }

    # 合并自定义规则
    rules = default_rules.copy()
    if custom_rules:
        rules.update(custom_rules)

    # 根据级别调整规则
    if reduction_level == 'basic':
        # basic级别只启用基础精简
        for key in rules:
            if key.startswith('enable_') and key != 'enable_basic_simplify':
                rules[key] = False
    elif reduction_level == 'aggressive':
        # aggressive级别启用所有规则
        pass  # 使用默认的全启用配置

    # 初始化统计信息
    stats = {
        "original_length": len(question_text),
        "applied_rules": [],
        "intermediate_lengths": [],
        "errors": []
    }

    result = question_text
    stats["intermediate_lengths"].append(("original", len(result)))

    # 执行缩减流水线（按优先级顺序）

    # 1. 时间表达处理（优先级最高）
    if rules.get("enable_time_expressions", True):
        try:
            processed = normalize_time_expressions(result)
            if processed != result:
                result = processed
                stats["applied_rules"].append("time_expressions")
                stats["intermediate_lengths"].append(("time_expressions", len(result)))
        except Exception as e:
            stats["errors"].append(f"time_expressions: {str(e)}")

    # 2. 工程属性提取（局部替换策略）
    if rules.get("enable_engineering_keywords", True):
        try:
            # 只有当文本包含"工程属性"时才处理
            if "工程属性" in result:
                # 使用正则找到工程属性部分并局部替换
                engineering_pattern = r'工程属性[^，,]*'
                match = re.search(engineering_pattern, result)
                if match:
                    engineering_part = match.group(0)
                    processed_part = extract_engineering_keywords(engineering_part)
                    if processed_part != engineering_part:
                        result = result.replace(engineering_part, processed_part)
                        stats["applied_rules"].append("engineering_keywords")
                        stats["intermediate_lengths"].append(("engineering_keywords", len(result)))
        except Exception as e:
            stats["errors"].append(f"engineering_keywords: {str(e)}")

    # 3. 公司名称简化
    if rules.get("enable_company_shortname", True):
        try:
            processed = extract_company_shortname(result)
            if processed != result:
                result = processed
                stats["applied_rules"].append("company_shortname")
                stats["intermediate_lengths"].append(("company_shortname", len(result)))
        except Exception as e:
            stats["errors"].append(f"company_shortname: {str(e)}")

    # 4. 实验编号标准化
    if rules.get("enable_experiment_id", True):
        try:
            processed = normalize_experiment_id(result)
            if processed != result:
                result = processed
                stats["applied_rules"].append("experiment_id")
                stats["intermediate_lengths"].append(("experiment_id", len(result)))
        except Exception as e:
            stats["errors"].append(f"experiment_id: {str(e)}")

    # 5. 材料类型处理（局部替换策略）
    if rules.get("enable_material_type", True):
        try:
            # 只有当文本包含"材料类型为"时才处理
            if "材料类型为" in result:
                # 使用正则找到材料类型部分并局部替换
                material_pattern = r'材料类型为[^，,]*'
                match = re.search(material_pattern, result)
                if match:
                    material_part = match.group(0)
                    # 导入现有的材料类型处理函数
                    from src.service.common.tools import normalize_material_type_name
                    processed_part = normalize_material_type_name(material_part)
                    # 如果处理后不为空且不以"材料"结尾，添加"材料"后缀
                    if processed_part and not processed_part.endswith("材料"):
                        processed_part = f"{processed_part}材料"

                    if processed_part != material_part:
                        result = result.replace(material_part, processed_part)
                        stats["applied_rules"].append("material_type")
                        stats["intermediate_lengths"].append(("material_type", len(result)))
        except Exception as e:
            stats["errors"].append(f"material_type: {str(e)}")

    # 6. 基础精简（优先级最低）
    if rules.get("enable_basic_simplify", True):
        try:
            # 导入现有的基础精简函数
            from src.service.common.tools import simplify_question

            # 对于aggressive级别，添加额外的关键词
            extra_keywords = None
            if reduction_level == 'aggressive':
                extra_keywords = rules.get("aggressive_keywords", [])

            if extra_keywords:
                # 合并默认关键词和额外关键词
                default_keywords = ["看", "的", "是", "项目", "供应商", "状态是", "总金额是", "货单", "结算单"]
                combined_keywords = default_keywords + extra_keywords
                processed = simplify_question(result, combined_keywords)
            else:
                processed = simplify_question(result)

            if processed != result:
                result = processed
                stats["applied_rules"].append("basic_simplify")
                stats["intermediate_lengths"].append(("basic_simplify", len(result)))
        except Exception as e:
            stats["errors"].append(f"basic_simplify: {str(e)}")

    # 计算最终统计信息
    stats["final_length"] = len(result)
    stats["reduction_rate"] = (stats["original_length"] - stats["final_length"]) / stats["original_length"] if stats["original_length"] > 0 else 0
    stats["reduction_level"] = reduction_level

    # 返回结果
    if return_stats:
        return {
            "result": result,
            "stats": stats
        }
    else:
        return result
