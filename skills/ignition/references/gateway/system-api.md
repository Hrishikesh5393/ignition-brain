# The `system.*` Scripting API

> **See also:** `references/ignition-8-3/scripting-core.md`, `scripting-ui.md`, `scripting-platform.md`, `scripting-connectivity.md` [M] — a current official-docs catalog of `system.*` categories and functions (359 entries) to cross-check against this file's reflection-and-decompile-verified `schema/system-api.json`, especially for a function this file's own coverage stats mark `types_only` (unrecoverable param names).

How to use `schema/system-api.json` to get a **real, complete** `system.*` signature —
parameter names, defaults, keyword-arg support, documentation, return text, module
gating and scope — plus how to recover anything the schema still doesn't have. All
`system.*` scripting is **Jython 2.7.4** (gateway JVM 17) — see
`references/standards/jython.md` for runtime constraints.

---

## The two files

| File | What it is | Edit? |
|------|-----------|-------|
| `system-api.raw.json` (kept by the driver repo, outside the skill payload — regenerate, don't read) | The **immutable** live-gateway reflection dump — 969 entries, `<subpkg>.<fn>` → `{overloads: [[javaType, …]], doc}`. Ground truth for *what exists*. Extracted from an 8.3.9 gateway. | never by hand — re-dump from a live reflection walk |
| `schema/system-api.json` (relative to this skill, i.e. `skill/schema/system-api.json`) | The **enriched** reference, regenerated from the raw dump by `<repo>/scripts/enrich_system_api.py`: full signatures + param names + defaults + docstrings recovered from the decompiled `@KeywordArgs` / `@ScriptArg` annotations and the i18n `.properties` doc bundles. Lives inside the skill tree so the skill is self-contained — a copy of this file must ship with the skill wherever it's installed. | never by hand — re-run the extractor |
| `schema/system-api-coverage.json` (relative to this skill, i.e. `skill/schema/system-api-coverage.json`) | Per-subpackage coverage stats + the exact list of the types-only tail. | regenerated with the schema |

Re-generate after a gateway upgrade: refresh `system-api.raw.json` from a reflection
walk, refresh the jar decompile (`<decompiled-jars>/`), then
`python3 scripts/enrich_system_api.py`. It is idempotent (always reads the raw dump).

---

## Enriched entry shape

```json
"tag": {
  "readBlocking": {
    "doc": "Reads the value of the tags at the given tag paths. This function will block until the read operation is complete or times out.",
    "returns": "A list of qualified values corresponding to the tag paths. Each qualified value has three sub-members: value, quality, and timestamp.",
    "module": "platform",
    "scopes": ["gateway", "designer", "client", "perspective-session", "vision-client"],
    "paramSource": "annotation",
    "overloads": [
      {
        "kwargs": true,
        "params": [
          { "name": "tagPaths", "type": "List",    "optional": true,
            "doc": "A list of tag paths to read from. If no property is specified in a tag path, the Value property is assumed." },
          { "name": "timeout",  "type": "Integer", "optional": true, "default": "45000",
            "doc": "How long to wait (in milliseconds) before the read operation times out." }
        ]
      }
    ]
  }
}
```

⇒ **`system.tag.readBlocking(tagPaths, timeout=45000)`** → `list[QualifiedValue]`
(`.value`, `.quality`, `.timestamp`).

| Field | Meaning |
|-------|---------|
| `doc` / `returns` | prose from the i18n doc bundle (`<fn>.desc` / `<fn>.returns`). `null` when the bundle has no entry. |
| `module` | the module that must be installed for the namespace to exist (`"platform"` = always). |
| `scopes` | where the namespace is mounted — `gateway` / `designer` / `client` / `perspective-session` / `vision-client`. |
| `overloads[].kwargs: true` | the function takes **keyword arguments** — call it `fn(name=value, …)`. Its Java signature is the `(PyObject[], String[])` dispatch shim; the real names are in `params`. |
| `overloads[].params[]` | `{name, type, optional, default?, doc?, keywordOnly?}`. `name` is **absent** when no annotation/bundle names that positional arg — then only `type` is given. |
| `paramSource` | provenance of the params — see below. |
| `deprecated: true` | the decompiled method (or its doc bundle) carries `@Deprecated`. Still callable; prefer the replacement. |
| `kind: "constant"` | not a function — a module constant / enum field (`system.db.BIGINT`, `system.date.MONDAY`, `system.file.UTF_8`). `overloads` is `[]`. |

### `paramSource` values

| value | meaning | trust |
|-------|---------|-------|
| `annotation` | params from a decompiled `@KeywordArgs` / `@ScriptArg` — names, types, optionality exact | ✅ authoritative |
| `bundle` | params from a doc-bundle `<fn>.param.*` key order (no annotation was available — module not in the decompile set: `dnp3`, `iec61850`, `opchda`) | ✅ names right, order is the bundle's |
| `no_args` | the function takes no arguments | ✅ |
| `constant` | module constant, not callable | ✅ |
| `types_only` | **no source names this function's params** — only the reflected Java types are given | ⚠️ names unknown — do not guess |

---

## Coverage (8.3.9, regenerated 2026-09-04)

`system-api.raw.json` holds 969 reflected entries. 373 are Java/PyObject members the
walk leaked in (`clear`, `getClass`, `toString`, `.name`, and the whole
`dict` / `getName` / `system` pseudo-subpackages) — excluded. That leaves **596 real
`system.*` names**:

| | count | with param names | with docstring |
|---|---:|---:|---:|
| **callable functions** | **451** | **377** (84%) + 35 no-arg = **412 fully resolved** | 445 |
| module constants / enum fields | 145 | — | (many) |

377 param-resolved = 350 from decompiled annotations + 27 from doc bundles only. The
**39-function types-only tail** (listed in `system-api-coverage.json →
by_subpackage.<sub>.types_only_functions`) is genuinely unrecoverable from our
sources, not withheld:

- `*Internal` helpers — `historian.queryMetadataInternal`, `util.sendMessageInternal`, `device.addDeviceInternal`, …
- legacy Vision-scope tag calls — `tag.getTagValue`, `tag.writeToTag`, `tag.*ManagedTag*` (no `@ScriptArg`, no bundle key)
- deprecated converters — `db.toDataSet`, `dataset.dataSetToCSV`, `db.dateFormat`
- Java-overload-only methods Ignition never script-annotated — `dataset.insertRow` / `insertColumn` / `removeRow` / `toJSONObject` (positional types kept, names absent)

Per-subpackage numbers are in `system-api-coverage.json`. The reconciliation against a
live `system.*` reflection walk (2026-09-04) found **every** live callable represented
— 0 missing.

### `system.gui` / `system.nav` / `system.vision`

Not in the schema. `system.gui.*` and `system.nav.*` were the Vision-client window/
navigation namespaces; in 8.3 they are unified as **`system.vision.*`**, which is
**Vision-client scope only** and absent from the gateway reflection dump the schema is
built from. Their signatures live in the `WindowUtilities` / `NavUtilities` /
`VisionUtilities` doc bundles (inside `vision-*.jar`) if a Vision task needs them.

---

## Worked example — `system.perspective.navigate`

**1. Look it up** in `schema/system-api.json`:

```json
"perspective": { "navigate": {
  "doc": "Navigate to a page, view, or any external URL...",
  "module": "Perspective",
  "scopes": ["gateway", "perspective-session"],
  "paramSource": "annotation",
  "overloads": [ { "kwargs": true, "params": [
    { "name": "page",      "type": "String",       "optional": true, "doc": "The URL of the page to navigate to." },
    { "name": "url",       "type": "String",       "optional": true, "doc": "... Not to be used simultaneously with 'view'" },
    { "name": "view",      "type": "String",       "optional": true, "doc": "... Not to be used simultaneously with 'url'" },
    { "name": "params",    "type": "PyDictionary",  "optional": true, "doc": "Dictionary of key-value pairs to use as input parameters to the target view." },
    { "name": "sessionId", "type": "String",       "optional": true },
    { "name": "pageId",    "type": "String",       "optional": true },
    { "name": "newTab",    "type": "Boolean",      "optional": true, "doc": "Open contents in a new tab." }
  ] } ]
} }
```

⇒ keyword-arg function, scopes tell you it runs in a **Perspective session** (or from
the gateway if you pass `sessionId` + `pageId`):

```python
system.perspective.navigate(page="/orders/detail", params={"orderId": 42})
```

**2. Cross-check the runtime** when in doubt (module gating, an overload the static
extract missed) — `run_gateway_script` (gateway scope):

```python
import system
result = "navigate" in dir(system.perspective)
```

---

## Recovering / extending what the schema still lacks

The extractor (`<repo>/scripts/enrich_system_api.py`) already parses these; reach for them
directly only for the `types_only` tail or a namespace added by a newer module.

| Source | Location | Carries |
|--------|----------|---------|
| decompiled `*ScriptModule` / `*Utilities` | `<decompiled-jars>/` | `@SystemLibrary(mountPath=…)`, `@KeywordArgs(names=…, types=…)`, `@ScriptArg(value=…, optional=…)`, `@Deprecated`, `@NoHint` |
| i18n doc bundles | `*.properties` inside `lib/core/{common,gateway,client}/*.jar` and each module's `*.jar` | `<fn>.desc`, `<fn>.param.<name>`, `<fn>.param.<name>.default`, `<fn>.returns` — the prose |
| the module hook | same decompiled tree | `manager.addScriptModule("system.<x>", new <Class>())` — the mount for a class with no `@SystemLibrary` (Kotlin modules: `system.dnp`, `system.opcua`) |
| the live gateway | `run_gateway_script` | ground truth for existence, arity, module gating; catches anything static extraction missed |

**Deriving a signature with no decompile source at all:** modules that expose
`system.*` functions ship a `*PyWrapper` class (e.g. `ReportScriptingFunctionsPyWrapper`)
whose bytecode embeds the real parameter names as string literals right where each
Jython-callable method builds its `PyObject[]` args. `javap -p -c` on that class shows
them inline (`// String path`, `// String project`, …), giving a real signature with no
shipped stubs and no annotation source. Useful for re-deriving a `types_only` entry or
checking a signature you suspect is wrong, when the module isn't in the decompile set at
all. Method: `references/gateway/notes/verification.md`.

Grep example — the real signature of a tail function:

```bash
grep -n -B2 "writeToTag" \
  <decompiled-jars>/common/com/inductiveautomation/ignition/common/script/builtin/LegacyTagUtilities.java
```

---

## Call-pattern notes

- **Scope** — `run_gateway_script` runs in **gateway** scope. Namespaces with
  `gateway` in `scopes` work there; `vision-client`-only namespaces
  (`system.vision.*`) and session-bound Perspective calls
  (`navigate` / `openPopup` without `sessionId`+`pageId`) do not.
- Prefer the **`*Blocking`** tag calls (`readBlocking` / `writeBlocking`) — the async
  `read` / `write` forms need a callback and are awkward from a one-shot script.
- `system.tag.configure(basePath, tags, collisionPolicy)` with `collisionPolicy="o"`
  (overwrite) / `"m"` (merge) / `"a"` (abort) is the proven way to create tags & UDT
  types (`mcp-tool-map.md` — the MCP `create_tags` tool is broken on 8.3.9).
- `system.db.runNamedQuery` is `deprecated: true` in 8.3 (still present) — the entry
  records the `@Deprecated(since="8.3.0")` on the decompiled method.
- Jython 2.7: no f-strings, `print` is a statement, `except Exception, e:` old syntax
  tolerated, catch Java exceptions with a bare `except:` + `sys.exc_info()`.
