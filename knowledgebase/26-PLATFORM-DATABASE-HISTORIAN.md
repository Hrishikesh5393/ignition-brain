> **Skill level:** 200 · **Read first:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 26-PLATFORM-DATABASE-HISTORIAN

# Ignition 8.3 Platform: Database & Historian

## Overview
Comprehensive guide for database connections, historical data logging, retention policies, and performance optimization in Ignition 8.3.

---

## 1. Database Connections

### 1.1 Connection Types

| Type | Driver | Use Case | Notes |
|------|--------|----------|-------|
| **MySQL** | Connector/J | Local/network database | Most common in Ignition deployments |
| **Microsoft SQL Server** | SQL Server JDBC | Enterprise Windows environments | Excellent clustering support |
| **PostgreSQL** | PostgreSQL JDBC | Cross-platform open-source | Growing adoption, excellent performance |
| **Oracle Database** | Oracle JDBC | Enterprise legacy systems | Requires specific driver versions |
| **SQLite** | SQLite JDBC | Testing, small embedded systems | Not recommended for production historian |
| **H2 Database** | H2 JDBC | Development, lightweight | Built-in Ignition database option |

### 1.2 Connection Configuration

**Location:** Gateway Configuration > Database > Connections

**Essential Configuration Parameters:**

```
Connection Name:        [User-defined identifier]
Database Type:          [MySQL, MSSQL, PostgreSQL, Oracle, etc.]
Host:                   [IP/Hostname]
Port:                   [Default: DB-specific - MySQL:3306, MSSQL:1433, PG:5432]
Username:               [Database user]
Password:               [Encrypted on gateway]
Database Name:          [Schema/database name]
Max Pool Size:          [10-100, depends on usage]
Min Pool Size:          [2-5]
Connection Timeout:     [30-60 seconds]
Auto Commit:            [true/false - typically false for transactions]
Validation Query:       [SELECT 1 - ensures connection health]
Max Wait Time:          [60-120 seconds before timeout]
Test on Borrow:         [true - validates connection before use]
```

### 1.3 Connection Pooling

**Connection Pool Strategy:**
- **Min Pool Size:** Minimum idle connections maintained (2-5 typical)
- **Max Pool Size:** Maximum connections allowed (10-100 depending on load)
- **Connection Reuse:** Connections returned to pool after use
- **Idle Timeout:** Connections closed after inactivity
- **Test on Borrow:** Validates connection health before returning to application

**Pool Configuration Example:**

```
Min Pool Size:     5
Max Pool Size:     50
Idle Timeout:      15 minutes
Max Wait Time:     60 seconds
Test on Borrow:    Enabled
Validation Query:  SELECT 1
```

**Performance Tuning:**
- Monitor connection usage via Gateway Console > Diagnostics > Database
- Increase Max Pool Size if connections are exhausted
- Reduce Min Pool Size if memory is constrained
- Enable "Test on Borrow" to catch stale connections

### 1.4 Named Queries & Database Scripting

**Named Query Scope Options:**
```
- Gateway         (shared, affects all clients)
- Project         (project-specific)
- Personal        (designer workspace only)
```

**Best Practices:**
- Use named queries for repeated database access
- Implement parameterized queries to prevent SQL injection
- Use transactions for multi-step database operations
- Monitor query execution time via Gateway logs

---

## 2. Historical Data Logging (Historian Module)

### 2.1 Historian Architecture

**Core Components:**

| Component | Purpose |
|-----------|---------|
| **Tag History Provider** | Logs tag value changes to database |
| **Historian Database** | Dedicated database for historical data |
| **Tag History Binding** | Visual component for retrieving historical data |
| **Historical Query Scripts** | System functions for data access |

**Data Storage Strategy:**
- **Block Compression:** Reduced storage for unchanged values
- **Scan Classes:** Polling intervals (e.g., "Rapid", "Normal", "Slow") determine logging frequency
- **On-Change Logging:** Records only when value changes
- **Periodic Logging:** Records at fixed intervals regardless of change

### 2.2 Enabling Tag History

**Configuration Steps:**

1. **Create Historian Database Connection**
   - Gateway > Configuration > Databases > Create connection
   - Dedicated DB recommended (separate from OPC data)
   - Must support concurrent writes

2. **Configure Tag History Provider**
   - Gateway > Configuration > Tags > Historian
   - Select database connection
   - Configure log tables (optional)

3. **Enable on Tags**
   ```
   Tag Properties:
   - History Enabled:    true
   - History Scan Class: [Rapid/Normal/Slow/Custom]
   - History Deadband:   [0-100%] - minimum change to trigger logging
   - History Deadband Mode: [Percent/Absolute/Raw]
   ```

**Scan Class Intervals:**
| Scan Class | Default Interval | Use Case |
|-----------|------------------|----------|
| Rapid | 1 second | Critical process values |
| Normal | 1 minute | Standard PLC/sensor data |
| Slow | 1 hour | Long-term trends, less critical |
| Custom | User-defined | Specific requirements |

### 2.3 Historian Data Structure

**Default Table Schema:**

```sql
-- Tag history table
CREATE TABLE taghistory (
    ts BIGINT,              -- Timestamp (milliseconds since epoch)
    tagid INT,              -- Reference to tag
    intvalue INT,           -- Integer value
    floatvalue DOUBLE,      -- Float value
    stringvalue VARCHAR,    -- String value
    dataintegrity INT,      -- Data quality flag
    datatype INT            -- Value type indicator
);

-- Tag ID lookup
CREATE TABLE tagids (
    tagid INT PRIMARY KEY,
    tagpath VARCHAR,        -- Full tag path
    datasource VARCHAR      -- OPC server or source
);
```

**Data Integrity Flags:**
```
0 = Good (Quality.Good)
1 = Uncertain
2 = Bad (Quality.Bad)
3 = Disabled/Not Connected
```

---

## 3. Data Retention Policies

### 3.1 Retention Configuration

**Archival Strategy Options:**

| Strategy | Implementation | Best For |
|----------|-----------------|----------|
| **Automatic Pruning** | Database triggers/events | Simple retention requirements |
| **Partitioned Tables** | Monthly/yearly partitions | Large datasets (>1M rows/day) |
| **Archival Database** | Offload to separate DB | Long-term compliance/analytics |
| **Compression** | Block compression | Reducing active DB size |

### 3.2 Implementing Retention Policies

**Option 1: Gateway Script (Nightly Maintenance)**

```python
# Remove data older than 90 days
import system
from java.util import Calendar

# Calculate cutoff time
cal = Calendar.getInstance()
cal.add(Calendar.DAY_OF_MONTH, -90)
cutoff = cal.getTimeInMillis()

# Delete old records
query = """
DELETE FROM taghistory 
WHERE ts < ?
"""

system.db.runUpdateQuery(
    "HistorianDB",  # Connection name
    query,
    [cutoff]
)

system.tag.write("[System]Events/Retention/LastRun", system.date.now())
```

**Option 2: Database Maintenance Job (SQL Server)**

```sql
-- SQL Server job - daily at 2 AM
DELETE FROM taghistory 
WHERE ts < DATEADD(DAY, -90, GETDATE())

-- Rebuild indexes
DBCC DBREINDEX (taghistory)

-- Update statistics
ANALYZE TABLE taghistory
```

**Retention Periods by Data Type:**

| Data Type | Recommended Retention | Reason |
|-----------|----------------------|--------|
| Real-time OPC | 7-30 days | High frequency, voluminous |
| Alarm events | 1-2 years | Compliance, auditing |
| Batch/SPC data | 5+ years | Regulatory, quality records |
| System diagnostics | 90 days | Troubleshooting recent issues |
| Audit trail | Permanent | Regulatory requirement |

### 3.3 Partitioning Strategy for Large Datasets

**Monthly Partition Example:**

```sql
-- MySQL: Create monthly partitions
CREATE TABLE taghistory (
    ts BIGINT,
    tagid INT,
    floatvalue DOUBLE,
    -- ... other columns
)
PARTITION BY RANGE (YEAR(FROM_UNIXTIME(ts/1000)) * 100 + MONTH(FROM_UNIXTIME(ts/1000))) (
    PARTITION p202601 VALUES LESS THAN (202602),
    PARTITION p202602 VALUES LESS THAN (202603),
    PARTITION p202603 VALUES LESS THAN (202604),
    -- ... monthly partitions
);
```

---

## 4. Querying Historical Data

### 4.1 System Functions

**Primary Query Functions:**

| Function | Purpose | Return |
|----------|---------|--------|
| `system.tag.getTagHistories()` | Query multiple tags | Dataset with ts, value, quality |
| `system.tag.queryTagHistory()` | Single tag query | Ordered results |
| `system.db.runQuery()` | Direct SQL access | Raw dataset |

### 4.2 Query Examples

**Example 1: Basic Tag History Query**

```python
import system
from java.util import Date

# Query last 24 hours of tag data
startTime = Date(Date().getTime() - (24 * 60 * 60 * 1000))
endTime = Date()

dataset = system.tag.queryTagHistory(
    tagPath="[TagProvider]Building/Temperature/Setpoint",
    startDate=startTime,
    endDate=endTime,
    returnSize=0,  # 0 = all results
    aggregationMode="Average",
    aggregationInterval=300000,  # 5 minute intervals
    includeNullValues=False,
    noInterpolation=False
)

# Return column names
columnNames = list(dataset.getColumnNames())
for row in dataset:
    print("Time: %s, Value: %s" % (row['t_stamp'], row['v_double']))
```

**Example 2: Multiple Tag History with SQL**

```python
query = """
SELECT 
    t1.ts as timestamp,
    t1.floatvalue as temperature,
    t2.floatvalue as humidity,
    t3.floatvalue as pressure
FROM taghistory t1
LEFT JOIN taghistory t2 ON t1.ts = t2.ts AND t2.tagid = ?
LEFT JOIN taghistory t3 ON t1.ts = t3.ts AND t3.tagid = ?
WHERE t1.tagid = ?
  AND t1.ts >= ?
  AND t1.ts < ?
ORDER BY t1.ts DESC
"""

dataset = system.db.runQuery(
    "HistorianDB",
    query,
    [tagid_humidity, tagid_pressure, tagid_temperature, startMs, endMs]
)
```

**Example 3: Aggregated Data Query**

```python
# Monthly average calculation
query = """
SELECT 
    DATE_TRUNC('month', FROM_UNIXTIME(ts/1000)) as month,
    AVG(floatvalue) as avg_value,
    MIN(floatvalue) as min_value,
    MAX(floatvalue) as max_value,
    COUNT(*) as sample_count
FROM taghistory
WHERE tagid = ?
  AND ts >= ?
  AND ts < ?
GROUP BY DATE_TRUNC('month', FROM_UNIXTIME(ts/1000))
ORDER BY month DESC
"""

dataset = system.db.runQuery(
    "HistorianDB",
    query,
    [tagid, startMs, endMs]
)
```

### 4.3 Aggregation Modes

| Mode | Description | Typical Use |
|------|-------------|-------------|
| **None** | Raw data points | Real-time charting |
| **Average** | Mean over interval | Trend analysis |
| **MinMax** | Min/Max per interval | Range visualization |
| **LastValue** | Final value in interval | Step data, counters |
| **Count** | Number of samples | Frequency analysis |
| **Stddev** | Standard deviation | Variability trending |

### 4.4 Binding Historical Data to Charts

**Easy Chart Historian Data:**

```
Mode: Historical
Pen 1 -> Tag: [TagProvider]Building/Temperature
         Start Time: [SystemTags]Session/SwapStartTime
         End Time: [SystemTags]Session/SwapEndTime
         Resolution: 60000 (1 minute)
         Aggregation Mode: Average
```

---

## 5. Database Backup & Recovery

### 5.1 Backup Strategy

**Three-Tier Backup Approach:**

1. **Historian Database Backups**
   ```
   Frequency: Daily (off-peak hours)
   Retention: 30 days
   Location: Network storage, cloud backup
   Type: Full backup + differential/incremental
   ```

2. **Tag Configuration Backups**
   ```
   Frequency: After any tag/historian changes
   Retention: 1 year
   Method: Export tag XML from Designer
   Location: Version control (Git)
   ```

3. **Gateway Backup**
   ```
   Frequency: Weekly
   Retention: 90 days
   Method: Gateway restore point or VM snapshot
   Location: Redundant storage
   ```

### 5.2 MySQL Backup Example

```bash
# Full backup - daily at 1 AM
mysqldump \
  -h database.server \
  -u historian_user \
  -p \
  --single-transaction \
  --routines \
  --triggers \
  historian_db > /backups/historian_$(date +%Y%m%d).sql

# Compress for storage
gzip /backups/historian_$(date +%Y%m%d).sql

# Cleanup backups older than 30 days
find /backups -name "historian_*.sql.gz" -mtime +30 -delete
```

### 5.3 SQL Server Backup Strategy

```sql
-- Full backup - daily
BACKUP DATABASE [Ignition_Historian] 
TO DISK = 'D:\Backups\Historian_FULL_$(date).bak'
WITH COMPRESSION

-- Transaction log backup - every 15 minutes
BACKUP LOG [Ignition_Historian] 
TO DISK = 'D:\Backups\Historian_TLog_$(datetime).trn'

-- Verify backup
RESTORE VERIFYONLY 
FROM DISK = 'D:\Backups\Historian_FULL_*.bak'
```

### 5.4 Recovery Procedures

**Scenario: Data Corruption in Tag History**

```python
# Step 1: Identify corruption
query = """
SELECT COUNT(*) as corrupt_rows
FROM taghistory
WHERE floatvalue IS NULL 
  AND dataintegrity = 2
  AND ts > ?
"""

# Step 2: Restore from backup if within retention period
# Use database restore tools (MySQL dump, SQL Server restore)

# Step 3: Re-enable tag history after recovery
# - Stop historical polling
# - Restore database
# - Verify data integrity
# - Re-enable tags

# Step 4: Log recovery event
system.tag.write("[System]Events/Recovery/LastRecovery", system.date.now())
```

**Scenario: Recovering Lost Historical Data**

```python
# If backup exists and is recent enough:
# 1. Restore to separate database
# 2. Query data from backup
# 3. Insert missing records back into production

query_backup = """
SELECT ts, tagid, floatvalue, dataintegrity
FROM backup_taghistory
WHERE ts > ? AND ts < ?
  AND tagid IN (?, ?, ?)
"""

# Verify before restore
verify_query = """
SELECT COUNT(*) as existing_records
FROM taghistory
WHERE ts > ? AND ts < ?
"""
```

---

## 6. Performance Optimization for Historian

### 6.1 Database Optimization Checklist

| Optimization | Impact | Difficulty | Notes |
|--------------|--------|-----------|-------|
| **Indexing** | High | Low | Index tagid, ts columns |
| **Partitioning** | High | Medium | For >1M rows/day |
| **Compression** | Medium | Low | Block compression on tags |
| **Purging Old Data** | Medium | Low | Implement retention policy |
| **Connection Pooling** | Medium | Low | Right-size pool settings |
| **Query Optimization** | High | High | Use EXPLAIN, optimize queries |
| **Hardware Upgrade** | High | High | SSD, more RAM for DB server |

### 6.2 Database Indexing Strategy

**Critical Indexes:**

```sql
-- MySQL
CREATE INDEX idx_tagid ON taghistory(tagid);
CREATE INDEX idx_ts ON taghistory(ts);
CREATE INDEX idx_tagid_ts ON taghistory(tagid, ts);
CREATE INDEX idx_ts_tagid ON taghistory(ts, tagid);

-- SQL Server
CREATE CLUSTERED INDEX idx_ts_tagid 
ON taghistory(ts DESC, tagid);
CREATE NONCLUSTERED INDEX idx_tagid 
ON taghistory(tagid) INCLUDE (ts, floatvalue);

-- PostgreSQL
CREATE INDEX idx_tagid ON taghistory(tagid);
CREATE INDEX idx_ts ON taghistory(ts DESC);
CREATE INDEX idx_tagid_ts ON taghistory(tagid, ts DESC);
```

### 6.3 Query Performance Monitoring

**Enable Query Logging:**

```
Gateway > Configuration > Databases > [Connection] > Advanced
Query Timeout: 30000 ms (30 seconds)
Log Slow Queries: Enabled
Slow Query Threshold: 1000 ms
```

**Analyze Slow Queries:**

```sql
-- MySQL: Explain plan
EXPLAIN SELECT * FROM taghistory 
WHERE tagid = 5 AND ts > UNIX_TIMESTAMP() - (86400 * 30);

-- SQL Server: Actual Execution Plan
SET STATISTICS IO ON
SELECT * FROM taghistory 
WHERE tagid = 5 AND ts > DATEDIFF(DAY, -30, GETDATE())
SET STATISTICS IO OFF

-- PostgreSQL: Analyze query
EXPLAIN ANALYZE SELECT * FROM taghistory 
WHERE tagid = 5 AND ts > (NOW() - INTERVAL '30 days');
```

### 6.4 Tag Configuration for Performance

**Optimize Tag History Logging:**

```
Rapid Scan Class: Use only for critical values
- Frequency: 1 second
- Data volume: Extremely high
- Recommendation: Limit to <5% of tags

Normal Scan Class: Balanced logging
- Frequency: 1 minute
- Data volume: 1,000+ samples/hour per tag
- Suitable: Standard PLC/sensor data

Slow Scan Class: Low-frequency logging
- Frequency: 1 hour
- Data volume: 24 samples/day per tag
- Suitable: Derived/calculated values

Deadband Settings:
- Deadband Mode: Percent (for proportional values)
- Deadband Value: 1-5% (prevents logging small fluctuations)
- Raw Deadband: For absolute value changes
```

**Example Configuration:**

```
Temperature Tag:
- History Enabled: true
- Scan Class: Normal (1 minute)
- Deadband Mode: Absolute
- Deadband Value: 0.5°C (only log on >0.5° change)
- Result: ~1,440 records/day instead of 1,440/hour

Counter Tag:
- History Enabled: true
- Scan Class: Normal
- Deadband Mode: Raw
- Deadband Value: 1 (only log on actual count change)
- Result: Sparse logging, only value changes recorded
```

### 6.5 Database Maintenance Schedule

**Daily Maintenance (2:00 AM):**
```sql
-- Optimize/analyze tables
OPTIMIZE TABLE taghistory;
ANALYZE TABLE taghistory;

-- Check table integrity
CHECK TABLE taghistory;

-- Purge data older than retention period
DELETE FROM taghistory 
WHERE ts < UNIX_TIMESTAMP() - (86400 * 90);
```

**Weekly Maintenance (Sunday 3:00 AM):**
```sql
-- Full table rebuild
REPAIR TABLE taghistory;

-- Check for fragmentation
SELECT 
    TABLE_NAME, 
    ROUND(DATA_FREE / 1024 / 1024) as fragmented_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'ignition_historian';

-- Defragment if >100MB free space
OPTIMIZE TABLE taghistory;
```

**Monthly Maintenance (1st of month, 4:00 AM):**
```sql
-- Archive old data to separate table
INSERT INTO taghistory_archive
SELECT * FROM taghistory 
WHERE ts < UNIX_TIMESTAMP() - (86400 * 180);

DELETE FROM taghistory 
WHERE ts < UNIX_TIMESTAMP() - (86400 * 180);

-- Rebuild all indexes
REPAIR TABLE taghistory;
OPTIMIZE TABLE taghistory;

-- Update table statistics
ANALYZE TABLE taghistory;
```

### 6.6 Gateway Configuration Tuning

**Gateway Memory Allocation:**

```
For Historian Workload (in gateway.conf):
Java Heap: -Xmx4G to -Xmx8G (depends on tag count)
Example:
  -Xms2G -Xmx6G for medium deployments
  -Xms4G -Xmx12G for high-volume historian
```

**Database Connection Pool Tuning:**

```
Min Pool Size:    5
Max Pool Size:    50 (for moderate traffic)
Idle Timeout:     15 minutes
Max Wait Time:    60 seconds
Test on Borrow:   true
Test on Return:   false
Test While Idle:  true (check every 30 min)
```

**Historian Scan Class Threads:**

```
Gateway > Configuration > General > Historian
Scan Classes Thread Pool: 8-16 threads
Higher for more scan classes / more tags
```

---

## 7. Troubleshooting Common Issues

### 7.1 Historian Not Logging

**Diagnostic Steps:**

```python
# Check if historian is enabled
historianEnabled = system.tag.read("[System]Gateway/Historian/Enabled").value

# Check database connection status
query = """
SELECT 1 FROM taghistory LIMIT 1
"""
try:
    system.db.runQuery("HistorianDB", query)
    print("Database connection: OK")
except:
    print("Database connection: FAILED")

# Check tag history enabled status
print(system.tag.read("[TagProvider]TestTag").getMetadata("HistoryEnabled").value)

# Verify tag provider is running
tagProvidersRunning = system.tag.getTagMetaData(
    "[TagProvider]TestTag",
    "ProviderName"
)
```

### 7.2 Poor Query Performance

**Diagnosis:**
```sql
-- Check for missing indexes
SHOW INDEX FROM taghistory;

-- Identify slow queries
SELECT * FROM mysql.slow_log LIMIT 20;

-- Check table size
SELECT 
    TABLE_NAME,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'ignition_historian';
```

### 7.3 High Disk Usage

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| No retention policy | Implement purge script (see Section 3.2) |
| Rapid scan class overuse | Reduce scan class frequency |
| No deadband settings | Add deadband to prevent trivial changes |
| Uncompressed data | Enable block compression on tags |
| Fragmented tables | Run OPTIMIZE/REBUILD commands |

---

## 8. Best Practices Summary

1. **Database Selection:** PostgreSQL/MySQL for flexibility, SQL Server for Windows shops
2. **Separation:** Use dedicated historian database connection
3. **Indexing:** Always index (tagid, ts) columns
4. **Retention:** Implement automated purge policy within 48 hours of deployment
5. **Deadband:** Set appropriate deadband to reduce data volume by 50-80%
6. **Monitoring:** Review query performance monthly
7. **Backup:** Daily automated backups with 30-day retention minimum
8. **Partitioning:** Implement for >500K samples/day
9. **Pool Sizing:** Monitor and tune connection pools quarterly
10. **Testing:** Validate queries/scripts in test environment first

---

## References

- Inductive Automation Documentation: docs.inductiveautomation.com/docs/8.3/platform
- Database-specific tuning guides (MySQL, PostgreSQL, SQL Server)
- Ignition User Forum: forum.inductiveautomation.com
- Performance tuning: Best practices by data volume and query patterns

**Document Version:** 8.3  
**Last Updated:** 2026-07-13  
**Status:** Complete Reference

---

## See Also

**Prerequisites:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

**Builds toward:** [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
