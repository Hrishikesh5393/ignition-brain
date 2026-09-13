> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Alarm Journal Table

**Category:** Display / General | **Ignition:** ia.display.alarmjournaltable

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| name | string | "Journal" | ✓ | Name of the configured Alarm Journal to query |
| refreshRate | number | 30000 | ✓ | Poll interval in ms |
| dateRange.mode | string | "realtime" | ✓ | `realtime` or `historical` |
| dateRange.realtime.interval / .unit | number / string | 8 / "hours" | ✓ | Rolling lookback window when `mode: "realtime"` |
| dateRange.historical.startDate / .endDate | date\|number\|null | null / null | ✓ | Fixed range when `mode: "historical"` |
| filter.text | string | "" | ✓ | Free-text filter |
| filter.events.active / .acked / .cleared / .enabled / .disabled / .system | boolean | varies | ✓ | Which event-state types to include |
| filter.priorities.diagnostic / .low / .medium / .high / .critical | boolean | varies (low/medium/high/critical default true) | ✓ | Priority pre-filters |
| filter.conditions.source / .displayPath / .provider | string | "" | ✓ | Path (wildcard `*` supported, comma-separated for multiple) / display-path / provider filters |
| toolbar.enabled / .enableDateRange / .enableFilter / .enablePreFilters / .enableConfiguration | boolean | true (all) | ✓ | Toolbar section toggles |
| dateFormat | string | "MM/DD/YYYY HH:mm:ss" | ✓ | Date display format |
| enableHeader | boolean | true | ✓ | Show table header |
| enableDetails | boolean | true | ✓ | Enable the row-details action |
| responsive.enabled / .breakpoint | boolean / number | false / 500 | ✓ | Card-style responsive layout below the breakpoint width |
| rowStyles.active/.acked/etc. | object | (priority-colored defaults) | ✓ | Per-event-state, per-priority row styling |
| sortOrder | array | — | ✓ | Column sort weighting |
| dragOrderable | boolean | — | ✓ | Allow dragging to reorder columns |
| columns / columnsAssociated | array | (default set) | ✓ | Visible column configuration |
| pager | object | — | ✓ | Pagination config (same shape as the Table component's `pager`) |
| style | object | {} | ✓ | Container CSS |

There is no `data.source`/`data.filters.*` object, `selection.data`, or `pageSize` property. The journal name is the top-level `name` property; filtering is split across `dateRange` (time window), `filter.events`/`filter.priorities` (checkbox-style pre-filters), and `filter.conditions` (path/provider text filters) — not a single `data.filters` bag; and pagination is `pager`, matching the Table component's pager shape.

## Data Binding Examples

```javascript
// Scope to a specific line, last 24 hours, high/critical only
filter.conditions.source: "Line1/*"
dateRange.mode: "realtime"
dateRange.realtime: {interval: 24, unit: "hours"}
filter.priorities: {diagnostic: false, low: false, medium: false, high: true, critical: true}

// Fixed historical window
dateRange.mode: "historical"
dateRange.historical: {startDate: {expr: "dateArithmetic(now(), -7, 'days')"}, endDate: {expr: "now()"}}

// Custom journal store (not the default)
name: "AlarmJournalArchive"
```

## Common Gotchas
- Requires a configured **Alarm Journal** (database-backed alarm history store) at the Gateway level — pointing `name` at a journal that doesn't exist returns an empty table with no error banner in the component itself.
- `filter.conditions.source`/`.displayPath` use tag-path-style wildcards (`*`) and comma-separated multi-path lists, not SQL `LIKE` syntax — a stray `%` instead of `*` silently matches nothing.
- Priority/event-state filtering is a set of individual booleans (`filter.priorities.high`, `filter.events.acked`, etc.), not an array of priority numbers or state strings.
- `dateRange.mode: "realtime"` uses a rolling window (`dateRange.realtime.interval`/`.unit`) — switch to `"historical"` for a fixed `startDate`/`endDate` range. Leaving a wide realtime window on a high-alarm-volume system can pull large result sets and be slow.
- This is historical/queryable data (a database read), distinct from the **Alarm Status Table**, which shows live/active alarms — using the wrong one for "show me currently active alarms" is a common mix-up.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
