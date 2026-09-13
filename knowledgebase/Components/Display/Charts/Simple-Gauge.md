> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Simple Gauge

**Category:** Chart | **Ignition:** ia.components.chart.simpleGauge

## Overview

The Simple Gauge is a minimal-configuration radial dial for displaying a single value against a min/max range with a small number of color-coded severity bands. It trades the fine-grained control of the full Gauge component (custom angles, tick counts, multiple needle styles) for a small, fast-to-configure property set — best for quick KPI/status dials where a full Gauge would be overkill.

## Properties

**Verified against:** `perspective-amcharts.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs. This component has **no severity-band coloring at all** (no low/normal/high concept) — it's a single-arc dial with a value label.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number | 0 | ✓ | Current value shown by the dial |
| minValue | number | 0 | ✓ | Scale minimum |
| maxValue | number | 100 | ✓ | Scale maximum |
| startAngle | number (deg) | 180 | ✓ | Angle where the arc begins |
| endAngle | number (deg) | 360 | ✓ | Angle where the arc ends |
| arc.width | number | 20 | ✓ | Thickness of the value arc |
| arc.color | string (color) | "#77B6D8" | ✓ | Color of the value arc |
| arc.cornerRadius | number | 0 | ✓ | Rounds the arc's edges |
| arcBackground.color | string (color) | "#77B6D8" | ✓ | Track/background color behind the arc |
| arcBackground.opacity | number (0-1) | 0.2 | ✓ | Track opacity |
| label.visible | boolean | true | ✓ | Show the numeric value label — this is the real "show value" toggle |
| label.size | number | 25 | ✓ | Label font size |
| label.color | string (color) | "#697077" | ✓ | Label text color |
| label.units | string | "" | ✓ | Unit suffix on the label |
| label.maxDecimal | number\|null | 4 | ✓ | Max decimal places shown (`null` = full precision) |
| label.offsetX / .offsetY | number | 0 / 0 | ✓ | Label position offset |
| animate | boolean | false | ✓ | Animate the arc in a sweeping motion on value change |
| style | object | {} | ✓ | Container CSS |

There is no `lowWarn`/`highWarn`/`lowColor`/`normalColor`/`highColor` — this component has a single-color arc (`arc.color`), not multi-band severity coloring at all. There's also no `label` top-level string, `units` top-level string, `valueFormat`, `showValue`, or `animation.enabled` — the value label and its formatting live entirely under the `label.*` object, and the animation toggle is the plain boolean `animate`.

## Data Structure Examples

```python
# Simple Gauge — scalar props, no dataset required
value: 68
minValue: 0
maxValue: 100
label.units: "%"
label.visible: true
```

## Binding Example

```python
# Direct tag binding — the common case for Simple Gauge
# props.value bound to: [default]Tanks/Tank1/LevelPercent
# props.maxValue could be bound to a capacity tag if the scale is dynamic per-asset
```

## Common Gotchas

- This component has **no severity-band coloring** — there is no low/normal/high concept, only a single `arc.color`. If multi-band severity coloring against a scale is needed, that's the full Gauge component's `outerAxis`/`innerAxis` config, not Simple Gauge.
- The value readout is entirely under `label.*` (`label.visible`, `label.units`, `label.maxDecimal`) — there's no separate top-level `units`/`valueFormat`/`showValue` property.
- The animation toggle is the plain boolean `animate`, not a nested `animation.enabled`.
- Because Simple Gauge has fixed-by-property (not preset-locked) `startAngle`/`endAngle`, it actually *can* be adapted to a full-circle or custom-arc sweep — unlike some other simplified gauge components, this isn't hardcoded.
- No built-in `onValueChanged` alarm/event hook — status-driven actions (e.g., flashing on high alarm) must be handled by binding `arc.color`/`style` on the component based on the same value, not from the gauge itself.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
