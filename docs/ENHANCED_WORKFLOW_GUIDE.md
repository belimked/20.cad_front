# AutoCAD 批量打印完整工作流 - 使用指南

## 📋 概述

已成功创建并集成 `EnhancedWorkflow` 增强型工作流，支持完整的前置/主流程/后置操作。

## ✅ 完成的工作

### 1️⃣ **创建 EnhancedWorkflow 类**
- 📁 文件: `research/autocad_com_api/enhanced_workflow.py`
- ✨ 功能:
  - ✅ 支持前置操作（system_command, directory_cleanup）
  - ✅ 支持主流程（command, menu, input, screenshot_extract）
  - ✅ 支持后置操作（file_monitor, system_command）
  - ✅ 变量系统（保存和引用OCR提取的值）

### 2️⃣ **更新 bplot 配置**
- 📝 配置名: `bplot` (ID: 7)
- 📊 操作步骤: **13步**
  - 前置 (2步): 关闭CAD + 清空目录
  - 主流程 (9步): BPLOT命令 + OCR交互
  - 后置 (2步): 文件监控 + 关闭CAD

### 3️⃣ **集成到 task_processor**
- 📁 文件: `api/services/task_processor.py`
- ✨ 功能: `use_bplot=true` 时自动路由到 EnhancedWorkflow

---

## 🚀 使用方法

### **API 调用**

```bash
POST /api/v1/tasks/print
Content-Type: application/json

{
    "config_name": "bplot",
    "dwg_url": "http://10.3.19.199/cad/PCX2.dwg",
    "use_bplot": true
}
```

### **请求参数说明**

| 参数 | 说明 | 示例 |
|------|------|------|
| `config_name` | 配置名称 | `"bplot"` |
| `dwg_url` | DWG文件下载地址 | `"http://10.3.19.199/cad/PCX2.dwg"` |
| `use_bplot` | 使用增强型工作流 | `true` |

---

## 📊 完整工作流详情

### **前置操作 (2步)**

```
步骤1: [system_command] 强制关闭所有AutoCAD进程
  命令: taskkill /IM acad.exe /T /F
  忽略错误: 是
  等待: 2秒

步骤2: [directory_cleanup] 清空输出目录
  路径: F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000
  创建目录: 是
  等待: 1秒
```

### **主流程操作 (9步)**

```
步骤3: [command] 执行BPLOT命令
  方法: keyboard
  命令: _.bplot
  等待: 5秒

步骤4: [menu] OCR识别并点击按钮
  方法: ocr
  按钮文本: "选择要处理的图纸"
  等待: 2秒

步骤5: [input] 输入all
  文本: all
  回车前等待: 2秒
  回车次数: 2次
  等待: 2秒

步骤6: [screenshot_extract] 提取图纸数量
  正则: 选中图纸.*?(\d+)
  保存到变量: selected_sheets
  必需: 否
  等待: 0.5秒

步骤7-11: 打印设置操作
  - OCR点击"无"按钮
  - 输入 t
  - OCR点击"无"按钮
  - 输入 11 + 回车
  - OCR点击"确定"按钮
```

### **后置操作 (2步)**

```
步骤12: [file_monitor] 监控PDF生成
  监控路径: F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000
  文件模式: *.pdf
  期望数量: selected_sheets 变量值
  检查间隔: 2秒
  稳定持续时间: 10秒（10秒内无新文件才算完成）
  最大等待: 600秒

步骤13: [system_command] 关闭AutoCAD
  命令: taskkill /IM acad.exe /T /F
  忽略错误: 是
  等待: 1秒
```

---

## 🔍 执行流程监控

### **查看任务详情**

```bash
GET /api/v1/tasks/{task_id}
```

**响应示例:**
```json
{
  "code": 200,
  "data": {
    "task_id": "xxx-xxx-xxx",
    "status": "processing",
    "current_step": "执行AutoCAD工作流",
    "progress": 50,
    "steps": [
      {
        "step_name": "下载DWG文件",
        "status": "completed",
        "duration_seconds": 2.5
      },
      {
        "step_name": "执行AutoCAD工作流",
        "status": "running",
        "message": "正在执行步骤 6/13: 提取选中图纸数量"
      }
    ]
  }
}
```

---

## 🎯 关键特性

### ✅ **智能变量系统**

```python
# 步骤6: 提取图纸数量
{
  "type": "screenshot_extract",
  "target_pattern": r"选中图纸.*?(\d+)",
  "save_to": "selected_sheets"  # 保存到变量
}

# 步骤12: 使用变量
{
  "type": "file_monitor",
  "expected_count_variable": "selected_sheets"  # 引用变量
}
```

### ✅ **文件监控机制**

- **稳定性检测**: 10秒内无新文件才认为完成
- **数量验证**: 对比 `selected_sheets` 变量值
- **超时保护**: 最长等待10分钟

### ✅ **错误处理**

- **前置清理**: 忽略错误继续执行
- **可选步骤**: `screenshot_extract` 失败不中断
- **超时恢复**: 文件监控超时记录警告但继续

---

## 🛠️ 配置管理

### **查看当前配置**

```python
from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService

db = get_db_session()
service = AutoCADConfigService(db)
config = service.get_config(config_name="bplot")

print(f"配置ID: {config.id}")
print(f"描述: {config.description}")
```

### **修改配置**

```bash
# 运行更新脚本
python scripts/update_bplot_with_pre_post.py
```

---

## 📝 测试清单

- [ ] 前置操作: 确认CAD进程已关闭
- [ ] 前置操作: 确认输出目录已清空
- [ ] 主流程: CAD文件正确打开
- [ ] 主流程: BPLOT命令正确执行
- [ ] 主流程: OCR成功识别按钮
- [ ] 主流程: 正确提取图纸数量
- [ ] 后置操作: 文件监控正常工作
- [ ] 后置操作: 数量验证准确
- [ ] 后置操作: CAD进程已关闭

---

## 🐛 故障排查

### **问题1: OCR识别失败**
```
解决方案:
1. 检查 Umi-OCR 服务是否运行
2. 确认配置中的 umi_ocr_service_url 正确
3. 查看截图质量是否足够
```

### **问题2: 文件监控超时**
```
解决方案:
1. 检查输出目录是否正确
2. 确认AutoCAD打印设置正确
3. 增加 max_wait_time 参数
```

### **问题3: 数量不匹配**
```
解决方案:
1. 检查 screenshot_extract 是否成功
2. 查看 selected_sheets 变量值
3. 确认打印完成后的PDF数量
```

---

## 📞 支持

如有问题，请提供：
- 任务ID
- 错误日志
- 配置名称
- DWG文件信息
