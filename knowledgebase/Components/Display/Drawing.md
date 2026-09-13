> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Drawing

**Category:** Display | **Ignition:** ia.shapes.svg (**corrected 2026-07-28, second correction**: real palette entry is `{"id":"ia.shapes.svg","palette":{"category":"display","name":"Drawing"}}` — confirmed directly against `ia.components.json` AND against a live Designer's own copy-paste export of a real component instance. An earlier "fix" to `ia.container.drawing` was itself wrong — that string exists in the registry but isn't this component; it was never verified against a live instance, only inferred from an unrelated SVG-import file. Lesson: verify against `ia.components.json` or a real Designer export directly, don't infer from adjacent examples.)

`props.elements` is a real, flat array — each entry is `{type: "<shape>", name, fill: {paint,...}, stroke: {paint,width,...}, ...geometry}` with NO nested `props` wrapper per element. **The `type` value here is the SHORT shape name (`rect`, `circle`, `line`, `polygon`), NOT the `ia.shapes.*` palette ID** — that longer ID only names the top-level draggable component in the registry, not the value used inside an element list. Using the long form silently fails: Designer auto-corrects most `ia.shapes.X` values down to `X` on save, but at least one occurrence didn't correct and instead fell back to `type:"group"` (an empty/invisible element) — caught by comparing the file after a Designer save against what was authored. Confirmed shape types in the registry: `ia.shapes.rect` (`x,y,width,height`), `.circle` (`cx,cy,r`), `.ellipse`, `.line` (`x1,y1,x2,y2`), `.polygon`/`.polyline` (`points`), `.path` (`path` = SVG d-string), `.text`, `.group` (nested `elements`), plus compound shapes `perspective-arc` (`specialPath: {x,y,width,height,start,end,slice}`) and `perspective-star`. `fill`/`stroke` shapes confirmed against `schemas/svg-fill.json` (`paint`,`opacity`,`rule`) and `schemas/svg-stroke.json` (`paint`,`width`,`opacity`,`dashArray`,`dashoffset`,`linecap`,`linejoin`,`miterlimit`) in the same jar.

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.elements | array | [] | ✓ | Array of drawable shape/path definitions |
| props.viewBox | string | "0 0 100 100" | ✓ | SVG viewBox coordinate space |
| props.style | object | {} | ✓ | Container CSS |
| props.preserveAspectRatio | string | "xMidYMid meet" | ✓ | SVG scaling behavior |

## Data Binding Examples

```javascript
// Static piping/vessel outline defined as SVG-like element objects
props.elements: [
  {type: "rect", x: 10, y: 10, width: 80, height: 40, style: {fill: "#CCCCCC", stroke: "#000"}},
  {type: "circle", cx: 50, cy: 70, r: 15, style: {fill: "#229AD6"}}
]

// Dynamically color a shape based on a tag (element style bound via expression on element array)
props.elements: {expr: "
  [{'type':'rect','x':10,'y':10,'width':80,'height':40,
    'style':{'fill': {Root.TankLevel.value} > 80 ? '#F55353' : '#0AA648'}}]
"}

// Fixed piping diagram, size scales responsively via viewBox
props.viewBox: "0 0 400 200"
```

## Common Gotchas
- `elements` is a raw array of shape-definition objects (rect/circle/path/line/polygon/text) — building complex P&ID-style graphics by hand in this array is tedious; most real projects use pre-built vector graphics (SVG imported as an Image, or a Symbol Factory-style library) instead of Drawing for anything beyond simple dynamic shapes.
- Coordinates are relative to `viewBox`, **not** pixels — resizing the component on-canvas rescales everything proportionally; get `viewBox` wrong and shapes appear tiny or clipped.
- There is no drag-and-drop visual editor for `elements` in Designer — it's authored as JSON/array data, typically via a script or exported from an external SVG-to-JSON conversion, which is a real productivity gotcha vs. other display components.
- Dynamic per-element styling (e.g. color-by-value on individual shapes) requires rebuilding the whole `elements` array via expression/script on every change — there's no per-element sub-binding path.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
