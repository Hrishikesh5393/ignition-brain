# ignition-mcp Tool Map (gateway 8.3.9)

Every `ignition-mcp` tool, what it hits under the hood, its status on the target
gateway (**8.3.9**, standard, Trial — live: `get_gateway_info` 2026-09-04), and the
ground-truth fallback when it's broken. Source: `~/ignition-mcp/src/ignition_mcp/`
(`ignition_client.py`, `tools/*.py`) + live probes 2026-09-04.

Two transports:
- **Native REST** — `GET/POST /data/api/v1/…`, auth header `X-Ignition-API-Token: <keyName>:<secret>`
  (the API key must have **admin scope** or every call 403s — build-notes `ignition-mcp-setup`).
- **WebDev** — `POST /system/webdev/global/GatewayAPI/<name>`, python resources deployed in
  the `global` project. **Every WebDev-backed tool returns HTTP 402 when the trial timer
  has lapsed** (§ 402 rule below). Native REST keeps working through a 402.

---

## The golden path — `run_gateway_script`

`run_gateway_script` (WebDev `…/GatewayAPI/scriptExec`) runs arbitrary Jython in **full
gateway scope** and is the fallback for almost everything below. Live-verified working
2026-09-04.

- **Disabled by default** — needs `IGNITION_MCP_ENABLE_SCRIPT_EXECUTION=true` (already set
  in this deployment's `.env`).
- Return values: set a module-level **`result`** variable (JSON-serialised) or `print()`.
  Response shape: `{"result":…, "stdout":…, "scriptHash":…, "error":…}`.
- **Result is capped (~110 KB).** For large output, write it to a workspace file from the
  script (`open(r"C:\…","w")`) and read that file in a follow-up call.
- **`timeout_secs` max 60** (client + gateway both enforce).
- Gateway runs as the same OS user → the script can `open()` files under the Ignition
  install dir and the workspace directly.
- **Classloader isolation:** you cannot `import` Perspective/Vision gateway classes in the
  sandbox. Reach their context via:
  ```python
  ctx = (IgnitionGateway.get().getModuleManager()
         .getModule("com.inductiveautomation.perspective").getHook().getContext())
  ```
- Every execution is logged gateway-side with its `scriptHash` (logger `GatewayAPI.scriptExec`).

---

## Gateway diagnostics

| Tool | Under the hood | 8.3.9 status | Fallback |
|------|----------------|--------------|----------|
| `get_gateway_info` | REST `GET /gateway-info` | **works** ( — live 2026-09-04) | — |
| `get_module_health` | REST `GET /modules/healthy` | **works** | — |
| `get_gateway_logs` | REST `GET /logs` | **works** ( — live: returned WebDev error stacks 2026-09-04) | — |
| `get_database_connections` | tool calls REST `GET /connections/database` — **wrong URL**, always 404 | **tool is broken, platform isn't** — real endpoint `GET /data/api/v1/resources/list/ignition/database-connection` **works**, live-verified 2026-09-22 (returns full connection config, pool state, health) | Until the tool is repointed: call the real path directly, or `run_gateway_script`: `IgnitionGateway.get().getDatasourceManager().getDatasources()` |
| `get_opc_connections` | tool calls REST `GET /connections/opc` — **wrong URL**, always 404 | **tool is broken, platform isn't** — real endpoint `GET /data/api/v1/resources/list/ignition/opc-connection` **works**, live-verified 2026-09-22 | Until the tool is repointed: call the real path directly, or `run_gateway_script` via the OPC module context / `system.opc.getServers()` |
| `get_system_metrics` | REST `GET /system/metrics` | **404 broken** ( — live 2026-09-04) | `browse_tags` empty-path returns the `jvm`/`host`/`status` metric tree (§ browse_tags); or `run_gateway_script` |
| `list_designers` | REST `GET /designers` | **works** ( — live: `{items:[]}` 2026-09-04) | — |

---

## Projects

| Tool | Under the hood | 8.3.9 status | Fallback |
|------|----------------|--------------|----------|
| `list_projects` | REST `GET /projects/list` | **works** ( — live: lists every project incl. `global`) | — |
| `get_project` | REST `GET /projects/find/{name}` | **works** ( — live 2026-09-04) | — |
| `create_project` | REST `POST /projects` | **works** ( — build-notes: creates a project) | — |
| `delete_project` | REST `DELETE /projects/{name}?confirm=true` | works (native) — irreversible | — |
| `copy_project` | REST `POST /projects/copy` | native — not re-tested | `run_gateway_script`: `pm.copy(...)` |
| `rename_project` | REST `POST /projects/rename/{name}` | native — not re-tested | — |
| `export_project` | REST `GET /projects/export/{name}` → base64 ZIP | native — not re-tested | — |
| `import_project` | REST `POST /projects/import/{name}` (`application/zip`) | **works** ( — this is how the WebDev endpoints are deployed) | — |

---

## Scan control — native REST, no `ignition-mcp` tool wraps these yet

Discovered via the gateway's own OpenAPI spec (`GET /openapi.json`, 588 documented
paths — most of the ignition-mcp tool coverage only reaches a fraction of it). These
two are the write-protocol-relevant ones; full multi-file usage in
`resource-formats.md` §11.

| Endpoint | Under the hood | 8.3.9 status |
|------|----------------|--------------|
| `GET /data/api/v1/scan/projects` | Returns `{scanActive, lastScanTimestamp, lastScanDuration}` | **works**, live-verified 2026-09-22 — real scan-completion signal instead of trusting a Jython `requestScan()` call blindly returned |
| `POST /data/api/v1/scan/projects` | Triggers a project filesystem scan; also releases the scan-lock if one is held | **works** (schema-confirmed; not yet POST-tested live — GET status and the paired scan-lock endpoints below were) |
| `GET /data/api/v1/scan-lock/projects` | Returns lock info (`timestamp`, `remaining`, `actor`) or `204` if none held | **works**, live-verified 2026-09-22 (`204`, no lock held) |
| `POST /data/api/v1/scan-lock/projects` | Acquires an exclusive window where "it is safe to make external changes to the filesystem" (the platform's own doc string) — released by the next `POST /scan/projects` | **works**, live-verified 2026-09-22 — **requires a JSON body**, `{"acquireTimeout":10,"holdTimeout":60}`; an empty POST 500s despite the endpoint description reading as if a body is optional |
| `GET /data/api/v1/scan/projects` (poll after triggering) | `{scanActive, lastScanTimestamp, lastScanDuration}` | **live-verified but `scanActive`/timestamp did not update within ~5s** of a real, successfully-applied change (2026-09-22) — treat this status endpoint as unreliable for fast confirmation; verify the actual write via `pm.find("<proj>").get().getResources()` / `getProjectCache()` instead (§11), don't poll-wait on this field |

Auth: same `X-Ignition-API-Token: <keyName>:<secret>` header as every other native
call. Use these instead of the Jython `requestScan()` path for any write touching
more than one resource file.

---

## Project resources — all broken on 8.3.9, use the gateway-side write loop

| Tool | Under the hood | 8.3.9 status | Ground truth |
|------|----------------|--------------|--------------|
| `list_project_resources` | REST `GET /projects/{p}/resources` | **404 broken** ( — live 2026-09-04) | `run_gateway_script`: `pm.find("<p>").get().getResources()` → list of `ResourcePath` ( — live-verified 2026-09-04) |
| `get_project_resource` | REST `GET /projects/{p}/resources/{path}` | **404 broken** ( — live 2026-09-04) | `run_gateway_script`: `open(r"…\data\projects\<p>\<module>\<type>\<name>\<file>","rb").read()` ( — live-verified 2026-09-04) |
| `set_project_resource` | REST `PUT /projects/{p}/resources/{path}` | **broken / unreliable on 8.3.9** ( — build-notes) | `run_gateway_script`: write files with `flush()`+`os.fsync()`, then `pm.requestScan()`, then verify — see `workflow.md` and `resource-formats.md` §10–11 |
| `delete_project_resource` | REST `DELETE /projects/{p}/resources/{path}` | broken (same route) | `run_gateway_script` via `ProjectManager` delete API; never `shutil.rmtree` a live resource dir (file locks) |

---

## Tag providers (configuration)

| Tool | Under the hood | 8.3.9 status |
|------|----------------|--------------|
| `list_tag_providers` | REST `GET /resources/list/ignition/tag-provider` | **works** ( — live 2026-09-04: `System` 36 tags, `default` STANDARD **13 832 tags**) |
| `get_tag_provider` | REST `GET /resources/find/ignition/tag-provider/{name}` | works (native) |
| `create_tag_provider` | REST `POST /resources/ignition/tag-provider` | native — not re-tested |
| `delete_tag_provider` | REST `POST /resources/delete/ignition/tag-provider` | native — irreversible, not re-tested |

---

## Tags & UDTs

| Tool | Under the hood | 8.3.9 status | Ground truth for the broken ones |
|------|----------------|--------------|----------------------------------|
| `browse_tags` | REST `GET /entity/browse` | **fixed** — was calling the wrong native endpoint (gateway diagnostics entity tree, not tags), always empty; now routes through `tagConfig`'s new `browse` action (`system.tag.browse`, recursive depth 4). Needs an `ignition-mcp` server restart to pick up client-side. See `environment-setup.md` | `run_gateway_script`: `system.tag.browse("[<provider>]Folder").getResults()` — query **narrow subtrees only**, never a provider root |
| `read_tags` | WebDev `…/tags` `{paths:[…]}` | **works** ( — live 2026-09-04: `[<provider>]Folder/Tag` → 25.62 Good) | — |
| `write_tag` | WebDev `…/tags` `{tagPath,value,dataType?}` | works on existing tags ( — build-notes) | `run_gateway_script`: `system.tag.writeBlocking([p],[v])` |
| `get_tag_config` | WebDev `…/tagConfig` `getConfig` | **500 broken** — `TagPathFormatException: Invalid source or array specification` in `TagPathParser` inside `AbstractTagUtilities.getConfiguration` ( — live gateway log 2026-09-04) | `run_gateway_script`: `system.tag.getConfiguration("[default]…", True)` |
| `create_tags` | WebDev `…/tagConfig` `configure` editMode `a` | **broken** — returns `{"results":["Good"]}` but **nothing is created** ( — build-notes) | `run_gateway_script`: `system.tag.configure("[default]<folder>", [<cfg>…], "o")` in dependency order — proven path for the 16-type UDT library |
| `edit_tags` | WebDev `…/tagConfig` `configure` editMode `m` | suspect (same endpoint/bug family) | `run_gateway_script`: `system.tag.configure(base, tags, "m")` |
| `delete_tags` | WebDev `…/tagConfig` `deleteTags` | not verified (same endpoint) | `run_gateway_script`: `system.tag.deleteTags([…])` |
| `list_udt_types` | WebDev `…/tagConfig` `listUDTTypes` | **works** ( — live 2026-09-04: 16 types under `[default]_types_`) | — |
| `get_udt_definition` | WebDev `…/tagConfig` `getUDTDefinition` | **500 broken** (same `TagPathParser` bug — live 2026-09-04) | `run_gateway_script`: `system.tag.getConfiguration("[default]_types_/<Name>", True)` |

---

## Alarms & history

| Tool | Under the hood | 8.3.9 status | Notes / fallback |
|------|----------------|--------------|------------------|
| `get_active_alarms` | WebDev `…/alarms` `getActive` | **works** ( — live 2026-09-04) | filters: `sourceFilter`, `priorityFilter`, `stateFilter` |
| `get_alarm_history` | WebDev `…/alarms` `getHistory` | **degraded** — returns a graceful `note` ("No alarm journal profile specified"), `entries:[]` until an Alarm Journal profile exists ( — live 2026-09-04) | configure a journal profile gateway-side, or pass `journalName` |
| `acknowledge_alarms` | WebDev `…/alarms` `acknowledge` | not tested | `run_gateway_script`: `system.alarm.acknowledge([...], note)` |
| `get_tag_history` | WebDev `…/tagHistory` (wraps `system.tag.queryTagHistory`) | not tested (needs history-enabled tags + a historian) | `run_gateway_script`: `system.tag.queryTagHistory(paths=…, startDate=…, endDate=…)` |

---

## The 402 stop rule

A WebDev-backed call returning **HTTP 402 Payment Required** means the gateway's ~2-hour
**Trial timer has lapsed** (Perspective/WebDev are trial modules). When that happens:

1. append `blocked: gateway trial timer needs a reset` to the status file and **stop**.
2. **Do not** try to reset it — a human clears it from the gateway's
   "Trial Mode" banner → "Reset Trial".
3. Native REST tools (`get_gateway_info`, `list_projects`, tag-provider list, …) still
   work through a 402 — use them if you only need read-only gateway facts.

---

## Driving this same server outside Claude Code

The `ignition-mcp` connection details (command, args, env) live in `~/.claude.json`
under `mcpServers.ignition-mcp` — the same block Claude Code reads to launch it. A
non-Claude-Code driver (a Gemini/Ollama agent, a standalone script) can read that block
directly instead of hardcoding a second copy of the connection config, so both harnesses
stay pointed at one source of truth. Pattern borrowed from `ignition-brain/tools/ignition_agent.py`.
