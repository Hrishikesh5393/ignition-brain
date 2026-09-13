# Verified traps

Every entry says where it was verified so it can be re-checked rather than trusted.
Verified against Ignition **8.3.7** unless noted. If `get_gateway_info` reports a
different version, re-check before relying on any of it.

---

## Layout

### Flex layout is props, not CSS

`ia.container.flex` declares `direction`, `wrap`, `justify`, `alignItems`,
`alignContent` as **required** props with defaults `row`, `nowrap`, `flex-start`,
`stretch`, `stretch`. The container maps them straight onto CSS:

```
direction -> flexDirection   wrap -> flexWrap   justify -> justifyContent
alignItems -> alignItems     alignContent -> alignContent
```

`style.justifyContent` is not rejected. `style` has no `additionalProperties: false`, so
it binds and reaches the DOM, and is then overwritten. See the precedence chain below.

*Verified: `ia.components.json` from `perspective-common-3.3.7.jar`, and
`flexParentProps` in `PerspectiveComponents.<hash>.js`.*
*Cost: 113 occurrences across one project, and repeated alignment problems chased from
the wrong end.*

### The style precedence chain

`emitterFactory` in `PerspectiveClient.<hash>.js` assembles the final style, and
`applyCssProperties(...e) { return Object.assign(this.style, ...e), this }` is a plain
merge, so later stages overwrite earlier ones:

| Order | Source |
|---|---|
| 1 | `props.style` |
| 2 | the component's own render style, built from its props |
| 3 | meta (`visible`, `domId`) |
| 4 | **the parent container's child-position layout** |
| 5 | rotation transforms |

Two rules fall out of this, and they explain most "my style did nothing":

- a component prop always beats the equivalent CSS in its own `style`
- the parent's `position` always beats the child's `style`

*Verified: `emitterFactory` and `applyCssProperties` in the client bundle.*

### Flex children are sized by `position`

Each child carries a `position` object. `grow`, `shrink`, `basis` are required:

| | default | meaning |
|---|---|---|
| `grow` | **0** | not 1. Children do not expand by default |
| `shrink` | 1 | the child may be squeezed below its stated size |
| `basis` | `auto` | size along `direction`: width when row, height when column |
| `align` | - | per-child cross-axis override |
| `display` | true | **false removes the child from layout**, not CSS `display` |

A fixed-size field is `basis: "104px"` with `shrink: 0`. A `style.width` sits outside
the flex negotiation and loses to it: with the default `shrink: 1` the container is free
to make it narrower than asked.

*Verified: `childPositionSchema`, a sibling key of `schema`, same file.*

### The cross axis is not the child's to set

It comes from the parent's `alignItems`, default `stretch`. A row inside a `column`
container is therefore already full width. If `width: 100%` on it appears to help,
something else is wrong and the width is hiding it.

*Learned the hard way: 11 rows carried a `width: 100%` that was never needed.*

---

## Events and scripts

### Python actions need `scope: "G"`

The client resolves an action type against a client-side registry:

```js
if ("C" === scope) { const a = ActionRegistry.get(type); if (a) { ...register... } }
else if ("G" === scope) { gatewayActionRequired = true }
```

There is no client-side `script` action, because Python cannot run in a browser. So
`{"type": "script", "scope": "C"}` resolves to nothing, registers nothing, and logs
nothing. The button is simply dead.

*Verified: `PerspectiveClient.*.js` from the running gateway.*
*Cost: every popup in a project silently broken, and long assumed to be a styling issue.*

### Script transforms and event scripts store the body only

No `def transform(...)` line. Tab-indented body:

```json
{ "type": "script", "code": "\treturn 'AHU %s' % value" }
```

*Verified: existing working transforms in a real project.*
*Same convention as tag event scripts via the configure API.*

---

## Bindings

### PropertyTree reads more than three types

`readString`, `readNumber`, `readBoolean`, `readObject`, `readArray`, `readEncoded`,
`readDate`, `readColor`.

`readObject(path, {})` is what lets a component take an arbitrary-shaped object prop
without declaring its keys.

*Verified: `PerspectiveClient.*.js`.*
*Cost: an entire design nearly abandoned on the assumption that only three existed.*

### One binding beats twenty

For many tags into one component, bind the object prop once rather than binding each
key. Either an expression binding on `now(1000)` with a script transform doing
`system.tag.readBlocking`, or an expression-structure binding.

Expression-structure bindings are type `expr-struct`; the runtime config key is
`struct` with `waitOnAll`, though the Designer labels it "expressions".

*Verified: `ExpressionStructureBinding` in `perspective-gateway`, and the designer
delegate.*

### Drop bad-quality tags, do not zero them

In a read transform, omit the key when quality is bad so the consumer keeps its previous
value. Sending `0` shows a confident wrong number, for example a damper reading 0%.

---

## Views and routing

Page routes live in `com.inductiveautomation.perspective/page-config/config.json` as a
`pages` map of route to `{title, viewPath}`. A route parameter such as `/ahu/:ahuId`
arrives as `self.view.params.ahuId`, so one view can serve every instance.

*Verified: the config file in a working project.*

---

## Module SDK

### Component icons

The project browser does exactly one thing:
`descriptor.getIcon().ifPresent(this::setIcon)`. No icon means the default glyph, which
reads as a folder. Ignition's own components get theirs from a path that resolves by
component id, which module components never touch.

`ComponentDescriptorImpl.icon` is final, so it is set at build time. `InteractiveSvgIcon`
is designer scope, so referencing it from `common` breaks the gateway at class init:
expose a `descriptor(Icon)` factory, gateway passes null, designer passes the icon.

`createIcon` loads every variant eagerly and throws if `-disabled` is missing. Ship
base, `-selected` and `-disabled`. Convention is 16x16, flat fill, `#445C6D` /
`#FFF` / `#808080`.

*Verified: `javap` on `ComponentNode`, `ComponentDescriptorImpl`, and a headless load
test against the real class.*

### Declared events are static per component type

`setEvents()` is called once when the descriptor is built, so a component cannot mint a
new Perspective event per instance. Carry variation in the event payload instead.
Ignition does this itself: the Coordinate Container declares one `onPipeClicked` carrying
`{pipeName, pipeIndex, event}`, covering every pipe on the container.

There is **no Pipe component**. `ia.display.pipe` does not exist. Pipes are the `pipes`
array property on `ia.container.coord`, each a tree of points via
`origin.connections[]`, with appearance following session prop `pipes.autoAppearance`
when set to `auto`.

*Verified: `ComponentDescriptorImpl.ComponentBuilder`, and `ia.container.coord` in
`ia.components.json`. An earlier version of this file attributed the event to a
nonexistent `ia.display.pipe`.*

### Routes cannot serve arbitrary depth

`Route.pathMatches` requires the pattern and the request to have the **same number of
path segments**. Fine for a fixed endpoint, useless for a folder tree. Use a servlet via
`WebResourceManager.addServlet(name, class)`, which mounts at `/system/<name>/**`.
WebDev does the same.

`mountRouteHandlers` mounts at `/data/<module-id-or-alias>/*`; jar resources are served
at `/res/<module-id-or-alias>/*`. `onMountedResourceRequest` has an empty default body,
so it is a header hook, not a content source.

*Verified: bytecode of `Route.pathMatches`; SDK example javadoc; and `/system/webdev/`
answering on the live gateway.*

### Sandboxed iframes and ES modules

A sandbox without `allow-same-origin` gives an opaque origin, and module scripts are
always fetched with CORS. A scene using `<script type="module">` then renders nothing.
Serving `Access-Control-Allow-Origin: *` from the module's own servlet fixes it.

*Reasoned from the module-script CORS rule and consistent with observed behaviour, but
**not** independently confirmed by isolating the header. Treat as probable, not proven.*

---

## Tags

- Boolean expression tags need explicit coercion: `if(cond, 1, 0)`, not a bare
  comparison, which lands as `Error_Configuration`.
- Editing a UDT instance member needs the nested instance shape. A flat `edit_tags` call
  returns `Good` and silently does nothing.
- `{Param}` substitution resolves only in expression bindings, not in a memory tag's
  `value`.

*From `AHU_Control_Demo/local.md`, hit during a real build.*

---

## Conventions

**No em-dash or en-dash anywhere**, in view text, script strings, tag descriptions or
notes. An em-dash inside a script transform rendered as mojibake in a popup title and
had to be fixed by hand. Keep project strings ASCII where a plain character will do.
Symbols that carry meaning, degree signs and similar, are fine and do render.

---

## Environment notes

- A `402` from a WebDev endpoint is the trial licence window expiring. Restarting the
  gateway resets it. Not a code fault.
- The `ignition-mcp` project-resource REST endpoints return 404 on this gateway version.
  Writing `view.json` directly to the project folder works; the gateway picks it up on a
  project scan.
