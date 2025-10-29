"""
健康检查路由

简单的健康检查接口，老王我最喜欢简单的东西了！
"""

from fastapi import APIRouter
from datetime import datetime

from api.schemas.response import success_response


router = APIRouter(tags=["health"])


@router.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口

    Returns:
        服务状态和时间戳
    """
    return success_response(
        data={
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "DWG Process API"
        },
        message="服务正常运行"
    )


@router.get("/", summary="根路径")
async def root():
    """根路径重定向到API文档"""
    return {
        "message": "DWG Processing API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }
