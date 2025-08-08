#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional, Callable
import os
import json
import datetime
import importlib
from src.service.staffing_service import generate_staffing_data
from src.service.staff_update_service import generate_staff_update_data
from src.service.cargo_update_service import generate_cargo_update_data
from src.service.common import get_random_string_connector, join_names_smart

def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def format_question_searchStaff(question_data: Dict) -> str:
    """
    将searchStaff的问题数据格式化为自然语言
    
    Args:
        question_data: 问题数据字典
        
    Returns:
        格式化后的问题字符串
    """
    if 'personName' in question_data and 'personProjectQuery' in question_data:
        return f"{question_data['personName']}{question_data['personProjectQuery']}"
    elif 'projectName' in question_data and 'projectPersonQuery' in question_data:
        return f"{question_data['projectName']}{question_data['projectPersonQuery']}"
    elif 'projectStatusQuery' in question_data:
        return question_data['projectStatusQuery']
    else:
        return str(question_data)

def format_question_updateStaff(question_data: Dict) -> str:
    """
    将updateStaff的问题数据格式化为自然语言
    
    Args:
        question_data: 问题数据字典
        
    Returns:
        格式化后的问题字符串
    """
    # 安排项目人员的情况
    if 'addStaffAction' in question_data:
        if 'personName' in question_data:
            # 按照人名安排到项目
            if 'projectFrom' in question_data and 'roleType' in question_data:
                return f"{question_data.get('addStaffAction', '')}将{question_data.get('personName', '')}{question_data.get('toAction', '')}"\
                       f"{question_data.get('projectFrom', '')}{question_data.get('projectInfo', '')}的{question_data.get('roleType', '')}{question_data.get('role', '')}"
        elif 'staffId' in question_data:
            # 按照工号安排到项目
            if 'projectFrom' in question_data and 'roleType' in question_data:
                return f"{question_data.get('addStaffAction', '')}{question_data.get('staffId', '')}{question_data.get('toAction', '')}"\
                       f"{question_data.get('projectFrom', '')}{question_data.get('projectInfo', '')}的{question_data.get('roleType', '')}{question_data.get('role', '')}"
    
    # 撤销/删除项目人员的情况
    elif 'removeStaffAction' in question_data:
        if 'personName' in question_data:
            # 按照人名删除项目角色
            if 'projectFrom' in question_data and 'roleType' in question_data:
                return f"{question_data.get('removeStaffAction', '')}{question_data.get('will', '')}{question_data.get('personName', '')}{question_data.get('connector', '')}"\
                       f"{question_data.get('projectFrom', '')}{question_data.get('projectInfo', '')}的{question_data.get('roleType', '')}{question_data.get('role', '')}"
        elif 'staffId' in question_data:
            # 按照工号删除项目角色
            if 'projectFrom' in question_data and 'roleType' in question_data:
                return f"{question_data.get('removeStaffAction', '')}{question_data.get('will', '')}{question_data.get('staffId', '')}{question_data.get('connector', '')}"\
                       f"{question_data.get('projectFrom', '')}{question_data.get('projectInfo', '')}的{question_data.get('roleType', '')}{question_data.get('role', '')}"
    
    # 将人员从项目移除的情况
    elif 'will' in question_data and 'removeAction' in question_data:
        if 'personName' in question_data:
            # 将人员从项目移除
            return f"{question_data.get('will', '')}{question_data.get('personName', '')}{question_data.get('connector', '')}"\
                   f"{question_data.get('toAction', '')}项目{question_data.get('removeAction', '')}"
        elif 'staffId' in question_data:
            # 将工号从项目移除
            return f"{question_data.get('will', '')}{question_data.get('staffId', '')}{question_data.get('connector', '')}"\
                   f"{question_data.get('toAction', '')}项目{question_data.get('removeAction', '')}"
    
    # 如果没有匹配的模式，则将字典转换为更友好的格式
    try:
        # 尝试将字典的所有值连接成一个自然语句
        parts = []
        for key, value in question_data.items():
            if isinstance(value, str) and value:
                parts.append(value)
        
        if parts:
            return " ".join(parts)
    except:
        pass
    
    # 最后的备用方案：返回原始字典字符串
    return str(question_data)

def format_question_updateCargo(question_data: Dict) -> str:
    """
    将updateCargo的问题数据格式化为自然语言
    
    Args:
        question_data: 问题数据字典
        
    Returns:
        格式化后的问题字符串
    """
    # 对比送货单件数/重量/面积的情况
    if '操作' in question_data and ('对比' in question_data['操作']):
        result_parts = []
        
        # 添加操作
        if question_data.get('操作'):
            result_parts.append(question_data['操作'])
        
        # 添加项目
        if question_data.get('项目'):
            result_parts.append(question_data['项目'])
        
        # 添加供应商
        if question_data.get('供应商'):
            result_parts.append(question_data['供应商'])
        
        # 添加单号或送货单号
        if question_data.get('对象单号'):
            result_parts.append(question_data['对象单号'])
        elif question_data.get('送货单号'):
            result_parts.append(question_data['送货单号'])
        
        return join_names_smart(result_parts)
    
    # 审核通过货单的情况
    elif '操作' in question_data and ('审核通过' in question_data['操作']):
        result_parts = []
        
        # 添加操作
        if question_data.get('操作'):
            result_parts.append(question_data['操作'])
        
        # 添加项目
        if question_data.get('项目'):
            result_parts.append(question_data['项目'])
        
        # 添加供应商
        if question_data.get('供应商'):
            result_parts.append(question_data['供应商'])
        
        # 添加单号或送货单号
        if question_data.get('对象单号'):
            result_parts.append(question_data['对象单号'])
        elif question_data.get('送货单号'):
            result_parts.append(question_data['送货单号'])
        
        return join_names_smart(result_parts)
    
    # 导出结算单的情况
    elif '操作' in question_data and ('导出结算单' in question_data['操作']):
        result_parts = []
        
        # 添加操作
        if question_data.get('操作'):
            result_parts.append(question_data['操作'])
        
        # 添加项目
        if question_data.get('项目'):
            result_parts.append(question_data['项目'])
        
        # 添加供应商
        if question_data.get('供应商'):
            result_parts.append(question_data['供应商'])
        
        # 添加单号或送货单号
        if question_data.get('对象单号'):
            result_parts.append(question_data['对象单号'])
        elif question_data.get('送货单号'):
            result_parts.append(question_data['送货单号'])
        
        return join_names_smart(result_parts)
    
    # 如果没有匹配的模式，则将字典转换为更友好的格式
    try:
        # 尝试将字典的所有值连接成一个自然语句
        parts = []
        for key, value in question_data.items():
            if isinstance(value, str) and value:
                parts.append(value)
        
        if parts:
            return join_names_smart(parts)
    except:
        pass
    
    # 最后的备用方案：返回原始字典字符串
    return str(question_data)

def get_format_question_function(business_object: str) -> Callable[[Dict], str]:
    """
    根据业务对象获取对应的问题格式化函数
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        格式化函数
    """
    format_functions = {
        'searchStaff': format_question_searchStaff,
        'updateStaff': format_question_updateStaff,
        'updateCargo': format_question_updateCargo
    }
    
    return format_functions.get(business_object, lambda x: str(x))

def get_rule_codebase_searchStaff(rules: List[Dict], question: Dict) -> str:
    """
    根据searchStaff的问题数据获取对应的规则codebase
    
    Args:
        rules: 规则列表
        question: 问题数据
        
    Returns:
        规则codebase字符串
    """
    if 'personName' in question and ('personProjectQuery' in question):
        # 规则2: 查询人员被安排到项目
        for rule in rules:
            if rule.get('id') == 2:
                return rule.get('codebase', '')
    elif 'projectName' in question and ('projectPersonQuery' in question):
        # 规则3: 查询项目安排了哪些人员
        for rule in rules:
            if rule.get('id') == 3:
                return rule.get('codebase', '')
    elif 'projectStatusQuery' in question:
        # 规则1: 查询项目没有安排人员
        for rule in rules:
            if rule.get('id') == 1:
                return rule.get('codebase', '')
    
    return ""

def get_rule_codebase_updateStaff(rules: List[Dict], question: Dict) -> str:
    """
    根据updateStaff的问题数据获取对应的规则codebase
    
    Args:
        rules: 规则列表
        question: 问题数据
        
    Returns:
        规则codebase字符串
    """
    # 安排人员规则
    if ('staffUpdateOperation' in question and '安排' in question.get('staffUpdateOperation', '')):
        if 'personName' in question:
            # 规则1: 安排XX到XX项目的XX角色
            for rule in rules:
                if rule.get('id') == 1:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question:
            # 规则4: 安排工号XX到XX项目的XX角色
            for rule in rules:
                if rule.get('id') == 4:
                    return rule.get('codebase', '')
    
    # 删除人员规则
    elif ('staffUpdateOperation' in question and '撤销' in question.get('staffUpdateOperation', '')):
        if 'personName' in question:
            # 规则2: 删除XX的XX项目的XX角色
            for rule in rules:
                if rule.get('id') == 2:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question:
            # 规则5: 删除工号XX的XX项目的XX角色
            for rule in rules:
                if rule.get('id') == 5:
                    return rule.get('codebase', '')
    
    # 移除人员规则
    elif 'moveFromOperation' in question and '将' in question.get('moveFromOperation', ''):
        if 'personName' in question:
            # 规则3: 将XX从XX项目移除
            for rule in rules:
                if rule.get('id') == 3:
                    return rule.get('codebase', '')
        elif 'personJobNumber' in question:
            # 规则6: 将工号XX从XX项目移除
            for rule in rules:
                if rule.get('id') == 6:
                    return rule.get('codebase', '')
    
    return ""

def get_rule_codebase_updateCargo(rules: List[Dict], question: Dict) -> str:
    """
    根据updateCargo的问题数据获取对应的规则codebase
    
    Args:
        rules: 规则列表
        question: 问题数据
        
    Returns:
        规则codebase字符串
    """
    # 对比送货单件数/重量/面积的情况
    if '操作' in question and '对比' in question.get('操作', ''):
        for rule in rules:
            if rule.get('id') in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                if '件数' in question.get('操作', ''):
                    return rule.get('codebase', '')
                elif '重量' in question.get('操作', ''):
                    return rule.get('codebase', '')
                elif '面积' in question.get('操作', ''):
                    return rule.get('codebase', '')
    
    # 审核通过货单的情况
    elif '操作' in question and '审核通过' in question.get('操作', ''):
        for rule in rules:
            if rule.get('id') in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                return rule.get('codebase', '')
    
    # 导出结算单的情况
    elif '操作' in question and '导出结算单' in question.get('操作', ''):
        for rule in rules:
            if rule.get('id') in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                return rule.get('codebase', '')
    
    return ""

def get_rule_codebase_function(business_object: str) -> Callable[[List[Dict], Dict], str]:
    """
    根据业务对象获取对应的规则codebase获取函数
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        规则codebase获取函数
    """
    codebase_functions = {
        'searchStaff': get_rule_codebase_searchStaff,
        'updateStaff': get_rule_codebase_updateStaff,
        'updateCargo': get_rule_codebase_updateCargo
    }
    
    return codebase_functions.get(business_object, lambda rules, question: "")

def get_data_generator_function(business_object: str) -> Callable[[str, int, int], List[Dict]]:
    """
    根据业务对象获取对应的数据生成函数
    
    Args:
        business_object: 业务对象名称
        
    Returns:
        数据生成函数
    """
    generator_functions = {
        'searchStaff': generate_staffing_data,
        'updateStaff': generate_staff_update_data,
        'updateCargo': generate_cargo_update_data
    }
    
    return generator_functions.get(business_object, generate_staffing_data)

def get_rule_codebase(business_object: str, data: Dict) -> str:
    """
    根据问题数据获取对应的规则codebase
    
    Args:
        business_object: 业务对象代码
        data: 生成的数据
        
    Returns:
        规则codebase字符串
    """
    from src.service.rule_logic import get_sorted_rules
    
    # 获取所有规则
    rules = get_sorted_rules(business_object)
    
    # 根据问题字段匹配规则
    question = data.get('question', {})
    
    # 获取相应的codebase函数
    codebase_function = get_rule_codebase_function(business_object)
    
    # 使用相应的函数获取codebase
    return codebase_function(rules, question)

def process_answer_fields(answer_data: Dict) -> Dict:
    """
    处理答案字段，进行数据清理和转换
    
    Args:
        answer_data: 原始答案数据字典
        
    Returns:
        处理后的答案数据字典
    """
    # 创建答案数据的副本，避免修改原始数据
    processed_data = answer_data.copy()
    
    # 1. 处理"项目"字段 - 去除"项目"前缀
    if "项目" in processed_data and processed_data["项目"]:
        project_value = processed_data["项目"]
        # 去除开头的"项目"
        if project_value.startswith("项目"):
            project_value = project_value[2:]
        # 去除结尾的"项目"
        if project_value.endswith("项目"):
            project_value = project_value[:-2]
        processed_data["项目"] = project_value
    
    # 2. 处理"供应商"字段 - 只保留供应商名称
    if "供应商" in processed_data and processed_data["供应商"]:
        supplier_value = processed_data["供应商"]
        # 去除"是"前缀
        if supplier_value.startswith("是"):
            supplier_value = supplier_value[1:]
        # 去除"的"后缀
        if supplier_value.endswith("的"):
            supplier_value = supplier_value[:-1]
        processed_data["供应商"] = supplier_value
    
    # 3. 处理"对象状态"字段 - 根据"操作"字段值设置
    if "操作" in processed_data:
        operation = processed_data["操作"]
        if operation == "导出结算单":
            processed_data["对象状态"] = "审核通过"
        elif "对比" in operation:
            processed_data["对象状态"] = "待成本审核"
        elif "审核通过" in operation:
            processed_data["对象状态"] = "待成本审核"
    
    return processed_data

def generate_qwen_data(business_object: str, total_samples: int = 100, variations_per_rule: int = 2, save_original: bool = True) -> Tuple[str, Optional[str]]:
    """
    生成通义千问训练数据并保存为jsonl文件，同时可选择保存原始数据为json文件
    
    Args:
        business_object: 业务对象代码，例如searchStaff或updateStaff
        total_samples: 生成数据总条数，默认100
        variations_per_rule: 每个规则的变种数量，默认2
        save_original: 是否同时保存原始格式数据，默认True
        
    Returns:
        Tuple包含: 
        - 生成的qwen格式jsonl文件路径
        - 生成的原始数据json文件路径（如果save_original=False则为None）
    """
    print(f"开始为业务对象 '{business_object}' 生成千问训练数据...")
    
    # 确保输出目录存在
    output_dir = os.path.join("outputs", "data", "qwen")
    ensure_dir(output_dir)
    original_dir = os.path.join("outputs", "data", "original")
    if save_original:
        ensure_dir(original_dir)
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 构建临时输出文件名（使用请求数量）
    temp_output_file = os.path.join(output_dir, f"{business_object}_{total_samples}_{timestamp}.jsonl")
    temp_original_file = None
    if save_original:
        temp_original_file = os.path.join(original_dir, f"{business_object}_{total_samples}_{timestamp}.json")
    
    # 获取数据生成函数
    data_generator = get_data_generator_function(business_object)
    
    # 生成数据
    generated_data = data_generator(business_object, total_samples, variations_per_rule)
    actual_count = len(generated_data)
    print(f"成功生成 {actual_count} 条数据")
    
    # 如果需要保存原始数据
    if save_original and temp_original_file:
        with open(temp_original_file, 'w', encoding='utf-8') as f:
            json.dump(generated_data, f, ensure_ascii=False, indent=2)
        print(f"原始数据已临时保存")
    
    # 获取问题格式化函数
    format_function = get_format_question_function(business_object)
    
    # 转换为千问格式并写入jsonl文件
    written_count = 0
    with open(temp_output_file, 'w', encoding='utf-8') as f:
        for data in generated_data:
            # 获取问题和答案
            question_data = data.get('question', {})
            answer_data = data.get('answer', {})
            
            # 处理答案字段
            processed_answer_data = process_answer_fields(answer_data)
            
            # 格式化问题
            formatted_question = format_function(question_data)
            
            # 获取规则codebase
            codebase = get_rule_codebase(business_object, data)
            
            # 创建答案JSON字符串
            answer_json = json.dumps(processed_answer_data, ensure_ascii=False)
            
            # 创建千问格式数据
            qwen_data = {
                "messages": [
                    {
                        "role": "user", 
                        "content": f"### 指令：\n你是一个企业信息检索助手，请根据查询内容，返回包含以下字段的标准JSON响应，缺失字段填\"无\"：\n[操作, 对象, 项目, 供应商, 对象状态, 对象提交时间, 对象审核时间, 对象发货时间, 对象下单时间, 材料状态, 材料类型, 材料工艺图, 材料工程属性, 材料所属订单, 材料编号, 对象金额, 对象附加费用, 材料AI金额条件, 对象审核单类型, 材料是否异型, 材料是否超长超宽, 对象单号, 送货单号, 运费, 其他费用, 其他费用说明, 网版费, 人员姓名, 人员工号, 角色信息, 人员项目]\n\n### 查询问题\n{formatted_question}"
                    },
                    {
                        "role": "assistant", 
                        "content": answer_json
                    }
                ]
            }
            
            # 将数据写入jsonl文件
            f.write(json.dumps(qwen_data, ensure_ascii=False) + '\n')
            written_count += 1
    
    print(f"写入了 {written_count} 条记录到千问格式文件")
    
    # 用实际数量重命名文件
    final_output_file = os.path.join(output_dir, f"{business_object}_{actual_count}_{timestamp}.jsonl")
    final_original_file = None
    
    if temp_output_file != final_output_file:
        os.rename(temp_output_file, final_output_file)
        print(f"文件已重命名为反映实际数据量: {os.path.basename(final_output_file)}")
    
    if save_original and temp_original_file:
        final_original_file = os.path.join(original_dir, f"{business_object}_{actual_count}_{timestamp}.json")
        if temp_original_file != final_original_file:
            os.rename(temp_original_file, final_original_file)
            print(f"原始数据文件已重命名为反映实际数据量: {os.path.basename(final_original_file)}")
    
    print(f"千问格式数据已保存到 {final_output_file}")
    return final_output_file, final_original_file

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的千问训练数据（同时生成原始数据）
        qwen_file, original_file = generate_qwen_data('searchStaff', 10, 2)
        print(f"生成的千问文件路径: {qwen_file}")
        print(f"生成的原始文件路径: {original_file}")
        
        # 也可以生成updateStaff的千问训练数据，但不保存原始数据
        # qwen_file, _ = generate_qwen_data('updateStaff', 10, 2, save_original=False)
        # print(f"生成的千问文件路径: {qwen_file}")
        
        # 或者生成updateCargo的千问训练数据
        # qwen_file, original_file = generate_qwen_data('updateCargo', 10, 2)
        # print(f"生成的千问文件路径: {qwen_file}")
        # print(f"生成的原始文件路径: {original_file}")
    except Exception as e:
        import traceback
        print(f"发生错误: {e}")
        traceback.print_exc() 
