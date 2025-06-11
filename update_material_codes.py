#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os
import re

# CSV文件路径
csv_file = "/Users/saul/Desktop/fangda_cost_test_01_rchase_order_material.csv"
# material_code_extended_dict.json文件路径
material_code_file = "src/dict/material_code_extended_dict.json"

def is_valid_item_code(text):
    """
    判断文本是否符合物料编码格式（简单判断为字母数字组合且长度合适）
    """
    # 去除引号和空白
    text = text.strip('"\'').strip()
    # 判断是否为编码格式（简单规则：至少包含一个数字和字母，长度在5-10之间）
    if len(text) < 4 or len(text) > 15:
        return False
    
    # 检查是否包含字母和数字
    has_letter = False
    has_digit = False
    for char in text:
        if char.isalpha():
            has_letter = True
        if char.isdigit():
            has_digit = True
    
    # 如果文本太长或包含大量特殊字符，可能是描述而不是编码
    if len(text.split()) > 3 or text.count('(') > 0 or text.count('（') > 0:
        return False
    
    return has_letter or has_digit

def update_material_codes():
    try:
        # 读取CSV文件
        with open(csv_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 提取有效的物料编码
        valid_codes = []
        for line in lines:
            line = line.strip()
            if line and is_valid_item_code(line):
                code = line.strip('"\'').strip()
                valid_codes.append(code)
        
        print(f"从CSV文件提取了 {len(valid_codes)} 个有效的物料编码")
        
        # 创建新的物料编码数据
        material_data = []
        for idx, code in enumerate(valid_codes, 1):
            material_data.append({
                "id": idx,
                "itemCode": code
            })
        
        # 写入到material_code_extended_dict.json文件
        with open(material_code_file, 'w', encoding='utf-8') as f:
            json.dump(material_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功更新了 {len(material_data)} 个物料编码到 {material_code_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if update_material_codes():
        print("物料编码数据更新成功！")
    else:
        print("物料编码数据更新失败！")
        sys.exit(1) 