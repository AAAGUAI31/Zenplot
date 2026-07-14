---
name: bclass-diagram-to-system-root-xml
description: Convert B-class circuit architecture and control-system block-diagram figures into SimulinkSystemJSON and editable Simulink core XML. Use when Codex needs to recognize paper control-system, Sigma-Delta modulator, Simulink-style, signal-flow, or discrete-time DSP diagrams and emit simulink/systems/system_root.xml <System> output.
---

# B-Class Diagram To System Root XML

## Purpose

Use this skill for B-class circuit-architecture and control-system block diagrams. It recognizes diagram semantics and emits Simulink-editable `simulink/systems/system_root.xml` core XML through `SimulinkSystemJSON`. It supports two related intermediate representations:

- `MasterFigureJSON`: visual nodes/edges/layout/style for paper-style redraw.
- `SimulinkSystemJSON`: Simulink-editable model structure for generating `simulink/systems/system_root.xml`.

For Simulink reconstruction, treat `SimulinkSystemJSON` as canonical. `MasterFigureJSON` may help visualization, but it loses Simulink semantics such as `SID`, `BlockType`, `PortCounts`, block `P` parameters, `Line`, nested `Branch`, `Points`, `ZOrder`, and `Annotation`.

## Simulink XML Workflow

```text
paper figure image
  -> recognize block diagram semantics
  -> SimulinkSystemJSON
  -> validate_simulink_system_json.py
  -> emit_system_root_xml.py
  -> generated system_root.xml containing <System>...</System>
```

Output only the core `<System>...</System>` for Simulink XML tasks. Do not emit a full `.slx`, MATLAB script, draw.io file, SVG, or Mermaid diagram as the primary output.

## Required SimulinkSystemJSON Shape

The root object must contain:

```json
{
  "meta": {},
  "system": {},
  "blocks": [],
  "lines": [],
  "annotations": [],
  "layout": {},
  "style": {},
  "evidence": {}
}
```

Read `references/simulink_system_json_schema.json` for the field contract.

## Recognition Rules

Map paper block-diagram semantics to Simulink blocks:

- input/output labels -> `Inport` / `Outport`
- triangle gain -> `Gain`
- circle with signs -> `Sum`
- integrator box -> `Integrator`
- quantizer/relay -> `Relay`
- switched references -> `Switch` plus `Constant`
- long bus or branch -> `Line` with nested `Branch`
- visible notes -> `Annotation`

Use `references/simulink_block_mapping.md` and `references/system_root_xml_patterns.md` for exact conventions.

## Tools

Parse existing `system_root.xml` into `SimulinkSystemJSON`:

```bash
python skills/bclass-diagram-to-system-root-xml/scripts/parse_system_root_xml.py path/to/system_root.xml --output system.json
```

Validate:

```bash
python skills/bclass-diagram-to-system-root-xml/scripts/validate_simulink_system_json.py system.json
```

Emit XML:

```bash
python skills/bclass-diagram-to-system-root-xml/scripts/emit_system_root_xml.py system.json --output generated_system_root.xml
```

Compare generated XML with a reference:

```bash
python skills/bclass-diagram-to-system-root-xml/scripts/compare_system_root_xml.py reference.xml generated_system_root.xml
```

## Quality Checklist

- Every Simulink block has `sid`, `name`, `block_type`, `position`, `parameters`, and optional `port_counts`.
- Every line preserves `src`, `dst`, `points`, recursive `branches`, and `z_order`.
- Every annotation preserves `sid`, `name`, `position`, margins, and `z_order`.
- `SIDHighWatermark` is preserved or recomputed conservatively.
- Unknown visual facts are recorded in `evidence.unresolved`, not silently dropped.
