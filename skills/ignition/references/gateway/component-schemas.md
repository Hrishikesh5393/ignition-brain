# Perspective Component Schemas

> **See also:** `references/gateway/deep/perspective-schema-truth.md` — the decompile-verified style precedence chain (a component prop always beats the equivalent CSS in its own `style`; a parent container's `position` always beats a child's `style`), the flex prop-to-CSS map, and named-style/session-prop/view-prop schemas this file doesn't cover. Verified against Ignition 8.3.7; this file is verified against 8.3.9 — re-check before trusting a version-sensitive number from either.

> **See also:** `references/gateway/notes/feedback_perspective_flex_props.md` — the flex style-precedence chain and prop-to-CSS map as a condensed lesson-learned (113 migrated occurrences in one project), the same fact `perspective-schema-truth.md` §2 documents at length.

> **See also:** `references/gateway/notes/gotchas.md` — this skill's own verified-traps list: the same flex precedence chain, plus `PropertyTree`'s 8 `read*` accessor types (`readObject`, `readArray`, …) and the "one binding beats twenty" pattern for many-tags-into-one-component.

How to turn `schema/perspective/**` into valid Perspective `view.json`. Pair this with
`resource-formats.md` §4 (the `view.json` / `ComponentConfig` envelope) and §6 (bindings).

---

## The files

**82 components**, enumerated 2026-09-04 from the live Perspective `ComponentRegistry`
on gateway 8.3.9 (Perspective 3.3.9, Reporting 7.3.9) — the authoritative "what can be
placed" list. `by-id/` is the complete set for the modules installed when it was dumped.

| Path | What |
|------|------|
| `schema/perspective/ia.components.json` | master index of the core `ia` library — `{groupId:"ia", libraryName:"PerspectiveComponents", hash, components:[…70…]}` — verbatim from `perspective-common-3.3.9.jar` |
| `schema/perspective/<library>.components.json` | 7 add-on-library master indexes (see breakdown below), verbatim from the module jar |
| `schema/perspective/by-id/<id>.json` | one file per component (`ia.display.label`, `ia.chart.xy`, …), **82 files** |

### Module / library breakdown (live registry, 8.3.9, 2026-09-04)

| Library `*.components.json` | Module | N | Components |
|------|--------|---|-----|
| `ia.components.json` | perspective | 70 | `ia.container.*` (7), `ia.display.*` (26), `ia.input.*` (18), `ia.navigation.*` (4), `ia.shapes.*` (10), `ia.symbol.*` (5) |
| `perspective-amcharts.components.json` | perspective | 4 | `ia.chart.gauge`, `ia.chart.pie`, `ia.chart.simple-gauge`, `ia.chart.xy` |
| `perspective-timeseries.components.json` | perspective | 3 | `ia.chart.chartrangeselector`, `ia.chart.powerchart`, `ia.chart.timeseries` |
| `perspective-googlemap.components.json` | perspective | 1 | `ia.display.google-map` (needs a Maps API key on the gateway) |
| `perspective-map.components.json` | perspective | 1 | `ia.display.map` (Leaflet / OpenStreetMap) |
| `pdf-viewer.components.json` | perspective | 1 | `ia.display.pdf-viewer` |
| `barcode.component.json` | perspective | 1 | `ia.display.barcode` |
| `reporting-components.components.json` | reporting | 1 | `ia.reporting.report-viewer` |

The 7 add-on libraries ship **inside** the Perspective and Reporting module jars (not
separate modules). `ia.symbol.*` is **complete at 5** (`motor`, `pump`, `sensor`,
`valve`, `vessel`) — no extra P&ID symbol set is registered. **Symbol Factory** (module
present) contributes **no** Perspective components — its SVGs are used via
`ia.display.icon` / SVG import. **11** components are `deprecated` but still placeable:
`ia.container.drawing`, `ia.navigation.navlinks`, and the 9 legacy `ia.shapes.*`
primitives (use `ia.shapes.svg` + a coordinate container instead).

Each add-on `by-id/` file carries a top-level **`_source`** key citing the jar,
library and hash it was extracted from; the core-70 files have no `_source`.

Each `by-id` file:

```json
{
  "id": "ia.display.led-display",
  "name": "LED Display",
  "defaultMetaName": "LedDisplay",       // seeds meta.name when you drop the component
  "palette": { "category": "display", "variants": [ … ] },
  "schema": {                            // JSON Schema for props ONLY
    "type": "object",
    "required": [ … ],                   // often absent = nothing strictly required
    "properties": { "value": { "type": ["number","string"], "default": 0 }, … }
  },
  "childPositionSchema": { … },           // containers only — shape of each CHILD's position{}
  "events": { … },                        // optional
  "resources": [ … ]                      // css/js the component pulls (informational)
}
```

---

## Mapping a schema into a `view.json` component node

`schema.properties` → the node's **`props`** object. Everything else in the node
(`type`, `meta`, `position`, `propConfig`, `children`) comes from `resource-formats.md`
§4, **not** from this schema.

```json
{
  "type": "ia.display.led-display",          // = schema.id
  "version": 0,
  "meta": { "name": "flowLed" },             // unique among siblings; seed from defaultMetaName
  "position": { "grow": 0, "basis": "80px" },// keys come from the PARENT container's childPositionSchema
  "props": {                                 // keys + enums + types from schema.properties
    "value": 0,
    "segmentFormat": "7 segment",
    "numberFormat": "#,##0.0"
  },
  "propConfig": {                            // bindings — see resource-formats.md §6
    "props.value": { "binding": { "type": "tag", "config": { "tagPath": "…", "mode": "direct" } } }
  }
}
```

Rules:

- **Only emit props you set.** Omitted props fall back to `schema.properties.<p>.default`.
- **Respect `enum`.** A value outside the enum is rejected at parse.
- **`style`** on most components is `{"$ref": "urn:ignition-schema:schemas/style-properties.schema.json"}`
  — a free-form CSS-ish object (`backgroundColor`, `padding`, `fontSize`, `classes`, …).
  Not expanded in the by-id file.
- `position` keys are dictated by the **parent**:
  - inside `ia.container.flex` → `grow` (dflt 0), `shrink` (dflt 1), `basis` (dflt `"auto"`), `align`, `display` ( — `ia.container.flex.json` `childPositionSchema`)
  - inside `ia.container.coord` → `x`, `y`, `width`, `height`, `rotate` (required `x`,`y`) ( — `ia.container.coord.json`)
  - inside `ia.container.tab` → `tabIndex` (required) ( — `ia.container.tab.json` `childPositionSchema`)
- `meta.name` must be unique among siblings — it's the tree name and the identifier in
  `{parent.children.<name>.…}` expressions.
- **Expression language has no ternary.** `cond ? a : b` is not valid Ignition
  expression syntax — always `if(cond, a, b)`. Recurring authoring mistake worth a
  grep before treating an `expr` binding as done.

---

## Verified per-component gotchas

Each checked against its `schema/perspective/by-id/` file 2026-09-04.

### `ia.display.led-display` — ` — schema/perspective/by-id/ia.display.led-display.json`
props are exactly `value`, `segmentFormat`, `numberFormat`, `backgroundColor`,
`diodeOnColor`, `diodeOffColor`, `locale`, `style`. **No** `digitCount` / `label`.
- `value`: `["number","string"]`, default `0`
- `segmentFormat`: enum **`"7 segment"` | `"14 segment"`** (default `"14 segment"`)
- `numberFormat`: enum of pattern strings (`"#,##0"`, `"#,##0.00"`, `"0.0"`, `"#,##0%"`, `"0.###E0"`, …), default `"#,##0.00"`

### `ia.container.tab` — ` — schema/perspective/by-id/ia.container.tab.json`
- `schema.required` = `["tabs","currentTabIndex","menuType","tabSize","menuStyle","tabStyle","style"]`
- `props.tabs`: **array**, each item is either a bare string **or** `{"text": "…", "disabled"?, "runWhileHidden"?}`
- `props.currentTabIndex`: number, default `0`
- `props.menuType`: enum **`"classic"` | `"modern"`** (default `"classic"`)
- each child carries `position.tabIndex` (required) — the child at `tabIndex: N` is the body of tab N

### `ia.display.flex-repeater` — ` — schema/perspective/by-id/ia.display.flex-repeater.json`
- `props.path`: string, `format: "view-path"` — **project-relative** view path (`"templates/MetricTile"`)
- `props.instances`: array of param objects, one rendered view each; each may also carry
  `instanceStyle` / `instancePosition`. `additionalProperties: true` — your view's param
  names go straight in.
- other props: `direction`, `wrap`, `justify`, `alignItems`, `alignContent`,
  `elementStyle`, `elementPosition`

### `ia.display.view` (embedded view) — ` — schema/perspective/by-id/ia.display.view.json`
- `props.path`: string, `format: "view-path"`, project-relative
- `props.params`: object — keys must match the embedded view's `params`
- `useDefaultViewWidth` / `useDefaultViewHeight`: booleans

### `ia.display.table` — ` — schema/perspective/by-id/ia.display.table.json`
- `props.data`: `["array","dataset"]` — an **array of objects** (`[{"member":"…","value":"…"}]`),
  an array of arrays, or a Dataset. Object values may be a plain scalar or
  `{"value":…, "editable":…, "style":…, "align":…}`.
- `props.columns` (optional): array of column configs; `field` matches a key in the first
  data row; also `visible`, `editable`, `sortable`, `width`, `header`, `justify`, …
- ~26 props total (`virtualized`, `selection`, `filter`, `pager`, `rows`, `cells`, …) —
  read the file before using the advanced ones.

### `ia.container.flex` — ` — schema/perspective/by-id/ia.container.flex.json`
- props: `direction` (`row`|`row-reverse`|`column`|`column-reverse`), `wrap`, `justify`,
  `alignItems`, `alignContent`, `style` (default `{"classes":"","overflow":"auto"}`)
- no `defaultMetaName` — name children yourself
- children position: `grow`/`shrink`/`basis`/`align`/`display`

### `ia.display.label` — ` — schema/perspective/by-id/ia.display.label.json`
- props: `text`, `alignVertical`, `textStyle`, `style` — bind display text on **`props.text`**

---

## Add-on component libraries (`ia.chart.*`, maps, barcode, pdf, report)

These 12 are **not** in `ia.components.json` — each has its own
`schema/perspective/<library>.components.json` master and a `_source` key in its
`by-id/` file. They are registered by default on any gateway with the Perspective
module (Reporting for `ia.reporting.report-viewer`). Every chart prop below is
`type:"object"`/`"array"` with a deep sub-shape — **dump the `by-id/` file before
building one**, don't guess the nested keys.

### `ia.chart.xy` — ` — schema/perspective/by-id/ia.chart.xy.json`
- **`required` is everything**: `dataSources`, `title`, `subtitle`, `legend`, `cursor`,
  `enableTransitions`, `scrollBars`, `background`, `xAxes`, `yAxes`, `series`, `style` —
  emit all of them (drop `selection`, which is the one optional prop).
- `dataSources` is an **object** (named datasets), `xAxes`/`yAxes`/`series` are arrays.

### `ia.chart.timeseries` — ` — schema/perspective/by-id/ia.chart.timeseries.json`
- data goes in **`props.series`** (array of `{name,data}`) + **`props.plots`** (array —
  each plot references series and carries `trends`); `autoGenerateSeriesNames` default `false`.
- `enablePanZoom` default `true`; `timeRange` / `timeAxis` are objects.
- palette variants seed a full `plots` example — copy one from the `by-id` file.

### `ia.chart.powerchart` — ` — schema/perspective/by-id/ia.chart.powerchart.json`
- `required: []` but it is the Perspective **Power Chart** (operator trend tool) — the
  meaningful config is `pens` (array), `axes` (array), `plots` (array), `config` (object).
  Usually configured live by the operator; set `pens`/`axes` to preload trends.

### `ia.chart.gauge` / `ia.chart.simple-gauge` — ` — by-id/ia.chart.gauge.json`, `ia.chart.simple-gauge.json`
- `simple-gauge` is the lightweight one: flat props `value`, `minValue`, `maxValue`,
  `startAngle` (dflt 180), `endAngle` (dflt 360), `arc`, `arcBackground`, `label`.
- `gauge` (amCharts) has `outerAxis`/`innerAxis` **objects** with `ranges`, tick config,
  `data` (`"value"`|`"secondaryValue"`); `value` + `secondaryValue` are the needles.

### `ia.chart.pie` — ` — schema/perspective/by-id/ia.chart.pie.json`
- `props.data`: `["array","dataset"]` — array of `{ <category>, <value> }` objects.
- `labels` config uses the field names; `tooltipFormat` default is a template string
  `"{category} : {value.percent.formatNumber('#.0')}%"`.

### `ia.chart.chartrangeselector` — ` — schema/perspective/by-id/ia.chart.chartrangeselector.json`
- companion brush/range control for a time-series chart; `props.data` (array),
  `selectedRange` / `brushRange` objects — wire `selectedRange` to the chart's `timeRange`.

### `ia.display.map` — ` — schema/perspective/by-id/ia.display.map.json` (Leaflet / OSM)
- `required: []`. Center/zoom live in **`props.location`** and **`props.zoom`** (objects),
  markers/vectors/tile layers in **`props.layers`** (object, keyed groups).
- 11 events (`onMarkerClick`, `onMapClick`, `onMoveEnd`, …).

### `ia.display.google-map` — ` — schema/perspective/by-id/ia.display.google-map.json`
- **needs a Google Maps JavaScript API key** configured on the gateway (Perspective
  settings) or it renders an error tile.
- **`props.init` is the only required prop** — `{center:{lat,lng}, zoom}` seed; runtime
  center/zoom then live in `props.zoom` / other objects, not `init`.
- `gestureHandling` enum `cooperative|greedy|none|auto`; `tilt` enum `null|0|45`.
- ~100 events (every overlay type). `mapId` enables cloud-styled maps.

### `ia.display.barcode` — ` — schema/perspective/by-id/ia.display.barcode.json`
- `props.value` (`["string","number"]`), `props.type` — enum of **~100 symbologies**
  (`code128` default, `qrcode`, `datamatrix`, `ean13`, `pdf417`, …); an unsupported
  value renders via `errorStyle`.
- `displayValue` (dflt `true`), `valuePosition` `top|bottom`.

### `ia.display.pdf-viewer` — ` — schema/perspective/by-id/ia.display.pdf-viewer.json`
- `props.source`: URL/path to a PDF **served by the gateway or a reachable web server**
  (default is the bundled `/res/perspective/documents/pdf-sample.pdf`).
- `props.page` is read/write (current page); `props.pageCount` is readonly.

### `ia.reporting.report-viewer` — ` — schema/perspective/by-id/ia.reporting.report-viewer.json`
- **Reporting module** component. `props.source` = the report resource path
  (`"path/to/Report"`, project-relative); `props.params` object feeds the report
  parameters. `required`: `source`, `page`, `pageCount`, `zoomLevel`.
- `allowDownload` / `allowOpenInTab` default `true`; renders the report as PDF.

---

## Finding the right component

```bash
# list every registered component id (all 82, core + add-on libraries)
ls schema/perspective/by-id/ | sed 's/\.json$//'

# list one library's components with names
python3 -c "import json;[print(c['id'],'—',c['name']) for c in \
  json.load(open('schema/perspective/perspective-amcharts.components.json'))['components']]"

# dump one component's prop tree
python3 -m json.tool schema/perspective/by-id/ia.chart.xy.json
```

Worked builder examples that emit these nodes: `<repo>/scripts/build_views3.py` (templates,
tab page, live table, flex-repeater, indirect bindings), `<repo>/scripts/build_view.py`
(single overview view). The views they produced loaded cleanly on a live gateway.
