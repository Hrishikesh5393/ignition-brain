---
title: Clustering & High Availability Configuration
description: Step-by-step redundant pair setup, tag/DB/OPC-UA failover config, DR procedures, health monitoring, and troubleshooting
---

> **Skill level:** 300 · **Read first:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 85-CLUSTERING-HA-CONFIGURATION

# Clustering & High Availability Configuration

This is the operational companion to 84-CLUSTERING-HA-ARCHITECTURE.md. It walks through building a working redundant pair, wiring up dependent systems (DB failover, OPC-UA redundancy), monitoring cluster health, and the gotchas that actually bite in production. Read the architecture doc first if you haven't — this doc assumes you already know Ignition redundancy is a 2-node active/standby model, not N-node clustering.

## 1. Step-by-Step Cluster Setup

### 1.1 Two-node redundant pair (the baseline)

**Prerequisites**

- Two gateway hosts, same Ignition version and build number (mismatched versions between Master/Backup are not supported — always patch both nodes together).
- Valid redundancy-enabled licenses for both nodes.
- Low-latency network path between the two hosts (same DC/metro strongly preferred — see 84-...-ARCHITECTURE.md §7.2).
- A stable way for clients to reach "whichever node is Active" — either a virtual IP (VIP), a DNS record you can flip, or a load balancer with health checks. Ignition does not provide this piece for you.

**Steps**

1. **Install identical Ignition builds** on both hosts. Do not attempt to pair different minor/patch versions.
2. On the intended **Master**, go to `Config → System → Redundancy`.
3. Set **Redundancy Role = Master**. Configure:
   - **Node address** of the peer (Backup's hostname/IP + Gateway Network port).
   - **Heartbeat/timeout settings** (see §1.3 for tuning guidance).
4. On the **Backup** host, go to the same `Config → System → Redundancy` screen.
5. Set **Redundancy Role = Backup**, pointing back at the Master's address.
6. Save on both. The two gateways will establish a Gateway Network connection and begin negotiating roles — watch `Config → System → Redundancy → Status` on both; you should see Master reach **Active**, Backup reach **Backup (Warm)** once initial sync completes.
7. **Verify initial full sync completed** before relying on the pair — check the redundancy status page for a "synced" indicator and confirm project resource counts match between nodes (Backup is read-only, so compare via Gateway Status → Projects on each).
8. Point your VIP/DNS/load-balancer health check at both nodes' Gateway Status "is this node Active" indicator (see §6.1) so traffic routes to whichever is currently Active.

**Verification checklist**

```
[ ] Both nodes show the same Ignition build number
[ ] Master shows Active, Backup shows Backup (Warm) - not Cold, not Independent
[ ] Project list and resource versions match on both (Gateway Status -> Projects)
[ ] Test tag write on Master appears on Backup's tag browser within a few seconds
[ ] VIP/DNS points at Active node's IP, confirmed by resolving during a controlled failover test
```

### 1.2 Three/four-node examples (site-level, not true N-node clustering)

Since native redundancy is strictly 2 nodes, a "4-node cluster" in practice means **two independent redundant pairs** tied together via the Gateway Network, e.g., a hub pair aggregating from spoke pairs, or two pairs in different roles.

**Example: 4-node DR-capable design**

```
Site A (Primary)                      Site B (DR)
┌───────────────┐                     ┌───────────────┐
│  A-Master      │◄──redundancy sync──►│  A-Backup n/a │  (redundancy pair
│  (Active)      │   (same site,       │  same-site    │   stays within
│                │    low latency)     │               │   Site A)
└───────┬────────┘                     └───────────────┘
        │
        │ Gateway Network (cross-site, point-to-point)
        ▼
┌───────────────┐                     ┌───────────────┐
│  B-Master      │◄──redundancy sync──►│  B-Backup      │  (Site B's own
│  (Active,      │                     │                │   independent
│   standby role │                     │                │   redundant pair)
│   for the app) │                     │                │
└───────────────┘                     └───────────────┘
```

Setup order for this pattern:

1. Build Site A's redundant pair per §1.1.
2. Build Site B's redundant pair per §1.1, independently.
3. On Site A's Master, add a **Gateway Network connection** to Site B's Master (`Config → Networking → Gateway Network → Outgoing Connections`), and the reverse on Site B if bidirectional access is needed.
4. Configure **remote tag providers** on Site B pulling from Site A (or vice versa) so Site B can display/react to Site A's data — this is data visibility, not automatic failover between sites; see §5 for actual DR promotion steps.
5. If Site B should be able to take over Site A's SCADA function during a full-site outage, this requires either database-level replication (§5) plus manual project promotion, or a third-party DR orchestration layer — Ignition does not auto-promote across independent pairs.

### 1.3 Heartbeat/timeout tuning

| Setting | Too aggressive (short) | Too lax (long) | Guidance |
|---|---|---|---|
| Heartbeat interval | False failovers on brief network blips | Slow detection of real outages | Start with vendor defaults; only tighten after observing your network's actual jitter |
| Failover timeout | Same as above, amplified | Extended visibility gap during real outage | Tune per-environment; validate with induced-failure testing (§8) before trusting in production |

Do not guess at specific millisecond values from memory or forum posts — pull the live defaults from your installed build's `Config → System → Redundancy` screen and adjust incrementally, testing each change with a real failover drill.

## 2. Tag Synchronization Configuration

### 2.1 What syncs automatically vs what you must design for

- **In-scope automatically**: memory tags, UDT instances, expression tag results, tag quality/timestamp, alarm state tied to those tags.
- **Requires design attention**:
  - Tags backed by **scripted logic with local Python state** (e.g., a tag change script that accumulates a counter in a module-level variable) — the counter resets on the newly-Active node. Persist such state in a memory tag instead of a bare Python variable if it must survive failover.
  - **OPC tags** whose live values originate from device polling — see §4; the Backup's copy is only as fresh as the last sync tick unless you've set up independent redundant device connections.

### 2.2 Practical pattern: persisting script state across failover

```python
# BAD - lost on failover, only lives in gateway process memory
_counter = 0
def valueChanged(tag, tagPath, previousValue, currentValue, initialChange, missedEvents):
	global _counter
	_counter += 1

# GOOD - counter lives in a memory tag, synced to Backup automatically
def valueChanged(tag, tagPath, previousValue, currentValue, initialChange, missedEvents):
	current = system.tag.readBlocking(["[default]Diagnostics/ChangeCounter"])[0].value
	system.tag.writeBlocking(["[default]Diagnostics/ChangeCounter"], [current + 1])
```

### 2.3 Tag provider scope considerations

- Each **tag provider** (default, or additional providers you create) is synced as part of the paired gateway's overall state — there's no per-provider redundancy toggle; redundancy applies gateway-wide.
- **Remote tag providers** (tags pulled from another gateway over the Gateway Network) add a dependency: if the *source* gateway of a remote tag provider fails, the *consuming* gateway (even if itself perfectly healthy and Active) shows stale/bad-quality tags for that provider. Document these cross-gateway dependencies explicitly — they are a common cause of "why did my healthy Active node show bad tag quality" incidents.

## 3. Database Failover Setup

Ignition's own gateway redundancy is orthogonal to your **historian/application database's** own HA. Both nodes in a pair typically point at the *same* database connection string — the DB itself needs its own failover story.

### 3.1 Recommended pattern: DB-side HA in front of Ignition

```
Ignition Master ──┐
                   ├──► DB Listener/VIP ──► Primary DB
Ignition Backup ───┘         (failover-aware)      │
                                                     ▼
                                              Standby/Replica DB
```

- Configure Ignition's **Database Connection** (`Config → Databases → Connections`) to point at a DB-vendor-provided failover endpoint (e.g., SQL Server AlwaysOn Listener, PostgreSQL with a connection-pooler like pgpool/HAProxy in front of a streaming-replication pair, MySQL/MariaDB with a VIP in front of Galera/Group Replication).
- Set the JDBC connection string's built-in failover/retry parameters where the driver supports them (e.g., SQL Server JDBC `multiSubnetFailover=true` for AlwaysOn, Postgres JDBC `targetServerType=primary` with multiple host entries).
- Ignition's connection pool will retry per its **Connection validation** settings (`Config → Databases → Connections → <name> → Connection Properties`) — tune `Validation Query`, `Max Connection Age`, and retry intervals so a DB failover (typically seconds) doesn't cascade into a longer Ignition-side outage than necessary.

### 3.2 Store-and-forward behavior during DB outages

- While the DB connection is down/failing validation, tag history and transaction group writes queue to the **Store and Forward** buffer (disk-backed, bounded by configured size/duration in `Config → Databases → Store and Forward`).
- On DB reconnect, queued data flushes in order. Monitor the store-and-forward queue depth (§6.2) — a queue that isn't draining faster than it fills indicates the DB failover didn't actually complete or the new primary is under-provisioned.
- **Critical gotcha**: store-and-forward queues are **per-gateway-node**, held on local disk. If the *Ignition* node itself fails (not just the DB) before the queue flushes, that buffered data is lost with it — DB HA does not protect data sitting in an Ignition node's local S&F queue during a simultaneous Ignition-node failure.

### 3.3 Multiple DB connections / read replicas

- If you offload reporting queries to a read replica, remember replicas typically lag the primary — historical queries against a replica immediately after a write can show stale data. Don't point live operational dashboards needing sub-second freshness at a lagging replica.

## 4. OPC-UA Redundancy in Clustered Environments

### 4.1 Default behavior (single-owner polling)

By default, only the **Active** gateway node actively polls/subscribes to OPC-UA devices; the Backup relies on the in-memory tag sync from the Active (see 84-...-ARCHITECTURE.md §3.2). This minimizes load on field devices (they see one client, not two) but means **device-level connection health on the Backup is unverified** until it actually activates.

### 4.2 Independent redundant device connections (faster failover, more device load)

For devices/PLCs that support multiple simultaneous OPC-UA/native-driver client connections, you can configure **both** nodes to independently connect to the device:

```
Device (e.g., Allen-Bradley PLC, Siemens PLC, OPC-UA server)
        │                              │
   connection 1                   connection 2
        │                              │
        ▼                              ▼
   Master (Active)                Backup (standby polling)
```

- Configure the device connection identically on both nodes (`Config → OPC UA → Device Connections`), each pointing at the same device endpoint.
- On failover, the newly-Active node already has a warm, established device connection — it doesn't need to spend the first several seconds of activation opening new sockets/handshakes to every field device, meaningfully shortening the "full parity restored" phase from 84-...-ARCHITECTURE.md §5.2.
- **Trade-off**: doubles the polling load on each device/PLC. Verify the device's/driver's max simultaneous client connections before enabling this broadly — some PLC firmware has low client connection ceilings (sometimes as few as 2-4), and this pattern can starve out other legitimate clients (e.g., engineering workstations) if not budgeted for.

### 4.3 OPC-UA server-side redundancy (Ignition as an OPC-UA server to external clients)

- External OPC-UA clients connecting *to* Ignition's built-in OPC-UA server should be configured with **both nodes' endpoints** in their own client-side redundancy list (most mature OPC-UA client stacks support a list of endpoint URLs with automatic failover) — Ignition doesn't rewrite external clients' connections for them.
- Certificates: if using OPC-UA security (Sign/SignAndEncrypt), each node has its own server certificate by default. External clients need to trust *both* nodes' certificates ahead of time, or you need a shared certificate/SAN strategy, or failover will succeed at the network level but fail at the OPC-UA security handshake level — test this explicitly, it's a frequent silent failure mode.

## 5. Disaster Recovery Procedures

DR here means recovering from a scenario where **both** nodes of a pair (or an entire site) are lost — beyond what same-pair failover covers.

### 5.1 Backup export/import (baseline, always do this regardless of redundancy)

```
Config -> System -> Backup/Restore -> Create Backup
```

- Schedule automated `.gwbk` backups (Gateway Backup) on a cron/EAM schedule, stored off-node (network share, object storage, or EAM central repository).
- A `.gwbk` captures project resources, gateway configuration, and (optionally) the internal database — restoring it to a fresh gateway is your ultimate DR path when both nodes of a pair are gone.
- **Test restores periodically.** A backup you've never restored is a hope, not a plan.

### 5.2 Cross-site DR promotion (when Site A is fully down)

1. Confirm Site A is actually unreachable, not just experiencing a transient network partition — promoting Site B while Site A is still partially live risks split-brain writes to shared downstream systems (historian DB, MES, etc.).
2. Restore or activate Site B's standby project set (kept current via Gateway Network remote tag providers/EAM-scheduled config sync, or via periodic `.gwbk` restore from Site A's backups).
3. Repoint external integrations (MES, SCADA HMI DNS/VIP, alarm notification endpoints, third-party OPC-UA clients) at Site B.
4. Once Site A is recovered, treat it as the *new Backup/DR site* rather than immediately flipping back — validate data consistency (especially any tag writes/alarms generated on Site B during the outage window) before any re-promotion.
5. Document and rehearse this as a runbook — DR that only exists as an idea in someone's head is not DR.

### 5.3 RPO/RTO expectations to set with stakeholders

| Scenario | Realistic RPO | Realistic RTO |
|---|---|---|
| Same-pair failover (Master dies, Backup takes over) | Near-zero for tag/alarm state; possible seconds of un-flushed S&F history | Tens of seconds to ~a couple minutes (per 84-...-ARCHITECTURE.md §5.2) |
| DB failover (DB HA layer handles it) | Near-zero to seconds, depending on DB HA technology | Seconds to low minutes |
| Full-site DR promotion | Since last successful config sync / backup — could be hours if relying only on scheduled `.gwbk` backups | Manual runbook execution time — realistically 30 min to several hours depending on rehearsal maturity |

## 6. Monitoring Cluster Health

### 6.1 Built-in status surfaces

- `Config → System → Redundancy → Status` on each node: current role, peer reachability, sync state (Warm/Cold/Independent).
- **Gateway Status → Overview**: shows Activity Level prominently — this is the field to key an external health-check (VIP/LB) off of.
- **Diagnostics → Logs**: filter for the redundancy/`GatewayRedundancy` logger; role transitions and sync failures log here first.

### 6.2 What to alert on (build these into your existing monitoring stack, e.g., via Ignition's own alarm system pointed at diagnostic tags, or an external tool polling the Gateway's status API/webpage)

| Metric | Alert condition | Why it matters |
|---|---|---|
| Backup sync state | Not "Warm" for > a few minutes | Cold backup means failover will not be seamless |
| Redundancy role flapping | More than 1 role change in a short window | Indicates network instability or mistuned heartbeat timeouts (see §1.3) |
| Store-and-forward queue depth | Growing, not draining | DB connection degraded/failed; risk of data loss if node also fails |
| Gateway Network connection status (hub/spoke links) | Any configured outgoing/incoming connection down | Loss of cross-site visibility even if local site is healthy |
| License/activation state on both nodes | Any non-valid state | Backup won't legally/functionally activate without a valid license |
| Device connection status (both nodes, if using independent redundant device connections per §4.2) | Any device down on either node | Silent Backup-side device failure won't surface until an actual failover |
| Disk space on both nodes | Approaching capacity | Store-and-forward and internal DB (if used) both need headroom; a full disk during a DB outage turns a recoverable event into data loss |

### 6.3 External health checks for VIP/LB routing

Poll each node's Gateway Status page (or a lightweight dedicated endpoint if your version exposes one) for Activity Level, and route traffic only to the node currently reporting Active. Don't rely on plain TCP-connect health checks against the gateway port — a Backup node is up and answering connections but should not receive client traffic.

## 7. Common Clustering Gotchas & Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Backup activated with an old project version after failover | Config change on Master hadn't finished propagating before crash | Always verify sync status before/after any config push; don't treat "saved on Master" as "safe on Backup" |
| Both nodes claim Active simultaneously (split-brain) | Network partition between the pair while both still see clients/devices | Fix network path reliability first (84-...-ARCHITECTURE.md §7); verify tie-breaker configuration; manually force one node to Standby to resolve immediately |
| Backup stuck in "Cold" indefinitely | Initial sync never completed (large project, slow/high-latency link, or an error mid-sync) | Check Diagnostics logs on Backup for sync errors; verify network throughput between nodes; retry by forcing a resync if your build exposes that action |
| Mismatched Ignition build numbers between nodes | One node was patched, the other wasn't | Always patch both nodes in the same maintenance window; treat version parity as a hard requirement, not best-effort |
| Clients don't reconnect after failover | VIP/DNS/LB not actually health-checking Activity Level (see §6.3), or client-side retry/backoff misconfigured | Fix the health-check target; for custom OPC-UA/API clients, confirm they implement endpoint-list failover |
| OPC-UA clients fail to reconnect after failover despite network being fine | Certificate trust mismatch between nodes (see §4.3) | Pre-trust both nodes' certs on every external client, or unify certificate strategy |
| Store-and-forward queue balloons and doesn't drain | DB "failover" only partially succeeded (e.g., replica is read-only, connection string still points at dead primary) | Validate the DB connection's actual writable target post-failover, not just reachability |
| Devices intermittently drop after enabling independent redundant device connections | PLC/device client-connection ceiling exceeded (see §4.2) | Check device/driver max simultaneous connections; fall back to single-owner polling if the device can't support two clients plus other legitimate clients |
| Alarms re-fire (duplicate notifications) right after failover | Alarm state sync lagged the crash, or notification pipeline retried an in-flight send | Confirm alarm journal/state sync latency in your environment; make notification integrations idempotent where possible |
| Gateway Network connection between hub and spoke silently down for hours before anyone notices | No explicit alert on Gateway Network connection status | Add the connection-status alert from §6.2; don't rely on someone happening to look at the topology screen |
| "Working" pair fails its first real failover test in production | Never actually tested failover under realistic load before go-live | Always run induced-failure drills (§8) before trusting a pair in production, and periodically thereafter |

## 8. Performance Tuning for Clustered Gateways

### 8.1 Tag sync overhead

- Every tag write on the Active node has a marginal cost to propagate to the Backup. At very high tag-change rates (tens of thousands of changes/sec), this sync traffic can itself become the bottleneck on the inter-node link before it becomes a bottleneck on either gateway's CPU. Monitor the Master-Backup link utilization, not just each gateway's own CPU/memory (per 83-PERFORMANCE-TUNING.md general guidance), when diagnosing slowness in a redundant pair.
- Reduce unnecessary tag churn (deadband tuning on OPC tags, avoiding needlessly high-frequency expression tag recalculation) — this helps single-node performance per 83-PERFORMANCE-TUNING.md and *also* directly reduces redundancy sync load.

### 8.2 Backup node sizing

- Don't under-provision the Backup "because it's just standby." The moment it activates, it *is* production, at full load. Size CPU/memory/disk identically to the Master.
- If using independent redundant device connections (§4.2), the Backup's device-driver subsystem is under real load even while standby — budget CPU for that, it's not free just because it's not serving clients.

### 8.3 Gateway Network link sizing for hub/spoke

- A hub aggregating many spokes' remote tag providers pays a steady-state bandwidth/CPU cost proportional to the total tag-change rate across all spokes, not just its own local tags. Size the hub gateway's hardware for the *sum* of what it's aggregating, and re-evaluate as spokes are added — this is a common "hub gateway slowly degrades as we onboard more sites" root cause.
- Prefer filtering/subscribing to only the tags actually needed on the hub (rather than exposing entire spoke tag trees as remote providers wholesale) to keep this cost bounded.

### 8.4 Database write path under redundancy

- Both nodes typically share one DB target; ensure the DB itself is sized for peak write rate from a single Active node at a time (redundancy doesn't double DB write load in steady state — only one node writes at once) but *does* need to absorb a burst when a store-and-forward queue flushes after a reconnect (§3.2) — that flush can be a meaningful spike above steady-state rate, so don't size the DB purely off average throughput.

## 9. Pre-Production Checklist

```
[ ] Both nodes on identical Ignition build/version
[ ] Redundancy licenses valid on both nodes, sized for full production load
[ ] Master-Backup link is low-latency, same-DC/metro where possible, QoS-prioritized
[ ] VIP/DNS/LB health check keys off Activity Level, not plain TCP reachability
[ ] DB connection points at a DB-vendor HA endpoint, not a single static host
[ ] Store-and-forward buffer sized for realistic outage duration + disk headroom verified
[ ] OPC-UA redundant device connections evaluated against each device's client-connection ceiling
[ ] External OPC-UA/API clients configured with both nodes' endpoints and trust both certs
[ ] Monitoring/alerting wired for: sync state, role flapping, S&F queue depth, Gateway Network link status, license validity, disk space
[ ] .gwbk backups scheduled off-node and restore has been test-run at least once
[ ] Cross-site DR runbook written and rehearsed at least once, not just documented in theory
[ ] Induced-failure drill performed under realistic load with stakeholders watching, before go-live
```

---

## See Also

**Prerequisites:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md)

**Builds toward:** [87-GATEWAY-OPERATIONS-RUNBOOK](87-GATEWAY-OPERATIONS-RUNBOOK.md)

**Related:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [25-PLATFORM-TAGS-ARCHITECTURE](25-PLATFORM-TAGS-ARCHITECTURE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
