from pathlib import Path
from types import SimpleNamespace

import pytest

from src.caddxftool.dxf import rectangle_detector
from src.caddxftool.dxf.reader import DrawingContext


class DummyModelSpace:
    def __init__(self, entities):
        self._entities = entities

    def query(self, _pattern):
        return self._entities


class DummyLwPolyline:
    def __init__(self, points, closed=True, layer="FRAME"):
        self._points = points
        self.closed = closed
        self.dxf = SimpleNamespace(layer=layer, handle="ABC123")

    def dxftype(self):
        return "LWPOLYLINE"

    def get_points(self, mode):
        assert mode == "xy"
        return [(*pt, 0, 0) for pt in self._points]


class DummyPolyline:
    def __init__(self, points, closed=True, layer="FRAME"):
        self._points = points
        self._closed = closed
        self.dxf = SimpleNamespace(layer=layer, handle="XYZ789")

    def dxftype(self):
        return "POLYLINE"

    def vertices(self):
        for x, y in self._points:
            yield SimpleNamespace(dxf=SimpleNamespace(location=SimpleNamespace(x=x, y=y)))

    @property
    def is_closed(self):
        return self._closed


@pytest.fixture
def base_context():
    return DrawingContext(
        path=Path("dummy.dxf"),
        document=None,
        modelspace=DummyModelSpace([]),
    )


def test_detects_rectangle_from_lwpolyline(base_context):
    entity = DummyLwPolyline(
        points=[(0, 0), (10, 0), (10, 5), (0, 5), (0, 0)],
        closed=True,
    )
    base_context.modelspace = DummyModelSpace([entity])

    regions = rectangle_detector.find_rectangles(base_context)

    assert len(regions) == 1
    region = regions[0]
    assert region.min_x == pytest.approx(0)
    assert region.max_x == pytest.approx(10)
    assert region.height == pytest.approx(5)


def test_ignores_non_rectangular_polyline(base_context):
    irregular = DummyPolyline(
        points=[(0, 0), (2, 1), (4, 0), (0, 0)],
        closed=True,
    )
    base_context.modelspace = DummyModelSpace([irregular])

    regions = rectangle_detector.find_rectangles(base_context)

    assert regions == []
