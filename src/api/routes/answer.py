#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
处理回答元素相关的路由
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, List, Any, Optional
from pathlib import Path as FilePath
import os
import json
from pydantic import BaseModel

# 创建路由
router = APIRouter()

# 定义数据模型
class AnswerElement(BaseModel):
    name: str
    nameCN: str
    relateToBase: Optional[str] = "无"
    isStatic: Optional[str] = "否"
    staticValue: Optional[str] = "无"

class AnswerElementList(BaseModel):
    answerObject: str
    answerElements: List[AnswerElement]

# 获取项目根目录路径
BASE_DIR = FilePath(__file__).resolve().parent.parent.parent.parent
ANSWER_DIR = BASE_DIR / "src" / "entity" / "answerElements"

# 辅助函数：读取文件
def read_json_file(filepath: FilePath) -> Dict:
    """读取JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")

# 辅助函数：写入文件
def write_json_file(filepath: FilePath, data: Dict) -> None:
    """写入JSON文件"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入文件失败: {str(e)}")

@router.get("/answer/", response_model=List[Dict])
async def get_answer_types():
    """
    获取所有回答元素类型
    """
    try:
        # 读取索引文件
        index_path = ANSWER_DIR / "index.json"
        if not index_path.exists():
            raise HTTPException(status_code=404, detail="索引文件不存在")
        
        answer_types = read_json_file(index_path)
        return answer_types
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回答元素类型失败: {str(e)}")

@router.get("/answer/{answer_type}/elements", response_model=Dict)
async def get_answer_elements(answer_type: str = Path(..., description="回答元素类型")):
    """
    获取指定类型的回答元素
    """
    try:
        # 检查文件是否存在
        file_path = ANSWER_DIR / f"{answer_type}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"回答元素文件 {answer_type}.json 不存在")
        
        # 读取文件内容
        answer_data = read_json_file(file_path)
        return answer_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回答元素失败: {str(e)}")

@router.post("/answer/{answer_type}", response_model=Dict)
async def update_answer_elements(answer_type: str, answer_data: Dict):
    """
    更新回答元素
    """
    try:
        # 检查文件是否存在
        file_path = ANSWER_DIR / f"{answer_type}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"回答元素文件 {answer_type}.json 不存在")
        
        # 写入文件
        write_json_file(file_path, answer_data)
        return {"status": "success", "message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新回答元素失败: {str(e)}") 