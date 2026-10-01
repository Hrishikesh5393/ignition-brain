# `schema/named-query/` — Named Query resource schema

Ground-truth on-disk format of an Ignition 8.3 **Named Query** project resource
(`ignition/named-query/<name>/` = `query.sql` + `resource.json`).

| File | What it is |
|------|-----------|
| `named-query.schema.json` | Machine-parseable JSON Schema for `resource.json`, with every field cited to its decompiled source in `_provenance` / per-field `_source`. Also carries the query-type table, parameter-substitution rules, authorization model and invocation cheat-sheet as `_*` keys. |
| `example/resource.json`, `example/query.sql` | A minimal valid Named Query (`Query` type, one bound param, one query-string param, 30 s cache). |

**Provenance:** decompiled `com.inductiveautomation.ignition.common.db.namedquery.NamedQuery`
(8.3.9) + a live write→`requestScan()`→`NamedQuery.fromResource()` round-trip on a live
8.3.9 gateway (`references/VERIFIED.md`). See `_provenance` in the schema for the full class list.

Human-facing guide: [`skill/references/gateway/named-queries.md`](../../skill/references/gateway/named-queries.md).

Do not edit by hand to "fix" a value — re-verify against the gateway and bump the date.
