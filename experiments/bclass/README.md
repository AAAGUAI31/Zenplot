# B-Class Experiments

This directory contains B-class circuit architecture and control-system block-diagram experiments.

The cases are organized by figure case rather than by test batch, so each case can be compared across methods:

```text
cases/case1/
  reference/
  runs/baseline1/
  runs/test1/
  runs/test2_llm/
  runs/test3_llm/
```

Recommended comparison dimensions:

- topology correctness against `system_root.xml`
- block type and parameter correctness
- branch and feedback preservation
- draw.io editability
- visual QA score and remaining high-severity issues

