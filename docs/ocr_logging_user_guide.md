# OCR日志和文件管理功能 - 使用指南

## 📚 功能概述

本次更新添加了以下功能：

1. **OCR识别日志记录**：记录每次OCR识别的详细信息和性能指标
2. **预处理方法性能统计**：记录每个预处理方法的识别效果和耗时
3. **截图文件管理**：支持自定义截图目录、自动清理/归档旧文件

---

## 🚀 快速开始

### 步骤1：执行数据库迁移

```bash
cd /Users/saul/IdeaProjects/100.AI.TrainData
python scripts/migrate_ocr_logging.py
```

迁移脚本会：
- 创建 `ocr_recognition_logs` 表
- 创建 `ocr_preprocessing_performance` 表
- 在 `autocad_config` 表添加7个新字段
- 插入字典配置项

### 步骤2：配置AutoCAD工作流程

在数据库中更新配置：

```sql
UPDATE autocad_config
SET
  -- OCR日志开关
  ocr_enable_detailed_logging = TRUE,

  -- 截图目录配置
  ocr_screenshot_base_dir = 'screenshots',
  ocr_screenshot_timestamp_format = '%Y%m%d_%H%M%S',

  -- 文件清理配置
  ocr_file_cleanup_enabled = TRUE,
  ocr_file_cleanup_strategy = 'archive',  -- delete/archive/none
  ocr_file_archive_dir = 'screenshots_archive',
  ocr_file_retention_days = 7

WHERE config_name = 'default';
```

### 步骤3：运行测试

```python
from research.autocad_com_api.configurable_workflow import ConfigurableAutoCADWorkflow

workflow = ConfigurableAutoCADWorkflow(config_name='default')
workflow.run(dwg_file_path="path/to/file.dwg")
```

---

## 📋 功能详解

### 1. OCR识别日志记录

每次OCR识别都会记录：

**主日志表 (`ocr_recognition_logs`)**：
- 目标文本、是否找到、匹配文本、置信度
- 性能指标：总耗时、截图耗时、预处理耗时、OCR耗时、合并耗时
- 预处理统计：使用的方法列表、生成的图像数量
- 识别统计：识别到的文本总数、去重后的唯一文本数
- 文件信息：截图目录、保存的截图数量

**性能详情表 (`ocr_preprocessing_performance`)**：
- 每个预处理方法的耗时（预处理时间、OCR时间、总时间）
- 识别结果（识别到的文本数、是否找到目标、最高/平均置信度）
- 文件信息（图像路径、大小）

### 2. 文件管理策略

**清理策略 (`ocr_file_cleanup_strategy`)**：
- `delete`：直接删除旧文件，不保留
- `archive`：移动到归档目录保存
- `none`：不清理，持续累积

**保留期限 (`ocr_file_retention_days`)**：
- 默认7天
- 超过保留期的文件会根据策略处理

**归档目录 (`ocr_file_archive_dir`)**：
- 默认 `screenshots_archive`
- 可配置为任意路径

### 3. 时间戳格式

支持的格式：
- `%Y%m%d_%H%M%S`：20251027_143025
- `%Y%m%d_%H%M%S_%f`：20251027_143025_123456
- `%Y-%m-%d_%H-%M-%S`：2025-10-27_14-30-25
- `%Y%m%d`：20251027

---

## 📊 查询日志数据

### 查询最近的OCR识别记录

```sql
SELECT
    id,
    target_text,
    found,
    matched_text,
    confidence,
    matched_version,
    total_time,
    ocr_time,
    preprocessing_count,
    total_texts_found,
    unique_texts_count,
    created_at
FROM ocr_recognition_logs
ORDER BY created_at DESC
LIMIT 10;
```

### 查询某次识别的详细性能

```sql
-- 查看主日志
SELECT * FROM ocr_recognition_logs WHERE id = 1;

-- 查看各方法性能
SELECT
    method_name,
    method_order,
    processing_time,
    ocr_time,
    total_time,
    texts_found,
    target_found,
    max_confidence
FROM ocr_preprocessing_performance
WHERE recognition_log_id = 1
ORDER BY method_order;
```

### 统计最有效的预处理方法

```sql
SELECT
    method_name,
    COUNT(*) AS total_count,
    AVG(ocr_time) AS avg_ocr_time,
    AVG(max_confidence) AS avg_max_confidence,
    SUM(target_found) AS times_found_target
FROM ocr_preprocessing_performance
GROUP BY method_name
ORDER BY times_found_target DESC, avg_max_confidence DESC;
```

---

## 🔧 故障排查

### 问题1：迁移失败

**症状**：运行迁移脚本时报错

**排查**：
```bash
# 检查数据库连接
python -c "from src.utils.database import SessionLocal; db = SessionLocal(); print('✅ 连接成功')"

# 检查表是否已存在
mysql -u root -p -e "SHOW TABLES LIKE 'ocr_%'"
```

**解决**：
- 如果表已存在但结构不同，删除后重新迁移
- 如果是权限问题，检查数据库用户权限

### 问题2：日志未记录

**症状**：OCR识别成功但数据库无日志

**排查**：
```sql
-- 检查是否启用日志
SELECT ocr_enable_detailed_logging FROM autocad_config WHERE config_name = 'default';

-- 查看最近的日志
SELECT COUNT(*) FROM ocr_recognition_logs WHERE created_at > NOW() - INTERVAL 1 HOUR;
```

**解决**：
- 确保 `ocr_enable_detailed_logging = TRUE`
- 检查日志输出是否有错误信息

### 问题3：文件清理未执行

**症状**：旧文件没有被清理

**排查**：
```sql
-- 检查清理配置
SELECT
    ocr_file_cleanup_enabled,
    ocr_file_cleanup_strategy,
    ocr_file_retention_days
FROM autocad_config
WHERE config_name = 'default';
```

**解决**：
- 确保 `ocr_file_cleanup_enabled = TRUE`
- 检查文件年龄是否超过保留期
- 查看日志输出的清理统计

---

## 📈 性能优化建议

1. **日志清理**：定期清理旧的OCR日志
   ```sql
   DELETE FROM ocr_recognition_logs WHERE created_at < NOW() - INTERVAL 30 DAY;
   ```

2. **索引优化**：如果日志表数据量大，检查索引
   ```sql
   SHOW INDEX FROM ocr_recognition_logs;
   SHOW INDEX FROM ocr_preprocessing_performance;
   ```

3. **文件归档**：定期将归档目录备份到外部存储
   ```bash
   tar -czf screenshots_archive_$(date +%Y%m%d).tar.gz screenshots_archive/
   ```

---

## 📝 数据库Schema

### ocr_recognition_logs 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| config_id | INT | 配置ID |
| task_log_id | BIGINT | 任务日志ID |
| target_text | VARCHAR(100) | 目标文本 |
| found | BOOLEAN | 是否找到 |
| matched_text | VARCHAR(200) | 匹配文本 |
| confidence | DECIMAL(5,4) | 置信度 |
| matched_version | VARCHAR(50) | 匹配版本 |
| position_x | INT | X坐标 |
| position_y | INT | Y坐标 |
| total_time | DECIMAL(10,3) | 总耗时(秒) |
| screenshot_time | DECIMAL(10,3) | 截图耗时(秒) |
| preprocessing_time | DECIMAL(10,3) | 预处理耗时(秒) |
| ocr_time | DECIMAL(10,3) | OCR耗时(秒) |
| merge_time | DECIMAL(10,3) | 合并耗时(秒) |
| preprocessing_methods | TEXT | 预处理方法(JSON) |
| preprocessing_count | INT | 预处理图像数 |
| ocr_results_summary | TEXT | OCR结果汇总(JSON) |
| total_texts_found | INT | 识别文本总数 |
| unique_texts_count | INT | 唯一文本数 |
| screenshot_dir | VARCHAR(500) | 截图目录 |
| screenshots_saved | INT | 截图数量 |
| status | VARCHAR(20) | 状态 |
| error_message | TEXT | 错误信息 |
| created_at | DATETIME | 创建时间 |

### ocr_preprocessing_performance 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| recognition_log_id | BIGINT | 识别日志ID |
| method_name | VARCHAR(50) | 方法名称 |
| method_order | INT | 执行顺序 |
| processing_time | DECIMAL(10,3) | 预处理耗时 |
| ocr_time | DECIMAL(10,3) | OCR耗时 |
| total_time | DECIMAL(10,3) | 总耗时 |
| texts_found | INT | 识别文本数 |
| target_found | BOOLEAN | 是否找到目标 |
| max_confidence | DECIMAL(5,4) | 最高置信度 |
| avg_confidence | DECIMAL(5,4) | 平均置信度 |
| image_path | VARCHAR(500) | 图像路径 |
| image_size_kb | INT | 图像大小(KB) |
| created_at | DATETIME | 创建时间 |

---

**更新日期**: 2025-10-27
**作者**: CAD Auto Processor Team
