#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试StaffingService服务功能
"""

from src.service.cargo_update_service import generate_update_cargo_data
from src.service.staffing_update_service import generate_update_staffing_data
from src.service.rule_logic import get_rule_components, get_sorted_rules, format_question_by_codebase

def format_question(question_data):
    """
    将问题数据格式化为自然语言
    """
    if 'personName' in question_data and 'personProjectQuery' in question_data:
        return f"{question_data['personName']}{question_data['personProjectQuery']}"
    elif 'projectName' in question_data and 'projectPersonQuery' in question_data:
        return f"{question_data['projectName']}{question_data['projectPersonQuery']}"
    elif 'projectStatusQuery' in question_data:
        return question_data['projectStatusQuery']
    else:
        # 如果没有匹配的模式，则返回原始格式
        return str(question_data)

def get_rule_codebase(business_object, data):
    """
    根据数据中的rule_id找到对应的规则codebase
    """
    sorted_rules = get_sorted_rules(business_object)
    
    # 直接通过rule_id匹配对应的规则
    if 'rule_id' in data:
        for rule in sorted_rules:
            if rule.get('id') == data['rule_id']:
                return rule.get('codebase', '')
    
    # 如果没有找到匹配的规则，返回空字符串
    return ""

def test_generate_staffing_data(businessObject):
    """
    测试生成人员安排数据功能
    """
    print("开始测试StaffingService服务...")
    
    try:
        # 生成searchStaff的人员安排数据，使用较小的样本数进行测试
        business_object = businessObject
        total_samples = 100
        variations_per_rule = 5
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        staffing_data = generate_update_cargo_data(business_object, total_samples, variations_per_rule)
        # staffing_data = generate_update_staffing_data(business_object, total_samples, variations_per_rule)

        # 打印生成的数据统计
        print(f"\n生成数据成功！总共生成了 {len(staffing_data)} 个数据")
        
        # 打印所有样本数据
        if staffing_data:
            print("\n所有样本数据示例:")
            for i, data in enumerate(staffing_data):
                # 获取该样本对应的规则codebase
                codebase = get_rule_codebase(business_object, data)
                
                # 使用新方法格式化问题
                formatted_question = format_question_by_codebase(data['question'], codebase, business_object)

                print(f"\n样本 {i+1}:")
                print(f"原始问题: {data['question']}")
                print(f"问题: {formatted_question}")
                print(f"答案: {data['answer']}")
                print(f"codebase: \"{codebase}\"")
        
        # 分析数据结构
        question_keys = set()
        answer_keys = set()
        
        for data in staffing_data:
            question_keys.update(data['question'].keys())
            answer_keys.update(data['answer'].keys())
        
        print("\n数据结构分析:")
        print(f"问题字段列表: {sorted(list(question_keys))}")
        print(f"答案字段列表: {sorted(list(answer_keys))}")
        
        print("\nStaffingService服务测试完成，功能正常！")
        return True
        
    except Exception as e:
        import traceback
        print(f"\n测试过程中发生错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # test_generate_staffing_data('updateStaff')
    # test_generate_staffing_data('searchStaff')
    test_generate_staffing_data('updateCargo')
