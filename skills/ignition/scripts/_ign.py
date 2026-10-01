"""Shared helpers for fat.py / sat.py / loop.py (stdlib only, no LLM, no MCP).

Report shape (both tools):
    {"tool": "fat"|"sat", "ok": bool, "paused": bool, "summary": {check: n_failures},
     "failures": [{"check", "file", "path", "message", "hint"}], "warnings": [...]}
Exit codes: 0 green, 1 red, 2 usage/config error, 3 paused (HTTP 402: trial lapsed).
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

EXIT_OK, EXIT_RED, EXIT_USAGE, EXIT_PAUSED = 0, 1, 2, 3
PERSP = "com.inductiveautomation.perspective"


class Paused(Exception):
    """Gateway answered HTTP 402: trial timer lapsed. Report and stop; never reset it."""


class Report:
    def __init__(self, tool):
        self.tool, self.failures, self.warnings, self.checks, self.paused = tool, [], [], {}, False

    def check(self, name):
        self.checks.setdefault(name, 0)

    def fail(self, check, file, path, message, hint=""):
        self.check(check)
        self.checks[check] += 1
        self.failures.append(dict(check=check, file=file, path=path, message=message, hint=hint))

    def warn(self, check, file, message):
        self.warnings.append(dict(check=check, file=file, message=message))

    def data(self):
        return dict(tool=self.tool, ok=not self.failures and not self.paused, paused=self.paused,
                    summary=self.checks, failures=self.failures, warnings=self.warnings)

    def finish(self, out=None):
        d = self.data()
        text = json.dumps(d, indent=2)
        if out:
            with open(out, "w") as f:
                f.write(text + "\n")
        print(text)
        return EXIT_PAUSED if self.paused else (EXIT_OK if d["ok"] else EXIT_RED)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def views(root):
    """{view name: absolute view.json path} for a build output dir or project folder."""
    base = os.path.join(root, PERSP, "views")
    out = {}
    for dp, _, fn in os.walk(base):
        if "view.json" in fn:
            out[os.path.relpath(dp, base).replace(os.sep, "/")] = os.path.join(dp, "view.json")
    return out


def walk(node, path=""):
    """Yield (json-path, dict) for every dict under node."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))


EXPR_TAG = re.compile(r"\{(\[[^\]{}]*\][^{}]*)\}")
PARAM_REF = re.compile(r"^\{view\.params\.([\w.]+)\}$")


def _param_values(root, vmap):
    """{view: {param: set(literal values)}} from view defaults and every embed that targets it."""
    vals = {}
    docs = {n: read_json(p) for n, p in vmap.items()}
    for n, d in docs.items():
        for k, v in (d.get("params") or {}).items():
            if isinstance(v, str) and v:
                vals.setdefault(n, {}).setdefault(k, set()).add(v)
    for d in docs.values():
        for _, node in walk(d.get("root", {})):
            props = node.get("props") if isinstance(node.get("props"), dict) else {}
            target = props.get("path") if node.get("type") == "ia.display.view" else None
            for k, v in (props.get("params") or {}).items() if target else []:
                if isinstance(v, str) and v:
                    vals.setdefault(target, {}).setdefault(k, set()).add(v)
    return vals


def tag_refs(root):
    """Bound tag paths in every view: [{"file","path"(json path),"tag"}] plus [unresolved notes].

    Handles direct/indirect `tag` bindings (references to view params are resolved from
    embed call sites and view defaults) and `{[provider]path}` refs inside expressions.
    """
    vmap = views(root)
    pv = _param_values(root, vmap)
    refs, notes = [], []
    for name, vpath in vmap.items():
        rel = os.path.relpath(vpath, root)
        for jp, node in walk(read_json(vpath)):
            if node.get("type") == "tag" and isinstance(node.get("config"), dict):
                cfg = node["config"]
                tpl = cfg.get("tagPath", "")
                choices = [[]]
                for idx, ref in (cfg.get("references") or {}).items():
                    m = PARAM_REF.match(ref) if isinstance(ref, str) else None
                    vs = sorted(pv.get(name, {}).get(m.group(1), ())) if m else []
                    choices = [c + [(idx, v)] for c in choices for v in vs]
                for c in choices:
                    p = tpl
                    for idx, v in c:
                        p = p.replace("{%s}" % idx, v)
                    if re.match(r"^\[[^\]]+\]", p) and "{" not in p:
                        refs.append(dict(file=rel, path=jp, tag=p))
                    else:
                        notes.append("%s %s: unresolved tag path %r" % (rel, jp, p))
            elif node.get("type") == "expr" and isinstance(node.get("config"), dict):
                for m in EXPR_TAG.finditer(node["config"].get("expression", "")):
                    refs.append(dict(file=rel, path=jp, tag=m.group(1)))
    return refs, notes


# ---- gateway HTTP (native REST + WebDev), API key from env ----

def gateway():
    url = os.environ.get("IGNITION_URL") or os.environ.get("IGNITION_MCP_IGNITION_GATEWAY_URL")
    key = os.environ.get("IGNITION_API_KEY") or os.environ.get("IGNITION_MCP_IGNITION_API_KEY")
    if not url or not key:
        sys.exit("set IGNITION_URL and IGNITION_API_KEY (keyName:secret, admin scope)")
    return url.rstrip("/"), key


def http(method, path, body=None, raw=False, timeout=60, auth=True):
    url, key = gateway()
    headers = {"X-Ignition-API-Token": key} if auth else {}
    data = None
    if body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
    req = urllib.request.Request(url + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = r.read()
            return r.status, payload if raw else (json.loads(payload) if payload else None)
    except urllib.error.HTTPError as e:
        if e.code == 402:
            raise Paused("HTTP 402 from %s: gateway trial timer lapsed" % path)
        return e.code, e.read()


def script_exec(script, timeout=60):
    """Run Jython on the gateway via the WebDev scriptExec endpoint; returns its `result`."""
    code, r = http("POST", "/system/webdev/global/GatewayAPI/scriptExec", {"script": script}, timeout=timeout)
    if code != 200 or not isinstance(r, dict) or r.get("error"):
        raise RuntimeError("scriptExec failed: %s %s" % (code, (r.get("error") if isinstance(r, dict) else r)))
    return r.get("result")
