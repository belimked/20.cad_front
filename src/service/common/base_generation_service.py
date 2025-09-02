#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional, Type, Callable
import random
import math
import importlib


class BaseGenerationService:
    """
    基础数据生成服务类，提供通用的数据生成逻辑
    作为各种生成服务的共同父类，提供单例管理和通用方法
    """

    # 添加单例注册表，用于管理所有服务实例
    _instances = {}

    def __init__(self):
        """
        初始化基础数据生成服务
        """
        pass

    @classmethod
    def get_instance(cls) -> 'BaseGenerationService':
        """
        获取当前类的单例实例
        
        Returns:
            当前类的单例实例
        """
        if cls not in cls._instances:
            cls._instances[cls] = cls()
        return cls._instances[cls]

    @classmethod
    def register_service(cls, service_class: Type['BaseGenerationService']) -> None:
        """
        注册服务类到单例系统
        
        Args:
            service_class: 要注册的服务类
        """
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()

    @classmethod
    def get_service(cls, service_class: Type['BaseGenerationService']) -> 'BaseGenerationService':
        """
        获取指定服务类的实例
        
        Args:
            service_class: 服务类
            
        Returns:
            服务类的单例实例
        """
        if service_class not in cls._instances:
            cls._instances[service_class] = service_class()
        return cls._instances[service_class]

    def calculate_rule_weights(self, business_object: str, total_samples: int = 200) -> List[Dict]:
        """
        计算规则权重并分配生成份额
        
        Args:
            business_object: 业务对象名称，如 searchStaff, updateStaff
            total_samples: 总样本数，默认200
            
        Returns:
            包含规则和对应份额的列表
        """
        # 延迟导入，避免循环导入问题
        from src.service.rule_logic import get_sorted_rules

        # 获取排序后的规则
        sorted_rules = get_sorted_rules(business_object)

        # 计算总权重
        total_weight = sum(rule.get('codecount', 0) for rule in sorted_rules)

        # 分配份额
        rule_shares = []
        for rule in sorted_rules:
            weight = rule.get('codecount', 0)
            # 计算该规则应分配的份额
            share = math.floor(weight * total_samples / total_weight) if total_weight > 0 else 0
            share = max(1, share)  # 确保至少有1个样本

            # 获取codeList集合长度
            code_list = rule.get('codeList', [])
            code_list_length = len(code_list) if isinstance(code_list, list) else 1

            # 如果share小于codeList长度，则将share设为codeList长度
            if share < code_list_length:
                # print(f"规则 {rule.get('id', '')}: 原始share={share}，codeList长度={code_list_length}，调整share")
                share = code_list_length

            rule_shares.append({
                'rule': rule,
                'share': share
            })

        return rule_shares

    def generate_base_question(self, rule: Dict, base_elements: Dict, combo_index: int = -1) -> Tuple[Dict, Dict]:
        """
        生成基础问题数据（两个服务类共享的部分）
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            combo_index: 指定使用codeList中的哪个组合，-1表示随机选择
            
        Returns:
            问题数据和需要处理的字典元素
        """
        # 获取规则中的codeList并处理
        code_list = []

        # 处理各种可能的codeList格式
        code_list_value = rule.get('codeList', [])
        # print(f"原始codeList值: {code_list_value}, 类型: {type(code_list_value)}")

        if isinstance(code_list_value, list) and code_list_value:
            # 从codeList中选择一个组合进行处理
            if combo_index >= 0 and combo_index < len(code_list_value):
                # 使用指定索引的组合
                selected_combo = code_list_value[combo_index]
                # print(f"使用指定的组合索引 {combo_index}: {selected_combo}")
            else:
                # 随机选择一个组合
                selected_combo = random.choice(code_list_value)
                # print(f"随机选择组合: {selected_combo}")

            # 处理选定的组合
            if isinstance(selected_combo, str):
                # 如果组合是字符串且包含分隔符，则分割
                if ';' in selected_combo:
                    code_list = selected_combo.split(';')
                else:
                    code_list = [selected_combo]
            else:
                # 非字符串元素，转为字符串后添加
                code_list = [str(selected_combo)]
        elif isinstance(code_list_value, str):
            # 如果整个codeList是一个字符串，按分隔符分割
            if code_list_value:
                code_list = code_list_value.split(';')

        # print(f"使用的code_list组合: {code_list}")

        # 获取基础元素列表
        base_data_list = base_elements.get('baseDataList', [])

        # 映射元素号到元素定义
        element_map = {item.get('number', ''): item for item in base_data_list}

        # 生成问题数据
        question_data = {}
        # 存储需要处理字典替换的元素
        elements_with_dict = {}
        # 跟踪每个字段名已使用的条件，避免重复
        used_conditions_by_field = {}

        # 生成基本问题数据，标记需要处理字典的元素
        field_occurrence_count = {}  # 跟踪每个字段名的出现次数

        for code in code_list:
            if code and code in element_map:
                element = element_map[code]
                element_name = element.get('name', '')
                # print(f"处理元素: {code}, 名称: {element_name}")

                # 检查元素是否有字典列表或条件列表
                dict_list = element.get('dictlist', [])
                conditions = element.get('conditionList', [])

                # 处理字段名重复的情况
                actual_field_name = element_name
                if element_name in question_data:
                    # 字段名已存在，需要创建唯一的字段名
                    field_occurrence_count[element_name] = field_occurrence_count.get(element_name, 1) + 1
                    actual_field_name = f"{element_name}_{field_occurrence_count[element_name]}"
                    # print(f"字段名重复，使用新字段名: {actual_field_name}")

                # 修改：同时考虑dictlist和conditionList，只要有一个不为空，就添加到elements_with_dict
                if dict_list or conditions:
                    elements_with_dict[actual_field_name] = {
                        'code': code,
                        'element': element,
                        'dict_list': dict_list
                    }

                # 从元素的conditionList中随机选择一个条件
                if conditions:
                    # 获取该字段名已使用的条件
                    used_conditions = used_conditions_by_field.get(element_name, set())

                    # 获取可用的条件（排除已使用的）
                    available_conditions = [c for c in conditions if c not in used_conditions]

                    # 如果没有可用条件，重置已使用条件列表
                    if not available_conditions:
                        used_conditions = set()
                        available_conditions = conditions

                    # 从可用条件中随机选择
                    condition = random.choice(available_conditions)

                    # 记录已使用的条件
                    if element_name not in used_conditions_by_field:
                        used_conditions_by_field[element_name] = set()
                    used_conditions_by_field[element_name].add(condition)

                    # print(f"字段 {element_name} (实际: {actual_field_name}) 选择的condition: {condition}, 已使用: {used_conditions_by_field[element_name]}")

                    # 处理不同类型的condition
                    if isinstance(condition, dict):
                        condition_text = condition.get('text', '')
                    elif isinstance(condition, str):
                        condition_text = condition
                    else:
                        condition_text = str(condition)

                    question_data[actual_field_name] = condition_text
                    # print(f"添加问题数据: {actual_field_name} = {condition_text}")

        return question_data, elements_with_dict

    def process_special_elements(self, question_data: Dict, elements_with_dict: Dict) -> Dict:
        """
        处理特殊元素，如字典替换等
        提供默认的字典替换实现，子类可以重写
        
        Args:
            question_data: 问题数据
            elements_with_dict: 需要特殊处理的元素
            
        Returns:
            处理后的问题数据
        """
        # 处理需要字典替换的元素
        for element_name, data in elements_with_dict.items():
            element = data['element']
            dict_list = data['dict_list']

            # 目前值，可能包含XX占位符
            current_value = question_data.get(element_name, "")

            # 遍历字典列表
            for dict_mapping in dict_list:
                # 延迟导入，避免循环导入问题
                from src.service.common import get_dict_by_element_mapping

                # 根据映射获取字典
                dict_item = get_dict_by_element_mapping(dict_mapping)
                if dict_item:
                    # 处理字典替换
                    processed_value = self.process_dict_replacement(element_name, current_value, dict_mapping,
                                                                    dict_item)
                    question_data[element_name] = processed_value

        return question_data

    def process_dict_replacement(self, element_name, current_value, dict_mapping, dict_item):
        """
        处理字典替换
        
        Args:
            element_name: 元素名称
            current_value: 当前值
            dict_mapping: 字典映射
            dict_item: 字典项
            
        Returns:
            处理后的值
        """
        # 如果字典项为None，则返回原值
        if dict_item is None:
            return current_value

        # 检查是否是项目或供应商字典
        dict_name = ""
        if ":" in dict_mapping:
            _, dict_name = dict_mapping.split(":", 1)

        # 特殊处理项目和供应商字典，返回多个项并用特定连接符连接
        if dict_name in ["projects", "vendors", "persons", "drawings", "businessNumbers", "userRoles", "staffInfos", "staffNumbers", "packageNumbers", "packageNumbers_ext", "material_code_dict" ,"materials"]:
            # 延迟导入，避免循环导入问题
            from src.service.common import get_dict

            # 随机决定选择1-3个项
            count = random.randint(1, 3)
            dict_items = get_dict(dict_name, count, random_select=True)

            if not dict_items:
                return current_value

            # 提取项目名称或供应商名称
            names = []
            for item in dict_items:
                name = None
                if dict_name == "projects" and "projectname" in item:
                    name = item["projectname"]
                elif dict_name == "vendors" and "vendorname" in item:
                    name = item["vendorname"]
                elif dict_name == "persons" and "name" in item:
                    name = item["name"]
                elif dict_name == "businessNumbers" and "number" in item:
                    name = item["number"]
                elif dict_name == "staffInfos" and "staffInfo" in item:
                    name = item["staffInfo"]
                elif dict_name == "staffNumbers" and "staffNumber" in item:
                    name = item["staffNumber"]
                elif dict_name == "userRoles" and "rolename" in item:
                    name = item["rolename"]
                elif dict_name == "packageNumbers" and "packageNumber" in item:
                    name = item["packageNumber"]
                elif dict_name == "packageNumbers_ext" and "packageNumber" in item:
                    name = item["packageNumber"]
                elif dict_name == "material_code_extended_dict" and "itemCode" in item:
                    name = item["itemCode"]
                elif dict_name == "drawings" and "drawname" in item:
                    name = item["drawname"]
                elif dict_name == "materials" and "engineeringProperties" in item:
                    name = item["engineeringProperties"]
                elif dict_name == "material_code_dict" and "itemCode" in item:
                    name = item["itemCode"]
                elif "name" in item:
                    name = item["name"]

                if name:
                    names.append(name)

            # 如果没有提取到名称，返回原值
            if not names:
                return current_value

            # 使用智能连接符连接多个名称（支持随机连接符）
            from . import join_names_smart
            return join_names_smart(names)

        # 特殊处理：cargoNumberWithQuantity 和 deliveryNumberWithQuantity 替换XX为packageNumber
        if element_name in ['cargoNumberWithQuantity', 'deliveryNumberWithQuantity', 'cargoNumberonly',
                            'deliveryNumberonly']:
            # 检查packageNumber字段
            if 'packageNumber' in dict_item and 'XX' in current_value:
                package_number = dict_item['packageNumber']
                # 保留模板格式，只替换XX占位符
                result = current_value.replace('XX', package_number)
                print(f"特殊处理字段 {element_name}: 模板'{current_value}'替换XX为'{package_number}'，结果：'{result}'")
                return result

        # 检查支持的占位符列表
        placeholders = ['XX', 'YY', 'ZZ']
        placeholder_found = False

        for placeholder in placeholders:
            if placeholder in current_value:
                placeholder_found = True
                # 尝试获取字典数据
                dict_data = None

                # 检查字典项结构
                if isinstance(dict_item, dict):
                    # 根据元素名称和字典数据进行特殊处理
                    if element_name == 'projectInfo':
                        if 'projectname' in dict_item:
                            return dict_item['projectname']
                    elif element_name == 'drawingNo':
                        if 'drawname' in dict_item:
                            # return dict_item['drawname']
                            return current_value.replace('XX', str(dict_item['drawname']))
                    elif element_name == 'sourceProject' or element_name == 'targetProjects':
                        if 'projectname' in dict_item:
                            # return dict_item['drawname']
                            return current_value.replace('XX', str(dict_item['projectname']))
                    elif element_name == 'processDrawing':
                        if 'drawname' in dict_item:
                            # return dict_item['drawname']
                            return current_value.replace('XX', str(dict_item['drawname']))
                    elif element_name == 'engineeringProperties':
                        if 'itemCode' in dict_item:
                            # return dict_item['drawname']
                            return current_value.replace('XX', str(dict_item['itemCode']))
                    # 添加对materialCode的支持
                    elif element_name == 'materialCode':
                        if 'itemCode' in dict_item:
                            # 使用条件列表中的模板，替换XX为价格
                            return current_value.replace('XX', str(dict_item['itemCode']))
                    elif element_name == 'relatedOrder':
                        if 'number' in dict_item:
                            # 使用条件列表中的模板，替换XX为价格
                            return current_value.replace('XX', str(dict_item['number']))
                    # 添加对vendorName的支持
                    elif element_name == 'supplierInfo':
                        if 'vendorname' in dict_item:
                            return dict_item['vendorname']
                    # 添加对personInfo的支持
                    elif element_name == 'personInfo':
                        if 'name' in dict_item:
                            return dict_item['name']
                    # 添加对personInfo的支持
                    elif element_name == 'amountCondition':
                        if 'price' in dict_item:
                            # 使用条件列表中的模板，替换XX为价格
                            return current_value.replace('XX', str(dict_item['price']))
                            # condition_template = random.choice(element.get('conditionList', ['XX']))
                            # return condition_template.replace('XX', str(dict_item['price']))

                    # 添加对personInfo的支持
                    elif element_name == 'orderNumber':
                        if 'number' in dict_item:
                            # 使用条件列表中的模板，替换XX为价格
                            return current_value.replace('XX', str(dict_item['number']))
                    elif element_name == 'deliveryNumber' or element_name == 'cargoNumber' or element_name == 'auditNumber':
                        if 'number' in dict_item:
                            # 使用条件列表中的模板，替换XX为价格
                            return current_value.replace('XX', str(dict_item['number']))
                            # condition_template = random.choice(element.get('conditionList', ['XX']))
                            # return condition_template.replace('XX', str(dict_item['price']))

                    # 通用字段尝试
                    for key in ['name', 'projectname', 'value', 'text', 'id', 'code', 'staffNumber', 'businessNumber',
                                'number', 'drawname', 'materialcode', 'vendorname']:
                        if key in dict_item:
                            return dict_item[key]
                # 如果字典项是字符串，直接返回
                elif isinstance(dict_item, str):
                    return dict_item
                # 如果字典项是列表，随机选择一个
                elif isinstance(dict_item, list) and dict_item:
                    random_item = random.choice(dict_item)
                    if isinstance(random_item, dict):
                        # 尝试提取字典中的合适字段
                        for key in ['name', 'projectname', 'value', 'text', 'id', 'code', 'staffNumber',
                                    'businessNumber',
                                    'number', 'drawname', 'materialcode', 'vendorname']:
                            if key in random_item:
                                return random_item[key]
                        # 如果没有找到合适的属性，返回第一个值
                        if random_item:
                            return list(random_item.values())[0]
                    else:
                        return str(random_item)

        # 如果没有占位符，或者字典为空，保持原值
        return current_value

    def add_element_to_question(self, question_data: Dict, code_list: List, element_map: Dict, element_code: str,
                                element_key: str):
        """
        向问题数据中添加元素，提供给子类使用的通用方法
        
        Args:
            question_data: 要填充的问题数据字典
            code_list: 代码列表
            element_map: 元素映射
            element_code: 元素编号
            element_key: 问题数据中的键名
            
        Returns:
            添加是否成功
        """
        if element_code in code_list and element_code in element_map:
            element = element_map[element_code]
            element_name = element.get('name', '')

            # 从元素的conditionList中随机选择一个条件
            conditions = element.get('conditionList', [])
            if conditions:
                condition = random.choice(conditions)

                # 处理不同类型的condition
                if isinstance(condition, dict):
                    condition_text = condition.get('text', '')
                elif isinstance(condition, str):
                    condition_text = condition
                else:
                    condition_text = str(condition)

                question_data[element_key] = condition_text
                # print(f"添加问题数据: {element_key} = {condition_text}")
                return True
            else:
                # print(f"元素 {element_code} 没有可用的条件列表")
                return False
        return False

    def generate_question(self, rule: Dict, base_elements: Dict, num_variations: int = 1,
                          combo_index: int = -1) -> Dict:
        """
        生成完整的问题数据
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            num_variations: 变种数量，默认为1（此参数在基类中不处理变种，而是在子类VariationGenerationService中处理）
            combo_index: 指定使用codeList中的哪个组合，-1表示随机选择
            
        Returns:
            完整的问题数据
        """
        # 生成基础问题数据
        question_data, elements_with_dict = self.generate_base_question(rule, base_elements, combo_index)

        # 处理特殊元素
        question_data = self.process_special_elements(question_data, elements_with_dict)

        return question_data

    def generate_answer(self, question_data: Dict, answer_elements: Dict, base_elements: Dict) -> Dict:
        """
        生成答案数据
        
        Args:
            question_data: 问题数据
            answer_elements: 回答元素数据
            base_elements: 基础元素数据
            
        Returns:
            答案数据
        """
        # 获取回答元素列表
        answer_elements_list = answer_elements.get('answerElements', [])

        # 获取基础元素名称到数据的映射
        base_data_map = {item.get('name', ''): item for item in base_elements.get('baseDataList', [])}

        # 存储生成的答案
        answer_data = {}

        # 处理每个回答元素
        for element in answer_elements_list:
            element_id = element.get('id', '')
            element_name = element.get('name', '')

            # 获取输出模板
            template = element.get('template', '')

            # 根据输入元素填充模板
            for key, value in question_data.items():
                # 替换模板中的标记
                if f'${key}$' in template:
                    template = template.replace(f'${key}$', str(value))

            # 简单处理：如果模板中仍有$x$形式的标记，用空字符串替换
            import re
            template = re.sub(r'\$[^$]+\$', '', template)

            # 保存处理后的答案元素
            answer_data[element_name] = template

        return answer_data

    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict,
                            num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据
        基础实现，考虑规则中的codeList组合，为每个组合生成至少一个数据
        子类可以重写此方法以提供更高级的变种生成功能
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            answer_elements: 回答元素数据
            num_variations: 每个组合的变种数量，默认2
            
        Returns:
            变种数据列表
        """
        variations = []

        # 获取codeList
        code_list_value = rule.get('codeList', [])

        if isinstance(code_list_value, list) and code_list_value:
            # 为每个组合生成数据
            for combo_index in range(len(code_list_value)):
                # 为当前组合生成指定数量的变种
                combo_variations = self._generate_combo_variations(
                    rule, base_elements, answer_elements, num_variations, combo_index)
                variations.extend(combo_variations)
        else:
            # 如果没有多个组合，执行标准变种生成逻辑
            # 简单实现：生成指定数量的变种
            for _ in range(num_variations):
                # 生成问题数据
                question_data = self.generate_question(rule, base_elements)

                # 生成答案数据
                answer_data = self.generate_answer(question_data, answer_elements, base_elements)

                # 添加到变种列表
                variations.append({
                    'question': question_data,
                    'answer': answer_data,
                    'rule_id': rule.get('id', ''),
                    'rule_name': rule.get('name', '')
                })

        return variations

    def _generate_combo_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict,
                                   num_variations: int, combo_index: int) -> List[Dict]:
        """
        为特定组合生成变种数据
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            answer_elements: 回答元素数据
            num_variations: 变种数量
            combo_index: 组合索引
            
        Returns:
            变种数据列表
        """
        combo_variations = []

        # 为指定组合生成指定数量的变种
        for _ in range(num_variations):
            # 生成问题数据，传递combo_index
            question_data = self.generate_question(rule, base_elements, 1, combo_index)

            # 生成答案数据
            answer_data = self.generate_answer(question_data, answer_elements, base_elements)

            # 添加到变种列表
            combo_variations.append({
                'question': question_data,
                'answer': answer_data,
                'rule_id': rule.get('id', ''),
                'rule_name': rule.get('name', ''),
                'combo_index': combo_index  # 记录使用的组合索引，便于调试
            })

        return combo_variations

    def generate_business_data(self, business_object: str, total_samples: int = 200,
                               variations_per_rule: int = 2, variation_service=None,
                               ruleids: str = None) -> List[Dict]:
        """
        生成业务数据，并对数据进行处理。
        
        Args:
            business_object: 业务对象名称
            total_samples: 总样本数，默认为200
            variations_per_rule: 每条规则的变种数，默认为2
            variation_service: 变种生成服务，如果为None，则会创建一个默认的变种生成服务
            ruleids: 规则ID过滤字符串，格式如"1,2,3"或"-1,-2,-3"，正数表示包含，负数表示排除
            
        Returns:
            处理后的业务数据列表
        """
        # 获取答案元素
        from src.service.rule_logic import get_rule_components
        _, _, answer_elements = get_rule_components(business_object)

        # 使用传入的variation_service或创建一个新的
        _variation_service = variation_service
        if _variation_service is None:
            from src.service.common.generation_service_factory import GenerationServiceFactory
            _variation_service = GenerationServiceFactory.create_variation_service()

        # 生成数据
        data = _variation_service.generate_data(
            business_object,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=ruleids
        )

        # 确保生成了足够的数据
        if not data:
            print(f"警告：{business_object}没有生成任何数据")
            return []

        # 后处理
        processed_data = self.post_process_data(data, answer_elements)

        return processed_data

    def post_process_data(self, data: List[Dict], answer_elements) -> List[Dict]:
        """
        对生成的数据进行后处理，子类应重写此方法来处理特定业务逻辑
        
        Args:
            data: 生成的数据列表
            answer_elements: 回答元素定义
            
        Returns:
            处理后的数据列表
        """
        # 基类中提供默认实现，不做任何处理
        return data

    @classmethod
    def create_specific_generator(cls, business_object: str, answer_elements: Dict) -> Any:
        """
        创建特定业务对象的生成器
        
        Args:
            business_object: 业务对象名称
            answer_elements: 答案元素定义
            
        Returns:
            生成器实例
        """
        from src.service.common.generation_service_factory import GenerationServiceFactory
        return GenerationServiceFactory.create_variation_service()
