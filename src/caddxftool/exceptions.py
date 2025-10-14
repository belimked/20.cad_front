from __future__ import annotations


class CadDxFToolError(RuntimeError):
    """基础异常类型。"""


class ExternalToolError(CadDxFToolError):
    """外部工具调用失败。"""


class ConversionError(CadDxFToolError):
    """文件转换过程出现问题。"""
