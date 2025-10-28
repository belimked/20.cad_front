#!/usr/bin/env python3
"""
自动数据库迁移脚本

在启动程序前自动执行所有待处理的迁移

Author: CAD Auto Processor Team
Date: 2025-10-28
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.utils.database import SessionLocal


def get_pending_migrations():
    """获取所有待执行的迁移文件"""
    migrations_dir = project_root / "migrations"

    # 按文件名排序（确保按创建顺序执行）
    migration_files = sorted(migrations_dir.glob("*.sql"))

    return migration_files


def check_column_exists(db, table_name, column_name):
    """检查表中是否存在指定列"""
    try:
        result = db.execute(text(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'"))
        return result.fetchone() is not None
    except:
        return False


def check_table_exists(db, table_name):
    """检查表是否存在"""
    try:
        result = db.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
        return result.fetchone() is not None
    except:
        return False


def is_migration_needed(db, migration_file):
    """判断迁移是否需要执行（简单检查）"""
    filename = migration_file.name.lower()

    # 根据文件名判断
    if 'add_umi_ocr_config' in filename:
        return not check_column_exists(db, 'autocad_config', 'umi_ocr_service_url')

    elif 'add_matched_text' in filename:
        return not check_column_exists(db, 'ocr_preprocessing_performance', 'matched_text')

    elif 'add_umi_ocr_limit_side_len' in filename:
        return not check_column_exists(db, 'autocad_config', 'umi_ocr_limit_side_len')

    elif 'add_umi_ocr_max_workers' in filename:
        return not check_column_exists(db, 'autocad_config', 'umi_ocr_max_workers')

    elif 'add_ocr_logging' in filename:
        return not check_table_exists(db, 'ocr_recognition_logs')

    # 默认尝试执行
    return True


def run_auto_migration(silent=False):
    """
    自动执行数据库迁移

    Args:
        silent: 如果为True，没有待执行的迁移时不输出信息
    """
    db = SessionLocal()

    try:
        migration_files = get_pending_migrations()

        if not migration_files:
            if not silent:
                print("⚠️ 未找到迁移文件")
            return True

        executed_count = 0
        skipped_count = 0
        failed_count = 0

        for migration_file in migration_files:
            # 检查是否需要执行
            if not is_migration_needed(db, migration_file):
                skipped_count += 1
                continue

            print(f"📦 执行迁移: {migration_file.name}")

            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()

                # 分割SQL语句（以分号分隔）
                statements = []
                for stmt in sql_content.split(';'):
                    stmt = stmt.strip()
                    # 跳过注释和空语句
                    if stmt and not stmt.startswith('--'):
                        statements.append(stmt)

                # 执行每条语句
                for stmt in statements:
                    try:
                        db.execute(text(stmt))
                    except Exception as e:
                        error_msg = str(e).lower()
                        # 忽略"已存在"类的错误
                        if 'already exists' in error_msg or 'duplicate' in error_msg:
                            continue
                        raise

                db.commit()
                print(f"   ✅ 成功")
                executed_count += 1

            except Exception as e:
                error_msg = str(e).lower()

                # 忽略"已存在"类的错误
                if 'already exists' in error_msg or 'duplicate' in error_msg:
                    print(f"   ⚠️ 已存在（跳过）")
                    skipped_count += 1
                else:
                    print(f"   ❌ 失败: {e}")
                    failed_count += 1

                db.rollback()

        # 输出总结
        if executed_count > 0 or failed_count > 0:
            print("\n" + "=" * 50)
            print(f"迁移执行完成:")
            if executed_count > 0:
                print(f"  ✅ 成功: {executed_count} 个")
            if skipped_count > 0:
                print(f"  ⏭️  跳过: {skipped_count} 个")
            if failed_count > 0:
                print(f"  ❌ 失败: {failed_count} 个")
            print("=" * 50 + "\n")
        elif not silent:
            print("✅ 数据库已是最新版本，无需迁移\n")

        return failed_count == 0

    except Exception as e:
        print(f"❌ 迁移系统错误: {e}")
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    # 检查是否传入了 --silent 参数
    silent = '--silent' in sys.argv

    success = run_auto_migration(silent=silent)
    sys.exit(0 if success else 1)
