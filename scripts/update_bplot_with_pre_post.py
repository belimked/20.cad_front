"""
更新 bplot 配置 - 追加前置和后置逻辑

在现有的 9 个操作基础上追加：
- 前置: 关闭CAD进程、清空目录
- 后置: 监控文件生成、关闭CAD进程

Author: CAD Auto Processor Team
Date: 2025-11-04
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def update_bplot_config():
    """更新 bplot 配置"""

    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        # 获取现有配置
        config = service.get_config(config_name="bplot")

        if not config:
            print("❌ 未找到 bplot 配置")
            return

        print(f"✅ 找到配置: {config.config_name} (ID: {config.id})")

        # 构建完整的操作列表（前置 + 主流程 + 后置）
        complete_operations = []

        # ========================================
        # 前置操作 (2步)
        # ========================================
        complete_operations.extend([
            {
                "type": "system_command",
                "method": "cmd",
                "command": "taskkill /IM acad.exe /T /F",
                "description": "前置: 强制关闭所有AutoCAD进程",
                "ignore_error": True,
                "wait_time": 2
            },
            {
                "type": "directory_cleanup",
                "method": "delete",
                "path": r"F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000",
                "description": "前置: 清空输出目录",
                "create_if_not_exist": True,
                "wait_time": 1
            }
        ])

        # ========================================
        # 主流程操作 (9步 - 现有的)
        # ========================================
        complete_operations.extend([
            {
                "type": "command",
                "method": "keyboard",
                "text": "_.bplot",
                "description": "执行BPLOT命令（批量打印）",
                "wait_time": 5
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "选择要处理的图纸",
                "description": "点击设置批量打印图纸表按钮",
                "wait_time": 2
            },
            {
                "type": "input",
                "method": "keyboard",
                "text": "all",
                "description": "键盘输入all并确认选择",
                "wait_before_enter": 2,
                "enter_count": 2,
                "wait_between_enters": 2,
                "wait_time": 2
            },
            {
                "type": "screenshot_extract",
                "target_pattern": r"选中图纸.*?(\d+)",
                "save_to": "selected_sheets",
                "description": "提取选中图纸数量",
                "required": False,
                "wait_time": 0.5
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "无",
                "description": "打印预设点击",
                "wait_time": 1
            },
            {
                "type": "input",
                "method": "keyboard",
                "text": "t",
                "description": "打印选中",
                "wait_before_enter": 0,
                "enter_count": 0,
                "wait_between_enters": 1,
                "wait_time": 1
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "无",
                "description": "打印预设点击",
                "wait_time": 1
            },
            {
                "type": "input",
                "method": "keyboard",
                "text": "11",
                "description": "打印选中",
                "wait_before_enter": 0,
                "enter_count": 1,
                "wait_between_enters": 1,
                "wait_time": 2
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "确定",
                "description": "开始打印",
                "wait_time": 1
            }
        ])

        # ========================================
        # 后置操作 (2步)
        # ========================================
        complete_operations.extend([
            {
                "type": "file_monitor",
                "method": "watch_directory",
                "watch_path": r"F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000",
                "expected_count_variable": "selected_sheets",
                "description": "后置: 监控PDF文件生成",
                "file_pattern": "*.pdf",
                "check_interval": 2,
                "max_wait_time": 600,
                "stable_duration": 10,
                "validation": {
                    "check_file_count": True,
                    "check_no_new_files": True,
                    "no_new_files_threshold": 10
                }
            },
            {
                "type": "system_command",
                "method": "cmd",
                "command": "taskkill /IM acad.exe /T /F",
                "description": "后置: 完成后关闭AutoCAD进程",
                "ignore_error": True,
                "wait_time": 1
            }
        ])

        # 更新配置
        updated_config = service.update_config(
            config_id=config.id,
            update_data={
                'menu_operations': complete_operations,
                'description': 'AutoCAD批量打印(bplot)完整工作流 - 含前置清理和后置监控(共13步)',
            }
        )

        print("\n" + "=" * 80)
        print("✅ 配置已更新！")
        print("=" * 80)
        print(f"配置名称: {updated_config.config_name}")
        print(f"配置ID: {updated_config.id}")
        print(f"描述: {updated_config.description}")
        print(f"\n操作步骤:")
        print(f"  前置操作: 2 步")
        print(f"    1. 关闭所有AutoCAD进程")
        print(f"    2. 清空输出目录")
        print(f"\n  主流程操作: 9 步")
        print(f"    1. 执行BPLOT命令")
        print(f"    2. OCR识别并点击按钮")
        print(f"    3. 输入all")
        print(f"    4. 提取选中图纸数量")
        print(f"    5-9. 打印设置和确认")
        print(f"\n  后置操作: 2 步")
        print(f"    1. 监控PDF文件生成")
        print(f"    2. 关闭AutoCAD进程")
        print(f"\n  总计: {len(complete_operations)} 步")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("更新 bplot 配置 - 追加前置和后置逻辑")
    print("=" * 80 + "\n")

    update_bplot_config()

    print("\n✅ 完成！\n")
