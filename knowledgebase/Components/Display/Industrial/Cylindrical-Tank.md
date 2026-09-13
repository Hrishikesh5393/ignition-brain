> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Cylindrical Tank

**Category:** Display / Industrial | **Ignition:** ia.display.cylindrical-tank

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| value | number | 0 | ✓ | Current fill level |
| capacity | number | 100 | ✓ | Scale maximum (full) — there is no separate scale-minimum property |
| liquidColor | string (color) | "" | ✓ | Liquid fill color |
| tankColor | string (color) | "" | ✓ | Tank outline/body color |
| liquidOpacity | number (0-1) | 0.7 | ✓ | Liquid fill transparency |
| liquidWarningColor / tankWarningColor | string (color) | "" | ✓ | Colors applied once `value` (as % of `capacity`) crosses `warningThreshold` |
| warningThreshold | number | 100 | ✓ | % of capacity above which the warning colors apply |
| strokeWidth | number | 2 | ✓ | Tank outline thickness |
| valueDisplay.enabled | boolean | true | ✓ | Show the numeric/percentage overlay |
| valueDisplay.format | string | "0%" | ✓ | Display format |
| valueDisplay.unit.enabled / .value / .fix | boolean / string / "pre"\|"post" | false / "" / "post" | ✓ | Optional unit suffix/prefix on the overlay |
| style | object | {} | ✓ | Container CSS |

There is no `startValue`/`endValue` (only `capacity`, implying a 0 floor), no `fillColor` (it's `liquidColor`), and no `ranges` array for multi-band coloring — warning coloring is a single `warningThreshold` plus `liquidWarningColor`/`tankWarningColor`, not an arbitrary list of colored bands.

## Data Binding Examples

```javascript
// Tank level in gallons, 5000 gal capacity
capacity: 5000
value: {tag: "[default]Tank1/LevelGal"}

// Fill color reflects liquid type via tag-driven color lookup
liquidColor: {expr: "lookup({Root.LiquidColorMap.value}, {Root.Tank1.productCode}, '#229AD6')"}

// Warn above 90% full
warningThreshold: 90
liquidWarningColor: "#F55353"
tankWarningColor: "#F55353"

// Show percentage overlay
valueDisplay.enabled: true
valueDisplay.format: "0%"
```

## Common Gotchas
- There is no `ranges` array like Linear Scale/Thermometer's `intervals` — level-based coloring here is a single threshold (`warningThreshold` + `liquidWarningColor`/`tankWarningColor`), not multiple colored bands.
- `value` is expressed relative to `capacity` (not a separate `startValue`/`endValue` pair) — always sanity-check the source tag's engineering-unit range matches `capacity`, since a units mismatch (e.g. liters vs. gallons) silently produces a wrong-looking fill level with no error.
- `valueDisplay.format` follows the fixed suggestion list (`none`, `0,0`, `0%`, `$0,0.00`) — it shows a percentage by default (`"0%"`), not raw units, unless you change the format.
- Visually renders a cylindrical vessel with an elliptical top/bottom cap — use this component when a literal cylindrical vessel shape matches the physical equipment, otherwise a styled Progress or custom Drawing may fit better for non-cylindrical vessels.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
