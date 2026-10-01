# Environment setup: `ignition-mcp` and the `global` project

Fresh-machine setup for #AIDriven Ignition development: what to clone, what
to recreate, and the one project on the gateway that everything above this
repo depends on.

---

## `ignition-mcp` is a separate tool

`ignition-mcp` (the MCP server providing `run_gateway_script`, `read_tags`,
etc.) is its own git repository, cloned separately from the driver toolkit.
The skill only carries a portable copy of
one of its operational scripts (`skill/scripts/deploy_webdev_endpoints.py`,
see below) because that script has no other durable home.

On a new machine:

1. Clone `ignition-mcp` fresh from its GitHub remote.
2. Recreate its `.env` (never committed — it holds the API key):
   ```ini
   IGNITION_MCP_IGNITION_GATEWAY_URL=http://<gateway-host>:8088
   IGNITION_MCP_IGNITION_API_KEY=<keyName>:<secret>
   IGNITION_MCP_SERVER_HOST=127.0.0.1
   IGNITION_MCP_SERVER_PORT=8007
   IGNITION_MCP_SSL_VERIFY=false

   # WebDev endpoints deployed in the `global` project
   IGNITION_MCP_WEBDEV_TAG_ENDPOINT=global/GatewayAPI/tags
   IGNITION_MCP_WEBDEV_TAG_CONFIG_ENDPOINT=global/GatewayAPI/tagConfig
   IGNITION_MCP_WEBDEV_ALARM_ENDPOINT=global/GatewayAPI/alarms
   IGNITION_MCP_WEBDEV_TAG_HISTORY_ENDPOINT=global/GatewayAPI/tagHistory
   IGNITION_MCP_WEBDEV_SCRIPT_EXEC_ENDPOINT=global/GatewayAPI/scriptExec
   IGNITION_MCP_ENABLE_SCRIPT_EXECUTION=true
   ```
   The API key needs **admin scope** on the gateway or native REST calls 403
   (`mcp-tool-map.md`).
3. Install with `uv` (`uv sync` / `uv run` per `ignition-mcp`'s own README).

---

## WARNING: the `global` project is required infrastructure, not a scaffold

The gateway's `global` project looks empty from its own metadata — no
Perspective views, no obvious content — and is easy to mistake for a
deletable default/scaffold project. **It is not.** It hosts the WebDev
Python resources that back 5 required `ignition-mcp` tool groups, plus 2
bonus diagnostic endpoints:

| Endpoint (`global/GatewayAPI/<name>`) | Backs tools | What breaks if deleted |
|---|---|---|
| `tags` | `read_tags`, `write_tag` | Tag reads and writes |
| `tagConfig` | `get_tag_config`, `create_tags`, `edit_tags`, `delete_tags`, `list_udt_types`, `get_udt_definition`, and (since this session) the `browse` action `browse_tags` now routes through | All tag configuration/edit, UDT listing, and tag browsing |
| `alarms` | `get_active_alarms`, `get_alarm_history`, `acknowledge_alarms` | Alarm status, history, acknowledgement |
| `tagHistory` | `get_tag_history` | Tag historian queries |
| `scriptExec` | `run_gateway_script` | Arbitrary gateway-scope Jython execution — the golden-path fallback for almost every other broken native-REST tool (`mcp-tool-map.md`) |
| `ping`, `health` | none (diagnostic only) | Nothing tool-facing; useful for probing that WebDev resources deploy correctly |

Deleting the `global` project or its `com.inductiveautomation.webdev/`
resources breaks tag config/edit, alarms, tag history, and gateway script
execution for every agent driving the gateway — not just a cosmetic
loss. Table sourced from `~/ignition-mcp/docs/webdev-setup.md`'s own
endpoint table.

**402/trial-timer stop rule:** every WebDev-backed call above 402s when the
gateway's trial timer lapses — do not confuse that with the endpoints being
missing. See the existing rule in `mcp-tool-map.md` ("The 402 stop rule")
and `workflow.md` ("Stop rules") — not duplicated here.

---

## Known trigger: restoring a gateway backup drops `global`

Loading a gateway backup replaces the whole project set, so any
previously-live projects (including `global`) are gone, replaced by whatever the
backup contained. `global` is not special-cased by a
gateway restore; it's an ordinary project and gets wiped like any other.

**Symptom:** every WebDev-backed `ignition-mcp` tool (`run_gateway_script`,
tag config/edit, alarms, tag history) returns a persistent
`405 Method Not Allowed` on `…/GatewayAPI/<name>` — not a 402 (trial timer)
and not a connection error, which makes it easy to mistake for a broken MCP
server rather than a missing gateway-side resource. Native REST tools
(`get_gateway_info`, `list_projects`, `get_project`) keep working through
this, which is the fastest way to confirm the diagnosis: `get_project` with
`name: "global"` returning 404 means the project itself is gone, not just
one endpoint.

**Any gateway backup restore should be followed by checking `global` exists**
before assuming `ignition-mcp` is fully functional again — don't wait for a
405 to notice.

## Recreating the `global` project if it's ever missing

1. If the project doesn't exist: `create_project` with name exactly
   `global` (lowercase — the WebDev endpoint paths and every `.env` var
   above are hardcoded to that casing).
2. Run the deploy script — **use the skill's copy** (`scripts/deploy_webdev_endpoints.py`),
   not one assumed to live inside `ignition-mcp`. Run it from the `ignition-mcp` checkout
   (for its `uv` environment), pointing at the script by full path:
   ```bash
   cd <ignition-mcp-checkout> && uv run python \
     <skill-dir>/scripts/deploy_webdev_endpoints.py full
   ```
   This builds a ZIP of the 7 `GatewayAPI/*` WebDev resources and POSTs it
   to `/data/api/v1/projects/import/global?overwrite=true` (8.3.9 has no
   direct resource-write route — see `resource-formats.md` §7). No MCP-server
   restart needed afterward — `run_gateway_script` picked it up immediately
   on the next call.

---

## The `browse_tags` fix

**What was wrong:** `browse_tags` called the native REST endpoint
`GET /data/api/v1/entity/browse`. That endpoint is the gateway's
status/diagnostics **entity tree** (JVM/host/config metrics), not a tag
browser — confirmed live via direct curl: a real tag path like
`[<provider>]Folder` returns `200 []`, not tag children. This matches
`mcp-tool-map.md`'s existing `browse_tags` row.

**The fix:** added a `browse` action to the `tagConfig` WebDev resource
(`skill/scripts/deploy_webdev_endpoints.py`'s `TAGCONFIG['doPost']`). It
calls `system.tag.browse()` recursively up to depth 4, returning
`{name, path, hasChildren, tagType, children}` per node. `browse_tags`
should be repointed to route through `tagConfig`'s `browse` action instead
of the native entity-browse endpoint.

**Deploy status:** the gateway-side resource is already redeployed live
(via `deploy_webdev_endpoints.py full`). The fix only takes
effect client-side after an **`ignition-mcp` MCP-server restart** — the
running server process has the old `browse_tags` implementation cached in
memory even though the gateway-side WebDev resource is current.

---

## Native REST theme/font/icon CRUD 

A theme's `classes.css` may have no generator script in the driver repo — style additions
then get read/appended gateway-side via `run_gateway_script`. There is a cleaner mechanism than a
raw file read/append: the gateway's `GET /openapi.json` (`http://<gateway>/openapi`
for the human-readable ReDoc viewer) documents a full native REST CRUD surface
for Perspective themes, fonts, and icons — **gateway-scoped resources**, not
project resources, so they sit outside the "no direct project-resource-write
route" limitation (`mcp-tool-map.md`'s "Project resources" section):

| Endpoint | Verb | Purpose |
|---|---|---|
| `/data/api/v1/resources/list/com.inductiveautomation.perspective/themes` | GET | List installed themes |
| `/data/api/v1/resources/find/com.inductiveautomation.perspective/themes/{name}` | GET | Read one theme's config |
| `/data/api/v1/resources/com.inductiveautomation.perspective/themes` | PUT/POST | Create/modify theme resource metadata (`entrypoint`, `isPrivate`, etc.) |
| `/data/api/v1/resources/datafile/com.inductiveautomation.perspective/themes/{name}/{filename}` | GET/PUT/DELETE | The actual theme file content (e.g. `classes.css`) — this is the one that replaces the gateway-side read/append hack |
| same pattern under `.../fonts` and `.../icons` | — | Custom font and icon CRUD, same shape |

Schema-confirmed against the live gateway's OpenAPI spec, not yet
exercised end-to-end (no theme write attempted at time of writing). The `datafile/.../{filename}`
PUT is the one worth trying first — it should let a script push updated
`classes.css` content directly instead of the current read-full-file →
string-append → write-full-file pattern over `run_gateway_script`.
