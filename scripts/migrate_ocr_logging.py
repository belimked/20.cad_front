#!/usr/bin/env python3
"""
执行OCR日志和文件管理功能的数据库迁移

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.utils.database import SessionLocal


def run_migration():
    """执行数据库迁移"""
    print("=" * 80)
    print("OCR日志和文件管理功能 - 数据库迁移")
    print("=" * 80)

    # 读取SQL迁移文件
    migration_file = project_root / "migrations" / "add_ocr_logging_and_file_management.sql"

    if not migration_file.exists():
        print(f"❌ 迁移文件不存在: {migration_file}")
        return False

    print(f"\n📄 读取迁移文件: {migration_file}")

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 移除注释行和空行
    lines = []
    for line in sql_content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('--'):
            lines.append(line)

    sql_content = '\n'.join(lines)

    # 按分号分割SQL语句（这次使用更简单的方法：直接split，然后过滤空语句）
    # 注意：这种方法假设SQL中的字符串里没有分号（我们的SQL文件确实没有）
    raw_statements = sql_content.split(';')

    # 过滤掉空语句
    statements = []
    for stmt in raw_statements:
        stmt = stmt.strip()
        if stmt:
            statements.append(stmt)

    print(f"✅ 解析到 {len(statements)} 条SQL语句")

    # 执行迁移
    db = SessionLocal()
    success_count = 0
    failed_count = 0

    try:
        print("\n🔄 开始执行迁移...")

        for i, statement in enumerate(statements, 1):
            statement = statement.strip()
            if not statement:
                continue

            # 提取语句类型（CREATE TABLE、ALTER TABLE、INSERT等）
            first_words = statement.split(None, 2)[:2]
            statement_type = ' '.join(first_words) if len(first_words) >= 2 else first_words[0]

            print(f"\n[{i}/{len(statements)}] 执行: {statement_type}...", end=" ")

            try:
                # 执行SQL语句
                db.execute(text(statement))
                db.commit()
                print("✅")
                success_count += 1

            except Exception as e:
                error_msg = str(e)

                # 检查是否是"已存在"错误（可以忽略）
                if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
                    print("⚠️ (已存在，跳过)")
                    success_count += 1
                else:
                    print(f"❌")
                    print(f"     错误: {error_msg}")
                    failed_count += 1

                    # 询问是否继续
                    if failed_count >= 3:
                        print("\n❌ 遇到多个错误，迁移中止")
                        return False

                db.rollback()

        print("\n" + "=" * 80)
        print("迁移完成！")
        print(f"✅ 成功: {success_count} 条")
        if failed_count > 0:
            print(f"❌ 失败: {failed_count} 条")
        print("=" * 80)

        return failed_count == 0

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")

    db = SessionLocal()

    try:
        # 检查表是否存在
        tables_to_check = [
            'ocr_recognition_logs',
            'ocr_preprocessing_performance'
        ]

        for table_name in tables_to_check:
            result = db.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
            if result.fetchone():
                print(f"  ✅ 表 {table_name} 存在")
            else:
                print(f"  ❌ 表 {table_name} 不存在")
                return False

        # 检查autocad_configs表的新字段
        result = db.execute(text("DESCRIBE autocad_configs"))
        columns = {row[0] for row in result.fetchall()}

        required_columns = [
            'ocr_screenshot_base_dir',
            'ocr_screenshot_timestamp_format',
            'ocr_file_cleanup_enabled',
            'ocr_file_cleanup_strategy',
            'ocr_file_archive_dir',
            'ocr_file_retention_days',
            'ocr_enable_detailed_logging'
        ]

        for column in required_columns:
            if column in columns:
                print(f"  ✅ 字段 autocad_configs.{column} 存在")
            else:
                print(f"  ❌ 字段 autocad_configs.{column} 不存在")
                return False

        # 检查字典数据
        result = db.execute(text(
            "SELECT COUNT(*) FROM sys_dictionary WHERE dict_type IN ('ocr_cleanup_strategy', 'ocr_timestamp_format')"
        ))
        dict_count = result.fetchone()[0]

        if dict_count > 0:
            print(f"  ✅ 字典数据已插入 ({dict_count} 条)")
        else:
            print(f"  ⚠️ 字典数据未插入（可能需要手动执行）")

        print("\n✅ 验证通过！")
        return True

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        return False

    finally:
        db.close()


def main():
    """主函数"""
    print("\n⚠️  警告：此脚本将修改数据库结构！")
    print("建议先备份数据库！\n")

    response = input("是否继续？(yes/no): ").strip().lower()

    if response not in ['yes', 'y', '是']:
        print("已取消")
        return

    # 执行迁移
    if run_migration():
        # 验证迁移
        if verify_migration():
            print("\n🎉 迁移成功完成！")
            print("\n📋 后续步骤：")
            print("1. 检查 autocad_configs 表的新字段是否正确")
            print("2. 配置 ocr_screenshot_base_dir 等参数")
            print("3. 测试OCR功能，验证日志记录是否正常")
        else:
            print("\n⚠️ 迁移执行完成，但验证未通过！")
            print("请手动检查数据库")
    else:
        print("\n❌ 迁移失败！")
        print("请检查错误信息，并手动修复数据库")


if __name__ == "__main__":
    main()
