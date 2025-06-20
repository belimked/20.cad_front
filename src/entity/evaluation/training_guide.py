#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练指南模型

定义训练指南相关的数据结构
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class RecommendationType(str, Enum):
    """建议类型枚举"""
    TRAINING = "training"  # 需要训练
    PROMPT = "prompt"      # 改进提示词
    BOTH = "both"          # 两者都需要


class Priority(str, Enum):
    """优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TrainingRecommendation:
    """训练建议类"""
    rule_id: str                               # 规则ID
    business_object: str                       # 业务对象
    failure_count: int                         # 失败次数
    failure_percentage: float                  # 失败百分比
    failure_types: List[str]                   # 失败类型列表
    similarity_score: float                    # 相似度分数
    recommendation_type: RecommendationType    # 建议类型
    description: str                           # 建议描述
    priority: Priority = Priority.MEDIUM       # 优先级
    examples: List[Dict[str, Any]] = field(default_factory=list)  # 示例记录
    
    # 新增字段
    failure_type_distribution: Dict[str, int] = field(default_factory=dict)  # 各失败类型数量
    failure_type_percentage: Dict[str, float] = field(default_factory=dict)  # 各失败类型占比(%)
    score_percentage: float = 0.0               # 该rule失败记录分数占业务对象总分百分比
    weight_analysis: str = "medium"             # 权重分析: high/medium/low
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 确保所有字段值都是可序列化的
        examples = []
        for example in self.examples:
            if isinstance(example, dict):
                # 确保字典中的值是可序列化的
                safe_example = {}
                for k, v in example.items():
                    # 处理可能的特殊类型
                    if isinstance(v, (str, int, float, bool, type(None))):
                        safe_example[k] = v
                    else:
                        safe_example[k] = str(v)
                examples.append(safe_example)
            else:
                # 如果不是字典，转换为字符串
                examples.append(str(example))
        
        # 确保failure_types是字符串列表
        failure_types = []
        for ft in self.failure_types:
            if isinstance(ft, str):
                failure_types.append(ft)
            else:
                failure_types.append(str(ft))
        
        return {
            "rule_id": str(self.rule_id),
            "business_object": str(self.business_object),
            "failure_count": self.failure_count,
            "failure_percentage": round(float(self.failure_percentage), 1),
            "failure_types": failure_types,
            "similarity_score": float(self.similarity_score),
            "recommendation_type": str(self.recommendation_type.value),
            "description": str(self.description),
            "priority": str(self.priority.value),
            "examples": examples,
            
            # 新增字段
            "failure_type_distribution": dict(self.failure_type_distribution),
            "failure_type_percentage": {k: round(float(v), 1) for k, v in self.failure_type_percentage.items()},
            "score_percentage": round(float(self.score_percentage), 1),
            "weight_analysis": str(self.weight_analysis)
        }


@dataclass
class BusinessObjectTrainingGuide:
    """业务对象训练指南"""
    business_object: str                               # 业务对象
    total_records: int                                 # 总记录数
    failure_count: int                                 # 失败记录数
    failure_percentage: float                          # 失败百分比
    recommendations: List[TrainingRecommendation] = field(default_factory=list)  # 训练建议列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 确保所有字段值都是可序列化的
        recommendations = []
        for rec in self.recommendations:
            try:
                recommendations.append(rec.to_dict())
            except Exception as e:
                # 如果转换失败，添加一个简化版本
                recommendations.append({
                    "rule_id": str(rec.rule_id),
                    "business_object": str(rec.business_object),
                    "failure_count": rec.failure_count,
                    "error": f"无法序列化完整建议: {str(e)}"
                })
        
        return {
            "business_object": str(self.business_object),
            "total_records": int(self.total_records),
            "failure_count": int(self.failure_count),
            "failure_percentage": float(self.failure_percentage),
            "recommendations": recommendations
        }


@dataclass
class TrainingGuide:
    """训练指南"""
    total_records: int                                 # 总记录数
    total_failures: int                                # 总失败记录数
    overall_failure_percentage: float                  # 整体失败率
    timestamp: datetime = field(default_factory=datetime.now)  # 生成时间
    summary: str = ""                                   # 总体摘要
    business_object_guides: Dict[str, BusinessObjectTrainingGuide] = field(default_factory=dict)  # 按业务对象划分的指南
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 确保所有字段值都是可序列化的
        bo_guides = {}
        for bo, guide in self.business_object_guides.items():
            try:
                # 确保业务对象名称不包含特殊字符
                safe_bo = str(bo).replace('{', '_').replace('}', '_')
                bo_guides[safe_bo] = guide.to_dict()
            except Exception as e:
                # 如果转换失败，添加一个简化版本
                bo_guides[str(bo).replace('{', '_').replace('}', '_')] = {
                    "error": f"无法序列化业务对象指南: {str(e)}",
                    "business_object": str(bo)
                }
        
        # 确保时间戳是ISO格式字符串
        try:
            timestamp = self.timestamp.isoformat()
        except:
            timestamp = datetime.now().isoformat()
        
        return {
            "total_records": int(self.total_records),
            "total_failures": int(self.total_failures),
            "overall_failure_percentage": float(self.overall_failure_percentage),
            "timestamp": timestamp,
            "summary": str(self.summary),
            "business_object_guides": bo_guides
        }
    
    def get_all_recommendations(self) -> List[TrainingRecommendation]:
        """获取所有建议"""
        all_recs = []
        for bo_guide in self.business_object_guides.values():
            all_recs.extend(bo_guide.recommendations)
        return all_recs
    
    def get_high_priority_recommendations(self) -> List[TrainingRecommendation]:
        """获取高优先级建议"""
        return [rec for rec in self.get_all_recommendations() 
                if rec.priority == Priority.HIGH] 