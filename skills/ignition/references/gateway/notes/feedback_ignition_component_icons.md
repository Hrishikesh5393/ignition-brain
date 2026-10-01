---
name: feedback-ignition-component-icons
description: "Why SDK-built Perspective components show a folder glyph in the Designer project browser, and the exact fix"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73fda676-3a9b-4234-851f-8c4403970773
  modified: 2026-08-08T13:46:54.001Z
---

A custom Perspective component built through `ComponentDescriptorImpl.ComponentBuilder` shows the nav tree's **default glyph (looks like a folder)** unless the descriptor carries an icon. `ComponentNode` does exactly one thing: `descriptor.getIcon().ifPresent(this::setIcon)`.

**Why:** Ignition's own components never go through `ComponentBuilder` - they load from `ia.components.json` via `ComponentDescriptorImpl.fromJson(..., Function<String,Icon>, ...)`, and the designer resolves the icon by `substringAfterLast(id, ".")` → `/images/components/<name>.svg` inside `perspective-designer.jar`. Module components get no such lookup. `addPaletteEntry`'s 4th arg is the palette *thumbnail*, not the tree icon.

**How to apply:**
- `ComponentDescriptorImpl.icon` is `final` → must be set at build time via `.setIcon(Icon)`.
- `InteractiveSvgIcon` is **designer scope**; referencing it from `common` NoClassDefFoundErrors the gateway at class init. So expose `descriptor(Icon)` per component - gateway hook passes `null`, designer hook passes the real icon. `getIcon()` is `Optional.ofNullable`, so null is safe.
- Icon convention: 16×16 viewBox, flat fill, `#445C6D` normal / `#FFF` `-selected` / `#808080` `-disabled`.
- **`InteractiveSvgIcon.createIcon` loads every variant eagerly and NPEs if `-disabled` is missing.** Ship all three.

Verify headlessly before installing: compile a tiny main that calls `createIcon` on each resource with the designer jar + `Ignition/lib/core/{client,common}` on the classpath. See [[project_ignition_component_library]].
