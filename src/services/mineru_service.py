"""
MinerU PDF 识别服务

使用 MinerU API 批量识别 PDF，提取图号、表格、技术要求等信息

使用方法:
    from src.services.mineru_service import MinerUService

    service = MinerUService(config=config, task_id=task_id, db_session=db)
    result = service.batch_recognize_pdfs(pdf_directory='./output')

Author: CAD Auto Processor Team
Date: 2025-11-05
"""

import os
import re
import time
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from src.models.dwg_drawing_sheet import DWGDrawingSheet
from src.models.dwg_recognition_result import DWGRecognitionResult
from src.models.autocad_config import AutoCADConfig


class MinerUService:
    """MinerU PDF 识别服务"""

    def __init__(self, config: AutoCADConfig, task_id: str, db_session):
        """初始化服务

        Args:
            config: AutoCAD 配置（包含 MinerU 配置）
            task_id: 任务 ID
            db_session: 数据库会话
        """
        self.config = config
        self.task_id = task_id
        self.db = db_session

        # API 配置
        self.api_url = config.mineru_api_url or 'http://127.0.0.1:18080'
        self.output_dir = config.mineru_output_dir or r'F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000_outputs'
        self.timeout_per_file = config.mineru_timeout_per_file or 30
        self.batch_size = config.mineru_batch_size or 10

        # 解析语言列表（JSON 字符串转列表）
        try:
            if isinstance(config.mineru_lang_list, str):
                self.lang_list = json.loads(config.mineru_lang_list)
            else:
                self.lang_list = config.mineru_lang_list or ['ch']
        except:
            self.lang_list = ['ch']

        # 解析方法
        self.parse_method = config.mineru_parse_method or 'auto'
        self.table_enable = config.mineru_table_enable if config.mineru_table_enable is not None else True
        self.return_md = config.mineru_return_md if config.mineru_return_md is not None else True
        self.return_content_list = config.mineru_return_content_list if config.mineru_return_content_list is not None else True

    def batch_recognize_pdfs(self, pdf_directory: str, pdf_pattern: str = '*.pdf') -> Dict[str, Any]:
        """批量识别 PDF 文件

        Args:
            pdf_directory: PDF 目录
            pdf_pattern: 文件匹配模式（默认 *.pdf）

        Returns:
            识别结果统计:
            {
                'success': True/False,
                'total_files': 总文件数,
                'success_count': 成功数,
                'failed_count': 失败数,
                'results': [各文件结果列表]
            }
        """
        # 1. 收集 PDF 文件
        pdf_files = self._collect_pdf_files(pdf_directory, pdf_pattern)
        if not pdf_files:
            return {
                'success': False,
                'message': '未找到 PDF 文件',
                'total_files': 0,
                'success_count': 0,
                'failed_count': 0,
                'results': []
            }

        print(f"  📋 找到 {len(pdf_files)} 个 PDF 文件")

        # 2. 批量处理（分批提交）
        results = []
        total_files = len(pdf_files)

        for i in range(0, total_files, self.batch_size):
            batch = pdf_files[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (total_files + self.batch_size - 1) // self.batch_size

            print(f"  🔄 处理批次 {batch_num}/{total_batches} ({len(batch)} 个文件)")

            batch_result = self._process_batch(batch)
            results.extend(batch_result)

        # 3. 统计结果
        success_count = sum(1 for r in results if r.get('success'))
        failed_count = total_files - success_count

        return {
            'success': success_count > 0,
            'total_files': total_files,
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results
        }

    def _collect_pdf_files(self, directory: str, pattern: str) -> List[str]:
        """收集 PDF 文件列表

        Args:
            directory: 目录路径
            pattern: 文件模式

        Returns:
            PDF 文件路径列表
        """
        pdf_dir = Path(directory)
        if not pdf_dir.exists():
            print(f"  ⚠️  目录不存在: {directory}")
            return []

        pdf_files = [str(f) for f in pdf_dir.glob(pattern)]
        return sorted(pdf_files)  # 排序以保证顺序一致

    def _process_batch(self, pdf_files: List[str]) -> List[Dict]:
        """处理一批 PDF 文件

        Args:
            pdf_files: PDF 文件路径列表

        Returns:
            批次处理结果
        """
        batch_results = []

        # 调用 MinerU API
        start_time = time.time()
        try:
            response = self._call_mineru_api(pdf_files)
            processing_time = time.time() - start_time

            print(f"     ✅ API 调用成功，耗时 {processing_time:.1f} 秒")

            # 解析响应
            for pdf_file in pdf_files:
                result = self._parse_single_result(
                    pdf_file,
                    response,
                    processing_time / len(pdf_files)
                )
                batch_results.append(result)

                if result['success']:
                    print(f"     ✅ {Path(pdf_file).name} 识别成功")
                else:
                    print(f"     ❌ {Path(pdf_file).name} 识别失败: {result.get('error')}")

        except Exception as e:
            print(f"     ❌ 批次处理失败: {e}")
            # 批量失败
            for pdf_file in pdf_files:
                self._save_failed_result(pdf_file, str(e))
                batch_results.append({
                    'pdf_file': pdf_file,
                    'success': False,
                    'error': str(e)
                })

        return batch_results

    def _call_mineru_api(self, pdf_files: List[str]) -> Dict:
        """调用 MinerU API

        Args:
            pdf_files: PDF 文件路径列表

        Returns:
            API 响应 JSON
        """
        url = f"{self.api_url}/file_parse"

        # 构建 multipart/form-data
        files = []
        file_handles = []

        try:
            for pdf_path in pdf_files:
                fp = open(pdf_path, 'rb')
                file_handles.append(fp)
                files.append(('files', (Path(pdf_path).name, fp, 'application/pdf')))

            # 请求参数
            # 注意：MinerU API 要求 form-data 格式，参数格式：
            # - lang_list: 单个语言直接传字符串 'ch'，多个语言用逗号分隔 'ch,en'
            # - 布尔值: 小写字符串 'true'/'false'
            # - output_dir: 使用相对路径（远程服务器兼容性）
            data = {
                'output_dir': './output',  # 使用相对路径，避免 Windows/Linux 路径不兼容
                'lang_list': self.lang_list[0] if len(self.lang_list) == 1 else ','.join(self.lang_list),
                'parse_method': self.parse_method,
                'table_enable': str(self.table_enable).lower(),  # 转为小写字符串 "true"/"false"
                'return_md': str(self.return_md).lower(),
                'return_content_list': str(self.return_content_list).lower(),
                'return_middle_json': 'true',  # 获取结构化识别数据
                'backend': 'vlm-vllm-async-engine',  # 使用 VLM 引擎（需配置本地模型）
                # 远程 API 必需参数
                'start_page_id': '0',
                'end_page_id': '99999',
                'return_model_output': 'false',
                'return_images': 'false',
                'response_format_zip': 'false',
                'server_url': 'string'
            }

            # 计算总超时
            total_timeout = len(pdf_files) * self.timeout_per_file

            print(f"     🌐 调用 MinerU API: {url}")
            print(f"     📁 输出目录: {self.output_dir}")
            print(f"     ⏱️  超时设置: {total_timeout} 秒")

            # 发送请求
            response = requests.post(url, files=files, data=data, timeout=total_timeout)
            response.raise_for_status()

            result = response.json()

            # 检查 API 是否返回错误
            if isinstance(result, dict) and 'error' in result:
                raise Exception(f"MinerU API 返回错误: {result['error']}")

            return result

        finally:
            # 确保关闭所有文件句柄
            for fp in file_handles:
                try:
                    fp.close()
                except:
                    pass

    def _parse_single_result(self, pdf_file: str, api_response: Dict, processing_time: float) -> Dict:
        """解析单个 PDF 的识别结果

        Args:
            pdf_file: PDF 文件路径
            api_response: MinerU API 响应
            processing_time: 处理时间

        Returns:
            解析结果
        """
        pdf_filename = Path(pdf_file).name

        try:
            # 0. 保存原始 API 响应（调试用）
            debug_dir = Path(pdf_file).parent / 'debug_responses'
            debug_dir.mkdir(exist_ok=True)
            debug_file = debug_dir / f"{Path(pdf_file).stem}_response.json"
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(api_response, f, ensure_ascii=False, indent=2)
                print(f"     💾 API 响应已保存: {debug_file}")
            except Exception as e:
                print(f"     ⚠️  保存 API 响应失败: {e}")

            # 1. 检查 API 响应是否包含错误
            if isinstance(api_response, dict) and 'error' in api_response:
                raise Exception(f"API 错误: {api_response['error']}")

            # 2. 从响应中提取对应文件的结果
            # MinerU API v2.6+ 返回格式: {"results": {"filename": {"md_content": "..."}}}
            markdown_content = ''
            content_list = []

            if isinstance(api_response, dict) and 'results' in api_response:
                # 获取文件名（不含扩展名）
                file_key = Path(pdf_file).stem  # tz001.pdf -> tz001

                # 从 results 中提取对应文件的数据
                if file_key in api_response['results']:
                    file_result = api_response['results'][file_key]

                    # 提取 markdown 内容
                    if 'md_content' in file_result:
                        markdown_content = file_result['md_content'] or ''  # 确保不是 None

                    # 提取 content_list（如果有）
                    if 'content_list' in file_result:
                        raw_content = file_result['content_list']
                        # content_list 可能是 JSON 字符串，需要解析
                        if isinstance(raw_content, str):
                            try:
                                content_list = json.loads(raw_content)
                                print(f"     📋 content_list: 已解析 JSON 字符串")
                            except json.JSONDecodeError as e:
                                print(f"     ⚠️  content_list JSON 解析失败: {e}")
                                content_list = []
                        else:
                            content_list = raw_content or []
                else:
                    # 尝试旧格式或其他键名
                    for key, value in api_response['results'].items():
                        if isinstance(value, dict) and 'md_content' in value:
                            markdown_content = value['md_content'] or ''
                            # content_list 可能是 JSON 字符串
                            raw_content = value.get('content_list')
                            if isinstance(raw_content, str):
                                try:
                                    content_list = json.loads(raw_content)
                                except json.JSONDecodeError:
                                    content_list = []
                            else:
                                content_list = raw_content or []
                            break
            else:
                # 兼容旧版本格式
                if isinstance(api_response, dict):
                    if 'markdown' in api_response:
                        markdown_content = api_response['markdown'] or ''
                    elif 'content' in api_response:
                        markdown_content = api_response['content'] or ''
                    elif 'md_content' in api_response:
                        markdown_content = api_response['md_content'] or ''

                    if 'content_list' in api_response:
                        raw_content = api_response['content_list']
                        if isinstance(raw_content, str):
                            try:
                                content_list = json.loads(raw_content)
                            except json.JSONDecodeError:
                                content_list = []
                        else:
                            content_list = raw_content or []

            # 2.1. 提取 middle_json（新增）
            middle_json = None
            if isinstance(api_response, dict) and 'results' in api_response:
                file_key = Path(pdf_file).stem
                if file_key in api_response['results']:
                    file_result = api_response['results'][file_key]
                    if 'middle_json' in file_result:
                        middle_json = file_result['middle_json']
                        # 如果是字符串，解析为字典
                        if isinstance(middle_json, str):
                            try:
                                middle_json = json.loads(middle_json)
                                print(f"     📊 middle_json: 已获取并解析")
                            except json.JSONDecodeError as e:
                                print(f"     ⚠️  middle_json 解析失败: {e}")
                                middle_json = None
                        else:
                            print(f"     📊 middle_json: 已获取")
                    elif 'pdf_info' in file_result:
                        # 兼容直接返回 pdf_info 的格式
                        middle_json = file_result
                        print(f"     📊 middle_json: 已获取（直接格式）")

            # 3. 保存识别结果记录
            recognition_result = DWGRecognitionResult(
                task_id=self.task_id,
                pdf_filename=pdf_filename,
                pdf_path=pdf_file,
                markdown_content=markdown_content,
                content_list=content_list,
                status='completed',
                processing_time_seconds=processing_time,
                file_size_bytes=Path(pdf_file).stat().st_size if Path(pdf_file).exists() else None,
                parse_method=self.parse_method
            )
            self.db.add(recognition_result)

            # 4. 提取图号信息
            drawing_info = self._extract_drawing_info(markdown_content, content_list, middle_json)
            print(f"     📋 图号提取: {drawing_info if drawing_info else '无'}")

            # 5. 提取表格数据
            table_data = self._extract_tables_from_content(content_list)
            print(f"     📊 表格提取: {len(table_data) if table_data else 0} 个")
            if table_data:
                recognition_result.table_data = table_data
                print(f"     ✅ 表格数据已设置")

            # 6. 提取技术要求
            tech_requirements = self._extract_technical_requirements(markdown_content)
            if tech_requirements:
                recognition_result.technical_requirements = tech_requirements
                print(f"     ✅ 技术要求已设置 ({len(tech_requirements)} 字符)")

            # 7. 保存图号记录
            if drawing_info:
                print(f"     💾 创建图号记录...")
                sheet = DWGDrawingSheet(
                    task_id=self.task_id,
                    pdf_filename=pdf_filename,
                    pdf_path=pdf_file,
                    **drawing_info
                )
                self.db.add(sheet)
                print(f"     ✅ 图号记录已添加到会话")
            else:
                print(f"     ⚠️  未提取到图号信息，跳过")

            print(f"     💾 提交事务...")
            self.db.commit()
            print(f"     ✅ 事务提交成功")

            return {
                'pdf_file': pdf_file,
                'success': True,
                'drawing_info': drawing_info,
                'has_tables': len(table_data) > 0 if table_data else False,
                'has_tech_requirements': bool(tech_requirements)
            }

        except Exception as e:
            self.db.rollback()
            error_msg = str(e)
            # 打印完整的堆栈跟踪以便调试
            import traceback
            traceback_str = traceback.format_exc()
            print(f"     ⚠️  解析失败: {error_msg}")
            print(f"     📍 堆栈跟踪:\n{traceback_str}")
            self._save_failed_result(pdf_file, error_msg)
            return {
                'pdf_file': pdf_file,
                'success': False,
                'error': error_msg
            }

    def _extract_drawing_info(self, markdown: str, content_list: List, middle_json: Optional[Dict] = None) -> Optional[Dict]:
        """从识别结果中提取图号信息

        优先级策略：
        1. middle_json 结构化数据（最准确）- 从 preproc_blocks 表格 HTML 提取
        2. content_list 表格数据（次优）- 从返回的表格 HTML 提取
        3. markdown 纯文本（保留）- 正则匹配文本

        Args:
            markdown: Markdown 文本
            content_list: 结构化内容列表
            middle_json: MinerU 返回的 middle_json 结构化数据（可选）

        Returns:
            图号信息字典或 None
        """
        # 调试输出
        print(f"     🔍 _extract_drawing_info 参数检查:")
        print(f"        - markdown 类型: {type(markdown)}, 长度: {len(markdown) if markdown else 0}")
        print(f"        - content_list 类型: {type(content_list)}, 长度: {len(content_list) if content_list else 0}")
        print(f"        - middle_json 类型: {type(middle_json)}")

        info = {}

        # 优先使用 middle_json 结构化数据（新增）
        if middle_json:
            print("     🔍 尝试从 middle_json 提取...")
            try:
                info = self._extract_from_middle_json(middle_json)
                if info:
                    print(f"     ✅ middle_json 提取成功: {info}")
                    return info
                print("     ⚠️  middle_json 提取失败，降级到现有逻辑")
            except Exception as e:
                print(f"     ⚠️  middle_json 提取异常: {e}，降级到现有逻辑")

        # 确保 markdown 和 content_list 不是 None
        markdown = markdown or ''
        content_list = content_list or []

        # 如果没有任何数据，直接返回
        if not markdown and not content_list:
            return None

        # 辅助函数：匹配第一个符合的模式
        def match_first_pattern(text: str, patterns: List[str], key: str):
            if not text:  # 确保 text 不为空
                return False
            for pattern in patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        info[key] = match.group(1).strip()
                        return True
                except Exception:
                    continue
            return False

        # 从 markdown 提取图号（常见模式）
        if markdown:
            match_first_pattern(markdown, [
                r'图\s*号[：:]\s*([A-Z0-9\-\.]+)',
                r'Drawing\s+No[.：:]?\s*([A-Z0-9\-\.]+)',
                r'编\s*号[：:]\s*([A-Z0-9\-\.]+)',
                r'图\s*纸\s*编\s*号[：:]\s*([A-Z0-9\-\.]+)'
            ], 'sheet_number')

        # 如果 markdown 中没找到图号，尝试从表格 HTML 中提取
        if 'sheet_number' not in info and content_list:
            for item in content_list:
                if isinstance(item, dict) and item.get('type') == 'table':
                    table_html = item.get('table_body') or ''  # 确保不是 None
                    if table_html:
                        # 匹配类似 PCX-01-01-03-01-3 的图号模式
                        # 特征：大写字母开头，包含连字符和数字
                        pattern = r'<td[^>]*>([A-Z]{2,}[-\d]+[-\d]+[-\d]+[-\d]+[-\d]+[^<]*)</td>'
                        matches = re.findall(pattern, table_html, re.IGNORECASE)
                        if matches:
                            # 取最长的匹配项作为图号
                            drawing_number = max(matches, key=len).strip()
                            if len(drawing_number) >= 10:  # 图号至少 10 个字符
                                info['sheet_number'] = drawing_number
                                break

        # 版本号提取
        if markdown:
            match_first_pattern(markdown, [
                r'版\s*本[：:]\s*([A-Z0-9.]+)',
                r'Version[：:]?\s*([A-Z0-9.]+)',
                r'Rev[.：:]?\s*([A-Z0-9.]+)',
                r'修\s*订[：:]\s*([A-Z0-9.]+)'
            ], 'version')

        # 比例提取
        if markdown:
            match_first_pattern(markdown, [
                r'比\s*例[：:]\s*([\d:]+)',
                r'Scale[：:]?\s*([\d:]+)'
            ], 'scale')

        # 图纸标题提取（尝试从表格中提取）
        if markdown:
            match_first_pattern(markdown, [
                r'图\s*名[：:]\s*([^\n]+)',
                r'Title[：:]?\s*([^\n]+)',
                r'名\s*称[：:]\s*([^\n]+)'
            ], 'sheet_title')

        # 如果 markdown 中没找到标题，从表格中提取
        if 'sheet_title' not in info and content_list:
            for item in content_list:
                if isinstance(item, dict) and item.get('type') == 'table':
                    table_html = item.get('table_body') or ''  # 确保不是 None
                    if table_html:
                        # 提取中文标题
                        pattern = r'<td[^>]*>([\u4e00-\u9fa5]{4,}[^<]*)</td>'
                        matches = re.findall(pattern, table_html)
                        if matches:
                            # 过滤掉通用词汇
                            excluded = ['技术要求', '材料', '数量', '备注', '名称', '代号', '序号', '设计', '审核', '批准']
                            for title in matches:
                                # 确保 title 不是 None，转换为字符串后再 strip
                                title = str(title).strip() if title is not None else ''
                                if title and not any(ex in title for ex in excluded):
                                    info['sheet_title'] = title
                                    break
                        if 'sheet_title' in info:
                            break

        return info if info else None

    def _extract_tables_from_content(self, content_list: List) -> Optional[List[Dict]]:
        """从 content_list 提取表格数据

        Args:
            content_list: 结构化内容列表

        Returns:
            表格数据列表或 None
        """
        if not content_list:
            return None

        tables = []

        for item in content_list:
            if isinstance(item, dict) and item.get('type') == 'table':
                # MinerU API 返回格式：
                # {
                #   "type": "table",
                #   "table_body": "<table>...</table>",  # HTML 格式
                #   "table_caption": [],
                #   "table_footnote": [],
                #   "img_path": "images/..."
                # }
                table_info = {
                    'table_body': item.get('table_body', ''),
                    'table_caption': item.get('table_caption', []),
                    'table_footnote': item.get('table_footnote', []),
                    'img_path': item.get('img_path', '')
                }
                tables.append(table_info)

        return tables if tables else None

    def _extract_technical_requirements(self, markdown: str) -> Optional[str]:
        """提取技术要求段落

        Args:
            markdown: Markdown 文本

        Returns:
            技术要求文本或 None
        """
        if not markdown:
            return None

        # 匹配技术要求段落
        patterns = [
            r'技\s*术\s*要\s*求[：:]?\s*\n([\s\S]+?)(?=\n\n|\Z)',
            r'Technical\s+Requirements?[：:]?\s*\n([\s\S]+?)(?=\n\n|\Z)',
            r'要\s*求[：:]?\s*\n([\s\S]+?)(?=\n\n|\Z)'
        ]

        for pattern in patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                tech_req = match.group(1).strip()
                # 限制长度
                if len(tech_req) > 5000:
                    tech_req = tech_req[:5000] + '...'
                return tech_req

        return None

    def _extract_from_middle_json(self, middle_json: Dict) -> Optional[Dict]:
        """从 middle_json 结构化数据提取图号和标题

        Args:
            middle_json: MinerU API 返回的 middle_json 结构

        Returns:
            包含 sheet_number 和 sheet_title 的字典，或 None
        """
        if not middle_json:
            return None

        info = {}

        # 获取第一页的 preproc_blocks
        pdf_info_list = middle_json.get('pdf_info', [])
        if not pdf_info_list:
            return None

        preproc_blocks = pdf_info_list[0].get('preproc_blocks', [])

        # 遍历所有表格区域
        for block in preproc_blocks:
            # 确保 block 不是 None 且是字典类型
            if not block or not isinstance(block, dict):
                continue

            if block.get('type') != 'table':
                continue

            # 提取表格 HTML
            html = self._extract_table_html(block)
            if not html:
                continue

            # 提取图号
            if not info.get('sheet_number'):
                drawing_number = self._extract_drawing_number(html)
                if drawing_number:
                    info['sheet_number'] = drawing_number

            # 提取标题
            if not info.get('sheet_title'):
                drawing_title = self._extract_drawing_title(html)
                if drawing_title:
                    info['sheet_title'] = drawing_title

            # 如果都提取到了，提前退出
            if info.get('sheet_number') and info.get('sheet_title'):
                break

        return info if info else None

    def _extract_table_html(self, table_block: Dict) -> Optional[str]:
        """从 table block 提取 HTML 内容

        Args:
            table_block: type='table' 的 block 结构

        Returns:
            表格 HTML 字符串，或 None
        """
        try:
            # 确保 table_block 不是 None
            if not table_block or not isinstance(table_block, dict):
                return None

            blocks = table_block.get('blocks', [])
            for block in blocks:
                # 确保 block 不是 None
                if not block or not isinstance(block, dict):
                    continue

                if block.get('type') == 'table_body':
                    lines = block.get('lines', [])
                    for line in lines:
                        # 确保 line 不是 None
                        if not line or not isinstance(line, dict):
                            continue

                        spans = line.get('spans', [])
                        for span in spans:
                            # 确保 span 不是 None
                            if not span or not isinstance(span, dict):
                                continue

                            if span.get('type') == 'table':
                                return span.get('html', '')
        except Exception as e:
            print(f"     ⚠️  提取表格 HTML 失败: {e}")

        return None

    def _extract_drawing_number(self, html: str) -> Optional[str]:
        """从表格 HTML 提取图号

        通用规则：
        1. 包含多个连字符的长编码
        2. 格式：大写字母开头 + 多组数字（用连字符分隔）
        3. 最小长度 10 字符

        Args:
            html: 表格 HTML

        Returns:
            图号字符串，或 None
        """
        if not html:
            return None

        # 模式1：匹配类似 PCX-01-01-03-01-3 的编码
        # 特征：大写字母开头，至少3个连字符分隔的数字组
        pattern1 = r'<td[^>]*>([A-Z]{2,}(?:-\d+){3,}(?:-[A-Z\d]+)*)</td>'
        matches = re.findall(pattern1, html, re.IGNORECASE)

        if matches:
            # 过滤：长度至少10字符，包含至少3个连字符
            valid_numbers = [m for m in matches if len(m) >= 10 and m.count('-') >= 3]
            if valid_numbers:
                # 返回最长的（通常是完整图号）
                return max(valid_numbers, key=len)

        # 模式2：备用模式，匹配更宽松的编码
        pattern2 = r'<td[^>]*>([A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+-[^<]{5,})</td>'
        matches = re.findall(pattern2, html, re.IGNORECASE)

        if matches:
            valid_numbers = [m.strip() for m in matches if len(m.strip()) >= 10]
            if valid_numbers:
                return valid_numbers[0]

        return None

    def _extract_drawing_title(self, html: str) -> Optional[str]:
        """从表格 HTML 提取图纸标题

        通用规则：
        1. 包含至少4个中文字符
        2. 排除通用词汇
        3. 优先选择字符数多的

        Args:
            html: 表格 HTML

        Returns:
            标题字符串，或 None
        """
        if not html:
            return None

        # 提取所有包含中文的单元格
        pattern = r'<td[^>]*>([\u4e00-\u9fa5]{4,}[^<]*)</td>'
        matches = re.findall(pattern, html)

        if not matches:
            return None

        # 排除通用词汇
        excluded_keywords = [
            '技术要求', '材料', '数量', '备注', '名称', '代号', '序号',
            '设计', '审核', '批准', '标记', '处数', '修改日期', '签名',
            '重量', '版号', '比例', '深圳市', '有限公司', '单重', '总重'
        ]

        # 过滤候选标题
        candidates = []
        for match in matches:
            # 确保 match 不是 None，转换为字符串后再 strip
            text = str(match).strip() if match is not None else ''

            # 跳过空字符串
            if not text:
                continue

            # 跳过包含排除词的
            if any(keyword in text for keyword in excluded_keywords):
                continue

            # 跳过纯数字或太短的
            if len(text) < 4 or text.isdigit():
                continue

            candidates.append(text)

        if not candidates:
            return None

        # 返回最长的（通常是完整标题）
        return max(candidates, key=len)

    def _save_failed_result(self, pdf_file: str, error_message: str):
        """保存失败记录

        Args:
            pdf_file: PDF 文件路径
            error_message: 错误信息
        """
        result = DWGRecognitionResult(
            task_id=self.task_id,
            pdf_filename=Path(pdf_file).name,
            pdf_path=pdf_file,
            status='failed',
            error_message=error_message
        )
        self.db.add(result)
        try:
            self.db.commit()
        except Exception as e:
            print(f"     ⚠️  保存失败记录异常: {e}")
            self.db.rollback()
