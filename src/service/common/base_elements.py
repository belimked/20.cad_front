#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import List, Dict, Any, Optional
from .tools import get_base_path, load_index_file, load_json_file, load_indexed_file

class BaseElementsService:
    """
    基础元素服务类，用于读取和管理src/entity/baseElements目录下的基础元素文件
    """
    
    def __init__(self):
        """
        初始化基础元素服务，加载索引文件
        """
        self.base_path = get_base_path("entity/baseElements")
        self.index_path = os.path.join(self.base_path, "index.json")
        self.base_elements_index = self._load_index()
        self.base_elements_cache = {}  # 用于缓存已加载的基础元素
        
    def _load_index(self) -> Dict[str, Dict]:
        """
        加载索引文件，转换为以文件名(不含扩展名)为键的字典
        如果索引文件不存在，则遍历目录获取所有JSON文件
        """
        if os.path.exists(self.index_path):
            return load_index_file(self.base_path)
        else:
            # 如果没有索引文件，则遍历目录获取所有JSON文件
            result = {}
            for file_name in os.listdir(self.base_path):
                if file_name.endswith('.json'):
                    key = os.path.splitext(file_name)[0]
                    result[key] = {"filename": file_name}
            return result
    
    def _load_base_elements(self, business_object: str) -> Dict:
        """
        加载指定的基础元素文件
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            基础元素内容的字典
        """
        if business_object in self.base_elements_cache:
            return self.base_elements_cache[business_object]
            
        base_elements_data = load_indexed_file(self.base_path, business_object)
        
        if base_elements_data is None:
            return {}
                
        self.base_elements_cache[business_object] = base_elements_data
        return base_elements_data
    
    def get_available_base_elements(self) -> List[str]:
        """
        获取所有可用的基础元素业务对象名称
        
        Returns:
            基础元素业务对象名称列表
        """
        return list(self.base_elements_index.keys())
    
    def get_base_elements_info(self, business_object: str) -> Optional[Dict]:
        """
        获取指定基础元素的信息
        
        Args:
            business_object: 业务对象名称，不含扩展名
            
        Returns:
            基础元素信息，如果不存在则返回None
        """
        return self.base_elements_index.get(business_object)
    
    def get_base_elements(self, business_object: str) -> Dict:
        """
        获取指定业务对象的基础元素内容
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            基础元素内容的字典
        """
        return self._load_base_elements(business_object)

# 单例模式
_instance = None

def get_base_elements_service() -> BaseElementsService:
    """
    获取基础元素服务的单例实例
    
    Returns:
        BaseElementsService实例
    """
    global _instance
    if _instance is None:
        _instance = BaseElementsService()
    return _instance

# 便捷方法
def get_base_elements(business_object: str) -> Dict:
    """
    获取指定业务对象的基础元素内容的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        基础元素内容的字典
    """
    return get_base_elements_service().get_base_elements(business_object)

def get_available_base_elements() -> List[str]:
    """
    获取所有可用的基础元素业务对象名称的便捷方法
    
    Returns:
        基础元素业务对象名称列表
    """
    return get_base_elements_service().get_available_base_elements()

# 使用示例
if __name__ == "__main__":
    # 获取所有可用的基础元素业务对象
    business_objects = get_available_base_elements()
    print(f"可用基础元素业务对象: {business_objects}")
    
    # 获取特定业务对象的基础元素
    staff_search_elements = get_base_elements("searchStaff")
    if staff_search_elements:
        print(f"业务对象名称: {staff_search_elements['businessObject']}")
        print(f"基础数据要素数量: {len(staff_search_elements.get('baseDataList', []))}") 