---
name: ignition
description: Ignition SCADA / Inductive Automation platform expertise - Perspective components, tags/UDTs, gateway scripting (system.*), alarms, named queries, OPC-UA, gateway administration. Use this skill whenever the user mentions Ignition, Inductive Automation, Perspective, Vision, a Gateway in a SCADA/industrial-automation sense, tag providers, UDTs, alarm pipelines, named queries, or gateway scripting - even if they don't say "Ignition" explicitly but the task is clearly SCADA/industrial-HMI-shaped (tags, views, historian, gateway). Skip it if a different SCADA/HMI/PLC platform is named instead (FactoryTalk, WinCC, Wonderware/AVEVA System Platform, CODESYS) and Ignition isn't mentioned.
---

# Ignition

You have two resources for Ignition work: a local knowledge base (what the platform generally does) and a live MCP server (what *this* deployment is actually doing right now). Neither one is trustworthy alone - the KB documents a snapshot of the platform, and a live Gateway can't tell you *why* something is designed the way it is. Use both, and don't let either one go unchallenged when it disagrees with the other.

## Knowledge base

Path: `C:\Users\THINKPAD T14 GEN2\Documents\Projects\ClaudeMem\Ignition-knowledgebase`

**Building or editing a Perspective view, component, layout, binding or event? Invoke the `ignition-perspective` skill.** It is the schema-first discipline for that work, and it carries the verified traps. Its two highest-value KB targets are `16-PERSPECTIVE-SCHEMA-TRUTH.md` (shipped schemas, the style precedence chain, the full 81-component inventory) and `04-RESOURCE-MODEL.md` (every project resource type and its on-disk files). Both were extracted directly from this install.

Start at `KNOWLEDGE-GRAPH.md` - it has learning paths, a prerequisite graph, a glossary, and use-case chains that route you to the right doc without guessing. For component-specific questions, go straight to `Components/<Category>/<ComponentName>.md` (e.g. `Components/Display/Table.md`, `Components/Input/Dropdown.md`) - the folder structure mirrors the Perspective palette categories (Containers, Display, Input, Navigation, Misc, and Display's Charts/Industrial/Mapping subfolders).

**Confidence levels matter here, and they differ by topic:**

- **Component property docs are high-confidence but incomplete.** A 2026-08-14 recount against the install found **82 shipped components** (81 across seven `perspective-common` library files, plus `ia.reporting.report-viewer` shipped separately by the Reporting module) and **56 component docs**, so symbols, shapes and Nav Links have no page at all - the gap list is in `16-PERSPECTIVE-SCHEMA-TRUTH.md`. The docs that do exist were cross-checked against the actual runtime schemas extracted from the Ignition 8.3.7 install's jar-cache (`data\jar-cache\com.inductiveautomation.perspective\*.jar` - plain JSON, unzip-able, no decompiler needed). Before that pass, roughly a third of these docs had invented property names that looked plausible but didn't exist in the real schema. Trust the current docs, but if a property name feels off or the user reports a binding error, it's worth re-extracting and checking rather than assuming the doc is still right - Ignition versions do change schemas.
- **Scripting (`system.*`) docs are medium-confidence, except where a `PyWrapper` class exists.** `31-SYSTEM-FUNCTIONS.md` and `35-COMPLETE-SYSTEM-FUNCTIONS.md` are mostly spot-checked against Inductive Automation's public docs, not schema-verified - most of the scripting API is compiled Java with no shipped stubs. But a 2026-08-14 pass on the Reporting module found `ReportScriptingFunctionsPyWrapper` in `reporting-common-7.3.7.jar`: modules that expose Python-callable functions ship a `*PyWrapper` class whose bytecode literally contains the real parameter names as string constants (`javap -c` shows them as `// String path`, `// String project`, etc. next to each method). This is how `71-REPORTING-MODULE.md`'s `system.report.*` signatures were corrected - the KB had `executeReport` missing its required `project` argument. Worth checking for a `*PyWrapper` class before assuming a `system.*` namespace is unverifiable. If a `system.*` signature looks suspicious or the user hits an error calling it, check `docs.inductiveautomation.com` or grep for its `PyWrapper` before assuming the KB is right.

## Live gateway (ignition-mcp)

For anything about *this specific* deployment's current state, use the live tools - never guess a live fact from the KB, since the KB describes the platform generically, not any one Gateway's configuration or runtime data.

- **Tags/UDTs:** `mcp__ignition-mcp__browse_tags`, `get_tag_config`, `read_tags`, `write_tag`, `edit_tags`, `create_tags`, `delete_tags`, `get_tag_history`, `get_tag_provider`, `list_tag_providers`, `get_udt_definition`, `list_udt_types`
- **Projects:** `get_project`, `list_projects`, `get_project_resource`, `list_project_resources`, `create_project`, `copy_project`, `rename_project`, `delete_project`, `export_project`, `import_project`, `set_project_resource`, `delete_project_resource`
- **Alarms:** `get_active_alarms`, `get_alarm_history`, `acknowledge_alarms`
- **Gateway health/admin:** `get_gateway_info`, `get_gateway_logs`, `get_system_metrics`, `get_module_health`, `get_database_connections`, `get_opc_connections`, `list_designers`
- **Scripting:** `run_gateway_script` - runs Python against the live Gateway scope; use this to verify a `system.*` call actually behaves as documented, not just to execute one-off tasks
- **Tag providers:** `create_tag_provider`, `delete_tag_provider`

Mutation tools (`write_tag`, `edit_tags`, `delete_tags`, `delete_project`, `delete_tag_provider`, `acknowledge_alarms`, etc.) act on a real running system - confirm with the user before calling them unless they've clearly asked for the change.

## Drift handling

If a live-gateway fact contradicts the KB - a property that doesn't exist, a function signature that's different, a default value that's changed - don't silently pick a side. Surface the discrepancy to the user ("the KB says X, but the live Gateway/schema shows Y") and ask before editing the KB doc. This isn't optional caution: this KB previously had a meta-doc that confidently claimed "100% verified, zero fabricated properties" while about 25 of the underlying docs were actually wrong. Confident-sounding documentation is not the same as correct documentation - treat a KB claim of certainty the same way you'd treat any other claim: verifiable, not automatically true.

When you do confirm a real discrepancy and the user wants it fixed, edit the specific component/function doc directly (keep the hand-written examples and gotchas, fix the property table), and note what changed - don't rewrite the whole file.

## Version awareness

The KB's component schemas were verified against Ignition 8.3.7 (per the install's `lib\install-info.txt`). If `get_gateway_info` (or the user) reports a different version, the schemas may have shifted - flag this rather than assuming the KB still applies. `Components/README.md` documents the re-extraction procedure (unzip the relevant `*.components.json` files from the new install's `data\jar-cache\com.inductiveautomation.perspective\` folder - still no decompiler needed) if a re-verification pass is warranted.
