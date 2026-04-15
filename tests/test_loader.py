"""
Tests for src/las/loader.py
"""

from pathlib import Path

import numpy as np
import pytest

from src.las.loader import load_las

_DEMO_DIR = Path("data/demo/El Dorado")
_SAMPLE = _DEMO_DIR / "Barnhill_'A'_30.las"


class TestLoadLas:
    """Tests for load_las()."""

    def test_returns_dataframe_and_meta(self):
        """Valid LAS file returns a non-empty DataFrame and a populated meta dict."""
        curves, meta = load_las(_SAMPLE)

        assert not curves.empty
        assert curves.index.name == "depth_ft"
        assert isinstance(meta, dict)
        assert meta["well_name"] is not None

    def test_nulls_replaced_with_nan(self):
        """Null values (-999.25) must be replaced with NaN in curves."""
        curves, _ = load_las(_SAMPLE)

        assert -999.25 not in curves.values
        # At least some NaN should be present (shallow depths have nulls in this file)
        assert curves.isnull().any().any()

    def test_metadata_fields_present(self):
        """Meta dict must contain all expected keys."""
        _, meta = load_las(_SAMPLE)

        required = {"well_name", "field", "api", "lat", "lon",
                    "elev_ft", "depth_start_ft", "depth_stop_ft",
                    "available_curves", "raw_other"}
        assert required.issubset(meta.keys())

    def test_metadata_field_values(self):
        """Meta fields match known values in the sample file."""
        _, meta = load_las(_SAMPLE)

        assert meta["field"] == "El Dorado"
        assert meta["api"] == "15-015-23876"
        assert meta["depth_start_ft"] == pytest.approx(245.0)
        assert meta["depth_stop_ft"] == pytest.approx(2485.5)

    def test_available_curves_list(self):
        """available_curves must be a non-empty list of strings."""
        _, meta = load_las(_SAMPLE)

        assert isinstance(meta["available_curves"], list)
        assert len(meta["available_curves"]) > 0
        assert all(isinstance(c, str) for c in meta["available_curves"])

    def test_raw_other_preserved(self):
        """raw_other must contain the formation table header."""
        _, meta = load_las(_SAMPLE)

        assert "BASE,TOP,FORMATION" in meta["raw_other"].upper()

    def test_file_not_found_raises(self):
        """Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_las("data/demo/El Dorado/nonexistent.las")

    def test_depth_index_is_numeric(self):
        """Depth index must be numeric (float)."""
        curves, _ = load_las(_SAMPLE)

        assert curves.index.dtype == np.float64
