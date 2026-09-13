> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Label

**Category:** Display / General | **Ignition:** ia.display.label

## Properties

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| props.text | string | "Label" | ✓ | Text content displayed |
| props.style | object | {} | ✓ | CSS styling (color, fontSize, fontWeight, textAlign, etc.) |
| props.textStyle | object | {} | ✓ | Text-specific style block separate from container style |
| props.tooltipText | string | "" | ✓ | Hover tooltip text |
| props.overflow | boolean | true | ✓ | Whether overflowing text is clipped/ellipsized |
| meta.name | string | "Label" | — | Component name in tree (not a bindable prop) |
| position.* | object | — | ✓ | Standard layout position props (grow/shrink/basis in flex parents) |
| visible | boolean | true | ✓ | Component visibility (standard on all components) |

## Data Binding Examples

```javascript
// Tag binding to text
props.text: {tag: "[default]Line1/CurrentProduct"}

// Expression binding with formatting
props.text: {expr: "toStr({Root.Gauge.value}, \"0.0\") + \" °C\""}

// Property binding from a sibling component
props.text: {bidirectional: false, path: "Root.Params.title"}

// Conditional styling via expression
props.style.color: {expr: "{Root.Alarm.active} ? '#F55353' : '#0AA648'"}
```

## Common Gotchas
- `props.text` only accepts a string — binding a numeric or object value directly throws a render error; wrap numerics with `toStr()`.
- `textStyle` vs `style`: `style` affects the container (background, padding, border); `textStyle` affects the text run itself (font properties). Confusing the two is the most common cause of "my font-size binding does nothing."
- Long text does not auto-wrap by default in a fixed-width container — set `whiteSpace: "normal"` in `style` or the Label truncates/overflows depending on `overflow`.
- Label does **not** support HTML/markdown rendering — use the Markdown Viewer component for rich text.
- No built-in `enabled` prop — Label is always non-interactive; wrap in a container with a click handler if click behavior is needed.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
