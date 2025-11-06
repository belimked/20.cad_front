# PDF 文件重组织功能 - 执行计划

**任务ID:** pdf_reorganize_feature
**创建时间:** 2025-11-06
**状态:** 执行中

---

## 需求描述

完成 PDF 信息提取后，自动执行文件重组织：
1. 在处理目录同级创建 `xxx_convert` 目录
2. PDF 文件重命名：原文件名 → `sheet_number`（图号）
3. 在数据库记录新目录和新文件名

**用户选择：**
- 图号缺失：跳过文件，记录日志（选项A）
- 文件名冲突：追加序号 `_1`, `_2`...（选项A，记录异常）
- 数据库字段：新增 5 个字段（同意）
- 触发时机：MinerU 识别后自动执行（选项A）
- 原文件处理：保留原文件
- 权限继承：是

---

## 技术方案

**方案选择：** 方案 3（混合方案）

**核心设计：**
1. 创建独立的 `PDFReorganizeService` 服务
2. 在 `MinerUService` 中集成自动调用
3. 支持手动和自动两种模式

---

## 执行步骤

### 阶段 1：数据库表结构更新

#### 1.1 创建迁移脚本
- 文件：`scripts/migrate_add_conversion_fields.py`
- 新增字段：
  - `converted_directory` VARCHAR(500)
  - `converted_filename` VARCHAR(255)
  - `conversion_status` VARCHAR(20) DEFAULT 'pending'
  - `conversion_error` TEXT
  - `converted_at` DATETIME

#### 1.2 更新 ORM 模型
- 文件：`src/models/dwg_drawing_sheet.py`
- 添加 5 个新字段到 `DWGDrawingSheet` 类
- 定义状态常量：pending/completed/failed/skipped

### 阶段 2：创建 PDF 重组织服务

#### 2.1 创建服务类骨架
- 文件：`src/services/pdf_reorganize_service.py`
- 类：`PDFReorganizeService`

#### 2.2 实现核心方法
- `reorganize_pdfs()` - 主流程
- `_create_convert_directory()` - 创建目录
- `_generate_unique_filename()` - 处理冲突
- `_copy_and_rename_pdf()` - 文件操作
- `_update_database_record()` - 更新数据库

### 阶段 3：集成到 MinerUService

#### 3.1 修改 MinerUService
- 文件：`src/services/mineru_service.py`
- 在 `batch_recognize_pdfs()` 末尾集成调用
- 新增 `_reorganize_converted_pdfs()` 方法

### 阶段 4：配置管理

#### 4.1 更新 AutoCAD 配置
- 文件：`scripts/update_autocad_config_reorganize.py`
- 新增 `auto_reorganize_pdfs` 字段

### 阶段 5：测试脚本

#### 5.1 单元测试
- 文件：`scripts/test_pdf_reorganize.py`

#### 5.2 集成测试
- 文件：`scripts/test_mineru_with_reorganize.py`

### 阶段 6：文档更新

#### 6.1-6.2 更新文档
- `scripts/CLAUDE.md`
- `src/services/CLAUDE.md`

---

## 关键决策

1. **文件操作：** 使用 `shutil.copy2()` 保留元数据
2. **冲突处理：** 追加序号（`_1`, `_2`...）
3. **错误处理：** 跳过无图号文件，记录 `skipped` 状态
4. **事务管理：** 使用现有 `db_session`
5. **并发安全：** 在 MinerUService 线程安全框架内调用

---

## 预期时间

**总计：** ~2.5 小时

---

## 进度跟踪

- [ ] 阶段 1：数据库表结构更新
- [ ] 阶段 2：创建 PDF 重组织服务
- [ ] 阶段 3：集成到 MinerUService
- [ ] 阶段 4：配置管理
- [ ] 阶段 5：测试脚本
- [ ] 阶段 6：文档更新
