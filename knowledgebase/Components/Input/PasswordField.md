> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Password Field Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.password-field` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| text | string | "" | ✓ | The password text. Same naming as Text Field — not `value`. |
| placeholder | string | "" | ✓ | Text shown when the field is empty. |
| enabled | boolean | true | ✓ | Controls whether the user can modify the entry. Disabled components still run scripts. |
| allowReveal | boolean | false | ✓ | Adds a "show password" toggle to temporarily unmask the text. |
| style | object | {} | ✓ | Styling for text, background, margin/padding, border, shape, misc; supports style classes. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Do NOT bind props.text directly to a persisted tag/DB column in plaintext.
# Typical pattern: read on submit only, via a Button's onActionPerformed, then discard.
```

## Script/Event Handlers

```python
def onActionPerformed(self, event):
	# Triggered from a sibling "Login" Button, not from the Password Field itself
	username = self.getSibling("UsernameField").props.text
	password = self.getSibling("PasswordField").props.text
	# Never system.perspective.print() a password value — avoid leaking it to session logs
	authResult = system.security.validateUser(username, password)
```

```python
# Property Change Script on props.text — live strength meter, never logs the value
strength = "weak"
if currentValue.value and len(currentValue.value) >= 8:
	strength = "strong"
self.getSibling("StrengthLabel").props.text = strength
```

## Common Gotchas
- Property is `text`, exactly like Text Field — copy/paste between the two components is otherwise safe, but remember `type="password"` (a Vision-era assumption) does not exist here; masking is inherent to the component itself.
- `allowReveal` shows the raw password in the UI when toggled — don't enable it on shared/kiosk sessions where shoulder-surfing is a risk.
- Never bind `props.text` to a Tag or expression that persists/logs the value (tag history, alarm messages, `system.perspective.print`) — there's no built-in masking once the value leaves the component.
- No `minLength`/`pattern` validation properties exist on the standalone component — use a Form `password` widget (`constraints.minLength`, `constraints.pattern`) if you need built-in validation UI.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
