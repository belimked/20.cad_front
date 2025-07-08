#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from typing import Dict, Any, Optional

from src.service.common.tools import get_base_path, load_yaml_file

class ConfigService:
    """
    配置服务类，用于读取和管理配置文件
    """
    
    def __init__(self):
        """
        初始化配置服务
        """
        self.base_path = get_base_path("config")
    
    def load_yaml_file(self, file_path: str) -> Dict:
        """
        加载YAML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: YAML文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件 {file_path} 时发生错误: {e}")
            return {}
    
    def get_test_config(self) -> Dict:
        """
        获取测试配置
        
        Returns:
            Dict: 测试配置
        """
        config_path = os.path.join(self.base_path, "test_config.yml")
        
        if os.path.exists(config_path):
            return self.load_yaml_file(config_path)
        else:
            return {
                "default": {
                    "total_samples": 50,
                    "variations_per_rule": 10
                }
            }
    
    def get_generation_settings(self) -> Dict:
        """
        获取生成设置配置
        
        Returns:
            Dict: 生成设置配置
        """
        settings_path = os.path.join(self.base_path, "generation_settings.yml")
        
        # 如果文件存在，读取配置
        if os.path.exists(settings_path):
            settings = self.load_yaml_file(settings_path)
        else:
            # 如果文件不存在，返回默认配置
            settings = {
                "variation_generation": {
                    "variation_ratio_factor": 1.2,
                    "min_data_count": 8,
                    "far_greater_factor": 2.0,
                    "variation_multiplier": 2.0
                },
                "rule_processing": {
                    "min_rule_share": 1,
                    "weight_allocation_factor": 1.0
                }
            }
        
        return settings
    
    def get_variation_settings(self) -> Dict:
        """
        获取变种生成相关设置，便捷方法
        
        Returns:
            Dict: 变种生成设置
        """
        settings = self.get_generation_settings()
        return settings.get("variation_generation", {})
    
    def get_rule_processing_settings(self) -> Dict:
        """
        获取规则处理相关设置，便捷方法
        
        Returns:
            Dict: 规则处理设置
        """
        settings = self.get_generation_settings()
        return settings.get("rule_processing", {}) 

    def get_alist_config(self) -> Optional[Dict]:
        """
        获取 Alist 服务配置

        Returns:
            Optional[Dict]: Alist 配置, 如果找不到则返回 None
        """
        config_path = os.path.join(self.base_path, "external_services.yml")
        if os.path.exists(config_path):
            all_configs = self.load_yaml_file(config_path)
            return all_configs.get("alist")
        return None 