# 100.AI.TrainData 项目文档

## 项目概述

100.AI.TrainData是一个智能化AI训练数据生成与评估分析项目，主要提供两大核心功能：

### 1. 训练数据生成系统
用于生成针对不同业务场景的结构化训练数据。项目通过定义各种规则文件和数据元素，为AI模型提供高质量的训练数据。

### 2. 评估分析系统 🆕
提供全方位的模型评估数据分析功能，包括：
- **智能失败模式检测**：自动识别和分类评估失败原因
- **质量指标计算**：多维度质量分析和性能评估  
- **可视化报告生成**：生成包含图表的HTML分析报告
- **改进建议引擎**：基于分析结果提供针对性改进建议
- **REST API接口**：提供完整的API服务支持

## 目录结构

```
100.AI.TrainData/
├── rules/                   # 原始规则文件目录
│   ├── staff/               # 人员相关规则
│   │   ├── searchStaff      # 查询人员规则
│   │   └── updateStaff      # 更新人员规则
│   ├── cost/                # 成本相关规则
│   │   ├── searchCargo      # 查询货单规则
│   │   └── updateCargo      # 更新货单规则
│   ├── po/                  # 订单相关规则
│   │   └── searchPo         # 查询订单规则
│   ├── contract/            # 合同相关规则
│   │   └── searchContract   # 查询合同规则
│   └── cargo/               # 货物相关规则（当前为空）
├── src/                     # 源代码目录
│   ├── entity/              # 实体定义目录
│   │   ├── baseElements/    # 基础数据要素定义
│   │   │   ├── searchStaff.json     # 查询人员基础元素
│   │   │   ├── updateStaff.json     # 更新人员基础元素
│   │   │   ├── searchCargo.json     # 查询货单基础元素
│   │   │   ├── updateCargo.json     # 更新货单基础元素
│   │   │   ├── searchPo.json        # 查询订单基础元素
│   │   │   └── searchContract.json  # 查询合同基础元素
│   │   ├── answerElements/  # 回答要素定义
│   │   │   ├── searchStaff.json     # 查询人员回答要素
│   │   │   ├── updateStaff.json     # 更新人员回答要素
│   │   │   ├── searchCargo.json     # 查询货单回答要素
│   │   │   ├── updateCargo.json     # 更新货单回答要素
│   │   │   ├── searchPo.json        # 查询订单回答要素
│   │   │   └── searchContract.json  # 查询合同回答要素
│   │   ├── evaluation/      # 评估分析实体 🆕
│   │   │   ├── __init__.py           # 模块初始化
│   │   │   ├── evaluation_record.py  # 评估记录数据结构
│   │   │   ├── failure_pattern.py    # 失败模式数据结构
│   │   │   ├── quality_metrics.py    # 质量指标数据结构
│   │   │   └── analysis_result.py    # 分析结果数据结构
│   │   └── relationship/    # 关系定义（当前为空）
│   ├── service/             # 服务层代码
│   │   ├── common/          # 通用服务
│   │   │   ├── base_generation_service.py  # 基础生成服务
│   │   │   ├── variation_generation_service.py  # 变种生成服务
│   │   │   └── ...
│   │   ├── evaluation_analysis/  # 评估分析服务 🆕
│   │   │   ├── __init__.py              # 模块初始化
│   │   │   ├── evaluation_analyzer.py   # 主分析引擎
│   │   │   ├── failure_pattern_detector.py  # 失败模式检测器
│   │   │   ├── quality_metrics_calculator.py  # 质量指标计算器
│   │   │   ├── recommendation_engine.py     # 建议引擎
│   │   │   └── report_generator.py         # 报告生成器
│   │   ├── staffing_service.py      # 人员安排服务
│   │   ├── staff_update_service.py  # 人员更新服务
│   │   ├── qwen_service.py          # 通义千问格式服务
│   │   └── rule_logic.py            # 规则逻辑服务
│   ├── api/                 # API接口层 🆕
│   │   ├── __init__.py              # 模块初始化
│   │   ├── app.py                   # FastAPI应用主文件
│   │   └── routes/                  # API路由模块
│   │       ├── __init__.py              # 路由模块初始化
│   │       ├── base_dict.py             # 基础字典路由
│   │       ├── relationship.py          # 关系规则路由
│   │       ├── answer.py                # 回答元素路由
│   │       ├── generate.py              # 数据生成路由
│   │       └── evaluation_analysis.py   # 评估分析路由 🆕
│   ├── config/              # 配置文件目录
│   │   ├── generation_settings.yml     # 生成设置配置文件
│   │   ├── evaluation_analysis_settings.yml  # 评估分析配置 🆕
│   │   └── config_loader.py         # 配置加载器 🆕
├── test/                    # 测试代码目录 🆕
│   ├── __init__.py              # 测试模块初始化
│   ├── service/                 # 服务测试
│   │   └── evaluation_analysis/ # 评估分析测试
│   │       ├── test_evaluation_analyzer.py    # 分析器测试
│   │       ├── test_report_generator.py       # 报告生成器测试
│   │       └── test_real_file.py              # 真实文件测试
│   └── api/                     # API测试
│       ├── test_evaluation_analysis_api.py    # API接口测试
│       └── demo_evaluation_analysis.py       # 功能演示脚本
├── outputs/                 # 输出目录 🆕
│   ├── data/               # 生成的训练数据
│   ├── temp/               # 临时文件
│   └── reports/            # 分析报告
└── docs/                   # 文档目录
    ├── README.md           # 本文档
    ├── codebase.md         # 代码库文档
    ├── services.md         # 服务层文档
    └── variation_generation.md  # 变种生成逻辑详解文档
```

## 文件说明

### 规则文件 (rules/)

规则文件是项目的核心，它们定义了生成训练数据的模式和逻辑规则。每个规则文件通常包含以下几个部分：

1. **数据要素定义**：定义该业务场景中的基本数据要素
2. **要素组合规则**：规定数据要素如何组合
3. **要素组合要求**：（部分文件包含）对要素组合的额外约束
4. **举例**：提供实际应用中的例子
5. **问题解析格式**：定义如何解析和回答相关问题

#### staff/ 目录 - 人员管理相关规则

* **searchStaff**: 定义查询项目人员的规则，包括查询没有安排人员的项目、查询特定人员被安排的项目、查询项目中被安排的人员等。
* **updateStaff**: 定义更新项目人员的规则，包括添加项目人员、将人员安排到项目、从项目中撤销人员等。

#### cost/ 目录 - 成本管理相关规则

* **searchCargo**: 定义查询货单的规则，包括查询特定项目的货单、特定供应商的货单、特定状态的货单等。
* **updateCargo**: 定义更新货单的规则，包括两种主要规则模式（操作+供应商+项目+发货单号、操作+供应商+项目+送货单号）以及审核通过货单、导出结算单、审核退回货单、删除货单等操作。

#### po/ 目录 - 订单管理相关规则

* **searchPo**: 定义查询订单的规则，包括查询特定项目的订单、特定供应商的订单、特定状态的订单、特定金额范围的订单等。

#### contract/ 目录 - 合同管理相关规则

* **searchContract**: 定义查询合同的规则，包括查询特定项目的合同、特定供应商的合同、特定状态的合同等。

### 实体定义文件 (src/entity/)

实体定义文件以JSON格式组织，结构化地描述了各种业务实体及其属性。

#### baseElements/ 目录 - 基础数据要素

这些文件定义了对应规则文件中的基础数据要素，以JSON结构化表示。每个文件包含：

* **businessObject**: 业务对象名称
* **baseDataList**: 数据要素数组
  * **name**: 语义名称
  * **number**: 要素编号
  * **conditionList**: 变体数组
  * **originalText**: 原始文本
  * **originalLogic**: 逻辑说明
  * **originalRegex**: 正则表达式

#### answerElements/ 目录 - 回答要素

这些文件定义了各种业务场景中问题的回答要素，对应于规则文件中的"问题解析格式"部分。每个文件包含：

* **answerObject**: 回答对象名称
* **answerElements**: 回答要素数组
  * **name**: 元素名称
  * **nameCN**: 中文名称
  * **relateToBase**: 与基础数据要素的关联关系
  * **isStatic**: 是否为静态值
  * **staticValue**: 静态值内容

#### relationship/ 目录 - 关系定义

用于定义业务实体之间的关系（当前为空）。

### 评估分析实体 (src/entity/evaluation/) 🆕

评估分析实体定义了评估分析系统中使用的核心数据结构：

* **evaluation_record.py**: 定义单条评估记录的数据结构，包括问题、期望答案、实际答案、评分等信息
* **failure_pattern.py**: 定义失败模式分析的数据结构，包括失败类型、严重程度、统计信息等
* **quality_metrics.py**: 定义质量指标相关的数据结构，包括分数分布、性能指标、质量洞察等
* **analysis_result.py**: 定义分析结果的综合数据结构，包含完整的分析报告和建议

### 服务层代码 (src/service/)

服务层代码实现了从规则到结构化训练数据的转换逻辑，以及评估分析的核心功能，是项目的核心功能部分。

#### evaluation_analysis/ 目录 - 评估分析服务 🆕

* **evaluation_analyzer.py**: 主分析引擎，协调整个评估分析流程，负责文件解析、质量分析和结果生成
* **failure_pattern_detector.py**: 失败模式检测器，智能识别和分类评估失败原因，提供失败统计和分析
* **quality_metrics_calculator.py**: 质量指标计算器，计算多维度质量指标，包括成功率、分数分布、性能指标等
* **recommendation_engine.py**: 建议引擎，基于分析结果生成针对性的改进建议，提供优先级排序
* **report_generator.py**: 报告生成器，生成包含可视化图表的HTML分析报告

#### common/ 目录 - 通用服务

* **base_generation_service.py**: 基础数据生成服务类，封装了通用的数据生成逻辑，作为具体业务服务的父类。提供了规则权重计算、问题生成、答案生成等通用功能。
* **variation_generation_service.py**: 变种生成服务类，继承自BaseGenerationService，提供更专注的变种生成功能。实现了智能处理可能变种数量与份额不匹配的情况，确保生成数据的数量和多样性。

#### 业务服务文件

* **staffing_service.py**: 人员安排服务，继承自BaseGenerationService，用于生成searchStaff业务对象的训练数据。
* **staff_update_service.py**: 人员安排更新服务，继承自BaseGenerationService，用于生成updateStaff业务对象的训练数据。此服务重写了父类的特殊元素处理方法，实现了字典替换逻辑。
* **qwen_service.py**: 通义千问格式服务，将生成的训练数据转换为通义千问模型所需的JSONL格式。
* **rule_logic.py**: 规则逻辑服务，提供规则解析和处理的功能。

### API接口层 (src/api/) 🆕

API接口层提供了完整的REST API服务，支持训练数据生成和评估分析功能：

* **app.py**: FastAPI应用主文件，配置CORS、路由挂载和静态文件服务
* **routes/evaluation_analysis.py**: 评估分析API路由，提供8个核心端点：
  - `POST /api/evaluation/upload` - 文件上传接口
  - `POST /api/evaluation/analyze` - 分析请求接口
  - `GET /api/evaluation/status/{task_id}` - 状态查询接口
  - `GET /api/evaluation/result/{task_id}` - 结果获取接口
  - `GET /api/evaluation/report/{task_id}` - HTML报告下载接口
  - `GET /api/evaluation/tasks` - 任务列表查询接口
  - `DELETE /api/evaluation/task/{task_id}` - 任务清理接口
  - `GET /api/evaluation/health` - 健康检查接口

## 数据流程

项目包含两个主要的数据流程：

### 训练数据生成流程

1. 通过规则文件（rules/）定义各种业务场景的数据生成规则
2. 将规则文件转换为结构化的基础数据要素（baseElements/）
3. 定义问题解析格式的回答要素（answerElements/）
4. 使用服务层代码（service/）生成符合规则的训练数据
5. 根据需要将数据转换为特定的格式（如通义千问格式）

### 评估分析流程 🆕

1. **文件上传**：通过API上传评估结果JSON文件
2. **数据解析**：解析评估文件，提取评估记录和元数据
3. **失败分析**：识别和分类失败模式，统计失败原因
4. **质量计算**：计算多维度质量指标，包括成功率、分数分布、性能指标
5. **建议生成**：基于分析结果生成针对性改进建议
6. **报告生成**：生成包含可视化图表的HTML分析报告
7. **结果输出**：通过API提供JSON结果和HTML报告下载

## 使用说明

本项目提供训练数据生成和评估分析两大功能，具体使用步骤如下：

### 基础数据生成

```python
# 导入相关服务
from src.service.staffing_service import generate_staffing_data
from src.service.staff_update_service import generate_staff_update_data

# 生成searchStaff的人员安排数据
staffing_data = generate_staffing_data('searchStaff', 10, 2)
print(f"\n生成的数据数量: {len(staffing_data)}")

# 生成updateStaff的人员安排更新数据
staff_update_data = generate_staff_update_data('updateStaff', 10, 2)
```

### 生成通义千问格式数据

```python
# 导入千问服务
from src.service.qwen_service import generate_qwen_data

# 生成searchStaff的千问训练数据
output_file = generate_qwen_data('searchStaff', 10, 2)
print(f"生成的文件路径: {output_file}")

# 生成updateStaff的千问训练数据
output_file = generate_qwen_data('updateStaff', 10, 2)
```

### 评估分析系统使用 🆕

#### API服务启动

```bash
# 进入项目目录
cd 100.AI.TrainData

# 安装依赖（如果还未安装）
pip install -r requirements.txt

# 启动API服务
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

# 访问API文档
# http://localhost:8000/docs
```

#### Python SDK使用示例

```python
# 导入评估分析模块
from src.service.evaluation_analysis.evaluation_analyzer import EvaluationAnalyzer
from src.service.evaluation_analysis.report_generator import ReportGenerator

# 创建分析器实例
analyzer = EvaluationAnalyzer()

# 分析评估文件
result = analyzer.analyze_evaluation_file("path/to/evaluation_file.json")

# 生成HTML报告
report_generator = ReportGenerator()
html_report = report_generator.generate_html_report(result)

# 保存报告
with open("outputs/reports/analysis_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)

print(f"分析完成! 处理了 {result['total_records']} 条记录")
print(f"成功率: {result['metrics']['success_rate']:.1%}")
print(f"平均分数: {result['metrics']['average_score']:.1f}")
```

#### API调用示例

```python
import requests

# 1. 上传评估文件
with open("evaluation_data.json", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/evaluation/upload",
        files={"file": f}
    )
file_id = response.json()["file_id"]

# 2. 请求分析
response = requests.post(
    "http://localhost:8000/api/evaluation/analyze",
    json={"file_id": file_id}
)
task_id = response.json()["task_id"]

# 3. 查询分析状态
response = requests.get(f"http://localhost:8000/api/evaluation/status/{task_id}")
status = response.json()["status"]

# 4. 获取分析结果
if status == "completed":
    response = requests.get(f"http://localhost:8000/api/evaluation/result/{task_id}")
    result = response.json()
    
    # 下载HTML报告
    report_response = requests.get(f"http://localhost:8000/api/evaluation/report/{task_id}")
    with open("analysis_report.html", "w", encoding="utf-8") as f:
        f.write(report_response.text)
```

## 进一步开发

项目可以向以下方向扩展：

### 训练数据生成系统扩展
1. 完善cargo目录下的规则文件
2. 丰富relationship目录下的实体关系定义
3. 开发更多种类的数据生成服务
4. 支持更多AI模型的训练数据格式
5. 建立验证机制，确保生成数据的质量和有效性

### 评估分析系统扩展 🆕
1. **多格式支持**：扩展支持CSV、Excel等其他评估数据格式
2. **实时监控**：开发实时评估监控面板，支持流式数据分析
3. **对比分析**：实现多个模型版本之间的对比分析功能
4. **自动化报告**：支持定时生成和发送分析报告
5. **机器学习增强**：使用ML算法改进失败模式检测和建议生成
6. **集成部署**：支持Docker容器化部署和Kubernetes集群部署
7. **数据可视化增强**：开发更丰富的交互式图表和仪表板
8. **API扩展**：增加批量分析、历史数据查询等高级API功能 

## 文档列表

项目提供了详细的文档，包括：

1. **README.md** (本文档): 项目总体概述和使用说明
2. **codebase.md**: 代码库结构和主要组件说明
3. **services.md**: 服务层详细设计和实现说明
4. **variation_generation.md**: 变种生成逻辑详解，包括变种生成策略、配置参数和实际案例分析

