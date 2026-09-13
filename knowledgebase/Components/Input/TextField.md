> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Text Field Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.text-field` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| text | string | "" | ✓ | Current text content. **Not called `value`.** |
| placeholder | string | "" | ✓ | Hint text shown when `text` is empty. |
| enabled | boolean | true | ✓ | If true, user may alter text. |
| deferUpdates | boolean | false | ✓ | When true, external updates to `text` are deferred until focus is lost or Enter is pressed — prevents the field from overwriting what the user is typing. |
| rejectUpdatesWhileFocused | boolean | false | ✓ | When true, `text` ignores external binding updates entirely while the field is focused. |
| spellcheck | boolean | false | ✓ | Underlines potential spelling errors (session-rendered only). |
| style | object | {} | ✓ | Full styling menu (text, background, margin/padding, border, shape, misc). |

There is **no `type` property** on the Perspective Text Field (unlike Vision) — email/URL/number-specific input types are configured on the **Form** component's field widgets instead (see `Form.md`), not on a standalone Text Field.

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (with `style.classes`), `custom`.

## Binding Example

```python
# Tag binding on props.text (Designer Binding dialog, Tag type, Bidirectional enabled
# so typed text writes back automatically)

# Expression binding with fallback:
if(isNull({[default]Path/To/Tag}), "Default Text", {[default]Path/To/Tag})
```

## Script/Event Handlers

```python
# Component Event Script: onKeyPress or onKeyDown for Enter-to-search behavior
def onKeyPress(self, event):
	if event.key == "Enter":
		system.perspective.print("Search for: " + self.props.text)
```

```python
# Property Change Script on props.text — runs whenever text changes,
# including from typing (if deferUpdates=False) or from an external binding
if currentValue.value is not None and len(currentValue.value) < 3:
	self.props.style["border"] = "1px solid red"
else:
	self.props.style["border"] = ""
```

```python
# onFocus / onBlur for validation-on-exit pattern
def onBlur(self, event):
	value = self.props.text.strip() if self.props.text else ""
	self.props.text = value
```

## Common Gotchas
- Property is `text`, not `value` — same trap as Checkbox's `selected`.
- No built-in `type="email"` / `type="number"` restriction — validate in a Property Change Script or use a Form widget instead.
- No `maxLength` or `autoComplete` property exists on the standalone Text Field (these belong to Form text widgets: `constraints.maxLength.value`, `text.autoComplete`).
- If bound bidirectionally to a fast-changing tag, set `deferUpdates=true` or the field will overwrite the user's keystrokes mid-typing.
- `rejectUpdatesWhileFocused` and `deferUpdates` solve different problems — the former blocks ALL external updates while focused (even after the field is idle), the latter only delays until blur/Enter. Don't assume they're interchangeable.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
