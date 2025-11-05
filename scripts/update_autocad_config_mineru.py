"""
为 AutoCAD 配置添加 MinerU 默认值

运行此脚本为现有的 AutoCAD 配置添加 MinerU 相关字段的默认值

使用方法:
    python scripts/update_autocad_config_mineru.py

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


def update_config_with_mineru():
    """更新配置增加 MinerU 字段"""
    print("=" * 60)
    print("更新 AutoCAD 配置 - 添加 MinerU 字段")
    print("=" * 60)

    db = SessionLocal()
    try:
        configs = db.query(AutoCADConfig).all()

        if not configs:
            print("\n⚠️  未找到任何配置")
            return

        print(f"\n找到 {len(configs)} 个配置")

        for config in configs:
            updated = False

            # 设置默认值（如果字段不存在或为空）
            if not hasattr(config, 'mineru_api_url') or not config.mineru_api_url:
                config.mineru_api_url = 'http://127.0.0.1:18080'
                updated = True

            if not hasattr(config, 'mineru_enabled') or config.mineru_enabled is None:
                config.mineru_enabled = False  # 默认禁用，需要手动开启
                updated = True

            if not hasattr(config, 'mineru_timeout_per_file') or not config.mineru_timeout_per_file:
                config.mineru_timeout_per_file = 30
                updated = True

            if not hasattr(config, 'mineru_pdf_render_timeout') or not config.mineru_pdf_render_timeout:
                config.mineru_pdf_render_timeout = 300
                updated = True

            if not hasattr(config, 'mineru_batch_size') or not config.mineru_batch_size:
                config.mineru_batch_size = 10
                updated = True

            if not hasattr(config, 'mineru_lang_list') or not config.mineru_lang_list:
                config.mineru_lang_list = '["ch"]'
                updated = True

            if not hasattr(config, 'mineru_parse_method') or not config.mineru_parse_method:
                config.mineru_parse_method = 'auto'
                updated = True

            if not hasattr(config, 'mineru_table_enable') or config.mineru_table_enable is None:
                config.mineru_table_enable = True
                updated = True

            if not hasattr(config, 'mineru_return_md') or config.mineru_return_md is None:
                config.mineru_return_md = True
                updated = True

            if not hasattr(config, 'mineru_return_content_list') or config.mineru_return_content_list is None:
                config.mineru_return_content_list = True
                updated = True

            if updated:
                print(f"✅ 更新配置: {config.config_name}")
                print(f"   - API 地址: {config.mineru_api_url}")
                print(f"   - 启用状态: {'✅ 启用' if config.mineru_enabled else '❌ 禁用'}")
                print(f"   - 批次大小: {config.mineru_batch_size}")
            else:
                print(f"⏭️  配置已是最新: {config.config_name}")

        db.commit()
        print("\n" + "=" * 60)
        print("✅ 所有配置已更新")
        print("=" * 60)

        print("\n💡 提示:")
        print("   - MinerU 默认为禁用状态")
        print("   - 请在数据库中将 mineru_enabled 设置为 TRUE 以启用")
        print("   - 或使用 autocad_config_manager.py 工具修改配置")

    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    update_config_with_mineru()
