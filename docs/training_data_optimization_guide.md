# 训练数据优化指南

## 📋 功能概述

意图分析训练数据优化器是智能问题精简系统的扩展功能，专门用于优化已有的训练数据文件。它可以：

- 🔧 **问题精简**: 使用已开发的问题缩减策略对用户问题进行智能缩减
- 🎯 **意图分析提取**: 从原始回答中提取关键信息作为意图分析对象
- 📈 **质量评估**: 提供详细的优化效果统计和质量评分
- 📁 **格式保持**: 保持原有的JSONL格式，确保兼容性

## 🚀 快速开始

### 1. Python模块直接使用

```python
from src.service.data_processing.intent_analysis_optimizer import IntentAnalysisOptimizer

# 创建意图分析优化器
optimizer = IntentAnalysisOptimizer()

# 优化训练数据
result = optimizer.optimize_training_data(
    input_file='outputs/data/qwen_data_20250808_163531.jsonl',
    reduction_level='advanced'
)

print(f"优化完成！输出文件: {result['output_file']}")
```

### 2. 命令行使用

```bash
# 基础使用
python src/service/data_processing/intent_analysis_optimizer.py \
  outputs/data/qwen_data_20250808_163531.jsonl

# 指定输出文件和缩减级别
python src/service/data_processing/intent_analysis_optimizer.py \
  outputs/data/qwen_data_20250808_163531.jsonl \
  -o outputs/data/intent_optimized_data.jsonl \
  -l aggressive
```

### 3. API接口调用

```bash
curl -X POST "http://localhost:8000/api/evaluation/optimize-training-data" \
  -H "Content-Type: application/json" \
  -d '{
    "input_file_path": "outputs/data/qwen_data_20250808_163531.jsonl",
    "reduction_level": "advanced",
    "enable_question_reduction": true,
    "enable_answer_optimization": true
  }'
```

## 🔧 配置参数

### 缩减级别 (reduction_level)
- **basic**: 保守缩减，保持原意不变
- **advanced**: 平衡缩减，去除冗余但保留关键信息
- **aggressive**: 激进缩减，最大化压缩文本长度

### 功能开关
- **enable_question_reduction**: 是否启用问题精简 (默认: true)
- **enable_answer_optimization**: 是否启用回答优化 (默认: true)

## 📊 优化效果示例

### 原始数据
```json
{
  "messages": [
    {
      "role": "user",
      "content": "将，熊建伟，021141,项目实验74，中移除"
    },
    {
      "role": "assistant",
      "content": "{\"操作\": \"删除\", \"对象\": \"人员安排\", \"项目\": \"无\", \"供应商\": \"无\", \"对象状态\": \"无\", \"对象提交时间\": \"无\", \"对象下单时间\": \"无\", \"对象审核结束时间\": \"无\", \"材料状态\": \"无\", \"材料类型\": \"无\", \"材料工艺图\": \"无\", \"材料工程属性\": \"无\", \"材料编号\": \"无\", \"对象金额\": \"无\", \"材料AI金额条件\": \"无\", \"对象审核单类型\": \"无\", \"材料是否异型\": \"无\", \"材料是否超长超宽\": \"无\", \"对象单号\": \"无\", \"网版费\": \"无\", \"其他费用说明\": \"无\", \"人员姓名\": [{\"name\": \"熊建伟\", \"code\": \"\"}, {\"name\": \"\", \"code\": \"021141\"}], \"人员工号\": \"无\", \"角色信息\": \"无\", \"人员项目\": [\"实验74\"], \"人员全部项目\": \"无\"}"
    }
  ]
}
```

### 优化后数据（意图分析格式）
```json
{
  "messages": [
    {
      "role": "user",
      "content": "将，熊建伟，021141，实验74以及中移除"
    },
    {
      "role": "assistant",
      "content": "{\"操作\":\"删除\",\"对象\":\"人员安排\",\"项目\":\"实验74\",\"人员\":[\"姓名:熊建伟\",\"编号:021141\"]}"
    }
  ],
  "optimization_metadata": {
    "question_reduction": {
      "original_question": "将，熊建伟，021141,项目实验74，中移除",
      "reduction_level": "advanced",
      "reduction_stats": {
        "original_length": 23,
        "final_length": 22,
        "reduction_rate": 0.043,
        "applied_rules": ["company_shortname", "experiment_id", "basic_simplify"]
      }
    },
    "intent_extraction": {
      "extracted_fields": ["操作", "对象", "项目", "人员"],
      "extraction_method": "rule_based"
    },
    "optimization_timestamp": "2025-08-11T10:30:00.290000"
  }
}
```

### 优化效果对比

| 项目 | 原始 | 优化后 | 改进 |
|------|------|--------|------|
| **问题长度** | 23字符 | 22字符 | 缩减4.3% |
| **回答长度** | 1,089字符 | 134字符 | 缩减87.7% |
| **JSON字段数** | 25个字段 | 4个字段 | 减少84% |
| **文件大小** | 显著减小 | - | 节省存储空间 |

## 📈 优化报告解读

### 处理统计
```
- 总记录数: 60
- 成功优化: 60  
- 失败记录: 0
- 成功率: 100.0%
```

### 问题缩减效果
```
- 平均缩减率: 9.6%
- 平均原始长度: 33.9 字符
- 平均缩减长度: 30.8 字符
- 平均质量评分: 0.701
```

### 应用规则统计
```
- basic_simplify: 60次
- company_shortname: 32次  
- experiment_id: 31次
- time_expressions: 6次
```

## 🎯 优化策略

### 问题精简策略
1. **实验编号标准化**: "项目实验74" → "实验74"
2. **人员信息整理**: 规范姓名和工号格式
3. **冗余词汇移除**: 去除"项目"、"将"等冗余词汇
4. **标点符号优化**: 统一使用标准标点符号

### 回答优化策略
1. **无用字段移除**: 删除所有值为"无"的字段
2. **核心信息保留**: 保留操作、对象、人员姓名、项目等关键字段
3. **数据结构清理**: 优化嵌套结构，移除空值
4. **JSON压缩**: 移除不必要的空格和格式化

## 🔍 质量保证

### 自动质量检查
- **语义完整性**: 确保缩减后意思不变
- **关键信息保持**: 验证重要信息不丢失
- **JSON有效性**: 确保输出JSON格式正确
- **数据一致性**: 保持原有数据结构逻辑

### 错误处理
- **格式错误**: 自动跳过无法解析的记录
- **缩减失败**: 保留原始内容，记录错误信息
- **JSON解析错误**: 保持原始回答不变
- **详细日志**: 记录所有处理过程和错误

## 📁 输出文件

### 文件命名规则
```
optimized_{原文件名}_{时间戳}.jsonl
```

### 输出格式
- **保持JSONL格式**: 每行一个JSON对象
- **添加元数据**: 包含优化过程的详细信息
- **向后兼容**: 可以直接用于模型训练

### 元数据字段
```json
{
  "optimization_metadata": {
    "question_reduction": {
      "original_question": "原始问题",
      "reduction_level": "缩减级别",
      "reduction_stats": "缩减统计信息"
    },
    "optimization_timestamp": "优化时间戳"
  }
}
```

## 🚀 性能优化

### 处理速度
- **批量处理**: 支持大文件批量优化
- **内存优化**: 流式处理，避免内存溢出
- **并发处理**: 支持多线程处理（规划中）

### 存储优化
- **文件压缩**: 显著减少文件大小
- **格式优化**: 移除冗余信息
- **结构化存储**: 便于后续处理和分析

## 🔧 高级用法

### 批量处理多个文件
```python
import glob
from src.service.data_processing.training_data_optimizer import TrainingDataOptimizer

optimizer = TrainingDataOptimizer()

# 处理目录下所有JSONL文件
for file_path in glob.glob("outputs/data/*.jsonl"):
    if not file_path.startswith("optimized_"):
        result = optimizer.optimize_training_data(file_path)
        print(f"优化完成: {result['output_file']}")
```

### 自定义优化策略
```python
# 只进行问题精简，不优化回答
result = optimizer.optimize_training_data(
    input_file="data.jsonl",
    enable_question_reduction=True,
    enable_answer_optimization=False
)

# 使用激进缩减策略
result = optimizer.optimize_training_data(
    input_file="data.jsonl", 
    reduction_level="aggressive"
)
```

## 📞 故障排除

### 常见问题

**Q: 优化后的文件无法正常使用？**
A: 检查原始文件格式是否正确，确保每行都是有效的JSON对象。

**Q: 缩减效果不明显？**
A: 尝试使用"aggressive"缩减级别，或检查原始问题是否已经很简洁。

**Q: 出现JSON解析错误？**
A: 检查原始数据中的JSON格式是否正确，特别注意引号和转义字符。

**Q: 处理速度较慢？**
A: 对于大文件，这是正常现象。可以考虑分批处理或使用更高性能的硬件。

### 日志分析
- **INFO级别**: 正常处理进度
- **WARNING级别**: 非致命错误，如缩减失败
- **ERROR级别**: 严重错误，需要人工干预

---

*训练数据优化器让你的训练数据更精简、更高效！* 🚀
