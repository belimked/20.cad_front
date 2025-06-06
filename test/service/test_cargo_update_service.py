#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试StaffingService服务功能
"""

from src.service.cargo_update_service import generate_update_cargo_data
from src.service.rule_logic import get_rule_components, get_sorted_rules

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
    根据数据特征找到对应的规则codebase
    """
    sorted_rules = get_sorted_rules(business_object)

    # 根据问题的字段判断属于哪个规则
    if 'personName' in data['question'] and 'personProjectQuery' in data['question']:
        # 查询人员被安排到项目
        for rule in sorted_rules:
            if rule.get('id') == 2:
                return rule.get('codebase', '')
    elif 'projectName' in data['question'] and 'projectPersonQuery' in data['question']:
        # 查询项目安排了哪些人员
        for rule in sorted_rules:
            if rule.get('id') == 3:
                return rule.get('codebase', '')
    elif 'projectStatusQuery' in data['question']:
        # 查询项目没有安排人员
        for rule in sorted_rules:
            if rule.get('id') == 1:
                return rule.get('codebase', '')

    # 如果没有找到匹配的规则，则查看规则的codeList
    for rule in sorted_rules:
        code_list = rule.get('codeList', [])
        if isinstance(code_list, list) and len(code_list) > 0:
            if isinstance(code_list[0], str) and ';' in code_list[0]:
                # 检查是否匹配问题字段
                codes = code_list[0].split(';')
                matched = True
                for code in codes:
                    if code == '01' and 'projectStatusQuery' not in data['question']:
                        matched = False
                    elif code == '02' and 'personProjectQuery' not in data['question']:
                        matched = False
                    elif code == '03' and 'projectPersonQuery' not in data['question']:
                        matched = False
                    elif code == '04' and 'personName' not in data['question']:
                        matched = False
                    elif code == '05' and 'projectName' not in data['question']:
                        matched = False

                if matched:
                    return rule.get('codebase', '')

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
        variations_per_rule = 1

        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        staffing_data = generate_update_cargo_data(business_object, total_samples, variations_per_rule)

        # 打印生成的数据统计
        print(f"\n生成数据成功！总共生成了 {len(staffing_data)} 个数据")

        # 打印所有样本数据
        if staffing_data:
            print("\n所有样本数据示例:")
            for i, data in enumerate(staffing_data):
                # 获取该样本对应的规则codebase
                codebase = get_rule_codebase(business_object, data)

                # 格式化问题为自然语言
                formatted_question = format_question(data['question'])

                print(f"\n样本 {i+1}:")
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
