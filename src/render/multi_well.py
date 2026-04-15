"""
3D multi-well formation renderer for reservoir-visualizer.

Interpolates formation top surfaces across N wells using
scipy.interpolate.griddata and renders them as Plotly go.Surface traces.
Well positions are shown as vertical sticks (go.Scatter3d).

Coordinate system:
  - Lat/lon → XY in metres via equirectangular projection centred on the
    mean well location. Valid for small fields (< 50 km across).
  - Z = -depth_ft (negative): surface at Z=0, deeper = more negative.

Public functions: build_multi_well_figure
"""

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

from src.las.lithology_map import get_formation_color, get_formation_lithology

_GRID_N            = 40     # interpolation grid resolution (n×n)
_GRID_MARGIN       = 0.15   # fractional margin around well bounding box
_MIN_WELLS_INTERP  = 2      # minimum wells to attempt interpolation
_STICK_COLOR       = "#333333"
_LAT_M_PER_DEG     = 111_320.0   # metres per degree latitude


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_multi_well_figure(
    wells_data: list[dict],
    formation_names: list[str] | None = None,
) -> go.Figure:
    """Build a Plotly 3D figure with interpolated formation surfaces for N wells.

    Args:
        wells_data: List of dicts, one per well. Each dict must have:
            - "meta": dict from loader.load_las() — needs lat, lon, well_name,
              depth_start_ft, depth_stop_ft.
            - "formations": list[dict] from formation_parser.parse_formations().
        formation_names: Formation names to render. None renders all formations
            present in at least two wells.

    Returns:
        plotly.graph_objects.Figure with go.Surface traces per formation and
        go.Scatter3d traces for well sticks.

    Raises:
        ValueError: If fewer than 2 wells with valid coordinates are provided.
    """
    # ----------------------------------------
    # Step 1 — Validate and extract well positions
    # ----------------------------------------
    wells = _validated_wells(wells_data)
    if len(wells) < _MIN_WELLS_INTERP:
        raise ValueError(
            f"At least {_MIN_WELLS_INTERP} wells with valid lat/lon required "
            f"for multi-well render. Got {len(wells)}."
        )

    xs, ys = _latlon_to_xy(
        [w["meta"]["lat"]  for w in wells],
        [w["meta"]["lon"]  for w in wells],
    )

    # ----------------------------------------
    # Step 2 — Find formations to render
    # ----------------------------------------
    target_names = formation_names or _common_formations(wells, min_count=2)
    if not target_names:
        raise ValueError("No formations found in 2 or more wells.")

    # ----------------------------------------
    # Step 3 — Build surface trace per formation
    # ----------------------------------------
    traces: list[go.BaseTraceType] = []

    grid_x, grid_y = _make_grid(xs, ys)

    for fname in target_names:
        surface = _build_surface_trace(fname, wells, xs, ys, grid_x, grid_y)
        if surface is not None:
            traces.append(surface)

    # ----------------------------------------
    # Step 4 — Add well sticks
    # ----------------------------------------
    for i, well in enumerate(wells):
        traces.append(_well_stick_trace(
            x=xs[i], y=ys[i],
            z_top=-(well["meta"].get("depth_start_ft") or 0),
            z_bottom=-(well["meta"].get("depth_stop_ft") or 5000),
            well_name=str(well["meta"].get("well_name", f"Well {i+1}")),
        ))

    # ----------------------------------------
    # Step 5 — Assemble figure
    # ----------------------------------------
    z_min = -max(w["meta"].get("depth_stop_ft") or 5000 for w in wells)
    z_max = -min(w["meta"].get("depth_start_ft") or 0 for w in wells)

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text=f"<b>El Dorado Field</b> — {len(wells)} wells, "
                 f"{len(target_names)} formations",
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(title="X (m)", showbackground=False),
            yaxis=dict(title="Y (m)", showbackground=False),
            zaxis=dict(
                title="Depth (ft)",
                range=[z_min, z_max],
                autorange="reversed",
                tickvals=np.linspace(z_min, z_max, 6).tolist(),
                ticktext=[str(int(abs(v))) for v in np.linspace(z_min, z_max, 6)],
            ),
            bgcolor="white",
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.9)),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=1.5),
        ),
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        legend=dict(title=dict(text="Formation / Well"), x=1.02, y=0.5),
    )

    return fig


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _validated_wells(wells_data: list[dict]) -> list[dict]:
    """Return only wells that have valid lat, lon, and at least one formation.

    Args:
        wells_data: Raw input list from the caller.

    Returns:
        Filtered list of well dicts with valid coordinates and formations.
    """
    valid = []
    for w in wells_data:
        meta = w.get("meta", {})
        lat  = meta.get("lat")
        lon  = meta.get("lon")
        fmts = w.get("formations", [])
        if lat and lon and fmts:
            valid.append(w)
    return valid


def _latlon_to_xy(lats: list[float], lons: list[float]) -> tuple[np.ndarray, np.ndarray]:
    """Convert lat/lon lists to XY metres via equirectangular projection.

    The origin is the centroid of all well locations.

    Args:
        lats: Latitude values (decimal degrees, NAD27 or WGS84).
        lons: Longitude values (decimal degrees).

    Returns:
        Tuple of (x_metres, y_metres) numpy arrays.
    """
    lat_arr = np.array(lats, dtype=float)
    lon_arr = np.array(lons, dtype=float)

    lat_ref = lat_arr.mean()
    lon_ref = lon_arr.mean()

    x = (lon_arr - lon_ref) * np.cos(np.radians(lat_ref)) * _LAT_M_PER_DEG
    y = (lat_arr - lat_ref) * _LAT_M_PER_DEG

    return x, y


def _common_formations(wells: list[dict], min_count: int = 2) -> list[str]:
    """Return formation names present in at least min_count wells.

    Args:
        wells: Validated wells list.
        min_count: Minimum number of wells a formation must appear in.

    Returns:
        List of formation names sorted by mean top depth ascending.
    """
    from collections import Counter, defaultdict

    counts: Counter = Counter()
    depths: defaultdict = defaultdict(list)

    for well in wells:
        seen = set()
        for fmt in well["formations"]:
            name = fmt["name"]
            if name not in seen:
                counts[name] += 1
                depths[name].append(fmt["top_ft"])
                seen.add(name)

    common = [n for n, c in counts.items() if c >= min_count]
    return sorted(common, key=lambda n: np.mean(depths[n]))


def _make_grid(
    xs: np.ndarray,
    ys: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Build a regular XY grid covering the well bounding box with margin.

    Args:
        xs: Well X coordinates in metres.
        ys: Well Y coordinates in metres.

    Returns:
        Tuple of (grid_x, grid_y) 2D numpy arrays (shape _GRID_N × _GRID_N).
    """
    x_span = max(xs.max() - xs.min(), 1.0)
    y_span = max(ys.max() - ys.min(), 1.0)
    margin_x = x_span * _GRID_MARGIN
    margin_y = y_span * _GRID_MARGIN

    gx = np.linspace(xs.min() - margin_x, xs.max() + margin_x, _GRID_N)
    gy = np.linspace(ys.min() - margin_y, ys.max() + margin_y, _GRID_N)

    return np.meshgrid(gx, gy)


def _build_surface_trace(
    fname: str,
    wells: list[dict],
    xs: np.ndarray,
    ys: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
) -> go.Surface | None:
    """Interpolate and build a go.Surface trace for one formation.

    Args:
        fname: Formation name to render.
        wells: Validated wells list.
        xs: Well X coordinates.
        ys: Well Y coordinates.
        grid_x: Meshgrid X (shape _GRID_N × _GRID_N).
        grid_y: Meshgrid Y (shape _GRID_N × _GRID_N).

    Returns:
        go.Surface trace, or None if fewer than 2 data points exist.
    """
    # ✅ Collect (x, y, top_ft) for wells that have this formation
    pts_x, pts_y, pts_z = [], [], []
    for i, well in enumerate(wells):
        for fmt in well["formations"]:
            if fmt["name"] == fname:
                pts_x.append(xs[i])
                pts_y.append(ys[i])
                pts_z.append(-fmt["top_ft"])   # negative depth
                break

    if len(pts_x) < 2:
        return None

    points  = np.column_stack([pts_x, pts_y])
    values  = np.array(pts_z)
    method  = "linear" if len(pts_x) >= 3 else "nearest"

    # 🔄 Interpolate onto regular grid
    grid_z = griddata(points, values, (grid_x, grid_y), method=method)

    # 💾 Fill NaN outside convex hull with nearest-neighbour values
    if np.isnan(grid_z).any():
        grid_z_nn = griddata(points, values, (grid_x, grid_y), method="nearest")
        grid_z = np.where(np.isnan(grid_z), grid_z_nn, grid_z)

    color    = get_formation_color(fname)
    lithology = get_formation_lithology(fname)
    mean_top = int(abs(values.mean()))

    return go.Surface(
        x=grid_x, y=grid_y, z=grid_z,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        opacity=0.80,
        name=f"{fname} ({lithology}, ~{mean_top} ft)",
        hovertemplate=(
            f"<b>{fname}</b><br>"
            f"Lithology: {lithology}<br>"
            "Top: %{z:.0f} ft<br>"
            "<extra></extra>"
        ),
        contours=dict(z=dict(show=False)),
        showlegend=True,
        legendgroup=fname,
    )


def _well_stick_trace(
    x: float,
    y: float,
    z_top: float,
    z_bottom: float,
    well_name: str,
) -> go.Scatter3d:
    """Build a vertical line trace representing a well stick.

    Args:
        x: Well X position in metres.
        y: Well Y position in metres.
        z_top: Top of the stick (negative depth).
        z_bottom: Bottom of the stick (negative depth, more negative).
        well_name: Label shown on hover and legend.

    Returns:
        go.Scatter3d trace (vertical line + surface marker).
    """
    return go.Scatter3d(
        x=[x, x],
        y=[y, y],
        z=[z_top, z_bottom],
        mode="lines+text",
        line=dict(color=_STICK_COLOR, width=4),
        text=[well_name, ""],
        textposition="top center",
        name=well_name,
        hovertemplate=f"<b>{well_name}</b><br>X: {x:.0f} m<br>Y: {y:.0f} m<extra></extra>",
        showlegend=True,
    )
