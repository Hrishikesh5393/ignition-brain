> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Time Series Chart

**Category:** Chart | **Ignition:** ia.components.chart.timeseries

## Overview

The Time Series Chart plots one or more numeric "pens" against a shared time-based X-axis. It supports live tag history binding, multiple Y-axes, zoom/pan, and configurable pen styling. This is the general-purpose historical trend chart in Perspective — for interactive range selection paired with a detail chart, use the Chart Range Selector alongside it; for high-density industrial trending with built-in pen editor UI, prefer the Power Chart instead.

## Properties

**Verified against:** `perspective-timeseries.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`). This table reflects the real top-level property names; nested sub-fields aren't fully expanded here — check the Designer property panel for exact sub-shapes before scripting deep paths.

| Property Name | Type | Purpose |
|---|---|---|
| series | array | Pen/series definitions |
| plots | object | Plot area configuration (this is where axis-like plot behavior lives, not a separate `axes` map) |
| timeAxis | object | The X (time) axis configuration — singular, not `xAxisParams` |
| timeRange | object | The chart's active time range — **this is the real selection/range property**, not `selection` |
| xTrace | object | Vertical trace-line/cursor behavior |
| enablePanZoom | boolean | Enable pan/zoom interaction (replaces the invented `zoomMode`) |
| autoGenerateSeriesNames | boolean | Auto-derive series names from data columns |
| title | object | Chart title configuration |
| legend | object | Legend visibility/position config |
| defaultStyles | object | Default pen/line styling applied across series |
| style | object | Container CSS |

There is no top-level `data` property, no `axes` map (Y-axis config lives inside `plots`), no `xAxisParams` (it's `timeAxis`), no `cursor` object (crosshair behavior is `xTrace`), no `zoomMode` (it's the boolean `enablePanZoom`), and no `selection` (the active range is `timeRange`).

## Data Structure Examples

> The exact per-series data-source shape (whether each `series` entry takes its own dataset, or references a shared tag-history binding) isn't fully expanded in this doc — verify the `series` item schema in the Designer property panel before authoring complex multi-pen bindings. The examples below show the general intent, not a byte-for-byte verified schema.

```python
# Conceptual: each pen in `series` typically binds to its own Tag History
# source or shares a common time range via `timeRange`.
timeRange = {"startDate": "now-8h", "endDate": "now"}
```

## Binding Example

```python
# Bind each series entry to a Tag History source in the Designer (Binding
# dialog > Tag History), or use a Named Query / transform per series as
# needed — check the series item's own binding options rather than a single
# shared top-level `data` property (which doesn't exist on this component).
```

## Common Gotchas

- There is no top-level `data` property — series data is configured per-entry inside `series`, not as one shared row-oriented dataset (unlike Table/other components). Check each `series` entry's own data-source config in the Designer property panel.
- The active/selected time range is `timeRange`, not `selection` — bind to `timeRange` for reading or driving the chart's current window.
- Y-axis-like configuration lives inside `plots`, not a separate top-level `axes` map — mixing very different value ranges (e.g., temperature and flow rate) needs separate plot configuration, not an `axes[key]` structure.
- Zoom/pan is a single boolean, `enablePanZoom` — there's no `zoomMode` string with x/y/xy/none options.
- Crosshair/trace behavior is `xTrace`, not a `cursor` object.
- Large series data (tens of thousands of points) degrades browser rendering performance — pre-aggregate/downsample in the query (e.g., `system.tag.queryTagHistory` with `returnSize`) rather than pushing raw high-frequency data to the client.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
