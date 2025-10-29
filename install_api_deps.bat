@echo off
REM ============================================================================
REM 安装HTTP API服务依赖
REM ============================================================================

echo ================================================================================
echo 安装HTTP API服务依赖
echo ================================================================================
echo.

REM 切换到项目根目录
cd /d "%~dp0"

echo 正在安装新增依赖...
echo.
echo 新增依赖列表：
echo   - fastapi ^>= 0.104.0
echo   - uvicorn[standard] ^>= 0.24.0
echo   - pydantic ^>= 2.0.0
echo   - python-multipart ^>= 0.0.6
echo   - httpx ^>= 0.25.0
echo   - aiofiles ^>= 23.0.0
echo.
echo ================================================================================
echo.

REM 方式1：安装所有依赖（推荐）
echo [方式1] 安装requirements.txt中的所有依赖（推荐）
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [失败] 完整安装失败，尝试单独安装新增依赖...
    echo.

    REM 方式2：仅安装新增依赖
    echo [方式2] 仅安装HTTP API新增依赖
    pip install fastapi>=0.104.0
    pip install "uvicorn[standard]>=0.24.0"
    pip install pydantic>=2.0.0
    pip install python-multipart>=0.0.6
    pip install httpx>=0.25.0
    pip install aiofiles>=23.0.0

    if errorlevel 1 (
        echo.
        echo ================================================================================
        echo [失败] 依赖安装失败！
        echo ================================================================================
        echo 请检查：
        echo   1. Python环境是否正确
        echo   2. pip是否可用
        echo   3. 网络连接是否正常
        echo.
        echo 手动安装命令：
        echo   pip install fastapi uvicorn[standard] pydantic python-multipart httpx aiofiles
        echo ================================================================================
        pause
        exit /b 1
    )
)

echo.
echo ================================================================================
echo [成功] 依赖安装完成！
echo ================================================================================
echo.
echo 验证安装...
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import httpx; print(f'httpx: {httpx.__version__}')"
python -c "import aiofiles; print('aiofiles: OK')"
echo.
echo ================================================================================
echo 现在可以启动HTTP API服务：
echo   start_api.bat
echo.
echo 或访问API文档：
echo   http://localhost:8000/docs
echo ================================================================================
echo.
pause
