# 业务服务层文档 (src/services)

[根目录](../../CLAUDE.md) > [核心模块](../CLAUDE.md) > **services**

## 模块概述

**业务服务层 (src/services)** 封装核心业务逻辑，提供高层服务接口，是连接数据模型和应用层的桥梁。

**职责：**
- 封装复杂业务逻辑
- 管理数据库事务
- 提供可复用的服务接口
- 实现业务规则和验证

**设计原则：**
- 单一职责：每个服务专注一个业务领域
- 依赖注入：通过构造函数注入数据库会话
- 事务管理：使用 `db_session()` 上下文管理器
- 无状态服务：避免实例变量存储状态

## 服务列表

| 服务 | 文件 | 职责 | 状态 |
|------|------|------|------|
| **AutoCADConfigService** | `autocad_config_service.py` | AutoCAD 配置管理 | ✅ 完整 |
| **TaskService** | `task_service.py` | DWG 任务管理 | ✅ 完整 |
| **DictService** | `dict_service.py` | 字典配置管理 | ✅ 完整 |
| **OCRLoggingService** | `ocr_logging_service.py` | OCR 识别日志 | ✅ 完整 |
| **MinerUService** | `mineru_service.py` | MinerU PDF 识别 | ✅ 完整 |
| **PDFReorganizeService** | `pdf_reorganize_service.py` | PDF 文件重组织 | 🆕 ⭐ |

## 核心服务详解

### AutoCADConfigService

**文件：** `autocad_config_service.py`

**功能：**
- 查询/创建/更新 AutoCAD 配置
- 解析 JSON 工作流配置
- 验证配置有效性

**主要方法：**

```python
class AutoCADConfigService:
    def get_config_by_name(self, config_name: str) -> AutoCADConfig
    def get_config_by_id(self, config_id: int) -> AutoCADConfig
    def create_config(self, config_data: dict) -> AutoCADConfig
    def update_config(self, config_name: str, updates: dict) -> AutoCADConfig
    def delete_config(self, config_name: str) -> bool
    def list_configs(self, active_only: bool = True) -> List[AutoCADConfig]
```

**使用示例：**

```python
from src.services.autocad_config_service import AutoCADConfigService

service = AutoCADConfigService()
config = service.get_config_by_name("default")
print(config.menu_operations)  # JSON 格式的操作序列
```

---

### TaskService

**文件：** `task_service.py`

**功能：**
- 创建/查询/更新 DWG 处理任务
- 记录任务步骤日志
- 更新任务状态和进度
- 处理任务失败和重试

**任务状态流转：**

```
pending → downloading → processing → completed
                                   ↓
                                 failed
```

**主要方法：**

```python
class TaskService:
    def create_task(self, dwg_url: str, config_name: str, **kwargs) -> DWGProcessTask
    def get_task(self, task_id: str) -> DWGProcessTask
    def update_task_status(self, task_id: str, status: str, progress: int = None) -> None
    def add_task_step(self, task_id: str, step_name: str, step_number: int, status: str, details: str = None) -> DWGTaskStep
    def mark_task_failed(self, task_id: str, error_message: str) -> None
    def mark_task_completed(self, task_id: str) -> None
    def list_tasks(self, status: str = None, limit: int = 50) -> List[DWGProcessTask]
```

**使用示例：**

```python
from src.services.task_service import TaskService

service = TaskService()

# 创建任务
task = service.create_task(
    dwg_url="http://example.com/file.dwg",
    config_name="default",
    use_bplot=True
)

# 更新状态
service.update_task_status(task.task_id, "downloading", progress=10)

# 记录步骤
service.add_task_step(
    task_id=task.task_id,
    step_name="下载文件",
    step_number=1,
    status="success",
    details="文件下载完成"
)
```

---

### DictService

**文件：** `dict_service.py`

**功能：**
- 查询字典配置数据
- 获取 OCR 预处理配置
- 提供配置实时查询（无缓存）

**主要方法：**

```python
class DictionaryService:
    @staticmethod
    def get_preprocessing_config(dict_key: str) -> dict

    @staticmethod
    def get_config_list(dict_key: str, default: list = None) -> list

    @staticmethod
    def get_config_dict(dict_key: str, default: dict = None) -> dict
```

**使用示例：**

```python
from src.services.dict_service import DictionaryService

# 获取预处理配置
config = DictionaryService.get_preprocessing_config('default_preprocessing')

# 获取列表配置（如材料关键字）
keywords = DictionaryService.get_config_list(
    'extraction_material_keywords',
    default=['材料:', 'Material:']
)

# 获取字典配置（如提取规则）
rules = DictionaryService.get_config_dict(
    'extraction_rules',
    default={'min_chinese_chars': 4}
)
```

---

### OCRLoggingService

**文件：** `ocr_logging_service.py`

**功能：**
- 记录 OCR 识别日志
- 查询历史识别记录
- 统计识别成功率

**主要方法：**

```python
class OCRLoggingService:
    def log_ocr_recognition(
        self,
        config_name: str,
        target_text: str,
        screenshot_path: str,
        ocr_result: dict,
        status: str,
        **kwargs
    ) -> OCRRecognitionLog

    def get_recent_logs(self, limit: int = 20) -> List[OCRRecognitionLog]

    def get_success_rate(self, config_name: str = None) -> float
```

**使用示例：**

```python
from src.services.ocr_logging_service import OCRLoggingService

service = OCRLoggingService()

# 记录识别结果
service.log_ocr_recognition(
    config_name='default',
    target_text='批量打印',
    screenshot_path='/path/to/screenshot.png',
    ocr_result={"data": [...], "code": 100},
    status='success'
)

# 查询最近日志
logs = service.get_recent_logs(limit=10)
for log in logs:
    print(f"{log.target_text}: {log.status}")
```

---

### MinerUService

**文件：** `mineru_service.py`

**功能：**
- 批量 PDF 识别（MinerU API）
- 提取图号、标题、表格数据
- 并发处理提升性能
- **自动触发 PDF 文件重组织** 🆕

**性能优化：**
- 使用 ThreadPoolExecutor 并发处理
- 线程安全的数据库会话
- 单个 PDF 独立请求 API
- 性能提升：10 个 PDF 从 37.5s → ~12s

**主要方法：**

```python
class MinerUService:
    def __init__(self, config: AutoCADConfig, task_id: str, db_session)

    def batch_recognize_pdfs(
        self,
        pdf_directory: str,
        pdf_pattern: str = '*.pdf'
    ) -> Dict[str, Any]
    # 返回格式：
    # {
    #     'success': True/False,
    #     'total_files': int,
    #     'success_count': int,
    #     'failed_count': int,
    #     'results': [...],
    #     'reorganize_stats': {...}  # 🆕 重组织结果
    # }
```

**识别流程：**

```
1. 收集 PDF 文件 → 2. 并发调用 MinerU API → 3. 解析识别结果
   ↓
4. 保存数据库 (DWGRecognitionResult + DWGDrawingSheet)
   ↓
5. 自动触发重组织 (auto_reorganize_pdfs=True) 🆕
```

**使用示例：**

```python
from src.services.mineru_service import MinerUService

service = MinerUService(config=autocad_config, task_id=task_id, db_session=db)
result = service.batch_recognize_pdfs(pdf_directory='./output')

print(f"识别成功: {result['success_count']} 个")
print(f"重组织完成: {result['reorganize_stats']['completed']} 个")
```

---

### PDFReorganizeService 🆕 ⭐

**文件：** `pdf_reorganize_service.py`

**功能：**
- 根据图号重命名 PDF 文件
- 创建转换目录（`xxx_convert`）
- 处理文件名冲突（追加序号）
- 更新数据库转换记录

**核心特性：**
- 单一职责：专注文件重组织逻辑
- 事务安全：统一提交/回滚
- 冲突处理：自动追加 `_1`, `_2`...
- 权限继承：自动继承源目录权限

**主要方法：**

```python
class PDFReorganizeService:
    def __init__(self, db_session)

    def reorganize_pdfs(
        self,
        drawing_sheets: List[DWGDrawingSheet],
        source_directory: str
    ) -> Dict[str, Any]
    # 返回格式：
    # {
    #     'success': True/False,
    #     'total_files': int,
    #     'completed': int,  # 成功重命名
    #     'skipped': int,    # 跳过（无图号）
    #     'failed': int,     # 失败
    #     'convert_directory': str,
    #     'details': [...]
    # }
```

**文件处理流程：**

```
1. 检查图号存在 → 2. 生成唯一文件名（处理冲突）→ 3. 复制并重命名
   ↓                    ↓                              ↓
   跳过（无图号）      追加序号 _1, _2...           保留元数据
   ↓
4. 更新数据库记录
   - converted_directory
   - converted_filename
   - conversion_status
   - converted_at
```

**使用示例：**

```python
from src.services.pdf_reorganize_service import PDFReorganizeService
from src.models.dwg_drawing_sheet import DWGDrawingSheet

service = PDFReorganizeService(db_session)

# 查询图纸记录
sheets = db_session.query(DWGDrawingSheet).filter_by(task_id=task_id).all()

# 执行重组织
result = service.reorganize_pdfs(sheets, source_directory='./output')

print(f"✅ 成功: {result['completed']}")
print(f"⚠️  跳过: {result['skipped']}")
print(f"📁 转换目录: {result['convert_directory']}")
```

**冲突处理示例：**

```
源文件：
  tz001.pdf (图号: PCX-01-01-03-01-1)
  tz002.pdf (图号: PCX-01-01-03-01-1)  # 重复图号
  tz003.pdf (图号: None)              # 无图号

转换后：
  xxx_convert/
    ├─ PCX-01-01-03-01-1.pdf      # 第一个
    ├─ PCX-01-01-03-01-1_1.pdf    # 冲突，追加 _1
    └─ (tz003.pdf 被跳过，数据库记录 status=skipped)
```

**数据库更新字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `converted_directory` | VARCHAR(500) | 转换后目录路径 |
| `converted_filename` | VARCHAR(255) | 转换后文件名 |
| `conversion_status` | VARCHAR(20) | pending/completed/failed/skipped |
| `conversion_error` | TEXT | 错误信息 |
| `converted_at` | DATETIME | 转换完成时间 |

---

## 服务集成架构

### MinerU + PDF 重组织集成流程

```
┌─────────────────────────────────────────────┐
│        MinerUService                        │
│                                             │
│  1. batch_recognize_pdfs()                  │
│     ├─ 并发调用 MinerU API                   │
│     ├─ 解析识别结果                          │
│     ├─ 保存 DWGRecognitionResult            │
│     └─ 保存 DWGDrawingSheet (含 sheet_number)│
│                                             │
│  2. _reorganize_converted_pdfs() 🆕         │
│     ├─ 查询有图号的记录                      │
│     └─ 调用 PDFReorganizeService            │
│                                             │
└─────────────┬───────────────────────────────┘
              │ 自动触发（auto_reorganize_pdfs=True）
              ↓
┌─────────────────────────────────────────────┐
│     PDFReorganizeService 🆕                 │
│                                             │
│  reorganize_pdfs()                          │
│     ├─ 创建转换目录                          │
│     ├─ 遍历图纸记录                          │
│     │   ├─ 检查图号                         │
│     │   ├─ 生成唯一文件名                    │
│     │   ├─ 复制并重命名文件                  │
│     │   └─ 更新数据库记录                    │
│     └─ 提交事务                             │
│                                             │
└─────────────────────────────────────────────┘
```

### 配置驱动设计

所有服务依赖的配置参数都存储在数据库：

| 配置来源 | 表 | 字段 | 服务 |
|---------|---|------|------|
| AutoCAD 配置 | `autocad_config` | `mineru_*` | MinerUService |
| AutoCAD 配置 | `autocad_config` | `auto_reorganize_pdfs` | PDFReorganizeService |
| 字典配置 | `dict_preprocessing` | `dict_value` | DictService |
| 提取配置 | `dict_preprocessing` | `extraction_*` | MinerUService |

---

## 测试

### 单元测试

```bash
# 测试 PDF 重组织服务
python scripts/test_pdf_reorganize.py

# 测试 MinerU + 重组织集成
python scripts/test_mineru_with_reorganize.py ./output

# 测试材料提取
python scripts/test_material_extraction.py
```

### 集成测试

```bash
# 完整流程测试
python scripts/test_mineru_with_reorganize.py ./output --config default
```

---

## 开发指南

### 添加新服务

1. 在 `src/services/` 创建服务文件
2. 继承基础设计模式
3. 实现服务方法
4. 添加类型注解
5. 编写单元测试

**示例模板：**

```python
"""
服务名称和功能描述

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

from typing import Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger()


class NewService:
    """新服务描述"""

    def __init__(self, db_session):
        """初始化服务

        Args:
            db_session: 数据库会话
        """
        self.db = db_session
        self.logger = logger

    def main_method(self, param: str) -> Dict:
        """主要方法描述

        Args:
            param: 参数说明

        Returns:
            返回值说明
        """
        try:
            # 业务逻辑
            result = {'success': True}
            return result

        except Exception as e:
            self.logger.error(f"操作失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
```

---

## 相关文档

- [根目录文档](../../CLAUDE.md)
- [核心模块文档](../CLAUDE.md)
- [数据模型文档](../models/CLAUDE.md)
- [脚本工具文档](../../scripts/CLAUDE.md)

---

**最后更新：** 2025-11-06
**维护者：** 老王团队
**服务总数：** 6
**新增服务：** PDFReorganizeService（PDF 文件重组织）🆕 ⭐
