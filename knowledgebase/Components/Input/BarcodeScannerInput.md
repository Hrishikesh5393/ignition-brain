> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# Barcode Scanner Input Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.barcode-scanner-input` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| prefix | string | "" | ✓ | String marking the start of a barcode scan capture. |
| suffix | string | "" | ✓ | String marking the end of a barcode scan capture. |
| regex | object | — | ✓ | Regex pattern (JavaScript syntax) to identify a scan; the first capture group is extracted. |
| window | numeric | — | ✓ | Length of the keystroke buffer monitored for a `regex` match. |
| captureMode | string | "keypress" | ✓ | Key event listener type: `keypress`, `keyup`, or `keydown`. |
| data | array | [] | (read-only, bindable as source) | Barcode scans returned from the scanner. |
| dataStyle | object | {} | ✓ | Styling for the returned data display (text, background, margin/padding, border, shape, misc). |
| style | object | {} | ✓ | Component styling; supports style classes. |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`.

## Binding Example

```python
# props.data changes are typically consumed via a Property Change Script rather than a binding,
# since each scan appends a new entry that needs immediate processing.

# Static config example: most barcode scanners emulate a keyboard and send Enter as a suffix.
# prefix: ""      suffix: "\n" (or scanner-specific terminator)
```

## Script/Event Handlers

```python
# Property Change Script on props.data — fires each time a new scan is captured
if currentValue.value:
	latestScan = currentValue.value[-1]
	system.perspective.print("Scanned: " + str(latestScan))
	self.getSibling("PartNumberField").props.text = str(latestScan)
```

## Common Gotchas
- **Prefix/suffix take priority over `regex`** — if either `prefix` or `suffix` is a non-empty string, `regex` is ignored entirely, even if configured. Clear both if you intend to rely on `regex` matching alone.
- The component listens continuously without requiring focus — it does not need to be the active/clicked element to capture scans, which is easy to forget when debugging "scans not registering" (the issue is usually elsewhere, e.g. `window` too short).
- `regex` only extracts the **first capture group** — a pattern without any `(...)` group, or with the target data in the second group, silently returns nothing usable.
- `window` must be large enough to hold the full expected barcode length plus prefix/suffix — too short a buffer truncates fast scans from high-speed scanners.
- Most USB/Bluetooth barcode scanners emulate keyboard input and send an Enter keystroke as a terminator — set `captureMode` and `suffix` to match the specific scanner model being deployed.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
