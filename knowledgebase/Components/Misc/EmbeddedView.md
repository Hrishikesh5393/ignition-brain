> **Component category:** Misc · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Embedded View Component

**Category:** Special / Embedding | **Palette:** Perspective - Embedding Palette
**Ignition Version:** 8.3+
**Docs source:** `perspective-components/perspective-embedding-palette/perspective-embedded-view` + `ignition-modules/perspective/views-in-perspective/embedded-views` (verified 2026-07-13)

> Qualified type string not directly confirmed in the fetched docs page; follows the `ia.<category>.<name>` convention inferred from other confirmed types (e.g. `ia.container.flex`). Verify against a real project's `view.json` before relying on it programmatically.

---

## Purpose & Description

The Embedded View component includes an entire other Perspective view inside the current one, as a reusable, parameterized unit — the primary mechanism for view composition/reuse in Perspective (e.g. a "detail card" view reused across a dashboard, list, and a popup). It is functionally distinct from **View Canvas** (dynamically swaps which view is embedded at runtime) and **View Object**/root view props (the outermost container of a view, not a nested one).

---

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| `path` | string | `""` | ✓ | Resource path of the view to embed, e.g. `"embedded/ComponentLibrary"`. When set in the Designer, an "Open View" icon appears for quick navigation to the embedded view's own editor |
| `params` | object | `{}` | ✓ | Parameters passed into the embedded view. Key names **must exactly match** the parameter names defined on the target view's `params` — mismatched names are silently dropped, not errored |
| `useDefaultViewWidth` | boolean | `false` | ✓ | If `true`, use the embedded view's own configured default width instead of stretching/shrinking to the container's content width |
| `useDefaultViewHeight` | boolean | `false` | ✓ | Same as above, for height |
| `loading.order` | string | `"with-parent"` | ✓ | Controls load timing: `"with-parent"` (loads alongside the parent view) or `"after-parent"` (defers until parent finishes loading — reduces perceived load time for heavy nested views) |
| `style` | object | `{}` | ✓ | Style applied to the embedded view's wrapper container |

---

## View/Embed Examples

```python
# Embed a reusable card, passing an id and a mode
props.path = 'embedded/ComponentLibrary'
props.params = {
    'deviceId': 42,
    'mode': 'edit',
}
```

```python
# Dynamic embed path + params driven by a selected table row
props.path = 'detail-views/device-card'
props.params = {
    'deviceId': self.parent.getChild("Table").props.selection.selectedRow['deviceId'],
    'returnTo': 'device-list',
}
```

```python
# Sizing: let a fixed-size popup card use its own natural dimensions
# instead of stretching to fill a coordinate-container region
props.useDefaultViewWidth = True
props.useDefaultViewHeight = True
```

### Reading Parameters Inside the Embedded View

Parameters arrive on the embedded view's own `params` (accessible on that view's root as `{view.params.paramName}` in bindings, or `self.view.params.paramName` in scripts):

```python
# Inside the embedded view, onStartup/onLoad-style script
deviceId = self.view.params.deviceId
mode = self.view.params.mode
```

```javascript
// Inside the embedded view, an expression binding
{view.params.deviceId}
```

---

## Common Gotchas

- **Param name mismatch fails silently.** If `props.params` on the Embedded View component has a key that doesn't exist as a parameter on the target view, there is no error in the Designer or at runtime — the value is simply unavailable inside the embedded view. Always define the parameter on the target view first, then bind to it from the parent.
- **`path` is a view resource path, not a page-mounted URL.** Don't confuse this with Link/Horizontal Menu/Menu Tree's `target`, which expects a mounted page path (`/my-page`) or external URL — Embedded View's `path` is the raw Perspective view resource path (`folder/subfolder/ViewName`), the same string you'd see in the view browser.
- **`useDefaultViewWidth`/`useDefaultViewHeight` default to `false`**, meaning by default the embedded view stretches/shrinks to fill its container — a common surprise when a view was designed at a fixed size (e.g. a modal card) and then looks stretched or squished when embedded. Set both to `true` for fixed-size cards/popups.
- **Performance with many/nested embeds**: heavy use of Embedded View — especially deeply nested embeds, or many instances on one view — can cause noticeable load and update lag, plus potential race conditions when parameters flow through multiple embed layers before the innermost view is ready. Prefer `loading.order = "after-parent"` for secondary/below-the-fold embedded content, and prefer **Flex Repeater** over many manually-placed Embedded View instances when repeating the same view for a list/collection.
- **Embedded View vs. View Canvas vs. Flex Repeater**:
  - **Embedded View** — one fixed view path, optionally parameterized, set at design time (or bound, but still one instance).
  - **View Canvas** — the *which view to show* itself is dynamic/runtime-driven (e.g. a content area that swaps views based on navigation state).
  - **Flex Repeater** — many instances of the *same* view, one per row of a dataset, each with its own params.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
