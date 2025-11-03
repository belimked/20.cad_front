#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查OCR日志记录情况

Usage:
    python scripts/check_ocr_logs.py
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.database import SessionLocal
from src.models.ocr_recognition_log import OCRRecognitionLog, OCRPreprocessingPerformance


def main():
    print("\n" + "=" * 80)
    print("OCR日志检查工具")
    print("=" * 80)

    db = SessionLocal()
    try:
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()

        if 'ocr_recognition_logs' not in tables:
            print("\n❌ 表 ocr_recognition_logs 不存在")
            print("   请运行数据库迁移: python scripts/auto_migrate.py")
            return 1

        if 'ocr_preprocessing_performance' not in tables:
            print("\n❌ 表 ocr_preprocessing_performance 不存在")
            print("   请运行数据库迁移: python scripts/auto_migrate.py")
            return 1

        print("\n✅ 数据库表存在")

        # 查询记录总数
        total_logs = db.query(OCRRecognitionLog).count()
        total_perf = db.query(OCRPreprocessingPerformance).count()

        print(f"\n📊 统计信息:")
        print(f"   ocr_recognition_logs: {total_logs} 条记录")
        print(f"   ocr_preprocessing_performance: {total_perf} 条记录")

        if total_logs == 0:
            print("\n❌ 没有OCR日志记录")
            print("\n可能原因：")
            print("1. ⚠️  你运行的是硬编码版本 (11_bplot_auto_workflow.py)")
            print("   → 该脚本不记录日志")
            print()
            print("2. ✅ 需要运行配置化版本:")
            print("   → python research/autocad_com_api/12_bplot_configurable_workflow.py")
            print()
            print("3. ✅ 或者通过API调用:")
            print("   → POST /api/dwg/process")
            print("   → {\"dwg_url\": \"...\", \"config_name\": \"bplot\"}")
            print()
            print("4. ⚠️  日志记录可能失败（检查控制台输出）")
            print("   → 查找: \"📊 OCR日志已记录\" 或 \"⚠️ OCR日志记录失败\"")
            return 0

        # 显示最近的日志
        print("\n" + "=" * 80)
        print("最近5条OCR识别日志")
        print("=" * 80)

        logs = db.query(OCRRecognitionLog).order_by(
            OCRRecognitionLog.created_at.desc()
        ).limit(5).all()

        for log in logs:
            print(f"\nID: {log.id}")
            print(f"  目标文本: '{log.target_text}'")
            print(f"  是否找到: {'✅ 是' if log.found else '❌ 否'}")
            if log.matched_text:
                print(f"  匹配文本: '{log.matched_text}'")
            if log.confidence:
                print(f"  置信度: {log.confidence:.4f}")
            if log.matched_version:
                print(f"  匹配版本: {log.matched_version}")
            if log.position_x and log.position_y:
                print(f"  点击位置: ({log.position_x}, {log.position_y})")
            print(f"  总耗时: {log.total_time:.3f}秒")
            print(f"  预处理方法数: {log.preprocessing_count}")
            print(f"  识别文本总数: {log.total_texts_found} → {log.unique_texts_count} (去重后)")
            print(f"  创建时间: {log.created_at}")
            print(f"  状态: {log.status}")

            # 查询对应的预处理性能记录
            perfs = db.query(OCRPreprocessingPerformance).filter(
                OCRPreprocessingPerformance.recognition_log_id == log.id
            ).order_by(OCRPreprocessingPerformance.method_order).all()

            if perfs:
                print(f"\n  预处理性能详情 ({len(perfs)} 个方法):")
                for perf in perfs:
                    found_marker = "✅" if perf.target_found else "❌"
                    print(f"    {perf.method_order}. {found_marker} {perf.method_name}")
                    print(f"       处理: {perf.processing_time:.3f}s | OCR: {perf.ocr_time:.3f}s | 总计: {perf.total_time:.3f}s")
                    print(f"       文本数: {perf.texts_found} | 最高置信度: {perf.max_confidence if perf.max_confidence else 'N/A'}")

            print("-" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
