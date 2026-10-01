# Ignition Named Queries

> **See also:** `references/gateway/deep/udt-and-named-query-internals.md` (Part 2 of that file) — Named Query concepts, use cases, and SQL-composition examples (JOINs, aggregation, window functions). Part 1 of the same file covers UDT design instead (see `standards/udt-design.md`). `references/ignition-8-3/security-and-databases.md` [M] also covers Named Queries at the current official-docs level.

The on-disk format of an Ignition 8.3 **Named Query** project resource, the three query
types, parameter typing, `:name` / `{name}` substitution, caching, authorization, and how
to invoke one from scripting. Target gateway **8.3.9** ( — live `get_gateway_info`
2026-09-04, `8.3.9 (b2026082511)`, standard edition).

Machine-readable schema + a minimal example: **`schema/named-query/`**
(`named-query.schema.json`, `example/`). Every field below is verified against decompiled
`com.inductiveautomation.ignition.common.db.namedquery.NamedQuery` (8.3.9) and a live
write → `requestScan()` → `NamedQuery.fromResource()` round-trip on a live
8.3.9 gateway (`references/VERIFIED.md`). Named
Queries are never edited by hand — write them gateway-side through `ignition-mcp` and
scan (`resource-formats.md` §10–11), then verify at runtime.

---

## 1. On-disk layout

```
<install>/data/projects/<project>/ignition/named-query/<name>/
  query.sql        REQUIRED — raw SQL text, exactly as typed in the Designer editor
  resource.json    REQUIRED — the manifest (§3)
```

- `ResourceType` = `("ignition", "named-query")` — `NamedQuery.RESOURCE_TYPE`.
- `<name>` may contain `/` for folders — `ignition/named-query/reports/DailyProduction/`.
- The **query file key is `query.sql`** (`NamedQuery.ResourceKeys.QUERY_FILE`), written via
  `builder.putData("query.sql", …)`. `resource.json` `files` = `["query.sql"]`.
- `scope` is `"G"` (gateway; Designer-created queries are `"DG"` live — both load), `version` is **`2`** (`NamedQuery.CURRENT_RESOURCE_VERSION`).
  Version `1` is the legacy pre-8.x form — an XML-serialized blob in `data.bin`, no
  `query.sql`. `fromResource()` still reads v1; **never author it** — always write v2
  (`toResource()` sets version 2 and calls `removeData("data.bin")`).

( — live 2026-09-04: hand-written `ignition/named-query/probe/{query.sql,resource.json}`
in a test project parsed cleanly; `resource.getData("query.sql")` returned the SQL verbatim,
`getVersion()` = 2.)

---

## 2. The three query types (`attributes.type`)

`NamedQuery.Type` enum — the attribute stores the **enum name**, not the i18n label.

| `type` | Returns | Invoke with | Cacheable? | Fallback? | Notes |
|--------|---------|-------------|:----------:|:---------:|-------|
| `Query` | `Dataset` (all rows) | `system.db.execQuery` | yes | no | `connection.runPrepQuery` / `runPrepLimitQuery`. Row cap (`maxReturnSize`) applies **Designer-only** — see §6. |
| `ScalarQuery` | single value — row 0, col 0 | `system.db.execScalar` | yes | **yes** | `runPrepLimitQuery(q, 1, args)`. Zero rows → `fallbackValue` if `fallbackEnabled`, else `null`. |
| `UpdateQuery` | affected-row count (`Integer`), or generated key (`Long`) when `getKey=True` | `system.db.execUpdate` / `execUpdateAsync` | **no** | no | `runPrepUpdate` / `runPrepInsertGetKey`. The only type allowed through store-and-forward. |

The Designer's type dropdown shows localized labels (`BundleUtil.i18n("NamedQuery.Type.<name>")`);
the value written to `attributes.type` is always the bare enum name above.

**Type guard:** `execQuery` / `execScalar` / `execUpdate` inject
`params["__EXPECTED_QUERY_TYPE"]`; `GatewayNamedQueryManager.validateQueryTypeParameter()`
raises `IllegalArgumentException: Query type mismatch` if the resource's `type` differs.
Call the function that matches `attributes.type`.

---

## 3. `resource.json` — `attributes`

Every key is written by `NamedQuery.toResource(...)`; `fromResource(...)` reads each with
`.ifPresent(...)`, so any key may be omitted and falls back to the default shown.

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `type` | string | *(none — required)* | `Query` \| `ScalarQuery` \| `UpdateQuery`. A missing `type` leaves the field `null` and the query fails to run. |
| `database` | string | `""` | Datasource name. `""` = project default datasource. `"{}"` = caller **must** pass a `database` parameter at execution. Else = that exact connection. |
| `enabled` | bool | `true` | `false` → `execute()` throws "Named Query cannot be executed when disabled." |
| `cacheEnabled` | bool | `false` | Query-level result cache (§7). **Key is `cacheEnabled`** though the class field is `cachingEnabled`. |
| `cacheAmount` | int | `1` | TTL magnitude. |
| `cacheUnit` | string | `"SEC"` | `TimeUnits` name: `MS SEC MIN HOUR DAY WEEK MONTH YEAR`. TTL = `cacheAmount × cacheUnit`. |
| `useMaxReturnSize` | bool | `false` | Cap `Query` row count at `maxReturnSize` — **only when `canLimit=true`, which is Designer-only** (§6). |
| `maxReturnSize` | long | `100` | The row cap (see caveat §6). |
| `fallbackEnabled` | bool | `false` | `ScalarQuery` only: return `fallbackValue` on error / zero rows. |
| `fallbackValue` | string | *(key omitted when null)* | The scalar fallback. |
| `autoBatchEnabled` | bool | `false` | Store-and-forward auto-batching hint for `execUpdateAsync` / `runSFNamedQuery`. |
| `syntaxProvider` | string | *(key omitted when null)* | Optional DB-syntax / translator override key. |
| `parameters` | array | *(key omitted when empty)* | Declared parameters (§4). |
| `permissions` | array | *(key omitted when empty / only-empty-requirement)* | Authorization (§8). **Never write `[]`** (§8, §Smells). |

**Description quirk:** the query's description is written to the **top-level
`documentation`** key of `resource.json` (`builder.setDocumentation(...)`), *not* an
attribute. But `fromResource()` v2 reads an *attribute* named `description` — so the
description does **not** round-trip back into the in-memory `NamedQuery` (confirmed live:
`getDescription()` → `None`, `getDocumentation()` populated). Put it in `documentation`;
do not also add a `description` attribute.

Minimal valid manifest ( — `schema/named-query/example/resource.json`):

```json
{ "scope": "G", "version": 2, "restricted": false, "overridable": true,
  "files": ["query.sql"],
  "attributes": { "type": "Query", "enabled": true } }
```

---

## 4. Parameter typing (`attributes.parameters[]`)

Each entry is `{ "type": <ParameterType>, "identifier": <name>, "sqlType": <int> }`
(serialized by `NamedQuery.Parameter.GsonAdapter`).

**`type`** — `NamedQuery.ParameterType`:

| `type` | Token in `query.sql` | Substitution | Use for |
|--------|----------------------|--------------|---------|
| `Parameter` | `:identifier` | replaced with a JDBC `?`, value bound as a prepared-statement arg (**safe**). Designer UI labels this **"Value"**. | every user-supplied value |
| `QueryString` | `{identifier}` | `TypeUtilities.toString(value)` **spliced into the SQL text literally** — *not* parameterised. | trusted structural fragments only (a sort column, a schema name). **SQL-injection surface.** |
| `Database` | *(none)* | the special `database` selector; only valid when `attributes.database == "{}"` | choosing the connection at call time |

**`identifier`** — must match `[\p{L}\p{N}\-_]+` and must **not** be `database`
(case-insensitive) — `NamedQuery.isValidParamName()`.

**`sqlType`** — the `DataType` enum **int** value. Allowed set
(`NamedQuery.PARAMETER_TYPES`); the value is coerced to this type
(`TypeUtilities.coerceNullSafe`) before binding:

| int | DataType | Java |
|----:|----------|------|
| 0 | `Int1` | `Byte` |
| 1 | `Int2` | `Short` |
| 2 | `Int4` | `Integer` |
| 3 | `Int8` | `Long` |
| 4 | `Float4` | `Float` |
| 5 | `Float8` | `Double` |
| 6 | `Boolean` | `Boolean` |
| 7 | `String` | `String` |
| 8 | `DateTime` | `java.util.Date` |
| 20 | `ByteArray` | `byte[]` |

( — live: `{id: Int4=2}`, `{maxRows: Int8=3}`, `{colName: QueryString/String=7}` written
and read back unchanged.)

---

## 5. `:name` / `{name}` substitution in `query.sql`

`QueryParser` token regex: `(\{[\p{L}\p{N}\-_]+\})|(\:[\p{L}\p{N}\-_]+)`.

- `:name` → replaced with a single `?` (`StringUtils.replaceOnce`) and the value appended
  to the JDBC arg list, **in first-appearance order**. Each occurrence of `:name`
  produces its own `?` and its own arg (repeat the token to bind the value twice).
- `{name}` → **every** occurrence replaced with the stringified value, spliced in. An
  empty / blank value raises `NamedQuery.Parser.MissingQueryStringValue`.
- A token only substitutes if a parameter of the **same `ParameterType`** is declared
  with that identifier (`parseAndRebuild` `paramTypeLookup` check). An undeclared `:foo`
  is left in the SQL and the driver will choke.

```sql
SELECT batch_id, good_count, reject_count
FROM   batch_history
WHERE  line_id = :lineId          -- Parameter  (Int4)  -> ?
  AND  finished >= :since          -- Parameter  (DateTime) -> ?
ORDER  BY {sortCol} DESC           -- QueryString (String) -> spliced, trusted only
```

---

## 6. Row limiting — Designer-only

`useMaxReturnSize` / `maxReturnSize` only take effect when the caller passes
`canLimit=true`. The **only** caller that does is the Perspective / Vision query binding
**running inside the Designer** (`DirectQueryBinding`: `designerUseLimit && isDesigner`;
Vision RPC: designer branch passes `canLimit=true`). At runtime — and from **all**
scripting (`execQuery` / `runNamedQuery` pass `canLimit=false`) — the cap is **not
applied**. It is a Designer preview guard, nothing more.

**For a real runtime cap, write it into the SQL** (`TOP`, `LIMIT`, `FETCH FIRST … ROWS`).

---

## 7. Caching

When `cacheEnabled` is `true`, the caller allows caching (`canCache`), and `type !=
UpdateQuery`, the result is cached for `cacheAmount × cacheUnit`. The cache key is
`hash(bound args) · query text · datasource name · resourceId` — so different parameter
values cache independently, and editing the query or its resource invalidates it
(`resourcesUpdated` → `clearCacheForResource`).

- `execQuery` / `execScalar` / `runNamedQuery` pass `canCache=true` → the query cache is
  consulted.
- The Designer passes `canCache=false` → always a fresh hit while you edit.
- The Perspective **binding** value cache (`enableValueCache` on the binding) is a
  *separate*, runtime-only (`!isDesigner`) layer in front of this.
- Clear manually: `system.db.clearNamedQueryCache([project,] path)` /
  `system.db.clearAllNamedQueryCaches([project])`.

Cache only idempotent, slow-changing reads. Never cache a query whose caller expects
live data every poll.

---

## 8. Authorization (`attributes.permissions[]`)

Each entry is a `ZoneRoleRequirement`: `{ "zone": <name|null>, "role": <name|null> }`.
Access is **GRANTED if *any* requirement matches** the caller's roles + zones (OR
semantics — `SecuredNamedQueryManager.authorized()`). A blank `role` or `zone` in a
requirement is skipped; a requirement with both blank = "allow everyone" (the default
when `permissions` is absent).

**Where it is enforced:**

| Caller | Enforced? | How |
|--------|:---------:|-----|
| Perspective **query binding** | **yes** | the session's `SecuredNamedQueryManager` — `QueryBindingParams` carries the session roles + zones |
| Vision client (query binding, and client-scope `system.db.*` via RPC) | **yes** | `NamedQueryRpcImpl.hasPermissions` vs the client session's `authUser` |
| Designer | n/a | always allowed (`session.isDesigner()`) |
| **Any `system.db.exec*` / `runNamedQuery` script call** — gateway timer, tag-change, message handler, WebDev, **and Perspective event scripts / transforms** | **NO** | `GatewayDBUtilities._execNamedQuery()` calls `context.getNamedQueryManager()` (the raw `GatewayNamedQueryManager`) directly — it never consults the `SecuredNamedQueryManager` wrapper, even when a session `SecurityContext` is on the thread |

So `permissions` guards the **declarative query binding**, not scripted execution. A
Perspective button script that calls `system.db.execScalar(...)` runs the query with no
permission check. If a query must never run for some users, it also must not be reachable
from a script path.

Cross-reference the project's role set (its gateway profile) and the
model in `references/standards/security-roles.md`.

---

## 9. Invoking a Named Query

`path` = the resource folder path under `ignition/named-query/`, **without** that prefix
and **without** the project name. Resource dir
`ignition/named-query/reports/DailyProduction/` → `path` = `"reports/DailyProduction"`.

**Modern (8.3):**

```python
ds  = system.db.execQuery("reports/DailyProduction", {"lineId": 3})           # Query   -> Dataset
val = system.db.execScalar("kpi/OeeNow", {"lineId": 3})                        # Scalar  -> value
n   = system.db.execUpdate("batch/CloseBatch", {"batchId": 88})               # Update  -> row count
key = system.db.execUpdate("batch/OpenBatch", {"line": 3}, getKey=True)       # Update  -> generated key
ok  = system.db.execUpdateAsync("audit/Log", {"msg": "x"})                     # Update  -> store-and-forward
```

Signatures ( — decompiled `AbstractDBUtilities`, keyword order):
`execQuery(path, parameters, tx=None, project=None)`,
`execScalar(path, parameters, tx=None, project=None)`,
`execUpdate(path, parameters, tx=None, getKey=False, project=None)`,
`execUpdateAsync(path, parameters, project=None)`.

**Deprecated since 8.3 but still present:** `system.db.runNamedQuery`,
`runSFNamedQuery`, `clearNamedQueryCache`, `clearAllNamedQueryCaches`. Note
`runNamedQuery` takes **`project` as its first positional arg** —
`runNamedQuery([project,] path, parameters, tx=None, getKey=False)` — unlike `execQuery`
where `path` is first. Prefer the `exec*` functions.

**Parameter set must match exactly.** `execQuery` / `execScalar` / `execUpdate` call
`validateQueryParameters(required, provided)` — the keys of your `parameters` dict must
**equal** the declared identifier set. A missing or extra key raises
`ValueError: Parameter mismatch`. When `database == "{}"`, a `database` key is
additionally required.

Full `system.*` guidance: **`system-api.md`** (backed by `schema/system-api.json`).

Gateway-side write + verify loop: **`resource-formats.md`** §10–11, **`workflow.md`**.

---

## agent rules

1. **Write `version: 2`, `scope: "G"`, `files: ["query.sql"]`** — never the legacy v1
   `data.bin` form.
2. **`type` must be present** and must match the `exec*` function you call
   (`Query`→`execQuery`, `ScalarQuery`→`execScalar`, `UpdateQuery`→`execUpdate`) or the
   type guard rejects it.
3. **User input → `Parameter` (`:name`)**, never `QueryString` (`{name}`). Reserve
   `{name}` for trusted structural fragments and say so in the description.
4. **`sqlType` is the `DataType` *int*** (String = 7, Int4 = 2, DateTime = 8, …), from
   the allowed set of 10. Not a type name.
5. **Description goes in top-level `documentation`**, not an attribute.
6. **Row cap belongs in the SQL** (`FETCH FIRST … ROWS` / `LIMIT` / `TOP`) —
   `maxReturnSize` only limits in the Designer.
7. **`permissions` only guards the declarative query binding** — Perspective/Vision.
   Any `system.db.exec*` script call (including in a Perspective transform) runs the
   query unchecked. Design access assuming a script route can reach it.
8. Never write `"permissions": []` — omit the key. An explicit empty array denies every
   non-Designer Vision user (`NamedQueryRpcImpl.hasPermissions`).
9. Cache (`cacheEnabled`) only slow-changing, idempotent reads; never `UpdateQuery`
   (silently ignored) and never a "must be live" poll.
10. `flush()` + `os.fsync()` on `query.sql` **before** `resource.json`; then
    `requestScan()`; then verify with `NamedQuery.fromResource(resource, deser)` or an
    actual `system.db.execQuery` — not an HTTP 200.

## Smells

- `sqlType: "String"` / `"Int4"` in a parameter — must be the **int** (`7`, `2`).
- `{orderBy}` fed straight from a Perspective input prop — injection; that must be a
  whitelisted `Parameter`, or validated before the call.
- A `"description"` key inside `attributes` — it is read on load but never written there;
  the real home is `documentation`.
- `useMaxReturnSize: true` used as the runtime row limit — it does nothing outside the
  Designer.
- `cacheEnabled: true` on an `UpdateQuery`, or on a dashboard tile that must refresh
  every few seconds.
- Relying on `permissions` to stop a script (`system.db.exec*`) — gateway or Perspective
  transform — from running a sensitive query. It only gates the query binding.
- `system.db.runNamedQuery("reports/Daily", {...})` — first arg is treated as the
  *project* name; use `execQuery`, or pass `path=`/`project=` explicitly.
- `"permissions": []` written to "clear" permissions — locks out Vision users instead.
- Authoring `data.bin` / `version: 1` by copying an old 7.x export.
