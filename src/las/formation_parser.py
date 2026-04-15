"""
Formation tops/bases parser for reservoir-visualizer.

Parses the ~Other section of Kansas LAS files into a list of formation
dicts. Handles the CSV format used by the Kansas Geological Survey:

    BASE,TOP,FORMATION
    nan,1387.0,Oread
    2154.0,1992.0,Kansas City

Missing BASE values are inferred from the next formation's TOP after
sorting by depth. The deepest formation retains nan if BASE is absent.

Public functions: parse_formations
"""

import io
import math

import pandas as pd


def parse_formations(raw_other: str) -> list[dict]:
    """Parse formation tops and bases from a LAS ~Other section.

    Args:
        raw_other: Raw text from the LAS ~Other section (las.other).

    Returns:
        List of dicts sorted by top_ft ascending, each with keys:
            - name (str): Formation name.
            - top_ft (float): Formation top depth in feet.
            - base_ft (float | None): Formation base depth in feet,
              or None if it cannot be inferred.

    Raises:
        ValueError: If the section contains a header but no data rows.
    """
    # ----------------------------------------
    # Step 1 — Guard: empty or missing section
    # ----------------------------------------
    text = raw_other.strip() if raw_other else ""
    if not text or "BASE,TOP,FORMATION" not in text.upper():
        return []

    # ----------------------------------------
    # Step 2 — Isolate the CSV block
    # ----------------------------------------
    start = text.upper().index("BASE,TOP,FORMATION")
    csv_text = text[start:]

    # ----------------------------------------
    # Step 3 — Parse CSV rows
    # ----------------------------------------
    df = pd.read_csv(
        io.StringIO(csv_text),
        header=0,
        names=["base_ft", "top_ft", "name"],
        skipinitialspace=True,
    )
    df["name"] = df["name"].str.strip()
    df["top_ft"] = pd.to_numeric(df["top_ft"], errors="coerce")
    df["base_ft"] = pd.to_numeric(df["base_ft"], errors="coerce")

    # ✅ Drop rows with missing name or top
    df = df.dropna(subset=["name", "top_ft"])

    if df.empty:
        raise ValueError("Formation header found but no valid data rows in ~Other section.")

    # ----------------------------------------
    # Step 4 — Sort by top depth ascending
    # ----------------------------------------
    df = df.sort_values("top_ft").reset_index(drop=True)

    # ----------------------------------------
    # Step 5 — Infer missing BASE from next TOP
    # ----------------------------------------
    for i, row in df.iterrows():
        if math.isnan(row["base_ft"]) and i + 1 < len(df):
            df.at[i, "base_ft"] = df.at[i + 1, "top_ft"]

    # 🔄 Convert remaining nan to None for clean downstream use
    formations = []
    for _, row in df.iterrows():
        base = None if math.isnan(row["base_ft"]) else float(row["base_ft"])
        formations.append({
            "name":    row["name"],
            "top_ft":  float(row["top_ft"]),
            "base_ft": base,
        })

    return formations
