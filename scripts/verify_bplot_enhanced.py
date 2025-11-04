"""
验证 bplot 配置 - 显示完整的13步工作流

Author: CAD Auto Processor Team
Date: 2025-11-04
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def verify_bplot_config():
    """验证 bplot 配置"""

    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        config = service.get_config(config_name="bplot")

        if not config:
            print("❌ 未找到 bplot 配置")
            return

        print("\n" + "=" * 80)
        print("bplot 配置验证")
        print("=" * 80)
        print(f"配置ID: {config.id}")
        print(f"配置名: {config.config_name}")
        print(f"描述: {config.description}")
        print("=" * 80)

        # 解析操作
        operations = json.loads(config.menu_operations)

        print(f"\n📋 操作步骤 (共 {len(operations)} 步):\n")

        # 分类显示
        pre_ops = []
        main_ops = []
        post_ops = []

        for i, op in enumerate(operations, 1):
            desc = op.get('description', '')
            if desc.startswith('前置:'):
                pre_ops.append((i, op))
            elif desc.startswith('后置:'):
                post_ops.append((i, op))
            else:
                main_ops.append((i, op))

        # 前置操作
        print(f"{'=' * 80}")
        print(f"前置操作 ({len(pre_ops)} 步)")
        print(f"{'=' * 80}")
        for i, op in pre_ops:
            print(f"\n步骤 {i}: [{op['type']}] {op['description']}")
            if op['type'] == 'system_command':
                print(f"  命令: {op.get('command')}")
                print(f"  忽略错误: {op.get('ignore_error', False)}")
            elif op['type'] == 'directory_cleanup':
                print(f"  路径: {op.get('path')}")
                print(f"  创建目录: {op.get('create_if_not_exist', False)}")
            print(f"  等待时间: {op.get('wait_time', 0)} 秒")

        # 主流程操作
        print(f"\n{'=' * 80}")
        print(f"主流程操作 ({len(main_ops)} 步)")
        print(f"{'=' * 80}")
        for i, op in main_ops:
            print(f"\n步骤 {i}: [{op['type']}] {op['description']}")
            if op['type'] == 'command':
                print(f"  方法: {op.get('method')}")
                print(f"  命令: {op.get('text')}")
            elif op['type'] == 'menu':
                print(f"  方法: {op.get('method')}")
                print(f"  按钮文本: {op.get('text')}")
            elif op['type'] == 'input':
                print(f"  输入文本: {op.get('text')}")
                print(f"  回车前等待: {op.get('wait_before_enter', 0)} 秒")
                print(f"  回车次数: {op.get('enter_count', 1)}")
            elif op['type'] == 'screenshot_extract':
                print(f"  提取模式: {op.get('target_pattern')}")
                print(f"  保存到变量: {op.get('save_to')}")
                print(f"  是否必需: {op.get('required', True)}")
            print(f"  等待时间: {op.get('wait_time', 0)} 秒")

        # 后置操作
        print(f"\n{'=' * 80}")
        print(f"后置操作 ({len(post_ops)} 步)")
        print(f"{'=' * 80}")
        for i, op in post_ops:
            print(f"\n步骤 {i}: [{op['type']}] {op['description']}")
            if op['type'] == 'file_monitor':
                print(f"  监控路径: {op.get('watch_path')}")
                print(f"  文件模式: {op.get('file_pattern')}")
                print(f"  期望数量变量: {op.get('expected_count_variable')}")
                print(f"  检查间隔: {op.get('check_interval')} 秒")
                print(f"  最大等待: {op.get('max_wait_time')} 秒")
                print(f"  稳定持续时间: {op.get('stable_duration')} 秒")
            elif op['type'] == 'system_command':
                print(f"  命令: {op.get('command')}")
                print(f"  忽略错误: {op.get('ignore_error', False)}")

        print(f"\n{'=' * 80}")
        print("✅ 配置验证完成！")
        print(f"{'=' * 80}\n")

        # 生成API调用示例
        print(f"{'=' * 80}")
        print("API 调用示例")
        print(f"{'=' * 80}\n")
        print("POST /api/v1/tasks/print")
        print("Content-Type: application/json\n")
        print('''{
    "config_name": "bplot",
    "dwg_url": "http://10.3.19.199/cad/PCX2.dwg",
    "use_bplot": true
}''')
        print(f"\n{'=' * 80}\n")

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    verify_bplot_config()
