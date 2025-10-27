# AutoCAD Config System - Install Script for PowerShell
# Run this in PowerShell: .\install.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AutoCAD Config System - Install" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Check Python environment"
Write-Host "  2. Create virtual environment"
Write-Host "  3. Install dependencies"
Write-Host "  4. Initialize config database"
Write-Host "  5. Run tests"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$continue = Read-Host "Press Enter to continue, or Ctrl+C to cancel"

# ========================================
# Step 1: Check Python
# ========================================
Write-Host ""
Write-Host "[Step 1/5] Checking Python..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion detected" -ForegroundColor Green

    # Check version
    $versionCheck = python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Python version too old, need 3.9+" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Python version is compatible" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    Write-Host "Please install Python 3.9+" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Sleep -Seconds 2

# ========================================
# Step 2: Create venv
# ========================================
Write-Host ""
Write-Host "[Step 2/5] Creating virtual environment..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

if (Test-Path "venv") {
    Write-Host "[INFO] Virtual environment already exists" -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create venv" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# ========================================
# Step 3: Install dependencies
# ========================================
Write-Host ""
Write-Host "[Step 3/5] Installing dependencies..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Activate venv
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Clear ALL proxy settings
Write-Host "[INFO] Clearing proxy settings..." -ForegroundColor Yellow
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:ALL_PROXY = ""
$env:NO_PROXY = "*"

# Configure pip to use mirror and no proxy
Write-Host "[INFO] Configuring pip..." -ForegroundColor Yellow
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple 2>$null
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn 2>$null
pip config set global.proxy "" 2>$null

Write-Host "[INFO] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -q

Write-Host "[INFO] Installing packages..." -ForegroundColor Yellow
Write-Host "[INFO] Using Tsinghua mirror (faster in China)..." -ForegroundColor Yellow

# Install packages individually to avoid encoding issues
$packages = @(
    "requests>=2.28.0",
    "pywin32>=305",
    "watchdog>=3.0.0",
    "loguru>=0.7.0",
    "tenacity>=8.2.0",
    "tqdm>=4.65.0",
    "pyyaml>=6.0",
    "psutil>=5.9.0",
    "pytest>=7.0.0",
    "pytest-mock>=3.10.0",
    "pytest-cov>=4.0.0",
    "pyautogui>=0.9.53",
    "pillow>=9.0.0",
    "opencv-python>=4.7.0",
    "typing-extensions>=4.5.0",
    "pymysql>=1.1.0",
    "sqlalchemy>=2.0.0",
    "cryptography>=41.0.0"
)

$failed = @()
foreach ($pkg in $packages) {
    Write-Host "  Installing $pkg..." -ForegroundColor Cyan
    $env:NO_PROXY = "*"
    pip install $pkg -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    [WARN] Failed to install $pkg" -ForegroundColor Yellow
        $failed += $pkg
    } else {
        Write-Host "    [OK] $pkg installed" -ForegroundColor Green
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARN] Some packages failed to install:" -ForegroundColor Yellow
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Red
    }
    Write-Host ""
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        Write-Host "[CANCEL] Installation cancelled" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Start-Sleep -Seconds 2

# ========================================
# Step 4: Initialize database
# ========================================
Write-Host ""
Write-Host "[Step 4/5] Initializing config database..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check and create config.yaml if needed
if (-not (Test-Path "config\config.yaml")) {
    Write-Host "[INFO] config.yaml not found, creating from template..." -ForegroundColor Yellow

    if (-not (Test-Path "config")) {
        Write-Host "[INFO] Creating config directory..." -ForegroundColor Yellow
        New-Item -ItemType Directory -Path "config" -Force | Out-Null
    }

    if (Test-Path "config\config.yaml.example") {
        Copy-Item "config\config.yaml.example" "config\config.yaml"
        Write-Host "[OK] config.yaml created from template" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] config.yaml.example not found!" -ForegroundColor Red
        Write-Host "[INFO] Please ensure config/config.yaml.example exists" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[INFO] Found existing config.yaml" -ForegroundColor Yellow
}

# Check if scripts directory exists
if (-not (Test-Path "scripts")) {
    Write-Host "[ERROR] Scripts directory not found!" -ForegroundColor Red
    Write-Host "[INFO] Please ensure all project files are copied to this directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if init script exists
if (-not (Test-Path "scripts\init_autocad_config.py")) {
    Write-Host "[ERROR] init_autocad_config.py not found!" -ForegroundColor Red
    Write-Host "[INFO] Please ensure all project files are copied to this directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

if (Test-Path "data\*.db") {
    Write-Host "[INFO] Found existing database" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (Y/N)"
    if ($overwrite -ne "Y" -and $overwrite -ne "y") {
        Write-Host "[SKIP] Keeping existing database" -ForegroundColor Yellow
    } else {
        Write-Host "[INFO] Initializing database..." -ForegroundColor Yellow
        python scripts\init_autocad_config.py

        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Database init failed" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
        Write-Host "[OK] Database initialized" -ForegroundColor Green
    }
} else {
    Write-Host "[INFO] Initializing database..." -ForegroundColor Yellow
    python scripts\init_autocad_config.py

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Database init failed" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Database initialized" -ForegroundColor Green
}

Start-Sleep -Seconds 2

# ========================================
# Step 5: Run tests
# ========================================
Write-Host ""
Write-Host "[Step 5/5] Running tests..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$runTest = Read-Host "Run tests? (Y/N)"
if ($runTest -eq "Y" -or $runTest -eq "y") {
    Write-Host "[INFO] Running tests..." -ForegroundColor Yellow
    python scripts\test_autocad_config.py

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARN] Some tests failed" -ForegroundColor Yellow
    } else {
        Write-Host "[OK] All tests passed" -ForegroundColor Green
    }
} else {
    Write-Host "[SKIP] Tests skipped" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# ========================================
# Installation Complete
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database location: data\*.db"
Write-Host "Logs location: logs\"
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Yellow
Write-Host "  1. Run: .\start.ps1"
Write-Host "  2. Or use CMD: cmd /c start.bat"
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - Full guide: docs\DATABASE_CONFIG_GUIDE.md"
Write-Host "  - Quick ref: docs\CONFIG_QUICK_REFERENCE.md"
Write-Host ""
Write-Host "Common commands:" -ForegroundColor Yellow
Write-Host "  View configs: python scripts\autocad_config_manager.py list"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$startNow = Read-Host "Start now? (Y/N)"
if ($startNow -eq "Y" -or $startNow -eq "y") {
    & .\start.ps1
} else {
    Write-Host "Installation complete!" -ForegroundColor Green
    Read-Host "Press Enter to exit"
}
