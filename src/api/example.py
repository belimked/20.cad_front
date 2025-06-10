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
    parser.add_argument('--keyword', type=str, default=None,
                        help='关键字过滤，格式如"最近,月"')
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
        
    if args.keyword:
        params["keyword"] = args.keyword
    
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
            total_count = data['statistics']['total_count']
            
            print(f"请求成功! 生成了 {total_count} 条训练数据")
            print(f"数据已保存到:")
            print(f"- 对话数据: {data['files']['dialogs_file']}")
            print(f"- 原始数据: {data['files']['raw_file']}")
            
            # 打印数据分布
            print("\n规则分布:")
            for rule in data['statistics']['rule_distribution']:
                print(f"- 规则{rule['rule_id']} '{rule['rule_name']}': {rule['count']}条数据 ({(rule['count']/total_count*100):.1f}%)")
            
            # 打印示例数据
            if data['examples']:
                print("\n示例数据:")
                for i, example in enumerate(data['examples']):
                    user_content = example['messages'][0]['content']
                    assistant_content = example['messages'][1]['content']
                    print(f"\n示例 {i+1}:")
                    print(f"问题: {user_content}")
                    print(f"回答: {assistant_content}")
        else:
            print(f"请求失败! 状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main() 