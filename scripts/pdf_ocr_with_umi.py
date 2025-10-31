#!/usr/bin/env python3
"""
使用Umi-OCR文档识别API识别PDF文件
支持：提取文本、生成可搜索PDF
"""

import requests
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List


class UmiOCRDocProcessor:
    """Umi-OCR文档处理器"""

    def __init__(self, base_url: str = "http://10.3.19.63:11224"):
        self.base_url = base_url.rstrip('/')
        self.task_id: Optional[str] = None

    def upload_pdf(
        self,
        pdf_path: str,
        page_range_start: int = 1,
        page_range_end: int = -1,
        language: str = "models/config_chinese.txt",
        extraction_mode: str = "fullPage",
        parser: str = "multi_line"
    ) -> Optional[str]:
        """
        上传PDF文件进行识别

        Args:
            pdf_path: PDF文件路径
            page_range_start: 起始页码（1-based）
            page_range_end: 结束页码（-1表示到最后）
            language: OCR语言模型
            extraction_mode: 提取模式
                - "mixed": 混合模式（图片用OCR，文字直接提取）
                - "fullPage": 整页强制OCR（推荐用于矢量PDF）
                - "imageOnly": 仅对图片进行OCR
                - "textOnly": 仅保留原有文本
            parser: 排版解析方案
                - "multi_line": 多栏-总是换行（推荐）
                - "multi_para": 多栏-按自然段换行
                - "multi_none": 多栏-无换行
                - "single_line": 单栏-总是换行
                - "single_para": 单栏-按自然段换行
                - "single_none": 单栏-无换行
                - "single_code": 单栏-保留缩进
                - "none": 不做处理

        Returns:
            任务ID，失败返回None
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ 文件不存在: {pdf_path}")
            return None

        print(f"\n📤 上传PDF文件: {pdf_file.name}")
        print(f"   文件大小: {pdf_file.stat().st_size / (1024*1024):.2f} MB")

        # 准备配置
        config = {
            "ocr.language": language,
            "doc.pageRangeStart": page_range_start,
            "doc.pageRangeEnd": page_range_end,
            "doc.extractionMode": extraction_mode,
            "tbpu.parser": parser,
        }

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

    def wait_for_completion(
        self,
        task_id: Optional[str] = None,
        check_interval: float = 2.0,
        timeout: float = 600.0,
        show_progress: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        等待任务完成

        Args:
            task_id: 任务ID（None则使用self.task_id）
            check_interval: 检查间隔（秒）
            timeout: 超时时间（秒）
            show_progress: 是否显示进度

        Returns:
            识别结果，失败返回None
        """
        task_id = task_id or self.task_id
        if not task_id:
            print("❌ 未指定任务ID")
            return None

        print(f"\n⏳ 等待识别完成...")

        url = f"{self.base_url}/api/doc/result"
        start_time = time.time()
        last_state = None

        while True:
            # 检查超时
            elapsed = time.time() - start_time
            if elapsed > timeout:
                print(f"\n❌ 识别超时 ({timeout}秒)")
                return None

            # 查询状态
            try:
                response = requests.post(
                    url,
                    json={
                        'id': task_id,
                        'is_data': True,  # 获取识别结果
                        'format': 'dict'  # 字典格式
                    },
                    timeout=30
                )
                result = response.json()

                if result.get('code') != 100:
                    print(f"\n❌ 查询失败: {result.get('data', '未知错误')}")
                    return None

                # 直接从result获取状态信息（不是嵌套在data中）
                is_done = result.get('is_done', False)
                state = result.get('state', '')
                processed_count = result.get('processed_count', 0)
                pages_count = result.get('pages_count', 0)

                # 显示进度
                if show_progress:
                    if state == 'running':
                        percentage = (processed_count / pages_count * 100) if pages_count > 0 else 0
                        print(f"   识别中: {processed_count}/{pages_count} 页 ({percentage:.1f}%)")
                    elif state != last_state:
                        if state == 'waiting':
                            print(f"   等待中...")
                    last_state = state

                # 检查完成状态
                if is_done:
                    if state == 'success':
                        print(f"   ✅ 识别完成！耗时: {elapsed:.1f}秒")
                        return result  # 返回完整的result
                    elif state == 'failure':
                        print(f"   ❌ 识别失败")
                        return None

            except Exception as e:
                print(f"\n❌ 查询异常: {e}")
                return None

            # 等待下次检查
            time.sleep(check_interval)

    def extract_text(
        self,
        result_data: Dict[str, Any],
        output_format: str = "text"
    ) -> str:
        """
        从识别结果中提取文本

        Args:
            result_data: wait_for_completion返回的结果
            output_format: 输出格式
                - "text": 纯文本
                - "csv": CSV格式
                - "jsonl": JSON Lines格式

        Returns:
            提取的文本内容
        """
        data = result_data.get('data', [])

        if output_format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['page', 'text', 'score'])  # header

            for i, page in enumerate(data, 1):
                if isinstance(page, dict):
                    text = page.get('data', '')
                    if isinstance(text, list):
                        for block in text:
                            writer.writerow([i, block.get('text', ''), block.get('score', '')])
                    else:
                        writer.writerow([i, text, ''])

            return output.getvalue()

        elif output_format == "jsonl":
            import json
            lines = []
            for i, page in enumerate(data, 1):
                if isinstance(page, dict):
                    lines.append(json.dumps({'page': i, 'data': page.get('data', '')}, ensure_ascii=False))
            return '\n'.join(lines)

        else:  # text
            texts = []
            for page in data:
                if isinstance(page, dict):
                    page_data = page.get('data', '')
                    if isinstance(page_data, list):
                        # 字典格式的data
                        for block in page_data:
                            text = block.get('text', '')
                            if text:
                                texts.append(text)
                    elif isinstance(page_data, str):
                        # 文本格式的data
                        if page_data:
                            texts.append(page_data)

            return '\n'.join(texts)

    def download_result(
        self,
        task_id: Optional[str] = None,
        file_types: List[str] = None,
        ignore_blank: bool = True
    ) -> Optional[str]:
        """
        获取结果下载链接并下载

        Args:
            task_id: 任务ID
            file_types: 文件类型列表
                - "pdfLayered": 双层可搜索PDF（默认）
                - "pdfOneLayer": 单层纯文本PDF
                - "txt": 带页数等信息的txt文件
                - "txtPlain": 只含识别文本的txt文件
                - "jsonl": JSON Lines格式
                - "csv": CSV表格
            ignore_blank: 是否忽略空页

        Returns:
            下载的文件内容（文本）
        """
        task_id = task_id or self.task_id
        if not task_id:
            print("❌ 未指定任务ID")
            return None

        if file_types is None:
            file_types = ["txtPlain"]  # 默认纯文本

        print(f"\n📥 请求下载: {', '.join(file_types)}")

        url = f"{self.base_url}/api/doc/download"
        try:
            response = requests.post(
                url,
                json={
                    'id': task_id,
                    'file_types': file_types,
                    'ignore_blank': ignore_blank
                },
                timeout=60
            )
            result = response.json()

            if result.get('code') != 100:
                print(f"   ❌ 请求失败: {result.get('data', '未知错误')}")
                return None

            download_url = result.get('data')
            print(f"   ✅ 获取下载链接: {download_url}")

            # 下载文件（处理URL编码问题）
            from urllib.parse import urlparse, urlunparse, quote as url_quote

            if download_url.startswith('http'):
                # 完整URL：需要编码path部分
                parsed = urlparse(download_url)
                encoded_path = url_quote(parsed.path.encode('utf-8'), safe='/')
                download_full_url = urlunparse((parsed.scheme, parsed.netloc, encoded_path, '', '', ''))
            else:
                # 相对URL
                download_full_url = f"{self.base_url}{download_url}"

            response = requests.get(download_full_url, timeout=120)

            if response.status_code == 200:
                content = response.text if 'text' in file_types[0] or 'csv' in file_types[0] or 'jsonl' in file_types[0] else response.content
                print(f"   ✅ 下载完成: {len(content)} {'字符' if isinstance(content, str) else '字节'}")
                return content
            else:
                print(f"   ❌ 下载失败: HTTP {response.status_code}")
                return None

        except Exception as e:
            print(f"   ❌ 下载异常: {e}")
            return None

    def clear_task(self, task_id: Optional[str] = None) -> bool:
        """
        清理任务临时文件

        Args:
            task_id: 任务ID

        Returns:
            成功返回True
        """
        task_id = task_id or self.task_id
        if not task_id:
            return False

        url = f"{self.base_url}/api/doc/clear"
        try:
            response = requests.post(url, json={'id': task_id}, timeout=30)
            result = response.json()

            if result.get('code') == 100:
                print(f"   ✅ 清理任务: {task_id}")
                return True
            else:
                print(f"   ⚠️  清理失败: {result.get('data', '未知错误')}")
                return False

        except Exception as e:
            print(f"   ⚠️  清理异常: {e}")
            return False

    def process_pdf(
        self,
        pdf_path: str,
        output_mode: str = "text",
        output_path: Optional[str] = None,
        output_format: str = "text",
        extraction_mode: str = "fullPage",
        parser: str = "multi_line",
        clean_after: bool = True
    ) -> Optional[str]:
        """
        完整处理PDF流程（上传→识别→提取/生成→清理）

        Args:
            pdf_path: PDF文件路径
            output_mode: 输出模式
                - "text": 提取文本
                - "searchable_pdf": 生成可搜索PDF
                - "both": 两者都生成
            output_path: 输出路径（文本或PDF文件）
            output_format: 文本格式
                - "text": 纯文本
                - "csv": CSV格式
                - "jsonl": JSON Lines格式
            extraction_mode: 提取模式
                - "fullPage": 整页强制OCR（推荐用于矢量PDF）
                - "mixed": 混合模式
                - "imageOnly": 仅图片OCR
                - "textOnly": 仅文本
            parser: 排版解析
                - "multi_line": 多栏-总是换行（推荐）
                - 其他见upload_pdf说明
            clean_after: 完成后是否清理任务

        Returns:
            - text模式: 返回文本内容
            - searchable_pdf模式: 返回PDF文件路径
            - both模式: 返回元组(text, pdf_path)
        """
        # 1. 上传
        task_id = self.upload_pdf(
            pdf_path,
            extraction_mode=extraction_mode,
            parser=parser
        )
        if not task_id:
            return None

        # 2. 等待完成
        result = self.wait_for_completion(task_id)
        if not result:
            return None

        # 3. 下载结果
        output = None
        if output_mode == "text":
            # 根据output_format选择文件类型
            file_type_map = {
                "text": "txtPlain",
                "csv": "csv",
                "jsonl": "jsonl"
            }
            file_type = file_type_map.get(output_format, "txtPlain")

            content = self.download_result(task_id, file_types=[file_type])

            if content:
                print(f"\n📝 提取文本: {len(content)} 字符")
                output = content

                # 保存到文件
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   保存到: {output_path}")

        elif output_mode == "searchable_pdf":
            content = self.download_result(task_id, file_types=["pdfLayered"])

            if content and output_path:
                with open(output_path, 'wb') as f:
                    f.write(content)
                print(f"   ✅ 可搜索PDF已保存: {output_path}")
                output = output_path

        elif output_mode == "both":
            # 同时下载文本和PDF
            file_type_map = {
                "text": "txtPlain",
                "csv": "csv",
                "jsonl": "jsonl"
            }
            file_type = file_type_map.get(output_format, "txtPlain")

            text_content = self.download_result(task_id, file_types=[file_type])
            pdf_content = self.download_result(task_id, file_types=["pdfLayered"])

            if text_content:
                print(f"\n📝 提取文本: {len(text_content)} 字符")

            pdf_path = None
            if pdf_content and output_path:
                pdf_path = output_path if output_path.endswith('.pdf') else f"{output_path}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_content)
                print(f"   ✅ 可搜索PDF已保存: {pdf_path}")

            output = (text_content, pdf_path)

        # 4. 清理
        if clean_after:
            self.clear_task(task_id)

        return output


# ==================== 使用示例 ====================

def example_1_extract_text():
    """示例1: 提取PDF文本（全页OCR模式）"""
    processor = UmiOCRDocProcessor()

    pdf_path = "/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf"

    text = processor.process_pdf(
        pdf_path,
        output_mode="text",
        extraction_mode="fullPage",  # 全页OCR（推荐用于矢量PDF）
        parser="multi_line"          # 多栏-总是换行
    )

    if text:
        print("\n" + "="*60)
        print("提取的文本内容（前500字符）:")
        print("="*60)
        print(text[:500])

        # 保存到文件
        output_txt = "/tmp/extracted_text.txt"
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n完整文本已保存到: {output_txt}")


def example_2_extract_csv():
    """示例2: 提取为CSV格式"""
    processor = UmiOCRDocProcessor()

    pdf_path = "/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf"
    output_csv = "/tmp/extracted_data.csv"

    text = processor.process_pdf(
        pdf_path,
        output_mode="text",
        output_path=output_csv,
        output_format="csv",         # CSV格式
        extraction_mode="fullPage",
        parser="multi_line"
    )

    if text:
        print(f"\n✅ CSV文件已生成: {output_csv}")
        print("\n预览（前10行）:")
        print('\n'.join(text.split('\n')[:10]))


def example_3_extract_jsonl():
    """示例3: 提取为JSONL格式"""
    processor = UmiOCRDocProcessor()

    pdf_path = "/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf"
    output_jsonl = "/tmp/extracted_data.jsonl"

    text = processor.process_pdf(
        pdf_path,
        output_mode="text",
        output_path=output_jsonl,
        output_format="jsonl",        # JSONL格式
        extraction_mode="fullPage",
        parser="multi_line"
    )

    if text:
        print(f"\n✅ JSONL文件已生成: {output_jsonl}")
        print("\n预览（前3行）:")
        print('\n'.join(text.split('\n')[:3]))


def example_2_generate_searchable_pdf():
    """示例2: 生成可搜索PDF"""
    processor = UmiOCRDocProcessor()

    pdf_path = "/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf"
    output_path = "/tmp/searchable_output.pdf"

    result = processor.process_pdf(
        pdf_path,
        output_mode="searchable_pdf",
        output_path=output_path
    )

    if result:
        print(f"\n✅ 可搜索PDF生成成功: {result}")
        print("\n验证命令:")
        print(f"  pdftotext '{result}' - | head -20")


def example_3_batch_process():
    """示例3: 批量处理多个PDF"""
    processor = UmiOCRDocProcessor()

    pdf_dir = Path("/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf")
    output_dir = Path("/tmp/ocr_results")
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # 处理前3个

    print(f"\n批量处理 {len(pdf_files)} 个PDF文件")
    print("="*60)

    results = []
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")

        text = processor.process_pdf(str(pdf_file), output_mode="text")

        if text:
            # 保存文本
            txt_file = output_dir / f"{pdf_file.stem}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(text)

            results.append({
                'pdf': pdf_file.name,
                'text_length': len(text),
                'output': str(txt_file)
            })

    print("\n" + "="*60)
    print(f"批量处理完成！成功: {len(results)}/{len(pdf_files)}")
    for r in results:
        print(f"  ✅ {r['pdf']}: {r['text_length']} 字符 → {r['output']}")


def example_4_compare_modes():
    """示例4: 对比不同提取模式"""
    processor = UmiOCRDocProcessor()

    pdf_path = "/Users/saul/IdeaProjects/100.AI.TrainData/data/pdf/PCX20.01%20主体钢结构（20230301）0001.pdf"

    modes = [
        ("mixed", "混合模式（推荐）"),
        ("ocr", "全部OCR"),
        ("txt", "仅提取文字")
    ]

    print("\n对比不同提取模式:")
    print("="*60)

    for mode, desc in modes:
        print(f"\n【{desc}】")

        # 手动流程以控制extraction_mode
        task_id = processor.upload_pdf(pdf_path, extraction_mode=mode)
        if task_id:
            result = processor.wait_for_completion(task_id, show_progress=False)
            if result:
                text = processor.extract_text(result)
                print(f"  提取文本: {len(text)} 字符")
                if text:
                    print(f"  预览: {text[:100]}")
                processor.clear_task(task_id)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # 命令行模式
        pdf_path = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "text"
        output_format = sys.argv[3] if len(sys.argv) > 3 else "text"

        processor = UmiOCRDocProcessor()
        result = processor.process_pdf(
            pdf_path,
            output_mode=mode,
            output_format=output_format,
            extraction_mode="fullPage",  # 全页OCR
            parser="multi_line"          # 多栏-总是换行
        )

        if mode == "text" and result:
            print(result)
    else:
        # 运行示例
        print("选择示例:")
        print("  1. 提取PDF文本（text）")
        print("  2. 提取为CSV格式")
        print("  3. 提取为JSONL格式")
        print("  4. 生成可搜索PDF")
        print("  5. 批量处理")

        choice = input("\n请选择 (1-5): ").strip()

        if choice == "1":
            example_1_extract_text()
        elif choice == "2":
            example_2_extract_csv()
        elif choice == "3":
            example_3_extract_jsonl()
        elif choice == "4":
            example_2_generate_searchable_pdf()
        elif choice == "5":
            example_3_batch_process()
        else:
            print("\n示例用法:")
            print("  # 提取为文本")
            print("  python pdf_ocr_with_umi.py file.pdf text text")
            print("")
            print("  # 提取为CSV")
            print("  python pdf_ocr_with_umi.py file.pdf text csv")
            print("")
            print("  # 提取为JSONL")
            print("  python pdf_ocr_with_umi.py file.pdf text jsonl")
            print("")
            print("  # 生成可搜索PDF")
            print("  python pdf_ocr_with_umi.py file.pdf searchable_pdf")
