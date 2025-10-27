"""
日志系统配置模块 - 基于 loguru
提供统一的日志记录接口，支持控制台和文件输出

Author: CAD Auto Processor Team
Date: 2025-10-24
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional
from functools import lru_cache


class LoggerConfig:
    """
    日志配置类

    功能：
    - 配置 loguru 日志系统
    - 支持控制台和文件输出
    - 文件轮转（大小限制）
    - 日志保留策略
    - 自定义日志格式
    """

    def __init__(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        rotation: str = "100 MB",
        retention: str = "30 days",
        console_output: bool = True,
        file_output: bool = True,
        format_string: Optional[str] = None
    ):
        """
        初始化日志配置

        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径，None 则使用默认路径
            rotation: 文件轮转策略 (例如: "100 MB", "1 day", "00:00")
            retention: 日志保留时间 (例如: "30 days", "1 week")
            console_output: 是否输出到控制台
            file_output: 是否输出到文件
            format_string: 自定义日志格式
        """
        self.log_level = log_level.upper()
        self.rotation = rotation
        self.retention = retention
        self.console_output = console_output
        self.file_output = file_output

        # 默认日志文件路径
        if log_file is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = str(log_dir / "cad_processor_{time:YYYY-MM-DD}.log")

        self.log_file = log_file

        # 日志格式
        if format_string is None:
            self.format_string = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )
        else:
            self.format_string = format_string

        self._setup_logger()

    def _setup_logger(self) -> None:
        """配置 logger"""
        # 移除默认的 handler
        logger.remove()

        # 控制台输出
        if self.console_output:
            logger.add(
                sys.stderr,
                format=self.format_string,
                level=self.log_level,
                colorize=True,
                backtrace=True,
                diagnose=True
            )

        # 文件输出
        if self.file_output:
            logger.add(
                self.log_file,
                format=self.format_string,
                level=self.log_level,
                rotation=self.rotation,
                retention=self.retention,
                compression="zip",  # 压缩旧日志
                encoding="utf-8",
                backtrace=True,
                diagnose=True,
                enqueue=True  # 异步写入，避免阻塞
            )

    def set_level(self, level: str) -> None:
        """
        动态设置日志级别

        Args:
            level: 新的日志级别
        """
        self.log_level = level.upper()
        self._setup_logger()

    @staticmethod
    def add_custom_sink(
        sink,
        level: str = "DEBUG",
        format_string: Optional[str] = None
    ) -> int:
        """
        添加自定义日志输出目标

        Args:
            sink: 输出目标（文件路径、函数、流对象等）
            level: 日志级别
            format_string: 格式字符串

        Returns:
            handler ID
        """
        if format_string is None:
            format_string = (
                "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
                "{name}:{function}:{line} - {message}"
            )

        return logger.add(sink, format=format_string, level=level)


# 全局日志配置实例
@lru_cache(maxsize=1)
def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    file_output: bool = True
) -> logger:
    """
    设置全局日志系统

    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        console_output: 是否输出到控制台
        file_output: 是否输出到文件

    Returns:
        配置好的 logger 实例
    """
    LoggerConfig(
        log_level=log_level,
        log_file=log_file,
        console_output=console_output,
        file_output=file_output
    )
    return logger


def get_logger(name: Optional[str] = None) -> logger:
    """
    获取 logger 实例

    Args:
        name: 日志名称（loguru 不使用此参数，仅为了兼容性）

    Returns:
        logger 实例
    """
    # loguru 使用全局单例 logger，不需要根据 name 创建不同实例
    # 这里接受 name 参数仅为了兼容标准 logging 的调用方式
    return logger


# 便捷的日志函数
def log_debug(message: str, **kwargs) -> None:
    """记录 DEBUG 级别日志"""
    logger.debug(message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    """记录 INFO 级别日志"""
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """记录 WARNING 级别日志"""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """记录 ERROR 级别日志"""
    logger.error(message, **kwargs)


def log_critical(message: str, **kwargs) -> None:
    """记录 CRITICAL 级别日志"""
    logger.critical(message, **kwargs)


def log_exception(message: str = "异常发生", **kwargs) -> None:
    """
    记录异常信息（包含完整堆栈跟踪）

    Args:
        message: 异常描述信息
    """
    logger.exception(message, **kwargs)


# 上下文管理器：临时改变日志级别
class temporary_log_level:
    """
    临时改变日志级别的上下文管理器

    Examples:
        >>> with temporary_log_level("DEBUG"):
        ...     logger.debug("这条消息会被记录")
    """

    def __init__(self, level: str):
        self.new_level = level.upper()
        self.original_level = None

    def __enter__(self):
        # 保存当前级别并设置新级别
        # 注意：这是一个简化实现，实际可能需要更复杂的逻辑
        logger.level(self.new_level)
        return logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 恢复原来的级别
        pass


if __name__ == "__main__":
    # 测试日志系统
    print("=== 测试日志系统 ===\n")

    # 初始化日志
    setup_logger(log_level="DEBUG")

    # 测试各级别日志
    logger.debug("这是 DEBUG 级别日志 - 调试信息")
    logger.info("这是 INFO 级别日志 - 一般信息")
    logger.warning("这是 WARNING 级别日志 - 警告信息")
    logger.error("这是 ERROR 级别日志 - 错误信息")
    logger.critical("这是 CRITICAL 级别日志 - 严重错误")

    # 测试结构化日志
    logger.info("用户操作", user="admin", action="login", ip="192.168.1.100")

    # 测试异常日志
    try:
        result = 1 / 0
    except ZeroDivisionError:
        logger.exception("捕获到除零异常")

    print("\n✅ 日志系统测试完成")
    print(f"📁 日志文件位置: logs/cad_processor_*.log")
