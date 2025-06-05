#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
qwen数据合并测试服务
用于清空生成数据、重新生成测试数据并合并所有qwen格式训练数据
"""

import os
import json
import glob
import shutil
import random
from datetime import datetime
from typing import List, Dict, Any

# 引入测试服务
from test.service.test_qwen_service import (
    test_generate_qwen_data_for_searchStaff,
    test_generate_qwen_data_for_updateStaff,
    test_generate_qwen_data_for_updateCargo,
    test_generate_qwen_data_for_searchContract
)

def clear_output_data():
    """
    清空outputs/data目录下的生成数据文件
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(root_dir, 'outputs', 'data')
    
    # 清空qwen目录
    qwen_dir = os.path.join(data_dir, 'qwen')
    if os.path.exists(qwen_dir):
        print(f"正在清空目录: {qwen_dir}")
        for file in glob.glob(os.path.join(qwen_dir, '*.jsonl')):
            os.remove(file)
            print(f"已删除文件: {file}")
    else:
        print(f"创建目录: {qwen_dir}")
        os.makedirs(qwen_dir, exist_ok=True)
    
    # 清空original目录
    original_dir = os.path.join(data_dir, 'original')
    if os.path.exists(original_dir):
        print(f"正在清空目录: {original_dir}")
        for file in glob.glob(os.path.join(original_dir, '*.json')):
            os.remove(file)
            print(f"已删除文件: {file}")
    else:
        print(f"创建目录: {original_dir}")
        os.makedirs(original_dir, exist_ok=True)
    
    print("数据目录清空完成！")

def generate_test_data():
    """
    生成测试数据
    """
    print("\n开始生成测试数据...")
    
    test_generate_qwen_data_for_searchStaff()
    test_generate_qwen_data_for_updateStaff()
    test_generate_qwen_data_for_updateCargo()
    test_generate_qwen_data_for_searchContract()
    
    print("测试数据生成完成！")

def find_qwen_data_files() -> List[str]:
    """
    查找所有生成的qwen数据文件
    
    Returns:
        qwen数据文件路径列表
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    qwen_dir = os.path.join(root_dir, 'outputs', 'data', 'qwen')
    
    # 查找所有jsonl文件
    files = glob.glob(os.path.join(qwen_dir, '*.jsonl'))
    
    print(f"找到 {len(files)} 个qwen数据文件:")
    for file in files:
        print(f"  - {os.path.basename(file)}")
    
    return files

def merge_qwen_data(files: List[str]) -> List[Dict]:
    """
    合并所有qwen数据文件
    
    Args:
        files: qwen数据文件路径列表
        
    Returns:
        合并后的数据列表
    """
    all_data = []
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            print(f"从文件 {os.path.basename(file)} 中读取 {len(lines)} 条数据")
            
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    all_data.append(data)
                except json.JSONDecodeError:
                    print(f"警告: 无法解析JSON行: {line[:50]}...")
    
    # 打乱数据
    random.shuffle(all_data)
    
    print(f"合并完成，共有 {len(all_data)} 条数据")
    
    return all_data

def save_merged_data(data: List[Dict]) -> str:
    """
    保存合并后的数据
    
    Args:
        data: 合并后的数据列表
        
    Returns:
        保存的文件路径
    """
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    qwen_dir = os.path.join(root_dir, 'outputs', 'data', 'qwen')
    
    # 生成文件名，包含数据条数和时间戳
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"merged_{len(data)}_{timestamp}.jsonl"
    filepath = os.path.join(qwen_dir, filename)
    
    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"合并数据已保存到: {filepath}")
    
    return filepath

def test_qwen_merge():
    """
    测试qwen数据合并功能
    """
    print("开始qwen数据合并测试...")
    
    # 1. 清空输出目录
    clear_output_data()
    
    # 2. 生成测试数据
    generate_test_data()
    
    # 3. 查找qwen数据文件
    files = find_qwen_data_files()
    
    if not files:
        print("未找到qwen数据文件，合并操作取消")
        return
    
    # 4. 合并数据
    merged_data = merge_qwen_data(files)
    
    # 5. 保存合并后的数据
    saved_file = save_merged_data(merged_data)
    
    print(f"\n合并测试完成！")
    print(f"共合并 {len(files)} 个文件，{len(merged_data)} 条数据")
    print(f"合并后的文件: {saved_file}")

if __name__ == "__main__":
    test_qwen_merge() 