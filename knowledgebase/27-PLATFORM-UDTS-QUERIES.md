---
title: User-Defined Types (UDTs) and Named Queries
description: OOP tag design, query management, parameterization, composition
---

> **Skill level:** 200 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 27-PLATFORM-UDTS-QUERIES

# User-Defined Types (UDTs) and Named Queries

Ignition's advanced data management features enabling object-oriented tag design and centralized query management.

---

## Part 1: User-Defined Types (UDTs)

### Overview

**UDTs** (also called Complex Tags) implement object-oriented design in Ignition:
- Parameterized data templates matching real-world devices
- Definitions define structure; instances are running copies
- Changes to Definition automatically propagate to all instances
- Support inheritance, nesting, and Vision template integration

**Core Value:** Create once, reuse everywhere—rapid deployment with centralized maintenance.

---

### UDT Creation & Structure

#### Create a Definition

**Location:** Designer → Project → Tag Browser → UDT Definitions tab

**Steps:**
1. Click Add icon → "New Data Type"
2. Name the Definition (avoid renaming after instances exist)
3. Add members by:
   - Creating Memory tags directly
   - Browsing connected devices (OPC UA, etc.)
   - Using Tag Editor's "Connected Devices" button
4. Configure properties (data types, initial values)
5. Save

**Definition Properties:**

| Property | Purpose |
|----------|---------|
| Name | Unique identifier (locked after instances created) |
| Documentation | Freeform description |
| Tooltip | UI hint text |
| Type Color | Visual organization |
| Parameters | Template variables for instances |

#### Definition Member Types

**Memory Tags:** User-created, static configuration
```
Definition "MotorStatus":
- Speed (int, range 0-5000)
- Temperature (float)
- IsRunning (bool)
```

**OPC Tags:** Device-sourced, live polling
```
Definition "Motor":
- Speed: [OPC Device]/Motors/Speed
- Fault: [OPC Device]/Motors/Fault
```

**Expression Tags:** Calculated values
```
Definition "Analysis":
- AverageSpeed: average({Speed})
- IsOverheating: {Temperature} > 80
```

**Nested UDTs:** Hierarchical structures
```
Definition "Pump":
- Motor: Motor UDT instance
- Valve: Valve UDT instance
- Metrics: Metrics UDT instance
```

---

### Parameters & Parameterization

**Purpose:** Enable template flexibility—substitute instance-specific values.

#### Define Parameters

**In Definition:**
1. Right-click Definition → "Edit Data Type"
2. Go to Parameters tab
3. Add parameter: name, default value, documentation

**Example:**
```
Definition "Motor"
Parameters:
  - DeviceAddress (default: "Device1", used in OPC paths)
  - MaxSpeed (default: 5000)
  - WarningTemp (default: 75)
```

#### Reference Parameters

**In member paths:**
```
OPC Tag Member:
  Path: {DeviceAddress}/Motors/MainMotor/Speed
  → Instance "Motor_A" → DeviceAddress = "Line1"
  → Instance "Motor_B" → DeviceAddress = "Line2"
```

**In property values:**
```
Member "SpeedWarning":
  High Limit: {MaxSpeed} * 0.8
  → Automatically scales per instance
```

#### Override Parameters per Instance

1. Create instance from Definition
2. Select instance in Tag Browser
3. Edit parameters in Tag Editor
4. Each instance can override any parameter value

**Example Workflow:**
```
Definition "MotorType" {
  Parameter: DeviceIP = "192.168.1.100"
}

Instance "Motor_A": DeviceIP = "192.168.1.101"
Instance "Motor_B": DeviceIP = "192.168.1.102"
Instance "Motor_C": (uses default) = "192.168.1.100"
```

---

### UDT Instances & Management

#### Creating Instances

**Method 1: Direct Creation**
```
Tag Browser → Tags tab → Add → Data Type Instance
→ Select Definition → Name instance → OK
```

**Method 2: Duplication**
```
Right-click existing instance → Copy
→ Paste → Rename
(Inherits all parameter overrides from original)
```

**Method 3: Multi-Instance Wizard**
```
Designer → Project → Manage Data Types → Create Multiple Instances
(Batch create with pattern-based naming)
```

#### Instance Properties

| Aspect | Behavior |
|--------|----------|
| **Inheritance** | All Definition members automatically inherited |
| **Parameter Overrides** | Select instances can override parameter defaults |
| **Member Overrides** | Select members can have different values (green dot = overridden) |
| **Parent Data Type** | Cannot change after creation; orphaned if Definition renamed |
| **Tags Contained** | Memory, OPC, Expression, nested UDT instances all supported |

#### Modifying Instances

**Override a Member Value:**
1. Select instance in Tag Browser
2. Expand instance → Select member
3. Edit property in Tag Editor
4. Green dot = overridden; grey dot = inherited from Definition
5. Click green dot to revert to Definition value

**Rename Instance:** Right-click → Rename (safe, does not affect Definition)

**Delete Instance:** Right-click → Delete (leaves Definition intact)

---

### UDT Inheritance

**Single Inheritance:** Extend existing UDT types

**Definition Hierarchy:**
```
Base Definition "Motor":
  - Speed (int)
  - Temperature (float)
  - IsRunning (bool)

Child Definition "ACMotor" (inherits Motor):
  + Frequency (float)          [new member]
  + Phase (int)                [new member]
  - Temperature override (range 0-120)  [overridden]
```

**Instance Behavior:**
- "ACMotor" instances inherit Speed, Temperature, IsRunning from Motor
- Plus gain Frequency, Phase
- Temperature has new range constraints

**Multi-Level Inheritance:**
```
Base: "Motor"
  ↓ Child: "ACMotor"
    ↓ Grandchild: "ThreePhaseACMotor"
      - Inherits all parent members
      - Can override any property
      - Can add new members
```

**Override Inherited Members:**
1. Child Definition inherits member from parent
2. Right-click member → "Edit Data Type"
3. Modify property (e.g., range, initial value)
4. All child instances automatically reflect change

---

### Best Practices

1. **Naming:**
   - Use clear, device-based names: `MotorAssembly`, `PumpStation`, `TemperatureSensor`
   - Avoid renaming Definitions after instances created (causes orphaning)
   - Use PascalCase for Definitions

2. **Parameterization:**
   - Maximize parameters to minimize instance overrides
   - Use meaningful parameter names with documentation
   - Set sensible defaults
   - Example: Single `OPCDevice` parameter vs. 10 individual overrides per instance

3. **Documentation:**
   - Add Definition-level documentation explaining purpose
   - Document each parameter with units, valid ranges
   - Use tooltips for member hints
   - Example: `Parameter "MaxSpeed": Maximum RPM (0-6000)`

4. **Organization:**
   - Create folders within Definitions for logical grouping
   - Example: Motor Definition with `Motors/`, `Status/`, `Diagnostics/` folders
   - Mirror folder structure in instances for clarity

5. **Inheritance Strategy:**
   - Use inheritance for related device types with shared core members
   - Avoid deep inheritance (3+ levels) unless necessary
   - Override only when truly different behavior needed
   - Document inheritance chain in Definition comments

6. **Nesting:**
   - Create modular Definitions—nest smaller UDTs into larger ones
   - Example: `MotorAssembly` contains `Motor` + `Gearbox` + `Coupling` UDTs
   - Supports reuse: `Motor` used standalone and nested in `Pump`

7. **Binding Support:**
   - Full Vision template support: Create templates bound to UDT member values
   - Perspective/Vision components: Bind directly to UDT instances or members
   - Example: Dashboard template parameterized with UDT root → works for any instance

---

### Example: Complete Motor UDT Workflow

**Create Definition "Motor":**
```
Parameters:
  - DeviceAddress = "opc.tcp://192.168.1.100:4840"
  - MotorID = "Motor1"
  - MaxRPM = 5000
  - TempWarning = 75

Members:
  - Speed (OPC): {DeviceAddress}/Motors/{MotorID}/Speed
  - Temperature (OPC): {DeviceAddress}/Motors/{MotorID}/Temperature
  - IsRunning (Memory): bool, initial = false
  - RPMPercent (Expression): {Speed} / {MaxRPM} * 100
  - IsHot (Expression): {Temperature} > {TempWarning}
  - LastError (Memory): string
```

**Create Instances:**
```
Instance "Motor_LineA":
  - DeviceAddress = "opc.tcp://192.168.1.101:4840"
  - MotorID = "LineA_Main"
  - MaxRPM = 6000 (override)

Instance "Motor_LineB":
  - DeviceAddress = "opc.tcp://192.168.1.102:4840"
  - MotorID = "LineB_Main"
  - MaxRPM = 5000 (default)
```

**Update Definition:**
Add new member "Vibration (OPC): {DeviceAddress}/Motors/{MotorID}/Vibration"
→ Both Motor_LineA and Motor_LineB automatically gain Vibration member

---

## Part 2: Named Queries

### Overview

**Named Queries** are pre-built, reusable SQL queries managed centrally in the Gateway.

**Benefits:**
- Write query once, call everywhere
- Centralized management and security
- Parameter support for dynamic building
- Cross-project reuse (via Gateway)
- Easier auditing and optimization

**Usage Locations:**
- Named Query bindings in Vision/Perspective
- Scripting: `system.db.runNamedQuery("path/QueryName")`
- Scheduled tasks, event handlers, timers

### Resource File Format (verified against bytecode, 8.3.7)

No Named Query resource exists anywhere on this install to inspect directly, so this is grounded in the shipped class `com.inductiveautomation.ignition.common.db.namedquery.NamedQuery` (`lib\core\common\common.jar`), not a live example — the SQL-file and resource-type-id claims are literal string constants found in that class; the exact JSON metadata filename is inferred from the standard Ignition resource wrapper pattern, not directly observed.

- Resource type id: **`named-query`** → on-disk folder `com.inductiveautomation.ignition/named-query/<Name>/`
- The SQL text itself lives in its own file, confirmed via the literal constant `QUERY_FILE = "query.sql"` (plus a guard error `"No query.sql data available..."`) — so a resource folder has `query.sql` holding the raw SQL, separate from a JSON metadata file (name unconfirmed, standard project resources use `resource.json` + `files: [...]`).
- Serialized with Gson. Real field names (from `NamedQuery$ResourceKeys`): `database`, `description`, `documentation`, `type`, `parameters`, `permissions`, `enabled`, `cacheEnabled`/`cacheAmount`/`cacheUnit`, `fallbackEnabled`/`fallbackValue`, `maxReturnSize`/`useMaxReturnSize`, `autoBatchEnabled`, `syntaxProvider`.
- `type` enum (`NamedQuery.Type`): `Query` / `ScalarQuery` / `UpdateQuery` — the return-shape concept.
- Each entry in `parameters` is a `NamedQuery.Parameter` with `type`, `identifier`, `sqlType`; the parameter's substitution kind is a separate enum `NamedQuery.ParameterType`: `Database` (bind value) / `QueryString` (literal SQL-string substitution) / `Parameter` (generic).

---

### Named Query Creation

#### Setup

**Location:** Designer → Project → Named Queries folder (or right-click → New Named Query)

**Dialog Fields:**
- **Name:** Unique identifier (use `/` for hierarchy: `Production/Motors/GetSpeed`)
- **Database:** Select datasource (must exist in Gateway config)
- **Query Type:** SELECT, INSERT, UPDATE, DELETE
- **SQL:** Write SQL with `?` placeholders for parameters

#### Simple SELECT Query

**Example: Fetch active sensors**
```sql
SELECT SensorID, SensorName, LastValue, LastUpdated
FROM Sensors
WHERE IsActive = 1
ORDER BY SensorName
```

**Call in script:**
```python
result = system.db.runNamedQuery("Sensors/GetActive")
for row in result:
    print row["SensorName"], row["LastValue"]
```

#### Parameterized Query

**Example: Get sensor data by ID**
```sql
SELECT SensorID, SensorName, LastValue, LastUpdated, MinValue, MaxValue
FROM Sensors
WHERE SensorID = ?
```

**Parameters:** Define in dialog
- Parameter 1: `sensorID` (int)

**Call with parameters:**
```python
result = system.db.runNamedQuery("Sensors/GetByID", {"sensorID": 42})
row = result[0]
print row["SensorName"], row["LastValue"]
```

#### INSERT/UPDATE/DELETE Query

**Example: Log event**
```sql
INSERT INTO EventLog (LogTime, EventType, Message, UserID)
VALUES (GETDATE(), ?, ?, ?)
```

**Parameters:**
- `eventType` (string)
- `message` (string)
- `userID` (int)

**Call in script:**
```python
system.db.runNamedQuery("Logging/InsertEvent", {
    "eventType": "MOTOR_FAULT",
    "message": "Motor_A thermal protection triggered",
    "userID": 1
})
```

---

### Query Composition

#### Simple Queries

**Single table, basic WHERE:**
```sql
SELECT OrderID, OrderDate, TotalAmount
FROM Orders
WHERE OrderDate >= ?
  AND Status = 'Open'
ORDER BY OrderDate DESC
```

**Parameters:** `startDate` (datetime)

#### Complex Queries with JOINs

**Multi-table composition:**
```sql
SELECT 
  o.OrderID,
  o.OrderDate,
  c.CustomerName,
  c.City,
  p.ProductName,
  od.Quantity,
  od.UnitPrice,
  od.Quantity * od.UnitPrice AS LineTotal
FROM Orders o
  INNER JOIN Customers c ON o.CustomerID = c.CustomerID
  INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
  INNER JOIN Products p ON od.ProductID = p.ProductID
WHERE o.OrderDate >= ?
  AND c.City = ?
ORDER BY o.OrderID, od.OrderID
```

**Parameters:**
- `startDate` (datetime)
- `city` (string)

**Bind in Perspective:**
```json
{
  "value": {
    "query": "Reports/OrdersByCity",
    "params": {
      "startDate": "2024-01-01",
      "city": "New York"
    }
  }
}
```

#### Aggregation & GROUP BY

**Summary queries:**
```sql
SELECT 
  ProductCategory,
  COUNT(DISTINCT OrderID) AS TotalOrders,
  SUM(Quantity) AS TotalQuantity,
  AVG(UnitPrice) AS AvgPrice,
  MIN(OrderDate) AS FirstOrder,
  MAX(OrderDate) AS LastOrder
FROM Orders o
  JOIN OrderDetails od ON o.OrderID = od.OrderID
  JOIN Products p ON od.ProductID = p.ProductID
WHERE o.OrderDate BETWEEN ? AND ?
GROUP BY ProductCategory
HAVING COUNT(DISTINCT OrderID) > ?
ORDER BY TotalOrders DESC
```

**Parameters:**
- `startDate` (datetime)
- `endDate` (datetime)
- `minOrders` (int)

#### Subqueries

**Nested SELECT for filtering:**
```sql
SELECT DISTINCT CustomerName, City, Phone
FROM Customers
WHERE CustomerID IN (
  SELECT DISTINCT CustomerID
  FROM Orders
  WHERE OrderDate >= ?
    AND TotalAmount > ?
)
ORDER BY CustomerName
```

**Parameters:**
- `startDate` (datetime)
- `minAmount` (decimal)

#### CASE & Conditional Logic

**Transform data with conditions:**
```sql
SELECT 
  SensorID,
  SensorName,
  LastValue,
  CASE 
    WHEN LastValue > MaxThreshold THEN 'CRITICAL'
    WHEN LastValue > WarningThreshold THEN 'WARNING'
    WHEN LastValue < MinThreshold THEN 'LOW'
    ELSE 'OK'
  END AS Status,
  LastUpdated
FROM Sensors
WHERE IsActive = 1
  AND LastValue IS NOT NULL
ORDER BY 
  CASE Status
    WHEN 'CRITICAL' THEN 1
    WHEN 'WARNING' THEN 2
    WHEN 'LOW' THEN 3
    ELSE 4
  END,
  SensorName
```

**No parameters—static status logic**

#### Window Functions (SQL Server / PostgreSQL)

**Ranking, ROW_NUMBER, LAG/LEAD:**
```sql
SELECT 
  MotorID,
  MeasurementTime,
  Temperature,
  LAG(Temperature) OVER (PARTITION BY MotorID ORDER BY MeasurementTime) AS PrevTemp,
  LEAD(Temperature) OVER (PARTITION BY MotorID ORDER BY MeasurementTime) AS NextTemp,
  ROW_NUMBER() OVER (PARTITION BY MotorID ORDER BY MeasurementTime DESC) AS RecencyRank
FROM MotorReadings
WHERE MeasurementTime >= ?
ORDER BY MotorID, MeasurementTime
```

**Parameter:** `startTime` (datetime)

---

### Parameterization & Binding

#### In Named Query Dialog

**Define parameters:**
1. Add each parameter with name, data type, optional default
2. Example: `sensorID` (int, default=1)
3. Reference in SQL with `?` placeholders in order

**Parameter Types Supported:**
- String, Int, Float, Double, Boolean, DateTime, Long, Short, Byte

#### In Script

**Pass parameters as map:**
```python
params = {
    "sensorID": 42,
    "startDate": system.date.addDays(system.date.now(), -7),
    "threshold": 75.5
}
result = system.db.runNamedQuery("Reports/SensorTrend", params)
```

#### In Bindings (Perspective/Vision)

**Named Query binding:**
```json
{
  "type": "namedQuery",
  "namedQuery": "Reports/GetOrderHistory",
  "namedQueryParams": {
    "customerID": "{view.params.selectedCustomerID}",
    "startDate": "{root.container.dateStart.value}"
  },
  "datasource": "productionDB"
}
```

**Auto-refreshes when parameters change**

#### Binding Best Practice

```json
{
  "type": "namedQuery",
  "namedQuery": "Sensors/HistoricalData",
  "namedQueryParams": {
    "sensorID": {
      "type": "property",
      "path": "params.sensorID"
    },
    "startTime": {
      "type": "expression",
      "value": "dateExtract({view.sessionDate}, 'hour') - 24"
    }
  },
  "mode": "synchronous"
}
```

---

### Named Query Best Practices

1. **Naming & Organization:**
   - Use hierarchical paths: `Production/Motors/GetSpeed`, `Reports/DailyYield`
   - Group related queries in folders
   - Use verb-noun naming: `GetXxx`, `InsertYyy`, `UpdateZzz`

2. **Parameterization:**
   - Always parameterize dynamic values; avoid string concatenation
   - UNSAFE: `"... WHERE id = " + str(id)`
   - SAFE: `"... WHERE id = ?"` + params map
   - Define meaningful parameter names and default values
   - Document parameter purpose/valid ranges in query comments

3. **Performance:**
   - Index columns used in WHERE clauses
   - Avoid SELECT * unless truly needed
   - Use database-side aggregation (SUM, COUNT, AVG) not application logic
   - Limit result sets: Add TOP/LIMIT if results can be large
   - Example: `SELECT TOP 1000 * FROM Logs WHERE...`

4. **Security:**
   - Never concatenate user input into SQL
   - Use parameterized queries exclusively
   - Named Queries run with Gateway datasource credentials (not user credentials)
   - Don't store sensitive data in query comments

5. **Maintainability:**
   - Add header comment explaining query purpose
   - Example:
     ```sql
     -- Get active sensor readings since specified time
     -- Used in Dashboard/SensorPanel
     -- Params: sensorID (int), startTime (datetime)
     SELECT ...
     ```
   - Keep queries focused—avoid overly complex logic
   - Use CTEs (WITH clauses) for readability on complex queries

6. **Error Handling:**
   ```python
   try:
       result = system.db.runNamedQuery("Path/QueryName", params)
   except:
       print "Database error: " + system.gui.errorDialog(str(lastException))
       # Fallback behavior
   ```

7. **Caching:**
   - Named Query results not cached by default
   - For read-heavy queries, consider expression tag with Query type
   - Or cache in memory tag with scheduled system.db.runNamedQuery() refresh

8. **Testing:**
   - Test queries with various parameter values in Designer
   - Verify result structure (column names, data types) before binding
   - Check performance on production dataset size, not sample data

---

### Use Cases: UDTs vs. Named Queries

| Scenario | UDT | Named Query |
|----------|-----|------------|
| **Modeling a device's tags** | ✓ Best choice | ✗ Wrong tool |
| **Reusing device templates** | ✓ Best choice | ✗ Wrong tool |
| **Fetching data from database** | ✗ Wrong tool | ✓ Best choice |
| **Parameterized queries** | ✗ Wrong tool | ✓ Best choice |
| **Dashboard data binding** | - | ✓ Named Query + UDT instances as parameter source |
| **Multiple motors with same structure** | ✓ UDT Motor instances | ✗ Wrong tool |
| **Reporting multiple sensor values** | - | ✓ Named Query (SELECT motor readings) |
| **Inheriting common tag structure** | ✓ UDT inheritance | ✗ Wrong tool |
| **Real-time OPC polling** | ✓ UDT with OPC tags | ✗ Wrong tool |
| **Historical trend analysis** | - | ✓ Named Query (SELECT historian data) |

**Typical Integration:**
```
UDT "Motor" instance
  ├─ Has OPC tags (live speed, temp)
  ├─ Has memory tags (last fault, status)
  └─ Bound to Named Query "Motors/GetMaintenanceHistory"
      → Fetches historical faults from database
```

---

## Quick Reference

### Create UDT Definition
```
Designer → Tag Browser → UDT Definitions → Add → New Data Type
→ Name it → Add members (Memory/OPC/Expression/Nested)
→ Define parameters → Save
```

### Create UDT Instance
```
Tag Browser → Tags → Add → Data Type Instance
→ Select Definition → Name instance → Set parameter overrides → OK
```

### Create Named Query
```
Designer → Project → Named Queries → New Named Query
→ Select database → Write SQL with ? placeholders
→ Define parameters → Save
```

### Call Named Query (Script)
```python
result = system.db.runNamedQuery("Folder/QueryName", {"param1": value1})
for row in result:
    print row["columnName"]
```

### Bind Named Query (Perspective)
```json
{
  "type": "namedQuery",
  "namedQuery": "Path/QueryName",
  "namedQueryParams": {"paramName": "{bindingExpression}"}
}
```

---

**Last Updated:** 2026-07-13
**Source:** docs.inductiveautomation.com/docs/8.3/platform + comprehensive research

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md)

**Builds toward:** [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md), [41-PLATFORM-ALARMS-COMPLETE](41-PLATFORM-ALARMS-COMPLETE.md), [28-PLATFORM-TRANSACTIONS-SFCS](28-PLATFORM-TRANSACTIONS-SFCS.md)

**Related:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [23-DATABASE-INTEGRATION](23-DATABASE-INTEGRATION.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
