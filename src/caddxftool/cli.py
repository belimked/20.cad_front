from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .exceptions import ConversionError, ExternalToolError
from .models import ConvertConfig, SplitConfig
from .services.convert_service import ConvertService
from .services.split_service import SplitService
from .utils.logging import setup_logging

app = typer.Typer(help="CAD 图纸转换与拆分工具")
console = Console()


@app.callback()
def main(
    verbose: int = typer.Option(
        0,
        "--verbose",
        "-v",
        count=True,
        help="增加日志详细程度，可重复使用。",
    ),
    log_file: Optional[Path] = typer.Option(
        None,
        "--log-file",
        help="可选的日志文件路径。",
        resolve_path=True,
        file_okay=True,
        dir_okay=False,
    ),
) -> None:
    """
    初始化全局日志配置。
    """
    level_map = {0: "INFO", 1: "DEBUG", 2: "DEBUG"}
    level = level_map.get(verbose, "DEBUG")
    setup_logging(level=level, log_file=log_file)


@app.command(help="将目录下所有 DWG 文件批量转换为 DXF。")
def convert(
    input_dir: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        resolve_path=True,
        help="包含 DWG 文件的输入目录。",
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        help="DXF 输出目录，需提前存在或具有写权限。",
        resolve_path=True,
        file_okay=False,
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="允许覆盖已存在的 DXF 文件。",
    ),
    oda_path: Optional[Path] = typer.Option(
        None,
        "--oda-path",
        help="自定义 ODAFileConverter 可执行文件路径。",
        resolve_path=True,
        file_okay=True,
        dir_okay=False,
    ),
) -> None:
    service = ConvertService()
    config = ConvertConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        overwrite=overwrite,
        oda_path=oda_path,
    )

    try:
        report = service.run(config)
    except (ExternalToolError, ConversionError, FileNotFoundError) as error:
        console.print(f"[red]转换失败：{error}[/red]")
        raise typer.Exit(code=1) from error

    console.print(
        f"[green]转换完成：{report.success_count}/{report.total} 个成功，"
        f"{report.failure_count} 个失败。[/green]"
    )

    if report.failure_count:
        for item in report.failed:
            console.print(f"[red]- {item.source}: {item.error}[/red]")
        raise typer.Exit(code=1)

    raise typer.Exit(code=0)


@app.command(help="按矩形方框拆分指定 DXF 文件。")
def split(
    source_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        resolve_path=True,
        help="需要拆分的 DXF 文件路径。",
    ),
    output_dir: Path = typer.Option(
        ...,
        "--output-dir",
        help="子 DXF 输出目录，需具备写权限。",
        resolve_path=True,
        file_okay=False,
    ),
    include_frame: bool = typer.Option(
        True,
        "--include-frame/--exclude-frame",
        help="是否在子 DXF 中保留原方框边界。",
    ),
    naming_pattern: str = typer.Option(
        "{name}_region_{index}.dxf",
        "--naming-pattern",
        help="子文件命名模式，可使用 {name} 与 {index} 占位符。",
    ),
) -> None:
    service = SplitService()
    config = SplitConfig(
        source_file=source_file,
        output_dir=output_dir,
        include_frame=include_frame,
        naming_pattern=naming_pattern,
    )

    try:
        report = service.run(config)
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]拆分失败：{error}[/red]")
        raise typer.Exit(code=1) from error

    if report.warnings:
        for warning in report.warnings:
            console.print(f"[yellow]{warning}[/yellow]")

    if report.skipped_regions:
        console.print("[red]以下区域未能导出：[/red]")
        for message in report.skipped_regions:
            console.print(f"  - {message}")

    console.print(f"[green]成功导出 {report.generated_count} 个子 DXF 文件。[/green]")

    exit_code = 0 if not report.skipped_regions else 1
    raise typer.Exit(code=exit_code)


def run() -> None:
    """
    Typer 应用入口。
    """
    app()


if __name__ == "__main__":
    run()
