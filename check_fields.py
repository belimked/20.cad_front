#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import glob
import os

def check_field_completion(obj_types=None, field_name='object'):
    """检查各业务对象中指定字段的填充情况"""
    # 默认检查所有业务对象
    if obj_types is None:
        obj_types = ['searchStaff', 'updateCargo', 'updateStaff', 'searchContract']
    
    print(f"检查各业务对象的{field_name}字段填充情况:")
    for obj_type in obj_types:
        file_path = f'outputs/data/original/{obj_type}_*_*.json'
        files = glob.glob(file_path)
        
        if files:
            # 获取最新的文件
            latest_file = max(files, key=os.path.getctime)
            print(f"\n文件: {latest_file}")
            
            with open(latest_file) as f:
                data = json.load(f)
            
            filled_count = 0
            total = len(data)
            example_value = "<空>"
            
            for item in data:
                field_value = item['answer'].get(field_name, '')
                if field_value:
                    filled_count += 1
                    if example_value == "<空>":
                        example_value = field_value
            
            fill_rate = filled_count/total*100 if total > 0 else 0
            print(f"{obj_type}: {filled_count}/{total} 条数据有{field_name}字段值，填充率: {fill_rate:.2f}%")
            print(f"  示例{field_name}字段值: {example_value}")
        else:
            print(f"{obj_type}: 未找到数据文件")

if __name__ == "__main__":
    # 检查object字段
    check_field_completion(field_name='object')
    print("\n" + "="*50 + "\n")
    # 检查operation字段
    check_field_completion(field_name='operation') 