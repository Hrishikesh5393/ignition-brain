# Ignition 8.3 — Vision module

Source: live docs.inductiveautomation.com/docs/8.3 (Markdown fetch of 84 pages under `ignition-modules/vision/*`, plus `scopes/vision-client`, `launchers-and-workstation/vision-client-launcher`, `ignition-modules/symbol-factory`). Developer-oriented distillation; every claim below traces to page content actually read.

---

## Concepts

### Windows

A Vision project is built from **Windows**. Every window has exactly one **Root Container** — a non-deletable, non-resizable `Container` that always fills the window and is the root of the component tree. Windows have a **Name** (used for paths, must be unique per folder) and a separate **Title** property (shown in titlebars and the Windows menu; defaults to the window-type name like "Main Window").

There is only one underlying window object type; **window type is entirely determined by property settings**, not by how it was created:

- **Main window** — `Start Maximized = true`, Border/Titlebar policy "When Not Maximized" or "Never". Takes all available space minus docked windows. Only one should be open at a time.
- **Popup window** — `Dock Position = Floating`, not maximized. Floats over the main window; give it a `Layer` > 0 so it doesn't get buried, and optionally a fixed `Location` (uncheck "Open and Center" to honor it). Can be [parameterized](#templates) and opened as **additional instances** (`system.vision.openWindowInstance`) to show several at once (e.g. 4 tank popups).
- **Docked window** — `Dock Position` set to anything but Floating; locks to a Client edge and fills that edge. `Dock Index` orders multiple windows docked to the same side (lowest = closest to edge). Project-wide **Axis Precedence** (N/S vs E/W) decides which pair of docked windows reaches the corners. **Prevent Popup/Docking Overlap** and **Infinite Desktop** are also project-wide (Vision > User Interface).

**Window lifecycle / cache policy**: Ignition caches windows once opened.
- `visionWindowOpened` / `visionWindowClosed` — fire **every time** the window opens/closes, before bindings evaluate.
- `internalFrameOpened` — fires only the **first time** a window is opened (i.e., when it's actually instantiated); subsequent opens of a cached window do **not** re-fire it. Use `internalFrameActivated` (fires on every show/focus) if you need "every open" behavior via the InternalFrame handlers instead.
- `internalFrameClosed` fires each close; `internalFrameClosing` fires just before close; `internalFrameDeactivated` on focus loss.

**Navigation operations** — every window change is either:
- **Opening** (`system.vision.openWindow` / `closeWindow`) — opens at Designer size unless maximized/non-floating; used for popups.
- **Swapping** (`system.vision.swapWindow`, `system.vision.swapTo`) — closes the current main window and opens another in its place; `swapTo` assumes both windows are maximized. Used for main-window navigation.

**Common navigation mistakes** (explicitly documented antipatterns):
- Using `openWindow()` instead of `swapTo()` between main windows leaves stale windows open behind the visible one — check the Windows menu for a longer-than-expected list.
- Calling `swapTo()` on a **docked** window forces it into a maximized "swapped in" state, breaking the dock; the only fix is logging out/restarting the client.

**Multi-desktop / multi-monitor clients**: A single Client can spawn additional **Desktops** via `system.vision.openDesktop(windows=[...], title=name, handle=name)`. Desktops share a session ID and Client Tag values with the launching Client but are independent for window state and non-Tag property values. Only the **primary desktop** shows a menu bar and gets the project-title titlebar; secondary desktops show their handle/index (or a custom title). A script on one desktop can drive another via `system.vision.desktop(handle).swapTo(...)` / `.openWindow(...)`. Project-update banners (Notify mode) only appear on the primary desktop, and updating it pushes to all local desktops. `system.vision.getScreens()` returns a dataset of `(screenIndex, width, height)` for iterating monitors on startup — the documented pattern skips index 0 (already showing the primary window) and opens one new desktop per remaining screen:

```python
screensDataset = system.vision.getScreens()
screenIndex = screensDataset[0][0]
system.vision.swapTo('Main Windows/Overview', {'Display': 'This is Monitor %d' % (screenIndex + 1)})
for screenDetails in screensDataset[1:]:
    screenIndex, screenWidth, screenHeight = screenDetails
    handleName = "Monitor %d" % (screenIndex + 1)
    system.vision.openDesktop(screen=screenIndex, handle=handleName, width=screenWidth, height=screenHeight)
    system.vision.desktop(handleName).swapTo('Main Windows/Overview', {'Display': "This is Monitor %d" % (screenIndex + 1)})
```

### Window right-click menu (Project Browser)

| Function | Notes |
|---|---|
| Open Window / Close & Commit / Close & Revert | Commit saves in-Designer edits; Revert discards them back to last save/load |
| **Open on Startup** | Marks a window (right-arrow icon) to auto-open on Client login; multiple windows can be flagged, but only **one main window** should be, since opening several stacks them hidden behind each other |
| About Window | One window can be flagged as the About window (info-bubble icon); shown via Help > About This Application in the Client |
| Documentation | Free-text notes attached to the window (document icon marker) |
| Scripting / Security | Jump to Component Scripting / Security Settings for the window object |
| Rename / Duplicate / Cut / Copy / Copy Path / Paste / Delete / Revert Changes | Standard resource operations |
| Export / Send to Project | Exports as a project-resource file, or pushes directly to another project on the same Gateway (folder-level or single-window); **overwrites** a same-named resource in the target with no additional warning beyond the confirmation dialog |
| Protect | Locks the resource from further edits except by users with unprotect permission |
| Find/Replace selected Windows | Scoped search-and-replace across just the selected window(s) |

### Navigation strategies

All strategies reduce to combinations of **Opening** (popups) and **Swapping** (main windows); the choice of strategy is really a choice of *docked-window navigation UI*:

- **Tab Strip** — best for a handful of windows, all visible on one screen at once. Two modes: **Swap Windows** (tab click → `system.vision.swapTo()` automatically) or **Disabled** (roll your own via `propertyChange` on `selectedTab`). The `[System]/Client/User/CurrentWindow` tag reflects the current maximized window name under this pattern, and the Public Demo project uses it.
- **Two Tier** — a first-tier Tab Strip that does *no* window swapping itself (`Navigation Mode = Disabled`), used only to conditionally show/hide a second-tier Tab Strip via an Expression binding on `Visible`, e.g. `{Root Container.First Tier Tabs.selectedTab} = "Reports"`. The second tier does the actual swapping.
- **Tree View** — a docked Tree View with an `Items` dataset (columns include `windowPath` and `path` for tree grouping); **edit that dataset directly via the Dataset Editor, never the Tree View Customizer**, or it overwrites the item data. Typical double-click handler:
  ```python
  if event.clickCount == 2:
      row = event.source.selectedItem
      if row != -1:
          windowPath = event.source.data.getValueAt(row, "windowPath")
          system.vision.swapTo(windowPath)
  ```
- **Back/Forward Buttons** — no docked nav at all; one big main window with two buttons calling the Navigation Script Builder's Forward/Back action, which relies on `swapTo()`'s internal history tracking. Best for small, linear, ordered-step processes.
- **Drill Down** — a background image (e.g. a facility map) with Drawing Tool shapes overlaid per area; `mousePressed` on each shape opens/swaps to that area's detail window; a return button swaps back.
- **Menubar** — navigation entries added under Client Menubar Scripts (Add Sibling/Add Child in the Menu Structure tree), each leaf running a script like `system.vision.swapTo("Overview")`. Maximizes usable screen space since no docked window is consumed.
- **Retargeting** — navigation *between projects/Gateways*, not windows; see [Client configuration](#client-configuration) below.

### Client session model, Client Tags, and startup/shutdown

Each Vision Client is a full session against a Gateway/project. **Vision Client Tags** are per-Client-runtime variables (created in the Designer, but each running Client gets its own independent value set) — good for cross-window indirection (e.g., "current work area") without different Clients fighting over one value. They support most standard tag types/datasets, have **no Tag Group** (update only on poll or on an internal expression's own trigger), and remain writable even when the Client is in Read-Only mode. Expression Type options: **None** (behaves like a Memory tag), **Expression**, **Query** (SQL), **Named Queries**. Client Tags are Vision-only — Perspective's analogue is [Session Properties].

Client Tags can be **overridden at launch** via the Vision Client Launcher's Client Tag Overrides (globally in Settings, or per-application in Manage), or via deep-link query args; folder-nested tags use `/` and spaces are escaped with `+`. **System Client Tags** (memory, performance, IP, hostname, username, etc.) are read-only status tags, one set per running Client.

**Client Event Scripts** (run in the Client's own JVM, not the Gateway; **not** triggered in Designer Preview — test in an actual Client):
- **Startup** — fires on login, before any windows open. Ideal for [dynamic startup-window selection by role](#dynamic-startup-windows) via `system.nav`-flavored logic (now under `system.vision`).
- **Shutdown** — fires on logout, trial expiry, project deletion while running, Gateway-console termination, or closing the Client.
- **Shutdown-Intercept** — *"a legacy script migrated from Ignition 8.1."* Fires only when the user tries to close the Client from the Client itself (not on logout). Set `event.cancel = 1` to block the close, e.g. gated on role membership.
- **Keystroke** — Modifiers + Action (Pressed/Released/Typed) + Key define a global shortcut.
- **Timer** — one running instance **per open Client**; DB/Tag writes belong in Gateway Timer scripts instead to avoid duplication.
- **Tag Change** — per-Client instance; unlike Gateway Tag Change scripts, these *can* monitor Client Tags.
- **Menubar** — builds the Client's Command menu (tree of items with Name/Icon/Tooltip/Accelerator/Mnemonic Character/Action Script); Windows and Help menus are separate, project-property controlled.
- **Message** (Client Message Handlers) — Shared / Dedicated / EDT threading, same mechanism as Gateway Event Scripts but Client-scoped.

<a id="dynamic-startup-windows"></a>Example pattern for role-based startup windows (remove "Open on Startup" from the windows themselves and decide in the Startup script):

```python
roles = system.security.getRoles()
if 'Administrator' in roles:
    system.vision.openWindow('Administrator Screen')
elif 'Operator' in roles:
    system.vision.openWindow('Operator Screen')
else:
    system.vision.openWindow('Welcome Screen')
```

### Templates and template parameters

A **master template** is edited once; every **instance** dropped on a window inherits future master edits automatically. Templates have **no Root Container** — the template itself acts as the container, and its background is transparent by default.

Two kinds of custom properties on a template:
- **Template Parameters** — exposed on every instance for outside binding; **not bindable inside the master design** (this guarantees each parameter carries a single binding, set per-instance).
- **Internal Properties** — bindable *inside* the master design, never exposed on instances; used for the template's internal plumbing.

**Indirection into UDTs** — two approaches:
1. **Standard indirection**: pass a scalar parameter (e.g. `tankNumber: Integer`) and use it inside [Indirect Tag bindings](#tag-binding-types) (`[default]Ramp/Ramp{1}`).
2. **UDT parameter**: make the template parameter itself a UDT type; this creates a complex property whose sub-properties map 1:1 to the UDT's members, bindable with plain Property bindings inside the template.
   - **Caveat**: Template Canvas and Template Repeater **cannot** pass UDT-typed parameters into embedded templates — use standard (numeric) indirection with those two components instead.

**Template Path** on an instance can be dynamically bound to any string (e.g., swap between `Tanks/Tank A` and `Tanks/Tank B`).

**Drop Target**: mark one template parameter as the drop target so dragging a matching-type Tag (including UDT instances) onto a window auto-creates a bound template instance; nested menus appear when multiple templates share a drop-target type.

**Resizing**: instances default to master size; **Enable Layout** (set on the template definition) makes instance content respect each component's individual Layout Constraints on resize — otherwise the whole template stretches uniformly like a Component Group, ignoring per-component layout.

**Accessing an instance's inner components from script** — a Template Instance is a two-layer container; `.getComponent(0)` drills from the Outer Layer (parameters + standard properties) into the Inner Layer (the actual components):

```python
myTemplate = event.source.parent.getComponent('MyTemplate')
print myTemplate.getComponent(0).getComponent('Label').text
```

**Template Canvas** vs **Template Repeater**:
| | Template Canvas | Template Repeater |
|---|---|---|
| Multiple *different* master templates at once | Yes | No (one template path) |
| Placement | Absolute (x/y/w/h/z) or Layout (MiG-style grid, e.g. `'wrap'`) — don't mix both on one canvas | Vertical/Horizontal/Flow (top-to-bottom or left-to-right), auto-scrolls |
| Instance source | `Templates` dataset property (bindable, e.g. via SQL) | **Count** mode (index passed as one parameter) or **Dataset** mode (one row per instance, one column per parameter — required when passing >1 parameter or non-zero-based indices) |
| Reading instance values | `canvas.getAllTemplates()` → list of instance objects, access parameters as attributes | n/a (read the driving dataset) |

---

## Bindings

<a id="tag-binding-types"></a>All binding types are reached from the property's **Binding** icon in the Property Editor.

| Binding | Category | Config summary | Bidirectional? | When to use |
|---|---|---|---|---|
| **Property** | Event-based | Binds one component property straight to another (only properties that fire `propertyChangeEvent` are eligible targets) | Checkbox at bottom of binding window | Visual feedback / mirroring one component off another |
| **Tag** | Event-based (Tag subscription) | Point at a Tag; defaults to `.Value` but can target any Tag attribute (e.g. `.Quality`, `.Tooltip`, `Alarms.HighestActivePriority`) | Checkbox; requires Tag be read/write + user security; **Fallback Delay** (recommend 2× scan class rate) holds the written value until a real Tag update lands or the delay lapses | Standard live display / control |
| **Indirect Tag** | Event-based | Tag path with numbered placeholders `{1}`, `{2}…`, each bound to a component property via the References list | Checkbox, same rules as Tag binding | Dynamic Tag path driven by UI selection (area/unit/motor number) |
| **Tag History** | Polling (dataset only) | See dedicated section below | No | Trend data from the Historian |
| **Expression** | Hybrid — event *and* poll | Ignition's expression language; poll only kicks in if the expression uses a polling function like `now()` | No | Calculated values, string formatting, multi-source logic |
| **Named Query** | Polling | Points at a pre-built Named Query resource; separate SELECT + optional UPDATE query on scalar props; **Retain Rows** toggles whether Designer-fetched rows save with the window | Yes, when an UPDATE query is configured (`{this}` = new value) | Security-hardened SQL access (role/zone restrictions baked into the Named Query) |
| **SQL Query** | Polling | Hand-written SQL; `{Component.Property}` / `{Tag}` substituted as literals (quote strings/dates!); scalar mode returns first row/col, `{this}` in an UPDATE query for writeback; supports stored procs (`CALL`/`EXEC`, DB-specific); **Use Fallback Value** covers zero-row results | Yes (scalar + enabled update query) | Full control queries, JOINs, stored procedures |
| **DB Browse** | Polling | GUI-generated SQL: pick table/columns, mark **Key columns** (→ WHERE), mark sort columns (→ ORDER BY); key columns can be bound to a property for dynamic filtering; scalar mode has an **Enable Database Writeback** checkbox that auto-generates the UPDATE | Yes (writeback checkbox) | Quick-start for simple filtered table reads; can be converted to SQL Query to hand-tune |
| **Cell Update** | Event-based (dataset only) | Targets individual cells of an existing dataset property by **Row Index** or `columnName=value`, plus a **Column** name and a **Value** (static / Tag / Property / mixed `text{ref}text`) | N/A (it's a targeted write into the dataset) | Injecting live values into Table/Linear Scale/Easy Chart config datasets without a full re-query; powers [Indirect Easy Chart](#easy-chart) |
| **Function** | Polling | Bind a dataset property to a prebuilt function (Alarm Status, Alarm Journal, Audit Log, others per installed modules); function's own params can themselves be Tag/Property-bound | No | Pull Alarm/Audit data into a customizable Table instead of the canned Alarm Status Table |

**Polling options** (SQL Query, DB Browse, Named Query, Tag History, Function): **Off** (runs once on open + whenever a referenced value changes), **Relative Rate** (project Base Polling Rate ± offset), **Absolute Rate** (fixed ms). All three *always* re-fire on window open, and all three *always* re-fire when a `{}`-referenced Tag/property changes, regardless of the polling setting.

**Event-based vs polling cheat sheet** — Tag, Indirect Tag, Property, and Cell Update bindings are event-based; anything that queries a database (Named Query, DB Browse, SQL Query, Tag History) or runs a Function binding is polling; Expression bindings are whichever their contents dictate.

**Copying bindings**: right-click a bound property → **Copy Binding**, then **Paste Binding** on a type-compatible property (same or different component).

### Tag History binding details

Dataset-only. Key settings:
- **Selected Historical Tags** — drag Tag paths in; result has a timestamp column + one column per selected path.
- **Date Range** — Historical (bind Start/End from Date Range or Popup Calendar components) or Realtime (length only, always ends "now"). Caution: Historical ranges are **inclusive of the End Date**, including `now()` — this can produce one extra interpolated-to-0 interval and duplicate boundary rows when stitching adjacent ranges.
- **Sample Size**: **On Change** (raw rows, one row per any tag's change — row count can explode with multiple tags), **Natural** (matches the Tag's logging rate), **Fixed** (N evenly-spaced time slices across the range — recommended when users can pick arbitrarily large ranges, to cap row count; returns N+1 when the range doesn't divide evenly; **Min/Max** aggregation doubles the row count), **Interval** (slice size instead of count; use a divisor of the range or expect interpolation on the remainder).
- **Aggregation Mode** table (scripting name differs from UI label where noted): Time-weighted Average (scripting: *Average*), Min/Max (2 rows/slice), Closest Value (scripting: *Last Value*), Basic Average (scripting: *Simple Average*), Sum, Maximum, Minimum, Duration On/Off, Count On/Off, Count, Percent Good/Bad, Range (returns 0 if static), Standard Deviation, Variance.
- **Return Format**: `wide` (default, one column per Tag) or `tall` (`path, value, quality, timestamp` rows).
- **Advanced**: Ignore Bad Quality, Prevent Interpolation, Avoid Scan Class Validation (skips the check that marks gaps bad-quality when the Gateway was down — faster, but loses that signal), **Bypass Tag History Cache** (per-binding; the Historian cache aligns query start/end to existing subcaches for speed, which can mask the most recent value when the range includes "now" — this checkbox forces a live query).
- **Polling & Row Options**: Off/Relative/Absolute, Polling Rate (Absolute default 5s), **Retain Rows** (persist Designer-fetched rows with the window/template — trades load time for it).
- **Indirect Tag History Binding**: same `{1}` placeholder mechanism as Indirect Tag binding, applied inside the Selected Historical Tags paths.

### Property Editor status indication (binding/style coloring)

The **Name** column of a property in the Property Editor encodes its state at a glance:
- **Blue name** — a [custom property](#).
- **Bold + Link icon** — driven by a property binding.
- **Bold + Color Palette icon** — driven by a Style Customizer.
- **Red bold + Warning icon** — **double-bound**: both a binding and a style are trying to drive the same property simultaneously, which will fight at runtime (see [Performance guidance](#performance-and-design-guidance)).

---

## Historian and charts

The Historian records Tag data via configured history providers; Vision's chart components read that data back plus (for some charts) arbitrary SQL. Four chart families exist for time-based / status data, distinct from the categorical [Comparison Charts](#comparison-charts):

<a id="easy-chart"></a>
### Easy Chart

Purpose-built around the Tag Historian — drag Tags straight from the Tag Browser onto the chart to auto-create pens. Non-Historian data (e.g. Transaction Group tables) is supported too, via **Database Pens**.

**Chart Modes** (Vision Property Editor > Chart Mode):
- **Historical** (default) — adds a built-in Date Range Selector under the chart; density shading shows data volume; **the chart does not poll in this mode** — new values only appear when the selection box moves/resizes.
- **Realtime** — shows the most recent window of data, with Spinner/Dropdown controls for how far back to look; polls at the **Poll Rate** property. Watch for pens that appear to "flat-line then snap" — that's the poll interval outrunning the history-logging interval (e.g. 1000ms poll vs 10000ms logging extrapolates the last value for up to 9s between real updates).
- **Manual** — like Historical but with no built-in UI; Start Date/End Date are driven entirely by your own bindings (e.g. "yesterday" or "previous shift").

**Pen types**:
| Pen type | Data source | Notes |
|---|---|---|
| **Tag Pens** | Tag Historian | Created by dragging Tags on; requires an Aggregation Mode + Tag Path per pen; can span multiple history providers/databases on one chart |
| **Database Pens** | Arbitrary SQL query | Set Datasource, Table Name, Value Column, Time Column, Axis — good for Transaction Group data or any externally-recorded timestamped table |
| **Calculated Pens** | Derived from another pen at runtime (not stored) | See function table below; **cannot** be bound directly in the customizer — use a [Cell Update binding](#) on the calc-pen dataset property instead |

All pens show a white **X** by default (for [ad-hoc charting](#ad-hoc-charting) removal) — disable per-row via the Tag Pens dataset's `User Removable` column if you don't want operators deleting pens.

**Calculated Pen functions**: Constant (fixed value), Upper/Lower Control Limit (±3σ from driving pen's mean), Upper/Lower Warning Limit (±2σ), Average, Moving Average (window size = a multiplier of the chart's date range), Multiply (× a factor), Min, Max, Running Sum, Sum (two driving pens), Difference (two driving pens), Linear Regression. Disabling/removing a Driving Pen also removes its dependent Calculated Pens — to keep the calculation but hide the source line, set the driving pen's **Hidden** property to `true` instead of disabling it.

**Axes** — Numeric (default), Logarithmic, or **Symbol** (maps discrete numeric values to text labels on the axis, e.g. `0,1,2` → `Auto, Off, Hand`, in ascending-order-of-entry). By default axis positioning is automatic (`Auto Axis Positioning`); `Auto Range = false` exposes manual `Lower Bound`/`Upper Bound`. Each pen is assigned to exactly one axis.

**Subplots** — split the plot area into multiple stacked panes sharing one X axis but independent Y axes; each subplot's height is proportional to its **Relative Weight** (default 1 = equal split). Assign a pen to a subplot per-pen in the Edit Pen dialog.

**Pen Names and Groups** — rename any pen (defaults to the Tag name) and assign a **Group Name** to cluster related pens under one legend heading; editable inline by double-clicking the pen/group name directly on the rendered legend, not just via the Edit Pen dialog.

**Pen Renderer** — per-pen line color/style/weight/shape; default style `Line w/ Gaps` shows a visible break during comm loss / missing data.

**Digital Offset** — when 2+ **Digital**-style pens share a subplot, their 0/1 lines overlap visually; per-pen `Digital Offset = true` staggers them so both remain readable.

<a id="ad-hoc-charting"></a>**Ad-hoc charting (Tag Browse Tree)** — pair a **Tag Browse Tree** component (`Include Realtime Tags = false`, `Include Historical Tags = true`, `Selection Mode = Multiple - Discontiguous`) with an Easy Chart; users drag Tags on at runtime to add pens, click the per-pen delete X to remove them. Whatever pen set exists when the Designer last saved is also what a freshly-launched Client shows. A dragged Tag has no way to pick an axis from the tree UI — Ignition auto-matches the Tag's Engineering Units to an existing axis, falling back to the default axis on no match; use the chart's tag-drop **Extension Function** for full control (axis/subplot/color routing) — see the worked HOA-tag-routing example under [Extension Functions](#extension-functions).

**Indirect Easy Chart** — point pens at a dynamically-selected Tag family (e.g. "whichever tank the operator picked") using a **Cell Update binding** on the `Tag Pens` dataset property, targeting the Tag Path cell for each pen with a mixed static+reference value like:
```
[~]Tank/{Root Container.Dropdown.selectedStringValue}/Level
```

### Classic Chart

Renders time-series, XY, or Bar charts from one or more dataset **Custom Properties** (each new dataset added via the Chart Customizer becomes its own subplot). Default dataset expects a first (domain) column plus N pen columns; `Extract Order` and the Dataset Properties renderer type together determine the expected shape. Switching `Chart Type` to **Category Chart** requires also switching the X-axis to a Category Axis and feeding string-based X values (commonly paired with the Bar renderer). Customizer tabs: **Datasets**, **X-Axes/Y-Axes** (six axis types: Number, Date, Category, Logarithmic, Elapsed, Symbol), **Dataset Properties** (axis/subplot assignment per dataset), **Plot Properties** (visual styling, e.g. Line Size).

### Other trending charts

- **Sparkline Chart** — minimal single-pen trend line for [High Performance HMI](#performance-and-design-guidance); `Data` binds to a two-column (date, value) dataset (extra columns ignored, must be date-ascending); red dot marks the latest value; `Desired High`/`Desired Low` (both required together) paint a target-range color band behind the line.
- **Status Chart** — discrete/categorical state-over-time (machine states, HOA). X axis is always time; Y axis is one category per series. `Series Data` in **Wide** format = first column datetime + one numeric column per series (column order = bottom-to-top display order); **Tall** format = exactly 3 columns (`timestamp, name, value`). Discrete-value-to-color mapping lives in the expert-level `Series Properties Data` dataset (editable at runtime), configured via the Status Chart Customizer.

<a id="comparison-charts"></a>
### Comparison charts (categorical, not time-series)

- **Bar Chart** — `Data` property: first column = category names, remaining columns = series values. `Extract Order`: **By Row** (default; each dataset row is a series, each non-first column a category) vs **By Column** (each row is a category, each column a series) — same underlying data, different grouping. **No additional datasets can be added** — aggregate everything into the one `Data` property (SQL binding or scripting); use a Classic Chart with a Bar renderer if you need multiple independent datasets.
- **Radar Chart** ("web"/"spider" chart) — `Data` needs at minimum `Value`, `Min`, `Max` columns, **≥3 rows** (1–2 rows render as a degenerate vertical line, not a polygon). Dragging Tags on auto-creates a Cell Update binding to each Tag's Value/EngLow/EngHigh. The midpoint between Min/Max per row draws a "desired" reference polygon, making off-spec values visually obvious at a glance.
- **Pie Chart** — `Data` needs `Label` + `Value` columns (By Row extract order instead uses one column per wedge, and only reads the first row).
- **Box and Whisker Chart** — `Data`'s first column is a `Key` (domain/series label, case-sensitive), remaining columns are categories (legend labels) whose *raw* values Ignition itself aggregates into box (1st–3rd quartile), median line, and min/max whiskers — you supply raw data, not precomputed statistics.

---

## Scripting in Vision

### Component hierarchy and `event.source`

Windows are trees: one Root Container, nested containers/groups, leaf components. Navigation is strictly **up** (`.parent`) or **down** (`.getComponent("Name")`) — to reach a sibling, go up to the shared parent, then down.

```python
component.parent                    # container above
component.getComponent("Text Field") # named child
```

**Exception**: a Root Container's `.parent` is *not* the window, and a window object has no `.getComponent()`. Get the window first — `system.vision.getParentWindow(event)` from an event object — then `.rootContainer` to reach the tree root, or `.getComponentForPath('Root Container.Group.Label')` to jump straight to a nested component by dotted path string, or `.getRootContainer().getComponent(...)` chained manually.

Starting points by script location:
- **Event Handler**: `event.source` is the firing component; `event.source.parent.getComponent('Text Field')` reaches siblings.
- **Extension Function**: `self` **is** the component (no `event` object exists here).
- **Client Event Script**: no window/component reference at all — call `system.vision.getWindow("Window Name")` (only works if that window is currently open; wrap in try/except `ValueError`) then `.getRootContainer()`.
- **Project Library script**: usually receives `event` or `self` passed in from the caller; if truly detached, fall back to the Client Event Script pattern (`system.vision.getWindow`).
- **Reading another open window's properties** works the same way, but only while that window is open.

Complex property types (Font, Border) are Java AWT objects — import from `java.awt` and assign directly, e.g. `component.font = Font('Dialog', Font.BOLD, 50)`.

### Event Handlers (component scripting)

| Handler group | Events | Key `event.*` fields |
|---|---|---|
| Action | `actionPerformed` | `source` — fires on the component's "action" (button press etc.); prefer this over `mouseClicked` |
| Property | `propertyChange` | `source, newValue, oldValue, propertyName` — always filter by `propertyName`, fires for *any* bindable prop change |
| Mouse | `mouseClicked, mouseEntered, mouseExited, mousePressed, mouseReleased` | `source, button (BUTTON1/2/3), clickCount, x, y, popupTrigger, altDown, controlDown, shiftDown` |
| MouseMotion | `mouseDragged, mouseMoved` | same as Mouse; **does not fire on mobile/touch browser gestures** (used for pan/zoom instead) |
| Key | `keyPressed, keyReleased, keyTyped` | `source, keyCode, keyChar, keyLocation, altDown, controlDown, shiftDown` — uses Java `KeyEvent` constants (`event.VK_A`, etc.) |
| Focus | `focusGained, focusLost` | `source, oppositeComponent` |
| VisionWindow | `visionWindowOpened, visionWindowClosed` | `source` (the window) — fires every open/close, before bindings |
| InternalFrame | `internalFrameActivated, internalFrameClosed, internalFrameClosing, internalFrameDeactivated, internalFrameOpened` | `source` — **`internalFrameOpened` fires only the first time** (caching); use `internalFrameActivated` for "every show" |
| Cell | `cellEdited` (Table only) | `source, oldValue, newValue, row, column` |
| Item | `itemStateChanged` (radio/checkbox/toggle) | `source, stateChange, SELECTED, DESELECTED` |
| Paint | `repaint` (Paintable Canvas only) | `source, graphics (java.awt.Graphics2D), width, height` |

Even disabled components can still fire mouse events — that's why `actionPerformed` is preferred over `mouseClicked` for buttons.

### Extension Functions

Found on certain components' Scripting window; the component "subclasses" itself in Python. First arg is always `self` = the component instance; **no `event` object exists**. Signature/docstring are locked (only the body is editable). Examples seen: `filterUser()` on User Management, `getBackgroundAt()` on Table (per-cell background color), `onPopupTrigger()` on Power Table (build a right-click context menu with `system.vision.createPopupMenu({...})`), and the Easy Chart's tag-drop extension function (customize pen axis/subplot/color when a Tag is dragged onto the chart at runtime).

### Custom Component Methods

Like a Project Library function but written directly on a component; `self` is auto-passed, additional named parameters (with optional defaults) can be declared. **Must use tab indentation** (pre-seeded that way). Called like any method: `event.source.parent.getComponent("Text Field").myCustomMethod()`. Placed on a **template**, a custom method becomes callable from every instance and exports automatically with the template (no separate script-library export step needed).

### Script Builders

Component Scripting windows offer builder tabs that generate the underlying script (viewable/editable in the **Script Editor** tab); only one builder's config is "live" at a time — combine actions manually in Script Editor if you need more than one.

- **Navigation** — Open/Swap (with optional center, close-source, and **Additional Instance** for multiple popup copies), Forward/Back (relies on `swapTo` history tracking), Closing. **Pass Parameters** rows map to Custom Properties on the target's Root Container.
- **Set Tag Value** — literal or property-sourced value → `system.tag.writeBlocking([path], [value])`.
- **SQL Update** — DB-browse-style UPDATE builder → `system.db.runUpdateQuery(...)`.
- **Set Property** — literal or property-sourced value written directly to a target property.
- **Script Editor** advanced settings: **Scoping dropdown** (Standard vs **Legacy** — Legacy exists purely for upgrade compatibility; new scripts should always use Standard), **Invoke Later** (defers the script until after current event processing — needed for focus-manipulation scripts and sometimes `visionWindowOpened`).
- **Action Qualifiers** (available on every builder): **Security** (restrict to selected roles) and **Confirmation** (popup Yes/No gate) — both optional and independently toggled.

### `system.vision.*` scope rules

Vision-specific scripting lives under the **`system.vision`** namespace (see [8.3 gotchas](#gotchas) — this is a consolidated namespace). Representative functions referenced across the pages read: `getParentWindow(event)`, `getWindow(name)`, `getCurrentWindow()`, `getRootContainer()` (via window object), `openWindow`, `openWindowInstance`, `closeWindow`, `swapWindow`, `swapTo`, `centerWindow`, `openDesktop`, `desktop(handle)`, `getScreens`, `getScreenIndex`, `getDesktopHandles`, `getCurrentDesktop`, `closeDesktop`, `retarget`, `updateProject`, `transform`, `invokeLater`, `getRoles`, `getUsername`, `isScreenLocked`, `lockScreen`, `logout`, `switchUser`, `unlockScreen`, `setConnectionMode`, `getConnectionMode`, `isTouchscreenMode`, `setTouchscreenMode`, `showTouchscreenKeyboard`, `showDiagnostics`, `showMessage`, `showConfirm`, `showError`, `showWarning`, `createPopupMenu`, `createPrintJob`, `color`. Focus-related helpers (`requestFocusInWindow()`, `getComponentForPath()`) are called on window/component object references obtained via `getParentWindow`/`getWindow`, not directly on `system.vision`.

---

## Client permissions and security

### Authentication strategy

Set per-project under Vision > Login > Authentication Strategy:
- **Classic** — *"User Source system that works as it did before release 8.1."* Assign a User Source; **Required Client Roles** can gate the whole Client.
- **Identity Provider (IdP)** — assign an IdP resource; Vision's role/zone model is derived by mapping the IdP's `Authenticated/Roles...` and `SecurityZones/...` security levels — this requires [user attribute mapping](#) configured on the IdP before Vision can use role-based access.

### Vision Client Permissions (project-wide capability gating)

Every category is **disabled by default** on a new project. Each has an **Enable?** checkbox and a **Required Client Roles** field supporting a comma-separated list mixing plain role names (any zone) and `roleName@zoneName` (role **and** zone required). Categories: Alarm Management, Datasource Management, Device Management, DNP3 Management, Legacy Database Access (raw queries from the Client — Named Queries unaffected), OPC Server Management, SFC Management, Tag Editing, Tag History (query/modify), Translation Management, User Management. Third-party modules can add categories.

### Component / window security

Right-click → **Security** opens the Security Settings panel. **Inherit Permissions** (default) takes the parent's settings; unchecking it exposes **Exempt Roles** (any one matching role grants access — not all required; refresh the list via right-click if new roles don't appear).

**Restrictions** (combinable) applied when the user lacks an exempt role:
| Restriction | Applies to | Effect |
|---|---|---|
| Access Denied Overlay | Components | Overlay shown over the component |
| Disable | Components | `Enabled = false` on window open — only meaningful for interactive components (disabling a Label does nothing) |
| Disable Events | Components, Root Container | Blocks event scripts from firing |
| Hide | Components, Root Container | `Visible = false` on window open |
| Do Not Open | Window object only | Window refuses to open |

### Security in scripting

Beyond declarative role checks, use `system.vision.getRoles()` / `getUsername()` for arbitrary combinational logic the declarative UI can't express (e.g., requiring *all* of several roles, not just one). `system.vision.setConnectionMode(2)` forces Read-Only mode (commonly set in a Startup Script for kiosk-style Clients — note Client Tag writes are still allowed in Read-Only mode). Security Qualifiers can also be attached to any Script Builder action (see above), not just to windows/components directly.

### Client launch/auth flow

Login screen is configurable (Welcome Message/Image, Login Button Text, Locale Selector visibility policy, Classic-only Username/Password field labels, IdP-only Login Prompt/Message/**Auto-Redirect**). **Auto-Login** (Classic only) stores a username/password so the Client skips the login screen entirely, falling back to the login screen on failure; a button on the login screen also lets the user manually invoke the stored auto-login credentials if they get logged out. **SSO Login** (Classic only) requires an Active Directory default Authentication Profile with SSO enabled. IdP-only **Auth Token** settings: Inactivity Timeout (minutes idle before expiry, default 10, must be > 0) and Time-To-Live (≤ 0 = never expires from age alone).

---

## Layout and design

### Anchored vs Relative layout

Project-wide default is set in Project Properties (Vision > Design > Layout Mode); per-component override via right-click → **Layout**.

- **Relative** (default) — component's size/position is remembered as a *percentage* of its parent's bounds at last save; scales proportionally as the parent resizes. Options: **Maintain Aspect Ratio** (+ Center/Leading/Trailing alignment when the parent's aspect ratio differs), **Scale Font** (scales font with size; on a Group this applies to every member unless overridden per-component — the individual override wins, and **ungrouping resets every member back to default layout including font scaling**).
- **Anchored** — each of the 4 edges is independently pinned to the matching parent edge at a fixed pixel distance. Selecting both edges on an axis stretches the component to maintain both distances; **Center Vertically**/**Center Horizontally** deselect the opposing edge pair and instead hold size while centering.
- **Groups ignore layout entirely** — members act as if in unconstrained Relative layout with no aspect-ratio limits, both at runtime and while resizing in the Designer (unlike Containers, whose layout doesn't preview-resize in the Designer). Converting Group ↔ Container is available from the right-click menu; Ignition remembers each component's prior per-component layout settings across that conversion.

### Coordinate space

Drawing-tool **shapes** (not general components) expose direct `X`, `Y`, `Height`, `Width` properties — these values are always **relative to the shape's immediate parent container's current size**, even at runtime when that container is a completely different size than in the Designer. Binding an Angle/rotation property changes the shape's reported position too (position = top-left corner of the enclosing bounding rect), so combining animated rotation with animated position requires grouping the shape with an invisible, larger enclosing rectangle and binding position on the *group* instead of the shape directly.

### Templates vs windows

Use a **window** for a unique screen; use a **template** for anything repeated with only data differing (motor faceplates, tank displays, input rows). See [Templates](#templates-and-template-parameters) above for the full parameter/indirection model — templates are strictly the right tool once you're copy/pasting + re-binding the same component group more than once, since master-template edits propagate to every instance automatically.

### Symbol Factory

Bundled with Vision or Perspective; ~4,000 industrial SVG symbols, drag-and-drop from **Tools > Symbol Factory** or the toolbar valve icon. In Vision, a dropped symbol becomes a **group of shape components** (fully editable/animatable — ungroup to reach individual paths); in Perspective it stays a styleable icon component instead. **Use the "Enhanced" radio button** when searching — Enhanced symbols include the sub-groupings (e.g. `Group_Impeller`) needed for realistic partial-component animation (rotate just an impeller/fan blade by binding its `Angle` property to a Timer's `Value`). **Tank Cutaway** technique: select a Tank + a Cutaway shape (tank first), apply **Shape > Difference**, then place a Level Indicator behind the cut area (Alignment > Move Back) for a "look inside the tank" effect.

### Touchscreen mode

Enabled project-wide (Vision > General > Touch Screen: **Touch Screen Mode Enabled**, optionally **Active on Startup**, plus a scrollbar-width setting). Each touch-capable Input component has a **Touch Screen Mode** property: **Single-Click**, **Double-Click**, or **None**. Keyboard width/font-size are configurable in Vision > User Interface, or overridden locally via the `-Dignition.touchscreen.keyboardWidth` / `-Dignition.touchscreen.keyboardFontSize` JVM args. Scripted invocation pattern:

```python
if system.vision.isTouchscreenMode():
    currentText = event.source.text
    newText = system.vision.showTouchscreenKeyboard(currentText)
```

Designer has a **View > Emulate Touchscreen** mode to test without launching a real Client.

### Creating and manipulating components

Four ways to add components to a window: (1) select in the palette then click-drag on the window to draw its bounds, (2) drag the palette icon directly onto a container at default size, (3) **drag a Tag** onto a container — Ignition prompts for Display/Control/Template component types appropriate to the Tag's data type and **auto-wires multiple property bindings at once** (e.g. dropping a Float Tag as a Numeric Text Field binds `doubleValue`↔Tag `Value` bidirectionally, plus `minimum`/`maximum`→`EngLow`/`EngHigh`, `decimalFormat`→`FormatString`, `toolTipText`→`Tooltip` — editing the Tag's `FormatString` metadata later then automatically updates every place that Tag was dropped this way), or (4) draw shapes/SVGs with the drawing tools.

**Selection**: direct mouse click (Alt+click steps down through z-order for obscured components); window-selection drag (left-to-right = fully-contained components only, right-to-left = anything touched); Alt+drag = touch-selection (a line selects anything it crosses); Project Browser tree selection (the only way to select invisible components, or the window itself, which sits behind its Root Container).

**Manipulation**: 8 resize handles (Ctrl = maintain aspect ratio, Shift = resize from center, combinable); arrow keys nudge by the project's Nudge Distance, Shift+arrows resize the right/bottom edge, Ctrl+Shift+arrows resize the top/left edge, Alt = use the Alt-Nudge Distance instead; Alt+drag moves the current selection regardless of mouse position (needed to move a Container, since a plain drag inside one draws a selection rectangle); Ctrl+drag or Ctrl-D duplicates; shapes only can be rotated (click once to select, click again — not double-click — to reveal rotation handles; Ctrl snaps to 15°; the red crosshair is the rotation anchor and can be dragged off-center).

**Grouping** — visually/behaviorally equivalent to cutting components into a perfectly-sized Container and switching it to group mode, *except* an all-shapes group also gains rotation and other shape-like properties. Inside a group, individual Layout settings are **ignored** — everything acts as unconstrained Relative layout; converting Group→Container restores individual per-component Layout settings (Ignition remembers what they were pre-group).

### Component data types

| Category | Type | Notes |
|---|---|---|
| Numeric | Boolean | 0/1 in Python; 0 = false, anything else = true |
| Numeric | Short / Integer / Long | 16-bit / 32-bit / 64-bit signed |
| Numeric | Float / Double | 32-bit / 64-bit IEEE 754 |
| Non-numeric | String | UTF-16 internally |
| Non-numeric | Color | RGBA; animatable via bindings/Styles |
| Non-numeric | Date | ms since epoch (1970-01-01 UTC) |
| Non-numeric | Dataset | 2D table, typed columns |
| Non-numeric | Font | typeface name + size + style |
| Non-numeric | Border | Java `Border` object — dynamic via Style Customizer, the `toBorder()` expression function on an Expression binding, or scripting a `javax.swing.border.Border` directly (never bind it as if it were a plain string/enum) |

Every component also carries a **Common** property group: `Name` (identifies the component in scripts/bindings — bindable but *strongly* advised against binding, since it will break dependent scripts/bindings), `Enabled`, `Visible`, `Border`, `Mouseover Text` (HTML allowed), `Cursor` (0–13 enumerated pointer styles).

**Dataset Editor** icons (appear next to the Data property's binding icon): Add Row, Delete Selected Rows, Add Column, Delete Selected Column, Delete All Rows, Copy-to-Clipboard, Paste-from-Clipboard. Note: manual edits here are **overwritten on the next binding poll**, so the Dataset Editor is only useful for statically-configured datasets, or to seed the shape of a dataset a Cell Update binding will subsequently target.

### Drawing tools and shapes

The right-side drawing toolbar: **Selection** (default active tool), **Rectangle** (Ctrl = square, Shift = grow from center; small circle handles round corners, Ctrl drags them independently for asymmetric rounding; **Make Straight** reverts to sharp corners; resizing a *rotated* rectangle must use its own handles, not the generic Selection tool, or it skews into a parallelogram and silently converts to a path), **Circle** (Ctrl = perfect circle, Shift = grow from center), **Polygon** (configurable corner count; check **Star** for a star shape, Ctrl snaps rotation to 15°), **Arrow** (single/double-headed), **Pencil** (freehand; simplification setting in px reduces point density, optional Bézier smoothing; closing back on the origin square = closed path), **Line** (click-per-vertex, not drag; straight / perpendicular-only / curved segment modes; double-click, Enter, or clicking the origin box ends the path; Ctrl snaps to 15°), **Path** (directly edit existing path nodes — add/remove/toggle straight-vs-curved), **Gradient** (drag handles to re-orient/resize a Linear or Radial Fill/Stroke Paint directly on the shape), **Eyedropper** (left-click = set fill/background from elsewhere in the window, right-click = set stroke/foreground; remember to switch back to Selection afterward or every click keeps recoloring).

Shapes uniquely expose `X`, `Y`, `Height`, `Width`, and `Angle` as first-class bindable properties (see [coordinate space](#coordinate-space) above for the relative-to-parent caveat, and the rotate+move-together workaround involving an invisible enclosing rectangle).

**Fill and Stroke**: every shape has `Fill Paint` (interior), `Stroke Paint` (outline color), `Stroke Style` (thickness/dash/corner behavior). Five paint types: **No Paint** (transparent fill, or no outline drawn), **Solid Color**, **Linear Gradient** (stops along a straight line, default horizontal across the shape width), **Radial Gradient** (stops radiate from a center point), **Pattern** (repeating two-color pixel pattern, pick a preset or build custom). Gradient **cycle modes**: No Cycle (edge stops repeat forever beyond the gradient bounds), Reflect (mirrors back and forth), Repeat (tiles). Stroke Style sub-settings: thickness (px) and dash pattern; **Cap style** (line-end decoration: none / round / square); **Join style** (corner decoration: miter / round / bevel); **Miter Limit** (caps runaway-long miter points on very sharp angles).

**Shape Geometry / Constructive Area Geometry** (Shape menu, needs 2+ shapes selected — **selection order matters**, the first shape is generally what's retained/operated on): **Union** (merge into one shape — e.g. combining a circle+rectangle+triangle into a pump symbol), **Difference** (punch the 2nd shape out of the 1st — the documented Tank Cutaway technique), **Intersection** (keep only the overlap), **Exclusion**/XOR (keep only the non-overlapping area), **Division** (cuts the 1st shape along the 2nd shape's outline — difference + intersection combined into two resulting pieces). Any shape can be converted to a raw editable path via **To Path**, or implicitly becomes one if stretched in a way the underlying primitive can't represent. A **Bézier curve** is built from 2 endpoints + 2 control points and is created with the Line tool's curve-segment mode.

### Images and SVGs

Dragging an SVG file onto a window imports it as a new grouped-path polygon component (small resulting size is common — just resize up); supported element/attribute/property coverage follows the embedded Apache Batik library, not the full SVG spec. Two documented **coloring techniques**:
- **Coloring SVG parts** — ungroup down to the individual path, set its `Fill Paint` (optionally bound via Expression + `color()`, or a Tag/Property binding's built-in Number-to-Color Translator), then re-group.
- **SVG tinting** (for symbols too intricate to recolor path-by-path) — duplicate the whole SVG, **Union** the duplicate into one flat shape, remove its outline (`Stroke Paint = No Paint`), bind its `Fill Paint` via a Tag binding's Number-to-Color Translator using semi-transparent colors (e.g. 40% green/red), then layer that tinted duplicate directly on top of the original (Alignment > Move to Front) and group the pair — the semi-transparent flat shape acts as a color overlay ("tint") without having to individually recolor dozens of paths.

Standalone images come from the Gateway-hosted **Image Management Tool** (folder-search icon next to `Image Path`) or a local filesystem path prefixed `file:///` — local-path images only render correctly if that exact path is reachable from wherever the Client is actually running, so a shared network drive is recommended over a Designer-machine-local path.

### HTML in Vision

Prefixing a text property with `<html>` (closing `</html>` optional; tags case-insensitive) enables inline formatting on **display**-oriented text properties (Label, Button, Table, Mouseover Text) — but not on input properties like a Text Field's `Text`, since a user might type into it. Supported elements: `<html>`, `<b>`, `<u>`, `<s>` (strikethrough), `<br>`, `<ol>`/`<ul>`/`<li>`, `<center>` (immediately after `<html>`), `<font color="...">` (name, hex, or RGB).

### Localization in Vision

Built on the platform Translation system. Once a **2nd language** exists in the project, the Client's Login Screen automatically gains a Language Selector (visibility policy: Automatic [shown once ≥2 languages exist]/Show/Hide, set in Project Properties); a user's saved language preference (from their user profile) auto-applies on login. A single **Language Selector** component placed on any one window (commonly a nav window) can retrigger translation across *every* open window with no binding required, since selections compare directly against the Translation Manager database rather than propagating through the property system.

---

## Client configuration

### Launch properties (Project Properties > Vision > Launching)

- **Gateway Launch Page**: Default Launch Mode (Windowed/Full Screen), Hide From Launcher.
- **Launch Icon**: path to an uploaded Gateway image (PNG/SVG/GIF/JPEG).
- **Windowed Properties**: Vendor/Homepage (shown in JWS-era app manager UI), Width, Height, Screen Index (0-based, OS-dependent support), Start Maximized, Start Centered (ignored if maximized), Hide Exit Button (Full Screen mode only — for kiosk terminals).
- **Client Memory**: Initial and Maximum heap — bump Initial for startup perf, bump Maximum to let a Client actually use more RAM on a beefy host.

### Auto-login

Vision > Login > **Enable Auto-Login** + Username/Password (+ repeat). Typical for a shared low-privilege "guest" account; **File > Save All** to push. A button remains on the login screen for a user to manually re-invoke the stored auto-login credentials if they get logged out mid-session.

### Retargeting

`system.vision.retarget("ProjectName"[, "gateway:port"])` — switches the running Client to a different project, same Gateway or a different one (even cross-WAN). Attempts to transfer current credentials (re-prompts on failure), preserves Vision Client launch properties, and sets `_RETARGET_FROM_PROJECT` / `_RETARGET_FROM_Gateway` in the target project's global namespace even if no explicit `parameters` dict is passed. Typical pattern: a neutral "landing" project routes authorized users out to area-specific projects via retarget buttons whose visibility is itself role-gated.

### Local Client Fallback

Lets a Client fail over to a **Gateway running on its own host** if it loses the central Gateway. Requires **port 6501** open locally. Enable under Platform > System > Gateway Settings on the *local* Gateway: **Enable Local Fallback**, Fallback Project name (must be published locally, ≥1 main window), **Seconds Before Failover** (default 60, manual trigger button also available). Does **not** auto-transfer back — build your own reconnect check (e.g. a 30s Timer script calling `system.util.getGatewayStatus(...)` then `system.vision.retarget(...)`). Pairs with **Fallback Cache Authentication** (a User Source designed to cache remote credentials for offline fallback logins).

### Vision Client Launcher

Installed from Gateway webpage Home > Vision > Download. Per-application settings (Manage → three-dot menu): Application Name, Gateway Address, Description, **Vision Client Project** (required), Fallback Application (used once Retries is exceeded), Image Path, Window Mode (`window`/`fullscreen`), Screen Index, Timeout, **Retries** (`-1` infinite, `0` none, `N` count), Init/Max Heap, JVM Arguments. Separate **Client Tag Overrides** tab. Supports **Redundancy** — the backup Gateway address is cached automatically on first successful connect and used if the primary is unreachable, alternating until one responds.

**Command line** launch (`visionclientlauncher.exe`/`.sh`): `application=<name>` (Launcher app name, not project name; spaces → `%20`), `window.mode`, `screen`, `fallback.application`, `timeout`, `retries`, `init.heap`, `max.heap`, `-Djavaws.launchparams="Tag1;Tag2"` + `-Djavaws.launchparam.Tag1=value` pairs to override Client Tags at launch, `config.json=<path>` to run from an exported launcher-config JSON as a temporary override set.

### Vision Project Properties reference (remaining settings)

Beyond Launch/Login/Permissions/Update Mode/Touch Screen (covered above), Project Properties > Vision includes:

- **Design**: `Commit on Close` (Prompt vs Always commit window/template edits on close), `Template Auto Commit` (On/Off when switching windows/templates), `Constrain to Parent Container Bounds` (disable to position components outside their parent, useful for advanced layouts), `Nudge Distance` / `Alt-Nudge Distance` (px per arrow-key / Alt+arrow-key move-or-resize), `Layout Mode` (project default for newly-created components: Relative or Anchored) + its Relative/Anchored Layout Options, `Default Color Mapping` (seed values for new Number-to-Color bindings).
- **General**: `Timezone Behavior` (Client emulates the Gateway Timezone by default — so all Clients behave identically regardless of host OS timezone — or can use the Client's own host timezone, or an explicit override), `Update Mode` (see below), `Disable Tag History Data Cache`, `Resource Encoding` (Auto/Binary/XML for windows/templates/**Client Tags**, anterograde — only affects future saves).
- **Timing**: `Polling Base Rate` (ms, the project-wide base all Relative-rate bindings key off of), `Connect Timeout` / `Read Timeout` (ms, Gateway socket limits), `OPC Browse Timeout` (ms, default 120,000), `Connection Concurrency` (see [Performance guidance](#performance-and-design-guidance)).
- **User Interface**: `Minimum Size` (defaults 800×600 — shrinking the Root Container below this in the Designer shows guide lines; scrollbars appear at runtime once the usable area drops below these bounds), `Client Background Color`, `Menu Font`, `Hide Menu Bar` / `Hide Windows Menu` (client-relaunch-required), Touch Screen Keyboard Width/Font Size (also overridable per-launch via `-Dignition.touchscreen.keyboardWidth`/`keyboardFontSize`), **Docking**: `Axis Precedence` (North/South vs East/West — decides which docked-window pair reaches the corners), `Prevent Popup/Docking Overlap`, `Infinite Desktop` (expand the desktop area instead of clamping dragged floating windows to bounds).

### Client Update Modes (Vision > General > Update Mode)

- **Notify** (default) — orange banner on save; user clicks to download+apply.
- **Push** — applies automatically on Designer save, no user interaction (good for unattended overhead displays).
- **None** — defers until Client restart or an explicit `system.vision.updateProject()` call.

Changing this setting itself only takes effect for Clients launched *after* the change (it's read at launch time).

---

## Designer and Client interface reference

### Vision Designer Interface

The Welcome tab offers one-click creation of Main/Popup/Docked windows and Templates, plus a recently-modified list. The **Component Palette** (tabbed, docks N/S, or collapsible, docks E/W — switch via View > Panels) is the drag source for built-in components. The **Vision Property Editor** shows the union of properties across a multi-selection; Categorized vs Alphabetic sort toggle; hover or the description-area toggle shows each property's type + scripting name; dropdown-valued properties are 0-based enumerations, so a matching on-screen Dropdown can bind straight to `Selected Value`. **Designer Comms** (Project menu) controls Gateway communication during editing: **Comm Read-Only** (default — Gateway data is read-only in the Designer), **Comm Off**, **Comm Read/Write**.

Menubar highlights beyond Edit/Cut/Copy/Paste basics:
| Menu | Notable items |
|---|---|
| Edit | Find/Replace; Select Same Type (in container, or in-window); Group Rename (prefix + auto-increment) |
| View | Emulate Touchscreen; Disable Overlays (suppress red/gray bad-binding overlays for this Designer session only); Grid Size (5 or 10) / Show Grid / Snap to Grid; Show/Snap to Guides; **Spotlights** (highlight bound=green / scripted=blue / invisible=pink components); **Dependencies** (Show Supporters / Show Dependents / Show All — draws binding-relationship arrows) |
| Project | Designer Comms; Properties; Event Scripts shortcut; Preview Mode; Preview Language |
| Component | Group/Ungroup; Convert to Container; Lock; Layout; Size and Position; Customizers; Scripting; Security; Translations |
| Alignment | Move to Front/Back/Forward/Backward (z-order); Align Left/Right/Top/Bottom/Centers; Align as Row/Stack (with optional size-normalizing) |
| Shape | Rotate 90°; Mirror; Union/Difference/Intersection/Exclusion/Division; To Path; Stroke To Path |

### Vision Client Interface (runtime)

Default menubar: **Command** (Logout, Lock Screen, Exit — extendable via Client Menubar Scripts), **Windows** (list of open windows by *title*, not name/path; Close current / Close All), **Help** (Diagnostics; About Ignition Vision). Hide all or part of it via Project Properties > Vision > Client Menu (`Hide Menu Bar`, `Hide Windows Menu`) — takes effect on next Client launch.

**Diagnostics popup** (Help > Diagnostics, or **Ctrl+Shift+F7** if the menu bar is visible, or `system.vision.showDiagnostics()` scripted when it's hidden): Performance, **Console** (script `print`/error output — also reachable from Designer Preview Mode via Tools > Console), **Log Viewer**, **Logging Levels** (per-logger level, session-only, resets on restart — search bar to filter loggers), Thread Viewer, Connections, Scripts tabs. Vision Client log files are **only** obtainable from this runtime popup — there is no Gateway web-interface path to a specific Client's own log file.

---

## Performance and design guidance

- **High Performance HMI**: prefer gray-scale base graphics over bright traditional SCADA colors; reserve saturated colors (red/orange/yellow) exclusively for abnormal states so they visually "pop." A documented convention is dark gray for a "scheduled" (intentionally off) state, distinct from "faulted." Don't rely on equipment body color alone for fault state — pair with a dedicated **Alarm Indicator** (shape + color + descriptive text, optionally a dotted line to the offending equipment) so the HMI degrades gracefully for colorblind viewers and monochrome/limited displays, and stays legible if color rendering is lost. Purpose-built components for this style: [Moving Analog Indicator], [Sparkline Chart], [Radar Chart], [Status Chart].
- **Sparkline Chart** shows exactly one pen (extra dataset columns beyond date+value are ignored) — stack multiple instances rather than expecting multi-pen support; cheap way to add glanceable trend context without a full Easy Chart.
- **Connection Concurrency** (Vision > Timing): unlimited by default; enabling a cap trades some Client performance for reduced simultaneous-connection load on congested networks.
- **Disable Tag History Data Cache** (Vision > General > Data): the Client normally caches Historian results for repeat graph/table operations; disabling it forces a full Gateway round-trip every time — only disable if staleness/caching artifacts are a bigger problem than the extra load. The per-binding **Bypass Tag History Cache** flag is the finer-grained version of the same tradeoff.
- **Fixed sample size** on Tag History/Easy Chart bindings is the recommended guard against unbounded row counts when users control arbitrarily wide date ranges.
- **Double-bound properties** (a Style Customizer driving the same property as a direct binding) throw a red warning icon in the Property Editor and will fight at runtime — pick one mechanism per property.
- **Navigation antipatterns** (see [Windows](#windows) above) — `openWindow` instead of `swapTo` between main windows, and `swapTo` on a docked window, are both explicitly called out as common sources of "stuck" window state.
- **Resource Encoding** (Vision > General > Data): Auto/Binary/XML controls how windows/templates/**Client Tags** serialize on save; XML trades file size/binary-diff-friendliness for human readability. This setting is **anterograde** — changing it only affects future saves, not resources already serialized under the old setting.

---

## Common task patterns

**Component animation** — two distinct techniques, chosen by what's being animated:
- **Actually moving/resizing a component** — either bind a part's transform property directly (e.g. bind an Enhanced Symbol Factory sub-group's `Angle` to a Timer's `Value`, with the Timer stepping by N every N ms up to a Bound of 360, for a spinning impeller/fan), or drive it from script with `system.vision.transform(...)`, which can move/resize any component from Python in one call (useful when a change should be triggered by an event/condition rather than continuously ticking).
- **Cycling static images to fake motion** (e.g. a conveyor belt) — duplicate the graphic N times, offset each copy's visual detail slightly (e.g. shift a `Path` sub-element left/right per copy), then bind each copy's `Visible` to `if({SignalGenerator.value} = N, 1, 0)` so exactly one copy shows at a time; drive the index with a **Signal Generator** in Ramp mode (`Values/Period` = number of copies, matching Upper Bound) for a smooth illusion of continuous movement at a controllable rate.

**Dropdown List** `Data` dataset drives three distinct modes based on column count/type, which in turn determine `Selected Value` / `Selected String Value` / `Selected Label`:
- **Number/Label pair** — col 1 integer (hidden `Value`), col 2 string (visible `Label`).
- **Single Label column** — two string columns; first is the hidden value (`Selected String Value`), second the visible label.
- **Code/Label pair** — exactly one string column; that single value serves as both `Selected Label` and `Selected String Value`.
Extra columns beyond the first two are ignored for these three derived properties but can still be shown to the user by setting `Dropdown Display Mode = Table`.

**Reusable input template** — a template with a `display` (label text) and `text` (bidirectional input) String parameter, plus an Expression binding on the Text Field's `Background` that validates non-blank input: `if(len(trim({textBox.Text Field.text}))>0, color(255,255,255), color(255,0,0))` — turns the field red until the operator enters something. Demonstrates the general "validate + visually flag" pattern reusable across any templated input.

**Reading a selected Table/Power Table cell** — `Power Table` (and `Table`) expose `selectedRow` and a `getSelectedRows()` method (for multi-select) alongside the raw `data` dataset; always check for `-1`/empty before indexing:
```python
table = event.source.parent.getComponent('Power Table')
if table.selectedRow != -1:
    mechanicName = table.data.getValueAt(table.selectedRow, "Mechanic_Name")  # or an integer column index
```

**Client Tags for cross-window indirection** — bind a window's Root Container Custom Property to a Client Tag (e.g. `MachineNumberRef`), then use that Custom Property inside Indirect Tag bindings throughout the window's components; a Dropdown/Numeric Text Field bidirectionally bound to the same Client Tag lets the operator retarget every indirect binding on every open window at once, purely by changing one value — and because Client Tags are per-Client, two separate Clients can be looking at two different "machines" simultaneously using the identical window set.

---

<a id="gotchas"></a>
## Gotchas and 8.3 notes

**CHANGED — `system.gui` / `system.nav` fully consolidated into `system.vision`.** Every scripting example across all 84 pages read uses `system.vision.*` exclusively (`system.vision.openWindow`, `.swapTo`, `.getParentWindow`, `.retarget`, `.getRoles`, `.isTouchscreenMode`, etc.) — there is no `system.gui` or `system.nav` call anywhere in the current docs. Corroborating evidence from the URL index: `grep`-ing the full 8.3 docs site URL list for `system-gui` or `system-nav` returns **zero** pages, while `system-vision` returns **85** individual scripting-function reference pages. Notably, the *prose* on the Multi-Monitor Clients page still refers informally to *"Functions for the **gui** and **nav** scripting modules will execute in the Desktop that originated the call"* — immediately followed by code that uses only `system.vision.swapTo` and `system.vision.desktop(1)`. Treat any legacy `system.gui.*`/`system.nav.*` reference in older code, forum posts, or migration notes as needing a mechanical rename to `system.vision.*` under 8.3.

**LEGACY, explicitly labeled in-docs** — the **Shutdown-Intercept** Client Event Script is called out verbatim as *"a legacy script migrated from Ignition 8.1"*; it survives in 8.3 but is presented as a holdover rather than the preferred shutdown-control mechanism.

**LEGACY, explicitly labeled in-docs** — the Script Editor's **Scoping dropdown** offers Standard vs **Legacy** scoping specifically *"to provide backwards compatibility when upgrading"* from versions where event-handler scoping worked differently; docs explicitly say *"All new scripts should ideally leave the scope set to Standard Scoping, as there is no reason for new scripts to use the Legacy Scoping option."*

**Authentication baseline** — the **Classic** authentication strategy is described as the User Source system *"that works as it did before release 8.1,"* i.e. it is the pre-8.1 legacy model kept alive as one of two selectable strategies, with **Identity Provider (IdP)** as the other, newer path requiring its own user-attribute-mapping configuration before Vision's role/zone model can consume it.

**Expanded scope, 8.3-era note** — the **Resource Encoding** project property (Auto/Binary/XML) is documented as *"now also applies to Vision Client Tags"* — implying this setting's scope was recently widened to cover Client Tag serialization in addition to windows/templates.

**Newer per-binding safety valve** — the **Bypass Tag History Cache** checkbox on Vision Tag History bindings exists specifically to counter a known Historian-cache staleness scenario (subcache-aligned start/end dates can mask the truly latest value when a range includes "now"); this is a targeted, per-binding escape hatch rather than the blunt project-wide "Disable Tag History Data Cache" switch.

**Designer UX refinement** — the Vision Property Editor's **Search Bar** ships with a dedicated Search Filter panel (Case Sensitive/Insensitive, Use Wildcards, Use Regular Expression, Match from Start/Exactly/Anywhere, Match Description) for filtering the property list by name or description live as you type — a materially richer property-finding UX than a flat alphabetical/categorized list.

**Vision's role relative to Perspective** — nothing in the Vision docs read states Vision is deprecated, and the module continues to receive incremental refinements (cache-bypass flags, search filtering, expanded resource-encoding scope). However, cross-links consistently steer *session/state*-oriented questions toward Perspective's parallel mechanism rather than duplicating guidance — e.g. the Vision Client Tags page explicitly says *"If you are using Perspective, see the Session Properties page for a similar system,"* and Symbol Factory's animation guidance is split per-module (Vision: ungroup into shape components and animate directly; Perspective: use the styleable Symbols Palette component instead). Read this as: Vision remains a fully supported, actively documented desktop/thick-client HMI module in 8.3, with Perspective positioned as the parallel (and for browser-based/session-state-centric patterns, generally preferred) alternative — but this framing is an inference from cross-reference patterns, not a direct statement found in the Vision docs themselves.

**Cache/caching nuance to remember when debugging "window won't reset" bugs** — because windows are cached, `internalFrameOpened` (fires once, ever, per window instance) is frequently mistaken for an "on every open" hook; use `internalFrameActivated` (or `visionWindowOpened`, which *does* fire every time and runs before bindings) instead.

**Aggregation-mode naming mismatch** — three Tag History aggregation modes have **different names in the UI vs. in scripting**: UI "Time-weighted Average" = scripting `Average`; UI "Closest Value" = scripting `Last Value`; UI "Basic Average" = scripting `Simple Average`. This trips people up when translating a working binding into equivalent `system.tag.*`/`system.historian.*` script calls.

**Template Canvas/Repeater + UDT parameters** — explicitly documented as **unsupported**: UDT-typed template parameters cannot be passed through either container; fall back to scalar indirection (an integer/string parameter feeding an Indirect Tag binding) inside templates destined for a Canvas or Repeater.

---

## Detailed sub-topics

*The sections above are a project-wide synthesis. This section drills into the individual binding-type, navigation-strategy, popup, template, Easy Chart, and common-task sub-pages with their exact field names, dialog layout, and worked-example syntax.*

### Binding types in depth

**Property binding** — only properties that fire a `propertyChangeEvent` can be bind *targets* (this is why the target-property dropdown in a binding window is a subset of all properties). One-way by default; check **Bidirectional** at the bottom of the binding window to make it two-way off a single binding (e.g. bind a Numeric Text Field's `Value (Integer)` to a Slider's `Value` bidirectionally instead of needing two separate bindings). Good for pure visual mirroring — no Tag or DB round-trip involved.

**Tag binding** — defaults to the Tag's `.Value` if you select the Tag node itself in the tree; to bind to a Tag *attribute* instead (e.g. `.Quality`, `.Tooltip`, `Alarms.HighestActivePriority`, `AlarmActiveAckCount`), drag that specific attribute row from the Tag Browser onto the property, or append `.AttributeName` to the path manually — e.g. `[default]Test/Alarm_Active_1.Quality`. Bidirectional requires the Tag to be read/write *and* the user to hold write security on it; **Fallback Delay** (seconds) holds the last-written value on screen while waiting for a real Tag-value echo, falling back to the pre-write value if none arrives in time — rule of thumb, set it to 2× the Tag's scan-class rate, because a PLC or another writer can silently re-assert the old value with no change event.

**Indirect Tag binding** — the **Indirect Tag Path** field takes a path with `{1}`, `{2}`, … placeholders; the **Tag** helper button inserts a full Tag path at the cursor (which you then hand-edit to swap a literal segment for `{n}`), the **Property** helper button inserts a new numbered reference and lets you pick the source property from the References list below. Each row in **References** corresponds to one `{n}` and is bound to a component property elsewhere in the same window (not across windows). Also bidirectional via the same checkbox, same Tag-write-security requirement. Worked pattern: `[TagProvider]MyPlant/{1}/Valves/Valve{2}/FlowRate` with `{1}=Root Container.AreaName`, `{2}=Root Container.ValveNumber`.

**Expression binding** — hybrid event/poll: fires on window open and on any referenced Tag/property change (event-based), *and* re-polls if the expression body uses a polling function like `now()`. Four helper icons next to the editor: **Properties** (insert `{Component.property}` at cursor), **Tags** (insert `{[provider]path}`), **Operators**, **Functions** (also documents each function's expected parameters). No Bidirectional checkbox exists on Expression bindings — they are one-way only, since an expression's inverse isn't generally defined. Nested `if()` vs `switch()` produce identical results for multi-branch logic; `switch()` is more compact for a single driving value tested against several discrete cases.

**Named Query binding** — polling-only. On a **dataset** property you configure a single Named Query: **Path** (browse via the magnifying-glass icon), a **Parameters** table where each declared Named Query parameter gets a Tag or Property reference inserted via the Insert Property / Tag icons, a read-only **Query** preview, a **Polling Mode**, and **Retain Rows** (persists Designer-fetched rows with the window — slows load, like Tag History's same-named option). On a **scalar** property, a *second* Named Query can be configured as the write side; it must itself be authored with **Query Type = Update** in the Named Query's own Authoring tab, and the **This** button inserts `{this}` as a parameter Value to wire in the new value from the bound property.

**SQL Query binding** — polling; hand-written SQL against any Gateway DB connection. `{Component.Property}` / `{Tag}` are substituted as *literal text* before the query reaches the driver, so string/date literals need their own quotes in the SQL (`t_stamp >= '{Root Container.DateRange.startDate}'`) — a syntax error here is a database error, not an Ignition one (debug by pasting the query with literal values into the Query Browser). Scalar mode returns row 0/col 0 only; **Use Fallback Value** supplies a value when the query returns zero rows (datasets never need this — an empty dataset is valid). Scalar mode can add an **Update Query** using the same `{this}` keyword as Named Query bindings to make the binding bidirectional. Stored procedures are supported with DB-specific syntax (`CALL proc_name` on MySQL, `EXEC proc_name` on SQL Server). A DB Browse–built query converts to SQL Query with the generated SQL preserved, for hand-tuning beyond what DB Browse's UI can express; the reverse direction is not offered.

**DB Browse binding** — a GUI query builder that is functionally a SQL Query binding under the hood. Pick a table in the Browse Database tree; select specific columns or leave the table itself selected to mean `SELECT *`. Any column can be flagged a **Key column** (the key/remove-key icons) which places it in the generated `WHERE` clause, or a **sort column** (multiple allowed, in click order) which builds the `ORDER BY`. A key column's value can itself be bound to a component property (bind icon next to the key field) for dynamic run-time filtering — e.g. filter a Table's rows by whatever a Text Field currently contains. Scalar mode gets an **Enable Database Writeback** checkbox that auto-generates the UPDATE statement (no manual `{this}` needed, unlike SQL Query/Named Query).

**Cell Update binding** — only appears as an option when the target property is a **dataset**. The dialog shows the source **Dataset** table on top and a **Cell Bindings** table below; each cell binding needs a **Row** identifier, a **Column** identifier, and a **Value**. Row can be a literal zero-based index, or `columnName=value` (case-sensitive) which re-resolves dynamically — if the matched column's value later changes (even via another cell update), the binding follows it to whichever row(s) newly match, and can match multiple rows at once. Duplicate-cell targeting across rows is not an error; updates apply top-to-bottom and the last one wins. Value can be a static literal, a pure Tag/Property reference (select the cell, don't put text-cursor focus in it, then use the Tag/Property icon), or a mixed string like `Motors/Motor {Root Container.MotorNumber}/Amps` or `[~]Tank/{Root Container.Dropdown.selectedStringValue}/Level` that concatenates a reference into a larger string — the standard mechanism for Indirect Easy Chart pen paths and for pushing individual live Tag values into an otherwise-static Table dataset. Also used to drive individual Linear Scale `Indicators` dataset rows (Value + Color columns) for a runtime-moving setpoint marker.

**Function binding** — binds a dataset property to a pre-built function (Alarm Status, Alarm Journal, Audit Log, plus whatever other installed modules add); the function's own parameters can individually be Tag- or Property-bound. Typical use: pull Alarm Status data into a plain Table via a Function binding instead of the canned Alarm Status Table component, to get full customizer/extension-function/scripting control over the display while keeping the canned data source.

**Color Animation (Style Customizer / Number-to-Color)** — two independent mechanisms for dynamic color, chosen based on the binding type in use:
- *Expression binding with `color()`* — for any color-type property when multiple properties/Tags need to be combined into one decision, e.g. `switch({HOA tag}, 0,1,2, color(255,0,0), color(0,255,0), color(255,255,0), color(0,0,0))`.
- *Number-to-Color Translator* — appears automatically at the bottom of Property/Tag/Indirect-Tag binding windows when the bound value can't itself be a color; maps numeric ranges to specific colors via **Add New Translation**/**Delete Selected Translation**, supports a **Low Fallback Color** for values below the lowest mapped range, and can blink between two colors per range.
- *Style Customizer* — a separate, component-level mechanism (right-click → Customizers → Style Customizer), not a property binding at all. Pick one **Driving Property** (often a custom Integer/state property), move properties from the available list into **Styled Properties**, then define **Styles** as a list of `(Value, {styled-property values})` rows — the style whose Value is the highest one ≤ the driving property's current value is applied. Each style can be **Animate**d into multiple steps, each with its own **Step Duration (ms)**, to build a flash/alternate effect (e.g. red↔yellow flashing above a high-high setpoint). A property simultaneously bound *and* styled shows a red warning icon in the Property Editor — pick one mechanism per property, never both.

### Navigation strategies

**Tab Strip** — best for a handful of windows visible at once, typically docked. **Navigation Mode** on the Tab Strip: **Swap Windows** (each tab click auto-calls `system.vision.swapTo()` with that tab's configured window) or **Disabled** (tabs do nothing automatically; roll your own logic off the `propertyChange` event on `selectedTab`). Configured via right-click → Customizers → Tab Strip Customizer: **Add Tab** creates a new tab (or duplicates the currently-selected one), each tab needs a **Window Name** (full path, e.g. `Main Windows/Main Window 2`, not just the bare name) and a **Display Name**; Move Up/Move Down/Remove Tab reorder or delete; per-tab Background/Foreground colors control selected vs. unselected appearance.

**Two Tier** — a first-tier Tab Strip with **Navigation Mode = Disabled** (it does no swapping itself) whose `selectedTab` drives the **Visible** property of one or more second-tier Tab Strips via an Expression binding, e.g. `{Root Container.First Tier Tabs.selectedTab} = "Reports"`. Each second-tier Tab Strip *does* have Navigation Mode = Swap Windows and holds only the tabs belonging to that first-tier category. Built by duplicating an existing second-tier Tab Strip for each new top-level category rather than building one from scratch. Good for medium-sized, cleanly-grouped window sets.

**Tree View** — a docked Tree View bound to an **Items** dataset with (at minimum) `windowPath` and `path` columns; `path` determines the tree's folder grouping, `windowPath` is the full window path to swap to. Edit this dataset **only through the Dataset Editor** (Property Editor → Items → Dataset Viewer icon) — editing through the Tree View Customizer instead overwrites the whole item dataset. Navigation itself is not automatic and needs a `mouseClicked` handler checking `event.clickCount == 2`, reading `event.source.selectedItem` (a row index) and `event.source.data.getValueAt(row, "windowPath")`, then calling `system.vision.swapTo(windowPath)`. Best for large window counts since the tree is compact and supports folder nesting.

**Drill Down** — a background image (facility map, plant photo) with Drawing Tool shapes (rectangle/circle/polygon) overlaid on each area of interest. Each shape gets a `mousePressed` handler configured via the Navigation tab of its Scripting dialog: select **Open/Swap**, pick the target **Window** from the dropdown. `Mouseover Text` on each shape is commonly used to show the area name before the user clicks. The overview map window is typically flagged **Open on Startup**; each detail/area window gets its own back button with the same Open/Swap navigation pattern pointed back at the map.

### Popup windows

A popup is any window with `Dock Position = Floating` and not maximized; it floats over the main window and can be resized/moved by the user without closing the main window. **Layer** controls popup-vs-main z-order — all windows default to Layer 0, so bump a popup's Layer property above 0 to guarantee it stays on top even when the main window regains focus (at Layer 0, clicking the main window can visually bury the popup behind it, even though the Windows menu shows it's still open). **Location** (Property Editor → Layout → Location, X/Y in px) gives a popup a fixed screen position; the **Open and Center** option must be *unchecked* on the opening script/action or it overrides the explicit Location every time.

Opening a popup is done from a component's `actionPerformed`/`mousePressed` scripting via the **Navigation** tab of the Script Builder — Open/Swap action, target window from the dropdown, optional **Pass Parameters** rows (see below), and an **Additional Instance** checkbox for opening more than one copy of the same popup simultaneously (four tank popups, one per tank, all open at once) — equivalently, `system.vision.openWindowInstance(...)` from script for more complex multi-instance logic. By default only a single instance of a given popup window is kept open at a time; opening it again just brings the existing instance forward unless Additional Instance / `openWindowInstance` is used.

**Parameterized popups** — the receiving popup window gets custom properties on its **Root Container** (right-click → Customizers → Custom Properties; leave them **unbound**, since the opening script writes into them directly, and any other binding would fight that write). The opening component's Script Builder Navigation tab has a **Pass Parameters** checkbox → **Add** row → pick the target's custom-property **Parameter Name** from a dropdown (Ignition auto-discovers it from the target window's Root Container) → enter a literal or property-sourced **Value**. Inside the popup, everything else (labels, Indirect Tag bindings, etc.) references `{Root Container.paramName}` for indirection, so one popup design serves every instance of the thing it displays (e.g. one Compressor-detail popup reused for Compressor 1, 2, 3…, driven entirely by a passed `compNum` integer).

**Passing a UDT to a popup** works the same way except the popup's custom property is itself typed as a specific, pre-defined UDT (not a scalar), and the value passed in at open-time is an entire UDT Tag instance rather than a literal — this gives the popup binding access to every member Tag inside that UDT instance in one shot, useful for "show me everything about this equipment instance" detail popups.

### Templates in depth

Two categories of template custom property, both configured the same way (right-click background → Customizers → Custom Properties → Add) but exposed differently:
- **Template Parameters** are exposed on every instance dropped on a window/other template, for external binding — but they are **not bindable from inside the master template's own design**, which is a deliberate constraint ensuring each parameter carries exactly one binding, set per-instance from the outside.
- **Internal Properties** are the opposite: bindable freely *inside* the master design (internal plumbing between the template's own components) but never exposed to the outside world on an instance.

Templates have no Root Container — the template canvas itself is the container, and it is transparent by default (settable to an opaque background color if desired). Double-clicking a template in the Project Browser, or double-clicking any instance on a window, opens it for editing; editing the master immediately propagates to every instance project-wide.

**Template indirection** has two documented approaches: (1) pass a scalar (Integer/String) Template Parameter and use it as an Indirect Tag binding's `{1}` reference inside the template — e.g. Tag Path `[default]Ramp/Ramp{1}` with `{1}` bound to the template's own `tankNumber` parameter; (2) pass the parameter typed as a whole **UDT**, which creates a complex property whose sub-properties mirror the UDT's members one-to-one, each bindable inside the template with ordinary Property bindings (e.g. `{Tank.tankUDT::Meta.TagName}` to read the UDT instance's Tag name, or bind a Slider directly to `tankUDT.sliderValue`). **Explicit limitation**: Template Canvas and Template Repeater cannot pass a UDT-typed parameter through to an embedded template — only scalar indirection (approach 1) works inside those two container components.

**Template Canvas** — holds instances of **multiple different** master templates at once, laid out either **Absolute Positioning** (each instance has X/Y/Width/Height plus a **Z-index** field controlling stacking order within the canvas) or **Layout Positioning** (MiG Layout grid syntax — e.g. entering the literal string `wrap` in an instance's layout field forces the next grid cell onto a new row). Absolute and Layout positioning should not be mixed on the same canvas. Everything the customizer does is really just editing the canvas's own **Templates** dataset property (Name, Template path, Parameters as a JSON-like map, x/y/layout/z columns) — so it can equally be driven by a SQL binding or a Cell Update binding to load/rearrange instances at runtime, or edited directly via the dataset's own Dataset Viewer. `canvas.getAllTemplates()` from script returns a list of every instance object on the canvas, with each instance's parameters accessible as plain attributes (`template.TextField_Text`), useful for bulk-reading a canvas built as a dynamic input form.

**Template Repeater** — repeats a **single** master template only, arranged Vertical/Horizontal/Flow (top-to-bottom or left-to-right), auto-adding a scrollbar once instances overflow the visible area. Two distinct **Repeat Behavior** modes: **Count** mode takes a **Repeat Count** and an **Index Parameter Name** (the name of one Template Parameter on the master, which each instance receives as its own 0-based index — instance 0 gets index 0, instance 1 gets 1, etc.); **Dataset** mode instead binds the **Template Parameters** property to a dataset where each *row* is one instance and each *column name* must exactly match (case-sensitive) one Template Parameter name on the master — required whenever more than one parameter needs to be passed per instance, or when the driving values aren't a clean zero-based sequence (e.g. Ramp numbers 2, 5, 7, 3, 8 in that exact order, non-contiguous and non-sequential). Dataset mode's Template Parameters property can itself be bound (SQL, Named Query) so repeater contents come from a database table.

### Easy Chart in depth

**Pen types** — **Tag Pens** are created by dragging Tags from the Tag Browser directly onto the chart; each needs an Aggregation Mode and can span multiple history providers/databases on one chart. **Database Pens** are driven by hand-specified **Datasource** (the Gateway DB connection), **Table Name**, **Value Column** (drives Y-position), **Time Column** (drives X-position), and an **Axis** — ideal for Transaction Group tables or any other externally-timestamped SQL table, since they bypass the Tag Historian entirely. **Calculated Pens** derive their value from a **Driving Pen** at render time (never stored) and **cannot** be configured via a direct binding inside the customizer — to make a calculated pen's own parameters dynamic (e.g. a variable Constant setpoint), use a Cell Update binding targeting the `calcPens` dataset property instead, the same mechanism used for Indirect Easy Chart.

**Calculated Pen functions** (Function dropdown on the Edit Pen dialog, each with its own extra property): Constant (**Constant Value**), Upper/Lower Control Limit (±3σ from the driving pen's mean, no extra params), Upper/Lower Warning Limit (±2σ), Average, Moving Average (**Window Size**, expressed as a multiplier of the chart's date range, e.g. `.2`), Multiply Pen (**Factor**), Minimum/Maximum Value, Running Sum, Sum and Difference (each needs a **Secondary Pen** — the second driving pen), Linear Regression. Disabling/hiding the driving pen also hides dependent calculated pens by default; to keep a calculation visible while hiding its source line, set the driving pen's own **Hidden** property to `true` rather than disabling it outright.

**Axes** — Numeric (default), Logarithmic, or **Symbol** (maps ascending numeric values to a comma-separated ordered label list entered in **Symbols/Grid Bands**, e.g. `Auto,Off,Hand` for values 0,1,2 — good for turning a Multi-State Button's numeric history into readable text on the axis). Each new axis is added via the Axes tab's Add icon and given a **Name**, **Label**, **Type**, optional Label/Tick Label/Tick Color styling; **Position** (which chart edge it draws on) is normally left to **Auto Axis Positioning** on the chart itself and only hand-set after disabling that. **Auto Range** (default true) pads automatically; disabling it exposes manual **Lower Bound**/**Upper Bound**. Every pen must be assigned to exactly one axis (Pens tab → Edit Pen → Axis dropdown), and removing all pens from a given axis lets Auto Positioning re-flow the remaining axes.

**Pen Names and Groups** — the pen's display name defaults to its source Tag's name; rename per-pen and set a **Group Name** (Edit Pen dialog, or double-click directly on the rendered legend at runtime for a faster edit) to cluster related pens under one legend heading — e.g. grouping several Ramp pens under "Ramps" and several Sine pens under "Sines" produces two separate legend sections instead of one flat list.

**Pen Renderer** — per-pen Style/Color/Weight/Shape editable from the Edit Pen dialog's right-side Style controls, with a live preview; default Style is **Line w/ Gaps**, which visibly breaks the line during a communication loss or missing-data period rather than interpolating across it.

**Ad-hoc charting (Tag Browse Tree)** — pair a **Tag Browse Tree** component with an Easy Chart, setting the tree's **Include Realtime Tags = false**, **Include Historical Tags = true**, and **Selection Mode = Multiple - Discontiguous** (enables non-adjacent Shift-click multi-select in the tree). Users drag Tags from the tree onto the chart at runtime to add pens, and click each pen's built-in delete-X to remove it; whatever pen set exists when the Designer last saved the window is what a freshly-launched Client will show by default. Because the tree gives no way to choose an axis, a dropped Tag's axis is auto-matched by comparing its Engineering Units metadata to an existing axis's units, falling back to the default axis when nothing matches.

**Indirect Easy Chart** — makes the whole set of historical Tags a chart displays swap dynamically (e.g., "whichever tank the operator picked from a Dropdown"), via a Cell Update binding on the Easy Chart's own **Tag Pens** dataset property: drag the real Tags on first (for the initial pen structure), then open a Cell Update binding on Tag Pens, select each pen's Tag-Path cell, add a Cell Binding row, and set its Value to a mixed literal+reference string such as `[~]Tank/{Root Container.Dropdown.selectedStringValue}/Temperature` — the `{...}` portion is replaced with the Dropdown's `selectedStringValue` live, repointing the pen at a different Tag family whenever the operator's selection changes.

### Common tasks and component techniques

**Images and SVGs** — dragging an SVG file onto a window imports it as a grouped path-based component (small initial render size is common, just resize up); supported element/attribute coverage tracks the embedded **Apache Batik** library, not the full SVG spec. Two documented coloring techniques: *coloring SVG parts* — ungroup down to the individual `<path>`, set that path's own `Fill Paint` (via Expression + `color()`, or a Tag/Property binding's built-in Number-to-Color Translator), then re-group; *SVG tinting* — for symbols too intricate to recolor path-by-path, duplicate the whole SVG, select the duplicate and apply **Union** (Shape menu) to flatten it into one shape, set its `Stroke Paint = No Paint`, bind its `Fill Paint` via a Tag binding's Number-to-Color Translator using semi-transparent colors (e.g. ~40% opacity green/red/white), then **Alignment > Move to Front** and group the tinted flat shape directly on top of the original symbol — the semi-transparent overlay reads as a color tint without touching any of the original symbol's individual paths. Standalone images come from the Gateway-hosted **Image Management Tool** (folder-search icon next to `Image Path`) or a `file:///` local filesystem path — local paths only render if that exact path is reachable from wherever the Client happens to be running, so a shared network drive is recommended over a Designer-machine-local path.

**High Performance HMI techniques** — gray-scale base graphics, reserving saturated red/orange/yellow exclusively for abnormal states so they visually "pop" against the neutral background; a documented convention uses dark gray specifically for a "scheduled" (intentionally off, not faulted) equipment state, which is called out as a common point of operator/maintenance-tech confusion when a traditional bright-color scheme is used instead. Fault state should be indicated by a dedicated **Alarm Indicator** object (colored shape + number/text, optionally with a dotted connecting line to the actual equipment) rather than by recoloring the equipment body itself, both to reduce ambiguity about which specific alarm is active and to remain legible for colorblind viewers or on a display that's temporarily lost color rendering — descriptive text paired with color is the recommended colorblind-accessible pattern. Purpose-built components for this style: Moving Analog Indicator, Sparkline Chart, Radar Chart.

**Dropdown List** — the `Data` dataset property drives which of `Selected Value` / `Selected String Value` / `Selected Label` populate, based purely on column count/type (extra columns beyond the first two never affect these three derived properties, but can still be surfaced to the user by setting `Dropdown Display Mode = Table`): a leading Integer column + String column pair is **Number/Label** mode (hidden numeric Value, visible Label); two String columns is **Single Label Column** mode (hidden first-column string as `Selected String Value`, visible second-column Label); a single String column alone is **Code/Label** mode (that one value serves as both `Selected Label` and `Selected String Value`). Options can be entered manually via the Dataset Viewer, or bound (commonly a SQL Query binding returning an id/name pair from a table).

**Custom Input Template** — a small reusable template with two String Template Parameters, `display` (label text, property-bound one-way to a Label's Text) and `text` (bidirectionally property-bound to a Text Field's Text), plus a validation Expression binding on the Text Field's `Background`: `if(len(trim({textBox.Text Field.text}))>0, color(255,255,255), color(255,0,0))` — turns the field red until the operator types something non-blank. This "validate + visually flag" pattern generalizes to any templated input field.

**Component animation** — two distinct techniques depending on what's being animated. *Actually moving a component* — bind a moving part's transform property directly (classic case: a Symbol Factory **Enhanced** symbol's sub-group, e.g. `Group_Impeller`, has its own `Angle` property; bind it to a Timer's `Value` with the Timer set to Delay 200ms / Step By 10 / Bound 360 / Running=true for a continuously-spinning fan/impeller), or drive it from script with `system.vision.transform(...)` for event-triggered rather than continuous motion. Search Symbol Factory with the **Enhanced** radio button specifically to get symbols with these internal sub-groupings — non-Enhanced symbols don't expose animatable sub-parts. *Cycling static images to fake motion* (e.g. a conveyor belt) — duplicate the graphic N times (11 copies in the documented example), ungroup each copy down to its moving detail path and shift that path progressively further left/right per copy so the sequence reads as continuous movement when flipped through, then re-group each copy and bind each copy's `Visible` to `if({Root Container.Signal Generator.value} = N, 1, 0)` (N = that copy's index) so exactly one copy is visible at a time, driven by a **Signal Generator** in **Ramp** mode with Values/Period and Upper Bound both set to the copy count.

**Client Tags for cross-window indirection** — bind a window's Root Container custom property (e.g. Integer `MachineNumberRef`) to a Vision Client Tag via a Tag binding; every component on that window (and on every other window using the same pattern) then uses `{Root Container.MachineNumberRef}` inside Indirect Tag bindings. Because Client Tags are per-running-Client, two separate Clients viewing the identical window set can independently be looking at two different machines simultaneously — changing the value in one Client's UI (e.g. a Numeric Text Field or a dragged-on Tag control bound to the Client Tag) does not affect any other open Client.

**Dynamic startup windows** — remove "Open on Startup" from the target main windows themselves and decide which one to open from a Client **Startup** event script using `system.security.getRoles()` and `system.vision.openWindow(...)`, so the actual displayed screen depends on the logging-in user's role rather than being static per-project.

**Tank Cutaway** — from Symbol Factory, drag a Tank (Tank category) and a matching Cutaway shape (Basic > Tank Cutaways category) onto the window and align the cutaway over the desired viewing area; select the tank **first**, then Ctrl-select the cutaway (selection order matters — the first-selected shape is the one retained), and apply **Shape > Difference** to punch the cutaway's outline out of the tank. Place a Level Indicator component in the resulting cut area, bind its `Value`, then use **Alignment > Move Back** to tuck it behind the tank graphic so the tank's own outline still reads as the container. Optionally group the whole assembly (and template-ize it) for reuse across multiple tanks.

**Component Customizers** — most special components (Easy Chart, Table, Tab Strip, Multi-State Button, etc.) have their own dedicated customizer UI, but every customizer is really just a friendlier editor over one or more underlying dataset/expert properties (e.g. the Easy Chart Customizer edits the `pens`, `tagPens`, `calcPens`, `axes`, and `subplots` dataset properties directly) — meaning anything doable in a customizer dialog is also directly bindable/scriptable on the underlying property for runtime dynamism the dialog itself doesn't expose. Custom Properties (right-click → Customizers → Custom Properties) can be typed as a UDT Definition, which creates a matching complex property with one sub-property per UDT member — the same mechanism templates use for UDT-typed parameters.

**Comparison charts (categorical, not time-series)** — deeper field notes beyond the earlier summary: the **Bar Chart**'s initial `Data` dataset ships as `Label` + one column per series (e.g. `North Area`, `South Area`) with rows as categories (months); **Extract Order = By Row** treats each dataset *row* as a series and each non-first *column* as a category, **By Column** treats each row as a category and each column as a series — same data, transposed grouping, no data change required to flip between them. The **Radar Chart**'s `Data` needs `Value`/`Min`/`Max` columns at minimum, and needs **3+ rows** to render as a proper polygon (1–2 rows degrade to a straight vertical line); dragging Tags onto it auto-creates a Cell Update binding wiring each Tag's Value/EngLow/EngHigh into a new row, and the Min/Max midpoint per row draws the white "desired" reference polygon used to eyeball off-spec values at a glance. The **Pie Chart** needs `Label` + `Value` columns in By-Column mode; switching to **By Row** extract order instead reads one column per wedge and only the *first row* of the dataset — extra rows are silently ignored in that mode. The **Box and Whisker Chart**'s first column is a case-sensitive `Key` (domain/series grouping label, e.g. `Lot A`/`Lot B`), with each additional column a category whose raw (non-aggregated) values Ignition itself reduces into the box/whisker statistics — you always supply raw per-sample data, never precomputed quartiles.
