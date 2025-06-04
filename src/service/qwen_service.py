#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Any, Optional
import os
import json
import datetime
from src.service.staffing_service import generate_staffing_data

def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        dir_path: 目录路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def format_question(question_data: Dict) -> str:
    """
    将问题数据格式化为自然语言
    
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

def generate_qwen_data(business_object: str, total_samples: int = 100, variations_per_rule: int = 2) -> str:
    """
    生成通义千问训练数据并保存为jsonl文件
    
    Args:
        business_object: 业务对象代码，例如searchStaff
        total_samples: 生成数据总条数，默认100
        variations_per_rule: 每个规则的变种数量，默认2
        
    Returns:
        生成的jsonl文件路径
    """
    print(f"开始为业务对象 '{business_object}' 生成千问训练数据...")
    
    # 确保输出目录存在
    output_dir = os.path.join("outputs", "data", "qwen")
    ensure_dir(output_dir)
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 构建输出文件名
    output_file = os.path.join(output_dir, f"{business_object}_{total_samples}_{timestamp}.jsonl")
    
    # 生成数据
    staffing_data = generate_staffing_data(business_object, total_samples, variations_per_rule)
    print(f"成功生成 {len(staffing_data)} 条数据")
    
    # 转换为千问格式并写入jsonl文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in staffing_data:
            # 获取问题和答案
            question_data = data.get('question', {})
            answer_data = data.get('answer', {})
            
            # 格式化问题
            formatted_question = format_question(question_data)
            
            # 获取规则codebase
            codebase = get_rule_codebase(business_object, data)
            
            # 创建答案JSON字符串
            answer_json = json.dumps(answer_data, ensure_ascii=False)
            
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
    
    print(f"数据已保存到 {output_file}")
    return output_file

# 使用示例
if __name__ == "__main__":
    try:
        # 生成searchStaff的千问训练数据
        output_file = generate_qwen_data('searchStaff', 10, 2)
        print(f"生成的文件路径: {output_file}")
    except Exception as e:
        import traceback
        print(f"发生错误: {e}")
        traceback.print_exc() 