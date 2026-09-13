> **Skill level:** 300 · **Read first:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 28-PLATFORM-TRANSACTIONS-SFCS

# Ignition 8.3: Transaction Groups & Sequential Function Charts (SFCs)

**Date:** 2026-07-13, corrected 2026-08-15 | **Source:** docs.inductiveautomation.com/docs/8.3/ for the general prose, install-verified bytecode for the resource-format and API sections flagged as such | **Module:** SQL Bridge + SFC Module

---

## 1. Transaction Groups: Purpose, Configuration & Execution

### Purpose
Transaction Groups are the core execution engines of the SQL Bridge module. They perform event-driven database operations including:
- **Historical data logging** - Store tag values to database with synchronized timestamps
- **Database-to-device synchronization** - Pull data from database and write to OPC items
- **Recipe management** - Load/store recipe values from tags to database
- **Status tables** - Maintain current state of devices/processes

### Key Difference from Tag History
| Aspect | Transaction Groups | Tag History |
|--------|-------------------|------------|
| **Trigger** | Event-based (discrete triggers) | Continuous asynchronous |
| **Storage** | Single SQL transaction for all items | Independent per-tag timing |
| **Timestamp** | Grouped (all items per trigger) | Individual per tag |
| **Table Structure** | User-defined, flexible schema | Fixed tall-format with partitioning |
| **Best For** | Discrete manufacturing, batch processes | Continuous monitoring/trending |

### Configuration Elements
- **Execution Trigger:** User-defined item state controls group execution
- **Handshake Mechanism:** Success/failure response handling
- **Timestamp/Quality:** Optional timestamp and quality code storage
- **Expression Items:** Calculated values at execution time
- **WHERE Clauses:** Custom conditions for row updates/inserts

### Real config keys (verified against bytecode, 8.3.7)

No Transaction Group resource exists anywhere on this install to inspect directly - grounded in `com.inductiveautomation.factorysql.*` classes inside `data\jar-cache\com.inductiveautomation.sqlbridge\*-common-11.3.7.jar` / `*-gateway-11.3.7.jar` (SQL Bridge still uses the legacy FactorySQL package name internally). Uses the standard Ignition resource-wrapper system, same `resource.json` pattern as other project resources.

**The open question in the line above is closed: the payload is XML, not JSON.** Confirmed 2026-08-15 by reading the actual load path in `ProjectRunner.loadGroupResource()`: `Resource.getData() -> byte[] -> XMLDeserializer.deserialize(...) -> checkcast GroupConfig`. `XMLDeserializer` here is `com.inductiveautomation.ignition.common.xmlserialization.deserialization.XMLDeserializer` - the same generic platform object-serialization framework used by the Reporting module's report resources (see [72-REPORTING-SHAPE-MODEL.md](72-REPORTING-SHAPE-MODEL.md) for how that framework actually works). No Gson/JSON string constant exists anywhere in the sqlbridge jars - confirmed by search, zero hits. `GroupConfig extends BasicConfigObject implements Serializable` (`typeKey: String`, `properties: MetaPropertyCollection`), and the key literal strings inside `MetaPropertyCollection` are confirmed identical to the Java constant names below (`CommonGroupProperties`'s `WellKnownMetaProperty<>("DATA_SOURCE", ...)` etc use the same literal as the field name - no camelCase translation at this layer). The exact XML tag names the generic serializer emits were not re-derived from the shared `xmlserialization` package directly - but a real example was found and decoded instead, see below, which closes this gap the practical way.

Also newly confirmed: `TIMESTAMP_COLUMN` default = `t_stamp`, `QUALITY_COLUMN` default = `quality_code`, `BLOCKID_COLUMN` default = `block_id`, `ROWID_COLUMN` default = `row_id`. `AUTO_CREATE_TABLE` is a real `Boolean` property - a group can create its own destination table, it does not need to pre-exist (exact DDL generated not verified). `CONFIGURED_ITEMS` entries are `ItemConfig` (same `typeKey`/`properties` shape as the group); the real keys for a plain tag-to-column item are `NAME`, `DRIVING_TAG_PATH`, `TARGET_NAME`, `TARGET_TYPE` (confirmed enum `ItemTargetTypes`: `NONE` / `DB_FIELD` / `TAG`), `TARGET_DATA_TYPE`.

### Real `data.bin` structure, decoded from a live example - Inductive Automation's own IADemo reference project

`GroupConfig` (`com.inductiveautomation.factorysql.common.config.GroupConfig`) is a thin object: `path` (String, folder path), `properties` (`MetaPropertyCollection`), `typeKey` (String, e.g. `"standard"`). `MetaPropertyCollection` wraps a `Map<String, TypedMetaProperty>` - one `TypedMetaProperty` per group setting, each holding just `name` + `value`. This confirms the keys really are the flat literal strings already listed above (`TABLE_NAME`, `TRIGGER_PATH`, `NAME`, etc), used directly as the map key.

**A real, working `History on Trigger` group example**, decoded in full:
- `typeKey = "standard"`, `NAME = "History on Trigger"`, `TABLE_NAME = "txn_sample"`
- `TRIGGER_MODE = NotEqualZero` (real enum value, confirmed), `TRIGGER_PATH`, `HANDSHAKE_PATH`, and `FAILURE_HANDSHAKE_PATH` all pointed at the *same* tag path in this example (`"Transaction Group/Trigger"`) - a single boolean trigger tag doing triple duty.
- `GROUP_EXECUTION_FLAGS = 210` (int - a real bitmask property not previously documented; exact bit meanings not decoded).
- `EXECUTION_ENABLED = true`, `DELETE_OLD_RECORDS = true` (both real Boolean properties).
- **The trigger tag is also modeled as its own `CONFIGURED_ITEMS` entry** - one more `ItemConfig` beyond the actual data-carrying ones, with `DRIVING_TAG_PATH` = the same trigger tag path, `TARGET_TYPE = NONE` (confirmed real enum value - "don't write this one to a column"), `NAME = "Trigger"`. So a group with 4 real data items shows 5 `CONFIGURED_ITEMS` entries - the trigger is always one of them, not a separate hidden mechanism.
- Each real data item's `typeKey = "grouptag_sqltref"` (confirmed real - a plain tag-sourced item), with `DRIVING_TAG_PATH` (e.g. `"Dairy/fillLevel"`), `TARGET_NAME` (destination column, e.g. `"fillLevel"`), `TARGET_DATA_TYPE` (enum `DataType`, e.g. `Int4`, `Boolean`).
- No `DATA_SOURCE` key was present in this example at all - likely omitted-when-using-project-default rather than always-required.

**Write path proven, not just plausible.** Built a real 16-item Standard group (`AHU_OEE_Log`, 4 AHUs x Availability/Performance/Quality/OEE, `FinancialPlanner` connection, `RATE`/5-minute execution, `AUTO_CREATE_TABLE`) via `GroupConfig`/`ItemConfig` real setters - `setPropertyValue(WellKnownMetaProperty<T>, T)` on `BasicConfigObject`, using the real constants from `CommonGroupProperties`/`CommonItemProperties` (no manual `MetaPropertyCollection` construction needed, the property system handles that internally) - then `XMLSerializer.serializeAndGZip(group)`. Decoded the result back before deploying: every item, every group setting round-tripped exactly as set. `ItemConfig.SQLTAG_GROUPTAG_ID` (`"grouptag_sqltref"`) is the real constant for a plain tag-sourced item - use it instead of a string literal. Group-level `NAME` has no `WellKnownMetaProperty` constant; use the inherited `BasicConfigObject.setName(String)` instead (it populates the same underlying property, just via a different method than the typed items use).

- Group **type** registry (`GroupTypeRegistry`) - real type-key strings: `standard` (Standard Group), `storedprocedure` (Stored Proc Group), `block` (Block Group), `historical` (Historical Group).
- Record mode (`REC_MODE`, enum `RecordMode`): `INSERT_ALL` / `INSERT_CHANGED` / `UPDATE` - this is the real "read/write" concept, not a separate mode.
- Execution schedule (`EXECUTION_SCHEDULE_MODE`, enum `ExecutionScheduleMode`): `RATE` (periodic, paired with `UPDATE_RATE`/`UPDATE_UNITS`) / `SCHEDULE` (paired with `RUN_SCHEDULE`).
- Value-based triggering: `TRIGGER_PATH` (the bound tag) + comparison enum `TriggerMode`: `NotEqualZero` / `EqualsZero` / `Custom` / `AnyChange`. There's no separate "periodic vs. OPC vs. tag-change" enum - periodicity is `ExecutionScheduleMode.RATE`, tag-change triggering is just binding `TRIGGER_PATH`.
- Other real keys: `DATA_SOURCE`, `TABLE_NAME`, `WHERE_CLAUSE`, `CONFIGURED_ITEMS`, `KEY_VALUE_BINDINGS`, `GUID`, `STORE_TIMESTAMP`/`TIMESTAMP_COLUMN`, `STORE_QUALITY`/`QUALITY_COLUMN`, `HANDSHAKE_PATH`/`HANDSHAKE_VALUE`, `FAILURE_HANDSHAKE_PATH`/`FAILURE_HANDSHAKE_VALUE`, `DELETE_OLD_RECORDS`/`DELETE_RECORDS_TIME`/`DELETE_RECORDS_UNITS`.

---

## 2. Transaction Group Types: Standard vs. Queued Groups

Ignition 8.3 provides **four main types** of transaction groups:

### Standard Group (Most Flexible)
```
Data Flow: Bidirectional (↔)
┌─────────────────────────────────────┐
│  Tags ↔ Database                    │
│  - Update or insert rows             │
│  - Read data back to items           │
│  - Custom WHERE clause support       │
│  - Flexible two-way sync             │
└─────────────────────────────────────┘
```
- **Use Cases:** Historical logging, PLC sync, recipe management, status tables
- **Operations:** INSERT, UPDATE, DELETE with flexible control
- **Key Feature:** Values can flow FROM database TO items or vice versa

### Historical Group (Write-Only)
```
Data Flow: One-way (→ Database only)
┌─────────────────────────────────────┐
│  Tags → Database                    │
│  - Insert records only               │
│  - No update/delete capability       │
│  - No write-back to items            │
│  - Simple logging                    │
└─────────────────────────────────────┘
```
- **Use Cases:** Basic historical logging, shift tracking
- **Operations:** INSERT only
- **Limitation:** Cannot update existing rows or write values back

### Block Group (Vertical Storage)
```
Data Storage Format:
┌──────────────────────────┐
│ Item    │ Timestamp │ Value │
├──────────────────────────┤
│ Item_A  │ T1        │ V1    │
│ Item_B  │ T1        │ V2    │
│ Item_C  │ T1        │ V3    │
│ Item_A  │ T2        │ V4    │
└──────────────────────────┘
```
- **Use Cases:** Array mirroring, massive datasets, recipe storage
- **Format:** Tall/vertical layout (rows per item per timestamp)
- **Key Feature:** Efficient for large data volumes

### Stored Procedure Group (Parameter-Based)
```
Flow: Items ↔ Stored Procedure
┌─────────────────────────────────────┐
│  Item → SP Input Parameter          │
│  SP Output Parameter → Item         │
│  Item ↔ Input/Output Parameter      │
└─────────────────────────────────────┘
```
- **Use Cases:** Stored procedure execution, legacy system integration
- **Mapping:** Items bind to IN, OUT, or IN/OUT parameters
- **Popular For:** RSSQL migration

---

## 3. Sequential Function Charts (SFCs): Creation, States & Transitions

### What is an SFC?
A Sequential Function Chart is a graphical programming language (IEC 61131-1 standard) built into Ignition that:
- Executes as a series of scripts in sequential order
- Runs on the Gateway (independent of clients)
- Uses Python + Expression language for flexibility
- Supports multiple concurrent instances with isolated scopes

**Resource format, confirmed against three real examples (2026-08-15) - Inductive Automation's own IADemo reference project's `SFC Loop`, `SFC Control`, and `Batch Process` charts.** `sfc.xml` is genuinely plain, human-readable XML - not gzip'd, not routed through `ignition.common.xmlserialization` like Transaction Groups and Alarm Pipelines are. `RESOURCE_NAME = "sfc.xml"` (bytecode constant, now doubly confirmed - filename matches exactly). A complete real chart (`SFC Loop`):

```xml
<sfc zoom="1.0" canvas="8 10" execution-mode="Callable" hot-editable="false" persist-state="true" redundant-sync="false">
  <step id="<uuid>" location="5 1" name="__begin" factory-id="begin-step">
    <parameters>
      <parameter><name>counter</name><expression>0</expression></parameter>
      <parameter key="true"><name>max</name><expression>1</expression></parameter>
    </parameters>
  </step>
  <step id="<uuid>" location="5 3" name="Increment" factory-id="action-step">
    <notes>Add one to the chart variable</notes>
    <start-script>def onStart(chart, step):
	import time
	time.sleep(1)
	chart.counter += 1</start-script>
  </step>
  <step id="<uuid>" location="4 7" name="__end1" factory-id="end-step" />
  <transition id="<uuid>" location="4 5">{counter}&gt;={max}</transition>
  <transition id="<uuid>" location="5 5">{counter}&lt;{max}</transition>
  <link id="<uuid>" location="5 2"><up/><left/><down/><right/></link>
  <!-- more <link> elements filling the remaining grid cells between steps -->
</sfc>
```

Confirmed real, closing every gap the earlier bytecode-only pass left open:

- **`canvas="8 10"` and every `location="col row"` are grid cells, not pixels.** `<link>` elements are the actual connectivity mechanism - each occupies one grid cell and declares which of its four sides (`<up/>`, `<left/>`, `<down/>`, `<right/>`) connect to a neighboring cell. A chart's wiring is a path of link segments threading between steps/transitions on the grid, not an ID-referencing `outputId`-style graph (unlike Transaction Groups and Alarm Pipelines, which do use UUID references). This is genuinely a different connectivity model per resource type - don't assume one pattern generalizes.
- **`begin-step` parameters confirmed exactly**: `<parameters><parameter [key="true"]><name>...</name><expression>...</expression></parameter>...</parameters>` - the `key="true"` attribute (only present when true) is what the earlier research called the "key param" - the doc text's "optional chart instance identifier" claim.
- **`action-step` scripts keep their full signature** - `<start-script>def onStart(chart, step):` with the `def` line intact, body tab-indented beneath it. **This is the opposite convention from Alarm Pipeline Script blocks**, which strip the `def handleAlarm(self, event):` line entirely and store body-only. Two resource types, two different script-storage conventions - always check per-type, don't assume one holds everywhere.
- **Transitions are plain text expression content** inside the element (`{counter}>={max}`), not an attribute - matches the general chart-variable-in-braces syntax already documented, now confirmed real.
- **Equality is a single `=`, not `==`.** `SFC Control`'s real transitions use `{path} = 1` / `{path} = 2` - this is the SFC expression language, not Python. Confirmed by mistake once already: a hand-authored chart used `{step1Done}==1` despite the correct `=` syntax being visible in an already-decoded reference example one section up - the lesson isn't "this syntax is unverified," it's "cross-check your own new content against evidence already in hand, not just against general expectations." `>=`/`<` (from `SFC Loop`) still use their normal form - only equality is single-`=`.
- `end-step` can self-close with no children when it has no `OUTPUTS`.

Given the format turned out to be plain, simple, readable XML with no fragile generic-serialization layer underneath, **hand-authoring `sfc.xml` is a much lower-risk proposition than Transaction Groups or Alarm Pipelines** - closer to the Perspective `view.json` case than the Reporting case.

**Even better ground truth than a demo project: Ignition ships its own canonical scaffold.** `sfc-common-6.3.7.jar` bundles `templates/callable.xml` and `templates/run-always.xml` - the literal files the Designer instantiates when you create a new chart of that execution mode. `callable.xml` in full:

```xml
<sfc zoom="1.0" canvas="20 20" execution-mode="Callable" hot-editable="false" persist-state="true" redundant-sync="false">
  <step id="<uuid>" location="5 1" name="__begin" factory-id="begin-step" />
  <step id="<uuid>" location="5 3" name="S1" factory-id="action-step" />
  <step id="<uuid>" location="5 6" name="__end1" factory-id="end-step" />
  <transition id="<uuid>" location="5 4">true</transition>
  <link id="<uuid>" location="5 2"><up/><down/></link>
  <link id="<uuid>" location="5 5"><up/><down/></link>
</sfc>
```

This confirms `begin-step` has no children at all when it has no parameters (`<parameters>` is only present when parameters exist, not a required empty tag), and that a **bare `true` is valid unconditional transition content** - useful for a transition that should just always pass through rather than checking a chart variable. Built and deployed a real 3-step chart (`AHU_Startup_Sequence` - enable system, wait, start fan, wait, hand to Auto mode) matching this exact skeleton extended to 3 action steps, cross-checked against both this canonical template and the three demo-project examples before deploying.

### Chart Lifecycle & States

```
┌──────────────┐
│ Begin Step   │  Initialize parameters
└──────┬───────┘
       │
   ┌───▼────────────────────┐
   │ Action Step 1          │  Execution Phase
   │ (On Start/Timer/OnStop)│
   └───┬───────────────────┘
       │
   ┌───▼──────────────┐
   │ Transition 1     │  Boolean
   │ (Condition?)     │  Check
   └───┬──────────────┘
       │
   ┌───▼──────────────┐
   │ Action Step 2    │
   └───┬──────────────┘
       │
   ┌───▼──────────────┐
   │ End Step         │  Termination
   └──────────────────┘
```

**Chart state enum (verified 2026-08-15, corrects an earlier wrong "1-10" claim in this doc).** Confirmed two independent ways: the Java class `com.inductiveautomation.sfc.ChartStateEnum` and the wire-protocol `chart_state_enum.proto` (which itself comments `// com.inductiveautomation.sfc.ChartStateEnum`). Real values, 15 total, 0-indexed:

| # | State | # | State | # | State |
|---|---|---|---|---|---|
| 0 | Aborted | 5 | InitPaused | 10 | Starting |
| 1 | Aborting | 6 | Paused | 11 | Stopped |
| 2 | Canceled | 7 | Pausing | 12 | Stopping |
| 3 | Canceling | 8 | Resuming | 13 | Suspended |
| 4 | Initial | 9 | Running | 14 | RedundantInactive |

There is no `Error` state. A separate, different enum (`ElementStateEnumPb`) tracks per-element (not per-chart) runtime state: `Aborting, Aborted, Activating, Active, Deactivating, Inactive, Pausing, Paused, Resuming, Cancelling, Canceled` (0-10) - don't conflate the two.

### Built-in Chart Variables
```python
chart.instanceId      # Unique identifier (UUID string)
chart.startTime       # java.util.Date initialization time
chart.runningTime     # Duration in seconds (float)
chart.state           # Current state code (0-14)
chart.running         # Boolean status
```

### Chart Parameters (Begin Step)
- Defined in Begin step
- Accessible throughout chart scope
- Optional default values
- **Key Param:** Optional chart instance identifier (e.g., product VIN)
- **Limitation:** Cannot store entire QualifiedValue objects (individual fields OK)

### Transitions & Flow Control
```
Transition Syntax:
┌─────────────────────────────────┐
│ {variable1} > {variable2}       │  Chart variables in {}
│ {counter} >= 10                 │  Expression language
│ {mode} == "RUN" && {temp} < 50  │  Logical operators
│ timeout() [Optional timeout]    │  After elapsed time
└─────────────────────────────────┘
```
- **When True:** Flow advances to next step
- **When False:** Flow blocked, waiting at current step
- **Timeout Transitions:** Set flags after elapsed milliseconds

### Reserved Words (Avoid as Variable Names)
```python
keys, values, items, get, clear, copy, update
# These conflict with Python dictionary methods
```

---

## 4. SFC Execution & Monitoring

### Chart Types
Real confirmed enum `ChartExecutionMode`: `Callable`, `RunAlways`, `Disabled`. ("Run-Always" below is written as two words for readability; the actual enum constant is `RunAlways`.)
1. **Callable Charts** - Called from scripts/transitions, return values
2. **Run-Always Charts** - Continuous execution on gateway

### Execution Model

**`system.sfc.runChart` does not exist - it was invented prose in an earlier version of this doc, disproven 2026-08-15.** Confirmed real functions, from `SfcScriptingFunctionsPyWrapper` in `sfc-common-6.3.7.jar` (namespace registration string confirmed as `"sfc"`, so the real root is `system.sfc`):

```python
system.sfc.startChart(chartPath, parameters)                    # current project, returns instance id (str)
system.sfc.startChart(projectName, chartPath, parameters)       # explicit project
system.sfc.getRunningCharts()
system.sfc.getRunningCharts(chartPath)                          # -> Dataset
system.sfc.cancelChart(instanceId)
system.sfc.pauseChart(instanceId)
system.sfc.resumeChart(instanceId)
system.sfc.getVariables(instanceId)                              # -> PyChartScope, has an "activeSteps" key
system.sfc.setVariable(instanceId, variableName, value)
system.sfc.setVariable(instanceId, stepId, variableName, value)
system.sfc.setVariables(instanceId, dict)
system.sfc.setVariables(instanceId, stepId, dict)
system.sfc.redundantCheckpoint(instanceId)
```

`parameters` is a plain dict, matched against the Begin step's `ExpressionParam` names - dict values win over the Begin step's own defaults.

```
Chart Instance Creation:
┌──────────────────────────────────────────┐
│ script: system.sfc.startChart(            │
│   "MyChart",                              │
│   {"partNumber": "ABC123"}                │
│ )                                         │
└──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Gateway-Side Execution (Independent)    │
│ - Isolated scope per instance            │
│ - Variables persist across steps         │
│ - Timer actions run at intervals         │
│ - On Start (blocking)                    │
│ - Timer (repeated)                       │
│ - On Stop (before transition)            │
└──────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│ Return to Calling Script                │
│ (For callable charts only)               │
└──────────────────────────────────────────┘
```

### Step Action Lifecycle

| Action Type | When | Blocking | Purpose |
|-------------|------|----------|---------|
| **On Start** | Step entered | YES | Initialize step state |
| **Timer** | After On Start (repeats) | NO | Periodic checks/updates |
| **On Stop** | Before exiting step | YES | Cleanup/finalization |
| **Error Handler** | Exception caught | YES | Exception management |

### Monitoring & Debugging

#### Designer Interface
1. Open the chart in Designer
2. Running instances appear in **Chart Control** list (right side)
3. Double-click instance to monitor → view real-time state
4. Element legend shows current states visually
5. Click banner to return to design mode

#### Vision Client Component
```
SFC Monitor (Admin category in Vision)
├── Option 1: Pick-list (select instance from dropdown)
└── Option 2: Fixed instance ID (hide pick-list)
    • Shows current step/action
    • Displays transitions
    • Real-time state indicator
```

### State Visualization
- **Highlighted elements:** Currently active
- **Completed elements:** Previous steps
- **Waiting elements:** Blocked at transition
- **Error indicators:** Exception state

---

## 5. Error Handling & Common SFC Patterns

### Error Handling in SFCs

#### Error Handler Actions
```python
# Define in Action Step's "Error Handler" script
# Automatically triggered on exception in On Start/Timer/OnStop

try:
    # Action code
except:
    # Error handler catches exceptions
    # Can retry, abort, or set error state
```

#### Error Step States
- **chart.state = 9:** Error state (stop at step)
- **Recovery Options:**
  1. Fix condition and resume
  2. Transition to error handling step
  3. Jump to recovery branch
  4. Abort entire chart

#### Best Practices
- Wrap device communication in error handlers
- Log errors to database before aborting
- Provide retry transitions for recoverable errors
- Use assertion steps to prevent invalid states

---

### Common SFC Patterns

#### 1. Loop Pattern (Repeat Until Condition)
```
┌──────────────────┐
│ Initialize:      │
│ Counter = 0      │
└────────┬─────────┘
         │
    ┌────▼──────────────┐
    │ Action: Process   │ ◄──────┐
    │ Counter++         │        │
    └────┬──────────────┘        │
         │                       │
    ┌────▼──────────────┐        │
    │ Transition:       │        │
    │ {counter} < 10?   ├────────┘
    │ YES: loop         │
    │ NO: continue      │
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │ Final Step        │
    └───────────────────┘
```

#### 2. Conditional/Decision Pattern
```
┌──────────────────┐
│ Read Sensor      │
│ Store in: mode   │
└────────┬─────────┘
         │
    ┌────▼────────────┐
    │ Transition 1:    │
    │ {mode}=="AUTO"?  ├─────────► [Auto Mode Step]
    │ YES/NO          │
    └────┬────────────┘
         │
    ┌────▼────────────┐
    │ Transition 2:    │
    │ {mode}=="MAN"?   ├─────────► [Manual Mode Step]
    │ YES/NO          │
    └─────────────────┘
```

#### 3. Wait/Timer Pattern
```
┌──────────────────────────┐
│ Start Operation          │
│ startTime = current_time │
└────────┬─────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Transition with Timeout:   │
    │ timeout(5000)              │  Wait 5 seconds
    │ OR {elapsed} >= 5000       │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ Next Step (After Delay)    │
    └────────────────────────────┘
```

#### 4. Parallel Execution (Concurrent Branches)
```
        ┌─────────────────┐
        │ Branch Start    │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
    ┌───▼────┐       ┌───▼────┐
    │Branch 1│       │Branch 2│  Run simultaneously
    │Step A  │       │Step C  │
    └───┬────┘       └───┬────┘
        │                 │
    ┌───▼────┐       ┌───▼────┐
    │Step B  │       │Step D  │
    └───┬────┘       └───┬────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │Sync Point       │ Wait for all branches
        │(Continue after) │
        └─────────────────┘
```

#### 5. Jump/Anchor (Flow Redirection)
```
Example: Skip steps on error recovery

┌──────────┐
│ Step A   │
└────┬─────┘
     │
┌────▼──────────┐
│ Check Error?  │
└────┬──────────┘
     │ YES
  ◄─┴─ Jump to Anchor [R]
     │ NO
┌────▼──────────┐
│ Step B        │
└────┬──────────┘
     │
[R] ◄┤ Anchor Point (labeled "R")
│ │
└────▼──────────┐
│ Final Step    │
└───────────────┘
```

#### 6. Assertion Step (Validate Before Progress)
```
┌──────────────────────────┐
│ Assertion Step:          │
│ Validate:                │
│ - {pressure} > 100       │  If condition fails:
│ - {temperature} < 80     │  Chart aborts/transitions
│ - {valve_state} == "OK"  │  to error handling
└──────────────────────────┘
```

---

## Quick Reference: Transaction Group vs. SFC

| Aspect | Transaction Groups | SFCs |
|--------|-------------------|------|
| **Purpose** | Database logging/sync | Sequential automation logic |
| **Trigger** | Event-based | Continuous gateway execution |
| **Scope** | Group-level | Chart instance-level |
| **Data Storage** | SQL database | Chart variables (Python objects) |
| **Language** | SQL + Expressions | Python + Expression language |
| **Location** | SQL Bridge module | SFC module |
| **Execution** | On trigger event | Gateway (run-always or callable) |
| **Best For** | Historical data, sync | Automation workflows, sequences |

---

## References
- [Ignition 8.3 SQL Bridge - Types of Groups](https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/sql-bridge-transaction-groups/types-of-groups)
- [Ignition 8.3 Sequential Function Charts](https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/sequential-function-charts)
- [SFC Basics & Chart Scope](https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/sequential-function-charts/SFC-basics/chart-scope-and-variables)
- [SFC Elements](https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/sequential-function-charts/SFC-elements)
- [SFC Monitoring & Debugging](https://www.docs.inductiveautomation.com/docs/8.1/ignition-modules/sequential-function-charts/SFCs-in-action/monitoring-and-debugging-charts)

---

## See Also

**Prerequisites:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Builds toward:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md)

**Related:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
