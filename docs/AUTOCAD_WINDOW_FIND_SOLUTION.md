# AutoCAD 窗口查找失败问题解决方案

## 问题描述

AutoCAD 批量打印脚本 (`autocad_batch_print_full.Q`) 在执行时无法找到 AutoCAD 主窗口，导致后续流程无法继续。

### 日志特征
```
✅ AutoCAD进程已启动
⚠️ 10秒后仍未找到，进行窗口诊断...
❌ 未找到任何相关窗口
💡 AutoCAD可能未启动或启动失败
```

## 根本原因分析

### 1. **启动对话框阻塞主窗口**
AutoCAD 启动时可能弹出以下对话框:
- 许可证确认对话框
- 欢迎页面/启动中心
- 文件恢复对话框
- 版本更新提示
- 网络许可证检查

这些对话框会导致主窗口未完全初始化，窗口标题和类名都处于临时状态。

### 2. **大文件加载时间过长**
文件 `PCX20.01 主体钢结构(20230301).dwg` 可能包含:
- 大量复杂图形实体
- 外部引用 (XREF)
- 大尺寸光栅图像
- 复杂的块定义

建议等待时间: **30-45 秒**

### 3. **中文文件名编码问题**
按键精灵的窗口查找 API 可能无法正确处理包含中文的窗口标题:
- `Plugin.Window.Find(0, "主体钢结构")` 可能失败
- 需要使用类名查找替代

### 4. **AutoCAD 2014 特定问题**
- 窗口类名: `AfxFrameOrView80` 或 `AfxFrameOrView`
- 可能以兼容模式运行
- 可能需要管理员权限

## 解决方案

### 方案 1: 使用诊断工具 (推荐首选)

我已创建专用诊断脚本 `autocad_window_diagnostic.Q`

#### 使用步骤:

1. **手动启动 AutoCAD**
   ```
   打开 AutoCAD 2014
   加载文件: F:\cad\caddd\PCX20.01 主体钢结构(20230301).dwg
   等待文件完全加载完成
   ```

2. **运行诊断脚本**
   ```
   在按键精灵中打开: autocad_window_diagnostic.Q
   点击运行
   根据提示确认 AutoCAD 已打开
   ```

3. **查看诊断结果**

   诊断脚本会输出:
   - 所有匹配的窗口句柄
   - 窗口标题(完整标题)
   - 窗口类名(用于精确查找)
   - 窗口尺寸和位置
   - AutoCAD 窗口的置信度评分

4. **根据结果更新主脚本**

   找到诊断结果中标记为 "⭐ 高概率" 的窗口信息，然后:

   ```vbscript
   // 在 autocad_batch_print_full.Q 的第 38-43 行更新:
   Dim AutoCADTitles(3)
   AutoCADTitles(0) = "[从诊断结果复制完整窗口标题]"
   AutoCADTitles(1) = "AutoCAD 2014"
   AutoCADTitles(2) = "AutoCAD"
   AutoCADTitles(3) = ".dwg"
   ```

### 方案 2: 增加启动等待时间

修改主脚本 `/scripts/autocad_batch_print_full.Q`:

```vbscript
// 第 218 行，将等待时间从 15 秒增加到 30 秒
Delay 30000  // 增加到30秒让AutoCAD完全启动

// 第 233 行，将文件加载等待时间从 10 秒增加到 20 秒
Delay 20000  // 增加到20秒让文件完全加载
```

**原理**: 给予 AutoCAD 足够时间完成以下流程:
1. 进程启动 (5-10 秒)
2. 加载界面组件 (5-10 秒)
3. 打开 DWG 文件 (10-20 秒)
4. 渲染图形 (5-10 秒)

总计: 25-50 秒

### 方案 3: 添加启动参数优化

修改 AutoCAD 启动命令，跳过启动对话框:

```vbscript
// 第 342-343 行修改为:
Dim cmd_line
cmd_line = """" & acad_path & """ """ & dwg_path & """ /nologo /nossm /p DefaultProfile"

// 参数说明:
// /nologo      - 跳过启动画面
// /nossm       - 禁用图纸集管理器
// /p ProfileName - 使用指定配置文件（加快启动）
```

### 方案 4: 使用备用窗口查找策略

在主脚本的 `WaitForAutoCADWindow()` 函数中添加新策略:

#### 4.1 使用 FindEx 枚举所有 Afx 窗口

在第 462 行的窗口类名查找循环中，添加更宽松的匹配:

```vbscript
// 策略3的增强版本
For i = 0 To UBound(autocad_classes)
    // 原有的精确查找
    hwnd = Plugin.Window.FindEx(0, 0, autocad_classes(i), "")
    If hwnd > 0 Then
        // 验证这是 AutoCAD 窗口而不是其他 MFC 应用
        Dim win_title
        win_title = Plugin.Window.GetTitle(hwnd)

        // 只接受包含 dwg 或 AutoCAD 的窗口
        If InStr(win_title, ".dwg") > 0 Or _
           InStr(win_title, "AutoCAD") > 0 Or _
           InStr(win_title, "acad") > 0 Then
            LogMessage "   ✅ 找到窗口（按类名+验证）: " & autocad_classes(i)
            LogMessage "      窗口标题: " & win_title
            Call PrintWindowInfo(hwnd, "      ")
            WaitForAutoCADWindow = hwnd
            Exit Function
        End If
    End If
Next i
```

#### 4.2 使用模糊匹配查找

```vbscript
// 在策略3之后添加策略4：模糊匹配
// 查找所有可能包含文件名片段的窗口

Dim filename_parts(5)
filename_parts(0) = "PCX"
filename_parts(1) = "20.01"
filename_parts(2) = "2023"
filename_parts(3) = "钢"
filename_parts(4) = "DWG"
filename_parts(5) = "dwg"

For i = 0 To UBound(filename_parts)
    hwnd = Plugin.Window.Find(0, filename_parts(i))
    If hwnd > 0 Then
        Dim verify_class
        verify_class = Plugin.Window.GetClass(hwnd)

        // 只接受 MFC 窗口类
        If InStr(verify_class, "Afx") > 0 Then
            LogMessage "   ✅ 找到窗口（模糊匹配）: 包含'" & filename_parts(i) & "'"
            LogMessage "      类名验证: " & verify_class
            Call PrintWindowInfo(hwnd, "      ")
            WaitForAutoCADWindow = hwnd
            Exit Function
        End If
    End If
Next i
```

### 方案 5: 使用按键检测窗口焦点

如果 AutoCAD 窗口处于前台但无法被查找到，可以使用键盘焦点检测:

```vbscript
// 策略5: 检测前台窗口
Dim foreground_hwnd
foreground_hwnd = Plugin.Window.GetForeground()

If foreground_hwnd > 0 Then
    Dim fg_class, fg_title
    fg_class = Plugin.Window.GetClass(foreground_hwnd)
    fg_title = Plugin.Window.GetTitle(foreground_hwnd)

    // 检查前台窗口是否为 AutoCAD
    If InStr(fg_class, "Afx") > 0 And _
       (InStr(fg_title, "AutoCAD") > 0 Or InStr(fg_title, ".dwg") > 0) Then
        LogMessage "   ✅ 找到前台窗口: " & fg_title
        WaitForAutoCADWindow = foreground_hwnd
        Exit Function
    End If
End If
```

## 完整修复流程

### 步骤 1: 运行诊断 ✅

```
1. 打开按键精灵
2. 加载脚本: autocad_window_diagnostic.Q
3. 手动启动 AutoCAD 并打开 DWG 文件
4. 运行诊断脚本
5. 记录输出的窗口信息
```

### 步骤 2: 根据诊断结果选择方案

| 诊断结果 | 推荐方案 |
|---------|---------|
| 找到窗口，但标题与预期不符 | 方案 1: 更新标题关键字 |
| 10秒内未找到窗口，20秒后找到 | 方案 2: 增加等待时间 |
| 找到启动对话框而非主窗口 | 方案 3: 添加启动参数 |
| 完全找不到任何相关窗口 | 方案 4: 使用备用查找策略 |
| 诊断工具也无法找到 | 检查 AutoCAD 是否真的启动了 |

### 步骤 3: 应用修复并测试

```
1. 根据诊断结果修改主脚本
2. 保存修改
3. 重新运行 autocad_batch_print_full.Q
4. 观察日志输出
5. 如果仍然失败，返回步骤1重新诊断
```

## 预防措施

### 1. 禁用 AutoCAD 启动对话框

在 AutoCAD 中永久禁用启动对话框:

```
1. 打开 AutoCAD
2. 输入命令: STARTUPTODAY
3. 设置为: 0 (不显示启动对话框)
4. 输入命令: OPTIONS
5. 在"打开和保存"选项卡中:
   - 取消勾选"显示启动中心"
   - 取消勾选"自动恢复"（如果不需要）
```

### 2. 创建专用配置文件

创建一个用于批量打印的精简配置:

```
1. 在 AutoCAD 中输入: OPTIONS
2. 点击"配置"选项卡
3. 点击"添加到列表"创建新配置文件
4. 命名为: BatchPrint
5. 配置以下设置:
   - 关闭所有不必要的工具栏
   - 禁用自动保存
   - 禁用背景图
   - 使用2D线框视觉样式
6. 保存配置

然后在脚本中使用此配置:
cmd_line = """" & acad_path & """ """ & dwg_path & """ /p BatchPrint"
```

### 3. 使用简单文件名测试

先用简单的纯英文文件名测试:

```
创建测试文件: test.dwg
修改脚本第27行:
DWGFilePath = "F:\cad\caddd\test.dwg"

测试成功后再使用复杂的中文文件名
```

## 附加说明

### 按键精灵窗口查找 API 限制

```vbscript
// Plugin.Window.Find(parent, title)
// 限制:
// 1. 标题匹配是部分匹配(包含即可)
// 2. 对中文支持有限，可能受系统编码影响
// 3. 无法匹配隐藏或最小化的窗口

// Plugin.Window.FindEx(parent, after, class, title)
// 优势:
// 1. 可以按类名精确查找
// 2. 可以枚举多个窗口(使用 after 参数)
// 3. 更可靠，不受窗口标题变化影响
```

### AutoCAD 窗口类名参考

| AutoCAD 版本 | 主窗口类名 |
|-------------|-----------|
| AutoCAD 2014 | AfxFrameOrView80 |
| AutoCAD 2015 | AfxFrameOrView80 |
| AutoCAD 2016 | AfxFrameOrView90 |
| AutoCAD 2017 | AfxFrameOrView90 |
| AutoCAD 2018 | AfxFrameOrView100 |
| AutoCAD 2019 | AfxFrameOrView100 |
| AutoCAD 2020 | AfxFrameOrView140 |
| AutoCAD 2021 | AfxFrameOrView140 |
| AutoCAD 2022+ | AfxFrameOrView140 |

## 快速修复建议

如果需要快速解决，建议按以下顺序尝试:

1. **最快**: 增加等待时间到 30-40 秒 (方案 2)
2. **最稳**: 运行诊断工具获取准确信息 (方案 1)
3. **最佳**: 结合方案 2 + 方案 3 + 禁用启动对话框

## 联系支持

如果以上所有方案都无法解决问题，请提供:
1. 诊断脚本的完整输出
2. AutoCAD 版本号 (输入命令 `ABOUT`)
3. Windows 版本和语言设置
4. 按键精灵版本号
