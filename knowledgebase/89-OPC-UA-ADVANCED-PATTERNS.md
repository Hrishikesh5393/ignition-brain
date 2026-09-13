---
title: OPC-UA Advanced Patterns
description: Certificate management, redundant servers, aggregation, large-scale subscriptions, browse optimization, historical access, PubSub, troubleshooting, diagnostics
---

> **Skill level:** 300 · **Read first:** [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 89-OPC-UA-ADVANCED-PATTERNS

# OPC-UA Advanced Patterns

Enterprise OPC-UA deployments go beyond a single Gateway talking to a single PLC. This document covers certificate lifecycle management, redundant/failover server topologies, federating multiple OPC-UA sources, scaling subscriptions across thousands of tags, PubSub as an alternative transport, and a systematic troubleshooting/diagnostics workflow. Pairs with `88-OPC-UA-SERVER-CONFIGURATION.md`.

## Certificate Management

Every OPC-UA endpoint using a security policy above `None` requires an X.509 certificate for the server, and — for `Sign`/`SignAndEncrypt` sessions — the client presents its own certificate as well. Certificate mismanagement is the single most common cause of "works in testing, fails in production" OPC-UA outages.

### Generating Certificates

Ignition auto-generates a **self-signed server certificate** on first startup, sufficient for internal/lab use. For production:

```
Gateway Config → OPC-UA → Security → Certificates → Server Certificate
  Options:
    - Use auto-generated self-signed cert (default, lab/testing only)
    - Generate CSR → sign with internal/enterprise CA
    - Import existing PKCS#12 (.p12/.pfx) certificate + private key
```

**Recommended enterprise flow:**
1. Generate a Certificate Signing Request (CSR) from the Gateway, specifying the correct Subject Alternative Names (SANs) — must include every hostname/IP clients will use to connect (mismatches cause silent trust failures).
2. Submit the CSR to your internal CA (or a public CA if external partners connect).
3. Import the signed certificate chain back into the Gateway's Certificate Manager.
4. Distribute the CA root certificate to all client trust stores instead of trusting each server certificate individually — this scales far better than pairwise trust.

### Certificate Trust Model

OPC-UA trust is **explicit and mutual** — the server must trust the client's certificate AND the client must trust the server's certificate before a secure session establishes. Ignition's Certificate Manager maintains three lists:

```
Gateway Config → OPC-UA → Security → Certificates
  - Trusted Certificates (client certs this server will accept)
  - Rejected Certificates (auto-populated when an unknown client connects — review and promote if legitimate)
  - Issuer Certificates (CA certs, enables chain-of-trust validation instead of per-cert trust)
```

**Operational pattern:** when a new legitimate client connects for the first time, its certificate lands in "Rejected." An administrator reviews the thumbprint/subject out-of-band (confirm with the integration owner) and manually moves it to "Trusted." Never bulk-trust the Rejected list without verification — it is, by design, also where connection attempts from misconfigured or malicious clients land.

### Renewal

Certificates carry expiration dates (commonly 1–5 years depending on CA policy). Expiration causes **hard session failures** with no graceful degradation — plan renewal before expiry, not after failure:

- Track certificate expiration dates in your maintenance calendar/CMMS, not just Ignition's UI.
- Renew via the same CSR flow above; the Gateway can hold both old and new certificates during a transition window if configured with overlapping validity.
- After renewal, **redistribute the new server certificate (or CA root, if using chain trust) to all clients** — this is the step most commonly forgotten, resulting in "certificate expired, reconnecting" loops even though the server-side renewal succeeded.

### Distribution at Scale

For deployments with many OPC-UA clients (dozens of Gateway Network peers, MES integrations, SCADA bridges), prefer **CA-chain trust over per-certificate trust**:

| Model | Trust unit | Renewal impact |
|---|---|---|
| Per-certificate trust | Individual server/client cert | Every renewal requires redistributing to every peer |
| CA-chain trust | Root/intermediate CA cert | Server cert can rotate freely as long as it's signed by the trusted CA; peers need no update |

## Redundant OPC-UA Servers (Failover)

Ignition's **Redundancy** module extends to OPC-UA: a redundant pair (Master/Backup Gateway) can each run an OPC-UA server, with external clients configured to fail over between them.

### Topology

```
Master Gateway (opc.tcp://master:4096) ←── Active
Backup Gateway (opc.tcp://backup:4096)  ←── Standby, mirrors tag state via redundancy sync

External OPC-UA Client
  Endpoint list: [master, backup]
  Reconnect policy: on session failure, attempt next endpoint in list
```

Ignition's own redundancy handles Master↔Backup state synchronization (tag values, historian buffering, alarm state) transparently — the OPC-UA server on each node simply exposes whatever tag state that node currently holds. The **client's** responsibility is detecting the Master's unavailability and reconnecting to the Backup's endpoint; this is standard OPC-UA client failover behavior, not an Ignition-specific extension, so client library support varies.

### Design Considerations

- **Warm standby, not hot failover at the protocol level** — there is a brief gap (seconds) during Master→Backup transition where OPC-UA sessions must fully reconnect (new SecureChannel, new Session, re-subscribe). Applications sensitive to sub-second data gaps need local buffering/interpolation on the client side, not reliance on seamless OPC-UA continuity.
- **Subscriptions are not preserved across the failover** — the client's Subscriptions and Monitored Items live on whichever server node accepted the session; a failover client must re-create subscriptions against the new endpoint. Design client reconnect logic to re-subscribe automatically rather than assuming subscription state survives.
- **Endpoint discovery**: configure clients with both Master and Backup endpoint URLs explicitly rather than relying on OPC-UA Discovery Server auto-detection in redundant topologies — discovery adds a failure mode of its own during the exact outage window you're trying to survive.
- Verify certificate trust is configured identically on **both** Master and Backup — a client trusting only the Master's certificate will fail to establish a secure session against the Backup during failover, defeating the purpose.

## OPC-UA Aggregation (Federating Multiple Servers)

"Aggregation" here means a single Ignition Gateway acting as an OPC-UA **client to multiple upstream OPC-UA servers**, then re-exposing a unified view as its own OPC-UA **server** — collapsing a multi-vendor, multi-site OPC-UA landscape into one integration point for downstream consumers (MES, historian, cloud gateway).

### Pattern

```
Site A OPC-UA Server (vendor X) ─┐
Site B OPC-UA Server (vendor Y) ─┼──> Aggregation Gateway (OPC-UA client to all three)
Site C OPC-UA Server (Ignition) ─┘         │
                                            └──> Re-exposed as unified OPC-UA server
                                                 (or consumed directly by Perspective/scripts)
```

### Configuration

Each upstream server is added as a standard OPC-UA **Device connection** on the aggregation Gateway:

```
Gateway Config → Devices → New Device → OPC-UA Server
  Name: SiteA
  Endpoint URL: opc.tcp://sitea-server:4840
  Security Policy: Basic256Sha256
  Authentication: Certificate or Username/Password per Site A's requirements
```

Tags from each site land under `[SiteA]`, `[SiteB]`, `[SiteC]` tag providers (or a shared provider with namespaced folders, per your naming convention). The aggregation Gateway's own OPC-UA server then re-exposes all three under its unified namespace, per `88-OPC-UA-SERVER-CONFIGURATION.md`.

### Design Considerations

- **Namespace collisions**: if two upstream sites use identical tag naming conventions (e.g., both have `Line1/Temperature`), enforce a folder-per-site convention on the aggregation Gateway to avoid ambiguity for downstream consumers.
- **Latency stacking**: each additional hop adds subscription/publish latency. A value change at Site A propagates: PLC → Site A server → aggregation Gateway (client-side subscription) → aggregation Gateway (server-side re-publish) → downstream client. Budget cumulative latency accordingly for control-adjacent use cases; aggregation is appropriate for monitoring/MES/reporting, not tight control loops.
- **Single point of failure**: the aggregation Gateway becomes a dependency for all downstream consumers even if individual sites are healthy. Pair with redundancy (above) for any aggregation Gateway serving business-critical downstream systems.
- **Security policy translation**: the aggregation Gateway can (and should) present a uniform, stronger security posture downstream even if upstream site connections vary in policy quality — it's a natural point to enforce a security floor.

## Large-Scale Subscription Management

Enterprise deployments commonly expose tens of thousands of tags via OPC-UA to multiple downstream consumers. Beyond the basic tuning in `88-OPC-UA-SERVER-CONFIGURATION.md`, at scale:

### Subscription Sharding

Rather than one client maintaining a single subscription with 20,000 monitored items, shard by logical grouping (area, line, priority tier):

```
Subscription "Critical" — Publishing Interval: 250ms  — Alarms, safety interlocks, ~500 items
Subscription "Process"  — Publishing Interval: 1000ms — Process values, ~5000 items
Subscription "Slow"     — Publishing Interval: 5000ms — Setpoints, config, rarely-changing, ~10000 items
```

This lets fast-changing critical data publish promptly without paying the cost of evaluating slow-changing configuration tags at the same rate.

### Deadband Filtering

Configure **Monitored Item deadbands** (absolute or percent) on analog values so trivial noise-level fluctuations don't generate publish traffic:

```
Monitored Item: Temperature
  Filter: DataChangeFilter
  DeadbandType: Percent
  DeadbandValue: 0.5   (only publish on >0.5% change)
```

Deadband filtering is configured client-side (in the MonitoredItem request) but enforced server-side — it materially reduces server evaluation and network overhead when applied broadly across noisy analog tag sets.

### Server Capacity Planning

| Tag count exposed | Guidance |
|---|---|
| < 5,000 | Default server settings generally sufficient |
| 5,000–50,000 | Increase `Max Monitored Items per Subscription`, tune JVM heap, monitor GC pauses |
| > 50,000 | Consider aggregation-tier splitting (multiple Gateways each owning a tag subset), dedicated hardware sizing, and sharding subscriptions per consumer as above |

Monitor heap and GC behavior under load via `Gateway Config → Status → Performance` — OPC-UA subscription evaluation is a recurring background task, and sustained high monitored-item counts show up first as GC pause frequency before manifesting as client-visible lag.

## Browse Path Optimization

External clients frequently need to **Browse** the address space (discover available nodes) before subscribing, especially during initial integration or dynamic tag discovery. Naive recursive browsing of a large address space is slow and load-intensive.

### Guidance

- **Avoid recursive "browse everything" patterns** in client code — browse one level at a time and let the integration target specific known subtrees rather than crawling the entire namespace on every startup.
- Use **TranslateBrowsePathsToNodeIds** when the client already knows the logical path (e.g., from a config file or prior discovery) — this resolves a path to a NodeId in one round-trip instead of a multi-level Browse sequence.
- Cache resolved NodeIds client-side across sessions; NodeIds are stable for a given tag as long as the tag isn't renamed/moved, so re-resolving on every connect is wasted overhead.
- On the server side, deep/wide folder hierarchies with thousands of siblings under one folder slow Browse response times — prefer moderately balanced folder structures (hundreds, not tens of thousands, of direct children per folder) if you control the tag organization.

## Historical Access (Backfilling Historical Data)

OPC-UA defines the **Historical Access** (HA) service set for querying time-series data (`ReadRawModified`, `ReadProcessed`, `ReadAtTime`). Ignition's Tag Historian integrates with this so external OPC-UA HA clients can query Ignition-stored history directly, and Ignition itself can act as an HA client against upstream historian-capable OPC-UA servers for backfill.

### Exposing Ignition History via OPC-UA HA

```
Gateway Config → OPC-UA → Server → Settings → History
  Enable Historical Access: true
  Exposed history source: Tag Historian (per provider)
```

Once enabled, historized tags report `AccessLevel` including `HistoryRead`, and external clients can issue `ReadRaw` (raw stored values) or `ReadProcessed` (aggregates: average, min, max, count over an interval) requests against the standard time range parameters.

### Backfilling from an Upstream OPC-UA HA Source

When a device or edge Gateway buffers historical data locally (e.g., during a network outage) and exposes it via OPC-UA HA, a central Gateway can backfill:

1. Configure the upstream as an OPC-UA Device connection (see Aggregation above).
2. Use `system.tag.queryTagHistory` against `[edgeProvider]` tags is only valid if that provider is itself locally historized on the central Gateway — for **pulling** raw history from an upstream OPC-UA HA server directly, use scripted OPC-UA HA client calls or Ignition's store-and-forward buffering, which handles reconnect gaps automatically for tags historized through a live OPC subscription.
3. For scenarios needing an explicit one-time backfill of a known outage window, script a `ReadRaw` request against the source's historical NodeId for the specific time range, then bulk-insert into the target historian via `system.tag.storeTagHistory` (Ignition 8.1+/8.3 scripting function) rather than relying on live re-subscription, which only captures data from "now" forward.

**Key gotcha:** live tag subscriptions (store-and-forward) only buffer data going forward from connection loss — they cannot retroactively fill a gap that predates the subscription's own buffer window if the buffer itself overflowed (e.g., outage longer than the configured store-and-forward retention). True backfill of a long historical gap requires an explicit HA `ReadRaw`/`ReadProcessed` query against a source that independently retained the data (device-local historian, edge Gateway historian) for the full outage duration.

## PubSub Mode (vs. Traditional Client/Server)

OPC-UA **PubSub** is a publish-subscribe transport alternative to the classic client/server (SecureChannel/Session) model, using UDP multicast or MQTT/AMQP as the underlying transport rather than a persistent TCP session per client.

### Client/Server vs. PubSub

| Aspect | Client/Server | PubSub |
|---|---|---|
| Connection model | Persistent session per client | Publisher broadcasts; any number of subscribers listen, no per-subscriber session |
| Transport | TCP (`opc.tcp://`) | UDP multicast or MQTT/AMQP broker |
| Scalability to many consumers | Server load scales with client count | Publisher load is constant regardless of subscriber count |
| Security | Basic128Rsa15 / Basic256Sha256 with Sign/SignAndEncrypt at the session layer | Basic256Sha256PubSub — message-level signing/encryption since there's no session to secure |
| Typical use case | Point-to-point integration, tight request/response (browse, method call, historical query) | One-to-many broadcast — edge-to-cloud telemetry, many identical dashboard consumers |

### When to Use PubSub

- Broadcasting the same tag set to many independent consumers (multiple dashboards, multiple cloud endpoints) without linearly scaling server-side session/subscription overhead.
- MQTT-transport PubSub aligns naturally with Ignition's existing MQTT Transmission/Engine modules if the deployment already has an MQTT broker (Sparkplug-adjacent architectures) — PubSub-over-MQTT and Sparkplug B are related but distinct; don't conflate them when designing the integration.
- Edge-to-cloud scenarios where maintaining thousands of persistent TCP sessions back to a central server is undesirable.

### When to Stay on Client/Server

- Any use case requiring request/response semantics — Browse, Method calls, Historical Access queries — PubSub has no equivalent to these; it is data-broadcast only.
- Environments where UDP multicast is blocked or unreliable (common across routed/segmented industrial networks) and no MQTT broker is available.
- Point-to-point integrations where a single well-known consumer exists — client/server's per-session flow control and acknowledgment give tighter delivery guarantees than a fire-and-forget broadcast.

## Troubleshooting OPC-UA Connections

Work through this order for any connection failure:

### 1. Network Reachability

```
Test: telnet <gateway-host> 4096  (or Test-NetConnection on Windows)
Expect: connection succeeds (no timeout, no refused)
```

Refused → firewall blocking port 4096, or OPC-UA server module not running.
Timeout → routing/firewall issue further upstream, or wrong hostname/IP.

### 2. Endpoint/Security Mismatch

**Symptom:** Client's endpoint discovery shows no compatible security policy, or connection is rejected immediately after SecureChannel open.

**Check:** Does the client support one of the security policies actually published by the server (`88-OPC-UA-SERVER-CONFIGURATION.md` → Security Policies)? A client hardcoded to `Basic128Rsa15` fails silently against a server that has disabled that legacy policy.

### 3. Certificate Trust

**Symptom:** SecureChannel opens, but Session activation fails with a certificate-related status code (`BadCertificateUntrusted`, `BadCertificateHostNameInvalid`, `BadCertificateTimeInvalid`).

**Check:**
```
Gateway Config → OPC-UA → Security → Certificates → Rejected
  Look for the client's certificate — confirm thumbprint matches expected, promote to Trusted if valid
```

`BadCertificateHostNameInvalid` specifically indicates the connection URL's hostname doesn't match the server certificate's SAN — fix by regenerating the certificate with the correct SAN or connecting via the correct hostname.

### 4. Session/Identity Rejection

**Symptom:** SecureChannel and initial handshake succeed, but session activation fails with `BadUserAccessDenied` or `BadIdentityTokenRejected`.

**Check:** Anonymous access disabled but client attempting anonymous? Username/password mismatched against the configured User Source? Certificate identity not mapped to any role?

### 5. Browse/Subscribe Failures After Successful Connection

**Symptom:** Session activates, but Browse returns empty or specific tags are missing from subscription results.

**Check:** Tag Provider's "Enable OPC-UA Server exposure" flag; Security Zone permissions restricting the authenticated identity's read access to that tag subtree (see User Mapping in `88-OPC-UA-SERVER-CONFIGURATION.md`).

## Performance Monitoring & Diagnostics

### Gateway-Side Diagnostics

```
Gateway Config → Status → OPC-UA → Server
  - Active Sessions (count, per-client identity, connect time)
  - Active Subscriptions (count, publishing intervals in use)
  - Monitored Items (total count across all subscriptions)
  - Service call statistics (Read/Write/Browse/HistoryRead call rates and average latency)
```

```
Gateway Config → Status → Logs
  Look for logger: com.inductiveautomation.opcua
  Filter: WARN/ERROR level for session drops, certificate rejections, subscription overflow
```

### Key Metrics to Trend

| Metric | Healthy pattern | Warning sign |
|---|---|---|
| Active session count | Stable, matches known integration count | Steadily climbing (leaked sessions) |
| Subscription publish latency | Consistent with configured publishing interval | Growing lag between configured and actual publish timing |
| Monitored item queue overflow events | Zero/rare | Frequent — sampling faster than publishing can drain, increase queue size or publishing rate |
| Rejected certificate count | Zero after initial commissioning | New rejections appearing — unexpected/unauthorized connection attempts |
| CPU/heap during peak subscription load | Within normal Gateway baseline | Sustained spike correlated with OPC-UA activity — revisit subscription sharding and deadband settings |

### Client-Side Diagnostics

For third-party OPC-UA clients, a general-purpose tool like **UaExpert** is invaluable for isolating whether an issue is server-side (reproducible from a known-good independent client) or specific to the production client's implementation — connect UaExpert to the same endpoint with the same security policy and credentials to establish a baseline before debugging the production client's code.

## Related Documents

- `88-OPC-UA-SERVER-CONFIGURATION.md` — server setup, namespace, security policies, endpoint/user mapping, base subscription tuning
- `24-OPC-UA-DEVICES.md` — Ignition as OPC-UA client, device driver basics
- `82-DEBUGGING-GUIDE.md` — general Gateway log/diagnostic methodology
- `83-PERFORMANCE-TUNING.md` — general performance tuning patterns applicable beyond OPC-UA
- `50-SECURITY-MODEL.md` / `51-PLATFORM-SECURITY-COMPLETE.md` — Security Zones and User Source configuration referenced throughout

---

## See Also

**Prerequisites:** [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md)

**Builds toward:** [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)

**Related:** [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
