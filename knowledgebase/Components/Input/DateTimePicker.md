> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# DateTime Picker Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.datetime-picker` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | string/numeric | — | ✓ | Current date/time as a Date object or epoch-millisecond timestamp. |
| formattedValue | string | — | (read-only) | Formatted display string using `format`. |
| pickerType | string | "date" | ✓ | Picker for date only, or date **and** time together. |
| minDate | string/numeric | now − 10 years | ✓ | Minimum selectable date. If left null, defaults to 10 years before today. |
| maxDate | string/numeric | now + 10 years | ✓ | Maximum selectable date. If left null, defaults to 10 years after today. |
| format | string | "MM/DD/YYYY h:mm a" | ✓ | moment.js format string. |
| locale | string | "en" | ✓ | Localization code (Designer offers a dropdown of supported locales). |
| enabled | boolean | true | ✓ | False disables all interaction with the calendar (scripts still run). |
| style | object | {} | ✓ | Full styling menu. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Bidirectional tag binding on props.value to a DateTime tag

# Expression binding to constrain the max to "today":
system.date.now()
# → bind this expression to props.maxDate to prevent future-dated selections
```

## Script/Event Handlers

```python
# Property Change Script on props.value
import system.date
if currentValue.value:
	deltaMs = system.date.now().getTime() - currentValue.value.getTime()
	if deltaMs < 0:
		system.perspective.print("Warning: future date selected")
```

## Common Gotchas
- `minDate`/`maxDate` silently default to a ±10-year window if left blank — don't assume "unbounded" when the property is empty; explicitly set both if you need to allow older/newer dates.
- Same moment.js formatting caveat as DateTime Input — `format` is NOT Java `SimpleDateFormat` syntax.
- Unlike DateTime Input, `pickerType` here only toggles between `date` and `date+time` — there's no standalone time-only variant on this component (use DateTime Input's "Time" variant for that).
- `value` from a bidirectional tag binding round-trips as a `java.util.Date`; comparing it directly to a Python `datetime` will fail — use `system.date.*` functions instead.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
