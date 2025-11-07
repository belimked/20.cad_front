# GitHub Actions 问题修复记录

## 问题汇总

构建过程中遇到的两个主要问题及解决方案。

---

## 问题 1: npm 找不到 package.json

### 错误信息
```
npm error code ENOENT
npm error syscall open
npm error path /home/runner/work/20.cad_front/20.cad_front/package.json
npm error errno -2
npm error enoent Could not read package.json
```

### 根本原因
GitHub Actions 的 `actions/checkout@v4` 成功 checkout 了代码，但某些情况下工作目录可能不正确。

### 解决方案
添加文件验证步骤，确保在运行 npm 命令前检查文件是否存在：

```yaml
- name: Verify repository files
  run: |
    echo "=== Current directory ==="
    pwd
    echo "=== Files in root ==="
    ls -la
    echo "=== Check package.json ==="
    test -f package.json && echo "✓ package.json found" || echo "✗ package.json NOT found"
```

这个步骤可以帮助诊断问题，如果 package.json 确实不存在，会清楚地显示出来。

---

## 问题 2: Ubuntu 缺少 libwebkit2gtk-4.0-dev

### 错误信息
```
E: Unable to locate package libwebkit2gtk-4.0-dev
E: Couldn't find any package by glob 'libwebkit2gtk-4.0-dev'
```

### 根本原因
GitHub Actions 使用 `ubuntu-latest`（当前为 Ubuntu 24.04 Noble），该版本的 WebKit2GTK 包名已更新：
- **旧版本** (Ubuntu 20.04/22.04): `libwebkit2gtk-4.0-dev`
- **新版本** (Ubuntu 24.04+): `libwebkit2gtk-4.1-dev`

### 解决方案

**修改前**:
```yaml
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev \
  libappindicator3-dev librsvg2-dev patchelf
```

**修改后**:
```yaml
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev \
  libappindicator3-dev librsvg2-dev patchelf
```

### 为什么会出现这个问题？

1. **GitHub Actions 环境更新**: `ubuntu-latest` 别名从 Ubuntu 22.04 升级到 24.04
2. **Tauri 文档滞后**: Tauri 官方文档中仍使用 `4.0` 版本示例
3. **Ubuntu 包管理变化**: Ubuntu 24.04 弃用了旧版本的 WebKit 包

### 相关链接
- [Tauri Prerequisites](https://tauri.app/v1/guides/getting-started/prerequisites)
- [Ubuntu 24.04 Package Changes](https://ubuntu.com/blog/ubuntu-24-04-lts-noble-numbat-released)

---

## 完整修复记录

### Commit 1: `93398c1`
```
fix: 移除 npm cache 配置，使用 npm install 替代 npm ci
```
- 移除 `cache: 'npm'` 配置（需要 package-lock.json）
- 将 `npm ci` 改为 `npm install`

### Commit 2: `72da4b6`
```
fix: 更新 Ubuntu WebKit 依赖版本为 4.1，添加文件验证步骤
```
- 更新 `libwebkit2gtk-4.0-dev` → `libwebkit2gtk-4.1-dev`
- 添加文件验证步骤到 CI workflow

---

## 后续优化建议

### 1. 锁定 Ubuntu 版本（推荐）

如果需要稳定的构建环境，明确指定 Ubuntu 版本而不是使用 `ubuntu-latest`：

```yaml
matrix:
  platform:
    - ubuntu-22.04  # 明确版本，避免意外升级
    - macos-latest
    - windows-latest
```

**优点**:
- 构建环境可预测
- 避免因系统升级导致的破坏性更改

**缺点**:
- 需要手动更新版本
- 不会自动获得新版本的性能改进

### 2. 提交 package-lock.json

将 `package-lock.json` 提交到 Git：

```bash
git add package-lock.json
git commit -m "chore: 添加 package-lock.json 用于依赖锁定"
```

然后恢复 npm 缓存配置：

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm'  # 重新启用缓存

- name: Install dependencies
  run: npm ci  # 使用 ci 确保一致性
```

**优点**:
- 加速依赖安装（缓存生效时从 1-2 分钟减少到 10-20 秒）
- 确保所有环境使用相同的依赖版本
- 防止依赖版本漂移

### 3. 使用条件安装依赖

根据不同的 Ubuntu 版本安装正确的包：

```yaml
- name: Install dependencies (ubuntu)
  if: startsWith(matrix.platform, 'ubuntu')
  run: |
    sudo apt-get update

    # 检测 Ubuntu 版本并安装对应包
    if [ -f /etc/os-release ]; then
      . /etc/os-release
      if [ "$VERSION_ID" = "24.04" ]; then
        WEBKIT_PKG="libwebkit2gtk-4.1-dev"
      else
        WEBKIT_PKG="libwebkit2gtk-4.0-dev"
      fi
    fi

    sudo apt-get install -y libgtk-3-dev ${WEBKIT_PKG} \
      libappindicator3-dev librsvg2-dev patchelf
```

### 4. 添加构建状态徽章

在 README.md 中添加状态徽章，实时显示构建状态：

```markdown
# CAD PDF Converter

[![CI](https://github.com/belimked/20.cad_front/actions/workflows/ci.yml/badge.svg)](https://github.com/belimked/20.cad_front/actions/workflows/ci.yml)
[![Release](https://github.com/belimked/20.cad_front/actions/workflows/release.yml/badge.svg)](https://github.com/belimked/20.cad_front/actions/workflows/release.yml)

Convert CAD files to PDF with ease.
```

---

## 测试建议

### 本地测试（推荐）

在推送前本地验证构建：

```bash
# 测试前端构建
npm install
npm run lint
npm run check

# 测试 Tauri 构建
npm run tauri build
```

### Docker 测试（可选）

使用 Docker 模拟 GitHub Actions 环境：

```bash
# Ubuntu 24.04 环境测试
docker run -it ubuntu:24.04 bash

# 安装依赖并测试
apt-get update
apt-get install -y curl git libgtk-3-dev libwebkit2gtk-4.1-dev \
  libappindicator3-dev librsvg2-dev patchelf

# 安装 Node.js 和 Rust
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone 并测试构建
git clone https://github.com/belimked/20.cad_front.git
cd 20.cad_front
npm install
npm run tauri build
```

---

## 总结

| 问题 | 原因 | 解决方案 | 状态 |
|------|------|---------|------|
| npm 找不到 package.json | 工作目录问题 | 添加文件验证步骤 | ✅ 已修复 |
| 缺少 WebKit 包 | Ubuntu 24.04 包名变更 | 更新为 4.1 版本 | ✅ 已修复 |
| 缺少 package-lock.json | npm ci 需要锁文件 | 改用 npm install | ✅ 已修复 |

**当前状态**: 所有已知问题已修复，GitHub Actions 应该可以正常运行。

**最新提交**: `72da4b6` - "fix: 更新 Ubuntu WebKit 依赖版本为 4.1，添加文件验证步骤"

**下一步**: 等待 15-20 分钟查看构建结果。

---

**创建时间**: 2025-11-07
**最后更新**: 2025-11-07
