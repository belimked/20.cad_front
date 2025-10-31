#!/usr/bin/env python3
"""
工程图纸信息自动提取工具

支持提取:
- 图号、材料、公司信息
- 设计人员、审核人员、批准人员
- 技术要求
- 零件BOM表（装配图）
- 图纸说明/备注

策略: 位置规则 + 关键词匹配 + 模式识别
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from pathlib import Path


class DrawingInfoExtractor:
    """工程图纸信息提取器"""

    def __init__(self, tolerance: int = 15):
        """
        Args:
            tolerance: 坐标对齐容差（像素）
        """
        self.tolerance = tolerance

    def get_center(self, box: List[List[float]]) -> Tuple[float, float]:
        """获取边界框中心点"""
        x = sum(p[0] for p in box) / 4
        y = sum(p[1] for p in box) / 4
        return (x, y)

    def get_bbox(self, box: List[List[float]]) -> Tuple[float, float, float, float]:
        """获取边界框 (x_min, y_min, x_max, y_max)"""
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))

    def extract_drawing_number(self, items: List[Dict]) -> Optional[str]:
        """提取图号

        策略:
        1. 模式匹配: PCX[数字]-[数字]-... 格式
        2. 位置约束: X: 1000-1400, Y: 850-1050
        3. 关键词附近: "图号"字段附近
        """
        candidates = []

        for item in items:
            text = item['text'].strip()
            center_x, center_y = self.get_center(item['box'])

            # 模式1: 标准图号格式
            if re.match(r'^[A-Z]{2,}[0-9\-\.]+$', text) and '-' in text:
                # 位置检查
                if 1000 <= center_x <= 1400 and 850 <= center_y <= 1050:
                    candidates.append({
                        'text': text,
                        'score': item['score'],
                        'confidence': 0.9,  # 高置信度
                        'method': 'pattern+position'
                    })
                else:
                    candidates.append({
                        'text': text,
                        'score': item['score'],
                        'confidence': 0.6,  # 中等置信度
                        'method': 'pattern'
                    })

        # 策略2: 查找"图号"关键词附近的文本
        for i, item in enumerate(items):
            if '图号' in item['text']:
                # 查找附近的文本（右侧或下方）
                base_x, base_y = self.get_center(item['box'])

                for j, other in enumerate(items):
                    if i == j:
                        continue

                    other_x, other_y = self.get_center(other['box'])

                    # 在右侧（X差距50-300）或下方（Y差距10-50）
                    if ((base_x + 50 <= other_x <= base_x + 300 and abs(base_y - other_y) < 20) or
                        (abs(base_x - other_x) < 50 and base_y + 10 <= other_y <= base_y + 50)):

                        other_text = other['text'].strip()
                        # 检查是否像图号
                        if len(other_text) >= 5 and ('-' in other_text or re.search(r'\d', other_text)):
                            candidates.append({
                                'text': other_text,
                                'score': other['score'],
                                'confidence': 0.7,
                                'method': 'keyword_nearby'
                            })

        # 选择最佳候选
        if candidates:
            # 过滤：排除不完整的图号（以"-"结尾）
            complete_candidates = [c for c in candidates if not c['text'].endswith('-')]

            # 如果有完整的，优先使用
            if complete_candidates:
                # 按文本长度（更完整）、置信度、OCR得分排序
                complete_candidates.sort(
                    key=lambda x: (len(x['text']), x['confidence'], x['score']),
                    reverse=True
                )
                return complete_candidates[0]['text']
            else:
                # 没有完整的，选最佳的
                candidates.sort(key=lambda x: (x['confidence'], x['score']), reverse=True)
                return candidates[0]['text']

        return None

    def extract_material(self, items: List[Dict]) -> Optional[str]:
        """提取材料信息

        策略:
        1. 关键词匹配: Q235B, Q345B, 304, 316L等
        2. 位置约束: X > 1500, Y: 850-1050
        3. "材料"关键词附近
        """
        candidates = []

        # 常见材料代号
        material_patterns = [
            r'Q\d{3}[A-Z]?',  # Q235B, Q345等
            r'\d{3}L?',        # 304, 316L等
            r'.*钢.*',         # XX钢
            r'.*mm.*板.*',     # XXmm厚钢板
        ]

        for item in items:
            text = item['text'].strip()
            center_x, center_y = self.get_center(item['box'])

            # 策略1: 模式匹配
            for pattern in material_patterns:
                if re.search(pattern, text):
                    # 位置检查
                    if center_x > 1500 and 850 <= center_y <= 1050:
                        candidates.append({
                            'text': text,
                            'score': item['score'],
                            'confidence': 0.9,
                            'method': 'pattern+position'
                        })
                    else:
                        candidates.append({
                            'text': text,
                            'score': item['score'],
                            'confidence': 0.6,
                            'method': 'pattern'
                        })

        # 策略2: "材料"关键词附近
        for i, item in enumerate(items):
            if '材料' in item['text'] or '料' in item['text']:
                base_x, base_y = self.get_center(item['box'])

                for j, other in enumerate(items):
                    if i == j:
                        continue

                    other_x, other_y = self.get_center(other['box'])

                    # 附近文本
                    if ((base_x + 20 <= other_x <= base_x + 300 and abs(base_y - other_y) < 20) or
                        (abs(base_x - other_x) < 50 and base_y + 10 <= other_y <= base_y + 50)):

                        other_text = other['text'].strip()
                        # 排除"材料："本身
                        if other_text != '材料' and other_text != '材料：':
                            candidates.append({
                                'text': other_text,
                                'score': other['score'],
                                'confidence': 0.75,
                                'method': 'keyword_nearby'
                            })

        if candidates:
            candidates.sort(key=lambda x: (x['confidence'], x['score']), reverse=True)
            return candidates[0]['text']

        return None

    def extract_company(self, items: List[Dict]) -> Optional[str]:
        """提取公司信息

        策略:
        1. 关键词: "公司", "有限公司", "COMPANY", "CO."
        2. 位置约束: Y: 1050-1090
        """
        for item in items:
            text = item['text'].strip()
            center_x, center_y = self.get_center(item['box'])

            # 包含"公司"且长度合理
            if ('公司' in text or 'COMPANY' in text.upper() or 'CO.' in text.upper()):
                if len(text) >= 5:  # 公司名称通常较长
                    # 位置检查
                    if 1050 <= center_y <= 1090:
                        return text
                    elif center_y > 900:  # 放宽条件
                        return text

        return None

    def extract_personnel(self, items: List[Dict]) -> Dict[str, Optional[str]]:
        """提取人员信息（设计、审核、批准）

        策略:
        1. 查找"设计"、"审核"、"批准"关键词
        2. 提取其右侧或下方的文本
        3. 位置约束: Y: 1080-1150
        """
        personnel = {
            'designer': None,
            'reviewer': None,
            'approver': None
        }

        keywords = {
            'designer': ['设计'],
            'reviewer': ['审核'],
            'approver': ['批准', '批核']
        }

        for role, kws in keywords.items():
            for item in items:
                text = item['text'].strip()
                center_x, center_y = self.get_center(item['box'])

                # 找到关键词
                if any(kw in text for kw in kws):
                    # 位置检查
                    if 1080 <= center_y <= 1150:
                        # 查找右侧或下方的文本
                        candidates = []

                        for other in items:
                            if other is item:
                                continue

                            other_x, other_y = self.get_center(other['box'])
                            other_text = other['text'].strip()

                            # 右侧（X差距20-200）
                            if (center_x + 20 <= other_x <= center_x + 200 and
                                abs(center_y - other_y) < 15):

                                # 排除关键词本身、空文本和无效值
                                # 过滤规则：排除包含特殊字符、关键词的文本
                                invalid_keywords = ['/', 'Kg', 'kg', '版号', '重量', '比例', '修改', '日期', '签名', 'A', 'B', 'C', 'D']
                                is_invalid = any(kw in other_text for kw in invalid_keywords)

                                if (other_text and
                                    other_text not in kws and
                                    not is_invalid and
                                    2 <= len(other_text) <= 10 and  # 人名长度限制
                                    not other_text.isdigit() and     # 排除纯数字
                                    not re.match(r'^\d+[:：]', other_text)):  # 排除比例格式

                                    candidates.append({
                                        'text': other_text,
                                        'distance': other_x - center_x,
                                        'score': other['score']
                                    })

                        # 选择最近的候选
                        if candidates:
                            candidates.sort(key=lambda x: x['distance'])
                            personnel[role] = candidates[0]['text']
                            break

        return personnel

    def extract_tech_requirements(self, items: List[Dict]) -> List[str]:
        """提取技术要求

        策略:
        1. 查找"技术要求"关键词
        2. 提取其下方的编号文本（1., 2., 3.等）
        3. 或提取长文本（长度>=20）
        """
        requirements = []

        # 查找"技术要求"位置
        tech_req_y = None
        for item in items:
            if '技术要求' in item['text']:
                _, tech_req_y = self.get_center(item['box'])
                break

        if not tech_req_y:
            return requirements

        # 收集技术要求下方的文本
        candidates = []
        for item in items:
            text = item['text'].strip()
            center_x, center_y = self.get_center(item['box'])

            # 在技术要求下方（Y范围）
            if tech_req_y < center_y <= tech_req_y + 300:
                # 策略1: 以数字编号开头且长度合理
                if re.match(r'^\d+[\.、]', text) and len(text) >= 10:
                    # 排除纯数字或单词
                    if not text.replace('.', '').replace('、', '').isdigit():
                        candidates.append({
                            'text': text,
                            'y': center_y,
                            'score': item['score']
                        })
                # 策略2: 长文本（可能是技术要求）
                elif len(text) >= 20:
                    # 过滤噪音：排除连续大写字母（公司英文名）、纯数字
                    has_long_caps = re.search(r'[A-Z]{5,}', text)
                    is_number = re.match(r'^\d+\.?\d*$', text)

                    if not has_long_caps and not is_number:
                        candidates.append({
                            'text': text,
                            'y': center_y,
                            'score': item['score']
                        })

        # 按Y坐标排序
        candidates.sort(key=lambda x: x['y'])

        # 提取文本
        for candidate in candidates:
            requirements.append(candidate['text'])

        return requirements

    def extract_scale(self, items: List[Dict]) -> Optional[str]:
        """提取比例信息

        策略:
        1. 模式匹配: 1:XX 格式
        2. "比例"关键词附近
        """
        for item in items:
            text = item['text'].strip()

            # 比例格式
            if re.match(r'^1:\d+$', text):
                return text

        # 查找"比例"附近
        for i, item in enumerate(items):
            if '比例' in item['text']:
                base_x, base_y = self.get_center(item['box'])

                for other in items:
                    other_x, other_y = self.get_center(other['box'])

                    if (base_x + 20 <= other_x <= base_x + 200 and
                        abs(base_y - other_y) < 15):

                        other_text = other['text'].strip()
                        if re.search(r'1:\d+', other_text):
                            return other_text

        return None

    def extract_weight(self, items: List[Dict]) -> Optional[str]:
        """提取重量信息

        策略:
        1. "重量"或"Kg"关键词附近
        2. 数字格式
        """
        for i, item in enumerate(items):
            if '重量' in item['text'] or 'Kg' in item['text'] or 'kg' in item['text']:
                base_x, base_y = self.get_center(item['box'])

                for other in items:
                    other_x, other_y = self.get_center(other['box'])

                    if (base_x + 20 <= other_x <= base_x + 200 and
                        abs(base_y - other_y) < 15):

                        other_text = other['text'].strip()
                        # 数字（可能包含小数点）
                        if re.match(r'^\d+\.?\d*$', other_text):
                            return other_text + ' Kg'

        return None

    def extract_bom_table(self, items: List[Dict]) -> List[Dict]:
        """提取零件BOM表（仅装配图）

        策略:
        1. 查找表头（"序号"、"图号"、"名称"等）
        2. 提取表头下方的表格行
        3. 按X坐标分配到对应列
        """
        bom_data = []

        # 查找表头行
        header_row = None
        header_items = []

        for item in items:
            if '序号' in item['text'] or '图号' in item['text']:
                _, header_row = self.get_center(item['box'])
                break

        if not header_row:
            return bom_data

        # 收集表头行所有项目（确定列位置）
        for item in items:
            _, y = self.get_center(item['box'])
            if abs(y - header_row) < self.tolerance:
                x, _ = self.get_center(item['box'])
                header_items.append({
                    'text': item['text'].strip(),
                    'x': x
                })

        # 按Y坐标分组（识别数据行）
        y_groups = defaultdict(list)
        for item in items:
            center_x, center_y = self.get_center(item['box'])

            # 在表头下方范围
            if header_row + 20 <= center_y <= header_row + 300:
                y_key = round(center_y / self.tolerance) * self.tolerance
                y_groups[y_key].append(item)

        # 提取每行数据
        for y, group in sorted(y_groups.items()):
            if len(group) < 3:  # 至少3个字段才算有效行
                continue

            # 按X坐标排序
            group.sort(key=lambda x: self.get_center(x['box'])[0])

            row_data = {
                'sequence': None,     # 序号
                'drawing_no': None,   # 图号
                'name': None,         # 名称
                'material': None,     # 材料
                'quantity': None,     # 数量
                'remark': None        # 备注
            }

            for item in group:
                text = item['text'].strip()
                x, _ = self.get_center(item['box'])

                # 根据X坐标判断列
                if x < 1100:
                    # 序号列（通常是数字）
                    if text.isdigit():
                        row_data['sequence'] = int(text)
                elif 1100 <= x < 1300:
                    # 图号列
                    if re.search(r'[A-Z]{2,}.*\d', text) and '-' in text:
                        row_data['drawing_no'] = text
                elif 1300 <= x < 1550:
                    # 名称列
                    if len(text) >= 2 and not text.isdigit():
                        row_data['name'] = text
                elif 1550 <= x < 1650:
                    # 数量或材料
                    if re.match(r'Q\d{3}', text):
                        row_data['material'] = text
                    elif text.isdigit():
                        row_data['quantity'] = int(text)
                else:
                    # 备注或材料
                    if re.match(r'Q\d{3}', text):
                        row_data['material'] = text
                    elif len(text) >= 2:
                        row_data['remark'] = text

            # 至少有图号或名称才算有效
            if row_data['drawing_no'] or row_data['name']:
                bom_data.append(row_data)

        return bom_data

    def extract_all(self, jsonl_data: Dict) -> Dict:
        """提取所有信息

        Returns:
            完整的提取结果字典
        """
        items = jsonl_data.get('data', [])

        if not items:
            return {'error': 'No data to extract'}

        # 提取基本信息
        drawing_number = self.extract_drawing_number(items)
        material = self.extract_material(items)
        company = self.extract_company(items)
        scale = self.extract_scale(items)
        weight = self.extract_weight(items)

        # 提取人员信息
        personnel = self.extract_personnel(items)

        # 提取技术要求
        tech_requirements = self.extract_tech_requirements(items)

        # 提取BOM表（可能为空）
        bom_table = self.extract_bom_table(items)

        # 判断图纸类型
        total_blocks = len(items)
        if total_blocks >= 70:
            drawing_type = 'assembly'  # 装配图
        elif total_blocks >= 20:
            drawing_type = 'part'      # 零件图
        else:
            drawing_type = 'simple'    # 简图

        # 组装结果
        result = {
            'basic_info': {
                'drawing_number': drawing_number,
                'drawing_type': drawing_type,
                'material': material,
                'company': company,
                'scale': scale,
                'weight': weight
            },
            'personnel': {
                'designer': personnel.get('designer'),
                'reviewer': personnel.get('reviewer'),
                'approver': personnel.get('approver')
            },
            'technical_requirements': tech_requirements,
            'bom_table': bom_table,
            'metadata': {
                'total_text_blocks': total_blocks,
                'ocr_time': jsonl_data.get('time', 0),
                'page_count': jsonl_data.get('page', 1)
            }
        }

        return result


def load_jsonl(file_path: str) -> Dict:
    """加载JSONL文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """命令行入口"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='工程图纸信息自动提取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 从JSONL文件提取
  %(prog)s input.jsonl

  # 输出到JSON文件
  %(prog)s input.jsonl -o output.json

  # 输出详细信息
  %(prog)s input.jsonl -v

  # 批量处理
  for f in output/layout_analysis/*.jsonl; do
      %(prog)s "$f" -o "${f%.jsonl}.extracted.json"
  done
        '''
    )

    parser.add_argument('input', help='输入JSONL文件路径')
    parser.add_argument('-o', '--output', help='输出JSON文件路径（可选）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-t', '--tolerance', type=int, default=15,
                        help='坐标对齐容差（像素，默认15）')

    args = parser.parse_args()

    # 加载数据
    try:
        jsonl_data = load_jsonl(args.input)
    except Exception as e:
        print(f"❌ 加载文件失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 提取信息
    extractor = DrawingInfoExtractor(tolerance=args.tolerance)
    result = extractor.extract_all(jsonl_data)

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {args.output}")
    else:
        # 打印到stdout
        if args.verbose:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 简洁输出
            print("\n" + "="*60)
            print("📋 工程图纸信息提取结果")
            print("="*60)

            basic = result['basic_info']
            print(f"\n【基本信息】")
            print(f"  图号: {basic['drawing_number'] or '未识别'}")
            print(f"  类型: {basic['drawing_type']}")
            print(f"  材料: {basic['material'] or '未识别'}")
            print(f"  比例: {basic['scale'] or '未识别'}")
            print(f"  重量: {basic['weight'] or '未识别'}")
            print(f"  公司: {basic['company'] or '未识别'}")

            personnel = result['personnel']
            print(f"\n【人员信息】")
            print(f"  设计: {personnel['designer'] or '未识别'}")
            print(f"  审核: {personnel['reviewer'] or '未识别'}")
            print(f"  批准: {personnel['approver'] or '未识别'}")

            tech_reqs = result['technical_requirements']
            print(f"\n【技术要求】({len(tech_reqs)}条)")
            for i, req in enumerate(tech_reqs, 1):
                # 限制长度
                display_text = req if len(req) <= 60 else req[:60] + '...'
                print(f"  {i}. {display_text}")

            bom = result['bom_table']
            if bom:
                print(f"\n【零件BOM表】({len(bom)}项)")
                for item in bom:
                    print(f"  - {item['drawing_no'] or '?'}: {item['name'] or '?'} " +
                          f"({item['material'] or '?'}, 数量:{item['quantity'] or '?'})")

            metadata = result['metadata']
            print(f"\n【元数据】")
            print(f"  文字块数: {metadata['total_text_blocks']}")
            print(f"  识别耗时: {metadata['ocr_time']:.2f}秒")
            print(f"  页数: {metadata['page_count']}")

            print("\n" + "="*60)


if __name__ == '__main__':
    main()
