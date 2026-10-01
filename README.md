# ignition-brain

Personal Ignition (Inductive Automation) knowledge base, Claude Code skills,
and tooling — built up across sessions on one gateway, portable to any
machine. No client project data in here (tags, views, gateway backups) —
knowledge and tooling only.

## Layout

- `knowledgebase/` — the full platform knowledge base (`00-INDEX.md` to start,
  `Components/<Category>/<Name>.md` for per-component docs). Verified against
  a real Ignition 8.3.7 install, not just public docs — see
  `knowledgebase/reference_ignition_install_truth.md`-equivalent notes in
  `memory/` for how.
- `skills/` — Claude Code skills, pure platform mechanics only (global
  Ignition 8.3 behavior, no client/project specifics — those live in
  `knowledgebase/`, `memory/`, or the consuming project's own context, never
  baked into a skill). `ignition/` is the entry point and Helm selector,
  routing to the focused skill(s) a task needs:
  `ignition-alarms`, `ignition-data`, `ignition-deploy`, `ignition-forge`,
  `ignition-perspective`, `ignition-platform`, `ignition-playbook`,
  `ignition-scout`, `ignition-scripting`, `ignition-security`,
  `ignition-tags`. Install with `sh skills/ignition/install.sh` (symlinks
  into `~/.claude/skills`).
  `ignition_outdated/` and `ignition-perspective_outdated/` are the prior
  2-skill generation, kept for reference only — superseded by the above,
  do not install.
- `memory/` — standalone lessons-learned notes (tag param substitution,
  event-script body-only convention, component icon registration, flex
  layout props-vs-CSS, etc). Each is self-contained; frontmatter carries a
  `description` and any `[[cross-links]]` to other notes in this set.
- `tools/ignition_agent.py` — a small Gemini/Ollama-driven agent that reuses
  the ignition-mcp server as tools, independent of Claude Code.
- `mcp/` — reference and config templates for the live-gateway MCP server
  (the server itself is a third-party project, not vendored here — see
  `mcp/README.md`).

## Setting this up on a new machine

1. Run `sh skills/ignition/install.sh` (symlinks `ignition` + all
   `ignition-*` skills into `~/.claude/skills/`; pass `--target DIR` for a
   different Agent Skills folder).
2. The skills carry no hardcoded paths — they're global Ignition 8.3
   knowledge only. Project-specific facts (this gateway's KB, naming
   conventions, verified schema notes) live in `knowledgebase/` and
   `memory/` below, referenced from your project's own context, not from
   the skill.
3. Drop the `memory/*.md` files into your Claude Code memory directory and
   add index lines to `MEMORY.md` if you use the auto-memory system.
4. Follow `mcp/README.md` to clone and wire up the live ignition-mcp server.

## Provenance

Everything here was learned/built against a real Ignition Gateway (8.3.7,
trial license) via Claude Code + the ignition-mcp server, iterated over
several sessions. Confidence levels and verification method for each claim
are noted inline — this isn't a copy of Inductive Automation's docs, it's
what was independently confirmed against the shipped schemas, jars, and
client bundle.
