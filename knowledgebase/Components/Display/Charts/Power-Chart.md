> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Power Chart

**Category:** Chart | **Ignition:** ia.components.chart.powerChart

## Overview

The Power Chart is the high-end industrial trend chart, modeled after the Vision Power Chart. It includes a built-in pen editor, pen table (name/color/scale/visibility toggles editable at runtime by operators), multiple Y-axes with independent scaling, and native Tag History integration — pens can be bound directly to historical tag paths without a manual query/transform. It is heavier-weight than the Time Series Chart and intended for trending screens where operators need to add/remove pens or adjust ranges interactively.

## Properties

**Verified against:** `perspective-timeseries.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`). This table reflects the real top-level property names; nested sub-fields aren't fully expanded here — check the Designer property panel for exact sub-shapes before scripting deep paths.

| Property Name | Type | Purpose |
|---|---|---|
| pens | array | Pen definitions — confirmed real, matches prior understanding |
| axes | object | Y-axis definitions — confirmed real |
| timeAxis | object | The time (X) axis configuration — **not** a separate `timeRange` object |
| plots | object | Plot area configuration |
| dataColumns | object | Column/data-source configuration for pens |
| config | object | General chart configuration — likely where toolbar/interaction toggles actually live, not a separate `toolbar` object |
| interaction | object | User-interaction configuration (pan/zoom/cursor) — **not** a separate `cursor` object |
| title | object | Chart title configuration |
| legend | object | Legend visibility/position config |
| style | object | Container CSS |

`pens` and `axes` are real, but there is no top-level `data`, `timeRange` (it's `timeAxis`), `toolbar` (toolbar-like behavior is likely under `config`), `cursor` (interaction/crosshair behavior is under `interaction`), or `annotations` property in this schema. Verify `config`/`interaction`'s exact nested shape in the Designer property panel before relying on specific sub-paths — this doc has not fully mapped those two objects.

## Data Structure Examples

> `pens` and `axes` are confirmed real top-level properties; their exact per-item shape (tag path, color, aggregation, etc.) follows the same general pattern as other Ignition history-bound chart pens, but hasn't been byte-for-byte verified against this schema dump — check the Designer property panel for exact field names before scripting pen arrays.

```python
# Conceptual — pens typically reference historical tag paths directly
pens = [
    {"tagPath": "[default]Line1/Reactor/Temperature", "axis": "tempAxis"},
    {"tagPath": "[default]Line1/Reactor/Pressure", "axis": "pressAxis"},
]
```

## Binding Example

```python
# Pens generally reference tag history paths directly, querying
# system.tag.queryTagHistory internally against the chart's active
# time window (timeAxis) — verify exact binding UI in the Designer.
```

## Common Gotchas

- Power Chart pens query Tag History **directly by tag path** — the tag must have historization enabled (`historyEnabled = true` in tag config) or the pen renders empty with no error.
- The time window property is `timeAxis`, not `timeRange` — and toolbar-like UI toggles (pen editor, export) likely live under `config`, not a separate `toolbar` object; verify exact paths in the Designer before scripting them.
- There is no confirmed `annotations` property in this schema — don't assume batch/event marker overlays exist without verifying against the Designer property panel first.
- `axes` placement (`side`/left-right) can collide when many axes share a side — verify layout doesn't overflow the container on narrow screens when using more than 2-3 axes.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
