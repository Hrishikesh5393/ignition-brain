> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Markdown (Viewer)

**Category:** Display / General | **Ignition:** ia.display.markdown

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| source | string | "" | ✓ | Raw markdown source to render — the property is `source`, not `text` |
| sectionSpacing | number | 24 | ✓ | Pixels of vertical space between sections/headers |
| markdown.escapeHtml | boolean | true | ✓ | Escape (don't render) raw HTML — set `false` only for trusted content |
| markdown.skipHtml | boolean | false | ✓ | Skip inline/block HTML entirely instead of escaping it |
| markdown.disallowedTypes | array | [] | ✓ | Node types to suppress (e.g. `image`, `table`) |
| markdown.unwrapDisallowed | boolean | false | ✓ | Keep disallowed nodes' text content instead of dropping it entirely |
| markdown.sourcePos | boolean | false | ✓ | Track source position (debugging) |
| style | object | {} | ✓ | Container CSS |

There is no `linksInNewTab`, `scrollable`, or generic `parserOptions.*` — the parser config lives under `markdown.*` with a specific fixed set of keys (`escapeHtml`, `skipHtml`, `disallowedTypes`, `unwrapDisallowed`, `sourcePos`); there's no `breaks`/`linkify` toggle in this schema.

## Data Binding Examples

```javascript
// Static help text
source: """
# Startup Procedure
1. Verify E-stop is released
2. Confirm air pressure > 80 PSI
3. Press **Start**
"""

// Bind to a tag holding operator instructions (String/Text tag)
source: {tag: "[default]Line1/WorkInstructions"}

// Compose markdown dynamically from an expression
source: {expr: "'## Batch ' + {Root.Params.batchId} + '\\n\\nStatus: **' + {Root.Status.value} + '**'"}

// Load from a named query returning a text blob
source: {query: {namedQuery: "Docs/GetSOPMarkdown", parameters: {"docId": "{Root.Params.docId}"}}}
```

## Common Gotchas
- This is a **read-only viewer** — for operator-editable rich text, use the separate Markdown Editor component (Input category), not this one.
- `markdown.escapeHtml` defaults to `true` (safe) — only set it to `false` for fully trusted, non-user-generated content, since disabling it renders raw embedded HTML.
- No `linksInNewTab`/`scrollable` toggle exists — link target behavior and overflow scrolling aren't independently configurable component properties here; control overflow via `style`.
- Very large markdown strings (megabyte-scale SOP documents) can cause noticeable render lag; page or paginate long documents instead of dumping the whole file into `source`.
- Binding `source` from a query result requires the column to already be a single concatenated string — the component does not iterate rows.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
