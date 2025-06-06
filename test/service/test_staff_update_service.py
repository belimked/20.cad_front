#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试StaffUpdateService服务功能
"""

from src.service.staffing_update_service import generate_update_staffing_data
from src.service.rule_logic import get_rule_components, get_sorted_rules

def format_question(question_data):
    """
    将问题数据格式化为自然语言
    """
    # 安排项目人员的情况
    if 'addStaffAction' in question_data and ('安排' in question_data['addStaffAction'] or '添加' in question_data['addStaffAction']):
        if 'personName' in question_data and 'projectFrom' in question_data and 'roleType' in question_data:
            return f"{question_data.get('addStaffAction', '')}将{question_data.get('personName', '')}安排到{question_data.get('projectFrom', '')}的{question_data.get('roleType', '')}角色"
        elif 'staffId' in question_data and 'projectFrom' in question_data and 'roleType' in question_data:
            return f"{question_data.get('addStaffAction', '')}将{question_data.get('staffId', '')}安排到{question_data.get('projectFrom', '')}的{question_data.get('roleType', '')}角色"
    
    # 撤销项目人员的情况
    elif 'removeStaffAction' in question_data and ('撤销' in question_data['removeStaffAction'] or '删除' in question_data['removeStaffAction']):
        if 'personName' in question_data and 'projectFrom' in question_data and 'roleType' in question_data:
            return f"{question_data.get('removeStaffAction', '')}将{question_data.get('personName', '')}{question_data.get('projectFrom', '')}的{question_data.get('roleType', '')}角色中删除"
        elif 'staffId' in question_data and 'projectFrom' in question_data and 'roleType' in question_data:
            return f"{question_data.get('removeStaffAction', '')}将{question_data.get('staffId', '')}{question_data.get('projectFrom', '')}的{question_data.get('roleType', '')}角色中删除"

    # 将人员从项目移除的情况
    elif 'will' in question_data and 'removeAction' in question_data:
        if 'personName' in question_data and 'projectFrom' in question_data:
            return f"{question_data.get('will', '')}{question_data.get('personName', '')}{question_data.get('projectFrom', '')}中移除"
        elif 'staffId' in question_data and 'projectFrom' in question_data:
            return f"{question_data.get('will', '')}{question_data.get('staffId', '')}{question_data.get('projectFrom', '')}中移除"
    # print(f"问题原始: {str(question_data)})

    # 如果没有匹配的模式，则返回原始格式
    return str(question_data)

def get_rule_codebase(business_object, data):
    """
    根据数据特征找到对应的规则codebase
    """
    sorted_rules = get_sorted_rules(business_object)
    
    # 根据问题的字段判断属于哪个规则
    question = data['question']
    print(f"\n打印问题数据: {question}")
    
    # 安排人员规则
    if ('addStaffAction' in question and '安排' in question.get('addStaffAction', '')):
        if 'personName' in question:
            # 规则1: 安排XX到XX项目的XX角色
            for rule in sorted_rules:
                if rule.get('id') == 1:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question or 'staffId' in question:
            # 规则4: 安排工号XX到XX项目的XX角色
            for rule in sorted_rules:
                if rule.get('id') == 4:
                    return rule.get('codebase', '')
    
    # 删除人员规则
    elif ('removeStaffAction' in question and '撤销' in question.get('removeStaffAction', '')) or \
         ('removeStaffAction' in question and '删除' in question.get('removeStaffAction', '')):
        if 'personName' in question:
            # 规则2: 删除XX的XX项目的XX角色
            for rule in sorted_rules:
                if rule.get('id') == 2:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question or 'staffId' in question:
            # 规则5: 删除工号XX的XX项目的XX角色
            for rule in sorted_rules:
                if rule.get('id') == 5:
                    return rule.get('codebase', '')
    
    # 移除人员规则
    elif 'will' in question and 'removeAction' in question:
        if 'personName' in question:
            # 规则3: 将XX从XX项目移除
            for rule in sorted_rules:
                if rule.get('id') == 3:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question or 'staffId' in question:
            # 规则6: 将工号XX从XX项目移除
            for rule in sorted_rules:
                if rule.get('id') == 6:
                    return rule.get('codebase', '')
    
    return ""

def test_generate_staff_update_data():
    """
    测试生成人员安排更新数据功能
    """
    print("开始测试StaffUpdateService服务...")
    
    try:
        # 生成updateStaff的人员安排更新数据，使用较小的样本数进行测试
        business_object = 'updateStaff'
        total_samples = 100
        variations_per_rule = 1
        
        print(f"正在为业务对象 '{business_object}' 生成 {total_samples} 个样本，每个规则 {variations_per_rule} 个变种...")
        staff_update_data = generate_update_staffing_data(business_object, total_samples, variations_per_rule)
        
        # 打印生成的数据统计
        print(f"\n生成数据成功！总共生成了 {len(staff_update_data)} 个数据")
        
        # 打印所有样本数据
        if staff_update_data:
            print("\n所有样本数据示例:")
            for i, data in enumerate(staff_update_data):
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
        
        for data in staff_update_data:
            question_keys.update(data['question'].keys())
            answer_keys.update(data['answer'].keys())
        
        print("\n数据结构分析:")
        print(f"问题字段列表: {sorted(list(question_keys))}")
        print(f"答案字段列表: {sorted(list(answer_keys))}")
        
        print("\nStaffUpdateService服务测试完成，功能正常！")
        return True
        
    except Exception as e:
        import traceback
        print(f"\n测试过程中发生错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_generate_staff_update_data() 
