# DWG 文件 URL 测试指南

**创建日期**: 2025-11-07
**用途**: 快速测试新 API 接口的打印任务提交功能

---

## 🎯 功能说明

URL 测试面板用于快速提交远程 DWG 文件的打印任务,无需上传本地文件。

### 预设的测试文件

| 文件名 | 显示名称 | URL |
|--------|----------|-----|
| tz.dwg | TZ 图纸 | http://10.3.19.199/cad/tz.dwg |
| PCX2.dwg | PCX2 图纸 #1 | http://10.3.19.199/cad/PCX2.dwg |
| PCX2.dwg | PCX2 图纸 #2 | http://10.3.19.199/cad/PCX2.dwg |

---

## 🚀 使用步骤

### 1. 切换到 URL 测试页面

启动应用后,在顶部 Tab 栏点击 **"🧪 URL 测试"**

### 2. 选择测试文件

在下拉菜单中选择一个预设的 DWG 文件:
- TZ 图纸 - 标准测试图纸
- PCX2 图纸 #1 / #2 - PCX2 测试图纸

### 3. 配置打印选项

可选:勾选 **"使用 bplot 工作流"** 复选框

- ✅ 勾选:使用 bplot 配置(`config_name: "bplot"`, `use_bplot: true`)
- ⬜ 不勾选:使用默认配置(`config_name: "default"`, `use_bplot: false`)

### 4. 提交任务

点击 **"🚀 提交打印任务"** 按钮

### 5. 查看结果

- ✅ 成功:显示绿色成功消息,任务自动添加到下方的任务监控列表
- ❌ 失败:显示红色错误消息,说明失败原因

---

## 📊 任务监控

提交成功后,任务会自动出现在下方的 **"任务监控"** 区域:

- 任务 ID (前8位)
- 文件名
- 状态徽章
- 进度条 (queued/processing 状态)
- PDF 下载区域 (completed 状态)

任务会每 3 秒自动轮询状态更新。

---

## 🔧 配置说明

### 文件服务器

预设的文件服务器地址:`http://10.3.19.199/cad/`

如需修改,可以编辑配置文件:
- **代码配置**: `src/config/dwgFiles.ts:11`
- **环境变量**: `.env` 文件中设置 `VITE_FILE_SERVER_URL`

### API 服务器

当前 API 服务器:`http://10.3.19.63:8000`

配置位置:
- `src/stores/configStore.ts:12`

### 添加新的测试文件

编辑 `src/config/dwgFiles.ts`,在 `DWG_FILE_OPTIONS` 数组中添加:

```typescript
{
  id: 'your-file-id',
  name: 'your-file.dwg',
  displayName: '显示名称',
  url: `${FILE_SERVER_BASE_URL}/your-file.dwg`,
  description: '文件描述（可选）',
}
```

---

## 🧪 测试场景

### 场景 1: 标准打印任务
- 文件:TZ 图纸
- Bplot:不勾选
- 预期:任务正常创建,状态为 queued

### 场景 2: Bplot 工作流
- 文件:PCX2 图纸
- Bplot:勾选
- 预期:任务使用 bplot 配置,后端应用 bplot 工作流

### 场景 3: 同一文件多次提交
- 文件:TZ 图纸
- 操作:连续提交 3 次
- 预期:创建 3 个独立的任务,每个任务有独立的 task_id

---

## 🐛 常见问题

### Q1: 提交失败 "请求失败: ..."
**原因**: 无法连接到 API 服务器 `http://10.3.19.63:8000`

**解决方案**:
1. 检查网络连接
2. 确认 API 服务器是否运行
3. 使用浏览器访问 `http://10.3.19.63:8000` 测试连通性

### Q2: 提交失败 "HTTP 404 - ..."
**原因**: API 端点路径错误

**解决方案**:
1. 确认 API 服务器已部署 `/api/v1/tasks/print` 接口
2. 检查后端日志确认接口路由配置

### Q3: 提交成功但任务一直 queued
**原因**: 后端可能无法下载 DWG 文件

**解决方案**:
1. 确认文件服务器 `http://10.3.19.199` 可访问
2. 使用浏览器直接访问 DWG URL 测试
3. 检查后端日志查看下载错误

### Q4: 任务状态不更新
**原因**: 轮询服务可能未启动或查询接口失败

**解决方案**:
1. 打开开发者工具(F12)查看控制台日志
2. 检查是否有网络错误或 API 错误
3. 确认 `/api/v1/tasks/{task_id}` 接口可用

---

## 🔍 调试技巧

### 查看请求详情

打开浏览器开发者工具(F12) → Network 标签页:

1. **提交任务请求**
   - URL: `http://10.3.19.63:8000/api/v1/tasks/print`
   - Method: POST
   - Request Body:
     ```json
     {
       "dwg_url": "http://10.3.19.199/cad/tz.dwg",
       "config_name": "default",
       "use_bplot": false
     }
     ```

2. **查询任务详情**
   - URL: `http://10.3.19.63:8000/api/v1/tasks/{task_id}`
   - Method: GET
   - 频率:每 3 秒一次

### 查看控制台日志

在开发者工具 Console 标签页中,可以看到:
- `提交打印任务:` - 任务提交日志
- `任务创建成功:` - 任务创建成功日志
- `查询任务详情:` - 轮询日志(Rust 端)
- `任务状态:` - 状态更新日志

---

## 📝 API 请求示例

### 提交任务 (标准配置)

```bash
curl -X POST http://10.3.19.63:8000/api/v1/tasks/print \
  -H "Content-Type: application/json" \
  -d '{
    "dwg_url": "http://10.3.19.199/cad/tz.dwg",
    "config_name": "default",
    "use_bplot": false
  }'
```

### 提交任务 (bplot 配置)

```bash
curl -X POST http://10.3.19.63:8000/api/v1/tasks/print \
  -H "Content-Type: application/json" \
  -d '{
    "dwg_url": "http://10.3.19.199/cad/PCX2.dwg",
    "config_name": "bplot",
    "use_bplot": true
  }'
```

### 查询任务详情

```bash
curl http://10.3.19.63:8000/api/v1/tasks/abc12345
```

---

## 🎯 与文件上传的区别

| 特性 | 文件上传 Tab | URL 测试 Tab |
|------|-------------|-------------|
| 文件来源 | 本地文件系统 | 远程 URL |
| 上传方式 | (待实现) | 直接提交 URL |
| 使用场景 | 用户日常使用 | 开发测试 |
| 文件大小限制 | 取决于后端 | 无限制 |
| 网络要求 | 上传带宽 | 后端到文件服务器 |

---

**创建者**: Claude Code
**维护状态**: 活跃
**反馈**: 如有问题请查看 `docs/api-migration-summary.md`
