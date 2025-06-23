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
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
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

analysis_tasks: Dict[str, dict] = {}

def extract_detailed_failure_reason(record_data: Dict[str, Any]) -> str:
    """
    从记录中提取详细的失败原因
    支持从analysis字段提取详细信息，包括低级错误等
    """
    evaluation = record_data.get('evaluation', {})
    analysis = evaluation.get('analysis', '')
    # failure_reason = evaluation.get('failure_reason', '')
    status = evaluation.get('status', 'unknown')
    score = evaluation.get('score', 0)
    
    # 1. 如果有明确的失败原因，优先使用
    # if failure_reason and failure_reason.strip():
    #     return failure_reason.strip()
    
    # 2. 从详细分析中提取关键错误信息
    if analysis and analysis.strip():
        import re
        
        # 解析低位错误模式
        if '低位错误:' in analysis:
            # 提取低位错误的具体类型
            low_error_match = re.search(r'低位错误:\s*(\d+)\(([^)]+)\)', analysis)
            if low_error_match:
                error_code = low_error_match.group(1)
                error_type = low_error_match.group(2)
                
                # 根据错误代码生成更具体的原因
                if error_code == "8":
                    return f"字段值不一致错误 (代码{error_code}: {error_type})"
                elif error_code == "2":
                    return f"字段内容格式错误 (代码{error_code}: {error_type})"
                else:
                    return f"低级别匹配错误 (代码{error_code}: {error_type})"
        
        # 其他分析模式
        if '条件值不一致' in analysis:
            return "字段值不匹配"
        elif '条件数量不一致' in analysis:
            return "字段数量不一致"
        elif 'JSON解析失败' in analysis:
            return "JSON格式错误"
        elif '条件数量一致，内容不一致' in analysis:
            return "字段内容格式差异"
        elif '值变更' in analysis:
            return "字段值格式标准化问题"
        
        # 如果有分析但无法分类，返回前150个字符作为原因
        return analysis[:150] + ('...' if len(analysis) > 150 else '')
    
    # 3. 根据记录状态和分数推断原因
    if status == 'success':
        if score < 10:
            return f"部分匹配问题 (得分: {score}/10)"
        else:
            return "格式标准化问题"
    
    # 4. 默认原因
    return "未知原因"


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
        
        # 处理可能包含特殊字符的字段
        def sanitize_dict_keys(d):
            if not isinstance(d, dict):
                return d
            
            result = {}
            for k, v in d.items():
                # 处理字典键中的特殊字符
                safe_key = str(k).replace('{', '_').replace('}', '_')
                
                # 递归处理嵌套字典和列表
                if isinstance(v, dict):
                    result[safe_key] = sanitize_dict_keys(v)
                elif isinstance(v, list):
                    result[safe_key] = [sanitize_dict_keys(item) if isinstance(item, dict) else item for item in v]
                else:
                    result[safe_key] = v
            
            return result
        
        # 将分析结果转换为字典并处理特殊字符
        analysis_result_dict = sanitize_dict_keys(analysis_result.to_dict())
        
        result_data = {
            "analysis_result": analysis_result_dict,
            "executive_summary": sanitize_dict_keys(analysis_result.get_executive_summary()),
            "actionable_items": sanitize_dict_keys(analysis_result.get_actionable_items())
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
            report_path = report_generator.generate_html_report(analysis_result, REPORTS_DIR, evaluation_records, task_id)
        
        # 更新任务状态为完成
        task_status[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "分析完成",
            "end_time": datetime.now(),
            "result_path": result_path,
            "report_path": report_path
        })
        
        # 保存评估记录到单独的文件，以便其他功能使用
        if evaluation_records:
            try:
                # 将评估记录序列化为可存储的格式
                serializable_records = []
                for record in evaluation_records:
                    try:
                        # 将记录转换为字典格式并处理特殊字符
                        record_dict = record.to_dict() if hasattr(record, 'to_dict') else record.__dict__
                        sanitized_record = sanitize_dict_keys(record_dict)
                        serializable_records.append(sanitized_record)
                    except Exception as e:
                        logging.warning(f"无法序列化评估记录: {e}")
                        continue
                
                # 保存到文件
                records_filename = f"evaluation_records_{task_id}.json"
                records_path = os.path.join(TEMP_DIR, records_filename)
                with open(records_path, 'w', encoding='utf-8') as f:
                    json.dump(serializable_records, f, ensure_ascii=False, indent=2, default=str)
                
                # 只在任务状态中存储文件路径，而不是数据本身
                task_status[task_id]["evaluation_records_path"] = records_path
                task_status[task_id]["evaluation_records_count"] = len(serializable_records)
                
            except Exception as e:
                logging.error(f"保存评估记录失败: {e}")
                # 如果保存失败，至少记录数量
                task_status[task_id]["evaluation_records_count"] = len(evaluation_records)
        
    except Exception as e:
        # 更新任务状态为失败
        error_message = str(e)
        error_type = type(e).__name__
        
        # 记录更详细的错误信息
        logging.error(f"分析任务失败: {error_type}: {error_message}")
        logging.error(f"错误详情:", exc_info=True)
        
        # 如果是JSON相关错误，尝试提供更详细的信息
        if "JSONDecodeError" in error_type or "unexpected" in error_message:
            logging.error("检测到JSON解析错误，尝试提供更多信息")
            # 尝试获取更多上下文
            if hasattr(e, 'doc') and hasattr(e, 'pos'):
                context = e.doc[max(0, e.pos-20):min(len(e.doc), e.pos+20)]
                logging.error(f"JSON错误上下文: ...{context}...")
                error_message = f"{error_message} (错误位置附近: ...{context}...)"
        
        task_status[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"分析失败: {error_message}",
            "error_type": error_type,
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
    
    # 移除不可序列化的字段
    fields_to_remove = ['evaluation_records', 'training_guide_path']
    for field in fields_to_remove:
        status_info.pop(field, None)
    
    # 格式化时间字段
    for time_field in ['created_time', 'start_time', 'end_time']:
        if time_field in status_info and status_info[time_field]:
            try:
                status_info[time_field] = status_info[time_field].isoformat()
            except (AttributeError, TypeError):
                # 如果时间字段不是datetime对象，尝试保持原样或移除
                if not isinstance(status_info[time_field], str):
                    status_info.pop(time_field, None)
    
    # 处理可能包含特殊字符的字段
    def sanitize_dict_keys(d):
        if not isinstance(d, dict):
            return d
        
        result = {}
        for k, v in d.items():
            # 处理字典键中的特殊字符
            safe_key = str(k).replace('{', '_').replace('}', '_')
            
            # 递归处理嵌套字典和列表
            if isinstance(v, dict):
                result[safe_key] = sanitize_dict_keys(v)
            elif isinstance(v, list):
                result[safe_key] = [sanitize_dict_keys(item) if isinstance(item, dict) else item for item in v]
            else:
                result[safe_key] = v
        
        return result
    
    # 递归处理所有字典，确保没有特殊字符
    status_info = sanitize_dict_keys(status_info)
    
    # 验证响应是否可以序列化为JSON
    try:
        import json
        json.dumps(status_info, default=str)
    except (TypeError, ValueError) as e:
        # 如果仍然无法序列化，返回基本状态信息
        logging.warning(f"任务状态序列化失败，返回基本信息: {e}")
        return {
            "task_id": task_id,
            "status": task_status[task_id].get("status", "unknown"),
            "progress": task_status[task_id].get("progress", 0.0),
            "message": str(task_status[task_id].get("message", "")),
            "created_time": datetime.now().isoformat()
        }
    
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
    
    # 处理可能包含特殊字符的字段
    def sanitize_dict_keys(d):
        if not isinstance(d, dict):
            return d
        
        result = {}
        for k, v in d.items():
            # 处理字典键中的特殊字符
            safe_key = str(k).replace('{', '_').replace('}', '_')
            
            # 递归处理嵌套字典和列表
            if isinstance(v, dict):
                result[safe_key] = sanitize_dict_keys(v)
            elif isinstance(v, list):
                result[safe_key] = [sanitize_dict_keys(item) if isinstance(item, dict) else item for item in v]
            else:
                result[safe_key] = v
        
        return result
    
    # 确保所有结果都经过sanitize处理
    result_data = sanitize_dict_keys(result_data)
    
    if format == "summary":
        return result_data.get("executive_summary", {})
    elif format == "actionable":
        return result_data.get("actionable_items", [])
    else:
        # 返回前端期望的完整数据结构（包含charts）
        analysis_result = result_data.get("analysis_result", {})
        
        # 构建business_object图表的records数据
        business_object_records = {}
        quality_metrics = analysis_result.get("quality_metrics", {})
        quality_by_business_object = quality_metrics.get("quality_by_business_object", {})
        
        for bo_name, bo_data in quality_by_business_object.items():
            # 确保业务对象名称中的特殊字符被替换（与报告生成器保持一致）
            safe_bo_name = str(bo_name).replace('{', '_').replace('}', '_')
            business_object_records[safe_bo_name] = {
                'total': bo_data.get('total_records', 0),
                'success': int(bo_data.get('total_records', 0) * bo_data.get('success_rate', 0.0)),
                'failure': bo_data.get('total_records', 0) - int(bo_data.get('total_records', 0) * bo_data.get('success_rate', 0.0)),
                'success_rate': bo_data.get('success_rate', 0.0) * 100  # 转换为百分比
            }
        
        # 构建charts数据结构
        charts_data = {
            "business_object": {
                "title": "Business Object Performance",
                "data": quality_by_business_object,
                "records": business_object_records,
                "stats": {
                    "best_performing": "未知",
                    "worst_performing": "未知"
                }
            }
        }
        
        # 找出最佳和最差表现的业务对象
        if quality_by_business_object:
            sorted_bos = sorted(
                quality_by_business_object.items(),
                key=lambda x: x[1].get('success_rate', 0),
                reverse=True
            )
            if sorted_bos:
                charts_data["business_object"]["stats"]["best_performing"] = sorted_bos[0][0].replace('{', '_').replace('}', '_')
                charts_data["business_object"]["stats"]["worst_performing"] = sorted_bos[-1][0].replace('{', '_').replace('}', '_')
        
        # 增强新格式特性分析 - 从评估记录中提取新字段统计
        enhanced_features_stats = {}
        records_path = task_info.get("evaluation_records_path")
        
        if records_path and os.path.exists(records_path):
            try:
                with open(records_path, 'r', encoding='utf-8') as f:
                    records_data = json.load(f)
                
                # 统计新格式特性
                total_records = len(records_data)
                if total_records > 0:
                    # JSON有效性统计
                    json_valid_count = 0
                    json_invalid_count = 0
                    
                    # 规则级别统计
                    rule_performance = {}
                    
                    # 关键词匹配统计
                    keyword_effectiveness = {}
                    
                    # 详细分析类型统计
                    analysis_types = {}
                    
                    for record in records_data:
                        # JSON有效性统计
                        json_valid = record.get('evaluation', {}).get('json_valid')
                        if json_valid is True:
                            json_valid_count += 1
                        elif json_valid is False:
                            json_invalid_count += 1
                        
                        # 规则性能统计
                        rule_name = record.get('original_data', {}).get('rule_name', '未知规则')
                        if rule_name not in rule_performance:
                            rule_performance[rule_name] = {
                                'total': 0,
                                'success': 0,
                                'json_valid': 0,
                                'success_rate': 0.0,
                                'json_valid_rate': 0.0
                            }
                        
                        rule_performance[rule_name]['total'] += 1
                        if record.get('status') == 'success':
                            rule_performance[rule_name]['success'] += 1
                        if json_valid is True:
                            rule_performance[rule_name]['json_valid'] += 1
                    
                    # 计算规则性能百分比
                    for rule_name, stats in rule_performance.items():
                        if stats['total'] > 0:
                            stats['success_rate'] = stats['success'] / stats['total']
                            stats['json_valid_rate'] = stats['json_valid'] / stats['total']
                    
                    # 关键词效果统计
                    for record in records_data:
                        matched_keyword = record.get('prompt_info', {}).get('matched_keyword')
                        if matched_keyword:
                            if matched_keyword not in keyword_effectiveness:
                                keyword_effectiveness[matched_keyword] = {
                                    'total': 0,
                                    'success': 0,
                                    'success_rate': 0.0
                                }
                            
                            keyword_effectiveness[matched_keyword]['total'] += 1
                            if record.get('status') == 'success':
                                keyword_effectiveness[matched_keyword]['success'] += 1
                    
                    # 计算关键词效果百分比
                    for keyword, stats in keyword_effectiveness.items():
                        if stats['total'] > 0:
                            stats['success_rate'] = stats['success'] / stats['total']
                    
                    # 详细分析类型统计
                    for record in records_data:
                        analysis = record.get('evaluation', {}).get('analysis', '')
                        if analysis:
                            # 简单的分析类型分类
                            if '完美匹配' in analysis or '高质量' in analysis:
                                analysis_type = '高质量匹配'
                            elif 'JSON' in analysis or 'json' in analysis:
                                analysis_type = 'JSON相关问题'
                            elif '格式' in analysis:
                                analysis_type = '格式问题'
                            else:
                                analysis_type = '其他分析'
                            
                            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
                    
                    enhanced_features_stats = {
                        "json_validity": {
                            "valid_count": json_valid_count,
                            "invalid_count": json_invalid_count,
                            "total_with_info": json_valid_count + json_invalid_count,
                            "valid_rate": json_valid_count / (json_valid_count + json_invalid_count) if (json_valid_count + json_invalid_count) > 0 else 0.0
                        },
                        "rule_performance": dict(sorted(rule_performance.items(), key=lambda x: x[1]['success_rate'], reverse=True)),
                        "keyword_effectiveness": dict(sorted(keyword_effectiveness.items(), key=lambda x: x[1]['success_rate'], reverse=True)),
                        "analysis_distribution": analysis_types,
                        "enhanced_format_coverage": {
                            "total_records": total_records,
                            "records_with_rule_name": len([r for r in records_data if r.get('original_data', {}).get('rule_name')]),
                            "records_with_keyword": len([r for r in records_data if r.get('prompt_info', {}).get('matched_keyword')]),
                            "records_with_structured_data": len([r for r in records_data if isinstance(r.get('original_data', {}).get('question'), dict)]),
                            "records_with_detailed_analysis": len([r for r in records_data if r.get('evaluation', {}).get('analysis')])
                        }
                    }
                    
                    # 扩展charts数据以包含新格式特性可视化
                    if enhanced_features_stats:
                        # JSON有效性图表数据
                        if enhanced_features_stats["json_validity"]["total_with_info"] > 0:
                            charts_data["json_validity"] = {
                                "title": "JSON Validity Analysis",
                                "data": {
                                    "valid": enhanced_features_stats["json_validity"]["valid_count"],
                                    "invalid": enhanced_features_stats["json_validity"]["invalid_count"]
                                },
                                "stats": {
                                    "valid_rate": enhanced_features_stats["json_validity"]["valid_rate"],
                                    "total_analyzed": enhanced_features_stats["json_validity"]["total_with_info"]
                                }
                            }
                        
                        # 规则性能图表数据（取前5个规则）
                        top_rules = dict(list(enhanced_features_stats["rule_performance"].items())[:5])
                        if top_rules:
                            charts_data["rule_performance"] = {
                                "title": "Top Rules Performance",
                                "data": top_rules,
                                "stats": {
                                    "total_rules": len(enhanced_features_stats["rule_performance"]),
                                    "best_rule": list(enhanced_features_stats["rule_performance"].keys())[0] if enhanced_features_stats["rule_performance"] else "无",
                                    "worst_rule": list(enhanced_features_stats["rule_performance"].keys())[-1] if enhanced_features_stats["rule_performance"] else "无"
                                }
                            }
                        
                        # 关键词效果图表数据（取前5个关键词）
                        top_keywords = dict(list(enhanced_features_stats["keyword_effectiveness"].items())[:5])
                        if top_keywords:
                            charts_data["keyword_effectiveness"] = {
                                "title": "Keyword Effectiveness",
                                "data": top_keywords,
                                "stats": {
                                    "total_keywords": len(enhanced_features_stats["keyword_effectiveness"]),
                                    "most_effective": list(enhanced_features_stats["keyword_effectiveness"].keys())[0] if enhanced_features_stats["keyword_effectiveness"] else "无",
                                    "least_effective": list(enhanced_features_stats["keyword_effectiveness"].keys())[-1] if enhanced_features_stats["keyword_effectiveness"] else "无"
                                }
                            }
                        
                        # 分析类型分布图表数据
                        if enhanced_features_stats["analysis_distribution"]:
                            charts_data["analysis_distribution"] = {
                                "title": "Analysis Type Distribution",
                                "data": enhanced_features_stats["analysis_distribution"],
                                "stats": {
                                    "total_types": len(enhanced_features_stats["analysis_distribution"]),
                                    "most_common": max(enhanced_features_stats["analysis_distribution"], key=enhanced_features_stats["analysis_distribution"].get) if enhanced_features_stats["analysis_distribution"] else "无"
                                }
                            }
                    
            except Exception as e:
                logging.warning(f"解析增强特性统计时出错: {e}")
                enhanced_features_stats = {"error": "无法解析增强特性"}
        
        # 构建前端期望的完整数据格式（包含新特性统计）
        complete_result = {
            "total_records": analysis_result.get("quality_metrics", {}).get("total_questions", 0),
            "metrics": {
                "success_rate": analysis_result.get("quality_metrics", {}).get("success_rate", 0.0),
                "average_score": analysis_result.get("quality_metrics", {}).get("score_distribution", {}).get("mean", 0.0)
            },
            "failure_patterns": analysis_result.get("failure_analysis", {}).get("patterns", []),
            "processing_time": analysis_result.get("processing_time", 0.0),
            "key_insights": analysis_result.get("key_insights", []),
            "charts": charts_data,
            "enhanced_features": enhanced_features_stats  # 新增的增强特性统计
        }
        
        return complete_result


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


@router.get("/evaluation/detailed-records/{task_id}", summary="获取详细记录")
async def get_detailed_records(
    task_id: str,
    business_object: Optional[str] = None,
):
    """
    获取指定业务对象的详细评估记录
    
    Args:
        task_id: 任务ID
        business_object: 业务对象名称（可选，如果提供则只返回该业务对象的记录）
    
    Returns:
        详细记录列表
    """
    try:
        # 检查任务状态
        if task_id not in task_status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_status[task_id]
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 检查记录文件
        records_path = task.get("evaluation_records_path")
        if not records_path or not os.path.exists(records_path):
            raise HTTPException(status_code=404, detail="详细记录文件不存在")
        
        # 读取评估记录
        try:
            with open(records_path, 'r', encoding='utf-8') as f:
                records_data = json.load(f)
        except Exception as e:
            logging.error(f"读取记录文件失败: {e}")
            raise HTTPException(status_code=500, detail="读取记录文件失败")
        
        # 过滤指定业务对象的记录
        if business_object:
            filtered_records = []
            for record in records_data:
                if isinstance(record, dict):
                    # 检查业务对象字段
                    record_business_object = record.get('original_data', {}).get('business_object', '')
                    if record_business_object == business_object:
                        filtered_records.append(record)
            
            logging.info(f"找到业务对象 {business_object} 的 {len(filtered_records)} 条记录")
            return filtered_records
        else:
            # 返回所有记录
            logging.info(f"返回所有 {len(records_data)} 条记录")
            return records_data
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取详细记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取详细记录失败: {str(e)}")


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
            evaluation_records = None
            records_path = task.get("evaluation_records_path")
            
            if records_path and os.path.exists(records_path):
                try:
                    with open(records_path, 'r', encoding='utf-8') as f:
                        records_data = json.load(f)
                    
                    # 重建评估记录对象
                    from src.entity.evaluation.evaluation_record import EvaluationRecord
                    evaluation_records = []
                    for record_dict in records_data:
                        try:
                            record = EvaluationRecord.from_dict(record_dict)
                            evaluation_records.append(record)
                        except Exception as e:
                            logging.warning(f"重建评估记录失败: {e}")
                            continue
                            
                except Exception as e:
                    logging.error(f"读取评估记录文件失败: {e}")
            
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
            # 如果没有quality_metrics，使用metrics字段
            if "quality_metrics" in analysis_result and analysis_result["quality_metrics"]:
                quality_metrics_data = analysis_result["quality_metrics"]
            else:
                # 使用metrics字段，并创建兼容的数据结构
                metrics_data = analysis_result.get("metrics", {})
                quality_metrics_data = {
                    "total_questions": analysis_result.get("total_records", 0),
                    "successful_responses": int(analysis_result.get("total_records", 0) * metrics_data.get("success_rate", 0)),
                    "failed_responses": analysis_result.get("total_records", 0) - int(analysis_result.get("total_records", 0) * metrics_data.get("success_rate", 0)),
                    "success_rate": metrics_data.get("success_rate", 0),
                    "score_distribution": {},
                    "perfect_score_count": 0,
                    "perfect_score_rate": 0.0,
                    "json_valid_count": 0,
                    "json_valid_rate": 0.0,
                    "average_response_length": 0.0,
                    "min_response_length": 0,
                    "max_response_length": 0,
                    "performance_metrics": {},
                    "quality_by_business_object": {},
                    "quality_by_rule": {},
                    "quality_insights": {},
                    "quality_trends": None
                }
            
            # 计算failure_rate，如果不存在的话
            failure_rate = quality_metrics_data.get("failure_rate")
            if failure_rate is None:
                success_rate = quality_metrics_data.get("success_rate", 0)
                # success_rate是小数格式（0-1），需要转换为百分比
                failure_rate = (1.0 - success_rate) * 100.0 if success_rate <= 1.0 else 0.0
            
            # 创建必要的嵌套对象
            from src.entity.evaluation.quality_metrics import ScoreDistribution, PerformanceMetrics, QualityInsights
            
            # 创建分数分布对象
            score_dist_data = quality_metrics_data.get("score_distribution", {})
            score_distribution = ScoreDistribution(
                score_ranges=score_dist_data.get("score_ranges", {}),
                percentiles=score_dist_data.get("percentiles", {}),
                mean=score_dist_data.get("mean", 0.0),
                median=score_dist_data.get("median", 0.0),
                std_dev=score_dist_data.get("std_dev", 0.0)
            )
            
            # 创建性能指标对象
            perf_data = quality_metrics_data.get("performance_metrics", {})
            performance_metrics = PerformanceMetrics(
                total_processing_time=perf_data.get("total_processing_time", 0.0),
                average_time_per_question=perf_data.get("average_time_per_question", 0.0),
                min_processing_time=perf_data.get("min_processing_time", 0.0),
                max_processing_time=perf_data.get("max_processing_time", 0.0),
                time_percentiles=perf_data.get("time_percentiles", {})
            )
            
            # 创建质量洞察对象
            insights_data = quality_metrics_data.get("quality_insights", {})
            quality_insights = QualityInsights(
                high_quality_patterns=insights_data.get("high_quality_patterns", []),
                low_quality_patterns=insights_data.get("low_quality_patterns", []),
                improvement_recommendations=insights_data.get("improvement_recommendations", []),
                best_practice_examples=insights_data.get("best_practice_examples", [])
            )
            
            metrics = QualityMetrics(
                total_questions=quality_metrics_data.get("total_questions", 0),
                successful_responses=quality_metrics_data.get("successful_responses", 0),
                failed_responses=quality_metrics_data.get("failed_responses", 0),
                success_rate=quality_metrics_data.get("success_rate", 0.0),
                score_distribution=score_distribution,
                perfect_score_count=quality_metrics_data.get("perfect_score_count", 0),
                perfect_score_rate=quality_metrics_data.get("perfect_score_rate", 0.0),
                json_valid_count=quality_metrics_data.get("json_valid_count", 0),
                json_valid_rate=quality_metrics_data.get("json_valid_rate", 0.0),
                average_response_length=quality_metrics_data.get("average_response_length", 0.0),
                min_response_length=quality_metrics_data.get("min_response_length", 0),
                max_response_length=quality_metrics_data.get("max_response_length", 0),
                performance_metrics=performance_metrics,
                quality_by_business_object=quality_metrics_data.get("quality_by_business_object", {}),
                quality_by_rule=quality_metrics_data.get("quality_by_rule", {}),
                quality_insights=quality_insights,
                quality_trends=quality_metrics_data.get("quality_trends")
            )
            simplified_result.quality_metrics = metrics
            
            # 添加metrics属性，以便训练指南生成器能够访问
            from types import SimpleNamespace
            simplified_result.metrics = SimpleNamespace()
            simplified_result.metrics.success_rate = quality_metrics_data.get("success_rate", 0)
            simplified_result.metrics.average_score = analysis_result.get("metrics", {}).get("average_score", 0)
            
            # 生成训练指南
            try:
                training_guide = guide_generator.generate_training_guide(simplified_result, evaluation_records)
                
                # 将训练指南转换为字典并检查特殊字符
                guide_dict = training_guide.to_dict()
                
                # 确保所有字段名不包含特殊字符
                def sanitize_dict(d):
                    if not isinstance(d, dict):
                        return d
                    
                    result = {}
                    for k, v in d.items():
                        # 确保键是字符串且不包含特殊字符
                        safe_key = str(k).replace('{', '_').replace('}', '_')
                        
                        # 递归处理嵌套字典
                        if isinstance(v, dict):
                            result[safe_key] = sanitize_dict(v)
                        # 处理列表中的字典
                        elif isinstance(v, list):
                            result[safe_key] = [sanitize_dict(item) if isinstance(item, dict) else item for item in v]
                        else:
                            result[safe_key] = v
                    return result
                
                # 清理字典中的特殊字符
                sanitized_guide = sanitize_dict(guide_dict)
                
                # 将训练指南保存到文件
                guide_filename = f"training_guide_{task_id}.json"
                guide_path = os.path.join(TEMP_DIR, guide_filename)
                with open(guide_path, 'w', encoding='utf-8') as f:
                    json.dump(sanitized_guide, f, ensure_ascii=False, indent=2, default=str)
                
                # 更新任务状态
                task_status[task_id]["training_guide_path"] = guide_path
                
            except Exception as e:
                import traceback
                error_detail = f"生成训练指南失败: {str(e)}\n{traceback.format_exc()}"
                logging.error(error_detail)
                raise HTTPException(status_code=500, detail=error_detail)
                
        except Exception as e:
            import traceback
            error_detail = f"处理训练指南请求失败: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_detail)
            raise HTTPException(status_code=500, detail=error_detail)
    
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


@router.get("/evaluation/training-guide/{task_id}/details", summary="获取训练指南详细信息")
async def get_training_guide_details(
    task_id: str,
    business_object: Optional[str] = Query(None, description="业务对象名称"),
    rule_id: Optional[str] = Query(None, description="规则ID"),
    include_records: bool = Query(False, description="是否包含详细记录")
):
    """
    获取训练指南详细信息
    
    支持按业务对象和rule_id过滤，可选择包含详细记录
    
    Args:
        task_id: 任务ID
        business_object: 业务对象名称（可选）
        rule_id: 规则ID（可选）
        include_records: 是否包含失败记录样例
    
    Returns:
        过滤后的训练建议详细信息
    """
    try:
        # 检查任务状态
        if task_id not in task_status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        task = task_status[task_id]
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 确保训练指南已生成
        if "training_guide_path" not in task:
            # 尝试生成训练指南
            await get_training_guide(task_id)
        
        # 加载训练指南
        guide_path = task_status[task_id]["training_guide_path"]
        with open(guide_path, 'r', encoding='utf-8') as f:
            guide_data = json.load(f)
        
        # 过滤结果
        filtered_recommendations = []
        
        for bo_name, bo_guide in guide_data["business_object_guides"].items():
            # 按业务对象过滤
            if business_object and bo_name != business_object:
                continue
                
            for recommendation in bo_guide["recommendations"]:
                # 按rule_id过滤
                if rule_id and recommendation["rule_id"] != rule_id:
                    continue
                    
                # 添加业务对象信息
                recommendation["business_object"] = bo_name
                filtered_recommendations.append(recommendation)
        
        # 如果需要包含详细记录
        detailed_records = []
        if include_records and filtered_recommendations:
            records_path = task.get("evaluation_records_path")
            if records_path and os.path.exists(records_path):
                try:
                    with open(records_path, 'r', encoding='utf-8') as f:
                        all_records = json.load(f)
                    
                    # 为每个建议查找对应的失败记录
                    for rec in filtered_recommendations:
                        rec_business_object = rec["business_object"]
                        rec_rule_id = rec["rule_id"]
                        
                        # 找到匹配的失败记录（从配置获取最大数量）
                        from src.config.config_loader import get_config
                        config = get_config()
                        max_records = config.get('recommendation', {}).get('training_guide', {}).get('sample_records', {}).get('max_records_per_rule', 10)
                        
                        matching_records = []
                        count = 0
                        for record in all_records:
                            if count >= max_records:  # 限制返回的记录数量
                                break
                                
                            if (isinstance(record, dict) and 
                                record.get('status') == 'failed' and
                                record.get('original_data', {}).get('business_object') == rec_business_object and
                                record.get('original_data', {}).get('rule_id') == rec_rule_id):
                                
                                # 从配置获取文本截断长度
                                truncate_length = config.get('recommendation', {}).get('training_guide', {}).get('sample_records', {}).get('text_truncate_length', 200)
                                
                                # 简化记录信息，只保留关键字段
                                simplified_record = {
                                    'id': record.get('id'),
                                    'question': record.get('question', '')[:truncate_length] + '...' if len(record.get('question', '')) > truncate_length else record.get('question', ''),
                                    'expected_answer': record.get('expected_answer', '')[:truncate_length] + '...' if len(record.get('expected_answer', '')) > truncate_length else record.get('expected_answer', ''),
                                    'actual_answer': record.get('actual_answer', '')[:truncate_length] + '...' if len(record.get('actual_answer', '')) > truncate_length else record.get('actual_answer', ''),
                                    'score': record.get('score', 0),
                                    'failure_reason': extract_detailed_failure_reason(record),
                                    'processing_time': record.get('processing_time', 0)
                                }
                                matching_records.append(simplified_record)
                                count += 1
                        
                        detailed_records.extend(matching_records)
                        
                except Exception as e:
                    logging.warning(f"读取详细记录失败: {e}")
        
        # 构建响应
        response = {
            "task_id": task_id,
            "total_recommendations": len(filtered_recommendations),
            "filters": {
                "business_object": business_object,
                "rule_id": rule_id,
                "include_records": include_records
            },
            "recommendations": filtered_recommendations
        }
        
        if include_records:
            response["detailed_records"] = detailed_records
            response["detailed_records_count"] = len(detailed_records)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"获取训练指南详细信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取训练指南详细信息失败: {str(e)}")


# 新增API端点
class InputFileAnalysisRequest(BaseModel):
    """输入文件分析请求模型"""
    file_name: str


@router.get("/evaluation/input-files", summary="获取输入目录文件列表")
async def get_input_files():
    """
    获取输入目录中的文件列表
    
    扫描项目的input目录，返回可用于评估分析的文件列表
    """
    try:
        # 项目根目录的input目录
        input_dir = "input"
        
        if not os.path.exists(input_dir):
            return {
                "files": [],
                "message": "输入目录不存在"
            }
        
        files = []
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            
            # 只处理文件，跳过目录
            if os.path.isfile(file_path):
                # 获取文件信息
                stat = os.stat(file_path)
                file_info = {
                    "name": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "path": file_path
                }
                files.append(file_info)
        
        # 按修改时间排序，最新的在前
        files.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "files": files,
            "count": len(files),
            "message": f"找到 {len(files)} 个文件"
        }
        
    except Exception as e:
        logging.error(f"获取输入文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


@router.post("/evaluation/analyze-input-file", summary="分析输入目录文件")
async def analyze_input_file(
    background_tasks: BackgroundTasks,
    request: InputFileAnalysisRequest
):
    """
    直接分析输入目录中的文件
    
    跳过上传步骤，直接对input目录中的指定文件进行评估分析
    """
    try:
        # 构建文件路径
        input_dir = "input"
        file_path = os.path.join(input_dir, request.file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {request.file_name}")
        
        # 检查文件格式
        if not request.file_name.endswith('.json'):
            raise HTTPException(status_code=400, detail="仅支持JSON格式的评估文件")
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="文件大小不能超过100MB")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        task_status[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "progress": 0.0,
            "message": "任务已创建，等待开始...",
            "file_name": request.file_name,
            "file_path": file_path,
            "generate_report": True,  # 默认生成报告
            "created_time": datetime.now()
        }
        
        # 添加后台任务
        background_tasks.add_task(
            background_analysis_task,
            task_id,
            file_path,
            True  # generate_report
        )
        
        return {
            "task_id": task_id,
            "status": "pending",
            "message": f"正在分析文件: {request.file_name}",
            "file_name": request.file_name,
            "estimated_time": "1-5分钟"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"分析输入文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


# 在现有导入之后添加新的数据模型
class FormatDetectionRequest(BaseModel):
    """格式检测请求模型"""
    file_id: str

class FormatDetectionResult(BaseModel):
    """格式检测结果模型"""
    file_id: str
    format_type: str  # "legacy", "enhanced", "mixed"
    enhanced_features: Dict[str, Any]
    recommendations: List[str]
    compatibility_score: float  # 0.0 - 1.0
    
# 在文件末尾添加新的API端点

@router.post("/evaluation/detect-format", summary="检测评估文件格式")
async def detect_evaluation_format(
    request: FormatDetectionRequest
):
    """
    检测评估文件的格式类型和新特性支持
    
    Args:
        request: 包含file_id的格式检测请求
        
    Returns:
        格式检测结果，包括格式类型、支持的新特性、兼容性评分等
    """
    try:
        # 根据file_id查找对应的文件
        file_path = None
        for filename in os.listdir(TEMP_DIR):
            if filename.startswith(f"evaluation_{request.file_id}_"):
                file_path = os.path.join(TEMP_DIR, filename)
                break
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="指定的文件不存在，请先上传文件")
        
        # 分析文件格式
        format_analysis = _analyze_file_format(file_path)
        
        return FormatDetectionResult(
            file_id=request.file_id,
            format_type=format_analysis["format_type"],
            enhanced_features=format_analysis["enhanced_features"],
            recommendations=format_analysis["recommendations"],
            compatibility_score=format_analysis["compatibility_score"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"格式检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"格式检测失败: {str(e)}")


def _analyze_file_format(file_path: str) -> Dict[str, Any]:
    """
    分析文件格式特性
    
    Args:
        file_path: 文件路径
        
    Returns:
        格式分析结果字典
    """
    try:
        # 读取并解析JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logs = data.get('logs', [])
        if not logs:
            # 尝试其他可能的字段名
            for field_name in ['records', 'data', 'evaluation_records']:
                if field_name in data:
                    logs = data[field_name]
                    break
        
        if not logs:
            return {
                "format_type": "unknown",
                "enhanced_features": {},
                "recommendations": ["文件中未找到有效的评估记录"],
                "compatibility_score": 0.0
            }
        
        # 统计新格式特性
        total_records = len(logs)
        enhanced_features = {
            "evaluation_detail": 0,  # evaluation字段包含详细信息
            "prompt_info_enhanced": 0,  # prompt_info包含matched_keyword
            "original_data_structured": 0,  # original_data包含question/answer结构
            "json_valid_field": 0,  # 包含json_valid字段
            "rule_name_field": 0,  # 包含rule_name字段
            "detailed_analysis": 0,  # 包含detailed_analysis字段
        }
        
        sample_record = None
        
        for record in logs[:min(10, len(logs))]:  # 只检查前10条记录以提高性能
            if sample_record is None:
                sample_record = record
            
            # 检查evaluation字段是否为详细结构
            evaluation = record.get('evaluation', {})
            if isinstance(evaluation, dict) and 'json_valid' in evaluation:
                enhanced_features["evaluation_detail"] += 1
            
            # 检查prompt_info是否包含matched_keyword
            prompt_info = record.get('prompt_info', {})
            if isinstance(prompt_info, dict) and 'matched_keyword' in prompt_info:
                enhanced_features["prompt_info_enhanced"] += 1
            
            # 检查original_data是否为结构化
            original_data = record.get('original_data', {})
            if (isinstance(original_data, dict) and 
                ('question' in original_data or 'answer' in original_data) and
                isinstance(original_data.get('question'), dict)):
                enhanced_features["original_data_structured"] += 1
            
            # 检查特定字段
            if evaluation.get('json_valid') is not None:
                enhanced_features["json_valid_field"] += 1
            
            if original_data.get('rule_name'):
                enhanced_features["rule_name_field"] += 1
            
            if evaluation.get('analysis'):
                enhanced_features["detailed_analysis"] += 1
        
        # 计算特性覆盖率
        feature_coverage = {}
        feature_weights = {
            "evaluation_detail": 0.2,
            "prompt_info_enhanced": 0.15,
            "original_data_structured": 0.25,
            "json_valid_field": 0.15,
            "rule_name_field": 0.15,
            "detailed_analysis": 0.1
        }
        
        total_weighted_score = 0.0
        for feature, count in enhanced_features.items():
            coverage = count / total_records
            feature_coverage[feature] = {
                "count": count,
                "total": total_records,
                "coverage": coverage,
                "description": _get_feature_description(feature)
            }
            total_weighted_score += coverage * feature_weights.get(feature, 0.0)
        
        # 确定格式类型
        if total_weighted_score >= 0.8:
            format_type = "enhanced"
        elif total_weighted_score >= 0.3:
            format_type = "mixed"
        else:
            format_type = "legacy"
        
        # 生成建议
        recommendations = _generate_format_recommendations(format_type, feature_coverage)
        
        return {
            "format_type": format_type,
            "enhanced_features": {
                "coverage_score": total_weighted_score,
                "feature_details": feature_coverage,
                "total_records": total_records,
                "sample_record_structure": _get_record_structure_summary(sample_record) if sample_record else {}
            },
            "recommendations": recommendations,
            "compatibility_score": total_weighted_score
        }
        
    except Exception as e:
        logging.error(f"文件格式分析失败: {e}")
        return {
            "format_type": "error",
            "enhanced_features": {"error": str(e)},
            "recommendations": [f"文件分析失败: {str(e)}"],
            "compatibility_score": 0.0
        }


def _get_feature_description(feature: str) -> str:
    """获取特性描述"""
    descriptions = {
        "evaluation_detail": "详细的评估结果结构，包含json_valid、comparison_result等字段",
        "prompt_info_enhanced": "增强的提示词信息，包含matched_keyword等字段",
        "original_data_structured": "结构化的原始数据，包含question和answer对象",
        "json_valid_field": "JSON有效性标识字段",
        "rule_name_field": "规则名称字段，便于规则级别分析",
        "detailed_analysis": "详细的错误分析描述"
    }
    return descriptions.get(feature, "未知特性")


def _generate_format_recommendations(format_type: str, feature_coverage: Dict[str, Dict]) -> List[str]:
    """生成格式建议"""
    recommendations = []
    
    if format_type == "enhanced":
        recommendations.extend([
            "✅ 您的文件采用了增强格式，支持所有新特性",
            "📊 可以使用完整的分析功能，包括规则级别和关键词分析",
            "🎯 建议使用新格式专用的分析端点获取更详细的洞察"
        ])
    elif format_type == "mixed":
        recommendations.extend([
            "⚠️  您的文件为混合格式，部分记录支持新特性",
            "🔄 建议将所有记录升级到增强格式以获得最佳分析效果"
        ])
        
        # 针对缺失的特性提供具体建议
        low_coverage_features = [
            name for name, info in feature_coverage.items() 
            if info.get("coverage", 0) < 0.5
        ]
        
        if "json_valid_field" in low_coverage_features:
            recommendations.append("📝 建议在evaluation字段中添加json_valid布尔值")
        if "rule_name_field" in low_coverage_features:
            recommendations.append("📝 建议在original_data中添加rule_name字段")
        if "prompt_info_enhanced" in low_coverage_features:
            recommendations.append("📝 建议在prompt_info中添加matched_keyword字段")
            
    else:  # legacy
        recommendations.extend([
            "📄 您的文件采用传统格式，仍可正常分析",
            "⬆️  强烈建议升级到增强格式以获得更丰富的分析功能",
            "🆕 增强格式支持规则级分析、关键词匹配分析、JSON有效性检测等新特性"
        ])
    
    return recommendations


def _get_record_structure_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    """获取记录结构摘要"""
    if not record:
        return {}
    
    structure = {
        "basic_fields": [],
        "evaluation_structure": "unknown",
        "prompt_info_structure": "unknown", 
        "original_data_structure": "unknown"
    }
    
    # 基本字段
    basic_fields = ["id", "question", "expected_answer", "actual_answer", "status", "score"]
    for field in basic_fields:
        if field in record:
            structure["basic_fields"].append(field)
    
    # evaluation字段结构
    evaluation = record.get("evaluation", {})
    if isinstance(evaluation, dict):
        if "json_valid" in evaluation and "analysis" in evaluation:
            structure["evaluation_structure"] = "enhanced"
        elif len(evaluation) > 1:
            structure["evaluation_structure"] = "structured"
        else:
            structure["evaluation_structure"] = "basic"
    
    # prompt_info字段结构
    prompt_info = record.get("prompt_info", {})
    if isinstance(prompt_info, dict):
        if "matched_keyword" in prompt_info:
            structure["prompt_info_structure"] = "enhanced"
        elif len(prompt_info) > 1:
            structure["prompt_info_structure"] = "structured"
        else:
            structure["prompt_info_structure"] = "basic"
    
    # original_data字段结构
    original_data = record.get("original_data", {})
    if isinstance(original_data, dict):
        if (isinstance(original_data.get("question"), dict) and 
            isinstance(original_data.get("answer"), dict)):
            structure["original_data_structure"] = "enhanced"
        elif len(original_data) > 2:
            structure["original_data_structure"] = "structured"
        else:
            structure["original_data_structure"] = "basic"
    
    return structure 

# 新格式特性专用API端点

@router.get("/evaluation/enhanced-features/{task_id}", summary="获取新格式特性分析")
async def get_enhanced_features_analysis(
    task_id: str,
    format: str = Query("detailed", description="返回格式：detailed(详细), summary(摘要)")
):
    """
    获取新格式特性的详细分析
    
    Args:
        task_id: 任务ID
        format: 返回格式（detailed: 完整分析, summary: 关键指标摘要）
        
    Returns:
        新格式特性的详细统计和分析结果
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"任务未完成，当前状态: {task_info['status']}"
        )
    
    # 读取评估记录进行新格式特性分析
    records_path = task_info.get("evaluation_records_path")
    if not records_path or not os.path.exists(records_path):
        raise HTTPException(status_code=404, detail="评估记录文件不存在")
    
    try:
        with open(records_path, 'r', encoding='utf-8') as f:
            records_data = json.load(f)
        
        enhanced_analysis = _analyze_enhanced_features(records_data)
        
        if format == "summary":
            # 返回关键指标摘要
            summary = {
                "task_id": task_id,
                "analysis_time": datetime.now().isoformat(),
                "total_records": enhanced_analysis["coverage"]["total_records"],
                "format_type": enhanced_analysis["format_detection"]["primary_format"],
                "enhancement_score": enhanced_analysis["format_detection"]["enhancement_score"],
                "key_metrics": {
                    "json_validity_rate": enhanced_analysis["json_validity"]["valid_rate"],
                    "rules_analyzed": len(enhanced_analysis["rule_performance"]),
                    "keywords_analyzed": len(enhanced_analysis["keyword_effectiveness"]),
                    "top_performing_rule": enhanced_analysis["insights"]["best_rule"],
                    "most_effective_keyword": enhanced_analysis["insights"]["best_keyword"]
                },
                "recommendations": enhanced_analysis["recommendations"][:3]  # 前3个建议
            }
            return summary
        else:
            # 返回详细分析
            return {
                "task_id": task_id,
                "analysis_time": datetime.now().isoformat(),
                "enhanced_features_analysis": enhanced_analysis
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析新格式特性时出错: {str(e)}")


@router.get("/evaluation/keyword-analysis/{task_id}", summary="获取关键词匹配分析")
async def get_keyword_analysis(
    task_id: str,
    top_n: int = Query(10, description="返回前N个关键词，默认10个"),
    include_details: bool = Query(True, description="是否包含详细匹配记录")
):
    """
    获取关键词匹配效果的详细分析
    
    Args:
        task_id: 任务ID
        top_n: 返回前N个关键词
        include_details: 是否包含详细的匹配记录
        
    Returns:
        关键词匹配分析结果，包括效果排序、成功率、失败原因等
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"任务未完成，当前状态: {task_info['status']}"
        )
    
    records_path = task_info.get("evaluation_records_path")
    if not records_path or not os.path.exists(records_path):
        raise HTTPException(status_code=404, detail="评估记录文件不存在")
    
    try:
        with open(records_path, 'r', encoding='utf-8') as f:
            records_data = json.load(f)
        
        keyword_analysis = _analyze_keyword_effectiveness(records_data, top_n, include_details)
        
        return {
            "task_id": task_id,
            "analysis_time": datetime.now().isoformat(),
            "keyword_analysis": keyword_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析关键词效果时出错: {str(e)}")


@router.get("/evaluation/rule-performance/{task_id}", summary="获取规则级别性能分析")
async def get_rule_performance_analysis(
    task_id: str,
    rule_name: Optional[str] = Query(None, description="指定规则名称，为空则返回所有规则"),
    sort_by: str = Query("success_rate", description="排序方式：success_rate, json_valid_rate, total_count"),
    include_records: bool = Query(False, description="是否包含详细记录")
):
    """
    获取规则级别的性能分析
    
    Args:
        task_id: 任务ID
        rule_name: 指定规则名称（可选）
        sort_by: 排序方式
        include_records: 是否包含详细记录
        
    Returns:
        规则性能分析结果，包括成功率、JSON有效率、问题分布等
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")
    
    task_info = task_status[task_id]
    
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"任务未完成，当前状态: {task_info['status']}"
        )
    
    records_path = task_info.get("evaluation_records_path")
    if not records_path or not os.path.exists(records_path):
        raise HTTPException(status_code=404, detail="评估记录文件不存在")
    
    try:
        with open(records_path, 'r', encoding='utf-8') as f:
            records_data = json.load(f)
        
        rule_analysis = _analyze_rule_performance(records_data, rule_name, sort_by, include_records)
        
        return {
            "task_id": task_id,
            "analysis_time": datetime.now().isoformat(),
            "rule_performance_analysis": rule_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析规则性能时出错: {str(e)}")


# 辅助分析函数

def _analyze_enhanced_features(records_data: List[Dict]) -> Dict[str, Any]:
    """综合分析新格式特性"""
    
    total_records = len(records_data)
    if total_records == 0:
        return {"error": "没有可分析的记录"}
    
    # 格式检测分析
    records_with_json_valid = 0
    records_with_rule_name = 0
    records_with_keyword = 0
    records_with_structured_data = 0
    records_with_detailed_analysis = 0
    
    # JSON有效性统计
    json_valid_count = 0
    json_invalid_count = 0
    
    # 规则性能统计
    rule_performance = {}
    
    # 关键词效果统计
    keyword_effectiveness = {}
    
    # 分析类型分布
    analysis_types = {}
    
    # 业务对象性能
    business_object_performance = {}
    
    for record in records_data:
        # 检测增强特性
        evaluation = record.get('evaluation', {})
        prompt_info = record.get('prompt_info', {})
        original_data = record.get('original_data', {})
        
        # JSON有效性检测
        json_valid = evaluation.get('json_valid')
        if json_valid is not None:
            records_with_json_valid += 1
            if json_valid is True:
                json_valid_count += 1
            else:
                json_invalid_count += 1
        
        # 规则名称检测
        rule_name = original_data.get('rule_name')
        if rule_name:
            records_with_rule_name += 1
            
            # 规则性能统计
            if rule_name not in rule_performance:
                rule_performance[rule_name] = {
                    'total': 0,
                    'success': 0,
                    'json_valid': 0,
                    'failed': 0,
                    'success_rate': 0.0,
                    'json_valid_rate': 0.0,
                    'failure_reasons': {}
                }
            
            rule_performance[rule_name]['total'] += 1
            if record.get('status') == 'success':
                rule_performance[rule_name]['success'] += 1
            else:
                rule_performance[rule_name]['failed'] += 1
                failure_reason = evaluation.get('failure_reason', '未知原因')
                rule_performance[rule_name]['failure_reasons'][failure_reason] = \
                    rule_performance[rule_name]['failure_reasons'].get(failure_reason, 0) + 1
            
            if json_valid is True:
                rule_performance[rule_name]['json_valid'] += 1
        
        # 关键词检测
        matched_keyword = prompt_info.get('matched_keyword')
        if matched_keyword:
            records_with_keyword += 1
            
            # 关键词效果统计
            if matched_keyword not in keyword_effectiveness:
                keyword_effectiveness[matched_keyword] = {
                    'total': 0,
                    'success': 0,
                    'success_rate': 0.0,
                    'rules_used': set(),
                    'avg_score': 0.0,
                    'scores': []
                }
            
            keyword_effectiveness[matched_keyword]['total'] += 1
            if record.get('status') == 'success':
                keyword_effectiveness[matched_keyword]['success'] += 1
            
            # 记录使用的规则
            if rule_name:
                keyword_effectiveness[matched_keyword]['rules_used'].add(rule_name)
            
            # 记录分数
            score = record.get('score', 0)
            keyword_effectiveness[matched_keyword]['scores'].append(score)
        
        # 结构化数据检测
        if isinstance(original_data.get('question'), dict):
            records_with_structured_data += 1
        
        # 详细分析检测
        if evaluation.get('analysis'):
            records_with_detailed_analysis += 1
            
            # 分析类型分类
            analysis = evaluation.get('analysis', '')
            if '完美匹配' in analysis or '高质量' in analysis:
                analysis_type = '高质量匹配'
            elif 'JSON' in analysis or 'json' in analysis:
                analysis_type = 'JSON相关问题'
            elif '格式' in analysis:
                analysis_type = '格式问题'
            elif '语义' in analysis:
                analysis_type = '语义问题'
            else:
                analysis_type = '其他分析'
            
            analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
        
        # 业务对象性能统计
        business_object = original_data.get('business_object', '未知业务对象')
        if business_object not in business_object_performance:
            business_object_performance[business_object] = {
                'total': 0,
                'success': 0,
                'success_rate': 0.0,
                'rules': set()
            }
        
        business_object_performance[business_object]['total'] += 1
        if record.get('status') == 'success':
            business_object_performance[business_object]['success'] += 1
        if rule_name:
            business_object_performance[business_object]['rules'].add(rule_name)
    
    # 计算性能指标
    for rule_name, stats in rule_performance.items():
        if stats['total'] > 0:
            stats['success_rate'] = stats['success'] / stats['total']
            stats['json_valid_rate'] = stats['json_valid'] / stats['total']
    
    for keyword, stats in keyword_effectiveness.items():
        if stats['total'] > 0:
            stats['success_rate'] = stats['success'] / stats['total']
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            stats['rules_used'] = list(stats['rules_used'])  # 转换为列表
    
    for bo_name, stats in business_object_performance.items():
        if stats['total'] > 0:
            stats['success_rate'] = stats['success'] / stats['total']
            stats['rules'] = list(stats['rules'])  # 转换为列表
    
    # 计算增强评分
    feature_weights = {
        'json_valid': 0.25,
        'rule_name': 0.25, 
        'keyword': 0.20,
        'structured_data': 0.20,
        'detailed_analysis': 0.10
    }
    
    enhancement_score = (
        (records_with_json_valid / total_records) * feature_weights['json_valid'] +
        (records_with_rule_name / total_records) * feature_weights['rule_name'] +
        (records_with_keyword / total_records) * feature_weights['keyword'] +
        (records_with_structured_data / total_records) * feature_weights['structured_data'] +
        (records_with_detailed_analysis / total_records) * feature_weights['detailed_analysis']
    )
    
    # 确定主要格式类型
    if enhancement_score >= 0.8:
        primary_format = "enhanced"
    elif enhancement_score >= 0.3:
        primary_format = "mixed"
    else:
        primary_format = "legacy"
    
    # 生成洞察
    insights = {
        "best_rule": max(rule_performance.items(), key=lambda x: x[1]['success_rate'])[0] if rule_performance else "无",
        "worst_rule": min(rule_performance.items(), key=lambda x: x[1]['success_rate'])[0] if rule_performance else "无",
        "best_keyword": max(keyword_effectiveness.items(), key=lambda x: x[1]['success_rate'])[0] if keyword_effectiveness else "无",
        "worst_keyword": min(keyword_effectiveness.items(), key=lambda x: x[1]['success_rate'])[0] if keyword_effectiveness else "无",
        "main_issue": max(analysis_types.items(), key=lambda x: x[1])[0] if analysis_types else "无明显问题"
    }
    
    # 生成建议
    recommendations = []
    
    if json_invalid_count > json_valid_count:
        recommendations.append("JSON有效性较低，建议检查数据生成逻辑")
    
    if rule_performance:
        low_performance_rules = [name for name, stats in rule_performance.items() if stats['success_rate'] < 0.5]
        if low_performance_rules:
            recommendations.append(f"以下规则性能较低，建议优化: {', '.join(low_performance_rules[:3])}")
    
    if enhancement_score < 0.5:
        recommendations.append("建议升级到增强格式以获得更详细的分析功能")
    
    if '高质量匹配' not in analysis_types or analysis_types.get('高质量匹配', 0) < total_records * 0.5:
        recommendations.append("建议改进提示词和规则以提高匹配质量")
    
    return {
        "format_detection": {
            "primary_format": primary_format,
            "enhancement_score": enhancement_score,
            "feature_coverage": {
                "json_valid": records_with_json_valid / total_records,
                "rule_name": records_with_rule_name / total_records,
                "keyword": records_with_keyword / total_records,
                "structured_data": records_with_structured_data / total_records,
                "detailed_analysis": records_with_detailed_analysis / total_records
            }
        },
        "json_validity": {
            "valid_count": json_valid_count,
            "invalid_count": json_invalid_count,
            "total_with_info": records_with_json_valid,
            "valid_rate": json_valid_count / records_with_json_valid if records_with_json_valid > 0 else 0.0
        },
        "rule_performance": dict(sorted(rule_performance.items(), key=lambda x: x[1]['success_rate'], reverse=True)),
        "keyword_effectiveness": dict(sorted(keyword_effectiveness.items(), key=lambda x: x[1]['success_rate'], reverse=True)),
        "analysis_distribution": analysis_types,
        "business_object_performance": dict(sorted(business_object_performance.items(), key=lambda x: x[1]['success_rate'], reverse=True)),
        "coverage": {
            "total_records": total_records,
            "records_with_json_valid": records_with_json_valid,
            "records_with_rule_name": records_with_rule_name,
            "records_with_keyword": records_with_keyword,
            "records_with_structured_data": records_with_structured_data,
            "records_with_detailed_analysis": records_with_detailed_analysis
        },
        "insights": insights,
        "recommendations": recommendations
    }


def _analyze_keyword_effectiveness(records_data: List[Dict], top_n: int, include_details: bool) -> Dict[str, Any]:
    """分析关键词匹配效果"""
    
    keyword_stats = {}
    keyword_records = {}
    
    for record in records_data:
        prompt_info = record.get('prompt_info', {})
        matched_keyword = prompt_info.get('matched_keyword')
        
        if not matched_keyword:
            continue
        
        if matched_keyword not in keyword_stats:
            keyword_stats[matched_keyword] = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'success_rate': 0.0,
                'avg_score': 0.0,
                'scores': [],
                'business_objects': set(),
                'rules': set(),
                'failure_reasons': {}
            }
            keyword_records[matched_keyword] = []
        
        keyword_stats[matched_keyword]['total'] += 1
        
        status = record.get('status')
        if status == 'success':
            keyword_stats[matched_keyword]['success'] += 1
        else:
            keyword_stats[matched_keyword]['failed'] += 1
            failure_reason = extract_detailed_failure_reason(record)
            keyword_stats[matched_keyword]['failure_reasons'][failure_reason] = \
                keyword_stats[matched_keyword]['failure_reasons'].get(failure_reason, 0) + 1
        
        # 记录分数
        score = record.get('score', 0)
        keyword_stats[matched_keyword]['scores'].append(score)
        
        # 记录业务对象和规则
        original_data = record.get('original_data', {})
        business_object = original_data.get('business_object')
        rule_name = original_data.get('rule_name')
        
        if business_object:
            keyword_stats[matched_keyword]['business_objects'].add(business_object)
        if rule_name:
            keyword_stats[matched_keyword]['rules'].add(rule_name)
        
        # 保存详细记录（如果需要）
        if include_details:
            keyword_records[matched_keyword].append({
                'id': record.get('id'),
                'question': record.get('question'),
                'status': status,
                'score': score,
                'business_object': business_object,
                'rule_name': rule_name,
                'json_valid': record.get('evaluation', {}).get('json_valid'),
                'failure_reason': extract_detailed_failure_reason(record)
            })
    
    # 计算统计指标
    for keyword, stats in keyword_stats.items():
        if stats['total'] > 0:
            stats['success_rate'] = stats['success'] / stats['total']
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            stats['min_score'] = min(stats['scores'])
            stats['max_score'] = max(stats['scores'])
            stats['business_objects'] = list(stats['business_objects'])
            stats['rules'] = list(stats['rules'])
    
    # 排序并取前N个
    sorted_keywords = sorted(keyword_stats.items(), key=lambda x: x[1]['success_rate'], reverse=True)
    top_keywords = dict(sorted_keywords[:top_n])
    
    # 生成分析摘要
    total_keywords = len(keyword_stats)
    avg_success_rate = sum(stats['success_rate'] for stats in keyword_stats.values()) / total_keywords if total_keywords > 0 else 0.0
    
    analysis_summary = {
        "total_keywords": total_keywords,
        "analyzed_keywords": min(top_n, total_keywords),
        "avg_success_rate": avg_success_rate,
        "best_keyword": sorted_keywords[0][0] if sorted_keywords else "无",
        "worst_keyword": sorted_keywords[-1][0] if sorted_keywords else "无"
    }
    
    result = {
        "summary": analysis_summary,
        "keyword_effectiveness": top_keywords
    }
    
    if include_details:
        result["detailed_records"] = {k: keyword_records[k] for k in top_keywords.keys() if k in keyword_records}
    
    return result


def _analyze_rule_performance(records_data: List[Dict], specific_rule: Optional[str], sort_by: str, include_records: bool) -> Dict[str, Any]:
    """分析规则级别性能"""
    
    rule_stats = {}
    rule_records = {}
    
    for record in records_data:
        original_data = record.get('original_data', {})
        rule_name = original_data.get('rule_name', '未知规则')
        
        if specific_rule and rule_name != specific_rule:
            continue
        
        if rule_name not in rule_stats:
            rule_stats[rule_name] = {
                'total': 0,
                'success': 0,
                'failed': 0,
                'json_valid': 0,
                'json_invalid': 0,
                'success_rate': 0.0,
                'json_valid_rate': 0.0,
                'avg_score': 0.0,
                'scores': [],
                'business_objects': set(),
                'keywords': set(),
                'failure_reasons': {},
                'analysis_types': {}
            }
            rule_records[rule_name] = []
        
        rule_stats[rule_name]['total'] += 1
        
        status = record.get('status')
        if status == 'success':
            rule_stats[rule_name]['success'] += 1
        else:
            rule_stats[rule_name]['failed'] += 1
            failure_reason = extract_detailed_failure_reason(record)
            rule_stats[rule_name]['failure_reasons'][failure_reason] = \
                rule_stats[rule_name]['failure_reasons'].get(failure_reason, 0) + 1
        
        # JSON有效性统计
        json_valid = record.get('evaluation', {}).get('json_valid')
        if json_valid is True:
            rule_stats[rule_name]['json_valid'] += 1
        elif json_valid is False:
            rule_stats[rule_name]['json_invalid'] += 1
        
        # 记录分数
        score = record.get('score', 0)
        rule_stats[rule_name]['scores'].append(score)
        
        # 记录业务对象和关键词
        business_object = original_data.get('business_object')
        matched_keyword = record.get('prompt_info', {}).get('matched_keyword')
        
        if business_object:
            rule_stats[rule_name]['business_objects'].add(business_object)
        if matched_keyword:
            rule_stats[rule_name]['keywords'].add(matched_keyword)
        
        # 分析类型统计
        analysis = record.get('evaluation', {}).get('analysis', '')
        if analysis:
            if '完美匹配' in analysis or '高质量' in analysis:
                analysis_type = '高质量匹配'
            elif 'JSON' in analysis or 'json' in analysis:
                analysis_type = 'JSON相关问题'
            elif '格式' in analysis:
                analysis_type = '格式问题'
            elif '语义' in analysis:
                analysis_type = '语义问题'
            else:
                analysis_type = '其他分析'
            
            rule_stats[rule_name]['analysis_types'][analysis_type] = \
                rule_stats[rule_name]['analysis_types'].get(analysis_type, 0) + 1
        
        # 保存详细记录（如果需要）
        if include_records:
            rule_records[rule_name].append({
                'id': record.get('id'),
                'question': record.get('question'),
                'expected_answer': record.get('expected_answer'),
                'actual_answer': record.get('actual_answer'),
                'status': status,
                'score': score,
                'business_object': business_object,
                'matched_keyword': matched_keyword,
                'json_valid': json_valid,
                'failure_reason': extract_detailed_failure_reason(record),
                'analysis': analysis
            })
    
    # 计算统计指标
    for rule_name, stats in rule_stats.items():
        if stats['total'] > 0:
            stats['success_rate'] = stats['success'] / stats['total']
            json_total = stats['json_valid'] + stats['json_invalid']
            stats['json_valid_rate'] = stats['json_valid'] / json_total if json_total > 0 else 0.0
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
            stats['min_score'] = min(stats['scores'])
            stats['max_score'] = max(stats['scores'])
            stats['business_objects'] = list(stats['business_objects'])
            stats['keywords'] = list(stats['keywords'])
    
    # 排序
    sort_key_map = {
        'success_rate': lambda x: x[1]['success_rate'],
        'json_valid_rate': lambda x: x[1]['json_valid_rate'],
        'total_count': lambda x: x[1]['total']
    }
    
    sort_key = sort_key_map.get(sort_by, sort_key_map['success_rate'])
    sorted_rules = sorted(rule_stats.items(), key=sort_key, reverse=True)
    
    # 生成分析摘要
    total_rules = len(rule_stats)
    if total_rules > 0:
        avg_success_rate = sum(stats['success_rate'] for stats in rule_stats.values()) / total_rules
        avg_json_valid_rate = sum(stats['json_valid_rate'] for stats in rule_stats.values()) / total_rules
    else:
        avg_success_rate = 0.0
        avg_json_valid_rate = 0.0
    
    analysis_summary = {
        "total_rules": total_rules,
        "avg_success_rate": avg_success_rate,
        "avg_json_valid_rate": avg_json_valid_rate,
        "best_rule": sorted_rules[0][0] if sorted_rules else "无",
        "worst_rule": sorted_rules[-1][0] if sorted_rules else "无",
        "sort_by": sort_by
    }
    
    if specific_rule:
        analysis_summary["specific_rule"] = specific_rule
        analysis_summary["rule_found"] = specific_rule in rule_stats
    
    result = {
        "summary": analysis_summary,
        "rule_performance": dict(sorted_rules)
    }
    
    if include_records:
        result["detailed_records"] = rule_records
    
    return result 

@router.get("/detailed-issue-analysis/{task_id}")
async def get_detailed_issue_analysis(
    task_id: str,
    include_success_issues: bool = Query(True, description="是否包含成功记录中的问题"),
    min_score_threshold: int = Query(10, description="低于此分数的成功记录视为有问题"),
    format: str = Query("detailed", description="返回格式: detailed 或 summary")
):
    """
    获取详细的问题分析
    包括失败记录和成功但有问题的记录的详细分析
    """
    try:
        # 检查任务状态
        task_info = analysis_tasks.get(task_id)
        if not task_info:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task_info["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"任务状态: {task_info['status']}")
        
        # 读取评估记录数据
        records_path = task_info.get("evaluation_records_path")
        if not records_path or not os.path.exists(records_path):
            raise HTTPException(status_code=404, detail="评估记录文件不存在")
        
        with open(records_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('logs', [])
        if not records:
            raise HTTPException(status_code=404, detail="没有找到评估记录")
        
        # 分类记录
        failed_records = []
        problematic_success_records = []
        clean_success_records = []
        
        for record in records:
            evaluation = record.get('evaluation', {})
            status = evaluation.get('status', 'unknown')
            score = evaluation.get('score', 0)
            analysis = evaluation.get('analysis', '')
            failure_reason = evaluation.get('failure_reason', '')
            
            if status != 'success':
                # 真正的失败记录
                failed_records.append({
                    'id': record.get('id'),
                    'status': status,
                    'score': score,
                    'failure_reason': extract_detailed_failure_reason(record),
                    'analysis': analysis,
                    'question': record.get('question', '')[:200] + '...' if len(record.get('question', '')) > 200 else record.get('question', ''),
                    'rule_name': record.get('original_data', {}).get('rule_name', ''),
                    'matched_keyword': record.get('prompt_info', {}).get('matched_keyword', ''),
                    'business_object': record.get('original_data', {}).get('business_object', ''),
                    'issue_type': 'failed'
                })
            else:
                # 成功记录，检查是否有问题
                has_issues = False
                issue_details = []
                
                if include_success_issues:
                    # 检查详细分析中的问题指标
                    if analysis:
                        if '低位错误:' in analysis:
                            has_issues = True
                            issue_details.append('低位错误')
                        if '条件值不一致' in analysis:
                            has_issues = True
                            issue_details.append('字段值不匹配')
                        if '值变更:' in analysis:
                            has_issues = True
                            issue_details.append('字段值格式变更')
                        if '条件数量一致，内容不一致' in analysis:
                            has_issues = True
                            issue_details.append('字段内容格式差异')
                    
                    # 检查分数
                    if score < min_score_threshold:
                        has_issues = True
                        issue_details.append(f'分数偏低({score}/{min_score_threshold})')
                
                if has_issues:
                    problematic_success_records.append({
                        'id': record.get('id'),
                        'status': status,
                        'score': score,
                        'failure_reason': extract_detailed_failure_reason(record),
                        'analysis': analysis,
                        'question': record.get('question', '')[:200] + '...' if len(record.get('question', '')) > 200 else record.get('question', ''),
                        'rule_name': record.get('original_data', {}).get('rule_name', ''),
                        'matched_keyword': record.get('prompt_info', {}).get('matched_keyword', ''),
                        'business_object': record.get('original_data', {}).get('business_object', ''),
                        'issue_type': 'success_with_issues',
                        'issue_details': issue_details
                    })
                else:
                    clean_success_records.append(record.get('id'))
        
        # 提取详细的失败原因分析
        def extract_detailed_reason(record_data):
            analysis = record_data.get('analysis', '')
            failure_reason = record_data.get('failure_reason', '')
            
            if failure_reason and failure_reason.strip():
                return failure_reason.strip()
            
            if analysis:
                # 解析低位错误
                import re
                low_error_match = re.search(r'低位错误:\s*(\d+)\(([^)]+)\)', analysis)
                if low_error_match:
                    error_code = low_error_match.group(1)
                    error_type = low_error_match.group(2)
                    return f"低级错误代码{error_code}: {error_type}"
                
                # 其他模式
                if '条件值不一致' in analysis:
                    return "字段值不匹配"
                elif '条件数量一致，内容不一致' in analysis:
                    return "字段内容格式差异"
                elif '值变更:' in analysis:
                    return "字段值格式标准化问题"
                
                return analysis[:100] + ('...' if len(analysis) > 100 else '')
            
            if record_data.get('status') == 'success' and record_data.get('score', 0) < min_score_threshold:
                return f"部分匹配问题 (得分: {record_data.get('score')}/10)"
            
            return "未知原因"
        
        # 统计失败原因
        reason_stats = {}
        all_problematic = failed_records + problematic_success_records
        
        for record in all_problematic:
            reason = extract_detailed_reason(record)
            if reason not in reason_stats:
                reason_stats[reason] = {
                    'count': 0,
                    'records': [],
                    'score_range': {'min': 10, 'max': 0, 'avg': 0},
                    'business_objects': set(),
                    'rule_names': set(),
                    'keywords': set()
                }
            
            reason_stats[reason]['count'] += 1
            reason_stats[reason]['records'].append(record)
            
            # 统计分数范围
            score = record['score']
            reason_stats[reason]['score_range']['min'] = min(reason_stats[reason]['score_range']['min'], score)
            reason_stats[reason]['score_range']['max'] = max(reason_stats[reason]['score_range']['max'], score)
            
            # 收集相关信息
            if record['business_object']:
                reason_stats[reason]['business_objects'].add(record['business_object'])
            if record['rule_name']:
                reason_stats[reason]['rule_names'].add(record['rule_name'])
            if record['matched_keyword']:
                reason_stats[reason]['keywords'].add(record['matched_keyword'])
        
        # 计算平均分数
        for reason in reason_stats:
            if reason_stats[reason]['count'] > 0:
                total_score = sum(r['score'] for r in reason_stats[reason]['records'])
                reason_stats[reason]['score_range']['avg'] = round(total_score / reason_stats[reason]['count'], 2)
        
        # 构建响应
        if format == "summary":
            # 简化格式
            result = {
                'task_id': task_id,
                'total_records': len(records),
                'failed_records_count': len(failed_records),
                'problematic_success_count': len(problematic_success_records),
                'clean_success_count': len(clean_success_records),
                'reason_summary': [
                    {
                        'reason': reason,
                        'count': stats['count'],
                        'percentage': round((stats['count'] / len(all_problematic)) * 100, 2) if all_problematic else 0,
                        'avg_score': stats['score_range']['avg']
                    }
                    for reason, stats in sorted(reason_stats.items(), key=lambda x: x[1]['count'], reverse=True)
                ]
            }
        else:
            # 详细格式
            result = {
                'task_id': task_id,
                'analysis_summary': {
                    'total_records': len(records),
                    'failed_records_count': len(failed_records),
                    'problematic_success_count': len(problematic_success_records),
                    'clean_success_count': len(clean_success_records),
                    'total_problematic': len(all_problematic)
                },
                'detailed_analysis': {}
            }
            
            for reason, stats in sorted(reason_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                result['detailed_analysis'][reason] = {
                    'count': stats['count'],
                    'percentage': round((stats['count'] / len(all_problematic)) * 100, 2) if all_problematic else 0,
                    'score_statistics': {
                        'min': stats['score_range']['min'],
                        'max': stats['score_range']['max'],
                        'average': stats['score_range']['avg']
                    },
                    'affected_scope': {
                        'business_objects': list(stats['business_objects']),
                        'rule_names': list(stats['rule_names']),
                        'keywords': list(stats['keywords'])
                    },
                    'example_records': stats['records'][:5]  # 限制示例数量
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取详细问题分析失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


# 在文件末尾添加此路由定义
