#!/usr/bin/env python3
"""FAT: offline factory acceptance test for a build output dir or project folder.

    python3 skill/scripts/fat.py <dir> [--report out.json] [--no-skill]
    python3 skill/scripts/fat.py --skill-only

<dir> holds project-relative resources (com.inductiveautomation.perspective/…, ignition/…),
e.g. a build script's staged output. Stdlib only, no gateway, no LLM. Checks:
  json          every *.json parses
  view_lint     view_lint.py findings per view.json
  expression    no `? :` ternary in expressions (Ignition only has if(c,a,b))
  resource      resource.json shape + listed files present (views, named queries)
  page_config   pages point at views; a shared-dock view is not also embedded
  playbook      warnings only: script transform that is a pure expression; hex literal in a
                view style (rules: references/standards/playbook.md §2, §10)
  skill         check_global.py and check_links.py (skipped by --no-skill)
Exit 0 green, 1 red; JSON report on stdout (failures carry file/path and a fix hint).
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ign  # noqa: E402
import view_lint  # noqa: E402

STR = re.compile(r"\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'")


def expressions(doc):
    for jp, n in _ign.walk(doc):
        c = n.get("config")
        if n.get("type") == "expr" and isinstance(c, dict):
            yield jp, c.get("expression", "")
        elif n.get("type") == "expression":
            yield jp, n.get("expression", "")


def check_json(root, rep):
    rep.check("json")
    docs = {}
    for dp, _, fn in os.walk(root):
        for f in fn:
            if f.endswith(".json"):
                p = os.path.join(dp, f)
                try:
                    docs[p] = _ign.read_json(p)
                except ValueError as e:
                    rep.fail("json", os.path.relpath(p, root), "", "invalid JSON: %s" % e,
                             "regenerate the file from the build script; never hand-edit")
    return docs


def check_views(root, rep, vmap):
    rep.check("view_lint")
    rep.check("expression")
    for name, p in vmap.items():
        rel = os.path.relpath(p, root)
        view_lint.SCHEMA_DIR = view_lint._find_schema_dir(p)
        for f in view_lint.lint(p):
            rep.fail("view_lint", rel, "", str(f), "see skill/scripts/view_lint.py; fix the prop/param named")
        try:
            doc = _ign.read_json(p)
        except ValueError:
            continue
        for jp, e in expressions(doc):
            if "?" in STR.sub("", e):
                rep.fail("expression", rel, jp, "`? :` ternary in expression: %s" % e[:120],
                         "Ignition expressions have no ternary; use if(cond, then, else)")


PURE_RETURN = re.compile(r"^return\s+\S")
IMPURE = re.compile(r"\b(system|self|import|for|while|if|def)\b|\bvalue\.\w+\(")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def playbook_warnings(doc):
    """Yield (json-path, check, message) for Playbook rules that are mechanically checkable."""
    for jp, n in _ign.walk(doc):
        if n.get("type") == "script" and isinstance(n.get("code"), str) and "transforms" in jp:
            lines = [l.strip() for l in n["code"].splitlines() if l.strip() and not l.strip().startswith("#")]
            if len(lines) == 1 and PURE_RETURN.match(lines[0]) and not IMPURE.search(lines[0]):
                yield jp, "playbook.script-transform", (
                    "script transform is a single `return` expression; use an expression transform (playbook §2)")
        t = n.get("type", "")
        st = (n.get("props") or {}).get("style") if t.startswith("ia.") and not t.startswith("ia.chart.") else None
        if isinstance(st, dict):
            hexes = [v for v in st.values() if isinstance(v, str) and HEX.search(v)]
            if hexes:
                yield jp + ".props.style", "playbook.hex-literal", (
                    "inline hex colour %s; use a theme variable/style class (playbook §10)" % hexes[0][:40])


def check_playbook(root, rep, vmap):
    for name, p in vmap.items():
        try:
            doc = _ign.read_json(p)
        except ValueError:
            continue
        for jp, check, msg in playbook_warnings(doc):
            rep.warn(check, os.path.relpath(p, root) + ":" + jp, msg)


def check_resources(root, rep, vmap):
    rep.check("resource")
    dirs = [os.path.dirname(p) for p in vmap.values()]
    nq = os.path.join(root, "ignition", "named-query")
    for dp, _, fn in os.walk(nq):
        if fn:
            dirs.append(dp)
    for d in dirs:
        rel = os.path.relpath(d, root)
        rp = os.path.join(d, "resource.json")
        if not os.path.isfile(rp):
            rep.warn("resource", rel, "no resource.json (fine only when patching an existing live resource)")
            continue
        try:
            r = _ign.read_json(rp)
        except ValueError:
            continue
        for k in ("scope", "version", "files", "attributes"):
            if k not in r:
                rep.fail("resource", rel + "/resource.json", k, "missing key %r" % k,
                         "copy resource.json from a currently loading live resource of the same type")
        for f in r.get("files", []):
            if not os.path.isfile(os.path.join(d, f)):
                rep.fail("resource", rel + "/resource.json", "files", "lists %r but the file is absent" % f,
                         "write the payload file next to resource.json")


def check_pages(root, rep, vmap):
    rep.check("page_config")
    p = os.path.join(root, _ign.PERSP, "page-config", "config.json")
    if not os.path.isfile(p):
        return
    try:
        cfg = _ign.read_json(p)
    except ValueError:
        return
    rel = os.path.relpath(p, root)
    for route, pg in (cfg.get("pages") or {}).items():
        if pg.get("viewPath") not in vmap:
            rep.warn("page_config", rel, "page %s -> %s not in this dir (must already exist live)"
                     % (route, pg.get("viewPath")))
    docks = {d.get("viewPath") for side, lst in (cfg.get("sharedDocks") or {}).items()
             if isinstance(lst, list) for d in lst if isinstance(d, dict)}
    for name, vp in vmap.items():
        for jp, n in _ign.walk(_ign.read_json(vp).get("root", {})):
            t = (n.get("props") or {}).get("path") if n.get("type") == "ia.display.view" else None
            if t in docks:
                rep.fail("page_config", os.path.relpath(vp, root), jp,
                         "view %r is a shared dock and is also embedded" % t,
                         "remove the embed or the sharedDocks entry (a project-diff error otherwise)")


def check_skill(rep):
    rep.check("skill")
    for s in ("check_global.py", "check_links.py"):
        r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True)
        if r.returncode:
            rep.fail("skill", "skill/scripts/" + s, "", (r.stdout.strip().splitlines() or ["failed"])[0][:200],
                     "run it directly for the full list; the skill must stay global and links valid")


def run(root, skill=True):
    rep = _ign.Report("fat")
    if not os.path.isdir(root):
        sys.exit("not a directory: %s" % root)
    check_json(root, rep)
    vmap = _ign.views(root)
    check_views(root, rep, vmap)
    check_resources(root, rep, vmap)
    check_pages(root, rep, vmap)
    check_playbook(root, rep, vmap)
    if skill:
        check_skill(rep)
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--skill-only", action="store_true", help="only check_global + check_links")
    ap.add_argument("--report")
    ap.add_argument("--no-skill", action="store_true")
    a = ap.parse_args()
    if a.skill_only:
        r = _ign.Report("fat")
        check_skill(r)
        sys.exit(r.finish(a.report))
    if not a.dir:
        ap.error("dir required (or --skill-only)")
    sys.exit(run(a.dir, not a.no_skill).finish(a.report))
