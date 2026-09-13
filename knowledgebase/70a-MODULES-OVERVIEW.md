---
title: Ignition Modules
description: Available modules, capabilities, use cases
---

> **Skill level:** 100 · **Read first:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 70a-MODULES-OVERVIEW

# Ignition Modules

Modular architecture. Install only what you need.

## Core Modules (Standard)

### Perspective Module
- **Purpose:** Modern web-based UI
- **Use:** Most new projects
- **Deployment:** Browser, mobile
- **Recommended:** Yes, default

### Vision Module
- **Purpose:** Legacy desktop/HMI visualization
- **Use:** Desktop-only, older projects
- **Deployment:** Windows desktop client
- **Recommended:** No, unless required for legacy

### OPC-UA Module
- **Purpose:** Device communication via OPC protocol
- **Use:** Connect to PLC, sensors, industrial devices
- **Protocols:** OPC-UA, Modbus TCP, EtherCAT, etc.
- **Recommended:** Yes, if using devices

### SQL Module
- **Purpose:** Database connectivity
- **Use:** Query, store, historical logging
- **Databases:** MySQL, MSSQL, PostgreSQL, Oracle
- **Recommended:** Yes, for any database work

### Tag Historian Module
- **Purpose:** Historical data logging
- **Use:** Trend analysis, compliance, auditing
- **Storage:** Database
- **Recommended:** Yes, for production data

## Optional Modules

### Reporting Module
- **Purpose:** Design and execute reports
- **Formats:** PDF, Excel, HTML
- **Use:** Daily/weekly reports, compliance docs
- **Deployment:** Embed in Perspective or export
- **Recommended:** Yes, if reporting needed

### MES Modules (Sepasoft)
- **Purpose:** Manufacturing execution system
- **Features:** Production tracking, OEE, genealogy
- **Use:** Track batches, calculate efficiency
- **Recommended:** Large manufacturing facilities

### MQTT Transmission Module
- **Purpose:** MQTT pub/sub messaging
- **Use:** IoT, edge devices, lightweight comms
- **Recommended:** Edge/IoT deployments

### Cirrus Link Modules
- **Purpose:** MQTT Edge Intelligence
- **Features:** Edge processing, sparkplug protocol
- **Use:** Distributed edge computing
- **Recommended:** Multi-site edge architectures

### Mobile Module
- **Purpose:** Native iOS/Android apps
- **Use:** Mobile interfaces (doesn't require Perspective)
- **Recommended:** If native app required

### Compute Module
- **Purpose:** Edge gateway (lightweight Ignition)
- **Use:** Remote sites, edge processing
- **Deployment:** Smaller footprint than full gateway
- **Recommended:** Edge nodes in hub-spoke

## Module Management

**Enable/Disable:**
```
Admin Console → Config → Modules
- Check to enable
- Uncheck to disable
- Modules download automatically (~1-2 min)
```

**View installed:**
```
Admin Console → Status → Modules
- Shows version, license status
```

## Licensing

**Most modules included** in Standard/Professional license.

**Advanced modules** (MES, Mobile) may require additional license.

**Check:** Admin Console → Status → Licensing

## Selection Guide

| Scenario | Modules |
|----------|---------|
| Simple monitoring dashboard | Perspective, OPC-UA, SQL (basic) |
| Production tracking | Perspective, OPC-UA, SQL, Historian, Reporting |
| Manufacturing site | Perspective, OPC-UA, SQL, Historian, MES, Reporting |
| Multi-site edge | Perspective, OPC-UA, SQL, MQTT, Compute |
| Legacy + new | Vision + Perspective, OPC-UA, SQL |

## Module Dependencies

Some modules depend on others:

```
Perspective → (no dependencies)
Vision → (no dependencies)
OPC-UA → (no dependencies)
SQL → (no dependencies)
Historian → Requires SQL module
Reporting → Perspective (for embedding)
MES → Requires Historian, SQL
```

All modules depend on core gateway.

---
**Best Practice:** Enable only modules in use (reduces memory, complexity).

---

## See Also

**Prerequisites:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)

**Builds toward:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [71-REPORTING-MODULE](71-REPORTING-MODULE.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md)

**Related:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md), [71-REPORTING-MODULE](71-REPORTING-MODULE.md), [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
