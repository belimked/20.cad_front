# Bplot配置脚本修复说明

## 🔧 修复内容

### 问题描述

之前创建的 bplot 配置脚本使用了错误的数据库字段名和表名，导致无法正常执行：

1. ❌ **错误的字段名**: `workflow_steps` （实际应该是 `menu_operations`）
2. ❌ **错误的表名**: `autocad_configs` （实际应该是 `autocad_config`）
3. ❌ **不存在的字段**: `ocr_enabled`, `ocr_screenshot_enabled`

### 修复内容

**修正后的字段映射：**

| 旧字段名 | 新字段名 | 说明 |
|---------|---------|------|
| `workflow_steps` | `menu_operations` | 工作流步骤JSON |
| `autocad_configs` (表名) | `autocad_config` (表名) | 数据库表名 |
| `ocr_enabled` | ❌ 删除 | 模型中不存在 |
| `ocr_screenshot_enabled` | ❌ 删除 | 模型中不存在 |

**修改的文件：**
- ✅ `scripts/add_bplot_config.py` - Python安装脚本
- ✅ `scripts/add_bplot_config.sql` - SQL安装脚本
- ✅ `docs/BPLOT_CONFIG_GUIDE.md` - 配置文档

---

## 📖 数据库Schema参考

根据 `src/models/autocad_config.py` 的定义：

```python
class AutoCADConfig(Base):
    __tablename__ = 'autocad_config'  # 表名（单数）

    # 工作流步骤字段
    menu_operations = Column(Text, comment='菜单操作配置（JSON格式）')
    # 格式示例：
    # [
    #   {"type": "command", "method": "keyboard", "text": "_.bplot", ...},
    #   {"type": "menu", "method": "ocr", "text": "设置批量打印图纸表", ...},
    #   {"type": "input", "method": "keyboard", "text": "all", ...},
    #   {"type": "screenshot_extract", "target_pattern": "...", ...}
    # ]

    # OCR配置字段
    ocr_screenshot_base_dir = Column(String(500), ...)
    umi_ocr_enabled = Column(Boolean, default=True, ...)
    umi_ocr_service_url = Column(String(200), default='http://127.0.0.1:11224', ...)
    # ... 其他OCR相关字段
```

---

## ✅ 现在可以安全执行

### 方式1: Python脚本（推荐）

```bash
# 在项目根目录执行
python scripts/add_bplot_config.py
```

**预期输出：**
```
================================================================================
添加 bplot 配置到数据库
================================================================================

✅ 成功添加 bplot 配置

📋 配置详情:
   名称: bplot
   描述: AutoCAD批量打印(bplot)全自动化工作流 - OCR识别按钮并自动输入
   OCR启用: 是
   OCR地址: http://127.0.0.1:11224/api/ocr
   截图目录: screenshots/bplot_auto
   工作流步骤: 5 个
```

### 方式2: SQL脚本

```bash
# 连接到数据库
mysql -h 10.3.19.189 -P 3313 -u root -p cad_auto_processor

# 执行脚本
source scripts/add_bplot_config.sql;
```

或者直接执行：
```bash
mysql -h 10.3.19.189 -P 3313 -u root -p cad_auto_processor < scripts/add_bplot_config.sql
```

---

## 🔍 验证配置

### 查询配置是否存在

```sql
SELECT
    config_name,
    description,
    umi_ocr_enabled,
    umi_ocr_service_url,
    created_at
FROM autocad_config
WHERE config_name = 'bplot';
```

### 查看完整工作流步骤

```sql
SELECT
    config_name,
    menu_operations
FROM autocad_config
WHERE config_name = 'bplot';
```

**预期结果：** `menu_operations` 字段包含5个步骤的JSON数组

---

## 📝 工作流步骤说明

配置包含以下5个步骤（存储在 `menu_operations` 字段）：

### 1️⃣ 执行BPLOT命令
```json
{
    "type": "command",
    "method": "keyboard",
    "text": "_.bplot",
    "description": "执行BPLOT命令（批量打印）",
    "wait_time": 5.0
}
```

### 2️⃣ 点击设置按钮（OCR识别）
```json
{
    "type": "menu",
    "method": "ocr",
    "text": "设置批量打印图纸表",
    "description": "点击设置批量打印图纸表按钮",
    "alternative_texts": [
        "选择批量打印图纸",
        "选择图纸",
        "图纸表",
        "Select Drawings",
        "Add Sheets"
    ],
    "wait_time": 1.0
}
```

### 3️⃣ 输入all选择所有图纸
```json
{
    "type": "input",
    "method": "keyboard",
    "text": "all",
    "description": "键盘输入all选择所有图纸",
    "wait_time": 2.0
}
```

### 4️⃣ 提取选中图纸数
```json
{
    "type": "screenshot_extract",
    "target_pattern": "选中图纸[:\\s]*(\\d+)",
    "save_to": "selected_sheets",
    "description": "提取选中图纸数量",
    "required": false,
    "wait_time": 0.5
}
```

### 5️⃣ 提取总页数
```json
{
    "type": "screenshot_extract",
    "target_pattern": "共\\s*(\\d+)\\s*页",
    "save_to": "total_pages",
    "description": "提取总页数",
    "alternative_patterns": [
        "Total[:\\s]*(\\d+)",
        "(\\d+)\\s*sheets",
        "页数[:\\s]*(\\d+)"
    ],
    "required": false,
    "wait_time": 0.5
}
```

---

## 💡 使用方法

### API调用示例

```python
import requests

# 方式1: 直接指定配置名
response = requests.post("http://api_url/process", json={
    "dwg_url": "http://example.com/file.dwg",
    "config_name": "bplot"
})

# 方式2: 使用use_bplot标志（如果API支持自动路由）
response = requests.post("http://api_url/process", json={
    "dwg_url": "http://example.com/file.dwg",
    "use_bplot": true
})
```

### 返回数据示例

```json
{
    "task_id": "task_20251102_183045_abc123",
    "status": "completed",
    "extracted_data": {
        "selected_sheets": "15",
        "total_pages": "15"
    }
}
```

---

## ⚠️ 注意事项

### 1. SQL中的正则表达式转义

SQL字符串中需要**四个反斜杠**（`\\\\`）：

```sql
-- SQL中
"target_pattern": "共\\\\s*(\\\\d+)\\\\s*页"

-- 等价于Python中的
r"共\s*(\d+)\s*页"
```

### 2. 字段对应关系

| Python代码 | SQL字段名 | JSON格式 |
|-----------|----------|---------|
| `menu_operations=json.dumps(...)` | `menu_operations` | TEXT类型 |

### 3. 配置覆盖

如果配置 `bplot` 已存在：
- **Python脚本**: 会提示是否覆盖（需要手动确认）
- **SQL脚本**: 使用 `WHERE NOT EXISTS` 不会重复插入

---

## 🎯 Git提交记录

```
commit 49a1f6e
fix(bplot-config): 修正数据库字段名和表名

关键修复：
- 字段名：workflow_steps → menu_operations
- 表名：autocad_configs → autocad_config
- 删除不存在的字段：ocr_enabled, ocr_screenshot_enabled
```

---

**文档版本:** v1.1
**最后更新:** 2025-11-03
**修复日期:** 2025-11-03
**作者:** CAD Auto Processor Team
