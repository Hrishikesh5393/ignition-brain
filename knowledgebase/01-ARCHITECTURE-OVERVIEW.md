---
title: Ignition 8.3 Architecture Overview
description: Platform layers, core concepts, modular design
---

> **Skill level:** 100 · **Read first:** [00-INDEX](00-INDEX.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 01-ARCHITECTURE-OVERVIEW

# Ignition Platform Architecture

## Layered Design

Ignition operates in 5 layers:

1. **OS Layer** - Windows/Linux/macOS. Hardware, network, compute resources.
2. **Platform Layer** - Core: device connectivity, database connections, licensing, module manager
3. **Module Layer** - HMI/SCADA modules, third-party extensions (MES, MQTT, Reporting, etc.)
4. **Application Layer** - Projects: Perspective views, Vision windows, scripts, tags, alarms
5. **User Layer** - End users accessing UI via browser or client

## Core Concepts

**Gateway** - Central hub, runs on port 8088 (web). Manages:
- All modules
- Device connections (OPC-UA, serial, ethernet)
- Database connections
- Tag engine
- Alarm engine
- User authentication
- Project deployment

**Modular** - Build solutions by combining modules. No monolith.

**Cross-platform** - Same gateway/projects run on Windows, Linux, macOS.

**Unlimited licensing** - Single license supports unlimited deployed clients.

**Web-native** - Perspective is browser-based (responsive, mobile-friendly).

## Data Flow Basics

```
Device/PLC → OPC-UA/Protocol → Gateway → Tags → Perspective Views
                ↓
         Expressions/Bindings ← Scripts (Python)
                ↓
         Database (historical storage)
```

**Tag** = Central data point in Ignition. Can be:
- OPC-UA bound (live from device)
- Expression-driven (calculated)
- SQL query (database)
- Manual (static values)

**Binding** = Link property to tag/expression. Updates automatically.

**Script** = Python code executing in Gateway, Vision, or Perspective context.

## Ignition vs. Competitors

| Feature | Ignition |
|---------|----------|
| Licensing | Unlimited/web clients (no per-seat cost) |
| UI | Modern web (Perspective) or desktop (Vision) |
| Scripting | Python |
| Modules | 50+ available |
| Deployment | Any architecture (cloud, edge, enterprise) |
| OPC-UA | Native support |

---
**Key Files to Reference:**
- Gateway config: C:/Program Files/Inductive Automation/Ignition/data/gateway.xml
- Projects: C:/Program Files/Inductive Automation/Ignition/data/projects/
- Logs: C:/Program Files/Inductive Automation/Ignition/logs/

---

## See Also

**Prerequisites:** [00-INDEX](00-INDEX.md)

**Builds toward:** [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

**Related:** [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md), [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
