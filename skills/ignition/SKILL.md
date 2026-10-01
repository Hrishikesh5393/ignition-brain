---
name: ignition
description: >-
  Entry point and selector for any Ignition (Inductive Automation) 8.3 SCADA/HMI work —
  Perspective/Vision views, Jython gateway/Designer scripts, tags/UDTs, alarms and
  pipelines, historian, named queries, reporting, OPC/gateway config, security, or
  driving a live gateway through the ignition-mcp tools. Load this first: its Helm selector carries
  the guardrails and routes you to the one or two focused ignition-* skills (and the
  exact files inside them) the task needs, so you don't read the whole reference set.
---

# Ignition (#AIDriven development) — core + Helm (selector)

Global Ignition mechanics only. Concrete choices of a deployment (naming scheme, palette,
provider names, gateway URL) come from your project layer and brief, not from here.

**Base dir** of this skill (all `references/…`, `schema/…`, `scripts/…` paths below and in the
`ignition-*` skills are relative to it): `~/.claude/skills/ignition/`.

## Guardrails (always)

- The gateway's project files are never edited by hand. Change them by running scripts
  through `ignition-mcp` (`run_gateway_script`, `set_project_resource`, …), then
  `f.flush(); os.fsync(f.fileno())` → `requestScan()` → verify at runtime (`getProjectCache()`,
  a tag read) — never trust an HTTP 200 alone. Details: skill `ignition-deploy`.
- **HTTP 402** = gateway trial timer lapsed: report to your supervisor and stop; never reset it.
- Never `browse_tags` a whole large provider — query narrow subtrees.
- Never hand-guess a JSON envelope, event schema or resource shape from memory: copy a
  currently-loading live example (or the bundled schema) and lint it.
- Verify worktree isolation before writing, if you work in a task worktree.
- Jython is 2.7 (not Python 3); Ignition expressions have no `? :` — only `if(c, a, b)`.

## Helm (selector) — pick skills by task keyword, then follow that skill only

| Task mentions | Load skill |
|---|---|
| view, component, binding, embed, Perspective event/action, theme, page-config, dock, style, ISA-101 HMI | `ignition-perspective` |
| tag, UDT, tag provider, tag naming, tag path, ISA-95, historian config, IEC 61131/61850 | `ignition-tags` |
| alarm, alarm pipeline, notification, roster, ack, ISA-18.2 | `ignition-alarms` |
| script, Jython, `system.*`, timer/tag-change/message handler, WebDev endpoint, expression, cron | `ignition-scripting` |
| named query, SQL/database, Reporting module, Transaction Groups, SQLBridge, tag history query | `ignition-data` |
| OPC UA, driver, device, Event Streams, gateway config, HA/redundancy, editions/licensing, Vision client, custom module (SDK), 8.1→8.3 upgrade | `ignition-platform` |
| role, IdP, security level, zone, API key, hardening, IEC 62443 | `ignition-security` |
| decode, understand, reverse-engineer or audit an existing project (live, export zip, .gwbk) | `ignition-scout` |
| replicate, rebuild, clone, copy or migrate a project into another project/gateway | `ignition-scout` then `ignition-forge` |
| which / when to use / should I / best way / choose / binding vs script vs expression / template vs embed / param vs session prop | `ignition-playbook` |
| **any** live-gateway write or `ignition-mcp` call (in addition to the above) | `ignition-deploy` |

Multiple keywords → load each matching skill (usually 1–2; `ignition-deploy` only if you write
live). Each skill names the exact files and section ranges; read only those — never a whole
directory. Big files have a section index: `references/TOC.md` → `references/toc/<file>.md` →
`Read <file> offset=… limit=…`. Fat component schemas have a digest:
`schema/perspective/digest/<component>.md`.

Fallbacks: full file map `references/INDEX.md`; verification baseline `references/VERIFIED.md`;
8.1-era doubts `references/ignition-8-3/8.1-to-8.3-traps.md` (read the section you need via TOC).
Lint any touched Perspective view with `python3 scripts/view_lint.py <view.json>`; check the
skill itself stays global with `python3 scripts/check_global.py`.
