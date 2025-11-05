#!/usr/bin/env python3
"""
简化的区域过滤测试 - 仅使用后处理方式
对比全页识别 vs 区域过滤的文字块数量和信息完整性
"""

import subprocess
import json
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from extract_drawing_info import DrawingInfoExtractor


def process_pdf_full(pdf_path: str, output_path: str) -> dict:
    """全页识别"""
    print(f"\n【步骤1】全页识别 - {Path(pdf_path).name}")

    cmd = [
        "python3", "scripts/pdf_ocr_with_umi.py",
        pdf_path, "text", "jsonl"
    ]

    with open(output_path, 'w') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.DEVNULL, timeout=120)

    if result.returncode != 0:
        return None

    # 读取结果
    with open(output_path, 'r') as f:
        content = f.read()

    match = re.search(r'\{"code".*\}', content, re.DOTALL)
    if not match:
        return None

    data = json.loads(match.group(0))
    return data


def filter_region_post(jsonl_data: dict, y_threshold: float = 0.65) -> dict:
    """后处理区域过滤"""
    print(f"\n【步骤2】应用区域过滤 (保留底部{(1-y_threshold)*100:.0f}%)")

    items = jsonl_data.get('data', [])

    # 计算页面高度
    all_y = []
    for item in items:
        y_coords = [p[1] for p in item['box']]
        all_y.extend(y_coords)

    if not all_y:
        return jsonl_data

    y_min, y_max = min(all_y), max(all_y)
    page_height = y_max - y_min
    threshold_y = y_min + page_height * y_threshold

    # 过滤
    filtered_items = []
    for item in items:
        center_y = sum(p[1] for p in item['box']) / 4
        if center_y >= threshold_y:
            filtered_items.append(item)

    print(f"  原始文字块: {len(items)}个")
    print(f"  过滤后文字块: {len(filtered_items)}个")
    print(f"  减少: {len(items) - len(filtered_items)}个 ({(len(items) - len(filtered_items))/len(items)*100:.1f}%)")

    filtered_data = jsonl_data.copy()
    filtered_data['data'] = filtered_items

    return filtered_data


def extract_info(jsonl_data: dict) -> dict:
    """提取信息"""
    extractor = DrawingInfoExtractor()
    result = extractor.extract_all(jsonl_data)
    return result


def compare_results(original_info: dict, filtered_info: dict):
    """对比结果"""
    print("\n" + "=" * 80)
    print("📊 信息完整性对比")
    print("=" * 80)

    fields = [
        ('图号', 'drawing_number'),
        ('材料', 'material'),
        ('公司', 'company'),
    ]

    print(f"\n{'字段':<10} {'全页识别':<30} {'区域过滤':<30} {'状态'}")
    print("-" * 80)

    for name, key in fields:
        val1 = original_info['basic_info'].get(key, '未识别')
        val2 = filtered_info['basic_info'].get(key, '未识别')

        status = "✅ 相同" if val1 == val2 else "⚠️ 不同"

        print(f"{name:<10} {str(val1)[:28]:<30} {str(val2)[:28]:<30} {status}")

    # 技术要求
    tech1 = len(original_info.get('technical_requirements', []))
    tech2 = len(filtered_info.get('technical_requirements', []))
    status = "✅ 相同" if tech1 == tech2 else f"⚠️ {tech2}/{tech1}"
    print(f"{'技术要求':<10} {f'{tech1}条':<30} {f'{tech2}条':<30} {status}")

    # BOM表
    bom1 = len(original_info.get('bom_table', []))
    bom2 = len(filtered_info.get('bom_table', []))
    status = "✅ 相同" if bom1 == bom2 else f"⚠️ {bom2}/{bom1}"
    print(f"{'BOM项':<10} {f'{bom1}项':<30} {f'{bom2}项':<30} {status}")

    # 统计
    blocks1 = original_info['metadata']['total_text_blocks']
    blocks2 = filtered_info['metadata']['total_text_blocks']
    reduction = (blocks1 - blocks2) / blocks1 * 100

    print(f"\n{'文字块':<10} {f'{blocks1}个':<30} {f'{blocks2}个':<30} ⬇️ {reduction:.1f}%")

    # 结论
    print("\n" + "=" * 80)
    print("📝 结论")
    print("=" * 80)

    # 检查核心信息是否完整
    core_complete = (
        original_info['basic_info']['drawing_number'] == filtered_info['basic_info']['drawing_number'] and
        original_info['basic_info']['material'] == filtered_info['basic_info']['material'] and
        tech1 == tech2
    )

    if core_complete and reduction > 10:
        print(f"✅ 区域过滤效果显著:")
        print(f"   - 核心信息100%保留 (图号、材料、技术要求)")
        print(f"   - 减少{reduction:.0f}%文字块 (过滤尺寸标注等噪音)")
        print(f"   - 推荐使用区域过滤")
    elif core_complete:
        print(f"⚠️ 区域过滤效果一般:")
        print(f"   - 核心信息100%保留")
        print(f"   - 仅减少{reduction:.0f}%文字块")
        print(f"   - 可选使用 (提升有限)")
    else:
        print(f"❌ 区域过滤导致信息丢失:")
        print(f"   - 核心信息不完整")
        print(f"   - 不推荐使用")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='测试区域过滤效果 (后处理方式)')
    parser.add_argument('pdf', help='PDF文件路径')
    parser.add_argument('--region-percent', type=float, default=0.65,
                        help='忽略顶部百分比 (默认0.65)')

    args = parser.parse_args()

    print("=" * 80)
    print(f"📊 区域过滤测试 - {Path(args.pdf).name}")
    print("=" * 80)

    # 临时文件
    temp_full = "/tmp/test_full.jsonl"

    # Step 1: 全页识别
    full_data = process_pdf_full(args.pdf, temp_full)
    if not full_data:
        print("❌ 全页识别失败")
        return

    full_info = extract_info(full_data)

    # Step 2: 区域过滤
    filtered_data = filter_region_post(full_data, args.region_percent)
    filtered_info = extract_info(filtered_data)

    # Step 3: 对比
    compare_results(full_info, filtered_info)

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
