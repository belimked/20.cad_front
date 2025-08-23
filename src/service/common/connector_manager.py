#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
from typing import List, Optional, Dict, Union

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

    # 预编译的正则表达式模式，用于高效解析不同格式
    _CHINESE_BRACKET_PATTERN = re.compile(r'^(.+?)（(.+?)）$')
    _ENGLISH_BRACKET_PATTERN = re.compile(r'^(.+?)\((.+?)\)$')
    _REVERSE_CHINESE_BRACKET_PATTERN = re.compile(r'^（(.+?)）(.+?)$')
    _DASH_PATTERN = re.compile(r'^(.+?)-(.+?)$')

    # 字符类型识别的预编译正则表达式模式
    _CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]+')  # 汉字
    _LETTER_PATTERN = re.compile(r'[a-zA-Z]+')  # 字母
    _NUMBER_PATTERN = re.compile(r'\d+')  # 数字
    _PURE_NUMBER_PATTERN = re.compile(r'^\d+$')  # 纯数字检测
    def __init__(self):
        """
        初始化连接符管理器
        """
        # 可能是名称组成部分的连接符，需要智能检测
        self.ambiguous_connectors = ['和', '以及']

        # 企业/供应商相关关键字列表
        self.business_keywords = [
            '供应商', '厂家', '有限公司', '股份有限公司', '集团',
            '企业', '工厂', '制造', '贸易', '科技', '实业',
            '建设', '工程', '材料', '设备', '机械', '化工',
            '电子', '通信', '网络', '软件', '技术', '开发',
            '生产', '销售', '服务', '投资', '控股', '国际',
            '中国', '北京', '上海', '广州', '深圳', '有限',
            '责任', '合作', '联合', '总公司', '分公司'
        ]

    def _has_special_characters(self, text: str) -> bool:
        """
        检测字符串是否包含特殊字符

        Args:
            text: 要检测的字符串

        Returns:
            如果包含中文括号、英文括号或短横线则返回True，否则返回False
        """
        special_chars = ['（', '）', '(', ')', '-']
        return any(char in text for char in special_chars)

    def _would_create_empty_strings(self, text: str, connector: str) -> bool:
        """
        检测使用指定连接符分割文本是否会产生空字符串

        Args:
            text: 要检测的文本
            connector: 连接符

        Returns:
            如果分割后会产生空字符串则返回True，否则返回False
        """
        if connector not in text:
            return False

        split_items = text.split(connector)
        # 检查是否有空字符串或只包含空格的字符串
        return any(not item.strip() for item in split_items)

    def _should_skip_ambiguous_connector(self, text: str, connector: str) -> bool:
        """
        判断是否应该跳过模糊连接符的分割

        检查逻辑：
        1. 如果分割会产生空字符串，跳过
        2. 如果连接符出现在文本末尾，可能是名称的一部分，跳过
        3. 如果连接符前后的文本长度过短，可能是名称的一部分，跳过

        Args:
            text: 要检测的文本
            connector: 连接符

        Returns:
            如果应该跳过则返回True，否则返回False
        """
        if connector not in text:
            return False

        # 检查是否会产生空字符串
        if self._would_create_empty_strings(text, connector):
            return True

        # 检查连接符的位置和上下文
        connector_index = text.find(connector)

        # 如果连接符在文本开头或结尾，可能是名称的一部分
        if connector_index == 0 or connector_index == len(text) - len(connector):
            return True

        # 分割并检查各部分的合理性
        parts = text.split(connector)
        for part in parts:
            part = part.strip()
            # 如果某个部分太短（少于2个字符），可能是误分割
            if len(part) < 2:
                return True

        return False

    def _parse_name_code(self, item: str, force_extract_numbers: bool = False) -> Dict[str, str]:
        """
        解析单个元素的 name 和 code

        按照优先级（中文括号 > 英文括号 > 短横线）进行匹配
        支持智能字符分离和强制数字提取模式

        Args:
            item: 要解析的字符串元素
            force_extract_numbers: 是否启用强制数字提取模式

        Returns:
            包含 name 和 code 字段的字典
        """
        # 优先匹配中文括号
        match = self._CHINESE_BRACKET_PATTERN.match(item)
        if match:
            return {"name": match.group(1).strip(), "code": match.group(2).strip()}

        # 匹配英文括号
        match = self._ENGLISH_BRACKET_PATTERN.match(item)
        if match:
            return {"name": match.group(1).strip(), "code": match.group(2).strip()}

        # 匹配短横线
        match = self._DASH_PATTERN.match(item)
        if match:
            return {"name": match.group(1).strip(), "code": match.group(2).strip()}

        # 新增：强制数字提取模式
        if force_extract_numbers:
            # 检测纯数字
            if self._is_pure_number(item):
                return {"name": "", "code": item.strip()}

            # 应用智能字符分离
            return self._classify_characters(item)

        # 无特殊字符，整个作为 name（保持原有逻辑）
        return {"name": item.strip(), "code": ""}

    def _classify_characters(self, text: str) -> Dict[str, str]:
        """
        智能分离汉字/字母和数字

        将文本中的汉字和字母组合作为name，第一个数字序列作为code
        保持字符的原始顺序

        Args:
            text: 要分离的文本

        Returns:
            包含name和code字段的字典
        """
        # 使用正则表达式替换，保持原始顺序
        # 先提取第一个数字序列作为code
        numbers = self._NUMBER_PATTERN.findall(text)
        code = numbers[0] if numbers else ""

        # 移除所有数字，保留汉字和字母
        name = re.sub(r'\d+', '', text)
        # 移除可能的连接符和特殊字符，只保留汉字和字母
        name = re.sub(r'[^\u4e00-\u9fff\u3400-\u4dbfa-zA-Z]', '', name)

        return {"name": name, "code": code}

    def _is_pure_number(self, text: str) -> bool:
        """
        检测是否为纯数字

        Args:
            text: 要检测的字符串

        Returns:
            如果是纯数字则返回True，否则返回False
        """
        return bool(self._PURE_NUMBER_PATTERN.match(text.strip()))

    def _is_likely_code(self, text: str) -> bool:
        """
        判断字符串是否更可能是工号

        工号特征：
        1. 纯数字
        2. 包含数字且数字字符占比 >= 50%

        Args:
            text: 要判断的字符串

        Returns:
            如果更可能是工号则返回True，否则返回False
        """
        text = text.strip()
        if not text:
            return False

        # 纯数字肯定是工号
        if self._is_pure_number(text):
            return True

        # 计算数字字符占比
        digit_count = len(self._NUMBER_PATTERN.findall(text))
        total_chars = len(text)

        # 如果数字字符数量 >= 总字符数的50%，认为是工号
        return digit_count >= total_chars * 0.5

    def _is_likely_name(self, text: str) -> bool:
        """
        判断字符串是否更可能是姓名

        姓名特征：
        1. 主要由汉字组成
        2. 汉字字符占比 >= 50%

        Args:
            text: 要判断的字符串

        Returns:
            如果更可能是姓名则返回True，否则返回False
        """
        text = text.strip()
        if not text:
            return False

        # 计算汉字字符数量
        chinese_chars = self._CHINESE_CHAR_PATTERN.findall(text)
        chinese_count = sum(len(match) for match in chinese_chars)
        total_chars = len(text)

        # 如果汉字字符数量 >= 总字符数的50%，认为是姓名
        return chinese_count >= total_chars * 0.5

    def _parse_and_format_item(self, item: str) -> str:
        """
        解析单个元素并格式化为统一输出格式

        支持四种格式：
        1. 姓名（工号） - 例如：吴慧敏（051703）
        2. （工号）姓名 - 例如：（051703）吴慧敏
        3. 工号-姓名 - 例如：051703-吴慧敏
        4. 姓名-工号 - 例如：吴慧敏-051703

        Args:
            item: 要解析的字符串元素

        Returns:
            统一格式的字符串："name:姓名\ncode:工号"
        """
        item = item.strip()
        if not item:
            return "name:\ncode:"

        # 1. 匹配 姓名（工号）格式
        match = self._CHINESE_BRACKET_PATTERN.match(item)
        if match:
            name = match.group(1).strip()
            code = match.group(2).strip()
            return f"name:{name}\ncode:{code}"

        # 2. 匹配 （工号）姓名 格式
        match = self._REVERSE_CHINESE_BRACKET_PATTERN.match(item)
        if match:
            code = match.group(1).strip()
            name = match.group(2).strip()
            return f"name:{name}\ncode:{code}"

        # 3. 匹配 姓名(工号) 格式（英文括号）
        match = self._ENGLISH_BRACKET_PATTERN.match(item)
        if match:
            name = match.group(1).strip()
            code = match.group(2).strip()
            return f"name:{name}\ncode:{code}"

        # 4. 匹配短横线格式：工号-姓名 或 姓名-工号
        match = self._DASH_PATTERN.match(item)
        if match:
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()

            # 判断哪个是工号，哪个是姓名
            if self._is_likely_code(part1) and self._is_likely_name(part2):
                # 工号-姓名
                return f"name:{part2}\ncode:{part1}"
            elif self._is_likely_name(part1) and self._is_likely_code(part2):
                # 姓名-工号
                return f"name:{part1}\ncode:{part2}"
            else:
                # 无法确定，默认第一个为姓名，第二个为工号
                return f"name:{part1}\ncode:{part2}"

        # 5. 无特殊字符，尝试智能分离
        if self._is_likely_code(item):
            # 纯工号
            return f"name:\ncode:{item}"
        elif self._is_likely_name(item):
            # 纯姓名
            return f"name:{item}\ncode:"
        else:
            # 默认作为姓名处理
            return f"name:{item}\ncode:"

    def split_and_format_names(self, text: str, connectors: Optional[List[str]] = None) -> List[str]:
        """
        专门用于拆分连接字符串并格式化为统一的 name:姓名\\ncode:工号 格式

        支持四种格式：
        1. 姓名（工号） - 例如：吴慧敏（051703）
        2. （工号）姓名 - 例如：（051703）吴慧敏
        3. 工号-姓名 - 例如：051703-吴慧敏
        4. 姓名-工号 - 例如：吴慧敏-051703

        Args:
            text: 要拆分的字符串，如 "吴慧敏（051703）、张三-ABC123"
            connectors: 连接符列表，默认使用 ALL_CONNECTORS

        Returns:
            格式化后的字符串列表，每个元素格式为 "name:姓名\\ncode:工号"

        Examples:
            >>> manager = ConnectorManager()
            >>> result = manager.split_and_format_names("吴慧敏（051703）、051703-张三")
            >>> print(result)
            ['name:吴慧敏\\ncode:051703', 'name:张三\\ncode:051703']
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

        # 对每个拆分项进行格式化
        formatted_result = []
        for item in final_result:
            formatted_item = self._parse_and_format_item(item)
            formatted_result.append(formatted_item)

        return formatted_result

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

        # 确保所有元素都是字符串类型
        str_names = []
        for name in names:
            if isinstance(name, str):
                str_names.append(name)
            elif name is not None:
                str_names.append(str(name))

        if not str_names:
            return ""

        if len(str_names) == 1:
            return str_names[0]
        
        if len(str_names) == 2:
            # 两个名称，使用随机连接符
            connector = self.get_random_connector()
            return f"{str_names[0]}{connector}{str_names[1]}"

        # 多个名称，中间用标点符号，最后用连词
        result_parts = []

        # 添加前面的名称，用中间连接符连接
        for i in range(len(str_names) - 2):
            result_parts.append(str_names[i])
            result_parts.append(self.get_random_middle_connector())
        
        # 添加倒数第二个名称
        result_parts.append(str_names[-2])

        # 添加最后的连接符
        result_parts.append(self.get_random_final_connector())

        # 添加最后一个名称
        result_parts.append(str_names[-1])
        
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

    def split_connected_string(self, text: str, connectors: Optional[List[str]] = None, force_extract_numbers: bool = False) -> Union[List[str], List[Dict[str, str]]]:
        """
        将包含连接字符的字符串拆分为列表（反向连接操作）

        实现混合解析策略：
        - 如果字符串包含特殊字符（中英文括号、短横线），返回 List[Dict[str, str]] 格式
        - 如果不包含特殊字符，返回原有的 List[str] 格式

        解析优先级（从高到低）：
        1. 中文括号（）：'FJ031-01（1300）' → name='FJ031-01', code='1300'
        2. 英文括号()：'孙洪(041501)' → name='孙洪', code='041501'
        3. 短横线-：'FJ031-01' → name='FJ031', code='01'

        Args:
            text: 要拆分的字符串
                - 复杂格式：'FJ031-01（1300）、28018-7（2）'
                - 简单格式：'雷利冬、胡炽浩'
            connectors: 连接符列表，默认使用 ALL_CONNECTORS
            force_extract_numbers: 是否启用强制数字提取模式
                - True: 纯数字项目作为code，name为空；混合内容智能分离
                - False: 保持原有解析逻辑（默认）

        Returns:
            - 包含特殊字符时：List[Dict[str, str]]
              如：[{"name": "FJ031-01", "code": "1300"}, {"name": "28018-7", "code": "2"}]
            - 不包含特殊字符时：List[str]
              如：["雷利冬", "胡炽浩"]

        Examples:
            >>> manager = ConnectorManager()
            >>> # 复杂格式解析
            >>> result1 = manager.split_connected_string("FJ031-01（1300）、28018-7（2）")
            >>> print(result1)
            [{'name': 'FJ031-01', 'code': '1300'}, {'name': '28018-7', 'code': '2'}]

            >>> # 简单格式解析（向后兼容）
            >>> result2 = manager.split_connected_string("雷利冬、胡炽浩")
            >>> print(result2)
            ['雷利冬', '胡炽浩']

            >>> # 强制数字提取模式
            >>> result3 = manager.split_connected_string("吴慧敏(051703)、021137,081601", force_extract_numbers=True)
            >>> print(result3)
            [{'name': '吴慧敏', 'code': '051703'}, {'name': '', 'code': '021137'}, {'name': '', 'code': '081601'}]
        """
        if not text or not text.strip():
            return []

        # 使用默认连接符列表
        if connectors is None:
            connectors = self.ALL_CONNECTORS

        # 检测是否包含特殊字符
        has_special_chars = self._has_special_characters(text)

        # 初始化结果列表，从原始文本开始
        result = [text.strip()]

        # 依次使用每个连接符进行拆分
        for connector in connectors:
            new_result = []
            for item in result:
                # 对于模糊连接符（如"和"、"以及"），先检测是否应该跳过
                if connector in self.ambiguous_connectors:
                    if self._should_skip_ambiguous_connector(item, connector):
                        # 如果应该跳过，保持原字符串不变
                        new_result.append(item)
                        continue

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

        # 根据是否包含特殊字符或强制模式决定返回格式
        if has_special_chars or force_extract_numbers:
            # 返回 List[Dict[str, str]] 格式，传递 force_extract_numbers 参数
            return [self._parse_name_code(item, force_extract_numbers) for item in final_result]
        else:
            # 返回原有的 List[str] 格式
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

def split_connected_string(text: str, connectors: Optional[List[str]] = None, force_extract_numbers: bool = False) -> Union[List[str], List[Dict[str, str]]]:
    """
    将包含连接字符的字符串拆分为列表的便捷方法

    实现混合解析策略：
    - 如果字符串包含特殊字符（中英文括号、短横线），返回 List[Dict[str, str]] 格式
    - 如果不包含特殊字符，返回原有的 List[str] 格式

    解析优先级（从高到低）：
    1. 中文括号（）：'FJ031-01（1300）' → name='FJ031-01', code='1300'
    2. 英文括号()：'孙洪(041501)' → name='孙洪', code='041501'
    3. 短横线-：'FJ031-01' → name='FJ031', code='01'

    Args:
        text: 要拆分的字符串
            - 复杂格式：'FJ031-01（1300）、28018-7（2）'
            - 简单格式：'雷利冬、胡炽浩'
        connectors: 连接符列表，默认使用 ALL_CONNECTORS
        force_extract_numbers: 是否启用强制数字提取模式
            - True: 纯数字项目作为code，name为空；混合内容智能分离
            - False: 保持原有解析逻辑（默认）

    Returns:
        - 包含特殊字符时：List[Dict[str, str]]
          如：[{"name": "FJ031-01", "code": "1300"}, {"name": "28018-7", "code": "2"}]
        - 不包含特殊字符时：List[str]
          如：["雷利冬", "胡炽浩"]

    Examples:
        >>> # 复杂格式解析
        >>> result1 = split_connected_string("FJ031-01（1300）、28018-7（2）")
        >>> print(result1)
        [{'name': 'FJ031-01', 'code': '1300'}, {'name': '28018-7', 'code': '2'}]

        >>> # 简单格式解析（向后兼容）
        >>> result2 = split_connected_string("雷利冬、胡炽浩")
        >>> print(result2)
        ['雷利冬', '胡炽浩']

        >>> # 强制数字提取模式
        >>> result3 = split_connected_string("吴慧敏(051703)、021137,081601", force_extract_numbers=True)
        >>> print(result3)
        [{'name': '吴慧敏', 'code': '051703'}, {'name': '', 'code': '021137'}, {'name': '', 'code': '081601'}]
    """
    return get_connector_service().split_connected_string(text, connectors, force_extract_numbers)

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

    # 测试混合解析策略
    print("\n=== 混合解析策略测试 ===")

    # 测试包含特殊字符的复杂格式（返回 List[Dict[str, str]]）
    print("1. 复杂格式测试（包含特殊字符）：")
    complex_test_cases = [
        "FJ031-01（1300）、28018-7（2）",
        "孙洪（041501）、雷利冬、胡炽浩",
        "26012（1）、28018-7（2）、522001（26）、524021（5）",
        "孙洪(041501)、张三-001"
    ]

    for test_string in complex_test_cases:
        result = split_connected_string(test_string)
        print(f"  原字符串: {test_string}")
        print(f"  拆分结果: {result}")
        print(f"  返回类型: List[Dict] (包含 name 和 code 字段)")
        print()

    # 测试不包含特殊字符的简单格式（返回 List[str]）
    print("2. 简单格式测试（不包含特殊字符）：")
    simple_test_cases = [
        "雷利冬、胡炽浩",
        "项目A、项目B、项目C",
        "张三，李四，王五"
    ]

    for test_string in simple_test_cases:
        result = split_connected_string(test_string)
        print(f"  原字符串: {test_string}")
        print(f"  拆分结果: {result}")
        print(f"  返回类型: List[str] (向后兼容)")
        print()

    # 演示解析优先级
    print("3. 解析优先级演示：")
    priority_test = "FJ031-01（1300）"  # 同时包含短横线和中文括号
    result = split_connected_string(priority_test)
    print(f"  测试字符串: {priority_test}")
    print(f"  解析结果: {result}")
    print(f"  说明: 中文括号优先级高于短横线，name='FJ031-01', code='1300'")
    print()

    # 测试强制数字提取模式
    print("4. 强制数字提取模式测试：")
    force_test_cases = [
        "吴慧敏(051703)、021137,081601",  # 混合：括号+纯数字
        "文林101409向文静林桂涛",         # 智能字符分离
        "FJ031ABC456DEF789",            # 字母数字混合
        "12345、67890、13579",          # 纯数字序列
        "纯汉字内容、PureEnglish"        # 纯汉字和纯字母
    ]

    for test_string in force_test_cases:
        result_normal = split_connected_string(test_string)
        result_force = split_connected_string(test_string, force_extract_numbers=True)
        print(f"  原字符串: {test_string}")
        print(f"  普通模式: {result_normal}")
        print(f"  强制模式: {result_force}")
        print(f"  说明: 强制模式下纯数字作为code，混合内容智能分离")
        print()

    # 测试智能字符分离功能
    print("5. 智能字符分离功能演示：")
    intelligent_test_cases = [
        "文林以及101409向文静以及林桂涛",  # 用户原始需求
        "中文English123数字456",         # 多种字符混合
        "ABC123DEF456GHI789",           # 字母数字交替
        "项目A101项目B202项目C303"        # 汉字数字模式
    ]

    for test_string in intelligent_test_cases:
        result = split_connected_string(test_string, force_extract_numbers=True)
        print(f"  原字符串: {test_string}")
        print(f"  智能分离结果: {result}")
        # 分析每个结果
        for i, item in enumerate(result):
            if isinstance(item, dict):
                print(f"    项目{i+1}: name='{item['name']}', code='{item['code']}'")
        print()

    # 测试边界情况
    print("6. 边界情况测试：")
    edge_test_cases = [
        ("", "空字符串"),
        ("纯汉字内容", "纯汉字"),
        ("PureEnglishText", "纯字母"),
        ("1234567890", "纯数字"),
        ("特殊符号!@#$%", "特殊符号"),
        ("  空格测试  ", "带空格")
    ]

    for test_string, description in edge_test_cases:
        try:
            result_normal = split_connected_string(test_string)
            result_force = split_connected_string(test_string, force_extract_numbers=True)
            print(f"  {description}: '{test_string}'")
            print(f"    普通模式: {result_normal}")
            print(f"    强制模式: {result_force}")
        except Exception as e:
            print(f"  {description}: '{test_string}' - 错误: {e}")
        print()

    print("=== 测试完成 ===")
    print("说明：")
    print("- 普通模式：保持原有解析逻辑，向后兼容")
    print("- 强制模式：启用智能字符分离和强制数字提取")
    print("- 解析优先级：中文括号 > 英文括号 > 短横线 > 智能分离")
