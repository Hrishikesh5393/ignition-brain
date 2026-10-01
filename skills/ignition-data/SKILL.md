---
name: ignition-data
description: >-
  Use for Ignition data plumbing: named queries (resource format, parameters, caching), SQL/database connections, the Reporting module (report resources, shapes, data sources), Transaction Groups, SQLBridge, SFC, and tag-history queries feeding reports.
---

# Ignition named queries, databases, reporting

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

- Named queries: `references/gateway/named-queries.md` (4.3k), schema `schema/named-query/` (+ `example/`); decompiled context: `references/gateway/deep/udt-and-named-query-internals.md` Part 2.
- Reporting resources: `references/gateway/deep/reporting-module.md` (2.7k), `deep/reporting-shape-model.md` (3.5k, only when authoring shapes/XML).
- Manual detail: `references/ignition-8-3/reporting-sqlbridge-sfc-eam.md` (11.5k) — TOC + sections (Reporting, Transaction Groups, SFC, EAM); DB connections: `references/ignition-8-3/security-and-databases.md` (TOC, DB section).
- Report viewer component: `schema/perspective/by-id/ia.reporting.report-viewer.json` (`ignition-perspective`).
- Writing queries/reports live → also load `ignition-deploy`.
