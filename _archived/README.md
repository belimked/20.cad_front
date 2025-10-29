# 项目归档文件

这个目录包含项目开发过程中产生的历史文件，已不再用于生产环境，但保留作为参考。

## 📦 归档时间

**2025-10-29** - 项目整理，归档历史文件

---

## 📋 归档目录结构

```
_archived/
├── reports/           # 历史报告文档（8个文件）
├── scripts_testing/   # 测试和诊断脚本（12个文件）
└── root_tests/        # 根目录测试文件（3个文件）
```

---

## 📚 1. 历史报告文档 (`reports/`)

开发阶段产生的各类报告和计划文档。

| 文件 | 大小 | 说明 |
|-----|------|------|
| BUGFIX_VERSION_PARSING.md | 4.8K | AutoCAD版本解析Bug修复报告 |
| DATABASE_INTEGRATION_REPORT.md | 9.5K | 数据库集成报告 |
| DAY1_COMPLETION_REPORT.md | 6.3K | 第1天开发完成报告 |
| DAY1_FINAL_SUMMARY.md | 12K | 第1天最终总结 |
| DAY2_MORNING_COMPLETION_REPORT.md | 9.3K | 第2天上午完成报告 |
| DAY2_SUMMARY.md | 8.7K | 第2天开发总结 |
| PHASE_BREAKDOWN.md | 34K | 项目阶段分解文档 |
| PROJECT_PLAN.md | 28K | 项目计划文档 |

**归档原因：** 开发阶段已完成，这些报告文档已完成历史使命。

---

## 🔧 2. 测试和诊断脚本 (`scripts_testing/`)

开发过程中用于测试、诊断和调试的工具脚本。

### 菜单操作测试工具

| 文件 | 大小 | 说明 |
|-----|------|------|
| capture_menu_icon.py | 9.5K | 截取菜单图标工具 |
| click_menu_by_baidu_ocr.py | 6.9K | 百度OCR菜单点击测试 |
| click_menu_by_image.py | 6.3K | 图像识别菜单点击测试 |
| click_menu_by_ocr.py | 10K | OCR文字识别菜单点击测试 |
| inspect_autocad_ui.py | 9.1K | AutoCAD UI结构检查工具 |

### OCR功能测试

| 文件 | 大小 | 说明 |
|-----|------|------|
| test_multi_image_ocr.py | 8.9K | 多图像OCR测试 |
| test_preprocessing_methods.py | 4.5K | 图像预处理方法测试 |
| test_tesseract_ocr.py | 8.0K | Tesseract OCR引擎测试 |
| test_umi_ocr_api.py | 7.3K | Umi-OCR API测试 |

### 其他工具

| 文件 | 大小 | 说明 |
|-----|------|------|
| create_test_package.py | 7.3K | 创建测试包工具 |
| diagnose_ocr_cleanup.py | 7.8K | OCR清理诊断工具 |
| test_autocad_config.py | 7.2K | AutoCAD配置测试 |

**归档原因：** 功能已集成到主程序，测试脚本已完成使命。

**参考价值：**
- 了解各种菜单操作方式的实现原理
- OCR引擎对比测试方法
- UI自动化调试技巧

---

## 🧪 3. 根目录测试文件 (`root_tests/`)

项目根目录的临时测试文件。

| 文件 | 大小 | 说明 |
|-----|------|------|
| test_db_connection.py | 4.0K | 数据库连接测试脚本 |
| test_pywinauto.py | 1.6K | pywinauto库功能测试 |
| img.png | 20K | 测试用图片 |

**归档原因：** 临时测试文件，已完成验证任务。

---

## 🎯 当前生产环境

归档后，项目聚焦于生产环境文件：

### 核心程序
- `research/autocad_com_api/9_configurable_workflow.py` - 主工作流程（111KB）

### 生产工具（`scripts/`）
- `autocad_config_manager.py` - 配置管理
- `enable_output_cleanup.py` - 输出目录清理
- `add_menu_operations.py` - 菜单操作配置
- `add_screenshot_extract_step.py` - 截图提取配置
- `init_*.py` - 初始化脚本
- `migrate_*.py` - 数据库迁移脚本
- `auto_migrate.py` - 自动迁移工具

### 核心代码
- `src/` - 源代码目录
- `config/` - 配置文件
- `docs/` - 文档目录
- `migrations/` - 数据库迁移
- `tests/` - 单元测试

---

## 📖 参考价值

这些归档文件具有以下参考价值：

### 1. 历史追溯
- 查看项目开发过程和决策记录
- 了解功能演进历史

### 2. 技术参考
- 各种技术方案的实现代码
- 测试和调试方法
- 问题排查思路

### 3. 学习资料
- AutoCAD COM API 使用示例
- OCR引擎对比和选择
- UI自动化技术实现

---

## 🔗 相关文档

- [项目主README](../README.md) - 项目说明和快速开始
- [AutoCAD工作流程README](../research/autocad_com_api/README.md) - 核心程序文档
- [开发文档](../docs/) - 完整的功能文档

---

**归档日期：** 2025-10-29
**归档文件数量：** 23个文件（8个报告 + 12个脚本 + 3个测试文件）
**归档原因：** 项目整理，聚焦生产环境
**状态：** 📦 已归档，保留供参考
