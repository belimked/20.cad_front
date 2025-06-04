#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import random
from typing import List, Dict, Any, Optional

class DictService:
    """
    字典服务类，用于读取和管理src/dict目录下的字典文件
    """
    
    def __init__(self):
        """
        初始化字典服务，加载索引文件
        """
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dict")
        self.index_path = os.path.join(self.base_path, "index.json")
        self.dict_index = self._load_index()
        self.dict_cache = {}  # 用于缓存已加载的字典
        
    def _load_index(self) -> Dict[str, Dict]:
        """
        加载索引文件，转换为以文件名(不含扩展名)为键的字典
        """
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                
            # 转换为以文件名(不含扩展名)为键的字典
            result = {}
            for item in index_data:
                key = os.path.splitext(item["filename"])[0]
                result[key] = item
            return result
        except Exception as e:
            print(f"加载索引文件失败: {e}")
            return {}
    
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
            
        try:
            file_path = os.path.join(self.base_path, f"{dict_name}.json")
            
            if not os.path.exists(file_path):
                print(f"字典文件不存在: {file_path}")
                return []
                
            with open(file_path, 'r', encoding='utf-8') as f:
                dict_data = json.load(f)
                
            self.dict_cache[dict_name] = dict_data
            return dict_data
        except Exception as e:
            print(f"加载字典文件 {dict_name} 失败: {e}")
            return []
    
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