# API 模块文档

[根目录](../CLAUDE.md) > **api**

## 模块概述

**API 模块**是 CAD 文件自动化处理系统的 HTTP 服务层，基于 FastAPI 框架构建，提供 RESTful API 接口供外部系统调用。

**职责：**
- 提供 HTTP API 接口（任务提交、查询、状态追踪）
- 请求验证和响应格式化（Pydantic 模型）
- 异步任务处理和调度
- 健康检查和服务监控

**技术栈：**
- FastAPI 0.104+ - 现代高性能 Web 框架
- Uvicorn - ASGI 服务器
- Pydantic 2.0+ - 数据验证
- httpx - 异步 HTTP 客户端
- aiofiles - 异步文件操作

## 目录结构

```
api/
├── __init__.py                 # 包初始化
├── main.py                     # FastAPI 应用入口 ⭐
├── routers/                    # 路由层
│   ├── __init__.py
│   ├── tasks.py                # 任务管理路由
│   └── health.py               # 健康检查路由
├── schemas/                    # 数据模型层
│   ├── __init__.py
│   ├── task.py                 # 任务相关模型
│   └── response.py             # 统一响应模型
└── services/                   # 业务服务层
    ├── __init__.py
    ├── task_processor.py       # 任务处理器
    └── file_downloader.py      # 异步文件下载
```

## 核心组件

### 1. 应用入口 (`main.py`)

**职责：**
- 创建 FastAPI 应用实例
- 配置 CORS 中间件
- 注册路由
- 全局异常处理
- 启动/关闭事件处理

**关键代码：**
```python
app = FastAPI(
    title="DWG Processing API",
    description="DWG文件自动化处理API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 注册路由
app.include_router(health.router)
app.include_router(tasks.router)
```

**启动方式：**
```bash
# 开发模式
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 路由层 (`routers/`)

#### tasks.py - 任务管理路由

**接口列表：**

| 方法 | 路径 | 功能 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/api/v1/tasks/print` | 提交打印任务 | `PrintTaskRequest` | `TaskResponse` |
| GET | `/api/v1/tasks/{task_id}` | 查询任务详情 | - | `TaskDetailResponse` |
| GET | `/api/v1/tasks` | 查询任务列表 | Query 参数 | `TaskListResponse` |
| PUT | `/api/v1/tasks/{task_id}/cancel` | 取消任务 | - | `TaskResponse` |

**使用示例：**
```bash
# 提交打印任务
curl -X POST http://localhost:8000/api/v1/tasks/print \
  -H "Content-Type: application/json" \
  -d '{
    "dwg_url": "http://example.com/file.dwg",
    "config_name": "default",
    "callback_url": "http://callback.com/result"
  }'

# 查询任务状态
curl http://localhost:8000/api/v1/tasks/{task_id}
```

#### health.py - 健康检查路由

**接口：**
- `GET /health` - 服务健康检查
- `GET /health/db` - 数据库连接检查

**响应示例：**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-04T21:15:53+08:00",
  "database": "connected"
}
```

### 3. 数据模型层 (`schemas/`)

#### task.py - 任务模型

**核心模型：**

```python
class PrintTaskRequest(BaseModel):
    """打印任务请求"""
    dwg_url: str = Field(..., description="DWG文件下载地址")
    config_name: str = Field(default="default", description="配置名称")
    callback_url: Optional[str] = Field(None, description="回调地址")
    use_bplot: bool = Field(default=False, description="是否使用BPLOT工作流")

class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str
    created_at: datetime
```

#### response.py - 统一响应模型

**标准响应格式：**
```python
class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = Field(default=200, description="状态码")
    message: str = Field(default="success", description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now)
```

### 4. 业务服务层 (`services/`)

#### task_processor.py - 任务处理器

**职责：**
- 接收任务请求并入库
- 调度任务执行（异步/后台）
- 更新任务状态
- 处理任务失败和重试
- 执行回调通知

**关键流程：**
1. 验证请求参数
2. 创建任务记录（`dwg_process_tasks` 表）
3. 异步下载 DWG 文件
4. 调用 AutoCAD 工作流处理
5. 监控输出文件
6. 回调通知结果

#### file_downloader.py - 异步文件下载

**特性：**
- 异步下载（httpx）
- 断点续传
- 进度回调
- MD5 校验
- 超时控制

**使用示例：**
```python
from api.services.file_downloader import AsyncFileDownloader

async def download_file(url: str, save_path: str):
    downloader = AsyncFileDownloader()
    await downloader.download(
        url=url,
        save_path=save_path,
        progress_callback=lambda p: print(f"进度: {p}%")
    )
```

## 依赖关系

**内部依赖：**
- `src.models` - 数据库模型（`DWGProcessTask`, `AutoCADConfig`）
- `src.services` - 业务服务（`TaskService`, `AutoCADConfigService`）
- `src.utils` - 工具模块（`database`, `logger`, `config`）

**外部依赖：**
- FastAPI - Web 框架
- Pydantic - 数据验证
- SQLAlchemy - ORM（通过 src.models）
- httpx - 异步 HTTP 客户端
- aiofiles - 异步文件 I/O

**依赖图：**
```
api/routers/tasks.py
    ├─> api/schemas/task.py
    ├─> api/services/task_processor.py
    │       ├─> src/services/task_service.py
    │       ├─> src/services/autocad_config_service.py
    │       └─> api/services/file_downloader.py
    └─> src/utils/logger.py
```

## API 文档

### Swagger UI

访问地址：`http://localhost:8000/docs`

**特性：**
- 交互式 API 文档
- 在线测试接口
- 请求/响应示例
- 模型定义查看

### ReDoc

访问地址：`http://localhost:8000/redoc`

**特性：**
- 美观的文档展示
- 导出 OpenAPI 规范
- 搜索功能

## 配置说明

API 服务相关配置位于 `config/config.yaml`：

```yaml
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: true  # 开发模式
  log_level: info

server:
  base_url: http://example.com/api
  timeout: 300
  max_retries: 3
```

**环境变量覆盖：**
```bash
export CAD_API_HOST=0.0.0.0
export CAD_API_PORT=8000
export CAD_API_WORKERS=4
```

## 启动脚本

### Windows

**start_api.bat**
```batch
@echo off
echo Starting DWG Processing API...
call venv\Scripts\activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Linux/Mac

**start_api.sh**
```bash
#!/bin/bash
echo "Starting DWG Processing API..."
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 测试

### 单元测试

```bash
# 运行 API 测试
pytest tests/api/ -v

# 测试覆盖率
pytest tests/api/ --cov=api --cov-report=html
```

### 集成测试

```bash
# 使用测试脚本
python scripts/test_api.py

# 使用 curl 测试
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/tasks/print \
  -H "Content-Type: application/json" \
  -d @test_data/task_request.json
```

## 常见问题

### 1. 端口被占用

**问题：** `Address already in use: 0.0.0.0:8000`

**解决：**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### 2. CORS 错误

**问题：** 跨域请求被拒绝

**解决：** 在 `main.py` 中配置 CORS：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 异步任务超时

**问题：** 长时间运行的任务导致请求超时

**解决：** 使用后台任务：
```python
from fastapi import BackgroundTasks

@app.post("/tasks")
async def create_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {"status": "accepted"}
```

## 性能优化

### 1. 异步处理

- 所有 I/O 操作使用 `async/await`
- 使用 `httpx.AsyncClient` 进行异步 HTTP 请求
- 使用 `aiofiles` 进行异步文件操作

### 2. 连接池

- 数据库连接池（SQLAlchemy）
- HTTP 连接复用（httpx Client）

### 3. 并发控制

```python
# 限制并发任务数
from asyncio import Semaphore

semaphore = Semaphore(10)  # 最多10个并发任务

async def process_task(task_id: str):
    async with semaphore:
        await do_work(task_id)
```

## 安全建议

1. **认证授权：** 添加 API Key 或 JWT 认证
2. **速率限制：** 使用 `slowapi` 限制请求频率
3. **输入验证：** Pydantic 自动验证，额外检查敏感字段
4. **HTTPS：** 生产环境使用 SSL/TLS
5. **日志审计：** 记录所有 API 调用和错误

## 监控和日志

### 日志记录

```python
from src.utils.logger import get_logger
logger = get_logger()

logger.info(f"Task created: {task_id}")
logger.error(f"Task failed: {task_id}, error: {error}")
```

### 健康检查

- `/health` - 基础健康检查
- `/health/db` - 数据库连接检查
- 配合 Kubernetes Liveness/Readiness Probes

## 相关文档

- [根目录文档](../CLAUDE.md)
- [核心模块文档](../src/CLAUDE.md)
- [数据库配置指南](../docs/DATABASE_CONFIG_GUIDE.md)
- [API 使用指南](../docs/API_GUIDE.md)

---

**最后更新：** 2025-11-04
**维护者：** 老王团队
