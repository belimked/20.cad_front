#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
意图分析训练数据优化器

第一部分：使用已开发的问题缩减策略优化问题
第二部分：从原始回答中提取关键信息作为意图分析对象
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.service.common.question_reduction import advanced_simplify_question, evaluate_reduction_quality


class IntentAnalysisOptimizer:
    """意图分析训练数据优化器"""
    
    def __init__(self):
        """初始化优化器"""
        self.logger = self._setup_logger()
        self.stats = {
            "total_processed": 0,
            "successfully_optimized": 0,
            "question_reductions": [],
            "intent_extractions": 0,
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
                             messages_only: bool = False) -> Dict[str, Any]:
        """
        优化训练数据

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则自动生成
            reduction_level: 问题缩减级别 (basic/advanced/aggressive)
            messages_only: 是否只生成messages结构，移除优化元数据

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
                optimized_record = self._optimize_single_record(record, reduction_level, messages_only)
                optimized_data.append(optimized_record)
                self.stats["successfully_optimized"] += 1
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"已处理 {i + 1}/{len(original_data)} 条记录")
                    
            except Exception as e:
                self.logger.error(f"处理第 {i + 1} 条记录时出错: {e}")
                self.stats["errors"].append({
                    "record_index": i + 1,
                    "error": str(e),
                    "original_record": record
                })
        
        self.stats["total_processed"] = len(original_data)
        
        # 生成输出文件路径
        if output_file is None:
            input_path = Path(input_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if messages_only:
                output_file = str(input_path.parent / f"intent_optimized_messages_only_{input_path.stem}_{timestamp}.jsonl")
            else:
                output_file = str(input_path.parent / f"intent_optimized_{input_path.stem}_{timestamp}.jsonl")
        
        # 保存优化后的数据
        self._save_jsonl_file(optimized_data, output_file)
        
        # 生成报告
        report = self._generate_report()
        
        self.logger.info(f"优化完成，输出文件: {output_file}")
        self.logger.info(f"处理统计: {self.stats['successfully_optimized']}/{self.stats['total_processed']} 条记录成功优化")
        
        return {
            "input_file": input_file,
            "output_file": output_file,
            "stats": self.stats,
            "report": report
        }
    
    def _optimize_single_record(self, record: Dict[str, Any], reduction_level: str, messages_only: bool = False) -> Dict[str, Any]:
        """优化单条记录"""
        if "messages" not in record or len(record["messages"]) < 2:
            raise ValueError("记录格式不正确，缺少messages字段或消息数量不足")
        
        user_message = record["messages"][0]
        assistant_message = record["messages"][1]
        
        if user_message.get("role") != "user" or assistant_message.get("role") != "assistant":
            raise ValueError("消息角色不正确")
        
        original_question = user_message.get("content", "")
        original_answer = assistant_message.get("content", "")
        
        # 第一部分：使用问题缩减策略优化问题
        optimized_question = original_question
        reduction_stats = None
        
        if original_question:
            try:
                reduction_result = advanced_simplify_question(
                    original_question, 
                    reduction_level=reduction_level, 
                    return_stats=True
                )
                optimized_question = reduction_result["result"]
                reduction_stats = reduction_result["stats"]
                
                # 评估缩减质量
                quality_result = evaluate_reduction_quality(original_question, optimized_question)
                
                # 记录统计信息
                self.stats["question_reductions"].append({
                    "original_length": len(original_question),
                    "reduced_length": len(optimized_question),
                    "reduction_rate": reduction_stats["reduction_rate"],
                    "applied_rules": reduction_stats["applied_rules"],
                    "quality_score": quality_result["overall_quality"]
                })
                
            except Exception as e:
                self.logger.warning(f"问题缩减失败: {e}")
                optimized_question = original_question
        
        # 第二部分：从原始回答中提取关键信息作为意图分析对象
        intent_analysis = self._extract_intent_analysis(original_answer)
        if intent_analysis:
            self.stats["intent_extractions"] += 1
        
        # 构建优化后的记录
        optimized_record = {
            "messages": [
                {
                    "role": "user",
                    "content": optimized_question
                },
                {
                    "role": "assistant", 
                    "content": json.dumps(intent_analysis, ensure_ascii=False, separators=(',', ':'))
                }
            ]
        }
        
        # 添加优化元数据（仅在非messages-only模式下）
        if not messages_only and reduction_stats:
            optimized_record["optimization_metadata"] = {
                "question_reduction": {
                    "original_question": original_question,
                    "reduction_level": reduction_level,
                    "reduction_stats": reduction_stats
                },
                "intent_extraction": {
                    "extracted_fields": list(intent_analysis.keys()) if intent_analysis else [],
                    "extraction_method": "rule_based"
                },
                "optimization_timestamp": datetime.now().isoformat()
            }
        
        return optimized_record
    
    def _extract_intent_analysis(self, original_answer: str) -> Dict[str, Any]:
        """从原始回答中提取关键信息作为意图分析对象"""
        try:
            # 解析原始JSON回答
            answer_data = json.loads(original_answer)

            # 定义意图分析的关键字段映射（中文->英文）
            intent_fields = {
                # 核心操作信息
                "操作": "businessOpt",
                "对象": "businessObject",

                # 项目相关
                "项目": "businessProject",
                "人员项目": "businessProject",
                "人员全部项目": "businessProject",

                # 供应商相关
                "供应商": "businessSupplies",

                # 人员相关
                "人员姓名": "businessPerson",
                "人员工号": "businessPerson",

                # 材料相关
                "材料类型": "businessMaterial",
                "材料编号": "businessMaterial",
                "材料工程属性": "businessMaterial",

                # 状态和时间
                "对象状态": "businessStatus",
                "对象提交时间": "businessTime",
                "对象下单时间": "businessTime",

                # 金额相关
                "对象金额": "businessAmount"
            }
            
            # 提取意图分析对象
            intent_analysis = {}

            # 1. 操作类型（必须字段）
            operation = answer_data.get("操作", "")
            if operation and operation != "无":
                intent_analysis["businessOpt"] = operation

            # 2. 操作对象（必须字段）
            target = answer_data.get("对象", "")
            if target and target != "无":
                intent_analysis["businessObject"] = target
            
            # 3. 提取其他关键信息
            extracted_info = {}

            for field, english_field in intent_fields.items():
                if field in answer_data:
                    value = answer_data[field]
                    if self._is_meaningful_value(value):
                        if english_field not in extracted_info:
                            extracted_info[english_field] = []

                        # 处理不同类型的值
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    # 提取字典中的有效信息
                                    dict_info = self._extract_dict_info(item)
                                    if dict_info:
                                        extracted_info[english_field].extend(dict_info)
                                elif self._is_meaningful_value(item):
                                    extracted_info[english_field].append(str(item))
                        elif isinstance(value, str):
                            extracted_info[english_field].append(value)
                        else:
                            extracted_info[english_field].append(str(value))

            # 4. 整理提取的信息
            for english_field, values in extracted_info.items():
                if values:
                    # 去重并清理
                    unique_values = list(set(values))
                    if len(unique_values) == 1:
                        intent_analysis[english_field] = unique_values[0]
                    else:
                        intent_analysis[english_field] = unique_values
            
            # 5. 确保至少有操作信息
            if not intent_analysis.get("businessOpt"):
                intent_analysis["businessOpt"] = "未知"

            # 6. 生成完整问题结构（fullQuestion）
            intent_analysis["fullQuestion"] = self._generate_full_question(intent_analysis, answer_data, original_answer)

            return intent_analysis
            
        except json.JSONDecodeError:
            # 如果不是有效JSON，尝试文本解析
            return self._extract_intent_from_text(original_answer)
        except Exception as e:
            self.logger.warning(f"意图提取失败: {e}")
            return {"操作": "未知", "对象": "未知"}
    
    def _extract_dict_info(self, item_dict: Dict[str, Any]) -> List[str]:
        """从字典中提取有效信息"""
        info = []
        for key, value in item_dict.items():
            if self._is_meaningful_value(value):
                if key in ["name", "姓名"]:
                    info.append(f"姓名:{value}")
                elif key in ["code", "编号", "工号"]:
                    info.append(f"编号:{value}")
                else:
                    info.append(f"{key}:{value}")
        return info
    
    def _extract_intent_from_text(self, text: str) -> Dict[str, Any]:
        """从文本中提取意图信息（备用方法）"""
        intent = {"操作": "未知", "对象": "未知"}
        
        # 简单的关键词匹配
        if "删除" in text or "移除" in text:
            intent["操作"] = "删除"
        elif "添加" in text or "新增" in text:
            intent["操作"] = "添加"
        elif "修改" in text or "更新" in text:
            intent["操作"] = "修改"
        elif "查询" in text or "查找" in text:
            intent["操作"] = "查询"
        
        if "人员" in text:
            intent["对象"] = "人员"
        elif "项目" in text:
            intent["对象"] = "项目"
        elif "材料" in text:
            intent["对象"] = "材料"
        
        return intent

    def _generate_full_question(self, intent_analysis: Dict[str, Any], original_data: Dict[str, Any], original_answer: str) -> str:
        """生成丰富化的完整问题描述"""
        # 从意图分析对象和原始数据中提取信息，生成自然的完整问题

        # 1. 获取操作类型
        operation = intent_analysis.get("businessOpt", "")

        # 2. 从原始数据中提取额外信息
        extra_info = self._extract_extra_info_from_original(original_data)

        # 3. 构建完整问题的各个部分
        question_parts = []

        # 操作部分
        if operation:
            if "导出" in operation:
                question_parts.append("导出结算单")
            elif "审核" in operation:
                question_parts.append("审核通过以下货单")
            elif "删除" in operation:
                question_parts.append("删除")
            elif "添加" in operation:
                question_parts.append("添加")
            elif "查询" in operation:
                question_parts.append("查询")
            else:
                question_parts.append(operation)

        # 供应商部分
        supplier = intent_analysis.get("businessSupplies", "")
        if supplier:
            if isinstance(supplier, list):
                supplier_text = "，".join(supplier)
                question_parts.append(f"供应商是{supplier_text}的")
            else:
                question_parts.append(f"供应商是{supplier}的")

        # 项目部分
        project = intent_analysis.get("businessProject", "")
        if project:
            if isinstance(project, list):
                # 清理项目信息，移除"姓名:"前缀
                clean_projects = []
                for p in project:
                    p_str = str(p)
                    if "姓名:" in p_str:
                        clean_projects.append(p_str.replace("姓名:", ""))
                    else:
                        clean_projects.append(p_str)

                project_text = "和".join(clean_projects)
                question_parts.append(f"项目{project_text}")
            else:
                project_str = str(project)
                if "姓名:" in project_str:
                    project_str = project_str.replace("姓名:", "")
                question_parts.append(f"项目{project_str}")

        # 人员部分
        person = intent_analysis.get("businessPerson", "")
        if person:
            if isinstance(person, list):
                # 清理人员信息格式
                person_info = []
                for p in person:
                    p_str = str(p)
                    if "姓名:" in p_str:
                        person_info.append(p_str.replace("姓名:", ""))
                    elif "编号:" in p_str:
                        person_info.append(p_str.replace("编号:", ""))
                    else:
                        person_info.append(p_str)
                person_text = "，".join(person_info)
                question_parts.append(f"人员{person_text}")
            else:
                question_parts.append(f"人员{person}")

        # 材料部分
        material = intent_analysis.get("businessMaterial", "")
        if material:
            if isinstance(material, list):
                material_text = "，".join(material)
                question_parts.append(f"材料{material_text}")
            else:
                question_parts.append(f"材料{material}")

        # 金额部分（避免重复）
        amount = intent_analysis.get("businessAmount", "")
        extra_amounts = extra_info.get("amounts", [])

        # 合并金额信息，去重
        all_amounts = []
        if amount:
            all_amounts.append(str(amount))
        all_amounts.extend([str(a) for a in extra_amounts if str(a) not in all_amounts])

        if all_amounts:
            if len(all_amounts) == 1:
                question_parts.append(f"金额{all_amounts[0]}")
            else:
                amount_text = "，".join(all_amounts)
                question_parts.append(f"金额{amount_text}")

        # 单号部分
        if extra_info.get("order_numbers"):
            order_text = "，".join(extra_info["order_numbers"])
            question_parts.append(f"单号{order_text}")

        # 状态部分
        status = intent_analysis.get("businessStatus", "")
        if status and status != "审核通过":  # 避免重复
            question_parts.append(f"状态{status}")

        # 时间部分
        time_info = intent_analysis.get("businessTime", "")
        if time_info:
            if isinstance(time_info, list):
                time_text = "，".join(time_info)
                question_parts.append(f"时间{time_text}")
            else:
                question_parts.append(f"时间{time_info}")

        # 组合成自然的完整问题
        if question_parts:
            # 根据操作类型调整连接方式
            if operation and "导出" in operation:
                # 导出类操作：导出结算单，供应商是...的，项目...，单号...
                return "，".join(question_parts)
            elif operation and "审核" in operation:
                # 审核类操作：审核通过以下货单，供应商是...的，项目...，单号...
                return "，".join(question_parts)
            elif operation and "删除" in operation:
                # 删除类操作：删除人员...，项目...
                return "，".join(question_parts)
            else:
                # 其他操作
                return "，".join(question_parts)
        else:
            return "未知操作"

    def _extract_extra_info_from_original(self, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """从原始数据中提取额外信息"""
        extra_info = {
            "order_numbers": [],
            "amounts": []
        }

        # 提取单号信息
        for field in ["对象单号", "货单号", "单号"]:
            if field in original_data:
                value = original_data[field]
                if self._is_meaningful_value(value):
                    if isinstance(value, list):
                        for v in value:
                            if isinstance(v, dict):
                                # 处理字典格式的单号
                                if 'name' in v and self._is_meaningful_value(v['name']):
                                    extra_info["order_numbers"].append(str(v['name']))
                                if 'code' in v and self._is_meaningful_value(v['code']):
                                    extra_info["order_numbers"].append(str(v['code']))
                            elif self._is_meaningful_value(v):
                                extra_info["order_numbers"].append(str(v))
                    elif isinstance(value, str):
                        # 处理逗号分隔的单号
                        if ',' in value:
                            parts = [p.strip() for p in value.split(',')]
                            extra_info["order_numbers"].extend([p for p in parts if p])
                        else:
                            extra_info["order_numbers"].append(value)
                    else:
                        extra_info["order_numbers"].append(str(value))

        # 提取金额信息
        for field in ["对象金额", "总金额", "金额"]:
            if field in original_data:
                value = original_data[field]
                if self._is_meaningful_value(value):
                    if isinstance(value, list):
                        extra_info["amounts"].extend([str(v) for v in value if self._is_meaningful_value(v)])
                    else:
                        extra_info["amounts"].append(str(value))

        return extra_info

    def _is_meaningful_value(self, value: Any) -> bool:
        """检查值是否有意义"""
        if value is None:
            return False
        
        if isinstance(value, str):
            return value.strip() not in ["", "无", "None", "null"]
        
        if isinstance(value, list):
            return len(value) > 0 and any(self._is_meaningful_value(item) for item in value)
        
        if isinstance(value, dict):
            return any(self._is_meaningful_value(v) for v in value.values())
        
        return True
    
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
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                for record in data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"保存文件失败: {e}")
            raise
    
    def _generate_report(self) -> str:
        """生成优化报告"""
        stats = self.stats
        
        # 计算问题缩减统计
        if stats["question_reductions"]:
            avg_reduction_rate = sum(r["reduction_rate"] for r in stats["question_reductions"]) / len(stats["question_reductions"])
            avg_quality = sum(r["quality_score"] for r in stats["question_reductions"]) / len(stats["question_reductions"])
            total_char_saved = sum(r["original_length"] - r["reduced_length"] for r in stats["question_reductions"])
        else:
            avg_reduction_rate = avg_quality = total_char_saved = 0
        
        # 统计应用的规则
        rule_counter = {}
        for reduction in stats["question_reductions"]:
            for rule in reduction["applied_rules"]:
                rule_counter[rule] = rule_counter.get(rule, 0) + 1
        
        report = f"""
# 意图分析训练数据优化报告

## 处理统计
- **总记录数**: {stats['total_processed']}
- **成功优化**: {stats['successfully_optimized']}
- **失败记录**: {len(stats['errors'])}
- **成功率**: {stats['successfully_optimized']/stats['total_processed']*100:.1f}%

## 问题缩减效果
- **平均缩减率**: {avg_reduction_rate:.1%}
- **平均质量评分**: {avg_quality:.3f}
- **总节省字符**: {total_char_saved} 个
- **有效缩减记录**: {len(stats['question_reductions'])} 条

## 意图分析提取
- **成功提取**: {stats['intent_extractions']} 条
- **提取成功率**: {stats['intent_extractions']/stats['total_processed']*100:.1f}%

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
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="意图分析训练数据优化器")
    parser.add_argument("input_file", help="输入JSONL文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-l", "--level", choices=["basic", "advanced", "aggressive"],
                       default="aggressive", help="问题缩减级别")
    parser.add_argument("--messages-only", action="store_true",
                       help="生成纯净的messages结构，移除优化元数据，适合直接用于训练")

    args = parser.parse_args()
    
    optimizer = IntentAnalysisOptimizer()
    result = optimizer.optimize_training_data(
        input_file=args.input_file,
        output_file=args.output,
        reduction_level=args.level,
        messages_only=args.messages_only
    )
    
    print("优化完成！")
    print(f"输出文件: {result['output_file']}")
    print("\n" + result['report'])


if __name__ == "__main__":
    main()
