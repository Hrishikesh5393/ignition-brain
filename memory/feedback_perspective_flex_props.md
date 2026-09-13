---
name: feedback-perspective-flex-props
description: "Perspective flex containers take layout from props (justify, alignItems, direction, wrap), not from CSS in style"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73fda676-3a9b-4234-851f-8c4403970773
  modified: 2026-08-11T08:36:28.807Z
---

`ia.container.flex` declares `direction`, `wrap`, `justify`, `alignItems`, `alignContent` as REQUIRED props with defaults `row` / `nowrap` / `flex-start` / `stretch` / `stretch`. Verified in ia.components.json inside perspective-common. The container renders its flex layout from those props.

Setting `justifyContent`, `alignItems`, `flexDirection`, `flexWrap` or `alignContent` in `style` creates a second source of truth and the prop is what decides.

**The mechanism, verified 2026-08-11 in the client bundle.** `emitterFactory` in `PerspectiveClient.<hash>.js` builds the final style as `props.style` first, then `.applyCssProperties(componentRenderStyle)`, then meta, then **the parent's child-position layout**, then transforms. `applyCssProperties(...e){return Object.assign(this.style,...e),this}` is a plain merge, so later stages overwrite earlier ones. So `style.justifyContent` is not rejected (the style schema has no `additionalProperties:false`) - it binds, reaches the DOM, and is then overwritten. That is why it looks configured in the Designer and does nothing at runtime. Same chain explains why the parent's `position` always beats the child's own `style`.

Flex prop to CSS map, from `flexParentProps` / `flexChildProps`: `direction`->flexDirection, `wrap`->flexWrap, `justify`->justifyContent, `alignItems`->alignItems, `alignContent`->alignContent; child `align`->alignSelf, `grow`->flexGrow, `shrink`->flexShrink, `basis`->flexBasis, `display`->display.

**Why:** the user caught this. It was the real cause of repeated alignment problems, and it had produced silent contradictions in their project, such as a header whose style said `space-between` while its prop said `center`. 113 occurrences were migrated across the AHU_Control_Demo views.

**How to apply:** set layout on the props. Keep `style` only for what flex has no prop for - padding, gap, width, colour, border. Before styling any Ignition component, check its schema in `ia.components.json` for a first-class prop rather than assuming CSS applies. See [[project_ignition_component_library]].

## Child sizing: position, not CSS

Every child of a flex container has a `position` object. From `childPositionSchema` on `ia.container.flex`, `grow`, `shrink`, `basis` are REQUIRED:

- `grow` default **0** (not 1). Children do not expand by default.
- `shrink` default 1. The child may be squeezed below its stated size.
- `basis` default `auto`. Size along `direction`: width when row, height when column.
- `align` per-child cross-axis override.
- `display` default true; **false removes the child from layout entirely**, it is not CSS display.

A fixed-size field is `basis: "104px"` + `shrink: 0`, never `style.width`. A style width sits outside the flex negotiation and loses to it.

The cross axis is not the child's to set: it comes from the parent's `alignItems`, default `stretch`. A row inside a `column` container is already full width, so `width: 100%` on it is a crutch, and if it appears to be needed something else is wrong.

## The general rule this is an instance of

Perspective is an application built with JS, not the web platform. It resembles HTML,
CSS and React closely enough that web instincts feel like they should apply, and that
resemblance is the trap. The authors made their own decisions and wrote them down.

Before touching anything in Perspective, read the source of truth for it: the component
entry in `ia.components.json` (schema and childPositionSchema), the descriptor in the
jar, or the client bundle. Do this FIRST, not after something looks wrong, and
especially when the thing looks familiar. The dangerous cases are the familiar-looking
ones, `justifyContent` being the example that cost the most time.

Same lesson, other instances found in this project: icons need `descriptor.setIcon()`;
script actions need `scope: G` regardless of the DOM event name; script transforms
store the body with no `def` line; `Route.pathMatches` requires equal path segment
counts; `PropertyTree` has `readObject` and `readArray`.

Corollary: a change that makes something look right is not evidence it was the right
change. Adding `width: 100%` to rows looked like it fixed them and merely hid the cause.
