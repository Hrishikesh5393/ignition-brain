# Reference index — the full map (fallback)

Normal entry is the selector in `SKILL.md` → a focused `ignition-*` skill that names its files.
Use this index when no skill fits or to find a file directly. Section-addressed reads for big
files: `TOC.md`. Verification baseline: `VERIFIED.md`.

Three tiers, cited by prefix: **[S]** `references/standards/` (universal, version-independent
industry standards — Jython, ISA-95, ISA-101, IEC), **[G]** `references/gateway/` (mechanics
verified by decompile, live round-trip or incident, never guessed: on-disk resource formats,
action shapes, write loop, MCP tool behaviour — true of any 8.3 gateway), **[M]**
`references/ignition-8-3/` (official 8.3 manual, distilled — snapshot 2026-09-22; includes
`doc-index.md` mapping every canonical page, `whats-new-8.3.md` the feature narrative, and
`8.1-to-8.3-traps.md` the removed/deprecated/changed tables). [M] = "how does Ignition 8.3
work"; [G] = ground truth the public docs don't cover. If [M] documents something and [G] is
silent, trust [M]. `gateway/deep/` = decompile-verified internals; `gateway/notes/` = short
lessons learned.

**Any live-gateway write:** `workflow.md` → `gateway/mcp-tool-map.md` →
`gateway/resource-formats.md` (`gateway/environment-setup.md` only when `ignition-mcp` or the
WebDev endpoints are missing). **8.1-era doubts:** `ignition-8-3/8.1-to-8.3-traps.md`.

| Bucket | Files |
|---|---|
| **Tags, UDTs, historian** | `tag-naming.md`, `udt-design.md`, `historian.md`, `isa95.md` [S]; `references/ignition-8-3/tags-alarms-historian.md` [M]; `references/gateway/deep/udt-and-named-query-internals.md` [G] (decompiled UDT/Named Query internals) |
| **Design decisions (which mechanism)** | `playbook.md` [S] (quick-decision flow + per-topic tables) |
| **Perspective UI** | `component-schemas.md`, `component-composition.md`, `perspective-events.md` [G]; `isa101-hmi.md` [S]; `references/ignition-8-3/perspective-module.md` (bindings/transforms/security), `perspective-components.md` (72 components, full property trees) [M]; `references/gateway/deep/perspective-schema-truth.md` [G] (decompiled style precedence, client action-scope dispatch, full 82-component install inventory) |
| **Vision (legacy client)** | `references/ignition-8-3/vision-module.md`, `vision-components.md` (77 components) [M] |
| **Alarming** | `alarms.md` [S]; `alarm-pipelines.md` [G] (on-disk format, every block type, backed by `schema/alarm-pipeline/`); `references/ignition-8-3/tags-alarms-historian.md` [M]; `references/gateway/deep/alarm-pipeline-schema-truth.md` [G] (decompiled `PipelineDescriptor`/block-factory confirmation) |
| **Security** | `security-roles.md`, `iec-62443.md` [S]; `references/ignition-8-3/security-and-databases.md` [M] (IdPs, security levels/rules/grants, zones, secrets, API keys, DB connections, Named Queries) |
| **Reporting module** | `references/ignition-8-3/reporting-sqlbridge-sfc-eam.md` [M] (Reporting, Transaction Groups, SFC, SECS/GEM, EAM); `references/gateway/deep/reporting-module.md`, `reporting-shape-model.md` [G] (ReportMill shape/XML architecture, bytecode-verified — no Report resource exists in a fresh project, confirmed against the real Java classes) |
| **OPC-UA / device comms** | `references/ignition-8-3/connectivity-and-modules.md` [M] (module catalog, OPC UA client/server, every driver's addressing syntax, Event Streams, Web Dev, JDBC) |
| **Scripting & system.\* API** | `jython.md` [S]; `system-api.md`, `scripting-contexts.md` [G] (which `system.*` calls reach from gateway/session/view/Vision scope, the Python-3-assumption trap under Jython 2.7 — `schema/system-api.json` is the reflection/decompile-verified companion); `references/ignition-8-3/scripting-core.md`, `scripting-ui.md`, `scripting-platform.md`, `scripting-connectivity.md` (359 entries total, signatures + scope) [M] |
| **HA/clustering, mobile, SFC** | `references/ignition-8-3/gateway-and-deployment.md` [M] (redundancy, store-and-forward) |
| **Module SDK (custom module dev)** | `module-sdk.md` [G] — Kotlin/Gradle project-per-scope layout, the `io.ia.sdk.modl` manifest/build/sign loop, recurring stdlib-skew and stale-jar gotchas, toolchain baseline. Generalized from one project's build; re-verify plugin/version specifics against the target repo. |
| **Expression language** | `references/ignition-8-3/expression-language.md` [M] — full syntax, 130 functions by category, binding-scope differences, cron syntax |
| **Gateway config, deployment, editions** | `references/ignition-8-3/gateway-and-deployment.md`, `platform-overview.md` [M] |
| **Lessons learned / gotchas** | `references/gateway/notes/*` [G] — short dated write-ups (tag event script body-only, component icons, flex props, install-truth methodology, …); check here before re-deriving something the hard way |
| **Finding the exact canonical page** | `references/ignition-8-3/doc-index.md` [M] — all 1,574 manual page paths; fetch `<path>.md` off `docs.inductiveautomation.com/docs/8.3/` for clean Markdown, cheaper than HTML |

For a task spanning buckets (e.g. "add a Perspective screen with an alarm-driven
color binding"), read the always-first list plus each relevant bucket's [G]/[S]
files, and [M] for anything general-platform the task touches.

