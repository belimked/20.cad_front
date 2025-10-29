"""
数据库迁移脚本 - 添加输出目录清理配置字段

添加4个新字段到 autocad_config 表：
- output_dir_cleanup_enabled: 是否启用输出目录清理
- output_dir_path: 输出目录路径
- output_dir_backup_before_cleanup: 清理前是否备份
- output_dir_backup_path: 备份目录路径

Author: 老王
Date: 2025-10-28
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal, engine
from sqlalchemy import text


def migrate():
    """执行迁移"""

    print("=" * 80)
    print("数据库迁移 - 添加输出目录清理配置字段")
    print("=" * 80)
    print()

    db = SessionLocal()

    try:
        # 检查字段是否已存在
        print("🔍 检查字段是否已存在...")
        result = db.execute(text("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'autocad_config'
              AND COLUMN_NAME = 'output_dir_cleanup_enabled'
        """))

        if result.fetchone():
            print("⚠️ 字段已存在，跳过迁移")
            return True

        print("✅ 字段不存在，开始迁移...\n")

        # 添加新字段
        migration_sql = """
        ALTER TABLE autocad_config
        ADD COLUMN output_dir_cleanup_enabled BOOLEAN DEFAULT FALSE COMMENT '是否在运行前清理输出目录',
        ADD COLUMN output_dir_path VARCHAR(1000) DEFAULT 'F:\\\\cad\\\\caddd\\\\cadpython\\\\CAD_AutoProcessor\\\\outputs' COMMENT '输出目录路径',
        ADD COLUMN output_dir_backup_before_cleanup BOOLEAN DEFAULT FALSE COMMENT '清理前是否备份',
        ADD COLUMN output_dir_backup_path VARCHAR(1000) DEFAULT NULL COMMENT '备份目录路径';
        """

        print("📝 执行SQL:")
        print(migration_sql)
        print()

        db.execute(text(migration_sql))
        db.commit()

        print("✅ 迁移成功!")
        print()
        print("新增字段:")
        print("  1. output_dir_cleanup_enabled (BOOLEAN) - 是否启用清理")
        print("  2. output_dir_path (VARCHAR(1000)) - 输出目录路径")
        print("  3. output_dir_backup_before_cleanup (BOOLEAN) - 是否备份")
        print("  4. output_dir_backup_path (VARCHAR(1000)) - 备份目录路径")
        print()

        # 验证字段
        print("🔍 验证新字段...")
        result = db.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'autocad_config'
              AND COLUMN_NAME IN ('output_dir_cleanup_enabled', 'output_dir_path',
                                  'output_dir_backup_before_cleanup', 'output_dir_backup_path')
            ORDER BY ORDINAL_POSITION
        """))

        print("\n字段详情:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} (默认: {row[2]}, 注释: {row[3]})")

        print("\n" + "=" * 80)
        print("✅ 迁移完成！")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
