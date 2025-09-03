#!/usr/bin/env python3
"""
简单的数据库专家AI训练脚本
使用 transformers 库进行快速实验
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from torch.utils.data import Dataset
import numpy as np
from sklearn.metrics import accuracy_score, classification_report

class DBExpertDataset(Dataset):
    """数据库专家数据集"""
    
    def __init__(self, data, tokenizer, max_length=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # 构建输入文本
        input_text = f"用户问题: {item['input']}\n回答: {item['output']}"
        
        # 编码
        encoding = self.tokenizer(
            input_text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()
        }

def load_data(file_path):
    """加载数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def setup_model_and_tokenizer(model_name="microsoft/DialoGPT-small"):
    """设置模型和分词器"""
    print(f"🤖 加载模型: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # 添加特殊token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer

def train_model():
    """训练模型"""
    print("🚀 开始训练数据库专家AI模型")
    print("=" * 50)
    
    # 1. 加载数据
    print("📂 加载数据集...")
    train_data = load_data('db_expert_train.json')
    val_data = load_data('db_expert_validation.json')
    
    print(f"  训练集: {len(train_data)} 样本")
    print(f"  验证集: {len(val_data)} 样本")
    
    # 2. 设置模型
    model, tokenizer = setup_model_and_tokenizer()
    
    # 3. 创建数据集
    print("🔄 准备数据集...")
    train_dataset = DBExpertDataset(train_data, tokenizer)
    val_dataset = DBExpertDataset(val_data, tokenizer)
    
    # 4. 设置训练参数
    training_args = TrainingArguments(
        output_dir='./db_expert_model',
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
    )
    
    # 5. 数据整理器
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # 6. 创建训练器
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )
    
    # 7. 开始训练
    print("🎯 开始训练...")
    trainer.train()
    
    # 8. 保存模型
    print("💾 保存模型...")
    trainer.save_model()
    tokenizer.save_pretrained('./db_expert_model')
    
    print("✅ 训练完成！")
    
    return model, tokenizer

def test_model(model, tokenizer):
    """测试模型"""
    print("\n🧪 测试模型效果...")
    
    # 加载测试数据
    test_data = load_data('db_expert_test.json')
    
    # 测试几个样本
    test_samples = test_data[:5]  # 取前5个样本测试
    
    for i, sample in enumerate(test_samples):
        print(f"\n--- 测试样本 {i+1} ---")
        print(f"问题: {sample['input']}")
        print(f"期望回答: {sample['output'][:100]}...")
        
        # 生成回答
        input_text = f"用户问题: {sample['input']}\n回答:"
        inputs = tokenizer.encode(input_text, return_tensors='pt')
        
        with torch.no_grad():
            outputs = model.generate(
                inputs, 
                max_length=inputs.shape[1] + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_answer = generated_text[len(input_text):].strip()
        
        print(f"模型回答: {generated_answer}")
        print("-" * 50)

def quick_evaluation():
    """快速评估"""
    print("\n📊 快速评估...")
    
    # 简单的评估指标
    test_data = load_data('db_expert_test.json')
    
    task_type_counts = {}
    for item in test_data:
        task_type = item['task_type']
        task_type_counts[task_type] = task_type_counts.get(task_type, 0) + 1
    
    print("测试集任务类型分布:")
    for task_type, count in task_type_counts.items():
        print(f"  {task_type}: {count}")

def main():
    """主函数"""
    try:
        # 检查是否有GPU
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️ 使用设备: {device}")
        
        # 训练模型
        model, tokenizer = train_model()
        
        # 测试模型
        test_model(model, tokenizer)
        
        # 快速评估
        quick_evaluation()
        
        print("\n🎉 实验完成！")
        print("\n📋 结果文件:")
        print("  - 模型: ./db_expert_model/")
        print("  - 日志: ./logs/")
        
    except Exception as e:
        print(f"❌ 训练过程中出现错误: {e}")
        print("💡 建议:")
        print("  1. 检查是否安装了所需依赖: pip install transformers torch")
        print("  2. 如果内存不足，可以减小batch_size")
        print("  3. 可以尝试更小的模型，如 'gpt2' 或 'distilgpt2'")

if __name__ == "__main__":
    main()
