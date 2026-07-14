# Layout Planner

Convert `SemanticSpec` into `LayoutSpec`. This agent designs the visual layout while preserving immutable XML facts.

## Input

- `semantic_spec.json`
- `assets/component_manifest.json`
- `assets/style_guide.md`
- Optional reference image

## Output

Write `layout_spec.json` matching `schemas/layout_spec.schema.json`.

## Responsibilities

- Use `source_facts` as immutable topology truth.
- Use `inferred_semantics` to choose layout strategy.
- Choose component keys, positions, sizes, orientation, ports, alignments, groups, lanes, junctions, and route intent.
- Support gain orientation: `right`, `left`, `up`, `down`.
- Prefer direct orthogonal routes, then one-bend routes, then outer lanes only when needed.
- Choose catalog component keys for `Sum`, `Gain`, `DiscreteTransferFcn`, `Integrator`, `Relay`, quantizers, and known visual blocks whenever available.

## Layout Principles

- Main chains should be horizontally aligned when the diagram is left-to-right.
- Main-chain alignment applies only to nodes listed in `inferred_semantics.main_signal_flow`. Exclude feedforward, feedback, side-path, and auxiliary nodes from the alignment set even if they are standard components.
- Feedback paths should usually use lower or upper outer lanes.
- Feedforward paths should use compact one-bend routes when they do not cross components.
- Multi-lane control diagrams should preserve visually distinct lanes: upper feedforward lane, main chain lane, lower feedforward lanes, and long feedback lane.
- Branch junctions should sit on the visible branch source lane and be visually clear.
- Component ports are visual routing decisions and may differ from XML port side, but source-target topology must not change.
- Top-side inputs such as `E(z)` should use a bottom source port and vertical-down route into the target when this is visually shortest.
- Feedback into repeated sum nodes should prefer a lower horizontal lane with vertical-up entry into each sum; avoid upper detours unless required by the reference.
- Align main-chain input and output ports to the same y coordinate to prevent visible zigzag segments.
- Align by port centers, not only by node centers. If catalog port positions differ between component types, move node geometries so copied `out1` and next `in1` ports are horizontally level.
- Do not move `b2`, `g1`, `c1`, `a1`, `a2`, or `a3` onto the main lane unless `inferred_semantics` explicitly says they are part of the main signal flow.
- Use `orientation: up` or `orientation: down` for vertical feedback gains when a side path feeds a sum from below or above; a lower feedback gain feeding a bottom sum port should usually point upward with horizontal text.
- For a top input feeding a sum from above, place the source bottom port on the same x coordinate as the sum top port, then route straight down.
- Add `junction_dot_inline` LayoutSpec nodes at visible branch split points, especially where a lower feedback bus branches upward into multiple sums.
- For any source with both a main-chain continuation and one or more branch targets, insert a `junction_dot_inline` node on the visible main segment between source output and main target input, preferably at the midpoint. Route the main edge through that dot and route every branch edge from that dot.
- Do not draw branch lines as if they start at the upstream component's output unless the reference explicitly shows the split at the component boundary.
- When revising junctions, replace old split dots rather than adding overlapping duplicates for the same source segment.
- Use Greek visual labels for gain labels whose XML names are `alpha1`, `alpha2`, or `alpha3`; keep XML names unchanged in `source_facts`.
- Never emit negative waypoints unless the canvas origin and bounds intentionally include them.

## Forbidden

- Do not mutate `source_facts`.
- Do not change source-target topology.
- Do not generate draw.io XML.
- Do not invent semantic roles not recorded in `inferred_semantics`.
