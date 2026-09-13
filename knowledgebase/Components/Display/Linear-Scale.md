> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Linear Scale

**Category:** Display / General | **Ignition:** ia.display.linear-scale

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs. This component is purely an axis/ruler with tick marks and optional indicator markers — it does not render a `value`-driven pointer itself.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| minValue | number | 0 | ✓ | Scale minimum |
| maxValue | number | 100 | ✓ | Scale maximum |
| majorTicks.span / .length / .color / .stroke | number/string/number | 20 / 20 / "" / 1 | ✓ | Major tick spacing (in scale units), length, color, stroke width |
| minorTicks.span / .length / .color / .stroke | number/string/number | 5 / 10 / "" / 1 | ✓ | Same, for minor ticks |
| fineTicks.span / .length / .color / .stroke | number/string/number | 1 / 5 / "" / 1 | ✓ | Same, for the finest tick tier |
| labels.angle | number | 0 | ✓ | Rotation of numeric tick labels |
| labels.style | object | {} | ✓ | Tick label styling |
| indicators | array | — | ✓ | Marker objects: `{label, value, color, length, stroke, opacity, indicatorStyle, labelAngle, labelColor, extent}` |
| mirror | boolean | false | ✓ | Flip scale to the opposite side |
| reverse | boolean | false | ✓ | Reverse min-to-max order |
| style | object | {} | ✓ | Container CSS |

There is no `startValue`/`endValue` (it's `minValue`/`maxValue`), no `vertical` orientation property, no `numberOfMajorTicks`/`numberOfMinorTicks` tick-count properties (ticks are configured by spacing interval — `span` — not a target count), and no `ranges` array — colored-band-style annotations are done via `indicators`, which are point/range markers with a `label`/`value`, not `{start, end, color}` bands.

## Data Binding Examples

```javascript
// Tank level indicator scale, 0-1000 gal
minValue: 0
maxValue: 1000
majorTicks: {span: 200, length: 20, stroke: 1}

// Low/high indicator markers instead of colored bands
indicators: [
  {label: "Low", value: 200, color: "#F55353", indicatorStyle: "wedge"},
  {label: "High", value: 800, color: "#CF7911", indicatorStyle: "wedge"}
]
```

## Common Gotchas
- This component has no `value` property and draws no pointer/needle itself — it's a tick-marked axis only. Pair it visually alongside a Gauge or a separately-positioned marker component if you need to show a live value against the scale.
- Tick density is set by `span` (spacing between ticks in scale units), not a target tick count — a `minValue`/`maxValue` span that doesn't divide evenly by your chosen `span` produces uneven end ticks.
- "Colored bands" aren't a thing here — use `indicators` (point markers with `indicatorStyle: "wedge"` or `"range"` and an `extent`) to call out zones, not a `{start, end, color}` array.
- No built-in alarm/threshold flashing — combine with a separate style binding on `value`-adjacent components (e.g. a Label showing the raw number) if blink/flash feedback on out-of-range values is required.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
