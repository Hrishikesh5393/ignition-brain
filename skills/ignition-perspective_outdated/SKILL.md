---
name: ignition-perspective
description: Use when building or editing an Ignition Perspective view, component, layout, binding, event or popup - including setting any prop or style, aligning or sizing components in a flex container, writing a script transform or action, wiring tags into a component, or when a layout looks wrong, a button does nothing, a popup will not open, values show as blank, or text renders as mojibake.
---

# Perspective screen building

Perspective looks like the web platform. It renders in a browser, uses React, and its
props are named `alignItems` and `justify`. That resemblance is the trap. It is an
application whose authors made their own decisions, and those decisions are written
down in schemas and descriptors that ship with the install.

**Your web knowledge is a hypothesis here, not a fact.**

## The rule

**Before setting any prop or style on a component, open its schema.**

Not when unsure. Always. Especially when it looks familiar, because the
familiar-looking ones are what cost the most time. `justifyContent` looked familiar,
so it was never checked, and it was wrong in 113 places.

Two places to look, in order:

1. `Ignition-knowledgebase/Components/<Category>/<ComponentName>.md` - fastest, and it
   already carries the common traps.
2. The runtime schema itself, when the KB is silent, disagrees, or the version differs.
   See references/verification.md - it is four copy-pasteable recipes, none needing a
   decompiler.

## Red flags

These thoughts come immediately before the mistake:

- "This is just CSS"
- "I know how flex works"
- "It looks right now"
- "I will check if it breaks"
- "The style property is obviously the place for styling"

All of them mean: stop, open the schema.

## Rationalizations

| Excuse | Reality |
|---|---|
| "It is a style, so it goes in `style`" | Layout is props. `style` is for what flex has no prop for: padding, gap, colour, border |
| "It renders correctly now" | Looking right is not evidence of being right. A `width: 100%` masked a problem for an entire session |
| "I will read the docs if it misbehaves" | It misbehaves silently. A `scope: "C"` script action registers nothing and logs nothing |
| "The KB is probably out of date" | Check it, then check the schema. It was right and unread every time it mattered |
| "This component is simple" | The flex container is the simplest one and it has five required props and a separate child schema |

## Quick reference

The traps that come up most. Full list with provenance in references/gotchas.md.

| Doing | Wrong | Right |
|---|---|---|
| Align children in a flex container | `style.justifyContent` | prop `justify` |
| Cross-axis align | `style.alignItems` | prop `alignItems` |
| Row vs column | `style.flexDirection` | prop `direction` |
| Fixed-size child | `style.width: "104px"` | `position.basis: "104px"` + `position.shrink: 0` |
| Child fills space | `style.flex: 1` | `position.grow: 1` |
| Full-width row in a column | `style.width: "100%"` | nothing, parent `alignItems` defaults to `stretch` |
| Hide a child | `style.display: none` | `position.display: false` |
| Python on a click | `scope: "C"` | `scope: "G"` |
| Script transform body | `def transform(...):` header | body only, tab-indented |
| Many tags into one component | one binding per key | one binding on the object prop |
| Any dash in a string | `-` or `-` | `-` |

`position.grow` defaults to **0**, not 1. `position.shrink` defaults to **1**, so a
child can be squeezed below whatever size you asked for.

## When something is already broken

Symptom first, since that is how you arrive:

- **Layout ignores what you set** - the value is in `style` and belongs in a prop.
- **Button does nothing, no error** - a Python action with `scope: "C"`. There is no
  client-side `script` action, so nothing registers.
- **Component shows blank or `--`** - the binding is absent, or a value arrived with the
  wrong type. Check `propConfig` is not null before blaming the tag.
- **Text renders as mojibake** - non-ASCII punctuation in a project string.
- **Fields squeezed narrower than set** - `shrink` is 1 and the size is in `style`.

## Growing this skill

This is early. When a new trap is found: verify it against the jar, the client bundle
or the live gateway, add it to references/gotchas.md **with where it was verified**, and
only promote it into this file if it recurs often enough to earn the tokens.

Never add a claim here that has not been verified first-hand. An unverified line in a
skill is worse than no line, because it is read with authority.
