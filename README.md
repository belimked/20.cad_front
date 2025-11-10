# CAD PDF Converter

> 基于 Tauri 的现代化桌面应用，将 CAD 文件转换为 PDF

[![Tauri](https://img.shields.io/badge/Tauri-1.5-blue.svg)](https://tauri.app/)
[![Svelte](https://img.shields.io/badge/Svelte-4.0-orange.svg)](https://svelte.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Rust](https://img.shields.io/badge/Rust-1.75+-orange.svg)](https://www.rust-lang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📖 项目简介

CAD PDF Converter 是一款跨平台桌面应用程序，专为 CAD 文件到 PDF 的转换流程设计。应用采用现代化的技术栈，提供流畅的用户体验和强大的功能。

**核心功能：**

1. 📤 **文件上传** - 支持拖拽上传和文件选择对话框
2. 🔄 **异步处理** - 提交任务后实时监控转换进度
3. 📊 **任务管理** - 查看任务状态、进度和历史记录
4. 📄 **PDF 预览** - 内置 PDF.js 查看器，支持缩放、旋转、翻页
5. 📥 **批量下载** - 支持单个或批量下载转换结果
6. 🎨 **关系可视化** - 图形化展示 DWG 与 PDF 文件的对应关系

---

## ✨ 技术特性

- ✅ **现代化 UI** - 基于 Svelte 4 构建的响应式界面
- ✅ **类型安全** - TypeScript 提供完整的类型检查
- ✅ **高性能后端** - Rust 驱动的 Tauri 后端，内存占用小
- ✅ **跨平台支持** - Windows、macOS 原生应用
- ✅ **安全可靠** - Tauri 安全架构，严格的权限控制
- ✅ **本地存储** - 任务历史本地持久化
- ✅ **CI/CD 自动化** - GitHub Actions 自动构建和发布

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端层 (Svelte)                   │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ 文件上传   │  │ 任务监控   │  │  PDF 预览    │  │
│  │ 组件       │  │ 组件       │  │  组件        │  │
│  └──────┬─────┘  └──────┬─────┘  └──────┬───────┘  │
│         │                │                │          │
│         └────────────────┼────────────────┘          │
│                          │                           │
│                  ┌───────▼────────┐                  │
│                  │  状态管理      │                  │
│                  │  (Store)       │                  │
│                  └───────┬────────┘                  │
└──────────────────────────┼──────────────────────────┘
                           │
                  ┌────────▼─────────┐
                  │  Tauri Commands  │
                  └────────┬─────────┘
┌──────────────────────────┼──────────────────────────┐
│                    后端层 (Rust)                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ 文件上传    │  │ HTTP 客户端  │  │ 本地存储   │ │
│  │ Handler     │  │ (reqwest)    │  │ Manager    │ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                │                 │         │
│         └────────────────┼─────────────────┘         │
│                          │                           │
│                  ┌───────▼────────┐                  │
│                  │  API 客户端    │                  │
│                  │  (后端服务)    │                  │
│                  └───────┬────────┘                  │
└──────────────────────────┼──────────────────────────┘
                           │
                  ┌────────▼─────────┐
                  │   远程 API 服务   │
                  │  (DWG 转 PDF)    │
                  └──────────────────┘
```

---

## 📂 项目结构

```
cad-pdf-converter/
├── src/                        # 前端源码 (Svelte + TypeScript)
│   ├── App.svelte              # 主应用组件
│   ├── components/             # UI 组件
│   │   ├── upload/             # 文件上传组件
│   │   ├── task/               # 任务管理组件
│   │   └── preview/            # PDF 预览组件
│   ├── stores/                 # 状态管理
│   │   ├── taskStore.ts        # 任务状态
│   │   └── configStore.ts      # 配置管理
│   ├── services/               # 服务层
│   │   ├── api.ts              # API 客户端
│   │   └── taskPollingService.ts  # 轮询服务
│   ├── types/                  # TypeScript 类型定义
│   └── utils/                  # 工具函数
├── src-tauri/                  # Rust 后端源码
│   ├── src/
│   │   ├── main.rs             # 应用入口
│   │   ├── commands/           # Tauri Commands
│   │   │   ├── upload.rs       # 文件上传
│   │   │   ├── task.rs         # 任务查询
│   │   │   └── storage.rs      # 本地存储
│   │   ├── models/             # 数据模型
│   │   │   ├── task.rs         # 任务模型
│   │   │   └── response.rs     # 响应模型
│   │   └── utils/              # 工具模块
│   ├── Cargo.toml              # Rust 依赖配置
│   └── tauri.conf.json         # Tauri 配置
├── docs/                       # 项目文档
│   ├── index.md                # 文档索引
│   ├── prd.md                  # 产品需求文档
│   ├── architecture.md         # 架构设计文档
│   ├── DEVELOPMENT_SETUP.md    # 开发环境配置
│   └── stories/                # 开发任务 Stories
├── .github/                    # GitHub Actions 配置
│   └── workflows/
│       ├── ci.yml              # 代码质量检查
│       └── release.yml         # 自动构建发布
├── package.json                # Node.js 依赖
├── vite.config.ts              # Vite 构建配置
├── tsconfig.json               # TypeScript 配置
└── README.md                   # 项目说明
```

---

## 🚀 快速开始

### 前置要求

- **Node.js**: 18.x 或更高版本
- **Rust**: 1.75 或更高版本 (可选，仅本地开发需要)
- **操作系统**: Windows 10+, macOS 11+

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/cad-pdf-converter.git
cd cad-pdf-converter

# 2. 安装前端依赖
npm install

# 3. 启动开发服务器
npm run tauri dev
```

### 构建应用

```bash
# 构建生产版本
npm run tauri build
```

构建产物位置：
- **macOS**: `src-tauri/target/release/bundle/dmg/`
- **Windows**: `src-tauri/target/release/bundle/msi/`

---

## 📚 开发指南

### 开发环境配置

详细的开发环境配置请参考：[开发环境设置指南](docs/DEVELOPMENT_SETUP.md)

### 可用脚本

```bash
# 开发模式
npm run tauri dev          # 启动 Tauri 开发服务器

# 代码检查
npm run lint               # 运行 ESLint
npm run format             # 运行 Prettier 格式化
npm run format:check       # 检查代码格式
npm run check              # TypeScript 类型检查

# Rust 代码检查
cd src-tauri
cargo fmt                  # 格式化 Rust 代码
cargo clippy               # 运行 Clippy 静态分析

# 构建
npm run tauri build        # 构建生产版本
```

### 项目文档

- 📋 [产品需求文档 (PRD)](docs/prd.md)
- 🏗️ [系统架构文档](docs/architecture.md)
- 📖 [完整文档索引](docs/index.md)
- 📝 [用户故事 (Stories)](docs/stories/STORIES_INDEX.md)

---

## 🔧 技术栈

### 前端

- **框架**: [Svelte 4](https://svelte.dev/) - 编译型响应式框架
- **语言**: [TypeScript 5](https://www.typescriptlang.org/) - 类型安全的 JavaScript
- **构建工具**: [Vite 5](https://vitejs.dev/) - 下一代前端构建工具
- **状态管理**: Svelte Stores - 内置状态管理
- **HTTP 客户端**: Fetch API + Tauri HTTP

### 后端

- **框架**: [Tauri 1.5](https://tauri.app/) - 轻量级桌面应用框架
- **语言**: [Rust 1.75+](https://www.rust-lang.org/) - 内存安全的系统编程语言
- **HTTP 客户端**: [reqwest](https://github.com/seanmonstar/reqwest) - Rust HTTP 客户端
- **序列化**: [serde](https://serde.rs/) - Rust 序列化框架

### 开发工具

- **代码规范**: ESLint + Prettier + Clippy + rustfmt
- **版本控制**: Git
- **CI/CD**: GitHub Actions
- **包管理**: npm + Cargo

---

## 📊 开发进度

**当前版本**: v0.1.0

| Epic | 描述 | 进度 | 状态 |
|------|------|------|------|
| Epic 1 | 项目基础设施与核心文件上传 | 17% (1/6) | 🚧 进行中 |
| Epic 2 | 异步任务处理与状态监控 | 0% (0/5) | ⏳ 待开始 |
| Epic 3 | PDF 生成集成与文件关系可视化 | 0% (0/5) | ⏳ 待开始 |
| Epic 4 | PDF 预览与文件下载 | 0% (0/6) | ⏳ 待开始 |
| Epic 5 | 任务历史管理与持久化 | 0% (0/5) | ⏳ 待开始 |

**总体完成度**: 4% (1/27 Stories 完成)

详细开发进度：[Stories 索引](docs/stories/STORIES_INDEX.md)

---

## 🧪 测试

### 运行测试

```bash
# 前端测试 (待实现)
npm run test

# Rust 测试
cd src-tauri
cargo test
```

### 代码质量检查

```bash
# 前端检查
npm run lint              # ESLint
npm run format:check      # Prettier
npm run check             # TypeScript

# Rust 检查
cd src-tauri
cargo fmt -- --check      # 格式检查
cargo clippy -- -D warnings  # Clippy 分析
```

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 提交规范

本项目遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` - 新功能
- `fix:` - 问题修复
- `docs:` - 文档更新
- `style:` - 代码格式（不影响功能）
- `refactor:` - 重构
- `test:` - 测试相关
- `chore:` - 构建/工具链相关

---

## 📝 开发原则

本项目遵循以下软件工程最佳实践：

- **SOLID** - 面向对象设计原则
- **DRY** - 不重复代码 (Don't Repeat Yourself)
- **KISS** - 保持简单 (Keep It Simple, Stupid)
- **YAGNI** - 只实现需要的功能 (You Aren't Gonna Need It)

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🔗 相关链接

- 📘 [Tauri 官方文档](https://tauri.app/)
- 📘 [Svelte 官方文档](https://svelte.dev/)
- 📘 [Rust 官方文档](https://www.rust-lang.org/)
- 🐛 [问题反馈](https://github.com/your-username/cad-pdf-converter/issues)

---

## 👥 团队

- **产品经理**: John (PM)
- **架构师**: Winston (Architect)
- **测试架构师**: Quinn (Test Architect)
- **开发工程师**: James (Developer)

---

**⚡ 使用现代化技术栈构建，提供卓越的用户体验！**
