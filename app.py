"""
Reservoir Visualizer — Streamlit entry point.

Wires sidebar selections to 3D render and viewer display.
Session state key: wells_data (list[dict])
"""

import streamlit as st

from src.ui.sidebar import render_sidebar
from src.ui.viewer import render_viewer


def main() -> None:
    st.set_page_config(
        page_title="Reservoir Visualizer",
        page_icon="🛢️",
        layout="wide",
    )

    # ----------------------------------------
    # Step 1 — Session state initialisation
    # ----------------------------------------
    if "wells_data" not in st.session_state:
        st.session_state.wells_data = []

    # ----------------------------------------
    # Step 2 — Sidebar (returns user selections)
    # ----------------------------------------
    selections = render_sidebar(st.session_state.wells_data)
    wells_data = st.session_state.wells_data

    # ----------------------------------------
    # Step 3 — Empty state: nothing loaded yet
    # ----------------------------------------
    if not wells_data:
        st.title("🛢️ Reservoir Visualizer")
        st.markdown(
            "Upload LAS files or load the **El Dorado** demo dataset "
            "from the sidebar to begin."
        )
        return

    # ----------------------------------------
    # Step 4 — Build figure based on view mode
    # ----------------------------------------
    view_mode = selections["view_mode"]
    selected_formations = selections["selected_formations"]

    if view_mode == "single":
        from src.render.single_well import build_single_well_figure
        import yaml

        with open("data/config.yaml") as fh:
            cfg = yaml.safe_load(fh)

        idx = selections["selected_well_idx"]
        well = wells_data[idx]
        well_name = well["meta"].get("well_name", f"Well {idx}")

        formations = well["formations"]
        if selected_formations:
            formations = [f for f in formations if f["name"] in selected_formations]

        fig = build_single_well_figure(
            formations=formations,
            well_name=str(well_name),
            width_ft=cfg["render"]["single_well_width_ft"],
        )

    else:  # multi
        from src.render.multi_well import build_multi_well_figure

        try:
            fig = build_multi_well_figure(
                wells_data=wells_data,
                formation_names=selected_formations,
            )
        except ValueError as exc:
            st.error(str(exc))
            return

    # ----------------------------------------
    # Step 5 — Render viewer with metrics
    # ----------------------------------------
    render_viewer(fig, wells_data)


if __name__ == "__main__":
    main()
