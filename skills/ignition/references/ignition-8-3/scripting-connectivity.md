# Ignition 8.3 — Device & connectivity scripting functions (opc, opcua, opchda, device, serial, dnp3, bacnet, iec61850, secsgem, mongodb, kafka)

This reference covers the `system.*` scripting namespaces used to talk to devices and external
systems directly from Python scripting, rather than through the Tag system. It is compiled from
the live Ignition 8.3 documentation (docs.inductiveautomation.com/docs/8.3), trimmed to signatures,
parameters, return values and scope.

## How OPC access works in Ignition, and when to script against it directly

Every driver-backed device connection and every OPC UA/DA/HDA server in Ignition is exposed through
an **OPC server connection**. Ignition's own OPC UA Server module exposes device driver connections
(Modbus, Allen-Bradley/Logix, DNP3, BACnet, etc.) as OPC items underneath it, and third-party OPC
servers can be added as their own connections. Every OPC item has two identifying pieces:

- **OPC server name** — the name of the OPC server *connection* as configured in the Gateway (e.g.
  `"Ignition OPC UA Server"`), independent of any Ignition project.
- **Item path** (a.k.a. address) — the path to the specific point on that server, e.g.
  `[MyDevice]N11/N11:0` for a driver point, or a fully qualified OPC UA node path for a UA server.

This is a fundamentally different addressing scheme from **Tags**, which live in the Ignition Tag
Provider hierarchy (`[provider]folder/tagName`) and carry configuration (history, alarms, scaling,
security) on top of a value. Tags are usually backed by an OPC item (an OPC-connected Tag stores its
server name + item path as its OPC Item Path property), but a Tag path and an OPC item path are not
interchangeable — `system.tag.readBlocking` takes tag paths, while `system.opc.*` takes an OPC server
name plus an item path.

**Script against `system.opc`/`system.opcua`/`system.opchda` directly, instead of through Tags, when:**
- You need a value from a point that has **no Tag configured** for it (e.g. an ad hoc diagnostic read,
  or a one-off value while building out a system).
- You are **browsing** a device or server's structure to discover what's available (`system.opc.browse`,
  `system.opc.browseServer`) — for example to dynamically generate Tags.
- You need a **synchronous, blocking round-trip** to the device right now (e.g. `system.opc.readValue`/
  `writeValue`) rather than the cached, scan-class-driven value a Tag read returns.
- You need OPC UA server management operations that have no Tag equivalent: calling a UA method
  (`system.opcua.callMethod`), or adding/removing a UA connection at runtime (`system.opcua.addConnection`/
  `removeConnection`).
- You need OPC **HDA** history (`system.opchda.*`) from a third-party historian-capable OPC server, which
  is a separate access path from Ignition's own Tag History system.

**Prefer Tags** for anything that needs to be visualized, alarmed, historized, or shared across a project
— Tags cache the last good value, apply scaling/engineering units, and don't hit the device on every read.
Direct OPC scripting bypasses all of that and talks straight to the server on every call.

## system.opc

Low-level, synchronous read/write/browse access to any OPC server connection (including Ignition's own OPC UA Server, which fronts every device driver). Use `browseServer` over the fully-recursive `browse`/`browseSimple` for large systems. All reads/writes take an OPC server name plus an item path — see the intro above for how that differs from a Tag path.

### system.opc.browse
`system.opc.browse(opcServer, device, folderPath, opcItemPath)`

Allows browsing of the OPC servers in the runtime, returning a list of tags. Accepts keyword arguments.

**Params:**
- String `opcServer` — The name of the OPC server to browse.
- String `device` — The name of the device to browse.
- String `folderPath` — Filters on a folder path. * = any-length wildcard, ? = single-character wildcard.
- String `opcItemPath` — Filters on an OPC item path. * = any-length wildcard, ? = single-character wildcard.

**Returns:** List[OPCBrowseTag] - Array of OPCBrowseTag objects (getOpcServer(), getOpcItemPath(), getType(), getDisplayName(), getDisplayPath(), getDataType()).

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** Fully recursive and cannot be terminated — the docs recommend system.opc.browseServer instead for large systems, since recursion there is driven by subsequent calls.

### system.opc.browseServer
`system.opc.browseServer(opcServer, nodeId)`

Browses a single level of an OPC server's node tree; caller drives recursion via repeated calls.

**Params:**
- String `opcServer` — The name of the OPC server connection.
- String `nodeId` — The node ID to browse.

**Returns:** List - In Vision Client/Perspective Session/Designer, a list of OPCBrowseElement objects; otherwise a list of PyOPCTagEx objects.

**Scope:** Gateway

### system.opc.browseSimple
`system.opc.browseSimple(opcServer, device, folderPath, opcItemPath)`

Allows browsing of OPC servers in the runtime, returning a list of tags.

**Params:**
- String `opcServer` — The name of the OPC server to browse.
- String `device` — The name of the device to browse.
- String `folderPath` — Filters on a folder path. * = any-length wildcard, ? = single-character wildcard.
- String `opcItemPath` — Filters on an OPC item path. * = any-length wildcard, ? = single-character wildcard.

**Returns:** OPCBrowseTag[] - Array of OPCBrowseTag objects (getOpcServer(), getOpcItemPath(), getType(), getDisplayName(), getDisplayPath(), getDataType()).

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.getServerState
`system.opc.getServerState(opcServer)`

Retrieves the current state of the given OPC server connection.

**Params:**
- String `opcServer` — The name of an OPC server connection.

**Returns:** String - The current state of the connection, or None if the connection doesn't exist.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.getServers
`system.opc.getServers()`

Returns a list of server names.

**Params:**
- Boolean `includeDisabled` — If True, both enabled and disabled servers are returned; if False, only enabled servers.

**Returns:** List - A list of server name strings. If no servers are found, returns an empty list.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.isServerEnabled
`system.opc.isServerEnabled(serverName)`

Checks if an OPC server connection is enabled or disabled.

**Params:**
- String `serverName` — The name of an OPC server connection.

**Returns:** Boolean - True if the connection is enabled, false if disabled.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.readValue
`system.opc.readValue(opcServer, itemPath)`

Reads a single value directly from an OPC server connection.

**Params:**
- String `opcServer` — The name of the OPC server connection in which the item resides.
- String `itemPath` — The item path, or address, to read from.

**Returns:** QualifiedValue - Object containing the value, quality, and timestamp returned from the OPC server for the address specified.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.readValues
`system.opc.readValues(opcServer, itemPaths)`

Equivalent to system.opc.readValue, except that it can operate in bulk.

**Params:**
- String `opcServer` — The name of the OPC server connection in which the items reside.
- List[String] `itemPaths` — A list of strings, each representing an item path, or address, to read from.

**Returns:** List[QualifiedValue] - One QualifiedValue object per address specified, in order.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.setServerEnabled
`system.opc.setServerEnabled(serverName, enabled)`

Enables or disables an OPC server connection.

**Params:**
- String `serverName` — The name of an OPC server connection.
- Boolean `enabled` — The new state: true to enable the connection, false to disable it.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.writeValue
`system.opc.writeValue(opcServer, itemPath, value)`

Writes a value directly through an OPC server connection, synchronously.

**Params:**
- String `opcServer` — The name of the OPC server connection in which the item resides.
- String `itemPath` — The item path, or address, to write to.
- Object `value` — The value to write to the OPC item.

**Returns:** Quality - The status of the write; use returnValue.isGood() to check success.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opc.writeValues
`system.opc.writeValues(opcServer, itemPaths, values)`

Bulk version of system.opc.writeValue.

**Params:**
- String `opcServer` — The name of the OPC server connection in which the items reside.
- List[String] `itemPaths` — A list of item paths, or addresses, to write to.
- List[Any] `values` — A list of values to write, one per address specified.

**Returns:** List[Quality] - One Quality object per address specified, in order.

**Scope:** Gateway, Vision Client, Perspective Session

## system.opcua

OPC UA server/connection *management* from script: add or remove an OPC UA connection at runtime (`addConnection`/`removeConnection`), and invoke a method exposed by a UA server (`callMethod`). This is a small namespace (3 functions) layered on top of `system.opc` for OPC UA specifically.

### system.opcua.addConnection
`system.opcua.addConnection(name, description, discoveryUrl, endpointUrl, securityPolicy, securityMode, settings)`

Adds a new OPC UA connection at runtime.

**Params:**
- String `name` — Name to assign to the new connection.
- String `description` — Description assigned to the new OPC UA connection.
- String `discoveryUrl` — Endpoint URL to use for discovery services.
- String `endpointUrl` — Endpoint URL to use for session services.
- String `securityPolicy` — SecurityPolicy name: None, Basic128Rsa15, Basic256, Basic256Sha256, Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaPss.
- String `securityMode` — MessageSecurityMode name: None, Sign, SignAndEncrypt.
- Dictionary[String, Any] `settings` — Additional connection settings (ENABLED, USERNAME, PASSWORD, timeouts, failover keys, etc).

**Returns:** Nothing

**Scope:** Gateway, Perspective Session

### system.opcua.callMethod
`system.opcua.callMethod(connectionName, objectId, methodId, inputs)`

Calls a method in an OPC UA server.

**Params:**
- String `connectionName` — The name of the OPC UA connection to the server the method resides in.
- String `objectId` — The NodeId of the Object Node the Method is a member of.
- String `methodId` — The NodeId of the Method Node to call.
- List `inputs` — A list of input values expected by the method.

**Returns:** Tuple - (0) resulting StatusCode for the call, (1) list of StatusCode per input argument, (2) list of output values.

**Scope:** Gateway, Perspective Session

### system.opcua.removeConnection
`system.opcua.removeConnection(name)`

Removes an OPC UA connection.

**Params:**
- String `name` — The name of the OPC UA connection to remove.

**Returns:** Boolean - True if the connection was successfully removed, False otherwise.

**Scope:** Gateway, Perspective Session

## system.opchda

Access to OPC **HDA** (Historical Data Access) servers — third-party historians such as Matrikon or Kepware that expose history over the OPC HDA interface, separate from Ignition's own Tag History providers. Covers browsing, reading raw/processed/attribute data, and inserting/replacing history values on the HDA server.

### system.opchda.browse
`system.opchda.browse(root)`

Performs a browse at the given root.

**Params:**
- String `root` — The root at which to browse. Needs to be a qualified path.

**Returns:** BrowseResults[] - The results of the browse operation from the given root.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.getAggregates
`system.opchda.getAggregates(serverName)`

Queries the server for the aggregates it supports.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server to query.

**Returns:** List[Aggregate] - Supported Aggregate objects, each with 'id', 'name', and 'desc' properties.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.getAttributes
`system.opchda.getAttributes(serverName)`

Queries the server for item attributes available via system.opchda.readAttributes.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server to query.

**Returns:** List[AttributeInfo] - A list of AttributeInfo objects.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.getServers
`system.opchda.getServers()`

Returns a list of the OPC-HDA servers configured on the system.

**Params:** none

**Returns:** List[String] - A list of the string names of servers.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.insert
`system.opchda.insert(serverName, itemId, value, date, quality)`

Inserts values on the OPC-HDA server.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server.
- String `itemId` — The item ID to perform the operation on.
- Any `value` — The value to insert.
- Any `date` — The date to insert.
- Integer `quality` — The quality to insert.

**Returns:** QualityCode - The result of the insert.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.insertReplace
`system.opchda.insertReplace(serverName, itemId, value, date, quality)`

Inserts values on the OPC-HDA server, or replaces them if they already exist.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server.
- String `itemId` — The item ID to perform the operation on.
- Object `value` — The value to insert or replace.
- Object `date` — The date to insert or replace.
- QualityCode `quality` — The quality to insert or replace.

**Returns:** QualityCode - The result of the insert or replace operation.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.isServerAvailable
`system.opchda.isServerAvailable()`

Checks whether the specified OPC-HDA server is defined, enabled, and connected.

**Params:**
- String `serverName` — The name of the OPC-HDA server to check.

**Returns:** Boolean - True if the server is available and can be queried, false otherwise.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.readAttributes
`system.opchda.readAttributes(serverName, itemId, attributeIds, startDate, endDate)`

Reads the specified attributes for the given item over a time range.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server to read.
- String `itemId` — The itemID to retrieve attributes for.
- List[String] `attributeIds` — The integer IDs of the attributes to read, as defined by the OPC-HDA spec.
- Object `startDate` — The starting date/time of the query (string or other date-like type).
- Object `endDate` — The ending date/time of the query (string or other date-like type).

**Returns:** List[ReadResults] - One-to-one with the requested attributes; each has a serviceResult quality property.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.readProcessed
`system.opchda.readProcessed(serverName, itemIds, startDate, endDate, resampleIntervalMS, aggregates)`

Reads processed (aggregated/resampled) values from the OPC-HDA server.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server to read.
- List[String] `itemIds` — A list of item ids to read.
- Object `startDate` — The starting date/time of the query.
- Object `endDate` — The ending date/time of the query.
- Integer `resampleIntervalMS` — The interval, in milliseconds, that each value should cover.
- List[Integer] `aggregates` — One-to-one with itemIds, specifying the aggregate id to apply per item.

**Returns:** List[ReadResults] - One-to-one with the item IDs passed in; each has a serviceResult quality property.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.readRaw
`system.opchda.readRaw(serverName, itemIds, startDate, endDate, maxValues, boundingValues)`

Reads raw (unprocessed) values from the OPC-HDA server.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server to read.
- List `itemIds` — A list of item ids to read.
- Object `startDate` — The starting date/time of the query.
- Object `endDate` — The ending date/time of the query.
- Integer `maxValues` — Maximum number of values to return; 0 or less means unlimited.
- Boolean `boundingValues` — Whether "bounding values" should be included in the results.

**Returns:** List[ReadResults] - One-to-one with the item IDs passed in; each has a serviceResult quality property.

**Scope:** Gateway, Vision Client, Perspective Session

### system.opchda.replace
`system.opchda.replace(serverName, itemId, value, date, quality)`

Replaces values on the OPC-HDA server if the given item ID exists.

**Params:**
- String `serverName` — The name of the defined OPC-HDA server.
- String `itemId` — The item ID to perform the operation on.
- Object `value` — The value to replace.
- Object `date` — The date to replace.
- Integer `quality` — The quality to replace.

**Returns:** Integer - The item's quality resulting from the operation.

**Scope:** Gateway, Vision Client, Perspective Session

## system.device

Manage device *connections* themselves in the Gateway (add, remove, enable/disable, restart, rename hostname, list, force a browse) — as opposed to reading/writing values through them, which goes through `system.opc`/Tags. `addDevice` requires keyword arguments and a `deviceProps` dictionary whose keys vary per driver type (see the full deviceProps key listing in the docs' system-device-addDevice-deviceProps-Listing page, not reproduced here).

### system.device.addDevice
`system.device.addDevice(deviceType, deviceName, deviceProps, [description])`

Adds a new device connection in Ignition.

**Params:**
- String `deviceType` — The device driver type. Possible values are listed in the Device Types table below.
- String `deviceName` — The name that will be given to the new device connection.
- Dictionary[String, Any] `deviceProps` — A dictionary of device connection properties and values. Each deviceType has different pr…
- String `description` — The description that will be given to the new device connection. [optional]

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.getDeviceHostname
`system.device.getDeviceHostname()`

Returns the hostname of the device.

**Params:**
- String `deviceName` — The name of the device in Ignition.

**Returns:** The hostname of the device. The value will display null if the device doesn't have a hostname.

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.listDevices
`system.device.listDevices()`

Returns a dataset of information about each configured device.

**Params:** none

**Returns:** Dataset - A dataset, where each row represents a device. Contains 4 columns: - Name - Enabled - State - Driver

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.refreshBrowse
`system.device.refreshBrowse(deviceName)`

Forces Ignition to browse the controller.

**Params:**
- String `deviceName` — The name of the device in Ignition.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.removeDevice
`system.device.removeDevice(deviceName)`

Removes a given device from Ignition.

**Params:**
- String `deviceName` — The name of the device in Ignition.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.restart
`system.device.restart(deviceName)`

Restarts the named device connection.

**Params:**
- String `deviceName` — The name of the device connection to restart. The function will throw an error if the spe…

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.setDeviceEnabled
`system.device.setDeviceEnabled(deviceName, enabled)`

Enables/disables a device in Ignition.

**Params:**
- String `deviceName` — The name of the device in Ignition.
- Boolean `enabled` — Specifies whether the device connection will be set to enabled or disabled state.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.device.setDeviceHostname
`system.device.setDeviceHostname(deviceName, hostname)`

Changes the hostname of a device. Used for all ethernet based drivers.

**Params:**
- String `deviceName` — The name of the device in Ignition.
- String `hostname` — The new IP address or hostname.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

## system.serial

Direct read/write access to serial (RS-232/RS-485) ports from Gateway or Client scope: configure a port, then read bytes/lines/until-delimiter or write bytes/strings. `system.serial.port` returns a context manager (`with` block) that closes the port automatically; the open/close/read/write functions are the lower-level, manual-lifecycle alternative.

### system.serial.closeSerialPort
`system.serial.closeSerialPort(port)`

Closes a previously opened serial port.

**Params:**
- String `port` — The name of the serial port, e.g. "COM1" or "/dev/ttyS0".

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.configureSerialPort
`system.serial.configureSerialPort(port, [bitRate], [dataBits], [hardwareFlowControl], [parity], [stopBits])`

Configures a serial port for use in a later call.

**Params:**
- String `port` — The name of the serial port, e.g. "COM1" or "/dev/ttyS0". Required.
- Integer `bitRate` — Bit rate; valid values defined by system.serial constants. [optional]
- Integer `dataBits` — Data bits; valid values defined by system.serial constants. [optional]
- Boolean `hardwareFlowControl` — Hardware flow control on/off. [optional]
- Integer `parity` — Parity; valid values defined by system.serial constants. [optional]
- Integer `stopBits` — Stop bits; valid values defined by system.serial constants. [optional]

**Returns:** SerialConfigurator - Object with functions to configure the port instead of, or in addition to, the arguments.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.openSerialPort
`system.serial.openSerialPort(port)`

Opens a previously configured serial port for use.

**Params:**
- String `port` — The name of the serial port, e.g. "COM1" or "/dev/ttyS0".

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.port
`system.serial.port(port, [bitRate], [dataBits], [handshake], [hardwareFlowControl], [parity], [stopBits])`

Returns a context manager wrapping a serial port for use with a Python `with` statement.

**Params:**
- String `port` — The name of the serial port, e.g. "COM1" or "/dev/ttyS0". Required.
- Integer `bitRate` — Bit rate; valid values defined by system.serial constants. [optional]
- Integer `dataBits` — Data bits; valid values defined by system.serial constants. [optional]
- Boolean `hardwareFlowControl` — Hardware flow control on/off. [optional]
- Integer `parity` — Parity; valid values defined by system.serial constants. [optional]
- Integer `stopBits` — Stop bits; valid values defined by system.serial constants. [optional]

**Returns:** PortManager - Wrapper around the configured port; closes automatically on exiting the `with` block.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.readBytes
`system.serial.readBytes(port, numberOfBytes [, timeout])`

Reads numberOfBytes bytes from a serial port.

**Params:**
- String `port` — The previously configured serial port to use.
- Int `numberOfBytes` — The number of bytes to read.
- Int `timeout` — Max time in milliseconds to block before returning. Default 5000. [optional]

**Returns:** List[Byte] - Bytes read from the serial port.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.readBytesAsString
`system.serial.readBytesAsString(port, numberOfBytes, [timeout], [encoding])`

Reads numberOfBytes bytes from a serial port and converts them to a String.

**Params:**
- String `port` — The previously configured serial port to use.
- Integer `numberOfBytes` — The number of bytes to read.
- Integer `timeout` — Max time in milliseconds to block before returning. Default 5000. [optional]
- String `encoding` — Encoding to use when constructing the string. Defaults to platform default. [optional]

**Returns:** String - A String created from the bytes read.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.readLine
`system.serial.readLine(port [, timeout] [, encoding])`

Attempts to read a line from a serial port.

**Params:**
- String `port` — The previously configured serial port to use.
- Integer `timeout` — Max time in milliseconds to block before returning. Default 5000. [optional]
- String `encoding` — The String encoding to use. Default UTF8. [optional]

**Returns:** String - A line of text.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.readUntil
`system.serial.readUntil(port, delimiter, includeDelimiter, [timeout])`

Reads a byte at a time from a serial port until a delimiter character is encountered.

**Params:**
- String `port` — The previously configured serial port to use.
- Char `delimiter` — The delimiter to read until.
- Boolean `includeDelimiter` — If true, the delimiter is included in the return value.
- Integer `timeout` — Timeout in milliseconds. Default 5000. [optional]

**Returns:** String - ASCII characters read until the delimiter, including it if includeDelimiter is true.

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.sendBreak
`system.serial.sendBreak(port, millis)`

Sends a break signal for approximately millis milliseconds.

**Params:**
- String `port` — The name of the serial port, e.g. "COM1" or "/dev/ttyS0".
- Integer `millis` — Approximate length of break signal, in milliseconds.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.write
`system.serial.write(port, toWrite, [timeout], [encoding])`

Writes a String to a serial port using the platform's default character encoding.

**Params:**
- String `port` — The previously configured serial port to use.
- String `toWrite` — The String to write.
- Integer `timeout` — Timeout in milliseconds for the write. Default 5000. [optional]
- String `encoding` — Encoding to decode the string with, e.g. UTF-8. Default platform default. [optional]

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

### system.serial.writeBytes
`system.serial.writeBytes(port, toWrite)`

Writes a List[Byte] to a serial port.

**Params:**
- String `port` — The previously configured serial port to use.
- List[Byte] `toWrite` — The List[Byte] to write.

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session

## system.dnp / system.dnp3 — two parallel DNP3 scripting namespaces

Ignition 8.3 ships **two** DNP3 driver implementations with two separate scripting namespaces, and the docs cross-link every function page between them:

- **`system.dnp`** — works with the newer **DNP3 driver**.
- **`system.dnp3`** — works with the **Legacy DNP3 driver**.

Every function page in both namespaces carries an explicit docs note pointing at its counterpart (e.g. the `system.dnp.demandPoll` page says: *"The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3."*). Match your scripting namespace to whichever DNP3 driver type the device connection actually uses — the two are not interchangeable, and `system.dnp` is not simply a renamed/newer version of every `system.dnp3` call (parameter shapes differ in places, e.g. `directOperateBinary`'s argument order).

**system.dnp (DNP3 driver):**

### system.dnp.demandPoll
`system.dnp.demandPoll(deviceName, classList)`

Issues a poll request for one or more classes.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- List `classList` — A List of classes (1, 2, 3) to issue polls.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.directOperateAnalog
`system.dnp.directOperateAnalog(deviceName, variation, index, value)`

Performs a Direct Operate command on an analog point.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Integer `variation` — The Group 41 variation to use during the operation.
- Integer `index` — The index of the analog point.
- Numeric `value` — The requested value.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.directOperateBinary
`system.dnp.directOperateBinary(deviceName, index, tcc, opType, count, onTime, offTime)`

Performs a Direct Operate command on a binary point.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Integer `index` — The index of the binary point.
- Integer `tcc` — Trip Close Code: 0=NUL, 1=CLOSE, 2=TRIP.
- Integer `opType` — Operation Type: 0=NUL, 1=PULSE_ON, 2=PULSE_OFF, 3=LATCH_ON, 4=LATCH_OFF.
- Integer `count` — The number of times the outstation shall execute the operation.
- Integer `onTime` — Duration (in milliseconds) the output drive remains active.
- Integer `offTime` — Duration (in milliseconds) the output drive remains non-active.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeAnalogs
`system.dnp.freezeAnalogs(deviceName, indexes)`

Issues an Immediate Freeze command targeting one or more analog points.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- List `indexes` — The indices of the analog points to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeAtTimeAnalogs
`system.dnp.freezeAtTimeAnalogs(deviceName, absoluteTime, intervalTime, indexes)`

Issues a Freeze at Time command targeting one or more analog points.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Long `absoluteTime` — Absolute time (in milliseconds since epoch UTC) when the initial action should occur.
- Long `intervalTime` — Interval time (in milliseconds) between periodic actions.
- List `indexes` — The indices of the analog points to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeAtTimeCounters
`system.dnp.freezeAtTimeCounters(deviceName, absoluteTime, intervalTime, indexes)`

Issues a Freeze at Time command targeting one or more counters.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Long `absoluteTime` — Absolute time (in milliseconds since epoch UTC) when the initial action should occur.
- Long `intervalTime` — Interval time (in milliseconds) between periodic actions.
- List `indexes` — The indices of the counters to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeClearAnalogs
`system.dnp.freezeClearAnalogs(deviceName, indexes)`

Issues a Freeze and Clear command targeting one or more analog points.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- List `indexes` — The indices of the analog points to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeClearCounters
`system.dnp.freezeClearCounters(deviceName, indexes)`

Issues a Freeze and Clear command targeting one or more counters.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- List `indexes` — The indices of the counters to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.freezeCounters
`system.dnp.freezeCounters(deviceName, indexes)`

Issues an Immediate Freeze command targeting one or more counters.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- List `indexes` — The indices of the counters to freeze.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.selectOperateAnalog
`system.dnp.selectOperateAnalog(deviceName, variation, index, value)`

Performs a Select then Operate command on an analog point.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Integer `variation` — The Group 41 variation to use during the operation.
- Integer `index` — The index of the analog point.
- Numeric `value` — The requested value.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.selectOperateBinary
`system.dnp.selectOperateBinary(deviceName, index, tcc, opType, count, onTime, offTime)`

Performs a Select then Operate command on a binary point.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.
- Integer `index` — The index of the binary point.
- Integer `tcc` — Trip Close Code: 0=NUL, 1=CLOSE, 2=TRIP.
- Integer `opType` — Operation Type: 0=NUL, 1=PULSE_ON, 2=PULSE_OFF, 3=LATCH_ON, 4=LATCH_OFF.
- Integer `count` — The number of times the outstation shall execute the operation.
- Integer `onTime` — Duration (in milliseconds) the output drive remains active.
- Integer `offTime` — Duration (in milliseconds) the output drive remains non-active.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

### system.dnp.synchronizeTime
`system.dnp.synchronizeTime(deviceName)`

Issues a Synchronize Time command using the current Ignition Gateway time.

**Params:**
- String `deviceName` — The name of the DNP3 device instance.

**Returns:** Nothing.

**Scope:** Gateway
**Note:** The following function uses system.dnp and the DNP3 driver. For system.dnp3 functions and the Legacy DNP3 driver, see DNP3.

**system.dnp3 (Legacy DNP3 driver):**

### system.dnp3.directOperateAnalog
`system.dnp3.directOperateAnalog(deviceName, index, value, [variation])`

Issues a Select-And-Operate command to set an analog value in an analog output point.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- Integer `index` — The index of the object to be modified in the outstation.
- Numeric `value` — The analog value that is requested (of type int, short, float, or double).
- Integer `variation` — The DNP3 object variation to use in the request.

**Returns:** Integer - The DNP3 status code of the response, as an integer.

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.directOperateBinary
`system.dnp3.directOperateBinary(deviceName, indexes, opType, tcCode, count, onTime, offTime)`

Issues a Direct-Operate command for digital control operations at binary output points (CROB).

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- List `indexes` — A list of indexes of the objects to be modified in the outstation.
- Integer `opType` — The type of the operation. 0=NUL, 1=PULSE_ON, 2=PULSE_OFF, 3=LATCH_ON, 4=LATCH_OFF
- Integer `tcCode` — The Trip-Close code, used in conjunction with the opType. 0=NUL, 1=CLOSE, 2=TRIP
- Integer `count` — The number of times the outstation shall execute the operation.
- Long `onTime` — The duration that the output drive remains active, in millis. [optional]
- Long `offTime` — The duration that the output drive remains non-active, in millis. [optional]

**Returns:** The DNP3 status code of the response, as an integer.

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.freezeAnalogs
`system.dnp3.freezeAnalogs(deviceName, [indexes])`

Issues a freeze command on the given analog outputs.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- List `indexes` — A list of specific indexes on which to issue the freeze command. An empty list can be pas…

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.freezeAnalogsAtTime
`system.dnp3.freezeAnalogsAtTime(deviceName, absoluteTime, intervalTime, indexes)`

Issues a freeze command on the given analog outputs at the given time for the specified duration.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- Integer `absoluteTime` — The absolute time at which to freeze, in millis.
- Integer `intervalTime` — The interval at which to periodically freeze, in millis.
- List `indexes` — A list of specific indexes on which to issue the freeze command. An empty list will freez…

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.freezeCounters
`system.dnp3.freezeCounters(deviceName, [indexes])`

Issues a freeze command on the given counters.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- List `indexes` — A list of specific indexes on which to issue the freeze command. An empty list can be pas…

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.freezeCountersAtTime
`system.dnp3.freezeCountersAtTime(deviceName, absoluteTime, intervalTime, indexes)`

Issues a freeze command on the given counters at the given time for the specified duration.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- Integer `absoluteTime` — The absolute time at which to freeze, in millis.
- Integer `intervalTime` — The interval at which to periodically freeze, in millis.
- List `indexes` — A list of specific indexes on which to issue the freeze command. An empty list will freez…

**Returns:** Nothing

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.selectOperateAnalog
`system.dnp3.selectOperateAnalog(deviceName, index, value, [variation])`

Issues a Select-And-Operate command to set an analog value in an analog output point.

**Params:**
- String `deviceName` — The name of the DNP3 device driver.
- Integer `index` — The index of the object to be modified in the outstation.
- Numeric `value` — The analog value that is requested (of type int, short, float, or double).
- Integer `variation` — The DNP3 object variation to use in the request. [optional]

**Returns:** The DNP3 status code of the response, as an integer.

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

### system.dnp3.selectOperateBinary
`system.dnp3.selectOperateBinary(deviceName, indexes, opType, tcCode, [count], [onTime], [offTime])`

Issues a Select-And-Operate command for digital control operations at binary output points (CROB).

**Params:**
- String `deviceName` — The name of the DNP3 driver.
- List `indexes` — A list of indexes of the objects to be modified in the outstation.
- Integer `opType` — The type of operation. 0=NUL, 1=PULSE_ON, 2=PULSE_OFF, 3=LATCH_ON, 4=LATCH_OFF
- Integer `tcCode` — The Trip-Close code, used in conjunction with the opType. 0=NUL, 1=CLOSE, 2=TRIP
- Integer `count` — The number of times the outstation shall execute the operation. [optional]
- Integer `onTime` — The duration that the output drive remains active, in millis. [optional]
- Integer `offTime` — The duration that the output drive remains non-active, in millis. [optional]

**Returns:** The DNP3 status code of the response, as an integer.

**Scope:** Gateway, Vision Client, Perspective Session
**Note:** The following function uses system.dnp3 and the Legacy DNP3 driver. See system.dnp for DNP3 functions using the DNP3 driver.

## system.bacnet

Raw BACnet/IP object access for objects/properties not explicitly modeled by the BACnet driver's own item types: read/write arbitrary object type + instance + property combinations (singly or in bulk), synchronize device time, and write with a specific command priority. `system.bacnet` also exposes `objectType`/`propertyId`/Enums packages so scripts can import BACnet4J enum classes without knowing their full Java path (see `system.bacnet.readRaw`'s Importing Classes section).

### system.bacnet.readRaw
`system.bacnet.readRaw(deviceName, objectType, objectId, propertyId, [propertyArrayIndex])`

Read from any BACnet object not explicitly supported by the BACnet driver.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to read from.
- ObjectType `objectType` — The numeric id of the objectType of the object instance being read from. See the objectTy…
- Integer `objectId` — The object instance number to read.
- PropertyIdentifier `propertyId` — The PropertyIdentifier of the object instance being read. See the propertyId Reference be…
- Integer `propertyArrayIndex` — [optional] The array index of the property to read from. This parameter is optional and s…

**Returns:** Nothing

**Scope:** Gateway

### system.bacnet.readRawMultiple
`system.bacnet.readRawMultiple(deviceName, objectTypes, objectIds, propertyIds)`

This function is the bulk version of system.bacnet.readRaw to allow multiple object/property combinations to be read simultaneously from a single request.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to read from.
- ObjectTypes `objectTypes` — The numeric ids of the objectType of the object instances being read from. See the object…
- Integer `objectIds` — The object instance number to read.
- PropertyIdentifier `propertyIds` — The PropertyIdentifier of the object instance being read. See the propertyId Reference be…

**Returns:** A list of Encodable objects corresponding to the properties being read.

**Scope:** Gateway

### system.bacnet.synchronizeTime
`system.bacnet.synchronizeTime(deviceName)`

Notifies the remote device of the correct current time, which is the system time (factoring in time zone and DST) of the server Ignition is running on.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to write from.

**Returns:** Nothing

**Scope:** Gateway, Perspective Session

### system.bacnet.synchronizeTimeUtc
`system.bacnet.synchronizeTimeUtc(deviceName)`

Notifies the remote device of the correct current time in UTC.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to write from.

**Returns:** Nothing

**Scope:** Gateway, Perspective Session

### system.bacnet.writeRaw
`system.bacnet.writeRaw(deviceName, objectType, objectId, propertyId, value, [priority], [propertyArrayIndex])`

Write to any BACnet object not explicitly supported by the BACnet driver.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to write from.
- ObjectType `objectType` — The numeric id of the objectType of the object instance being written to. See the objectT…
- Integer `objectId` — The object instance number to write to.
- PropertyIdentifier `propertyId` — The PropertyIdentifier of the object instance being written to. See the propertyId Refere…
- Object `value` — The value to write. Clearing a value can be accomplished by writing a None value.
- Integer `priority` — [optional] The priority level to use when writing to commandable properties. Must match a…
- Integer `propertyArrayIndex` — [optional] The array index of the property to write to. This parameter is optional and sh…

**Returns:** Nothing

**Scope:** Gateway

### system.bacnet.writeRawMultiple
`system.bacnet.writeRawMultiple(deviceName, objectTypes, objectIds, propertyIds, values, [priorities], [propertyArrayIndices])`

This function is the bulk version of system.bacnet.writeRaw by writing properties to objects provided equal-length lists of object types, object instance numbers, property IDs, values, priorities, and property array indices.

**Params:**
- String `deviceName` — Name of the configured BACnet/IP device instance to write from.
- ObjectType `objectTypes` — A list of ObjectType(s) for the object instance being written to.
- Integer `objectIds` — A list of object instance numbers to write to.
- PropertyIdentifier `propertyIds` — A list of PropertyIdentifier(s) for the object instances being written to.
- Object `values` — A list of values to write.
- Integer `priorities [optional]` — An optional list of priority levels to use when writing to commandable properties. All el…
- Integer `propertyArrayIndices [optional]` — An optional list of array indices corresponding to array properties being written. None s…

**Returns:** No return value.

**Scope:** Gateway

### system.bacnet.writeWithPriority
`system.bacnet.writeWithPriority(deviceName, objectType, objectId, value, priority)`

Write to the Present_Value attribute of an object with a custom priority level.

**Params:**
- String `deviceName` — The name of the configured BACnet/IP device instance to write from.
- Integer `objectType` — The numeric id of the objectType of the object instance being written to. See the objectT…
- Integer `objectId` — The object instance number to write to.
- Object `value` — The value to write. Clearing a value can be accomplished by writing a None value.
- Integer `priority` — The priority level to write the value at. Must match a level in the standard BACnet prior…

**Returns:** Nothing

**Scope:** Gateway, Perspective Session

## system.iec61850

Scripted control and file transfer against IEC 61850 IEDs (substation devices): select/operate/cancel for SBO (select-before-operate) controls, read control parameters, and list/read/write files on the device. **Safety-critical**: the docs carry an explicit danger callout that misuse of the Check parameter (see `getControlParams`) bypassing an IED's Control Interlock (CILO) / Synchrocheck (RSYN) logical nodes can cause unintended high-voltage switching operations.

### system.iec61850.cancel
`system.iec61850.cancel(deviceName, mapParams)`

Cancels the selection of an SBO type control on a configured IEC 61850 device to prevent the operate command from performing.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- PyDictionary `mapParams` — Control parameters dictionary that requires the following keys to be specified: name, T,…

**Returns:** No return value.

**Scope:** Gateway, Perspective Session
**Note:** Docs typo — the Syntax code block on this page literally reads `system.iec81650.cancel(...)` (digits transposed); the function is `system.iec61850.cancel`.

### system.iec61850.getControlParams
`system.iec61850.getControlParams(deviceName)`

This function returns a list of report control names and their attributes contained in the configured IEC 61850 device.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.

**Returns:** List[PyDictionary] - A list of PyDictionaries, where each dictionary contains keys such as: name (logical device pathname), ctlModel, and related control attributes.

**Scope:** Gateway, Perspective Session
**Note:** Docs typo — the Syntax code block on this page literally reads `system.iec81650.getControlParams(...)` (digits transposed); the function is `system.iec61850.getControlParams`.

### system.iec61850.listFiles
`system.iec61850.listFiles(deviceName, remoteFilePath)`

This function returns a list of filenames from a remote path for the configured IEC 61850 device.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- String `remoteFilePath` — The remote file path on the server of the configured IEC 61850 device for the file to rea…

**Returns:** No return value.

**Scope:** Gateway, Perspective Session

### system.iec61850.operate
`system.iec61850.operate(deviceName, mapParams, controlValue)`

This function operates on the IEC 61850 device control immediately, such as to change the position of a switch.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- PyDictionary `mapParams` — Control parameters dictionary that requires the following keys to be specified: name, T,…
- Float `controlValue` — Control value (32-bit float).

**Returns:** No return value.

**Scope:** Gateway, Perspective Session

### system.iec61850.readFile
`system.iec61850.readFile(deviceName, remoteFilePath, localFilePath)`

This function downloads remote files from the configured IEC 61850 device to an identified local path.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- String `remoteFilePath` — The remote file path on the server of the file to read.
- String `localFilePath` — The local file path on client to store the file contents.

**Returns:** No return value.

**Scope:** Gateway, Perspective Session

### system.iec61850.select
`system.iec61850.select(device_name, mapParams, value)`

Select an SBO type control to prepare it for a subsequent operate command for a configured IEC 61850 device.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- PyDictionary `mapParams` — Control parameters dictionary that requires the following keys to be specified: name, T,…
- Float `controlValue` — Control value (32-bit float).

**Returns:** No return value.

**Scope:** Gateway, Perspective Session

### system.iec61850.writeFile
`system.iec61850.writeFile(deviceName, localFilePath, remoteFilePath)`

This function uploads a file from a local path to the configured IEC 61850 device remote path.

**Params:**
- String `deviceName` — The name of the configured IEC 61850 device.
- String `localFilePath` — The local file path on client to pull the file contents from.
- String `remoteFilePath` — The remote file path on the server of the file to write to.

**Returns:** No return value.

**Scope:** Gateway, Perspective Session

## system.secsgem

Scripting for the SECS/GEM module (semiconductor/electronics equipment communication) — requires the SECS/GEM module to be installed. Send/receive SECS messages and responses, manage equipment connections (copy, enable/disable), manage process programs (tool programs), run simulator event runs, and convert SECS message objects to Datasets (including a tree-view-ready form).

### system.secsgem.deleteToolProgram
`system.secsgem.deleteToolProgram(ppid)`

Deletes a process program from the Gateway.

**Params:**
- String `ppid` — The PPID that was sent from the tool when the S7F3 message was saved.

**Returns:** Nothing

**Scope:** Vision Client
**Note:** This page's URL slug is misspelled `system-secgem-deleteToolProgram` in the docs site's own directory structure, but the function itself is `system.secsgem.deleteToolProgram`.

### system.secsgem.copyEquipment
`system.secsgem.copyEquipment(equipmentSource, newEquipmentName, enabled, activeAddress, activePort, passiveAddress, passivePort, deviceId [, dbTablePrefix] [, description])`

Creates a copy of an equipment connection.

**Params:**
- String `equipmentSource` — Existing equipment connection whose settings seed the new one.
- String `newEquipmentName` — The name of the new equipment connection.
- Boolean `enabled` — If False, the new equipment connection is disabled after creation.
- String `activeAddress` — IP address of new equipment; required if SECS/GEM module is in Active mode.
- Integer `activePort` — Port number of new equipment; required if SECS/GEM module is in Active mode.
- String `passiveAddress` — IP address of new equipment; required if SECS/GEM module is in Passive mode.
- Integer `passivePort` — Port number of new equipment; required if SECS/GEM module is in Passive mode.
- Integer `deviceId` — Unique integer identifier of the new equipment.
- String `dbTablePrefix` — Prefix for SECS/GEM database table names for the new equipment. [optional]
- String `description` — Description for the new equipment connection. [optional]

**Returns:** Nothing

**Scope:** Vision Client

### system.secsgem.enableDisableEquipment
`system.secsgem.enableDisableEquipment(enable, names)`

Enables or disables a Tuple of equipment connections from a script.

**Params:**
- Boolean `enable` — True to enable the equipment connections, False to disable them.
- Tuple `names` — A Tuple of Strings, each matching an Equipment Connection configured on the Gateway.

**Returns:** List - Messages about connections that could not be enabled/disabled; empty if all succeeded.

**Scope:** Vision Client

### system.secsgem.getResponse
`system.secsgem.getResponse(transactionID, equipment, [timeout], [poll])`

Attempts to retrieve a response message from the Gateway.

**Params:**
- Integer `transactionID` — The transactionID of the request/response pair to retrieve.
- String `equipment` — Name of equipment connection.
- Integer `timeout` — Seconds to wait for a response before returning None. [optional]
- Integer `poll` — Milliseconds between polls of the system for a response. [optional]

**Returns:** Any - A Python object (typically a dictionary) decoded from the response's JSON string.

**Scope:** Gateway, Vision Client, Perspective Session

### system.secsgem.getToolProgram
`system.secsgem.getToolProgram(ppid)`

Returns a process program from the Gateway previously sent by a tool in an S7F3 message.

**Params:**
- String `ppid` — The PPID that was sent from the tool when the S7F3 message was saved.

**Returns:** Dictionary - Keys: editDate, ppbody, bodyFormat.

**Scope:** Vision Client

### system.secsgem.getToolProgramDataset
`system.secsgem.getToolProgramDataset()`

Returns a Dataset containing information about all stored process programs.

**Params:** none

**Returns:** Dataset - Columns: ppid, editDate, bodyFormat.

**Scope:** Vision Client

### system.secsgem.sendRequest
`system.secsgem.sendRequest(streamFunction, reply, body, equipment)`

Sends a JSON-formatted SECS message to a tool.

**Params:**
- String `streamFunction` — The stream and function of the SECS message to send, e.g. "S1F13".
- Boolean `reply` — Whether the SECS message expects a reply message.
- Object `body` — The body of the SECS message, as a Python object or JSON string.
- String `equipment` — Name of the equipment connection to use.

**Returns:** Integer - The transactionID of the SECS message response.

**Scope:** Gateway, Vision Client, Perspective Session

### system.secsgem.sendResponse
`system.secsgem.sendResponse(transactionID, systemBytes, streamFunction, body, equipment)`

Sends a JSON-formatted SECS response message to a message sent by a tool.

**Params:**
- Integer `transactionID` — The TxID of the response, taken from the received request.
- Integer `systemBytes` — The SystemBytes of the response, taken from the received request.
- String `streamFunction` — The stream and function of the SECS message to send, e.g. "S1F14".
- Any `body` — The body of the SECS response, as a Python object or JSON string.
- String `equipment` — Name of the equipment connection to use.

**Returns:** Nothing

**Scope:** Gateway, Perspective Session

### system.secsgem.startSimEventRun
`system.secsgem.startSimEventRun(simulatorName, eventRunName)`

Starts a configured simulator event run in the Gateway.

**Params:**
- String `simulatorName` — The simulator holding the configured event run; throws if not found.
- String `eventRunName` — The event run to start; throws if the simulator can't be found.

**Returns:** Nothing

**Scope:** Vision Client

### system.secsgem.toDataset
`system.secsgem.toDataset(secsObject)`

Converts a SECS message data structure (as returned by system.secsgem.getResponse) into a dataset.

**Params:**
- Any `secsObject` — A Python object (e.g. Sequence or Dictionary) representing a SECS message to convert.

**Returns:** DataSet - A Dataset representing a SECS message.

**Scope:** Gateway, Vision Client, Perspective Session

### system.secsgem.toTreeDataset
`system.secsgem.toTreeDataset(dataset)`

Changes an existing dataset (as returned by system.secsgem.toDataset) for use with the Tree View component.

**Params:**
- Dataset `dataset` — A DataSet containing a SECS message; cannot take a raw JSON message.

**Returns:** Dataset - Columns suited for Vision's tree view: "path", "text", "icon", "background", "foreground", etc.

**Scope:** Gateway, Vision Client, Perspective Session

## system.mongodb

CRUD and aggregation against a MongoDB instance through a configured **MongoDB connector** (`find`/`findOne`/`insertOne`/`insertMany`/`updateOne`/`updateMany`/`replaceOne`/`deleteOne`/`deleteMany`/`aggregate`), plus connector/collection introspection (`listConnectorInfo`, `listCollectionNames`). All functions take a `connector` name (case-insensitive) and `collection` name (case-sensitive) as the first two arguments; filters/updates/projections are PyDictionaries modeled directly on MongoDB's own query/update document syntax.

### system.mongodb.aggregate
`system.mongodb.aggregate(connector, collection, aggregate, [collation])`

Returns a list of aggregate results.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- List[PyDictionary] `aggregate` — A list of PyDictionaries to specify an aggregate pipeline. See MongoDB documentation.
- PyDictionary `collation` — A PyDictionary of items to specify language-specific rules. See MongoDB docs. [optional]

**Returns:** List[PyDictionary] `result` - A list of PyDictionary results containing aggregation results.

**Scope:** Gateway, Perspective Session

### system.mongodb.deleteMany
`system.mongodb.deleteMany(connector, collection, filter, [options])`

Removes documents from the collection that match the filter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary `options` — A PyDictionary for including additional delete configurations. [optional]

**Returns:** PyDictionary `result` - Result formatted as PyDictionary with keys 'acknowledged' and 'deleteCount'.

**Scope:** Gateway, Perspective Session

### system.mongodb.deleteOne
`system.mongodb.deleteOne(connector, collection, filter, [options])`

Removes a document from the collection that matches the filter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary `options` — A PyDictionary for including additional delete configurations. [optional]

**Returns:** PyDictionary `result` - Result formatted as PyDictionary with keys 'acknowledged' and 'deleteCount'.

**Scope:** Gateway, Perspective Session

### system.mongodb.find
`system.mongodb.find(connector, collection, filter, [projection], [sort], [collation], [limit], [skip])`

Returns a list of PyDictionaries that match the criteria specified on the filter parameter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary `projection` — A PyDictionary for including or omitting specific key value pairs in the query result.
- PyDictionary `sort` — A PyDictionary of specified items to sort returned results.
- PyDictionary `collation` — A PyDictionary of items to specify language-specific rules. [optional]
- Int `limit` — The maximum number of PyDictionaries that will be returned. [optional]
- Int `skip` — The number of PyDictionaries to skip before returning results. [optional]

**Returns:** List[PyDictionary] `result` - A list of PyDictionary results.

**Scope:** Gateway, Perspective Session

### system.mongodb.findOne
`system.mongodb.findOne(connector, collection, filter, [projection])`

Returns a single PyDictionary that matches the criteria specified on the filter parameter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary `projection` — A PyDictionary for including or omitting specific key value pairs in the query result.

**Returns:** PyDictionary `result` - A single PyDictionary as a result.

**Scope:** Gateway, Perspective Session

### system.mongodb.insertMany
`system.mongodb.insertMany(connector, collection, document, [options])`

Inserts a list of PyDictionaries into a specified collection.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- List[PyDictionary] `document` — A list of PyDictionaries representing new records being added to the collection.
- PyDictionary `options` — A PyDictionary for including additional insert configurations. [optional]

**Returns:** List[PyObject] `objectIdList` - Keys of the inserted documents (usually BSON ObjectId, unless a different key type is specified).

**Scope:** Gateway, Perspective Session

### system.mongodb.insertOne
`system.mongodb.insertOne(connector, collection, document, [options])`

Inserts a single PyDictionary into a specified collection.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `document` — A PyDictionary of specified fields representing a record being added to the collection.
- PyDictionary `options` — A PyDictionary for including additional insert configurations. [optional]

**Returns:** PyObject `objectId` - Key of inserted document (usually BSON ObjectId, unless a different key type is specified).

**Scope:** Gateway, Perspective Session

### system.mongodb.listCollectionNames
`system.mongodb.listCollectionNames(connector)`

Returns a list of all collection names.

**Params:**
- String `connector` — Name of connector (case-insensitive).

**Returns:** List[String] `collectionNames` - A list of all collection names.

**Scope:** Gateway, Perspective Session

### system.mongodb.listConnectorInfo
`system.mongodb.listConnectorInfo()`

Returns a list of PyDictionary descriptors of all MongoDB Connectors.

**Params:** none

**Returns:** List[PyDictionary] `connectors` - Descriptors with keys 'name', 'description', 'status', and 'error' (if present).

**Scope:** Gateway, Perspective Session

### system.mongodb.replaceOne
`system.mongodb.replaceOne(connector, collection, filter, replacement, [options])`

Replaces a document in the collection that matches the filter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary `replacement` — New values to apply for all non-immutable document fields.
- PyDictionary `options` — A PyDictionary for including additional replace configurations. [optional]

**Returns:** PyDictionary `result` - Result with keys 'acknowledged', 'modifiedCount', 'matchedCount', and 'upsertedId'.

**Scope:** Gateway, Perspective Session

### system.mongodb.updateMany
`system.mongodb.updateMany(connector, collection, filter, updates, [options])`

Updates all documents in the collection that match the filter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary / List[PyDictionary] `updates` — Changes to apply to document fields; also supports an aggregation-pipeline form.
- PyDictionary `options` — A PyDictionary for including additional update configurations. [optional]

**Returns:** PyDictionary `result` - Result with keys 'acknowledged', 'modifiedCount', 'matchedCount', and 'upsertedId'.

**Scope:** Gateway, Perspective Session

### system.mongodb.updateOne
`system.mongodb.updateOne(connector, collection, filter, updates, [options])`

Updates a document in the collection that matches the filter.

**Params:**
- String `connector` — The name of connector (case-insensitive).
- String `collection` — The name of collection (case-sensitive).
- PyDictionary `filter` — A PyDictionary for specifying matching key value pair criteria when querying a collection.
- PyDictionary / List[PyDictionary] `updates` — Changes to apply to document fields; also supports an aggregation-pipeline form.
- PyDictionary `options` — A PyDictionary for including additional update configurations. [optional]

**Returns:** PyDictionary `result` - Result with keys 'acknowledged', 'modifiedCount', 'matchedCount', and 'upsertedId'.

**Scope:** Gateway, Perspective Session

## system.kafka

Poll and produce records against a Kafka cluster through a configured **Kafka connector**: list connectors/topics/partitions, poll a topic or a specific partition (with consumer group / offset control), seek to the latest N records, and send records synchronously or asynchronously.

### system.kafka.listConnectorInfo
`system.kafka.listConnectorInfo()`

Returns descriptions of all Kafka connectors in PyDictionary format.

**Params:** none

**Returns:** List - A list of descriptions of all Kafka connectors in PyDictionary format.

**Scope:** Gateway

### system.kafka.listTopicPartitions
`system.kafka.listTopicPartitions(connector, topic, groupId, [options])`

Returns a list of records that match the filter.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- String `groupId` — The unique string of the consumer group the consumer belongs to.
- Dictionary `options` — Custom options specific to the consumer, with key value string pairs. Optional.

**Returns:** List - A list of records that match the filter.

**Scope:** Gateway

### system.kafka.listTopics
`system.kafka.listTopics(connector)`

Returns a list of topics for the provided connector.

**Params:**
- String `connector` — The name of the Kafka connector.

**Returns:** List - A list of topics for the provided connector.

**Scope:** Gateway

### system.kafka.pollPartition
`system.kafka.pollPartition(connector, topic, partition, offset, [options], sizeCutoff, timeoutMs)`

Returns a list of records polled from a specified partition.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- Integer `partition` — The partition to poll.
- Long `offset` — The position of offset to start the poll at.
- Dictionary `options` — Custom options specific to the consumer, with key value string pairs. Optional.
- Integer `sizeCutoff` — The total record count allowed before polling will be stopped.
- Long `timeoutMs` — The amount of time in milliseconds before polling will be stopped.

**Returns:** List - A list of records polled from a specified partition.

**Scope:** Gateway

### system.kafka.pollTopic
`system.kafka.pollTopic(connector, topic, groupId, [options], sizeCutoff, timeoutMs)`

Returns a list of records from the specified topic.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- String `groupId` — The unique string of the consumer group the consumer belongs to.
- Dictionary `options` — Custom options specific to the consumer, with key value string pairs. Optional.
- Integer `sizeCutoff` — The total record count allowed before polling will be stopped.
- Long `timeoutMs` — The amount of time in milliseconds before polling will be stopped.

**Returns:** List - A list of records from the specified topic.

**Scope:** Gateway

### system.kafka.seekLatest
`system.kafka.seekLatest(connector, topic, partition, recordCount, [options])`

Retrieves the last N number of records from a specified topic.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- Integer `partition` — The partition to target.
- Integer `recordCount` — The number of records to return.
- Dictionary `options` — Custom options specific to the consumer, with key value string pairs. Optional.

**Returns:** List - An N number of records from a specified topic, as a list.

**Scope:** Gateway

### system.kafka.sendRecord
`system.kafka.sendRecord(connector, topic, key, value, [partition], [timestamp], [headerKeys], [headerValues], [options])`

Sends a record to a specified topic.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- String `key` — The Kafka record key, used in identifying the record.
- String `value` — The Kafka record value you want to send.
- Integer `partition` — The partition to target. Optional.
- Long `timestamp` — The record timestamp, in milliseconds. Optional.
- List `headerKeys` — The header keys for the record. Optional.
- List `headerValues` — The header values for the record. Optional.
- Dictionary `options` — Custom options specific to the producer, with key value string pairs. Optional.

**Returns:** PyDictionary - Metadata response with keys: topic, partition, offset, timestamp.

**Scope:** Gateway

### system.kafka.sendRecordAsync
`system.kafka.sendRecordAsync(connector, topic, key, value, [partition], [timestamp], [headerKeys], [headerValues], [options])`

Sends a record to a specified topic asynchronously.

**Params:**
- String `connector` — The name of the Kafka connector.
- String `topic` — The name of the Kafka topic.
- String `key` — The Kafka record key, used in identifying the record.
- String `value` — The Kafka record value you want to send.
- Integer `partition` — The partition to target. Optional.
- Long `timestamp` — The record timestamp, in milliseconds. Optional.
- List `headerKeys` — The header keys for the record. Optional.
- List `headerValues` — The header values for the record. Optional.
- Dictionary `options` — Custom options specific to the producer, with key value string pairs. Optional.

**Returns:** Nothing

**Scope:** Gateway

## Gotchas and 8.3 notes

- **DNP3 is split into two namespaces on purpose.** `system.dnp` targets the newer DNP3 driver;
  `system.dnp3` targets the Legacy DNP3 driver. Every function page in both namespaces explicitly
  cross-links to its counterpart in the other namespace — this pairing is stated directly in the docs,
  not inferred. Picking the wrong namespace for your device's driver type will not throw a helpful error
  at script-write time; verify which DNP3 driver a given device connection actually uses before choosing
  a namespace.
- **`system.kafka` and `system.mongodb` are connector-based, not device-based.** Both namespaces take a
  `connector` name (a Kafka Connector / MongoDB Connector configured in the Gateway) rather than a device
  or OPC server name, and both expose a `listConnectorInfo()` introspection call. This is a different
  connectivity model from the driver/device pattern used by `system.device`, `system.opc`, `system.dnp*`,
  `system.bacnet`, etc. — treat Kafka/MongoDB access as "connector scripting" rather than "device
  scripting" when reasoning about scope, permissions, and error handling.
- **`system.opcua.addConnection`/`removeConnection` let you manage OPC UA connections entirely from
  script**, including security policy, security mode, and full failover settings — something otherwise
  done in the Gateway UI. There is no Tag-system equivalent; this is pure connection lifecycle
  management, separate from reading/writing values (which still goes through `system.opc`).
- **Docs typo**: the `system.iec61850.cancel` and `system.iec61850.getControlParams` pages both show
  `system.iec81650...` (digits transposed) in their literal Syntax code block. The real function names
  are `system.iec61850.cancel` and `system.iec61850.getControlParams` — trust the H1/page title and the
  Description text, not the Syntax line, on those two pages.
- **URL slug typo**: the docs site's own directory for `system.secsgem.deleteToolProgram` is spelled
  `system-secgem-deleteToolProgram` (missing an `s`) even though the function itself is correctly
  `system.secsgem.deleteToolProgram`.
- **`system.opc.browse` is fully recursive and cannot be terminated** — the docs themselves warn this is
  "especially problematic in larger systems" and recommend `system.opc.browseServer` instead, since that
  function's recursion is caller-driven (one level per call).
- **Mixed permission model across namespaces.** Most `system.opc*`/`system.mongodb`/`system.kafka`
  functions carry *no* Client Permission restriction, but `system.device.addDevice`/`removeDevice`/etc.
  and `system.dnp3.*` control functions require the **Device Management** / **DNP3 Management** Client
  Permission types respectively (Gateway scope is unaffected either way) — check each function's Scope
  line, since several are Gateway-only (all of `system.secsgem`'s Vision-Client-only calls, most of
  `system.dnp`/`system.kafka`) while others run in Gateway, Vision Client, *and* Perspective Session.
- **`system.mongodb.updateOne`/`updateMany`'s `updates` parameter accepts either a PyDictionary or a
  List[PyDictionary]** (the latter for MongoDB's aggregation-pipeline update form) — the source docs
  table for this parameter is malformed (an extra unescaped `|` splits the type across two cells); the
  type is correctly `PyDictionary / List[PyDictionary]`.
- **OPC HDA is a separate history system from Tag History.** `system.opchda.*` talks to third-party
  OPC HDA servers (e.g. Matrikon, Kepware) directly; it does not read from or write to Ignition's own
  Tag Historian, even when a Tag's value ultimately comes from the same underlying device.
- Every function above that is missing a **Note** line had no explicit deprecation/removal/version
  callout in the live 8.3 docs; absence of a note here is not a guarantee the function is unchanged
  since 8.1, only that the docs page carries no such notice.
