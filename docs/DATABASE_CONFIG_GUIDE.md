# AutoCAD 自动化数据库配置指南

## 概述

本系统通过数据库配置实现 AutoCAD 自动化工作流程的灵活管理，所有参数均可存储在数据库中并动态加载。

## 可配置参数

### 1. CAD 程序配置
- **CAD 启动程序路径** (`autocad_exe_path`): AutoCAD 可执行文件路径，留空则自动检测
- **CAD 版本** (`autocad_version`): 目标 AutoCAD 版本，如 "2014"
- **强制关闭现有进程** (`force_close_existing`): 运行前是否关闭已打开的 AutoCAD

### 2. 文件配置
- **DWG 文件路径** (`dwg_file_path`): 要打开的 DWG 文件完整路径
- **文件打开重试次数** (`file_open_max_retries`): 打开文件失败时的最大重试次数（默认 3 次）
- **文件打开重试延迟** (`file_open_retry_delay`): 重试之间的等待时间（秒，默认 3.0）

### 3. 延迟配置（所有单位为秒）
- **启动等待时间** (`startup_wait_time`): 最多等待 AutoCAD 启动的时间（默认 10.0）
- **启动检查间隔** (`startup_check_interval`): 检查启动状态的间隔（默认 1.0）
- **启动后额外等待** (`post_startup_wait`): 启动成功后的额外稳定等待（默认 2.0）
- **验证等待时间** (`verification_wait_time`): 验证文件加载的最长时间（默认 30.0）
- **验证检查间隔** (`verification_check_interval`): 验证检查的间隔（默认 2.0）

### 4. 菜单操作配置
- **菜单操作** (`menu_operations`): JSON 格式的菜单操作序列

菜单操作 JSON 格式示例：
```json
[
    {
        "type": "command",
        "command": "ZOOM",
        "wait_time": 0.5
    },
    {
        "type": "command",
        "command": "E",
        "wait_time": 1.0
    }
]
```

## 快速开始

### 步骤 1: 初始化数据库配置

运行初始化脚本创建表和示例配置：

```bash
# Windows
python scripts\init_autocad_config.py

# macOS/Linux
python scripts/init_autocad_config.py
```

该脚本会：
- 创建 `autocad_config` 和 `autocad_task_log` 表
- 插入 4 个示例配置：
  - **default**: 通用配置（10秒启动，30秒验证）
  - **fast**: 快速模式（5秒启动，15秒验证）- 适合高性能机器
  - **stable**: 稳定模式（20秒启动，60秒验证）- 适合旧机器或慢速系统
  - **with_menu_operations**: 包含菜单操作的示例

### 步骤 2: 查看配置

使用配置管理工具查看所有配置：

```bash
# 列出所有配置
python scripts\autocad_config_manager.py list

# 仅显示激活的配置
python scripts\autocad_config_manager.py list --active-only

# 显示指定配置详情
python scripts\autocad_config_manager.py show 1
```

### 步骤 3: 激活配置

激活要使用的配置（同时会停用其他配置）：

```bash
python scripts\autocad_config_manager.py activate 1
```

### 步骤 4: 修改配置

修改配置参数：

```bash
# 修改启动等待时间
python scripts\autocad_config_manager.py update 1 --startup-wait 15.0

# 修改验证等待时间
python scripts\autocad_config_manager.py update 1 --verification-wait 45.0

# 修改重试次数
python scripts\autocad_config_manager.py update 1 --retry-count 5

# 修改描述
python scripts\autocad_config_manager.py update 1 --description "适用于2014版本的稳定配置"
```

### 步骤 5: 使用配置运行工作流程

#### 方法 1: 使用配置名称

```python
from research.autocad_com_api.9_configurable_workflow import ConfigurableAutoCADWorkflow

# 使用名为 'default' 的配置
workflow = ConfigurableAutoCADWorkflow(config_name='default')

# 运行工作流程
dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"
success = workflow.run(dwg_file_path=dwg_file)
```

#### 方法 2: 使用配置 ID

```python
# 使用 ID 为 1 的配置
workflow = ConfigurableAutoCADWorkflow(config_id=1)
success = workflow.run(dwg_file_path=dwg_file)
```

#### 方法 3: 使用默认激活配置

```python
# 如果配置名称和 ID 都不提供，会使用标记为激活的配置
from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService

db = SessionLocal()
service = AutoCADConfigService(db)
config = service.get_config()  # 获取激活的配置
db.close()

workflow = ConfigurableAutoCADWorkflow(config=config)
success = workflow.run(dwg_file_path=dwg_file)
```

## 高级使用

### 直接在数据库中创建自定义配置

使用 Python 代码创建自定义配置：

```python
from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService

db = SessionLocal()
service = AutoCADConfigService(db)

# 创建自定义配置
custom_config = {
    'config_name': 'my_custom_config',
    'description': '我的自定义配置',
    'autocad_version': '2014',
    'force_close_existing': True,
    'startup_wait_time': 12.0,
    'startup_check_interval': 1.0,
    'post_startup_wait': 3.0,
    'file_open_retry_delay': 4.0,
    'file_open_max_retries': 5,
    'verification_wait_time': 40.0,
    'verification_check_interval': 2.0,
    'menu_operations': [
        {"type": "command", "command": "ZOOM", "wait_time": 0.5},
        {"type": "command", "command": "E", "wait_time": 1.0}
    ],
    'is_active': False
}

config = service.create_config(custom_config)
print(f"创建配置成功，ID: {config.id}")

db.close()
```

### 查看任务执行日志

```python
from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService

db = SessionLocal()
service = AutoCADConfigService(db)

# 获取所有任务日志
logs = service.get_task_logs(limit=10)

for log in logs:
    print(f"任务: {log.task_name}")
    print(f"状态: {log.status}")
    print(f"开始时间: {log.start_time}")
    print(f"耗时: {log.duration_seconds}秒")
    if log.error_message:
        print(f"错误: {log.error_message}")
    print("-" * 50)

db.close()
```

### 根据配置获取日志

```python
# 获取特定配置的日志
logs = service.get_task_logs(config_id=1, limit=20)

# 获取失败的任务
failed_logs = service.get_task_logs(status='failed', limit=20)

# 获取成功的任务
success_logs = service.get_task_logs(status='success', limit=20)
```

## 配置文件说明

### 预设配置对比

| 配置名称 | 启动等待 | 验证等待 | 重试次数 | 适用场景 |
|---------|---------|---------|---------|---------|
| **default** | 10秒 | 30秒 | 3次 | 通用场景，适合大多数机器 |
| **fast** | 5秒 | 15秒 | 2次 | 高性能机器，SSD 硬盘 |
| **stable** | 20秒 | 60秒 | 5次 | 旧版本 CAD，慢速机器，网络驱动器 |
| **with_menu_operations** | 10秒 | 30秒 | 3次 | 需要执行菜单操作的场景 |

### 选择合适的配置

**选择 `fast` 配置如果：**
- 使用高性能计算机
- AutoCAD 安装在 SSD 上
- DWG 文件较小（<10MB）

**选择 `default` 配置如果：**
- 使用标准配置的计算机
- 不确定应该使用哪个配置

**选择 `stable` 配置如果：**
- 使用较旧的计算机
- DWG 文件较大（>50MB）
- 文件存储在网络驱动器
- 经常遇到超时问题

## 调优建议

### 问题：AutoCAD 启动超时

**症状**：看到"等待中..."消息持续出现，然后失败

**解决方案**：
```bash
# 增加启动等待时间
python scripts\autocad_config_manager.py update <config_id> --startup-wait 20.0
```

### 问题：文件打开失败

**症状**：提示"文件打开失败"或"COM 错误 -2147418111"

**解决方案**：
```bash
# 增加重试次数和延迟
python scripts\autocad_config_manager.py update <config_id> --retry-count 5

# 同时增加启动后额外等待时间（需要直接修改数据库）
```

### 问题：验证超时

**症状**：文件打开成功但验证阶段超时

**解决方案**：
```bash
# 增加验证等待时间
python scripts\autocad_config_manager.py update <config_id> --verification-wait 60.0
```

## 数据库表结构

### autocad_config 表

| 字段名 | 类型 | 说明 | 默认值 |
|-------|------|------|--------|
| id | Integer | 主键 | 自增 |
| config_name | String(100) | 配置名称（唯一） | 必填 |
| description | String(500) | 配置描述 | 可选 |
| autocad_exe_path | String(500) | CAD 可执行文件路径 | NULL（自动检测） |
| autocad_version | String(50) | CAD 版本号 | NULL |
| dwg_file_path | String(1000) | DWG 文件路径 | NULL |
| force_close_existing | Boolean | 强制关闭现有进程 | True |
| startup_wait_time | Float | 启动等待时间（秒） | 10.0 |
| startup_check_interval | Float | 启动检查间隔（秒） | 1.0 |
| post_startup_wait | Float | 启动后额外等待（秒） | 2.0 |
| file_open_retry_delay | Float | 文件打开重试延迟（秒） | 3.0 |
| file_open_max_retries | Integer | 文件打开最大重试次数 | 3 |
| verification_wait_time | Float | 验证等待时间（秒） | 30.0 |
| verification_check_interval | Float | 验证检查间隔（秒） | 2.0 |
| menu_operations | Text | 菜单操作（JSON） | NULL |
| is_active | Boolean | 是否激活 | False |
| created_at | DateTime | 创建时间 | 自动 |
| updated_at | DateTime | 更新时间 | 自动 |

### autocad_task_log 表

| 字段名 | 类型 | 说明 |
|-------|------|------|
| id | Integer | 主键 |
| config_id | Integer | 关联的配置 ID |
| task_name | String(200) | 任务名称 |
| dwg_file | String(1000) | DWG 文件路径 |
| status | String(50) | 状态（running/success/failed） |
| start_time | DateTime | 开始时间 |
| end_time | DateTime | 结束时间 |
| duration_seconds | Float | 执行时长（秒） |
| error_message | Text | 错误信息 |
| execution_log | Text | 执行日志 |
| created_at | DateTime | 创建时间 |

## 工作流程说明

### 完整执行流程

```
1. 加载配置
   ↓
2. 记录任务开始
   ↓
3. 关闭现有 AutoCAD（如果配置要求）
   ↓
4. 启动 AutoCAD
   ↓
5. 等待启动完成（使用 startup_wait_time）
   ↓
6. 打开 DWG 文件（使用 file_open_max_retries）
   ↓
7. 验证文件加载（使用 verification_wait_time）
   ↓
8. 执行菜单操作（如果配置了 menu_operations）
   ↓
9. 记录任务完成
```

### 错误处理机制

- **启动失败**：如果在 `startup_wait_time` 内未能启动，返回失败
- **文件打开失败**：重试 `file_open_max_retries` 次，每次间隔 `file_open_retry_delay` 秒
- **验证失败**：如果在 `verification_wait_time` 内未验证成功，返回失败
- **菜单操作失败**：记录警告但不影响整体流程状态

## 常见问题 (FAQ)

### Q: 如何同时使用多个配置？

A: 每次只能激活一个配置作为默认配置，但可以在代码中指定使用任何配置：

```python
workflow1 = ConfigurableAutoCADWorkflow(config_name='fast')
workflow2 = ConfigurableAutoCADWorkflow(config_name='stable')
```

### Q: 配置中的文件路径可以留空吗？

A: 可以。`dwg_file_path` 可以留空，在运行时通过 `run(dwg_file_path=...)` 参数指定。

### Q: 如何删除配置？

A: 目前通过数据库或 Python 代码删除：

```python
from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService

db = SessionLocal()
service = AutoCADConfigService(db)
success = service.delete_config(config_id=5)
db.close()
```

### Q: 菜单操作支持哪些类型？

A: 目前支持：
- `command` - 执行 AutoCAD 命令
- 未来可扩展：键盘操作、鼠标点击等

### Q: 如何备份配置？

A: 配置存储在 SQLite 数据库中，备份整个数据库文件即可。

## 文件清单

### 核心文件

- `src/models/autocad_config.py` - 数据库模型定义
- `src/services/autocad_config_service.py` - 配置管理服务
- `research/autocad_com_api/9_configurable_workflow.py` - 可配置工作流程

### 工具脚本

- `scripts/init_autocad_config.py` - 初始化数据库和示例配置
- `scripts/autocad_config_manager.py` - CLI 配置管理工具

### 文档

- `docs/DATABASE_CONFIG_GUIDE.md` - 本文档（使用指南）
- `research/autocad_com_api/WORKFLOW_GUIDE.md` - 原始工作流程指南

## 示例代码

### 完整示例：使用自定义配置处理多个文件

```python
from pathlib import Path
from research.autocad_com_api.9_configurable_workflow import ConfigurableAutoCADWorkflow

def batch_process_dwg_files(config_name='default', file_pattern='*.dwg'):
    """批量处理 DWG 文件"""

    # 初始化工作流程
    workflow = ConfigurableAutoCADWorkflow(config_name=config_name)

    # 查找所有 DWG 文件
    dwg_dir = Path(r"F:\cad\caddd")
    dwg_files = list(dwg_dir.glob(file_pattern))

    print(f"找到 {len(dwg_files)} 个文件")

    results = []
    for i, dwg_file in enumerate(dwg_files, 1):
        print(f"\n处理文件 {i}/{len(dwg_files)}: {dwg_file.name}")

        success = workflow.run(dwg_file_path=str(dwg_file))
        results.append({
            'file': dwg_file.name,
            'success': success
        })

    # 汇总结果
    print("\n" + "=" * 80)
    print("处理结果汇总")
    print("=" * 80)

    success_count = sum(1 for r in results if r['success'])
    print(f"成功: {success_count}/{len(results)}")

    if success_count < len(results):
        print("\n失败的文件:")
        for r in results:
            if not r['success']:
                print(f"  - {r['file']}")

    workflow.cleanup()

if __name__ == "__main__":
    batch_process_dwg_files(config_name='stable', file_pattern='PCX*.dwg')
```

## 下一步

1. 根据实际测试调整默认配置参数
2. 添加更多预设配置
3. 扩展菜单操作支持更多类型
4. 实现配置导入/导出功能
5. 添加 Web 界面管理配置（可选）

---

**创建日期**: 2025-10-26
**版本**: 1.0
**作者**: CAD Auto Processor Team
