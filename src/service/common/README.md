# src/service/common 目录说明文档

本目录提供项目通用服务模块，包含各种可复用的工具函数和服务类。

## 目录结构

```
src/service/common/
├── __init__.py    # 包初始化文件，导出主要函数
├── dict.py        # 字典服务模块
└── README.md      # 本文档
```

## 模块说明

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
print(f"可用字典: {dicts}")  # 输出：可用字典: ['drawings', 'vendors', 'materials', 'projects']
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

### __init__.py

包初始化文件，导出主要函数，方便外部直接从包中导入。

导出的函数：
- `get_dict`
- `get_available_dicts`
- `get_dict_service`

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