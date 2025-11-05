#!/usr/bin/env python3
"""
优化版OCR识别 - 支持区域裁剪
专注于右下角标题栏区域，忽略图形和尺寸标注区域
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pdf_ocr_with_umi import UmiOCRDocProcessor
import json
from pathlib import Path
from typing import Optional, List, Dict


class OptimizedOCRProcessor(UmiOCRDocProcessor):
    """优化的OCR处理器 - 支持区域裁剪"""

    def upload_pdf_with_region(
        self,
        pdf_path: str,
        ignore_top_percent: float = 0.65,  # 忽略顶部65%（保留底部35%）
        page_range_start: int = 1,
        page_range_end: int = -1,
        language: str = "models/config_chinese.txt",
        extraction_mode: str = "fullPage",
        parser: str = "multi_line"
    ) -> Optional[str]:
        """
        上传PDF并设置识别区域（专注于右下角标题栏）

        Args:
            pdf_path: PDF文件路径
            ignore_top_percent: 忽略顶部百分比（0-1）
                默认0.65表示忽略顶部65%，只识别底部35%
            其他参数同upload_pdf

        Returns:
            任务ID
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ 文件不存在: {pdf_path}")
            return None

        print(f"\n📤 上传PDF文件: {pdf_file.name}")
        print(f"   文件大小: {pdf_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"   🎯 识别区域: 底部{(1-ignore_top_percent)*100:.0f}% (标题栏区域)")

        # 准备配置
        config = {
            "ocr.language": language,
            "doc.pageRangeStart": page_range_start,
            "doc.pageRangeEnd": page_range_end,
            "doc.extractionMode": extraction_mode,
            "tbpu.parser": parser,
        }

        # 使用tbpu.ignoreArea参数忽略顶部和中间区域
        # 格式: [[[左上角x,y],[右下角x,y]], ...]
        #
        # 根据布局分析：
        # - TOP区域 (Y: 0-450) - 图纸标题、部分尺寸
        # - MIDDLE区域 (Y: 450-800) - 图形主体
        # - BOTTOM区域 (Y: 800-1200) - 标题栏+技术要求 (需要保留)
        #
        # 典型页面尺寸约1700x1200，我们忽略Y<800的区域

        # 计算忽略区域的Y坐标（假设页面高度1200）
        page_height = 1200  # 典型A3/A4图纸高度（像素）
        page_width = 1700   # 典型宽度

        ignore_y_threshold = int(page_height * ignore_top_percent)

        # 忽略顶部区域（从0到阈值）
        ignore_areas = [
            [[0, 0], [page_width, ignore_y_threshold]]  # 忽略整个顶部
        ]

        config["tbpu.ignoreArea"] = ignore_areas

        print(f"   📍 忽略区域: Y < {ignore_y_threshold} (保留底部标题栏)")

        # 上传文件
        url = f"{self.base_url}/api/doc/upload"

        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file.name, f, 'application/pdf')}
            data = {'json': json.dumps(config)}

            try:
                response = requests.post(url, files=files, data=data, timeout=60)
                result = response.json()

                if result.get('code') == 100:
                    self.task_id = result.get('data')
                    print(f"   ✅ 上传成功，任务ID: {self.task_id}")
                    return self.task_id
                else:
                    print(f"   ❌ 上传失败: {result.get('data', '未知错误')}")
                    return None

            except Exception as e:
                print(f"   ❌ 上传异常: {e}")
                return None


def test_region_parameters():
    """测试区域参数支持"""
    import requests

    base_url = "http://10.3.19.63:11224"

    print("=" * 80)
    print("🔍 测试Umi-OCR区域参数支持")
    print("=" * 80)

    # 测试配置
    test_configs = [
        {
            "name": "ignoreArea (忽略区域)",
            "config": {"ocr.ignoreArea": [[0, 0, 100, 65]]}
        },
        {
            "name": "limitArea (限定区域)",
            "config": {"ocr.limitArea": [0, 65, 100, 100]}
        },
        {
            "name": "clipArea (裁剪区域)",
            "config": {"ocr.clipArea": [0, 65, 100, 100]}
        },
        {
            "name": "ocr.clip (裁剪)",
            "config": {"ocr.clip": "bottom"}
        }
    ]

    print("\n测试文件: 使用小PDF测试")
    print("\n支持的参数:")

    # 注意：实际测试需要真实PDF文件
    # 这里只是展示可能的参数名称

    for test in test_configs:
        print(f"  - {test['name']}: {test['config']}")

    print("\n" + "=" * 80)
    print("💡 建议:")
    print("  1. 查阅Umi-OCR官方文档确认参数名称")
    print("  2. 使用小文件测试各参数")
    print("  3. 如不支持区域参数，可考虑后处理过滤")
    print("=" * 80)


def filter_by_region_post_process(jsonl_data: Dict, y_threshold: float = 0.65) -> Dict:
    """
    后处理方式：从JSONL结果中过滤区域

    Args:
        jsonl_data: OCR结果JSON
        y_threshold: Y坐标阈值（百分比）

    Returns:
        过滤后的JSON数据
    """
    if 'data' not in jsonl_data:
        return jsonl_data

    items = jsonl_data['data']

    # 计算页面高度
    all_y = []
    for item in items:
        box = item['box']
        y_coords = [p[1] for p in box]
        all_y.extend(y_coords)

    if not all_y:
        return jsonl_data

    y_min = min(all_y)
    y_max = max(all_y)
    page_height = y_max - y_min

    # 计算阈值Y坐标
    threshold_y = y_min + page_height * y_threshold

    # 过滤：只保留Y坐标在阈值以下的文字块
    filtered_items = []
    for item in items:
        # 获取中心Y坐标
        center_y = sum(p[1] for p in item['box']) / 4

        # 只保留底部区域
        if center_y >= threshold_y:
            filtered_items.append(item)

    print(f"\n🎯 区域过滤结果:")
    print(f"   原始文字块: {len(items)}个")
    print(f"   过滤后文字块: {len(filtered_items)}个")
    print(f"   保留比例: {len(filtered_items)/len(items)*100:.1f}%")
    print(f"   阈值Y坐标: {threshold_y:.0f} (保留Y≥{threshold_y:.0f}的文字)")

    # 创建新的结果
    filtered_jsonl = jsonl_data.copy()
    filtered_jsonl['data'] = filtered_items

    return filtered_jsonl


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='优化版OCR识别 - 支持区域裁剪',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:

  # 测试区域参数支持
  %(prog)s --test-params

  # 只识别底部35%区域（标题栏）
  %(prog)s input.pdf --region bottom

  # 自定义保留区域（保留底部40%）
  %(prog)s input.pdf --region-percent 0.60

  # 后处理过滤（适用于不支持区域参数的情况）
  %(prog)s input.jsonl --post-filter

区域说明:
  - 默认识别底部35%区域（Y > 65%）
  - 包含标题栏、技术要求、BOM表等核心信息
  - 排除顶部和中间的图形、尺寸标注
        '''
    )

    parser.add_argument('input', nargs='?', help='输入PDF或JSONL文件')
    parser.add_argument('--test-params', action='store_true',
                        help='测试区域参数支持')
    parser.add_argument('--region', choices=['bottom', 'all'],
                        default='bottom', help='识别区域（默认bottom）')
    parser.add_argument('--region-percent', type=float, default=0.65,
                        help='忽略顶部百分比（0-1，默认0.65）')
    parser.add_argument('--post-filter', action='store_true',
                        help='后处理过滤模式（用于已生成的JSONL）')
    parser.add_argument('-o', '--output', help='输出文件路径')

    args = parser.parse_args()

    # 测试参数模式
    if args.test_params:
        test_region_parameters()
        return

    if not args.input:
        parser.print_help()
        return

    # 后处理过滤模式
    if args.post_filter:
        print("📝 后处理过滤模式")

        # 读取JSONL
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取JSON对象
        import re
        match = re.search(r'\{"code".*\}', content, re.DOTALL)
        if not match:
            print("❌ 无效的JSONL文件")
            return

        jsonl_data = json.loads(match.group(0))

        # 过滤区域
        filtered = filter_by_region_post_process(jsonl_data, args.region_percent)

        # 输出
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存到: {args.output}")
        else:
            print(json.dumps(filtered, ensure_ascii=False, indent=2))

        return

    # OCR识别模式
    print("📤 OCR识别模式")

    processor = OptimizedOCRProcessor()

    # 上传并识别
    if args.region == 'bottom':
        task_id = processor.upload_pdf_with_region(
            args.input,
            ignore_top_percent=args.region_percent
        )
    else:
        # 全页识别
        task_id = processor.upload_pdf(args.input)

    if not task_id:
        print("❌ 上传失败")
        return

    # 等待完成
    result = processor.wait_for_completion(task_id)

    if not result:
        print("❌ 识别失败")
        return

    # 下载结果
    text = processor.download_result(task_id, file_types=['txtPlain'])

    if text:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ 已保存到: {args.output}")
        else:
            print(text)

    # 清理
    processor.clean_task(task_id)


if __name__ == '__main__':
    import requests
    main()
