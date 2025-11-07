# GitHub Personal Access Token 配置指南

## 为什么需要 Personal Access Token？

GitHub 从 2021 年 8 月起不再支持使用账户密码进行 Git 操作，必须使用 Personal Access Token (PAT)。

---

## 步骤 1: 创建 Personal Access Token

### 1.1 访问 GitHub Token 设置页面
访问：https://github.com/settings/tokens

或手动导航：
1. 点击右上角头像
2. Settings
3. Developer settings（左侧菜单最下方）
4. Personal access tokens > Tokens (classic)

### 1.2 生成新 Token
1. 点击 **Generate new token** > **Generate new token (classic)**
2. 填写信息：
   - **Note**: `CAD PDF Converter - Local Dev` (备注，方便识别)
   - **Expiration**: 建议选择 **No expiration** 或 **90 days**
3. 选择权限（Scopes）：
   - ✅ **repo** (勾选顶级 repo，包含所有子权限)
     - 这会自动包含：
       - repo:status
       - repo_deployment
       - public_repo
       - repo:invite
       - security_events
   - ✅ **workflow** (允许 GitHub Actions 运行)
4. 滚动到底部，点击 **Generate token**

### 1.3 复制 Token
⚠️ **重要**：Token 只会显示一次！
- 复制生成的 token（类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
- 保存到安全的地方（密码管理器或安全笔记）

---

## 步骤 2: 配置 Git 凭据

### 方式 A：首次推送时输入（推荐）

直接推送代码，Git 会提示输入凭据：

```bash
git push -u github cad_front
```

提示输入时：
- **Username**: 输入您的 GitHub 用户名（例如：`belimked`）
- **Password**: 粘贴刚才复制的 Personal Access Token

macOS 会自动将凭据保存到 Keychain，下次无需再输入。

### 方式 B：在 URL 中包含用户名（不推荐）

```bash
# 修改远程仓库 URL，包含用户名
git remote set-url github https://belimked@github.com/belimked/20.cad_front.git

# 推送时只需输入 token（作为密码）
git push -u github cad_front
```

### 方式 C：使用 Git Credential Helper

```bash
# macOS：配置使用 Keychain 存储凭据（通常已默认启用）
git config --global credential.helper osxkeychain

# 验证配置
git config --global credential.helper
```

---

## 步骤 3: 推送代码到 GitHub

### 3.1 推送当前分支

```bash
git push -u github cad_front
```

### 3.2 推送所有本地分支（如果有多个）

```bash
# 查看所有本地分支
git branch -a

# 推送所有分支
git push github --all
```

### 3.3 推送所有 tags

```bash
# 查看所有 tags
git tag

# 推送所有 tags
git push github --tags
```

---

## 步骤 4: 验证推送成功

访问您的 GitHub 仓库：
https://github.com/belimked/20.cad_front

应该能看到：
- ✅ 代码文件
- ✅ 提交历史
- ✅ Branches（分支）
- ✅ GitHub Actions workflows（`.github/workflows/` 下的文件）

---

## 常见问题

### Q1: 忘记保存 Token 怎么办？

如果忘记保存 token，需要重新生成：
1. 访问 https://github.com/settings/tokens
2. 找到之前创建的 token
3. 点击 **Regenerate token**
4. 重新复制并保存

### Q2: Token 过期了怎么办？

如果设置了过期时间，token 过期后：
1. 访问 https://github.com/settings/tokens
2. 点击过期 token 旁的 **Regenerate token**
3. 重新复制新 token
4. 下次推送时输入新 token

macOS Keychain 会自动更新保存的凭据。

### Q3: 如何查看已保存的凭据？

**macOS Keychain**:
1. 打开 "钥匙串访问" (Keychain Access) 应用
2. 搜索 "github.com"
3. 双击查看详情

### Q4: 如何删除已保存的凭据？

```bash
# macOS: 删除 github.com 的凭据
git credential-osxkeychain erase
host=github.com
protocol=https
[按两次回车]
```

或在 Keychain Access 应用中手动删除。

### Q5: 推送时显示 "Permission denied"？

检查 Token 权限：
1. 访问 https://github.com/settings/tokens
2. 点击 token 查看详情
3. 确保勾选了 **repo** 权限
4. 如果没有，删除 token 重新创建

---

## 安全建议

### ✅ DO（推荐做法）
- 使用有意义的 Token 备注，方便管理
- 为不同设备/项目创建不同的 Token
- 定期检查和删除不用的 Token
- 将 Token 保存到密码管理器（如 1Password、LastPass）
- 设置合理的过期时间（如 90 天）

### ❌ DON'T（避免做法）
- 不要在代码中硬编码 Token
- 不要将 Token 提交到 Git 仓库
- 不要在公开场合分享 Token
- 不要使用过于简单的备注名称
- 不要给 Token 过多的权限

---

## 快速参考

### 首次推送流程

```bash
# 1. 确保已添加 GitHub 远程仓库
git remote -v

# 2. 推送代码（会提示输入凭据）
git push -u github cad_front

# 提示输入时：
# Username: belimked
# Password: [粘贴 Personal Access Token]

# 3. 推送所有 tags
git push github --tags

# 4. 验证
# 访问 https://github.com/belimked/20.cad_front
```

### 配置 Git Alias 简化操作

```bash
# 同时推送到本地服务器和 GitHub
git config alias.pushall '!git push origin "$@" && git push github "$@" && :'

# 使用
git pushall cad_front
```

---

## 相关文档

- [GitHub Docs: Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Git Credentials](https://git-scm.com/docs/gitcredentials)

---

**创建时间**: 2025-11-07
