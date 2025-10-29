# DWG Processing API 使用文档

## 📋 概述

DWG Processing API 是一个基于FastAPI的HTTP服务，提供DWG文件自动化处理功能。

**核心功能：**
- 📥 异步下载DWG文件
- 🖨️ 调用AutoCAD工作流执行打印
- 📊 实时任务进度追踪
- 📝 完整的步骤日志记录

---

## 🚀 快速开始

### 1. 启动服务

**Windows:**
```bash
start_api.bat
```

**Linux/Mac:**
```bash
./start_api.sh
```

服务默认监听在 `http://localhost:8000`

### 2. 访问API文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

---

## 📡 API接口

### 1. 提交打印任务

**接口:** `POST /api/v1/tasks/print`

**功能:** 提交DWG文件处理任务，服务会异步下载文件并执行AutoCAD工作流

**请求示例:**

```bash
curl -X POST "http://localhost:8000/api/v1/tasks/print" \
  -H "Content-Type: application/json" \
  -d '{
    "dwg_url": "http://example.com/files/drawing.dwg",
    "config_name": "default",
    "callback_url": "http://example.com/callback"
  }'
```

**请求体:**

```json
{
  "dwg_url": "http://example.com/files/drawing.dwg",  // 必填：DWG文件下载地址
  "config_name": "default",                           // 可选：配置名称，默认default
  "callback_url": "http://example.com/callback"       // 可选：完成后回调地址
}
```

**响应示例:**

```json
{
  "code": 200,
  "message": "任务创建成功",
  "data": {
    "task_id": "task_20251029_171234_abc123",
    "status": "pending",
    "created_at": "2025-10-29T17:12:34"
  }
}
```

---

### 2. 查询任务详情

**接口:** `GET /api/v1/tasks/{task_id}`

**功能:** 查询指定任务的详细信息，包括所有步骤日志

**请求示例:**

```bash
curl "http://localhost:8000/api/v1/tasks/task_20251029_171234_abc123"
```

**响应示例:**

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "task_id": "task_20251029_171234_abc123",
    "dwg_url": "http://example.com/files/drawing.dwg",
    "dwg_filename": "drawing.dwg",
    "local_path": "/path/to/downloads/drawing.dwg",
    "file_size": 2048576,
    "status": "processing",
    "current_step": "执行AutoCAD工作流",
    "progress": 60,
    "error_message": null,
    "config_name": "default",
    "started_at": "2025-10-29T17:12:40",
    "completed_at": null,
    "created_at": "2025-10-29T17:12:34",
    "steps": [
      {
        "step_name": "下载DWG文件",
        "step_order": 1,
        "status": "completed",
        "message": "文件已保存到: /path/to/downloads/drawing.dwg",
        "error_message": null,
        "started_at": "2025-10-29T17:12:40",
        "completed_at": "2025-10-29T17:12:55",
        "duration_seconds": 15.234
      },
      {
        "step_name": "执行AutoCAD工作流",
        "step_order": 2,
        "status": "running",
        "message": "正在启动AutoCAD工作流",
        "error_message": null,
        "started_at": "2025-10-29T17:12:56",
        "completed_at": null,
        "duration_seconds": null
      }
    ]
  }
}
```

---

### 3. 查询任务列表

**接口:** `GET /api/v1/tasks`

**功能:** 分页查询任务列表，支持状态过滤

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|------|------|
| status | string | 否 | 状态过滤：pending/downloading/processing/completed/failed |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页大小，默认20，最大100 |

**请求示例:**

```bash
# 查询所有任务
curl "http://localhost:8000/api/v1/tasks"

# 查询正在处理的任务
curl "http://localhost:8000/api/v1/tasks?status=processing&page=1&size=10"
```

**响应示例:**

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "total": 100,
    "page": 1,
    "size": 20,
    "items": [
      {
        "task_id": "task_20251029_171234_abc123",
        "dwg_filename": "drawing.dwg",
        "status": "processing",
        "progress": 60,
        "current_step": "执行AutoCAD工作流",
        "created_at": "2025-10-29T17:12:34"
      },
      {
        "task_id": "task_20251029_170523_def456",
        "dwg_filename": "plan.dwg",
        "status": "completed",
        "progress": 100,
        "current_step": "已完成",
        "created_at": "2025-10-29T17:05:23"
      }
    ]
  }
}
```

---

### 4. 健康检查

**接口:** `GET /health`

**功能:** 检查服务是否正常运行

**请求示例:**

```bash
curl "http://localhost:8000/health"
```

**响应示例:**

```json
{
  "code": 200,
  "message": "服务正常运行",
  "data": {
    "status": "ok",
    "timestamp": "2025-10-29T17:12:34",
    "service": "DWG Process API"
  }
}
```

---

## 📊 任务状态说明

| 状态 | 说明 |
|-----|------|
| pending | 等待处理 |
| downloading | 正在下载文件 |
| processing | 正在执行AutoCAD工作流 |
| completed | 已完成 |
| failed | 失败 |

---

## 🔄 完整工作流程

```
1. 客户端提交任务
   ↓
2. 创建任务记录（状态：pending）
   ↓
3. 后台异步下载文件（状态：downloading，进度：10-40%）
   ↓
4. 执行AutoCAD工作流（状态：processing，进度：40-90%）
   ├── 步骤1: 关闭并打开CAD
   ├── 步骤2: 验证文件加载
   └── 步骤3: 执行菜单操作
   ↓
5. 任务完成（状态：completed，进度：100%）
```

---

## 🧪 测试示例

### Python示例

```python
import requests
import time

API_BASE = "http://localhost:8000"

# 1. 提交任务
response = requests.post(
    f"{API_BASE}/api/v1/tasks/print",
    json={
        "dwg_url": "http://example.com/test.dwg",
        "config_name": "default"
    }
)

result = response.json()
task_id = result['data']['task_id']
print(f"任务ID: {task_id}")

# 2. 轮询任务状态
while True:
    response = requests.get(f"{API_BASE}/api/v1/tasks/{task_id}")
    result = response.json()

    task = result['data']
    print(f"状态: {task['status']}, 进度: {task['progress']}%")

    if task['status'] in ['completed', 'failed']:
        break

    time.sleep(5)

print("任务完成！")
```

### JavaScript示例

```javascript
const API_BASE = "http://localhost:8000";

// 1. 提交任务
async function submitTask() {
  const response = await fetch(`${API_BASE}/api/v1/tasks/print`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      dwg_url: "http://example.com/test.dwg",
      config_name: "default"
    })
  });

  const result = await response.json();
  return result.data.task_id;
}

// 2. 查询任务状态
async function getTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/api/v1/tasks/${taskId}`);
  const result = await response.json();
  return result.data;
}

// 3. 轮询直到完成
async function waitForTask(taskId) {
  while (true) {
    const task = await getTaskStatus(taskId);
    console.log(`状态: ${task.status}, 进度: ${task.progress}%`);

    if (task.status === 'completed' || task.status === 'failed') {
      return task;
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }
}

// 运行
const taskId = await submitTask();
console.log(`任务ID: ${taskId}`);
await waitForTask(taskId);
console.log("任务完成！");
```

---

## ⚙️ 配置说明

### 数据库配置

配置文件：`config/database.yaml`

```yaml
database:
  host: 10.3.19.189
  port: 3313
  user: root
  password: your_password
  database: cad_mgt
```

### 下载目录

默认下载目录：`downloads/`

可在代码中修改：

```python
# api/services/file_downloader.py
downloader = FileDownloader(download_dir="your_custom_dir")
```

### AutoCAD配置

使用数据库中的配置，通过 `config_name` 参数指定：

```json
{
  "config_name": "default"  // 或其他配置名称
}
```

---

## 🐛 故障排查

### 问题1：服务启动失败

**现象:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决:**
```bash
pip install -r requirements.txt
```

### 问题2：下载文件失败

**现象:** 任务状态为 `failed`，错误信息为"下载失败"

**排查:**
1. 检查DWG文件URL是否可访问
2. 检查网络连接
3. 查看任务步骤日志获取详细错误

### 问题3：AutoCAD工作流失败

**现象:** 状态卡在 `processing`

**排查:**
1. 检查AutoCAD是否正常安装
2. 查看任务步骤日志
3. 查看 `autocad_task_logs` 表

---

## 📝 更新日志

### v1.0.0 (2025-10-29)

- ✅ 实现HTTP API服务
- ✅ 异步文件下载
- ✅ AutoCAD工作流集成
- ✅ 任务状态追踪
- ✅ 步骤日志记录
- ✅ Swagger/ReDoc文档

---

## 🔗 相关文档

- [AutoCAD工作流程文档](../research/autocad_com_api/README.md)
- [数据库配置指南](DATABASE_CONFIG_GUIDE.md)
- [全屏截图提取指南](SCREENSHOT_EXTRACT_GUIDE.md)

---

**创建时间:** 2025-10-29
**作者:** 老王团队
**版本:** 1.0.0
**状态:** ✅ 生产使用
