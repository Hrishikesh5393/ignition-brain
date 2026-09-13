---
title: Clustering & High Availability Architecture
description: Redundancy model, state synchronization, failover mechanics, and Gateway Network topologies for production HA deployments
---

> **Skill level:** 300 · **Read first:** [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 84-CLUSTERING-HA-ARCHITECTURE

# Clustering & High Availability Architecture

Ignition does not implement N-node "active-active" clustering the way a web application tier or a database cluster does. Its HA model is **Gateway Redundancy**: a pair of gateways (Master + Backup) sharing one logical identity, with one node "Active" and the other "Backup" at any moment. Scale-out beyond a pair is achieved with the **Gateway Network** (a different mechanism — inter-gateway communication/fan-out, not shared-state clustering) and, for fleet management, the **Enterprise Administration Module (EAM)**. Understanding this distinction is the single most important thing to get right before designing an HA topology, because it changes what failover buys you and what it doesn't.

## 1. Clustering Overview & Topologies

### 1.1 The Redundant Pair (the only true "cluster" unit)

A redundant pair is exactly two gateways:

- **Master** — the gateway you configure as primary; it is the system of record for configuration.
- **Backup** — a gateway that continuously receives state and configuration from the Master and stands ready to become Active.

At runtime, only one of the two is ever **Active** (serving clients, running scripts, polling devices, writing history). The other is **Backup** (Warm or Cold, depending on sync state). This is an active/standby pair, not a load-balanced pool. You cannot add a third node to the same redundant pair — Ignition's built-in redundancy is strictly 2-node.

```
                 ┌───────────────────────┐
                 │   Redundant Pair      │
                 │                       │
   Clients ──►   │  ┌────────┐           │
   (Perspective,  │  │ MASTER │◄───sync───┼──┐
   Vision, OPC)   │  │ ACTIVE │           │  │
                 │  └────────┘           │  │
                 │                       │  │
                 │  ┌────────┐           │  │
                 │  │ BACKUP │◄──────────┼──┘
                 │  │ (warm) │           │
                 │  └────────┘           │
                 └───────────────────────┘
```

### 1.2 Scale-out patterns that people call "clustering"

Because Ignition doesn't offer native N-node clustering, production architectures achieve horizontal scale and resilience using layered patterns:

| Pattern | What it actually is | When to use |
|---|---|---|
| Redundant pair | 2-node active/standby, shared identity | Any single point of control that must not go down (SCADA HMI Gateway, historian front end) |
| Multiple independent redundant pairs + Gateway Network | Each functional area (e.g., per-plant, per-line) runs its own pair; pairs report up to a central gateway | Multi-site enterprises, hub/spoke reporting |
| EAM-managed fleet | Many independent gateways (not paired) centrally provisioned/monitored, each with or without its own redundancy | Large distributed plants with many edge gateways |
| Edge + Central aggregation | Edge/Panel gateways (often non-redundant, low-cost) push/store-and-forward to a central redundant pair | IIoT / distributed field sites with unreliable WAN links |
| Load-balanced identical Perspective front ends behind a reverse proxy | Not Ignition redundancy at all — external LB (nginx/HAProxy) in front of gateways sharing a common external DB/tag source | Very large concurrent Perspective client counts where session affinity is managed externally |

The important nuance: **redundancy protects one gateway's availability; the Gateway Network and EAM address fleet-scale distribution, not shared state.** A hub gateway does not take over tag execution for a spoke gateway that dies — it just relays data and commands between independently-running gateways.

### 1.3 Vision vs Perspective clustering implications

- **Perspective sessions** are tied to the gateway that serves them. On failover, browser clients reconnect (auto-reconnect logic in the Perspective session) to whichever gateway now answers on the shared/virtual IP or DNS name — session state (view parameters, unsaved form data) is generally lost unless you've built persistence into session props/tags.
- **Vision clients** maintain a persistent socket to the gateway. On failover they detect the drop and reconnect; open windows remain, but any in-flight write operations mid-failover can be lost or duplicated if not idempotent.

## 2. Master-Backup Redundancy Model

### 2.1 Roles and activation levels

Each gateway in a pair reports an **activity level**:

| Level | Meaning |
|---|---|
| **Active** | Running normally, serving clients, executing tags/scripts, talking to devices |
| **Backup (Warm)** | Fully synced, ready to activate in seconds if Master fails |
| **Backup (Cold)** | Out of sync (e.g., just started, or lost connection to Master for a while) — will not seamlessly take over; forces a "cold start" |
| **Independent** | Redundancy is enabled but the peer is unreachable and role negotiation hasn't resolved it (split-brain risk state, guarded against by the tie-breaker rules below) |

### 2.2 Master vs Backup is a *role*, not a permanent identity

In Ignition's redundancy model, "Master" and "Backup" are configuration-time labels for *which node normally runs Active*. After a failover, the surviving node (originally Backup) becomes Active and stays Active even after the original Master comes back — **Ignition does not auto-failback by default**. This is deliberate: auto-failback right after a Master reboot (which may still be flaky) risks flapping. Failback is a manual "Force Active" administrative action (or scripted via the Gateway API) unless you've explicitly configured otherwise.

### 2.3 Tie-breaking and split-brain avoidance

If both nodes lose contact with each other but both can still see clients/devices, you get a **split-brain** risk: both think they should be Active. Ignition mitigates this with:

- A **configured tie-breaker role** — one node is designated to "win" ties (normally the Master).
- **Redundancy heartbeat** over the Gateway Network connection between the pair, with a configurable timeout before a node assumes its peer is dead.
- Optional **witness/quorum considerations at the network layer** — Ignition itself doesn't run a third-node quorum service, so split-brain avoidance is fundamentally two-node logic plus network design (see §7). This is the biggest architectural weakness relative to true quorum-based clusters (e.g., etcd/Raft-based systems) and must be compensated for with reliable, low-latency, redundant network paths between the pair, not with additional Ignition configuration.

### 2.4 License-follows-role

Only the **Active** node consumes/enforces the Ignition license for running tags, clients, and modules. The Backup node runs a special reduced mode. See §4 for license mechanics in detail.

## 3. State Synchronization Mechanisms

The Backup node needs three categories of state to take over cleanly: **configuration**, **runtime tag/device state**, and **buffered data**.

### 3.1 Configuration synchronization

- Project resources, Gateway settings, security configuration, device connections, and module configuration are pushed from Master → Backup automatically over the Gateway Network connection whenever they change on the Master.
- The Backup gateway is **read-only for configuration** — you cannot edit projects directly on the Backup; edits must happen on Master and propagate.
- Sync is near-real-time but not instantaneous; a config change made seconds before a Master crash may not have propagated. This is the classic "why did my Backup activate with the old version of the project" gotcha (see 85-CLUSTERING-HA-CONFIGURATION.md §7).

### 3.2 Runtime state synchronization

- **Tag values** (memory tags, UDT instance values, expression tag results) are streamed from Active to Backup continuously so the Backup's in-memory tag tree matches the Active's, not just its configuration.
- **OPC-UA device connections**: the Backup does *not* normally hold its own live connections to field devices in the default configuration — the Active node owns device polling, and tag values are synced to Backup in memory. (See §6 and 85-...-CONFIGURATION.md for the "redundant device connection" pattern where both nodes *do* connect independently, trading device-load for faster failover.)
- **Alarm state** (active alarms, acknowledgement state, shelving) is synchronized so the Backup can take over alarm evaluation without re-raising or losing acknowledgements.
- **Session state for Perspective/Vision** is *not* transparently synchronized — this is a common source of confusion. A failover is not "hot" from the end user's perspective; clients reconnect and resume against fresh sessions.

### 3.3 Store-and-forward / historical data buffering

- **Tag History / Store and Forward**: history writes are queued locally and forwarded to the historian database. On the Active node, if the DB connection is down, data queues to disk and is not lost (bounded by configured buffer size/duration). On failover, the newly-Active node picks up its own store-and-forward queue — it does **not** inherit the old Active's pending queue automatically unless that queue was on shared/replicated storage. Data captured on the old Active but not yet flushed to DB before a hard crash can be lost.
- **Transaction Groups**: similarly buffer locally; same caveat applies on hard failover.

### 3.4 What is *not* synchronized

- Local gateway-scoped Python module state held in memory outside tags (e.g., module-level variables in a gateway event script) resets on the newly-Active node — it starts cold.
- Scheduled/one-shot `system.util.invokeAsynchronous` timers or in-flight `system.tag.queryTagHistory` calls in progress at failover time are lost, not resumed.
- File-system resources that live only on local disk (e.g., a script writing temp files to the OS filesystem rather than a tag/DB) are **not replicated** — treat local disk as ephemeral per-node, not shared.

## 4. License Implications of Clustering

- Redundant pairs require a license that explicitly authorizes redundancy — you cannot silently run two nodes off one non-redundant license and expect legitimate failover; the Backup will run in a limited/demo-like mode without a valid paired license.
- Both Master and Backup typically need to be licensed at (or above) the tag/connection/client counts you intend to run — sizing the Backup identically to the Master is the standard practice, since after failover the Backup *is* the production system and must sustain full load.
- **License activation is tied to hardware/host identity.** Because only one node is Active at a time, IA's licensing model allows the paired license to move with activation rather than requiring two fully separate full-price licenses — but the exact commercial terms (whether Backup is a discounted "standby" SKU or requires full parity licensing) depend on your IA account/edition, so confirm current terms with your IA sales contact or the license management console before assuming cost — **do not assume free/discounted standby licensing without verifying in the specific license file**.
- Third-party/OEM modules (e.g., some device drivers, certain add-on modules) may carry their own per-node licensing that isn't automatically covered by the platform redundancy license — verify each installed module's license scope independently.
- EAM-managed fleets: EAM itself has module-level licensing on the managing/central gateway; managed gateways generally need their own valid Ignition licenses, EAM does not "share" a license across the fleet.

## 5. Failover Process & Timing

### 5.1 Trigger conditions

Failover (Backup → Active) is triggered by any of:

- Master gateway process/host crash or unreachable (heartbeat timeout exceeded).
- Master gateway placed into a fault state (e.g., licensing failure, manual "Go to Fault" via Gateway Status).
- Administrator manually forces a role change ("Force Active" on Backup, or "Force Standby" on Master).
- Network partition where Backup determines (per tie-breaker rules) it should activate.

### 5.2 Failover timing breakdown

Approximate phases (actual numbers depend on heartbeat interval, network latency, and how much runtime state must reconcile — always validate against your own environment, don't treat these as guaranteed SLAs):

| Phase | Typical duration | Notes |
|---|---|---|
| Heartbeat timeout detection | Configurable, commonly a few seconds to tens of seconds | Shorter = faster detection but more false positives on transient blips |
| Role negotiation / tie-break | Sub-second to a few seconds | Only relevant if both nodes are contactable but disagree |
| Backup activation (tag engine, device polling, module startup) | Several seconds to ~1 minute | Depends on tag count, number of device connections needing (re)establishment, module startup order |
| Client reconnect | Seconds to ~1-2 minutes | Vision clients auto-reconnect; Perspective clients depend on browser retry/backoff and any load-balancer/DNS TTL in front of the pair |
| Full "warm" parity restored | Minutes | Historian catch-up, alarm re-sync, any queued store-and-forward flush |

**Practical expectation to set with stakeholders:** treat Ignition redundancy as **minutes-scale HA**, not sub-second failover. If your process requires sub-second failover (e.g., safety-instrumented control), Ignition redundancy is not the mechanism to rely on for that — SCADA/HMI-tier visibility loss for tens of seconds to a couple of minutes during failover is the realistic bound, and the underlying control system (PLC-level redundancy) should not depend on Ignition being up.

### 5.3 What clients experience during failover

- Vision: brief disconnect banner, automatic reconnect, screens resume.
- Perspective: session drop; browser typically shows a reconnect/error overlay, then reloads the session against the now-Active node. Unsaved view-local (non-tag) state is lost.
- OPC-UA clients consuming Ignition's OPC-UA server: they reconnect per their own client-side retry logic; in-flight subscriptions need to re-establish.
- Alarm notification pipelines (email/SMS): a brief gap is possible around the exact failover moment; already-active alarms and their ack state are preserved as described in §3.2.

## 6. Hub/Spoke vs Distributed Architectures

The **Gateway Network** (not the redundancy pairing mechanism) is what connects multiple, independently-running gateways for data sharing, remote tag providers, and centralized reporting/EAM.

### 6.1 Hub-and-spoke

```
              ┌─────────────┐
              │  Hub / Central │
              │    Gateway     │
              └───────┬────────┘
        ┌──────────────┼──────────────┐
   ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
   │ Spoke A │    │ Spoke B │    │ Spoke C │
   │ (site1) │    │ (site2) │    │ (site3) │
   └─────────┘    └─────────┘    └─────────┘
```

- Spokes connect outbound to the hub (useful when spokes are behind NAT/firewalls and can't accept inbound connections).
- Hub aggregates: remote tag providers exposed from each spoke, centralized alarm rollup, EAM management, centralized reporting.
- Each spoke can independently be a redundant pair or a single gateway — hub/spoke is orthogonal to whether any individual node is itself redundant.
- Failure of the hub does **not** stop spokes from running locally (they keep controlling their own process) — it does stop cross-site visibility/reporting/EAM until the hub recovers. This is a key resilience property: don't centralize control logic on the hub if spokes must survive hub outages.

### 6.2 Distributed / mesh

```
   ┌─────────┐        ┌─────────┐
   │ Gateway │◄──────►│ Gateway │
   │    A    │        │    B    │
   └────┬────┘        └────┬────┘
        │                  │
        │    ┌─────────┐   │
        └───►│ Gateway │◄──┘
             │    C    │
             └─────────┘
```

- Any gateway can establish a direct outgoing Gateway Network connection to any other — used when sites need peer-to-peer data exchange rather than everything funneling through one hub.
- More resilient to a single node's outage (no single aggregation point), but harder to secure/administer (N×N potential connections, more certs/firewall rules to manage) and harder to reason about data flow.
- In practice, most production designs use hub-and-spoke for manageability and add a few point-to-point links only where truly needed (e.g., a DR site pulling directly from two regional hubs).

### 6.3 Choosing a topology

| Requirement | Recommended topology |
|---|---|
| Many small remote sites, unreliable/NAT'd links, central reporting | Hub-and-spoke, spokes outbound-only |
| A handful of large, well-connected sites needing to share data with each other directly | Distributed/mesh (selectively) |
| Enterprise fleet management (patch, backup, monitor many gateways) | Hub-and-spoke with EAM on the hub |
| Disaster recovery between two large redundant pairs at separate DCs | Point-to-point Gateway Network link between the two hubs, plus DB-level replication (see 85-...-CONFIGURATION.md §5) |

## 7. Network Requirements

### 7.1 Ports and connectivity

| Purpose | Default port(s) | Direction | Notes |
|---|---|---|---|
| Gateway web/HTTP | 8088 | Client/inter-gateway | Confirm current default in your installed version; often moved to 80 in production reverse-proxy setups |
| Gateway web/HTTPS | 8043 | Client/inter-gateway | Preferred for anything crossing an untrusted network |
| Gateway Network (inter-gateway, incl. redundancy sync) | Same HTTP(S) port, upgraded connection | Bi-directional between paired/peer nodes | Redundancy sync rides the Gateway Network connection — treat its bandwidth/latency requirements as *higher priority* than ordinary inter-gateway traffic |
| OPC-UA | 4096 (default) | Client → Gateway, and Gateway ↔ field devices | Redundant OPC-UA patterns need this open on both nodes if using independent device connections |
| Database | Per DB vendor (1433 MSSQL, 5432 Postgres, 3306 MySQL, etc.) | Both nodes → DB | Both Active and Backup often need DB reachability for store-and-forward flushing after failover |

Always verify exact port numbers against your installed Ignition 8.3 build's Gateway Network settings — defaults can be changed per-install and have shifted across versions.

### 7.2 Latency and bandwidth

- The Master-Backup link is latency-sensitive: heartbeat and state sync run continuously. High latency (>~50-100ms) or jitter between the pair increases false-failover risk and slows tag-state convergence. **Do not place a redundant pair across a WAN link with variable latency if you can avoid it** — same-DC or same-metro low-latency links are strongly preferred.
- Bandwidth scales with tag count/change rate and history volume, not client count (clients talk to Active only). Size the link for peak tag-change bursts, not steady state.

### 7.3 Firewall / segmentation guidance

- Redundant pair nodes should sit in the same network segment/security zone where possible; if they must cross a firewall, ensure the Gateway Network port has a persistent, prioritized (QoS-tagged) allow rule in both directions.
- For hub-and-spoke over the internet/WAN, terminate spoke connections with HTTPS + gateway network certificates; do not run unencrypted Gateway Network links across untrusted networks.
- DNS/VIP in front of a redundant pair (for client connectivity) should have a short TTL and health-check-driven failover if using a load balancer/VIP approach — see 85-...-CONFIGURATION.md §1 for concrete VIP/DNS patterns.

## 8. Summary: Design Principles

1. Treat Ignition redundancy as a 2-node active/standby pair, always — plan multi-site/multi-gateway resilience with Gateway Network + EAM patterns layered on top, not by expecting native N-node clustering.
2. Budget for minutes-scale failover, not sub-second — communicate this expectation to stakeholders and don't let Ignition redundancy stand in for control-system-level HA.
3. Configuration and tag/alarm runtime state sync automatically; session state, in-flight scripts, and local-disk state do not — design scripts and integrations to be idempotent and resumable.
4. Keep the Master-Backup link low-latency and high-priority on the network; this link is the actual reliability bottleneck of the whole model.
5. License both nodes for full production load, and verify redundancy/module licensing terms explicitly rather than assuming standby discounting.

---

## See Also

**Prerequisites:** [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md)

**Builds toward:** [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md)

**Related:** [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
