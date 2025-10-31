#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加 use_bplot 字段

为 dwg_process_tasks 表添加 use_bplot 列

执行方式:
    python scripts/migrate_add_use_bplot.py

Author: CAD Auto Processor Team
Date: 2025-10-31
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_manager
from sqlalchemy import text


def check_column_exists(db_manager, table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    try:
        with db_manager.session_scope() as session:
            result = session.execute(
                text("""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = :table_name
                      AND COLUMN_NAME = :column_name
                """),
                {"table_name": table_name, "column_name": column_name}
            )
            count = result.scalar()
            return count > 0
    except Exception as e:
        print(f"❌ 检查列失败: {e}")
        return False


def migrate_add_use_bplot():
    """添加 use_bplot 列"""
    print("\n" + "=" * 80)
    print("数据库迁移：添加 use_bplot 字段")
    print("=" * 80)

    # 获取数据库管理器
    db_manager = get_db_manager()

    # 测试连接
    print("\n▶ 步骤 1: 测试数据库连接")
    if not db_manager.test_connection():
        print("❌ 数据库连接失败")
        return False
    print("✅ 数据库连接成功")

    # 检查列是否已存在
    print("\n▶ 步骤 2: 检查 use_bplot 列是否存在")
    if check_column_exists(db_manager, 'dwg_process_tasks', 'use_bplot'):
        print("ℹ️  use_bplot 列已存在，无需迁移")
        return True

    # 添加列
    print("\n▶ 步骤 3: 添加 use_bplot 列")
    try:
        with db_manager.session_scope() as session:
            # 添加列的 SQL
            alter_sql = text("""
                ALTER TABLE dwg_process_tasks
                ADD COLUMN use_bplot INT DEFAULT 0 COMMENT '是否使用bplot工作流（0=否，1=是）'
                AFTER autocad_task_log_id
            """)

            session.execute(alter_sql)
            print("✅ use_bplot 列添加成功")

    except Exception as e:
        print(f"❌ 添加列失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 验证
    print("\n▶ 步骤 4: 验证列是否添加成功")
    if check_column_exists(db_manager, 'dwg_process_tasks', 'use_bplot'):
        print("✅ 验证成功：use_bplot 列已存在")
    else:
        print("❌ 验证失败：use_bplot 列不存在")
        return False

    print("\n" + "=" * 80)
    print("✅ 数据库迁移完成！")
    print("=" * 80)

    return True


if __name__ == "__main__":
    try:
        success = migrate_add_use_bplot()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
