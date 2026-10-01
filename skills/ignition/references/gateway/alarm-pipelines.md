# Alarm Notification Pipelines

> **See also:** `references/gateway/deep/alarm-pipeline-schema-truth.md` — an independently decompiled confirmation of the same `PipelineDescriptor`/block-factory model from Ignition 8.3.7 (this file: 8.3.9), plus the methodology writeup for how the XML-not-JSON format was actually proven (trace the real `XMLDeserializer` load call — "no Gson found" is not proof of JSON).

> **See also:** `references/gateway/notes/verification.md` §Method lessons — the "absence of Gson is not proof of JSON" methodology lesson from the same alarm-pipeline research, generalized to Transaction Groups and SFCs (also XML via the same `ignition.common.xmlserialization` framework, confirmed by tracing their real load calls the same way).

How an Ignition 8.3 **Alarm Notification Pipeline** is laid out on disk, every block
type and its config, how blocks wire together, and how a tag's alarm binds to a
pipeline. Companion machine-readable schema: `schema/alarm-pipeline/`
(`pipeline.schema.json`, `blocks.schema.json`). Concept + alarm-management context:
`skill/references/standards/alarms.md`. General resource format + safe-write protocol:
`resource-formats.md`.

Everything below is verified from decompiled **`alarm-notification-common-7.3.9`** /
**`alarm-notification-gateway-7.3.9`** (`…alarming.common.pipelines.*`,
`…alarming.pipelines.*`) plus a live
round-trip on an 8.3.9 gateway (`references/VERIFIED.md`): a
`PipelineDescriptor` built through the module classloader, serialized with the
module's `XMLSerializer`, written to disk, loaded by `requestScan()` (confirmed via
`AlarmPipelineManager.getPipelineNames()`), then deleted. **Nothing here is invented.**

---

## 1. On-disk layout

`ResourceType` = `("com.inductiveautomation.alarm-notification", "alarm-pipelines")`
(decompiled `PipelineDescriptor.RESOURCE_TYPE`). A pipeline is a **project** resource:

```
data/projects/<project>/com.inductiveautomation.alarm-notification/alarm-pipelines/<PipelineName>/
  resource.json      resource manifest — files:["data.bin"]
  data.bin           the block graph, as Ignition XML object-serialization (NOT JSON)
```

- `<PipelineName>` is the resource **folder path** and may nest
  (`Area1/Escalation`) — decompiled `startPipelineFromResource()` uses
  `resource.getFolderPath()` as the pipeline name, `resource.getCollectionName()` as
  the project.
- Minimal `resource.json` that the gateway accepted and ran ( — live 2026-09-04):

```json
{ "scope": "G", "version": 1, "restricted": false, "overridable": true,
  "files": ["data.bin"], "attributes": {} }
```

  The Designer additionally stamps `attributes.lastModificationSignature` /
  `attributes.lastModification`. You do not need those. `files` **must** contain
  `data.bin` (that string is `Resource.DEFAULT_DATA_KEY`).

- `data.bin` is **not JSON**. It is the platform `XMLSerializer` dump of a
  `PipelineDescriptor` (a `BasicPropertySet`), read back gateway-side with
  `gatewayContext.createDeserializer().deserialize(bytes)` →
  `rootObjects().get(0)`. Shape:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<objects>
  <o cls="…alarming.common.pipelines.PipelineDescriptor">
    <o-c m="setRawValueMap" s="1;java.util.Map">
      <o cls="java.util.HashMap"> … BasicProperty → value entries … </o>
    </o-c>
  </o>
</objects>
```

  It carries Java class refs, constructor arg-lists (`o-ctor s="3;…"`) and
  back-references (`<ref>N</ref>`). **Hand-writing it is not practical.** Build the
  descriptor on the gateway and serialize it (recipe in §6), or edit the pipeline in
  the Designer's pipeline workspace.

---

## 2. The pipeline descriptor (`PipelineDescriptor`)

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `enabled` | Boolean | `true` | `false` → a `DisabledPipeline`; events fall straight through |
| `blocks` | `ObservablePropertySet[]` | — | one PropertySet per block; each carries `factoryId` + `blockId` |
| `startingBlock` | `ObservablePropertySet` | empty | holder whose **`outputId` UUID** names the first block |
| `dropoutConditions` | `EnumSet<DropoutCondition>` | all three | early-exit: `OnAck`, `OnClear`, `OnShelve` (member names; localized labels are *Acknowledged / Cleared / Shelved*) |
| `fallbackPipeline` | String | `null` | pipeline to hand off to on a **block evaluation error** (Expression / Switch). Empty → drop + log |
| `projectName` | String | — | injected at load from the resource's collection; not hand-persisted |

`dropoutConditions` is the mechanism that makes a two-way ACK stop a running
escalation: it is checked in every block's evaluation context and before each user
inside a Notification block (`DropoutCondition.drop(conditions, event)`). At load the
manager copies `dropoutConditions`, `fallbackPipeline` and `projectName` onto **every**
block config.

---

## 3. Block catalog

The registry is fixed — **9 block factories**, from the `AlarmPipelineManagerImpl`
constructor. A block config whose `factoryId` is unknown is silently replaced with a
No-Op and logged.

| Block (UI name) | `factoryId` (suffix of `com.inductiveautomation.`) | Purpose | Key props | Outputs |
|-----------------|---------------------------------------------------|---------|-----------|---------|
| **Delay** | `delayBlockFactory` | wait, then continue | `delay` (ms, def `5000`) | `outputId` |
| **Expression** | `expressionBlockFactory` | eval alarm expression → bool → branch | `expression` | `trueOutput`, `falseOutput` |
| **Switch** | `switchBlockFactory` | eval → match against a value table → route | `mode` (`Property`\|`Expression`), `expression`, `outputTable` (List) | `outputId0..N-1`, `_default_` |
| **Splitter** | `splitterBlockFactory` | fan out to N parallel branches (branched event copies) | `outputCount` (def `2`) | `outputId0..N-1` |
| **Notification** | `notificationBlockFactory` | notify a roster via profile(s), then continue | see §3.1 | `outputId` |
| **Jump** | `jumpBlockFactory` | transfer event to another pipeline (fresh context) | `pipelineName` | — (terminal) |
| **Set Property** | `propertySetterBlockFactory` | eval expression → set a property on the event | `propertyId`, `expression`, `scope` (`Local`\|`Global`) | `outputId` |
| **Script** | `scriptableBlockFactory` | run Jython `handleAlarm(event)` | `script` | `outputId` |
| **Event Stream** | `eventStreamBlockFactory` | publish a JSON alarm snapshot to an Event Stream resource | `eventStreamName` | `outputId` |

Every block config also carries `factoryId` (String, required) and `blockId` (UUID,
required, unique in the pipeline). `outputId` / `trueOutput` / … hold the **`blockId`
of the successor**. A missing or unresolvable target → the synthetic **No-Op
terminal** (the pipeline path ends; the tracking context is destroyed ~15 s later).

Full per-field detail, types, defaults and cite lines: `schema/alarm-pipeline/blocks.schema.json`.

### 3.1 Notification block properties

| Key | Type | Default | Notes |
|-----|------|---------|-------|
| `blockVersion` | Integer | `1` | `1` → use `notificationProfile`; `>=2` → use `notificationProfiles[]` |
| `notificationProfile` | String | — | **deprecated**, blockVersion 1 only |
| `notificationProfiles` | String[] | `[]` | profile names; first one supporting the user's contact type wins |
| `rosterType` | String | — | `roster` (name **or** expression yielding a name) · `calculated` (indented Jython `calculateRoster(event, builder)` body) · `Direct` (resolve once, notify everyone) |
| `roster` | String | — | the roster name / expression / script body, per `rosterType` |
| `ignoreSchedule` | Boolean | `false` | ignore users' on-call schedules |
| `throttlingEnabled` | Boolean | `false` | consolidate events before sending (a `ThrottlingAggregator`) |
| `throttlingDelay` / `throttlingFrequency` | Long | `15000` / `60000` | ms — debounce / max-rate window |
| `timeBetweenNotifications` | Long | `0` | ms between successive roster users; **only applied after a success** |
| `settingsFor_<profileName>` | PropertySet | — | per-profile overrides for this block (prefix `settingsFor_`) |

### 3.2 There is no Escalation block and no Two-Way / ACK block

Both are patterns, not block types:

- **Escalation** — `Notification(roster A) → Delay → Expression("!{isAcked}")
  --true--> Notification(roster B) → Delay → …`. With `dropoutConditions` including
  `OnAck`, an acknowledgement anywhere yanks the event out of every downstream
  `Delay`/`Notification` with no explicit check.
- **Two-way ACK** — a notification **profile** that can receive the ACK back
  (`EmailNotificationProfileType` two-way / POP3 reply, or an SMS module's
  reply-to-ack) **plus** `dropoutConditions` containing `OnAck`. `EmailNotificationProfile`
  only appends the ACK link when two-way is enabled, an ACK send is configured, and
  the event is not already acked.

---

## 4. The flow graph

- **Nodes** = `blocks[]` entries, keyed by `blockId`.
- **Edges** = successor `blockId` held in `outputId` (linear), `trueOutput` /
  `falseOutput` (Expression), `outputId0..N-1` (Splitter / Switch), `_default_`
  (Switch catch-all).
- **Entry** = `startingBlock.outputId`.
- **Dangling edge** → No-Op terminal (path ends). A block with no output set just
  ends that path.
- **Splitter** branches the `AlarmEvent` (`AlarmEventInstance.branch`) down every leg
  and bumps `CommonAlarmProperties.LiveBranchCount`.
- **Jump** destroys the current tracking context and calls
  `AlarmPipelineManager.evaluate(<other pipeline>, event)` — a transfer, not a
  call/return. `Switch` value-table entry *i* pairs with `outputId{i}`; unmatched →
  `_default_`.

```
startingBlock ─▶ Delay(10s) ─▶ Expression{priority>2} ──true──▶ Notification(operators)
                                       │                              │
                                       └──false──▶ (No-Op: ends)      ▼
                                                              Delay(5m) ─▶ Expression{!isAcked} ──true──▶ Notification(supervisors)
```

---

## 5. Binding a pipeline to an alarm

The bindings are ordinary alarm-config keys (dict entries in a tag's `alarms` list),
category **Notification** (decompiled `CommonAlarmProperties`):

| Key | Default | Fires when… |
|-----|---------|-------------|
| `activePipeline` | `""` | the alarm becomes **active** |
| `clearPipeline` | `""` | the alarm **clears** |
| `ackPipeline` | `""` | the alarm is **acknowledged** |
| `defaultPipelineProject` | `"alarm-pipelines"` | — project used to resolve an unqualified pipeline name |

A reference is either a bare name (resolved via `defaultPipelineProject`, or the
event's `PipelineProject`) or fully qualified: `project:<Proj>:/pipeline:<Name>`.
Set these on the **UDT type member**, not per instance — see
`skill/references/standards/alarms.md` and `udt-design.md`.

### Notification profiles & rosters it references

`notificationProfiles` names resolve to **gateway-scoped** Alarm Notification Profiles
(Gateway → Config → Alarming → Notification), *not* project resources. Types in this
module: `EmailNotificationProfileType` (two-way email — ACK link + POP3 reply),
`OneWayNotificationProfileType` (send-only email, own priority criteria +
consolidation), `RemoteNotificationProfileType` (delegate to a profile on another
gateway over the gateway network). **SMS / voice** profiles come from separate add-on
modules — none installed on gateway 8.3.9 as of 2026-09-04. **Rosters** are the
gateway config resource `ignition/roster-config` (`RosterConfig.RESOURCE_TYPE`);
reach them from script with `system.alarm.getRosters()`.

---

## 6. Authoring recipe (gateway-side, `run_gateway_script`)

`data.bin` is object-XML, so build the descriptor with the module's classes and let
its serializer produce the bytes. The module classes are **not** on the WebDev script
classpath — load them through the module hook's classloader:

```python
from com.inductiveautomation.ignition.gateway import IgnitionGateway
ctx = IgnitionGateway.get()
am  = ctx.getModule("com.inductiveautomation.alarm-notification")
cl  = am.getClass().getClassLoader()
def C(n): return cl.loadClass(n)

PD  = C("com.inductiveautomation.ignition.alarming.common.pipelines.PipelineDescriptor")
CBP = C("com.inductiveautomation.ignition.alarming.common.pipelines.CommonBlockProperties")
DBP = C("com.inductiveautomation.ignition.alarming.common.pipelines.DelayBlockProperties")
NBP = C("com.inductiveautomation.ignition.alarming.common.pipelines.NotificationBlockProperties")
BPS = C("com.inductiveautomation.ignition.common.config.BasicPropertySet")
XS  = C("com.inductiveautomation.ignition.common.xmlserialization.serialization.XMLSerializer")
from java.util import UUID
from java.lang import Long as JLong
def f(k, n): return k.getField(n).get(None)

pd = PD.newInstance()
pd.set(f(PD, "ENABLED"), True)

delay = BPS(); did = UUID.randomUUID()
delay.set(f(CBP, "FACTORY_ID"), f(DBP, "FACTORY"))
delay.set(f(CBP, "BLOCK_ID"), did)
delay.set(f(DBP, "DELAY"), JLong(10000))

notif = BPS(); nid = UUID.randomUUID()
notif.set(f(CBP, "FACTORY_ID"), f(NBP, "FACTORY"))
notif.set(f(CBP, "BLOCK_ID"), nid)
notif.set(f(NBP, "ROSTER_TYPE"), "roster")
notif.set(f(NBP, "ON_CALL_ROSTER"), "operators")

delay.set(f(CBP, "OUTPUT_ID"), nid)          # delay -> notification
pd.addBlock(delay); pd.addBlock(notif)
pd.get(f(PD, "STARTING_BLOCK")).set(f(CBP, "OUTPUT_ID"), did)   # start at delay

ser = XS(); am.configureSerializer(ser); ser.addObject(pd)
xml = ser.serializeXML()                      # <-- this is data.bin
```

Then write `data.bin` + `resource.json` gateway-side with **`flush()` +
`os.fsync(fileno())`** (data file first — the fsync trap in `resource-formats.md` §10
applies), `ctx.getProjectManager().requestScan()`, and **verify at runtime**:

```python
am.getAlarmPipelineManager().getPipelineNames()   # contains project:<proj>:/pipeline:<Name>
```

To delete a pipeline resource (the running gateway holds a file lock, so
`os.remove` fails): build a delete `ChangeOperation` and `forcePush` it —

```python
from com.inductiveautomation.ignition.common.resourcecollection import (
    ChangeOperation, ResourceSignature, ResourceId, ResourcePath, ResourceType)
from java.util import ArrayList
pm  = ctx.getProjectManager()
r   = pm.find("<proj>").get().getResource(
        ResourcePath(ResourceType("com.inductiveautomation.alarm-notification","alarm-pipelines"),
                     "<Name>")).get()
sig = ResourceSignature(ResourceId(r.getDefiningCollectionName(), r.getResourcePath()),
                        r.getResourceSignature().signature())
ops = ArrayList(); ops.add(ChangeOperation.newDeleteOp(sig))
pm.forcePush(ops)
```

---

## Crewmate rules

1. **Author `data.bin` through the module's serializer or the Designer** — never
   hand-write the object-XML. `resource.json` you can write directly.
2. `dropoutConditions` is your ACK/clear/shelve exit. Leave all three on unless you
   have a reason; drop `OnAck` only when the pipeline *must* keep going after an ack.
3. An escalation is `Notification → Delay → Expression("!{isAcked}")` chained — there
   is no Escalation block. A two-way ACK needs a two-way **profile** *and* `OnAck` in
   `dropoutConditions`.
4. `Jump` is a one-way transfer (new tracking context). Don't expect control to come
   back.
5. `Splitter` multiplies work — every leg notifies. Use `Switch` / `Expression` when
   you want exactly one path.
6. `timeBetweenNotifications` only paces users **after a successful** notification; a
   failed user is retried against the next immediately.
7. Notification-profile and roster names are **gateway config**, not project
   resources — confirm they exist (a fresh gateway has
   **no** pipelines, profiles or rosters). SMS/voice need an
   add-on module.
8. Bind pipelines on the **UDT type member** (`activePipeline` etc.), not per
   instance.
9. Verify with `getAlarmPipelineManager().getPipelineNames()` at runtime — an HTTP
   200 on the resource write proves nothing (`resource-formats.md` §10–11).

## Smells

- `data.bin` that looks like JSON, or was hand-edited — it will fail
  `XMLDeserializer` and the manager logs *"Error deserializing PipelineDescriptor"*
  and skips the pipeline.
- A block with an `outputId` pointing at a `blockId` that isn't in `blocks[]` — the
  path silently dead-ends at the No-Op (sometimes intended, often a broken edit).
- Escalation built as one giant `Script` block instead of `Notification`/`Delay`/
  `Expression` — loses the status page, the per-block tracking, and the automatic
  dropout behaviour.
- `dropoutConditions` emptied "so notifications always send" — now an acked alarm
  keeps paging people.
- `activePipeline` set on 200 tag instances by copy-paste instead of on the UDT type.
- Pipeline references a `notificationProfile` / `roster` that was never created on the
  gateway — events enter the pipeline and go nowhere (logged as *"Roster '…' has no
  users"* / *"profile … is disabled"*).
- `Splitter` feeding several `Notification` blocks that all target the same roster —
  duplicate pages.
- Relying on `fallbackPipeline` as normal control flow — it only fires on an
  Expression/Switch **evaluation error**, not on a false result.

## Notification profiles — the "roster has no users" gotcha's fix, natively (found 2026-09-22)

The gotcha above ("pipeline references a `notificationProfile` that was never
created") is directly addressable via native REST — the gateway's
`GET /openapi.json` documents CRUD for alarm-notification profiles (SMS/email/
voice — who actually gets paged), separate from the pipeline itself:

| Endpoint | Verb | Purpose |
|---|---|---|
| `/data/api/v1/resources/list/com.inductiveautomation.alarm-notification/alarm-notification-profile` | GET | List configured notification profiles |
| `/data/api/v1/resources/find/com.inductiveautomation.alarm-notification/alarm-notification-profile/{name}` | GET | Read one profile's config |
| `/data/api/v1/resources/com.inductiveautomation.alarm-notification/alarm-notification-profile` | PUT/POST | Create/modify a profile |

Check a profile exists via `list` before wiring a pipeline's `Notification`
block to it, instead of discovering the gap only after events silently vanish
into a missing roster. Schema-confirmed against the live gateway's OpenAPI
spec, not yet exercised end-to-end. Auth: `X-Ignition-API-Token` header, same
as every native call.
