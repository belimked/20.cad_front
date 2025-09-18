# 本地Swift使用说明

## 📋 概述

本文档记录了在本地和服务器上使用Swift的完整流程，包括所有必要的命令和配置。

## 🚀 快速开始

### 1. 本地环境设置

```bash
# 克隆项目
git clone http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git
cd 100.AI.TrainData

# 安装Swift
pip install ms-swift[llm]

# 快速启动
./quick_start_swift.sh
```

### 2. 服务器部署

#### 环境准备
```bash
# 安装依赖
pip install ms-swift[llm,eval,train]

# 设置环境变量
export MODEL_PATH="/root/lanyun-tmp/modelscope_cache/qwen/Qwen2___5-3B"
export ADAPTER_PATH="./outputs/4table_training_20250903_105534"
```

#### 启动服务
```bash
# 使用管理脚本（推荐）
./scripts/swift_manager.sh start

# 或手动启动
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --adapters_id_or_path $ADAPTER_PATH \
    --port 8000 \
    --host 0.0.0.0 \
    --api_mode openai
```

## 🔧 管理命令

### Swift服务管理
```bash
# 启动服务
./scripts/swift_manager.sh start

# 停止服务
./scripts/swift_manager.sh stop

# 重启服务
./scripts/swift_manager.sh restart

# 查看状态
./scripts/swift_manager.sh status

# 测试服务
./scripts/swift_manager.sh test

# 查看日志
./scripts/swift_manager.sh logs

# 清理日志
./scripts/swift_manager.sh clean-logs

# 检查环境
./scripts/swift_manager.sh check
```

### Git管理
```bash
# 推送Swift相关信息
./scripts/git_push_swift.sh

# 使用自定义提交信息
./scripts/git_push_swift.sh -m "更新Swift配置"

# 推送到指定分支
./scripts/git_push_swift.sh -b develop

# 只提交不推送
./scripts/git_push_swift.sh -n

# 强制推送
./scripts/git_push_swift.sh -f
```

## 🧪 API测试

### 基础测试
```bash
# 检查模型列表
curl http://localhost:8000/v1/models

# 简单聊天测试
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2_5-3b-instruct",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100
  }'
```

### ERD专业测试
```bash
# 基础关系查询
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2_5-3b-instruct",
    "messages": [
      {
        "role": "system",
        "content": "你是一个数据库专家，负责分析表关系、生成SQL查询和ERD设计。请提供简洁、准确的答案。"
      },
      {
        "role": "user", 
        "content": "mstb_project_materials通过什么字段与mstb_project关联？"
      }
    ],
    "max_tokens": 30,
    "temperature": 0.1
  }'

# SQL生成测试
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2_5-3b-instruct",
    "messages": [
      {
        "role": "user", 
        "content": "生成SQL：查询项目ID为1的所有材料名称"
      }
    ],
    "max_tokens": 50,
    "temperature": 0.1
  }'
```

## 📊 训练记录

### 最新训练结果
- **模型**: Qwen2.5-3B + LoRA微调
- **训练时间**: 2025-09-03 10:55-11:42 (46分钟)
- **最终验证损失**: 0.934226
- **训练步数**: 620步
- **数据集**: 549条ERD问答数据

### 训练配置
```yaml
model_type: qwen2_5-3b-instruct
learning_rate: 1e-6
num_train_epochs: 20
batch_size: 2
gradient_accumulation_steps: 4
lora_rank: 16
lora_alpha: 16
lora_dropout: 0.1
max_length: 1024
```

### 性能指标
- **收敛质量**: 稳定收敛，无过拟合
- **改善幅度**: 从1.008降到0.934，改善7.3%
- **训练稳定性**: 优秀，连续多次改善

## 🔍 验证结果

### 自动验证
```bash
# 运行全面验证
python3 comprehensive_verification.py

# 运行快速验证
python3 quick_manual_verification.py

# 运行真实数据验证
python3 vllm_erd_verification.py
```

### 手动验证要点
1. **简洁性**: 回答是否简洁明了
2. **准确性**: 关键信息是否正确
3. **一致性**: 回答风格是否一致
4. **专业性**: 是否符合ERD专业要求

## 🛠️ 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查进程
ps aux | grep swift

# 查看详细日志
./scripts/swift_manager.sh logs
```

#### 2. 内存不足
```bash
# 启用模型量化
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --quant_bits 4 \
    --port 8000
```

#### 3. 显存不足
```bash
# 使用CPU推理
swift deploy \
    --model_type qwen2_5-3b-instruct \
    --model_id_or_path $MODEL_PATH \
    --device_map cpu \
    --port 8000
```

### 日志位置
- **服务日志**: `logs/swift_service.log`
- **PID文件**: `logs/swift_service.pid`
- **Git日志**: 通过 `git log` 查看

## 📁 文件结构

```
100.AI.TrainData/
├── docs/
│   ├── swift-deployment-guide.md    # Swift部署指南
│   └── training-logs.md             # 训练日志记录
├── scripts/
│   ├── swift_manager.sh             # Swift服务管理脚本
│   └── git_push_swift.sh            # Git推送脚本
├── outputs/
│   └── 4table_training_20250903_105534/  # 训练好的LoRA模型
├── logs/                            # 日志目录
├── quick_start_swift.sh             # 快速启动脚本
├── comprehensive_verification.py    # 全面验证脚本
├── vllm_erd_verification.py        # vLLM验证脚本
└── LOCAL_SWIFT_USAGE.md            # 本文档
```

## 🔗 相关链接

- **项目仓库**: http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git
- **Swift官方文档**: https://swift.readthedocs.io/
- **ModelScope**: https://modelscope.cn/
- **Qwen2.5模型**: https://modelscope.cn/models/qwen/Qwen2.5-3B-Instruct

## 📞 技术支持

如有问题，请：
1. 查看日志文件
2. 运行环境检查: `./scripts/swift_manager.sh check`
3. 查看文档: `docs/swift-deployment-guide.md`
4. 检查Git提交记录: `git log --oneline`

---

**最后更新**: 2025-09-03 18:11:19  
**版本**: 1.0  
**作者**: Claude 4.0 sonnet 🐾
