# 🚀 快速开始 / Quick Start

## ⚡ 一键安装 / One-Click Installation

### Windows 测试机器安装 (推荐)

**方式 1: PowerShell (推荐)** ⭐⭐⭐⭐⭐
```powershell
.\install.ps1
```

**方式 2: 命令提示符 (CMD)**
```cmd
install.bat
```

**方式 3: 双击运行**
- 在文件管理器中双击 `install.bat`

---

## ❗ 遇到安装问题?

### 如果看到以下错误:

#### 1️⃣ 代理错误 (ProxyError) ⚠️ 最常见!
```
ProxyError('Cannot connect to proxy.')
[WinError 10061] 由于目标计算机积极拒绝，无法连接。
```

**✅ 解决方案 (按顺序尝试)**:

**方案 A: 使用中科大源修复脚本 (推荐)** ⭐⭐⭐⭐⭐
```powershell
# PowerShell
.\fix_proxy_ustc.ps1
```
或
```cmd
REM CMD
fix_proxy_ustc.bat
```

**方案 B: 使用清华源紧急修复**
```powershell
.\emergency_fix.ps1
```

**方案 C: 一键救命命令**
```powershell
# 复制粘贴到 PowerShell 直接运行
$env:HTTP_PROXY=""; $env:HTTPS_PROXY=""; netsh winhttp reset proxy; pip config unset global.proxy; pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/web/simple; pip config set global.trusted-host mirrors.ustc.edu.cn
```

**方案 D: 查看详细解决方案**
- 打开 `PROXY_FIX_ULTIMATE.md` 查看完整的手动修复步骤

#### 2️⃣ 编码错误 (UnicodeDecodeError)
```
UnicodeDecodeError: 'gbk' codec can't decode
```
**解决**: 文件已修复,重新运行安装脚本即可
```powershell
.\install.ps1
```

#### 3️⃣ PowerShell 乱码
```
'?timeout' 不是内部或外部命令
```
**解决**: 使用 CMD 或双击 .bat 文件
```cmd
install.bat
```

---

## 📖 详细文档

- **🔥 代理错误终极解决方案**: `PROXY_FIX_ULTIMATE.md` - 代理问题完整修复指南 ⭐⭐⭐⭐⭐
- **安装问题修复指南**: `INSTALLATION_FIX_GUIDE.md` - 所有安装问题的详细解决方案
- **修复内容总结**: `FIXES_SUMMARY.md` - 已修复的问题清单
- **如何运行脚本**: `HOW_TO_RUN.md` - 不同运行方式说明
- **数据库配置指南**: `docs/DATABASE_CONFIG_GUIDE.md` - 完整使用指南
- **部署指南**: `docs/TESTING_DEPLOYMENT_GUIDE.md` - 测试机器部署步骤

---

## ✅ 验证安装成功

安装完成后,运行:

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 查看配置列表
python scripts\autocad_config_manager.py list
```

如果看到配置列表,说明安装成功! 🎉

---

## 🎯 快速使用

### 1. 查看所有配置
```powershell
python scripts\autocad_config_manager.py list
```

### 2. 激活配置
```powershell
python scripts\autocad_config_manager.py activate default
```

### 3. 运行工作流
```powershell
python research\autocad_com_api\9_configurable_workflow.py --config default
```

### 4. 更新配置
```powershell
python scripts\autocad_config_manager.py update 1 --autocad_exe_path "C:\Program Files\Autodesk\AutoCAD 2014\acad.exe"
```

---

## 🔄 更新系统

```powershell
.\update.bat
```

或

```cmd
update.bat
```

---

## 📦 项目结构

```
项目根目录/
├── scripts/              # 管理脚本
│   ├── init_autocad_config.py      # 初始化数据库
│   ├── autocad_config_manager.py   # 配置管理CLI
│   └── test_autocad_config.py      # 测试脚本
├── src/
│   ├── models/          # 数据模型
│   │   └── autocad_config.py
│   └── services/        # 业务逻辑
│       └── autocad_config_service.py
├── research/
│   └── autocad_com_api/
│       └── 9_configurable_workflow.py  # 主工作流
├── data/                # 数据库文件 (自动生成)
├── logs/                # 日志文件 (自动生成)
├── docs/                # 文档
├── install.ps1          # PowerShell 安装脚本
├── install.bat          # CMD 安装脚本
├── fix_proxy_ustc.ps1   # 中科大源代理修复 (推荐) ⭐⭐⭐⭐⭐
├── fix_proxy_ustc.bat   # 中科大源代理修复 (CMD)
├── emergency_fix.ps1    # 清华源紧急修复
├── PROXY_FIX_ULTIMATE.md  # 代理问题终极指南
└── requirements.txt     # Python 依赖
```

---

## 🆘 需要帮助?

1. **🔥 代理错误**: 查看 `PROXY_FIX_ULTIMATE.md` - 完整的代理问题解决方案
2. **查看详细错误**: 检查 `logs/` 目录
3. **阅读修复指南**: `INSTALLATION_FIX_GUIDE.md`
4. **查看配置文档**: `docs/DATABASE_CONFIG_GUIDE.md`

---

## ⚙️ 系统要求

- **操作系统**: Windows 7/8/10/11
- **Python**: 3.9 或更高版本
- **AutoCAD**: 2014 或更高版本
- **磁盘空间**: 至少 500MB

---

## 🎉 开始使用!

现在就运行 `.\install.ps1` 开始安装吧! 🚀

**❗ 如果遇到代理错误**: 运行 `.\fix_proxy_ustc.ps1` 修复! 🔧

**提示**: 所有安装问题都已修复,可以放心使用! ✅
