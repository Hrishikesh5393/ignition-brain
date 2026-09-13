> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Flex Repeater

**Category:** Embedding | **Ignition:** `ia.display.flex-repeater`

## Overview

Renders many instances of the **same** view, one per entry in `instances`, laid out in a flex row/column — the standard way to repeat a card/row template over a dataset (e.g. one instance per equipment item) without manually placing an Embedded View per row.

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| path | string | "" | ✓ | View path rendered once per entry in `instances` |
| instances | array | [] | ✓ | One entry per repeated instance — each becomes that instance's view params, plus `instanceStyle`/`instancePosition` overrides |
| direction | string | "row" | ✓ | `row`, `row-reverse`, `column`, `column-reverse` |
| wrap | string | "nowrap" | ✓ | `nowrap`, `wrap`, `wrap-reverse` |
| justify | string | "flex-start" | ✓ | Main-axis alignment |
| alignItems | string | "stretch" | ✓ | Cross-axis alignment |
| alignContent | string | "stretch" | ✓ | Cross-axis alignment when wrapped |
| useDefaultViewWidth / useDefaultViewHeight | boolean | true / true | ✓ | Use each view's own default size instead of flex-sizing |
| elementStyle | object | {} | ✓ | Style applied to every repeated instance |
| elementPosition | object | `{grow:1, shrink:1, basis:0}` | ✓ | Flex position applied to every repeated instance |
| loading.order | string | "after-parent" | ✓ | `after-parent` or `with-parent` |
| style | object | {} | ✓ | Container CSS |

## Data Binding Examples

```javascript
// One instance per row of a query
instances: {query: {sql: "SELECT id, name FROM equipment", database: "default"}}

// path points at a reusable card view; each instance's row fields
// (id, name) become that instance's view params automatically
path: "embedded/EquipmentCard"
```

## Common Gotchas
- `instances` entries become the repeated view's **params** directly — the row's own fields (whatever the query/array returns) are passed in as `view.params.*`, plus each instance can carry its own `instanceStyle`/`instancePosition` to override the shared `elementStyle`/`elementPosition`.
- `useDefaultViewWidth`/`useDefaultViewHeight` default to `true` here (unlike Embedded View, where they default to `false`) — repeated instances use their own natural size by default rather than stretching to fill.
- Large `instances` arrays (hundreds+) with heavy per-instance views can be a performance bottleneck — same caution as many manually-placed Embedded Views, just generated instead of hand-placed.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
