> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# DateTime Input Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.datetime-input` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | string/numeric | — | ✓ | Current date/time as a Date object or epoch-millisecond timestamp. |
| formattedValue | string | — | (read-only) | The date/time rendered using `format`. |
| pickerType | string | "date" | ✓ | Which picker to show/enable: date only, time only, or both. |
| minDate | string/numeric | — | ✓ | Minimum selectable date/time (Date object or ms timestamp). |
| maxDate | string/numeric | — | ✓ | Maximum selectable date/time. |
| format | string | "MM/DD/YYYY" | ✓ | Display format — must be a **valid moment.js format string**, e.g. `"MM/DD/YYYY h:mm a"`. |
| locale | string | "en" | ✓ | Localization code for language/formatting. |
| enabled | boolean | true | ✓ | Disables calendar interaction when false (scripts still run). |
| placeholder | string | "" | ✓ | Text shown when no date/time selected. |
| dismissOnSelect | boolean | true | ✓ | Whether the picker popup closes immediately after a date is chosen. |
| inputProps | object | {} | ✓ | Styling for the text input portion (text, background, margin/padding, border, shape). |
| modalStyle | object | {} | ✓ | Styling applied to the popup calendar modal itself. |
| style | object | {} | ✓ | Component-level styling. |

Pre-configured Designer variants: **Date and Time** (full calendar + time), **Time** (up/down arrow time-only picker).

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Tag binding on props.value — bind directly to a DateTime-type tag, bidirectional

# Expression reading the formatted value into a Label elsewhere:
{Root.DateTimeInput.props.formattedValue}
```

## Script/Event Handlers

```python
# Property Change Script on props.value
if currentValue.value is not None:
	# currentValue.value is a java.util.Date — convert for comparisons
	system.perspective.print("Selected: " + str(currentValue.value))
```

```python
# Component Event Script: onFocus / onBlur are supported since this is a text-entry-backed picker
def onBlur(self, event):
	if self.props.value is None:
		self.props.value = system.date.now()
```

## Common Gotchas
- `format` must be **moment.js** tokens (`YYYY`, `MM`, `DD`, `h`, `mm`, `a`), not Java `SimpleDateFormat` tokens (`yyyy`, `dd`) — mixing the two silently mis-renders the string.
- `value` is not the display string — use `formattedValue` (read-only) whenever you need the formatted text, don't try to reformat `value` yourself in an expression.
- `pickerType` controls date vs. time vs. both — forgetting to set it to `"both"` is why time selection sometimes "doesn't show up" for developers expecting DateTime Picker-like behavior.
- For a true combined date+time picker with a single popup calendar, prefer the **DateTime Picker** component — DateTime Input's time-only variant uses spinner arrows, not a calendar.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
