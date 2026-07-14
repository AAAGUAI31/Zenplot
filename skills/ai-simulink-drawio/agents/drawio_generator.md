# Draw.io Generator

Generate draw.io XML from `SemanticSpec`, `LayoutSpec`, and the component catalog.

## Input

- `semantic_spec.json`
- `layout_spec.json`
- `assets/drawio_component_catalog.xml`
- `templates/drawio_base.xml`

## Output

- `generated.drawio`
- `generation_manifest.json`

## Responsibilities

- Generate valid draw.io XML directly from LayoutSpec.
- Copy matching catalog groups by `component_key`.
- Assign unique mxCell IDs.
- Bind labels and parameter text.
- Scale and move copied templates to LayoutSpec geometry.
- Set internal port cells according to LayoutSpec ports.
- Write edges and waypoints exactly from LayoutSpec route intent.
- Maintain manifest mappings from semantic/layout IDs to mxCell IDs.

## Forbidden

- Do not relayout.
- Do not reinterpret XML semantics.
- Do not rewire source-target topology.
- Do not freehand redraw a standard component if a catalog template exists.
- Report missing component templates instead of silently substituting.
