"""
3D single-well formation renderer for reservoir-visualizer.

Builds a Plotly 3D figure where each formation is a rectangular block
colored by lithology (USGS TM 11-B1 / KGS Bulletin 189 conventions).
The well is centered at (x=0, y=0); depth runs on the negative Z axis
so the surface sits at the top of the figure.

Public functions: build_single_well_figure
"""

import plotly.graph_objects as go

from src.las.lithology_map import FORMATION_LITHOLOGY, get_formation_color, get_formation_lithology

_DEFAULT_BOTTOM_THICKNESS_FT = 50.0   # used when deepest formation has no base


def build_single_well_figure(
    formations: list[dict],
    well_name: str = "Well",
    width_ft: float = 200.0,
) -> go.Figure:
    """Build a Plotly 3D figure of formation layers for a single well.

    Each formation is a rectangular block centered at (0, 0) and colored
    by its lithology. Depth is displayed on the Z axis as negative feet
    (surface = 0, deeper = more negative).

    Args:
        formations: List of dicts from formation_parser.parse_formations().
            Each dict must have: name (str), top_ft (float), base_ft (float | None).
        well_name: Label shown in the figure title.
        width_ft: Half-width of each formation block in X and Y directions (ft).

    Returns:
        plotly.graph_objects.Figure with one Mesh3d trace per formation.

    Raises:
        ValueError: If formations list is empty.
    """
    if not formations:
        raise ValueError("formations list is empty — nothing to render.")

    # ----------------------------------------
    # Step 1 — Build one Mesh3d trace per formation
    # ----------------------------------------
    traces = []
    for formation in formations:
        trace = _formation_box(formation, width_ft)
        if trace is not None:
            traces.append(trace)

    # ----------------------------------------
    # Step 2 — Assemble figure with geological layout
    # ----------------------------------------
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text=f"<b>{well_name}</b> — Formation Column",
            x=0.5, font=dict(color="#c9d1d9", size=15),
        ),
        scene=dict(
            xaxis=dict(
                title="", showticklabels=False,
                showbackground=True, backgroundcolor="#161b22",
                gridcolor="#30363d",
            ),
            yaxis=dict(
                title="", showticklabels=False,
                showbackground=True, backgroundcolor="#0d1117",
                gridcolor="#30363d",
            ),
            zaxis=dict(
                title="Depth (ft)",
                titlefont=dict(color="#8b949e", size=11),
                tickfont=dict(color="#8b949e", size=10),
                autorange="reversed",
                tickvals=_depth_ticks(formations),
                ticktext=[str(abs(v)) for v in _depth_ticks(formations)],
                showbackground=True, backgroundcolor="#161b22",
                gridcolor="#30363d",
            ),
            bgcolor="#0d1117",
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=2),
        ),
        paper_bgcolor="#0d1117",
        font=dict(color="#c9d1d9"),
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        legend=dict(
            title=dict(text="Lithology", font=dict(color="#8b949e", size=11)),
            x=1.02, y=0.5,
            bgcolor="rgba(22,27,34,0.9)",
            bordercolor="#30363d",
            borderwidth=1,
            font=dict(color="#c9d1d9", size=11),
        ),
    )

    return fig


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _formation_box(formation: dict, width_ft: float) -> go.Mesh3d | None:
    """Create a Mesh3d box trace for a single formation.

    Args:
        formation: Dict with name, top_ft, base_ft (None allowed).
        width_ft: Half-width of the block in X and Y (ft).

    Returns:
        go.Mesh3d trace, or None if the formation has zero thickness.
    """
    top  = -formation["top_ft"]
    base = -(formation["base_ft"] if formation["base_ft"] is not None
             else formation["top_ft"] + _DEFAULT_BOTTOM_THICKNESS_FT)

    # ✅ Skip zero-thickness formations
    if top == base:
        return None

    w = width_ft
    color     = get_formation_color(formation["name"])
    lithology = get_formation_lithology(formation["name"])

    # 8 vertices of the box
    x = [-w,  w,  w, -w, -w,  w,  w, -w]
    y = [-w, -w,  w,  w, -w, -w,  w,  w]
    z = [base, base, base, base, top, top, top, top]

    # 12 triangles (6 faces × 2 triangles each)
    i = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    j = [1, 3, 2, 5, 3, 6, 0, 7, 5, 7, 6, 4]
    k = [2, 4, 6, 4, 7, 5, 4, 6, 6, 0, 7, 0]  # noqa: E741

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=0.85,
        flatshading=True,
        name=f"{formation['name']} ({lithology})",
        hovertemplate=(
            f"<b>{formation['name']}</b><br>"
            f"Lithology: {lithology}<br>"
            f"Top: {formation['top_ft']:.0f} ft<br>"
            f"Base: {formation['base_ft']:.0f} ft<br>"
            "<extra></extra>"
            if formation["base_ft"] is not None else
            f"<b>{formation['name']}</b><br>"
            f"Lithology: {lithology}<br>"
            f"Top: {formation['top_ft']:.0f} ft<br>"
            "Base: unknown<br>"
            "<extra></extra>"
        ),
        showlegend=True,
        legendgroup=lithology,
        showscale=False,
    )


def _depth_ticks(formations: list[dict]) -> list[float]:
    """Generate Z-axis tick values from formation tops.

    Args:
        formations: List of formation dicts with top_ft values.

    Returns:
        List of negative depth values for Z-axis ticks.
    """
    tops = sorted({-f["top_ft"] for f in formations})
    # 💾 Keep at most 10 ticks to avoid crowding
    step = max(1, len(tops) // 10)
    return tops[::step]
