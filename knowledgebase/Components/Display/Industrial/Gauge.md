> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Gauge

**Category:** Display / Industrial | **Ignition:** ia.chart.gauge

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.value | numeric | 0 | ✓ | Primary needle value (root-level prop, not nested under an axis) |
| props.secondaryValue | numeric | 0 | ✓ | Secondary needle value (dual-needle gauges) |
| props.outerAxis.minValue | numeric | 0 | ✓ | Outer axis minimum (default max is 120) |
| props.outerAxis.maxValue | numeric | 120 | ✓ | Outer axis maximum |
| props.outerAxis.show | boolean | true | ✓ | Show/hide the outer axis ring |
| props.outerAxis.data | array | [] | ✓ | Colored range bands for the outer axis |
| props.outerAxis.needle.color | string (color) | "" | ✓ | Outer needle color |
| props.outerAxis.needle.reach | numeric | — | ✓ | How far the needle extends toward the axis ring |
| props.outerAxis.needle.origin | string | "center" | ✓ | Needle pivot origin |
| props.outerAxis.startAngle / endAngle | numeric | 180 / 360 (context-dependent) | ✓ | Arc sweep bounds — verify per instance if exact arc shape matters |
| props.innerAxis.* | object | (mirrors outerAxis, default max 80) | ✓ | Second concentric axis ring; set `innerAxis.show: false` for a single-axis gauge |
| props.backgroundColor | string (color) | "" | ✓ | Gauge face background |

*Note: real component type is `ia.chart.gauge` (chart category), not `ia.display.gauge` — confirmed from production usage.*

## Data Binding Examples

```javascript
// Single-axis gauge: hide the inner ring
props.innerAxis.show: false
props.outerAxis.minValue: 0
props.outerAxis.maxValue: 100
props.value: {tag: "[default]Line1/PressurePSI"}

// Colored range bands (nested path binding is supported)
props.outerAxis.data: [
  {from: 0, to: 40, color: "#0AA648"},
  {from: 40, to: 80, color: "#CF7911"},
  {from: 80, to: 100, color: "#F55353"}
]

// Dual-needle: compare setpoint vs actual
props.value: {tag: "[default]Line1/ActualTemp"}
props.secondaryValue: {tag: "[default]Line1/SetpointTemp"}

// Needle color reflects proximity to setpoint (bound via expression to props.style.color pattern)
props.outerAxis.needle.color: {expr: "abs({Root.Gauge.value} - {Root.Gauge.secondaryValue}) > 5 ? '#F55353' : '#0AA648'"}
```

## Common Gotchas
- The component type string is `ia.chart.gauge`, **not** `ia.display.gauge` — a common wrong guess since the Designer palette lists it under "Display."
- `value` and `secondaryValue` are root-level props, not nested under `outerAxis`/`innerAxis` — only the axis *configuration* (min/max/ranges/needle style) is nested; the actual live value binding target is `props.value`.
- Default axis maximums are asymmetric: `outerAxis.maxValue` defaults to 120, `innerAxis.maxValue` defaults to 80 — always explicitly set both when repurposing the gauge for a different range, or leftover defaults produce a misleadingly-scaled needle position.
- For a common single-ring gauge (most typical use case), remember to set `innerAxis.show: false` — leaving both axes visible when only one value is meaningful confuses operators with an idle second ring.
- Nested dotted-path bindings (e.g. binding directly into `props.outerAxis.minValue`) are fully supported — don't assume you must rebuild the whole `outerAxis` object on every binding.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
