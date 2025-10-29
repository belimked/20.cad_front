@echo off
REM ============================================================================
REM DWG Processing API 启动脚本 (Windows)
REM ============================================================================

echo ================================================================================
echo DWG Processing API 服务启动
echo ================================================================================
echo.

REM 切换到项目根目录
cd /d "%~dp0"

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 检查依赖是否安装
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo.
    echo [错误] 缺少FastAPI依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [失败] 依赖安装失败，请手动执行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo 启动API服务...
echo - 主机: 0.0.0.0
echo - 端口: 8000
echo - API文档: http://localhost:8000/docs
echo - ReDoc: http://localhost:8000/redoc
echo.
echo 按Ctrl+C停止服务
echo ================================================================================
echo.

REM 启动FastAPI服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
