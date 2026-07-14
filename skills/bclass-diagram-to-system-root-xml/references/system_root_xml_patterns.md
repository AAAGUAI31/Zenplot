# system_root.xml Patterns

This skill emits only the core `<System>...</System>` element used inside `simulink/systems/system_root.xml`.

## Block

```xml
<Block BlockType="Gain" Name="0.8 input" SID="2">
  <P Name="Position">[110, 226, 160, 284]</P>
  <P Name="ZOrder">2</P>
  <P Name="Gain">0.8</P>
</Block>
```

Preserve all block `P` parameters. Store `Position` as four integers in JSON and emit it back in bracket form.

## PortCounts

```xml
<PortCounts in="3" out="1"/>
```

Use for blocks where the source XML includes it, especially `Sum` and `Integrator`.

## Line And Branch

```xml
<Line>
  <P Name="ZOrder">10</P>
  <P Name="Src">4#out:1</P>
  <P Name="Points">[60, 0]</P>
  <Branch>
    <P Name="Dst">5#in:1</P>
  </Branch>
  <Branch>
    <P Name="Points">[0, -150]</P>
    <P Name="Dst">10#in:1</P>
  </Branch>
</Line>
```

Represent nested branches recursively in JSON. Preserve `Src`, `Dst`, `Points`, and `ZOrder`.

## Annotation

Annotations contain `SID` plus `P` parameters, usually `Name`, `Position`, `InternalMargins`, and `ZOrder`.
