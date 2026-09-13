> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Slider Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.slider` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | numeric | 0 | ✓ | Current value of the slider handle. |
| min | numeric | 0 | ✓ | Minimum of the slider scale (all the way left/down). |
| max | numeric | 100 | ✓ | Maximum of the slider scale (all the way right/up). |
| orientation | boolean | — | ✓ | Track alignment: vertical or horizontal (documented as boolean, not a string enum). |
| step | numeric | 1 | ✓ | Increment size for drag-driven changes. Does **not** enforce stepping when the value is set manually/via script. |
| labels.show | boolean | false | ✓ | Show labels at periodic values along the track. |
| labels.interval | numeric | — | ✓ | Interval at which periodic labels are displayed. |
| enabled | boolean | true | ✓ | Enables slider interaction. |
| handleColor | color | — | ✓ | Color of the drag handle. |
| railColor | color | — | ✓ | Color of the full track (behind the fill). |
| trackColor | color | — | ✓ | Color of the filled portion of the track, from min up to the current value. |
| style | object | {} | ✓ | Full styling menu. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# Bidirectional tag binding on props.value to a numeric setpoint tag

# Expression binding dynamically setting max from another tag:
{[default]Line1/TankCapacity}   # → props.max
```

## Script/Event Handlers

```python
# Property Change Script on props.value — live readout label
self.getSibling("ValueLabel").props.text = str(self.props.value) + " %"
```

```python
def onActionPerformed(self, event):
	# fires once the user releases the handle (drag completed)
	system.tag.writeBlocking(["[default]Line1/Setpoint"], [self.props.value])
```

## Common Gotchas
- `step` only governs the granularity while **dragging** — a script or binding can still set `value` to a non-stepped number; don't assume stepping is enforced everywhere.
- No `format` property — for a percent/unit-labeled readout, bind a sibling Label to `props.value` with an expression, as shown above.
- `orientation` is boolean per the official docs, not `"horizontal"`/`"vertical"` strings — verify against the property panel dropdown in the Designer before scripting it, since boolean-backed orientation toggles are easy to invert.
- Continuous `onActionPerformed`/Property Change firing during drag can flood tag writes if bound bidirectionally without any deferral — for OPC tags with limited write rates, write only on a dedicated "drag complete" event rather than every intermediate value.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
