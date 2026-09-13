---
title: Ignition Tags - The Central Data Model
description: Tag types, paths, binding syntax, tag engine
---

> **Skill level:** 100 · **Read first:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 20-TAGS-FUNDAMENTALS

# Tags - Central Data Model

**Tag** = Named data point in Ignition. Single source of truth for data.

Tags are the heart of Ignition. Everything flows through tags.

## Tag Types

### 1. Standard (Static/Manual)
**Source:** User manually sets value
```
Tag Name: ProductionCount
Value: 150 (int)
Can update via: UI binding, script, API
```

### 2. OPC-UA (Device Data)
**Source:** Device/PLC via OPC-UA protocol
```
Tag Name: MotorSpeed
OPC Path: ns=2;s=Production/Motor_01/Speed
Value: Live from PLC (updated continuously)
Read-only (unless device supports write)
```

### 3. Expression (Calculated)
**Source:** Expression that recalculates when dependencies change
```
Tag Name: SpeedKPH
Expression: {MotorSpeed} * 3.6
Value: Auto-calculated
```

### 4. SQL Query (Database)
**Source:** Database query
```
Tag Name: TotalProduction
Query: SELECT SUM(quantity) FROM production WHERE date = TODAY()
Value: Query result refreshed on schedule
Polling interval configurable
```

### 5. Memory (Temporary)
**Source:** Runtime storage, resets on gateway restart
```
Tag Name: SessionUserID
Value: Temporary, no persistence
Use for: Script variables, UI state
```

## Tag Paths

Format: `[provider]folder/subfolder/tagName`

**Examples:**
```
[default]Production/LineA/Speed
[OPC]Devices/PLC1/Temperature
[SQL]Reports/DailyTotal
[Memory]Session/UserID
```

**Provider** = Data source
- `[default]` - Standard/Expression/Memory tags
- `[OPC]` - OPC-UA device tags (configured OPC server)
- `[SQL]` - SQL query tags
- `[History]` - Historical data (read-only)

**Folder/Path** = Organization (like file folders)

**Tag Name** = The actual tag identifier

## Tag Properties

Every tag has metadata:

| Property | Meaning |
|----------|---------|
| `Name` | Tag identifier |
| `Type` | Data type (int, float, bool, string, datetime) |
| `Value` | Current value |
| `Quality` | Good/Bad/Uncertain (OPC quality) |
| `Expression` | (if expression tag) calculation formula |
| `OPC Path` | (if OPC tag) device address |
| `Query` | (if SQL tag) database query |
| `Polling Interval` | (if SQL tag) how often to query |
| `Documentation` | Description of tag purpose |

## Reading Tags

### From Component (Binding)
**Most Common** - Automatic, efficient
```javascript
// In component prop binding:
{tag: "[default]Production/Speed"}
```

Component automatically updates when tag changes.

### From Script
```python
# Single tag
value = system.tag.read("[default]MyTag").value

# Multiple tags (more efficient)
result = system.tag.readAll(["[default]Tag1", "[default]Tag2"])
tag1_value = result[0].value
tag2_value = result[1].value

# Blocking read (wait for response)
value = system.tag.readBlocking("[default]MyTag", timeout=5000)  # 5 sec timeout
```

## Writing Tags

### From Component (Event Handler)
```python
# In component onClick event:
system.tag.write("[default]MyTag", 42)

# Multiple tags at once
system.tag.writeAll(
    ["[default]Tag1", "[default]Tag2"],
    [100, "ON"]
)
```

### From Script (Gateway)
```python
# Write from gateway script (most common)
system.tag.write("[default]Production/LineA/Running", True)

# With quality/timestamp (advanced)
from com.inductiveautomation.ignition.common import QualityCode
system.tag.write("[default]MyTag", 42, QualityCode.Good)
```

## Tag Naming Conventions

**Good Practices:**
- `PascalCase` for tag names (MyTag, ProductionCount)
- Use folders for organization (Production/Line01/Speed not ProductionLine01Speed)
- Descriptive names (Temperature not Temp, not T)
- No special characters (use `_` not `-` or spaces)
- Lowercase provider: `[default]`, `[opc]`, `[sql]`

**Bad:**
```
[default]production-line-A-motor-speed  // Hyphenated, hard to read
[Default]MotorSpeed  // Wrong provider case
[default]T  // Unclear abbreviation
```

**Good:**
```
[default]Production/LineA/MotorSpeed  // Clear hierarchy
[opc]Devices/PLC01/Temperature  // Organized
[sql]Reports/DailyTotal  // Purpose-driven
```

## Tag Permissions

Tags respect user permissions:
- **Read** - User can read tag
- **Write** - User can modify tag
- **Execute** - User can run tag (if callable)

Set in Designer's tag configuration. Enforced at runtime.

## Tag Memory & Persistence

**Standard Tags:**
- Persist to disk (survive gateway restart)
- Loaded on startup

**Memory Tags:**
- Lost on gateway restart
- Use for: UI state, temporary calculations

**Database Tags (SQL):**
- Query results cached in memory
- Refreshed on polling interval
- Not persistent (query is source of truth)

## Performance Implications

**Efficient:**
- Bind component to tag (automatic, optimized)
- Use `readAll()` for multiple tags in script
- Use polling interval for SQL tags (not continuous queries)

**Inefficient:**
- Looping script reading one tag at a time
- Frequent database queries (polling at 100ms)
- Expression tags with many dependencies

**Optimization:**
```python
# SLOW
for tag in ["[default]Tag1", "[default]Tag2", "[default]Tag3"]:
    value = system.tag.read(tag).value

# FAST
values = system.tag.readAll(["[default]Tag1", "[default]Tag2", "[default]Tag3"])
for result in values:
    value = result.value
```

## Tag Scope

**Global** - Accessible from anywhere (bindings, scripts, components)
**Local to View** - Embedded View has own tag namespace (not common)

## Common Gotchas

1. **Forgetting provider:** `system.tag.read("MyTag")` fails → `system.tag.read("[default]MyTag")` works
2. **Case sensitive:** `[default]myTag` ≠ `[default]MyTag`
3. **Quality check:** OPC tags can have Bad quality if device disconnected
4. **SQL polling:** Query runs every polling interval (expensive!)
5. **Expression loops:** `Tag A = Tag B`, `Tag B = Tag A` = infinite loop

---
**See Also:**
- [[21-BINDINGS]] - How to bind tags to components
- [[22-EXPRESSIONS]] - Tag expressions syntax
- [[31-SYSTEM-FUNCTIONS]] (system.tag.*) - Tag scripting API

---

## See Also

**Prerequisites:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

**Builds toward:** [21-BINDINGS](21-BINDINGS.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)

**Related:** [21-BINDINGS](21-BINDINGS.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
