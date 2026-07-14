# Semantic Interpreter

Convert `system_root.xml` into `SemanticSpec`. This agent reads XML facts and separates them from LLM inference.

## Input

- `system_root.xml`
- Optional domain notes
- Optional component catalog summary

## Output

Write `semantic_spec.json` matching `schemas/semantic_spec.schema.json`.

## Required Structure

- `source_facts`: facts directly present in XML only.
- `inferred_semantics`: LLM interpretation only.
- `uncertainties`: ambiguous interpretations with candidates and confidence.

## Source Facts

Extract exactly:

- system properties
- blocks: SID, BlockType, Name, parameters, PortCounts, ports, original Position, ZOrder when present
- lines: source, source port, target, target port, Points
- branches: nested branch topology, branch Points, branch destinations
- annotations

Do not normalize away original identifiers. Preserve XML topology exactly.

## Inferred Semantics

Infer:

- main signal flow
- feedback loops
- feedforward paths
- semantic roles
- functional groups
- preferred signal directions

For each inference, include supporting source fact IDs where practical.

## Forbidden

- Do not generate layout coordinates.
- Do not generate draw.io XML.
- Do not add or delete blocks, ports, edges, branches, or annotations.
- Do not mix inferred semantics into `source_facts`.
