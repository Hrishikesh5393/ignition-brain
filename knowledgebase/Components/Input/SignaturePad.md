> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Signature Pad Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.signature-pad` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| enabled | boolean | true | ✓ | Enables the canvas, clear button, and submit button together. |
| pad.pen.color | string (hex/RGB/HSL) | — | ✓ | Drawing line color. |
| pad.pen.width | numeric | — | ✓ | Line width in pixels. |
| pad.canvas.clearColor | string | "transparent" | ✓ | Color the canvas is painted with when cleared. |
| pad.style | object | {} | ✓ | Canvas styling (text, background, margin/padding, border, shape). |
| actionBar.position | string | "bottom" | ✓ | Where the action bar sits relative to the canvas: `top`, `bottom`, `left`, `right`. |
| actionBar.submitButton.text | string | "submit" | ✓ | Submit button label. |
| actionBar.submitButton.enabled | boolean | true | ✓ | Enables the submit button. |
| actionBar.submitButton.primary | boolean | — | ✓ | Primary/secondary style toggle for submit. |
| actionBar.submitButton.style | object | {} | ✓ | Submit button styling. |
| actionBar.clearButton.text | string | "clear" | ✓ | Clear button label. |
| actionBar.clearButton.enabled | boolean | true | ✓ | Enables the clear button. |
| actionBar.clearButton.primary | boolean | — | ✓ | Primary/secondary style toggle for clear. |
| actionBar.clearButton.style | object | {} | ✓ | Clear button styling. |
| actionBar.style | object | {} | ✓ | Action bar container styling. |
| status.touched | boolean | — | (read-only) | `true` once the pad contains an unsaved signature. |
| style | object | {} | ✓ | Component-level styling. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# status.touched is typically read (not bound outward) to gate a parent Form's submit button:
{Root.SignaturePad.props.status.touched}   # → bind to another Button's props.enabled
```

## Script/Event Handlers

```python
# Component Event Script: onSignatureSubmitted — fires when the user presses Submit
def onSignatureSubmitted(self, event):
	imageBytes = event.signatureFile.getBytes()
	system.file.writeFile("C:/signatures/" + str(system.date.now().getTime()) + ".png", imageBytes)
```

```python
# Scripting functions available directly on the component instance
self.clearSignature()      # programmatically clear the canvas
self.submitSignature()     # programmatically trigger submission
```

## Common Gotchas
- The signature image is delivered through the `onSignatureSubmitted` **event**, not through a readable `props.value` — there is no property holding the drawn image directly; you must handle `event.signatureFile.getBytes()` at submit time.
- `status.touched` only tracks whether ANY strokes exist — it doesn't validate signature quality/completeness; pair it with your own business logic if partial scribbles need to be rejected.
- Clearing the canvas via `clearSignature()` does not automatically reset `status.touched` until the next render cycle — don't assume it's synchronously false immediately after the call in the same script line.
- `actionBar.submitButton.enabled=false` disables the submit button but does not stop the user from drawing — combine with `enabled=false` at the root level to fully lock the pad.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
