---
description: Enforce consistent file naming across the project
---

# File Naming

All files must follow consistent and descriptive naming conventions
for discoverability, clarity, and traceability across the codebase.

## General conventions

- Use `snake_case` for all files: lowercase letters with underscores.
- Filenames must reflect the purpose or main component of the file.
- Avoid generic names like `script.py`, `data.json`, `utils.py` unless scoped in clearly named folders.
- No spaces, accented characters, or mixed camelCase/snake_case.
- **File name language: English.**

## Execution order naming

- Pipeline or sequential scripts carry the `sNN_` prefix (consistent with the OilCoder portfolio).
- Pattern: `sNN_<verb>_<noun>.<ext>` (e.g., `s01_load_las.py`, `s02_parse_formations.py`).
- Sub-steps use a letter suffix: `sNNx_` (e.g., `s03a_render_single_well.py`).
- Orchestrators or main launchers use prefix `s99_` (e.g., `s99_run_pipeline.py`).
- The numeric prefix is for natural sorting only — it must not create hard dependencies.

## Output files

- Generated plots: `{well_id}_{property}_{view}.png` (e.g., `arroyo_22_porosity_3d.png`)
- Exported data: `{dataset}_{step}.csv` or `{dataset}_{step}.parquet`
- Output files live in `outputs/` or `data/outputs/` (gitignored).

## Data files

- Input LAS files: use original names from source (Kansas KGS convention).
- Config files: `config.yaml` or `{component}_config.yaml` in the project root or `src/`.
- Demo data symlinked or copied from `/home/pokinux/Kansas/data/v3.0_las_files/`.

## Test files

- Pattern: `test_<module>_<case>.py`
- All test files live under `tests/`.
- Tests are **committed to git** for portfolio visibility.

## Debug files

- Pattern: `dbg_<slug>[_<experiment>].py`
- All debug files live under `debug/`.
- `debug/` must always be in `.gitignore`.

## Documentation

- Pattern: `NN_<slug>.md` for ordered docs.
- Location: `docs/` (this folder is the sync surface with the Windows/Obsidian vault).

## Cross-references

- See `docs-style.md` for documentation content standards.
- See `code-change.md` for multi-file change procedures.
