@echo off
REM ============================================================================
REM AutoCAD 批量打印 - Windows批处理脚本
REM
REM 功能：批量调用按键精灵脚本处理多个DWG文件
REM 作者：CAD Auto Processor Team
REM 日期：2025-11-03
REM ============================================================================

chcp 65001 >nul
echo.
echo ========================================
echo AutoCAD 批量打印自动化工具
echo ========================================
echo.

REM ----------------------------------------------------------------------------
REM 配置区域 - 请根据实际情况修改
REM ----------------------------------------------------------------------------

REM 按键精灵程序路径
set "QM_EXE=C:\Program Files\QuickMacro\QMApp.exe"

REM 按键精灵脚本路径
set "QM_SCRIPT=%~dp0autocad_batch_print_full.Q"

REM DWG文件所在目录
set "DWG_DIR=F:\cad\caddd"

REM 每个文件处理后的等待时间（秒）
set "WAIT_TIME=120"

REM 日志文件
set "LOG_FILE=%~dp0batch_print.log"

REM ----------------------------------------------------------------------------
REM 环境检查
REM ----------------------------------------------------------------------------

echo [1] 检查环境...

REM 检查按键精灵是否存在
if not exist "%QM_EXE%" (
    echo ❌ 错误：未找到按键精灵程序
    echo    路径：%QM_EXE%
    echo    请修改脚本中的 QM_EXE 变量
    pause
    exit /b 1
)
echo    ✅ 按键精灵：%QM_EXE%

REM 检查脚本是否存在
if not exist "%QM_SCRIPT%" (
    echo ❌ 错误：未找到按键精灵脚本
    echo    路径：%QM_SCRIPT%
    pause
    exit /b 1
)
echo    ✅ 脚本文件：%QM_SCRIPT%

REM 检查DWG目录是否存在
if not exist "%DWG_DIR%" (
    echo ❌ 错误：DWG目录不存在
    echo    路径：%DWG_DIR%
    echo    请修改脚本中的 DWG_DIR 变量
    pause
    exit /b 1
)
echo    ✅ DWG目录：%DWG_DIR%
echo.

REM ----------------------------------------------------------------------------
REM 统计DWG文件
REM ----------------------------------------------------------------------------

echo [2] 扫描DWG文件...

set "FILE_COUNT=0"
for %%f in ("%DWG_DIR%\*.dwg") do (
    set /a FILE_COUNT+=1
)

if %FILE_COUNT%==0 (
    echo ❌ 错误：目录中没有DWG文件
    echo    路径：%DWG_DIR%
    pause
    exit /b 1
)

echo    ✅ 找到 %FILE_COUNT% 个DWG文件
echo.

REM ----------------------------------------------------------------------------
REM 用户确认
REM ----------------------------------------------------------------------------

echo [3] 确认操作...
echo.
echo    即将批量处理以下文件：
echo    ----------------------------------------
dir /b "%DWG_DIR%\*.dwg"
echo    ----------------------------------------
echo    共 %FILE_COUNT% 个文件
echo    每个文件预计用时：%WAIT_TIME% 秒
echo.
set /p "CONFIRM=确认开始处理吗？(Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo ⏭️  操作已取消
    pause
    exit /b 0
)

REM ----------------------------------------------------------------------------
REM 开始批量处理
REM ----------------------------------------------------------------------------

echo.
echo [4] 开始批量处理...
echo.

REM 清空或创建日志文件
echo ======================================== > "%LOG_FILE%"
echo AutoCAD批量打印日志 >> "%LOG_FILE%"
echo 开始时间：%date% %time% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

set "PROCESSED=0"
set "FAILED=0"

for %%f in ("%DWG_DIR%\*.dwg") do (
    set /a PROCESSED+=1

    echo ========================================
    echo [!PROCESSED!/%FILE_COUNT%] 正在处理：%%~nxf
    echo ========================================

    REM 记录到日志
    echo [!PROCESSED!/%FILE_COUNT%] %%~nxf >> "%LOG_FILE%"
    echo    开始时间：%time% >> "%LOG_FILE%"

    REM 调用按键精灵脚本
    echo    启动按键精灵...
    start /wait "" "%QM_EXE%" "%QM_SCRIPT%" "%%f"

    REM 检查返回值
    if errorlevel 1 (
        echo    ❌ 处理失败
        echo    状态：失败 >> "%LOG_FILE%"
        set /a FAILED+=1
    ) else (
        echo    ✅ 处理完成
        echo    状态：成功 >> "%LOG_FILE%"
    )

    echo    结束时间：%time% >> "%LOG_FILE%"
    echo. >> "%LOG_FILE%"

    REM 等待后处理下一个
    if !PROCESSED! LSS %FILE_COUNT% (
        echo.
        echo    ⏳ 等待 %WAIT_TIME% 秒后处理下一个文件...
        timeout /t %WAIT_TIME% /nobreak >nul
        echo.
    )
)

REM ----------------------------------------------------------------------------
REM 完成总结
REM ----------------------------------------------------------------------------

echo.
echo ========================================
echo 批量处理完成！
echo ========================================
echo.
echo 📊 处理统计：
echo    总文件数：%FILE_COUNT%
echo    成功数：%PROCESSED%
echo    失败数：%FAILED%
echo.
echo 📁 日志文件：%LOG_FILE%
echo.

REM 记录完成信息到日志
echo ======================================== >> "%LOG_FILE%"
echo 批量处理完成 >> "%LOG_FILE%"
echo 结束时间：%date% %time% >> "%LOG_FILE%"
echo 总文件数：%FILE_COUNT% >> "%LOG_FILE%"
echo 成功数：%PROCESSED% >> "%LOG_FILE%"
echo 失败数：%FAILED% >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

REM 打开日志文件
set /p "OPEN_LOG=是否打开日志文件？(Y/N): "
if /i "%OPEN_LOG%"=="Y" (
    start notepad "%LOG_FILE%"
)

pause
exit /b 0
