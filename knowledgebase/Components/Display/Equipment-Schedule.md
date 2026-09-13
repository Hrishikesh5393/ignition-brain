> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Equipment Schedule

**Category:** Display / General | **Ignition:** ia.display.equipmentschedule

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| items | array/dataset | — | ✓ | Equipment rows: `{id, label, iconConfig, headerBackgroundColor, rowBackgroundColor, rowStyle, ...}` |
| scheduledEvents | array/dataset | [] | ✓ | Job/work events: `{itemId, eventId, startDate, endDate, label, leadTime, percentDone, backgroundColor, style, ...}` |
| downtimeEvents | array/dataset | [] | ✓ | Downtime overlay events: `{itemId, startDate, endDate, underlay, color, opacity, style}` |
| breakEvents | array/dataset | [] | ✓ | Scheduled breaks applied across all rows: `{startDate, endDate, style}` |
| dateRange.startDate / dateRange.endDate | date\|number\|null | null / null | ✓ | Visible range (invalid range defaults to one week from today) |
| defaultZoom | string | "hours" | ✓ | `month`, `day`, `12-hr`, `8-hr`, `6-hr`, `3-hr`, `hours`, `minutes` |
| addEnabled / resizeEnabled / moveEnabled / deleteEnabled / clickEnabled | boolean | true (all) | ✓ | Per-interaction UI toggles — there is no single `editable` flag, each interaction is separate |
| rowHeight | number | 46 | ✓ | Row height in px (also sets grid size) |
| selectedEvent | object `{itemId, eventId}` | — | ✓ (bidirectional) | Last-selected scheduled event |
| progressBar.enabled | boolean | true | ✓ | Show completion progress bars on scheduled events (uses `percentDone` per-event) |
| currentTimeIndicator.color / .width | string / number | "#0C7BB3" / 2 | ✓ | "Now" line styling |
| headerStyles.primaryHeaderStyle / .secondaryHeaderStyle / .tertiaryHeaderStyle | object | {} | ✓ | Header tier styling |
| rowStyle / scheduledEventStyle / downtimeEventStyle / breakEventStyle / selectedEventStyle / bodyStyle / style | object | {} | ✓ | Per-element-type CSS |

There is no `props.data`, `props.rows`, `props.startDate`/`endDate`, `props.timeScale`, or a single `editable` flag. Rows are `items`; events are split across three typed arrays (`scheduledEvents`/`downtimeEvents`/`breakEvents`); visible range is `dateRange.startDate`/`dateRange.endDate`; granularity is `defaultZoom`; and interactions are individually toggled (`addEnabled`/`resizeEnabled`/`moveEnabled`/`deleteEnabled`/`clickEnabled`).

## Data Binding Examples

```javascript
// Equipment rows
items: {query: {sql: "SELECT equipment_id AS id, equipment_name AS label FROM equipment", database: "default"}}

// Scheduled jobs per equipment
scheduledEvents: {query: {
  sql: "SELECT equipment_id AS itemId, job_id AS eventId, job_name AS label, start_time AS startDate, end_time AS endDate, pct_complete AS percentDone FROM schedule WHERE start_time >= :startDate",
  database: "default",
  parameters: {"startDate": "{Root.EquipmentSchedule.dateRange.startDate}"}
}}

// One-week view
dateRange.startDate: {expr: "now()"}
dateRange.endDate: {expr: "dateArithmetic(now(), 7, 'days')"}
defaultZoom: "day"

// Persist a drag-resized event back to the database
onEventChanged: function(self, event) {
  system.db.runUpdateQuery(
    "UPDATE schedule SET start_time=?, end_time=? WHERE id=?",
    [event.startDate, event.endDate, event.eventId]
  )
}
```

## Common Gotchas
- There's no combined `editable` flag — drag-resize, drag-move, add, delete, and click are five independent booleans (`resizeEnabled`, `moveEnabled`, `addEnabled`, `deleteEnabled`, `clickEnabled`). Turning off resize alone still allows moving unless `moveEnabled` is also `false`.
- Event objects in `scheduledEvents`/`downtimeEvents` must reference an `itemId` that exists in `items` — an orphaned event is silently dropped from the rendered chart rather than erroring.
- Interaction toggles change the UI/event-handling behavior only — persistence is entirely your responsibility via an `onEventChanged`/similar script; nothing writes back to the source query automatically.
- `breakEvents` apply across **all** rows uniformly (not per-item) — use it for shift breaks/holidays, not per-equipment downtime (that's `downtimeEvents`, which is per-`itemId`).
- Large date ranges combined with fine `defaultZoom` (`minutes`/`hours`) render a very wide timeline — pair broad ranges with coarser zoom (`day`/`month`) for usable rendering performance.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
