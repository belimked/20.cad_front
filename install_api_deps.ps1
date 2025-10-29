# ============================================================================
# 安装HTTP API服务依赖 (PowerShell)
# ============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "安装HTTP API服务依赖" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "正在安装新增依赖..." -ForegroundColor Yellow
Write-Host ""
Write-Host "新增依赖列表：" -ForegroundColor Cyan
Write-Host "  - fastapi >= 0.104.0" -ForegroundColor Gray
Write-Host "  - uvicorn[standard] >= 0.24.0" -ForegroundColor Gray
Write-Host "  - pydantic >= 2.0.0" -ForegroundColor Gray
Write-Host "  - python-multipart >= 0.0.6" -ForegroundColor Gray
Write-Host "  - httpx >= 0.25.0" -ForegroundColor Gray
Write-Host "  - aiofiles >= 23.0.0" -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 方式1：安装所有依赖（推荐）
Write-Host "[方式1] 安装requirements.txt中的所有依赖（推荐）" -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[失败] 完整安装失败，尝试单独安装新增依赖..." -ForegroundColor Red
    Write-Host ""

    # 方式2：仅安装新增依赖
    Write-Host "[方式2] 仅安装HTTP API新增依赖" -ForegroundColor Yellow
    pip install "fastapi>=0.104.0"
    pip install "uvicorn[standard]>=0.24.0"
    pip install "pydantic>=2.0.0"
    pip install "python-multipart>=0.0.6"
    pip install "httpx>=0.25.0"
    pip install "aiofiles>=23.0.0"

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host "[失败] 依赖安装失败！" -ForegroundColor Red
        Write-Host "================================================================================" -ForegroundColor Red
        Write-Host "请检查：" -ForegroundColor Yellow
        Write-Host "  1. Python环境是否正确" -ForegroundColor Gray
        Write-Host "  2. pip是否可用" -ForegroundColor Gray
        Write-Host "  3. 网络连接是否正常" -ForegroundColor Gray
        Write-Host ""
        Write-Host "手动安装命令：" -ForegroundColor Cyan
        Write-Host "  pip install fastapi uvicorn[standard] pydantic python-multipart httpx aiofiles" -ForegroundColor Gray
        Write-Host "================================================================================" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "[成功] 依赖安装完成！" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "验证安装..." -ForegroundColor Yellow
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import httpx; print(f'httpx: {httpx.__version__}')"
python -c "import aiofiles; print('aiofiles: OK')"
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "现在可以启动HTTP API服务：" -ForegroundColor Cyan
Write-Host "  .\start_api.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "或访问API文档：" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "按任意键退出"
