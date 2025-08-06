#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from typing import List, Optional

class ConnectorManager:
    """
    连接符管理器，用于管理字符串连接符的随机选择和智能连接
    
    管理用户提供的连接符列表：['，', ',', '和', '、', '以及']
    提供多种连接策略：智能连接、完全随机连接等
    """
    
    # 用户提供的所有连接符
    ALL_CONNECTORS = ['，', ',', '和', '、', '以及']
    
    # 中间连接符（标点符号）
    MIDDLE_CONNECTORS = ALL_CONNECTORS
    
    # 最后连接符（连词）
    FINAL_CONNECTORS = ALL_CONNECTORS
    def __init__(self):
        """
        初始化连接符管理器
        """
        pass
    
    def get_random_connector(self) -> str:
        """
        从所有连接符中随机选择一个
        
        Returns:
            随机选择的连接符
        """
        return random.choice(self.ALL_CONNECTORS)
    
    def get_random_middle_connector(self) -> str:
        """
        从中间连接符中随机选择一个
        
        Returns:
            随机选择的中间连接符（标点符号）
        """
        return random.choice(self.MIDDLE_CONNECTORS)
    
    def get_random_final_connector(self) -> str:
        """
        从最后连接符中随机选择一个
        
        Returns:
            随机选择的最后连接符（连词）
        """
        return random.choice(self.FINAL_CONNECTORS)
    
    def get_all_connectors(self) -> List[str]:
        """
        获取所有连接符列表
        
        Returns:
            所有连接符的列表
        """
        return self.ALL_CONNECTORS.copy()
    
    def join_names_smart(self, names: List[str]) -> str:
        """
        智能连接名称列表
        
        连接策略：
        - 1个名称：直接返回
        - 2个名称：使用随机连接符连接
        - 多个名称：中间使用标点符号，最后使用连词
        
        Args:
            names: 要连接的名称列表
            
        Returns:
            连接后的字符串
        """
        if not names:
            return ""
        
        if len(names) == 1:
            return names[0]
        
        if len(names) == 2:
            # 两个名称，使用随机连接符
            connector = self.get_random_connector()
            return f"{names[0]}{connector}{names[1]}"
        
        # 多个名称，中间用标点符号，最后用连词
        result_parts = []
        
        # 添加前面的名称，用中间连接符连接
        for i in range(len(names) - 2):
            result_parts.append(names[i])
            result_parts.append(self.get_random_middle_connector())
        
        # 添加倒数第二个名称
        result_parts.append(names[-2])
        
        # 添加最后的连接符
        result_parts.append(self.get_random_final_connector())
        
        # 添加最后一个名称
        result_parts.append(names[-1])
        
        return "".join(result_parts)
    
    def join_names_random(self, names: List[str]) -> str:
        """
        完全随机连接名称列表
        
        所有连接符都从完整列表中随机选择
        
        Args:
            names: 要连接的名称列表
            
        Returns:
            连接后的字符串
        """
        if not names:
            return ""
        
        if len(names) == 1:
            return names[0]
        
        result_parts = []
        
        # 添加第一个名称
        result_parts.append(names[0])
        
        # 为每个后续名称添加随机连接符
        for i in range(1, len(names)):
            result_parts.append(self.get_random_connector())
            result_parts.append(names[i])
        
        return "".join(result_parts)
    
    def join_with_connector(self, names: List[str], connector: str) -> str:
        """
        使用指定连接符连接名称列表

        Args:
            names: 要连接的名称列表
            connector: 指定的连接符

        Returns:
            连接后的字符串
        """
        if not names:
            return ""

        return connector.join(names)

    def split_connected_string(self, text: str, connectors: Optional[List[str]] = None) -> List[str]:
        """
        将包含连接字符的字符串拆分为列表（反向连接操作）

        Args:
            text: 要拆分的字符串，如 "孙洪(041501)、雷利冬、胡炽浩"
            connectors: 连接符列表，默认使用 ALL_CONNECTORS

        Returns:
            拆分后的字符串列表，如 ["孙洪(041501)", "雷利冬", "胡炽浩"]
        """
        if not text or not text.strip():
            return []

        # 使用默认连接符列表
        if connectors is None:
            connectors = self.ALL_CONNECTORS

        # 初始化结果列表，从原始文本开始
        result = [text.strip()]

        # 依次使用每个连接符进行拆分
        for connector in connectors:
            new_result = []
            for item in result:
                # 按当前连接符拆分
                split_items = item.split(connector)
                # 去除每个拆分项的首尾空格
                split_items = [s.strip() for s in split_items if s.strip()]
                new_result.extend(split_items)
            result = new_result

        # 去重并保持原始顺序
        seen = set()
        final_result = []
        for item in result:
            if item and item not in seen:
                seen.add(item)
                final_result.append(item)

        return final_result


# 单例模式
_instance = None

def get_connector_service() -> ConnectorManager:
    """
    获取连接符管理器的单例实例
    
    Returns:
        ConnectorManager实例
    """
    global _instance
    if _instance is None:
        _instance = ConnectorManager()
    return _instance

# 便捷方法
def get_random_connector() -> str:
    """
    获取随机连接符的便捷方法
    
    Returns:
        随机选择的连接符
    """
    return get_connector_service().get_random_connector()

def get_random_middle_connector() -> str:
    """
    获取随机中间连接符的便捷方法
    
    Returns:
        随机选择的中间连接符（标点符号）
    """
    return get_connector_service().get_random_middle_connector()

def get_random_final_connector() -> str:
    """
    获取随机最后连接符的便捷方法
    
    Returns:
        随机选择的最后连接符（连词）
    """
    return get_connector_service().get_random_final_connector()

def join_names_smart(names: List[str]) -> str:
    """
    智能连接名称列表的便捷方法
    
    Args:
        names: 要连接的名称列表
        
    Returns:
        连接后的字符串
    """
    return get_connector_service().join_names_smart(names)

def join_names_random(names: List[str]) -> str:
    """
    完全随机连接名称列表的便捷方法
    
    Args:
        names: 要连接的名称列表
        
    Returns:
        连接后的字符串
    """
    return get_connector_service().join_names_random(names)

def get_all_connectors() -> List[str]:
    """
    获取所有连接符列表的便捷方法

    Returns:
        所有连接符的列表
    """
    return get_connector_service().get_all_connectors()

def split_connected_string(text: str, connectors: Optional[List[str]] = None) -> List[str]:
    """
    将包含连接字符的字符串拆分为列表的便捷方法

    Args:
        text: 要拆分的字符串，如 "孙洪(041501)、雷利冬、胡炽浩"
        connectors: 连接符列表，默认使用 ALL_CONNECTORS

    Returns:
        拆分后的字符串列表，如 ["孙洪(041501)", "雷利冬", "胡炽浩"]
    """
    return get_connector_service().split_connected_string(text, connectors)

# 使用示例
if __name__ == "__main__":
    # 获取连接符管理器实例
    manager = get_connector_service()
    
    # 测试随机连接符
    print(f"随机连接符: {get_random_connector()}")
    print(f"随机中间连接符: {get_random_middle_connector()}")
    print(f"随机最后连接符: {get_random_final_connector()}")
    
    # 测试智能连接
    names1 = ["项目A"]
    names2 = ["项目A", "项目B"]
    names3 = ["项目A", "项目B", "项目C"]
    names4 = ["项目A", "项目B", "项目C", "项目D"]
    
    print(f"1个名称: {join_names_smart(names1)}")
    print(f"2个名称: {join_names_smart(names2)}")
    print(f"3个名称: {join_names_smart(names3)}")
    print(f"4个名称: {join_names_smart(names4)}")
    
    # 测试随机连接
    print(f"随机连接3个名称: {join_names_random(names3)}")
    
    # 获取所有连接符
    print(f"所有连接符: {get_all_connectors()}")

    # 测试拆分功能
    print("\n=== 拆分功能测试 ===")
    test_string = "孙洪(041501)、雷利冬、胡炽浩"
    result = split_connected_string(test_string)
    print(f"原字符串: {test_string}")
    print(f"拆分结果: {result}")
