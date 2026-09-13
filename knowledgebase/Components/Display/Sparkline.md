> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Sparkline

**Category:** Display / General | **Ignition:** ia.display.sparkline

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| points | array/string/dataset | — | ✓ | Data to plot — flat number array, array of `{x, y}` objects, a dataset, or an `"x,y x,y"` string |
| color | string (color) | "" | ✓ | Line stroke color (`stroke` still exists but is deprecated — use `color`) |
| width | number | 0.75 | ✓ | Line stroke width (`strokeWidth` is deprecated — use `width`) |
| opacity | number | 1 | ✓ | Stroke opacity |
| dashArray | string\|number | "" | ✓ | Dash pattern for the line |
| range.high / range.low | number\|string | — | ✓ | Fixed upper/lower edge of the chart's y-scale |
| desired.high / desired.low | number\|string | — | ✓ | Desired operating band — rendered as a shaded region (`desired.stroke`/`desired.fill`) |
| marker.first / .last / .low / .high | object | shape/size/stroke/fill per marker | ✓ | Per-position marker styling (this is how min/max/endpoint highlighting is done, not a boolean) |
| style | object | {} | ✓ | Container CSS (sized small, typically inline with a Label) |

There is no `data` property (it's `points`), no `type` (`line`/`bar`/`area`) selector — this component only draws a line, there's no bar/area mode — and no `showMinMax` boolean or `fillBaseline` — min/max-style highlighting is done via the `marker.low`/`marker.high` objects, and there's no baseline-fill concept at all.

## Data Binding Examples

```javascript
// Trailing 20-sample rolling buffer from a custom prop
points: {expr: "{view.custom.tempHistory}"}

// Simple array binding from a query result column
points: {query: {sql: "SELECT value FROM readings ORDER BY t_stamp DESC LIMIT 20", database: "default"},
  transform: "script: reverseAndExtractValues"}

// Highlight low/high points with markers instead of a "showMinMax" flag
marker.low: {shape: "square", size: 6, fill: {color: "#F55353"}}
marker.high: {shape: "square", size: 6, fill: {color: "#0AA648"}}

// Color the line red if trending toward an out-of-spec condition
color: {expr: "avg({Root.Sparkline.points}) > {Root.Params.limit} ? '#F55353' : '#229AD6'"}
```

## Common Gotchas
- `points` expects a **flat numeric array** (or `{x,y}` objects/dataset), not a full query result set with multiple columns — extract the single value column via a transform script before binding if the source is a query.
- There's no `line`/`bar`/`area` type toggle — this component only ever draws a line; there is no bar or filled-area rendering mode.
- Min/max highlighting is `marker.low`/`marker.high` (styled marker objects), not a `showMinMax` boolean — and there's no `fillBaseline` since there's no area-fill mode to baseline against.
- `stroke`/`strokeWidth` still work but are deprecated in favor of `color`/`width` — use the new names in new work.
- Sparkline has no axis labels, gridlines, or tooltips by design (that's the point — a compact trend glyph, not a full chart); use the Time Series Chart component instead when axis detail or interactivity is needed.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
