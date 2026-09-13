---
title: OPC-UA Server Configuration
description: Running Ignition as an OPC-UA server, namespace design, method exposure, security policies, endpoint management, user mapping, subscription tuning
---

> **Skill level:** 300 · **Read first:** [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [24b-PLATFORM-DEVICES](24b-PLATFORM-DEVICES.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 88-OPC-UA-SERVER-CONFIGURATION

# OPC-UA Server Configuration

Ignition ships with a built-in OPC-UA server module. Every Ignition Gateway can act as both an OPC-UA **client** (pulling data from PLCs/devices) and an OPC-UA **server** (exposing its own tags, methods, and object hierarchy to external OPC-UA clients — other Gateways, SCADA systems, MES/ERP integrations, or third-party historians). This document covers running Ignition as a server: what gets exposed, how the namespace is structured, security configuration, and performance tuning for outbound subscriptions.

## Why Run Ignition as an OPC-UA Server

Common scenarios:

- **Gateway Network Federation** — a central Ignition Gateway consumes tags from edge Gateways over OPC-UA instead of (or alongside) Gateway Network Remote Tag Providers.
- **Third-party SCADA/HMI integration** — legacy Wonderware, FactoryTalk, or WinCC systems browse Ignition tags as an OPC-UA source.
- **MES/ERP bridging** — an MES historian or middleware polls Ignition-calculated values (aggregates, KPIs, UDT-derived tags) via standard OPC-UA rather than a custom API.
- **Multi-vendor interoperability** — exposing Ignition's own scripted/calculated values to non-Ignition consumers without building a REST layer.

The OPC-UA server is enabled by default on every Gateway (the module is `com.inductiveautomation.opcua`). It listens on **port 4096** (TCP, `opc.tcp://`) unless reconfigured.

## What Gets Exposed

By default, the Ignition OPC-UA server exposes:

- **All tags** in all configured Tag Providers (memory tags, OPC tags re-exposed, expression tags, UDT instances) — organized under the `Tag Providers` folder in the address space.
- **Scripted OPC-UA methods**, if explicitly registered (see Method Exposure below).
- **UDT structure** as a browsable object hierarchy mirroring the UDT definition tree.

Tag visibility can be restricted per-provider:

```
Gateway Config → Tags → Tag Providers → [provider] → Edit
  "Enable OPC-UA Server exposure": true/false
```

Disable exposure for providers containing sensitive or purely-internal calculation tags that should never be visible to external OPC-UA clients — this is the primary access-control lever before you get into per-endpoint security policies.

### Data Types, Quality, and Timestamps

Every Ignition tag exposed via OPC-UA carries its native data type mapped to the closest OPC-UA built-in type:

| Ignition Tag Type | OPC-UA Data Type |
|---|---|
| Integer/Long | Int32 / Int64 |
| Float/Double | Float / Double |
| Boolean | Boolean |
| String | String |
| DateTime | DateTime |
| Document/Dataset | ByteString (serialized) or custom structure, depending on client support |

Beyond the raw value, every read returns a **DataValue** triple — Value, StatusCode (quality), and SourceTimestamp/ServerTimestamp — mirroring Ignition's own internal `Good`/`Bad`/`Uncertain` quality model. A tag whose underlying OPC device connection is down reports `Bad` quality through to the external OPC-UA client exactly as it would inside Ignition's own tag browser; there is no silent masking of upstream quality issues when re-exposing tags. Downstream client integrations should always branch on StatusCode, not just check for a non-null value, for the same reason Ignition scripting checks `result.quality.name` before trusting `result.value` (see `24-OPC-UA-DEVICES.md`).

### Perspective and Vision Data Considerations

The OPC-UA server exposes **Gateway-scoped tag data**, not session-scoped UI state — Perspective session props, view params, and client-local Vision window state are never visible over OPC-UA because they don't exist as tags. What *is* commonly exposed and consumed this way:

- **Memory tags written from Perspective/Vision scripts** (e.g., an operator-entered setpoint written via `system.tag.write` from a component event) — these behave like any other tag once written, immediately visible to OPC-UA clients subscribed to that path.
- **Expression tags computing UI-adjacent aggregates** (shift totals, OEE rollups) that a dashboard elsewhere (Perspective, third-party HMI, or a non-Ignition BI tool) consumes via OPC-UA rather than a database round-trip.
- **UDT instance data bound into Perspective views** — since the UDT's OPC-UA ObjectType exposure (see Reference Types below) mirrors the same UDT definition driving the Perspective binding, a change visible in the Designer's tag browser is exposed identically to external OPC-UA clients with no separate configuration step.

**Practical implication:** if a value needs to reach an external OPC-UA client, get it into a tag (memory, expression, or UDT member) — there is no path from Perspective component state directly to the OPC-UA address space that bypasses the tag system.

## Namespace Configuration

### Namespace URIs (URNs)

Every OPC-UA server publishes one or more **Namespace URIs** — strings that uniquely identify the origin of a NodeId so that clients from different vendors don't collide on numeric namespace indexes. Ignition auto-assigns namespace indexes at runtime; **never hardcode a namespace index in a client** — always resolve via the namespace URI array first, then use the resolved index.

Ignition's default namespace URI pattern:

```
urn:{gateway-hostname}:{gateway-name}/tag-provider/{provider-name}
```

Example: a Gateway named `PlantA-Gateway` with a default tag provider produces:

```
urn:plantA-gw.plant.local:PlantA-Gateway/tag-provider/default
```

Each additional tag provider gets its own namespace URI, meaning a single Ignition server may publish namespace indexes 0 (OPC-UA standard), 1 (server-specific), 2 (`default` provider), 3 (`EdgeHistorian` provider), etc. Namespace index assignment is **not stable across restarts if providers are added/removed** — always resolve indexes dynamically via `Server/NamespaceArray`.

### Node ID Structure

Ignition assigns Node IDs using the **string identifier** type (not numeric), formatted as the full tag path:

```
ns=2;s=[default]Line1/Station3/Temperature
```

Breaking this down:
- `ns=2` — namespace index (resolved dynamically, see above)
- `s=` — string identifier type
- `[default]Line1/Station3/Temperature` — full Ignition tag path including provider

UDT member tags follow the same pattern with the instance path fully expanded:

```
ns=2;s=[default]Motors/Motor_001/RunHours
```

### Address Space Structure

The exposed address space mirrors Ignition's tag folder hierarchy:

```
Root
└── Objects
    └── Tag Providers
        └── default
            └── Line1
                └── Station3
                    ├── Temperature (Variable)
                    ├── Pressure (Variable)
                    └── Motor_001 (Object, UDT instance)
                        ├── RunHours (Variable)
                        ├── Start (Method, if exposed)
                        └── Stop (Method, if exposed)
```

UDT **definitions** are exposed as **ObjectTypes** under `Types/ObjectTypes/BaseObjectType`, allowing OPC-UA clients that understand type hierarchies (e.g., UaExpert, other Ignition Gateways) to browse instances by type rather than only by folder path.

## Method Exposure (Scripting → OPC-UA Methods)

Ignition can expose Python/Jython gateway scripts as callable OPC-UA **Methods** attached to a UDT instance or folder node. This lets external OPC-UA clients invoke server-side logic (e.g., "Start Motor", "Reset Alarm", "Run Recipe") rather than just reading/writing variables.

### Configuring an Exposed Method

Method exposure is configured per-UDT via the **UDT Definition → Methods** section (Ignition 8.1+ carries forward into 8.3 with expanded typing support):

```
UDT Definition: MotorType
└── Methods
    └── Start
        Input Arguments:
          - targetSpeed (Float, optional)
        Output Arguments:
          - success (Boolean)
        Script:
          def execute(self, targetSpeed=0.0):
              if self.getValue("Interlocked"):
                  return False
              system.tag.write(f"{self.path}/RunCommand", 1)
              if targetSpeed > 0:
                  system.tag.write(f"{self.path}/SpeedSetpoint", targetSpeed)
              return True
```

Once defined, every UDT instance based on `MotorType` exposes a `Start` method at:

```
ns=2;s=[default]Motors/Motor_001.Start
```

### Security Considerations for Exposed Methods

- Methods execute with **Gateway-level script privileges**, not the calling client's OPC-UA identity — treat every exposed method as a potential privileged remote-execution vector.
- Always validate input arguments inside the method body; OPC-UA type-checking only guarantees the argument's *data type*, not its *range* or *business validity*.
- Pair method exposure with a restrictive endpoint (Sign & Encrypt, non-anonymous identity) — never expose write-capable methods on an anonymous/None-security endpoint.
- Log every method invocation (`logger.info(f"OPC-UA method Start invoked by {system.opcua.getClientCertificateSubject()}")` pattern, where available) for audit trails on safety-adjacent actions.

## Reference Types & Object Hierarchies

OPC-UA models relationships between nodes using typed **References**. Ignition uses the standard OPC-UA reference type set plus a few Ignition-specific extensions for UDTs:

| Reference Type | Direction | Use in Ignition |
|---|---|---|
| `Organizes` | Folder → child | Tag folder containment |
| `HasComponent` | Object → Variable/Method | UDT instance → member tag/method |
| `HasTypeDefinition` | Instance → Type | UDT instance → UDT ObjectType |
| `HasProperty` | Node → Property | Tag metadata (engineering units, documentation) exposed as Properties |
| `HasSubtype` | Type → Type | UDT inheritance (parent UDT → child UDT) |

UDT inheritance in Ignition maps directly to OPC-UA `HasSubtype` chains: a `PumpType` UDT that extends `MotorType` produces an ObjectType hierarchy `BaseObjectType → MotorType → PumpType`, and OPC-UA clients that support type-based browsing (Type Definition browsing) can query "give me all instances of MotorType or any subtype" and receive both motors and pumps.

**Practical implication:** design UDT inheritance hierarchies deliberately if you plan to expose them via OPC-UA to type-aware clients (other Ignition Gateways, UaExpert, some MES platforms) — flat/duplicated UDTs with no inheritance lose this browsing capability.

## Security Policies

Ignition's OPC-UA server supports the four standard security policy tiers, configured per-endpoint:

| Policy | Encryption | Signing | Use Case |
|---|---|---|---|
| **None** | No | No | Local-only, trusted network segment, testing. **Never use over untrusted networks.** |
| **Basic128Rsa15** | Yes (128-bit) | Yes | Legacy compatibility only — deprecated by the OPC Foundation, has known cryptographic weaknesses. Avoid for new deployments. |
| **Basic256Sha256** | Yes (256-bit) | Yes | Standard secure OPC-UA client/server traffic. Default recommendation for Gateway-to-Gateway and third-party client connections. |
| **Basic256Sha256PubSub** | Yes (256-bit) | Yes | Used specifically for OPC-UA PubSub (UDP/MQTT transport) message signing/encryption — not applicable to classic client/server sessions. See 89-OPC-UA-ADVANCED-PATTERNS.md for PubSub details. |

### Configuring Security Policies

```
Gateway Config → OPC-UA → Server → Settings → Security
  Endpoints:
    - opc.tcp://gateway:4096  | Security: None          | MessageMode: None
    - opc.tcp://gateway:4096  | Security: Basic256Sha256 | MessageMode: Sign
    - opc.tcp://gateway:4096  | Security: Basic256Sha256 | MessageMode: SignAndEncrypt
```

**Recommended production posture:**
- Disable the `None` security policy endpoint entirely once initial commissioning is complete.
- Standardize on `Basic256Sha256` with `SignAndEncrypt` message mode.
- Reject `Basic128Rsa15` unless a specific legacy client mandates it — document the exception and plan its retirement.

### Message Security Modes

- **None** — no signing, no encryption (paired only with security policy None).
- **Sign** — messages are signed (tamper-evident) but sent in cleartext. Detects tampering, does not prevent eavesdropping.
- **SignAndEncrypt** — full confidentiality and integrity. Required for any traffic crossing untrusted network segments (corporate WAN, cloud links, cross-site Gateway Networks over public internet).

## Endpoint Management

An OPC-UA server can publish **multiple endpoints** simultaneously — different combinations of transport, security policy, and message mode — allowing heterogeneous clients to connect at their own supported security level.

```
Gateway Config → OPC-UA → Server → Settings → Endpoints
  Discovery URL: opc.tcp://gateway-hostname:4096/discovery
  Endpoints:
    1. opc.tcp://gateway-hostname:4096  None / None
    2. opc.tcp://gateway-hostname:4096  Basic256Sha256 / Sign
    3. opc.tcp://gateway-hostname:4096  Basic256Sha256 / SignAndEncrypt
```

**Hostname vs. IP binding:** always publish endpoints using a resolvable hostname (matching the server certificate's Subject Alternative Name), not a bare IP. Clients validating the server certificate against the connection URL will reject mismatches — a common source of "certificate untrusted" errors on otherwise-correctly-configured servers. If the Gateway is multi-homed (multiple NICs), configure `gateway.network.publicAddress` in `gateway_network.xml` or the equivalent Gateway Network settings so the correct externally-resolvable hostname is advertised.

**Firewall note:** port 4096 (server) must be reachable from every intended client. If Ignition is also configured with the redundant/Gateway Network features, additional ports (8060 for HTTP, 8043 for HTTPS gateway web interface, 8088 Gateway Network) are separate concerns from OPC-UA proper.

## User Mapping to OPC-UA Identities

OPC-UA supports three identity token types at the session layer: **Anonymous**, **Username/Password**, and **X.509 Certificate**. Ignition maps incoming session identities to internal permission checks:

```
Gateway Config → OPC-UA → Server → Settings → Security
  Allow Anonymous Access: false   (recommended for production)
  Enabled Identity Providers:
    - Username/Password → mapped to configured Ignition User Source
    - Certificate → mapped via Certificate Manager trusted list
```

### Username/Password Mapping

When a client authenticates with Username/Password, Ignition validates against the **User Source** configured for OPC-UA authentication (can be the same or a dedicated User Source separate from Perspective/Vision session auth). Tag-level **Security Zones** and **OPC Tag security** still apply on top of session authentication — a successfully authenticated OPC-UA user can be further restricted from reading/writing specific tag subtrees via the same security zone mechanism used elsewhere in the platform.

```
Gateway Config → Security → Security Levels / Zones
  Zone: "OPC-External-ReadOnly"
    Assigned to: OPC-UA session role "ExternalClients"
    Tag permission: Read only, on [default]Line1/* and below
```

### Certificate-Based Identity

For machine-to-machine integrations (Gateway Network federation, automated MES polling), certificate-based identity avoids embedding credentials in client configuration:

1. Client presents its X.509 certificate during session activation.
2. Ignition checks the certificate against the **OPC-UA Client Certificate** trust list (Gateway Config → OPC-UA → Security → Certificates).
3. If trusted, the session is mapped to a configured role via the certificate's Subject/Thumbprint.

**Rotate and audit trusted certificates on a fixed schedule** — stale trusted certs from decommissioned integrations are a common lingering attack surface.

### Role Mapping and Least Privilege

Whichever identity model is used, map incoming OPC-UA sessions to the **narrowest role that satisfies the integration's actual need**:

```
Role: "OPC-ReadOnly-Reporting"    → Read-only, [default]Reporting/* subtree only
Role: "OPC-ReadWrite-MES"         → Read/write, [default]Production/* subtree, no Methods
Role: "OPC-Admin-Federation"      → Full read/write + Methods, restricted to Gateway Network peer certificates only
```

Avoid a single catch-all "OPC-UA Users" role granted broad read/write across the entire tag space — it collapses the audit trail (every external write looks identical regardless of source system) and turns one compromised integration credential into full write access across every exposed tag.

## Performance Tuning (Subscriptions, Sampling Intervals)

External OPC-UA clients subscribe to Ignition tag data using standard OPC-UA **Subscriptions**, each containing one or more **Monitored Items**. Server-side tuning affects how many subscriptions the Gateway can sustain and how promptly changes propagate.

### Key Parameters

| Parameter | Location | Effect |
|---|---|---|
| Publishing Interval | Client-requested, server-clamped | How often the server evaluates the subscription for changed values to publish |
| Sampling Interval | Per-monitored-item | How often the underlying tag value is checked for change (independent of publish rate) |
| Queue Size | Per-monitored-item | How many buffered value changes are retained between publishes before overwrite |
| Max Subscriptions per Session | Server setting | Caps per-client subscription count |
| Max Monitored Items per Subscription | Server setting | Caps items per subscription |

### Server-Side Tuning

```
Gateway Config → OPC-UA → Server → Settings → Performance
  Minimum Publishing Interval: 100ms   (floor — clients cannot request faster)
  Minimum Sampling Interval: 100ms
  Max Sessions: 100
  Max Subscriptions per Session: 20
  Max Monitored Items per Subscription: 5000
```

**Guidance:**
- Set `Minimum Publishing Interval` no lower than your actual scan-rate needs — every client requesting sub-100ms publishing on thousands of items multiplies server CPU/memory load linearly.
- For high tag-count exposures (>10,000 tags visible to a single external client), coach the client integrator toward **fewer, larger subscriptions** rather than many small ones — subscription bookkeeping overhead scales with subscription count, not just item count.
- Sampling interval should generally match (or exceed) the underlying tag's actual update rate from its device source — sampling an OPC device tag at 50ms when the PLC scan cycle only updates it every 250ms wastes server cycles producing duplicate "changed" evaluations.
- Monitor `Gateway Config → Status → OPC-UA → Server → Sessions` for session count and subscription count trending upward without a corresponding increase in known client integrations — a sign of leaked/unclosed client sessions that should be investigated.

### Common Symptom: Server-Side Subscription Overload

**Symptom:** Gateway CPU climbs steadily with no tag-count growth; `wrapper.log` shows GC pressure; OPC-UA client connections time out intermittently.

**Diagnosis:**
```
Gateway Config → Status → OPC-UA → Server
  Check: total active subscriptions, total monitored items, publish rate distribution
```

**Fix:** raise `Minimum Publishing Interval`/`Minimum Sampling Interval` floors, cap `Max Monitored Items per Subscription`, and audit connected clients for redundant/duplicate subscriptions to the same tag set (common when a client library reconnects without cleanly closing the prior session).

## Worked Example: Connecting a Third-Party Client

A minimal end-to-end walkthrough for validating a new server configuration using a generic OPC-UA test client (e.g., UaExpert):

1. **Confirm the server is running:** `Gateway Config → OPC-UA → Server → Settings` shows status "Running" and lists the active endpoints.
2. **Discover endpoints:** point the test client at `opc.tcp://gateway-hostname:4096` and request Endpoint Discovery — confirm the expected security policy/message-mode combinations appear (see Endpoint Management above).
3. **Establish a secure session:** select `Basic256Sha256` / `SignAndEncrypt`, supply Username/Password or Certificate identity per the User Mapping configuration, and accept the server certificate on first connect (it will appear in the client's own trust store prompt).
4. **Check the Gateway's Rejected Certificates list:** on the client's first connection attempt, the client's own certificate (if using certificate auth) lands in `Gateway Config → OPC-UA → Security → Certificates → Rejected` — promote it to Trusted and reconnect.
5. **Browse the address space:** navigate `Objects → Tag Providers → default → ...` and confirm the expected tag folders and UDT instances appear with correct data types.
6. **Subscribe to a test tag:** add a known-good tag to a new subscription at a 1000ms publishing interval and confirm live value updates with `Good` quality.
7. **Validate write access (if applicable):** attempt a write to a tag the test identity is permitted to modify, and confirm a write to a restricted tag is correctly rejected (`BadUserAccessDenied`) — this validates the Security Zone configuration is actually being enforced, not just present in configuration.

This sequence isolates each configuration layer (network reachability, endpoint/security policy, certificate trust, session identity, tag exposure, subscription behavior, write permissions) so a failure at any step points directly at the layer to fix, rather than requiring a full re-audit of the entire server configuration.

## OPC-UA Server Exposure vs. Gateway Network Remote Tag Providers

Ignition offers two distinct mechanisms for one Gateway to consume another Gateway's tags: the built-in **Gateway Network Remote Tag Provider** and standard **OPC-UA client/server**. They are not interchangeable, and choosing wrong leads to unnecessary complexity or missed capability.

| Aspect | Gateway Network Remote Tag Provider | OPC-UA Client/Server |
|---|---|---|
| Protocol | Ignition-proprietary (Gateway Network, port 8060/8043) | Standard OPC-UA (`opc.tcp://`, port 4096) |
| Peer requirement | Both ends must be Ignition | Either end can be any OPC-UA-compliant product |
| Setup complexity | Lower — built-in Gateway Network trust/certificate handling | Higher — explicit endpoint/security/certificate configuration |
| Tag write-through | Full read/write, near-native feel | Read/write per exposed permissions, standard OPC-UA semantics |
| UDT definition sync | Full UDT definitions propagate automatically | Only ObjectType hierarchy visible, not full editable UDT definitions |
| External (non-Ignition) consumers | Not applicable | Primary use case |

**Guidance:** default to Gateway Network Remote Tag Providers for Ignition-to-Ignition tag sharing within a trusted enterprise — it's simpler to configure and keeps UDT definitions in sync automatically. Reach for OPC-UA client/server specifically when a non-Ignition system needs to participate, or when the interoperability of an open standard (auditability, vendor-neutral tooling, contractual requirement for OPC-UA compliance) matters more than setup convenience.

## Additional Method Exposure Example: Parameterized Recipe Execution

A second worked example illustrating a more complex exposed method — running a named recipe against a UDT-based process cell, with input validation and structured error reporting:

```python
UDT Definition: ProcessCellType
└── Methods
    └── RunRecipe
        Input Arguments:
          - recipeName (String)
          - batchSize (Float)
        Output Arguments:
          - accepted (Boolean)
          - message (String)
        Script:
          def execute(self, recipeName="", batchSize=0.0):
              valid_recipes = system.tag.read(f"{self.path}/ValidRecipeList").value
              if recipeName not in valid_recipes:
                  return (False, f"Unknown recipe: {recipeName}")
              max_batch = system.tag.read(f"{self.path}/MaxBatchSize").value
              if batchSize <= 0 or batchSize > max_batch:
                  return (False, f"batchSize out of range (0, {max_batch}]")
              if system.tag.read(f"{self.path}/CellBusy").value:
                  return (False, "Cell currently busy, reject")
              system.tag.write(f"{self.path}/ActiveRecipe", recipeName)
              system.tag.write(f"{self.path}/TargetBatchSize", batchSize)
              system.tag.write(f"{self.path}/StartCommand", 1)
              logger = system.util.getLogger("OPC-UA-Methods")
              logger.info(f"RunRecipe '{recipeName}' batch={batchSize} accepted on {self.path}")
              return (True, "Recipe accepted")
```

This pattern demonstrates the recommended shape for any exposed method with real-world consequences: validate every input against current tag state before acting, fail closed (reject rather than clamp/guess on invalid input), write intent to tags rather than triggering side effects directly from the method body where possible (keeps the audit trail in the historian alongside every other tag change), and log the invocation with enough context to reconstruct who requested what.

## Related Documents

- `24-OPC-UA-DEVICES.md` — Ignition as an OPC-UA client, device driver configuration
- `89-OPC-UA-ADVANCED-PATTERNS.md` — certificates, redundancy, aggregation, PubSub, troubleshooting
- `50-SECURITY-MODEL.md` / `51-PLATFORM-SECURITY-COMPLETE.md` — Security Zones, User Sources referenced above
- `83-PERFORMANCE-TUNING.md` — general Gateway performance methodology

---

## See Also

**Prerequisites:** [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [24b-PLATFORM-DEVICES](24b-PLATFORM-DEVICES.md)

**Builds toward:** [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md)

**Related:** [89-OPC-UA-ADVANCED-PATTERNS](89-OPC-UA-ADVANCED-PATTERNS.md), [24-OPC-UA-DEVICES](24-OPC-UA-DEVICES.md), [24b-PLATFORM-DEVICES](24b-PLATFORM-DEVICES.md), [51-PLATFORM-SECURITY-COMPLETE](51-PLATFORM-SECURITY-COMPLETE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
