#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
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
    # 向上两级获取src目录
    src_dir = os.path.dirname(os.path.dirname(current_dir))
    # 构建目标路径
    target_dir = os.path.join(src_dir, relative_dir)
    return target_dir


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