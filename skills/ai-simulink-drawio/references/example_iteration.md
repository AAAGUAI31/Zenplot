# Example Iteration

## Iteration 0

1. Semantic Interpreter reads `system_root.xml`.
2. It writes `semantic_spec.json` with XML facts under `source_facts` and main-chain/feedback interpretation under `inferred_semantics`.
3. Layout Planner writes `layout_spec.json`.
4. Draw.io Generator writes `generated.drawio` and `generation_manifest.json`.
5. Render tool creates `generated.png`.
6. Visual QA writes `qa_report.json`.

Example QA issue:

```json
{
  "id": "issue_1",
  "type": "edge_node_overlap",
  "severity": "high",
  "targets": ["edge_feedback_1", "node_gain_a2"],
  "description": "The feedback edge crosses a gain block.",
  "evidence": {"region": [480, 320, 620, 410]}
}
```

## Revision

Revision Agent writes:

```json
{
  "base_iteration": 0,
  "patches": [
    {
      "operation": "set_waypoints",
      "target": "edge_feedback_1",
      "value": [[1200, 520], [180, 520], [180, 260]],
      "reason": "Route long feedback on the lower outer lane.",
      "qa_issue_ids": ["issue_1"]
    }
  ],
  "expected_improvements": ["remove edge-node overlap"]
}
```

The updated LayoutSpec is then regenerated into the next draw.io and PNG.
