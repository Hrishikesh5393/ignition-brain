> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Checkbox Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.checkbox` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| selected | boolean | false | ✓ | The checked/unchecked state. **Not called `value` or `checked`.** |
| text | string | "" | ✓ | Label text; supports inline editing. **Not called `label`.** |
| textPosition | string | "right" | ✓ | Label placement: `top`, `right`, `bottom`, `left`. |
| enabled | boolean | true | ✓ | Enables interaction. Scripts still execute when `false`. |
| triState | boolean | false | ✓ | Enables a third, indeterminate state (null/mixed selection). |
| checkedIcon.path | string | — | ✓ | Icon shown when selected (`library/IconName`). |
| checkedIcon.color.enabled | string | — | ✓ | Icon color when selected and enabled. |
| checkedIcon.color.disabled | string | — | ✓ | Icon color when selected and disabled. |
| uncheckedIcon.path / .color.enabled / .color.disabled | string | — | ✓ | Same pattern for the unselected state. |
| indeterminateIcon.path / .color.enabled / .color.disabled | string | — | ✓ | Same pattern for the tri-state indeterminate icon. |
| style | object | {} | ✓ | Component-level styling. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (with `style.classes`), `custom` apply identically to every Perspective component.

## Binding Example

```python
# Tag binding on props.selected (configure via Designer Binding dialog, type = Tag)
# Path shown in binding config: [default]Line1/Enable

# Expression binding combining two component states:
{Root.Checkbox1.props.selected} && {Root.Checkbox2.props.selected}

# Bidirectional tag binding note: set the binding's "Bidirectional" toggle
# so user clicks write back to the tag automatically — no onActionPerformed needed.
```

## Script/Event Handlers

```python
# Component Event Script: onActionPerformed
# (fires when the user toggles the checkbox — checkbox has no dedicated onChange event property;
#  use a Property Change Script on props.selected instead for value-driven logic)
def onActionPerformed(self, event):
	system.perspective.print("Checkbox is now " + str(self.props.selected))
```

```python
# Property Change Script attached directly to props.selected
# (Designer: right-click "selected" property > Scripting > Property Change Script)
# Params are fixed: self, previousValue, currentValue, origin, missedEvents
if currentValue.value:
	self.getSibling("AdminOptions").props.visible = True
else:
	self.getSibling("AdminOptions").props.visible = False
```

## Common Gotchas
- Value property is `selected`, not `value` or `checked` — a very common copy-paste mistake from other UI frameworks.
- Label property is `text`, not `label`.
- `triState` alone does not put the checkbox into the indeterminate state — the indeterminate visual only appears when the bound value itself is `null`/unset while `triState=true`; setting `selected=false` with `triState=true` just shows unchecked.
- There is no `readOnly` property — to make it non-interactive but still visible, set `enabled=false`.
- Property Change Scripts use `previousValue`/`currentValue` (QualifiedValue objects — use `.value` to unwrap), **not** `oldValue`/`newValue`, and there is no `event` parameter on property change scripts (that pattern is only for Component Event Scripts like `onActionPerformed`).

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
