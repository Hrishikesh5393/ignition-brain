---
title: Gotchas, Common Mistakes, Bugs
description: Known issues, workarounds, what NOT to do
---

> **Skill level:** 200 · **Read first:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 81-GOTCHAS-BUGS

# Gotchas & Common Mistakes

## Tag Paths

**Wrong:** `{MyTag}` → Missing provider, won't find tag
**Right:** `{[default]MyTag}` → Includes provider

**Wrong:** `{[Default]MyTag}` → Case sensitive, should be lowercase
**Right:** `{[default]MyTag}`

**Wrong:** Tag path with spaces: `{[default]My Tag}`
**Right:** Use underscore: `{[default]My_Tag}`

## Expressions

**Wrong:** Circular reference: `Tag_A = Tag_B + 1` and `Tag_B = Tag_A + 1`
**Right:** Use intermediate: `Tag_A_Calc = Tag_B + 1`

**Wrong:** Missing concatenation operator: `"Hello" "World"`
**Right:** `concat("Hello", " ", "World")` or `"Hello" + "World"`

## Scripts

**Wrong:** Blocking operation in gateway script
```python
time.sleep(30)  # Blocks ALL clients for 30 sec!
```
**Right:** Use threadPool
```python
system.util.threadPool.execute(long_operation)
```

**Wrong:** SQL injection
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
system.db.query(query)  # VULNERABLE
```
**Right:** Prepared query
```python
system.db.runPreparedQuery("SELECT * FROM users WHERE id = ?", [user_id])
```

**Wrong:** No error handling
```python
value = system.tag.read("[default]MyTag").value  # May crash if tag missing
```
**Right:**
```python
result = system.tag.read("[default]MyTag")
if result and result.value:
    value = result.value
else:
    logger.error("Tag not found")
```

**Wrong:** Silent failures
```python
try:
    dangerous_operation()
except:
    pass  # User won't know it failed
```
**Right:** Log or notify
```python
try:
    dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

## OPC-UA Tags

**Issue:** Tag quality "Bad" even though device online
**Cause:** Device returned bad quality (not connected, out of range)
**Fix:** Check tag quality before using value

**Issue:** Can't browse OPC server
**Cause:** OPC server offline or unreachable
**Fix:** Verify network, restart device, check firewall

## Database

**Issue:** Slow queries
**Cause:** No index, querying large table without WHERE
**Fix:** Add index on column, filter queries

**Issue:** Connection pool exhausted
**Cause:** Too many open queries, not closing connections
**Fix:** Gateway closes automatically, but review query count

**Issue:** Data won't sync
**Cause:** SQL user lacks permissions or network down
**Fix:** Test connection in Admin Console

## Components

**Issue:** Component not updating after tag change
**Cause:** Binding not created or expression syntax wrong
**Fix:** Check binding in Designer, verify tag path

**Issue:** Table/Tree very slow with many rows
**Cause:** No virtualization, rendering all rows
**Fix:** Enable virtualization in component config (automatic in modern versions)

**Issue:** Popup not showing
**Cause:** Z-index issue or off-screen
**Fix:** Check position, add to correct parent container

## Perspective Specific

**Issue:** Browser session lost, data cleared
**Cause:** Page refresh, browser crash, session timeout
**Fix:** Use persistent tags (not memory tags) for important data

**Issue:** Can't read file or execute command
**Cause:** Perspective script is sandboxed (security)
**Fix:** Create Gateway script to do file I/O, expose via tag

## Vision Specific

**Issue:** Client won't start
**Cause:** Vision client not installed or corrupted
**Fix:** Reinstall Vision client

**Issue:** Window won't open
**Cause:** Window path wrong or doesn't exist
**Fix:** Verify window name in Designer project tree

## Performance

**Issue:** Gateway slow, CPU high
**Cause:** Inefficient scripts, too many database queries, many bindings updating
**Fix:** Use `readAll()` not loop read, batch database ops, reduce polling frequency

**Issue:** Perspective pages slow to load
**Cause:** Too many components, large dataset binding
**Fix:** Lazy load components, paginate data, use virtual list

---
**Golden Rule:** Test on fresh install before deploying production.

---

## See Also

**Prerequisites:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

**Builds toward:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
