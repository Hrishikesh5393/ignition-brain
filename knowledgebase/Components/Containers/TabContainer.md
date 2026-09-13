> **Component category:** Containers · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

# Tab Container

**Category:** Container / Layout | **Ignition:** ia.container.tab

## Properties

| Property Name | Type | Default | Purpose |
|---|---|---|---|
| tabs | array | 1 tab | Defines the tabs themselves. Each element is an object: `{text, viewPath, viewParams, runWhileHidden, disabled}`. Adding an element to this array renders an additional tab. |
| currentTabIndex | numeric | 0 | Index into `tabs` of the currently active/selected tab. Read/write — can be set programmatically or via binding to switch tabs. |
| menuType | string | "classic" | `classic` — traditional boxed-tab menu. `modern` — borderless, active tab indicated with an underline. |
| tabSize | object | {width: null, height: 32} | Default size allotted to a single tab: `{width, height}` in pixels |
| menuStyle | object | {} | Style block for the tab menu bar itself (text, background, padding, border) |
| contentStyle | object | {} | Style block for the content frame that displays the active tab's content |
| tabStyle.active | object | {} | Style overrides applied only to the currently selected tab |
| tabStyle.inactive | object | {} | Style overrides applied to all non-selected tabs |
| style | object | {} | General component-level style |

## Tabs Array Structure

```python
tabs = [
    {
        "text": "Overview",           # label shown on the tab
        "viewPath": None,             # optional: path to an embedded view to load instead of an inline child
        "viewParams": {},             # params passed to the embedded view, if viewPath is set
        "runWhileHidden": False,      # if True, tab content loads on first activation and stays alive in the background (8.1.5+)
        "disabled": False,            # if True, tab cannot be selected/clicked (8.1.20+)
    },
    {"text": "Details"},
    {"text": "History", "disabled": True},
]
currentTabIndex = 0   # "Overview" tab active
```

## Child Component Properties

Tab Container has no documented dedicated `position.*` linking property for direct children the way other containers do — content association is handled one of two ways:

1. **Embedded view per tab** (recommended for anything non-trivial): set `tabs[i].viewPath` and `tabs[i].viewParams` — the tab's content is a whole separate view, loaded/unloaded (or kept alive if `runWhileHidden: true`) as the tab activates.
2. **Direct inline children**, matched to tabs by declaration order matching the `tabs` array order (one root child component per tab entry) — used for very simple single-component tab content.

## Responsive Configuration Example

```python
# Modern, underline-style tabs, sized to fill available width
menuType = "modern"
tabSize.height = 40
tabStyle.active.textStyle.fontWeight = "600"

tabs = [
    {"text": "Overview", "viewPath": "Dashboards/Overview", "runWhileHidden": True},
    {"text": "Details",  "viewPath": "Dashboards/Details"},
    {"text": "Alarms",   "viewPath": "Dashboards/Alarms", "disabled": {"expr": "!{session.props.auth.roles} ? true : {'admin' in session.props.auth.roles} == false"}},
]
```

## Layout Example

```python
# Manage tabs and bind active selection to a shared session/view param
props.tabs = [
    {"text": "Overview", "viewPath": "Views/Overview"},
    {"text": "Details",  "viewPath": "Views/Details"},
]
props.currentTabIndex = 0   # bind this to a param/tag to drive tab selection programmatically

# Switch tabs from a script (e.g. a button's onActionPerformed):
def runAction(self, event):
	self.getSibling("TabContainer").props.currentTabIndex = 1
```

## Common Gotchas

- **`currentTabIndex` is 0-based**, not 1-based — off-by-one is the most common bug when wiring an external nav control to a Tab Container.
- **Inactive tabs are unloaded by default.** Unless `runWhileHidden: true` is set per-tab, switching away from a tab tears down its component tree — any client-side script state or unsaved form input in that tab is lost when the user tabs away and back. Set `runWhileHidden` on any tab holding live user input you need to preserve.
- **`disabled` (8.1.20+) prevents selection but still renders the tab visibly** — pair it with a style override (`tabStyle.inactive`) if you want a stronger "unavailable" visual cue, disabling alone doesn't gray it out automatically in all themes.
- **Prefer `viewPath` over direct inline children** for anything beyond a couple of simple components — it keeps each tab's content independently maintainable and reusable, and is required if the same tab content needs to be reused elsewhere in the project.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [11-COMPONENTS-PALETTES](../../11-COMPONENTS-PALETTES.md), [13-TEMPLATES-REUSE](../../13-TEMPLATES-REUSE.md), [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
