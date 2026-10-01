#!/usr/bin/env python3
"""SAT: live site acceptance test of a build against a running gateway (native REST + WebDev).

    IGNITION_URL=http://host:8088 IGNITION_API_KEY=keyName:secret \\
    python3 skill/scripts/sat.py --project <name> --build-dir <dir> [--since T] [--wait S]

<dir> is the same build output dir fat.py checks. Env: IGNITION_URL, IGNITION_API_KEY
(admin scope). Checks, each against an endpoint confirmed in references/gateway/mcp-tool-map.md:
  resource   every file in <dir> is in the project (GET /data/api/v1/projects/export/{name}) and
             view/page/query payloads match; every page-config viewPath exists in the project
  tags       every bound tag path reads Quality Good (POST /system/webdev/global/GatewayAPI/tags)
  logs       no WARN/ERROR since T tied to the project under test (GET /data/api/v1/logs);
             --strict-logs counts every gateway WARN/ERROR
  pages      each page route answers HTTP 200 (weak: the client shell answers 200 for any route)
--since: epoch seconds/milliseconds or ISO time (default 15 min ago). --wait S: retry the
resource check up to S seconds (a scan can take minutes). HTTP 402 -> paused report, exit 3.
"""
import argparse
import datetime
import io
import json
import os
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _ign  # noqa: E402

ROOTS = (_ign.PERSP + "/", "ignition/")
LOG_LOGGERS = ("perspective", "project", "namedquer", "binding", "tag")


def parse_since(s):
    if not s:
        return int((time.time() - 900) * 1000)
    try:
        v = float(s)
        return int(v if v > 1e11 else v * 1000)
    except ValueError:
        return int(datetime.datetime.fromisoformat(s).timestamp() * 1000)


def build_files(build):
    out = {}
    for dp, _, fn in os.walk(build):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), build).replace(os.sep, "/")
            if rel.startswith(ROOTS):
                out[rel] = os.path.join(dp, f)
    return out


def project_zip(project):
    code, body = _ign.http("GET", "/data/api/v1/projects/export/" + project, raw=True, timeout=120)
    if code != 200:
        raise RuntimeError("export of project %r failed: HTTP %s" % (project, code))
    z = zipfile.ZipFile(io.BytesIO(body))
    return {n: z.read(n) for n in z.namelist()}


def check_resources(rep, project, files, pages):
    rep.check("resource")
    try:
        live = project_zip(project)
    except RuntimeError as e:
        rep.fail("resource", "", project, str(e), "check the project name and that the API key has admin scope")
        return None
    for rel, local in sorted(files.items()):
        if rel not in live:
            rep.fail("resource", rel, project, "not present in project %r on the gateway" % project,
                     "deploy it, then request a project scan; a fresh resource can take minutes to load")
        elif not rel.endswith("resource.json"):
            want = open(local, "rb").read()
            same = want == live[rel]
            if not same and rel.endswith(".json"):
                same = json.loads(want) == json.loads(live[rel])
            if not same:
                rep.fail("resource", rel, project, "gateway copy differs from the build output",
                         "stale scan or a later edit; redeploy and rescan, or rebuild")
    for route, vp in pages.items():
        if _ign.PERSP + "/views/%s/view.json" % vp not in live:
            rep.fail("resource", _ign.PERSP + "/page-config/config.json", route,
                     "page %s points at view %r which is not in project %r" % (route, vp, project),
                     "deploy the view or fix the page viewPath")
    return live


def check_tags(rep, build):
    rep.check("tags")
    refs, notes = _ign.tag_refs(build)
    for n in notes:
        rep.warn("tags", "", n)
    by_tag = {}
    for r in refs:
        by_tag.setdefault(r["tag"], []).append(r)
    tags = sorted(by_tag)
    for i in range(0, len(tags), 100):
        code, res = _ign.http("POST", "/system/webdev/global/GatewayAPI/tags", {"paths": tags[i:i + 100]})
        if code != 200 or not isinstance(res, list):
            rep.fail("tags", "", "", "tag read endpoint failed: HTTP %s" % code,
                     "WebDev GatewayAPI endpoints must be deployed (see references/gateway/environment-setup.md)")
            return
        for t in res:
            if not t.get("good"):
                for r in by_tag[t["path"]]:
                    rep.fail("tags", r["file"], r["path"],
                             "tag %s quality %s" % (t["path"], t.get("quality")),
                             "fix the tag path in the binding, or create the tag / repair its source")
    return len(tags)


def check_logs(rep, project, since, names, strict):
    rep.check("logs")
    code, res = _ign.http("GET", "/data/api/v1/logs?minLevel=WARN&limit=200&startTime=%d" % since)
    if code != 200 or not isinstance(res, dict):
        rep.fail("logs", "", "", "log endpoint failed: HTTP %s" % code, "check API key scope")
        return
    for e in res.get("items", []):
        if e.get("level") not in ("WARN", "ERROR"):
            continue
        msg, lg = e.get("message", ""), e.get("loggerName", "").lower()
        ours = (e.get("mdc") or {}).get("project-name") == project or project in msg
        rel = strict or (ours and (any(k in lg for k in LOG_LOGGERS) or any(n in msg for n in names)))
        line = "%s %s: %s" % (e["level"], e.get("loggerName"), msg[:200])
        if rel:
            rep.fail("logs", "", str(e.get("timestamp")), line, "open the gateway log around this time; fix the cause")
        else:
            rep.warn("logs", "", "unrelated " + line)


def check_pages(rep, project, pages):
    rep.check("pages")
    for route in pages:
        code, _ = _ir_get(project, route)
        if code != 200:
            rep.fail("pages", "", route, "page URL returned HTTP %s" % code,
                     "check the route in page-config and that the project is loaded")


def _ir_get(project, route):
    return _ign.http("GET", "/data/perspective/client/%s%s" % (project, route), raw=True, auth=False)


def run(project, build, since, wait=0, strict_logs=False):
    rep = _ign.Report("sat")
    files = build_files(build)
    pages = {}
    pc = os.path.join(build, _ign.PERSP, "page-config", "config.json")
    if os.path.isfile(pc):
        pages = {r: p["viewPath"] for r, p in _ign.read_json(pc).get("pages", {}).items()}
    try:
        deadline = time.time() + wait
        while True:
            probe = _ign.Report("sat")
            check_resources(probe, project, files, pages)
            if not probe.failures or time.time() >= deadline:
                break
            time.sleep(10)
        rep.failures, rep.checks = probe.failures, probe.checks
        n = check_tags(rep, build)
        names = [os.path.basename(os.path.dirname(f)) for f in files if f.endswith("view.json")]
        check_logs(rep, project, since, names, strict_logs)
        check_pages(rep, project, pages)
        rep.checks["_tags_checked"] = n or 0
    except _ign.Paused as e:
        rep.paused = True
        rep.warn("paused", "", str(e))
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--build-dir", required=True)
    ap.add_argument("--since")
    ap.add_argument("--wait", type=int, default=0)
    ap.add_argument("--strict-logs", action="store_true")
    ap.add_argument("--report")
    a = ap.parse_args()
    sys.exit(run(a.project, a.build_dir, parse_since(a.since), a.wait, a.strict_logs).finish(a.report))
