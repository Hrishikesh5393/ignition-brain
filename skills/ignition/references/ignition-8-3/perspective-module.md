# Ignition 8.3 — Perspective module

Source: live Ignition 8.3 User Manual (docs.inductiveautomation.com/docs/8.3/), Perspective module pages, session/scoping pages, style reference, and event-types reference. This is a dense developer reference, not a tutorial — read the linked manual pages for step-by-step click-throughs.

---

## Concepts

### Sessions, Pages, Views — the hierarchy

Perspective replaces the Vision "Client" with a **Session**: a running instance of a project inside a web browser (or the Ignition Perspective mobile app, or Perspective Workstation). A single Session can span multiple browser tabs/pages simultaneously — much like a shopping site where every open tab shares your cart/login.

The runtime hierarchy, bottom to top:

- **Component** — buttons, labels, charts, gauges, etc. The design-time building block.
- **Container** — holds components and *defines the layout strategy* for its children (Coordinate, Flex, Breakpoint, Split, Tab, Column…). Containers nest inside containers.
- **View** — the primary unit of design. A View has exactly **one root-level container**, chosen at creation time and not changeable afterward. Views are project resources organized in folders in the Project Browser; their folder path uniquely identifies them and is used for runtime navigation. A View can act as either a full-page screen *or* an embedded component nested in another View (via the Embedded View component or a repeater). Views roughly correspond to both Vision Windows and Templates combined.
- **Page** — a collection of Views shown together in one browser tab: exactly one **primary view** filling the center, plus optional **docked views** anchored to the Top/Bottom/Left/Right edges, plus floating **popup views**. A Page is bound to a URL ("Page URL"), so browser Back/Forward work as navigation.
- **Session** — can have any number of open Pages (tabs) at once.

Comparison table (Perspective ↔ Vision):

| Perspective | Vision analog | Notes |
|---|---|---|
| Session | Client | Runs in browser instead of Java; multiple pages share one session, like browser tabs sharing a login |
| Page | Desktop / multi-monitor client | Bound to a URL; consists of a primary view + docked views |
| View | Window + Template | Root container defines layout; can be embedded (template-like) or be a top-level screen (window-like) |
| Container | Container + layout constraints | Layout strategy lives on the container, not each component |
| Component | Component | Same concept, different palette |
| Property | Property | JSON-typed: value / object / array (no more per-type configuration) |
| Session Property | Client Tag | Per-session variables, visible to all views/scripts in that session |
| Events and Actions | Component scripting | More event types + declarative "Actions" in addition to script actions |
| Styles | Style properties/Customizer | CSS-based; Style Classes give reusable, inheritable style bundles |

### The JSON model of a view and its mapping to disk

Every Perspective component's configuration is JSON. There are exactly three property data types:

- **Value** — primitive: boolean, numeric, or string.
- **Object** — a JSON object (string-keyed map); Perspective renders it with `{ }`.
- **Array** — a JSON list (`[ ]`), each element itself a value/object/array.

Perspective adds convenience *variants* of Value for UI purposes only (Dataset, Date, Color) — on the wire these are still primitives/arrays of primitives.

Component properties are grouped into categories, most of which show up as JSON keys under the component/view resource:

- **props** — the component's own configuration/runtime data (documented per-component).
- **position** — layout attributes controlled by the *parent container type* (e.g., x/y/width/height in a Coordinate container; grow/basis in a Flex container).
- **custom** — user-defined properties (safe place for your own data; never collides with hidden built-in properties).
- **meta** — Perspective-module-defined properties every component has: `name`, `visible`, `tooltip`, `contextMenu`, and the hidden-by-default `domId`/`tabIndex`.
- **params** — **Views only**. Defines input/output/in-out parameters for passing data across a view boundary (docked view, embedded view, popup, or page URL parameter).

On disk, each View is a project resource: a folder under `Perspective/Views/<path>` in the project's resource tree, holding a `view.json` (the JSON property tree described above) plus a resource.json. Style Classes live similarly under a `Styles` resource folder, and Page Configuration is stored as project-level Perspective settings (not per-view). Because JSON is the wire and storage format, HTTP/Query/Tag-History bindings that return JSON documents can populate a component's property tree directly, and a Script Transform that returns a Python dict/list becomes an object/array property.

### View properties: props / position / meta / custom / params

At the View level (not a generic component), the property panel is organized as: **Props** (visual/behavioral config of the view's root container), **Custom** (user-defined, scoped to the view, visible to all children), and **Params** (input/output contract for the view). View params are what let a view interchange data with whatever mounts it — a docked view configuration, an Embedded View component, a page URL, or a UDT drop configuration.

### Primary view, docked views, popups

- **Primary View** — the one view every Page must have, filling the center region.
- **Docked View** — anchored to Top/Bottom/Left/Right; only one dock per edge per page configuration. Configured under **Page Configuration** (the Perspective icon at the bottom of the Designer), either per-page or under **Shared Settings** (inherited by every page in the project). Key docked-view properties:
  - `Display`: `visible` (always shown) / `onDemand` (collapsed, opens via handle) / `auto` (shows/hides based on the **Auto Breakpoint** page width).
  - `Content`: `push` (center view resizes out of the way) / `cover` (dock slides over center) / `auto` (cover below breakpoint, push above).
  - `Modal?` (only with `onDemand`), `Resizable?`, `Anchor` (`fixed`/`scrollable`, North dock only), `Size` (height for N/S, width for E/W), `Dock ID` (for scripted/action control), `Handle` (`Show`/`Hide`/`AutoHide`), `View Parameters`.
  - **Corner Priority** (page-level) decides whether top/bottom docks or left/right docks get the corners.
- **Popup View** — floats over the primary view, opened via a Popup Action or `system.perspective.openPopup()`. Gets a built-in title bar automatically if a `title` is set, `showCloseIcon` is enabled, or `draggable` is enabled. Popup Action settings: Open/Close/Toggle, an **Identifier** string (needed to close it later), Draggable, Resizable, Modal, Background dismissible (only meaningful when Modal), Position Exact vs Position Relative (mouse-anchored), Viewport Bound.
- **Embedded View** — not a page-layout region but a component (`Perspective - Embedded View`) that nests one view inside another. Key props: `path` (view to embed), `params` (object passed to the embedded view's input/output params — must name-match), `useDefaultViewWidth`/`useDefaultViewHeight` (whether the embed keeps the source view's authored size or stretches to fit — uncheck to kill unwanted scrollbars).

### Page configuration and URL routing

Every Page is mounted at a **Page URL** (must start with `/`); the project's "home" page should use `/`. Page Configuration screen shows Page Title (falls back to the project name), the primary view assignment, and docked-view assignments (per-page or Shared).

**Dynamic/parameterized URLs**: use colon-prefixed segments, e.g. `/:towerNumber`. Navigating to `.../2` sets the primary view's input parameter `towerNumber = "2"`. Invalid characters in a parameter segment: `/ ? # %`.

**Query parameters**: anything after `?` in the URL is parsed into the read-only `page.props.urlParams` object (all values arrive as strings). Query params only populate via direct browser navigation or `system.perspective.navigate(url=...)` — page-navigation *actions* don't carry query strings, since navigation actions are for in-session page routing only.

Page runtime properties (bindable/scriptable, not visible in the property editor since Pages aren't Designer-selectable objects): `pageId` (design-time = view name, runtime = generated string like `"2bf737f8"`), `path`, `primaryView`, `appBarVisible`, `dimensions` (`viewport`, `screen`, `primaryView` sub-objects with width/height/scroll), `urlParams` (read-only), `title` (writable — scripts/bindings can retitle the browser tab).

### Component palette categories

The Component Palette groups every built-in component into six categories: **Chart**, **Container** (layout/positioning), **Display** (static/dynamic info), **Embedding** (Embedded View, Flex Repeater, View Canvas, Accordion — components that instantiate other views), **Input** (data entry / device control), **Navigation** (Link, Menu Tree, Horizontal Menu — in-session routing). Some components expose **Variants** — pre-configured property bundles for a common use case (e.g. Time Series Chart's Line/Area/Bar/Scatter variants), indicated by a number badge next to the component name in the palette; picking a variant is a shortcut, not a different component type. The palette itself can be viewed as a flat **List View** (category + name) or thumbnail **Tile View**, and supports the same case-sensitive/wildcard/regex/match-anywhere search-filter options as the Property Editor's search bar.

### Designer interface essentials

The Perspective workspace adds a dedicated toolbar, Property Editor, and Project Browser badges on top of the shared Designer chrome (File/Project/Help menus are shared with Vision).

**Selecting components**: single-click selects; double-click **deep-selects** into a container (thick solid border, darkened surrounding area, a Deep Selection badge in the Project Browser) so you can select something nested without first selecting each intermediate container. Alt+Shift+click is a single-click alternative to double-click deep-select. **Select-through**: Alt+left-click a nested component selects it *and* auto-deep-selects its parent in one step. Click the gray design-area background to pop back up to the top-level view from a nested selection. Drag-selection direction matters: left-to-right rectangle selects only fully-enclosed components; right-to-left selects anything the rectangle touches; hold Alt while dragging for a touch/line-selection.

**Project Browser badge icons** next to a component's name flag extra configuration present on it: Binding, Custom Method, Deep Select (on the currently-selected nested component), Event Action, Message Handler, Script (a property change script), Security (permissions applied). The **Configuration Explorer** (right-click a view/component) lists every Binding/Transform, Custom Method, Embedded View, Event/Action, Extension Function, Message Handler, and Property Change Script live on that object, with a **Go To Reference** jump.

**Z-order** (right-click menu): Send to Back / Move Backward / Move Forward / Bring to Front — controls draw order for overlapping components. **Wrap in Container** one-step-wraps a selected component in a new parent container. **Alignment tools** (Coordinate containers only): align left/right/top/bottom/center-horizontal/center-vertical, plus "align as row"/"align as stack" each with a Normalize variant that resizes the whole group to match the first-selected component (rotation-aware). Rotation: drag a component's rotation handle, or set `position.rotate.angle` directly (handle/anchor UI hidden below 28×28px — use the property editor instead).

**Preview Mode** (toolbar toggle) runs the currently-open view "live" in the Designer — bindings and event handlers execute exactly as they will in a Session, without a full browser launch. Gateway communication has a 3-state toggle: disabled / read-only (SELECT-only) / full read-write, useful for testing UI without risking writes. **External Debugger** (Tools > Launch Project) opens Chrome DevTools against the Designer's own JxBrowser-rendered view for inspecting the live DOM/console.

### Project Properties reference (Perspective section)

Project Properties > **Perspective** spans several functional sub-areas (menu bar: **Project > Project Properties**):

**General**: `Enable Update Notification` (+ `{timeLeft}` token message; false = silent immediate update), `Project Locale` + `Include regional variations`, `Hide from Launch Page and Native Apps`, `Launch Icon` (uploaded Gateway image, used on the launch page and mobile app listing, and as the Android shortcut icon), `Project Timezone` (Gateway / Session / specific zone), `Session Timeout Desktop` / `Session Timeout Mobile` (seconds), `Session Closed Message` (shown on `system.perspective.closeSession`), `Page Closed Message` (shown on `system.perspective.closePage`), `Logged Out Message`.

**Permissions**: an interactive security-levels tree gating whole-project session access; `All` (must match every checked level) vs `Any` (at least one) radio choice — same semantics as View permissions.

**Tag Drop**: governs what happens when a tag is dropped onto *empty space* in a view (distinct from a view's own `dropConfig`, which governs drop-onto-an-existing-view-instance). Two linked tables: **Data Type Configuration** (per tag data type, which component types are offered in the drop popup) and **Component Bindings Configuration** (per offered component type, which prop paths get bound to which tag property, e.g. `value` → `props.value`, plus per-binding `Bidirectional`/`Coalesce` checkboxes — Bidirectional is on by default for Input-category components).

### Session lifecycle

Ways to launch a Session: from the Designer (**Tools > Launch Perspective > Launch Session**), from the Gateway webpage (**Home > Perspective > Sessions > View Projects > Launch**), by typing the project URL directly, via Perspective Workstation, or via the Ignition Perspective mobile app.

Every Session runs a websocket connection to the Gateway. If it drops, a banner appears and the Session keeps retrying; it resumes normally on reconnect — unless the underlying project was deleted or overwritten (Gateway restore), in which case reconnection permanently fails.

Closing a browser tab does **not** immediately end the Session — it lingers until the configured **Session Timeout** elapses (Project Properties > Perspective > General: separate Desktop/Mobile timeouts). Shutdown scripts fire on: timeout, loss of authorization, redundancy failover, licensing loss, or the project being deleted/made unrunnable.

**Project Updates**: saving a change in the Designer either silently updates running sessions, or (if **Enable Update Notification** is on) shows a banner with a countdown (`{timeLeft}` token) and an **Update Now** button.

Minimum supported browsers for 8.3.0: Chrome 92, Firefox 90, Safari 15.4, Edge 92.

### Session properties reference

`session.props` is the closest Perspective analog to a Vision Client Tag set — per-session, readable/writable from any view via binding or scripting, and the standard channel for cross-view state that Object Traversal can't reach. Full table (system-managed entries carry a **System** badge in the Property Editor and can't be edited/removed):

| Property | Description |
|---|---|
| `id` | Unique session identifier (string) |
| `host` | Connecting host/IP (affected by the Gateway's **Resolve Client Hostname** web-server setting) |
| `theme` | Active theme name (default `light`); writable at runtime |
| `locale` | BCP-47 language tag, e.g. `en-US` |
| `timeZoneId` | Session time zone id, e.g. `America/Los_Angeles`; can be bound to `gateway.timezone.id`/`device.timezone.id` to auto-follow Gateway/client TZ (Project Properties Timezone Behavior) |
| `lastActivity` | Last-interaction timestamp, Gateway time, read-only |
| `auth.*` | See Security section |
| `gateway.address` / `gateway.timezone.{id,name,utcOffset}` / `gateway.connected` | Gateway connection info; `connected` requires every tab in the session to have a live websocket |
| `device.type` | `ios` / `android` / `designer` / `browser` / `workstation` (empty string while loading) |
| `device.identifier` | Convenience-only device id (not for security use — can change on reinstall/cache clear) |
| `device.timezone.{id,utcOffset}` | Device-reported TZ |
| `device.userAgent` | Browser/device user agent string |
| `device.settings.pullToRefresh` / `.preventSleep` | Mobile app behavior toggles (default `true`/`false`) |
| `device.accelerometer.{timestamp,x,y,z}` | Populated during Continuous accelerometer capture |
| `bluetooth.enabled` / `.options.{updateInterval,limit,filter}` / `.data` | Filter sub-object supports `altBeacon`/`eddystone`/`iBeacon` with `exclusive`/`uuid`/`nameSpaceID`/`minimumRSSI` |
| `geolocation.enabled` / `.permissionGranted` (read-only) / `.options.{accuracy,maximumAge}` / `.data.{latitude,longitude,altitude,accuracy,altitudeAccuracy,heading,speed,timestamp}` | `accuracy` options: `max`/`balanced` (default)/`low` |
| `appBar.togglePosition` (`left`/`right`/`hidden`) / `.about.{show,icon,path,title}` | Controls the bottom app-bar toggle and custom About modal |
| `pipes.autoAppearance` / `.overlapGap` (default 4; 0 or negative disables overlap rendering — can help render performance) | Perspective Pipes global config |
| `symbols.autoAnimationSpeed` / `.autoAppearance` (`auto`/`p&id`/`mimic`/`simple`) | Governs any Symbol component set to `auto` |
| `googleMapsApiKey` | Required for the Google Map component |
| `address` | Session's IP address as seen by the Gateway |

### Session App Bar

Every session has a collapsible **App Bar** at the bottom (expand via the Maximize icon). It shows an **About Ignition** popup (installed modules + versions) and a **Session Status** popup with Gateway/Project tabs (connection status, Gateway URL, Session ID, page ID, view/component/property-change counts, Latency, Up Time, a Visit Gateway shortcut, and project up-to-date status). The toggle icon's screen position is controlled by `session.props.appBar.togglePosition`. Trial Mode adds a Timer icon showing the trial countdown. App Bar visuals (show/hide, About icon/view/title — defaults: `Show = FALSE`) are further customizable under **Perspective Co-Branding** on the Gateway (Home > Perspective > Brand Customization; Standard/Cloud Edition only), which also covers General (`Custom Branding` on/off), Colors (Background/Text/Button/Button Text), and Graphics (`Logo` — jpg/png, ~160×160; `Favicon` — png, ~180×180, shown on the browser tab after refresh; `App Icon` — png, ~180×180, used when an iOS user saves the session to their home screen; note transparency in a Logo/Favicon renders fine but an App Icon with transparency renders solid black). Icon design notes from the manual: 16×16 or 32×32px favicons suit desktop (browsers upscale fine from a larger source); 180×180 or 192×192px suits multi-platform/Android use (many Android devices ignore smaller favicons entirely, and Chrome-on-Android specifically won't use an undersized favicon when saving to the home screen).

### Reverse proxy considerations

Perspective's websocket architecture requires specific reverse-proxy configuration, not just a plain HTTP passthrough:
- Force **HTTP/1.1** and forward the `Upgrade`/`Connection: upgrade` headers (websocket upgrade won't work over a naive HTTP/1.0-style proxy pass).
- Whitelist/forward custom headers the session relies on: `client-timezone`, `device-id`, `device-type`, `version-code`, `perspective-session-id`, `designer-session-id` (e.g., `proxy_pass_request_headers on;` in NGINX).
- Proxy several **additional location contexts** beyond the project path itself: `/data/`, `/system/`, `/res/`, `/idp/`, `/.well-known/` all need to resolve back to the Gateway.
- The Gateway's **Use Proxy Forwarded Headers** setting (Network > Network Settings > Web Server) lets the Gateway trust the proxy's reported client IP/host instead of the proxy's own connection details.

---

## Property model and bindings

### props / position / meta / custom / params — recap

See Concepts above for the category breakdown. Practical implications:
- Add user properties to **Custom** or **Params** only — adding to Props/Position/Meta risks colliding with a hidden built-in property of the same name and silently breaking the component.
- **Property access levels** (right-click a property > Access): `Public` (default; browser-side JS can read/write), `Protected` (browser DOM interaction is inert — backend ignores write attempts from JS, but bindings/scripts can still write), `Private` (also hidden from read), `System` (fully backend-managed, not user-writable, cannot be removed). This is a defense against a user opening devtools and scripting the DOM directly to bypass validation — not a general ACL. Style Class *names* are always visible client-side regardless of access level.
- **Persistence**: properties save their value with the project by default (**Persistent**). Any property with a binding auto-becomes non-persistent (its value is going to be overwritten on load anyway). A user-created property that is not flagged Persistent is discarded when its containing view closes in the Designer, and won't exist at all in a Session — *unless* it has a binding configured, which forces re-creation. Toggle via right-click > Persistent.

### Parameter direction (in / out / in-out)

View **params** must each be one of:
- **Input** — not bindable from inside the view's own config; receives values pushed in from outside (page URL segment, docked-view parameter, embedded-view `params`, or navigation-action parameter). Becomes bindable from outside once the view is instantiated.
- **Output** — the opposite: bindable from inside the view, read-only from outside.
- **In/Out** — bindable both ways; useful for a "decorator" view that both consumes and republishes a value across its own boundary.

### Bidirectional bindings

Tag and Property bindings can be checked **Bidirectional**: the bound property still reads updates from the source, but user/script writes to the property now also write back to the source. Checking Bidirectional exposes **Coalesce** — when on, writes to multiple child properties of a complex (object/array) target are combined into a single write-back instead of one write per child change (Coalesce defaults off).

### Binding property paths

Within one view, properties reference each other with a path syntax (see `binding-property-path-reference`):

| Token | Meaning |
|---|---|
| `/` (leading) | Absolute path from the view root |
| `/` (mid-path) | Descend into a child container |
| `.` | Dot into a nested property document, e.g. `.meta.rotate.angle` |
| `[n]` | Array index |
| `../` | Parent-container shortcut; stack for multiple levels (`../../Label.position.x`), or use extra dots (`.../Label...`) |
| `./` | "Container self" shortcut — only valid on a binding configured on a container |
| `this` | The component the binding lives on |
| `parent` | Immediate parent — valid only from a component's scope |
| `view` | The containing view; `view.params.paramName` reaches a view parameter |
| `page` | The containing page — valid only from a view's scope |
| `session` | The session object, reachable from anywhere — the *only* sanctioned way to share state across separate views (a binding can never directly reference a property in another view instance) |

### Binding types

**Tag binding** — subscribes a property directly to a tag (defaults to the tag's `value` property if you pick a bare tag). Three modes:
- *Direct* — fixed tag path.
- *Indirect* — tag path built from `{1}`, `{2}`… placeholders, each wired to a Property or View Parameter reference; lets one binding dynamically follow "Motor {n}/Amps" style paths.
- *Expression* — the tag path itself is computed by an expression (string result); this is different from an Expression Binding and is the only Tag-binding mode that stays bidirectional-capable while being dynamic.
- Shared options: **Enabled**, **Overlay Opt-Out** (suppress the bad-quality overlay), **Publish Initial Uncertain Value** (suppress the transient `Uncertain_InitialValue` overlay flash on view open), **Bidirectional**, **Fallback Delay** (seconds before a pending write reverts to the tag's actual value if no write-confirmation arrives).
- Drag-and-drop from the Tag Browser onto a view/component auto-creates bindings per the project's **Tag Drop** configuration (Project Properties > Perspective > Tag Drop): map tag data type → component type → which prop(s) get bound, with per-mapping Bidirectional/Coalesce flags.

**Property binding** — links one property to another *within the same view* (including UDT member properties), or is the mechanism used to pass a value into an embedded view's input param. Cannot cross view instances directly.

**Tag History binding** — pulls historian data. Configuration: Return Format (`Wide`/`Tall`/`Calculations`), Query Mode (`PointCount`, `-1` = as-stored / `AsStored`, `Periodic`), Time Range (`Realtime` window with polling, or `Historical` fixed Start/End expressions — caution: Historical ranges are *inclusive* of the End Date, which can add a spurious interpolated-zero interval at the tail), tag selection (direct or via an **Expression** mode with a JSON array of `{aggregate, alias, path}` objects for dynamic multi-tag paths), Aggregation Mode (Average, MinMax, LastValue, SimpleAverage, Sum, Minimum, Maximum, DurationOn/Off, CountOn/Off, Count, Range, Variance, StdDev, PctGood, PctBad), and Options (Overlay Opt-Out, Ignore Bad Quality, Prevent Interpolation, **Cache & Share**, Value Format Dataset/Document).

**Property binding across a UDT / Query / Expression Structure** — see below.

**Expression binding** — evaluates the Ignition expression language, can reference tags, other properties, and expression functions. Updates on events (property/tag change) by default; only becomes a *polling* binding if the expression uses a function with an inherent update cadence (e.g. `now()`), in which case it polls at the specified rate.

**Query binding** — runs a **Named Query** only (no ad hoc SQL from this binding UI). Path Mode Direct (parameters auto-populate from the Named Query) or Expression (dynamic path + user-defined parameters, values evaluated as expressions so strings need quotes). Return Format: `auto`, `json`, `dataset`, `scalar` (first element only). Options include Cache & Share, Designer Limit (caps rows when previewing in the Designer), and Polling (seconds).

**Expression Structure binding** — the output is an **object**, built from multiple *individual* expressions, one per key in the structure — useful for building a complex parameter object from one binding, or feeding a Script Transform with several pre-computed inputs. `Wait On All` forces every sub-expression to resolve before the object publishes (vs. each key updating independently as its expression resolves).

**HTTP binding** — fetch/post to an arbitrary URL, JSON-aware (a JSON response can populate the property tree directly since Perspective's own property format is JSON). Config: URL (expression — quote static strings), Method (GET/HEAD/POST/PUT/DELETE/TRACE/CONNECT), Headers (key/value, value is an expression), Body (expression), Authentication Type (None/Basic/Bearer/Digest) + Authentication Value, Connect/Socket Timeouts, Allow Cookies, Cache & Share, Polling.

**MongoDB binding** (requires the MongoDB Cloud Connector module) — read-only, structured like an Expression Structure binding: pick Connector, Collection, Query Type (Find/FindOne/Aggregate), build filter/project/sort/collation/limit/skip (Find) or filter/project (FindOne) or aggregate/collation (Aggregate). Writes require `system.mongodb.*` scripting instead.

All binding types share the pattern: **Enabled**, **Overlay Opt-Out**, and where polling applies, **Cache & Share** (a shared Gateway-side polling engine: polls once, caches the result, serves it to every subscribing Session — the cache TTL matches the poll rate, or 250ms if polling is off; big win when many sessions bind to the same slow source).

### Property data types in the Designer

Beyond the three wire-level JSON types (value/object/array), the Property Editor renders a few UI-convenience variants, all still primitives/arrays underneath:

| Type | Notes |
|---|---|
| Value (primitive) | Boolean (blue), Numeric (orange, up to max `long`), String (green) |
| Object | `{ }` — one or more named sub-values |
| Array | `[ ]` — indexed sub-values, each itself value/object/array |
| Dataset | Value variant; only appears when a binding returns dataset-shaped data (SQL query, Tag History) or a script writes one; shows `rows x columns` plus a Dataset Browser/editor (add/delete row, add/delete column, delete all rows, clipboard copy/paste) — edits are overwritten on the next binding poll |
| Date | Value variant; frontend shows `YYYY-MM-dd HH:mm:ss` with a calendar-icon picker, backend stores a long integer |
| Color | Value variant; backend is a plain string, Designer renders a color swatch + picker |

**Large-number caveat**: JavaScript doubles safely represent integers only up to ±(2⁵³−1) ≈ ±9.007×10¹⁵. A Dataset Double/Long column value outside that range (whether edited in the Designer, arriving from a bound tag, or rendered by a component) can silently round to floating-point precision.

### Meta properties reference

Every component carries a `meta` category: `name` (used when path-referencing by name), `visible` (bool), `domId` (hidden by default; sets the rendered DOM `id`, intended for Selenium-style automated testing only), `tabIndex` (hidden by default; sets keyboard tab-focus order), plus two structured objects:

- **`meta.tooltip`**: `enabled`, `width` (px number or `"auto"`), `text` (supports multi-line via an expression concatenating `\n` plus `style: "white-space: pre"`), `style` (standard style object), `delay`/`sustain` (ms, `0` = immediate/indefinite), `location` (`mouse`, or `top/center/bottom` × `left/center/right`, constrained to stay in-viewport), `tail` (decorative pointer triangle, ignored when `location: mouse`). Trigger/dismiss from script with `self.requestTooltip()`/`self.removeTooltip()` — handy on mobile where there's no `onMouseEnter`.
- **`meta.contextMenu`**: `enabled`, `style`, `items[]` — each item has `text`, optional `icon` (`path`/`color`/`style`), `style`, and `type`: `submenu` (nests a `children` array of the same item shape), `link` (`url` + `target`, internal page URLs need the exact configured leading-slash Page URL), `method` (invokes a component Custom Method by `name` with a `params` object — no positional args), `message` (fires a component message handler: `type`/`payload`/`scope`), `separator` (visual divider only). Trigger/dismiss from script with `self.requestContextMenu()`/`self.removeContextMenu()`.

### Restricting and persisting properties — quick reference

Access levels (right-click property > **Access**): `Public` (default — browser JS can read/write), `Protected` (backend ignores JS write attempts; bindings/scripts still write normally), `Private` (also unreadable from JS), `System` (fully backend-managed, un-writable from anywhere but the platform, cannot be removed). This defends against a user opening devtools to script around your validation — it is not a general-purpose ACL, and Style Class *names* remain visible client-side regardless of access level. To write to a Private/Protected **session** prop from your own code, use a scripting action or a bidirectional property binding (the restriction only blocks *browser-originated* writes).

Persistence (right-click property > **Persistent**, shown with a Transient badge when off): properties save their value with the project by default. Attaching *any* binding to a property automatically flips it to non-persistent (its startup value is going to be overwritten by the binding anyway). A user-created property lacking the Persistent flag is discarded — not just its value, the property itself — when its view closes in the Designer or when a session launches, *unless* a binding is configured on it (which forces re-creation).

### Property Editor right-click reference

Right-clicking a property in the Perspective Property Editor exposes, by section:
- **Actions** — copy/paste/duplicate/delete the property itself.
- **Structure** — `Add Before`/`Add After` (insert a sibling before/after this element — only visible inside an Array or Object), `Insert`, and `Value` (retype the property as Value/Array/Object).
- **Binding** — `Configure Binding…`, `Copy Binding`/`Paste Binding` (clipboard-based binding reuse across properties — Paste only shows once something's been copied), `Disable Binding` (keeps the config but stops it firing), `Remove Binding`.
- **Options** — `Add Change Script` (see Property Change Scripts), `Persistent` toggle, `Access` (Public/Protected/Private — see below).

### Drop Configuration (`dropConfig`)

A **view-level** property (`dropConfig`) that wires up drag-and-drop tag→view binding automatically, letting a tag dropped from the Tag Browser instantiate a pre-configured embedded view with bindings already attached. Two mutually-listed approaches:

- **`dropConfig.udts`** — associates the view with a specific UDT definition. Each entry has: `type` (the UDT definition to match), `param` (name of a view parameter, typically an Object param, that receives the UDT's member values keyed by member name), `action` (`bind` creates a live Tag binding between the view param and the dropped UDT instance's members; `path` instead populates the param with the tag *path* string, for use in scripts/expressions rather than direct binding).
- **`dropConfig.dataTypes`** — associates the view with a plain tag data type (e.g., `Int4`) instead of a UDT; same `param`/`action` semantics, useful for building a single reusable "detail" view that any similarly-typed tag can be dropped onto.

Practical pattern: build a `Small_View` with an Object view param whose keys match your UDT's member names 1:1, set `dropConfig.udts[0] = {type: MyUDT, param: "UDT_Prop", action: "bind"}`, then dragging any instance of that UDT onto a `Big_View` prompts a popup listing associated views (`Small_View` among them) and, on selection, creates a fully-bound embedded instance automatically. This is distinct from — and layered on top of — the project-wide **Tag Drop** configuration (Project Properties > Perspective > Tag Drop), which governs what happens when a tag is dropped onto *empty space* (data-type → component-type → prop-binding mapping, with Bidirectional/Coalesce flags per mapping) rather than onto an existing dropConfig-aware view.

### Transforms

Transforms sit between a binding and the property, chained top-to-bottom (each transform's output feeds the next).

- **Map** — input→output lookup table. Input Type: `Value` (exact match), `Numeric Range` (`[x,y]` inclusive / `(x,y)` exclusive, brackets mixable, open-ended ranges allowed), `Expression`. Output Type: `Value`, `Color`, `Expression`, `Document` (hand-built JSON), `Style`, `Style Class`. First matching row (top-down) wins; **Fallback** row covers no-match. Classic use: tag-value → color/style-class for state indication.
- **Format** — string-formats the value (return type is always string). Numeric formats: Pattern (`0`/`#` mask), Integer, Number (locale-aware), Percent, Currency. Datetime formats: Pattern, Date/Time/Datetime with Full/Long/Medium/Short granularity, plus Locale and Time Zone (`auto` = session locale/timezone, or explicit).
- **Expression** — runs an expression against `{value}`, with the same Operators/Functions/Tag/Property helper buttons as an Expression binding. Common for a second manipulation step after an indirect Tag binding.
- **Script** — arbitrary Python. Args provided: `self` (the component), `value` (incoming value/prior transform output — already stripped of quality/timestamp), `quality`, `timestamp`. Must `return` a single value/dataset/document/etc.; the returned type overwrites the target property's data type. Complex properties referenced *inside* the script (not via the `value` arg) come back as Qualified Values and need `.value()`. Note: Tag History and Query bindings both offer a native **Value Format: Document** return option — prefer that over a script transform when it covers the need.

  Reference patterns (verbatim from the manual):

  ```python title="Dataset to Array of Objects (Table, etc.)"
  header = value.getColumnNames()
  newList = []
  for row in value:
      newDict = {}
      for i in range(len(row)):
          newDict[header[i]] = row[i]
      newList.append(newDict)
  return newList
  ```

  ```python title="Sparkline: Tag History dataset -> flat value list"
  newList = []
  for row in value:
      if row[1] is not None:
          newList.append(row[1])
  return newList
  ```

  ```python title="Timestamp -> Session-timezone-formatted string (Tag History props.data)"
  convertedTimestamps = []
  from java.text import SimpleDateFormat
  from java.util import TimeZone

  dateFormatIn = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS")
  dateFormatIn.setTimeZone(TimeZone.getTimeZone("UTC"))
  dateFormatOut = SimpleDateFormat("yyyy-MM-dd hh:mm:ss.SSS Z")
  dateFormatOut.setTimeZone(TimeZone.getTimeZone(self.session.props.timeZoneId))

  for row in range(value.getRowCount()):
      date = dateFormatIn.parse(str(value.getValueAt(row, 't_stamp').toInstant()))
      convertedTimestamps.append(str(dateFormatOut.format(date)))
  return system.dataset.addColumn(value, convertedTimestamps, 'formatted_timestamp', str)
  ```

### Time zones

Perspective sessions juggle Gateway TZ, session TZ, and browser TZ simultaneously. Two control points:
- **Project Properties > Perspective > General > Project Timezone**: `Gateway`, `Client` (browser TZ), `Specific` (fixed named zone), or a literal regional zone.
- **Session property `timeZoneId`** (e.g. `America/New_York`) — overrides Project Timezone for that session if set; bind it to a Dropdown to let users self-select.

Scoping gotcha: **scripting and Expression bindings execute in Gateway scope** in Perspective (there is no client scope), so a plain Expression `toDateString()` or script-formatted date defaults to the *Gateway's* time zone, not the browser's, unless you explicitly convert using `session.props.timeZoneId`. Components themselves (Label, Table date-render, XY Chart axis, Power Chart) generally default to the *browser's* time zone for their own built-in date rendering.

---

## Scripting in Perspective

### Fundamentals and scope rules

Perspective uses Jython, same as the rest of Ignition, but **there is no Client scope** — Perspective has no clients. All Perspective scripting executes **in the Gateway**, even when the effect (e.g., navigation) only touches one session. Consequences:
- `system.file`, `system.gui`, `system.nav` (Vision client-scope functions) **do not work** in Perspective.
- `system.util.getLogger()` and friends run in Gateway context.
- Any date/time formatting done in a script or Expression binding uses the **Gateway's** time zone unless you convert explicitly (see Time Zones above).

### self / this / the object model

`self` in a component script refers to the component the script is attached to. From `self` you can traverse:

| Property/Method | Returns |
|---|---|
| `.children` / `.getChildren()` | Child components |
| `.parent` / `.getParent()` | Parent container (root container → the view; view/session → `None`) |
| `.getChild('Name')` / `'Container/Name'` | Named descendant, `None` if absent |
| `.getSibling('Name')` | Shortcut for `self.parent.getChild('Name')` |
| `.view` / `.getView()` | The containing view |
| `.page` / `.getPage()` | The page object (`.close()` closes it, `.props.pageId`/`.props.path`) |
| `.session` / `.getSession()` | The current Session object |

Session object extras: `.close()` / `.close(message)`, `.getInfo()` (dict matching `system.perspective.getSessionInfo`), `.getPages()`, `.getPage(id)`, `.getProjectInfo()` (name/title/description/lastModified/lastModifiedBy/views/pageConfigs).

View object extras: `.rootContainer`, `.id` (e.g. `path/to/view@C`), `.session`.

**Object Traversal is scoped to a single view** and is brittle — renaming a component or moving it into a new container breaks any `getSibling`/`getChild` path that referenced it, and traversal cannot reach across view instances at all. For anything cross-view, or where the hierarchy might change, use **Component Message Handlers** instead.

### Component/session/message-handler object model, cont'd

**Built-in component methods**: `self.refreshBinding("props.data")` (manually re-fire a pollable binding — saves Gateway resources vs. tight polling, often combined with a message handler so one message refreshes several bindings at once), `self.focus()` (input components only), `self.requestTooltip()`/`self.removeTooltip()`, `self.requestContextMenu()`/`self.removeContextMenu()`, `self.requestPrint(target='component'|'view'|'page', documentTitle=...)`.

**Custom Methods**: define your own component method via **Configure Scripts > Custom Methods > Add method**, with a name and comma-separated parameter list (positional args only, `self` is implicit). Call as `self.myMethod(arg1, arg2)`.

**Extension Functions** are different from Event Handlers: no `event` object, `self` *is* the first argument (true instance methods), signature/docstring are fixed by the component. They're used to subclass built-in component behavior — e.g., Alarm Status Table's `filterAlarm` extension function decides per-event whether to display it.

### Component event scripts and Component Message Handlers

**Message handlers are the preferred cross-component/cross-view communication mechanism** (over Object Traversal). Two-part pattern:
1. Configure a Message Handler on the listening component (**Configure Scripts > Add handler**), give it a **Message Type** string (case-sensitive; multiple components can share one type so one broadcast fans out to many).
2. Elsewhere, call `system.perspective.sendMessage(messageType, payload={...}, scope='view'|'page'|'session')`.

Scope table:

| Scope | Reach |
|---|---|
| `view` | Listeners in the same View only |
| `page` | Listeners in the same Page (all Views on it, including docked/popup) |
| `session` | Listeners in **any** open tab of the session |

Messages execute **asynchronously, on a separate thread** — the sending script does not block on the handler, and there is no guaranteed ordering between the sender's remaining lines and the handler's execution. Payload is a Python dict, unpacked as `payload['key']` in the handler.

**Session-scope Message event scripts** (Project Browser > Perspective > Session Events > Message) are a *different* mechanism: they respond to `system.util.sendMessage`/`sendRequest` (platform-wide messaging, not `system.perspective.sendMessage`), and cannot be targeted by `system.perspective.sendMessage`.

### Property Change Scripts

Attach directly to any component property (right-click > **Add Change Script**). Args: `self` (component, or the session object if attached to a session property), `previousValue`/`currentValue` (QualifiedValue: `.value`, `.quality`, `.timestamp`), `origin` (string — `Browser`, `Binding`, `BindingWriteback`, `Script`, `Delegate`, `Session`, `Project`), `missedEvents` (bool — some updates were coalesced/dropped due to overflow). Prefer an Expression binding over a change script when possible — lighter on session performance.

### Session event scripts — Gateway vs. session execution

Two categories, both configured under Project Browser > **Perspective**:

**Gateway Event Scripts** — centralized, not tied to a live session context, support Offline Mode workflows (e.g. a form submitted while disconnected, queued and replayed later). Currently: **Form Submission** — args `session`, `name`, `data` (dict of field values), `formContext`, `sessionContext` (timestamp/user/device/location), `retry` (bool, resubmission after failure); the script must return a dict shaped like `{"success": bool, "title": ..., "message": ..., "fieldErrors": {...}}`.

**Session Event Scripts** — tied to an individual session, run in Gateway scope:

| Event | Fires when | Key args |
|---|---|---|
| Startup | Session starts | `session` |
| Shutdown | Session ends (timeout, deauth, redundancy failover, licensing loss, project deleted/unrunnable) | `session` |
| Page Startup | A page opens in a *new* tab/window (not on navigating to an already-open page, e.g. via `system.perspective.navigate`) | `page` |
| Authentication Challenge | An Authentication Challenge Action completes | `session`, `payload`, `result` (`.isSuccess()`/`.getAsSuccess()` → `WebAuthUserContext`; `.isError()`/`.getAsError()` → generic/timeout/cancelled) |
| Message | `system.util.sendMessage`/`sendRequest` targets this session | `session`, `payload` |
| Keystroke | KeyboardEvent matches a configured single-key or regex pattern (works with HID barcode scanners that emit KeyboardEvents) | `page`, `event` (key/code/modifiers/`matches` for regex capture groups) |
| Barcode (Perspective App) | Scan Barcode Action completes on a mobile device | `session`, `data` (`.text`, `.timestamp`, `.barcodeType`), `context` |
| Bluetooth (Perspective App) | Beacon advertising data received (iBeacon/Eddystone) | `session`, `data` (list of advertising packets) |
| Accelerometer (Perspective App) | Batched Accelerometer Action completes | `session`, `data.values.data` (rows with x/y/z), `context` |
| NFC (Perspective App) | Scan Ndef NFC Action reads a tag | `session`, `data` (list of NDEF records: type/typeNameFormat/payload/string/bytes), `context` |

Barcode/Bluetooth/Accelerometer/NFC are **Perspective App-only actions** — silently ignored in an ordinary browser session.

### Component Events and Actions reference

Configured via right-click a component > **Configure Events**. An **Event** (mouse click, key press, `onStartup`, etc. — full catalog in the Gotchas/appendix note below) can have any number of **Actions** attached, executed top-to-bottom in list order but **not synchronously** — a slow Action does not block a faster one queued after it. Every action shares: **Enabled**, **Prevent Default** (suppress the browser's native behavior, e.g. its own right-click menu), **Stop Propagation** (block the event from also triggering handlers higher in the component hierarchy), **Security Settings** (gate the action on required security levels, independent of any binding-based visual indicator — see Security section).

| Action | Purpose / key settings |
|---|---|
| Accelerometer | Perspective-App-only. `Continuous` (streams into `session.props.device.accelerometer` at a Sample Rate) / `Batch` (records for a Duration at a Sample Rate, then delivers to the `Accelerometer` session event) / `Off`. Optional `Context` object passed through to the session event. |
| Alter Logging | Change a session's browser-side log verbosity and optionally forward it to Gateway logs (`Remote Logging Enabled` + matching Perspective.Client logger level Gateway-side). |
| Alter Dock | Reconfigures an *existing* docked view's settings at runtime (View, Display, Resizable?, Modal?, Content, Anchor, Size, Auto Breakpoint, Dock ID, Handle, Handle Icon, View Parameters) — blank fields are left unchanged. |
| Dock | `Open`/`Close`/`Toggle` a docked view by its **Dock ID**, optionally passing `Parameters` matching the docked view's params. |
| Fullscreen | `Enter`/`Exit`/`Toggle`, targeting the whole session, a `View`, or a `Page`. Must originate from a genuine user interaction (browser restriction); not all browsers support it. |
| Login / Logout | Log the current user in/out. `Ask the IdP to re-authenticate users`: `Project` (use Project Properties default) / `Enable` (always prompt) / `Disable` (skip if already logged in). |
| Authentication Challenge | Navigates the user to an IdP to authenticate a *second* identity without disturbing the current session's own login (e-signature pattern). Settings: `Identity Provider` (defaults to project IdP if unset), re-auth mode, `Timeout` (minutes, 0 → default 2), `Payload` (opaque data forwarded to the completion event), `Framing` (`Same Tab/Window`, `New Tab/Window`, `Embedded Frame` — Workstation sessions fall back to Same Tab; mobile only supports Same Tab). |
| Navigation | `Page` (Set Page URL, Open in new tab), `View` (replace the current primary View + Parameters), `Url` (external address, Open in new tab), `Browser` (forward/back through browser history). |
| Request Print | Print `Page`/`View`/`Component` contents; `Document Title` sets the saved-file name. |
| Popup | `Open`/`Close`/`Toggle` a view as a popup: `Select View`, `Parameters`, `Identifier` (needed to later Close/Toggle it from elsewhere), `Title`, `Show close button`, `Draggable`, `Resizable`, `Modal`, `Background dismissible` (modal-only), `Position Exact` (Top/Left/Bottom/Right offsets + Width/Height) or `Position Relative` (anchored to the mouse cursor on a Mouse Event), `Viewport Bound` (keeps/shifts the popup within the visible viewport and blocks off-screen dragging). |
| Refresh | Reloads the current browser tab. No settings beyond the shared ones. |
| Scan Barcode | Perspective-App-only. `Barcode Type` (or `Any`), `Barcode Background Color` (`Light`/`Dark`/`Auto`), optional `Context` — result delivered to the `Barcode` session event. |
| Scan Ndef NFC | Perspective-App-only. `Single` (one scan) / `Continuous` (keep listening) / `Off` — results delivered to the `NFC` session event. |
| Script | Arbitrary Python; gets a built-in `event` object describing the trigger (properties vary by event class — see the Event Types reference below). |
| Theme | `Select Theme` — sets `session.props.theme` from a dropdown of available themes. |
| Workstation Mode | Only meaningful inside a Perspective Workstation session. `Windowed` / `Kiosk` / `Toggle`. |

### `system.perspective.*` scope rules

- Navigation/session-state functions (`system.perspective.navigate`, `openPopup`, `togglePopup`, `closeSession`, `closePage`, `sendMessage`, `getSessionInfo`, `workstation.*`) execute against a specific session context but the *script itself* still runs Gateway-side.
- `system.perspective.sendMessage` is component-message-handler scoped; it is distinct from `system.util.sendMessage` which targets Session Event "Message" scripts.
- There is no `system.gui`/`system.nav`/`system.file` in Perspective — those are Vision client-scope only.

### Event types reference (`event` object by class)

For a Script Action, the `event` parameter's shape depends on the event's class (full per-component event catalog is in `appendix/reference-pages/perspective-event-types-reference`):

| Class | Events | Notable `event.*` properties |
|---|---|---|
| System | `onStartup` (component/view mounted), `onShutdown` (component/view unmounted, or session closed via logout/timeout) | none (no special properties) |
| Mouse | `onClick`, `onContextMenu`, `onDoubleClick`, `onMouseDown`/`Up`, `onMouseEnter`/`Leave`/`Move`/`Over`/`Out` | `altKey`/`ctrlKey`/`shiftKey`/`metaKey`, `button`/`buttons` (bitmask), `clientX/Y`, `pageX/Y`, `screenX/Y`, `relatedTarget`, `getModifierState(key)`. Note: `onClick` still fires on a *disabled* component — use `onActionPerformed` or check enabled state in-script if that's not wanted. |
| Pointer | `onPointerOver`/`Enter`/`Out`/`Leave`/`Up`/`Down`/`Cancel`/`Move` (unifies touch/pen/mouse; may not fire on older Safari/Firefox) | `height`/`width` (contact geometry), `isPrimary`, `pointerId`, `pointerType`, `pressure`, `tangentialPressure`, `tiltX`/`tiltY`, `twist` |
| Keyboard | `onKeyDown`, `onKeyUp`, `onKeyPress` (deprecated, prefer `onKeyDown`) | `key`, `code`/`keyCode` (deprecated), `location`, `repeat`, `altKey`/`ctrlKey`/`shiftKey`/`metaKey`, `getModifierState(key)`, `which` (deprecated) |
| Text Composition | `onCompositionStart`/`Update`/`End` (IME/voice-to-text input) | none special |
| Focus | `onFocus`, `onBlur` | none special |
| Selection | `onSelect` (text selected inside the element) | none special |
| Touch | `onTouchStart`/`Move`/`End`/`Cancel` | `altKey`/`ctrlKey`/`shiftKey`/`metaKey` |
| Wheel | `onWheel` | `deltaMode` (0 px/1 line/2 page), `deltaX`, `deltaY` (most common — positive = scroll down), `deltaZ` |
| Component (Action Performed) | `onActionPerformed` — fires on the component's "primary action" (button press, checkbox toggle, dropdown selection, etc.) across Date/Time Input & Picker, Barcode Scanner Input, Button, Checkbox, Dropdown, Multi-State Button, Numeric Entry Field, One-Shot Button, Radio Group, Slider, Toggle Switch | none special beyond the base event |

`onClick` vs `onActionPerformed`: prefer `onActionPerformed` for anything that should respect a component's own enabled/disabled state, since `onClick` fires regardless.

### Quick-reference scripting snippets

```python title="Send a scoped message with a payload"
system.perspective.sendMessage('my-handler', payload={'time': system.date.format(system.date.now(), 'HH:mm:ss')}, scope='view')
```

```python title="Message handler receiving the payload (configured on the listening component)"
self.props.text = payload['time']
```

```python title="Define + call a Custom Method"
# Custom Method body (configured via Configure Scripts > Custom Methods):
self.props.text = myParam1
self.custom.myProp = myParam2
# Calling it from elsewhere on the same component:
self.myMethod("Hi!", "This is a test")
```

```python title="Manually pulse a pollable binding (Tag History / Query) from a message handler"
self.refreshBinding("props.data")
```

```python title="Object Traversal from a deeply-nested Button (fragile — prefer Message Handlers if the hierarchy may change)"
text3 = self.parent.getSibling('Text Field 3').props.text
text4 = self.getSibling('Text Field 4').props.text
```

### Gateway vs. session execution — practical summary

Everything (bindings' server side, transforms, event scripts, message handlers) runs on the **Gateway**. "Session" in Perspective means *which browser tab's UI state is affected*, not *where the code executes*. This has two big practical effects: (1) date/time defaults to Gateway TZ unless converted, (2) heavy per-session scripting multiplies Gateway CPU load across every connected session — prefer bindings/expressions and shared polling (Cache & Share) over scripted polling loops.

---

## Styling and theming

### Style properties

Every styleable component/property exposes a `style` object plus a **Styles** editor icon in the Property Editor, covering: **Text** (font family/size/color/weight/italic/line-height/letter+word spacing, alignment, transform, decoration, shadow, overflow-wrap, text-overflow), **Background** (color, image, position, clip/repeat/attachment/size, box-shadow), **Margin and Padding** (per-side), **Border** (linked or per-side style/width/color/radius, outline style), **Shape** (fill/stroke/stroke-width for SVG-based components), **Misc** (opacity, cursor, overflow/overflow-x/overflow-y). All CSS length units are supported; a bare number is assumed px (`35pt` etc. also valid). Full property tables: `appendix/reference-pages/style-reference`.

Precedence, most-specific wins: **inline style on the component** > **Style Class(es) applied to the component** (multiple classes apply in alphabetical order — a later-alphabet class's set properties override an earlier one's, but unset properties fall through) > **theme defaults**.

### Style classes

A reusable named bundle of style rules, stored under the project's `Styles` folder (foldered like views). Created via right-click **Styles > New Style**; the `ia_` name prefix is reserved for built-in styling and must not be used for custom classes. Deleting a class reverts affected components to default + any inline overrides (inline stays). Renaming a class **breaks the reference** on every component using it — must be reapplied. Classes can be **Protected** to lock them from further edits without unprotect permission.

Two power features on a Style Class:
- **Element States** — CSS-pseudo-class-driven conditional styling (`hover`, `active`, `focus`, `disabled`, `checked`, `enabled`, `first-child`, `last-child`, `invalid`, `valid`, `required`, `read-only`, `read-write`, `in-range`/`out-of-range`, `empty`, `visited`, `link`, `fullscreen`, `default-choice`, `only-child`), each independently Animate-able.
- **Media Query** — style rules gated on `min-width`/`max-width` (px), `orientation` (portrait/landscape), `min-aspect-ratio`/`max-aspect-ratio`, `hover` capability. This is how Style Classes participate in responsive design without touching layout containers.

**Animated Style Classes**: set `Animated: true` to get Duration/Direction/Iterations/Timing/Delay/FillMode plus 0%–100% keyframe stops, each with its own style settings — the standard mechanism for a "flashing alarm" indicator. Typically combined with a Tag binding + Map transform on `style.classes` to add/remove the animated class conditionally (input `true`→ output type `Style Class` → the animated class name; no matching row → class stays off).

**Bindings on Style Classes**: `style.classes` itself is bindable (directly, or via Map transform), letting a component switch its whole class set based on a tag/expression at runtime.

**Advanced Stylesheet** (right-click Styles folder > **Enable Advanced Stylesheet**) exposes a project-scoped `stylesheet.css` for raw CSS overrides. Style Classes are injected with a `.psc-` prefix (target `.psc-yourClassName` in raw CSS, but keep entering the plain name in the Property Editor); built-in component classes use the `.ia_` prefix. This resource sits between theme CSS and project Style Classes in cascade order, and is project-scoped (unlike Theme files, which are Gateway-scoped).

### Themes

Built-in themes, all shipped: **light**, **dark** (bases — system config resources, cannot be edited directly); **light-cool**, **light-warm**, **dark-cool**, **dark-warm** (derived — freely editable, but edits are silently reset on upgrade, so prefer authoring a genuinely custom theme instead). Active theme = the session property `session.props.theme` (writable at runtime — bind a Dropdown bidirectionally to `session.props.theme` to build a live theme switcher, or use the **Theme Action** on an event).

Overriding the base `light`/`dark` themes specifically requires creating an `overrides-light`/`overrides-dark` theme resource whose `index.css` `@import`s the base theme and layers custom rules on top; set `isPrivate: true` on that override resource so it doesn't show up as a selectable theme itself.

**CSS variables** are the backbone of theme authoring — colors are centralized in a `variables.css` per theme (`--neutral-10`…`--neutral-90`, sequence colors, etc.); reference them from Style Classes with `var(--variable-name)`, and from a component's plain style property by typing the variable name directly.

**Custom theme structure**: a folder under `.../resources/core/com.inductiveautomation.perspective/themes/<name>/` containing `config.json` (sets `entrypoint`, default `index.css`, and `isPrivate` to hide it from the theme picker), `resource.json`, and the CSS entrypoint. Create via the Gateway's OpenAPI resource endpoints, or directly on the file system followed by **Scan File System** on the Gateway's Platform Overview page (or a full restart) to pick up changes. Selecting a new theme in Session Props only takes effect after a **Gateway restart**.

**Descriptive CSS class naming convention** used throughout the built-in themes: ABEM — `atomicPrefix_blockName__elementName--modifierName` (e.g. `ia_cylindricalTankComponent__liquid--animation`) — useful when reverse-engineering which selector to target in the Advanced Stylesheet.

### Responsive/breakpoint design

Three complementary responsive tools:
1. **Breakpoint Container** — swaps between entirely different child views based on session width (classic pattern: `HeaderLarge`/`HeaderSmall` embedded views inside a Breakpoint parent).
2. **Media Query on a Style Class** — same style class, different rules at different widths/orientations (font-size scaling, hiding decorative elements, etc.) — see Style Classes above.
3. **Docked view Auto display + Auto Breakpoint** — collapses a docked nav drawer below a given page width and exposes a handle/toggle instead (the canonical "self-hiding navigation drawer" pattern: a `MenuTree` in its own view, docked Left with `Display: auto`, `Auto Breakpoint` matching a Breakpoint container elsewhere, and a `Dock` action wired to a menu icon).

Design guidance (from the manual's Design Tips page): minimum touch target 25px, optimal 40px, minimum 10px spacing between interactive elements; put primary actions in the device's "thumb zone" (lower-center); favor mobile-first design (smaller screens force prioritization and yield one consistent data model across form factors); avoid over-cluttering — fewer, clearer elements read better at every size.

### Flex vs. Coordinate container trade-off

- **Coordinate Container** — explicit X/Y/width/height per child (optionally `Percent` mode for relative positioning); the closest analog to a Vision window with top/left-anchored components. Fast to build with, poor at reflowing for different screen sizes without a lot of manual re-authoring. Also the *only* container that supports drawn **Pipes** (P&ID-style flow visualizations) and rotation handles/component anchors.
- **Flex Container** — CSS-flexbox row/column layout; children grow/shrink/wrap based on flex rules rather than fixed coordinates. Naturally responsive, harder to eyeball pixel-perfect placement. Common pattern: a Flex container with a fixed-height header and a Coordinate (or another Flex) container filling the remainder, echoing a Vision "anchored header + relative body" window.
- Other container types (Breakpoint, Split, Tab, Accordion, Column) exist for specific responsive/navigation needs but the fundamental trade-off is: Coordinate = precise but static; Flex = fluid but less precisely controllable.

### Symbol visual states (Perspective Symbols palette)

Project Properties > Perspective > Symbols governs the built-in and custom visual **states** available to the Perspective Symbols component palette (Motor, Valve, Pump-style P&ID symbols). Each state has light/dark sub-styles configurable under **Edit State Style**: `Primary Color` (fill), `Secondary Color` (alternate fill, used when `Enable Flashing`), `Tertiary Color` (vessel fill), `Stroke Color` (outline), `Enable Animation`, `Enable Flashing` (alternates Primary/Secondary). States are managed with Add (blank new state), Duplicate (clone an existing state's config, still fully editable regardless of origin), and Delete (custom states only — built-ins can be edited but not deleted); Undo/Reset-Theme icons revert to last-saved / original config. A state's `Available Symbols`/`Applied Symbols` lists (moved with arrow buttons) control which symbol components can select that state at design time. Once applied, set a placed symbol's `state` property from `default` to the custom state name to activate it immediately in the Designer.

### Perspective Pipes (Coordinate-container-only)

Pipes draw P&ID-style flow lines directly on a **Coordinate Container** — the Pipe Draw/Move tools disable themselves on any other container type. Terminology: a **Pipe** = origin + connections + segments, listed as its own entry in the Project Browser under Pipes; a **Pipe Connection** = an XY point (circle; the origin connection additionally shows a center dot); a **Pipe Segment** = the line between a connection and one immediate child, addressable by an index path like `[0,1,0]`. Pipes always render at the back of the z-order, so components added afterward sit visually on top.

Editing: click the Pipe Draw Tool, then click inside the container to start an origin; drag from a connection's arrow handles to grow new segments (Alt/Option = snap to 15° increments, Shift = free placement); drag a new connection onto an existing segment to split it; select a connection + Delete to remove a segment; drag one pipe onto another to combine their appearance (Ctrl/Cmd-Z immediately after undoes the combine without undoing the drag, letting pipes overlap without merging). Symbol-type components expose custom anchor points that segments snap to while drawing (visual guide only — the pipe is not actually bound to the component, so moving the component later does not move the pipe).

Per-pipe-set properties: `Pipe Name`, `Appearance` (`Simple`/`Mimic`/`P&ID`, or `auto` → follows `session.props.pipes.autoAppearance`), `Width`, `Fill Color`/`Stroke Color` (Simple/Mimic only), `Display flanges` (Mimic only), `Line Variation`/`Line Color`/`Start`/`End` (P&ID only), `Visible`. `session.props.pipes.overlapGap` (default 4) sets the visual gap drawn where pipes cross; 0 or negative disables overlap rendering, which can help render performance on pipe-heavy views.

### Images and icons

Supported formats: PNG, JPG, JPEG, GIF, SVG, all rendered through the **Image** component's `source` property or, for icons specifically, the **Icon** component / `icon` props on select components (Horizontal Menu, Map, Accordion). Three ways to supply an image: (1) upload/reference via the **Image Management** tool — reference path is `/system/images/<path>` prepended manually onto whatever Copy Path gives you; (2) drag a local file onto a view and choose **Save and link** (goes into Image Management for reuse) or **Embed image** (inlined into the property — files over 100KB trigger a warning to use link instead, since embedding degrades performance); (3) paste an external web address directly into `source`.

Built-in icon libraries: `material` (Google Material Symbols & Icons — the bulk of shipped icons), `ignition`, `sample-component`. Icon paths look like `material/location_on`. **Custom icon repositories**: an SVG file at `.../resources/core/com.inductiveautomation.perspective/icons/<name>.svg` where each icon is a nested `<svg viewBox="0 0 24 24" id="icon-name">...</svg>`, paired with a `config.json` (`{"svgFileName": "example.svg"}`) and `resource.json` (scope/version/files list) in the same directory — requires a Designer (and ideally Gateway **Scan File System**) restart to pick up.

**Bypassing browser cache**: components that wrap an embedded Chromium instance (e.g., Inline Frame) are subject to the ordinary HTTP cache — replacing a file at the same URL server-side won't refresh what's shown until the cache is bypassed. Fix with a cache-busting Expression binding on `src`: `'http://YOURURL?timestamp=$' + floor(toMillis(now())*0.00001)` (tune the `0.00001` divisor to control refresh cadence).

**Convert to Drawing**: right-clicking most SVG-based Perspective components (e.g., Cylindrical Tank) offers **Convert to Drawing**, which replaces the component's normal typed props (`value`, `capacity`, `liquidColor`, etc.) with raw drawing props (`viewBox`, `preserveAspectRatio`, `elements`) for direct SVG-level editing — a one-way trade of the component's built-in behavior for full visual control.

### Localization

Built on Ignition's platform-wide **Translation** system (translation lists mapping a key string to per-locale translations). A session's active language is the `locale` session property (default `"en-US"`); switching it re-renders any text that matches a defined translation key. Locale also affects number/date formatting on components like Numeric Entry Field and Power Chart. Standard pattern for an in-session language switcher: a Dropdown with `options` value/label pairs per locale tag (e.g. `es-US`/`Español`, `en-US`/`English`), bidirectionally bound to `session.props.locale`.

---

## Security in Perspective

### IdP login flow

Security is anchored on an **Identity Provider (IdP)**, configured Gateway-side, then wired to a project via **Project Properties > Project > General > Identity Provider**. IdP types include Ignition's internal user source plus federated options (SAML, OAuth/OIDC, etc. — configured elsewhere in the Security section of the manual). No additional Perspective-level security (view permissions, session permissions) can be applied until a project has an IdP selected.

### `isAuthorized` and security levels

**Security Levels** (Ignition 8+ concept, replacing/extending Roles) form a hierarchy — a user granted a more specific level ("Operator / LineB") automatically also has the more general parent level ("Operator"). Three places security levels get enforced in Perspective:

1. **Perspective Session security** — Project Properties > Perspective > Permissions: check the security levels allowed to open the session at all. Choose **All** (must match every checked level) or **Any** (at least one).
2. **Perspective View security** — right-click a view > **Configure View Permissions**: same All/Any semantics, scoped to gating a single view.
3. **Event Action security** — any component action's **Security Settings** panel: gates whether that specific action fires for the current user.

`isAuthorized(...)` is an **expression function** used in bindings to *visually* reflect authorization state (e.g., disabling a button for unauthorized users), independent of and in addition to the Gateway-enforced action security:

```python
isAuthorized(false, "Authenticated/Roles/YourRoleGoesHere")
```

Bound to a component's `enabled` prop, this also incidentally blocks the `onClick`/`onActionPerformed` event from firing for a disabled component. An alternative pattern reads `session.props.auth.user.roles` via a Property binding + Script Transform (`return "Administrator" in str(value)`). **Both approaches are visual indicators only** — they do not themselves enforce security; the actual enforcement is the Gateway-side Security Settings on the action/view/session.

**Deleted security levels**: if a level referenced by a project's permission config is later deleted Gateway-side, the Designer shows it grayed-out with a red warning underline (dotted underline on ancestor levels) and a count badge, in Project Properties > Perspective > Permissions, the Event Configuration screen, Edit Permissions, and the Tag Editor. Warnings clear once the stale level is unchecked and settings resaved.

### Inactivity timeout

Project Properties > Perspective > Inactivity provides a separate, session-only auto-logout/close mechanism, distinct from the plain Session Timeout: `Enabled`, `Inactivity Timer` (minutes of no clicking/typing/tapping/swiping before triggering, max 2,147,483,647), `Grace Period` (seconds of warning before the action fires), `Grace Period Message` (supports a `{seconds}` placeholder), `Inactive Session Action` (`Logout` or `Close Session`). The Gateway is the timekeeper (not the browser), so this is resistant to clock manipulation on the client. Note that either action only affects the *Perspective session* — the user stays logged into the IdP itself, so pair this with **Always ask the IdP to re-authenticate users by default** (a separate Project Properties setting) if the intent is to force fresh credentials, not just a fresh session.

### Session props for the authenticated user

Under `session.props.auth`:

| Property | Contents |
|---|---|
| `authenticated` | `true`/`false`/`null` (unknown) |
| `user.id` / `userName` / `firstName` / `lastName` / `email` / `roles` / `timestamp` | Identity attributes from the IdP; null if not authenticated or IdP didn't supply the attribute |
| `securityLevels` | Array of `{name, children}` — deepest granted levels under the (always-implicit) Public level |
| `idp` | Name of the project's configured IdP |
| `idpAttributes` | Raw JSON from the IdP after login (e.g. `.authnResponse` holds the SAML Response XML for SAML IdPs); always empty in the Designer, which doesn't authenticate against real IdPs — use the Test Login IdP page to inspect the real shape |

**Login/Logout Actions** and the **Authentication Challenge Action** are the scripted/declarative ways to drive re-authentication: Ask-IdP-to-reauthenticate can be forced per-action (`Enable`/`Disable`/`Project`-default). The Authentication Challenge Action is specifically for "secondary user" e-signature-style workflows — it authenticates a *different* user without logging out the current session user, delivering the result to the `Authentication Challenge` session event script (`result.isSuccess()`/`getAsSuccess().getContext()` → `user`/`roles`/`securityLevels`, or `result.isError()` → generic/timeout/cancelled variants).

---

## Perspective Workstation and mobile

### Workstation mode, kiosk

**Perspective Workstation** is a dedicated desktop launcher/wrapper (built on JxBrowser) for running Perspective as a standalone desktop app on HMIs/panel PCs — not a browser tab. Requires Ignition 8.1+ Gateway. Two launch modes, both switchable at runtime via the **Workstation Mode Action** (`Windowed`/`Kiosk`/`Toggle`) or `system.perspective.workstation.*` scripting:
- **Windowed** — normal desktop window.
- **Kiosk** — full-screen, restricts OS access, minimizes distraction — designed for locked-down HMI terminals.

**Multi-monitor**: one Workstation application can open one OS window per display, each independently assigned a Page URL (Page Configuration tab, default Display 1 = `/`), with one display marked **Primary Display** for login/auth dialogs; an **Identify Displays** overlay helps match display numbers to physical monitors.

**Tab/Window Links** setting controls what happens to links that would normally spawn a browser tab: `Blocked`, `In Window` (stays inside Workstation), or `System Browser`.

**Redundancy/fallback**: Workstation supports redundant Gateway pairs — if the master is unreachable at startup it tries the backup, alternating until one connects. Independently, **Advanced Fallback Redirect** settings (Connect Timeout, Retries, Fallback Redirect enabled, Fallback Application, Auto-Return, Launch Delay — default 30s) let a *running* application redirect itself to a different configured application after an extended outage, and optionally auto-return once the original Gateway is reachable again.

**Command-line launch**: `perspectiveworkstation.exe application=<name> [debugPort=<n>] [launch.mode=WINDOWED|KIOSK] [browser.tab.mode=BLOCKED|IN_WINDOW|SYSTEM] [config.json=<path>] [devTools]`. `debugPort`/`devTools` both require `application=` to also be set. System requirements: 64-bit only (no ARM); macOS build targets Apple Silicon (a separate Intel build is available from Downloads).

### Native app features (camera/barcode/GPS)

The **Ignition Perspective mobile app** (iOS/Android) is the native launcher that, unlike a plain mobile browser session, exposes device hardware to Perspective via dedicated **Perspective App Actions**, each paired with a Session Event script that receives the resulting data (see the Scripting section's event table for full parameter details):

- **Scan Barcode Action** → `Barcode` session event (`data.text`, `.timestamp`, `.barcodeType`).
- **Scan Ndef NFC Action** → `NFC` session event (list of NDEF records).
- **Accelerometer Action** (Continuous or Batch mode) → `Accelerometer` session event (x/y/z rows) or continuously updates `session.props.device.accelerometer`.
- **Bluetooth** — enable via `session.props.bluetooth.enabled` + `.options` (`updateInterval`, `limit`, `filter` for iBeacon/Eddystone/AltBeacon) → data streams to `session.props.bluetooth.data` and the `Bluetooth` session event.
- **Geolocation** — `session.props.geolocation.enabled`, `.options.accuracy` (`max`/`balanced`/`low`), populates `session.props.geolocation.data` (lat/long/altitude/accuracy/heading/speed/timestamp) once `permissionGranted`.

All four "Perspective App" actions are **silently ignored** if the session is running in an ordinary browser rather than the native app.

**Managed configuration (MDM/EMM)**: the app can be pre-provisioned by enterprise mobility management tooling — `auto_launch` (`.auto_launch_url`, `.auto_launch_locked`, `.prevent_exit`), `hide_demo`, `initial_applications` (`project_url`, `alias`, `is_favorite`), `initial_gateways` (`gateway_url`). Android pulls these from the APK via the EMM console; iOS needs a sample PLIST supplied to the EMM.

**Deep links / project shortcuts**: `perspective://host:port/project` or `http(s)://host:port/data/perspective/client/project` URL forms let a shortcut or MDM auto-launch directly into a project. On Android, users can create Home-screen shortcuts (Perspective app > project's **⋮ > Create Shortcut**); iOS has no shortcut creation but supports Long-Press-to-select from the app icon.

### Offline behavior

**Offline Mode** (Project Properties > Perspective > Offline Mode) is mobile-app-only — **not supported in desktop browsers**. When enabled, the app caches visited views, supported components, auth tokens, themes, and localization assets locally so a project can (a) keep running through a temporary disconnection and (b) be *launched* with no Gateway connection at all.

Settings: **Enabled**, **Security Levels** (which users may use Offline Mode, All/Any), **Authentication Token Expiration** (days a cached auth token remains valid offline; default 7) + **Always ask IdP to re-authenticate** (forces fresh login every time the app reconnects online), **Themes** (which themes to bundle offline — unselected themes are unavailable if chosen while offline), **Languages** (which localization assets to bundle).

While offline:
- Realtime data (tags, alarms, queries) freezes — no updates until reconnect.
- Scripts needing Gateway/DB access don't run.
- Views never previously visited online aren't available.
- The **Form** component specifically queues submissions locally and replays them once reconnected (ordering across a reconnect is not guaranteed — timestamp your data if order matters). Other components' local event scripts (`onClick`, `onChange`, etc.) keep working normally.
- A project opened online but with Offline Mode *not* enabled will keep running if disconnection happens mid-session, but cannot be *relaunched* offline, and form submissions will fail outright instead of queuing.

---

## Performance and design guidance

### View embedding vs. templates

Perspective has no separate "template" concept — a View serves double duty as a top-level screen and as a reusable, parameterized unit (the "template" role) via the **Embedded View** component or a **Flex Repeater**. Practical guidance:

- Prefer **Embedded View + view params** over duplicating a layout across many views — a shared source view means one place to fix bugs/update styling.
- `useDefaultViewWidth`/`useDefaultViewHeight` on the Embedded View component control whether the embed keeps its source's authored size (with scrollbars if it doesn't fit) or stretches to the embedding slot — unchecking these is the usual fix for unwanted embedded scrollbars.
- If an Embedded View's `path` property is itself bound (e.g., swapping which sub-view shows based on a tag), the property defaults to non-persistent and will flash empty→loaded on every view open; configuring the `path` property as **Persistent** with a sane default path avoids the flash.
- A single view definition can simultaneously be instantiated as a stand-alone view *and* many embedded instances in the same session (e.g., a tank detail view used both by a Flex Repeater grid and by a popup for one specific tank) — this is expected and doesn't require special handling.

### Avoiding over-bound props

- **Bidirectional + Coalesce**: turn on Coalesce whenever a bidirectional binding targets a complex (object/array) property whose children can change independently — otherwise every child change triggers its own separate write-back round trip.
- **Cache & Share** on Tag History/Query/HTTP/MongoDB bindings de-duplicates identical polling work across every connected session — always worth enabling when many sessions will bind to the same slow/expensive source (a shared Named Query, a slow external API, etc.). Cache TTL tracks the configured poll rate (250ms default if polling is off).
- Prefer an **Expression binding** over a **Property Change Script** for simple derived values — change scripts carry more session overhead per the manual's own guidance.
- Prefer `refreshBinding()` calls (manually pulse a pollable binding on demand, often from a message handler) over tight scripted polling loops, to avoid needlessly hammering the Gateway.

### Table/chart performance

- Tag History bindings: **AsStored**/`PointCount = -1` returns every stored point as-is — fine for small windows, potentially very large for wide historical ranges; prefer `Periodic`/bounded `PointCount` for chart-friendly downsampling.
- Historical (fixed Start/End) Tag History ranges are *inclusive of the End Date* — chaining adjoining historical queries (e.g., two back-to-back hour windows) can double-count the boundary interval; trim the End Date by one interval to avoid overlap.
- Script Transforms that reshape a Tag History/Query dataset into an array of objects (for Table/XY Chart/Dropdown consumption) are common but add per-refresh scripting cost; where the binding supports a native **Value Format: Document/JSON** return type, prefer that over a script transform.
- Large numeric values in Dataset properties are subject to JavaScript's IEEE-754 double-precision limits (~±9×10^15) — values outside that range can silently round when they pass through a Perspective Dataset property (Double/Long columns), including values coming from a bound tag.

### Message handler patterns

- Keep message **Types** unique per intended-single-listener use case, or intentionally reused when you want one broadcast to fan out to multiple listeners (e.g., a shared `"reset"` type on several input components).
- Scope messages as tightly as the use case allows (`view` < `page` < `session`) — a `session`-scoped message is heard in every open tab, which is rarely what you want for view-local coordination.
- Never assume message-handler execution order relative to the sending script, or relative to other handlers — messages are asynchronous and unordered by design.
- Avoid writing transient cross-session-communication data into **Tags** — tag values are shared Gateway-wide across every session, so multiple sessions racing to write "their" value will stomp on each other. Use session properties, message payloads, or (for cross-session data) a proper database/named query instead.

### Common causes of slow sessions

- Heavy scripted polling instead of bindings, or bindings without Cache & Share where many sessions share a source.
- Over-broad message scopes (`session`-scope spam) triggering unnecessary handler execution across every open tab.
- Deep, tightly-coupled Object Traversal chains that force rebinding/rewriting whenever the view hierarchy shifts (fragile *and* a sign that Message Handlers should have been used).
- Large embedded historical datasets rendered without downsampling.
- Property Change Scripts used where a simple Expression binding would suffice.
- Non-Coalesced bidirectional bindings on complex properties causing write storms.

---

## Gotchas and 8.3 notes

Marked where the source material explicitly calls out a version boundary; unmarked items are general 8.3-era behavior worth flagging because they commonly surprise Vision developers or older Perspective users.

- **NEW (8.3): Font management/custom font workflow** — the manual's custom-theme walkthrough for adding a font now documents dedicated font `resource.json`/`config.json` pairs under `.../com.inductiveautomation.perspective/fonts/`, served at `/data/perspective/fonts/<file>`, referenced via `@font-face` in a `fonts.css` imported by the theme — and notes font-adding can alternatively go through dedicated `font` OpenAPI routes that auto-build these files. This is presented as current 8.3 guidance (example timestamps in the doc are dated late 2025).
- **NEW (8.3): Perspective Offline Mode** is documented as a first-class Project Properties section (`Perspective > Offline Mode`) with its own settings block (Enabled, Security Levels, Authentication Token Expiration, Always-ask-IdP, Themes, Languages) and a dedicated manual page — mobile-app-only, not for desktop browsers.
- **NEW (8.3): `tabIndex` Meta property** — a hidden-by-default Meta property to control keyboard tab-focus order, alongside the longer-standing `domId`.
- **NEW-ish: `system.perspective.workstation` scripting namespace** and the **Workstation Mode Action** for runtime Windowed/Kiosk switching — tied to the Perspective Workstation launcher (an 8.1+ feature) and its advanced fallback-redirect/redundancy settings, which read as more fleshed-out in 8.3's docs than earlier versions.
- **Advanced Stylesheet** (project-scoped raw CSS resource, `.psc-`/`.ia_` prefixes) is presented as a relatively recent addition to Style Classes for power users doing CSS-level overrides beyond the Style Class UI.
- **Authentication Challenge Action / session event** — a full secondary-user "e-signature" authentication workflow with a typed `Result.Success`/`Result.Error` (generic/timeout/cancelled) object model; framing options include Same Tab, New Tab, and Embedded Frame, with the note that Perspective Workstation sessions fall back to Same Tab (New Tab unsupported there) and mobile sessions only support Same Tab.
- **`isAuthorized()` and role-based script transforms are cosmetic only.** Both patterns documented for showing/hiding UI based on security level are explicitly *not* the actual enforcement mechanism — real enforcement is the Gateway-side Session/View/Action security settings. Don't rely on a disabled button alone to keep a user out.
- **No client scope in Perspective, ever.** This isn't new to 8.3 but remains a frequent point of confusion for Vision-background developers: `system.gui`, `system.nav`, `system.file` simply don't exist in a Perspective script context, and *all* Perspective scripting (including what "feels" like client-side logic) runs Gateway-side — with the time-zone-defaults-to-Gateway consequence that trips people up constantly.
- **Renaming a Style Class breaks every reference to it** — there's no automatic reference migration; every component using the old name silently reverts to unstyled and must be manually reapplied.
- **Persistent property + binding interaction**: adding *any* binding to a property auto-flips it to non-persistent. This is usually invisible/desired, but catches people who then wonder why their bound property's "saved" value doesn't survive a Designer close/reopen — it was never meant to.
- **Docked view "Corner Priority" and container semantics only apply to Coordinate containers for Pipes/rotation/anchors** — Pipes specifically can only be drawn inside a Coordinate Container; the draw/move tools disable themselves when any other container type is the current deep-selection target.
- **Perspective Session security ≠ IdP presence.** Selecting an IdP on a project is a *prerequisite* for View permissions and Event Action security to even be configurable — a project without an IdP selected cannot have per-view or per-action security applied, regardless of what's configured Gateway-side.
- **Query params vs. page-navigation params are mutually exclusive mechanisms.** URL query-string (`?key=value`) parameters only populate via direct browser navigation or `system.perspective.navigate(url=...)`; the Navigation Action's "Page" navigation type is for in-project page routing and does not carry query strings.
- **`onClick` still fires on a disabled component.** Several input components (Button et al.) keep dispatching `onClick` even while their `enabled` prop is false — use `onActionPerformed` instead when the intent is "only when the component is actually usable," or explicitly check the enabled state inside the script.
- **`ia_`-prefixed Style Class names are reserved.** User-created Style Classes must not use the `ia_` prefix (built-in Perspective styling) — doing so risks unintended collisions with base styling rules. Style Classes are injected client-side with a `.psc-` prefix, distinct from the `.ia_` prefix used for built-in component CSS classes — know which prefix to target when writing Advanced Stylesheet overrides.
- **Selecting a new theme requires a Gateway restart to take effect** (`session.props.theme` writes switch *which* theme is active at runtime, but the theme's own CSS is only (re)loaded into the Gateway on restart when first created/modified via file-system edits) — plan theme-authoring iteration accordingly, or use the OpenAPI theme-data-file endpoints which don't require this.
- **Base `light`/`dark` themes cannot be edited directly** — only derived themes (light-cool, light-warm, dark-cool, dark-warm) can be freely modified in place, and even those revert on upgrade; overriding a base theme requires the dedicated `overrides-light`/`overrides-dark` resource + `@import` pattern.
- **A Session's `device.identifier` is not a security-grade ID.** The manual explicitly calls it "not intended/suited for security purposes" since it can change across reinstalls or a browser cache clear — don't use it as a durable user/device identity key.
