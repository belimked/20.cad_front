#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import random
from typing import List, Dict, Any, Optional, Union
from .tools import get_base_path, load_index_file, load_json_file, load_indexed_file

class ConnectionService:
    """
    连接关系服务类，用于读取和管理src/entity/connection目录下的连接关系文件
    """
    
    def __init__(self):
        """
        初始化连接关系服务，加载索引文件
        """
        self.base_path = get_base_path("entity/connection")
        self.index_path = os.path.join(self.base_path, "index.json")
        self.connection_index = self._load_index()
        self.connection_cache = {}  # 用于缓存已加载的连接关系
        
    def _load_index(self) -> Dict[str, Dict]:
        """
        加载索引文件，转换为以文件名(不含扩展名)为键的字典
        """
        return load_index_file(self.base_path)
    
    def _load_connection(self, business_object: str) -> Dict:
        """
        加载指定业务对象的连接关系文件
        
        Args:
            business_object: 业务对象名称，如searchStaff、updateCargo等
            
        Returns:
            连接关系数据字典
        """
        if business_object in self.connection_cache:
            return self.connection_cache[business_object]
            
        connection_data = load_indexed_file(self.base_path, business_object)
        
        if connection_data is None:
            return {}
                
        self.connection_cache[business_object] = connection_data
        return connection_data
    
    def get_available_business_objects(self) -> List[str]:
        """
        获取所有可用的业务对象名称
        
        Returns:
            业务对象名称列表
        """
        return list(self.connection_index.keys())
    
    def get_connection_info(self, business_object: str) -> Optional[Dict]:
        """
        获取指定业务对象的连接关系信息
        
        Args:
            business_object: 业务对象名称
            
        Returns:
            连接关系信息，如果不存在则返回None
        """
        return self.connection_index.get(business_object)
    
    def get_connections(self, business_object: str) -> List[str]:
        """
        获取指定业务对象的连接关系列表
        
        Args:
            business_object: 业务对象名称，如searchStaff、updateCargo等
            
        Returns:
            连接关系字符串列表，如["01,04", "01,05"]
        """
        connection_data = self._load_connection(business_object)
        
        if not connection_data or 'connectionList' not in connection_data:
            return []
            
        connections = []
        for item in connection_data['connectionList']:
            if 'connections' in item:
                connections.extend(item['connections'])
                
        return connections
    
    def get_random_connection(self, business_object: str) -> Optional[str]:
        """
        获取指定业务对象的随机一个连接关系
        
        Args:
            business_object: 业务对象名称
            
        Returns:
            随机一个连接关系字符串，如"01,04"，如果没有则返回None
        """
        connections = self.get_connections(business_object)
        
        if not connections:
            return None
            
        return random.choice(connections)
    
    def get_connection_pairs(self, business_object: str) -> List[tuple]:
        """
        获取指定业务对象的连接关系对列表
        
        Args:
            business_object: 业务对象名称
            
        Returns:
            连接关系对的列表，如[("01", "04"), ("01", "05")]
        """
        connections = self.get_connections(business_object)
        
        pairs = []
        for connection in connections:
            if ',' in connection:
                parts = connection.split(',', 1)
                if len(parts) == 2:
                    pairs.append((parts[0].strip(), parts[1].strip()))
                    
        return pairs

# 单例模式
_instance = None

def get_connection_service() -> ConnectionService:
    """
    获取连接关系服务的单例实例
    
    Returns:
        ConnectionService实例
    """
    global _instance
    if _instance is None:
        _instance = ConnectionService()
    return _instance

# 便捷方法
def get_connections(business_object: str) -> List[str]:
    """
    获取指定业务对象的连接关系列表的便捷方法
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        连接关系字符串列表
    """
    return get_connection_service().get_connections(business_object)

def get_random_connection(business_object: str) -> Optional[str]:
    """
    获取指定业务对象的随机一个连接关系的便捷方法
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        随机一个连接关系字符串
    """
    return get_connection_service().get_random_connection(business_object)

def get_connection_pairs(business_object: str) -> List[tuple]:
    """
    获取指定业务对象的连接关系对列表的便捷方法
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        连接关系对的列表
    """
    return get_connection_service().get_connection_pairs(business_object)

def get_available_business_objects() -> List[str]:
    """
    获取所有可用的业务对象名称的便捷方法
    
    Returns:
        业务对象名称列表
    """
    return get_connection_service().get_available_business_objects()

# 使用示例
if __name__ == "__main__":
    # 获取所有可用的业务对象
    business_objects = get_available_business_objects()
    print(f"可用业务对象: {business_objects}")
    
    # 获取searchStaff的连接关系
    connections = get_connections("searchStaff")
    print(f"searchStaff连接关系: {connections}")
    
    # 获取随机连接关系
    random_connection = get_random_connection("searchStaff")
    print(f"随机连接关系: {random_connection}")
    
    # 获取连接关系对
    pairs = get_connection_pairs("searchStaff")
    print(f"连接关系对: {pairs}") 