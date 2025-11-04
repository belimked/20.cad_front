# 项目文件清理分析报告

**生成时间**: 2025-11-04 21:30:00
**分析者**: Claude Code (Workflow Agent)
**项目**: CAD 文件自动化处理系统

---

## 📊 项目概况

- **文件总数**: 149 个 (Python/Markdown/脚本)
- **项目大小**: 19 MB
- **核心文件**: 6 个 (已指定)
- **扫描范围**: 全项目 (排除 venv, .git, __pycache__, data, logs)

---

## 🎯 核心文件清单 (绝对保留)

### 1. API 启动脚本
| 文件路径 | 类型 | 用途 |
|---------|------|------|
| `start_api.ps1` | PowerShell | FastAPI 服务启动脚本 |

### 2. AutoCAD 工作流核心文件
| 文件路径 | 类型 | 用途 |
|---------|------|------|
| `research/autocad_com_api/9_configurable_workflow.py` | Python | 可配置工作流（数据库驱动） |
| `research/autocad_com_api/10_bplot_workflow.py` | Python | BPLOT 批量打印工作流 |
| `research/autocad_com_api/11_bplot_auto_workflow.py` | Python | BPLOT 全自动化工作流 |
| `research/autocad_com_api/enhanced_workflow.py` | Python | **增强型工作流（最完整实现）** ⭐ |
| `research/autocad_com_api/README.md` | Markdown | 研究模块说明文档 |

---

## ✅ 强关联文件 (必须保留)

### A. 代码级依赖

#### A1. 核心业务模块 (被核心文件 import)
```
src/
├── models/                          # 数据模型 (5个)
│   ├── autocad_config.py            ✅ enhanced_workflow 导入
│   ├── dwg_process_task.py          ✅ enhanced_workflow 导入
│   ├── dwg_task_step.py             ✅ enhanced_workflow 导入
│   ├── dictionary.py                ✅ 图像预处理配置
│   └── ocr_recognition_log.py       ✅ OCR 日志记录
│
├── services/                        # 业务服务 (4个)
│   ├── autocad_config_service.py    ✅ enhanced_workflow 导入
│   ├── task_service.py              ✅ 任务管理
│   ├── dict_service.py              ✅ 字典服务
│   └── ocr_logging_service.py       ✅ OCR 日志
│
├── modules/                         # 功能模块 (1个)
│   └── downloader.py                ✅ 文件下载
│
└── utils/                           # 工具模块 (5个)
    ├── database.py                  ✅ enhanced_workflow 导入
    ├── image_processing.py          ✅ 11_bplot, enhanced 导入
    ├── ocr_file_manager.py          ✅ 11_bplot 导入
    ├── config.py                    ✅ 配置管理
    └── logger.py                    ✅ 日志工具
```

**统计**: 15 个 Python 文件 (100% 保留)

#### A2. API 模块 (start_api.ps1 启动)
```
api/
├── main.py                          ✅ FastAPI 入口
├── routers/                         ✅ 路由 (2个)
│   ├── tasks.py
│   └── health.py
├── schemas/                         ✅ 数据模型 (4个)
│   ├── task.py
│   ├── response.py
│   └── ...
└── services/                        ✅ 业务服务 (2个)
    ├── task_service.py
    └── workflow_service.py
```

**统计**: 11 个 Python 文件 (100% 保留)

#### A3. 配置文件
```
config/
└── config.yaml.example              ✅ 配置模板

requirements.txt                     ✅ 依赖清单
.gitignore                          ✅ Git 配置
```

**统计**: 3 个文件 (100% 保留)

#### A4. 数据库初始化脚本 (必须保留)
```
scripts/
├── init_database.py                 ✅ 数据库初始化
├── init_autocad_config.py           ✅ AutoCAD 配置初始化
├── init_task_tables.py              ✅ 任务表初始化
├── init_preprocessing_dict.py       ✅ 预处理字典初始化
└── autocad_config_manager.py        ✅ 配置管理工具
```

**统计**: 5 个脚本 (必须保留)

### B. 文档级依赖

#### B1. 根级文档 (必须保留)
```
README.md                            ✅ 项目主文档
QUICK_START.md                       ✅ 快速开始指南
CLAUDE.md                            ✅ AI 协助开发指导 (根级)
```

#### B2. 模块架构文档 (新生成，必须保留)
```
api/CLAUDE.md                        ✅ API 模块文档
src/CLAUDE.md                        ✅ 核心模块文档
research/CLAUDE.md                   ✅ 研究模块文档
scripts/CLAUDE.md                    ✅ 脚本工具文档
.claude/index.json                   ✅ 架构索引
```

#### B3. 核心功能指南 (强关联)
```
docs/
├── ENHANCED_WORKFLOW_GUIDE.md       ✅ 增强型工作流指南 ⭐
├── BPLOT_AUTO_WORKFLOW_GUIDE.md     ✅ BPLOT 自动化指南 ⭐
├── DATABASE_CONFIG_GUIDE.md         ✅ 配置系统指南 ⭐
├── MENU_OPERATIONS_GUIDE.md         ✅ 菜单操作指南 ⭐
├── UMI_OCR_API_GUIDE.md             ✅ OCR 集成指南
├── API_GUIDE.md                     ✅ HTTP API 指南
├── MENU_CLICKING_GUIDE.md           ✅ 菜单点击指南
├── SCREENSHOT_EXTRACT_GUIDE.md      ✅ 截图提取指南
├── image_preprocessing_guide.md     ✅ 图像预处理指南
├── ocr_preprocessing_config_guide.md ✅ OCR 预处理配置
├── ocr_logging_user_guide.md        ✅ OCR 日志指南
├── BPLOT_CONFIGURABLE_GUIDE.md      ✅ BPLOT 可配置指南
├── BPLOT_CONFIG_GUIDE.md            ✅ BPLOT 配置指南
├── BPLOT_VERSION_COMPARISON.md      ✅ BPLOT 版本对比
├── TESSERACT_INSTALLATION_GUIDE.md  ✅ Tesseract 安装
└── autocad/
    ├── AUTOCAD_COM_API_SUMMARY.md   ✅ AutoCAD API 总结
    └── TESTING_GUIDE.md             ✅ 测试指南
```

**统计**: 17 个文档 (强关联，建议保留)

#### B4. 测试和验证脚本 (建议保留)
```
scripts/
├── test_api.py                      ✅ API 测试
├── check_bplot_dependencies.py      ✅ 依赖检查
├── verify_bplot_enhanced.py         ✅ 增强工作流验证
├── verify_workflow_config.py        ✅ 配置验证
├── check_config_format.py           ✅ 配置格式检查
└── check_ocr_logs.py                ✅ OCR 日志检查
```

**统计**: 6 个脚本 (建议保留)

---

## ❌ 建议清理的文件

### C1. 历史归档代码 (research/_archived/)

**清理原因**: 早期研究代码，已被 9-11 和 enhanced 版本完全替代

```
research/autocad_com_api/_archived/
├── 1_connect_to_autocad.py          ❌ 基础 COM 连接探索
├── 2_file_operations.py             ❌ 文件操作探索
├── 3_command_execution.py           ❌ 命令执行探索
├── 4_error_handling.py              ❌ 错误处理探索
├── 5_version_check.py               ❌ 版本检测探索
├── 6_autocad_workflow.py            ❌ 基础工作流 (硬编码)
├── 6b_alternative_workflow.py       ❌ 替代方案
├── 7_menu_automation.py             ❌ 菜单自动化探索
├── 8_complete_example.py            ❌ 完整示例 (旧版)
├── README.md                        ❌ 归档说明
└── WORKFLOW_GUIDE.md                ❌ 旧版工作流指南
```

**统计**: 11 个文件
**预估大小**: ~200 KB
**价值**: 技术演进记录，但已无实用价值

---

### C2. 历史项目报告 (_archived/reports/)

**清理原因**: 过程性文档，项目开发历史记录

```
_archived/
├── README.md                        ❌ 归档说明
└── reports/
    ├── BUGFIX_VERSION_PARSING.md    ❌ Bug 修复报告
    ├── DATABASE_INTEGRATION_REPORT.md ❌ 数据库集成报告
    ├── DAY1_COMPLETION_REPORT.md    ❌ 第1天完成报告
    ├── DAY1_FINAL_SUMMARY.md        ❌ 第1天总结
    ├── DAY2_MORNING_COMPLETION_REPORT.md ❌ 第2天上午报告
    ├── DAY2_SUMMARY.md              ❌ 第2天总结
    ├── PHASE_BREAKDOWN.md           ❌ 阶段分解
    └── PROJECT_PLAN.md              ❌ 项目计划
```

**统计**: 9 个文件
**预估大小**: ~150 KB
**价值**: 历史记录，但已无实用价值

---

### C3. 临时修复文档 (docs/)

**清理原因**: 临时问题修复说明，问题已解决并集成到主文档

```
docs/
├── BPLOT_CONFIG_FIX_NOTES.md        ❌ BPLOT 配置修复说明
├── OCR_URL_UPDATE_GUIDE.md          ❌ OCR URL 更新指南
├── OUTPUT_DIR_CLEANUP_GUIDE.md      ❌ 输出目录清理指南
└── PDF_EXTRACTION_TROUBLESHOOTING.md ❌ PDF 提取故障排查
```

**统计**: 4 个文件
**预估大小**: ~30 KB
**价值**: 临时文档，已过时

---

### C4. 一次性迁移/配置脚本 (scripts/)

**清理原因**: 已执行完成，不再需要

```
scripts/
├── migrate_ocr_logging.py           ❌ OCR 日志迁移 (已执行)
├── migrate_add_output_dir_cleanup.py ❌ 输出清理迁移 (已执行)
├── migrate_add_use_bplot.py         ❌ BPLOT 迁移 (已执行)
├── auto_migrate.py                  ❌ 自动迁移工具 (已执行)
├── add_menu_operations.py           ❌ 添加菜单操作 (一次性)
├── add_screenshot_extract_step.py   ❌ 添加截图提取 (一次性)
├── add_bplot_config.py              ❌ 添加 BPLOT 配置 (一次性)
├── enable_output_cleanup.py         ❌ 启用输出清理 (一次性)
├── update_bplot_with_pre_post.py    ❌ 更新 BPLOT 配置 (一次性)
└── update_ocr_url.py                ❌ 更新 OCR URL (一次性)
```

**统计**: 10 个文件
**预估大小**: ~50 KB
**价值**: 历史工具，已完成使命

---

### C5. 诊断/提取工具 (可选清理)

**清理原因**: 临时诊断工具，非核心功能

```
scripts/
├── diagnose_pdf_extraction.py       ⚠️ PDF 提取诊断 (可选保留)
├── extract_drawing_info.py          ⚠️ 图纸信息提取 (可选保留)
├── batch_extract_info.py            ⚠️ 批量提取信息 (可选保留)
├── pdf_ocr_with_umi.py              ⚠️ PDF OCR 工具 (可选保留)
└── check_raw_bplot_config.py        ⚠️ 原始配置检查 (可选清理)
```

**统计**: 5 个文件
**预估大小**: ~30 KB
**价值**: 诊断工具，偶尔有用

**建议**: 保留前 4 个，清理最后 1 个

---

## 📊 清理统计总览

| 分类 | 文件数 | 预估大小 | 决策 |
|------|--------|---------|------|
| **核心文件** | 6 | ~100 KB | ✅ 保留 |
| **强关联 - 代码** | 34 | ~200 KB | ✅ 保留 |
| **强关联 - 文档** | 25 | ~500 KB | ✅ 保留 |
| **强关联 - 脚本** | 11 | ~80 KB | ✅ 保留 |
| **历史归档代码** | 11 | ~200 KB | ❌ 清理 |
| **历史报告** | 9 | ~150 KB | ❌ 清理 |
| **临时文档** | 4 | ~30 KB | ❌ 清理 |
| **一次性脚本** | 10 | ~50 KB | ❌ 清理 |
| **诊断工具** | 5 | ~30 KB | ⚠️ 部分清理 (1个) |
| **其他文件** | 34 | ~17.7 MB | ✅ 保留 |

### 清理前后对比

| 指标 | 清理前 | 清理后 | 变化 |
|------|--------|--------|------|
| **文件总数** | 149 | ~114 | -35 (-23.5%) |
| **文档/代码** | ~1.3 MB | ~0.88 MB | -0.42 MB |
| **项目大小** | 19 MB | ~18.5 MB | -0.5 MB |

---

## 📋 详细清理列表

### 确认清理的文件 (35个)

#### 1. 历史归档代码 (11个)
```
research/autocad_com_api/_archived/1_connect_to_autocad.py
research/autocad_com_api/_archived/2_file_operations.py
research/autocad_com_api/_archived/3_command_execution.py
research/autocad_com_api/_archived/4_error_handling.py
research/autocad_com_api/_archived/5_version_check.py
research/autocad_com_api/_archived/6_autocad_workflow.py
research/autocad_com_api/_archived/6b_alternative_workflow.py
research/autocad_com_api/_archived/7_menu_automation.py
research/autocad_com_api/_archived/8_complete_example.py
research/autocad_com_api/_archived/README.md
research/autocad_com_api/_archived/WORKFLOW_GUIDE.md
```

#### 2. 历史报告 (9个)
```
_archived/README.md
_archived/reports/BUGFIX_VERSION_PARSING.md
_archived/reports/DATABASE_INTEGRATION_REPORT.md
_archived/reports/DAY1_COMPLETION_REPORT.md
_archived/reports/DAY1_FINAL_SUMMARY.md
_archived/reports/DAY2_MORNING_COMPLETION_REPORT.md
_archived/reports/DAY2_SUMMARY.md
_archived/reports/PHASE_BREAKDOWN.md
_archived/reports/PROJECT_PLAN.md
```

#### 3. 临时文档 (4个)
```
docs/BPLOT_CONFIG_FIX_NOTES.md
docs/OCR_URL_UPDATE_GUIDE.md
docs/OUTPUT_DIR_CLEANUP_GUIDE.md
docs/PDF_EXTRACTION_TROUBLESHOOTING.md
```

#### 4. 一次性脚本 (10个)
```
scripts/migrate_ocr_logging.py
scripts/migrate_add_output_dir_cleanup.py
scripts/migrate_add_use_bplot.py
scripts/auto_migrate.py
scripts/add_menu_operations.py
scripts/add_screenshot_extract_step.py
scripts/add_bplot_config.py
scripts/enable_output_cleanup.py
scripts/update_bplot_with_pre_post.py
scripts/update_ocr_url.py
```

#### 5. 诊断工具 (1个)
```
scripts/check_raw_bplot_config.py
```

---

## ✅ 保留文件清单 (114个)

### 核心和强关联文件

详见上述 "强关联文件 (必须保留)" 章节。

**总计**:
- 核心文件: 6
- 代码模块: 34
- 文档: 25
- 脚本: 11
- 配置: 3
- 其他: 35

---

## 🔄 清理执行方案

### 方案: 安全归档 (推荐)

**操作**: 移动到 `_archived_cleanup_20251104/` 目录

**优势**:
- ✅ 完全可恢复
- ✅ 保留原始文件结构
- ✅ 生成详细清理日志
- ✅ 不影响 Git 历史

**执行命令**:
```bash
# 创建归档目录
mkdir -p _archived_cleanup_20251104

# 移动文件 (保持目录结构)
# ... (详细命令见执行脚本)
```

---

## ⚠️ 注意事项

1. **Git 提交建议**: 清理后建议创建一个清理提交
2. **备份确认**: 移动到归档目录，30天后可永久删除
3. **文档更新**: 需要更新引用已删除文件的文档链接
4. **测试验证**: 清理后运行核心功能测试

---

## 📝 后续行动

1. ✅ **用户审查本报告**
2. ⏳ **用户确认清理列表**
3. ⏳ **执行清理操作**
4. ⏳ **生成清理日志**
5. ⏳ **验证核心功能**

---

**报告生成完成！请审查上述清理列表，确认后将执行清理操作。**

**确认方式**:
- 回复 "**确认清理**" - 执行清理
- 回复 "**保留 [文件路径]**" - 从清理列表移除指定文件
- 回复 "**调整**" + 说明 - 修改清理策略
