---
title: Ignition Module Architecture & Integration
description: Module system architecture, lifecycle, communication patterns, dependencies, and integration guide
version: 8.3+
---

> **Skill level:** 300 · **Read first:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 79-MODULES-ARCHITECTURE

# Ignition Module Architecture & Integration Guide

Comprehensive guide to how Ignition modules are architected, communicate, and integrate with each other.

**Last Updated:** 2026-07-13  
**Ignition Version:** 8.3+  
**Scope:** System architecture, module lifecycle, communication, performance

---

## Part 1: Module System Architecture

### 1.1 Core Architecture Overview

Ignition is built on a **modular gateway architecture** where the core gateway loads optional modules at startup.

```
┌─────────────────────────────────────────────────────────┐
│ IGNITION GATEWAY ARCHITECTURE (8.3+)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Gateway Core (Java JVM)                 │  │
│  │  ├─ Configuration Manager                        │  │
│  │  ├─ Module Loader                                │  │
│  │  ├─ Hook System                                  │  │
│  │  ├─ Script Engine (Jython/Python)                │  │
│  │  ├─ Clustering Support                           │  │
│  │  └─ License Manager                              │  │
│  └──────────────────────────────────────────────────┘  │
│           ↓ (loads modules from /modules dir)          │
│                                                          │
│  ┌────────────┬────────────┬────────────┬────────┐    │
│  │ Perspective│   Vision   │  OPC-UA    │  SQL   │    │
│  │   Module   │   Module   │   Module   │ Module │    │
│  └────────────┴────────────┴────────────┴────────┘    │
│                                                          │
│  ┌────────────┬────────────┬────────────┬────────┐    │
│  │  Historian │ Reporting  │   MQTT     │  Mobile│    │
│  │   Module   │   Module   │   Module   │ Module │    │
│  └────────────┴────────────┴────────────┴────────┘    │
│                                                          │
│  ┌────────────┬────────────┬────────────┐             │
│  │    MES     │     SFC    │   Compute  │             │
│  │   Module   │   Module   │   Module   │             │
│  └────────────┴────────────┴────────────┘             │
│                                                          │
│  All modules access:                                    │
│  - Tag system (real-time & historian)                  │
│  - Database layer (SQL Bridge)                         │
│  - Script engine                                       │
│  - Alarm system                                        │
│  - Security model                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Module Installation & Directory Structure

**Module files location:**
```
Ignition/
  ├─ bin/                  (gateway executables)
  ├─ lib/                  (core libraries)
  ├─ modules/              (loaded modules)
  │   ├─ Perspective-8.3.5.jar
  │   ├─ Vision-8.3.5.jar
  │   ├─ OPC-UA-8.3.5.jar
  │   ├─ SQL-8.3.5.jar
  │   ├─ Historian-8.3.5.jar
  │   ├─ Reporting-8.3.5.jar
  │   ├─ MQTT-8.3.5.jar
  │   └─ ... (other modules)
  ├─ data/
  │   ├─ projects/         (Perspective projects)
  │   ├─ db/               (internal H2 database)
  │   ├─ projects_backup/  (backups)
  │   └─ logs/             (all logs)
  └─ user-lib/             (custom classes)
```

**Module format:**
- Java .jar (Java Archive)
- Self-contained with all dependencies
- Loaded by Gateway ClassLoader
- Can be swapped/upgraded without reinstalling

### 1.3 Module ClassLoader Hierarchy

```
Bootstrap ClassLoader
    ↓
Platform ClassLoader
    ↓
Application ClassLoader (Ignition Gateway)
    ├─ Core Gateway Classes
    ├─ shared-lib/ classes
    └─ each Module has own ClassLoader
        ├─ Module A classes
        ├─ Module A dependencies
        ├─ Module B classes
        └─ Module B dependencies
```

**Isolation:**
- Each module has isolated ClassLoader
- Reduces dependency conflicts
- Modules can have different dependency versions
- But all share core gateway APIs (Tags, Database, etc.)

---

## Part 2: Module Lifecycle

### 2.1 Gateway Startup Sequence

**Sequence of events when gateway starts:**

```
Time →

1. JVM starts (Java Virtual Machine)
   |
2. Gateway core loads
   ├─ Read configuration
   ├─ Initialize system
   ├─ Start thread pools
   └─ Load hook system
   |
3. Database initialization
   ├─ Start internal H2 DB (for gateway config)
   ├─ Load project definitions
   ├─ Load module settings
   └─ Connect to external DBs (if configured)
   |
4. Module discovery
   ├─ Scan /modules/ directory
   ├─ Read module manifests (version, dependencies)
   ├─ Sort by load order
   └─ Validate licenses
   |
5. Module loading (sequential order)
   ├─ Load Module 1 (e.g., Perspective)
   │   ├─ Extract JAR
   │   ├─ Register ClassLoader
   │   ├─ Call setup() hook
   │   └─ Initialize module-specific systems
   ├─ Load Module 2 (e.g., OPC-UA)
   │   └─ (same as above)
   └─ ... Load remaining modules
   |
6. Tag system initialization
   ├─ Load tag definitions from configuration
   ├─ Register OPC-UA subscriptions (if enabled)
   ├─ Start Historian recording (if enabled)
   └─ Initialize transaction groups
   |
7. Web server startup
   ├─ Start HTTP/HTTPS (port 8088 - Admin Console)
   ├─ Start Perspective web server (if enabled)
   ├─ Load all web modules
   └─ Initialize sessions
   |
8. Post-startup hooks
   ├─ Run any scripts defined in hooks
   ├─ Start MQTT broker (if enabled)
   ├─ Initialize Mobile (if enabled)
   └─ Send startup completion event
   |
9. Ready state
   ├─ Accept connections
   ├─ Process tag reads/writes
   └─ Handle device communication
   
Total startup time: 30-240 seconds (depending on modules loaded)
```

**Module setup() hook:**
```java
public void setup(GatewayContext context) throws Exception {
  // Module initialization code
  // Access to gateway services:
  // - context.getTags()
  // - context.getDatabaseManager()
  // - context.getScriptManager()
  // etc.
}
```

### 2.2 Module Lifecycle States

```
┌─────────────────────────────────────────────┐
│  MODULE STATE MACHINE                       │
├─────────────────────────────────────────────┤
│                                              │
│  UNLOADED                                   │
│    ↓ (Admin enables module)                │
│  LOADING (JAR extraction, dependency check) │
│    ↓                                        │
│  INITIALIZING (setup() hook called)         │
│    ↓                                        │
│  RUNNING (module is active)                 │
│    ↓ (error occurs)                        │
│  ERROR (recoverable error)                  │
│    ↓ (auto-retry or admin intervention)    │
│  RUNNING or FAILED                         │
│    ↓ (admin disables module)               │
│  STOPPING (shutdown() hook called)          │
│    ↓                                        │
│  STOPPED (can be restarted)                │
│                                              │
└─────────────────────────────────────────────┘
```

### 2.3 Module Shutdown Sequence

**When gateway shuts down or module is disabled:**

```
1. Notify all modules: shutdown() hook
   ├─ Module saves state
   ├─ Close connections (devices, databases)
   ├─ Save any pending data
   └─ Cleanup resources
   
2. Wait for graceful shutdown (timeout configurable)
   ├─ Historian flushes pending writes
   ├─ Transaction groups complete
   └─ MQTT publishes last-will
   
3. Force shutdown (if timeout exceeded)
   ├─ Close thread pools
   ├─ Interrupt running tasks
   └─ Release ClassLoader
   
4. Report shutdown status
   ├─ Log shutdown events
   ├─ Save module state
   └─ Clear resources
```

**Graceful shutdown period:**
- Default: 30 seconds
- Can configure in gateway.conf
- Allows modules to save state cleanly

---

## Part 3: Module Communication

### 3.1 Inter-Module Communication Patterns

Modules communicate through shared **gateway context** and **shared systems:**

```
┌──────────────────────────────────────────────────────────┐
│ SHARED SYSTEMS (all modules access)                      │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  1. TAG SYSTEM (TagManager)                             │
│     All modules can:                                      │
│     - Read tag values (real-time)                        │
│     - Write tag values                                   │
│     - Subscribe to tag changes                           │
│     - Create/modify tags dynamically                     │
│     Example:                                              │
│       - OPC-UA reads device → writes to tag             │
│       - Perspective reads tag → displays value           │
│       - Historian listens to tag → logs value           │
│                                                            │
│  2. DATABASE LAYER (DatabaseManager)                    │
│     All modules can:                                      │
│     - Execute named queries                              │
│     - Execute raw SQL                                    │
│     - Call stored procedures                             │
│     Example:                                              │
│       - OPC-UA device reading → query config DB         │
│       - Reporting → queries SQL for report data         │
│       - MES → queries production data                   │
│                                                            │
│  3. SCRIPT ENGINE (ScriptManager)                       │
│     All modules can:                                      │
│     - Execute Python/Jython scripts                      │
│     - Schedule script execution                          │
│     - Pass data between scripts                          │
│     Example:                                              │
│       - Perspective triggers script                      │
│       - Script reads OPC-UA device                       │
│       - Script writes to database                        │
│                                                            │
│  4. ALARM SYSTEM (AlarmManager)                         │
│     All modules can:                                      │
│     - Trigger alarms                                     │
│     - Listen to alarms                                   │
│     - Query alarm history                                │
│     Example:                                              │
│       - OPC-UA detects high temp → raises alarm         │
│       - Perspective shows alarm                          │
│       - Mobile notifies user                             │
│       - Historian logs alarm event                       │
│                                                            │
│  5. SECURITY MODEL (SecurityManager)                    │
│     All modules use:                                      │
│     - User/role authentication                           │
│     - Permission checking                                │
│     - Session management                                 │
│     Example:                                              │
│       - Perspective enforces user permissions           │
│       - OPC-UA restricts device writes                  │
│       - Mobile app checks user role                     │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Tag System as Central Hub

**Tags are the primary inter-module communication mechanism:**

```
┌─────────────────────────────────────────────────────────────┐
│ TAG SYSTEM: Central Data Hub                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  OPC-UA Module                                              │
│  (reads from devices)                                       │
│    ↓ writes device values                                   │
│    └──→ TAG SYSTEM                                          │
│           ├── [Machine1/Temperature] = 87.3°C              │
│           ├── [Machine1/Pressure] = 45.2 psi               │
│           └── [Machine1/Status] = "Running"                │
│             ↑                                                │
│    ┌────────┴─────────┬──────────────┬──────────────┐      │
│    │                  │              │              │      │
│    ↓                  ↓              ↓              ↓      │
│ Perspective       Historian       Mobile        Reporting   │
│ Module            Module          Module        Module      │
│ (displays)        (logs)          (notifies)    (queries)   │
│                                                               │
│  Tag subscription flow:                                     │
│  1. Module registers listener on tag                        │
│  2. OPC-UA writes new value to tag                         │
│  3. Tag system notifies all listeners                       │
│  4. Each module reacts independently:                       │
│     - Perspective updates UI                               │
│     - Historian records value                               │
│     - Mobile sends notification                            │
│     - Reporting flags for next report                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Tag data types** (for all modules):
- Integer (int32, int64)
- Float (float32, float64)
- Boolean
- String
- DateTime
- Dataset (table structure)
- Object (complex types)

### 3.3 Query-Based Communication

**Modules communicate via database queries:**

```
Reporting Module
  └─ "SELECT * FROM production WHERE date = TODAY()"
       ↓ (executes against SQL Database)
       ↓
SQL Bridge Module
  └─ Forwards query to connected database
       ↓
   Database (PostgreSQL/MySQL/MSSQL)
       ↓ (returns result set)
       ↓
Reporting Module
  └─ Generates PDF report from results
```

### 3.4 Event-Based Communication

**Modules communicate via events:**

```
Event: Tag value changed
  ├─ Triggered by: OPC-UA writes tag
  ├─ Listeners:
  │   ├─ Historian (logs the change)
  │   ├─ Perspective (updates UI)
  │   ├─ MES (updates production metrics)
  │   └─ Alarms (checks alarm conditions)
  └─ Result: Multiple modules react independently

Event: Alarm triggered
  ├─ Triggered by: OPC-UA or script
  ├─ Listeners:
  │   ├─ Perspective (shows alarm)
  │   ├─ Mobile (sends notification)
  │   ├─ Reporting (logs for compliance)
  │   └─ Historian (records event)
  └─ Result: Coordinated response across UI/reporting
```

### 3.5 Script-Based Communication

**Python/Jython scripts act as glue between modules:**

```python
# Script example: Coordinate between OPC-UA and Database

# Read from OPC-UA tag
temp = system.tag.read("Machine1/Temperature").value

# Check condition
if temp > 100:
    # Write to database (SQL Bridge)
    system.db.runNamedQuery("LogHighTemperature", 
                           {"device": "Machine1", 
                            "temp": temp})
    
    # Create alarm (Alarm System)
    system.alarm.acknowledge("Machine1/HighTemp")
    
    # Notify via MQTT (MQTT Module)
    system.mqtt.publish("alerts/temperature/high", 
                       f"Machine1 temp = {temp}")
    
    # Log for audit trail
    system.util.getLogger().info(f"High temp alert: {temp}")
```

---

## Part 4: Module Dependencies Matrix

### 4.1 Hard Dependencies

**Must-have module relationships:**

| Module | Requires | Reason |
|--------|----------|--------|
| Tag Historian | SQL Bridge | Stores historical data in database |
| Reporting | Perspective | Uses Perspective embedding |
| Mobile | Perspective | Backend authentication & data |
| MES (Sepasoft) | SQL Bridge + Historian | Stores production data |
| SFC | (none) | But controls OPC-UA devices |
| Transaction Groups | OPC-UA + SQL Bridge | Reads devices, writes database |
| Compute Module | MQTT Module | Communicates to primary gateway |

### 4.2 Soft Dependencies (Optional but Common)

| Module A | Module B | Use Case |
|----------|----------|----------|
| Perspective | OPC-UA | Display real-time device data |
| Perspective | SQL Bridge | Populate forms/tables from database |
| Perspective | Historian | Show trending charts |
| Perspective | Reporting | Embed reports in dashboards |
| Reporting | Historian | Report on historical data |
| Reporting | OPC-UA | Report on device status |
| MQTT | OPC-UA | Publish device data to cloud |
| Mobile | SQL Bridge | Sync offline data |
| MES | MQTT | Send production data to cloud |

### 4.3 Module Dependency Diagram

```
┌────────────────────────────────────────────────────────┐
│  DEPENDENCY MATRIX (what needs what)                   │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Perspective (UI)                                      │
│    ├─ Optional: OPC-UA (real-time data)               │
│    ├─ Optional: SQL Bridge (database queries)         │
│    ├─ Optional: Historian (trend charts)              │
│    ├─ Optional: Reporting (embed reports)             │
│    └─ Optional: MQTT (IoT data feeds)                 │
│                                                         │
│  Vision (Legacy UI)                                    │
│    └─ No dependencies (independent)                    │
│                                                         │
│  OPC-UA (Device Connectivity)                          │
│    ├─ Optional: SQL Bridge (store readings)           │
│    ├─ Optional: Historian (log trends)                │
│    └─ Optional: MQTT (edge publish)                   │
│                                                         │
│  SQL Bridge (Database)                                 │
│    ├─ Historian (REQUIRES)                            │
│    ├─ MES (REQUIRES)                                  │
│    ├─ Reporting (needs for data)                      │
│    └─ Transaction Groups (REQUIRES for writes)        │
│                                                         │
│  Tag Historian                                         │
│    ├─ SQL Bridge (REQUIRES)                           │
│    └─ Optional: OPC-UA (device data source)           │
│                                                         │
│  Reporting                                             │
│    ├─ Perspective (REQUIRES for embedding)            │
│    ├─ SQL Bridge (needs for queries)                  │
│    └─ Historian (optional for trends)                 │
│                                                         │
│  MQTT Transmission                                     │
│    ├─ Optional: OPC-UA (publish device data)          │
│    ├─ Optional: Tags (publish tag changes)            │
│    └─ Optional: SQL Bridge (publish DB results)       │
│                                                         │
│  Mobile Module                                         │
│    ├─ Perspective (REQUIRES backend)                  │
│    ├─ Optional: OPC-UA (live data)                    │
│    └─ Optional: SQL Bridge (offline sync)             │
│                                                         │
│  MES (Sepasoft)                                        │
│    ├─ SQL Bridge (REQUIRES)                           │
│    ├─ Historian (REQUIRES)                            │
│    ├─ Optional: Perspective (dashboards)              │
│    └─ Optional: OPC-UA (machine data)                 │
│                                                         │
│  SFC (Sequential Function Charts)                      │
│    ├─ Optional: OPC-UA (device control)               │
│    ├─ Optional: SQL Bridge (state logging)            │
│    └─ Optional: Perspective (UI)                      │
│                                                         │
│  Transaction Groups                                    │
│    ├─ OPC-UA (REQUIRES for reads)                     │
│    ├─ SQL Bridge (REQUIRES for writes)                │
│    └─ Optional: Historian (auto-logging)              │
│                                                         │
│  Compute/Edge Module                                   │
│    ├─ MQTT (REQUIRES uplink)                          │
│    ├─ Optional: OPC-UA (local devices)                │
│    └─ Optional: SQL Bridge (local DB)                 │
│                                                         │
│  Perspective Workstation                               │
│    ├─ Perspective (REQUIRES backend)                  │
│    ├─ Optional: OPC-UA (live data)                    │
│    └─ Optional: SQL Bridge (data)                     │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## Part 5: Common Integration Patterns

### 5.1 Pattern 1: OPC-UA → Tags → Perspective Dashboard

**Data flow:**

```
┌─────────────┐
│ Industrial  │
│ PLC/Device  │
└──────┬──────┘
       │ (OPC-UA protocol)
       ↓
┌─────────────────────────────────┐
│ OPC-UA Module (subscribe to tag) │
└──────┬──────────────────────────┘
       │ (read tag value every 100ms)
       ↓
┌─────────────────────────────────┐
│ Tag System                       │
│ [Machine1/Temperature] = 87.3    │
│ [Machine1/Pressure] = 45.2       │
└──────┬──────────────────────────┘
       │ (tag change event)
       ↓
┌─────────────────────────────────┐
│ Perspective Module (listener)    │
│ Renders gauge: 87.3°C            │
│ Renders graph: trending chart    │
└──────┬──────────────────────────┘
       │ (HTTP/WebSocket)
       ↓
┌─────────────────────────────────┐
│ Browser Client                   │
│ Shows live dashboard             │
└─────────────────────────────────┘
```

**Configuration:**
- OPC-UA: Create device → add tag → set scan rate (e.g., 100ms)
- Tag: Create memory tag → bind to OPC-UA tag
- Perspective: Add gauge component → bind to tag

**Latency:**
- Device → OPC-UA: 5-50ms
- OPC-UA → Tag: <1ms
- Tag → Perspective: <100ms (WebSocket)
- Total: ~150ms typical

### 5.2 Pattern 2: Database ↔ Perspective Forms

**Data flow:**

```
┌─────────────────────┐
│ SQL Database        │
│ (MySQL/PostgreSQL)  │
└──────┬──────────────┘
       │ (JDBC)
       ↓
┌──────────────────────────────────┐
│ SQL Bridge (Named Query)          │
│ SELECT * FROM products WHERE ...  │
└──────┬───────────────────────────┘
       │ (ResultSet)
       ↓
┌──────────────────────────────────┐
│ Perspective Module               │
│ Dropdown/Table component binding │
└──────┬───────────────────────────┘
       │ (render options/rows)
       ↓
┌──────────────────────────────────┐
│ Browser Client                   │
│ User selects from dropdown       │
└──────┬───────────────────────────┘
       │ (user input)
       ↓
┌──────────────────────────────────┐
│ Perspective Script Handler       │
│ INSERT/UPDATE into database      │
└──────┬───────────────────────────┘
       │ (via SQL Bridge)
       ↓
┌─────────────────────┐
│ SQL Database        │
│ (record updated)    │
└─────────────────────┘
```

**Components used:**
- Dropdown: `props.options` bound to named query
- Table: `props.data` bound to named query
- Text field: Script trigger via `system.db.runNamedQuery()`

### 5.3 Pattern 3: Tag → Historian → Reporting

**Data flow:**

```
┌─────────────────────┐
│ OPC-UA Device       │
│ (temperature)       │
└──────┬──────────────┘
       │ (every 60 seconds)
       ↓
┌──────────────────────────────────┐
│ Tag System                       │
│ [Machine1/Temperature]           │
└──────┬───────────────────────────┘
       │ (tag subscription)
       ↓
┌──────────────────────────────────┐
│ Historian Module                 │
│ Records: {value, timestamp, ...} │
└──────┬───────────────────────────┘
       │ (batch write every 5 min)
       ↓
┌─────────────────────┐
│ History Database    │
│ (time-series data)  │
└──────┬──────────────┘
       │ (SQL query)
       ↓
┌──────────────────────────────────┐
│ Reporting Module                 │
│ SELECT * FROM historian          │
│ WHERE tag='Machine1/Temperature' │
│ AND date=TODAY()                 │
└──────┬───────────────────────────┘
       │ (render report)
       ↓
┌──────────────────────────────────┐
│ PDF Report                       │
│ - Hourly avg chart               │
│ - Daily summary                  │
│ - Min/Max/Avg values             │
└──────────────────────────────────┘
```

**Setup:**
1. Create tag from OPC-UA
2. Configure Historian: Enable logging, set storage (SQL), set scan rate
3. Create Report: Add chart component, set data source to historian query
4. Schedule report: Daily email at 6 AM

**Storage considerations:**
- 1000 values/day = ~50 KB (depends on data type)
- 1 year = ~20 MB for one tag
- Partitioning recommended for large deployments

### 5.4 Pattern 4: MQTT ↔ Cloud Integration

**Data flow:**

```
┌──────────────────────────┐
│ Ignition Gateway         │
│ (primary, on-premise)    │
└──────┬───────────────────┘
       │ (tags)
       ↓
┌──────────────────────────┐
│ MQTT Transmission Module │
└──────┬───────────────────┘
       │ (MQTT protocol)
       │ Topics:
       │ - device/machine1/temp
       │ - device/machine1/pressure
       │ - production/orders
       ↓
┌──────────────────────────┐
│ Cloud (AWS/Azure/GCP)    │
│ ├─ AWS IoT Core          │
│ ├─ Azure IoT Hub         │
│ └─ Google Cloud Pub/Sub  │
└──────┬───────────────────┘
       │ (cloud processing)
       │ - Analytics
       │ - ML predictions
       │ - Cloud dashboard
       ↓
┌──────────────────────────┐
│ MQTT Publish (down link) │
│ Topic:                   │
│ - commands/restart/line1 │
└──────┬───────────────────┘
       │ (MQTT subscribe)
       ↓
┌──────────────────────────┐
│ MQTT Transmission Module │
└──────┬───────────────────┘
       │ (script handler)
       ↓
┌──────────────────────────┐
│ Tag or OPC-UA Write      │
│ (execute restart command)│
└──────────────────────────┘
```

**Configuration:**
- MQTT Module: Enable broker, configure cloud connection
- Tags: Create MQTT bridge tags
- Script: Subscribe to command topics, trigger actions

### 5.5 Pattern 5: Transaction Group (Batch Collection)

**Data flow:**

```
┌──────────────────────────┐
│ Transaction Group        │
│ (trigger: every 60 sec)  │
└──────┬───────────────────┘
       │
       ├─→ Read OPC-UA
       │   - Machine1/Temperature
       │   - Machine1/Pressure
       │   - Machine1/Speed
       │
       ├─→ Read OPC-UA
       │   - Machine2/Temperature
       │   - Machine2/Pressure
       │
       └─→ Collect all values
           + timestamp
           ↓
┌──────────────────────────┐
│ Prepare INSERT statement │
│ INSERT INTO machine_log  │
│   (device, temp, press,  │
│    speed, timestamp)     │
│ VALUES (?, ?, ?, ?, ?)   │
└──────┬───────────────────┘
       │ (atomically)
       ↓
┌──────────────────────────┐
│ SQL Bridge (execute)     │
│ Transaction succeeds or  │
│ all-or-nothing (rollback)│
└──────┬───────────────────┘
       │
       ↓
┌──────────────────────────┐
│ Database                 │
│ machine_log table        │
│ (new rows inserted)      │
└──────────────────────────┘
```

**Benefits:**
- Single database write (atomic)
- Consistent timestamp for all values
- High performance (no row locks, batch insert)

---

## Part 6: Performance Implications (Per Module)

### 6.1 Memory Impact

| Module | Loaded | Active Session | Notes |
|--------|--------|---|---|
| Perspective | ~50 MB | +30-50 MB | Per active session |
| Vision | ~40 MB | +50-100 MB | Per client connection |
| OPC-UA | ~30 MB | +5-10 MB | Per device connection |
| SQL Bridge | ~20 MB | Minimal | Per query execution |
| Historian | ~40 MB | +1-5 MB | Per logged tag |
| Reporting | ~30 MB | +10-20 MB | Per report generation |
| MQTT | ~25 MB | Minimal | Per message |
| Mobile | ~20 MB | +50-100 MB | Per app instance |
| MES | ~50 MB | +10-50 MB | Per batch tracked |
| SFC | ~25 MB | +5-10 MB | Per SFC instance |

**Rule of thumb:** 
- Base gateway: 200-500 MB
- Each 1000 tags: +50-100 MB
- Each 100 Perspective sessions: +3-5 GB
- Total for production: 2-8 GB typical

### 6.2 CPU Impact

| Operation | CPU Cost | Notes |
|-----------|----------|-------|
| OPC-UA tag read | 0.1-1% | Per 100ms scan |
| Tag value change | 0.01% | Per event |
| Historian write | 0.2-2% | Per batch write |
| Perspective render | 1-5% | Per session, per update |
| Report generation | 5-20% | Per report (transient) |
| Script execution | 0.1-5% | Depends on complexity |
| Database query | 1-10% | Depends on query complexity |

**Scaling:**
- 100 OPC-UA devices @ 100ms scan: ~1% CPU
- 50 Perspective sessions: ~5-10% CPU
- 1000 historian tags: ~5% CPU
- Total high-load scenario: 50-70% CPU utilization

### 6.3 Network Impact

| Operation | Bandwidth | Frequency | Notes |
|-----------|-----------|-----------|-------|
| OPC-UA subscription | 0.5-5 Kbps | Per device | Varies by tag count |
| Perspective WebSocket | 1-10 Kbps | Per session | Varies by UI updates |
| MQTT publish | 0.1-1 Kbps | Per topic | Varies by frequency |
| Database query | 10-100 Kbps | Variable | Depends on result set |
| Historian write | 1-10 Kbps | Per batch | Buffered writes |

**Example bandwidth budget:**
- 100 OPC-UA devices: ~100 Kbps
- 50 Perspective sessions: ~250 Kbps
- MQTT cloud link: ~50 Kbps
- Total: ~400 Kbps (leaves plenty for edge)

### 6.4 Disk I/O Impact

| Operation | Impact | Notes |
|-----------|--------|-------|
| Historian logging | High (batch) | Write every 5-60 seconds |
| Reporting generation | Medium | Temporary file creation |
| Database queries | Variable | Depends on indexes |
| Project backup | High (periodic) | Nightly or manual |
| Log rotation | Medium | Daily rotation |

**Storage requirements:**
- Gateway config: ~100 MB
- Perspective projects: ~50-500 MB
- Internal database (H2): ~100-500 MB
- Historian database: ~1-10 GB/year (per 1000 tags)

---

## Part 7: Licensing Model

### 7.1 License Tiers & Module Inclusion

```
┌──────────────────────────────────────────────────────┐
│ LICENSING PYRAMID (by capability level)              │
├──────────────────────────────────────────────────────┤
│                                                        │
│  ENTERPRISE (All capabilities)                       │
│  ├─ All standard modules                            │
│  ├─ Professional modules                            │
│  ├─ Premium modules (Cirrus Link, MEE)              │
│  ├─ Unlimited sessions/devices/tags                 │
│  └─ Premium support                                 │
│                                                        │
│  PROFESSIONAL (Manufacturing-grade)                 │
│  ├─ All standard modules                            │
│  ├─ Mobile, SFC, Compute, Workstation              │
│  ├─ Limited sessions (e.g., 20-50)                 │
│  ├─ Limited devices (e.g., 1000)                   │
│  └─ Standard support                                │
│                                                        │
│  STANDARD (Essential features)                      │
│  ├─ Perspective, Vision, OPC-UA                    │
│  ├─ SQL Bridge, Historian, Reporting               │
│  ├─ MQTT Transmission, Transaction Groups          │
│  ├─ Limited sessions (e.g., 5-10)                  │
│  ├─ Limited devices (e.g., 100)                    │
│  └─ Basic support                                  │
│                                                        │
└──────────────────────────────────────────────────────┘
```

### 7.2 Module License Check

**Where to verify:**
```
Admin Console → Status → Licensing
- Shows: License type, expiration, module status
- Green checkmark: Module licensed
- Yellow warning: Trial or limited
- Red error: Not licensed or expired
```

**What each module requires:**
- Most modules: Standard+ license
- Mobile: Professional+ license
- MES (Sepasoft): Professional+ + additional cost
- Cirrus Link: Enterprise + additional cost

### 7.3 Session/Device Limits by License

| License Type | Max Sessions | Max OPC Devices | Max Tags |
|--------------|---|---|---|
| Standard | 5-20 | 100-500 | 1,000-5,000 |
| Professional | 20-100 | 500-2,000 | 5,000-20,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

**Note:** Actual limits depend on specific license purchased. Check Admin Console.

---

## Part 8: Best Practices for Module Integration

### 8.1 Architecture Design Principles

1. **Minimal module set**
   - Enable only modules you use
   - Reduces memory, startup time, complexity
   - Easier to maintain and troubleshoot

2. **Tag as central hub**
   - Use tags for inter-module communication
   - Avoid direct module-to-module dependencies
   - Makes architecture decoupled and scalable

3. **Script as orchestration layer**
   - Use scripts to coordinate complex workflows
   - Keep business logic out of UI or device modules
   - Easy to debug and modify

4. **Database for persistence**
   - Store important data in SQL database
   - Use Historian for time-series
   - Easy to query and report on

5. **Alarms for critical events**
   - Use alarm system for notifications
   - Avoids polling and polling overload
   - Event-driven architecture

### 8.2 Configuration Checklist

**Before deploying:**

```
□ License verification
  □ All needed modules licensed?
  □ License not expired?
  □ Session/device limits sufficient?

□ Module dependencies
  □ SQL Bridge configured if Historian enabled?
  □ Database connections working?
  □ OPC-UA devices discoverable?

□ Performance sizing
  □ Gateway has sufficient RAM (2-8 GB)?
  □ CPU capable (2+ cores recommended)?
  □ Network bandwidth adequate?
  □ Storage space available?

□ Security configuration
  □ SSL/TLS enabled for Admin Console?
  □ User/role security configured?
  □ Database authentication set?
  □ OPC-UA security configured?

□ Monitoring
  □ Gateway logs monitored?
  □ Module status monitored?
  □ Database connectivity monitored?
  □ Backup procedure in place?

□ Testing
  □ OPC-UA devices reading correctly?
  □ Perspective dashboards rendering?
  □ Database queries working?
  □ Historian logging data?
  □ MQTT (if used) publishing?
```

### 8.3 Troubleshooting Common Integration Issues

**Problem: Histogram not logging data**
```
Check:
1. SQL Bridge configured and connected
2. Histogram module enabled (Status → Modules)
3. Tag has Histogram enabled (Tag Manager)
4. Database table exists (check database)
5. Disk space available
```

**Problem: Perspective not showing OPC-UA data**
```
Check:
1. OPC-UA device connected (Devices status)
2. Tag created and visible (Tag Manager)
3. Perspective binding correct (property binding)
4. Network connectivity (ping device)
5. OPC-UA driver correct (device type)
```

**Problem: MQTT messages not received**
```
Check:
1. MQTT module enabled
2. Broker started (Status → Modules)
3. Topic name correct (case-sensitive)
4. QoS level appropriate
5. Network firewall allows MQTT (default 1883)
6. Cloud connection authenticated (if cloud)
```

**Problem: Transaction group not executing**
```
Check:
1. OPC-UA devices available
2. SQL database connected
3. Group enabled (Transaction Group config)
4. Trigger configured correctly
5. Group has read/write steps defined
6. Log shows execution (system logs)
```

---

## Part 9: Module Update & Maintenance

### 9.1 Update Procedure

**Steps to update a module:**

```
1. Note current version
   Admin Console → Status → Modules → [Module Name]

2. Check for updates
   Admin Console → Config → Modules
   (system checks automatically weekly)

3. Click [Update] button
   - Module downloads
   - Gateway may restart (depends on module)
   - Restart typically 2-5 minutes

4. Verify update successful
   Admin Console → Status → Modules
   - Confirm new version number
   - Check module status (should be "Running")

5. Test functionality
   - Verify dashboards still render
   - Check OPC-UA connections
   - Confirm database queries work
```

### 9.2 Version Compatibility

**Critical rule:** All modules must match gateway version

**Example:**
- Gateway: 8.3.5
- Perspective: 8.3.5 ✅ (correct)
- OPC-UA: 8.3.4 ❌ (old, may cause issues)
- SQL: 8.3.6 ❌ (newer, not compatible)

**Compatibility check:**
```
Admin Console → Status → Modules
(module version must match gateway X.Y.Z)
```

### 9.3 Backup Before Module Updates

```
Before any major module update:

1. Backup gateway
   Admin Console → Tools → Backup

2. Document current state
   - Module versions
   - Configuration
   - Any customizations

3. Test in dev environment first
   - Staging server recommended
   - Verify all integrations work
   - Check performance

4. Schedule maintenance window
   - Updates may require restart
   - Plan for potential downtime
```

---

## Part 10: Cloud & Hybrid Deployments

### 10.1 Edge-to-Cloud Architecture

```
┌──────────────────────────────────────────────────────┐
│ MULTI-SITE ARCHITECTURE WITH EDGE                   │
├──────────────────────────────────────────────────────┤
│                                                        │
│  CLOUD (Ignition Cloud / AWS / Azure)               │
│  ┌─────────────────────────────────────────────┐    │
│  │ Primary Ignition Gateway (Central)          │    │
│  │ ├─ Perspective (Central Dashboard)          │    │
│  │ ├─ Database (Central, all data)             │    │
│  │ ├─ Reporting (Enterprise reports)           │    │
│  │ └─ MQTT Broker (Cloud)                      │    │
│  └──────┬──────────┬──────────┬────────────────┘    │
│         │ MQTT     │ MQTT     │ MQTT                 │
│         │ Uplink   │ Uplink   │ Uplink              │
│         ↓          ↓          ↓                      │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────┐   │
│  │ SITE 1       │ │ SITE 2       │ │ SITE 3     │   │
│  │ Compute Edge │ │ Full Gateway │ │ Compute    │   │
│  ├──────────────┤ ├──────────────┤ ├────────────┤   │
│  │ OPC-UA       │ │ OPC-UA       │ │ OPC-UA     │   │
│  │ 10 devices   │ │ 50 devices   │ │ 5 devices  │   │
│  │              │ │ Perspective  │ │            │   │
│  │              │ │ Local UI     │ │            │   │
│  │              │ │ Local DB     │ │            │   │
│  └──────────────┘ └──────────────┘ └────────────┘   │
│        ↓                  ↓                ↓         │
│   Devices 1-10      Devices 11-60     Devices 61-65 │
│                                                        │
└──────────────────────────────────────────────────────┘

Communication:
- Cloud ← Edge: MQTT publish (telemetry, status)
- Cloud → Edge: MQTT subscribe (commands, configs)
- Each site: Independent OPC-UA to devices
- Central: All data aggregated in database
```

### 10.2 Module Strategy for Cloud

**Primary gateway (Cloud):**
- Perspective (central UI)
- SQL Bridge (central database)
- Historian (all data)
- Reporting (enterprise reports)
- MQTT Broker (uplink receiver)
- Mobile (for remote access)

**Edge gateway (Remote sites):**
- Compute Module (lightweight)
- OPC-UA (local device connectivity)
- MQTT (uplink to primary)
- Optional: SQL Bridge (local caching)

**Communication:**
- MQTT: Lightweight, reliable, works over internet
- Database: Sync periodic summaries
- Perspective: Access primary gateway dashboard

---

## Appendix: Module Reference URLs

| Module | Documentation | Admin Path |
|--------|---|---|
| Perspective | docs.inductiveautomation.com/docs/8.3/perspective/ | Config → Modules |
| Vision | docs.inductiveautomation.com/docs/8.3/vision/ | Config → Modules |
| OPC-UA | docs.inductiveautomation.com/docs/8.3/opcua/ | Devices |
| SQL Bridge | docs.inductiveautomation.com/docs/8.3/sql/ | Databases → Connections |
| Historian | docs.inductiveautomation.com/docs/8.3/historian/ | Tag Manager |
| Reporting | docs.inductiveautomation.com/docs/8.3/reporting/ | Config → Modules |
| MQTT | docs.inductiveautomation.com/docs/8.3/mqtt/ | Config → MQTT |
| Mobile | docs.inductiveautomation.com/docs/8.3/mobile/ | Config → Modules |
| SFC | docs.inductiveautomation.com/docs/8.3/sfc/ | SFC Designer |
| Compute | docs.inductiveautomation.com/docs/8.3/compute-edge/ | Config → Modules |
| Workstation | docs.inductiveautomation.com/docs/8.3/perspective-workstation/ | Config → Modules |

---

**Document Version:** 2.0  
**Last Updated:** 2026-07-13  
**Ignition Version:** 8.3+  
**Audience:** Architects, Developers, System Integrators  
**Format:** Comprehensive architectural reference

---

## See Also

**Prerequisites:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)

**Builds toward:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)

**Related:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
