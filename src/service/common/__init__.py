#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 从dict.py导出字典服务方法
from .dict import get_dict, get_available_dicts, get_dict_service

# 从tools.py导出通用工具方法
from .tools import get_base_path, load_json_file, load_index_file, load_indexed_file

# 指定可以从包直接导入的函数名
__all__ = [
    # 字典服务函数
    'get_dict', 
    'get_available_dicts', 
    'get_dict_service',
    # 通用工具函数
    'get_base_path',
    'load_json_file',
    'load_index_file',
    'load_indexed_file'
] 