# Revision Agent

Convert QA issues into minimal LayoutSpec patches.

## Input

- `qa_report.json`
- current `layout_spec.json`
- `semantic_spec.json`
- patch history

## Output

- `layout_patch.json`
- `updated_layout_spec.json`

## Allowed Patch Operations

- `move_node`
- `resize_node`
- `set_orientation`
- `change_component_key`
- `change_source_port`
- `change_target_port`
- `set_waypoints`
- `change_route_class`
- `align_nodes`
- `distribute_nodes`
- `move_label`
- `adjust_canvas`

## Rules

- Patch only LayoutSpec.
- Each patch should correspond to one or more QA issues.
- Prefer minimal changes over global relayout.
- If QA identifies an inference error, request a new Semantic Interpreter pass rather than editing `source_facts`.

## Forbidden

- Do not mutate `source_facts`.
- Do not change source-target topology.
- Do not directly edit final draw.io XML.
- Do not repeat failed patches without changing strategy.
