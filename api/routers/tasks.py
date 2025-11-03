"""
任务相关API路由

这个SB路由负责处理任务的增删改查，艹！
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional

from api.schemas.task import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskListItem,
    TaskStepInfo
)
from api.schemas.response import success_response, error_response
from api.services.task_processor import TaskProcessor
from src.utils.database import SessionLocal
from src.services.task_service import DWGTaskService


router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


# ============================================================================
# 依赖注入
# ============================================================================

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# API接口
# ============================================================================

@router.post("/print", summary="提交打印任务")
async def create_print_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    提交DWG文件打印任务

    该接口会：
    1. 创建任务记录
    2. 异步下载DWG文件
    3. 根据use_bplot参数选择工作流：
       - use_bplot=false（默认）：使用标准配置工作流，支持完整的PDF提取和配置化打印
       - use_bplot=true：使用bplot批量打印工作流，打开文件后执行AutoCAD的BPLOT命令
    4. 记录每一步日志

    请求参数:
        - dwg_url: DWG文件下载地址（必填）
        - config_name: 配置名称（可选，默认为"default"）
        - callback_url: 完成后回调地址（可选）
        - use_bplot: 是否使用bplot工作流（可选，默认为false）

    Args:
        request: 任务创建请求
        background_tasks: 后台任务
        db: 数据库会话

    Returns:
        任务ID和状态
    """
    try:
        task_service = DWGTaskService(db)

        # 创建任务
        task = task_service.create_task(
            dwg_url=request.dwg_url,
            config_name=request.config_name or 'default',
            callback_url=request.callback_url,
            use_bplot=request.use_bplot
        )

        # 添加到后台任务队列（异步处理）
        processor = TaskProcessor()
        background_tasks.add_task(processor.process_task, task.task_id)

        # 返回任务信息
        response_data = TaskCreateResponse(
            task_id=task.task_id,
            status=task.status,
            created_at=task.created_at.isoformat()
        )

        return success_response(
            data=response_data.model_dump(),
            message="任务创建成功"
        )

    except Exception as e:
        return error_response(
            message=f"创建任务失败: {str(e)}",
            code=500
        )


@router.get("/{task_id}", summary="查询任务详情")
async def get_task_detail(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    查询任务详情

    包含任务基本信息和所有步骤日志

    Args:
        task_id: 任务ID
        db: 数据库会话

    Returns:
        任务详情
    """
    try:
        task_service = DWGTaskService(db)

        # 获取任务
        task = task_service.get_task(task_id)
        if not task:
            return error_response(
                message=f"任务不存在: {task_id}",
                code=404
            )

        # 获取步骤日志
        steps = task_service.get_task_steps(task_id)

        # 构建响应
        response_data = TaskDetailResponse(
            task_id=task.task_id,
            dwg_url=task.dwg_url,
            dwg_filename=task.dwg_filename,
            local_path=task.local_path,
            file_size=task.file_size,
            status=task.status,
            current_step=task.current_step,
            progress=task.progress,
            error_message=task.error_message,
            config_name=task.config_name,
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            created_at=task.created_at.isoformat(),
            steps=[
                TaskStepInfo(
                    step_name=step.step_name,
                    step_order=step.step_order,
                    status=step.status,
                    message=step.message,
                    error_message=step.error_message,
                    started_at=step.started_at.isoformat() if step.started_at else None,
                    completed_at=step.completed_at.isoformat() if step.completed_at else None,
                    duration_seconds=float(step.duration_seconds) if step.duration_seconds else None
                )
                for step in steps
            ]
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        return error_response(
            message=f"查询任务失败: {str(e)}",
            code=500
        )


@router.get("", summary="查询任务列表")
async def list_tasks(
    status: Optional[str] = Query(None, description="状态过滤"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db)
):
    """
    查询任务列表（分页）

    Args:
        status: 状态过滤（pending/downloading/processing/completed/failed）
        page: 页码（从1开始）
        size: 每页大小（1-100）
        db: 数据库会话

    Returns:
        任务列表
    """
    try:
        task_service = DWGTaskService(db)

        # 查询任务
        tasks, total = task_service.list_tasks(
            status=status,
            page=page,
            size=size
        )

        # 构建响应
        response_data = TaskListResponse(
            total=total,
            page=page,
            size=size,
            items=[
                TaskListItem(
                    task_id=task.task_id,
                    dwg_filename=task.dwg_filename,
                    status=task.status,
                    progress=task.progress,
                    current_step=task.current_step,
                    created_at=task.created_at.isoformat()
                )
                for task in tasks
            ]
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        return error_response(
            message=f"查询任务列表失败: {str(e)}",
            code=500
        )
