"""
失败模式数据结构

定义失败模式分析的数据模型
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from enum import Enum


class FailureType(Enum):
    """失败类型枚举"""
    JSON_MISMATCH = "json_mismatch"  # JSON属性不匹配
    FORMAT_ERROR = "format_error"    # JSON格式错误
    TIMEOUT = "timeout"              # 处理超时
    PARSING_ERROR = "parsing_error"  # 解析错误
    OTHER = "other"                  # 其他类型


class SeverityLevel(Enum):
    """严重程度枚举"""
    CRITICAL = "critical"  # 严重
    MAJOR = "major"        # 重要
    MINOR = "minor"        # 轻微


@dataclass
class FailurePattern:
    """失败模式数据结构"""
    
    # 基本信息
    pattern_type: FailureType
    pattern_name: str
    description: str
    
    # 统计信息
    count: int
    percentage: float
    
    # 严重程度
    severity: SeverityLevel
    
    # 示例数据
    examples: List[Dict[str, Any]]
    
    # 改进建议
    improvement_suggestions: List[str]
    
    # 相关规则ID
    related_rule_ids: List[str]
    
    # 相关业务对象
    related_business_objects: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'pattern_type': self.pattern_type.value,
            'pattern_name': self.pattern_name,
            'description': self.description,
            'count': self.count,
            'percentage': self.percentage,
            'severity': self.severity.value,
            'examples': self.examples,
            'improvement_suggestions': self.improvement_suggestions,
            'related_rule_ids': self.related_rule_ids,
            'related_business_objects': self.related_business_objects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FailurePattern':
        """从字典创建失败模式"""
        return cls(
            pattern_type=FailureType(data.get('pattern_type', 'other')),
            pattern_name=data.get('pattern_name', ''),
            description=data.get('description', ''),
            count=data.get('count', 0),
            percentage=data.get('percentage', 0.0),
            severity=SeverityLevel(data.get('severity', 'minor')),
            examples=data.get('examples', []),
            improvement_suggestions=data.get('improvement_suggestions', []),
            related_rule_ids=data.get('related_rule_ids', []),
            related_business_objects=data.get('related_business_objects', [])
        )


@dataclass 
class FailureAnalysis:
    """失败分析结果"""
    
    # 总体统计
    total_failed_count: int
    total_success_count: int
    failure_rate: float
    
    # 失败模式列表
    patterns: List[FailurePattern]
    
    # 最常见的失败原因
    most_common_failure: str
    
    # 按业务对象分组的失败统计
    failure_by_business_object: Dict[str, int]
    
    # 按规则ID分组的失败统计  
    failure_by_rule_id: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_failed_count': self.total_failed_count,
            'total_success_count': self.total_success_count,
            'failure_rate': self.failure_rate,
            'patterns': [pattern.to_dict() for pattern in self.patterns],
            'most_common_failure': self.most_common_failure,
            'failure_by_business_object': self.failure_by_business_object,
            'failure_by_rule_id': self.failure_by_rule_id
        }
    
    def get_critical_patterns(self) -> List[FailurePattern]:
        """获取严重级别的失败模式"""
        return [p for p in self.patterns if p.severity == SeverityLevel.CRITICAL]
    
    def get_top_failure_patterns(self, limit: int = 5) -> List[FailurePattern]:
        """获取前N个最常见的失败模式"""
        sorted_patterns = sorted(self.patterns, key=lambda x: x.count, reverse=True)
        return sorted_patterns[:limit] 