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

### 2. common目录 - 基础服务模块

common目录包含各种基础服务模块，提供数据访问和基础功能：

- **base_elements.py**: 基础元素服务，负责读取src/entity/baseElements/目录中的基础元素数据
- **answer_elements.py**: 回答元素服务，负责读取src/entity/answerElements/目录中的回答元素数据
- **business_rules.py**: 业务规则服务，负责读取src/entity/relationship/目录中的业务规则数据
- **dict.py**: 字典服务，负责读取src/dict/目录中的字典数据
- **tools.py**: 工具函数，提供文件读取等通用功能 