> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# One-Shot Button Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.one-shot-button` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | numeric/boolean/string/null | 0 | ✓ | Current value displayed/tracked by the component. **Should be bound bidirectionally to a tag** so the Gateway's response updates it. |
| setValue | numeric/boolean/string/null | 1 | ✓ | The value written when the button is pushed. |
| primary | boolean | true | ✓ | Toggles primary/secondary visual style. |
| enabled | boolean | true | ✓ | Controls user interaction. |
| readyState.text | string | — | ✓ | Button text while idle/ready to be pushed. |
| readyState.icon.path | string | — | ✓ | Icon shown in the ready state. |
| readyState.icon.color | color | — | ✓ | Icon color in the ready state. |
| readyState.style | object | {} | ✓ | Style for the ready state. |
| writingState.text | string | — | ✓ | Button text while waiting for the write to resolve. |
| writingState.icon.path | string | — | ✓ | Icon shown while writing. |
| writingState.icon.color | color | — | ✓ | Icon color while writing. |
| writingState.style | object | {} | ✓ | Style for the writing state. |
| confirm.enabled | boolean | false | ✓ | Show a confirmation dialog before writing. |
| confirm.text | string | "Are you sure?" | ✓ | Confirmation dialog message. |
| style | object | {} | ✓ | Component-level styling. |
| disabledStyle | object | {} | ✓ | Styling applied while the component is disabled/mid-write. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Required setup: props.value MUST be bound bidirectionally to a feedback/command tag,
# e.g. [default]Line1/StartCommandAck — so that when the PLC/tag processes the command
# and the tag value changes back away from setValue, the button re-arms automatically.
```

## Script/Event Handlers

```python
# onActionPerformed only fires if confirm.enabled=true — it runs AFTER the user confirms,
# and before the write occurs, letting you cancel or log the action.
def onActionPerformed(self, event):
	system.perspective.print("User confirmed one-shot write")
```

## Common Gotchas
- **The write/response cycle is state-driven, not event-driven**: when `value` and `setValue` become equal, the button enters the "writing" state and **disables itself**; it only returns to "ready" once `value` changes away from `setValue` again — which must happen externally (e.g., the PLC/tag resets after processing). If nothing ever changes `value` back, the button stays permanently disabled after one click — a very common integration bug.
- `value` must be a **bidirectional** binding, not a one-way read — a one-way binding means the click never actually reaches the tag, and the button will appear to "hang" in the writing state forever.
- `setValue` is what gets written, `value` is the current/feedback state — they are easy to mix up since both accept the same data types.
- `confirm.enabled` gates `onActionPerformed`, but the underlying write itself is driven by the `value`/`setValue` binding mechanism, not by script — don't try to perform the write manually inside `onActionPerformed` unless you're intentionally bypassing the built-in state machine.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
