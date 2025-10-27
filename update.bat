@echo off
REM ========================================
REM  AutoCAD Config System - Update
REM ========================================

title AutoCAD Config System - Update

cls
echo ========================================
echo  AutoCAD Config System - Update
echo ========================================
echo.
echo This script will:
echo   1. Backup current database
echo   2. Pull latest code (Git)
echo   3. Update dependencies
echo   4. Restore database
echo   5. Run tests
echo.
echo ========================================
echo.

pause

REM ========================================
REM Step 1: Backup database
REM ========================================
echo.
echo [Step 1/5] Backing up database...
echo ========================================

if not exist "data" mkdir data
if not exist "backup" mkdir backup

set BACKUP_DIR=backup\backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

echo [INFO] Creating backup dir: %BACKUP_DIR%
mkdir "%BACKUP_DIR%"

if exist "data\*.db" (
    echo [INFO] Backing up database files...
    copy data\*.db "%BACKUP_DIR%\" > nul
    echo [OK] Database backed up to: %BACKUP_DIR%
) else (
    echo [INFO] No database files found, skipping backup
)

timeout /t 2 > nul

REM ========================================
REM Step 2: Pull latest code
REM ========================================
echo.
echo [Step 2/5] Pulling latest code...
echo ========================================

git --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not installed
    echo [INFO] Please update code manually or install Git
    echo.
    set /p manual="Did you manually copy new code? (Y/N): "
    if /i not "%manual%"=="Y" (
        echo [CANCEL] Update cancelled
        pause
        exit /b 1
    )
    goto SKIP_GIT_PULL
)

echo [INFO] Checking Git status...
git status > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Not a Git repository
    echo [INFO] Please update code manually
    pause
    exit /b 1
)

echo [INFO] Saving local changes...
git stash
if errorlevel 1 (
    echo [WARN] Failed to save local changes, continuing...
)

echo [INFO] Pulling latest code...
git pull origin cad
if errorlevel 1 (
    echo [ERROR] Code pull failed
    echo [INFO] Restoring local changes...
    git stash pop
    pause
    exit /b 1
)

echo [INFO] Restoring local changes...
git stash pop > nul 2>&1

echo [OK] Code updated

:SKIP_GIT_PULL
timeout /t 2 > nul

REM ========================================
REM Step 3: Update dependencies
REM ========================================
echo.
echo [Step 3/5] Updating dependencies...
echo ========================================

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo [INFO] Please run: install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Clear proxy settings
set HTTP_PROXY=
set HTTPS_PROXY=

echo [INFO] Updating pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple -q

echo [INFO] Updating packages...
echo [INFO] Using Tsinghua mirror...
pip install -r requirements.txt --upgrade -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [ERROR] Package update failed
    echo.
    echo Try running: fix_pip_network.bat
    echo.
    set /p fix_network="Run network fix script now? (Y/N): "
    if /i "%fix_network%"=="Y" (
        call fix_pip_network.bat
    ) else (
        echo [WARN] Some packages failed to update, continuing...
    )
)

echo [OK] Dependencies updated
timeout /t 2 > nul

REM ========================================
REM Step 4: Restore database
REM ========================================
echo.
echo [Step 4/5] Restoring database...
echo ========================================

if exist "%BACKUP_DIR%\*.db" (
    echo [INFO] Found backup database
    set /p restore="Restore backup? (Y/N): "
    if /i "%restore%"=="Y" (
        echo [INFO] Restoring database...
        copy "%BACKUP_DIR%\*.db" data\ > nul
        echo [OK] Database restored
    ) else (
        echo [SKIP] Not restoring database
        echo [INFO] To restore manually, copy from: %BACKUP_DIR%
    )
) else (
    echo [INFO] No backup files, skipping restore
)

timeout /t 2 > nul

REM ========================================
REM Step 5: Run tests
REM ========================================
echo.
echo [Step 5/5] Running tests...
echo ========================================

set /p run_test="Run tests? (Y/N): "
if /i not "%run_test%"=="Y" (
    echo [SKIP] Tests skipped
    goto SKIP_TEST
)

echo [INFO] Running tests...
python scripts\test_autocad_config.py
if errorlevel 1 (
    echo [WARN] Some tests failed
) else (
    echo [OK] All tests passed
)

:SKIP_TEST
timeout /t 2 > nul

REM ========================================
REM Update Complete
REM ========================================
echo.
echo ========================================
echo  Update Complete!
echo ========================================
echo.
echo Backup location: %BACKUP_DIR%
echo.
echo Update summary:
echo   - Code updated to latest version
echo   - Dependencies updated
echo   - Database preserved/restored
echo.
echo Next steps:
echo   1. View configs: python scripts\autocad_config_manager.py list
echo   2. Start system: start.bat
echo   3. View docs: docs\
echo.
echo ========================================
echo.

set /p start_now="Start now? (Y/N): "
if /i "%start_now%"=="Y" (
    start.bat
) else (
    echo Update complete, press any key to exit
    pause
)
