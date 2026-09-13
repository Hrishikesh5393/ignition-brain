> **Skill level:** 300 · **Read first:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 90-DATABASE-ADVANCED-OPTIMIZATION

# Ignition 8.3 Database Advanced: Optimization

## Overview
Deep-dive guide for tuning database performance in Ignition 8.3 deployments — query optimization, connection pool tuning, transaction isolation, historian storage/compression, database-specific tuning (MySQL, PostgreSQL, SQL Server, Oracle), monitoring, backup strategy, and capacity planning. Complements `23-DATABASE-INTEGRATION.md` and `26-PLATFORM-DATABASE-HISTORIAN.md`, which cover connection setup and basic historian configuration.

---

## 1. Query Optimization

### 1.1 Indexing Strategy

Ignition-generated historian tables (`sqlt_data_1_*`) and transaction group tables are read/written constantly. Missing or wrong indexes are the single most common cause of slow dashboards.

**Core index rules:**

| Table Type | Recommended Index | Reason |
|---|---|---|
| `sqlth_te` (tag events) | `tagid`, `intervalid` | Historian queries filter by tag path resolution |
| `sqlt_data_1_YYYY_MM` (partitioned data) | `(tagid, t_stamp)` composite | Every tag-history query filters both |
| Transaction group tables | Primary key on timestamp or surrogate ID | Prevents full scans on insert-heavy tables |
| Custom Named Query source tables | Index on WHERE/JOIN columns | Named Queries run frequently from bindings |

**Example — composite index for a custom production log table:**

```sql
CREATE INDEX idx_prodlog_line_time
ON production_log (line_id, event_timestamp DESC);
```

Composite index column order matters: put the equality-filter column (`line_id`) first, the range/sort column (`event_timestamp`) second. This lets the engine seek to the right line, then scan in timestamp order without an extra sort.

**Avoid over-indexing.** Every index adds write overhead. On tables ingesting historian data at sub-second intervals, more than 3-4 indexes per table starts measurably slowing inserts. Audit unused indexes quarterly.

```sql
-- MySQL: find unused indexes
SELECT object_schema, object_name, index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL AND count_star = 0
ORDER BY object_schema, object_name;
```

### 1.2 Reading Execution Plans

Before changing anything, capture the plan for the exact query Ignition is issuing (visible in Named Query editor's preview, or via `system.db.runQuery` logging).

**MySQL / MariaDB:**
```sql
EXPLAIN ANALYZE
SELECT t_stamp, floatvalue
FROM sqlt_data_1_2026_07
WHERE tagid = 4821
  AND t_stamp BETWEEN 1752000000000 AND 1752086400000
ORDER BY t_stamp;
```
Watch for `type: ALL` (full table scan) — this means the composite index is missing or the query can't use it (e.g., wrapping the indexed column in a function).

**PostgreSQL:**
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT t_stamp, floatvalue
FROM sqlt_data_1_2026_07
WHERE tagid = 4821
  AND t_stamp BETWEEN 1752000000000 AND 1752086400000
ORDER BY t_stamp;
```
Look for `Seq Scan` vs `Index Scan`. `Seq Scan` on a table with millions of rows is the red flag. Check `Buffers: shared hit=X read=Y` — high `read` relative to `hit` means the working set doesn't fit in `shared_buffers` and pages are coming from disk.

**SQL Server:**
```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
SELECT t_stamp, floatvalue
FROM sqlt_data_1_2026_07
WHERE tagid = 4821
  AND t_stamp BETWEEN 1752000000000 AND 1752086400000
ORDER BY t_stamp;
```
Or use `SET SHOWPLAN_XML ON` / the graphical execution plan in SSMS. Look for "Missing Index" suggestions (SSMS surfaces these automatically) and "Key Lookup" operators, which usually mean a nonclustered index doesn't cover all needed columns.

**Oracle:**
```sql
EXPLAIN PLAN FOR
SELECT t_stamp, floatvalue
FROM sqlt_data_1_2026_07
WHERE tagid = 4821
  AND t_stamp BETWEEN 1752000000000 AND 1752086400000
ORDER BY t_stamp;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```
Watch the `Cost` column and check for `TABLE ACCESS FULL` on large partitions — a sign the partition pruning or index isn't being used.

### 1.3 Named Query and Binding Query Optimization

**Common anti-patterns found in Ignition projects:**

| Anti-pattern | Fix |
|---|---|
| `SELECT *` in a Named Query bound to a table component | Select only the columns rendered; reduces network payload and lets covering indexes apply |
| Query bound directly to a component with a 1-second polling rate | Move to a cache-friendly binding (Tag History binding with appropriate aggregation, or increase poll interval) |
| String concatenation building dynamic WHERE clauses in scripts | Use Named Query parameters (`:paramName`) so the DB can cache the execution plan |
| Nested subqueries repeated per row | Rewrite as JOIN or use a CTE (`WITH` clause) evaluated once |
| Nightly reports scanning full historian tables | Aggregate incrementally (materialized/summary tables) instead of scanning raw data each run |

**Example — parameterized Named Query (plan-cacheable) vs string-built (not cacheable):**

```sql
-- Good: parameterized, plan reused across calls
SELECT line_id, event_timestamp, event_type
FROM production_log
WHERE line_id = :lineId
  AND event_timestamp >= :startTime
  AND event_timestamp <  :endTime
ORDER BY event_timestamp;
```

```python
# Bad: forces a new plan on every distinct string, defeats plan cache
query = "SELECT * FROM production_log WHERE line_id = " + str(lineId)
system.db.runQuery(query)
```

### 1.4 Batch Operations

For scripted bulk inserts/updates (e.g., recipe imports, historical backfills), use `system.db.runPrepUpdate` in a loop only for small counts. For larger batches, use `system.db.runScalarPrepUpdate` with batched multi-row `INSERT` statements or `system.db.runPrepUpdate` with an array of parameter sets where the driver supports batching, to avoid one network round-trip per row.

```python
# Batch insert pattern - build multi-row VALUES clause in chunks of ~500
rows = [(t, v) for t, v in data]
chunk_size = 500
for i in range(0, len(rows), chunk_size):
    chunk = rows[i:i+chunk_size]
    placeholders = ",".join(["(?,?)"] * len(chunk))
    query = "INSERT INTO staging_table (t_stamp, value) VALUES " + placeholders
    params = [item for row in chunk for item in row]
    system.db.runPrepUpdate(query, params)
```

---

## 2. Connection Pooling Configuration

Connection pool sizing is a balance: too few connections cause queuing and timeouts under load; too many exhaust the database's `max_connections` and waste memory (each connection has overhead on the DB server, not just the gateway).

### 2.1 Sizing Guidance

| Deployment Size | Max Pool Size | Notes |
|---|---|---|
| Small (single gateway, <50 clients) | 15-25 | Default is often sufficient |
| Medium (multiple projects, 50-200 clients) | 25-60 | Separate pools per critical project if contention appears |
| Large / Enterprise (redundant gateways, 200+ clients, heavy historian writes) | 60-150, split across dedicated connections for historian vs. transactional | Historian writes should use a dedicated connection to avoid blocking interactive queries |

**Rule of thumb:** `Max Pool Size` should never approach the database server's `max_connections` when summed across *all* gateways/applications hitting it. Reserve headroom (20-30%) for admin tools, replication processes, and other consumers.

### 2.2 Key Parameters (Gateway > Config > Databases > Connections)

```
Max Active Connections:   50        (hard cap on concurrent connections)
Max Idle Connections:     8         (connections kept warm when idle)
Min Idle Connections:     2         (floor maintained even under no load)
Connection Age Limit:     28800000  (ms; recycle connections every 8 hrs to avoid stale TCP/firewall drops)
Validation Query:         SELECT 1
Test On Borrow:           true      (validate before handing to a query - catches dead connections)
Test While Idle:          true      (background validation, catches issues before they're borrowed)
Time Between Eviction Runs: 30000   (ms; how often idle-connection reaper runs)
Query Timeout:            60        (seconds; abort runaway queries)
```

**Test On Borrow vs Test While Idle:** `Test On Borrow` adds a small latency to every checkout (a lightweight `SELECT 1` round trip) but guarantees the connection handed to your query is alive. `Test While Idle` does this in the background so borrow-time stays fast. Running both is common in production — background validation for speed, borrow validation for correctness under flaky network conditions (VPNs, WAN links to remote sites).

### 2.3 Diagnosing Pool Exhaustion

Symptoms: intermittent "Unable to get connection" errors, dashboards that hang for exactly `Max Wait Time` seconds before failing, or slow logins.

Check Gateway > Status > Databases for the connection panel showing active/idle counts. If **Active** consistently sits at **Max Active**, either:
1. Something is leaking connections (script not closing a `system.db.beginTransaction()` or throwing before `commitTransaction`), or
2. Genuine load exceeds the pool — raise `Max Active` (after confirming the DB server can handle it) or split load across a dedicated pool.

```python
# Correct transaction pattern - always closes in finally
txId = system.db.beginTransaction(database="ProdDB", timeout=30000)
try:
    system.db.runPrepUpdate("INSERT INTO log (msg) VALUES (?)", [message], tx=txId)
    system.db.commitTransaction(txId)
except Exception as e:
    system.db.rollbackTransaction(txId)
    raise
finally:
    system.db.closeTransaction(txId)
```

---

## 3. Transaction Tuning

### 3.1 Isolation Levels

| Isolation Level | Behavior | When to Use in Ignition |
|---|---|---|
| **READ UNCOMMITTED** | Dirty reads possible | Rarely appropriate; only for non-critical dashboard reads where staleness is fine and you need max throughput |
| **READ COMMITTED** | No dirty reads; default for most engines (PostgreSQL, SQL Server, Oracle) | Default choice for most transaction groups and Named Query writes |
| **REPEATABLE READ** | No dirty/non-repeatable reads; MySQL InnoDB default | Use when a transaction reads the same row multiple times and needs consistency within that transaction |
| **SERIALIZABLE** | Full isolation, highest locking cost | Only for critical sequences (e.g., generating unique batch/lot numbers) where race conditions are unacceptable |

Set at the connection or query level. In Ignition, transaction isolation is generally controlled at the JDBC connection string or driver default; for per-transaction overrides, use `system.db.beginTransaction(database, isolationLevel, timeout)` where `isolationLevel` accepts constants like `system.db.READ_COMMITTED`, `system.db.SERIALIZABLE`, etc.

```python
txId = system.db.beginTransaction(
    database="ProdDB",
    isolationLevel=system.db.SERIALIZABLE,
    timeout=15000
)
```

**Guidance:** Default to READ COMMITTED unless you have a specific consistency requirement. SERIALIZABLE on high-frequency transaction groups will cause lock contention and throughput collapse under concurrent writers.

### 3.2 Deadlock Prevention and Diagnosis

Deadlocks typically occur when multiple transactions (e.g., two transaction groups, or a transaction group and a scripted process) update the same rows in different orders.

**Prevention:**
- Always acquire locks / update rows in a **consistent order** across all code paths (e.g., always update `parent_table` before `child_table`).
- Keep transactions **short** — do not hold a transaction open across a script's slow external call (email, HTTP request); commit first, then perform the slow operation.
- Avoid interactive-style logic (user prompts, waits) inside an open transaction.

**Diagnosis:**

MySQL:
```sql
SHOW ENGINE INNODB STATUS\G
-- Review the LATEST DETECTED DEADLOCK section
```

PostgreSQL:
```sql
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query,
       blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
 AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
 AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
 AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

SQL Server: enable Trace Flag 1222 or use Extended Events session `system_health` to capture deadlock graphs (`xml_deadlock_report`).

Ignition's Gateway logs (`wrapper.log` / Gateway Console > Diagnostics > Logs) will surface JDBC deadlock exceptions (`Deadlock found when trying to get lock`, SQLState `40001`) — set the logger for `com.inductiveautomation.ignition.gateway.datasource` to DEBUG temporarily when chasing intermittent deadlocks.

### 3.3 Lock Contention Reduction

- Use row-level locking (default on InnoDB/PostgreSQL/SQL Server with default isolation) rather than table locks.
- Avoid `SELECT ... FOR UPDATE` on wide row ranges; scope it as tightly as possible.
- For high-frequency transaction groups writing to the same table from multiple lines/areas, consider partitioning by a natural key (e.g., separate tables per line) to eliminate cross-line contention entirely.

---

## 4. Historian Optimization

### 4.1 Tag Grouping and Scan Class Alignment

Group tags with similar logging requirements into shared scan classes rather than one-off custom rates per tag. Fewer distinct scan classes mean fewer distinct write patterns hitting the historian tables, which improves batching efficiency.

| Data Category | Suggested Scan Class | Store Mode |
|---|---|---|
| Critical process variables (temp, pressure) | 1s Rapid | On-change with deadband |
| Standard production tags | 10s Standard | On-change with deadband |
| Slow-moving setpoints/config | 60s Slow | On-change only, no periodic |
| KPIs / rollups | 5 min | Periodic (already aggregated) |

### 4.2 Compression and Deadband Tuning

Ignition's historian uses **on-change logging** with configurable deadband (absolute or percent) plus a max time between forced writes. Poorly tuned deadbands are the #1 cause of bloated historian tables.

```
Tag History Settings:
  Deadband Mode:        Analog
  Deadband Style:        Percent of Span (recommended over absolute for tags with EU ranges)
  Deadband Value:        0.25% - 1% typical for analog process tags
  Max Time Between Rec:  15 min - 1 hr (forces a record even if value is flat, for gap detection)
```

**Sizing impact example:** A pressure tag scanning at 1s with no deadband generates ~86,400 rows/day. With a 0.5% deadband tuned to real process noise, the same tag might generate 500-2,000 rows/day — a 40-170x reduction with no meaningful loss of trend fidelity.

Audit deadband effectiveness periodically:
```sql
-- Rows/day per tag over the last 7 days - flag tags with unexpectedly high counts
SELECT te.tagpath, COUNT(*) / 7.0 AS avg_rows_per_day
FROM sqlt_data_1_2026_07 d
JOIN sqlth_te te ON te.id = d.tagid
WHERE d.t_stamp > (UNIX_TIMESTAMP(NOW() - INTERVAL 7 DAY) * 1000)
GROUP BY te.tagpath
ORDER BY avg_rows_per_day DESC
LIMIT 20;
```

### 4.3 Partitioning Strategy

Ignition auto-partitions historian data tables (default monthly: `sqlt_data_1_YYYY_MM`). Confirm the **Partitioning** settings under Gateway > Config > Tags > History match your query patterns:

- **Partition size:** Monthly is standard for moderate volume. High-volume sites (millions of rows/day) may benefit from weekly partitions to keep individual table/index sizes manageable and speed up partition pruning.
- **Partition pre-creation:** Ensure the historian pre-creates the next partition before month-end to avoid a write stall at the boundary.

### 4.4 Archival and Purge Policy

Configure automatic purging under **Tag History > Storage** to move old data out of the "hot" query path.

```
Partitioning:
  Enabled:              true
  Partition Size:        1 Month
  Data Retention:         13 Months (rolling)
  Auto-purge:             Enabled, runs nightly at low-traffic window (e.g., 02:00)
```

For data that must be retained longer than the hot retention window but doesn't need fast query access, export to a cold archive (flat files, a separate archive database, or cloud object storage) before purge runs, using a scheduled script with `system.tag.queryTagHistory` or direct SQL export against the partition about to be dropped.

```python
# Example: export a partition to CSV before it's purged
data = system.tag.queryTagHistory(
    paths=["[default]Area1/Pressure"],
    startDate=exportStart,
    endDate=exportEnd,
    returnFormat="Wide"
)
system.dataset.toCSV(data)  # write result to archive location
```

---

## 5. Database-Specific Tuning

### 5.1 MySQL / MariaDB

```ini
# my.cnf key settings for an Ignition historian workload
innodb_buffer_pool_size = 8G          # 60-70% of available RAM on a dedicated DB host
innodb_log_file_size = 1G             # Larger redo log = fewer checkpoint stalls on write-heavy loads
innodb_flush_log_at_trx_commit = 2    # 2 = better throughput, ~1s durability window (acceptable for historian)
innodb_flush_method = O_DIRECT
max_connections = 200
innodb_file_per_table = 1
slow_query_log = 1
long_query_time = 1                   # log anything over 1s
```

Run `ANALYZE TABLE` on historian partitions after large backfills so the optimizer's statistics stay current:
```sql
ANALYZE TABLE sqlt_data_1_2026_07;
```

### 5.2 PostgreSQL

```conf
# postgresql.conf key settings
shared_buffers = 4GB                  # ~25% of RAM
effective_cache_size = 12GB           # ~75% of RAM, hints planner about OS cache
work_mem = 32MB                       # per-sort/hash operation; raise carefully, multiplied by concurrent ops
maintenance_work_mem = 512MB
wal_buffers = 16MB
checkpoint_completion_target = 0.9
max_connections = 150
autovacuum = on
autovacuum_vacuum_scale_factor = 0.05 # more aggressive than default on high-churn historian tables
```

PostgreSQL relies on autovacuum to reclaim dead tuples from UPDATE/DELETE-heavy tables (e.g., transaction group tables with upserts). Monitor bloat:
```sql
SELECT relname, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / NULLIF(n_live_tup,0) * 100, 1) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_pct DESC;
```

### 5.3 SQL Server

```sql
-- Instance-level: set max server memory to leave headroom for OS
EXEC sp_configure 'max server memory (MB)', 12288;
RECONFIGURE;

-- Enable read committed snapshot isolation to reduce reader/writer blocking
ALTER DATABASE IgnitionHistorian SET READ_COMMITTED_SNAPSHOT ON;

-- Rebuild fragmented indexes on historian tables (schedule via SQL Agent, off-peak)
ALTER INDEX ALL ON sqlt_data_1_2026_07 REBUILD WITH (ONLINE = ON);
```

`READ_COMMITTED_SNAPSHOT` is particularly valuable in Ignition deployments where dashboards (readers) run concurrently with historian writers — it eliminates most reader/writer blocking by using row versioning instead of shared locks.

### 5.4 Oracle

```sql
-- Gather stats after large loads
EXEC DBMS_STATS.GATHER_TABLE_STATS(ownname => 'IGN_HIST', tabname => 'SQLT_DATA_1_2026_07', cascade => TRUE);

-- Check for excessive parsing (indicates non-parameterized queries)
SELECT sql_text, executions, parse_calls
FROM v$sql
WHERE parse_calls > executions * 2
ORDER BY parse_calls DESC
FETCH FIRST 20 ROWS ONLY;
```

Use partitioned tables (`INTERVAL` partitioning) for historian data so Oracle auto-creates monthly partitions and the optimizer can prune irrelevant partitions on time-range queries.

---

## 6. Monitoring Database Performance

### 6.1 Slow Query Logging

| Database | Enable | Threshold Config |
|---|---|---|
| MySQL | `slow_query_log = 1` | `long_query_time = 1` (seconds) |
| PostgreSQL | `log_min_duration_statement = 1000` (ms) | Logs any statement over 1000ms |
| SQL Server | Extended Events session on `sql_statement_completed` | Filter `duration > 1000000` (microseconds) |
| Oracle | AWR / `v$sql` with `elapsed_time` | Query `v$sql` ordered by `elapsed_time` |

### 6.2 Key Metrics to Track

| Metric | Healthy Range | Where to Check |
|---|---|---|
| Connection pool active/max ratio | < 80% sustained | Gateway > Status > Databases |
| Query timeout rate | Near zero | Gateway logs, `system.db` errors |
| Historian write latency | < scan class interval | Gateway diagnostics, DB slow log |
| DB CPU utilization | < 70% sustained | OS/DB monitoring (Prometheus exporters, native DB dashboards) |
| Disk I/O wait | Low, no sustained queue | `iostat`, DB-native wait stats |
| Replication lag (if applicable) | < a few seconds | See `91-DATABASE-FAILOVER-REPLICATION.md` |

### 6.3 Gateway-Side Monitoring

Gateway > Status > Databases shows per-connection active/idle counts and recent errors. Combine with Gateway logs filtered on the `datasource` logger, and export Gateway metrics (via the Gateway's built-in metrics or a Prometheus/Grafana integration if using the Enterprise Administration Module) to correlate DB latency spikes with dashboard slowness reports.

```sql
-- Generic: top 10 longest-running current queries (PostgreSQL example)
SELECT pid, now() - query_start AS duration, state, query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;
```

---

## 7. Backup Strategies

### 7.1 Backup Types

| Type | Description | Recovery Point | Use With |
|---|---|---|---|
| **Full backup** | Complete copy of the database | To backup time | Weekly baseline, all engines |
| **Incremental** | Changes since last backup (full or incremental) | To last increment | Daily, reduces backup window |
| **Differential** | Changes since last full backup | To last differential | Nightly, simpler restore chain than incremental |
| **Point-in-time recovery (PITR)** | Full backup + continuous transaction log/WAL archiving | To any point (seconds granularity) | Production historian and transactional DBs where data loss must be minimized |

### 7.2 Engine-Specific PITR Setup

**MySQL:** Enable binary logging, take periodic full backups (`mysqldump` or `mysqlbackup`/`xtrabackup` for large DBs), retain binlogs, and replay them from the last full backup to the desired point.
```ini
log_bin = /var/log/mysql/mysql-bin
binlog_expire_logs_seconds = 604800   # 7 days retention
```

**PostgreSQL:** Use WAL archiving with `pg_basebackup` for the base and continuous WAL shipping for PITR.
```conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/wal/%f'
```

**SQL Server:** Set recovery model to FULL, schedule regular transaction log backups between full/differential backups.
```sql
ALTER DATABASE IgnitionHistorian SET RECOVERY FULL;
BACKUP DATABASE IgnitionHistorian TO DISK = 'D:\Backups\Full.bak';
BACKUP LOG IgnitionHistorian TO DISK = 'D:\Backups\Log.trn';
```

**Oracle:** Use RMAN with archivelog mode enabled.
```sql
RMAN> BACKUP DATABASE PLUS ARCHIVELOG;
```

### 7.3 Ignition-Specific Backup Considerations

- Back up the **Ignition Gateway** (project files, tag configs, `.gwbk`) on a separate schedule from the database — they are independently restorable but must be kept compatible (a gateway restore pointing at a stale DB schema can break historian bindings).
- Test restores regularly, into an isolated environment, and confirm Ignition can reconnect and query historian data against the restored copy.
- For historian databases specifically, prioritize PITR since gaps in trend data are often noticed by operators immediately and are hard to backfill after the fact.

---

## 8. Storage Capacity Planning

### 8.1 Estimating Historian Growth

```
Daily rows per tag ≈ (86400 / logging_interval_seconds) × (1 - deadband_suppression_rate)
Daily storage ≈ Σ(tags) [daily rows × row_size_bytes] + index overhead (typically 30-50% of data size)
```

**Worked example:**
- 2,000 analog tags, average logging interval 10s with deadband suppressing ~80% of samples
- Effective rows/tag/day ≈ (86400/10) × 0.20 ≈ 1,728
- Total rows/day ≈ 2,000 × 1,728 ≈ 3.46M rows
- At ~40 bytes/row (value + timestamp + tagid overhead) ≈ 138 MB/day raw, ~190-210 MB/day including indexes
- Over a 13-month hot retention window ≈ 75-85 GB

### 8.2 Planning Table

| Factor | Impact on Storage |
|---|---|
| Logging interval | Inverse — halving interval roughly doubles volume |
| Deadband tuning | Largest lever; well-tuned deadbands can cut volume 10-100x |
| Retention window | Linear — directly multiplies total footprint |
| Number of tags | Linear |
| Index count | Adds 30-50% overhead per additional index on hot tables |
| Compression (DB-native, e.g., InnoDB page compression, PostgreSQL TOAST, SQL Server PAGE compression) | Can reduce storage 30-60% with modest CPU cost |

### 8.3 Recommendations

- Size storage for **18-24 months** of projected growth, not current volume — tag counts grow as projects expand.
- Separate historian storage (fast, moderate-durability disks acceptable given PITR/replication) from transactional/config storage (needs highest durability).
- Revisit deadband tuning and retention policy every 6-12 months as part of a capacity review — it's cheaper than buying storage.
- Monitor actual vs. projected growth monthly; a sudden jump usually indicates a deadband regression (e.g., a tag replaced without carrying over its deadband setting) rather than genuine new load.

```sql
-- Monthly storage trend (MySQL, using information_schema)
SELECT table_name,
       ROUND(data_length / 1024 / 1024, 1) AS data_mb,
       ROUND(index_length / 1024 / 1024, 1) AS index_mb
FROM information_schema.tables
WHERE table_schema = 'ignition_historian'
  AND table_name LIKE 'sqlt_data_1_%'
ORDER BY table_name DESC
LIMIT 12;
```

---

## Related Documentation
- `23-DATABASE-INTEGRATION.md` — Connection setup, Named Queries, prepared statements
- `26-PLATFORM-DATABASE-HISTORIAN.md` — Historian architecture and basic configuration
- `91-DATABASE-FAILOVER-REPLICATION.md` — Redundancy, replication, and disaster recovery
- `83-PERFORMANCE-TUNING.md` — Gateway-wide performance tuning

---

## See Also

**Prerequisites:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md)

**Builds toward:** [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
