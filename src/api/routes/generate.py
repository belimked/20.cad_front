from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime
import logging
from collections import Counter
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 导入千问API服务
from src.service.qwen_api_service import generate_and_save_data, generate_dialogs_and_raw_data

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
GENERATED_DIR = BASE_DIR / "generated_data"

# 确保生成数据目录存在
if not GENERATED_DIR.exists():
    GENERATED_DIR.mkdir(parents=True)

@router.post("/generate/{business_type}")
async def generate_data(
    business_type: str, 
    params: Dict[str, Any] = Body(...)
):
    """
    根据业务类型生成训练数据
    
    参数:
    - business_type: 业务类型，如searchStaff、searchCargo等
    - params: 包含生成参数的字典
        - count: 生成数量
        - variation: 数据变化程度（数值）
        - ruleIds: 规则ID列表（可选）
        - includeErrors: 是否包含错误数据
    """
    try:
        # 获取参数
        count = int(params.get("count", 200))
        variation_value = params.get("variation", 5)
        rule_ids = params.get("ruleIds", None)  # 获取规则ID列表
        
        # 验证参数
        if count < 1 or count > 500:
            raise HTTPException(status_code=400, detail="生成数量必须在1到500之间")
            
        # 将数值转换为变化程度
        try:
            variation_value = int(variation_value)
            # 不再限制范围
            # if variation_value < 1 or variation_value > 10:
            #     raise HTTPException(status_code=400, detail="变化程度必须在1到10之间")
            
            # 根据数值设置variations_per_rule参数
            variations_per_rule = variation_value
        except (ValueError, TypeError):
            # 兼容旧版API，处理字符串变化程度
            variation_level = str(variation_value).lower()
            if variation_level == "low":
                variations_per_rule = 2
            elif variation_level == "medium":
                variations_per_rule = 5
            else:  # high
                variations_per_rule = 10
        
        # 处理规则ID参数
        ruleids_str = None
        if rule_ids:
            if isinstance(rule_ids, list):
                # 如果是列表，转换为逗号分隔的字符串
                ruleids_str = ",".join(map(str, rule_ids))
            elif isinstance(rule_ids, str):
                # 如果已经是字符串，直接使用
                ruleids_str = rule_ids
                
        # 记录请求信息
        logger.info(f"生成数据请求: 业务类型={business_type}, 数量={count}, 变化程度={variations_per_rule}, 规则IDs={ruleids_str}")
        
        # 直接使用qwen_api_service中的函数生成数据
        try:
            # 使用generate_dialogs_and_raw_data生成对话数据和原始数据
            _, raw_data = generate_dialogs_and_raw_data(
                business_object=business_type,
                total_samples=count,
                variations_per_rule=variations_per_rule,
                ruleids=ruleids_str
            )
            
            # 在截断前统计规则分布
            total_generated = len(raw_data)
            rule_ids = [item.get('rule_id', 'unknown') for item in raw_data]
            rule_counts = Counter(rule_ids)
            
            # 准备统计信息
            stats = {
                "total_generated": total_generated,
                "rule_distribution": [
                    {"rule_id": rule_id, "count": count} 
                    for rule_id, count in rule_counts.most_common()
                ]
            }
            
            # 确保不超过请求的数量
            if len(raw_data) > count:
                raw_data = raw_data[:count]
                
            # 统计数据并记录日志
            logger.info(f"数据生成统计: 业务类型={business_type}, 总生成数量={total_generated}, 实际返回数量={len(raw_data)}")
            
            # 记录规则分布
            rule_distribution = ", ".join([f"规则{rule_id}:{count}条" for rule_id, count in rule_counts.most_common()])
            logger.info(f"规则分布: {rule_distribution}")
                
            # 保留原始数据的完整属性，而不仅仅是提取answer字段
            result = []
            for item in raw_data:
                # 保留原始数据项的完整属性
                result.append(item)
                    
            logger.info(f"生成成功，返回 {len(result)} 条数据")
            
            # 返回数据和统计信息
            return {
                "data": result,
                "stats": {
                    "total_generated": total_generated,
                    "returned": len(result),
                    "rule_distribution": rule_distribution
                }
            }
        except ValueError as e:
            if "不支持的业务对象" in str(e):
                raise HTTPException(status_code=400, detail=str(e))
            raise
            
    except ImportError as e:
        logger.error(f"导入服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入服务失败: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成数据失败: {str(e)}")

@router.post("/save-generated/{business_type}")
async def save_generated_data(
    business_type: str,
    params: Dict[str, Any] = Body(...)
):
    """
    直接生成数据并保存到服务器
    
    参数:
    - business_type: 业务类型
    - params: 包含生成参数和配置的字典
        - count: 生成数量
        - variation: 数据变化程度（数值）
        - ruleIds: 规则ID列表（可选）
        - prefix: 文件前缀（默认为"export"）
        - evaluation_percentage: 评估数据百分比（默认为10）
    """
    try:
        # 从参数中获取生成参数和配置
        count = int(params.get("count", 200))
        variation_value = params.get("variation", 5)
        rule_ids = params.get("ruleIds", None)
        prefix = params.get("prefix", "export")
        evaluation_percentage = params.get("evaluation_percentage", 10)
        
        # 验证参数
        if count < 1:
            raise HTTPException(status_code=400, detail="生成数量必须大于0")
        
        # 验证百分比范围
        if evaluation_percentage < 1 or evaluation_percentage > 100:
            raise HTTPException(status_code=400, detail="评估数据百分比必须在1-100之间")
        
        # 处理变化程度参数（与generate API保持一致）
        try:
            variation_value = int(variation_value)
            variations_per_rule = variation_value
        except (ValueError, TypeError):
            # 兼容旧版API，处理字符串变化程度
            variation_level = str(variation_value).lower()
            if variation_level == "low":
                variations_per_rule = 2
            elif variation_level == "medium":
                variations_per_rule = 5
            else:  # high
                variations_per_rule = 10
        
        # 处理规则ID参数（与generate API保持一致）
        ruleids_str = None
        if rule_ids:
            if isinstance(rule_ids, list):
                ruleids_str = ",".join(map(str, rule_ids))
            elif isinstance(rule_ids, str):
                ruleids_str = rule_ids
        
        # 记录请求信息
        logger.info(f"保存数据请求: 业务类型={business_type}, 数量={count}, 变化程度={variations_per_rule}, 规则IDs={ruleids_str}")
        
        # 直接生成数据
        try:
            _, raw_data = generate_dialogs_and_raw_data(
                business_object=business_type,
                total_samples=count,
                variations_per_rule=variations_per_rule,
                ruleids=ruleids_str
            )
            
            # 记录生成结果
            total_generated = len(raw_data)
            logger.info(f"成功生成数据: 业务类型={business_type}, 生成数量={total_generated}")
            
            # # 确保不超过请求的数量
            # if len(raw_data) > count:
            #     raw_data = raw_data[:count]
                
        except ValueError as e:
            if "不支持的业务对象" in str(e):
                raise HTTPException(status_code=400, detail=str(e))
            raise
        except Exception as e:
            logger.error(f"生成数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"生成数据失败: {str(e)}")
        
        # 创建时间戳目录结构: outputs/export/时间戳
        timestamp = datetime.now().strftime("%Y%m%d")
        export_dir = BASE_DIR / "outputs" / "export" / timestamp
        
        # 确保目录存在
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        raw_filename = f"{prefix}_raw_data_{business_type}_{timestamp}.jsonl"
        qwen_filename = f"{prefix}_qwen_data_{business_type}_{timestamp}.jsonl"
        
        # 文件路径
        raw_file_path = export_dir / raw_filename
        qwen_file_path = export_dir / qwen_filename
        
        # 1. 准备raw数据用于保存（保持原始格式）
        raw_data_for_saving = []
        for item in raw_data:
            raw_item = {
                "business_object": business_type,
                "rule_id": item.get("rule_id", ""),
                "rule_name": item.get("rule_name", ""),
                "question": item.get("question", {}),
                "answer": item.get("answer", {}),
                "codebase": item.get("codebase", ""),
                "formatted_question": item.get("formatted_question", ""),
                "formatted_answer": item.get("formatted_answer", ""),
                "combo_value": item.get("combo_value", f"{business_type}_{item.get('rule_id', '')}")
            }
            raw_data_for_saving.append(raw_item)
        
        # 从raw_data_for_saving中随机抽取指定百分比的数据
        total_count = len(raw_data_for_saving)
        sample_count = max(1, int(total_count * evaluation_percentage / 100))
        sampled_raw_data = random.sample(raw_data_for_saving, sample_count)
        
        # 2. 准备qwen数据 - 对话格式
        qwen_data = []
        for item in raw_data:
            qwen_item = {
                "messages": [
                    {
                        "role": "user",
                        "content": item.get("formatted_question", "")
                    },
                    {
                        "role": "assistant", 
                        "content": item.get("formatted_answer", "")
                    }
                ]
            }
            qwen_data.append(qwen_item)
        
        # 3. 保存raw数据（抽样后） - JSONL格式
        with open(raw_file_path, "w", encoding="utf-8") as f:
            for item in sampled_raw_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # 4. 保存qwen数据 - JSONL格式  
        with open(qwen_file_path, "w", encoding="utf-8") as f:
            for item in qwen_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        logger.info(f"保存数据到目录: {export_dir}")
        logger.info(f"Raw数据文件: {raw_file_path} (抽样{sample_count}条)")
        logger.info(f"Qwen数据文件: {qwen_file_path} (完整{len(qwen_data)}条)")
        
        return {
            "message": f"数据已生成并保存到服务器",
            "directory": str(export_dir),
            "files": {
                "raw_file": raw_filename,
                "qwen_file": qwen_filename
            },
            "generated_count": total_generated,
            "original_count": len(raw_data),
            "raw_count": sample_count,
            "qwen_count": len(qwen_data),
            "evaluation_percentage": evaluation_percentage,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"保存数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存数据失败: {str(e)}") 
