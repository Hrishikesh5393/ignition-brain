> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# XY Chart

**Category:** Chart | **Ignition:** ia.components.chart.xyChart

## Overview

The XY Chart plots numeric X values against numeric Y values (not time-based), suitable for scatter plots, correlation plots, process curves (e.g., pump curves, calibration curves), and any dataset where the X-axis is not a timestamp. Unlike the Time Series Chart, both axes are freely numeric/continuous.

## Properties

**Verified against:** `perspective-amcharts.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`). This table reflects the real top-level property names; nested sub-fields aren't fully expanded here — check the Designer property panel for exact sub-shapes before scripting deep paths.

| Property Name | Type | Purpose |
|---|---|---|
| dataSources | object | Named data sources referenced by `series` entries — **this is the real data property**, not a flat top-level `data` array |
| series | array | Series/trace definitions, each referencing a `dataSources` entry |
| xAxes | array | X-axis definitions — an **array**, not a single `xAxis` object |
| yAxes | array | Y-axis definitions — an array, matching `xAxes`'s shape |
| title / subtitle | object | Chart title/subtitle configuration |
| legend | object | Legend visibility/position config |
| cursor | object | Hover crosshair/tooltip config |
| enableTransitions | boolean | Animate data transitions |
| scrollBars | object | Scrollbar configuration for panning |
| selection | object | Selection state/config |
| background | object | Chart background styling |
| style | object | Container CSS |

There is no top-level `data` array (it's `dataSources`, referenced by name from each `series` entry), no singular `xAxis` (it's the plural `xAxes` array, matching `yAxes`), no `zoomMode` (pan/zoom behavior lives elsewhere in this schema, not a simple mode string), and no `gridLines.x`/`gridLines.y` toggle — gridline behavior is configured within the axis objects themselves.

## Data Structure Examples

> The exact shape of `dataSources` and how `series` entries reference them isn't fully expanded in this doc — verify against the Designer property panel before authoring bindings. The example below shows the general intent (flow/head pump-curve pairs), not a byte-for-byte verified schema.

```python
# Conceptual pump-curve data
[
    {"flow": 10, "head": 95},
    {"flow": 20, "head": 90},
    {"flow": 30, "head": 82},
    {"flow": 40, "head": 70},
]
```

## Binding Example

```python
# Bind a dataSources entry to a Named Query returning flow/head pairs,
# then reference that source by name from a series entry.
def transform(self, value, quality, timestamp):
    ds = system.db.runNamedQuery("Pumps/GetCurveData", {"pumpId": self.custom.pumpId})
    rows = []
    for row in range(ds.rowCount):
        rows.append({
            "flow": ds.getValueAt(row, "flow_gpm"),
            "head": ds.getValueAt(row, "head_ft"),
        })
    return rows
```

## Common Gotchas

- There is no top-level `data` array — data lives in `dataSources`, referenced by name from each `series` entry. Don't bind a flat array directly to a nonexistent `data` property.
- Axis config is `xAxes`/`yAxes` (both arrays), not a singular `xAxis` object plus a `yAxes` map — verify the array-item shape in the Designer before scripting axis bounds.
- This is **not** a time series chart — the X-axis has no built-in time formatting; if plotting time-like values on X, they must be pre-formatted or the axis will treat them as plain numbers.
- Line-type series generally connect points in the order they're stored, not by X value — sort your source data by the X field first or the line will zig-zag.
- Selection/interaction behavior is on the `selection`/`cursor` objects — check their nested shape in the Designer property panel rather than assuming a `zoomMode` string exists (it doesn't).

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
