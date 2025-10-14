from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import ezdxf
from ezdxf import DXFError


@dataclass(slots=True)
class DrawingContext:
    path: Path
    document: "ezdxf.EzDxf"
    modelspace: "ezdxf.layouts.Modelspace"


def load_drawing(path: Path) -> DrawingContext:
    """
    读取 DXF 文件并返回上下文。
    """
    try:
        document = ezdxf.readfile(path)
    except DXFError as error:
        raise DXFError(f"读取 DXF 失败: {path} -> {error}") from error

    return DrawingContext(
        path=path,
        document=document,
        modelspace=document.modelspace(),
    )
