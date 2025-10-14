from __future__ import annotations

from collections.abc import Iterable
from typing import List, Sequence, Tuple

from ..models import RectangleRegion
from .reader import DrawingContext

EPSILON = 1e-6


def find_rectangles(ctx: DrawingContext) -> List[RectangleRegion]:
    """
    在 DXF 模型空间中识别轴对齐矩形框。
    """
    regions: List[RectangleRegion] = []
    for entity in ctx.modelspace.query("LWPOLYLINE POLYLINE"):
        points = _extract_points(entity)
        if not points:
            continue

        if not _is_closed(points):
            continue

        min_x, min_y, max_x, max_y = _bounds(points)
        if abs(max_x - min_x) < EPSILON or abs(max_y - min_y) < EPSILON:
            continue

        if not _forms_rectangle(points, min_x, min_y, max_x, max_y):
            continue

        handle = getattr(entity.dxf, "handle", None)
        region_id = str(handle) if handle else f"region-{len(regions) + 1}"
        layer = getattr(entity.dxf, "layer", None)

        regions.append(
            RectangleRegion(
                id=region_id,
                min_x=min_x,
                min_y=min_y,
                max_x=max_x,
                max_y=max_y,
                layer=layer,
                frame_handle=handle,
            )
        )

    return regions


def _extract_points(entity) -> List[Tuple[float, float]]:
    """
    从多段线实体中提取二维坐标。
    """
    if entity.dxftype() == "LWPOLYLINE":
        return [(float(x), float(y)) for x, y, *_ in entity.get_points("xy")]

    if entity.dxftype() == "POLYLINE":
        return [
            (float(vertex.dxf.location.x), float(vertex.dxf.location.y))
            for vertex in entity.vertices()
        ]

    return []


def _is_closed(points: Sequence[Tuple[float, float]]) -> bool:
    if not points:
        return False

    first = points[0]
    last = points[-1]
    return abs(first[0] - last[0]) < EPSILON and abs(first[1] - last[1]) < EPSILON


def _bounds(points: Iterable[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _forms_rectangle(
    points: Sequence[Tuple[float, float]],
    min_x: float,
    min_y: float,
    max_x: float,
    max_y: float,
) -> bool:
    """
    判断多段线是否形成轴对齐矩形。
    """
    if len(points) < 4:
        return False

    unique_points = {(_round(x), _round(y)) for x, y in points[:-1]}
    if len(unique_points) < 4:
        return False

    for x, y in unique_points:
        on_boundary = (
            abs(x - min_x) < EPSILON
            or abs(x - max_x) < EPSILON
            or abs(y - min_y) < EPSILON
            or abs(y - max_y) < EPSILON
        )
        if not on_boundary:
            return False

    corners = {
        (_round(min_x), _round(min_y)),
        (_round(min_x), _round(max_y)),
        (_round(max_x), _round(min_y)),
        (_round(max_x), _round(max_y)),
    }

    return corners.issubset(unique_points)


def _round(value: float) -> float:
    return round(value, 6)
