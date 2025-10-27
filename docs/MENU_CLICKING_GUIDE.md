# AutoCAD 菜单点击操作指南

## 问题诊断

当菜单点击失败（如"依云"菜单无法找到）时，按以下步骤诊断：

---

## 步骤 1: 运行UI结构检查工具

```bash
# 激活虚拟环境
venv\Scripts\activate

# 启动AutoCAD并打开目标文件

# 运行检查工具
python scripts\inspect_autocad_ui.py
```

### 工具功能

1. **查找AutoCAD窗口**: 自动检测所有AutoCAD窗口
2. **搜索特定文本**: 输入"依云"查找包含该文本的所有控件
3. **导出UI树**: 生成`autocad_ui_tree.json`文件，包含完整UI结构
4. **检查菜单栏**: 列出MenuBar中的所有菜单项

### 输出示例

```
✅ 找到 1 个AutoCAD窗口:
  1. Autodesk AutoCAD 2014 (HWND=7733976)

[步骤 3/4] 搜索包含 '依云' 的控件...
✅ 找到 2 个匹配的控件:

  [1] 控件信息:
      文本: 依云
      类名: Afx:00400000:8:00010011:00000000:019B05E1
      类型: Button
      深度: 5
      可用: True
      可见: True
```

---

## 步骤 2: 分析控件信息

### 关键信息解读

1. **control_type**: 控件类型
   - `MenuItem`: 传统菜单项
   - `Button`: 按钮（Ribbon界面常用）
   - `TabItem`: 选项卡
   - `Custom`: 自定义控件

2. **depth**: 控件深度
   - 0-3: 顶层控件
   - 4-7: 中层控件
   - 8+: 深层嵌套

3. **visible**: 是否可见
   - `True`: 控件可见
   - `False`: 控件隐藏（无法点击）

### 常见情况

| 情况 | control_type | 解决方案 |
|-----|-------------|---------|
| 传统菜单 | MenuItem | 已支持（策略1/4） |
| Ribbon界面 | Button | 已支持（策略2/5） |
| 选项卡 | TabItem | 已支持（策略3） |
| 自绘菜单 | Custom | 需要图像识别 |
| 未找到 | - | 使用键盘快捷键或命令行 |

---

## 步骤 3: 测试改进后的菜单点击

### 当前支持的搜索策略

代码会按顺序尝试7种策略：

```python
# 策略1: MenuItem精确匹配
{"title": "依云", "control_type": "MenuItem"}

# 策略2: Button精确匹配（Ribbon界面）
{"title": "依云", "control_type": "Button"}

# 策略3: TabItem精确匹配（选项卡）
{"title": "依云", "control_type": "TabItem"}

# 策略4: MenuItem模糊匹配
{"title_re": ".*依云.*", "control_type": "MenuItem"}

# 策略5: Button模糊匹配
{"title_re": ".*依云.*", "control_type": "Button"}

# 策略6: 仅通过标题搜索（不限控件类型）
{"title": "依云"}

# 策略7: 模糊标题搜索（不限控件类型）
{"title_re": ".*依云.*"}
```

### 测试流程

1. 确保pywinauto已安装在虚拟环境中：
   ```bash
   venv\Scripts\python -m pip list | findstr pywinauto
   ```

2. 添加菜单操作到配置：
   ```bash
   python scripts\add_menu_operations.py 1
   # 选择 [2] 菜单点击
   # 输入: 依云
   ```

3. 运行工作流程：
   ```bash
   python research\autocad_com_api\9_configurable_workflow.py
   ```

4. 观察输出：
   ```
   [步骤 3] 执行菜单操作
   📋 操作 1/1: menu
   [模式] 鼠标点击
   [1/1] 查找菜单: 依云
   ✅ [策略2] 找到控件: 依云 (Button/精确)
   ✅ 已点击菜单: 依云
   ```

---

## 步骤 4: 备选方案

### 方案A: 使用键盘快捷键

如果菜单有快捷键（如"帮助(H)"），使用键盘方式：

```python
{
    "type": "menu",
    "path": ["帮助(H)", "欢迎屏幕(W)"],
    "wait_time": 1.0
}
```

### 方案B: 使用AutoCAD命令

如果菜单对应某个命令，直接使用命令方式：

```python
{
    "type": "command",
    "command": "MENUNAME",  # 替换为实际命令
    "wait_time": 0.5
}
```

### 方案C: 图像识别（需安装pyautogui）

对于自绘菜单或特殊控件：

```python
import pyautogui

# 查找并点击图像
location = pyautogui.locateOnScreen('menu_icon.png')
if location:
    pyautogui.click(location)
```

### 方案D: 坐标点击

如果菜单位置固定：

```python
import pyautogui

# 点击固定坐标
pyautogui.click(x=100, y=50)
```

---

## 常见问题

### Q1: 提示"缺少pywinauto库"

**原因**: pywinauto未安装或安装到错误的Python环境

**解决**:
```bash
# 必须在虚拟环境中安装
venv\Scripts\activate
pip install pywinauto>=0.6.8
```

**验证**:
```bash
python test_pywinauto.py
```

### Q2: 找到控件但点击失败

**原因**: 控件不可点击或被遮挡

**解决**:
1. 检查控件是否enabled和visible
2. 尝试激活窗口后再点击
3. 增加等待时间
4. 使用备用点击方式（代码已自动尝试）

### Q3: 所有策略均未找到控件

**原因**: 控件可能是自绘的或深度嵌套

**解决**:
1. 增加搜索深度（修改inspect_autocad_ui.py中的max_depth）
2. 使用图像识别
3. 使用键盘快捷键
4. 使用AutoCAD命令行

### Q4: UI树文件太大无法查看

**解决**:
1. 减小导出深度（修改dump_ui_tree的max_depth参数）
2. 使用JSON查看器（如VSCode）
3. 只搜索特定文本而不导出完整树

---

## 调试技巧

### 1. 打印详细日志

在9_configurable_workflow.py中已包含详细日志：
```
[策略1] MenuItem精确匹配 -> 失败
[策略2] Button精确匹配 -> 成功
✅ 找到控件: 依云 (Button/精确)
✅ 使用备用点击方式成功
```

### 2. 手动测试pywinauto

```python
from pywinauto import Desktop
import win32gui

# 查找窗口
def find_window(hwnd, param):
    if 'AutoCAD' in win32gui.GetWindowText(hwnd):
        param.append(hwnd)
    return True

windows = []
win32gui.EnumWindows(find_window, windows)

# 连接窗口
desktop = Desktop(backend="uia")
app = desktop.window(handle=windows[0])

# 搜索控件
item = app.child_window(title="依云")
print(f"找到: {item.exists()}")
print(f"类型: {item.element_info.control_type}")
```

### 3. 查看pywinauto支持的后端

```python
from pywinauto import Desktop

# 尝试不同后端
backends = ["uia", "win32"]
for backend in backends:
    try:
        desktop = Desktop(backend=backend)
        print(f"✅ {backend} 后端可用")
    except:
        print(f"❌ {backend} 后端不可用")
```

---

## 性能优化

### 1. 减少搜索策略

如果已知控件类型，只保留相关策略：

```python
# 仅搜索Button类型
search_strategies = [
    {"title": menu_name, "control_type": "Button"},
    {"title_re": f".*{menu_name}.*", "control_type": "Button"},
]
```

### 2. 调整等待时间

根据AutoCAD响应速度调整：

```python
# 快速模式
time.sleep(0.2)

# 稳定模式
time.sleep(1.0)
```

### 3. 缓存窗口句柄

避免重复查找窗口：

```python
if not hasattr(self, '_cached_hwnd'):
    self._cached_hwnd = self._find_autocad_window()

hwnd = self._cached_hwnd
```

---

## 总结

1. **优先使用**: 改进后的鼠标点击方法（支持7种策略）
2. **备选方案**: 键盘快捷键 > AutoCAD命令 > 图像识别
3. **诊断工具**: scripts/inspect_autocad_ui.py
4. **测试工具**: test_pywinauto.py

遇到问题按以下顺序排查：
1. 运行inspect_autocad_ui.py检查控件是否存在
2. 确认pywinauto安装在虚拟环境中
3. 测试改进后的点击方法
4. 考虑备选方案
