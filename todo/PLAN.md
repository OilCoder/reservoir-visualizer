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

### Phase 3 — Multi-Well Interpolation and Render (COMPLETED)
- [x] Implement `multi_well.py`: load N wells, interpolate formation surfaces, build combined 3D figure (2026-04-15)
- [x] Validate interpolation with 4 El Dorado wells in debug script (2026-04-15)

### Phase 4 — Streamlit UI Assembly (COMPLETED)
- [x] Implement `sidebar.py`: file uploader, well selector, property selector (src/ui/sidebar.py) (2026-04-15)
- [x] Implement `viewer.py`: wraps Plotly figure in st.plotly_chart with metrics row (src/ui/viewer.py) (2026-04-15)
- [x] Implement `app.py`: wire sidebar + viewer, manage session state (app.py) (2026-04-15)
- [x] Create `data/config.yaml` with render settings and demo config (data/config.yaml) (2026-04-15)
- [x] Smoke test full flow: app boots, responds on :8501, demo data path confirmed (2026-04-15)

### Phase 4b — 3D Render Quality Improvements (COMPLETED)
- [x] Replace go.Surface with go.Mesh3d volumetric bodies (top + base + side walls) (2026-04-15)
- [x] Add elevation offset (elev_ft) to well sticks and formation Z coordinates (2026-04-15)
- [x] Focus Z axis on formation interval instead of full well depth (2026-04-15)
- [x] Apply dark theme (.streamlit/config.toml) matching petroleum industry tools (2026-04-15)
- [x] Fix "3D surfaces" metric to count Mesh3d traces (src/ui/viewer.py) (2026-04-15)
- [x] Switch demo field from El Dorado (18 valid wells, 40%) to Schaben (140 valid, 97%) (2026-04-15)
- [x] Make demo_field configurable via data/config.yaml (src/ui/sidebar.py) (2026-04-15)
- [x] Extend lithology_map.py with Schaben and Permian evaporite formations (2026-04-15)
- [x] Fix collinear-points crash in griddata with try/except fallback to nearest (2026-04-15)
- [x] Increase well stick width for visibility (src/render/multi_well.py) (2026-04-15)

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
