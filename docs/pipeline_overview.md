# Pipeline Overview

Zenplot separates recognition, semantic reconstruction, visual generation, and QA into explicit stages.

## B-Class Recognition Pipeline

```text
paper figure image
  -> recognize diagram semantics
  -> SimulinkSystemJSON
  -> validate_simulink_system_json.py
  -> emit_system_root_xml.py
  -> system_root.xml
```

The B-class skill treats `SimulinkSystemJSON` as the canonical intermediate representation because it can preserve Simulink-specific facts such as SIDs, block types, parameters, ports, lines, branches, points, annotations, and layout.

## Draw.io Reconstruction Pipeline

```text
system_root.xml
  -> Semantic Interpreter
  -> SemanticSpec
  -> Layout Planner
  -> LayoutSpec
  -> Draw.io Generator / materializer
  -> generated.drawio
  -> PNG render
  -> Visual QA
  -> LayoutPatch
  -> regenerated output
```

The draw.io skill keeps immutable XML facts separate from LLM inference:

- `source_facts`: facts directly read from `system_root.xml`.
- `inferred_semantics`: main signal flow, feedback loops, feedforward paths, roles, and preferred directions.
- `LayoutSpec`: design decisions such as component templates, geometry, ports, lanes, and routes.
- `QAReport`: structured visual and semantic issues.
- `LayoutPatch`: minimal changes to the layout spec, not direct edits to final draw.io XML.

## Design Principle

LLM agents make semantic and layout decisions. Scripts perform mechanical validation, XML emission, template copying, rendering, and artifact organization.

