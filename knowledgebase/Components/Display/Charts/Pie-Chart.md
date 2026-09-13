> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Pie Chart

**Category:** Chart | **Ignition:** ia.components.chart.pie

## Overview

The Pie Chart renders proportional slices from a flat list of name/value pairs. It supports donut-style rendering (via inner radius), slice labels, legends, and click-to-drill interaction through `onSliceClicked` events. Best suited for categorical breakdowns (downtime reason codes, production mix, OEE loss categories) rather than continuous/time-based data.

## Properties

**Verified against:** `perspective-amcharts.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| data | array/dataset | [] | ✓ | One object per slice: `{label, value}` |
| colors | array | [] | ✓ | Color palette applied to slices in data order |
| title | string | "" | ✓ | Chart title text |
| titleColor | string (color) | "" | ✓ | Title text color |
| valueFormat.showValueAsPercent | boolean | true | ✓ | Show value as % of total vs raw value |
| valueFormat.showPercentSymbol | boolean | true | ✓ | Append `%` symbol (only when `showValueAsPercent`) |
| showLabels | boolean | true | ✓ | Show per-slice labels |
| labels.showName / labels.showValue | boolean | true / true | ✓ | Toggle name/value parts of the label |
| labels.bent | boolean | false | ✓ | Bend labels around slices (disables `align`/`wrap`) |
| labels.inside.enabled | boolean | false | ✓ | Render labels inside slices below `inside.percentLimit` |
| labels.wrap.enabled | boolean | false | ✓ | Wrap long label text |
| tooltipFormat | string | `"{category} : {value.percent.formatNumber('#.0')}%"` | ✓ | Tooltip text template — supports `{category}`, `{value.value}` |
| showLegend | boolean | true | ✓ | Show/hide legend |
| legend.position | string | "bottom" | ✓ | `left`, `top`, `right`, `bottom` |
| legend.fontSize | number | 16 | ✓ | Legend label font size |
| legendLabelColor | string (color) | "" | ✓ | Legend label text color |
| cutoutRadius | number (0-100) | 0 | ✓ | % of radius cut from center — >0 makes it a donut |
| selection.enabled | boolean | false | ✓ | Enable clickable/selectable slices |
| selection.data | array (read-only) | [] | ✓ | Currently selected slice(s) |
| sectionOutline.width / .color / .opacity | number / string / number | 0 / "" / 1 | ✓ | Border around each slice |
| enableTransitions | boolean | true | ✓ | Animate data changes |
| threeDimensional | boolean | false | ✓ | 3D depth effect |
| style | object | {} | ✓ | Container CSS |

There is no `labelKey`/`valueKey`/`colorKey` remapping — the data object keys must literally be `label` and `value`. There is no `innerRadius`/`outerRadius`/`padAngle`/`cornerRadius`/`startAngle`/`sortSlices` — the only radius control is `cutoutRadius` (donut effect); slice order/rotation follow data order and aren't independently configurable.

## Data Structure Examples

```python
# Pie Chart data format — flat array of {label, value} objects (exact key names required)
data = [
    {"label": "Mechanical Failure", "value": 30},
    {"label": "Changeover", "value": 45},
    {"label": "Material Shortage", "value": 12},
    {"label": "Operator Break", "value": 8},
]

# Donut chart: set cutoutRadius = 60 (percent, not a 0-1 fraction)
```

## Binding Example

```python
# Bind data to a Named Query aggregating downtime reason codes
def transform(self, value, quality, timestamp):
    ds = system.db.runNamedQuery("Downtime/ReasonCodeSummary", {
        "lineId": self.custom.lineId,
        "shiftDate": self.custom.shiftDate,
    })
    return [
        {"label": ds.getValueAt(r, "reason_desc"), "value": ds.getValueAt(r, "total_minutes")}
        for r in range(ds.rowCount)
    ]
```

## Common Gotchas

- Data keys must be exactly `label` and `value` — there's no key-remapping property. Rename columns in the query/transform, not via a component property.
- `cutoutRadius` is a 0-100 percentage, not a 0-1 fraction — `cutoutRadius: 0.6` does almost nothing; use `60`.
- Slice click/selection uses `selection.enabled` + reading back `selection.data` — there's no dedicated `onSliceClicked` event property; wire selection through the standard property-change script on `selection.data`.
- A pie with many small-value slices (long tail of categories each <2% of total) becomes unreadable — pre-aggregate low-value categories into an "Other" bucket in the query/transform rather than passing 20+ raw rows.
- `cutoutRadius` > 0 without `showLegend` or `showLabels` leaves a donut chart with no way to identify slices — pair a non-zero `cutoutRadius` with one of them.
- `tooltipFormat` percent values come from `value.percent`, computed against the **currently rendered** data set — filtering `data` changes the percentage base.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
