#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 bplot 配置到数据库

创建一个新的AutoCAD配置，用于批量打印(bplot)全自动化工作流

Usage:
    python scripts/add_bplot_config.py
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig


def main():
    print("\n" + "=" * 80)
    print("添加 bplot 配置到数据库")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 检查是否已存在
        existing = db.query(AutoCADConfig).filter(
            AutoCADConfig.config_name == 'bplot'
        ).first()

        if existing:
            print("\n⚠️  配置 'bplot' 已存在")
            print(f"   创建时间: {existing.created_at}")
            print(f"   描述: {existing.description}")
            print("\n是否覆盖现有配置? (y/N): ", end='')
            if input().lower() != 'y':
                print("已取消")
                return 0

            # 删除现有配置
            db.delete(existing)
            db.commit()
            print("✅ 已删除旧配置")

        # 定义工作流步骤
        workflow_steps = [
            {
                "type": "command",
                "method": "keyboard",
                "text": "_.bplot",
                "description": "执行BPLOT命令（批量打印）",
                "wait_time": 5.0
            },
            {
                "type": "menu",
                "method": "ocr",
                "text": "设置批量打印图纸表",
                "description": "点击设置批量打印图纸表按钮",
                "alternative_texts": [
                    "选择批量打印图纸",
                    "选择图纸",
                    "图纸表",
                    "Select Drawings",
                    "Add Sheets"
                ],
                "wait_time": 1.0
            },
            {
                "type": "input",
                "method": "keyboard",
                "text": "all",
                "description": "键盘输入all选择所有图纸",
                "wait_time": 2.0
            },
            {
                "type": "screenshot_extract",
                "target_pattern": r"选中图纸[:\s]*(\d+)",
                "save_to": "selected_sheets",
                "description": "提取选中图纸数量",
                "required": False,
                "wait_time": 0.5
            },
            {
                "type": "screenshot_extract",
                "target_pattern": r"共\s*(\d+)\s*页",
                "save_to": "total_pages",
                "description": "提取总页数",
                "alternative_patterns": [
                    r"Total[:\s]*(\d+)",
                    r"(\d+)\s*sheets",
                    r"页数[:\s]*(\d+)"
                ],
                "required": False,
                "wait_time": 0.5
            }
        ]

        # 预处理方法
        preprocessing_methods = [
            "original",
            "grayscale",
            "binary_otsu",
            "binary_adaptive",
            "denoise_gaussian",
            "high_contrast"
        ]

        # 创建新配置
        new_config = AutoCADConfig(
            config_name='bplot',
            description='AutoCAD批量打印(bplot)全自动化工作流 - OCR识别按钮并自动输入',
            workflow_steps=json.dumps(workflow_steps, ensure_ascii=False),
            ocr_enabled=True,
            ocr_screenshot_enabled=True,
            ocr_screenshot_base_dir='screenshots/bplot_auto',
            ocr_screenshot_timestamp_format='%Y%m%d_%H%M%S',
            ocr_file_retention_days=7,
            ocr_enable_detailed_logging=True,
            umi_ocr_enabled=True,
            umi_ocr_service_url='http://127.0.0.1:11224',
            umi_ocr_api_path='/api/ocr',
            umi_ocr_timeout=60,
            umi_ocr_limit_side_len=2880,
            ocr_preprocessing_methods=json.dumps(preprocessing_methods, ensure_ascii=False)
        )

        db.add(new_config)
        db.commit()
        db.refresh(new_config)

        print("\n✅ 成功添加 bplot 配置")
        print("\n📋 配置详情:")
        print(f"   名称: {new_config.config_name}")
        print(f"   描述: {new_config.description}")
        print(f"   OCR启用: {'是' if new_config.umi_ocr_enabled else '否'}")
        print(f"   OCR地址: {new_config.umi_ocr_service_url}{new_config.umi_ocr_api_path}")
        print(f"   截图目录: {new_config.ocr_screenshot_base_dir}")
        print(f"   工作流步骤: {len(workflow_steps)} 个")

        print("\n🔧 工作流步骤:")
        for i, step in enumerate(workflow_steps, 1):
            print(f"   {i}. [{step['type']}] {step.get('description', step.get('text', ''))}")

        print("\n" + "=" * 80)
        print("✅ 配置添加完成！")
        print("=" * 80)
        print("\n💡 使用方法:")
        print("   1. API调用时传递: config_name='bplot'")
        print("   2. 或使用 use_bplot=true 参数自动路由")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 添加配置失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
