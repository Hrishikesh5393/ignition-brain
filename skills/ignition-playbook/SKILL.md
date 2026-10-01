---
name: ignition-playbook
description: >-
  Use when choosing between Ignition mechanisms: which binding type, transform vs expression vs script, script scope (component event / message handler / gateway event / library), template/embedded view vs inline, view param vs URL param vs session prop, dock vs popup vs embed, named query vs tag history vs SQL, UDT vs folder, polling vs event-driven, style class vs inline. Also "should I", "best way", "when to use", "choose".
---

# Ignition Playbook — design decisions

Base dir: `~/.claude/skills/ignition/` (paths relative to it). Load core `ignition` first.
Plain markdown; usable by any agent or human.

1. Read the **quick-decision flow** at the top of `references/standards/playbook.md` (section 0).
2. Jump to the one table you need (§1 bindings, §2 transforms, §3 script scopes, §4 templates, §5 state, §6 docks/popups, §7 data sources, §8 UDT/folders, §9 polling, §10 styling). Each row: use when / avoid when / example / trap / source.
3. Every rule cites a reference; a rule marked **unverified** is judgement, not fact. Verify before relying on it.
4. Then implement with the domain skill (`ignition-perspective`, `ignition-scripting`, `ignition-tags`, `ignition-data`), and `ignition-deploy` for live writes.
5. Check a build dir: `python3 scripts/fat.py <dir>`; Playbook warnings (`playbook.*`) are advice, not failures.

To learn what an existing project already does before choosing, run `ignition-scout` and read its `patterns.md`.
