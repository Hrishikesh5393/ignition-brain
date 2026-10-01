---
name: ignition-perspective
description: >-
  Use for Ignition Perspective work: view.json, components and their props, bindings, embedded views/templates, event actions, page-config/docks, styles/themes, ISA-101 HMI design, and linting views against the bundled component schemas. Not for Vision (see ignition-platform).
---

# Ignition Perspective

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

Read only what the task needs (sizes in tokens):
- Any view: `references/gateway/component-schemas.md` (3.8k) — how schema → valid `view.json`, per-component gotchas.
- Embeds / templates / repeaters / shared docks: `references/gateway/component-composition.md` (0.8k).
- Any click/`actions`/event handler: `references/gateway/perspective-events.md` (1.9k) — action shapes are `{config, scope, type}`; a bare `{"script":…}` crashes project loads. Never guess; copy a live example.
- Look/feel or a new HMI screen: `references/standards/isa101-hmi.md` (1.8k); flex layout props: `references/gateway/notes/feedback_perspective_flex_props.md` (1.2k); icons: `notes/feedback_ignition_component_icons.md`.
- Component props: fat components → `schema/perspective/digest/<component>.md` first (table, form, xy/timeseries/power charts, maps, alarm tables); else `schema/perspective/by-id/<id>.json` (index: `schema/perspective/*.components.json`). Never read the whole `by-id/` dir.
- Bindings/transforms/security/session props (official manual): `references/ignition-8-3/perspective-module.md` and component reference `references/ignition-8-3/perspective-components.md` / `component-scripting-api.md` — via `references/TOC.md`, section reads only.
- Style precedence, client action-scope dispatch, full component inventory (only when debugging rendering): `references/gateway/deep/perspective-schema-truth.md` (5.5k).
- Writing to the gateway → also load `ignition-deploy`. Lint before done: `python3 scripts/view_lint.py <view.json>` (unknown types, unwired required props, wrong-level keys).
