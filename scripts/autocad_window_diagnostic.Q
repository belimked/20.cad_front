//==============================================================================
// AutoCAD 窗口诊断工具
//
// 功能: 帮助诊断 AutoCAD 启动后窗口查找失败的问题
// 用法:
//   1. 手动启动 AutoCAD 并打开你的 DWG 文件
//   2. 运行本脚本查看所有可能的窗口信息
//   3. 根据输出结果优化主脚本的窗口查找策略
//==============================================================================

Call Main()

Sub Main()
    LogMessage "========================================="
    LogMessage "AutoCAD 窗口诊断工具"
    LogMessage "========================================="
    LogMessage ""

    // 提示用户先打开 AutoCAD
    Dim user_ready
    user_ready = MsgBox("请确保已经手动打开 AutoCAD 并加载了 DWG 文件" & vbCrLf & vbCrLf & _
                        "准备好后点击'是'开始诊断", vbYesNo + vbQuestion, "准备诊断")

    If user_ready <> vbYes Then
        LogMessage "用户取消诊断"
        Exit Sub
    End If

    LogMessage ""
    LogMessage "[诊断1] 查找所有包含 AutoCAD 关键字的窗口"
    LogMessage "========================================="
    Call FindWindowsByKeywords()

    LogMessage ""
    LogMessage "[诊断2] 查找所有 Afx 类窗口（MFC 窗口）"
    LogMessage "========================================="
    Call FindAfxWindows()

    LogMessage ""
    LogMessage "[诊断3] 查找所有包含文件名关键字的窗口"
    LogMessage "========================================="
    Call FindWindowsByFilename()

    LogMessage ""
    LogMessage "[诊断4] 使用进程 ID 查找窗口"
    LogMessage "========================================="
    Call FindWindowsByProcess()

    LogMessage ""
    LogMessage "========================================="
    LogMessage "✅ 诊断完成"
    LogMessage "========================================="
    LogMessage ""
    LogMessage "💡 请根据上述诊断结果:"
    LogMessage "   1. 确认 AutoCAD 窗口的实际标题"
    LogMessage "   2. 确认窗口类名"
    LogMessage "   3. 更新主脚本中的查找策略"

    MsgBox "诊断完成，请查看日志输出！", vbInformation, "完成"
End Sub

//==============================================================================
// 诊断函数
//==============================================================================

// 诊断1: 按关键字查找
Sub FindWindowsByKeywords()
    Dim keywords(15)
    keywords(0) = "AutoCAD"
    keywords(1) = "acad"
    keywords(2) = "Autodesk"
    keywords(3) = "2014"
    keywords(4) = "2021"
    keywords(5) = ".dwg"
    keywords(6) = "DWG"
    keywords(7) = "图形"
    keywords(8) = "drawing"
    keywords(9) = "CAD"
    keywords(10) = "PCX"
    keywords(11) = "主体"
    keywords(12) = "钢结构"
    keywords(13) = "20230301"
    keywords(14) = "Afx"
    keywords(15) = ""  // 空字符串匹配任意窗口

    Dim i, hwnd, found_count
    found_count = 0

    For i = 0 To UBound(keywords)
        hwnd = Plugin.Window.Find(0, keywords(i))
        If hwnd > 0 Then
            found_count = found_count + 1
            LogMessage ""
            LogMessage "找到窗口 #" & found_count
            LogMessage "  查找关键字: '" & keywords(i) & "'"
            Call PrintDetailedWindowInfo(hwnd)
        End If
    Next i

    If found_count = 0 Then
        LogMessage "  ❌ 未找到任何窗口"
    Else
        LogMessage ""
        LogMessage "共找到 " & found_count & " 个窗口"
    End If
End Sub

// 诊断2: 查找 MFC 窗口
Sub FindAfxWindows()
    Dim afx_classes(10)
    afx_classes(0) = "AfxFrameOrView80"     // AutoCAD 2014
    afx_classes(1) = "AfxFrameOrView90"     // AutoCAD 2016
    afx_classes(2) = "AfxFrameOrView100"    // AutoCAD 2018
    afx_classes(3) = "AfxFrameOrView140"    // AutoCAD 2021
    afx_classes(4) = "AfxFrameOrView"       // 通用
    afx_classes(5) = "AcApplicationFrame"   // AutoCAD 应用框架
    afx_classes(6) = "AfxWnd"
    afx_classes(7) = "AfxWnd80"
    afx_classes(8) = "AfxWnd90"
    afx_classes(9) = "AfxWnd140"
    afx_classes(10) = "AfxControlBar"

    Dim i, hwnd, found_count
    found_count = 0

    For i = 0 To UBound(afx_classes)
        hwnd = Plugin.Window.FindEx(0, 0, afx_classes(i), "")
        If hwnd > 0 Then
            found_count = found_count + 1
            LogMessage ""
            LogMessage "找到 MFC 窗口 #" & found_count
            LogMessage "  查找类名: " & afx_classes(i)
            Call PrintDetailedWindowInfo(hwnd)
        End If
    Next i

    If found_count = 0 Then
        LogMessage "  ❌ 未找到任何 MFC 窗口"
    Else
        LogMessage ""
        LogMessage "共找到 " & found_count & " 个 MFC 窗口"
    End If
End Sub

// 诊断3: 按文件名查找
Sub FindWindowsByFilename()
    // 这里需要用户手动修改为实际的文件名
    Dim filenames(5)
    filenames(0) = "PCX20.01 主体钢结构（20230301）.dwg"
    filenames(1) = "PCX20.01 主体钢结构（20230301）"
    filenames(2) = "PCX20.01"
    filenames(3) = "主体钢结构"
    filenames(4) = ".dwg"
    filenames(5) = "20230301"

    Dim i, hwnd, found_count
    found_count = 0

    For i = 0 To UBound(filenames)
        hwnd = Plugin.Window.Find(0, filenames(i))
        If hwnd > 0 Then
            found_count = found_count + 1
            LogMessage ""
            LogMessage "找到窗口 #" & found_count
            LogMessage "  查找文件名片段: '" & filenames(i) & "'"
            Call PrintDetailedWindowInfo(hwnd)
        End If
    Next i

    If found_count = 0 Then
        LogMessage "  ❌ 未找到包含文件名的窗口"
        LogMessage "  💡 提示: 如果文件名包含中文，可能需要调整脚本的编码设置"
    Else
        LogMessage ""
        LogMessage "共找到 " & found_count & " 个窗口"
    End If
End Sub

// 诊断4: 通过进程查找
Sub FindWindowsByProcess()
    LogMessage "  尝试查找 acad.exe 进程..."

    // 方法1: 查找任意 AutoCAD 窗口，然后获取进程信息
    Dim test_keywords(3)
    test_keywords(0) = "AutoCAD"
    test_keywords(1) = "acad"
    test_keywords(2) = ".dwg"
    test_keywords(3) = "Afx"

    Dim i, hwnd
    For i = 0 To UBound(test_keywords)
        hwnd = Plugin.Window.Find(0, test_keywords(i))
        If hwnd > 0 Then
            LogMessage ""
            LogMessage "  找到可能的 AutoCAD 窗口:"
            LogMessage "    查找关键字: " & test_keywords(i)
            Call PrintDetailedWindowInfo(hwnd)

            // 尝试获取进程 ID（某些按键精灵版本支持）
            LogMessage "    💡 建议: 使用任务管理器确认 acad.exe 的进程 ID"
            Exit For
        End If
    Next i

    If hwnd = 0 Then
        LogMessage "  ❌ 未找到任何可能的 AutoCAD 窗口"
        LogMessage "  ⚠️  可能原因:"
        LogMessage "     1. AutoCAD 未启动"
        LogMessage "     2. AutoCAD 以最小化模式启动"
        LogMessage "     3. 存在启动对话框阻止主窗口显示"
        LogMessage "     4. 窗口标题和类名都不匹配预期"
    End If
End Sub

//==============================================================================
// 工具函数
//==============================================================================

// 打印详细的窗口信息
Sub PrintDetailedWindowInfo(hwnd)
    If hwnd <= 0 Then
        LogMessage "    ❌ 无效窗口句柄"
        Exit Sub
    End If

    LogMessage "    句柄: " & hwnd

    // 获取窗口标题（多种方法）
    Dim title
    title = Plugin.Window.GetTitle(hwnd)
    If title <> "" Then
        LogMessage "    标题: " & title
    Else
        LogMessage "    标题: (空)"
    End If

    // 获取窗口类名
    Dim class_name
    class_name = Plugin.Window.GetClass(hwnd)
    If class_name <> "" Then
        LogMessage "    类名: " & class_name
    Else
        LogMessage "    类名: (无法获取)"
    End If

    // 获取窗口位置
    Dim rect
    rect = Plugin.Window.GetWindowRect(hwnd)
    If rect <> "" And rect <> "0|0|0|0" And rect <> "0,0,0,0" Then
        LogMessage "    位置: " & NormalizeRect(rect)

        // 计算窗口尺寸
        Dim parts
        parts = Split(NormalizeRect(rect), ",")
        If UBound(parts) >= 3 Then
            Dim width, height
            width = CLng(parts(2)) - CLng(parts(0))
            height = CLng(parts(3)) - CLng(parts(1))
            LogMessage "    尺寸: " & width & " x " & height
        End If
    Else
        LogMessage "    位置: (无法获取)"
    End If

    // 检查窗口状态
    Dim is_visible
    is_visible = Plugin.Window.IsWindow(hwnd)
    LogMessage "    可见: " & IIf(is_visible, "是", "否")

    // 尝试判断是否为 AutoCAD 窗口
    If InStr(class_name, "Afx") > 0 Then
        LogMessage "    ⭐ 高概率: MFC 应用程序（AutoCAD 使用 MFC）"
    End If

    If InStr(class_name, "AutoCAD") > 0 Or InStr(title, "AutoCAD") > 0 Then
        LogMessage "    ⭐ 高概率: AutoCAD 窗口"
    End If

    If InStr(title, ".dwg") > 0 Then
        LogMessage "    ⭐ 高概率: 已打开 DWG 文件"
    End If
End Sub

// 统一解析 RECT 字符串
Function NormalizeRect(rectStr)
    If rectStr = "" Then
        NormalizeRect = ""
        Exit Function
    End If

    If InStr(rectStr, "|") > 0 Then
        Dim p
        p = Split(rectStr, "|")
        If UBound(p) >= 3 Then
            NormalizeRect = p(0) & "," & p(1) & "," & p(2) & "," & p(3)
        Else
            NormalizeRect = ""
        End If
    Else
        NormalizeRect = rectStr
    End If
End Function

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
