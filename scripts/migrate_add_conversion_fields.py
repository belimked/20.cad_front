"""
数据库迁移：为 dwg_drawing_sheets 表新增 PDF 转换字段

新增字段：
- converted_directory: 转换后目录路径
- converted_filename: 转换后文件名
- conversion_status: 转换状态（pending/completed/failed/skipped）
- conversion_error: 转换错误信息
- converted_at: 转换完成时间

使用方法：
    python scripts/migrate_add_conversion_fields.py

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session, engine
from sqlalchemy import text


def migrate_add_conversion_fields():
    """为 dwg_drawing_sheets 表新增转换字段"""

    print("=" * 70)
    print("数据库迁移：新增 PDF 转换字段")
    print("=" * 70)

    # SQL 语句
    migrations = [
        {
            'name': 'converted_directory',
            'sql': """
                ALTER TABLE dwg_drawing_sheets
                ADD COLUMN converted_directory VARCHAR(500) NULL
                COMMENT '转换后目录路径'
            """
        },
        {
            'name': 'converted_filename',
            'sql': """
                ALTER TABLE dwg_drawing_sheets
                ADD COLUMN converted_filename VARCHAR(255) NULL
                COMMENT '转换后文件名'
            """
        },
        {
            'name': 'conversion_status',
            'sql': """
                ALTER TABLE dwg_drawing_sheets
                ADD COLUMN conversion_status VARCHAR(20) DEFAULT 'pending'
                COMMENT '转换状态: pending/completed/failed/skipped'
            """
        },
        {
            'name': 'conversion_error',
            'sql': """
                ALTER TABLE dwg_drawing_sheets
                ADD COLUMN conversion_error TEXT NULL
                COMMENT '转换错误信息'
            """
        },
        {
            'name': 'converted_at',
            'sql': """
                ALTER TABLE dwg_drawing_sheets
                ADD COLUMN converted_at DATETIME NULL
                COMMENT '转换完成时间'
            """
        }
    ]

    try:
        with engine.connect() as conn:
            print("\n📋 开始迁移...\n")

            for migration in migrations:
                field_name = migration['name']
                sql = migration['sql']

                try:
                    # 检查字段是否已存在
                    check_sql = text(f"""
                        SELECT COUNT(*) as count
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                          AND TABLE_NAME = 'dwg_drawing_sheets'
                          AND COLUMN_NAME = '{field_name}'
                    """)

                    result = conn.execute(check_sql)
                    exists = result.fetchone()[0] > 0

                    if exists:
                        print(f"  ⚠️  字段已存在: {field_name} (跳过)")
                        continue

                    # 执行迁移
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"  ✅ 已添加字段: {field_name}")

                except Exception as e:
                    # 忽略 "Duplicate column" 错误
                    if "Duplicate column" in str(e):
                        print(f"  ⚠️  字段已存在: {field_name} (跳过)")
                    else:
                        raise

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
                  AND TABLE_NAME = 'dwg_drawing_sheets'
                  AND COLUMN_NAME IN (
                      'converted_directory',
                      'converted_filename',
                      'conversion_status',
                      'conversion_error',
                      'converted_at'
                  )
                ORDER BY ORDINAL_POSITION
            """)

            result = conn.execute(verify_sql)
            rows = result.fetchall()

            if rows:
                for row in rows:
                    print(f"  ✅ {row[0]}")
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
    success = migrate_add_conversion_fields()
    exit(0 if success else 1)
