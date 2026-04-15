"""
Tests for src/las/formation_parser.py
"""

import pytest

from src.las.formation_parser import parse_formations


class TestParseFormations:
    """Tests for parse_formations()."""

    _STANDARD = (
        "BASE,TOP,FORMATION\n"
        "nan,1387.0,Oread\n"
        "nan,1424.0,Heebner Shale\n"
        "2154.0,1992.0,Kansas City\n"
        "nan,2459.0,Arbuckle\n"
    )

    def test_returns_list_of_dicts(self):
        """Standard input returns a list of dicts."""
        result = parse_formations(self._STANDARD)

        assert isinstance(result, list)
        assert all(isinstance(f, dict) for f in result)

    def test_required_keys_present(self):
        """Each formation dict must have name, top_ft, base_ft."""
        result = parse_formations(self._STANDARD)

        for formation in result:
            assert "name" in formation
            assert "top_ft" in formation
            assert "base_ft" in formation

    def test_sorted_by_top_ascending(self):
        """Formations are sorted by top_ft ascending."""
        result = parse_formations(self._STANDARD)

        tops = [f["top_ft"] for f in result]
        assert tops == sorted(tops)

    def test_infers_base_from_next_top(self):
        """nan BASE is inferred from the next formation's TOP."""
        result = parse_formations(self._STANDARD)

        oread = next(f for f in result if f["name"] == "Oread")
        heebner = next(f for f in result if f["name"] == "Heebner Shale")

        assert oread["base_ft"] == pytest.approx(heebner["top_ft"])

    def test_explicit_base_preserved(self):
        """Explicit BASE values are not overwritten."""
        result = parse_formations(self._STANDARD)

        kc = next(f for f in result if f["name"] == "Kansas City")
        assert kc["base_ft"] == pytest.approx(2154.0)
        assert kc["top_ft"] == pytest.approx(1992.0)

    def test_deepest_formation_base_is_none(self):
        """Last formation retains None when BASE is absent."""
        result = parse_formations(self._STANDARD)

        deepest = result[-1]
        assert deepest["name"] == "Arbuckle"
        assert deepest["base_ft"] is None

    def test_empty_string_returns_empty_list(self):
        """Empty ~Other section returns an empty list."""
        assert parse_formations("") == []

    def test_none_returns_empty_list(self):
        """None ~Other returns an empty list."""
        assert parse_formations(None) == []

    def test_missing_header_returns_empty_list(self):
        """~Other without BASE,TOP,FORMATION header returns empty list."""
        assert parse_formations("Some random text\nwithout the header\n") == []

    def test_unsorted_input_is_sorted(self):
        """Rows not sorted by TOP are reordered correctly."""
        unsorted = (
            "BASE,TOP,FORMATION\n"
            "nan,2108.0,Stark\n"
            "nan,1401.0,Oread\n"
            "nan,1438.0,Heebner\n"
        )
        result = parse_formations(unsorted)
        tops = [f["top_ft"] for f in result]

        assert tops == sorted(tops)
        assert result[0]["name"] == "Oread"

    def test_no_data_rows_raises(self):
        """Header present but no valid data rows raises ValueError."""
        with pytest.raises(ValueError):
            parse_formations("BASE,TOP,FORMATION\n")
