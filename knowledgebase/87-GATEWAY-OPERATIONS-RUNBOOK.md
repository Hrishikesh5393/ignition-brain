---
title: Gateway Operations Runbook
description: Startup/shutdown procedures, log rotation, backup verification, upgrades, and emergency restart scenarios
---

> **Skill level:** 300 · **Read first:** 61-GATEWAY-MANAGEMENT, 62-LOGGING-DIAGNOSTICS · **Part of:** Operations track
> **You are here:** [00-INDEX](00-INDEX.md) › Operations › Gateway Operations Runbook

# Gateway Operations Runbook

Day-2 operational procedures for running Ignition Gateways in production. This is the "what do I actually type/click" companion to [[61-GATEWAY-MANAGEMENT]] (concepts) and [[84-CLUSTERING-HA-ARCHITECTURE]] (redundancy theory).

## 1. Startup / Shutdown Procedures

**Standard startup (service-managed):**
1. Verify DB connections reachable before starting Gateway (`telnet <db-host> <port>` or equivalent) — Gateway will start without DB but tags/history will queue/fail until connection resolves.
2. Start the Ignition service (`systemctl start ignition` on Linux, Services console or `net start Ignition Gateway` on Windows).
3. Tail `wrapper.log` during startup — watch for `INFO | ... | Ignition Gateway starting...` through `Gateway startup complete`.
4. Confirm via Gateway webpage (`https://<host>:8043/`) — Status → Overview should show all modules "Running," no red module states.
5. Spot-check a known-good tag read and a Perspective session before declaring healthy.

**Graceful shutdown:**
1. Warn connected users (Perspective session banner / Vision message via `system.gui.messageBox` scripted broadcast, or just accept in-flight session drop for planned maintenance windows).
2. Stop via service manager, not `kill -9` — this lets the Gateway close DB connections, flush store-and-forward buffers, and release device driver sockets cleanly.
3. Confirm process fully exits (`wrapper.log` shows shutdown complete) before any disk/config work.

**Gotcha:** killing the JVM process directly (not via wrapper) can leave lock files that block the next startup — always stop through the service/wrapper, never `kill -9` the java process.

## 2. Log Rotation

- Gateway logs (`wrapper.log`, and the internal Gateway Logs viewer backed by an internal DB table) rotate automatically by default (size- and count-limited), configured in `ignition.conf` (`wrapper.logfile.maxsize`, `wrapper.logfile.maxfiles`).
- For high-volume systems, reduce retained Gateway Logs history (Config → System → Gateway Settings) to control the internal logging DB table size — this table can bloat the internal SQLite/embedded DB on long-uptime, high-log-volume gateways.
- Ship logs externally (syslog forward, or scheduled log-file archival) for anything needing >30 days retention or off-box audit trails; don't rely on the Gateway's own rotation as a long-term archive.

See [[62-LOGGING-DIAGNOSTICS]] for log locations and levels.

## 3. Backup Verification

A backup you haven't test-restored is a hope, not a backup.

1. **Take backup:** Config → Backup/Restore → Create Gateway Backup (`.gwbk` file) — includes projects, tag configs (not history data), Gateway config, module configs.
2. **Store off-box** immediately (the backup is worthless if it lives on the same disk as the failure that necessitates it).
3. **Verify quarterly (minimum):** restore the `.gwbk` to a scratch/staging Gateway instance, confirm projects open, tag counts match, and a sample Perspective view renders.
4. **Document restore time** — this is your actual RTO (Recovery Time Objective), not the vendor's marketing number. Include DB-side restore time if the DB isn't independently backed up (Gateway backup does NOT include historian/DB data — that's a separate DB backup job).

**Gotcha:** `.gwbk` does not include external DB data (tag history, alarm journal rows). A full DR plan needs the Gateway backup AND a coordinated DB backup with compatible timestamps — see [[91-DATABASE-FAILOVER-REPLICATION]].

## 4. Performance Monitoring

Baseline these during known-good operation so you have something to compare against during an incident:

- **JVM heap usage** — Status → Performance; sustained >80% with frequent full GC pauses signals undersized heap or a leak (see [[83-PERFORMANCE-TUNING]]).
- **Thread counts** — runaway thread growth (especially in script execution pools) indicates blocking calls in event scripts (missed `system.util.invokeAsynchronous` usage).
- **Tag execution rate / scan class overruns** — Status → Tags shows overrun counts; frequent overruns mean scan classes are too aggressive for the device/DB load.
- **DB connection pool utilization** — near-100% pool usage under normal load means the pool is undersized or queries are running long (see [[90-DATABASE-ADVANCED-OPTIMIZATION]]).

## 5. Diagnostic Data Collection

When escalating to support or doing root-cause analysis, collect in one pass (avoid multiple back-and-forth requests during an active incident):

1. Gateway backup (`.gwbk`) — captures config state at time of issue.
2. Thread dump — Status → Threads → "Dump Threads" (take 2-3, 10 seconds apart, to see if threads are stuck vs. progressing).
3. Recent `wrapper.log` (full file, not just tail — the root cause is often earlier than the visible symptom).
4. Gateway Logs export filtered to the incident time window.
5. System info (Status → System) — memory, CPU, module versions, OS/JVM version.

## 6. Upgrade Procedures

1. **Read release notes fully** — check for breaking changes to scripting APIs, module compatibility, and DB schema migrations before upgrading.
2. **Backup first** (Section 3) — non-negotiable, upgrades can fail mid-migration.
3. **Test in staging** — restore production backup to a staging Gateway, perform the upgrade there first, validate projects/scripts/bindings still function.
4. **Upgrade sequence for redundant pairs:** upgrade the Backup node first, confirm it starts clean and can sync, then force failover, then upgrade the former-Master (now Backup) — see rolling restart notes below and [[85-CLUSTERING-HA-CONFIGURATION]].
5. **Post-upgrade smoke test:** verify each module's status, spot-check bindings/scripts that use version-sensitive APIs, confirm device driver reconnection.

## 7. Rolling Restart (Clustered / Redundant Pairs)

For a redundant pair (see [[84-CLUSTERING-HA-ARCHITECTURE]]), avoid simultaneous restart of both nodes:

1. Confirm current Active/Backup roles and that Backup is fully synced ("Warm," not "Cold") before touching anything.
2. Restart the **Backup** node first. Wait for it to rejoin and resync.
3. Once Backup is confirmed Warm again, force failover (manual "Force Active") to make it the new Active.
4. Restart the now-Backup (former Active/Master) node.
5. Optionally force failback if you require the original Master to resume the Active role (not automatic by design — see [[84-CLUSTERING-HA-ARCHITECTURE]] §2.2).

This sequence keeps one node serving clients/devices at all times, at the cost of one failover event (which is why maintenance windows matter even with redundancy — client sessions still reconnect across the failover).

## 8. Emergency Restart Scenarios

**Gateway unresponsive (webpage hangs, no log output):**
1. Take a thread dump if the JVM still responds to `jstack`/service manager tools — this is your best root-cause evidence before you kill anything.
2. If truly hung, restart via service manager (not `kill -9`) to allow whatever graceful shutdown hooks can still fire.
3. Post-restart, immediately pull the thread dump + logs for later analysis — don't let the "it's working again" relief skip the root-cause step, or the same freeze recurs.

**Split-brain suspected (both nodes claim Active):**
1. Do NOT restart either node blindly — this can worsen data divergence.
2. Identify true source of truth (which node has been serving client writes) via application-level evidence (last DB write timestamps, most recent alarm events).
3. Force the incorrect node to Backup role manually, resync, then investigate the network path between the pair (see [[84-CLUSTERING-HA-ARCHITECTURE]] §2.3 tie-breaking) before returning to normal operation.

**Runaway resource consumption (memory/CPU spike):**
1. Thread dump + heap dump before restart if system is still somewhat responsive — a post-mortem restart with no diagnostic capture just guarantees a repeat incident.
2. Restart the Gateway service.
3. Cross-reference the spike time against recent project deployments or script changes — most runaway-resource incidents trace to a newly deployed script lacking proper scope/async handling (see [[81-GOTCHAS-BUGS]]).

---

## See Also

**Prerequisites:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)
**Builds toward:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md)
**Related:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [91-DATABASE-FAILOVER-REPLICATION](91-DATABASE-FAILOVER-REPLICATION.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
