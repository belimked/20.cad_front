#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成API
"""

from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
import uvicorn
from src.service.qwen_api_service import generate_and_save_data

# 创建FastAPI应用
app = FastAPI(
    title="训练数据生成API",
    description="用于生成AI训练数据的API服务",
    version="1.0.0"
)

@app.get("/")
async def root():
    """API根路径，返回API信息"""
    return {"message": "训练数据生成API服务", "version": "1.0.0"}

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

def start_server():
    """启动API服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start_server() 