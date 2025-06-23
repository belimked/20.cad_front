"""
评估记录数据结构

定义单条评估记录的数据模型 - 支持新的增强格式
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, Union


@dataclass
class EvaluationDetail:
    """评估详情结构"""
    status: str
    score: int
    json_valid: bool
    comparison_result: Optional[Any] = None
    failure_reason: str = ""
    analysis: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationDetail':
        return cls(
            status=data.get('status', 'unknown'),
            score=data.get('score', 0),
            json_valid=data.get('json_valid', False),
            comparison_result=data.get('comparison_result'),
            failure_reason=data.get('failure_reason', ''),
            analysis=data.get('analysis', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'score': self.score,
            'json_valid': self.json_valid,
            'comparison_result': self.comparison_result,
            'failure_reason': self.failure_reason,
            'analysis': self.analysis
        }


@dataclass
class PromptInfo:
    """提示词信息结构"""
    prompt_file: str = ""
    matched_keyword: str = ""
    prompt_content: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptInfo':
        return cls(
            prompt_file=data.get('prompt_file', ''),
            matched_keyword=data.get('matched_keyword', ''),
            prompt_content=data.get('prompt_content', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt_file': self.prompt_file,
            'matched_keyword': self.matched_keyword,
            'prompt_content': self.prompt_content
        }


@dataclass
class OriginalData:
    """原始数据结构"""
    business_object: str
    rule_id: Union[int, str]
    rule_name: str = ""
    question: Dict[str, Any] = field(default_factory=dict)
    answer: Dict[str, Any] = field(default_factory=dict)
    codebase: str = ""
    formatted_question: str = ""
    formatted_answer: str = ""
    combo_value: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OriginalData':
        return cls(
            business_object=data.get('business_object', ''),
            rule_id=data.get('rule_id', ''),
            rule_name=data.get('rule_name', ''),
            question=data.get('question', {}),
            answer=data.get('answer', {}),
            codebase=data.get('codebase', ''),
            formatted_question=data.get('formatted_question', ''),
            formatted_answer=data.get('formatted_answer', ''),
            combo_value=data.get('combo_value', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'business_object': self.business_object,
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'question': self.question,
            'answer': self.answer,
            'codebase': self.codebase,
            'formatted_question': self.formatted_question,
            'formatted_answer': self.formatted_answer,
            'combo_value': self.combo_value
        }


@dataclass
class EvaluationRecord:
    """单条评估记录数据结构 - 支持新增强格式"""
    
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
    
    # 评估结果 - 支持新的结构化格式
    score: int
    evaluation: Union[EvaluationDetail, Dict[str, Any]]
    
    # 提示词信息 - 支持新的增强格式
    prompt_info: Union[PromptInfo, Dict[str, Any]]
    
    # 原始数据信息 - 支持新的复杂结构
    original_data: Union[OriginalData, Dict[str, Any]]
    
    # 来源文件
    source_file: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationRecord':
        """从字典创建评估记录 - 支持新旧格式"""
        
        # 处理时间戳
        timestamp_str = data.get('timestamp', '')
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # 处理evaluation字段 - 支持新的结构化格式
        evaluation_data = data.get('evaluation', {})
        if isinstance(evaluation_data, dict) and 'json_valid' in evaluation_data:
            # 新格式：结构化evaluation
            evaluation = EvaluationDetail.from_dict(evaluation_data)
        else:
            # 兼容旧格式：直接使用字典或转换
            if isinstance(evaluation_data, dict):
                evaluation = evaluation_data
            else:
                evaluation = {}
        
        # 处理prompt_info字段 - 支持新的增强格式
        prompt_data = data.get('prompt_info', {})
        if isinstance(prompt_data, dict) and 'matched_keyword' in prompt_data:
            # 新格式：包含matched_keyword
            prompt_info = PromptInfo.from_dict(prompt_data)
        else:
            # 兼容旧格式
            if isinstance(prompt_data, dict):
                prompt_info = prompt_data
            else:
                prompt_info = {}
        
        # 处理original_data字段 - 支持新的复杂结构
        original_data_dict = data.get('original_data', {})
        if isinstance(original_data_dict, dict) and 'question' in original_data_dict and isinstance(original_data_dict['question'], dict):
            # 新格式：复杂嵌套结构
            original_data = OriginalData.from_dict(original_data_dict)
        else:
            # 兼容旧格式
            if isinstance(original_data_dict, dict):
                original_data = original_data_dict
            else:
                original_data = {}
        
        return cls(
            id=data.get('id', 0),
            question=data.get('question', ''),
            expected_answer=data.get('expected_answer', ''),
            actual_answer=data.get('actual_answer', ''),
            raw_answer=data.get('raw_answer', ''),
            processing_time=data.get('processing_time', 0.0),
            timestamp=timestamp,
            status=data.get('status', 'unknown'),
            score=data.get('score', 0),
            evaluation=evaluation,
            prompt_info=prompt_info,
            original_data=original_data,
            source_file=data.get('source_file', '')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        # 处理evaluation字段
        if isinstance(self.evaluation, EvaluationDetail):
            evaluation_dict = self.evaluation.to_dict()
        else:
            evaluation_dict = self.evaluation if isinstance(self.evaluation, dict) else {}
        
        # 处理prompt_info字段
        if isinstance(self.prompt_info, PromptInfo):
            prompt_info_dict = self.prompt_info.to_dict()
        else:
            prompt_info_dict = self.prompt_info if isinstance(self.prompt_info, dict) else {}
        
        # 处理original_data字段
        if isinstance(self.original_data, OriginalData):
            original_data_dict = self.original_data.to_dict()
        else:
            original_data_dict = self.original_data if isinstance(self.original_data, dict) else {}
        
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
            'evaluation': evaluation_dict,
            'prompt_info': prompt_info_dict,
            'original_data': original_data_dict,
            'source_file': self.source_file
        }
    
    @property
    def is_successful(self) -> bool:
        """是否评估成功"""
        return self.status == 'success'
    
    @property
    def failure_reason(self) -> Optional[str]:
        """获取失败原因 - 支持新的结构化格式"""
        if self.is_successful:
            return None
        
        # 从新的结构化evaluation中获取失败原因
        if isinstance(self.evaluation, EvaluationDetail):
            return self.evaluation.failure_reason or '未知失败原因'
        elif isinstance(self.evaluation, dict):
            return self.evaluation.get('failure_reason', '未知失败原因')
        else:
            return '未知失败原因'
    
    @property
    def business_object(self) -> str:
        """获取业务对象"""
        if isinstance(self.original_data, OriginalData):
            return self.original_data.business_object
        elif isinstance(self.original_data, dict):
            return self.original_data.get('business_object', '未知')
        else:
            return '未知'
    
    @property
    def rule_id(self) -> Optional[Union[str, int]]:
        """获取规则ID"""
        if isinstance(self.original_data, OriginalData):
            return self.original_data.rule_id
        elif isinstance(self.original_data, dict):
            return self.original_data.get('rule_id')
        else:
            return None
    
    @property
    def rule_name(self) -> str:
        """获取规则名称 - 新增属性"""
        if isinstance(self.original_data, OriginalData):
            return self.original_data.rule_name
        elif isinstance(self.original_data, dict):
            return self.original_data.get('rule_name', '')
        else:
            return ''
    
    @property
    def matched_keyword(self) -> str:
        """获取匹配的关键词 - 新增属性"""
        if isinstance(self.prompt_info, PromptInfo):
            return self.prompt_info.matched_keyword
        elif isinstance(self.prompt_info, dict):
            return self.prompt_info.get('matched_keyword', '')
        else:
            return ''
    
    @property
    def json_valid(self) -> bool:
        """判断JSON是否有效 - 新增属性"""
        if isinstance(self.evaluation, EvaluationDetail):
            return self.evaluation.json_valid
        elif isinstance(self.evaluation, dict):
            return self.evaluation.get('json_valid', False)
        else:
            return False
    
    @property
    def detailed_analysis(self) -> str:
        """获取详细分析 - 新增属性"""
        if isinstance(self.evaluation, EvaluationDetail):
            return self.evaluation.analysis
        elif isinstance(self.evaluation, dict):
            return self.evaluation.get('analysis', '')
        else:
            return ''
    
    @property
    def structured_question(self) -> Dict[str, Any]:
        """获取结构化问题 - 新增属性"""
        if isinstance(self.original_data, OriginalData):
            return self.original_data.question if isinstance(self.original_data.question, dict) else {}
        elif isinstance(self.original_data, dict):
            question_data = self.original_data.get('question', {})
            return question_data if isinstance(question_data, dict) else {}
        else:
            return {}
    
    @property
    def structured_answer(self) -> Dict[str, Any]:
        """获取结构化答案 - 新增属性"""
        if isinstance(self.original_data, OriginalData):
            return self.original_data.answer if isinstance(self.original_data.answer, dict) else {}
        elif isinstance(self.original_data, dict):
            answer_data = self.original_data.get('answer', {})
            return answer_data if isinstance(answer_data, dict) else {}
        else:
            return {} 