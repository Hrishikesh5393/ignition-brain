---
title: Scripting Patterns & Best Practices
description: Common patterns, gotchas, optimization
---

> **Skill level:** 200 · **Read first:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 32-SCRIPTING-PATTERNS

# Scripting Patterns

## Pattern: Tag Read Multiple

**Slow (wrong):**
```python
for tag in ["[default]T1", "[default]T2", "[default]T3"]:
    val = system.tag.read(tag).value
```

**Fast (right):**
```python
results = system.tag.readAll(["[default]T1", "[default]T2", "[default]T3"])
values = [r.value for r in results]
```

## Pattern: Conditional Tag Write

```python
# If value > 100, write ALARM; else NORMAL
status = "ALARM" if {[default]Sensor} > 100 else "NORMAL"
system.tag.write("[default]Status", status)
```

## Pattern: Database Query with Safety

**Vulnerable (SQL injection):**
```python
query = f"SELECT * FROM data WHERE id = {user_id}"
system.db.query(query)  # UNSAFE!
```

**Safe (prepared statement):**
```python
query = "SELECT * FROM data WHERE id = ?"
system.db.runPreparedQuery(query, [user_id])
```

## Pattern: Message Handler (Perspective)

**Send:**
```python
# In component event script:
system.perspective.sendMessage("updateData", {"id": 42, "value": 100})
```

**Receive:**
```python
# In view's messageHandler event:
if messageId == "updateData":
    payload = message.get("data")
    self.getSibling("output").props.text = f"ID: {payload['id']}"
```

## Pattern: Date Arithmetic

```python
from com.inductiveautomation.ignition.common.script import KeyboardInterrupt
import system

# Yesterday
yesterday = system.date.addDays(system.date.today(), -1)

# 1 hour from now
later = system.date.addHours(system.date.now(), 1)

# Format date
formatted = system.date.format(system.date.now(), "yyyy-MM-dd HH:mm:ss")
```

## Pattern: Debounce Component Change

```python
# In component onChange event:
# Only act if value hasn't changed for 1 second

import threading

def delayed_action(val):
    time.sleep(1)
    system.tag.write("[default]Result", val)

# Cancel previous timer if running
if hasattr(self, "_timer"):
    self._timer.cancel()

# Start new timer
import threading
self._timer = threading.Timer(1.0, delayed_action, [self.props.value])
self._timer.start()
```

## Pattern: Batch Database Insert

**Slow:**
```python
for row in data:
    system.db.runUpdateQuery(f"INSERT INTO table VALUES(...)")  # Repeated transactions
```

**Fast:**
```python
# Use transaction
txid = system.db.beginTransaction()
try:
    for row in data:
        system.db.runUpdateQuery("INSERT INTO table VALUES(?)", [row], txid=txid)
    system.db.commitTransaction(txid)
except:
    system.db.rollbackTransaction(txid)
```

## Gotchas

1. **Blocking gateway:** Long sleep/loop blocks all clients
   - **Fix:** Use `threadPool.execute()` for long ops

2. **Tag path typos:** `{MyTag}` instead of `{[default]MyTag}`
   - **Fix:** Always include provider

3. **Circular dependencies:** Tag A references B, B references A
   - **Fix:** Use intermediate tag

4. **Scope violation:** Trying file I/O in Perspective script
   - **Fix:** Move to Gateway script, expose via tag

5. **Unicode tags:** Non-ASCII characters in tag path
   - **Fix:** Use `u"[default]HÅ/Motor"` (unicode prefix)

6. **Exception swallowing:**
   ```python
   try:
       dangerous_operation()
   except:
       pass  # BAD - silent failure
   ```
   - **Fix:** Log error: `logger.error("Operation failed", exc_info=True)`

---
**Performance:** Prefer bindings over scripts when possible (more efficient)

---

## See Also

**Prerequisites:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md)

**Builds toward:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [QUICK-REFERENCE](QUICK-REFERENCE.md)

**Related:** [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [QUICK-REFERENCE](QUICK-REFERENCE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
