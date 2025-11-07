# 开发设置指南

本文档提供详细的开发环境配置步骤。

## 目录

1. [前置要求](#前置要求)
2. [环境安装](#环境安装)
3. [项目配置](#项目配置)
4. [IDE 设置](#ide-设置)
5. [常见问题](#常见问题)

---

## 前置要求

### 系统要求

- **操作系统**: Windows 10+, macOS 11+, 或主流 Linux 发行版
- **内存**: 最少 8GB RAM（推荐 16GB）
- **磁盘空间**: 至少 10GB 可用空间

### 必需软件

| 软件 | 最低版本 | 推荐版本 | 安装链接 |
|------|---------|---------|---------|
| Node.js | 18.x | 20.x | [nodejs.org](https://nodejs.org/) |
| Rust | 1.75 | Latest | [rustup.rs](https://rustup.rs/) |
| Git | 2.x | Latest | [git-scm.com](https://git-scm.com/) |

---

## 环境安装

### 1. Node.js 安装

**Windows / macOS**:
1. 访问 https://nodejs.org/
2. 下载 LTS 版本
3. 运行安装程序
4. 验证安装:
   ```bash
   node --version
   npm --version
   ```

**Linux (Ubuntu/Debian)**:
```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证
node --version
npm --version
```

### 2. pnpm 安装 (推荐)

```bash
# 全局安装 pnpm
npm install -g pnpm

# 验证
pnpm --version
```

### 3. Rust 安装

**所有平台**:
```bash
# 安装 Rustup (Rust 安装器)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 选择默认安装 (选项 1)

# 更新环境变量
source $HOME/.cargo/env

# 验证
rustc --version
cargo --version
```

### 4. Tauri 系统依赖

**Windows**:
1. 安装 Visual Studio C++ Build Tools:
   - 访问 https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - 安装 "Desktop development with C++" 工作负载

2. 安装 WebView2:
   - Windows 10/11 自带
   - 如需手动安装: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

**macOS**:
```bash
# 安装 Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev
```

**Linux (Fedora)**:
```bash
sudo dnf install webkit2gtk4.0-devel \
    openssl-devel \
    curl \
    wget \
    libappindicator-gtk3-devel \
    librsvg2-devel
sudo dnf group install "C Development Tools and Libraries"
```

---

## 项目配置

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/cad-pdf-converter.git
cd cad-pdf-converter
```

### 2. 安装依赖

```bash
# 安装前端依赖
pnpm install

# 首次运行会自动安装 Rust 依赖
# 或手动安装:
cd src-tauri
cargo build
cd ..
```

### 3. 配置环境变量

创建 `.env.local` 文件:

```env
# API 基础 URL
VITE_API_BASE_URL=https://api.example.com

# 轮询间隔 (毫秒)
VITE_POLLING_INTERVAL=3000

# 开发模式
VITE_DEV_MODE=true
```

### 4. 验证安装

```bash
# 运行前端开发服务器
pnpm dev

# 在另一个终端运行 Tauri
pnpm tauri:dev
```

如果应用成功启动，说明环境配置正确！

---

## IDE 设置

### VS Code (推荐)

#### 必装扩展

```json
{
  "recommendations": [
    "svelte.svelte-vscode",           // Svelte 支持
    "rust-lang.rust-analyzer",        // Rust 支持
    "tauri-apps.tauri-vscode",        // Tauri 支持
    "dbaeumer.vscode-eslint",         // ESLint
    "esbenp.prettier-vscode",         // Prettier
    "bradlc.vscode-tailwindcss"       // Tailwind (可选)
  ]
}
```

#### 工作区设置

创建 `.vscode/settings.json`:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[svelte]": {
    "editor.defaultFormatter": "svelte.svelte-vscode"
  },
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  },
  "rust-analyzer.checkOnSave.command": "clippy",
  "files.associations": {
    "*.rs": "rust"
  }
}
```

#### 调试配置

创建 `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "lldb",
      "request": "launch",
      "name": "Tauri Development Debug",
      "cargo": {
        "args": [
          "build",
          "--manifest-path=./src-tauri/Cargo.toml",
          "--no-default-features"
        ]
      },
      "preLaunchTask": "ui:dev"
    }
  ]
}
```

### IntelliJ IDEA / WebStorm

#### 必装插件

- Svelte
- Rust
- Prettier
- ESLint

#### 项目设置

1. 打开项目
2. 信任项目
3. 启用 Prettier: Settings → Languages & Frameworks → JavaScript → Prettier
4. 启用 ESLint: Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint

---

## 开发工作流

### 日常开发

```bash
# 1. 启动开发模式
pnpm tauri:dev

# 2. 修改代码（自动热重载）

# 3. 提交前检查
pnpm lint
pnpm format:check
cd src-tauri && cargo clippy
```

### 添加新功能

```bash
# 1. 创建新分支
git checkout -b feature/my-feature

# 2. 开发功能

# 3. 运行测试
pnpm test
cd src-tauri && cargo test

# 4. 提交代码
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### 构建发布版本

```bash
# 构建所有平台
pnpm tauri:build

# 构建特定平台
pnpm tauri build -- --target x86_64-pc-windows-msvc  # Windows
pnpm tauri build -- --target x86_64-apple-darwin      # macOS Intel
pnpm tauri build -- --target aarch64-apple-darwin     # macOS Apple Silicon
pnpm tauri build -- --target x86_64-unknown-linux-gnu # Linux
```

---

## 常见问题

### 问题 1: `cargo: command not found`

**原因**: Rust 环境变量未加载

**解决**:
```bash
# 手动加载环境变量
source $HOME/.cargo/env

# 或重启终端
```

### 问题 2: Tauri 编译错误 `linker 'cc' not found`

**原因**: 缺少 C/C++ 编译器

**解决**:
- Windows: 安装 Visual Studio C++ Build Tools
- macOS: 运行 `xcode-select --install`
- Linux: 运行 `sudo apt install build-essential`

### 问题 3: 前端无法连接 Tauri

**原因**: 端口冲突或防火墙

**解决**:
1. 检查端口 1420 是否被占用
2. 检查防火墙设置
3. 使用 `pnpm tauri:dev` 而不是分别启动

### 问题 4: WebView2 错误 (Windows)

**原因**: 缺少 WebView2 Runtime

**解决**:
1. 下载 WebView2 Runtime: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
2. 运行安装程序

### 问题 5: Svelte 类型错误

**原因**: TypeScript 配置或缓存问题

**解决**:
```bash
# 重新生成类型
pnpm check

# 清理缓存
rm -rf node_modules .svelte-kit
pnpm install
```

---

## 性能优化建议

### 开发模式优化

```bash
# 使用 Rust 增量编译
export CARGO_INCREMENTAL=1

# 启用 Rust 缓存
export CARGO_TARGET_DIR=~/.cache/cargo-target
```

### 构建优化

```bash
# 使用 LTO (Link Time Optimization)
# 在 src-tauri/Cargo.toml 中:
[profile.release]
lto = true
codegen-units = 1
```

---

## 获取帮助

遇到问题？

1. 查看 [常见问题](#常见问题)
2. 搜索 [GitHub Issues](https://github.com/yourusername/cad-pdf-converter/issues)
3. 查阅 [Tauri 文档](https://tauri.app/)
4. 查阅 [Svelte 文档](https://svelte.dev/)
5. 联系团队: support@example.com

---

**文档版本**: v1.0
**最后更新**: 2025-11-06
