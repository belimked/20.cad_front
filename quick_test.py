#!/usr/bin/env python3
"""
快速测试脚本 - 验证训练数据和基础功能
"""

import json
import os
from collections import Counter

def test_data_files():
    """测试数据文件是否正确生成"""
    print("🔍 测试数据文件...")
    
    required_files = [
        'db_expert_train.json',
        'db_expert_validation.json', 
        'db_expert_test.json'
    ]
    
    for file_name in required_files:
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✅ {file_name}: {len(data)} 样本")
            
            # 检查数据格式
            if data and isinstance(data[0], dict):
                sample = data[0]
                required_keys = ['messages', 'task_type', 'input', 'output']
                missing_keys = [key for key in required_keys if key not in sample]
                if missing_keys:
                    print(f"    ⚠️ 缺少字段: {missing_keys}")
                else:
                    print(f"    ✅ 数据格式正确")
        else:
            print(f"  ❌ {file_name}: 文件不存在")

def test_baseline_model():
    """测试基线模型"""
    print("\n🤖 测试基线模型...")
    
    if os.path.exists('baseline_model.py'):
        print("  ✅ baseline_model.py 存在")
        
        # 简单测试
        exec(open('baseline_model.py').read())
        
        # 测试几个问题
        test_cases = [
            ("mstb_project和mstb_project_materials的关系是什么？", "basic_relationship"),
            ("查询每个项目的材料数量", "sql_generation"),
            ("mstb_project和不存在的表有关系吗？", "negative_relationship")
        ]
        
        for question, task_type in test_cases:
            try:
                answer = baseline_model(question, task_type)
                print(f"    问题: {question[:30]}...")
                print(f"    回答: {answer[:50]}...")
                print()
            except:
                print(f"    ❌ 基线模型测试失败")
    else:
        print("  ❌ baseline_model.py 不存在")

def analyze_training_data():
    """分析训练数据的特征"""
    print("\n📊 分析训练数据特征...")
    
    try:
        with open('db_expert_train.json', 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        
        # 统计输入长度
        input_lengths = [len(item['input']) for item in train_data]
        output_lengths = [len(item['output']) for item in train_data]
        
        print(f"  输入文本长度: 平均 {sum(input_lengths)/len(input_lengths):.0f} 字符")
        print(f"  输出文本长度: 平均 {sum(output_lengths)/len(output_lengths):.0f} 字符")
        print(f"  最长输入: {max(input_lengths)} 字符")
        print(f"  最长输出: {max(output_lengths)} 字符")
        
        # 任务类型分布
        task_types = [item['task_type'] for item in train_data]
        type_counts = Counter(task_types)
        
        print("\n  训练集任务类型分布:")
        for task_type, count in type_counts.items():
            percentage = (count / len(train_data)) * 100
            print(f"    {task_type}: {count} ({percentage:.1f}%)")
            
    except Exception as e:
        print(f"  ❌ 分析失败: {e}")

def check_dependencies():
    """检查训练依赖"""
    print("\n📦 检查训练依赖...")
    
    required_packages = [
        'torch',
        'transformers', 
        'sklearn',
        'pandas',
        'numpy'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - 需要安装")

def estimate_training_time():
    """估算训练时间"""
    print("\n⏱️ 估算训练时间...")
    
    try:
        with open('db_expert_train.json', 'r', encoding='utf-8') as f:
            train_data = json.load(f)
        
        num_samples = len(train_data)
        epochs = 3
        batch_size = 4
        
        steps_per_epoch = num_samples // batch_size
        total_steps = steps_per_epoch * epochs
        
        print(f"  训练样本: {num_samples}")
        print(f"  训练轮数: {epochs}")
        print(f"  批次大小: {batch_size}")
        print(f"  总训练步数: {total_steps}")
        print(f"  预估时间: {total_steps * 2 // 60} 分钟 (CPU)")
        print(f"  预估时间: {total_steps * 0.5 // 60} 分钟 (GPU)")
        
    except Exception as e:
        print(f"  ❌ 估算失败: {e}")

def main():
    """主函数"""
    print("🧪 数据库专家AI训练 - 快速测试")
    print("=" * 50)
    
    # 1. 测试数据文件
    test_data_files()
    
    # 2. 测试基线模型
    test_baseline_model()
    
    # 3. 分析训练数据
    analyze_training_data()
    
    # 4. 检查依赖
    check_dependencies()
    
    # 5. 估算训练时间
    estimate_training_time()
    
    print("\n🎯 测试完成！")
    print("\n📋 下一步建议:")
    print("  1. 如果所有测试通过，可以开始训练")
    print("  2. 运行: python simple_trainer.py")
    print("  3. 监控训练过程和损失变化")
    print("  4. 训练完成后测试模型效果")

if __name__ == "__main__":
    main()
