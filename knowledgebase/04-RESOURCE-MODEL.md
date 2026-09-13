> **Core KB:** [00-INDEX](00-INDEX.md) · [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md) · [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

# Project resource model (8.3)

Everything the Designer can create is a **project resource**, and every resource type is
registered in code as a `ResourceType(moduleId, typeName)` pair. Nothing is magic: the
Designer's project browser is driven by this registry, and the on-disk layout mirrors it
exactly.

**Verified on Ignition 8.3.7 (b2026060908)** by decompiling the shipped jars under
`Ignition/lib/core` and `Ignition/data/jar-cache`, and by reading real project folders
under `Ignition/data/projects`. Method is at the bottom so it can be re-run.

---

## 1. The type

```java
com.inductiveautomation.ignition.common.resourcecollection.ResourceType(String moduleId, String typeName)
```

Every module declares its own constants. Example, the SQL Bridge:

```
// com.inductiveautomation.factorysql.common.ModuleMeta
new ResourceType("com.inductiveautomation.sqlbridge", "transaction-groups")
```

On disk that becomes:

```
Ignition/data/projects/<Project>/<moduleId>/<typeName>/<resource path>/
```

So a Perspective view named `Templates/KpiCard` lives at:

```
data/projects/AHU_Control_Demo/com.inductiveautomation.perspective/views/Templates/KpiCard/
    view.json
    resource.json
```

---

## 2. The registry

Complete as of 8.3.7, for the modules installed on this gateway. Each row was read out
of the class that constructs the `ResourceType`.

### Core platform, module id `ignition`

| typeName | Files | Declared in |
|---|---|---|
| `global-props` | `data.bin` | `common.project.GlobalProps` |
| `named-query` | `query.sql`, `data.bin` | `common.db.namedquery.NamedQuery` |
| `script-python` | `code.py` | `common.script.ModuleLibrary` |
| `script-app-library` | - | `common.script.ScriptLibrary` |
| `event-scripts` | - | `common.script.ScriptConfig` |
| `scheduled` | - | `common.script.ScheduledScript` |
| `update` | - | `common.gateway.script.UpdateScriptConfig` |
| `tags` | - | `common.tags.config.model.TagReferenceLocation` |
| `keyboard_layout` | - | `common.i18n.keyboard.KeyboardLayout` |

### Perspective, module id `com.inductiveautomation.perspective`

| typeName | Files | Declared in |
|---|---|---|
| `views` | `view.json`, `data.bin` | `config.ViewConfig` |
| `page-config` | `config.json` | `config.PagesConfig` |
| `session-props` | `props.json` | `config.SessionPropsConfig` |
| `session-permissions` | - | `config.SessionPermissionsConfig` |
| `style-classes` | `style.json`, `data.bin` | `config.styles.StyleClassConfig` |
| `stylesheet` | `stylesheet.css` | `config.StylesheetConfig` |
| `general-properties` | - | `config.PerspectiveProjectProps` |
| `gateway-scripts` | - | `config.PerspectiveGatewayEventsConfig` |
| `form-submission-handler` | - | `config.PerspectiveGatewayEventsConfig$FormSubmissionHandlerScript` |
| `session-scripts` | - | `config.SystemEventsConfig` |
| `startup` | - | `config.SystemEventsConfig` |
| `page-startup` | - | `config.SystemEventsConfig$PageStartupScript` |
| `auth-challenge` | - | `config.SystemEventsConfig$AuthChallengeScript` |
| `key-event` | - | `config.SystemEventsConfig$KeyEventScript` |
| `barcode` | - | `config.SystemEventsConfig$BarcodeScript` |
| `accelerometer` | - | `config.SystemEventsConfig$AccelerometerScript` |
| `bluetooth` | - | `config.SystemEventsConfig$BluetoothScript` |
| `nfc-scan` | - | `config.SystemEventsConfig$NfcScanScript` |
| `inactivity-properties` | - | `config.IdleTimeoutProps` |
| `offline-mode-settings` | - | `config.OfflineModeConfig` |
| `tag-drop-settings` | - | `config.tagdrop.TagDropConfig` |
| `symbol-state-settings` | - | `config.symbols.SymbolPropConfig` |

Perspective has **22 resource types**, not one. "Perspective config" is not a single
blob; each of those is an independently versioned, independently overridable resource.

### Other modules

| moduleId | typeName | Declared in |
|---|---|---|
| `com.inductiveautomation.vision` | `windows` | `factorypmi.common.VisionModule` |
| `com.inductiveautomation.vision` | `general-properties` | `factorypmi.common.VisionModule` |
| `com.inductiveautomation.vision` | `login-properties` | `factorypmi.common.VisionModule` |
| `com.inductiveautomation.vision` | `launch-properties` | `factorypmi.common.VisionModule` |
| `com.inductiveautomation.sqlbridge` | `transaction-groups` | `factorysql.common.ModuleMeta` |
| `com.inductiveautomation.reporting` | `reports` | `reporting.common.resource.ReportResource` |
| `com.inductiveautomation.alarm-notification` | `alarm-pipelines` | `alarming.common.pipelines.PipelineDescriptor` - see [[41-ALARM-PIPELINE-SCHEMA-TRUTH]] for the full bean schema and real block registry |
| `com.inductiveautomation.sfc` | `charts` | `sfc.uimodel.ChartUIModel` |
| `com.inductiveautomation.webdev` | `resources` | `webdev.common.WebDevModule` |
| `com.inductiveautomation.eventstream` | `event-streams` (`config.json`) | `eventstream.EventStreamResource` |

Vision templates are also a resource type; the literal appears in `vision-designer`
rather than in `VisionModule`, so it is listed here without a verified declaring class.

---

## 3. `resource.json`

Every resource folder carries one. This is the real shape, copied from a live project:

```json
{
  "scope": "G",
  "version": 1,
  "restricted": false,
  "overridable": true,
  "files": [ "config.json" ],
  "attributes": {
    "lastModificationSignature": "716d46b4...",
    "lastModification": { "actor": "admin", "timestamp": "2026-08-07T19:18:14Z" }
  }
}
```

| Field | Meaning |
|---|---|
| `scope` | `G` gateway, `C` client, `D` designer, or a combination |
| `version` | resource schema version, per type |
| `restricted` | inheriting projects cannot see it |
| `overridable` | inheriting projects may override it |
| `files` | the payload files that sit beside `resource.json` |
| `attributes.lastModificationSignature` | content hash used for conflict detection |

`lastModification` is sometimes written at the top level rather than under `attributes`.
Both forms are accepted, and hand-written resources with
`"lastModificationSignature": ""` load fine.

**Writing resources by hand works.** Drop the folder in place, keep `files` accurate, and
ask for a project scan. The gateway picks it up. That is the reliable path on this
version, because the `ignition-mcp` project-resource REST endpoints return 404 here.

---

## 4. `project.json`

One per project, at the project root:

```json
{
  "title": "AHU Control Demo",
  "description": "...",
  "enabled": true,
  "inheritable": false,
  "parent": ""
}
```

Inheritance is `parent` plus the per-resource `restricted` / `overridable` flags. There
is no separate inheritance manifest.

---

## 5. Where things actually live on disk

```
Ignition/
  data/
    projects/<Project>/           project resources, as above
    modules/                      installed .modl files
    jar-cache/<moduleId>/         the jars a module actually runs from
    config/<moduleId>/            per-module writable config dir
    gateway.xml, logback.xml      gateway config
    db/                           internal HSQLDB
  lib/core/{common,gateway,client,designer}/    platform jars
  user-lib/modules/               third-party modules
  logs/                           wrapper and gateway logs
```

`data/jar-cache/<moduleId>/` is the copy the gateway loads. Files there are prefixed with
a hash, for example `__2060388498__perspective-common-3.3.7.jar`. When reading platform
truth, read from **jar-cache**, not from the `.modl` in `data/modules`.

---

## 6. How to re-derive this list

The registry is not published as a file, so it is read out of bytecode. No decompiler
needed, `javap` ships with the JDK bundled at
`Ignition/lib/runtime/jre-win` or any JDK 17.

```bash
IG="/c/Program Files/Inductive Automation/Ignition"
JAVAP="/c/Program Files/Eclipse Adoptium/jdk-17.0.20.8-hotspot/bin/javap"

# 1. explode the jars you care about into one directory
mkdir -p mods
for j in "$IG"/data/jar-cache/com.inductiveautomation.*/__*common*.jar; do
  unzip -oq "$j" -d mods
done

# 2. find every class that constructs a ResourceType
grep -rlaF 'resourcecollection/ResourceType' mods

# 3. read the pair out of each one
for f in $(grep -rlaF 'resourcecollection/ResourceType' mods); do
  c=$(echo "$f" | sed 's|^mods/||; s|\.class$||; s|/|.|g')
  echo "### $c"
  "$JAVAP" -p -c -cp mods "$c" 2>/dev/null \
    | grep -B4 'ResourceType."<init>"' | grep -oE '// String .*' | sed 's|// String ||'
done
```

The same trick gives the payload file names: `javap -p -c` the config class and look for
string constants ending in `.json`, `.py`, `.sql`, `.css` or `.bin`.

---

## See Also

- [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
- [16-PERSPECTIVE-SCHEMA-TRUTH](16-PERSPECTIVE-SCHEMA-TRUTH.md) - the Perspective side, in detail
- [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md) - named queries
- [28-PLATFORM-TRANSACTIONS-SFCS](28-PLATFORM-TRANSACTIONS-SFCS.md) - transaction groups and charts

[↑ Back to KB INDEX](00-INDEX.md)
