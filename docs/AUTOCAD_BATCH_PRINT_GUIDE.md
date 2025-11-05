# AutoCAD 批量打印全自动化脚本使用指南

## 📋 目录

- [方案概述](#方案概述)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [故障排查](#故障排查)
- [高级配置](#高级配置)

---

## 方案概述

### 架构设计

```
按键精灵全自动化流程
    ↓
步骤1: 关闭现有AutoCAD进程
    ↓
步骤2: 启动AutoCAD并打开DWG文件
    ↓
步骤3: 等待AutoCAD窗口完全加载
    ↓
步骤4: 执行bplot命令
    ↓
步骤5: 等待批量打印对话框
    ↓
步骤6: 点击"选择批量打印图纸"按钮
    ↓
步骤7: 输入all选择所有图纸
    ↓
完成（用户手动确认打印）
```

### 优势

✅ **完全自动化** - 从启动到配置一键完成
✅ **无需编程** - 纯按键精灵脚本，易于维护
✅ **窗口检测** - 智能等待，稳定可靠
✅ **多版本支持** - 兼容AutoCAD 2014/2021等版本
✅ **容错机制** - 多种备用方案确保成功率

---

## 环境要求

### 必需软件

| 软件 | 版本要求 | 说明 |
|------|---------|------|
| **按键精灵** | 9.x 或以上 | 主要自动化工具 |
| **AutoCAD** | 2014/2021/其他 | 目标CAD软件 |
| **Windows** | 7/10/11 | 操作系统 |

### 可选软件

| 软件 | 用途 |
|------|-----|
| **Python 3.x** | 批量调用脚本 |
| **Umi-OCR** | 按钮识别增强 |

---

## 快速开始

### 步骤1: 安装按键精灵

1. 下载并安装按键精灵（[官网](https://www.anjian.com/)）
2. 启动按键精灵软件
3. 确保已获得完整版权限（支持插件功能）

### 步骤2: 导入脚本

1. 打开按键精灵
2. 点击"新建脚本"
3. 将 `scripts/autocad_batch_print_full.Q` 内容复制粘贴
4. 保存脚本（命名为"AutoCAD批量打印"）

### 步骤3: 配置路径

**编辑脚本开头的配置区域：**

```vbscript
// AutoCAD 可执行文件路径
Dim AutoCADExePath
AutoCADExePath = "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

// DWG 文件路径
Dim DWGFilePath
DWGFilePath = "F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"
```

**修改为您的实际路径！**

### 步骤4: 运行测试

1. 点击"启动脚本"按钮
2. 观察日志输出
3. 检查每个步骤是否成功执行

---

## 配置说明

### 核心配置项

#### 1. AutoCAD路径配置

```vbscript
// 主要路径（优先使用）
AutoCADExePath = "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

// 备用路径（按顺序尝试）
AlternativePaths(0) = "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe"
AlternativePaths(1) = "C:\Program Files (x86)\Autodesk\AutoCAD 2014\acad.exe"
```

**如何查找AutoCAD路径：**
1. 右键点击AutoCAD快捷方式
2. 选择"属性"
3. 复制"目标"路径

#### 2. DWG文件路径

```vbscript
DWGFilePath = "F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"
```

**支持中文路径！**

#### 3. 窗口标题关键字

```vbscript
// AutoCAD窗口标题
AutoCADTitles(0) = "AutoCAD 2014"
AutoCADTitles(1) = "AutoCAD 2021"
AutoCADTitles(2) = "AutoCAD"

// 对话框标题
DialogTitles(0) = "批量打印"
DialogTitles(1) = "Batch Plot"
DialogTitles(2) = "发布"
```

**如果窗口检测失败，添加您的AutoCAD版本窗口标题！**

#### 4. 超时设置

```vbscript
Const MAX_WAIT_AUTOCAD = 60000    // AutoCAD启动超时 60秒
Const MAX_WAIT_DIALOG = 30000     // 对话框超时 30秒
Const CHECK_INTERVAL = 1000       // 检测间隔 1秒
```

**配置建议：**
- 老电脑增加超时时间
- 快速电脑可减少等待时间

---

## 使用方法

### 方法A: 直接运行（单文件）

1. 修改脚本中的 `DWGFilePath` 为目标文件
2. 点击"启动脚本"
3. 等待自动完成

### 方法B: 命令行传参（批量处理）

**启动命令：**
```batch
"C:\Program Files\QuickMacro\QMApp.exe" "autocad_batch_print_full.Q" "F:\cad\file1.dwg"
```

**批处理脚本示例：**
```batch
@echo off
set SCRIPT_PATH=C:\AutoCAD_Automation\autocad_batch_print_full.Q
set QM_PATH=C:\Program Files\QuickMacro\QMApp.exe

for %%f in (F:\cad\*.dwg) do (
    echo 正在处理: %%f
    "%QM_PATH%" "%SCRIPT_PATH%" "%%f"
    timeout /t 120 /nobreak
)

echo 批量处理完成！
pause
```

### 方法C: Python集成（高级）

**创建Python启动器：**

```python
import subprocess
import time
from pathlib import Path

def batch_print_with_qm(dwg_file: str):
    """使用按键精灵批量打印"""
    qm_exe = r"C:\Program Files\QuickMacro\QMApp.exe"
    script = r"C:\AutoCAD_Automation\autocad_batch_print_full.Q"

    cmd = [qm_exe, script, dwg_file]

    print(f"启动按键精灵: {dwg_file}")
    subprocess.Popen(cmd)

    # 等待完成（根据文件大小调整）
    time.sleep(120)

# 批量处理
dwg_files = Path("F:/cad").glob("*.dwg")
for dwg in dwg_files:
    batch_print_with_qm(str(dwg))
```

---

## 故障排查

### 问题1: 找不到AutoCAD窗口

**症状：**
```
❌ 错误: 未找到AutoCAD窗口
```

**解决方案：**

1. **检查AutoCAD是否成功启动**
   - 手动运行AutoCAD查看是否正常
   - 检查DWG文件是否损坏

2. **修改窗口标题关键字**
   ```vbscript
   // 查看实际窗口标题
   // 使用Windows任务管理器或Spy++工具
   AutoCADTitles(4) = "您的窗口标题"
   ```

3. **增加等待时间**
   ```vbscript
   Const MAX_WAIT_AUTOCAD = 120000  // 改为120秒
   ```

### 问题2: 无法点击按钮

**症状：**
```
⚠️  图像识别未找到按钮
```

**解决方案：**

**方案A: 使用固定坐标**
```vbscript
// 修改 ClickByPosition 函数中的坐标百分比
click_x = left + CInt(width * 0.35)  // 调整为35%
click_y = top + CInt(height * 0.50)  // 调整为50%
```

**方案B: 截取按钮图片（推荐）**

1. **手动打开批量打印对话框**
2. **使用截图工具精确截取按钮区域**
3. **保存为 `button_select_sheets.bmp`**
4. **放置到脚本同目录或指定路径**

```vbscript
pic_path = "C:\AutoCAD_Automation\button_select_sheets.bmp"
```

**图片要求：**
- 格式：BMP
- 尺寸：尽量小（仅包含按钮）
- 背景：尽量统一

**方案C: 使用颜色识别**
```vbscript
// 在ClickSelectButton函数中添加颜色查找
Dim color_x, color_y
color_x = -1
color_y = -1

// 查找特定颜色（按钮背景色）
Dim find_color_result
find_color_result = Plugin.Color.FindColorEx(left, top, right, bottom, "2A8FBD", 0, 0.9, color_x, color_y)

If find_color_result = 0 Then
    TracePrint "   ✅ 通过颜色找到按钮"
    MoveTo color_x, color_y
    LeftClick 1
    Exit Function
End If
```

### 问题3: bplot命令执行失败

**症状：**
```
❌ 错误: 未找到批量打印对话框
```

**解决方案：**

1. **检查AutoCAD命令别名**
   ```
   // AutoCAD命令行输入
   ALIASEDIT

   // 查看bplot是否存在
   // 如果不存在，修改脚本使用完整命令
   ```

2. **修改命令发送方式**
   ```vbscript
   // 方法1: 使用完整命令名
   SayString "_PUBLISH"  // 或 "_PLOT"

   // 方法2: 增加延迟
   KeyPress "Esc", 2
   Delay 1000  // 增加到1秒
   SayString "_.bplot"
   Delay 2000  // 增加到2秒
   KeyPress "Enter", 1
   ```

3. **手动测试命令**
   - 打开AutoCAD
   - 手动输入 `_.bplot` 并回车
   - 观察对话框标题是否匹配脚本配置

### 问题4: 脚本执行过快

**症状：**
操作跳过或点击失败

**解决方案：**

**增加关键步骤的延迟：**
```vbscript
// 在步骤之间增加延迟
Delay 8000   // AutoCAD加载后等待8秒
Delay 5000   // bplot命令后等待5秒
Delay 2000   // 点击按钮后等待2秒
```

### 问题5: 命令行参数不生效

**症状：**
始终使用脚本中的默认路径

**解决方案：**

**按键精灵命令行传参格式：**
```batch
QMApp.exe /r "脚本路径" /p "参数"
```

**修改 CheckCommandLineArgs 函数：**
```vbscript
Sub CheckCommandLineArgs()
    // 按键精灵9.x使用CommandLine获取参数
    Dim args
    args = CommandLine

    If args <> "" Then
        DWGFilePath = args
        TracePrint "使用命令行参数: " & DWGFilePath
    End If
End Sub
```

---

## 高级配置

### 1. 自动点击打印按钮

**启用自动打印（谨慎使用）：**

在主流程末尾取消注释：
```vbscript
// 步骤8: 完成
// ...

// 启用自动打印
Call ClickPrintButton(dialog_hwnd)
```

**⚠️ 警告：启用后将自动执行打印，请确保设置正确！**

### 2. 日志输出到文件

```vbscript
// 在 TracePrint 函数中添加文件输出
Sub TracePrint(msg)
    Dim timestamp, log_msg
    timestamp = Year(Now()) & "-" & _
                Right("0" & Month(Now()), 2) & "-" & _
                Right("0" & Day(Now()), 2) & " " & _
                Right("0" & Hour(Now()), 2) & ":" & _
                Right("0" & Minute(Now()), 2) & ":" & _
                Right("0" & Second(Now()), 2)

    log_msg = timestamp & " | " & msg

    // 输出到控制台
    TracePrint log_msg

    // 输出到文件
    Dim log_file
    log_file = "C:\AutoCAD_Automation\logs\autocad_batch.log"
    Call Plugin.File.AppendFile(log_file, log_msg & vbCrLf)
End Sub
```

### 3. 错误重试机制

```vbscript
// 在关键步骤添加重试逻辑
Function WaitForDialogWithRetry(max_retry)
    Dim retry_count, hwnd
    retry_count = 0

    Do While retry_count < max_retry
        hwnd = WaitForDialog()

        If hwnd > 0 Then
            WaitForDialogWithRetry = hwnd
            Exit Function
        End If

        TracePrint "   重试第 " & (retry_count + 1) & " 次..."
        retry_count = retry_count + 1
        Delay 5000
    Loop

    WaitForDialogWithRetry = 0
End Function
```

### 4. 集成通知功能

```vbscript
// 完成后发送通知
Sub SendCompletionNotification()
    // 方法1: 系统消息框
    MsgBox "AutoCAD批量打印已完成！", vbInformation, "完成通知"

    // 方法2: Windows通知（需要额外工具）
    // RunApp "C:\Tools\notify.exe" & " AutoCAD批量打印完成"

    // 方法3: 邮件通知（集成Python脚本）
    // RunApp "python C:\Tools\send_email.py 批量打印完成"
End Sub
```

---

## 最佳实践

### 📌 使用建议

1. **首次使用先测试**
   - 使用简单的DWG文件测试
   - 观察每个步骤的执行情况
   - 调整延迟时间以匹配您的电脑性能

2. **准备按钮图片**
   - 提前截取"选择图纸"按钮的图片
   - 保存为高清BMP格式
   - 配置正确的图片路径

3. **批量处理注意事项**
   - 每个文件之间留足够的间隔时间
   - 监控第一个文件的完整流程
   - 使用日志记录处理状态

4. **备份重要文件**
   - 批量打印前备份原始DWG文件
   - 保存打印配置文件
   - 记录成功的配置参数

### ⚡ 性能优化

1. **减少不必要的等待**
   ```vbscript
   // 使用动态等待而非固定延迟
   Function WaitForWindowSmart(title, max_wait)
       Dim elapsed_time, hwnd
       elapsed_time = 0

       Do While elapsed_time < max_wait
           hwnd = Plugin.Window.Find(0, title)
           If hwnd > 0 Then
               Exit Do
           End If

           Delay 100  // 短间隔检测
           elapsed_time = elapsed_time + 100
       Loop

       WaitForWindowSmart = hwnd
   End Function
   ```

2. **并行处理多个文件**
   - 使用多个按键精灵实例
   - 每个实例处理不同的文件
   - 注意资源占用

---

## 附录

### A. 按键精灵常用命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `RunApp` | 启动程序 | `RunApp "notepad.exe"` |
| `Delay` | 延迟(毫秒) | `Delay 1000` |
| `KeyPress` | 按键 | `KeyPress "Enter", 1` |
| `SayString` | 输入文本 | `SayString "hello"` |
| `MoveTo` | 移动鼠标 | `MoveTo 100, 200` |
| `LeftClick` | 左键点击 | `LeftClick 1` |
| `Plugin.Window.Find` | 查找窗口 | `hwnd = Plugin.Window.Find(0, "标题")` |

### B. AutoCAD命令速查

| 命令 | 说明 |
|------|------|
| `BPLOT` | 批量打印 |
| `PUBLISH` | 发布 |
| `PLOT` | 打印 |
| `PAGESETUP` | 页面设置 |

### C. 相关资源

- [按键精灵官网](https://www.anjian.com/)
- [AutoCAD开发者中心](https://www.autodesk.com/developer-network/platform-technologies/autocad)
- [项目GitHub](https://github.com/your-repo/cad-automation)

---

## 📞 支持与反馈

如有问题或建议，请：
1. 查看本文档的[故障排查](#故障排查)章节
2. 提交Issue到GitHub仓库
3. 联系技术支持团队

---

**版本历史：**
- v2.0 (2025-11-03): 完整版发布，支持全流程自动化
- v1.0 (2025-11-02): 初始版本

**作者：** CAD Auto Processor Team
**最后更新：** 2025-11-03
