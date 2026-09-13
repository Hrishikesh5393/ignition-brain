---
title: Logging and Diagnostics
description: Log locations, reading logs, debugging
---

> **Skill level:** 200 · **Read first:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 62-LOGGING-DIAGNOSTICS

# Logging & Diagnostics

Gateway and project logs for troubleshooting.

## Log Locations

**Windows:**
```
C:\Program Files\Inductive Automation\Ignition\logs\
```

**Linux:**
```
/opt/ignition/logs/
```

**Files:**
- `wrapper.log` - Java/gateway startup
- `ignition.log` - Main gateway + modules
- `audit.log` - User actions, security events
- `converter.log` - Database operations
- `modules/` - Module-specific logs (MQTT, OPC, etc.)

## Reading Logs

**tail (live):**
```bash
tail -f ignition.log
```

**grep (search):**
```bash
grep "ERROR" ignition.log
grep "OPC" ignition.log | head -50
```

**Date filter:**
```bash
grep "2026-07-13" ignition.log
```

## Log Levels

| Level | Severity | Use |
|-------|----------|-----|
| **DEBUG** | Low | Detailed diagnostic info |
| **INFO** | Low | Normal operations |
| **WARN** | Medium | Potential issue |
| **ERROR** | High | Something failed |
| **FATAL** | Critical | System crashed |

## Ignition Console Logging

**In scripts:**
```python
logger = system.util.getLogger("MyScript")
logger.debug("Debug info")
logger.info("Normal message")
logger.warn("Warning!")
logger.error("Error occurred")
```

**Output:** Appears in `ignition.log` tagged with logger name.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `OPC Server not found` | OPC device offline | Check network, restart device |
| `Database connection failed` | DB unreachable | Check connection string, firewall |
| `Tag path not found` | Typo in tag ref | Verify provider: `[default]` vs `[opc]` |
| `Permission denied` | User lacks role | Check security settings |
| `Null pointer` | Tag/component undefined | Check bindings, initialization order |
| `Timeout` | Operation took too long | Increase timeout, check performance |

## Debugging Techniques

**1. Add logging:**
```python
logger = system.util.getLogger("Debug")
logger.info(f"Current value: {tag_value}")
```

**2. Check tag quality:**
```python
result = system.tag.read("[default]MyTag")
if result.quality.name != "Good":
    logger.warn(f"Tag quality: {result.quality}")
```

**3. Monitor in Designer:**
Desktop → Tools → Logger (view logs in real-time)

**4. HTTP Status:**
Gateway at `localhost:8088/web/home` → Status page shows modules, DB connections

**5. Script debugging:**
```python
# Pause and debug point
import pdb; pdb.set_trace()
```
(Advanced - not recommended in production)

## Performance Monitoring

**Gateway status:**
```
http://localhost:8088/web/admin
```
Shows: CPU, memory, active sessions, tag count

**Database queries:**
- Check `converter.log` for slow queries
- Look for repeated queries (inefficiency)

**Memory leaks:**
- Monitor `wrapper.log` for heap size growth
- Restart if out of memory approaching limit

---
**Quick Checklist:**
1. Check `ignition.log` for ERROR lines
2. Verify tag paths include provider: `[default]TagName`
3. Check network connectivity (OPC, database)
4. Verify user permissions
5. Check tag quality (OPC tags only)

---

## See Also

**Prerequisites:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md)

**Builds toward:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)

**Related:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
