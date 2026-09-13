> **Core KB:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md) · [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md) · [04-RESOURCE-MODEL](04-RESOURCE-MODEL.md) · [21-BINDINGS](21-BINDINGS.md)

# Perspective: the shipped schemas

Perspective is not documented by convention, it is documented by files that ship inside
the module. This page is the index of those files and the facts read out of them.

**Verified on Ignition 8.3.7, Perspective module 3.3.7.** Everything here came from
`perspective-common-3.3.7.jar` and the client bundle served by the running gateway. Where
a claim is inference rather than a file, it says so.

---

## 1. Where the truth lives

Inside `Ignition/data/jar-cache/com.inductiveautomation.perspective/`:

| Jar | Contains |
|---|---|
| `perspective-common-3.3.7.jar` | **all component schemas and all JSON schemas** |
| `app-3.3.7.jar` | the client and designer JS bundles under `mounted/js/` |
| `perspective-designer-3.3.7.jar` | `dom_events.json`, designer descriptors |
| `perspective-themes-3.3.7.jar` | the six built-in themes, as zips |

Extract the schemas:

```bash
IG="/c/Program Files/Inductive Automation/Ignition"
unzip -o "$IG/data/jar-cache/com.inductiveautomation.perspective/"*perspective-common*.jar \
  'descriptors/*' 'schemas/*' '*.components.json' '*.component.json' -d pcommon
```

### Component libraries

| File | groupId | Components |
|---|---|---|
| `ia.components.json` | `ia` | 70 |
| `perspective-googlemap.components.json` | `perspective-googlemap` | 1 |
| `perspective-timeseries.components.json` | `perspective-timeseries` | 3 |
| `perspective-amcharts.components.json` | `perspective-amcharts` | 4 |
| `perspective-map.components.json` | `perspective-map` | 1 |
| `pdf-viewer.components.json` | `pdf-viewer` | 1 |
| `barcode.component.json` | `barcode` | 1 |

**82 components total** (81 from `perspective-common`, plus `ia.reporting.report-viewer` shipped by the Reporting module itself in `reporting-components.components.json` - see 71-REPORTING-MODULE.md). Anyone quoting 70 is counting `ia.components.json` only; anyone quoting 81 missed the Reporting module's entry.

### JSON schemas in `schemas/`

| File | Describes |
|---|---|
| `binding-tag.json` | tag binding config |
| `binding-expr.json` | expression binding |
| `binding-expr-struct.json` | expression structure binding |
| `binding-property.json` | property binding |
| `binding-query.json` | named query binding |
| `binding-tag-history.json` | tag history binding |
| `binding-http.json` | HTTP binding |
| `transform-expr.json` | expression transform |
| `transform-format.json` | format transform |
| `transform-map.json` | map transform |
| `style-properties.schema.json` | the `style` object on every component |
| `css-props.schema.json` | the CSS subset behind it |
| `css-length.schema.json`, `css-time.schema.json`, `css-rotation.schema.json` | value formats |
| `session-props.json` | every built-in session property |
| `view-props-schema.json` | `view.props` |
| `style-class-schema.json` | a named style resource |
| `project-mounts.json` | project mount config |
| `icon-schema.json`, `optional-icon-schema.json`, `svg-fill.json`, `svg-stroke.json`, `trend-style.schema.json` | shared value shapes |
| `meta-schema.json` | the schema Ignition validates the others against |

### Scripting descriptors in `descriptors/`

`session.json`, `page.json`, `view.json`, `element.json`, `component.json`,
`key_events.json`, `authchallenge.json`, `error.json`, `success.json`,
`page_startup.json`. These drive Designer autocomplete for `self.session`, `self.page`,
`self.view` and friends.

`view.json` is short and worth knowing: a View exposes exactly three members, all dicts -
`props`, `custom`, `params`. A Page exposes `id`, `connected`, `views`, `props`, and one
method, `close(message=None)`.

---

## 2. Style precedence: the actual chain

This is the single highest-value fact on this page, and it explains a whole class of
"my style did nothing" bugs.

Every component's final DOM style is assembled in `emitterFactory`, in
`PerspectiveClient.<hash>.js`:

```js
const a = (n ? new Style : this.props.readStyle())
    .applyCssProperties(t.style ? t.style : {})
    .transformCssProperties(this.translateMetaToStyle)
    .transformCssProperties(p ? undefined : e.style)
    .addClasses(...)
```

and `applyCssProperties` is a plain merge, so **later stages overwrite earlier ones**:

```js
applyCssProperties(...e) { return Object.assign(this.style, ...e), this }
```

Read bottom-up, the winner is last:

| Order | Source | Beats |
|---|---|---|
| 1 | `props.style` - the style object you edit in the Designer | nothing |
| 2 | the component's own render style, built from its props | `props.style` |
| 3 | meta translation (`visible`, `domId`, ...) | 1 and 2 |
| 4 | the **parent container's child-position layout** | 1, 2 and 3 |
| 5 | rotation transforms | all |

Consequences:

- **A component prop always beats the equivalent CSS in `style`.** Not because the style
  is rejected, but because it is written first and then overwritten.
- **The parent's `position` always beats the child's own `style`.** A child cannot argue
  with its container about layout.

### Flex container: the prop to CSS map

From `PerspectiveComponents.<hash>.js`, verbatim:

```js
// flexParentProps: set on the container
direction   -> flexDirection
wrap        -> flexWrap
justify     -> justifyContent
alignItems  -> alignItems
alignContent-> alignContent
overflow    -> auto

// flexChildProps: set on each child, from the child's position object
align   -> alignSelf
grow    -> flexGrow
shrink  -> flexShrink
basis   -> flexBasis
display -> display     // false emits display:none
```

So `style.justifyContent` on a Flex Container is overwritten by `props.justify` at stage 2
of the chain above. Same for `flexDirection` vs `direction`, `flexWrap` vs `wrap`,
`alignItems`, `alignContent`.

The container's props reducer reads only these five:

```js
getPropsReducer(e) {
  return {
    direction:    e.readString("direction",  "row"),
    wrap:         e.readString("wrap",       "nowrap"),
    justify:      e.readString("justify"),
    alignItems:   e.readString("alignItems"),
    alignContent: e.readString("alignContent")
  }
}
```

and it skips falsy values when writing them out, so clearing a prop to `""` does leave
the style value in place. That is the one case where `style.justifyContent` survives.

### Flex child defaults

From `childPositionSchema` on `ia.container.flex`. Required: `grow`, `shrink`, `basis`.

| | default | consequence |
|---|---|---|
| `grow` | **0** | children do not expand by default. This is CSS's default too, but the habit of expecting `flex: 1` behaviour is where people get caught |
| `shrink` | 1 | a child may be squeezed below its stated size |
| `basis` | `auto` | width in a `row`, height in a `column` |
| `align` | - | per-child `alignSelf` |
| `display` | true | `false` emits `display: none` |

A fixed-size field is `basis: "104px"` plus `shrink: 0`. `style.width` alone loses,
because `flex-basis` outranks `width` on the main axis and `shrink: 1` lets the container
take the rest.

The cross axis is not the child's to set: it comes from the parent's `alignItems`, which
defaults to `stretch`. A row inside a `column` container is therefore already full width,
and a `width: 100%` that appears to fix something is masking a different problem.

---

## 3. The `style` object

`style-properties.schema.json` is `css-props.schema.json` plus three keys: `classes`,
`fill`, `opacity`. 93 properties are enumerated.

**It does not declare `additionalProperties: false`.** The enumerated 93 are the ones the
Designer gives editors and dropdowns for. Any other camelCased CSS property passes
through: `width`, `height`, `gap`, `padding`, `border`, `backgroundImage`, `boxShadow`
and so on all work and are used throughout Ignition's own views. So the list is an editor
affordance, not a whitelist.

`classes` is `["array", "string"]`, format `style-list` - the named styles applied to the
component.

---

## 4. Named styles

`style-classes` resources, one folder per style, holding `style.json` validated against
`style-class-schema.json`.

| Field | Notes |
|---|---|
| `pseudo` | one of 22 CSS pseudo-classes: `active`, `checked`, `default`, `disabled`, `empty`, `enabled`, `first-child`, `fullscreen`, `focus`, `hover`, `in-range`, `invalid`, `last-child`, `link`, `only-child`, `out-of-range`, `read-only`, `read-write`, `required`, `valid`, `visited` |
| `declarations` | plain CSS declarations, for a non-animated style |
| `animation` | `duration` (default `2s`), `delay` (`0s`), `direction`, `iterationCount` (default `infinite`), `timingFunction`, `fillMode` (default `both`) |
| `keyframes` | `0%` / `100%` / any `\d+%` key. **Required whenever `animation` is present** |

The style's own name is not in the file. It is the resource path.

---

## 5. Bindings

| Type | Required | Notable optional |
|---|---|---|
| `tag` | `tagPath` | `mode` (`direct` \| `indirect` \| `expression`), `bidirectional`, `references` for indirect |
| `expr` | `expression` | - |
| `expr-struct` | `struct` | `waitOnAll`, default `true`. Designer labels this "expressions" |
| `property` | `path` | `bidirectional` |
| `query` | `queryPath` | `mode` (`direct` \| `expression`), `returnFormat` (`auto` \| `json` \| `dataset` \| `scalar`), `parameters` (values are **expressions**), `polling.enabled`, `polling.rate` (number of seconds, or a string treated as an expression), `designerUseLimit`, `bypassCache` |
| `tag-history` | see `binding-tag-history.json` | |
| `http` | see `binding-http.json` | |

All of the above declare `additionalProperties: false`, so an unrecognised key is a
hard error, not a silently ignored one.

Query binding detail worth remembering: `polling.rate` may be a string, and a
non-positive rate disables polling rather than erroring.

### Transforms

- `expr` - `{ "expression": "..." }`
- `format` - `formatType` is `datetime` or `numeric`; `formatValue` is either a named
  size (`full` \| `long` \| `medium` \| `short` for dates, `currency` \| `integer` \|
  `number` \| `percent` for numbers) or a Java `SimpleDateFormat` / `DecimalFormat`
  pattern. Default is `{"formatType": "datetime", "formatValue": "yyyy-MM-dd h:mm:ss aa"}`
- `map` - see `transform-map.json`
- `script` - stores the **body only**, tab-indented, with no `def` line

### One binding beats twenty

For many tags into one component, bind an object prop once rather than binding each key:
either an expression binding on `now(1000)` with a script transform doing
`system.tag.readBlocking`, or an `expr-struct` binding.

In a read transform, **omit** a key when its tag quality is bad, rather than sending `0`.
A dropped key leaves the consumer's previous value; a `0` shows a confident wrong number.

---

## 6. Session props

`schemas/session-props.json`. The full set of built-ins:

`id`, `host`, `theme` (default `light`), `locale`, `timeZoneId`, `lastActivity`.

| Group | Keys |
|---|---|
| `auth` | `authenticated`, `user.{id,userName,firstName,lastName,email,roles,timestamp}`, `securityLevels` |
| `gateway` | `address`, `timezone` |
| `device` | `type` (`ios` \| `android` \| `designer` \| `browser` \| `workstation` \| `""`), `identifier`, `timezone`, `userAgent`, `settings.{pullToRefresh,preventSleep}`, `accelerometer.{timestamp,x,y,z}` |
| `bluetooth` | `enabled`, `options.{updateInterval,limit,filter}`, `data` |
| `geolocation` | `enabled`, `permissionGranted`, `options.{accuracy,timeout,maximumAge}`, `data.{latitude,longitude,altitude,accuracy,altitudeAccuracy,heading,speed,timestamp}` |
| `appBar` | `togglePosition` (`left` \| `right` \| `hidden`), `about.{show,icon,path,title}` |
| `pipes` | `autoAppearance` (`p&id` \| `mimic` \| `simple`, default `simple`), `overlapGap` (default 4) |
| `symbols` | `autoAnimationSpeed` (default 100), `autoAppearance` (default `simple`) |
| `offline` | `capable`, `enabled`, `lastSynced`, `language` |
| | `googleMapsApiKey` |

`pipes` and `symbols` are session-wide appearance switches. Any component or pipe set to
`appearance: "auto"` follows them, so a whole project's P&ID vs mimic look is one
session prop.

---

## 7. View props

`schemas/view-props-schema.json`:

| Prop | Default | Notes |
|---|---|---|
| `defaultSize.width` / `.height` | 800 / 800 | |
| `loading.mode` | `non-blocking` | `blocking` \| `non-blocking` |
| `inputBehavior` | `replace` | `merge` \| `replace`. How input params combine with their defaults |
| `dropConfig.udts[]` | `[]` | `{type (udt-path), param, action: bind \| path}` |
| `dropConfig.dataTypes[]` | `[]` | `{type, param, action}` where type is one of the 22 Ignition data types |

`dropConfig` is what makes a view a drop target for a tag or UDT dragged from the tag
browser. It is per-view, and it is the supported way to build "drag a UDT onto the canvas
and get a faceplate".

---

## 8. Client action scopes

The client resolves an action type against a registry:

```js
if ("C" === scope) { const a = ActionRegistry.get(type); if (a) { ...register... } }
else if ("G" === scope) { gatewayActionRequired = true }
```

`if (a)` has no else. A type with no client-side implementation is dropped **silently**.

There is no client-side `script` action, because Python cannot run in a browser. So
`{"type": "script", "scope": "C"}` registers nothing, runs nothing, and logs nothing. The
button is simply dead. Python actions need `scope: "G"`.

---

## 9. Component inventory

`showOnPalette = NO` means the component exists and can be instantiated, but is only
reachable through the Drawing editor.

| Category | id | Name | Library | Palette | Child pos | Events |
|---|---|---|---|---|---|---|
| - | `ia.navigation.navlinks` | Nav Links | ia | yes | - | - |
| chart | `ia.chart.chartrangeselector` | Chart Range Selector | perspective-timeseries | yes | - | - |
| chart | `ia.chart.gauge` | Gauge | perspective-amcharts | yes | - | - |
| chart | `ia.chart.pie` | Pie | perspective-amcharts | yes | - | - |
| chart | `ia.chart.powerchart` | Power Chart | perspective-timeseries | yes | - | - |
| chart | `ia.chart.simple-gauge` | Simple Gauge | perspective-amcharts | yes | - | - |
| chart | `ia.chart.timeseries` | Time Series Chart | perspective-timeseries | yes | - | - |
| chart | `ia.chart.xy` | XY Chart | perspective-amcharts | yes | - | - |
| container | `ia.container.breakpt` | Breakpoint Container | ia | yes | yes | - |
| container | `ia.container.column` | Column Container | ia | yes | yes | - |
| container | `ia.container.coord` | Coordinate Container | ia | yes | yes | onPipeClicked |
| container | `ia.container.drawing` | Drawing | ia | **NO** | yes | - |
| container | `ia.container.flex` | Flex Container | ia | yes | yes | - |
| container | `ia.container.split` | Split Container | ia | yes | yes | onMinBoundReached, onMaxBoundReached |
| container | `ia.container.tab` | Tab Container | ia | yes | yes | - |
| display | `ia.display.alarmjournaltable` | Alarm Journal Table | ia | yes | - | - |
| display | `ia.display.alarmstatustable` | Alarm Status Table | ia | yes | - | - |
| display | `ia.display.audio` | Audio | ia | yes | - | onPlay, onPause, onError, onEnded, onLoaded, onRateChanged |
| display | `ia.display.barcode` | Barcode | barcode | yes | - | - |
| display | `ia.display.cylindrical-tank` | Cylindrical Tank | ia | yes | - | - |
| display | `ia.display.dashboard` | Dashboard | ia | yes | - | - |
| display | `ia.display.equipmentschedule` | Equipment Schedule | ia | yes | - | onAddEvent, onMoveEvent, onResizeEvent, onDeleteEvent, onClickEvent |
| display | `ia.display.google-map` | Google Map | perspective-googlemap | yes | - | 104 events, see the schema |
| display | `ia.display.icon` | Icon | ia | yes | - | - |
| display | `ia.display.iframe` | Inline Frame | ia | yes | - | - |
| display | `ia.display.image` | Image | ia | yes | - | - |
| display | `ia.display.label` | Label | ia | yes | - | - |
| display | `ia.display.led-display` | LED Display | ia | yes | - | - |
| display | `ia.display.linear-scale` | Linear Scale | ia | yes | - | - |
| display | `ia.display.map` | Map | perspective-map | yes | - | onMarkerClick, onMapClick, onMapMouseMove, onVectorClick, onZoom*, onMove*, onResize |
| display | `ia.display.markdown` | Markdown | ia | yes | - | - |
| display | `ia.display.moving-analog-indicator` | Moving Analog Indicator | ia | yes | - | - |
| display | `ia.display.pdf-viewer` | PDF Viewer | pdf-viewer | yes | - | - |
| display | `ia.display.progress` | Progress | ia | yes | - | - |
| display | `ia.display.sparkline` | Sparkline | ia | yes | - | - |
| display | `ia.display.table` | Table | ia | yes | - | onEditCellCommit, onEditCellStart, onEditCellCancel, onSelectionChange, onRowClick, onRowDoubleClick, onSubviewExpand, onSubviewCollapse |
| display | `ia.display.tag-browse-tree` | Tag Browse Tree | ia | yes | - | onNodeClick, onNodeDoubleClick, onNodeContextMenu |
| display | `ia.display.thermometer` | Thermometer | ia | yes | - | - |
| display | `ia.display.tree` | Tree | ia | yes | - | onItemClicked |
| display | `ia.display.video-player` | Video Player | ia | yes | - | - |
| display | `ia.shapes.svg` | Drawing | ia | yes | - | onElementClicked |
| embedding | `ia.display.accordion` | Accordion | ia | yes | - | onItemExpanded, onItemCollapsed |
| embedding | `ia.display.carousel` | Carousel | ia | yes | - | - |
| embedding | `ia.display.flex-repeater` | Flex Repeater | ia | yes | - | - |
| embedding | `ia.display.view` | Embedded View | ia | yes | - | - |
| embedding | `ia.display.viewcanvas` | View Canvas | ia | yes | - | onInstanceClicked |
| input | `ia.input.barcodescannerinput` | Barcode Scanner Input | ia | yes | - | onActionPerformed |
| input | `ia.input.button` | Button | ia | yes | - | onActionPerformed |
| input | `ia.input.checkbox` | Checkbox | ia | yes | - | onActionPerformed |
| input | `ia.input.date-time-input` | DateTime Input | ia | yes | - | onActionPerformed |
| input | `ia.input.date-time-picker` | DateTime Picker | ia | yes | - | onActionPerformed |
| input | `ia.input.dropdown` | Dropdown | ia | yes | - | onActionPerformed |
| input | `ia.input.fileupload` | File Upload | ia | yes | - | onFileReceived, onUploadsCleared |
| input | `ia.input.form` | Form | ia | yes | - | onChange, onSuccess, onError, onCancelActionPerformed, onSubmitActionPerformed |
| input | `ia.input.multi-state-button` | Multi-State Button | ia | yes | - | onActionPerformed |
| input | `ia.input.numeric-entry-field` | Numeric Entry Field | ia | yes | - | onActionPerformed |
| input | `ia.input.oneshotbutton` | One-Shot Button | ia | yes | - | onActionPerformed |
| input | `ia.input.password-field` | Password Field | ia | yes | - | - |
| input | `ia.input.radio-group` | Radio Group | ia | yes | - | onActionPerformed |
| input | `ia.input.signature-pad` | Signature Pad | ia | yes | - | onSignatureSubmitted, onSignatureCleared |
| input | `ia.input.slider` | Slider | ia | yes | - | onActionPerformed |
| input | `ia.input.text-area` | Text Area | ia | yes | - | - |
| input | `ia.input.text-field` | Text Field | ia | yes | - | - |
| input | `ia.input.toggle-switch` | Toggle Switch | ia | yes | - | onActionPerformed |
| navigation | `ia.navigation.horizontalmenu` | Horizontal Menu | ia | yes | - | onItemClicked |
| navigation | `ia.navigation.link` | Link | ia | yes | - | - |
| navigation | `ia.navigation.menutree` | Menu Tree | ia | yes | - | onItemClicked |
| shapes | `ia.shapes.circle` | Circle | ia | **NO** | - | - |
| shapes | `ia.shapes.ellipse` | Ellipse | ia | **NO** | - | - |
| shapes | `ia.shapes.group` | Group | ia | **NO** | yes | - |
| shapes | `ia.shapes.line` | Line | ia | **NO** | - | - |
| shapes | `ia.shapes.path` | Path | ia | **NO** | - | - |
| shapes | `ia.shapes.polygon` | Polygon | ia | **NO** | - | - |
| shapes | `ia.shapes.polyline` | Polyline | ia | **NO** | - | - |
| shapes | `ia.shapes.rect` | Rectangle | ia | **NO** | - | - |
| shapes | `ia.shapes.text` | Text | ia | **NO** | - | - |
| symbols | `ia.symbol.motor` | Motor | ia | yes | - | - |
| symbols | `ia.symbol.pump` | Pump | ia | yes | - | - |
| symbols | `ia.symbol.sensor` | Sensor | ia | yes | - | - |
| symbols | `ia.symbol.valve` | Valve | ia | yes | - | - |
| symbols | `ia.symbol.vessel` | Vessel | ia | yes | - | - |

Two id traps worth naming:

- **`ia.shapes.svg` is the palette component called "Drawing"**, in the `display`
  category. `ia.container.drawing` is a different thing and is not on the palette.
- **There is no Pipe component.** Pipes are the `pipes` array property on
  `ia.container.coord`. See [CoordinateContainer](Components/Containers/CoordinateContainer.md).

Only 7 containers accept children (`childPositionSchema`): breakpoint, column,
coordinate, drawing, flex, split, tab, plus `ia.shapes.group` inside the Drawing editor.

---

## 10. Gaps in this KB

Component pages exist for 56 of the 81. Missing pages, all verified to exist in the
product:

- Symbols: Motor, Pump, Sensor, Valve, Vessel
- Shapes: Circle, Ellipse, Group, Line, Path, Polygon, Polyline, Rectangle, Text
- Navigation: Nav Links

`Components/` also carries duplicate `Gauge.md` and `Simple-Gauge.md` under two
directories.

---

## See Also

- [04-RESOURCE-MODEL](04-RESOURCE-MODEL.md) - where these resources live on disk
- [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md)
- [21-BINDINGS](21-BINDINGS.md)
- [Component Index](Components/00-Component-Index.md)

[↑ Back to KB INDEX](00-INDEX.md)
