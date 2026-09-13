> **Component category:** Input · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

# File Upload Component

**Category:** Input | **Ignition:** Perspective Input Palette — `ia.input.file-upload` | **Verified:** Ignition 8.3 official docs

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| enabled | boolean | true | ✓ | Whether the component accepts uploads (8.3.5+). |
| maxUploads | integer | 5 | ✓ | Maximum concurrent (simultaneous) uploads allowed. |
| supportedFileTypes | array | [] | ✓ | Allowed file extensions, e.g. `["pdf", "txt"]`. Empty = all types allowed. |
| fileSizeLimit | integer | 10 (MB) | ✓ | Max file size per upload; hard-capped at 20 MB unless the Gateway's `web.xml` is adjusted. |
| fileUploadIcon.path | string | — | ✓ | Icon (`library/iconName`). |
| fileUploadIcon.color.enabled | color | — | ✓ | Icon color when enabled (8.3.5+). |
| fileUploadIcon.color.disabled | color | — | ✓ | Icon color when disabled (8.3.5+). |
| fileUploadIcon.style | object | {} | ✓ | Icon styling. |
| style.enabled | object | {} | ✓ | Component styling when enabled (8.3.5+). |
| style.disabled | object | {} | ✓ | Component styling when disabled (8.3.5+). |

## Common Properties (All Components)
See `Button.md` — `meta.*`, `position`, `style` (`style.classes`), `custom`. Note: this component's `style` is split into `style.enabled`/`style.disabled` sub-objects rather than one flat `style` block.

## Binding Example

```python
# supportedFileTypes is typically a static array set in the Designer, not bound:
["pdf", "csv", "xlsx"]

# fileSizeLimit bound from a Gateway-wide config tag to keep limits centrally managed:
{[default]Config/MaxUploadSizeMB}
```

## Script/Event Handlers

```python
# Component Event Script: onFileReceived — the primary handler for this component.
# Runs in the Gateway scope once the file finishes uploading.
def onFileReceived(self, event):
	fileName = event.fileName
	fileData = event.fileData  # bytes
	system.file.writeFile("C:/uploads/" + fileName, fileData)
```

## Common Gotchas
- Actual upload handling happens in `onFileReceived`, which runs at **Gateway scope**, not session/client scope — `self` references still work, but heavy client-only APIs (e.g. `system.gui.*`) are unavailable there.
- `fileSizeLimit` is capped at 20 MB by the Gateway's servlet configuration regardless of what you set in the property — raising the property above that requires a `web.xml` change on the Gateway itself, not just a component property edit.
- `enabled`/per-state icon colors (`fileUploadIcon.color.*`) and `style.enabled`/`style.disabled` split styling were **added in 8.3.5** — earlier 8.3.x versions used a single always-on style block.
- `supportedFileTypes` filters the browser's file picker but is not a hard server-side guarantee — validate the actual extension/content again in `onFileReceived` for security-sensitive uploads.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [21-BINDINGS](../../21-BINDINGS.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
