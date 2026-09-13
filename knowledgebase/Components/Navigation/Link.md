> **Component category:** Navigation · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Link Component

**Category:** Navigation / Hyperlink  
**Ignition Version:** 8.3+  
**Palette:** Navigation

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| url | string | "" | ✓ | Destination — a URL, URL fragment, or mounted page path (start with `/` for a mount, e.g. `/status`). Not a raw view resource path. |
| text | string | "" | ✓ | Link text/label displayed to the user |
| target | string | — | ✓ | `self` (current tab), `tab`/`blank` (new tab), `parent` (parent frame), `top` (full window) — standard W3C anchor target values |
| download | string | — | ✓ | Target filename for the browser to download when the link is a download link |
| referrerPolicy | string | — | ✓ | `no-referrer`, `no-referrer-when-downgrade`, `origin`, `origin-when-cross-origin`, `unsafe-url` |
| rel | string | — | ✓ | Standard `rel` attribute (`nofollow`, `noopener`, `external`, etc.) |
| style | object | {} | ✓ | Full styling (text, background, margin, padding, border, shape); supports style classes |

There is no `targetType`, `disabled`, `params`, `className`, `color`, `hoverColor`, `underline`, or dedicated `width`/`height`/`fontSize` property — this is a plain anchor-style component (`url`/`text`/`target` plus standard anchor attributes), not a structured view-navigation component like Embedded View. Passing parameters to a destination view isn't a built-in Link feature — encode them in the `url` query string yourself and read them on the destination side, or use Embedded View / page navigation with params instead.

---

## Purpose & Description

The Link component creates a clickable hyperlink (a plain HTML anchor) for navigating to a URL, URL fragment, or mounted page path. It does not have a `disabled` state, structured parameter passing, or a "destination type" concept — those need to be built with expressions/scripting on top of the plain `url`/`target` properties.

---

## Common Use Cases

1. **External Links** — link to external websites or resources
2. **Mounted Page Navigation** — navigate to another mounted page via its path
3. **Download Links** — trigger a file download via the `download` property
4. **Menu Links** — part of navigation menus
5. **Inline Navigation** — navigate within text content

---

## Common Bindings

```javascript
// Change destination based on user role
url: {expr: "
  switch(system.security.getRoles()[0],
    'admin', '/admin/dashboard',
    'user', '/user/dashboard',
    '/public/home'
  )
"}

// Open external docs in a new tab
url: "https://docs.inductiveautomation.com"
target: "blank"

// Mailto link
url: {expr: "'mailto:' + {Root.userEmail}"}
text: "Send Email"

// Encode a query param manually — there's no built-in params object
url: {expr: "'/item-detail?id=' + {Root.Table.selection.data[0].id}"}
```

### Event Handlers

```javascript
// onClick - fires before/alongside navigation
onClick: function(self, event) {
  system.perspective.print("Navigating to: " + self.props.url)
}
```

---

## When to Use vs. Alternatives

- **Link vs. Button:** Link navigates (to a URL/mount path); Button triggers arbitrary script logic.
- **Link vs. Horizontal Menu:** Link is a single navigation option; Horizontal Menu handles multiple, with dropdowns.
- **Link vs. Embedded View:** Link navigates the browser/page; Embedded View composes another Perspective view (with structured `params`) inline into the current one — use Embedded View, not Link, when you need real parameter passing between views.

---

## Common Errors & Solutions

### Link Not Navigating
**Cause:** `url` empty, or it's a raw view resource path instead of a mounted page path.
**Solution:** Verify `url` is a real URL/fragment or a `/`-prefixed mounted page path (check Page Configuration), not a `view.json` resource path.

### External Link Opens in Same Tab
**Cause:** `target` unset or `"self"`.
**Solution:** Set `target: "blank"` for external links.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [10-PERSPECTIVE-OVERVIEW](../../10-PERSPECTIVE-OVERVIEW.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
