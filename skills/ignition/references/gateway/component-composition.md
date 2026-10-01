# Component composition: Embedded View vs docked view vs Template


Three ways Perspective reuses UI. Pick by scope, not habit.

## Decision table

| Need | Pattern | Where it lives | Example this session |
|---|---|---|---|
| Same layout, different data, used N times inside one or more views | **Embedded View** (`ia.display.view`) + `params` | A `views/<name>` resource, referenced via `props.path` + `props.params` | `msn-perspective`'s `templates/lineCard` — one card layout, embedded once per production line via `embed(name, "templates/lineCard", {...})` |
| One shared UI element every page on the project needs (nav, header, footer) | **Docked view** via `page-config/config.json`'s `sharedDocks` | Project-level `page-config/config.json`, not inside any view's own root | `common/sidebarMenu`, mounted as a `left` shared dock |
| Legacy Vision windows-with-embedded-templates pattern | **Perspective Template resource** | N/A on 8.3 — **does not exist in Perspective** | — |

## Embedded View + params

A view (e.g. `templates/lineCard`) declares `params` (View → Configure View). A
parent view embeds it with `ia.display.view`:

```python
{"type": "ia.display.view", "version": 0,
 "props": {"path": "templates/lineCard", "params": {"lineId": "L1"},
           "useDefaultViewWidth": False, "useDefaultViewHeight": False},
 "meta": {"name": "line_L1"}, "position": {}}
```

`view_lint.py` already checks every `params` key passed here against the target
view's declared `params` (the appHeader/breadcrumb bug class — see its module
docstring). Use Embedded View whenever the same layout repeats 3+ times with
different bound data (`13-TEMPLATES-REUSE.md`'s "golden rule": 3+ repeats → template).

## Docked view + page-config

A project-level shared dock is **not** an embed inside a view's own root — it is an
entry in `page-config/config.json`'s `sharedDocks.{top,bottom,left,right}` array,
each `{anchor, autoBreakpoint, content, handle, iconUrl, id, modal, resizable, show,
size, viewParams, viewPath}` (live-verified shape).

**Never embed a view that is also referenced by `sharedDocks`, and never delete a
docked view without removing every reference first** — a dangling `sharedDocks`
entry or embed breaks `getProject`/project-diff for *every route*,
same failure class as a bad `events` shape (§perspective-events.md) but a different
cause: a missing resource, not a malformed JSON key.

Use a docked view for anything that must appear identically on every page without
being wired into each view's own tree — sidebar nav, a global header, a status bar.

## Perspective Template resource: does not apply on 8.3

Confirmed against `references/ignition-8-3/vision-module.md` [M]: `Template`,
`Template Repeater`, and `Template Canvas` are **Vision-module concepts only**. The
verified, install-derived Perspective component inventory
(`deep/perspective-schema-truth.md`, all 82 shipped components) contains zero
`Template`-family component. Perspective's answer to "Vision Template" is the
**Embedded View** — do not look for, or try to author, a Perspective "Template"
resource; it is not a thing on this platform version.

## See also

- `perspective-events.md` — event wiring inside whichever pattern you pick.
