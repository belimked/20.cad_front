# ============================================================================
# DWG Processing API 启动脚本 (PowerShell)
# ============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "DWG Processing API 服务启动" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# 激活虚拟环境（如果存在）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "激活虚拟环境..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# 检查依赖是否安装
Write-Host ""
Write-Host "检查依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "FastAPI未安装"
    }
} catch {
    Write-Host ""
    Write-Host "[错误] 缺少FastAPI依赖，正在安装..." -ForegroundColor Red
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[失败] 依赖安装失败，请手动执行: pip install -r requirements.txt" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

Write-Host ""
Write-Host "启动API服务..." -ForegroundColor Green
Write-Host "- 主机: 0.0.0.0" -ForegroundColor Gray
Write-Host "- 端口: 8000" -ForegroundColor Gray
Write-Host "- API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "- ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "按Ctrl+C停止服务" -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 启动FastAPI服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
