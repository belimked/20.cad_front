from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass(slots=True)
class ConvertConfig:
    input_dir: Path
    output_dir: Path
    overwrite: bool = False
    oda_path: Optional[Path] = None


@dataclass(slots=True)
class SplitConfig:
    source_file: Path
    output_dir: Path
    include_frame: bool = True
    naming_pattern: str = "{name}_region_{index}.dxf"


@dataclass(slots=True)
class RectangleRegion:
    id: str
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    layer: Optional[str] = None
    frame_handle: Optional[str] = None

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    def to_polygon(self):
        """
        延迟创建 shapely Polygon，避免模块级依赖。
        """
        from shapely.geometry import Polygon  # type: ignore

        return Polygon(
            [
                (self.min_x, self.min_y),
                (self.max_x, self.min_y),
                (self.max_x, self.max_y),
                (self.min_x, self.max_y),
            ]
        )


@dataclass(slots=True)
class FailedItem:
    source: Path
    error: str


@dataclass(slots=True)
class ConvertReport:
    processed: List[Path] = field(default_factory=list)
    succeeded: List[Path] = field(default_factory=list)
    failed: List[FailedItem] = field(default_factory=list)

    def record_success(self, path: Path) -> None:
        self.processed.append(path)
        self.succeeded.append(path)

    def record_failure(self, path: Path, error: str) -> None:
        self.processed.append(path)
        self.failed.append(FailedItem(source=path, error=error))

    @property
    def total(self) -> int:
        return len(self.processed)

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)


@dataclass(slots=True)
class SplitReport:
    source_file: Path
    generated: List[Path] = field(default_factory=list)
    skipped_regions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def record_generated(self, path: Path) -> None:
        self.generated.append(path)

    def record_skip(self, region_id: str, reason: str) -> None:
        message = f"{region_id}: {reason}"
        self.skipped_regions.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def generated_count(self) -> int:
        return len(self.generated)
