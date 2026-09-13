> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# View Canvas

**Category:** Embedding | **Ignition:** `ia.display.viewcanvas`

## Overview

Freely-positioned canvas for one or more embedded view instances, each independently placed (absolute or relative to the previous instance) and independently transitionable — distinct from Embedded View (one fixed view) and Flex Repeater (many instances of the same view in a flex layout); View Canvas allows multiple *different* views, each with its own absolute/relative position.

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| instances | array | — | ✓ | One entry per placed view: `{position, top, left, bottom, right, zIndex, width, height, viewPath, viewParams, style}` |
| instances[].position | string | "absolute" | ✓ | `absolute` (offset from canvas origin) or `relative` (offset from the previous relative instance) |
| instances[].top / .left / .bottom / .right | CSS length | "0px" / "0px" / "auto" / "auto" | ✓ | Position offsets (meaning depends on `position` mode) |
| instances[].zIndex | string\|number | "auto" | ✓ | Stacking order |
| instances[].width / .height | CSS length | "auto" / "auto" | ✓ | Instance size |
| instances[].viewPath / .viewParams | string / object | — | ✓ | The view rendered at this position |
| transitionSettings.duration / .timingFunction / .delay | CSS time / string / CSS time | — | ✓ | Transition applied when an instance's position/size changes |
| enableTransitions | boolean | true | ✓ | Enable/disable transitions globally |
| useDefaultViewWidth / useDefaultViewHeight | boolean | true / true | ✓ | Use each view's own default size (overrides any per-instance width/height) |
| defaultStyle | object | {} | ✓ | Style applied to all instances by default |
| style | object | {} | ✓ | Container CSS |

## Common Gotchas
- `position: "relative"` offsets from the **previous relative instance's** bottom-left corner (or the canvas origin, if it's the first) — it is not the same as CSS `position: relative`, which offsets from an element's own normal flow position.
- `useDefaultViewWidth`/`useDefaultViewHeight` (both default `true`) override any per-instance `width`/`height` — set them `false` if you need explicit per-instance sizing to actually apply.
- Multiple different views can be placed here (unlike Flex Repeater, which repeats one view) — use View Canvas for a free-form composition of distinct views, Flex Repeater for many instances of the same view over a dataset, and Embedded View for a single fixed view.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
