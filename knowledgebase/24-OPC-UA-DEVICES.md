---
title: OPC-UA & Device Connectivity
description: Device communication, OPC protocol, drivers
---

> **Skill level:** 200 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 24-OPC-UA-DEVICES

# OPC-UA & Device Connectivity

Industrial protocol for real-time data from PLC/devices.

## What is OPC-UA?

**OPC** = OLE for Process Control (industrial standard)
**OPC-UA** = Modern, secure version over TCP/IP

**Why:** Device-agnostic way to read sensor values, control equipment.

## Architecture

```
PLC/Device (Modbus, EtherCAT, etc.)
    ↓
OPC Server (device manufacturer provides)
    ↓
Ignition Gateway (OPC-UA client)
    ↓
Perspective Client (reads tags)
```

## Configure OPC Device in Ignition

**Admin Console:**
```
Config → Devices → New Device
Select driver: Siemens S7, Beckhoff, OPC-UA Server, Modbus TCP, etc.
Name: PLC01
Address: 192.168.1.100:502
```

**Verify:** Test connection button

## OPC-UA Tag Paths

**Format:** `[opc]NamespacePath/NodeName`

**Examples:**
```
[opc]Siemens/PLC01/Main/Temperature
[opc]Beckhoff/Axis1/Position
[opc]Modbus/InputRegisters/Value_001
```

**Browse:** Designer → Show Tag Browser → OPC device folder → Browse available nodes

## Reading OPC Tags

**Binding:**
```javascript
{tag: "[opc]PLC01/MotorSpeed"}
```

**Script:**
```python
result = system.tag.read("[opc]PLC01/Temperature")
value = result.value
quality = result.quality.name  # "Good", "Bad", "Uncertain"
```

## Writing OPC Tags

```python
# Write to writable OPC tag
system.tag.write("[opc]PLC01/StartMotor", 1)
```

**Note:** Not all OPC tags are writable (depends on device).

## OPC Tag Quality

Every OPC tag has quality indicator:

| Quality | Meaning |
|---------|---------|
| Good | Value is current and valid |
| Bad | Device disconnected or error |
| Uncertain | Device question mark |
| Not Connected | OPC server offline |

**Check quality before using:**
```python
result = system.tag.read("[opc]PLC01/Temp")
if result.quality.name == "Good":
    value = result.value
else:
    logger.warn(f"Tag quality: {result.quality.name}")
    # Use last-known value or default
```

## Common Drivers

| Driver | Use Case |
|--------|----------|
| **OPC-UA Server** | Generic OPC-UA server (Siemens, Beckhoff, etc.) |
| **Siemens S7** | Siemens PLC (older models without OPC-UA) |
| **Beckhoff** | Beckhoff TwinCAT |
| **Modbus TCP** | Legacy devices, PLCs with Modbus |
| **Ethernet/IP** | Allen-Bradley CompactLogix, etc. |
| **MQTT** | IoT sensors, distributed edge devices |
| **REST** | HTTP API devices |

## Troubleshooting OPC

**Issue:** Tag quality "Bad"
**Cause:** Device offline, no response, firewall blocked
**Fix:** Check network ping, verify IP/port, check firewall

**Issue:** Can't browse OPC server
**Cause:** OPC server not running or Ignition can't reach it
**Fix:** Start OPC server, verify network connectivity

**Issue:** Tag value not updating
**Cause:** Tag not readable, low polling rate configured
**Fix:** Verify tag readable, increase polling frequency in device config

## OPC Polling

**Polling Interval:** How often Ignition reads OPC tag (milliseconds).

**Config:** Device settings → Polling Interval (default 1000ms = 1 sec)

**Higher frequency** = More real-time but more network traffic
**Lower frequency** = Less responsive but less load

**Recommendation:**
- Critical tags: 100-500ms
- Normal tags: 1000ms
- Low-priority: 5000ms+

---
**See Also:** [[30-SCRIPTING-OVERVIEW]] for `system.opcua.*` functions

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

**Builds toward:** [24b-PLATFORM-DEVICES](24b-PLATFORM-DEVICES.md), [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md)

**Related:** [24b-PLATFORM-DEVICES](24b-PLATFORM-DEVICES.md), [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
