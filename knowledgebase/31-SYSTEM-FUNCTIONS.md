---
title: Ignition System Functions Reference
description: Complete system.* API organized by category
---

> **Skill level:** 200 · **Read first:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 31-SYSTEM-FUNCTIONS

# Ignition System Functions (system.* API)

Python scripting in Ignition accesses functions via `system` module. Organized by category.

## Data & Collections

### system.dataset
- `system.dataset.addColumn(dataset, data, colName, colIndex)` - Add column to dataset
- `system.dataset.addRow(dataset, rowIndex, data)` - Add row
- `system.dataset.deleteColumn(dataset, colName)` - Remove column
- `system.dataset.deleteRow(dataset, rowIndex)` - Remove row
- `system.dataset.formatDataset(dataset, format)` - Convert to CSV/Excel/HTML
- `system.dataset.getColumnHeaders(dataset)` - Get column names
- `system.dataset.getColumnIndex(dataset, colName)` - Get column number
- `system.dataset.getColumnType(dataset, colIndex)` - Get data type
- `system.dataset.getSelectedData(tableComponent)` - Get selected rows
- `system.dataset.setValue(dataset, rowIndex, colIndex, value)` - Set cell value
- `system.dataset.toExcel(data, filename, rowOffset, colOffset)` - Export to Excel
- `system.dataset.toPyObject(dataset)` - Convert to Python object

### system.date
- `system.date.addDays(date, numDays)` - Add days to date
- `system.date.addHours(date, numHours)` - Add hours
- `system.date.addMinutes(date, numMinutes)` - Add minutes
- `system.date.addMonths(date, numMonths)` - Add months
- `system.date.addSeconds(date, numSeconds)` - Add seconds
- `system.date.addYears(date, numYears)` - Add years
- `system.date.daysBetween(date1, date2)` - Days between dates
- `system.date.format(date, format)` - Format date string (e.g., "yyyy-MM-dd HH:mm:ss")
- `system.date.getHour(date)` - Extract hour (0-23)
- `system.date.getMinute(date)` - Extract minute
- `system.date.getMonth(date)` - Extract month (1-12)
- `system.date.getSecond(date)` - Extract second
- `system.date.getYear(date)` - Extract year
- `system.date.now()` - Current date/time
- `system.date.parse(date, format)` - Parse date string to date object
- `system.date.toTimeZone(date, timeZone)` - Convert timezone

### system.math
- `system.math.average(values)` - Mean
- `system.math.ceil(value)` - Round up
- `system.math.floor(value)` - Round down
- `system.math.max(values)` - Maximum
- `system.math.median(values)` - Median
- `system.math.min(values)` - Minimum
- `system.math.percentile(values, percentile)` - Nth percentile
- `system.math.pow(base, exponent)` - Power
- `system.math.sqrt(value)` - Square root
- `system.math.stdDev(values)` - Standard deviation
- `system.math.sum(values)` - Sum all values
- `system.math.variance(values)` - Variance

## Database Operations

### system.db
- `system.db.beginTransaction(database)` - Start transaction
- `system.db.closeTransaction(transactionID)` - Commit/rollback
- `system.db.commitTransaction(transactionID)` - Commit changes
- `system.db.queryValue(query, [args], database)` - Single value result
- `system.db.query(query, [args], database)` - Return dataset
- `system.db.runNamedQuery(path, [parameters])` - Execute named query
- `system.db.runPreparedQuery(query, args, database)` - Prepared statement (prevents SQL injection)
- `system.db.runSFCQuery(sfcName, database, durationSeconds)` - SFC query
- `system.db.runUpdateQuery(query, [args], database)` - INSERT/UPDATE/DELETE
- `system.db.rollbackTransaction(transactionID)` - Rollback changes

**Best Practice:** Always use `runPreparedQuery()` with args to prevent SQL injection.

## Networking & Integration

### system.net
- `system.net.getIpAddress()` - Get local IP
- `system.net.getHostName()` - Get hostname
- `system.net.httpClient(url, method, [headers], [body], [timeout], [ssl])` - HTTP request
- `system.net.httpGet(url, [params])` - GET request
- `system.net.httpPost(url, [params])` - POST request
- `system.net.sendEmail(smtp, port, fromAddr, toAddrs, subject, body, [html], [attachments])` - Send email
- `system.net.sendHTTPClientRequest(url, method, params, data, headers)` - Advanced HTTP

### system.kafka
- `system.kafka.createProducer(servers, properties)` - Create Kafka producer
- `system.kafka.createConsumer(servers, topics, properties)` - Create consumer
- `system.kafka.publish(producer, topic, message, key)` - Publish message

### system.mongodb
- `system.mongodb.insert(server, database, collection, doc)` - Insert document
- `system.mongodb.find(server, database, collection, query)` - Query MongoDB
- `system.mongodb.update(server, database, collection, query, update)` - Update document
- `system.mongodb.delete(server, database, collection, query)` - Delete document

### system.opc / system.opcua / system.opchda
- `system.opcua.browse(serverName, nodeId)` - Browse OPC-UA server
- `system.opcua.readValue(serverName, nodeId)` - Read OPC-UA value
- `system.opcua.writeValue(serverName, nodeId, value)` - Write OPC-UA value
- `system.opchda.query(serverName, itemName, startTime, endTime)` - Query historical OPC data

## Tag Management

### system.tag
- `system.tag.browse(rootPath, filter)` - List tags
- `system.tag.configure(basePath, config, action)` - Create/modify tag configuration
- `system.tag.read(tagPath)` - Read tag value (single)
- `system.tag.readAll(tagPaths)` - Read multiple tags (efficient)
- `system.tag.readBlocking(tagPath, timeout)` - Read with timeout
- `system.tag.write(tagPath, value)` - Write tag value (single)
- `system.tag.writeAll(tagPaths, values)` - Write multiple tags
- `system.tag.getConfiguration(tagPath)` - Get tag config properties
- `system.tag.queryTagCalculations(tagPath, calculations, startDate, endDate)` - Historical data

**Tag Path Format:**
```
[providerName]folderName/tagName
[default]Production/Temperature
[OPC]Devices/PLC1/Motor_Speed
```

## Alarms

### system.alarm
- `system.alarm.acknowledge(alarmIds, notes)` - Acknowledge alarms
- `system.alarm.cancel(alarmIds, notes)` - Cancel alarms
- `system.alarm.query(filters)` - Query active/historical alarms
- `system.alarm.journal(filters, limit)` - Get alarm journal
- `system.alarm.createEvent(eventPath, label, priority)` - Create alarm event

## User & Security

### system.user
- `system.user.getUser()` - Current logged-in user
- `system.user.getUsers()` - All users
- `system.user.getFullName(username)` - Get user's display name
- `system.user.getRoles(username)` - Get user's roles
- `system.user.hasRole(username, role)` - Check if user has role
- `system.user.validateUser(username, password)` - Verify credentials
- `system.user.addUser(username, password, fullName)` - Create user
- `system.user.editUser(username, fullName, password)` - Modify user

### system.security
- `system.security.authenticate(username, password)` - Auth check
- `system.security.hashPassword(password)` - Hash for storage
- `system.security.verifyPassword(inputPassword, hashedPassword)` - Verify hash

### system.secrets
- `system.secrets.create(key, value)` - Store encrypted secret
- `system.secrets.get(key)` - Retrieve secret
- `system.secrets.delete(key)` - Delete secret
- `system.secrets.list()` - List all secret keys

## Project & Application Control

### system.project
- `system.project.getName()` - Get current project name
- `system.project.getVersion()` - Get project version
- `system.project.getProperty(propertyPath)` - Get project property

### system.vision (Desktop/Vision Client)
- `system.vision.createDialog(title, contentPath, width, height, [options])` - Show dialog
- `system.vision.closeWindow(windowPath)` - Close window
- `system.vision.openWindow(windowPath, [parameters])` - Open Vision window
- `system.vision.getWindow(windowPath)` - Get window object
- `system.vision.getParentWindow(component)` - Get window containing component

### system.perspective (Web/Perspective)
- `system.perspective.navigate(url)` - Navigate to page/view
- `system.perspective.navigateToView(viewPath, params)` - Open view with parameters
- `system.perspective.sendMessage(messageId, payload)` - Send message to session
- `system.perspective.getSessionInfo()` - Current session data
- `system.perspective.logout()` - Logout user

## File Operations

### system.file
- `system.file.readFileAsString(path, encoding)` - Read file content
- `system.file.writeFile(path, content, overwrite)` - Write file
- `system.file.listFiles(path)` - List directory contents
- `system.file.copyFile(source, dest, overwrite)` - Copy file
- `system.file.deleteFile(path)` - Delete file
- `system.file.exists(path)` - Check if file exists
- `system.file.getFileInfo(path)` - File metadata

## Reporting

### system.report
- `system.report.executeReport(reportPath, parameters, format)` - Run report
- `system.report.getReportTags(reportPath)` - Get available report parameters

## Logging & Diagnostics

### system.util
- `system.util.getLogger(loggerName)` - Get logger object
- `system.util.beep()` - System beep
- `system.util.jsonEncode(obj)` - Convert to JSON
- `system.util.jsonDecode(jsonString)` - Parse JSON
- `system.util.getVersion()` - Ignition version
- `system.util.threadPool` - Execute async code
- `system.util.execute(command, [args], [timeout])` - Run external process

### Logging Pattern
```python
logger = system.util.getLogger("MyScript")
logger.info("Information message")
logger.warn("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

## Scopes

Functions available differ by scope:

**Gateway Scope** (scripts, event handlers, scheduling)
- All functions available
- Can read/write tags, databases, OPC
- Long-running operations OK

**Vision Scope** (Vision client scripts)
- Tag read/write
- Window management (system.vision.*)
- Network calls (system.net.*)
- NOT: Database direct (through gateway)

**Perspective Scope** (web scripts, event handlers)
- Tag read/write (via gateway)
- Navigation (system.perspective.*)
- NOT: Direct file access, direct OPC

---
**Common Mistakes:**
1. Forgetting parameters in tag paths: `system.tag.read("[default]MyTag")` not `system.tag.read("MyTag")`
2. Not using `runPreparedQuery()` → SQL injection risk
3. Blocking gateway script → timeout. Use `threadPool` for long operations.
4. Hardcoding tag paths → fragile. Use bindings or centralized constants instead.

---

## See Also

**Prerequisites:** [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Builds toward:** [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md), [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md), [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [QUICK-REFERENCE](QUICK-REFERENCE.md)

**Related:** [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md), [36-COMPLETE-EXPRESSION-FUNCTIONS](36-COMPLETE-EXPRESSION-FUNCTIONS.md), [33-APPENDIX-SCRIPTING-EXTENDED](33-APPENDIX-SCRIPTING-EXTENDED.md), [32-SCRIPTING-PATTERNS](32-SCRIPTING-PATTERNS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
