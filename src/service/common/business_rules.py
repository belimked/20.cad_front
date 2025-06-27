#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from typing import List, Dict, Any, Optional
from .tools import get_base_path, load_index_file, load_json_file, load_indexed_file

class BusinessRulesService:
    """
    业务规则服务类，用于读取和管理src/entity/relationship目录下的业务规则文件
    """
    
    def __init__(self):
        """
        初始化业务规则服务，加载索引文件
        """
        self.base_path = get_base_path("entity/relationship")
        self.index_path = os.path.join(self.base_path, "index.json")
        self.business_rules_index = self._load_index()
        self.business_rules_cache = {}  # 用于缓存已加载的业务规则
        
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
            # 确保目录存在
            if os.path.exists(self.base_path):
                for file_name in os.listdir(self.base_path):
                    if file_name.endswith('.json'):
                        key = os.path.splitext(file_name)[0]
                        result[key] = {"filename": file_name}
            return result
    
    def _load_business_rules(self, business_object: str) -> Dict:
        """
        加载指定的业务规则文件
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            业务规则内容的字典
        """
        if business_object in self.business_rules_cache:
            return self.business_rules_cache[business_object]
            
        business_rules_data = load_indexed_file(self.base_path, business_object)
        
        if business_rules_data is None:
            return {}
                
        self.business_rules_cache[business_object] = business_rules_data
        return business_rules_data
    
    def get_available_business_rules(self) -> List[str]:
        """
        获取所有可用的业务规则对象名称
        
        Returns:
            业务规则对象名称列表
        """
        return list(self.business_rules_index.keys())
    
    def get_business_rules_info(self, business_object: str) -> Optional[Dict]:
        """
        获取指定业务规则的信息
        
        Args:
            business_object: 业务对象名称，不含扩展名
            
        Returns:
            业务规则信息，如果不存在则返回None
        """
        return self.business_rules_index.get(business_object)
    
    def get_business_rules(self, business_object: str) -> Dict:
        """
        获取指定业务对象的业务规则内容
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            业务规则内容的字典
        """
        return self._load_business_rules(business_object)
    
    def clear_cache(self, business_object: str = None) -> None:
        """
        清理指定业务对象的缓存，如果不指定则清理所有缓存
        
        Args:
            business_object: 业务对象名称，不含扩展名。如果为None则清理所有缓存
        """
        if business_object is None:
            self.business_rules_cache.clear()
        else:
            self.business_rules_cache.pop(business_object, None)
    
    def clear_all_cache(self) -> None:
        """
        清理所有业务规则缓存
        """
        self.business_rules_cache.clear()

# 单例模式
_instance = None

def get_business_rules_service() -> BusinessRulesService:
    """
    获取业务规则服务的单例实例
    
    Returns:
        BusinessRulesService实例
    """
    global _instance
    if _instance is None:
        _instance = BusinessRulesService()
    return _instance

# 便捷方法
def get_business_rules(business_object: str) -> Dict:
    """
    获取指定业务对象的业务规则内容的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        业务规则内容的字典
    """
    return get_business_rules_service().get_business_rules(business_object)

def get_available_business_rules() -> List[str]:
    """
    获取所有可用的业务规则对象名称的便捷方法
    
    Returns:
        业务规则对象名称列表
    """
    return get_business_rules_service().get_available_business_rules()

def clear_business_rules_cache(business_object: str = None) -> None:
    """
    清理业务规则缓存的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名。如果为None则清理所有缓存
    """
    return get_business_rules_service().clear_cache(business_object)

# 使用示例
if __name__ == "__main__":
    # 获取所有可用的业务规则对象
    business_objects = get_available_business_rules()
    print(f"可用业务规则对象: {business_objects}")
    
    # 获取特定业务对象的业务规则
    staff_search_rules = get_business_rules("searchStaffRules")
    if staff_search_rules:
        print(f"业务规则: {staff_search_rules}") 