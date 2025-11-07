# Git 双远程仓库配置指南

## 当前配置

**本地私有 Git 服务器**:
- Remote 名称: `origin`
- URL: `http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git`

---

## 配置方案

### 方案 1：添加 GitHub 作为第二个远程仓库（推荐）

这种方案保持现有 `origin` 不变，添加 `github` 作为额外的远程仓库。

#### Step 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 创建新仓库（可以是私有或公开）
3. **不要**初始化 README、.gitignore 或 LICENSE（避免冲突）
4. 复制仓库 URL，例如：`https://github.com/username/cad-pdf-converter.git`

#### Step 2: 添加 GitHub 远程仓库

```bash
# 添加 GitHub 为新的远程仓库
git remote add github https://github.com/username/cad-pdf-converter.git

# 验证远程仓库配置
git remote -v
```

结果应该显示：
```
origin    http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git (fetch)
origin    http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git (push)
github    https://github.com/username/cad-pdf-converter.git (fetch)
github    https://github.com/username/cad-pdf-converter.git (push)
```

#### Step 3: 推送代码到 GitHub

```bash
# 首次推送（设置上游分支）
git push -u github master

# 或者推送所有分支
git push github --all

# 推送所有 tags
git push github --tags
```

#### Step 4: 日常使用

**推送到本地私有服务器**:
```bash
git push origin master
```

**推送到 GitHub**:
```bash
git push github master
```

**同时推送到两个远程仓库**:
```bash
git push origin master && git push github master
```

---

### 方案 2：配置 origin 同时推送到两个仓库

这种方案让 `git push` 自动推送到两个远程仓库。

#### Step 1: 添加 GitHub 作为 origin 的第二个推送地址

```bash
# 添加 GitHub URL 到 origin 的推送列表
git remote set-url --add --push origin https://github.com/username/cad-pdf-converter.git

# 添加本地服务器 URL 到 origin 的推送列表
git remote set-url --add --push origin http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git
```

#### Step 2: 验证配置

```bash
git remote -v
```

结果应该显示：
```
origin    http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git (fetch)
origin    http://10.3.19.191:8080/git/BLK/100.AI.TrainData.git (push)
origin    https://github.com/username/cad-pdf-converter.git (push)
```

#### Step 3: 使用

```bash
# 一次推送，自动推送到两个远程仓库
git push origin master
```

⚠️ **注意**：这种方案的缺点是，如果一个仓库推送失败，可能导致两个仓库不同步。

---

### 方案 3：使用 Git Alias 简化操作（推荐）

结合方案 1，创建 alias 简化同时推送操作。

```bash
# 添加 alias 到 Git 配置
git config --global alias.pushall '!git push origin master && git push github master'

# 使用 alias 同时推送
git pushall
```

或者为当前仓库配置（不影响其他项目）：
```bash
git config alias.pushall '!git push origin master && git push github master'
```

---

## GitHub Actions 配置

### 方案 A：仅 GitHub 触发 CI/CD（推荐）

**优点**: 简单，利用 GitHub 的免费 CI/CD 资源

**使用流程**:
1. 日常开发推送到本地服务器：`git push origin master`
2. 需要构建时推送到 GitHub：`git push github master`
3. 发布新版本时创建 tag 并推送：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   git push github v1.0.0  # 触发 GitHub Actions 构建
   ```

### 方案 B：自动同步到 GitHub

在本地服务器配置 Git Hooks，自动同步到 GitHub（需要本地服务器管理员权限）。

---

## 推荐工作流程

### 日常开发

```bash
# 1. 提交代码
git add .
git commit -m "feat: 实现新功能"

# 2. 推送到本地私有服务器（团队协作）
git push origin master

# 3. （可选）推送到 GitHub（代码备份 + CI 检查）
git push github master
```

### 发布新版本

```bash
# 1. 创建版本 tag
git tag v1.0.0

# 2. 推送到两个远程仓库
git push origin v1.0.0
git push github v1.0.0

# 3. GitHub Actions 自动构建三个平台的安装包
# 4. 15-20 分钟后在 GitHub Releases 下载安装包
```

---

## 安全建议

### 1. 使用 SSH 密钥（推荐）

GitHub 支持 SSH 方式，更安全且无需每次输入密码：

```bash
# 生成 SSH 密钥（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 添加公钥到 GitHub（复制 ~/.ssh/id_ed25519.pub 内容）
# GitHub Settings > SSH and GPG keys > New SSH key

# 使用 SSH URL 添加远程仓库
git remote add github git@github.com:username/cad-pdf-converter.git
```

### 2. 使用 Personal Access Token

如果使用 HTTPS，建议使用 GitHub Personal Access Token 替代密码：

1. GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Generate new token
3. 选择权限：`repo` (完整仓库访问权限)
4. 复制 token
5. 首次推送时输入 token 作为密码

### 3. 配置 Git 凭据缓存

```bash
# macOS：使用 Keychain 存储凭据
git config --global credential.helper osxkeychain

# Linux：缓存凭据 1 小时
git config --global credential.helper 'cache --timeout=3600'
```

---

## 常见问题

### Q1: 两个仓库同步出现冲突怎么办？

```bash
# 从 GitHub 拉取最新代码
git fetch github
git merge github/master

# 解决冲突后推送到本地服务器
git push origin master
```

### Q2: 如何删除远程仓库？

```bash
# 删除 github 远程仓库配置
git remote remove github
```

### Q3: 如何重命名远程仓库？

```bash
# 将 origin 重命名为 private
git remote rename origin private

# 将 github 设为新的 origin
git remote rename github origin
```

### Q4: GitHub Actions 需要访问私有依赖怎么办？

如果项目依赖本地私有服务器的其他仓库，需要：
1. 将依赖也推送到 GitHub（私有仓库）
2. 或者在 GitHub Actions 中配置访问本地服务器的凭据

---

## 快速配置命令

```bash
# 方案 1：添加 GitHub 作为独立远程仓库（推荐）
git remote add github https://github.com/username/cad-pdf-converter.git
git push -u github master
git push github --tags

# 创建 alias 简化同步
git config alias.pushall '!git push origin "$1" && git push github "$1" && :'
git config alias.pushtagall '!git push origin --tags && git push github --tags'

# 使用
git pushall master           # 推送分支到两个仓库
git pushtagall              # 推送所有 tags 到两个仓库
```

---

## 总结

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **方案 1** | 灵活，可选择性推送 | 需要手动推送到 GitHub | **推荐**：日常用本地服务器，发布时用 GitHub |
| **方案 2** | 自动同步 | 一个失败会影响另一个 | 需要保持两个仓库完全同步 |
| **方案 3** | 简化操作 | 需要配置 alias | **推荐**：结合方案 1 使用 |

**最佳实践**: 使用方案 1 + 方案 3，既保持灵活性，又简化操作。

---

**创建时间**: 2025-11-07
**相关文档**: `docs/github-actions.md`
