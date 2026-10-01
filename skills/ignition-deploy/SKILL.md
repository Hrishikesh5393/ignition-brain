---
name: ignition-deploy
description: >-
  Use for ANY write to a live Ignition gateway or any ignition-mcp tool call — the write → fsync → requestScan → runtime-verify loop, the 402 stop rule, which MCP tool to use per step and which are unreliable, on-disk resource layout/formats, and WebDev endpoint setup. Load alongside the domain skill whenever you change project resources, tags or gateway config.
---

# Ignition deploy — safe write loop

Base dir: `~/.claude/skills/ignition/` (paths below are relative to it). Big files: read `references/toc/<name>.md` first, then `Read` the section range. Load core `ignition` first if not already loaded.

The loop: author on disk → push via `ignition-mcp` → `flush+fsync` → `requestScan()` → verify at runtime.
Stop rules: HTTP 402 = trial timer lapsed → report and stop; same obstacle twice → report blocked.

Read, in order:
1. `references/workflow.md` (1.4k) — 5-step loop, stop rules, isolation.
2. `references/gateway/mcp-tool-map.md` (3.2k) — which tool per step, per-tool reliability, fallbacks (`run_gateway_script` is the golden path).
3. `references/gateway/resource-formats.md` (6.7k; TOC: `references/toc/gateway__resource-formats.md`) — read only the section for the resource type you write (view, page-config, timer, tag script, named query, alarm pipeline, …) plus the fsync / large-payload staging section.
4. `references/gateway/notes/gotchas.md` (2.4k) — traps hit before; `notes/verification.md` only when re-deriving internals; `notes/feedback_ignition_check_gateway_logs.md` when a write silently fails (read the gateway logs).
5. `references/gateway/environment-setup.md` (2.1k) — ONLY if `ignition-mcp` tools or the WebDev endpoints are missing/fresh machine (deploy script: `scripts/deploy_webdev_endpoints.py`).
Perspective view.json touched → also lint: `python3 scripts/view_lint.py <view.json>` (see `ignition-perspective`).
