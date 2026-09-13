> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Breakpoint Container

**Category:** Container / Layout | **Ignition:** ia.container.breakpoint

## Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| breakpoint | numeric | 960 | Width (in pixels) at which the container switches between its two child layouts. Below this width, children tagged for the "small" layout render; at or above it, the "large" layout renders. |
| determinant | string | "width" | Which dimension of the container triggers the breakpoint switch: `width` or `height` |
| currentBreakpoint | string (read-only) | — | Reports which breakpoint is currently active: `"small"` or `"large"`. **New in 8.3.4** — usable in bindings/scripts to react to the active state, but cannot be written to. |
| style | object | {} | Standard style object |

> Unlike Column Container, Breakpoint Container has only **one** numeric breakpoint (a single small/large split), not an array of named breakpoints. Don't confuse the two — Column Container is the one with a `breakpoints` array and 3 tiers (sm/md/lg).

## Child Component Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| position.size | string | "large" | Which layout this child belongs to. Expected values: `"small"` or `"large"`. A child with `position.size: "small"` only renders/exists when `currentBreakpoint` is `"small"`, and vice versa — they are **completely separate component instances**, not the same component reflowed. |

## Responsive Configuration Example

```python
# Breakpoint Container: single width breakpoint at 768px
breakpoint = 768
determinant = "width"

# Desktop nav (Flex Container as child), tagged for large layout
desktopNav.position.size = "large"

# Mobile hamburger menu (different component entirely), tagged for small
mobileNav.position.size = "small"

# React to the active breakpoint elsewhere in the view via binding:
# {view.root.currentBreakpoint} == "small"
```

## Layout Example

```python
# Typical use: swap an entire nav structure, not just resize it
# Large breakpoint: full horizontal menu bar
navBarLarge.position.size = "large"
navBarLarge.type = "ia.container.flex"   # direction: row, full menu items

# Small breakpoint: collapsed hamburger + drawer
navBarSmall.position.size = "small"
navBarSmall.type = "ia.display.icon"     # single hamburger icon component
```

## Common Gotchas

- **Only two states, no middle tier.** If you need 3+ responsive tiers (mobile/tablet/desktop), use Column Container instead — Breakpoint Container is strictly binary (small/large).
- **Children are separate instances, not one reflowed component.** Because each `position.size` value creates an entirely distinct component tree, state (e.g., a Text Field's typed value) does **not** carry over when the breakpoint flips — each side starts fresh. Don't put critical live user-input state directly inside a Breakpoint Container child unless you bind it to a shared prop/tag outside the container.
- **`currentBreakpoint` is read-only.** You cannot force the breakpoint state via this property — only the container's actual measured width/height (per `determinant`) drives it. Use CSS/session-width workarounds if you need to force a breakpoint for testing.
- **Choose `determinant` deliberately.** Defaulting to `width` is correct for most nav/dashboard use cases, but a container nested in a Split Container or resizable panel may need `height` as the trigger instead.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
