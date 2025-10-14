from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Sequence, Tuple

import ezdxf
from ezdxf.addons import Importer
from shapely.geometry import LineString, Point, Polygon

from ..models import RectangleRegion
from .reader import DrawingContext

SUPPORTED_TYPES = {
    "LINE",
    "LWPOLYLINE",
    "POLYLINE",
    "CIRCLE",
    "ARC",
    "TEXT",
    "MTEXT",
    "POINT",
    "SPLINE",
}


def write_sub_dxf(
    ctx: DrawingContext,
    region: RectangleRegion,
    output_path: Path,
    include_frame: bool = True,
) -> Path:
    """
    将矩形区域内的实体导出为独立 DXF。
    """
    polygon = region.to_polygon()
    document = ezdxf.new(ctx.document.dxfversion)
    document.header["$INSUNITS"] = ctx.document.header.get("$INSUNITS", 1)
    target_msp = document.modelspace()

    entities_to_copy = []

    for entity in ctx.modelspace:
        if entity.dxftype() not in SUPPORTED_TYPES:
            continue

        if getattr(entity.dxf, "handle", None) == region.frame_handle:
            if include_frame:
                entities_to_copy.append(entity)
            continue

        geometry = _entity_geometry(entity)
        if geometry is None:
            continue

        if geometry.within(polygon) or geometry.intersects(polygon):
            entities_to_copy.append(entity)

    importer = Importer(ctx.document, document)
    for entity in entities_to_copy:
        importer.import_entity(entity, target_msp)
    importer.finalize()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.saveas(output_path)
    return output_path


def _entity_geometry(entity) -> Optional[Polygon | LineString | Point]:
    dxftype = entity.dxftype()

    if dxftype == "LINE":
        return LineString([_to_xy(entity.dxf.start), _to_xy(entity.dxf.end)])

    if dxftype == "LWPOLYLINE":
        points = [_to_xy(p) for p in entity.get_points("xy")]
        if not points:
            return None
        if getattr(entity, "closed", False):
            if points[0] != points[-1]:
                points.append(points[0])
            return Polygon(points)
        return LineString(points)

    if dxftype == "POLYLINE":
        points = [_to_xy(v.dxf.location) for v in entity.vertices()]
        if not points:
            return None
        if getattr(entity, "is_closed", False) or points[0] == points[-1]:
            if points[0] != points[-1]:
                points.append(points[0])
            return Polygon(points)
        return LineString(points)

    if dxftype == "CIRCLE":
        center = entity.dxf.center
        radius = float(entity.dxf.radius)
        return Point(_to_xy(center)).buffer(radius, resolution=32)

    if dxftype == "ARC":
        center = entity.dxf.center
        radius = float(entity.dxf.radius)
        start_angle = math.radians(float(entity.dxf.start_angle))
        end_angle = math.radians(float(entity.dxf.end_angle))
        points = _arc_points(_to_xy(center), radius, start_angle, end_angle)
        return LineString(points)

    if dxftype in {"TEXT", "MTEXT", "POINT"}:
        insert = getattr(entity.dxf, "insert", None) or getattr(entity.dxf, "location", None)
        if insert is None:
            return None
        return Point(_to_xy(insert))

    if dxftype == "SPLINE":
        points = [(_x, _y) for _x, _y, *_ in entity.approximate(64)]
        if not points:
            return None
        return LineString(points)

    return None


def _arc_points(center: Tuple[float, float], radius: float, start: float, end: float) -> Sequence[Tuple[float, float]]:
    step = max(4, int(abs(end - start) / (math.pi / 18)))  # 10° 间隔
    if end < start:
        end += 2 * math.pi

    return [
        (
            center[0] + radius * math.cos(start + i * (end - start) / step),
            center[1] + radius * math.sin(start + i * (end - start) / step),
        )
        for i in range(step + 1)
    ]


def _to_xy(value) -> Tuple[float, float]:
    if hasattr(value, "x") and hasattr(value, "y"):
        return float(value.x), float(value.y)
    x, y = value[:2]
    return float(x), float(y)
