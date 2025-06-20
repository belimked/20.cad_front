#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件加载器

提供统一的配置文件加载功能
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def get_config_path(config_name: str) -> str:
    """
    获取配置文件路径
    
    Args:
        config_name: 配置文件名（不含扩展名）
        
    Returns:
        配置文件的完整路径
    """
    # 获取当前文件的目录（src/config）
    config_dir = Path(__file__).parent
    config_file = config_dir / f"{config_name}.yml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    return str(config_file)


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    加载YAML配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        解析后的配置字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"配置文件格式错误: {e}")
    except Exception as e:
        raise RuntimeError(f"加载配置文件失败: {e}")


def load_evaluation_analysis_config() -> Dict[str, Any]:
    """
    加载评估分析配置
    
    Returns:
        评估分析配置字典
    """
    config_path = get_config_path("evaluation_analysis_settings")
    return load_yaml_config(config_path)


def load_generation_config() -> Dict[str, Any]:
    """
    加载数据生成配置
    
    Returns:
        数据生成配置字典
    """
    config_path = get_config_path("generation_settings")
    return load_yaml_config(config_path)


def load_test_config() -> Dict[str, Any]:
    """
    加载测试配置
    
    Returns:
        测试配置字典
    """
    config_path = get_config_path("test_config")
    return load_yaml_config(config_path)


def load_server_config() -> Dict[str, Any]:
    """
    加载服务器配置
    
    Returns:
        服务器配置字典
    """
    config_path = get_config_path("4090_server")
    return load_yaml_config(config_path)


# 配置验证函数
def validate_evaluation_analysis_config(config: Dict[str, Any]) -> bool:
    """
    验证评估分析配置的完整性
    
    Args:
        config: 配置字典
        
    Returns:
        配置是否有效
    """
    required_sections = [
        'failure_analysis',
        'quality_assessment',
        'recommendation_engine',
        'reporting'
    ]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"配置缺少必需的节：{section}")
    
    # 验证关键配置项
    failure_config = config.get('failure_analysis', {})
    if 'enabled' not in failure_config:
        raise ValueError("failure_analysis配置缺少'enabled'项")
    
    quality_config = config.get('quality_assessment', {})
    if 'thresholds' not in quality_config:
        raise ValueError("quality_assessment配置缺少'thresholds'项")
    
    return True


# 便捷函数
def get_evaluation_analyzer_config() -> Dict[str, Any]:
    """
    获取验证过的评估分析器配置
    
    Returns:
        验证过的配置字典
    """
    config = load_evaluation_analysis_config()
    validate_evaluation_analysis_config(config)
    return config 