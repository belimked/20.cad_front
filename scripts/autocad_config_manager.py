"""
AutoCAD 配置管理工具

命令行工具，用于管理 AutoCAD 自动化配置

Author: CAD Auto Processor Team
Date: 2025-10-24

使用方法:
    python scripts/autocad_config_manager.py list
    python scripts/autocad_config_manager.py show <config_id>
    python scripts/autocad_config_manager.py activate <config_id>
    python scripts/autocad_config_manager.py update <config_id> --field <value>
"""

import sys
import argparse
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService


def list_configs(args):
    """列出所有配置"""
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)
        configs = service.get_all_configs(active_only=args.active_only)

        if not configs:
            print("（无配置）")
            return

        print("=" * 80)
        print(f"AutoCAD 配置列表（共 {len(configs)} 个）")
        print("=" * 80)

        for cfg in configs:
            status = "●" if cfg.is_active else "○"
            print(f"\n{status} [{cfg.id}] {cfg.config_name}")
            print(f"  描述: {cfg.description}")
            print(f"  版本: {cfg.autocad_version or '自动检测'}")
            print(f"  启动等待: {cfg.startup_wait_time}秒")
            print(f"  文件打开重试: {cfg.file_open_max_retries}次")

    finally:
        db.close()


def show_config(args):
    """显示配置详情"""
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)
        config = service.get_config(config_id=args.config_id)

        if not config:
            print(f"❌ 配置不存在: ID={args.config_id}")
            return

        print("=" * 80)
        print(f"配置详情: {config.config_name}")
        print("=" * 80)

        # 基本信息
        print(f"\n【基本信息】")
        print(f"  ID: {config.id}")
        print(f"  名称: {config.config_name}")
        print(f"  描述: {config.description}")
        print(f"  激活: {'是' if config.is_active else '否'}")
        print(f"  创建时间: {config.created_at}")
        print(f"  更新时间: {config.updated_at}")

        # CAD 配置
        print(f"\n【CAD 配置】")
        print(f"  版本: {config.autocad_version or '自动检测'}")
        print(f"  可执行文件: {config.autocad_exe_path or '自动查找'}")
        print(f"  强制关闭现有进程: {'是' if config.force_close_existing else '否'}")

        # 文件配置
        print(f"\n【文件配置】")
        print(f"  默认文件路径: {config.dwg_file_path or '(使用时指定)'}")

        # 延迟配置
        print(f"\n【延迟配置】")
        print(f"  启动等待时间: {config.startup_wait_time}秒")
        print(f"  启动检查间隔: {config.startup_check_interval}秒")
        print(f"  启动后额外等待: {config.post_startup_wait}秒")
        print(f"  文件打开重试延迟: {config.file_open_retry_delay}秒")
        print(f"  文件打开最大重试: {config.file_open_max_retries}次")
        print(f"  验证等待时间: {config.verification_wait_time}秒")
        print(f"  验证检查间隔: {config.verification_check_interval}秒")

        # 菜单操作
        print(f"\n【菜单操作】")
        if config.menu_operations:
            try:
                ops = json.loads(config.menu_operations)
                if ops:
                    for i, op in enumerate(ops, 1):
                        print(f"  {i}. {op}")
                else:
                    print("  （无）")
            except:
                print(f"  （解析失败）")
        else:
            print("  （无）")

    finally:
        db.close()


def activate_config(args):
    """激活配置"""
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 停用所有配置
        all_configs = service.get_all_configs()
        for cfg in all_configs:
            if cfg.is_active:
                service.update_config(cfg.id, {'is_active': False})

        # 激活指定配置
        config = service.update_config(args.config_id, {'is_active': True})

        if config:
            print(f"✅ 已激活配置: {config.config_name}")
        else:
            print(f"❌ 配置不存在: ID={args.config_id}")

    finally:
        db.close()


def update_config(args):
    """更新配置"""
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 构建更新数据
        update_data = {}

        if args.startup_wait:
            update_data['startup_wait_time'] = float(args.startup_wait)

        if args.verification_wait:
            update_data['verification_wait_time'] = float(args.verification_wait)

        if args.retry_count:
            update_data['file_open_max_retries'] = int(args.retry_count)

        if args.description:
            update_data['description'] = args.description

        # 新增：文件路径和AutoCAD配置
        if args.dwg_file:
            update_data['dwg_file_path'] = args.dwg_file

        if args.autocad_path:
            update_data['autocad_exe_path'] = args.autocad_path

        if args.autocad_version:
            update_data['autocad_version'] = args.autocad_version

        if not update_data:
            print("❌ 未指定要更新的字段")
            return

        config = service.update_config(args.config_id, update_data)

        if config:
            print(f"✅ 已更新配置: {config.config_name}")
            for key, value in update_data.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ 配置不存在: ID={args.config_id}")

    finally:
        db.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AutoCAD 配置管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # list 命令
    parser_list = subparsers.add_parser('list', help='列出所有配置')
    parser_list.add_argument('--active-only', action='store_true', help='仅显示激活的配置')
    parser_list.set_defaults(func=list_configs)

    # show 命令
    parser_show = subparsers.add_parser('show', help='显示配置详情')
    parser_show.add_argument('config_id', type=int, help='配置ID')
    parser_show.set_defaults(func=show_config)

    # activate 命令
    parser_activate = subparsers.add_parser('activate', help='激活配置')
    parser_activate.add_argument('config_id', type=int, help='配置ID')
    parser_activate.set_defaults(func=activate_config)

    # update 命令
    parser_update = subparsers.add_parser('update', help='更新配置')
    parser_update.add_argument('config_id', type=int, help='配置ID')
    parser_update.add_argument('--startup-wait', type=float, help='启动等待时间（秒）')
    parser_update.add_argument('--verification-wait', type=float, help='验证等待时间（秒）')
    parser_update.add_argument('--retry-count', type=int, help='文件打开重试次数')
    parser_update.add_argument('--description', type=str, help='配置描述')
    parser_update.add_argument('--dwg-file', type=str, help='DWG文件路径')
    parser_update.add_argument('--autocad-path', type=str, help='AutoCAD可执行文件路径')
    parser_update.add_argument('--autocad-version', type=str, help='AutoCAD版本（如2014、2021）')
    parser_update.set_defaults(func=update_config)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    try:
        args.func(args)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
