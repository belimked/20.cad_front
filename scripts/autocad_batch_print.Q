//==============================================================================
// AutoCAD 批量打印自动化脚本 (按键精灵版)
//
// 功能：接管 Python 工作流的步骤 4-6
//   步骤4: OCR识别并点击"选择批量打印图纸"按钮
//   步骤5: 输入 all 并回车
//   步骤6: 等待打印完成
//
// 作者: CAD Auto Processor Team
// 日期: 2025-11-03
// 版本: 1.0
//==============================================================================

//==============================================================================
// 配置区域 - 可根据实际情况调整
//==============================================================================

// AutoCAD 窗口标题关键字（支持多个版本）
Dim AutoCADTitles(4)
AutoCADTitles(0) = "AutoCAD 2014"
AutoCADTitles(1) = "AutoCAD 2021"
AutoCADTitles(2) = "AutoCAD"
AutoCADTitles(3) = "acad"

// 批量打印对话框标题关键字
Dim DialogTitles(3)
DialogTitles(0) = "批量打印"
DialogTitles(1) = "Batch Plot"
DialogTitles(2) = "发布"

// 等待超时设置（毫秒）
Const MAX_WAIT_AUTOCAD = 60000      // 等待AutoCAD窗口最大时间 60秒
Const MAX_WAIT_DIALOG = 30000       // 等待对话框最大时间 30秒
Const CHECK_INTERVAL = 500          // 检测间隔 500毫秒

// 按钮识别区域（屏幕百分比）
Const BUTTON_AREA_TOP = 0.3         // 按钮搜索区域上边界（屏幕30%处）
Const BUTTON_AREA_BOTTOM = 0.8      // 按钮搜索区域下边界（屏幕80%处）

//==============================================================================
// 主流程
//==============================================================================

Call Main()

Sub Main()
    TracePrint "========================================="
    TracePrint "AutoCAD 批量打印自动化脚本 v1.0"
    TracePrint "========================================="
    TracePrint ""

    // 步骤1: 等待AutoCAD窗口准备就绪
    TracePrint "[步骤1] 等待AutoCAD窗口..."
    Dim acad_hwnd
    acad_hwnd = WaitForAutoCAD()

    If acad_hwnd = 0 Then
        TracePrint "❌ 错误: 未找到AutoCAD窗口，脚本退出"
        ExitScript
    End If

    TracePrint "✅ AutoCAD窗口已就绪: " & acad_hwnd
    Delay 1000

    // 步骤2: 等待批量打印对话框出现
    TracePrint ""
    TracePrint "[步骤2] 等待批量打印对话框..."
    Dim dialog_hwnd
    dialog_hwnd = WaitForDialog()

    If dialog_hwnd = 0 Then
        TracePrint "❌ 错误: 未找到批量打印对话框"
        ExitScript
    End If

    TracePrint "✅ 批量打印对话框已打开: " & dialog_hwnd
    Delay 1000

    // 步骤3: 激活对话框窗口
    TracePrint ""
    TracePrint "[步骤3] 激活对话框窗口..."
    Call ActivateWindow(dialog_hwnd)
    Delay 500

    // 步骤4: 点击"选择批量打印图纸"按钮
    TracePrint ""
    TracePrint "[步骤4] 查找并点击按钮..."
    Dim button_clicked
    button_clicked = ClickSelectButton(dialog_hwnd)

    If Not button_clicked Then
        TracePrint "⚠️  警告: 未能通过OCR找到按钮，尝试使用坐标点击"
        Call ClickByPosition(dialog_hwnd)
    End If

    Delay 1500

    // 步骤5: 输入 all 并回车
    TracePrint ""
    TracePrint "[步骤5] 输入 all 并回车..."
    Call InputAll()
    Delay 2000

    // 步骤6: 等待用户确认或执行打印
    TracePrint ""
    TracePrint "[步骤6] 等待打印完成..."
    TracePrint "💡 提示: 请手动检查图纸选择，确认无误后点击打印按钮"
    TracePrint ""
    TracePrint "========================================="
    TracePrint "✅ 脚本执行完成！"
    TracePrint "========================================="
End Sub

//==============================================================================
// 窗口检测函数
//==============================================================================

// 等待AutoCAD窗口准备就绪（方案B - 窗口检测法）
Function WaitForAutoCAD()
    Dim hwnd, elapsed_time, i
    hwnd = 0
    elapsed_time = 0

    TracePrint "⏳ 正在查找AutoCAD窗口..."

    Do While elapsed_time < MAX_WAIT_AUTOCAD
        // 遍历所有AutoCAD标题关键字
        For i = 0 To UBound(AutoCADTitles)
            hwnd = Plugin.Window.Find(0, AutoCADTitles(i))
            If hwnd > 0 Then
                // 验证窗口可见性
                If Plugin.Window.IsVisible(hwnd) Then
                    TracePrint "   找到窗口: " & AutoCADTitles(i) & " (句柄:" & hwnd & ")"
                    WaitForAutoCAD = hwnd
                    Exit Function
                End If
            End If
        Next

        // 等待并更新进度
        Delay CHECK_INTERVAL
        elapsed_time = elapsed_time + CHECK_INTERVAL

        // 每5秒输出一次进度
        If elapsed_time Mod 5000 = 0 Then
            TracePrint "   等待中... (" & (elapsed_time / 1000) & "秒/" & (MAX_WAIT_AUTOCAD / 1000) & "秒)"
        End If
    Loop

    WaitForAutoCAD = 0
End Function

// 等待批量打印对话框出现
Function WaitForDialog()
    Dim hwnd, elapsed_time, i
    hwnd = 0
    elapsed_time = 0

    TracePrint "⏳ 正在查找批量打印对话框..."

    Do While elapsed_time < MAX_WAIT_DIALOG
        // 遍历所有对话框标题关键字
        For i = 0 To UBound(DialogTitles)
            hwnd = Plugin.Window.Find(0, DialogTitles(i))
            If hwnd > 0 Then
                // 验证窗口可见性
                If Plugin.Window.IsVisible(hwnd) Then
                    TracePrint "   找到对话框: " & DialogTitles(i) & " (句柄:" & hwnd & ")"
                    WaitForDialog = hwnd
                    Exit Function
                End If
            End If
        Next

        // 也尝试查找子窗口
        Dim parent_hwnd, child_hwnd
        parent_hwnd = Plugin.Window.Find(0, "AutoCAD")
        If parent_hwnd > 0 Then
            For i = 0 To UBound(DialogTitles)
                child_hwnd = Plugin.Window.FindEx(parent_hwnd, 0, "", DialogTitles(i))
                If child_hwnd > 0 Then
                    TracePrint "   找到子对话框: " & DialogTitles(i) & " (句柄:" & child_hwnd & ")"
                    WaitForDialog = child_hwnd
                    Exit Function
                End If
            Next
        End If

        // 等待并更新进度
        Delay CHECK_INTERVAL
        elapsed_time = elapsed_time + CHECK_INTERVAL

        If elapsed_time Mod 3000 = 0 Then
            TracePrint "   等待中... (" & (elapsed_time / 1000) & "秒/" & (MAX_WAIT_DIALOG / 1000) & "秒)"
        End If
    Loop

    WaitForDialog = 0
End Function

// 激活窗口
Sub ActivateWindow(hwnd)
    Call Plugin.Window.Active(hwnd)
    TracePrint "   窗口已激活: " & hwnd
End Sub

//==============================================================================
// 界面操作函数
//==============================================================================

// 点击"选择批量打印图纸"按钮（通过颜色/图像识别）
Function ClickSelectButton(dialog_hwnd)
    TracePrint "🔍 搜索按钮..."

    // 激活对话框
    Call ActivateWindow(dialog_hwnd)
    Delay 300

    // 方法1: 尝试使用字库识别（如果已配置）
    Dim x, y, result
    result = 0

    // 获取对话框位置和尺寸
    Dim rect, left, top, right, bottom
    rect = Plugin.Window.GetClientRect(dialog_hwnd)
    If IsEmpty(rect) Or rect = "" Then
        TracePrint "   ⚠️  无法获取窗口位置"
        ClickSelectButton = False
        Exit Function
    End If

    // 解析坐标 (格式: "left,top,right,bottom")
    Dim coords
    coords = Split(rect, ",")
    left = CInt(coords(0))
    top = CInt(coords(1))
    right = CInt(coords(2))
    bottom = CInt(coords(3))

    TracePrint "   对话框区域: (" & left & "," & top & ") - (" & right & "," & bottom & ")"

    // 方法2: 使用图像识别（需要预先截取按钮图片）
    // 尝试查找按钮图片（如果存在）
    Dim pic_path
    pic_path = "C:\AutoCAD_Automation\button_select_sheets.bmp"

    Dim intX, intY
    intX = -1
    intY = -1

    // 查找图片
    Dim find_result
    find_result = Plugin.Pic.FindPic(left, top, right, bottom, pic_path, "000000", 0.9, 0, intX, intY)

    If find_result = 0 Then
        TracePrint "   ✅ 找到按钮图片: (" & intX & "," & intY & ")"
        MoveTo intX, intY
        Delay 200
        LeftClick 1
        ClickSelectButton = True
        Exit Function
    Else
        TracePrint "   ⚠️  未找到按钮图片（文件可能不存在）"
    End If

    // 方法3: 如果上述方法都失败，返回False让调用者使用备用方案
    ClickSelectButton = False
End Function

// 通过固定位置点击（备用方案）
Sub ClickByPosition(dialog_hwnd)
    TracePrint "📍 使用固定位置点击按钮..."

    // 获取对话框尺寸
    Dim rect, coords, left, top, right, bottom
    rect = Plugin.Window.GetClientRect(dialog_hwnd)
    coords = Split(rect, ",")
    left = CInt(coords(0))
    top = CInt(coords(1))
    right = CInt(coords(2))
    bottom = CInt(coords(3))

    // 假设按钮在对话框中间偏左位置
    // 这个位置需要根据实际AutoCAD版本调整
    Dim click_x, click_y
    click_x = left + (right - left) * 0.3   // 左侧30%位置
    click_y = top + (bottom - top) * 0.5    // 垂直中间位置

    TracePrint "   点击位置: (" & click_x & "," & click_y & ")"

    MoveTo click_x, click_y
    Delay 200
    LeftClick 1
End Sub

// 输入 all 并回车
Sub InputAll()
    TracePrint "⌨️  输入: all"

    // 方法1: 直接发送文本
    SayString "all"
    Delay 500

    // 方法2: 逐个字符输入（更稳定）
    // KeyPress "A", 1
    // Delay 100
    // KeyPress "L", 1
    // Delay 100
    // KeyPress "L", 1
    // Delay 500

    TracePrint "⏎  按下回车"
    KeyPress "Enter", 1
    Delay 200
    KeyPress "Enter", 1  // 可能需要回车两次

    TracePrint "   ✅ 输入完成"
End Sub

//==============================================================================
// 工具函数
//==============================================================================

// 增强的日志输出
Sub TracePrint(msg)
    Dim timestamp
    timestamp = Year(Now()) & "-" & Right("0" & Month(Now()), 2) & "-" & Right("0" & Day(Now()), 2) & " " & _
                Right("0" & Hour(Now()), 2) & ":" & Right("0" & Minute(Now()), 2) & ":" & Right("0" & Second(Now()), 2)
    TracePrint timestamp & " | " & msg
End Sub
