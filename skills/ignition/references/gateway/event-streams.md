# Event Streams: resource format, deploy, verify (8.3)

Stage concepts (source/encoder/filter/transform/buffer/handler/error handler, source and handler
property tables) live in `../ignition-8-3/connectivity-and-modules.md` § Event Streams. This file
holds what the manual does not: the on-disk resource, how to write it to a live gateway, how to
read runtime state, and the traps. Verified live on 8.3 with a Tag Event source and a Database handler.

## Resource layout

`data/projects/<project>/com.inductiveautomation.eventstream/event-streams/<StreamName>/`
holds two files:

- `resource.json`: `{"scope":"G","version":1,"restricted":false,"overridable":true,"attributes":{},"files":["config.json"]}`
- `config.json`: the stream (shape below).

Stages map to keys. `filter`/`transform`/`onError` hold Jython in `userCode`; the body is the
indented body of a function taking `event` and `state` (tab-indent every line, no `def`).

```json
{
 "enabled": true,
 "source": {"type": "ignition.tagEvent", "config": {
    "paths": ["[provider]folder/*/tag"], "changeTypes": ["VALUE"], "skipInitialValues": false}},
 "sourceEncoder": {"type": "ignition.jsonObject", "properties": {"encoding": "UTF-8"}},
 "filter": {"enabled": true, "userCode": "\treturn event.data.get('value') is not None"},
 "transform": {"enabled": true, "userCode": "\td = dict(event.data)\n\td['name'] = str(event.metadata['tagPath'])\n\treturn d"},
 "transformEncoder": {"type": "ignition.jsonObject", "properties": {"encoding": "UTF-8"}},
 "batch": {"debounceMs": 100, "maxWaitMs": 1000, "maxQueueSize": 0, "overflow": "DROP_OLDEST"},
 "handlers": [{"enabled": true, "type": "com.inductiveautomation.sqlbridge.datasource",
   "config": {"mode": "INSERT", "bypassStoreForward": false, "datasourceName": "<db connection>",
     "tableName": "<table>", "autoCreateTable": false,
     "timestampColumnEnabled": true, "timestampColumnName": "t_stamp",
     "columnMappings": [{"name": "col", "type": "String",
        "value": {"data": "{event.data.name}", "type": "EXPRESSION"}}],
     "whereClauses": []},
   "failureStrategy": {"type": "ABORT", "retryPolicy": null}}],
 "onError": {"enabled": false, "userCode": ""}}
```

Type ids seen: source `ignition.tagEvent`; encoder `ignition.jsonObject`; handler
`com.inductiveautomation.sqlbridge.datasource` (Database; needs SQL Bridge). Other source/handler
type ids (Kafka, HTTP, Logger, Script, Tag, Gateway Event/Message) are registered by their
modules: create one in the Designer once and copy the resulting `config.json` rather than guessing.

Data contract for a Tag Event source: `event.data` = `value`, `quality`, `timestamp`;
`event.metadata['tagPath']`, `['isInitial']`. Transform returns a dict; each key becomes
`{event.data.<key>}` in handler column expressions. Wrap non-primitive fields with `str(...)`
in the transform so column types stay simple.

## Create

Stage `config.json` on the Windows side, then copy it in from a short `run_gateway_script`
(see `mcp-tool-map.md`, `environment-setup.md`, `resource-formats.md` for the general write
loop): `os.makedirs` the stream dir, write `config.json` and `resource.json` with
`f.flush(); os.fsync(f.fileno())`, then `requestScan()`. Create the target table first
(handler `autoCreateTable` false), and confirm the DB connection name and that SQL Bridge is installed.

## Verify

The stream is not proven by the scan returning. Read the manager through the module hook:

```python
mod = <the eventstream module object>
m = mod.getHook().getClass().getDeclaredMethod("getEventStreamManager")
m.setAccessible(True)
mgr = m.invoke(mod.getHook())
mgr.listAllEventStreams()
mgr.getState(project, name)          # expect RUNNING
mgr.getDiagnostics(project, name)    # per-stage metrics: state GOOD, errors=0, received.count
```

Then change an upstream tag, and check the row landed in the target table. Restore the tag afterwards.
`skipInitialValues=false` emits one `isInitial=true` event per matched tag on start.

## Traps

- `getScanInformation().scanActive` is a **method**. `if scanInfo.scanActive:` is always
  truthy. Call `scanActive()` when waiting for a scan to finish.
- Scans can take ~100 s. A new stream may **not load on the first scan** (manager `listAllEventStreams()`
  stays empty). Touch or rewrite `config.json` and `requestScan()` again.
- A clean scan and a present resource prove nothing: only `getState` = RUNNING plus a landed
  row proves the stream works.
- Filter/transform `userCode` is a function body: a missing tab indent is a compile error at load.
- HTTP source mounts at `/system/eventstream/{project}/{resourcePath}`; Kafka source/handler need
  the Kafka Connector module (not in every install), HTTP source/handler need Web Dev, Database
  handler needs SQL Bridge. Check installed modules before designing (`get_module_health`).
