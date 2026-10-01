# Ignition 8.3 — Scripting model, Designer and project structure

Sources: live docs at `docs.inductiveautomation.com/docs/8.3/` — `platform/scripting/**`, `platform/designer/**`, `platform/projects/**`, `platform/localization-and-languages/**`, `scopes/**`, `tutorials/**`, and the appendix pages `scripting-object-reference`, `resource-json-file`, `symbol-reference`.

---

## Execution scopes

Ignition scripts run in one of three scopes. **Where a script is written determines the scope it executes in** — not where you happened to open the Designer, and not what the script "looks like it should do."

* **Gateway scope** — runs on the Gateway itself. Scripts here cannot reach components in a Vision Client or Perspective Session. Tags live in the Gateway scope, so Tag Event Scripts always run here. Gateway Event Scripts (startup/shutdown/timer/tag-change/message/scheduled) are Gateway-scoped project resources.
* **Perspective Session scope** — runs as part of a Perspective Session, but **executes on the Gateway, not in the browser**. It is a distinct scope from plain Gateway scope even though the code runs on the same JVM — a different set of `system.*` functions is available (see below), and output/logging behaves differently (`system.perspective.print` vs `print`).
* **Vision Client scope** — runs inside a specific instance of a Vision Client (a JVM on the operator's machine).

### How scope is enforced

Ignition's autocomplete popup (`Ctrl+Space` after typing `system.`) **only shows functions scoped to the current script location** — if a system function doesn't appear, it isn't available in that scope. Autocomplete also offers **Parameter Assistance** (tab through a multi-parameter call filling in one argument at a time) and picks up docstrings written in Google Python Style Guide format on project-library functions/classes, surfacing the description/args/returns in the hint popup:

```python
def setMode(mode):
    """Changes the mode of the running system.

    Args:
        mode: An integer representing the mode to switch to.
    Returns:
        A boolean indicating whether the switch succeeded.
    Raises:
        Error: If communications are down, an exception will be thrown.
    """
```

Both Automatic Activation and Parameter Assistance can be turned off via right-click in the Script Editor if they get in the way. The Project Library's own script-hint dropdown lets you pick which scope populates the *editor's* hints while writing a shared script — this only affects what autocomplete shows you, not what actually runs at Gateway vs Client/Session scope at runtime:

| Script Hint Scope value | What populates the hints |
|---|---|
| `None` | Neither Designer nor Gateway scope functions |
| `Designer` | Designer-scope functions |
| `Gateway` | Gateway-scope functions |
| `All` | Both Designer and Gateway scope functions |

### What's available where (by the numbers)

The live "Functions by Scope" reference in the docs (`/scopes/gateway`, `/scopes/perspective-session`, `/scopes/vision-client`) lists **367** functions available to Gateway scope, **332** to Perspective Session scope, and **356** to Vision Client scope. Diffing the three lists is the fastest way to know if a function you want is reachable from where you're writing:

| Module / function | Gateway | Perspective Session | Vision Client |
|---|:---:|:---:|:---:|
| `system.config.*` (resource config CRUD) | ✔ | — | — |
| `system.dnp.*` (legacy DNP) | ✔ | — | — |
| `system.dnp3.*` | ✔ | ✔ | ✔ |
| `system.eventstream.*` | ✔ | — | — |
| `system.kafka.*` | ✔ | — | — |
| `system.iec61850.*` | ✔ | ✔ | — |
| `system.groups.*` | ✔ | ✔ | — |
| `system.roster.*` | ✔ | ✔ | — |
| `system.tag.query` | ✔ | — | — |
| `system.util.getModules` | ✔ | — | — |
| `system.perspective.*` | subset (message/session control) | full set | — |
| `system.vision.*` (dialogs, windows, desktop) | `logout` only | `logout` only | full set |
| `system.secsgem.*` extras (`copyEquipment`, `getToolProgram*`, `startSimEventRun`, …) | — | — | ✔ |
| `system.bacnet.*` raw read/write | ✔ | — | — |
| `system.bacnet.synchronizeTime/writeWithPriority` | ✔ | ✔ | ✔ |
| `system.tag.readBlocking/writeBlocking`, `system.dataset.*`, `system.date.*`, `system.db.*`, `system.math.*`, `system.net.*`, `system.opc(ua)/opchda.*`, `system.historian.*`, `system.file.*`, `system.user.*`, `system.security.*`, `system.serial.*`, `system.sfc.*` | ✔ | ✔ | ✔ |

Practical reading of this table: Gateway scope is the only place with direct access to resource/config management, legacy protocol modules, and cross-project `system.tag.query`; Perspective Session scope gets the full `system.perspective.*` surface (dialogs, navigation, docks) because the session lives there logically even though code executes on the Gateway; Vision Client scope is the only place with the `system.vision.*` UI/dialog/desktop functions (`showMessage`, `openWindow`, `getScreens`, keyboard/touchscreen control, etc.).

### Threading model

Ignition schedules event-driven scripts on pooled or dedicated threads depending on the resource type and its configuration:

* **Timer Scripts** (Gateway Event Scripts) choose **Shared** (default; all Timer Scripts share one thread — cheap, but a slow script blocks the others) or **Dedicated** (own thread — use when consistent timing matters and other timers shouldn't be able to delay it). Delay Type is **Fixed Delay** (waits the delay *after* each run finishes — default, safest) or **Fixed Rate** (attempts to fire at a fixed cadence regardless of run time; see `java.util.Timer.scheduleAtFixedRate`).
* **Tag Change Scripts** each run in their **own separate thread** per execution, so one long-running tag-change script cannot block another tag's change script. They fire in the Gateway scope and don't require a live Client/Session.
* **Gateway Message Handlers** choose **Shared** (pooled, ordered; can queue up under load) or **Dedicated** (own thread, more Gateway resource cost, avoids being blocked by other handlers).
* **Component event handlers** (Vision `actionPerformed`, Perspective `onActionPerformed`, etc.) run on the **GUI/render thread** of the Client or Session. A slow script here freezes the screen until it returns — see Practical guidance below for the fix (`invokeLater`/`invokeAsynchronous`, never `time.sleep`/busy `while` loops on this thread).
* **Client/Session Startup Scripts** and other lifecycle scripts run once, synchronously, at the relevant lifecycle point (Gateway start, Client login, Session open) and can gate downstream startup work.

---

## Python / Jython in Ignition

Ignition scripting is **Python 2.7 syntax, run on Jython 2.7** — the Java implementation of Python (as opposed to the far more common CPython implementation most people mean when they say "Python"). Jython code compiles to JVM bytecode and can be further JIT-compiled by the JVM, which is why it tends to be fast. Because it's Jython, **the entire Java standard library is available for import** alongside the Python standard library, and you can subclass Java interfaces from Python:

```python
from java.lang import System
from java.io import File, FilenameFilter

class ExtensionFilter(FilenameFilter):
    def __init__(self, extension=".txt"):
        self.extension = extension.lower()
    def accept(self, directory, name):
        return name.lower().endswith(self.extension)

homeDir = File(System.getProperty("user.home"))
for filename in homeDir.list(ExtensionFilter(".pdf")):
    print filename
```

Java standard library reference: the JavaDocs at `docs.oracle.com/javase/8/docs/api/`. Python standard library reference: `docs.python.org/2/library/index.html` (**2.x docs — not 3.x**, a very common trap for developers coming from modern Python).

### Coming from CPython 3 — what trips people up

* **`print` is a statement, not a function.** `print "hello"` works; `print("hello")` also happens to work in Jython 2.7 (parens are just grouping a single expression) but `print("a", "b")` does **not** behave like Python 3's function — it prints a tuple.
* **Integer division floors.** `4 / 5` is `0`, not `0.8`; you need at least one operand to be a `float` (`4 / 5.0`) to get true division. `//` is floor division explicitly.
* There is a **`long` type** distinct from `int` (unlimited precision vs. 32-bit-minimum `int`) — a CPython-3 developer used to unified `int` should watch for this in older example code and in range/size math.
* **Unicode is not automatic.** Non-ASCII string literals need a `u` prefix (`u"äöü"`); this matters in practice because some system functions fail on tag paths or strings with special characters if they aren't unicode-marked.
* **Two parallel exception hierarchies.** Regular Python exceptions (`except ZeroDivisionError:`, etc.) do **not** catch Java exceptions thrown by underlying `system.*` calls, because Jython models Java exceptions separately. Catch `java.lang.Exception` (catches most recoverable Java exceptions) or `java.lang.Throwable`/`java.lang.Error` for the small set of "unrecoverable" JVM errors (`OutOfMemoryError`, `StackOverflowError`). A robust handler catches both:

```python
from java.lang import Throwable
try:
    riskyWork()
except Exception as e:      # Jython/Python-side exceptions
    handle(e)
except Throwable as t:      # Java-side exceptions
    handle(t)
```

* **Datasets are not a native Python type.** Ignition's `Dataset`/`PyDataset` objects exist specifically because Python has no spreadsheet-like tabular type; `system.dataset.*` bridges the gap (see Practical guidance). As of 8.3, datasets support direct Python-style indexing/iteration (`for row in dataset: print row["City"]`) without first converting through `system.dataset.toPyDataSet()` — that conversion function still works for backward compatibility but is no longer required.
* **Colors are just tuples.** `(255, 0, 0)` assigned to a `foreground` property works as RGB; `system.vision.color(255,0,0)` is the function-call equivalent.
* Third-party pure-Python libraries (`.py` files, version 2.7-compatible only) go in the `user-lib/pylib` folder under the Ignition install directory (path differs by OS — Windows: `Program Files\Inductive Automation\Ignition\user-lib\pylib`; Linux: `/usr/local/bin/ignition/user-lib/pylib`; macOS: `/usr/local/ignition/user-lib/pylib`). Java `.jar` libraries are added to the Gateway's classpath through the Gateway's module/library mechanisms rather than this folder (project-library code just does `import myLibrary` / `from java.pkg import Class` once the jar is on the classpath).
### Built-in data structures at a glance

**Strings** — single/double/triple-quoted, `u"…"` for unicode, `r"…"` for raw (no escape processing — the standard way to write a Windows path: `r"C:\Folder\file.txt"`). Indexed and sliceable like any sequence (`a[4]`, `a[2:5]`, `a[-2:]`). String formatting uses `%`-substitution (`"I have %i apples" % (8)`, or with several values `"%i, %i" % (a, b)`), not `.format()` or f-strings. Common methods: `find`/`rfind` (returns `-1` if absent), `upper`/`lower`/`capitalize`/`title`, `strip`/`lstrip`/`rstrip` (optionally with a character set to strip), `count`, `split`/`rsplit` (optional delimiter + maxsplit), `join` (called *on* the separator: `"-".join(["a","b"])` → `"a-b"`), `replace(old, new[, count])`.

**Lists** `[ ]` (mutable) vs **Tuples** `( )` (immutable) — both are ordered sequences supporting concatenation (`+`), indexing/slicing, and nesting. List-only mutators: `append(x)`, `insert(i, x)`, `remove(x)` (removes first match), `pop([i])` (removes & returns; defaults to last item), `reverse()`. Both support `len()`, `x in seq`, `min()`/`max()`, `.index(x)`, `.count(x)`.

**Dictionaries** `{key: value, ...}` — unordered key/value maps; keys can be numbers, strings, or tuples. `dict[key]` raises if the key is absent (assigning to a missing key creates it); `del dict[key]` removes a key; `key in dict` tests membership; `.keys()`/`.values()`/`.clear()` behave as expected. Common in Ignition for Message Handler `payload`s and dynamically-built alarm rosters.

**Numeric types** — `int` (≥32-bit), `long` (unlimited precision, no CPython-3 equivalent), `float`, and `bool` (a subtype of `int`: `True`/`False` == `1`/`0`). Mixed-type arithmetic promotes to the more precise type (`int + float → float`); `int / int` floors (see above); `**` is power (`5 ** 3` → `125`); `//` is explicit floor division and `%` is modulo, both usable on floats too.

**Dates** — prefer `system.date.*` (`now()`, `getDate(y,m,d)` — midnight by default, `setTime(date,h,m,s)`, `format(date, pattern)`, `addMinutes`/`add*`) over Java's `java.util.Calendar` (legacy; note January is month **0**) or Python's own `time`/`datetime` standard-library modules — components with a Date-typed property generally expect a **Java date object**, and a `datetime.datetime` built purely with Python's own library will raise when assigned to one. Date-format pattern characters (subset, used by `system.date.format` and Java's `SimpleDateFormat`): `yyyy`/`yy` year, `MM`/`MMM`/`MMMM` month, `dd` day of month, `EEEE`/`EEE` weekday name, `HH` 24-hour, `hh` 12-hour, `mm` minute, `ss` second, `SSS` millisecond, `a` AM/PM, `zzzz`/`z` time zone name, `Z`/`X` numeric time zone offset (RFC-822 vs ISO-8601).

**Datasets** (`system.dataset.*`) — Ignition's tabular type, not native to Python; created with `system.dataset.toDataset(headers, rows)`. **Immutable**: `setValue`/`addRow`/`deleteRow`/etc. all return a *new* dataset rather than mutating in place. As of 8.3, iterate/index directly (`for row in ds: row["ColName"]`, `ds[rowIdx][colIdx]`) without first calling the now-optional `toPyDataSet()`. Useful methods: `getColumnAsList(i)`, `getColumnCount()`, `getColumnIndex(name)`, `getColumnName(i)`, `getRowCount()`, `getValueAt(row, col)`.

### Control flow and built-ins quick reference
`if`/`elif`/`else` (lowercase keywords, colon-terminated, body indented — no braces); `elif` chains are unlimited and `else` is optional. `for item in sequence:` iterates any sequence (list, tuple, string, dataset, `range(...)`); `while condition:` repeats until false. `break` exits the loop entirely; `continue` skips to the next iteration. `pass` is a syntactic no-op — useful as an explicit "not implemented yet" placeholder in an `elif`/`except` branch that must have *some* body.

```python
# common bulk-tag-path idiom: generate paths with range() + string formatting
tagPaths = []
for num in range(1, 6):
    tagPaths.append("[Provider]Folder/Sub_Folder_%i/Tag" % num)
results = system.tag.readBlocking(tagPaths)

# guard against an infinite while loop with a counter as a second condition
counter = 0
while True and counter < 1000:
    counter += 1
```

A forgotten increment inside a `while` is the single most common cause of an Ignition Designer/Client hang during development — always give a `while` loop a guaranteed exit (a counter bound, as above, or prefer a `for`/`range()` when the iteration count is knowable up front).

Frequently-used built-ins: `type(x)`/`isinstance(x, cls)` (prefer `isinstance` — it also matches subclasses, and `basestring` catches both `str` and `unicode` in one check), `int()`/`long()`/`float()`/`str()`/`unicode()`/`bool()` for casting (casting a decimal-containing string to `int()` raises `ValueError` — go through `float()` first, or use `round()`), `round(x[, digits])`, `len(sequence)`, `range([start,] stop[, step])` (stop is exclusive; a negative `step` counts down). Casting `bool()`: `0`/`""`/empty-sequence are `False`, everything else is `True`.

### User-defined functions and scope
Defined with `def`; arguments can carry default values (`def cap(x, min=0, max=100):`), making them optional at the call site, and can be passed **by keyword** at the call site for readability (`cap(150, max=200)`) — a keyword argument may not precede a positional one in the same call (`cap(max=200, 150)` is a syntax error). Functions are **first-class objects**: they can be assigned to variables, stored in a list/dict, and passed as arguments to another function — the pattern several `system.*` functions rely on (`system.vision.createPopupMenu`, the `runScript` expression function, `system.util.invokeAsynchronous`'s callback) is exactly "pass a function object in, it gets called later":

```python
def isEven(num):
    return num % 2 == 0

def extract(filterFunction, items):
    return [x for x in items if filterFunction(x)]

extract(isEven, range(10))   # [0, 2, 4, 6, 8] — isEven is passed, not invoked
```

**Scope**: a variable is defined at the point it's *assigned*, and which scope it belongs to depends on where that assignment happens — not on braces or indentation blocks. A function body gets its own local scope; a variable assigned inside an `if`/`for`/`while` block at the top level of a script, by contrast, is **not** block-scoped and remains visible after the block ends (unlike Java/C-family languages) — a frequent surprise for developers used to block-scoped languages, and a common source of "it works but I don't know why" scripts that happen to rely on a loop variable leaking out of its `for`.

**Quick reference, in code:**

```python
# strings — % formatting, not .format()/f-strings; r"" for raw (Windows paths)
name = "world"
print "Hello, %s! You have %i items." % (name, 3)
path = r"C:\Data\Exports\file.csv"

# lists vs tuples — lists mutate, tuples don't
fruits = ['Apples', 'Oranges', 'Bananas']
fruits.append('Grapes')
point = (10, 20)          # point[0] = 5 would raise TypeError

# dictionaries — keyed lookup, KeyError on a missing key unless you guard it
scores = {'Bob': 89.9, 'Joe': 188.72}
scores['Amir'] = 45.89                 # add
if 'Joe' in scores:
    print scores['Joe']
for key in scores.keys():
    print key, scores[key]

# dates — build with system.date, not Python's own datetime module
start = system.date.getDate(2026, 0, 1)          # Jan is month 0
formatted = system.date.format(start, "yyyy-MM-dd HH:mm:ss")
```

### JSON in Ignition
Ignition uses JSON internally for a lot more than script data interchange — **Tags** (export/import, and `system.tag.configure` accepts either a JSON string or object) and **Perspective component properties** (a component's `props` tree *is* structurally a JSON document; only properties that differ from their type's defaults are actually serialized/sent to the client) are both JSON-shaped. `system.util.jsonEncode`/`jsonDecode` convert between a JSON string and native Python objects (dicts/lists), which is the standard way to consume a REST API response fetched with `system.net.httpClient()`. Inside a Tag UDT, `{ }` is reserved syntax for a parameter reference, so a literal JSON-looking string value in a UDT property needs care to avoid collision. Looping a decoded JSON structure is just nested dict/list traversal:

```python
json = self.items                      # e.g. a JSON array of objects
companies = json["companies"]           # a list
for company in companies:
    name = company["companyName"]
    city = company["cityName"]
```

* **The historically-included SUDS SOAP library is gone.** It used to ship in the Python Standard Library bundled with Ignition; it's now removed and unmaintained. Its docs are kept only for legacy scripts (`Web Services, SUDS, and REST` page). New SOAP integrations should use a REST/HTTP approach via `system.net.httpClient()` where the target service supports it, or bring in a third-party library.

**Tags are JSON too.** `system.tag.configure` accepts either a JSON string or a native Python/dict structure defining one or more tags; UDT instance overrides are expressed as simple property redefinition, while structured config (Event Scripts, Alarms) merges with the inherited UDT definition rather than replacing it wholesale. The Tag Browser can copy selected tags as JSON straight to the system clipboard, and pasting JSON back into a Tag Browser (in the same Designer or a different one entirely) creates or overwrites tags accordingly — a quick way to move a handful of tags between projects without a full tag export file. One JSON-in-UDT gotcha: inside a UDT, `{ }` is reserved syntax for a parameter reference, so a literal string property whose value happens to look like a JSON object needs care to avoid being misread as one (the editor renders literal strings in black, parameter references in grey italics, as a visual tell).

* **The historically-included SUDS SOAP library is gone.** It used to ship in the Python Standard Library bundled with Ignition; it's now removed and unmaintained. Its docs are kept only for legacy scripts (`Web Services, SUDS, and REST` page). New SOAP integrations should use a REST/HTTP approach via `system.net.httpClient()` where the target service supports it, or bring in a third-party library.

---

## Where scripts live

Location determines scope and determines *when* the code runs. In rough order of how often you'll touch them:

### Project Library (`shared`/project scripts)
User-defined Python modules/packages stored as a project resource, browsable under **Scripting** in the Project Browser. Two resource types: **Scripts** (hold functions/objects) and **Packages** (folders for organizing scripts). Anything defined in one is callable from anywhere else in the same project once the project is **saved** (`myFuncs.hello()`), exactly like calling a `system.*` function.

Because Python is dynamic, the top-level code in a project library module actually **executes** whenever the module is (re)loaded — on Script Console startup, on save, when third-party libraries on the Gateway change, etc. Anything not wrapped in a function or class definition at the top level will re-run on every reload, so **wrap all project-library code in functions/classes**.

Project Library scripts are normally only reachable **from the project they're defined in** — a Gateway-scoped Tag Event Script in a *different* project can't call them (you'd get `global name 'yourScript' is not defined`). The one exception is the **Gateway Scripting Project**: set a project name in the Gateway's `Gateway Scripting Project` setting (Config → Gateway Settings) and that project's library becomes callable from *any* Gateway-scoped script (tag events, other projects' Gateway Event Scripts, etc.) without qualifying it by project name. This setting has no effect on that project's own Gateway Event Scripts (startup/shutdown/update/message) — those are always project-resources and only run for the project they belong to.

### Gateway Event Scripts
Project resources (stored as readable `.py` files, included in project backups/exports) that run **on the Gateway**, always active regardless of whether any Client/Session is open. Found in the Project Browser under **Scripting → Gateway Events** or the Designer's **Project** menu.

* **Startup** — runs when the Gateway starts *and* whenever the project restarts (e.g., saving a change to a Gateway Event Script triggers a project restart, so this fires more than you might expect during development). Order: Gateway process starts → projects start (Gateway-scoped resources like Transaction Groups/SFCs start, Startup Scripts run per-project) — client launches are not part of this sequence.
* **Shutdown** — runs on project shutdown (which includes disabling the project or a genuine Gateway shutdown), **not** on an abrupt power loss/hard kill.
* **Update** — runs after the project is saved/updated on the Gateway; receives `actor` (who/what triggered it) and `resources` (a dict with `added`/`removed`/`modified` resource lists and a `manifestChanged` boolean). This is the natural hook for "auto-commit to git on save" automation (see Tutorials section).
* **Timer** — fires on a fixed delay/rate; multiple Timer Scripts can coexist (right-click menu to add/copy/rename/delete); see Threading model above for Shared vs Dedicated.
* **Tag Change** — fires when any of a configured list of tag paths changes; Change Triggers can be Value/Quality/Timestamp (only fires once per tag change even if several trigger types match). Supports wildcards at the end of a tag path to match a whole folder; as of **8.3.4**, wildcards can also be used at the tag-name level, not just the folder level. Exposes:
  * `initialChange` (bool) — true only on the very first execution after a project (re)starts (`executionCount == 0`); use to skip "startup noise".
  * `executionCount` (int) — resets to 0 whenever event scripts restart (project library edits, event-script edits+save, etc.).
  * `newValue` / `previousValue` — `QualifiedValue`-like objects (`.getValue()`, `.getQuality()`, `.getTimestamp()`).
  * `event` — richer object: `getCurrentValue()`, `getPreviousValue()`, `getTagPath()`, `changes` (set of `TagChangeType`), `tagPath.getItemName()` / `tagPath.getParentPath()`.
  * Client Tags do **not** trigger Gateway Tag Change Scripts (use a Client Event Script for that).
* **Message** — see Message handlers below.
* **Scheduled** — cron-style, fires at fixed times of day per the Gateway clock (see Crontab Formatting Reference in the appendix, not scraped here).

### Client / Session event scripts
Vision **Client Event Scripts** (`Project` menu → **Client Events**, or the Project Browser) and Perspective **Session Event Scripts** mirror much of the Gateway Event Script shape (Startup/Shutdown/Timer, plus a Tag Change-equivalent for Client Tags) but execute in Vision Client scope / Perspective Session scope respectively, on the Client JVM / the Gateway-hosted session, rather than in plain Gateway scope. Referenced throughout the docs as the mechanism for:

* **Location-based access control** — a Client Startup Script reads `[System]Client/Network/Hostname` (or an IP/tag/database lookup) and either blocks the client entirely or routes it to a different opening window based on where it's logging in from:

```python
hostname = system.tag.readBlocking(["[System]Client/Network/Hostname"])[0].value

if hostname != "Machine A Computer":
    system.vision.showMessage("This project can only be accessed from the 'Machine A Computer'.")
    system.vision.exit()
```

* **Per-session/per-client locale initialization** and other startup personalization pulled from [System Tags](for Vision) or Session Properties (for Perspective).
* **Client Tag change reactions** — Client Tags do not trigger Gateway Tag Change Scripts (Client Tags don't exist on the Gateway), so a Client Event Script is the only way to react to one changing.

A **Client Event Script preventing a write** is a common false trail when troubleshooting "why won't my write go through" — even with Comm Mode set to Read/Write, an enabled Client Event Script can itself be blocking the write; check for one before assuming a Comm Mode or security problem. Also note: some events, notably Client Startup Scripts, **do not fire in the Designer's Preview Mode** — get in the habit of testing with a real launched Client for anything startup-related. The default Vision project template ships a pre-wired **Client Event Timer** script (fires every 5 seconds, locks the screen after 5 minutes of inactivity) — easy to forget it's there; disable/delete it via **Project → Client Events → Timer** if not wanted.

### Component event handlers
Both Vision and Perspective offer per-component scripting (button click, property change, etc.) via **Component Scripting** (Vision) / **Configure Events** (Perspective). These execute in the scope of wherever the component lives (Vision Client or Perspective Session) and, critically, on that runtime's UI thread (see Threading model / Practical guidance).

### Tag event scripts
Configured directly on a tag (fires on value change or alarm event) — Gateway-scoped by nature, since tags live in the Gateway. Same shape as the Gateway Tag Change Script event described above, just attached to the tag itself instead of being a project-level list.

### Expression vs script (choosing the right tool)
Three languages coexist and are easy to confuse when skimming a UI field: **Python Scripting**, the **Expression Language**, and **SQL**. Quick tells:

| Signal | Scripting | Expression | SQL |
|---|---|---|---|
| Comment syntax | `# comment` | `// comment` | `-- comment` |
| UI cues | "Script"/"Event" wording, an Event Handler list on the left | An "Expression" field, an `ƒ` Expression Function button | "Query"/"Database" wording, a database-connection picker |
| Nature | Imperative, statements, variables, side effects | Purely functional — a single expression that returns a value, no variables/statements | Declarative row/column operations against a database |
| Typical homes | Event handlers, Gateway/Client/Session events, Tag events | Property Bindings, Expression Tags/Derived Tags, Alarm Pipeline Expression/Switch blocks, Transaction Group Expression Items, Report Parameters, SFC Transitions | SQL Query Bindings, Named Queries, Database Query Browser, Reporting SQL data sources, Query Tags |

SQL can also be called **from** a script (`system.db.runPrepQuery`, `runPrepUpdate`, etc.) — the recommendation is to get the raw query working first in the Database Query Browser (with static stand-in values for parameters), then move it into the script, since the Script Editor's syntax highlighting only understands Python, not embedded SQL.

### Other scripting touchpoints
A few less-obvious places script code runs, worth knowing about even outside the core event-script model:

* **Reporting** — a Scripting Data Source computes/returns a report's data programmatically instead of via SQL; chart scripting customizes chart rendering; a Run Script scheduled-report action executes arbitrary code as part of report generation/delivery.
* **Alarm Notification Pipelines** — a **Script Block** runs inline as an alarm event travels through the pipeline (can inspect/modify the event, or call `cancelNotification()` to stop it); a **calculated roster** uses a script to build the notified-user list dynamically at runtime instead of a static list.
* **Sequential Function Charts (SFCs)** — each step/transition in the flowchart can run a script; because SFC execution is inherently ordered (a step's script completes before the chart advances), this is the natural tool when a multi-step process genuinely needs "wait for this to finish before starting that," which a Gateway Timer Script or Tag Change Script can't guarantee on its own.

### The Script Console
A live Python REPL, **Designer-only**, opened via **Tools → Script Console**. Two panes: the **Multiline Buffer** (left, write a whole script, `Execute` to run, supports folding/comments/font-size-via-Ctrl+scroll/Find-Replace via `Ctrl+R`) and the **Interactive Interpreter** (right, one line at a time, `Enter` to run, command history via arrow keys). It executes in **Designer/local scope** — it cannot touch components on an open window/view, but it *can* call Project Library and Gateway-scoped scripts (reset the console via the Reset icon after adding a new project script so it picks it up). Gateway-scoped print/logger output never appears here or in the Output Console — check `wrapper.log` or the Gateway's Logs page instead.

---

## Message handlers

Gateway Message Handlers are scripts, attached to a project, that can be invoked **from any project or even a remote Gateway** — the mechanism for cross-scope and cross-Gateway calls. Configured under the Message folder of Gateway Event Scripts; each handler needs a project-unique name, a **Threading** mode (Shared/Dedicated — see Threading model), and optional **Security** (zone + role requirements for who's allowed to invoke it).

Inside the handler, a single object is available: **`payload`**, a plain `dict` of whatever the caller passed in.

```python
value1 = payload["MyFirstValue"]
value2 = payload["MySecondValue"]
```

Three functions invoke a message handler, from any scope that has them available (see the scope table above — Vision Client scope only has `sendMessage`/`sendRequest`/`sendRequestAsync` without the target handler needing to be local):

* **`system.util.sendMessage(project, messageHandler, payload)`** — fire-and-forget.
* **`system.util.sendRequest(...)`** — synchronous, blocks for a return value from the handler.
* **`system.util.sendRequestAsync(...)`** — asynchronous with a callback/future for the return value.

```python
project = "test"
messageHandler = "My Message Handler"
myDict = {'MyFirstValue': "Hello", 'MySecondValue': "World"}
results = system.util.sendMessage(project, messageHandler, myDict)
```

`sendMessage` accepts a `remoteServers` list to target other Gateways over the Gateway Network — this is the standard pattern for a Front-End Gateway invoking Back-End-only functionality (report execution, SFC control, `system.eam`/`system.device`/`system.opc` calls, which are Gateway-scoped and don't cross Gateway Network boundaries on their own). Errors from a handler invoked this way surface in the *handling* Gateway's logs, not the caller's.

**Perspective session messages**: `system.perspective.sendMessage` lets a Perspective session send a message to other sessions/pages (within the Perspective visualization layer) — distinct from the Gateway Message Handler mechanism above, though both follow a broadly similar "name + payload" request/response shape.

---

## Named resources and project structure

### The `resource.json` file
Every Ignition project resource is a folder containing a `resource.json` manifest plus the actual resource data files (commonly `data.bin` or `config.json`). It mixes user-set and Ignition-calculated metadata and exists specifically to make conflict resolution, version tracking, and out-of-band (filesystem-level) auditing possible:

| Field | Meaning |
|---|---|
| `Scope` | Where the resource is used: `G` Gateway, `C` Client, `A` All |
| `Version` | Resource-type schema version — affects how data is parsed internally (e.g., Named Queries v2 exposes data as listed attributes that v1 didn't) |
| `Restricted` | If true, only users with the required role(s) can access it |
| `Overrideable` | If true, a child project can override the inherited resource (only meaningful on the parent project side) |
| `Files` | Where the resource's actual data lives (e.g., `data.bin`, `config.json`) |
| `Attributes` | Resource property values; `lastModification` and `lastModificationSignature` are always populated automatically for audit purposes, and users can add their own |

A sibling `project.json` at the project root stores the project's title, parent project name, description, inheritable flag, and enabled state.

### Resource types & where they live on disk
Projects are stored as folders/files under the Gateway's `data/projects` directory (Linux default `/var/lib/ignition/data/projects`; Windows default `...\Ignition\data\projects`). A project holds: Windows/Templates or Views, Transaction Groups, Reports, Scripts (Project Library + event scripts, stored as readable `.py`), Alarm Pipelines, SFCs, and general settings. **Tags, Alarms, database/device connections, and Gateway configuration are *not* part of a project** — they're Gateway-level resources referenced by, not stored inside, projects (relevant when deciding what a project export/import will and won't carry — see Tutorials, Deployment Best Practices).

### 8.3's biggest structural change: Gateway config is now files too
In Ignition 8.1, only **projects** lived in the file system — all other Gateway configuration (connections, users/roles, alarm settings, etc.) lived inside Ignition's internal SQLite database and was invisible to source control short of a full binary Gateway backup. **In 8.3, the entire Gateway configuration is externalized into a `data/config` directory structure**, human-readable and diffable, alongside `data/projects`. This is repeatedly called out in the docs as one of the most consequential 8.3 changes for teams — see the Gotchas section and the Version Control Guide summary in Tutorials below.

### Project export and import
Project-level backup/restore, distinct from a full Gateway Backup. An export is a `.zip` containing **only project-specific resources**: Alarm Pipelines, Named Queries, Perspective Properties/Views, Project Properties, Reports, SFCs, Transaction Groups, Vision Client Tags/Windows/Templates, Client Event Scripts, Gateway Event Scripts. It explicitly **excludes** Gateway-level resources — device/database connections, Tag Providers, and Tags themselves need a separate Tag export (`system.tag.exportTags` or the Tag Browser's export) and are not restored by a project import.

* **From the Gateway webpage** (System → Projects → ⋮ → Export/Import Project) — always the *whole* project; on import, a name collision forces a choice between **Rename** and **Overwrite**.
* **From the Designer** (File → Export / File → Import) — resource-selectable in both directions: choose which resources go into the export, and later choose which resources from an export get merged into the currently-open project. A **Send to Project** option lets you push selected resources directly into another project on the same Gateway without going through a file at all. Export defaults to **local** (non-inherited) resources only. Import conflicts prompt **Overwrite / Overwrite All / Skip / Skip All / Rename / Cancel** per resource, and the project must still be saved afterward for the merge to take effect.
* **Version boundary**: a project exported from **before Ignition 8.1** cannot be imported directly into 8.3 — it must first be imported into an 8.1 Gateway and re-exported from there.

### Project inheritance
A project can be marked **Inheritable**; other ("child") projects set it as their **Parent Project** and receive its resources automatically. Inherited resources render grayed-out in a child's Project Browser (![inherited icon] vs ![inherited-overridden icon] once a developer has explicitly **Override Resource**d one). An inheritable project **cannot be launched standalone** ("Project Not Runnable" error) — it exists purely as a shared-resource library. Renaming an inherited resource in the child project does **not** delete it from the parent — the parent's original propagates back down as a fresh, ungrayed copy alongside the renamed one, so renaming inherited resources is a common footgun.

Some resource types are **"runnable"** — they execute automatically in every *leaf* project (a project nothing else inherits from): **Gateway Event Scripts, Alarm Notification Pipelines, SFCs, Transaction Groups**. If two leaf projects both inherit from the same parent that contains a Gateway Tag Change Script, that script runs **twice** — once per leaf. The fix is to keep runnable resources in a dedicated standalone (non-inherited, non-inheriting) project rather than in a shared parent.

### What this means for git / version control
* Projects are already plain files, so `git init` on the `data/projects` directory (or, in 8.3, on the whole `data` directory to also capture Gateway config) works with essentially no adaptation. Recommended `.gitignore` entries include database/cache/log/certificate directories, `**/config/local`, `**/config/resources/local` (environment-specific overrides), and Vision-only-relevant `.bin`-encoded resources if you haven't converted them to XML (Transaction Groups, Client Tags, Reports, Alarm Pipelines still encode as binary and aren't diff-friendly).
* Vision projects default to a binary `.bin` encoding; **8.3 recommends switching to XML encoding** for git-friendliness — this happens incrementally as you re-save individual windows, and applies automatically to new resources.
* Best-practice guidance (from `resource-json-file` + the Best Practices for Team Environments page): avoid committing `resource.json` changes without their accompanying `view.json` (or `projects/*/com.inductiveautomation.perspective/session-props/props.json`) changes in the same commit — partial commits desync the manifest from the data it describes.
* See **Tutorials worth knowing** below for the full version-control workflow (subtractive vs. additive/curated mounting, Deployment Modes, Gateway API, GitOps).

---

## Designer

### Layout & docking
Panels (Project Browser, Tag Browser, Component Palette, Property Editor, etc.) live in a flexible docking system with four states: **Docked** (snaps to a workspace edge; stacks as tabs when two panels share a spot), **Floating** (dragged out, can go on a second monitor), **Pinned** (auto-hides to an edge tab), **Hidden** (closed; reopen via **View → Panels**). Layout is remembered per-workspace-type and stored under `%USER_HOME%/.ignition/*.layout`; delete those files to force a full reset (or use **View → Reset Panels** for a quick revert). Which panels appear depends on what kind of resource is open — editing a Window/View gives you Component Palette + Property Editor, editing an Alarm Pipeline gives you the Pipeline Block Editor, editing a Report gives you the Report Designer, etc. — these are called **Designer Spaces**.

### Project Browser
Tree view of the whole project (windows/views down to individual components), with a right-click menu whose exact options depend on resource type: **Close & Commit**, **Close & Revert**, **Configure View Permissions**, **Configure Events**, **Rename**, **Cut/Copy/Copy Path/Paste**, **Delete**, **Revert Changes**, **Export**, **Protect**, **Documentation…**. Resource names must start with a letter/digit/underscore and cannot contain `< > : " / \ | ? *`, nor be one of the reserved Windows device names (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`).

### Tag Browser
Left-side panel (below Project Browser) for browsing, creating, editing, exporting, and importing tags and OPC servers directly.

### Comm Mode (Designer/Client data safety switch)
Every Designer or Client instance has an independent **Comm Mode**: **Comm Off** (all Tag subscriptions/writes and DB traffic blocked — useful to pause polling), **Comm Read-Only** (default; subscriptions and `SELECT`s work, writes/`UPDATE`/`INSERT`/`DELETE` are silently ignored by the Gateway), **Comm Read/Write** (full read/write). It's per-instance — changing it in one open Designer doesn't affect any other open Designer or Client. Transaction Groups are unaffected since they execute on the Gateway regardless of any Designer's comm mode.

### Resource locking / concurrent editing & designer communication
Ignition Designer uses a **lock-free** concurrent-editing model: any number of Designers can open the same project at once, and opening/editing a resource does **not** lock it for anyone else. The Concurrent Users UI (bottom-right corner) shows who else has which resources open and flags overlapping edits in red. Conflicts are resolved only at **save time**: if your save collides with someone else's, the Resolve Conflicts screen opens automatically, showing thumbnails and JSON diffs per conflicting resource, and you choose per-conflict to keep your version, take theirs, or cancel and go talk to them. **Update Project** (`Ctrl+Shift+U`) explicitly pulls in others' saved changes (and runs the same conflict-resolution flow if needed) without you having to save first.

### Designer tool inventory
| Tool | Menu path | What it's for |
|---|---|---|
| Output Console | Tools → Console (`Ctrl+Shift+C`) | `print`/`system.util.getLogger` output from anywhere except Gateway scope and the Script Console's own buffer |
| Script Console | Tools → Script Console | Live REPL, Designer/local scope only (see above) |
| Database Query Browser | Tools → Database Query Browser | Ad-hoc SQL against any configured connection; auto-detects Select/Update mode, 1000-row default `SELECT` cap, multiple result tabs, query history, Auto Refresh polling, in-grid editing (green=new/red=deleted/blue=changed cells) |
| Image Management | Tools → Image Management | Upload/download/organize PNG/JPG/GIF/SVG (no bitmap support) stored Gateway-side (not per-project); drag-drop or the Upload icon; right-click for **Copy Path** (project-relative) vs **Copy Mounted Path** (for Perspective) |
| Translation Manager | Tools → Translation Manager | See Localization section |
| Keyboard Layouts | Tools → Keyboard Layouts (Vision workspace only) | JSON-defined, Gateway-wide touchscreen keyboard layouts; 6 defaults included (English×2, Spanish, French, German, Italian); assignable per-component, per-locale, or switchable at runtime; supports accent long-press |
| Symbol Factory | Tools → Symbol Factory | Vector symbol library, drag-drop as ungroupable shape groups |
| Find and Replace | Edit → Find/Replace (`Ctrl+F`) | Project-wide search/replace across Named Queries, Pipelines, Transaction Groups, Scripting, Tags, Templates, Views, Windows, WebDev resources; supports `*`/`?` wildcards; can be scoped contextually via right-click on a Project Browser node |

### Keyboard shortcuts worth knowing (developer-relevant subset)
Full reference: `platform/designer/windows-linux-and-mac-keyboard-shortcuts`. The shortcuts most relevant to scripting/project work day to day (Windows/Linux — MacOS substitutes Command for Ctrl and Option for Alt):

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save (opens the Save dialog subset picker) |
| `Ctrl+Shift+U` | Update Project (pull others' saves without saving your own) |
| `F5` | Toggle Design Mode / Preview Mode |
| `F10` / `F11` | Launch a windowed / full-screen Client or Session |
| `Ctrl+Shift+C` | Open the Output Console |
| `Ctrl+F` | Find/Replace |
| `Ctrl+/` | Comment/uncomment the selected line(s) of code |
| `Ctrl+.` | Fold/unfold the selected block of code |
| `Ctrl+J` | Open Component Scripting (Vision) / Configure Events (Perspective) for the selection |
| `Ctrl+K` | Open Script Configuration for the selected View/component (Perspective only) |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `F2` | Rename the selected item (tag, window, component, transaction group, …) |
| `Ctrl+Mousewheel` | Zoom the workspace |

### Symbol reference
The `appendix/reference-pages/symbol-reference` page is itself only a landing/index page — it links out to per-area tables (project browser icons, tag browser icons, etc.) that give the name and meaning of every icon/symbol used across the Designer's browsers. Useful as a lookup when a doc or screenshot references "the ![X] icon" and you need to know what it does.

### Saving, updating, and resolving conflicts
Project save actions live under the Designer's **File** menu:

* **Save All** — saves the entire project immediately, unless a concurrent-edit conflict is detected, in which case the Resolve Conflicts screen opens automatically.
* **Save…** — shows every resource created/modified/deleted since the last save and lets you save a subset; **Update Before Save** (on by default) first pulls in others' committed changes so you're not saving against a stale local copy.
* **Save As** — saves the open project under a new name (defaults to `Copy_Of_<name>`).
* **Update Project** (`Ctrl+Shift+U`) — pulls other Designers' saves into your local copy without saving your own changes; runs the same conflict-resolution flow if there's an overlap.

Downstream of a save, **Vision Clients** either silently update or show a banner depending on the project's configured Client Update Mode; the operator confirms via a popup before the client actually swaps in the new resources. **Perspective Sessions** either update silently or show an Update Notification that auto-applies after 30 seconds (or immediately via **Update Now**).

### Project properties reference (Designer → Project → Project Properties)
Settings apply Gateway-wide for that project, grouped into the following (per docs; a "Resource Inherited" overlay appears when a child project inherits a section from its parent — **Override Resource** edits it locally, **Discard Overrides** reverts to the inherited value):

| Group | Key settings |
|---|---|
| Tag Settings | Default Provider; Client Poll Rate (ms — how often a Vision Client/Designer polls the Gateway for subscribed-tag updates) |
| Database Settings | Default Database (the special `<default>` connection, or `""` from a script, resolves to whatever this is set to) |
| Security Settings | Identity Provider; whether re-authentication is always forced; whether users auto-redirect to the IdP or see a "speed bump" page first; User Source (Vision/Classic auth only) |
| Audit Settings | Enable Auditing; Audit Profile |
| Permissions | Required Designer Roles for View / Save / Delete / access to Protected Resources |
| Designer Properties | Initial Gateway Comm Mode the Designer starts in for this project; Designer Timezone Behavior (overrides Vision's Client Timezone setting, Designer-only) |

Project name/description/title are **not** editable from inside the Designer — they're set from the Gateway webpage (**Config → Projects → edit**) and the Designer only reflects them, because changing the project *name* (not the Title, which is the safe, cosmetic one to change) breaks any shortcuts/deep-links that reference it by name.

### Project templates
New projects can start from a built-in navigation template rather than a blank project: **Perspective** offers **Web Nav** (flat, tab-based, good for a handful of top-level views) and **Menu Nav** (hierarchical, collapsible, good for medium/large structures, auto-hides on small screens); **Vision** offers **Tab Nav**, **2-Tier Tab Nav**, and **Tree Nav** (same size-of-project reasoning). Vision templates additionally ship a pre-wired inactivity-lockout Client Timer script (checks every 5 seconds, locks after 5 minutes) that's easy to overlook and disable/delete if not wanted. More templates are downloadable from the Ignition Exchange (requires internet access from the Designer machine to even list them).

### Concurrent editing in practice: what actually gets checked
The lock-free model means two Designers can have the *same* window/view open simultaneously without either being blocked — Ignition doesn't detect a conflict until someone actually **saves**. Opening a resource someone else already has open just shows a heads-up popup, not a refusal. The Concurrent Users UI in the bottom-right shows, live, who has what open and colors overlapping in-progress edits red as an early warning before anyone has even tried to save.

### Designer Diagnostics (Help → Diagnostics)
A tabbed troubleshooting window, scoped to **this Designer/Client/session instance**, not the Gateway (for Gateway-wide stats use the Gateway webpage's Diagnostics → Logs instead). Tabs can be shown/hidden via right-click:

| Tab | What it shows |
|---|---|
| Performance | Six realtime charts: Tag Throughput (scans/sec), Tag Value Changes (changes/sec), Select Queries (queries/sec), Rows Returned from Select Queries (rows/sec), Update Queries (queries/sec), Memory (MB, sawtooth pattern is normal). The Select-Queries chart is the fastest way to spot "too many queries too often" as a performance root cause. |
| Console | The same Ignition Console output as elsewhere (print statements, errors) for whatever launched the Diagnostics window — except Gateway-scope scripts, which never appear here. |
| Log Viewer | Logged messages for this instance, filterable by severity; uncheck **Group Categories** to see one flat chronological stream across categories instead. |
| Logging Levels | Lists internal loggers with a searchable filter (case-sensitive/wildcard/regex/match-start/match-exact/match-anywhere options); intended for support-directed troubleshooting — remember to set levels back to Info afterward or you'll flood the console. |
| Thread Viewer | Expand/collapse individual running threads; supports saving a manual thread dump. Automated thread dumps are also written to the Client Launcher's `.ignition/cache` directory whenever a UI thread blocks for 2-5+ seconds, with a console message giving the saved file's path — useful evidence for a "the client froze" report. |
| Connections | Gateway connection status plus a realtime ping-time chart and current/average/min/max ping summary. |
| Scripts | Lists currently running scripts; a Delete icon lets you forcibly terminate one (e.g., a runaway loop you don't want to wait out). |

---

## Localization and languages

### Model
Translations live in one **shared Gateway-side database**, usable from Perspective Sessions, Vision Clients, Gateway scripts, and alarm messages alike — define a term once, it's available everywhere. A **key** is the lookup string (a literal word like `Start`, or a coded identifier like `#start` / `dialog.save_changes`); if no translation exists for the active locale, the **English value is shown by default**.

* **Global terms** — defined once in the Translation Manager (Tools → Translation Manager), reused everywhere. This is the default/recommended approach.
* **Component terms** (**Vision only**) — override a global term for one specific component/window via the Translatable Terms panel (right-click a component → Translations). Component term always wins over a same-keyed global term. Use this only when context genuinely needs a different translation (docs example: a global "Tank" → "Tanque" but one window's Label needs "Barril" specifically).

### Key naming best practice
Prefix ambiguous/short keys with `#` (`#Auto`, `#Off`, `#Hand`, `#Barrel`) so common English words used as keys don't accidentally collide with unrelated project terms elsewhere. Once a key is live, **don't rename it** — that breaks the mapping to every translation already entered for it.

### Locale string formats — the thing most likely to bite a developer
Locales are Java `Locale` objects under the hood, serialized as strings, and there are **two accepted formats** — mixing them up silently breaks lookups:

* **BCP-47 language tag (recommended for new code)**: hyphen-separated, e.g. `en`, `en-US`, `es-ES`, `fr-CA`.
* **Legacy underscore format** (still accepted for backward compatibility, **not recommended for new code**): `en`, `en_US`, `es_ES`. Some functions (notably `system.vision.getLocale`/`getAvailableLocales`) **only return** this legacy format even though other functions expect the hyphenated form.

| Location | Accepts | Returns | Preferred |
|---|---|---|---|
| `system.util.translate` | both | — | language tag |
| `system.util.modifyTranslation` | both | — | language tag |
| `translate` expression function | both | — | language tag |
| `system.vision.getLocale` | — | underscore | — |
| `system.vision.getAvailableLocales` | — | underscore | — |
| Perspective session `locale` property | language tag | language tag | — |
| `system.user.editUser` `Language` attribute | both | both | language tag |

A locale **name is not a locale identifier** — `system.util.translate("Hello", "Spanish")` silently falls back to the untranslated term; it must be `"es"` or `"es-ES"`.

### Translation Manager workflow
Reached via **Tools → Translation Manager** in the Designer. English, French, German, Italian, Korean, Norwegian, Portuguese, and Spanish are pre-defined; adding a language (Languages panel → **+**) makes it available project-wide as a new column in the Translation Terms table, with an optional **Include regional variations** checkbox to add region-specific codes (`fr-CA` vs `fr-FR`) alongside the base language. Adding a term: **+** on the Terms table, type the key, expand it to enter a value per language, **Save** — the term is then usable from any project immediately (it's Gateway-shared, not per-project). Testing a fresh term: in Perspective, bind/set a component's `text` to the key and change `session.props.locale`; in Vision, drop a Language Selector component on the window and toggle it in Preview Mode.

**Import/export** (Translation Manager's own icons, distinct from a project export): export to **PROPERTIES** or **XML** format (XML supports UTF-8, useful for non-Latin scripts), one file per selected language, either the full term set or only the currently-selected rows — the standard way to hand a batch of strings to a third-party translator or sync terms across Gateways. Import re-reads a file back in, with **Import All**/**Import Selected**, and **overwrites any existing term with the same key** — there's no merge-and-keep-both option, so review a diff before importing into a Gateway with terms you don't want clobbered.

### Switching language at runtime
* **Vision**: a Language Selector dropdown at login, or the **Language Selector** component embedded in a window at runtime; in the Designer, **Project → Preview Language** sets what Preview Mode uses (remembered across restarts, reverts when Preview Mode is off).
* **Perspective**: write to the session's `locale` property (`session.props.locale`) — from a script on session open, or bind it to a user-facing control. All components bound to translation keys update immediately when it changes.

### Vision-specific extras
* Vision **Table** components do **not** support translation; the **Alarm Status Table** and **Alarm Journal Table** do.
* Bound text is translated **after** the binding evaluates.
* Long translated strings can wrap across multiple lines in Vision by prefixing the value with `<html>`.
* Certain built-in Vision system dialogs (Access Denied on a `Do Not Open`-restricted window; the Screen Locked overlay from `system.vision.lockScreen`) aren't exposed as component properties but **can still be localized** by adding their exact fixed-text HTML string as a translation key in the Translation Manager (the `%s` placeholder for window name / username is preserved).

---

## Practical guidance

### Error handling
Standard `try`/`except`/`else`/`pass`/`finally`, Python 2 syntax. Multiple `except` clauses are checked **in declaration order** against the thrown exception's class (direct or superclass match); only the **first** matching block runs. Remember the dual exception hierarchy from the Python/Jython section — a robust handler around a `system.db.*` call typically needs both:

```python
__log = system.util.getLogger("myTransactionUtil")

def doSomethingWithTheDatabase(args):
    tx = system.db.beginTransaction("myDatabase")
    try:
        return system.db.runPrepUpdate("query", [args], tx=tx)
    except Exception as e:
        system.db.rollbackTransaction(tx)
        __log.warnf("Update failed due to Jython Exception: %s", e)
    except Throwable as t:
        system.db.rollbackTransaction(tx)
        __log.warn("Update failed due to Java Throwable", t)
    else:
        system.db.commitTransaction(tx)
    finally:
        system.db.closeTransaction(tx)
```

Common exceptions you'll actually see, and what they mean: **NoneType has no attribute 'x'** (something you referenced — often `event.source.parent.getComponent('Name')` — resolved to nothing, usually a rename/typo mismatch), **AttributeError** (property name typo or wrong case, e.g. `showmessage` vs `showMessage`), **IndexError**/`ArrayIndexOutOfBoundsException` (index past the end of a list/dataset — commonly `-1` from an unselected table row), **NameError** (referencing an undefined variable — often a missing string quote around a bare word), **TypeError** (wrong argument type, e.g. passing an `int` where `showMessage` wants a `str`), **ValueError** (right type, bad value, e.g. `int("Hello")`).

### Logging
`system.util.getLogger(name)` is the preferred logging mechanism, especially for Gateway-scoped code, because its output reliably lands on both the Gateway's Logs page **and** `wrapper.log` regardless of scope — unlike bare `print`, whose destination varies wildly by where the script runs:

| Scope | `print` goes to | `system.util.getLogger` goes to | Other notes |
|---|---|---|---|
| Designer (non-Perspective) | Output Console | Output Console | — |
| Script Console | Multiline Buffer (right pane) | Output Console (not the Script Console) | — |
| Perspective, in Designer | Recommend `system.perspective.print` → Designer's Output Console; bare `print` → `wrapper.log` | Gateway system logs + `wrapper.log` | Even in the Designer, Perspective scripts execute on the Gateway |
| Gateway (event scripts, tag events, SFCs, pipelines, reports) | `wrapper.log` | Gateway system logs + `wrapper.log` | `system.perspective.print` does nothing here unless a session id is explicitly given |
| Perspective Session, runtime | `system.perspective.print` with scope `client` → browser console; scope `gateway` → Gateway logs; unspecified → `client` in Designer, `gateway` in a live session | Gateway logs + `wrapper.log` | bare `print` → `wrapper.log` |
| Vision Client, runtime | Client Console (**Help → Diagnostics → Console**, or `Ctrl+Shift+F7`) | same | — |

### Performance rules
* **Never block the render/GUI thread.** Component event handlers run on the same thread that redraws the Client/Session UI — `time.sleep()` or a busy `while` loop there **freezes the whole screen** for the duration, and doesn't yield to other component scripts either. Use `system.vision.invokeLater(fn, delayMs)` (no ability to pass parameters — bind them via closure/default args instead) or Python's `threading.Timer(seconds, fn, [args]).start()` (does accept parameters, cancellable via `.cancel()` before it fires) to add a delay without blocking. If a `sleep()`/`while` loop is genuinely unavoidable, wrap it in `system.util.invokeAsynchronous()` so it runs off the UI thread.
* **Avoid heavy work in Tag Change Scripts.** They fire on the Gateway per tag-change event; each execution gets its own thread (so one slow tag-change script can't block another), but stacking expensive logic onto a fast-changing tag will still spawn a lot of concurrent work. Filter early with `initialChange`/`executionCount` and keep the body minimal; push heavy lifting to a message handler or a scheduled/timer script instead.
* **Batch tag reads/writes.** `system.tag.readBlocking` / `writeBlocking` both take a **list** of paths (and, for writes, a parallel list of values) — always prefer one call with N paths over N calls with one path each:

```python
paths = ["Scripting/Tags/Alarm_1", "Scripting/Tags/Alarm_2", "Scripting/Tags/Alarm_3"]
values = system.tag.readBlocking(paths)
for i in range(len(paths)):
    print values[i].value
```

* Web-service/HTTP calls block whatever thread called them — wrap them in `system.util.invokeAsynchronous()` when triggered from a button, or show a "working" indicator, since the first call to an external endpoint especially can be slow.
* Watch out for scope-provider prefixes in shared/Gateway-scoped scripts: a script in the Project scope can omit `[provider]` (falls back to the project default), but a script in a **Shared** context (Alarm Pipelines, etc.) must always fully qualify the tag path (`[default]My/Tag/Path`) or it can throw.

### Testing / debugging technique
* **Read the Error Message Box fully** — the **Message** tab names the exact Event Handler and component that threw; the **Details** tab gives the line number and the real exception message. Start at the reported line and work *upward* — the true root cause (a bad variable initialization, a renamed component) is often above the reported line, not on it.
* **Prototype in the Script Console first** — no component/window scaffolding required, immediate feedback in the Interactive Interpreter, and it's the natural place to reproduce a `NoneType`/`AttributeError` in isolation before pasting a fix back into the real event handler.
* Liberal `print` statements bracketing suspect branches ("Starting if-statement" / "Inside if-statement") make it easy to tell whether a branch of code executed at all, which is often the actual question when "nothing happens."
* If truly nothing happens and there's no error box: check for a **hidden** error box behind the Designer/Client window first; then verify the Designer is in **Preview Mode** (event-based scripts don't run in plain Design Mode); then check for silently-wrong wiring (script attached to the wrong event, e.g. `propertyChange` instead of `actionPerformed`; or a defined-but-never-called function).
* Use a real launched Client for testing whatever won't behave correctly in Preview Mode — the docs specifically flag `system.vision.retarget` and `system.vision.openWindowInstance` as needing a true Client.
* The Error Message Box has a **Send to Front** / **Send to Back** toggle; leave it on Send to Front while actively debugging so a second error can't silently stack up hidden behind the first.

### Worked troubleshooting example (the docs' own walkthrough)
A Button script that reads a selected Power Table cell and writes it to a tag, fixed across three iterations — a good illustration of "start at the reported line, work upward, fix one error at a time":

```python
# v1 — throws AttributeError: 'NoneType' object has no attribute 'data'
table = event.source.parent.getComponent('Power Table')
userSelectedValue = table.data.getValueAt(table.selectedrow, table.selectedColumn)
system.tag.writeBlocking(["Scripting/ButtonError/WriteTarget"], [userSelectedValue])
```
Root cause: the component was renamed to `My Table` after the script was written, so `getComponent('Power Table')` silently returns `None` instead of raising — the *next* line that touches `.data` on that `None` is what actually throws. Fix the component name:
```python
table = event.source.parent.getComponent('My Table')   # v2 — throws AttributeError on 'selectedrow'
```
That surfaces a second bug: `table.selectedrow` doesn't exist — the real property is `selectedRow` (capital R), a case-sensitivity typo. Fixing the typo reveals a third, non-exception failure mode: clicking the button with **no row selected** silently writes `-1` (Ignition's "nothing selected" sentinel) instead of erroring, because -1 is a valid index that just happens to be out of bounds only sometimes. Final, defensive version:
```python
table = event.source.parent.getComponent('My Table')
if table.selectedRow != -1:
    userSelectedValue = table.data.getValueAt(table.selectedRow, table.selectedColumn)
    system.tag.writeBlocking(["Scripting/ButtonError/WriteTarget"], [userSelectedValue])
else:
    system.vision.showMessage("Please select a cell in the table first!")
```
The general lesson: a `NoneType`/`AttributeError` traceback names the *symptom's* line, not necessarily the *cause's* line — the cause is often an earlier variable assignment (a rename, a typo, an unchecked "nothing selected" sentinel) that produced a bad value quietly, which then blows up several lines later on first use.

### Common scripting recipes (grounded in the docs' own examples)

**Reading/writing tags, in bulk, with correct scope prefixing.** `readBlocking`/`writeBlocking` always take (and return) **lists**, even for a single tag — and a script in a *Shared* scope (an Alarm Pipeline, a Gateway Scripting Project library, etc.) must fully qualify the provider (`[default]Path`), while a script inside a Project's own component/window scope can rely on the project's default provider:

```python
# get value + quality + timestamp for a single tag
tag = system.tag.readBlocking(["[default]My/Tag/Path"])[0]
value, quality, timestamp = tag.value, tag.quality, tag.timestamp

# write several tags at once
paths  = ["Scripting/Tags/Setpoint_1", "Scripting/Tags/Setpoint_2"]
values = [72, 72]
system.tag.writeBlocking(paths, values)

# relative paths inside a UDT ("[.]" = same UDT instance)
system.tag.readBlocking(["[.]otherMember"])[0].value
```

**Exporting a dataset to CSV and back.** `system.dataset.toCSV`/`fromCSV` round-trip Ignition's own CSV dialect (a `#NAMES`/`#TYPES`/`#ROWS,n` header block); Python's own `csv` module is the fallback for CSVs that don't use that format:

```python
csv = system.dataset.toCSV(component.data)
system.file.writeFile(r"C:\myExports\myExport.csv", csv)

# round-trip via Python's csv module for a plain-header CSV
import csv as pycsv
f = open(path)
reader = pycsv.reader(f)
header = reader.next()
dataset = system.dataset.toDataset(header, list(reader))
f.close()
```

**Calling a REST endpoint and parsing the result.**

```python
client = system.net.httpClient()
response = client.get(url, {"lat": 38.65, "lon": -121.19, "appid": "KEY"})
decoded = response.getJson()               # or: system.util.jsonDecode(response.getText())
print decoded.get("weather")[0].get("description")
```

**Parsing XML** with Java's bundled DOM/SAX/StAX parsers (no third-party library needed) — DOM for small documents you want to walk as a tree (`document.getDocumentElement()`, `.getElementsByTagName(name)`, `.item(i)`, `.getAttribute(name)`, `.textContent`), SAX/StAX for large documents processed as a stream of start/end/character events without holding the whole thing in memory. The docs flag that unhardened XML parsing is a real security exposure (XXE-style attacks) — see the OWASP XML Security Cheat Sheet referenced on that page before parsing untrusted XML.

**Querying Tag Historian data and exporting to CSV.** `system.historian.queryRawPoints` is the recommended API for pulling raw history programmatically (vs. querying the auto-generated SQL tables directly); combine it with `system.historian.browse` to recursively discover every historical tag under a folder when you don't want to hardcode paths:

```python
def browse(t, path):
    for result in system.historian.browse(path).getResults():
        t.append(result.getPath())
        if result.hasChildren():
            browse(t, result.getPath())

historyPaths = []
browse(historyPaths, path='histprov:myDB:/sys:myGateway/prov:myTagProvider:/tag:myFolder')
tagPaths = ["[myTagProvider]" + str(p).split("tag:")[1] for p in historyPaths]

end = system.date.now()
start = system.date.addMinutes(end, -30)
data = system.historian.queryRawPoints(paths=tagPaths, startTime=start, endTime=end,
                                        returnSize=10, returnFormat='Wide', includeBounds=True)
system.file.writeFile(r"C:\myExports\myExport.csv", system.dataset.toCSV(data))
```

A recursive historian browse like this is flagged in the docs as potentially dangerous on a large tag tree or a long time range — it can generate enough simultaneous history queries to bog down the Gateway, so scope the starting folder and time window deliberately.

**Delaying without blocking** — see Performance rules above for the full explanation; the three patterns in order of preference are `system.vision.invokeLater(fn, delayMs)`, `threading.Timer(seconds, fn, [args]).start()` (when you need to pass parameters or be able to `.cancel()`), and, only inside `system.util.invokeAsynchronous()`, `time.sleep()` or a counter-bounded `while` loop.

---

## Scripting object quick reference

Selected objects returned by common `system.*` calls (full reference: appendix `scripting-object-reference` page, or the Javadocs/SDK docs for anything not covered here).

**`QualifiedValue`** (tag reads, Tag Event Script `newValue`/`previousValue`, Perspective property-change events) — properties `value`, `quality` (a `QualityCode`), `timestamp`; equivalent getter methods `getValue()`/`getQuality()`/`getTimestamp()`.

**`QualityCode`** — boolean properties `good`/`uncertain`/`bad`/`error`/`notGood`/`badOrError`, plus `code` (32-bit int) and `diagnosticMessage`; equivalent `is*()` getter methods, plus `toValue()` (wrap as a full `QualifiedValue`) and `is(other)`/`isNot(other)` for comparing two quality codes.

**Tag browse results** (`system.tag.browse`, `system.historian.browse`) — the returned object's `getResults()` gives a list of per-node dicts. Every node dict has `fullPath` (a `BasicTagPath`, `str()`-able), `hasChildren` (bool), `name`, `tagType` (`AtomicTag`/`Folder`/`UdtType`/`UdtInstance`). Atomic tags additionally carry `dataType`, `valueSource`, `value`; UDT nodes carry `typeId` (parent UDT type, `None` if none).

**Alarm objects** — `system.alarm.queryStatus`/`queryJournal` return an `AlarmQueryResult` whose `getDataset()` gives a `Dataset` with columns `EventId`/`Source`/`DisplayPath`/`EventTime`/`State` (or `EventState` for journal queries)/`Priority` (+`IsSystemEvent` for journal queries). Iterating alarm results directly yields `PyAlarmEvent`-shaped objects with `get(propertyName)`/`getOrDefault`/`getOrElse`, `getState()`/`isAcked()`/`isCleared()`/`isShelved()`, `getPriority()`, `getSource()`/`getDisplayPath()`, and dict-style key access (`event["EventId"]`). Inside an Alarm Pipeline **Script Block** the same shape is exposed as `ScriptableBlockPyAlarmEvent`, with one extra method: `cancelNotification()` (aborts the running pipeline instance).

**`system.user.getUser`/`getUsers`** results — `.get(field)`/`.getOrDefault(field)` for `Username`/`Firstname`/`Lastname`/`Notes`/`Schedule`/`Language`/any custom parameter name; `.getRoles()`, `.getContactInfo()` (list of `{contactType, value}`), `.getScheduleAdjustments()` (list of `{start, end, available, note}`), `.getPath()` (a deterministic `QualifiedPath` identifying the user).

---

## Tutorials worth knowing

Compact summaries of the resource-guide/tutorial pages (`tutorials/**`), which lean heavily toward deployment and operations rather than scripting syntax.

**Ignition 8 Deployment Best Practices** — Four areas of Gateway configuration are stored, and thus must be tracked, differently: **Gateway Configuration** (settings/connections/security — internal SQLite historically, now file-system-based in 8.3, still requires manual documentation/diffing discipline since there's no built-in export/import for it), **Tags** (internal storage, but exportable to JSON — automate via a Gateway Event Update script calling `system.tag.exportTags`), **Images** (internal storage, exportable via the Image Management tool only, no automated export API), **Projects** (already plain files — commit the folder directly). Recommends a 3-environment workflow (Development → Testing → Production) with matching source-control branches, keeping identically-**named** but differently-**pointed** connections across environments (so screens/queries referencing a connection "by name" just work everywhere), and gives several strategies for feeding non-production environments live-shaped data safely (OPC UA passthrough to prod, MQTT fan-out, Gateway Network remote tag providers, or the Programmable Device Simulator/SFC-based simulation). Includes a worked GitLab example: `.gitignore` the `.resources/` folder, auto-commit via a Gateway Event **Update** script shelling out to a `git add/commit/push` script (`system.util.execute(["/path/to/git-auto-commit.sh"])`), branch-per-environment, merge-request-driven promotion, and `git pull` + a Gateway "Scan File System" (or the `/data/api/v1/scan/config` and `/data/api/v1/scan/projects` REST endpoints) to apply pulled changes.

**Ignition Historian Guide** — Distinguishes the **Historian Core module** (tag-based, asynchronous, internal or SQL storage, `system.historian.queryRawPoints()` is the recommended API for external tools rather than querying the auto-generated tables directly) from **SQL Bridge/Transaction Groups** (event-based, synchronous multi-column inserts under one timestamp, fully custom table shape). Gives concrete architecture diagrams (Standard / High-Resilience-Standard / High-Performance Multi-Database / IIoT-with-collectors) and a throughput formula: `Tag Changes/sec = Tag Count × Change Rate % / Storage Rate (sec)`, plus a companion storage formula: roughly **100 bytes per tag change**, uncompressed. Optimization guidance: set realistic deadbands and "Min Time Between Samples," don't log at 1-second rates unless required, consider disabling Stale Data Detection if `sqlth_sce` is growing unexpectedly, and for MySQL specifically add `rewriteBatchedStatements=true` to roughly 10x throughput.

**Version and Source Control Guide** — Centers on the file-system-based 8.3 Gateway config (see Gotchas below) as the enabling change. Walks through a **subtractive** approach (clone the whole `data` directory into git, `.gitignore` out runtime/cache/db/log/cert noise — simple, works for 1-2 Gateways, gets unwieldy for teams/fleets) versus an **additive/curated** approach (bind-mount only specific subfolders of `data/config` and `data/projects` from a repo into a containerized Gateway — scales to many Gateways from one repo, much smaller `.gitignore`). Flags the fully-documented **Gateway RESTful API** as the mechanism for GitOps-style pipelines (Ansible/Terraform/ArgoCD/Flux watching a repo and pushing config via API rather than raw file sync), and **Deployment Modes** (a new resource-collection inheritance mechanism letting one config repo behave differently per environment — e.g., dev auto-connects to test devices/DBs, the same config in prod mode connects to live infrastructure, no manual reconfig at deploy time).

**Best Practices for Using Git in a Team Environment** — Pick one branching strategy (Git Flow / GitHub Flow / trunk-based) and document it in a `CONTRIBUTING.md`; short-lived, descriptively-named branches (`feature/…`, `fix/…`, `hotfix/…`); Conventional-Commits-style messages; PR review required before merge; never commit secrets (env vars + a leak-scanner like GitGuardian instead); rebase feature branches on main frequently to keep conflicts small; and the Ignition-specific gotcha — **don't commit a changed `resource.json` without its matching `view.json`** (or Perspective's `session-props/props.json`) in the same commit, or you desync the manifest from the data it describes.

**Scale-Out Architecture Guide** — A detailed Front-End/Back-End split checklist, resource by resource (Alarming, Auditing, EAM, Identity Providers, Images, OPC Drivers, Reporting, SFCs, SQL Bridge, Tag History, WebDev). Recurring pattern: keep device/database-adjacent, "runnable," Gateway-scope-only functionality (`system.eam`, `system.device`, `system.opc`, `system.report`, `system.sfc`, etc. — none of which cross Gateway Network boundaries on their own) on the **Back-End**, expose it to the Front-End via a **Gateway Message Handler** + `system.util.sendMessage(..., remoteServers=[...])`, and move visualization (Perspective/Vision resources) plus Remote Tag Providers (matched by name to the Back-End's realtime providers, Alarm Mode set to **Subscribe** for low-latency alarms) to the **Front-End**. Recommends a security-zone profile keyed to the Front-End's IP plus explicit Service Security policy on the Back-End as the enforcement boundary.

**Tag History vs. Transaction Groups** — Frame the decision around **discrete** (countable units moving station to station — automotive, steel, batching) vs. **continuous** (unbroken material flow — extrusion, oil & gas, water/wastewater) manufacturing processes. Tag Historian (asynchronous, per-tag storage, deadband/compression tuning, built-in aggregation, monthly partitioning) suits continuous processes where you're watching for deviations in an ongoing trend. SQL Bridge/Transaction Groups (synchronous, one row per triggering event with many columns under a shared timestamp, fully custom table) suits discrete processes where each unit is a first-class event with a start/end and a bundle of associated data.

**Other shorter pages, in brief**: *Deployment/tutorials index* just links to external IA resource-center guides (sizing/architecture, security hardening, Keycloak, Let's Encrypt, NERC CIP, 21 CFR Part 11). *Accessing Projects Remotely* — Gateway IP URLs (`:8088` HTTP / `:8043` HTTPS), Deep Links (`vision://Gateway/project`, `perspective://Gateway/project`), VPN, port forwarding, and reverse-proxy (sample Nginx config) options. *Development Server Best Practices* — give the dev server its own PLCs/database, keep device- and database-connection **names** matched to production, use Project/Tag Exports (not Gateway Backups) to promote dev→prod since a Gateway Backup would drag dev connection details along. *Migrating Servers* — backup → install identical version on new hardware → restore → unactivate old license → activate new. *Optimize Gateway Network Performance* — watch the Gateway Network Diagnostics → Performance page for queue/thread-pool saturation, use a **splitter** for local mirrored history queries, tune ping rate/timeout for large networks, prefer proxy nodes and one-directional outbound connections for segmented/OT networks, and default to a **zero-trust Service Security policy** at the security-zone level. *Mapping a Network Drive* — `wrapper.share.*` directives in `ignition.conf` to make a Windows share survive service reboots (8.3 note: the upgraded Java Service Wrapper will now **shut down** rather than silently ignore `wrapper.share.<n>.account` when the Gateway runs under a system account). *Working with Long File Paths* — Windows' 255-character API limit interacts badly with Ignition's deep `data/config/resources/.../tag-definition` paths (worse with dynamically-named MQTT tags); enable the `LongPathsEnabled` registry key and, for Git specifically, also set `core.longpaths=true` — Explorer still has issues either way. *Secure Disposal Guide* — document backup/data locations up front, release the license before uninstalling, prefer secure-delete tooling (SDelete/SRM) over a plain `rm -rf`, and separately sanitize any external database and I/O device storage. *Ignition Simulations and Games* — a small set of standalone interactive training modules/CYOA games embedded in the docs, not really a scripting reference.

---

## Gotchas and 8.3 notes

Clearly flagged in the source pages as new, changed, or removed for **8.3**:

* **NEW — Gateway config is now file-system based.** The single largest structural change referenced across these pages: 8.3 externalizes *all* Gateway configuration (not just projects) into `data/config`, human-readable and git-diffable, versus 8.1's internal-SQLite-only model. This is what makes full-Gateway version control, GitOps, and the Gateway REST API-driven CI/CD pipelines described in the Version Control Guide newly practical.
* **NEW — Deployment Modes.** A resource-collection inheritance mechanism letting a single configuration repository behave differently depending on which environment (dev/staging/prod) a Gateway identifies as, without manual reconfiguration at deploy time.
* **NEW — fully documented Gateway RESTful API**, explicitly positioned for GitOps/Infrastructure-as-code tooling (Ansible/Terraform/ArgoCD/Flux) and for triggering `scan/config` and `scan/projects` after a raw file pull.
* **NEW (8.3.4) — tag-level wildcards in Tag Change Script paths.** Previously wildcards in a Tag Change Script's path list only worked at the folder level; 8.3.4 added wildcard matching at the individual tag-name level too.
* **CHANGED — datasets no longer require `toPyDataSet()` conversion.** Ignition datasets can now be indexed/iterated directly with Python syntax (`for row in dataset: row["City"]`); the legacy `system.dataset.toPyDataSet()` conversion still works for old scripts but is redundant going forward.
* **CHANGED — Vision project encoding recommendation.** 8.3 recommends migrating Vision windows from binary `.bin` encoding to XML for version-control friendliness; this happens incrementally per-window as they're re-saved, and new resources default to XML automatically.
* **CHANGED — Java Service Wrapper upgraded to 3.5.56.** Behavioral change: using `wrapper.share.<n>.account` while the Ignition service runs under a system account now causes the wrapper service to **shut down** instead of silently ignoring the setting (relevant to the network-drive-mapping tutorial).
* **CHANGED — locale-format guidance formalized.** The docs now explicitly call out BCP-47 hyphenated tags (`en-US`) as the preferred format over the legacy underscore format (`en_US`), and document exactly which scripting functions/properties accept vs. always return each form — worth checking any pre-8.3 script that stores or compares locale strings.
* **REMOVED / deprecated — SUDS library.** No longer bundled with the Python Standard Library shipped in Ignition; its documentation page is retained only for legacy scripts and is explicitly marked deprecated. New SOAP integrations need a third-party library or a REST-based alternative.
* **Legacy path called out — Internal Historian (Legacy).** Still present and useful for small/remote deployments (~10M row / 1-week soft guidance), but named and documented as a legacy option relative to SQL-database-backed Historian Core storage.
* **Boundary condition worth remembering** — projects created before **Ignition 8.1** cannot be imported directly into 8.3; they must first be upgraded through an 8.1 Gateway, then exported/imported into 8.3.
