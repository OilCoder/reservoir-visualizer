---
description: Control use of print and logging across all code
---

# Logging Policy

## Print usage

- Temporary `print()` statements are allowed during development.
- **Log/print message language: English.**
- All print calls must be removed before final commits unless:
  - They are part of CLI tools or user-facing interfaces.
  - They appear in notebooks used for demos or traceability.
  - They serve a critical runtime function (progress indicators, etc.).

## Logging usage

- Use Python's standard `logging` module for structured output in production.
- Avoid debug-level logging unless the logger is properly configured and output can be filtered.
- Use module-scoped loggers: `logger = logging.getLogger(__name__)`.

## Progress output

- **Batch operations** (e.g., loading multiple LAS files): use `tqdm` progress bars.
- **Streamlit UI operations** (e.g., rendering 3D mesh, running LLM inference): use `st.progress` or `st.spinner`.
- Log errors per item without stopping the full batch when appropriate.
- A final summary line (total processed, skipped, failed) is recommended for batch operations.

## Cleanup and isolation

- Extensive debug output must be isolated into scripts inside `debug/`.
- Debug code and verbose logs must be excluded from main modules under `src/`.
- Final production code must not include leftover print or logging unless justified by scope.
- Treat print/log statements as disposable scaffolding unless approved.
- Do not add `logging.debug()` noise to production modules unless the logger is properly configured.

## Exceptions

- In Streamlit pages, `st.write()` and `st.info()` are the preferred output mechanisms.
- CLI scripts may retain structured logging or print if it improves UX or runtime feedback.
- Notebooks in `debug/` may use print freely for exploration.
