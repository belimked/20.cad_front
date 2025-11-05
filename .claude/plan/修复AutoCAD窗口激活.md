# 修复 AutoCAD 窗口激活失败问题

## 任务背景

**问题**：在执行 BPLOT 命令后，`SetForegroundWindow` 调用失败，导致窗口无法激活到前台。

**现象**：
- AutoCAD 已启动 ✅
- 文件已打开 ✅
- BPLOT 命令已执行 ✅
- 对话框已显示，但窗口不在前台 ⚠️

**错误信息**：
```
⚠️  激活窗口失败: (0, 'SetForegroundWindow', 'No error message is available')
```

---

## 解决方案

**选择方案**：使用 pywinauto 库替代原生 Windows API

**理由**：
- pywinauto 已在项目依赖中（requirements.txt:11）
- 自动处理 Windows 窗口激活限制
- 更高的成功率和稳定性
- 支持多种窗口查找策略

---

## 实施步骤

### 1. 更新依赖导入
- 添加 pywinauto 到延迟导入机制
- 在 `_ensure_dependencies()` 中加载

### 2. 改进窗口查找方法
- 使用 `find_windows()` 支持正则匹配
- 模糊匹配窗口标题（"AutoCAD 2024"、"tz.dwg - AutoCAD" 等）

### 3. 重写窗口激活方法
- 使用 `pywinauto.Application().connect()`
- 使用 `window.set_focus()` 替代 `SetForegroundWindow`
- 添加重试机制（最多 3 次）

---

## 涉及文件

- `research/autocad_com_api/enhanced_workflow.py`
  - `_find_target_window()` (第 567-586 行)
  - `_activate_autocad_window()` (第 645-653 行)
  - 依赖导入部分 (第 40-63 行)

---

## 预期结果

- ✅ 窗口激活不再报错
- ✅ BPLOT 对话框成功显示在前台
- ✅ 后续 OCR 识别正常工作

---

**执行时间**：2025-11-05
**状态**：执行中
