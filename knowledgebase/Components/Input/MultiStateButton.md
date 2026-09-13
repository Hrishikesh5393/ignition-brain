> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Multi-State Button Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.multi-state-button` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| controlValue | numeric | — | ✓ | Bind this to the Tag/value that **controls** the state (write target). |
| indicatorValue | numeric | — | ✓ | Bind this to the Tag/value that **indicates** the current state (read/feedback). |
| states | array | [] | ✓ | Array of state objects: `{text, value, selectedStyle, unselectedStyle, tooltipText}`. |
| states[].text | string | — | ✓ | Display text for that state's button. |
| states[].value | numeric | — | ✓ | Value written to `controlValue` when that button is clicked. |
| states[].selectedStyle | object | {} | ✓ | Style applied when this state is currently active. |
| states[].unselectedStyle | object | {} | ✓ | Style applied when this state is not active. |
| states[].tooltipText | string | "" | ✓ | Hover tooltip for that specific state button (must be added manually per state). |
| orientation | boolean | — | ✓ | Physical arrangement: column or row (boolean-backed, like Slider). |
| defaultSelectedStyle | object | {} | ✓ | Fallback style for selected buttons that don't define their own `selectedStyle`. |
| defaultUnselectedStyle | object | {} | ✓ | Fallback style for unselected buttons. |
| primary | boolean | true | ✓ | Toggles primary/secondary visual style. |
| enabled | boolean | true | ✓ | Controls interaction for the whole group. |
| buttonGap | numeric | — | ✓ | Spacing in pixels between buttons. |
| endButtonCornerRadius | numeric | — | ✓ | Corner radius applied to the first/last button in the row/column. |
| style | object | {} | ✓ | Component-level styling. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# controlValue: bidirectional binding is NOT used here — it's a write-only target.
# Typical setup:
#   indicatorValue  <- Tag binding (read), e.g. [default]Line1/CurrentMode
#   controlValue    -> written by the component when a state button is clicked
```

## Script/Event Handlers

```python
# Component Event Script: onActionPerformed fires when a state button is clicked
def onActionPerformed(self, event):
	system.tag.writeBlocking(["[default]Line1/ModeCommand"], [self.props.controlValue])
```

```python
# Property Change Script on props.indicatorValue — react to external state changes
self.getSibling("StatusLabel").props.text = "Mode: " + str(currentValue.value)
```

## Common Gotchas
- **`controlValue` and `indicatorValue` are two separate properties, not one** — a very common mistake is binding a single tag to both and expecting bidirectional behavior automatically; you must wire `indicatorValue` from the feedback tag and let `controlValue` be written by the component's own click logic (typically forwarded to the write tag in `onActionPerformed`, not by binding `controlValue` itself to the same tag bidirectionally).
- If `indicatorValue` doesn't match any `states[].value`, none of the buttons show as "selected," even though the underlying process is in a valid state — verify the state's `value` types match exactly (int vs. float mismatches are a frequent cause).
- `orientation` is boolean-typed here (matches Slider's pattern, not Radio Group's string pattern) — check the Designer property panel before scripting it.
- `tooltipText` per state must be set individually inside each `states[]` entry — there's no group-level tooltip fallback.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
