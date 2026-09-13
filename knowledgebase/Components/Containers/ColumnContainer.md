> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Column Container

**Category:** Container / Layout | **Ignition:** ia.container.column

## Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| breakpoints | array | 3 entries (sm/md/lg) | Named breakpoint declarations, each `{name: string, minWidth: numeric}`. When the container's width falls below a breakpoint's `minWidth`, layout rules fall back to the next lower breakpoint. |
| currentBreakpoint | string (read-only) | — | Reports the currently active breakpoint name: `"sm"`, `"md"`, or `"lg"`. **New in 8.3.4.** |
| gutters.horizontal | numeric | 10 | Horizontal spacing (px) between columns |
| gutters.vertical | numeric | 10 | Vertical spacing (px) between rows |
| style | object | {} | Standard style object |

> Built on a **12-column grid** per breakpoint — every child declares how many of the 12 columns it spans, independently at each breakpoint tier. This is the closest Ignition equivalent to a Bootstrap-style responsive grid.

## Child Component Properties

Every child stores a **separate position block per breakpoint** (sm/md/lg), so the same component can span different columns/rows at each screen size:

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| position.[breakpoint].span | numeric (1–12) | 12 | Number of the 12 grid columns this child occupies at that breakpoint |
| position.[breakpoint].colIndex | numeric | 0 | Starting column (0-based) at that breakpoint |
| position.[breakpoint].rowIndex | numeric | 0 | Row placement (0-based) at that breakpoint |
| position.[breakpoint].order | numeric | 0 | Placement order among siblings sharing a row, independent of declaration order |
| position.[breakpoint].height | numeric | auto | Component height (px) at that breakpoint |

## Responsive Configuration Example

```python
# Column Container: three named breakpoints
breakpoints = [
    {"name": "sm", "minWidth": 0},
    {"name": "md", "minWidth": 768},
    {"name": "lg", "minWidth": 1200},
]
gutters.horizontal = 16
gutters.vertical = 16

# A card that's full-width on mobile, half-width on tablet,
# a third-width on desktop
card.position.sm.span = 12
card.position.sm.colIndex = 0

card.position.md.span = 6
card.position.md.colIndex = 0

card.position.lg.span = 4
card.position.lg.colIndex = 0
```

## Layout Example

```python
# 3-card dashboard row on large screens, stacked on small screens
cardA.position.lg.span = 4
cardA.position.lg.colIndex = 0
cardA.position.lg.rowIndex = 0
cardA.position.sm.span = 12
cardA.position.sm.rowIndex = 0

cardB.position.lg.span = 4
cardB.position.lg.colIndex = 4
cardB.position.lg.rowIndex = 0
cardB.position.sm.span = 12
cardB.position.sm.rowIndex = 1

cardC.position.lg.span = 4
cardC.position.lg.colIndex = 8
cardC.position.lg.rowIndex = 0
cardC.position.sm.span = 12
cardC.position.sm.rowIndex = 2

# React to active breakpoint elsewhere:
# {view.root.currentBreakpoint} == "sm"
```

## Common Gotchas

- **Span math must total ≤12 per row per breakpoint**, or children overflow into the next row unexpectedly — always sanity-check `colIndex + span` stays within 12.
- **Each breakpoint's position values are independent** — setting `position.lg.span` does nothing for the `sm` layout; every breakpoint you support needs its own explicit values, there's no automatic fallback/inheritance between tiers beyond the container-level `minWidth` cascade.
- **Don't confuse with Breakpoint Container.** Column Container = 3 named tiers with a 12-col grid per tier, reflowing the *same* components. Breakpoint Container = exactly 2 states (`small`/`large`) swapping *entirely separate* component instances. Use Column Container when you want the same content to reflow; use Breakpoint Container when mobile and desktop need fundamentally different UI.
- **`currentBreakpoint` is read-only**, same caveat as Breakpoint Container — can't be scripted to force a layout for testing without actually resizing the container.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
