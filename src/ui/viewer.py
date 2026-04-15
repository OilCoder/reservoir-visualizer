"""
3D viewer UI component for reservoir-visualizer.

Wraps a Plotly figure inside a Streamlit layout with metrics
and renders it with st.plotly_chart.

Public functions: render_viewer
"""

import plotly.graph_objects as go
import streamlit as st
import yaml


def render_viewer(fig: go.Figure, wells_data: list[dict]) -> None:
    """Render the 3D figure with well and formation metrics above it.

    Args:
        fig: Plotly Figure built by single_well or multi_well renderer.
        wells_data: Currently loaded wells (used for metrics display).
    """
    # ----------------------------------------
    # Step 1 — Metrics row
    # ----------------------------------------
    n_wells = len(wells_data)
    n_formations = len({
        f["name"]
        for w in wells_data
        for f in w["formations"]
    })
    n_surfaces = sum(1 for t in fig.data if type(t).__name__ == "Surface")
    depths = [
        w["meta"].get("depth_stop_ft") or 0
        for w in wells_data
        if w["meta"].get("depth_stop_ft")
    ]
    max_depth = int(max(depths)) if depths else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Wells",         n_wells)
    col2.metric("Formations",    n_formations)
    col3.metric("3D surfaces",   n_surfaces)
    col4.metric("Max depth (ft)", f"{max_depth:,}")

    # ----------------------------------------
    # Step 2 — 3D figure
    # ----------------------------------------
    with open("data/config.yaml") as fh:
        cfg = yaml.safe_load(fh)
    height = cfg["render"]["figure_height_px"]

    st.plotly_chart(fig, use_container_width=True, height=height)
