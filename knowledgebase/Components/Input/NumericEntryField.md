> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Numeric Entry Field Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.numeric-entry-field` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | numeric | 0 | ✓ | The numeric value, as a number or numeric string. |
| format | string | — | ✓ | Format style: `currency`, `number`, `integer`, `percent`, `scientific`, `accounting`, `duration`, `abbreviation`, `ordinal`. Locale-aware. |
| mode | string | "direct" | ✓ | Edit interaction: `Direct` (click to edit), `Protected` (double-click/long-press to edit), `Button` (popup editor). |
| align | boolean | — | ✓ | Aligns the displayed value left or right. |
| inputBounds.minimum | numeric | — | ✓ | Minimum allowable value. **Nested under `inputBounds`, not a flat `min`.** |
| inputBounds.maximum | numeric | — | ✓ | Maximum allowable value. **Nested under `inputBounds`, not a flat `max`.** |
| inputBounds.invalidStyle | object | {} | ✓ | Style applied when the entered value is outside `minimum`/`maximum`. |
| placeholder | string | "" | ✓ | Text shown when the field is empty. |
| spinner.enabled | boolean | false | ✓ | Show up/down spinner arrows when the field is selected. |
| spinner.increment | numeric | 1 | ✓ | Amount each spinner click changes the value by. |
| tooltipText | string | "" | ✓ | Tooltip shown on hover. |
| enabled | boolean | true | ✓ | Whether the user may alter the value. |
| containerStyle | object | {} | ✓ | Styling for the outer container (border, margin, padding). |
| style | object | {} | ✓ | Styling for the inner input/display area. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Bidirectional tag binding on props.value to a numeric OPC tag

# inputBounds set from expressions (e.g., dynamic setpoint range from another tag):
{[default]Line1/SetpointMin}   # → inputBounds.minimum
{[default]Line1/SetpointMax}   # → inputBounds.maximum
```

## Script/Event Handlers

```python
# Property Change Script on props.value
if currentValue.value is not None:
	if currentValue.value < self.props.inputBounds.minimum or currentValue.value > self.props.inputBounds.maximum:
		system.perspective.print("Out of range write attempted")
```

```python
# onFocus / onBlur are supported for direct-mode fields
def onBlur(self, event):
	# round to 2 decimal places on exit
	self.props.value = round(self.props.value, 2)
```

## Common Gotchas
- Bounds properties are **`inputBounds.minimum` / `inputBounds.maximum`** — NOT `min`/`max` and NOT `inputBounds.min`/`inputBounds.max`. This is the single most common mistake when configuring this component (confirmed against 8.3 docs — earlier assumptions about `inputBounds.min` are wrong).
- `mode: "Protected"` exists specifically to prevent accidental edits on touchscreens/HMIs where a stray tap shouldn't change a setpoint — don't default to `Direct` mode for safety-critical values.
- `format` affects **display only**; the underlying `value` remains a plain number — don't parse the formatted string back out for math.
- Values outside `inputBounds` are visually flagged via `inputBounds.invalidStyle` but are **not automatically clamped** — you must clamp in a Property Change Script if hard limits are required.
- `align` is documented as boolean in the official reference (left/right toggle), not a string enum like other alignment properties — don't pass `"left"`/`"right"` strings.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
