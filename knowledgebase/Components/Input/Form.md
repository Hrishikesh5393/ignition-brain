> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Form Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.form` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| name | string | — | ✓ | Identifier for the form used by handlers/submission logic. |
| disabled | boolean | false | ✓ | Disables all inputs and actions in the form. |
| readOnly | boolean | false | ✓ | Sets all fields to read-only. |
| columns | array | [] | ✓ | Column layout definitions (`align`, `justify`, `items[]`). |
| actions | object | {} | ✓ | Submit/Cancel button configuration block. |
| context | object | {} | ✓ | Additional form metadata/config. |
| data | object | {} | (read/write) | Live store of user input, keyed by widget `id`. |
| validation | object | — | (read-only) | Live validation results per widget. |
| style | object | {} | ✓ | Component-level styling. |

### Actions Block
| Property | Type | Purpose |
|---|---|---|
| actions.disabled | boolean | Disable all action buttons at once. |
| actions.fixed | boolean | Keep the action bar visible while the form scrolls. |
| actions.layout | string | `row`, `column`, `row-reverse`, `column-reverse`. |
| actions.submit.text / .icon / .style | — | Submit button appearance. |
| actions.submit.fireComponentEvent | boolean | Fires `onSubmitActionPerformed`. |
| actions.submit.fireSubmissionEvent | boolean | Sends form `data` to a Gateway event handler. |
| actions.submit.submissionHandler | string | Name of the Gateway-side handler script to run. |
| actions.submit.awaitResponse | boolean | Wait for the Gateway response before re-enabling the form. |
| actions.submit.resetOn | string | `success` or `action` — when to reset field values. |
| actions.cancel.text / .icon / .style | — | Cancel button appearance. |
| actions.cancel.fireComponentEvent | boolean | Fires `onCancelActionPerformed`. |
| actions.cancel.reset | boolean | Reset form fields when Cancel is pressed. |

### Widget Types (inside `columns[].rows[].widgets[]`)
`text`, `email`, `url`, `password`, `number`, `tel`, `text-area`, `radio`, `checkbox`, `toggle`, `slider`, `dropdown`, `date-picker`, `time-picker`, `date-time-picker` — each with its own `<type>.*` sub-properties (e.g. `radio.options`, `dropdown.multiselect`, `number.validation`).

### Validation (per-widget, under `constraints.*`)
`constraints.required.enabled`, `constraints.maxLength.value`, `constraints.minLength.value`, `constraints.pattern.value` (text-like widgets), `constraints.min`/`constraints.max` (number/slider), `constraints.step.value` (number).

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Read a specific field's current value out of the form's data object,
# where "email" is a widget id defined in columns[].rows[].widgets[]:
{Root.Form.props.data.email}
```

## Script/Event Handlers

```python
def onSubmitActionPerformed(self, event):
	# Fires only if actions.submit.fireComponentEvent = true
	system.perspective.print("Form submitted: " + str(self.props.data))
```

```python
# Gateway Form Submission handler (separate script, runs at Gateway scope,
# configured when actions.submit.fireSubmissionEvent = true and
# actions.submit.submissionHandler names this handler)
def onSubmit(self, event):
	data = event.data
	system.db.runPrepUpdate(
		"INSERT INTO requests (name, email) VALUES (?, ?)",
		[data["name"], data["email"]]
	)
	return {"success": True}
```

## Common Gotchas
- Form is fundamentally different from a plain container: it **always renders its own Submit/Cancel action bar**, auto-collects widget values into `props.data` keyed by widget `id`, and runs built-in per-widget validation — don't rebuild this manually with loose components unless you specifically need to avoid the built-in action bar.
- Field values live under `data.<widgetId>` — renaming a widget's `id` breaks every binding/script referencing the old key with no compile-time warning.
- `actions.submit.fireComponentEvent` and `actions.submit.fireSubmissionEvent` are independent toggles — you can have the client-side `onSubmitActionPerformed` event fire without ever hitting a Gateway handler, or vice versa; check both if "submit does nothing."
- `actions.submit.awaitResponse=true` blocks the form (shows a pending state) until the Gateway handler returns — a Gateway handler that hangs or errors without returning will leave the form stuck disabled.
- Validation (`constraints.*`) is configured **per widget type**, not globally — e.g., `constraints.pattern` only applies to text-like widgets (`text`, `email`, `password`, `url`, `tel`), not to `number` or `dropdown`.
- `readOnly` and `disabled` are NOT the same: `readOnly` still submits existing values and shows them non-editable; `disabled` also blocks the action buttons entirely.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
