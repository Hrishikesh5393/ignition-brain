> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Table

**Category:** Display / General | **Ignition:** ia.display.table

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| data | array/dataset | [] | ✓ | Row data — array of row objects, array of arrays, or a dataset/query result |
| columns | array | [] (auto-derived from data if empty) | ✓ | Column config objects: `{field, visible, editable, render, justify, align, sortable, width, ...}` |
| virtualized | boolean | true | ✓ | Only renders rows currently in view — leave on for large tables |
| selection.mode | string | "single" | ✓ | `single`, `single interval`, `multiple interval` |
| selection.enableRowSelection | boolean | true | ✓ | Whole-row selection |
| selection.enableColumnSelection | boolean | false | ✓ | Whole-column selection |
| selection.selectedRow | number\|null | null | ✓ (bidirectional) | Index of selected row |
| selection.data | array | [] | ✓ (bidirectional) | Array of currently-selected row objects |
| filter.enabled | boolean | false | ✓ | Enable built-in filter row |
| filter.text | string | "" | ✓ | Current filter text |
| filter.results.enabled | boolean | false | ✓ | Write filtered result back to `filter.results.data` (perf cost — avoid on large tables) |
| enableHeader | boolean | true | ✓ | Show header row |
| enableFooter | boolean | false | ✓ | Show footer row |
| enableHeaderGroups / enableFooterGroups | boolean | false | ✓ | Show multi-column header/footer groupings (needs `headerGroups`/`footerGroups`) |
| dragOrderable | boolean | true | ✓ | Let users drag column headers to reorder |
| sortOrder | array | [] | ✓ | Weighted sort order across columns |
| rows.height | string\|number | "auto" | ✓ | Minimum row height (px or "auto") |
| rows.striped.enabled | boolean | true | ✓ | Zebra-striped rows |
| cells.allowEditOn | string | "double-click" | ✓ | `single-click`, `double-click`, `long-press` |
| editingCell | object | — | ✓ | `{column, row}` of the cell currently being edited |
| nullFormat.nullFormatValue | string\|number\|null | "" | ✓ | Table-wide display value for nulls (overridable per-column) |
| pager.activeOption | number | 25 | ✓ | Rows per page (must be one of `pager.options`) |
| pager.bottom / pager.top | boolean | true / false | ✓ | Show pager above/below table |
| pager.activePage | number | 1 | ✓ | Current page |
| resizeMode | string | "fill" | ✓ | `fill` or `fixed` column resize behavior |
| emptyMessage.noData.text | string | "" | ✓ | Message shown when `data` is empty |
| headerStyle / bodyStyle / footerStyle / headerGroupStyle / footerGroupStyle | object | {} | ✓ | CSS per table section |
| style | object | {} | ✓ | Container CSS |

Column config object keys (each entry in `columns`): `field`, `visible`, `editable`, `render` (`auto`/`number`/`date`/`boolean`/`string`/`view`), `justify`, `align`, `resizable`, `sortable`, `sort`, `filter`, `width`, `strictWidth`, `numberFormat`, `dateFormat`, `viewPath`/`viewParams` (when `render: "view"`), `header`, `footer`, `style`.

## Data Binding Examples

```javascript
// Bind directly to a query
data: {query: {sql: "SELECT id, name, status FROM production_orders ORDER BY id", database: "default"}}

// Columns auto-derive from data keys when `columns` is left empty,
// but explicit config controls order/title/width:
columns: [
  {field: "id", header: {title: "Order #"}, width: 80, sortable: true},
  {field: "name", header: {title: "Product"}, width: 200, sortable: true},
  {field: "status", header: {title: "Status"}, width: 100}
]

// Row selection driving a detail panel
onSelectionChanged: function(self, event) {
  var row = self.props.selection.data[0]
  system.perspective.navigate("../order-detail", {"orderId": row.id})
}

// Status-based row coloring
rows.style: {expr: "
  switch({.status},
    'error', {'backgroundColor': 'var(--error)'},
    'warning', {'backgroundColor': 'var(--warning)'},
    {}
  )
"}
```

## Common Gotchas
- No `props.` prefix on bound paths in bindings/scripts config (`self.props.data` in scripts, yes — but the *property* itself is `data`, not `props.data`). Don't confuse the runtime object path (`self.props.X`) with the property name (`X`) when writing docs/configs.
- There is no `pagination` property — pagination is `pager` (`pager.activeOption`, `pager.top`, `pager.bottom`). There is no `showFilter` — it's `filter.enabled`.
- `selection.data` is an array of selected row objects regardless of mode — there's no separate `selectedRows` property. For single-selection, read `selection.data[0]`.
- `pager` does client-side paging over whatever's already in `data` — for genuinely large datasets, page at the SQL level (`LIMIT`/`OFFSET` in the query binding) rather than pulling everything client-side.
- Editable columns (`editable: true`) update `data` locally in the browser but do **not** write back to the source database automatically — an `onCellEdited`-style event handler must persist the change via `system.db.runUpdateQuery` or similar.
- `rows.style` expressions reference the current row via `{.fieldName}` (relative binding), not an absolute path — using an absolute path evaluates against the wrong row context.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
