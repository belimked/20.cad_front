"""
FastAPI主应用

DWG文件处理HTTP服务，老王我精心打造的API服务，艹！

启动命令:
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import tasks, health


# ============================================================================
# 创建FastAPI应用
# ============================================================================

app = FastAPI(
    title="DWG Processing API",
    description="""
    ## DWG文件处理API服务

    提供DWG文件自动化处理功能，包括：
    - 📥 文件下载
    - 🖨️ AutoCAD打印
    - 📊 进度追踪
    - 📝 日志记录

    ### 核心功能
    - 提交打印任务（POST /api/v1/tasks/print）
    - 查询任务详情（GET /api/v1/tasks/{task_id}）
    - 查询任务列表（GET /api/v1/tasks）

    ### 作者
    老王团队 - 专业暴躁技术流
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# 中间件配置
# ============================================================================

# CORS配置（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 注册路由
# ============================================================================

app.include_router(health.router)
app.include_router(tasks.router)


# ============================================================================
# 异常处理
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )


# ============================================================================
# 启动事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("=" * 80)
    print("DWG Processing API 启动中...")
    print("=" * 80)
    print(f"📚 API文档: http://localhost:8000/docs")
    print(f"📖 ReDoc: http://localhost:8000/redoc")
    print(f"💚 健康检查: http://localhost:8000/health")
    print("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("\n" + "=" * 80)
    print("DWG Processing API 关闭")
    print("=" * 80)


# ============================================================================
# 开发模式运行
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式：代码修改自动重载
        log_level="info"
    )
