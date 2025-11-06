"""
初始化提取配置到 sys_dictionary 表

该脚本用于初始化图号/材料/标题提取所需的配置参数，包括：
1. 排除词汇列表
2. 材料关键字列表
3. 提取规则参数

使用方法：
    python scripts/init_extraction_config.py

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from src.models.dictionary import Dictionary
import json


def init_extraction_config():
    """初始化提取配置到 sys_dictionary 表"""

    print("=" * 60)
    print("初始化提取配置 - sys_dictionary 表")
    print("=" * 60)

    # 配置数据
    configs = [
        {
            'dict_type': 'extraction',
            'dict_key': 'extraction_excluded_keywords',
            'dict_value': json.dumps([
                '技术要求', '材料', '数量', '备注', '名称', '代号', '序号',
                '设计', '审核', '批准', '标记', '处数', '修改日期', '签名',
                '重量', '版号', '比例', '深圳市', '有限公司', '单重', '总重'
            ], ensure_ascii=False),
            'dict_label': '标题提取排除词汇',
            'dict_description': '从表格中提取标题时需要排除的通用词汇列表',
            'is_active': True,
            'sort_order': 1
        },
        {
            'dict_type': 'extraction',
            'dict_key': 'extraction_material_keywords',
            'dict_value': json.dumps([
                '材料:', 'Material:', 'material:'
            ], ensure_ascii=False),
            'dict_label': '材料关键字列表',
            'dict_description': '用于识别材料信息的关键字（支持中英文）',
            'is_active': True,
            'sort_order': 2
        },
        {
            'dict_type': 'extraction',
            'dict_key': 'extraction_rules',
            'dict_value': json.dumps({
                'min_chinese_chars': 4,
                'min_title_length': 4,
                'drawing_number_min_length': 10,
                'drawing_number_min_hyphens': 3
            }, ensure_ascii=False),
            'dict_label': '提取规则参数',
            'dict_description': '提取图号、标题、材料时使用的规则参数',
            'is_active': True,
            'sort_order': 3
        }
    ]

    try:
        with db_session() as session:
            print("\n📝 开始插入配置...")

            for config in configs:
                dict_key = config['dict_key']

                # 检查是否已存在
                existing = session.query(Dictionary).filter_by(
                    dict_type='extraction',
                    dict_key=dict_key
                ).first()

                if existing:
                    print(f"  ⚠️  配置已存在: {dict_key} (跳过)")
                    continue

                # 插入新配置
                record = Dictionary(**config)
                session.add(record)
                print(f"  ✅ 已添加: {dict_key}")
                print(f"     - 标签: {config['dict_label']}")
                print(f"     - 描述: {config['dict_description']}")

            # 提交事务
            session.commit()
            print("\n" + "=" * 60)
            print("🎉 提取配置初始化完成！")
            print("=" * 60)

            # 验证插入结果
            print("\n📊 配置验证:")
            configs_in_db = session.query(Dictionary).filter_by(
                dict_type='extraction',
                is_active=True
            ).order_by(Dictionary.sort_order).all()

            print(f"\n已插入 {len(configs_in_db)} 条配置:\n")
            for cfg in configs_in_db:
                print(f"  - {cfg.dict_key}")
                print(f"    标签: {cfg.dict_label}")
                print(f"    值: {cfg.dict_value[:100]}..." if len(cfg.dict_value) > 100 else f"    值: {cfg.dict_value}")
                print()

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = init_extraction_config()
    exit(0 if success else 1)
