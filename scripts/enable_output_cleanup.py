"""
启用输出目录清理功能

为指定配置启用输出目录清理功能

Author: 老王
Date: 2025-10-28
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig


def enable_output_cleanup(config_name='default',
                          output_dir=r'F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs',
                          backup_enabled=False,
                          backup_dir=None):
    """启用输出目录清理功能"""

    db = SessionLocal()
    try:
        # 查找配置
        config = db.query(AutoCADConfig).filter_by(config_name=config_name).first()

        if not config:
            print(f"❌ 错误：未找到配置 '{config_name}'")
            return False

        print(f"✅ 找到配置: {config.config_name} (ID: {config.id})")
        print()

        # 更新配置
        config.output_dir_cleanup_enabled = True
        config.output_dir_path = output_dir
        config.output_dir_backup_before_cleanup = backup_enabled
        if backup_dir:
            config.output_dir_backup_path = backup_dir

        db.commit()

        print("✅ 配置已更新!")
        print()
        print("📋 输出目录清理配置:")
        print(f"  启用状态: ✅ 已启用")
        print(f"  输出目录: {config.output_dir_path}")
        print(f"  清理前备份: {'✅ 是' if config.output_dir_backup_before_cleanup else '❌ 否'}")
        if config.output_dir_backup_path:
            print(f"  备份目录: {config.output_dir_backup_path}")
        else:
            print(f"  备份目录: （自动生成）")

        print("\n" + "=" * 80)
        print("✅ 完成！下次运行工作流程时会自动清理输出目录")
        print("   python research/autocad_com_api/9_configurable_workflow.py")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 80)
    print("启用输出目录清理功能")
    print("=" * 80)
    print()

    # 解析命令行参数
    import argparse

    parser = argparse.ArgumentParser(description='启用输出目录清理功能')
    parser.add_argument('--config', type=str, default='default',
                        help='配置名称 (默认: default)')
    parser.add_argument('--output-dir', type=str,
                        default=r'F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs',
                        help='输出目录路径')
    parser.add_argument('--backup', action='store_true',
                        help='清理前备份')
    parser.add_argument('--backup-dir', type=str,
                        help='备份目录路径（可选，默认自动生成）')

    args = parser.parse_args()

    success = enable_output_cleanup(
        config_name=args.config,
        output_dir=args.output_dir,
        backup_enabled=args.backup,
        backup_dir=args.backup_dir
    )

    sys.exit(0 if success else 1)
