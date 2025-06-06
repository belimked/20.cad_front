# Service模块

本目录包含项目的服务层模块，负责业务逻辑处理和数据访问。

## 服务模块列表

### 1. rule_logic.py - 规则逻辑服务

规则逻辑服务模块用于整合基础元素、回答元素和业务规则数据，提供规则排序和组合功能。

#### 主要功能：

1. 获取指定业务对象的三个数据集合（基础元素、业务规则和回答元素）
2. 按codecount（代码复杂度）降序排序业务规则

#### 使用示例：

```python
from src.service import get_rule_components, get_sorted_rules

# 获取searchStaff的三个数据集合
base_elements, business_rules, answer_elements = get_rule_components('searchStaff')

# 获取按复杂度排序的规则列表
sorted_rules = get_sorted_rules('searchStaff')
for rule in sorted_rules:
    print(f"规则ID: {rule.get('id')}, 名称: {rule.get('name')}, 复杂度: {rule.get('codecount')}")
```

### 2. qwen_service.py - 千问服务

千问服务模块用于生成、格式化和处理问答对，为训练千问模型提供数据支持。

#### 主要功能：

1. 为不同业务对象（updateStaff、searchStaff、updateCargo、searchContract）生成标准化的问答数据
2. 格式化问题到自然语言形式
3. 根据规则代码库匹配问答模式
4. 处理答案字段为中文响应格式

#### 使用示例：

```python
from src.service.qwen_service import generate_qwen_data

# 为search查询对象生成千问训练数据
jsonl_file, original_data_file = generate_qwen_data('searchStaff', total_samples=5000, variations_per_rule=5)

# 为update操作对象生成千问训练数据
jsonl_file, original_data_file = generate_qwen_data('updateStaff', total_samples=8000, variations_per_rule=5)
```

### 3. 业务对象服务模块

#### 3.1 staffing_service.py - 人员查询服务

负责生成人员查询相关的问答数据。

```python
from src.service.staffing_service import generate_staffing_data

# 生成人员查询数据，默认生成5000个样本，每个规则5个变种
staffing_data = generate_staffing_data('searchStaff', total_samples=5000, variations_per_rule=5)
```

#### 3.2 staffing_update_service.py - 人员更新服务

负责生成人员安排更新相关的问答数据。

```python
from src.service.staffing_update_service import generate_update_staffing_data

# 生成人员更新数据，默认生成8000个样本，每个规则5个变种
staffing_update_data = generate_update_staffing_data('updateStaff', total_samples=8000, variations_per_rule=5)
```

#### 3.3 cargo_update_service.py - 货单更新服务

负责生成货单更新相关的问答数据。

```python
from src.service.cargo_update_service import generate_update_cargo_data

# 生成货单更新数据，默认生成10000个样本，每个规则5个变种
cargo_update_data = generate_update_cargo_data('updateCargo', total_samples=10000, variations_per_rule=5)
```

#### 3.4 contract_search_service.py - 合同查询服务

负责生成合同查询相关的问答数据。

```python
from src.service.contract_search_service import generate_search_contract_data

# 生成合同查询数据，默认生成30000个样本，每个规则5个变种
contract_search_data = generate_search_contract_data('searchContract', total_samples=30000, variations_per_rule=5)
```

### 4. common目录 - 基础服务模块

common目录包含各种基础服务模块，提供数据访问和基础功能：

- **base_elements.py**: 基础元素服务，负责读取src/entity/baseElements/目录中的基础元素数据
- **answer_elements.py**: 回答元素服务，负责读取src/entity/answerElements/目录中的回答元素数据
- **business_rules.py**: 业务规则服务，负责读取src/entity/relationship/目录中的业务规则数据
- **dict.py**: 字典服务，负责读取src/dict/目录中的字典数据
- **tools.py**: 工具函数，提供文件读取等通用功能
- **base_generation_service.py**: 基础生成服务，提供问答数据生成的基本功能
- **variation_generation_service.py**: 变种生成服务，用于生成多样化的问题变体 