> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Tag Browse Tree

**Category:** Display / General | **Ignition:** ia.display.tagbrowsetree

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| root.path | string | "" | ✓ | Root tag provider/path to browse from — `root` is an object, not a bare string |
| filter.enabled | boolean | false | ✓ | Show/enable the filter box |
| filter.text | string\|number | "" | ✓ | Current filter text |
| selection.mode | string | "multiple" | ✓ | `single` or `multiple` — there is no separate `multiSelect` boolean |
| selection.values | array | [] | ✓ (bidirectional) | Selected tag paths, in selection order |
| display.refreshIcon.visible | boolean | true | ✓ | Show the manual-refresh icon |
| display.refreshIcon.path | string | "material/refresh" | ✓ | Icon shown for refresh |
| display.refreshIcon.style | object | {} | ✓ | Style for the refresh icon |
| style | object | {} | ✓ | Container CSS |

There is no `selection.tagPath`/`selection.tagPaths` (it's `selection.values`, a single array regardless of mode), no top-level `multiSelect` (it's `selection.mode`), no `showProviderIcons`, and `filter`/`root` are objects (`.enabled`/`.text`, `.path`) rather than plain strings.

## Data Binding Examples

```javascript
// Browse a specific provider/folder as root
root.path: "[default]Line1"

// Filter to only tags containing "Temp"
filter.enabled: true
filter.text: "Temp"

// Use selected tag to drive a value display elsewhere (single-select mode)
onSelectedItemChange: function(self, event) {
  self.getSibling("ValueLabel").props.text = self.props.selection.values[0]
}
```

## Common Gotchas
- This component browses the **live tag provider structure**, not an arbitrary data array like Tree — there is no `items` property here; configuration is done via `root`/`filter`, not a manually-built hierarchy.
- `selection.values` is always an array, even in `single` mode — read `selection.values[0]`, there's no separate scalar `tagPath` property.
- Requires the Perspective session's identity/security to have read/browse permission on the tag provider — a locked-down role sees an empty or partial tree with no explicit error.
- Selecting a **folder** (UDT instance or tag folder) vs. a leaf **tag** both populate `selection.values`, but downstream bindings expecting a scalar tag value will fail or show `null` if a folder was selected — validate the selection type (often via `system.tag.exists`/`browse`) before wiring it to a value display.
- Large tag providers (tens of thousands of tags) can be slow to fully expand — use `root.path` scoped to a relevant subfolder rather than browsing the entire provider from `[default]`.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
