"""
PDF 文件重组织服务单元测试

测试 PDFReorganizeService 的核心功能：
- 目录创建
- 文件重命名
- 冲突处理
- 数据库更新

使用方法：
    python scripts/test_pdf_reorganize.py

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from src.models.dwg_drawing_sheet import DWGDrawingSheet
from src.services.pdf_reorganize_service import PDFReorganizeService
from src.utils.logger import get_logger

logger = get_logger()


def setup_test_environment():
    """创建测试环境"""
    print("=" * 70)
    print("📦 创建测试环境")
    print("=" * 70)

    # 创建测试目录
    test_dir = project_root / 'data' / 'test_reorganize'
    test_dir.mkdir(parents=True, exist_ok=True)

    # 创建测试 PDF 文件（空文件）
    test_pdfs = [
        test_dir / 'tz001.pdf',
        test_dir / 'tz002.pdf',
        test_dir / 'tz003.pdf',
        test_dir / 'tz004.pdf',  # 无图号
        test_dir / 'tz005.pdf',  # 重复图号
    ]

    for pdf_file in test_pdfs:
        pdf_file.touch()
        print(f"  ✅ 创建测试文件: {pdf_file.name}")

    print(f"\n📁 测试目录: {test_dir}\n")
    return test_dir


def create_test_data(test_dir: Path, task_id: str):
    """创建测试数据库记录"""
    print("=" * 70)
    print("📊 创建测试数据")
    print("=" * 70)

    sheets = [
        {
            'task_id': task_id,
            'pdf_filename': 'tz001.pdf',
            'pdf_path': str(test_dir / 'tz001.pdf'),
            'sheet_number': 'PCX-01-01-03-01-1',
            'sheet_title': '材料: 80x80钢块(Q235B)',
        },
        {
            'task_id': task_id,
            'pdf_filename': 'tz002.pdf',
            'pdf_path': str(test_dir / 'tz002.pdf'),
            'sheet_number': 'PCX-01-01-03-01-2',
            'sheet_title': '材料: 见列表',
        },
        {
            'task_id': task_id,
            'pdf_filename': 'tz003.pdf',
            'pdf_path': str(test_dir / 'tz003.pdf'),
            'sheet_number': 'PCX-01-01-03-01-3',
            'sheet_title': '材料: 不锈钢 304',
        },
        {
            'task_id': task_id,
            'pdf_filename': 'tz004.pdf',
            'pdf_path': str(test_dir / 'tz004.pdf'),
            'sheet_number': None,  # 无图号
            'sheet_title': '测试无图号文件',
        },
        {
            'task_id': task_id,
            'pdf_filename': 'tz005.pdf',
            'pdf_path': str(test_dir / 'tz005.pdf'),
            'sheet_number': 'PCX-01-01-03-01-1',  # 重复图号
            'sheet_title': '材料: 铝合金 6061',
        },
    ]

    with db_session() as session:
        created_sheets = []
        for data in sheets:
            sheet = DWGDrawingSheet(**data)
            session.add(sheet)
            created_sheets.append(sheet)

        session.commit()

        for sheet in created_sheets:
            print(f"  ✅ {sheet.pdf_filename}: sheet_number={sheet.sheet_number}")

    print()
    return created_sheets


def test_reorganize_service(test_dir: Path, task_id: str):
    """测试重组织服务"""
    print("=" * 70)
    print("🧪 测试 PDFReorganizeService")
    print("=" * 70)

    with db_session() as session:
        # 查询测试数据
        sheets = session.query(DWGDrawingSheet).filter_by(task_id=task_id).all()

        # 调用服务
        service = PDFReorganizeService(session)
        result = service.reorganize_pdfs(sheets, str(test_dir))

        print("\n📊 重组织结果:\n")
        print(f"  成功: {result.get('success')}")
        print(f"  总文件数: {result.get('total_files')}")
        print(f"  已完成: {result.get('completed')}")
        print(f"  已跳过: {result.get('skipped')}")
        print(f"  失败: {result.get('failed')}")
        print(f"  转换目录: {result.get('convert_directory')}")

        print("\n📋 详细结果:\n")
        for detail in result.get('details', []):
            status = detail['status']
            symbol = '✅' if status == 'completed' else '⚠️' if status == 'skipped' else '❌'
            print(f"  {symbol} {detail.get('pdf_filename')} -> {detail.get('new_filename', 'N/A')}")
            if 'reason' in detail:
                print(f"     原因: {detail['reason']}")
            if 'error' in detail:
                print(f"     错误: {detail['error']}")

        return result


def verify_results(test_dir: Path, task_id: str, result: dict):
    """验证结果"""
    print("\n" + "=" * 70)
    print("✅ 验证结果")
    print("=" * 70)

    convert_dir = Path(result['convert_directory'])

    # 验证转换目录存在
    assert convert_dir.exists(), "转换目录不存在"
    print(f"  ✅ 转换目录已创建: {convert_dir}")

    # 验证文件重命名
    expected_files = [
        'PCX-01-01-03-01-1.pdf',
        'PCX-01-01-03-01-2.pdf',
        'PCX-01-01-03-01-3.pdf',
        'PCX-01-01-03-01-1_1.pdf',  # 重复图号（追加序号）
    ]

    for filename in expected_files:
        file_path = convert_dir / filename
        if file_path.exists():
            print(f"  ✅ 文件存在: {filename}")
        else:
            print(f"  ❌ 文件缺失: {filename}")

    # 验证数据库更新
    with db_session() as session:
        sheets = session.query(DWGDrawingSheet).filter_by(task_id=task_id).all()

        print("\n📊 数据库记录验证:\n")
        for sheet in sheets:
            if sheet.conversion_status == DWGDrawingSheet.CONVERSION_STATUS_COMPLETED:
                print(f"  ✅ {sheet.pdf_filename}")
                print(f"     converted_filename: {sheet.converted_filename}")
                print(f"     conversion_status: {sheet.conversion_status}")
            elif sheet.conversion_status == DWGDrawingSheet.CONVERSION_STATUS_SKIPPED:
                print(f"  ⚠️  {sheet.pdf_filename} (跳过: {sheet.conversion_error})")
            else:
                print(f"  ❌ {sheet.pdf_filename} (失败: {sheet.conversion_error})")

    print("\n🎉 验证通过！")


def cleanup_test_environment(test_dir: Path, task_id: str):
    """清理测试环境"""
    print("\n" + "=" * 70)
    print("🧹 清理测试环境")
    print("=" * 70)

    # 删除测试目录
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"  ✅ 删除测试目录: {test_dir}")

    # 删除转换目录
    convert_dir = test_dir.parent / f"{test_dir.name}_convert"
    if convert_dir.exists():
        shutil.rmtree(convert_dir)
        print(f"  ✅ 删除转换目录: {convert_dir}")

    # 删除数据库记录
    with db_session() as session:
        deleted = session.query(DWGDrawingSheet).filter_by(task_id=task_id).delete()
        session.commit()
        print(f"  ✅ 删除数据库记录: {deleted} 条")

    print("\n🎉 清理完成！")


def main():
    """主函数"""
    task_id = f"test_reorganize_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # 1. 创建测试环境
        test_dir = setup_test_environment()

        # 2. 创建测试数据
        create_test_data(test_dir, task_id)

        # 3. 执行测试
        result = test_reorganize_service(test_dir, task_id)

        # 4. 验证结果
        verify_results(test_dir, task_id, result)

        # 5. 清理环境
        cleanup_test_environment(test_dir, task_id)

        print("\n" + "=" * 70)
        print("🎉 所有测试通过！")
        print("=" * 70)

    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
