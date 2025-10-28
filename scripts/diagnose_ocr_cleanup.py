#!/usr/bin/env python3
"""
OCR文件清理诊断工具

帮助诊断为什么文件清理功能没有工作

Author: CAD Auto Processor Team (老王修复版)
Date: 2025-10-28
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.services.autocad_config_service import AutoCADConfigService
from src.utils.ocr_file_manager import OCRFileManager


def main():
    """诊断清理功能"""
    print("=" * 80)
    print("OCR文件清理诊断工具")
    print("=" * 80)

    db = SessionLocal()
    try:
        service = AutoCADConfigService(db)

        # 查询激活的配置（不传参数会返回第一个激活的配置）
        config = service.get_config()
        if not config:
            print("\n❌ 没有激活的配置")
            return

        print(f"\n✅ 当前激活配置: {config.config_name}")
        print("\n" + "=" * 80)
        print("清理配置信息")
        print("=" * 80)
        print(f"  cleanup_enabled: {config.ocr_file_cleanup_enabled} (类型: {type(config.ocr_file_cleanup_enabled)})")
        print(f"  cleanup_strategy: {config.ocr_file_cleanup_strategy}")
        print(f"  retention_days: {config.ocr_file_retention_days}")
        print(f"  base_dir: {config.ocr_screenshot_base_dir}")
        print(f"  archive_dir: {config.ocr_file_archive_dir}")
        print(f"  timestamp_format: {config.ocr_screenshot_timestamp_format}")

        # 检查逻辑问题
        print("\n" + "=" * 80)
        print("逻辑检查")
        print("=" * 80)

        # 测试 or 运算符的行为
        result_with_or = config.ocr_file_cleanup_enabled or False
        print(f"  config.ocr_file_cleanup_enabled or False = {result_with_or} (类型: {type(result_with_or)})")

        if config.ocr_file_cleanup_enabled is None:
            print("  ⚠️ 警告：cleanup_enabled 是 None！这会导致清理被禁用")
        elif config.ocr_file_cleanup_enabled == 0:
            print("  ℹ️  cleanup_enabled = 0（禁用）")
        elif config.ocr_file_cleanup_enabled == 1:
            print("  ✅ cleanup_enabled = 1（启用）")
        elif config.ocr_file_cleanup_enabled is True:
            print("  ✅ cleanup_enabled = True（启用）")
        elif config.ocr_file_cleanup_enabled is False:
            print("  ℹ️  cleanup_enabled = False（禁用）")

        # 创建文件管理器（模拟workflow的方式）
        print("\n" + "=" * 80)
        print("文件管理器实例化")
        print("=" * 80)

        file_manager = OCRFileManager(
            base_dir=config.ocr_screenshot_base_dir or "screenshots",
            timestamp_format=config.ocr_screenshot_timestamp_format or "%Y%m%d_%H%M%S",
            cleanup_enabled=config.ocr_file_cleanup_enabled or False,  # ← 这里是问题所在
            cleanup_strategy=config.ocr_file_cleanup_strategy or "archive",
            archive_dir=config.ocr_file_archive_dir,
            retention_days=config.ocr_file_retention_days or 7
        )

        print(f"  实际 cleanup_enabled: {file_manager.cleanup_enabled} (类型: {type(file_manager.cleanup_enabled)})")
        print(f"  实际 base_dir: {file_manager.base_dir}")
        print(f"  实际 retention_days: {file_manager.retention_days}")
        print(f"  实际 cleanup_strategy: {file_manager.cleanup_strategy}")
        print(f"  实际 archive_dir: {file_manager.archive_dir}")

        # 检查目录状态
        print("\n" + "=" * 80)
        print("目录状态")
        print("=" * 80)

        if not file_manager.base_dir.exists():
            print(f"  ❌ 基础目录不存在: {file_manager.base_dir}")
            return

        print(f"  ✅ 基础目录存在: {file_manager.base_dir}")

        # 获取统计信息
        stats = file_manager.get_directory_stats()
        print(f"\n  总目录数: {stats['total_dirs']}")
        print(f"  总文件数: {stats['total_files']}")
        print(f"  总大小: {stats['total_size_mb']} MB")
        print(f"  最老目录: {stats['oldest_dir']}")
        print(f"  最新目录: {stats['newest_dir']}")
        print(f"  需要清理的目录数: {stats['dirs_to_cleanup']}")

        # 显示最近的目录
        print("\n" + "=" * 80)
        print("最近10个目录详情")
        print("=" * 80)

        recent_dirs = file_manager.get_recent_directories(10)
        cutoff_date = datetime.now() - timedelta(days=file_manager.retention_days)

        for i, dir_info in enumerate(recent_dirs, 1):
            age_days = dir_info['age_days']
            timestamp = dir_info['timestamp']

            status = ""
            if timestamp:
                if timestamp < cutoff_date:
                    status = "🗑️ [需要清理]"
                else:
                    status = "✅ [保留]"
            else:
                status = "⚠️ [时间戳解析失败]"

            print(f"\n  {i}. {dir_info['name']} {status}")
            print(f"     路径: {dir_info['path']}")
            print(f"     时间戳: {timestamp}")
            print(f"     年龄: {age_days} 天" if age_days is not None else "     年龄: 未知")
            print(f"     文件数: {dir_info['file_count']}")

        # 模拟执行清理（但不真正清理）
        print("\n" + "=" * 80)
        print("清理模拟")
        print("=" * 80)

        if not file_manager.cleanup_enabled:
            print("  ❌ cleanup_enabled = False，清理不会执行！")
            print("\n  🔍 问题原因分析:")
            print(f"     数据库值: {config.ocr_file_cleanup_enabled}")
            print(f"     使用 'or False': {config.ocr_file_cleanup_enabled or False}")

            if config.ocr_file_cleanup_enabled is None:
                print("     ⚠️ 数据库值是 None，'None or False' = False")
                print("     💡 解决方案：确保数据库字段有明确的值（0或1）")
            elif config.ocr_file_cleanup_enabled == 0:
                print("     ℹ️  数据库值是 0（禁用），符合预期")

        else:
            print("  ✅ cleanup_enabled = True，清理会执行")
            print(f"\n  📅 截止日期: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  📁 保留天数: {file_manager.retention_days} 天")
            print(f"  🔄 清理策略: {file_manager.cleanup_strategy}")

            if stats['dirs_to_cleanup'] > 0:
                print(f"\n  🎯 将清理 {stats['dirs_to_cleanup']} 个目录")
            else:
                print(f"\n  ℹ️  没有需要清理的目录（所有目录都在保留期内）")

        # 测试实际清理
        print("\n" + "=" * 80)
        print("实际清理测试")
        print("=" * 80)
        print("  是否执行真实清理？这将会：")
        if file_manager.cleanup_strategy == 'delete':
            print("  - 删除超过保留期的目录")
        elif file_manager.cleanup_strategy == 'archive':
            print("  - 归档超过保留期的目录")
        print()

        confirm = input("  确认执行清理？(输入 yes 确认): ")

        if confirm.lower() == 'yes':
            print("\n  🧹 执行清理...")
            cleanup_stats = file_manager.cleanup_old_files()
            print(f"\n  清理结果:")
            print(f"    删除: {cleanup_stats['deleted']}")
            print(f"    归档: {cleanup_stats['archived']}")
            print(f"    跳过: {cleanup_stats['skipped']}")
            print(f"    错误: {cleanup_stats['errors']}")
        else:
            print("\n  ⏭️  跳过实际清理")

    finally:
        db.close()

    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
