# 核心模块文档 (src)

[根目录](../CLAUDE.md) > **src**

## 模块概述

**核心模块 (src)** 是 CAD 文件自动化处理系统的业务逻辑核心，包含数据模型、业务服务、功能模块和工具模块。

**职责：**
- 定义数据库模型和表结构（ORM）
- 实现核心业务逻辑（任务管理、配置管理、OCR 服务）
- 提供功能模块（文件下载、监控）
- 封装工具模块（配置、日志、数据库）

**设计原则：**
- 分层架构：数据层 → 服务层 → 应用层
- 单一职责：每个模块职责明确
- 依赖注入：服务间松耦合
- 配置驱动：参数外部化

## 目录结构

```
src/
├── __init__.py                      # 包初始化
├── models/                          # 数据模型层 ⭐
│   ├── __init__.py
│   ├── autocad_config.py            # AutoCAD 配置模型
│   ├── dwg_process_task.py          # DWG 任务模型
│   ├── dwg_task_step.py             # 任务步骤日志模型
│   ├── dictionary.py                # 字典表模型
│   └── ocr_recognition_log.py       # OCR 识别日志模型
├── services/                        # 业务服务层 ⭐
│   ├── __init__.py
│   ├── autocad_config_service.py    # AutoCAD 配置服务
│   ├── task_service.py              # 任务管理服务
│   ├── dict_service.py              # 字典服务
│   └── ocr_logging_service.py       # OCR 日志服务
├── modules/                         # 功能模块层
│   ├── __init__.py
│   └── downloader.py                # 文件下载模块
└── utils/                           # 工具模块层 ⭐
    ├── __init__.py
    ├── config.py                    # 配置管理
    ├── database.py                  # 数据库管理（单例）
    ├── logger.py                    # 日志工具
    ├── image_processing.py          # 图像预处理
    └── ocr_file_manager.py          # OCR 文件管理
```

## 子模块导航

- **[models/](./models/CLAUDE.md)** - 数据模型层（SQLAlchemy ORM）
- **[services/](./services/CLAUDE.md)** - 业务服务层
- **[modules/](./modules/CLAUDE.md)** - 功能模块层
- **[utils/](./utils/CLAUDE.md)** - 工具模块层

## 核心组件概览

### 1. 数据模型层 (`models/`)

**职责：** 定义数据库表结构，提供 ORM 映射

**核心模型：**

| 模型 | 表名 | 职责 |
|------|------|------|
| `AutoCADConfig` | `autocad_config` | 存储 AutoCAD 工作流配置（JSON 格式） |
| `DWGProcessTask` | `dwg_process_tasks` | 记录 DWG 处理任务状态 |
| `DWGTaskStep` | `dwg_task_steps` | 记录任务执行步骤日志 |
| `Dictionary` | `dict_preprocessing` | 存储 OCR 图像预处理配置 |
| `OCRRecognitionLog` | `ocr_recognition_logs` | 记录 OCR 识别结果和日志 |

**数据库关系图：**
```
dwg_process_tasks (任务表)
    ├─> config_id ──> autocad_config (配置表)
    └─> task_id ──> dwg_task_steps (步骤日志)

autocad_config (配置表)
    └─> preprocessing_dict_key ──> dict_preprocessing (字典表)

dwg_task_steps (步骤日志)
    └─> task_id ──> ocr_recognition_logs (OCR 日志)
```

**详细文档：** [models/CLAUDE.md](./models/CLAUDE.md)

### 2. 业务服务层 (`services/`)

**职责：** 封装业务逻辑，提供高层服务接口

**核心服务：**

#### AutoCADConfigService (`autocad_config_service.py`)

**功能：**
- 查询/创建/更新 AutoCAD 配置
- 解析 JSON 工作流配置
- 验证配置有效性

**使用示例：**
```python
from src.services.autocad_config_service import AutoCADConfigService

service = AutoCADConfigService()
config = service.get_config_by_name("default")
print(config.menu_operations)  # JSON 格式的操作序列
```

#### TaskService (`task_service.py`)

**功能：**
- 创建/查询/更新任务
- 记录任务步骤
- 更新任务状态和进度
- 处理任务失败和重试

**任务状态流转：**
```
pending → downloading → processing → completed
                                   ↓
                                 failed
```

#### DictService (`dict_service.py`)

**功能：**
- 查询 OCR 预处理配置
- 管理字典数据

#### OCRLoggingService (`ocr_logging_service.py`)

**功能：**
- 记录 OCR 识别日志
- 查询历史识别记录
- 统计识别成功率

**详细文档：** [services/CLAUDE.md](./services/CLAUDE.md)

### 3. 功能模块层 (`modules/`)

**职责：** 实现独立的功能模块

**现有模块：**

#### Downloader (`downloader.py`)

**功能：**
- HTTP 文件下载
- 断点续传
- MD5 校验
- 进度回调

**缺失模块（TODO）：**
- ❌ `uploader.py` - 文件上传模块
- ❌ `file_monitor.py` - 文件监控模块
- ❌ `cad_automation.py` - AutoCAD 自动化封装

**详细文档：** [modules/CLAUDE.md](./modules/CLAUDE.md)

### 4. 工具模块层 (`utils/`)

**职责：** 提供通用工具和基础设施

**核心工具：**

#### database.py - 数据库管理

**特性：**
- 单例模式管理数据库连接
- 连接池配置
- 自动重连
- 上下文管理器

**使用示例：**
```python
from src.utils.database import db_session

# 推荐方式：上下文管理器
with db_session() as session:
    tasks = session.query(DWGProcessTask).all()
    # 自动 commit 和 close
```

#### config.py - 配置管理

**特性：**
- YAML 配置文件解析
- 环境变量覆盖
- 配置验证
- 单例模式

**配置优先级：**
```
环境变量 (CAD_*) > config.yaml > 默认值
```

#### logger.py - 日志工具

**特性：**
- 基于 loguru 的日志管理
- 按日期轮转
- 多级别日志（DEBUG/INFO/WARNING/ERROR）
- 彩色输出

**使用示例：**
```python
from src.utils.logger import get_logger

logger = get_logger()
logger.info("任务开始")
logger.error("任务失败", exc_info=True)
```

#### image_processing.py - 图像预处理

**功能：**
- 图像二值化
- 去噪处理
- 对比度增强
- OCR 预处理优化

**支持的预处理方法：**
- `binary_adaptive` - 自适应二值化
- `denoise_bilateral` - 双边滤波去噪
- `high_contrast` - 对比度增强
- `clahe` - CLAHE 对比度增强
- `sharpen` - 锐化
- `canny_edge` - Canny 边缘检测

#### ocr_file_manager.py - OCR 文件管理

**功能：**
- OCR 截图保存
- 文件归档和清理
- 按时间戳组织文件

**详细文档：** [utils/CLAUDE.md](./utils/CLAUDE.md)

## 依赖关系

### 内部依赖

```
services/ (业务服务层)
    ├─> models/ (数据模型层)
    └─> utils/ (工具模块层)

modules/ (功能模块)
    └─> utils/ (工具模块层)

models/ (数据模型)
    └─> utils/database.py (数据库管理)
```

### 外部依赖

**核心依赖：**
- SQLAlchemy 2.0+ - ORM 框架
- pymysql - MySQL 驱动
- loguru - 日志库
- pyyaml - YAML 解析

**OCR 相关：**
- opencv-python - 图像处理
- pillow - 图像操作
- numpy - 数值计算
- requests - HTTP 请求（调用 UMI-OCR API）

## 数据库设计

### 表结构概览

**配置表：**
- `autocad_config` - AutoCAD 工作流配置
- `dict_preprocessing` - OCR 预处理配置字典

**任务表：**
- `dwg_process_tasks` - DWG 处理任务主表
- `dwg_task_steps` - 任务步骤日志表

**日志表：**
- `autocad_task_log` - AutoCAD 任务执行日志
- `ocr_recognition_logs` - OCR 识别日志

### 配置驱动设计

**核心理念：** 所有自动化流程参数存储在数据库，而非硬编码

**配置存储格式：**
```json
{
  "前置操作": [...],
  "主流程": [
    {
      "type": "command",
      "command": "_OPEN",
      "wait_time": 2.0
    },
    {
      "type": "menu",
      "text": "批量打印",
      "timeout": 10
    }
  ],
  "后置操作": [...]
}
```

**优势：**
- 无需修改代码即可调整流程
- 支持多套配置方案
- 版本控制和审计
- 热更新（无需重启服务）

## 使用示例

### 完整任务处理流程

```python
from src.services.task_service import TaskService
from src.services.autocad_config_service import AutoCADConfigService
from src.utils.logger import get_logger

logger = get_logger()

# 1. 创建任务
task_service = TaskService()
task = task_service.create_task(
    dwg_url="http://example.com/file.dwg",
    config_name="default",
    use_bplot=True
)

logger.info(f"任务创建成功: {task.task_id}")

# 2. 更新任务状态
task_service.update_task_status(
    task_id=task.task_id,
    status="downloading",
    progress=10
)

# 3. 记录任务步骤
task_service.add_task_step(
    task_id=task.task_id,
    step_name="下载文件",
    step_number=1,
    status="success",
    details="文件下载完成"
)

# 4. 获取 AutoCAD 配置
config_service = AutoCADConfigService()
autocad_config = config_service.get_config_by_name("default")

# 5. 执行工作流...
# (调用 research/autocad_com_api/enhanced_workflow.py)
```

## 测试

### 单元测试

```bash
# 测试数据库连接
python src/utils/database.py

# 测试配置加载
python src/utils/config.py

# 测试服务层
pytest tests/src/services/ -v
```

### 数据库初始化

```bash
# 初始化所有表
python scripts/init_database.py

# 初始化 AutoCAD 配置
python scripts/init_autocad_config.py

# 初始化任务表
python scripts/init_task_tables.py
```

## 常见问题

### 1. 数据库连接失败

**问题：** `Can't connect to MySQL server`

**解决：**
1. 检查 MySQL 服务状态
2. 验证 `config.yaml` 中的数据库配置
3. 测试网络连接：`telnet 10.3.19.189 3313`
4. 检查防火墙规则

### 2. 配置文件未找到

**问题：** `Config file not found: config/config.yaml`

**解决：**
```bash
# 复制配置模板
cp config/config.yaml.example config/config.yaml

# 编辑配置
vim config/config.yaml
```

### 3. 数据库表不存在

**问题：** `Table 'cad_mgt.autocad_config' doesn't exist`

**解决：**
```bash
# 运行初始化脚本
python scripts/init_database.py
python scripts/init_autocad_config.py
```

### 4. OCR 预处理失败

**问题：** 图像预处理导致 OCR 识别率下降

**解决：**
1. 检查预处理配置是否适合当前场景
2. 尝试不同的预处理方法组合
3. 查看 OCR 日志：`python scripts/check_ocr_logs.py`
4. 调整预处理参数

## 开发指南

### 添加新的数据模型

1. 在 `src/models/` 创建模型文件
2. 继承 `Base` 类
3. 定义表结构和字段
4. 添加 `to_dict()` 方法
5. 创建迁移脚本

**示例：**
```python
from sqlalchemy import Column, Integer, String, DateTime
from src.utils.database import Base

class NewModel(Base):
    __tablename__ = 'new_table'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    created_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

### 添加新的业务服务

1. 在 `src/services/` 创建服务文件
2. 实现服务类
3. 依赖注入数据库会话
4. 添加业务方法
5. 编写单元测试

### 添加新的工具模块

1. 在 `src/utils/` 创建工具文件
2. 实现工具函数或类
3. 添加类型注解
4. 编写文档字符串
5. 添加使用示例

## 性能优化建议

1. **数据库查询优化**
   - 使用索引
   - 避免 N+1 查询
   - 使用 `joinedload` 预加载关联数据

2. **连接池配置**
   ```python
   engine = create_engine(
       DATABASE_URL,
       poolclass=QueuePool,
       pool_size=10,
       max_overflow=20
   )
   ```

3. **缓存策略**
   - 配置数据缓存（Redis）
   - 查询结果缓存

4. **日志优化**
   - 异步日志写入
   - 按级别过滤
   - 定期归档

## 相关文档

- [根目录文档](../CLAUDE.md)
- [API 模块文档](../api/CLAUDE.md)
- [数据模型文档](./models/CLAUDE.md)
- [业务服务文档](./services/CLAUDE.md)
- [工具模块文档](./utils/CLAUDE.md)
- [数据库配置指南](../docs/DATABASE_CONFIG_GUIDE.md)

---

**最后更新：** 2025-11-04
**维护者：** 老王团队
