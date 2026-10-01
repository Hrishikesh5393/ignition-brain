# ISA-101 High-Performance HMI

Principles from **ANSI/ISA-101.01-2015** (HMI for process automation) and the
"high-performance HMI" practice it codifies. This is the universal layer — *what a
good HMI is and why*. The exact palette, type scale, component whitelist and
display-level content for this deployment are in the project HMI style guide.

Standards principles below are stated from knowledge; items flagged `unverified:` are
not backed by a gateway read. Perspective mechanism claims are backed by the
component schema (`schema/perspective/**`,
`skill/references/gateway/component-schemas.md`).

## Core idea

The screen is quiet when the plant is normal, and draws the eye **only** to what is
abnormal or actionable. Operators should detect a developing upset from the display
*before* the alarm, and never hunt for the one number that matters among fifty that
don't.

## Display hierarchy (ISA-101 Level 1–4)

| Level | Name | Scope | Contains | Does **not** contain |
|---|---|---|---|---|
| **1** | Operation / area overview | Whole area or process unit, "at a glance" health | KPIs, trends of the 3–6 process-critical variables, abnormal-condition indication, navigation to L2 | Individual valve faceplates, setpoint entry, raw tag dumps |
| **2** | Unit control | One process unit | Process schematic, equipment status, primary controls, alarm shelf for the unit | Full loop tuning, diagnostics |
| **3** | Equipment / loop detail | One equipment item or control loop | All parameters for that item, mode control, interlock status, related trends | Unrelated equipment |
| **4** | Diagnostic / faceplate / support | Sub-component, config, help | Diagnostics, tuning, manuals, config detail | Anything an operator needs during a normal shift |

Navigation is **hierarchical and consistent**: every display has a fixed home/back
path, L1→L2→L3 drill-down in the same place on every screen, and no dead ends.

## Colour

| Rule | Why |
|---|---|
| Base palette is **low-contrast greyscale** — light-to-mid grey background, dark-grey equipment lines, off-white workspace | Reserves the eye's contrast budget for abnormal states |
| **Saturated colour = abnormal only.** Red / amber / (sometimes) magenta appear *only* on active alarms or abnormal conditions | A red pump that is simply "running" trains the operator to ignore red |
| Running/stopped shown by **shape, fill pattern, or a small state label**, not by green vs red | ~8% of male operators have red-green deficiency; colour alone fails |
| One consistent alarm-colour → priority map across every display (see below) | Operator learns it once |
| No colour as the *sole* carrier of meaning — pair with text, position, or shape | Accessibility + printing + projector drift |

**Alarm colour ↔ priority (ISA-18.2 priorities; typical high-performance mapping —
`unverified:` exact hex is a site choice in the project conventions):**

| Priority | Typical treatment |
|---|---|
| Critical | Red fill / red border, highest-contrast, may flash until ack |
| High | Amber/orange |
| Medium | Yellow |
| Low | Pale yellow / dark outline only |
| Diagnostic | No operator annunciation on the graphic; journal only |

Ignition alarm priority enum is `Diagnostic, Low, Medium, High, Critical` (verified,
`skill/references/standards/alarms.md`) — map site colours to those five names.

## Value presentation

- **Analog over digital.** Show a moving analog indicator / bar / radial with the
  normal band, alarm limits, and current value marked — the shape tells the operator
  "near the top of normal" faster than a 4-digit readout.
- Put a **sparkline or short trend** next to any value where rate-of-change matters.
- Show **engineering units and a sensible number of significant figures** — not
  `73.418206 °C`.
- Deviation from setpoint is usually more useful than the raw PV.
- Quiet, consistent number formatting; right-align columns of numbers.

## Layout & chrome

- **Consistent placement:** the same information type lives in the same screen region
  on every display (title/nav top, alarm ribbon one fixed edge, process area centre).
- **Minimal chrome:** no 3-D bevels, gradients, drop shadows, glossy tanks, photoreal
  equipment. Flat 2-D line symbols.
- Grid-aligned; generous whitespace; group by process relationship, not by tag folder.
- Static labels dim; dynamic values prominent.
- One screen = one operator job. If it needs a scrollbar to do that job, it is two
  screens.

## Applying it in Perspective

| Do | Mechanism |
|---|---|
| Centralise colour, type, spacing in **one theme** + **style classes** | Perspective theme CSS + `props.style.classes`; never per-component inline `props.style.*` for anything reused |
| Build faceplates once, embed them | `ia.display.view` (`props.path` + `props.params`, project-relative path) and `ia.display.flex-repeater` (`props.path` + `props.instances`) — verified keys, `skill/references/gateway/component-schemas.md` |
| Restrict the component palette | Agree a **whitelist** (label, moving-analog-indicator, linear-scale, cylindrical-tank, sparkline, simple table, flex/coord containers, symbols) and a **blacklist** (gauges with chrome, gradient fills, `iframe` for core content, audio as the only alarm cue) in the project HMI style guide |
| Keep views composable | Small views + params + indirect tag bindings (`tagPath` + `mode:"indirect"` + `references`), so one faceplate serves every instance |
| Alarm annunciation on screen | `ia.display.alarmstatustable` for the shelf/ribbon; per-symbol abnormal state driven by a binding on the tag's alarm state |

Colour/spacing tokens, the type scale, the component whitelist, the display-level
content definitions, and the navigation model are all the project HMI style guide.
Equipment structure that navigation follows: `skill/references/standards/isa95.md` and
the project equipment hierarchy.

## agent rules

1. Grey by default. Saturated colour only for abnormal/actionable.
2. Never encode state with green-vs-red alone — add shape or text.
3. Every graphic gets its numbers as analog indication with the normal band shown,
   not bare digits.
4. Colour ↔ priority map comes from the project HMI style guide; use it unchanged.
5. Style via theme + style classes. An inline `props.style` on a reused element is a
   review failure.
6. Faceplates are embedded views with params — build once, never copy-paste per unit.
7. Same info type, same screen region, every display. Fixed back/home nav.
8. If the brief doesn't name a display level, ask which of L1–L4 the view is — the
   content rules differ.

## Smells

- A P&ID-style mimic with glossy 3-D tanks and a green "RUN" pump.
- Colour used decoratively (blue headers, coloured section bands).
- A screen that is mostly a grid of numeric readouts.
- Per-component inline colours duplicated across 20 components instead of a style
  class.
- One monster view with `if instance == ...` logic instead of a parameterised
  embedded faceplate.
- Alarm state only audible (audio component) with no on-screen indication.
- Navigation depth > 4, or drill-down links in a different place on each screen.
- Diagnostic-priority alarms annunciated on the operator graphic.
