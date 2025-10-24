# AutoCAD COM API 研究示例

本目录包含 AutoCAD COM API 的研究示例代码，用于 Day 2 上午的 AutoCAD COM 接口调研任务。

---

## 📋 文件列表

| 文件 | 说明 | 行数 |
|------|------|------|
| `1_connect_to_autocad.py` | AutoCAD 连接管理示例 | 150 行 |
| `2_file_operations.py` | 文件操作示例（打开/保存/关闭） | 170 行 |
| `3_command_execution.py` | 命令执行示例 | 90 行 |
| `4_error_handling.py` | 异常处理示例 | 80 行 |
| `5_version_check.py` | 版本检测示例 | 60 行 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pywin32 psutil
```

### 2. 运行示例

```bash
# 测试连接功能
python 1_connect_to_autocad.py

# 测试版本检测
python 5_version_check.py

# 测试文件操作（需要修改文件路径）
python 2_file_operations.py
```

### 3. 注意事项

- ⚠️ **必须在 Windows 系统上运行**
- ⚠️ **需要安装 AutoCAD（2018-2024 任意版本）**
- ⚠️ **文件操作示例需要修改测试文件路径**

---

## 📖 使用示例

### 示例 1：连接到 AutoCAD

```python
from research.autocad_com_api.connect_to_autocad import AutoCADConnection

# 使用上下文管理器
with AutoCADConnection() as conn:
    if conn.is_connected():
        print(f"已连接到 {conn.get_version_info()['version_name']}")
```

### 示例 2：打开和保存文件

```python
import win32com.client
from research.autocad_com_api.file_operations import AutoCADFileOps

# 连接 AutoCAD
acad = win32com.client.GetActiveObject("AutoCAD.Application")

# 创建文件操作对象
file_ops = AutoCADFileOps(acad)

# 打开文件
doc = file_ops.open_file(r"C:\path\to\file.dwg")

# 保存文件
file_ops.save_document(doc)

# 关闭文件
file_ops.close_document(doc, save_changes=True)
```

### 示例 3：执行命令

```python
from research.autocad_com_api.command_execution import AutoCADCommands

acad = win32com.client.GetActiveObject("AutoCAD.Application")
cmd = AutoCADCommands(acad)

# 缩放到图形范围
cmd.zoom_extents()

# 重新生成图形
cmd.regen()
```

---

## 🎯 核心功能

### 1. 连接管理（`1_connect_to_autocad.py`）

- ✅ 连接到正在运行的 AutoCAD
- ✅ 自动启动 AutoCAD（如果未运行）
- ✅ 自动重连机制（最多 3 次）
- ✅ 进程状态监控
- ✅ 等待 AutoCAD 空闲

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
- ✅ 兼容性验证（2018-2024）

---

## 📚 相关文档

完整的 AutoCAD COM API 文档请查看：
- [docs/autocad/AUTOCAD_COM_API_SUMMARY.md](../../docs/autocad/AUTOCAD_COM_API_SUMMARY.md)

---

## ⚠️ 常见问题

### Q1: 找不到 AutoCAD

**错误：** `pywintypes.com_error: (-2147467259, ...)`

**解决：**
```bash
# 重新注册 AutoCAD COM 接口
cd "C:\Program Files\Autodesk\AutoCAD 2024"
acad.exe /regserver
```

### Q2: 命令执行无响应

**原因：** 命令字符串格式错误

**解决：**
```python
# ❌ 错误
doc.SendCommand("ZOOM E")

# ✅ 正确
doc.SendCommand("._ZOOM _E ")  # 注意前缀和末尾空格
```

### Q3: 文件无法打开

**原因：** 路径不正确或文件不存在

**解决：**
```python
import os

# 使用绝对路径
abs_path = os.path.abspath("test.dwg")

# 检查文件存在
if os.path.exists(abs_path):
    doc = file_ops.open_file(abs_path)
```

---

## 🔗 参考资源

- [AutoCAD ActiveX and VBA Reference](https://help.autodesk.com/view/OARX/2024/ENU/)
- [pywin32 Documentation](https://github.com/mhammond/pywin32)
- [AutoCAD DevBlog](https://adndevblog.typepad.com/autocad/)

---

**创建日期：** 2025-10-24
**状态：** ✅ 完成
**下一步：** 基于这些示例开发完整的 AutoCAD 自动化模块
