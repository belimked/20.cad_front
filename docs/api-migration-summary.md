# API 接口迁移总结

**更新日期**: 2025-11-07
**版本**: v0.1.0
**状态**: ✅ 已完成

---

## 📋 变更概述

根据用户需求,将应用的 API 接口迁移到新的后端服务器,并更新了 API 结构以支持更详细的任务管理。

### 新 API 服务器

- **旧地址**: `https://api.example.com`
- **新地址**: `http://10.3.19.63:8000`

### 核心接口变更

#### 1. 提交打印任务接口

**旧接口**: `POST /api/cad/upload` (multipart/form-data)
**新接口**: `POST /api/v1/tasks/print` (application/json)

**请求参数变化**:
```typescript
// 旧参数
FormData {
  file: File
}

// 新参数
{
  dwg_url: string,          // 必填 - DWG 文件下载地址
  config_name?: string,     // 可选 - 配置名称(默认 "default")
  callback_url?: string,    // 可选 - 回调地址
  use_bplot?: boolean       // 可选 - 是否使用 bplot 工作流(默认 false)
}
```

**响应结构**:
```typescript
{
  task_id: string,
  message: string
}
```

#### 2. 查询任务详情接口

**旧接口**: `GET /api/tasks/{task_id}/status`
**新接口**: `GET /api/v1/tasks/{task_id}` (统一详情接口)

**新增的响应字段**:
```typescript
{
  task_id: string,
  dwg_url: string,              // 新增 - 源文件 URL
  config_name: string,          // 新增 - 使用的配置
  use_bplot: boolean,           // 新增 - 是否使用 bplot
  status: 'queued' | 'processing' | 'completed' | 'failed',
  progress: number,
  created_at: string,           // 新增 - 创建时间
  updated_at: string,           // 新增 - 更新时间
  completed_at?: string,        // 新增 - 完成时间
  error_message?: string,
  steps: TaskStep[]             // 新增 - 步骤详情
}
```

**新增的 TaskStep 结构**:
```typescript
{
  step_id: number,
  step_name: string,
  status: 'pending' | 'running' | 'completed' | 'failed',
  started_at?: string,
  completed_at?: string,
  duration?: number,
  log_message?: string,
  error_message?: string
}
```

---

## 🔧 代码变更详情

### 1. 配置文件更新

**文件**: `src/stores/configStore.ts`

```typescript
const defaultConfig: AppConfig = {
  apiBaseUrl: 'http://10.3.19.63:8000',  // 更新服务器地址
  pollingInterval: 3000,
  maxHistoryRecords: 1000,
  enableNotifications: true,
};
```

### 2. TypeScript API 服务层

**文件**: `src/services/api.ts`

**新增类型定义**:
- `PrintTaskRequest` - 打印任务请求参数
- `TaskDetailResponse` - 任务详情响应
- `TaskStep` - 任务步骤

**更新的方法**:

#### `uploadFile()`
```typescript
// 变更前: multipart 文件上传
async uploadFile(filePath: string): Promise<UploadResponse>

// 变更后: JSON 请求,支持 bplot 配置
async uploadFile(filePath: string, useBplot = false): Promise<UploadResponse>
```

#### `getTaskStatus()`
```typescript
// 变更前: 调用 poll_task_status 命令
async getTaskStatus(taskId: string): Promise<TaskStatusResponse>

// 变更后: 调用 get_task_detail 命令并转换为简化的状态
async getTaskStatus(taskId: string): Promise<TaskStatusResponse>
```

#### `getTaskDetail()` (新增)
```typescript
// 新增方法:获取完整的任务详情
async getTaskDetail(taskId: string): Promise<TaskDetailResponse>
```

#### `getStatusMessage()` (新增私有方法)
```typescript
// 新增方法:根据任务详情生成状态消息
private getStatusMessage(detail: TaskDetailResponse): string
```

### 3. Rust 后端更新

#### 文件: `src-tauri/src/models/response.rs`

**新增类型**:
```rust
/// 任务步骤
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskStep {
    pub step_id: i32,
    pub step_name: String,
    pub status: String,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub duration: Option<f64>,
    pub log_message: Option<String>,
    pub error_message: Option<String>,
}

/// 任务详情响应
#[derive(Debug, Serialize, Deserialize)]
pub struct TaskDetailResponse {
    pub task_id: String,
    pub dwg_url: String,
    pub config_name: String,
    pub use_bplot: bool,
    pub status: String,
    pub progress: u8,
    pub created_at: String,
    pub updated_at: String,
    pub completed_at: Option<String>,
    pub error_message: Option<String>,
    pub steps: Vec<TaskStep>,
}
```

#### 文件: `src-tauri/src/commands/upload.rs`

**变更说明**:
- 移除 multipart 文件上传逻辑
- 改为发送 JSON POST 请求到 `/api/v1/tasks/print`
- 接受 TypeScript 传入的 JSON 字符串,解析后转发

```rust
#[derive(Debug, Serialize, Deserialize)]
struct PrintTaskRequest {
    dwg_url: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    config_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    callback_url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    use_bplot: Option<bool>,
}

#[tauri::command]
pub async fn upload_file(api_url: String, request_data: String) -> Result<UploadResponse, String>
```

#### 文件: `src-tauri/src/commands/task.rs`

**新增命令**:
```rust
/// 查询任务详情命令(新 API)
/// GET /api/v1/tasks/{task_id}
#[tauri::command]
pub async fn get_task_detail(
    task_id: String,
    api_url: String,
) -> Result<TaskDetailResponse, String>
```

#### 文件: `src-tauri/src/main.rs`

**注册新命令**:
```rust
.invoke_handler(tauri::generate_handler![
    // ...
    task::poll_task_status,
    task::get_task_detail,  // 新增
    task::generate_pdf,
    // ...
])
```

---

## ✅ 编译验证

### Rust 编译状态

```bash
$ cargo check
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 1.10s

warning: function `validate_file_path` is never used
  --> src/commands/file.rs:80:8
   |
80 | pub fn validate_file_path(path: &str) -> Result<PathBuf, AppError> {
   |        ^^^^^^^^^^^^^^^^^^
```

**编译结果**: ✅ 成功
**警告数量**: 1 (无害的未使用函数警告,已保留供未来使用)

---

## 🎯 兼容性说明

### 前端轮询服务

现有的 `taskPollingService.ts` 可以无缝兼容新 API:

```typescript
// taskPollingService.ts 中的调用
const statusResponse = await apiService.getTaskStatus(taskId);

// ↓ 内部自动调用新的 get_task_detail 命令
// ↓ 并转换为简化的 TaskStatusResponse
```

### 文件上传流程

**重要说明**: 新 API 不再接受文件上传,而是需要提供 `dwg_url` (文件下载地址)。

**当前实现**:
```typescript
// FileUpload.svelte
const requestData: PrintTaskRequest = {
  dwg_url: filePath,  // ⚠️ 注意:这里 filePath 应该是一个可访问的 URL
  config_name: useBplot ? 'bplot' : 'default',
  use_bplot: useBplot,
};
```

**需要注意**:
- 如果 `filePath` 是本地文件路径,后端无法访问
- **建议**: 在调用此接口前,先将文件上传到文件服务器,获取 URL 后再调用打印任务接口
- **或者**: 后端提供额外的文件上传接口,返回可访问的 URL

---

## 🔄 数据流对比

### 旧流程
```
用户选择文件
  ↓
上传文件到 API (multipart)
  ↓
获取 task_id
  ↓
轮询 /api/tasks/{task_id}/status
  ↓
显示简单的状态和进度
```

### 新流程
```
用户选择文件
  ↓
(需要先上传到文件服务器)
  ↓
提交 dwg_url 到 /api/v1/tasks/print
  ↓
获取 task_id
  ↓
轮询 /api/v1/tasks/{task_id}
  ↓
显示详细的状态、进度和步骤
```

---

## 📝 待完成事项

### 1. 文件上传处理 ⚠️
- [ ] 确认 `dwg_url` 的来源(需要文件服务器?)
- [ ] 更新 `FileUpload.svelte` 组件处理文件上传
- [ ] 或者后端提供文件上传接口

### 2. 步骤详情展示
- [ ] 在 `TaskCard` 组件中展示 `steps` 数组
- [ ] 显示每个步骤的状态和耗时
- [ ] 可选:添加步骤日志查看功能

### 3. 测试
- [ ] 测试新 API 接口连通性
- [ ] 测试任务提交流程
- [ ] 测试任务轮询和状态更新
- [ ] 测试错误处理

---

## 🎯 PRD 对应关系

本次更新属于技术架构升级,不直接对应 PRD 中的 Epic/Story,但为以下功能提供了更强大的数据支持:

- **Epic 2 (任务轮询与进度显示)** - 可以获取更详细的任务状态和步骤信息
- **Epic 5 (任务历史管理)** - 可以存储更多的任务元数据

---

## 📊 代码统计

| 文件 | 行数变化 | 说明 |
|------|----------|------|
| configStore.ts | ~1 | 更新 API 地址 |
| api.ts | ~40 | 新增类型和方法 |
| upload.rs | ~30 | 重写上传逻辑 |
| task.rs | +42 | 新增详情查询命令 |
| response.rs | +28 | 新增响应类型 |
| main.rs | +1 | 注册新命令 |
| **总计** | **~142** | 新增/修改代码 |

---

**实现者**: Claude Code
**审查状态**: 待测试
**后续步骤**: 确认文件上传方案并测试 API 连通性
