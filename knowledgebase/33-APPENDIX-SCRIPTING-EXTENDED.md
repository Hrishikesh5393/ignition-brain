> **Skill level:** 200 · **Read first:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 33-APPENDIX-SCRIPTING-EXTENDED

# Ignition 8.3 Scripting Functions - Extended Reference

> **Source**: Ignition 8.3 Official Documentation
> **Last Updated**: Ignition 8.3 Platform Documentation
> **URL**: https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions

---

## Table of Contents

1. [Scripting Overview](#scripting-overview)
2. [Execution Scopes](#execution-scopes)
3. [System Function Modules](#system-function-modules)
4. [Core Scripting Patterns](#core-scripting-patterns)
5. [Common Use Cases](#common-use-cases)

---

## Scripting Overview

The Ignition scripting API provides the `system` module with comprehensive functionality for:

- Running database queries and transactions
- Manipulating components and UI elements
- Reading and writing tags
- File I/O operations
- Date/time calculations
- User and security management
- Report generation and distribution
- Historical data access
- Network and HTTP operations
- Device and OPC communications
- Project management and configuration

**Total Available**: 31+ major function modules across 200+ functions in Gateway scope and 150+ in Vision/Perspective scopes.

---

## Execution Scopes

Scripting functions are restricted to specific execution contexts:

### Gateway Scope

**Server-side operations**. Used in:
- Gateway event scripts
- Vision window event scripts (with shared database)
- Expression language via `runScript()` (limited)
- Report scripts
- Project library scripts
- Module scripts

**~200+ functions available** including:
- Database operations
- Historian queries
- Alarm management
- User administration
- OPC/Device communication
- File operations
- Security operations

**Example**:
```python
# Gateway only: Query database
results = system.db.runNamedQuery("GetProductionData")
```

### Vision Scope

**Desktop client operations**. Used in:
- Vision client startup scripts
- Window/component event scripts
- Vision library scripts

**~150+ functions available** including:
- Tag read/write
- Window management
- Printing
- Clipboard operations
- Screen management
- Locale settings
- Client information

**Example**:
```python
# Vision only: Open window
system.gui.openWindow("MainScreen")
```

### Perspective Scope

**Web client operations**. Used in:
- Perspective view scripts
- Component event handlers
- Perspective session startup
- Popup/dialog scripts

**~100+ functions available** including:
- Session management
- View/page navigation
- Popup management
- Popup/notification display
- Theme configuration
- Device integration (vibration, etc.)
- Local storage

**Example**:
```python
# Perspective only: Navigate view
system.perspective.navigate("ProductionDashboard")
```

### Universal Scope

**Available across all execution contexts** (~80+ functions):
- Dataset manipulation
- Date operations
- Math operations
- Basic file I/O
- Tag operations (read/write)
- JSON encoding/decoding
- Utility logging
- String operations

**Example**:
```python
# Universal: Works in Gateway, Vision, Perspective
system.tag.write("[default]MyTag", 100)
```

---

## System Function Modules

### system.alarm

**Scope**: Gateway

Alarm management and acknowledgment operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `queryStatus` | `system.alarm.queryStatus(provider, priority, state)` | Query alarm status |
| `acknowledge` | `system.alarm.acknowledge(displayPath, displayPath, ...)` | Acknowledge alarms |
| `cancel` | `system.alarm.cancel(displayPath, displayPath, ...)` | Cancel alarms |
| `shelve` | `system.alarm.shelve(displayPath, hours, displayPath, ...)` | Shelve alarm for duration |
| `unshelve` | `system.alarm.unshelve(displayPath, displayPath, ...)` | Unshelve alarms |
| `getRoster` | `system.alarm.getRoster(provider)` | Get alarm roster |

### system.dataset

**Scope**: Universal

Dataset manipulation and conversion operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `addColumn` | `system.dataset.addColumn(dataset, index, colName, colType, [colData])` | Add column to dataset |
| `addRow` | `system.dataset.addRow(dataset, rowIndex, [rowData])` | Add row to dataset |
| `addRows` | `system.dataset.addRows(dataset, rowIndex, rows)` | Add multiple rows |
| `deleteColumn` | `system.dataset.deleteColumn(dataset, columnIndex)` | Delete column |
| `deleteRow` | `system.dataset.deleteRow(dataset, rowIndex)` | Delete row |
| `deleteRows` | `system.dataset.deleteRows(dataset, rowIndex, count)` | Delete multiple rows |
| `getColumnName` | `system.dataset.getColumnName(dataset, colIndex)` | Get column name |
| `getColumnIndex` | `system.dataset.getColumnIndex(dataset, colName)` | Get column index |
| `getColumnType` | `system.dataset.getColumnType(dataset, colIndex)` | Get column data type |
| `getColumnTypes` | `system.dataset.getColumnTypes(dataset)` | Get all column types |
| `getColumnNames` | `system.dataset.getColumnNames(dataset)` | Get all column names |
| `getRowCount` | `system.dataset.getRowCount(dataset)` | Get number of rows |
| `getColumnCount` | `system.dataset.getColumnCount(dataset)` | Get number of columns |
| `toExcel` | `system.dataset.toExcel(showHeaders, datasets...)` | Convert to Excel file |
| `fromExcel` | `system.dataset.fromExcel(filepath, sheetIndex, [hasHeaders])` | Read Excel into dataset |
| `toCSV` | `system.dataset.toCSV(dataset, [showHeaders], [delimiter])` | Convert to CSV string |
| `fromCSV` | `system.dataset.fromCSV(csvData, [hasHeaders])` | Parse CSV to dataset |
| `toHTML` | `system.dataset.toHTML(dataset, [showHeaders])` | Convert to HTML table |
| `toLowerCase` | `system.dataset.toLowerCase(dataset)` | Convert all strings to lowercase |
| `toUpperCase` | `system.dataset.toUpperCase(dataset)` | Convert all strings to uppercase |
| `sort` | `system.dataset.sort(dataset, columnIndex, [ascending])` | Sort dataset by column |

**Example**:
```python
# Add a row to dataset
newDataset = system.dataset.addRow(myDataset, 0, ["John", 30, "Active"])

# Convert to CSV
csvString = system.dataset.toCSV(myDataset, True, ",")
```

### system.date

**Scope**: Universal

Date and time operations with timezone support.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `now` | `system.date.now()` | Current date/time |
| `fromMillis` | `system.date.fromMillis(millis)` | Milliseconds to date |
| `toMillis` | `system.date.toMillis(date)` | Date to milliseconds |
| `getDate` | `system.date.getDate(year, month, day)` | Create date object |
| `format` | `system.date.format(date, format)` | Format date as string |
| `parse` | `system.date.parse(dateString, format)` | Parse string to date |
| `add` | `system.date.add(date, field, amount)` | Add time to date |
| `diff` | `system.date.diff(date1, date2, unit)` | Difference between dates |
| `getTimezone` | `system.date.getTimezone()` | Get current timezone |
| `getTimezones` | `system.date.getTimezones()` | List all timezones |
| `getDSTOffset` | `system.date.getDSTOffset(date)` | Get DST offset |
| `equals` | `system.date.equals(date1, date2)` | Compare dates |
| `isAfter` | `system.date.isAfter(date1, date2)` | Date1 after date2? |
| `isBefore` | `system.date.isBefore(date1, date2)` | Date1 before date2? |

**Example**:
```python
# Add 7 days to today
futureDate = system.date.add(system.date.now(), system.date.DAY, 7)

# Format for display
dateString = system.date.format(futureDate, "yyyy-MM-dd HH:mm:ss")
```

### system.db

**Scope**: Gateway (limited in Vision/Perspective)

Database query and transaction operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `runQuery` | `system.db.runQuery(query, [database])` | Execute SQL query (blocking) |
| `runQueryAsync` | `system.db.runQueryAsync(query, [database], callback)` | Execute query asynchronously |
| `runUpdateQuery` | `system.db.runUpdateQuery(query, [database])` | Execute INSERT/UPDATE/DELETE |
| `runUpdateQueryAsync` | `system.db.runUpdateQueryAsync(query, [database], callback)` | Async update query |
| `runNamedQuery` | `system.db.runNamedQuery(queryName, [args])` | Execute stored named query |
| `runNamedQueryAsync` | `system.db.runNamedQueryAsync(queryName, [args], callback)` | Async named query |
| `runStoredProc` | `system.db.runStoredProc(name, [args])` | Call stored procedure |
| `getConnection` | `system.db.getConnection([database])` | Get database connection |
| `closeConnection` | `system.db.closeConnection(connection)` | Close connection |
| `beginTransaction` | `system.db.beginTransaction([database])` | Start transaction |
| `commitTransaction` | `system.db.commitTransaction([database])` | Commit transaction |
| `rollbackTransaction` | `system.db.rollbackTransaction([database])` | Rollback transaction |
| `toPyDataSet` | `system.db.toPyDataSet(sqlDataSet)` | Convert to Python dataset |

**Example**:
```python
# Run SQL query
results = system.db.runQuery("SELECT * FROM machines WHERE status = 'Running'")

# Transaction example
system.db.beginTransaction()
try:
    system.db.runUpdateQuery("UPDATE machines SET status = 'Stopped'")
    system.db.commitTransaction()
except:
    system.db.rollbackTransaction()
    raise
```

### system.tag

**Scope**: Universal

Tag reading, writing, browsing, and configuration operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `read` | `system.tag.read(tagPath)` | Read tag value (blocking) |
| `readAll` | `system.tag.readAll([tagPath, ...])` | Read multiple tags |
| `readAsync` | `system.tag.readAsync(tagPath, callback)` | Read tag asynchronously |
| `readBlocking` | `system.tag.readBlocking(tagPath, timeout)` | Read with timeout |
| `write` | `system.tag.write(tagPath, value)` | Write tag value |
| `writeAll` | `system.tag.writeAll([tagPath, value, ...])` | Write multiple tags |
| `writeAsync` | `system.tag.writeAsync(tagPath, value, callback)` | Write asynchronously |
| `writeBlocking` | `system.tag.writeBlocking(tagPath, value, timeout)` | Write with timeout |
| `browse` | `system.tag.browse(tagPath)` | Browse tag structure |
| `getConfiguration` | `system.tag.getConfiguration(tagPath)` | Get tag properties |
| `setConfiguration` | `system.tag.setConfiguration(tagPath, config)` | Modify tag properties |
| `getTagType` | `system.tag.getTagType(tagPath)` | Get tag data type |
| `exists` | `system.tag.exists(tagPath)` | Tag exists? |
| `queryTagCalculations` | `system.tag.queryTagCalculations(tagPath, startTime, endTime, calculations, params)` | Historical calculations |

**Special Character Handling**: Unicode strings required for special characters:
```python
# Correct (with Unicode string prefix)
system.tag.writeAsync(u'[default]HÅ/Motor_01', 10)

# Incorrect (will fail)
system.tag.writeAsync('[default]HÅ/Motor_01', 10)
```

**Example**:
```python
# Read tag value
value = system.tag.read("[default]Sensor/Temperature").value

# Write with quality check
system.tag.write("[default]Setpoint", 75, quality=192)  # 192 = Good quality

# Read multiple tags
values = system.tag.readAll(["[default]Tag1", "[default]Tag2"])
```

### system.util

**Scope**: Universal

Utility functions for logging, JSON, auditing, and version information.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `getVersion` | `system.util.getVersion()` | Get Ignition version |
| `print` | `system.util.print(message)` | Print to console/logs |
| `getLogger` | `system.util.getLogger(loggerName)` | Get logger object |
| `jsonEncode` | `system.util.jsonEncode(object)` | Encode object to JSON |
| `jsonDecode` | `system.util.jsonDecode(jsonString)` | Decode JSON to object |
| `auditable` | `system.util.auditable(message)` | Log auditable event |
| `error` | `system.util.error(message, [exception])` | Log error |
| `warn` | `system.util.warn(message)` | Log warning |
| `info` | `system.util.info(message)` | Log info |
| `debug` | `system.util.debug(message)` | Log debug |
| `sendEmail` | `system.util.sendEmail(smtp, from, to, subject, body)` | Send email |
| `modifyTranslation` | `system.util.modifyTranslation(key, locale, value)` | Modify translation |

**Example**:
```python
# Log information
system.util.print("Processing batch: %s" % batchId)

# JSON operations
jsonData = system.util.jsonEncode({"status": "Running", "value": 42})
parsedData = system.util.jsonDecode(jsonData)

# Log audit event
system.util.auditable("User modified production parameters")
```

### system.file

**Scope**: Gateway (limited in Vision/Perspective)

File I/O operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `readFileAsString` | `system.file.readFileAsString(filepath)` | Read file contents |
| `readFileAsBytes` | `system.file.readFileAsBytes(filepath)` | Read file as bytes |
| `readTextFile` | `system.file.readTextFile(filepath, [encoding])` | Read text file |
| `writeFile` | `system.file.writeFile(filepath, content)` | Write file |
| `appendFile` | `system.file.appendFile(filepath, content)` | Append to file |
| `getFileInfo` | `system.file.getFileInfo(filepath)` | Get file metadata |
| `exists` | `system.file.exists(filepath)` | File exists? |
| `getTempDir` | `system.file.getTempDir()` | Get temp directory |
| `deleteFile` | `system.file.deleteFile(filepath)` | Delete file |
| `listFiles` | `system.file.listFiles(dirPath)` | List directory contents |
| `mkdir` | `system.file.mkdir(dirPath)` | Create directory |

**Example**:
```python
# Read CSV and parse
content = system.file.readFileAsString("C:\\data\\production.csv")
lines = content.split("\n")

# Write results to file
system.file.writeFile("C:\\output\\results.txt", "Completed at " + str(system.date.now()))
```

### system.net

**Scope**: Gateway

Network and HTTP operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `getHostname` | `system.net.getHostname()` | Get machine hostname |
| `getIpAddress` | `system.net.getIpAddress()` | Get IP address |
| `getRemoteIpAddress` | `system.net.getRemoteIpAddress()` | Get remote IP |
| `httpClient` | `system.net.httpClient()` | Create HTTP client |
| `httpGet` | `system.net.httpGet(url, [headers])` | HTTP GET request |
| `httpPost` | `system.net.httpPost(url, [body], [headers])` | HTTP POST request |
| `httpPut` | `system.net.httpPut(url, body, [headers])` | HTTP PUT request |
| `httpDelete` | `system.net.httpDelete(url, [headers])` | HTTP DELETE request |

**Example**:
```python
# Make HTTP GET request
response = system.net.httpGet("https://api.example.com/data")
statusCode = response.getStatusCode()

# POST with JSON
import json
data = json.dumps({"status": "Running", "value": 42})
response = system.net.httpPost("https://api.example.com/update", data)
```

### system.opc

**Scope**: Gateway

OPC Classic server operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `browse` | `system.opc.browse(opcServer, filter)` | Browse OPC items |
| `read` | `system.opc.read(opcServer, itemId)` | Read OPC value |
| `readGroup` | `system.opc.readGroup(opcServer, [itemIds])` | Read multiple items |
| `write` | `system.opc.write(opcServer, itemId, value)` | Write OPC value |
| `writeGroup` | `system.opc.writeGroup(opcServer, [itemIds], [values])` | Write multiple items |

### system.security

**Scope**: Gateway

User authentication and role management.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `validateUser` | `system.security.validateUser(username, password)` | Check credentials |
| `getUserRoles` | `system.security.getUserRoles(username)` | Get user roles |
| `isUserInRole` | `system.security.isUserInRole(username, role)` | Has role? |
| `addUser` | `system.security.addUser(username, password, [roles])` | Create user |
| `changePassword` | `system.security.changePassword(username, newPassword)` | Update password |
| `removeUser` | `system.security.removeUser(username)` | Delete user |

**Example**:
```python
# Validate user credentials
if system.security.validateUser(username, password):
    system.util.print("User authenticated")
else:
    system.util.print("Authentication failed")

# Check user roles
if system.security.isUserInRole(username, "Administrator"):
    # Allow admin operations
    pass
```

### system.user

**Scope**: Gateway (limited in Vision/Perspective)

User and schedule management.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `getUser` | `system.user.getUser()` | Get current user |
| `getCurrentUser` | `system.user.getCurrentUser()` | Current username |
| `getCurrentUserRoles` | `system.user.getCurrentUserRoles()` | Current user roles |
| `getUserSchedules` | `system.user.getUserSchedules(username)` | Get user schedules |
| `getHolidays` | `system.user.getHolidays()` | Get holidays |
| `isUserScheduled` | `system.user.isUserScheduled(username, [datetime])` | Is user on schedule? |

### system.project

**Scope**: Gateway

Project information and configuration.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `getProjectName` | `system.project.getProjectName()` | Get current project name |
| `getProjectNames` | `system.project.getProjectNames()` | List all projects |
| `getProjectPath` | `system.project.getProjectPath([projectName])` | Get project file path |

### system.device

**Scope**: Gateway

Device configuration and management.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `getHostname` | `system.device.getHostname()` | Get device hostname |
| `setHostname` | `system.device.setHostname(hostname)` | Set device hostname |
| `restart` | `system.device.restart([delaySeconds])` | Restart Ignition |
| `restartMode` | `system.device.restartMode(mode)` | Set restart mode |

### system.vision (Vision Scope Only)

**Scope**: Vision

Vision client-specific operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `openWindow` | `system.vision.openWindow(projectName, windowName, [params])` | Open window |
| `closeWindow` | `system.vision.closeWindow(window)` | Close window |
| `getWindow` | `system.vision.getWindow(windowName)` | Get window object |
| `openDialog` | `system.vision.openDialog(dialogName, [params])` | Show dialog |
| `showMessageDialog` | `system.vision.showMessageDialog(message, [title])` | Message box |
| `showConfirmDialog` | `system.vision.showConfirmDialog(message, [title])` | Confirm dialog |
| `showInputDialog` | `system.vision.showInputDialog(message, [title], [defaultValue])` | Input dialog |
| `print` | `system.vision.print(component)` | Print component |
| `getScreen` | `system.vision.getScreen([index])` | Get screen info |
| `getScreenCount` | `system.vision.getScreenCount()` | Number of screens |

**Example**:
```python
# Open a window with parameters
params = {"machineId": 42, "mode": "view"}
system.vision.openWindow("ProductionApp", "MachineDetail", params)

# Show confirmation dialog
if system.vision.showConfirmDialog("Continue with operation?"):
    # Proceed
    pass
```

### system.perspective (Perspective Scope Only)

**Scope**: Perspective

Perspective web client operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `navigate` | `system.perspective.navigate(path, [params])` | Navigate to view/page |
| `print` | `system.perspective.print(component)` | Print component |
| `openPopup` | `system.perspective.openPopup(path, [params], [options])` | Open popup |
| `closePopup` | `system.perspective.closePopup(popupId)` | Close popup |
| `showNotification` | `system.perspective.showNotification(message, [title], [options])` | Show notification |
| `setSessionData` | `system.perspective.setSessionData(key, value)` | Store session data |
| `getSessionData` | `system.perspective.getSessionData(key)` | Retrieve session data |
| `logout` | `system.perspective.logout()` | Log out current user |
| `getSessionInfo` | `system.perspective.getSessionInfo()` | Get session details |
| `setTheme` | `system.perspective.setTheme(themeName)` | Change theme |

**Example**:
```python
# Navigate to dashboard
system.perspective.navigate("Dashboard", {"timeRange": "24h"})

# Show notification
system.perspective.showNotification("Operation completed", "Success")

# Store session data
system.perspective.setSessionData("lastUpdate", system.date.now())
```

### system.report

**Scope**: Gateway

Report generation and distribution.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `executeReport` | `system.report.executeReport(reportPath, [format], [params])` | Generate report |
| `executeReportAsync` | `system.report.executeReportAsync(reportPath, [format], [params], callback)` | Async report generation |
| `sendReport` | `system.report.sendReport(reportPath, email, [format], [params])` | Email report |

### system.historian

**Scope**: Gateway

Historical tag data operations.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `query` | `system.historian.query(path, startTime, endTime, [aggregations], [params])` | Query historical data |
| `insert` | `system.historian.insert(provider, tagPath, value, timestamp)` | Insert historical data |
| `delete` | `system.historian.delete(path, startTime, endTime)` | Delete historical records |

### system.math

**Scope**: Universal

Mathematical and statistical functions.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `mean` | `system.math.mean([values])` | Calculate average |
| `median` | `system.math.median([values])` | Calculate median |
| `standardDeviation` | `system.math.standardDeviation([values])` | Calculate std dev |
| `percentile` | `system.math.percentile(percentile, [values])` | Calculate percentile |
| `maximum` | `system.math.maximum([values])` | Find maximum |
| `minimum` | `system.math.minimum([values])` | Find minimum |
| `sum` | `system.math.sum([values])` | Sum values |

---

## Core Scripting Patterns

### Blocking vs Asynchronous Operations

**Blocking** (waits for completion):
```python
# Waits for query to finish
results = system.db.runQuery("SELECT * FROM data")
print("Query completed: %d rows" % system.dataset.getRowCount(results))
```

**Asynchronous** (non-blocking):
```python
def onQueryComplete(results, error):
    if error:
        print("Error: %s" % error)
    else:
        print("Query completed: %d rows" % system.dataset.getRowCount(results))

# Returns immediately, calls callback when done
system.db.runQueryAsync("SELECT * FROM data", onQueryComplete)
```

### Transaction Management

```python
# Explicit transaction control
try:
    system.db.beginTransaction()
    
    # Multiple operations
    system.db.runUpdateQuery("UPDATE table1 SET status = 'Running'")
    system.db.runUpdateQuery("UPDATE table2 SET lastModified = NOW()")
    
    system.db.commitTransaction()
except Exception as e:
    system.db.rollbackTransaction()
    system.util.error("Transaction failed: %s" % e)
```

### Error Handling

```python
# Safe tag read with error checking
try:
    tagValue = system.tag.read("[default]Sensor/Pressure")
    if tagValue.quality.isGood():
        value = tagValue.value
    else:
        system.util.warn("Tag has poor quality: %s" % tagValue.quality)
except Exception as e:
    system.util.error("Failed to read tag: %s" % e)
```

### Resource Cleanup

```python
# File operations should be closed
try:
    content = system.file.readFileAsString("C:\\data\\config.txt")
    # Process content
finally:
    # File is automatically closed after reading
    pass

# Database connections
connection = system.db.getConnection()
try:
    # Use connection
    pass
finally:
    system.db.closeConnection(connection)
```

### Logging Best Practices

```python
# Use appropriate log levels
system.util.debug("Detailed information for debugging")
system.util.info("General information about operation")
system.util.warn("Warning about potential issue")
system.util.error("Error occurred during processing")

# Audit-worthy events
system.util.auditable("User modified critical parameters")

# Log with context
eventName = "ProductionStart"
system.util.info("%s: Operation started at %s" % (eventName, system.date.now()))
```

---

## Common Use Cases

### Database Operations with Error Handling

```python
def getProductionStats():
    try:
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total,
            SUM(CASE WHEN status='Complete' THEN 1 ELSE 0 END) as completed
        FROM production
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        """
        results = system.db.runQuery(query)
        return results
    except Exception as e:
        system.util.error("Failed to get production stats: %s" % e)
        return None
```

### Async Tag Writing

```python
def updateMultipleTags(tagUpdates):
    """
    tagUpdates: dict like {"[default]Tag1": 100, "[default]Tag2": 200}
    """
    tagPaths = list(tagUpdates.keys())
    tagValues = [tagUpdates[path] for path in tagPaths]
    
    system.tag.writeAll(tagPaths, tagValues)
```

### Dataset Manipulation

```python
def filterDataset(dataset, column, value):
    # Find matching rows
    matches = []
    for row in range(system.dataset.getRowCount(dataset)):
        if system.dataset.getValueAt(dataset, row, column) == value:
            matches.append(row)
    
    # Remove non-matching rows (from bottom up)
    for row in sorted(matches, reverse=True):
        dataset = system.dataset.deleteRow(dataset, row)
    
    return dataset
```

### Scheduled Report Generation

```python
def generateDailyReport():
    """Generate and email daily production report"""
    yesterday = system.date.add(system.date.now(), system.date.DAY, -1)
    dateStr = system.date.format(yesterday, "yyyy-MM-dd")
    
    reportParams = {"date": yesterday}
    system.report.sendReport(
        "ProductionReport",
        "manager@company.com",
        "pdf",
        reportParams
    )
    system.util.print("Daily report generated for %s" % dateStr)
```

### Configuration Change Logging

```python
def updateConfiguration(paramName, oldValue, newValue):
    """Log configuration changes"""
    system.util.auditable(
        "Configuration changed: %s from '%s' to '%s'" % 
        (paramName, oldValue, newValue)
    )
    
    # Update tag
    tagPath = "[default]Config/%s" % paramName
    system.tag.write(tagPath, newValue)
```

### Safe Data Conversions

```python
def convertTemperature(fahrenheit):
    """Convert F to C with type safety"""
    try:
        # Ensure numeric type
        f = float(fahrenheit)
        c = (f - 32) * 5.0 / 9.0
        return round(c, 2)
    except:
        system.util.error("Invalid temperature value: %s" % fahrenheit)
        return None
```

### User Authentication with Roles

```python
def executeAdminOperation():
    """Check user credentials before sensitive operation"""
    currentUser = system.user.getCurrentUser()
    
    if system.security.isUserInRole(currentUser, "Administrator"):
        # Perform admin operation
        system.util.auditable("Admin operation by %s" % currentUser)
        return True
    else:
        system.util.warn("Unauthorized: %s attempted admin operation" % currentUser)
        return False
```

---

## Important Cautions

### 1. Mutable Object Override

```python
# WRONG: This breaks all system.* function calls
system = "foo"
system.tag.read("[default]Tag")  # Will fail!

# CORRECT: Use different variable name
myValue = "foo"
system.tag.read("[default]Tag")  # Works
```

### 2. Unicode String Requirements

```python
# Special characters require Unicode prefix
# WRONG
system.tag.writeAsync('[default]HÅ/Motor_01', 10)  # Fails

# CORRECT
system.tag.writeAsync(u'[default]HÅ/Motor_01', 10)  # Works
```

### 3. Scope Limitations

```python
# Wrong scope - this won't work in Perspective
system.vision.openWindow("App", "Main")  # Error in Perspective

# Use perspective-safe alternative
system.perspective.navigate("MainView")
```

### 4. Performance Considerations

```python
# SLOW: Multiple individual tag reads
for i in range(100):
    value = system.tag.read("[default]Tag_%d" % i)

# FAST: Read all at once
tagPaths = ["[default]Tag_%d" % i for i in range(100)]
values = system.tag.readAll(tagPaths)
```

---

## Related Resources

- Ignition 8.3 Documentation: https://www.docs.inductiveautomation.com/docs/8.3/
- Scripting Functions: https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/
- Python Scripting in Ignition: https://www.docs.inductiveautomation.com/docs/8.3/platform/scripting/
- Vision Scripting: https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/vision/working-with-vision-components/event-scripts/
- Perspective Scripting: https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/perspective/working-with-perspective-components/scripting/

---

## See Also

**Prerequisites:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md)

**Builds toward:** [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md)

**Related:** [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md), [34-APPENDIX-VISION-MODULE](34-APPENDIX-VISION-MODULE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
