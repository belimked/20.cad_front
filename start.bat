@echo off
setlocal enabledelayedexpansion
REM ========================================
REM  AutoCAD 自动化配置系统 - 启动脚本
REM ========================================

chcp 65001 > nul
title AutoCAD 自动化配置系统

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在！
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

:MENU
cls
echo ========================================
echo  AutoCAD 自动化配置系统
echo ========================================
echo.
echo 请选择操作:
echo.
echo  [1] 查看配置列表
echo  [2] 查看配置详情
echo  [3] 激活配置
echo  [4] 修改配置参数
echo  [5] 初始化配置数据库
echo  [6] 运行工作流程 (default)
echo  [7] 运行工作流程 (stable)
echo  [8] 测试配置系统
echo  [9] 查看帮助文档
echo  [0] 退出
echo.
echo ========================================

set /p choice="请输入选项 (0-9): "

REM 查看配置列表
if "%choice%"=="1" (
    cls
    echo [执行] 查看配置列表
    echo ========================================
    python scripts\autocad_config_manager.py list
    echo.
    pause
    goto MENU
)

REM 查看配置详情
if "%choice%"=="2" (
    cls
    echo [执行] 查看配置详情
    echo ========================================
    set /p config_id="请输入配置 ID: "
    python scripts\autocad_config_manager.py show %config_id%
    echo.
    pause
    goto MENU
)

REM 激活配置
if "%choice%"=="3" (
    cls
    echo [执行] 激活配置
    echo ========================================
    echo 当前配置:
    python scripts\autocad_config_manager.py list
    echo.
    set /p config_id="请输入要激活的配置 ID: "
    python scripts\autocad_config_manager.py activate %config_id%
    echo.
    pause
    goto MENU
)

REM 修改配置参数
if "%choice%"=="4" (
    cls
    echo [执行] 修改配置参数
    echo ========================================
    echo 当前配置:
    python scripts\autocad_config_manager.py list
    echo.
    set /p config_id="请输入配置 ID: "
    echo.
    echo 可修改的参数:
    echo   --startup-wait [秒]       启动等待时间
    echo   --verification-wait [秒]  验证等待时间
    echo   --retry-count [次数]      重试次数
    echo   --description [描述]      配置描述
    echo   --dwg-file [路径]         DWG文件路径
    echo   --autocad-path [路径]     AutoCAD程序路径
    echo   --autocad-version [版本]  AutoCAD版本
    echo.
    echo 示例: --startup-wait 15.0 --dwg-file "F:\cad\test.dwg"
    set /p params="请输入参数: "
    python scripts\autocad_config_manager.py update %config_id% %params%
    echo.
    pause
    goto MENU
)

REM 初始化配置数据库
if "%choice%"=="5" (
    cls
    echo [执行] 初始化配置数据库
    echo ========================================
    echo [警告] 此操作会创建新的配置表
    echo.
    set /p confirm="确认继续? (Y/N): "
    if /i "%confirm%"=="Y" (
        python scripts\init_autocad_config.py
    ) else (
        echo 已取消
    )
    echo.
    pause
    goto MENU
)

REM 运行工作流程 (default)
if "%choice%"=="6" (
    cls
    echo [执行] 运行工作流程 (default 配置)
    echo ========================================

    REM 查询default配置的默认路径
    echo [信息] 正在查询配置...
    for /f "delims=" %%i in ('python -c "import sys; sys.path.insert(0, '.'); from src.utils.database import SessionLocal; from src.services.autocad_config_service import AutoCADConfigService; db = SessionLocal(); service = AutoCADConfigService(db); config = service.get_config(config_name='default'); print(config.dwg_file_path if config and config.dwg_file_path else ''); db.close()"') do set default_dwg_file=%%i

    echo.
    if defined default_dwg_file if not "%default_dwg_file%"=="" (
        echo [默认路径] %default_dwg_file%
        echo.
        set /p dwg_file="请输入 DWG 文件路径（直接回车使用默认路径）: "
        if "!dwg_file!"=="" set dwg_file=%default_dwg_file%
    ) else (
        echo [提示] 配置中未设置默认路径
        echo.
        set /p dwg_file="请输入 DWG 文件完整路径: "
    )

    echo.
    echo [提示] 即将使用 default 配置处理文件
    echo 文件: !dwg_file!
    echo.
    pause
    python research\autocad_com_api\9_configurable_workflow.py
    echo.
    echo [完成] 按任意键返回菜单
    pause
    goto MENU
)

REM 运行工作流程 (stable)
if "%choice%"=="7" (
    cls
    echo [执行] 运行工作流程 (stable 配置)
    echo ========================================

    REM 查询stable配置的默认路径
    echo [信息] 正在查询配置...
    for /f "delims=" %%i in ('python -c "import sys; sys.path.insert(0, '.'); from src.utils.database import SessionLocal; from src.services.autocad_config_service import AutoCADConfigService; db = SessionLocal(); service = AutoCADConfigService(db); config = service.get_config(config_name='stable'); print(config.dwg_file_path if config and config.dwg_file_path else ''); db.close()"') do set stable_dwg_file=%%i

    echo.
    if defined stable_dwg_file if not "%stable_dwg_file%"=="" (
        echo [默认路径] %stable_dwg_file%
        echo.
        set /p dwg_file="请输入 DWG 文件路径（直接回车使用默认路径）: "
        if "!dwg_file!"=="" set dwg_file=%stable_dwg_file%
    ) else (
        echo [提示] 配置中未设置默认路径
        echo.
        set /p dwg_file="请输入 DWG 文件完整路径: "
    )

    echo.
    echo [提示] 即将使用 stable 配置处理文件
    echo [注意] 请确保 stable 配置已激活 (选项 3)
    echo 文件: !dwg_file!
    echo.
    pause
    python research\autocad_com_api\9_configurable_workflow.py
    echo.
    echo [完成] 按任意键返回菜单
    pause
    goto MENU
)

REM 测试配置系统
if "%choice%"=="8" (
    cls
    echo [执行] 测试配置系统
    echo ========================================
    python scripts\test_autocad_config.py
    echo.
    pause
    goto MENU
)

REM 查看帮助文档
if "%choice%"=="9" (
    cls
    echo [帮助] 文档位置
    echo ========================================
    echo.
    echo 详细文档:
    echo   - 完整指南: docs\DATABASE_CONFIG_GUIDE.md
    echo   - 快速参考: docs\CONFIG_QUICK_REFERENCE.md
    echo   - 部署指南: docs\TESTING_DEPLOYMENT_GUIDE.md
    echo   - 项目说明: docs\DATABASE_CONFIG_README.md
    echo.
    echo 快速命令:
    echo   查看配置: python scripts\autocad_config_manager.py list
    echo   查看详情: python scripts\autocad_config_manager.py show [ID]
    echo   激活配置: python scripts\autocad_config_manager.py activate [ID]
    echo   修改配置: python scripts\autocad_config_manager.py update [ID] [参数]
    echo.
    echo 配置参数:
    echo   启动等待: --startup-wait 15.0
    echo   验证等待: --verification-wait 45.0
    echo   重试次数: --retry-count 5
    echo   描述信息: --description "新描述"
    echo   DWG文件: --dwg-file "F:\cad\caddd\xxx.dwg"
    echo   CAD路径: --autocad-path "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"
    echo   CAD版本: --autocad-version 2014
    echo.
    pause
    goto MENU
)

REM 退出
if "%choice%"=="0" (
    echo.
    echo 再见！
    timeout /t 1 > nul
    exit
)

REM 无效选项
echo.
echo [错误] 无效选项，请重新选择
timeout /t 2 > nul
goto MENU
