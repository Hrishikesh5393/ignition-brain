> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Simple Gauge

**Category:** Display / Industrial | **Ignition:** ia.display.simple-gauge

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.value | numeric | 0 | ✓ | Needle/pointer value |
| props.startValue | numeric | 0 | ✓ | Scale minimum |
| props.endValue | numeric | 100 | ✓ | Scale maximum |
| props.ranges | array | [] | ✓ | Colored bands: `{start, end, color, label}` |
| props.numberOfMajorTicks | numeric | 5 | ✓ | Labeled tick count |
| props.numberOfMinorTicks | numeric | 4 | ✓ | Minor ticks between majors |
| props.startAngle / props.endAngle | numeric | 225 / -45 (typical) | ✓ | Arc sweep bounds |
| props.style | object | {} | ✓ | Container CSS |

*This is the simplified, lighter-weight sibling of the full `ia.chart.gauge` — fewer configuration knobs (no dual-axis/dual-needle), intended for quick single-value dial displays.*

## Data Binding Examples

```javascript
// Basic 0-100% dial
props.startValue: 0
props.endValue: 100
props.value: {tag: "[default]Line1/OEEPercent"}

// Color bands for a speed dial
props.ranges: [
  {start: 0, end: 30, color: "#767676", label: "Idle"},
  {start: 30, end: 80, color: "#0AA648", label: "Normal"},
  {start: 80, end: 100, color: "#F55353", label: "Overspeed"}
]

// Bind range bands dynamically from a recipe's operating envelope
props.ranges: {expr: "
  [{'start':0,'end':{Root.Recipe.lowLimit},'color':'#767676'},
   {'start':{Root.Recipe.lowLimit},'end':{Root.Recipe.highLimit},'color':'#0AA648'},
   {'start':{Root.Recipe.highLimit},'end':{Root.SimpleGauge.endValue},'color':'#F55353'}]
"}
```

## Common Gotchas
- Choose Simple Gauge over the full Gauge component when only a single needle/value on a single scale is needed — it renders faster and has a much smaller prop surface, which matters when placing many gauges on one overview screen.
- `ranges` bounds must stay within `startValue`/`endValue` — a range extending past `endValue` is clipped/ignored rather than extending the visible scale.
- Unlike the full Gauge, there is no `secondaryValue`/dual-needle support — for setpoint-vs-actual comparison, either use the full Gauge or overlay a Linear Scale marker alongside this component.
- Verify `startAngle`/`endAngle` defaults in Designer preview before relying on them for a specific look — sweep-angle defaults vary slightly by Ignition version and are worth confirming visually rather than assuming.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
