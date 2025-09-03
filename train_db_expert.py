#!/usr/bin/env python3
"""
数据库专家AI训练脚本
快速验证训练效果
"""

import json
import random
from sklearn.model_selection import train_test_split
from collections import Counter
import pandas as pd

def load_and_analyze_data(file_path):
    """加载并分析训练数据"""
    print("🔍 加载训练数据...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 总样本数: {len(data)}")
    
    # 统计任务类型分布
    task_types = [item['task_type'] for item in data]
    type_counts = Counter(task_types)
    
    print("\n📈 任务类型分布:")
    for task_type, count in type_counts.items():
        percentage = (count / len(data)) * 100
        print(f"  {task_type}: {count} ({percentage:.1f}%)")
    
    return data, type_counts

def prepare_training_data(data):
    """准备训练数据格式"""
    print("\n🛠️ 准备训练数据...")
    
    training_samples = []
    
    for item in data:
        # 提取对话内容
        messages = item['messages']
        task_type = item['task_type']
        
        # 构建训练样本
        sample = {
            'messages': messages,
            'task_type': task_type,
            'input': messages[-2]['content'] if len(messages) >= 2 else "",  # user message
            'output': messages[-1]['content'] if len(messages) >= 1 else "", # assistant message
        }
        
        training_samples.append(sample)
    
    return training_samples

def split_dataset(data, test_size=0.2, val_size=0.1):
    """划分数据集"""
    print(f"\n📂 划分数据集 (训练:{1-test_size-val_size:.0%}, 验证:{val_size:.0%}, 测试:{test_size:.0%})...")
    
    # 按任务类型分层抽样
    task_types = [item['task_type'] for item in data]
    
    # 先分出测试集
    train_val_data, test_data = train_test_split(
        data, test_size=test_size, stratify=task_types, random_state=42
    )
    
    # 再从训练集中分出验证集
    train_task_types = [item['task_type'] for item in train_val_data]
    val_ratio = val_size / (1 - test_size)
    
    train_data, val_data = train_test_split(
        train_val_data, test_size=val_ratio, stratify=train_task_types, random_state=42
    )
    
    print(f"  训练集: {len(train_data)} 样本")
    print(f"  验证集: {len(val_data)} 样本") 
    print(f"  测试集: {len(test_data)} 样本")
    
    return train_data, val_data, test_data

def save_datasets(train_data, val_data, test_data):
    """保存数据集"""
    print("\n💾 保存数据集...")
    
    datasets = {
        'train': train_data,
        'validation': val_data, 
        'test': test_data
    }
    
    for split_name, split_data in datasets.items():
        filename = f"db_expert_{split_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(split_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {filename}: {len(split_data)} 样本")

def analyze_data_balance(data):
    """分析数据平衡性"""
    print("\n⚖️ 数据平衡性分析:")
    
    task_counts = Counter([item['task_type'] for item in data])
    total = len(data)
    
    for task_type, count in task_counts.items():
        ratio = count / total
        status = "⚠️ 不平衡" if ratio < 0.15 else "✅ 平衡"
        print(f"  {task_type}: {count}/{total} ({ratio:.1%}) {status}")

def create_simple_baseline():
    """创建简单的基线模型用于对比"""
    print("\n🤖 创建基线模型...")
    
    baseline_code = '''
# 简单的基线模型 - 基于规则的回答
def baseline_model(question, task_type):
    """基于规则的简单基线模型"""
    
    if "关联" in question or "关系" in question:
        if task_type == "basic_relationship":
            return "通过外键字段关联，关系类型为多对一。"
        elif task_type == "negative_relationship":
            return "这两个表之间没有直接关联关系。"
    
    elif "查询" in question and "数量" in question:
        return "SQL查询:\\n```sql\\nSELECT COUNT(*) FROM table_name\\n```"
    
    return "需要更多信息来回答这个问题。"
'''
    
    with open('baseline_model.py', 'w', encoding='utf-8') as f:
        f.write(baseline_code)
    
    print("  ✅ 基线模型已保存到 baseline_model.py")

def main():
    """主函数"""
    print("🎯 数据库专家AI训练数据预处理")
    print("=" * 50)
    
    # 1. 加载数据
    data, type_counts = load_and_analyze_data('data/4table_training_data_messages_format.json')
    
    # 2. 分析数据平衡性
    analyze_data_balance(data)
    
    # 3. 准备训练数据
    training_samples = prepare_training_data(data)
    
    # 4. 划分数据集
    train_data, val_data, test_data = split_dataset(training_samples)
    
    # 5. 保存数据集
    save_datasets(train_data, val_data, test_data)
    
    # 6. 创建基线模型
    create_simple_baseline()
    
    print("\n🎉 数据预处理完成！")
    print("\n📋 下一步建议:")
    print("  1. 检查生成的数据集文件")
    print("  2. 选择训练框架 (transformers, openai fine-tuning, etc.)")
    print("  3. 开始小规模训练实验")
    print("  4. 评估模型效果并与基线对比")

if __name__ == "__main__":
    main()
