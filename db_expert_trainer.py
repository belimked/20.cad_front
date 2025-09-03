#!/usr/bin/env python3
"""
数据库专家AI训练脚本 - 基于现有训练框架优化
适配 4table_training_data_messages_format.json 数据格式
作者：Claude 4.0 sonnet
"""

import os
import json
import argparse
import datetime
from pathlib import Path

def check_dependencies():
    """检查训练依赖"""
    missing_deps = []
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError:
        missing_deps.append("torch")
    
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        missing_deps.append("transformers")
    
    try:
        from peft import LoraConfig
        print("✅ PEFT (LoRA)")
    except ImportError:
        missing_deps.append("peft")
    
    try:
        from datasets import Dataset
        print("✅ Datasets")
    except ImportError:
        missing_deps.append("datasets")
    
    if missing_deps:
        print(f"\n❌ 缺少依赖: {', '.join(missing_deps)}")
        print("\n📦 安装命令:")
        print("pip install torch transformers peft datasets accelerate")
        return False
    
    return True

def validate_data_format(data_path):
    """验证数据格式"""
    print(f"🔍 验证数据格式: {data_path}")
    
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        return False
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("❌ 数据格式错误：应为JSON数组")
            return False
        
        if len(data) == 0:
            print("❌ 数据为空")
            return False
        
        # 检查第一个样本的格式
        sample = data[0]
        required_keys = ['messages', 'task_type']
        
        for key in required_keys:
            if key not in sample:
                print(f"❌ 缺少必要字段: {key}")
                return False
        
        # 检查messages格式
        messages = sample['messages']
        if not isinstance(messages, list) or len(messages) < 2:
            print("❌ messages格式错误")
            return False
        
        # 检查消息结构
        for msg in messages:
            if 'role' not in msg or 'content' not in msg:
                print("❌ 消息缺少role或content字段")
                return False
        
        print(f"✅ 数据格式验证通过")
        print(f"📊 总样本数: {len(data)}")
        
        # 统计任务类型
        task_types = {}
        for item in data:
            task_type = item.get('task_type', 'unknown')
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        print("📈 任务类型分布:")
        for task_type, count in task_types.items():
            percentage = (count / len(data)) * 100
            print(f"  {task_type}: {count} ({percentage:.1f}%)")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def create_training_command(args):
    """创建训练命令"""
    
    # 基础命令
    cmd = f"python examples/first_time_training.py"
    
    # 必需参数
    cmd += f" --data_path {args.data_path}"
    
    # 可选参数
    if args.model_path:
        cmd += f" --model_path {args.model_path}"
    
    if args.output_dir:
        cmd += f" --output_dir {args.output_dir}"
    else:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        cmd += f" --output_dir ./outputs/db_expert_training_{timestamp}"
    
    cmd += f" --num_epochs {args.epochs}"
    
    # 训练优化参数
    if args.test_mode:
        cmd += " --test_mode"
    
    if args.enable_evaluation:
        cmd += " --enable_evaluation"
        cmd += f" --eval_split_ratio {args.eval_split_ratio}"
        cmd += f" --eval_steps {args.eval_steps}"
    
    if args.enable_early_stopping:
        cmd += " --enable_early_stopping"
        cmd += f" --early_stopping_patience {args.early_stopping_patience}"
        cmd += f" --early_stopping_threshold {args.early_stopping_threshold}"
        cmd += f" --early_stopping_metric {args.early_stopping_metric}"
    
    # 硬件优化
    if args.batch_size:
        cmd += f" --per_device_train_batch_size {args.batch_size}"
    
    if args.learning_rate:
        cmd += f" --learning_rate {args.learning_rate}"
    
    if args.gradient_accumulation_steps:
        cmd += f" --gradient_accumulation_steps {args.gradient_accumulation_steps}"
    
    # LoRA参数
    if args.lora_r:
        cmd += f" --lora_r {args.lora_r}"
    
    if args.lora_alpha:
        cmd += f" --lora_alpha {args.lora_alpha}"
    
    # 其他选项
    if args.skip_gpu_check:
        cmd += " --skip_gpu_check"
    
    if args.enable_wechat:
        cmd += " --enable_wechat"
    
    return cmd

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库专家AI训练脚本")
    
    # 必需参数
    parser.add_argument("--data_path", type=str, required=True,
                        help="训练数据文件路径")
    
    # 模型参数
    parser.add_argument("--model_path", type=str,
                        default="microsoft/DialoGPT-small",
                        help="预训练模型路径")
    
    parser.add_argument("--output_dir", type=str,
                        help="输出目录")
    
    parser.add_argument("--epochs", type=int, default=3,
                        help="训练轮数")
    
    # 训练参数
    parser.add_argument("--batch_size", type=int, default=2,
                        help="批次大小")
    
    parser.add_argument("--learning_rate", type=float, default=5e-6,
                        help="学习率")
    
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8,
                        help="梯度累积步数")
    
    # LoRA参数
    parser.add_argument("--lora_r", type=int, default=16,
                        help="LoRA rank")
    
    parser.add_argument("--lora_alpha", type=int, default=16,
                        help="LoRA alpha")
    
    # 评估参数
    parser.add_argument("--enable_evaluation", action="store_true",
                        help="启用评估")
    
    parser.add_argument("--eval_split_ratio", type=float, default=0.1,
                        help="评估数据比例")
    
    parser.add_argument("--eval_steps", type=int, default=100,
                        help="评估间隔步数")
    
    # 早停参数
    parser.add_argument("--enable_early_stopping", action="store_true",
                        help="启用早停")
    
    parser.add_argument("--early_stopping_patience", type=int, default=3,
                        help="早停耐心值")
    
    parser.add_argument("--early_stopping_threshold", type=float, default=0.0001,
                        help="早停阈值")
    
    parser.add_argument("--early_stopping_metric", type=str, default="dual_loss",
                        help="早停监控指标")
    
    # 其他选项
    parser.add_argument("--test_mode", action="store_true",
                        help="测试模式")
    
    parser.add_argument("--skip_gpu_check", action="store_true",
                        help="跳过GPU检查")
    
    parser.add_argument("--enable_wechat", action="store_true",
                        help="启用微信通知")
    
    parser.add_argument("--dry_run", action="store_true",
                        help="只显示命令，不执行")
    
    args = parser.parse_args()
    
    print("🎯 数据库专家AI训练脚本")
    print("=" * 50)
    
    # 1. 检查依赖
    print("📦 检查训练依赖...")
    if not check_dependencies():
        print("\n💡 请先安装依赖，然后重新运行")
        return
    
    # 2. 验证数据格式
    if not validate_data_format(args.data_path):
        print("\n❌ 数据验证失败")
        return
    
    # 3. 创建训练命令
    print("\n🚀 准备训练命令...")
    cmd = create_training_command(args)
    
    print(f"\n📋 训练命令:")
    print(cmd)
    
    if args.dry_run:
        print("\n🔍 干运行模式，不执行训练")
        return
    
    # 4. 确认执行
    print(f"\n⚠️ 即将开始训练，配置如下:")
    print(f"  数据文件: {args.data_path}")
    print(f"  模型: {args.model_path}")
    print(f"  训练轮数: {args.epochs}")
    print(f"  测试模式: {args.test_mode}")
    print(f"  启用评估: {args.enable_evaluation}")
    print(f"  启用早停: {args.enable_early_stopping}")
    
    confirm = input("\n是否开始训练? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ 训练已取消")
        return
    
    # 5. 执行训练
    print("\n🚀 开始训练...")
    print("=" * 50)
    
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print("\n✅ 训练完成！")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 训练失败: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ 训练被用户中断")

if __name__ == "__main__":
    main()
