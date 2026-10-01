# Jython 2.7 Constraints

The gateway and Designer embed **Jython 2.7.4** (verified: `sys.version` →
`2.7.4 (heads/ia/2.7.4 ... Apr 27 2026)`, `[OpenJDK 64-Bit Server VM (Azul Systems)]`,
JVM 17, gateway 8.3.9). Every gateway/Designer/Perspective script
runs under this interpreter. It is CPython **2.7** semantics on a JVM — not Python 3,
not full CPython 2.7 stdlib.

All checks below were run through `run_gateway_script` on a live 8.3.9 gateway
(baseline: `references/VERIFIED.md`).

## Language — hard limits (verified)

| You cannot write | Proof | Use instead |
|---|---|---|
| f-strings `f'{x}'` | `compile("f'{1}'","<t>","eval")` → `SyntaxError: no viable alternative` | `"%s" % x` / `"{}".format(x)` / `+` |
| `print(a, end='')` / `print(a, b, sep=)` | `compile("print('hi', end='')")` → `SyntaxError` | `from __future__ import print_function` at top of file, **or** the `print x` statement |
| true division | `7/2` → `3`, `-7/2` → `-4` (floor), `7/2.0` → `3.5` | force a float operand, or `from __future__ import division` |
| `x: int` type hints, `typing` | `import typing` → `ImportError: No module named typing` | docstrings / comments |
| `pathlib` | `import pathlib` → `ImportError` | `os.path`, `os` |
| `enum` | `import enum` → `ImportError` | module-level constants |
| `async`/`await`, `asyncio` | `import asyncio` → `ImportError` | `system.util.invokeAsynchronous` |
| walrus `:=`, dict merge `|`, `match` | Py3.8+ syntax | — |

**str vs unicode (Py2):** `type('x')` → `str`, `type(u'x')` → `unicode`, both are
`basestring`. `system.*` and Java calls return **`unicode`** (e.g. `list(ArrayList)`
→ `[u'a', u'b']`). Coerce tag names/paths with `str(...)` before using them as dict
keys or string-formatting into paths — mixed `str`/`unicode` keys silently miss.
`long` exists (`2**64` → `...L`).

**`exec` is a statement.** Use the qualified form `exec script in g, g` (not
`exec(script, g)`) — confirmed working; `exec "y = x + 1" in g, g` → `g['y'] == 42`.
This is the pattern the WebDev script-exec endpoint itself uses (`memory/ignition-mcp-setup.md`).

## Stdlib — present vs absent (verified by `__import__`)

**Present:** `os` `sys` `re` `math` `json` `datetime` `collections` `functools`
`itertools` `string` `io` `codecs` `csv` `hashlib` `base64` `random` `time`
`threading` `subprocess` `urllib` `urllib2` `httplib` `socket` `struct` `decimal`
`uuid` `traceback` `logging` `copy` `pickle` `shutil` `tempfile` `glob` `zipfile`
`xml.etree.ElementTree` `StringIO` `cStringIO` `Queue` `ConfigParser`.

**Absent:** `pathlib` `typing` `enum` `asyncio` `sqlite3` (and anything Py3-only:
`dataclasses`, `pathlib`, `secrets`, `f`-string machinery).

> `subprocess` and `socket` *import* but are Java-backed and partial — prefer Java
> (`java.lang.ProcessBuilder`, `java.net`) or `system.net.*` for anything non-trivial.
> Do not shell out from a gateway script to "fix" something the platform API covers.

## Java interop (verified)

- `from java.util import ArrayList, HashMap, Date` — direct import of `java.*` /
  `com.inductiveautomation.*` classes works in gateway scope.
- **Catch Java exceptions with a bare `except:`** then `sys.exc_info()` — a Java
  `NumberFormatException` is *not* a Python `Exception` subclass, so
  `except Exception:` misses it. Confirmed: `Integer.parseInt("x")` caught only by
  bare `except:`, `sys.exc_info()[0]` → `<type 'java.lang.NumberFormatException'>`.
- Java collections returned to Jython yield `unicode` strings and need `list()` /
  `dict()` wrapping to get Python semantics.

## Scope — what `system.*` is where

Full context map (gateway vs Perspective session/view vs Vision vs Designer,
worked failure modes, the Python-3-assumption trap): `references/gateway/
scripting-contexts.md`. Table below is the quick-reference only.

| Scope | Has | Not |
|---|---|---|
| **Gateway** (timer/tag-change/message scripts, `run_gateway_script`, WebDev, gateway startup) | `system.tag`, `system.db`, `system.util`, `system.alarm`, `system.opc`, `system.dataset`, `system.date`, `system.net`, `system.user`, `system.security`, `system.perspective.send*` | `system.gui`, `system.nav` (Vision client only); `system.perspective.navigate/openPopup` (session-bound) |
| **Perspective session** | `system.perspective.*` (navigate, popups, docks, `getSessionInfo`), `system.tag`, `system.db` via gateway | `system.gui`, `system.nav` |
| **Vision client** | `system.gui`, `system.nav`, `system.vision` | — |
| **Designer** | most of gateway + client, plus resource APIs | runtime session context |

Verified in gateway scope: `system.tag`/`system.db`/`system.util`/`system.perspective`
present; `system.gui`/`system.nav` **absent**.

## The `run_gateway_script` sandbox specifically

- **Classloader isolation.** `import`ing a module's gateway classes directly fails —
  `from com.inductiveautomation.perspective.gateway import ...` →
  `ImportError: No module named perspective`. Reach them through the module manager:

  ```python
  from com.inductiveautomation.ignition.gateway import IgnitionGateway
  ctx = (IgnitionGateway.get().getModuleManager()
         .getModule("com.inductiveautomation.perspective").getHook().getContext())
  # ctx -> PerspectiveGatewayContext  (verified)
  ```
  `IgnitionGateway.get()` itself and `java.*` / core `com.inductiveautomation.ignition.*`
  imports work fine — it is *module* packages that are isolated.
- **~110 KB result cap.** A large return value / stdout is truncated
 . Dump big output to a workspace file from the script
  (`open(r"C:\...", "w")`) and read the file separately.
- The gateway runs as the same OS user as your workspace, so a gateway script can
  `open()` a path on the Windows host directly — this is how cleaned artefacts are
  fed in.

## The FSYNC trap (summary)

Writing a project-resource file from Jython with `open(p,"wb").write(...)` and no
`os.fsync()` lets the `ResourceTreeFileWatcher` hash a **0-byte** file, cache the
empty-string digest in `data/projects/.resources/` and in ProjectManager memory, and
that poisoned entry **survives later rewrites** (the watcher keys off `resource.json`,
not the data file). Symptom: `resource.getData(f).get().getBytes()` length 0 though
the disk file is fine; a timer script then throws `SyntaxError: expecting INDENT`.

**Fix — every file, every time:**

```python
f = open(path, "w")
f.write(text); f.flush(); os.fsync(f.fileno()); f.close()
```

Write **data files before `resource.json`**. If a resource is already poisoned, write
it under a **fresh resource name** — the cached bad hash will not clear otherwise.
The gateway also holds **file locks** on live resource dirs, so `shutil.rmtree` on one
throws `unlink()` errors. Full write protocol and the `resource.json` envelope:
`skill/references/gateway/resource-formats.md`; helper: `<repo>/scripts/lib/gateway_io.py`
(`fsync_write`, `request_scan`, `verify_resource`).

## Threading

- Never do long work on the gateway event thread (tag-change, timer with
  `sharedThread=true`, message handlers) — it stalls tag processing. Offload with
  `system.util.invokeAsynchronous(func)` (verified present).
- Timer scripts: `sharedThread=false` gives the script its own thread; keep the body
  short regardless.
- `threading` imports, but prefer `system.util.invokeAsynchronous` /
  `system.util.invokeLater` (Vision) so Ignition owns the lifecycle.
- Gateway scripts have no session/page context — `system.perspective.navigate` etc.
  will fail; use `system.perspective.sendMessage` to reach sessions.

## agent rules

1. No f-strings, no `print(...)` kwargs, no `typing`/`pathlib`/`enum` — the file will
   not compile and the whole resource fails to load.
2. Force float division where you mean it (`a / float(b)`).
3. `str()`-coerce every tag path / name coming back from `system.*` before using it
   as a dict key or formatting it into another path.
4. Catch Java exceptions with a bare `except:` + `sys.exc_info()`; log the real type.
5. `flush()` + `os.fsync()` on **every** resource file; data before `resource.json`.
6. Reach module classes via `IgnitionGateway.get().getModuleManager()...getContext()`,
   never a direct module `import`.
7. Big output → write to a host file, don't return it.
8. No long work on the gateway event thread; `system.util.invokeAsynchronous`.
9. Verify at runtime (`getProjectCache()` / a tag read), never trust an HTTP 200
   (`skill/references/workflow.md`).

## Smells

- `from __future__ import print_function` in one file and `print x` statements in the
  next — pick one per codebase.
- `except Exception:` around a block that calls Java — Java errors slip through.
- `open(path,"w").write(json)` with no `flush`/`fsync`.
- A gateway timer script that reads 60 tags, formats a dataset, and writes it back
  **inline** every tick — move it off-thread or lengthen the period.
- `import subprocess` / `os.system` in a gateway script to do something
  `system.net` / `system.file` / Java already does.
- Re-`configure`-ing a poisoned resource under the same name and expecting the empty
  hash to clear.

## Site layer

No site-specific Jython choices belong here. Project scripting conventions (package
layout, logging names, shared-library structure) go in the project conventions if adopted.
