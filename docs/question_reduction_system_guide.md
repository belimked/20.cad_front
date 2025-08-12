# 智能问题精简系统使用指南

## 📋 系统概述

智能问题精简系统是一个完整的问题文本缩减解决方案，提供了从基础缩减到高级整合的全套功能，支持多种训练数据格式生成和完整的质量评估体系。

### 🎯 核心功能
- **问题缩减处理**：支持实验编号标准化、公司名称简化、工程属性提取、时间表达标准化
- **训练数据生成**：支持Standard、Classification、SFT三种格式
- **质量评估体系**：提供缩减率、关键信息保持率、语义相似度、可读性评分等指标
- **专项分析报告**：生成详细的缩减效果分析和改进建议

## 🚀 快速开始

### 1. 基础问题缩减

```python
from src.service.common.question_reduction import advanced_simplify_question

# 基础缩减
original = "找一下实验03以及实验41的相关信息"
result = advanced_simplify_question(original, reduction_level='basic')
print(result)  # 输出: "实验03、实验41"

# 获取详细统计信息
result_with_stats = advanced_simplify_question(original, return_stats=True)
print(result_with_stats['stats'])
```

### 2. 生成训练数据

#### 通过API接口生成

```bash
# 生成标准格式训练数据
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff",
    "count": 10,
    "enable_question_reduction": true,
    "training_format": "standard"
  }'

# 生成分类训练格式
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff", 
    "count": 10,
    "enable_question_reduction": true,
    "training_format": "classification"
  }'

# 生成SFT训练格式
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff",
    "count": 10, 
    "enable_question_reduction": true,
    "training_format": "sft"
  }'
```

### 3. 质量评估

```python
from src.service.common.question_reduction import evaluate_reduction_quality

original = "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息"
reduced = "百聚鑫钢构、紧鑫五金项目信息"

quality_result = evaluate_reduction_quality(original, reduced)
print(quality_result)
# 输出: {
#   "reduction_rate": 0.567,
#   "key_info_retention_rate": 1.0,
#   "semantic_similarity": 0.823,
#   "readability_score": 0.9,
#   "overall_quality": 0.823
# }
```

## 📊 API接口详解

### 1. 数据生成接口

**端点**: `POST /api/generate/save-generated-data`

**参数说明**:
- `business_type`: 业务类型 (如: "updateStaff")
- `count`: 生成数据数量
- `enable_question_reduction`: 是否启用问题缩减 (boolean)
- `training_format`: 训练格式 ("standard" | "classification" | "sft")
- `reduction_level`: 缩减级别 ("basic" | "advanced" | "aggressive")

**响应格式**:
```json
{
  "files": {
    "question_reduction_file": "文件名.jsonl",
    "classification_file": "分类格式文件名.jsonl",  // 仅classification格式
    "sft_file": "SFT格式文件名.jsonl"  // 仅sft格式
  },
  "training_format": "classification",
  "question_reduction_count": 100,
  "format_specific_count": 100
}
```

### 2. 问题缩减分析接口

**端点**: `POST /api/evaluation/question-reduction/analyze`

**请求格式**:
```json
{
  "reduction_data": [
    {
      "original_question": "原始问题文本",
      "reduced_question": "缩减后文本", 
      "reduction_stats": {
        "applied_rules": ["规则名称"],
        "reduction_level": "basic"
      }
    }
  ],
  "generate_report": true
}
```

**响应格式**:
```json
{
  "analysis_result": {
    "reduction_effectiveness": {
      "average_reduction_rate": 0.533,
      "median_reduction_rate": 0.5,
      "average_length_reduction": 11.7
    },
    "rule_application_analysis": {
      "most_used_rules": {"规则名": "使用次数"},
      "reduction_level_distribution": {"basic": 1, "advanced": 1}
    },
    "quality_distribution": {
      "quality_category_percentages": {
        "excellent": 0.0,
        "good": 66.7,
        "fair": 0.0, 
        "poor": 33.3
      }
    },
    "recommendations": ["改进建议列表"]
  }
}
```

### 3. 报告生成接口

**端点**: `POST /api/evaluation/question-reduction/report`

**参数**:
- `output_format`: 输出格式 ("html" | "markdown" | "json")

**响应**: 根据格式返回相应的报告内容

## 🔧 训练数据格式说明

### Standard格式
```json
{
  "original_question": "找一下实验03以及实验41的相关信息",
  "reduced_question": "实验03、实验41",
  "reduction_stats": {
    "original_length": 17,
    "final_length": 9,
    "reduction_rate": 0.471,
    "applied_rules": ["normalize_experiment_id"],
    "reduction_level": "basic"
  },
  "question_metadata": {
    "business_type": "updateStaff",
    "rule_id": "10",
    "rule_name": "人员项目管理"
  }
}
```

### Classification格式
```json
{
  "text": "找一下实验03以及实验41的相关信息",
  "labels": {
    "reduction_type": ["normalize_experiment_id"],
    "target_length": 9
  },
  "reduced_text": "实验03、实验41"
}
```

### SFT格式
```json
{
  "messages": [
    {
      "role": "user",
      "content": "请将以下问题进行精简缩减：找一下实验03以及实验41的相关信息"
    },
    {
      "role": "assistant", 
      "content": "实验03、实验41"
    }
  ]
}
```

## 🧪 测试和验证

### 运行测试套件

```bash
# 运行问题缩减专项测试
python test/service/test_question_reduction.py

# 运行特定测试类
python -m pytest test/service/test_question_reduction.py::TestBasicReductionFunctions -v

# 运行评估功能测试
python -m pytest test/service/test_question_reduction.py::TestEvaluateReductionQuality -v
```

### 测试覆盖范围
- ✅ 基础缩减函数测试 (4个测试用例)
- ✅ 高级缩减功能测试 (6个测试用例)  
- ✅ 评估指标功能测试 (5个测试用例)
- ✅ 边界情况测试 (4个测试用例)

## 📈 质量评估指标

### 评估维度
1. **缩减率** (Reduction Rate): 文本长度缩减比例
2. **关键信息保持率** (Key Info Retention): 重要信息保留程度
3. **语义相似度** (Semantic Similarity): 原文与缩减文本的语义相似性
4. **可读性评分** (Readability Score): 缩减后文本的可读性
5. **综合质量评分** (Overall Quality): 加权综合评分

### 质量等级分类
- **优秀** (≥90%): 高质量缩减，信息完整且表达清晰
- **良好** (70-89%): 缩减效果良好，基本满足要求
- **一般** (50-69%): 缩减效果一般，可能需要优化
- **较差** (<50%): 缩减质量不佳，建议重新处理

## 🛠️ 配置和自定义

### 缩减级别配置
- **basic**: 基础缩减，保守处理
- **advanced**: 高级缩减，平衡效果与质量
- **aggressive**: 激进缩减，最大化缩减率

### 自定义缩减规则
系统支持以下内置规则：
- `normalize_experiment_id`: 实验编号标准化
- `extract_company_shortname`: 公司名称简化
- `extract_engineering_keywords`: 工程属性提取
- `normalize_time_expressions`: 时间表达标准化

## 📁 文件输出说明

### 文件命名规范
- **标准格式**: `{prefix}_questionReduction_data_{business_type}_{timestamp}.jsonl`
- **分类格式**: `{prefix}_questionReduction_train_classification_{business_type}_{timestamp}.jsonl`
- **SFT格式**: `{prefix}_questionReduction_train_sft_{business_type}_{timestamp}.jsonl`

### 输出目录
- 默认输出目录: `export/`
- 支持自定义输出路径
- 自动创建时间戳子目录

## 🔍 故障排除

### 常见问题

**Q: 缩减效果不理想怎么办？**
A: 
1. 尝试调整缩减级别 (basic → advanced → aggressive)
2. 检查输入文本是否符合预期格式
3. 使用质量评估功能分析具体问题

**Q: 训练数据格式不正确？**
A:
1. 确认`training_format`参数设置正确
2. 检查API响应中的文件路径
3. 验证生成的JSONL文件格式

**Q: 测试失败怎么处理？**
A:
1. 检查依赖模块是否正确安装
2. 确认项目路径配置正确
3. 查看具体错误信息进行针对性修复

### 日志和调试
- 系统使用标准Python logging模块
- 日志级别: INFO (默认)
- 关键操作都有详细日志记录

## 📞 技术支持

如需技术支持或有任何问题，请：
1. 查看本文档的故障排除部分
2. 运行测试套件验证系统状态
3. 检查日志文件获取详细错误信息

---

*本文档涵盖了智能问题精简系统的完整使用方法，建议收藏备用！* 🐾
