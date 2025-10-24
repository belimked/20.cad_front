# AutoCAD 完整自动化流程 - 使用说明

## 📋 概述

这个完整的自动化流程包含三个步骤：

```
01. 关闭现有 CAD → 启动 CAD → 打开指定 DWG 文件
02. 验证文件已加载（使用 sleep 等待机制）
03. 打开 CAD 指定菜单（使用 UI Automation）
```

## 📦 依赖安装

```powershell
pip install pywin32 psutil pywinauto
```

## 📂 文件说明

| 文件 | 功能 | 说明 |
|------|------|------|
| `6_autocad_workflow.py` | **核心工作流程** | 步骤1和2的完整实现 |
| `7_menu_automation.py` | UI 自动化 | 步骤3的菜单操作实现 |
| `8_complete_example.py` | 完整示例 | 整合所有步骤的演示 |

## 🚀 快速开始

### 方式 1：使用完整工作流程脚本（推荐）

**文件：** `6_autocad_workflow.py`

这个脚本实现了步骤 1 和 2：

```python
from pathlib import Path

# 创建工作流程
from research.autocad_com_api.autocad_workflow import AutoCADWorkflow

workflow = AutoCADWorkflow()

# 步骤 1: 关闭并打开 CAD
dwg_file = r"C:\path\to\your\drawing.dwg"
workflow.step1_close_and_open_cad(dwg_file)

# 步骤 2: 验证加载
workflow.step2_verify_file_loaded(max_wait_time=30)

# 步骤 3: 菜单操作（见下方）
```

**修改配置：**

在 `6_autocad_workflow.py` 的 `main()` 函数中修改：

```python
# 第 268 行左右
dwg_file = r"C:\你的实际路径\drawing.dwg"
```

**运行：**

```powershell
python 6_autocad_workflow.py
```

**预期结果：**

```
============================================================
步骤 1: 关闭现有 CAD 并打开指定文件
============================================================
📄 目标文件: C:\...\drawing.dwg

🔍 检查现有 AutoCAD 进程...
✅ 已关闭 1 个 AutoCAD 进程
⏳ 等待 3 秒以确保进程完全关闭...

🚀 启动 AutoCAD 并打开文件...
✅ AutoCAD 已启动
⏳ 等待 5 秒让 AutoCAD 完全初始化...
📂 打开文件: C:\...\drawing.dwg
✅ 文件已打开: drawing.dwg

============================================================
步骤 2: 验证文件已加载
============================================================
⏳ 最大等待时间: 30 秒
🔄 检查间隔: 2.0 秒

🔍 检查 #1 (已用时: 0.0秒)...
  ✅ AutoCAD 进程正在运行
  ✅ 文档仍然打开: drawing.dwg
  ✅ 文档是活动文档
  ✅ 模型空间实体数: 125

✅ 文件验证成功！
📊 文档信息:
   - 文件名: drawing.dwg
   - 完整路径: C:\...\drawing.dwg
   - 实体数量: 125
```

### 方式 2：使用 UI 自动化操作菜单

**文件：** `7_menu_automation.py`

这个脚本实现了步骤 3（菜单操作）：

```python
from research.autocad_com_api.menu_automation import AutoCADMenuController

# 创建菜单控制器
controller = AutoCADMenuController()

# 连接到 AutoCAD 窗口
controller.connect_to_autocad()

# 方式 1: 点击菜单
controller.click_menu(["工具", "选项"])  # 中文版
# controller.click_menu(["Tools", "Options"])  # 英文版

# 方式 2: 执行命令
controller.execute_command_via_keyboard("ZOOM")
controller.execute_command_via_keyboard("E")  # Extents
```

**运行演示：**

```powershell
# 确保 AutoCAD 已打开并加载了文件
python 7_menu_automation.py
```

## 🎯 完整流程示例

### 示例 1：仅打开文件并验证

```python
from research.autocad_com_api.autocad_workflow import AutoCADWorkflow

workflow = AutoCADWorkflow()

# 运行完整流程（不含菜单操作）
success = workflow.run_complete_workflow(
    dwg_file_path=r"C:\path\to\drawing.dwg"
)

if success:
    print("✅ 文件已打开并验证")
```

### 示例 2：打开文件 + 执行命令

```python
# 步骤 1-2: 使用 workflow
workflow = AutoCADWorkflow()
workflow.run_complete_workflow(r"C:\path\to\drawing.dwg")

# 步骤 3: 使用 menu_controller
from research.autocad_com_api.menu_automation import AutoCADMenuController
controller = AutoCADMenuController()
controller.connect_to_autocad()

# 执行 ZOOM 命令
controller.execute_command_via_keyboard("ZOOM")
controller.execute_command_via_keyboard("E")
```

### 示例 3：完整的菜单操作流程

```python
# 完整流程
workflow = AutoCADWorkflow()
controller = AutoCADMenuController()

# 步骤 1-2
if workflow.run_complete_workflow(r"C:\path\to\drawing.dwg"):
    # 步骤 3
    controller.connect_to_autocad()
    controller.click_menu(["工具", "选项"])
```

## ⚠️ 重要说明

### 关于步骤 3（菜单操作）

**COM API 的限制：**
- AutoCAD COM API **不直接支持**菜单点击操作
- 需要使用 **UI Automation** (pywinauto) 或其他方式

**三种替代方案：**

1. **使用命令代替菜单**（推荐）
   ```python
   # 不点击菜单，直接发送命令
   controller.execute_command_via_keyboard("OPTIONS")  # 打开选项对话框
   ```

2. **使用 pywinauto 点击菜单**
   ```python
   controller.click_menu(["工具", "选项"])
   ```
   - ⚠️ 菜单路径因 AutoCAD 版本和语言而异
   - ⚠️ 需要调试找到正确的菜单路径

3. **使用 LISP 脚本**
   ```python
   # 加载并执行 LISP 脚本
   doc.SendCommand("(load \"your_script.lsp\") ")
   ```

### AutoCAD 2014 兼容性

您的 AutoCAD 2014 (版本 19.1) **已完全支持**：

- ✅ COM API 基本功能正常
- ✅ 文件打开/关闭操作
- ✅ 命令执行
- ⚠️ 某些新版本特性可能不可用

## 🧪 测试步骤

### 测试 1：基本工作流程

```powershell
# 1. 修改配置
# 编辑 6_autocad_workflow.py 第 268 行，设置正确的 DWG 文件路径

# 2. 运行测试
python 6_autocad_workflow.py

# 3. 观察
# - AutoCAD 应该自动启动
# - 指定的 DWG 文件应该自动打开
# - 控制台显示验证信息
```

### 测试 2：UI 自动化

```powershell
# 1. 确保 AutoCAD 已打开并加载了文件

# 2. 运行测试
python 7_menu_automation.py

# 3. 观察
# - 应该自动连接到 AutoCAD 窗口
# - 执行 ZOOM EXTENTS 命令
# - AutoCAD 视图应该缩放
```

## 📝 自定义流程

### 修改等待时间

在 `6_autocad_workflow.py` 中：

```python
# 步骤 1 中的等待时间
time.sleep(3)  # 等待进程关闭（第 61 行）
time.sleep(5)  # 等待 AutoCAD 初始化（第 73 行）

# 步骤 2 中的验证参数
workflow.step2_verify_file_loaded(
    max_wait_time=30,      # 最大等待 30 秒
    check_interval=2.0     # 每 2 秒检查一次
)
```

### 添加自定义菜单操作

在 `7_menu_automation.py` 的 `demo_workflow()` 函数中添加：

```python
# 执行自定义命令
controller.execute_command_via_keyboard("YOUR_COMMAND")

# 或点击自定义菜单
controller.click_menu(["你的菜单", "子菜单"])
```

## 🔧 故障排查

### 问题 1：AutoCAD 启动失败

```
❌ 启动 AutoCAD 或打开文件失败
```

**解决方法：**
- 确认 AutoCAD 已正确安装
- 确认 DWG 文件路径正确
- 以管理员身份运行脚本

### 问题 2：文件验证超时

```
❌ 超时：文件在 30 秒内未完全加载
```

**解决方法：**
- 增加 `max_wait_time` 参数
- 检查文件是否过大或损坏
- 确认 AutoCAD 没有显示错误对话框

### 问题 3：无法连接到窗口

```
❌ 超时：在 10 秒内未找到 AutoCAD 窗口
```

**解决方法：**
- 确认 AutoCAD 窗口可见
- 增加连接超时时间
- 检查 AutoCAD 窗口类名（可能因版本而异）

### 问题 4：菜单路径不正确

```
❌ 无法点击 '工具'
```

**解决方法：**
- 使用命令代替菜单（推荐）
- 使用 UI Inspector 工具查看实际的菜单结构
- 根据 AutoCAD 版本和语言调整菜单路径

## 📚 更多资源

- **COM API 文档：** `docs/autocad/AUTOCAD_COM_API_SUMMARY.md`
- **测试指南：** `docs/autocad/TESTING_GUIDE.md`
- **Bug 修复报告：** `BUGFIX_VERSION_PARSING.md`

## 💡 最佳实践

1. **先测试基本流程**
   - 先运行 `6_autocad_workflow.py` 确保步骤 1-2 正常
   - 再尝试添加菜单操作

2. **使用命令代替菜单**
   - 大多数菜单操作都有对应的命令
   - 命令更稳定，不受界面变化影响

3. **适当的等待时间**
   - 不要使用过短的等待时间
   - 根据实际硬件性能调整

4. **错误处理**
   - 检查返回值
   - 捕获异常
   - 记录日志

---

**创建日期：** 2025-10-24
**AutoCAD 支持版本：** 2013-2024
**测试状态：** 等待用户反馈
