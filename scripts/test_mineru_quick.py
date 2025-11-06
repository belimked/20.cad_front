"""
MinerU 快速集成测试

仅测试前 N 个 PDF 文件，验证材料提取功能

使用方法:
    python scripts/test_mineru_quick.py [数量]

示例:
    python scripts/test_mineru_quick.py 5    # 测试前 5 个
    python scripts/test_mineru_quick.py 10   # 测试前 10 个

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


def test_mineru_quick(test_count=5):
    """快速测试 MinerU 服务

    Args:
        test_count: 测试文件数量（默认 5）
    """
    print("=" * 70)
    print(f"MinerU 快速集成测试（前 {test_count} 个文件）")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. 获取配置
        print("\n📋 步骤 1/4: 加载配置")
        config = db.query(AutoCADConfig).filter_by(config_name='default').first()

        if not config:
            print("❌ 配置不存在: default")
            print("💡 请先运行: python scripts/init_autocad_config.py")
            return False

        print(f"✅ 配置已加载: {config.config_name}")

        # 2. 检查 MinerU 配置
        print("\n📋 步骤 2/4: 检查 MinerU 配置")
        if not hasattr(config, 'mineru_api_url') or not config.mineru_api_url:
            print("❌ MinerU 配置缺失")
            print("💡 请先运行: python scripts/update_autocad_config_mineru.py")
            return False

        print(f"   MinerU API: {config.mineru_api_url}")
        print(f"   启用状态: {'✅ 启用' if config.mineru_enabled else '❌ 禁用'}")
        print(f"   批次大小: {config.mineru_batch_size}")
        print(f"   超时时间: {config.mineru_timeout_per_file} 秒/文件")

        # 3. 检查 API 连接
        print("\n📋 步骤 3/4: 检查 MinerU API 连接")
        import requests
        try:
            # 测试连接（使用 health 或 根路径）
            test_url = config.mineru_api_url.rstrip('/') + '/'
            response = requests.get(test_url, timeout=5)
            print(f"   ✅ API 连接正常 (HTTP {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  API 连接失败: {e}")
            print(f"   💡 请确认 MinerU 服务运行在: {config.mineru_api_url}")
            print("   继续测试...")

        # 4. 创建临时测试目录
        print("\n📋 步骤 4/4: 准备测试文件")
        test_dir = Path('./data/pdf_test_temp')
        test_dir.mkdir(exist_ok=True)

        # 复制前 N 个文件到临时目录
        source_dir = Path('./data/pdf')
        pdf_files = sorted(source_dir.glob('*.pdf'))[:test_count]

        if not pdf_files:
            print(f"❌ 未找到 PDF 文件: {source_dir}")
            return False

        print(f"   📁 源目录: {source_dir}")
        print(f"   📁 临时目录: {test_dir}")
        print(f"   📄 复制 {len(pdf_files)} 个文件...")

        import shutil
        for pdf in pdf_files:
            dest = test_dir / pdf.name
            if not dest.exists():
                shutil.copy2(pdf, dest)
                print(f"      ✅ {pdf.name}")

        # 5. 创建 MinerU 服务
        print("\n" + "=" * 70)
        print("开始识别测试")
        print("=" * 70)

        service = MinerUService(
            config=config,
            task_id=f'test_quick_{test_count}',
            db_session=db
        )

        # 6. 执行识别
        result = service.batch_recognize_pdfs(str(test_dir))

        # 7. 显示结果
        print("\n" + "=" * 70)
        print("识别结果:")
        print("=" * 70)
        print(f"✅ 总文件数: {result.get('total_files', 0)}")
        print(f"✅ 成功: {result.get('success_count', 0)}")
        print(f"❌ 失败: {result.get('failed_count', 0)}")

        if result.get('results'):
            print("\n📊 详细结果:")
            for i, r in enumerate(result.get('results', []), 1):
                status = "✅" if r.get('success') else "❌"
                pdf_file = Path(r.get('pdf_file', '')).name
                print(f"\n  {i}. {status} {pdf_file}")

                if r.get('success'):
                    # 显示提取的信息
                    info = r.get('drawing_info', {})
                    if info:
                        if info.get('sheet_number'):
                            print(f"     📋 图号: {info['sheet_number']}")
                        if info.get('sheet_title'):
                            # 高亮材料信息（如果是材料开头）
                            title = info['sheet_title']
                            if title.startswith('材料:') or 'Material:' in title:
                                print(f"     🔧 材料: {title} ⭐")  # 标记材料信息
                            else:
                                print(f"     📝 标题: {title}")
                        if info.get('version'):
                            print(f"     🔖 版本: {info['version']}")
                        if info.get('scale'):
                            print(f"     📏 比例: {info['scale']}")

                    # 显示表格和技术要求状态
                    if r.get('has_tables'):
                        print(f"     ✅ 包含表格数据")
                    if r.get('has_tech_requirements'):
                        print(f"     ✅ 包含技术要求")
                else:
                    if r.get('error'):
                        print(f"     ❌ 错误: {r['error']}")

        # 8. 清理临时目录
        print("\n🧹 清理临时文件...")
        shutil.rmtree(test_dir, ignore_errors=True)
        print("   ✅ 已清理")

        print("\n" + "=" * 70)
        if result.get('success_count', 0) > 0:
            print("✅ 测试完成 - 材料提取功能正常")
        else:
            print("⚠️  测试完成 - 但所有识别都失败了")
        print("=" * 70)

        return result.get('success_count', 0) > 0

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == '__main__':
    # 从命令行参数获取测试数量
    test_count = 5  # 默认 5 个
    if len(sys.argv) > 1:
        try:
            test_count = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  无效的数量参数: {sys.argv[1]}，使用默认值 5")

    success = test_mineru_quick(test_count)
    exit(0 if success else 1)
