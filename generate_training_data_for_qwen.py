#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练数据生成脚本 - 专为qwen2.5-3b模型设计
生成业务意图识别的训练数据

作者: Claude 4.0 sonnet
日期: 2025-08-20
"""

import json
import os
import sys
from typing import List, Dict, Any
from collections import Counter
import random

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.service.qwen_api_service import generate_dialogs_and_raw_data


class TrainingDataGenerator:
    """训练数据生成器"""
    
    def __init__(self):
        # 业务对象到业务意图的映射
        self.business_object_mapping = {
            'searchCargo': {
                'intent': '查询',
                'object': '货单信息审核单',
                'description': '货单查询'
            },
            'searchContract': {
                'intent': '查询', 
                'object': '合同信息审核单',
                'description': '合同查询'
            },
            'searchPo': {
                'intent': '查询',
                'object': '订单预结算审核单', 
                'description': '订单查询'
            },
            'searchStaff': {
                'intent': '查询',
                'object': '人员安排',
                'description': '人员查询'
            },
            'updateCargo': {
                'intent': '更新',
                'object': '货单信息审核单',
                'description': '货单更新'
            },
            'updateStaff': {
                'intent': '更新', 
                'object': '人员安排',
                'description': '人员更新'
            }
        }
        
        # 每个业务对象的目标数据量
        self.target_samples_per_object = 250
        
    def generate_natural_language_from_question_data(self, question_data: Dict, business_object: str) -> str:
        """
        将问题数据转换为自然语言
        
        Args:
            question_data: 问题数据字典
            business_object: 业务对象名称
            
        Returns:
            自然语言字符串
        """
        # 过滤掉空值和无意义的字段
        meaningful_parts = []
        
        for key, value in question_data.items():
            if value and str(value).strip() and str(value) not in ['', '的', '和', '将', '到', '去', '从', '角色']:
                meaningful_parts.append(str(value))
        
        # 组合成自然语言
        if meaningful_parts:
            # 简单的连接，保持自然性
            natural_text = ''.join(meaningful_parts)
            
            # 特殊处理：确保语句的完整性
            if not natural_text.endswith(('？', '。', '！')):
                # 根据业务对象类型添加适当的结尾
                if 'search' in business_object:
                    if not any(char in natural_text for char in ['查询', '查', '看', '找', '列出']):
                        natural_text = '查询' + natural_text
                elif 'update' in business_object:
                    if not any(char in natural_text for char in ['安排', '添加', '更新', '修改']):
                        natural_text = '安排' + natural_text
            
            return natural_text
        else:
            # 如果没有有意义的部分，返回一个默认查询
            mapping = self.business_object_mapping.get(business_object, {})
            return f"查询{mapping.get('object', '相关信息')}"
    
    def generate_business_object_data(self, business_object: str) -> List[Dict]:
        """
        为单个业务对象生成训练数据
        
        Args:
            business_object: 业务对象名称
            
        Returns:
            训练数据列表
        """
        print(f"正在生成 {business_object} 的训练数据...")
        
        try:
            # 使用现有框架生成原始数据
            _, raw_data = generate_dialogs_and_raw_data(
                business_object=business_object,
                total_samples=self.target_samples_per_object,
                variations_per_rule=3,  # 增加变种数量提高多样性
                ruleids=None
            )
            
            training_data = []
            mapping = self.business_object_mapping.get(business_object, {})
            intent = mapping.get('intent', '查询')
            obj = mapping.get('object', '未知对象')
            
            for item in raw_data:
                question_data = item.get('question', {})
                
                # 生成自然语言
                user_content = self.generate_natural_language_from_question_data(question_data, business_object)
                
                # 生成助手回复
                assistant_content = f"业务意图[{intent}]业务对象[{obj}]"
                
                # 构建训练数据格式
                training_item = {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_content
                        },
                        {
                            "role": "assistant", 
                            "content": assistant_content
                        }
                    ]
                }
                
                training_data.append(training_item)
            
            print(f"✓ {business_object} 生成了 {len(training_data)} 条数据")
            return training_data
            
        except Exception as e:
            print(f"✗ 生成 {business_object} 数据时出错: {e}")
            return []
    
    def generate_all_training_data(self) -> List[Dict]:
        """
        生成所有业务对象的训练数据
        
        Returns:
            完整的训练数据列表
        """
        print("开始生成完整训练数据集...")
        print("=" * 50)
        
        all_training_data = []
        statistics = {}
        
        for business_object in self.business_object_mapping.keys():
            data = self.generate_business_object_data(business_object)
            all_training_data.extend(data)
            statistics[business_object] = len(data)
        
        print("=" * 50)
        print("数据生成完成！")
        print(f"总计生成: {len(all_training_data)} 条训练数据")
        print("\n各业务对象数据分布:")
        for obj, count in statistics.items():
            desc = self.business_object_mapping[obj]['description']
            print(f"  {obj} ({desc}): {count} 条")
        
        return all_training_data, statistics
    
    def save_training_data(self, training_data: List[Dict], statistics: Dict, output_file: str = "qwen_training_data.json"):
        """
        保存训练数据到文件
        
        Args:
            training_data: 训练数据列表
            statistics: 统计信息
            output_file: 输出文件名
        """
        # 随机打乱数据顺序
        random.shuffle(training_data)
        
        # 保存训练数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, ensure_ascii=False, indent=2)
        
        # 保存统计信息
        stats_file = output_file.replace('.json', '_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_samples': len(training_data),
                'business_object_distribution': statistics,
                'business_object_mapping': self.business_object_mapping
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 训练数据已保存到: {output_file}")
        print(f"✓ 统计信息已保存到: {stats_file}")
        
        # 显示数据样本
        print(f"\n数据样本预览 (前3条):")
        for i, sample in enumerate(training_data[:3]):
            print(f"\n样本 {i+1}:")
            print(f"  用户: {sample['messages'][0]['content']}")
            print(f"  助手: {sample['messages'][1]['content']}")


def main():
    """主函数"""
    print("🐾 Claude 4.0 sonnet 训练数据生成器")
    print("专为qwen2.5-3b业务意图识别模型设计")
    print("=" * 60)
    
    # 创建生成器
    generator = TrainingDataGenerator()
    
    # 生成训练数据
    training_data, statistics = generator.generate_all_training_data()
    
    # 保存数据
    generator.save_training_data(training_data, statistics)
    
    print("\n🎉 训练数据生成完成！")
    print("数据已准备好用于qwen2.5-3b模型训练")


if __name__ == "__main__":
    main()
