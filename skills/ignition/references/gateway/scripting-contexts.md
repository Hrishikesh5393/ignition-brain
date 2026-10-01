# Scripting contexts: gateway vs Perspective vs plain Python 3 assumptions

> **See also:** `references/ignition-8-3/scripting-model-and-designer.md` [M] — the general gateway/Vision/Perspective scope table and execution-context list this file's three-context map builds on, from the current official manual.

New file, not an extension of `standards/jython.md`: that file documents the
**Jython 2.7 language** (what syntax/stdlib exists at all). This file is the
**runtime-context** map — given valid Jython, which `system.*` calls and script
"slots" are even reachable from where. The two overlap only at jython.md's own
"Scope — what `system.*` is where" table, which this file supersedes with more
detail and worked failure modes; jython.md keeps a pointer here instead of
duplicating it.

## The three contexts, basic → advanced

### 1. Gateway scripting (simplest — no session, no page)

Timer scripts, tag-change scripts, message handlers, `run_gateway_script`,
WebDev endpoints, gateway startup/shutdown scripts. Full `system.tag`,
`system.db`, `system.util`, `system.alarm`, `system.opc`, `system.perspective.send*`
(broadcast only — no session to navigate). **No `system.perspective.navigate`,
no `openPopup`, no `system.gui`, no `system.nav`** — there is no session or
window to act on. If a gateway script needs to reach a live session, it must
`system.perspective.sendMessage` and let a session-scope handler act.

### 2. Perspective session/view scripting (a session exists)

Component event scripts (Button's `onActionPerformed`, etc. — see
`perspective-events.md`), `runScript()` property-binding transforms, session
event scripts (`onStartup`/`onShutdown` at session scope). Adds
`system.perspective.navigate`, `openPopup`, dock control, `getSessionInfo` —
all bound to *this* session. Still **no `system.gui`, no `system.nav`**
(those are Vision-only) and still runs under Jython 2.7, not Python 3 — a
`runScript()` transform is not a JavaScript-like sandboxed mini-language, it
is a real Jython function body with the same 2.7 constraints as a gateway
script.

### 3. Vision client scripting (separate module)

Adds `system.gui`, `system.nav`, `system.vision`. Not reachable from
Perspective, so irrelevant to Perspective work —
listed here only so an agent doesn't reach for `system.nav.*` inside a
Perspective binding by habit from an unrelated Vision example.

### Designer scripting (superset)

Most of gateway + client scope, plus resource-manipulation APIs
(`ProjectManager`, resource browsing) unavailable at runtime in any of the
above. Only reachable through `run_gateway_script`/interactive Designer
sessions in this toolkit, not through a deployed view/session script.

## Concrete break: plain-Python-3 assumptions under Jython 2.7

`open(path, "w", encoding="utf-8")` — a normal Python 3 call — **fails under
Jython 2.7**: Jython 2.7's `open()` is Python 2's two/three-positional-arg
builtin (`open(name[, mode[, buffering]])`), which has no `encoding` keyword
at all. Calling it with `encoding=` raises `TypeError: open() takes no
keyword arguments` (hit and fixed this session, gateway-side file write for
a project resource). Use `codecs.open(path, "w", encoding="utf-8")` (from
the confirmed-present `codecs` stdlib module, `standards/jython.md`) when an
explicit encoding matters, or plain `open(path, "w")` + `.write(unicode_str)`
relying on the platform default when it doesn't — never the Python-3-only
`encoding=` kwarg on the builtin.

This is one instance of a general rule: **any code copied from a Python 3
reference (tutorials, LLM training data's dominant Python dialect,
StackOverflow answers) needs a Jython-2.7 compatibility pass before it goes
into a gateway or Perspective script.** `standards/jython.md`'s "Language —
hard limits" table is the checklist; this file's job is only to flag that
the check applies in **every** one of the three runtime contexts above, not
just gateway scripts — a `runScript()` transform breaks on `f'{x}'` exactly
as hard as a timer script does.

## Rules

1. Identify which of the 3 contexts a script slot is before writing it —
   `system.gui`/`system.nav` in a Perspective binding, or
   `system.perspective.navigate` in a gateway timer script, both fail at
   runtime with no compile-time warning.
2. Every context is Jython 2.7, never Python 3 — re-check
   `standards/jython.md`'s hard-limits table against any snippet pulled from
   an external Python 3 source before pasting it into gateway, session, or
   view scripting.
3. `open()` never takes `encoding=` here — use `codecs.open()` when encoding
   must be explicit.
4. A gateway script cannot act on a live session directly; route through
   `system.perspective.sendMessage` to a session-scope handler.
