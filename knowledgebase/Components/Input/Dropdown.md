> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Dropdown Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.dropdown` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | any | — | ✓ | Currently selected value (matches an item's `value` field in `options`). |
| options | array | [] | ✓ | Array of `{value, label, isDisabled}` objects defining the choices. |
| multiSelect | boolean | false | ✓ | Allow selecting more than one option at once. |
| wrapMultiSelectValues | boolean | false | ✓ | When `multiSelect` is on, wrap selected-value chips onto multiple lines instead of scrolling horizontally. |
| placeholder.text | string | "" | ✓ | Prompt text shown when nothing is selected. |
| placeholder.color | color | — | ✓ | Placeholder text color. |
| placeholder.icon.path | string | — | ✓ | Icon path (`library/iconName`) shown next to the placeholder. |
| enabled | boolean | true | ✓ | Enables interaction. |
| search.enabled | boolean | true | ✓ | Allow type-ahead searching within the option list. |
| search.matching | string | "start" | ✓ | Match mode: `start` (prefix match) or `any` (substring match). |
| search.noResultsText | string | "No results found." | ✓ | Message shown when search yields nothing. |
| showClearIcon | boolean | false | ✓ | Show an "x" to clear the current selection. |
| allowCustomOptions | boolean | false | ✓ | Let the user type a value that isn't in `options`. |
| textAlign | string | "left" | ✓ | Text alignment: `left`, `center`, `right`. |
| minMenuHeight | numeric | 150 | ✓ | Minimum open-menu height in px. |
| maxMenuHeight | numeric | 350 | ✓ | Maximum open-menu height in px. |
| style | object | {} | ✓ | Component styling. |
| dropdownOptionStyle | object | {} | ✓ | Styling for the individual options in the open menu. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# options via an Expression or Query binding, e.g. transform a dataset to the array shape:
# [{"value": row["id"], "label": row["name"]} for row in dataset rows]

# Tag binding for value (bidirectional) so the dropdown selection writes back to a tag.
```

## Script/Event Handlers

```python
# Component Event Script: onActionPerformed fires when selection changes
def onActionPerformed(self, event):
	system.perspective.print("Selected: " + str(self.props.value))
```

```python
# Property Change Script on props.value
if currentValue.value is not None:
	self.getSibling("DetailPanel").props.visible = True
```

## Common Gotchas
- `options` entries need `value` AND `label` — a common mistake is providing only `label`, which leaves `props.value` unable to match anything.
- `multiSelect=true` changes `props.value` from a scalar to an **array** — bindings/scripts written for single-select mode will break silently (comparisons against a single value stop matching).
- `allowCustomOptions=true` lets typed text become the value even if it doesn't exist in `options` — validate downstream if you rely on `options` as the authoritative list.
- Disabled individual options use `isDisabled: true` on that specific option object, not a component-level property.
- `search.matching: "start"` (the default) will NOT find matches in the middle of a label — switch to `"any"` if users expect substring search.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
