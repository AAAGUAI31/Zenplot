# Workflow Contract

This skill uses five LLM agents plus a mechanical render/tool layer.

## Layer Boundaries

- `SemanticSpec` is the fact and interpretation layer.
- `source_facts` is immutable XML truth.
- `inferred_semantics` is LLM interpretation.
- `LayoutSpec` is the design layer.
- `draw.io XML` is the execution layer.
- `QA Report` is the evaluation layer.
- `Layout Patch` is the correction layer.

## Non-Negotiable Rules

- Do not edit `source_facts` after semantic interpretation unless the source XML changes.
- Do not directly patch final draw.io XML during revision.
- Do not let QA modify files.
- Do not let Draw.io Generator relayout the diagram.
- Do not use deterministic semantic/layout Python generators from older skills.
- Use scripts/tools only for mechanical validation, rendering, file organization, or asset copying.

## Iteration Policy

Each iteration must keep:

- LayoutSpec
- draw.io XML
- PNG preview or render failure report
- generation manifest
- QA report
- layout patch if generated

When a revision makes the diagram worse, keep the previous best-scoring iteration.
