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
| Demo data | Kansas Geological Survey LAS (El Dorado field) |

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

### Phase 1 — LAS Loading and Formation Parsing (COMPLETED)
- [x] Explore El Dorado LAS files and document ~Other section format (2026-04-15)
- [x] Implement `loader.py`: read LAS file, return curves as DataFrame + well metadata dict (2026-04-15)
- [x] Implement `formation_parser.py`: extract tops/bases dict from ~Other section (2026-04-15)
- [x] Add El Dorado field LAS files to data/demo/ (2026-04-15)
- [x] Write `test_loader.py` covering: valid file, missing curves, null handling (2026-04-15)
- [x] Write `test_formation_parser.py` covering: standard format, missing tops, empty section (2026-04-15)
- [x] Implement `lithology_map.py`: formation→lithology (KGS Bulletin 189) + lithology→color (USGS TM 11-B1) (2026-04-15)
- [x] Write `test_lithology_map.py`: exact match, fallback, hex format, palette completeness (2026-04-15)

### Phase 2 — Single Well 3D Render (COMPLETED)
- [x] Implement `single_well.py`: build Plotly 3D figure from one well's formations colored by lithology (2026-04-15)
- [x] Validate render with a real El Dorado LAS file in a debug script (2026-04-15)

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
- [x] Write `requirements.txt` with pinned versions (2026-04-15)
- [x] Write `docker-compose.yml` for local run (2026-04-15)
- [x] Write `docs/01_architecture.md` with Mermaid flow diagram (2026-04-15)
- [ ] Push to GitHub and validate README renders correctly
- [ ] Deploy to Hugging Face Spaces (manual step)

## Conventions

- File prefix: `sNN_` for sequential pipeline scripts only; clean names for importable modules
- Docstrings: Google Style, English, all public functions in src/
- Null value in LAS: -999.25 (replace with NaN on load)
- Formation depths: always in feet (LAS Kansas convention)
- Tests committed to git; debug/ always gitignored
