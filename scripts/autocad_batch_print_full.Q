//==============================================================================
// AutoCAD 批量打印全自动化脚本 (按键精灵完整版)
//
// 功能：完整自动化流程
//   步骤1: 启动AutoCAD并打开DWG文件
//   步骤2: 等待AutoCAD窗口加载完成
//   步骤3: 执行bplot命令
//   步骤4: 点击"选择批量打印图纸"按钮
//   步骤5: 输入all并回车
//   步骤6: 完成打印设置
//
// 作者: CAD Auto Processor Team
// 日期: 2025-11-03
// 版本: 2.0 (全流程版本)
//==============================================================================

//==============================================================================
// 配置区域 - 请根据实际情况修改
//==============================================================================

// AutoCAD 可执行文件路径
Dim AutoCADExePath
AutoCADExePath = "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"

// DWG 文件路径（可通过命令行参数传入）
Dim DWGFilePath
DWGFilePath = "F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

// 备用AutoCAD路径（按优先级尝试）
Dim AlternativePaths(1)
AlternativePaths(0) = "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe"
AlternativePaths(1) = "C:\Program Files (x86)\Autodesk\AutoCAD 2014\acad.exe"

// AutoCAD 窗口标题关键字
Dim AutoCADTitles(3)
AutoCADTitles(0) = "AutoCAD 2014"
AutoCADTitles(1) = "AutoCAD 2021"
AutoCADTitles(2) = "AutoCAD"
AutoCADTitles(3) = "acad"

// 批量打印对话框标题关键字
Dim DialogTitles(3)
DialogTitles(0) = "批量打印 V3"        // 精确匹配带版本号的对话框
DialogTitles(1) = "批量打印"
DialogTitles(2) = "Batch Plot"
DialogTitles(3) = "发布"

// 按钮文本关键字（用于查找）
Dim ButtonTexts(4)
ButtonTexts(0) = "选择批量打印图纸"
ButtonTexts(1) = "设置批量打印图纸表"
ButtonTexts(2) = "选择要处理的图纸"
ButtonTexts(3) = "Select Drawings"
ButtonTexts(4) = "Add Sheets"

// 等待超时设置（毫秒）
Const MAX_WAIT_AUTOCAD = 60000      // 等待AutoCAD启动 60秒
Const MAX_WAIT_LOADED = 30000       // 等待文件加载完成 30秒
Const MAX_WAIT_DIALOG = 30000       // 等待对话框 30秒
Const CHECK_INTERVAL = 1000         // 检测间隔 1秒

//==============================================================================
// 手动按钮坐标配置（如果自动查找失败）
//==============================================================================
// 使用方法：
// 1. 手动打开批量打印对话框
// 2. 移动鼠标到"选择要处理的图纸"按钮上
// 3. 按键精灵查看鼠标坐标（或用GetCursorPos命令）
// 4. 将坐标填入下面
Const MANUAL_BUTTON_X = 0    // 按钮X坐标（0表示使用自动查找）
Const MANUAL_BUTTON_Y = 0    // 按钮Y坐标（0表示使用自动查找）

//==============================================================================
// 工具函数
//==============================================================================

// 获取并打印窗口详细信息
Sub PrintWindowInfo(hwnd, prefix)
    If hwnd <= 0 Then
        LogMessage prefix & "无效窗口句柄"
        Exit Sub
    End If

    LogMessage prefix & "窗口详细信息:"
    LogMessage prefix & "  句柄: " & hwnd

    // 尝试获取窗口矩形位置
    Dim rect
    rect = Plugin.Window.GetWindowRect(hwnd)
    If rect <> "" Then
        LogMessage prefix & "  位置: " & rect
    End If

    // 尝试获取窗口类名
    Dim class_name
    class_name = Plugin.Window.GetClass(hwnd)
    If class_name <> "" Then
        LogMessage prefix & "  类名: " & class_name
    End If

    // 检查窗口状态
    LogMessage prefix & "  可见: " & (hwnd > 0)
End Sub

//==============================================================================
// 主流程
//==============================================================================

Call Main()

Sub Main()
    Call PrintBanner()

    // 检查命令行参数（如果有传入DWG路径）
    Call CheckCommandLineArgs()

    // 步骤1: 强制关闭现有AutoCAD进程（确保干净启动）
    LogMessage ""
    LogMessage "[步骤1] 强制关闭现有AutoCAD进程..."
    Call CloseExistingAutoCAD()
    Delay 2000

    // 步骤2: 启动AutoCAD并打开文件
    LogMessage ""
    LogMessage "[步骤2] 启动AutoCAD并打开文件..."
    LogMessage "   文件: " & DWGFilePath

    Dim launch_success
    launch_success = LaunchAutoCAD(DWGFilePath)

    If Not launch_success Then
        LogMessage "❌ 错误: AutoCAD启动失败"
        Call ShowError("AutoCAD启动失败，请检查路径配置")
        ExitScript
    End If

    // 步骤3: 等待AutoCAD窗口完全加载
    LogMessage ""
    LogMessage "[步骤3] 等待AutoCAD窗口加载..."

    Dim acad_hwnd
    acad_hwnd = WaitForAutoCADWindow()

    If acad_hwnd = 0 Then
        LogMessage "❌ 错误: 未找到AutoCAD窗口"
        Call ShowError("未找到AutoCAD窗口")
        ExitScript
    End If

    LogMessage "✅ AutoCAD窗口已就绪 (句柄: " & acad_hwnd & ")"

    // 额外等待确保文件完全加载
    LogMessage "   等待文件加载完成..."
    Delay 8000  // 等待8秒让文件完全加载

    // 步骤4: 激活AutoCAD窗口并执行bplot命令
    LogMessage ""
    LogMessage "[步骤4] 执行BPLOT命令..."

    Delay 500

    Call ExecuteBplotCommand()

    // 步骤5: 等待批量打印对话框
    LogMessage ""
    LogMessage "[步骤5] 等待批量打印对话框..."

    Dim dialog_hwnd
    dialog_hwnd = WaitForDialog()

    If dialog_hwnd = 0 Then
        LogMessage "❌ 错误: 未找到批量打印对话框"
        Call ShowError("未找到批量打印对话框")
        ExitScript
    End If

    LogMessage "✅ 批量打印对话框已打开 (句柄: " & dialog_hwnd & ")"
    Delay 1000

    // 步骤6: 点击"选择批量打印图纸"按钮
    LogMessage ""
    LogMessage "[步骤6] 查找并点击选择按钮..."

    Call ActivateWindow(dialog_hwnd)
    Delay 500

    Dim button_clicked
    button_clicked = ClickSelectButton(dialog_hwnd)

    If Not button_clicked Then
        LogMessage "⚠️  使用备用方案点击..."
        Call ClickByPosition(dialog_hwnd)
    End If

    Delay 1500

    // 步骤7: 输入all并回车
    LogMessage ""
    LogMessage "[步骤7] 输入 all 选择所有图纸..."

    Call InputAll()
    Delay 2000

    // 步骤8: 完成
    LogMessage ""
    LogMessage "========================================="
    LogMessage "✅ 自动化流程执行完成！"
    LogMessage "========================================="
    LogMessage ""
    LogMessage "💡 后续操作："
    LogMessage "   1. 检查选中的图纸数量"
    LogMessage "   2. 确认打印设置"
    LogMessage "   3. 点击'打印'按钮开始批量打印"
    LogMessage ""

    // 可选：自动点击打印按钮（谨慎使用）
    // Call ClickPrintButton(dialog_hwnd)

End Sub

//==============================================================================
// AutoCAD 启动和加载
//==============================================================================

// 启动AutoCAD并打开文件
Function LaunchAutoCAD(dwg_path)
    // 检查AutoCAD路径是否存在
    Dim acad_path
    acad_path = AutoCADExePath

    If Not Plugin.File.IsFileExist(acad_path) Then
        LogMessage "⚠️  默认路径不存在，尝试备用路径..."

        Dim i, found
        found = False

        For i = 0 To UBound(AlternativePaths)
            If Plugin.File.IsFileExist(AlternativePaths(i)) Then
                acad_path = AlternativePaths(i)
                LogMessage "   找到AutoCAD: " & acad_path
                found = True
                Exit For
            End If
        Next

        If Not found Then
            LogMessage "❌ 错误: 无法找到AutoCAD可执行文件"
            LaunchAutoCAD = False
            Exit Function
        End If
    End If

    // 检查DWG文件是否存在
    If Not Plugin.File.IsFileExist(dwg_path) Then
        LogMessage "❌ 错误: DWG文件不存在: " & dwg_path
        LaunchAutoCAD = False
        Exit Function
    End If

    // 构建启动命令
    Dim cmd_line
    cmd_line = """" & acad_path & """ """ & dwg_path & """"

    LogMessage "   启动命令: " & cmd_line

    // 启动AutoCAD
    RunApp acad_path & " " & """" & dwg_path & """"

    LogMessage "   ✅ AutoCAD进程已启动"

    LaunchAutoCAD = True
End Function

// 关闭现有AutoCAD进程（增强版 - 使用taskkill）
Sub CloseExistingAutoCAD()
    LogMessage "   检查现有AutoCAD进程..."
    RunApp "taskkill /IM acad.exe /T /F"
End Sub

// 等待AutoCAD窗口出现
Function WaitForAutoCADWindow()
    Dim hwnd, elapsed_time, i
    hwnd = 0
    elapsed_time = 0

    LogMessage "⏳ 正在查找AutoCAD窗口..."
    LogMessage "   将尝试以下窗口标题："
    For i = 0 To UBound(AutoCADTitles)
        LogMessage "     - " & AutoCADTitles(i)
    Next

    Do While elapsed_time < MAX_WAIT_AUTOCAD
        For i = 0 To UBound(AutoCADTitles)
            hwnd = Plugin.Window.Find(0, AutoCADTitles(i))

            If hwnd > 0 Then
                LogMessage "   ✅ 找到窗口: " & AutoCADTitles(i) & " (句柄:" & hwnd & ")"
                Call PrintWindowInfo(hwnd, "      ")
                WaitForAutoCADWindow = hwnd
                Exit Function
            End If
        Next

        // 如果前面都失败，尝试查找任何包含"AutoCAD"的窗口
        hwnd = Plugin.Window.Find(0, "AutoCAD")
        If hwnd > 0 Then
            LogMessage "   ✅ 找到窗口: AutoCAD (通配, 句柄:" & hwnd & ")"
            Call PrintWindowInfo(hwnd, "      ")
            WaitForAutoCADWindow = hwnd
            Exit Function
        End If

        // 尝试查找acad.exe的窗口
        hwnd = Plugin.Window.Find(0, "")
        If hwnd > 0 Then
            // 找到了某个窗口，先假设是它
            LogMessage "   ⚠️  使用第一个找到的窗口 (句柄:" & hwnd & ")"
            Call PrintWindowInfo(hwnd, "      ")
            WaitForAutoCADWindow = hwnd
            Exit Function
        End If

        Delay CHECK_INTERVAL
        elapsed_time = elapsed_time + CHECK_INTERVAL

        If elapsed_time Mod 5000 = 0 Then
            LogMessage "   等待中... (" & (elapsed_time / 1000) & "秒/" & (MAX_WAIT_AUTOCAD / 1000) & "秒)"
            LogMessage "   提示: 如果CAD已启动但脚本未检测到，请手动关闭并重试"
        End If
    Loop

    WaitForAutoCADWindow = 0
End Function

//==============================================================================
// BPLOT命令执行
//==============================================================================

// 执行BPLOT命令
Sub ExecuteBplotCommand()
    LogMessage "   📝 发送BPLOT命令..."

    // 查找AutoCAD窗口并激活
    Dim acad_hwnd
    acad_hwnd = Plugin.Window.Find(0, "AutoCAD")

    If acad_hwnd > 0 Then
        LogMessage "   激活AutoCAD窗口..."
        Call Plugin.Window.Active(acad_hwnd)
        Delay 500

        // 点击命令行区域获得焦点（通常在窗口底部）
        Dim rect
        rect = Plugin.Window.GetClientRect(acad_hwnd)
        If rect <> "" Then
            Dim coords, left, top, right, bottom
            coords = Split(rect, ",")
            left = CInt(coords(0))
            top = CInt(coords(1))
            right = CInt(coords(2))
            bottom = CInt(coords(3))

            // 点击命令行区域（窗口底部中间位置）
            Dim cmd_x, cmd_y
            cmd_x = (left + right) / 2
            cmd_y = bottom - 30  // 距离底部30像素

            LogMessage "   点击命令行区域: (" & cmd_x & "," & cmd_y & ")"
            MoveTo cmd_x, cmd_y
            Delay 200
            LeftClick 1
            Delay 500
        End If
    End If

    // 按ESC清除当前状态
    LogMessage "   按ESC清除当前状态..."
    KeyPress "Esc", 2
    Delay 500

    // 输入bplot命令
    LogMessage "   输入命令: _.bplot"
    SayString "_.bplot"
    Delay 1500

    // 回车执行
    LogMessage "   按回车执行命令..."
    KeyPress "Enter", 1
    Delay 500

    LogMessage "   ✅ BPLOT命令已发送"
    LogMessage "   等待对话框打开..."
    Delay 5000  // 等待对话框出现
End Sub

//==============================================================================
// 对话框操作
//==============================================================================

// 列出所有可见窗口（调试用）
Sub ListAllWindows()
    LogMessage "   📋 当前所有可见窗口："

    // 按键精灵没有直接枚举窗口的API，我们使用一些常见窗口类来查找
    Dim test_titles(20)
    test_titles(0) = "批量打印"
    test_titles(1) = "Batch Plot"
    test_titles(2) = "发布"
    test_titles(3) = "AutoCAD"
    test_titles(4) = "打印"
    test_titles(5) = "Plot"
    test_titles(6) = "Publish"
    test_titles(7) = "批量"
    test_titles(8) = "对话框"
    test_titles(9) = "Dialog"
    test_titles(10) = "设置"
    test_titles(11) = "Setup"
    test_titles(12) = "图纸"
    test_titles(13) = "Sheet"
    test_titles(14) = "选择"
    test_titles(15) = "Select"
    test_titles(16) = ""  // 空字符串尝试找任意窗口
    test_titles(17) = "V3"
    test_titles(18) = "批量打印 V3"
    test_titles(19) = "PCX"
    test_titles(20) = "主体"

    Dim i, hwnd, found_count
    found_count = 0

    For i = 0 To UBound(test_titles)
        hwnd = Plugin.Window.Find(0, test_titles(i))
        If hwnd > 0 Then
            found_count = found_count + 1
            LogMessage "      [" & found_count & "] 句柄:" & hwnd & " 关键字:'" & test_titles(i) & "'"
        End If
    Next

    If found_count = 0 Then
        LogMessage "      (未找到任何窗口)"
    Else
        LogMessage "      共找到 " & found_count & " 个窗口"
    End If
End Sub

// 等待批量打印对话框
Function WaitForDialog()
    Dim hwnd, elapsed_time, i
    hwnd = 0
    elapsed_time = 0

    LogMessage "⏳ 正在查找批量打印对话框..."
    LogMessage "   将尝试以下对话框标题："
    For i = 0 To UBound(DialogTitles)
        LogMessage "     - '" & DialogTitles(i) & "'"
    Next

    // 先列出所有窗口（仅在第一次查找时）
    LogMessage ""
    Call ListAllWindows()
    LogMessage ""

    Do While elapsed_time < MAX_WAIT_DIALOG
        For i = 0 To UBound(DialogTitles)
            hwnd = Plugin.Window.Find(0, DialogTitles(i))

            If hwnd > 0 Then
                LogMessage "   ✅ 找到对话框: " & DialogTitles(i) & " (句柄:" & hwnd & ")"
                Call PrintWindowInfo(hwnd, "      ")
                WaitForDialog = hwnd
                Exit Function
            End If
        Next

        // 也尝试查找AutoCAD子窗口
        Dim parent_hwnd
        parent_hwnd = Plugin.Window.Find(0, "AutoCAD")
        If parent_hwnd > 0 Then
            For i = 0 To UBound(DialogTitles)
                Dim child_hwnd
                child_hwnd = Plugin.Window.FindEx(parent_hwnd, 0, "", DialogTitles(i))
                If child_hwnd > 0 Then
                    LogMessage "   ✅ 找到子对话框: " & DialogTitles(i) & " (句柄:" & child_hwnd & ")"
                    Call PrintWindowInfo(child_hwnd, "      ")
                    WaitForDialog = child_hwnd
                    Exit Function
                End If
            Next
        End If

        Delay CHECK_INTERVAL
        elapsed_time = elapsed_time + CHECK_INTERVAL

        If elapsed_time Mod 3000 = 0 Then
            LogMessage "   等待中... (" & (elapsed_time / 1000) & "秒/" & (MAX_WAIT_DIALOG / 1000) & "秒)"
        End If
    Loop

    // 超时后再次列出所有窗口
    LogMessage ""
    LogMessage "   ⚠️  超时！再次检查所有窗口："
    Call ListAllWindows()

    WaitForDialog = 0
End Function

// 激活窗口
Sub ActivateWindow(hwnd)
    Call Plugin.Window.Active(hwnd)
    Delay 200
End Sub

// 点击"选择批量打印图纸"按钮
Function ClickSelectButton(dialog_hwnd)
    LogMessage "🔍 查找选择按钮..."

    // 方法1: 通过控件查找（最可靠）
    Dim btn_hwnd, i

    // 尝试查找按钮控件
    For i = 0 To UBound(ButtonTexts)
        LogMessage "   尝试查找按钮: " & ButtonTexts(i)

        // 查找Button类型的控件
        btn_hwnd = Plugin.Window.FindControl(dialog_hwnd, "Button", ButtonTexts(i))

        If btn_hwnd > 0 Then
            LogMessage "   ✅ 找到按钮控件: " & ButtonTexts(i) & " (句柄:" & btn_hwnd & ")"

            // 方法A: 发送点击命令 (BM_CLICK = 0x00F5)
            Plugin.Window.SendCommand btn_hwnd, &H00F5

            LogMessage "   ✅ 已点击按钮"
            ClickSelectButton = True
            Exit Function
        End If
    Next

    // 方法2: 如果上面失败，尝试查找StaticText或其他控件类型
    LogMessage "   尝试查找其他类型控件..."
    Dim control_types(2)
    control_types(0) = "Static"
    control_types(1) = "WindowsForms10.BUTTON"
    control_types(2) = ""  // 空字符串匹配所有类型

    Dim j
    For i = 0 To UBound(ButtonTexts)
        For j = 0 To UBound(control_types)
            btn_hwnd = Plugin.Window.FindControl(dialog_hwnd, control_types(j), ButtonTexts(i))
            If btn_hwnd > 0 Then
                LogMessage "   ✅ 找到控件: " & ButtonTexts(i) & " 类型:" & control_types(j)
                Plugin.Window.SendCommand btn_hwnd, &H00F5
                ClickSelectButton = True
                Exit Function
            End If
        Next
    Next

    LogMessage "   ⚠️  未找到按钮控件，使用备用方案..."
    ClickSelectButton = False
End Function

// 通过固定位置点击（备用方案）
Sub ClickByPosition(dialog_hwnd)
    LogMessage "📍 使用固定位置点击..."

    // 优先使用手动配置的坐标
    If MANUAL_BUTTON_X > 0 And MANUAL_BUTTON_Y > 0 Then
        LogMessage "   使用手动配置的坐标: (" & MANUAL_BUTTON_X & "," & MANUAL_BUTTON_Y & ")"
        MoveTo MANUAL_BUTTON_X, MANUAL_BUTTON_Y
        Delay 300
        LeftClick 1
        LogMessage "   ✅ 已点击手动坐标"
        Exit Sub
    End If

    // 如果没有手动配置，尝试自动获取窗口位置
    Dim rect
    rect = Plugin.Window.GetWindowRect(dialog_hwnd)

    LogMessage "   窗口坐标原始值: " & rect

    // 检查返回值是否有效
    If rect <> "" And rect <> "0|0|0|0" Then
        // 解析坐标字符串
        Dim parts, left, top, right, bottom, width, height
        parts = Split(rect, "|")

        If UBound(parts) >= 3 Then
            left = CLng(parts(0))
            top = CLng(parts(1))
            right = CLng(parts(2))
            bottom = CLng(parts(3))

            // 再次验证坐标有效性
            If left > 0 Or top > 0 Or right > 0 Or bottom > 0 Then
                width = right - left
                height = bottom - top

                // 计算按钮位置（通常在左侧30%，垂直45%位置）
                Dim click_x, click_y
                click_x = left + width * 0.3
                click_y = top + height * 0.45

                LogMessage "   对话框尺寸: " & width & "x" & height
                LogMessage "   点击坐标: (" & click_x & "," & click_y & ")"

                MoveTo click_x, click_y
                Delay 300
                LeftClick 1

                LogMessage "   ✅ 已点击自动坐标"
                Exit Sub
            End If
        End If
    End If

    // 所有方法都失败
    LogMessage "   ❌ 无法获取有效坐标"
    LogMessage "   ⚠️  请手动配置按钮坐标："
    LogMessage "      1. 打开批量打印对话框"
    LogMessage "      2. 将鼠标移到按钮上"
    LogMessage "      3. 按键精灵查看坐标"
    LogMessage "      4. 修改脚本中的 MANUAL_BUTTON_X 和 MANUAL_BUTTON_Y"
End Sub

// 输入all并回车
Sub InputAll()
    LogMessage "⌨️  输入文本: all"

    // 清除可能的现有输入
    KeyPress "Esc", 1
    Delay 200

    // 输入all
    SayString "all"
    Delay 800

    // 回车确认
    LogMessage "⏎  按回车确认"
    KeyPress "Enter", 1
    Delay 300
    KeyPress "Enter", 1  // 可能需要两次回车

    LogMessage "   ✅ 输入完成"
End Sub

// 可选：自动点击打印按钮
Sub ClickPrintButton(dialog_hwnd)
    LogMessage ""
    LogMessage "[可选] 自动点击打印按钮..."

    // 等待用户确认
    Dim user_confirm
    user_confirm = MsgBox("是否自动点击'打印'按钮？" & vbCrLf & vbCrLf & "点击'是'将开始打印", vbYesNo + vbQuestion, "确认打印")

    If user_confirm = vbYes Then
        Call ActivateWindow(dialog_hwnd)
        Delay 500

        // 通常打印按钮在右下角
        Dim rect
        rect = Plugin.Window.GetClientRect(dialog_hwnd)

        If Not IsEmpty(rect) And rect <> "" Then
            Dim coords
            coords = Split(rect, ",")
            Dim right, bottom
            right = CInt(coords(2))
            bottom = CInt(coords(3))

            // 打印按钮通常在右下角往左约100像素，往上约50像素
            Dim print_x, print_y
            print_x = right - 100
            print_y = bottom - 50

            LogMessage "   点击打印按钮: (" & print_x & "," & print_y & ")"
            MoveTo print_x, print_y
            Delay 300
            LeftClick 1

            LogMessage "   ✅ 已点击打印按钮"
        End If
    Else
        LogMessage "   ⏭️  跳过自动打印"
    End If
End Sub

//==============================================================================
// 工具函数
//==============================================================================

// 检查命令行参数
Sub CheckCommandLineArgs()
    // 按键精灵可以通过命令行传递参数
    // 格式: QMApp.exe script.Q "参数1" "参数2"

    // 如果传入了DWG路径参数，使用它
    If CommandLine <> "" Then
        DWGFilePath = CommandLine
        LogMessage "使用命令行参数: " & DWGFilePath
    End If
End Sub

// 打印横幅
Sub PrintBanner()
    LogMessage "========================================="
    LogMessage "AutoCAD 批量打印全自动化脚本 v2.0"
    LogMessage "========================================="
    LogMessage ""
    LogMessage "配置信息:"
    LogMessage "  AutoCAD: " & AutoCADExePath
    LogMessage "  DWG文件: " & DWGFilePath
    LogMessage ""
    LogMessage "========================================="
End Sub

// 显示错误信息
Sub ShowError(msg)
    MsgBox msg, vbCritical, "AutoCAD自动化错误"
End Sub

// 增强的日志输出
Sub LogMessage(msg)
    Dim timestamp
    timestamp = Year(Now()) & "-" & _
                Right("0" & Month(Now()), 2) & "-" & _
                Right("0" & Day(Now()), 2) & " " & _
                Right("0" & Hour(Now()), 2) & ":" & _
                Right("0" & Minute(Now()), 2) & ":" & _
                Right("0" & Second(Now()), 2)

    TracePrint timestamp & " | " & msg
End Sub
