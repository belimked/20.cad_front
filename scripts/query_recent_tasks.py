"""
查询最近的 MinerU 识别任务

快速查看最近的任务 ID 和识别结果统计

使用方法：
    python scripts/query_recent_tasks.py [limit]

示例：
    python scripts/query_recent_tasks.py        # 默认显示最近 5 个任务
    python scripts/query_recent_tasks.py 10     # 显示最近 10 个任务

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from sqlalchemy import text


def query_recent_tasks(limit: int = 5):
    """查询最近的识别任务"""

    print("=" * 70)
    print(f"📋 最近 {limit} 个 MinerU 识别任务")
    print("=" * 70)

    with db_session() as session:
        # 查询最近的任务
        sql = text("""
            SELECT
                task_id,
                COUNT(*) as total_files,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                MAX(created_at) as latest_time
            FROM dwg_recognition_results
            GROUP BY task_id
            ORDER BY latest_time DESC
            LIMIT :limit
        """)

        tasks = session.execute(sql, {"limit": limit}).fetchall()

        if not tasks:
            print("\n  ⚠️  未找到识别任务记录")
            return

        print()
        for idx, task in enumerate(tasks, 1):
            print(f"{idx}. Task ID: {task.task_id}")
            print(f"   时间: {task.latest_time}")
            print(f"   总文件数: {task.total_files}")
            print(f"   成功: {task.success_count}, 失败: {task.failed_count}")

            # 查询图号提取情况
            sheet_sql = text("""
                SELECT
                    COUNT(*) as total_sheets,
                    SUM(CASE WHEN sheet_number IS NOT NULL THEN 1 ELSE 0 END) as has_sheet_number
                FROM dwg_drawing_sheets
                WHERE task_id = :task_id
            """)

            sheet_stats = session.execute(sheet_sql, {"task_id": task.task_id}).fetchone()

            if sheet_stats and sheet_stats.total_sheets > 0:
                print(f"   图纸记录: {sheet_stats.total_sheets} 条")
                print(f"   有图号: {sheet_stats.has_sheet_number} 个 ✅")
                if sheet_stats.has_sheet_number == 0:
                    print(f"   ⚠️  警告：所有文件都未提取到图号！")
            else:
                print(f"   ⚠️  未创建图纸记录（图号提取失败）")

            print()

        print("=" * 70)
        print("💡 使用诊断脚本查看详情:")
        print("=" * 70)
        if tasks:
            print(f"  python scripts/diagnose_reorganize_issue.py {tasks[0].task_id}")


def main():
    """主函数"""
    limit = 5

    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print("❌ 参数必须是数字")
            sys.exit(1)

    query_recent_tasks(limit)


if __name__ == '__main__':
    main()
