# Tag Naming Principles

The universal layer: what makes an industrial tag-naming convention good, the options
and their trade-offs, and the Ignition-specific rules a name must obey. The scheme
**this deployment adopted** is the project naming convention — that file makes the
choices; this one explains them.

Ignition mechanism claims below were verified live against an 8.3.9 gateway
(`references/VERIFIED.md`) unless flagged `unverified:`. Related:
`skill/references/standards/isa95.md` (folder hierarchy), `udt-design.md` (parameter
alignment), `alarms.md`, `historian.md`.

## Path vs name

An Ignition tag reference is `[provider]Folder/Sub/Folder/TagName[.property]`.

| Part | Rule |
|---|---|
| **Provider** | In brackets: `[default]`. Case-insensitive on lookup. Omitted = current project's default provider. Name it for its role, not its host (`default`, `edge_lineA`, `sim`), short, no spaces. |
| **Path segments** (folders) | Carry the **hierarchy** — ISA-95 area/line/unit. Keep them stable; renaming a folder rewrites every binding under it. |
| **Leaf name** | Identifies the **signal** on that equipment. This is where a signal-type affix scheme lives. |
| **Property** | After a `.` — `.value`, `.Quality`, alarm props. This is why `.` is illegal in a name (below). |

Design rule: **hierarchy in the path, signal identity in the leaf.** Don't encode the
full area path into every leaf name (`PLANT_UTIL_CMP01_PRESSURE`) — that duplicates the
folder tree and breaks when equipment moves.

## Allowed / reserved characters (verified 8.3.9)

Configured 21 candidate names via `system.tag.configure(..., "o")` and checked which
were accepted:

| Result | Characters |
|---|---|
| **Rejected** — `Error_Configuration("… is not a valid tag name")` | `.`  `/`  `\`  `[`  `]`  `*`  `?`  `%`  `+`  `#`  `@`  `&`  `"` |
| **Accepted** | letters, digits, `_`, `-`, space, `:`, `(`, `)`, `'` |
| **Accepted but avoid** | leading digit (`123tag` works), space, `:`, `'`, `(` `)` — legal but fragile in expressions, bindings, and DB history table/column names |

**Practical safe set: `[A-Za-z0-9_-]`, no leading digit.** `/` and `\` are path
separators; `[ ]` delimit the provider; `*` `?` `%` are glob/wildcard;
`.` selects a property; the rest collide with the expression language.

## Case (verified 8.3.9 — differs from older guidance)

- Tag path resolution is **case-insensitive**: `Motor_A`, `motor_a`, `MOTOR_A`,
  `mOtOr_a` all read the same tag (value + Good quality).
- Two sibling tags differing **only** by case **cannot coexist** — a later
  `configure` merges onto the existing tag and can even rewrite its stored casing
  (`Motor_A` then `motor_a` → one tag, stored as `motor_a`).
- Casing **is** preserved in storage and in `browse()` results.
- Therefore: treat names as **case-preserving but not case-distinguishing**. Pick one
  casing convention and apply it everywhere; never rely on case to disambiguate two
  signals. (`unverified:` whether UDT `typeId`, project names, and script-package
  paths are equally lenient — assume they are case-sensitive and match exactly.)
- IEC 61131 identifiers are case-insensitive too (`skill/references/standards/iec-61131.md`),
  so a PLC `Motor_A` and `MOTOR_A` are one variable — the mapping is consistent, but
  only if your import tooling normalises case.

## Delimiter options & trade-offs

The leaf name often packs several fields (equipment id, signal, type). Options:

| Delimiter | Example | Pros | Cons |
|---|---|---|---|
| `_` underscore | `CMP01_DischPress_PV` | readable, DB-safe, expression-safe | long; must be consistent about field order |
| CamelCase | `Cmp01DischPressPv` | compact | ambiguous field boundaries, hard to parse |
| `-` hyphen | `CMP01-DischPress-PV` | readable | some tools treat `-` as minus in expressions |
| extra folder | `CMP01/DischPress` + leaf `PV` | fields become browsable hierarchy | deep trees, more binding churn on moves |
| `.` | — | **illegal** in names | reserved for properties |

Recommended: **`_` between fields in the leaf, `/` for genuine hierarchy.** Fixed
field order, documented in the project naming convention.

## Signal-type affix schemes

Encode the signal role so a name is self-describing and lists sort usefully.

| Scheme | Form | Example | Notes |
|---|---|---|---|
| ISA-5.1 style prefix | `<function><loop>` | `PT_1001`, `TIC_205` | instrument-centric; familiar to process engineers |
| IEC 61131 / IO suffix | `<name>_<AI\|AO\|DI\|DO>` | `DischPress_AI` | I/O-centric; good for PLC-mirrored tags |
| Semantic suffix | `_PV _SP _CV _CMD _STS _FB` | `DischPress_PV`, `Pump_CMD` | HMI-centric; pairs naturally with faceplate params |
| Hungarian datatype | `b… i… f… s…` | `bRunning` | discouraged — datatype is metadata, not identity |

Pick **one** affix vocabulary and a **fixed position** (all suffixes or all
prefixes). The set must be closed and listed in the project conventions.

## Aligning names with UDTs and indirect bindings

- **UDT member names become the tail of every instance path.** `Compressor` with
  member `DischPress_PV` → `[default]PLANT/UTIL/CMP01/DischPress_PV`. Choose member
  names as carefully as standalone tags — renaming a member breaks every instance and
  every binding.
- **UDT parameters** (`{InstanceName}`, `{PLC}`, custom) are substituted into member
  OPC item paths and expressions. Name parameters for what they carry (`DeviceName`,
  `PlcAddress`), and keep instance folder names equal to the value you'd pass as the
  identity parameter so indirect bindings stay mechanical.
- **Indirect tag bindings** build a path by string substitution:
  `tagPath` = `[default]PLANT/UTIL/{view.params.unit}/DischPress_PV`,
  `mode:"indirect"`, `references:{"0":"{view.params.unit}"}` (verified binding-config
  keys, `skill/references/gateway/component-schemas.md`). This only works if every
  unit uses the **identical member name** and folder-naming pattern. Inconsistent
  names force `if/else` in bindings — the primary smell this convention exists to
  prevent.
- Keep leaf names **free of the area path** so the same faceplate view drops onto any
  instance.

## Alarm & history naming

- **Alarm name** is scoped to its tag, so it can be short (`High`, `LowLow`,
  `Fault`). The operator-facing string is `displayPath` (verified alarm prop,
  `skill/references/standards/alarms.md`) — set that to something like
  `UTIL/CMP01/Discharge Pressure High`, independent of the tag path.
- **History**: the historian derives its SQL table/column identifiers from the tag
  path. Names with spaces, `:` or `'` produce awkward quoted SQL and fragile
  `queryTagHistory` calls — another reason to hold the leaf to `[A-Za-z0-9_-]`
  (`skill/references/standards/historian.md`).

## Length / practical limits

- No hard character limit was hit in testing, but **keep leaf names ≤ ~30 chars** and
  total path depth modest — long paths bloat every binding, every history row, and
  every log line.
- Folder nesting: match the ISA-95 levels actually used
  (the project equipment hierarchy), typically 3–5 deep, not more.

## agent rules

1. Use only `[A-Za-z0-9_-]` in names; never a leading digit. No `. / \ [ ] * ? % + # @ & "`.
2. Hierarchy goes in folders; signal identity goes in the leaf. Don't repeat the path
   in the name.
3. One casing convention everywhere; never rely on case to tell two tags apart.
4. One delimiter for fields (`_`), one closed affix vocabulary, fixed position.
5. UDT member names and instance folder names must follow the convention so indirect
   bindings need no branching.
6. Set `displayPath` for the operator string; keep the alarm `name` short.
7. When the brief needs a concrete name, take the scheme from
   the project naming convention — do not invent one.
8. Provider names describe role, are lowercase-ish, no spaces.

## Smells

- `.` in a tag name (it will fail to configure).
- `PLANT_UTIL_CMP01_DISCH_PRESS_PV` — full path duplicated into the leaf.
- Two siblings `Pump1` / `pump1` expected to be different tags.
- Binding expressions with `if({unit}='CMP01', ..., if({unit}='CMP02', ...))` — the
  members aren't named consistently.
- Spaces / `:` / `'` in names that then flow into history tables or expressions.
- Mixed suffix and prefix affixes (`PT_DischPress` next to `DischPress_AI`).
- Datatype-in-name (`fDischPress`).
- A UDT parameter named `{P1}` / `{X}` instead of `{DeviceName}`.
- Renaming a folder/member late in the build and discovering 200 broken bindings —
  lock names early.
