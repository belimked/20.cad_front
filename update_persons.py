#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os

# CSV文件路径
csv_file = "/Users/saul/Desktop/employee_test_mstb_employee.csv"
# persons.json文件路径
persons_json_file = "src/dict/persons.json"
# 最大行数限制
max_lines = 500

def update_persons():
    try:
        # 读取CSV文件，仅取前500行
        with open(csv_file, 'r', encoding='utf-8') as f:
            person_names = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                name = line.strip()
                if name:
                    person_names.append(name)
        
        print(f"从CSV文件读取了 {len(person_names)} 个人员名称 (限制为前{max_lines}个)")
        
        # 创建新的persons数据
        persons_data = []
        for idx, name in enumerate(person_names, 1):
            persons_data.append({
                "name": name,
                "id": idx
            })
        
        # 写入到persons.json文件
        with open(persons_json_file, 'w', encoding='utf-8') as f:
            json.dump(persons_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功更新了 {len(persons_data)} 个人员到 {persons_json_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if update_persons():
        print("人员数据更新成功！")
    else:
        print("人员数据更新失败！")
        sys.exit(1) 