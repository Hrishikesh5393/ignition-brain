> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Split Container

**Category:** Container / Layout | **Ignition:** ia.container.split

## Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| orientation | string | "horizontal" | `horizontal` — divider runs vertically, panels sit left/right, user drags left-right to resize. `vertical` — divider runs horizontally, panels sit top/bottom, user drags up-down to resize. |
| split.position | numeric | 0.5 | Bidirectional: current position of the divider, as a 0–1 fraction of the container's relevant dimension. Reading this updates live as the user drags; writing it programmatically repositions the divider. |
| split.size | numeric | 8 | Thickness (px) of the draggable divider bar itself |
| split.visible | boolean | true | Whether the divider bar is visibly rendered |
| split.draggable | boolean | true | Whether the user can drag the divider to resize panels at runtime. Set `false` for a fixed 2-pane split that still shows a visual divider but can't be dragged. |
| style | object | {} | Standard style object |

## Child Component Properties

The container holds **exactly two** children. Each automatically receives:

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| position.area | string | — | Which pane the child occupies. `"left"` / `"right"` when `orientation: "horizontal"`; `"top"` / `"bottom"` when `orientation: "vertical"`. |

> A third child cannot be meaningfully placed — Split Container is strictly two-pane. For 3+ resizable panes, nest a second Split Container inside one pane of the first.

## Responsive Configuration Example

```python
# Vertical split (top/bottom panes) for a details view with a
# resizable log panel below the main content
orientation = "vertical"
split.position = 0.7      # main content gets 70%, log panel 30%
split.size = 6
split.draggable = True

mainContent.position.area = "top"
logPanel.position.area = "bottom"
```

## Layout Example

```python
# Classic master-detail: list on the left, detail view on the right
orientation = "horizontal"
split.position = 0.3       # list pane starts at 30% width
split.size = 8
split.visible = True
split.draggable = True

listPanel.position.area = "left"
detailPanel.position.area = "right"

# Nest a second split inside the detail pane for a 3-pane layout:
# detailPanel itself is a Split Container with orientation: "vertical",
# holding a preview pane (top) and a properties pane (bottom)
```

## Common Gotchas

- **Exactly two children, no more.** Attempting to add a third child to a Split Container doesn't create a third pane — nest another Split Container inside one of the two existing panes instead for 3+ resizable regions.
- **`split.position` is a fraction (0–1), not pixels.** Setting `split.position = 300` expecting "300px from the left" is a common mistake — it silently clamps/misbehaves since values are expected in the 0–1 range.
- **`split.draggable: false` still shows the divider** (unless `split.visible` is also `false`) — it just becomes non-interactive. Set both `false` for a truly invisible fixed split, or just `draggable: false` for a visible-but-fixed divider (useful for a subtle visual separator that shouldn't move).
- **Orientation determines the position.area values** — flipping `orientation` from `horizontal` to `vertical` without updating each child's `position.area` (`left`/`right` vs `top`/`bottom`) leaves children with a now-invalid area value and they may not render in the expected pane.
- **No built-in min/max pane size property** confirmed in the props table — enforce minimum pane sizes via `style.minWidth`/`style.minHeight` on the child components themselves, or via a script on `split.position`'s change event that clamps the value.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
