# The #AIDriven Ignition Change Loop

The end-to-end procedure for changing an Ignition project. The gateway and its
resources run on a Windows host and are **never edited by hand** — a agent authors
resources in the repo, pushes them gateway-side through `ignition-mcp`, and verifies at
runtime. The human's only step is a rescan in the Designer.

---

## 0. Before anything — verify worktree isolation

```bash
pwd -P
git rev-parse --show-toplevel
```

Both must resolve to your **disposable task worktree**, not the primary checkout
the supervisor operates from. If it's the primary checkout, stop and report — do not write.

---

## 1. Compose the knowledge layers

| Layer | Source |
|-------|--------|
| Global standards + platform reference | load the `/ignition` skill; read the `references/**` files it indexes |
| This deployment's choices | read the the project conventions files **your brief names** |
| Gateway / fleet facts (URL, version, edition, trial-timer state, provider sizes, DB/OPC names) | **from your brief** — the supervisor folds them in |
| Intent (what to build, acceptance criteria, scope) | the brief itself |

Full model: `docs/knowledge-architecture.md`.

---

## 2. Author the resource on disk (in the repo)

- Match the on-disk format exactly — `references/gateway/resource-formats.md`
  (`resource.json` manifest, per-type payload files, page-config key is `viewPath`,
  binding JSON shape, timer-script layout, WebDev `resources/` segment).
- For Perspective, every component node must be valid against its schema —
  `references/gateway/component-schemas.md` + `schema/perspective/**`.
- **View path references are project-relative** — `templates/MetricTile`, never
  `<project>/templates/MetricTile` (`resource-formats.md` §9).
- Builders: `scripts/build_view*.py`; shared helpers: `<repo>/scripts/lib/gateway_io.py`.
- Lint is enforced automatically: the repo's pre-commit hook runs
  `skill/scripts/view_lint.py` on every staged `*/views/*/view.json` and
  blocks the commit on any finding — this is not a step to remember to run
  yourself before pushing.

---

## 3. Push to the gateway (gateway-side write + fsync)

Through `ignition-mcp` `run_gateway_script` (the golden path — `mcp-tool-map.md`). The
MCP `set_project_resource` tool is **broken on 8.3.9** — do not use it.

For **every** file (payload files first, `resource.json` last):

```python
import os
def put(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d): os.makedirs(d)
    f = open(path, "w")
    try:
        f.write(text); f.flush(); os.fsync(f.fileno())   # THE FSYNC TRAP — resource-formats.md §10
    finally:
        f.close()
```

Skipping `os.fsync()` lets the gateway's file-watcher cache a 0-byte file and that
poison **survives later rewrites**. If a resource is already poisoned, rewrite it under
a **fresh resource name**. Never `shutil.rmtree` a live resource dir — the gateway
holds file locks.

Project dir (Windows default):
`C:\Program Files\Inductive Automation\Ignition\data\projects\<project>\`

---

## 4. Trigger a rescan

```python
from com.inductiveautomation.ignition.gateway import IgnitionGateway
IgnitionGateway.get().getProjectManager().requestScan()
```

(or `system.project.requestScan()` where exposed.)

---

## 5. Verify at runtime — an HTTP 200 is NOT verification

A 200 from the write call only means the script ran. It does **not** mean the gateway
parsed and loaded the resource (see the fsync trap — the file can be on disk and still
cached as empty). Confirm one of:

**Any resource — is it in the project model?** ( — live-verified 2026-09-04)

```python
pm = IgnitionGateway.get().getProjectManager()
res = [str(r) for r in pm.find("<project>").get().getResources()]
# -> ['com.inductiveautomation.perspective/views/Dashboard', ...]
```

**Perspective — did the view/page actually parse?** ( — live-verified 2026-09-04)

```python
ctx = (IgnitionGateway.get().getModuleManager()
       .getModule("com.inductiveautomation.perspective").getHook().getContext())
pc = ctx.getProjectCache().get("<project>").get().projectConfig
views = sorted(str(k) for k in pc.views.keySet())        # Map<name, ViewConfig>
pages = sorted(str(k) for k in pc.pageConfig.pages.keySet())  # Map<mount, PageConfig>
```

If the view name is absent, or `pc.views` throws, the resource is malformed — fix and
re-scan. **Tags:** read the tag back (`system.tag.readBlocking`) and check `.quality`.
**Timer scripts:** check the gateway log for a `SyntaxError` on the handler.

`run_gateway_script` results are capped ~110 KB — for large verification dumps, write to
a workspace file and read it back in a second call.

---

## 6. Hand back

Report what's on the gateway and that the human's only step is **Project → Update /
rescan in the Designer**. The user does not develop in the Designer — never say "fix it
in the Designer", "save it in the Designer", or "re-pick the binding in the Designer".
Deliver working resources; they scan.

---

## Stop rules

| Condition | Action |
|-----------|--------|
| **HTTP 402** from any WebDev-backed call (`run_gateway_script`, tag CRUD, alarms, …) | The gateway's ~2-hour Trial timer lapsed. Append `blocked: gateway trial timer needs a reset` to the status file and **stop**. **Never** try to reset it — a human does that from the gateway's "Trial Mode" banner. Native REST reads still work if you only need gateway facts. |
| `browse_tags` on a whole large provider | Don't — it can be ~13.8k tags ( — a large production provider can hold >10k). Query narrow subtrees via `system.tag.browse("[default]<Area>/<Sub>")`. |
| Same obstacle hit twice | Report `blocked: <why>` to your supervisor and stop. |
