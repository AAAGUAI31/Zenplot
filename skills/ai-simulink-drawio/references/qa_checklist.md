# QA Checklist

## Semantic QA

- All XML source blocks appear visually or are intentionally collapsed into a documented visual component.
- All source edges and branches are represented.
- Source-target direction is correct.
- Standard blocks use copied component catalog templates when a matching template exists.
- Formula-bearing components are rendered as formula templates, not escaped literal text.
- Sum signs and input roles match inferred semantics.
- Gain orientation follows preferred signal direction.
- Feedback and feedforward paths return to the correct semantic targets.
- Known multi-block visual patterns are collapsed only at the visual layer and are documented by trace fields.
- `Constant(+alphaDeltaVBE) + Constant(-alphaDeltaVBE) + Switch` must render as `bipolar_reference_selector_alpha_inline` when that pattern exists.
- `Constant(+VBE) + Constant(-VBE) + Switch` must render as `bipolar_reference_selector_vbe_inline` when that pattern exists.
- Collapsed selector source blocks must not also appear as visible generic Constant/Switch boxes.

## Geometric QA

- No node-node overlap.
- No edge-node overlap except at connected ports.
- No label-node or label-edge overlap.
- No disconnected wires.
- No out-of-canvas objects.
- Ports connect naturally to component boundaries.

## Routing QA

- Avoid unnecessary bends.
- Main chain routes should be direct.
- Feedforward routes should be direct or one-bend when possible.
- Long feedback routes should use an outer lane.
- Branch junctions should be visible and clear.
- Branch junction dots between two connected components should sit on the main segment, near the midpoint between source output and main target input.
- Branch routes should start from the junction dot, not directly from the upstream component output, unless the reference explicitly shows that.
- Do not leave duplicate junction dots for the same visual split after revision; one visible split point should have one junction node.
- Parallel lines should not visually merge.
- Top-side sources feeding lower targets should exit from the bottom and travel vertically down unless blocked.
- Top-side source bottom ports should align horizontally with the receiving top port before the vertical segment begins.
- Repeated feedback into sums should use lower lanes and vertical-up entry when that is simpler than upper routing.
- Feedback bus split points should be marked by copied `junction_dot_inline` black-dot templates.
- No negative canvas waypoints unless the canvas explicitly includes that area.
- Main-chain line segments should not show small zigzags caused by port y-coordinate drift.
- Main-chain QA should compare actual port centers, not only node centers.

## Layout QA

- Main chain alignment is clean.
- Feedforward and feedback lanes remain visually separated from the main chain.
- Side-path gains are not collapsed into the main-chain lane unless explicitly intended.
- Feedforward gains that feed the same sum remain separately visible, with distinct geometries and readable labels.
- If two or more side-path gains overlap heavily, count the hidden ones as missing visual components.
- Spacing is balanced.
- Functional groups are readable.
- Empty space is not excessive.
- The layout is visually simpler than alternatives with equivalent topology.

## Style QA

- Stroke width is consistent.
- Fonts are readable and consistent.
- Arrows are consistent.
- Component sizes are coordinated.
- Catalog templates do not look mismatched.

## Required Issue Types

Use these issue types when applicable:

- `component_template_not_copied`
- `formula_rendered_as_text`
- `top_source_not_bottom_exit`
- `avoidable_upper_sum_detour`
- `jagged_main_chain`
- `negative_waypoint`
- `missing_branch_junction_dot`
- `branch_starts_at_component_output`
- `branch_junction_not_midspan`
- `duplicate_junction_dot`
- `top_input_x_misaligned`
- `ascii_alpha_label`
- `side_path_collapsed_to_main_chain`
- `lost_multilane_structure`
- `feedforward_gain_missing_or_hidden`
- `feedforward_gain_overlap`
- `selector_pattern_not_collapsed`
- `collapsed_source_drawn_twice`
