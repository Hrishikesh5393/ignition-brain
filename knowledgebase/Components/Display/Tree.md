> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Tree

**Category:** Display / General | **Ignition:** ia.display.tree

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| items | array | [] | ✓ | Hierarchical node array (each a `TreeNode`: label/data/icon/nested items) |
| interactable | boolean | true | ✓ | If `false`, tree renders but cannot be interacted with |
| branchNodeSelectable | boolean | true | ✓ | If `false`, only leaf (childless) nodes are selectable |
| selection | array (of path strings) | [] | ✓ (bidirectional) | Index paths of currently selected items — this is the path array directly, not nested under `.path` |
| selectionData | array | [] | ✓ (bidirectional) | `{itemPath, value}` for each currently-selected item — this is where the node's data payload actually lives, not `selection.data` |
| appearance.textOverflow | string | "scroll" | ✓ | `scroll` or `truncate` for overflowing labels |
| appearance.expandIcons.collapsed / .expanded / .empty | icon config | — | ✓ | Icons for collapsed/expanded/leaf nodes |
| appearance.defaultNodeIcons.expanded / .collapsed / .empty | icon config | — | ✓ | Default per-node icons |
| appearance.selectedStyle / .unselectedStyle | object | {} | ✓ | Styling for selected vs. unselected nodes |
| appearance.rowHeight | number | 24 | ✓ | Row height in px |
| style | object | {} | ✓ | Container CSS |

There is no top-level `selection.data`/`selection.path` object, no `expanded` property, and no `editable` property. Selection is two separate top-level properties (`selection` = path array, `selectionData` = data-with-path array); there's no built-in expand-state tracking or inline-rename feature at all.

## Data Binding Examples

```javascript
// Static equipment hierarchy
items: [
  {label: "Line 1", items: [
    {label: "Station A", data: {tagPath: "[default]Line1/StationA"}},
    {label: "Station B", data: {tagPath: "[default]Line1/StationB"}}
  ]}
]

// Build tree from a query using a transform script (flat rows -> nested items)
items: {query: {sql: "SELECT id, parent_id, name FROM equipment", database: "default"},
  transform: "script: buildTreeFromRows"}

// React to node selection
onSelectedItemChange: function(self, event) {
  var node = self.props.selectionData[0]
  system.perspective.navigate("../equipment-detail", {"tagPath": node.value.tagPath})
}
```

## Common Gotchas
- Selection data lives in `selectionData` (an array of `{itemPath, value}`), **not** `selection.data` — `selection` itself is only the array of index-path strings.
- There is no `editable`/inline-rename feature and no `expanded` property to read or drive expand/collapse state programmatically.
- `items` must already be nested (parent objects containing an `items` array of children) — a flat list of rows from a query does **not** auto-nest; a script transform is required to build the hierarchy from `parent_id`-style relational data.
- Deeply nested trees (thousands of nodes) with `items` fully bound and re-evaluated on every tag change can be a performance bottleneck — prefer lazy-loading children where possible for large hierarchies.
- `branchNodeSelectable: false` disables selecting parent/folder nodes entirely — only terminal (childless) nodes become selectable.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
