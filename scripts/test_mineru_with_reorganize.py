"""
MinerU + PDF 重组织集成测试

测试完整流程：
1. MinerU PDF 识别
2. 自动触发文件重组织
3. 验证最终结果

使用方法：
    python scripts/test_mineru_with_reorganize.py <pdf_directory>

示例：
    python scripts/test_mineru_with_reorganize.py ./output

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from src.models.autocad_config import AutoCADConfig
from src.models.dwg_drawing_sheet import DWGDrawingSheet
from src.services.mineru_service import MinerUService
from src.utils.logger import get_logger

logger = get_logger()


def test_mineru_with_reorganize(pdf_directory: str, config_name: str = 'default'):
    """测试 MinerU 识别 + PDF 重组织

    Args:
        pdf_directory: PDF 文件目录
        config_name: AutoCAD 配置名称（默认 'default'）
    """
    print("=" * 70)
    print("🧪 MinerU + PDF 重组织集成测试")
    print("=" * 70)

    task_id = f"test_mineru_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        with db_session() as session:
            # 1. 加载 AutoCAD 配置
            config = session.query(AutoCADConfig).filter_by(config_name=config_name).first()

            if not config:
                print(f"❌ 未找到配置: {config_name}")
                return False

            print(f"\n📋 使用配置: {config_name}")
            print(f"  - MinerU 服务: {config.mineru_api_url}")
            print(f"  - 自动重组织: {config.auto_reorganize_pdfs}")

            if not config.auto_reorganize_pdfs:
                print(f"\n⚠️  警告: auto_reorganize_pdfs = False，不会执行重组织")

            # 2. 创建 MinerU 服务
            print(f"\n🚀 启动 MinerU 服务...")
            service = MinerUService(config=config, task_id=task_id, db_session=session)

            # 3. 执行批量识别（自动触发重组织）
            print(f"\n📂 处理目录: {pdf_directory}\n")
            result = service.batch_recognize_pdfs(pdf_directory=pdf_directory)

            # 4. 显示识别结果
            print("\n" + "=" * 70)
            print("📊 识别结果统计")
            print("=" * 70)
            print(f"  成功: {result.get('success')}")
            print(f"  总文件数: {result.get('total_files')}")
            print(f"  成功数: {result.get('success_count')}")
            print(f"  失败数: {result.get('failed_count')}")

            # 5. 显示重组织结果
            if 'reorganize_stats' in result:
                print("\n" + "=" * 70)
                print("📁 重组织结果统计")
                print("=" * 70)

                reorg = result['reorganize_stats']
                print(f"  成功: {reorg.get('success')}")
                print(f"  总文件数: {reorg.get('total_files')}")
                print(f"  已完成: {reorg.get('completed')}")
                print(f"  已跳过: {reorg.get('skipped')}")
                print(f"  失败: {reorg.get('failed')}")
                print(f"  转换目录: {reorg.get('convert_directory')}")

                if 'details' in reorg:
                    print("\n📋 详细结果:\n")
                    for detail in reorg['details']:
                        status = detail['status']
                        symbol = '✅' if status == 'completed' else '⚠️' if status == 'skipped' else '❌'
                        print(f"  {symbol} {detail.get('pdf_filename')} -> {detail.get('new_filename', 'N/A')}")
                        if 'reason' in detail:
                            print(f"     原因: {detail['reason']}")
                        if 'error' in detail:
                            print(f"     错误: {detail['error']}")
            else:
                print("\n⚠️  未执行重组织（可能未启用或无有效图号）")

            # 6. 查询数据库验证
            print("\n" + "=" * 70)
            print("📊 数据库记录验证")
            print("=" * 70)

            sheets = session.query(DWGDrawingSheet).filter_by(task_id=task_id).all()

            if sheets:
                print(f"\n找到 {len(sheets)} 条图纸记录:\n")
                for sheet in sheets:
                    print(f"  📄 {sheet.pdf_filename}")
                    print(f"     图号: {sheet.sheet_number or '无'}")
                    print(f"     标题: {sheet.sheet_title or '无'}")
                    print(f"     转换状态: {sheet.conversion_status}")
                    if sheet.converted_filename:
                        print(f"     新文件名: {sheet.converted_filename}")
                    if sheet.conversion_error:
                        print(f"     错误: {sheet.conversion_error}")
                    print()
            else:
                print("  ⚠️  未找到图纸记录")

            print("=" * 70)
            print("🎉 集成测试完成！")
            print("=" * 70)

            return result.get('success', False)

    except Exception as e:
        logger.error(f"集成测试失败: {e}", exc_info=True)
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MinerU + PDF 重组织集成测试')
    parser.add_argument('pdf_directory', type=str, help='PDF 文件目录')
    parser.add_argument('--config', type=str, default='default', help='AutoCAD 配置名称（默认 default）')

    args = parser.parse_args()

    # 验证目录存在
    pdf_dir = Path(args.pdf_directory)
    if not pdf_dir.exists():
        print(f"❌ 目录不存在: {args.pdf_directory}")
        sys.exit(1)

    # 检查是否有 PDF 文件
    pdf_files = list(pdf_dir.glob('*.pdf'))
    if not pdf_files:
        print(f"❌ 目录中无 PDF 文件: {args.pdf_directory}")
        sys.exit(1)

    print(f"📂 找到 {len(pdf_files)} 个 PDF 文件")

    # 执行测试
    success = test_mineru_with_reorganize(
        pdf_directory=args.pdf_directory,
        config_name=args.config
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
