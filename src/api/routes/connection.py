#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
连接符管理API路由模块
处理与连接符(connection)相关的请求
"""

from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, List, Any
from pathlib import Path as FilePath
import json
import os
from pydantic import BaseModel

# 导入连接符服务
from src.service.common.connection import get_connection_service

# 创建路由
router = APIRouter()

# 获取项目根目录
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent.parent
CONNECTION_DIR = BASE_DIR / "src" / "entity" / "connection"

class ConnectionUpdateData(BaseModel):
    """连接符更新数据模型"""
    businessObject: str
    connectionList: List[Dict]

@router.get("/connection/")
async def get_available_business_objects():
    """获取所有可用的业务对象列表"""
    try:
        connection_service = get_connection_service()
        business_objects = connection_service.get_available_business_objects()
        
        # 获取每个业务对象的详细信息
        result = []
        for business_object in business_objects:
            info = connection_service.get_connection_info(business_object)
            connections = connection_service.get_connections(business_object)
            
            result.append({
                "id": business_object,
                "name": info.get("description", business_object) if info else business_object,
                "description": info.get("description", "业务对象连接关系") if info else "业务对象连接关系",
                "connectionCount": len(connections),
                "connections": connections
            })
        
        return {
            "businessObjects": result,
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取业务对象列表失败: {str(e)}")

@router.get("/connection/{business_object}")
async def get_connection_data(business_object: str = Path(..., description="业务对象名称，例如searchStaff")):
    """获取指定业务对象的连接符数据"""
    try:
        connection_service = get_connection_service()
        
        # 检查业务对象是否存在
        available_objects = connection_service.get_available_business_objects()
        if business_object not in available_objects:
            raise HTTPException(status_code=404, detail=f"业务对象 '{business_object}' 不存在")
        
        # 读取连接符文件
        connection_file = CONNECTION_DIR / f"{business_object}.json"
        if not connection_file.exists():
            # 如果文件不存在，创建默认结构
            default_data = {
                "businessObject": business_object,
                "connectionList": [
                    {
                        "id": 1,
                        "description": "业务对象连接",
                        "connections": []
                    }
                ]
            }
            return default_data
        
        with open(connection_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取连接符数据失败: {str(e)}")

@router.post("/connection/{business_object}")
async def update_connection_data(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    update_data: ConnectionUpdateData = Body(..., description="连接符更新数据")
):
    """更新指定业务对象的连接符数据"""
    try:
        connection_service = get_connection_service()
        
        # 检查业务对象是否存在
        available_objects = connection_service.get_available_business_objects()
        if business_object not in available_objects:
            raise HTTPException(status_code=404, detail=f"业务对象 '{business_object}' 不存在")
        
        # 验证数据
        if update_data.businessObject != business_object:
            raise HTTPException(status_code=400, detail="业务对象名称不匹配")
        
        # 验证连接符格式
        for conn_list in update_data.connectionList:
            if "connections" in conn_list:
                for connection in conn_list["connections"]:
                    if not isinstance(connection, str) or "," not in connection:
                        raise HTTPException(status_code=400, detail=f"连接符格式错误: {connection}")
                    
                    parts = connection.split(",")
                    if len(parts) != 2:
                        raise HTTPException(status_code=400, detail=f"连接符格式错误: {connection}")
                    
                    # 验证编码格式（应该是2位数字）
                    for part in parts:
                        part = part.strip()
                        if not part.isdigit() or len(part) != 2:
                            raise HTTPException(status_code=400, detail=f"连接符编码格式错误: {part}，应为2位数字")
        
        # 保存到文件
        connection_file = CONNECTION_DIR / f"{business_object}.json"
        
        # 确保目录存在
        connection_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(connection_file, 'w', encoding='utf-8') as f:
            json.dump(update_data.dict(), f, ensure_ascii=False, indent=2)
        
        # 清除缓存以确保下次读取最新数据
        if hasattr(connection_service, 'connection_cache'):
            connection_service.connection_cache.pop(business_object, None)
        
        return {
            "message": f"业务对象 '{business_object}' 的连接符已成功更新",
            "businessObject": business_object,
            "connectionCount": sum(len(conn_list.get("connections", [])) for conn_list in update_data.connectionList)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新连接符数据失败: {str(e)}")

@router.get("/connection/{business_object}/connections")
async def get_connections_only(business_object: str = Path(..., description="业务对象名称")):
    """获取指定业务对象的连接符列表（仅返回连接符数组）"""
    try:
        connection_service = get_connection_service()
        connections = connection_service.get_connections(business_object)
        
        return {
            "businessObject": business_object,
            "connections": connections,
            "count": len(connections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取连接符列表失败: {str(e)}")

@router.get("/connection/{business_object}/random")
async def get_random_connection(business_object: str = Path(..., description="业务对象名称")):
    """获取指定业务对象的随机连接符"""
    try:
        connection_service = get_connection_service()
        random_connection = connection_service.get_random_connection(business_object)
        
        if random_connection is None:
            raise HTTPException(status_code=404, detail=f"业务对象 '{business_object}' 没有可用的连接符")
        
        return {
            "businessObject": business_object,
            "connection": random_connection
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取随机连接符失败: {str(e)}")

@router.delete("/connection/{business_object}")
async def reset_connection_data(business_object: str = Path(..., description="业务对象名称")):
    """重置指定业务对象的连接符数据"""
    try:
        connection_service = get_connection_service()
        
        # 检查业务对象是否存在
        available_objects = connection_service.get_available_business_objects()
        if business_object not in available_objects:
            raise HTTPException(status_code=404, detail=f"业务对象 '{business_object}' 不存在")
        
        # 创建默认数据
        default_data = {
            "businessObject": business_object,
            "connectionList": [
                {
                    "id": 1,
                    "description": "业务对象连接",
                    "connections": []
                }
            ]
        }
        
        # 保存到文件
        connection_file = CONNECTION_DIR / f"{business_object}.json"
        with open(connection_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        
        # 清除缓存
        if hasattr(connection_service, 'connection_cache'):
            connection_service.connection_cache.pop(business_object, None)
        
        return {
            "message": f"业务对象 '{business_object}' 的连接符已重置",
            "businessObject": business_object
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置连接符数据失败: {str(e)}") 