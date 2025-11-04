# 脚本工具文档 (scripts)

[根目录](../CLAUDE.md) > **scripts**

## 模块概述

**脚本工具 (scripts)** 包含数据库初始化、配置管理、测试验证等实用脚本，是项目开发和运维的工具箱。

**职责：**
- 数据库表初始化和迁移
- AutoCAD 配置管理
- OCR 功能测试和验证
- 系统诊断和问题排查
- 批量数据处理

## 脚本分类

### 数据库初始化 (6 个)

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `init_database.py` | 通用数据库初始化 | 首次部署 |
| `init_task_tables.py` | 初始化任务管理表 | 创建任务系统 |
| `init_autocad_config.py` | 初始化 AutoCAD 配置表 | 创建配置系统 |
| `init_preprocessing_dict.py` | 初始化预处理字典 | 创建 OCR 配置 |
| `add_menu_operations.py` | 添加菜单操作配置 | 扩展工作流 |
| `add_screenshot_extract_step.py` | 添加截图提取步骤 | 增强 OCR 功能 |

### 数据库迁移 (4 个)

| 脚本 | 功能 | 版本 |
|------|------|------|
| `auto_migrate.py` | 自动迁移脚本 | 通用 |
| `migrate_ocr_logging.py` | OCR 日志表迁移 | v0.2.0 |
| `migrate_add_output_dir_cleanup.py` | 输出目录清理配置迁移 | v0.2.5 |
| `migrate_add_use_bplot.py` | BPLOT 配置迁移 | v0.3.0 |

### 配置管理 (7 个)

| 脚本 | 功能 | 常用命令 |
|------|------|---------|
| `autocad_config_manager.py` | AutoCAD 配置管理工具 | `list`, `get`, `add`, `update`, `delete` |
| `add_bplot_config.py` | 添加 BPLOT 配置 | 单次运行 |
| `update_bplot_with_pre_post.py` | 更新 BPLOT 配置（前置/后置） | 升级配置 |
| `enable_output_cleanup.py` | 启用输出目录清理 | 配置开关 |
| `update_ocr_url.py` | 更新 OCR 服务地址 | 环境切换 |
| `check_config_format.py` | 检查配置格式 | 验证配置 |
| `check_raw_bplot_config.py` | 检查原始 BPLOT 配置 | 调试配置 |

### 测试验证 (6 个)

| 脚本 | 功能 | 使用场景 |
|------|------|---------|
| `test_api.py` | API 接口测试 | 测试 HTTP API |
| `check_bplot_dependencies.py` | 检查 BPLOT 依赖 | 环境检查 |
| `verify_bplot_enhanced.py` | 验证增强型 BPLOT | 功能验证 |
| `verify_workflow_config.py` | 验证工作流配置 | 配置验证 |
| `check_ocr_logs.py` | 查看 OCR 日志 | 问题排查 |
| `diagnose_pdf_extraction.py` | 诊断 PDF 提取 | 故障诊断 |

### OCR 和数据提取 (3 个)

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `pdf_ocr_with_umi.py` | PDF OCR 识别 | PDF 文件 | JSONL + JSON |
| `extract_drawing_info.py` | 提取图纸信息 | 单个 PDF | JSON |
| `batch_extract_info.py` | 批量提取信息 | PDF 目录 | CSV + JSON |

## 常用脚本详解

### autocad_config_manager.py - 配置管理工具

**功能：** 管理 AutoCAD 配置的 CRUD 操作

**命令：**
```bash
# 列出所有配置
python scripts/autocad_config_manager.py list

# 查看特定配置
python scripts/autocad_config_manager.py get default

# 添加新配置
python scripts/autocad_config_manager.py add my_config

# 更新配置
python scripts/autocad_config_manager.py update my_config

# 删除配置
python scripts/autocad_config_manager.py delete my_config

# 导出配置到 JSON
python scripts/autocad_config_manager.py export my_config output.json

# 从 JSON 导入配置
python scripts/autocad_config_manager.py import input.json
```

### check_ocr_logs.py - OCR 日志查看

**功能：** 查询和分析 OCR 识别日志

**输出示例：**
```
最近 20 条 OCR 识别记录：
==================================================
ID: 123
时间: 2025-11-04 21:15:53
配置: default
识别文本: 批量打印
截图路径: /path/to/screenshot.png
OCR 结果: {"data": [...], "code": 100}
状态: 成功
==================================================
```

### test_api.py - API 测试

**功能：** 测试 HTTP API 接口

**测试项：**
- 健康检查 (`/health`)
- 提交任务 (`POST /api/v1/tasks/print`)
- 查询任务 (`GET /api/v1/tasks/{task_id}`)
- 任务列表 (`GET /api/v1/tasks`)

### pdf_ocr_with_umi.py - PDF OCR 识别

**功能：** 使用 UMI-OCR 文档 API 识别 PDF

**使用方式：**
```bash
# 单个 PDF
python scripts/pdf_ocr_with_umi.py input.pdf

# 指定输出目录
python scripts/pdf_ocr_with_umi.py input.pdf --output ./results

# 指定 OCR 服务地址
python scripts/pdf_ocr_with_umi.py input.pdf --ocr-url http://10.3.19.63:11224
```

**输出：**
- `*.jsonl` - 原始 OCR 结果
- `*.json` - 提取的图纸信息

### batch_extract_info.py - 批量提取

**功能：** 批量处理 PDF 文件，提取图纸信息

**使用方式：**
```bash
# 处理目录下所有 PDF
python scripts/batch_extract_info.py /path/to/pdfs

# 指定输出目录
python scripts/batch_extract_info.py /path/to/pdfs --output ./results

# 生成 CSV 汇总
python scripts/batch_extract_info.py /path/to/pdfs --csv summary.csv
```

## 快速参考

### 首次部署

```bash
# 1. 初始化数据库
python scripts/init_database.py

# 2. 初始化 AutoCAD 配置
python scripts/init_autocad_config.py

# 3. 初始化任务表
python scripts/init_task_tables.py

# 4. 初始化预处理字典
python scripts/init_preprocessing_dict.py

# 5. 验证配置
python scripts/verify_workflow_config.py

# 6. 测试 API
python scripts/test_api.py
```

### 日常维护

```bash
# 查看 OCR 日志
python scripts/check_ocr_logs.py

# 检查配置格式
python scripts/check_config_format.py

# 验证 BPLOT 功能
python scripts/verify_bplot_enhanced.py

# 测试 API
python scripts/test_api.py
```

### 问题排查

```bash
# 诊断 PDF 提取
python scripts/diagnose_pdf_extraction.py

# 检查 BPLOT 依赖
python scripts/check_bplot_dependencies.py

# 查看数据库配置
python scripts/autocad_config_manager.py get default
```

### 配置更新

```bash
# 更新 OCR 服务地址
python scripts/update_ocr_url.py

# 启用输出目录清理
python scripts/enable_output_cleanup.py

# 更新 BPLOT 配置
python scripts/update_bplot_with_pre_post.py
```

## 脚本开发规范

### 模板结构

```python
#!/usr/bin/env python
"""
脚本名称和功能描述

Author: 老王团队
Date: 2025-11-04
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.utils.database import db_session

logger = get_logger()

def main():
    """主函数"""
    logger.info("脚本开始执行")
    try:
        with db_session() as session:
            # 业务逻辑
            pass
        logger.info("脚本执行成功")
    except Exception as e:
        logger.error(f"脚本执行失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 命名规范

- **初始化脚本：** `init_*.py`
- **迁移脚本：** `migrate_*.py`
- **测试脚本：** `test_*.py`, `check_*.py`, `verify_*.py`
- **管理工具：** `*_manager.py`
- **批处理脚本：** `batch_*.py`
- **诊断工具：** `diagnose_*.py`

## 相关文档

- [根目录文档](../CLAUDE.md)
- [核心模块文档](../src/CLAUDE.md)
- [数据库配置指南](../docs/DATABASE_CONFIG_GUIDE.md)

---

**最后更新：** 2025-11-04
**维护者：** 老王团队
**脚本总数：** 27
