#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
供应商智能匹配服务
使用字典服务进行供应商名称的智能匹配和分割
"""

from typing import List, Dict, Optional, Tuple
import re
from .dict import get_dict
from .connector_manager import get_all_connectors


class VendorMatcher:
    """
    供应商智能匹配器
    基于字典服务进行供应商名称的智能识别和分割
    """
    
    def __init__(self):
        """初始化供应商匹配器"""
        self.vendors_cache = None
        self.vendor_names = None
        self.connectors = get_all_connectors()
    
    def _load_vendors(self) -> List[Dict]:
        """加载供应商字典"""
        if self.vendors_cache is None:
            self.vendors_cache = get_dict('vendors', count=0, random_select=False)
            # 提取所有供应商名称，包括全名和简称
            self.vendor_names = set()
            for vendor in self.vendors_cache:
                if 'vendorname' in vendor:
                    self.vendor_names.add(vendor['vendorname'])
                if 'vendorshortname' in vendor:
                    self.vendor_names.add(vendor['vendorshortname'])
        return self.vendors_cache
    
    def _find_vendor_matches(self, text: str) -> List[Tuple[str, int, int]]:
        """
        在文本中查找所有可能的供应商匹配
        
        Args:
            text: 要搜索的文本
            
        Returns:
            匹配结果列表，每个元素为 (供应商名称, 开始位置, 结束位置)
        """
        self._load_vendors()
        matches = []
        
        # 按长度降序排列，优先匹配长名称
        sorted_names = sorted(self.vendor_names, key=len, reverse=True)
        
        for vendor_name in sorted_names:
            if vendor_name in text:
                start = 0
                while True:
                    pos = text.find(vendor_name, start)
                    if pos == -1:
                        break
                    matches.append((vendor_name, pos, pos + len(vendor_name)))
                    start = pos + 1
        
        # 按位置排序并去除重叠
        matches.sort(key=lambda x: (x[1], -len(x[0])))
        return self._remove_overlapping_matches(matches)
    
    def _remove_overlapping_matches(self, matches: List[Tuple[str, int, int]]) -> List[Tuple[str, int, int]]:
        """
        移除重叠的匹配项，保留最长的匹配
        
        Args:
            matches: 匹配结果列表
            
        Returns:
            去重后的匹配结果列表
        """
        if not matches:
            return []
        
        result = []
        last_end = -1
        
        for match in matches:
            name, start, end = match
            if start >= last_end:
                result.append(match)
                last_end = end
        
        return result
    
    def _split_by_connectors(self, text: str) -> List[str]:
        """
        使用连接符分割文本
        
        Args:
            text: 要分割的文本
            
        Returns:
            分割后的文本列表
        """
        result = [text.strip()]
        
        for connector in self.connectors:
            new_result = []
            for item in result:
                split_items = item.split(connector)
                split_items = [s.strip() for s in split_items if s.strip()]
                new_result.extend(split_items)
            result = new_result
        
        return result
    
    def smart_split_vendors(self, text: str) -> List[str]:
        """
        智能分割供应商名称
        
        优先使用字典匹配，如果无法完全匹配则回退到连接符分割
        
        Args:
            text: 包含供应商名称的文本
            
        Returns:
            分割后的供应商名称列表
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()
        
        # 1. 尝试字典匹配
        matches = self._find_vendor_matches(text)
        
        if matches:
            # 检查是否完全覆盖了文本
            covered_chars = set()
            for _, start, end in matches:
                covered_chars.update(range(start, end))
            
            # 计算覆盖率
            total_chars = len([c for c in text if not c.isspace() and c not in self.connectors])
            covered_non_connector_chars = len([i for i in covered_chars if i < len(text) and text[i] not in self.connectors and not text[i].isspace()])
            
            coverage_ratio = covered_non_connector_chars / total_chars if total_chars > 0 else 0
            
            # 如果覆盖率高于80%，使用字典匹配结果
            if coverage_ratio > 0.8:
                return [match[0] for match in matches]
        
        # 2. 回退到连接符分割
        return self._split_by_connectors(text)
    
    def get_vendor_info(self, vendor_name: str) -> Optional[Dict]:
        """
        获取供应商详细信息
        
        Args:
            vendor_name: 供应商名称
            
        Returns:
            供应商信息字典，如果未找到则返回None
        """
        self._load_vendors()
        
        for vendor in self.vendors_cache:
            if (vendor.get('vendorname') == vendor_name or 
                vendor.get('vendorshortname') == vendor_name):
                return vendor
        
        return None


# 单例模式
_instance = None

def get_vendor_matcher() -> VendorMatcher:
    """
    获取供应商匹配器的单例实例
    
    Returns:
        VendorMatcher实例
    """
    global _instance
    if _instance is None:
        _instance = VendorMatcher()
    return _instance

def smart_split_vendors(text: str) -> List[str]:
    """
    智能分割供应商名称的便捷方法
    
    Args:
        text: 包含供应商名称的文本
        
    Returns:
        分割后的供应商名称列表
    """
    return get_vendor_matcher().smart_split_vendors(text)

def get_vendor_info(vendor_name: str) -> Optional[Dict]:
    """
    获取供应商详细信息的便捷方法
    
    Args:
        vendor_name: 供应商名称
        
    Returns:
        供应商信息字典，如果未找到则返回None
    """
    return get_vendor_matcher().get_vendor_info(vendor_name)


# 使用示例
if __name__ == "__main__":
    # 测试智能分割
    test_cases = [
        "泰州亚辉、远和",
        "泰州亚辉、海置和东莞市远和五金制品",
        "海置、东莞市远和五金制品",
        "上海置翰建筑科技有限公司、泰州亚辉不锈钢有限公司"
    ]
    
    matcher = get_vendor_matcher()
    
    for test_text in test_cases:
        print(f"\n输入: '{test_text}'")
        result = matcher.smart_split_vendors(test_text)
        print(f"结果: {result}")
        
        # 显示匹配的供应商信息
        for vendor_name in result:
            info = matcher.get_vendor_info(vendor_name)
            if info:
                print(f"  - {vendor_name}: ID={info.get('vendorid')}, 简称={info.get('vendorshortname')}")
            else:
                print(f"  - {vendor_name}: 未在字典中找到")
