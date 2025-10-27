"""
为AutoCAD配置添加菜单操作

Usage:
    python scripts/add_menu_operations.py <config_id>

Author: CAD Auto Processor Team
Date: 2025-10-27
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
import json


def show_current_operations(config_id: int):
    """显示当前菜单操作"""
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)
        config = service.get_config(config_id=config_id)

        if not config:
            print(f"❌ 配置不存在: ID={config_id}")
            return None

        print(f"\n【当前配置】")
        print(f"名称: {config.config_name}")
        print(f"描述: {config.description}")

        if config.menu_operations:
            try:
                ops = json.loads(config.menu_operations)
                if ops:
                    print(f"\n【当前菜单操作】（共{len(ops)}个）")
                    for i, op in enumerate(ops, 1):
                        if op['type'] == 'command':
                            print(f"  {i}. 命令: {op['command']} (等待{op.get('wait_time', 0)}秒)")
                        elif op['type'] == 'menu':
                            method = op.get('method', 'auto')
                            if method == 'ocr':
                                print(f"  {i}. OCR识别: '{op['text']}' (等待{op.get('wait_time', 0)}秒)")
                            elif method == 'image':
                                print(f"  {i}. 图像识别: {op.get('icon_path')} (等待{op.get('wait_time', 0)}秒)")
                            else:
                                print(f"  {i}. 菜单: {' > '.join(op.get('path', []))} (等待{op.get('wait_time', 0)}秒)")
                else:
                    print(f"\n【当前菜单操作】: 无")
            except:
                print(f"\n【当前菜单操作】: 解析失败")
        else:
            print(f"\n【当前菜单操作】: 无")

        return config

    finally:
        db.close()


def add_operations_interactive(config_id: int):
    """交互式添加菜单操作"""

    # 显示当前操作
    config = show_current_operations(config_id)
    if not config:
        return

    print("\n" + "=" * 60)
    print("添加菜单操作")
    print("=" * 60)
    print("\n操作类型:")
    print("  [1] AutoCAD命令")
    print("  [2] 菜单点击（键盘/鼠标）")
    print("  [3] OCR文字识别（推荐）")
    print("  [0] 完成并保存")

    # 获取现有操作
    operations = []
    if config.menu_operations:
        try:
            operations = json.loads(config.menu_operations)
        except:
            operations = []

    while True:
        print("\n" + "-" * 60)
        choice = input("\n请选择操作类型 (0-3): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            # 添加命令
            command = input("请输入命令名称 (如ZOOM, LINE, REGEN): ").strip().upper()
            if not command:
                print("❌ 命令不能为空")
                continue

            wait_time = input("执行后等待时间（秒，默认0.5）: ").strip()
            wait_time = float(wait_time) if wait_time else 0.5

            operations.append({
                "type": "command",
                "command": command,
                "wait_time": wait_time
            })
            print(f"✅ 已添加命令: {command}")

        elif choice == "2":
            # 添加菜单点击（传统方式）
            print("\n菜单点击方式:")
            print("  - 有快捷键：输入如 '帮助(H),欢迎屏幕(W)'")
            print("  - 无快捷键：输入如 '工具,选项'")
            path_input = input("菜单路径（逗号分隔）: ").strip()
            if not path_input:
                print("❌ 菜单路径不能为空")
                continue

            path = [p.strip() for p in path_input.split(",")]

            wait_time = input("点击后等待时间（秒，默认1.0）: ").strip()
            wait_time = float(wait_time) if wait_time else 1.0

            operations.append({
                "type": "menu",
                "path": path,
                "wait_time": wait_time
            })
            print(f"✅ 已添加菜单: {' > '.join(path)}")

        elif choice == "3":
            # 添加OCR文字识别
            print("\nOCR文字识别 - 智能方案")
            print("  只需输入菜单文字，系统自动识别并点击")
            print("  示例: '依云'、'帮助'、'工具' 等")

            text = input("请输入要识别的菜单文字: ").strip()
            if not text:
                print("❌ 文字不能为空")
                continue

            wait_time = input("点击后等待时间（秒，默认1.0）: ").strip()
            wait_time = float(wait_time) if wait_time else 1.0

            operations.append({
                "type": "menu",
                "method": "ocr",
                "text": text,
                "wait_time": wait_time
            })
            print(f"✅ 已添加OCR识别: '{text}'")

        else:
            print("❌ 无效选项")

        # 显示当前已添加的操作
        if operations:
            print(f"\n【已添加操作】（共{len(operations)}个）")
            for i, op in enumerate(operations, 1):
                if op['type'] == 'command':
                    print(f"  {i}. 命令: {op['command']} (等待{op.get('wait_time', 0)}秒)")
                elif op['type'] == 'menu':
                    method = op.get('method', 'auto')
                    if method == 'ocr':
                        print(f"  {i}. OCR识别: '{op['text']}' (等待{op.get('wait_time', 0)}秒)")
                    else:
                        print(f"  {i}. 菜单: {' > '.join(op.get('path', []))} (等待{op.get('wait_time', 0)}秒)")

    # 保存到数据库
    if operations:
        db = SessionLocal()
        try:
            service = AutoCADConfigService(db)
            service.update_config(config_id, {'menu_operations': operations})

            print("\n" + "=" * 60)
            print("✅ 菜单操作已保存")
            print("=" * 60)

            # 显示最终结果
            show_current_operations(config_id)

        finally:
            db.close()
    else:
        print("\n⚠️ 未添加任何操作，未保存")


def show_examples():
    """显示示例"""
    print("\n" + "=" * 60)
    print("常用AutoCAD命令示例")
    print("=" * 60)
    print("\n视图命令:")
    print("  ZOOM    - 缩放视图")
    print("  E       - ZOOM Extents (显示全部)")
    print("  REGEN   - 重新生成图形")
    print("  REGENALL - 重新生成所有视口")

    print("\n绘图命令:")
    print("  LINE    - 直线")
    print("  CIRCLE  - 圆")
    print("  ARC     - 弧")
    print("  PLINE   - 多段线")

    print("\n修改命令:")
    print("  MOVE    - 移动")
    print("  COPY    - 复制")
    print("  ROTATE  - 旋转")
    print("  SCALE   - 缩放")

    print("\n其他命令:")
    print("  SAVE    - 保存")
    print("  QSAVE   - 快速保存")
    print("  AUDIT   - 审核图形")
    print("  PURGE   - 清理")


def main():
    """主函数"""
    print("=" * 60)
    print("AutoCAD 配置 - 菜单操作管理")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\n用法: python scripts/add_menu_operations.py <config_id>")
        print("\n示例:")
        print("  python scripts/add_menu_operations.py 4")
        print("\n提示: 先运行 'python scripts/autocad_config_manager.py list' 查看配置ID")
        return

    try:
        config_id = int(sys.argv[1])
    except ValueError:
        print(f"❌ 无效的配置ID: {sys.argv[1]}")
        return

    # 显示示例
    show_examples()

    # 交互式添加
    add_operations_interactive(config_id)


if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 键退出...")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
