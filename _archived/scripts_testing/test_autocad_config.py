"""
测试数据库配置系统

验证配置的创建、读取、更新和删除功能

Author: CAD Auto Processor Team
Date: 2025-10-26
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService


def test_config_crud():
    """测试配置的增删改查"""
    print("=" * 80)
    print("测试配置 CRUD 操作")
    print("=" * 80)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 1. 创建测试配置
        print("\n【测试 1】创建配置")
        test_config = {
            'config_name': 'test_config',
            'description': '测试配置',
            'autocad_version': '2014',
            'startup_wait_time': 12.0,
            'verification_wait_time': 35.0,
            'file_open_max_retries': 4,
            'menu_operations': [
                {"type": "command", "command": "ZOOM", "wait_time": 0.5}
            ],
            'is_active': False
        }

        config = service.create_config(test_config)
        print(f"✅ 创建成功: ID={config.id}, Name={config.config_name}")

        # 2. 读取配置
        print("\n【测试 2】读取配置")

        # 按 ID 读取
        config_by_id = service.get_config(config_id=config.id)
        print(f"✅ 按 ID 读取: {config_by_id.config_name}")

        # 按名称读取
        config_by_name = service.get_config(config_name='test_config')
        print(f"✅ 按名称读取: {config_by_name.config_name}")

        # 验证数据
        assert config_by_id.startup_wait_time == 12.0
        assert config_by_id.file_open_max_retries == 4
        print("✅ 数据验证通过")

        # 3. 更新配置
        print("\n【测试 3】更新配置")
        update_data = {
            'startup_wait_time': 15.0,
            'description': '更新后的测试配置'
        }
        updated_config = service.update_config(config.id, update_data)
        print(f"✅ 更新成功: startup_wait_time={updated_config.startup_wait_time}")
        assert updated_config.startup_wait_time == 15.0

        # 4. 获取所有配置
        print("\n【测试 4】获取所有配置")
        all_configs = service.get_all_configs()
        print(f"✅ 共找到 {len(all_configs)} 个配置")
        for cfg in all_configs:
            status = "●" if cfg.is_active else "○"
            print(f"  {status} [{cfg.id}] {cfg.config_name}")

        # 5. 删除配置
        print("\n【测试 5】删除配置")
        success = service.delete_config(config.id)
        print(f"✅ 删除成功: {success}")

        # 验证已删除
        deleted_config = service.get_config(config_id=config.id)
        assert deleted_config is None
        print("✅ 验证删除成功")

        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def test_task_logging():
    """测试任务日志功能"""
    print("\n" + "=" * 80)
    print("测试任务日志功能")
    print("=" * 80)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 获取第一个配置
        configs = service.get_all_configs()
        if not configs:
            print("⚠️ 没有配置，跳过日志测试")
            return

        config = configs[0]
        print(f"\n使用配置: {config.config_name} (ID={config.id})")

        # 1. 记录任务开始
        print("\n【测试 1】记录任务开始")
        log = service.log_task_start(
            config_id=config.id,
            task_name="测试任务",
            dwg_file=r"F:\test\drawing.dwg"
        )
        print(f"✅ 任务日志创建: ID={log.id}")

        # 模拟一些延迟
        import time
        time.sleep(1)

        # 2. 记录任务成功
        print("\n【测试 2】记录任务成功")
        success = service.log_task_end(
            log_id=log.id,
            status='success'
        )
        print(f"✅ 任务日志更新: {success}")

        # 3. 获取任务日志
        print("\n【测试 3】获取任务日志")
        logs = service.get_task_logs(config_id=config.id, limit=5)
        print(f"✅ 找到 {len(logs)} 条日志")

        for task_log in logs:
            print(f"\n  任务: {task_log.task_name}")
            print(f"  状态: {task_log.status}")
            print(f"  文件: {task_log.dwg_file}")
            print(f"  耗时: {task_log.duration_seconds:.2f}秒" if task_log.duration_seconds else "  耗时: N/A")

        print("\n" + "=" * 80)
        print("✅ 日志功能测试通过！")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def test_json_operations():
    """测试 JSON 菜单操作的序列化"""
    print("\n" + "=" * 80)
    print("测试 JSON 菜单操作")
    print("=" * 80)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 创建包含复杂菜单操作的配置
        print("\n【测试 1】创建包含菜单操作的配置")
        menu_ops = [
            {"type": "command", "command": "ZOOM", "wait_time": 0.5},
            {"type": "command", "command": "E", "wait_time": 1.0},
            {"type": "command", "command": "REGEN", "wait_time": 2.0}
        ]

        config = service.create_config({
            'config_name': 'test_menu_config',
            'description': '测试菜单操作配置',
            'menu_operations': menu_ops,
            'is_active': False
        })
        print(f"✅ 创建成功: ID={config.id}")

        # 读取并验证
        print("\n【测试 2】读取并验证菜单操作")
        loaded_config = service.get_config(config_id=config.id)

        import json
        loaded_ops = json.loads(loaded_config.menu_operations)

        print(f"✅ 菜单操作数量: {len(loaded_ops)}")
        for i, op in enumerate(loaded_ops, 1):
            print(f"  操作 {i}: {op['type']} - {op['command']} - {op['wait_time']}秒")

        assert len(loaded_ops) == 3
        assert loaded_ops[0]['command'] == 'ZOOM'
        print("✅ 菜单操作验证通过")

        # 清理
        service.delete_config(config.id)
        print("✅ 清理完成")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


def main():
    """主测试函数"""
    print("=" * 80)
    print("AutoCAD 配置系统测试")
    print("=" * 80)

    try:
        # 运行所有测试
        test_config_crud()
        test_task_logging()
        test_json_operations()

        print("\n" + "=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
    input("\n按 Enter 键退出...")
