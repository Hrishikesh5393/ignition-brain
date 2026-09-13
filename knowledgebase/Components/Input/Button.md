> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Button Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.button` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| text | string | "" | ✓ | Text displayed on the button. Supports inline editing via deep-click selection in the Designer. |
| textStyle | object | {} | ✓ | Style block (text, background, margin, padding, border, shape) applied only to the text/label. |
| primary | boolean | true | ✓ | Toggles the built-in "Primary" vs "Secondary" visual variant. |
| enabled | boolean | true | ✓ | Enables/disables interaction. **There is no `disabled` property** — use `enabled`. |
| image.source | string | "" | ✓ | Image URL, e.g. `/system/images/{path}`. |
| image.icon.path | string | "" | ✓ | Icon path in `library/IconName` format (e.g. `material/home`). |
| image.icon.color | string | "" | ✓ | Icon color (hex/RGB/HSL). |
| image.icon.width | numeric | — | ✓ | Icon width in px. |
| image.icon.height | numeric | — | ✓ | Icon height in px. |
| image.position | string | "left" | ✓ | Image position relative to text: `left`, `right`, `top`, `bottom`, `center`. |
| align | string | "center" | ✓ | Aligns text/image along the cross axis: `start`, `center`, `end`, `stretch`. |
| justify | string | "center" | ✓ | Justifies text/image along the main axis: `start`, `center`, `end`, `space-around`, `space-between`, `space-evenly`. |
| style | object | {} | ✓ | Full component styling (text, background, margin, padding, border, shape, misc). |

There is **no `props.text` shorthand like `value`** — the display text property is `text`, not `value` or `label`.

## Common Properties (All Components)
- `meta.name` (string) — component identifier used by `self.getSibling()` and navigation paths
- `meta.visible` (boolean, default `true`) — show/hide
- `meta.tooltip.text` / `meta.tooltip.enabled` — hover tooltip
- `meta.domId` (string) — HTML `id` attribute
- `meta.tabIndex` (integer, default 0) — keyboard tab order
- `position` (object) — shape depends on parent container (Coordinate: x/y/width/height; Flex: grow/shrink/basis)
- `style` (object) — CSS-like styling; supports style classes under `style.classes` (array of strings) — **there is no `className` property**
- `custom` (object) — user-defined scripting properties

## Binding Example

```python
# Property binding path syntax (Designer > right-click property > Bindings)
# Expression binding referencing a tag directly:
{[default]Path/To/EnableTag}

# Expression binding referencing another component's property:
{Root.Container.NumericEntryField.props.value} > 0

# Full component prop path used in scripts:
self.getSibling("Button").props.text
```

## Script/Event Handlers

Perspective components do not expose an `onClick` *property* — click behavior is configured as a **Component Event Script** (right-click component → Scripting → Events → onActionPerformed), which generates a `def` stub:

```python
def onActionPerformed(self, event):
	# self  = the Button component
	# event = event object (source, type)
	system.tag.writeBlocking(["[default]Path/To/Tag"], [1])
	system.perspective.navigate(view="Path/To/View")
```

Other available events (from the Perspective Event Types Reference): `onStartup`, `onShutdown`, `onClick`, `onMouseEnter`, `onMouseLeave`, `onFocus`, `onBlur`, `onKeyDown`, `onKeyUp`. Mouse/keyboard events fire in addition to `onActionPerformed`, which is the semantic "this button was activated" event (fires on click *and* Enter/Space when focused).

```python
# Disable button during a long-running write, re-enable after
def onActionPerformed(self, event):
	self.props.enabled = False
	self.props.text = "Working..."
	system.tag.writeBlocking(["[default]Cmd"], [1])
	self.props.enabled = True
	self.props.text = "Save"
```

## Common Gotchas
- Property is `enabled`, not `disabled` — logic is inverted from what many developers expect coming from Vision.
- Property is `text`, not `label` or `value`.
- No `className` — use `style.classes` (array) tied to a Perspective Style Class resource, or set `style` directly for one-off styling.
- `onClick` fires on any mouse click; `onActionPerformed` is the recommended handler because it also fires for keyboard activation (accessibility).
- `primary: false` does not disable the button — it only switches the visual variant (primary/secondary), unrelated to `enabled`.
- Icon path must reference an existing Perspective icon library (`material/...`) — an invalid path silently renders nothing, no error.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
