# Zenplot

Zenplot is a collaborative research repository for reconstructing editable technical diagrams from paper figures and Simulink-style sources.

The current repository focuses on the B-class workflow:

```text
paper block-diagram figure
  -> bclass-diagram-to-system-root-xml
  -> SimulinkSystemJSON
  -> simulink/systems/system_root.xml
  -> ai-simulink-drawio
  -> editable draw.io XML
  -> PNG preview and visual QA
```

## Repository Layout

```text
skills/
  bclass-diagram-to-system-root-xml/  # B-class paper figure -> system_root.xml
  ai-simulink-drawio/                 # system_root.xml -> draw.io/PNG/QA
  aclass-circuit-recognition/         # reserved for A-class work

experiments/
  bclass/                             # B-class cases and runs
  aclass/                             # reserved for teammate A-class experiments

datasets/
  bclass/                             # curated source datasets or references
  aclass/

docs/
  pipeline_overview.md
  contribution_guide.md
```

## Included Workflows

- `skills/bclass-diagram-to-system-root-xml`: recognizes B-class circuit architecture and control-system block diagrams, then emits Simulink-editable `system_root.xml`.
- `skills/ai-simulink-drawio`: converts `system_root.xml` into editable draw.io diagrams using a SemanticSpec -> LayoutSpec -> visual QA iteration loop.

## Experiment Organization

B-class experiments are organized by case:

```text
experiments/bclass/cases/case1/
  input/
  reference/
  runs/
    baseline1/
    test1/
    test2_llm/
    test3_llm/
```

Each `runs/*` directory preserves the outputs from one experimental attempt. Prefer committing curated final outputs and summaries over unbounded temporary artifacts.

