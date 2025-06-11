#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import os

# CSV文件路径
csv_file = "/Users/saul/Desktop/fangda_cost_test_09_rchase_order_material.csv"
# drawings.json文件路径
drawings_json_file = "src/dict/drawings.json"

def update_drawings():
    try:
        # 读取CSV文件
        with open(csv_file, 'r', encoding='utf-8') as f:
            drawing_codes = [line.strip() for line in f if line.strip()]
        
        print(f"从CSV文件读取了 {len(drawing_codes)} 个图纸编号")
        
        # 创建新的图纸数据
        drawings_data = []
        for idx, code in enumerate(drawing_codes, 1):
            drawings_data.append({
                "drawname": code,
                "drawid": idx
            })
        
        # 写入到drawings.json文件
        with open(drawings_json_file, 'w', encoding='utf-8') as f:
            json.dump(drawings_data, f, ensure_ascii=False, indent=2)
        
        print(f"成功更新了 {len(drawings_data)} 个图纸编号到 {drawings_json_file}")
        
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if update_drawings():
        print("图纸数据更新成功！")
    else:
        print("图纸数据更新失败！")
        sys.exit(1) 