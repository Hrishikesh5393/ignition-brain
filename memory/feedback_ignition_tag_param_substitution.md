---
name: feedback-ignition-tag-param-substitution
description: "Ignition UDT {Param} substitution only works inside expression-type tag bindings, never inside a plain memory tag's static \"value\" field"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6c9a969c-e21b-416c-bf0d-2ea751dc079a
---

In Ignition tag-config JSON, `{ParamName}` substitution of a UDT parameter only
resolves inside binding-type fields - an `expression`-type tag's `expression`
text, a tag-path string, an alarm `setpointA` bound as `{"bindType":
"Expression", ...}`, etc. It does **not** resolve inside a plain `memory`-type
tag's static `"value"` field - writing `"valueSource": "memory", "value":
"{TempTarget}"` imports without error but the value never links to the
parameter; Designer shows it as a normal unbound field needing per-instance
manual entry.

**Also written into the project itself** (portable, survives a tool switch):
`PROGRESS.md` in `ClarityGardens_RoomSim`'s root has this same gotcha in its
"Lessons learned" section - that's the copy to trust if this memory file and
the project ever drift apart.

**Why:** Discovered building the `Cultivation Room` UDT for
[[project_clarity_gardens_multiroom]] (2026-07-14) - added `TempTarget`/
`HumidityTarget`/`CO2Target` UDT parameters specifically to avoid duplicating
literal setpoint numbers per room instance, tried to memory-tag-template them
with `{Param}`, and the user caught it live in Designer after import
("temp target value tag is not linked to temp target parameter"). Meanwhile
`{PhaseOffset}` in the same UDT worked fine everywhere, because it was only
ever used inside `expression`-type tags (sine wave formulas).

**How to apply:** if a UDT member needs a value that varies per instance,
either (a) make the member itself `valueSource: "expr"` referencing the
parameter directly (read-only consequence: it can no longer be freely
overridden/written at runtime by an operator), or (b) keep it a plain
overridable `memory` tag with a literal default in the UDT definition, and set
the per-instance value via a nested member-override tree in the instance's
tag-import JSON (`"tags": [{"name": "Temperature", "tags": [{"name":
"Setpoints", "tags": [{"name": "Target", "value": 74.0}]}]}]`) or by hand in
Designer's Tag Browser (green-dot override). Don't reach for `{Param}`
templating on a memory tag's `value` - it silently does nothing.
