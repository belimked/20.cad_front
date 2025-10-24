# AutoCAD COM API 总结文档

**文档版本：** 1.0
**创建日期：** 2025-10-24
**适用版本：** AutoCAD 2018-2024

---

## 📋 概述

AutoCAD COM API 是 Autodesk 提供的 COM (Component Object Model) 接口，允许外部程序通过 OLE Automation 控制 AutoCAD。

### 核心优势

- ✅ **无需修改 AutoCAD**：通过外部程序控制
- ✅ **跨版本兼容**：支持 AutoCAD 2018-2024
- ✅ **功能完整**：可访问几乎所有 AutoCAD 功能
- ✅ **Python 支持**：通过 pywin32 库轻松调用

---

## 🏗️ COM API 层次结构

```
AcadApplication (应用程序对象 - 顶层)
├── Documents (文档集合)
│   └── AcadDocument (单个文档)
│       ├── ModelSpace (模型空间)
│       ├── PaperSpace (图纸空间)
│       ├── Blocks (块集合)
│       ├── Layers (图层集合)
│       ├── Layouts (布局集合)
│       └── Utility (实用工具)
├── Preferences (首选项)
├── MenuGroups (菜单组)
└── StatusId (状态 ID)
```

---

## 🔑 核心对象说明

### 1. AcadApplication（应用程序对象）

**作用：** AutoCAD 应用程序的顶层对象

**主要属性：**
- `Name` - 应用程序名称
- `Version` - AutoCAD 版本号
- `Visible` - AutoCAD 窗口是否可见
- `ActiveDocument` - 当前活动文档
- `Documents` - 所有打开的文档集合
- `Preferences` - 首选项设置
- `WindowState` - 窗口状态（最小化/最大化/正常）
- `Path` - AutoCAD 安装路径

**主要方法：**
- `GetInterfaceObject(progID)` - 获取其他 COM 对象
- `ListArx()` - 列出加载的 ARX 应用
- `LoadArx(arxFile)` - 加载 ARX 应用
- `UnloadArx(arxFile)` - 卸载 ARX 应用
- `Quit()` - 退出 AutoCAD
- `Update()` - 强制重绘
- `ZoomExtents()` - 缩放到范围
- `ZoomAll()` - 缩放全部

### 2. AcadDocument（文档对象）

**作用：** 代表一个打开的 DWG 文件

**主要属性：**
- `Name` - 文档名称
- `Path` - 文档路径
- `Active` - 是否为活动文档
- `ModelSpace` - 模型空间对象
- `PaperSpace` - 图纸空间对象
- `Blocks` - 块集合
- `Layers` - 图层集合
- `Layouts` - 布局集合
- `Utility` - 实用工具对象
- `Database` - 数据库对象

**主要方法：**
- `Open(fileName)` - 打开文件
- `Save()` - 保存文档
- `SaveAs(fileName, fileType)` - 另存为
- `Close(saveChanges)` - 关闭文档
- `SendCommand(command)` - 发送命令字符串
- `Regen(mode)` - 重新生成
- `PurgeAll()` - 清理未使用项
- `Activate()` - 激活文档
- `CopyObjects(objects, owner)` - 复制对象
- `HandleToObject(handle)` - 通过句柄获取对象
- `ObjectIdToObject(objectId)` - 通过 ID 获取对象

### 3. AcadUtility（实用工具对象）

**作用：** 提供各种实用功能

**主要方法：**
- `GetInteger(prompt)` - 获取整数输入
- `GetReal(prompt)` - 获取实数输入
- `GetString(hasSpaces, prompt)` - 获取字符串输入
- `GetPoint(basePoint, prompt)` - 获取点坐标
- `GetEntity(prompt)` - 获取实体
- `Prompt(message)` - 显示提示消息
- `GetInput()` - 获取命令行输入
- `TranslateCoordinates(point, fromCS, toCS, displacement)` - 坐标转换

---

## 🚀 Python 连接 AutoCAD

### 使用 pywin32 连接

```python
import win32com.client
import pythoncom

def connect_to_autocad():
    """
    连接到 AutoCAD 应用程序

    返回：
        AcadApplication 对象
    """
    try:
        # 尝试连接到正在运行的 AutoCAD
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        print(f"✅ 已连接到运行中的 AutoCAD {acad.Version}")
        return acad
    except:
        try:
            # 如果 AutoCAD 未运行，启动它
            acad = win32com.client.Dispatch("AutoCAD.Application")
            acad.Visible = True
            print(f"✅ 已启动 AutoCAD {acad.Version}")
            return acad
        except Exception as e:
            print(f"❌ 连接 AutoCAD 失败: {e}")
            return None
```

### 版本识别

```python
def get_autocad_version(acad):
    """获取 AutoCAD 版本信息"""
    version = acad.Version
    version_map = {
        "22.0": "AutoCAD 2018",
        "23.0": "AutoCAD 2019",
        "23.1": "AutoCAD 2020",
        "24.0": "AutoCAD 2021",
        "24.1": "AutoCAD 2022",
        "24.2": "AutoCAD 2023",
        "24.3": "AutoCAD 2024",
    }
    return version_map.get(version, f"AutoCAD (版本 {version})")
```

---

## 📂 文件操作

### 打开文件

```python
def open_dwg_file(acad, file_path):
    """
    打开 DWG 文件

    参数：
        acad: AutoCAD Application 对象
        file_path: DWG 文件绝对路径

    返回：
        AcadDocument 对象
    """
    import os

    # 确保路径是绝对路径
    abs_path = os.path.abspath(file_path)

    try:
        # 打开文件
        doc = acad.Documents.Open(abs_path)
        print(f"✅ 成功打开文件: {abs_path}")
        return doc
    except Exception as e:
        print(f"❌ 打开文件失败: {e}")
        return None
```

### 保存文件

```python
def save_document(doc, new_path=None):
    """
    保存文档

    参数：
        doc: AcadDocument 对象
        new_path: 新路径（另存为），None 表示保存
    """
    try:
        if new_path:
            # 另存为
            doc.SaveAs(new_path)
            print(f"✅ 文件已另存为: {new_path}")
        else:
            # 保存
            doc.Save()
            print(f"✅ 文件已保存: {doc.Name}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
```

### 关闭文件

```python
def close_document(doc, save_changes=True):
    """
    关闭文档

    参数：
        doc: AcadDocument 对象
        save_changes: 是否保存更改
    """
    try:
        doc.Close(save_changes)
        print(f"✅ 文档已关闭")
    except Exception as e:
        print(f"❌ 关闭失败: {e}")
```

---

## ⚡ 命令执行

### 发送命令字符串

```python
def send_command(doc, command_string):
    """
    向 AutoCAD 发送命令字符串

    参数：
        doc: AcadDocument 对象
        command_string: 命令字符串（需要包含空格和回车）

    注意：
        命令字符串需要用空格分隔参数，用回车结束命令
        例如: "._ZOOM _E " (注意末尾的空格作为回车)
    """
    try:
        doc.SendCommand(command_string + " ")
        print(f"✅ 命令已发送: {command_string}")
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
```

### 执行 LISP 脚本

```python
def execute_lisp(doc, lisp_code):
    """
    执行 AutoLISP 代码

    参数：
        doc: AcadDocument 对象
        lisp_code: LISP 代码字符串

    示例：
        execute_lisp(doc, '(command "._ZOOM" "_E")')
    """
    try:
        # 通过 SendCommand 执行 LISP
        doc.SendCommand(f"(progn {lisp_code}) ")
        print(f"✅ LISP 代码已执行")
    except Exception as e:
        print(f"❌ LISP 执行失败: {e}")
```

### 加载并执行 LISP 文件

```python
def load_lisp_file(doc, lisp_file_path):
    """
    加载并执行 LISP 文件

    参数：
        doc: AcadDocument 对象
        lisp_file_path: LISP 文件路径
    """
    import os

    abs_path = os.path.abspath(lisp_file_path).replace("\\", "/")

    try:
        # 使用 LOAD 命令加载 LISP
        doc.SendCommand(f'(load "{abs_path}") ')
        print(f"✅ LISP 文件已加载: {abs_path}")
    except Exception as e:
        print(f"❌ 加载 LISP 文件失败: {e}")
```

---

## 🔧 常用操作示例

### 缩放视图

```python
def zoom_extents(acad):
    """缩放到图形范围"""
    acad.ZoomExtents()
    print("✅ 已缩放到范围")

def zoom_all(acad):
    """缩放全部"""
    acad.ZoomAll()
    print("✅ 已缩放全部")
```

### 重新生成图形

```python
def regen_document(doc, mode=True):
    """
    重新生成文档

    参数：
        doc: AcadDocument 对象
        mode: True=全部重生成, False=快速重生成
    """
    doc.Regen(mode)
    print("✅ 图形已重新生成")
```

### 获取文档信息

```python
def get_document_info(doc):
    """获取文档详细信息"""
    info = {
        "name": doc.Name,
        "path": doc.Path if doc.Path else "未保存",
        "active": doc.Active,
        "model_space_count": doc.ModelSpace.Count,
        "paper_space_count": doc.PaperSpace.Count,
        "layers_count": doc.Layers.Count,
        "blocks_count": doc.Blocks.Count,
    }
    return info
```

---

## ⚠️ 异常处理

### COM 异常类型

```python
import pywintypes

# 常见 COM 异常
class AutoCADError:
    """AutoCAD COM 错误代码"""

    # 错误代码映射
    ERROR_CODES = {
        -2147467259: "未找到 AutoCAD（未安装或未注册）",
        -2147221005: "AutoCAD 无法启动",
        -2147024894: "文件未找到",
        -2147352567: "自动化错误（命令执行失败）",
        -2147417848: "对象已断开连接",
        -2147023170: "拒绝访问",
    }

    @staticmethod
    def get_error_message(error_code):
        """获取错误消息"""
        return AutoCADError.ERROR_CODES.get(
            error_code,
            f"未知错误代码: {error_code}"
        )
```

### 错误处理示例

```python
def safe_open_file(acad, file_path):
    """安全地打开文件（带错误处理）"""
    try:
        doc = acad.Documents.Open(file_path)
        return doc, None
    except pywintypes.com_error as e:
        error_code = e.args[0]
        error_message = AutoCADError.get_error_message(error_code)
        return None, f"COM 错误 ({error_code}): {error_message}"
    except Exception as e:
        return None, f"未知错误: {str(e)}"
```

### 进程崩溃检测

```python
import psutil
import time

def is_autocad_running():
    """检测 AutoCAD 是否正在运行"""
    for proc in psutil.process_iter(['name']):
        try:
            if 'acad.exe' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def wait_for_autocad_idle(timeout=60):
    """
    等待 AutoCAD 进程空闲

    参数：
        timeout: 超时时间（秒）

    返回：
        True 表示已空闲，False 表示超时
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                if 'acad.exe' in proc.info['name'].lower():
                    cpu_usage = proc.cpu_percent(interval=1.0)

                    # CPU 使用率低于 5% 认为是空闲
                    if cpu_usage < 5.0:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(1)

    return False
```

---

## 🔄 自动恢复机制

### 连接恢复

```python
class AutoCADConnection:
    """AutoCAD 连接管理器（支持自动恢复）"""

    def __init__(self):
        self.acad = None
        self.max_retries = 3
        self.retry_delay = 5  # 秒

    def connect(self):
        """连接到 AutoCAD（带重试）"""
        for attempt in range(self.max_retries):
            try:
                self.acad = win32com.client.GetActiveObject("AutoCAD.Application")
                print(f"✅ 连接成功（尝试 {attempt + 1}）")
                return True
            except:
                if attempt < self.max_retries - 1:
                    print(f"⚠️ 连接失败，{self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    try:
                        self.acad = win32com.client.Dispatch("AutoCAD.Application")
                        self.acad.Visible = True
                        print("✅ AutoCAD 已启动")
                        return True
                    except Exception as e:
                        print(f"❌ 无法连接或启动 AutoCAD: {e}")
                        return False
        return False

    def is_connected(self):
        """检查是否仍然连接"""
        try:
            # 尝试访问一个简单的属性
            _ = self.acad.Version
            return True
        except:
            return False

    def reconnect(self):
        """重新连接"""
        print("⚠️ 检测到连接断开，尝试重新连接...")
        self.acad = None
        return self.connect()
```

---

## 📚 最佳实践

### 1. 连接管理

- ✅ **优先使用 GetActiveObject**：先连接已运行的 AutoCAD
- ✅ **延迟启动**：只在必要时启动 AutoCAD
- ✅ **检查连接状态**：定期验证连接是否有效
- ✅ **优雅断开**：操作完成后正确释放 COM 对象

### 2. 文件操作

- ✅ **使用绝对路径**：避免相对路径引起的问题
- ✅ **检查文件存在性**：打开前验证文件是否存在
- ✅ **备份原文件**：重要操作前备份
- ✅ **显式保存**：不依赖自动保存

### 3. 命令执行

- ✅ **添加前缀**：使用 `._` 前缀避免本地化问题（如 `._ZOOM` 而非 `ZOOM`）
- ✅ **添加空格**：命令末尾添加空格代表回车
- ✅ **等待完成**：执行命令后等待足够时间
- ✅ **错误捕获**：所有命令都应有错误处理

### 4. 异常处理

- ✅ **捕获 COM 错误**：使用 `pywintypes.com_error`
- ✅ **友好错误消息**：提供可读的错误说明
- ✅ **日志记录**：记录所有异常
- ✅ **自动重试**：网络或临时错误应重试

### 5. 性能优化

- ✅ **批量操作**：避免频繁的单个操作
- ✅ **禁用重绘**：大量操作时临时禁用重绘
- ✅ **减少 COM 调用**：缓存常用对象和属性
- ✅ **并发控制**：避免多个进程同时操作同一文件

---

## 🔗 版本兼容性

### AutoCAD 2018-2024 差异

| 特性 | 2018-2020 | 2021-2024 | 注意事项 |
|------|-----------|-----------|---------|
| COM API | 完全支持 | 完全支持 | 无差异 |
| ProgID | AutoCAD.Application | AutoCAD.Application | 相同 |
| 版本号 | 22.0-23.1 | 24.0-24.3 | 可用于版本检测 |
| DWG 格式 | AC1032 | AC1035 | 需要注意保存格式 |
| 命令集 | 基本相同 | 部分新命令 | 旧命令保持兼容 |

### 跨版本代码示例

```python
def get_compatible_autocad():
    """获取兼容任何版本的 AutoCAD"""
    try:
        acad = win32com.client.GetActiveObject("AutoCAD.Application")
        version = float(acad.Version)

        # 检查版本范围
        if version < 22.0:
            print("⚠️ 警告：AutoCAD 版本过低，可能不兼容")
        elif version > 24.3:
            print("⚠️ 警告：AutoCAD 版本较新，未测试")
        else:
            print(f"✅ 支持的 AutoCAD 版本: {version}")

        return acad
    except Exception as e:
        print(f"❌ 获取 AutoCAD 失败: {e}")
        return None
```

---

## 🚨 常见问题和解决方案

### 问题 1：找不到 AutoCAD

**现象：** `pywintypes.com_error: (-2147467259, ...)`

**原因：**
- AutoCAD 未安装
- COM 注册损坏

**解决方案：**
```bash
# 重新注册 AutoCAD COM 接口
cd "C:\Program Files\Autodesk\AutoCAD 2024"
acad.exe /regserver
```

### 问题 2：命令执行无响应

**现象：** `SendCommand` 后无反应

**原因：**
- 命令字符串格式错误
- 缺少回车（空格）

**解决方案：**
```python
# ❌ 错误
doc.SendCommand("ZOOM E")

# ✅ 正确
doc.SendCommand("._ZOOM _E ")  # 注意前缀和末尾空格
```

### 问题 3：文件锁定

**现象：** 无法打开或保存文件

**原因：**
- 文件被其他进程占用
- AutoCAD 未正确关闭

**解决方案：**
```python
import os
import time

def wait_for_file_unlock(file_path, timeout=30):
    """等待文件解锁"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # 尝试以独占模式打开文件
            with open(file_path, 'r+'):
                return True
        except IOError:
            time.sleep(1)

    return False
```

### 问题 4：内存泄漏

**现象：** 长时间运行后内存占用增加

**原因：**
- COM 对象未释放

**解决方案：**
```python
def cleanup_com_objects():
    """清理 COM 对象"""
    import gc
    import pythoncom

    gc.collect()
    pythoncom.CoUninitialize()
```

---

## 📖 参考资源

### 官方文档

- [AutoCAD ActiveX and VBA Reference](https://help.autodesk.com/view/OARX/2024/ENU/)
- [AutoCAD Developer Documentation](https://www.autodesk.com/developer-network/platform-technologies/autocad)

### Python 库

- [pywin32](https://github.com/mhammond/pywin32) - Windows COM 接口
- [comtypes](https://github.com/enthought/comtypes) - 另一个 COM 库（备选）

### 社区资源

- [AutoCAD DevBlog](https://adndevblog.typepad.com/autocad/)
- [Autodesk Forums](https://forums.autodesk.com/)

---

**文档创建完成：** 2025-10-24
**下一步：** 创建可执行的示例代码
