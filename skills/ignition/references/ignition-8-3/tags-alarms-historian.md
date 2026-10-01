# Ignition 8.3 — Tags, alarming and the historian

A dense developer reference distilled from the live 8.3 Ignition User Manual (`docs.inductiveautomation.com/docs/8.3/...`), covering the tag system, UDTs, tag scripting, the Historian, alarming, and alarm notification.

---

## Tag system model

### What a tag is

A tag is a point of data with a static or dynamic value (OPC address, expression, or SQL query). Tags are configured in the Designer (Tag Browser / Tag Editor) and organized under Tag Providers, which are configured on the Gateway and apply globally across all projects on that Gateway.

Tag configuration on disk is split by resource type, under `/data/config/core/ignition/`:

| Resource | Path |
|---|---|
| Atomic tags | `tag-definition/<provider>/<path to folder>/tags.json` |
| UDT instances | `tag-definition/<provider>/<path to folder>/udts.json` |
| UDT definitions | `tag-type-definition/<provider>/<path to folder>/udts.json` |

**Tag naming rules**: first character must be a Unicode Letter, a digit, or underscore. Subsequent characters may additionally include spaces and the special characters `' - : ( )`. No other special characters are allowed. Max length 256 characters.

### Tag Providers (realtime vs. historical)

A **Tag Provider** is a named tag database. Every Gateway can host multiple providers; each can be secured or disabled independently. Providers hold *realtime* values; a separate concept, **Tag Historian Providers**, stores historical values, and each tag can independently target a historian provider for its history.

Realtime provider types:

| Type | Description |
|---|---|
| **Standard** | Tags are stored and executed entirely on the local Gateway (reads, writes, history, alarms). Every fresh install creates a Standard provider named `default`. |
| **Remote** | A link to a Tag Provider on another Gateway over the Gateway Network. Local Ignition may read/write, but execution (PLC writes, alarms, history) happens on the *remote* Gateway. Falls under the Default Security Zone and is read-only by default. Annotations to remote Gateways are **not supported** via Remote Tag Providers — use a Remote Historian provider instead. |
| **Managed** | System-created only; the built-in **System Tag Provider** (Client/Gateway system tags) is the only example. Cannot be created or deleted by users; the only editable setting is enabling/disabling the Tag Reference Tracker Store. |

Key Standard Tag Provider settings: `Default Datasource` (for Query tags with default DB selected), `Value Persistence` (None / Database / Configuration — governs whether Memory tag writes survive a Gateway restart), `Tag Read/Write/Editing Permissions` (security-level paths, AnyOf/AllOf), `Read Only`, `Allow Back-fill Data` (lets data arrive out of order — stored to history but *not* used for alarms/scripts/subscriptions), `Enable Tag Reference Tracker Store`.

Key Remote Tag Provider settings: `Gateway`, `Provider` (remote provider name — need not match locally), `History Access Mode` (**GatewayNetwork**: remote Gateway queries and processes, then ships results over the network; **Database**: requesting Gateway queries the DB directly), `History Datasource`/`History Driver`/`History Provider` (used only when History Access Mode = Database), `Alarms Enabled`, `Alarm Mode` (**Queried** vs **Subscribed** — subscribed gives better performance at the cost of memory).

> ⚠️ Naming a Tag Provider the same as a database connection is **not recommended** — can cause tag data queries to silently return nothing.

### Tag types (Value Source)

| Tag type | Behavior |
|---|---|
| **OPC** | Driven by an OPC Item Path + OPC server; polled/subscribed per its Tag Group. |
| **Memory** | Static until written by script/binding. Governed by `Value Persistence` (falls back to Provider setting unless overridden per-tag). |
| **Expression** | Value from an expression; can reference other Gateway-scoped tags but *not* Vision/Perspective component properties (scoping). Execution governed by `Execution Mode`. |
| **Query** | Executes a SQL query; result becomes the value. `Query Type` = AutoDetect / Select / Update (Update tags report affected-row count as their value). `Datasource` selects the DB connection. |
| **Reference** | Points at another tag via `Source Tag Path`; writes pass through to the source unmodified. |
| **Derived** | Like Reference, but with a `Read Expression` (applies to the value coming *from* the source, referencing `{source}`) and a `Write Expression` (applies to values being written *to* the source, referencing `{source}` and `{value}`). `Preserve Source Timestamp` controls whether the derived value keeps the source's timestamp or gets a fresh one. The `SourceTagPath` can be changed live via script or binding. |
| **UDT Instance** | A running structure inheriting from a UDT Definition (see UDTs section). |

`Tag Object Type` (`tagType` — visible to `system.tag.browse` etc.): `Property`, `Node`, `Folder`, `AtomicTag`, `UdtInstance`, `UdtType`, `Provider`.

### Tag paths — the `[provider]Folder/Tag` syntax

Canonical form: `[Tag Provider]folder/path/tag.property`. The bracketed provider selector accepts:

| Selector | Meaning |
|---|---|
| `[Tag Provider Name]` | Explicit named provider. |
| `[]` or omitted | The current project's default Tag Provider. In Gateway scope this is usually **invalid** — the Gateway has no notion of a project default. |
| `[.]` | **Relative** to the folder of the tag being bound — invaluable inside UDT definitions so instances stay portable across moves. Use `..` to step up a folder, e.g. `[.]../../tag`. |
| `[~]` | Relative to the **Tag Provider root** of the tag being bound — survives provider renames and cross-provider import/export/move. |
| `[Client]` | The Vision Client Tag Provider (Vision Client tags only). |
| `[System]` | The System tag provider. |

Omitting `.property` implies `.value`. Array elements: `[default]Folder/myArrayTag[0]`. Document-type tag members: `[default]myDocumentTag['key[0]']` (array index inside the key) or dotted JSON traversal, e.g. `[default]myDocumentTag['sub-object.deep-object.key']` — writable the same way via a bidirectional binding.

**Historical tag paths** use a different, colon-delimited syntax consumed by Power Chart, Tag Browse Tree, and `system.historian.*`:
```
histprov:test:/sys:myGateway:/prov:default:/tag:_Simulator_/Ramp/Ramp0
```

**Dynamic path construction** — because paths are plain strings, they can be assembled programmatically:
```python title="Python Dynamic Tag Path"
tankNumber = 2
tagPath = "[default]Tanks/Tank %i/Level" % tankNumber
```
```js title="Expression Dynamic Tag Path"
tag("[default]Tanks/Tank "+{[.]tankNumber}+"/Level")
```

**The `{this}` keyword**: refers to the tag itself, usable in an expression configured on one of that tag's own properties — `{this.name}` always returns the *tag's* name. Note that inside an **alarm** property expression, `{this}` still resolves to the host **tag**, not the alarm (`this.name` on an alarm gives the tag's name).

**Wildcards** (glob-style) are accepted specifically in Gateway Event Tag Change Script paths and the Event Streams Tag Event source — see the Gotchas section for the full 8.3.4 wildcard operator table.

### Data types

Scalars: `Int1`(Byte,0) `Int2`(Short,1) `Int4`(Integer,2) `Int8`(Long,3) `Float4`(Float,4) `Float8`(Double,5) `Boolean`(6) `String`(7) `DateTime`(8) `Text`(10, deprecated).
Array variants exist for most scalars (`Int1Array` 17, `Int2Array` 18, `Int4Array` 11, `Int8Array` 12, `Float4Array` 19, `Float8Array` 13, `BooleanArray` 14, `StringArray` 15, `DateTimeArray` 16). Plus `ByteArray` (Binary Data, 20), `DataSet` (9), `Document` (29).

- **Array tags**: config for alarming/history/scaling propagates down to elements. OPC write-back to arrays may require writing the whole array if the OPC server doesn't support per-element writes.
- **Dataset tags**: multiple rows/columns in a single tag; each column appears as a subfolder. Valid column types: Float, Short, Long, Date, Integer, Boolean, String, Color, Double, Timestamp, Byte Array. **Tag History and Alarming do not support Dataset tags.**
- **Document tags**: JSON-document-valued tags, edited via a JSON editor; accepts/coerces Python dictionaries. **Also unsupported by History and by most OPC servers** — best used on Query/Memory tags.

### Tag properties (complete reference)

**Basic**: `name`, `tagGroup` (execution rate/conditions — see Tag Groups), `enabled` (disabled tags keep existing but return no value/bad quality).

**Value**: `tagType` (read-only, scripting-only), `typeId` (UDT parent path — shown as *Parent Data Type* in the editor), `valueSource` (`derived`/`expr`/`memory`/`opc`/`db`/`reference`), `dataType`, `defaultValue` (Memory tags only — used on first creation and whenever Value Persistence = None), `value`, `valuePersistence` (per-tag override of the Provider setting), `opcServer`, `opcItemPath` (supports escaping `{` `}` via doubling, e.g. `{{device_name}}`), `sourceTagPath` (Derived/Reference), `executionMode` (`EventDriven` default / `FixedRate` (+`Execution Rate` ms) / `TagGroupRate`), `expression`, `deriveExpressionGetter`/`deriveExpressionSetter` (Derived), `query`, `datasource`, `queryType`, `preserveSourceTimestamp` (Derived).

**Numeric**: `deadband` + `deadbandMode` (Absolute/Percent/Off), `scaleMode` (Off 0 / Linear 1 / SquareRoot 2 / ExponentialFilter 3 / BitInversion 4), `rawLow`/`rawHigh`/`scaledLow`/`scaledHigh` (Linear/SquareRoot only), `clampMode` (No_Clamp/Clamp_Low/Clamp_High/Clamp_Both), `scaleFactor` (Exponential Filter only), `engUnit`, `engLow`/`engHigh` (feeds Out-of-Range alarms, Engineering Limit modes, and History Analog deadband calc), `engLimitMode`, `formatString` (`#`/`0` numeric mask).

**Meta data**: `tooltip`, `documentation`.

**Security**: `readPermissions`, `readOnly`, `writePermissions` — each permission is `{type: AnyOf|AllOf, securityLevels: [...]}` JSON.

**Scripting**: `eventScripts` — array of `{eventid, script}`; `eventid` ∈ `qualityChanged`, `valueChanged`, `alarmActive`, `alarmCleared`, `alarmAcked`.

**Alarms**: `alarms` (array — see Alarming section), `alarmEvalEnabled`.

**History**: `historyEnabled`, `historyProvider` (targets exactly one historian; the dropdown shows names *as configured at the time*, so renaming the provider later requires manually reselecting it on every tag), `historicalDeadbandStyle` (`Auto`/`Analog_Compressed`/`Discrete`), `historicalDeadbandMode`, `historicalDeadband`, `sampleMode` (`OnChange`/`Periodic`/`TagGroup`), `historySampleRate` + `historySampleRateUnits`, `historyTagGroup`, `historyTimeDeadband` + units (Min Time Between Samples), `historyMaxAge` + units (Max Time Between Samples — must be ≥1000ms; 0 disables forced collection; ignored if Sample Mode = Tag Group and the Tag Group itself sets a non-default Max Time).

Units-of-time enum (`MS`, `SEC`, `MIN`, `HOUR`, `DAY`, `WEEK`, `MONTH`, `YEAR`) is shared across Numeric, History, and Alarm-delay properties.

**Runtime-only** (Tag Browser, not the editor): `CanRead`, `CanWrite` — computed from permissions + provider settings + Read Only.

**Custom properties**: arbitrary user-defined properties addable per-tag via the Tag Editor's Custom category; bindable like any other property from Vision/Perspective.

### Quality / QualifiedValue model

Every value carries quality as a `(level, subcode)` pair. Four levels, by numeric range:

| Range | Level | Meaning |
|---|---|---|
| 0–255 | **Good** | Value generally trustworthy |
| 256–511 | **Uncertain** | Was good, reliability now questionable (commonly: no new value arrived in time) |
| 512–767 | **Bad** | A recognized, "expected" problem class (denied access, disabled source, license issue...) |
| 768–1023 | **Error** | Unexpected internal failure; details usually only in a Gateway console log |

Selected subcodes: `Good_Unspecified`(0), `Good_WritePending`(2), `Good`(192), `Good_Provisional`(200), `Good_Initial`(201), `Good_Overload`(202), `Good_Backfill`(203); `Uncertain`(256), `Uncertain_LastKnownValue`(257), `Uncertain_InitialValue`(258), `Uncertain_DataSubNormal`(259), `Uncertain_EngineeringUnitsExceeded`(260), `Uncertain_IncompleteOperation`(261); `Bad`(512), `Bad_Unauthorized`(513), `Bad_AccessDenied`(514), `Bad_Disabled`(515), `Bad_Stale`(516), `Bad_TrialExpired`(517), `Bad_LicenseExceeded`(518), `Bad_NotFound`(519), `Bad_ReferenceNotFound`(520), `Bad_AggregateNotFound`(521), `Bad_NotConnected`(522), `Bad_GatewayCommOff`(523), `Bad_OutofRange`(524), `Bad_DatabaseNotConnected`(525), `Bad_ReadOnly`(526), `Bad_Failure`(527), `Bad_Unsupported`(528); `Error`(768), `Error_Configuration`(769), `Error_ExpressionEval`(770), `Error_TagExecution`(771), `Error_TypeConversion`(772), `Error_DatabaseQuery`(773), `Error_IO`(774), `Error_TimeoutExpired`(775), `Error_Exception`(776), `Error_InvalidPathSyntax`(777), `Error_Formatting`(778), `Error_ScriptEval`(779), `Error_CycleDetected`(780).

A `QualifiedValue` = `{value, quality, timestamp}`. Referenced/expression tags propagate the *worst* sub-quality of their inputs upward.

Full subcode reference tables (as published in the docs):

**Good (0–255)**

| Quality | Subcode | Description |
|---|---|---|
| Good_Unspecified | 0 | Generic "good" code, generally paired with 1/2/192. |
| Good_WritePending | 2 | A write is in progress; resolves to 192 once confirmed. |
| Good | 192 | Meets all criteria for reliability. |
| Good_Provisional | 200 | Good, but not to be considered valid long-term. |
| Good_Initial | 201 | Initial/seed value for a starting-up system. |
| Good_Overload | 202 | Good data sampled slower than requested due to a resource limitation. |
| Good_Backfill | 203 | Good value that arrived out of order. |

**Uncertain (256–511)**

| Quality | Subcode | Description |
|---|---|---|
| Uncertain | 256 | Unspecified degree of uncertainty. |
| Uncertain_LastKnownValue | 257 | Current value unavailable; showing last known. |
| Uncertain_InitialValue | 258 | Subscribed; a good value should arrive shortly. |
| Uncertain_DataSubNormal | 259 | Insufficient good-quality sources to derive this value. |
| Uncertain_EngineeringUnitsExceeded | 260 | Value has gone beyond its configured engineering units. |
| Uncertain_IncompleteOperation | 261 | An async operation is pending; result unknown. |

**Bad (512–767)**

| Quality | Subcode | Description |
|---|---|---|
| Bad | 512 | General bad-value code. |
| Bad_Unauthorized | 513 | Unauthorized request for data requiring authorization. |
| Bad_AccessDenied | 514 | Requester lacks required credentials. |
| Bad_Disabled | 515 | Data source currently disabled. |
| Bad_Stale | 516 | Out of date vs. the requested refresh interval. |
| Bad_TrialExpired | 517 | Trial mode timer expired. |
| Bad_LicenseExceeded | 518 | License limit exceeded. |
| Bad_NotFound | 519 | Requested object not found. |
| Bad_ReferenceNotFound | 520 | A derived/referenced object required was not found. |
| Bad_AggregateNotFound | 521 | Requested aggregate not found. |
| Bad_NotConnected | 522 | A required connection is not currently connected. |
| Bad_GatewayCommOff | 523 | Designer's connection to the Gateway is off. |
| Bad_OutofRange | 524 | Value exceeded its allowed range. |
| Bad_DatabaseNotConnected | 525 | A required DB connection is not connected. |
| Bad_ReadOnly | 526 | Write attempted on a read-only target. |
| Bad_Failure | 527 | A recognized "failure" response, not an exception. |
| Bad_Unsupported | 528 | Operation not supported by the target. |

**Error (768–1023)**

| Quality | Subcode | Description |
|---|---|---|
| Error | 768 | Unexpected error retrieving/calculating the value. |
| Error_Configuration | 769 | Value's source is misconfigured. |
| Error_ExpressionEval | 770 | Source expression failed to execute. |
| Error_TagExecution | 771 | Source tag could not execute. |
| Error_TypeConversion | 772 | Raw value could not coerce to the configured data type. |
| Error_DatabaseQuery | 773 | Required DB query errored on execution. |
| Error_IO | 774 | I/O error retrieving/calculating the value. |
| Error_TimeoutExpired | 775 | Async operation timed out. |
| Error_Exception | 776 | An exception was caught and logged. |
| Error_InvalidPathSyntax | 777 | A tag/property path could not be parsed. |
| Error_Formatting | 778 | Numeric/date formatting failed. |
| Error_ScriptEval | 779 | A required script failed to execute. |
| Error_CycleDetected | 780 | Calculating the value hit an execution cycle. |

> Note for 7.9 upgrades: old quality codes are automatically adapted to this scheme, so historical quality results and bindings remain trustworthy, but manual/hardcoded quality checks in old scripts should be re-verified against the new codes above.

**Component overlays**: Perspective has 3 overlay classes — Pending (Good subcode 2 only), Unknown (any Uncertain), Error (any Bad/Error) — each with small/large variants; clicking shows diagnostic detail. Vision has a richer per-subcode overlay chart and shows the underlying error type directly on the overlay icon (Designer, Preview mode, and running Client all behave the same). A binding can set **Overlay Opt-Out** to suppress overlays for a tag entirely — use sparingly since it hides quality problems from the operator. A separate **Template Overlay** appears on Vision template instances whose `Template Path` fails to resolve.

### Scan classes / tag groups (execution model)

A **Tag Group** dictates the *rate and conditions* under which its member tags execute (OPC poll/subscribe rate, Expression re-evaluation rate, Query re-run rate). Configured per Tag Provider via the Tag Group Editor (Tag Browser → Edit Tag Groups icon).

| Mode | Behavior |
|---|---|
| **Direct** | Single fixed `Rate` (ms). Simplest; the default group on a fresh install. |
| **Driven** | Switches between `Rate` and `Leased/Driven Rate` based on comparing a `Driving Expression` against `Comparison Value` using `Driving Comparison` (`=`,`!=`,`<`,`<=`,`>`,`>=`, or **Any Change** — which ignores both Rate settings and executes immediately on any change). `One Shot`: executes once per false→true (rising-edge) transition instead of continuously at the driven rate — lets one tag change fan out to refresh many others on demand. |
| **Leased** | Switches per-*tag* between `Rate` and `Leased/Driven Rate` depending on whether that specific tag is currently displayed/bound in an open Designer, Vision Client, or Perspective Session — **not** merely visible in the Tag Browser. Different tags in the same Leased group can run at different rates simultaneously. |

OPC-specific Tag Group settings: `Data Mode` (**Subscribed** — event-driven, can overload network if the source over-publishes, silently fails over to polling; **Polled** — predictable load each execution, and combined with Driven+One-Shot gives you a manual "refresh" trigger), `Read After Write` (write then read-back — doubles traffic, and is dangerous combined with Subscribed mode due to a race condition), `Optimistic Writes` (+ timeout — apply the write to the Ignition tag immediately, before PLC confirmation; keep the timeout *longer* than the Rate or you'll see flicker back to old value then a snap to the true value).

OPC UA settings: `Publishing Interval` (-1 = automatic), `Sampling Interval` (-1 = inherit from Tag Group Rate; 0 has driver-dependent behavior), `Queue Size`, `Include Timestamp-Only Changes`.

History settings on a Tag Group (`Min/Max Time Between Samples` + units) apply to tags whose `Sample Mode` = Tag Group, and take precedence over the tag's own Max Time setting *only* when set to non-default values.

> Note: a Tag Group `Rate` of 0 means that group **never executes** (used deliberately on Driven/Leased "off" states to freeze the last value — including for history, which then records nothing during that period).

### System tags

Read-only status tags under a special **Managed** `[System]` provider, split into `Client` (Vision-only, per-client values) and `Gateway` (server-wide) folders.

Selected **System Client tags** (Vision): `Network` folder — `GatewayAddress`, `GatewayRedundancyRole`, `Hostname`, `IPAddress`, `MACAddress`; `System` folder — `CurrentDateTime`, `DefaultDatabase`, `DefaultTagProvider`, `FPMIVersion`, `JavaVersion`, `OperatingSystem`, `ProjectName`, `ProjectUpdateAvailable`, `SystemFlags`, `UserSource`; `User` folder — `Username`, `RolesString`/`RolesDataSet`, `Country`, `Language`, `Timezone`, `HomeFolder`, plus a full set of locale-aware date/time format strings (`DateFormatFull/Long/Medium/Short`, `TimeFormatFull/Long/Medium/Short`, `DateTimeFormatFull/Long/Medium/Short`).

Selected **Gateway System tags**, by folder:

| Folder | Notable tags |
|---|---|
| Root | `CurrentDateTime`, `DeploymentMode`, `LicenseState` (`Activated` or `Trial`), `RestartTasks`, `SystemName`, `Timezone`, `UptimeSeconds`. |
| Alarming | `Active and Acked`, `Active and Unacked`, `Clear and Acked`, `Clear and Unacked` — quick alarm-count labels. |
| Database (per connection) | `ActiveConnections`, `Available`, `AvailableThroughFailover`, `AvgQueryTime`, `ConnectionSaturation`, `QueriesPerSecond`. |
| Device (per device) | `Description`, `Enabled`, `Name`, `Status`. |
| EAM (per Agent) | Metrics subfolders for Database/Logging/Session/System, plus root tags `AgentGroup`, `AgentName`, `IsApproved`, `IsConnected`, `IsRunning`, `LastCommunication`, `NodeRole` (Independent/Master/Backup), `PlatformEdition`, `RunningState`, `ServerId`, `Version`. |
| Gateway Network (per peer, named `0:0`/`0:1`/`0:2`) | `IsAvailable`, `LastComm`. |
| Licenses (leased licenses only) | `ConsecutiveErrorCount`, `ErrorCode`, `Expiration`, `ExpiresInSeconds`, `NextCheck`, `Problem`, `Status`. |
| OPC (per OPC UA server) | `Connected`, `Enabled`, `State`. |
| Performance | `Available Disk Space (MB)`, `CPU Usage`, `Disk Utilization`, `Max Memory`, `Memory Usage`, `Memory Utilization`. |
| Redundancy | `Connection.IsConnected`, `Connection.PeerId`, `ActivityLevel` (undecided/cold/warm/active), `IsActive`, `IsMaster`, `Role`. |
| Sessions | `SessionCount` (does not include Perspective sessions). |
| Store and Forward (per connection) | `TotalDroppedCount`, `TotalPendingCount`, `TotalQuarantinedCount`, plus `ForwardMetric`/`StoreMetric` subfolders with `FifteenMinuteRate`/`FiveMinuteRate`/`OneMinuteRate`. |

System tag configurations (e.g. alarms on `LicenseState`) cannot go through the normal Tag Browser import/export UI — see **Exporting/Importing System Tag Configurations** below for the scripting-only path.

### Tag Browser / Tag Editor UI

**Tag Browser toolbar**: Add (browse devices / new tag / folder / UDT instance / UDT definition), Find/Replace (opens the Designer's global Find/Replace), Refresh Providers, the Tag Provider Selector (bold entry = the project's default provider, set under Project Properties > Tag Settings > Default Provider), and a **More Options** menu holding Tag Groups editor, Import/Export, Column Selector, **Tag Report Tool**, and a **Display Alarm Metrics** toggle (the Alarm Metrics folder is shown by default under alarmed tags and at the provider level).

**Right-click menu** highlights: `Edit (raw)` opens the underlying JSON directly — for UDTs, note the default **Overwrite** collision policy on a raw edit/import *removes members missing from the pasted JSON*, so prefer `MergeOverwrite` for a partial patch; `Copy JSON` / paste round-trips tag definitions between providers or Designers via the system clipboard; `Restart Tag` refreshes value generation, scaling, engineering limits, alarms, deadbands, and event scripts for that tag (recursively, if a folder is restarted) — useful after a config change that doesn't otherwise take effect live.

**Tag Traits** (icons shown inline next to a tag in the Browser): Scaling (non-Off Scale Mode), Alarming (≥1 alarm configured), Tag History (history enabled), Tag Event Script (≥1 event script enabled), Lock (permissions restricted), Inheritance (UDT parent-type indicator), Override (a UDT instance member overrides its parent's value).

### Creating tags and addressing individual bits

Two creation paths: the **Connected Devices** window (browse OPC tags and drag them in, or manually stage a new standard tag — invalid characters `! @ # $ ^ & * + [ ]` are auto-replaced with `_` when drag-dropping an OPC item, and a leading parenthesis gets an underscore prefix), or creating a tag directly in the **Tag Browser** and configuring it in the Tag Editor.

**Bit addressing**: to expose a single PLC bit as its own Boolean tag, create a second OPC tag pointing at the same word with a bit suffix — syntax is device-dependent: MicroLogix `[device]N7:1/0`, ControlLogix `[device]Folder/Tag.0`, Siemens `[device]I0.0`. Worked example against a MicroLogix integer 1025 (`0000010000000001` binary, bits 0 and 10 set): `[MLX]B3:0/0` reads `True` (bit 0 set), `[MLX]B3:0/1` reads `False` (bit 1 clear) — MicroLogix accepts either `/` or `.` as the bit-index separator.

### Exporting and importing tags

Ignition exports tags as **JSON** or **XML**; it can **import** JSON, XML, or **CSV**, converting everything to JSON internally. Collision policies on import:

| Policy | Behavior |
|---|---|
| Abort | Aborts the whole import if any duplicate is found. |
| Overwrite | Full replace of matching tags. **On a UDT Definition, this removes any member not present in the import file.** |
| Rename | Duplicate tags are imported under a new name. |
| Ignore | Only unique (non-colliding) tags are imported. |
| MergeOverwrite | Overwrites matching properties but merges (keeps) any property *not* present in the import file — the safe choice for partial UDT Definition patches. |

The **Interactive** import variant (Import Tags > Interactive) opens an Advanced Tag Import tool combining staging-area selection with an inline Tag Editor for pre-import edits; it only supports **Overwrite** or **Ignore** as collision policies. A large interactive import may require raising the Designer's memory allocation (Gateway > Config > Gateway Settings > Designer Memory, 128MB–4.0GB).

CSV import supports most tag properties (including scaling, history, and basic OPC/Expression/Query/Derived/Memory typing) but **not alarm configuration** — alarms must be added afterward in the Designer. The legacy CSV `TagType` values: `0`=OPC, `1`=DB Tag (see `ExpressionType`: `0`=None/Memory, `1`=Expression, `2`=SQL Query), `2`=Client Tag, `6`=Folder, `10`=UDT Instance, `13`=Derived. Ignition does **not** export to CSV (JSON/XML are needed to represent the full tree/alarm structure).

**UDT export note**: exporting a UDT *instance* does not automatically bundle its *definition* — export the definition separately from the UDT Definitions tab, and import definitions before instances.

**System tags** cannot use the normal export/import UI at all — use `system.tag.exportTags(filePath, tagPaths)` and `system.tag.configure(providerPath, tagsJsonString)` from the Script Console instead:
```python title="Export a single System tag"
filePath = "C:\\Users\\myUser\\Desktop\\mySystemTags\\targetedSystemTag.json"
tagPaths = ["[System]Gateway/LicenseState"]
system.tag.exportTags(filePath, tagPaths)
```
```python title="Import it back / onto another Gateway"
filePath = "C:\\Users\\myUser\\Desktop\\mySystemTags\\targetedSystemTag.json"
tags = system.file.readFileAsString(filePath)
system.tag.configure("[System]Gateway", tags)
```
A `Bad_AccessDenied("Insufficient Tag Provider Edit Permissions")` warning after such an import is expected/benign when the JSON references tags that don't exist, live elsewhere, or aren't editable on the target system — tags that *do* match still get updated.

### Tag Diagnostics and the Tag Reference Tracker

Right-click any tag → **View Tag Diagnostics** opens a window with three tabs. Values shown are a **static snapshot at open time** (use the Refresh icon to update) — they do not live-update.

- **Diagnostics** tab: current value/quality/timestamp, error messages, dependent-datasource status, plus per-category diagnostic subfolders — `Alarm*` (Last State, Live Event Count, capped by the Gateway's Live Event Limit), `Deadband` (Last value, Limit), `History` (Deadband Analog/Discrete sub-metrics, Min/Max Age Limits in ms, Pending Value, last-storage timestamps, lifetime Stored Value Count), `OPC` (Last Subscription Value — ignores deadband, Server/Subscription Name, Valid Tag Group?), plus `Is Leased`, `Is Scaled`, `Tag Definition Valid?`, `Tag id`, and per-tag-event-script error surfaces (Value/Quality/Alarm Active/Cleared/Acked Changed).
- **Active Subscriptions** tab: live list of every resource currently subscribed to the tag (Subscriptions path, First Referenced timestamp, Totals count) — e.g. multiple open Sessions bound to the same View increment Totals.
- **Reference Log** tab (backed by the **Tag Reference Tracker Store**, enabled by default): shows every place a tag has been read, written, subscribed, or had its configuration changed (`Read`/`Write`/`Subscription`/`Configuration` usage types), with Last Referenced timestamp and an Updates count. It **only reflects references seen since tracking began** — it will miss anything not active since then, and gets more reliable the longer it runs. Toggle it per Standard/Remote provider (provider's Edit page) or globally for Managed providers (System Settings page — affects *all* managed providers at once, so many third-party modules can generate a lot of data). Gateway backups **do not include** Tag Reference Store data — its files live in a separate `data/diagnostics/tags` folder (per-OS paths differ) and must be backed up manually if that history matters.

### Tag Report Tool

Cross-tag search/report builder (More Options > Tag Report Tool), scoped to **one Tag Provider per query**. Criteria include Tag Path (wildcard `*`), Quality (broad level or specific subcode), Types (value source), Traits (Event Script Configured / Value Scaling Applied / Alarm(s) Configured / History Enabled / Overrides Parent Properties / Custom Security Permissions / Tag Disabled — **trait selections combine as AND**), Ancestor (UDT parent type), and per-Property filters using operators `Has`, `Has Not`, `Overridden`, `Like`/`Not Like` (wildcard `*`), and the usual `> >= < <= = !=`. `Or` combines top-level criteria (with `And` nestable inside an `Or`) — **not supported querying a remote Tag Provider on a Gateway older than 8.1.28**. Saved reports are shared across all users/Designers on the Gateway and reusable against different providers. Results can be copied as a JSON query (pasteable into another Gateway's Tag Report Tool) or as an equivalent `system.tag.query()` script, and exported to CSV. **Caution**: editing or deleting a row in the Tag Report Tool edits/deletes the real tag, not just the report.

---

## UDTs

**Terminology**: a **Definition** is the static structure (doesn't run/poll on its own); an **Instance** is a running copy that inherits structure from its Definition — you cannot add members directly to an Instance, but you can **override** property *values* on its members. The **Root Node** is the UDT's top-level item; **Members** are the tags beneath it (standard tags or nested UDT instances). **Parameters** are user-defined variables on a Definition, referenceable from member properties, overridable per Instance.

### Definition vs. instance workflow

1. UDT Definitions live only under the **UDT Definitions** tab of the Tag Browser; Instances live under **Tags**.
2. Create a Definition: Add → New Data Type in the Definitions tab; build its member tags (including browsing OPC devices directly from inside the Tag Editor).
3. You can also **derive a Definition from existing tags**: select tags/folders → right-click → *Create Data Type from Selected*. Selecting a single folder uses its members (not the folder itself) as the structure. Original tags are untouched.
4. Create an Instance: Tags tab → Add → *Data Type Instance* → pick the Definition.
5. **Renaming a Definition after instances exist** creates an "orphaned UDT instance" — an instance no longer tied to any definition. Avoid renaming definitions once instantiated unless you also plan to repoint every instance.

### Root Node properties

`name`, `typeId` (**on a Definition**: the parent Definition it inherits from, if any; **on an Instance**: which Definition it's an instance of — *cannot be changed on an Instance*), `documentation`, `tooltip`, `parameters` (addable/removable only on Definitions), `typeColor` (purely cosmetic; propagates to all instances' Root Node icon — useful to make certain UDT families visually distinct in a large Tag Browser tree).

### Inheritance vs. nesting — different concepts

- **Inheritance**: a new Definition sets `typeId`/Parent Data Type to an existing Definition, inheriting *all* its members and parameters; the child can then add more members and override inherited property values. Use for "simple vs. complex variant" relationships (e.g., Motor → Complex Motor).
- **Nesting**: one UDT Definition contains an *instance* of another UDT as one of its members (e.g., an Area UDT nests a Motor instance and a Sensor instance). Use for composition ("this thing is built out of these other things"). Parameters of the nested UDT must be individually wired to a parameter on the containing UDT (or a literal), even when both UDTs happen to use a parameter of the same name.

Worked nesting example from the docs: build an `Area` UDT Definition that nests one `Motor` instance and one `Sensor` instance.
1. Create the `Area` Definition; inside it add a New UDT Instance of `Motor` (rename it `Motor`) and one of `Sensor` (rename it `Sensor`).
2. Each nested instance already declares its own parameters (`MotorNumber` on Motor, `SensorNumber` on Sensor) — these must be satisfied from *somewhere*.
3. Add matching `MotorNumber`/`SensorNumber` parameters on the **containing** `Area` Definition.
4. On the nested `Motor` instance's Parameters, set the reference `{MotorNumber}` (and likewise `{SensorNumber}` on the nested `Sensor` instance) so the value flows down from whatever `Area` instance eventually supplies it.
5. If multiple nested UDTs happen to share a parameter name, it only needs to be declared once on the parent.

This means an `Area` instance's parameter values cascade automatically into its nested Motor/Sensor instances without editing each nested member by hand.

**Overriding**: click the gray override-dot next to a property on an Instance and edit the value — the dot turns green to mark an override; click again to revert to the Definition's value. Alarming and History can likewise be turned on for an instance-only member via the same override mechanism, even if off in the parent Definition. The Tag Browser shows an **Inheritance** icon (parent type name > instance) and a separate **Override** icon per affected member. The **UDT Hierarchy Tool** (right-click a Definition or Instance → *View UDT Hierarchy*) visualizes inheritance chains, overrides, and directly-related instances (nested instances are **not** shown in this tool).

### What breaks when you edit a Definition in place

- Editing the structure of a live Definition **propagates immediately** to every Instance (adding a folder/member, changing alarm config, etc.) — this is the entire point of UDTs, but it means a structural mistake fans out everywhere at once.
- **Renaming a Definition** breaks the `typeId` link on existing Instances → orphaned instances.
- The default JSON-import **Overwrite** collision policy on a UDT Definition import **removes any members not present in the import file** — use **MergeOverwrite** if you only want to patch specific members without deleting the rest.
- Instances cannot have their **Parent Data Type reassigned** after creation via the UI.

### Parameters

Pre-defined parameters available on every UDT member without explicit declaration: `{InstanceName}` (name of the immediate containing UDT instance — for a nested UDT, this is the nested instance's own name), `{ParentInstanceName}` (name of the parent UDT instance, for nested members), `{PathToParentFolder}`, `{TagName}`, `{PathToTag}`, `{RootInstanceName}` (top-most Instance name).

Reference syntax: `{ParamName}`; offset: `{ParamName+offset}`; format: `{ParamName|000}` (numberFormat-style mask). Full operator precedence table (highest to lowest):

| Operator | Description | Example |
|:---:|---|---|
| `()` | Grouping / order of operations | `{Baseaddress*(2+3)}` |
| `^` | Power | `{BaseAddress^2}` |
| unary `-` | Negative | `{BaseAddress*-2}` |
| `*` | Multiplication | `{BaseAddress*2}` |
| `/` | Division | `{BaseAddress/2}` |
| `%` | Modulus | `{BaseAddress%2}` |
| `+` | Addition | `{BaseAddress+2}` |
| `-` | Subtraction | `{BaseAddress-2}` |
| `\|` | Formatting pattern separator | `{BaseAddress\|##0.00}` |

Worked example combining offset, per-member index, and zero-padding across three sequential PLC addresses:
```python title="Standard, offset, and formatted referencing"
# Standard: OPC Item Path = DataPoint{BaseAddress}
# Offset, for three sequential fields laid out in the device:
#   Member 1: DataPoint{BaseAddress+0}
#   Member 2: DataPoint{BaseAddress+1}
#   Member 3: DataPoint{BaseAddress+2}
# Formatted to 3 digits (e.g. BaseAddress=98 -> DataPoint098/099/100):
#   Member 1: DataPoint{BaseAddress+0|000}
#   Member 2: DataPoint{BaseAddress+1|000}
#   Member 3: DataPoint{BaseAddress+2|000}

# Combined multi-parameter example:
# ns=1;s=[DeviceName]Path/to/tag{BaseAddress+(ParamNum*Multiplier)|0000}
# With BaseAddress=5, ParamNum=8, Multiplier=2 this resolves to:
# ns=1;s=[DeviceName]Path/to/tag0021
```

- A **purely numeric parameter name** requires quoting to do arithmetic on it: `{0 * 1000}` evaluates the literal 0, not the parameter named "0" — use `{"0" * 1000}`.
- A reference to a **nonexistent parameter** is *not* an error — the binding returns the literal string, braces included (`SomeText/{myParameter}`).
- A reference to a parameter whose **value is null** behaves the same way — returns the literal string form, not an error or empty value.

Multi-Instance Wizard (Add menu / right-click → *Multi-Instance Wizard*) bulk-creates instances from a Definition, across two tabs:

**Create Instances** tab — `Data Type` (Definition to instantiate), `Folder Location`, `Base Instance Name` (accepts `{token}` reference patterns, e.g. `motor{x}`), and a Reference Table (one row auto-added per `{token}` used):

| Column | Description |
|---|---|
| Reference | Token name (e.g. `x` in `{x}`). |
| Pattern Type | Numeric / Alpha (Upper) / Alpha (Lower) / **List of Names** (added in **8.3.9**). |
| Number Format | Optional mask for numeric patterns (`#`, `##`, `000`). |
| Step Count | Numeric increment between values. |
| Start From | Starting value. |
| End At | Last value (numeric references only). |

**Configure Parameters** tab (shown only if the UDT declares parameters) — by default all parameters inherit the Definition's values; check a parameter to override it:

| Column | Description |
|---|---|
| Parameter | Name + enable-override checkbox. |
| Type | Parameter's data type. |
| Parameter Value | Value to assign (editable once enabled). |
| Pattern Type | None / Numeric / Manual Entry. |
| Step Count | Interval between values (numeric patterns). |
| Start From | Starting value (numeric patterns). |
| Placement | Before/after the base string, e.g. `1Motor` vs `Motor1`. |

A live **Preview** table (Instance Name + one column per UDT parameter) updates as the pattern config changes. Worked example: Base Instance Name `Motor {x}`, Pattern Type Numeric, Start From `1`, End At `5` → generates `Motor 1` … `Motor 5`. The wizard **only creates** new instances — it cannot be used to bulk-edit existing ones.

### Designing UDTs well (patterns pulled from the docs)

- Use `[.]` (folder-relative) and `[~]` (provider-root-relative) tag paths inside UDT members so instances remain portable if moved between folders/providers.
- Parameterize the volatile part of an OPC Item Path (e.g. a base address or unit number) rather than hard-coding per-instance addressing, and use offset/format syntax (`{BaseAddress+1|000}`) for sequentially-addressed member tags.
- Put Alarms directly on UDT members so every instance automatically alarms; combine with a dynamic **Display Path** (bound to an expression using a UDT parameter, e.g. `"Motor" + {MotorNumber}`) so multiple instances don't collide on the same alarm display name.
- For dynamic setpoints shared by all instances but still overridable, add a Memory tag member to hold the setpoint and bind the alarm's Setpoint property to it (Tag or Expression binding) — this also lets a single instance's setpoint be overridden independently later.

---

## Tag events and scripting

Available tag events: `Value Changed`, `Quality Changed`, `Qualified Value` (fires on any of value/quality/timestamp change per a configurable trigger set), `Alarm Active`, `Alarm Cleared`, `Alarm Acknowledged`. Configured per-tag under **Tag Events**; each is a Python function body (indent all code beneath the generated `def`).

### The `event` object / script arguments

**Value Changed** args: `tagPath` (string), `previousValue` / `currentValue` (QualifiedValue — access `.value`, `.quality`, `.timestamp`), `initialChange` (bool — true when previous value was null, e.g. first eval after Gateway restart, or previous quality was `Uncertain_InitialValue`, e.g. an OPC tag's pre-subscription value), `missedEvents` (bool — an event-overflow condition occurred).

**Quality Changed** args: same four as above.

**Qualified Value** args: `tagPath`, `previousValue`, `currentValue`, `initialChange`, `changed` (which of value/quality/timestamp triggered this particular firing), `missedEvents`.

**Alarm Active / Alarm Cleared** args: `tagPath`, `alarmName`, `alarmEvent` (object with `eventId`, `source`, `name`, `priority`, `displayPath`, `displayPathOrSource`, `state`, `eventState`, `isClear`, `isAcked`, `isShelved`, `notes`), `alarmPath`, `missedEvents`.

**Alarm Acknowledged** args: as above, plus `ackedBy` (full path of the acknowledging user).

### Gateway tag change scripts vs. tag event scripts

Tag Event Scripts are attached directly to an individual tag (or, for UDT members, to the Definition so every Instance shares it). Because tags are Gateway-scoped and not tied to a specific project, `print` statements do **not** appear in the Designer console — they go to the wrapper log — and system functions that need project/DB context (e.g. `system.db.runPrepUpdate`) may require you to specify a database explicitly. Prefer `system.util.getLogger(...)` over `print` so messages land in the Gateway's Logs page.

UDT parameters are readable inside a Tag Event Script (always the *current* value, no restart needed) via:
```python
paramValue = tag['parameters']['myParam']
```

Project Library scripts are callable from a Tag Event Script **only if defined in the Gateway Scripting Project**.

### Threading / performance rules

- Tag Event Scripts, Expression tags, and Query tags all draw from shared Gateway thread pools; heavy or slow logic in any of them can exhaust the pool and cause *other* scripts/tags to silently stop firing on time. The docs explicitly call out raising the default thread pool count (Gateway Configuration File Reference → Thread Pool Counts) when troubleshooting or load-testing Expression tags, Query tags, or Tag Event Scripts.
- Tags sharing the same Tag Provider + history provider + rate are evaluated together as a batch by the Historian's sample-mode actor; Periodic-mode tags are grouped into a special "exempt" batch.
- A `missedEvents=True` flag on any tag event indicates the Gateway's internal event queue overflowed for that tag — treat consecutive/rapid value changes as potentially *coalesced*, not guaranteed one-event-per-change, if your script logic depends on catching every transition.

---

## Tag historian

### Storage pipeline (how a value becomes a history record)

1. **Sample mode actor** decides *when* to check for a storable value: `On Change` (evaluate every tag update, plus an internal timer that force-stores if the tag has been static too long), `Periodic` (fixed interval regardless of change), `Tag Group` (piggybacks on a configured Tag Group's execution rate).
2. **Min/Max timer actor**: discards the candidate if the configured minimum time between samples hasn't elapsed; force-stores if the maximum time has been exceeded even without a real change.
3. **Deadband actor**: compares the candidate to the last-stored value; only stores if the change exceeds the configured deadband (interpreted per Deadband Style — see below).
4. Stored samples are bundled into a **history set** (values sharing a Tag Provider/history provider/rate — except Periodic-mode tags, which form their own "exempt" set) and handed to either the **Store and Forward** system or written directly to disk, depending on the target historian provider.
5. **Store and Forward path** (Internal Historian (Legacy), SQL Historian, most external providers): memory buffer → (if no backlog) direct DB write, else → disk local cache (write-time/size threshold) with a separate **quarantine** area for records that fail to write (stuck until manual intervention or automatic retry) → database sink, which batches records into one transaction, caches tag-ID lookups in memory, and retries failed records individually before quarantining them.
6. **Core Historian path**: writes **directly to disk via a write-ahead log (WAL)** — it explicitly **does not use Store and Forward** at all, bypassing that buffering/retry/quarantine mechanism entirely.

Each record: value, quality, and a **millisecond-resolution timestamp**.

### Deadband styles (Discrete vs. Analog compression)

- **Discrete**: store `V1` iff `|V1 - V0| >= Deadband`. No interpolation on query — returned value is simply the last-known value held until the next real record.
- **Analog** (a modified Sliding-Window compression algorithm): on every value change, compute
  ```
  Upper Slope = ((NewValue + Deadband) - PreviousValue) / (NewTimestamp - PreviousTimestamp)
  Lower Slope = ((NewValue - Deadband) - PreviousValue) / (NewTimestamp - PreviousTimestamp)
  ```
  The first value on a tag is always stored (needed as slope baseline). A new value is stored whenever the new Upper Slope < the *previously tracked* Lower Slope, or the new Lower Slope > the *previously tracked* Upper Slope; a quality change always forces a store. Otherwise, slope bounds are tightened (only ever narrowed) for the next comparison. Query-time values are linearly interpolated between stored points.
  > ⚠️ **Caution — Core Historian + Analog deadband**: out-of-order writes generated by the Analog style "can be taxing" on the Core Historian; the docs recommend either the Discrete style or turning deadband off and using Periodic sample mode instead.
- **Auto** (default): picks Analog for float/double tags, Discrete for everything else.

### Interpolation, seed values, raw queries

- Interpolation only occurs when the chosen Aggregation Mode supports it, `Avoid Interpolation` is off, and no raw data exists in a given window.
- The **Average** aggregation mode uses a *time-weighted* mean (`0.5 × |curr−prev| × timediff + timediff × min(curr,prev)`, summed and divided by total window duration) rather than a simple arithmetic mean used by other modes.
- **Seed values** (aka boundary values) are the last value just before the query start (pre-query seed) and just after the query end (post-query seed), fetched to support interpolation at the window edges. They're included by default; to suppress them you must simultaneously disable interpolation, use Discrete deadband style, and set `noInterpolation=True` + `includeBoundingValues=False` on the query. Post-query seeds are **not** returned for Discrete-deadband tags. For a live/near-now query end, Ignition may substitute the current tag value as the post-query seed instead of a DB read.
- SQL Historian: **Number of past partitions queried for seed values** (0 = disable seed search globally; negative = search every partition) controls how far back a seed search looks — important when comparing two Historian Splitter targets with different partition sizes, since inconsistent seed-search depth otherwise produces a misleading `0` from one side.
- **Raw data queries** (no aggregation/interpolation) are obtained via: Vision Tag History binding Sample Mode = **On Change**; `returnSize=-1` on `system.historian.queryRawPoints`/`queryAggregatedPoints`; or Perspective Tag History binding Query Mode = **AsStored**. Note `queryRawPoints` **never** uses pre-processed partitions, even when pre-processing is enabled.

### History providers ("Historians")

Configured under **Services > Historians > Historians** on the Gateway. All share Name/Description/Enabled.

| Provider | Read/write | Notes |
|---|---|---|
| **Core Historian** | R/W | Embedded, powered by **QuestDB**. Partitioning, deduplication, archiving, native in-DB aggregation. Writes via WAL, **bypasses Store and Forward**. Default memory allocation is 10% of system RAM (tunable via Java params). `Partition Interval` (Week/Month/Year), `Data Deduplication` (matching-key writes update in place instead of duplicating). Maintenance `Mode`: **None** (keep forever), **Prune** (delete old partitions, default), **Archive** (move old partitions to `Archive Folder`), each governed by `Maintenance Age`/`Units` which must be a whole multiple of the Partition Interval. |
| **Internal Historian (Legacy)** | R/W | Lightweight embedded **SQLite**-backed historian; suited to Edge/standalone/small systems. Supports automatic pruning (time- and/or point-count-based) and remote sync to another Gateway (with an optional schedule string like `9:00-15:00`). SQLite-based historians **do not record scan-class execution data**. |
| **SQL Historian** | R/W | External SQL DB (MySQL/SQL Server/Postgres/etc.) via a Data Source connection; requires the separate **SQL Historian module** in addition to Historian Core. Supports time-based table **partitioning**, **pre-processed partitions** (see below), **data pruning**, and **stale-data detection** (flags values as bad on query if the tag group hasn't executed within `Stale Detection Multiplier × tag group rate`). |
| **DB Table Historian** | R only | Exposes arbitrary existing SQL tables (e.g. from a Transaction Group, or a 3rd-party system) as queryable tag history, via a `histprov:...:/table:...:/column:...:/timestamp:...:/keycolumn:...:/keyvalue:...` path syntax. No native alarm/filter support beyond a single keycolumn/keyvalue pair — use a Named Query for anything more complex. |
| **CSV Historian** | R only | Imports a CSV (timestamp column + value columns, tag names in the header row); optional `Relative Timestamps` treats the first row's timestamp as t=0 and later rows as offsets. |
| **OPC HDA Historian** | R only | Connects to an OPC HDA server; **Windows-only**, requires the OPC COM module. Cannot store/forward. |
| **Remote Historian** | R (and optionally W) | Reads/writes a history provider on another Gateway over the Gateway Network. `Storage Allowed=false` limits it to query-only; `true` builds a Store-and-Forward pipeline to the remote provider, capped by `Max Group Size` (0 = unlimited). |
| **Historian Splitter** | W (dual) | Writes to two configured providers simultaneously (redundancy/migration/dual-archival). Queries go to the **first** connection by default; a query time-window **Limit** can be imposed to force spillover to the second. |
| **Simulator Historian** | Synthetic | Generates deterministic, repeatable fake history with **no storage** at all — pure function of the tag path. Path syntax: `function_periodTime_amplitude_resolutionTime`, e.g. `sine_10s_20_500ms`. Functions: `Ramp` (0→amplitude repeating), `Sine`, `Cos`, `Square` (half-time-at-zero/half-at-amplitude), `Realistic` (400 pseudo-realistic points repeating per period — ignores amplitude/resolution). Time-unit suffixes: `ms s m h d`. |

**Pre-processed partitions** (SQL Historian only): summarizes raw rows into a second set of partition tables named `sqlth_data_X_YYYY_MM_windowSize`, using a configurable `Pre-processed Window Size` (seconds; default 60). Only engaged for (a) legacy `system.tag.queryTagHistory`/`queryTagCalculations` calls, and (b) when the requested interval **exceeds** the configured window size — a smaller requested interval falls back to raw tables. Pre-processed rows carry a `vtype` bitmask: `0`=time-weighted average, `1`=min, `2`=max, `4`=exit (last-in-window), `32`=first-value flag, `64`=entry (first-in-window) — combined additively, e.g. `98 = 64+32+2` (entry + first + max).

**Metadata storage** (Core and Internal-Legacy historians only): enabling `Include Metadata` on a tag's History settings stores tag path/data-type/units/scaling in system-managed tables that **persist even if the tag is later deleted**. Required for annotations, aggregates, and the `system.historian` scripting API.

### Querying / API surface

- **Tag History bindings** in Perspective and Vision; **Report Data** tab in Reporting; and the `system.historian` namespace: `queryValues`, `storeDataPoints`, `queryMetadata`, `storeAnnotations`, `queryRawPoints`, `queryAggregatedPoints`.
- Perspective/Vision component-driven queries are routed through a **cache**; missing ranges are fetched from the DB and merged, then the combined result is cached again. Scripting calls like `system.historian.queryValues` **always skip the cache** and hit the DB directly.
- If **pre-processed partitions** are enabled and the query qualifies, the Historian uses them instead of raw tables (SQL Historian only — the Core Historian doesn't support pre-processed partitions).
- The **processor** slices the combined dataset by requested sample size and applies aggregation/interpolation per slice (e.g. a 10-minute query for 10 values → ten 1-minute slices).
- **Query Only licensing**: for Scale-Out architectures where a front-end server should only *read* history, a licensing option limits the Historian Core module to read-only operation.

### Aggregation modes

Selected via the Aggregation Mode property on Tag History bindings / `system.historian.queryAggregatedPoints`. From the docs' interpolation walkthrough and property references, the named modes include **SimpleAverage** (plain arithmetic mean of raw values in the window) and **Average** (the time-weighted mean described above — the *only* mode that differs from the "use the interpolated boundary value" rule that otherwise applies uniformly across modes). Other standard modes (min/max/sum/count/range/etc., referenced generically as "Aggregation Mode" throughout the binding docs) select which statistic is computed per time slice once the processor has bucketed the raw+interpolated values.

### Pruning

- **Internal Historian (Legacy)**: `Time Limit` (age-based) and/or `Point Limit` (count-based) pruning, each independently toggleable.
- **SQL Historian**: `Enable Data Pruning` + `Prune Age`/`Units`. Pruning deletes whole **partitions**, so data is only removed once an entire partition falls older than the prune age (i.e., pruning granularity = partition length, not per-row).
- **Core Historian**: pruning is one of the three Maintenance `Mode`s (**Prune** deletes; **Archive** relocates before deleting; **None** keeps forever), governed by `Maintenance Age`/`Units`, which must be a whole-number multiple of the configured `Partition Interval`.

### 8.3 historian changes

> The docs describe the Historian around a **"Historian Core module"** governing a family of pluggable *history providers* — a QuestDB-backed **Core Historian** (new, high-throughput, WAL-based, no Store-and-Forward, native in-DB aggregation, dedup, archiving) alongside an explicitly-labeled **"Internal Historian (Legacy)"** (the older SQLite-based embedded historian). This Legacy naming, and the fact that the Core Historian is now the module's flagship embedded option, is the clearest signal of the reorg.
- **NEW**: Core Historian (QuestDB). Starting in **8.3.4**, `server.conf` and `log.conf` are auto-created per Core Historian and should be used to customize settings (Cairo commit mode, WAL, HTTP/PG-wire, RAM, logging, Materialized View, Metrics) — `server.conf` **supersedes** the older system properties, though legacy properties like `historian.questdb.httpServerEnabled` still work and take precedence *if* they conflict with `server.conf`.
- **RENAMED / DEMOTED**: the old default embedded SQLite historian is now explicitly the **"Internal Historian (Legacy)"** — still fully supported (good for Edge/small installs) but positioned as the legacy path next to Core Historian.
- **NEW scripting API**: `system.historian.*` (queryValues, storeDataPoints, queryMetadata, storeAnnotations, queryRawPoints, queryAggregatedPoints) is the current interface; **Custom Tag History Aggregates are deprecated** and only work with the deprecated `system.tag.queryTagHistory`/`system.tag.queryTagCalculations` functions — "these features still work for older projects... but are not supported by the newer `system.historian` API and are not recommended for new development."
- **NEW**: Query-Only licensing option for read-only Scale-Out front ends.
- Metadata storage (`Include Metadata`) is scoped specifically to Core + Internal-Legacy historians, and is a prerequisite for annotations/aggregates/scripting-API features.

---

## Alarming

### Alarm sources

Alarms can be configured on: Memory, Query, Expression tags; tags inside a UDT; OPC items inside SQL Bridge / Transaction Groups (without needing a full Ignition tag); and **System tags** (e.g. Gateway CPU/performance). **Dataset-type tags are not supported.**

### Configuration properties on tags (full set)

**Main**: `name` (unique per host; only text after the last `/` is displayed in tables — avoid `/` in names), `enabled`, `priority` (`Diagnostic` 0 / `Low` 1 / `Medium` 2 / `High` 3 / `Critical` 4), `timestampSource` (`System`=0 or `Value`=1 — Gateway clock vs. the source value's own timestamp), `label` (dynamic display alternative to `name`), `displayPath` (defaults to tag-path + alarm name if blank), `ackMode` (`Unused`=0 always-acked / `Auto`=1 acked-on-clear / `Manual`=2 — note: **Unused** prevents the alarm from ever entering a pipeline via the default Acknowledged dropout condition, unless you also clear that dropout condition), `notes`, `ackNotesReqd`, `shelvingAllowed`.

**Mode / setpoints**: `mode` — **Equality**, **Inequality**, **AboveValue**, **BelowValue**, **BetweenValues** (`anyChange` variant fires one event per value change while inside range), **OutsideValues** (same anyChange variant), **OutOfEngRange** (same as OutsideValues but sourced from the tag's own Engineering High/Low), **BadQuality**, **AnyChange** (fires an event on every value change; *never* reports "active" — each active pairs instantly with a clear), **Bit** (`bitPosition`, `bitOnZero` to invert), **OnCondition** (free-form — bind `activeCondition`/`Is Active` to any boolean expression or tag), **WhenTrue** / **WhenFalse** (Boolean tags, or non-zero/zero for Integer tags). `setpointA` (Setpoint, or Low Setpoint for dual-setpoint modes — **must be numeric**; a string setpoint coerces to 0), `inclusiveA`, `setpointB` (High Setpoint, dual-setpoint modes only), `inclusiveB`.

**Deadband / time delay**: `deadband` + `deadbandMode` (Absolute/Percent/Off) — a *positive* deadband means an active alarm must clear its setpoint by that margin before transitioning to Cleared (e.g. Between-Setpoints 50–70 with deadband 2 activates in [50,70] but only clears below 48 or above 72). `timeOnDelaySeconds` (**Active Delay** — rising-edge time deadband: condition must hold true this long before the alarm actually goes active), `timeOffDelaySeconds` (**Clear Delay** — falling-edge equivalent). Note the tag's own value-deadband is applied *before* any alarm ever gets a chance to evaluate a new value.

**Notification routing**: `activePipeline`, `clearPipeline`, `ackPipeline` — pipeline names to enter on each transition. Per-alarm message overrides: `voip.customMessage`, `CustomEmailSubject`, `CustomEmailMessage` (supports raw HTML), `CustomSmsMessage`.

**Bit-packed alarms**: a common PLC pattern stores multiple discrete fault conditions as individual bits of one integer word. Ignition reads that integer as a normal tag (via OPC UA), and the **Bit** alarm mode lets you configure one alarm per bit. Worked example — an 8-bit tag with value `142` (binary `10001110`) can carry up to 8 independent bit alarms, one per `Bit Position` (0 = least significant):
```
Binary     Decimal
10001110   142
```
Steps: Tag Editor → Alarms → Add → set `Mode = Bit State`, `Bit Position = <n>`, repeat per bit, incrementing `Bit Position` each time.

**Associated data**: arbitrary user-defined properties (static or dynamic/bound), snapshotted onto the event when it becomes active, and carried through the notification/journal/status pipelines. Always stored as **strings** — retrieving them in scripting/expressions requires explicit type-casting (`alarmEvent.get("PropertyName")` then cast). Recommended as the primary mechanism for **alarm grouping** (over folder hierarchy or Display Path), since it's the most flexible and filterable option. Values are attached *before* the events that use them occur — adding associated data does not retroactively populate already-recorded history.

Worked grouping example: add a `Group` associated-data property (e.g. value `Production`) to an alarm, then filter an Alarm Journal Table to only that group by enabling the table's `filterAlarm` extension function:
```python title="filterAlarm extension function"
group = alarmEvent.get("Group")
if group == "Production":
    return True
return False
```

### Alarm states and lifecycle (Active/Clear/Ack)

Two independent conditions combine into 4 states:
- **Active** condition: `Active` (setpoint currently met) → `Cleared` (no longer met). Events **never** transition Cleared→Active; a brand-new event is generated instead.
- **Acknowledged** condition: `Unacknowledged` → `Acknowledged` (a one-way flag, typically set via the Alarm Status Table or `system.alarm.acknowledge`).
- Combined states: Active+Unacked, Active+Acked, Cleared+Unacked, Cleared+Acked.

**General alarm settings** (Gateway → Services > Alarming > Settings; not on Edge Gateways): `Live Event Limit` (default 5 — max "live" (active-or-unacked) events retained per alarm; the system auto-acknowledges the oldest beyond this, without storing history for the discarded overflow — raising it increases memory use under flapping alarms), `Continuous Event Detection Window` (default 10 min — suppresses duplicate unacked-active events being regenerated purely from a reboot; 0 disables), `Notify Initial Events` (default false — an alarm's very first evaluation, e.g. right after being added or re-enabled, does *not* notify by default).

**Runtime alarm metrics** (auto-exposed under `<TagPath>/Alarm Metrics.<property>` once ≥1 alarm exists on a tag, and also at the folder/provider level as an aggregate): `ActiveAckCount`, `ActiveUnackCount`, `ClearUnackCount`, `HasActive`, `HasUnacknowledged`, `HighestAckedName`/`Priority`, `HighestActiveName`/`Priority`, `HighestUnackedName`/`Priority`, `LastActiveTime`, `ShelvedCount`, plus priority-bucketed families `ActiveCount(Pri*)`, `HasActiveUnacked(Pri*)`, `UnackCount(Pri*)` (e.g. `ActiveCountCritical`, or wildcard `ActiveCount(*)`). These are bindable/subscribable but **not directly readable** — create a Reference tag pointing at a specific metric if you need to read it via script. Per-individual-alarm runtime properties (under `Alarms.<AlarmName>`): `AckTime`, `AckUser`, `AckUserName`, `ActiveTime`, `ClearTime`, `DisplayPath`, `DisplayPathOrSource`, `Enabled`, `EventState` (Active 0/Clean 1/Acknowledge 2 — sic), `EventTime`, `EventValue`, `IsAcked`, `IsActive`, `IsClear`, `IsShelved`, `Label`, `Name`, `Priority`, `SetpointA`/`SetpointB`, `Source`, `State` (Clear+Unacked 0/Clear+Acked 1/Active+Unacked 2/Active+Acked 3).

### Priorities, shelving

Priorities (with numeric values used for sorting/comparison): Diagnostic(0), Low(1), Medium(2), High(3), Critical(4).

**Shelving** suppresses an alarm for a fixed duration — new events are prevented and existing events are hidden from Status Table components and notifications during the shelf window; at expiration the source tag is re-evaluated and can generate a fresh event. Per-alarm, shelving can be disabled entirely via `shelvingAllowed=false`.

### Alarm journal

Stores every status transition to a database (or locally, or forwarded to a remote Gateway's journal) — realtime in-memory alarm status is otherwise finite and volatile. Multiple Alarm Journal profiles can coexist on one Gateway, each with its own filters, so different alarm subsets can be routed to different journals.

Three profile types: **Database** (external DB connection), **Internal** (stored inside the Ignition install directory — pruning strongly recommended to avoid filling the disk), **Remote** (forwards local events to another Gateway's journal — useful for hub-and-spoke architectures; its own settings are `Gateway Name`/`Alarm Journal`, `Use Store and Forward` default true, `Max Group Size`).

Key settings (Database/Internal): `Query Only` (opt out of storage while still being usable elsewhere), `Minimum Priority` (default Low), `Store Shelved Events` (off by default), `Store Enabled & Disabled Events`; Event Data toggles `Static Config`/`Dynamic Config`/`Static Associated Data`/`Dynamic Associated Data`; three **Data Filters** (`Filter by Alarm Source`, `Filter by Display Path`, `Filter by Display Path or Source`) combine via **logical AND** — using all three at once is discouraged since an alarm failing *any one* filter is dropped entirely; `Enable Data Pruning` + `Prune Age`/`Units`; Advanced: `Table Name` (default `alarm_events`), `Event Data Table Name` (default `alarm_event_data`), `Use Store and Forward` (default true, Database type only).

**Table schema** — `alarm_events`: `id`, `eventid` (UUID grouping one active/clear/ack cycle), `source` (qualified path, e.g. `prov:X:/tag:Y:/alm:Z`), `display path`, `priority` (0–4), `eventtype` (0 Active/1 Clear/2 Acknowledged/4 Enabled/5 Disabled), `eventflags` (bitmask: bit0 System Event, bit1 Shelved Event, bit2 System Acknowledgement (auto-ack from Live Event Limit overflow), bit3 Acknowledged Event, bit4 Cleared Event, bit5 Enabled-state-changed), `eventtime`. `alarm_event_data`: `id` (FK), `propname`, `dtype` (0 int/1 float/2 string), `intvalue`/`floatvalue`/`strvalue`.

> ⚠️ **8.3 interop caution**: *"Due to serialization updates, 8.3 Gateways will not be able to store Alarm Journal data to a remote 8.1 Gateway."* Upgrade the central server hosting journal data to 8.3 **before** upgrading remote 8.1 Gateways that feed it.

### Alarming schedules

Two schedule shapes: **Standard** (per-day hour ranges, `All Days`/`Weekdays`/individual-day selection are mutually exclusive with each other but individual days combine freely; optional `Repeat/Alternate` N-days/weeks-on / N-off pattern anchored to a `Starting At` date — if Repeat is anything but Off and no start is given, the schedule is **never** active) and **Composite** (OR of two other schedules — active whenever either underlying schedule is active). Built-ins: **Always** (24/7) and an **Example** (Mon–Fri 8–5 with lunch break). Schedule evaluation uses **Gateway system time**, not the viewing user's local time. `Observe Holidays` (default true) suppresses activity on configured Holiday dates (`Name`, `Date` MM-DD-YYYY, `Repeat Annually` default true). A User Source's `Schedule Restricted` setting can additionally deny *login* outside the user's own active schedule window.

### Alarm expressions / bindings

Most alarm properties (Setpoint, Enabled, Priority, etc.) are bindable to a Tag, an Expression, or (inside a UDT) a **UDT Parameter**. Binding type is chosen per-property from the alarm's binding icon in the Tag Editor → Alarms section. Common uses: bind `Enabled` to a "machine running" tag or a `timeBetween(...)` expression to auto-enable/disable by shift; bind `Setpoint` to an operator-adjustable Memory tag for a runtime-changeable threshold. The `{this}` keyword, when used inside an *alarm* property expression, still refers to the **tag**, not the alarm — `{this.name}` on an alarm property returns the tag's name, not the alarm's.

---

## Alarm notification

Requires the **Alarm Notification module**, at least one **Notification Profile**, and at least one **Alarm Notification Pipeline**. SMS and Voice notification each need their own additional module (or a Twilio account, which needs the separate Twilio Notification module instead of physical hardware).

### Notification contact info

Users need contact info (email address, phone number, etc.) attached to their account before any profile can reach them — managed under Platform > Security > User Sources > (source) > Manage Users, in the user editor's **Contact** section (`Type` dropdown + `Value`). An optional **Security PIN** (Extended Properties) gates voice-notification authentication. Setting up a new user for alarm notification: Create User, fill in the standard identity fields, then Contact > Add, choose a delivery `Type`, enter the `Value`, and Save.

### Defining a Twilio account

Before any Twilio-backed profile (SMS/Voice/WhatsApp) can be created, a Twilio account must first be registered in Ignition: Services > Alarming > Twilio > Create Account, supplying `Name`, `Twilio Account Sid`, `Twilio Auth Token` (both from the Twilio console's Account Settings), an optional `Local Address` (pins outbound traffic to a specific local NIC), and, for two-way/inbound use, a `Public Hostname` + `Public Port`/`Public SSL Port` (+ optional backup-Gateway equivalents for redundancy) and `HTTPS Enabled`/`Inbound Validation Enabled` (cryptographically verifies inbound requests really came from Twilio). Ignition automatically retries a failed Twilio connection attempt. Because Twilio delivers two-way acknowledgements as inbound POSTs to the Gateway's web server, the Gateway must be reachable by Twilio's servers on port 80/443 — cloud-hosted Gateways usually already satisfy this, while on-premise installs typically need port forwarding or a cloud relay Gateway on the Gateway Network, which is why physical SMS/Voice modules are often preferred over Twilio for on-prem-only deployments.

### Pipelines

Pipelines are **global Gateway resources**, not part of any single project — created under the Designer's Project Browser **Global** node, editable from any project, and (unlike per-project resources) can pull in pipelines exposed by a connected **Remote Gateway**. A pipeline is a directed graph of blocks starting at a fixed, undeletable **Start block**; multiple inputs can feed one block, and loops (an output wired back to an earlier block's input) are legal but risky (e.g. can send unbounded repeat notifications).

**Event flow**: each alarm transition (Active/Clear/Ack) that names a pipeline in its `activePipeline`/`clearPipeline`/`ackPipeline` spawns a new alarm event at that pipeline's Start block. Multiple events can be in-flight concurrently; one event's progress never blocks another's. **Dropout conditions** (`Acknowledged`, `Cleared`, `Shelved` — evaluated pipeline-wide, default all three true) are re-checked at every block transition *and* mid-execution inside a Notification block (e.g., between individual roster members) — if a condition becomes true, the event exits immediately, wherever it is. Because the default dropout set includes Acknowledged/Cleared/Shelved, a pipeline invoked from the **Clear** or **Ack** event will itself immediately drop out at the Start block unless you specifically flip those dropout conditions off for that pipeline — "it is a good idea to have special 'cleared' or 'shelved' versions of any pipelines that will be called from these other events."

**Event instances / runtime properties**: an alarm event carries both its static alarm-configuration properties and pipeline-only **runtime properties** (created/updated via the Set Property block; never journaled). A **Splitter** block *branches* an event into independent instances, each with its own subsequent property mutations from that point forward, while later system-driven fields (e.g. acknowledgement) still propagate correctly to all branches.

**Pipeline lifecycle on edit**: saving a pipeline instantiates a fresh running instance; the previous instance is retired but keeps running any events it already had in flight — new events always go to the new instance.

Pipeline-level properties: `Dropout Condition` (Acknowledged/Cleared/Shelved, any combination), `Pipeline Enabled`.

**8.3 addition — Gateway Test button**: *"Ignition 8.3 includes a Test button for verifying alarm notifications directly from the Gateway."* Services > Alarming > Notification → Test, configure a target Pipeline + optional Display Path + Priority, Submit, then monitor via a live progress table (Source / Display Path / Block / Time in Block / Status / cancel control) — validates pipelines, profiles, and rosters end-to-end without needing a live alarm.

### Pipeline block types

| Block | Function |
|---|---|
| **Start** | Fixed entry point; undeletable. |
| **Notification** | Sends via a chosen Notification Profile + On-Call Roster (see below). Falls through to the next profile type listed if a contact lacks info for the first. |
| **Delay** | Blocks the event for N seconds (independently timed per event) — commonly used to give a dropout condition (e.g. Ack) time to become true before proceeding, or to pace an escalation. |
| **Splitter** | Forwards one event to *all* connected outputs concurrently (fan-out to multiple rosters/profiles at once). Uncontrolled use risks an exponential blow-up of concurrent event copies. |
| **Switch** | Evaluates a non-boolean expression, routes by matching against a defined value list, with a **Catch-all** fallback output. |
| **Expression** | Evaluates a boolean expression; routes True/False. Helper functions inside these expressions: `isActive()`, `isPropertyDefined("name")`, plus normal `{alarmProperty}` reference syntax and comparison/logical operators. Unconfigured outputs simply act as a filter (event silently drops there). |
| **Set Property** | Writes/updates a runtime property (often used as a loop counter, e.g. `coalesce({counter},0)+1`), scoped to the pipeline only — never journaled or shown in the status table. |
| **Jump** | Forwards the event to a *different named pipeline* — used to decompose a large escalation graph into smaller reusable pipelines. |
| **Script** | Runs arbitrary Python against a `ScriptableBlockPyAlarmEvent` object — e.g. writing to another tag, or a DB. |
| **Event Stream Source** | Emits the event (as an `AlarmEventObject`) into an Event Stream configured with an event-listener source. |

**Notification block — Contacts / roster resolution**, three modes:
- **Direct**: a hard-coded On-Call Roster.
- **Expression**: an expression (referencing alarm properties/associated data) that must resolve to a roster **name string** — quote the name (`"Operators"`) unless the expression body literally *is* just the bare roster name with nothing else (in which case unquoted text is tolerated as a fallback-parse of the roster name) — any expression with real logic *must* be quoted or it fails to parse and then gets misinterpreted as a literal (and likely nonexistent) roster name.
- **Calculated**: a script returning a list of contact dictionaries (`username`, `firstname`, `lastname`, `email:[...]`, `phone:[...]`, `sms:[...]`, `whatsapp:[...]`, `extraProps:{...}` for arbitrary user properties like `language` or a per-notification-module `user.pin`), or built via a fluent `builder.username(...).email([...]).add()...build()` API. Contacts here **need not exist** as real Gateway users — useful for building rosters dynamically from an external DB query.
- `Ignore User Schedules` (Direct/Expression only) forces notification even to off-shift users — caution: if their User Source is `Schedule Restricted`, they'll be notified but unable to log in to act on it until their shift starts.

**Consolidation** (email/SMS/Twilio profiles): `Delay` (pause after the first eligible alarm to catch a burst arriving together) + `Frequency` (max send rate afterward, to avoid re-notifying a flapping alarm too often). Consolidated messages use double-brace `{{ }}` repeat-block syntax (not a real expression — string literals need no quoting) and expose `{alarmEvents.Count}`, `{alarmEvents.MaxPriority}`, `{alarmEvents.MinPriority}` in addition to normal single-alarm properties. HTML formatting: lead the message with `<html>` (no closing tag required) — but note this suppresses the profile's automatic line breaks, so add `<br>` explicitly.

**Message property reference** (available inside Notification block message fields via `{propertyName}`, with optional format like `{eventTime|hh:mm:ss}`): `displayPath`, `displayPathOrSource`, `name`, `priority`, `source`, `ackTime`, `ackUser`, `ackUserName`, `isAcked`, `activeTime`, `isActive`, `clearTime`, `isClear`, `state`, `eventState`, `eventTime`, `eventValue`, `isShelved`, plus the consolidation-only `AlarmEvents.Count/MaxPriority/MinPriority`.

### On-call rosters

A named, **ordered** list of users (Services > Alarming > Rosters); statically defined and not editable from within a pipeline (only a Calculated roster can build an ad-hoc list at runtime). At notification time, the roster is filtered down to only users whose individual **schedule** is currently active (unless `Ignore User Schedules` is set). Manageable from the Gateway or from a Vision **Roster Management** component (add/remove/reorder users, select User Source).

### Notification profile types

| Profile | Delivery | Key settings |
|---|---|---|
| **Email Notification** | 1-way or 2-way email | SMTP settings (or `Use SMTP Profile` to reuse a Gateway SMTP profile), `Two-way Enabled` (adds an ack link into the email body), optional **POP3 two-way** (ack via email *reply*, syntax `Pop3AckId:<systemId>:<ackId>` in the body — works even as an empty reply besides that line), `Debug Mode Enabled` (logs SMTP session to wrapper.log), `STARTTLS Enabled`. |
| **Simple One-Way Email Notification** | 1-way only, no pipeline needed | Listens directly for active alarms within a `Minimum Priority`–`Maximum Priority` range and notifies a single fixed On-Call Roster; supports its own `Consolidation Enabled`/`Delay`/`Frequency`. No ack links at all — simplest possible email path. |
| **SMS Notification** | Cellular via AirLink modem | Officially supported: RV50/RV50X, RV55, LX40. `Send Port`/`Receive Port` (default 17341/17342) + optional backup modem pair for redundant Gateways. `Two-way Enabled` + `Numeric Only Ack Code`. One modem can serve multiple Gateways in one-way mode, but only one Gateway may receive two-way replies from it. |
| **Voice Notification (VOIP/SIP)** | SIP/VOIP phone call | Requires a separate Voice Notification module **and** at least one TTS voice module (voices: Katherine/EN, Laura/IT, Sara/ES, Suzanne/FR, Alex/DE). SIP Gateway address/account/password, `Answer Timeout` (default 60s), `Max Call Duration` (default 5 min), `Use Fair Scheduling` (one call per job at a time), ports (SIP 5060 default, RTP 8000 default). Supports **Notification Security PIN** per user (Platform > Security > User Sources → user's Security PIN field) to gate acknowledgement/hearing the message; enabled via `Require PIN` on the profile. Voice Notification Scripts (per-language TTS phrase sets) are plain spoken text, not executable code. |
| **Twilio SMS / Voice / WhatsApp** | Cloud (Twilio) | No hardware; Gateway needs internet + a Twilio account (SID/Auth Token) defined once under **Alarming > Twilio**, then referenced by each profile. Public inbound webhook config (`Public Hostname`/Port/SSL Port, HTTPS toggle, inbound signature validation) is required for two-way ack via SMS reply or phone keypress — the Gateway must be reachable by Twilio's servers on port 80/443. Twilio Voice adds `Broadcast Notifications` (call the whole roster at once, **bypassing** PIN auth and per-user ack — i.e. unauthenticated by default even though it may speak sensitive alarm content), `Record Calls` (recordings land in the Twilio dashboard), configurable `Call Script` phrase set (Greeting/PIN Challenge/Summary/Active Message/Clear Message/Ack options/Closing, each overridable, with `{propertyName}` substitution). Twilio WhatsApp requires a pre-approved **Template** for the first outbound contact (free-text only opens up for 24h after the user replies) and a `WhatsApp Service SID`; user contact type must be set to **WhatsApp SMS**. All three Twilio profiles fault as "Missing Dependency" if the core Alarm Notification module isn't installed/enabled. |
| **Remote Gateway Notification** | Delegates to another Gateway | Lets a Gateway lacking SMTP/telephony infrastructure trigger a notification profile *hosted on a different Gateway* over the Gateway Network — the remote Gateway does the actual sending; only it needs the delivery-specific module installed. `Retry Delay` (default 10000ms) and `Max Queued Alarm Transitions` (default 10000) govern resilience while the remote Gateway is unreachable. Assigned to alarms the same way as a local pipeline, from the Tag Editor's Notification Settings (targets show as `RemoteName/PipelineName`). |

### Worked pipeline patterns

- **Simple pipeline**: Start → Notification block (profile + roster set). The most basic possible pipeline — notify immediately, once, when the alarm goes active. Created under the Designer's Alarm Notification Pipelines node; a pipeline does nothing until an alarm's `activePipeline`/`clearPipeline`/`ackPipeline` actually references it.
- **Filter on alarm priority**: Expression block testing `toInt({priority})` (or the Alarm Properties picker's `Priority` placeholder) against numeric priority values (Diagnostic 0 / Low 1 / Medium 2 / High 3 / Critical 4) — True/False outputs feed separate Notification blocks pointed at different rosters (e.g. a `Critical` vs `NonCritical` on-call roster), so priority alone determines who is paged. A Switch block is the equivalent choice when there are more than two priority buckets to split on.
- **Filter on alarm associated data**: after adding associated data (e.g. a `Group` property with values `Group A`/`Group B`) to an alarm, drag in a Switch block and enter the associated-data placeholder in curly braces (e.g. `{Group}` — it won't appear in the binding dropdown, must be typed manually) as the switched expression; add one output value per group plus the automatic Catch-all, then wire each output to its own Notification block/roster.
- **Simple loop**: Notification block → Delay block, with the Delay block's `OUT` wired back to the Notification block's `IN` (default dropout conditions — Acknowledged/Cleared/Shelved — left enabled) — repeats indefinitely (notify, wait N seconds, notify again...) until the alarm meets a dropout condition. Combine with escalation (jump to a different pipeline after N loops) rather than looping forever unconditionally.

### Escalation and the two-way ack flow

A canonical escalation pattern (from the docs' worked example): `Set Property(numCalls=0)` → `Notification(Operators)` → `Delay(300s)` → `Set Property(numCalls={numCalls}+1)` → `Expression(numCalls<3)` — True loops back to the Operators Notification block, False routes to a second `Notification(Managers)` block. A **Jump** block to a separate "Escalate" pipeline is offered as a cleaner alternative to nesting a second Notification block directly.

Two-way acknowledgement mechanics differ by channel: **Email** — click an ack link in the message body (or, for POP3, reply with the `Pop3AckId:` syntax) which lands on a web landing page where notes can optionally be required before clicking Acknowledge; consolidated notifications can present multiple alarms on one landing page. **SMS** — reply with the code substituted for `%s` in the profile's `Acknowledge Message`. **Voice** — press a configured DTMF key (default option 1) after optionally entering a security PIN; Twilio Voice additionally supports fully unauthenticated **broadcast** delivery that skips both PIN and per-call ack.

---

## Gotchas and 8.3 notes

Marked **NEW**, **CHANGED**, or a **TRAP** where the doc content makes the distinction explicit or strongly implied; unmarked items are general operational pitfalls worth knowing regardless of version.

- **NEW (8.3.4)** — **Wildcards in tag paths**: `*` (one path segment), `**` (any number of intermediate folders), `?`/`??`/... (fixed-length character matches) are now accepted in Gateway Event **Tag Change Script** paths and the Event Streams **Tag Event** source, at *both* the folder and tag-name level (folder-level wildcarding already existed for Tag Change Scripts; tag-level is what's new). Patterns cannot be validated at edit time ("Glob pattern detected, unable to validate") — they're resolved against the live tag tree on the Gateway at runtime, and each matched tag produces its own event downstream (docs cite verified behavior against a 10,000-tag folder with no subscription issues, but note you should design for the resulting fan-out same as explicit subscriptions).
- **NEW (8.3.9)** — UDT **Multi-Instance Wizard** gained a **List of Names** Pattern Type for reference tokens (previously only Numeric/Alpha Upper/Alpha Lower).
- **NEW (8.3.4)** — **Core Historian** auto-creates `server.conf`/`log.conf` on creation, letting Cairo/WAL/HTTP/PG-wire/RAM/logging/Materialized-View/Metrics settings be tuned per-historian; `server.conf` now **supersedes** the older system-properties approach (though legacy system properties still override on conflict, for backward compatibility).
- **CHANGED — Historian architecture**: the historian is now explicitly a multi-provider system under a "Historian Core module," headlined by the new **QuestDB-based Core Historian** (WAL writes, no Store-and-Forward, native aggregation/dedup/archiving) as the modern embedded default, with the prior SQLite-based embedded historian re-labeled **"Internal Historian (Legacy)."** The SQL Historian (external DB) continues to exist alongside both, still with its own pre-processed-partitions/pruning/stale-detection feature set — those are **not** available on the Core Historian.
- **CHANGED — Historian scripting API**: `system.historian.*` (queryValues / storeDataPoints / queryMetadata / storeAnnotations / queryRawPoints / queryAggregatedPoints) is the current interface. Legacy `system.tag.queryTagHistory` / `system.tag.queryTagCalculations` and **Custom Tag History Aggregates are deprecated** — old projects keep working, but new development should not use them, and they're the only path that engages SQL Historian **pre-processed partitions**.
- **CHANGED (interop trap)** — **Remote Alarm Journals**: "8.3 Gateways will not be able to store Alarm Journal data to a remote 8.1 Gateway" due to serialization changes. When mixing versions in a hub-and-spoke deployment, upgrade the central/hub Gateway to 8.3 *before* upgrading remote spokes that write into its journal.
- **TRAP — cross-version tag editing**: "8.3 tags cannot be edited by 8.1 systems" — attempting to open an 8.3 tag's editor from an 8.1 Designer throws an error. Plan Designer/Gateway version alignment carefully during a staged 8.1→8.3 rollout.
- **NEW-ish (8.3 Gateway UX)** — a **Test** button under Services > Alarming > Notification lets you fire a synthetic alarm event at a chosen pipeline/priority/display-path directly from the Gateway webpage, with a live per-event progress table — no need to trip a real alarm to validate profile/roster/pipeline wiring end to end.
- **TRAP — Historian deadband style vs. engine**: using the **Analog** deadband style against the **Core Historian** is explicitly flagged as potentially taxing on I/O/performance due to out-of-order writes; prefer Discrete, or Periodic sampling with deadband off, on Core Historian tags.
- **TRAP — UDT rename**: renaming a UDT Definition after instances exist orphans those instances (their `typeId` link breaks); the docs explicitly advise against renaming a Definition post-instantiation unless you're prepared to repoint every instance.
- **TRAP — UDT import collision policy**: the default **Overwrite** collision policy on a UDT Definition import silently *deletes* any member not present in the import file; use **MergeOverwrite** for a non-destructive patch.
- **TRAP — Alarm Ack Mode = Unused**: this setting causes the alarm to never enter any pipeline at all (because the default dropout conditions include "Acknowledged," and an Unused-mode alarm's events are always already-acked) — you must separately uncheck the Acknowledged dropout condition on the target pipeline to still get notifications.
- **TRAP — pipeline dropout defaults on non-Active entry points**: a pipeline invoked from the Clear or Ack alarm event immediately drops out at the Start block under default dropout settings (Cleared/Acknowledged both default to "drop out on true") — build dedicated Clear/Ack variant pipelines with those specific dropout conditions turned off.
- **TRAP — Notification-block Expression roster names**: unquoted roster names only work by accident (a failed expression parse falls back to treating the raw text as a literal roster name); any expression with real logic (`if(...)`, comparisons, etc.) *must* quote the roster name string or it fails silently by targeting a nonexistent roster.
- **TRAP — Twilio Voice broadcast mode**: `Broadcast Notifications Enabled` bypasses both PIN authentication and per-user acknowledgement, delivering potentially sensitive alarm content to an entire roster with no authentication at all — the docs recommend it mainly as a fallback when no valid inbound public hostname is configured for two-way use.
- **TRAP — Associated Data typing**: all associated-data values are stored and returned as **strings**, always — any numeric/boolean comparisons in scripts or expressions need explicit type-casting, even though the Tag Editor lets you pick a value that "looks" numeric.
- **TRAP — Dataset and Document tag types**: unsupported by both the **Alarming** system and the **Tag Historian** — don't build alarm or history requirements around either type; they're best reserved for Memory/Query tags feeding tables/JSON viewers directly.
- **TRAP — Scan-class/Tag-Group Rate = 0**: a `0` Rate doesn't mean "as fast as possible," it means the group **never executes** — used deliberately for Driven/Leased "idle" states, but a common misconfiguration trap if applied to a Direct group.
- **TRAP — Leased Tag Groups and the Tag Browser**: merely *viewing* a leased tag in the Tag Browser does **not** trigger the Leased/Driven rate — only an actual component binding in an open Designer/Client/Session does.
- Reminder that Historian sample/deadband settings on a **Tag Group** (when a tag's Sample Mode = Tag Group) only override the tag's own Max-Time-Between-Samples setting when the Tag Group itself uses *non-default* values — otherwise the tag-level setting wins.
