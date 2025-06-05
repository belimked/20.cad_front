#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Dict, Any, Optional
from .tools import get_base_path, load_yaml_file

class ConfigService:
    """
    配置服务类，用于读取和管理src/config目录下的配置文件
    """
    
    _instance = None
    
    def __new__(cls):
        """
        单例模式
        """
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """
        初始化配置服务，加载配置文件
        """
        if self._initialized:
            return
            
        self.base_path = get_base_path("config")
        self.config_cache = {}  # 用于缓存已加载的配置
        self._initialized = True
    
    def load_config(self, config_name: str) -> Dict:
        """
        加载指定的配置文件
        
        Args:
            config_name: 配置文件名称，不含扩展名(如 test_config 等)
            
        Returns:
            配置内容的字典
        """
        if config_name in self.config_cache:
            return self.config_cache[config_name]
            
        config_path = os.path.join(self.base_path, f"{config_name}.yml")
        config_data = load_yaml_file(config_path)
        
        if config_data is None:
            return {}
                
        self.config_cache[config_name] = config_data
        return config_data
    
    def get_test_config(self) -> Dict:
        """
        获取测试配置
        
        Returns:
            测试配置内容的字典
        """
        return self.load_config("test_config")
    
    def get_test_params(self, business_object: Optional[str] = None) -> Dict[str, int]:
        """
        获取测试参数
        
        Args:
            business_object: 业务对象名称，如果为None则返回默认参数
            
        Returns:
            包含total_samples和variations_per_rule的字典
        """
        config = self.get_test_config()
        default_params = config.get('default', {})
        
        if business_object is None:
            return default_params
            
        business_objects = config.get('business_objects', {})
        business_params = business_objects.get(business_object, {})
        
        # 使用默认参数，然后用特定业务对象参数覆盖
        params = default_params.copy()
        params.update(business_params)
        
        return params
    
    def get_no_original_test_params(self) -> Dict[str, int]:
        """
        获取不保存原始数据的测试参数
        
        Returns:
            包含total_samples和variations_per_rule的字典
        """
        config = self.get_test_config()
        return config.get('no_original_test', {}) 