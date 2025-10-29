@echo off
REM ============================================================================
REM DWG Processing API Startup Script (Windows)
REM ============================================================================

echo ================================================================================
echo DWG Processing API Service Starting...
echo ================================================================================
echo.

REM Switch to project root directory
cd /d "%~dp0"

REM Activate virtual environment (if exists)
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if dependencies are installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] FastAPI not found, installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [FAILED] Dependency installation failed. Please run manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo Starting API service...
echo - Host: 0.0.0.0
echo - Port: 8000
echo - API Docs: http://localhost:8000/docs
echo - ReDoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the service
echo ================================================================================
echo.

REM Start FastAPI service
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
