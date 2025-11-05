"""
测试 MinerU 集成

测试 MinerU PDF 识别功能是否正常工作

使用方法:
    # 1. 确保已初始化数据库表
    python scripts/init_mineru_tables.py

    # 2. 确保已更新配置
    python scripts/update_autocad_config_mineru.py

    # 3. 运行测试
    python scripts/test_mineru_integration.py

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig
from src.services.mineru_service import MinerUService


def test_mineru():
    """测试 MinerU 服务"""
    print("=" * 60)
    print("MinerU 集成测试")
    print("=" * 60)

    db = SessionLocal()
    try:
        # 1. 获取配置
        print("\n📋 步骤 1/4: 加载配置")
        config = db.query(AutoCADConfig).filter_by(config_name='default').first()

        if not config:
            print("❌ 配置不存在: default")
            print("💡 请先运行: python scripts/init_autocad_config.py")
            return

        print(f"✅ 配置已加载: {config.config_name}")

        # 2. 检查 MinerU 配置
        print("\n📋 步骤 2/4: 检查 MinerU 配置")
        if not hasattr(config, 'mineru_api_url') or not config.mineru_api_url:
            print("❌ MinerU 配置缺失")
            print("💡 请先运行: python scripts/update_autocad_config_mineru.py")
            return

        print(f"   MinerU API: {config.mineru_api_url}")
        print(f"   启用状态: {'✅ 启用' if config.mineru_enabled else '❌ 禁用'}")
        print(f"   批次大小: {config.mineru_batch_size}")
        print(f"   超时时间: {config.mineru_timeout_per_file} 秒/文件")

        # 3. 启用 MinerU（如果未启用）
        if not config.mineru_enabled:
            print("\n⚠️  MinerU 未启用，自动启用中...")
            config.mineru_enabled = True
            config.mineru_api_url = 'http://10.3.19.63:18080'  # 使用测试机器地址
            db.commit()
            print("✅ 已启用 MinerU")

        # 4. 创建 MinerU 服务
        print("\n📋 步骤 3/4: 创建 MinerU 服务")
        service = MinerUService(
            config=config,
            task_id='test_mineru_001',
            db_session=db
        )
        print(f"✅ MinerU 服务已创建")
        print(f"   API URL: {service.api_url}")
        print(f"   批次大小: {service.batch_size}")

        # 5. 测试识别（指定测试目录）
        print("\n📋 步骤 4/4: 测试 PDF 识别")
        test_pdf_dir = './data/pdf'  # 默认测试目录

        # 检查目录是否存在
        if not Path(test_pdf_dir).exists():
            print(f"⚠️  测试目录不存在: {test_pdf_dir}")
            print("\n💡 请指定包含 PDF 文件的目录进行测试")
            print("   修改此脚本中的 test_pdf_dir 变量")
            print("\n示例:")
            print("   test_pdf_dir = 'F:/cad/caddd/cadpython/CAD_AutoProcessor/outputs'")
            return

        print(f"   测试目录: {test_pdf_dir}")
        print(f"   开始识别...\n")

        result = service.batch_recognize_pdfs(test_pdf_dir)

        # 6. 显示结果
        print("\n" + "=" * 60)
        print("识别结果:")
        print("=" * 60)
        print(f"✅ 总文件数: {result.get('total_files', 0)}")
        print(f"✅ 成功: {result.get('success_count', 0)}")
        print(f"❌ 失败: {result.get('failed_count', 0)}")

        if result.get('results'):
            print("\n详细结果:")
            for i, r in enumerate(result.get('results', []), 1):
                status = "✅" if r.get('success') else "❌"
                pdf_file = Path(r.get('pdf_file', '')).name
                print(f"  {i}. {status} {pdf_file}")
                if r.get('drawing_info'):
                    info = r['drawing_info']
                    if info.get('sheet_number'):
                        print(f"     图号: {info['sheet_number']}")
                    if info.get('version'):
                        print(f"     版本: {info['version']}")
                    if info.get('scale'):
                        print(f"     比例: {info['scale']}")
                if not r.get('success') and r.get('error'):
                    print(f"     错误: {r['error']}")

        print("\n" + "=" * 60)
        print("✅ 测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    test_mineru()
