> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Flex Container

**Category:** Container / Layout | **Ignition:** ia.container.flex

## Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| direction | string | "row" | Flex direction: `row`, `row-reverse`, `column`, `column-reverse` |
| wrap | string | "nowrap" | `nowrap`, `wrap`, `wrap-reverse` |
| justify | string | "flex-start" | Main-axis alignment: `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` (this is Ignition's actual prop name - **not** `justifyContent`) |
| alignItems | string | "stretch" | Cross-axis alignment per line: `flex-start`, `flex-end`, `center`, `stretch`, `baseline` |
| alignContent | string | "stretch" | Cross-axis alignment of wrapped lines as a group (only matters when `wrap` is on and there are multiple lines) |
| style | object | {} | Standard style object (background, border, padding, classes, etc.) |

> Verified against `ia.components.json` inside `perspective-common-3.3.7.jar`, Ignition 8.3.7.
> All five layout props plus `style` are listed in the schema's `required` array. The
> property is `justify`, not `justifyContent` - a common mistake carried over from raw CSS
> habits. See [16-PERSPECTIVE-SCHEMA-TRUTH](../../16-PERSPECTIVE-SCHEMA-TRUTH.md) for why
> the prop wins over the style.

The container maps its props straight onto CSS, from `PerspectiveComponents.<hash>.js`:

```
direction -> flexDirection      alignItems   -> alignItems
wrap      -> flexWrap           alignContent -> alignContent
justify   -> justifyContent
```

## Child Component Properties

Every child placed inside a Flex Container gets a `position` object (Position category in
the Property Editor). `grow`, `shrink` and `basis` are in the schema's `required` array.
The container maps them onto CSS the same way: `align -> alignSelf`, `grow -> flexGrow`,
`shrink -> flexShrink`, `basis -> flexBasis`, `display -> display`.

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| position.grow | numeric | 0 | Flex-grow factor. Exactly one child per row/column should usually get `grow: 1` to consume remaining space. |
| position.shrink | numeric | 1 | Flex-shrink factor. **Set explicitly to 0 on every fixed-size child** - CSS defaults `shrink` to 1, so "fixed" sections can still compress under content pressure if you only set `grow: 0`. |
| position.basis | string/numeric | "auto" | Flex-basis: fixed px size, a percentage, or `auto` (size to content) |
| position.align | string | - | Per-child cross-axis override. Emits `alignSelf`. |
| position.display | **boolean** | **true** | `false` emits `display: none` and removes the child from layout. It is not the CSS `display` keyword and does not take `"flex"`. |

## Responsive Configuration Example

```python
# Flex Container: responsive direction via expression binding
direction = "{expr: if({view.params.screenWidth} < 768, 'column', 'row')}"

# Gap is achieved via style, not a dedicated gap property in older 8.x -
# on 8.3 use style.gap directly:
style.gap = "16px"
style.padding = "20px"
```

## Layout Example

```python
# Root view container convention (confirmed from real prod views):
# Root is ALWAYS ia.container.flex, direction: "column" - never a
# Coordinate Container at the top level of a page.

# Header row - fixed height, never compresses
header.position.grow = 0
header.position.shrink = 0
header.position.basis = "60px"

# Content area - consumes all remaining vertical space
content.position.grow = 1
content.position.shrink = 1

# Footer row - fixed height, never compresses
footer.position.grow = 0
footer.position.shrink = 0
footer.position.basis = "40px"
```

```python
# Horizontal bar with a spacer to push content right without
# justify: "space-between" (seen literally named "Filler" in prod views)
leftCluster.position.grow = 0
leftCluster.position.shrink = 0

spacer.position.grow = 1   # invisible filler, e.g. a blank Label

rightCluster.position.grow = 0
rightCluster.position.shrink = 0
```

## Common Gotchas

- **Prop is `justify`, not `justifyContent`.** Putting `justifyContent` in `style` is *accepted* - `style` has no `additionalProperties: false`, so it binds and is written to the DOM. Then the container's own render style overwrites it, because component-emitted style is merged on top of `props.style`. So it looks configured in the Designer and does nothing at runtime, which is why this one costs so much time. Same for `flexDirection`, `flexWrap`, `alignItems`, `alignContent`.
- **The parent's `position` beats the child's own `style`.** Child-position layout is applied last in the style chain. A `style.width` on a flex child loses to `basis` on the main axis, and with the default `shrink: 1` the container is free to squeeze it.
- **The cross axis is not the child's to set.** It comes from the parent's `alignItems`, default `stretch`. A row inside a `column` container is already full width, so a `width: 100%` that seems to help is masking a different problem.
- **Always set `position.shrink: 0` explicitly on fixed-size children.** Relying on the default (`1`) is the #1 cause of "my fixed header/footer got squished" bugs - CSS flexbox shrink defaults to 1 regardless of `grow`.
- **Coordinate vs. Flex for page root:** use Flex (`direction: "column"`) for the page root, not Coordinate Container - Coordinate is for small fixed-geometry widgets (gauges, overlays), not whole-page structure.
- **Wrapping + fixed row height clips content.** If a row's children `wrap`, the row itself must NOT have a fixed `position.basis` - use `shrink: 0` alone (auto height) or wrapped rows get clipped.
- **Nesting depth:** minimize nested Flex Containers for complex layouts - each nesting level adds a reflow pass; prefer flat structures with `wrap` over deep nesting where possible.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
