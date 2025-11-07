# CAD PDF Converter

[![CI](https://github.com/belimked/20.cad_front/actions/workflows/ci.yml/badge.svg)](https://github.com/belimked/20.cad_front/actions/workflows/ci.yml)
[![Release Build](https://github.com/belimked/20.cad_front/actions/workflows/release.yml/badge.svg)](https://github.com/belimked/20.cad_front/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个基于 Tauri + Svelte 的跨平台桌面应用，用于将 CAD 文件（DWG）转换为 PDF 格式。

## 🎯 功能特性

- ✅ 支持 DWG 文件上传（拖拽或选择）
- ✅ 异步任务处理与实时监控
- ✅ 进度条可视化
- ✅ PDF 生成和下载
- ✅ 任务历史记录
- ✅ 跨平台支持（Windows、macOS、Linux）

## 🛠️ 技术栈

### 前端
- **框架**: Svelte 4.x
- **语言**: TypeScript 5.x
- **构建**: Vite 5.x
- **UI**: 自研组件

### 后端
- **框架**: Tauri 1.5
- **语言**: Rust 1.75+
- **HTTP**: reqwest
- **存储**: tauri-plugin-store

## 📋 前置要求

### 开发环境

- **Node.js**: >= 18.x
- **pnpm**: >= 8.x（推荐）或 npm
- **Rust**: >= 1.75 (安装: https://rustup.rs/)
- **Tauri CLI**: 通过 npm 自动安装

### 平台特定要求

**Windows**:
- Microsoft Visual Studio C++ Build Tools
- WebView2 (Windows 10+ 自带)

**macOS**:
- Xcode Command Line Tools
  ```bash
  xcode-select --install
  ```

**Linux** (Ubuntu/Debian):
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

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/cad-pdf-converter.git
cd cad-pdf-converter
```

### 2. 安装依赖

```bash
# 使用 pnpm (推荐)
pnpm install

# 或使用 npm
npm install
```

### 3. 启动开发服务器

```bash
# 启动 Tauri 开发模式
pnpm tauri:dev

# 或
npm run tauri:dev
```

应用将自动打开，前端开发服务器运行在 `http://localhost:1420`

### 4. 构建生产版本

```bash
# 构建应用
pnpm tauri:build

# 或
npm run tauri:build
```

构建产物位于:
- **Windows**: `src-tauri/target/release/bundle/msi/`
- **macOS**: `src-tauri/target/release/bundle/dmg/`
- **Linux**: `src-tauri/target/release/bundle/appimage/`

## 📁 项目结构

```
cad-pdf-converter/
├── src/                        # 前端源码 (Svelte + TypeScript)
│   ├── components/             # UI 组件
│   │   ├── upload/             # 上传相关组件
│   │   ├── task/               # 任务相关组件
│   │   ├── pdf/                # PDF 相关组件
│   │   ├── history/            # 历史相关组件
│   │   └── common/             # 通用组件
│   ├── stores/                 # 状态管理 (Svelte Stores)
│   ├── services/               # 业务逻辑服务
│   ├── utils/                  # 工具函数
│   ├── types/                  # TypeScript 类型定义
│   ├── styles/                 # 全局样式
│   ├── App.svelte              # 根组件
│   └── main.ts                 # 入口文件
├── src-tauri/                  # Tauri 后端 (Rust)
│   ├── src/
│   │   ├── commands/           # Tauri Commands
│   │   ├── services/           # Rust 服务层
│   │   ├── models/             # 数据模型
│   │   ├── error.rs            # 错误类型
│   │   └── main.rs             # 入口文件
│   ├── icons/                  # 应用图标
│   ├── Cargo.toml              # Rust 依赖配置
│   └── tauri.conf.json         # Tauri 配置
├── docs/                       # 项目文档
│   ├── prd.md                  # 产品需求文档
│   └── architecture.md         # 架构文档
├── package.json                # 前端依赖
├── vite.config.ts              # Vite 配置
├── tsconfig.json               # TypeScript 配置
└── README.md                   # 本文件
```

## 🔧 开发指南

### 可用脚本

```bash
# 前端开发
pnpm dev                 # 启动 Vite 开发服务器
pnpm build               # 构建前端
pnpm preview             # 预览构建结果

# Tauri 开发
pnpm tauri:dev           # 启动 Tauri 开发模式
pnpm tauri:build         # 构建 Tauri 应用

# 代码质量
pnpm lint                # 运行 ESLint
pnpm lint:fix            # 自动修复 ESLint 问题
pnpm format              # 格式化代码 (Prettier)
pnpm format:check        # 检查代码格式
pnpm check               # 运行 Svelte 类型检查
```

### 环境变量

创建 `.env.local` 文件（不提交到 Git）:

```env
# API 基础 URL
VITE_API_BASE_URL=https://api.example.com

# 开发模式
VITE_DEV_MODE=true
```

### 调试

**前端调试**:
- 开发模式下自动打开 Chrome DevTools
- 使用 VS Code Debugger

**Rust 后端调试**:
```bash
# 启用 Rust 日志
RUST_LOG=debug pnpm tauri:dev
```

## 🧪 测试

```bash
# 前端单元测试
pnpm test

# Rust 后端测试
cd src-tauri
cargo test
```

## 📝 代码规范

项目使用以下工具确保代码质量:

- **ESLint**: JavaScript/TypeScript 代码检查
- **Prettier**: 代码格式化
- **Clippy**: Rust 代码检查
- **rustfmt**: Rust 代码格式化

提交代码前请确保:
```bash
pnpm lint:fix
pnpm format
cd src-tauri && cargo clippy && cargo fmt
```

## 🔗 相关链接

- **Tauri 文档**: https://tauri.app/
- **Svelte 文档**: https://svelte.dev/
- **架构文档**: [docs/architecture.md](./docs/architecture.md)
- **PRD 文档**: [docs/prd.md](./docs/prd.md)

## 🐛 常见问题

### 1. Rust 编译失败

**问题**: `error: linker 'cc' not found`

**解决方案**:
- Windows: 安装 Visual Studio C++ Build Tools
- macOS: 运行 `xcode-select --install`
- Linux: 运行 `sudo apt install build-essential`

### 2. 前端无法连接到 Tauri

**问题**: `Failed to connect to Tauri backend`

**解决方案**:
- 确保使用 `pnpm tauri:dev` 而不是 `pnpm dev`
- 检查防火墙设置

### 3. 应用无法启动

**问题**: `Error: Could not find WebView2`

**解决方案**:
- Windows: 安装 WebView2 Runtime
- 下载: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

## 📄 许可证

[MIT License](LICENSE)

## 🤝 贡献

欢迎贡献! 请遵循以下步骤:

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 👥 团队

- **Product Manager**: John
- **Architect**: Winston
- **Developers**: [待补充]

## 📮 联系方式

- 问题反馈: [GitHub Issues](https://github.com/yourusername/cad-pdf-converter/issues)
- 邮箱: support@example.com

---

**开发状态**: 🚧 积极开发中

**当前版本**: v0.1.0

**最后更新**: 2025-11-06
