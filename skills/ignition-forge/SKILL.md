---
name: ignition-forge
description: >-
  Use to replicate, rebuild, clone or migrate an existing Ignition project into a target project: turns a Scout decode (map.json + source export) into a re-runnable build script, deploys it to the target and proves it with FAT + SAT. Deterministic script, no LLM, no MCP.
---

# Ignition Forge — project replicator

Base dir: `~/.claude/skills/ignition/` (paths relative to it). Load core `ignition` and `ignition-scout` first.
HTTP 402 (exit 3) = trial lapsed: report and stop.

## 1. Run

```
python3 scripts/scout.py --live <Source> -o scout-report/            # or --zip / --gwbk
python3 scripts/forge.py --scout scout-report/ --live <Source> --name <build>   # or --zip export.zip
# create the empty target project (Designer, or ignition-mcp create_project), then:
python3 scripts/loop.py <repo>/scripts/builds/<build> --project <Target>       # build -> FAT -> deploy -> SAT
python3 scripts/scout.py --live <Target> -o target-report/
python3 scripts/scout.py --diff scout-report/map.json target-report/map.json
```

Forge writes `<out-root>/<build>/` (default `--out-root`, the repo's build folder): `build.py`, `src/` (verbatim resources), `tags.json`.
`build.py` copies `src/` to `_staged/` (fsync, `resource.json` last) and holds no project name, so one build deploys to any target. Re-run Forge to refresh `src/` from a changed source.

## 2. What is staged

Roots `com.inductiveautomation.perspective/` and `ignition/`: views, page-config, style classes, session props, inactivity props, named queries, script library, gateway timer/message scripts. Everything else in the source (alarm pipelines, event streams, reports, Vision) is reported in Forge's output as `not_staged`: rebuild by hand (`ignition-alarms`, `ignition-data`).

## 3. Tags

An export has no tag/UDT definitions. `tags.json` lists referenced tag paths (`suspect: true` = probable regex false hit). Create them on the target first (`ignition-tags`; pull definitions from the source provider), or set `RETARGET = {"OldProvider": "NewProvider"}` in `build.py`. SAT fails on missing tags: that is the proof they are in place.

## 4. Expect in the `--diff`

Project name/description; resources and patterns for the not-staged types; tag references that came only from not-staged resources. Any other difference is a defect: fix the source of it, do not edit `_staged`.

## 5. Limits

Session props and page-config are copied verbatim (target theme, tag provider default, DB and user source are gateway/project settings, not resources: set them on the target). Inherited (`parent`) resources are not merged. Never deploy into the source project.
