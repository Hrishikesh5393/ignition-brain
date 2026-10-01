# Ignition 8.3 — Reporting, SQL Bridge, SFC, SECS/GEM and EAM

Source: live docs.inductiveautomation.com/docs/8.3 (Reporting, SQL Bridge/Transaction Groups, Sequential Function
Charts, SECS/GEM, Enterprise Administration, and the Report Design Components appendix — 108 pages, all read).
Trimmed to developer-relevant structure, properties, and behavior.

---

## Reporting module

### Resource model

- Reports are a **project-level resource**, under the **Reports** node in the Designer's Project Browser. Right-click → **New Report** (Blank or Tabular template).
- Shift-right-click exposes **Copy XML To Clipboard** / **Set XML From Clipboard** for copying a report definition between reports.
- Report Workspace tabs: **Report Overview** (name, thumbnail of last run, last/next execution time), **Data** (Parameters + Data Sources), **Design** (WYSIWYG layout, Key Browser left, Report Design Palette right), **Preview** (renders against live/sample data — the only place effects like Overflow Behavior, dynamic-key colors, or date/number formats are visible; Design view does not show them live), **Schedule** (cron schedule table + parameter overrides + distribution Actions).
- **Legacy reports** (pre-7.8 Vision Report Panel) still run unmodified. Right-click a Report Viewer → **Convert...** creates a new Report resource non-destructively; legacy custom properties become Parameters, but Data Sources must be added manually. Imperfect conversions: Narrow/Extended Code 39, Codabar, MSI barcodes (unsupported by new encoder); Charts (rebuilt, may need reconfiguration).
- Trial mode: full functionality, watermark on every page.
- Output formats: CSV, HTML, JPEG, **PDF (recommended)**, PNG, RTF, XML, XLS, XLSX. XLS/XLSX fidelity depends on the rendering spreadsheet app.

### Data tab

- **Order matters**: a Parameter/Data Source can only reference items *above* it in the list.
- **Parameters** (Date, String, Long, Double, Boolean, Dataset, Binary Data) are Ignition Expressions resolved at execution time. Every new report starts with `StartDate` (`dateArithmetic(now(), -8, "hr")`) and `EndDate` (`now()`). Default value precedence: Report Viewer / Scheduled Report override > default.
- **Data Source types** (8, each needs a unique Data Key except Script):
  - **Named Query** — runs a Gateway Named Query; parameters from Report Parameters; supports Nested Queries.
  - **SQL Query Data Source** — prepared statement, `?` placeholders bound to per-`?` parameter boxes; has a drag-and-drop Query Builder.
  - **Basic SQL Query** — pre-7.8 style, `{ParamName}` inline substitution (string params need quotes); dates often need manual `dateFormat()`/`dateArithmetic()` since the driver won't accept a raw Date object.
  - **Tag Historian Query** — like a Vision Tag History binding; indirection via typed `{ParamName}` (not `[{Param}]`), e.g. `[~]station {StationNumber}/paint pressure`.
  - **Tag Calculation Query** — Historian aggregates across the whole range → one row per tag path; multiple calcs per path in one query. **Min/Max is special**: always returns two rows per tag path (min + max), even if MinMax isn't requested, with other columns duplicated on both.
  - **Alarm Journal Query** — Journal history, or (checkbox) live alarm status instead (ignores Journal Name). Filters: dates, Include Events, Source/Provider/Display Path Filter (comma-separated, `*` wildcard), Search Filter, Min/Max Priority.
  - **Script** — Python script manipulating the `data` dict of all Parameters/Data Sources; conventionally placed last.
  - **Static CSV** — literal pasted CSV, all values as strings; good for prototyping.
  - All Query types support **Nested Queries** (per-parent-row re-run using `{parentColumnName}`), arbitrarily deep.
- **Scripting Data Source**: `data['key']` reads/writes simple params directly; for query sources, `data['key'].getCoreResults()` (Dataset, no nested data) and `data['key'].getNestedQueryResults()['SubQueryName']` (list of per-row child objects). `system.dataset.toDataset(header, rows)` builds a new/updated key.

### Data Keys

- `@KeyName@` placeholders; drag onto page → Text Shape (scalar) or Table (dataset), setting its Data Key. Escape literal `@` as `@@`.
- **Built-In Keys**: `Report.Gateway`, `Report.Name`, `Report.Path`, `Report.Timestamp`, `Date`, `Page`, `PageMax`, `Page of PageMax`, `PageBreak`, `PageBreakMax`, `PageBreakPage`, `PageBreakPageMax`, `Row` (table-only).
- **Show Calculations** toggle exposes aggregate sub-keys per key: `value`, `total`, `average`, `max`, `min`, `Running.total`, `Running.average`, `Running.count`, etc. (usable even hidden, e.g. `@total.NestedQueryKey@`).
- **Dynamic Data Keys** bind non-text properties (color, width, visibility) to a key — no `@`; drag key onto property or right-click → **Use dynamic data key**; revert via **Use static value**.
- Keychain path syntax: dot notation (`@Downtime.runInfo.operator@`), array indexing (`@dataSource[0].columnName@`).
- **Reserved column names** (never as key/column headers): `Running`, `Remaining`, `Up`, `total`, `average`, `count`, `countDeep`, `max`, `min`.

### Keychain Expressions

A distinct expression language, evaluated only inside `@...@` (or unquoted, in a Dynamic Data Key field) — not the main Ignition Expression Language.

- Operators: `()`, `* / %`, `+ -`, comparisons, `&&`/`AND`, `||`/`OR`, ternary `cond ? a : b` (false branch optional, `null` falsy), and assignment `=`/`+=` for report-scoped temp variables (e.g. `@revTotal=0@` then `@revTotal+=revenue@` as an alternative to Running keys).
- Math: `floor`, `ceil`, `round`, `abs`, `min`, `max`, `pow` (return floats). String: `startsWith`, `endsWith`, `substring(str, start[, end])`, `join(list, keychainOnEach, delimiter)`.
- Colors: hex (`"0000FF"`, optional alpha digits), named color string (`"red"`, `"clear"`=zero opacity), or a String Parameter via the `color()` expression function for dynamic theming.

### Design tab / Report Design Components

Palettes: **Object** (Report, Page), **Table** (Table, CrossTab, Simple Table), **Display** (Barcode, Images, Labels), **Chart** (Bar, Pie, Radar, Timeseries, XY), **Shape** (Line, Rectangle, Ellipse, Star, Polygon, Pencil, Text). Single-click selects the outer object; double-click ("super-select") drills into a group/template/polygon/pencil. Z-order/grouping/union-difference/alignment on the Component menu; page add/remove on the Pages menu.

All components share common geometry (`Roll`, `Scale X/Y`, `Visible`, `Width`, `Height`, `X`, `Y`, `URL` — clickable PDF link, supports `Page:Next`/`Page:Back`/`Page:<N>` nav tokens) and most expose `Use Raster`.

**Object palette**

| Component | Key properties |
|---|---|
| Report | Paper Size/Dimensions (Units: Inch, Point=1/72in, Centimeter, Millimeter, Pica=1/6in), Orientation, Margins (Show/Snap), Grid Spacing (default 9pt), Snap to Grid, **Bypass Image Cache**, **Page Layout** (Single/Double/Quadruple/Facing/Continuous/ContinuousDouble), report-wide **String for Null** |
| Page | Menu: Add Page, Add Page Previous, Remove Page; `Hidden` (bindable to a dynamic data key) |

**Table palette**

| Component | Key properties |
|---|---|
| Table | Data Key, Grouping, Rows (Header/Details/Summary, each Structured/Unstructured), Sorting (Default/Basic/TopN w/ Include Others), Page Break, **Table Repeat Count** (renamed from "Column Count"), Column Spacing, Filter Key, Starting Page Break; **Make Table Group** button → Configure TableGroup (add Child/Peer tables, reorder, per-table Start on new page/New page per row) |
| Simple Table | Data Key, Columns, Rows, Header Columns/Rows, Filter Key, Style presets; dynamically sized; places data directly in spreadsheet cells on XLS export (vs Table's overlay) |
| CrossTab Table | Same Style properties + cell Grouping to pivot two categorical columns against an aggregate |

**Display palette**

| Component | Key properties |
|---|---|
| Barcode | Data Key, Barcode Format (Standard: Codabar, Code39, Code128, EAN_8/13, ITF, UPC_A; 2D: Aztec, Data_Matrix, PDF417, QR_Code), Show Text, Font. GS1-128 via Code128 + 4 GS1 escape chars (ñòóô) |
| Images | Key (byte array/URL/file path, resolved on the **Gateway**), drag-drop from disk/Image Mgmt Tool/webpage (embeds directly, no Key). Grow to Fit, Preserve Aspect Ratio, Padding, Page Index, Radius. Keychain Expressions not usable directly in Key — go through a Parameter/Data Source |
| Labels | Data Key (Dataset), Label Formatting (Avery presets/Custom), Rows/Columns, Label/Spacing Width/Height (live-resizes). Super-select the top-left template label to edit Text/Image/Barcode/Keychain content, replicated to all cells |

**Chart palette** — all 5 share Data Key, Scripting Enabled + Edit Script (`configureChart` JFreeChart hook), Opacity/Stroke/Fill, standard geometry.

| Component | Key properties |
|---|---|
| Bar Chart | Extract Order (Row/Column), 3D, **Pareto** (descending + 80% line), Render Style (Bars/Stacked/Layered), Segment Colors, Category/Item Margin, Axis Autorange/Low/High/Format/Label, Bar Labels |
| Pie Chart | Label Key, Value Key, Segment Colors, Label Style (None/Simple/Outset), Label Format (`{0}`name/`{1}`value/`{2}`%), Style (Pie/3D/Ring), Sort Order, Section Outline, Chart Shadow |
| Radar Chart | Extract Order (Row→Series Key/Column→Variable Key), Series/Variable Colors, Axis Color, Start Angle, Rotation (CW/CCW), Axis Label Gap |
| Timeseries Chart | Domain Key (timestamp), Pens (Range Key, Pen Name, style/color), Axes (Name/Label/Auto/Low/High), Bar Width (ms), Date Format, Gap Threshold (multiplier of avg spacing → treat as gap), No Data Msg |
| XY Chart | Same as Timeseries but numeric Domain Key; adds Margin and Number Format for x-axis |

**Shape palette** — Fill/Fill Color/Opacity + Stroke Style (Hidden / Shape Outline (Color, Dash Pattern, Width) / Border (+ per-edge toggles) / Double (Color, Inner/Outer Width, Position, Separation)).

| Component | Key properties |
|---|---|
| Ellipse | Start Angle, Sweep Angle (0=line, 360=oval); Shift forces circle |
| Line | Stroke Color/Width; Shift forces 45°/90° |
| Rectangle | Radius (rounded corners); Shift forces square |
| Star | Bloat, Points, Star Type (Star/Polygon) |
| Polygon | Click vertices, click start to close; double-click edge to reshape |
| Pencil | Freehand; auto-closes if ended inside the origin square, else stays open |
| Text Shape | Text, Text Color, Character Spacing, Coalesce Newlines, Font, H/V Alignment, Line Spacing, Margin, **Overflow Behavior** (Paginate vs Shrink text to fit), Underlined, Date/Number/Null Format, Negative in Red, Radius. Limited HTML subset when value is `<html>...</html>` and field contains `@html@`: `<br> <b> <i> <em> <u> <font size='1-7'> <font color='name|#hex'> <sup> <sub> <left> <center> <right>` |

### Nesting, table groups, grouping (disambiguation)

- **Grouping Data Inside of Tables** — breaks one dataset's rows into sub-headers by a shared column value (drag key into Grouping list); each level gets its own Header/Details/Summary and level-scoped aggregate keys; optional Page Break per grouping instance.
- **Table Groups** — one Table hosting multiple independently-configured tables: **Peer** (second table starts where the first ends, for unrelated datasets shown back-to-back) or **Child** (nested inside parent rows — ideal for Nested Query results). Relationship is always relative to immediate neighbor in the hierarchy tree. **Start on new page** forces a fresh page for that table.
- **Charts Inside of Tables** — place in an unstructured Header row (once, top of page 1) or unstructured Details row (repeats per parent row — typically paired with Grouping/Nested Queries for one chart per group).
- **Table Row Versioning** — conditional row formatting: Standard, First Only, Reprint, Alternate, TopN Others, Split Header, or **Custom** (named, selected via a `Version Key` expression string match). **Sync Alternate Versions** keeps a version's widths matched to Standard automatically.
- **Structured vs Unstructured rows** — structured = fixed Text-Shape columns (`Column Count`), Text Shapes only; unstructured = free placement of any component.

### Pagination

- `Reprint When Wrapped` on Header rows; auto-shrink text to avoid truncation.
- `Min. Remainder Height` / `Min. Split Height` (default 72pt) controls whether a tall row (e.g. containing a chart) splits across a page boundary or moves whole to the next page — raise both to avoid ugly splits.
- `Page Break` at table level → break after each grouping instance; at row level → accepts a data key/expression for per-row force-break.
- `Stay with Children` keeps a header/parent bound to N children even if some overflow the page.

### Report scripting API

- **`system.report.*`** — execute/distribute reports on demand from any script scope.
- **Chart scripting**: `Scripting Enabled` + Edit Script on Timeseries/XY/Bar exposes `configureChart`, run right before rendering; charts are JFreeChart objects (`chart.getPlot()`, `plot.getRangeAxis()`, `plot.dataset`, `DatasetUtilities.findRangeBounds()`) — see JFreeChart Javadocs. Common use: dynamically clamp/pad axis range based on actual data.
- **Run Script Action** exposes `handleFinishedReport(reportName, reportPath, dataMap, reportBytes)` for archiving/custom distribution. `dataMap` is the Data tab's raw configured values (not Design-tab calculated values); rows accessed by index with `getKeys()`/`getKeyValue()`.

---

## Report scheduling and distribution

### Schedules

- Multiple named schedules per report, each with its own Cron pattern (preset dropdown or manual builder) and Enabled flag.
- Presets: Once Per Hour `0 * * * *`, Twice Per Day `0 0,12 * * *`, Once Per Day `0 0 * * *`, Once Per Week `0 0 * * 0`, 1st & 15th `0 0 1,15 * *`, 1st of Month `0 0 1 * *`, 1st Monday `0 0 1-7 * 1`, Last Day of Month `0 0 L * *`, Once Per Year `0 0 1 1 *`.
- Execute on **Gateway local time**.
- Parameters tab per-schedule overrides any report Parameter default, including binding to a live Tag (`{TagPath}`).

### Actions

| Action | Notes |
|---|---|
| Print | Primary/Backup Printer, Print Mode (**Vector** — requires `Use Raster=false` on Chart/Barcode components or it falls back to raster; vs **Raster**, always rasterized), Copies, duplex, Collate, AutoLandscape, Page Orientation |
| FTP | Server Address, Port, Folder Path, Format, Username, Password, SSL, expression-built Filename |
| Save File | Folder Path (relative to the **Gateway** OS), Format, expression-built Filename |
| Email | Needs a configured SMTP profile. From Address must match SMTP profile username if multiple servers configured. Address Source: Email Addresses (To/CC/BCC/ReplyTo) or User Roles (Recipient User Source + Roles, optional ReplyTo User Source + Roles). Subject/Attachment Filename/Body all expression-built |
| Run Script | Calls `handleFinishedReport()`; Format controls `reportBytes` content |

### Distribution troubleshooting

- Silent action failures: check report execution/schedule status and Gateway logs; SMTP failures retry up to the Email Action's `Retries` count.
- Save/FTP paths resolve against the **Gateway server's OS** — a Windows path silently fails on a Linux Gateway and vice versa.
- Reports execute on the Gateway even for on-demand `system.report.*` calls from a Client — client-side paths are never valid targets.

---

## SQL Bridge / Transaction Groups

### Overview

User-configured collections of data references (**Items**) linked to columns of a SQL table (or a stored procedure), requiring no SQL knowledge — Ignition can auto-create/maintain the target table. Groups run entirely on the **Gateway**, independent of any Client/Session once enabled and saved.

### Group types

| Type | Direction | Behavior |
|---|---|---|
| Historical Group | one-way, OPC/Tag → DB | Simplest; inserts a new row per execution; cannot update or write back. Alternative to Tag Historian for full SQL-schema control. |
| Standard Group | bi-directional | Most flexible: insert new row, or update/select first/last/custom/key-value-pair row. Historical logging, status-table maintenance, recipe pull-down, PLC-to-PLC sync. |
| Block Group | bi-directional, multi-row | **Block Items** (List mode, or Pattern mode with `{?}` wildcard) write an ordered list of values vertically as rows in one execution — efficient for arrays (e.g. 100x100 in a few hundred ms). Optional `row_id`/`block_id` columns. Table Action adds Insert New Block / Insert changed rows. |
| Stored Procedure Group | bi-directional via SP params | Items map to IN/INOUT (write) or OUT/INOUT (read back via item's `Output` column), addressed by name or 0-indexed position (not mixed); Oracle/PostgreSQL require indexed params. RSSQL migration path. |

### Items

- **OPC Item** — subscribed directly to an OPC server at the group's rate; bypasses Tags/Tag Groups.
- **Tag Reference Item** — references an existing Tag, updates per the tag's own Tag Group/scan class; useful for sharing a common trigger across groups.
- **Expression Item** — `None` (static), **Expression** (Ignition Expression Language, can reference other group items/tags), **SQL Query**, or **Named Query**; scoped to its own group; items execute top-to-bottom (lower items see prior execution's value from items above unless reordered).
  - **Run-Always** items evaluate every cycle before the trigger check (can serve as the trigger itself); **Triggered** items evaluate only when the trigger fires (or every cycle if no trigger configured).
  - Gateway/group restart or editing the Expression Item resets Hour/Event meter accumulation.
- **Value Mode**: Direct Value, **Hour Meter** (accumulate time source is non-zero; `On Zero` flips polarity; `Retentive` preserves value while not accumulating), **Event Meter** (count value-changes to non-zero; target must be Integer).
- **Write Target**: None (read-only), Database field, or (Expression Items only) Other Tag (write back into another group item).

### Hour and Event Meters

Hour Meter accumulates ms/s/min/hr/day while a condition is true, resets on false; target = Other Tag on a numeric tag. Event Meter counts false→true transitions, target must be Integer. Either can reset on condition (Reset on condition + Group Tag + comparison operator/threshold).

### Triggers

- **Only evaluate when values have changed** (All tags or Custom selection).
- **Execute this group on a trigger** — pick a Run-Always item, condition `!=0`/`=0`/active/non-active/**Active on value change**.
- **Only execute once while trigger is active** — rising-edge only.
- **Reset trigger after execution** — writes opposite value back (ack relay).
- **Prevent trigger caused by group start** — suppresses spurious first-eval fire.

### Handshakes

Write a success and/or failure value back to a chosen item after each execution, signaling outcome without polling.

### Update modes

| Mode | Behavior |
|---|---|
| OPC to DB | one-way, OPC/Tag → DB |
| DB to OPC | one-way, DB → OPC/Tag |
| Bi-directional OPC wins | both sync; on start, if values differ, OPC overwrites DB |
| Bi-directional DB wins | both sync; on start, if values differ, DB overwrites OPC/Tag |

Historical Groups only support OPC to DB.

### Table Action

`Insert New Row` / `Update/Select` with target strategy **First**, **Last**, **Custom** (raw SQL WHERE, can reference item values via Tag-insert icon), or **Key/Value Pairs** (UI-built WHERE clause; supports **Insert row when not present** = upsert without hand SQL).

### Execution cycle

1. Timer/Schedule fires. 2. Skip if paused or this Gateway is the inactive redundant node. 3. Evaluate Run-Always items. 4. Check trigger (abort cycle if inactive). 5. Evaluate Triggered Expression Items. 6. Read from DB (DB-to-OPC direction). 7. Compare items to targets; execute writes. 8. Report configured alarms. 9. Acknowledge trigger / write handshake.

DB-connection failure requires **manually restarting** the group. With Bypass Store and Forward off (default for insert-type groups), a write counts successful once it enters the Store-and-Forward pipeline.

### Execution scheduling

- **Timer** — fixed rate, timed from group enable/start.
- **Schedule** — comma-separated clock times/ranges (`8:00, 15:00, 21:00`, `8am-11am, 3pm-5pm`, midnight-spanning `9pm-8am`); ranges auto-align to range start regardless of enable time (e.g. `9am-5pm` @ 30min fires 9:00, 9:30... daily) — the mechanism for "on the hour" requirements Timer mode can't guarantee.

### Advanced settings (Options tab)

`OPC Data Mode`: **Subscribe** (default, on-change, best perf, but a fast-changing value may lag a cycle) vs **Read** (actively re-reads every item at execution — guarantees a consistent snapshot, used for batch/interlocked data). Also: Bypass Store and Forward, Override OPC subscription rate, Always store NULL for bad quality, Set NULL tag/DB values to type default (numeric→0, Boolean→FALSE, String→`''`, Date/Time→now, Dataset/Array→empty).

### When to use vs. Named Query / Gateway script (legacy status)

Nothing in the 8.3 docs marks Transaction Groups as deprecated or removed — the module remains fully supported and documented. But it predates, and today sits alongside, **Named Queries** + hand-written **Gateway scripting** (`system.db.*`/`system.tag.*` driven by Timer/Tag Change/Scheduled scripts), which newer guidance elsewhere in the manual generally favors for new development. Transaction Groups are best reached for specifically for: no-SQL-required table creation, built-in Update-Mode "wins" semantics for bi-directional sync/recipe patterns, Hour/Event meter accumulation (no equivalent in Named Queries/Tag scripting), non-SQL-fluent configuration staff, and RSSQL migration (Stored Procedure Group). A Named Query + Gateway script is generally better when logic needs branching/error handling beyond an expression, multiple queries in one logical transaction, or an existing Named Query library should stay the single source of truth.

---

## Sequential Function Charts

### What they are / when to use them

Python scripts organized as chart elements executed in a defined flow, based on IEC 61131-1. Built in the Designer but always **execute on the Gateway**, independent of any Client, and **not scoped to a project** — one shared SFC folder serves all projects on that Gateway. Best fits: parallel processes (Parallel element, no manual thread/sleep management), guaranteed-order multi-step processes, complicated multi-step processes needing visual troubleshooting, linked/encapsulated processes (step code can only be invoked by the chart itself — a deliberate security boundary).

### Chart elements

| Element | Purpose |
|---|---|
| Begin / End | Exactly one implicit Begin (Chart Parameters + optional Key Param identifier); any number of Ends (chart stops on reaching one; none needed if looping forever) |
| Action | Holds actions: **On Start** (once, to completion, before anything else), **On Stop** (once, after any in-flight action finishes), **Timer** (repeats every N ms, starts only after On Start finishes, may never fire if told to stop first), **Error Handler** (runs if another action throws; if it throws too, chart Aborts). Sees chart's shared `chart.*` scope plus a private step-lifetime "step scope" |
| Assertion | Checks chart-parameter conditions; passes or fails/aborts flow |
| Transition | Boolean gate (Ignition Expression Language); optional timeout flips a chart-scoped boolean flag after N time |
| Parallel | Bounded region (branch line top, sync line bottom); contained elements run concurrently, flow continues past sync only once every branch's exit condition is met |
| Jump / Anchor | Single-character-keyed shortcut link; Parallel sections have a separate jump/anchor namespace (can't jump in/out of a Parallel) |
| Enclosing | Invokes another chart (subchart) from a parent chart; relative paths (`./sibling`, `../uncle`). Execution Mode: **Block** (wait for subchart End) or **Cancel** (cancel subchart when ready to stop). Parameters pass as expressions; return values map subchart-scope vars back to parent scope, including onto Chart Scoped Variables |
| Note | Documentation only |
| Link | Directional connector; cannot cross above/below other elements/links; flow must enter the **top** of an element (entering bottom = compile error) |

### Chart flow and rules

Flow generally top-to-bottom, can loop bottom-to-top. Before exiting an Action: a next element must be reachable, and the active step must finish any running script. Multiple open Transitions → **left-most path wins**. Compile errors (red triangles, toggle Show Errors): flow into element bottom; disconnected elements; dangling links (incl. inside Parallel); flow into multiple Actions simultaneously outside Parallel; End Steps **not allowed** inside Parallel. Charts need no End Step — can loop indefinitely or idle on a false Transition.

### Chart lifecycle / states

Active: Starting (On Start fires) → Running → Pausing (finishes in-flight, starts none new) → Paused → Resuming. Terminal: Stopping→Stopped (normal End Step, On Stop fires), Aborting→Aborted (action threw; `chart.abortCause` available only in On Abort script), Cancelling→Cancelled (external cancel; On Cancel fires, not On Stop). Numeric `chart.state`: 0 Aborted, 1 Aborting, 2 Canceled, 3 Canceling, 4 Initial, 5 InitPaused, 6 Paused, 7 Pausing, 8 Resuming, 9 Running, 10 Starting, 11 Stopped, 12 Stopping, 13 Suspended, 14 RedundantInactive.

### Chart properties

- **Execution Mode**: Callable (via `system.sfc.startChart`, Enclosing Step, or Designer Chart Control Start; unlimited concurrent instances), RunAlways (Gateway auto-starts on startup; not restarted automatically if it ends — design to loop forever), Disabled.
- **Persist State** — on clean Gateway shutdown, running state + chart-scoped variables save to disk and resume on restart, only if the chart was between script executions when shutdown arrived (design for frequent, short scripts). Power loss isn't captured; pair with Redundancy.
- **Redundancy Sync** — syncs chart state/parameters to the backup node; sync points occur only when a new step starts — call `system.sfc.redundantCheckpoint` for intermediate state in long steps. `On Redundant Failover` gets `activeSteps` and `restartAction` dict (`cancel=True` or `goto="S2"`; cannot target a step inside Parallel).
- **Event Scripts**: On Start, On Stop (normal End-Step only), On Cancel, On Abort (exposes `chart.abortCause`), On Redundant Failover.

### Chart scope and variables

- Each instance gets a private free-form name→value scope; Begin-step Chart Parameters seed it (overridable at start), one may be flagged **Key Param** as external identifier.
- Action scripts: `chart.varName = value` reads/writes; undefined names auto-create.
- Transition expressions (Expression Language, not Python): `{varName}` references chart scope, e.g. left Transition `{counter} < 100`, right `true`.
- Built-ins: `chart.instanceId` (UUID string), `chart.startTime` (java.util.Date), `chart.runningTime` (seconds, int), `chart.parent` (enclosing chart's scope or null), `chart.running` (bool), `chart.state` (int), `chart.abortCause` (On Abort only).
- **Reserved words** (collide with Python dict methods, since chart scope is dict-backed): `clear, copy, fromkeys, get, has_key, items, keys, setdefault, update, values`.
- SFC parameters **cannot store a whole QualifiedValue** — extract `.value` first.

### SFC scripting API

`system.sfc.*`: `startChart` (invoke Callable chart), `pauseChart`/`resumeChart`, `cancelChart`, `setVariable` (write a running chart's scope from outside, e.g. from a client message-handler reply), `redundantCheckpoint` (manual sync point in a long Redundancy-Sync step).

### Interaction / monitoring

Chart instances run on the Gateway — no direct UI interaction. Use `system.util.sendMessage` from the chart to a Client message handler for notifications; client calls `system.sfc.setVariable` to push input back (paired with a Transition gated on that variable). Vision **SFC Monitor** component visualizes running instances. In the Designer, double-click a running instance in Chart Control to enter Monitor View. **Chart Recording** (disabled by default; Gateway → SFCs → Settings) captures execution detail for Designer replay. **Debug Mode**: right-click → Toggle breakpoint; Chart Control gains Debug/Step/Continue; **Begin Here** starts a fresh instance at an arbitrary element.

### Design patterns

Avoid blocking calls (`sleep()`/`wait()`) in Action scripts — let Transitions own pausing/waiting; only unavoidable I/O should block. Refactor large loops into a **Timer Action** (increment chart-scoped counter, gate Transition on `{counter} >= N`) or a **Chart Loop** (processing step + two-way Transition pair) instead of one long-running `while` — keeps scripts short, required for pausability/persistence/redundancy sync. Put logging in **On Abort** since the three terminal states don't self-explain *why* they ended.

---

## SECS/GEM

### Overview

Implements SEMI's **GEM** (E30), **SECS-II** (E5), **HSMS** (E37), **SECS-I** (E4) standards, acting purely as a **host** (never equipment). Each **Equipment Connection** talks to one tool over HSMS (Ethernet/TCP-IP) or SECS-I (RS-232 serial), and needs an associated DB connection for message auditing/config (connections can share or use separate DB connections/table prefixes).

Terms: **Stream/Function** (`S#F#` — stream = category, function = specific message; odd=request/primary, even=response/secondary), **SDL file** (validates every message; undefined messages are rejected → logged to Errors table), **Transaction/TransactionID (TxID)** — request+response pair, a 32-bit int ("System Bytes" at protocol level).

### Equipment connections

- Common: Equipment Name/Description, Enabled, Device ID (default 0), Database Connection, Database Table Prefix, SDL File (falls back to built-in `messages.sdl`), **T3 Reply Timeout** (default 45s).
- Ethernet/HSMS-only: Active/Passive IP+Port, Connection Mode (Active/Passive/Alternating), **T5** Connect Separation (10s), **T6** Control Transaction (5s), **T7** Not Selected (10s, Passive only), **T8** Network Intercharacter (5s), Keep Alive Timeout (LinkTest interval, default 300s, 0 disables).
- Serial/SECS-I-only: Serial Port Name, Data Bit Rate, **T1** Inter-Character (0.5s), **T2** Protocol (10s), **T4** Inter-Block (45s), Retry Limit (3).
- DB tables: `SECSGEM_EquipmentInfo` (one row per connection sharing that DB connection, no prefix), `<prefix>Messages` (every sent/received message as JSON: StreamFunction, Direction, RequestResponse, CommonID, TxID, Reply, timestamp), `<prefix>Errors` (validation/connection/timeout failures). Not auto-pruned.
- Equipment page shows Active/Errored connection counts, aggregate throughput, per-connection Sent/Received + status (**Not Connected** on fault); View Details adds live throughput stats.

### SDL file

JSON with `doc`, `formats` (SECS datatypes: A, B, Bool, U1/U2/U4/U8, I1/I2/I4/I8, F4/F8, L, J, Local, B64; composite groups I/U/F bundle sizes), `items` (reusable named definitions: doc, allowed formats, byte length, codes enum table), `messages` (per S#F#: doc, block single/multiple, direction h->e/h<-e/h<->e, reply bool, body structure, optional CommonID, realtime, SQLTags), `defaults` (fallback values for omitted message properties). Editable in-browser via Gateway Edit File action (download/upload also supported); equipment connection **must restart** after saving. Stock `messages.sdl` ships the full SEMI standard catalog pre-defined.

### SECS message basics / scripting surface

- Messages represented as structured JSON (or Python dict from scripting): `header` (doc, stream, function, reply) + `body` array of items/nested lists.
- `system.secsgem.sendRequest(streamFunction, replyExpected, body, equipmentName)` → TransactionID; `system.secsgem.getResponse(transactionID, equipmentName)` retrieves reply.
- **Messages through Tags**: mark `"SQLTags": true` (+ `CommonID` list) → auto-surfaced as read-only, non-persistent tags under the equipment connection's SECS/GEM Realtime Tag Provider (recreated every Gateway restart).
- **Messages through Message Handlers**: mark `"realtime": true` → invokes Gateway/Client Event Script Message Handler named exactly `onSecsGemRealtimeUpdate` (configured per-project, separate Gateway vs Client settings). Only for messages that can originate from equipment. `payload` keys: CommonID, Equipment, Direction, RequestResponse, TxID, Reply, Message (JSON string).
- **Custom Message Response Handlers** override automatic SDL replies, configured per S#F# under the connection's Custom Responses page (Enabled, Intercept Stream Function, Gateway Message Handler name + Project); handler calls `system.secsgem.sendResponse`. One custom response per S#F# per connection; works for SECS-I too.
- `system.secsgem.sendMessage` — general send entry point outside the request/response pattern.

### Simulators

Implements GEM Communications/Control State Models; auto-responds to a fixed default set (S1F1, S1F3, S1F11, S1F13, S1F15, S1F17, S2F13, S2F15, S2F17, S2F23, S2F29, S2F31, S2F33) — anything else defined but not listed is rejected unless covered by an Echo Response. Own SDL adds `Status Variables` (svid, name, units, format, value, optional eventTriggers ceid+newValue firing a Collection Event), `Equipment Constants` (ecid, name, min/maxValue, format, defaultValue, units; via S2F13/S2F15), `Echo Responses` (fixed request→response map), `Event Runs` (scheduled S6F11 sequence, configurable delay, manually started, runs in order — all referenced CEIDs/RPTIDs/variables must already exist in the SDL). Edited via Gateway → Connections → SECS/GEM → Simulators → Sim Variables; restart after saving.

### Troubleshooting

Port conflicts (equipment connections and simulators need unique ports) are the most common setup failure. Message failures land in the Errors table; logging severity per-equipment (TRACE logs every SECS message). `wrapper.log` (Windows: `Program Files\Inductive Automation\Ignition\logs`; Linux: `/var/log/ignition`; macOS: `/usr/local/ignition/logs`). MySQL: verify latest JDBC driver if DB tables aren't auto-created.

---

## Enterprise Administration Module (EAM)

### Controller/agent model

**Controller** — single Gateway per Gateway Network managing/monitoring **agents**, assigning/tracking Gateway Tasks. **Agent** — every other participant; executes tasks, reports status. Requires a Gateway Network connection agent<->controller (manual approval per network security policy) plus, on the controller, a dedicated DB connection for agent event history.

- Set up Controller: Network → Enterprise → Configure → **Configure EAM** → Controller → Default Database + Archive Path (can be a mounted share — monitor free space externally) → Finish.
- Set up Agent: same wizard → Agent → select existing Gateway Network connection to controller → Finish. New agents land **pending** until approved (Network → Enterprise → Agents → row menu → Approve); version/license fields empty until approved. Delete removes from list (reappears pending if machine still live); full removal requires uninstalling the agent role from the agent's own Agent Settings page.
- **Agent Groups** organize agents and can be targeted by Gateway Tasks; new agents added to a group auto-join its scheduled tasks.
- **Unattended installs**: `init.properties` (Gateway Network identity: SystemName, AutoDetectLocal/LocalInterface, UseSSL, numbered `gateway.network.#.*` settings) + `eam-install.properties` (`setup.installSelection=Agent|Controller`, `agent.controllerServerName`, `agent.sendStatsInterval`, `controller.archivePath`, `controller.archiveLocation`, `controller.lowDiskThresholdMB`, `controller.dataSource`) dropped into `/data` before first startup; each renamed to `.bak` once consumed. Docker env vars take precedence when using the official image.

### Tasks

Activate/Update/Unactivate License, Collect Backup, Install Modules, Remote Agent Upgrade, Restart Agent, Restore Backup, Send Project, Send Project Resources, Send Tags.

- Scheduling: Execute Immediately, On Demand, Once Scheduled, Once Delayed, On Schedule (cron).
- **Retry** re-runs a failed task; a failed Remote Upgrade transfer **resumes from interruption point**.
- **Run Now** fires outside cadence without disturbing it (immediate/running tasks don't show it; one-shot scheduled/delayed tasks reschedule to now and won't refire on original schedule; recurring unaffected).
- **Pause/Resume**: running/waiting tasks — outstanding remote calls cancelled on pause, reissued on resume; once-scheduled — come off schedule, go back at original time (or fire immediately if passed); recurring — skip missed iterations, resume normal cadence, no catch-up.
- **Cancel** (one-shot only, before start, or a running task with no completeness guarantee) **permanently deletes** the task, unrecoverable.
- Results in controller DB `agent_events` (`event_category='task'`), one row per agent per execution, `event_level` NORMAL/ERROR: `select * from agent_events where event_category = 'task' order by event_time desc;`

**Backup/Restore**: Collect Backup takes a Gateway backup + archives installed modules; required before Agent Recovery works. Default timeout 60min generate + 60min transfer (tunable via `ignition.eam.task.collectBackup.transferTimeout`). Restore Backup restores a `.gwbk` (uploaded or from archive); agent keeps its previous name. **Pre-8.1 backups cannot restore directly onto an 8.3 Gateway** — restore onto 8.1 first, then upgrade. Install Modules installs from fresh upload or a prior Collect Backup archive. Restart Agent restarts the Ignition service.

**Licensing**: activation always proxied **from the controller** — agents never talk to licensing servers directly. License Management page (Network → Enterprise → License Keys) preloads keys, shows per-license details refreshed on approved-agent report, bulk-assigns via Activate License task; Leased Keys tab manages leased activations with controller-proxied renewal. Deleting a license requires unactivating from any assigned agent first.

**Send Project** replaces the target project outright; supports **cross-major-version** (8.1 controller → 8.3 agent) and agent-to-agent sends. Optional Inherited Resources flattening. **Gateway and Perspective Event Scripts cannot be sent from an 8.3 controller down to an 8.1 agent.**

**Send Project Resources** sends selected resources (templates, windows, transaction groups, pipelines, script modules) into an existing/new project, or Global Resources (Shared Scripts, Alarm Pipelines) into the agent's Global project. Mixing Edge and Standard agents in one task fails silently (no delivery) — target one edition per task.

**Send Tags** distributes tags from a controller-side Tag Provider to agents (or agent-to-agent via a Remote Tag Provider on the controller pointed at the source agent). Enforces **Service Security** tag-editing permissions, not the local provider's. Same Tag Collision Policy as ordinary import (default Overwrite; MergeOverwrite won't overwrite values under an existing UDT instance). Uniquely triggered **from the Designer** (Tag Browser → right-click → EAM → Send Tags to Agents), not Gateway Agent Tasks UI, though it appears in Agent Tasks history. One-shot runs stay visible under Available even after failure (for retry) even without Save Task on Controller checked; checking it persists as a saved task.

### Disaster recovery: Agent Recovery

Agents report health metrics; problems generate Agent Events recorded to controller DB, optionally wired into Alarm Pipelines via **Event Threshold Settings** (Activity/Metric/Task alarm thresholds; Inactivity Warning/Error minutes; CPU/Memory/Errors-per-min/hr/Connected Clients/Perspective Sessions/DB Utilization Warning+Error levels; Active/Ack pipeline routing `project:ProjectName:/pipeline:PipelinePath`).

**Recovery procedure**: fresh Ignition install on the crashed machine (EAM module included by default in Typical install) → EAM wizard → Agent → **Agent Recovery** → select controller/agent → Set Up Agent. Wizard checks agent status, retrieves license file, downloads previously-installed modules, copies most recent Gateway backup → **Apply Files** completes it (Gateway restarts). **Entirely dependent on a prior Collect Backup task** — set up a recurring Collect Backup task for every agent as a matter of course.

### EAM in the Designer

- **Agent System Tags** auto-created under System → Gateway → EAM → Agents in a controller-hosted Designer.
- **Property Binding Functions** (controller-hosted only): Agent Status (platform version, connection status, last-message time), Agent History (raw `agent_events` rows).
- **`system.eam.*`**: `getGroups()` (agent group names), `queryAgentHistory()` (Dataset from agent_events), `queryAgentStatus()` (per-agent status Dataset), `runTask(name)` (execute a pre-configured controller task by name).

### Redundant EAM configuration

No config changes possible on a backup controller (new agents can still be added). Agent metrics only flow to the **active** controller — System Tags won't populate on backup until active. Running/scheduled tasks **suspend automatically** on failover, resume once master regains control. Redundant agents need separate Gateway Network connections to both master and backup (approve master first, then force sync or manually approve on backup). Redundant agents report separate master/backup System Tag folders. Non-config-changing tasks (License) can run against both nodes of a redundant agent pair; config-changing tasks (Send Project) **fail on the backup node** by design.

---

## Gotchas and 8.3 notes

**Explicitly called out as new/changed on the live 8.3 docs** (most pages don't diff against 8.1 explicitly — treat anything not listed here as stable):

- **EAM agent stats interval default changed** — "In version 8.3.2, the default value for the Send Stats Interval was updated from 30 seconds to 45 seconds."
- **Gateway Network cross-version serialization flag** — `gateway.network.allowJavaSerialization=true` exists specifically so 8.1 Gateways keep talking to 8.3 Gateways; documented as a temporary migration bridge, not a long-term setting.
- **EAM Remote Upgrade 8.1→8.3 ordering** — upgrade the controller to 8.3 first; install Historian modules on the 8.1 agent *before* upgrading it to 8.3.
- **8.3 cannot restore pre-8.1 Gateway backups directly** — restore onto 8.1 first, then upgrade that Gateway to 8.3.
- **Send Project/Send Project Resources explicitly support cross-major-version transfer** as a first-class capability — but **Gateway and Perspective Event Scripts cannot be sent from an 8.3 controller down to an 8.1 agent**, a concrete incompatibility to plan around during staged fleet upgrades.
- **SFC Enclosing Step return values** can now map directly onto **Chart Scoped Variables** using the same syntax as passed parameters — check this against older automation examples.
- **SFC redundancy**: `system.sfc.redundantCheckpoint` + the `On Redundant Failover` event's `restartAction` dict (`cancel`/`goto`) is the current full mechanism for controlling how a chart resumes on a failed-over backup node — older guidance describing automatic full-resume is incomplete.
- **Report Table "Column Count" renamed to "Table Repeat Count"** on the Table component — same behavior, new label; relevant when cross-referencing older community examples/screenshots.
- **SFC Element Properties gained a dedicated Notes tab** for Transition, Parallel, Action, Assertion, and Enclosing elements.
- **EAM Setup Wizard entry point** is Network → Enterprise → Configure → Configure EAM (single wizard branches into Controller vs Agent setup, including Agent Recovery) — current 8.3 location if older material names a different entry point.

**Recurring practical gotchas (not new to 8.3, but easy to trip on):**

- Report Save File/FTP paths, and SECS/GEM `wrapper.log` locations, resolve against the **Gateway's own OS** — a Windows-style path silently fails on a Linux Gateway and vice versa.
- Report image paths and Script Data Source logic run **on the Gateway**, not the Designer/Client machine — a local-desktop image path only resolves for you, in Designer preview.
- **Table (Structured) vs Simple Table** export to XLS differently: Table's content becomes an editable overlay; Simple Table's dynamic grid places data directly into cells — use Simple Table when the deliverable must be a real spreadsheet.
- **CrossTab/Simple Table reserved column names** (`Running`, `Remaining`, `Up`, `total`, `average`, `count`, `countDeep`, `max`, `min`) silently collide with the module's own aggregate keys if reused as literal data-source column names.
- A Transaction Group's **Run-Always Expression Item should never have a Write Target** (per the docs' own caution) — it executes every cycle regardless of trigger, so a target invites unintended writes every cycle.
- SFC **chart-scoped variable names must avoid Python dict method names** (`clear, copy, fromkeys, get, has_key, items, keys, setdefault, update, values`) since chart scope is a Python dict under the hood.
- SECS/GEM **Realtime Tag Provider tags are not persistent** — recreated from scratch every Gateway restart; log to the Messages DB table or use a Message Handler writing to real Tags instead.
- **Redundant EAM agents**: only non-config-changing tasks (license tasks) can target both nodes of a redundant pair — config-changing tasks like Send Project always fail against the backup node by design.
