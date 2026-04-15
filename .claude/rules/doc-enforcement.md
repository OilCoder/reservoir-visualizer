---
description: Enforce standardized docstrings and module-level documentation in all source files
---

# Doc Enforcement

All public functions, methods, and classes must include a docstring.
This rule applies passively to all code Claude generates or modifies.

## Docstring required

- All public functions, methods, and classes must include a docstring.
- Private functions (starting with `_`) require a docstring only if they contain nontrivial logic.
- **Docstring format: Google Style.**

## Module header

- Every source file must begin with a top-level module docstring.
- Content: concise summary of the module's purpose (1–3 lines).
- May include an optional bullet list of major functions or classes.
- May include optional usage context (e.g., "Called by `s99_run_pipeline.py`").
- Keep it under 100 words.

## Docstring structure (Google Style)

Must include (if applicable):

```python
def function_name(param1: type, param2: type) -> return_type:
    """One-line summary of what this function does.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When something is invalid.
    """
```

## Style rules

- Do not mix formats within the project.
- Avoid vague terms like "does something", "helper function", "processes data".
- If a function has no parameters or return value, still explain what it does.
- **Language: English.**

## Consistency

- Docstrings must reflect actual behavior, not intentions or placeholders.
- Do not duplicate content across sections.
- Keep docstrings concise, specific, and informative.
- When modifying a function, update its docstring if the behavior changed.

## Enforcement scope

- **Applies to all files under `src/`.**
- Functions without docstrings may be excluded from generated documentation.

## Cross-references

- See `doc-enforce/SKILL.md` for the on-demand review and enforcement workflow.
- See `docs-style.md` for Markdown documentation standards.
