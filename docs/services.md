# 100.AI.TrainData 服务层文档

## 服务层概述

100.AI.TrainData项目的服务层位于`src/service`目录，提供了一系列用于数据生成、转换和处理的服务类。这些服务类封装了从规则文件到结构化训练数据的转换逻辑，使项目能够高效地生成符合不同业务场景需求的训练数据。

服务层采用了面向对象的设计模式，通过基类和子类的继承关系，实现了代码的复用和扩展。主要组件包括：

- **BaseGenerationService**: 数据生成的基础服务类，提供通用的数据生成逻辑
- **VariationGenerationService**: 变种生成服务，提供多样化数据生成的逻辑
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

## VariationGenerationService 详解

### 功能描述

`VariationGenerationService`是变种生成服务类，位于`src/service/common/variation_generation_service.py`。它继承自`BaseGenerationService`，提供更专注的变种生成功能。该服务负责处理如何根据规则的特性生成多样化的数据变种，特别是在可能变种数量与分配份额不匹配的情况下提供了智能处理策略。

### 与基类的关系

`VariationGenerationService`继承了`BaseGenerationService`，并对变种生成相关的方法进行了扩展和优化。它提供了更精细的变种生成控制和灵活的配置选项。

### 核心方法

1. **generate_question_with_variations**: 生成带变种的问题数据
    ```python
    def generate_question_with_variations(self, rule: Dict, base_elements: Dict, num_variations: int = 1) -> Dict:
        """生成带变种的问题数据"""
        # ...
    ```

2. **generate_variations**: 为一个规则生成多个变种数据
    ```python
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                           num_variations: int = 2) -> List[Dict]:
        """为一个规则生成多个变种数据"""
        # ...
    ```

3. **calculate_possible_variations**: 计算一个规则可能的变种数量
    ```python
    def calculate_possible_variations(self, rule: Dict, base_elements: Dict) -> int:
        """计算一个规则可能的变种数量，基于codeList的元素组合"""
        # ...
    ```

4. **generate_data**: 生成指定业务对象的数据，支持变种生成
    ```python
    def generate_data(self, business_object: str, total_samples: int = 200, 
                     variations_per_rule: int = 2) -> List[Dict]:
        """生成指定业务对象的数据，支持变种生成"""
        # ...
    ```

### 变种生成策略

`VariationGenerationService`实现了两种主要的变种生成策略，根据可能变种数量与份额的关系动态选择：

1. **当可能变种数量小于份额时**:
   - 计算需要重复生成的次数: `repeat_times = max(1, int(share / possible_variations))`
   - 多次生成变种并合并，直到满足份额要求
   - 如果生成的数据仍不足，随机复制已有数据
   - 如果生成的数据超过份额，随机抽样至目标数量

2. **当可能变种数量大于或等于份额时**:
   - 根据可能变种数量、份额和配置参数动态计算生成变种数量
   - 特殊处理可能变种数量远大于份额的情况，增加变种数量以提高数据多样性
   - 根据计算的变种数量生成数据，必要时进行随机抽样

### 配置参数

`VariationGenerationService`的行为受以下配置参数控制（位于`src/config/generation_settings.yml`）：

| 参数名 | 默认值 | 说明 |
|-------|-------|------|
| variation_ratio_factor | 1.2 | 变种比例因子：当可能变种数量超过份额但不超过份额的这个倍数时，使用变种数量 |
| min_data_count | 8 | 最小数据量：确保生成的数据不少于此数量 |
| far_greater_factor | 2.0 | 远大于因子：当可能变种数量超过份额的这个倍数时，认为变种潜力远大于份额 |
| variation_multiplier | 2.0 | 变种倍增因子：当变种潜力远大于份额时，变种数量的倍增系数 |

### 主要特性

1. **智能份额分配**：根据规则权重合理分配数据生成份额。
2. **动态变种生成**：根据规则的特性和配置参数智能决定变种生成策略。
3. **变种不足处理**：当规则的可能变种数量不足时，通过多次生成和必要时的随机复制，确保满足份额要求。
4. **数据多样性保证**：通过随机选择和组合，确保生成数据的多样性。
5. **配置驱动**：通过配置文件控制变种生成行为，无需修改代码即可调整策略。

有关变种生成逻辑的详细说明，请参阅[变种生成逻辑详解](variation_generation.md)文档。

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

## ContractSearchService 详解

### 功能描述

`ContractSearchService`是合同搜索服务，位于`src/service/contract_search_service.py`。它继承自`BaseGenerationService`，用于根据规则生成合同搜索的问题和答案，主要应用于`searchContract`业务对象。该服务负责处理合同相关的搜索数据生成，包括合同号、供应商、材料等信息。

### 与基类的关系

`ContractSearchService`继承了`BaseGenerationService`，并重写了以下关键方法：
- `process_dict_replacement`: 处理字典替换逻辑，特别是对业务单号的处理
- `generate_answer`: 生成答案数据，特别是对供应商信息的提取
- `generate_variations`: 确保使用自身的`generate_answer`方法，而非基类方法

### 特殊实现

1. **供应商名称提取**

`ContractSearchService`实现了专门的供应商名称提取功能，通过正则表达式从供应商信息中提取真正的供应商名称：

```python
def extract_supplier_name(self, supplier_info: str) -> str:
    """从供应商信息中提取真正的供应商名称"""
    # 使用单一的正则表达式替换掉所有可能的前缀和后缀
    # 前缀: 供应商(是)? 或 厂家(是)? 或 是
    # 后缀: 的 或 供应商 或 厂家
    supplier = re.sub(r'^供应商(是)?|^厂家(是)?|(供应商|厂家|的)$|^是|(的)$', '', supplier_info)
    return supplier.strip()
```

此方法可以处理多种形式的供应商信息：
- "供应商湖南装饰材料有限公司" → "湖南装饰材料有限公司"
- "湖南装饰材料有限公司供应商" → "湖南装饰材料有限公司"
- "供应商是湖南装饰材料有限公司" → "湖南装饰材料有限公司"
- "厂家湖南装饰材料有限公司" → "湖南装饰材料有限公司"
- "是湖南装饰材料有限公司的" → "湖南装饰材料有限公司"

2. **字典替换处理**

该服务重写了`process_dict_replacement`方法，增加了对业务单号字典的处理：

```python
def process_dict_replacement(self, element_name, current_value, dict_mapping, dict_item):
    """重写字典替换处理方法，增加对特定字典的处理"""
    # 首先调用父类方法，尝试基本处理
    result = super().process_dict_replacement(element_name, current_value, dict_mapping, dict_item)
    if result:
        return result
        
    # 处理业务单号字典（适用于contractNumber和materialCode）
    if 'businessNumbers' in dict_mapping and 'XX' in current_value:
        business_number = dict_item.get('number', "")
        if business_number:
            # 替换XX部分为业务单号
            new_value = current_value.replace('XX', business_number)
            return new_value
            
    return None
```

3. **生成变种数据**

为了确保正确处理供应商信息，该服务重写了`generate_variations`方法，确保使用`ContractSearchService`自身的`generate_answer`方法，而不是父类的方法：

```python
def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                       num_variations: int = 2) -> List[Dict]:
    """重写为一个规则生成多个变种数据的方法，确保使用ContractSearchService的generate_answer方法"""
    variations = []
    
    # 生成指定数量的变种
    for _ in range(num_variations):
        # 生成问题数据
        question_data = self.generate_question(rule, base_elements)
        
        # 获取基础元素列表
        base_data_list = base_elements.get('baseDataList', [])
        
        # 生成答案数据 - 使用ContractSearchService的generate_answer方法
        answer_data = self.generate_answer(question_data, answer_elements, base_data_list)
        
        # 添加到变种列表
        variations.append({
            'question': question_data,
            'answer': answer_data,
            'rule_id': rule.get('id', ''),
            'rule_name': rule.get('name', '')
        })
    
    return variations
```

### 核心方法

1. **extract_supplier_name**: 从供应商信息中提取供应商名称
    ```python
    def extract_supplier_name(self, supplier_info: str) -> str:
        """从供应商信息中提取真正的供应商名称"""
        # ...
    ```

2. **process_dict_replacement**: 处理字典替换
    ```python
    def process_dict_replacement(self, element_name, current_value, dict_mapping, dict_item):
        """重写字典替换处理方法，增加对特定字典的处理"""
        # ...
    ```

3. **generate_answer**: 生成答案数据
    ```python
    def generate_answer(self, question_data: Dict, answer_elements: Dict, base_elements: List) -> Dict:
        """重写生成答案数据的方法，处理静态值"""
        # ...
    ```

4. **generate_contract_search_data**: 生成合同搜索数据
    ```python
    def generate_contract_search_data(self, business_object: str = BUSINESS_OBJECT, 
                               total_samples: int = 200, 
                               variations_per_rule: int = 2) -> List[Dict]:
        """生成合同搜索数据"""
        return self.generate_data(business_object, total_samples, variations_per_rule)
    ```

5. **generate_variations**: 生成变种数据
    ```python
    def generate_variations(self, rule: Dict, base_elements: Dict, answer_elements: Dict, 
                       num_variations: int = 2) -> List[Dict]:
        """重写为一个规则生成多个变种数据的方法，确保使用ContractSearchService的generate_answer方法"""
        # ...
    ```

### 便捷函数

1. **get_contract_search_service**: 获取合同搜索服务的单例实例
    ```python
    def get_contract_search_service() -> ContractSearchService:
        """获取合同搜索服务的单例实例"""
        # ...
    ```

2. **generate_contract_search_data**: 便捷方法，用于快速生成合同搜索数据
    ```python
    def generate_contract_search_data(business_object: str, total_samples: int = 50, 
                                 variations_per_rule: int = 10) -> List[Dict]:
        """生成合同搜索数据的便捷方法"""
        # ...
    ```

### 修复记录

2023年11月：修复了`generate_variations`方法，确保使用`ContractSearchService`的`generate_answer`方法而非基类方法，解决了在生成训练数据时`supplier`字段无法被正确处理的问题。在修复前，当存在`supplierInfo`字段时，无法正确提取`supplier`字段值。 