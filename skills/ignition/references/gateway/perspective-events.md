# Perspective events: component event scripts vs. ActionConfig actions

> **See also:** `references/gateway/deep/perspective-schema-truth.md` §8 ("Client action scopes") — the client-side `ActionRegistry` dispatch code (`if ("C" === scope) {...}` with no `else`) that explains *why* a `scope: "C"` script action fails silently, one level below this file's incident writeup.

> **See also:** `references/gateway/notes/gotchas.md` ("Python actions need `scope: "G"`") — independent confirmation of the same `ActionRegistry` dead-button trap from a live client-bundle grep.

Two different, non-interchangeable mechanisms both get called "events" or
"actions" in conversation. Confusing them broke the live gateway twice this
session. This doc is the disambiguation.

## Mechanism 1: component event scripts (`events.<domain>.<eventName>`)

Nearly every component exposes **Component Events** (Designer: right-click →
Scripting → Events) — `onActionPerformed`, `onStartup`, `onClick`,
`onMouseEnter`, etc. The official 8.3 docs (`references/ignition-8-3/
perspective-components.md` [M]) document the Designer-generated script as a
bare Python stub:

```python
def onActionPerformed(self, event):
	system.tag.writeBlocking(["[default]Path/To/Tag"], [1])
```

which is stored in `view.json` under `events.<domain>.<eventName>`. **Designer
always writes the `{"config": {"script": "..."}, "permissions": {...},
"scope": "G", "type": "script"}` envelope there (live: 526 of 526 event
entries; a bare `{"script": "..."}` never occurs and throws the NPE below)** —
copy a real, currently-loading example off the live gateway rather than
hand-writing one. What's fixed either way: never put an
`ActionConfig`-style `actions` array under `events.<domain>.<eventName>` (or
vice versa) — that's mechanism 2's shape leaking into mechanism 1's slot, the
class of mistake this session hit.

## Mechanism 2: ActionConfig `actions` props (specific components only)

A **separate, smaller set of components** register `type`/`scope`-keyed
action entries through their own `actions`-shaped prop, not through the
generic `events` tree. Verified via `deep/perspective-schema-truth.md` §8
("Client action scopes"):

```js
if ("C" === scope) { /* client-side action registry lookup */ }
else if ("G" === scope) { /* gateway round-trip required */ }
```

`{"type": "script", "scope": "C"}` is invalid — there is no client-side
Python, so a script action **must** use `scope: "G"`; a `"C"`-scoped script
action registers nothing and fails silently, no error at all.

This mechanism is what backs the **named events listed against specific
components** in `16-PERSPECTIVE-SCHEMA-TRUTH.md`'s component inventory —
e.g. `ia.container.coord`'s `onPipeClicked`, `ia.container.split`'s
`onMinBoundReached`/`onMaxBoundReached`. It is not a generic mechanism every
component gets; check that component's own by-id schema
(`schema/perspective/by-id/<type>.json`) for an `actions`-shaped prop before
assuming it applies. **Grepped the bundled `schema/perspective/by-id/`:
the only `"actions"` key present anywhere is `ia.input.form.json`'s
`props.actions` (form submit/reset button layout — `justify`/columns, not
`type`/`scope`), so no component in the bundled schema set has a verified,
literal `type`/`scope` ActionConfig example** — treat any such shape as
unverified until pulled from a live Designer export, same rule as mechanism
1's `onActionPerformed`.

## Worked examples: this session's two live NPEs

Both incidents used mechanism 1's key path (`events.component.onActionPerformed`)
with a bare `{"script": "..."}` value (the bare stub in the official docs is
the Designer script editor's view, not the stored envelope) and the gateway threw:

```
NullPointerException: ActionConfig$ActionScope.name() ... "actionConfig.scope" is null
```
in `Perspective.Routes`, on **every** project-diff request (breaking
Designer/gateway project loads for every connected client, not just the
authored view).

1. **`views/trace`'s `searchBtn`** (`fix-trace-view`) — hit and reverted
   twice; see the historical `resources/trace_notes.md` on that branch.
2. **`common/sidebarMenu`'s hamburger toggle** — same NPE, third time it was hit.

**Both fixes removed the `events` key entirely** rather than finding a
working shape at the time. That gap is now closed, and corrected again on
2026-09-23 against a second, larger live sample. A real Designer-saved
button's `view.json` export (this session) confirmed the stored `script`
value under `config.script` is **body-only** — no `def onActionPerformed(self,
event):` line and no leading `def` at all. That part holds.

**Correction (2026-09-23):** the original write-up of this section claimed
the *only* documented shape at `events.<domain>.<eventName>` was a bare
`{"script": "..."}` and that `scope`/`type` keys never belong there — that
claim was drawn from one unconfigured/default button stub and was too
narrow. A live, currently-loaded, zero-NPE button pulled straight off this
gateway (`scadaTemplate1x/.../Templates/Common/button-command/view.json`,
re-confirmed 2026-09-23) has this full shape at
`events.component.onActionPerformed`:

```json
{
  "config": {"script": "\tsystem.tag.writeBlocking([self.view.custom.tagPath],[self.view.params.command])\n\tself.props.value = 0"},
  "permissions": {"securityLevels": [], "type": "AnyOf"},
  "scope": "G",
  "type": "script"
}
```

This exact shape (`config` + `permissions` + `scope: "G"` + `type: "script"`,
all siblings under the event name) was used twice more the same day on the
a second live project's button and loaded clean both times, no
NPE. So `scope`/`type` **do** belong at this level on a configured action —
the earlier blanket "never" was wrong. What still holds: never *guess* this
envelope from memory — pull a real, currently-loading example off the live
gateway (`get_project_resource` / direct file read) before hand-authoring
one, because the exact field set is something Designer itself writes, not
something to infer from one prior example.

## Rules

1. **Never hand-guess this envelope from memory or a single prior example.**
   Before writing `events.<domain>.<eventName>`, pull a real, currently-
   loading button/action from the live gateway (or a fresh Designer export)
   and copy its exact shape — always the
   `{"config", "permissions", "scope", "type"}` envelope; a bare
   `{"script": "..."}` has never been seen live.
2. Never write a bare `{"script": "..."}` where a component's own schema
   defines an `actions`-shaped prop (mechanism 2) — check the by-id schema
   first.
3. A `type: "script"` action **must** carry `scope: "G"` when `scope` is
   present — `scope: "C"` on a script action fails silently (no error, dead
   button).
4. `view_lint.py` flags any `events.<domain>.<eventName>` value containing
   `actions` keys instead of a bare `script` string or the full
   `config`/`permissions`/`scope`/`type` envelope — treat a lint failure as
   a signal to re-pull a live example, not as proof the fuller envelope is
   wrong. It cannot catch the inverse (mechanism-1 shapes used where
   mechanism 2 is required), since that depends on the specific component's
   schema, not a generic pattern.
