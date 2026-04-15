# reservoir-visualizer

3D reservoir visualizer with local LLM copilot.
Loads LAS files, renders formation layers in 3D colored by petrophysical property,
and provides a conversational interface powered by Ollama (qwen3:14b) with function calling.

## Project identity

- **Portfolio**: OilCoder — public, English code and docs
- **Goal**: Close three portfolio gaps simultaneously: modern LLMs, serious 3D visualization, function calling with structured data
- **Demo data**: Kansas Geological Survey LAS files (public domain)
- **Deployment**: `docker compose up` locally + Hugging Face Spaces

## Rules (always active)

| Rule | Purpose |
|---|---|
| `code-style.md` | English comments, snake_case, step/substep structure, 40-line limit |
| `file-naming.md` | `sNN_` prefix pattern, English names |
| `code-change.md` | Minimal edits, read before modify, no silent refactors |
| `logging-policy.md` | tqdm for batch, st.progress for UI, English messages |
| `doc-enforcement.md` | Google Style docstrings, scope = src/ |
| `docs-style.md` | docs/ folder, English, Mermaid diagrams for flows |
| `plan-format.md` | todo/PLAN.md format, flat checkboxes, mark [x] with date |
| `project-guidelines.md` | Mode = warn, full index and constraints |

## Skills (on demand)

| Skill | Trigger |
|---|---|
| `/bitacora` | After commits or "log the session" |
| `/plan-writing` | "write the plan", "update the plan", "what's left" |
| `/phase-executor` | "execute phase N", "work on phase N" |
| `/test` | "test this", "create tests for X" |
| `/debug` | "debug this", "investigate this error" |
| `/document` | "document this file", "generate docs for X" |
| `/doc-enforce` | "review docstrings", "enforce docs on this file" |

## Conventions

- **Code language**: English (comments, docstrings, variable names, log messages)
- **Prose language**: Spanish (plans, session logs, bitacoras)
- **File prefix**: `sNN_` pattern (`s01_load_las.py`, `s02_parse_formations.py`, `s99_run_pipeline.py`)
- **Working folder**: `todo/` for PLAN.md and bitacoras
- **Testing**: `tests/` — committed to git
- **Debug**: `debug/` — always gitignored
- **Docs**: `docs/` — WSL↔Windows bridge to Obsidian vault
- **Docstrings**: Google Style

## Validation mode

**Current: `warn`** — Active development. Violations are flagged but not blocking.

## Project phases

- **Phase 1**: 3D visualizer (LAS → formations → Plotly/PyVista render in Streamlit)
- **Phase 2**: Ollama chat (qwen3:14b + basic context injection)
- **Phase 3**: Function calling (tools: get_formation_properties, compare_formations, find_best_zone)

## Tech constraints

- WSL2 (Ubuntu) — no direct file bridge to Windows
- RTX 4080 — Ollama inference on GPU
- Ollama local — qwen3:14b (confirmed working)
- Streamlit — UI framework
- Python 3.10+, snake_case everywhere
- Kansas LAS data at `/home/pokinux/Kansas/data/v3.0_las_files/`
- Kansas preprocessing code at `/home/pokinux/Kansas/code/src/data_preprocessing/`

## Key policy

**Fail fast on data**: invalid or incomplete LAS files must raise immediately with a clear
error message. No silent degradation, no partial renders with bad data.
