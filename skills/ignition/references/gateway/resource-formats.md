# Ignition 8.3.x Project Resource Formats

How an Ignition 8.3 project is laid out on disk, the exact `resource.json` schema, the
per-type payload files, and the write protocol that keeps the gateway from caching a
half-written file. Target gateway: **8.3.9** ( — live: `get_gateway_info` 2026-09-04,
`ignitionVersion` `8.3.9 (b2026082511)`, standard edition, JVM 17). Resources are never
edited by hand — they are written gateway-side through `ignition-mcp` (see
`mcp-tool-map.md`) and then scanned. This file is the format spec those writes must match.

---

## 1. Where a project lives

```
<install>/data/projects/<project-name>/          ( — e.g. `C:\Program Files\Inductive Automation\Ignition\data\projects\` on Windows)
  project.json                                    project manifest (see §3)
  <module-id>/<resource-type>/<name.../>          one directory per resource
    resource.json                                 resource manifest (see §2)
    <payload files>                               view.json, code.py, config.json, …
<install>/data/projects/.resources/               gateway's resource cache — see §9, do not touch
```

- The **project name is the directory name** — `project.json` carries no `name` field
  ( — live: `data/projects/<project>/project.json` = `{"title","description","enabled","inheritable","parent"}`).
- A resource's **path** is `<module-id>/<resource-type>/<name>` where `<name>` may itself
  contain `/` for nesting (e.g. `views/templates/MetricTile`).
- Module-scoped top directories seen on a real project ( — live: `pm.find("<project>").get().getResources()`):

| Directory | Resource types under it |
|-----------|-------------------------|
| `com.inductiveautomation.perspective/` | `views/`, `page-config/`, `session-props/`, `general-props/` |
| `com.inductiveautomation.webdev/` | `resources/` (the literal segment `resources` matters — see §7) |
| `ignition/` | `timer/`, `event-scripts` family (`startup/`, `shutdown/`, `message/`, `tag-change/`, `scheduled-script/`), `script-python/`, `named-query/` (see §12) |
| `com.inductiveautomation.vision/` | `client-tags/`, windows, templates |
| `com.inductiveautomation.alarm-notification/` | `alarm-pipelines/` (alarm notification pipelines — see §13) |

---

## 2. `resource.json` — the resource manifest

One per resource directory. Verified field-by-field against decompiled
`com.inductiveautomation.ignition.common.resourcecollection.json.ResourceManifestSerializer`
and `ResourceManifest.Builder`.

| Field | Type | Required? | Default if absent | Notes |
|-------|------|-----------|-------------------|-------|
| `scope` | string | optional | `null` | `"G"` gateway, `"D"` designer, `"DG"` designer+gateway, `"C"` client, `"A"` all. Perspective/timer resources use `"G"`; live named queries use `"DG"` (most) or `"G"`. |
| `version` | int | optional | `1` | `ResourceManifest.RESOURCE_VERSION` = 1. |
| `restricted` | bool | optional | `false` | |
| `overridable` | bool | optional | `true` | |
| `files` | string[] | optional | `[]` (empty set) | Names of the payload files in this dir. Read into a `HashSet` — **order irrelevant**, duplicates collapse. |
| `attributes` | object | optional | `{}` | Free-form `Map<String,JsonElement>`. Resource-type-specific keys (timer delay, last-modification signature) live here. |
| `documentation` | string | optional | `null` | Project resources read/write this under the key **`documentation`** (collections use `description`) — decompiled `ResourceManifestSerializer.forProject()`. |

Every field is optional and lenient — a missing or malformed `resource.json` degrades to
defaults rather than failing the scan. Minimal valid manifest for a Perspective view
( — live: written by the phase-3 builder, accepted by the gateway):

```json
{ "scope": "G", "version": 1, "restricted": false, "overridable": true,
  "files": ["view.json"], "attributes": {} }
```

When the **Designer** saves a resource it adds audit attributes
( — live: `views/<view>/resource.json`):

```json
"attributes": {
  "lastModificationSignature": "e9e46c8f…",
  "lastModification": { "actor": "admin", "timestamp": "2026-09-03T09:09:45Z" }
}
```

You do **not** need to write those — omit `attributes` or leave it `{}`.

---

## 3. `project.json`

( — live: `data/projects/<project>/project.json`)

```json
{ "title": "My Project", "description": "Example project …",
  "enabled": true, "inheritable": false, "parent": "" }
```

All fields optional. `parent` is the inherited project name (`""` = standalone).
Create projects with the `create_project` MCP tool, not by writing this file.

---

## 4. Perspective view — `com.inductiveautomation.perspective/views/<Name>/`

| File | Required? | Content |
|------|-----------|---------|
| `view.json` | **yes** | the view tree (below) |
| `resource.json` | yes | manifest; `files` should list `view.json` (+ `thumbnail.png` if present) |
| `thumbnail.png` | no | written by the Designer on save; never required at runtime ( — live: builder-written views have none, Designer-saved views do) |

`view.json` shape — verified against decompiled
`perspective-common …/config/ViewConfig.java` and `ComponentConfig.java`:

```json
{
  "custom": {},                         // optional  — view-scope custom props
  "params": { "title": "Instance" },    // optional  — view input/output params (default values)
  "props":  { "defaultSize": { "width": 1100, "height": 620 } },   // optional
  "propConfig": { … },                  // optional  — bindings on view.params.* / view.custom.*
  "root": { … ComponentConfig … }       // REQUIRED  — the root component (usually a container)
}
```

Each **component node** (`ComponentConfig`):

| Key | Required? | Default | Notes |
|-----|-----------|---------|-------|
| `type` | **yes** | — | e.g. `ia.container.flex`, `ia.display.label`. Missing `type` fails the parse. |
| `version` | no | `0` | component schema version |
| `props` | no | `{}` | component props — must match the component schema (`component-schemas.md`) |
| `meta` | no | `{}` | `{"name": "<uniqueChildName>"}` — the name shown in the component tree / used in expressions |
| `position` | no | `{}` | layout hints **for this child inside its parent container** — keys depend on the parent's `childPositionSchema` (flex: `grow`/`shrink`/`basis`; coord: `x`/`y`/`width`/`height`; tab: `tabIndex`) |
| `custom` | no | `{}` | per-component custom props |
| `propConfig` | no | `{}` | bindings/transforms keyed by property path (§6) |
| `events` | no | — | component event scripts |
| `children` | no | `[]` | array of child `ComponentConfig` (containers only) |

---

## 5. `page-config` — `com.inductiveautomation.perspective/page-config/config.json`

Verified against decompiled `perspective-common …/config/PagesConfig.java` +
`PageConfig.java` ( — live: `data/projects/<project>/com.inductiveautomation.perspective/page-config/config.json`):

```json
{
  "pages": {
    "/":     { "viewPath": "Dashboard", "title": "Dashboard" },
    "/tags": { "viewPath": "TagValues", "title": "Tag Values" }
  },
  "sharedDocks": {}
}
```

- Map key = the URL **mount path**. Value keys: **`viewPath`** (NOT `primaryView`),
  `title`, optional `docks`.
- `resource.json` `files` = `["config.json"]`.
- `ResourceType` is `("com.inductiveautomation.perspective", "page-config")`, filename
  `config.json` — decompiled `PagesConfig.RESOURCE_TYPE` / `FILENAME`.

**`sharedDocks`** — a sibling key to `pages`, one array per anchor:

```json
"sharedDocks": {
  "top": [ { "id": "…", "anchor": "fixed", "autoBreakpoint": 480, "content": "push",
             "handle": "hide", "iconUrl": "", "modal": false, "resizable": false,
             "show": "visible", "size": 60, "viewParams": {},
             "viewPath": "docks/TopBar" } ],
  "bottom": [], "left": [], "right": []
}
```

Every `viewPath` referenced here is another dangling-reference hazard: deleting or
moving a shared-dock's target view without removing this entry breaks
`getProject`/project-diff for **every route**, the same class of gateway-wide failure
as the `events`/`ActionConfig` NPE above — verify no `sharedDocks` entry still points
at a view being removed before deleting it.

---

## 6. Perspective binding JSON

Lives under a component's `propConfig`, keyed by the **fully-qualified property path**
(`props.text`, `props.data`, …). Verified against decompiled
`perspective-common …/config/BindingConfig.java`, the `*BindingConstants` interfaces,
and gateway `…/binding/tag/TagBindingConfig.java`.

```json
"propConfig": {
  "props.text": {
    "binding": {
      "type": "tag | expr | property | query | http | tag-history",
      "config": { … type-specific … },
      "transforms": [ { "type": "…", … } ],     // optional, array
      "enabled": true                            // optional; omit unless disabling
    }
  }
}
```

`config` keys per type ( — decompiled constants):

| `type` | key(s) in `config` |
|--------|--------------------|
| `property` | `path` — e.g. `"view.params.title"` ( — `PropertyBindingConstants.CONFIG_SOURCE_PATH`) |
| `expr` | `expression` — e.g. `"'Members - ' + {view.params.instancePath}"` ( — `ExpressionBindingConstants.CONFIG_EXPRESSION`) |
| `tag` | **`tagPath`**, `mode` (`"direct"`\|`"indirect"`\|`"expression"`), `references`, `fallbackDelay` ( — `TagBindingConstants`; parser default `fallbackDelay` 2.5) |
| `query` | see §6a |
| `http` | see §6b |
| `tag-history` | see §6c |

A shared `polling` object appears on `query`/`http`/`tag-history` bindings:
`{"enabled": false, "rate": "30"}` — `rate` is a **string** (seconds), `enabled`
default `false` ( — decompiled `PollingConfig.fromJson`).

### 6a. `query` binding

Verified against decompiled `QueryBindingConfig.java`, `QueryBindingConfig.fromJson`:

```json
"binding": { "type": "query", "config": {
  "queryPath": "path/to/NamedQuery",
  "mode": "direct",
  "returnFormat": "auto",
  "designerUseLimit": true,
  "enableValueCache": true,
  "polling": { "enabled": false, "rate": "30" },
  "parameters": { "siteId": "{view.params.siteId}" },
  "parametersMeta": {}
} }
```

- `queryPath` — project-relative named-query path (required-non-blank).
- `mode` — enum `QueryPathMode`, default `"direct"` (uppercased before parse —
  the JSON value itself is lowercase: `"direct"` or `"expression"`).
- `returnFormat` — enum `QueryReturnFormat`, default `"auto"`.
- `parameters` — flat `{paramName: "<value-or-binding-expr-string>"}` map, every
  value read as a string (bind sub-expressions inline as a string, not nested JSON).
- `enableValueCache` — legacy alias `bypassCache` (inverted) still read if
  `enableValueCache` absent; write `enableValueCache` directly, don't use the alias.
- `designerUseLimit` default `true` — caps rows in the Designer preview only.

### 6b. `http` binding

Verified against decompiled `HttpBindingConfig.java` + nested `RequestConfig`/`AuthConfig`:

```json
"binding": { "type": "http", "config": {
  "request": {
    "url": "https://api.example.com/status",
    "method": "GET",
    "header": [ { "key": "Accept", "value": "application/json" } ],
    "body": null,
    "auth": { "type": "None", "value": "" }
  },
  "enableCookies": true,
  "connectTimeout": 30000,
  "socketTimeout": 30000,
  "enableValueCache": true,
  "polling": { "enabled": false, "rate": "30" }
} }
```

- `request` is **required**; `request.url` and `request.method` are required
  strings inside it. `method` enum: `GET|HEAD|POST|PUT|DELETE|TRACE|OPTIONS|CONNECT|PATCH`.
- `request.header` — **array** of `{"key","value"}` objects (not a flat map).
- `request.auth.type` — enum `None|Basic|Bearer|Digest`; `request.auth.value` is
  a single string (for `Basic`, `user:pass` pre-formatted by the author — the
  class does no credential splitting itself).
- `connectTimeout`/`socketTimeout` — ms, default `30000` each.

### 6c. `tag-history` binding

Verified against decompiled `TagHistoryBindingConfig.java`, `fromJson` +
nested `Builder`:

```json
"binding": { "type": "tag-history", "config": {
  "dateRange": { "startDate": "{view.custom.startDate}", "endDate": "{view.custom.endDate}" },
  "tags": [ { "path": "[default]Site/Line/Temperature", "aggregate": "Average", "alias": "temp" } ],
  "returnFormat": "Wide",
  "returnSize": { "type": "natural" },
  "polling": { "enabled": true, "rate": "10" },
  "aggregate": "MinMax",
  "ignoreBadQuality": false,
  "preventInterpolation": false,
  "avoidScanClassValidation": false,
  "valueFormat": "dataset",
  "enableValueCache": true
} }
```

- **`dateRange` is required** and is **either/or**: `startDate`+`endDate`
  (historical) **or** `mostRecent`+`mostRecentUnits` (realtime, e.g.
  `{"mostRecent": "15", "mostRecentUnits": "MINUTE"}`) — setting both or
  neither throws `IllegalArgumentException` at build time.
- `tags` — either an **array** of `{"path", "aggregate"?, "alias"?}` objects, or
  a bare **string expression** in a field literally named `tags` (mutually
  exclusive with the array form — `tagsExpr` internally).
- `returnSize.type` enum `RAW|NATURAL|FIXED|INTERVAL`; `FIXED` needs `numRows`,
  `INTERVAL` needs `delay`+`delayUnits`.
- `returnFormat` enum `Wide|Tall|...` (capitalized), default `Wide`.
- `valueFormat` enum `DATASET|DOCUMENT` (uppercase in the enum, lowercase
  accepted in JSON — parser uppercases before matching), default `DATASET`.
- `aggregate` default `MinMax`; per-tag `aggregate` on a `tags[]` entry
  overrides it for that tag only.

Indirect tag binding — the tag path is a template with `{N}` slots filled from `references`:

```json
"binding": { "type": "tag", "config": {
  "tagPath": "{0}",
  "mode": "indirect",
  "references": { "0": "{view.params.tableTag}" },
  "fallbackDelay": 2.0 } }
```

( — live: `views/templates/InstancePanel/view.json` `props.data` binding, 2026-09-04.)
Direct binding: `"mode": "direct"`, `"tagPath": "[default]Site/Line/Temperature"`, no `references`.

---

## 7. WebDev python resource — `com.inductiveautomation.webdev/resources/<route>/`

Hard-won format ( — verified build-notes `ignition-mcp-setup`, and the deployed
`global/GatewayAPI/*` endpoints the MCP tools call):

- Path **must** be `com.inductiveautomation.webdev/resources/<routePath>/` — the literal
  `resources` segment is the `ResourceType("com.inductiveautomation.webdev","resources")`
  name. Omit it and the module silently ignores the resource → HTTP 404.
- `resource.json`: `{"scope":"G","version":1,"restricted":false,"overridable":true,"files":[…],"attributes":{}}`
- `config.json`: `{"resource-type":"python-resource","doGet":{…},"doPost":{…}, …}` — each
  method object has **kebab-case** keys: `enabled`, `require-https`, `require-auth`,
  `user-source`, `required-roles`, `max-retry-attempts`.
- **One file per HTTP method**: `doGet.py`, `doPost.py`, … Each file's **first line must
  start with `def doX(request, session):`** — if it doesn't, the loader tab-indents the
  whole file and it breaks. Return a dict: `{'json': …}` / `{'html': …}` /
  `{'response': {'code': N}}`.
- Jython 2.7: use `exec script in g, g` (qualified), catch Java exceptions with a bare
  `except:` + `sys.exc_info()`.
- Deploy/update via `ignition-mcp/deploy_webdev_endpoints.py full` (builds a project ZIP,
  POSTs to `/data/api/v1/projects/import/global?overwrite=true` — 8.3.9 has no direct
  resource-write route).

---

## 8. Gateway timer script — `ignition/timer/<Name>/`

Verified against decompiled `common …/script/ScriptConfig.java` (`record TimerScript`)
and `common …/script/TimerKey.java` (`Serializer`) ( — live:
`data/projects/<project>/ignition/timer/<Timer>/`).

| File | Content |
|------|---------|
| `handleTimerEvent.py` | starts with `def handleTimerEvent():` then a **TAB-indented** body. The runtime does `descriptor.buildMethod()` + `extractUserScript(file, "handleTimerEvent")` — it round-trips the `def` line. |
| `resource.json` | `files: ["handleTimerEvent.py"]`, and `attributes` carries the timer key: |

```json
"attributes": { "delay": 3000, "fixedDelay": true, "sharedThread": true, "enabled": true }
```

( — live `<Timer>/resource.json`; `delay` in ms, read as `getAsLong`; other three
`getAsBoolean`; `TimerKey` defaults `delay=1000, fixedDelay=true, sharedThread=true,
enabled=true`.) The timer runs in that project's **gateway scope** — `system.tag.*`,
`system.db.*`, `system.dataset.*` all work. Sibling event-script types under `ignition/`
follow the same shape: `startup/onStartup.py`, `shutdown/onShutdown.py`,
`message/handleMessage.py`, `tag-change/onTagChange.py` — decompiled `ScriptConfig`.

**`tag-change/onTagChange.py` — the real 5-param signature**, verified against
decompiled `ScriptConfig.TagChangeScriptEvent.DESCRIPTOR` and
`TagChangeScriptExecutor.invoke()`'s positional argument array:

```python
def onTagChange(initialChange, newValue, previousValue, event, executionCount):
	# stored on disk with this `def` line and a TAB-indented body, same as the timer script above
	if not initialChange and newValue.value != previousValue.value:
		system.tag.writeBlocking(["[default]Site/Line/Alarm"], [True])
```

- `initialChange` — `bool`, `True` on the first execution after the script
  subscribes (startup/scan-mode change), not a real value transition — most
  scripts guard on `if not initialChange:` before acting.
- `newValue` / `previousValue` — `QualifiedValue` (`.value`, `.quality`,
  `.timestamp`); `previousValue` is `None` on the initial change.
- `event` — a bean-style object exposing **`.currentValue`, `.previousValue`,
  `.tagPath`, `.changes`** (`.changes` is a `Set` of which sub-properties
  changed — value/quality/timestamp — useful to skip quality-only churn).
- `executionCount` — `int`, monotonically increasing per script instance.
- Runs in **gateway scope**, one instance per tag-change resource, fired by the
  platform's tag subscription system — not something a script calls directly.

**Value-change binding (Perspective) vs. tag-change event script (gateway) — which one:**

| | Perspective value-change **binding** | gateway **tag-change script** |
|---|---|---|
| Where it lives | a component's `propConfig` (§6, `type: "tag"`) | `ignition/tag-change/<Name>/` (this section) |
| Scope | client/session — reactive UI update only | gateway — full `system.*` access |
| Use for | driving a component prop (color, text, value) directly off a tag | side effects: writing other tags, DB writes, alarms, messaging — anything beyond "show this value" |
| Cost model | one subscription per bound component instance | one subscription for the whole project, regardless of client count |

Reach for a binding first for anything that's purely "display this tag's value."
Reach for a tag-change script only when the reaction needs gateway-scope
capability (write, DB, alarm ack) or must fire once project-wide regardless of
how many clients are viewing — a value-change binding on every open client is
not a substitute for a single gateway-side reaction.

---

## 9. The project-relative view-path rule

Inside a view, **every reference to another view is project-relative** — the project
name is never a segment:

- `ia.display.view` → `props.path` = `"templates/MetricTile"` (not `"<project>/templates/MetricTile"`)
- `ia.display.flex-repeater` → `props.path`
- `ia.container.tab` child `viewPath`
- `page-config` `viewPath` (bare view name)

( — live: `views/templates/InstancePanel/view.json` flex-repeater `props.path` =
`"templates/MetricTile"`, 2026-09-04.)

---

## 10. THE FSYNC TRAP (critical — read before any gateway-side write)

Writing a resource file from Jython with `open(p,"wb").write(...)` **without
`os.fsync()`** lets the gateway's `ResourceTreeFileWatcher` catch the file at 0 bytes,
hash it to the empty-string digest
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and cache that
digest in `data/projects/.resources/` **and** in ProjectManager's in-memory model.
Because the watcher keys off `resource.json`'s mtime, **the poison survives later
rewrites of the data file**.

- **Symptom:** `resource.getData("view.json").get().getBytes()` has length 0 though the
  disk file is complete; a timer script fails with `SyntaxError: expecting INDENT (line 1)`.
- **Fix, every file, no exceptions:**
  ```python
  f = open(path, "w")
  f.write(text); f.flush(); os.fsync(f.fileno()); f.close()
  ```
  Write **all payload/data files before `resource.json`**. Then trigger a scan (§11).
- **If already poisoned:** you cannot un-poison in place — write the resource under a
  **fresh resource name** and delete the poisoned one.
- Reusable helper: `<repo>/scripts/lib/gateway_io.py` `fsync_write()` / `write_json()`.

**Large-payload corruption:** a multi-KB view.json/script passed as an inline string
literal to `run_gateway_script` (gzip+base64-encoded to fit) can arrive corrupted —
symptom `zlib.error: invalid distance too far back`. Passing megabyte-scale text
through a single JSON-encoded MCP call argument is the failure mode; the fix is to
stage the payload to a writable temp path first (the gateway-side script can read
its own filesystem) and have `run_gateway_script` copy from there instead of
carrying the bytes in the call itself.

### Gateway file locks

The running gateway holds OS file locks on live resource directories. `shutil.rmtree`
on a live resource dir throws `unlink()` errors. Delete resources through the platform
(`ProjectManager` / `system.*`), not the filesystem.

---

## 11. Write protocol (summary — full loop in `workflow.md`)

**Single-file write:**
1. Write the payload file gateway-side with `flush()` + `os.fsync(fileno())`.
2. Write `resource.json` last, same fsync.
3. Trigger a rescan — either `IgnitionGateway.get().getProjectManager().requestScan()`
   (Jython, via `run_gateway_script`) or the native REST equivalent below.
4. **Verify at runtime** — never trust the HTTP 200:
   `pm.find("<proj>").get().getResources()` lists the `ResourcePath`, or for Perspective
   `ctx.getProjectCache().get("<proj>").get().projectConfig.views` contains the view
   ( — live 2026-09-04, both confirmed).

**Multi-file write (a view + its page-config mount, a UDT plus its instances, any
change touching more than one resource) — prefer the scan-lock, verified live
2026-09-22:**

1. `POST /data/api/v1/scan-lock/projects` — acquires an exclusive window where the
   platform guarantees external filesystem changes are safe. **A JSON body is
   required** (`{"acquireTimeout": 10, "holdTimeout": 60}`, seconds, both
   optional but the object itself must be present) — an empty body 500s, live-
   verified 2026-09-22, despite the endpoint description reading as if a body
   is optional. Without this lock, an auto-scan can interleave between your
   first and second file write and observe a half-written project state — the
   same class of risk the single-file fsync trap (§10) guards against, but
   across files instead of within one.
2. Write every payload file for every resource, fsync each (§10's trap still
   applies per-file).
3. `POST /data/api/v1/scan/projects` — triggers the scan **and releases the
   scan-lock** in the same call (per the platform's own doc string: "The next
   call to `POST /data/api/v1/scan/projects` will release the lock").
4. **Don't trust `GET /data/api/v1/scan/projects` as a completion signal** —
   live-verified 2026-09-22: `scanActive`/`lastScanTimestamp` did not update
   within ~5s of a real, successfully-applied multi-file change. Go straight
   to step 5's real verification instead of polling this endpoint.
5. Verify at runtime as in the single-file case — `pm.find("<proj>").get().getResources()`
   for the raw resource, and for Perspective specifically
   `ctx.getProjectCache().get("<proj>").get().projectConfig.views` to confirm
   the gateway actually *parsed and loaded* the resource, not just that the
   file landed on disk.

Auth for both: same `X-Ignition-API-Token` header as every other native REST call
(`mcp-tool-map.md`). Neither endpoint is wrapped by an `ignition-mcp` tool yet —
call them directly (`curl` or an HTTP client from `run_gateway_script`, or a
future dedicated tool), not through `run_gateway_script`'s Jython path.

---

## 12. Named query — `ignition/named-query/<Name>/`

`ResourceType("ignition", "named-query")`. Two files: **`query.sql`** (raw SQL text) and
`resource.json` with `scope` `"G"`, `version` **`2`**, `files` `["query.sql"]`. The query
type (`Query` / `ScalarQuery` / `UpdateQuery`), target `database`, parameter list
(`{type, identifier, sqlType-int}`), caching (`cacheEnabled`/`cacheAmount`/`cacheUnit`)
and authorization (`permissions[]` of `{zone, role}`) all live in
`attributes`; the description goes in the top-level `documentation` key (not an
attribute). `<Name>` may contain `/` for folders.

Full field-by-field schema, provenance, the three query types, `:name`/`{name}`
substitution, the Designer-only row-limit caveat, the gateway-scope authorization
bypass, and how to invoke (`system.db.execQuery` / `execScalar` / `execUpdate`):

- **`named-queries.md`** — the reference doc
- **`schema/named-query/named-query.schema.json`** + `schema/named-query/example/` — the
  machine-readable schema and a minimal valid example

Verified against decompiled `NamedQuery` (8.3.9) + a live write/parse round-trip on
a live gateway (`references/VERIFIED.md`).

---

## 13. Alarm notification pipeline — `com.inductiveautomation.alarm-notification/alarm-pipelines/<Name>/`

A **project** resource, `ResourceType("com.inductiveautomation.alarm-notification",
"alarm-pipelines")` (decompiled `PipelineDescriptor.RESOURCE_TYPE`). `<Name>` is the
folder path and may nest.

| File | Content |
|------|---------|
| `resource.json` | `files:["data.bin"]`; `{"scope":"G","version":1,…}` accepted and run ( — live: throwaway pipeline round-tripped on a live gateway) |
| `data.bin` | the block graph as **Ignition XML object-serialization** (`<objects><o cls="…PipelineDescriptor">…`) — **not JSON**; produced by the platform `XMLSerializer` with the module's serializer delegates, read back with `gatewayContext.createDeserializer()` |

`data.bin` is Java-object XML (class refs, ctor arg-lists, `<ref>` back-references) —
**do not hand-write it.** Build a `PipelineDescriptor` gateway-side and serialize it,
or edit in the Designer. Full block catalog, the flow graph, alarm binding
(`activePipeline`/`clearPipeline`/`ackPipeline`), and the gateway-script authoring +
delete recipe: **`alarm-pipelines.md`** + `schema/alarm-pipeline/`.
