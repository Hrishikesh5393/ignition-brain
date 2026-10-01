#!/usr/bin/env python3
"""scout.py - decode an existing Ignition project into a machine-readable map.

Deterministic, stdlib only, no LLM. Three loaders feed one extractor:
  --live NAME      live gateway, read-only REST export (env: IGNITION_URL + IGNITION_API_KEY)
  --zip  FILE      project export .zip
  --gwbk FILE      gateway backup .gwbk (a zip; projects live under projects/<name>/)

Output folder (default ./scout-report):
  map.json       full machine-readable map (input for Forge / Playbook)
  inventory.md   tables of everything found
  patterns.md    patterns used, with counts and examples (input for Playbook)

  python3 scout.py --zip MyProject.zip --name MyProject -o out/
  python3 scout.py --live MyProject -o out/
  python3 scout.py --gwbk backup.gwbk --project MyProject -o out/
  python3 scout.py --diff out1/map.json out2/map.json      # 0 = same, 1 = differ

Exit codes: 0 ok, 2 usage/input error, 3 gateway HTTP 402 (trial lapsed: report and stop).
"""
import argparse
import collections
import gzip
import io
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

SCOUT_VERSION = 1
PERSP = "com.inductiveautomation.perspective"
TAG_RE = re.compile(r"(?<![\w)\]])\[([A-Za-z_][\w.\-]*)\]((?:[\w\-./]|(?<=\w) (?=\w))+)")
API_RE = re.compile(r"\bsystem\.[a-z]+\.[A-Za-z_]\w*")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
VAR_RE = re.compile(r"var\(--[\w-]+\)")
BLOCK_RE = re.compile(r"com\.inductiveautomation\.(\w+BlockFactory)")
DEF_RE = re.compile(r"^def\s+(\w+)\s*\(", re.M)
VIEW_TYPES_WITH_PATH = ("ia.display.view", "ia.container.flex-repeater", "ia.display.flex-repeater")


class ScoutError(Exception):
    pass


# --------------------------------------------------------------------------- loaders
def _strip_common_root(names):
    """Prefix of the dir that holds project.json (export zip: '', gwbk: 'projects/<n>/')."""
    roots = sorted(n[: -len("project.json")] for n in names if n.endswith("project.json"))
    return roots


def _files_from_zip(zf, prefix):
    out = {}
    for info in zf.infolist():
        if info.is_dir() or not info.filename.startswith(prefix):
            continue
        out[info.filename[len(prefix):]] = zf.read(info.filename)
    return out


def load_zip(path, name=None):
    with zipfile.ZipFile(path) as zf:
        roots = _strip_common_root(zf.namelist())
        if "" in roots:
            root = ""
        elif len(roots) == 1:
            root = roots[0]
        else:
            raise ScoutError("no project.json at zip root (is this a project export?)")
        files = _files_from_zip(zf, root)
    default = os.path.splitext(os.path.basename(path))[0]
    return {"kind": "zip", "ref": os.path.basename(path), "name": name or default,
            "files": files, "gateway_meta": {}}


def load_gwbk(path, project=None):
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        projects = sorted({m.group(1) for n in names
                           for m in [re.match(r"(?:.*/)?projects/([^/]+)/project\.json$", n)] if m})
        if not projects:
            raise ScoutError("no projects/<name>/project.json in backup (is this a .gwbk?)")
        if not project:
            raise ScoutError("--project required; backup holds: " + ", ".join(projects))
        if project not in projects:
            raise ScoutError("project %r not in backup; has: %s" % (project, ", ".join(projects)))
        pj = [n for n in names if re.match(r"(?:.*/)?projects/%s/project\.json$" % re.escape(project), n)][0]
        files = _files_from_zip(zf, pj[: -len("project.json")])
    return {"kind": "gwbk", "ref": os.path.basename(path), "name": project,
            "files": files, "gateway_meta": {}}


def _http(url, key, verify, timeout=120):
    req = urllib.request.Request(url, headers={"X-Ignition-API-Token": key})
    ctx = None if verify else ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:  # GET only: read-only
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 402:
            print("HTTP 402: gateway trial timer lapsed - report to supervisor and stop.", file=sys.stderr)
            sys.exit(3)
        raise ScoutError("GET %s -> HTTP %s" % (url, e.code))
    except urllib.error.URLError as e:
        raise ScoutError("GET %s failed: %s" % (url, e.reason))


def load_live(project, url=None, key=None, verify=True):
    url = (url or os.environ.get("IGNITION_URL") or os.environ.get("IGNITION_MCP_IGNITION_GATEWAY_URL") or "").rstrip("/")
    key = key or os.environ.get("IGNITION_API_KEY") or os.environ.get("IGNITION_MCP_IGNITION_API_KEY")
    if os.environ.get("IGNITION_MCP_SSL_VERIFY", "").lower() == "false":
        verify = False
    if not url or not key:
        raise ScoutError("set IGNITION_URL and IGNITION_API_KEY (or pass --url / --api-key)")
    base = url + "/data/api/v1/projects/"
    meta = {}
    try:
        listing = json.loads(_http(base + "list", key, verify))
        meta = next((p for p in listing.get("items", []) if p.get("name") == project), {})
    except (ScoutError, ValueError):
        pass  # metadata is a bonus; the export below is the real input
    data = _http(base + "export/" + urllib.parse.quote(project, safe=""), key, verify)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        files = _files_from_zip(zf, "")
    return {"kind": "live", "ref": project, "name": project, "files": files, "gateway_meta": meta}


# --------------------------------------------------------------------------- helpers
def jload(b):
    try:
        return json.loads(b.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError):
        return None


def utext(b):
    return b.decode("utf-8", "replace")


def gunzip_text(b):
    try:
        return gzip.decompress(b).decode("utf-8", "replace")
    except (OSError, EOFError):
        return utext(b)


def strings(obj):
    """Yield every string in a JSON structure."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def tag_refs(text):
    for m in TAG_RE.finditer(text):
        if m.group(1) in ("True", "False", "None"):
            continue
        yield "[%s]%s" % (m.group(1), m.group(2).rstrip("/."))


def as_list(x):
    return x if isinstance(x, list) else ([] if x is None else [x])


def case_style(s):
    if re.fullmatch(r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)*", s):
        return "PascalCase"
    if re.fullmatch(r"[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*)+", s):
        return "camelCase"
    if re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)+", s):
        return "snake_case"
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", s):
        return "kebab-case"
    if re.fullmatch(r"[a-z0-9]+", s):
        return "lowercase"
    return "other"


def top(counter, n=8):
    return [[k, v] for k, v in sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))[:n]]


# --------------------------------------------------------------------------- extractor
def split_resources(files):
    """{resource_key: {file: bytes}} where key = module/type[/name...]; skips project.json."""
    dirs = collections.defaultdict(dict)
    for path, data in files.items():
        if path == "project.json":
            continue
        d, _, f = path.rpartition("/")
        dirs[d][f] = data
    return {d: fs for d, fs in dirs.items() if "resource.json" in fs}


def walk_components(node, cpath, visit):
    visit(node, cpath)
    for i, ch in enumerate(node.get("children") or []):
        name = (ch.get("meta") or {}).get("name") or "%s[%d]" % (ch.get("type", "?"), i)
        walk_components(ch, cpath + "/" + name, visit)


def analyse_view(name, vj):
    root = vj.get("root") or {}
    info = {"root_type": root.get("type"), "params": sorted((vj.get("params") or {}).keys()),
            "custom": sorted((vj.get("custom") or {}).keys()),
            "default_size": (vj.get("props") or {}).get("defaultSize"),
            "components": 0, "types": collections.Counter(), "bindings": collections.Counter(),
            "transforms": collections.Counter(), "embeds": [], "popups": [], "navs": [],
            "events": collections.Counter(), "tags": set(), "queries": set(), "style_classes": set(),
            "inline_styles": 0, "hex_colors": 0, "css_vars": 0, "scripts": [], "message_handlers": [],
            "api_calls": collections.Counter(), "binding_list": [], "component_names": []}
    text_all = []

    def note_binding(cpath, prop, b):
        bd = b.get("binding") or {}
        t = bd.get("type", "?")
        cfg = bd.get("config") or {}
        info["bindings"][t] += 1
        item = {"component": cpath, "prop": prop, "type": t}
        if t == "tag":
            item["tagPath"] = cfg.get("tagPath")
            item["mode"] = cfg.get("mode", "direct")
            info["tags"].add(cfg.get("tagPath") or "")
            for r in (cfg.get("references") or {}).values():
                info["tags"].add(str(r))
        elif t == "expr":
            item["expression"] = cfg.get("expression")
        elif t == "property":
            item["path"] = cfg.get("path")
        elif t == "query":
            item["queryPath"] = cfg.get("queryPath")
            info["queries"].add(cfg.get("queryPath") or "")
            item["polling"] = bool((cfg.get("polling") or {}).get("enabled"))
        elif t == "tag-history":
            for tg in cfg.get("tags") or []:
                info["tags"].add(tg.get("path") if isinstance(tg, dict) else str(tg))
        for tr in bd.get("transforms") or []:
            info["transforms"][tr.get("type", "?")] += 1
            if tr.get("type") == "script":
                info["scripts"].append({"where": cpath + ":" + prop, "kind": "transform", "code": tr.get("code", "")})
        if len(info["binding_list"]) < 5000:
            info["binding_list"].append(item)

    def visit(c, cpath):
        info["components"] += 1
        ctype = c.get("type", "?")
        info["types"][ctype] += 1
        nm = (c.get("meta") or {}).get("name")
        if nm:
            info["component_names"].append(nm)
        props = c.get("props") or {}
        st = props.get("style") or {}
        for cl in str(st.get("classes", "")).split():
            info["style_classes"].add(cl)
        if isinstance(st, dict) and any(k != "classes" for k in st):
            info["inline_styles"] += 1
        if ctype in VIEW_TYPES_WITH_PATH or ("path" in props and "view" in ctype):
            if props.get("path"):
                info["embeds"].append({"path": props["path"], "component": cpath, "type": ctype,
                                       "params": sorted((props.get("params") or {}).keys())})
        for v in as_list(props.get("views")):  # view canvas
            if isinstance(v, dict) and v.get("viewPath"):
                info["embeds"].append({"path": v["viewPath"], "component": cpath, "type": ctype, "params": []})
        for tab in as_list(props.get("tabs")):  # tab container may carry view refs
            if isinstance(tab, dict) and isinstance(tab.get("view"), str):
                info["embeds"].append({"path": tab["view"], "component": cpath, "type": ctype, "params": []})
        for prop, b in (c.get("propConfig") or {}).items():
            if isinstance(b, dict) and "binding" in b:
                note_binding(cpath, prop, b)
        for dom, evs in (c.get("events") or {}).items():
            if not isinstance(evs, dict):
                continue
            for evname, acts in evs.items():
                for a in as_list(acts):
                    if not isinstance(a, dict):
                        continue
                    at, sc = a.get("type", "?"), a.get("scope", "?")
                    info["events"]["%s.%s:%s/%s" % (dom, evname, at, sc)] += 1
                    cfg = a.get("config") or {}
                    if at == "script":
                        info["scripts"].append({"where": cpath + ":" + evname, "kind": "event", "code": cfg.get("script", "")})
                    elif at == "popup":
                        info["popups"].append({"viewPath": cfg.get("viewPath") or cfg.get("id"), "component": cpath,
                                               "params": sorted((cfg.get("viewParams") or {}).keys()),
                                               "modal": cfg.get("modal")})
                    elif at == "nav":
                        info["navs"].append({"target": cfg.get("page") or cfg.get("url") or cfg.get("viewPath"), "component": cpath})
        sc = c.get("scripts") or {}
        for mh in as_list(sc.get("messageHandlers")):
            if isinstance(mh, dict):
                info["message_handlers"].append({"messageType": mh.get("messageType"), "component": cpath,
                                                 "scope": {k: mh.get(k) for k in ("pageScope", "sessionScope", "viewScope") if k in mh}})
                info["scripts"].append({"where": cpath + ":msg:" + str(mh.get("messageType")), "kind": "message-handler", "code": mh.get("script", "")})
        for cm in as_list(sc.get("customMethods")):
            if isinstance(cm, dict):
                info["scripts"].append({"where": cpath + ":method:" + str(cm.get("name")), "kind": "custom-method", "code": cm.get("script", "")})
        cust = c.get("custom")
        if cust:
            info.setdefault("component_custom", []).append(cpath)

    walk_components(root, name, visit)
    for k, b in (vj.get("propConfig") or {}).items():  # view-level bindings
        if isinstance(b, dict) and "binding" in b:
            note_binding("<view>", k, b)
    blob = json.dumps(vj)
    for s in strings(vj):
        for r in tag_refs(s):
            info["tags"].add(r)
        for a in API_RE.findall(s):
            info["api_calls"][a] += 1
    info["hex_colors"] = len(HEX_RE.findall(blob))
    info["css_vars"] = len(VAR_RE.findall(blob))
    info["tags"] = sorted(t for t in info["tags"] if t)
    info["queries"] = sorted(q for q in info["queries"] if q)
    info["style_classes"] = sorted(info["style_classes"])
    return info


def extract(src):
    files = src["files"]
    proj = jload(files.get("project.json", b"{}")) or {}
    res = split_resources(files)
    m = {"scout_version": SCOUT_VERSION,
         "source": {"kind": src["kind"], "ref": src["ref"]},
         "project": {"name": src["name"], "title": proj.get("title", ""), "description": proj.get("description", ""),
                     "enabled": proj.get("enabled"), "inheritable": proj.get("inheritable"), "parent": proj.get("parent", ""),
                     "gateway": {k: src["gateway_meta"][k] for k in ("userSource", "identityProvider", "tagProvider", "defaultDb")
                                 if k in src["gateway_meta"]}}}
    # -- resource inventory
    resources, counts = [], collections.Counter()
    for d in sorted(res):
        parts = d.split("/")
        resources.append(d)
        counts["/".join(parts[:2])] += 1
    m["resources"] = resources
    m["resource_counts"] = dict(sorted(counts.items()))

    def of(prefix):
        p = prefix.rstrip("/") + "/"
        return {d[len(p):]: fs for d, fs in res.items() if d.startswith(p)}

    # -- pages / docks
    pc = {}
    if PERSP + "/page-config" in res:
        pc = jload(res[PERSP + "/page-config"].get("config.json", b"{}")) or {}
    pages = []
    for route, p in sorted((pc.get("pages") or {}).items()):
        pages.append({"route": route, "viewPath": p.get("viewPath"), "title": p.get("title"),
                      "path_params": re.findall(r":(\w+)", route), "docks": p.get("docks")})
    m["pages"] = pages
    docks = []
    for anchor, arr in sorted((pc.get("sharedDocks") or {}).items()):
        for d in as_list(arr) if isinstance(arr, list) else []:
            docks.append({"anchor": anchor, "id": d.get("id"), "viewPath": d.get("viewPath"), "size": d.get("size"),
                          "show": d.get("show"), "handle": d.get("handle"), "modal": d.get("modal"),
                          "content": d.get("content"), "viewParams": sorted((d.get("viewParams") or {}).keys())})
    m["docks"] = docks

    # -- views
    view_res = of(PERSP + "/views")
    views, vinfo = {}, {}
    for vname in sorted(view_res):
        vj = jload(view_res[vname].get("view.json", b""))
        if vj is None:
            views[vname] = {"error": "unparseable view.json"}
            continue
        vinfo[vname] = analyse_view(vname, vj)
    known = set(vinfo)
    embed_tree, embedded_by, popup_targets = {}, collections.defaultdict(set), collections.defaultdict(set)
    for vn, i in vinfo.items():
        embed_tree[vn] = sorted({e["path"] for e in i["embeds"]})
        for e in i["embeds"]:
            embedded_by[e["path"]].add(vn)
        for p in i["popups"]:
            if p["viewPath"]:
                popup_targets[p["viewPath"]].add(vn)
    page_views = {p["viewPath"] for p in pages}
    dock_views = {d["viewPath"] for d in docks}
    for vn, i in sorted(vinfo.items()):
        views[vn] = {
            "root_type": i["root_type"], "default_size": i["default_size"], "params": i["params"], "custom": i["custom"],
            "components": i["components"], "component_types": dict(sorted(i["types"].items())),
            "bindings": dict(sorted(i["bindings"].items())), "transforms": dict(sorted(i["transforms"].items())),
            "events": dict(sorted(i["events"].items())),
            "embeds": sorted(i["embeds"], key=lambda e: (e["path"], e["component"])),
            "embedded_by": sorted(embedded_by.get(vn, [])),
            "popups": sorted(i["popups"], key=lambda e: (str(e["viewPath"]), e["component"])),
            "popup_target_of": sorted(popup_targets.get(vn, [])),
            "navs": sorted(i["navs"], key=lambda e: (str(e["target"]), e["component"])),
            "tags": i["tags"], "queries": i["queries"], "style_classes": i["style_classes"],
            "inline_style_components": i["inline_styles"], "hex_colors": i["hex_colors"], "css_vars": i["css_vars"],
            "api_calls": dict(sorted(i["api_calls"].items())), "inline_scripts": len(i["scripts"]),
            "role": [r for r, ok in (("page", vn in page_views), ("dock", vn in dock_views),
                                     ("popup", vn in popup_targets), ("embedded", vn in embedded_by)) if ok] or ["unreferenced"],
        }
    m["views"] = views
    m["embed_tree"] = {"edges": embed_tree,
                       "roots": sorted(v for v in known if v in page_views or v in dock_views),
                       "missing_targets": sorted({e["path"] for i in vinfo.values() for e in i["embeds"]} - known),
                       "unreferenced": sorted(v for v in known if views[v]["role"] == ["unreferenced"])}
    m["broken_refs"] = {
        "pages": sorted(p["viewPath"] for p in pages if p["viewPath"] not in known),
        "docks": sorted(d["viewPath"] for d in docks if d["viewPath"] not in known),
        "popups": sorted(t for t in popup_targets if t not in known),
        "queries": [],
    }

    # -- bindings by type
    bt = collections.Counter()
    tr = collections.Counter()
    for i in vinfo.values():
        bt.update(i["bindings"])
        tr.update(i["transforms"])
    blist = {}
    for vn, i in sorted(vinfo.items()):
        for b in i["binding_list"]:
            blist.setdefault(b["type"], []).append(dict(b, view=vn))
    m["bindings"] = {"by_type": dict(sorted(bt.items())), "transforms": dict(sorted(tr.items())),
                     "examples": {t: v[:5] for t, v in sorted(blist.items())},
                     "tag_binding_modes": dict(collections.Counter(b.get("mode") for b in blist.get("tag", [])))}

    # -- scripts by scope
    scripts = {"project_library": [], "gateway_events": [], "view_inline": {}, "api_calls": {}}
    api = collections.Counter()
    for name, fs in sorted(of("ignition/script-python").items()):
        code = utext(fs.get("code.py", b""))
        scripts["project_library"].append({"name": name, "functions": DEF_RE.findall(code), "lines": code.count("\n") + 1})
        api.update(API_RE.findall(code))
    ev_types = collections.defaultdict(list)
    handlers = []
    for d in sorted(res):
        parts = d.split("/")
        if parts[0] == "ignition" and len(parts) > 2 and parts[1] not in ("script-python", "named-query", "global-props"):
            fs = res[d]
            attrs = (jload(fs["resource.json"]) or {}).get("attributes", {})
            code = "\n".join(utext(b) for f, b in sorted(fs.items()) if f.endswith(".py"))
            api.update(API_RE.findall(code))
            entry = {"type": parts[1], "name": "/".join(parts[2:]),
                     "files": sorted(f for f in fs if f != "resource.json"),
                     "attributes": {k: v for k, v in attrs.items() if not k.startswith("lastModification")},
                     "functions": DEF_RE.findall(code),
                     "tags_referenced": sorted(set(tag_refs(code)))}
            scripts["gateway_events"].append(entry)
            ev_types[parts[1]].append(entry["name"])
            if parts[1] in ("message", "message-handler"):
                handlers.append({"scope": "gateway", "messageType": attrs.get("messageType") or entry["name"], "name": entry["name"]})
    scripts["gateway_event_types"] = {k: sorted(v) for k, v in sorted(ev_types.items())}
    for vn, i in sorted(vinfo.items()):
        by = collections.Counter(s["kind"] for s in i["scripts"])
        if by:
            scripts["view_inline"][vn] = dict(by)
        api.update(i["api_calls"])
        for mh in i["message_handlers"]:
            handlers.append({"scope": "view", "messageType": mh["messageType"], "name": mh["component"]})
    # inline api use inside view scripts is already in i['api_calls'] via strings(); library counted above
    scripts["api_calls"] = dict(sorted(api.items()))
    m["scripts"] = scripts
    m["message_handlers"] = sorted(handlers, key=lambda h: (h["scope"], str(h["messageType"]), h["name"]))

    # -- named queries
    nq_names = set()
    nqs = []
    used = collections.defaultdict(set)
    for vn, i in vinfo.items():
        for q in i["queries"]:
            used[q].add(vn)
    for name, fs in sorted(of("ignition/named-query").items()):
        attrs = (jload(fs["resource.json"]) or {}).get("attributes", {})
        sql = utext(fs.get("query.sql", b""))
        nq_names.add(name)
        nqs.append({"name": name, "type": attrs.get("type"), "database": attrs.get("database"),
                    "enabled": attrs.get("enabled"), "parameters": [p.get("identifier") for p in attrs.get("parameters", []) if isinstance(p, dict)],
                    "caching": attrs.get("cacheEnabled"), "sql_lines": sql.count("\n") + 1 if sql else 0,
                    "tables": sorted(set(re.findall(r"(?i)\b(?:from|join|into|update)\s+([\w.\"]+)", sql))),
                    "used_by_views": sorted(used.get(name, []))})
    m["named_queries"] = nqs
    m["broken_refs"]["queries"] = sorted(q for q in used if q not in nq_names)

    # -- tags referenced
    tagmap = collections.defaultdict(set)
    for vn, i in vinfo.items():
        for t in i["tags"]:
            tagmap[t].add(vn)
    for s in scripts["gateway_events"]:
        for t in s["tags_referenced"]:
            tagmap[t].add("gateway:%s/%s" % (s["type"], s["name"]))
    for name, fs in sorted(of("ignition/script-python").items()):
        for t in tag_refs(utext(fs.get("code.py", b""))):
            tagmap[t].add("library:" + name)
    for name, fs in sorted(of("com.inductiveautomation.eventstream/event-streams").items()):
        cj = jload(fs.get("config.json", b"")) or {}
        for s in strings(cj):
            for t in tag_refs(s):
                tagmap[t].add("eventstream:" + name)
    provs = collections.Counter()
    tags = []
    for t, by in sorted(tagmap.items()):
        pm = re.match(r"\[([^\]]+)\]", t)
        if pm:
            provs[pm.group(1)] += 1
        tags.append({"path": t, "provider": pm.group(1) if pm else None, "indirect": "{" in t, "used_by": sorted(by)})
    m["tags"] = {"providers": dict(sorted(provs.items())), "referenced": tags,
                 "note": "Tag/UDT definitions live in the tag provider, not the project; export them separately (get_tag_config / tag export)."}

    # -- alarms
    pipelines = []
    for name, fs in sorted(of("com.inductiveautomation.alarm-notification/alarm-pipelines").items()):
        txt = gunzip_text(fs.get("data.bin", b""))
        pipelines.append({"name": name, "blocks": dict(sorted(collections.Counter(BLOCK_RE.findall(txt)).items()))})
    alarm_comps = collections.Counter()
    for i in vinfo.values():
        for t, n in i["types"].items():
            if "alarm" in t:
                alarm_comps[t] += n
    m["alarms"] = {"pipelines": pipelines, "alarm_components": dict(sorted(alarm_comps.items())),
                   "api_calls": {k: v for k, v in scripts["api_calls"].items() if k.startswith("system.alarm")},
                   "note": "Per-tag alarm config lives on tags (tag provider), not in the project."}

    # -- other resources (event streams, reports, vision, ...)
    other = collections.defaultdict(list)
    known_types = {PERSP + "/views", PERSP + "/page-config", PERSP + "/session-props", PERSP + "/style-classes",
                   "ignition/script-python", "ignition/named-query", "com.inductiveautomation.alarm-notification/alarm-pipelines"}
    for d in sorted(res):
        t = "/".join(d.split("/")[:2])
        if t in known_types or (d.split("/")[0] == "ignition" and d.count("/") >= 2 and d.split("/")[1] != "global-props"):
            continue
        other[t].append(d[len(t) + 1:])
    es = []
    for name, fs in sorted(of("com.inductiveautomation.eventstream/event-streams").items()):
        cj = jload(fs.get("config.json", b"")) or {}
        es.append({"name": name, "enabled": cj.get("enabled"), "source": (cj.get("source") or {}).get("type"),
                   "handlers": [h.get("type") for h in cj.get("handlers", []) if isinstance(h, dict)]})
    m["other_resources"] = {"by_type": {k: v for k, v in sorted(other.items())}, "event_streams": es}

    # -- session / params / theme / style
    sp = {}
    if PERSP + "/session-props" in res:
        sp = jload(res[PERSP + "/session-props"].get("props.json", b"{}")) or {}
    sprops = sp.get("props") or {}
    style_res = of(PERSP + "/style-classes")
    classes_defined = sorted(style_res)
    used_cls = collections.Counter()
    for i in vinfo.values():
        used_cls.update(i["style_classes"])
    inline = sum(i["inline_styles"] for i in vinfo.values())
    m["params"] = {
        "session": {"custom": sorted((sp.get("custom") or {}).keys()),
                    "props_set": {k: v for k, v in sorted(sprops.items()) if v not in ({}, [], "", None)}},
        "view_params": {vn: i["params"] for vn, i in sorted(vinfo.items()) if i["params"]},
        "view_custom": {vn: i["custom"] for vn, i in sorted(vinfo.items()) if i["custom"]},
        "page_path_params": {p["route"]: p["path_params"] for p in pages if p["path_params"]},
        "embed_param_keys": {vn: sorted({k for e in i["embeds"] for k in e["params"]}) for vn, i in sorted(vinfo.items())
                             if any(e["params"] for e in i["embeds"])},
    }
    hex_total = sum(i["hex_colors"] for i in vinfo.values())
    var_total = sum(i["css_vars"] for i in vinfo.values())
    style_blob = " ".join(utext(fs.get("style.json", b"")) for fs in style_res.values())
    m["theme"] = {"session_theme": sprops.get("theme"),
                  "style_classes_defined": classes_defined,
                  "style_classes_used": dict(top(used_cls, 50)),
                  "style_classes_unused": sorted(set(classes_defined) - set(k.replace("/", "/") for k in used_cls)),
                  "css_vars_in_views": var_total, "css_vars_in_classes": len(VAR_RE.findall(style_blob)),
                  "hex_colors_in_views": hex_total, "hex_colors_in_classes": len(HEX_RE.findall(style_blob)),
                  "components_with_inline_style": inline,
                  "themes_resources": sorted(d for d in res if d.startswith(PERSP + "/themes"))}

    # -- conventions
    vnames = list(vinfo)
    segs = [s for v in vnames for s in v.split("/")]
    leafs = [v.split("/")[-1] for v in vnames]
    cnames = [n for i in vinfo.values() for n in i["component_names"]]
    tpaths = [t["path"] for t in tags if not t["indirect"]]
    sufs = collections.Counter(re.search(r"[-_]([a-z]{1,4})$", p.split("/")[-1]).group(1) for p in tpaths if re.search(r"[-_]([a-z]{1,4})$", p.split("/")[-1]))
    m["conventions"] = {
        "view_leaf_case": dict(top(collections.Counter(case_style(s) for s in leafs))),
        "view_folders": sorted({v.rsplit("/", 1)[0] for v in vnames if "/" in v}),
        "view_top_folders": dict(top(collections.Counter(v.split("/")[0] for v in vnames if "/" in v), 20)),
        "component_name_case": dict(top(collections.Counter(case_style(n) for n in cnames))),
        "component_name_count": len(cnames),
        "route_shape": dict(top(collections.Counter(("root" if p["route"] == "/" else "/" + p["route"].strip("/").split("/")[0]) for p in pages), 20)),
        "named_query_folders": sorted({q["name"].rsplit("/", 1)[0] for q in nqs if "/" in q["name"]}),
        "script_library_names": [s["name"] for s in scripts["project_library"]],
        "style_class_prefixes": dict(top(collections.Counter(c.split("/")[0] for c in classes_defined), 10)),
        "tag_leaf_suffixes": dict(top(sufs, 10)),
        "tag_path_depths": dict(top(collections.Counter(p.split("]", 1)[-1].count("/") + 1 for p in tpaths), 10)),
        "view_segments_count": len(set(segs)),
    }
    m["patterns"] = derive_patterns(m, vinfo)
    return m


def derive_patterns(m, vinfo):
    P = []

    def add(pid, title, count, examples, note=""):
        if count:
            P.append({"id": pid, "title": title, "count": count, "examples": examples[:4], "note": note})

    views = m["views"]
    bt = m["bindings"]["by_type"]
    ex = m["bindings"]["examples"]
    modes = m["bindings"]["tag_binding_modes"]
    alltag = [b for i in vinfo.values() for b in i["binding_list"] if b["type"] == "tag"]
    add("binding.tag.direct", "Tag binding, fixed path", modes.get("direct", 0), [b["tagPath"] for b in alltag if b.get("mode") == "direct"])
    add("binding.tag.indirect", "Tag binding, indirect (path from view param)", modes.get("indirect", 0), [b["tagPath"] for b in alltag if b.get("mode") == "indirect"], "template views take an instance path param")
    add("binding.expr", "Expression binding", bt.get("expr", 0), [b.get("expression") for b in ex.get("expr", [])])
    add("binding.property", "Property binding (view.params/custom -> component)", bt.get("property", 0), [b.get("path") for b in ex.get("property", [])])
    add("binding.query", "Named-query binding", bt.get("query", 0), [b.get("queryPath") for b in ex.get("query", [])])
    add("binding.tag-history", "Tag-history binding", bt.get("tag-history", 0), [b["view"] + ":" + b["prop"] for b in ex.get("tag-history", [])])
    tr = m["bindings"]["transforms"]
    add("transform.script", "Script transform on a binding", tr.get("script", 0), [])
    add("transform.expression", "Expression transform on a binding", tr.get("expression", 0), [])
    add("transform.other", "Other transforms (map/format/...)", sum(v for k, v in tr.items() if k not in ("script", "expression")), [k for k in tr if k not in ("script", "expression")])
    n_tpl = sorted(v for v, i in views.items() if i.get("embedded_by") and i.get("params"))
    add("view.template", "Parameterised view embedded elsewhere (template)", len(n_tpl), n_tpl, "reuse via view params")
    multi = sorted(v for v, i in views.items() if len(i.get("embedded_by", [])) > 1 or sum(1 for w in views.values() for e in w.get("embeds", []) if e["path"] == v) > 1)
    add("view.embed.reused", "View embedded more than once", len(multi), multi)
    add("nav.shared-docks", "Shared docks (page chrome)", len(m["docks"]), ["%s:%s" % (d["anchor"], d["viewPath"]) for d in m["docks"]])
    pop = sorted({p["viewPath"] for v in views.values() for p in v.get("popups", []) if p["viewPath"]})
    add("view.popup", "Popup views opened from events", len(pop), pop)
    add("event.nav", "Navigation from a component event", sum(len(v.get("navs", [])) for v in views.values()), [n["target"] for v in views.values() for n in v.get("navs", [])])
    evc = collections.Counter()
    for v in views.values():
        evc.update(v.get("events", {}))
    for k, n in sorted(evc.items()):
        add("event." + k.replace(":", ".").replace("/", "."), "Component event %s" % k, n, [k])
    add("script.project-library", "Project script library modules", len(m["scripts"]["project_library"]), [s["name"] for s in m["scripts"]["project_library"]])
    for t, names in m["scripts"]["gateway_event_types"].items():
        add("script.gateway." + t, "Gateway %s script" % t, len(names), names)
    add("script.message-handler", "Message handlers", len(m["message_handlers"]), [h["messageType"] for h in m["message_handlers"]])
    add("data.named-query", "Named queries defined", len(m["named_queries"]), [q["name"] for q in m["named_queries"]])
    add("alarm.pipeline", "Alarm notification pipelines", len(m["alarms"]["pipelines"]), [p["name"] for p in m["alarms"]["pipelines"]])
    add("alarm.component", "Alarm display components", sum(m["alarms"]["alarm_components"].values()), list(m["alarms"]["alarm_components"]))
    add("eventstream", "Event streams", len(m["other_resources"]["event_streams"]), [e["name"] for e in m["other_resources"]["event_streams"]])
    th = m["theme"]
    add("style.classes", "Named style classes used by components", sum(th["style_classes_used"].values()), list(th["style_classes_used"]))
    add("style.css-vars", "Theme CSS variables (var(--..)) in views and classes", th["css_vars_in_views"] + th["css_vars_in_classes"], [])
    add("style.inline", "Components with inline style props", th["components_with_inline_style"], [])
    add("style.hex-literal", "Literal hex colours in views", th["hex_colors_in_views"], [], "candidates to move to theme tokens")
    add("session.theme", "Session theme set", 1 if th["session_theme"] else 0, [th["session_theme"]])
    add("params.session-custom", "Session custom props", len(m["params"]["session"]["custom"]), m["params"]["session"]["custom"])
    add("params.page-path", "Routes with path params", len(m["params"]["page_path_params"]), list(m["params"]["page_path_params"]))
    ct = collections.Counter()
    for v in views.values():
        ct.update(v.get("component_types", {}))
    add("components.types", "Component types used (most common)", sum(ct.values()), ["%s x%d" % (k, n) for k, n in top(ct, 12)])
    return P


# --------------------------------------------------------------------------- writers
def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in r) + " |")
    return "\n".join(out) + "\n"


def tree_lines(m):
    edges = m["embed_tree"]["edges"]
    out, seen = [], set()

    def rec(v, depth, trail):
        mark = " (cycle)" if v in trail else ""
        out.append("  " * depth + "- " + v + mark)
        if v in trail:
            return
        for c in edges.get(v, []):
            rec(c, depth + 1, trail | {v})

    roots = m["embed_tree"]["roots"] or sorted(edges)
    for r in roots:
        rec(r, 0, frozenset())
        seen.add(r)
    return out


def write_inventory(m, path):
    p, v = m["project"], m["views"]
    L = ["# Scout inventory: %s\n" % p["name"],
         "Source: `%s` (%s). Generated by scout.py; edit nothing here, regenerate.\n" % (m["source"]["ref"], m["source"]["kind"]),
         "## Project\n", md_table(["field", "value"], [[k, json.dumps(x) if isinstance(x, dict) else x] for k, x in p.items()]),
         "## Resources by type (%d resources)\n" % len(m["resources"]),
         md_table(["module/type", "count"], sorted(m["resource_counts"].items())),
         "## Pages / routes\n", md_table(["route", "view", "title", "path params"],
                                         [[x["route"], x["viewPath"], x["title"], ",".join(x["path_params"])] for x in m["pages"]]),
         "## Shared docks\n", md_table(["anchor", "id", "view", "size", "show", "handle"],
                                       [[d["anchor"], d["id"], d["viewPath"], d["size"], d["show"], d["handle"]] for d in m["docks"]]),
         "## Views (%d)\n" % len(v),
         md_table(["view", "role", "comps", "params", "bindings", "embeds", "embedded by"],
                  [[n, ",".join(i.get("role", [])), i.get("components", ""), ",".join(i.get("params", [])),
                    " ".join("%s:%d" % kv for kv in sorted(i.get("bindings", {}).items())),
                    len(i.get("embeds", [])), len(i.get("embedded_by", []))] for n, i in v.items()]),
         "## Embed tree (from pages and docks)\n", "\n".join(tree_lines(m)) + "\n",
         "Unreferenced views: %s\n" % (", ".join(m["embed_tree"]["unreferenced"]) or "none"),
         "Embed targets missing: %s\n" % (", ".join(m["embed_tree"]["missing_targets"]) or "none"),
         "## Broken references\n", md_table(["kind", "targets"], [[k, ", ".join(x) or "none"] for k, x in m["broken_refs"].items()]),
         "## Bindings by type\n", md_table(["type", "count"], sorted(m["bindings"]["by_type"].items())),
         "Transforms: %s\n" % (json.dumps(m["bindings"]["transforms"]) or "none"),
         "## Scripts\n", "### Project library\n",
         md_table(["module", "lines", "functions"], [[s["name"], s["lines"], ", ".join(s["functions"])] for s in m["scripts"]["project_library"]]),
         "### Gateway event scripts\n",
         md_table(["type", "name", "attributes", "functions"],
                  [[s["type"], s["name"], json.dumps(s["attributes"]), ", ".join(s["functions"])] for s in m["scripts"]["gateway_events"]]),
         "### Inline view scripts (transforms, events, handlers)\n",
         md_table(["view", "kinds"], [[n, json.dumps(k)] for n, k in m["scripts"]["view_inline"].items()]),
         "### system.* API use\n", md_table(["call", "count"], sorted(m["scripts"]["api_calls"].items())),
         "## Message handlers\n", md_table(["scope", "messageType", "where"], [[h["scope"], h["messageType"], h["name"]] for h in m["message_handlers"]]),
         "## Named queries\n", md_table(["name", "type", "database", "params", "tables", "used by"],
                                        [[q["name"], q["type"], q["database"], ",".join(x or "" for x in q["parameters"]), ",".join(q["tables"]), ",".join(q["used_by_views"])] for q in m["named_queries"]]),
         "## Tags referenced\n", "Providers: %s\n" % json.dumps(m["tags"]["providers"]), md_table(["path", "indirect", "used by"], [[t["path"], t["indirect"], ",".join(t["used_by"])] for t in m["tags"]["referenced"]]),
         "_%s_\n" % m["tags"]["note"],
         "## Alarms\n", md_table(["pipeline", "blocks"], [[a["name"], json.dumps(a["blocks"])] for a in m["alarms"]["pipelines"]]),
         "Alarm components: %s\n\n_%s_\n" % (json.dumps(m["alarms"]["alarm_components"]), m["alarms"]["note"]),
         "## Other resources\n", md_table(["type", "names"], [[k, ", ".join(x)] for k, x in m["other_resources"]["by_type"].items()]),
         md_table(["event stream", "enabled", "source", "handlers"], [[e["name"], e["enabled"], e["source"], ",".join(x or "" for x in e["handlers"])] for e in m["other_resources"]["event_streams"]]),
         "## Session / view / page parameters\n",
         "Session custom: %s\n\nSession props set: %s\n" % (m["params"]["session"]["custom"] or "none", json.dumps(m["params"]["session"]["props_set"])),
         md_table(["view", "params"], [[n, ",".join(x)] for n, x in m["params"]["view_params"].items()]),
         "## Theme and styling\n",
         md_table(["item", "value"], [["session theme", m["theme"]["session_theme"]], ["style classes defined", len(m["theme"]["style_classes_defined"])],
                                      ["css vars (views/classes)", "%d / %d" % (m["theme"]["css_vars_in_views"], m["theme"]["css_vars_in_classes"])],
                                      ["hex literals (views/classes)", "%d / %d" % (m["theme"]["hex_colors_in_views"], m["theme"]["hex_colors_in_classes"])],
                                      ["components with inline style", m["theme"]["components_with_inline_style"]],
                                      ["unused classes", ", ".join(m["theme"]["style_classes_unused"]) or "none"]]),
         "## Naming conventions (detected)\n", md_table(["aspect", "value"], [[k, json.dumps(x)] for k, x in m["conventions"].items()])]
    with open(path, "w") as f:
        f.write("\n".join(L))


def write_patterns(m, path):
    L = ["# Scout patterns: %s\n" % m["project"]["name"],
         "Patterns detected mechanically (counts + examples). Playbook uses these to decide which to reuse; "
         "`id` is a stable key. Absence of a pattern here means it was not found, not that it is wrong.\n",
         md_table(["id", "pattern", "count", "examples"],
                  [[x["id"], x["title"] + (" - " + x["note"] if x["note"] else ""), x["count"], "; ".join(str(e) for e in x["examples"])] for x in m["patterns"]])]
    with open(path, "w") as f:
        f.write("\n".join(L))


def write_report(m, outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "map.json"), "w") as f:
        json.dump(m, f, indent=2, sort_keys=True)
        f.write("\n")
    write_inventory(m, os.path.join(outdir, "inventory.md"))
    write_patterns(m, os.path.join(outdir, "patterns.md"))


def diff_maps(a, b):
    ja, jb = json.load(open(a)), json.load(open(b))
    for j in (ja, jb):
        j.pop("source", None)
        (j.get("project") or {}).pop("gateway", None)

    def walk(x, y, path):
        if type(x) is not type(y):
            yield path
        elif isinstance(x, dict):
            for k in sorted(set(x) | set(y)):
                if k not in x or k not in y:
                    yield path + "/" + k
                else:
                    yield from walk(x[k], y[k], path + "/" + k)
        elif x != y:
            yield path
    d = list(walk(ja, jb, ""))
    print("maps agree (ignoring source/gateway meta)" if not d else "DIFF at:\n  " + "\n  ".join(d[:50]))
    return 1 if d else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--live", metavar="PROJECT", help="project name on a live gateway (read-only REST export)")
    g.add_argument("--zip", metavar="FILE", help="project export zip")
    g.add_argument("--gwbk", metavar="FILE", help="gateway backup .gwbk")
    g.add_argument("--diff", nargs=2, metavar=("MAP_A", "MAP_B"), help="compare two map.json files")
    ap.add_argument("--project", help="project name inside a .gwbk (required there)")
    ap.add_argument("--name", help="project name to record for a --zip (default: file stem)")
    ap.add_argument("--url", help="gateway base URL (default env IGNITION_URL)")
    ap.add_argument("--api-key", help="API key 'name:secret' (default env IGNITION_API_KEY)")
    ap.add_argument("--insecure", action="store_true", help="skip TLS verification")
    ap.add_argument("-o", "--out", default="scout-report", help="output folder (default scout-report)")
    a = ap.parse_args(argv)
    try:
        if a.diff:
            return diff_maps(*a.diff)
        if a.live:
            src = load_live(a.live, a.url, a.api_key, not a.insecure)
        elif a.zip:
            src = load_zip(a.zip, a.name)
        elif a.gwbk:
            src = load_gwbk(a.gwbk, a.project)
        else:
            ap.error("give one of --live / --zip / --gwbk / --diff")
        m = extract(src)
    except (ScoutError, zipfile.BadZipFile, OSError) as e:
        print("scout: %s" % e, file=sys.stderr)
        return 2
    write_report(m, a.out)
    print("scout: %s (%s) -> %s  [%d resources, %d views, %d pages]" % (
        m["project"]["name"], src["kind"], a.out, len(m["resources"]), len(m["views"]), len(m["pages"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
