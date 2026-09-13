---
title: Reporting Module
description: Report design, data sources, export formats
---

> **Skill level:** 200 · **Read first:** [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 71-REPORTING-MODULE

# Reporting Module

Design and distribute reports (PDF, Excel, HTML).

## Resource format (verified against bytecode, 8.3.7, re-checked 2026-08-14)

No Report resource exists in any project on this install (checked every project on disk again 2026-08-14, still zero) - grounded in the real class `com.inductiveautomation.reporting.common.resource.ReportResource` (`data\jar-cache\com.inductiveautomation.reporting\*-reporting-common-7.3.7.jar`), not a live example.

- Resource type id: `com.inductiveautomation.reporting`, collection folder `reports` → on-disk `com.inductiveautomation.reporting/reports/<Name>/`. Confirmed via `ReportResource.RESOURCE_TYPE` (also referenced directly in `ReportingGatewayHook`, e.g. `new ResourcePath(ReportResource.RESOURCE_TYPE, ...)`).
- Real fields on `ReportResource`: `title`, `description`, `template` (a `PageTemplate` wrapping `com.inductiveautomation.rm.shape.RMDocument` - the report canvas, stored as `serializedRMDocument: String`), `dataConfig` (`ReportDataConfiguration`), `schedules` (list of `ReportSchedule`), `snapshot` (cached preview, `byte[]`).
- `ReportDataConfiguration` = `parameters: List<ReportParameter>` (`name`, `type: Class<?>`, `defaultValue: String`; two factory helpers `getStartDateParam()`/`getEndDateParam()` confirm Start/End Date are first-class, not user-invented) + `datasources: List<DataSourceConfig>` (`dataSourceId: String`, `configObject` - a polymorphic `DataSourceConfigObject`, serialized as raw `JsonObject` since Gson can't know the concrete subtype from the interface alone).
- The layout model is a licensed third-party Swing editor called ReportMill (`com.inductiveautomation.rm.*`), not something IA built on Ignition's own JSON-schema system - a real shape-tree object graph (`RMTable`, `RMTableGroup`, `RMGraph`, `RMText`, etc.), archived to/from a custom XML dialect via `RMArchiver`, not a JSON component tree like Perspective views and not covered by any single schema file the way `ia.components.json` covers Perspective. **Full shape vocabulary, the tag registry, and the annotation-driven property-panel layer are now extracted - see [72-REPORTING-SHAPE-MODEL.md](72-REPORTING-SHAPE-MODEL.md).** Note: `RMXYChart`/`RMPieChart`/`RMCategoryChart`/`RMTimeseriesChart`/`RMRadarChart` (under `rm2dshapes`/`j2dshapes`) are legacy classes not registered in the live archiver - the actual chart shape is the single class `RMGraph`, with a `type` attribute (`Bar`/`BarH`/`Area`/`Line`/`Scatter`/`Pie`).
- **This is load-bearing for how you build one**: the report canvas has no hand-authorable format. Unlike a Perspective view (`view.json`, plain JSON, editable by hand or by MCP `set_project_resource`), a report's layout only exists as this opaque serialized document, produced and consumed exclusively by the Designer's Reporting module UI. There is no schema to write JSON against and no confirmed API to construct one outside the Designer. Building a report means opening the Designer, not writing a resource file.

## Report Types

### Data-driven
- Pull data from database
- Display in tables, charts
- Use SQL queries

### Template-based
- Predefined layout
- Populate with data
- Reusable format

### Dashboard-style
- Graphs, KPIs, trends
- Embedded in Perspective view
- Interactive parameters

## Design Report

**Report Designer:**
```
Admin Console → Reporting → New Report
Name: DailyProduction
Description: Daily production summary
```

**Steps:**
1. Add data source (SQL query or named query)
2. Add page layout (table, chart, image, etc.)
3. Bind fields to query columns
4. Set parameters (date range, site, etc.)
5. Preview
6. Save

## Parameters

**User-provided inputs** (date range, site, filter).

```
Parameters:
- StartDate: type Date
- EndDate: type Date
- SiteName: type String
- Priority: type Integer
```

**In SQL query:**
```sql
SELECT * FROM orders 
WHERE date BETWEEN ${StartDate} AND ${EndDate}
  AND site = '${SiteName}'
```

## Data Sources

Verified against the concrete `QuerySource`/`ReportDataSource` implementations shipped in `reporting-gateway-7.3.7.jar` (`com.inductiveautomation.reporting.gateway.data(.queries)`). These are the real, exhaustive list of data source types available in the Designer's Data panel - anything not on this list does not exist as a source type:

| Class | Data panel source |
|---|---|
| `PrepStmtQuerySource` | SQL Query (parameterized/prepared statement) |
| `SimpleSqlQuerySource` | SQL Query (plain, unparameterized) |
| `NamedQuerySource` | Named Query |
| `TagHistQuerySource` | Tag History |
| `TagCalculationQuerySource` | Tag Calculation |
| `AlarmJournalQuerySource` | Alarm Journal |
| `StaticReportDataSource` | Static (manually-entered table, typed in the Designer) |
| `ScriptReportDataSource` | Script (Python, returns a dataset) |

There is no "Perspective Component" data source - that direction only runs the other way: a Perspective view embeds a *finished report* via the Report Viewer component, it does not feed report data. Live tag reads, SQL, named queries, tag history, tag calculations, alarm journal, a hand-typed table, or a script are the only inputs a report can pull from.

## Rendering

**On-demand.** Real signatures, verified via `javap` on `ReportScriptingFunctionsPyWrapper` (`reporting-common-7.3.7.jar`) - the doc's previous example was missing the required `project` argument and had the format param in the wrong slot:

```python
# system.report.executeReport(path, project, parameters={}, fileType='pdf') -> bytes
pdfBytes = system.report.executeReport(
    "DailyProduction",           # report path, relative to the project's reports root
    "AHU_Control_Demo",          # project - REQUIRED, not optional
    {"StartDate": "2026-08-01", "EndDate": "2026-08-14"},
    "pdf"
)

# system.report.executeAndDistribute(path, project, parameters, action, actionSettings)
# runs one of the report's own configured schedule actions on demand instead of returning bytes
system.report.executeAndDistribute(
    "DailyProduction", "AHU_Control_Demo", {}, "email", {}
)

# Discover what reports exist in a project:
system.report.getReportNamesAsList("AHU_Control_Demo")       # -> list[str]
system.report.getReportNamesAsDataset("AHU_Control_Demo")    # -> Dataset, includeReportName arg controls a name column
```

Confirmed dead ends: no `system.report` function takes a bare params dict without a project name, and format is a string among `pdf, html, csv, excel, rtf, jpeg, png, xml, xls` (`ReportFormat` enum, `reporting-common`) - `xlsx` is not one of the literal values, the enum constant is `EXCEL`.

**Scheduled.** Each `ReportSchedule` on the resource carries `enabled: boolean`, `cron: String` (a real cron string, not day-of-week prose - `DEFAULT_CRON_STRING` exists as a fallback constant), a `scheduleParameterMap` (per-parameter override + a `useValue` flag), and a list of `AbstractReportActionConfig` - see Distribution below for what those actually are.

**Export formats** (from `ReportFormat`, exhaustive): PDF, HTML, CSV, EXCEL, RTF, JPEG, PNG, XML, XLS.

## Embed in Perspective

**Report Viewer Component** (`ia.reporting.report-viewer`) - ships from the Reporting module itself (`reporting-components.components.json` inside `reporting-common-7.3.7.jar`), not from `perspective-common` like the other 81 components, which is why an earlier component-count pass here missed it. Real props, `required: ["source","page","pageCount","zoomLevel"]`, `additionalProperties: false` (the previous `reportPath`/`parameters` names below were wrong):

| Prop | Type | Notes |
|---|---|---|
| `source` | string | path to the report, required. Editor has a `report-paths` suggestion source. |
| `params` | object | not `parameters` - params to pass the report |
| `page` | number | current page, required |
| `pageCount` | number | read-only, required |
| `zoomLevel` | number | required. `1` = "Fit Panel"; suggestions run 25-200 |
| `allowDownload` | boolean | default `true`. Always false on iOS/Android regardless of setting |
| `downloadFilename` | string | defaults to the report's own name if blank |
| `allowOpenInTab` | boolean | default `true`. Always false in Workstation, iOS, Android |
| `controlStyle` | object | style of the control bar, separate from `style` |
| `style` | object | standard style object |

```python
# Perspective View → drag "Report Viewer" onto canvas, then:
ReportViewer.props.source = "DailyProduction"
ReportViewer.props.params = {"StartDate": self.view.params.dateFrom, "EndDate": self.view.params.dateTo}
```

## Common Report Elements

### Table
- Rows from SQL query
- Sortable, grouped

### Chart
- XY, TimeSeries, Pie, Bar
- Data from SQL

### Image
- Static logo, background
- Or dynamic from database

### Text
- Labels, headers, footers
- Static or dynamic from data

### Page Break
- Separate pages in output

## Report Styling

**Colors, fonts, layout:**
```
Report Properties → Appearance
- Font family, size
- Text color, background
- Margins, padding
- Page orientation (portrait/landscape)
```

## Distribution (Schedule Actions)

Each `ReportSchedule` holds a list of `AbstractReportActionConfig`. There are exactly 5 concrete subclasses (`SAVE_ID`, `EMAIL_ID`, `PRINT_ID`, `FTP_ID`, `RUNSCRIPT_ID` constants), verified via `javap` on `reporting-common-7.3.7.jar`:

| Action | Fields |
|---|---|
| `EmailActionConfig` | `format` (`ReportFormat`), `smtpServerName`, `toAddresses`/`ccAddresses`/`bccAddresses` (lists), `fromAddress` |
| `SaveFileActionConfig` | `path`, `fileName`, `format` |
| `PrintActionConfig` | `primaryPrinterName`, `secondaryPrinterName`, `copies`, `printBothSides`, `collate`, `useVector`, plus a `PrinterSource` enum (`DEFAULT`/`NONE`/`USER`) and `PrinterOrientation` (`PORTRAIT`/`LANDSCAPE`) |
| `FtpActionConfig` | `serverAddress`, `port`, `ftpUsername`, `ftpPassword`, `folderPath`, `fileName` |
| `RunScriptActionConfig` | `scriptString`, `format` |

All 5 are configured in the Designer under the report's Schedule tab, one schedule can carry several actions, each fires when that schedule's cron matches. This is the actual mechanism behind "email me the report every morning" - there is no separate emailing path; you don't call `system.net.sendEmail` with a rendered PDF, the module ships a real SMTP-backed `EmailAction`. Scripting a distribution manually (bypassing the schedule) is what `executeAndDistribute` above is for - it runs one of these action types on demand.

## Performance

**Large datasets** can be slow.

**Optimization:**
- Filter data in SQL (WHERE clause, not in report)
- Use summary tables (pre-aggregated data)
- Limit rows displayed (pagination)
- Avoid real-time updates in batch reports

---
**See:** docs.inductiveautomation.com/docs/8.3/modules/reporting

---

## See Also

**Prerequisites:** [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md)

**Builds toward:** [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md)

**Related:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
