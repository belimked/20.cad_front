"""
配置更新：为 AutoCAD 配置新增 auto_reorganize_pdfs 字段

功能：
- 为所有 AutoCAD 配置新增 auto_reorganize_pdfs 字段（默认 True）
- 允许单独配置是否启用 PDF 文件重组织功能

使用方法：
    python scripts/update_autocad_config_reorganize.py

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import db_session
from src.models.autocad_config import AutoCADConfig
from src.utils.logger import get_logger

logger = get_logger()


def update_all_configs():
    """为所有配置新增 auto_reorganize_pdfs 字段"""

    print("=" * 70)
    print("AutoCAD 配置更新：新增 auto_reorganize_pdfs 字段")
    print("=" * 70)

    try:
        with db_session() as session:
            # 查询所有配置
            configs = session.query(AutoCADConfig).all()

            if not configs:
                print("\n⚠️  未找到 AutoCAD 配置，请先运行 init_autocad_config.py")
                return False

            print(f"\n📋 找到 {len(configs)} 个配置\n")

            updated_count = 0
            skipped_count = 0

            for config in configs:
                # 检查是否已有该字段
                if hasattr(config, 'auto_reorganize_pdfs') and config.auto_reorganize_pdfs is not None:
                    print(f"  ⚠️  {config.config_name}: 已有 auto_reorganize_pdfs 字段 (跳过)")
                    skipped_count += 1
                    continue

                # 新增字段，默认启用
                config.auto_reorganize_pdfs = True
                updated_count += 1
                print(f"  ✅ {config.config_name}: 已设置 auto_reorganize_pdfs = True")

            # 提交更改
            session.commit()

            print("\n" + "=" * 70)
            print(f"🎉 更新完成！")
            print(f"   - 已更新: {updated_count} 个配置")
            print(f"   - 已跳过: {skipped_count} 个配置")
            print("=" * 70)

            # 显示当前配置状态
            print("\n📊 当前配置状态:\n")
            for config in configs:
                status = "✅ 启用" if config.auto_reorganize_pdfs else "❌ 禁用"
                print(f"  {config.config_name}: {status}")

            return True

    except Exception as e:
        logger.error(f"更新配置失败: {e}", exc_info=True)
        print(f"\n❌ 更新失败: {e}")
        return False


def set_config_reorganize(config_name: str, enable: bool):
    """设置特定配置的 auto_reorganize_pdfs 字段

    Args:
        config_name: 配置名称
        enable: 是否启用重组织功能
    """
    try:
        with db_session() as session:
            config = session.query(AutoCADConfig).filter_by(config_name=config_name).first()

            if not config:
                print(f"❌ 未找到配置: {config_name}")
                return False

            config.auto_reorganize_pdfs = enable
            session.commit()

            status = "启用" if enable else "禁用"
            print(f"✅ 已{status} {config_name} 的 PDF 重组织功能")
            return True

    except Exception as e:
        logger.error(f"设置配置失败: {e}", exc_info=True)
        print(f"❌ 设置失败: {e}")
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='管理 AutoCAD 配置的 PDF 重组织功能')
    parser.add_argument('--config', type=str, help='特定配置名称')
    parser.add_argument('--enable', action='store_true', help='启用重组织')
    parser.add_argument('--disable', action='store_true', help='禁用重组织')

    args = parser.parse_args()

    if args.config:
        # 设置特定配置
        if args.enable and args.disable:
            print("❌ --enable 和 --disable 不能同时使用")
            sys.exit(1)

        enable = True if args.enable else False if args.disable else None

        if enable is None:
            print("❌ 必须指定 --enable 或 --disable")
            sys.exit(1)

        success = set_config_reorganize(args.config, enable)
    else:
        # 批量更新所有配置
        success = update_all_configs()

    sys.exit(0 if success else 1)
