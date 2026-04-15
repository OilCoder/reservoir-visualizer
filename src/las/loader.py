"""
LAS file reader for reservoir-visualizer.

Reads a LAS 2.0 file and returns curve data as a DataFrame
plus a well metadata dictionary. Handles null replacement and
basic validation at load time.

Public functions: load_las
"""

from pathlib import Path

import lasio
import numpy as np
import pandas as pd

_NULL_VALUE = -999.25


def load_las(file_path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Read a LAS file and return curves and well metadata.

    Null values (-999.25) are replaced with NaN in the curves DataFrame.
    The raw ~Other section text is preserved in the metadata dict for
    downstream formation parsing.

    Args:
        file_path: Path to the .las file.

    Returns:
        Tuple of (curves, meta) where:
            - curves: DataFrame indexed by depth_ft with one column per curve.
            - meta: Dict with well header fields and raw ~Other text.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If lasio cannot parse the file.
    """
    path = Path(file_path)

    # ----------------------------------------
    # Step 1 — Validate file exists
    # ----------------------------------------
    if not path.exists():
        raise FileNotFoundError(f"LAS file not found: {path}")

    # ----------------------------------------
    # Step 2 — Parse with lasio
    # ----------------------------------------
    try:
        las = lasio.read(str(path))
    except Exception as exc:
        raise ValueError(f"Cannot parse {path.name}: {exc}") from exc

    # ----------------------------------------
    # Step 3 — Build curves DataFrame
    # ----------------------------------------
    curves = las.df()
    curves.replace(_NULL_VALUE, np.nan, inplace=True)
    curves.index.name = "depth_ft"

    # ----------------------------------------
    # Step 4 — Extract metadata
    # ----------------------------------------
    meta = _extract_meta(las, path)

    return curves, meta


def _extract_meta(las: lasio.LASFile, path: Path) -> dict:
    """Extract well metadata from a parsed LASFile.

    Args:
        las: Parsed LASFile object from lasio.
        path: Original file path used as fallback for well name.

    Returns:
        Dictionary with well header fields and raw ~Other text.
    """
    def _get(key: str, default=None):
        try:
            return las.well[key].value
        except KeyError:
            return default

    return {
        "well_name": _get("WELL", path.stem),
        "field":     _get("FLD"),
        "api":       _get("UWI") or _get("API"),
        "lat":       _get("LAT"),
        "lon":       _get("LONG"),
        "elev_ft":   _get("ELEV"),
        "depth_start_ft": _get("STRT"),
        "depth_stop_ft":  _get("STOP"),
        "null_value": _get("NULL", _NULL_VALUE),
        "available_curves": list(las.curves.keys()),
        "raw_other":  las.other,
    }
