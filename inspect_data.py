#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

def main():
    # 找到最新生成的searchContract数据文件
    root_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(root_dir, 'outputs', 'data', 'original')
    
    search_contract_files = [f for f in os.listdir(output_dir) if f.startswith('searchContract_') and f.endswith('.json')]
    if not search_contract_files:
        print("未找到searchContract数据文件")
        return
    
    # 按时间戳排序，获取最新的文件
    latest_file = sorted(search_contract_files)[-1]
    file_path = os.path.join(output_dir, latest_file)
    
    print(f"分析文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查supplier字段
    supplier_fields = [item.get('answer', {}).get('supplier', '') for item in data]
    non_empty_supplier_count = sum(1 for s in supplier_fields if s)
    
    print(f"总数据条数: {len(data)}")
    print(f"非空supplier字段数: {non_empty_supplier_count}")
    print(f"空supplier字段数: {len(data) - non_empty_supplier_count}")
    
    # 检查supplierInfo字段
    supplier_info_fields = [item.get('question', {}).get('supplierInfo', '') for item in data]
    has_supplier_info_count = sum(1 for s in supplier_info_fields if s)
    
    print(f"\nsupplierInfo字段存在的数据条数: {has_supplier_info_count}")
    
    # 打印带有supplierInfo的样例
    if has_supplier_info_count > 0:
        for i, item in enumerate(data):
            if item.get('question', {}).get('supplierInfo', ''):
                print("\n样例数据:")
                print(f"问题: {item['question']}")
                print(f"回答: {item['answer']}")
                print(f"supplierInfo: {item['question'].get('supplierInfo', '')}")
                print(f"supplier: {item['answer'].get('supplier', '')}")
                break

if __name__ == "__main__":
    main() 