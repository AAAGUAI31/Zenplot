# Contribution Guide

## Where To Put New Work

- New reusable recognition or rendering logic belongs in `skills/<skill-name>/`.
- Case-specific experiments belong in `experiments/<class>/cases/<case-id>/`.
- Shared helper scripts belong in `tools/shared/`.
- Curated datasets belong in `datasets/<class>/`.

## Experiment Case Layout

Use this structure for new B-class or A-class cases:

```text
experiments/<class>/cases/<case-id>/
  input/
  reference/
  runs/
    <method-or-date>/
      README.md
      final/
      intermediate/
```

Keep large temporary outputs local unless they are needed to reproduce a result.

## Skill Hygiene

Do not commit:

- `__pycache__/`
- `.venv/`
- local API keys or credentials
- unbounded logs
- machine-specific absolute paths

Each skill should include:

- `SKILL.md`
- agent prompts or tool scripts
- schemas or references required by the skill
- small examples when useful

