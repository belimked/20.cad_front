# Swift 部署与使用指南

## 📋 概述

本文档记录了在服务器上部署和使用 Swift 的完整流程，包括环境配置、模型部署、API调用等关键信息。

## 🚀 服务器环境配置

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+
- **Python**: 3.8+
- **CUDA**: 11.8+ (GPU推理)
- **内存**: 16GB+ (推荐32GB+)
- **显存**: 8GB+ (推荐24GB+)

### Swift 安装

#### 方法1: 使用 pip 安装
```bash
# 安装基础版本
pip install ms-swift[llm]

# 安装完整版本（包含所有依赖）
pip install ms-swift[llm,eval,train]
```

#### 方法2: 从源码安装
```bash
git clone https://github.com/modelscope/swift.git
cd swift
pip install -e .
```

## 🔧 模型部署配置

### 1. 模型下载与配置

#### 下载 Qwen2.5 模型
```bash
# 使用 modelscope 下载
python -c "
from modelscope import snapshot_download
model_dir = snapshot_download('qwen/Qwen2.5-3B-Instruct', cache_dir='./models')
print(f'Model downloaded to: {model_dir}')
"
```

#### 配置模型路径
```bash
export MODEL_PATH="/path/to/models/qwen/Qwen2___5-3B-Instruct"
export SWIFT_UI_LANG=zh
```

### 2. LoRA 微调模型部署

#### 部署微调后的模型
```bash
# 部署 LoRA 微调模型
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --adapters_id_or_path ./outputs/4table_training_20250903_105534 \
    --port 8000 \
    --host 0.0.0.0
```

#### 部署合并后的模型
```bash
# 如果已经合并了 LoRA 权重
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path ./merged_model \
    --port 8000 \
    --host 0.0.0.0
```

## 🌐 API 服务配置

### 启动 OpenAI 兼容 API 服务

```bash
# 基础启动
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --port 8000 \
    --api_mode openai

# 高级配置启动
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --adapters_id_or_path ./outputs/4table_training_20250903_105534 \
    --port 8000 \
    --host 0.0.0.0 \
    --api_mode openai \
    --max_length 2048 \
    --temperature 0.1 \
    --top_p 0.8 \
    --repetition_penalty 1.1
```

### 服务健康检查

```bash
# 检查服务状态
curl http://localhost:8000/v1/models

# 测试聊天接口
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2_5-3b-instruct",
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "max_tokens": 100
  }'
```

## 🔄 模型训练流程

### 1. 数据准备

#### 训练数据格式
```json
{
  "messages": [
    {
      "role": "system",
      "content": "你是一个数据库专家，负责分析表关系、生成SQL查询和ERD设计。"
    },
    {
      "role": "user",
      "content": "数据库结构:\n表 mstb_project:\n  - pro_id (int, 主键)\n\n问题: 主键的作用是什么？"
    },
    {
      "role": "assistant",
      "content": "主键用于唯一标识表中的每一行记录。"
    }
  ]
}
```

### 2. 启动训练

```bash
# LoRA 微调
swift sft \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --dataset ./data/4table_training_data_fixed.json \
    --train_dataset_sample -1 \
    --num_train_epochs 3 \
    --max_length 1024 \
    --check_dataset_strategy warning \
    --lora_rank 16 \
    --lora_alpha 32 \
    --lora_dropout_p 0.1 \
    --lora_target_modules ALL \
    --gradient_checkpointing true \
    --batch_size 2 \
    --weight_decay 0.01 \
    --learning_rate 1e-4 \
    --gradient_accumulation_steps 4 \
    --max_grad_norm 0.5 \
    --warmup_ratio 0.1 \
    --eval_steps 30 \
    --save_steps 50 \
    --save_total_limit 3 \
    --logging_steps 10 \
    --use_flash_attn true
```

### 3. 模型合并

```bash
# 合并 LoRA 权重到基础模型
swift export \
    --ckpt_dir ./outputs/qwen2_5-3b-instruct/vx-xxx/checkpoint-xxx \
    --merge_lora true
```

## 📊 监控与日志

### 服务监控

```bash
# 查看 GPU 使用情况
nvidia-smi

# 查看进程状态
ps aux | grep swift

# 查看端口占用
netstat -tlnp | grep 8000
```

### 日志管理

```bash
# 启动时保存日志
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --port 8000 \
    > swift_deploy.log 2>&1 &

# 实时查看日志
tail -f swift_deploy.log
```

## 🔧 常见问题与解决方案

### 1. 内存不足
```bash
# 启用模型量化
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --quant_bits 4 \
    --port 8000
```

### 2. 显存不足
```bash
# 启用 CPU 推理
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --device_map cpu \
    --port 8000
```

### 3. 服务重启
```bash
# 停止服务
pkill -f "swift deploy"

# 重启服务
./scripts/restart_swift_service.sh
```

## 📝 配置文件示例

### swift_config.yaml
```yaml
model_type: qwen2_5-3b-instruct
model_id_or_path: /path/to/models/qwen/Qwen2___5-3B-Instruct
adapters_id_or_path: ./outputs/4table_training_20250903_105534
port: 8000
host: 0.0.0.0
api_mode: openai
max_length: 2048
temperature: 0.1
top_p: 0.8
repetition_penalty: 1.1
use_flash_attn: true
```

### 使用配置文件启动
```bash
swift deploy --config swift_config.yaml
```

## 🚀 性能优化建议

1. **使用 Flash Attention**: `--use_flash_attn true`
2. **启用梯度检查点**: `--gradient_checkpointing true`
3. **合理设置批次大小**: 根据显存调整 `batch_size`
4. **使用混合精度**: `--fp16 true` 或 `--bf16 true`
5. **模型量化**: `--quant_bits 4` 或 `--quant_bits 8`

## 📞 技术支持

- **官方文档**: https://swift.readthedocs.io/
- **GitHub**: https://github.com/modelscope/swift
- **社区论坛**: https://modelscope.cn/community
