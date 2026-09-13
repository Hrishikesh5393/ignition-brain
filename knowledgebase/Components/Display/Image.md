> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Image

**Category:** Display / General | **Ignition:** ia.display.image

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| source | string | "" | ✓ | Path to image (project resource path, URL, or data-URI) |
| altText | string | "" | ✓ | Accessibility alt text |
| fit.mode | string | "none" | ✓ | `none`, `fill`, `contain`, `cover`, `percent`, `absolute` |
| fit.width / fit.height | number | 100 / 100 | ✓ | Target size when `fit.mode` is `percent` or `absolute` |
| fit.scroll | boolean | false | ✓ | Allow scrolling when the image exceeds its container |
| tint.enabled | boolean | false | ✓ | Apply a color tint over the whole image |
| tint.color | string (color) | "#CCCCCC" | ✓ | Tint color (only when `tint.enabled`) |
| style | object | {} | ✓ | Container CSS (border, background, opacity, filter) |

There is no `style.objectFit`/`style.objectPosition` or `tooltipText` property — fit behavior is its own `fit` object (with a different enum than CSS `object-fit`: no `scale-down`, but adds `percent`/`absolute`), and tinting is a dedicated `tint` object, not a CSS filter.

## Data Binding Examples

```javascript
// Static project image resource
source: "Images/logo.png"

// Dynamic image from a tag path (base64 blob converted to data-URI in a transform)
source: {tag: "[default]Line1/CameraSnapshot", transform: "toDataUri"}

// Expression selecting an icon-style image based on status
source: {expr: "{Root.Status.value} = 1 ? 'Images/ok.png' : 'Images/fault.png'"}

// Fit to container without distortion, tint red when in fault
fit.mode: "contain"
tint: {expr: "{Root.Status.value} = 0 ? {'enabled': true, 'color': '#F55353'} : {'enabled': false}"}
```

## Common Gotchas
- `source` expects a *path string*, not a binary blob directly — binary/BLOB tag data must go through a script transform that converts to a base64 data-URI (`"data:image/png;base64,..."`) before assignment.
- Relative paths resolve against the project's `Images` resource folder; a leading `/` or full URL bypasses that and is treated as absolute/external.
- `fit.mode: "fill"` distorts aspect ratio — use `contain` or `cover` unless distortion is intentional. There is no CSS-style `scale-down` option here.
- No native click/rotate/zoom interaction — those require wrapping in a container with event scripts or using the Drawing component instead.
- Referencing a non-existent project image path fails silently (broken image icon) rather than throwing a binding error — check browser dev tools network tab when an image doesn't render.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
