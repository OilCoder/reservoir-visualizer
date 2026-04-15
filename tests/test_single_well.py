"""
Tests for src/render/single_well.py
"""

import pytest
import plotly.graph_objects as go

from src.render.single_well import build_single_well_figure
from src.las.lithology_map import LITHOLOGY_COLORS

_FORMATIONS = [
    {"name": "Oread",       "top_ft": 1387.0, "base_ft": 1424.0},
    {"name": "Heebner Shale","top_ft": 1424.0, "base_ft": 1437.0},
    {"name": "Lansing",     "top_ft": 1711.0, "base_ft": 1992.0},
    {"name": "Arbuckle",    "top_ft": 2459.0, "base_ft": None},
]


class TestBuildSingleWellFigure:
    """Tests for build_single_well_figure()."""

    def test_returns_plotly_figure(self):
        """Return type is a Plotly Figure."""
        fig = build_single_well_figure(_FORMATIONS)
        assert isinstance(fig, go.Figure)

    def test_one_trace_per_valid_formation(self):
        """Figure has one Mesh3d trace per formation with valid geometry."""
        fig = build_single_well_figure(_FORMATIONS)
        assert len(fig.data) == len(_FORMATIONS)

    def test_all_traces_are_mesh3d(self):
        """Every trace is a Mesh3d."""
        fig = build_single_well_figure(_FORMATIONS)
        for trace in fig.data:
            assert isinstance(trace, go.Mesh3d)

    def test_trace_colors_are_hex(self):
        """Every trace color is a hex string."""
        fig = build_single_well_figure(_FORMATIONS)
        for trace in fig.data:
            assert trace.color.startswith("#")
            assert len(trace.color) == 7

    def test_known_formation_gets_non_fallback_color(self):
        """Known formations receive a color different from the Unknown fallback."""
        fallback = LITHOLOGY_COLORS["Unknown"]
        fig = build_single_well_figure(_FORMATIONS[:3])   # first 3 are known
        for trace in fig.data:
            assert trace.color != fallback

    def test_well_name_in_title(self):
        """Well name appears in the figure title."""
        fig = build_single_well_figure(_FORMATIONS, well_name="Test Well A")
        assert "Test Well A" in fig.layout.title.text

    def test_empty_formations_raises(self):
        """Empty formations list raises ValueError."""
        with pytest.raises(ValueError):
            build_single_well_figure([])

    def test_formation_with_none_base_is_rendered(self):
        """Formation with base_ft=None (deepest) still produces a trace."""
        only_unknown = [{"name": "Arbuckle", "top_ft": 2459.0, "base_ft": None}]
        fig = build_single_well_figure(only_unknown)
        assert len(fig.data) == 1

    def test_z_values_are_negative_depths(self):
        """Z coordinates are negative (depth on negative Z axis)."""
        fig = build_single_well_figure(_FORMATIONS[:1])
        trace = fig.data[0]
        assert all(z <= 0 for z in trace.z)

    def test_custom_width_affects_xy_extent(self):
        """Custom width_ft changes XY extent of the boxes."""
        fig_narrow = build_single_well_figure(_FORMATIONS[:1], width_ft=50.0)
        fig_wide   = build_single_well_figure(_FORMATIONS[:1], width_ft=500.0)
        max_narrow = max(abs(x) for x in fig_narrow.data[0].x)
        max_wide   = max(abs(x) for x in fig_wide.data[0].x)
        assert max_wide > max_narrow
