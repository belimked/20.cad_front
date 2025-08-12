# 智能问题精简系统 API 使用示例

## 🚀 快速开始示例

### 1. 生成标准格式训练数据

```bash
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff",
    "count": 50,
    "enable_question_reduction": true,
    "training_format": "standard",
    "reduction_level": "advanced"
  }'
```

**响应示例**:
```json
{
  "message": "数据生成成功",
  "files": {
    "raw_file": "raw_data_updateStaff_20250811_100000.jsonl",
    "qwen_file": "qwen_data_updateStaff_20250811_100000.jsonl",
    "question_reduction_file": "questionReduction_data_updateStaff_20250811_100000.jsonl"
  },
  "training_format": "standard",
  "question_reduction_count": 50,
  "format_specific_count": 50,
  "question_reduction_stats": {
    "reduction_level": "advanced",
    "total_processed": 50,
    "overall_reduction_rate": 0.45,
    "applied_rules_count": {
      "normalize_experiment_id": 15,
      "extract_company_shortname": 20,
      "normalize_time_expressions": 10
    }
  }
}
```

### 2. 生成分类训练格式数据

```bash
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff",
    "count": 100,
    "enable_question_reduction": true,
    "training_format": "classification",
    "reduction_level": "basic"
  }'
```

**生成的数据格式**:
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

### 3. 生成SFT训练格式数据

```bash
curl -X POST "http://localhost:8000/api/generate/save-generated-data" \
  -H "Content-Type: application/json" \
  -d '{
    "business_type": "updateStaff",
    "count": 200,
    "enable_question_reduction": true,
    "training_format": "sft",
    "reduction_level": "aggressive"
  }'
```

**生成的数据格式**:
```json
{
  "messages": [
    {
      "role": "user",
      "content": "请将以下问题进行精简缩减：广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息"
    },
    {
      "role": "assistant",
      "content": "百聚鑫钢构、紧鑫五金项目信息"
    }
  ]
}
```

## 📊 质量分析示例

### 1. 分析问题缩减数据

```bash
curl -X POST "http://localhost:8000/api/evaluation/question-reduction/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "reduction_data": [
      {
        "original_question": "找一下实验03以及实验41的相关信息",
        "reduced_question": "实验03、实验41",
        "reduction_stats": {
          "applied_rules": ["normalize_experiment_id"],
          "reduction_level": "basic"
        }
      },
      {
        "original_question": "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息",
        "reduced_question": "百聚鑫钢构、紧鑫五金项目信息",
        "reduction_stats": {
          "applied_rules": ["extract_company_shortname"],
          "reduction_level": "advanced"
        }
      }
    ],
    "generate_report": true
  }'
```

**分析结果示例**:
```json
{
  "analysis_result": {
    "analysis_metadata": {
      "timestamp": "2025-08-11T10:00:00.000000",
      "total_samples": 2,
      "analyzer_version": "1.0.0"
    },
    "reduction_effectiveness": {
      "average_reduction_rate": 0.533,
      "median_reduction_rate": 0.5,
      "max_reduction_rate": 0.567,
      "min_reduction_rate": 0.471,
      "std_reduction_rate": 0.058,
      "average_length_reduction": 11.7,
      "total_samples": 2
    },
    "rule_application_analysis": {
      "most_used_rules": {
        "normalize_experiment_id": 1,
        "extract_company_shortname": 1
      },
      "reduction_level_distribution": {
        "basic": 1,
        "advanced": 1
      },
      "total_rule_applications": 2,
      "unique_rules_count": 2
    },
    "quality_distribution": {
      "quality_category_percentages": {
        "excellent": 0.0,
        "good": 50.0,
        "fair": 0.0,
        "poor": 50.0
      },
      "total_evaluated_samples": 2
    },
    "recommendations": [
      "缩减效果偏低，建议调整缩减策略或增加更激进的缩减规则",
      "使用的缩减规则种类较少，建议增加更多样化的缩减策略"
    ],
    "summary": "问题缩减分析摘要：\n- 分析样本数量：2\n- 平均缩减率：53.3%\n- 高质量缩减比例：50.0%\n- 整体评估：需要改进"
  },
  "report_content": "# 问题缩减质量评估报告\n\n**生成时间**: 2025-08-11T10:00:00.000000\n**分析样本数**: 2\n\n## 执行摘要\n\n问题缩减分析摘要：\n- 分析样本数量：2\n- 平均缩减率：53.3%\n- 高质量缩减比例：50.0%\n- 整体评估：需要改进\n\n## 缩减效果分析\n\n- **平均缩减率**: 53.3%\n- **中位数缩减率**: 50.0%\n- **平均长度缩减**: 11.7 字符\n- **缩减率标准差**: 0.058\n\n## 规则应用分析\n\n**最常用规则**:\n  - normalize_experiment_id: 1次\n  - extract_company_shortname: 1次\n\n**缩减级别分布**:\n  - basic: 1次\n  - advanced: 1次\n\n- **总规则应用次数**: 2\n- **使用的规则种类**: 2\n\n## 质量分布分析\n\n**质量等级分布**:\n- 优秀 (≥90%): 0.0%\n- 良好 (70-89%): 50.0%\n- 一般 (50-69%): 0.0%\n- 较差 (<50%): 50.0%\n\n**评估样本数**: 2\n\n## 改进建议\n\n- 缩减效果偏低，建议调整缩减策略或增加更激进的缩减规则\n- 使用的缩减规则种类较少，建议增加更多样化的缩减策略\n\n---\n*报告由问题缩减专项分析器生成*",
  "timestamp": "2025-08-11T10:00:00.000000",
  "total_samples": 2
}
```

### 2. 生成HTML报告

```bash
curl -X POST "http://localhost:8000/api/evaluation/question-reduction/report?output_format=html" \
  -H "Content-Type: application/json" \
  -d '{
    "reduction_data": [
      {
        "original_question": "查看一下提交日在最近五天的订单预审单信息",
        "reduced_question": "近5天订单预审单",
        "reduction_stats": {
          "applied_rules": ["normalize_time_expressions"],
          "reduction_level": "aggressive"
        }
      }
    ],
    "generate_report": true
  }' \
  --output question_reduction_report.html
```

### 3. 生成Markdown报告

```bash
curl -X POST "http://localhost:8000/api/evaluation/question-reduction/report?output_format=markdown" \
  -H "Content-Type: application/json" \
  -d '{
    "reduction_data": [
      {
        "original_question": "工程属性70mm钢板（Q345B）钢制件的相关信息",
        "reduced_question": "70mm钢板（Q345B）钢制件",
        "reduction_stats": {
          "applied_rules": ["extract_engineering_keywords"],
          "reduction_level": "basic"
        }
      }
    ]
  }' \
  --output question_reduction_report.md
```

## 🐍 Python SDK 示例

### 1. 直接使用缩减函数

```python
from src.service.common.question_reduction import (
    advanced_simplify_question,
    evaluate_reduction_quality
)

# 基础使用
original = "找一下实验03以及实验41的相关信息"
reduced = advanced_simplify_question(original, reduction_level='basic')
print(f"原文: {original}")
print(f"缩减后: {reduced}")

# 获取详细统计
result = advanced_simplify_question(original, return_stats=True)
print(f"缩减率: {result['stats']['reduction_rate']:.1%}")
print(f"应用规则: {result['stats']['applied_rules']}")

# 质量评估
quality = evaluate_reduction_quality(original, reduced)
print(f"综合质量评分: {quality['overall_quality']:.3f}")
```

### 2. 使用分析器

```python
from src.service.evaluation_analysis.question_reduction_analyzer import QuestionReductionAnalyzer

# 创建分析器
analyzer = QuestionReductionAnalyzer()

# 准备测试数据
test_data = [
    {
        'original_question': '找一下实验03以及实验41的相关信息',
        'reduced_question': '实验03、实验41',
        'reduction_stats': {
            'applied_rules': ['normalize_experiment_id'],
            'reduction_level': 'basic'
        }
    },
    {
        'original_question': '广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息',
        'reduced_question': '百聚鑫钢构、紧鑫五金项目信息',
        'reduction_stats': {
            'applied_rules': ['extract_company_shortname'],
            'reduction_level': 'advanced'
        }
    }
]

# 执行分析
analysis_result = analyzer.analyze_reduction_data(test_data)

# 打印关键指标
print(f"平均缩减率: {analysis_result['reduction_effectiveness']['average_reduction_rate']:.1%}")
print(f"质量分布: {analysis_result['quality_distribution']['quality_category_percentages']}")

# 生成报告
report = analyzer.generate_report(test_data)
print("\n=== 分析报告 ===")
print(report)
```

### 3. 批量处理示例

```python
import requests
import json

def batch_generate_training_data(business_types, count_per_type=100):
    """批量生成多种业务类型的训练数据"""
    results = {}
    
    for business_type in business_types:
        for format_type in ['standard', 'classification', 'sft']:
            payload = {
                "business_type": business_type,
                "count": count_per_type,
                "enable_question_reduction": True,
                "training_format": format_type,
                "reduction_level": "advanced"
            }
            
            response = requests.post(
                "http://localhost:8000/api/generate/save-generated-data",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                key = f"{business_type}_{format_type}"
                results[key] = {
                    "file": result["files"]["question_reduction_file"],
                    "count": result["question_reduction_count"],
                    "reduction_rate": result["question_reduction_stats"]["overall_reduction_rate"]
                }
                print(f"✅ {key}: {result['question_reduction_count']} 条数据")
            else:
                print(f"❌ {business_type}_{format_type}: 生成失败")
    
    return results

# 使用示例
business_types = ["updateStaff", "updateCargo"]
results = batch_generate_training_data(business_types, 50)
print(json.dumps(results, indent=2, ensure_ascii=False))
```

## 🔧 高级配置示例

### 1. 自定义缩减参数

```python
# 使用不同缩减级别
levels = ['basic', 'advanced', 'aggressive']
original = "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息"

for level in levels:
    result = advanced_simplify_question(original, reduction_level=level, return_stats=True)
    print(f"{level}: {result['result']} (缩减率: {result['stats']['reduction_rate']:.1%})")
```

### 2. 质量阈值筛选

```python
def filter_high_quality_reductions(data_list, min_quality=0.7):
    """筛选高质量的缩减结果"""
    high_quality_data = []
    
    for item in data_list:
        original = item['original_question']
        reduced = item['reduced_question']
        
        quality = evaluate_reduction_quality(original, reduced)
        if quality['overall_quality'] >= min_quality:
            item['quality_score'] = quality['overall_quality']
            high_quality_data.append(item)
    
    return high_quality_data

# 使用示例
filtered_data = filter_high_quality_reductions(test_data, min_quality=0.8)
print(f"高质量数据: {len(filtered_data)} 条")
```

## 📈 性能监控示例

```python
import time
from collections import defaultdict

def performance_benchmark():
    """性能基准测试"""
    test_cases = [
        "找一下实验03以及实验41的相关信息",
        "广东百聚鑫钢构有限公司和东莞市紧鑫五金有限公司的项目信息",
        "查看一下提交日在最近五天的订单预审单信息",
        "工程属性70mm钢板（Q345B）钢制件的相关信息"
    ]
    
    performance_stats = defaultdict(list)
    
    for level in ['basic', 'advanced', 'aggressive']:
        for case in test_cases:
            start_time = time.time()
            result = advanced_simplify_question(case, reduction_level=level, return_stats=True)
            end_time = time.time()
            
            performance_stats[level].append({
                'processing_time': end_time - start_time,
                'reduction_rate': result['stats']['reduction_rate'],
                'original_length': len(case),
                'reduced_length': len(result['result'])
            })
    
    # 输出性能统计
    for level, stats in performance_stats.items():
        avg_time = sum(s['processing_time'] for s in stats) / len(stats)
        avg_reduction = sum(s['reduction_rate'] for s in stats) / len(stats)
        print(f"{level}: 平均处理时间 {avg_time:.4f}s, 平均缩减率 {avg_reduction:.1%}")

# 运行基准测试
performance_benchmark()
```

---

*这些示例涵盖了智能问题精简系统的主要使用场景，可以根据具体需求进行调整和扩展！* 🚀
