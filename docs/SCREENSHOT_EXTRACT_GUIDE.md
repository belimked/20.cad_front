# 全屏截图数据提取功能使用指南

## 📋 功能简介

`screenshot_extract` 是一个强大的自动化操作类型，用于在工作流程中执行**全屏截图 + OCR识别 + 正则提取数据**。

### 典型应用场景

- ✅ 提取打印进度的总页数（如："共 183 页"）
- ✅ 提取当前进度（如："正在处理第 29 页"）
- ✅ 提取百分比进度（如："75%"）
- ✅ 提取任意动态显示的文本信息

---

## 🎯 核心特性

1. **全屏截图**：不受窗口位置限制，扫描整个屏幕
2. **多OCR引擎**：自动选择最佳引擎（Umi-OCR > Tesseract > EasyOCR）
3. **正则提取**：使用正则表达式灵活匹配各种文本模式
4. **数据库存储**：自动保存提取结果到 `ocr_recognition_logs` 表
5. **调试友好**：显示识别到的文本，方便调试正则表达式

---

## 📝 配置格式

### 基本配置

```json
{
  "type": "screenshot_extract",
  "target_pattern": "共 (\\d+) 页",
  "save_to": "total_pages",
  "required": false,
  "wait_time": 1.0
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|------|--------|------|
| `type` | string | ✅ | - | 必须是 `screenshot_extract` |
| `target_pattern` | string | ✅ | - | 正则表达式，用 `()` 包住要提取的部分 |
| `save_to` | string | ❌ | `extracted_value` | 保存的变量名 |
| `required` | boolean | ❌ | `false` | 是否必须找到（true=找不到中断流程） |
| `wait_time` | float | ❌ | `1.0` | 操作后等待时间（秒） |

---

## 🚀 快速开始

### 示例1：提取打印总页数

#### 1. 完整配置示例

```json
[
  {
    "type": "menu",
    "method": "ocr",
    "text": "依云",
    "wait_time": 0.5
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "CAD批量打图精灵",
    "wait_time": 1.0
  },
  {
    "type": "menu",
    "method": "ocr",
    "text": "打印",
    "wait_time": 2.0
  },
  {
    "type": "screenshot_extract",
    "target_pattern": "共 (\\d+) 页",
    "save_to": "total_pages",
    "required": false,
    "wait_time": 1.0
  }
]
```

#### 2. 添加到数据库

**方式A：使用脚本自动添加**

```bash
python scripts/add_screenshot_extract_step.py
```

**方式B：直接SQL更新**

```sql
UPDATE autocad_config
SET menu_operations = '[
  {"type": "menu", "method": "ocr", "text": "依云", "wait_time": 0.5},
  {"type": "menu", "method": "ocr", "text": "CAD批量打图精灵", "wait_time": 1.0},
  {"type": "menu", "method": "ocr", "text": "打印", "wait_time": 2.0},
  {"type": "screenshot_extract", "target_pattern": "共 (\\\\d+) 页", "save_to": "total_pages", "required": false, "wait_time": 1.0}
]'
WHERE config_name = 'default';
```

**注意**：SQL中的正则表达式需要**双重转义**：`\\\\d+`（4个反斜杠）

#### 3. 运行工作流程

```bash
python research/autocad_com_api/9_configurable_workflow.py
```

#### 4. 预期输出

```
📋 操作 4/4: screenshot_extract
  [模式] 截图文本提取
  🔍 提取模式: 共 (\d+) 页
  ✅ 使用Umi-OCR: http://10.3.19.121:1224/api/ocr

  📸 执行全屏截图...
  ✅ 截图完成: 1920x1080 (耗时: 0.123秒)

  🔍 OCR识别中...
  ✅ 识别到 156 个文本区域
  ⏱️  OCR耗时: 2.456秒

  🔎 查找匹配文本...
  【调试】前20个识别结果:
    1. 'AutoCAD'
    2. '正在处理图纸'
    3. '共 183 页'
    ...

  ✅ 找到匹配!
     完整文本: '共 183 页'
     提取值: '183'

  💾 已保存截图: data/20251028_143052/fullscreen_extract_total_pages.png
  💾 已保存OCR文本: data/20251028_143052/fullscreen_extract_total_pages_ocr.txt

  📊 总耗时: 2.789秒
  💾 已保存到OCR日志 (ID: 42)
     提取数据: {"total_pages": "183"}
     截图文件: data/20251028_143052/fullscreen_extract_total_pages.png
     文本文件: data/20251028_143052/fullscreen_extract_total_pages_ocr.txt

  ✅ 提取成功: total_pages = 183
```

### 📁 保存的文件

每次执行全屏截图提取会自动保存以下文件：

**1. 截图文件** (`fullscreen_extract_{变量名}.png`)
- 完整的全屏截图
- PNG格式，原始分辨率
- 例如：`fullscreen_extract_total_pages.png`

**2. OCR文本文件** (`fullscreen_extract_{变量名}_ocr.txt`)
- 包含所有OCR识别的文本
- UTF-8编码，方便查看
- 格式示例：

```
全屏OCR识别结果
================================================================================
时间: 2025-10-28 14:30:52
目标模式: 共 (\d+) 页
匹配文本: 共 183 页
提取值: 183
================================================================================

识别到的所有文本 (共 156 条):
--------------------------------------------------------------------------------
   1. AutoCAD
   2. 正在处理图纸
   3. 共 183 页
   4. 正在打印第 29 页
   5. 75%
   ...
```

**3. 文件目录结构**

```
data/
└── 20251028_143052/          # 时间戳目录
    ├── fullscreen_extract_total_pages.png      # 截图
    └── fullscreen_extract_total_pages_ocr.txt  # OCR文本
```

如果配置了 `ocr_screenshot_base_dir`，则保存到指定目录。

**目录配置：**
- 默认：`data/` 目录
- 可配置：`config.ocr_screenshot_base_dir`
- 时间戳格式：`config.ocr_screenshot_timestamp_format`（默认：`%Y%m%d_%H%M%S`）

---

## 📚 更多示例

### 示例2：提取当前页码

```json
{
  "type": "screenshot_extract",
  "target_pattern": "正在打印第 (\\d+) 页",
  "save_to": "current_page",
  "required": false,
  "wait_time": 0.5
}
```

### 示例3：提取百分比进度

```json
{
  "type": "screenshot_extract",
  "target_pattern": "(\\d+)%",
  "save_to": "progress_percent",
  "required": false,
  "wait_time": 0.5
}
```

### 示例4：提取文件名

```json
{
  "type": "screenshot_extract",
  "target_pattern": "文件名[:：]\\s*([\\w\\-\\.]+)",
  "save_to": "filename",
  "required": false,
  "wait_time": 0.5
}
```

- 匹配："文件名: test.dwg" → 提取：`test.dwg`
- 匹配："文件名：my-file.dwg" → 提取：`my-file.dwg`

### 示例5：提取时间

```json
{
  "type": "screenshot_extract",
  "target_pattern": "剩余时间[:：]\\s*(\\d+:\\d+:\\d+)",
  "save_to": "remaining_time",
  "required": false,
  "wait_time": 0.5
}
```

- 匹配："剩余时间: 00:15:30" → 提取：`00:15:30`

### 示例6：多个提取步骤

```json
[
  {"type": "menu", "method": "ocr", "text": "打印", "wait_time": 2.0},
  {
    "type": "screenshot_extract",
    "target_pattern": "共 (\\d+) 页",
    "save_to": "total_pages",
    "required": false,
    "wait_time": 0.5
  },
  {
    "type": "screenshot_extract",
    "target_pattern": "正在打印第 (\\d+) 页",
    "save_to": "current_page",
    "required": false,
    "wait_time": 0.5
  },
  {
    "type": "screenshot_extract",
    "target_pattern": "(\\d+)%",
    "save_to": "progress",
    "required": false,
    "wait_time": 0.5
  }
]
```

---

## 🗄️ 数据存储

### 存储位置

提取的数据自动保存到两个地方：

#### 1. 数据库（`ocr_recognition_logs` 表）
- 保存提取结果和统计信息
- 便于查询和分析

#### 2. 文件系统
- **截图文件**：`{基础目录}/{时间戳}/fullscreen_extract_{变量名}.png`
- **OCR文本**：`{基础目录}/{时间戳}/fullscreen_extract_{变量名}_ocr.txt`
- 便于后续查看和调试

### 关键字段说明

| 字段 | 说明 | 示例值 |
|-----|------|--------|
| `target_text` | 正则表达式模式 | `"共 (\\d+) 页"` |
| `matched_text` | 完整匹配的文本 | `"共 183 页"` |
| `matched_version` | 固定为 `fullscreen_extract` | `"fullscreen_extract"` |
| `ocr_results_summary` | **提取的JSON数据** | `{"total_pages": "183"}` |
| `screenshot_dir` | **截图保存目录** | `"data/20251028_143052"` |
| `screenshots_saved` | **保存的截图数量** | `1` |
| `total_texts_found` | OCR识别文本总数 | `156` |
| `total_time` | 总耗时（秒） | `2.789` |
| `screenshot_time` | 截图耗时（秒） | `0.123` |
| `ocr_time` | OCR识别耗时（秒） | `2.456` |
| `status` | 状态 | `"success"` |

### 查询提取结果

**SQL查询：**

```sql
SELECT
    id,
    target_text,
    matched_text,
    ocr_results_summary,
    total_texts_found,
    total_time,
    created_at
FROM ocr_recognition_logs
WHERE matched_version = 'fullscreen_extract'
ORDER BY created_at DESC
LIMIT 10;
```

**Python查询：**

```python
from src.utils.database import SessionLocal
from src.models.ocr_recognition_log import OCRRecognitionLog
import json

db = SessionLocal()
logs = db.query(OCRRecognitionLog)\
    .filter_by(matched_version='fullscreen_extract')\
    .order_by(OCRRecognitionLog.created_at.desc())\
    .limit(10)\
    .all()

for log in logs:
    print(f"ID: {log.id}")
    print(f"目标模式: {log.target_text}")
    print(f"匹配文本: {log.matched_text}")

    # 解析提取的数据
    if log.ocr_results_summary:
        extracted = json.loads(log.ocr_results_summary)
        print(f"提取数据: {extracted}")

    print(f"耗时: {log.total_time}秒")
    print(f"时间: {log.created_at}")
    print("-" * 80)

db.close()
```

### 在代码中访问提取的数据

```python
from research.autocad_com_api.9_configurable_workflow import ConfigurableAutoCADWorkflow

workflow = ConfigurableAutoCADWorkflow(config_name='default')
success = workflow.run()

if success:
    # 获取提取的数据
    total_pages = workflow.extracted_data.get('total_pages')
    current_page = workflow.extracted_data.get('current_page')

    print(f"总页数: {total_pages}")
    print(f"当前页: {current_page}")
```

---

## 🔧 正则表达式指南

### 基础语法

| 模式 | 说明 | 示例 |
|-----|------|------|
| `\d` | 数字（0-9） | `\d+` 匹配一个或多个数字 |
| `\w` | 字母数字下划线 | `\w+` 匹配单词 |
| `\s` | 空白字符 | `\s*` 匹配0个或多个空格 |
| `()` | 捕获组（提取内容） | `共 (\d+) 页` 提取数字 |
| `[]` | 字符集 | `[0-9a-f]+` 匹配十六进制 |
| `+` | 一个或多个 | `\d+` |
| `*` | 零个或多个 | `\s*` |
| `?` | 零个或一个 | `\d?` |
| `\.` | 转义的点号 | `file\.txt` |

### 常用模式

**提取数字：**
```
(\d+)           # 整数
(\d+\.\d+)      # 小数
```

**提取时间：**
```
(\d{2}:\d{2}:\d{2})           # 时:分:秒
(\d{4}-\d{2}-\d{2})           # 年-月-日
```

**提取文件名：**
```
([^\s]+\.dwg)                 # xxx.dwg
([A-Za-z0-9_\-\.]+)           # 字母数字下划线破折号点号
```

**提取中文+数字：**
```
共\s*(\d+)\s*页              # 共 183 页
第\s*(\d+)\s*个              # 第 5 个
```

### 调试正则表达式

1. **查看调试输出**：运行时会显示前20个识别结果
2. **在线测试**：使用 https://regex101.com/ 测试正则表达式
3. **逐步完善**：先用简单模式，再逐步添加约束

---

## ⚙️ 配置管理

### 查看当前配置

```bash
python scripts/autocad_config_manager.py show 1
```

### 更新配置

**方式1：使用脚本（推荐）**

编辑 `scripts/add_screenshot_extract_step.py`，修改 `new_operations` 数组，然后运行：

```bash
python scripts/add_screenshot_extract_step.py
```

**方式2：直接SQL**

```sql
UPDATE autocad_config
SET menu_operations = '你的JSON配置'
WHERE config_name = 'default';
```

### 验证配置

```bash
python -c "
from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig
import json

db = SessionLocal()
config = db.query(AutoCADConfig).filter_by(config_name='default').first()
operations = json.loads(config.menu_operations)
print(json.dumps(operations, ensure_ascii=False, indent=2))
db.close()
"
```

---

## 🐛 故障排查

### 问题1：未找到匹配文本

**现象：**
```
❌ 未找到匹配的文本
```

**解决方案：**

1. 查看调试输出的前20个识别结果
2. 检查正则表达式是否正确
3. 尝试简化正则表达式（如：`\d+` 而不是 `共 (\d+) 页`）
4. 增加 `wait_time` 确保界面完全显示

### 问题2：OCR识别不准确

**现象：**
```
识别到的文本不包含目标内容
```

**解决方案：**

1. 确保Umi-OCR服务正常运行（推荐）
2. 检查屏幕分辨率和字体大小
3. 增加等待时间，确保界面完全加载
4. 尝试其他OCR引擎（Tesseract/EasyOCR）

### 问题3：提取了错误的值

**现象：**
```
提取值: '29'  # 期望是总页数183，实际提取了当前页29
```

**解决方案：**

1. 使用更精确的正则表达式
2. 添加上下文约束（如：`共\s*(\d+)\s*页` 而不是 `(\d+)`）
3. 调整 `wait_time` 确保目标文本已显示

### 问题4：保存数据库失败

**现象：**
```
⚠️ 保存OCR日志失败: ...
```

**解决方案：**

1. 检查数据库连接配置
2. 确认 `ocr_recognition_logs` 表存在
3. 查看完整错误信息
4. 注意：保存失败不影响主流程执行

---

## 📊 性能优化

### OCR引擎选择

| 引擎 | 优点 | 缺点 | 推荐场景 |
|-----|------|------|---------|
| **Umi-OCR** | 准确率最高、速度快 | 需要局域网服务 | ⭐⭐⭐⭐⭐ 首选 |
| **Tesseract** | 中文UI识别好 | 需要安装引擎 | ⭐⭐⭐⭐ 备选 |
| **EasyOCR** | 安装简单 | 速度较慢 | ⭐⭐⭐ 最后选择 |

### 优化建议

1. **使用Umi-OCR**：配置 `umi_ocr_enabled=true`
2. **合理设置等待时间**：确保界面稳定后再截图
3. **精简正则表达式**：越简单越快
4. **避免频繁提取**：合并多个提取步骤

---

## 🔗 相关文档

- [菜单操作完整指南](MENU_OPERATIONS_GUIDE.md)
- [OCR配置指南](TESSERACT_INSTALLATION_GUIDE.md)
- [数据库配置指南](DATABASE_CONFIG_GUIDE.md)

---

## 📝 更新日志

### v1.0.0 (2025-10-28)

- ✅ 新增 `screenshot_extract` 操作类型
- ✅ 支持全屏OCR识别
- ✅ 支持正则表达式提取
- ✅ 自动保存到 `ocr_recognition_logs` 表
- ✅ 支持多OCR引擎（Umi-OCR/Tesseract/EasyOCR）
- ✅ 提供配置更新脚本

---

## 🎉 总结

`screenshot_extract` 功能特点：

1. ✅ **简单配置**：只需一个正则表达式
2. ✅ **自动保存**：提取结果自动入库
3. ✅ **灵活扩展**：支持任意文本模式提取
4. ✅ **调试友好**：显示识别结果方便调试
5. ✅ **性能优秀**：全屏OCR约2-3秒完成

**完整示例：**

```json
{
  "type": "screenshot_extract",
  "target_pattern": "共 (\\d+) 页",
  "save_to": "total_pages",
  "required": false,
  "wait_time": 1.0
}
```

**一键添加：**

```bash
python scripts/add_screenshot_extract_step.py
```

**立即运行：**

```bash
python research/autocad_com_api/9_configurable_workflow.py
```

就这么简单！🚀
