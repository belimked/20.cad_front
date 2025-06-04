#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import random
from typing import List, Dict, Any, Optional
from .tools import get_base_path, load_index_file, load_json_file, load_indexed_file

class DictService:
    """
    字典服务类，用于读取和管理src/dict目录下的字典文件
    """
    
    def __init__(self):
        """
        初始化字典服务，加载索引文件
        """
        self.base_path = get_base_path("dict")
        self.index_path = os.path.join(self.base_path, "index.json")
        self.dict_index = self._load_index()
        self.dict_cache = {}  # 用于缓存已加载的字典
        
    def _load_index(self) -> Dict[str, Dict]:
        """
        加载索引文件，转换为以文件名(不含扩展名)为键的字典
        """
        return load_index_file(self.base_path)
    
    def _load_dict(self, dict_name: str) -> List[Dict]:
        """
        加载指定的字典文件
        
        Args:
            dict_name: 字典名称，不含扩展名(如 vendors, projects 等)
            
        Returns:
            字典内容的列表
        """
        if dict_name in self.dict_cache:
            return self.dict_cache[dict_name]
            
        dict_data = load_indexed_file(self.base_path, dict_name)
        
        if dict_data is None:
            return []
                
        self.dict_cache[dict_name] = dict_data
        return dict_data
    
    def get_available_dicts(self) -> List[str]:
        """
        获取所有可用的字典名称
        
        Returns:
            字典名称列表
        """
        return list(self.dict_index.keys())
    
    def get_dict_info(self, dict_name: str) -> Optional[Dict]:
        """
        获取指定字典的信息
        
        Args:
            dict_name: 字典名称，不含扩展名
            
        Returns:
            字典信息，如果不存在则返回None
        """
        return self.dict_index.get(dict_name)
    
    def get_dict(self, dict_name: str, count: int = 0, random_select: bool = True) -> List[Dict]:
        """
        获取指定字典的内容
        
        Args:
            dict_name: 字典名称，不含扩展名(如 vendors, projects 等)
            count: 需要获取的数量，0表示获取全部
            random_select: 是否随机选取，默认为True
            
        Returns:
            字典内容的列表
        """
        dict_data = self._load_dict(dict_name)
        
        if not dict_data:
            return []
            
        if count <= 0 or count >= len(dict_data):
            return dict_data
            
        if random_select:
            return random.sample(dict_data, count)
        else:
            return dict_data[:count]

# 单例模式
_instance = None

def get_dict_service() -> DictService:
    """
    获取字典服务的单例实例
    
    Returns:
        DictService实例
    """
    global _instance
    if _instance is None:
        _instance = DictService()
    return _instance

# 便捷方法
def get_dict(dict_name: str, count: int = 0, random_select: bool = True) -> List[Dict]:
    """
    获取指定字典的内容的便捷方法
    
    Args:
        dict_name: 字典名称，不含扩展名(如 vendors, projects 等)
        count: 需要获取的数量，0表示获取全部
        random_select: 是否随机选取，默认为True
        
    Returns:
        字典内容的列表
    """
    return get_dict_service().get_dict(dict_name, count, random_select)

def get_available_dicts() -> List[str]:
    """
    获取所有可用的字典名称的便捷方法
    
    Returns:
        字典名称列表
    """
    return get_dict_service().get_available_dicts()

# 使用示例
if __name__ == "__main__":
    # 获取所有可用的字典
    dicts = get_available_dicts()
    print(f"可用字典: {dicts}")
    
    # 随机获取20个供应商
    vendors = get_dict("vendors", 20)
    print(f"随机20个供应商: {vendors}")
    
    # 获取所有项目
    projects = get_dict("projects")
    print(f"项目总数: {len(projects)}") 