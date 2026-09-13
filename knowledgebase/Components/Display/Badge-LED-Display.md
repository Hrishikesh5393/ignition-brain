> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# LED Display (Badge)

**Category:** Display / General | **Ignition:** ia.display.ledDisplay

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number\|string | 0 | ✓ | Value shown on the display |
| segmentFormat | string | "14 segment" | ✓ | `"7 segment"` (digits/limited chars) or `"14 segment"` (full alphanumeric) |
| numberFormat | string | "#,##0.00" | ✓ | Numeric display format (commas, decimals) — one of a fixed enum, not a free-form pattern |
| backgroundColor | string (color) | "" | ✓ | Panel background color |
| diodeOnColor | string (color) | "" | ✓ | Color of lit segments |
| diodeOffColor | string (color) | "" | ✓ | Color of unlit segments |
| locale | string | "en-US" | ✓ | Locale for comma/decimal formatting rules |
| style | object | {} | ✓ | Container CSS |

There is no `color`, `numDigits`, or `showInactiveSegments` property. On/off segment coloring is `diodeOnColor`/`diodeOffColor` (two separate properties, not one `color`); digit count and unlit-segment visibility aren't independently configurable — they follow from `value`, `segmentFormat`, and `numberFormat`.

## Data Binding Examples

```javascript
// Bind to a counter tag
value: {tag: "[default]Line1/PartCount"}

// Alphanumeric status code — needs 14-segment mode
segmentFormat: "14 segment"
value: {tag: "[default]Line1/StatusCode"}

// Color changes when a limit tag is exceeded
diodeOnColor: {expr: "{Root.LEDDisplay.value} > {Root.Params.highLimit} ? '#F55353' : '#00FF00'"}
```

## Common Gotchas
- There's no single `color` property — lit and unlit segment colors are set independently via `diodeOnColor`/`diodeOffColor`.
- Alphanumeric text (letters, not just digits) requires `segmentFormat: "14 segment"` — 7-segment mode can't render most letters correctly.
- `numberFormat` is a fixed enum of format strings (e.g. `"#,##0.00"`, `"0.###E0"`), not an arbitrary custom pattern.
- Digit count and "ghost" unlit-segment appearance aren't separate toggles — they're implicit in how `value` renders under the chosen `segmentFormat`/`numberFormat`.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
