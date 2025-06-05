# 100.AI.TrainData 项目文档

## 项目概述

100.AI.TrainData是一个AI训练数据生成项目，主要用于生成针对不同业务场景的结构化训练数据。项目通过定义各种规则文件和数据元素，为AI模型提供高质量的训练数据。

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
│   │   └── relationship/    # 关系定义（当前为空）
│   ├── service/             # 服务层代码
│   │   ├── common/          # 通用服务
│   │   │   ├── base_generation_service.py  # 基础生成服务
│   │   │   ├── variation_generation_service.py  # 变种生成服务
│   │   │   └── ...
│   │   ├── staffing_service.py      # 人员安排服务
│   │   ├── staff_update_service.py  # 人员更新服务
│   │   ├── qwen_service.py          # 通义千问格式服务
│   │   └── rule_logic.py            # 规则逻辑服务
│   ├── config/              # 配置文件目录
│   │   └── generation_settings.yml  # 生成设置配置文件
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

### 服务层代码 (src/service/)

服务层代码实现了从规则到结构化训练数据的转换逻辑，是项目的核心功能部分。

#### common/ 目录 - 通用服务

* **base_generation_service.py**: 基础数据生成服务类，封装了通用的数据生成逻辑，作为具体业务服务的父类。提供了规则权重计算、问题生成、答案生成等通用功能。
* **variation_generation_service.py**: 变种生成服务类，继承自BaseGenerationService，提供更专注的变种生成功能。实现了智能处理可能变种数量与份额不匹配的情况，确保生成数据的数量和多样性。

#### 业务服务文件

* **staffing_service.py**: 人员安排服务，继承自BaseGenerationService，用于生成searchStaff业务对象的训练数据。
* **staff_update_service.py**: 人员安排更新服务，继承自BaseGenerationService，用于生成updateStaff业务对象的训练数据。此服务重写了父类的特殊元素处理方法，实现了字典替换逻辑。
* **qwen_service.py**: 通义千问格式服务，将生成的训练数据转换为通义千问模型所需的JSONL格式。
* **rule_logic.py**: 规则逻辑服务，提供规则解析和处理的功能。

## 数据流程

整个项目的数据流程如下：

1. 通过规则文件（rules/）定义各种业务场景的数据生成规则
2. 将规则文件转换为结构化的基础数据要素（baseElements/）
3. 定义问题解析格式的回答要素（answerElements/）
4. 使用服务层代码（service/）生成符合规则的训练数据
5. 根据需要将数据转换为特定的格式（如通义千问格式）

## 使用说明

本项目主要用于生成AI训练数据，具体使用步骤如下：

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

## 进一步开发

项目可以向以下方向扩展：

1. 完善cargo目录下的规则文件
2. 丰富relationship目录下的实体关系定义
3. 开发更多种类的数据生成服务
4. 支持更多AI模型的训练数据格式
5. 建立验证机制，确保生成数据的质量和有效性 

## 文档列表

项目提供了详细的文档，包括：

1. **README.md** (本文档): 项目总体概述和使用说明
2. **codebase.md**: 代码库结构和主要组件说明
3. **services.md**: 服务层详细设计和实现说明
4. **variation_generation.md**: 变种生成逻辑详解，包括变种生成策略、配置参数和实际案例分析

## 数据流程

整个项目的数据流程如下：

1. 通过规则文件（rules/）定义各种业务场景的数据生成规则
2. 将规则文件转换为结构化的基础数据要素（baseElements/）
3. 定义问题解析格式的回答要素（answerElements/）
4. 使用服务层代码（service/）生成符合规则的训练数据
5. 根据需要将数据转换为特定的格式（如通义千问格式） 