"""
3D multi-well formation renderer for reservoir-visualizer.

Interpolates formation surfaces across N wells and renders each formation
as a closed volumetric Mesh3d (top face + base face + side walls).
Well positions are shown as vertical sticks (go.Scatter3d).

Coordinate system:
  - Lat/lon → XY in metres via equirectangular projection centred on the
    mean well location. Valid for small fields (< 50 km across).
  - Z = elev_ft - depth_ft  (feet above/below sea level).
    Ground surface at Z = elev_ft; deeper values decrease Z.

Public functions: build_multi_well_figure
"""

import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

from src.las.lithology_map import get_formation_color, get_formation_lithology

_GRID_N                    = 20     # grid resolution per layer (n×n)
_GRID_MARGIN               = 0.15   # fractional margin around well bounding box
_MIN_WELLS_INTERP          = 2      # minimum wells to attempt interpolation
_DEFAULT_BASE_THICKNESS_FT = 50.0   # fallback thickness when base_ft is None
_STICK_COLOR               = "#ffffff"
_LAT_M_PER_DEG             = 111_320.0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_multi_well_figure(
    wells_data: list[dict],
    formation_names: list[str] | None = None,
) -> go.Figure:
    """Build a Plotly 3D figure with volumetric formation bodies for N wells.

    Each formation is rendered as a closed go.Mesh3d solid (top + base faces
    + perimeter side walls). Well positions are shown as vertical Scatter3d
    sticks anchored at ground elevation.

    Args:
        wells_data: List of dicts, one per well. Each dict must have:
            - "meta": dict from loader.load_las() — needs lat, lon, well_name,
              depth_stop_ft, and optionally elev_ft.
            - "formations": list[dict] from formation_parser.parse_formations().
        formation_names: Formation names to render. None renders all formations
            present in at least two wells.

    Returns:
        plotly.graph_objects.Figure with go.Mesh3d traces per formation and
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
        [w["meta"]["lat"] for w in wells],
        [w["meta"]["lon"] for w in wells],
    )
    elevs = np.array(
        [w["meta"].get("elev_ft") or 0.0 for w in wells], dtype=float
    )

    # ----------------------------------------
    # Step 2 — Find formations to render
    # ----------------------------------------
    target_names = formation_names or _common_formations(wells, min_count=2)
    if not target_names:
        raise ValueError("No formations found in 2 or more wells.")

    # ----------------------------------------
    # Step 3 — Build volumetric Mesh3d per formation
    # ----------------------------------------
    traces: list[go.BaseTraceType] = []
    grid_x, grid_y = _make_grid(xs, ys)
    mesh_i, mesh_j, mesh_k = _volume_mesh_indices(_GRID_N)

    for fname in target_names:
        vol = _build_formation_volume(
            fname, wells, xs, ys, elevs, grid_x, grid_y, mesh_i, mesh_j, mesh_k
        )
        if vol is not None:
            traces.append(vol)

    # ----------------------------------------
    # Step 4 — Add well sticks anchored at ground elevation
    # ----------------------------------------
    for i, well in enumerate(wells):
        traces.append(_well_stick_trace(
            x=xs[i],
            y=ys[i],
            z_top=float(elevs[i]),
            z_bottom=float(elevs[i]) - (well["meta"].get("depth_stop_ft") or 5000),
            well_name=str(well["meta"].get("well_name", f"Well {i + 1}")),
        ))

    # ----------------------------------------
    # Step 5 — Z range focused on formation interval
    # ----------------------------------------
    form_z: list[float] = []
    for i, well in enumerate(wells):
        for fmt in well["formations"]:
            if fmt["name"] in target_names:
                form_z.append(float(elevs[i]) - fmt["top_ft"])
                if fmt["base_ft"] is not None:
                    form_z.append(float(elevs[i]) - fmt["base_ft"])

    if form_z:
        z_data_min, z_data_max = min(form_z), max(form_z)
    else:
        z_data_min = float(min(elevs[i] - (wells[i]["meta"].get("depth_stop_ft") or 5000)
                               for i in range(len(wells))))
        z_data_max = float(max(elevs)) if elevs.any() else 0.0

    margin = (z_data_max - z_data_min) * 0.12
    z_min, z_max = z_data_min - margin, z_data_max + margin

    # ----------------------------------------
    # Step 6 — Assemble figure
    # ----------------------------------------
    field = wells[0]["meta"].get("field", "Field")
    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text=f"<b>{field}</b> — {len(wells)} wells · {len(target_names)} formations",
            x=0.5,
            font=dict(size=15),
        ),
        scene=dict(
            xaxis=dict(
                title="", showticklabels=False,
                showbackground=True, backgroundcolor="#161b22",
                gridcolor="#30363d", zerolinecolor="#30363d",
            ),
            yaxis=dict(
                title="", showticklabels=False,
                showbackground=True, backgroundcolor="#0d1117",
                gridcolor="#30363d", zerolinecolor="#30363d",
            ),
            zaxis=dict(
                title="Elevation (ft)",
                titlefont=dict(color="#8b949e", size=11),
                tickfont=dict(color="#8b949e", size=10),
                range=[z_min, z_max],
                tickvals=np.linspace(z_min, z_max, 6).tolist(),
                ticktext=[str(int(v)) for v in np.linspace(z_min, z_max, 6)],
                showbackground=True, backgroundcolor="#161b22",
                gridcolor="#30363d", zerolinecolor="#30363d",
            ),
            bgcolor="#0d1117",
            camera=dict(
                eye=dict(x=1.8, y=0.8, z=0.5),
                up=dict(x=0, y=0, z=1),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=2.5),
        ),
        paper_bgcolor="#0d1117",
        plot_bgcolor="#0d1117",
        font=dict(color="#c9d1d9"),
        margin=dict(l=0, r=0, t=45, b=0),
        showlegend=True,
        legend=dict(
            title=dict(text="Formation", font=dict(color="#8b949e", size=11)),
            x=1.01, y=0.5,
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

def _validated_wells(wells_data: list[dict]) -> list[dict]:
    """Return only wells that have valid lat, lon, and at least one formation.

    Args:
        wells_data: Raw input list from the caller.

    Returns:
        Filtered list of well dicts with valid coordinates and formations.
    """
    return [
        w for w in wells_data
        if w.get("meta", {}).get("lat")
        and w.get("meta", {}).get("lon")
        and w.get("formations")
    ]


def _latlon_to_xy(lats: list[float], lons: list[float]) -> tuple[np.ndarray, np.ndarray]:
    """Convert lat/lon lists to XY metres via equirectangular projection.

    The origin is the centroid of all well locations.

    Args:
        lats: Latitude values (decimal degrees).
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
        seen: set[str] = set()
        for fmt in well["formations"]:
            name = fmt["name"]
            if name not in seen:
                counts[name] += 1
                depths[name].append(fmt["top_ft"])
                seen.add(name)

    common = [n for n, c in counts.items() if c >= min_count]
    return sorted(common, key=lambda n: np.mean(depths[n]))


def _make_grid(xs: np.ndarray, ys: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Build a regular XY grid covering the well bounding box with margin.

    Args:
        xs: Well X coordinates in metres.
        ys: Well Y coordinates in metres.

    Returns:
        Tuple of (grid_x, grid_y) 2D numpy arrays (shape _GRID_N × _GRID_N).
    """
    x_span = max(xs.max() - xs.min(), 1.0)
    y_span = max(ys.max() - ys.min(), 1.0)
    gx = np.linspace(xs.min() - x_span * _GRID_MARGIN,
                     xs.max() + x_span * _GRID_MARGIN, _GRID_N)
    gy = np.linspace(ys.min() - y_span * _GRID_MARGIN,
                     ys.max() + y_span * _GRID_MARGIN, _GRID_N)
    return np.meshgrid(gx, gy)


def _volume_mesh_indices(N: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pre-compute triangle face indices for a closed top+base volumetric slab.

    Vertex layout (row-major):
      - Top layer  : indices 0 … N²-1
      - Base layer : indices N² … 2N²-1

    Args:
        N: Grid edge size (produces an N×N grid per layer).

    Returns:
        Tuple of (i, j, k) integer numpy arrays for go.Mesh3d.
    """
    M = N * N
    ii: list[int] = []
    jj: list[int] = []
    kk: list[int] = []

    def t(r: int, c: int) -> int:  # top layer index
        return r * N + c

    def b(r: int, c: int) -> int:  # base layer index
        return M + r * N + c

    # Top face (two triangles per cell, normal pointing up)
    for r in range(N - 1):
        for c in range(N - 1):
            a, bv, cv, d = t(r, c), t(r, c + 1), t(r + 1, c + 1), t(r + 1, c)
            ii += [a, bv]; jj += [bv, cv]; kk += [d,  d]

    # Base face (reversed winding, normal pointing down)
    for r in range(N - 1):
        for c in range(N - 1):
            a, bv, cv, d = b(r, c), b(r, c + 1), b(r + 1, c + 1), b(r + 1, c)
            ii += [a, bv]; jj += [d,  d]; kk += [bv, cv]

    # Front wall (r = 0)
    for c in range(N - 1):
        t0, t1, b0, b1 = t(0, c), t(0, c + 1), b(0, c), b(0, c + 1)
        ii += [t0, t1]; jj += [t1, b1]; kk += [b0, b0]

    # Back wall (r = N-1)
    for c in range(N - 1):
        t0, t1, b0, b1 = t(N - 1, c), t(N - 1, c + 1), b(N - 1, c), b(N - 1, c + 1)
        ii += [t0, b0]; jj += [b0, b1]; kk += [t1, t1]

    # Left wall (c = 0)
    for r in range(N - 1):
        t0, t1, b0, b1 = t(r, 0), t(r + 1, 0), b(r, 0), b(r + 1, 0)
        ii += [t0, b0]; jj += [b0, b1]; kk += [t1, t1]

    # Right wall (c = N-1)
    for r in range(N - 1):
        t0, t1, b0, b1 = t(r, N - 1), t(r + 1, N - 1), b(r, N - 1), b(r + 1, N - 1)
        ii += [t0, t1]; jj += [t1, b1]; kk += [b0, b0]

    return np.array(ii), np.array(jj), np.array(kk)


def _build_formation_volume(
    fname: str,
    wells: list[dict],
    xs: np.ndarray,
    ys: np.ndarray,
    elevs: np.ndarray,
    grid_x: np.ndarray,
    grid_y: np.ndarray,
    mesh_i: np.ndarray,
    mesh_j: np.ndarray,
    mesh_k: np.ndarray,
) -> go.Mesh3d | None:
    """Interpolate and build a closed volumetric Mesh3d for one formation.

    Constructs a solid 3D body from the interpolated top and base surfaces,
    connected by perimeter side walls, for a geologically realistic render.

    Args:
        fname: Formation name to render.
        wells: Validated wells list.
        xs: Well X coordinates in metres.
        ys: Well Y coordinates in metres.
        elevs: Ground elevation in ft for each well (same order as xs/ys).
        grid_x: Meshgrid X (shape _GRID_N × _GRID_N).
        grid_y: Meshgrid Y (shape _GRID_N × _GRID_N).
        mesh_i: Pre-computed triangle i indices from _volume_mesh_indices.
        mesh_j: Pre-computed triangle j indices.
        mesh_k: Pre-computed triangle k indices.

    Returns:
        go.Mesh3d trace, or None if fewer than 2 data points exist.
    """
    # ✅ Collect elevation-adjusted Z for top and base at each well
    pts_x, pts_y, tops_z, bases_z = [], [], [], []
    for i, well in enumerate(wells):
        for fmt in well["formations"]:
            if fmt["name"] == fname:
                top_z  = float(elevs[i]) - fmt["top_ft"]
                base_ft = (
                    fmt["base_ft"] if fmt["base_ft"] is not None
                    else fmt["top_ft"] + _DEFAULT_BASE_THICKNESS_FT
                )
                base_z = float(elevs[i]) - base_ft
                pts_x.append(xs[i])
                pts_y.append(ys[i])
                tops_z.append(top_z)
                bases_z.append(base_z)
                break

    if len(pts_x) < 2:
        return None

    points    = np.column_stack([pts_x, pts_y])
    tops_arr  = np.array(tops_z)
    bases_arr = np.array(bases_z)

    # 🔄 Interpolate top and base; fall back to nearest if linear fails (collinear points)
    def _interp(values: np.ndarray) -> np.ndarray:
        if len(pts_x) >= 3:
            try:
                result = griddata(points, values, (grid_x, grid_y), method="linear")
            except Exception:
                result = griddata(points, values, (grid_x, grid_y), method="nearest")
        else:
            result = griddata(points, values, (grid_x, grid_y), method="nearest")
        # 💾 Fill NaN outside convex hull with nearest-neighbour values
        if np.isnan(result).any():
            nn = griddata(points, values, (grid_x, grid_y), method="nearest")
            result = np.where(np.isnan(result), nn, result)
        return result

    grid_top  = _interp(tops_arr)
    grid_base = _interp(bases_arr)

    # 📐 Build vertex arrays: top layer then base layer (row-major)
    gx_f = grid_x.ravel()
    gy_f = grid_y.ravel()
    x_v  = np.tile(gx_f, 2)
    y_v  = np.tile(gy_f, 2)
    z_v  = np.concatenate([grid_top.ravel(), grid_base.ravel()])

    color    = get_formation_color(fname)
    lithology = get_formation_lithology(fname)

    return go.Mesh3d(
        x=x_v, y=y_v, z=z_v,
        i=mesh_i, j=mesh_j, k=mesh_k,
        color=color,
        opacity=0.92,
        flatshading=False,
        lighting=dict(
            ambient=0.55,
            diffuse=0.9,
            roughness=0.4,
            specular=0.3,
            fresnel=0.2,
        ),
        lightposition=dict(x=500, y=500, z=5000),
        name=f"{fname} ({lithology})",
        hovertemplate=(
            f"<b>{fname}</b><br>"
            f"Lithology: {lithology}<br>"
            "Elev: %{z:.0f} ft<br>"
            "<extra></extra>"
        ),
        showlegend=True,
        legendgroup=fname,
        showscale=False,
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
        z_top: Top of the stick (ground elevation in ft).
        z_bottom: Bottom of the stick (elevation minus total depth, in ft).
        well_name: Label shown on hover and legend.

    Returns:
        go.Scatter3d trace (vertical line + surface marker).
    """
    return go.Scatter3d(
        x=[x, x],
        y=[y, y],
        z=[z_top, z_bottom],
        mode="lines+text",
        line=dict(color=_STICK_COLOR, width=10),
        text=[well_name, ""],
        textposition="top center",
        name=well_name,
        hovertemplate=(
            f"<b>{well_name}</b><br>"
            f"X: {x:.0f} m<br>Y: {y:.0f} m<extra></extra>"
        ),
        showlegend=True,
    )
