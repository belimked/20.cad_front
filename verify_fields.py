#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import glob
import os
from collections import Counter

def verify_staff_operations():
    """验证人员安排的operation字段是否包含多种操作类型"""
    print("验证人员安排operation字段:")
    file_path = 'outputs/data/original/searchStaff_*_*.json'
    files = glob.glob(file_path)
    
    if files:
        # 获取最新的文件
        latest_file = max(files, key=os.path.getctime)
        print(f"\n文件: {latest_file}")
        
        with open(latest_file) as f:
            data = json.load(f)
        
        # 统计不同operation值的数量
        operations = [item['answer'].get('operation', '') for item in data if 'operation' in item['answer']]
        op_counter = Counter(operations)
        
        print(f"总数据量: {len(data)}条")
        print(f"operation字段数量: {len(operations)}条")
        print("\n各operation值分布:")
        for op, count in op_counter.items():
            print(f"  {op}: {count}条 ({count/len(data)*100:.2f}%)")
            
        # 检查是否包含四种预期的值
        expected_ops = {"查询", "对比", "审核通过", "导出结算单"}
        found_ops = set(op_counter.keys())
        missing_ops = expected_ops - found_ops
        
        if missing_ops:
            print(f"\n缺少以下operation类型: {', '.join(missing_ops)}")
        else:
            print("\n已包含所有预期的operation类型")
    else:
        print("未找到人员安排数据文件")

def verify_cargo_fields():
    """验证货单信息的project和supplier字段是否不为空"""
    print("\n验证货单信息的project和supplier字段:")
    file_path = 'outputs/data/original/updateCargo_*_*.json'
    files = glob.glob(file_path)
    
    if files:
        # 获取最新的文件
        latest_file = max(files, key=os.path.getctime)
        print(f"\n文件: {latest_file}")
        
        with open(latest_file) as f:
            data = json.load(f)
        
        total = len(data)
        project_count = 0
        supplier_count = 0
        
        # 统计非空字段数量
        for item in data:
            if item['answer'].get('project', ''):
                project_count += 1
            if item['answer'].get('supplier', ''):
                supplier_count += 1
        
        # 计算填充率
        project_rate = project_count/total*100 if total > 0 else 0
        supplier_rate = supplier_count/total*100 if total > 0 else 0
        
        print(f"总数据量: {total}条")
        print(f"project字段填充: {project_count}/{total} ({project_rate:.2f}%)")
        print(f"supplier字段填充: {supplier_count}/{total} ({supplier_rate:.2f}%)")
        
        # 显示示例值
        if data:
            print("\n示例数据:")
            print(f"  project值: {data[0]['answer'].get('project', '<空>')}")
            print(f"  supplier值: {data[0]['answer'].get('supplier', '<空>')}")
    else:
        print("未找到货单信息数据文件")

if __name__ == "__main__":
    # 验证人员安排的operation字段
    verify_staff_operations()
    
    # 验证货单信息的project和supplier字段
    verify_cargo_fields() 