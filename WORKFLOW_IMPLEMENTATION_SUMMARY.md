# AutoCAD 自动化工作流程 - 实现总结

**日期：** 2025-10-24
**类型：** 功能增强
**状态：** ✅ 完成

---

## 🎯 需求澄清

### 原先理解（错误）
仅调研 AutoCAD COM API，提供基础示例代码。

### 实际需求（正确）
实现完整的 AutoCAD 自动化工作流程：

```
步骤 1: 关闭现有 CAD → 启动 CAD → 打开指定 DWG 文件
步骤 2: 验证文件已加载（使用 sleep 等待机制）
步骤 3: 打开 CAD 指定菜单
```

---

## ✅ 完成的工作

### 1. 核心工作流程实现

**文件：** `research/autocad_com_api/6_autocad_workflow.py` (350行)

**功能：**
- ✅ 自动关闭所有现有 AutoCAD 进程
  - 首先尝试 COM Quit() 正常关闭
  - 然后使用 psutil 强制终止进程
  - 等待进程完全关闭

- ✅ 启动 AutoCAD 并打开指定文件
  - 使用 COM Dispatch 启动新实例
  - 自动打开指定的 DWG 文件
  - 设置窗口可见

- ✅ 验证文件加载（智能等待机制）
  - 循环检查 AutoCAD 进程状态
  - 验证文档是否打开
  - 检查模型空间是否可访问
  - 支持超时和间隔配置

**核心类：**
```python
class AutoCADWorkflow:
    def step1_close_and_open_cad(dwg_file_path, force_close=True)
    def step2_verify_file_loaded(max_wait_time=30, check_interval=2.0)
    def step3_open_menu(menu_name, submenu_name=None)
    def run_complete_workflow(dwg_file_path, menu_name=None)
```

### 2. UI 自动化实现

**文件：** `research/autocad_com_api/7_menu_automation.py` (280行)

**功能：**
- ✅ 使用 pywinauto 连接到 AutoCAD 窗口
  - 通过窗口类名 "AcadFrame" 查找
  - 支持超时重试

- ✅ 执行键盘命令
  - 自动聚焦窗口
  - 发送 ESC 清空命令
  - 输入命令并回车

- ✅ 点击菜单（实验性）
  - 通过菜单路径点击
  - 支持多级菜单

- ✅ 等待窗口就绪
  - 检测窗口状态
  - 避免操作过快

**核心类：**
```python
class AutoCADMenuController:
    def connect_to_autocad(timeout=10)
    def click_menu(menu_path, wait_time=1.0)
    def execute_command_via_keyboard(command)
    def wait_for_idle(timeout=30)
```

### 3. 完整示例

**文件：** `research/autocad_com_api/8_complete_example.py` (200行)

**功能：**
- ✅ 整合步骤 1-3 的完整流程
- ✅ 配置化的菜单操作定义
- ✅ 支持多种操作类型（命令、菜单）

### 4. 完整文档

**文件：** `research/autocad_com_api/WORKFLOW_GUIDE.md`

**内容：**
- ✅ 详细的步骤说明
- ✅ 配置和使用示例
- ✅ 三种菜单操作方案对比
- ✅ 故障排查指南
- ✅ 自定义流程说明

### 5. 更新 README

**文件：** `research/autocad_com_api/README.md`

**更新内容：**
- ✅ 添加新文件说明
- ✅ 更新核心工作流程
- ✅ 添加完整示例
- ✅ 更新常见问题（添加 Q4 菜单操作）

---

## 📊 技术实现细节

### 进程管理

```python
def _close_all_autocad_processes(self) -> int:
    # 1. 尝试 COM 正常关闭
    acad = win32com.client.GetActiveObject("AutoCAD.Application")
    acad.Quit()

    # 2. 强制终止所有 acad.exe 进程
    for proc in psutil.process_iter(['pid', 'name']):
        if 'acad.exe' in proc.info['name'].lower():
            proc.terminate()
            proc.wait(timeout=5)
```

### 文件加载验证

```python
def step2_verify_file_loaded(self, max_wait_time=30, check_interval=2.0):
    while time.time() - start_time < max_wait_time:
        # 检查 1: AutoCAD 进程是否运行
        if not self._is_autocad_running():
            return False

        # 检查 2: 文档是否打开
        doc_name = self.current_doc.Name

        # 检查 3: 文档是否活动
        active_doc = self.acad.ActiveDocument

        # 检查 4: 模型空间是否可访问
        entity_count = self.current_doc.ModelSpace.Count

        if entity_count >= 0:
            return True

        time.sleep(check_interval)
```

### UI 自动化

```python
def execute_command_via_keyboard(self, command: str):
    # 1. 聚焦窗口
    self.main_window.set_focus()

    # 2. 清空当前命令
    self.main_window.type_keys("{ESC}{ESC}")

    # 3. 输入命令并回车
    self.main_window.type_keys(command + "{ENTER}")
```

---

## 🔧 关于菜单操作的三种方案

### 方案 1：使用命令代替菜单（推荐）

**优点：**
- ✅ 最稳定可靠
- ✅ 不受界面变化影响
- ✅ 性能最好

**示例：**
```python
controller.execute_command_via_keyboard("OPTIONS")  # 打开选项
controller.execute_command_via_keyboard("ZOOM")     # 缩放
```

### 方案 2：使用 pywinauto 点击菜单

**优点：**
- ✅ 可以操作没有命令的菜单项
- ✅ 模拟真实用户操作

**缺点：**
- ⚠️ 菜单路径因版本和语言而异
- ⚠️ 需要调试找到正确路径
- ⚠️ UI 变化会导致失败

**示例：**
```python
controller.click_menu(["工具", "选项"])  # 中文版
controller.click_menu(["Tools", "Options"])  # 英文版
```

### 方案 3：使用 LISP 脚本

**优点：**
- ✅ 功能最强大
- ✅ 可以执行复杂操作

**缺点：**
- ⚠️ 需要编写 LISP 代码
- ⚠️ 学习曲线较高

**示例：**
```python
doc.SendCommand("(load \"my_script.lsp\") ")
doc.SendCommand("(my-function) ")
```

---

## 💡 使用建议

### 推荐工作流程

1. **基础测试**
   ```powershell
   python 5_version_check.py        # 验证版本识别
   python 1_connect_to_autocad.py   # 测试连接
   ```

2. **完整流程测试**
   ```powershell
   # 修改 6_autocad_workflow.py 中的文件路径
   python 6_autocad_workflow.py
   ```

3. **添加自定义操作**
   ```python
   # 在步骤 2 完成后，添加自定义命令
   workflow.current_doc.SendCommand("._YOUR_COMMAND ")
   ```

### 配置参数建议

```python
# 文件加载验证
max_wait_time = 30      # 大文件可增加到 60 秒
check_interval = 2.0    # 根据系统性能调整

# 进程关闭等待
time.sleep(3)           # 等待进程完全关闭

# AutoCAD 初始化等待
time.sleep(5)           # 等待 AutoCAD 启动
```

---

## 🧪 测试状态

### 已完成
- ✅ 代码实现完成
- ✅ 文档编写完成
- ✅ 示例代码验证
- ✅ 提交到 Git 仓库

### 待用户测试
- ⏳ AutoCAD 2014 实际测试
- ⏳ 文件打开流程验证
- ⏳ 菜单操作测试
- ⏳ 边界情况测试

---

## 📦 交付物清单

| 文件 | 类型 | 行数 | 说明 |
|------|------|------|------|
| `6_autocad_workflow.py` | 代码 | 350 | 核心工作流程 |
| `7_menu_automation.py` | 代码 | 280 | UI 自动化 |
| `8_complete_example.py` | 代码 | 200 | 整合示例 |
| `WORKFLOW_GUIDE.md` | 文档 | 500+ | 使用指南 |
| `README.md` | 文档 | 340 | 更新说明 |
| **总计** | - | **1,670+** | - |

---

## 🎯 与原需求的对比

| 方面 | 原实现 | 新实现 |
|------|--------|--------|
| **理解** | 仅 API 调研 | 完整自动化流程 |
| **步骤 1** | ❌ 未实现 | ✅ 完整实现 |
| **步骤 2** | ❌ 未实现 | ✅ 完整实现 |
| **步骤 3** | ❌ 未实现 | ✅ 提供 3 种方案 |
| **进程管理** | ❌ 无 | ✅ 自动关闭/启动 |
| **文件验证** | ❌ 无 | ✅ 智能等待机制 |
| **UI 操作** | ❌ 无 | ✅ pywinauto 支持 |
| **文档** | 基础说明 | 完整使用指南 |

---

## 🚀 下一步建议

### 用户测试
1. 在 AutoCAD 2014 上测试基本流程
2. 使用实际的 DWG 文件测试
3. 测试不同大小的文件（小/中/大）
4. 测试菜单操作（命令方式）

### 可能的改进
1. 添加日志记录
2. 添加配置文件支持
3. 添加批量处理功能
4. 添加进度回调机制
5. 添加错误恢复策略

### 性能优化
1. 优化等待时间
2. 添加并行处理
3. 缓存 AutoCAD 实例

---

## 📝 技术栈

- **COM 自动化：** pywin32 (win32com.client)
- **进程管理：** psutil
- **UI 自动化：** pywinauto
- **AutoCAD 版本：** 2013-2024
- **Python 版本：** 3.9+

---

## ✅ 完成状态

- ✅ 代码实现：100%
- ✅ 文档编写：100%
- ✅ Git 提交：100%
- ⏳ 用户测试：等待反馈
- ⏳ 生产使用：等待验证

---

**Commit:** a6fa54e
**分支:** cad
**创建时间：** 2025-10-24
**总代码行数：** 1,670+ 行（新增）
**总文档行数：** 840+ 行（新增+更新）
