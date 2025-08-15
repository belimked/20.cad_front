#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版训练数据优化器

专门针对已有训练数据进行简单而有效的优化
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class SimpleTrainingOptimizer:
    """简化版训练数据优化器"""
    
    def __init__(self):
        """初始化优化器"""
        self.logger = self._setup_logger()
        self.stats = {
            "total_processed": 0,
            "successfully_optimized": 0,
            "question_improvements": 0,
            "answer_improvements": 0,
            "total_question_reduction": 0,
            "total_answer_reduction": 0
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
                             output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        优化训练数据
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则自动生成
            
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
                optimized_record = self._optimize_single_record(record)
                optimized_data.append(optimized_record)
                self.stats["successfully_optimized"] += 1
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"已处理 {i + 1}/{len(original_data)} 条记录")
                    
            except Exception as e:
                self.logger.error(f"处理第 {i + 1} 条记录时出错: {e}")
                # 保留原始记录
                optimized_data.append(record)
        
        self.stats["total_processed"] = len(original_data)
        
        # 生成输出文件路径
        if output_file is None:
            input_path = Path(input_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(input_path.parent / f"simple_optimized_{input_path.stem}_{timestamp}.jsonl")
        
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
    
    def _optimize_single_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """优化单条记录"""
        if "messages" not in record or len(record["messages"]) < 2:
            return record
        
        user_message = record["messages"][0]
        assistant_message = record["messages"][1]
        
        if user_message.get("role") != "user" or assistant_message.get("role") != "assistant":
            return record
        
        original_question = user_message.get("content", "")
        original_answer = assistant_message.get("content", "")
        
        # 优化问题
        optimized_question = self._optimize_question(original_question)
        if len(optimized_question) < len(original_question):
            self.stats["question_improvements"] += 1
            self.stats["total_question_reduction"] += len(original_question) - len(optimized_question)
        
        # 优化回答
        optimized_answer = self._optimize_answer(original_answer)
        if len(optimized_answer) < len(original_answer):
            self.stats["answer_improvements"] += 1
            self.stats["total_answer_reduction"] += len(original_answer) - len(optimized_answer)
        
        # 构建优化后的记录
        return {
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
    
    def _optimize_question(self, question: str) -> str:
        """优化问题文本"""
        if not question:
            return question
        
        # 简单的文本清理
        optimized = question
        
        # 移除多余的标点符号
        optimized = re.sub(r'[，,]{2,}', '，', optimized)
        optimized = re.sub(r'[。.]{2,}', '。', optimized)
        
        # 标准化连接词
        optimized = optimized.replace('以及', '，')
        optimized = optimized.replace('和', '，')
        optimized = optimized.replace('、', '，')
        
        # 移除多余的空格
        optimized = re.sub(r'\s+', '', optimized)
        
        # 清理开头和结尾的标点
        optimized = optimized.strip('，。、')
        
        return optimized.strip()
    
    def _optimize_answer(self, answer: str) -> str:
        """优化回答JSON"""
        try:
            # 解析JSON
            answer_data = json.loads(answer)
            
            # 定义要保留的核心字段
            core_fields = {
                "操作", "对象", "人员姓名", "人员项目", "人员全部项目",
                "项目", "供应商", "材料类型", "材料编号", "材料工程属性",
                "对象金额", "对象状态", "对象提交时间", "对象下单时间"
            }
            
            # 创建优化后的数据
            optimized_data = {}
            
            for key, value in answer_data.items():
                if key in core_fields:
                    # 检查值是否有意义
                    if self._is_meaningful_value(value):
                        optimized_data[key] = self._clean_value(value)
                    elif key in ["操作", "对象"]:
                        # 操作和对象字段总是保留
                        optimized_data[key] = value
            
            # 确保必要字段存在
            if "操作" not in optimized_data:
                optimized_data["操作"] = answer_data.get("操作", "未知")
            if "对象" not in optimized_data:
                optimized_data["对象"] = answer_data.get("对象", "未知")
            
            return json.dumps(optimized_data, ensure_ascii=False, separators=(',', ':'))
            
        except json.JSONDecodeError:
            return answer
        except Exception:
            return answer
    
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
    
    def _clean_value(self, value: Any) -> Any:
        """清理值"""
        if isinstance(value, str):
            return value.strip()
        
        if isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    # 清理字典项
                    cleaned_dict = {}
                    for k, v in item.items():
                        if self._is_meaningful_value(v):
                            cleaned_dict[k] = self._clean_value(v)
                    if cleaned_dict:
                        cleaned_list.append(cleaned_dict)
                elif self._is_meaningful_value(item):
                    cleaned_list.append(self._clean_value(item))
            return cleaned_list
        
        if isinstance(value, dict):
            cleaned_dict = {}
            for k, v in value.items():
                if self._is_meaningful_value(v):
                    cleaned_dict[k] = self._clean_value(v)
            return cleaned_dict
        
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
        
        question_avg_reduction = (stats["total_question_reduction"] / stats["question_improvements"] 
                                if stats["question_improvements"] > 0 else 0)
        answer_avg_reduction = (stats["total_answer_reduction"] / stats["answer_improvements"] 
                              if stats["answer_improvements"] > 0 else 0)
        
        report = f"""
# 简化版训练数据优化报告

## 处理统计
- **总记录数**: {stats['total_processed']}
- **成功优化**: {stats['successfully_optimized']}
- **成功率**: {stats['successfully_optimized']/stats['total_processed']*100:.1f}%

## 问题优化效果
- **改进记录数**: {stats['question_improvements']}
- **总字符减少**: {stats['total_question_reduction']}
- **平均每条减少**: {question_avg_reduction:.1f} 字符

## 回答优化效果
- **改进记录数**: {stats['answer_improvements']}
- **总字符减少**: {stats['total_answer_reduction']}
- **平均每条减少**: {answer_avg_reduction:.1f} 字符

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """.strip()
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="简化版训练数据优化器")
    parser.add_argument("input_file", help="输入JSONL文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    optimizer = SimpleTrainingOptimizer()
    result = optimizer.optimize_training_data(
        input_file=args.input_file,
        output_file=args.output
    )
    
    print("优化完成！")
    print(f"输出文件: {result['output_file']}")
    print("\n" + result['report'])


if __name__ == "__main__":
    main()
