"""
PDF 文件重组织服务

在 PDF 识别完成后，根据提取的图号重命名文件并整理到新目录

使用方法:
    from src.services.pdf_reorganize_service import PDFReorganizeService

    service = PDFReorganizeService(db_session)
    result = service.reorganize_pdfs(drawing_sheets, source_directory)

Author: CAD Auto Processor Team
Date: 2025-11-06
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

from src.models.dwg_drawing_sheet import DWGDrawingSheet
from src.utils.logger import get_logger


class PDFReorganizeService:
    """PDF 文件重组织服务

    职责：
    1. 创建转换目录（xxx_convert）
    2. 根据图号重命名 PDF 文件
    3. 更新数据库记录
    4. 处理文件名冲突和错误
    """

    def __init__(self, db_session):
        """初始化服务

        Args:
            db_session: 数据库会话
        """
        self.db = db_session
        self.logger = get_logger()

    def reorganize_pdfs(
        self,
        drawing_sheets: List[DWGDrawingSheet],
        source_directory: str
    ) -> Dict[str, Any]:
        """批量重组织 PDF 文件

        Args:
            drawing_sheets: 图纸记录列表
            source_directory: PDF 源目录路径

        Returns:
            统计结果字典:
            {
                'success': True/False,
                'total_files': 总文件数,
                'completed': 成功数,
                'skipped': 跳过数,
                'failed': 失败数,
                'convert_directory': 转换目录路径,
                'details': [各文件处理结果列表]
            }
        """
        self.logger.info(f"开始 PDF 文件重组织: {len(drawing_sheets)} 个文件")

        # 统计信息
        stats = {
            'success': False,
            'total_files': len(drawing_sheets),
            'completed': 0,
            'skipped': 0,
            'failed': 0,
            'convert_directory': None,
            'details': []
        }

        if not drawing_sheets:
            self.logger.warning("无图纸记录，跳过重组织")
            stats['success'] = True
            return stats

        try:
            # 1. 创建转换目录
            convert_dir = self._create_convert_directory(source_directory)
            stats['convert_directory'] = str(convert_dir)
            self.logger.info(f"转换目录已创建: {convert_dir}")

            # 2. 跟踪已使用的文件名（处理冲突）
            existing_files: Set[str] = set()

            # 3. 遍历处理每个图纸
            for sheet in drawing_sheets:
                result = self._process_single_sheet(
                    sheet,
                    source_directory,
                    convert_dir,
                    existing_files
                )

                # 更新统计
                if result['status'] == DWGDrawingSheet.CONVERSION_STATUS_COMPLETED:
                    stats['completed'] += 1
                elif result['status'] == DWGDrawingSheet.CONVERSION_STATUS_SKIPPED:
                    stats['skipped'] += 1
                elif result['status'] == DWGDrawingSheet.CONVERSION_STATUS_FAILED:
                    stats['failed'] += 1

                stats['details'].append(result)

            # 4. 提交数据库更改
            self.db.commit()
            stats['success'] = True

            self.logger.info(
                f"重组织完成 - 成功: {stats['completed']}, "
                f"跳过: {stats['skipped']}, 失败: {stats['failed']}"
            )

        except Exception as e:
            self.logger.error(f"重组织失败: {e}", exc_info=True)
            self.db.rollback()
            stats['success'] = False
            stats['error'] = str(e)

        return stats

    def _process_single_sheet(
        self,
        sheet: DWGDrawingSheet,
        source_dir: str,
        convert_dir: Path,
        existing_files: Set[str]
    ) -> Dict:
        """处理单个图纸的 PDF 文件

        Args:
            sheet: 图纸记录
            source_dir: 源目录
            convert_dir: 转换目录
            existing_files: 已存在的文件名集合

        Returns:
            处理结果字典
        """
        pdf_name = sheet.pdf_filename or Path(sheet.pdf_path).name if sheet.pdf_path else None

        try:
            # 1. 检查图号是否存在
            if not sheet.sheet_number:
                self.logger.debug(f"跳过无图号文件: {pdf_name}")
                self._update_database_record(
                    sheet,
                    None,
                    None,
                    DWGDrawingSheet.CONVERSION_STATUS_SKIPPED,
                    "图号为空"
                )
                return {
                    'pdf_filename': pdf_name,
                    'status': DWGDrawingSheet.CONVERSION_STATUS_SKIPPED,
                    'reason': '图号为空'
                }

            # 2. 检查源文件是否存在
            source_path = Path(sheet.pdf_path) if sheet.pdf_path else Path(source_dir) / pdf_name
            if not source_path.exists():
                error_msg = f"源文件不存在: {source_path}"
                self.logger.warning(error_msg)
                self._update_database_record(
                    sheet,
                    None,
                    None,
                    DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                    error_msg
                )
                return {
                    'pdf_filename': pdf_name,
                    'status': DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                    'error': error_msg
                }

            # 3. 生成唯一文件名
            new_filename = self._generate_unique_filename(
                sheet.sheet_number,
                existing_files
            )
            existing_files.add(new_filename)

            # 4. 复制并重命名文件
            dest_path = convert_dir / new_filename
            success = self._copy_and_rename_pdf(source_path, dest_path)

            if not success:
                error_msg = "文件复制失败"
                self._update_database_record(
                    sheet,
                    None,
                    None,
                    DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                    error_msg
                )
                return {
                    'pdf_filename': pdf_name,
                    'status': DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                    'error': error_msg
                }

            # 5. 更新数据库记录
            self._update_database_record(
                sheet,
                str(convert_dir),
                new_filename,
                DWGDrawingSheet.CONVERSION_STATUS_COMPLETED,
                None
            )

            self.logger.debug(f"已转换: {pdf_name} -> {new_filename}")

            return {
                'pdf_filename': pdf_name,
                'new_filename': new_filename,
                'status': DWGDrawingSheet.CONVERSION_STATUS_COMPLETED
            }

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self.logger.error(f"{pdf_name}: {error_msg}", exc_info=True)
            self._update_database_record(
                sheet,
                None,
                None,
                DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                error_msg
            )
            return {
                'pdf_filename': pdf_name,
                'status': DWGDrawingSheet.CONVERSION_STATUS_FAILED,
                'error': error_msg
            }

    def _create_convert_directory(self, source_dir: str) -> Path:
        """创建转换目录

        Args:
            source_dir: 源目录路径

        Returns:
            转换目录 Path 对象

        Example:
            源目录: /data/pdf/
            转换目录: /data/pdf_convert/
        """
        source_path = Path(source_dir).resolve()
        convert_path = source_path.parent / f"{source_path.name}_convert"

        # 创建目录（如果已存在则跳过）
        convert_path.mkdir(exist_ok=True, parents=True)

        # 继承源目录权限（Unix 系统）
        if hasattr(os, 'chmod') and source_path.exists():
            try:
                source_stat = source_path.stat()
                os.chmod(convert_path, source_stat.st_mode)
            except Exception as e:
                self.logger.warning(f"无法继承权限: {e}")

        return convert_path

    def _generate_unique_filename(
        self,
        sheet_number: str,
        existing_files: Set[str]
    ) -> str:
        """生成唯一文件名（处理冲突）

        Args:
            sheet_number: 图号
            existing_files: 已存在的文件名集合

        Returns:
            唯一文件名

        Example:
            输入: "PCX-01-01", existing_files={"PCX-01-01.pdf"}
            输出: "PCX-01-01_1.pdf"
        """
        # 清理图号中的非法字符（Windows 文件名限制）
        sheet_number = sheet_number.replace('/', '-').replace('\\', '-').replace(':', '-')

        base_name = f"{sheet_number}.pdf"

        # 无冲突，直接返回
        if base_name not in existing_files:
            return base_name

        # 有冲突，追加序号
        counter = 1
        while True:
            new_name = f"{sheet_number}_{counter}.pdf"
            if new_name not in existing_files:
                self.logger.info(f"文件名冲突，追加序号: {new_name}")
                return new_name
            counter += 1

    def _copy_and_rename_pdf(
        self,
        source_path: Path,
        dest_path: Path
    ) -> bool:
        """复制并重命名 PDF 文件

        Args:
            source_path: 源文件路径
            dest_path: 目标文件路径

        Returns:
            是否成功
        """
        try:
            # 使用 shutil.copy2() 保留元数据和权限
            shutil.copy2(source_path, dest_path)
            return True

        except PermissionError as e:
            self.logger.error(f"权限错误: {source_path} -> {dest_path}: {e}")
            return False

        except FileNotFoundError as e:
            self.logger.error(f"文件未找到: {source_path}: {e}")
            return False

        except Exception as e:
            self.logger.error(f"复制失败: {source_path} -> {dest_path}: {e}")
            return False

    def _update_database_record(
        self,
        sheet: DWGDrawingSheet,
        converted_dir: str,
        converted_filename: str,
        status: str,
        error: str = None
    ):
        """更新数据库记录

        Args:
            sheet: 图纸记录
            converted_dir: 转换后目录路径
            converted_filename: 转换后文件名
            status: 转换状态
            error: 错误信息（可选）
        """
        sheet.converted_directory = converted_dir
        sheet.converted_filename = converted_filename
        sheet.conversion_status = status
        sheet.conversion_error = error

        if status == DWGDrawingSheet.CONVERSION_STATUS_COMPLETED:
            sheet.converted_at = datetime.now()

        # 注意：不在这里 commit，由调用方统一提交
