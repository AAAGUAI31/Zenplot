# Simulink Block Mapping

Use this mapping when converting paper block diagrams into `SimulinkSystemJSON`.

## Core Blocks

- External input label such as `Vin` -> `BlockType="Inport"`.
- External output label such as `BS` -> `BlockType="Outport"`.
- Triangle with numeric label -> `BlockType="Gain"` and `P Name="Gain"` set to the numeric value.
- Circle or small summing block -> `BlockType="Sum"` and `P Name="Inputs"` set from visible signs.
- Integrator box with integral sign or `1/s` -> `BlockType="Integrator"`.
- Quantizer / relay symbol -> `BlockType="Relay"`.
- Switched reference pair -> `Constant` blocks feeding a `Switch` block.
- Text note -> `Annotation`.

## Required Evidence

When the paper image does not provide exact Simulink parameters, choose the closest editable Simulink block and record the uncertainty in `evidence.unresolved`.

## Naming

Keep stable, human-readable `name` values. Keep `sid` numeric strings unique. Use `id` as a lowercase identifier derived from the Simulink name or semantic role.
