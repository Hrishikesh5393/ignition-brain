---
title: Reporting Module - Canvas Shape Model
description: The ReportMill-derived shape/XML architecture behind the report canvas, extracted via javap from reporting-common-7.3.7.jar
---

> **Skill level:** 300 - internals, not day-to-day usage. **Read first:** [71-REPORTING-MODULE](71-REPORTING-MODULE.md)
> **You are here:** [00-INDEX](00-INDEX.md) > 72-REPORTING-SHAPE-MODEL

# Reporting Module - Canvas Shape Model

Install-verified 2026-08-14 against `data\jar-cache\com.inductiveautomation.reporting\*-reporting-common-7.3.7.jar`, Ignition 8.3.7. Everything below is read directly from bytecode (`javap -p -c`, `javap -v` for annotations), not inferred. Where something wasn't checked, it's marked as a gap, not filled in with a guess.

## Why this file exists, and why it looks nothing like 16-PERSPECTIVE-SCHEMA-TRUTH

Perspective ships one JSON file (`ia.components.json`) that declares all 82 components' schemas in one place. The Reporting module has no equivalent. What's actually in the jar is a licensed third-party Swing desktop editor called **ReportMill** (`com.inductiveautomation.rm.*` - `RMEditor`, `RMEditorPane`, `.rib` Swing menu/toolbar resource files, real toolbar PNGs), bolted into Ignition rather than built by Inductive Automation on Ignition's own JSON-schema system. The report canvas (`RMDocument`) is a tree of Java bean objects (`RMShape` subclasses), not a JSON component tree, and it round-trips to/from a custom hand-rolled XML dialect via `com.inductiveautomation.rm.archiver.RMArchiver` - not via Ignition's usual Gson/JSON machinery.

## The resource envelope vs. the canvas document

Two different serialization mechanisms are nested inside one `data.bin`, confirmed by decompressing a real (if empty) report resource created on this install:

1. **Outer envelope** - standard Java `ObjectOutputStream` serialization (magic bytes `AC ED`, after gunzip) of `com.inductiveautomation.reporting.common.resource.ReportResource` and its nested fields (`title`, `description`, `dataConfig`, `template`, `schedules`, `snapshot` - full field list in [71-REPORTING-MODULE.md](71-REPORTING-MODULE.md)). This part is a small, fixed 6-field POJO graph.
2. **Inner document** - `PageTemplate.serializedRMDocument` is a plain `String` field inside that envelope, holding base64-encoded **XML text**, e.g. a genuinely empty report decodes to exactly:
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <document version="14" show-margin="true" snap-margin="true" margin="36 36 36 36" null-string="&lt;N/A&gt;">
     <page width="612" height="792" />
   </document>
   ```
   This XML is produced/consumed by `RMArchiver` (extends `RXArchiver`), using its own minimal DOM (`RXElement`/`RXAttribute`), not `javax.xml` conventions.

This matters practically: the *outer* envelope is simple enough to construct with a short Java program against the real classpath. The *inner* document's shape vocabulary is what needed reverse-engineering, since there's no schema file for it - see below.

## The tag registry: `RMArchiver.createClassMap()`

Every `RMShape` subclass implements `Archivable` (`toXML(RXArchiver): RXElement`, `fromXML(RXArchiver, RXElement): Object`). `RMArchiver.createClassMap()` is the XML-tag-name-to-Java-class registry - the direct equivalent of Perspective's component `id` field, just built as a `Map<String,Class>` instead of a JSON array. Extracted via `javap -p -c` on `RMArchiver.class`, reading the `ldc` string constants in call order. The live, Designer-relevant tags:

| XML tag | Java class | What it is |
|---|---|---|
| `document` | `RMDocument` | root |
| `page` | `RMPage` | one page |
| `shape` | `RMShape` | generic/base |
| `rect` | `RMRectShape` | rectangle |
| `oval` | `RMOvalShape` | oval |
| `polygon` | `RMPolygonShape` | polygon |
| `star` | `RMStarShape` | star |
| `line` | `RMLineShape` | line |
| `image-shape` | `RMImageShape` | image |
| `text` | (`RMTextShape` subclass) | free text block |
| `label` | `RMLabel` | single label |
| `labels` | `RMLabels` | repeating label grid (mailing labels) |
| `linked-text` | `RMLinkedText` | text flowing across linked frames |
| `row-cell-text` | `RMTableRowCellTextShape` | a table cell's text |
| `table` | `RMTable` | data table |
| `table-group` | `RMTableGroup` | grouped/master-detail table |
| `tablerow` | `RMTableRow` | one table row definition |
| `graph` | `RMGraph` | generic ReportMill chart shape - NOT what the Designer's chart palette buttons create, see below |
| `graph-legend` | `RMGraphLegend` | chart legend (for `RMGraph`, not the native `RM*Chart` classes) |
| `ignition-rm-timeseries-chart` | `RMTimeseriesChart` | native Timeseries Chart - registered dynamically at startup, see Charts section |
| `ignition-rm-xy-chart` | `RMXYChart` | native XY Chart |
| `ignition-rm-bar-chart` | `RMCategoryChart` | native Bar Chart |
| `ignition-rm-pie-chart` | `RMPieChart` | native Pie Chart |
| `ignition-radar-chart` | `RMRadarChart` | native Radar Chart |
| `subreport` | `RMSubreport` | embedded sub-report |
| `switchshape` | `RMSwitchShape` | conditional visibility container |
| `flow-shape` | `RMFlowShape` | flow layout container |
| `spring-shape` | `RMSpringShape` | spring/anchor layout container |
| `painter-shape` | `RMPainterShape` | custom-drawn shape |
| `animpath` | `RMAnimPathShape` | animation path (PDF/print target, likely dead in Ignition context) |
| `scene3d` | `RMScene3D` | 3D scene |
| `sound-shape` | `RMSoundShape` | embedded sound |
| `morph` | `RMMorphShape` | morph shape |

Also registered but **not part of Ignition's actual palette**: a full set of `jbutton`/`jtable`/`jcombobox`/etc Swing-widget shapes (`com.inductiveautomation.rm.swing.shape.*`) and PDF-oriented extras. These are inherited wholesale from ReportMill's original desktop-app shape set. No evidence they're reachable from the Ignition Designer's Reporting palette - flagged as a gap, not confirmed dead, just unconfirmed live.

## RMShape - universal attributes (every shape has these)

From `RMShape.toXMLShape()`, `ldc` constants in order:

`name`, `x`, `y`, `width`, `height`, `roll` (rotation degrees), `scalex`, `scaley`, `skewx`, `skewy`, `useStroke`, `useFill`, `opacity`, `visible`, `url`, `hover`, `MinWidth`, `MinHeight`, `PrefWidth`, `PrefHeight`, `asize` (autosizing string), `LayoutInfo`, `locked`, `EnabledEvents`.

Fill/stroke/effect are separate registered element types (from the same `createClassMap` pass): `stroke`, `border-stroke` -> `RMBorderStroke`, `double-stroke` -> `RMDoubleStroke`, `fill`, `gradient-fill`, `radial-fill`, `image-fill`, `contour-fill` -> `RMContourFill`, and effects `blur-effect`, `shadow-effect`, `reflection-effect`, `emboss-effect`, `chisel-effect` (all under `com.inductiveautomation.rm.graphics.*`). Not individually extracted yet - gap.

## Table - `RMTable` / `RMTableGroup` / `RMTableRow`

`RMTable.toXMLShape()`: `list-key`, `filter-key`, `pagebreak`, `startbreak`, `startrowbreak`, `columns`, `column-spacing`.

`RMTableRow.toXMLShape()`: `title`, `structured`, `sync-pars`, `sync-alts`, `stay-with`, `reprint`, `print-always`, `move-to-bottom`, `min-split`, `min-remain`, `page-break-key`, `DeleteVerticalSpansOfHiddenShapes`, `ShiftShapesBelowHiddenShapesUp`.

`RMTableGroup.toXMLShape()` only self-identifies (`table-group`) - it composes `RMTable`/`RMTableRow`, no unique attributes of its own found at this pass.

**`list-key` is the actual data binding.** It's what ties a `table` shape to a dataset produced by one of the report's `DataSourceConfig` entries (SQL/Named Query/Tag History/etc - see 71-REPORTING-MODULE.md). Confirmed independently: decompressing IA's own stock "Tabular Report" starter template (`AHU_Last8Hours.TabluarReport` on this install) shows a `static_data` data source and a `setKey` call wiring a shape to it. Per-cell (`row-cell-text` / the `Text` shape property, see below) binding syntax within a row - e.g. exactly how a column value gets referenced inside a text shape's key expression - was not captured this pass. Gap.

## Charts - five real native classes, plus one generic ReportMill shape that is NOT what the palette uses

**Correction, 2026-08-15: the claim below that `RMGraph` is "the only chart shape" and that `RMXYChart`/`RMPieChart`/`RMCategoryChart`/`RMTimeseriesChart`/`RMRadarChart` are unregistered legacy classes was wrong.** They ARE the real, live chart engine - confirmed by decompiling `ReportingModule.class`, which calls `RMArchiver.registerClass(...)` for each of them *dynamically at gateway startup*. That's why the earlier pass, which only checked `RMArchiver.createClassMap()`'s static initializer, missed them - the registration happens in a different class, at runtime, not compiled into the archiver itself. Independently confirmed against a real Designer-authored reference file (the user dragged one of every chart type onto a canvas and saved it).

Real registered tags and classes, from `ReportingModule.class`'s `registerClass` calls:

| Designer palette button | XML tag | Class |
|---|---|---|
| Bar Chart | `ignition-rm-bar-chart` | `com.inductiveautomation.rm.shape.rm2dshapes.RMCategoryChart` |
| Pie Chart | `ignition-rm-pie-chart` | `RMPieChart` |
| Radar Chart | `ignition-radar-chart` | `RMRadarChart` |
| Timeseries Chart | `ignition-rm-timeseries-chart` | `RMTimeseriesChart` |
| XY Chart | `ignition-rm-xy-chart` | `RMXYChart` |
| (Barcode, same mechanism) | - | `RMBarcode` |

**Use the specific class matching the palette button, not `RMGraph`.** `RMGraph`/`<graph>` genuinely exists and parses fine, but it is the generic ReportMill shape, not what any Designer chart button creates - using it produces a chart with wrong/default styling (confirmed: building a report with `<graph type="Line">` rendered as a default gray 3D bar chart with placeholder "Series 1/Series 2" labels once Designer touched the file, even though the XML said `type="Line"`).

Real bean API, `RMTimeseriesChart`/`RMXYChart` (share a base, `RMAbstractXYChart`): `setDatasetKey(String)` (row source, = old `list-key`), `setDomainKey(String)` (x-axis column, e.g. `t_stamp`), `setPens(List<Pen>)` - one `Pen` per series, real **public fields** (not getters) `key`, `display`, `axis`, `style`, `color` (`java.awt.Color`), `dash`, `shape`, `weight`, `labels`, `fill`; `setAxes(List<ArchivableAxis>)`; `setLegend(boolean)`, `setShowXAxis(boolean)`, `setPlotBackground(Color)`.

`RMCategoryChart` (Bar Chart) bean API is different in shape - no `pens` list. Real setters: `setDatasetKey(String)`, `setColors(Color[])` (array, not `List`), `setExtractOrder(int)` (row vs column series extraction, no keys list needed - it auto-derives series from the dataset's columns), `setLegend(boolean)`, `setVertical(boolean)`, `setAxisLabel(String)`, plus `setRender3d`, `setPareto*` (Pareto-chart mode), `setLabels`/`setLabelFont`/`setLabelColor`.

`RMGraph$Type` enum still real for the generic shape (`Bar`, `BarH`, `Area`, `Line`, `Scatter`, `Pie` - all lowercase as XML attribute values: `bar`, `hbar`, `area`, `line`, `scatter`, `pie`, case-sensitive, confirmed by reading `setGraphTypeString`'s bytecode; a capitalized value like `"Line"` silently falls back to the `bar` default rather than erroring). Its `colors` attribute's join delimiter is the literal empty string (confirmed via constant-pool inspection, not comma-separated) - fragile enough that setting colors via the real `setColors(...)` bean method after parsing is the safer path regardless of which chart class is in use.

## The annotation layer - how the Designer's property panel gets its field names

Separate from the XML archiver, `com.inductiveautomation.reporting.common.api.shape` ships a set of **runtime-retained annotations** (`@ShapeProperty`, `@Preferred`, `@Options`, `@OrderBelow`, `@NumberFormatProperty`, `@DateFormatProperty`, `@HiddenProperties`, `@ReadOnlyProperties`, `@NonKeyMappable`, `@EditableIf`, `@EnumExclusions`, `@InitialSize`, `@CompoundProperty`, `@ShapeMeta`) applied directly to shape setter methods. Confirmed via `javap -v` on `RMTextShape.class`, e.g.:

```
public void setText(String) / replaceChars(...)
  @ShapeProperty("Text")
  @Preferred

public void setNumberFormat(String)
  @ShapeProperty("NumberFormat")
  @NumberFormatProperty

public void setDateFormat(String)
  @ShapeProperty("DateFormat")
  @DateFormatProperty
```

This is Ignition's own layer on top of stock ReportMill - it's what drives the Designer's property-panel labels ("Text", "Font", "NumberFormat", "NegativeRed", "DateFormat", etc. on `RMTextShape`) and presumably which fields show a "bind to data key" option (`NonKeyMappable` implies most others *are* key-mappable by default). This is a real, install-verified, per-setter declarative registry - unlike the XML tag names, it could be enumerated exhaustively per shape class with `javap -v` + grep for `RuntimeVisibleAnnotations`, one class at a time. Only done for `RMTextShape` so far - gap for `RMTable`, `RMGraph`, and the rest.

## What this enables, and what it doesn't yet

**Enabled:** hand-authoring a valid `RMDocument` XML string for simple cases (a page with a table and/or a single-series chart bound to a `list-key`) is now a verified-vocabulary exercise, not a guess. Combined with the already-verified outer envelope (`71-REPORTING-MODULE.md`), a short Java program (JDK + `reporting-common-7.3.7.jar` on classpath, both present on this install) could construct a real `ReportResource`, parse hand-written XML into it via `RMArchiver`, and serialize a real `data.bin` - a genuine write path, not hand-crafted Java serialization bytes.

**Not yet enabled:** multi-series chart key binding (`RMGraphPartSeries` internals), per-cell text key-expression syntax inside a table row, fill/stroke/effect element attributes, and the annotation layer for any shape besides `RMTextShape`. Treat a claim about any of those as unverified until checked the same way as everything above - `javap -p -c` for XML constants, `javap -v` + grep `RuntimeVisibleAnnotations` for the property-panel layer.

---

## See Also

**Prerequisites:** [71-REPORTING-MODULE](71-REPORTING-MODULE.md)

[Back to INDEX](00-INDEX.md) - [Knowledge Graph](KNOWLEDGE-GRAPH.md)
