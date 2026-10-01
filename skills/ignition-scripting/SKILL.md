---
name: ignition-scripting
description: >-
  Use for Ignition scripting: Jython 2.7 gateway/Designer/Perspective/Vision scripts, the system.* API (signatures, scope, which calls work where), timer/tag-change/message/WebDev scripts, Ignition expression-language and bindings syntax, cron, and 8.1→8.3 deprecated-function replacements.
---

# Ignition scripting & expressions

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

- Language limits: `references/standards/jython.md` (2.3k). Which `system.*` reaches from which scope: `references/gateway/scripting-contexts.md` (1.2k). API guide: `references/gateway/system-api.md` (2.9k).
- Exact signature of one function: query `schema/system-api.json` (`python3 -c` / `jq '.["system.tag.readBlocking"]'`), never read it whole.
- Manual API detail: `references/ignition-8-3/scripting-core.md`, `scripting-ui.md`, `scripting-platform.md`, `scripting-connectivity.md`, `scripting-model-and-designer.md` — TOC + section reads.
- Deprecated/renamed function or 8.1-era code: `references/ignition-8-3/8.1-to-8.3-traps.md` → TOC section "Deprecated scripting functions" (1.8k) and "Behaviour changes" (0.8k).
- Expressions/cron: `references/ignition-8-3/expression-language.md` (19k) — TOC + the function/section you need. No ternary; use `if()`.
- Event scripts in Perspective: `ignition-perspective` (action shapes). Writing scripts live → `ignition-deploy` (timer scripts need `restartScripting()` when new).
