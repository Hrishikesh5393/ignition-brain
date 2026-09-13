> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Radio Group Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.radio-group` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | string/int/boolean/null | — | ✓ | Value of the currently selected radio. |
| index | integer | — | ✓ | Index of the selected node in `radios`. |
| radios | array | [] | ✓ | Array of radio definitions: `{text, value, selected, enabled, style}`. |
| radios[].text | string | — | ✓ | Label paired with this radio. |
| radios[].value | numeric | — | ✓ | Value evaluated when this radio is selected. |
| radios[].selected | boolean | false | ✓ | Whether this specific radio is selected. |
| radios[].enabled | boolean | true | ✓ | Whether the user may select this radio (added in 8.3.5). |
| radios[].style | object | {} | ✓ | Per-radio style override (added in 8.3.5). |
| orientation | string | "row" | ✓ | Layout direction: `row` or `column`. |
| align | string | — | ✓ | Cross-axis alignment of radios. |
| justify | string | — | ✓ | Main-axis justification of radios. |
| textPosition | string | "right" | ✓ | Label position relative to the radio button: `top`, `right`, `bottom`, `left`. |
| enabled | boolean | true | ✓ | Whether the user may select any radio. |
| selectedIcon | object | {} | ✓ | Icon config for the selected state (`path`, `color.enabled`, `color.disabled`, `style`). |
| unselectedIcon | object | {} | ✓ | Icon config for the unselected state. |
| radioStyle | object | {} | ✓ | Styling applied to all the radio buttons collectively. |
| style | object | {} | ✓ | Component-level styling. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# radios array via an Expression/Query/Script binding, e.g. built from a dataset:
# [{"text": row["label"], "value": row["id"], "selected": row["id"] == currentId} for row in rows]

# Bidirectional tag binding on props.value to write the chosen option straight to a tag.
```

## Script/Event Handlers

```python
# Component Event Script: onActionPerformed fires on selection change
def onActionPerformed(self, event):
	system.perspective.print("Selected value: " + str(self.props.value))
```

```python
# Property Change Script on props.index
self.getSibling("DetailView").props.selectedIndex = currentValue.value
```

## Common Gotchas
- Both `value` (the data) and each `radios[].selected` (the UI checkbox state) exist — setting `props.value` alone does **not** automatically flip `radios[].selected` on the matching entry unless the `radios` array itself is rebuilt/bound to reflect it. Prefer driving the array from a binding rather than hand-toggling both independently.
- `radios[].enabled` (per-radio disable) is an **8.3.5+ feature** — if targeting an earlier 8.3.x, per-option disabling isn't available; only the group-level `enabled` exists.
- `orientation` here IS a string (`"row"`/`"column"`), unlike Slider's boolean `orientation` — don't copy patterns between components without checking each one's actual type.
- `index` and `value` can disagree if the `radios` array has duplicate `value` entries — treat `index` as authoritative when the array can contain duplicates.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
