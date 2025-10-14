from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Sequence

from ..adapters import oda_converter
from ..exceptions import ConversionError, ExternalToolError
from ..models import ConvertConfig, ConvertReport

logger = logging.getLogger(__name__)


class ConvertService:
    """
    DWG→DXF 批量转换服务。
    """

    def __init__(self, adapter=oda_converter) -> None:
        self._adapter = adapter

    def run(self, config: ConvertConfig) -> ConvertReport:
        if not config.input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {config.input_dir}")

        config.output_dir.mkdir(parents=True, exist_ok=True)

        dwg_files = list(self._collect_dwg_files(config.input_dir))
        report = ConvertReport()

        if not dwg_files:
            logger.warning("输入目录未找到 DWG 文件: %s", config.input_dir)
            return report

        for dwg_file in dwg_files:
            try:
                self._adapter.convert(
                    dwg_path=dwg_file,
                    output_dir=config.output_dir,
                    overwrite=config.overwrite,
                    executable=config.oda_path,
                )
            except FileExistsError as error:
                logger.warning("文件已存在且未开启覆盖: %s", dwg_file)
                report.record_failure(dwg_file, str(error))
            except (ExternalToolError, ConversionError) as error:
                logger.error("转换失败: %s，原因：%s", dwg_file, error)
                report.record_failure(dwg_file, str(error))
            else:
                logger.info("转换成功: %s", dwg_file)
                report.record_success(dwg_file)

        return report

    @staticmethod
    def _collect_dwg_files(input_dir: Path) -> Iterable[Path]:
        pattern_variants: Sequence[str] = ("*.dwg", "*.DWG")
        seen: dict[str, Path] = {}
        for pattern in pattern_variants:
            for file_path in input_dir.rglob(pattern):
                key = file_path.resolve().as_posix()
                seen[key] = file_path

        for path in sorted(seen.values(), key=lambda p: p.as_posix()):
            yield path
