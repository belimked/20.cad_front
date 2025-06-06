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
            
            rule_shares.append({
                'rule': rule,
                'share': max(1, share)  # 确保至少有1个样本
            })
        
        return rule_shares
    
    def generate_base_question(self, rule: Dict, base_elements: Dict) -> Tuple[Dict, Dict]:
        """
        生成基础问题数据（两个服务类共享的部分）
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            
        Returns:
            问题数据和需要处理的字典元素
        """
        # 获取规则中的codeList并处理
        code_list = []
        
        # 处理各种可能的codeList格式
        code_list_value = rule.get('codeList', [])
        print(f"原始codeList值: {code_list_value}, 类型: {type(code_list_value)}")
        
        if isinstance(code_list_value, list):
            # 遍历列表中的每个元素
            for item in code_list_value:
                if isinstance(item, str):
                    # 如果元素是字符串且包含分隔符，则分割
                    if ';' in item:
                        code_list.extend(item.split(';'))
                    else:
                        code_list.append(item)
                else:
                    # 非字符串元素，转为字符串后添加
                    code_list.append(str(item))
        elif isinstance(code_list_value, str):
            # 如果整个codeList是一个字符串，按分隔符分割
            if code_list_value:
                code_list = code_list_value.split(';')
        
        print(f"处理后的code_list: {code_list}")
        
        # 获取基础元素列表
        base_data_list = base_elements.get('baseDataList', [])
        
        # 映射元素号到元素定义
        element_map = {item.get('number', ''): item for item in base_data_list}
        
        # 生成问题数据
        question_data = {}
        # 存储需要处理字典替换的元素
        elements_with_dict = {}
        
        # 生成基本问题数据，标记需要处理字典的元素
        for code in code_list:
            if code and code in element_map:
                element = element_map[code]
                element_name = element.get('name', '')
                print(f"处理元素: {code}, 名称: {element_name}")
                
                # 检查元素是否有字典列表或条件列表
                dict_list = element.get('dictlist', [])
                conditions = element.get('conditionList', [])
                
                # 修改：同时考虑dictlist和conditionList，只要有一个不为空，就添加到elements_with_dict
                if dict_list or conditions:
                    elements_with_dict[element_name] = {
                        'code': code,
                        'element': element,
                        'dict_list': dict_list
                    }
                
                # 从元素的conditionList中随机选择一个条件
                if conditions:
                    condition = random.choice(conditions)
                    print(f"选择的condition: {condition}, 类型: {type(condition)}")
                    
                    # 处理不同类型的condition
                    if isinstance(condition, dict):
                        condition_text = condition.get('text', '')
                    elif isinstance(condition, str):
                        condition_text = condition
                    else:
                        condition_text = str(condition)
                    
                    question_data[element_name] = condition_text
                    print(f"添加问题数据: {element_name} = {condition_text}")
        
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
                    processed_value = self.process_dict_replacement(element_name, current_value, dict_mapping, dict_item)
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
            
        # 特殊处理：cargoNumberWithQuantity 和 deliveryNumberWithQuantity 替换XX为packageNumber
        if element_name in ['cargoNumberWithQuantity', 'deliveryNumberWithQuantity']:
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
                random_entry = None
                
                # 检查dict_item的结构并提取相应的值
                if isinstance(dict_item, dict):
                    if 'data' in dict_item:
                        # 字典项包含data属性
                        dict_data = dict_item.get('data', [])
                        if dict_data and isinstance(dict_data, list):
                            random_entry = random.choice(dict_data)
                    else:
                        # 字典项本身就是要使用的值
                        # 查找一个合适的属性作为替换值
                        for key in ['name', 'projectname', 'value', 'id', 'code']:
                            if key in dict_item:
                                random_entry = dict_item[key]
                                break
                        # 如果没有找到合适的属性，使用字典项的第一个值
                        if random_entry is None and len(dict_item) > 0:
                            random_entry = list(dict_item.values())[0]
                elif isinstance(dict_item, list) and len(dict_item) > 0:
                    # 如果dict_item是列表，随机选择一个值
                    random_entry = random.choice(dict_item)
                
                # 执行替换
                if random_entry is not None:
                    replaced_value = current_value.replace(placeholder, str(random_entry))
                    return replaced_value
        
        # 如果包含占位符但替换失败，或者没有占位符，尝试直接使用字典值
        if (placeholder_found and random_entry is None) or not placeholder_found:
            # 如果字典项是字典，尝试获取值
            if isinstance(dict_item, dict):
                # 优先使用特定字段，针对不同元素类型
                if element_name == 'projectName':
                    if 'projectname' in dict_item:
                        return dict_item['projectname']
                elif element_name == 'personName':
                    if 'name' in dict_item:
                        return dict_item['name']
                # 添加对staffNumber的支持
                elif element_name == 'staffId':
                    if 'staffNumber' in dict_item:
                        return dict_item['staffNumber']
                # 添加对businessNumber的支持 - 注意这里使用的是number字段
                elif element_name == 'businessNumber':
                    if 'number' in dict_item:
                        return dict_item['number']
                # 添加对drawName的支持
                elif element_name == 'drawName':
                    if 'drawname' in dict_item:
                        return dict_item['drawname']
                # 添加对materialCode的支持
                elif element_name == 'materialCode':
                    if 'materialcode' in dict_item:
                        return dict_item['materialcode']
                # 添加对vendorName的支持
                elif element_name == 'supplierInfo':
                    if 'vendorname' in dict_item:
                        return dict_item['vendorname']
                
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
                    for key in ['name', 'projectname', 'value', 'text', 'id', 'code', 'staffNumber', 'businessNumber', 
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
    
    def add_element_to_question(self, question_data: Dict, code_list: List, element_map: Dict, element_code: str, element_key: str):
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
                print(f"添加问题数据: {element_key} = {condition_text}")
                return True
            else:
                print(f"元素 {element_code} 没有可用的条件列表")
                return False
        return False
    
    def generate_question(self, rule: Dict, base_elements: Dict, num_variations: int = 1) -> Dict:
        """
        生成完整的问题数据
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            num_variations: 变种数量，默认为1（此参数在基类中不处理变种，而是在子类VariationGenerationService中处理）
            
        Returns:
            完整的问题数据
        """
        # 生成基础问题数据
        question_data, elements_with_dict = self.generate_base_question(rule, base_elements)
        
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
        基础实现，每次都重新生成问题数据
        子类可以重写此方法以提供更高级的变种生成功能
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            answer_elements: 回答元素数据
            num_variations: 变种数量，默认2
            
        Returns:
            变种数据列表
        """
        variations = []
        
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
    
    def generate_business_data(self, business_object: str, 
                              total_samples: int = 200, 
                              variations_per_rule: int = 2,
                              variation_service = None) -> List[Dict]:
        """
        生成业务数据的通用方法
        
        Args:
            business_object: 业务对象名称
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            variation_service: 可选的变种生成服务实例，如果提供则使用该服务生成数据
            
        Returns:
            生成的数据列表
        """
        # 获取回答元素定义
        from src.service.rule_logic import get_rule_components
        _, _, answer_elements = get_rule_components(business_object)
        
        # 生成基础数据
        if variation_service:
            # 使用变种服务生成数据
            data = variation_service.generate_data(business_object, total_samples, variations_per_rule)
        else:
            # 如果没有提供变种服务，尝试创建一个
            from src.service.common.generation_service_factory import GenerationServiceFactory
            variation_service = GenerationServiceFactory.create_variation_service()
            data = variation_service.generate_data(business_object, total_samples, variations_per_rule)
        
        # 确保至少有一定数量的数据
        if len(data) < 8:
            # 如果数据不足8条，复制现有数据以达到8条
            current_count = len(data)
            needed = max(8 - current_count, 0)
            
            for i in range(needed):
                # 复制已有数据（如果有的话）
                if current_count > 0:
                    copy_idx = i % current_count
                    data.append(data[copy_idx].copy())  # 深拷贝
        
        # 对每条数据应用正确的字段填充
        for item in data:
            # 处理静态值字段
            for element in answer_elements.get('answerElements', []):
                element_name = element.get('name')
                # 静态值字段直接设置对应的值
                if element.get('isStatic') == "是":
                    static_value = element.get('staticValue', "")
                    # 避免将"无"字符串写入
                    if static_value != "无":
                        item['answer'][element_name] = static_value
                    else:
                        item['answer'][element_name] = ""
        
        # 子类应重写post_process_data方法来处理特定业务逻辑
        # 直接传递 answer_elements 作为第二个参数，而不是 business_object
        return self.post_process_data(data, answer_elements)
    
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
    def create_specific_generator(cls, service_class: Type['BaseGenerationService'], 
                                method_name: str, default_business_object: str = None) -> Callable:
        """
        创建特定生成器方法
        
        Args:
            service_class: 服务类
            method_name: 方法名
            default_business_object: 默认业务对象
            
        Returns:
            生成器方法
        """
        def generator_method(business_object: str = default_business_object, 
                           total_samples: int = 10, 
                           variations_per_rule: int = 2) -> List[Dict]:
            """
            自动生成的特定生成器方法
            
            Args:
                business_object: 业务对象名称
                total_samples: 总样本数
                variations_per_rule: 每个规则的变种数
                
            Returns:
                生成的数据列表
            """
            # 获取服务实例
            service = cls.get_service(service_class)
            
            # 调用生成方法
            return getattr(service, method_name)(business_object, total_samples, variations_per_rule)
        
        return generator_method 
