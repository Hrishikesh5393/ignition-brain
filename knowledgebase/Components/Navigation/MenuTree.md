> **Component category:** Navigation · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Menu Tree Component

**Category:** Navigation | **Palette:** Perspective - Navigation Palette
**Ignition Version:** 8.3+
**Docs source:** `perspective-components/perspective-navigation-palette/perspective-menu-tree` (verified 2026-07-13, cross-checked against 8.1 manual — 8.3 prop set unchanged aside from `backActionText` item-level override added in 8.1.24+)

> Qualified type string not directly confirmed in the fetched docs page; follows the `ia.<category>.<name>` convention (e.g. `ia.navigation.menu-tree`) inferred from other confirmed types. Verify against a real project's `view.json` before relying on it programmatically.

---

## Purpose & Description

The Menu Tree component renders a hierarchical, collapsible navigation tree — good for sidebar navigation with nested categories (e.g. `Western Region/CA/San Jose`). Unlike Horizontal Menu, Menu Tree supports drilling into a branch (replacing the visible list with that branch's children plus a "back" action) rather than a hover/click dropdown overlay.

---

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| `items` | array of objects | `[]` | ✓ | Root-level tree nodes (see Items schema below) |
| `layoutAlignment` | boolean | `false` | ✓ | Which side of the root menu submenus align to |
| `enabled` | boolean | `true` | ✓ | Enables/disables the whole component |
| `backActionText` | string | `"Back"` (approx.) | ✓ | Text shown on the prompt to return to the root menu after drilling into a branch |
| `itemStyle` | object | `{}` | ✓ | Style applied to every tree item |
| `headerStyle` | object | `{}` | ✓ | Style applied to a branch header (see `showHeader` below) |
| `backActionStyle` | object | `{}` | ✓ | Style applied to the back-navigation control |
| `style` | object | `{}` | ✓ | Style applied to the overall component container |

### Items Array Schema (`items[n]`)

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| `label.text` | string | `""` | Text displayed for the node |
| `label.icon.path` | string | — | Left-aligned icon, `"library/IconName"` format |
| `navIcon.path` | string | — | Right-aligned icon (commonly a chevron/expand indicator override) |
| `navIcon.color` | string | — | Right-aligned icon color |
| `target` | string | `""` | External URL or mounted page path. Only used when node has **no** `items` children |
| `items` | array | — | Nested child nodes; presence turns the node into a branch that drills in on click |
| `visible` | boolean | `true` | Whether the node is rendered in the tree |
| `enabled` | boolean | `true` | Whether the node can be clicked / drilled into |
| `showHeader` | boolean | `false` | Show this node's label as a header/title when its children are displayed after drilling in |
| `resetOnClick` | boolean | `false` | Clicking this item resets the Menu Tree back to the root level (useful for a "Home" node buried in a branch) |
| `backActionText` | string | inherits component-level | Per-item override of the back-button text when this node's children are shown |
| `style` | object | `{}` | Per-item style override |

---

## Navigation Patterns

```python
# Two-level hierarchical menu with icons
props.items = [
    {
        "label": {"text": "Facilities"},
        "items": [
            {"label": {"text": "Building A"}, "target": "/facilities/building-a"},
            {"label": {"text": "Building B"}, "target": "/facilities/building-b"},
        ],
    },
    {
        "label": {"text": "Reports", "icon": {"path": "material/description"}},
        "target": "/reports",
    },
]
```

```python
# Drilling reset: always-visible "Home" node inside every branch
props.items = [{
    "label": {"text": "Plant Overview"},
    "items": [
        {"label": {"text": "< Back to Root"}, "resetOnClick": True, "target": ""},
        {"label": {"text": "Line 1"}, "target": "/plant/line1"},
        {"label": {"text": "Line 2"}, "target": "/plant/line2"},
    ],
}]
```

```python
# Building a tree from tag-provider structure (script transform on props.items)
def buildNode(path):
	children = system.tag.browse(path)
	node = {"label": {"text": path.split('/')[-1]}}
	kids = [buildNode(r['fullPath']) for r in children if r['hasChildren']]
	if kids:
		node["items"] = kids
	else:
		node["target"] = "/tag-detail?path=" + path
	return node

return [buildNode("[default]Plant/AreaA"), buildNode("[default]Plant/AreaB")]
```

## Common Gotchas

- **Property path is nested for label/icon**: `label.text` and `label.icon.path`, not a flat `text`/`icon` on the item — mixing this up with Horizontal Menu's flatter `label`/`icon.path` schema is an easy copy-paste mistake between the two nav components.
- **`navIcon` vs `label.icon`**: `navIcon` is the right-aligned indicator icon (expand/drill arrow), `label.icon` is the left-aligned decorative icon. Setting only one is normal — don't assume both are required.
- **Drilling replaces the visible list**, it does not expand in place like a typical accordion tree. If you need in-place expand/collapse instead of drill-and-back, use the **Tree** component (Display palette) instead — different component, different item schema.
- **`resetOnClick` items still need a `target` key present** (even `""`) in some 8.1.x builds, or the item silently no-ops instead of resetting — always test after upgrade.
- **No built-in "currently selected" highlighting binding** — if you need to highlight the active branch based on the current view/page, you must compute it yourself (e.g. compare `session.custom.currentPath` in the item's `style` binding) rather than relying on component state.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
