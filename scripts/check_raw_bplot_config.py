"""
检查 bplot 配置的原始 JSON 数据

Author: CAD Auto Processor Team
Date: 2025-11-04
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.models.autocad_config import AutoCADConfig


def check_raw_config():
    """检查原始配置数据"""

    db = get_db_session()

    try:
        config = db.query(AutoCADConfig).filter(AutoCADConfig.config_name == "bplot").first()

        if not config:
            print("❌ 未找到 bplot 配置")
            return

        print("\n" + "=" * 80)
        print("原始配置数据检查")
        print("=" * 80)
        print(f"配置ID: {config.id}")
        print(f"配置名: {config.config_name}")
        print(f"描述: {config.description}")
        print("=" * 80)

        print(f"\nmenu_operations 字段类型: {type(config.menu_operations)}")
        print(f"menu_operations 长度: {len(config.menu_operations) if config.menu_operations else 0}")

        if config.menu_operations:
            # 解析 JSON
            operations = json.loads(config.menu_operations)
            print(f"\n解析后的类型: {type(operations)}")

            if isinstance(operations, list):
                print(f"✅ 是列表格式")
                print(f"操作数量: {len(operations)}")
                print(f"\n前3个操作:")
                for i, op in enumerate(operations[:3], 1):
                    print(f"  {i}. {op.get('type')} - {op.get('description', 'N/A')}")
            elif isinstance(operations, dict):
                print(f"✅ 是字典格式")
                print(f"顶层键: {list(operations.keys())}")
            else:
                print(f"⚠️  未知格式: {type(operations)}")

            # 显示原始 JSON（前500字符）
            print(f"\n原始 JSON（前500字符）:")
            print(config.menu_operations[:500])

    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    check_raw_config()
