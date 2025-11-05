"""
更新 AutoCAD 配置 - 添加完整的批量打印工作流

将完整的工作流配置（包括前置操作、主流程、后置监控）存储到 menu_operations 字段

Author: CAD Auto Processor Team
Date: 2025-11-04
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def create_batch_print_workflow_config():
    """创建批量打印完整工作流配置"""

    workflow_config = {
        "workflow_name": "AutoCAD批量打印完整工作流",
        "workflow_version": "3.0",
        "description": "包含前置清理、主流程执行、后置监控的完整自动化流程",

        "pre_operations": [
            {
                "type": "system_command",
                "method": "cmd",
                "command": "taskkill /IM acad.exe /T /F",
                "description": "强制关闭所有AutoCAD进程",
                "ignore_error": True,
                "wait_time": 2
            },
            {
                "type": "directory_cleanup",
                "method": "delete",
                "path": r"F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000",
                "description": "清空输出目录，确保干净环境",
                "create_if_not_exist": True,
                "wait_time": 1
            }
        ],

        "main_operations": [
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
        ],

        "post_operations": [
            {
                "type": "file_monitor",
                "method": "watch_directory",
                "watch_path": r"F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000",
                "expected_count_variable": "selected_sheets",
                "description": "监控PDF文件生成，确保数量与选中图纸一致",
                "file_pattern": "*.pdf",
                "check_interval": 2,
                "max_wait_time": 600,
                "stable_duration": 10,
                "validation": {
                    "check_file_count": True,
                    "check_no_new_files": True,
                    "no_new_files_threshold": 10
                },
                "on_complete": {
                    "log_summary": True,
                    "summary_fields": [
                        "total_files",
                        "expected_files",
                        "elapsed_time",
                        "status"
                    ]
                },
                "on_timeout": {
                    "action": "warn",
                    "message": "文件生成超时，但继续执行后续步骤"
                }
            },
            {
                "type": "system_command",
                "method": "cmd",
                "command": "taskkill /IM acad.exe /T /F",
                "description": "完成后关闭AutoCAD进程",
                "ignore_error": True,
                "wait_time": 1
            }
        ],

        "global_settings": {
            "umi_ocr_url": "http://127.0.0.1:11224/api/ocr",
            "screenshot_dir": "screenshots/workflow",
            "log_level": "INFO",
            "retry_on_failure": {
                "enabled": True,
                "max_retries": 3,
                "retry_delay": 5
            },
            "error_handling": {
                "screenshot_on_error": True,
                "continue_on_optional_failure": True,
                "abort_on_critical_failure": True
            }
        },

        "variables": {
            "selected_sheets": {
                "type": "integer",
                "description": "从OCR提取的选中图纸数量",
                "default": 0
            },
            "actual_generated_files": {
                "type": "integer",
                "description": "实际生成的PDF文件数量",
                "default": 0
            }
        }
    }

    return workflow_config


def update_config():
    """更新配置到数据库"""

    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        # 生成工作流配置
        workflow_config = create_batch_print_workflow_config()

        # 查找或创建配置
        config_name = "batch_print_full_workflow"
        config = service.get_config(config_name=config_name)

        if config:
            print(f"📝 找到现有配置: {config_name} (ID: {config.id})")
            print(f"   更新工作流配置...")

            # 更新配置
            updated_config = service.update_config(
                config_id=config.id,
                update_data={
                    'menu_operations': workflow_config,
                    'description': '完整的批量打印工作流（含前置清理和后置监控）',
                }
            )

            print(f"✅ 配置已更新！")

        else:
            print(f"📝 创建新配置: {config_name}")

            # 创建新配置
            new_config = service.create_config({
                'config_name': config_name,
                'description': '完整的批量打印工作流（含前置清理和后置监控）',
                'autocad_exe_path': r'C:\Program Files\Autodesk\AutoCAD 2014\acad.exe',
                'autocad_version': '2014',
                'dwg_file_path': r'F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg',
                'force_close_existing': True,
                'close_cad_after_completion': False,  # 由工作流的 post_operations 控制
                'startup_wait_time': 10.0,
                'startup_check_interval': 1.0,
                'post_startup_wait': 2.0,
                'menu_operations': workflow_config,

                # OCR配置
                'umi_ocr_service_url': 'http://127.0.0.1:11224',
                'umi_ocr_api_path': '/api/ocr',
                'umi_ocr_enabled': True,
                'umi_ocr_limit_side_len': 2880,

                # 输出目录配置
                'output_dir_cleanup_enabled': False,  # 由工作流的 pre_operations 控制
                'output_dir_path': r'F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000',

                'is_active': True,
            })

            config = new_config
            print(f"✅ 配置已创建！ID: {config.id}")

        # 显示配置详情
        print(f"\n" + "=" * 80)
        print(f"配置详情")
        print(f"=" * 80)
        print(f"配置名称: {config.config_name}")
        print(f"配置ID: {config.id}")
        print(f"描述: {config.description}")
        print(f"\n工作流结构:")
        print(f"  前置操作: {len(workflow_config['pre_operations'])} 步")
        for i, op in enumerate(workflow_config['pre_operations'], 1):
            print(f"    {i}. [{op['type']}] {op['description']}")

        print(f"\n  主流程操作: {len(workflow_config['main_operations'])} 步")
        for i, op in enumerate(workflow_config['main_operations'], 1):
            print(f"    {i}. [{op['type']}] {op['description']}")

        print(f"\n  后置操作: {len(workflow_config['post_operations'])} 步")
        for i, op in enumerate(workflow_config['post_operations'], 1):
            print(f"    {i}. [{op['type']}] {op['description']}")

        print(f"\n变量定义:")
        for var_name, var_info in workflow_config['variables'].items():
            print(f"  - {var_name}: {var_info['description']}")

        print(f"\n" + "=" * 80)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("AutoCAD 批量打印完整工作流配置更新")
    print("=" * 80 + "\n")

    update_config()

    print("\n✅ 完成！\n")
