> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Text Area Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.text-area` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| text | string | "" | ✓ | Multi-line text content. Not `value`. |
| placeholder | string | "" | ✓ | Hint text shown when empty. |
| enabled | boolean | true | ✓ | If true, user may edit text. |
| deferUpdates | boolean | false | ✓ | Delay external updates to `text` until focus lost/Enter. |
| rejectUpdatesWhileFocused | boolean | false | ✓ | Ignore external binding updates entirely while focused. |
| resize | string | "vertical" | ✓ | Whether the user can resize the box: `none`, `both`, `horizontal`, `vertical`. |
| wrap | string | "soft" | ✓ | Text wrapping: `hard`, `soft`, or `off`. |
| spellcheck | boolean | false | ✓ | Underline potential spelling errors while editing. |
| style | object | {} | ✓ | Full styling menu (text, background, margin/padding, border, shape, misc). |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Tag binding on props.text (bidirectional) to a String tag storing notes/comments

# Expression combining multiple field values into one text block:
{Root.NameField.props.text} + " — " + {Root.DateField.props.formattedValue}
```

## Script/Event Handlers

```python
# Property Change Script on props.text — live character counter
count = len(currentValue.value) if currentValue.value else 0
self.getSibling("CharCountLabel").props.text = str(count) + " / 500"
```

```python
def onBlur(self, event):
	# trim trailing whitespace and persist to DB on exit
	self.props.text = self.props.text.rstrip() if self.props.text else ""
	system.db.runPrepUpdate(
		"UPDATE notes SET body = ? WHERE id = ?",
		[self.props.text, self.custom.recordId]
	)
```

## Common Gotchas
- Same `text` (not `value`) naming as Text Field — the two share almost identical properties.
- `wrap: "off"` produces horizontal scrolling instead of wrapping — surprising if you expected `off` to mean "don't scroll."
- No built-in `maxLength` property — enforce length limits in a Property Change Script or use a Form `text-area` widget with `constraints.maxLength`.
- `resize: "none"` locks the box to its container-defined size — combine with a Flex/Coordinate container height to avoid clipped text.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
