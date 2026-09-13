---
title: Scripting - Python in Ignition
description: Scopes, execution contexts, patterns
---

> **Skill level:** 100 · **Read first:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 30-SCRIPTING-OVERVIEW

# Scripting (Python)

Ignition uses Jython (Python 2.7 compatible).

## Scopes

**Gateway Script:**
- Runs on gateway server
- Full access: tags, database, OPC, file system
- Best for: Long operations, data processing, integrations
- Execution: Scheduled, event-driven, manual trigger

**Vision Script:**
- Runs on Vision client (desktop app)
- Access: UI windows, local files, tags (via gateway)
- Best for: Client-side UI updates, user interactions
- Execution: Component events, window events

**Perspective Script:**
- Runs in browser session (sandboxed)
- Access: Tags (via gateway), component properties
- CANNOT: Direct file I/O, OPC access, DB queries
- Best for: Component logic, data validation, messaging
- Execution: Component events, message handlers

## Execution Contexts

| Context | Scope | Trigger |
|---------|-------|---------|
| Project Script | Gateway | Scheduled, event |
| Tag Event Script | Gateway | Tag change, alarm |
| Component Event | Perspective/Vision | User click, change |
| Gateway Event | Gateway | Startup, shutdown |
| Timer Script | Vision | Periodic timer |

## Basic Script Structure

```python
# Single script in component event handler
logger = system.util.getLogger("MyScript")
logger.info("Script executing")

# Read tag
value = system.tag.read("[default]MyTag").value
logger.info(f"Current value: {value}")

# Write tag
system.tag.write("[default]MyTag", value + 1)

# Message user
system.perspective.sendMessage("myMsg", {"data": 123})
```

## Error Handling

```python
try:
    value = system.tag.read("[default]MyTag").value
except:
    logger = system.util.getLogger("Error")
    logger.error("Failed to read tag")
    # Fallback logic
```

## Async Operations

Long operations block gateway. Use thread pool:

```python
def long_operation():
    # Slow DB query, OPC operation
    time.sleep(5)
    logger.info("Done")

# Run async (non-blocking)
system.util.threadPool.execute(long_operation)
```

## Scope Decision Tree

```
Need to:
  - Read/write tag? → Any scope (through gateway in Perspective)
  - Access device (OPC)? → Gateway only
  - Query database? → Gateway only (use gateway script or named query)
  - File I/O? → Gateway only
  - Update UI? → Vision or Perspective script
  - Scheduled operation? → Gateway script + schedule
```

---
**See:** [[31-SYSTEM-FUNCTIONS]] for complete API

---

## See Also

**Prerequisites:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

**Builds toward:** [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md), [33-APPENDIX-SCRIPTING-EXTENDED](33-APPENDIX-SCRIPTING-EXTENDED.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md)

**Related:** [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md), [21-BINDINGS](21-BINDINGS.md), [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
