#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练数据修正脚本
自动修正字段名错误、关联关系错误、删除多余表引用
"""

import json
import re
import copy
from typing import Dict, List, Tuple

class TrainingDataFixer:
    def __init__(self):
        # 字段名映射表
        self.field_mappings = {
            'pom_id': {
                'in_material_table': 'mpom_o_id',
                'in_main_table': 'o_id'
            },
            'material_code': 'psam_code',
            'proj_id': 'pro_id'
        }
        
        # 需要删除的多余表
        self.invalid_tables = {'mstb_meterial_project_properties'}
        
        # 正确的表关联关系
        self.correct_relationships = {
            'mstb_pms_purchase_order_material -> mstb_pms_purchase_order_main': 'mpom_o_id -> o_id',
            'mstb_project_materials -> mstb_project': 'pro_id -> pro_id',
            'mstb_pms_purchase_order_main -> mstb_project': 'o_proId -> pro_id',
            'mstb_pms_purchase_order_material -> mstb_project': 'mpom_proId -> pro_id'
        }
        
        self.stats = {
            'total_samples': 0,
            'fixed_field_names': 0,
            'fixed_relationships': 0,
            'removed_invalid_tables': 0,
            'added_complex_queries': 0
        }

    def fix_field_names(self, content: str) -> str:
        """修正字段名错误"""
        original_content = content

        # 修正 pom_id 错误 - 更全面的替换
        content = re.sub(r'\bpom_id\b', 'mpom_o_id', content)

        # 修正特定的关联关系描述
        content = re.sub(
            r'通过pom_id字段与.*?的pom_id字段关联',
            '通过mpom_o_id字段与mstb_pms_purchase_order_main的o_id字段关联',
            content
        )

        # 修正SQL中的关联
        content = re.sub(
            r'(\w+\.)mpom_o_id\s*=\s*(\w+\.)mpom_o_id',
            r'\1mpom_o_id = \2o_id',
            content
        )

        # 修正 material_code
        content = content.replace('material_code', 'psam_code')

        # 修正 proj_id
        content = content.replace('proj_id', 'pro_id')

        if content != original_content:
            self.stats['fixed_field_names'] += 1

        return content

    def fix_relationships(self, content: str) -> str:
        """修正表关联关系描述"""
        original_content = content
        
        # 修正关联关系描述
        patterns = [
            (r'通过pom_id字段与.*?的pom_id字段关联', 
             '通过mpom_o_id字段与mstb_pms_purchase_order_main的o_id字段关联'),
            (r'a\.pom_id\s*=\s*b\.pom_id', 
             'a.mpom_o_id = b.o_id'),
            (r'通过proj_id字段', 
             '通过pro_id字段')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            self.stats['fixed_relationships'] += 1
            
        return content

    def remove_invalid_tables(self, content: str) -> bool:
        """检查并标记包含无效表的样本"""
        for invalid_table in self.invalid_tables:
            if invalid_table in content:
                self.stats['removed_invalid_tables'] += 1
                return True
        return False

    def fix_sample(self, sample: Dict) -> Tuple[Dict, bool]:
        """修正单个样本"""
        fixed_sample = copy.deepcopy(sample)
        should_remove = False
        
        for message in fixed_sample.get('messages', []):
            content = message.get('content', '')
            
            # 检查是否包含无效表
            if self.remove_invalid_tables(content):
                should_remove = True
                break
            
            # 修正字段名
            content = self.fix_field_names(content)
            
            # 修正关联关系
            content = self.fix_relationships(content)
            
            message['content'] = content
        
        return fixed_sample, should_remove

    def generate_complex_queries(self) -> List[Dict]:
        """生成复杂的多表查询样本"""
        complex_samples = []
        
        # 3张表查询样本
        sample_3_tables = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个数据库专家，负责分析表关系、生成SQL查询和ERD设计。你专精于以下业务领域：\n- 项目管理系统的数据库设计\n- 采购订单管理系统\n- 材料管理和库存系统\n- 表关系分析和SQL查询优化\n\n请根据提供的数据库结构，准确分析表关系，生成正确的SQL查询，并提供专业的数据库设计建议。"
                },
                {
                    "role": "user",
                    "content": "需求: 查询每个项目的材料信息和对应的采购订单信息，包括项目名称、材料名称、材料编号、采购订单号、采购员"
                },
                {
                    "role": "assistant",
                    "content": "SQL查询:\n```sql\nSELECT \n    p.pro_name AS 项目名称,\n    pm.psam_name AS 材料名称,\n    pm.psam_code AS 材料编号,\n    pom.o_order_number AS 采购订单号,\n    pom.o_buyer AS 采购员\nFROM mstb_project p\nJOIN mstb_project_materials pm ON p.pro_id = pm.pro_id\nJOIN mstb_pms_purchase_order_main pom ON p.pro_id = pom.o_proId\nORDER BY p.pro_name, pm.psam_name\n```"
                }
            ],
            "task_type": "sql_generation",
            "original_id": "complex_3_tables_001"
        }
        
        # 4张表查询样本
        sample_4_tables = {
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个数据库专家，负责分析表关系、生成SQL查询和ERD设计。你专精于以下业务领域：\n- 项目管理系统的数据库设计\n- 采购订单管理系统\n- 材料管理和库存系统\n- 表关系分析和SQL查询优化\n\n请根据提供的数据库结构，准确分析表关系，生成正确的SQL查询，并提供专业的数据库设计建议。"
                },
                {
                    "role": "user",
                    "content": "需求: 查询项目的完整采购信息，包括项目名称、项目材料、采购订单、具体采购材料数量，要求显示材料的设计尺寸和采购数量"
                },
                {
                    "role": "assistant",
                    "content": "SQL查询:\n```sql\nSELECT \n    p.pro_name AS 项目名称,\n    pm.psam_name AS 项目材料名称,\n    pm.psam_design_size AS 设计尺寸,\n    pom.o_order_number AS 采购订单号,\n    pomat.mpom_psam_name AS 采购材料名称,\n    pomat.mpom_purchaseNumber AS 采购数量,\n    pomat.mpom_hasReceiving_count AS 已收货数量\nFROM mstb_project p\nJOIN mstb_project_materials pm ON p.pro_id = pm.pro_id\nJOIN mstb_pms_purchase_order_main pom ON p.pro_id = pom.o_proId\nJOIN mstb_pms_purchase_order_material pomat ON pom.o_id = pomat.mpom_o_id\nWHERE pomat.mpom_status = '1'\nORDER BY p.pro_name, pom.o_order_number\n```"
                }
            ],
            "task_type": "sql_generation",
            "original_id": "complex_4_tables_001"
        }
        
        complex_samples.extend([sample_3_tables, sample_4_tables])
        self.stats['added_complex_queries'] = len(complex_samples)
        
        return complex_samples

    def fix_training_data(self, input_file: str, output_file: str) -> None:
        """修正整个训练数据文件"""
        print("🔧 开始修正训练数据...")
        
        # 读取原始数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.stats['total_samples'] = len(data)
        print(f"📊 原始样本数量: {self.stats['total_samples']}")
        
        # 修正数据
        fixed_data = []
        removed_count = 0
        
        for i, sample in enumerate(data):
            fixed_sample, should_remove = self.fix_sample(sample)
            
            if should_remove:
                removed_count += 1
                print(f"❌ 移除样本 {i}: 包含无效表")
            else:
                fixed_data.append(fixed_sample)
        
        # 添加复杂查询样本
        complex_samples = self.generate_complex_queries()
        fixed_data.extend(complex_samples)
        
        # 保存修正后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, ensure_ascii=False, indent=2)
        
        # 输出统计信息
        print("\n📈 修正统计:")
        print(f"  原始样本数: {self.stats['total_samples']}")
        print(f"  移除样本数: {removed_count}")
        print(f"  修正字段名: {self.stats['fixed_field_names']} 个样本")
        print(f"  修正关联关系: {self.stats['fixed_relationships']} 个样本")
        print(f"  添加复杂查询: {self.stats['added_complex_queries']} 个样本")
        print(f"  最终样本数: {len(fixed_data)}")
        print(f"\n✅ 修正完成，保存到: {output_file}")

def main():
    fixer = TrainingDataFixer()
    fixer.fix_training_data(
        'data/4table_training_data_messages_format.json',
        'data/4table_training_data_fixed.json'
    )

if __name__ == "__main__":
    main()
