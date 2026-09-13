> **Component category:** Navigation · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Horizontal Menu Component

**Category:** Navigation | **Palette:** Perspective - Navigation Palette
**Ignition Version:** 8.3+
**Docs source:** `perspective-components/perspective-navigation-palette/perspective-horizontal-menu` (verified 2026-07-13)

> Qualified type string (`ia.navigation.horizontal-menu` or similar) follows the confirmed `ia.<category>.<name>` convention seen elsewhere (`ia.container.flex`, `ia.chart.gauge`, `ia.input.button`) but was **not directly confirmed** in the docs page fetched for this reference — verify against a real project's `view.json` (`grep -rn '"type": "ia\.' <project>`) before relying on it in scripting/import contexts.

---

## Purpose & Description

The Horizontal Menu component builds a top-level, horizontally-arranged navigation bar out of a configurable `items` array. Each item can link to a page/mounted path or an external URL, or expand a dropdown submenu of child items on hover/interaction. When items overflow the component's width, left/right scroll arrows appear automatically — no scroll property to configure.

---

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| `items` | array of objects | `[]` | ✓ | Root-level menu items (see Items schema below) |
| `enabled` | boolean | `true` | ✓ | Enables/disables the whole component |
| `itemStyle` | object | `{}` | ✓ | Style applied to every item (text, background, margin, padding, border, shape) |
| `style` | object | `{}` | ✓ | Style applied to the overall component container |

### Items Array Schema (`items[n]`)

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| `label` | string | `""` | Text displayed for the item |
| `target` | string | `""` | External URL (`http://example.com`) or mounted page path (`/my-page`). Only used when the item has **no** `items` children — if children exist, click opens the submenu instead of navigating |
| `icon.path` | string | — | Icon shown left of the label, format `"library/IconName"` (e.g. `material/home`) |
| `icon.color` | string | — | Icon color |
| `enabled` | boolean | `true` | Whether the item can be clicked / its submenu opened |
| `items` | array | — | Nested child items; presence of this array turns the item into a dropdown trigger instead of a direct link |
| `style` | object | `{}` | Per-item style override |

---

## Navigation Patterns

```python
# Static top-level bar with a dropdown
props.items = [
    {"label": "Home", "target": "/home"},
    {
        "label": "Products",
        "items": [
            {"label": "Widgets", "target": "/products/widgets"},
            {"label": "Gadgets", "target": "/products/gadgets"},
        ],
    },
    {"label": "Docs", "target": "https://docs.inductiveautomation.com", "icon": {"path": "material/menu_book"}},
]

# Disable a menu item based on role
props.items[2]['enabled'] = 'admin' in system.security.getRoles()
```

```python
# Building items dynamically from a dataset binding (expression/script transform)
# transform script on props.items, input = a named query result
value = []
for row in range(0, len(input)):
    value.append({
        "label": input.getValueAt(row, "displayName"),
        "target": "/dept/" + input.getValueAt(row, "deptSlug"),
    })
return value
```

## Common Gotchas

- **No `target` property at the top component level** — target/navigation URL lives *inside each item*, not as a component prop. Confusing this with the Link component's `props.target` (self/tab/parent/top) is a common mistake; Horizontal Menu items only take a page path or external URL string, no window-target option per item.
- **Items with children never navigate directly.** If an item object has a non-empty `items` array, its own `target` is ignored — clicking opens the submenu. To make a parent item both navigable *and* have a dropdown, there's no built-in way; use a duplicate "overview" child item instead.
- **Icon path format is strict**: `"library/IconName"` (e.g. `material/home`), not a raw SVG path or bare icon name.
- **Mounted paths vs. view paths**: `target` expects the *page's mounted URL* (as configured in Page Configuration), not the Perspective view resource path. Confusing this with `Embedded View`'s `path` property (which *is* a view resource path) is a frequent source of "link goes nowhere" bugs.
- Overflow scrolling is automatic and has no exposed property — you cannot force wrap-to-multiple-rows; only left/right scroll arrows appear once items exceed the component width.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
