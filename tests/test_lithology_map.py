"""
Tests for src/las/lithology_map.py
"""

from src.las.lithology_map import (
    FORMATION_LITHOLOGY,
    LITHOLOGY_COLORS,
    get_formation_color,
    get_formation_lithology,
)


class TestGetFormationLithology:
    """Tests for get_formation_lithology()."""

    def test_exact_match_known_formation(self):
        """Known formation returns correct lithology."""
        assert get_formation_lithology("Arbuckle") == "Dolomite/Chert"
        assert get_formation_lithology("Lansing") == "Limestone/Shale"
        assert get_formation_lithology("Stark Shale") == "Black Shale"
        assert get_formation_lithology("Cherokee") == "Sandstone/Shale"

    def test_case_insensitive_fallback(self):
        """Case variations still resolve to a known lithology."""
        assert get_formation_lithology("arbuckle") != "Unknown"
        assert get_formation_lithology("LANSING") != "Unknown"

    def test_partial_name_match(self):
        """Partial names that contain a known key resolve correctly."""
        assert get_formation_lithology("Heebner Shale Member") != "Unknown"

    def test_unknown_formation_returns_unknown(self):
        """Formation not in the dict returns 'Unknown'."""
        assert get_formation_lithology("Zzzformation") == "Unknown"

    def test_empty_string_returns_unknown(self):
        """Empty string returns 'Unknown'."""
        assert get_formation_lithology("") == "Unknown"


class TestGetFormationColor:
    """Tests for get_formation_color()."""

    def test_returns_hex_string(self):
        """Return value is a valid hex color string."""
        color = get_formation_color("Arbuckle")
        assert color.startswith("#")
        assert len(color) == 7

    def test_known_formation_returns_non_fallback_color(self):
        """Known formation returns a color different from the Unknown fallback."""
        unknown_color = LITHOLOGY_COLORS["Unknown"]
        assert get_formation_color("Lansing") != unknown_color
        assert get_formation_color("Cherokee") != unknown_color

    def test_unknown_formation_returns_fallback_color(self):
        """Unknown formation returns the 'Unknown' fallback color."""
        assert get_formation_color("Zzzformation") == LITHOLOGY_COLORS["Unknown"]

    def test_all_lithologies_have_colors(self):
        """Every lithology in FORMATION_LITHOLOGY has a color in LITHOLOGY_COLORS."""
        for formation, lithology in FORMATION_LITHOLOGY.items():
            assert lithology in LITHOLOGY_COLORS, (
                f"Formation '{formation}' maps to lithology '{lithology}' "
                f"which has no entry in LITHOLOGY_COLORS"
            )
