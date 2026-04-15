---
description: Define standards for documentation files
---

# Docs Style

All technical documentation must reflect the actual behavior of the code — not future plans or assumptions.

## Docs root folder

- **Documentation location: `docs/`** (this folder is the bridge to the Windows/Obsidian vault).
- Auto-generated content must not be placed in the docs folder.
- All documentation is in **English**.
- `todo/` holds session logs and plans (also readable from Windows/Obsidian).

## Filename convention

- See `file-naming.md` for naming guidance.
- Pattern: `NN_<slug>.md` for ordered docs.
- Examples: `01_las_loader.md`, `02_3d_renderer.md`, `03_llm_copilot.md`

## Required sections

Every documentation file must include:

1. **Title and Purpose** — Start with a single sentence summarizing the module's role.
2. **Workflow Description** — Describe the sequence of operations performed. Use numbered steps or descriptive text. Include a Mermaid diagram (`flowchart TD` or `graph LR`) if the flow is complex.
3. **Inputs and Outputs** — List each parameter with name, type, and purpose. Describe expected output(s) and their structure.
4. **Mathematical Explanation** (if applicable) — Use LaTeX or pseudocode for formulas. Relevant for kriging interpolation, petrophysical transforms, etc.
5. **Code Reference** — Always include the source module path (e.g., `Source: src/las/loader.py`).

## Style

- Write clearly and concisely. Use short paragraphs and examples when helpful.
- Document only what exists in the current version of the code.
- Avoid TODOs and speculative notes.
- Each document must be self-contained — readable without prior context.
- Mermaid diagrams are encouraged for data flows and component architecture.

## Cross-references

- See `doc-enforcement.md` for inline docstring standards.
- See `document/SKILL.md` for the on-demand documentation generation workflow.
