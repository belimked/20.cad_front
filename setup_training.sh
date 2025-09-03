#!/bin/bash

echo "🚀 设置数据库专家AI训练环境"
echo "================================"

# 检查Python版本
echo "🐍 检查Python版本..."
python3 --version

# 创建虚拟环境（可选）
echo "📦 创建虚拟环境..."
python3 -m venv db_expert_env
source db_expert_env/bin/activate

# 安装依赖
echo "📥 安装训练依赖..."
pip install --upgrade pip

# 核心依赖
pip install torch torchvision torchaudio
pip install transformers
pip install datasets
pip install scikit-learn
pip install pandas
pip install numpy

# 可选依赖（用于更好的训练体验）
pip install wandb  # 训练监控
pip install tensorboard  # 可视化
pip install accelerate  # 加速训练

echo "✅ 环境设置完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 激活虚拟环境: source db_expert_env/bin/activate"
echo "2. 运行数据预处理: python train_db_expert.py"
echo "3. 开始训练: python simple_trainer.py"
echo ""
echo "💡 提示:"
echo "- 如果没有GPU，训练会比较慢，但仍然可以运行"
echo "- 可以调整 simple_trainer.py 中的参数来适应你的硬件"
echo "- 建议先用小数据集测试，确认流程正常"
