"""
评估记录数据结构

定义单条评估记录的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class EvaluationRecord:
    """单条评估记录数据结构"""
    
    # 基本信息
    id: int
    question: str
    expected_answer: str
    actual_answer: str
    raw_answer: str
    
    # 处理信息
    processing_time: float
    timestamp: datetime
    status: str  # "success" or "failed"
    
    # 评估结果
    score: int
    evaluation: Dict[str, Any]
    
    # 提示词信息
    prompt_info: Dict[str, Any]
    
    # 原始数据信息
    original_data: Dict[str, Any]
    
    # 来源文件
    source_file: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationRecord':
        """从字典创建评估记录"""
        return cls(
            id=data.get('id'),
            question=data.get('question', ''),
            expected_answer=data.get('expected_answer', ''),
            actual_answer=data.get('actual_answer', ''),
            raw_answer=data.get('raw_answer', ''),
            processing_time=data.get('processing_time', 0.0),
            timestamp=datetime.fromisoformat(data.get('timestamp', '').replace('Z', '+00:00')) if data.get('timestamp') else datetime.now(),
            status=data.get('status', 'unknown'),
            score=data.get('score', 0),
            evaluation=data.get('evaluation', {}),
            prompt_info=data.get('prompt_info', {}),
            original_data=data.get('original_data', {}),
            source_file=data.get('source_file', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'question': self.question,
            'expected_answer': self.expected_answer,
            'actual_answer': self.actual_answer,
            'raw_answer': self.raw_answer,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'score': self.score,
            'evaluation': self.evaluation,
            'prompt_info': self.prompt_info,
            'original_data': self.original_data,
            'source_file': self.source_file
        }
    
    @property
    def is_successful(self) -> bool:
        """是否评估成功"""
        return self.status == 'success'
    
    @property
    def failure_reason(self) -> Optional[str]:
        """获取失败原因"""
        if self.is_successful:
            return None
        return self.evaluation.get('failure_reason', '未知失败原因')
    
    @property
    def business_object(self) -> str:
        """获取业务对象"""
        return self.original_data.get('business_object', '未知')
    
    @property
    def rule_id(self) -> Optional[str]:
        """获取规则ID"""
        return self.original_data.get('rule_id') 