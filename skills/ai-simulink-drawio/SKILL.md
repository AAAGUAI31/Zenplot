---
name: ai-simulink-drawio
description: AI-powered workflow for converting Simulink system_root.xml into editable draw.io XML and PNG previews. Use when Codex should let LLM agents read Simulink core XML, produce SemanticSpec and LayoutSpec, generate draw.io XML with a component catalog, visually QA the rendered PNG, and iterate with LayoutPatch corrections rather than using deterministic semantic/layout Python generators.
---

# AI Simulink Draw.io

## Purpose

Use this skill to convert `system_root.xml` into editable draw.io diagrams through an AI-powered five-agent workflow. The LLM is responsible for semantic interpretation, layout planning, draw.io XML generation, visual QA, and revision decisions.

Mechanical scripts/tools may only validate XML, render draw.io to PNG, copy assets, and organize iteration artifacts. Do not use deterministic Python semantic or layout generators from the older skills as the primary workflow.

When a standard component has a catalog entry, the final draw.io XML must contain a copied catalog group and its child cells. Writing `componentKey=...` onto a single primitive mxCell is not sufficient.

## Workflow

```text
system_root.xml
  -> Semantic Interpreter
  -> SemanticSpec
  -> Layout Planner
  -> LayoutSpec
  -> Draw.io Generator
  -> generated.drawio
  -> Render Tool
  -> generated.png
  -> Visual QA
  -> QA Report
  -> Revision Agent
  -> Layout Patch
  -> updated LayoutSpec
  -> regenerate until pass or stop
```

Stop when semantic errors against `source_facts` are zero, no high-severity QA issues remain, no edge-node overlaps or disconnected edges remain, component orientation is correct, and routing/layout scores are at least 85.

Hard stop at 5 iterations, two rounds without score improvement, increased high-severity issues after a patch, the same issue unresolved twice, or unrecoverable XML/render failure. Keep the best-scoring iteration if final pass is not reached.

## Intermediate Contracts

Always separate immutable XML facts from LLM inference in `SemanticSpec`:

```json
{
  "meta": {"source_format": "simulink_system_root_xml", "source_file": "system_root.xml"},
  "source_facts": {
    "nodes": [],
    "edges": [],
    "branches": [],
    "annotations": [],
    "system_properties": {}
  },
  "inferred_semantics": {
    "main_signal_flow": [],
    "feedback_loops": [],
    "feedforward_paths": [],
    "functional_groups": [],
    "semantic_roles": {},
    "preferred_signal_directions": {}
  },
  "uncertainties": []
}
```

`source_facts` may contain only XML-provided facts: SID, BlockType, Name, parameters, ports, PortCounts, lines, branches, Points, annotations, and original positions.

`inferred_semantics` may contain only LLM-derived interpretation: main chain, feedback loop, feedforward path, semantic role, functional group, and preferred signal direction.

`LayoutSpec` is the design layer. It may choose component keys, positions, sizes, orientations, ports, alignments, groups, lanes, junctions, and route intent. It must not change source-target topology or mutate `source_facts`.

## Agent Instructions

Load the relevant agent instruction before each phase:

- Semantic interpretation: `agents/semantic_interpreter.md`
- Layout planning: `agents/layout_planner.md`
- Draw.io XML generation: `agents/drawio_generator.md`
- Visual QA: `agents/visual_qa.md`
- Revision: `agents/revision_agent.md`

Use schemas as output contracts:

- `schemas/semantic_spec.schema.json`
- `schemas/layout_spec.schema.json`
- `schemas/qa_report.schema.json`
- `schemas/layout_patch.schema.json`

Use `assets/drawio_component_catalog.xml` and `assets/component_manifest.json` for component templates. Standard components must be copied from the catalog rather than redrawn freehand.

Use mechanical materialization only after `LayoutSpec` exists:

- `tools/materialize_layout_spec.py` may convert `LayoutSpec` into draw.io XML by copying catalog groups, binding labels, moving/scaling geometries, connecting internal port cells, and writing a generation manifest.
- It must not interpret Simulink semantics, choose component keys, place nodes, choose routes, or patch QA failures.

## Artifact Layout

For each run, create:

```text
output/
  semantic_spec.json
  iterations/
    iter_00/
      layout_spec.json
      generated.drawio
      generated.png
      generation_manifest.json
      qa_report.json
      layout_patch.json
  final/
    final_layout_spec.json
    final.drawio
    final.png
    final_qa_report.json
    run_summary.md
```

## Quality Rules

- Preserve `source_facts` exactly unless the original XML changes.
- Do not directly patch final draw.io XML during revision; patch `LayoutSpec` and regenerate.
- Prefer direct orthogonal routes, then one-bend routes, then outer lanes only when needed.
- Support gain orientation `right`, `left`, `up`, and `down`, while keeping internal text horizontal.
- Formula-bearing blocks such as `DiscreteTransferFcn` must use `discrete_transfer_inline`; the visible formula must come from the template, not escaped literal text.
- For top-side sources such as `E(z)` feeding a lower component, use the source bottom port and a vertical-down route whenever the topology allows it.
- Feedback paths into repeated sums should prefer the lower outer lane and vertical-up entry into the sum; do not route above the main chain unless the reference or layout explicitly requires it.
- Main-chain endpoints should be y-aligned within a small tolerance; avoid micro-offsets that produce visual zigzags.
- Alignment is port-based, not merely bounding-box based: for a main chain, every component's actual `out1`/next `in1` port center should share the same y coordinate within 1 px. Move component geometry to satisfy port alignment.
- Port alignment must apply only to nodes explicitly assigned to the inferred main chain. Do not align feedforward, feedback, side-path, or auxiliary gains to the main-chain lane.
- Preserve or deliberately assign separate lanes for feedforward/feedback components such as `b2`, `g1`, `c1`, `a1`, `a2`, and `a3`; collapsing these side-path nodes into the main chain is a high-severity layout error.
- Feedforward gains that feed the same downstream sum must remain independently visible with distinct geometries, lanes, and labels. Stacking `0.8`, `0.3`, and `0.05` gains at the same coordinates is a high-severity `feedforward_gain_missing_or_hidden` error.
- Known selector patterns must collapse visually into catalog components while keeping XML facts unchanged: `Constant(+alphaDeltaVBE) + Constant(-alphaDeltaVBE) + Switch` uses `bipolar_reference_selector_alpha_inline`; `Constant(+VBE) + Constant(-VBE) + Switch` uses `bipolar_reference_selector_vbe_inline`.
- When selector collapse is used, do not draw the consumed Constants or Switch as visible generic boxes. Add a trace field such as `collapsed_source_facts` on the selector LayoutSpec node.
- Top-side inputs should align their bottom port x coordinate with the receiving top port x coordinate before routing vertically downward.
- Branch points must be explicit `junction_dot_inline` nodes in LayoutSpec when a line visually splits or when a feedback bus feeds multiple sums.
- For a branch between two connected components, place the junction dot on the main segment between the source output port and the main target input port, preferably near the midpoint of those two ports. Do not visually split branches directly at the previous component's output port.
- Branch edges should visually start from the junction dot. Preserve the original XML source in `source_facts`, but represent the visual branch source as the junction node in `LayoutSpec` with a trace back to the semantic edge.
- LayoutSpec routes must not include negative canvas coordinates unless the canvas was intentionally expanded to include them.
- Gain labels may convert ASCII names such as `alpha1`, `alpha2`, `alpha3` into Greek math labels `α1`, `α2`, `α3` when this is a visual label improvement only; preserve the original XML name in `source_facts`.
- Distinguish fact errors from inference, layout, routing, and style errors in QA.
- Record uncertainty instead of guessing.
