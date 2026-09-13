> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Accordion

**Category:** Embedding | **Ignition:** `ia.display.accordion`

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| expansionMode | string | "multiple" | ✓ | `single` (only one section open at a time) or `multiple` |
| items | array | — | ✓ | Accordion sections: `{expanded, header, body}` |
| items[].expanded | boolean | false | ✓ (bidirectional) | Whether this section is open — read and written to |
| items[].header.toggle | object | — | ✓ | Toggle icon config (`enabled`, `expandedIcon`, `collapsedIcon`) |
| items[].header.content | object | — | ✓ | Header content — text or an embedded view (`viewPath`/`viewParams`) |
| items[].header.height | string | "40px" | ✓ | Header row height |
| items[].header.reverse | boolean | false | ✓ | Reverse toggle/content order |
| items[].body.viewPath / .viewParams | string / object | "" / {} | ✓ | Embedded view shown when the section is expanded |
| items[].body.height | string | "auto" | ✓ | Body height |
| unusedSpaceStyle | object | {} | ✓ | Styling for any unused space in the container |
| style | object | {} | ✓ | Container CSS |

## Common Gotchas
- Each section's body is an **embedded view** (`viewPath`/`viewParams`), not inline child components — content is composed the same way as Embedded View, not placed directly inside the Accordion.
- `items[].expanded` is bidirectional — reading it back tells you which sections are currently open; setting it programmatically opens/closes that section.
- `expansionMode: "single"` doesn't automatically collapse other sections when you set one `expanded: true` via script — verify behavior in the Designer if you need mutual-exclusivity enforced from scripting rather than user clicks.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
