"""
验证批量打印工作流配置

查询并显示数据库中的工作流配置详情
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import get_db_session
from src.services.autocad_config_service import AutoCADConfigService


def verify_config():
    """验证配置"""
    db = get_db_session()
    service = AutoCADConfigService(db)

    try:
        # 获取配置
        config = service.get_config(config_name="batch_print_full_workflow")

        if not config:
            print("❌ 配置不存在！")
            return

        print("\n" + "=" * 80)
        print("📋 配置基本信息")
        print("=" * 80)
        print(f"ID: {config.id}")
        print(f"配置名称: {config.config_name}")
        print(f"描述: {config.description}")
        print(f"AutoCAD路径: {config.autocad_exe_path}")
        print(f"DWG文件: {config.dwg_file_path}")
        print(f"输出目录: {config.output_dir_path}")
        print(f"是否激活: {'✅ 是' if config.is_active else '❌ 否'}")

        # 解析工作流配置
        if config.menu_operations:
            workflow = json.loads(config.menu_operations)

            print("\n" + "=" * 80)
            print("🔧 工作流配置")
            print("=" * 80)
            print(f"工作流名称: {workflow.get('workflow_name')}")
            print(f"版本: {workflow.get('workflow_version')}")
            print(f"描述: {workflow.get('description')}")

            # 前置操作
            print("\n" + "-" * 80)
            print("1️⃣  前置操作 (pre_operations)")
            print("-" * 80)
            for i, op in enumerate(workflow.get('pre_operations', []), 1):
                print(f"\n步骤 {i}:")
                print(f"  类型: {op['type']}")
                print(f"  方法: {op.get('method', 'N/A')}")
                print(f"  描述: {op['description']}")
                if op['type'] == 'system_command':
                    print(f"  命令: {op.get('command')}")
                    print(f"  忽略错误: {op.get('ignore_error', False)}")
                elif op['type'] == 'directory_cleanup':
                    print(f"  路径: {op.get('path')}")
                    print(f"  创建目录: {op.get('create_if_not_exist', False)}")
                print(f"  等待时间: {op.get('wait_time', 0)} 秒")

            # 主流程操作
            print("\n" + "-" * 80)
            print("2️⃣  主流程操作 (main_operations)")
            print("-" * 80)
            for i, op in enumerate(workflow.get('main_operations', []), 1):
                print(f"\n步骤 {i}:")
                print(f"  类型: {op['type']}")
                print(f"  方法: {op.get('method', 'N/A')}")
                print(f"  描述: {op['description']}")

                if op['type'] == 'command':
                    print(f"  命令文本: {op.get('text')}")
                elif op['type'] == 'menu':
                    print(f"  菜单文本: {op.get('text')}")
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
            print("\n" + "-" * 80)
            print("3️⃣  后置操作 (post_operations)")
            print("-" * 80)
            for i, op in enumerate(workflow.get('post_operations', []), 1):
                print(f"\n步骤 {i}:")
                print(f"  类型: {op['type']}")
                print(f"  方法: {op.get('method', 'N/A')}")
                print(f"  描述: {op['description']}")

                if op['type'] == 'file_monitor':
                    print(f"  监控路径: {op.get('watch_path')}")
                    print(f"  文件模式: {op.get('file_pattern')}")
                    print(f"  期望数量变量: {op.get('expected_count_variable')}")
                    print(f"  检查间隔: {op.get('check_interval')} 秒")
                    print(f"  最大等待: {op.get('max_wait_time')} 秒")
                    print(f"  稳定持续时间: {op.get('stable_duration')} 秒")

                    validation = op.get('validation', {})
                    print(f"  验证设置:")
                    print(f"    - 检查文件数量: {validation.get('check_file_count')}")
                    print(f"    - 检查无新文件: {validation.get('check_no_new_files')}")
                    print(f"    - 无新文件阈值: {validation.get('no_new_files_threshold')} 秒")
                elif op['type'] == 'system_command':
                    print(f"  命令: {op.get('command')}")
                    print(f"  忽略错误: {op.get('ignore_error', False)}")

            # 全局设置
            print("\n" + "-" * 80)
            print("⚙️  全局设置 (global_settings)")
            print("-" * 80)
            settings = workflow.get('global_settings', {})
            print(f"  Umi-OCR URL: {settings.get('umi_ocr_url')}")
            print(f"  截图目录: {settings.get('screenshot_dir')}")
            print(f"  日志级别: {settings.get('log_level')}")

            retry = settings.get('retry_on_failure', {})
            print(f"  重试设置:")
            print(f"    - 启用: {retry.get('enabled')}")
            print(f"    - 最大重试: {retry.get('max_retries')}")
            print(f"    - 重试延迟: {retry.get('retry_delay')} 秒")

            error_handling = settings.get('error_handling', {})
            print(f"  错误处理:")
            print(f"    - 错误时截图: {error_handling.get('screenshot_on_error')}")
            print(f"    - 可选失败继续: {error_handling.get('continue_on_optional_failure')}")
            print(f"    - 关键失败中止: {error_handling.get('abort_on_critical_failure')}")

            # 变量定义
            print("\n" + "-" * 80)
            print("📊 变量定义 (variables)")
            print("-" * 80)
            variables = workflow.get('variables', {})
            for var_name, var_info in variables.items():
                print(f"\n  {var_name}:")
                print(f"    类型: {var_info.get('type')}")
                print(f"    描述: {var_info.get('description')}")
                print(f"    默认值: {var_info.get('default')}")

            print("\n" + "=" * 80)
            print("✅ 配置验证完成！")
            print("=" * 80)

        else:
            print("\n⚠️  配置中没有工作流信息（menu_operations 为空）")

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    verify_config()
