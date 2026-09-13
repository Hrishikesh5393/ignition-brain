> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Carousel

**Category:** Embedding | **Ignition:** `ia.display.carousel`

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| views | array | — | ✓ | Slides, each `{viewPath, viewParams, direction, justify, alignItems}` |
| activePane | number | 0 | ✓ (bidirectional) | Index of the currently-displayed slide |
| lazyLoad | boolean | true | ✓ | Load slide views on demand rather than all at once |
| autoplay.enabled | boolean | false | ✓ | Auto-advance slides |
| autoplay.transitionDelay | number | 2500 | ✓ | Delay (ms) between auto-advances |
| autoplay.pauseOnHover / .pauseOnFocus / .pauseOnDotHover | boolean | false (all) | ✓ | Pause autoplay on interaction |
| behavior.transitionSpeed | number | 500 | ✓ | Slide transition duration (ms) |
| behavior.fade | boolean | false | ✓ | Fade instead of slide |
| behavior.mobileSwipeable / .desktopDraggable | boolean | true / true | ✓ | Touch/drag navigation |
| behavior.swipeThreshold | number | 200 | ✓ | Min drag distance (px) to trigger a slide change |
| appearance.dots.enabled | boolean | true | ✓ | Show navigation dots |
| appearance.arrows.enabled | boolean | true | ✓ | Show prev/next arrows |
| appearance.slidesToShow | number | 1 | ✓ | Slides visible per page (only when `behavior.fade` is `false`) |
| appearance.slidePadding | number | 20 | ✓ | Padding between slides |
| appearance.reverse | boolean | false | ✓ | Reverse slide order |
| style | object | {} | ✓ | Container CSS |

## Common Gotchas
- Each slide is an embedded view (`views[].viewPath`/`.viewParams`), same pattern as Embedded View/Accordion — not inline child components.
- `appearance.slidesToShow` only applies when `behavior.fade` is `false` — fade transitions always show one slide at a time regardless of this value.
- `activePane` is bidirectional — script-driven navigation writes to it directly (`self.props.activePane = 2`), no separate `next()`/`previous()` method call needed.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
