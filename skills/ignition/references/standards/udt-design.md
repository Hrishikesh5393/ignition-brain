# UDT Design Patterns

How to design Ignition **User-Defined Types** — the universal layer. The type library
**this deployment built** is the project UDT catalogue. Folder hierarchy the types
sit in: `skill/references/standards/isa95.md` + the project equipment hierarchy.
Member datatypes: `skill/references/standards/iec-61131.md`. On-disk resource format:
`skill/references/gateway/resource-formats.md`.

Mechanism claims verified live on the 8.3.9 gateway (2026-09-04) via
`system.tag.configure` + `system.tag.getConfiguration`, and against `<repo>/scripts/clean_udts.py`
(the verified UDT-import cleanup) .

## What a UDT is

A parameterised tag template stored under the provider's **`_types_`** folder.
Instances (`tagType: "UdtInstance"`, `typeId: "<TypeName>"`) inherit the type's member
tree, alarms, history and scripts, and substitute their **parameters** into member
OPC paths / expressions. Editing the type propagates to every instance.

## Parameters vs member overrides

| Use a **parameter** when | Use a **member override** when |
|---|---|
| The value differs per instance and feeds a path/expression — device name, PLC prefix, OPC namespace, scaling limit | One instance genuinely deviates in structure/config from the type (rare) |
| e.g. `{DeviceName}` in `ns=1;s=[PLC]{DeviceName}.Run` | e.g. this one pump has an extra vibration probe |
| Keeps every instance identical → indirect bindings need no branching | Each override is a maintenance liability — it *stops* tracking the type for that member |

**Rule: parameterise, don't override.** A type with many instance overrides is a type
that was modelled wrong. Verified: parameters round-trip as
`{datatype=String, value={SkidId}_M1}` and nested params can reference the parent's
params (`{SkidId}` used inside a member instance's `DeviceName`).

Parameter shape in `configure`:
`"parameters": {"DeviceName": {"dataType": "String", "value": ""}}` (dataType one of
`String`, `Integer`, `Long`, `Float`, `Double`, `Boolean`, dataset).

## Nest a UDT vs use a folder

| Want | Do |
|---|---|
| A reusable sub-assembly that appears in several parents (Motor inside Skid inside Line) | **Nested UDT** — define `Motor` type, reference it as a member `{"tagType":"UdtInstance","typeId":"Motor"}` |
| Just visual grouping of members inside one type | **Folder member** (`{"tagType":"Folder","tags":[…]}`) — no separate type, no reuse |
| One-off equipment that will never repeat | Plain tags in a folder, no UDT at all |

Nesting depth: **keep to 2–3 levels** (e.g. `Array → Core → Node → Enclosure → …` in
a demo library went 5+ deep and became painful to reason about and slow to
instantiate). Every extra level multiplies instance member count and binding-path
length.

## `typeId` resolution (verified)

- Type at `_types_` root → `typeId` is the bare name: `"DR_Motor"`.
- Type in a subfolder `_types_/DR_Sub/DR_Valve` → `typeId` is the **folder-relative
  path**: `"DR_Sub/DR_Valve"`.
- A dangling `typeId` fails hard:
  `Bad_NotFound("Cannot add data type instance tag 'X', the data type 'DR_DoesNotExist' was not found.")`

## Dependency-order creation (verified — this is the trap)

`system.tag.configure` does **not** topologically sort. A parent type that references
a child type not yet defined fails with `Bad_NotFound`. So:

```python
# leaf-first order — children before the parents that nest them
ORDER = ["EnController","EnHVAC","EnSensor","EnChiller","EnUPS",
         "CSEController","CSEHVAC","CSESensor","CSC","Inverter","BMS",
         "Enclosure","CSEEnclosure","Node","Core","Array"]
for name in ORDER:
    system.tag.configure("[default]_types_", [TYPES[name]], "o")   # one type per call
```

(from a verified 16-type library import — nesting
resolved `Array→Core→Node→{Enclosure→En*, Inverter, BMS, CSEEnclosure→CSE*}`.)
Build the `ORDER` list from your own dependency graph; assert it covers every type.

## The atomic-member whitelist (from `<repo>/scripts/clean_udts.py`)

A valid type definition contains only trusted atomic-tag config keys on its members.
An exported library is full of junk keys (`munsPath`, `Vendor`, `Model`, `protocol`,
`Recommendation`, `"Feature / Application"`, `DataTypeFix*`) that make `configure`
reject or misparse the type. `clean_udts.py`'s `ATOMIC_KEYS` set is the reference
whitelist:

```
name tagType dataType valueSource opcServer opcItemPath documentation tooltip
tagGroup readOnly formatString engUnit scaleMode rawLow rawHigh scaledLow scaledHigh
historyEnabled historyProvider alarmEvalEnabled engLow engHigh deadband
```

plus the history keys from `skill/references/standards/historian.md`
(`sampleMode`, `historicalDeadband`, `historicalDeadbandMode`, `historicalDeadbandStyle`,
`historySampleRate`, `historySampleRateUnits`, `historyTagGroup`, `historyMaxAge…`) and
`alarms` (list of alarm-config dicts, `skill/references/standards/alarms.md`).

`clean_udts.py` also: infers missing `typeId` on nested instances from a name map,
reduces nested `UdtInstance` members to `{name, tagType, typeId, parameters?}` stubs
(drops redundant override tags — the base type already defines them), and normalises
`parameters` to `{name: {dataType, value?}}`. The `NAME2TYPE` map and `ORDER` list are
per-library and must be rebuilt each time.

## Type-level alarms & history vs instance overrides

- Define alarms and history **on the type's member** (verified: an `alarms` list and
  `historyEnabled` on a `Speed` member of `DR_Motor` propagated into every instance
  and round-tripped through `getConfiguration`).
- `mode` normalises on write: `"AboveValue"` → stored `"Above Setpoint"`. Use the
  enum names from `skill/references/standards/alarms.md`.
- Only override an alarm setpoint on an instance when that unit's trip point is
  genuinely different (e.g. a smaller pump). Prefer making the setpoint a **type
  parameter** and binding the alarm `setpointA` to `{HighTrip}` so the type still
  owns the structure.
- Never enable history on every member of a big type "to be safe" — it is a per-point
  decision (`skill/references/standards/historian.md`).

## OPC item-path parameterisation

Member OPC item path is a template: `ns=1;s=[{PLC}]{DeviceName}.DischPress` with
`{PLC}` and `{DeviceName}` as parameters. Verified: `opcServer` + `opcItemPath` with
`{param}` placeholders store fine on a type member. Keep the **structure** (folders,
member names) identical across instances so a faceplate's indirect bindings are pure
string substitution.

## The `_types_` folder

- One per provider, holds every type. `system.tag.configure("[default]_types_", …)`.
- Subfolders are allowed and change the `typeId` (folder-relative path, above).
- Organise subfolders by the same ISA-95 logic as the instance tree, or by
  equipment class — decide once in the project UDT catalogue.

## agent rules

1. Parameterise per-instance differences; do **not** use member overrides for them.
2. Create types **leaf-first**, one `configure` call per type — the platform won't
   sort for you.
3. `typeId` = bare name at `_types_` root, folder-relative path if nested.
4. Members carry only whitelisted atomic keys (`<repo>/scripts/clean_udts.py` `ATOMIC_KEYS`
   + the history/alarm keys) — strip everything an export added.
5. Nesting depth ≤ 3; use folders (not nested types) for grouping-only.
6. Alarms/history live on the **type** member; instance-level only for a true
   deviation, preferably via a type parameter.
7. Keep every instance's member tree structurally identical so indirect bindings need
   no branching (`skill/references/standards/tag-naming.md`).
8. When the brief needs concrete types, read the project UDT catalogue; do not build on a
   vendor demo type library.

## Smells

- A type with a dozen member overrides on its instances.
- `configure` returning `Bad_NotFound` — parent created before its child type.
- Junk keys (`Vendor`, `munsPath`, `Recommendation`) surviving into a type def.
- Nesting 5+ types deep; instances that take seconds to create.
- `historyEnabled: true` on every member of a 200-member type.
- Instance folders named differently from the identity parameter value, forcing
  `if()` logic in faceplate bindings.
- A one-off skid modelled as a UDT with exactly one instance.
- Hard-coded PLC name in a member OPC path instead of a `{PLC}` parameter.
- Editing a type in a way that silently orphans instance overrides.
