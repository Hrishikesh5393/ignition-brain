> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Gauge

**Category:** Chart | **Ignition:** ia.components.chart.gauge

## Overview

The Gauge is a fully-configurable radial (or linear) dial component for displaying a single scalar value against a scaled range, with support for colored zones (e.g., normal/warning/critical bands), major/minor tick marks, and a needle/pointer. It is more heavily configurable than the Simple Gauge, at the cost of more properties to set up. Use Gauge when zone coloring, custom tick styling, or non-standard angle sweeps are required; use Simple Gauge for a quick minimal-config dial.

## Properties

**Verified against:** `perspective-amcharts.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs. This component is much simpler than previously documented — it has no `zones`, `thresholds`, `needle`, or tick-count properties at all.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number | 0 | ✓ | Primary value shown on the outer axis |
| secondaryValue | number | 0 | ✓ | Optional second value, shown on the inner axis |
| startAngle | number (deg) | 180 | ✓ | Angle where the scale begins |
| endAngle | number (deg) | 360 | ✓ | Angle where the scale ends |
| outerAxis | object (AxisConfig) | — | ✓ | Configuration for the outer scale/needle (range, ticks, bands — see nested AxisConfig schema) |
| innerAxis | object (AxisConfig) | — | ✓ | Same, for the secondary/inner scale |
| backgroundColor | string (color) | — | ✓ | Background fill within the gauge |
| animate | boolean | false | ✓ | Animate needle in a sweeping motion on value change (not `animation.enabled`) |
| reverseScale | boolean | false | ✓ | Reverse min-to-max direction on the dial |
| style | object | {} | ✓ | Container CSS |

There is no `minValue`/`maxValue` at the top level (range is configured inside `outerAxis`/`innerAxis`), no `shape`, `label`/`valueLabel`, `majorTicks`/`minorTicks`, `zones`, `needle`, `animation.duration`, or `thresholds` property — colored bands and range configuration all live inside the `outerAxis`/`innerAxis` objects, not as flat top-level arrays. For a much simpler gauge with a plain single arc, see Simple Gauge instead — it does not have the `outerAxis`/`innerAxis` dual-scale structure this component does.

## Data Structure Examples

```python
# Gauge does not take a dataset — value/config are scalar props.
value: 72.4
startAngle: 180
endAngle: 360
animate: true

# Range/band configuration lives inside outerAxis, not top-level zones —
# inspect the AxisConfig sub-schema (via Designer property panel) for the
# exact min/max/band structure before authoring dynamic band bindings.
```

## Binding Example

```python
# Direct tag binding — simplest case
# props.value bound to: [default]Line1/Reactor/Temperature
```

## Common Gotchas

- There's no flat `zones`/`thresholds` array — banded coloring and scale range are configured inside `outerAxis`/`innerAxis`, which this doc doesn't fully expand (check the Designer property panel's Axis Config editor for the exact nested shape before scripting bindings against it).
- The animation toggle is `animate` (boolean), not `animation.enabled`/`animation.duration` — there's no separate duration property.
- `secondaryValue` only renders meaningfully if `innerAxis` is configured — setting it with no inner axis config has no visible effect.
- Gauge has no historical trending capability — it always shows only the current bound `value`; pair with a Time Series Chart or Sparkline if trend context is also needed on the same screen.
- For a simpler single-arc dial without the dual outer/inner axis structure, use Simple Gauge instead.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
