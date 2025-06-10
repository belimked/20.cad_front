#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据生成脚本，用于验证字段修改是否生效
支持通过命令行参数指定规则ID过滤
"""

from src.service.staffing_service import generate_staffing_data
from src.service.cargo_update_service import generate_cargo_update_data
from verify_fields import verify_staff_operations, verify_cargo_fields
import os
import json
import time
import argparse

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

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成测试数据，支持规则ID过滤')
    
    parser.add_argument('-s', '--staff-samples', type=int, default=8,
                        help='人员安排数据样本数量，默认为8')
    parser.add_argument('-c', '--cargo-samples', type=int, default=20,
                        help='货单更新数据样本数量，默认为20')
    parser.add_argument('--staff-rules', type=str, default=None,
                        help='人员安排规则过滤，格式如"1,2,3"或"-1,-2,-3"')
    parser.add_argument('--cargo-rules', type=str, default=None,
                        help='货单更新规则过滤，格式如"1,2,3"或"-1,-2,-3"')
    parser.add_argument('--variations', type=int, default=2,
                        help='每条规则的变种数，默认为2')
    
    return parser.parse_args()

# 主函数
if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    print("开始生成测试数据...")
    print(f"配置: 人员样本数={args.staff_samples}, 货单样本数={args.cargo_samples}, "
          f"每规则变种数={args.variations}")
    if args.staff_rules:
        print(f"人员规则过滤: {args.staff_rules}")
    if args.cargo_rules:
        print(f"货单规则过滤: {args.cargo_rules}")
    
    # 生成人员安排数据
    print("\n生成人员安排数据...")
    staff_data = generate_staffing_data(
        total_samples=args.staff_samples,
        variations_per_rule=args.variations,
        ruleids=args.staff_rules
    )
    save_test_data(staff_data, 'searchStaff')
    
    # 生成货单更新数据
    print("\n生成货单更新数据...")
    cargo_data = generate_cargo_update_data(
        total_samples=args.cargo_samples,
        variations_per_rule=args.variations,
        ruleids=args.cargo_rules
    )
    save_test_data(cargo_data, 'updateCargo')
    
    # 验证生成的数据
    print("\n验证生成的数据...")
    verify_staff_operations()
    verify_cargo_fields()
    
    print("\n测试完成") 