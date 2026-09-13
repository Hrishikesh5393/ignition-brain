> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Alarm Status Table

**Category:** Display / General | **Ignition:** ia.display.alarmstatustable

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs. Note this component has **two parallel sub-trees**, `active` and `shelved`, for filters/selection — not one flat filter/selection object.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| refreshRate | number | 5000 | ✓ | Poll interval in ms |
| enableAcknowledge / enableShelve / enableUnshelve | boolean | true (all) | ✓ | Toggle each bulk action's availability — there's no single "editable" flag |
| enableDetails | boolean | true | ✓ | Enable the row-details action |
| toolbar.enableActiveTab / .enableShelvedTab | boolean | true / true | ✓ | Show the Active/Shelved tabs |
| toolbar.enableFilter / .enablePreFilters / .enableConfiguration | boolean | true (all) | ✓ | Toolbar section toggles |
| shelvingTimes | array | `[300, 900, 1800, ...]` | ✓ | Available shelve-duration options, in seconds |
| filters.active.text | string | "" | ✓ | Free-text filter on the Active tab |
| filters.active.states.activeUnacked / .activeAcked / .clearUnacked / .clearAcked | boolean | varies | ✓ | State pre-filters for the Active tab |
| filters.active.priorities.diagnostic / .low / .medium / .high / .critical | boolean | varies | ✓ | Priority pre-filters for the Active tab |
| filters.active.conditions.source / .displayPath / .provider | string | "" | ✓ | Path/provider filters (wildcard `*`, comma-separated) |
| filters.shelved.text | string | "" | ✓ | Free-text filter on the Shelved tab |
| selection.active.mode | string | "multiple" | ✓ | `single`, `multiple`, or `none` — selection mode for the Active tab |
| selection.active.data | array (read-only) | [] | ✓ | Currently-selected active alarms |
| selection.shelved.mode / .data | string / array | "multiple" / [] | ✓ | Same, for the Shelved tab |
| rowStyles.activeUnacked/etc. | object | (priority-colored defaults) | ✓ | Per-state, per-priority row styling |
| dateFormat | string | — | ✓ | Timestamp display format |
| activeSortOrder / shelvedSortOrder | array | — | ✓ | Per-tab column sort weighting |
| columns / columnsAssociated | array | (default set) | ✓ | Visible column configuration |
| pager | object | — | ✓ | Pagination config |
| style | object | {} | ✓ | Container CSS |

There is no `data.filters.*`, `selection.data`/`selection.dataMulti`, `multiSelect`, `pageSize`, or `style.row.*` — filters and selection are each split into parallel `active`/`shelved` sub-objects (this component shows both tabs at once, not one merged list), and selection mode is `selection.active.mode`/`selection.shelved.mode` (`single`/`multiple`/`none`), not a boolean `multiSelect`.

## Data Binding Examples

```javascript
// Show only active, unacknowledged, high/critical alarms for this line
filters.active.conditions.source: "Line1/*"
filters.active.states: {activeUnacked: true, activeAcked: false, clearUnacked: false, clearAcked: false}
filters.active.priorities: {diagnostic: false, low: false, medium: false, high: true, critical: true}

// Acknowledge currently-selected active alarms
onAckSelected: function(self) {
  var ids = self.props.selection.active.data.map(function(row){ return row.eventId })
  system.alarm.acknowledge(ids, "operator notes")
}

// Highlight critical unacked rows
rowStyles.activeUnacked.priorities.critical.base: {backgroundColor: "#F55353", color: "#FFFFFF"}
```

## Common Gotchas
- Shows **live/current** alarm status (active, acked, shelved) pulled from the Gateway's alarm manager — it is not a historical query like the Alarm Journal Table, and has no date-range filters.
- Filters and selection are duplicated per tab (`filters.active.*`/`filters.shelved.*`, `selection.active.*`/`selection.shelved.*`) — there is no single unified filter/selection object across both tabs.
- Acknowledge/shelve actions are performed via `system.alarm.*` scripting functions triggered from event handlers reading `selection.active.data`, not via a built-in prop toggle on the table itself — `enableAcknowledge`/`enableShelve`/`enableUnshelve` only control whether the UI action is *available*, not automatic execution.
- `filters.active.conditions.source` filters against the alarm's **source path** (the tag path); `.displayPath` matches the alarm's configured display path/label instead — mixing these up is a common cause of "my filter shows nothing."
- Security: acknowledging alarms typically requires the session's identity to hold appropriate alarm permissions at the Gateway — a read-only role can view but the ack action silently no-ops or errors depending on Gateway alarm security configuration.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
