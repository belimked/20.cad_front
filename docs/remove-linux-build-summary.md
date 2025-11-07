# 移除 Linux 构建配置 - 更新总结

**更新时间**: 2025-11-07
**提交**: ddbc6bc

## 📝 变更内容

### 修改的文件

**`.github/workflows/release.yml`**:
- ✅ 移除 `ubuntu-20.04` 构建平台
- ✅ 移除 Linux 依赖安装步骤
- ✅ 保留 macOS (Universal Binary) 和 Windows 构建

**保留不变**:
- `.github/workflows/ci.yml` - 继续使用 Ubuntu 进行代码质量检查（快速且免费）

### 更新的文档

1. `docs/build-status.md`
   - 更新构建平台列表
   - 修改预期构建产物
   - 添加 Linux 从源码构建说明

2. `docs/build-progress-summary.md`
   - 更新预期构建产物列表
   - 调整时间估算
   - 更新成功标准（2个平台，4个安装包）

3. `TAURI_README.md`
   - 添加 GitHub Actions 状态徽章

## 🎯 构建配置

### 发布平台（仅2个）

| 平台 | Runner | 构建目标 | 产物 |
|------|--------|---------|------|
| macOS | macos-latest | Universal Binary | .dmg, .app.tar.gz |
| Windows | windows-latest | x64 | .msi, .exe |

### CI 平台（用于代码检查）

| 平台 | Runner | 用途 |
|------|--------|------|
| Ubuntu | ubuntu-latest | ESLint, Prettier, TypeScript, Rust 格式/Clippy 检查 |

## 📦 预期构建产物

Release `v0.1.0-beta` 将包含 **4 个文件**:

```
v0.1.0-beta/
├── CAD-PDF-Converter_0.1.0-beta_universal.dmg         (macOS)
├── cad-pdf-converter.app.tar.gz                       (macOS)
├── CAD-PDF-Converter_0.1.0-beta_x64_en-US.msi         (Windows)
└── CAD-PDF-Converter_0.1.0-beta_x64-setup.exe         (Windows)
```

## ⏱️ 预计构建时间

- **macOS**: 15-20 分钟
- **Windows**: 10-15 分钟
- **并行总时间**: 15-20 分钟（取决于较慢的平台）

## 🔄 Git 状态

### 远程状态
```bash
$ git ls-remote github | grep -E "(cad_front|v0.1.0-beta)"
ddbc6bc646330202b3ae1a869978f16893cb5c08	refs/heads/cad_front
ddbc6bc646330202b3ae1a869978f16893cb5c08	refs/tags/v0.1.0-beta
```

### 本地提交
```
ddbc6bc ci: 移除 Linux 平台构建，仅保留 macOS 和 Windows
0600a60 fix: 添加 Ubuntu libsoup 和 JavaScriptCore 依赖
57481ff style: 修复 Rust 代码格式问题 (cargo fmt)
```

## ✅ 已推送到 GitHub

- ✅ cad_front 分支: `ddbc6bc`
- ✅ v0.1.0-beta tag: `ddbc6bc`

## 🚀 触发的构建

新的 GitHub Actions 构建将自动触发:

1. **CI #10** (cad_front 分支推送)
   - 代码质量检查
   - 预计 3-5 分钟

2. **Release Build #21** (v0.1.0-beta tag)
   - macOS 构建
   - Windows 构建
   - ~~Linux 构建~~（已移除）

## 📋 下一步

1. **等待构建触发** - GitHub Actions 正在处理推送事件
2. **监控构建进度** - 使用以下方式之一:
   - Web: https://github.com/belimked/20.cad_front/actions
   - 脚本: `./scripts/check-build-status.sh`
   - 持续监控: `./scripts/monitor-build.sh`

3. **验证构建结果**:
   - 确认只有 macOS 和 Windows 两个平台在构建
   - 检查是否生成 4 个安装包
   - 下载并测试安装包

## 💡 Linux 用户说明

如果需要在 Linux 上运行,可以从源码构建:

```bash
# 安装依赖
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-dev \
    libappindicator3-dev librsvg2-dev patchelf \
    libsoup-3.0-dev libjavascriptcoregtk-4.1-dev

# 克隆并构建
git clone https://github.com/belimked/20.cad_front.git
cd 20.cad_front
npm install
npm run tauri:build

# 产物位置
# src-tauri/target/release/bundle/deb/
# src-tauri/target/release/bundle/appimage/
```

## 🔗 相关链接

- **Actions**: https://github.com/belimked/20.cad_front/actions
- **Releases**: https://github.com/belimked/20.cad_front/releases
- **提交详情**: https://github.com/belimked/20.cad_front/commit/ddbc6bc

---

**状态**: ✅ 配置已更新并推送
**等待**: GitHub Actions 触发新构建
