#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基础字典API路由模块
处理与基础元素(baseElements)相关的请求
"""

import os
import json
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# 基础元素目录
BASE_ELEMENTS_DIR = os.path.join(BASE_DIR, "src", "entity", "baseElements")

# 创建路由
router = APIRouter(
    prefix="/api/dict/base",
    tags=["基础字典"],
    responses={404: {"description": "未找到"}},
)

# 工具函数：读取JSON文件
def read_json_file(file_path: str) -> Dict:
    """读取JSON文件并返回解析后的数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件未找到：{os.path.basename(file_path)}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail=f"JSON解析错误：{os.path.basename(file_path)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件错误：{str(e)}")

# 工具函数：写入JSON文件
def write_json_file(file_path: str, data: Dict) -> bool:
    """将数据写入JSON文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入文件错误：{str(e)}")

@router.get("/")
async def get_all_business_objects() -> List:
    """
    获取所有基础字典业务对象列表
    """
    try:
        # 读取索引文件
        index_file_path = os.path.join(BASE_ELEMENTS_DIR, "index.json")
        return read_json_file(index_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取业务对象列表失败：{str(e)}")

@router.get("/{business_object}")
async def get_business_object_data(business_object: str = Path(..., description="业务对象名称，例如searchStaff")) -> Dict:
    """
    获取指定业务对象的基础字典数据
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        return read_json_file(file_path)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取业务对象数据失败：{str(e)}")

@router.post("/{business_object}")
async def update_business_object_data(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    data: Dict = Body(..., description="业务对象数据")
) -> Dict:
    """
    更新指定业务对象的基础字典数据
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        # 验证文件存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"业务对象不存在：{business_object}")
        
        # 写入数据
        write_json_file(file_path, data)
        return {"status": "success", "message": f"业务对象 {business_object} 更新成功"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新业务对象数据失败：{str(e)}")

@router.get("/{business_object}/elements")
async def get_business_object_elements(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff")
) -> List:
    """
    获取指定业务对象的基础元素列表
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        data = read_json_file(file_path)
        return data.get("baseDataList", [])
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取业务对象元素失败：{str(e)}")

@router.get("/{business_object}/elements/{element_number}")
async def get_business_object_element(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    element_number: str = Path(..., description="元素编号，例如01")
) -> Dict:
    """
    获取指定业务对象的特定元素
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        data = read_json_file(file_path)
        elements = data.get("baseDataList", [])
        
        # 查找匹配的元素
        for element in elements:
            if element.get("number") == element_number:
                return element
        
        raise HTTPException(status_code=404, detail=f"未找到编号为 {element_number} 的元素")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"获取业务对象元素失败：{str(e)}")

@router.post("/{business_object}/elements")
async def add_business_object_element(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    element: Dict = Body(..., description="要添加的元素数据")
) -> Dict:
    """
    为指定业务对象添加新元素
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        data = read_json_file(file_path)
        elements = data.get("baseDataList", [])
        
        # 检查元素编号是否已存在
        for existing_element in elements:
            if existing_element.get("number") == element.get("number"):
                raise HTTPException(status_code=400, detail=f"编号为 {element.get('number')} 的元素已存在")
        
        # 添加新元素
        elements.append(element)
        data["baseDataList"] = elements
        
        # 保存更新后的数据
        write_json_file(file_path, data)
        
        return {"status": "success", "message": "元素添加成功", "element": element}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"添加元素失败：{str(e)}")

@router.put("/{business_object}/elements/{element_number}")
async def update_business_object_element(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    element_number: str = Path(..., description="元素编号，例如01"),
    element: Dict = Body(..., description="更新后的元素数据")
) -> Dict:
    """
    更新指定业务对象的特定元素
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        data = read_json_file(file_path)
        elements = data.get("baseDataList", [])
        
        # 查找并更新元素
        found = False
        for i, existing_element in enumerate(elements):
            if existing_element.get("number") == element_number:
                # 保持原有编号
                element["number"] = element_number
                elements[i] = element
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail=f"未找到编号为 {element_number} 的元素")
        
        # 保存更新后的数据
        data["baseDataList"] = elements
        write_json_file(file_path, data)
        
        return {"status": "success", "message": f"元素 {element_number} 更新成功", "element": element}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"更新元素失败：{str(e)}")

@router.delete("/{business_object}/elements/{element_number}")
async def delete_business_object_element(
    business_object: str = Path(..., description="业务对象名称，例如searchStaff"),
    element_number: str = Path(..., description="元素编号，例如01")
) -> Dict:
    """
    删除指定业务对象的特定元素
    """
    try:
        file_path = os.path.join(BASE_ELEMENTS_DIR, f"{business_object}.json")
        data = read_json_file(file_path)
        elements = data.get("baseDataList", [])
        
        # 查找并删除元素
        original_length = len(elements)
        elements = [e for e in elements if e.get("number") != element_number]
        
        if len(elements) == original_length:
            raise HTTPException(status_code=404, detail=f"未找到编号为 {element_number} 的元素")
        
        # 保存更新后的数据
        data["baseDataList"] = elements
        write_json_file(file_path, data)
        
        return {"status": "success", "message": f"元素 {element_number} 删除成功"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"删除元素失败：{str(e)}") 