# Playbook: which Ignition mechanism to use

Design-decision tables for Perspective-centred Ignition 8.3 work. Each row: **use X when / avoid when / example / trap / source**.
Sources are paths under the skill base dir. `PM` = `references/ignition-8-3/perspective-module.md` (section named after the arrow).
A rule with no verified source is marked **unverified** — treat it as judgement, not fact.
Mechanically checkable rules are FAT warnings: `python3 scripts/fat.py <dir>` (see the last section).

## 0. One-page quick-decision flow

Ask top to bottom; stop at the first "yes".

1. **Is the value a live tag value shown as-is (or with a lookup)?** → Tag binding (direct, or indirect if the path varies) + Map/Format transform. Not an expression. (§1, §2)
2. **Is it derived from tags/properties by arithmetic, string, `if()`?** → Expression binding. Expression transform if it needs a prior binding's `{value}`. (§1, §2)
3. **Does it need a loop, dict/list building, dataset reshape, or a `system.*` call?** → Script transform (last resort), or a native Value Format (Document/JSON) first. (§2)
4. **Is it data from SQL?** → Named Query, via Query binding (or `system.db.runNamedQuery` in a script). Not raw SQL in a binding (not possible) or a script (unchecked). (§7)
5. **Is it history of tags?** → Tag History binding. Not a Named Query on the history tables. (§7)
6. **Does a user action cause something?** → Component event script (scope `G`) for writes/logic; nav/popup/logout actions (scope `C`) for UI moves. (§3)
7. **Does something in one place need to make another place react?** → `system.perspective.sendMessage` to a message handler, tightest scope. Not a tag write, not a deep property path into another view. (§3, §5)
8. **Does the same layout repeat with different data (3+ times)?** → Embedded View with params. (§4)
9. **Must the same element appear on every page?** → Shared dock. Transient/modal content → popup. Reused block inside a view → embed. (§6)
10. **Where does the state live?** Per-instance input → view param. Which page/record → URL param. Per-user session state → `session.props` / `session.custom`. Plant-wide shared → tag. (§5)
11. **Should logic run on data change or on a clock?** Change → tag-change/event script. Clock → timer. Never a tight polling loop. (§9)
12. **Colour/spacing/font?** → Style class using theme variables. Inline only for one-off geometry. (§10)

## 1. Binding types

| Type | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Tag (direct) | Property mirrors one fixed tag; want quality overlay and optional write-back | Path varies per instance; value needs computing | `[prov]Line1/Pump/Speed` → `props.value` | Bad quality shows the overlay unless "Overlay Opt-Out" | PM → Binding types |
| Tag (indirect) | One view serves many tags; path assembled from a view param/property | One fixed tag (adds indirection for nothing) | `[prov]{1}/Amps` with `{1}` = `view.params.instancePath` | Placeholders must reference a Property or View Parameter; a wrong param name yields a silently unbound prop | PM → Binding types (Indirect) |
| Tag (expression path) | Path itself must be computed (string concat) and the binding must stay bidirectional | Simple `{1}` substitution is enough | path expr built from two params | Different from an Expression *binding*; only tag mode that is both dynamic and bidirectional | PM → Binding types (Expression) |
| Property | Copy one property into another in the same view; pass a value into an embedded view's param | Value lives in another view instance | `view.custom.rows` → `props.data` | Cannot cross view instances; use `session` or a message | PM → Binding types, "Session/page/view scopes" table |
| Expression | Derived, read-only value from tags/properties; formatting; conditional style class | Needs loops, dicts, `system.*`; needs write-back | `if({view.params.value.state} = 'Fault', "alarm", "ok")` | No `? :` ternary — only `if(c,a,b)`. Only polls if it uses a clocked function like `now()` | `references/ignition-8-3/expression-language.md`; PM → Binding types (Expression) |
| Expression structure | Build an object param from several small expressions (one per key) | Only one value is needed | `{label: ..., colour: ..., visible: ...}` fed to an embed | `Wait On All` off → keys publish independently, partial object briefly visible | PM → Binding types (Expression Structure) |
| Query (Named Query) | Data from SQL with parameters; want caching/shared polling | One-off write/update (use a script); tag history | `runs/ByLine` with `lineId` from a param | Only Named Queries, no ad-hoc SQL; enable Cache & Share for shared slow queries; Designer Limit only caps preview | PM → Binding types (Query); `references/gateway/named-queries.md` §7 |
| Tag history | Trend/table of historised tag values | Non-tag SQL data; tags without history enabled | Chart `series[0].data` over last 8h | Historical range is inclusive of End; AsStored on a wide range returns huge datasets | PM → Binding types (Tag History), "Table/chart performance" |
| HTTP | External REST JSON into a property | Data available via tag/DB; needs secrets in the view | weather/ERP JSON → props | Give it Cache & Share and a polling rate; URL/body are expressions, quote literals | PM → Binding types (HTTP) |

Bidirectional: only on Tag/Property bindings that a user edits (inputs). Turn on **Coalesce** when the target is an object/array whose children change independently, else write storms. Source: PM → "Bidirectional bindings", "Avoiding over-bound props".

## 2. Transform vs expression vs script

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Map transform | Value/range → colour, style class, text | Result depends on several inputs | State code → style class `Status/Fault` | First match wins top-down; set a Fallback row | PM → Transforms |
| Format transform | Number/date → string | Need arithmetic first | `0.0` pattern, `%` | Output is always a string | PM → Transforms |
| Expression transform | One more step on `{value}` after a tag/indirect binding | The whole binding could be one expression | `toInt({value})` | — | PM → Transforms |
| Expression binding (vs transform) | Value comes from several tags/props | Single source with a bound output | see §1 | — | PM → Binding types |
| Script transform | Loop/dict/list/dataset reshape; lookup with logic; call a library function | The body is a single `return <expression>` — that is an expression | Dataset → array of objects for a table | Runs on the gateway, per refresh, Jython 2.7 (no f-strings); returned type overwrites the property type. **FAT warns** on a pure-expression script | PM → Transforms (Script), "Performance and design guidance"; `references/gateway/scripting-contexts.md` |
| Native Value Format (Document/JSON) | Query/tag-history result must feed table/chart | Need per-row computation | tag history → chart series | Prefer over a reshaping script transform | PM → Transforms (Script note), "Table/chart performance" |
| Property change script | React to a change with side effects (write, message) | Only a derived value is needed — use an expression | On `value` change send a message | More session overhead than an expression binding | PM → Property Change Scripts, "Avoiding over-bound props" |

## 3. Script scopes: where does the code run?

All Perspective scripting runs on the gateway; there is no client scope. "Session" only means whose UI is affected. Source: PM → "Fundamentals and scope rules"; `references/gateway/scripting-contexts.md`.

| Slot | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Component event (`events.<domain>.<event>`, `scope: "G"`) | A user action must write a tag, call a query, open something with logic | Pure navigation/popup (use declarative actions) | Button writes a setpoint | Envelope is `{config, permissions, scope, type}`; a bare `{"script":…}` NPEs every project-diff; script needs `scope: "G"` (`"C"` dies silently). view_lint fails the bare shape | `references/gateway/perspective-events.md`; PM → "Component Events and Actions reference" |
| Declarative action (nav / popup / logout, `scope: "C"`) | Move between pages, open a popup | Any logic or write | Nav item → `/admin/users` | `popup`/`nav`/`logout` are client scope; script is gateway scope | `references/gateway/perspective-events.md` rule 3 |
| Message handler (component/view; session-scope in project events) | One place must trigger reaction elsewhere (refresh, close, reset), incl. from a gateway script | A direct call would do; broad `session` scope for local coordination | `system.perspective.sendMessage("refresh", scope="page")` | Async and unordered; scope `view` < `page` < `session`; session-scope Message event scripts answer `system.util.sendMessage`, a different mechanism | PM → "Component event scripts and Component Message Handlers", "Message handler patterns" |
| Gateway event script (timer / tag-change / startup) | Work with no session: aggregation, cleanup, polling an external system, reacting to a tag | Anything needing a session/page (`navigate`, `openPopup`) | Timer writes a rolled-up tag | No `system.perspective.navigate`; reach sessions via `sendMessage`. New timer/tag-change script needs `restartScripting()` to start. Keep the body short | `references/gateway/scripting-contexts.md` §1; `references/standards/jython.md` "Threading" |
| Project library (script module) | Same logic in 2+ places (transforms, events, timers) | One-off logic; anything a binding/expression handles | `userAdmin.levelOf(value)` | Callable from tag event scripts only if it is in the gateway scripting project | PM → Transforms; `references/ignition-8-3/tags-alarms-historian.md` "Gateway tag change scripts vs. tag event scripts" |
| Tag event script (on a tag/UDT definition) | Logic that must follow the tag itself, for every instance | Project-specific UI reaction | Definition-level value-change hook | Gateway-scoped, not project-scoped; use a logger, not `print`; specify the DB explicitly | `references/ignition-8-3/tags-alarms-historian.md` same section |
| Long work | Anything blocking >~ a second | On the event thread | Offload with `system.util.invokeAsynchronous` | Blocking stalls tag processing | `references/standards/jython.md` "Threading" |

## 4. Template vs embedded view vs inline

Perspective has no Template resource; a view with params, mounted by an Embedded View or Flex Repeater, is the template. Source: `references/gateway/component-composition.md`; PM → "View embedding vs. templates".

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Embedded View + params | Same layout, different data, 3+ repeats (or any repeat you'll need to change once) | Layout appears once and is tightly bound to its parent | A KPI tile embedded per KPI | Param names must match the target view's params (lint checks it); untick `useDefaultViewWidth/Height` to remove scrollbars | `references/gateway/component-composition.md`; PM → Primary view… "Embedded View" |
| Flex Repeater of embeds | N items from a list/dataset | Fixed small set | One card per line from a query | Instances share one view definition — expected | PM → "View embedding vs. templates" |
| Inline components | One-off layout | Copy-pasted 3rd time | Page header used once | Copy-paste drift: each copy diverges | `references/gateway/component-composition.md` ("3+ repeats → template") |
| Bound `path` on the embed | Swap sub-views by state | Static path | Tabs choose a view path | Bound path is non-persistent → empty flash; set Persistent with a default path | PM → "View embedding vs. templates" |
| Expose a UDT-shaped object param | Detail view for a UDT | Loose set of unrelated tags | Object param with keys = UDT member names; `dropConfig.udts` | Keys must match member names 1:1 | PM → Drop Configuration |

## 5. Where does state live?

| Store | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| View params (in/out/in-out) | Input contract of an embedded/docked/popup view; value differs per instance | Data shared with unrelated views | `instancePath` of an embed | Name-match between caller and view; direction matters | PM → View properties…, "Parameter direction" |
| Page URL params (`/:name` segment) | Which record/asset a page shows; bookmarkable | Secrets; per-user state | `/asset/:assetId` → primary view param `assetId` | Values are strings; bad chars `/ ? # %` | PM → "Page configuration and URL routing" |
| Query string → `page.props.urlParams` | Optional read-only filters from a link | Set from a page-navigation action | `?line=2` | Read-only, strings, only from browser nav or `system.perspective.navigate(url=…)`, not nav actions | PM → "Page configuration and URL routing" |
| Session props (`session.props`, `session.custom`) | Per-user/per-session state read by many views: theme, locale, selected site, auth user | Plant-wide shared data; heavy data | `session.props.theme` | The only sanctioned cross-view channel for bindings; writes to Protected/Private props from browser are blocked (scripts/bindings are fine); `session.custom` **unverified** in this skill's refs — confirm on a live session | PM → "Sessions, Pages, Views", "Session properties reference", "Restricting and persisting properties" |
| View custom props | State private to one view, computed helpers | Read from other views | `view.custom.selectedRow` | Not reachable across view instances | PM → "View properties" |
| Page props (`page.props`) | Read path/title/dimensions/urlParams | Storing your own state — **unverified** whether custom keys are supported | `page.props.title` binding | Not visible in the property editor | PM → "Page configuration and URL routing" |
| Tag | Value shared plant-wide/across sessions, historised, alarmed, or PLC-facing | Per-session transient data | Setpoint, status | Tags are global: sessions race each other on transient values | PM → "Message handler patterns" |
| Client tag | Vision only; Perspective's analogue is `session.props` | Any Perspective work | — | Do not look for client tags in Perspective | PM → "Sessions, Pages, Views" table |
| Database | Cross-session persisted records | Fast-changing live values | Shift notes | Go through a Named Query | PM → "Message handler patterns" |

## 6. Docks vs popups vs embedded

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Shared dock (`page-config` `sharedDocks`) | Element on every page: nav, header, status bar | Content specific to one view | Left nav, top header | One dock per edge; a view listed as a dock must not also be embedded; deleting it without removing dock references breaks project-diff for all routes | `references/gateway/component-composition.md`; PM → "Primary view, docked views, popups" |
| Popup | Short-lived task/confirmation/detail over the current page | Persistent navigation; content that must survive navigation | User-session dialog | Needs an Identifier to close/toggle later; `popup` action is scope `C` | PM → same; `references/gateway/perspective-events.md` |
| Embedded view | Reused block inside a view | Page-wide chrome | KPI tile | See §4 | `references/gateway/component-composition.md` |
| Page (primary view + route) | A distinct destination the user can bookmark | Small transient UI | `/admin/users` | The route must exist in `page-config` `pages`; check it live before linking | PM → "Page configuration and URL routing" |

## 7. Named query vs tag history vs raw SQL

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Named Query | Any SQL read/write shared or bound; typed params, cache, permission | Trend of historised tags | Events by line and date range | User input must be `:param`, never `{param}` (spliced into SQL); cache only slow, idempotent reads; row cap belongs in the SQL; `permissions` guards only declarative bindings | `references/gateway/named-queries.md` agent rules 3, 6, 7, 9 |
| Tag history binding / `system.tag.queryTagHistory` | Time series of a historised tag: charts, trend tables, aggregates | Tag has no history configured; relational records | 8h chart of a temperature | Historise per point at design time; wide AsStored ranges are huge | `references/standards/historian.md` "Design decisions"; PM → "Table/chart performance" |
| Raw `system.db.runQuery` / `runPrepQuery` in a script | Gateway job with no named query yet, dynamic structure | Anything bound to a view; user-supplied values via string concat | Maintenance script | Bypasses Named Query permissions and cache; use `runPrepQuery` with params | `references/gateway/named-queries.md` agent rule 7; **unverified**: preference of `runPrepQuery` over `runQuery` (general SQL-injection practice) |
| Update/insert from a button | Persist a user action | Bound reads | `UpdateQuery` NQ called with `system.db.runNamedQuery` from an event | Type must match the `exec*` call; never cache `UpdateQuery` | `references/gateway/named-queries.md` agent rules 2, 9 |

## 8. UDT vs folders vs plain tags

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| UDT (type + instances) | 2+ pieces of equipment share a shape; want one place for history/alarms/scaling | One-off device | `Motor` with Run/Speed/Fault | Parameterise, do not override instances; keep history/alarm config on the type | `references/standards/udt-design.md` "Parameters vs member overrides", "Type-level alarms & history…" |
| Nested UDT | Sub-assembly reused inside several parents | Only visual grouping | `Motor` inside `Skid` | Keep nesting to 2–3 levels; create leaf types first | `references/standards/udt-design.md` "Nest a UDT vs use a folder", "Dependency-order creation" |
| Folder member inside a type | Grouping within one type | Reuse across types | `Alarms/` folder inside `Motor` | No reuse | same |
| Folder + plain tags | One-off equipment, never repeated | Anything you will copy | A single flow meter | Copy-paste diverges | same |

## 9. Polling vs event-driven

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Binding (tag/expression) | Anything a view shows live | — | Live value label | Subscription-based; only clocked functions (`now()`) poll | PM → Binding types (Expression) |
| Tag change script (gateway) | React to a value change: log, write derived tag, message sessions | Work that must happen on a schedule regardless | Log a batch start when a tag flips | Wildcard paths need 8.3.4+; never run long work on the event thread | `references/ignition-8-3/tags-alarms-historian.md` (8.3.4 wildcards, tag-change section); `references/standards/jython.md` "Threading" |
| Event Streams | Stream tag/event data to an external sink | Simple derived tag | Motor events to a stream | See the Event Streams reference | `references/gateway/event-streams.md` |
| Gateway timer script | Periodic work with no trigger (roll-ups, external poll) | Change-driven work | 60 s aggregation | `sharedThread=false` for own thread; new timer needs `restartScripting()`; keep body short | `references/standards/jython.md` "Threading"; `references/gateway/scripting-contexts.md` §1 |
| Binding poll rate + Cache & Share | Query/history/HTTP data many sessions share | Values that must be instant (use a tag) | Shared dashboard query | Cache TTL = poll rate (250 ms if polling off) | PM → Binding types, "Avoiding over-bound props" |
| `self.refreshBinding()` from a message | Refresh on demand after a write | Continuous data | Save button refreshes a table | — | PM → Built-in component methods, "Message handler patterns" |
| Scripted polling loop | Never for UI | Always | — | Multiplies gateway CPU across sessions | PM → "Common causes of slow sessions" |

## 10. Style classes / theme variables vs inline style

| Choice | Use when | Avoid when | Example | Trap | Source |
|---|---|---|---|---|---|
| Style class | Reused look; state variants (hover/disabled); animated alerts; switch look by binding on `style.classes` | One-off geometry | `Card`, `Muted` | Renaming breaks every reference; never use the reserved `ia_` prefix; class names are visible client-side | PM → "Style classes" |
| Theme CSS variable in a class/style (`var(--x)`) | Colours/spacing that must follow the active theme | Chart props that take literal colours (**unverified**: amCharts-based `ia.chart.*` props do not resolve `var()`; verify per component) | `background: var(--hmi-chrome)` | Built-in themes' derived variants reset on upgrade — author a custom theme | PM → "Themes"; `references/standards/isa101-hmi.md` |
| Inline style | One-off position/size tweak | Any colour that has a theme token; anything copied twice | `style.marginTop` | Inline hex defeats theming. **FAT warns** on hex literals in view styles | PM → "Style properties"; `references/standards/isa101-hmi.md` |
| Map transform → `style.classes` | State-driven look (Fault/Normal) | Two-state boolean — an expression `if()` is shorter | State code → class | Set a Fallback row | PM → Transforms (Map), "Style classes" |
| Advanced stylesheet | Raw CSS the class editor cannot express | Anything a class can do | Custom scrollbar | Target `.psc-<className>`; project-scoped | PM → "Style classes" (Advanced Stylesheet) |

## FAT warnings (mechanical rules)

`python3 skill/scripts/fat.py <dir>` prints these under `warnings` (never failures; exit code unchanged):

| Warning check | Rule | Section |
|---|---|---|
| `playbook.script-transform` | A script transform whose body is one `return <expr>` and touches no `self`/`system`/`value.` method — try an expression transform | §2 |
| `playbook.hex-literal` | Hex colour literals in a view's `style` props (per view, with a count) — use a theme variable/class | §10 |

A bare `{"script": …}` event action is not repeated here: `view_lint` (run by FAT) already fails it (§3).

Test: `python3 skill/scripts/test_fat_playbook.py`.
