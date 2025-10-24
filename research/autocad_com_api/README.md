# AutoCAD COM API 研究示例

本目录包含 AutoCAD COM API 的完整研究和自动化实现。

---

## 📋 文件列表

### 基础示例（Day 2 上午完成）

| 文件 | 说明 | 行数 |
|------|------|------|
| `1_connect_to_autocad.py` | AutoCAD 连接管理示例 | 280 行 |
| `2_file_operations.py` | 文件操作示例（打开/保存/关闭） | 170 行 |
| `3_command_execution.py` | 命令执行示例 | 90 行 |
| `4_error_handling.py` | 异常处理示例 | 80 行 |
| `5_version_check.py` | 版本检测示例（已修复特殊版本格式） | 80 行 |

### 完整工作流程（新增）

| 文件 | 说明 | 行数 |
|------|------|------|
| `6_autocad_workflow.py` | **完整自动化工作流程** | 350 行 |
| `7_menu_automation.py` | UI 自动化（菜单操作） | 280 行 |
| `8_complete_example.py` | 整合示例（待完善） | 200 行 |
| **`WORKFLOW_GUIDE.md`** | **📖 完整工作流程使用指南** | - |

---

## 🎯 核心工作流程

### 正确的自动化流程

```
步骤 1: 关闭现有 CAD → 启动 CAD → 打开指定 DWG 文件
步骤 2: 验证文件已加载（使用 sleep 等待机制）
步骤 3: 打开 CAD 指定菜单/执行操作
```

### 快速开始

**文件：** `6_autocad_workflow.py`（推荐使用这个）

```python
from autocad_workflow import AutoCADWorkflow

workflow = AutoCADWorkflow()

# 运行完整流程
success = workflow.run_complete_workflow(
    dwg_file_path=r"C:\path\to\your\drawing.dwg"
)
```

**详细说明：** 请查看 [`WORKFLOW_GUIDE.md`](./WORKFLOW_GUIDE.md)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 基础依赖（必需）
pip install pywin32 psutil

# UI 自动化（可选，用于菜单操作）
pip install pywinauto
```

### 2. 运行基础示例

```bash
# 测试版本检测（推荐首先运行）
python 5_version_check.py

# 测试连接功能
python 1_connect_to_autocad.py

# 测试文件操作（需要修改文件路径）
python 2_file_operations.py
```

### 3. 运行完整工作流程

```bash
# 修改 6_autocad_workflow.py 中的文件路径（第 268 行）
# 然后运行：
python 6_autocad_workflow.py
```

### 4. 注意事项

- ⚠️ **必须在 Windows 系统上运行**
- ⚠️ **需要安装 AutoCAD（2013-2024 任意版本）**
- ⚠️ **工作流程会关闭现有的 AutoCAD 进程**

---

## 📖 使用示例

### 示例 1：完整的自动化流程

```python
from autocad_workflow import AutoCADWorkflow

# 创建工作流程管理器
workflow = AutoCADWorkflow()

# 步骤 1: 关闭并打开 CAD
dwg_file = r"C:\path\to\drawing.dwg"
if workflow.step1_close_and_open_cad(dwg_file):

    # 步骤 2: 验证文件加载
    if workflow.step2_verify_file_loaded(max_wait_time=30):

        # 步骤 3: 执行操作（使用命令）
        # 通过 COM API 发送命令
        workflow.current_doc.SendCommand("._ZOOM _E ")

        print("✅ 自动化流程完成")
```

### 示例 2：基本连接和版本检测

```python
from connect_to_autocad import AutoCADConnection

# 使用上下文管理器
with AutoCADConnection() as conn:
    if conn.is_connected():
        info = conn.get_version_info()
        print(f"已连接到 {info['version_name']}")
        print(f"版本号: {info['version']}")
```

### 示例 3：UI 自动化（菜单操作）

```python
from menu_automation import AutoCADMenuController

# 确保 AutoCAD 已打开
controller = AutoCADMenuController()

if controller.connect_to_autocad():
    # 方式 1: 执行命令
    controller.execute_command_via_keyboard("ZOOM")
    controller.execute_command_via_keyboard("E")

    # 方式 2: 点击菜单（需要根据版本调整）
    # controller.click_menu(["工具", "选项"])
```

---

## 🎯 核心功能

### 1. 连接管理（`1_connect_to_autocad.py`）

- ✅ 连接到正在运行的 AutoCAD
- ✅ 自动启动 AutoCAD（如果未运行）
- ✅ 自动重连机制（最多 3 次）
- ✅ 进程状态监控
- ✅ 等待 AutoCAD 空闲
- ✅ 支持特殊版本格式解析

### 2. 文件操作（`2_file_operations.py`）

- ✅ 打开 DWG 文件（支持只读）
- ✅ 保存文档
- ✅ 另存为
- ✅ 关闭文档
- ✅ 获取文档信息
- ✅ 列出所有打开的文档

### 3. 命令执行（`3_command_execution.py`）

- ✅ 发送命令字符串
- ✅ 执行 AutoLISP 代码
- ✅ 常用命令封装（缩放、重生成）

### 4. 异常处理（`4_error_handling.py`）

- ✅ COM 错误捕获
- ✅ 错误代码映射
- ✅ 友好错误消息

### 5. 版本检测（`5_version_check.py`）

- ✅ 检测 AutoCAD 版本
- ✅ 支持特殊版本格式（如 "19.1s (LMS Tech)"）
- ✅ 兼容性验证（2013-2024）
- ✅ 版本警告提示

### 6. 完整工作流程（`6_autocad_workflow.py`）⭐ 新增

- ✅ 自动关闭现有 CAD 进程
- ✅ 启动 CAD 并打开指定文件
- ✅ 验证文件加载（带超时和重试）
- ✅ 进程监控和状态检查
- ✅ 完整的错误处理

### 7. UI 自动化（`7_menu_automation.py`）⭐ 新增

- ✅ 连接到 AutoCAD 窗口
- ✅ 执行键盘命令
- ✅ 点击菜单（实验性）
- ✅ 等待窗口就绪

---

## 📚 相关文档

### 核心文档

- **[WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md)** - 完整工作流程使用指南 ⭐ 推荐阅读
- [docs/autocad/AUTOCAD_COM_API_SUMMARY.md](../../docs/autocad/AUTOCAD_COM_API_SUMMARY.md) - COM API 完整文档
- [docs/autocad/TESTING_GUIDE.md](../../docs/autocad/TESTING_GUIDE.md) - 测试部署指南

### Bug 修复和更新

- [BUGFIX_VERSION_PARSING.md](../../BUGFIX_VERSION_PARSING.md) - 版本解析修复报告
- [UPDATE_NOTES.md](../../UPDATE_NOTES.md) - 测试包更新说明

---

## ⚠️ 常见问题

### Q1: 版本检测失败

**错误：** `could not convert string to float: '19.1s (LMS Tech)'`

**解决：** ✅ 已修复！请使用最新的 `5_version_check.py`

现在支持：
- 标准格式：`"24.0"`, `"23.1"`
- 特殊版本：`"19.1s (LMS Tech)"` (AutoCAD 2014 LMS Tech)
- 扩展格式：`"23.1.49.0"`

### Q2: 找不到 AutoCAD

**错误：** `pywintypes.com_error: (-2147467259, ...)`

**解决：**
```bash
# 重新注册 AutoCAD COM 接口
cd "C:\Program Files\Autodesk\AutoCAD 2014"
acad.exe /regserver
```

### Q3: 文件加载超时

**错误：** `❌ 超时：文件在 30 秒内未完全加载`

**解决：**
```python
# 增加等待时间
workflow.step2_verify_file_loaded(
    max_wait_time=60,      # 增加到 60 秒
    check_interval=3.0     # 每 3 秒检查一次
)
```

### Q4: 菜单操作不工作

**原因：** COM API 不直接支持菜单操作

**解决方案（3种）：**

1. **使用命令代替菜单**（推荐）
   ```python
   controller.execute_command_via_keyboard("OPTIONS")  # 打开选项对话框
   ```

2. **使用 pywinauto 点击菜单**
   ```python
   controller.click_menu(["工具", "选项"])
   # 注意：需要根据 AutoCAD 版本和语言调整路径
   ```

3. **使用 LISP 脚本**
   ```python
   doc.SendCommand("(load \"script.lsp\") ")
   ```

---

## 🔧 AutoCAD 2014 支持

您的 **AutoCAD 2014 (版本 19.1)** 已完全支持：

- ✅ COM API 基本功能
- ✅ 文件操作
- ✅ 命令执行
- ✅ 版本检测（包括特殊版本格式）
- ⚠️ 某些新版本特性可能不可用

**支持的版本范围：** AutoCAD 2013-2024

---

## 🔗 参考资源

- [AutoCAD ActiveX and VBA Reference](https://help.autodesk.com/view/OARX/2024/ENU/)
- [pywin32 Documentation](https://github.com/mhammond/pywin32)
- [pywinauto Documentation](https://pywinauto.readthedocs.io/)
- [AutoCAD DevBlog](https://adndevblog.typepad.com/autocad/)

---

## 📊 文件依赖关系

```
1_connect_to_autocad.py (基础连接)
    ↓
2_file_operations.py (文件操作)
3_command_execution.py (命令执行)
    ↓
6_autocad_workflow.py (完整工作流程) ⭐ 推荐使用
    ↓
7_menu_automation.py (UI 自动化)
    ↓
8_complete_example.py (整合示例)
```

---

## 🚀 推荐使用流程

1. **首次测试：** 运行 `5_version_check.py` 确认版本识别正常
2. **基础测试：** 运行 `1_connect_to_autocad.py` 测试连接
3. **完整流程：** 使用 `6_autocad_workflow.py` 实现自动化
4. **进阶功能：** 根据需要添加 `7_menu_automation.py` 的 UI 操作

---

**创建日期：** 2025-10-24
**最后更新：** 2025-10-24
**状态：** ✅ 完成 + 工作流程增强
**支持版本：** AutoCAD 2013-2024
**测试状态：** 等待用户反馈
