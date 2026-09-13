> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Thermometer

**Category:** Display / Industrial | **Ignition:** ia.display.thermometer

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number | 25 | ✓ | Current fill level (temperature value) |
| lowBound | number | 0 | ✓ | Scale minimum |
| highBound | number | 100 | ✓ | Scale maximum |
| unit | string | "C" | ✓ | Unit label shown next to the value |
| intervals | array | — | ✓ | Colored band segments: `{low, high, color}` |
| thermometerColor | string (color) | "" | ✓ | Glass/tube outline color |
| mercuryColor | string (color) | "" | ✓ | Fill column color (used when `intervals` is empty) |
| axisLabelColor | string (color) | "" | ✓ | Scale tick label color |
| strokeWidth | number | 2 | ✓ | Outline stroke thickness |
| valueFontColor | string (color) | "" | ✓ | Numeric value text color |
| valueFont | object | {fontSize: 25} | ✓ | Style block for the numeric value text |
| style | object | {} | ✓ | Container CSS (component is tall/narrow by default) |

There is no `startValue`/`endValue` (it's `lowBound`/`highBound`), no `ranges` (it's `intervals`, with keys `low`/`high`/`color` not `start`/`end`/`color`), no `fillColor` (it's `mercuryColor`), and no `numberOfMajorTicks` property — tick count isn't independently configurable.

## Data Binding Examples

```javascript
// Process temperature, °C scale
lowBound: 0
highBound: 200
unit: "C"
value: {tag: "[default]Oven1/Temperature"}

// Color the fill red once above a safe limit
mercuryColor: {expr: "{Root.Thermometer.value} > 180 ? '#F55353' : '#229AD6'"}

// Banded intervals (normal/warning/danger zones on the glass)
intervals: [
  {low: 0, high: 150, color: "#0AA648"},
  {low: 150, high: 180, color: "#CF7911"},
  {low: 180, high: 200, color: "#F55353"}
]
```

## Common Gotchas
- Purely a **vertical linear fill indicator styled as a thermometer** — it has no unit-conversion logic (`unit` is display-only text, not a conversion trigger); if the source tag is in °F but `lowBound`/`highBound` are authored for °C, values render at the wrong height with no warning. Convert in an expression/transform before binding if unit mismatch is possible.
- `intervals` (if set) take precedence over `mercuryColor` for how the fill column is colored — setting both and expecting `mercuryColor` to apply is a common misconfiguration.
- `intervals` keys are `low`/`high`/`color`, not `start`/`end`/`color` — using the wrong keys silently fails schema validation for that entry.
- Component aspect ratio defaults to tall/narrow; forcing it into a wide container via `style` width/height overrides can visually break the bulb-at-bottom thermometer shape — keep height significantly greater than width.
- No built-in alarm blink on out-of-range — pair with an expression-bound `mercuryColor`/`style` change (as above) for visual alerting, since the component itself doesn't threshold-alert automatically.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
