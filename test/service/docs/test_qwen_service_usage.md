# test_qwen_service.py 使用文档

## 概述

`test_qwen_service.py`是一个用于测试和生成千问服务训练数据的脚本。该脚本可以批量生成不同业务对象（如人员查询、人员更新、货单更新、合同查询）的问答对，并将其保存为符合千问训练格式的JSONL文件。

## 功能特点

1. **多业务对象数据生成**：支持生成多种业务对象的数据，包括：
   - updateStaff（人员更新）
   - searchStaff（人员查询）
   - updateCargo（货单更新）
   - searchContract（合同查询）

2. **数据过滤**：支持通过关键字过滤数据，便于生成特定场景的训练数据

3. **自动保存**：将生成的数据自动保存为JSONL格式，符合大模型训练的标准格式

4. **数据统计**：提供详细的数据统计信息，包括字段分析和关键字匹配情况

## 最近更新

- **增大样本数量**：优化了各业务对象的默认样本数量
  - updateStaff: 8,000个样本
  - searchStaff: 5,000个样本
  - updateCargo: 10,000个样本
  - searchContract: 30,000个样本

- **优化过滤逻辑**：改进了关键字过滤机制，使过滤更加精准

- **修复输出路径**：修复了文件保存路径问题，现在文件将正确保存到项目根目录的`outputs/data/`目录下

## 使用方法

### 基本使用

```bash
# 进入项目根目录
cd /path/to/100.AI.TrainData

# 设置PYTHONPATH
export PYTHONPATH=/path/to/100.AI.TrainData

# 使用默认关键字运行
python test/service/test_qwen_service.py

# 使用自定义关键字运行
python test/service/test_qwen_service.py "关键字1,关键字2,关键字3"
```

### 参数说明

- **无参数**：使用默认关键字`最近,天,周,月,季度`进行过滤
- **关键字参数**：提供逗号分隔的关键字列表，用于过滤生成的数据

### 输出说明

脚本执行完成后，将在控制台输出以下信息：

1. 各业务对象生成的样本数量
2. 关键字过滤情况统计
3. 最终生成的文件信息，包括：
   - 文件路径
   - 文件大小
   - 记录数量

所有生成的数据将保存在项目根目录的`outputs/data/`目录下，文件名格式为`qwen_data_YYYYMMDD_HHMMSS.jsonl`。

## 代码示例

以下是如何在代码中集成该功能的示例：

```python
# 导入所需的函数
from test.service.test_qwen_service import test_generate_staffing_data, save_to_jsonl
import random

# 收集所有业务对象的数据
all_dialogs = []

# 生成updateStaff数据
updateStaff_dialogs = test_generate_staffing_data('updateStaff', totalSamples=8000, 
                                                  variations_per_rule=5, collect_data=True)
all_dialogs.extend(updateStaff_dialogs)

# 生成searchStaff数据
searchStaff_dialogs = test_generate_staffing_data('searchStaff', totalSamples=5000, 
                                                  variations_per_rule=5, collect_data=True)
all_dialogs.extend(searchStaff_dialogs)

# 数据打乱和保存
random.shuffle(all_dialogs)
output_dir = "outputs/data"
jsonl_file = save_to_jsonl(all_dialogs, output_dir)
print(f"数据已保存到: {jsonl_file}")
```

## 注意事项

1. 确保已正确设置`PYTHONPATH`，否则可能导致模块导入错误
2. 首次运行可能需要较长时间生成数据，请耐心等待
3. 生成的JSONL文件可能较大，请确保有足够的磁盘空间
4. 如需自定义样本数量，需修改脚本中的相关参数

## 常见问题

### Q: 为什么没有看到生成的文件？

A: 请检查以下几点：
- 确认脚本是否成功执行完毕
- 检查`outputs/data/`目录是否存在
- 检查是否有足够的权限创建和写入文件

### Q: 如何调整生成的样本数量？

A: 修改脚本中的以下变量：
- `update_staff_samples`
- `search_staff_samples`
- `update_cargo_samples`
- `search_contract_samples`

### Q: 如何过滤特定时间范围的数据？

A: 使用与时间相关的关键字，例如：
```bash
python test/service/test_qwen_service.py "最近,天,周,月,季度,年"
``` 