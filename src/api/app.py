#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据生成API
"""

from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
import uvicorn
from .data_generator import generate_training_data

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
    ruleids: Optional[str] = Query(None, description="规则ID过滤，格式如'1,2,3'或'-1,-2,-3'，正数表示包含，负数表示排除")
):
    """
    生成训练数据接口
    
    Args:
        business_object: 业务对象名称
        total_samples: 总样本数
        variations_per_rule: 每个规则的变种数
        ruleids: 规则ID过滤字符串
        
    Returns:
        JSON对象，包含生成的对话数据和原始数据
    """
    try:
        # 调用数据生成函数
        dialogs, raw_data = generate_training_data(
            business_object=business_object,
            total_samples=total_samples,
            variations_per_rule=variations_per_rule,
            ruleids=ruleids
        )
        
        # 返回生成的数据
        return {
            "status": "success",
            "message": f"成功生成{len(dialogs)}条训练数据",
            "data": {
                "dialogs": dialogs,
                "raw_data": raw_data
            }
        }
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