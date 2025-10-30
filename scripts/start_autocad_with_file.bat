@echo off
REM ============================================================================
REM AutoCAD启动脚本 - 关闭现有AutoCAD并打开指定文件
REM 参数1: AutoCAD可执行文件路径
REM 参数2: DWG文件路径
REM ============================================================================

set ACAD_EXE=%~1
set DWG_FILE=%~2

echo ========================================
echo  AutoCAD自动启动脚本
echo ========================================
echo AutoCAD路径: %ACAD_EXE%
echo 文件路径: %DWG_FILE%
echo.

REM 关闭现有AutoCAD进程
echo 正在关闭现有 AutoCAD 进程...
taskkill /IM acad.exe /F >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] AutoCAD进程已关闭
    timeout /t 2 /nobreak >nul
) else (
    echo [INFO] 没有运行中的AutoCAD进程
)

echo.
echo 正在启动 AutoCAD 并打开文件...
start "" "%ACAD_EXE%" "%DWG_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo [OK] AutoCAD启动命令已执行
    echo.
    echo 提示: AutoCAD正在启动，请等待...
    exit /b 0
) else (
    echo [ERROR] AutoCAD启动失败
    exit /b 1
)
