#!/usr/bin/env python3
"""
批量分析多个PDF文件的OCR布局规律
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict
from collections import defaultdict


def process_pdf_to_jsonl(pdf_path: str, output_path: str) -> bool:
    """处理PDF文件并生成JSONL"""
    script_path = "scripts/pdf_ocr_with_umi.py"

    try:
        cmd = [
            "python3", script_path,
            pdf_path, "text", "jsonl"
        ]

        with open(output_path, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.DEVNULL,
                timeout=120
            )

        return result.returncode == 0
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")
        return False


def extract_pure_jsonl(file_path: str) -> str:
    """从输出中提取纯JSONL内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找JSON对象
    import re
    match = re.search(r'\{"code".*\}', content, re.DOTALL)
    if match:
        return match.group(0)
    return None


def get_layout_stats(jsonl_data: Dict) -> Dict:
    """获取布局统计信息"""
    items = jsonl_data['data']

    stats = {
        'total_blocks': len(items),
        'page_height': 0,
        'page_width': 0,
        'avg_confidence': 0,
        'long_texts': 0,  # 长度>=20的文本块
        'horizontal_groups': 0,  # 横向对齐组
        'vertical_groups': 0,    # 纵向对齐组
        'y_range': (0, 0),
        'x_range': (0, 0),
    }

    if not items:
        return stats

    # 计算页面范围
    all_y = []
    all_x = []
    total_score = 0

    for item in items:
        box = item['box']
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        all_x.extend(x_coords)
        all_y.extend(y_coords)
        total_score += item['score']

        if len(item['text']) >= 20:
            stats['long_texts'] += 1

    stats['y_range'] = (min(all_y), max(all_y))
    stats['x_range'] = (min(all_x), max(all_x))
    stats['page_height'] = stats['y_range'][1] - stats['y_range'][0]
    stats['page_width'] = stats['x_range'][1] - stats['x_range'][0]
    stats['avg_confidence'] = total_score / len(items)

    # 检测横向对齐（表格行）
    tolerance = 15
    y_groups = defaultdict(list)
    for item in items:
        center_y = sum(p[1] for p in item['box']) / 4
        y_key = round(center_y / tolerance) * tolerance
        y_groups[y_key].append(item)

    stats['horizontal_groups'] = sum(1 for g in y_groups.values() if len(g) >= 2)

    # 检测纵向对齐（表格列）
    x_groups = defaultdict(list)
    for item in items:
        center_x = sum(p[0] for p in item['box']) / 4
        x_key = round(center_x / tolerance) * tolerance
        x_groups[x_key].append(item)

    stats['vertical_groups'] = sum(1 for g in x_groups.values() if len(g) >= 3)

    return stats


def analyze_multiple_files(pdf_files: List[str], output_dir: str):
    """批量分析多个文件"""

    print("=" * 80)
    print("📊 批量PDF布局分析")
    print("=" * 80)
    print(f"\n将分析 {len(pdf_files)} 个文件\n")

    results = []

    for i, pdf_file in enumerate(pdf_files, 1):
        filename = Path(pdf_file).name
        print(f"[{i}/{len(pdf_files)}] 处理: {filename}")

        # 生成JSONL
        jsonl_file = os.path.join(output_dir, f"file_{i:03d}.jsonl")
        print(f"  📤 上传并识别...")

        if not process_pdf_to_jsonl(pdf_file, jsonl_file):
            print(f"  ❌ 失败")
            continue

        # 提取纯JSONL
        pure_content = extract_pure_jsonl(jsonl_file)
        if not pure_content:
            print(f"  ❌ 无法提取JSONL")
            continue

        # 保存纯JSONL
        pure_jsonl_file = os.path.join(output_dir, f"file_{i:03d}_pure.jsonl")
        with open(pure_jsonl_file, 'w', encoding='utf-8') as f:
            f.write(pure_content)

        # 分析布局
        try:
            data = json.loads(pure_content)
            stats = get_layout_stats(data)

            results.append({
                'file': filename,
                'file_index': i,
                'stats': stats
            })

            print(f"  ✅ 完成: {stats['total_blocks']}个文字块, " +
                  f"置信度{stats['avg_confidence']:.1%}, " +
                  f"{stats['horizontal_groups']}个表格行, " +
                  f"{stats['vertical_groups']}个表格列")

        except Exception as e:
            print(f"  ❌ 分析失败: {e}")

        print()

    # 生成对比报告
    print("\n" + "=" * 80)
    print("📈 综合对比分析")
    print("=" * 80)

    if not results:
        print("\n没有成功分析的文件")
        return

    # 统计信息
    print(f"\n成功分析: {len(results)} 个文件\n")

    # 对比表格
    print("┌" + "─" * 8 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┬" + "─" * 12 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┐")
    print("│ 文件   │ 文字块数量 │ 表格行数   │ 表格列数   │ 段落数   │ 置信度   │")
    print("├" + "─" * 8 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 12 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┤")

    for r in results:
        stats = r['stats']
        file_num = r['file_index']

        print(f"│ {file_num:04d}   │ {stats['total_blocks']:10d} │ {stats['horizontal_groups']:10d} │ " +
              f"{stats['vertical_groups']:10d} │ {stats['long_texts']:8d} │ {stats['avg_confidence']:8.1%} │")

    print("└" + "─" * 8 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┴" + "─" * 12 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┘")

    # 统计分析
    print("\n" + "=" * 80)
    print("📊 统计摘要")
    print("=" * 80)

    total_blocks = [r['stats']['total_blocks'] for r in results]
    h_groups = [r['stats']['horizontal_groups'] for r in results]
    v_groups = [r['stats']['vertical_groups'] for r in results]
    long_texts = [r['stats']['long_texts'] for r in results]
    confidences = [r['stats']['avg_confidence'] for r in results]

    print(f"""
文字块数量:
  平均: {sum(total_blocks)/len(total_blocks):.1f}
  范围: {min(total_blocks)} - {max(total_blocks)}

表格行数:
  平均: {sum(h_groups)/len(h_groups):.1f}
  范围: {min(h_groups)} - {max(h_groups)}

表格列数:
  平均: {sum(v_groups)/len(v_groups):.1f}
  范围: {min(v_groups)} - {max(v_groups)}

长文本段落:
  平均: {sum(long_texts)/len(long_texts):.1f}
  范围: {min(long_texts)} - {max(long_texts)}

识别置信度:
  平均: {sum(confidences)/len(confidences):.2%}
  范围: {min(confidences):.2%} - {max(confidences):.2%}
""")

    # 识别规律
    print("\n" + "=" * 80)
    print("🔍 发现的规律")
    print("=" * 80)

    # 检查一致性
    block_variance = max(total_blocks) - min(total_blocks)
    if block_variance < 20:
        print("\n✅ 文字块数量高度一致 - 说明图纸模板统一")
    else:
        print(f"\n⚠️  文字块数量差异较大 (差异: {block_variance}) - 可能有不同类型的图纸")

    h_variance = max(h_groups) - min(h_groups)
    if h_variance < 5:
        print("✅ 表格行数一致 - 标题栏格式统一")
    else:
        print(f"⚠️  表格行数差异 (差异: {h_variance}) - 标题栏可能有变化")

    if min(confidences) > 0.85:
        print(f"✅ 识别质量优秀 - 所有文件置信度>{min(confidences):.1%}")
    elif min(confidences) > 0.75:
        print(f"⚠️  识别质量良好 - 最低置信度{min(confidences):.1%}")
    else:
        print(f"❌ 部分文件质量较差 - 最低置信度{min(confidences):.1%}")

    # 保存结果
    summary_file = os.path.join(output_dir, "analysis_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析完成！详细结果已保存到: {summary_file}")


if __name__ == '__main__':
    # 选择要分析的文件
    pdf_dir = "data/pdf"
    output_dir = "output/layout_analysis"

    # 选择样本文件（不同编号）
    sample_files = [
        "PCX20.01%20%E4%B8%BB%E4%BD%93%E9%92%A2%E7%BB%93%E6%9E%84%EF%BC%8820230301%EF%BC%890001.pdf",
        "PCX20.01%20%E4%B8%BB%E4%BD%93%E9%92%A2%E7%BB%93%E6%9E%84%EF%BC%8820230301%EF%BC%890010.pdf",
        "PCX20.01%20%E4%B8%BB%E4%BD%93%E9%92%A2%E7%BB%93%E6%9E%84%EF%BC%8820230301%EF%BC%890050.pdf",
        "PCX20.01%20%E4%B8%BB%E4%BD%93%E9%92%A2%E7%BB%93%E6%9E%84%EF%BC%8820230301%EF%BC%890100.pdf",
        "PCX20.01%20%E4%B8%BB%E4%BD%93%E9%92%A2%E7%BB%93%E6%9E%84%EF%BC%8820230301%EF%BC%890150.pdf",
    ]

    pdf_files = [os.path.join(pdf_dir, f) for f in sample_files]

    # 检查文件是否存在
    pdf_files = [f for f in pdf_files if os.path.exists(f)]

    if not pdf_files:
        print("❌ 找不到任何PDF文件")
        sys.exit(1)

    analyze_multiple_files(pdf_files, output_dir)
