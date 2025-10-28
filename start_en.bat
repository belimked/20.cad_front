@echo off
setlocal enabledelayedexpansion
REM ========================================
REM  AutoCAD Automation System - Launcher
REM ========================================

title AutoCAD Automation System

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Auto-run database migrations
echo [INFO] Checking database migrations...
python scripts\auto_migrate.py --silent
if errorlevel 1 (
    echo [WARNING] Migration check encountered issues, but continuing...
)
echo.

:MENU
cls
echo ========================================
echo  AutoCAD Automation System
echo ========================================
echo.
echo Select an option:
echo.
echo  [1] List configurations
echo  [2] Show configuration details
echo  [3] Activate configuration
echo  [4] Update configuration
echo  [5] Initialize database
echo  [6] Run workflow (default)
echo  [7] Run workflow (stable)
echo  [8] Test configuration
echo  [9] Show help
echo  [0] Exit
echo.
echo ========================================

set /p choice="Enter option (0-9): "

REM Exit
if "%choice%"=="0" (
    echo.
    echo Goodbye!
    timeout /t 1 > nul
    exit
)

REM List configurations
if "%choice%"=="1" (
    cls
    echo [Running] List configurations
    echo ========================================
    python scripts\autocad_config_manager.py list
    echo.
    pause
    goto MENU
)

REM Show configuration details
if "%choice%"=="2" (
    cls
    echo [Running] Show configuration details
    echo ========================================
    set /p config_id="Enter configuration ID: "
    python scripts\autocad_config_manager.py show %config_id%
    echo.
    pause
    goto MENU
)

REM Activate configuration
if "%choice%"=="3" (
    cls
    echo [Running] Activate configuration
    echo ========================================
    echo Current configurations:
    python scripts\autocad_config_manager.py list
    echo.
    set /p config_id="Enter configuration ID to activate: "
    python scripts\autocad_config_manager.py activate %config_id%
    echo.
    pause
    goto MENU
)

REM Update configuration
if "%choice%"=="4" (
    cls
    echo [Running] Update configuration
    echo ========================================
    echo Current configurations:
    python scripts\autocad_config_manager.py list
    echo.
    set /p config_id="Enter configuration ID: "
    echo.
    echo Available parameters:
    echo   --startup-wait [seconds]
    echo   --verification-wait [seconds]
    echo   --retry-count [count]
    echo   --description [text]
    echo   --dwg-file [path]
    echo   --autocad-path [path]
    echo   --autocad-version [version]
    echo.
    echo Example: --startup-wait 15.0 --dwg-file "F:\cad\test.dwg"
    set /p params="Enter parameters: "
    python scripts\autocad_config_manager.py update %config_id% %params%
    echo.
    pause
    goto MENU
)

REM Initialize database
if "%choice%"=="5" (
    cls
    echo [Running] Initialize database
    echo ========================================
    echo [WARNING] This will create new configuration tables
    echo.
    set /p confirm="Continue? (Y/N): "
    if /i "%confirm%"=="Y" (
        python scripts\init_autocad_config.py
    ) else (
        echo Cancelled
    )
    echo.
    pause
    goto MENU
)

REM Run workflow (default)
if "%choice%"=="6" (
    cls
    echo [Running] Workflow (default configuration)
    echo ========================================

    REM Query default DWG path
    echo [INFO] Querying configuration...
    for /f "usebackq delims=" %%i in (`python -c "import sys; import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.path.insert(0, '.'); from src.utils.database import SessionLocal; from src.services.autocad_config_service import AutoCADConfigService; db = SessionLocal(); service = AutoCADConfigService(db); config = service.get_config(config_name='default'); print(config.dwg_file_path if config and config.dwg_file_path else ''); db.close()"`) do set default_dwg_file=%%i

    echo.
    if defined default_dwg_file if not "%default_dwg_file%"=="" (
        echo [Default path] %default_dwg_file%
        echo.
        set /p dwg_file="Enter DWG file path (press Enter for default): "
        if "!dwg_file!"=="" set dwg_file=%default_dwg_file%
    ) else (
        echo [Note] No default path configured
        echo.
        set /p dwg_file="Enter DWG file full path: "
    )

    echo.
    echo [INFO] Will use 'default' configuration
    echo File: !dwg_file!
    echo.
    pause
    python research\autocad_com_api\9_configurable_workflow.py
    echo.
    echo [Done] Press any key to return to menu
    pause
    goto MENU
)

REM Run workflow (stable)
if "%choice%"=="7" (
    cls
    echo [Running] Workflow (stable configuration)
    echo ========================================

    REM Query stable DWG path
    echo [INFO] Querying configuration...
    for /f "usebackq delims=" %%i in (`python -c "import sys; import io; sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.path.insert(0, '.'); from src.utils.database import SessionLocal; from src.services.autocad_config_service import AutoCADConfigService; db = SessionLocal(); service = AutoCADConfigService(db); config = service.get_config(config_name='stable'); print(config.dwg_file_path if config and config.dwg_file_path else ''); db.close()"`) do set stable_dwg_file=%%i

    echo.
    if defined stable_dwg_file if not "%stable_dwg_file%"=="" (
        echo [Default path] %stable_dwg_file%
        echo.
        set /p dwg_file="Enter DWG file path (press Enter for default): "
        if "!dwg_file!"=="" set dwg_file=%stable_dwg_file%
    ) else (
        echo [Note] No default path configured
        echo.
        set /p dwg_file="Enter DWG file full path: "
    )

    echo.
    echo [INFO] Will use 'stable' configuration
    echo [Note] Make sure 'stable' configuration is activated (option 3)
    echo File: !dwg_file!
    echo.
    pause
    python research\autocad_com_api\9_configurable_workflow.py
    echo.
    echo [Done] Press any key to return to menu
    pause
    goto MENU
)

REM Test configuration
if "%choice%"=="8" (
    cls
    echo [Running] Test configuration
    echo ========================================
    python scripts\test_autocad_config.py
    echo.
    pause
    goto MENU
)

REM Show help
if "%choice%"=="9" (
    cls
    echo [Help] Documentation
    echo ========================================
    echo.
    echo Detailed documentation:
    echo   - Full guide: docs\DATABASE_CONFIG_GUIDE.md
    echo   - Quick reference: docs\CONFIG_QUICK_REFERENCE.md
    echo   - Deployment guide: docs\TESTING_DEPLOYMENT_GUIDE.md
    echo   - README: docs\DATABASE_CONFIG_README.md
    echo.
    echo Quick commands:
    echo   List configs: python scripts\autocad_config_manager.py list
    echo   Show details: python scripts\autocad_config_manager.py show [ID]
    echo   Activate: python scripts\autocad_config_manager.py activate [ID]
    echo   Update: python scripts\autocad_config_manager.py update [ID] [params]
    echo.
    echo Parameters:
    echo   --startup-wait 15.0
    echo   --verification-wait 45.0
    echo   --retry-count 5
    echo   --description "New description"
    echo   --dwg-file "F:\cad\caddd\xxx.dwg"
    echo   --autocad-path "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"
    echo   --autocad-version 2014
    echo.
    pause
    goto MENU
)

REM Invalid option
echo.
echo [ERROR] Invalid option, please try again
timeout /t 2 > nul
goto MENU
