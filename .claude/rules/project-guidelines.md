---
description: Project-level index of rules, skills, and enforcement strategy
---

# Project Guidelines — reservoir-visualizer

3D reservoir visualizer with LLM copilot. Built on LAS file parsing, PyVista/Plotly 3D
rendering, Streamlit UI, and a local Ollama-powered chat with function calling.

## Rules index

| Rule | Purpose |
|---|---|
| `code-style.md` | Layout, naming, spacing, step/substep structure |
| `file-naming.md` | File naming conventions and execution order |
| `code-change.md` | Scope and safety of edits |
| `logging-policy.md` | Print and logging control |
| `doc-enforcement.md` | Docstring requirements and standards |
| `docs-style.md` | Markdown documentation format |
| `plan-format.md` | Plan file format and update rules |

## Skills index

| Skill | Purpose |
|---|---|
| `/bitacora` | Register work session in `todo/bitacora-YYYY-MM-DD.md` |
| `/test` | Create test scripts for modules |
| `/debug` | Create isolated debug scripts for investigation |
| `/document` | Generate documentation for a module |
| `/doc-enforce` | Review and enforce docstrings on existing code |
| `/plan-writing` | Write and update project plans in `todo/` |
| `/phase-executor` | Read and execute a phase from `PLAN.md` in order |

## Enforcement strategy

- Rules apply automatically to all code generated in this project.
- Skills are invoked on demand by the user or triggered by Claude when relevant.
- When in doubt about a convention, check the specific rule file.

## Validation modes

| Mode | Description | Phase |
|---|---|---|
| `suggest` | Recommendations and warnings | Prototype / exploration |
| `warn` | Clear violations flagged but not blocking | Active development |
| `strict` | Enforcement with failures | Production / final |

**Current mode: `warn`**

## Progressive enforcement

- **Prototype phase**: `suggest` mode. Focus on speed, rules are advisory.
- **Development phase**: `warn` mode. Rules enforced, violations flagged.
- **Production phase**: `strict` mode. All rules enforced, no exceptions.

## Project structure

Defined at the start of each phase. Replace this section when the folder tree is finalized.
The following folders are always present regardless of phase:

```
src/          → Pure logic (LAS loading, 3D rendering, LLM copilot)
tests/        → pytest test scripts (committed to git)
debug/        → Exploration and debug scripts (always gitignored)
todo/         → PLAN.md and session logs (bitacoras)
docs/         → Technical documentation (read by Windows/Obsidian)
data/         → Demo LAS files and configs
```

## Tech constraints

- **Runtime**: WSL2 (Ubuntu), Python 3.10+
- **Hardware**: RTX 4080 — GPU available for LLM inference via Ollama
- **LLM**: Ollama local (qwen3:14b confirmed working). No external LLM API required.
- **UI**: Streamlit — all visualization served through the Streamlit app
- **3D rendering**: PyVista or Plotly 3D (decided per phase)
- **Deployment target**: `docker compose up` locally + Hugging Face Spaces (public demo)
- **Data**: Kansas Geological Survey LAS files at `/home/pokinux/Kansas/data/v3.0_las_files/`
- **No direct WSL↔Windows file bridge**: docs/ and todo/ are the sync surface with Obsidian

## Policies

This project applies three guiding principles (not enforced as strict rules):

- **KISS**: Prefer the simplest solution that renders correctly and explains clearly.
- **No over-engineering**: No abstractions for hypothetical future wells or formations.
- **Fail fast on data**: Invalid LAS files must error immediately with a clear message, not silently degrade.
