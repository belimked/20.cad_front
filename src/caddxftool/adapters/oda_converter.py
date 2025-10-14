from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from ..exceptions import ConversionError, ExternalToolError

DEFAULT_INPUT_VERSION = "ACAD2010"
DEFAULT_OUTPUT_VERSION = "ACAD2010"
DEFAULT_OUTPUT_TYPE = "DXF"


def resolve_executable(explicit_path: Optional[Path] = None) -> Path:
    """
    根据优先级解析 ODAFileConverter 可执行文件路径。
    """
    if explicit_path:
        if explicit_path.exists():
            return explicit_path
        raise ExternalToolError(f"指定的 ODAFileConverter 路径不存在: {explicit_path}")

    env_path = shutil.which("ODAFileConverter")
    if env_path:
        return Path(env_path)

    raise ExternalToolError(
        "未找到 ODAFileConverter，可通过 --oda-path 指定或将其加入 PATH。"
    )


def build_command(
    executable: Path,
    source: Path,
    output_dir: Path,
    input_version: str = DEFAULT_INPUT_VERSION,
    output_version: str = DEFAULT_OUTPUT_VERSION,
    output_type: str = DEFAULT_OUTPUT_TYPE,
    recurse: bool = False,
    audit: bool = False,
) -> list[str]:
    """
    构造 ODAFileConverter 命令参数。
    """
    return [
        str(executable),
        str(source),
        str(output_dir),
        input_version,
        output_version,
        output_type,
        "1" if recurse else "0",
        "1" if audit else "0",
    ]


def convert(
    dwg_path: Path,
    output_dir: Path,
    overwrite: bool = False,
    executable: Optional[Path] = None,
    extra_args: Optional[Iterable[str]] = None,
) -> Path:
    """
    调用 ODAFileConverter 将单个 DWG 转换为 DXF。
    """
    if not dwg_path.exists():
        raise FileNotFoundError(f"DWG 文件不存在: {dwg_path}")

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    target_path = output_dir / f"{dwg_path.stem}.dxf"
    if target_path.exists() and not overwrite:
        raise FileExistsError(f"目标文件已存在: {target_path}")

    resolved_exec = resolve_executable(executable)

    command = build_command(resolved_exec, dwg_path, output_dir)
    if extra_args:
        command.extend(str(arg) for arg in extra_args)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise ExternalToolError(
            f"ODAFileConverter 调用失败，退出码 {result.returncode}，"
            f"stderr: {result.stderr.strip()}"
        )

    if not target_path.exists():
        raise ConversionError(f"转换完成但未找到输出文件: {target_path}")

    return target_path
