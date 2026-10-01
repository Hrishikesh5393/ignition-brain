---
name: ignition-tags
description: >-
  Use for Ignition tags: tag providers, tag paths and naming, UDT definitions/instances/parameters, tag configuration via system.tag.configure, ISA-95 equipment hierarchy, tag historian settings, and IEC 61131/61850 modelling.
---

# Ignition tags, UDTs, historian

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

- Naming/paths: `references/standards/tag-naming.md` (2.1k), `references/standards/isa95.md` (2.1k).
- UDTs: `references/standards/udt-design.md` (2.1k); decompiled UDT internals: `references/gateway/deep/udt-and-named-query-internals.md` Part 1 (5.3k; read Part 1 only).
- Historian settings/queries: `references/standards/historian.md` (1.8k).
- Modelling standards, only if relevant: `references/standards/iec-61131.md`, `iec-61850.md` (2.2–2.4k each).
- Manual detail (tag types, providers, tag events, history): `references/ignition-8-3/tags-alarms-historian.md` (23k) — TOC + section reads only.
- Tag-event script body-only + parameter substitution: `references/gateway/notes/feedback_ignition_tag_event_script_body_only.md`, `feedback_ignition_tag_param_substitution.md`.
- Nested tag trees: build a nested config tree and call `system.tag.configure(base, tree, "a")` via `run_gateway_script`; do not rely on flat per-tag `path` args. Writing live → also load `ignition-deploy`. Scripts → `ignition-scripting`.
