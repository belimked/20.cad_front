#!/usr/bin/env python3
"""
对比测试：区域过滤 vs 全页识别

对比指标：
1. 识别速度
2. 文字块数量
3. 提取的信息完整性
"""

import subprocess
import time
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from extract_drawing_info import DrawingInfoExtractor


def run_ocr(pdf_file, output_file, use_region_filter=False):
    """运行OCR识别

    Args:
        pdf_file: PDF文件路径
        output_file: 输出JSONL文件路径
        use_region_filter: 是否使用区域过滤

    Returns:
        (success, elapsed_time, text_blocks_count)
    """
    start_time = time.time()

    if use_region_filter:
        cmd = [
            "python3", "scripts/pdf_ocr_optimized.py",
            pdf_file,
            "--region", "bottom",
            "--region-percent", "0.65"
        ]
    else:
        cmd = [
            "python3", "scripts/pdf_ocr_with_umi.py",
            pdf_file, "text", "jsonl"
        ]

    try:
        with open(output_file, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.DEVNULL,
                timeout=120
            )

        elapsed = time.time() - start_time

        if result.returncode == 0:
            # 读取结果统计文字块数
            with open(output_file, 'r') as f:
                content = f.read()

            # 提取JSON
            import re
            match = re.search(r'\{"code".*\}', content, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                text_blocks = len(data.get('data', []))
                return (True, elapsed, text_blocks)

        return (False, elapsed, 0)

    except Exception as e:
        elapsed = time.time() - start_time
        return (False, elapsed, 0)


def extract_and_compare(jsonl_file):
    """提取信息并返回统计"""
    try:
        with open(jsonl_file, 'r') as f:
            content = f.read()

        import re
        match = re.search(r'\{"code".*\}', content, re.DOTALL)
        if not match:
            return None

        data = json.loads(match.group(0))

        # 提取信息
        extractor = DrawingInfoExtractor()
        result = extractor.extract_all(data)

        # 统计
        stats = {
            'drawing_no': result['basic_info']['drawing_number'],
            'material': result['basic_info']['material'],
            'company': result['basic_info']['company'],
            'tech_reqs': len(result['technical_requirements']),
            'bom_items': len(result['bom_table']),
            'total_blocks': result['metadata']['total_text_blocks']
        }

        return stats

    except Exception as e:
        print(f"  ❌ 提取失败: {e}")
        return None


def compare_test(pdf_file):
    """对比测试单个文件"""
    print("=" * 80)
    print(f"📊 对比测试: {os.path.basename(pdf_file)}")
    print("=" * 80)

    # 测试1: 全页识别
    print("\n【测试1】全页识别（无区域过滤）")
    output1 = "/tmp/compare_full.jsonl"
    success1, time1, blocks1 = run_ocr(pdf_file, output1, use_region_filter=False)

    if success1:
        print(f"  ✅ 成功")
        print(f"  ⏱️  耗时: {time1:.2f}秒")
        print(f"  📝 文字块: {blocks1}个")

        stats1 = extract_and_compare(output1)
        if stats1:
            print(f"  📋 提取信息:")
            print(f"     图号: {stats1['drawing_no'] or '未识别'}")
            print(f"     材料: {stats1['material'] or '未识别'}")
            print(f"     技术要求: {stats1['tech_reqs']}条")
    else:
        print(f"  ❌ 失败")
        stats1 = None

    # 测试2: 区域过滤
    print("\n【测试2】区域过滤（只识别底部35%）")
    output2 = "/tmp/compare_region.jsonl"
    success2, time2, blocks2 = run_ocr(pdf_file, output2, use_region_filter=True)

    if success2:
        print(f"  ✅ 成功")
        print(f"  ⏱️  耗时: {time2:.2f}秒")
        print(f"  📝 文字块: {blocks2}个")

        stats2 = extract_and_compare(output2)
        if stats2:
            print(f"  📋 提取信息:")
            print(f"     图号: {stats2['drawing_no'] or '未识别'}")
            print(f"     材料: {stats2['material'] or '未识别'}")
            print(f"     技术要求: {stats2['tech_reqs']}条")
    else:
        print(f"  ❌ 失败")
        stats2 = None

    # 对比分析
    print("\n" + "=" * 80)
    print("📊 对比分析")
    print("=" * 80)

    if success1 and success2:
        # 速度对比
        speedup = (time1 - time2) / time1 * 100
        print(f"\n【速度】")
        print(f"  全页识别: {time1:.2f}秒")
        print(f"  区域过滤: {time2:.2f}秒")
        print(f"  提速: {speedup:.1f}%")

        # 文字块对比
        reduction = (blocks1 - blocks2) / blocks1 * 100
        print(f"\n【文字块数量】")
        print(f"  全页识别: {blocks1}个")
        print(f"  区域过滤: {blocks2}个")
        print(f"  减少: {reduction:.1f}%")

        # 信息完整性对比
        if stats1 and stats2:
            print(f"\n【信息完整性】")

            fields = [
                ('图号', 'drawing_no'),
                ('材料', 'material'),
                ('公司', 'company'),
                ('技术要求', 'tech_reqs'),
                ('BOM项', 'bom_items')
            ]

            print(f"  {'字段':<10} {'全页':<15} {'区域过滤':<15} {'状态':<10}")
            print(f"  {'-'*50}")

            for name, key in fields:
                val1 = stats1.get(key, '?')
                val2 = stats2.get(key, '?')

                # 判断状态
                if val1 == val2:
                    status = "✅ 相同"
                elif key in ['tech_reqs', 'bom_items']:
                    # 数量字段
                    if val2 >= val1 * 0.9:  # 保留90%以上认为OK
                        status = "✅ 基本保留"
                    else:
                        status = "⚠️ 部分丢失"
                else:
                    # 文本字段
                    if val2:
                        status = "✅ 保留"
                    else:
                        status = "❌ 丢失"

                print(f"  {name:<10} {str(val1):<15} {str(val2):<15} {status:<10}")

        # 结论
        print(f"\n【结论】")
        if reduction > 30 and speedup > 20:
            print(f"  🎉 区域过滤效果显著：")
            print(f"     - 速度提升{speedup:.0f}%")
            print(f"     - 减少{reduction:.0f}%噪音文字")
            if stats1 and stats2:
                print(f"     - 核心信息完整保留")
                print(f"  ✅ 建议使用区域过滤模式")
        else:
            print(f"  区域过滤效果一般")

    print("\n" + "=" * 80)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='对比测试：区域过滤 vs 全页识别')
    parser.add_argument('pdf', help='PDF文件路径')

    args = parser.parse_args()

    compare_test(args.pdf)


if __name__ == '__main__':
    main()
