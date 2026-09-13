---
title: Platform Device Connectivity
description: Device types, drivers, OPC-UA configuration, monitoring, troubleshooting, and best practices
tags: [devices, connectivity, OPC-UA, drivers, platform]
---

> **Skill level:** 200 · **Read first:** [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 24b-PLATFORM-DEVICES

# Platform Device Connectivity

Comprehensive guide for industrial device connectivity in Ignition 8.3, covering device types, protocols, drivers, configuration, monitoring, and troubleshooting.

---

## 1. Device Types & Protocols Supported

### Core Industrial Protocols

| Protocol | Use Case | Primary Drivers |
|----------|----------|-----------------|
| **OPC-UA** | Industrial standard for data access | Native support, TCP/IP encrypted |
| **Modbus TCP/RTU** | Simple industrial devices (scales, sensors) | Modbus TCP, Modbus RTU over TCP |
| **EtherNet/IP** | Allen-Bradley controllers | AB Ethernet drivers |
| **S7 Communication** | Siemens PLCs | Siemens Standard & Enhanced drivers |
| **TCP/UDP** | Barcode scanners, raw stream data | TCP/UDP drivers |
| **DNP3** | Utility/energy devices | DNP3 driver (current & legacy) |
| **BACnet** | Building automation | BACnet Local/Remote drivers |
| **IEC 61850** | Power systems | IEC 61850 driver |
| **Mitsubishi TCP** | Mitsubishi PLCs | Mitsubishi TCP driver |

### Device Categories

**Browsable Devices** (support live tag discovery):
- Allen-Bradley controllers (via EtherNet/IP)
- Siemens S7-1200/1500 (with Enhanced Driver using symbolic addressing)
- OPC-UA servers
- UDP/TCP devices (limited browsing)

**Non-Browsable Devices** (require manual tag definition):
- Modbus devices
- Siemens S7-300/400 (legacy, absolute addressing only)
- Custom protocol devices

---

## 2. OPC-UA Configuration & Management

### Architecture Overview

```
Industrial Device (PLC/Sensor)
    ↓
Device Driver (TCP/IP, Serial, etc.)
    ↓
Ignition OPC-UA Server/Client
    ↓
Gateway Tags
    ↓
Perspective Clients / Scripting
```

### Core OPC-UA Concepts

- **OPC-UA** = Open Platform Communications Unified Architecture
- **Standard Protocol**: TCP/IP with built-in encryption (TLS support)
- **Built-in**: Ignition includes OPC-UA client functionality by default
- **Module Requirement**: OPC-UA module required for device drivers and server functionality

### Gateway Configuration Access

```
Gateway WebUI:
├─ Connections → Devices → Connections
│  └─ Create new device connections
├─ Connections → OPC → Connections
│  └─ Connect to external OPC-UA servers
└─ Connections → OPC → Quick Client
   └─ Browse and validate OPC servers in real-time
```

### Device Connection Creation Workflow

1. **Navigate**: Gateway > Connections > Devices > Connections
2. **Create**: Click "Create Device Connection +"
3. **Select Driver**: Choose device type (Modbus, Allen-Bradley, Siemens, etc.)
4. **Configure Connection**:
   - Device name (alphanumeric, no special characters)
   - Network address (IP/hostname)
   - Port (driver-specific defaults)
   - Authentication (if required)
5. **Verify**: Connection status transitions from "Disconnected" → "Connected"
6. **Monitor**: View tag count, request frequency, diagnostics

### OPC-UA Server Connection Configuration

When connecting to external OPC-UA servers:

```
Endpoint URL Format: opc.tcp://IpAddress:Port
Example: opc.tcp://192.168.1.50:4840
```

**Critical Connection Settings**:

| Setting | Default | Purpose |
|---------|---------|---------|
| Connect Timeout | 5s | Initial connection wait time |
| Request Timeout | 60s | Per-request response wait time |
| Session Timeout | 120s | Server session keep-alive period |
| Max Nodes/Operation | 8,192 | Maximum nodes per single request |
| Keep-Alive Interval | 15,000ms | Heartbeat frequency to server |
| Keep-Alive Timeout | 10,000ms | Failure detection window |
| Message Size Limit | 33.5MB | Maximum message payload |

**Advanced Settings**:

- **Host Override**: Corrects endpoint address mismatches
- **Browse Origin**: OBJECTS_FOLDER (recommended) vs ROOT_FOLDER
- **Timestamp Source**: Ignition, server-preferred, or source-preferred (new in 8.3.1)
- **Max References Per Node**: Adjustable for flat address spaces
- **Failover Configuration**: "Sticky" failover (stays on backup until failure)

### Server Diagnostics & Monitoring

**Server Diagnostics Page** displays:
- Server build information
- Active session count
- Session activity logs
- Server health metrics

**Warning**: Server diagnostics disabled by default (network overhead). Enable only when needed for troubleshooting.

**Client Diagnostics Page** displays:
- Subscription groups
- Publishing intervals
- Monitored item counts
- Sampling rates
- Node-level subscription visibility

---

## 3. Device Drivers Configuration & Management

### Modbus TCP/RTU

**Connection Setup**:
```
Gateway > Connections > Devices > Create Device Connection
├─ Driver: Modbus TCP, Modbus RTU over TCP, or Modbus RTU
├─ Name: device_identifier (e.g., "Modbus_Scale01")
├─ TCP Address: IP address
├─ TCP Port: default 502
└─ Serial COM Port: (if using RTU serial)
```

**Supported Function Codes**:

| Code | Function | Read/Write |
|------|----------|-----------|
| 01 | Read Coils | Read |
| 02 | Read Discrete Inputs | Read |
| 03 | Read Holding Registers | Read |
| 04 | Read Input Registers | Read |
| 06 | Write Single Register | Write |
| 15 | Write Multiple Coils | Write |
| 16 | Write Multiple Registers | Write |
| 22 | Mask Write Register | Write |

**Key Configuration Options**:
- Communication timeout (milliseconds)
- Local address binding (TCP only)
- Serial parameters: baud rate, data bits, stop bits, parity, handshake
- Maximum registers per read: 125 (default)
- Maximum registers per write: 123 (default)
- Maximum coils/discrete inputs: 2,000 (default)
- Zero-based addressing toggle
- Word order reversal (for 32-bit values)

**Critical Limitation**: **Modbus devices do not support tag browsing**. Tags must be:
- Manually defined through Tag Editor
- Imported via CSV/Excel with unit ID and address mapping

**Tag Address Format**:
```
[device_name]Unit_ID.Coil_001
[device_name]Unit_ID.InputRegister_100
[device_name]Unit_ID.HoldingRegister_50
```

**Performance Tuning**:
- Adjust "Max Concurrent Requests" to balance throughput vs PLC performance
- Default retry count: enabled
- "Reconnect After Consecutive Timeouts": enabled by default

---

### Allen-Bradley Ethernet

**Supported PLC Series**:
- CompactLogix (5380, 5381)
- ControlLogix (5580, 5581)
- Logix controllers (via EtherNet/IP)
- Micro800 (820, 850, 870 series)
- MicroLogix 1400
- PLC5
- SLC 500

**Micro800 Configuration Example**:

```
Gateway > Connections > Devices > Create Device Connection
├─ Driver: Allen-Bradley Micro800
├─ Name: PLC_Micro800_Main
├─ Hostname: 10.20.1.2
├─ Port: 44818 (default)
├─ Local Address: auto-selected (or specify network adapter IP)
└─ Timeout: 5000ms (recommended)
```

**Supported Data Types** (14 total):
```
BOOL, INT, DINT, LINT, REAL, LREAL
STRING (UTF-8, max 80 chars), BYTE, WORD, DWORD, LWORD
DATE, TIME
```

**Addressing & Tag Browsing**:

✅ **Browsable via Designer**:
- Global variables with atomic types
- Atomic arrays

❌ **Requires Manual Configuration**:
- UDTs (User-Defined Types)
- System structures
- BOOL arrays
- Arrays with non-zero indices

**Import Methods**:

1. **CSV Export from Connected Components Workbench**:
   ```
   Right-click controller → Export > Variables → Save CSV
   Device → Three-dots menu → Addresses → Import Configuration File
   ```

2. **Zip Export**:
   ```
   Right-click controller → Export Device → Check "Export Variables Only"
   Import same workflow as CSV
   ```

**Bit-Level Addressing**:
```
MyUint.1          # Bit 1 of MyUint variable
MyByteArray[0].7  # Bit 7 of first array element
```

**Advanced Settings**:
- Write Priority Ratio: read-to-write balance
- Automatic Rebrowse: detects tag changes, triggers re-browsing
- CIP Connection Size: Forward Open request parameter
- Max Concurrent Requests: optimize throughput (impacts PLC load)

**Performance Notes**:
- Avoid subscriptions with unused tags
- Avoid rapid refresh rates
- Concurrent requests may degrade PLC performance if set too high

---

### Siemens S7 Drivers

#### Siemens Standard Driver

**Supported Devices**:
- S7-200
- S7-300
- S7-400
- S7-1200
- S7-1500

**Basic Configuration**:
```
Gateway > Connections > Devices > Create Device Connection
├─ Driver: Siemens (Standard)
├─ Name: PLC_Siemens_Main
└─ Hostname: 10.20.4.71
```

**Critical Limitation**: **S7 devices do not support tag browsing**

**Tag Definition Methods**:
1. Manual entry in Tag Editor
2. CSV/Excel import/export
3. Addressing spreadsheet with OPC Item Path syntax

**Tag Address Format**:
```
[device_name]address
[Siemens_Main]IW0              # Input Word 0
[Siemens_Main]DB500.DBReal10   # Real value in DB500, offset 10
[Siemens_Main]DB1.DBX9.7       # Bit 7 in byte 9 of DB1
```

#### Siemens Enhanced Driver

**Key Advantages**:
- Symbolic addressing support (S7-1200/1500 only)
- TLS secure connections
- Improved performance
- Modern data type support

**System Requirements**:
- Linux x64: GLIBC 2.34+
- Linux ARM: GLIBC 2.17+
- ⚠️ **Incompatible**: Ubuntu 20.04, Debian 10, Debian 11 (x64)

**Device Type Selection**:
```
S7-1500: Full support (absolute & symbolic)
S7-1200: Full support (absolute & symbolic)
S7-300:  Absolute addressing only
S7-400:  Absolute addressing only
```

**Addressing Methods**:

**Absolute Addressing** (all devices):
```
IW0                    # Input Word 0
DB500.DBREAL10        # Real value in data block 500
DB1.DBX9.7            # Bit 7 in byte 9 of DB1
DB500.STRING255[7]    # String array element
```

**Symbolic Addressing** (S7-1200/1500 only):
```
Gateway Tag Browser:
├─ Add OPC Standard Tag
├─ Select Ignition OPC-UA Server
├─ Browse device hierarchy
└─ Select tag from dropdown tree
```

**Key Configuration Options**:
- Timeout: 3,000ms (default)
- Port: 102 (default)
- Rack/Slot: 0/0 (default)
- Secure Connection Mode: REQUIRED, PREFERRED, or DISABLED
- Optimize Writes: batch multiple tag writes

**Data Type Support** (24 types):
- Numeric: BYTE, WORD, DWORD, LWORD, INT, DINT, LINT
- Float: REAL, LREAL
- Time/Date: TIME, DATE, DT, LDT
- String: CHAR, STRING, WSTRING

**Operational Limits**:
- Maximum 250 device connections per gateway
- Optimized for data block access (modern S7-1200/1500)
- Legacy compatibility maintained for older models

---

### UDP & TCP Drivers

**Use Cases**:
- Barcode scanners
- Weighing scales
- Serial port devices (via network)
- Raw stream data devices
- Delimited message protocols

**Device Architecture**:
```
Device Connection (configured name)
├─ Port Folder (one per configured port)
│  ├─ Last Receive Time (tag)
│  ├─ Message (string representation)
│  ├─ MessageBytes (binary representation)
│  ├─ Field 1 through N (parsed fields)
│  └─ Writable/WritableBytes (if enabled)
```

**TCP Driver Configuration**:

```
Gateway > Connections > Devices > Create Device Connection
├─ Driver: TCP
├─ Name: Scanner_TCP_01
├─ Port(s): 5000 (or comma-separated list)
├─ Address: 192.168.1.100 (target device IP)
├─ Connect Timeout: 0 (disabled) or milliseconds
├─ Inactivity Timeout: 0 (disabled) or milliseconds
├─ Message Delimiter: Packet Based, Character Based, or Fixed Size
├─ Field Delimiter: comma, tab, custom character
└─ Write Timeout: 5000ms (default)
```

**UDP Driver Configuration**:

```
Gateway > Connections > Devices > Create Device Connection
├─ Driver: UDP
├─ Name: Broadcast_UDP_01
├─ Port(s): 5000 (listening port, comma-separated)
├─ Address: 0.0.0.0 (listen all) or specific IP
├─ Message Delimiter: Packet Based, Character Based, or Fixed Size
├─ Field Delimiter: comma, tab, custom character
├─ Message Buffer Size: bytes
└─ Multicast: enabled/disabled
```

**Message Delimiter Options**:
- **Packet Based**: One message per network packet
- **Character Based**: Delimiter character signals message end
- **Fixed Size**: Fixed number of bytes per message

**Escape Sequences for Delimiters**:
```
\t   Tab
\b   Backspace
\n   Newline
\r   Carriage Return
\f   Form Feed
```

**Available Tags**:
- `Last Receive Time`: Timestamp of most recent message
- `Message`: String representation of data
- `MessageBytes`: Binary representation of data
- `Field_1, Field_2...`: Parsed fields (if configured)
- `Writable` / `WritableBytes`: Send data to device (TCP only, if enabled)

**Performance Notes**:
- Update rate limited by scan class frequency (typical: 100-200ms reliable)
- TCP minimum: 25ms (theoretical)
- UDP: depends on network conditions
- Configuration mismatch (delimiter/field count) causes BAD_CONFIG_ERROR

**Troubleshooting**:
- Verify delimiter characters match device data format exactly
- Verify field delimiter matches device message structure
- Check "Writeback Enabled" for bidirectional communication (TCP)

---

## 4. Device Status Monitoring

### Diagnostic Tags (System-Generated)

Every device connection automatically includes a **[device_name]Diagnostics** folder with health monitoring tags.

**Common Diagnostic Tags**:

| Tag | Type | Purpose |
|-----|------|---------|
| `Is Connected` | Boolean | 1 = connected, 0 = disconnected |
| `Last Receive Time` | Date/Time | Timestamp of most recent data update |
| `Last Write Time` | Date/Time | Timestamp of most recent write |
| `Tag Count` | Integer | Number of tags currently monitored |
| `Request Rate` | Integer/Float | Tags requested per second |
| `Uptime` | Time | Connection duration since last connect |
| `Error Count` | Integer | Cumulative communication errors |
| `Connection Attempts` | Integer | Total connection attempts |

### Gateway Connection Status Page

Access via: **Gateway WebUI > Connections > Devices**

Displays per device:
- **Name**: Device identifier
- **Driver**: Device type
- **Status**: Connected, Disconnected, Faulted, Missing Dependency
- **Tag Count**: Active monitored tags
- **Request Rate**: Frequency of tag requests
- **Details**: Click for advanced diagnostics

**Device Details Diagnostics Panel**:
- Per-tag quality and value history
- Network packet statistics
- Error frequency analysis
- Performance metrics
- Last error message

### Creating Device Status Dashboard

**Step 1: Collect Diagnostic Tags**
```
Tag Browser:
├─ New Folder: "DeviceStatus"
└─ Import for each device:
   ├─ [PLC01]Diagnostics/IsConnected
   ├─ [PLC02]Diagnostics/IsConnected
   ├─ [Scale01]Diagnostics/IsConnected
   └─ [Modbus01]Diagnostics/IsConnected
```

**Step 2: Visual Representation**
```
Perspective Template:
├─ Container (light background)
│  ├─ PLC01 Status
│  │  ├─ Status Icon (color binding: 0=red, 1=green)
│  │  ├─ Last Update Timestamp
│  │  └─ Connection Status Label
│  ├─ PLC02 Status
│  ├─ Scale01 Status
│  └─ Modbus01 Status
└─ Last Refresh Time
```

**Color Binding Example** (property binding):
```
colorStyle.background:
  if({DeviceStatus/PLC01_IsConnected} = 1, "#00FF00", "#FF0000")

With transparency (alpha ~30%):
  "rgba(0, 255, 0, 0.3)" for online
  "rgba(255, 0, 0, 0.3)" for offline
```

### OPC-UA Connection Diagnostics

**Server Diagnostics** (if enabled):
- Server status and uptime
- Session count and history
- Message processing metrics
- Subscription statistics

**Client Diagnostics**:
- Connection uptime
- Subscription groups
- Monitored items per subscription
- Requested vs. revised sampling intervals
- Publishing intervals
- Node visibility per subscription

---

## 5. Troubleshooting Device Connectivity

### Connection State Troubleshooting

| Status | Cause | Resolution |
|--------|-------|-----------|
| **Disconnected** | Initial state or network failure | Check IP/hostname, verify network connectivity, firewall rules |
| **Connected** | Active communication | Monitor tag count and request rate for anomalies |
| **Faulted** | Driver error or device configuration issue | Review gateway logs, check device-specific settings |
| **Missing Dependency** | OPC-UA module disabled or not installed | Gateway > Modules > Enable OPC-UA Module |

### Common Connection Issues

**1. Device Won't Connect**
```
Checklist:
□ Correct IP address/hostname
□ Device port matches driver default (502=Modbus, 44818=Micro800, etc.)
□ Network connectivity confirmed (ping device IP)
□ Firewall permits gateway ↔ device communication
□ Device supports protocol (OPC-UA, EtherNet/IP, Modbus, etc.)
□ Driver module installed and enabled
□ Device not reserved by another system
```

**2. Tags Show "Bad" Quality**
```
Quality Status Meanings:
- Good: Current, valid data
- Bad: Device offline or error condition
- Uncertain: Device returning uncertain status
- Not Connected: OPC server unreachable

Troubleshooting:
□ Verify device connection status (Diagnostics > Is Connected)
□ Check device logs for errors
□ Confirm tag addressing syntax (especially Modbus/Siemens)
□ Review communication timeout settings
□ Monitor network latency
```

**3. High Tag Request Latency**
```
Diagnosis:
□ Check "Tag Count" and "Request Rate" in diagnostics
□ Excessive tag count (>1000 tags) on slow network
□ PLC CPU overload (verify via device diagnostics)
□ Network congestion

Solutions:
□ Reduce monitored tag count (unsubscribe unused tags)
□ Increase scan class intervals
□ Reduce OPC-UA subscription publishing interval
□ Upgrade network bandwidth
□ Optimize tag addressing (batch related reads)
```

**4. Modbus-Specific Issues**
```
Problems:
- No response to requests → Device offline or wrong unit ID
- Partial reads → Register count exceeds device limits
- Data corruption → Word order or addressing mismatch

Solutions:
□ Verify Modbus unit ID matches device configuration
□ Reduce "Max Registers Per Read" (try 50-100)
□ Check "Word Order Reversal" for 32-bit values
□ Confirm register addresses (0-based vs 1-based)
□ Test with external Modbus client (e.g., Modbus Master)
```

**5. Siemens S7 Connection Issues**
```
Standard Driver (no browsing):
- Syntax error → Verify absolute addressing format (DB500.DBX9.7)
- Device unreachable → Check IP, slot number, rack number
- Permission denied → Verify PLC project allows remote access

Enhanced Driver (symbolic addressing):
- GLIBC incompatibility → Cannot run on Ubuntu 20.04, Debian 10/11 (x64)
- TLS failure → Certificate mismatch or security policy mismatch
- Browse not working → Symbolic addressing only works S7-1200/1500
```

**6. OPC-UA Server Connection Issues**
```
Endpoint unreachable:
□ Verify endpoint URL format: opc.tcp://IP:Port
□ Confirm server is running and listening
□ Check firewall permits gateway ↔ server communication
□ Verify port number matches server configuration

Authentication failures:
□ Username/password mismatch
□ Certificate validation errors (check TLS settings)
□ Session timeout too short (adjust Session Timeout setting)

Message size errors:
□ Reduce nodes per subscription
□ Increase "Max Per Operation" limit (default 8,192)
□ Check "Max References Per Node" for flat address spaces
```

### Logging & Diagnostics

**Gateway Logs Access**:
```
Gateway WebUI > Diagnostics > Logs
├─ OPC UA module logs
├─ Device connection logs
├─ Communication errors
└─ Driver-specific debug messages
```

**Enable Extended Logging** (for troubleshooting):
```
Gateway > Connections > OPC > Connections > View Details
├─ Server Diagnostics tab (enable if disabled)
├─ Client Diagnostics tab (review subscription details)
└─ Export diagnostics (if available)
```

**Quick Client Validation**:
```
Gateway > Connections > OPC > Quick Client
├─ Browse OPC-UA server nodes
├─ Test read values in real-time
├─ Verify endpoint connectivity
└─ Diagnose addressing issues without tags
```

---

## 6. Best Practices for Device Setup

### Device Planning & Architecture

**1. Connection Design**
```
Recommended:
├─ One Ignition gateway per facility/network
├─ Separate device connections per PLC/device type
├─ Minimize cross-network communication
├─ Use OPC-UA for remote/internet devices (TLS encryption)
└─ Use native drivers (Modbus, EtherNet/IP) for local devices

Avoid:
├─ Multiple gateways competing for same device
├─ Connecting through multiple network hops unnecessarily
├─ Unencrypted connections for sensitive data
└─ Excessive tag subscriptions (>5000 total)
```

**2. Network Configuration**
```
Firewall Rules:
├─ Permit Gateway IP ↔ Device IP/Port
├─ Standard ports:
│  ├─ OPC-UA: 4840 (server), 4860+ (clients)
│  ├─ Modbus TCP: 502
│  ├─ EtherNet/IP: 44818 (Allen-Bradley)
│  ├─ S7: 102 (Siemens)
│  └─ Custom: per device configuration
└─ Use VLANs to isolate industrial network traffic
```

### Device Configuration Best Practices

**1. Naming Conventions**
```
Device Names (use consistent format):
├─ PLC_[Location]_[Type]_[Number]
├─ Examples:
│  ├─ PLC_Floor1_AB_Main
│  ├─ PLC_Floor2_Siemens_Secondary
│  ├─ Scale_WareHouse_Modbus_01
│  └─ Scanner_Shipping_TCP_01
│
Tag Folder Structure:
├─ [DeviceFolder]/Raw Data/[Tag]
├─ [DeviceFolder]/Diagnostics/[Status]
├─ [DeviceFolder]/Commands/[Writable]
└─ [DeviceFolder]/History/[Archived]
```

**2. Communication Timeouts**
```
Recommended Settings:
├─ Standard industrial network: 3,000-5,000ms
├─ Slow/congested network: 10,000ms+
├─ Local fast network: 1,000-3,000ms
│
Rule of thumb:
├─ Set timeout = 2-3 × typical response time
├─ Monitor actual response times during testing
└─ Increase gradually if devices fail intermittently
```

**3. Scan Class Configuration**
```
Device Tag Scan Classes:
├─ Fast (100ms): Critical real-time data
├─ Medium (500ms): Normal operations
├─ Slow (2s): Diagnostics, infrequent updates
└─ Never: Manual polling via script

OPC-UA Subscription Intervals:
├─ Fast: 100-200ms
├─ Medium: 500-1000ms
├─ Slow: 5000ms+

Avoid:
├─ Scan rate faster than device supports
├─ Subscribing to every available tag
└─ Mixed fast/slow scans on same device
```

**4. Tag Browsing & Import**
```
For browsable devices (AB, Siemens Enhanced, OPC-UA):
├─ Use Designer Tag Browser to browse live device
├─ Import only required tags
├─ Validate tag paths before finalizing imports

For non-browsable devices (Modbus, Siemens Standard):
├─ Use CSV/Excel templates for bulk import
├─ Verify addressing format matches device documentation
├─ Test each address individually during development
└─ Document address mapping in spreadsheet
```

### Performance Optimization

**1. Reduce Unnecessary Tag Subscriptions**
```
Impact Analysis:
├─ Each tag = one subscription request
├─ 1000 tags @ 500ms = 2,000 requests/second
├─ Excessive subscriptions slow device responses

Optimization:
├─ Subscribe only to tags used by UI or scripts
├─ Use polling (system.tag.read) instead of subscriptions for infrequent reads
├─ Archive historical data separately (don't keep live subscriptions)
└─ Unsubscribe after tag import (remove from UI if unused)
```

**2. Batch Operations**
```
Read Operations:
├─ Use system.tag.readAll() for multiple tag reads
├─ Reduces network round-trips
└─ More efficient than individual read calls

Write Operations:
├─ Enable "Optimize Writes" in driver settings (Siemens)
├─ Batch multiple writes together
└─ Schedule writes during low-activity periods
```

**3. OPC-UA Subscription Optimization**
```
Subscription Settings:
├─ Use appropriate publishing intervals:
│  ├─ Fast: 100-200ms minimum
│  ├─ Medium: 500-1000ms typical
│  └─ Slow: 5000-10000ms for diagnostics
│
├─ Adjust sampling intervals per tag:
│  ├─ Real-time critical: 100-200ms
│  ├─ Process data: 500-1000ms
│  └─ Diagnostics: 5000ms+
│
└─ Enable dead-band filtering:
   ├─ Only report changes > threshold
   ├─ Reduces network traffic
   └─ Configure per tag type
```

### Monitoring & Maintenance

**1. Proactive Health Monitoring**
```
Daily Checks:
├─ Device connection status (all should be "Connected")
├─ Error counts (should remain stable)
├─ Request latency (should be consistent)

Weekly Checks:
├─ Tag quality distribution (% Good vs Bad)
├─ Error type analysis (connection, timeout, data)
├─ Network latency trends

Monthly Checks:
├─ Unused tag cleanup
├─ Scan class efficiency review
├─ Device firmware updates (if available)
└─ Connection statistics analysis
```

**2. Documentation**
```
Maintain Updated Records:
├─ Device IP addresses and hostnames
├─ Network diagram (gateway, PLCs, devices)
├─ Port and protocol mappings
├─ Tag address specifications (especially Modbus, Siemens)
├─ Communication timeout values
├─ Known limitations or workarounds
└─ Device firmware versions
```

**3. Backup & Disaster Recovery**
```
Regular Backups:
├─ Gateway configuration (devices, OPC connections)
├─ Tag definitions and addressing spreadsheets
├─ Device connection documentation
└─ Script-based device management (system.device.addDevice)

Recovery Procedures:
├─ Document manual reconnection steps
├─ Test restore process quarterly
├─ Maintain hardware backup list (if applicable)
└─ Keep device documentation accessible offline
```

---

## Configuration Examples

### Example 1: Basic Modbus Device Connection

**Scenario**: Connect weighing scale via Modbus TCP at 192.168.1.50:502

**Steps**:
1. Gateway > Connections > Devices > Create Device Connection
2. Select "Modbus TCP"
3. Configure:
   - Name: `Scale_WareHouse_Modbus01`
   - Address: `192.168.1.50`
   - Port: `502` (default)
   - Timeout: `5000` ms
4. Create and verify status = "Connected"

**Tag Creation** (manual via CSV):
```
DeviceName,Address,Type,Access
Scale_WareHouse_Modbus01,Unit1.HoldingRegister_100,Float,Read
Scale_WareHouse_Modbus01,Unit1.InputRegister_200,Int,Read
Scale_WareHouse_Modbus01,Unit1.Coil_1,Bool,Read/Write
```

**Monitoring**:
```
Perspective Binding:
{tag: "[Scale_WareHouse_Modbus01]Unit1.HoldingRegister_100"}

Script Read:
result = system.tag.read("[Scale_WareHouse_Modbus01]Unit1.HoldingRegister_100")
if result.quality.name == "Good":
    weight = result.value
```

---

### Example 2: Allen-Bradley Micro800 with Browsing

**Scenario**: Connect Micro800 at 10.20.1.2 with symbolic tag import

**Steps**:
1. Gateway > Connections > Devices > Create Device Connection
2. Select "Allen-Bradley Micro800"
3. Configure:
   - Name: `PLC_Floor1_AB_Micro`
   - Hostname: `10.20.1.2`
   - Port: `44818` (default)
   - Timeout: `5000` ms
4. Create and verify status = "Connected"

**Tag Import**:
1. Designer > Tag Browser
2. Right-click device > Add Tags
3. Select "Ignition OPC-UA Server"
4. Browse device hierarchy:
   ```
   └─ PLC_Floor1_AB_Micro
      ├─ Global Variables
      │  ├─ LineSpeed (DINT)
      │  ├─ MotorRunning (BOOL)
      │  └─ TemperatureSensor (REAL)
      └─ Arrays
         └─ DataLog[10]
   ```
5. Select tags and import

**Binding Example**:
```
Perspective Component Property:
value: {tag: "[PLC_Floor1_AB_Micro]LineSpeed"}

Conditional Formatting:
backgroundColor:
  if({tag: "[PLC_Floor1_AB_Micro]MotorRunning"}, 
     "rgb(0,255,0)", 
     "rgb(255,0,0)")
```

---

### Example 3: OPC-UA Server Connection with Diagnostics

**Scenario**: Connect to external OPC-UA server with monitoring dashboard

**Steps**:
1. Gateway > Connections > OPC > Connections > Create
2. Endpoint: `opc.tcp://192.168.1.100:4840`
3. Configure timeouts and security policies
4. Enable Server Diagnostics (view Details)

**Create Monitoring Tags**:
```
Tag Folder: "RemoteServerStatus"
├─ [RemoteOPCServer]Diagnostics/IsConnected
├─ [RemoteOPCServer]Diagnostics/LastReceiveTime
├─ [RemoteOPCServer]Diagnostics/ErrorCount
└─ Custom tag: {tag: "[RemoteOPCServer]/some/node/path"}
```

**Dashboard Configuration**:
```
Perspective View:
├─ Header
│  ├─ Server Status Icon (bind to IsConnected)
│  └─ Last Update Time (bind to LastReceiveTime)
├─ Data Grid (displays all subscribed nodes)
├─ Charts (plot tag values over time)
└─ Alert Panel (show ErrorCount when > threshold)
```

---

## Summary

| Topic | Key Takeaway |
|-------|--------------|
| **Protocols** | OPC-UA native; supports Modbus, EtherNet/IP, S7, DNP3, TCP/UDP |
| **Drivers** | Match to device type; consider browsable vs manual configuration |
| **OPC-UA Setup** | TCP/IP based, encrypted, supports both server and client roles |
| **Device Monitoring** | Automatic diagnostic tags per device; use for health dashboards |
| **Best Practice** | Plan network, minimize subscriptions, optimize timeouts, document everything |
| **Troubleshooting** | Check connection status first; use Quick Client to validate connectivity |

---

## Related Documentation

- [24-OPC-UA-DEVICES.md](24-OPC-UA-DEVICES.md) - OPC protocol details and tag operations
- [23-DATABASE-INTEGRATION.md](23-DATABASE-INTEGRATION.md) - Storing device data in databases
- [31-SYSTEM-FUNCTIONS.md](31-SYSTEM-FUNCTIONS.md) - Device management scripting (system.device.*)
- [62-LOGGING-DIAGNOSTICS.md](62-LOGGING-DIAGNOSTICS.md) - Gateway diagnostics and troubleshooting

---

## See Also

**Prerequisites:** [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)

**Builds toward:** [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md), [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md)

**Related:** [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md), [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
