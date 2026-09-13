> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Chart Range Selector

**Category:** Chart | **Ignition:** ia.components.chart.rangeSelector

## Overview

The Chart Range Selector is a compact overview strip showing a full data timeline with a draggable/resizable selection window, typically placed beneath a Time Series Chart or Power Chart to let users brush-select a sub-range for detailed viewing. It outputs the selected time range via a bidirectional `selection` property, which is bound into the detail chart's time range input. It does not render detailed pen data itself in most configurations — it's a navigation/overview control, not a primary trend display.

## Properties

**Verified against:** `perspective-timeseries.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`). The property table below reflects the real top-level property names; the nested shape of each isn't fully expanded here — check the Designer property panel for the exact sub-fields before scripting deep paths.

| Property Name | Type | Purpose |
|---|---|---|
| data | array/dataset | Overview data used to draw the background trace |
| enablePanZoom | boolean | Enable pan/zoom interaction on the overview strip |
| selectedRange | object | The currently-selected time range (bidirectional) — **this is the real selection property**, not `selection` |
| brushRange | object | The full brushable domain of the overview timeline |
| timeAxis | object | Time-axis configuration for the overview strip |
| yAxis | object | Y-axis configuration for the overview trace |
| areaStyles | object | Styling for the selected-vs-unselected shaded regions — **this is where selection/overlay coloring lives**, not separate `overlayColor`/`brushColor` properties |
| style | object | Container CSS |

There is no `series`, `domain`, `minRange`/`maxRange`, `handleStyle`, `overlayColor`/`brushColor`, `snapToPoints`, or `presets` property. The real names are `selectedRange` (not `selection`), `brushRange` (not `domain`), and `areaStyles` (not separate overlay/brush color properties). There's also no built-in quick-select preset buttons — those would need to be built as separate Button components that write to `selectedRange`.

## Data Structure Examples

```python
# Overview data — usually a coarser/downsampled trace to keep the overview lightweight
data = [
    {"timestamp": 1720780800000, "temperature": 71.0},
    {"timestamp": 1720800000000, "temperature": 72.4},
    {"timestamp": 1720820000000, "temperature": 74.1},
]
```

## Binding Example

```python
# Wire the range selector's output into a detail chart's query window.
# selectedRange is bidirectional (user drags it; scripts can also set it).

def transform(self, value, quality, timestamp):
    ds = system.tag.queryTagHistory(
        paths=["[default]Line1/Reactor/Temperature"],
        startDate=system.date.fromMillis(value["start"]),
        endDate=system.date.fromMillis(value["end"]),
        returnSize=1000,
        aggregationMode="Average",
    )
    return [{"timestamp": r["t_stamp"], "temperature": r["Temperature"]} for r in ds]

# Bind the detail chart's data-query binding, parameterized by
# RangeSelector.props.selectedRange (not "selection").
```

## Common Gotchas

- `selectedRange` (not `selection`) is bidirectional — a one-way binding means user drags won't propagate back to whatever consumes the selection, silently breaking the linked detail chart.
- `brushRange` (not `domain`) defines the full brushable extent of the overview timeline — it must bound the full range of `data`, or the overview trace gets clipped/misaligned with the draggable handles.
- Selection-window and overlay coloring live under `areaStyles`, not separate `overlayColor`/`brushColor` properties.
- The overview `data` is a separate dataset from the detail chart's data — using the exact same high-resolution query for both wastes bandwidth; downsample for the range selector's `data` since it only needs to convey overall shape.
- This component does not itself perform historian queries for the detail view — it only emits a range via `selectedRange`; forgetting to wire that into an actual data-fetching binding on a companion chart results in a range selector that visually works but has no effect on any other component.
- There are no built-in quick-select preset buttons ("Last 1h", etc.) — build those as separate Button components that write to `selectedRange` directly.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
