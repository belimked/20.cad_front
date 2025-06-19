#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成API
"""

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from typing import Optional, List
import os
import uvicorn
import argparse
from src.service.qwen_api_service import generate_and_save_data
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys

# 添加父目录到路径
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# 导入路由模块
from src.api.routes import base_dict_router, relationship_router, answer_router, generate_router, evaluation_analysis_router

# 获取项目根目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "src", "static")

# 创建FastAPI应用
app = FastAPI(
    title="训练数据生成API",
    description="用于生成AI训练数据的API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(base_dict_router)
app.include_router(base_dict_router, prefix="/api/dict", tags=["基础字典"])
app.include_router(relationship_router, prefix="/api", tags=["关系规则"])
app.include_router(answer_router, prefix="/api", tags=["回答元素"])
app.include_router(generate_router, prefix="/api", tags=["数据生成"])
app.include_router(evaluation_analysis_router, prefix="/api", tags=["评估分析"])

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """API根路径，返回API信息或重定向到首页"""
    # 如果静态目录中存在index.html，则返回该文件
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    # 否则返回API信息
    return {"message": "训练数据生成API服务", "version": "1.0.0"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "favicon.ico"))

@app.post("/api/generate-data")
async def generate_data(
    business_object: str = Query(..., description="业务对象代码，例如searchStaff、updateCargo等"),
    total_samples: int = Query(100, description="要生成的总样本数"),
    variations_per_rule: int = Query(2, description="每个规则的变种数量"),
    ruleids: Optional[str] = Query(None, description="规则ID过滤，格式如'1,2,3'或'-1,-2,-3'，正数表示包含，负数表示排除"),
    keyword: Optional[str] = Query(None, description="关键字过滤，多个关键字用逗号分隔")
):
    """
    生成训练数据接口
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串
        keyword: 关键字过滤，多个关键字用逗号分隔
        
    Returns:
        JSON对象，包含生成数据的统计信息和示例
    """
    try:
        # 调用qwen_api_service的生成数据功能
        result = generate_and_save_data(
            business_object=business_object,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=ruleids,
            keyword=keyword,
            output_dir="outputs/data"
        )
        
        # 直接返回结果
        return result
    except ValueError as e:
        # 参数错误
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # 其他错误
        raise HTTPException(status_code=500, detail=f"数据生成失败: {str(e)}")

def start_server(host="0.0.0.0", port=8000):
    """启动API服务器"""
    print(f"启动API服务，监听地址: {host}:{port}")
    print(f"静态文件目录: {STATIC_DIR}")
    print(f"访问静态页面: http://{host}:{port}/static/index.html")
    print(f"访问API文档: http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # 添加命令行参数解析
    parser = argparse.ArgumentParser(description="训练数据生成API服务")
    parser.add_argument("--host", default="0.0.0.0", help="服务监听的主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务监听的端口")
    args = parser.parse_args()
    
    # 使用命令行参数启动服务
    print(f"正在启动API服务于 {args.host}:{args.port}")
    start_server(host=args.host, port=args.port) 