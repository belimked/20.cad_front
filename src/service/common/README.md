# src/service/common 目录说明文档

本目录提供项目通用服务模块，包含各种可复用的工具函数和服务类。

## 目录结构

```
src/service/common/
├── __init__.py          # 包初始化文件，导出主要函数
├── dict.py              # 字典服务模块
├── base_elements.py     # 基础元素服务模块
├── answer_elements.py   # 回答元素服务模块
├── business_rules.py    # 业务规则服务模块
├── tools.py             # 通用工具模块
└── README.md            # 本文档
```

## 模块说明

### tools.py

通用工具模块，提供JSON文件读取、路径处理等通用功能。

#### 对外提供的方法

##### `get_base_path(relative_dir: str) -> str`

获取指定目录的绝对路径。

参数：
- `relative_dir`: 相对于src目录的路径，如 'dict', 'rules' 等

返回：
- 指定目录的绝对路径

使用示例：
```python
from service.common import get_base_path

# 获取rules目录的路径
rules_path = get_base_path('rules')
print(f"Rules目录路径: {rules_path}")
```

##### `load_json_file(file_path: str) -> Any`

加载JSON文件。

参数：
- `file_path`: JSON文件的路径

返回：
- JSON文件解析后的对象，加载失败则返回None

使用示例：
```python
from service.common import load_json_file

# 加载配置文件
config = load_json_file('/path/to/config.json')
if config:
    print("配置加载成功")
else:
    print("配置加载失败")
```

##### `load_index_file(base_dir: str, index_filename: str = "index.json") -> Dict[str, Dict]`

加载索引文件，转换为以文件名(不含扩展名)为键的字典。

参数：
- `base_dir`: 索引文件所在的目录
- `index_filename`: 索引文件名，默认为index.json

返回：
- 以文件名(不含扩展名)为键的字典

使用示例：
```python
from service.common import get_base_path, load_index_file

# 加载rules目录下的索引
rules_path = get_base_path('rules')
rules_index = load_index_file(rules_path)
print(f"可用规则: {list(rules_index.keys())}")
```

##### `load_indexed_file(base_dir: str, file_name: str) -> Any`

根据文件名加载指定目录下的JSON文件。

参数：
- `base_dir`: 文件所在的基础目录
- `file_name`: 文件名(不含扩展名)

返回：
- JSON文件解析后的对象，加载失败则返回None

使用示例：
```python
from service.common import get_base_path, load_indexed_file

# 加载rules目录下的特定规则文件
rules_path = get_base_path('rules')
rule_data = load_indexed_file(rules_path, 'searchContract')
if rule_data:
    print(f"规则加载成功: {rule_data['name']}")
```

### dict.py

字典服务模块，用于读取和管理项目中的字典数据。该模块从`src/dict`目录下读取索引文件和字典文件，提供对外访问接口。

#### 主要类

**DictService**

字典服务类，实现单例模式，负责加载和缓存字典数据。

#### 对外提供的方法

##### `get_dict(dict_name: str, count: int = 0, random_select: bool = True) -> List[Dict]`

获取指定字典的内容。

参数：
- `dict_name`：字典名称，不含扩展名(如 vendors, projects 等)
- `count`：需要获取的数量，0表示获取全部
- `random_select`：是否随机选取，默认为True

返回：
- 字典内容的列表

使用示例：
```python
from service.common import get_dict

# 随机获取5个供应商
vendors = get_dict('vendors', 5)

# 获取所有项目
projects = get_dict('projects')

# 获取前10个材料（不随机）
materials = get_dict('materials', 10, random_select=False)
```

##### `get_dict_by_element_mapping(dict_mapping: str, count: int = 0, random_select: bool = True) -> List[Dict]`

根据元素字典映射获取字典数据，支持通过基础元素的dictlist属性指定的映射关系获取对应字典数据。

参数：
- `dict_mapping`：字典映射字符串，格式为"元素编号:字典名称"，如"04:persons"、"05:projects"、"13:staffNumbers"
- `count`：需要获取的数量，0表示获取全部
- `random_select`：是否随机选取，默认为True

返回：
- 字典内容的列表，如果映射无效则返回空列表

使用示例：
```python
from service.common import get_dict_by_element_mapping

# 通过人员元素映射获取5个随机人员数据
persons = get_dict_by_element_mapping('04:persons', 5)
print(f"随机5个人员: {persons}")

# 通过项目元素映射获取所有项目数据
projects = get_dict_by_element_mapping('05:projects')
print(f"项目总数: {len(projects)}")

# 通过工号元素映射获取3个工号（不随机）
staff_numbers = get_dict_by_element_mapping('13:staffNumbers', 3, random_select=False)
print(f"工号数据: {staff_numbers}")
```

##### `get_available_dicts() -> List[str]`

获取所有可用的字典名称。

参数：无

返回：
- 可用字典名称的列表

使用示例：
```python
from service.common import get_available_dicts

# 获取所有可用字典
dicts = get_available_dicts()
print(f"可用字典: {dicts}")  # 输出：可用字典: ['drawings', 'vendors', 'materials', 'projects', 'persons', 'staffNumbers']
```

##### `get_dict_service() -> DictService`

获取字典服务的单例实例，通常不需要直接使用此方法，除非需要访问DictService类的特定方法。

参数：无

返回：
- DictService实例

使用示例：
```python
from service.common import get_dict_service

# 获取字典服务实例
service = get_dict_service()

# 获取特定字典的详细信息
dict_info = service.get_dict_info('vendors')
print(dict_info)  # 输出字典的元数据信息
```

### base_elements.py

基础元素服务模块，用于读取和管理项目中的基础元素数据。该模块从`src/entity/baseElements`目录下读取基础元素定义文件，提供对外访问接口。

#### 主要类

**BaseElementsService**

基础元素服务类，实现单例模式，负责加载和缓存基础元素数据。

#### 对外提供的方法

##### `get_base_elements(business_object: str) -> Dict`

获取指定业务对象的基础元素内容。

参数：
- `business_object`：业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)

返回：
- 基础元素内容的字典，包含businessObject和baseDataList字段

使用示例：
```python
from service.common import get_base_elements

# 获取人员查询的基础元素
staff_search_elements = get_base_elements('searchStaff')
if staff_search_elements:
    # 获取基础数据要素列表
    base_data_list = staff_search_elements.get('baseDataList', [])
    # 处理基础数据要素
    for item in base_data_list:
        print(f"要素名称: {item['name']}, 编号: {item['number']}")
```

##### `get_available_base_elements() -> List[str]`

获取所有可用的基础元素业务对象名称。

参数：无

返回：
- 基础元素业务对象名称的列表

使用示例：
```python
from service.common import get_available_base_elements

# 获取所有可用的基础元素业务对象
business_objects = get_available_base_elements()
print(f"可用基础元素业务对象: {business_objects}")  # 输出：可用基础元素业务对象: ['searchStaff', 'updateStaff', ...]
```

##### `get_base_elements_service() -> BaseElementsService`

获取基础元素服务的单例实例，通常不需要直接使用此方法，除非需要访问BaseElementsService类的特定方法。

参数：无

返回：
- BaseElementsService实例

使用示例：
```python
from service.common import get_base_elements_service

# 获取基础元素服务实例
service = get_base_elements_service()

# 获取特定业务对象的详细信息
business_object_info = service.get_base_elements_info('searchStaff')
print(business_object_info)  # 输出业务对象的元数据信息
```

### answer_elements.py

回答元素服务模块，用于读取和管理项目中的回答元素数据。该模块从`src/entity/answerElements`目录下读取回答元素定义文件，提供对外访问接口。

#### 主要类

**AnswerElementsService**

回答元素服务类，实现单例模式，负责加载和缓存回答元素数据。

#### 对外提供的方法

##### `get_answer_elements(business_object: str) -> Dict`

获取指定业务对象的回答元素内容。

参数：
- `business_object`：业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)

返回：
- 回答元素内容的字典，包含answerObject和answerElements字段

使用示例：
```python
from service.common import get_answer_elements

# 获取人员查询的回答元素
staff_search_answers = get_answer_elements('searchStaff')
if staff_search_answers:
    # 获取回答要素列表
    answer_elements_list = staff_search_answers.get('answerElements', [])
    # 处理回答要素
    for item in answer_elements_list:
        print(f"要素名称: {item['name']}, 中文名称: {item['nameCN']}, 关联基础要素: {item['relateToBase']}")
```

##### `get_available_answer_elements() -> List[str]`

获取所有可用的回答元素业务对象名称。

参数：无

返回：
- 回答元素业务对象名称的列表

使用示例：
```python
from service.common import get_available_answer_elements

# 获取所有可用的回答元素业务对象
business_objects = get_available_answer_elements()
print(f"可用回答元素业务对象: {business_objects}")  # 输出：可用回答元素业务对象: ['searchStaff', 'updateStaff', ...]
```

##### `get_answer_elements_service() -> AnswerElementsService`

获取回答元素服务的单例实例，通常不需要直接使用此方法，除非需要访问AnswerElementsService类的特定方法。

参数：无

返回：
- AnswerElementsService实例

使用示例：
```python
from service.common import get_answer_elements_service

# 获取回答元素服务实例
service = get_answer_elements_service()

# 获取特定业务对象的详细信息
business_object_info = service.get_answer_elements_info('searchStaff')
print(business_object_info)  # 输出业务对象的元数据信息
```

### business_rules.py

业务规则服务模块，用于读取和管理项目中的业务规则数据。该模块从`src/entity/relationship`目录下读取业务规则定义文件，提供对外访问接口。

#### 主要类

**BusinessRulesService**

业务规则服务类，实现单例模式，负责加载和缓存业务规则数据。

#### 对外提供的方法

##### `get_business_rules(business_object: str) -> Dict`

获取指定业务对象的业务规则内容。

参数：
- `business_object`：业务对象名称，不含扩展名(如 searchStaff, updateStaff 等)

返回：
- 业务规则内容的字典

使用示例：
```python
from service.common import get_business_rules

# 获取人员查询的业务规则
staff_search_rules = get_business_rules('searchStaff')
if staff_search_rules:
    # 处理业务规则
    # 注意：具体结构取决于规则定义文件的格式
    print(f"业务规则: {staff_search_rules}")
```

##### `get_available_business_rules() -> List[str]`

获取所有可用的业务规则对象名称。

参数：无

返回：
- 业务规则对象名称的列表

使用示例：
```python
from service.common import get_available_business_rules

# 获取所有可用的业务规则对象
rule_objects = get_available_business_rules()
print(f"可用业务规则对象: {rule_objects}")  # 输出：可用业务规则对象: ['searchStaff', 'updateStaff', ...]
```

##### `get_business_rules_service() -> BusinessRulesService`

获取业务规则服务的单例实例，通常不需要直接使用此方法，除非需要访问BusinessRulesService类的特定方法。

参数：无

返回：
- BusinessRulesService实例

使用示例：
```python
from service.common import get_business_rules_service

# 获取业务规则服务实例
service = get_business_rules_service()

# 获取特定业务对象的详细信息
business_object_info = service.get_business_rules_info('searchStaff')
print(business_object_info)  # 输出业务对象的元数据信息
```

### __init__.py

包初始化文件，导出主要函数，方便外部直接从包中导入。

导出的函数：
- 字典服务函数: `get_dict`, `get_available_dicts`, `get_dict_service`, `get_dict_by_element_mapping`
- 基础元素服务函数: `get_base_elements`, `get_available_base_elements`, `get_base_elements_service`
- 回答元素服务函数: `get_answer_elements`, `get_available_answer_elements`, `get_answer_elements_service`
- 业务规则服务函数: `get_business_rules`, `get_available_business_rules`, `get_business_rules_service`
- 通用工具函数: `get_base_path`, `load_json_file`, `load_index_file`, `load_indexed_file`

## 使用场景

1. **数据生成和测试**：获取随机的字典数据用于测试或演示
   ```python
   from service.common import get_dict
   
   # 随机获取10个项目用于测试
   test_projects = get_dict('projects', 10)
   ```

2. **前端下拉选择框数据源**：获取字典数据用于前端下拉框
   ```python
   from service.common import get_dict
   
   # 获取所有供应商作为下拉选择项
   vendors = get_dict('vendors')
   vendor_options = [{"value": v["vendorid"], "label": v["vendorname"]} for v in vendors]
   ```

3. **数据验证**：检查输入的ID是否在字典中存在
   ```python
   from service.common import get_dict
   
   def validate_vendor(vendor_id):
       vendors = get_dict('vendors')
       valid_ids = [v["vendorid"] for v in vendors]
       return vendor_id in valid_ids
   ```

4. **通用JSON文件读取**：从不同目录读取JSON文件
   ```python
   from service.common import get_base_path, load_indexed_file
   
   # 加载规则文件
   rules_path = get_base_path('rules')
   rule_data = load_indexed_file(rules_path, 'searchContract')
   
   # 处理规则数据
   if rule_data:
       process_rule(rule_data)
   ```

5. **获取业务对象基础元素**：获取特定业务对象的基础元素定义
   ```python
   from service.common import get_base_elements
   
   # 获取人员查询的基础元素
   search_staff_elements = get_base_elements('searchStaff')
   
   # 分析人员查询的基础数据要素
   if search_staff_elements:
       base_data_list = search_staff_elements.get('baseDataList', [])
       for element in base_data_list:
           element_name = element['name']
           element_number = element['number']
           variants = element['conditionList']
           print(f"要素 {element_number}: {element_name}, 变体数量: {len(variants)}")
   ```

6. **获取业务对象回答元素**：获取特定业务对象的回答元素定义
   ```python
   from service.common import get_answer_elements
   
   # 获取人员查询的回答元素
   search_staff_answers = get_answer_elements('searchStaff')
   
   # 分析人员查询的回答要素
   if search_staff_answers:
       answer_elements_list = search_staff_answers.get('answerElements', [])
       for element in answer_elements_list:
           element_name = element['name']
           element_cn_name = element['nameCN']
           relate_to_base = element['relateToBase']
           is_static = element['isStatic'] == '是'
           print(f"要素: {element_name} ({element_cn_name}), 关联基础要素: {relate_to_base}, 是否静态: {is_static}")
   ```

7. **获取业务对象规则**：获取特定业务对象的业务规则定义
   ```python
   from service.common import get_business_rules
   
   # 获取人员查询的业务规则
   search_staff_rules = get_business_rules('searchStaff')
   
   # 处理业务规则数据
   if search_staff_rules:
       # 业务规则的具体处理方式取决于规则的结构
       print(f"规则数据: {search_staff_rules}")
   ```

8. **综合使用多种服务**：结合基础元素、回答元素和业务规则生成完整的训练数据
   ```python
   from service.common import get_base_elements, get_answer_elements, get_business_rules, get_dict
   
   # 获取基础元素、回答元素和业务规则
   base_elements = get_base_elements('searchStaff')
   answer_elements = get_answer_elements('searchStaff')
   business_rules = get_business_rules('searchStaff')
   
   # 获取随机项目数据作为填充
   projects = get_dict('projects', 5)
   
   # 使用这些数据生成训练样本
   if base_elements and answer_elements and projects:
       # 示例实现 - 具体逻辑取决于实际需求
       # 使用基础元素生成问题，使用回答元素生成回答框架，使用业务规则验证生成的问答对
       pass
   ```

9. **通过元素映射获取字典数据**：使用基础元素的dictlist属性获取对应字典数据
   ```python
   from service.common import get_dict_by_element_mapping, get_base_elements
   
   # 获取基础元素
   base_elements = get_base_elements('updateStaff')
   if base_elements:
       base_data_list = base_elements.get('baseDataList', [])
       
       # 找到包含dictlist的元素
       for element in base_data_list:
           if element.get('dictlist'):
               element_number = element.get('number')
               element_name = element.get('name')
               dict_mapping = element.get('dictlist')[0]  # 获取第一个映射
               
               # 通过元素映射获取字典数据
               dict_data = get_dict_by_element_mapping(dict_mapping, 3)
               print(f"元素 {element_number}({element_name}) 通过映射 {dict_mapping} 获取数据: {dict_data}")
   ``` 