"""
Tests for src/render/multi_well.py
"""

import numpy as np
import plotly.graph_objects as go
import pytest

from src.render.multi_well import (
    build_multi_well_figure,
    _latlon_to_xy,
    _common_formations,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_WELL_A = {
    "meta": {
        "well_name": "Well A", "lat": 37.81, "lon": -96.92,
        "depth_start_ft": 200.0, "depth_stop_ft": 2500.0,
    },
    "formations": [
        {"name": "Oread",       "top_ft": 1400.0, "base_ft": 1430.0},
        {"name": "Lansing",     "top_ft": 1720.0, "base_ft": 2000.0},
        {"name": "Arbuckle",    "top_ft": 2460.0, "base_ft": None},
    ],
}

_WELL_B = {
    "meta": {
        "well_name": "Well B", "lat": 37.82, "lon": -96.93,
        "depth_start_ft": 200.0, "depth_stop_ft": 2500.0,
    },
    "formations": [
        {"name": "Oread",       "top_ft": 1410.0, "base_ft": 1440.0},
        {"name": "Lansing",     "top_ft": 1730.0, "base_ft": 2010.0},
        {"name": "Arbuckle",    "top_ft": 2470.0, "base_ft": None},
    ],
}

_WELL_C = {
    "meta": {
        "well_name": "Well C", "lat": 37.80, "lon": -96.94,
        "depth_start_ft": 200.0, "depth_stop_ft": 2500.0,
    },
    "formations": [
        {"name": "Oread",       "top_ft": 1390.0, "base_ft": 1420.0},
        {"name": "Lansing",     "top_ft": 1710.0, "base_ft": 1990.0},
    ],
}

_TWO_WELLS   = [_WELL_A, _WELL_B]
_THREE_WELLS = [_WELL_A, _WELL_B, _WELL_C]


class TestBuildMultiWellFigure:
    """Tests for build_multi_well_figure()."""

    def test_returns_plotly_figure(self):
        """Return type is a Plotly Figure."""
        assert isinstance(build_multi_well_figure(_TWO_WELLS), go.Figure)

    def test_figure_has_mesh3d_and_stick_traces(self):
        """Figure contains both Mesh3d (formations) and Scatter3d (sticks) traces."""
        fig = build_multi_well_figure(_TWO_WELLS)
        types = {type(t).__name__ for t in fig.data}
        assert "Mesh3d" in types
        assert "Scatter3d" in types

    def test_well_sticks_equal_well_count(self):
        """Number of Scatter3d traces equals the number of wells."""
        fig = build_multi_well_figure(_THREE_WELLS)
        sticks = [t for t in fig.data if isinstance(t, go.Scatter3d)]
        assert len(sticks) == 3

    def test_volumes_for_common_formations_only(self):
        """Mesh3d volumes are created only for formations present in ≥2 wells."""
        fig = build_multi_well_figure(_THREE_WELLS)
        volumes = [t for t in fig.data if isinstance(t, go.Mesh3d)]
        # Oread and Lansing are in all 3 wells; Arbuckle only in A and B → 3 volumes
        assert len(volumes) == 3

    def test_custom_formation_names_filter(self):
        """formation_names argument limits which volumes are rendered."""
        fig = build_multi_well_figure(_TWO_WELLS, formation_names=["Oread"])
        volumes = [t for t in fig.data if isinstance(t, go.Mesh3d)]
        assert len(volumes) == 1
        assert "Oread" in volumes[0].name

    def test_z_axis_title_is_elevation(self):
        """Z axis uses elevation convention (positive up, no reversal)."""
        fig = build_multi_well_figure(_TWO_WELLS)
        assert fig.layout.scene.zaxis.title.text == "Elevation (ft)"

    def test_single_well_raises(self):
        """Fewer than 2 valid wells raises ValueError."""
        with pytest.raises(ValueError):
            build_multi_well_figure([_WELL_A])

    def test_well_without_latlon_is_skipped(self):
        """Well missing lat/lon is excluded; figure still builds if 2+ remain."""
        no_coords = {
            "meta": {"well_name": "No coords", "lat": None, "lon": None,
                     "depth_start_ft": 200.0, "depth_stop_ft": 2500.0},
            "formations": _WELL_A["formations"],
        }
        fig = build_multi_well_figure([_WELL_A, _WELL_B, no_coords])
        sticks = [t for t in fig.data if isinstance(t, go.Scatter3d)]
        assert len(sticks) == 2   # no_coords excluded


class TestLatLonToXY:
    """Tests for _latlon_to_xy()."""

    def test_centroid_maps_to_origin(self):
        """Mean lat/lon maps to approximately (0, 0)."""
        lats = [37.81, 37.82, 37.80]
        lons = [-96.92, -96.93, -96.94]
        xs, ys = _latlon_to_xy(lats, lons)
        assert abs(xs.mean()) < 1.0
        assert abs(ys.mean()) < 1.0

    def test_north_well_has_positive_y(self):
        """Well north of centroid has positive Y coordinate."""
        lats = [37.80, 37.82]
        lons = [-96.92, -96.92]
        _, ys = _latlon_to_xy(lats, lons)
        assert ys[1] > ys[0]

    def test_east_well_has_positive_x(self):
        """Well east (less negative lon) of centroid has positive X coordinate."""
        lats = [37.81, 37.81]
        lons = [-96.93, -96.91]
        xs, _ = _latlon_to_xy(lats, lons)
        assert xs[1] > xs[0]

    def test_output_in_metres_scale(self):
        """~0.01 deg latitude ≈ 1,113 m — output should be in that range."""
        lats = [37.80, 37.81]
        lons = [-96.92, -96.92]
        _, ys = _latlon_to_xy(lats, lons)
        diff = abs(ys[1] - ys[0])
        assert 900 < diff < 1300


class TestCommonFormations:
    """Tests for _common_formations()."""

    def test_returns_formations_in_two_or_more_wells(self):
        """Only formations present in ≥2 wells are returned."""
        wells = [_WELL_A, _WELL_B, _WELL_C]
        common = _common_formations(wells, min_count=2)
        assert "Oread"   in common
        assert "Lansing" in common

    def test_formation_in_one_well_excluded(self):
        """Formation unique to one well is excluded."""
        unique_well = {
            "meta": _WELL_A["meta"],
            "formations": [{"name": "UniqueFormation", "top_ft": 1000.0, "base_ft": 1050.0}],
        }
        wells = [_WELL_A, _WELL_B, unique_well]
        common = _common_formations(wells, min_count=2)
        assert "UniqueFormation" not in common

    def test_sorted_by_mean_top_depth(self):
        """Results are sorted by mean top depth ascending."""
        common = _common_formations([_WELL_A, _WELL_B], min_count=2)
        tops_order = ["Oread", "Lansing", "Arbuckle"]
        indices = [common.index(n) for n in tops_order if n in common]
        assert indices == sorted(indices)
