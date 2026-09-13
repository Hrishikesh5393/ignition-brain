> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Coordinate Container

**Category:** Container / Layout | **Ignition:** ia.container.coord

> Verified against `ia.components.json` in `perspective-common-3.3.7.jar`, Ignition 8.3.7.

## Palette variants

The palette exposes three entries backed by the same component id:

| Variant id | Label | Props applied |
|---|---|---|
| (none) | Coordinate | defaults |
| `coord-fixed` | Fixed | defaults |
| `coord-percent` | Percent | `mode: "percent"` |

## Properties

Schema declares `required: ["mode", "aspectRatio", "style"]` and `additionalProperties: false`.

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| mode | string enum `fixed` \| `percent` | `"fixed"` | `fixed` - child layouts stay in fixed pixel coordinate space regardless of container resize. `percent` - child position/size scale relative to the container's current size. |
| aspectRatio | string | `""` | Only applies in `percent` mode. `"x:y"` string, e.g. `"16:9"`. Missing or invalid value defaults to `1:1`. Editor shows it only when `mode == "percent"` (`visibleWhen`). |
| pipes | array | `[]` | Pipe segments drawn by the container itself. See below. |
| style | object | `{"classes": ""}` | Standard style object |

> This is the **default root container** when creating a new view in the Designer (though real production page roots almost always switch to a Flex Container instead - see Flex Container gotchas). Once a view's root container type is chosen at creation, it cannot be changed later without recreating the view.

## Pipes

Pipes are **not a component**. There is no `ia.display.pipe` in the palette. Pipes are an
array property on the Coordinate Container, and they render as part of the container.

Each entry requires `appearance`, `width` and `origin`:

| Field | Type | Default | Notes |
|---|---|---|---|
| name | number \| string | - | Label shown in the Designer project browser |
| appearance | string enum `auto` \| `p&id` \| `mimic` \| `simple` | `"auto"` | `auto` follows session prop `pipes.autoAppearance` |
| flanges | boolean | `true` | Only when appearance resolves to `mimic` |
| lineVariant | string enum `solid` \| `dashed` \| `midArrow` \| `wavy` | `"solid"` | Only when appearance resolves to `p&id` |
| start | string enum `none` \| `arrowInward` \| `arrowOutward` | `"none"` | Only when appearance resolves to `p&id` |
| end | string enum `none` \| `arrowInward` \| `arrowOutward` | `"none"` | Drawn on connections with no further connection |
| fill | string (color) | `""` | Only when appearance resolves to `mimic` or `simple` |
| stroke | string (color) | `""` | Always applies |
| width | number | `10` | |
| origin | point | `{x:0, y:0, connections:[]}` | Recursive: a point carries a `connections` array of further points |
| visible | boolean | `true` | |

A pipe is a tree of points, not a polyline. `origin.connections[]` holds child points,
each of which has its own `connections[]`. That is how branches are expressed.

Session props that govern pipes:

- `pipes.autoAppearance` - enum `p&id` \| `mimic` \| `simple`, default `simple`
- `pipes.overlapGap` - number, default `4`

### Event

`onPipeClicked` is declared on the Coordinate Container, with payload:

| Field | Type |
|---|---|
| pipeIndex | number, index into `props.pipes` |
| pipeName | string |
| event | the mouse event: `altKey`, `button`, `buttons`, `clientX/Y`, `ctrlKey`, `metaKey`, `pageX/Y`, `screenX/Y`, `shiftKey` |

One event covers every pipe. The pipe identity travels in the payload, because
component events are declared per component **type**, not per instance.

## Child Component Properties

`childPositionSchema` declares `required: ["x", "y"]` and `additionalProperties: false`.
Only `x`, `y` and `rotate` carry defaults - `width` and `height` have none.

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| position.x | css-length (number or string) | 0 | Horizontal offset from the container's top-left. Pixels in `fixed` mode; a 0-1 decimal fraction of container width in `percent` mode. |
| position.y | css-length | 0 | Vertical offset from the container's top-left. Pixels in `fixed` mode; 0-1 fraction of container height in `percent` mode. |
| position.width | css-length | none | Component width. Pixels (`fixed`) or 0-1 fraction (`percent`). |
| position.height | css-length | none | Component height. Pixels (`fixed`) or 0-1 fraction (`percent`). |
| position.rotate.anchor | string | "50% 50%" | Anchor point for rotation, as a CSS-style percentage or keyword pair |
| position.rotate.angle | string | "0deg" | Rotation angle, in degrees or any valid CSS angle unit |

## Responsive Configuration Example

```python
# Percent mode: children scale proportionally as the container resizes
mode = "percent"
aspectRatio = "16:9"

# A gauge pinned to the top-right corner, 20% of container width,
# regardless of actual pixel size at runtime
gauge.position.x = 0.75
gauge.position.y = 0.05
gauge.position.width = 0.20
gauge.position.height = 0.20
```

## Layout Example

```python
# Fixed mode: pixel-perfect overlay - e.g. a status badge on top
# of a background diagram, common for schematic/P&ID-style views
mode = "fixed"

diagram.position.x = 0
diagram.position.y = 0
diagram.position.width = 1200
diagram.position.height = 800

statusBadge.position.x = 1050    # overlaps diagram via z-order (declaration order)
statusBadge.position.y = 20
statusBadge.position.width = 120
statusBadge.position.height = 40

# Rotated indicator needle
needle.position.rotate.anchor = "50% 100%"
needle.position.rotate.angle = "{expr: {tag.value} * 3.6 + 'deg'}"  # 0-100 -> 0-360deg
```

## Common Gotchas

- **Not for whole-page layout.** Coordinate Container is real and commonly used (small fixed-geometry widgets: gauges, meters, popups, diagram overlays) but is almost never the right choice for a full page's structure - that job belongs to a root Flex Container. Nesting a page's entire content in Coordinate Container is the single most common "why doesn't this resize on mobile" complaint.
- **`fixed` mode does not resize with the viewport.** If the container itself is stretched but `mode` is `fixed`, children stay pixel-anchored and get clipped or leave dead space - switch to `percent` mode if the container's outer size is expected to vary.
- **z-ordering is purely declaration order**, not an explicit z-index property - components declared later in the child list render on top. To reorder stacking, reorder the children in the project browser tree.
- **`aspectRatio` only works in `percent` mode** - setting it while `mode: "fixed"` has no effect.
- **Rotation pivots from `position.rotate.anchor`**, not the component's top-left corner - get the anchor wrong and rotation animations appear to "orbit" instead of spinning in place.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
