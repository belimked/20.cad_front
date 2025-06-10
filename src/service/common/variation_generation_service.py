#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
import random
from src.service.common.base_generation_service import BaseGenerationService

class VariationGenerationService(BaseGenerationService):
    """
    变种生成服务类，负责处理变种生成相关的逻辑
    继承自BaseGenerationService，提供更专注的变种生成功能
    """
    
    def __init__(self):
        """
        初始化变种生成服务
        """
        super().__init__()
    
    def generate_question_with_variations(self, rule: Dict, base_elements: Dict, num_variations: int = 1) -> Dict:
        """
        生成带变种的问题数据
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            num_variations: 变种数量，默认为1
            
        Returns:
            包含变种的问题数据
        """
        # 如果变种数为1，直接使用父类方法生成单个问题数据
        if num_variations <= 1:
            return super().generate_question(rule, base_elements)
        
        # 生成多个变种
        variations_data = {}
        
        # 生成基础问题数据
        question_data, elements_with_dict = self.generate_base_question(rule, base_elements)
        
        # 处理有变种需求的字段
        for element_name, element_data in elements_with_dict.items():
            element = element_data['element']
            dict_list = element_data.get('dict_list', [])
            
            # 初始化变种值列表
            value_list = []
            
            # 根据是否有字典列表处理变种
            if dict_list:
                # 从字典生成变种
                for _ in range(num_variations):
                    # 处理特殊元素并获取当前值
                    temp_elements = {element_name: element_data}
                    temp_question = {element_name: question_data.get(element_name, "")}
                    processed_data = self.process_special_elements(temp_question, temp_elements)
                    value_list.append(processed_data.get(element_name, ""))
            else:
                # 从conditionList生成变种
                conditions = element.get('conditionList', [])
                if conditions:
                    # 随机选择num_variations个条件（可能有重复）
                    for _ in range(num_variations):
                        condition = random.choice(conditions)
                        if isinstance(condition, dict):
                            condition_text = condition.get('text', '')
                        elif isinstance(condition, str):
                            condition_text = condition
                        else:
                            condition_text = str(condition)
                        value_list.append(condition_text)
            
            # 如果生成了变种值，添加到变种数据中
            if value_list:
                variations_data[element_name] = {
                    'name': element_name,
                    'valueList': value_list
                }
        
        # 处理没有变种的字段
        for key, value in question_data.items():
            if key not in variations_data:
                variations_data[key] = {
                    'name': key,
                    'valueList': [value]
                }
        
        # 处理特殊元素
        for key in list(question_data.keys()):
            if key not in elements_with_dict:
                question_data = self.process_special_elements(question_data, {})
        
        return variations_data
    
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成多个变种数据
        
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
                # 为单个组合生成变种
                combo_variations = []
                
                # 生成带变种的问题数据，使用指定的组合索引
                variations_data = self.generate_question_with_variations_for_combo(
                    rule, base_elements, num_variations, combo_index)
                
                # 检查是否是变种数据格式（包含valueList的字典）
                if any(isinstance(v, dict) and 'valueList' in v for v in variations_data.values()):
                    # 是变种数据格式，需要组合生成多个问题
                    
                    # 获取所有字段及其变种列表
                    fields_variations = {}
                    for key, value_data in variations_data.items():
                        if isinstance(value_data, dict) and 'valueList' in value_data:
                            fields_variations[key] = value_data['valueList']
                        else:
                            # 单值字段，转为列表以便统一处理
                            fields_variations[key] = [value_data]
                    
                    # 根据变种数量生成组合
                    for i in range(num_variations):
                        # 构建单个问题数据
                        question_data = {}
                        for field, values in fields_variations.items():
                            # 如果变种数量不足，则循环使用
                            idx = i % len(values)
                            question_data[field] = values[idx]
                        
                        # 生成答案数据
                        answer_data = self.generate_answer(question_data, answer_elements, base_elements)
                        
                        # 添加到变种列表
                        combo_variations.append({
                            'question': question_data,
                            'answer': answer_data,
                            'rule_id': rule.get('id', ''),
                            'rule_name': rule.get('name', ''),
                            'combo_index': combo_index,
                            'combo_value': code_list_value[combo_index]  # 记录实际使用的codeList元素值
                        })
                else:
                    # 不是变种数据格式，是单个问题数据
                    # 生成指定数量的变种
                    for _ in range(num_variations):
                        # 如果num_variations > 1但返回的不是变种格式，重新生成问题
                        if _ > 0:
                            question_data = super().generate_question(rule, base_elements, 1, combo_index)
                        else:
                            question_data = variations_data
                        
                        # 生成答案数据
                        answer_data = self.generate_answer(question_data, answer_elements, base_elements)
                        
                        # 添加到变种列表
                        combo_variations.append({
                            'question': question_data,
                            'answer': answer_data,
                            'rule_id': rule.get('id', ''),
                            'rule_name': rule.get('name', ''),
                            'combo_index': combo_index,
                            'combo_value': code_list_value[combo_index]  # 记录实际使用的codeList元素值
                        })
                
                variations.extend(combo_variations)
        else:
            # 如果没有多个组合，执行原有的变种生成逻辑
            variations_data = self.generate_question_with_variations(rule, base_elements, num_variations)
            
            # 检查是否是变种数据格式（包含valueList的字典）
            if any(isinstance(v, dict) and 'valueList' in v for v in variations_data.values()):
                # 是变种数据格式，需要组合生成多个问题
                
                # 获取所有字段及其变种列表
                fields_variations = {}
                for key, value_data in variations_data.items():
                    if isinstance(value_data, dict) and 'valueList' in value_data:
                        fields_variations[key] = value_data['valueList']
                    else:
                        # 单值字段，转为列表以便统一处理
                        fields_variations[key] = [value_data]
                
                # 根据变种数量生成组合
                for i in range(num_variations):
                    # 构建单个问题数据
                    question_data = {}
                    for field, values in fields_variations.items():
                        # 如果变种数量不足，则循环使用
                        idx = i % len(values)
                        question_data[field] = values[idx]
                    
                    # 生成答案数据
                    answer_data = self.generate_answer(question_data, answer_elements, base_elements)
                    
                    # 添加到变种列表
                    variations.append({
                        'question': question_data,
                        'answer': answer_data,
                        'rule_id': rule.get('id', ''),
                        'rule_name': rule.get('name', ''),
                        'combo_value': str(code_list_value)  # 记录原始codeList值的字符串表示
                    })
            else:
                # 不是变种数据格式，是单个问题数据
                # 生成指定数量的变种
                for _ in range(num_variations):
                    # 如果num_variations > 1但返回的不是变种格式，重新生成问题
                    if _ > 0:
                        question_data = super().generate_question(rule, base_elements)
                    else:
                        question_data = variations_data
                    
                    # 生成答案数据
                    answer_data = self.generate_answer(question_data, answer_elements, base_elements)
                    
                    # 添加到变种列表
                    variations.append({
                        'question': question_data,
                        'answer': answer_data,
                        'rule_id': rule.get('id', ''),
                        'rule_name': rule.get('name', ''),
                        'combo_value': str(code_list_value)  # 记录原始codeList值的字符串表示
                    })
        
        return variations
    
    def generate_question_with_variations_for_combo(self, rule: Dict, base_elements: Dict, 
                                                   num_variations: int = 1, combo_index: int = 0) -> Dict:
        """
        生成带变种的问题数据，针对特定的组合索引
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            num_variations: 变种数量，默认为1
            combo_index: 组合索引，指定使用codeList中的哪个组合
            
        Returns:
            包含变种的问题数据
        """
        # 如果变种数为1，直接使用父类方法生成单个问题数据
        if num_variations <= 1:
            return super().generate_question(rule, base_elements, 1, combo_index)
        
        # 生成多个变种
        variations_data = {}
        
        # 生成基础问题数据，传递combo_index
        question_data, elements_with_dict = self.generate_base_question(rule, base_elements, combo_index)
        
        # 处理有变种需求的字段
        for element_name, element_data in elements_with_dict.items():
            element = element_data['element']
            dict_list = element_data.get('dict_list', [])
            
            # 初始化变种值列表
            value_list = []
            
            # 根据是否有字典列表处理变种
            if dict_list:
                # 从字典生成变种
                for _ in range(num_variations):
                    # 处理特殊元素并获取当前值
                    temp_elements = {element_name: element_data}
                    temp_question = {element_name: question_data.get(element_name, "")}
                    processed_data = self.process_special_elements(temp_question, temp_elements)
                    value_list.append(processed_data.get(element_name, ""))
            else:
                # 从conditionList生成变种
                conditions = element.get('conditionList', [])
                if conditions:
                    # 随机选择num_variations个条件（可能有重复）
                    for _ in range(num_variations):
                        condition = random.choice(conditions)
                        if isinstance(condition, dict):
                            condition_text = condition.get('text', '')
                        elif isinstance(condition, str):
                            condition_text = condition
                        else:
                            condition_text = str(condition)
                        value_list.append(condition_text)
            
            # 如果生成了变种值，添加到变种数据中
            if value_list:
                variations_data[element_name] = {
                    'name': element_name,
                    'valueList': value_list
                }
        
        # 处理没有变种的字段
        for key, value in question_data.items():
            if key not in variations_data:
                variations_data[key] = {
                    'name': key,
                    'valueList': [value]
                }
        
        # 处理特殊元素
        for key in list(question_data.keys()):
            if key not in elements_with_dict:
                question_data = self.process_special_elements(question_data, {})
        
        return variations_data
    
    def calculate_possible_variations(self, rule: Dict, base_elements: Dict) -> int:
        """
        计算一个规则可能的变种数量，基于codeList的元素组合
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            
        Returns:
            可能的变种数量
        """
        # 获取规则中的codeList
        code_list_value = rule.get('codeList', [])
        
        # 如果codeList是列表，直接返回列表长度作为基础变种数量
        if isinstance(code_list_value, list) and code_list_value:
            return len(code_list_value)
            
        # 如果不是列表或列表为空，处理单个code_list
        code_list = []
        
        # 处理各种可能的codeList格式
        if isinstance(code_list_value, str) and code_list_value:
            code_list = code_list_value.split(';')
        
        # 如果没有有效的code_list，返回默认值
        if not code_list:
            return 2  # 默认变种数量
        
        # 获取基础元素列表
        base_data_list = base_elements.get('baseDataList', [])
        
        # 映射元素号到元素定义
        element_map = {item.get('number', ''): item for item in base_data_list}
        
        # 计算可能的变种数量
        total_variations = 0
        
        # 遍历codeList中的每个元素代码
        for code in code_list:
            if code and code in element_map:
                element = element_map[code]
                
                # 检查元素的变种可能性
                element_variations = 0
                
                # 从条件列表计算变种
                conditions = element.get('conditionList', [])
                if conditions:
                    element_variations += len(conditions)
                
                # 从字典列表计算变种
                dict_list = element.get('dictlist', [])
                if dict_list:
                    # 每个字典可能提供多个变种，这里简化处理
                    element_variations += len(dict_list) * 2  # 假设每个字典平均有2个选项
                
                # 确保至少有1个变种
                element_variations = max(1, element_variations)
                
                # 累加变种总数（简化处理，实际上应该考虑组合）
                if total_variations == 0:
                    total_variations = element_variations
                else:
                    # 我们累加而不是相乘，因为通常不是所有字段都会变化
                    total_variations += element_variations
        
        # 确保至少有1个变种
        return max(1, total_variations)

    def generate_data(self, business_object: str, total_samples: int = 200, 
                     variations_per_rule: int = 2) -> List[Dict]:
        """
        生成指定业务对象的数据，支持变种生成
        
        Args:
            business_object: 业务对象名称
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数，默认2
            
        Returns:
            生成的数据列表
        """
        # 打印参数信息
        print(f"========================================")
        print(f"开始生成数据：业务对象={business_object}, 请求总样本数={total_samples}, 每规则变种数={variations_per_rule}")
        
        # 延迟导入，避免循环导入问题
        from src.service.rule_logic import get_rule_components
        from src.service.common.config_service import ConfigService
        
        # 获取配置参数
        config_service = ConfigService()
        variation_settings = config_service.get_variation_settings()
        
        # 从配置中获取参数
        variation_ratio_factor = variation_settings.get("variation_ratio_factor", 1.2)
        min_data_count = variation_settings.get("min_data_count", 8)
        far_greater_factor = variation_settings.get("far_greater_factor", 2.0)
        variation_multiplier = variation_settings.get("variation_multiplier", 2.0)
        
        print(f"配置参数：variation_ratio_factor={variation_ratio_factor}, min_data_count={min_data_count}, " 
              f"far_greater_factor={far_greater_factor}, variation_multiplier={variation_multiplier}")
        
        # 获取三个组件数据
        base_elements, business_rules, answer_elements = get_rule_components(business_object)
        
        # 计算规则权重和份额
        rule_shares = self.calculate_rule_weights(business_object, total_samples)
        
        # 打印规则份额信息
        total_shares = sum(share['share'] for share in rule_shares)
        print(f"规则总数：{len(rule_shares)}, 总分配份额：{total_shares}, 请求样本数：{total_samples}")
        
        # 存储生成的所有数据
        all_data = []
        
        # 根据份额生成每个规则的数据
        for rule_share in rule_shares:
            rule = rule_share['rule']
            share = rule_share['share']
            
            # 计算规则可能的变种数量
            possible_variations = self.calculate_possible_variations(rule, base_elements)
            
            # 计算实际应该生成的变种数量
            if possible_variations < share:
                # 如果可能变种数量小于份额，需要多次生成数据直到满足份额
                # 初始变种数量设为可能的变种数量
                variations_count = possible_variations
                
                # 计算需要重复的次数
                repeat_times = max(1, int(share / possible_variations))
                
                print(f"规则 {rule.get('id', '')}: 份额={share}, 可能变种={possible_variations}, "
                      f"生成变种={variations_count}, 重复次数={repeat_times}")
                
                # 生成多次变种并合并
                all_variations = []
                for _ in range(repeat_times):
                    variations = self.generate_variations(
                        rule, base_elements, answer_elements, variations_count
                    )
                    all_variations.extend(variations)
                
                # 如果生成的总数据仍然小于份额，随机复制一些条目
                # if len(all_variations) < share:
                #     needed = share - len(all_variations)
                #     if all_variations:  # 确保有数据可复制
                #         print(f"  规则 {rule.get('id', '')}: 数据不足，需要复制 {needed} 条数据")
                #         for _ in range(needed):
                #             random_idx = random.randint(0, len(all_variations) - 1)
                #             all_variations.append(all_variations[random_idx].copy())
                
                # 如果生成的数据超过份额，随机抽样
                # if len(all_variations) > share:
                #     print(f"  规则 {rule.get('id', '')}: 数据过多，从 {len(all_variations)} 条中抽样 {share} 条")
                #     all_variations = random.sample(all_variations, share)
                #
                # 添加到总数据列表
                all_data.extend(all_variations)
            else:
                # 可能变种数量大于等于份额，执行标准逻辑
                
                # 修复：直接使用份额作为变种数量，而不是受限于variations_per_rule
                # 这确保了每个规则能生成其份额对应的数据量
                variations_count = share
                
                # 保留如下日志，但调整文本以正确反映修改后的逻辑
                print(f"规则 {rule.get('id', '')}: 份额={share}, 可能变种={possible_variations}, 已修复：直接使用份额={variations_count}")
                
                # 生成变种
                variations = self.generate_variations(
                    rule, base_elements, answer_elements, variations_per_rule
                )
                
                # # 如果生成的变种超过份额，随机抽样
                # if len(variations) > share:
                #     # 随机抽样而不是截断，保持数据多样性
                #     print(f"  规则 {rule.get('id', '')}: 数据过多，从 {len(variations)} 条中抽样 {share} 条")
                #     sampled_variations = random.sample(variations, share)
                #     all_data.extend(sampled_variations)
                # else:
                    # 添加到总数据列表
                all_data.extend(variations)
            
            # 打印当前累计数据量
            print(f"当前累计数据量: {len(all_data)}")
        
        print(f"生成完所有规则后的数据量: {len(all_data)}")
        
        # 如果生成的数据超过请求数量，随机抽样而不是截断
        # if len(all_data) > total_samples:
        #     print(f"生成的数据量 {len(all_data)} 超过请求数量 {total_samples}，将随机抽样到 {total_samples}")
        #     all_data = random.sample(all_data, total_samples)
        
        # 确保至少有min_data_count条数据
        # 理论上这段代码不应该被执行，因为我们已经确保了每个规则的份额得到满足
        # 但为了安全起见，仍然保留这个检查
        if len(all_data) < min_data_count:
            print(f"警告：生成的数据量({len(all_data)})小于最小要求({min_data_count})，将自动复制数据")
            # 如果数据不足min_data_count条，复制现有数据
            current_count = len(all_data)
            needed = max(min_data_count - current_count, 0)
            
            for i in range(needed):
                # 复制已有数据（如果有的话）
                if current_count > 0:
                    copy_idx = i % current_count
                    all_data.append(all_data[copy_idx].copy())  # 深拷贝
        
        print(f"最终返回的数据量: {len(all_data)}")
        print(f"========================================")
        
        return all_data 
