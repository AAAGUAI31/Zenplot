# Draw.io Generation Rules

## Component Templates

Use `assets/drawio_component_catalog.xml` for standard components. Copy the matching group by `component_key`, then:

- assign unique IDs
- set parent IDs
- scale/move to LayoutSpec geometry
- bind text fields from LayoutSpec
- move internal port cells to LayoutSpec port coordinates
- preserve internal catalog child edges

Do not redraw standard components freehand if a catalog template exists. The generated draw.io XML must contain the copied group cell whose style still includes `group;componentKey=...` plus the copied child cells. A primitive cell with `componentKey` added to its style is a failed generation.

Formula-bearing components must be copied from the catalog. Do not emit visible escaped formula strings such as `z&lt;sup...`; the formula must be the template's internal text.

## Edges

Generate edges from LayoutSpec only:

- source endpoint
- target endpoint
- orthogonal route style
- absolute waypoints
- arrow style
- stroke width

Do not infer new waypoints in the generator. If the route is bad, Visual QA and Revision Agent must patch LayoutSpec.

Resolve edge endpoints to copied internal port cells when a template exposes `portName=...`. If a requested port is absent, report `missing_component_port` in the manifest instead of silently connecting to the group body.

## IDs

Every generated mxCell ID must be unique and stable within an iteration. Write a `generation_manifest.json` that maps:

- semantic node ID to draw.io group/cell ID
- layout edge ID to draw.io edge cell ID
- component key to template group ID

## Failure

If a required template is missing, stop and report:

```json
{
  "status": "failed",
  "errors": [
    {"type": "missing_component_template", "target": "component_key"}
  ]
}
```
