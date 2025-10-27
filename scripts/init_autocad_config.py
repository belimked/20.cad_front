"""
初始化 AutoCAD 配置表

创建配置表并插入示例配置

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import engine, SessionLocal, Base
from src.models.autocad_config import AutoCADConfig, AutoCADTaskLog
from src.services.autocad_config_service import AutoCADConfigService, create_default_config
import json


def init_tables():
    """创建表"""
    print("=" * 60)
    print("创建 AutoCAD 配置表")
    print("=" * 60)

    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("✅ 表创建成功")
        return True
    except Exception as e:
        print(f"❌ 表创建失败: {e}")
        return False


def create_sample_configs():
    """创建示例配置"""
    print("\n" + "=" * 60)
    print("创建示例配置")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 配置 1: 默认配置
        config1 = {
            'config_name': 'default',
            'description': '默认配置 - 适用于大多数情况',
            'autocad_version': '2014',
            'force_close_existing': True,
            'startup_wait_time': 10.0,
            'startup_check_interval': 1.0,
            'post_startup_wait': 2.0,
            'file_open_retry_delay': 3.0,
            'file_open_max_retries': 3,
            'verification_wait_time': 30.0,
            'verification_check_interval': 2.0,
            'menu_operations': [],
            'is_active': True,
        }

        # 配置 2: 快速模式（减少等待时间）
        config2 = {
            'config_name': 'fast',
            'description': '快速模式 - 适用于性能好的机器',
            'autocad_version': '2021',
            'force_close_existing': True,
            'startup_wait_time': 5.0,
            'startup_check_interval': 0.5,
            'post_startup_wait': 1.0,
            'file_open_retry_delay': 2.0,
            'file_open_max_retries': 2,
            'verification_wait_time': 15.0,
            'verification_check_interval': 1.0,
            'menu_operations': [],
            'is_active': False,
        }

        # 配置 3: 稳定模式（增加等待时间）
        config3 = {
            'config_name': 'stable',
            'description': '稳定模式 - 适用于旧版本或慢速机器',
            'autocad_version': '2014',
            'force_close_existing': True,
            'startup_wait_time': 20.0,
            'startup_check_interval': 1.0,
            'post_startup_wait': 5.0,
            'file_open_retry_delay': 5.0,
            'file_open_max_retries': 5,
            'verification_wait_time': 60.0,
            'verification_check_interval': 3.0,
            'menu_operations': [],
            'is_active': False,
        }

        # 配置 4: 带菜单操作的示例
        config4 = {
            'config_name': 'with_menu_operations',
            'description': '示例：包含菜单操作的配置',
            'autocad_version': '2014',
            'force_close_existing': True,
            'startup_wait_time': 10.0,
            'startup_check_interval': 1.0,
            'post_startup_wait': 2.0,
            'file_open_retry_delay': 3.0,
            'file_open_max_retries': 3,
            'verification_wait_time': 30.0,
            'verification_check_interval': 2.0,
            'menu_operations': [
                {"type": "command", "command": "ZOOM", "wait_time": 0.5},
                {"type": "command", "command": "E", "wait_time": 1.0},  # ZOOM Extents
            ],
            'is_active': False,
        }

        # 创建配置
        configs = [config1, config2, config3, config4]
        created = []

        for cfg in configs:
            try:
                # 检查是否已存在
                existing = service.get_config(config_name=cfg['config_name'])
                if existing:
                    print(f"⚠️  配置已存在: {cfg['config_name']}")
                    continue

                config = service.create_config(cfg)
                created.append(config)
                print(f"✅ 创建配置: {config.config_name}")
                print(f"   ID: {config.id}")
                print(f"   描述: {config.description}")
                print(f"   激活: {config.is_active}")

            except Exception as e:
                print(f"❌ 创建配置失败 ({cfg['config_name']}): {e}")

        print(f"\n✅ 成功创建 {len(created)} 个配置")
        return True

    except Exception as e:
        print(f"❌ 创建示例配置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


def show_configs():
    """显示所有配置"""
    print("\n" + "=" * 60)
    print("当前配置列表")
    print("=" * 60)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)
        configs = service.get_all_configs()

        if not configs:
            print("（无配置）")
            return

        for cfg in configs:
            print(f"\n【{cfg.id}】 {cfg.config_name}")
            print(f"  描述: {cfg.description}")
            print(f"  版本: {cfg.autocad_version}")
            print(f"  激活: {'是' if cfg.is_active else '否'}")
            print(f"  启动等待: {cfg.startup_wait_time}秒")
            print(f"  验证等待: {cfg.verification_wait_time}秒")

            # 菜单操作
            if cfg.menu_operations:
                try:
                    ops = json.loads(cfg.menu_operations)
                    print(f"  菜单操作: {len(ops)}个")
                except:
                    print(f"  菜单操作: 无法解析")

        print(f"\n✅ 共 {len(configs)} 个配置")

    finally:
        db.close()


def main():
    """主函数"""
    print("=" * 60)
    print("AutoCAD 配置初始化")
    print("=" * 60)

    # 1. 创建表
    if not init_tables():
        return

    # 2. 创建示例配置
    if not create_sample_configs():
        print("\n⚠️ 部分配置创建失败，但不影响使用")

    # 3. 显示配置
    show_configs()

    print("\n" + "=" * 60)
    print("✅ 初始化完成")
    print("=" * 60)

    print("\n💡 使用方法：")
    print("1. 查看配置: python scripts/autocad_config_manager.py list")
    print("2. 使用配置: python research/autocad_com_api/9_configurable_workflow.py")
    print("3. 修改配置: 直接在数据库中修改，或使用配置管理脚本")


if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 键退出...")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
