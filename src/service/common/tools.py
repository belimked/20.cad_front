#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import yaml
from typing import Dict, List, Any, Optional


def get_base_path(relative_dir: str) -> str:
    """
    获取指定目录的绝对路径
    
    Args:
        relative_dir: 相对于src目录的路径，如 'dict', 'rules' 等
        
    Returns:
        指定目录的绝对路径
    """
    # 获取当前文件所在的src/service/common目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取src目录
    src_dir = os.path.dirname(os.path.dirname(current_dir))
    # 拼接目标目录
    return os.path.join(src_dir, relative_dir)


def load_json_file(file_path: str) -> Any:
    """
    加载JSON文件
    
    Args:
        file_path: JSON文件的路径
        
    Returns:
        JSON文件解析后的对象，加载失败则返回None
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载JSON文件失败 {file_path}: {e}")
        return None


def load_yaml_file(file_path: str) -> Any:
    """
    加载YAML文件
    
    Args:
        file_path: YAML文件的路径
        
    Returns:
        YAML文件解析后的对象，加载失败则返回None
    """
    try:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data
    except Exception as e:
        print(f"加载YAML文件失败 {file_path}: {e}")
        return None


def load_index_file(base_dir: str, index_filename: str = "index.json") -> Dict[str, Dict]:
    """
    加载索引文件，转换为以文件名(不含扩展名)为键的字典
    
    Args:
        base_dir: 索引文件所在的目录
        index_filename: 索引文件名，默认为index.json
        
    Returns:
        以文件名(不含扩展名)为键的字典
    """
    index_path = os.path.join(base_dir, index_filename)
    index_data = load_json_file(index_path)

    if not index_data:
        return {}

    # 转换为以文件名(不含扩展名)为键的字典
    result = {}
    for item in index_data:
        if "filename" in item:
            key = os.path.splitext(item["filename"])[0]
            result[key] = item
    return result


def load_indexed_file(base_dir: str, file_name: str) -> Any:
    """
    根据文件名加载指定目录下的JSON文件
    
    Args:
        base_dir: 文件所在的基础目录
        file_name: 文件名(不含扩展名)
        
    Returns:
        JSON文件解析后的对象，加载失败则返回None
    """
    file_path = os.path.join(base_dir, f"{file_name}.json")
    return load_json_file(file_path)


def remove_project_suffix(project_name: str, suffixes: List[str] = None) -> str:
    """
    移除项目名称中的常见后缀，如"项目"、"工程"等
    
    Args:
        project_name: 原始项目名称
        suffixes: 要移除的后缀列表，默认为["项目", "工程"]
        
    Returns:
        移除后缀后的项目名称
    """
    if suffixes is None:
        suffixes = ["项目", "工程"]

    # 处理项目名称，去掉项目后缀
    result = project_name
    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[:-len(suffix)]
            break

    return result


def normalize_project_name(project_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）
    
    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]
        
    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["从", "在", "是", "到", "项目", "工程"]

    # 处理项目名称，移除关键词
    result = project_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_vendor_name(vendor_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["供应商", "是", "的"]

    # 处理项目名称，移除关键词
    result = vendor_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_material_type_name(vendor_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["材料类型为", "为", "的","料","类","型","为"]

    # 处理项目名称，移除关键词
    result = vendor_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_material_code_name(vendor_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["材料编号是", "编号", "是"]

    # 处理项目名称，移除关键词
    result = vendor_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_material_status_name(vendor_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["全部材料都是", "材料都是", "全部"]

    # 处理项目名称，移除关键词
    result = vendor_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_object_status_name(vendor_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["状态是", "状态", "是", "的"]

    # 处理项目名称，移除关键词
    result = vendor_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_number_name(number_name: str, keywords: List[str] = None) -> str:
    """
    标准化项目名称，移除常见干扰词（如"从"、"项目"、"工程"等）

    Args:
        project_name: 原始项目名称
        keywords: 要移除的关键词列表，默认为["从", "在", "到", "项目", "工程"]

    Returns:
        标准化后的项目名称
    """
    if keywords is None:
        keywords = ["单", "送货", "发货", "的",  "是", "为", "供应商", "号", "结算", "审核"]

    # 处理项目名称，移除关键词
    result = number_name
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_staff_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等
    
    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]
        
    Returns:
        标准化后的工号
    """
    if prefixes is None:
        prefixes = ["工号", "号码", "编号"]

    # 处理工号，去掉前缀
    result = staff_id
    for prefix in prefixes:
        if result.startswith(prefix):
            result = result[len(prefix):]
            break

    # 去除可能的空格
    return result.strip()


def normalize_draw_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["是", "工", "艺", "图", "纸","包","含","有"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_gcsx_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["是", "工", "程", "属", "性","包","含","材","料"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()
def normalize_meterialsfrompo_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["材","料","所","属","订","单","包","含","编","号","有"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def normalize_cklx_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["材料类型为"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()
def normalize_yjs_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["预结算"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()
def normalize_zts_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["状态是","状","态","为","全","部","预","结","算"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()


def simplify_question(question_text: str, keywords: List[str] = None) -> str:
    """
    精简问题文本，移除常见冗余词汇

    Args:
        question_text: 原始问题文本
        keywords: 要移除的关键词列表，默认为常见冗余词

    Returns:
        精简后的问题文本
    """
    if keywords is None:
        keywords = ["看", "的", "是", "项目", "供应商", "状态是", "总金额是", "货单", "结算单"]

    result = question_text
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除多余空格和标点
    result = re.sub(r'[，。、]+', '，', result)
    result = re.sub(r'\s+', '', result)

    return result.strip()


def extract_business_intent(answer_dict: Dict) -> Dict:
    """
    从answer对象中提取业务意图信息

    Args:
        answer_dict: 原始answer字典

    Returns:
        包含操作意图、业务意图、业务项目的字典
    """
    # 操作意图映射
    operation_mapping = {
        "查询": "查询",
        "审核": "更新",
        "驳回": "更新",
        "对比重量": "更新",
        "对比面积": "更新",
        "对比件数": "更新",
        "审核通过": "更新",
        "统计": "统计",
        "删除": "更新",
        "添加": "更新",
        "修改": "更新"
    }

    operation = answer_dict.get("operation", "")
    mapped_operation = operation_mapping.get(operation, "查询")

    return {
        "操作意图": mapped_operation,
        "业务意图": answer_dict.get("object", ""),
        "业务项目": answer_dict.get("project", "") or answer_dict.get("projects", "") or answer_dict.get("personProject", "")
    }


def normalize_amount_condition(amount_condition: str, keywords: List[str] = None) -> str:
    """
    智能解析并转换金额条件表达式

    将自然语言的金额条件转换为标准化的符号表达式：
    - 大于1000 → >1000
    - 大于等于1000 → >=1000
    - 小于1000 → <1000
    - 小于等于1000 → <=1000
    - 等于1000 → 1000
    - 200至300 → 200~300
    - 1000左右 → !@1000

    Args:
        amount_condition: 原始金额条件文本，如"大于1000"、"在500左右"等
        keywords: 预留参数，用于未来扩展

    Returns:
        转换后的标准化表达式
    """
    import re

    # 输入验证
    if not amount_condition or not isinstance(amount_condition, str):
        return str(amount_condition) if amount_condition else ""

    text = amount_condition.strip()
    if not text:
        return ""

    # 定义转换模式，按优先级排序（更具体的模式在前）
    patterns = [
        # 范围模式 - 必须在其他模式之前处理
        (r'在?(\d+(?:\.\d+)?)至(\d+(?:\.\d+)?)', r'\1~\2'),  # "在200至300" 或 "200至300"
        (r'(\d+(?:\.\d+)?)至(\d+(?:\.\d+)?)', r'\1~\2'),     # "200至300"

        # 近似模式
        (r'在?(\d+(?:\.\d+)?)左右', r'!@\1'),               # "在1000左右" 或 "1000左右"
        (r'(\d+(?:\.\d+)?)左右', r'!@\1'),                  # "1000左右"

        # 比较操作符模式
        (r'大于等于(\d+(?:\.\d+)?)', r'>=\1'),              # "大于等于1000"
        (r'小于等于(\d+(?:\.\d+)?)', r'<=\1'),              # "小于等于1000"
        (r'大于(\d+(?:\.\d+)?)', r'>\1'),                   # "大于1000"
        (r'小于(\d+(?:\.\d+)?)', r'<\1'),                   # "小于1000"
        (r'超过(\d+(?:\.\d+)?)', r'>\1'),                   # "超过1000"

        # 范围内模式
        (r'在(\d+(?:\.\d+)?)以内', r'<=\1'),               # "在1000以内"
        (r'(\d+(?:\.\d+)?)以内', r'<=\1'),                  # "1000以内"

        # 等值模式
        (r'等于(\d+(?:\.\d+)?)', r'\1'),                    # "等于1000"
        (r'为(\d+(?:\.\d+)?)', r'\1'),                      # "为1000"
        (r'是(\d+(?:\.\d+)?)', r'\1'),                      # "是1000"
    ]

    # 按顺序应用转换模式
    for pattern, replacement in patterns:
        match = re.search(pattern, text)
        if match:
            result = re.sub(pattern, replacement, text)
            # 清理可能残留的中文字符和空格
            result = re.sub(r'[在的]', '', result).strip()
            return result

    # 如果没有匹配到任何模式，尝试提取纯数字
    number_match = re.search(r'(\d+(?:\.\d+)?)', text)
    if number_match:
        return number_match.group(1)

    # 如果完全无法解析，返回原始值
    return text


def normalize_additional_fee_condition(fee_condition: str) -> str:
    """
    智能解析并转换附加费用条件表达式

    将自然语言的附加费用条件转换为标准化的符号表达式：
    - 附加费用为0 → =0
    - 不存在附加费用 → =0
    - 没有附加费用 → =0
    - 只有材料费用 → =0
    - 附加费用大于0 → >0
    - 附加费用不为0 → !=0
    - 存在附加费用 → !=0
    - 有附加费用 → !=0
    - 附加费用小于0 → <0
    - 附加费用不等于0 → !=0

    Args:
        fee_condition: 原始附加费用条件文本，如"附加费用为0"、"存在附加费用"等

    Returns:
        转换后的标准化表达式
    """
    import re

    # 输入验证
    if not fee_condition or not isinstance(fee_condition, str):
        return str(fee_condition) if fee_condition else ""

    text = fee_condition.strip()
    if not text:
        return ""

    # 定义转换模式，按优先级排序（更具体的模式在前）
    patterns = [
        # 等于0的模式
        (r'附加费用为0', '=0'),
        (r'不存在附加费用', '=0'),
        (r'没有附加费用', '=0'),
        (r'只有材料费用', '=0'),

        # 不等于0的模式
        (r'附加费用不为0', '!=0'),
        (r'附加费用不等于0', '!=0'),
        (r'存在附加费用', '!=0'),
        (r'有附加费用', '!=0'),

        # 大于0的模式
        (r'附加费用大于0', '>0'),

        # 小于0的模式
        (r'附加费用小于0', '<0'),
    ]

    # 按顺序应用转换模式
    for pattern, replacement in patterns:
        if re.search(pattern, text):
            return replacement

    # 如果没有匹配到任何模式，返回原始值
    return text


