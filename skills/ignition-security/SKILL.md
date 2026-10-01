---
name: ignition-security
description: >-
  Use for Ignition security: users/roles, security levels and zones, identity providers (IdP), API keys, Perspective/Vision permissions, secrets, hardening and IEC 62443 mapping.
---

# Ignition security

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

- Roles/levels/zones/IdP/API keys mechanics and rules: `references/standards/security-roles.md` (2.2k).
- Standard mapping/hardening: `references/standards/iec-62443.md` (2.2k).
- Manual detail: `references/ignition-8-3/security-and-databases.md` (15.6k) — TOC + section (IdPs, security levels, zones, secrets, API keys).
- Rules that always apply: never widen an API key's scope or a role's grants to get past a 403 — escalate to your supervisor; keep secrets in the gateway credential store.
- Perspective view permissions/inactivity: `references/ignition-8-3/perspective-module.md` (TOC, security section) / `ignition-perspective`. Writing config live → `ignition-deploy`.
