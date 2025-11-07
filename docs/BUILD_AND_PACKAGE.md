# Tauri 应用打包指南

**项目**: CAD PDF Converter
**平台**: Windows、macOS、Linux
**更新时间**: 2025-11-07

---

## 📦 快速打包

### 基础打包命令

```bash
# 使用 npm
npm run tauri:build

# 或使用 pnpm
pnpm tauri:build
```

这将自动完成：
1. 编译前端代码（Vite build）
2. 编译 Rust 后端（Release 模式）
3. 生成平台特定的安装包

---

## 🎯 打包产物位置

### macOS
```
src-tauri/target/release/bundle/
├── dmg/                    # macOS 磁盘映像
│   └── CAD PDF Converter_0.1.0_aarch64.dmg  (Apple Silicon)
│   └── CAD PDF Converter_0.1.0_x64.dmg      (Intel)
└── macos/                  # .app 应用包
    └── CAD PDF Converter.app
```

### Windows
```
src-tauri/target/release/bundle/
├── msi/                    # Windows 安装器
│   └── CAD PDF Converter_0.1.0_x64_en-US.msi
└── nsis/                   # NSIS 安装器（可选）
    └── CAD PDF Converter_0.1.0_x64-setup.exe
```

### Linux
```
src-tauri/target/release/bundle/
├── appimage/               # AppImage 便携包
│   └── cad-pdf-converter_0.1.0_amd64.AppImage
└── deb/                    # Debian 安装包
    └── cad-pdf-converter_0.1.0_amd64.deb
```

---

## 🛠️ 打包前准备

### 1. 配置应用信息

编辑 `src-tauri/tauri.conf.json`:

```json
{
  "package": {
    "productName": "CAD PDF Converter",
    "version": "0.1.0"  // 更新版本号
  },
  "tauri": {
    "bundle": {
      "identifier": "com.yourcompany.cad-pdf-converter",  // ⚠️ 必须修改
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",    // macOS
        "icons/icon.ico"       // Windows
      ]
    }
  }
}
```

### 2. 准备应用图标

**所需图标文件**:
- `src-tauri/icons/32x32.png` - 32×32 像素
- `src-tauri/icons/128x128.png` - 128×128 像素
- `src-tauri/icons/128x128@2x.png` - 256×256 像素
- `src-tauri/icons/icon.icns` - macOS 图标（自动生成）
- `src-tauri/icons/icon.ico` - Windows 图标（自动生成）

**生成图标**:
```bash
# 从一张 PNG 图片自动生成所有格式
npm install -g @tauri-apps/cli
npx tauri icon /path/to/your/icon.png
```

### 3. 更新版本号

**三个文件需要同步**:

`package.json`:
```json
{
  "version": "0.1.0"
}
```

`src-tauri/Cargo.toml`:
```toml
[package]
version = "0.1.0"
```

`src-tauri/tauri.conf.json`:
```json
{
  "package": {
    "version": "0.1.0"
  }
}
```

---

## 🔧 高级打包选项

### 指定目标平台

```bash
# macOS Apple Silicon
npm run tauri build -- --target aarch64-apple-darwin

# macOS Intel
npm run tauri build -- --target x86_64-apple-darwin

# Windows
npm run tauri build -- --target x86_64-pc-windows-msvc

# Linux
npm run tauri build -- --target x86_64-unknown-linux-gnu
```

### 仅构建特定格式

编辑 `src-tauri/tauri.conf.json`:

```json
{
  "tauri": {
    "bundle": {
      "active": true,
      "targets": ["dmg"],  // 仅生成 DMG (macOS)
      // 或 ["msi"] (Windows)
      // 或 ["appimage", "deb"] (Linux)
    }
  }
}
```

### Debug 模式打包（用于调试）

```bash
npm run tauri build -- --debug
```

产物位于 `src-tauri/target/debug/bundle/`

---

## 📋 完整打包流程

### 步骤 1: 清理旧构建

```bash
# 清理前端构建
rm -rf dist/

# 清理 Rust 构建（可选，会导致重新编译）
cd src-tauri
cargo clean
cd ..
```

### 步骤 2: 验证代码

```bash
# 检查 TypeScript 类型
npm run check

# 检查代码规范
npm run lint

# Rust 代码检查
cd src-tauri
cargo clippy
cargo fmt --check
cd ..
```

### 步骤 3: 执行打包

```bash
# 生产环境打包
npm run tauri:build
```

### 步骤 4: 测试安装包

**macOS**:
1. 打开生成的 `.dmg` 文件
2. 将 `.app` 拖到 Applications
3. 运行并验证功能

**Windows**:
1. 运行 `.msi` 安装器
2. 完成安装向导
3. 从开始菜单启动

**Linux**:
```bash
# AppImage
chmod +x *.AppImage
./*.AppImage

# Debian
sudo dpkg -i *.deb
```

---

## 🎨 自定义安装器

### macOS DMG 背景图

创建 `src-tauri/icons/dmg-background.png` (1000×600 像素)

在 `tauri.conf.json` 中配置:
```json
{
  "tauri": {
    "bundle": {
      "macOS": {
        "dmg": {
          "background": "icons/dmg-background.png",
          "windowSize": {
            "width": 660,
            "height": 400
          }
        }
      }
    }
  }
}
```

### Windows NSIS 安装器

在 `tauri.conf.json` 中启用:
```json
{
  "tauri": {
    "bundle": {
      "targets": ["msi", "nsis"],
      "windows": {
        "wix": {
          "language": "zh-CN"  // 中文安装界面
        }
      }
    }
  }
}
```

---

## ⚙️ 优化打包大小

### 1. Rust 优化

编辑 `src-tauri/Cargo.toml`:

```toml
[profile.release]
opt-level = "z"        # 优化大小
lto = true             # 链接时优化
codegen-units = 1      # 减少并行编译单元
panic = "abort"        # 减少 panic 处理代码
strip = true           # 移除符号信息
```

预期效果：减少 30-50% 体积

### 2. 前端优化

编辑 `vite.config.ts`:

```typescript
export default defineConfig({
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 移除 console
        drop_debugger: true  // 移除 debugger
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte']  // 分离第三方库
        }
      }
    }
  }
});
```

### 3. 移除未使用的依赖

```bash
# 分析依赖大小
npm install -g depcheck
depcheck

# 移除未使用的包
npm uninstall <package-name>
```

---

## 🔐 代码签名

### macOS 签名

**前提条件**:
- Apple Developer 账号
- 开发者证书

**配置**:
```bash
# 在 tauri.conf.json 中
{
  "tauri": {
    "bundle": {
      "macOS": {
        "signingIdentity": "Developer ID Application: Your Name (TEAM_ID)",
        "entitlements": "path/to/entitlements.plist"
      }
    }
  }
}
```

**签名命令**:
```bash
# Tauri 自动签名
npm run tauri build

# 手动签名
codesign --force --deep --sign "Developer ID Application" \
  "src-tauri/target/release/bundle/macos/CAD PDF Converter.app"
```

### Windows 签名

**使用 SignTool**:
```bash
# 需要证书文件 (.pfx)
signtool sign /f certificate.pfx /p password \
  /t http://timestamp.digicert.com \
  "src-tauri/target/release/bundle/msi/*.msi"
```

---

## 🚀 自动化打包 (CI/CD)

### GitHub Actions 示例

创建 `.github/workflows/build.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        platform: [macos-latest, windows-latest, ubuntu-latest]

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install dependencies
        run: npm install

      - name: Build
        run: npm run tauri build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ matrix.platform }}
          path: src-tauri/target/release/bundle/
```

---

## 📊 打包统计

### 典型文件大小（参考）

| 平台 | 格式 | 大小范围 |
|------|------|---------|
| macOS | .dmg | 8-15 MB |
| Windows | .msi | 6-12 MB |
| Linux | .AppImage | 10-18 MB |
| Linux | .deb | 6-12 MB |

实际大小取决于：
- 依赖的 Rust crates
- 前端资源大小
- 是否启用优化

### 编译时间（首次）

| 平台 | 时间 |
|------|------|
| macOS (M1/M2) | 3-5 分钟 |
| macOS (Intel) | 5-8 分钟 |
| Windows | 5-10 分钟 |
| Linux | 4-7 分钟 |

后续编译会显著加快（增量编译）。

---

## 🐛 常见问题

### 问题 1: 打包失败 - 缺少图标

**症状**:
```
Error: Could not find icon at path: icons/icon.icns
```

**解决**:
```bash
# 使用默认图标或生成图标
npx tauri icon /path/to/icon.png
```

### 问题 2: Windows 签名失败

**症状**:
```
Error: Failed to sign the installer
```

**解决**:
- 检查证书是否有效
- 确保时间戳服务器可访问
- 或在 `tauri.conf.json` 中禁用签名（开发阶段）

### 问题 3: macOS 无法打开（安全限制）

**症状**: "无法打开，因为它来自身份不明的开发者"

**解决**:
```bash
# 用户端解决
xattr -cr /Applications/CAD\ PDF\ Converter.app

# 开发者解决：进行代码签名
```

### 问题 4: Linux 依赖缺失

**症状**:
```
Error: libwebkit2gtk-4.0.so.37: cannot open shared object file
```

**解决**:
```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install webkit2gtk3-devel
```

---

## 📚 参考资源

### 官方文档
- [Tauri 打包指南](https://tauri.app/v1/guides/building/)
- [跨平台编译](https://tauri.app/v1/guides/building/cross-platform)
- [应用签名](https://tauri.app/v1/guides/distribution/sign-macos)

### 工具
- [tauri-action](https://github.com/tauri-apps/tauri-action) - GitHub Actions
- [create-tauri-app](https://github.com/tauri-apps/create-tauri-app) - 脚手架工具

---

## ✅ 打包检查清单

发布前确保：

- [ ] 已更新版本号（3 个文件）
- [ ] 已准备应用图标
- [ ] 已修改 bundle identifier
- [ ] 已运行代码检查 (lint, clippy)
- [ ] 已测试核心功能
- [ ] 已在目标平台测试安装包
- [ ] 已准备 CHANGELOG.md
- [ ] 已准备发布说明
- [ ] （可选）已进行代码签名
- [ ] （可选）已配置自动更新

---

**文档版本**: v1.0
**最后更新**: 2025-11-07
**维护者**: Winston (架构师)
