"""
Sidebar UI component for reservoir-visualizer.

Renders the Streamlit sidebar with file upload, demo data loader,
view mode selector, well selector, and formation filter.
Reads and writes st.session_state directly.

Public functions: render_sidebar
"""

from pathlib import Path

import streamlit as st
import yaml

with open("data/config.yaml") as _fh:
    _cfg = yaml.safe_load(_fh)

_DEMO_DIR   = Path("data/demo") / _cfg["app"]["demo_field"]
_DEMO_LABEL = _cfg["app"]["demo_field"]


def render_sidebar(wells_data: list[dict]) -> dict:
    """Render the sidebar and return the current user selections.

    Args:
        wells_data: Currently loaded wells (may be empty list).

    Returns:
        Dict with keys:
            - view_mode (str): "single" or "multi"
            - selected_well_idx (int): index into wells_data for single mode
            - selected_formations (list[str] | None): None means show all
    """
    with st.sidebar:
        st.title("🛢️ Reservoir Visualizer")
        st.divider()

        # ----------------------------------------
        # Step 1 — Data source
        # ----------------------------------------
        _render_data_source()

        if not wells_data:
            st.info("Upload LAS files or load the demo dataset to begin.")
            return {"view_mode": "single", "selected_well_idx": 0,
                    "selected_formations": None}

        st.divider()

        # ----------------------------------------
        # Step 2 — View mode
        # ----------------------------------------
        view_mode = st.radio(
            "View mode",
            options=["single", "multi"],
            format_func=lambda x: "Single well" if x == "single" else "Multi-well field",
            horizontal=True,
        )

        # ----------------------------------------
        # Step 3 — Well selector (single mode only)
        # ----------------------------------------
        selected_well_idx = 0
        if view_mode == "single" and len(wells_data) > 1:
            well_names = [
                f"{w['meta'].get('well_name', f'Well {i}')} "
                f"({w['meta'].get('field', '')})"
                for i, w in enumerate(wells_data)
            ]
            selected_well_idx = st.selectbox(
                "Select well", range(len(wells_data)),
                format_func=lambda i: well_names[i],
            )

        # ----------------------------------------
        # Step 4 — Formation filter
        # ----------------------------------------
        selected_formations = _render_formation_filter(wells_data, view_mode)

        st.divider()
        _render_well_summary(wells_data)

    return {
        "view_mode": view_mode,
        "selected_well_idx": selected_well_idx,
        "selected_formations": selected_formations or None,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _render_data_source() -> None:
    """Render file uploader and demo data button, updating session state."""
    uploaded = st.file_uploader(
        "Upload LAS files",
        type=["las"],
        accept_multiple_files=True,
        help="LAS 2.0 format. Multiple files for multi-well view.",
    )

    if uploaded:
        from src.las.loader import load_las
        from src.las.formation_parser import parse_formations
        import tempfile

        wells = []
        for f in uploaded:
            try:
                with tempfile.NamedTemporaryFile(suffix=".las", delete=False) as tmp:
                    tmp.write(f.getvalue())
                    tmp_path = tmp.name
                curves, meta = load_las(tmp_path)
                formations = parse_formations(meta["raw_other"])
                wells.append({"meta": meta, "formations": formations, "curves": curves})
                Path(tmp_path).unlink(missing_ok=True)
            except Exception as exc:
                st.error(f"Could not load {f.name}: {exc}")

        if wells:
            st.session_state.wells_data = wells

    if st.button(f"Load {_DEMO_LABEL} demo", use_container_width=True):
        with st.spinner("Loading demo wells…"):
            st.session_state.wells_data = _load_demo_wells()


@st.cache_data
def _load_demo_wells() -> list[dict]:
    """Load El Dorado demo wells (cached).

    Returns:
        List of well dicts with meta, formations, and curves.
    """
    from src.las.loader import load_las
    from src.las.formation_parser import parse_formations
    import yaml

    with open("data/config.yaml") as fh:
        cfg = yaml.safe_load(fh)
    max_wells = cfg["app"]["max_demo_wells"]

    wells = []
    for las_path in sorted(_DEMO_DIR.glob("*.las"))[:max_wells]:
        try:
            curves, meta = load_las(las_path)
            formations = parse_formations(meta["raw_other"])
            if meta.get("lat") and meta.get("lon") and formations:
                wells.append({"meta": meta, "formations": formations, "curves": curves})
        except Exception:
            continue

    return wells


def _render_formation_filter(
    wells_data: list[dict],
    view_mode: str,
) -> list[str]:
    """Render formation multiselect and return selected names.

    Args:
        wells_data: Currently loaded wells.
        view_mode: "single" or "multi".

    Returns:
        List of selected formation names (empty list = all formations).
    """
    from src.render.multi_well import _common_formations

    if view_mode == "multi":
        available = _common_formations(wells_data, min_count=2)
    else:
        available = [f["name"] for f in wells_data[0]["formations"]]

    if not available:
        return []

    selected = st.multiselect(
        "Formations to display",
        options=available,
        default=available,
        help="Select which formations to render in the 3D view.",
    )
    return selected


def _render_well_summary(wells_data: list[dict]) -> None:
    """Render compact well count and field info in the sidebar.

    Args:
        wells_data: Currently loaded wells.
    """
    fields = {w["meta"].get("field", "Unknown") for w in wells_data}
    st.caption(
        f"**{len(wells_data)} well{'s' if len(wells_data) != 1 else ''}** loaded  \n"
        f"Field{'s' if len(fields) > 1 else ''}: {', '.join(sorted(fields))}"
    )
