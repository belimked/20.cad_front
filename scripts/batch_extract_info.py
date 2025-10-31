#!/usr/bin/env python3
"""
批量处理PDF图纸信息提取

工作流程:
1. 批量OCR识别PDF → JSONL
2. 批量提取信息 → JSON
3. 汇总生成报告 → CSV/Excel
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict
import csv
from datetime import datetime


def process_pdf_to_jsonl(pdf_path: str, output_dir: str) -> str:
    """处理PDF并生成JSONL文件

    Returns:
        JSONL文件路径，失败返回None
    """
    pdf_name = Path(pdf_path).stem
    jsonl_file = os.path.join(output_dir, f"{pdf_name}.jsonl")

    # 如果已存在，跳过
    if os.path.exists(jsonl_file):
        print(f"  ⏭️  已存在，跳过OCR")
        return jsonl_file

    try:
        cmd = [
            "python3", "scripts/pdf_ocr_with_umi.py",
            pdf_path, "text", "jsonl"
        ]

        with open(jsonl_file, 'w') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.DEVNULL,
                timeout=120
            )

        if result.returncode == 0:
            return jsonl_file
        else:
            return None

    except Exception as e:
        print(f"  ❌ OCR失败: {e}")
        return None


def extract_pure_jsonl(file_path: str) -> str:
    """从OCR输出中提取纯JSONL内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    match = re.search(r'\{"code".*\}', content, re.DOTALL)
    if match:
        return match.group(0)
    return None


def extract_info_from_jsonl(jsonl_file: str, output_file: str) -> Dict:
    """从JSONL提取信息

    Returns:
        提取结果字典，失败返回None
    """
    try:
        # 提取纯JSONL
        pure_content = extract_pure_jsonl(jsonl_file)
        if not pure_content:
            print(f"  ❌ JSONL格式错误")
            return None

        # 解析
        jsonl_data = json.loads(pure_content)

        # 提取信息
        from extract_drawing_info import DrawingInfoExtractor
        extractor = DrawingInfoExtractor()
        result = extractor.extract_all(jsonl_data)

        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    except Exception as e:
        print(f"  ❌ 提取失败: {e}")
        return None


def batch_process(pdf_files: List[str], output_base_dir: str):
    """批量处理PDF文件

    Args:
        pdf_files: PDF文件路径列表
        output_base_dir: 输出根目录
    """
    # 创建输出目录
    jsonl_dir = os.path.join(output_base_dir, 'jsonl')
    info_dir = os.path.join(output_base_dir, 'extracted_info')
    os.makedirs(jsonl_dir, exist_ok=True)
    os.makedirs(info_dir, exist_ok=True)

    print("=" * 80)
    print("📦 批量处理工程图纸信息")
    print("=" * 80)
    print(f"\n将处理 {len(pdf_files)} 个PDF文件\n")

    results = []
    success_count = 0
    fail_count = 0

    for i, pdf_file in enumerate(pdf_files, 1):
        filename = Path(pdf_file).name
        print(f"[{i}/{len(pdf_files)}] {filename}")

        # 步骤1: OCR识别
        print(f"  📤 OCR识别...")
        jsonl_file = process_pdf_to_jsonl(pdf_file, jsonl_dir)

        if not jsonl_file:
            print(f"  ❌ 处理失败")
            fail_count += 1
            continue

        # 步骤2: 信息提取
        print(f"  📝 信息提取...")
        pdf_name = Path(pdf_file).stem
        info_file = os.path.join(info_dir, f"{pdf_name}.json")

        result = extract_info_from_jsonl(jsonl_file, info_file)

        if not result:
            print(f"  ❌ 提取失败")
            fail_count += 1
            continue

        # 记录结果
        results.append({
            'filename': filename,
            'pdf_path': pdf_file,
            'jsonl_file': jsonl_file,
            'info_file': info_file,
            'result': result
        })

        # 显示摘要
        basic = result['basic_info']
        print(f"  ✅ 完成: 图号={basic['drawing_number'] or '?'}, " +
              f"类型={basic['drawing_type']}, " +
              f"材料={basic['material'] or '?'}")

        success_count += 1
        print()

    # 生成汇总报告
    print("\n" + "=" * 80)
    print("📊 生成汇总报告")
    print("=" * 80)

    generate_summary_report(results, output_base_dir)

    print(f"\n✅ 处理完成: 成功 {success_count}, 失败 {fail_count}")
    print(f"\n📁 输出目录: {output_base_dir}")
    print(f"  - JSONL文件: {jsonl_dir}")
    print(f"  - 提取结果: {info_dir}")
    print(f"  - 汇总报告: {output_base_dir}/summary_report.csv")


def generate_summary_report(results: List[Dict], output_dir: str):
    """生成汇总报告（CSV格式）"""

    csv_file = os.path.join(output_dir, 'summary_report.csv')

    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)

        # 写入表头
        writer.writerow([
            '文件名',
            '图号',
            '图纸类型',
            '材料',
            '公司',
            '设计',
            '审核',
            '批准',
            '比例',
            '重量',
            '技术要求条数',
            'BOM项数',
            '文字块数',
            'OCR耗时(秒)'
        ])

        # 写入数据
        for item in results:
            result = item['result']
            basic = result['basic_info']
            personnel = result['personnel']
            metadata = result['metadata']

            # 图纸类型中文
            type_map = {
                'assembly': '装配图',
                'part': '零件图',
                'simple': '简图'
            }

            writer.writerow([
                item['filename'],
                basic['drawing_number'] or '',
                type_map.get(basic['drawing_type'], basic['drawing_type']),
                basic['material'] or '',
                basic['company'] or '',
                personnel['designer'] or '',
                personnel['reviewer'] or '',
                personnel['approver'] or '',
                basic['scale'] or '',
                basic['weight'] or '',
                len(result['technical_requirements']),
                len(result['bom_table']),
                metadata['total_text_blocks'],
                f"{metadata['ocr_time']:.2f}"
            ])

    print(f"✅ CSV报告已生成: {csv_file}")

    # 生成详细报告（JSON格式）
    json_file = os.path.join(output_dir, 'detailed_report.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_files': len(results),
            'results': [
                {
                    'filename': item['filename'],
                    'info': item['result']
                }
                for item in results
            ]
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON报告已生成: {json_file}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='批量处理PDF工程图纸信息提取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 处理目录下所有PDF
  %(prog)s data/pdf -o output/batch_extraction

  # 处理特定文件
  %(prog)s file1.pdf file2.pdf -o output

  # 限制处理数量（测试用）
  %(prog)s data/pdf/*.pdf -o output --limit 10
        '''
    )

    parser.add_argument('input', nargs='+',
                        help='PDF文件或目录路径')
    parser.add_argument('-o', '--output', required=True,
                        help='输出目录')
    parser.add_argument('--limit', type=int,
                        help='限制处理文件数量（用于测试）')
    parser.add_argument('--skip-ocr', action='store_true',
                        help='跳过OCR，直接从已有JSONL提取')

    args = parser.parse_args()

    # 收集PDF文件
    pdf_files = []
    for input_path in args.input:
        if os.path.isdir(input_path):
            # 目录：查找所有PDF
            for root, dirs, files in os.walk(input_path):
                for f in files:
                    if f.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, f))
        elif os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
            # 单个文件
            pdf_files.append(input_path)

    if not pdf_files:
        print("❌ 未找到PDF文件")
        sys.exit(1)

    # 应用限制
    if args.limit:
        pdf_files = pdf_files[:args.limit]

    # 批量处理
    batch_process(pdf_files, args.output)


if __name__ == '__main__':
    main()
