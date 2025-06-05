# 100.AI.TrainData 服务层文档

## 服务层概述

100.AI.TrainData项目的服务层位于`src/service`目录，提供了一系列用于数据生成、转换和处理的服务类。这些服务类封装了从规则文件到结构化训练数据的转换逻辑，使项目能够高效地生成符合不同业务场景需求的训练数据。

服务层采用了面向对象的设计模式，通过基类和子类的继承关系，实现了代码的复用和扩展。主要组件包括：

- **BaseGenerationService**: 数据生成的基础服务类，提供通用的数据生成逻辑
- **StaffingService**: 人员安排数据生成服务，继承自BaseGenerationService
- **StaffUpdateService**: 人员安排更新数据生成服务，继承自BaseGenerationService
- **QwenService**: 通义千问格式数据生成服务，整合其他服务的输出

## BaseGenerationService 详解

### 功能描述

`BaseGenerationService`是数据生成服务的基础类，位于`src/service/common/base_generation_service.py`。它封装了数据生成的通用逻辑，为不同的业务场景提供了一致的处理流程。作为`StaffingService`和`StaffUpdateService`的共同父类，它减少了重复代码，提高了系统的可维护性。

### 核心方法

1. **calculate_rule_weights**: 计算规则权重并分配生成份额
    ```python
    def calculate_rule_weights(self, business_object: str, total_samples: int = 200) -> List[Dict]:
        """计算规则权重并分配生成份额"""
        # ...
    ```

2. **generate_base_question**: 生成基础问题数据
    ```python
    def generate_base_question(self, rule: Dict, base_elements: Dict) -> Tuple[Dict, Dict]:
        """生成基础问题数据（两个服务类共享的部分）"""
        # ...
    ```

3. **process_special_elements**: 处理特殊元素（默认实现不做处理，由子类重写）
    ```python
    def process_special_elements(self, question_data: Dict, elements_with_dict: Dict) -> Dict:
        """处理特殊元素，如字典替换等"""
        # 基类默认不做处理，直接返回原始问题数据
        return question_data
    ```

4. **generate_question**: 生成问题数据的模板方法
    ```python
    def generate_question(self, rule: Dict, base_elements: Dict) -> Dict:
        """生成问题数据，模板方法模式"""
        # ...
    ```

5. **generate_answer**: 根据问题数据和回答元素生成答案
    ```python
    def generate_answer(self, question_data: Dict, answer_elements: Dict, base_elements: Dict) -> Dict:
        """根据问题数据和回答元素生成答案"""
        # ...
    ```

6. **generate_variations**: 为一个规则生成指定数量的变种
    ```python
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """为一个规则生成指定数量的变种"""
        # ...
    ```

7. **generate_data**: 生成数据的通用方法
    ```python
    def generate_data(self, business_object: str, total_samples: int = 200, 
                     variations_per_rule: int = 2) -> List[Dict]:
        """生成数据的通用方法"""
        # ...
    ```

### 扩展机制

`BaseGenerationService`通过模板方法模式提供了扩展机制。子类可以重写`process_special_elements`方法来处理特定业务场景下的特殊元素，而不需要修改基类的其他方法。这种设计使得添加新的数据生成服务变得简单，只需要继承`BaseGenerationService`并根据需要重写特定方法。

`generate_answer`方法支持复杂的基础元素映射，包括处理多基础元素映射（用"|"分隔的情况），能够根据问题数据选择合适的值。

## StaffingService 详解

### 功能描述

`StaffingService`是人员安排数据生成服务，位于`src/service/staffing_service.py`。它继承自`BaseGenerationService`，用于根据规则生成人员安排的问题和答案，主要应用于`searchStaff`业务对象。

### 与基类的关系

`StaffingService`直接继承了`BaseGenerationService`的所有方法，并未重写任何方法，这表明它完全依赖基类提供的通用数据生成逻辑。

### 核心方法

1. **generate_staffing_data**: 生成人员安排数据
    ```python
    def generate_staffing_data(self, business_object: str, total_samples: int = 200, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """生成人员安排数据"""
        return self.generate_data(business_object, total_samples, variations_per_rule)
    ```

2. **get_staffing_service**: 获取人员安排服务的单例实例
    ```python
    def get_staffing_service() -> StaffingService:
        """获取人员安排服务的单例实例"""
        # ...
    ```

3. **generate_staffing_data**: 便捷方法，用于快速生成人员安排数据
    ```python
    def generate_staffing_data(business_object: str, total_samples: int = 10, 
                            variations_per_rule: int = 2) -> List[Dict]:
        """生成人员安排数据的便捷方法"""
        # ...
    ```

## StaffUpdateService 详解

### 功能描述

`StaffUpdateService`是人员安排更新数据生成服务，位于`src/service/staff_update_service.py`。它继承自`BaseGenerationService`，用于根据规则生成人员安排更新的问题和答案，主要应用于`updateStaff`业务对象。

### 与基类的关系

`StaffUpdateService`继承了`BaseGenerationService`，并重写了`process_special_elements`方法来处理特定的字典替换逻辑。

### 特殊实现

`StaffUpdateService`的主要特殊实现是字典替换功能，通过重写`process_special_elements`方法来实现：

```python
def process_special_elements(self, question_data: Dict, elements_with_dict: Dict) -> Dict:
    """
    重写特殊元素处理方法，处理字典替换逻辑
    """
    # 处理需要字典替换的元素
    for element_name, data in elements_with_dict.items():
        element = data['element']
        dict_list = data['dict_list']
        
        # 目前值，可能包含XX占位符
        current_value = question_data.get(element_name, "")
        
        # 遍历字典列表
        for dict_mapping in dict_list:
            from src.service.common import get_dict_by_element_mapping
            
            # 获取字典数据
            dict_data = get_dict_by_element_mapping(dict_mapping, 1, True)
            if dict_data and len(dict_data) > 0:
                dict_item = dict_data[0]
                
                # 针对项目字典处理
                if 'projects' in dict_mapping and 'XX' in current_value:
                    project_name = dict_item.get('projectname', "")
                    if project_name:
                        # 替换XX为实际项目名称
                        new_value = current_value.replace('XX', project_name)
                        question_data[element_name] = new_value
                        print(f"替换字典数据: {element_name} 从 {current_value} 到 {new_value}")
                
                # 针对其他字典类型的处理可以在这里添加
    
    return question_data
```

### 核心方法

1. **process_special_elements**: 处理特殊元素，重写基类方法
    ```python
    def process_special_elements(self, question_data: Dict, elements_with_dict: Dict) -> Dict:
        """重写特殊元素处理方法，处理字典替换逻辑"""
        # ...
    ```

2. **generate_staff_update_data**: 生成人员安排更新数据
    ```python
    def generate_staff_update_data(self, business_object: str, total_samples: int = 200, 
                                variations_per_rule: int = 2) -> List[Dict]:
        """生成人员安排更新数据"""
        return self.generate_data(business_object, total_samples, variations_per_rule)
    ```

3. **get_staff_update_service**: 获取人员安排更新服务的单例实例
    ```python
    def get_staff_update_service() -> StaffUpdateService:
        """获取人员安排更新服务的单例实例"""
        # ...
    ```

4. **generate_staff_update_data**: 便捷方法，用于快速生成人员安排更新数据
    ```python
    def generate_staff_update_data(business_object: str, total_samples: int = 10, 
                              variations_per_rule: int = 2) -> List[Dict]:
        """生成人员安排更新数据的便捷方法"""
        # ...
    ```

## QwenService 详解

### 功能描述

`QwenService`是通义千问格式数据生成服务，位于`src/service/qwen_service.py`。它整合了其他数据生成服务的输出，将数据转换为通义千问模型所需的训练格式。

### 数据格式

通义千问格式的数据采用JSONL（JSON Lines）格式，每行一个独立的JSON对象，包含以下结构：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "### 指令：\n你是一个企业信息检索助手，请根据查询内容，返回包含以下字段的标准JSON响应，缺失字段填\"无\"：\n[操作, 对象, 项目, 供应商, 对象状态, 对象提交时间, 对象审核时间, 对象发货时间, 对象下单时间, 材料状态, 材料类型, 材料工艺图, 材料工程属性, 材料所属订单, 材料编号, 对象金额, 对象附加费用, 材料AI金额条件, 对象审核单类型, 材料是否异型, 材料是否超长超宽, 对象单号, 送货单号, 运费, 其他费用, 其他费用说明, 网版费, 人员姓名, 人员工号, 角色信息, 人员项目]\n\n### 查询问题\n{格式化的问题}"
    },
    {
      "role": "assistant",
      "content": "{JSON格式的答案字符串}"
    }
  ]
}
```

### 核心方法

1. **format_question_searchStaff**: 格式化searchStaff的问题数据
    ```python
    def format_question_searchStaff(question_data: Dict) -> str:
        """将searchStaff的问题数据格式化为自然语言"""
        # ...
    ```

2. **format_question_updateStaff**: 格式化updateStaff的问题数据
    ```python
    def format_question_updateStaff(question_data: Dict) -> str:
        """将updateStaff的问题数据格式化为自然语言"""
        # ...
    ```

3. **get_format_question_function**: 获取对应的问题格式化函数
    ```python
    def get_format_question_function(business_object: str) -> Callable[[Dict], str]:
        """根据业务对象获取对应的问题格式化函数"""
        # ...
    ```

4. **get_rule_codebase_searchStaff**: 获取searchStaff的规则codebase
    ```python
    def get_rule_codebase_searchStaff(rules: List[Dict], question: Dict) -> str:
        """根据searchStaff的问题数据获取对应的规则codebase"""
        # ...
    ```

5. **get_rule_codebase_updateStaff**: 获取updateStaff的规则codebase
    ```python
    def get_rule_codebase_updateStaff(rules: List[Dict], question: Dict) -> str:
        """根据updateStaff的问题数据获取对应的规则codebase"""
        # ...
    ```

6. **get_rule_codebase_function**: 获取规则codebase获取函数
    ```python
    def get_rule_codebase_function(business_object: str) -> Callable[[List[Dict], Dict], str]:
        """根据业务对象获取对应的规则codebase获取函数"""
        # ...
    ```

7. **get_data_generator_function**: 获取数据生成函数
    ```python
    def get_data_generator_function(business_object: str) -> Callable[[str, int, int], List[Dict]]:
        """根据业务对象获取对应的数据生成函数"""
        # ...
    ```

8. **get_rule_codebase**: 获取规则codebase
    ```python
    def get_rule_codebase(business_object: str, data: Dict) -> str:
        """根据问题数据获取对应的规则codebase"""
        # ...
    ```

9. **generate_qwen_data**: 生成通义千问训练数据并保存为jsonl文件
    ```python
    def generate_qwen_data(business_object: str, total_samples: int = 100, variations_per_rule: int = 2) -> str:
        """生成通义千问训练数据并保存为jsonl文件"""
        # ...
    ```

### 使用示例

以下是使用QwenService生成数据的典型示例：

```python
# 生成searchStaff的千问训练数据
output_file = generate_qwen_data('searchStaff', 10, 2)
print(f"生成的文件路径: {output_file}")

# 生成updateStaff的千问训练数据
output_file = generate_qwen_data('updateStaff', 10, 2)
print(f"生成的文件路径: {output_file}")
```

生成的数据将保存在`outputs/data/qwen/`目录下，文件名格式为`{business_object}_{actual_count}_{timestamp}.jsonl`，其中`actual_count`是实际生成的数据条数（可能与请求的`total_samples`不同）。 