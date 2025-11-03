# Bplot 配置化工作流文档

## 📋 概述

将bplot全自动化工作流配置化，存储到数据库的 `autocad_configs` 表中，使其可以像标准工作流一样通过配置管理。

---

## 🗂️ 配置名称

**config_name:** `bplot`

---

## 📝 工作流步骤 (workflow_steps)

### **步骤1: 执行BPLOT命令**

```json
{
    "type": "command",
    "method": "keyboard",
    "text": "_.bplot",
    "description": "执行BPLOT命令（批量打印）",
    "wait_time": 5.0
}
```

**说明：**
- 使用键盘模拟输入 `_.bplot` 命令
- 等待5秒让对话框完全打开

---

### **步骤2: 点击设置按钮**

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

**说明：**
- 使用OCR识别按钮位置
- 支持多种按钮文本（中英文）
- 点击后等待1秒

---

### **步骤3: 输入all**

```json
{
    "type": "input",
    "method": "keyboard",
    "text": "all",
    "description": "键盘输入all选择所有图纸",
    "wait_time": 2.0
}
```

**说明：**
- 键盘输入 `all` 并回车
- 等待2秒让系统处理

---

### **步骤4: 提取选中图纸数**

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

**说明：**
- 截图并OCR识别
- 使用正则表达式提取数字
- 保存到 `selected_sheets` 变量
- 非必需（`required: false`）

---

### **步骤5: 提取总页数**

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

**说明：**
- 支持多种格式的总页数提取
- 中英文兼容
- 保存到 `total_pages` 变量

---

## ⚙️ OCR配置

```json
{
    "ocr_enabled": true,
    "umi_ocr_enabled": true,
    "umi_ocr_service_url": "http://127.0.0.1:11224",
    "umi_ocr_api_path": "/api/ocr",
    "umi_ocr_timeout": 60,
    "umi_ocr_limit_side_len": 2880
}
```

---

## 📸 截图配置

```json
{
    "ocr_screenshot_enabled": true,
    "ocr_screenshot_base_dir": "screenshots/bplot_auto",
    "ocr_screenshot_timestamp_format": "%Y%m%d_%H%M%S",
    "ocr_file_retention_days": 7,
    "ocr_enable_detailed_logging": true
}
```

---

## 🎨 图像预处理方法

```json
{
    "ocr_preprocessing_methods": [
        "original",
        "grayscale",
        "binary_otsu",
        "binary_adaptive",
        "denoise_gaussian",
        "high_contrast"
    ]
}
```

**生成的图像：**
- `bplot_dialog_original.png` - 原始截图
- `bplot_dialog_grayscale.png` - 灰度
- `bplot_dialog_binary_otsu.png` - Otsu二值化
- `bplot_dialog_binary_adaptive.png` - 自适应二值化
- `bplot_dialog_denoise_gaussian.png` - 高斯去噪
- `bplot_dialog_high_contrast.png` - 高对比度

---

## 📂 目录结构

```
screenshots/bplot_auto/
  ├── 20251102_183045/           # 步骤2截图（点击按钮前）
  │   ├── bplot_dialog_original.png
  │   ├── bplot_dialog_grayscale.png
  │   ├── bplot_dialog_binary_otsu.png
  │   └── ... (共6个版本)
  │
  └── 20251102_183050/           # 步骤4-5截图（输入all后）
      ├── bplot_info_original.png
      ├── bplot_info_grayscale.png
      └── ... (共6个版本)
```

---

## 🚀 安装配置

### **方式1: 使用Python脚本（推荐）**

```bash
python scripts/add_bplot_config.py
```

**输出示例：**
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

🔧 工作流步骤:
   1. [command] 执行BPLOT命令（批量打印）
   2. [menu] 点击设置批量打印图纸表按钮
   3. [input] 键盘输入all选择所有图纸
   4. [screenshot_extract] 提取选中图纸数量
   5. [screenshot_extract] 提取总页数
```

### **方式2: 使用SQL脚本**

```bash
mysql -h 10.3.19.189 -P 3313 -u root -p cad_auto_processor < scripts/add_bplot_config.sql
```

---

## 💡 使用方法

### **API调用示例**

```python
# 方式1: 直接指定配置名
{
    "dwg_url": "http://example.com/file.dwg",
    "config_name": "bplot"
}

# 方式2: 使用use_bplot标志（自动路由）
{
    "dwg_url": "http://example.com/file.dwg",
    "use_bplot": true
}
```

### **返回结果**

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

## 🔄 与硬编码版本的对比

| 特性 | 硬编码版本 | 配置化版本 |
|------|-----------|-----------|
| 步骤定义 | 代码中固定 | 数据库中配置 |
| 修改方式 | 修改代码+重启 | 更新数据库即可 |
| 版本管理 | Git | 数据库版本 |
| 灵活性 | 低 | 高 |
| 可维护性 | 中 | 高 |
| 调试难度 | 中 | 低（有日志） |

---

## 📊 工作流类型对比

### **标准工作流 (config_name='default')**
- 菜单导航 → OCR点击 → 截图提取

### **Bplot工作流 (config_name='bplot')**
- 键盘命令 → OCR点击 → 键盘输入 → 截图提取

---

## 🔧 自定义配置

可以创建多个bplot变体：

```python
# bplot_variant1 - 仅提取信息，不点击
# bplot_variant2 - 自定义图纸选择
# bplot_variant3 - 指定打印机设置
```

---

## ⚠️ 注意事项

1. **正则表达式转义**
   - SQL中需要双反斜杠：`共\\\\s*(\\\\d+)\\\\s*页`
   - Python中单反斜杠：`r"共\s*(\d+)\s*页"`

2. **wait_time调优**
   - 根据实际AutoCAD响应速度调整
   - 网络环境差的情况下增加等待时间

3. **alternative_texts**
   - 支持中英文混合
   - 按优先级排序

4. **required字段**
   - `false` = 失败不影响流程继续
   - `true` = 失败则中止流程

---

**文档版本:** v1.0
**最后更新:** 2025-11-02
**作者:** CAD Auto Processor Team
