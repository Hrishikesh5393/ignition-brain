---
name: ignition-platform
description: >-
  Use for Ignition platform topics: OPC UA/drivers and device connections, gateway configuration, redundancy/HA and store-and-forward, editions/licensing, module catalog, Vision client windows/components, custom module (SDK) development, and 8.1→8.3 upgrade/migration.
---

# Ignition platform, connectivity, Vision, module SDK

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

Via `references/TOC.md`, read sections only:
- OPC UA, drivers, addressing, Event Streams, JDBC: `references/ignition-8-3/connectivity-and-modules.md` (18.9k).
- Event Streams (create/deploy/verify a stream resource, traps): `references/gateway/event-streams.md` (4k); stage/property reference in the connectivity file's Event Streams section.
- Gateway config, HA, store-and-forward, deployment: `references/ignition-8-3/gateway-and-deployment.md` (19.9k), `platform-overview.md` (14.8k, editions/architecture).
- Vision: `references/ignition-8-3/vision-module.md` (26.7k), `vision-components.md` (51k — one component's section only).
- Custom modules: `references/gateway/module-sdk.md` (1.8k).
- Upgrade 8.1→8.3: `references/ignition-8-3/8.1-to-8.3-traps.md` (4.4k, whole) + `whats-new-8.3.md` sections (upgrade path).
- Canonical manual page for anything else: `references/ignition-8-3/doc-index.md` (grep the path, fetch `<path>.md` from docs.inductiveautomation.com/docs/8.3/).
