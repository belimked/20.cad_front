"""
添加全屏截图提取步骤到default配置

这个SB脚本给default配置添加第四步：全屏截图并提取总页数

Author: 老王
Date: 2025-10-28
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig


def add_screenshot_extract_step():
    """给default配置添加全屏截图提取步骤"""

    db = SessionLocal()
    try:
        # 查找default配置
        config = db.query(AutoCADConfig).filter_by(config_name='default').first()

        if not config:
            print("❌ 错误：未找到default配置")
            return False

        print(f"✅ 找到配置: {config.config_name} (ID: {config.id})")

        # 解析现有配置
        if config.menu_operations:
            try:
                operations = json.loads(config.menu_operations)
                print(f"\n📋 当前配置 ({len(operations)} 个步骤):")
                for i, op in enumerate(operations, 1):
                    op_type = op.get('type')
                    if op_type == 'menu':
                        text = op.get('text', '')
                        print(f"  {i}. 菜单点击: '{text}'")
                    elif op_type == 'command':
                        cmd = op.get('command', '')
                        print(f"  {i}. CAD命令: {cmd}")
                    elif op_type == 'screenshot_extract':
                        pattern = op.get('target_pattern', '')
                        print(f"  {i}. 截图提取: {pattern}")
            except:
                operations = []
                print("⚠️ 现有配置解析失败，将创建新配置")
        else:
            operations = []
            print("📋 当前无配置")

        # 构建完整的4步配置
        new_operations = [
            {
                "type": "menu",
                "method": "ocr",
                "text": "依云",
                "wait_time": 0.5
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "CAD批量打图精灵",
                "wait_time": 1.0
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "打印",
                "wait_time": 2.0
            },
            {
                "type": "screenshot_extract",
                "target_pattern": "共 (\\d+) 页",
                "save_to": "total_pages",
                "required": False,
                "wait_time": 1.0
            }
        ]

        # 更新配置
        config.menu_operations = json.dumps(new_operations, ensure_ascii=False)
        db.commit()

        print(f"\n✅ 配置已更新!")
        print(f"\n📋 新配置 ({len(new_operations)} 个步骤):")
        for i, op in enumerate(new_operations, 1):
            op_type = op.get('type')
            if op_type == 'menu':
                text = op.get('text', '')
                wait = op.get('wait_time', 1.0)
                print(f"  {i}. 菜单点击: '{text}' (等待{wait}秒)")
            elif op_type == 'command':
                cmd = op.get('command', '')
                wait = op.get('wait_time', 1.0)
                print(f"  {i}. CAD命令: {cmd} (等待{wait}秒)")
            elif op_type == 'screenshot_extract':
                pattern = op.get('target_pattern', '')
                save_to = op.get('save_to', '')
                required = op.get('required', False)
                wait = op.get('wait_time', 1.0)
                print(f"  {i}. 截图提取: 模式='{pattern}', 保存到={save_to}, 必填={required}, 等待{wait}秒")

        print("\n" + "=" * 80)
        print("✅ 完成！现在可以运行工作流程测试:")
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
    print("添加全屏截图提取步骤")
    print("=" * 80)
    print()

    success = add_screenshot_extract_step()

    if not success:
        sys.exit(1)
