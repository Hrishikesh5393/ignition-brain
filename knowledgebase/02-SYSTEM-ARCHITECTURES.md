---
title: Ignition System Architectures
description: Deployment patterns for different scales and requirements
---

> **Skill level:** 200 · **Read first:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 02-SYSTEM-ARCHITECTURES

# Ignition System Architectures

Ignition supports multiple deployment patterns. Choose based on scale, reliability, geography.

## 1. Basic (Single Gateway)

**When:** Small sites, single location, <100 users
**Setup:** One gateway + devices + database
**Pros:** Simplest, minimal cost, fast to deploy
**Cons:** Single point of failure, limited scalability

```
Devices → Single Gateway (port 8088) → Perspective/Vision Clients
                  ↓
             Database
```

## 2. Scale Out

**When:** Growing sites, multiple projects, moderate load
**Setup:** Multiple gateways, load balancer, shared database
**Pros:** Horizontal scaling, distributes load, maintains single management
**Cons:** More complex, requires load balancer

```
Devices → [Gateway 1]  ← Load Balancer → Web Browsers
       → [Gateway 2]  ↓
       → [Gateway 3]  Shared Database
```

## 3. Hub and Spoke

**When:** Multi-site operations, centralized control, remote sites
**Setup:** Central hub gateway + remote spoke gateways, hub manages all
**Pros:** Centralized management, remote autonomy, can work offline
**Cons:** Network dependency, sync complexity

```
Remote Site 1 [Gateway] --→ 
Remote Site 2 [Gateway] --→ Hub Gateway (Central) → DB + Reports
Remote Site 3 [Gateway] --→
```

## 4. Edge Architecture

**When:** Distributed manufacturing, IoT-heavy, real-time local processing
**Setup:** Edge gateways process locally, sync to cloud/hub
**Pros:** Low latency, autonomous edge nodes, cloud integration
**Cons:** Data sync complexity, edge management overhead

```
Edge Gateway 1 (autonomous) ↘
Edge Gateway 2 (autonomous) → Cloud/Central Hub
Edge Gateway 3 (autonomous) ↗
```

## 5. Enterprise

**When:** Large corporation, global operations, high availability
**Setup:** Multi-region, redundancy, disaster recovery
**Pros:** Maximum reliability, geo-distributed, scalable
**Cons:** Complex setup, expensive, requires expertise

```
Region 1: [Primary] ↔ [Secondary] (redundant)
Region 2: [Primary] ↔ [Secondary] (redundant)
    ↓ (sync)
Central DB + Archive
```

## 6. Cloud-Based

**When:** SaaS model, no on-premises hardware, flexibility
**Setup:** Cloud-hosted gateway (AWS, Azure, GCP) + edge components
**Pros:** Scalable, no infrastructure cost, automatic backups
**Cons:** Internet dependency, data residency concerns, latency

```
Cloud Gateway (AWS/Azure) → Multiple Regions
            ↓
    Perspective Clients (browser)
            ↓
    Optional: Edge gateways (local processing)
```

## 7. Redundancy (HA)

**When:** Mission-critical, cannot afford downtime
**Setup:** Active-Standby or Active-Active redundancy
**Pros:** Auto-failover, zero downtime, maintains operations
**Cons:** Expensive (2x hardware), complex sync

```
Active Gateway ↔ Standby Gateway (synced, heartbeat)
        ↓ (clients connect to active)
    Shared Database (single source of truth)
```

## 8. AWS Outposts

**When:** Hybrid AWS, on-premises with AWS integration
**Setup:** AWS Outposts + edge gateways
**Pros:** AWS benefits on-site, lower latency, AWS integration
**Cons:** Specialized, cost, infrastructure commitment

## Selection Guide

| Scale | Sites | Users | Recommendation |
|-------|-------|-------|-----------------|
| Small | 1 | <50 | Basic |
| Medium | 1 | <500 | Basic + Scale Out |
| Multi-site | 2-10 | Any | Hub-Spoke |
| Large | 10+ | 1000+ | Enterprise |
| Real-time | Any | Any | Edge + Hub |
| No CAPEX | Any | Any | Cloud |
| Critical | Any | Any | Redundancy (HA) |

---
**Design Decision:** Start with Basic. Grow to Scale Out or Hub-Spoke as needed. Enterprise/Redundancy = specialized requirements only.

---

## See Also

**Prerequisites:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)

**Builds toward:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md), [90-DATABASE-ADVANCED-OPTIMIZATION](90-DATABASE-ADVANCED-OPTIMIZATION.md)

**Related:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
