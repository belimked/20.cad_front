"""
失败模式检测器

分析失败的评估记录，识别失败模式并进行分类
"""

import json
import re
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import logging

from src.entity.evaluation.evaluation_record import EvaluationRecord
from src.entity.evaluation.failure_pattern import (
    FailurePattern, FailureAnalysis, FailureType, SeverityLevel
)


class FailurePatternDetector:
    """失败模式检测器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化失败模式检测器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.failure_config = config.get('analysis', {}).get('failure_pattern', {})
        self.logger = logging.getLogger(__name__)
        
        # 分类规则
        self.classification_rules = self.failure_config.get('classification_rules', {})
    
    def analyze_failures(self, 
                        failed_records: List[EvaluationRecord],
                        success_records: List[EvaluationRecord]) -> FailureAnalysis:
        """
        分析失败记录，生成失败分析结果
        
        Args:
            failed_records: 失败的评估记录
            success_records: 成功的评估记录
            
        Returns:
            失败分析结果
        """
        self.logger.info(f"开始分析失败模式，失败记录数: {len(failed_records)}")
        
        # 分类失败原因
        failure_patterns = self._classify_failure_reasons(failed_records)
        
        # 统计失败分布
        failure_by_business_object = self._analyze_failure_by_business_object(failed_records)
        failure_by_rule_id = self._analyze_failure_by_rule_id(failed_records)
        
        # 计算失败率
        total_records = len(failed_records) + len(success_records)
        failure_rate = len(failed_records) / total_records if total_records > 0 else 0.0
        
        # 找出最常见的失败原因
        most_common_failure = self._get_most_common_failure(failed_records)
        
        failure_analysis = FailureAnalysis(
            total_failed_count=len(failed_records),
            total_success_count=len(success_records),
            failure_rate=failure_rate,
            patterns=failure_patterns,
            most_common_failure=most_common_failure,
            failure_by_business_object=failure_by_business_object,
            failure_by_rule_id=failure_by_rule_id
        )
        
        self.logger.info(f"失败分析完成，识别出 {len(failure_patterns)} 种失败模式")
        return failure_analysis
    
    def _classify_failure_reasons(self, failed_records: List[EvaluationRecord]) -> List[FailurePattern]:
        """分类失败原因"""
        failure_reason_counts = Counter()
        failure_examples = defaultdict(list)
        
        for record in failed_records:
            # 优先使用详细分析，回退到失败原因
            reason = self._extract_detailed_reason(record)
            
            failure_reason_counts[reason] += 1
            
            # 保存示例（限制数量）- 增强示例信息
            if len(failure_examples[reason]) < self.failure_config.get('max_examples_per_pattern', 10):
                example = {
                    'id': record.id,
                    'question': record.question[:200] + '...' if len(record.question) > 200 else record.question,
                    'expected_answer': record.expected_answer[:200] + '...' if len(record.expected_answer) > 200 else record.expected_answer,
                    'actual_answer': record.actual_answer[:200] + '...' if len(record.actual_answer) > 200 else record.actual_answer,
                    'business_object': record.business_object,
                    'rule_id': record.rule_id,
                    'status': record.status,
                    'score': record.score
                }
                
                # 新增字段：规则名称和匹配关键词
                if hasattr(record, 'rule_name') and record.rule_name:
                    example['rule_name'] = record.rule_name
                if hasattr(record, 'matched_keyword') and record.matched_keyword:
                    example['matched_keyword'] = record.matched_keyword
                if hasattr(record, 'detailed_analysis') and record.detailed_analysis:
                    # 截取详细分析的前500个字符（增加长度以显示更多信息）
                    example['detailed_analysis'] = record.detailed_analysis[:500] + '...' if len(record.detailed_analysis) > 500 else record.detailed_analysis
                
                # 添加原始失败原因以供参考
                original_failure_reason = record.failure_reason or ""
                if original_failure_reason:
                    example['original_failure_reason'] = original_failure_reason
                
                failure_examples[reason].append(example)
        
        patterns = []
        total_failures = len(failed_records)
        
        for reason, count in failure_reason_counts.items():
            # 只有超过最小阈值的才形成模式
            if count >= self.failure_config.get('min_pattern_count', 5):
                pattern_type = self._classify_failure_type(reason)
                severity = self._determine_severity(pattern_type, count, total_failures)
                
                # 生成改进建议
                suggestions = self._generate_pattern_suggestions(pattern_type, reason)
                
                # 获取相关的规则ID和业务对象
                related_rule_ids = list(set([
                    str(record.rule_id) for record in failed_records 
                    if self._extract_detailed_reason(record) == reason and record.rule_id
                ]))
                related_business_objects = list(set([
                    record.business_object for record in failed_records 
                    if self._extract_detailed_reason(record) == reason
                ]))
                
                # 新增：获取相关的规则名称和关键词
                related_records = [r for r in failed_records if self._extract_detailed_reason(r) == reason]
                related_rule_names = list(set([
                    r.rule_name for r in related_records 
                    if hasattr(r, 'rule_name') and r.rule_name
                ]))
                related_keywords = list(set([
                    r.matched_keyword for r in related_records 
                    if hasattr(r, 'matched_keyword') and r.matched_keyword
                ]))
                
                pattern = FailurePattern(
                    pattern_type=pattern_type,
                    pattern_name=self._generate_pattern_name(reason),
                    description=self._generate_pattern_description(reason, count, total_failures, related_keywords),
                    count=count,
                    percentage=(count / total_failures) * 100,
                    severity=severity,
                    examples=failure_examples[reason],
                    improvement_suggestions=suggestions,
                    related_rule_ids=related_rule_ids,
                    related_business_objects=related_business_objects
                )
                
                # 添加新的相关信息到pattern对象（如果FailurePattern支持的话）
                if hasattr(pattern, 'related_rule_names'):
                    pattern.related_rule_names = related_rule_names
                if hasattr(pattern, 'related_keywords'):
                    pattern.related_keywords = related_keywords
                
                patterns.append(pattern)
        
        # 按数量排序
        patterns.sort(key=lambda x: x.count, reverse=True)
        return patterns
    
    def _extract_detailed_reason(self, record: EvaluationRecord) -> str:
        """从记录中提取详细的失败原因"""
        # 1. 如果有明确的失败原因，优先使用
        if record.failure_reason and record.failure_reason.strip():
            return record.failure_reason.strip()
        
        # 2. 从详细分析中提取关键错误信息
        if hasattr(record, 'detailed_analysis') and record.detailed_analysis:
            detailed_analysis = record.detailed_analysis
            
            # 解析低位错误模式
            if '低位错误:' in detailed_analysis:
                # 提取低位错误的具体类型
                import re
                low_error_match = re.search(r'低位错误:\s*(\d+)\(([^)]+)\)', detailed_analysis)
                if low_error_match:
                    error_code = low_error_match.group(1)
                    error_type = low_error_match.group(2)
                    
                    # 根据错误代码生成更具体的原因
                    if error_code == "8":
                        return f"字段值不一致错误 ({error_type})"
                    elif error_code == "2":
                        return f"字段内容格式错误 ({error_type})"
                    else:
                        return f"低级别匹配错误 (代码{error_code}: {error_type})"
            
            # 其他分析模式
            if '条件值不一致' in detailed_analysis:
                return "字段值不匹配"
            elif '条件数量不一致' in detailed_analysis:
                return "字段数量不一致"
            elif 'JSON解析失败' in detailed_analysis:
                return "JSON格式错误"
            elif '条件数量一致，内容不一致' in detailed_analysis:
                return "字段内容格式差异"
            elif '值变更' in detailed_analysis:
                return "字段值格式标准化问题"
            
            # 如果有分析但无法分类，返回前100个字符作为原因
            return detailed_analysis[:100] + ('...' if len(detailed_analysis) > 100 else '')
        
        # 3. 根据记录状态和分数推断原因
        if record.status == 'success':
            if record.score < 10:
                return f"部分匹配问题 (得分: {record.score}/10)"
            else:
                return "格式标准化问题"
        
        # 4. 默认原因
        return "未知原因"
    
    def _classify_failure_type(self, reason: str) -> FailureType:
        """根据失败原因分类失败类型"""
        reason_lower = reason.lower()
        
        # 根据配置的关键词进行分类
        for failure_type, rule in self.classification_rules.items():
            keywords = rule.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in reason_lower:
                    return FailureType(failure_type)
        
        # 使用正则表达式进一步分类
        if re.search(r'json.*格式', reason_lower) or 'json解析失败' in reason_lower:
            return FailureType.FORMAT_ERROR
        elif '属性不匹配' in reason_lower or '值不匹配' in reason_lower:
            return FailureType.JSON_MISMATCH
        elif '超时' in reason_lower or 'timeout' in reason_lower:
            return FailureType.TIMEOUT
        elif '解析' in reason_lower:
            return FailureType.PARSING_ERROR
        else:
            return FailureType.OTHER
    
    def _determine_severity(self, pattern_type: FailureType, count: int, total_failures: int) -> SeverityLevel:
        """确定严重程度"""
        percentage = (count / total_failures) * 100
        
        # 根据失败类型的基础严重程度
        base_severity = {
            FailureType.FORMAT_ERROR: SeverityLevel.CRITICAL,
            FailureType.JSON_MISMATCH: SeverityLevel.MAJOR,
            FailureType.TIMEOUT: SeverityLevel.MINOR,
            FailureType.PARSING_ERROR: SeverityLevel.MAJOR,
            FailureType.OTHER: SeverityLevel.MINOR
        }.get(pattern_type, SeverityLevel.MINOR)
        
        # 根据占比调整严重程度
        if percentage > 50:  # 超过50%的失败
            return SeverityLevel.CRITICAL
        elif percentage > 20:  # 超过20%的失败
            return SeverityLevel.MAJOR if base_severity != SeverityLevel.CRITICAL else SeverityLevel.CRITICAL
        else:
            return base_severity
    
    def _generate_pattern_name(self, reason: str) -> str:
        """生成模式名称"""
        # 简化失败原因作为模式名称
        if len(reason) > 50:
            return reason[:47] + "..."
        return reason
    
    def _generate_pattern_description(self, reason: str, count: int, total_failures: int, related_keywords: List[str] = None) -> str:
        """生成模式描述"""
        percentage = (count / total_failures) * 100
        base_desc = f"此类失败出现 {count} 次，占总失败数的 {percentage:.1f}%。原因：{reason}"
        
        if related_keywords:
            base_desc += f"。相关关键词：{', '.join(related_keywords[:5])}"
        
        return base_desc
    
    def _generate_pattern_suggestions(self, pattern_type: FailureType, reason: str) -> List[str]:
        """生成模式改进建议"""
        suggestions = []
        
        if pattern_type == FailureType.JSON_MISMATCH:
            suggestions.extend([
                "检查训练数据中字段值的一致性和标准化",
                "优化模型输出的字段值格式",
                "增加字段值的后处理和标准化逻辑"
            ])
        elif pattern_type == FailureType.FORMAT_ERROR:
            suggestions.extend([
                "强化JSON格式验证和自动修复机制",
                "优化模型提示词以强调JSON格式要求",
                "增加输出后的格式检查和修正"
            ])
        elif pattern_type == FailureType.TIMEOUT:
            suggestions.extend([
                "优化模型推理性能",
                "增加超时时间限制",
                "实现异步处理机制"
            ])
        elif pattern_type == FailureType.PARSING_ERROR:
            suggestions.extend([
                "改进输入数据的预处理逻辑",
                "增加输入验证和清理",
                "优化解析算法的容错性"
            ])
        else:
            suggestions.append("需要进一步分析具体失败原因以制定针对性改进措施")
        
        return suggestions
    
    def _analyze_failure_by_business_object(self, failed_records: List[EvaluationRecord]) -> Dict[str, int]:
        """按业务对象分析失败"""
        failure_counts = Counter()
        for record in failed_records:
            failure_counts[record.business_object] += 1
        return dict(failure_counts)
    
    def _analyze_failure_by_rule_id(self, failed_records: List[EvaluationRecord]) -> Dict[str, int]:
        """按规则ID分析失败"""
        failure_counts = Counter()
        for record in failed_records:
            if record.rule_id:
                failure_counts[str(record.rule_id)] += 1
        return dict(failure_counts)
    
    def _get_most_common_failure(self, failed_records: List[EvaluationRecord]) -> str:
        """获取最常见的失败原因"""
        if not failed_records:
            return "无失败记录"
        
        failure_reasons = [record.failure_reason or "未知原因" for record in failed_records]
        most_common = Counter(failure_reasons).most_common(1)
        
        if most_common:
            return most_common[0][0]
        else:
            return "未知原因"
    
    def analyze_json_differences(self, expected: str, actual: str) -> Dict[str, Any]:
        """
        深度分析JSON之间的差异
        
        Args:
            expected: 期望的JSON字符串
            actual: 实际的JSON字符串
            
        Returns:
            差异分析结果
        """
        try:
            expected_obj = json.loads(expected)
            actual_obj = json.loads(actual)
            
            return self._compare_json_objects(expected_obj, actual_obj)
        
        except json.JSONDecodeError as e:
            return {
                'error': 'JSON解析错误',
                'details': str(e),
                'analysis': '无法进行差异分析，因为JSON格式无效'
            }
    
    def _compare_json_objects(self, expected: Any, actual: Any, path: str = "") -> Dict[str, Any]:
        """递归比较JSON对象"""
        differences = {
            'missing_keys': [],
            'extra_keys': [],
            'value_differences': [],
            'type_differences': []
        }
        
        if isinstance(expected, dict) and isinstance(actual, dict):
            # 比较字典
            expected_keys = set(expected.keys())
            actual_keys = set(actual.keys())
            
            # 缺失的键
            missing = expected_keys - actual_keys
            differences['missing_keys'].extend([f"{path}.{key}" if path else key for key in missing])
            
            # 多余的键
            extra = actual_keys - expected_keys
            differences['extra_keys'].extend([f"{path}.{key}" if path else key for key in extra])
            
            # 比较共同的键
            common_keys = expected_keys & actual_keys
            for key in common_keys:
                sub_path = f"{path}.{key}" if path else key
                sub_diff = self._compare_json_objects(expected[key], actual[key], sub_path)
                
                # 合并子差异
                for diff_type, diff_list in sub_diff.items():
                    differences[diff_type].extend(diff_list)
        
        elif type(expected) != type(actual):
            # 类型不匹配
            differences['type_differences'].append({
                'path': path,
                'expected_type': type(expected).__name__,
                'actual_type': type(actual).__name__
            })
        
        elif expected != actual:
            # 值不匹配
            differences['value_differences'].append({
                'path': path,
                'expected': expected,
                'actual': actual
            })
        
        return differences 