#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.service.staff_update_service import generate_staff_update_data

def verify_staff_update_mapping():
    """验证人员更新数据中问题和答案之间的字段映射"""
    print("生成updateStaff数据样本用于验证...")
    
    # 只生成3条数据进行验证
    data = generate_staff_update_data(total_samples=3, variations_per_rule=1)
    
    print(f"生成了 {len(data)} 条数据\n")
    
    # 验证每条数据
    for i, item in enumerate(data):
        print(f"\n===== 样本 {i+1} =====")
        
        question = item['question']
        answer = item['answer']
        
        # 检查personName映射
        q_person_name = question.get('personName', '未指定')
        a_person_name = answer.get('personName', '未指定')
        
        print(f"问题中的personName: {q_person_name}")
        print(f"答案中的personName: {a_person_name}")
        print(f"映射是否正确: {q_person_name == a_person_name}")
        
        # 检查projectFrom映射到personProject
        q_project_from = question.get('projectFrom', '未指定')
        a_person_project = answer.get('personProject', '未指定')
        
        print(f"问题中的projectFrom: {q_project_from}")
        print(f"答案中的personProject: {a_person_project}")
        
        # 检查staffId映射到personJobNumber
        q_staff_id = question.get('staffId', '未指定')
        a_job_number = answer.get('personJobNumber', '未指定')
        
        print(f"问题中的staffId: {q_staff_id}")
        print(f"答案中的personJobNumber: {a_job_number}")
        
        # 检查roleType映射到roleInfo
        q_role_type = question.get('roleType', '未指定')
        a_role_info = answer.get('roleInfo', '未指定')
        
        print(f"问题中的roleType: {q_role_type}")
        print(f"答案中的roleInfo: {a_role_info}")
        
        # 打印完整的数据以便检查
        print("\n完整数据:")
        print(f"问题: {json.dumps(question, ensure_ascii=False, indent=2)}")
        print(f"答案: {json.dumps(answer, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    verify_staff_update_mapping() 