#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
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
        keywords = ["材料类型为", "为", "的"]

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
    keywords = ["是", "工", "艺", "图", "纸"]

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
    keywords = ["是", "工", "程", "属", "性"]

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
def normalize_zts_id(staff_id: str, prefixes: List[str] = None) -> str:
    """
    标准化工号格式，移除常见前缀如"工号"等

    Args:
        staff_id: 原始工号
        prefixes: 要移除的前缀列表，默认为["工号", "号码", "编号"]

    Returns:
        标准化后的工号
    """
    keywords = ["状态是","状","态","为","全","部"]

    # 处理工号，去掉前缀
    result = staff_id
    for keyword in keywords:
        result = result.replace(keyword, "")

    # 去除可能的空格
    return result.strip()
