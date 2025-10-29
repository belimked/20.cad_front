"""
初始化DWG任务表

创建时间: 2025-10-29
作者: 老王团队
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal, engine
from sqlalchemy import text


def init_task_tables():
    """初始化任务表"""
    print("=" * 80)
    print("DWG任务表初始化")
    print("=" * 80)

    # 读取SQL文件
    sql_file = project_root / "migrations" / "add_dwg_task_tables.sql"

    if not sql_file.exists():
        print(f"❌ SQL文件不存在: {sql_file}")
        return False

    print(f"\n📄 读取SQL文件: {sql_file}")

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 分割SQL语句（按分号分割）
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # 跳过注释和空行
        line = line.strip()
        if not line or line.startswith('--'):
            continue

        current_statement.append(line)

        # 如果行以分号结尾，表示一条语句结束
        if line.endswith(';'):
            statement = ' '.join(current_statement)
            statements.append(statement)
            current_statement = []

    print(f"✅ 解析到 {len(statements)} 条SQL语句")

    # 执行SQL语句
    db = SessionLocal()
    try:
        print("\n🔧 开始执行SQL...")

        for i, statement in enumerate(statements, 1):
            try:
                # 获取语句类型
                stmt_type = statement.split()[0].upper()

                print(f"\n  [{i}/{len(statements)}] {stmt_type}...", end=' ')

                db.execute(text(statement))
                db.commit()

                print("✅")

            except Exception as e:
                error_msg = str(e)

                # 如果表已存在，不算错误
                if 'already exists' in error_msg or 'duplicate' in error_msg.lower():
                    print(f"⚠️ 已存在")
                else:
                    print(f"❌ 失败: {e}")
                    db.rollback()
                    # 继续执行下一条（不中断）

        print("\n" + "=" * 80)
        print("✅ 任务表初始化完成！")
        print("=" * 80)

        # 验证表是否创建成功
        print("\n🔍 验证表结构...")

        tables = [
            'dwg_process_tasks',
            'dwg_task_steps'
        ]

        for table in tables:
            result = db.execute(text(f"SHOW TABLES LIKE '{table}'"))
            if result.fetchone():
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - 未找到")

        return True

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = init_task_tables()
    sys.exit(0 if success else 1)
