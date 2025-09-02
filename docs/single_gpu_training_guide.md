# RTX 4090单卡训练脚本使用指南

## 🎯 概述

`start_single_gpu_training.sh` 是基于原始分布式训练脚本改造的单卡训练专用版本，专门优化了单卡训练性能和易用性。

## 🚀 主要特性

### ✅ 单卡优化
- **自动设置 `CUDA_VISIBLE_DEVICES=0`** - 只使用第一张GPU
- **禁用分布式训练** - 移除torchrun依赖
- **优化内存使用** - 针对单卡场景调整参数

### ✅ 简化使用
- **保持原有参数兼容性** - 与分布式版本参数一致
- **智能默认值** - 针对单卡训练优化的默认参数
- **完整的帮助信息** - 详细的参数说明

### ✅ 增强功能
- **后台运行支持** - 支持 `--background` 参数
- **测试模式** - 快速验证训练流程
- **完整的日志记录** - 便于调试和监控

## 📋 基础用法

### 最简单的使用方式
```bash
./tasks/start_single_gpu_training.sh data.jsonl
```

### 指定基本参数
```bash
./tasks/start_single_gpu_training.sh data.jsonl \
  --epochs 4 \
  --batch-size 8 \
  --learning-rate 1e-4
```

### 启用评估和早停
```bash
./tasks/start_single_gpu_training.sh data.jsonl \
  --enable-evaluation \
  --enable-early-stopping \
  --early-stopping-patience 3
```

### 后台运行
```bash
./tasks/start_single_gpu_training.sh data.jsonl \
  --background \
  --enable-wechat \
  --enable-swanlab
```

## 🎯 针对附加费用解析的推荐配置

基于你的成功经验，推荐使用以下配置：

```bash
./tasks/start_single_gpu_training.sh \
  /Users/saul/IdeaProjects/100.AI.Train.Data/100.AI.TrainData/outputs/data/additional_fee_training_data.jsonl \
  --model-path /root/lanyun-tmp/modelscope_cache/qwen/Qwen2.5-3B \
  --learning-rate 1e-4 \
  --output-dir ./outputs/additional_fee_parser_single_gpu_$(date +"%Y%m%d_%H%M%S") \
  --epochs 4 \
  --batch-size 8 \
  --gradient-accumulation-steps 2 \
  --enable-evaluation \
  --eval-split-ratio 0.2 \
  --eval-steps 50 \
  --enable-early-stopping \
  --early-stopping-patience 3 \
  --early-stopping-threshold 0.001 \
  --enable-wechat \
  --enable-swanlab \
  --swanlab-project 'qwen2.5-3b-additional-fee-parser-single-gpu' \
  --background
```

## 📊 参数对比：单卡 vs 双卡

| 参数 | 双卡分布式 | 单卡训练 | 说明 |
|------|------------|----------|------|
| 启动方式 | `torchrun --nproc_per_node=2` | `python` | 单卡不需要torchrun |
| GPU设置 | `CUDA_VISIBLE_DEVICES=0,1` | `CUDA_VISIBLE_DEVICES=0` | 只使用第一张GPU |
| 批次大小 | 8 (每卡) | 8 | 保持一致 |
| 梯度累积 | 2 | 2 | 保持一致 |
| 有效批次 | 8×2×2=32 | 8×2=16 | 单卡有效批次更小 |
| 训练速度 | 更快 | 较慢 | 但更稳定 |
| 内存使用 | 双卡分担 | 单卡承担 | 需要注意内存限制 |

## ⚡ 性能优化建议

### 单卡训练优化
1. **适当增加梯度累积** - 补偿单卡的批次大小劣势
2. **使用fp16混合精度** - 节省显存和提升速度
3. **合理设置保存频率** - 避免频繁IO影响性能

### 推荐配置
```bash
# 高性能配置（24GB显存）
--batch-size 16 \
--gradient-accumulation-steps 2 \
--fp16

# 节省显存配置（显存不足时）
--batch-size 4 \
--gradient-accumulation-steps 8 \
--fp16
```

## 🔧 故障排除

### 常见问题

1. **显存不足**
   ```bash
   # 解决方案：减少批次大小，增加梯度累积
   --batch-size 4 --gradient-accumulation-steps 8
   ```

2. **训练速度慢**
   ```bash
   # 解决方案：启用混合精度，优化数据加载
   --fp16 --dataloader_num_workers 4
   ```

3. **模型不收敛**
   ```bash
   # 解决方案：检查学习率，启用评估监控
   --learning-rate 1e-4 --enable-evaluation --eval-steps 50
   ```

### 监控训练进度

```bash
# 查看训练日志
tail -f ./logs/single_gpu_training_TIMESTAMP.log

# 检查GPU使用情况
nvidia-smi

# 查看进程状态
ps aux | grep python
```

## 📝 训练完成后的步骤

1. **复制模型到vLLM目录**
   ```bash
   cp -r ./outputs/additional_fee_parser_single_gpu_* /root/lanyun-tmp/train/new/25out/
   ```

2. **重启vLLM服务**
   ```bash
   ./tasks/start_vllm_optimized_clean.sh restart
   ```

3. **测试新模型**
   ```bash
   curl -X POST 'http://localhost:8000/v1/completions' \
     -H 'Content-Type: application/json' \
     -d '{
       "model": "additional_fee_parser_single_gpu_TIMESTAMP",
       "prompt": "列出附加费用大于0的货单结算审核单",
       "max_tokens": 300,
       "temperature": 0.1
     }'
   ```

## 🎯 与分布式版本的选择建议

### 使用单卡训练的场景
- ✅ **调试和实验** - 更容易调试和监控
- ✅ **小数据集** - 500条以下的数据集
- ✅ **稳定性优先** - 避免分布式训练的复杂性
- ✅ **资源限制** - 只有一张GPU可用

### 使用分布式训练的场景
- ✅ **大数据集** - 1000条以上的数据集
- ✅ **速度优先** - 需要快速完成训练
- ✅ **资源充足** - 有多张GPU可用
- ✅ **生产环境** - 需要最大化硬件利用率

## 💡 最佳实践

1. **先用单卡验证** - 确保训练流程正确
2. **再用分布式加速** - 在确认无误后提升速度
3. **监控资源使用** - 避免资源浪费
4. **定期保存检查点** - 防止训练中断导致的损失

---

**作者**: Claude 4.0 sonnet  
**版本**: v1.0  
**更新时间**: 2025-09-01
