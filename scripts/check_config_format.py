"""
检查 batch_print_full_workflow 配置格式

查看 menu_operations 字段的实际内容
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def check_config_format():
    """检查配置格式"""
    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        # 获取配置
        config = service.get_config(config_name="batch_print_full_workflow")

        if not config:
            print("❌ 配置不存在！")
            return

        print("\n" + "=" * 80)
        print("配置格式检查")
        print("=" * 80)

        # 解析 menu_operations
        if config.menu_operations:
            workflow = json.loads(config.menu_operations)

            print("\n📊 当前配置结构:")
            print(f"  - workflow_name: {workflow.get('workflow_name')}")
            print(f"  - workflow_version: {workflow.get('workflow_version')}")
            print(f"  - 顶层键: {list(workflow.keys())}")

            print("\n⚠️  问题：")
            print("  当前配置包含多个阶段 (pre_operations, main_operations, post_operations)")
            print("  但 ConfigurableAutoCADWorkflow 期望的是单一的操作列表")

            print("\n🔧 需要的格式转换:")
            print("  方式1: 将所有操作合并为一个列表存储在 menu_operations")
            print("  方式2: 修改工作流代码支持分阶段配置")

            print("\n📋 建议的扁平化格式示例:")
            # 合并所有操作
            all_operations = []
            all_operations.extend(workflow.get('pre_operations', []))
            all_operations.extend(workflow.get('main_operations', []))
            all_operations.extend(workflow.get('post_operations', []))

            print(f"  总操作数: {len(all_operations)}")
            print("\n  合并后的操作列表:")
            for i, op in enumerate(all_operations, 1):
                print(f"    {i}. [{op['type']}] {op['description']}")

        else:
            print("\n⚠️  menu_operations 为空")

    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    check_config_format()
