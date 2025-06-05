#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
公共服务模块
"""

# 从dict.py导出字典服务方法
from .dict import DictService, get_dict, get_available_dicts, get_dict_service, get_dict_by_element_mapping

# 从tools.py导出通用工具方法
from .tools import get_base_path, load_json_file, load_index_file, load_indexed_file, load_yaml_file

# 从base_elements.py导出基础元素服务方法
from .base_elements import BaseElementsService, get_base_elements, get_available_base_elements, get_base_elements_service

# 从answer_elements.py导出回答元素服务方法
from .answer_elements import AnswerElementsService, get_answer_elements, get_available_answer_elements, get_answer_elements_service

# 从business_rules.py导出业务规则服务方法
from .business_rules import BusinessRulesService, get_business_rules, get_available_business_rules, get_business_rules_service

# 从config.py导出配置服务方法
from .config import ConfigService

# 创建服务实例 - 暂时不包含BaseGenerationService
dict_service = DictService()
base_elements_service = BaseElementsService()
answer_elements_service = AnswerElementsService()
business_rules_service = BusinessRulesService()
config_service = ConfigService()

# 延迟导入BaseGenerationService，避免循环导入
from .base_generation_service import BaseGenerationService

# 从variation_generation_service.py导出变种生成服务
from .variation_generation_service import VariationGenerationService

# 从generation_service_factory.py导出生成服务工厂
from .generation_service_factory import GenerationServiceFactory

# 指定可以从包直接导入的函数名
__all__ = [
    # 字典服务函数
    'get_dict', 
    'get_available_dicts', 
    'get_dict_service',
    'get_dict_by_element_mapping',
    # 基础元素服务函数
    'get_base_elements',
    'get_available_base_elements',
    'get_base_elements_service',
    # 回答元素服务函数
    'get_answer_elements',
    'get_available_answer_elements',
    'get_answer_elements_service',
    # 业务规则服务函数
    'get_business_rules',
    'get_available_business_rules',
    'get_business_rules_service',
    # 通用工具函数
    'get_base_path',
    'load_json_file',
    'load_index_file',
    'load_indexed_file',
    'load_yaml_file',
    # 新添加的服务函数
    'DictService',
    'BaseElementsService',
    'AnswerElementsService',
    'BusinessRulesService',
    'BaseGenerationService',
    'ConfigService',
    'dict_service',
    'base_elements_service',
    'answer_elements_service',
    'business_rules_service',
    'config_service',
    'VariationGenerationService',
    'GenerationServiceFactory'
] 