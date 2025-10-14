from __future__ import annotations

import logging
from pathlib import Path

from ..dxf import rectangle_detector, reader, writer
from ..models import RectangleRegion, SplitConfig, SplitReport

logger = logging.getLogger(__name__)


class SplitService:
    """按矩形方框拆分 DXF 文件。"""

    def __init__(self) -> None:
        self._reader = reader
        self._detector = rectangle_detector
        self._writer = writer

    def run(self, config: SplitConfig) -> SplitReport:
        if not config.source_file.exists():
            raise FileNotFoundError(f"DXF 文件不存在: {config.source_file}")

        config.output_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._reader.load_drawing(config.source_file)
        regions = self._detector.find_rectangles(ctx)

        report = SplitReport(source_file=config.source_file)

        if not regions:
            warning = "未识别到矩形方框，未生成任何文件。"
            logger.warning(warning)
            report.add_warning(warning)
            return report

        for index, region in enumerate(regions, start=1):
            output_path = self._build_output_path(config, region, index)
            try:
                self._writer.write_sub_dxf(
                    ctx,
                    region,
                    output_path,
                    include_frame=config.include_frame,
                )
            except Exception as error:  # noqa: BLE001 - 捕获并记录
                logger.error("拆分失败: %s，原因：%s", region.id, error)
                report.record_skip(region.id, str(error))
            else:
                logger.info("拆分成功: %s -> %s", region.id, output_path)
                report.record_generated(output_path)

        if not report.generated:
            report.add_warning("所有矩形均拆分失败，未生成输出文件。")

        return report

    @staticmethod
    def _build_output_path(config: SplitConfig, region: RectangleRegion, index: int) -> Path:
        try:
            filename = config.naming_pattern.format(
                name=config.source_file.stem,
                index=index,
                id=region.id,
            )
        except KeyError as error:
            raise ValueError(
                f"命名模板缺少占位符: {error}. 可用变量: name, index, id"
            ) from error

        if not filename.lower().endswith(".dxf"):
            filename = f"{filename}.dxf"

        return config.output_dir / filename
