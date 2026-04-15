# reservoir-visualizer

## Goal
Build an interactive 3D reservoir visualizer that loads LAS files, extracts formation tops/bases,
and renders formation layers colored by petrophysical property inside a Streamlit dashboard.

## Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| 3D Rendering | Plotly 3D |
| LAS I/O | lasio |
| Formation parsing | Custom parser on `~Other` section |
| Interpolation | scipy.interpolate (IDW / linear) |
| Language | Python 3.10+ |
| Demo data | Kansas Geological Survey LAS (Arroyo field) |

## Structure

```
reservoir-visualizer/
├── app.py                    ← Streamlit entry point
├── src/
│   ├── las/
│   │   ├── loader.py         ← LAS reading and curve extraction
│   │   └── formation_parser.py ← Tops/bases from ~Other section
│   ├── render/
│   │   ├── single_well.py    ← 3D figure for 1 well
│   │   └── multi_well.py     ← Surface interpolation + N wells
│   └── ui/
│       ├── sidebar.py        ← Upload, well and property selectors
│       └── viewer.py         ← 3D plot Streamlit component
├── data/demo/                ← Kansas LAS files (Arroyo field)
├── data/config.yaml          ← App settings
├── tests/                    ← Committed to git
├── debug/                    ← gitignored
├── todo/                     ← Plans and session logs
└── docs/                     ← Technical docs (bridge to Obsidian)
```

## Phases

### Phase 1 — LAS Loading and Formation Parsing
- [ ] Explore Arroyo LAS files and document available curves and ~Other section format (src/las/)
- [ ] Implement `loader.py`: read LAS file, return curves as DataFrame + well metadata dict (src/las/loader.py)
- [ ] Implement `formation_parser.py`: extract tops/bases dict from ~Other section (src/las/formation_parser.py)
- [ ] Copy 3 representative Arroyo LAS files to data/demo/ (data/demo/)
- [ ] Write `test_loader.py` covering: valid file, missing curves, null handling (tests/test_loader.py)
- [ ] Write `test_formation_parser.py` covering: standard format, missing tops, empty section (tests/test_formation_parser.py)

### Phase 2 — Single Well 3D Render
- [ ] Define formation color scheme and property-to-color mapping (src/render/single_well.py)
- [ ] Implement `single_well.py`: build Plotly 3D figure from one well's formations (src/render/single_well.py)
- [ ] Validate render with a real Arroyo LAS file in a debug script (debug/dbg_single_well_render.py)

### Phase 3 — Multi-Well Interpolation and Render
- [ ] Implement `multi_well.py`: load N wells, interpolate formation surfaces, build combined 3D figure (src/render/multi_well.py)
- [ ] Validate interpolation with 3 Arroyo wells in debug script (debug/dbg_multi_well_render.py)

### Phase 4 — Streamlit UI Assembly
- [ ] Implement `sidebar.py`: file uploader, well selector, property selector (src/ui/sidebar.py)
- [ ] Implement `viewer.py`: wraps Plotly figure in st.plotly_chart with camera controls (src/ui/viewer.py)
- [ ] Implement `app.py`: wire sidebar + viewer, manage session state (app.py)
- [ ] Create `data/config.yaml` with colormaps, default property, Ollama model placeholder (data/config.yaml)
- [ ] Smoke test full flow: upload LAS → select formation → render 3D (manual)

### Phase 5 — Polish and Deploy
- [ ] Write `requirements.txt` with pinned versions (requirements.txt)
- [ ] Write `docker-compose.yml` for local run (docker-compose.yml)
- [ ] Write `docs/01_architecture.md` with Mermaid flow diagram (docs/01_architecture.md)
- [ ] Push to GitHub and validate README renders correctly
- [ ] Deploy to Hugging Face Spaces (manual step)

## Conventions

- File prefix: `sNN_` for sequential pipeline scripts only; clean names for importable modules
- Docstrings: Google Style, English, all public functions in src/
- Null value in LAS: -999.25 (replace with NaN on load)
- Formation depths: always in feet (LAS Kansas convention)
- Tests committed to git; debug/ always gitignored
