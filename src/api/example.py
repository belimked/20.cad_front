#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成API调用示例
"""

import requests
import json
import argparse
from datetime import datetime

def save_to_jsonl(data, filename):
    """将数据保存为JSONL格式"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"数据已保存到: {filename}")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='训练数据生成API调用示例')
    parser.add_argument('--business', type=str, default='searchStaff', 
                        help='业务对象代码，如searchStaff、updateCargo等')
    parser.add_argument('--samples', type=int, default=10, 
                        help='生成的样本数量')
    parser.add_argument('--variations', type=int, default=2, 
                        help='每个规则的变种数量')
    parser.add_argument('--ruleids', type=str, default=None, 
                        help='规则ID过滤，格式如"1,2,3"')
    parser.add_argument('--host', type=str, default='http://localhost:8000', 
                        help='API服务地址')
    args = parser.parse_args()
    
    # 构建请求参数
    params = {
        "business_object": args.business,
        "total_samples": args.samples,
        "variations_per_rule": args.variations
    }
    
    if args.ruleids:
        params["ruleids"] = args.ruleids
    
    print(f"正在请求API生成{args.business}的训练数据...")
    print(f"参数: {params}")
    
    try:
        # 发送请求
        response = requests.post(
            f"{args.host}/api/generate-data",
            params=params
        )
        
        # 检查响应
        if response.status_code == 200:
            data = response.json()
            print(f"请求成功! 生成了 {len(data['data']['dialogs'])} 条训练数据")
            
            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dialogs_file = f"{args.business}_dialogs_{timestamp}.jsonl"
            raw_file = f"{args.business}_raw_{timestamp}.jsonl"
            
            save_to_jsonl(data['data']['dialogs'], dialogs_file)
            save_to_jsonl(data['data']['raw_data'], raw_file)
        else:
            print(f"请求失败! 状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main() 