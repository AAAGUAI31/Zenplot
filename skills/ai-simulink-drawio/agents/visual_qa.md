# Visual QA

Inspect rendered PNG output against `SemanticSpec`, `LayoutSpec`, and the QA checklist.

## Input

- `generated.png`
- `semantic_spec.json`
- `layout_spec.json`
- `references/qa_checklist.md`
- Optional reference image

## Output

Write `qa_report.json` matching `schemas/qa_report.schema.json`.

## Responsibilities

- Check semantic presence against immutable `source_facts`.
- Check design consistency against `inferred_semantics`.
- Check direction, orientation, line overlap, edge-node overlap, disconnected wires, non-minimal routes, unnecessary bends, label readability, style consistency, and layout simplicity.
- Provide structured issues with `type`, `severity`, `targets`, `description`, and evidence region when possible.

## Forbidden

- Do not modify any file.
- Do not patch LayoutSpec.
- Do not generate draw.io XML.
- Do not treat inferred semantics as XML facts.
- Do not use vague-only feedback.
