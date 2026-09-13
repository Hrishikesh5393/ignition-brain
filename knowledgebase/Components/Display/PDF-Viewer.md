> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# PDF Viewer

**Category:** Display / General | **Ignition:** ia.display.pdfviewer

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.source | string | "" | ✓ | PDF file path/URL or base64 data-URI |
| props.page | numeric | 1 | ✓ (bidirectional) | Currently displayed page |
| props.zoom | numeric | 1.0 | ✓ | Zoom level multiplier |
| props.showToolbar | boolean | true | ✓ | Show built-in page/zoom controls |
| props.style | object | {} | ✓ | Container CSS |

## Data Binding Examples

```javascript
// Static SOP document from project resources
props.source: "Documents/SOP-Line1-Startup.pdf"

// Dynamic document served from a database BLOB via a script transform (bytes -> data URI)
props.source: {tag: "[default]Documents/CurrentWorkOrderPdf", transform: "toDataUri"}

// Jump to a specific page based on a fault code lookup
props.page: {expr: "lookup({Root.FaultPageMap.value}, {Root.Alarm.faultCode}, 1)"}

// External document management system URL
props.source: {expr: "'https://docs.example.com/api/wo/' + {Root.Params.woId} + '/pdf'"}
```

## Common Gotchas
- Large PDFs (many megabytes, scanned image-heavy documents) can be slow to render client-side, especially on Perspective sessions running on lower-powered panel PCs — prefer text-based/optimized PDFs for operator-facing SOPs.
- `props.page` binding to jump to a page only works reliably **after** the document has finished loading — binding it from a fast-changing source right at view-open can race with the PDF load and be ignored; re-triggering the binding after a short delay is a common workaround.
- Cross-origin PDF URLs (external document servers) must have permissive CORS headers or the embedded viewer fails to load the file with no visible error beyond a blank pane.
- Printing directly from the embedded viewer depends on the browser's PDF plugin — for guaranteed print output, provide a separate download/open-in-new-tab link rather than relying on in-component print.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
