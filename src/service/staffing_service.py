#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
import random
import math
from src.service.rule_logic import get_rule_components, get_sorted_rules

class StaffingService:
    """
    人员安排服务类，用于根据规则生成人员安排的问题和答案
    """
    
    def __init__(self):
        """
        初始化人员安排服务
        """
        pass
    
    def calculate_rule_weights(self, business_object: str, total_samples: int = 200) -> List[Dict]:
        """
        计算规则权重并分配生成份额
        
        Args:
            business_object: 业务对象名称，如 searchStaff
            total_samples: 总样本数，默认200
            
        Returns:
            包含规则和对应份额的列表
        """
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
    
    def generate_question(self, rule: Dict, base_elements: Dict) -> Dict:
        """
        根据规则和基础元素生成问题
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            
        Returns:
            生成的问题数据
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
        for code in code_list:
            if code and code in element_map:
                element = element_map[code]
                element_name = element.get('name', '')
                print(f"处理元素: {code}, 名称: {element_name}")
                
                # 从元素的conditionList中随机选择一个条件
                conditions = element.get('conditionList', [])
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
        
        return question_data
    
    def generate_answer(self, question_data: Dict, answer_elements: Dict, base_elements: Dict) -> Dict:
        """
        根据问题数据和回答元素生成答案
        
        Args:
            question_data: 问题数据
            answer_elements: 回答元素数据
            base_elements: 基础元素数据（用于关联映射）
            
        Returns:
            生成的答案数据
        """
        # 获取回答元素列表
        answer_element_list = answer_elements.get('answerElements', [])
        
        # 获取基础元素列表
        base_data_list = base_elements.get('baseDataList', [])
        
        # 创建基础元素number到name的映射
        base_number_to_name = {item.get('number', ''): item.get('name', '') for item in base_data_list}
        print(f"基础元素映射: {base_number_to_name}")
        
        # 生成答案数据
        answer_data = {}
        for element in answer_element_list:
            element_name = element.get('nameCN', '')
            is_static = element.get('isStatic', '') == '是'
            relate_to_base = element.get('relateToBase', '')
            
            print(f"处理回答元素: {element_name}, 是否静态: {is_static}, 关联基础元素: {relate_to_base}")
            
            # 如果是静态元素，使用staticValue属性值
            if is_static:
                static_value = element.get('staticValue', '无')
                answer_data[element_name] = static_value
            else:
                # 找到关联的基础元素名称
                base_name = base_number_to_name.get(relate_to_base, '')
                
                # 如果找到对应的基础元素名称，并且该名称在问题数据中
                if base_name and base_name in question_data:
                    answer_data[element_name] = question_data[base_name]
                    print(f"设置答案: {element_name} = {question_data[base_name]}")
                else:
                    # 如果没有找到匹配的基础元素，设置为空值
                    answer_data[element_name] = ""
                    print(f"未找到匹配基础元素或问题数据，设置为空值: {element_name}")
        
        return answer_data
    
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """
        为一个规则生成指定数量的变种
        
        Args:
            rule: 规则对象
            base_elements: 基础元素数据
            answer_elements: 回答元素数据
            num_variations: 变种数量，默认2
            
        Returns:
            变种列表
        """
        variations = []
        for i in range(num_variations):
            print(f"\n生成第{i+1}个变种:")
            # 生成问题
            question_data = self.generate_question(rule, base_elements)
            
            # 生成答案
            answer_data = self.generate_answer(question_data, answer_elements, base_elements)
            
            # 组装结果
            variation = {
                "question": question_data,
                "answer": answer_data
            }
            
            variations.append(variation)
        
        return variations
    
    def generate_staffing_data(self, business_object: str, total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """
        生成人员安排数据
        
        Args:
            business_object: 业务对象名称，如 searchStaff
            total_samples: 总样本数，默认200
            variations_per_rule: 每个规则的变种数量，默认2
            
        Returns:
            生成的数据列表
        """
        print(f"\n开始生成{business_object}的人员安排数据")
        # 获取三个数据集合
        base_elements, business_rules, answer_elements = get_rule_components(business_object)
        
        # 打印规则数据结构信息
        print(f"\n业务规则类型: {type(business_rules)}")
        rules = business_rules.get('rulesMap', [])
        print(f"规则列表类型: {type(rules)}, 长度: {len(rules)}")
        if rules:
            first_rule = rules[0]
            print(f"第一条规则示例: {first_rule}")
        
        # 打印基础元素信息
        base_data_list = base_elements.get('baseDataList', [])
        print(f"基础元素数量: {len(base_data_list)}")
        if base_data_list:
            print(f"第一个基础元素示例: {base_data_list[0]}")
        
        # 打印回答元素信息
        answer_element_list = answer_elements.get('answerElements', [])
        print(f"回答元素数量: {len(answer_element_list)}")
        if answer_element_list:
            print(f"第一个回答元素示例: {answer_element_list[0]}")
        
        # 计算规则权重
        rule_shares = self.calculate_rule_weights(business_object, total_samples)
        print(f"\n规则份额分配:")
        for rule_share in rule_shares:
            rule = rule_share['rule']
            share = rule_share['share']
            print(f"规则ID: {rule.get('id', '')}, 名称: {rule.get('name', '')}, 权重: {rule.get('codecount', 0)}, 分配份额: {share}")
        
        # 生成数据
        result_data = []
        for rule_share in rule_shares:
            rule = rule_share['rule']
            share = rule_share['share']
            
            print(f"\n为规则ID: {rule.get('id', '')}, 名称: {rule.get('name', '')}生成数据")
            
            # 计算需要生成的变种集合数量
            num_sets = math.ceil(share / variations_per_rule)
            print(f"需要生成{num_sets}组变种，每组{variations_per_rule}个，总计目标{share}个")
            
            generated_for_rule = 0  # 跟踪为当前规则生成的样本数量
            
            # 生成所需数量的变种集合
            for set_index in range(num_sets):
                print(f"\n生成第{set_index+1}组变种:")
                # 生成一组变种
                variations = self.generate_variations(
                    rule, base_elements, answer_elements, variations_per_rule
                )
                
                # 添加到结果中，但不超过分配的份额
                for variation in variations:
                    if generated_for_rule < share:
                        result_data.append(variation)
                        generated_for_rule += 1
                    else:
                        break
                
                # 如果已经达到或超过分配的份额，跳出循环
                if generated_for_rule >= share:
                    break
            
            print(f"为规则ID: {rule.get('id', '')}生成了{generated_for_rule}个数据")
        
        print(f"\n总共生成了{len(result_data)}个数据")
        return result_data

# 单例模式
_instance = None

def get_staffing_service() -> StaffingService:
    """
    获取人员安排服务的单例实例
    
    Returns:
        StaffingService实例
    """
    global _instance
    if _instance is None:
        _instance = StaffingService()
    return _instance

# 便捷方法
def generate_staffing_data(business_object: str, total_samples: int = 10, 
                         variations_per_rule: int = 2) -> List[Dict]:
    """
    生成人员安排数据的便捷方法
    
    Args:
        business_object: 业务对象名称，如 searchStaff
        total_samples: 总样本数，默认10
        variations_per_rule: 每个规则的变种数量，默认2
        
    Returns:
        生成的数据列表
    """
    return get_staffing_service().generate_staffing_data(
        business_object, total_samples, variations_per_rule
    )

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的人员安排数据
        staffing_data = generate_staffing_data('searchStaff', 10, 2)
        print(f"\n生成的数据数量: {len(staffing_data)}")
        
        # 打印第一条数据
        if staffing_data:
            print("\n示例数据:")
            print(f"问题: {staffing_data[0]['question']}")
            print(f"答案: {staffing_data[0]['answer']}")
    except Exception as e:
        import traceback
        print(f"\n发生错误: {e}")
        traceback.print_exc() 