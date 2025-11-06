"""
诊断 PDF 重组织问题

检查项：
1. dwg_recognition_results 表是否有识别记录
2. 识别结果中是否有 markdown 内容
3. 图号提取是否成功
4. dwg_drawing_sheets 表是否有图号记录

使用方法：
    python scripts/diagnose_reorganize_issue.py <task_id>

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from src.models.dwg_drawing_sheet import DWGDrawingSheet
from sqlalchemy import text


def diagnose_recognition_results(task_id: str):
    """诊断识别结果"""

    print("=" * 70)
    print(f"📊 诊断任务: {task_id}")
    print("=" * 70)

    with db_session() as session:
        # 1. 检查识别结果表
        print("\n1️⃣ 检查 dwg_recognition_results 表:\n")

        sql = text("""
            SELECT
                id,
                pdf_filename,
                status,
                SUBSTRING(markdown_content, 1, 100) as markdown_preview,
                LENGTH(markdown_content) as markdown_length,
                LENGTH(content_list) as content_list_length,
                error_message
            FROM dwg_recognition_results
            WHERE task_id = :task_id
            ORDER BY created_at
            LIMIT 5
        """)

        results = session.execute(sql, {"task_id": task_id}).fetchall()

        if not results:
            print("  ❌ 未找到识别记录！")
            print("  提示：请检查 task_id 是否正确")
            return

        print(f"  ✅ 找到 {len(results)} 条识别记录（显示前5条）\n")

        for row in results:
            print(f"  📄 {row.pdf_filename}")
            print(f"     状态: {row.status}")
            print(f"     Markdown 长度: {row.markdown_length or 0} 字符")
            print(f"     Content List 长度: {row.content_list_length or 0} 字符")

            if row.markdown_preview:
                print(f"     Markdown 预览: {row.markdown_preview}...")
            else:
                print(f"     ⚠️  Markdown 内容为空！")

            if row.error_message:
                print(f"     ❌ 错误: {row.error_message}")
            print()

        # 2. 检查图号表
        print("2️⃣ 检查 dwg_drawing_sheets 表:\n")

        sheets = session.query(DWGDrawingSheet).filter_by(task_id=task_id).all()

        if not sheets:
            print("  ❌ 未找到图纸记录！")
            print("  原因可能：")
            print("    - 识别结果中没有提取到图号")
            print("    - _extract_drawing_info() 方法未成功执行")
            print("    - 图号提取正则表达式不匹配")
        else:
            print(f"  ✅ 找到 {len(sheets)} 条图纸记录\n")

            has_sheet_number = 0
            no_sheet_number = 0

            for sheet in sheets[:5]:  # 显示前5条
                print(f"  📄 {sheet.pdf_filename}")
                print(f"     图号: {sheet.sheet_number or '❌ 无'}")
                print(f"     标题: {sheet.sheet_title or '无'}")
                print(f"     版本: {sheet.version or '无'}")
                print(f"     比例: {sheet.scale or '无'}")
                print()

                if sheet.sheet_number:
                    has_sheet_number += 1
                else:
                    no_sheet_number += 1

            print(f"  统计: 有图号 {has_sheet_number} 个, 无图号 {no_sheet_number} 个")

        # 3. 检查识别结果详情（第一个文件）
        print("\n3️⃣ 检查第一个 PDF 识别详情:\n")

        sql = text("""
            SELECT
                pdf_filename,
                markdown_content,
                content_list
            FROM dwg_recognition_results
            WHERE task_id = :task_id
            LIMIT 1
        """)

        first_result = session.execute(sql, {"task_id": task_id}).fetchone()

        if first_result:
            print(f"  📄 {first_result.pdf_filename}")
            print(f"\n  Markdown 内容 (前500字符):")
            print("  " + "-" * 66)
            if first_result.markdown_content:
                content = first_result.markdown_content[:500]
                for line in content.split('\n'):
                    print(f"  {line}")
            else:
                print("  ⚠️  无内容")
            print("  " + "-" * 66)

            print(f"\n  Content List (前500字符):")
            print("  " + "-" * 66)
            if first_result.content_list:
                import json
                try:
                    content_list = json.loads(first_result.content_list) if isinstance(first_result.content_list, str) else first_result.content_list
                    print(f"  类型: {type(content_list)}")
                    print(f"  长度: {len(content_list) if isinstance(content_list, list) else 'N/A'}")
                    if isinstance(content_list, list) and len(content_list) > 0:
                        print(f"  第一项: {content_list[0]}")
                except Exception as e:
                    print(f"  ⚠️  解析失败: {e}")
            else:
                print("  ⚠️  无内容")
            print("  " + "-" * 66)

        # 4. 建议
        print("\n" + "=" * 70)
        print("💡 诊断建议:")
        print("=" * 70)

        if not results:
            print("  ❌ 识别记录为空，请检查 MinerU 服务是否正常运行")
        elif not sheets:
            print("  ⚠️  图号提取失败，可能原因：")
            print("    1. PDF 内容格式不符合预期")
            print("    2. 图号提取正则表达式需要调整")
            print("    3. 查看上面的 Markdown 内容，检查是否包含图号信息")
            print("    4. 运行 test_drawing_extraction.py 测试提取逻辑")
        else:
            print("  ✅ 识别和提取正常")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/diagnose_reorganize_issue.py <task_id>")
        print("\n示例:")
        print("  python scripts/diagnose_reorganize_issue.py test_mineru_20251106_152700")
        sys.exit(1)

    task_id = sys.argv[1]
    diagnose_recognition_results(task_id)


if __name__ == '__main__':
    main()
