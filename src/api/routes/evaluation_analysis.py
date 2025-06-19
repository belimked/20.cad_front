#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
评估分析API路由模块

提供评估文件分析相关的API接口
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.service.evaluation_analysis import EvaluationAnalyzer, TrainingGuideGenerator
from src.config.config_loader import load_evaluation_analysis_config

# 创建路由器
router = APIRouter()

# 全局任务状态存储（生产环境建议使用Redis等）
task_status: Dict[str, Dict[str, Any]] = {}

# 配置
config = load_evaluation_analysis_config()
TEMP_DIR = "outputs/temp"
REPORTS_DIR = "outputs/reports"

# 确保目录存在
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    file_id: str
    generate_report: bool = True
    report_format: str = "html"


class AnalysisStatus(BaseModel):
    """分析状态模型"""
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 - 1.0
    message: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_path: Optional[str] = None
    report_path: Optional[str] = None


def background_analysis_task(task_id: str, file_path: str, generate_report: bool = True):
    """后台分析任务"""
    try:
        # 更新任务状态为运行中
        task_status[task_id].update({
            "status": "running",
            "progress": 0.1,
            "message": "开始分析评估文件...",
            "start_time": datetime.now()
        })
        
        # 初始化分析器
        analyzer = EvaluationAnalyzer(config)
        
        # 更新进度
        task_status[task_id].update({
            "progress": 0.3,
            "message": "解析评估文件..."
        })
        
        # 执行分析
        analysis_result = analyzer.analyze_file(file_path)
        
        # 更新进度
        task_status[task_id].update({
            "progress": 0.8,
            "message": "生成分析报告..."
        })
        
        result_data = {
            "analysis_result": analysis_result.to_dict(),
            "executive_summary": analysis_result.get_executive_summary(),
            "actionable_items": analysis_result.get_actionable_items()
        }
        
        # 保存分析结果
        result_filename = f"analysis_result_{task_id}.json"
        result_path = os.path.join(TEMP_DIR, result_filename)
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2, default=str)
        
        report_path = None
        if generate_report:
            # 生成HTML报告
            from src.service.evaluation_analysis import ReportGenerator
            report_generator = ReportGenerator(config)
            # 传递评估记录（如果可用）
            evaluation_records = getattr(analysis_result, '_evaluation_records', None)
            report_path = report_generator.generate_html_report(analysis_result, REPORTS_DIR, evaluation_records)
        
        # 更新任务状态为完成
        task_status[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "分析完成",
            "end_time": datetime.now(),
            "result_path": result_path,
            "report_path": report_path
        })
        
        # 保存评估记录，以便其他功能使用
        if evaluation_records:
            task_status[task_id]["evaluation_records"] = evaluation_records
        
    except Exception as e:
        # 更新任务状态为失败
        task_status[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"分析失败: {str(e)}",
            "end_time": datetime.now()
        })


@router.post("/evaluation/upload", summary="上传评估文件")
async def upload_evaluation_file(
    file: UploadFile = File(..., description="评估文件（JSON格式）")
):
    """
    上传评估文件接口
    
    支持的文件格式：JSON
    最大文件大小：100MB
    """
    # 验证文件类型
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="仅支持JSON格式的评估文件")
    
    # 验证文件大小（100MB限制）
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 100 * 1024 * 1024:  # 100MB
        raise HTTPException(status_code=400, detail="文件大小不能超过100MB")
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = f"evaluation_{file_id}_{file.filename}"
    file_path = os.path.join(TEMP_DIR, filename)
    
    # 保存文件
    with open(file_path, 'wb') as f:
        f.write(content)
    
    return {
        "file_id": file_id,
        "filename": filename,
        "file_path": file_path,
        "file_size": file_size,
        "upload_time": datetime.now().isoformat(),
        "message": "文件上传成功"
    }


@router.post("/evaluation/analyze", summary="分析评估文件")
async def analyze_evaluation_file(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest
):
    """
    分析评估文件接口
    
    启动后台分析任务，返回任务ID用于查询进度和结果
    """
    # 根据file_id查找对应的文件
    # 搜索temp目录中以evaluation_{file_id}_开头的文件
    file_path = None
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(f"evaluation_{request.file_id}_"):
            file_path = os.path.join(TEMP_DIR, filename)
            break
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="指定的文件不存在，请先上传文件")
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    task_status[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "message": "任务已创建，等待开始...",
        "file_id": request.file_id,
        "file_path": file_path,
        "generate_report": request.generate_report,
        "created_time": datetime.now()
    }
    
    # 添加后台任务
    background_tasks.add_task(
        background_analysis_task,
        task_id,
        file_path,
        request.generate_report
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "分析任务已创建，请使用task_id查询进度",
        "estimated_time": "1-5分钟"
    }


@router.get("/evaluation/status/{task_id}", summary="查询分析状态")
async def get_analysis_status(task_id: str):
    """
    查询分析任务状态
    
    返回任务的详细状态信息，包括进度和消息
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    status_info = task_status[task_id].copy()
    
    # 格式化时间字段
    for time_field in ['created_time', 'start_time', 'end_time']:
        if time_field in status_info and status_info[time_field]:
            status_info[time_field] = status_info[time_field].isoformat()
    
    return status_info


@router.get("/evaluation/result/{task_id}", summary="获取分析结果")
async def get_analysis_result(
    task_id: str,
    format: str = Query("json", description="结果格式：json或summary")
):
    """
    获取分析结果
    
    Args:
        task_id: 任务ID
        format: 返回格式（json: 完整结果, summary: 执行摘要）
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"任务未完成，当前状态: {task_info['status']}"
        )
    
    result_path = task_info.get("result_path")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="分析结果文件不存在")
    
    # 读取结果文件
    with open(result_path, 'r', encoding='utf-8') as f:
        result_data = json.load(f)
    
    if format == "summary":
        return result_data.get("executive_summary", {})
    elif format == "actionable":
        return result_data.get("actionable_items", [])
    else:
        # 返回前端期望的简化数据结构
        analysis_result = result_data.get("analysis_result", {})
        
        # 构建前端期望的数据格式
        simplified_result = {
            "total_records": analysis_result.get("quality_metrics", {}).get("total_questions", 0),
            "metrics": {
                "success_rate": analysis_result.get("quality_metrics", {}).get("success_rate", 0.0),
                "average_score": analysis_result.get("quality_metrics", {}).get("score_distribution", {}).get("mean", 0.0)
            },
            "failure_patterns": analysis_result.get("failure_analysis", {}).get("patterns", []),
            "processing_time": analysis_result.get("processing_time", 0.0),
            "key_insights": analysis_result.get("key_insights", [])
        }
        
        return simplified_result


@router.get("/evaluation/report/{task_id}", summary="获取HTML分析报告")
async def get_analysis_report(task_id: str):
    """
    获取HTML分析报告
    
    返回可视化的分析报告HTML文件
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"任务未完成，当前状态: {task_info['status']}"
        )
    
    report_path = task_info.get("report_path")
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="分析报告文件不存在")
    
    # 检查文件是否存在且有内容
    try:
        file_size = os.path.getsize(report_path)
        if file_size == 0:
            raise HTTPException(status_code=500, detail="报告文件存在但内容为空")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查报告文件时出错: {str(e)}")
    
    # 添加跨域和缓存控制头
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Content-Disposition": f"inline; filename=evaluation_report_{task_id}.html"
    }
    
    return FileResponse(
        path=report_path,
        media_type='text/html',
        filename=f"evaluation_report_{task_id}.html",
        headers=headers
    )


@router.delete("/evaluation/task/{task_id}", summary="清理分析任务")
async def cleanup_analysis_task(task_id: str):
    """
    清理分析任务和相关文件
    
    删除任务状态和生成的临时文件
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    # 删除相关文件
    files_deleted = []
    for file_key in ['result_path', 'report_path']:
        file_path = task_info.get(file_key)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            files_deleted.append(file_path)
    
    # 删除任务状态
    del task_status[task_id]
    
    return {
        "message": "任务清理完成",
        "task_id": task_id,
        "files_deleted": files_deleted
    }


@router.get("/evaluation/tasks", summary="获取所有分析任务")
async def list_analysis_tasks(
    status_filter: Optional[str] = Query(None, description="状态过滤：pending, running, completed, failed")
):
    """
    获取所有分析任务列表
    
    支持按状态过滤任务
    """
    tasks = []
    
    for task_id, task_info in task_status.items():
        if status_filter and task_info.get("status") != status_filter:
            continue
        
        # 简化的任务信息
        task_summary = {
            "task_id": task_id,
            "status": task_info.get("status"),
            "progress": task_info.get("progress", 0.0),
            "message": task_info.get("message", ""),
            "created_time": task_info.get("created_time").isoformat() if task_info.get("created_time") else None,
            "has_result": bool(task_info.get("result_path")),
            "has_report": bool(task_info.get("report_path"))
        }
        tasks.append(task_summary)
    
    # 按创建时间倒序排列
    tasks.sort(key=lambda x: x.get("created_time", ""), reverse=True)
    
    return {
        "total_tasks": len(tasks),
        "filtered_tasks": len(tasks),
        "tasks": tasks
    }


# 健康检查端点
@router.get("/evaluation/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "evaluation_analysis",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_tasks": len([t for t in task_status.values() if t.get("status") in ["pending", "running"]])
    }


@router.get("/evaluation/training-guide/{task_id}", summary="获取训练指南")
async def get_training_guide(
    task_id: str,
    business_object: Optional[str] = None,
):
    """
    获取指定评估任务的训练指南
    
    如果指定了业务对象，则只返回该业务对象的训练指南
    否则返回所有业务对象的训练指南
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task = task_status[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成，无法获取训练指南")
    
    # 检查是否已经生成了训练指南
    if "training_guide_path" not in task:
        # 尝试生成训练指南
        try:
            # 加载分析结果
            result_path = task["result_path"]
            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
                
            analysis_result = result_data["analysis_result"]
            
            # 获取评估记录
            evaluation_records = task.get("evaluation_records")
            if not evaluation_records:
                raise HTTPException(status_code=400, detail="无法获取评估记录，无法生成训练指南")
            
            # 生成训练指南
            guide_generator = TrainingGuideGenerator(config)
            
            # 重建分析结果对象（简化版，只包含必要属性）
            from src.entity.evaluation.analysis_result import AnalysisResult
            from src.entity.evaluation.quality_metrics import QualityMetrics
            from src.entity.evaluation.failure_pattern import FailureAnalysis
            
            # 创建简化的分析结果对象
            simplified_result = AnalysisResult(
                file_path=analysis_result["file_path"],
                analysis_timestamp=datetime.fromisoformat(analysis_result["analysis_timestamp"]),
                processing_time=analysis_result["processing_time"],
                metadata=None,  # 非必要字段可以设为None
                quality_metrics=None,  # 稍后设置
                failure_analysis=None,  # 非必要字段可以设为None
                recommendations=[],
                key_insights=[]
            )
            
            # 设置质量指标（部分属性）
            metrics = QualityMetrics(
                total_questions=analysis_result["quality_metrics"]["total_questions"],
                successful_responses=analysis_result["quality_metrics"]["successful_responses"],
                failed_responses=analysis_result["quality_metrics"]["failed_responses"],
                success_rate=analysis_result["quality_metrics"]["success_rate"],
                failure_rate=analysis_result["quality_metrics"]["failure_rate"]
            )
            simplified_result.quality_metrics = metrics
            
            # 生成训练指南
            training_guide = guide_generator.generate_training_guide(simplified_result, evaluation_records)
            
            # 将训练指南保存到文件
            guide_filename = f"training_guide_{task_id}.json"
            guide_path = os.path.join(TEMP_DIR, guide_filename)
            with open(guide_path, 'w', encoding='utf-8') as f:
                json.dump(training_guide.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            
            # 更新任务状态
            task_status[task_id]["training_guide_path"] = guide_path
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成训练指南失败: {str(e)}")
    
    # 加载训练指南
    guide_path = task_status[task_id]["training_guide_path"]
    with open(guide_path, 'r', encoding='utf-8') as f:
        guide_data = json.load(f)
    
    # 如果指定了业务对象，只返回该业务对象的训练指南
    if business_object:
        if business_object not in guide_data["business_object_guides"]:
            raise HTTPException(status_code=404, detail=f"未找到业务对象 '{business_object}' 的训练指南")
        return {
            "business_object": business_object,
            "guide": guide_data["business_object_guides"][business_object],
            "summary": guide_data["summary"]
        }
    
    # 返回完整的训练指南
    return guide_data


@router.get("/evaluation/training-guide/{task_id}/download", summary="下载训练指南")
async def download_training_guide(
    task_id: str,
    business_object: Optional[str] = None,
    format: str = Query("json", description="文件格式：json或csv")
):
    """
    下载训练指南文件
    
    支持JSON和CSV格式，可选择下载单个业务对象或全部业务对象的训练指南
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task = task_status[task_id]
    
    if "training_guide_path" not in task:
        # 尝试先获取训练指南，这会触发生成过程
        await get_training_guide(task_id)
    
    guide_path = task_status[task_id]["training_guide_path"]
    
    # 加载训练指南数据
    with open(guide_path, 'r', encoding='utf-8') as f:
        guide_data = json.load(f)
    
    output_filename = ""
    output_path = ""
    
    if format.lower() == "json":
        # JSON格式输出
        if business_object:
            # 单个业务对象
            if business_object not in guide_data["business_object_guides"]:
                raise HTTPException(status_code=404, detail=f"未找到业务对象 '{business_object}' 的训练指南")
            
            output_data = {
                "business_object": business_object,
                "guide": guide_data["business_object_guides"][business_object],
                "summary": guide_data["summary"],
                "timestamp": guide_data["timestamp"]
            }
            output_filename = f"training_guide_{task_id}_{business_object}.json"
        else:
            # 全部业务对象
            output_data = guide_data
            output_filename = f"training_guide_{task_id}_all.json"
        
        # 保存为JSON文件
        output_path = os.path.join(TEMP_DIR, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
    
    elif format.lower() == "csv":
        import csv
        
        if business_object:
            # 单个业务对象
            if business_object not in guide_data["business_object_guides"]:
                raise HTTPException(status_code=404, detail=f"未找到业务对象 '{business_object}' 的训练指南")
            
            bo_guide = guide_data["business_object_guides"][business_object]
            output_filename = f"training_guide_{task_id}_{business_object}.csv"
            output_path = os.path.join(TEMP_DIR, output_filename)
            
            # 写入CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['规则ID', '失败次数', '失败百分比', '相似度', '建议类型', '优先级', '建议描述', '失败类型'])
                
                for rec in bo_guide["recommendations"]:
                    writer.writerow([
                        rec["rule_id"],
                        rec["failure_count"],
                        f"{rec['failure_percentage']:.1f}%",
                        f"{rec['similarity_score']:.2f}",
                        rec["recommendation_type"],
                        rec["priority"],
                        rec["description"],
                        ", ".join(rec["failure_types"]) if rec["failure_types"] else "未知"
                    ])
        else:
            # 全部业务对象
            output_filename = f"training_guide_{task_id}_all.csv"
            output_path = os.path.join(TEMP_DIR, output_filename)
            
            # 写入CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['业务对象', '规则ID', '失败次数', '失败百分比', '相似度', '建议类型', '优先级', '建议描述', '失败类型'])
                
                for bo_name, bo_guide in guide_data["business_object_guides"].items():
                    for rec in bo_guide["recommendations"]:
                        writer.writerow([
                            bo_name,
                            rec["rule_id"],
                            rec["failure_count"],
                            f"{rec['failure_percentage']:.1f}%",
                            f"{rec['similarity_score']:.2f}",
                            rec["recommendation_type"],
                            rec["priority"],
                            rec["description"],
                            ", ".join(rec["failure_types"]) if rec["failure_types"] else "未知"
                        ])
    else:
        raise HTTPException(status_code=400, detail=f"不支持的格式: {format}，请使用 'json' 或 'csv'")
    
    # 返回文件
    headers = {
        'Content-Disposition': f'attachment; filename="{output_filename}"'
    }
    return FileResponse(path=output_path, headers=headers) 