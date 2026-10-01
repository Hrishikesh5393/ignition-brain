# Historian & Tag History

Tag-historian design principles and the Ignition mechanism they map to. Universal
layer. The provider, sample rates, retention and which points are historised **for
this deployment** are in the project gateway profile. Naming:
`skill/references/standards/tag-naming.md`. Query API:
`skill/references/gateway/system-api.md` (`schema/system-api.json`).

Tag-history property names, enums and API surface below are verified from decompiled
8.3.9 bytecode (`TagHistoryProps`, `SampleMode`, `AggregationMode`,
`InterpolationMode`, `DeadbandMode` in the decompiled jars) and live gateway
calls (2026-09-04). Principles are stated from knowledge.

## Storage model

- **History providers** are registered stores. The common one is **SQL-backed**
  (Store-and-Forward → a database connection → partitioned tables). Other stores exist
  (e.g. an internal/edge store).
- A fresh gateway has no historian and no DB (`getTagHistoryProviders()` → `[]`,
  `system.db.getConnections()` → 0 rows). If a brief needs history, confirm the provider
  exists first; report its absence, do not provision one silently.
- **Trap:** `system.tag.queryTagHistory` still returns rows with **no provider and no
  stored data** — it interpolates from the current value (verified: 5 rows returned
  for a simulated tag with no historian). An HTTP-200 / non-empty
  dataset is **not** proof history is being recorded.

## Enabling history on a tag / type (verified keys — `TagHistoryProps`)

| Key | Enum / type | Default | Notes |
|---|---|---|---|
| `historyEnabled` | Boolean | `false` | gates everything below |
| `historyProvider` | String | `""` | which registered store |
| `sampleMode` | `OnChange \| Periodic \| TagGroup` | `OnChange` | |
| `historySampleRate` | Integer | `0` | with `Periodic` |
| `historySampleRateUnits` | `MS \| SEC \| MIN \| HOUR \| ...` | `SEC` | |
| `historicalDeadband` | Double | `0.01` | **value deadband** — suppress insignificant changes |
| `historicalDeadbandMode` | `Absolute \| Percent \| Off` | `Absolute` | |
| `historicalDeadbandStyle` | `Auto \| Analog_Compressed \| Discrete` | `Auto` | interpolation hint; allowed set restricted to these 3 |
| `historyTagGroup` | String | `Default Historical` | with `TagGroup` mode |
| `historyMaxAge` / `historyMaxAgeUnits` | Integer / `HOUR` | `0` / `HOUR` | max time between samples (bound staleness) |
| `historyTimeDeadband` / `…Units` | Integer / `SEC` | `1` / `SEC` | min time between samples (rate-limit on-change) |
| `includeMetadata` | Boolean | `false` | store eng-units/limits alongside |

Define these on the **UDT type member** (`skill/references/standards/udt-design.md`),
not per instance.

## Sample modes

| Mode | Records | Use for |
|---|---|---|
| **OnChange** | a row when the value changes beyond `historicalDeadband`, rate-limited by `historyTimeDeadband`, forced at `historyMaxAge` | most analog + discrete points — smallest storage, exact transitions |
| **Periodic** | a row every `historySampleRate` regardless of change | signals that must have a guaranteed cadence (regulatory), or very noisy signals where on-change floods |
| **TagGroup** | evaluated on a named tag group's schedule | aligning many points to one clock |

Default to **OnChange with a real deadband**.

## Value & timestamp deadband

- **Value deadband** (`historicalDeadband` + mode): a change smaller than this is not
  stored. Absolute in eng-units, or percent of span. Set it to the instrument's
  noise / meaningful resolution — e.g. ±0.5 °C, not 0.
- **Time deadband** (`historyTimeDeadband`): never store more often than this even if
  the value keeps changing — caps the row rate on a chattering signal.
- **Max age** (`historyMaxAge`): store at least this often even if nothing changed —
  gives a heartbeat so gaps mean "no data", not "unchanged".

## Retention / pruning / partitioning (SQL store)

- **Partitioning**: the SQL store writes into time-sliced partition tables (e.g.
  monthly). Queries touch only the partitions in range → keeps big histories fast.
- **Pruning**: enable age-based pruning on the provider to cap total size; set the
  horizon from the data's actual use (trend review, reporting, compliance).
- Partition size is a tuning trade-off: smaller = faster targeted queries, more
  tables; larger = fewer tables, slower wide scans.
- These are **provider settings**, recorded in the project gateway profile.

## Query & aggregation (verified API)

| Function | Purpose |
|---|---|
| `system.tag.queryTagHistory` | raw or aggregated series over a window |
| `system.tag.queryTagCalculations` | one aggregate value per tag over a window |
| `system.tag.queryTagDensity` | how much data exists in a window (gap detection) |

**Aggregate at query time, not by pre-storing rollups.** Verified `AggregationMode`
values: `Average, MinMax, LastValue, SimpleAverage, Sum, Minimum, Maximum,
DurationOn, DurationOff, CountOn, CountOff, Count, Range, Variance, StdDev, PctGood,
PctBad`.

- Trend screens: pass a `returnSize` / interval and an aggregation mode so the DB
  returns ~1 point per pixel, not every raw row.
- `Average` is time-weighted; `SimpleAverage` is not — pick deliberately.
- `DurationOn` / `CountOn` for runtime & cycle-count KPIs straight from a boolean.

## Design decisions

- History is a **per-point decision made at design time**, not "enable on the whole
  provider". Historise what will actually be trended, reported, or investigated.
- Deadband is a storage-control lever — tune it per signal class.
- Don't historise a value you can derive (store the flow, not the running total).
- Match `sampleMode` to the signal: OnChange for events/analog, Periodic for
  regulatory cadence.
- Put history config on the type; keep instances identical.

## agent rules

1. Confirm a history provider exists before relying on history; report its absence —
   don't provision one.
2. A non-empty `queryTagHistory` result is not proof of recording — verify with
   `queryTagDensity` or the provider's stored partitions.
3. `historyEnabled` per point, chosen deliberately — never blanket-on across a type
   or provider.
4. Every historised analog point gets a non-zero `historicalDeadband` sized to its
   noise; add `historyTimeDeadband` for noisy ones and `historyMaxAge` for a
   heartbeat.
5. History config on the **UDT type member**, not per instance.
6. Aggregate in the query (`queryTagCalculations` / aggregation mode), don't store
   rollups.
7. Trend queries specify an interval/`returnSize` + aggregation — never pull raw rows
   for a screen.
8. Take provider name / rates / retention from the project gateway profile.

## Smells

- `historyEnabled: true` on every member of a UDT "so we have it if we need it".
- `historicalDeadband: 0` on an analog point — every noise wiggle stored.
- `sampleMode: Periodic` at 1 s on hundreds of tags.
- A trend component querying raw history with no interval, then downsampling in the
  client.
- Storing a totaliser that could be integrated from the rate at query time.
- Pre-computed hourly-average tags instead of `queryTagCalculations`.
- Assuming history works because `queryTagHistory` returned rows (it interpolates).
- History settings overridden per instance instead of set on the type.
- No pruning horizon — the history DB grows unbounded.
