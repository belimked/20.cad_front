#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any
import random  # 添加random模块导入
from src.service.common import (
    get_base_elements, get_available_base_elements,
    get_answer_elements, get_available_answer_elements,
    get_business_rules, get_available_business_rules,
    get_connection_pairs, get_random_string_connector
)


class RuleLogicService:
    """
    规则逻辑服务类，用于整合基础元素、回答元素和业务规则数据，
    并提供按规则复杂度排序等功能
    """

    def __init__(self):
        """
        初始化规则逻辑服务
        """
        pass

    def _process_project_field(self, field_name: str, value: str) -> str:
        """
        处理包含project、supplier或engineering的字段名，随机应用相应的名称模式
        
        Args:
            field_name: 字段名称
            value: 原始值
            
        Returns:
            处理后的字符串
        """
        # 使用不区分大小写的字符串比较
        # 处理包含project的字段
        if 'project' in field_name.lower() and 'personprojectquery' not in field_name.lower() and 'projectpersonquery' not in field_name.lower() and 'projectstatusquery' not in field_name.lower():
            # 定义项目名称模式
            project_patterns = ["项目XX", "XX项目", "是XX项目", "项目是XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(project_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)

        # 处理包含supplier的字段
        elif 'supplier' in field_name.lower():
            # 定义供应商名称模式
            supplier_patterns = ["供应商XX", "XX", "XX供应商", "供应商是XX", "XX的", "供应商是XX的", "是XX的", "XX厂家",
                                 "厂家XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(supplier_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)

        # 处理包含engineering的字段
        elif 'engineering' in field_name.lower() or 'materialengineeringproperties' in field_name.lower():
            # 定义工程属性模式
            if '属性' in value:
                return value
            engineering_patterns = ["工程属性XX", "工程属性是XX", "XX属性", "属性为XX", "XX材料属性", "材料属性XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        # 处理包含engineering的字段
        # 处理包含engineering的字段
        elif 'materialcode' in field_name.lower():
            # 定义工程属性模式
            if '编号' in value:
                return value
            engineering_patterns = ["编号XX", "材料编号是XX", "材料编号是XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        # 处理包含engineering的字段
        # 处理包含engineering的字段
        elif 'propertycode' in field_name.lower():
            # 定义工程属性模式
            if '属性' in value:
                return value
            engineering_patterns = ["包含工程属性代码XX",
                                    "包含工程属性XX",
                                    "包含属性XX",
                                    "包含材料属性XX",
                                    "含工程属性代码XX",
                                    "含工程属性XX",
                                    "含属性XX",
                                    "含材料属性XX",
                                    "含有工程属性代码XX",
                                    "含有工程属性XX",
                                    "含有属性XX",
                                    "含有材料属性XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        # 处理包含engineering的字段
        elif 'drawinginfo' in field_name.lower() or 'processdrawing' in field_name.lower():
            # 定义工程属性模式
            engineering_patterns = ["包含工艺图XX",
                                    "包含图纸XX",
                                    "包含XX工艺图",
                                    "包含XX图纸",
                                    "包含图XX",
                                    "包含XX图",
                                    "含工艺图XX",
                                    "含图纸XX",
                                    "含XX工艺图",
                                    "含XX图纸",
                                    "含图XX",
                                    "含XX图",
                                    "含有工艺图XX",
                                    "含有图纸XX",
                                    "含有XX工艺图",
                                    "含有XX图纸",
                                    "含有图XX",
                                    "含有XX图"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)

        # 处理包含engineering的字段
        elif 'deliverynumber' in field_name.lower() or 'deliverynumberwithquantity' in field_name.lower()  or 'deliverynumberonly' in field_name.lower()  or 'invoicenumber' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '送货' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["送货单号XX","送货单号:XX","送货单:XX", "送货单号为XX", "供应商送货单号XX", "供应商送货单号为XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        elif 'cargonumberwithquantity' in field_name.lower() or 'cargonumberonly' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '发货' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["单XX",
                                    "XX单",
                                    "单号是XX",
                                    "XX的单",
                                    "发货单XX",
                                    "发货单号：XX",
                                    "发货单号XX",
                                    "货单号XX",
                                    "货单XX",
                                    "货单号：XX",
                                    "发货单：XX",
                                    "XX发货单",
                                    "发货单为XX",
                                    "发货单是XX",
                                    "结算单XX",
                                    "XX结算单",
                                    "结算单为XX",
                                    "结算单是XX"
                                    ]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        elif 'relatedinvoice' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '送货' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["关联送货单号XXX", "送货货单XX相关", "与送货单XXX相关", "与送货单XXX关联"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        elif 'auditnumber' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '审核' in value or '结算' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["审核单XX",
                                    "审核单号是XX",
                                    "单号为XX",
                                    "单号是XX",
                                    "结算审核单XX",
                                    "结算审核单为XX",
                                    "结算审核单是XX",
                                    "结算单XX",
                                    "结算单为XX",
                                    "结算单是XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        elif 'businessnumber' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '合同' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["合同XX", "XX合同", "合同号是XX", "合同为XX", "合同是XX", "审核单XX", "XX审核单",
                                    "审核单是XX", "审核单为XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)
        elif 'ordernumber' in field_name.lower() or 'relatedorder' in field_name.lower():
            # 如果value中已包含“送货”，直接返回原始值
            if '订单' in value:
                return value
            # 定义工程属性模式
            engineering_patterns = ["含订单XX",
                                    "材料所属订单XX",
                                    "包含订单XX",
                                    "含有订单XX",
                                    "含订单XX",
                                    "材料所属订单编号XX",
                                    "包含订单编号XX",
                                    "含有订单编号XX",
                                    "含订单编号XX",
                                    "材料所属订单号XX",
                                    "包含订单号XX",
                                    "含有订单号XX",
                                    "含订单号XX"]
            # 随机选择一个模式
            selected_pattern = random.choice(engineering_patterns)
            # 将模式中的XX替换为原始值
            return selected_pattern.replace("XX", value)

        # 如果字段名不包含project、supplier或engineering，返回原始值
        return value

    def get_rule_components(self, business_object: str) -> Tuple[Dict, Dict, Dict]:
        """
        获取指定业务对象的三个数据集合：基础元素、业务规则和回答元素
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            包含三个数据集合的元组：(基础元素, 业务规则, 回答元素)
        """
        # 获取基础元素数据
        base_elements_data = get_base_elements(business_object)

        # 获取业务规则数据
        business_rules_data = get_business_rules(f"{business_object}Rules")

        # 获取回答元素数据
        answer_elements_data = get_answer_elements(business_object)

        return (base_elements_data, business_rules_data, answer_elements_data)

    def get_sorted_rules(self, business_object: str) -> List[Dict]:
        """
        获取按codecount排序的规则集合
        
        Args:
            business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
            
        Returns:
            按codecount降序排列的规则列表
        """
        # 获取业务规则数据
        business_rules_data = get_business_rules(f"{business_object}Rules")

        # 提取规则列表
        rules = business_rules_data.get('rulesMap', [])

        # 按codecount降序排序
        sorted_rules = sorted(rules, key=lambda x: x.get('codecount', 0), reverse=True)

        return sorted_rules

    def _check_connection_exists(self, code1: str, code2: str, business_object: str) -> bool:
        """
        检查两个编码之间是否存在连接关系
        
        Args:
            code1: 第一个编码
            code2: 第二个编码  
            business_object: 业务对象名称
            
        Returns:
            如果存在连接关系返回True，否则返回False
        """
        try:
            # 获取业务对象的连接关系对
            connection_pairs = get_connection_pairs(business_object)

            # 检查连接关系（单向匹配）
            for pair in connection_pairs:
                if pair[0] == code1 and pair[1] == code2:
                    return True

            return False
        except Exception:
            # 如果获取连接关系失败，默认没有连接关系
            return False

    def format_question_by_codebase(self, question_dict: Dict, codebase: str,
                                    business_object: str = 'updateCargo') -> str:
        """
        根据 codebase 和问题字典生成格式化的问题文本
        
        Args:
            question_dict: 包含问题字段的字典
            codebase: 格式为 "xx;xx|xx" 或 "xx;xx|(xx&xx)" 的编码字符串
            business_object: 业务对象名称，默认为 updateCargo
            
        Returns:
            按照 codebase 顺序排列的问题文本。只有在相邻编码存在连接关系时才插入连接符（中文或英文逗号）
        """
        # 获取基础元素数据
        base_elements_data = get_base_elements(business_object)
        base_data_list = base_elements_data.get('baseDataList', [])

        # 构建编码到字段名的映射
        field_mapping = {}
        for base_element in base_data_list:
            number = base_element.get('number')
            name = base_element.get('name')
            if number and name:
                field_mapping[number] = name

        # 解析 codebase 并生成问题文本
        question_parts = []
        # 首先按;分隔
        code_segments = codebase.split(';')

        for segment in code_segments:
            # 如果段落包含|，则分别处理每个编码或编码组
            if '|' in segment:
                code_groups = segment.split('|')
                for code_group in code_groups:
                    # 检查是否是由&连接的编码组
                    if '&' in code_group:
                        # 处理&连接的编码组，必须所有编码都存在对应的问题字段
                        sub_codes = code_group.strip('()').split('&')
                        all_fields_present = True
                        sub_parts = []

                        for sub_code in sub_codes:
                            field_name = field_mapping.get(sub_code)
                            if field_name and field_name in question_dict:
                                qstrvalue = str(question_dict[field_name])
                                # 处理包含project的字段名，只有长度大于2时才处理
                                if len(qstrvalue) > 2:
                                    qstrvalue = self._process_project_field(field_name, qstrvalue)
                                sub_parts.append(qstrvalue)
                            else:
                                all_fields_present = False
                                break

                        # 只有当所有字段都存在时，才添加到问题部分
                        if all_fields_present and sub_parts:
                            question_parts.extend(sub_parts)
                    else:
                        # 处理单个编码
                        field_name = field_mapping.get(code_group)
                        if field_name and field_name in question_dict:
                            qstrvalue = str(question_dict[field_name])
                            # 处理包含project的字段名，只有长度大于2时才处理
                            if len(qstrvalue) > 2:
                                qstrvalue = self._process_project_field(field_name, qstrvalue)
                            question_parts.append(qstrvalue)
            else:
                # 处理单个编码
                field_name = field_mapping.get(segment)
                if field_name and field_name in question_dict:
                    qstrvalue = str(question_dict[field_name])
                    # 处理包含project的字段名，只有长度大于2时才处理
                    if len(qstrvalue) > 2:
                        qstrvalue = self._process_project_field(field_name, qstrvalue)
                    question_parts.append(qstrvalue)

        # 如果没有问题部分，返回空字符串
        if not question_parts:
            return ""

        # 如果只有一个部分，直接返回
        if len(question_parts) == 1:
            return question_parts[0]

        # 需要重新解析codebase来获取编码序列，用于连接关系判断
        code_sequence = []
        code_segments = codebase.split(';')

        for segment in code_segments:
            if '|' in segment:
                code_groups = segment.split('|')
                # 对于OR组合，只选择第一个匹配的分支
                for code_group in code_groups:
                    added_to_sequence = False
                    if '&' in code_group:
                        sub_codes = code_group.strip('()').split('&')
                        # 对于&连接的编码组，检查所有编码是否都有对应字段
                        all_present = True
                        for sub_code in sub_codes:
                            field_name = field_mapping.get(sub_code)
                            if not (field_name and field_name in question_dict):
                                all_present = False
                                break
                        if all_present:
                            code_sequence.extend(sub_codes)
                            added_to_sequence = True
                            break  # OR组合只选择第一个匹配的分支
                    else:
                        field_name = field_mapping.get(code_group)
                        if field_name and field_name in question_dict:
                            code_sequence.append(code_group)
                            added_to_sequence = True
                            break  # OR组合只选择第一个匹配的分支
            else:
                field_name = field_mapping.get(segment)
                if field_name and field_name in question_dict:
                    code_sequence.append(segment)

        # 定义可能的连接符列表（仅中英文逗号）
        connectors = [",", "，"]

        # 基于连接关系智能拼接
        result_parts = [question_parts[0]]  # 第一个部分直接添加

        for i in range(1, len(question_parts)):
            # 检查前一个编码和当前编码是否存在连接关系
            if i - 1 < len(code_sequence) and i < len(code_sequence):
                previous_code = code_sequence[i - 1]
                current_code = code_sequence[i]

                # 如果不存在连接关系，插入随机选择的连接符
                if previous_code and current_code and not self._check_connection_exists(previous_code, current_code,
                                                                                        business_object):
                    connector = random.choice(connectors)
                    if len(question_parts[i]) > 0 and len(question_parts[i - 1]) > 0:
                        result_parts.append(connector)

            # 添加当前问题部分
            result_parts.append(question_parts[i])

        # 返回拼接后的问题文本
        return "".join(result_parts)

    def format_answer_to_cn(self, answer_dict: Dict, business_object: str = 'updateStaff') -> str:
        """
        将原始答案字典转换为包含中文字段名的JSON字符串
        
        Args:
            answer_dict: 原始答案字典，包含英文字段名
            business_object: 业务对象名称，默认为 updateStaff
            
        Returns:
            包含中文字段名的JSON字符串
        """
        # 获取回答元素数据
        answer_elements_data = get_answer_elements(business_object)
        answer_elements_list = answer_elements_data.get('answerElements', [])

        # 构建英文字段名到中文字段名的映射
        field_mapping = {}
        for element in answer_elements_list:
            name = element.get('name')
            name_cn = element.get('nameCN')
            if name and name_cn:
                field_mapping[name] = name_cn

        # 创建新的字典，使用中文字段名
        result_dict = {}
        for key, value in answer_dict.items():
            # 获取中文字段名，如果不存在则使用原始字段名
            cn_key = field_mapping.get(key, key)
            # 如果值为空，则设置为"无"
            result_dict[cn_key] = value if value else "无"

        # 将字典转换为JSON字符串
        import json
        return json.dumps(result_dict, ensure_ascii=False)


# 单例模式
_instance = None


def get_rule_logic_service() -> RuleLogicService:
    """
    获取规则逻辑服务的单例实例
    
    Returns:
        RuleLogicService实例
    """
    global _instance
    if _instance is None:
        _instance = RuleLogicService()
    return _instance


# 便捷方法
def get_rule_components(business_object: str) -> Tuple[Dict, Dict, Dict]:
    """
    获取指定业务对象的三个数据集合的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        包含三个数据集合的元组：(基础元素, 业务规则, 回答元素)
    """
    return get_rule_logic_service().get_rule_components(business_object)


def get_sorted_rules(business_object: str) -> List[Dict]:
    """
    获取按codecount排序的规则集合的便捷方法
    
    Args:
        business_object: 业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)
        
    Returns:
        按codecount降序排列的规则列表
    """
    return get_rule_logic_service().get_sorted_rules(business_object)


def format_question_by_codebase(question_dict: Dict, codebase: str, business_object: str = 'updateCargo') -> str:
    """
    根据 codebase 和问题字典生成格式化的问题文本的便捷方法
    
    Args:
        question_dict: 包含问题字段的字典
        codebase: 格式为 "xx;xx|xx" 或 "xx;xx|(xx&xx)" 的编码字符串
        business_object: 业务对象名称，默认为 updateCargo
        
    Returns:
        按照 codebase 顺序排列的问题文本。只有在相邻编码存在连接关系时才插入连接符（中文或英文逗号）
    """
    return get_rule_logic_service().format_question_by_codebase(question_dict, codebase, business_object)


def format_answer_to_cn(answer_dict: Dict, business_object: str = 'updateStaff') -> str:
    """
    将原始答案字典转换为包含中文字段名的JSON字符串的便捷方法
    
    Args:
        answer_dict: 原始答案字典，包含英文字段名
        business_object: 业务对象名称，默认为 updateStaff
        
    Returns:
        包含中文字段名的JSON字符串
    """
    return get_rule_logic_service().format_answer_to_cn(answer_dict, business_object)


# 使用示例
if __name__ == "__main__":
    # 获取searchStaff的规则组件
    base_elements, business_rules, answer_elements = get_rule_components('searchStaff')
    print(f"基础元素数量: {len(base_elements.get('baseDataList', []))}")
    print(f"业务规则数量: {len(business_rules.get('rulesMap', []))}")
    print(f"回答元素数量: {len(answer_elements.get('answerElements', []))}")

    # 获取排序后的规则列表
    sorted_rules = get_sorted_rules('searchStaff')
    print("排序后的规则列表:")
    for rule in sorted_rules:
        print(f"规则ID: {rule.get('id')}, 名称: {rule.get('name')}, 复杂度: {rule.get('codecount')}")

        # 测试问题格式化
    question_dict = {
        'deliveryNumberWithQuantity': '送货单号NOP9012（67.89）',
        'projectInfo': '金地上海松江项目项目',
        'cargoNumberWithQuantity': '发货单GHI2345（6000）'
    }
    codebase = "05;03|04"

    formatted_question = format_question_by_codebase(question_dict, codebase)
    print("\n根据codebase格式化的问题:")
    print(formatted_question)
