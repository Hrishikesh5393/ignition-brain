> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Inline Frame (iframe)

**Category:** Display / General | **Ignition:** ia.display.iframe

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| src | string | "" | ✓ | URL to embed — the property is `src`, not `source` |
| allowFullScreen | boolean | false | ✓ | Allow the embedded content to request fullscreen |
| referrerPolicy | string | "no-referrer" | ✓ | `no-referrer`, `no-referrer-when-downgrade`, `origin`, `origin-when-cross-origin`, `unsafe-url` |
| style | object | {} | ✓ | Container CSS (dimensions, border) |

There is no `sandboxRules` or `allow` property — the `sandbox`/`allow` HTML iframe attributes aren't exposed as component properties in this schema.

## Data Binding Examples

```javascript
// Embed an external dashboard
src: "https://grafana.example.com/d/line1-overview"

// Embed a report server URL parameterized by session variables
src: {expr: "'https://reports.example.com/view?line=' + {Root.Params.lineId} + '&shift=' + {session.custom.shift}"}

// Locally hosted static HTML help page
src: "http://localhost/help/line1-manual.html"
```

## Common Gotchas
- The property is `src`, not `source` — easy to get wrong since most other Perspective components (Image, Audio) use `source`.
- Most third-party sites (including many SaaS dashboards) send `X-Frame-Options: DENY` or a restrictive `Content-Security-Policy: frame-ancestors`, which **blocks embedding entirely** regardless of Perspective configuration — this shows as a blank frame with no error surfaced in Ignition; check the target site's headers first.
- Mixed content: if the Perspective session is served over HTTPS, an `http://` iframe source is blocked by the browser — always use HTTPS sources in production.
- This component provides **no bidirectional communication** with the framed page's content by default — passing data in/out requires the embedded page to implement `postMessage` handling, which Perspective does not automate for you.
- Not a substitute for a native Perspective view — prefer building in-platform whenever the source supports it; iframe is best for genuinely external, already-existing web apps/reports.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
