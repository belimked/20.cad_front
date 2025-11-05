#!/usr/bin/env python3
"""
分析OCR结果的坐标布局，识别段落、表格等结构
"""

import json
from collections import defaultdict
from typing import List, Dict, Tuple


def load_jsonl(file_path: str) -> Dict:
    """加载JSONL文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_center(box: List[List[float]]) -> Tuple[float, float]:
    """获取边界框的中心点"""
    x = sum(p[0] for p in box) / 4
    y = sum(p[1] for p in box) / 4
    return (x, y)


def get_bbox(box: List[List[float]]) -> Tuple[float, float, float, float]:
    """获取边界框 (x_min, y_min, x_max, y_max)"""
    x_coords = [p[0] for p in box]
    y_coords = [p[1] for p in box]
    return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))


def analyze_layout(data: Dict, tolerance: float = 10):
    """分析布局结构

    Args:
        data: JSONL数据
        tolerance: 坐标对齐容差（像素）
    """

    items = data['data']

    print("=" * 80)
    print("📐 OCR布局分析")
    print("=" * 80)
    print(f"\n总文字块数: {len(items)}")

    # 1. 按Y坐标分组（识别横向对齐的文字 - 可能是表格行）
    print("\n" + "=" * 80)
    print("📊 横向对齐分析（表格行检测）")
    print("=" * 80)

    y_groups = defaultdict(list)
    for item in items:
        center_x, center_y = get_center(item['box'])
        # 将Y坐标归类到容差范围内
        y_key = round(center_y / tolerance) * tolerance
        y_groups[y_key].append({
            'text': item['text'],
            'x': center_x,
            'y': center_y,
            'score': item['score'],
            'bbox': get_bbox(item['box'])
        })

    # 找出包含多个文字块的行（可能是表格行）
    table_rows = []
    for y, group in sorted(y_groups.items()):
        if len(group) >= 2:  # 至少2个文字块才可能是表格
            # 按X坐标排序
            group.sort(key=lambda x: x['x'])
            texts = [item['text'] for item in group]
            table_rows.append({
                'y': y,
                'count': len(group),
                'items': group,
                'text_line': ' | '.join(texts)
            })

    # 显示可能的表格行（按包含文字块数量排序）
    table_rows.sort(key=lambda x: x['count'], reverse=True)
    print(f"\n检测到 {len(table_rows)} 个可能的表格行:\n")
    for i, row in enumerate(table_rows[:10], 1):  # 显示前10行
        print(f"【行 {i}】Y≈{row['y']:.0f}, 包含{row['count']}个文字块, 置信度avg={sum(item['score'] for item in row['items'])/row['count']:.2%}")
        print(f"  内容: {row['text_line']}")
        print()

    # 2. 按X坐标分组（识别纵向对齐的文字 - 可能是表格列）
    print("\n" + "=" * 80)
    print("📊 纵向对齐分析（表格列检测）")
    print("=" * 80)

    x_groups = defaultdict(list)
    for item in items:
        center_x, center_y = get_center(item['box'])
        # 将X坐标归类到容差范围内
        x_key = round(center_x / tolerance) * tolerance
        x_groups[x_key].append({
            'text': item['text'],
            'x': center_x,
            'y': center_y,
            'score': item['score']
        })

    # 找出包含多个文字块的列
    table_cols = []
    for x, group in sorted(x_groups.items()):
        if len(group) >= 3:  # 至少3个文字块才可能是表格列
            # 按Y坐标排序
            group.sort(key=lambda x: x['y'])
            texts = [item['text'] for item in group]
            table_cols.append({
                'x': x,
                'count': len(group),
                'items': group,
                'texts': texts
            })

    print(f"\n检测到 {len(table_cols)} 个可能的表格列:\n")
    for i, col in enumerate(table_cols[:5], 1):  # 显示前5列
        print(f"【列 {i}】X≈{col['x']:.0f}, 包含{col['count']}个文字块")
        print(f"  内容: {' → '.join(col['texts'][:5])}" + (" ..." if len(col['texts']) > 5 else ""))
        print()

    # 3. 区域聚类（识别段落）
    print("\n" + "=" * 80)
    print("📝 区域聚类分析（段落检测）")
    print("=" * 80)

    # 找出长文本（可能是段落）
    long_texts = []
    for item in items:
        if len(item['text']) >= 20:  # 文字长度>=20的可能是段落
            x_min, y_min, x_max, y_max = get_bbox(item['box'])
            long_texts.append({
                'text': item['text'],
                'bbox': (x_min, y_min, x_max, y_max),
                'score': item['score'],
                'width': x_max - x_min,
                'area': (x_max - x_min) * (y_max - y_min)
            })

    long_texts.sort(key=lambda x: x['area'], reverse=True)

    print(f"\n检测到 {len(long_texts)} 个长文本段落:\n")
    for i, item in enumerate(long_texts[:10], 1):
        x_min, y_min, x_max, y_max = item['bbox']
        print(f"【段落 {i}】位置:({x_min:.0f},{y_min:.0f})-({x_max:.0f},{y_max:.0f}), 宽度:{item['width']:.0f}, 置信度:{item['score']:.2%}")
        print(f"  内容: {item['text']}")
        print()

    # 4. 按区域划分（基于Y坐标范围）
    print("\n" + "=" * 80)
    print("🗺️  页面区域划分")
    print("=" * 80)

    # 计算Y坐标范围
    all_y = []
    for item in items:
        _, y_min, _, y_max = get_bbox(item['box'])
        all_y.extend([y_min, y_max])

    y_min_page = min(all_y)
    y_max_page = max(all_y)
    page_height = y_max_page - y_min_page

    # 将页面分为3个区域
    regions = {
        'top': (y_min_page, y_min_page + page_height / 3),
        'middle': (y_min_page + page_height / 3, y_min_page + 2 * page_height / 3),
        'bottom': (y_min_page + 2 * page_height / 3, y_max_page)
    }

    region_items = defaultdict(list)
    for item in items:
        center_x, center_y = get_center(item['box'])
        for region_name, (y_start, y_end) in regions.items():
            if y_start <= center_y < y_end:
                region_items[region_name].append(item['text'])
                break

    print(f"\n页面Y坐标范围: {y_min_page:.0f} - {y_max_page:.0f} (高度: {page_height:.0f})\n")
    for region_name, (y_start, y_end) in regions.items():
        texts = region_items[region_name]
        print(f"【{region_name.upper()}区域】Y: {y_start:.0f}-{y_end:.0f}, 文字块数: {len(texts)}")
        if texts:
            # 显示前5个文字块
            preview = ' | '.join(texts[:5])
            if len(texts) > 5:
                preview += " ..."
            print(f"  内容预览: {preview}")
        print()

    # 5. 特殊模式识别
    print("\n" + "=" * 80)
    print("🔍 特殊模式识别")
    print("=" * 80)

    # 识别图号模式
    drawing_numbers = []
    for item in items:
        text = item['text']
        # 图号通常包含"-"并且是字母数字组合
        if '-' in text and any(c.isdigit() for c in text) and any(c.isalpha() or c in 'PCX' for c in text):
            if len(text) >= 10:  # 图号长度通常>=10
                center_x, center_y = get_center(item['box'])
                drawing_numbers.append({
                    'text': text,
                    'x': center_x,
                    'y': center_y,
                    'score': item['score']
                })

    if drawing_numbers:
        print(f"\n检测到 {len(drawing_numbers)} 个可能的图号:\n")
        for i, dn in enumerate(drawing_numbers, 1):
            print(f"  {i}. {dn['text']} (位置: {dn['x']:.0f}, {dn['y']:.0f}, 置信度: {dn['score']:.2%})")

    # 识别材料标识
    materials = []
    for item in items:
        text = item['text']
        # 常见材料代号
        if text in ['Q235B', 'Q345B', '304', '316L'] or (text.startswith('Q') and any(c.isdigit() for c in text)):
            center_x, center_y = get_center(item['box'])
            materials.append({
                'text': text,
                'x': center_x,
                'y': center_y,
                'score': item['score']
            })

    if materials:
        print(f"\n检测到 {len(materials)} 个材料标识:\n")
        for i, mat in enumerate(materials, 1):
            print(f"  {i}. {mat['text']} (位置: {mat['x']:.0f}, {mat['y']:.0f}, 置信度: {mat['score']:.2%})")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        jsonl_file = sys.argv[1]
    else:
        jsonl_file = 'output/samples/pure_sample.jsonl'

    print(f"\n分析文件: {jsonl_file}\n")

    data = load_jsonl(jsonl_file)
    analyze_layout(data, tolerance=15)

    print("\n✅ 分析完成！\n")
