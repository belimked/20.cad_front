"""
API响应格式定义

统一的API响应格式，符合老王的KISS原则！
"""

from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """统一API响应格式"""

    code: int  # 状态码（200=成功，其他=失败）
    message: str  # 消息
    data: Optional[T] = None  # 数据

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "成功",
                "data": {}
            }
        }


def success_response(data: Any = None, message: str = "成功") -> dict:
    """
    成功响应

    Args:
        data: 返回数据
        message: 消息

    Returns:
        响应字典
    """
    return {
        "code": 200,
        "message": message,
        "data": data
    }


def error_response(message: str, code: int = 400, data: Any = None) -> dict:
    """
    错误响应

    Args:
        message: 错误消息
        code: 错误码
        data: 额外数据

    Returns:
        响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }
