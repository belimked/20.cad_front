# ========================================
# Emergency Proxy Fix - Using USTC Mirror
# ========================================

Write-Host "========================================" -ForegroundColor Red
Write-Host " EMERGENCY PROXY FIX" -ForegroundColor Red
Write-Host " Using USTC Mirror (ustc.edu.cn)" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# ========================================
# Step 1: Kill all proxy settings
# ========================================
Write-Host "[Step 1] Clearing ALL proxy settings..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# Clear environment variables
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:ALL_PROXY = ""
$env:NO_PROXY = "*"
$env:http_proxy = ""
$env:https_proxy = ""
$env:all_proxy = ""
$env:no_proxy = "*"

Write-Host "[OK] Environment proxy cleared" -ForegroundColor Green

# Clear system proxy
Write-Host "[INFO] Clearing system proxy..." -ForegroundColor Yellow
try {
    netsh winhttp reset proxy 2>&1 | Out-Null
    Write-Host "[OK] System proxy cleared" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not clear system proxy" -ForegroundColor Yellow
}

# Clear pip config
Write-Host "[INFO] Clearing pip proxy config..." -ForegroundColor Yellow
pip config unset global.proxy 2>$null
pip config unset install.proxy 2>$null
pip config unset proxy 2>$null
Write-Host "[OK] Pip proxy config cleared" -ForegroundColor Green

Start-Sleep -Seconds 2

# ========================================
# Step 2: Configure pip to use USTC mirror
# ========================================
Write-Host ""
Write-Host "[Step 2] Configuring pip to use USTC mirror..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple
pip config set install.trusted-host mirrors.ustc.edu.cn
pip config set global.trusted-host mirrors.ustc.edu.cn

Write-Host "[OK] Pip configured for USTC mirror" -ForegroundColor Green
Start-Sleep -Seconds 2

# ========================================
# Step 3: Verify configuration
# ========================================
Write-Host ""
Write-Host "[Step 3] Verifying configuration..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

Write-Host ""
Write-Host "Current pip config:" -ForegroundColor Cyan
pip config list

Write-Host ""
Write-Host "Current proxy env vars:" -ForegroundColor Cyan
Write-Host "  HTTP_PROXY: $env:HTTP_PROXY"
Write-Host "  HTTPS_PROXY: $env:HTTPS_PROXY"

Start-Sleep -Seconds 2

# ========================================
# Step 4: Install packages
# ========================================
Write-Host ""
Write-Host "[Step 4] Installing packages from USTC..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# Activate venv if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[WARN] No venv found, using system Python" -ForegroundColor Yellow
}

# Upgrade pip first
Write-Host ""
Write-Host "[INFO] Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip `
    -i https://mirrors.ustc.edu.cn/pypi/web/simple `
    --trusted-host mirrors.ustc.edu.cn `
    --trusted-host pypi.org `
    --trusted-host pypi.python.org `
    --trusted-host files.pythonhosted.org `
    --no-proxy ""

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Pip upgraded" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Pip upgrade failed" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Install packages one by one
Write-Host ""
Write-Host "[INFO] Installing core packages..." -ForegroundColor Cyan

$packages = @(
    "requests>=2.28.0",
    "sqlalchemy>=2.0.0",
    "pywin32>=305",
    "psutil>=5.9.0",
    "watchdog>=3.0.0",
    "loguru>=0.7.0",
    "tenacity>=8.2.0",
    "tqdm>=4.65.0",
    "pyyaml>=6.0",
    "pytest>=7.0.0",
    "pytest-mock>=3.10.0",
    "pytest-cov>=4.0.0",
    "pyautogui>=0.9.53",
    "pillow>=9.0.0",
    "opencv-python>=4.7.0",
    "typing-extensions>=4.5.0",
    "pymysql>=1.1.0",
    "cryptography>=41.0.0"
)

$success = @()
$failed = @()

foreach ($pkg in $packages) {
    Write-Host ""
    Write-Host "Installing: $pkg" -ForegroundColor Cyan

    # Use multiple methods to ensure no proxy
    $env:HTTP_PROXY = ""
    $env:HTTPS_PROXY = ""
    $env:NO_PROXY = "*"

    pip install $pkg `
        -i https://mirrors.ustc.edu.cn/pypi/web/simple `
        --trusted-host mirrors.ustc.edu.cn `
        --trusted-host pypi.org `
        --trusted-host pypi.python.org `
        --trusted-host files.pythonhosted.org `
        --no-cache-dir `
        2>&1 | Tee-Object -Variable output

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $pkg installed" -ForegroundColor Green
        $success += $pkg
    } else {
        Write-Host "[FAILED] $pkg" -ForegroundColor Red
        $failed += $pkg

        # If it still fails, try with pip.org directly
        Write-Host "[RETRY] Trying with PyPI directly..." -ForegroundColor Yellow
        pip install $pkg --trusted-host pypi.org --trusted-host files.pythonhosted.org

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $pkg installed (via PyPI)" -ForegroundColor Green
            $success += $pkg
            $failed = $failed | Where-Object { $_ -ne $pkg }
        }
    }
}

# ========================================
# Step 5: Summary
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Successfully installed: $($success.Count) packages" -ForegroundColor Green
foreach ($pkg in $success) {
    Write-Host "  [OK] $pkg" -ForegroundColor Green
}

Write-Host ""
if ($failed.Count -gt 0) {
    Write-Host "Failed to install: $($failed.Count) packages" -ForegroundColor Red
    foreach ($pkg in $failed) {
        Write-Host "  [X] $pkg" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "You can try installing failed packages manually:" -ForegroundColor Yellow
    Write-Host "  pip install <package-name> -i https://mirrors.aliyun.com/pypi/simple/" -ForegroundColor Yellow
} else {
    Write-Host "All packages installed successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
