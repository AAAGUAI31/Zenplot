# Render Draw.io To PNG Tool Contract

This is a mechanical tool layer. It may use any available local renderer, draw.io export path, browser automation, or manually configured renderer.

## Input

- `iteration_N.drawio`

## Output

- `iteration_N.png`
- `render_report.json`

## Requirements

- Do not change SemanticSpec or LayoutSpec.
- Do not repair draw.io XML.
- If rendering fails, write a clear failure report with command, error, and missing dependency.
- Keep the generated PNG associated with the exact draw.io input.
