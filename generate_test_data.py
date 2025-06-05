#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据生成脚本，用于验证字段修改是否生效
"""

from src.service.staffing_service import generate_staffing_data
from src.service.cargo_update_service import generate_cargo_update_data
from verify_fields import verify_staff_operations, verify_cargo_fields
import os
import json
import time

def save_test_data(data, business_object):
    """保存测试数据到文件"""
    # 确保目录存在
    os.makedirs('outputs/data/original', exist_ok=True)
    
    # 创建文件名（格式与标准相同）
    timestamp = time.strftime("%Y%m%d%H%M%S")
    count = len(data)
    filename = f"outputs/data/original/{business_object}_{count}_{timestamp}.json"
    
    # 保存数据
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存{count}条数据到: {filename}")

# 主函数
if __name__ == "__main__":
    print("开始生成测试数据...")
    
    # 生成人员安排数据
    print("\n生成人员安排数据...")
    staff_data = generate_staffing_data(total_samples=8)
    save_test_data(staff_data, 'searchStaff')
    
    # 生成货单更新数据
    print("\n生成货单更新数据...")
    cargo_data = generate_cargo_update_data(total_samples=20)
    save_test_data(cargo_data, 'updateCargo')
    
    # 验证生成的数据
    print("\n验证生成的数据...")
    verify_staff_operations()
    verify_cargo_fields()
    
    print("\n测试完成") 