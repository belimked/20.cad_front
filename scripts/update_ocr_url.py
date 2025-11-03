#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库中的OCR服务地址
从 http://10.3.19.121:1224 改为 http://127.0.0.1:11224

Usage:
    python scripts/update_ocr_url.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.autocad_config import AutoCADConfig


def main():
    print("\n" + "=" * 80)
    print("更新 Umi-OCR 服务地址")
    print("=" * 80)
    print("从: http://10.3.19.121:1224")
    print("到:   http://127.0.0.1:11224")
    print("=" * 80)

    db = SessionLocal()

    try:
        # 查询所有使用旧地址的配置
        old_configs = db.query(AutoCADConfig).filter(
            AutoCADConfig.umi_ocr_service_url == 'http://10.3.19.121:1224'
        ).all()

        if not old_configs:
            print("\n✅ 没有找到使用旧地址的配置")
            print("   所有配置都已是最新地址")
            return 0

        print(f"\n📋 找到 {len(old_configs)} 个使用旧地址的配置:")
        for config in old_configs:
            print(f"   - {config.config_name}")

        # 更新所有旧地址
        update_count = db.query(AutoCADConfig).filter(
            AutoCADConfig.umi_ocr_service_url == 'http://10.3.19.121:1224'
        ).update({
            'umi_ocr_service_url': 'http://127.0.0.1:11224'
        })

        db.commit()

        print(f"\n✅ 已更新 {update_count} 个配置")

        # 验证更新结果
        print("\n📊 当前所有配置的OCR地址:")
        all_configs = db.query(AutoCADConfig).all()
        for config in all_configs:
            enabled = "✅" if config.umi_ocr_enabled else "❌"
            print(f"   {enabled} {config.config_name:20s} -> {config.umi_ocr_service_url}")

        print("\n" + "=" * 80)
        print("✅ 更新完成！")
        print("=" * 80)
        print("\n⚠️  重要提示:")
        print("   如果API服务正在运行，需要重启才能生效:")
        print("   1. Ctrl+C 停止当前服务")
        print("   2. 重新运行: .\\start_api.ps1")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
