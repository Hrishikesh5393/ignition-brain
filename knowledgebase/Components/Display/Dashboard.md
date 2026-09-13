> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Dashboard

**Category:** Display / General | **Ignition:** `ia.display.dashboard`

## Overview

The Dashboard component is a runtime-configurable widget grid — operators can add, remove, resize, and rearrange embedded-view "widgets" from a catalog while a session is running, similar to a customizable home screen. It's distinct from manually laying out Embedded Views in a Coordinate/Flex Container, which is fixed at design time.

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| grid | string | "stretch" | ✓ | `fixed` (pixel cell size) or `stretch` (grid fills available space) |
| pack | boolean | true | ✓ | Auto-arrange widgets into an optimal layout vs. free placement |
| isEditing | boolean | false | ✓ (bidirectional) | Whether the dashboard is currently in runtime edit mode |
| editingToggle | boolean | true | ✓ | Show the built-in edit-mode toggle control |
| fixed.cellSize / .rowCount / .columnCount / .rowGutterSize / .columnGutterSize | number | 100 / 10 / 10 / 6 / 6 | ✓ | Grid geometry when `grid: "fixed"` |
| stretch.rowCount / .columnCount / .rowGutterSize / .columnGutterSize | number | 8 / 8 / 6 / 6 | ✓ | Grid geometry when `grid: "stretch"` |
| widgets | array | [] | ✓ | Widgets currently placed on the dashboard: `{name, viewPath, viewParams, isConfigurable, header, body, minSize, position, style}` |
| widgets[].position.rowStart / .rowEnd / .columnStart / .columnEnd | number | — | ✓ | Grid placement of this widget |
| widgets[].minSize.columnSpan / .rowSpan | number | 1 / 1 | ✓ | Minimum allowed size when resizing |
| availableWidgets | array | [] | ✓ | Catalog of widgets an operator can add — each `{viewPath, viewParams, category, name, defaultSize, minSize, header, body, style}` |
| style | object | {} | ✓ | Container CSS |

## Common Gotchas
- Widgets are embedded views (`viewPath`/`viewParams`), placed via `widgets[].position` — the "catalog" operators pick from at runtime is the separate `availableWidgets` array, not `widgets` itself.
- `isEditing` is bidirectional and controls whether operators can currently drag/resize/add/remove — set it `false` (with `editingToggle: false`) to lock a dashboard down for a read-only display.
- `grid: "fixed"` uses `fixed.*` config (pixel cell size); `grid: "stretch"` uses `stretch.*` config instead — only one of the two sub-objects is active at a time, per the `grid` setting.
- Widget-level `isConfigurable` exposes a per-widget config toggle to the operator; this is separate from the whole-dashboard `isEditing` layout-editing mode.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
