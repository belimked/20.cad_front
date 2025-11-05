# AutoCAD 工作流 PDF 自动提取集成指南

**日期**: 2025-10-31
**版本**: v1.0
**作者**: AI Assistant

---

## 📋 功能概述

本次集成在 AutoCAD 自动化工作流程中添加了 **步骤5: PDF 图纸信息自动提取** 功能。

### 工作流程

```
步骤0: 清理输出目录（可选）
    ↓
步骤1: 关闭并打开 AutoCAD + 加载 DWG 文件
    ↓
步骤2: 验证文件加载
    ↓
步骤3: 执行菜单操作（批量打印/导出PDF）
    ↓
步骤4: 监控输出文件生成
    ↓
【新增】步骤5: 批量提取PDF图纸信息 ⭐
    ↓
关闭 AutoCAD（可选）
```

### 核心功能

- ✅ 自动扫描输出目录中的所有 PDF 文件
- ✅ 批量 OCR 识别（使用 Umi-OCR 文档 API）
- ✅ 智能提取图纸信息：
  - 图号、图纸类型、材料、公司
  - 设计/审核/批准人员
  - 技术要求、BOM表
  - 比例、重量等
- ✅ 生成 CSV 汇总报告（Excel 兼容）
- ✅ 错误处理和重试机制
- ✅ 完全可配置（可启用/禁用）

---

## 🚀 快速开始

### 1. 运行数据库迁移

首先需要为数据库添加新的配置字段：

```bash
# 连接到你的数据库，运行迁移脚本
mysql -u your_user -p your_database < migrations/20251031_add_pdf_extraction_config.sql

# 或使用 Python 脚本（如果有）
python scripts/migrate_database.py
```

### 2. 更新配置

有两种方式启用 PDF 提取功能：

#### 方式A: 通过数据库直接更新

```sql
-- 启用 PDF 提取功能
UPDATE autocad_config
SET pdf_extraction_enabled = TRUE
WHERE config_name = 'default';

-- 可选：自定义配置
UPDATE autocad_config
SET
    pdf_extraction_enabled = TRUE,
    pdf_extraction_umi_service_url = 'http://10.3.19.63:11224',
    pdf_extraction_mode = 'fullPage',
    pdf_extraction_parser = 'multi_line',
    pdf_extraction_generate_csv = TRUE,
    pdf_extraction_csv_filename = 'extraction_summary.csv',
    pdf_extraction_fail_on_error = FALSE,
    pdf_extraction_max_retries = 2
WHERE config_name = 'default';
```

#### 方式B: 通过 Web 界面/API 更新（如果有）

访问配置管理页面，找到 "PDF 提取配置" 部分：

- **启用 PDF 提取**: ✅ 勾选
- **Umi-OCR 服务地址**: `http://10.3.19.63:11224`
- **提取模式**: `fullPage` (推荐)
- **文本解析器**: `multi_line` (推荐)
- **生成 CSV 报告**: ✅ 勾选
- **失败时中断流程**: ❌ 不勾选（推荐）

### 3. 运行工作流

```python
from research.autocad_com_api.configurable_workflow import ConfigurableAutoCADWorkflow

# 加载配置
workflow = ConfigurableAutoCADWorkflow(config_name='default')

# 运行工作流
dwg_file = r"F:\cad\caddd\your_file.dwg"
success = workflow.run(dwg_file_path=dwg_file)

if success:
    print("✅ 工作流完成，PDF已生成并提取信息！")
else:
    print("❌ 工作流失败")
```

### 4. 查看结果

工作流完成后，可以在以下目录找到结果：

```
F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs\
├── *.pdf                           # 生成的PDF文件
└── pdf_extraction/                 # PDF提取结果目录 ⭐
    ├── jsonl/                      # OCR识别结果（JSONL格式）
    │   ├── file1.jsonl
    │   ├── file2.jsonl
    │   └── ...
    ├── extracted_info/             # 提取的结构化信息（JSON格式）
    │   ├── file1.json
    │   ├── file2.json
    │   └── ...
    └── extraction_summary.csv      # CSV汇总报告 ⭐⭐⭐
```

**CSV 报告示例**:

| 序号 | 文件名 | 状态 | 图号 | 图纸类型 | 材料 | 公司 | ... |
|------|--------|------|------|----------|------|------|-----|
| 1 | file1.pdf | success | PCX-01-01 | 装配图 | Q235B | 深圳市奇见科技有限公司 | ... |
| 2 | file2.pdf | success | PCX-01-02 | 零件图 | 304不锈钢 | 深圳市奇见科技有限公司 | ... |

---

## ⚙️ 配置详解

### 配置字段说明

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **pdf_extraction_enabled** | Boolean | `False` | 是否启用PDF信息提取 |
| **pdf_extraction_output_dir** | String | `null` | 提取结果输出目录（为空则使用`{输出目录}/pdf_extraction`） |
| **pdf_extraction_umi_service_url** | String | `http://10.3.19.63:11224` | Umi-OCR 文档 API 地址 |
| **pdf_extraction_mode** | String | `fullPage` | 提取模式：`fullPage`（全页）/ `mixed`（混合） |
| **pdf_extraction_parser** | String | `multi_line` | 解析器：`multi_line`（多列）/ `single_line`（单列） |
| **pdf_extraction_generate_csv** | Boolean | `True` | 是否生成CSV汇总报告 |
| **pdf_extraction_csv_filename** | String | `extraction_summary.csv` | CSV报告文件名 |
| **pdf_extraction_fail_on_error** | Boolean | `False` | 提取失败是否中断整个流程 |
| **pdf_extraction_max_retries** | Integer | `2` | 单个PDF提取失败时的最大重试次数 |

### 推荐配置

#### 生产环境配置

```sql
UPDATE autocad_config SET
    pdf_extraction_enabled = TRUE,
    pdf_extraction_umi_service_url = 'http://10.3.19.63:11224',
    pdf_extraction_mode = 'fullPage',
    pdf_extraction_parser = 'multi_line',
    pdf_extraction_generate_csv = TRUE,
    pdf_extraction_fail_on_error = FALSE,  -- 不中断流程
    pdf_extraction_max_retries = 2
WHERE config_name = 'production';
```

#### 测试环境配置

```sql
UPDATE autocad_config SET
    pdf_extraction_enabled = TRUE,
    pdf_extraction_umi_service_url = 'http://10.3.19.63:11224',
    pdf_extraction_mode = 'fullPage',
    pdf_extraction_parser = 'multi_line',
    pdf_extraction_generate_csv = TRUE,
    pdf_extraction_fail_on_error = TRUE,   -- 测试时发现问题立即停止
    pdf_extraction_max_retries = 1
WHERE config_name = 'test';
```

---

## 📊 性能指标

基于 20 个样本验证的性能数据：

| 指标 | 数值 | 说明 |
|------|------|------|
| **平均处理时间** | 0.88秒/文件 | OCR识别时间 |
| **总处理时间（含提取）** | ~1.12秒/文件 | OCR + 信息提取 |
| **成功率** | 90% | 18/20 成功处理 |
| **准确率** | 83-94% | 各字段提取准确率 |

### 183个文件预计耗时

- **OCR识别**: 183 × 0.88秒 ≈ **2.7分钟**
- **信息提取**: 183 × 0.24秒 ≈ **0.7分钟**
- **总耗时**: 约 **3.5分钟**

---

## 🎯 使用场景

### 场景1: 批量处理图纸

```python
# 处理包含183个图纸的DWG文件
workflow = ConfigurableAutoCADWorkflow(config_name='default')
success = workflow.run(dwg_file_path="大型项目.dwg")

# 结果:
# - 生成183个PDF文件
# - 自动提取所有图纸信息
# - 生成Excel可打开的CSV报告
```

### 场景2: 仅提取特定PDF

```python
# 1. 禁用自动提取
workflow = ConfigurableAutoCADWorkflow(config_name='no_extraction')
workflow.run(dwg_file_path="项目.dwg")

# 2. 手动提取特定PDF
from scripts.batch_extract_info import process_pdf_to_jsonl, extract_info_from_jsonl

pdf_file = "outputs/特定图纸.pdf"
jsonl_file = process_pdf_to_jsonl(pdf_file, "outputs/jsonl")
info_file = extract_info_from_jsonl(jsonl_file, "outputs/info.json")
```

### 场景3: 自定义输出目录

```sql
-- 将提取结果输出到单独的目录
UPDATE autocad_config SET
    pdf_extraction_output_dir = 'F:\cad\extraction_results\20251031'
WHERE config_name = 'default';
```

---

## 🔧 故障排除

### 问题1: PDF提取失败

**症状**:
```
❌ OCR识别失败
```

**解决方案**:
1. 检查 Umi-OCR 服务是否运行
   ```bash
   curl http://10.3.19.63:11224/api/doc/upload
   ```
2. 检查网络连接
3. 验证 PDF 文件完整性
4. 增加重试次数：`pdf_extraction_max_retries = 5`

### 问题2: CSV报告乱码

**症状**:
Excel打开CSV报告显示乱码

**解决方案**:
- 报告使用 `utf-8-sig` 编码（含BOM），Excel应能正确识别
- 如仍有问题，使用记事本另存为 UTF-8 格式后再用Excel打开

### 问题3: 提取准确率低

**症状**:
图号、材料等字段识别错误率高

**解决方案**:
1. 检查 PDF 质量（扫描图vs矢量图）
2. 调整 OCR 参数（如需要，联系管理员）
3. 查看 `docs/RANDOM_20_VALIDATION_REPORT.md` 了解已知问题
4. 考虑使用多区域过滤（针对装配图）

### 问题4: 处理时间过长

**症状**:
183个文件处理超过10分钟

**解决方案**:
1. 检查 OCR 服务性能
2. 考虑批量处理而非实时处理
3. 调整超时时间：修改代码中的 `timeout=120` 参数

---

## 📝 代码示例

### 示例1: 完整工作流

```python
#!/usr/bin/env python3
"""
完整的 AutoCAD 到 PDF 提取工作流
"""
from research.autocad_com_api.configurable_workflow import ConfigurableAutoCADWorkflow

def main():
    # 加载配置
    workflow = ConfigurableAutoCADWorkflow(config_name='default')

    # DWG文件路径
    dwg_file = r"F:\cad\projects\PCX20.01 主体钢结构.dwg"

    # 运行工作流
    print("开始处理...")
    success = workflow.run(dwg_file_path=dwg_file)

    if success:
        print("✅ 成功！")
        print("📂 PDF文件: F:\\cad\\outputs\\")
        print("📊 CSV报告: F:\\cad\\outputs\\pdf_extraction\\extraction_summary.csv")
    else:
        print("❌ 失败，请查看日志")

    workflow.cleanup()

if __name__ == "__main__":
    main()
```

### 示例2: 条件启用PDF提取

```python
# 根据文件大小决定是否提取
import os
from pathlib import Path

dwg_file = "large_project.dwg"
file_size_mb = os.path.getsize(dwg_file) / (1024 * 1024)

# 大文件（>100MB）才提取
if file_size_mb > 100:
    # 启用PDF提取
    workflow = ConfigurableAutoCADWorkflow(config_name='with_extraction')
else:
    # 不提取
    workflow = ConfigurableAutoCADWorkflow(config_name='no_extraction')

workflow.run(dwg_file_path=dwg_file)
```

### 示例3: 自定义错误处理

```python
try:
    workflow = ConfigurableAutoCADWorkflow(config_name='default')
    success = workflow.run(dwg_file_path="project.dwg")

    if not success:
        # 记录到日志系统
        logger.error("工作流失败")

        # 发送通知
        send_email_notification("AutoCAD工作流失败", "请检查日志")

except Exception as e:
    logger.critical(f"严重错误: {e}")
    raise
finally:
    workflow.cleanup()
```

---

## 🧪 测试

### 单元测试

```bash
# 测试PDF提取功能
python -m pytest tests/test_pdf_extraction.py -v

# 测试工作流集成
python -m pytest tests/test_workflow_integration.py -v
```

### 手动测试清单

- [ ] 启用PDF提取，运行工作流
- [ ] 验证 PDF 文件生成
- [ ] 检查 `pdf_extraction` 目录是否创建
- [ ] 打开 CSV 报告，验证数据
- [ ] 测试失败场景（网络断开、OCR服务停止）
- [ ] 验证 `fail_on_error=False` 时流程继续执行
- [ ] 验证 `fail_on_error=True` 时流程中断

---

## 📚 相关文档

- [RANDOM_20_VALIDATION_REPORT.md](../docs/RANDOM_20_VALIDATION_REPORT.md) - 20个样本验证报告
- [ASSEMBLY_DRAWING_FILTER_REPORT.md](../docs/ASSEMBLY_DRAWING_FILTER_REPORT.md) - 装配图过滤策略
- [PDF_EXTRACTION_TOOLS.md](../docs/PDF_EXTRACTION_TOOLS.md) - 提取工具详细说明
- [configurable_workflow.py](../research/autocad_com_api/configurable_workflow.py) - 工作流核心代码

---

## 🎓 最佳实践

### 1. 分阶段启用

```
第1阶段：测试环境验证
    ↓
第2阶段：小批量生产测试（10-20个文件）
    ↓
第3阶段：全量生产部署
```

### 2. 监控关键指标

- 成功率（目标 >90%）
- 平均处理时间（目标 <2秒/文件）
- 提取准确率（目标 >85%）

### 3. 定期审查

- 每周查看 CSV 报告，抽查准确性
- 每月分析失败案例，优化规则
- 每季度更新提取规则和OCR配置

### 4. 备份策略

```sql
-- 在启用PDF提取前备份配置
SELECT * FROM autocad_config WHERE config_name = 'default' INTO OUTFILE '/backup/config_20251031.csv';
```

---

## 🔄 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2025-10-31 | 首次集成PDF提取功能 |

---

## 📞 支持

如有问题，请联系：

- **技术支持**: tech-support@company.com
- **GitHub Issues**: https://github.com/your-org/project/issues
- **文档**: https://docs.company.com/autocad-workflow

---

## ✅ 集成检查清单

部署前请确认：

- [ ] 数据库迁移已运行
- [ ] Umi-OCR 文档 API 服务可访问
- [ ] 配置已更新（`pdf_extraction_enabled = TRUE`）
- [ ] 输出目录有写权限
- [ ] 依赖脚本存在：`pdf_ocr_with_umi.py`, `extract_drawing_info.py`
- [ ] 测试环境验证通过
- [ ] 文档已阅读

---

**🎉 恭喜！PDF自动提取功能已成功集成到工作流中！**
