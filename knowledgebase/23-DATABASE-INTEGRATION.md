---
title: Database Integration
description: Connections, queries, historical data
---

> **Skill level:** 200 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 23-DATABASE-INTEGRATION

# Database Integration

Connect to SQL databases for queries, storage, historical data.

## Setup Datasource

**Admin Console:**
```
Config → Databases → New Datasource
```

**Types:** MySQL, MSSQL, PostgreSQL, Oracle, SQLite

**Credentials:**
- Host, port, database name
- Username, password
- Connection string (if advanced)

**Test:** Click "Test Connection"

## Query Methods

**Named Query (recommended):**
```
Designer → Project → Named Queries → Add
Write SQL query once, reuse everywhere
Call: system.db.runNamedQuery("path/QueryName")
```

**Direct Query:**
```python
# SELECT (returns dataset)
result = system.db.query("SELECT * FROM table", [], "datasourceName")
for row in result:
    print row["columnName"]

# INSERT/UPDATE/DELETE
system.db.runUpdateQuery("INSERT INTO table VALUES(?, ?)", [val1, val2])

# Single value
count = system.db.queryValue("SELECT COUNT(*) FROM table")
```

## Prepared Statements (Safe)

Always use `?` placeholders:

```python
# UNSAFE
query = f"SELECT * FROM users WHERE id = {user_id}"

# SAFE
query = "SELECT * FROM users WHERE id = ?"
result = system.db.runPreparedQuery(query, [user_id])
```

## Transactions

```python
txid = system.db.beginTransaction("datasource")
try:
    system.db.runUpdateQuery("INSERT INTO log VALUES(?)", [msg], txid=txid)
    system.db.runUpdateQuery("UPDATE status SET count = count + 1", [], txid=txid)
    system.db.commitTransaction(txid)
except:
    system.db.rollbackTransaction(txid)
```

## SQL Query Tags

Create tag that queries on schedule:

```
Tag Properties:
- Type: Query
- Query: SELECT temperature FROM sensors WHERE active = 1
- Polling Interval: 5 (seconds)
- Datasource: production_db
```

Tag value = Query result (dataset)

## Tag Historian

**Automatic persistence:**
Tags marked for history → Values logged to database automatically.

**Query historical data:**
```python
# Get last 24 hours of temperature data
query = system.tag.queryTagCalculations(
    "[default]Sensors/Temperature",
    [8000],  # 8000 = average calculation
    startDate=system.date.addHours(system.date.now(), -24),
    endDate=system.date.now()
)
```

**Common calculations:**
- 8000 = Average
- 8001 = Minimum
- 8002 = Maximum
- 8003 = Count

## Connection Pooling

Ignition manages connection pool automatically.
- Max connections configurable
- Recycles stale connections
- Thread-safe

**Issue:** Pool exhausted if too many long-running queries
**Fix:** Optimize queries, add connection pool size

## Performance Tips

1. **Index columns** used in WHERE clauses
2. **Avoid SELECT \*** → Specify columns needed
3. **Use LIMIT** on large queries
4. **Batch inserts** in transactions, not individually
5. **Cache results** if data doesn't change frequently

---
**Common Mistake:** 
```python
# DON'T loop and query:
for id in ids:
    system.db.query(f"SELECT * FROM table WHERE id = {id}")  # N queries!

# DO batch:
system.db.query(f"SELECT * FROM table WHERE id IN ({','.join(map(str, ids))})")  # 1 query
```

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Builds toward:** [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [28-PLATFORM-TRANSACTIONS-SFCS](28-PLATFORM-TRANSACTIONS-SFCS.md)

**Related:** [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
