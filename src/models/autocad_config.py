"""
AutoCAD 自动化配置模型

存储 AutoCAD 工作流程的配置参数

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from src.utils.database import Base


class AutoCADConfig(Base):
    """AutoCAD 自动化配置表"""

    __tablename__ = 'autocad_config'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    config_name = Column(String(100), unique=True, nullable=False, comment='配置名称')
    description = Column(String(500), comment='配置描述')

    # CAD 程序配置
    autocad_exe_path = Column(String(500), comment='AutoCAD 可执行文件路径')
    autocad_version = Column(String(50), comment='AutoCAD 版本（如 2014, 2021）')

    # 文件配置
    dwg_file_path = Column(String(1000), comment='DWG 文件路径')
    working_directory = Column(String(1000), comment='工作目录（文件处理时的工作路径）')
    copy_to_working_dir = Column(Boolean, default=False, comment='是否复制文件到工作目录')
    force_close_existing = Column(Boolean, default=True, comment='是否强制关闭现有 CAD 进程')
    close_cad_after_completion = Column(Boolean, default=True, comment='任务完成后是否关闭 CAD 进程')

    # 延迟配置（秒）
    startup_wait_time = Column(Float, default=10.0, comment='启动等待时间（秒）')
    startup_check_interval = Column(Float, default=1.0, comment='启动检查间隔（秒）')
    post_startup_wait = Column(Float, default=2.0, comment='启动后额外等待时间（秒）')
    file_open_retry_delay = Column(Float, default=3.0, comment='文件打开重试延迟（秒）')
    file_open_max_retries = Column(Integer, default=3, comment='文件打开最大重试次数')
    verification_wait_time = Column(Float, default=30.0, comment='文件验证最大等待时间（秒）')
    verification_check_interval = Column(Float, default=2.0, comment='文件验证检查间隔（秒）')

    # 菜单操作配置
    menu_operations = Column(Text, comment='菜单操作配置（JSON格式）')
    # 格式示例：
    # [
    #   {"type": "command", "command": "ZOOM", "wait_time": 1.0},
    #   {"type": "menu", "path": ["工具", "选项"], "wait_time": 1.5}
    # ]

    # OCR 图像预处理配置（新增）
    ocr_preprocessing_methods = Column(Text, comment='OCR预处理方法列表（JSON格式）')
    # 格式示例：["binary_adaptive", "high_contrast", "denoise_bilateral"]
    # null 或 空数组 = 使用推荐方法

    ocr_preprocessing_params = Column(Text, comment='OCR预处理参数配置（JSON格式）')
    # 格式示例：
    # {
    #   "binary_adaptive_block_size": 11,
    #   "clahe_clip_limit": 3.0,
    #   "canny_threshold1": 50
    # }

    # OCR 文件管理配置（新增）
    ocr_screenshot_base_dir = Column(String(500), comment='OCR截图基础目录')
    ocr_screenshot_timestamp_format = Column(String(50), default='%Y%m%d_%H%M%S', comment='时间戳格式')
    ocr_file_cleanup_enabled = Column(Boolean, default=False, comment='是否启用文件清理')
    ocr_file_cleanup_strategy = Column(String(20), default='archive', comment='清理策略: delete/archive/none')
    ocr_file_archive_dir = Column(String(500), comment='归档目录')
    ocr_file_retention_days = Column(Integer, default=7, comment='文件保留天数')
    ocr_enable_detailed_logging = Column(Boolean, default=True, comment='是否启用详细日志记录')

    # Umi-OCR 服务配置（新增）
    umi_ocr_service_url = Column(String(200), default='http://127.0.0.1:11224', comment='Umi-OCR服务地址')
    umi_ocr_api_path = Column(String(100), default='/api/ocr', comment='Umi-OCR API路径')
    umi_ocr_timeout = Column(Integer, default=30, comment='Umi-OCR请求超时时间(秒)')
    umi_ocr_enabled = Column(Boolean, default=True, comment='是否启用Umi-OCR')
    umi_ocr_limit_side_len = Column(Integer, default=2880, comment='Umi-OCR图像边长限制(像素): 960=标准, 2880=高精度, 4320=超高精度')
    umi_ocr_max_workers = Column(Integer, default=8, comment='Umi-OCR并行线程数(1-16): 建议值=CPU核心数或8')

    # 输出目录清理配置（新增）
    output_dir_cleanup_enabled = Column(Boolean, default=False, comment='是否在运行前清理输出目录')
    output_dir_path = Column(String(1000), default=r'F:\cad\caddd\cadpython\CAD_AutoProcessor\outputs', comment='输出目录路径')
    output_dir_backup_before_cleanup = Column(Boolean, default=False, comment='清理前是否备份')
    output_dir_backup_path = Column(String(1000), comment='备份目录路径')

    # PDF 提取配置（新增）
    pdf_extraction_enabled = Column(Boolean, default=False, comment='是否启用PDF信息提取（在输出PDF后自动提取图纸信息）')
    pdf_extraction_output_dir = Column(String(1000), comment='PDF提取结果输出目录（为空则使用输出目录下的pdf_extraction子目录）')
    pdf_extraction_jsonl_subdir = Column(String(100), default='jsonl', comment='JSONL文件子目录名（相对于提取结果目录）')
    pdf_extraction_info_subdir = Column(String(100), default='extracted_info', comment='提取信息JSON文件子目录名（相对于提取结果目录）')
    pdf_extraction_umi_service_url = Column(String(200), default='http://10.3.19.63:11224', comment='PDF提取使用的Umi-OCR文档API地址')
    pdf_extraction_mode = Column(String(20), default='fullPage', comment='PDF提取模式：fullPage(全页)/mixed(混合)，推荐fullPage')
    pdf_extraction_parser = Column(String(20), default='multi_line', comment='文本解析器：multi_line(多列)/single_line(单列)，推荐multi_line')
    pdf_extraction_generate_csv = Column(Boolean, default=True, comment='是否生成CSV汇总报告')
    pdf_extraction_csv_filename = Column(String(100), default='extraction_summary.csv', comment='CSV汇总报告文件名')
    pdf_extraction_fail_on_error = Column(Boolean, default=False, comment='PDF提取失败是否中断整个流程（False=记录错误但继续）')
    pdf_extraction_max_retries = Column(Integer, default=2, comment='单个PDF提取失败时的最大重试次数')
    pdf_extraction_enable_logging = Column(Boolean, default=True, comment='是否启用数据库日志记录（记录到dwg_task步骤日志）')
    pdf_extraction_parallel_workers = Column(Integer, default=1, comment='并行处理PDF的线程数（1=单线程，2-8=多线程，推荐CPU核心数）')

    # MinerU PDF 识别配置（新增 2025-11-05）
    mineru_api_url = Column(String(200), default='http://127.0.0.1:18080', comment='MinerU API 服务地址')
    mineru_enabled = Column(Boolean, default=False, comment='是否启用 MinerU 识别')
    mineru_output_dir = Column(String(1000), default=r'F:\cad\caddd\cadpython\CAD_AutoProcessor\downloads\000_outputs', comment='MinerU PDF 识别输出目录（服务端绝对路径）')
    mineru_timeout_per_file = Column(Integer, default=30, comment='单个 PDF 处理超时（秒）')
    mineru_pdf_render_timeout = Column(Integer, default=300, comment='PDF 渲染超时（秒）')
    mineru_batch_size = Column(Integer, default=10, comment='批量处理数量（一次提交多少个 PDF）')
    mineru_lang_list = Column(String(100), default='["ch"]', comment='识别语言列表（JSON数组）')
    mineru_parse_method = Column(String(20), default='auto', comment='解析方法: auto/ocr/txt')
    mineru_table_enable = Column(Boolean, default=True, comment='是否启用表格识别')
    mineru_return_md = Column(Boolean, default=True, comment='是否返回 Markdown')
    mineru_return_content_list = Column(Boolean, default=True, comment='是否返回结构化内容列表')
    mineru_extraction_patterns = Column(Text, comment='图号提取正则表达式（JSON格式）')

    # 状态字段
    is_active = Column(Boolean, default=True, comment='是否激活')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    def __repr__(self):
        return f"<AutoCADConfig(id={self.id}, name='{self.config_name}')>"

    def to_dict(self):
        """转换为字典"""
        import json

        menu_ops = None
        if self.menu_operations:
            try:
                menu_ops = json.loads(self.menu_operations)
            except:
                menu_ops = []

        # 解析OCR预处理配置
        ocr_methods = None
        if self.ocr_preprocessing_methods:
            try:
                ocr_methods = json.loads(self.ocr_preprocessing_methods)
            except:
                ocr_methods = None

        ocr_params = None
        if self.ocr_preprocessing_params:
            try:
                ocr_params = json.loads(self.ocr_preprocessing_params)
            except:
                ocr_params = {}

        return {
            'id': self.id,
            'config_name': self.config_name,
            'description': self.description,
            'autocad_exe_path': self.autocad_exe_path,
            'autocad_version': self.autocad_version,
            'dwg_file_path': self.dwg_file_path,
            'working_directory': self.working_directory,
            'copy_to_working_dir': self.copy_to_working_dir,
            'force_close_existing': self.force_close_existing,
            'close_cad_after_completion': self.close_cad_after_completion,
            'timing': {
                'startup_wait_time': self.startup_wait_time,
                'startup_check_interval': self.startup_check_interval,
                'post_startup_wait': self.post_startup_wait,
                'file_open_retry_delay': self.file_open_retry_delay,
                'file_open_max_retries': self.file_open_max_retries,
                'verification_wait_time': self.verification_wait_time,
                'verification_check_interval': self.verification_check_interval,
            },
            'menu_operations': menu_ops,
            'ocr_preprocessing': {
                'methods': ocr_methods,
                'params': ocr_params,
            },
            'ocr_file_management': {
                'screenshot_base_dir': self.ocr_screenshot_base_dir,
                'screenshot_timestamp_format': self.ocr_screenshot_timestamp_format,
                'cleanup_enabled': self.ocr_file_cleanup_enabled,
                'cleanup_strategy': self.ocr_file_cleanup_strategy,
                'archive_dir': self.ocr_file_archive_dir,
                'retention_days': self.ocr_file_retention_days,
                'enable_detailed_logging': self.ocr_enable_detailed_logging,
            },
            'umi_ocr': {
                'service_url': self.umi_ocr_service_url,
                'api_path': self.umi_ocr_api_path,
                'timeout': self.umi_ocr_timeout,
                'enabled': self.umi_ocr_enabled,
                'limit_side_len': self.umi_ocr_limit_side_len,
                'max_workers': self.umi_ocr_max_workers,
            },
            'output_dir_cleanup': {
                'enabled': self.output_dir_cleanup_enabled,
                'path': self.output_dir_path,
                'backup_before_cleanup': self.output_dir_backup_before_cleanup,
                'backup_path': self.output_dir_backup_path,
            },
            'pdf_extraction': {
                'enabled': self.pdf_extraction_enabled,
                'output_dir': self.pdf_extraction_output_dir,
                'jsonl_subdir': self.pdf_extraction_jsonl_subdir,
                'info_subdir': self.pdf_extraction_info_subdir,
                'umi_service_url': self.pdf_extraction_umi_service_url,
                'mode': self.pdf_extraction_mode,
                'parser': self.pdf_extraction_parser,
                'generate_csv': self.pdf_extraction_generate_csv,
                'csv_filename': self.pdf_extraction_csv_filename,
                'fail_on_error': self.pdf_extraction_fail_on_error,
                'max_retries': self.pdf_extraction_max_retries,
                'enable_logging': self.pdf_extraction_enable_logging,
                'parallel_workers': self.pdf_extraction_parallel_workers,
            },
            'mineru': {
                'api_url': self.mineru_api_url,
                'enabled': self.mineru_enabled,
                'output_dir': self.mineru_output_dir,
                'timeout_per_file': self.mineru_timeout_per_file,
                'pdf_render_timeout': self.mineru_pdf_render_timeout,
                'batch_size': self.mineru_batch_size,
                'lang_list': self.mineru_lang_list,
                'parse_method': self.mineru_parse_method,
                'table_enable': self.mineru_table_enable,
                'return_md': self.mineru_return_md,
                'return_content_list': self.mineru_return_content_list,
                'extraction_patterns': self.mineru_extraction_patterns,
            },
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AutoCADTaskLog(Base):
    """AutoCAD 任务执行日志表"""

    __tablename__ = 'autocad_task_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    config_id = Column(Integer, comment='配置ID（关联 autocad_config.id）')
    task_name = Column(String(200), comment='任务名称')

    # 执行信息
    dwg_file = Column(String(1000), comment='处理的 DWG 文件')
    status = Column(String(50), comment='状态：success, failed, running')
    error_message = Column(Text, comment='错误信息')

    # 时间统计
    start_time = Column(DateTime, comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    duration_seconds = Column(Float, comment='执行时长（秒）')

    # 详细日志
    execution_log = Column(Text, comment='执行日志（详细）')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    def __repr__(self):
        return f"<AutoCADTaskLog(id={self.id}, task='{self.task_name}', status='{self.status}')>"

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_id': self.config_id,
            'task_name': self.task_name,
            'dwg_file': self.dwg_file,
            'status': self.status,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'execution_log': self.execution_log,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
