#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
训练数据优化器

针对已有训练数据进行问题精简和意图分析对象JSON转换
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

from src.service.common.question_reduction import advanced_simplify_question, evaluate_reduction_quality


class TrainingDataOptimizer:
    """训练数据优化器"""
    
    def __init__(self):
        """初始化优化器"""
        self.logger = self._setup_logger()
        self.processed_count = 0
        self.optimization_stats = {
            "total_processed": 0,
            "successfully_optimized": 0,
            "reduction_stats": [],
            "quality_stats": [],
            "errors": []
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def optimize_training_data(self, 
                             input_file: str, 
                             output_file: Optional[str] = None,
                             reduction_level: str = "advanced",
                             enable_question_reduction: bool = True,
                             enable_answer_optimization: bool = True) -> Dict[str, Any]:
        """
        优化训练数据
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则自动生成
            reduction_level: 缩减级别 (basic/advanced/aggressive)
            enable_question_reduction: 是否启用问题精简
            enable_answer_optimization: 是否启用回答优化
            
        Returns:
            优化结果统计
        """
        self.logger.info(f"开始优化训练数据: {input_file}")
        
        # 读取原始数据
        original_data = self._load_jsonl_file(input_file)
        if not original_data:
            raise ValueError(f"无法读取文件或文件为空: {input_file}")
        
        # 处理数据
        optimized_data = []
        for i, record in enumerate(original_data):
            try:
                optimized_record = self._optimize_single_record(
                    record, 
                    reduction_level=reduction_level,
                    enable_question_reduction=enable_question_reduction,
                    enable_answer_optimization=enable_answer_optimization
                )
                optimized_data.append(optimized_record)
                self.optimization_stats["successfully_optimized"] += 1
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"已处理 {i + 1}/{len(original_data)} 条记录")
                    
            except Exception as e:
                self.logger.error(f"处理第 {i + 1} 条记录时出错: {e}")
                self.optimization_stats["errors"].append({
                    "record_index": i + 1,
                    "error": str(e),
                    "original_record": record
                })
        
        self.optimization_stats["total_processed"] = len(original_data)
        
        # 生成输出文件路径
        if output_file is None:
            input_path = Path(input_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(input_path.parent / f"optimized_{input_path.stem}_{timestamp}.jsonl")
        
        # 保存优化后的数据
        self._save_jsonl_file(optimized_data, output_file)
        
        # 生成统计报告
        stats_report = self._generate_optimization_report()
        
        self.logger.info(f"优化完成，输出文件: {output_file}")
        self.logger.info(f"处理统计: {self.optimization_stats['successfully_optimized']}/{self.optimization_stats['total_processed']} 条记录成功优化")
        
        return {
            "input_file": input_file,
            "output_file": output_file,
            "optimization_stats": self.optimization_stats,
            "stats_report": stats_report
        }
    
    def _optimize_single_record(self, 
                               record: Dict[str, Any], 
                               reduction_level: str = "advanced",
                               enable_question_reduction: bool = True,
                               enable_answer_optimization: bool = True) -> Dict[str, Any]:
        """优化单条记录"""
        if "messages" not in record or len(record["messages"]) < 2:
            raise ValueError("记录格式不正确，缺少messages字段或消息数量不足")
        
        user_message = record["messages"][0]
        assistant_message = record["messages"][1]
        
        if user_message.get("role") != "user" or assistant_message.get("role") != "assistant":
            raise ValueError("消息角色不正确")
        
        original_question = user_message.get("content", "")
        original_answer = assistant_message.get("content", "")
        
        # 优化问题
        optimized_question = original_question
        reduction_stats = None

        if enable_question_reduction and original_question:
            try:
                # 预处理：如果问题包含JSON结构，先清理
                cleaned_question = self._preprocess_question(original_question)

                reduction_result = advanced_simplify_question(
                    cleaned_question,
                    reduction_level=reduction_level,
                    return_stats=True
                )
                optimized_question = reduction_result["result"]
                reduction_stats = reduction_result["stats"]
                
                # 评估缩减质量
                quality_result = evaluate_reduction_quality(original_question, optimized_question)
                
                # 记录统计信息
                self.optimization_stats["reduction_stats"].append({
                    "original_length": len(original_question),
                    "reduced_length": len(optimized_question),
                    "reduction_rate": reduction_stats["reduction_rate"],
                    "applied_rules": reduction_stats["applied_rules"]
                })
                
                self.optimization_stats["quality_stats"].append(quality_result)
                
            except Exception as e:
                self.logger.warning(f"问题缩减失败: {e}")
                optimized_question = original_question
        
        # 优化回答（转换为意图分析对象JSON）
        optimized_answer = original_answer
        
        if enable_answer_optimization and original_answer:
            try:
                optimized_answer = self._optimize_answer_json(original_answer)
            except Exception as e:
                self.logger.warning(f"回答优化失败: {e}")
                optimized_answer = original_answer
        
        # 构建优化后的记录
        optimized_record = {
            "messages": [
                {
                    "role": "user",
                    "content": optimized_question
                },
                {
                    "role": "assistant", 
                    "content": optimized_answer
                }
            ]
        }
        
        # 添加优化元数据
        if reduction_stats:
            optimized_record["optimization_metadata"] = {
                "question_reduction": {
                    "original_question": original_question,
                    "reduction_level": reduction_level,
                    "reduction_stats": reduction_stats
                },
                "optimization_timestamp": datetime.now().isoformat()
            }
        
        return optimized_record

    def _preprocess_question(self, question: str) -> str:
        """预处理问题文本，清理复杂的JSON结构"""
        if not question:
            return question

        # 检查是否包含JSON结构
        if "{'name':" in question or '{"name":' in question:
            # 尝试提取有用信息
            import re

            # 提取姓名
            name_pattern = r"'name'\s*:\s*'([^']+)'"
            names = re.findall(name_pattern, question)

            # 提取代码
            code_pattern = r"'code'\s*:\s*'([^']+)'"
            codes = re.findall(code_pattern, question)

            # 提取实验编号
            exp_pattern = r"实验\d+"
            experiments = re.findall(exp_pattern, question)

            # 重构问题
            parts = []

            # 添加有效的姓名和代码
            for name in names:
                if name and name not in ['将', '中移除', '']:
                    parts.append(name)

            for code in codes:
                if code and code.strip():
                    parts.append(code)

            # 添加实验编号
            parts.extend(experiments)

            # 检查操作词
            if '移除' in question:
                parts.append('中移除')
            elif '撤销' in question:
                parts.append('撤销')
            elif '删除' in question:
                parts.append('删除')

            if parts:
                return '，'.join(parts)

        return question

    def _optimize_answer_json(self, original_answer: str) -> str:
        """优化回答JSON，移除无用字段，保留核心意图信息"""
        try:
            # 解析原始JSON
            answer_data = json.loads(original_answer)
            
            # 定义核心字段（保留有意义的字段）
            core_fields = {
                "操作", "对象", "人员姓名", "人员项目", "人员全部项目",
                "项目", "供应商", "材料类型", "材料编号", "材料工程属性",
                "对象金额", "对象状态", "对象提交时间", "对象下单时间",
                "对象附加费用"  # 🎯 新增：附加费用字段
            }
            
            # 创建优化后的JSON对象
            optimized_data = {}
            
            for key, value in answer_data.items():
                if key in core_fields:
                    # 保留核心字段
                    if value != "无" and value != "" and value is not None:
                        # 进一步优化值
                        optimized_value = self._optimize_field_value(key, value)
                        if optimized_value:
                            optimized_data[key] = optimized_value
                    elif key in ["操作", "对象"]:
                        # 操作和对象字段即使为"无"也保留
                        optimized_data[key] = value
            
            # 确保必要字段存在
            if "操作" not in optimized_data:
                optimized_data["操作"] = answer_data.get("操作", "未知")
            if "对象" not in optimized_data:
                optimized_data["对象"] = answer_data.get("对象", "未知")
            
            return json.dumps(optimized_data, ensure_ascii=False, separators=(',', ':'))
            
        except json.JSONDecodeError:
            # 如果不是有效JSON，返回原始内容
            return original_answer
        except Exception as e:
            self.logger.warning(f"JSON优化失败: {e}")
            return original_answer
    
    def _optimize_field_value(self, field_name: str, value: Any) -> Any:
        """优化字段值"""
        if isinstance(value, list):
            # 处理列表类型
            if field_name == "人员姓名":
                # 优化人员姓名列表，移除空值
                optimized_list = []
                for item in value:
                    if isinstance(item, dict):
                        # 清理姓名和编号
                        name = item.get("name", "").strip()
                        code = item.get("code", "").strip()
                        if name or code:
                            clean_item = {}
                            if name:
                                clean_item["name"] = name
                            if code:
                                clean_item["code"] = code
                            optimized_list.append(clean_item)
                    elif isinstance(item, str) and item.strip():
                        optimized_list.append(item.strip())
                return optimized_list if optimized_list else None
            
            elif field_name == "人员项目":
                # 优化项目列表
                optimized_list = []
                for item in value:
                    if isinstance(item, dict):
                        name = item.get("name", "").strip()
                        if name:
                            optimized_list.append(name)
                    elif isinstance(item, str) and item.strip():
                        optimized_list.append(item.strip())
                return optimized_list if optimized_list else None
            
            else:
                # 其他列表类型，移除空值
                return [item for item in value if item and str(item).strip()] or None
        
        elif isinstance(value, str):
            # 处理字符串类型
            cleaned_value = value.strip()
            return cleaned_value if cleaned_value and cleaned_value != "无" else None
        
        return value
    
    def _load_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """加载JSONL文件"""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            self.logger.error(f"第 {line_num} 行JSON解析失败: {e}")
            return data
        except Exception as e:
            self.logger.error(f"读取文件失败: {e}")
            return []
    
    def _save_jsonl_file(self, data: List[Dict[str, Any]], file_path: str):
        """保存JSONL文件"""
        try:
            # 确保输出目录存在
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for record in data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")
            raise
    
    def _generate_optimization_report(self) -> str:
        """生成优化报告"""
        stats = self.optimization_stats
        
        # 计算平均值
        if stats["reduction_stats"]:
            avg_reduction_rate = sum(s["reduction_rate"] for s in stats["reduction_stats"]) / len(stats["reduction_stats"])
            avg_original_length = sum(s["original_length"] for s in stats["reduction_stats"]) / len(stats["reduction_stats"])
            avg_reduced_length = sum(s["reduced_length"] for s in stats["reduction_stats"]) / len(stats["reduction_stats"])
        else:
            avg_reduction_rate = avg_original_length = avg_reduced_length = 0
        
        if stats["quality_stats"]:
            avg_quality = sum(s["overall_quality"] for s in stats["quality_stats"]) / len(stats["quality_stats"])
        else:
            avg_quality = 0
        
        # 统计应用的规则
        rule_counter = {}
        for stat in stats["reduction_stats"]:
            for rule in stat["applied_rules"]:
                rule_counter[rule] = rule_counter.get(rule, 0) + 1
        
        report = f"""
# 训练数据优化报告

## 处理统计
- **总记录数**: {stats['total_processed']}
- **成功优化**: {stats['successfully_optimized']}
- **失败记录**: {len(stats['errors'])}
- **成功率**: {stats['successfully_optimized']/stats['total_processed']*100:.1f}%

## 问题缩减效果
- **平均缩减率**: {avg_reduction_rate:.1%}
- **平均原始长度**: {avg_original_length:.1f} 字符
- **平均缩减长度**: {avg_reduced_length:.1f} 字符
- **平均质量评分**: {avg_quality:.3f}

## 应用规则统计
{chr(10).join([f"- **{rule}**: {count}次" for rule, count in sorted(rule_counter.items(), key=lambda x: x[1], reverse=True)])}

## 错误记录
{chr(10).join([f"- 第{err['record_index']}条: {err['error']}" for err in stats['errors'][:5]])}
{f"... 还有{len(stats['errors'])-5}个错误" if len(stats['errors']) > 5 else ""}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report


def main():
    """主函数，用于命令行调用"""
    import argparse
    
    parser = argparse.ArgumentParser(description="训练数据优化器")
    parser.add_argument("input_file", help="输入JSONL文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-l", "--level", choices=["basic", "advanced", "aggressive"], 
                       default="advanced", help="缩减级别")
    parser.add_argument("--no-question-reduction", action="store_true", 
                       help="禁用问题精简")
    parser.add_argument("--no-answer-optimization", action="store_true", 
                       help="禁用回答优化")
    
    args = parser.parse_args()
    
    optimizer = TrainingDataOptimizer()
    
    result = optimizer.optimize_training_data(
        input_file=args.input_file,
        output_file=args.output,
        reduction_level=args.level,
        enable_question_reduction=not args.no_question_reduction,
        enable_answer_optimization=not args.no_answer_optimization
    )
    
    print("优化完成！")
    print(f"输出文件: {result['output_file']}")
    print("\n" + result['stats_report'])


if __name__ == "__main__":
    main()
