---
name: ignition-scout
description: >-
  Use to decode, understand, reverse-engineer or audit an EXISTING Ignition project (live gateway project, project export zip, or gateway backup .gwbk): how it is built, what it contains, which patterns it uses, captured well enough to replicate. Runs a deterministic script (no LLM) that writes map.json, inventory.md and patterns.md; the agent then writes a plain-language summary.md.
---

# Ignition Scout — project decoder

Base dir: `~/.claude/skills/ignition/` (paths relative to it). Load core `ignition` first.
Read-only: Scout never writes to the gateway. HTTP 402 (exit code 3) = trial lapsed: report and stop.

## 1. Run

Stdlib Python 3, no MCP, no LLM. Pick the input:

```
python3 scripts/scout.py --zip  project-export.zip --name <Project> -o scout-report/
python3 scripts/scout.py --gwbk backup.gwbk --project <Project>     -o scout-report/   # omit --project to list projects
IGNITION_URL=http://host:8088 IGNITION_API_KEY=<keyName>:<secret> \
python3 scripts/scout.py --live <Project> -o scout-report/          # read-only REST export; key needs admin scope
python3 scripts/scout.py --diff a/map.json b/map.json               # 0 = maps agree
```

`--live` GETs `/data/api/v1/projects/export/<name>` (plus `projects/list` for user source / tag provider / default DB), so all three inputs go through the same extractor and give the same map. Exit 2 = bad input.

## 2. Output files (`scout-report/`)

| File | For | Content |
|---|---|---|
| `map.json` | Forge, Playbook, scripts | project meta, resource list, pages/routes, docks, views (bindings, embeds, popups, navs, events, tags, queries, styles), embed tree + broken refs, bindings by type, scripts by scope (library, gateway events, inline), system.* API use, message handlers, named queries, tags referenced, alarm pipelines, other resources (event streams, reports), session/view/page params, theme, conventions, patterns |
| `inventory.md` | humans / agents | the same as tables + embed tree |
| `patterns.md` | Playbook | stable-id pattern list with counts and examples |
| `summary.md` | humans | YOU write it (below) |

## 3. Write `summary.md`

Read `patterns.md`, then `inventory.md` (top to bottom; `map.json` only to answer a specific question — grep it, do not load whole). Write ≤ 1 page, plain language, no jargon dumps:

1. **What it is** — purpose in one paragraph, inferred from page titles, view names, tags, queries.
2. **How it is built** — navigation (routes, docks, popups), the reusable templates (views embedded with params), where data comes from (tag / query / history / script bindings), where logic runs (gateway scripts, library, inline).
3. **Conventions** — naming, folders, styling approach (classes vs inline vs theme tokens), tag naming.
4. **To replicate** — ordered build steps: tags/UDTs first, then queries and scripts, then templates, pages, docks, theme; name each pattern `id` from `patterns.md` you would reuse.
5. **Gaps and risks** — broken refs, unreferenced views, hex literals, anything the scan could not see.

Cite view/resource names exactly as in the inventory. Do not invent what the map does not show.

## 4. Limits (say so in the summary)

- Tag/UDT definitions and per-tag alarm config live in the tag provider, not the project: Scout lists tag paths *referenced* (regex over bindings/scripts; prose containing `[x]y` can give a false hit; paths with spaces can over-capture). Pull tag config separately when replicating.
- Alarm pipelines and reports are binary; Scout lists names and pipeline block types only. Vision windows/templates are inventoried by name, not decoded.
- A `.gwbk` is read for `projects/<name>/…` only; gateway config (DB connections, providers, users) inside its config DB is not decoded.
- Inherited-project resources (`parent`) are not merged; run Scout on the parent too.
