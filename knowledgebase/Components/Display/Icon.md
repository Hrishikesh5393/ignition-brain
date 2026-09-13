> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Icon

**Category:** Display / General | **Ignition:** ia.display.icon

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| path | string | "" | ✓ | Shorthand `"library/iconName"` (e.g. `material/insert_emoticon`) |
| library | string | — | ✓ | Alternative to `path` — library name (must pair with `name`) |
| name | string | — | ✓ | Alternative to `path` — icon name (must pair with `library`) |
| color | string (color) | "" | ✓ | Icon color — convenience for setting `fill` in styles |
| viewBox.x / .y / .width / .height | number | — | ✓ | Crop/viewBox region of the underlying SVG |
| style | object | {} | ✓ | Container CSS |

There is no `tooltipText` or `rotation.angle`/`rotation.origin` property on this component. For rotation, use `style` (a CSS `transform: rotate(...)` in the style object), since there's no dedicated rotation prop.

## Data Binding Examples

```javascript
// Static icon reference
path: "material/wb_incandescent"

// Color bound to alarm state via theme variable
color: {expr: "{Root.Alarm.active} ? 'var(--error)' : 'var(--success)'"}

// Rotation via style transform (no dedicated rotation property)
style: {expr: "{'transform': 'rotate(' + {tag: '[default]Line1/FanAngle'} + 'deg)'}"}

// Swap icon by device type
path: {expr: "switch({Root.Params.deviceType}, 'pump', 'material/water_pump', 'valve', 'material/valve', 'material/help_outline')"}
```

## Common Gotchas
- `path` format is strictly `"library/name"` — omitting the library prefix (e.g. just `"star"`) fails to resolve and renders blank. Alternatively, set `library` and `name` as two separate properties instead of one combined `path` string.
- Built-in libraries include `material`, `fontawesome/regular`, `fontawesome/solid`, `fontawesome/brands` — custom SVG icon libraries can be imported as a project resource and referenced the same way.
- `color` does nothing for multi-color icon sets (e.g. some FontAwesome brand icons ship with fixed colors) — single-color/monochrome icons only.
- No dedicated rotation property — rotation/animation must be done via CSS `transform` in `style`, not a `rotation.angle` prop (which doesn't exist).
- Icon has no `enabled`/click state or tooltip built in; wrap in a clickable container if used as a button-like control.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
