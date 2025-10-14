from pathlib import Path
from unittest import mock

import pytest

from src.caddxftool.models import RectangleRegion, SplitConfig
from src.caddxftool.services import split_service


@pytest.fixture
def sample_regions():
    return [
        RectangleRegion(id="frame-1", min_x=0, min_y=0, max_x=10, max_y=5),
        RectangleRegion(id="frame-2", min_x=12, min_y=0, max_x=20, max_y=6),
    ]


def test_split_service_exports_regions(tmp_path: Path, sample_regions):
    source = tmp_path / "plan.dxf"
    source.write_text("dummy")

    dummy_ctx = object()

    with (
        mock.patch.object(
            split_service.reader,
            "load_drawing",
            return_value=dummy_ctx,
        ) as load_mock,
        mock.patch.object(
            split_service.rectangle_detector,
            "find_rectangles",
            return_value=sample_regions,
        ) as detect_mock,
        mock.patch.object(split_service.writer, "write_sub_dxf") as writer_mock,
    ):
        config = SplitConfig(
            source_file=source,
            output_dir=tmp_path / "out",
            include_frame=True,
            naming_pattern="{name}_part_{index}.dxf",
        )

        service = split_service.SplitService()
        report = service.run(config)

    assert load_mock.called
    assert detect_mock.called
    assert writer_mock.call_count == len(sample_regions)
    assert len(report.generated) == len(sample_regions)
    for idx, call in enumerate(writer_mock.call_args_list, start=1):
        args, kwargs = call
        assert args[0] is dummy_ctx
        assert args[1] == sample_regions[idx - 1]
        output_path = args[2]
        assert output_path.name == f"plan_part_{idx}.dxf"
        assert output_path.parent == config.output_dir


def test_split_service_handles_missing_rectangles(tmp_path: Path):
    source = tmp_path / "plan.dxf"
    source.write_text("dummy")

    with (
        mock.patch.object(split_service.reader, "load_drawing", return_value=object()),
        mock.patch.object(split_service.rectangle_detector, "find_rectangles", return_value=[]),
    ):
        service = split_service.SplitService()
        report = service.run(
            SplitConfig(
                source_file=source,
                output_dir=tmp_path / "out",
            )
        )

    assert report.generated == []
    assert report.warnings
