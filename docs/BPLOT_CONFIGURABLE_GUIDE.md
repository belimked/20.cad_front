# Bplot配置化工作流使用指南

## 📋 问题解答

### 问题1: 为什么数据库表 `ocr_recognition_logs` 和 `ocr_preprocessing_performance` 为空？

**原因：**

`11_bplot_auto_workflow.py` 是一个**研究脚本**（硬编码版本），用于验证工作流的可行性，**不会**将OCR日志写入数据库。

**解决方案：**

使用**配置化版本** `12_bplot_configurable_workflow.py`，它会：
- ✅ 从数据库读取 `menu_operations` 配置
- ✅ 自动记录OCR识别日志到 `ocr_recognition_logs`
- ✅ 自动记录预处理性能到 `ocr_preprocessing_performance`
- ✅ 支持文件清理和归档
- ✅ 与API服务无缝集成

---

### 问题2: 为什么识别的是"设置批量打印图纸表"而不是"选择批量打印图纸"？

**原因：**

硬编码脚本 `11_bplot_auto_workflow.py` 的按钮文本列表中，"设置批量打印图纸表"排在前面，优先匹配。

**解决方案：**

配置化版本 `12_bplot_configurable_workflow.py` 从数据库读取配置，你可以在配置中指定：

```json
{
    "type": "menu",
    "method": "ocr",
    "text": "选择批量打印图纸",  // 主要匹配文本
    "alternative_texts": [      // 备选匹配文本
        "设置批量打印图纸表",
        "选择图纸",
        "图纸表"
    ]
}
```

系统会：
1. 首先尝试匹配 `"选择批量打印图纸"`
2. 如果失败，依次尝试 `alternative_texts` 中的文本
3. 找到第一个匹配的就点击

---

## 🚀 使用配置化工作流

### 方式1: 独立运行脚本

```bash
# 确保已添加bplot配置到数据库
python scripts/add_bplot_config.py

# 运行配置化工作流
python research/autocad_com_api/12_bplot_configurable_workflow.py
```

**输出示例：**
```
================================================================================
AutoCAD Batch Plot (bplot) 配置化工作流
================================================================================

✅ 已加载配置: bplot
   描述: AutoCAD批量打印(bplot)全自动化工作流 - OCR识别按钮并自动输入
   OCR启用: True
   OCR地址: http://127.0.0.1:11224/api/ocr

🔧 工作流步骤: 5 个
   1. [command] 执行BPLOT命令（批量打印）
   2. [menu] 点击设置批量打印图纸表按钮
   3. [input] 键盘输入all选择所有图纸
   4. [screenshot_extract] 提取选中图纸数量
   5. [screenshot_extract] 提取总页数

步骤 1: 打开CAD和文件
...
步骤 3: 执行菜单操作

📋 操作 1/5: command
  [模式] 键盘输入命令
  ⌨️  输入: _.bplot
  ⏎  按下回车键
  ✅ 命令已输入: _.bplot

📋 操作 2/5: menu
  [模式] OCR文字识别
  查找文本: '选择批量打印图纸'
  ✅ 使用Umi-OCR服务: http://127.0.0.1:11224/api/ocr
  ✅ 已激活AutoCAD窗口
  截图完成: 646x519（耗时: 0.123秒）
  ✅ 找到文本: '选择批量打印图纸' at (391, 249)
  🖱️  已点击按钮

📋 操作 3/5: input
  [模式] 键盘输入
  ⌨️  输入: all
  ⏎  按下回车键
  ✅ 输入完成

📋 操作 4/5: screenshot_extract
  [模式] 截图文本提取
  ✅ 提取成功: selected_sheets = 15

📋 操作 5/5: screenshot_extract
  [模式] 截图文本提取
  ✅ 提取成功: total_pages = 15

✅ 菜单操作完成

🎉 Bplot配置化工作流执行成功！

📊 提取到的数据:
   selected_sheets: 15
   total_pages: 15
```

---

### 方式2: 通过API调用

```python
import requests

response = requests.post("http://your-api-server/api/dwg/process", json={
    "dwg_url": "http://example.com/file.dwg",
    "config_name": "bplot"  # 指定使用bplot配置
})

result = response.json()
print(result)
```

**返回示例：**
```json
{
    "task_id": "task_20251103_150907_abc123",
    "status": "completed",
    "extracted_data": {
        "selected_sheets": "15",
        "total_pages": "15"
    },
    "ocr_logs": [
        {
            "target_text": "选择批量打印图纸",
            "found": true,
            "matched_text": "选择批量打印图纸",
            "confidence": 0.98,
            "position": {"x": 391, "y": 249},
            "total_time": 2.456
        },
        ...
    ]
}
```

---

## 📊 数据库日志记录

配置化工作流会自动记录：

### 1. OCR识别日志 (`ocr_recognition_logs`)

```sql
SELECT
    id,
    target_text,
    found,
    matched_text,
    confidence,
    matched_version,
    total_time,
    preprocessing_count,
    total_texts_found,
    created_at
FROM ocr_recognition_logs
ORDER BY created_at DESC
LIMIT 10;
```

**示例数据：**
| id | target_text | found | matched_text | confidence | total_time |
|----|-------------|-------|--------------|------------|------------|
| 1 | 选择批量打印图纸 | 1 | 选择批量打印图纸 | 0.9800 | 2.456 |
| 2 | all | 1 | all | 1.0000 | 1.234 |

### 2. 预处理性能日志 (`ocr_preprocessing_performance`)

```sql
SELECT
    id,
    recognition_log_id,
    method_name,
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

**示例数据：**
| method_name | processing_time | ocr_time | texts_found | target_found |
|-------------|-----------------|----------|-------------|--------------|
| original | 0.012 | 1.234 | 72 | 1 |
| grayscale | 0.023 | 1.456 | 68 | 1 |
| binary_otsu | 0.034 | 1.123 | 45 | 0 |
| high_contrast | 0.028 | 1.345 | 71 | 1 |

---

## 🔄 两种版本对比

| 特性 | 硬编码版本<br>(11_bplot_auto_workflow.py) | 配置化版本<br>(12_bplot_configurable_workflow.py) |
|------|-------------------------------------------|--------------------------------------------------|
| 配置来源 | 代码中硬编码 | 数据库 `menu_operations` |
| OCR日志 | ❌ 不记录 | ✅ 自动记录 |
| 性能日志 | ❌ 不记录 | ✅ 自动记录 |
| 修改方式 | 修改代码 + 重启 | 更新数据库即可 |
| API集成 | ❌ 独立脚本 | ✅ 无缝集成 |
| alternative_texts | ✅ 硬编码支持 | ✅ 配置支持 |
| 文件管理 | ✅ 手动 | ✅ 自动清理/归档 |
| 用途 | 研究和验证 | 生产环境 |

---

## 📝 配置示例

### 数据库中的 `menu_operations` 字段

```json
[
    {
        "type": "command",
        "method": "keyboard",
        "text": "_.bplot",
        "description": "执行BPLOT命令（批量打印）",
        "wait_time": 5.0
    },
    {
        "type": "menu",
        "method": "ocr",
        "text": "选择批量打印图纸",
        "description": "点击设置批量打印图纸表按钮",
        "alternative_texts": [
            "设置批量打印图纸表",
            "选择图纸",
            "图纸表",
            "Select Drawings"
        ],
        "wait_time": 2.0
    },
    {
        "type": "input",
        "method": "keyboard",
        "text": "all",
        "description": "键盘输入all选择所有图纸",
        "wait_time": 2.0
    },
    {
        "type": "screenshot_extract",
        "target_pattern": "选中图纸[:\\s]*(\\d+)",
        "save_to": "selected_sheets",
        "description": "提取选中图纸数量",
        "required": false,
        "wait_time": 0.5
    },
    {
        "type": "screenshot_extract",
        "target_pattern": "共\\s*(\\d+)\\s*页",
        "save_to": "total_pages",
        "description": "提取总页数",
        "alternative_patterns": [
            "Total[:\\s]*(\\d+)",
            "(\\d+)\\s*sheets"
        ],
        "required": false,
        "wait_time": 0.5
    }
]
```

---

## 🔧 修改配置

### 方式1: 通过Python脚本

```python
from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig
import json

db = SessionLocal()
try:
    # 获取bplot配置
    config = db.query(AutoCADConfig).filter(
        AutoCADConfig.config_name == 'bplot'
    ).first()

    # 修改 menu_operations
    operations = json.loads(config.menu_operations)

    # 例如：修改第2步的文本
    operations[1]['text'] = '新的按钮文本'
    operations[1]['alternative_texts'] = ['备选文本1', '备选文本2']

    # 保存
    config.menu_operations = json.dumps(operations, ensure_ascii=False)
    db.commit()

    print("✅ 配置已更新")
finally:
    db.close()
```

### 方式2: 直接执行SQL

```sql
-- 备份现有配置
SELECT menu_operations FROM autocad_config WHERE config_name = 'bplot';

-- 更新配置
UPDATE autocad_config
SET menu_operations = '[
    {
        "type": "menu",
        "method": "ocr",
        "text": "新的按钮文本",
        "alternative_texts": ["备选1", "备选2"]
    }
]'
WHERE config_name = 'bplot';
```

---

## ⚠️ 重要提示

### 1. 使用配置化版本的前提条件

- ✅ 数据库中已存在 `bplot` 配置
- ✅ Umi-OCR服务已启动 (http://127.0.0.1:11224)
- ✅ `ocr_recognition_logs` 和 `ocr_preprocessing_performance` 表已创建
- ✅ AutoCAD已正确安装

### 2. 配置验证

```bash
# 验证bplot配置是否存在
python -c "
from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig

db = SessionLocal()
config = db.query(AutoCADConfig).filter(
    AutoCADConfig.config_name == 'bplot'
).first()

if config:
    print(f'✅ bplot配置存在')
    print(f'   描述: {config.description}')
else:
    print('❌ bplot配置不存在，请运行: python scripts/add_bplot_config.py')

db.close()
"
```

### 3. 日志查询

```sql
-- 查看最近的OCR识别记录
SELECT
    ocr.id,
    ocr.target_text,
    ocr.found,
    ocr.total_time,
    ocr.created_at,
    COUNT(perf.id) as preprocessing_methods_count
FROM ocr_recognition_logs ocr
LEFT JOIN ocr_preprocessing_performance perf ON perf.recognition_log_id = ocr.id
WHERE ocr.created_at > NOW() - INTERVAL 1 HOUR
GROUP BY ocr.id
ORDER BY ocr.created_at DESC;
```

---

## 🎯 迁移建议

**从硬编码版本迁移到配置化版本：**

1. ✅ 运行 `python scripts/add_bplot_config.py` 添加配置
2. ✅ 验证配置是否正确
3. ✅ 测试运行 `python research/autocad_com_api/12_bplot_configurable_workflow.py`
4. ✅ 检查数据库日志是否记录
5. ✅ 在API中使用 `config_name='bplot'` 参数

**保留硬编码版本的场景：**
- 快速原型验证
- 不需要日志记录
- 临时调试

---

**文档版本:** v1.0
**最后更新:** 2025-11-03
**作者:** CAD Auto Processor Team
