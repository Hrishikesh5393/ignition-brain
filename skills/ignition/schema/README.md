# `schema/` — verified Ignition machine-readable schema

These files are **extracted from a live Ignition 8.3.9 gateway and its jars, not
hand-written**. They are the ground truth the `/ignition` skill points at when a
agent needs to know a real `system.*` signature or a real Perspective component's
prop tree. **Verified, not invented.** `system-api` reflection dump **2026-09-03**,
enriched **2026-09-04**; Perspective components enumerated **2026-09-04**.

| Path | What it is | Provenance |
|------|-----------|------------|
| `system-api.raw.json` (~170 KB) | The **immutable** `system.*` reflection dump — `<subpkg>.<fn>` → `{overloads:[[javaType,…]], doc}`. Ground truth for *what exists*. | Live-gateway reflection walk over the scripting environment, 2026-09-03 |
| `system-api.json` (~430 KB) | The **enriched** `system.*` reference — full signatures: parameter names, defaults, keyword-arg support, docstrings, return text, module gating, scope. Regenerated from `system-api.raw.json`. | `<repo>/scripts/enrich_system_api.py` — decompiled `@KeywordArgs`/`@ScriptArg` annotations + i18n `.properties` doc bundles |
| `system-api-coverage.json` | Per-subpackage `system.*` coverage stats + the exact list of the types-only tail + denominator reconciliation note | regenerated with `system-api.json` |
| `perspective/ia.components.json` | Master index of the core `ia` Perspective component library (`PerspectiveComponents`, 70 components) | Verbatim from `perspective-common-3.3.9.jar!/ia.components.json` (hash `bd312826011b021d1d4a`) |
| `perspective/<library>.components.json` (7 files) | One master index per **add-on component library** bundled in Perspective / Reporting — see table below | Verbatim from the module jar's bundled `*.components.json` resource |
| `perspective/by-id/*.json` (82 files) | One file per component: full prop schema, defaults, required props, `palette`/`childPositionSchema`/`events` envelope | The component's entry, verbatim, from the master index it belongs to |
| `named-query/named-query.schema.json` + `named-query/example/` | JSON Schema for a Named Query `resource.json` (query type, `database`, parameter list, caching, `permissions`) + the `query.sql` payload, with per-field `_source` citations and a minimal valid example | Decompiled `com.inductiveautomation.ignition.common.db.namedquery.NamedQuery` (8.3.9) + a live write→`requestScan()`→`NamedQuery.fromResource()` round-trip on a live 8.3.9 gateway (`references/VERIFIED.md`). Full class list in the schema's `_provenance`. |
| `alarm-pipeline/pipeline.schema.json` | Alarm notification pipeline **resource** format — `resource.json` + the `data.bin` block-graph, the `PipelineDescriptor` properties, the flow graph, and the `activePipeline`/`clearPipeline`/`ackPipeline` alarm bindings | Decompiled `alarm-notification-{common,gateway}-7.3.9` (`PipelineDescriptor`, `AlarmPipelineManagerImpl`) + a live pipeline round-tripped on a live 8.3.9 gateway |
| `alarm-pipeline/blocks.schema.json` | Every pipeline **block type** (9 in the registry + the synthetic No-Op terminal): `factoryId`, properties, types, defaults, enums, outputs, and the escalation / two-way-ack patterns | Decompiled `…alarming.common.pipelines.*BlockProperties` + `…alarming.pipelines.blocks.*Block`, cross-checked against a real `data.bin`, 2026-09-04 |

## `system.*` scripting API coverage

`system-api.raw.json` holds 969 reflected entries; 373 are Java/PyObject members the
walk leaked in (`clear`, `getClass`, `toString`, `<sub>.name`, and the
`dict` / `getName` / `system` pseudo-subpackages) and are excluded. That leaves
**596 real `system.*` names** — 451 callable functions (412 fully resolved: 377 with
parameter names + 35 no-arg), 145 module constants, 445 with docstrings.

The **39-function types-only tail** (no source names its params — `*Internal`
helpers, legacy Vision tag calls, un-annotated Java methods) is enumerated per
subpackage in `system-api-coverage.json`. Reconciled against a live `system.*`
reflection walk (2026-09-04): **0 live callable functions missing.** Guide:
`references/gateway/system-api.md`.

## Perspective component coverage — complete for the modules installed when it was dumped

Enumerated **2026-09-04** from the **live Perspective `ComponentRegistry`** on gateway
`8.3.9 (b2026082511)` (Perspective `3.3.9`, Reporting `7.3.9`), reached via
`IgnitionGateway.get().getModuleManager().getModule("com.inductiveautomation.perspective").getHook().getContext().getComponentRegistry()`.
That registry is the authoritative "what can actually be placed in a view" answer.

**82 registered components**, across 2 modules / 8 component libraries:

| Library (`*.components.json`) | Module | Components | ids |
|------|--------|-----------|-----|
| `ia.components.json` (`PerspectiveComponents`) | perspective | 70 | `ia.container.*`, `ia.display.*`, `ia.input.*`, `ia.navigation.*`, `ia.shapes.*`, `ia.symbol.*` |
| `perspective-amcharts.components.json` (`PerspectiveAmCharts`) | perspective | 4 | `ia.chart.gauge`, `ia.chart.pie`, `ia.chart.simple-gauge`, `ia.chart.xy` |
| `perspective-timeseries.components.json` (`PerspectiveTimeseriesCharts`) | perspective | 3 | `ia.chart.chartrangeselector`, `ia.chart.powerchart`, `ia.chart.timeseries` |
| `perspective-googlemap.components.json` (`PerspectiveGoogleMap`) | perspective | 1 | `ia.display.google-map` |
| `perspective-map.components.json` (`PerspectiveMap`) | perspective | 1 | `ia.display.map` |
| `pdf-viewer.components.json` (`PerspectivePdfViewer`) | perspective | 1 | `ia.display.pdf-viewer` |
| `barcode.component.json` (`PerspectiveBarcode`) | perspective | 1 | `ia.display.barcode` |
| `reporting-components.components.json` (`ReportingComponents`) | reporting | 1 | `ia.reporting.report-viewer` |

Palette categories (from the live registry): `container` 7, `display` 26, `input` 18,
`shapes` 9, `chart` 7, `symbols` 5, `embedding` 5, `navigation` 3, `reporting` 1,
`unknown` 1.

### What changed from the previous "core 70" extraction

The 2026-09-03 pass captured only the `ia` `PerspectiveComponents` library (70). The
7 add-on libraries above ship **inside the Perspective and Reporting module jars** —
they are not separately-installed modules — and the Perspective `ComponentRegistry`
loads them by default (`ComponentRegistry.DEF_FILE_NAMES`). They were missing from
`schema/`. This pass adds all **12** of their components. No component in the old 70
was renamed or removed.

- **Google Map** (`ia.display.google-map`) — the map add-on the brief called out. It is
  bundled in `perspective-common`, not a separate module, and needs a Google Maps API
  key configured on the gateway to render.
- **`ia.symbol.*` is complete at 5** (`motor`, `pump`, `sensor`, `valve`, `vessel`) —
  confirmed against the live registry. No P&ID / ISA symbol set ships as registered
  Perspective components. The **Symbol Factory** module (`com.inductiveautomation.symbol-factory`,
  8.3.9, ACTIVE on the dumped gateway) contributes **zero** Perspective components — it is a
  library of SVG drawing assets, used through `ia.display.icon` / the Designer's SVG
  import, not through the component registry.
- **Reporting** registers exactly one Perspective component: `ia.reporting.report-viewer`.
- **11 components are flagged `deprecated`** in the registry (still placeable, kept for
  backward compat): `ia.container.drawing`, `ia.navigation.navlinks`, and the 9 legacy
  `ia.shapes.*` primitives (`circle`, `ellipse`, `group`, `line`, `path`, `polygon`,
  `polyline`, `rect`, `text` — superseded by `ia.shapes.svg` + the coordinate
  container). These were already in the 70; nothing new.

### Recovery notes / fidelity

- Every `by-id/` file for the 12 new components is the component's entry **verbatim**
  from its module jar's bundled `*.components.json`, with one added top-level
  `_source` key citing the jar path, library, hash, and the live-registry
  verification. The core-70 files carry no `_source` (unchanged from the 2026-09-03
  extraction).
- All 12 schemas were recovered **in full** — no partial reconstructions. The live
  `ComponentRegistry.getSchema()` dump was cross-checked against the jar def-files and
  agrees on prop names.
- `by-id/` is now the **complete set of placeable Perspective components for this
  gateway's installed modules** (82 files).

## Alarm pipeline schema (`alarm-pipeline/`, added 2026-09-04)

Unlike `system-api.json` and `perspective/`, the two `alarm-pipeline/*.schema.json`
files are **transcribed** from decompiled bytecode into a stable shape, not a
wholesale machine dump — each field carries a `_cite` to the exact `BasicProperty`
declaration or block method it came from, and the top-level `_source` records the
live gateway round-trip that confirmed the on-disk format (build a `PipelineDescriptor`
through the module classloader → `XMLSerializer` → write → `requestScan` →
`getPipelineNames()` → delete). The human-facing guide is
`skill/references/gateway/alarm-pipelines.md`. If the alarm-notification module is
upgraded, re-verify the registry list in `AlarmPipelineManagerImpl` and re-run the
round-trip.

## Using these

- `references/gateway/system-api.md` in the skill is the human-facing guide to
  `system-api.json`.
- `references/gateway/component-schemas.md` is the guide to `perspective/`.
- `references/gateway/named-queries.md` is the guide to `named-query/`.
- The `scripts/build_view*.py` builders are worked examples of turning these schemas
  into valid resource JSON.

## Do not edit by hand

If Ignition is upgraded or the extraction is re-run, replace these files wholesale
and bump the dates above. Never patch a signature in by hand — that defeats the
"verified" guarantee.

- **`system-api`:** re-dump `system-api.raw.json` from a live reflection walk, refresh
  the jar decompile (`<decompiled-jars>/`), then
  `python3 scripts/enrich_system_api.py` (idempotent — always reads the raw dump,
  never its own output). Where a param name has no decompiled annotation and no
  doc-bundle key, the extractor leaves the entry types-only and flags it rather than
  guessing.
- **`perspective/`:** re-enumerate from the live `ComponentRegistry` (not the jars
  alone) so newly-installed modules that contribute components are caught.
