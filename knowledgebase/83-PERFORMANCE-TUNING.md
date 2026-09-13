---
title: Performance Tuning
description: Optimization, bottleneck identification, best practices
---

> **Skill level:** 300 · **Read first:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 83-PERFORMANCE-TUNING

# Performance Tuning

Identify and fix slowness.

## Monitoring Tools

**Gateway Status:**
```
Admin Console → Status
- Memory usage (should be < 80% max)
- CPU (should be < 80%)
- Active sessions
- Tag count
```

**Script Logger:**
```
Admin Console → Diagnostics → Logs
- Review ignition.log for errors
- Look for repeating ERROR lines (indicator of problem)
```

**Client Performance:**
- Browser DevTools (F12) → Network tab
- Check page load time
- Look for slow requests

## Common Bottlenecks

### Slow Database Queries

**Symptom:** Dashboard takes 5+ seconds to load

**Diagnosis:**
```
Admin Console → Logs → converter.log
Look for slow queries (execution time > 1000ms)
```

**Fix:**
```sql
-- SLOW: No index
SELECT * FROM orders WHERE customer_id = 123

-- FAST: Index on customer_id
CREATE INDEX idx_customer ON orders(customer_id);
```

### Too Many Binding Updates

**Symptom:** Component flickering, high CPU

**Cause:** Many tags/expressions updating simultaneously

**Fix:**
- Debounce updates (add delay)
- Reduce polling frequency
- Use script trigger instead of binding

### Large Dataset in Table

**Symptom:** Table scrolling is slow

**Cause:** All rows rendered in memory

**Fix:**
```
Table Component
└── Props:
    - virtualized: true (render only visible rows)
    - pageSize: 50 (paginate instead of scroll)
```

### High Memory Usage

**Symptom:** Gateway memory > 90%, clients disconnect

**Cause:** Memory leak in script, too many tags, large datasets cached

**Fix:**
```python
# BAD: Stores all history in memory
all_data = system.db.query("SELECT * FROM history")  # 1M rows!

# GOOD: Batch process
query = "SELECT * FROM history LIMIT 1000 OFFSET ?"
for offset in range(0, 1000000, 1000):
    batch = system.db.query(query, [offset])
    process(batch)
```

### Slow Script Execution

**Symptom:** Gateway freezes for 5+ seconds

**Cause:** Long operation blocks gateway thread

**Fix:**
```python
# BAD: Blocks gateway
for i in range(1000000):
    system.tag.write(f"[default]Tag{i}", i)

# GOOD: Async
def batch_write():
    results = system.tag.readAll([...])  # Efficient
    system.tag.writeAll([...], [...])    # Batch write

system.util.threadPool.execute(batch_write)
```

## Optimization Techniques

### Query Optimization

**BAD:**
```python
for order_id in range(1, 10000):
    result = system.db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    # 10k queries!
```

**GOOD:**
```python
results = system.db.query("SELECT * FROM orders WHERE id IN (SELECT id FROM orders LIMIT 10000)")
# 1 query
```

### Tag Reading

**BAD:**
```python
for tag in ["[default]T1", "[default]T2", ..., "[default]T100"]:
    val = system.tag.read(tag).value  # 100 operations
```

**GOOD:**
```python
results = system.tag.readAll(["[default]T1", "[default]T2", ..., "[default]T100"])
vals = [r.value for r in results]  # 1 batch operation
```

### Binding vs Script

**Bindings** more efficient than scripts for simple updates.

**Use binding:**
```javascript
{tag: "[default]MyTag"}  // Optimized, efficient
```

**Avoid script:**
```python
# Bad: Runs every change
def onChange(self, event):
    self.parent.getChild("display").props.text = system.tag.read(...).value
```

### Polling Frequency

**Gateway config:**
```
Device Settings → Polling Interval
- Low-priority: 5000ms (5 sec)
- Normal: 1000ms (1 sec)
- Critical: 500ms (0.5 sec)
```

**Rule:** Slowest tolerable interval for your use case.

### Caching

**Cache static data:**
```python
# First load
if not hasattr(system.util, 'cache_data'):
    system.util.cache_data = system.db.query("SELECT * FROM config")

# Subsequent uses
config = system.util.cache_data

# Invalidate when needed
del system.util.cache_data  # Next load refreshes
```

## Monitoring Best Practices

**1. Set baseline metrics:**
- Normal gateway memory: 1.5GB
- Normal CPU: 20-30%
- Normal page load time: 1-2 sec

**2. Monitor regularly:**
- Weekly check of memory trend
- Check error log for recurring issues

**3. Capacity planning:**
- Track growth: +100 tags/week → need to add capacity
- Test at expected load before deploying

---
**Quick Checklist:**
- [ ] Enable virtualization on tables
- [ ] Use prepared queries, not string concat
- [ ] Batch database operations
- [ ] Use readAll/writeAll, not loops
- [ ] Add database indexes on filter columns
- [ ] Limit polling frequency to needed interval
- [ ] Monitor memory weekly

---

## See Also

**Prerequisites:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)

**Builds toward:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)

**Related:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
