"""Build a project-import ZIP for the `global` project containing WebDev
Python resources, POST it to the Ignition 8.3 gateway, and report results.

Portability copy, adapted from `~/ignition-mcp/deploy_webdev_endpoints.py`
(untracked there). See `references/gateway/environment-setup.md` for what
this deploys and why the `global` project matters.

TOKEN is read from the `IGNITION_MCP_IGNITION_API_KEY` env var at runtime
(the value `ignition-mcp/.env` holds) -- never committed to any repo. Set
it before running this against a real gateway.

Usage:
  python build_import.py minimal   # just GatewayAPI/ping  (format probe)
  python build_import.py full      # all GatewayAPI endpoints
"""
import io
import json
import os
import sys
import zipfile

import httpx

BASE = os.environ.get("IGNITION_MCP_IGNITION_GATEWAY_URL", "http://localhost:8088")  # default: local gateway
TOKEN = os.environ.get("IGNITION_MCP_IGNITION_API_KEY",
                        "ClaudeApiKey:SET_IGNITION_MCP_IGNITION_API_KEY_ENV_VAR")
H = {"X-Ignition-API-Token": TOKEN}

METHOD_KEYS = {
    "enabled": True,
    "require-https": False,
    "require-auth": False,
    "user-source": "",
    "required-roles": "",
    "max-retry-attempts": 3,
}


def py_resource(files_methods):
    """files_methods: dict of method-name -> python source string.
    Returns dict of {filename: bytes} for one webdev python resource folder."""
    out = {}
    cfg = {"resource-type": "python-resource"}
    manifest_files = ["config.json"]
    for method, src in files_methods.items():
        cfg[method] = dict(METHOD_KEYS)
        fname = method + ".py"
        out[fname] = src.encode("utf-8")
        manifest_files.append(fname)
    out["config.json"] = json.dumps(cfg, indent=2).encode("utf-8")
    out["resource.json"] = json.dumps(
        {
            "scope": "G",
            "version": 1,
            "restricted": False,
            "overridable": True,
            "files": manifest_files,
            "attributes": {},
        },
        indent=2,
    ).encode("utf-8")
    return out


PING = {
    "doGet": (
        "def doGet(request, session):\n"
        "    return {'json': {'ok': True, 'msg': 'pong', 'scope': 'gateway'}}\n"
    ),
    "doPost": (
        "def doPost(request, session):\n"
        "    body = request['data']\n"
        "    if isinstance(body, basestring):\n"
        "        body = system.util.jsonDecode(body)\n"
        "    return {'json': {'ok': True, 'echo': body}}\n"
    ),
}

TAGS = {
    "doPost": r'''def doPost(request, session):
    body = request['data']
    if isinstance(body, basestring):
        body = system.util.jsonDecode(body)
    if body is None:
        body = {}
    if 'paths' in body:
        paths = [str(p) for p in body['paths']]
        qvs = system.tag.readBlocking(paths)
        out = []
        for i, p in enumerate(paths):
            qv = qvs[i]
            out.append({
                'path': p,
                'value': qv.value,
                'quality': str(qv.quality),
                'timestamp': str(qv.timestamp),
                'good': qv.quality.isGood(),
            })
        return {'json': out}
    if 'tagPath' in body:
        p = body['tagPath']
        v = body['value']
        res = system.tag.writeBlocking([p], [v])
        return {'json': {'status': 'ok', 'tagPath': p, 'value': v,
                         'writeResult': str(res[0])}}
    return {'json': {'error': 'expected "paths" or "tagPath"'},
            'response': {'code': 400}}
''',
    "doGet": (
        "def doGet(request, session):\n"
        "    return {'json': {'endpoint': 'tags', 'usage': "
        "'POST {\"paths\":[...]} to read or {\"tagPath\":..,\"value\":..} to write'}}\n"
    ),
}

TAGCONFIG = {
    "doPost": r'''def doPost(request, session):
    body = request['data']
    if isinstance(body, basestring):
        body = system.util.jsonDecode(body)
    if body is None:
        body = {}
    action = body.get('action')
    if action == 'getConfig':
        tp = body['tagPath']
        cfg = system.tag.getConfiguration([tp], False)
        if cfg:
            return {'json': system.util.jsonDecode(system.util.jsonEncode(cfg[0]))}
        return {'json': {'error': 'not found: ' + tp}, 'response': {'code': 404}}
    if action == 'configure':
        provider = body.get('provider') or 'default'
        tags = body['tags']
        mode = body.get('editMode', 'm')
        res = system.tag.configure(provider, tags, mode)
        return {'json': {'status': 'ok', 'results': [str(r) for r in res]}}
    if action == 'deleteTags':
        paths = list(body['tagPaths'])
        res = system.tag.deleteTags(paths)
        return {'json': {'status': 'deleted', 'count': len(paths),
                         'results': [str(r) for r in res]}}
    if action == 'listUDTTypes':
        provider = body.get('provider') or 'default'
        res = system.tag.browse('[%s]_types_' % provider, {'tagType': 'UdtType'})
        types = [{'name': r['name'], 'path': str(r['fullPath'])}
                 for r in res.getResults()]
        return {'json': types}
    if action == 'getUDTDefinition':
        up = body['udtPath']
        cfg = system.tag.getConfiguration([up], True)
        if cfg:
            return {'json': system.util.jsonDecode(system.util.jsonEncode(cfg[0]))}
        return {'json': {'error': 'not found: ' + up}, 'response': {'code': 404}}
    if action == 'browse':
        def browse_one(p, remaining):
            res = system.tag.browse(p)
            out = []
            for r in res.getResults():
                entry = {'name': r['name'], 'path': str(r['fullPath']),
                         'hasChildren': r['hasChildren'], 'tagType': str(r['tagType'])}
                if r['hasChildren'] and remaining > 1:
                    entry['children'] = browse_one(str(r['fullPath']), remaining - 1)
                out.append(entry)
            return out
        path = body.get('path', '') or ''
        try:
            depth = int(body.get('depth', 2))
        except Exception:
            depth = 2
        depth = max(1, min(depth, 4))
        if not path:
            providers = system.tag.getAllProviderNames()
            results = [{'name': pn, 'path': '[%s]' % pn, 'hasChildren': True,
                       'tagType': 'Provider', 'children': browse_one('[%s]' % pn, depth - 1) if depth > 1 else []}
                      for pn in providers]
        else:
            results = browse_one(path, depth)
        return {'json': {'path': path, 'depth': depth, 'results': results}}
    return {'json': {'error': 'unknown action: ' + str(action)},
            'response': {'code': 400}}
''',
}

ALARMS = {
    "doPost": r'''def doPost(request, session):
    from java.text import SimpleDateFormat
    body = request['data']
    if isinstance(body, basestring):
        body = system.util.jsonDecode(body)
    if body is None:
        body = {}
    action = body.get('action')

    def parse_iso(s):
        if not s:
            return None
        s = s.replace('Z', '+0000')
        for fmt in ("yyyy-MM-dd'T'HH:mm:ssXXX", "yyyy-MM-dd'T'HH:mm:ssZ",
                    "yyyy-MM-dd'T'HH:mm:ss"):
            try:
                return SimpleDateFormat(fmt).parse(s)
            except:
                pass
        return None

    if action == 'getActive':
        kw = {}
        if body.get('sourceFilter'):
            kw['source'] = [body['sourceFilter']]
        if body.get('priorityFilter'):
            kw['priority'] = [body['priorityFilter']]
        if body.get('stateFilter'):
            kw['state'] = [body['stateFilter']]
        alarms = system.alarm.queryStatus(**kw)
        out = []
        for a in alarms:
            out.append({
                'eventId': str(a.getId()),
                'displayPath': str(a.getDisplayPathOrSource()),
                'source': str(a.getSource()),
                'priority': str(a.getPriority()),
                'state': str(a.getState()),
                'activeTime': str(a.getActiveData().getTimestamp()),
            })
        return {'json': out}

    if action == 'getHistory':
        start = parse_iso(body.get('startTime'))
        end = parse_iso(body.get('endTime'))
        if start is None:
            start = system.date.addHours(system.date.now(), -24)
        if end is None:
            end = system.date.now()
        kw = {'startDate': start, 'endDate': end}
        jn = body.get('journalName')
        if jn:
            kw['journalName'] = jn
        if body.get('sourceFilter'):
            kw['source'] = [body['sourceFilter']]
        if body.get('priorityFilter'):
            kw['priority'] = [body['priorityFilter']]
        try:
            ds = system.alarm.queryJournal(**kw)
        except:
            import sys as _sy
            ex = _sy.exc_info()[1]
            return {'json': {'entries': [], 'total': 0,
                             'note': 'alarm journal query failed: ' + str(ex) +
                             ' (pass "journalName" or configure an Alarm Journal '
                             'profile on the gateway)'}}
        mx = int(body.get('maxResults', 100))
        rows = []
        for i in range(min(ds.getRowCount(), mx)):
            row = {}
            for c in range(ds.getColumnCount()):
                row[ds.getColumnName(c)] = str(ds.getValueAt(i, c))
            rows.append(row)
        return {'json': {'entries': rows, 'total': ds.getRowCount()}}

    if action == 'acknowledge':
        ids = list(body['eventIds'])
        note = body.get('ackNote', '')
        system.alarm.acknowledge(ids, note)
        return {'json': {'acknowledged': len(ids)}}

    return {'json': {'error': 'unknown action: ' + str(action)},
            'response': {'code': 400}}
''',
}

TAGHISTORY = {
    "doPost": r'''def doPost(request, session):
    from java.text import SimpleDateFormat
    body = request['data']
    if isinstance(body, basestring):
        body = system.util.jsonDecode(body)
    if body is None:
        body = {}

    def parse_iso(s):
        if not s:
            return None
        s = s.replace('Z', '+0000')
        for fmt in ("yyyy-MM-dd'T'HH:mm:ssXXX", "yyyy-MM-dd'T'HH:mm:ssZ",
                    "yyyy-MM-dd'T'HH:mm:ss"):
            try:
                return SimpleDateFormat(fmt).parse(s)
            except:
                pass
        return None

    paths = [str(p) for p in body['tagPaths']]
    start = parse_iso(body.get('startTime'))
    end = parse_iso(body.get('endTime'))
    agg = body.get('aggregation', 'LastValue')
    mx = int(body.get('maxResults', 1000))
    kw = {'paths': paths, 'startDate': start, 'endDate': end,
          'aggregationMode': agg, 'returnSize': mx}
    iv = body.get('intervalMs')
    if iv:
        kw['returnSize'] = 0
        kw['intervalHours'] = float(iv) / 3600000.0
    ds = system.tag.queryTagHistory(**kw)
    tags_out = []
    for c in range(1, ds.getColumnCount()):
        name = ds.getColumnName(c)
        vals = []
        for r in range(min(ds.getRowCount(), mx)):
            vals.append({'t': str(ds.getValueAt(r, 0)), 'v': ds.getValueAt(r, c)})
        tags_out.append({'path': name, 'values': vals})
    return {'json': {'tags': tags_out, 'rowCount': ds.getRowCount()}}
''',
}

SCRIPTEXEC = {
    "doPost": r'''def doPost(request, session):
    import sys as _s
    import traceback
    logger = system.util.getLogger('GatewayAPI.scriptExec')
    body = request['data']
    if isinstance(body, basestring):
        body = system.util.jsonDecode(body)
    if body is None:
        body = {}
    script = body.get('script', '')
    dry = body.get('dryRun', False)
    h = str(abs(hash(script)))
    logger.info('scriptExec hash=%s dryRun=%s' % (h, dry))
    if dry:
        return {'json': {'dry_run': True, 'would_execute': True, 'script': script}}
    buf = []

    class _Cap(object):
        def write(self, t):
            buf.append(t)

        def flush(self):
            pass

    g = {'system': system, 'result': None, '__name__': '__scriptexec__'}
    old = _s.stdout
    err = None
    try:
        _s.stdout = _Cap()
        exec script in g, g
    except Exception:
        err = traceback.format_exc()
    finally:
        _s.stdout = old
    return {'json': {'result': g.get('result'), 'stdout': ''.join(buf),
                     'error': err, 'scriptHash': h}}
''',
}

HEALTH = {
    "doGet": r'''def doGet(request, session):
    info = system.tag.readBlocking(['[System]Gateway/SystemName'])[0]
    return {'json': {'ok': True, 'systemName': info.value,
                     'time': str(system.date.now())}}
''',
}

FULL_RESOURCES = {
    "GatewayAPI/ping": PING,
    "GatewayAPI/health": HEALTH,
    "GatewayAPI/tags": TAGS,
    "GatewayAPI/tagConfig": TAGCONFIG,
    "GatewayAPI/alarms": ALARMS,
    "GatewayAPI/tagHistory": TAGHISTORY,
    "GatewayAPI/scriptExec": SCRIPTEXEC,
}

MINIMAL_RESOURCES = {"GatewayAPI/ping": PING}


def build_zip(resources):
    # keep the existing global-props resource from a fresh export
    with httpx.Client(base_url=BASE, timeout=60) as c:
        ex = c.get("/data/api/v1/projects/export/global",
                   headers={**H, "Accept": "*/*"})
        ex.raise_for_status()
    src = zipfile.ZipFile(io.BytesIO(ex.content))

    buf = io.BytesIO()
    z = zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED)
    for n in src.namelist():
        if n.startswith("com.inductiveautomation.webdev/"):
            continue  # drop any prior webdev resources; we re-add clean ones
        z.writestr(n, src.read(n))
    for route, methods in resources.items():
        folder = "com.inductiveautomation.webdev/resources/%s" % route
        for fname, data in py_resource(methods).items():
            z.writestr("%s/%s" % (folder, fname), data)
    z.close()
    return buf.getvalue()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "minimal"
    resources = MINIMAL_RESOURCES if mode == "minimal" else FULL_RESOURCES
    zip_bytes = build_zip(resources)
    path = __file__.rsplit("\\", 1)[0] + "\\global-import-%s.zip" % mode
    with open(path, "wb") as f:
        f.write(zip_bytes)
    print("built", path, len(zip_bytes), "bytes")
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    for n in zf.namelist():
        print("  ", n)

    with httpx.Client(base_url=BASE, timeout=120) as c:
        r = c.post(
            "/data/api/v1/projects/import/global",
            headers={**H, "Content-Type": "application/zip", "Accept": "application/json"},
            params={"overwrite": "true"},
            content=zip_bytes,
        )
    print("\nimport status:", r.status_code)
    print(r.text[:2000])


if __name__ == "__main__":
    main()
