"""
Formation-to-lithology mapping and lithology color conventions.

Two authoritative sources are combined here:

1. Formation lithologies — KGS Bulletin 189 (Zeller, 1968):
   "The Stratigraphic Succession in Kansas"
   https://www.kgs.ku.edu/Publications/Bulletins/189/index.html

2. Color conventions — USGS Technical Methods 11-B1:
   "Selection of Colors and Patterns for Geologic Maps" (Lindberg, 2005)
   https://pubs.usgs.gov/tm/2005/11B01/05tm11b01.html
   Blues for carbonates, yellows for clastics, grays for shales,
   browns for dolomite — consistent with USGS geologic map practice.

Public functions: get_formation_color, get_formation_lithology
"""

# ---------------------------------------------------------------------------
# Lithology color palette — USGS TM 11-B1 convention (hex)
# ---------------------------------------------------------------------------

LITHOLOGY_COLORS: dict[str, str] = {
    "Limestone":            "#6baed6",  # blue        (carbonate)
    "Limestone/Shale":      "#9ecae1",  # light blue  (mixed carbonate-clastic)
    "Shale":                "#969696",  # gray        (fine-grained clastic)
    "Black Shale":          "#525252",  # dark gray   (organic-rich shale)
    "Sandstone":            "#f5c842",  # yellow      (coarse clastic)
    "Sandstone/Shale":      "#d4a520",  # tan-yellow  (mixed clastic)
    "Dolomite":             "#c49a6c",  # brown       (diagenetic carbonate)
    "Dolomite/Chert":       "#a0785a",  # dark brown  (dolomite with chert)
    "Chert":                "#e08060",  # orange-red  (siliceous)
    "Anhydrite":            "#e8c4e8",  # pale purple (evaporite)
    "Salt":                 "#f5f0ff",  # near white  (evaporite)
    "Conglomerate":         "#b8860b",  # dark yellow (coarse clastic)
    "Coal":                 "#252525",  # near black  (organic)
    "Unknown":              "#bdbdbd",  # light gray  (fallback)
}


# ---------------------------------------------------------------------------
# Formation → primary lithology — KGS Bulletin 189 (Zeller, 1968)
# Covers Pennsylvanian and Permian section typical of El Dorado field.
# ---------------------------------------------------------------------------

FORMATION_LITHOLOGY: dict[str, str] = {
    # ── Permian / Upper Pennsylvanian ────────────────────────────────────────
    "Oread":                        "Limestone/Shale",
    "Toronto":                      "Limestone",
    "Heebner Shale":                "Black Shale",
    "Heebner":                      "Black Shale",

    # ── Missourian (Upper Pennsylvanian) ─────────────────────────────────────
    "Douglas":                      "Sandstone/Shale",
    "Douglas Shale":                "Shale",
    "Lansing":                      "Limestone/Shale",
    "Kansas City":                  "Limestone/Shale",
    "Stark Shale":                  "Black Shale",
    "Stark":                        "Black Shale",
    "Checkerboard":                 "Limestone",
    "Altamont":                     "Limestone",

    # ── Desmoinesian (Middle Pennsylvanian) ──────────────────────────────────
    "Cherokee":                     "Sandstone/Shale",
    "Ardmore":                      "Limestone",
    "Verdigris":                    "Limestone",

    # ── Mississippian ────────────────────────────────────────────────────────
    "Erosional Chert Conglomerate": "Conglomerate",
    "Erosional Mississippian":      "Conglomerate",
    "Mississippian":                "Limestone",
    "Osage":                        "Limestone",
    "St. Louis":                    "Limestone",
    "Ste. Genevieve":               "Limestone",
    "Meramecian":                   "Limestone",
    "Chesteran":                    "Limestone",

    # ── Permian / Evaporites ─────────────────────────────────────────────────
    "Anhydrite":                    "Anhydrite",
    "Stone Corral":                 "Anhydrite",
    "Hutchinson Salt":              "Salt",
    "Wellington":                   "Shale",
    "Blaine":                       "Anhydrite",
    "Cedar Hills":                  "Sandstone",
    "Day Creek":                    "Dolomite",

    # ── Schaben field (Pennsylvanian) ─────────────────────────────────────────
    "Lansing-Kansas City":          "Limestone/Shale",
    "Pawnee":                       "Limestone",
    "Fort Scott":                   "Limestone/Shale",

    # ── Ordovician ───────────────────────────────────────────────────────────
    "Arbuckle":                     "Dolomite/Chert",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_formation_lithology(formation_name: str) -> str:
    """Return the primary lithology for a named formation.

    Performs a case-insensitive prefix match so minor spelling variants
    (e.g. 'Heebner Shale Member') still resolve correctly.

    Args:
        formation_name: Formation name as it appears in the LAS ~Other section.

    Returns:
        Lithology string from FORMATION_LITHOLOGY, or 'Unknown' if not found.
    """
    name = formation_name.strip()

    # ✅ Guard: empty name
    if not name:
        return "Unknown"

    # ✅ Exact match first
    if name in FORMATION_LITHOLOGY:
        return FORMATION_LITHOLOGY[name]

    # 🔄 Case-insensitive fallback
    name_lower = name.lower()
    for key, lith in FORMATION_LITHOLOGY.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return lith

    return "Unknown"


def get_formation_color(formation_name: str) -> str:
    """Return the hex color for a named formation.

    Chains get_formation_lithology → LITHOLOGY_COLORS.

    Args:
        formation_name: Formation name as it appears in the LAS ~Other section.

    Returns:
        Hex color string (e.g. '#6baed6'). Never raises — unknown formations
        return the 'Unknown' fallback color.
    """
    lithology = get_formation_lithology(formation_name)
    return LITHOLOGY_COLORS.get(lithology, LITHOLOGY_COLORS["Unknown"])
