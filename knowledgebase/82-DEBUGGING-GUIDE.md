---
title: Debugging Guide
description: Finding and fixing problems systematically
---

> **Skill level:** 200 · **Read first:** [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 82-DEBUGGING-GUIDE

# Debugging Guide

Systematic approach to finding issues.

## Debugging Workflow

1. **Identify symptom** - What's wrong?
2. **Check logs** - Gateway logs, browser console
3. **Isolate** - Is it gateway, project, or client?
4. **Test** - Reproduce issue
5. **Fix** - Apply solution
6. **Verify** - Confirm fix works

## Check Logs First

**Gateway logs:**
```
C:\Program Files\Inductive Automation\Ignition\logs\ignition.log
```

**Search for ERROR:**
```bash
grep ERROR ignition.log | tail -20
```

**Look for patterns:**
- Repeated errors indicate root cause
- Timestamp matches issue time

**Browser console:**
```
F12 → Console tab
Look for JavaScript errors (red lines)
```

## Common Issues & Solutions

### "Tag not found" Error

**Error message:**
```
Could not read tag: [default]MyTag - tag does not exist
```

**Cause:** Typo in tag path or wrong provider

**Debug:**
1. Check tag exists in Designer
2. Verify provider: `[default]` vs `[opc]` vs `[sql]`
3. Verify spelling (case-sensitive)

**Fix:**
```python
# WRONG
system.tag.read("MyTag")

# RIGHT
system.tag.read("[default]MyTag")
```

### "Connection refused" (Database)

**Error:**
```
Unable to connect to database - connection refused
```

**Cause:** Database offline, firewall, credentials wrong

**Debug:**
1. Ping database host: `ping db.example.com`
2. Check credentials in Admin Console → Datasources → Test Connection
3. Check firewall allows port (usually 3306 for MySQL, 1433 for MSSQL)

**Fix:**
```
Admin Console → Datasources
Edit datasource → Test Connection
If fails, check: host, port, username, password, firewall
```

### Script Timeout

**Error:**
```
Script execution timeout after 30 seconds
```

**Cause:** Long-running operation in gateway script

**Debug:**
- Add logging to see where it hangs
- Check database query performance
- Verify loop isn't infinite

**Fix:**
```python
# SLOW: Blocks gateway
for i in range(1000000):
    system.tag.write(...)  # Slow

# FAST: Async
def slow_operation():
    for i in range(1000000):
        system.tag.write(...)

system.util.threadPool.execute(slow_operation)
```

### Component Not Updating

**Problem:** Component shows old value, doesn't refresh

**Cause:** Binding not created, tag quality bad

**Debug:**
1. Check binding exists in Designer
2. Check tag path in binding
3. Check tag quality (for OPC tags)

**Fix:**
```python
# Verify tag quality:
result = system.tag.read("[opc]Device/Value")
print(result.quality.name)  # Should be "Good"

# If Bad, check device connection
```

### OPC Tag Quality "Bad"

**Problem:** Tag shows Bad quality

**Causes:**
- Device offline
- Network disconnected
- Firewall blocking

**Debug:**
1. Ping device: `ping 192.168.1.100`
2. Check device is running
3. Check network cable/connection
4. Check firewall port open

**Fix:**
```
1. Restart device
2. Verify network connectivity
3. In Admin Console, restart OPC server
4. Check device firmware/driver updated
```

### Perspective Page Won't Load

**Error:** Blank page or "Error loading view"

**Cause:** Binding error, missing component, permission denied

**Debug:**
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check Admin Console logs for backend errors

**Fix:**
- If "permission denied": Check user role has access
- If binding error: Fix expression/tag path in view
- If component error: Check component properties

### Gateway Won't Start

**Error:** Service fails to start

**Cause:** Java not installed, port in use, corrupted files

**Debug:**
```bash
# Check Java:
java -version

# Check port 8088:
netstat -an | grep 8088

# Check logs:
tail -100 logs/wrapper.log
```

**Fix:**
```bash
# Install Java if missing
# Kill process on port 8088: lsof -i :8088 | kill
# Restart Ignition: net stop/start "Ignition"
```

## Debugging Tools

**Designer Tools:**
```
Tools → Logger (live log viewer)
Tools → Script Console (test Python code)
```

**Browser DevTools:**
```
F12 → Console (JavaScript errors)
F12 → Network (slow requests)
F12 → Performance (timing analysis)
```

**Command-line:**
```bash
# Tail live logs:
tail -f ignition.log

# Search logs:
grep "ERROR" ignition.log

# Count errors:
grep -c "ERROR" ignition.log
```

## Systematic Debug Process

**1. Reproduce:**
- Do you see error every time or intermittent?
- What action triggers it?

**2. Isolate:**
- Is it the gateway (check admin console)?
- Is it the project (try another project)?
- Is it the client (try different browser/device)?

**3. Check logs:**
- Gateway: `ignition.log`
- Browser: Console tab
- Database: `converter.log`

**4. Test component:**
- Create minimal test (one tag, one component)
- Does it work in isolation?
- Add complexity back one piece at a time

**5. Document:**
- Write down steps to reproduce
- Note exact error message
- Note gateway version, modules

---
**Golden Rule:** Logs are your friend. Always check them first.

---

## See Also

**Prerequisites:** [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)

**Builds toward:** [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
