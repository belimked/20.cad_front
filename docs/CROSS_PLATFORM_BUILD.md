# 跨平台打包指南

**项目**: CAD PDF Converter
**更新时间**: 2025-11-07

---

## 🎯 跨平台打包方案

### ⚠️ 重要说明

**直接在一台机器上打包所有平台是不可能的**，因为：
- macOS 应用需要在 macOS 上打包（需要 Xcode 工具链）
- Windows 应用需要在 Windows 上打包（需要 Visual Studio 工具链）
- Linux 应用需要在 Linux 上打包（需要系统库）

但我们有以下解决方案：

---

## 🚀 方案 1: GitHub Actions CI/CD（推荐）

使用 GitHub Actions 在云端自动构建所有平台。

### 优点
- ✅ 完全自动化
- ✅ 同时构建 macOS、Windows、Linux
- ✅ 免费（GitHub 免费用户有限额）
- ✅ 每次 push 或 tag 自动构建

### 实施步骤

#### 1. 创建 GitHub Actions 工作流

创建文件 `.github/workflows/release.yml`:

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'  # 当推送 v* 标签时触发
  workflow_dispatch:  # 允许手动触发

jobs:
  build:
    name: Build ${{ matrix.platform }}

    strategy:
      fail-fast: false
      matrix:
        platform:
          - macos-latest    # macOS (Intel + Apple Silicon)
          - windows-latest  # Windows
          - ubuntu-latest   # Linux

    runs-on: ${{ matrix.platform }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: |
            aarch64-apple-darwin
            x86_64-apple-darwin
            x86_64-pc-windows-msvc
            x86_64-unknown-linux-gnu

      - name: Install dependencies (Ubuntu)
        if: matrix.platform == 'ubuntu-latest'
        run: |
          sudo apt-get update
          sudo apt-get install -y libwebkit2gtk-4.0-dev \
            build-essential \
            curl \
            wget \
            libssl-dev \
            libgtk-3-dev \
            libayatana-appindicator3-dev \
            librsvg2-dev

      - name: Install frontend dependencies
        run: npm install

      - name: Build application
        run: npm run tauri:build

      - name: Upload macOS DMG
        if: matrix.platform == 'macos-latest'
        uses: actions/upload-artifact@v4
        with:
          name: macos-dmg
          path: src-tauri/target/release/bundle/dmg/*.dmg

      - name: Upload macOS App
        if: matrix.platform == 'macos-latest'
        uses: actions/upload-artifact@v4
        with:
          name: macos-app
          path: src-tauri/target/release/bundle/macos/*.app

      - name: Upload Windows MSI
        if: matrix.platform == 'windows-latest'
        uses: actions/upload-artifact@v4
        with:
          name: windows-msi
          path: src-tauri/target/release/bundle/msi/*.msi

      - name: Upload Linux AppImage
        if: matrix.platform == 'ubuntu-latest'
        uses: actions/upload-artifact@v4
        with:
          name: linux-appimage
          path: src-tauri/target/release/bundle/appimage/*.AppImage

      - name: Upload Linux DEB
        if: matrix.platform == 'ubuntu-latest'
        uses: actions/upload-artifact@v4
        with:
          name: linux-deb
          path: src-tauri/target/release/bundle/deb/*.deb

  release:
    name: Create Release
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')

    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            macos-dmg/*
            macos-app/*
            windows-msi/*
            linux-appimage/*
            linux-deb/*
          draft: true
          generate_release_notes: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### 2. 使用方法

**方式 1: 创建 Git Tag 触发**
```bash
# 创建标签
git tag v0.1.0
git push origin v0.1.0

# GitHub Actions 会自动构建所有平台并创建 Release
```

**方式 2: 手动触发**
1. 进入 GitHub 仓库
2. Actions → Release Build → Run workflow
3. 选择分支并运行

#### 3. 下载构建产物

构建完成后：
1. 进入 Actions 页面
2. 点击对应的工作流运行
3. 在 Artifacts 区域下载各平台的安装包

---

## 🛠️ 方案 2: tauri-action（更简单）

使用官方的 `tauri-action`，配置更简单。

创建 `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    permissions:
      contents: write
    strategy:
      fail-fast: false
      matrix:
        platform: [macos-latest, ubuntu-20.04, windows-latest]

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install Rust stable
        uses: dtolnay/rust-toolchain@stable

      - name: Install dependencies (ubuntu only)
        if: matrix.platform == 'ubuntu-20.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev \
            libappindicator3-dev librsvg2-dev patchelf

      - name: Install frontend dependencies
        run: npm install

      - uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'CAD PDF Converter v__VERSION__'
          releaseBody: 'See the assets to download this version and install.'
          releaseDraft: true
          prerelease: false
```

---

## 🖥️ 方案 3: 本地跨平台编译（有限支持）

### macOS → Windows（使用 Wine）

**不推荐**，因为：
- 需要安装 Wine 和 mingw
- 兼容性问题多
- 编译慢且不稳定

### 使用 Docker（仅 Linux）

可以在 macOS 上使用 Docker 构建 Linux 版本：

```bash
# 创建 Dockerfile
cat > Dockerfile.linux <<'EOF'
FROM rust:latest

RUN apt-get update && apt-get install -y \
    libwebkit2gtk-4.0-dev \
    build-essential \
    curl \
    wget \
    libssl-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev \
    nodejs \
    npm

WORKDIR /app
COPY . .

RUN npm install
RUN npm run tauri:build

CMD ["bash"]
EOF

# 构建 Docker 镜像
docker build -f Dockerfile.linux -t cad-pdf-builder .

# 运行并提取构建产物
docker run --rm -v $(pwd)/output:/output cad-pdf-builder \
  cp -r src-tauri/target/release/bundle /output
```

---

## 📦 方案 4: 云端构建服务

### 4.1 使用 Tauri Plugin

安装 `@tauri-apps/cli` 的云构建功能（未来特性）

### 4.2 使用第三方 CI/CD

**CircleCI**:
```yaml
version: 2.1

orbs:
  node: circleci/node@5.0
  rust: circleci/rust@1.6

workflows:
  build-all:
    jobs:
      - build-macos
      - build-windows
      - build-linux

jobs:
  build-macos:
    macos:
      xcode: 14.0.0
    steps:
      - checkout
      - node/install
      - rust/install
      - run: npm install
      - run: npm run tauri:build

  build-windows:
    machine:
      image: windows-server-2022
    steps:
      - checkout
      - run: npm install
      - run: npm run tauri:build

  build-linux:
    docker:
      - image: cimg/rust:1.75
    steps:
      - checkout
      - run: npm install
      - run: npm run tauri:build
```

**Travis CI**、**AppVeyor** 等也支持类似配置。

---

## 🎯 推荐方案对比

| 方案 | 难度 | 成本 | 速度 | 推荐度 |
|------|------|------|------|--------|
| GitHub Actions | ⭐⭐ | 免费 | 快 | ⭐⭐⭐⭐⭐ |
| tauri-action | ⭐ | 免费 | 快 | ⭐⭐⭐⭐⭐ |
| Docker (仅 Linux) | ⭐⭐⭐ | 免费 | 慢 | ⭐⭐ |
| 云端 CI/CD | ⭐⭐⭐ | 收费 | 中 | ⭐⭐⭐ |
| 本地交叉编译 | ⭐⭐⭐⭐⭐ | 免费 | 慢 | ⭐ |

---

## 🚀 快速开始（GitHub Actions）

### 步骤 1: 创建工作流文件

```bash
mkdir -p .github/workflows
# 复制上面的 tauri-action 配置到该文件
nano .github/workflows/release.yml
```

### 步骤 2: 提交并推送

```bash
git add .github/workflows/release.yml
git commit -m "ci: add cross-platform build workflow"
git push
```

### 步骤 3: 创建 Release Tag

```bash
git tag v0.1.0
git push origin v0.1.0
```

### 步骤 4: 等待构建完成

1. 访问 `https://github.com/用户名/仓库名/actions`
2. 查看构建进度
3. 下载各平台安装包

---

## 📊 构建时间预估

| 平台 | GitHub Actions 时间 |
|------|---------------------|
| macOS | 8-12 分钟 |
| Windows | 10-15 分钟 |
| Linux | 6-10 分钟 |
| **总计（并行）** | **10-15 分钟** |

---

## 🔧 高级配置

### 仅构建特定平台

```yaml
strategy:
  matrix:
    platform:
      - macos-latest   # 仅 macOS
      # - windows-latest  # 注释掉 Windows
      # - ubuntu-latest   # 注释掉 Linux
```

### 构建 macOS Universal Binary（Intel + Apple Silicon）

在 `tauri.conf.json` 中配置:

```json
{
  "tauri": {
    "bundle": {
      "macOS": {
        "targets": ["universal"]
      }
    }
  }
}
```

### 添加代码签名（GitHub Secrets）

```yaml
- uses: tauri-apps/tauri-action@v0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
    APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
```

---

## 🐛 常见问题

### Q1: GitHub Actions 构建失败

**检查**:
1. Rust 版本是否正确
2. Node.js 版本是否满足要求
3. 查看 Actions 日志中的具体错误

### Q2: 构建时间太长

**优化**:
1. 使用缓存加速依赖安装
2. 仅在 tag 时构建，不在每次 push 时构建
3. 使用 `fail-fast: false` 避免一个平台失败导致全部终止

### Q3: 如何本地测试 GitHub Actions

使用 `act` 工具:

```bash
# 安装 act
brew install act

# 本地运行 workflow
act -j build
```

---

## ✅ 最佳实践

1. **使用语义化版本标签**: `v1.0.0`, `v1.0.1` 等
2. **创建 Draft Release**: 在发布前检查所有平台的构建产物
3. **添加 CHANGELOG**: 记录每个版本的变更
4. **设置构建缓存**: 加速后续构建
5. **启用通知**: 构建完成后发送邮件通知

---

## 📚 参考资源

- [Tauri GitHub Actions 官方指南](https://tauri.app/v1/guides/building/cross-platform)
- [tauri-action 文档](https://github.com/tauri-apps/tauri-action)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

**文档版本**: v1.0
**最后更新**: 2025-11-07
**维护者**: Winston
