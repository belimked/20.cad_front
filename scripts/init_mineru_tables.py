"""
初始化 MinerU 相关数据库表

运行此脚本创建 MinerU 识别所需的数据库表：
- dwg_drawing_sheets: 图号关联表
- dwg_recognition_results: 识别结果表

使用方法:
    python scripts/init_mineru_tables.py

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_manager, Base
from src.models.dwg_drawing_sheet import DWGDrawingSheet
from src.models.dwg_recognition_result import DWGRecognitionResult


def init_mineru_tables():
    """创建 MinerU 相关表"""
    print("=" * 60)
    print("MinerU 数据库表初始化")
    print("=" * 60)

    db_manager = get_db_manager()
    engine = db_manager.engine

    print("\n正在创建 MinerU 相关表...")

    # 创建表（checkfirst=True 表示如果表已存在则跳过）
    try:
        DWGDrawingSheet.__table__.create(engine, checkfirst=True)
        print("✅ dwg_drawing_sheets 表已创建/已存在")
    except Exception as e:
        print(f"❌ dwg_drawing_sheets 表创建失败: {e}")

    try:
        DWGRecognitionResult.__table__.create(engine, checkfirst=True)
        print("✅ dwg_recognition_results 表已创建/已存在")
    except Exception as e:
        print(f"❌ dwg_recognition_results 表创建失败: {e}")

    print("\n" + "=" * 60)
    print("✅ MinerU 表初始化完成")
    print("=" * 60)


if __name__ == '__main__':
    init_mineru_tables()
