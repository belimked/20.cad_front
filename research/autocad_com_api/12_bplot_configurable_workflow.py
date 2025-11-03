"""
AutoCAD Batch Plot (bplot) 配置化工作流

从数据库读取bplot配置并执行，支持OCR日志记录

Usage:
    python research/autocad_com_api/12_bplot_configurable_workflow.py

Author: CAD Auto Processor Team
Date: 2025-11-03
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from research.autocad_com_api.9_configurable_workflow import ConfigurableAutoCADWorkflow
from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService


def main():
    """
    运行bplot配置化工作流
    """
    print("\n" + "=" * 80)
    print("AutoCAD Batch Plot (bplot) 配置化工作流")
    print("=" * 80)

    # 测试文件路径（修改为你的实际文件）
    dwg_file = r"F:\cad\caddd\PCX20.01 主体钢结构（20230301）.dwg"

    # 从数据库加载 bplot 配置
    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)
        config = service.get_config(config_name='bplot')

        if not config:
            print("❌ 未找到 bplot 配置")
            print("\n请先运行以下命令添加配置:")
            print("   python scripts/add_bplot_config.py")
            return 1

        print(f"\n✅ 已加载配置: {config.config_name}")
        print(f"   描述: {config.description}")
        print(f"   OCR启用: {config.umi_ocr_enabled}")
        print(f"   OCR地址: {config.umi_ocr_service_url}{config.umi_ocr_api_path}")

        # 解析菜单操作
        import json
        menu_operations = json.loads(config.menu_operations) if isinstance(
            config.menu_operations, str) else config.menu_operations

        if menu_operations:
            print(f"\n🔧 工作流步骤: {len(menu_operations)} 个")
            for i, op in enumerate(menu_operations, 1):
                desc = op.get('description', op.get('text', ''))
                print(f"   {i}. [{op.get('type')}] {desc}")

    finally:
        db.close()

    # 创建配置化工作流
    workflow = ConfigurableAutoCADWorkflow(config=config)

    try:
        # 执行工作流
        success = workflow.run(dwg_file_path=dwg_file)

        if success:
            print("\n🎉 Bplot配置化工作流执行成功！")

            # 显示提取的数据
            if hasattr(workflow, 'extracted_data') and workflow.extracted_data:
                print("\n📊 提取到的数据:")
                for key, value in workflow.extracted_data.items():
                    print(f"   {key}: {value}")

            return 0
        else:
            print("\n❌ Bplot配置化工作流执行失败")
            return 1

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        workflow.cleanup()
        input("\n按 Enter 键退出...")


if __name__ == "__main__":
    sys.exit(main())
