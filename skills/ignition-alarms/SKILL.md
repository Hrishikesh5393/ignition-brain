---
name: ignition-alarms
description: >-
  Use for Ignition alarming: alarm configuration on tags/UDTs, alarm priorities and states (ISA-18.2), alarm notification pipelines and their block types, rosters/profiles, ack/shelve, alarm journal and status queries.
---

# Ignition alarms

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

- Design/config standards: `references/standards/alarms.md` (2.0k).
- Pipeline on-disk format and every block type: `references/gateway/alarm-pipelines.md` (4.7k); schemas `schema/alarm-pipeline/pipeline.schema.json`, `blocks.schema.json` (query with python/jq, do not read whole).
- Decompiled confirmation (only if a pipeline fails to load): `references/gateway/deep/alarm-pipeline-schema-truth.md` (2.9k).
- Manual detail (alarm properties, journal, status): `references/ignition-8-3/tags-alarms-historian.md` — TOC + section reads.
- Alarm tables in Perspective: digests `schema/perspective/digest/ia.display.alarmstatustable.md`, `alarmjournaltable.md` (see `ignition-perspective`).
- Writing pipelines/tags live → also load `ignition-deploy`.
