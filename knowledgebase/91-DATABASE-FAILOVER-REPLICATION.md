> **Skill level:** 300 · **Read first:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 91-DATABASE-FAILOVER-REPLICATION

# Ignition 8.3 Database Advanced: Failover & Replication

## Overview
Guide for building database redundancy behind Ignition 8.3 gateways: replication architectures, failover automation, read replicas for scaling, disaster recovery for historian data, consistency verification, and troubleshooting. This is distinct from **Gateway Redundancy** (primary/backup Ignition gateways) — this document covers redundancy of the **database tier** those gateways connect to. A fully resilient deployment typically layers both.

---

## 1. Database Redundancy Architectures

### 1.1 Why the Database Tier Needs Its Own Redundancy

Ignition Gateway Redundancy protects the Ignition application layer (tag engine, scripting, clients), but if both the primary and backup gateway point at a **single** database instance, a database outage still takes down historian logging, transaction groups, and any Named Query-backed screens for both gateways. Database redundancy is a separate, complementary layer.

### 1.2 Common Architectures

| Architecture | Description | Failover Time | Complexity |
|---|---|---|---|
| **Single instance + backups** | One DB, regular backups, no live standby | Hours (restore time) | Low |
| **Master-slave (async replica)** | One writable primary, one or more read-only replicas kept in sync asynchronously | Minutes (manual or scripted promotion) | Medium |
| **Master-slave (sync replica)** | Primary waits for replica ack before commit confirms | Seconds, minimal data loss | Medium-High (latency cost) |
| **Multi-master / clustered (Galera, Always On Availability Groups, Oracle RAC)** | Multiple writable nodes with built-in consensus | Seconds, often automatic | High |
| **Two independent DBs + gateway-side dual-write** | Each gateway (primary/backup Ignition) writes to its own local DB | N/A (no single point of failure) but requires reconciliation | High operational overhead |

**Recommended baseline for most Ignition sites:** Master-slave replication (async for historian data where a few seconds of lag is acceptable; sync for transactional data like recipe/genealogy records where every write matters) with a documented, tested manual or semi-automated promotion procedure. Full multi-master clustering is justified mainly for large, multi-site enterprise deployments with strict RTO/RPO requirements.

### 1.3 Placement Relative to Ignition Gateway Redundancy

```
                 ┌───────────────┐        ┌───────────────┐
                 │  Primary GW   │        │  Backup GW    │
                 └───────┬───────┘        └───────┬───────┘
                         │                          │
                         ▼                          ▼
                 ┌───────────────────────────────────────┐
                 │     DB Connection String (VIP/DNS)     │
                 └───────────────┬─────────────────────────┘
                                 ▼
                       ┌───────────────┐   replication   ┌───────────────┐
                       │  DB Primary    │ ───────────────▶│  DB Replica   │
                       └───────────────┘                  └───────────────┘
```

Point both Ignition gateways at a **virtual IP (VIP)** or DNS name that resolves to the current database primary, rather than hardcoding the primary's IP in each gateway's connection config. This lets failover tooling repoint the VIP/DNS without touching Ignition configuration on every failover event.

---

## 2. Master-Slave Replication Setup

### 2.1 MySQL / MariaDB (GTID-based, recommended over legacy binlog position)

**On the primary:**
```ini
[mysqld]
server_id = 1
log_bin = mysql-bin
gtid_mode = ON
enforce_gtid_consistency = ON
binlog_format = ROW
```

```sql
CREATE USER 'repl_user'@'%' IDENTIFIED BY 'strong_password';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;
```

**On the replica:**
```ini
[mysqld]
server_id = 2
gtid_mode = ON
enforce_gtid_consistency = ON
read_only = ON
super_read_only = ON
```

```sql
CHANGE MASTER TO
  MASTER_HOST = 'db-primary.internal',
  MASTER_USER = 'repl_user',
  MASTER_PASSWORD = 'strong_password',
  MASTER_AUTO_POSITION = 1;
START SLAVE;
SHOW SLAVE STATUS\G
```
Confirm `Slave_IO_Running: Yes` and `Slave_SQL_Running: Yes`, and watch `Seconds_Behind_Master`.

### 2.2 PostgreSQL (Streaming Replication)

**On the primary (`postgresql.conf`):**
```conf
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB
hot_standby = on
```

`pg_hba.conf`:
```
host  replication  repl_user  10.0.0.0/24  scram-sha-256
```

**On the replica** — take a base backup, then configure standby mode:
```bash
pg_basebackup -h db-primary.internal -D /var/lib/postgresql/data -U repl_user -P -R
```
`-R` writes a `standby.signal` file and populates `primary_conninfo` automatically (PostgreSQL 12+). Start the replica; it will begin streaming WAL.

Check replication status from the primary:
```sql
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
       (pg_current_wal_lsn() - replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

### 2.3 SQL Server (Always On Availability Groups — preferred over legacy log shipping for automatic failover)

```sql
-- Enable Always On (requires Windows Failover Clustering or SQL Server 2022 Windows Server Failover Cluster-less)
ALTER SERVER CONFIGURATION SET SOFTNAT ON; -- or enable via SQL Server Configuration Manager

CREATE AVAILABILITY GROUP IgnitionAG
FOR DATABASE IgnitionHistorian
REPLICA ON
  'SQLNODE1' WITH (ENDPOINT_URL = 'TCP://sqlnode1:5022', AVAILABILITY_MODE = SYNCHRONOUS_COMMIT, FAILOVER_MODE = AUTOMATIC),
  'SQLNODE2' WITH (ENDPOINT_URL = 'TCP://sqlnode2:5022', AVAILABILITY_MODE = SYNCHRONOUS_COMMIT, FAILOVER_MODE = AUTOMATIC);
```

Point the Ignition JDBC connection string at the **Availability Group Listener** name, not an individual node, so failover is transparent to the gateway:
```
jdbc:sqlserver://IgnitionAGListener:1433;databaseName=IgnitionHistorian;
```

### 2.4 Oracle (Data Guard)

```sql
-- On primary, enable force logging and configure a standby redo log
ALTER DATABASE FORCE LOGGING;
ALTER SYSTEM SET LOG_ARCHIVE_DEST_2 = 'SERVICE=standby_db ASYNC VALID_FOR=(ONLINE_LOGFILES,PRIMARY_ROLE) DB_UNIQUE_NAME=standby_db';
ALTER SYSTEM SET LOG_ARCHIVE_DEST_STATE_2 = ENABLE;
```
Data Guard supports both physical standby (byte-for-byte, fastest failover) and logical standby (SQL-apply, allows some divergence). For Ignition historian workloads, physical standby with Fast-Start Failover (FSFO) via Data Guard Broker gives the closest experience to automatic failover.

---

## 3. Failover Automation

### 3.1 Detection

Automated failover requires reliable primary-down detection to avoid **split-brain** (two nodes both believing they're primary and accepting writes — this corrupts data).

| Mechanism | Description |
|---|---|
| **Heartbeat/health check agent** | External tool (Orchestrator for MySQL, Patroni for PostgreSQL, cluster quorum for SQL Server/Oracle) polls the primary; declares failure after N consecutive missed checks |
| **Quorum-based consensus** | Requires majority agreement among 3+ nodes before promoting a replica — prevents a single monitor's false positive from triggering failover |
| **Fencing (STONITH)** | "Shoot the other node in the head" — forcibly powers off/isolates the old primary before promoting a replica, guaranteeing no split-brain |

**Never rely on a single unattended monitor with no quorum for automatic promotion in production** — a network blip that isolates the monitor from the primary (but not from clients) can trigger an unnecessary, disruptive failover.

### 3.2 Switchover (Planned) vs Failover (Unplanned)

- **Switchover:** Controlled, no data loss — drain writes, confirm replica fully caught up (`Seconds_Behind_Master = 0` / `lag_bytes = 0`), then promote. Use for planned maintenance.
- **Failover:** Primary is unreachable — promote the most caught-up replica, accepting some possible data loss for async replication (RPO > 0), or zero loss for sync replication (RPO = 0 but with a latency cost on every write).

### 3.3 Common Automation Tools

| Database | Tool | Notes |
|---|---|---|
| MySQL | Orchestrator, MHA, ProxySQL | Orchestrator handles topology detection + automated promotion; ProxySQL/HAProxy handles connection routing |
| PostgreSQL | Patroni + etcd/Consul, repmgr | Patroni is the most widely adopted; integrates with a DCS (distributed config store) for quorum |
| SQL Server | Always On AG with WSFC | Built-in automatic failover when `FAILOVER_MODE = AUTOMATIC` and quorum is healthy |
| Oracle | Data Guard Broker + Fast-Start Failover, Oracle RAC | FSFO handles automated failover with an Observer process for quorum |

### 3.4 Ignition-Side Reconnection Behavior

After failover, Ignition's connection pool needs to notice the primary is gone and re-establish connections to the new primary. Key configuration to make this fast:

```
Test On Borrow:            true    (rejects dead connections immediately on next query)
Validation Query:          SELECT 1
Connection Age Limit:      Set low enough (e.g., 5-10 min) during failover testing windows,
                            normal production can use longer (hours)
Query Timeout:              Set low enough that a hung connection to a dead primary
                            fails fast rather than hanging client-facing screens (10-30s)
```

If using a VIP/DNS-based routing approach (recommended), ensure the VIP/DNS TTL and gateway's DNS caching won't delay reconnection — Java's JDBC drivers and the JVM can cache DNS resolutions longer than the OS; consider `networkaddress.cache.ttl` JVM setting on the Gateway if using DNS-based failover with short TTLs.

---

## 4. Read Replicas for Scaling

Not every replica needs to be a failover target — read replicas can offload reporting and dashboard query load from the primary.

### 4.1 Pattern

- Point heavy historian **read** queries (long-range trend reports, nightly rollup reports) at a dedicated read-only Ignition database connection configured against a replica.
- Keep **write** paths (transaction groups, historian ingestion, Named Query INSERT/UPDATE) exclusively on the primary connection.
- In Ignition, this means creating **two database connections** in Gateway config — e.g., `ProdDB_Write` (primary) and `ProdDB_Read` (replica) — and directing Named Queries/bindings accordingly. There is no automatic read/write splitting built into Ignition; it must be done at the project/query level.

```python
# Explicit read-replica routing example in a script
report_data = system.db.runQuery(
    "SELECT * FROM sqlt_data_1_2026_07 WHERE tagid = ? AND t_stamp BETWEEN ? AND ?",
    [tagId, startMs, endMs],
    database="ProdDB_Read"
)
```

### 4.2 Caveats

- Replicas (async) lag the primary — a read immediately after a write may not see that write (**read-your-writes** inconsistency). For screens where a user just submitted data and expects to see it reflected immediately, read from the primary, not the replica.
- Monitor replica lag continuously (see Section 8) — a replica falling far behind defeats the purpose and can serve stale data silently.

---

## 5. Disaster Recovery for Historians

### 5.1 RPO/RTO Targets

Define these explicitly per data class before choosing an architecture:

| Data Class | Typical RPO | Typical RTO | Approach |
|---|---|---|---|
| Real-time process historian | Seconds - minutes | Minutes | Sync or near-sync replica, fast automated failover |
| Production/genealogy transactional records | Zero (no loss tolerated) | Minutes | Synchronous replication |
| Long-term archive/compliance data | Hours (backup-based) | Hours - days | Nightly backups + offsite/cloud copy sufficient |

### 5.2 Multi-Site DR

For sites requiring geographic disaster recovery (entire site loss), replicate to a remote DR site asynchronously (sync replication across WAN distances usually adds unacceptable write latency). On DR activation:

1. Promote the DR replica to primary.
2. Repoint the DR-site Ignition gateway(s) (or restore/redeploy gateway backups) at the newly-promoted DR database.
3. Validate historian continuity — check for gaps at the failover boundary (see Section 6).
4. Once the original site recovers, re-establish it as a new replica (do **not** simply bring it back as primary — it is now stale and would conflict/split-brain if it starts accepting writes).

### 5.3 Historian-Specific DR Considerations

- Historian partition tables are created dynamically (monthly by default) — confirm the DR replica's Ignition historian configuration matches (same partition size, same purge/retention settings) so partition creation stays in sync after promotion.
- If using async replication, the DR site may be missing the most recent seconds/minutes of historian data at failover time — this shows as a small trend gap. Document this expected gap so operators don't mistake it for a tag communication fault.

---

## 6. Data Consistency Verification

### 6.1 Row Count and Checksum Comparison

Periodically verify replica data matches the primary, not just that replication is "running."

**MySQL — `pt-table-checksum` (Percona Toolkit):**
```bash
pt-table-checksum --replicate=percona.checksums h=db-primary.internal
pt-table-sync --replicate=percona.checksums --print h=db-primary.internal
```

**PostgreSQL — manual checksum comparison:**
```sql
-- Run on both primary and replica, compare results
SELECT count(*), sum(hashtext(t_stamp::text || floatvalue::text))
FROM sqlt_data_1_2026_07
WHERE tagid = 4821;
```

**SQL Server — `DBCC CHECKSUM` or Always On's built-in data consistency via `DBCC CHECKDB` run independently on each replica:**
```sql
DBCC CHECKDB('IgnitionHistorian') WITH NO_INFOMSGS;
```

### 6.2 Application-Level Sanity Checks

Beyond raw checksums, verify from an Ignition perspective:
```python
# Compare row counts for a recent window between primary and replica connections
primaryCount = system.db.runScalarQuery(
    "SELECT COUNT(*) FROM sqlt_data_1_2026_07 WHERE t_stamp > ?", [recentMs], database="ProdDB_Write")
replicaCount = system.db.runScalarQuery(
    "SELECT COUNT(*) FROM sqlt_data_1_2026_07 WHERE t_stamp > ?", [recentMs], database="ProdDB_Read")

if abs(primaryCount - replicaCount) > tolerance:
    system.util.getLogger("ReplicationCheck").warn(
        "Replica drift detected: primary=%d replica=%d" % (primaryCount, replicaCount))
```

Schedule this as a Gateway timer script running every few minutes, alerting via the alarm system on sustained drift.

---

## 7. Synchronization Monitoring

### 7.1 Lag Metrics by Engine

| Database | Metric | Query |
|---|---|---|
| MySQL | `Seconds_Behind_Master` | `SHOW SLAVE STATUS\G` |
| PostgreSQL | `replay_lag` / byte lag | `SELECT * FROM pg_stat_replication;` |
| SQL Server | `redo_queue_size`, `log_send_queue_size` | `SELECT * FROM sys.dm_hadr_database_replica_states;` |
| Oracle | Apply lag | `SELECT NAME, VALUE FROM V$DATAGUARD_STATS WHERE NAME = 'apply lag';` |

### 7.2 Alerting Thresholds

| Lag | Severity | Action |
|---|---|---|
| < 5s | Normal | None |
| 5-30s | Warning | Watch trend; check primary write load |
| 30s - 5min | High | Investigate immediately — possible replica resource contention or network issue |
| > 5min | Critical | Treat replica as unreliable for failover/reads until resolved; page on-call |

Wire these thresholds into Ignition's alarm system by polling replication status via a scheduled script and writing the lag value to a memory tag with configured alarm levels — this surfaces DB replication health in the same alarm pipeline operators already monitor.

```python
lag = system.db.runScalarQuery("SHOW SLAVE STATUS", database="ProdDB_Read")  # parse Seconds_Behind_Master
system.tag.writeBlocking(["[default]System/ReplicationLagSeconds"], [lag])
```

---

## 8. Troubleshooting Replication Lag

### 8.1 Common Causes and Fixes

| Cause | Symptom | Fix |
|---|---|---|
| Single-threaded replication apply (older MySQL default) | Lag grows under high write concurrency on primary | Enable multi-threaded replication (`slave_parallel_workers`, `slave_parallel_type = LOGICAL_CLOCK`) |
| Replica hardware weaker than primary | Lag correlates with primary write bursts | Match replica specs to primary, especially disk I/O |
| Large unindexed queries competing with replication apply on the replica | Lag spikes during report runs | Move reporting queries to a dedicated third replica, or throttle report scheduling |
| Network latency/bandwidth between sites (WAN replication) | Sustained baseline lag, not bursty | Compress replication traffic where supported; consider a closer DR site or async batching |
| Long-running transactions on the replica blocking apply (PostgreSQL, `hot_standby_feedback`) | Apply stalls while a report query runs | Set `max_standby_streaming_delay` appropriately; consider a separate reporting replica |
| Disk I/O saturation on replica | Lag grows during nightly batch jobs | Stagger backup/maintenance jobs away from peak write periods; upgrade storage (SSD/NVMe) |

### 8.2 Diagnostic Workflow

1. Confirm replication process is actually running (`SHOW SLAVE STATUS`, `pg_stat_replication`, AG dashboard, Data Guard Broker `show configuration`).
2. Check primary write volume — is lag correlated with write bursts (capacity issue) or constant (network/config issue)?
3. Check replica resource utilization (CPU, disk I/O, memory) during lag periods.
4. Check for long-running queries on the replica blocking apply threads.
5. Check network latency/throughput between primary and replica (`ping`, `iperf3`) if lag is WAN-related.

---

## 9. Testing Failover Scenarios

Untested failover is not a DR plan — schedule regular failover drills, at minimum quarterly.

### 9.1 Test Plan Template

| Step | Action | Expected Result |
|---|---|---|
| 1 | Record current replica lag, confirm near-zero | Baseline healthy state |
| 2 | Simulate primary failure (stop DB service, or block network to primary in a controlled test window) | Monitor/quorum tool detects failure within expected time |
| 3 | Confirm automated (or execute manual) promotion of replica | Replica becomes writable primary |
| 4 | Confirm VIP/DNS/listener repoints to new primary | Client connections route to new primary without manual gateway reconfiguration |
| 5 | Verify Ignition gateway reconnects and resumes historian writes | No sustained "Unable to get connection" errors past the expected reconnection window |
| 6 | Check for data gaps in historian trend around the failover timestamp | Gap should match expected RPO for the chosen replication mode (near-zero for sync, small for async) |
| 7 | Verify alarms fired appropriately for the DB outage and recovery | Confirms monitoring/alerting pipeline works end-to-end |
| 8 | Fail back / re-establish original primary as new replica | Original primary correctly rejoins as replica, no split-brain |

### 9.2 What to Measure

- **Actual detection time** vs configured thresholds.
- **Actual promotion time** (automated tools should log this).
- **Ignition reconnection time** — how long until dashboards/historian resume normal operation after DB-side failover completes. This is often the longest leg if `Test On Borrow`/pool settings aren't tuned (see Section 3.4).
- **Data loss window** — compare historian data before/after the test against what was actually written, to validate real-world RPO matches the design target.

### 9.3 Common Failure Modes Found in Testing

- Gateway connection pool configured with a long `Connection Age Limit` doesn't notice the primary is gone until existing connections are exhausted or explicitly invalidated — validated via `Test On Borrow`, but only at next query attempt.
- DNS/VIP TTL longer than expected, combined with JVM DNS caching, delays reconnection well past the DB-side promotion time.
- Named Queries or scripts hardcoding a specific database connection name that wasn't updated when a new read replica connection was added, silently reading stale data.
- Firewall rules scoped to the original primary's IP rather than the VIP, blocking the gateway from reaching the newly promoted primary.

---

## Related Documentation
- `90-DATABASE-ADVANCED-OPTIMIZATION.md` — Query optimization, pooling, historian tuning, backups
- `23-DATABASE-INTEGRATION.md` — Base connection configuration
- `26-PLATFORM-DATABASE-HISTORIAN.md` — Historian architecture fundamentals
- `61-GATEWAY-MANAGEMENT.md` — Ignition Gateway (application-layer) redundancy configuration

---

## See Also

**Prerequisites:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)

**Builds toward:** [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md)

**Related:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
