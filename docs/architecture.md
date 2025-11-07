# CAD 文件处理桌面应用 - 系统架构文档

**版本**: v1.0
**最后更新**: 2025-11-06
**架构师**: Winston (Architect)
**状态**: 架构设计阶段
**基于 PRD**: v1.4

---

## 文档目录

1. [架构概览](#1-架构概览)
2. [整体系统架构](#2-整体系统架构)
3. [前端架构设计](#3-前端架构设计)
4. [Rust 后端架构](#4-rust-后端架构)
5. [数据流设计](#5-数据流设计)
6. [状态管理方案](#6-状态管理方案)
7. [API 集成设计](#7-api-集成设计)
8. [本地存储设计](#8-本地存储设计)
9. [技术栈与依赖](#9-技术栈与依赖)
10. [项目目录结构](#10-项目目录结构)
11. [性能优化策略](#11-性能优化策略)
12. [安全考虑](#12-安全考虑)
13. [跨平台适配](#13-跨平台适配)
14. [测试策略](#14-测试策略)
15. [部署与构建](#15-部署与构建)
16. [技术风险与缓解措施](#16-技术风险与缓解措施)
17. [未来扩展性](#17-未来扩展性)

---

## 1. 架构概览

### 1.1 系统定位

本系统是一个**跨平台桌面应用**，基于 Tauri 框架构建，旨在为工程设计人员提供简洁、高效的 CAD 文件（DWG）到 PDF 的转换服务。

### 1.2 核心架构模式

**三层架构模式**：

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│              (Svelte UI Components)                     │
│   - 文件上传界面  - 任务监控  - PDF 预览  - 历史管理      │
└────────────────────┬────────────────────────────────────┘
                     │ Tauri IPC
┌────────────────────▼────────────────────────────────────┐
│                   Application Layer                     │
│              (Rust Tauri Commands)                      │
│   - 文件处理  - HTTP 客户端  - 本地存储  - 系统集成       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/HTTPS
┌────────────────────▼────────────────────────────────────┐
│                   External Services                     │
│              (远程 CAD 处理 API)                         │
│   - 文件上传  - 异步任务处理  - PDF 生成                  │
└─────────────────────────────────────────────────────────┘
```

### 1.3 架构原则

根据 PRD 和工程最佳实践，本架构遵循以下原则：

**KISS（简单至上）**
- 避免过度设计，采用 Tauri 标准模式
- 前端使用轻量级 Svelte，无运行时开销
- 状态管理使用 Svelte 内置 Stores，无需额外库

**YAGNI（精益求精）**
- 仅实现 MVP 所需功能（单文件处理）
- 批量处理、DXF 支持等留待未来版本

**DRY（杜绝重复）**
- API 调用逻辑统一封装在服务层
- 共用组件（进度条、文件卡片、通知）抽象复用
- Rust 和前端共享数据类型定义（通过 TypeScript 和 serde）

**SOLID 原则**
- **单一职责**：每个模块职责明确（上传、轮询、预览、存储）
- **开放封闭**：通过接口扩展，避免修改现有代码
- **依赖倒置**：依赖抽象（接口）而非具体实现

### 1.4 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| **桌面框架** | Tauri | 轻量、高性能、跨平台、安全性强 |
| **前端框架** | Svelte 4.x | 编译时框架、体积小、性能优异 |
| **状态管理** | Svelte Stores | 内置、轻量、与 Svelte 无缝集成 |
| **PDF 渲染** | PDF.js | 开源、成熟、跨平台一致性好 |
| **本地存储** | tauri-plugin-store | Tauri 官方插件、安全、易用 |
| **HTTP 客户端** | reqwest (Rust) | 高性能、支持流式下载、广泛使用 |
| **构建工具** | Vite | 快速、现代、与 Svelte 完美集成 |

---

## 2. 整体系统架构

### 2.1 架构分层图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                                │
│                    (Svelte Components)                          │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ 文件上传模块  │ 任务监控模块  │ PDF 预览模块  │ 历史管理模块        │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────────┘
       │              │              │                │
       │         Svelte Stores (状态管理)              │
       │              │              │                │
┌──────▼──────────────▼──────────────▼────────────────▼───────────┐
│                      服务层 (Services)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ API 服务  │ │ 轮询服务  │ │ 存储服务  │ │ 工具函数  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└──────┬───────────────┬──────────────┬────────────────┬──────────┘
       │ Tauri IPC     │              │                │
┌──────▼───────────────▼──────────────▼────────────────▼──────────┐
│                   Tauri 后端层 (Rust)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Commands     │ │ HTTP Client  │ │ File Handler │            │
│  │ (IPC 接口)   │ │ (reqwest)    │ │ (fs 操作)    │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└──────┬───────────────┬──────────────┬─────────────────┬─────────┘
       │               │              │                 │
       │ HTTP/HTTPS    │              │ Local FS        │
       ▼               ▼              ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐
│  远程 API    │  │  PDF 文件    │  │  本地存储    │  │ 系统服务  │
│  (CAD 处理)  │  │  (下载)      │  │  (历史记录)  │  │ (通知等)  │
└─────────────┘  └─────────────┘  └─────────────┘  └──────────┘
```

### 2.2 技术边界

**前端职责（Svelte + TypeScript）**
- UI 渲染和用户交互
- 状态管理（Svelte Stores）
- 任务轮询调度（setInterval）
- PDF.js 集成和渲染
- 路由管理（如果需要多页面）

**Rust 后端职责（Tauri）**
- 文件系统操作（读取、保存）
- HTTP 请求发送（上传、下载、API 调用）
- 系统级集成（通知、文件对话框）
- 本地数据持久化
- 安全沙箱和权限控制

**远程 API 职责（不在本项目范围）**
- CAD 文件处理
- 异步任务队列管理
- PDF 生成
- 文件存储和下载服务

---

## 3. 前端架构设计

### 3.1 组件层次结构

```
App.svelte (根组件)
│
├── Layout.svelte (布局容器)
│   ├── Header.svelte (顶部标题栏)
│   └── MainContent.svelte (主内容区)
│       │
│       ├── FileUpload.svelte (文件上传模块)
│       │   ├── DropZone.svelte (拖拽区域)
│       │   ├── FileSelector.svelte (文件选择按钮)
│       │   └── FileInfo.svelte (文件信息卡片)
│       │
│       ├── TaskMonitor.svelte (任务监控模块)
│       │   ├── TaskList.svelte (任务列表容器)
│       │   │   └── TaskCard.svelte (单个任务卡片)
│       │   │       ├── StatusBadge.svelte (状态标签)
│       │   │       └── ProgressBar.svelte (进度条)
│       │   │
│       │   └── FileRelationship.svelte (文件关系可视化)
│       │       ├── CadFileCard.svelte (CAD 文件卡片)
│       │       ├── PdfFileCard.svelte (PDF 文件卡片)
│       │       └── ConnectionLine.svelte (连线 SVG)
│       │
│       ├── PdfViewer.svelte (PDF 预览模块)
│       │   ├── PdfToolbar.svelte (工具栏)
│       │   ├── PdfCanvas.svelte (PDF 渲染区)
│       │   └── PdfThumbnails.svelte (缩略图侧边栏)
│       │
│       └── TaskHistory.svelte (历史管理模块)
│           ├── FilterBar.svelte (筛选工具栏)
│           └── HistoryList.svelte (历史列表)
│
└── Common (通用组件)
    ├── Button.svelte (按钮组件)
    ├── Modal.svelte (模态窗口)
    ├── Toast.svelte (通知组件)
    ├── Spinner.svelte (加载指示器)
    └── ConfirmDialog.svelte (确认对话框)
```

### 3.2 模块化设计

**按功能划分的模块**：

```typescript
src/
├── components/        // UI 组件
│   ├── upload/        // 上传相关组件
│   ├── task/          // 任务相关组件
│   ├── pdf/           // PDF 相关组件
│   ├── history/       // 历史相关组件
│   └── common/        // 通用组件
│
├── stores/            // 状态管理
│   ├── taskStore.ts         // 任务状态
│   ├── fileStore.ts         // 文件状态
│   ├── historyStore.ts      // 历史记录
│   └── uiStore.ts           // UI 状态
│
├── services/          // 业务逻辑服务
│   ├── api.ts               // API 调用封装
│   ├── taskPoller.ts        // 轮询服务
│   ├── localStorage.ts      // 本地存储服务
│   └── pdfService.ts        // PDF 处理服务
│
├── utils/             // 工具函数
│   ├── formatters.ts        // 格式化工具
│   ├── validators.ts        // 验证工具
│   └── constants.ts         // 常量定义
│
├── types/             // TypeScript 类型定义
│   ├── task.ts
│   ├── file.ts
│   └── api.ts
│
└── App.svelte         // 根组件
```

### 3.3 状态管理架构（Svelte Stores）

**Store 设计**：

```typescript
// taskStore.ts - 任务状态管理
import { writable, derived } from 'svelte/store';

export interface Task {
  taskId: string;
  fileName: string;
  fileSize: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  uploadTime: string;
  completionTime?: string;
  errorMessage?: string;
  pdfUrl?: string;
}

// 可写 Store
export const tasks = writable<Task[]>([]);

// 派生 Store - 自动计算当前处理中的任务
export const activeTasks = derived(
  tasks,
  $tasks => $tasks.filter(t => t.status === 'processing' || t.status === 'queued')
);

// 派生 Store - 已完成的任务
export const completedTasks = derived(
  tasks,
  $tasks => $tasks.filter(t => t.status === 'completed')
);

// Store 操作方法
export const taskActions = {
  addTask: (task: Task) => {
    tasks.update(list => [...list, task]);
  },

  updateTask: (taskId: string, updates: Partial<Task>) => {
    tasks.update(list =>
      list.map(t => t.taskId === taskId ? { ...t, ...updates } : t)
    );
  },

  removeTask: (taskId: string) => {
    tasks.update(list => list.filter(t => t.taskId !== taskId));
  },

  clearCompleted: () => {
    tasks.update(list => list.filter(t => t.status !== 'completed' && t.status !== 'failed'));
  }
};
```

### 3.4 路由设计（可选）

**单页面应用，采用模态窗口而非路由**：

- 主界面：文件上传 + 任务监控 + 文件关系
- PDF 预览：模态窗口覆盖
- 历史记录：侧边抽屉或独立模态

如需多页面，可引入 `svelte-spa-router` 或 `@roxi/routify`。

---

## 4. Rust 后端架构

### 4.1 Tauri Commands 设计

Tauri Commands 是前端与 Rust 后端通信的 IPC 接口。

**命令列表**：

```rust
// src-tauri/src/main.rs

fn main() {
  tauri::Builder::default()
    .plugin(tauri_plugin_store::Builder::default().build())
    .invoke_handler(tauri::generate_handler![
      // 文件操作
      select_file,
      upload_file,
      download_pdf,

      // API 调用
      poll_task_status,
      generate_pdf,

      // 本地存储
      save_task_history,
      load_task_history,
      clear_history,

      // 系统集成
      show_notification,
      open_file_location
    ])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
```

### 4.2 命令实现详解

#### 4.2.1 文件选择命令

```rust
// src-tauri/src/commands/file.rs

use tauri::api::dialog::FileDialogBuilder;

#[tauri::command]
pub async fn select_file() -> Result<String, String> {
    let file_path = FileDialogBuilder::new()
        .add_filter("DWG Files", &["dwg"])
        .set_title("选择 CAD 文件")
        .pick_file();

    match file_path {
        Some(path) => Ok(path.to_string_lossy().to_string()),
        None => Err("未选择文件".to_string())
    }
}
```

#### 4.2.2 文件上传命令

```rust
// src-tauri/src/commands/upload.rs

use reqwest::multipart::{Form, Part};
use std::fs::File;
use std::io::Read;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct UploadResponse {
    task_id: String,
    message: String,
}

#[tauri::command]
pub async fn upload_file(file_path: String, api_url: String) -> Result<UploadResponse, String> {
    // 读取文件
    let mut file = File::open(&file_path)
        .map_err(|e| format!("文件读取失败: {}", e))?;

    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|e| format!("文件读取错误: {}", e))?;

    // 构建 multipart 表单
    let file_name = std::path::Path::new(&file_path)
        .file_name()
        .unwrap()
        .to_string_lossy()
        .to_string();

    let part = Part::bytes(buffer)
        .file_name(file_name.clone())
        .mime_str("application/octet-stream")
        .map_err(|e| format!("文件 MIME 设置失败: {}", e))?;

    let form = Form::new().part("file", part);

    // 发送 HTTP 请求
    let client = reqwest::Client::new();
    let response = client
        .post(&format!("{}/api/cad/upload", api_url))
        .multipart(form)
        .timeout(std::time::Duration::from_secs(60))
        .send()
        .await
        .map_err(|e| format!("上传请求失败: {}", e))?;

    // 解析响应
    if response.status().is_success() {
        let upload_result: UploadResponse = response
            .json()
            .await
            .map_err(|e| format!("响应解析失败: {}", e))?;

        Ok(upload_result)
    } else {
        Err(format!("上传失败: HTTP {}", response.status()))
    }
}
```

#### 4.2.3 任务状态轮询命令

```rust
// src-tauri/src/commands/task.rs

#[derive(Serialize, Deserialize)]
pub struct TaskStatus {
    task_id: String,
    status: String,  // "queued" | "processing" | "completed" | "failed"
    progress: u8,    // 0-100
    message: Option<String>,
}

#[tauri::command]
pub async fn poll_task_status(task_id: String, api_url: String) -> Result<TaskStatus, String> {
    let client = reqwest::Client::new();
    let response = client
        .get(&format!("{}/api/tasks/{}/status", api_url, task_id))
        .timeout(std::time::Duration::from_secs(10))
        .send()
        .await
        .map_err(|e| format!("状态查询失败: {}", e))?;

    if response.status().is_success() {
        let status: TaskStatus = response
            .json()
            .await
            .map_err(|e| format!("状态解析失败: {}", e))?;

        Ok(status)
    } else {
        Err(format!("查询失败: HTTP {}", response.status()))
    }
}
```

#### 4.2.4 PDF 下载命令

```rust
// src-tauri/src/commands/download.rs

use futures_util::StreamExt;
use std::cmp::min;
use std::io::Write;
use tauri::Window;

#[tauri::command]
pub async fn download_pdf(
    window: Window,
    pdf_url: String,
    save_path: String,
) -> Result<String, String> {
    let client = reqwest::Client::new();
    let response = client
        .get(&pdf_url)
        .send()
        .await
        .map_err(|e| format!("下载请求失败: {}", e))?;

    let total_size = response
        .content_length()
        .ok_or("无法获取文件大小")?;

    let mut file = File::create(&save_path)
        .map_err(|e| format!("文件创建失败: {}", e))?;

    let mut downloaded: u64 = 0;
    let mut stream = response.bytes_stream();

    while let Some(item) = stream.next().await {
        let chunk = item.map_err(|e| format!("下载数据失败: {}", e))?;
        file.write_all(&chunk)
            .map_err(|e| format!("文件写入失败: {}", e))?;

        downloaded = min(downloaded + (chunk.len() as u64), total_size);

        // 发送进度事件到前端
        let progress = (downloaded as f64 / total_size as f64 * 100.0) as u8;
        window.emit("download-progress", progress).ok();
    }

    Ok(save_path)
}
```

### 4.3 错误处理机制

**统一错误类型**：

```rust
// src-tauri/src/error.rs

use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("文件操作错误: {0}")]
    FileError(#[from] std::io::Error),

    #[error("网络请求错误: {0}")]
    NetworkError(#[from] reqwest::Error),

    #[error("JSON 解析错误: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("自定义错误: {0}")]
    Custom(String),
}

// 转换为前端友好的错误字符串
impl From<AppError> for String {
    fn from(err: AppError) -> String {
        err.to_string()
    }
}
```

### 4.4 日志记录

```rust
// src-tauri/src/main.rs

use log::{info, warn, error};
use env_logger;

fn main() {
    // 初始化日志
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Info)
        .init();

    info!("应用启动");

    tauri::Builder::default()
        // ... 其他配置
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 5. 数据流设计

### 5.1 文件上传流程

```
用户操作                前端 (Svelte)              Rust 后端              远程 API
   │                        │                        │                      │
   │ 1. 选择文件             │                        │                      │
   ├────────────────────────>│                        │                      │
   │                        │ 2. 调用 select_file    │                      │
   │                        ├───────────────────────>│                      │
   │                        │ 3. 返回文件路径         │                      │
   │                        │<───────────────────────┤                      │
   │ 4. 显示文件信息         │                        │                      │
   │<────────────────────────┤                        │                      │
   │                        │                        │                      │
   │ 5. 点击"开始处理"        │                        │                      │
   ├────────────────────────>│                        │                      │
   │                        │ 6. 调用 upload_file    │                      │
   │                        ├───────────────────────>│                      │
   │                        │                        │ 7. POST /api/upload  │
   │                        │                        ├─────────────────────>│
   │                        │                        │ 8. 返回 task_id      │
   │                        │                        │<─────────────────────┤
   │                        │ 9. 返回 task_id        │                      │
   │                        │<───────────────────────┤                      │
   │ 10. 显示"上传成功"       │                        │                      │
   │<────────────────────────┤                        │                      │
   │ 11. 启动轮询            │                        │                      │
   │                        │                        │                      │
```

### 5.2 任务轮询流程

```
前端轮询服务              Rust 后端              远程 API
   │                        │                      │
   │ 每 3 秒                 │                      │
   ├───────────────────────>│                      │
   │ poll_task_status       │ GET /api/tasks/{id}  │
   │                        ├─────────────────────>│
   │                        │ 返回状态和进度        │
   │                        │<─────────────────────┤
   │ 更新 taskStore         │                      │
   │<───────────────────────┤                      │
   │                        │                      │
   │ UI 自动响应式更新        │                      │
   │                        │                      │
   │ 检测到"completed"       │                      │
   ├───> 停止轮询            │                      │
   ├───> 触发 PDF 生成      │                      │
   │                        │                      │
```

### 5.3 PDF 生成与下载流程

```
前端                    Rust 后端              远程 API
   │                        │                      │
   │ 任务完成后自动触发        │                      │
   ├───────────────────────>│                      │
   │ generate_pdf           │ POST /api/pdf        │
   │                        ├─────────────────────>│
   │                        │ 返回 PDF URL         │
   │                        │<─────────────────────┤
   │ 存储 PDF URL           │                      │
   │<───────────────────────┤                      │
   │                        │                      │
   │ 用户点击"下载"           │                      │
   ├───────────────────────>│                      │
   │ download_pdf           │ GET {PDF_URL}        │
   │                        ├─────────────────────>│
   │                        │ 流式返回 PDF 数据     │
   │                        │<─────────────────────┤
   │ 实时进度更新            │ (emit progress)      │
   │<───────────────────────┤                      │
   │ 下载完成通知            │                      │
   │<───────────────────────┤                      │
   │                        │                      │
```

---

## 6. 状态管理方案

### 6.1 Store 架构

**全局状态分类**：

```typescript
// stores/index.ts

// 1. 任务状态 Store
export { tasks, activeTasks, completedTasks, taskActions } from './taskStore';

// 2. 文件状态 Store
export { currentFile, fileActions } from './fileStore';

// 3. 历史记录 Store
export { taskHistory, historyActions } from './historyStore';

// 4. 文件关系 Store
export { fileRelationships, relationshipActions } from './relationshipStore';

// 5. UI 状态 Store
export { uiState, uiActions } from './uiStore';

// 6. 配置 Store
export { appConfig } from './configStore';
```

### 6.2 状态持久化

**集成 tauri-plugin-store**：

```typescript
// stores/historyStore.ts

import { writable } from 'svelte/store';
import { Store } from 'tauri-plugin-store-api';

const store = new Store('.settings.dat');

// 初始化：从本地加载历史
export async function initHistory() {
  const history = await store.get('taskHistory') || [];
  taskHistory.set(history);
}

// 自动保存：监听 Store 变化
taskHistory.subscribe(async (value) => {
  await store.set('taskHistory', value);
  await store.save();
});
```

### 6.3 响应式数据绑定

**Svelte 组件中使用 Store**：

```svelte
<!-- TaskList.svelte -->
<script lang="ts">
  import { tasks, activeTasks } from '$stores';

  // $ 前缀自动订阅 Store
  $: activeTaskCount = $activeTasks.length;
</script>

<div class="task-list">
  <h2>当前任务 ({activeTaskCount})</h2>

  {#each $tasks as task (task.taskId)}
    <TaskCard {task} />
  {/each}
</div>
```

---

## 7. API 集成设计

### 7.1 API 端点定义

**远程 API 接口规范**（需与后端团队确认）：

```typescript
// types/api.ts

export interface ApiEndpoints {
  // 文件上传
  upload: {
    method: 'POST';
    path: '/api/cad/upload';
    request: FormData;  // { file: File }
    response: {
      task_id: string;
      message: string;
    };
  };

  // 任务状态查询
  taskStatus: {
    method: 'GET';
    path: '/api/tasks/:taskId/status';
    response: {
      task_id: string;
      status: 'queued' | 'processing' | 'completed' | 'failed';
      progress: number;  // 0-100
      message?: string;
    };
  };

  // PDF 生成
  generatePdf: {
    method: 'POST';
    path: '/api/cad/generate-pdf';
    request: {
      task_id: string;
    };
    response: {
      pdf_id: string;
      file_name: string;
      download_url: string;
      file_size?: number;
    };
  };
}
```

### 7.2 API 服务封装

```typescript
// services/api.ts

import { invoke } from '@tauri-apps/api/tauri';

export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  // 上传文件
  async uploadFile(filePath: string): Promise<{ taskId: string; message: string }> {
    const response = await invoke<{ task_id: string; message: string }>(
      'upload_file',
      { filePath, apiUrl: this.baseUrl }
    );

    return {
      taskId: response.task_id,
      message: response.message
    };
  }

  // 查询任务状态
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    return await invoke<TaskStatus>(
      'poll_task_status',
      { taskId, apiUrl: this.baseUrl }
    );
  }

  // 生成 PDF
  async generatePdf(taskId: string): Promise<PdfInfo> {
    return await invoke<PdfInfo>(
      'generate_pdf',
      { taskId, apiUrl: this.baseUrl }
    );
  }

  // 下载 PDF
  async downloadPdf(pdfUrl: string, savePath: string): Promise<string> {
    return await invoke<string>(
      'download_pdf',
      { pdfUrl, savePath }
    );
  }
}

// 导出单例
export const apiService = new ApiService('https://api.example.com');
```

### 7.3 错误处理和重试机制

```typescript
// services/apiErrorHandler.ts

export class ApiErrorHandler {
  private maxRetries = 3;
  private retryDelay = 5000; // 5 秒

  async executeWithRetry<T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        console.error(`${operationName} 失败 (尝试 ${attempt}/${this.maxRetries}):`, error);

        if (attempt < this.maxRetries) {
          await this.delay(this.retryDelay * attempt); // 指数退避
        }
      }
    }

    throw new Error(`${operationName} 失败: ${lastError!.message}`);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

---

## 8. 本地存储设计

### 8.1 数据结构定义

```typescript
// types/storage.ts

export interface StoredTaskHistory {
  taskId: string;
  fileName: string;
  fileSize: number;
  uploadTime: string;
  completionTime?: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  errorMessage?: string;
  pdfFileUrl?: string;
}

export interface StoredFileRelationship {
  taskId: string;
  cadFile: {
    id: string;
    name: string;
    size: number;
    uploadTime: string;
  };
  pdfFile: {
    id: string;
    name: string;
    downloadUrl: string;
    generatedTime: string;
  };
}

export interface AppSettings {
  apiBaseUrl: string;
  pollingInterval: number;      // 毫秒
  maxHistoryRecords: number;
  enableNotifications: boolean;
  theme: 'light' | 'dark' | 'auto';
}
```

### 8.2 存储服务实现

```typescript
// services/localStorage.ts

import { Store } from 'tauri-plugin-store-api';

class LocalStorageService {
  private store: Store;

  constructor() {
    this.store = new Store('.app-data.dat');
  }

  // 任务历史
  async saveTaskHistory(tasks: StoredTaskHistory[]): Promise<void> {
    await this.store.set('taskHistory', tasks);
    await this.store.save();
  }

  async loadTaskHistory(): Promise<StoredTaskHistory[]> {
    return await this.store.get('taskHistory') || [];
  }

  // 文件关系
  async saveFileRelationships(relationships: StoredFileRelationship[]): Promise<void> {
    await this.store.set('fileRelationships', relationships);
    await this.store.save();
  }

  async loadFileRelationships(): Promise<StoredFileRelationship[]> {
    return await this.store.get('fileRelationships') || [];
  }

  // 应用设置
  async saveSettings(settings: AppSettings): Promise<void> {
    await this.store.set('settings', settings);
    await this.store.save();
  }

  async loadSettings(): Promise<AppSettings> {
    return await this.store.get('settings') || {
      apiBaseUrl: 'https://api.example.com',
      pollingInterval: 3000,
      maxHistoryRecords: 1000,
      enableNotifications: true,
      theme: 'auto'
    };
  }

  // 清除数据
  async clearHistory(): Promise<void> {
    await this.store.set('taskHistory', []);
    await this.store.save();
  }
}

export const localStorageService = new LocalStorageService();
```

### 8.3 存储位置

**Tauri 默认存储位置**：

- **Windows**: `%APPDATA%\{app_name}\`
- **macOS**: `~/Library/Application Support/{app_name}/`
- **Linux**: `~/.local/share/{app_name}/`

文件：`.app-data.dat`（JSON 格式）

---

## 9. 技术栈与依赖

### 9.1 前端依赖 (package.json)

```json
{
  "name": "cad-pdf-converter",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "@tauri-apps/api": "^1.5.0",
    "tauri-plugin-store-api": "^0.2.0",
    "pdfjs-dist": "^3.11.174",
    "lucide-svelte": "^0.294.0"
  },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3.0.0",
    "@tauri-apps/cli": "^1.5.0",
    "svelte": "^4.2.0",
    "svelte-check": "^3.6.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.55.0",
    "eslint-plugin-svelte": "^2.35.0",
    "prettier": "^3.1.0",
    "prettier-plugin-svelte": "^3.1.0"
  }
}
```

### 9.2 Rust 依赖 (Cargo.toml)

```toml
[package]
name = "cad-pdf-converter"
version = "0.1.0"
edition = "2021"

[dependencies]
tauri = { version = "1.5", features = ["dialog-all", "fs-all", "shell-open", "notification-all"] }
tauri-plugin-store = { version = "0.2" }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json", "multipart", "stream"] }
tokio = { version = "1.35", features = ["full"] }
futures-util = "0.3"
thiserror = "1.0"
log = "0.4"
env_logger = "0.11"

[dev-dependencies]
mockito = "1.2"

[build-dependencies]
tauri-build = { version = "1.5", features = [] }
```

### 9.3 工具链版本

| 工具 | 版本 | 用途 |
|------|------|------|
| Node.js | 18.x+ | 前端构建环境 |
| pnpm/npm | 8.x+ | 包管理器 |
| Rust | 1.75+ | Tauri 后端编译 |
| Tauri CLI | 1.5+ | 应用构建和打包 |
| TypeScript | 5.x | 类型系统 |
| Vite | 5.x | 前端构建工具 |

---

## 10. 项目目录结构

```
cad-pdf-converter/
├── src/                          # 前端源码 (Svelte + TypeScript)
│   ├── components/               # UI 组件
│   │   ├── upload/
│   │   │   ├── DropZone.svelte
│   │   │   ├── FileSelector.svelte
│   │   │   └── FileInfo.svelte
│   │   ├── task/
│   │   │   ├── TaskList.svelte
│   │   │   ├── TaskCard.svelte
│   │   │   ├── ProgressBar.svelte
│   │   │   └── StatusBadge.svelte
│   │   ├── pdf/
│   │   │   ├── PdfViewer.svelte
│   │   │   ├── PdfToolbar.svelte
│   │   │   └── PdfThumbnails.svelte
│   │   ├── relationship/
│   │   │   ├── FileRelationship.svelte
│   │   │   ├── CadFileCard.svelte
│   │   │   ├── PdfFileCard.svelte
│   │   │   └── ConnectionLine.svelte
│   │   ├── history/
│   │   │   ├── TaskHistory.svelte
│   │   │   ├── FilterBar.svelte
│   │   │   └── HistoryList.svelte
│   │   └── common/
│   │       ├── Button.svelte
│   │       ├── Modal.svelte
│   │       ├── Toast.svelte
│   │       ├── Spinner.svelte
│   │       └── ConfirmDialog.svelte
│   │
│   ├── stores/                   # 状态管理 (Svelte Stores)
│   │   ├── index.ts
│   │   ├── taskStore.ts
│   │   ├── fileStore.ts
│   │   ├── historyStore.ts
│   │   ├── relationshipStore.ts
│   │   ├── uiStore.ts
│   │   └── configStore.ts
│   │
│   ├── services/                 # 业务逻辑服务
│   │   ├── api.ts                # API 调用封装
│   │   ├── taskPoller.ts         # 任务轮询服务
│   │   ├── localStorage.ts       # 本地存储服务
│   │   ├── pdfService.ts         # PDF 处理服务
│   │   └── apiErrorHandler.ts    # 错误处理
│   │
│   ├── utils/                    # 工具函数
│   │   ├── formatters.ts         # 格式化工具
│   │   ├── validators.ts         # 验证工具
│   │   ├── constants.ts          # 常量定义
│   │   └── logger.ts             # 日志工具
│   │
│   ├── types/                    # TypeScript 类型定义
│   │   ├── task.ts
│   │   ├── file.ts
│   │   ├── api.ts
│   │   └── storage.ts
│   │
│   ├── styles/                   # 全局样式
│   │   ├── global.css
│   │   ├── variables.css
│   │   └── themes.css
│   │
│   ├── App.svelte                # 根组件
│   ├── main.ts                   # 入口文件
│   └── vite-env.d.ts             # Vite 类型声明
│
├── src-tauri/                    # Tauri 后端 (Rust)
│   ├── src/
│   │   ├── commands/             # Tauri Commands
│   │   │   ├── mod.rs
│   │   │   ├── file.rs           # 文件操作命令
│   │   │   ├── upload.rs         # 上传命令
│   │   │   ├── task.rs           # 任务查询命令
│   │   │   ├── download.rs       # 下载命令
│   │   │   └── storage.rs        # 存储命令
│   │   │
│   │   ├── services/             # Rust 服务层
│   │   │   ├── mod.rs
│   │   │   ├── http_client.rs    # HTTP 客户端封装
│   │   │   └── file_handler.rs   # 文件处理
│   │   │
│   │   ├── models/               # 数据模型
│   │   │   ├── mod.rs
│   │   │   ├── task.rs
│   │   │   └── response.rs
│   │   │
│   │   ├── error.rs              # 错误类型定义
│   │   ├── config.rs             # 配置管理
│   │   ├── main.rs               # 入口文件
│   │   └── lib.rs                # 库入口
│   │
│   ├── icons/                    # 应用图标
│   │   ├── icon.png
│   │   ├── icon.icns             # macOS
│   │   └── icon.ico              # Windows
│   │
│   ├── tauri.conf.json           # Tauri 配置文件
│   ├── Cargo.toml                # Rust 依赖配置
│   ├── Cargo.lock
│   └── build.rs                  # 构建脚本
│
├── public/                       # 静态资源
│   └── favicon.ico
│
├── docs/                         # 项目文档
│   ├── prd.md                    # 产品需求文档
│   ├── architecture.md           # 架构文档 (本文档)
│   └── api-spec.md               # API 规范
│
├── tests/                        # 测试文件
│   ├── unit/                     # 单元测试
│   ├── integration/              # 集成测试
│   └── e2e/                      # E2E 测试
│
├── .vscode/                      # VS Code 配置
│   └── settings.json
│
├── .eslintrc.cjs                 # ESLint 配置
├── .prettierrc                   # Prettier 配置
├── tsconfig.json                 # TypeScript 配置
├── svelte.config.js              # Svelte 配置
├── vite.config.ts                # Vite 配置
├── vitest.config.ts              # Vitest 配置
├── package.json                  # 前端依赖
├── pnpm-lock.yaml
├── .gitignore
└── README.md                     # 项目说明
```

---

## 11. 性能优化策略

### 11.1 前端性能优化

**1. Svelte 编译优化**
- 启用生产模式构建（自动 tree-shaking）
- 组件懒加载（动态导入）
- CSS 作用域优化

**2. PDF.js 性能优化**
- **懒加载页面**：仅渲染可见页面和前后各 2 页
- **Canvas 复用**：使用对象池避免频繁创建销毁
- **Web Worker**：PDF 解析在 Worker 中进行，不阻塞主线程
- **缓存策略**：已渲染页面缓存到内存

```typescript
// services/pdfService.ts

export class PdfService {
  private pageCache = new Map<number, HTMLCanvasElement>();
  private maxCacheSize = 20;

  async renderPage(pdf: any, pageNum: number): Promise<HTMLCanvasElement> {
    // 检查缓存
    if (this.pageCache.has(pageNum)) {
      return this.pageCache.get(pageNum)!;
    }

    // 渲染页面
    const page = await pdf.getPage(pageNum);
    const canvas = this.createCanvas(page);

    // 缓存管理（LRU）
    if (this.pageCache.size >= this.maxCacheSize) {
      const firstKey = this.pageCache.keys().next().value;
      this.pageCache.delete(firstKey);
    }

    this.pageCache.set(pageNum, canvas);
    return canvas;
  }
}
```

**3. 任务轮询优化**
- 使用指数退避策略减少请求频率
- 页面不可见时暂停轮询
- 多个任务共享轮询周期（批量查询）

**4. 虚拟滚动**
- 历史记录列表使用虚拟滚动（`svelte-virtual-list`）
- 仅渲染可见区域的 DOM 节点

### 11.2 Rust 后端性能优化

**1. 异步 I/O**
- 所有网络请求和文件操作使用 async/await
- 使用 Tokio 运行时的多线程调度

**2. 流式下载**
- PDF 下载使用流式传输，边下载边写入磁盘
- 避免将整个文件加载到内存

**3. 连接复用**
- HTTP 客户端使用连接池
- Keep-Alive 保持长连接

```rust
// 使用单例模式复用 HTTP 客户端
lazy_static! {
    static ref HTTP_CLIENT: reqwest::Client = reqwest::Client::builder()
        .pool_max_idle_per_host(10)
        .timeout(std::time::Duration::from_secs(60))
        .build()
        .unwrap();
}
```

### 11.3 网络优化

**1. 请求优化**
- API 响应使用 gzip 压缩
- 合理设置超时时间（上传 60s，查询 10s）
- 失败请求使用指数退避重试

**2. 并发控制**
- 限制同时进行的下载任务数（最多 3 个）
- 使用信号量控制并发

---

## 12. 安全考虑

### 12.1 Tauri 安全配置

**tauri.conf.json 安全设置**：

```json
{
  "tauri": {
    "allowlist": {
      "all": false,
      "fs": {
        "all": false,
        "readFile": true,
        "writeFile": true,
        "createDir": true,
        "scope": ["$APPDATA/*", "$DOWNLOAD/*"]
      },
      "dialog": {
        "all": false,
        "open": true,
        "save": true
      },
      "http": {
        "all": false,
        "request": true,
        "scope": ["https://api.example.com/*"]
      },
      "notification": {
        "all": true
      },
      "shell": {
        "all": false,
        "open": true
      }
    },
    "security": {
      "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src https://api.example.com"
    }
  }
}
```

### 12.2 数据验证

**前端验证**：
- 文件类型检查（仅允许 .dwg）
- 文件大小限制（建议 < 100 MB）
- 路径遍历攻击防护

**Rust 后端验证**：
- 文件扩展名白名单
- 文件 MIME 类型验证
- 路径规范化（防止路径遍历）

```rust
// 文件路径验证
fn validate_file_path(path: &str) -> Result<PathBuf, String> {
    let path_buf = PathBuf::from(path);

    // 检查文件是否存在
    if !path_buf.exists() {
        return Err("文件不存在".to_string());
    }

    // 检查扩展名
    if path_buf.extension().and_then(|s| s.to_str()) != Some("dwg") {
        return Err("仅支持 DWG 文件".to_string());
    }

    // 规范化路径（防止 ../ 等路径遍历）
    let canonical = path_buf.canonicalize()
        .map_err(|e| format!("路径解析失败: {}", e))?;

    Ok(canonical)
}
```

### 12.3 敏感数据处理

**不存储敏感信息**：
- API 密钥不硬编码，从环境变量或配置文件读取
- 本地存储不保存完整文件路径（仅文件名）
- 日志文件不记录敏感参数

**HTTPS 通信**：
- 所有 API 请求使用 HTTPS
- 验证 SSL 证书（不跳过证书验证）

---

## 13. 跨平台适配

### 13.1 平台差异处理

**文件路径**：
- 使用 Rust `std::path::PathBuf` 处理跨平台路径
- 前端使用正斜杠 `/`，Rust 自动转换

**文件对话框**：
- Tauri 的 `dialog` API 自动适配平台原生对话框

**通知**：
- Tauri 的 `notification` API 自动适配平台通知系统

### 13.2 UI 平台适配

**Windows 11**：
- 圆角窗口（`tauri.conf.json` 中 `decorations: true`）
- Fluent 设计语言（阴影、亚克力效果）

**macOS**：
- 毛玻璃效果（`window.setTransparent(true)`）
- 原生标题栏按钮

**Linux**：
- GTK 主题兼容
- 系统图标库集成

### 13.3 测试矩阵

| 平台 | 版本 | 测试重点 |
|------|------|---------|
| Windows | 10/11 | 文件路径、通知、安装程序 |
| macOS | 11+ (Big Sur) | 权限请求、代码签名、DMG 打包 |
| Linux | Ubuntu 20.04+, Fedora 36+ | 依赖库、AppImage 打包 |

---

## 14. 测试策略

### 14.1 前端测试

**单元测试（Vitest）**：
- Store 逻辑测试
- 工具函数测试
- 组件逻辑测试

```typescript
// stores/taskStore.test.ts

import { describe, it, expect } from 'vitest';
import { taskActions, tasks } from './taskStore';
import { get } from 'svelte/store';

describe('taskStore', () => {
  it('should add a task', () => {
    const task = {
      taskId: '123',
      fileName: 'test.dwg',
      fileSize: 1024,
      status: 'queued' as const,
      progress: 0,
      uploadTime: new Date().toISOString()
    };

    taskActions.addTask(task);

    const currentTasks = get(tasks);
    expect(currentTasks).toContainEqual(task);
  });
});
```

**组件测试（@testing-library/svelte）**：
- 交互测试
- 渲染测试

### 14.2 Rust 后端测试

**单元测试**：
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_file_path() {
        let result = validate_file_path("/path/to/file.dwg");
        assert!(result.is_ok());

        let result = validate_file_path("/path/to/file.pdf");
        assert!(result.is_err());
    }
}
```

**集成测试**：
- 使用 `mockito` 模拟 HTTP 响应
- 测试 Tauri Commands

### 14.3 E2E 测试

**工具**：Playwright 或 Tauri 的测试工具

**测试场景**：
- 完整文件上传流程
- 任务监控和进度更新
- PDF 预览和下载
- 历史记录管理

---

## 15. 部署与构建

### 15.1 开发环境

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm tauri dev
```

### 15.2 生产构建

```bash
# 构建应用
pnpm tauri build

# 输出位置：
# - Windows: src-tauri/target/release/bundle/msi/*.msi
# - macOS: src-tauri/target/release/bundle/dmg/*.dmg
# - Linux: src-tauri/target/release/bundle/appimage/*.AppImage
```

### 15.3 CI/CD

**GitHub Actions 示例**：

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
        os: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18

      - name: Setup Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install dependencies
        run: pnpm install

      - name: Build Tauri app
        run: pnpm tauri build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: app-${{ matrix.os }}
          path: src-tauri/target/release/bundle/
```

---

## 16. 技术风险与缓解措施

### 16.1 已识别风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| **PDF.js 大文件性能** | 高 | 中 | 懒加载、缓存、Web Worker |
| **跨平台文件路径** | 中 | 低 | 使用 PathBuf、充分测试 |
| **网络不稳定导致轮询失败** | 中 | 中 | 指数退避重试、离线缓存 |
| **本地存储数据损坏** | 中 | 低 | 数据校验、备份机制 |
| **API 接口变更** | 高 | 低 | 版本控制、适配层隔离 |

### 16.2 需架构师调查的领域

根据 PRD PM Checklist 报告，以下问题需深入研究：

**1. PDF.js vs 系统原生 PDF 查看器**
- **调查点**：性能对比、跨平台一致性、实现复杂度
- **建议**：MVP 阶段使用 PDF.js（一致性优先），未来版本可考虑原生方案

**2. Tauri 文件上传流式传输**
- **调查点**：reqwest 的 `Body::wrap_stream` 使用方式
- **建议**：参考 Tauri 官方文档和示例

**3. SVG 连线图响应式布局**
- **调查点**：SVG viewBox 动态计算、窗口 resize 事件处理
- **建议**：使用 `getBoundingClientRect()` 动态计算卡片位置

**4. 虚拟滚动实现**
- **调查点**：`svelte-virtual-list` 或自研方案
- **建议**：历史记录 > 100 条时启用虚拟滚动

---

## 17. 未来扩展性

### 17.1 后续版本路线图

**v1.0 (MVP)**：单文件处理、DWG 格式、桌面应用

**v2.0 (批量处理)**：
- 多文件同时上传
- 批量任务队列管理
- 批量下载（ZIP 打包）

**v3.0 (格式扩展)**：
- 支持 DXF 格式
- 支持其他 CAD 格式（DWF、DGN）

**v4.0 (云端集成)**：
- 云端存储（历史记录同步）
- 跨设备访问
- Web 版本

### 17.2 架构扩展点

**插件系统**（未来）：
- 支持第三方 PDF 渲染引擎
- 自定义文件处理流程

**多语言支持**：
- i18n 国际化框架集成

**高级配置**：
- API 端点自定义
- 主题切换
- 快捷键自定义

---

## 附录 A：关键代码示例

### A.1 轮询服务实现

```typescript
// services/taskPoller.ts

export class TaskPoller {
  private pollingIntervalId: number | null = null;
  private pollingInterval = 3000; // 3 秒
  private maxRetries = 3;

  start(taskId: string, onUpdate: (status: TaskStatus) => void) {
    this.stop(); // 停止之前的轮询

    let retryCount = 0;

    this.pollingIntervalId = window.setInterval(async () => {
      try {
        const status = await apiService.getTaskStatus(taskId);

        // 重置重试计数
        retryCount = 0;

        // 更新状态
        onUpdate(status);

        // 任务完成或失败，停止轮询
        if (status.status === 'completed' || status.status === 'failed') {
          this.stop();

          // 如果完成，触发 PDF 生成
          if (status.status === 'completed') {
            this.generatePdf(taskId);
          }
        }
      } catch (error) {
        console.error('轮询失败:', error);
        retryCount++;

        // 重试 3 次后停止
        if (retryCount >= this.maxRetries) {
          this.stop();
          onUpdate({
            taskId,
            status: 'failed',
            progress: 0,
            message: '连接失败，请检查网络'
          });
        }
      }
    }, this.pollingInterval);
  }

  stop() {
    if (this.pollingIntervalId !== null) {
      window.clearInterval(this.pollingIntervalId);
      this.pollingIntervalId = null;
    }
  }

  private async generatePdf(taskId: string) {
    try {
      const pdfInfo = await apiService.generatePdf(taskId);
      // 存储 PDF 信息到 Store
      relationshipActions.addPdf(taskId, pdfInfo);
    } catch (error) {
      console.error('PDF 生成失败:', error);
    }
  }
}

export const taskPoller = new TaskPoller();
```

### A.2 文件关系可视化组件

```svelte
<!-- components/relationship/FileRelationship.svelte -->

<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import CadFileCard from './CadFileCard.svelte';
  import PdfFileCard from './PdfFileCard.svelte';

  export let cadFile: CadFile;
  export let pdfFile: PdfFile;

  let cadCardElement: HTMLElement;
  let pdfCardElement: HTMLElement;
  let svgPath = '';

  function updateConnectionLine() {
    if (!cadCardElement || !pdfCardElement) return;

    const cadRect = cadCardElement.getBoundingClientRect();
    const pdfRect = pdfCardElement.getBoundingClientRect();

    const containerRect = cadCardElement.parentElement!.getBoundingClientRect();

    // 计算相对位置
    const x1 = cadRect.right - containerRect.left;
    const y1 = cadRect.top + cadRect.height / 2 - containerRect.top;
    const x2 = pdfRect.left - containerRect.left;
    const y2 = pdfRect.top + pdfRect.height / 2 - containerRect.top;

    // 贝塞尔曲线控制点
    const cx = (x1 + x2) / 2;

    svgPath = `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`;
  }

  onMount(() => {
    updateConnectionLine();
    window.addEventListener('resize', updateConnectionLine);
    return () => window.removeEventListener('resize', updateConnectionLine);
  });

  afterUpdate(updateConnectionLine);
</script>

<div class="relationship-container">
  <div class="cad-card" bind:this={cadCardElement}>
    <CadFileCard file={cadFile} />
  </div>

  <svg class="connection-svg">
    <defs>
      <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
        <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
      </marker>
    </defs>
    <path
      d={svgPath}
      stroke="#3b82f6"
      stroke-width="2"
      fill="none"
      marker-end="url(#arrowhead)"
      class="connection-line"
    />
  </svg>

  <div class="pdf-card" bind:this={pdfCardElement}>
    <PdfFileCard file={pdfFile} />
  </div>
</div>

<style>
  .relationship-container {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem;
  }

  .connection-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  .connection-line {
    transition: d 0.3s ease;
  }

  .connection-line:hover {
    stroke-width: 3;
    stroke: #2563eb;
  }
</style>
```

---

## 文档签署

**架构师**: Winston
**日期**: 2025-11-06
**状态**: ✅ 架构设计完成，待评审

**下一步**：
1. 架构评审会议
2. UX Expert 创建前端设计规范
3. Dev 团队根据本文档开始 Epic 1 实现

---

**文档结束**
