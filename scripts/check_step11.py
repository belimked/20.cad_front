"""
查看步骤11的详细配置
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def check_step11():
    """查看步骤11的配置"""

    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        config = service.get_config(config_name="bplot")
        if not config:
            print("❌ 未找到配置")
            return

        operations = json.loads(config.menu_operations)

        print(f"\n总步骤数: {len(operations)}")

        # 显示步骤11 (索引10)
        if len(operations) >= 11:
            step11 = operations[10]
            print(f"\n步骤 11 完整配置:")
            print(json.dumps(step11, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 只有 {len(operations)} 步")

    finally:
        db.close()


if __name__ == "__main__":
    check_step11()
