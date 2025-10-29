"""
任务相关Schema定义

Pydantic数据模型，用于API请求和响应验证
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class TaskCreateRequest(BaseModel):
    """创建任务请求"""

    dwg_url: str = Field(..., description="DWG文件下载地址")
    config_name: Optional[str] = Field("default", description="配置名称")
    callback_url: Optional[str] = Field(None, description="完成后回调地址")

    class Config:
        json_schema_extra = {
            "example": {
                "dwg_url": "http://example.com/files/drawing.dwg",
                "config_name": "default",
                "callback_url": "http://example.com/callback"
            }
        }


class TaskCreateResponse(BaseModel):
    """创建任务响应"""

    task_id: str
    status: str
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_20251029_171234_abc123",
                "status": "pending",
                "created_at": "2025-10-29T17:12:34"
            }
        }


class TaskStepInfo(BaseModel):
    """任务步骤信息"""

    step_name: str
    step_order: int
    status: str
    message: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None


class TaskDetailResponse(BaseModel):
    """任务详情响应"""

    task_id: str
    dwg_url: str
    dwg_filename: Optional[str] = None
    local_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    current_step: Optional[str] = None
    progress: int
    error_message: Optional[str] = None
    config_name: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str
    steps: List[TaskStepInfo] = []


class TaskListItem(BaseModel):
    """任务列表项"""

    task_id: str
    dwg_filename: Optional[str] = None
    status: str
    progress: int
    current_step: Optional[str] = None
    created_at: str


class TaskListResponse(BaseModel):
    """任务列表响应"""

    total: int
    page: int
    size: int
    items: List[TaskListItem]
