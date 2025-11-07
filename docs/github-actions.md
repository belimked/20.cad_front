# GitHub Actions 自动构建文档

## 概述

本项目配置了两个 GitHub Actions workflow：
1. **CI** - 代码质量检查（每次 push 触发）
2. **Release Build** - 多平台构建和发布（tag 触发或手动触发）

---

## CI Workflow

### 触发条件
- Push 到 `main`、`master` 或 `develop` 分支
- Pull Request 到 `main` 或 `master` 分支

### 执行任务
1. **Lint and Test** (Ubuntu)
   - ESLint 检查
   - Prettier 格式检查
   - TypeScript 类型检查

2. **Rust Check** (Ubuntu)
   - Rust 代码格式检查 (rustfmt)
   - Clippy 静态分析
   - Release 模式构建测试

### 查看结果
每次 push 后可在 GitHub 仓库的 "Actions" 标签页查看检查结果。

---

## Release Build Workflow

### 触发条件
**方式 1：创建 Git Tag（推荐）**
```bash
# 创建版本 tag
git tag v1.0.0

# 推送 tag 到 GitHub
git push origin v1.0.0
```

**方式 2：手动触发**
1. 访问 GitHub 仓库页面
2. 进入 "Actions" 标签页
3. 选择 "Release Build" workflow
4. 点击 "Run workflow" 按钮
5. 选择分支并运行

### 构建平台
自动为以下三个平台构建安装包：

| 平台 | 构建产物 | 文件格式 |
|------|---------|---------|
| **macOS** | Universal Binary (支持 Intel 和 Apple Silicon) | `.dmg`, `.app.tar.gz` |
| **Windows** | x86_64 | `.msi`, `.exe` |
| **Linux** | x86_64 | `.deb`, `.AppImage` |

### 构建时间
- macOS: ~15-20 分钟
- Windows: ~10-15 分钟
- Linux: ~8-12 分钟

### 下载产物
1. 构建完成后，进入 GitHub "Releases" 页面
2. 找到对应版本的 Release（Draft 状态）
3. 查看并下载对应平台的安装包
4. 测试完成后，编辑 Release 并取消 Draft 状态即可发布

---

## 优化特性

### 1. macOS Universal Binary
macOS 构建使用 `--target universal-apple-darwin` 参数，生成同时支持 Intel 和 Apple Silicon 的通用二进制文件。

### 2. 缓存优化
- **npm 依赖缓存**: 加速前端依赖安装
- **Rust 编译缓存**: 显著减少 Rust 代码重新编译时间

### 3. 依赖管理
- 使用 `npm ci` 替代 `npm install`，确保依赖版本一致性

### 4. 自动发布
构建完成后自动创建 GitHub Release（Draft 状态），包含所有平台的安装包。

---

## 使用示例

### 发布新版本完整流程

```bash
# 1. 确保代码已提交
git add .
git commit -m "feat: 完成 Epic 1 实现"

# 2. 推送到主分支
git push origin master

# 3. 等待 CI 检查通过（查看 Actions 页面）

# 4. 创建版本 tag
git tag v1.0.0

# 5. 推送 tag 触发构建
git push origin v1.0.0

# 6. 等待 15-20 分钟（所有平台构建完成）

# 7. 访问 Releases 页面下载测试

# 8. 测试通过后，发布 Release
```

### 仅构建不发布
如果只想测试构建流程：
1. 使用 "workflow_dispatch" 手动触发
2. 构建完成后，Release 保持 Draft 状态
3. 测试完成后可删除 Draft Release

---

## 故障排查

### CI 失败常见原因
1. **ESLint 错误**: 运行 `npm run lint` 查看具体错误
2. **TypeScript 错误**: 运行 `npm run check` 检查类型错误
3. **Rust Clippy 警告**: 运行 `cd src-tauri && cargo clippy`

### 构建失败常见原因
1. **依赖问题**: 检查 `package.json` 和 `Cargo.toml` 依赖是否正确
2. **Tauri 配置错误**: 检查 `src-tauri/tauri.conf.json`
3. **平台特定问题**: 查看 Actions 日志中对应平台的错误信息

### 查看详细日志
1. 进入 "Actions" 页面
2. 点击失败的 workflow run
3. 展开失败的 step 查看详细错误信息

---

## 高级配置

### 修改构建触发分支
编辑 `.github/workflows/release.yml`:
```yaml
on:
  push:
    branches:
      - main        # 修改为你的主分支名称
      - production  # 添加其他分支
```

### 修改 Release 名称格式
编辑 `.github/workflows/release.yml`:
```yaml
with:
  releaseName: 'CAD PDF Converter v__VERSION__'  # 自定义名称
  releaseBody: |                                   # 多行描述
    ## What's Changed
    - Feature 1
    - Feature 2
```

### 添加代码签名（macOS/Windows）
需要在 GitHub 仓库 Settings > Secrets 中添加签名证书：
- macOS: `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`
- Windows: `WINDOWS_CERTIFICATE`, `WINDOWS_CERTIFICATE_PASSWORD`

详见 [Tauri 官方文档](https://tauri.app/v1/guides/distribution/sign-macos)

---

## 性能优化建议

1. **并行构建**: GitHub Actions 自动并行执行三个平台的构建
2. **缓存利用**: 首次构建后，后续构建时间可减少 50%+
3. **增量构建**: 仅修改前端代码时，Rust 编译缓存可节省大量时间

---

## 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Tauri Action](https://github.com/tauri-apps/tauri-action)
- [Rust Cache Action](https://github.com/Swatinem/rust-cache)

---

**最后更新**: 2025-11-07
