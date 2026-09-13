> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Barcode

**Category:** Display / General | **Ignition:** ia.display.barcode

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.data | string | "" | ✓ | Value to encode |
| props.codeType | string | "CODE128" | ✓ | Symbology: `CODE128`, `CODE39`, `EAN13`, `EAN8`, `UPC`, `QR`, `DATAMATRIX`, `PDF417`, etc. |
| props.showText | boolean | true | ✓ | Show human-readable text under the barcode |
| props.foregroundColor | string (color) | "#000000" | ✓ | Bar/module color |
| props.backgroundColor | string (color) | "#FFFFFF" | ✓ | Background color |
| props.style | object | {} | ✓ | Container CSS (width/height control rendered size) |

## Data Binding Examples

```javascript
// Encode a lot number as Code128
props.data: {tag: "[default]Line1/Batch/LotNumber"}
props.codeType: "CODE128"

// QR code linking to a traceability URL
props.codeType: "QR"
props.data: {expr: "'https://mes.example.com/lot/' + {Root.Params.lotId}"}

// EAN-13 for retail product labeling
props.codeType: "EAN13"
props.data: {tag: "[default]Product/GTIN"}
```

## Common Gotchas
- Each symbology has strict input constraints — `EAN13`/`UPC` require an exact-length numeric string with a valid check digit; an invalid value renders an error placeholder instead of a barcode, not a partial/garbled one.
- `QR` and `DATAMATRIX` are 2D codes — their rendered aspect ratio is roughly square regardless of the component's width/height ratio; stretching the container distorts the quiet zone and can hurt scanability.
- Changing `codeType` at runtime via binding is supported, but mixing incompatible `data` with a newly bound `codeType` (e.g. alpha text with `EAN13`) produces the error state until `data` catches up — bind both from the same upstream source to avoid a flash of error state.
- Print/label workflows should verify actual physical scan distance and required quiet-zone margin — `style.padding` around the component often needs to be non-zero for reliable scanning on printed labels.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
