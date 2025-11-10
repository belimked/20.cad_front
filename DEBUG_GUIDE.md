# 任务状态不更新问题调试指南

## 问题描述
任务卡片显示:
```
#task_202
0 Bytes
排队中
PCX2.dwg
📤 2025/11/10 16:58
正在执行: 下载DWG文件
```

状态一直不变,调试日志无法展开。

## 调试步骤

### 1. 检查调试日志
打开应用底部的"调试日志"面板,查看:

1. **查看轮询日志**:
   - 筛选 "polling" 类型的日志
   - 检查是否每3秒有新的轮询请求
   - 查看轮询返回的数据

2. **查看API响应**:
   - 筛选 "response" 类型的日志
   - 找到 `GET /api/v1/tasks/task_202` 的响应
   - 点击"查看数据"展开完整的响应内容

### 2. 检查浏览器控制台

打开浏览器开发者工具 (F12 或 右键 -> 检查):

```javascript
// 在 Console 中执行以下命令查看任务状态

// 1. 查看当前所有任务
window.__tasks

// 2. 查看特定任务
window.__tasks.find(t => t.taskId === 'task_202')

// 3. 手动触发一次状态查询
await window.__TAURI__.invoke('get_task_detail', {
  taskId: 'task_202',
  apiUrl: 'http://你的API地址'
})
```

### 3. 检查后端API

使用curl或Postman测试API端点:

```bash
# 测试任务详情API
curl -X GET "http://localhost:8000/api/v1/tasks/task_202" \
  -H "Content-Type: application/json" | jq

# 预期响应格式 (新格式):
{
  "code": 200,
  "message": "success",
  "data": {
    "task_id": "task_202",
    "status": "processing",
    "progress": 25,
    "current_step": "下载DWG文件",
    "dwg_filename": "PCX2.dwg",
    ...
  }
}

# 或旧格式 (直接返回数据):
{
  "task_id": "task_202",
  "status": "processing",
  "progress": 25,
  ...
}
```

### 4. 常见问题诊断

#### 问题1: 调试日志无法展开

**症状**: 点击"查看数据"没有反应

**可能原因**:
- `<details>` 标签CSS问题
- 数据为 null 或 undefined

**解决方法**:
```javascript
// 在浏览器控制台执行
// 查看日志条目
$stores.logStore.entries

// 查看最新的API响应
$stores.logStore.entries.filter(e => e.level === 'response')[0]
```

#### 问题2: 任务状态不更新

**症状**: UI一直显示"排队中"和"下载DWG文件"

**可能原因**:

A. **轮询未启动**
```javascript
// 检查是否在轮询
// 在浏览器控制台查看
taskPollingService.getPollingCount()  // 应该 > 0
taskPollingService.isTaskPolling('task_202')  // 应该返回 true
```

B. **API返回的数据格式不正确**
- 检查后端返回的 `current_step` 字段
- 检查 `progress` 字段是否更新

C. **前端未正确更新状态**
```javascript
// 查看任务store
$stores.tasks

// 查看特定任务的最后更新时间
$stores.tasks.find(t => t.taskId === 'task_202')?.updatedAt
```

#### 问题3: 进度和文件大小显示为 0

**症状**: 显示 "0 Bytes" 和进度条无法显示

**可能原因**:
- API未返回 `file_size` 字段
- API未返回 `progress` 字段

**检查方法**:
```bash
# 检查API响应是否包含这些字段
curl "http://localhost:8000/api/v1/tasks/task_202" | jq '.data.file_size, .data.progress'
```

### 5. 临时修复方法

如果需要立即查看任务状态,可以在浏览器控制台手动更新:

```javascript
// 手动更新任务状态
import { taskActions } from '/src/stores/taskStore';

taskActions.updateTask('task_202', {
  status: 'processing',
  progress: 50,
  message: '正在处理CAD文件',
  fileSize: 2048000,  // 2MB
  updatedAt: Date.now()
});
```

### 6. 收集诊断信息

请提供以下信息以便进一步诊断:

1. **浏览器控制台的完整输出**
2. **调试日志中的最新10条记录** (筛选task_202相关)
3. **后端API的原始响应** (curl命令输出)
4. **当前的轮询状态**:
```javascript
{
  pollingCount: taskPollingService.getPollingCount(),
  isPolling: taskPollingService.isTaskPolling('task_202'),
  taskData: $stores.tasks.find(t => t.taskId === 'task_202')
}
```

## 预期行为

正常情况下,应该看到:

1. **调试日志** 每3秒有一条 "polling" 类型的日志
2. **任务状态** 从 `queued` -> `processing` -> `completed`
3. **进度条** 从 0% 逐步增长到 100%
4. **文件大小** 显示实际大小 (非 0 Bytes)
5. **状态消息** 随着步骤变化更新

## 下一步行动

根据调试结果:

- 如果轮询没有启动 → 检查 `startPolling()` 调用
- 如果API返回错误 → 检查后端日志
- 如果数据格式不匹配 → 检查API响应格式是否符合预期
- 如果前端未更新 → 检查 Svelte store 响应式机制
