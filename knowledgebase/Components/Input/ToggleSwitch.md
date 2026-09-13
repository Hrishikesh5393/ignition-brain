> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Toggle Switch Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.toggle-switch` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| selected | boolean | false | ✓ | On/off state. Same naming convention as Checkbox — **not `value`.** |
| label.text | string | "" | ✓ | Text label; supports inline editing. |
| label.position | boolean | — | ✓ | Text position relative to the switch: right or left (boolean-backed). |
| label.style | object | {} | ✓ | Label styling (text, background, margin/padding, border, shape, misc). |
| color.selected | object | — | ✓ | Switch color when selected (on). |
| color.unselected | object | — | ✓ | Switch color when unselected (off). |
| color.disabled.selected | object | — | ✓ | Color when selected AND disabled (new in 8.3.3). |
| color.disabled.unselected | object | — | ✓ | Color when unselected AND disabled (new in 8.3.3). |
| enabled | boolean | true | ✓ | Whether the user may alter the selected state. |
| style | object | {} | ✓ | Full component styling. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Bidirectional tag binding on props.selected to a boolean tag (e.g., equipment enable)

# Expression binding for the label reflecting current state:
if({Root.ToggleSwitch.props.selected}, "Running", "Stopped")
```

## Script/Event Handlers

```python
def onActionPerformed(self, event):
	system.tag.writeBlocking(["[default]Line1/Enable"], [self.props.selected])
```

```python
# Property Change Script on props.selected
self.getSibling("StatusLabel").props.text = "ON" if currentValue.value else "OFF"
```

## Common Gotchas
- Property is `selected`, functionally and semantically identical to Checkbox's `selected` — the two components are described in the official docs as sharing the same underlying functionality, differing only in visual presentation.
- Disabled-state colors (`color.disabled.*`) are only available from **8.3.3+**; on earlier 8.3.x releases the switch falls back to a default greyed-out look regardless of `color.selected`/`color.unselected`.
- No dedicated `onChange`-style component property — use a Property Change Script on `props.selected`, not a component event, when you need to react purely to value changes regardless of how they occurred (script, binding, or click).
- `label.position` is boolean-typed per docs (left/right), so passing string values like `"left"` may not bind correctly — confirm against the Designer's property panel control type first.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
