# Ignition 8.3 — Core scripting functions (system.tag, system.db, system.dataset, system.date, system.util, system.math, system.historian, system.config, system.project, system.secrets)

These ten namespaces are the workhorses of Ignition scripting: `system.tag` and `system.historian` read and write live and historical process data; `system.db` and `system.dataset` handle relational data and the tabular PyDataSet/Dataset objects that flow through Vision and Perspective components; `system.date` and `system.math` are pure utility/calculation libraries; `system.util` is a grab-bag of Gateway, logging, messaging and JSON utilities; `system.config` is the 8.x Gateway configuration/resource API (Gateway scope only); `system.project` exposes small project-identity helpers; and `system.secrets` is the secrets-management API for encrypted credential storage. Most functions run in all three scopes — Gateway, Vision Client, Perspective Session — but `system.config` is Gateway-only, and several `system.db`/`system.tag` calls are scope- or permission-restricted, noted per function below.

## system.config
Gateway-scoped API for reading and mutating Gateway configuration resources (database connections, device connections, etc.) as generic PyResource objects, identified by moduleId/typeId/name/collection. Most mutating calls (create, replace, delete, move, rename, copy) take keyword-only params (marked with *) and require a signature -- the resource's current hex signature -- to guard against concurrent edits. Read-only calls (getResource(s), getResourceTypes, getActiveMode, getModes) need no signature. All calls accept an optional actor string for audit attribution.

### system.config.copy
`system.config.copy(*moduleId, typeId, [name], [collection], [newName], [newCollection], signature, [actor])`
Copies a resource to a new name and/or collection. When using this function, either the newName or newCollection parameter must be defined.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `String *newName` — The new name for the copied resource. Required if not changing collection for named res...; `String *newCollection` — The new collection for the copied resource. Required if not changing name for singleton...; `String *signature` — The hex-encoded signature of the resource.; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** PyResource - A PyResource containing the specified parameter attributes of an existing Gateway resource, which can also be read as plain Python properties.
- **Scope:** Gateway

### system.config.create
`system.config.create(*moduleId, typeId, [name], [collection], [config], [backupConfig], [files], [description], [enabled], [attributes], [actor])`
Creates a new resource of the specified type.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `Dictionary *config` — A dictionary representing the resoure configuration, matching the resource type's JSON...; `Dictionary *backupConfig` — A dictionary representing the backup configuration for resources that support backup da...; `Dictionary *files` — A dictionary of additional files to include with the resource. Keys are filenames, valu...; `String *description` — A description for the resource. [Optional]; `Boolean *enabled` — Whether the resource should be enabled. If omitted, the resource will be enabled when c...; `Dictionary *attributes` — A dictionary of resource attributes to set. [Optional]; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** PyResource - A PyResource containing the specified parameter attributes of your newly created Gateway resource, which can also be read as plain Python properties.
- **Scope:** Gateway

### system.config.delete
`system.config.delete(*moduleId, typeId, [name], [collection], signature, [force], [actor])`
Deletes a resource of the specified type.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `String *signature` — The hex-encoded signature of the resource.; `Boolean *force` — If true, deletes the resource even if other resources reference it. If omitted, default...; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** Nothing
- **Scope:** Gateway

### system.config.getActiveMode
`system.config.getActiveMode()`
Returns the currently active resource collection mode, or None if no mode is explicitly active.
- **Params:** None
- **Returns:** String - The active collection, as a string.
- **Scope:** Gateway

### system.config.getModes
`system.config.getModes()`
Returns a list of all available resource collection modes.
- **Params:** None
- **Returns:** List - A list of strings, containing all the available deployment modes on the Gateway.
- **Scope:** Gateway

### system.config.getResource
`system.config.getResource(*moduleId, typeId, name, collection)`
Returns a single resource.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition.
- **Returns:** PyResource - The specified Gateway resource, as a PyResource that can be read as plain Python properties.
- **Scope:** Gateway

### system.config.getResources
`system.config.getResources(*moduleId, typeId)`
Returns all resources of the specified type.
- **Params:** `String moduleId` — The module ID portion of the resource type identifier.; `String typeId` — The type ID portion of the resource type identifier.
- **Returns:** List - A List of all the resources of the specified type, as a PyResource.
- **Scope:** Gateway

### system.config.getResourceTypes
`system.config.getResourceTypes()`
Returns a list of all registered resource types.
- **Params:** None
- **Returns:** List - A list of tuples containing all the currently registered resource types on the Gateway.
- **Scope:** Gateway

### system.config.move
`system.config.move(*moduleId, typeId, [name], [collection], newCollection, signature, [actor])`
Moves a resource to a different collection.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `String *newCollection` — The new collection for the resource to move to.; `String *signature` — The hex-encoded signature of the resource.; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** PyResource - The Gateway resource that was moved, which can also be read as plain Python properties.
- **Scope:** Gateway

### system.config.rename
`system.config.rename(*moduleId, typeId, [name], [collection], newName, [references], [actor])`
Renames the specified resource.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `String *newName` — The new name for the resource.; `String *references` — How Ignition should handle references from other resources to the current value of the...; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** PyResource - The resource that was renamed, as a PyResource that can also be read as plain Python properties.
- **Scope:** Gateway

### system.config.replace
`system.config.replace(*moduleId, typeId, [name], [collection], signature, [config], [backupConfig], [files], [description], [enabled], [attributes], [actor])`
Replaces an existing resource completely with a new configuration.
- **Params:** `String *moduleId` — The module ID portion of the resource type identifier.; `String *typeId` — The type ID portion of the resource type identifier.; `String *name` — The name of the resource. Required for named resources, but must be omitted for singlet...; `String *collection` — The collection containing the resource. If omitted, uses the active definition. [Optional]; `String *signature` — The hex-encoded signature of the resource.; `Dictionary *config` — A dictionary representing the resoure configuration, matching the resource type's JSON...; `Dictionary *backupConfig` — A dictionary representing the backup configuration for resources that support backup da...; `Dictionary *files` — A dictionary of additional files to include with the resource. Keys are filenames, valu...; `String *description` — A description for the resource. [Optional]; `Boolean *enabled` — Whether the replacement resource should be enabled. If omitted, the resource will be in...; `Dictionary *attributes` — A dictionary of resource attributes to set. [Optional]; `String *actor` — A string identifying the actor performing the operation. If not specified, an identifie...
- **Returns:** PyResource - The newly configured resource, as a PyResource that can also be read as plain Python properties.
- **Scope:** Gateway

## system.dataset
Datasets (Java Dataset / Jython PyDataset) are immutable -- every mutating-sounding call (addRow, deleteRow, setValue, sort, filterColumns, etc.) returns a NEW dataset rather than modifying the input in place, so scripts must reassign the result. Use toDataset/fromCSV to build datasets from raw Python data or CSV text, and toCSV/toExcel/dataSetToHTML to export them. Prefer these functions over hand-rolled loops when reshaping table/component data in Vision and Perspective.

### system.dataset.addColumn
`system.dataset.addColumn(dataset, [colIndex], col, colName, colType)`
Takes a dataset and returns a new dataset with a new column added or inserted into it.
- **Params:** `Dataset dataset` — The starting dataset. Please be aware that this dataset will not actually be modified (...; `Integer colIndex` — The index (starting at 0) at which to insert the new column. Will throw an IndexError i...; `List[Any] col` — A Python sequence representing the data for the new column. Its length must equal the n...; `String colName` — The name of the column.
- **Returns:** Dataset - A new dataset with the new column inserted or appended.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.addRow
`system.dataset.addRow(dataset, [rowIndex], row)`
Takes a dataset and returns a new dataset with a new row added or inserted into it.
- **Params:** `Dataset dataset` — The starting dataset. Please be aware that this dataset will not actually be modified (...; `Integer rowIndex` — The index (starting at 0) at which to insert the new row. Will throw an IndexError if l...; `List[Any] row` — A Python list representing the data for the new row. Its length must equal the number o...
- **Returns:** Dataset - A new dataset with the new row inserted or appended.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.addRows
`system.dataset.addRows(dataset, [rowIndex], rows)`
Takes a dataset and returns a new dataset with new rows added or inserted into it.
- **Params:** `Dataset dataset` — The starting dataset. Please be aware that this dataset will not actually be modified (...; `Integer rowIndex` — The index (starting at 0) at which to insert the new row. Will throw an IndexError if l...; `List[Any] rows` — A Python sequence of sequences representing the data for the new rows. The length of ea...
- **Returns:** Dataset - A new dataset with the new rows inserted or appended.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.appendDataset
`system.dataset.appendDataset(dataset1, dataset2)`
Takes two different datasets and returns a new dataset with the second dataset appended to the first.
- **Params:** `Dataset dataset1` — The dataset that will come first in the returned dataset.; `Dataset dataset2` — The second dataset that will be appended to the end in the returned dataset.
- **Returns:** Dataset - A new dataset that is a combination of the original two datasets.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.clearDataset
`system.dataset.clearDataset(dataset)`
Takes a dataset and returns a new dataset with all of the same column names, but all of the rows deleted.
- **Params:** `Dataset dataset` — The starting dataset.
- **Returns:** Dataset - A new dataset with no rows.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.dataSetToHTML
`system.dataset.dataSetToHTML(showHeaders, dataset, title)`
Formats the contents of a dataset as an HTML page, returning the results as a string.
- **Params:** `Boolean showHeaders` — If true, the HTML table will include a header row.; `Dataset dataset` — The dataset to export.; `String title` — The title for the HTML page.
- **Returns:** String - The HTML page as a string.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.deleteRow
`system.dataset.deleteRow(dataset, rowIndex)`
Takes a dataset and returns a new dataset with a row removed.
- **Params:** `Dataset dataset` — The starting dataset. Please be aware that this dataset will not actually be modified (...; `Integer rowIndex` — The index (starting at 0) of the row to delete. Will throw an IndexError if out of boun...
- **Returns:** Dataset - A new dataset with the specified row removed.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.deleteRows
`system.dataset.deleteRows(dataset, rowIndices)`
Takes a dataset and returns a new dataset with one or more rows removed.
- **Params:** `Dataset dataset` — The starting dataset. Please be aware that this dataset will not actually be modified (...; `List[Integer] rowIndices` — The indices (starting at 0) of the rows to delete. Will throw an IndexError if any elem...
- **Returns:** Dataset - A new dataset with the specified rows removed.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.filterColumns
`system.dataset.filterColumns(dataset, columns)`
Takes a dataset and returns a view of the dataset containing only the columns found within the given list of columns.
- **Params:** `Dataset / PyDataset dataset` — The starting dataset.; `List[Integer] / List[String] columns` — A list of columns to keep in the returned dataset. The columns may be in integer index...
- **Returns:** Dataset - A new dataset containing the filtered columns. The order of columns in this dataset is determined by the column order provided to the columns parameter.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.formatDates
`system.dataset.formatDates( dataset, dateFormat, [locale] )`
Returns a new dataset with Date columns as strings formatted according to the dateFormat specified.
- **Params:** `Dataset / PyDataset dataset` — The starting dataset to format.; `String dateFormat` — A valid Java DateFormat string, representing how the date should be formatted. For exam...; `Locale locale` — The Locale to use for formatting. The Locale parameter accepts any valid Java Locale ob...
- **Returns:** Dataset - A new dataset, containing the formatted dates.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.fromCSV
`system.dataset.fromCSV( csv )`
Converts a dataset stored in a CSV formatted string to a dataset that can be immediately assignable to a dataset property in your project.
- **Params:** `String csv` — A string holding a CSV dataset in the format outlined above.
- **Returns:** Dataset - A new dataset.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.getColumnHeaders
`system.dataset.getColumnHeaders(dataset)`
Takes in a dataset and returns the headers as a python list.
- **Params:** `Dataset dataset` — The input dataset.
- **Returns:** List - A list of column header strings.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.setValue
`system.dataset.setValue(dataset, rowIndex, columnName, value)` · `system.dataset.setValue(dataset, rowIndex, columnIndex, value)`
Takes a dataset and returns a new dataset with one value altered.
- **Params:** `Dataset dataset` — The starting dataset. Will not be modified (datasets are immutable), but acts as the ba...; `Integer rowIndex` — The index of the row to set the value at (starting at 0).; `String columnName` — The name of the column to set the value at. Case insensitive.; `Any value` — The new value for the specified row/column.; `Integer columnIndex` — The index of the column to set the value at (starting at 0)
- **Returns:** Dataset - A new dataset, with the new value set at the given location.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.sort
`system.dataset.sort(dataset, keyColumn [, ascending, naturalOrdering])`
Sorts a dataset and returns the sorted dataset.
- **Params:** `Dataset dataset` — The dataset to sort.; `Integer / String keyColumn` — The index of the column to sort on.; `Boolean ascending` — True for ascending order, False for descending order. If omitted, ascending order will...; `Boolean naturalOrdering` — True for natural ordering, False for alphabetical ordering. Ignored if the sort column...
- **Returns:** Dataset - A new sorted dataset.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.toCSV
`system.dataset.toCSV(dataset, showHeaders, forExport, localized)`
Formats the contents of a dataset as CSV (comma separated values), returning the resulting CSV as a string.
- **Params:** `Dataset dataset` — The dataset to export to CSV.; `Boolean showHeaders` — If set to true, a header row will be present in the CSV. Default is true.; `Boolean forExport` — If set to true, extra header information will be present in the CSV data which is neces...; `Boolean localized` — If set to true, the string representations of the values in the CSV data will be locali...
- **Returns:** String - The CSV data as a string.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.toDataset
`system.dataset.toDataset(headers, data)`
This function is used to convert PyDatasets to datasets and create new datasets from raw Python lists. When creating a new dataset, headers should have unique names.
- **Params:** `List[String] headers` — The column names for the dataset to create.; `List[Any] data` — A list of rows for the new dataset. Each row must have the same length as the headers l...
- **Returns:** Dataset - The newly created dataset.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.toExcel
`system.dataset.toExcel(showHeaders, dataset, [nullsEmpty], [sheetNames])`
Formats the contents of one or more datasets as an Excel spreadsheet, returning the results as a byte array.
- **Params:** `Boolean showHeaders` — If True, the spreadsheet will include a header row. If False, the header row will be om...; `List[Dataset] dataset` — A sequence of one or more datasets, one for each sheet in the resulting workbook.; `Boolean nullsEmpty` — If True, the spreadsheet will leave cells with NULL values empty, instead of allowing E...; `List[String] sheetNames` — Expects a list of strings, where each string is a name for one of the datasets. When us...
- **Returns:** Array - A byte array representing an Excel workbook.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.dataset.updateRow
`system.dataset.updateRow(dataset, rowIndex, changes)`
Takes a dataset and returns a new dataset with a one row altered.
- **Params:** `Dataset dataset` — The starting dataset. Will not be modified (datasets are immutable), but acts as the ba...; `Integer rowIndex` — The index of the row to update (starting at 0).; `Dictionary[String, Any] changes` — A dictionary of changes to make. The keys in the dictionary should match column names i...
- **Returns:** Dataset - A new dataset with the values at the specified row updated according to the values in the dictionary.
- **Scope:** Gateway, Vision Client, Perspective Session

## system.date
Dates are `java.util.Date` objects, always in the client/Gateway's local timezone unless a format/locale is given explicitly. Three functions are documented as wildcard families that expand to many concrete calls sharing one signature and behavior — treat each row below as a real callable function.

### system.date.add*  (family)
`system.date.add*(date, value)` — expands to: `addMillis`, `addSeconds`, `addMinutes`, `addHours`, `addDays`, `addWeeks`, `addMonths`, `addYears`.
Add or subtract an amount of time to a given date. `addMonths` rounds down to the closest valid day when the target month is shorter (e.g. Mar 31 + 1 month → Apr 30).
- **Params:** `Date date` — The starting date.; `Integer value` — Number of units to add (positive) or subtract (negative).
- **Returns:** Date - A new date object offset by value.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.get*  (family)
`system.date.get*(date)` — expands to: `getMillis`, `getSecond`, `getMinute`, `getHour12`, `getHour24`, `getDayOfWeek`, `getDayOfMonth`, `getDayOfYear`, `getMonth`, `getQuarter`, `getYear`, `getAMorPM`.
Extracts a single unit of time from a date (`getMonth` is 0-based, `getDayOfWeek` is 1=Sunday..7=Saturday, `getHour12` returns 0 for noon/midnight).
- **Params:** `Date date` — The date to use.
- **Returns:** Integer - the extracted unit.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.*Between  (family)
`system.date.*Between(date_1, date_2)` — expands to: `millisBetween`, `secondsBetween`, `minutesBetween`, `hoursBetween`, `daysBetween`, `weeksBetween`, `monthsBetween`, `yearsBetween`.
Calculates whole units of time between two dates (date_2 − date_1); result is negative if date_2 is earlier. `daysBetween`/`monthsBetween`/`yearsBetween` account for daylight-saving shifts.
- **Params:** `Date date_1` — The first (earlier reference) date.; `Date date_2` — The second date.
- **Returns:** Integer - signed whole-unit difference.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.format
`system.date.format(date, format)`
Returns the given date as a string and formatted according to a pattern.
- **Params:** `Date date` — The date to format.; `String format` — A format string such as "yyyy-MM-dd HH:mm:ss". The format argument is optional. The def...
- **Returns:** String - A string representing the formatted datetime.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.fromMillis
`system.date.fromMillis(millis)`
Creates a date object given a millisecond value.
- **Params:** `Long millis` — The number of milliseconds elapsed since January 1, 1970, 00:00:00 UTC (GMT).
- **Returns:** Date - A new date object.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.getDate
`system.date.getDate(year, month, day)`
Creates a new Date object given a year, month and a day.
- **Params:** `Integer year` — The year for the new date.; `Integer month` — The month of the new date. January is month 0.; `Integer day` — The day of the month for the new date. The first day of the month is day 1.
- **Returns:** Date - A new date, set to midnight of that day.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.getTimezone
`system.date.getTimezone()`
Returns the ID of the current timezone.
- **Params:** None
- **Returns:** String - A representation of the current time zone.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.getTimezoneOffset
`system.date.getTimezoneOffset([date])`
Returns the current timezone's offset versus UTC for a given instant, taking Daylight Savings Time into account.
- **Params:** `Date date` — The instant in time for which to calculate the offset. Uses now() if omitted. [optional]
- **Returns:** Double - The timezone offset compared to UTC, in hours.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.getTimezoneRawOffset
`system.date.getTimezoneRawOffset()`
Returns the current timezone offset versus UTC, not taking daylight savings into account.
- **Params:** None
- **Returns:** Double - The timezone offset.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.isAfter
`system.date.isAfter(date_1, date_2)`
Compares two dates to see if date_1 is after date_2.
- **Params:** `Date date_1` — The first date.; `Date date_2` — The second date.
- **Returns:** Boolean - True if date_1 is after date_2, false otherwise.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.isBefore
`system.date.isBefore(date_1, date_2)`
Compares two dates to see if date_1 is before date_2.
- **Params:** `Date date_1` — The first date.; `Date date_2` — The second date.
- **Returns:** Boolean - True if date_1 is before date_2, false otherwise.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.isBetween
`system.date.isBetween(target_date, start_date, end_date)`
Compares two dates to see if a target date is between two other dates.
- **Params:** `Date target_date` — The date to compare.; `Date start_date` — The start of a date range.; `Date end_date` — The end of a date range. This date must be after the start date.
- **Returns:** Boolean - True if start_date <= target_date <= end_date, false otherwise.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.isDaylightTime
`system.date.isDaylightTime([date])`
Checks to see if the current timezone is using daylight savings time during the date specified.
- **Params:** `Date date` — The date to check for daylight-saving observance in the current timezone. [optional, def...
- **Returns:** Boolean - True if date is observing daylight savings time in the current timezone; false otherwise.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.midnight
`system.date.midnight(date)`
Returns a copy of a date with the hour, minute, second, and millisecond fields set to zero.
- **Params:** `Date date` — The starting date.
- **Returns:** Date - A new date, set to midnight of the day provided.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.now
`system.date.now()`
Returns a java.util.Date object that represents the current time according to the local system clock.
- **Params:** None
- **Returns:** Date - A new date, set to the current date and time.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.parse
`system.date.parse(dateString, [formatString], [locale])`
Attempts to parse a string and create a Date.
- **Params:** `String dateString` — The string to parse into a date.; `String formatString` — Format string used by the parser. Default is "yyyy-MM-dd HH:mm:ss". [optional]; `Object locale` — Locale used for parsing. Can be a locale name such as 'fr', or a Java Locale object. [opt...
- **Returns:** Date - The parsed date.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.setTime
`system.date.setTime(date, hour, minute, second)`
Takes in a date, and returns a copy of it with the time fields set as specified.
- **Params:** `Date date` — The starting date.; `Integer hour` — The hours (0-23) to set.; `Integer minute` — The minutes (0-59) to set.; `Integer second` — The seconds (0-59) to set.
- **Returns:** Date - A new date, set to the appropriate time.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.date.toMillis
`system.date.toMillis(date)`
Converts a Date object to its millisecond value elapsed since January 1, 1970, 00:00:00 UTC (GMT).
- **Params:** `Date date` — The date object to convert.
- **Returns:** Integer - an 8-byte integer representing the number of milliseconds elapsed since epoch.
- **Scope:** Gateway, Vision Client, Perspective Session

## system.db
Covers ad-hoc SQL (execQuery/execUpdate-family against Named Queries; runPrepQuery/runPrepUpdate/execScalar for raw parameterized SQL), stored procedures (createSProcCall + execSProcCall), transactions, and datasource administration. Always prefer the *PrepQuery/PrepUpdate family (parameterized with ? placeholders) or Named Queries over string-concatenated SQL to avoid injection. A transaction (tx) is opened with beginTransaction/beginNamedQueryTransaction, passed as the tx argument to subsequent calls, and must be closed with commitTransaction/rollbackTransaction followed by closeTransaction. execUpdateAsync/runSFPrepUpdate route writes through the Store and Forward system for reliability against transient DB/network outages.

### system.db.addDatasource
`system.db.addDatasource(jdbcDriver, name, description, [connectUrl], [username], [password], [props], [validationQuery], [maxConnections])`
Adds a new database connection in Ignition.
- **Params:** `String jdbcDriver` — The name of the JDBC driver configuration to use. Available options are based off the J...; `String name` — The data source name.; `String description` — Description of the data source. [optional]; `String connectUrl` — Default is the connect URL for JDBC driver. [optional]; `String username` — Username to login to the data source with. [optional]; `String password` — Password for the login. [optional]; `String props` — The extra connection parameters. [optional]; `String validationQuery` — Default is the validation query for the JDBC driver. [optional]; `Integer maxConnections` — Default is 8. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.beginNamedQueryTransaction
`system.db.beginNamedQueryTransaction([database], [isolationLevel], [timeout])` · `system.db.beginNamedQueryTransaction(project, database, [isolationLevel], [timeout])`
Begins a new database named query transaction.
- **Params:** `String database` — The name of the database connection to create a transaction in. If omitted, uses the pr...; `Integer isolationLevel` — The transaction isolation level to use. Use one of the four constants: system.db.READ_C...; `Integer timeout` — The amount of time, in milliseconds, that this connection is allowed to remain open wit...; `String project` — The name of the project that contains the named query.
- **Returns:** String - The new transaction ID. You'll use this ID as the "tx" argument for all other calls to have them execute against this transaction.
- **Scope:** Vision Client, Gateway, Perspective Session

### system.db.beginTransaction
`system.db.beginTransaction(database, isolationLevel, timeout)`
Begins a new database transaction.
- **Params:** `String database` — The name of the database connection to create a transaction in.; `Integer isolationLevel` — The transaction isolation level to use. Use one of the four constants (system.db.READ_CO...; `Long timeout` — The amount of time, in milliseconds, that this connection is allowed to remain open wit...
- **Returns:** String - The new transaction ID. You'll use this ID as the "tx" argument for all other calls to have them execute against this transaction.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.clearQueryCache
`system.db.clearQueryCache(project, path)`
Clears the cache for a Named Query in a project.
- **Params:** `String project` — The project that contains the named query whose cache needs to be cleared. An error wil...; `String path` — The path to the named query whose cache needs to be cleared.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.closeTransaction
`system.db.closeTransaction(tx)`
Closes the transaction with the given ID.
- **Params:** `String tx` — The transaction ID.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.commitTransaction
`system.db.commitTransaction(tx)`
Performs a commit for the given transaction.
- **Params:** `String tx` — The transaction ID.
- **Returns:** —
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.createSProcCall
`system.db.createSProcCall(procedureName, database, [tx], [skipAudit])` · `system.db.createSProcCall(procedureName, [database], [tx], [skipAudit])`
Creates an SProcCall object, which is a stored procedure call context.
- **Params:** `String procedureName` — The name of the stored procedure to call.; `String database` — The name of the database connection to execute against.; `String tx` — A transaction identifier. If omitted, the call will be executed in its own transaction.; `Boolean skipAudit` — A flag which, if set to true, will cause the procedure call to skip the audit system. U...
- **Returns:** SProcCall - A stored procedure call context, which can be configured and then used as the argument to system.db.execSProcCall.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.execQuery
`system.db.execQuery(path, [parameters], [tx], [project])`
Executes a select query from a Named Query resource.
- **Params:** `String path` — The full path of the named query.; `Dictionary parameters` — A dictionary of parameters for the query. [optional]; `String tx` — A transaction ID, obtained from beginNamedQueryTransaction. If not specified, will not...; `String project` — A project name that the query exists in. [optional] Note: if unspecified, defaults to t...
- **Returns:** Dataset - The result of the query.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.execScalar
`system.db.execScalar(path, [parameters], [tx], [project])`
Executes a scalar query from a Named Query resource.
- **Params:** `String path` — The full path of the named query.; `Dictionary parameters` — A dictionary of parameters for the query. [optional]; `String tx` — A transaction ID, obtained from beginNamedQueryTransaction. If not specified, will not...; `String project` — A project name that the query exists in. [optional] Note: if unspecified, defaults to t...
- **Returns:** Any - The scalar result of the query, as either a single value or None if no rows were returned.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.execSProcCall
`system.db.execSProcCall(callContext)`
Executes a stored procedure call.
- **Params:** `SProcCall callContext` — A stored procedure call context, with any input, output, and/or return value parameters...
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.execUpdate
`system.db.execUpdate(path, [parameters], [tx], [getKey], [project])`
Executes an update query from a Named Query resource.
- **Params:** `String path` — The full path of the Named Query.; `Dictionary parameters` — A dictionary supplying parameters for the query. [optional]; `String tx` — A transaction ID, obtained from beginNamedQueryTransaction. If not specified, will not...; `Boolean getKey` — If True, the primary key of the row inserted or updated in an update query will be retu...; `String project` — A project name that the query exists in. [optional]
- **Returns:** Integer - The result of the query. The result will be either the number of rows affected or the key value that was generated, depending on the value of the getKey parameter.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.execUpdateAsync
`system.db.execUpdateAsync(path, [parameters], [project])`
Executes an update query through the Store and Forward system.
- **Params:** `String path` — The full path of the Named Query.; `Dictionary parameters` — A dictionary of parameters for the query. [optional]; `String project` — A project name that the query exists in. [optional]
- **Returns:** Boolean - True if successfully sent to the Store and Forward system.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.getConnectionInfo
`system.db.getConnectionInfo(name)`
Returns a dataset of information about a single database connection, as specified by the name argument.
- **Params:** `String name` — The name of the database connection to find information about. Will use the current pro...
- **Returns:** Dataset - Columns Name/Description/DBType/Status/Problem/ExtStatus/Throughput/ActiveConnections/MaxConnections/ValidationQuery for the connection, or an empty dataset if not found.
- **Scope:** Gateway, Vision Client, Perspective Session (Gateway scope uses the connection configured on the Gateway scripting project.)

### system.db.getConnections
`system.db.getConnections()`
Returns a dataset of information about each configured database connection. Each row represents a single connection.
- **Params:** None
- **Returns:** Dataset - one row per connection, same columns as getConnectionInfo (Name/Description/DBType/Status/Problem/ExtStatus/Throughput/ActiveConnections/MaxConnections/ValidationQuery).
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.removeDatasource
`system.db.removeDatasource(name)`
Removes a database connection from Ignition.
- **Params:** `String name` — The name of the database connection in Ignition.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.rollbackTransaction
`system.db.rollbackTransaction(tx)`
Performs a rollback on the given connection.
- **Params:** `String tx` — The transaction ID.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.runPrepQuery
`system.db.runPrepQuery(query, args, database, [tx])` · `system.db.runPrepQuery(query, args, [database], [tx])`
Runs a prepared statement against the database, returning the results in a PyDataSet.
- **Params:** `String query` — A query (typically a SELECT) to run as a prepared statement with placeholders (?) denot...; `Object[] args` — A list of arguments. Will be used in order to match each placeholder (?) found in the q...; `String database` — The name of the database connection to execute against.; `String tx` — A transaction identifier. If omitted, the query will be executed in its own transaction...
- **Returns:** PyDataSet - The results of the query as a PyDataSet.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.runPrepUpdate
`system.db.runPrepUpdate(query, args, database, [tx], [getKey], [skipAudit])` · `system.db.runPrepUpdate(query, args, [database], [tx], [getKey], [skipAudit])`
Runs a prepared statement against the database, returning the number of rows that were affected.
- **Params:** `String query` — A query (typically an UPDATE, INSERT, or DELETE) to run as a prepared statement with pl...; `Object[] args` — A list of arguments. Will be used in order to match each placeholder (?) found in the q...; `String database` — The name of the database connection to execute against.; `String tx` — A transaction identifier. If omitted, executed in its own transaction. [optional]; `Boolean getKey` — Whether the result should be the number of rows returned or the generated key. [optional]; `Boolean skipAudit` — If true, skips the audit system. [optional]
- **Returns:** Integer - The number of rows affected by the query, or the key value that was generated, depending on the value of the getKey flag.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.runSFPrepUpdate
`system.db.runSFPrepUpdate(query, args, datasources)`
Runs a prepared statement query through the store and forward system and to multiple data sources at the same time.
- **Params:** `String query` — A query (typically an UPDATE, INSERT, or DELETE) to run as a prepared statement, with p...; `Object[] args` — A list of arguments. Will be used in order to match each placeholder (?) found in the q...; `String[] datasources` — List of data sources to run the query through.
- **Returns:** Boolean - True if successfully sent to store-and-forward system.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.runScalarPrepQuery
`system.db.runScalarPrepQuery(query, args, database, [tx])` · `system.db.runScalarPrepQuery(query, args, [database], [tx])`
Runs a prepared statement against a database connection just like runPrepQuery, but only returns the value from the first row and column.
- **Params:** `String query` — A SQL query (typically a SELECT) to run as a prepared statement with placeholders (?) d...; `List[Any] args` — A list of arguments. Will be used in order to match each placeholder (?) found in the q...; `String database` — The name of the database connection to execute against.; `String tx` — A transaction identifier. If omitted, the query will be executed in its own transaction...
- **Returns:** Any - The value from the first row and first column of the results. Returns None if no rows were returned.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.setDatasourceConnectURL
`system.db.setDatasourceConnectURL(name, connectUrl)`
Changes the connect URL for a given database connection.
- **Params:** `String name` — The name of the database connection in Ignition.; `String connectUrl` — The new connect URL.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.setDatasourceEnabled
`system.db.setDatasourceEnabled(name, enabled)`
Enables/disables a given database connection.
- **Params:** `String name` — The name of the database connection in Ignition.; `Boolean enabled` — Whether the connection should be enabled.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.db.setDatasourceMaxConnections
`system.db.setDatasourceMaxConnections(name, maxConnections)`
Sets the Max Active and Max Idle parameters of a given database connection.
- **Params:** `String name` — The name of the database connection in Ignition.; `Integer maxConnections` — The new Max Active / Max Idle connection count.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

## system.historian
The 8.3 Historian rewrite: reads/writes/annotates historical data via generic "historical paths" (see Path Syntax on the system.historian overview page) rather than tag-history-specific calls. queryRawPoints returns unaggregated samples; queryAggregatedPoints applies aggregate functions (avg, min, max, etc.) per interval — prefer aggregated queries when reducing a time range to a single value or a small number of buckets, and raw queries when you need every sample. storeDataPoints/storeAnnotations/storeMetadata accept either flat parallel-list arguments or a single list of pre-built objects from `system.historian.types.dataPoint` / `.annotationPoint` / `.metadataPoint` (documented on separate type-reference pages, not full functions). All write calls return a List of QualityCode objects, one per input point, indicating per-point success/failure rather than throwing on partial failure.

### system.historian.browse
`system.historian.browse(rootPath, [nameFilters], [maxSize], [recursive], [continuationPoint], [includeMetadata])` · `system.historian.browse(rootPath, BrowseFilter)`
Returns a list of browse results for the specified historian.
- **Params:** `String rootPath` — The root path to start browsing from.; `List nameFilters` — A list of name filters to apply to the browse results. [optional]; `Integer maxSize` — The maximum number of results to return. [optional]; `Boolean recursive` — Whether to browse recursively. Default False. [optional]; `String continuationPoint` — The continuation point to continue browsing large result sets from. [optional]; `Boolean includeMetadata` — Whether to include metadata in the browse results. [optional]; `Dictionary[String, Any] browseFilter` — A dictionary of browse filter keys (Filter Keys section of the docs).
- **Returns:** Results - A Results object containing browse results; may be a partial result set (compare Total Available Size to Returned Size).
- **Scope:** Gateway, Vision Client, Perspective Session
- **Note:** `snapshotTime` parameter was removed in 8.3.9 but still accepted for backwards compatibility.

### system.historian.deleteAnnotations
`system.historian.deleteAnnotations(paths, storageIds)`
Deletes desired annotations from the specified historian.
- **Params:** `List paths` — A list of historical paths associated with the annotations.; `List storageIds` — A list of annotation storage IDs to be used for deleting.
- **Returns:** List - QualityCode objects indicating success/failure (and deletion) per storage ID.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.queryAggregatedPoints
`system.historian.queryAggregatedPoints(paths, startTime, endTime, [aggregates], [columnNames], [returnFormat], [returnSize])`
Queries aggregated data points for the specified historian.
- **Params:** `List paths` — A list of historical paths to query.; `Date startTime` — Start time to query.; `Date endTime` — End time to query.; `List aggregates` — A list of aggregate functions to apply (Average, Min, Max, etc.). [optional]; `List columnNames` — Alias column names for the returned dataset. [optional]; `String returnFormat` — WIDE (default, one row per interval, one column per path), TALL (one value per row), or CALCULATION.; `Integer returnSize` — The maximum number of results to return. [optional]
- **Returns:** Dataset - one row per interval/tag ID, one column per requested calculation/alias.
- **Scope:** Gateway, Vision Client, Perspective Session
- **Note:** `fillModes`, `includeBounds` and `excludeObservations` parameters were removed in 8.3.9 but still accepted for backwards compatibility.

### system.historian.queryAnnotations
`system.historian.queryAnnotations(paths, startDate, [endDate], [allowedTypes])`
Queries annotations for the specified historian.
- **Params:** `List paths` — A list of historical paths to query annotations for.; `Date startDate` — Start time to query annotations for.; `Date endDate` — End time to query annotations for. [optional]; `List allowedTypes` — A list of string types to filter annotations by. [optional]
- **Returns:** Results - A Results object that contains a list of query results.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.queryMetadata
`system.historian.queryMetadata(paths, [startDate], [endDate])`
Queries metadata for the specified historian.
- **Params:** `String paths` — A list of historical paths to query metadata for.; `Date startDate` — Start time to query metadata for; required if endDate is given.; `Date endDate` — End time to query metadata for; requires startDate.
- **Returns:** Results - A Results object that contains a list of query results.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.queryRawPoints
`system.historian.queryRawPoints(paths, startTime, [endTime], [columnNames], [returnFormat], [returnSize])`
Queries raw data points for the specified historian.
- **Params:** `List paths` — A list of historical paths to query.; `Date startTime` — Start time to query.; `Date endTime` — End time to query. [optional]; `List columnNames` — Alias column names for the returned dataset. [optional]; `String returnFormat` — WIDE (default), TALL, or CALCULATION. [optional]; `Integer returnSize` — Max results; only supported for Internal/Core Historian. [optional]
- **Returns:** Dataset - the raw data points for the specified historical paths.
- **Scope:** Gateway, Vision Client, Perspective Session
- **Note:** `includeBounds` and `excludeObservations` parameters were removed in 8.3.9 but still accepted for backwards compatibility. Result intervals are inclusive of endDate, so a query can return one extra (future-dated, interpolated-to-0) interval — watch for this when trending or stitching adjoining query windows.

### system.historian.storeAnnotations
`system.historian.storeAnnotations(paths, startTimes, [endTimes], [types], [data], [storageIds], [deleted])` · `system.historian.storeAnnotations(annotations)`
Store a list of annotations to the specified historian.
- **Params:** `List paths` — A list of historical paths.; `List startTimes` — Start times associated with each annotation.; `List endTimes` — End times associated with each annotation. [optional]; `List types` — String types indicating the annotation type. [optional]; `List data` — Annotation data. [optional]; `List storageIds` — Storage IDs to update existing annotations. [optional]; `List deleted` — Deleted flags per annotation. [optional]; `List annotations` — A list of annotation objects built with `system.historian.types.annotationPoint`.
- **Returns:** List - QualityCode objects indicating success/failure per annotation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.storeDataPoints
`system.historian.storeDataPoints(paths, values, [timestamps], [qualities])` · `system.historian.storeDataPoints(datapoints)`
Store a list of data points to the specified historian.
- **Params:** `List paths` — A list of qualified historical paths.; `List values` — A list of historical values.; `List timestamps` — Timestamps; current time used if omitted. [optional]; `List qualities` — Quality codes per point. [optional]; `Boolean blockForResult` — Whether to block until storage is confirmed.; `List datapoints` — A list of data point objects built with `system.historian.types.dataPoint`.
- **Returns:** List - QualityCode objects indicating success/failure per point.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.storeMetadata
`system.historian.storeMetadata(paths, timestamps, properties)` · `system.historian.storeMetadata(metadata)`
Store a list of metadata to the specified historian.
- **Params:** `List paths` — A list of historical paths.; `List timestamps` — Timestamps for each metadata entry (two datapoints may share a timestamp).; `Dictionary properties` — Properties to store as historical metadata.; `List metadata` — A list of metadata point objects built with `system.historian.types.metadataPoint`.
- **Returns:** List - QualityCode objects indicating success/failure per entry.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.updateRegisteredNodePath
`system.historian.updateRegisteredNodePath(previousPath, currentPath, [blockForResult])`
Updates the existing historical path for a stored historian node to the newly specified path.
- **Params:** `String previousPath` — The previous path for the historian node.; `String currentPath` — The new path; if null, the node is retired/unregistered.; `Boolean blockForResult` — Whether to block until the update is confirmed.
- **Returns:** List - QualityCode objects indicating success/failure of the path update.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.historian.types (data type helpers)
Three type-constructor pages (`system.historian.types.dataPoint`, `.annotationPoint`, `.metadataPoint`) build the Java objects accepted by the bulk-list overloads of `storeDataPoints`, `storeAnnotations` and `storeMetadata` respectively — use them instead of parallel lists when writing large or heterogeneous batches in one call.

## system.math
Statistics functions over a sequence (List/array) of numbers. All accept ints or floats, all return `NaN` for empty/null input (not an exception), and several (geometricMean, sumLog) return NaN if any value is negative since they use logarithms internally. Use these instead of hand-rolled loops for standard descriptive statistics on dataset columns or tag-history arrays.

### system.math.geometricMean
`system.math.geometricMean(values)`
Calculates the geometric mean.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The geometric mean, or NaN if input was empty/null, or if any entries are negative (uses logs internally).
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.kurtosis
`system.math.kurtosis(values)`
Calculates the kurtosis of a sequence of values.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The kurtosis, or NaN if input was empty/null or had fewer than four values.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.max
`system.math.max(values)`
Given a sequence of values, returns the greatest value in the sequence.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The maximum value, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.mean
`system.math.mean(values)`
Given a sequence of values, calculates the arithmetic mean (average).
- **Params:** `Float[] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The arithmetic mean, or NaN if input was empty or None.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.meanDifference
`system.math.meanDifference(values1, values2)`
Given two sequences of values, calculates the mean of the signed difference between both sequences.
- **Params:** `List[Float] values1` — First sequence of numerical values.; `List[Float] values2` — Second sequence of numerical values.
- **Returns:** Float - The mean difference, or NaN if either parameter was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.median
`system.math.median(values)`
Takes a sequence of values, and returns the median.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The median, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.min
`system.math.min(values)`
Given a sequence of numerical values, returns the minimum value.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The minimum value, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.mode
`system.math.mode(values)`
Given a sequence of values, returns the mode (most frequent value(s)).
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** List[Float] - The most frequent value(s); empty list if the input was empty.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.normalize
`system.math.normalize(values)`
Given a sequence of values, normalizes the values.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** List[Float] - The normalized input (mean 0, standard deviation 1); empty array if input was empty.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.percentile
`system.math.percentile(values, percentile)`
Given a sequence of numerical values, estimates the percentile of input.
- **Params:** `List[Float] values` — A sequence of numerical values.; `Float percentile` — The percentile to compute; > 0 and <= 100.
- **Returns:** Float - Value at the requested percentile, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.populationVariance
`system.math.populationVariance(values)`
Given a sequence of values, returns the population variance.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The population variance, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.product
`system.math.product(values)`
Given a sequence of values, calculates the product of the sequence.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The product of all values, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.skewness
`system.math.skewness(values)`
Given a sequence of values, calculates the skewness (third central moment).
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The skewness, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.standardDeviation
`system.math.standardDeviation(values)`
Given a sequence of numerical values, calculates the simple standard deviation.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The standard deviation, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.sum
`system.math.sum(values)`
Given a sequence of values, calculates the sum of all values.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The sum of all values, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.sumDifference
`system.math.sumDifference(values1, values2)`
Given two sequences of values, calculates the sum of the signed difference between both sequences.
- **Params:** `List[Float] values1` — First sequence of numerical values.; `List[Float] values2` — Second sequence of numerical values.
- **Returns:** Float - The sum difference, or NaN if either parameter was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.sumLog
`system.math.sumLog(values)`
Given a sequence of values, calculates the sum of the natural logs.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The sum of the natural logs, or NaN if input was empty, None, or contains negative numbers.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.sumSquares
`system.math.sumSquares(values)`
Given a sequence of values, calculates the sum of the squares of all values.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The sum of all squares, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.math.variance
`system.math.variance(values)`
Given a sequence of values, calculates the variance of all values.
- **Params:** `List[Float] values` — A sequence of numerical values (ints or floats).
- **Returns:** Float - The variance, or NaN if input was empty or null.
- **Scope:** Gateway, Vision Client, Perspective Session

## system.project
Three small helpers for identifying the running project and forcing the Gateway to pick up resource changes from disk.

### system.project.getProjectName
`system.project.getProjectName()`
Returns the name of the project where the function was called from.
- **Params:** None
- **Returns:** String - The name of the currently running project.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.project.getProjectNames
`system.project.getProjectNames()`
Returns an unsorted collection of strings, where each string represents the name of a project on the Gateway.
- **Params:** None
- **Returns:** List - String representations of project names on the Gateway.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.project.requestScan
`system.project.requestScan([timeout])`
Requests a manual scan of the projects directory in order to refresh projects and their resources.
- **Params:** `Integer timeout` — Time, in seconds, to block the current thread before timing out. [optional]
- **Returns:** None
- **Scope:** Gateway, Perspective Session

## system.secrets
Part of Ignition's Secrets Management system (a newer platform feature documented under Platform > Security > Secrets Management). Secrets are stored either "embedded" (encrypted directly in a resource) or "referenced" (pointing at a named Secret Provider); `createEmbeddedSecretConfig`/`createReferencedSecretConfig` build the JSON `SecretConfig` descriptor for each style, and `readConfiguredSecretValue`/`readSecretValue` resolve a config (or provider+name pair) down to a `PyPlaintext` value at runtime. `encrypt`/`decrypt` give direct access to the same encryption service for ad-hoc data outside the SecretConfig model. Treat every returned `PyPlaintext`/decrypted value as sensitive — avoid logging it or writing it back to an unencrypted tag/DB column.

### system.secrets.createEmbeddedSecretConfig
`system.secrets.createEmbeddedSecretConfig(json)`
Creates a new Embedded SecretConfig instance.
- **Params:** `PyObject json` — The JSON object containing the encrypted secret.
- **Returns:** PyObject - A Dictionary containing the JSON representation of an Embedded SecretConfig instance containing the encrypted secret.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.createReferencedSecretConfig
`system.secrets.createReferencedSecretConfig(providerName, secretName)`
Creates a new Referenced SecretConfig instance.
- **Params:** `String providerName` — The name of the secret provider.; `String secretName` — The name of the secret.
- **Returns:** PyObject - A Dictionary containing the JSON representation of a Referenced SecretConfig instance with the provider and secret names.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.decrypt
`system.secrets.decrypt(json)`
Decrypts the given JSON object containing an encrypted secret.
- **Params:** `Any json` — The JSON object containing the encrypted secret to decrypt.
- **Returns:** PyPlaintext - A PyPlaintext instance containing the decrypted secret.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.encrypt
`system.secrets.encrypt(string, [charset])` · `system.secrets.encrypt(bytes)`
Encrypts data using the Secrets Management system encryption service.
- **Params:** `String string` — The string data to encrypt.; `String charset` — The charset to use when encrypting. Defaults to UTF-8. [optional]; `List bytes` — The byte[] data to encrypt (Java-compatible byte array).
- **Returns:** PyDictionary - The encrypted secret (keys include ciphertext, encrypted_key, iv, protected, tag), or None if the input JSON was empty.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.getProviders
`system.secrets.getProviders()`
Browses a list of Secret Providers configured on the Gateway.
- **Params:** None
- **Returns:** List - SecretProviderMeta instances representing all of the Secret Providers.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.getSecrets
`system.secrets.getSecrets(providerName)`
Returns a list of all secrets for a named Secret Provider.
- **Params:** `String providerName` — The name of the Secret Provider to fetch secrets from.
- **Returns:** List - SecretMeta instances representing all secret names.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.readConfiguredSecretValue
`system.secrets.readConfiguredSecretValue(secretConfig)`
Reads the value of a secret.
- **Params:** `PyObject secretConfig` — The JSON object containing the SecretConfig.
- **Returns:** PyPlaintext - A PyPlaintext instance containing the specified secret.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.secrets.readSecretValue
`system.secrets.readSecretValue(providerName, secretName)`
Reads the plaintext value of a secret.
- **Params:** `String providerName` — The name of the Secret Provider to read the secret from.; `String secretName` — The name of the secret to read.
- **Returns:** PyPlaintext - A PyPlaintext instance that contains the secret.
- **Scope:** Gateway, Vision Client, Perspective Session

## system.tag
Reading/writing values uses two families: `readBlocking`/`writeBlocking` (pause the calling thread until the operation finishes or times out — default 45000 ms) and `readAsync`/`writeAsync` (fire-and-forget or callback-driven, return immediately). Prefer the Async variants in UI event handlers to avoid freezing Vision/Perspective while a read/write is in flight; use Blocking when the script logic must have the result before continuing. Structural operations (configure, copy, move, rename, importTags) share a `collisionPolicy` parameter controlling what happens when a tag/folder of the same name already exists at the destination. `system.tag.query` (Gateway-only) is the modern replacement for building ad-hoc tag reports against a provider.

### system.tag.browse
`system.tag.browse(path, filter)`
Returns a list of nodes found at the specified path.
- **Params:** `String path` — The path that will be browsed, typically to a folder or UDT instance.; `Dictionary[String, Any] filter` — A dictionary of browse filter keys.
- **Returns:** Results - A Results object containing a list of tag dictionaries, one per tag found during the browse.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.configure
`system.tag.configure(basePath, tags, [collisionPolicy])`
Creates tags from a given list of Python dictionaries or from a JSON source string.
- **Params:** `String basePath` — The starting point where the new tags will be created.; `Any tags` — A list of tag definitions (Python dictionaries), or a JSON string.; `String collisionPolicy` — Action to take on a name collision. [optional, default varies]
- **Returns:** List - QualityCode objects, one per tag, indicating the result of the operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.copy
`system.tag.copy(tags, destination, [collisionPolicy])`
Copies Tags from one folder to another.
- **Params:** `List tags` — A List of tag paths to copy.; `String destination` — The destination folder; all specified tags are copied to this single destination.; `String collisionPolicy` — Action to take on a name collision. [optional]
- **Returns:** List - QualityCode objects, one per tag, indicating the result of the operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.deleteTags
`system.tag.deleteTags(tagPaths)`
Deletes multiple tags or tag folders.
- **Params:** `List tagPaths` — A List of the paths to the tags or tag folders to remove.
- **Returns:** List - QualityCode objects, one per tag, indicating the result of the operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.exists
`system.tag.exists(tagPath)`
Checks whether or not a tag with a given path exists.
- **Params:** `String tagPath` — The path of the tag to look up.
- **Returns:** Boolean - True if a tag exists for the given path, false otherwise.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.exportTags
`system.tag.exportTags([filePath], tagPaths, [recursive], [exportType])`
Exports tags to a file on a local file system.
- **Params:** `String or Nothing filePath` — The path to export to; if omitted, returns the export as a string instead of writing a ...; `List tagPaths` — A List of tag paths to export, all from the same parent folder.; `Boolean recursive` — Export all tags under each path including child folders. [optional, default True]; `String exportType` — "json" or "xml"; defaults to "json".
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.getConfiguration
`system.tag.getConfiguration(basePath, recursive, [overridesOnly])`
Retrieves tags from the Gateway as Python dictionaries.
- **Params:** `String basePath` — The starting point (folder, provider or single tag) to retrieve from.; `Boolean recursive` — If true, retrieves the entire tag tree under basePath.; `Boolean overridesOnly` — If true, returns only overridden properties for UDT members. [optional]
- **Returns:** List - Tag dictionaries; nested tags are placed under the "tags" key.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.importTags
`system.tag.importTags(filePath, basePath, [collisionPolicy])`
Imports a JSON tag file at the provided path.
- **Params:** `String filePath` — The file path of the tag export to import.; `String basePath` — The Tag path to serve as the root node for the imported tags.; `String collisionPolicy` — Action to take on a name collision. [optional]
- **Returns:** List - QualityCode objects, one per tag, indicating the result of the operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.move
`system.tag.move(tags, destination, [collisionPolicy])`
Moves tags or folders to a new destination.
- **Params:** `List tags` — A List of tag paths to move.; `String destination` — The destination path; the destination tag provider must be specified.; `String collisionPolicy` — Action to take on a name collision. [optional]
- **Returns:** List - QualityCode objects, one per tag, indicating the result of the operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.query
`system.tag.query([provider], [query], [limit], [continuation])`
Queries a Tag Provider to produce a list of tags that meet the specified criteria.
- **Params:** `String provider` — The Tag Provider to query. Technically optional, but omitting it typically uses the def...; `PyObject query` — An object specifying the query conditions (buildable via the Tag Report Tool).; `Integer limit` — Maximum results to return; if more are possible, a continuation point is included.; `String continuation` — A previously returned continuation point, to continue the query.
- **Returns:** Results - A Results object containing a list of tag dictionaries matching the query.
- **Scope:** Gateway

### system.tag.readAsync
`system.tag.readAsync(tagPaths, callback)`
Asynchronously reads the value of the tags at the given paths.
- **Params:** `List tagPaths` — A List of Tag paths to read from; Value property assumed if none specified.; `Callable callback` — A Python function taking one argument (a List of QualifiedValues) to process the results.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.readBlocking
`system.tag.readBlocking(tagPaths, [timeout])`
Reads the value of the tags at the given paths; blocks until complete or timed out.
- **Params:** `String or List[String] tagPaths` — A single tag path, or a list of tag paths; Value property assumed if none specified.; `Integer timeout` — Milliseconds before the read times out. [optional, default 45000]
- **Returns:** List - QualifiedValue objects corresponding to the tag paths.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.rename
`system.tag.rename(tag, newName, [collisionPolicy])`
Renames a single tag or folder.
- **Params:** `String tag` — A path to the tag or folder to rename.; `String newName` — The new name for the tag or folder.; `String collisionPolicy` — Action to take on a name collision. [optional]
- **Returns:** QualityCode - Result of the rename operation.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.requestGroupExecution
`system.tag.requestGroupExecution(provider, tagGroup)`
Sends a request to the specified tag group to execute now.
- **Params:** `String provider` — Name of the Tag Provider that the tag group is in.; `String tagGroup` — The name of the tag group to execute.
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.writeAsync
`system.tag.writeAsync(tagPaths, values, [callback])`
Asynchronously writes values to tags at specified paths.
- **Params:** `List tagPaths` — A List of tag paths to write to (may include a tag property).; `List values` — The values to write to the specified paths.; `Callable callback` — A function invoked after the write completes. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.tag.writeBlocking
`system.tag.writeBlocking(tagPaths, values, [timeout])`
Writes values to tags at the given paths; blocks until complete or timed out.
- **Params:** `List tagPaths` — A List of tag paths to write to; Value property assumed if none specified.; `List values` — A list of values to write to the specified tag paths.; `Integer timeout` — Milliseconds before the write times out. [optional, default 45000]
- **Returns:** List - QualityCode objects, one per Tag path.
- **Scope:** Gateway, Vision Client, Perspective Session

## system.util
A grab-bag of Gateway/session utilities: process execution, logging (getLogger/setLoggingLevel), JSON (jsonEncode/jsonDecode), inter-scope messaging (sendMessage fire-and-forget, sendRequest/sendRequestAsync request-response), translations, auditing, and diagnostics (getVersion, threadDump, getGatewayStatus). Use invokeAsynchronous to run a Python function off the current (often GUI) thread rather than blocking it; use sendRequestAsync's Request Handle (get/block/onSuccess/onError) instead of sendRequest when the caller should not block waiting for the Gateway's response.

### system.util.audit
`system.util.audit([action], [actionTarget], [actionValue], [auditProfile], [actor], [actorHost], [originatingSystem], [eventTimestamp], [originatingContext], [statusCode])`
Inserts a record into an audit profile.
- **Params:** `String action` — What happened. [optional]; `String actionTarget` — What the action happened to. [optional]; `String actionValue` — The value of the action. [optional]; `String auditProfile` — Where the audit record should be stored; defaults to the project's audit profile. [opti...; `String actor` — Who made the change; auto-populated if omitted and a user is known. [optional]; `String actorHost` — Hostname of whoever made the change; auto-populated if omitted. [optional]; `List[String] originatingSystem` — Even-length list of extra context key/value pairs. [optional]; `Date eventTimestamp` — When the event happened; current time if omitted. [optional]; `Integer originatingContext` — Scope of origin: 1=Gateway, 2=Designer, 4=Client, etc. [optional]; `Integer statusCode` — A quality code to attach; default 0. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.execute
`system.util.execute(commands)`
Executes the given commands via the operating system, in a separate process.
- **Params:** `List[String] commands` — The command (1st entry) and its arguments (remaining entries).
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getGatewayStatus
`system.util.getGatewayStatus(gatewayAddress, [connectTimeoutMillis], [socketTimeoutMillis])`
Returns a string that indicates the status of the Gateway.
- **Params:** `String gatewayAddress` — The Gateway address to ping, in ADDR:PORT form.; `Integer connectTimeoutMillis` — Max time to initially contact the Gateway. [optional]; `Integer socketTimeoutMillis` — Max time to wait for a response after contact. [optional]; `Boolean bypassCertValidation` — For HTTPS addresses, skips certificate validation if True. [optional]
- **Returns:** String - Gateway status; "RUNNING" means fully functional.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getGlobals
`system.util.getGlobals()`
Returns a dictionary that provides access to the legacy global namespace.
- **Params:** None
- **Returns:** Dictionary[String, Any] - The global namespace, as a dictionary.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getLogger
`system.util.getLogger(name)`
Returns a Logger object that can be used to log messages to the console.
- **Params:** `String name` — The name of a logger to create.
- **Returns:** LoggerEx - A new LoggerEx object used to log informational and error messages.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getModules
`system.util.getModules()`
Returns a dataset of information about each installed module.
- **Params:** None
- **Returns:** Dataset - One row per module: Id, Name, Version, State (Running/Faulted/etc.), License Status (Trial/Activated/etc.).
- **Scope:** Gateway

### system.util.getProjectName
`system.util.getProjectName()`
Returns the name of the project that is currently being run.
- **Params:** None
- **Returns:** String - The name of the currently running project.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getProperty
`system.util.getProperty(propertyName)`
Retrieves the value of a named system property.
- **Params:** `String propertyName` — The name of the system property to get.
- **Returns:** String - The value for the named property.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getSessionInfo
`system.util.getSessionInfo([usernameFilter], [projectFilter])`
Returns a PyDataSet holding information about all of the open Designer sessions and Vision Clients.
- **Params:** `String usernameFilter` — Regex filter to restrict the list by username. [optional]; `String projectFilter` — Regex filter to restrict the list by project. [optional]
- **Returns:** Dataset - A dataset representing the Gateway's current sessions.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.getVersion
`system.util.getVersion()`
Returns the Ignition version number that is currently being run.
- **Params:** None
- **Returns:** Version - The running Ignition version, as a Version object exposing `.major`, `.minor`, and `isFutureVersion(versionString)` (compares against a given "X.X.X" version).
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.invokeAsynchronous
`system.util.invokeAsynchronous(function, [args], [kwargs], [description])`
Invokes (calls) the given Python function on a different thread.
- **Params:** `Callable function` — A Python function object to invoke on a newly created thread.; `List[Any] args` — Positional arguments passed to the function. [optional]; `Dictionary[String, Any] kwargs` — Keyword arguments passed to the function. [optional]; `String description` — A description used for the asynchronous thread (shown in diagnostics). [optional]
- **Returns:** Thread - The executing Thread.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.jsonDecode
`system.util.jsonDecode(jsonString)`
Takes a JSON string and converts it into a Python object such as a list or a dictionary.
- **Params:** `String jsonString` — The JSON string to decode into a Python object.
- **Returns:** Any - The decoded Python object (JSON→Python type mapping per the docs table).
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.jsonEncode
`system.util.jsonEncode(pyObj, [indentFactor])`
Takes a Python object such as a list or dictionary and converts it into a JSON string.
- **Params:** `Any pyObj` — The Python object to encode into JSON.; `Integer indentFactor` — Spaces per indentation level for pretty-printing. [optional]
- **Returns:** String - The encoded JSON string.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.modifyTranslation
`system.util.modifyTranslation(term, translation, [locale])`
Adds or modifies a global translation.
- **Params:** `String term` — The key term to translate.; `String translation` — The translated value to store.; `String locale` — The locale for the translation, such as "es" or "en-IE". [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.queryAuditLog
`system.util.queryAuditLog(auditProfileName, [startDate], [endDate], [actorFilter], [actionFilter], [targetFilter], [valueFilter], [systemFilter], [contextFilter])` · `system.util.queryAuditLog([auditProfileName], [startDate], [endDate], [actorFilter], [actionFilter], [targetFilter], [valueFilter], [systemFilter], [contextFilter])`
Queries an audit profile for audit history.
- **Params:** `String auditProfileName` — The audit profile to pull history from.; `Date startDate` — Earliest event to return; defaults to now - 8 hours. [optional]; `Date endDate` — Latest event to return; defaults to now. [optional]; `String actorFilter` — Restricts results by actor. [optional]; `String actionFilter` — Restricts results by action. [optional]; `String targetFilter` — Restricts results by target. [optional]; `String valueFilter` — Restricts results by value. [optional]; `String systemFilter` — Restricts results by originating system. [optional]; `Integer contextFilter` — Bitmask restricting by context: 0x01 Gateway, 0x02 Designer, 0x04 Client, etc.
- **Returns:** Dataset - Audit events from the specified profile matching the filter arguments.
- **Scope:** Gateway, Perspective Session, Vision Client

### system.util.sendMessage
`system.util.sendMessage(project, messageHandler, [payload], [scope], [clientSessionId], [user], [hasRole], [hostName], [remoteServers])`
Sends a message to clients running under the Gateway, or to a project within the Gateway itself. Fire-and-forget (no response).
- **Params:** `String project` — The project containing the message handler.; `String messageHandler` — The message handler that fires upon receiving the message.; `Dictionary[String, Any] payload` — Passed to the message handler as "payload". [optional]; `String scope` — "C" (clients), "G" (Gateway), or "CG" (both). [optional]; `String clientSessionId` — Restricts delivery to a specific client session. [optional]; `String user` — Restricts delivery to clients where the specified user is logged in. [optional]; `String hasRole` — Restricts delivery to clients whose logged-in user has this role. [optional]; `String hostName` — Restricts delivery to the client with this network host name. [optional]; `List remoteServers` — Gateway Server names to also deliver the message to over the Gateway Network. [optional]
- **Returns:** List - Strings describing each system selected for delivery (comma-delimited per item).
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.sendRequest
`system.util.sendRequest(project, messageHandler, [payload], [remoteServer], [timeoutSec])`
Sends a message to the Gateway like sendMessage, but blocks and expects a response.
- **Params:** `String project` — The project containing the message handler.; `String messageHandler` — The message handler that fires upon receiving the message.; `Dictionary[String, Any] payload` — Passed to the message handler as "payload". [optional]; `String remoteServer` — Target Gateway Server name to deliver over the Gateway Network. [optional]; `String timeoutSec` — Seconds before the call times out. [optional]
- **Returns:** Object - The value returned by the message handler.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.sendRequestAsync
`system.util.sendRequestAsync(project, messageHandler, [payload], [remoteServer], [timeoutSec], [onSuccess], [onError])`
Sends a message to the Gateway and expects a response, without blocking; returns a Request Handle immediately.
- **Params:** `String project` — The project containing the message handler.; `String messageHandler` — The message handler that fires upon receiving the message.; `Dictionary[String, Any] payload` — Passed to the message handler as "payload". [optional]; `String remoteServer` — Target Gateway Server name to deliver over the Gateway Network. [optional]; `String timeoutSec` — Seconds before the call times out. [optional]; `Callable onSuccess` — Called with the handler's result on success. [optional]; `Callable onError` — Called with the exception on failure. [optional]
- **Returns:** Request Handle - object with get()/block()/cancel()/getError()/onSuccess()/onError() used to await or attach callbacks to the response.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.setLoggingLevel
`system.util.setLoggingLevel(loggerName, loggerLevel)`
Sets the logging level on the given logger.
- **Params:** `String loggerName` — The unique name of the logger, e.g. "Tags.Client".; `String loggerLevel` — "trace", "debug", "info", "warn" or "error".
- **Returns:** Nothing
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.threadDump
`system.util.threadDump()`
Creates a thread dump of the current running JVM.
- **Params:** None
- **Returns:** String - The dump of the current running JVM.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.util.translate
`system.util.translate(term, [locale], [strict])`
Retrieves the global translation of a term from the translation database using the current locale.
- **Params:** `String term` — The term to look up.; `String locale` — Locale to translate against, e.g. "it" or "en-IE". [optional]; `Boolean strict` — If false, returns the original term when no translation is found instead of erroring. [...
- **Returns:** String - The translated term.
- **Scope:** Gateway, Vision Client, Perspective Session

## Gotchas and 8.3 notes

- **`system.historian` replaces tag-history calls with generic "historical paths."** Reads/writes go through `queryRawPoints`/`queryAggregatedPoints`/`storeDataPoints`/etc. rather than the older tag-history-specific functions, and paths use a distinct path syntax (see the `system.historian` overview page's Path Syntax section) rather than plain tag paths.
- **Several historian query parameters were removed in 8.3.9 but remain accepted for backwards compatibility**, and now silently no-op instead of doing anything: `snapshotTime` (`browse`), `fillModes`/`includeBounds`/`excludeObservations` (`queryAggregatedPoints`), and `includeBounds`/`excludeObservations` (`queryRawPoints`). Scripts written against pre-8.3.9 signatures still run, but should be updated to drop these arguments.
- **Historian query end times are inclusive**, so `queryRawPoints`/`queryAggregatedPoints` can return one extra interval beyond the requested window (interpolated to 0, since it's in the future) — this can throw off trend charts or double-count data when stitching together adjoining query windows; end a window one interval before the next window's start to avoid overlap.
- **`system.config` is Gateway-scope only.** Every function in the namespace (`create`, `replace`, `delete`, `move`, `rename`, `copy`, `getResource(s)`, `getResourceTypes`, `getActiveMode`, `getModes`) will fail if called from a Vision Client or Perspective Session; route these calls through a message handler (`system.util.sendRequest`) if a client needs to trigger one.
- **`system.config` mutating calls use keyword-only parameters** (marked with a leading `*` in the syntax line, e.g. `*moduleId`) — both the parameter name and value must be supplied as a keyword argument in the script (`moduleId="ignition"`), not positionally, and most also require the resource's current `signature` to avoid clobbering concurrent edits.
- **`system.secrets` is part of Ignition's newer Secrets Management system** for encrypted credential storage (embedded or provider-referenced secrets); treat every `PyPlaintext`/decrypted return value as sensitive and avoid writing it back to an unencrypted tag, log, or database column.
- **Datasets are immutable.** Every `system.dataset` call that looks like it mutates (addRow, deleteRow, setValue, sort, filterColumns, updateRow, etc.) actually returns a brand-new Dataset; scripts that don't reassign the result silently keep operating on the original, unmodified dataset.
- **Blocking vs. async tag I/O:** `system.tag.readBlocking`/`writeBlocking` pause the calling thread (default 45000 ms timeout) and should be avoided in UI event handlers that must stay responsive; `readAsync`/`writeAsync` return immediately and deliver results via a callback — prefer these in Vision/Perspective component event scripts.
- **Prefer parameterized SQL.** `system.db.runPrepQuery`/`runPrepUpdate`/`execScalarPrepQuery` (using `?` placeholders) and Named Queries (`execQuery`/`execUpdate`/`execScalar`) avoid SQL injection that string-concatenated queries are vulnerable to; `system.db.runQuery` (not in this reference — it lives under the separate deprecated scripting-functions tree) is deprecated in favor of `runPrepQuery`.
- **`system.db` transactions must be explicitly closed.** A `tx` obtained from `beginTransaction`/`beginNamedQueryTransaction` needs a `commitTransaction` or `rollbackTransaction`, followed by `closeTransaction`, or the underlying database connection can be left open/leaked.
- **`system.math` functions return `NaN`, not an exception, for empty or null input** — always check for `NaN` (e.g. with `system.math.mean(values) != system.math.mean(values)` or a proper `NaN`-check) before using a statistics result downstream; `geometricMean` and `sumLog` also return `NaN` if any input value is negative, since both use natural logarithms internally.
- **`system.date.add*`, `system.date.get*`, and `system.date.*Between` are function families, not single functions.** Each syntax entry (e.g. `system.date.add*(date, value)`) documents an entire group of concrete calls (`addDays`, `addHours`, `addMinutes`, …) that all share one signature and behavior; there is no literal function named `system.date.add*`.
