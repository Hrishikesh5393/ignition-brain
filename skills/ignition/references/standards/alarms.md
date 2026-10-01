# Alarming Standards

Alarm-management principles (**ANSI/ISA-18.2**, **EEMUA 191**) mapped onto Ignition's
alarm mechanism. Universal layer. The priority scheme, colours, sounds, rate targets
and annunciation policy **this deployment adopted** are in the project alarm policy.
HMI annunciation: `skill/references/standards/isa101-hmi.md`. Notification / roster
security: `skill/references/standards/security-roles.md`.

Alarm-config keys and enums below are verified from decompiled 8.3.9 bytecode
(`CommonAlarmProperties`, `AlarmMode`, `AlarmPriority`, `DeadbandMode`, `AlertAckMode`
in the decompiled jars) and a live
`system.tag.configure` + `getConfiguration` round-trip (2026-09-04). Standards
principles are stated from knowledge.

## ISA-18.2 lifecycle

`Identification → Rationalisation → Detailed design → Implementation → Operation →
Maintenance → Monitoring & assessment → Management of change → Audit.`
The agent mostly touches **detailed design + implementation**, but must not skip
**rationalisation**: every alarm needs a defined *consequence of inaction*, *operator
response*, and *time to respond*. No rationalisation → no alarm.

## EEMUA 191 targets (steady state, per operator)

| Metric | Target |
|---|---|
| Alarms per hour | ≤ ~6 (≈1 per 10 min) |
| Alarms in first 10 min after a major upset | ≤ ~10 |
| Standing (stale) alarms | < ~10 at any time |
| Priority distribution | ~80% Low / ~15% Medium / ~5% High (+ rare Critical) |

If a design would blow these, the fix is fewer/better alarms, not a bigger screen.

## Ignition alarm config on a tag (verified keys)

An alarm is a dict in the tag's `alarms` list. Verified property names & defaults
(`CommonAlarmProperties`):

| Key | Type / enum | Default | Notes |
|---|---|---|---|
| `name` | String | — | required, scoped to the tag; keep short (`High`, `LowLow`, `Fault`) |
| `enabled` | Boolean | `true` | |
| `priority` | `Diagnostic \| Low \| Medium \| High \| Critical` | `Low` | **consequence, not urgency-feel** |
| `mode` | see enum below | — | normalises on write (`AboveValue` → `Above Setpoint`) |
| `setpointA` / `setpointB` | Double | — | trip point(s); `Inclusive*` flags per mode |
| `deadband` | Double | `0.0` | **always set > 0** for analog alarms |
| `deadbandMode` | `Absolute \| Percent \| Off` | `Absolute` | |
| `timeOnDelaySeconds` | Double | `0.0` | must persist this long to activate |
| `timeOffDelaySeconds` | Double | `0.0` | must clear this long to clear |
| `ackMode` | `Unused \| Auto \| Manual` | `Manual` | `Auto` = self-acking (use sparingly) |
| `ackNotesReqd` | Boolean | `false` | |
| `notes` | String | `""` | rationalisation / operator action text |
| `displayPath` | String | `null` | **operator-facing identity** — set this, independent of tag path |
| `label` | String | `null` | short display label |
| `shelvingAllowed` | Boolean | `true` | |
| `timestampSource` | `System \| ...` | `System` | |
| `activePipeline` / `clearPipeline` / `ackPipeline` | String | `""` | notification pipeline names |
| `defaultPipelineProject` | String | `alarm-pipelines` | |
| `notifyInitialEvent` | Boolean | `false` | |

`alarmEvalEnabled` (tag-level, not per-alarm) gates evaluation for the whole tag.
**Associated data**: extra static/expression properties on the alarm event, carried
into the journal and notification — used for area, equipment id, SOP link.

### `mode` enum (verified `AlarmMode`)

`Equality, Inequality, AboveValue, BelowValue, BetweenValues, OutsideValues,
OutOfEngRange, BadQuality, AnyChange, Bit, OnCondition, WhenTrue, WhenFalse`

- Analog level: `AboveValue` / `BelowValue` / `BetweenValues` / `OutsideValues`
  (+ `setpointA`/`setpointB`, `InclusiveA`/`InclusiveB`, `AnyChange`).
- Digital: `WhenTrue` / `WhenFalse` / `Bit` (`BitPosition`, `BitOnZero`).
- Quality: `BadQuality`; range: `OutOfEngRange`; discrete match: `Equality`.

## Priority model

Five levels, ordinal `Diagnostic(0) … Critical(4)`. Map **consequence severity ×
time-to-respond**, per the project alarm policy:

| Priority | Meaning |
|---|---|
| Critical | Imminent safety / major environmental / large economic loss; immediate action |
| High | Significant consequence, prompt action, minutes to respond |
| Medium | Moderate consequence, action this shift |
| Low | Minor / informational-but-actionable |
| Diagnostic | Instrument / system health; **not annunciated on operator graphics** — journal/maintenance only |

## Deadband & delays — the anti-chatter rules

- **Every analog alarm has a non-zero `deadband`** (absolute eng-units or percent).
  Without it a signal sitting on the setpoint floods the journal.
- Use `timeOnDelaySeconds` for noisy/transient signals so a brief excursion doesn't
  alarm; `timeOffDelaySeconds` to stop flapping on clear.
- Chattering alarm (many transitions/min) = deadband or on-delay too small, or the
  alarm shouldn't exist.

## Alarm Notification pipeline (concept)

Pipelines live in an `alarm-pipelines`-style project and route active/clear/ack
events to notification blocks (email, SMS via a module, roster, delay, splitter,
escalation). A tag's alarm names a pipeline in `activePipeline` etc. Rosters
(`system.alarm.getRosters` / `createRoster`) are the on-call lists.

A fresh gateway has no pipelines (`system.alarm.listPipelines()` → `[]`). Notification is a
separate design task; check whether pipelines exist before assuming they do.

**Pipeline detail** — on-disk format, every block type and its config, the flow graph,
and how `activePipeline` / `clearPipeline` / `ackPipeline` bind an alarm to a pipeline:
`skill/references/gateway/alarm-pipelines.md` (+ `schema/alarm-pipeline/`).

## Alarm Journal profile requirement (verified)

Alarm **history** needs a configured **Alarm Journal profile** (a DB-backed store).
Verified: with none configured,
`system.alarm.queryJournal(...)` → `IllegalArgumentException: The alarm journal
profile 'Journal' does not exist.`, and the `ignition-mcp` `get_alarm_history` tool
returns a **graceful note**, not data (`memory/ignition-mcp-setup.md`). If a brief
asks for alarm-history analysis and no journal profile exists, report that and stop —
do not create one silently.

`system.alarm.queryStatus` (live/active alarms) works without a journal.

## Type-level vs instance

Define alarms on the **UDT type member** so every instance inherits them
(`skill/references/standards/udt-design.md`). Override a setpoint on an instance only
for a genuine per-unit difference — better, make the trip point a type parameter and
bind `setpointA` to it.

## agent rules

1. No alarm without a rationalisation: consequence, operator action (`notes`), time
   to respond.
2. `priority` reflects **consequence**, not how urgent it feels. Use the mapping in
   the project alarm policy.
3. Every analog alarm gets a non-zero `deadband`; noisy signals get
   `timeOnDelaySeconds`.
4. Set `displayPath` to the operator-facing identity; keep `name` short.
5. Diagnostic-priority alarms are journal/maintenance only — never on the operator
   graphic.
6. Alarms on the UDT type member, not per instance.
7. `ackMode: Auto` only for genuinely transient advisories.
8. No alarm-history work without a journal profile — report its absence, don't create
   one.
9. Notification pipelines/rosters are a separate task — confirm before relying on them.

## Smells

- `deadband: 0.0` on an analog alarm.
- Everything `priority: High` (or `Critical`).
- Alarm `name` doubles as the operator message; `displayPath` unset.
- Dozens of near-duplicate alarms on sub-signals of one device instead of one grouped
  alarm.
- A "nuisance" alarm that operators routinely shelve every shift — delete or redesign
  it.
- Alarms defined on each instance by copy-paste instead of on the type.
- Assuming `queryJournal` / `get_alarm_history` returns rows when no journal profile
  is configured.
- Alarm rate design that ignores the EEMUA 191 targets.
