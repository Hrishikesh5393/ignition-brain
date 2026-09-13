> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Progress Bar

**Category:** Display / General | **Ignition:** ia.display.progressbar

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number | 50 | ✓ | Current progress value |
| min | number | 0 | ✓ | Minimum of range |
| max | number | 100 | ✓ | Maximum of range |
| mode | string | "determinate" | ✓ | `determinate` (value-driven) or `indeterminate` (animated/unknown-progress spinner) |
| bar.color | string (color) | "" | ✓ | Fill/bar color — convenience for `style.backgroundColor` |
| bar.determinate.color / bar.indeterminate.color | string (color) | "" | ✓ | Mode-specific bar color overrides |
| track.color | string (color) | "" | ✓ | Track (unfilled) color |
| track.determinate.color / track.indeterminate.color | string (color) | "" | ✓ | Mode-specific track color overrides |
| valueDisplay.enabled | boolean | false | ✓ | Show the value overlay text (off by default) |
| valueDisplay.format | string | "0,0.##" | ✓ | Display format — `none`, `0,0`, `0.##%`, `$0,0.00`, `00:00:00` |
| valueDisplay.justify | string | "center" | ✓ | `left`, `center`, `right` |
| style | object | {} | ✓ | Container CSS |

There is no `vertical` orientation property, no `barColor`/`backgroundTrackColor` (they're `bar.color`/`track.color`), and no free-text `label.text`/`label.visible` — the overlay is `valueDisplay`, driven by a fixed `format` enum, not arbitrary text. There's also a `mode` property (determinate/indeterminate) that has no equivalent in the incorrect version of this doc at all.

## Data Binding Examples

```javascript
// Bind value to a batch percent-complete tag
value: {tag: "[default]Line1/Batch/PercentComplete"}

// Dynamic max from a recipe setpoint
max: {tag: "[default]Line1/Batch/TargetQuantity"}
value: {tag: "[default]Line1/Batch/CurrentQuantity"}

// Color the bar red near/over threshold
bar.color: {expr: "{Root.Progress.value} / {Root.Progress.max} > 0.9 ? '#F55353' : '#229AD6'"}

// Show live percentage overlay using the built-in format
valueDisplay.enabled: true
valueDisplay.format: "0.##%"

// Indeterminate spinner while waiting on an unknown-duration operation
mode: "indeterminate"
```

## Common Gotchas
- `valueDisplay` shows a formatted **value**, not free text — there's no `label.text` property to inject arbitrary strings; pick the closest `valueDisplay.format` or overlay a separate Label component if you need custom text.
- `value` is **not** automatically clamped to `[min, max]` — a source tag exceeding `max` can visually overflow the bar; clamp in an expression if the source is unreliable.
- No `vertical` orientation property exists — orientation isn't independently configurable here.
- `mode: "indeterminate"` ignores `value` entirely and shows an animated/unknown-progress indicator — useful while waiting on an operation with no known percent-complete.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
