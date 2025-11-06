"""
数据库迁移：为 autocad_config 表新增 auto_reorganize_pdfs 字段

新增字段：
- auto_reorganize_pdfs: 是否在识别完成后自动重组织PDF文件（BOOLEAN，默认 TRUE）

使用方法：
    python scripts/migrate_add_reorganize_field.py

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import engine
from sqlalchemy import text


def migrate_add_reorganize_field():
    """为 autocad_config 表新增 auto_reorganize_pdfs 字段"""

    print("=" * 70)
    print("数据库迁移：新增 PDF 重组织配置字段")
    print("=" * 70)

    # SQL 语句
    sql = """
        ALTER TABLE autocad_config
        ADD COLUMN auto_reorganize_pdfs BOOLEAN DEFAULT TRUE
        COMMENT '是否在识别完成后自动重组织PDF文件（重命名为图号）'
    """

    try:
        with engine.connect() as conn:
            print("\n📋 开始迁移...\n")

            # 检查字段是否已存在
            check_sql = text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'autocad_config'
                  AND COLUMN_NAME = 'auto_reorganize_pdfs'
            """)

            result = conn.execute(check_sql)
            exists = result.fetchone()[0] > 0

            if exists:
                print(f"  ⚠️  字段已存在: auto_reorganize_pdfs (跳过)")
            else:
                # 执行迁移
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✅ 已添加字段: auto_reorganize_pdfs")

            print("\n" + "=" * 70)
            print("🎉 迁移完成！")
            print("=" * 70)

            # 验证迁移结果
            print("\n📊 字段验证:\n")
            verify_sql = text("""
                SELECT
                    COLUMN_NAME as '字段名',
                    COLUMN_TYPE as '类型',
                    IS_NULLABLE as '可空',
                    COLUMN_DEFAULT as '默认值',
                    COLUMN_COMMENT as '注释'
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'autocad_config'
                  AND COLUMN_NAME = 'auto_reorganize_pdfs'
            """)

            result = conn.execute(verify_sql)
            row = result.fetchone()

            if row:
                print(f"  ✅ auto_reorganize_pdfs")
                print(f"     类型: {row[1]}")
                print(f"     可空: {row[2]}")
                print(f"     默认值: {row[3] if row[3] else 'NULL'}")
                print(f"     注释: {row[4]}")
                print()
            else:
                print("  ⚠️  未找到新增字段")

            return True

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = migrate_add_reorganize_field()
    exit(0 if success else 1)
