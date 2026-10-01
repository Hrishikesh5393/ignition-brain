# Ignition 8.3 — OPC UA, connectivity and the module catalog

Source: live docs at `docs.inductiveautomation.com/docs/8.3/` — module overview, OPC UA, device drivers, Event Streams, Cloud Connectors, Web Dev, JDBC Drivers pages (72 pages read in full).

---

## Module catalog

Ignition ships as a modular platform. Every module below is either a **core module** (typical install), an **additional module** (specialty use case), a **cloud connector** (bundled with Cloud Edition, usable standalone), or a **JDBC driver module** (bundled database drivers). Enabling/disabling a module only takes effect after a Gateway restart (a banner prompts you).

### Core modules

| Module | What it does | Depends on / notes |
|---|---|---|
| **Perspective** | Mobile-responsive HTML5/CSS3 web app builder; runs in browser or native iOS/Android app; offline mode; CSS theming. | None. |
| **Vision** | Java-client-based HMI/SCADA visualization; unlimited clients; drag-and-drop Designer, vector drawing, Symbol Factory library, templates. | None. Limited version available for small client counts. |
| **SQL Bridge** | Bidirectional OPC↔SQL data bridge via Transaction Groups: data logging, PLC↔DB synchronization, recipe/batching systems, process sequencing. | None. SQL Bridge Limited = historical-groups-only, cheaper. Required by the Event Streams **Database handler**. |
| **Historian Core** (Tag Historian) | Records tag history to embedded or external time-series storage; automatic table management, compression/interpolation/partitioning/aggregation; pluggable storage backends (Core Historian, Internal Historian (Legacy)). | None. |
| **SQL Historian** | Adds a SQL-database-backed historian option on top of Historian Core. | Requires **Historian Core** module. |
| **Reporting** | Drag-and-drop PDF/HTML/CSV/RTF report designer; scheduled or triggered execution; pulls from SQL, Tag Historian, alarm journal. | None. Limited version for a handful of reports. |
| **OPC UA** | Turns Ignition into a full OPC UA server (any driver) **and** OPC UA client; public driver API for custom drivers; redundancy-aware. | An OPC UA **client** ships built into Ignition even without this module (for connecting outbound to 3rd-party UA servers); the **server** and the bundled **device drivers** require this module. |
| **Alarm Notification** | Alarm pipelines (delay/escalation/consolidation/selection), on-call rosters, 2-way email ack. | Required by SMS, Voice, and Twilio notification modules. |
| **Event Streams** *(new in 8.3)* | Unified event-driven pipeline: Source → Filter → Transform → Buffer → Handler(s) → Error Handler. | Kafka source/handler needs **Kafka Connector**; HTTP source needs **Web Dev**; Database handler needs **SQL Bridge**. |
| **SMS Notification** | Text-message alarm notification/acknowledgement. | Requires **Alarm Notification** + a cellular modem. |
| **Sequential Function Charts (SFC)** | IEC 61131-3 visual logic programming (steps, transitions, parallel branches, jumps); long-running/redundant-safe charts. | None. |
| **Web Dev** | Hosts custom webpages/REST APIs from the Gateway using Python resources, static file/text resources, and mounted folders. | None by itself; required by Event Streams' **HTTP source** and **HTTP handler**. |
| **Enterprise Administration (EAM)** | Central Controller Gateway manages many Agent Gateways: license mgmt, module deployment, disaster recovery, remote backups, project/resource sync, health monitoring. | None. |
| **JDBC Drivers** | Bundles MariaDB (3.3.3, also covers MySQL), MSSQL (9.4.0.jre11), PostgreSQL (42.7.2) JDBC drivers as modules (auto-added to Database Settings). | None; SQLite ships as a built-in driver (no module). |

### Additional modules

| Module | What it does | Depends on |
|---|---|---|
| **Voice Notification** | Text-to-speech phone-call alarm delivery over SIP; two-way ack via response code; multi-language. | Requires **Alarm Notification** + a SIP-compatible VoIP service/gateway. |
| **OPC COM** | Bridges Ignition to legacy COM-based OPC-DA 2.0/3.0 servers (Windows only). | OPC Core Components (from OPC Foundation) installed on host. |
| **OPC COM Tunneller** | Exposes OPC-COM-connected DA servers through Ignition's OPC UA server — lets remote UA clients reach a DA server without Remote DCOM. | Requires **OPC COM** module. |
| **Twilio Notification** | SMS/Voice/WhatsApp alarm notification via Twilio; adds `system.twilio` scripting functions. | Requires **Alarm Notification**. |
| **SECS/GEM** | Host-side SECS-II/GEM/HSMS communication with semiconductor fab equipment; equipment simulators for testing. | None (own connection framework under **Connections**). |

### Cloud Connector modules

| Module | What it does | Depends on / notes |
|---|---|---|
| **Kafka Connector** | Gateway connections to Kafka clusters; produce/consume via `system.kafka` functions or as an Event Streams source/handler. | Bundled with Cloud Edition; available as an add-on for standard Ignition; **not available on Edge**. |
| **MongoDB Connector** | Gateway connections to MongoDB (incl. Atlas); `system.mongodb` functions; read-only MongoDB Perspective binding (Find/FindOne/Aggregate). | Bundled with Cloud Edition; available as an add-on; **not available on Edge or Maker Edition**. |

### "Which module do I need for X?" quick answers

- **Connect to a PLC** → OPC UA module + the matching driver module (Allen-Bradley, Siemens, Modbus, etc. — see Device Drivers below).
- **Poll a Kafka topic or publish to one from a tag change** → Kafka Connector + Event Streams.
- **Expose a REST endpoint that other systems POST to, and turn that into a tag write** → Web Dev (HTTP source) + Event Streams (Tag handler).
- **Bridge PLC data into a SQL table on a schedule/trigger** → SQL Bridge (Transaction Groups) — or Event Streams with a Database handler for event-driven inserts.
- **Talk to legacy Windows OPC-DA server** → OPC COM (local) or OPC COM Tunneller (remote, avoids DCOM).
- **Central management of many Gateways** → Enterprise Administration.
- **Custom host web page or webhook receiver hosted by the Gateway itself** → Web Dev.
- **Non-relational document storage / NoSQL** → MongoDB Connector.

---

## OPC UA

OPC UA (Unified Architecture) is Ignition's primary, platform/vendor-neutral data access standard, built on TCP/IP with encryption; supersedes the old DCOM-based OPC-DA/A&E/HDA specs. Ignition ships a built-in OPC UA **client** even without the OPC UA module (for reaching 3rd-party servers); the OPC UA **module** adds the **server** role plus the bundled device drivers.

### Ignition as OPC UA client vs. server

- **As client**: connects to third-party device servers (Kepware, Unified Automation demo, etc.), other Ignition Gateways' UA servers, or protocol-translation gateways. Browse the address space in the Designer and create OPC tags that subscribe to live data.
- **As server** (requires OPC UA module): exposes data from connected devices (drivers), memory/expression/historical tags to external UA clients (SCADA systems, other Gateways, UaExpert, etc.).
- Ignition supports **UA/TCP transport with UA/Binary encoding** for performance (not the XML/web-services variants in the spec) and all common encryption schemes.
- **Distributed architecture pattern**: lightweight remote Gateway with just the OPC UA module collects local device data and forwards to a central Gateway over OPC UA/VPN for storage and visualization.

### Ignition's OPC UA Server settings (**Connections > OPC > OPC UA Server Settings**)

Default credentials for authenticated access: **username `opcuauser`**, **password `password`** (auto-created on new installs so the Gateway can connect to its own server). Anonymous access is off by default. Discovery endpoint (server intentionally hard to discover otherwise): `opc.tcp://<host>/discovery`.

| Setting group | Key settings | Default |
|---|---|---|
| Endpoint Configuration | Bind Port | 62541 |
| | Bind Addresses (use `0.0.0.0` to expose externally) | `localhost` |
| | Endpoint Addresses (comma list; `<addr>` form tries to resolve to more hostnames/IPs) | `<hostname>,<localhost>` |
| | Security Policies (comma list: `None`, `Basic256Sha256`, `Aes128_Sha256_RsaOaep`, `Aes256_Sha256_RsaPss`) | `Basic256Sha256` |
| Authentication | Anonymous Access Allowed | false |
| | User Source | `opcua-module` |
| Advanced | Expose Tag Providers (lets 3rd-party UA clients read Ignition tag providers) | false |
| | Max Session Count | 100 |
| | GDS Push Enabled | false |
| Redundancy | Read-only When Inactive Node | false |

**Permissions tab**: per-role Browse/Read/Write/Call grants, settable as Default Device Permissions, Default Tag Provider Permissions, and per-Tag-Provider overrides.

**Redundancy diagnostics**: read the `ServiceLevel` node under **Server** via the OPC Quick Client — `255` = active master, `254` = active backup, `1` = inactive.

### OPC UA Connections (Ignition as client) — `Connections > OPC > Connections`

**Connect wizard**, step by step:

1. **OPC > Connections** → **Create OPC Connection +**.
2. Select **OPC UA Connection**, click **Next** (Server Discovery page appears).
3. Enter the endpoint URL: `opc.tcp://IpAddress:Port` or `opc.tcp://hostname:port`.
4. Click **Next** → choose a discovered server → **Next** → choose an endpoint (security policy/mode list is server-supplied) → **Next**.
5. Review the settings summary → **Next**.
6. Trust the server's certificate in the Manage Certificate popup (skipped automatically if already trusted) → **Next**.
7. Optionally supply a fallback discovery URL if the primary host is unreachable.
8. Select **Security Policy** and **Message Security** → **Finish**.
9. On **Configure Connection**, name the connection and supply any Authentication credentials the target server requires → **Create OPC Connection**.

Use **"Skip to Advanced Configuration"** (bottom-right of the popup) to hand-enter settings when a server doesn't allow anonymous endpoint discovery but exposes a separate discovery endpoint.

**Authentication Type**: `Username` (default, +Username/Password), `Anonymous`, or `Certificate` (X.509 PEM cert + PKCS1/PKCS8 private key, Embedded or Referenced).

**Keep Alive**:

| Property | Default |
|---|---|
| Keep-Alive Failures Allowed (0 or negative = never disconnect) | 1 |
| Keep-Alive Interval | 15,000 ms |
| Keep-Alive Timeout | 10,000 ms |

**Advanced**:

| Property | Default | Notes |
|---|---|---|
| Host Override | — | Use when the endpoint's returned IP/hostname differs from the discovered one. |
| Connect Timeout | 5,000 ms | Socket-open timeout. |
| Acknowledge Timeout | 5,000 ms | Wait for Acknowledge after client Hello. |
| Request Timeout | 60,000 ms | |
| Session Timeout | 120,000 ms | Requested session timeout. |
| Max Per Operation | 8,192 | Max nodes per read/write/subscribe/unsubscribe request. |
| Max References Per Node | 8,192 | Lower for flat address spaces to avoid oversized messages. |
| Max Pending Publish Requests | 2 | |
| Max Notifications Per Publish | 65,535 | |
| Max Message Size | 33,554,432 | |
| Max Array Length / Max String Length | 2,147,483,647 each | |
| Deprecated Data Type Dictionary Support | off | Use legacy DataType Dictionary instead of DataTypeDefinition attribute. |
| Browse Origin | `OBJECTS_FOLDER` | Or `ROOT_FOLDER` for non-standard servers (Ignition's own server uses `OBJECTS_FOLDER`). |
| Timestamp Source | `IGNITION` | Or `OPC_PREFER_SERVER` / `OPC_PREFER_SOURCE`. |

**Failover** — for a client connecting to a *pair* of redundant 3rd-party UA servers (distinct from Ignition's own redundant-Gateway "Backup" properties used with Kepware, see Third-Party OPC Servers below): Failover Enabled, Failover Threshold (3 retries default), Failover Discovery URL (`opc.tcp://hostname:port`), Failover Endpoint URL, Failover Host Override. Failover is **"sticky"** — once switched to the backup it stays there until the backup itself fails.

**Security**: Certificate Validation Enabled (default true — disabling it is a security compromise), Keystore Alias, Password (None/Embedded/Referenced).

**Diagnostics** (Connection Details panel, via 3-dot menu → View Details): **Server Diagnostics** tab (disabled by default — network overhead; requires `ConfigureAdmin` or `SecurityAdmin` role as of the Milo 1.1.6 upgrade shipped in 8.3.9+; upgrades from ≤8.3.8 must add the role manually) and **Client Diagnostics** tab (per-subscription Name/Rate/Requested & Revised Publishing Interval/Tag Count, expandable to per-node Requested/Revised Sampling Interval, Requested/Revised Queue Size, Status Code).

### OPC UA Security (`Connections > OPC > Security Settings`)

Separate **Client** and **Server** tabs, each with: upload/download/delete Trusted Certificates (Common Name, SHA-1 Fingerprint, Expiration), a Quarantined Certificates list (imported-but-untrusted — Trust or Delete), and a **Certificates** tab that can **Regenerate** the Gateway's own cert (default 3-year lifespan; regenerating invalidates the old private key immediately and is auto-trusted).

### Discovery, browsing, and the OPC Quick Client

- **OPC Quick Client** (`Connections > OPC > Quick Client`) — tree browse of the Ignition OPC UA server (all connected devices + tag providers) for ad-hoc testing; does **not** create or persist tags. Node action indicators: **[R]** read, **[W]** write, **[S]** subscribe (adds to Monitored Items table with live value/quality/timestamp; **Set Rate** adjusts poll ms; **Clear Monitored Items** removes all).
- **Getting PLC data into tags**: Tag Browser → Add → **Browse Devices** → navigate OPC Browser → stage tags → OK. Devices that don't support browsing (Modbus, Siemens absolute addressing) require manually created tags with a hand-built **OPC Item Path**.

### Subscriptions, sampling, and diagnostic tags

Every driver connection gets built-in diagnostic tags for health monitoring:

**Root diagnostics**: `Connected` (bool; replaces legacy `isConnected`), `Hostname`, `Name`, `Port`, `State` (string, e.g. "Connected"), `Status` (more granular), and for DNP3 drivers an `Internal Indicator (IIN)` folder.

**Sampling folder** — an `Aggregate` folder (overall) plus one folder per active sampling rate (e.g. `250ms`, `1000ms`) created because at least one subscribed item uses that rate (subscriptions are usually driven by [Tag Groups](../platform/tags/tag-groups.md), but can come from other sources like Transaction Group OPC Items). Each device also has a `MonitoredItemCount` tag (total subscribed items, including diagnostics).

Ignition batches individual item reads into **requests**; a request is the unit of read grouping, sized per-protocol. Sample Group Diagnostic tags (per rate folder + Aggregate):

| Tag | Meaning |
|---|---|
| `ActualSamplingInterval` | Actual achieved interval, ms (not in Aggregate). |
| `ActualThroughput` | Requests executed in the last interval. |
| `IdealSamplingInterval` | Configured interval, ms (not in Aggregate). |
| `IdealThroughput` | `RequestCount * 1000 / SamplingInterval`. |
| `OverloadFactor` | `100 * (QueueDuration / ActualSamplingInterval)`; >100% = falling behind (not in Aggregate). |
| `QueueDuration` | Avg time a request waits in queue (not in Aggregate). |
| `RequestCount` | Requests in the group. |

Plus **Execution Timer** tags (both per-group and Aggregate): `NthPercentile`, `Count`, `Max`, `Mean`, `Min`, `MeanRate`, `OneMinuteRate`, `FiveMinuteRate` — all measuring round-trip time from request-sent to response-received.

---

## Device drivers

All drivers require the **OPC UA module** installed and enabled (a missing/disabled OPC UA module faults the driver with "Missing Dependency"). General connection flow for every driver: Gateway → **Connections > Devices > Connections** → **Create Device Connection +** → pick driver → fill Name/Hostname → **Create Device Connection**. New devices show **Disconnected** briefly before moving to **Connected**.

### Quick reference — port, OS and browsability by driver

| Driver | Default port | Transport | Browsable? | OS support |
|---|---|---|---|---|
| Allen-Bradley (all variants) | 44,818 (Ethernet/IP) or 2222 (CSP, PLC5/SLC auto-detected) | TCP | Yes (tag-based) | Any (Java) |
| Siemens Driver (S7-300/400/1200/1500) | 102 | TCP | No — manual/CSV import | Windows, Linux, Mac, ARM |
| Siemens Enhanced Driver | 102 | TCP | Yes if Symbolic (S7-1200/1500 only) | Windows, Linux x64/ARM — **not Mac**; GLIBC ≥2.34(x64)/≥2.17(ARM) |
| Modbus TCP / RTU over TCP | 502 | TCP | No — manual or Address Map | Any |
| Modbus RTU | Serial (COM port) | Serial | No | Any |
| BACnet/IP | 47,808 | UDP | Yes | Any |
| DNP3 Driver / Legacy | 20,000 | TCP | N/A (GVI addressing) | Windows x64, Linux x64/arm32/arm64 — **not macOS** |
| IEC 61850 | 102 | TCP (MMS) | Yes (via SCD file) | Windows, Linux x64 — **not ARM/macOS** |
| Mitsubishi TCP (MELSEC/SLMP) | device-specific (set in GX Works) | TCP | No — manual/CSV/GX Works import | Any |
| Modbus-alike Omron FINS/TCP | 9,600 | TCP | No — manual/CSV import | Any |
| Omron FINS/UDP | 9,600 | UDP | No — manual/CSV import | Any |
| Omron NJ | — (CIP) | TCP | No — export from Sysmac Studio | Any |
| UDP Driver | user-defined | UDP | N/A (raw stream) | Any |
| TCP Driver | user-defined | TCP | N/A (raw stream, writeback optional) | Any |
| Programmable Device Simulator | n/a (no network) | — | n/a | Any |

### Allen-Bradley (EtherNet/IP)

Five drivers, chosen by firmware/model — all use **tag-based (symbolic) addressing**: Ignition browses the device and you drag tags in (no manual OPC Item Path needed, except Micro800 manual entries).

| Driver | Devices supported |
|---|---|
| **Logix** (recommended) | ControlLogix/CompactLogix firmware v21+ (optimized); works with earlier firmware at reduced performance. |
| **CompactLogix (Legacy)** | CompactLogix firmware ≤ v20.18. |
| **ControlLogix (Legacy)** | ControlLogix firmware ≤ v20.18 via 1756-ENET/A or /B. |
| **Micro800** | Micro820/850/870. |
| **MicroLogix** | 1100/1400 direct Ethernet/IP, or 1100/1400 via 1761-NET-ENI, or via Spectrum Controls WebPort 500. MicroLogix 1200/1500 need "Disable Processor Browse" and don't support Input Parameters. |
| **PLC5** | PLC-5 L/20E, L/40E, L/80E over Ethernet/IP, or any PLC-5 over DH+ via 1756-DHRIO. ASCII data types unsupported. |
| **SLC** | SLC 5/05 direct Ethernet, or 5/03–5/05 via 1761-NET-ENI, or 5/04 via 1756-DHRIO, or via WebPort 500. |

Common connection settings: **Name**, **Description**, **Enabled**; Connectivity: **Hostname**, **Local Address**, **Timeout**, **Connection Path**; Advanced: **Disable Automatic Browse/Disable Processor Browse**, **Show String Arrays**, **Status Request Poll Rate**, **Max Concurrent Requests**, plus driver-specific extras (Logix: Automatic Rebrowse, Identity Request Frequency, CIP Connection Size/Timeout, Slot Number; Micro800: Write Priority Ratio, CIP Connection Size/Timeout).

**Logix driver boolean-array mapping**: a `BOOL[64]` in the PLC becomes `DWORD[2]` in Ignition, e.g. `boolTag[32]` (PLC) → `boolTag[1].0` (Ignition). Logix also supports DT, LDT, LTIME, TIME, TIME32 types not exposed by the legacy drivers.

**Micro800 data types**: DATE, TIME, BOOL, SINT, INT, DINT, LINT, USINT, UINT, UDINT, ULINT, REAL, LREAL, STRING (UTF-8, max 80 chars), BYTE, WORD, DWORD, LWORD. Not all globals are browsable (UDTs, system structures, BOOL arrays, non-zero-start arrays) — import a CSV or ZIP exported from **Connected Components Workbench** (right-click controller → Export → Variables (CSV) or Export Device with "Export Variables Only" then convert .7z→.zip) via the device's **Addresses** panel. **Bit-level addressing**: `MyUint.1`, `MyByteArray[0].7`, `MyUdt.MyDint.11`.

**Allen-Bradley Connection Paths** (needed when routing through a bridge/Ethernet module, e.g. ControlLogix Gateway → downstream PLC): always an **even number of comma-separated entries**, built as repeating (exit-code, destination) pairs:

```
1 = move to backplane
<slot number> = module in that slot
<exit port/channel of that module>
<address of next module: IP / ControlNet address / DH+ station (octal)>
... repeat as needed, ending with: 1, <processor slot>
```

Module exit/entry codes:
```
ENET/ENBT/EN2T:  Exit 1=Backplane, 2=Ethernet Port   → Enter: IP Address
CNB:             Exit 1=Backplane, 2=ControlNet Port → Enter: ControlNet Address
DHRIO:           Exit 1=Backplane, 2=DH+ Chan A, 3=DH+ Chan B → Enter: DH+ Station # (octal 0–77)
```
Worked examples: ControlNet to PLC5 = `1,4,2,12,1,0`; ENBT to ControlLogix = `1,3,2,192.168.0.56,1,0`; DH+ to ControlLogix = `1,3,2,23,1,0`. PLC5/SLC-specific short form (via 1756-DHRIO): `1,<DHRIO slot>,<DHRIO channel: 2=A/3=B>,<DH+ node # octal>`.

### Siemens (S7 protocol over TCP/IP)

Two driver families:

- **Siemens Driver module** (Windows/Linux/Mac/ARM): separate S7-300 / S7-400 / S7-1200 / S7-1500 drivers, **absolute addressing only**, no browsing — manually create tags or bulk-import a tags CSV.
- **Siemens Enhanced Driver module** (Windows/Linux x64/ARM, **not Mac**; requires GLIBC ≥2.34 x64 / ≥2.17 ARM as of 8.3.3+, which excludes Ubuntu 20.04/Debian 10/11): one driver for all four families; supports **Absolute or Symbolic** addressing, browsing, and optimized-block access on S7-1200/1500. S7-300/400 must use Absolute. 250-device connection limit. Linux hosts need `libssl.so`/`libcrypto.so` symlinks for secure connections (provided automatically in Docker images).

**S7-1200/1500 prerequisites** (both driver families): only global DBs accessible; TM/CT areas not read/writable (Absolute addressing); **Optimized block access must be OFF** for the target DB(s) (Symbolic addressing on Enhanced driver is exempt); Protection & Security must allow **Full access (no protection)** + **PUT/GET communication**. Alternative: some S7-1200/1500 have an onboard OPC UA server you can connect to directly instead.

**Connect**: Gateway → Devices → Connections → Create Device Connection → select one of the four **Siemens SxxDriver** entries (Siemens Driver module) or **Siemens Enhanced Driver** (Enhanced module) → Name + Hostname (IP) → for Enhanced also pick **Device Type** (S7-300/400/1200/1500) and **Address Type** (Absolute — required for S7-300/400; or Symbolic for 1200/1500) → Create Device Connection.

**Addressing syntax (Siemens Driver, absolute only)** — `[device]Area+DataType+Offset{.Bit}`:

Areas: `DBn` (data block n), `I` (inputs), `Q` (outputs), `M` (flags), `T` (timers), `C` (counters).
Data types: `X` bit, `B` byte (unsigned), `C` char (signed), `W` word (unsigned), `I` int (signed), `D` dword (unsigned), `DI` dint (signed), `REAL`, `STRING`/`STRING.LEN`, `DT` (S7-300/400/1500 only), `LI` long int (S7-1500 only), `LREAL` (S7-1200/1500 only). Offsets are absolute — `IW0` and `IW1` share a byte, so use `IW0`/`IW2` for non-overlapping words. Timers/counters need no data type; counters are BCD in the PLC but exposed as `UInt16`. Examples: `IB0`, `IW0`, `DB500,DI8`, `ISTRING24.50`, `IX20.3`, `T0`, `C0`.

**Addressing syntax (Siemens Enhanced, absolute — TIA-portal-like, supports arrays)**:
```
Numeric, I/Q/M:      <Area><DataType><Offset>[ArrayDims]
Numeric, DB:          DB<n>.[DB]<DataType><Offset>[ArrayDims]
Bit, I/Q/M:            <Area>X<Offset>[.Bit][ArrayDims]
Bit, DB:                DB<n>.[DB]X<Offset>[.Bit][ArrayDims]
String, I/Q/M:         <Area>STRING<Offset>[Length]
String, DB:             DB<n>.[DB]STRING<Offset>[Length]
Timer/Counter:          T<Offset> / C<Offset>
```
Examples: `IW0` (Word@0), `QI12` (Int@12), `MD5[2]` (array of 2 DWords@5), `IW0[3,2,2]` (multidim array of Words), `DB500.DBREAL10`, `DB400.DBDI52[4,8]`, `DB1.DBX9.7` (bit 7 @ offset 9), `DB500.STRING255[7]`. Data type map: BOOL→Boolean, BYTE→Byte, WORD→UInt16, DWORD→UInt32, LWORD→UInt64, SINT→SByte, INT→Int16, DINT→Int32, LINT→Int64, USINT/UINT/UDINT/ULINT→Byte/UInt16/UInt32/UInt64, REAL→Float, LREAL→Double, S5TIME→UInt32(ms 0–9,990,000), TIME→Int32(ms), LTIME→Int64(ns), DATE→UInt16(days since 1990-01-01), TIME_OF_DAY→UInt32(ms since midnight), LTOD→UInt64(ns since midnight), DT→DateTime, LDT→UInt64(ns since 1970 epoch), DTL→not supported, CHAR/WCHAR/STRING/WSTRING→String.

**Symbolic addressing** (Enhanced, S7-1200/1500 only): create an OPC tag, click the Devices icon on OPC Item Path, browse the UA-server-like tree, Apply.

Connection settings: General (Name/Description/Enabled); Connectivity (Hostname, Port default 102, Local Address, Timeout); Advanced (PDU Size 240 default — raise for higher throughput if the CPU supports it, up to ~960; Rack Number default 0; CPU Slot Number default 2 [Siemens Driver] / Slot Number default 0 [Enhanced]; Reconnect After Consecutive Timeouts). Enhanced adds: Device Type, Address Type (Absolute/Symbolic), Optimize Writes (batches writes), **Secure Connection Mode** (`REQUIRED`/`PREFERRED` default/`DISABLED` — TLS; replaces the old boolean "Force Secure Connection" on upgrade), Password.

### Modbus (TCP, RTU over TCP, RTU)

Generic driver for **any** device speaking Modbus TCP or RTU-over-TCP (and native RTU serial) — not browsable, so addresses are either entered manually or via an **Address Map**. Only add **one** Ignition device connection per IP address, even for multiple unit IDs behind a gateway.

**Supported function codes**:

| Function | Code (hex) |
|---|---|
| Read Coils | 01 (0x01) |
| Read Discrete Inputs | 02 (0x02) |
| Read Holding Registers | 03 (0x03) |
| Read Input Registers | 04 (0x04) |
| Write Single Coil | 05 (0x05) |
| Write Single Register | 06 (0x06) |
| Write Multiple Coils | 15 (0x0F) |
| Write Multiple Registers | 16 (0x10) |
| Mask Write Register | 22 (0x16) |

**Connect**: Gateway → Devices → Connections → Create Device Connection → choose **Modbus TCP** (native TCP/IP), **Modbus RTU over TCP** (RTU framing tunneled in TCP), or **Modbus RTU** (serial) → Name + Hostname (TCP variants) or Serial Port (RTU) → Create.

Key settings by group:

| Group | Settings |
|---|---|
| Connectivity — TCP/RTU-over-TCP | Hostname, Port (default 502), Local Address, Communication Timeout |
| Connectivity — RTU (serial) | Serial Port, Bit Rate, Data Bits, Parity, Stop Bits, Handshake, Communication Timeout, RS-485 Mode |
| Request Optimization | Max Holding Registers per Read Request (125) / per Write Request (123), Max Input Registers per Request (125), Max Coils per Request (2000), Max Discrete Inputs per Request (2000), Concurrent Requests (not for RTU), Span Gaps |
| Write Request | Allow Write Multiple Registers Request, Force Multiple Register Writes, Allow Write Multiple Coils Request |
| Read Request | Allow Read Multiple Registers Request, Allow Read Multiple Coils, Allow Read Multiple Discrete Inputs |
| Advanced | Reconnect After Consecutive Timeouts (true, after 3), **Reverse Word Order** (32-bit values reversed), **Zero-based Addressing**, Max Retry Count (1) |
| String Handling | Reverse String Byte Order, Right Justify Strings, Read Raw Strings (include nulls) |

Tip: set **Max Holding Registers Per Request** to 1 while testing so one bad tag doesn't fault the whole batch read — restore it afterward or you'll strain the system once hundreds of tags exist.

**Manual addressing designators** — `[DeviceName]<Designator><Address>`:

| Designator | Meaning |
|---|---|
| `HR` | Holding Register 16-bit signed (`HR1` = 40001 elsewhere) |
| `IR` | Input Register 16-bit signed (`IR1` = 30001) |
| `C` | Coil bit (`C1` = 00001) |
| `DI` | Discrete Input bit (`DI1` = 10001) |
| `HRBCD` / `IRBCD` | 1-register BCD→decimal conversion |
| `HRBCD_32` / `IRBCD_32` | 2-register BCD conversion |
| `HRF` / `IRF` | 2 registers → Float |
| `HRD` / `IRD` | 4 registers → Double |
| `HRUS` / `IRUS` | 16-bit unsigned int |
| `HRI` / `IRI` | 2 registers → 32-bit signed int |
| `HRUI` / `IRUI` | 2 registers → 32-bit unsigned int |
| `HRI_64` / `IRUI_64` etc. | 4 registers → 64-bit signed/unsigned |
| `HRS<addr>:<len>` | Consecutive HRs as a string (len must be even — 2 chars/word) |

Examples: `[DL240]HR1024`, `[DL240]HRBCD1024`, `[DL240]IR512`, `[DL240]C3072`, `[DL240]HRS1024:20`. Unit ID prefix: `[DL240]3.HR1024`. Bit-level (needs Mask Write support): `[DL240]HR1024.0` (bit 0), `.10` (11th bit).

**Address Mapping** (drag-and-drop browsing substitute) properties: Prefix (letters/numbers/underscore; `HR`,`IR`,`C`,`DI` reserved), Start/End (0–65,535, sets how many mapped tags), Step (checked = combine adjacent 16-bit words into 32-bit, e.g. float), Radix (10 decimal or 16 hex — sets label numbering, e.g. 8=octal for the classic Direct Automation DL240 example), Unit ID (0 = first/only device on that IP), Modbus Type (table + size, e.g. "Holding Register (Int16)" or "(Float)"), Modbus Address (start address in that table, *not* prefixed with 3/4/00/10000 — the type dropdown supplies that). String data types cannot be mapped this way (Modbus Specific Addressing only). Example mapping the classic DL240 octal `V2000`–`V3777` → Holding Registers starting at 1024, Radix 8. Multiple unit IDs on one IP: same Prefix/Start/End/Type/Address rows, different Unit ID — the unit ID then appears as a browse folder. Import/export as CSV; example templates at inductiveautomation.com/downloads/extra-material under "Modbus Templates".

### BACnet (BACnet/IP over UDP; router needed for other media)

Two-step setup: **1) Local Device** (Ignition's presence on the network) then **2) Remote Device** (target). `Connections > Devices > BACnet` for local devices, `Connections > Devices > Connections` for remote.

**Connect — local device**: Connections → Devices → BACnet → Create BACnet Device → Name, Bind Address (IP or leave wildcard `0.0.0.0`), Bind Port (or leave 47808 default), Broadcast Address → Create BACnet Device.

**Connect — remote device**: Connections → Devices → Connections → Create Device Connection → **BACnet/IP** → Name, Local Device (from dropdown — set one up first if none shown), Remote Address (IP), Remote Device Number (instance number) → Create Device Connection.

A device only counts as "connected" once Ignition sends a Who-Is, receives an I-Am, and interrogates basic properties (object list + supported properties per object); results are cached and only re-read if `Database_Revision` changes (or you manually invalidate the browse cache via the 3-dot menu on the connection).

**Local device** settings: Name, Enabled, Bind Address (default `0.0.0.0` wildcard — needed to receive broadcast I-Am responses), Bind Port (47808 default), Broadcast Address, Network Prefix Length (24), Device Number (1000), Network Number (1), Foreign Device Registration Enabled (false) + BBMD Address/Port (47808) for bridging across subnets via a BACnet Broadcast Management Device, and (Ignition redundancy) Backup Device Number.

**Remote device** settings: Name/Description/Enabled; Local Device (which local device to use); Remote Address; Remote Port (47808); Remote Device Number; **COV Enabled** (true default — Change-of-Value subscription for Present_Value/Status_Flags only; false = poll everything); COV Heartbeat Interval (5s — reads `System_Status` as a keepalive, 3 consecutive failures → uncertain quality); COV Subscription Lifetime (900s, 0=indefinite, renewed at 75% of lifetime); COV Subscription Retry Interval (120s, 0=leave failed items polled instead); Confirmed Notifications Enabled (false); Discovery Timeout (5s); Write Priority (8, for commandable properties).

**OPC item path syntax**: `ns=1;s=[MyRemoteDevice]AnalogInput100.Present_Value` = `[RemoteDeviceName]ObjectType+ObjectIdentifier.Property`. Supported object types: Device, AnalogInput/Output/Value, LargeAnalogValue, BinaryInput/Output/Value, MultiStateInput/Output/Value. BinaryInput/Output/Value objects get an `ElapsedActiveTime` folder (`Elapsed_Active_Time` long, writable; `Time_Of_Active_Time_Reset` document, read-only).

`Status_Flags` returns a JSON document — extract bits with an expression tag, e.g. bit 0 (`In_Alarm`): `getBit(jsonGet({[.]Status_Flags}, 'Value[0]'), 0)`. Can write `None` (Python) to a subscribed tag for a null BACnet write. For objects the driver doesn't model, use `system.bacnet.readRaw` / `writeRaw` (returns raw BACnet4j types, not OPC-translated) — use with caution, writes can have unintended device consequences.

### DNP3 (two drivers, water/electric-utility protocol)

**DNP3 Driver** (current, default on new installs) vs **DNP3 Driver (Legacy)** (deprecated, no updates). Neither supports DNP3 Secure Authentication. Supported OS: Windows x64, Linux x64/arm32/arm64 (**not macOS**). Scripting namespaces: `system.dnp` (current) vs `system.dnp3` (legacy) — kept separate to avoid conflicts.

| | DNP3 Driver | DNP3 Driver (Legacy) |
|---|---|---|
| Data acquisition modes | Event-based polling (Class 1/2/3 + integrity poll), unsolicited messaging, explicit GVI reads | Explicit reads (Read function code), unsolicited messaging |
| Aliased points | Not supported | Supported (map friendly names to G/V/I addresses) |

**Connect**: Gateway → Devices → Connections → Create Device Connection → **DNP3 Driver** or **DNP3 Driver (Legacy)** → Name + Hostname (outstation IP) → Create Device Connection. Make a **separate device connection per outstation**, setting matching/opposite Source and Destination addresses for master and outstation on each.

Common connectivity settings: Hostname, Port (20000 default), Source Address (master, default 3), Destination Address (outstation, default 4 — must be opposite pairing), Response/Message Timeout (5000 ms), Keep Alive Timeout (current driver: 3,600,000 ms).

**Current driver's Data Acquisition settings**: Integrity Poll Period (3,600,000 ms, 0=disabled), Class 1/2/3 Poll Period (10,000 ms each, 0=disabled), Unsolicited Event Classes (blank unless using unsolicited messaging). **Advanced**: Analog/Binary Operation Command Mode (`DIRECT_OPERATE` default or `SELECT_BEFORE_OPERATE`), Read After Operate + Delay, Binary Trip Close Code / Op Type (`LATCH`/`PULSE`) / Count / On-Off Time; Logging: Auto Time Sync (true), Application/Physical Layer Debug Logging.

**Internal Indication (IIN) bits** exposed as read-only diagnostic points: `IIN1.0` Broadcast Received, `.1/.2/.3` Class 1/2/3 Events available, `.4` Need Time, `.5` Local Control, `.6` Device Trouble, `.7` Device Restart; `IIN2.0` No Func Code Support, `.1` Object Unknown, `.2` Parameter Error, `.3` Event Buffer Overflow, `.4` Already Executing, `.5` Configuration Corrupt, `.6`/`.7` Reserved.

**Point types (Legacy driver GVI addressing)**: SingleBitBinaryInput (Group 1), DoubleBitBinaryInput (3), Binary Output (10), Counter (20), FrozenCounter (21), AnalogInput (30), FrozenAnalogInput (31), AnalogOutput (40), OctetString (110) — each with a list of supported variations (packed/with-flags/16-bit/32-bit/float/double, see device docs). **Aliased point address format**: `g<group>v<variation>i<index>`, e.g. `g30v1i20`; Browse Path e.g. `Facility1/Voltage`.

**Buffered Events / Sequence of Events**: set the Tag Group's **Queue Size** > 1 to preserve missed events across a disconnect (oldest dropped when full); on reconnect the driver replays buffered events oldest→newest, which can retrigger alarms/history/event scripts. For true event-based reporting set the Tag Group's **OPC UA Sampling Interval to 0** (nonzero intervals can collapse multiple events into one update) and size **OPC UA Queue Size** to the max anticipated event burst.

### IEC 61850 (substation / MMS client — no GOOSE/SV)

Windows/Linux x64 only (no ARM/macOS); requires a modern Visual C++ Redistributable. One device connection per IED (Intelligent Electronic Device). Strongly recommended to upload an **SCD** (Substation Configuration Description) file per connection — without it, every restart re-requests *all* Logical Nodes (heavy network load), and quality/timestamp resolution may not work at all.

**Connect**: Connections → Devices → Connections → Create Device Connection → **IEC 61850 MMS Client Driver** → Name + Hostname → Create Device Connection → on the created device's 3-dot menu, **Manage SDL File** → upload an SCD file → select the IED to request reports for → Save Changes. Default Port is 102, default Request Timeout 2000 ms.

Device settings groups: General (Name/Description/Enabled); Main (Hostname, Port=102, Request Timeout=2000); SCD File Setting (Use SCD File=false default, Use Configured Hostname, Use Configured OSI Params, IED Name, Access Point Name — the last two auto-populate from the SCD upload); Advanced Client/Server OSI Parameters (AE Qualifier=12, AP Title=1,1,1,999,1, Presentation/Session/Transport-Selector); Misc (Use Report Timestamp, Password).

Address format (hierarchical): `[IED]LogicalDevice/LogicalNode.DataObject.Attribute`, e.g. `[SSSA_52AFA_FPR]LD0/LLN0.rcbDigitals05$SSSA_52AFA_FPRCTRL/CBCILO1.EnaCls.stVal`. Attributes defined under multiple Functional Constraints (FC) get an `[FC]` suffix, e.g. `...stVal[ST]` — upgrades auto-migrate colliding NodeIds and old unsuffixed tags report `Bad_NodeIdUnknown` until re-addressed.

Devices folders under the UA server: **Model** (pollable logical nodes), **Reports** (per-RCB folders, subscribe to enable a report via `RptEna`), **Diagnostics**. Reports are **Buffered** (survive a disconnect) or **Unbuffered** (data lost during disconnect); an RCB can only be enabled by one client connection at a time — replicate the report on the IED to share across Gateways.

**Control functions** (`system.iec61850.*`): `getControlParams`, `select`, `operate`, `cancel`. `ctlModel` values: 0 Status-only, 1 Direct-normal-security, 2 SBO-normal-security, 3 Direct-enhanced-security, 4 SBO-enhanced-security. **Safety-critical**: the `Check` parameter on `getControlParams`/`select` controls whether **CILO** (Control Interlock) and **RSYN** (Synchrocheck) logical nodes are honored — `Check=00` means the IED executes the command even with an active interlock or unsynchronized grid; misuse is called out as potentially catastrophic for high-voltage substations. File functions: `listFiles`, `readFile`, `writeFile` (paths are local to the **Gateway**, not the browser client).

### Mitsubishi (MELSEC via TCP, SLMP)

Supported series: iQ-R, iQ-F (FX5U), Q, L, F (FX3). Requires GX Works configuration first (Enable/Disable Online Change → Enable All (SLMP); Communication Data Code → Binary; add an SLMP Connection Module with Protocol=TCP) — GX Works also supplies the Hostname/Port values needed for the Ignition connection. Settings include Series, PC Number (255 default — station number of access target, or relay station if multi-drop), Network Number (0), Request Destination Module I/O Number (1023) and Station Number (0), plus Request Optimization: Max Gap Size (-1 = auto-optimize for fewest requests) and Write Priority Ratio (5).

**Connect**: Connections → Devices → Connections → Create Device Connection → **Mitsubishi TCP** → Name, Hostname, Port, optional Local Address → select **Series** (iQR/iQF/Q/L) under Device Settings, matching the physical hardware exactly → Create New Device. Addresses can then be entered on the Gateway's **Addresses** panel (individually, or bulk import/export a CSV / a GX Works-exported CSV) or as an OPC tag directly in the Designer.

**Addressing**: `Area{<DataType{[array]}>}Offset{.Bit}`. Example: `D<int32>0[0..9]` style dimensional arrays with `[0..9]` (10 elements, 1-D) or `[0..4,0..5]` (2-D, 30 elements).

Area/keyword table (Q/L, iQ-F, iQ-R): Special Relay `SM`(bit), Special Register `SD`(word), Input `X`(bit), Output `Y`(bit), Internal Relay `M`(bit), Latch Relay `L`(bit), Annunciator `F`(bit), Edge Relay `V`(bit), Link Relay `B`(bit), Step Relay `S`(bit), Data Register `D`(word), Link Register `W`(word), Timer contact/coil/value `TS`/`TC`/`TN`, Long timer `LTS`/`LTC`/`LTN`(dword, not Q/L), Retentive timer `STS`/`STC`/`STN`, Counter `CS`/`CC`/`CN`, Link Special Relay/Register `SB`/`SW`, Direct Access I/O `DX`/`DY`, Index Register `Z`/`LZ`, File Register `R`/`ZR`, Refresh Data Register `RD`. F-series (FX3) has a reduced set (`X`,`Y`,`M`,`S`,`D`,`TS`,`TN`,`CS`,`CN`,`R`).

Offsets are decimal by default; **hex** for `X`/`DX`/`Y`/`DY`/`B`/`SB`/`W`/`SW` on iQ-R/Q/L; **octal** for `X`/`Y` on iQ-F/F(FX3). Optional data type: `Bool`,`Int16`,`Int32`,`Int64`,`UInt16`,`UInt32`,`UInt64`,`Float`,`Double`,`String`(needs length, e.g. `D<string10>0`, auto-rounds to even),`Wstring`; modifiers `@BE`/`@LE`(default)/`@HL`(default)/`@LH`. Types can only be combined *up* from native size, never down. Bit index on any integer type is **read-only**.

### Omron — two drivers

**Omron FINS** (TCP or UDP transport). **Connect (TCP)**: Devices → Connections → Create Device Connection → **Omron FINS/TCP** → Name + Hostname → Create. **Connect (UDP)**: same path → **Omron FINS/UDP** → Name, Bind Address (Gateway IP), Remote Address (device IP), FINS Source/Destination Node → Create. Default port for both is **9,600**.

Settings: FINS Source/Destination Network (0–127), Source/Destination Node (0–254, typically last IP octet), Source/Destination Unit (0–255); Request Optimization: Concurrent Requests, Max Request Size, Max Gap Size, Write Priority Ratio. Addresses import via a CSV/TSV/CXR file through the device's **Addresses** panel (3-dot menu), or via manual OPC-tag entry in the Designer.

Data areas: CIO, Work `WR`/`W`, Holding Bit `HR`/`H`, Auxiliary Bit `AR`/`A`, Timer `TIM`/`T`, Counter `CNT`/`C`, Index Register `IR`(int32), Data Register `DR`, `DM`/`D`, `EM`/`Exx` (banks E00–E18 hex, 25 banks). Syntax: `Area{<DataType>}Offset{.Bit}`. Types: Bit, Bool, Int16/32/64, UInt16/32, Float, Double, String, BCD16, BCD32; modifiers `@BE`(default)/`@LE`, `@HL`/`@LH`(default). Examples: `CIO0` (Int16@0), `CIO<Int32>1`, `CIO<Int64>3.0` (bit 0), `TIM0` (present value), `TIM<Bool>0` (completion status), `E001000` (Int16, EM bank 0 offset 1000). Manual CSV tag file: `$ignitionHome/data/opcua/devices/$deviceName/tags.csv`, columns Browse Path/Address/Description; requires a device restart to pick up.

**Omron NJ Driver** (Sysmac / NJ series). **Connect**: Devices → Connections → Create Device Connection → **Omron NJ Driver** → Name + Hostname → Create Device Connection; then use the connection's 3-dot menu → **Addresses** to import/map tags before they're browsable. Settings: Connection Size (default/max 1994 bytes), Date/Time Offset (hours, default 0), Slot Number (0), Concurrency (2, 1:1 with CIP connections). Export global variables from Sysmac Studio via **Tools > Export Global Variables > CX-Designer** (tab-separated, paste into a text file to import). Tag mapping columns: Browse Name (struct members `.`-separated), Datatype, Characters (String max length), Elements (blank=scalar; `0..N` for arrays, or a single int = last offset shorthand; comma-separated groups for multidimensional, e.g. `0..3,0..3`), R/W. Extra data types: `TIME_NSEC`, `DATE_NSEC`, `TIME_OF_DAY_NSEC`, `DATE_AND_TIME_NSEC`. **Note**: the configured Elements range must match the PLC program's own range, or indices silently offset (e.g. PLC `0..4` mapped in Ignition as `3..7` shifts every element by 3).

### Programmable Device Simulator

No real network/PLC — a scriptable value generator, useful for realtime/history/alarm testing. Program = a table of instructions (Time Interval, Browse Path, Value Source, Data Type), stepped at a configurable **Base Rate** (ms), optionally **Repeat**ing. `Legacy Mode` lets pre-8.x simulator tags import without recreation.

Value Source functions: `sine(min,max,period,repeat)`, `cosine(...)`, `square(...)`, `triangle(...)`, `ramp(min,max,period,repeat)`, `realistic(setPoint,proportion,integral,derivative,repeat)` (PID-driven), `random(min,max,repeat)`, `list(v1,v2,...,repeat)`, `qv(value,qualityCode)` (simulate bad quality), `readonly(value)`. Defaults: min=0, max=100, period=10 (time intervals), setPoint=100, proportion=1.2, integral=0.06, derivative=0.25, qualityCode=Good, repeat=true.

Preloaded programs: **Generic** (varied data types/functions), **Dairy** (ControlLogix-like UDT-style structure), **SLC** (basic SLC address structure); or **Import** a 4-column CSV (Time Interval, Browse Path, Value Source, Data Type). Preloaded programs prefix tags with `_Meta:` for legacy compatibility (exported CSVs strip it — re-add manually if re-importing). **Meta tags** (under `[Controls]`, non-persistent across restart): `Base Rate`, `Pause`, `Program Counter`, `Repeat`, `Reset`.

### UDP and TCP Driver (raw stream ingestion — not a PLC protocol driver)

For simple devices like barcode scanners/scales that push raw ASCII/byte data. **UDP driver**: passive listener only. **TCP driver**: passive listener, plus optional **writeback** (writable tags send data back to the device). Both expose, per configured port, one tag for the whole message plus one tag per configured field.

**Connect (TCP)**: Devices → Connections → Create Device Connection → **TCP Driver** → Name, Port(s) (comma-separated), Address (device IP) → Create. **Connect (UDP)**: same path → **UDP Driver** → Name, Port(s), Address (`0.0.0.0` to listen on all interfaces) → Create. Devices connect to **ports**, not a PLC identity — the remote device must be configured to send data to those ports.

Settings: Message Delimiter Type (Packet Based / Character Based / Fixed Size) + Message Delimiter, Field Count, Field Delimiter; TCP-only: Writeback Enabled, Writeback Message Delimiter, Write Timeout (5000 ms default); Connect/Inactivity Timeout (0 = disabled). Delimiter escape characters: `\t` tab, `\b` backspace, `\n` newline, `\r` CR, `\f` form feed. Typical reliable scan rates 100–200 ms (TCP can theoretically hit 25 ms; UDP depends on network conditions) — tag values only update as fast as the Tag Group's scan class, and Ignition **drops** messages that arrive faster than that. Address browsing path example: `[TCP Driver] > 5000 > Message`.

### Simulators / testing without hardware

Use the **Programmable Device Simulator** (above) for scripted values, or connect to a hosted 3rd-party simulator via OPC UA client (Kepware demo server, Unified Automation demo server) — see Third-Party OPC Servers below.

### Third-party OPC servers

- **OPC UA**: connect like any OPC UA client connection (Kepware, Matrikon, etc.) — third-party server must support **at least OPC UA 1.03 datatype dictionaries** to read structured values. Worked example for **Kepware/KEPServerEX**: create OPC UA Connection → discover/select server & endpoint → trust cert → (most KEPServer installs require Username/Password — anonymous is often disabled) → connection shows **Faulted** until you go into **KEPServerEX's own OPC UA Configuration Manager > Trusted Clients**, trust "Ignition OPC UA Client", Reinitialize the server, then go to Ignition's **OPC > Security** page and **Trust** the now-Quarantined client cert. Failover: two independent Kepware copies, Failover Enabled + Failover Endpoint on the Ignition connection; **Backup** properties are for a *pair of redundant Ignition Gateways* pointed at the same Kepware server, not device failover. If a 3rd-party UA server doesn't automatically accept Ignition's client cert, download it manually from **OPC > Security > Client tab > (3-dot) Download** and hand it to the target server per its own docs.
- **OPC COM (OPC-DA, Windows only, requires OPC COM module)**: install **OPC Core Components** (from opcfoundation.org, matching 32/64-bit to your Java/Ignition install) on the Ignition host *and* on the remote OPC server host if remote. Create connection via **OPC > Connections > Create OPC Connection > OPC-DA COM Connection**, Local or Remote (Remote needs Host Machine + optional CLSID from `HKEY_CLASSES_ROOT\OPCServerName\CLSID`). Common faults: DCOM security not configured (add ANONYMOUS + Everyone with Allow to both Access/Launch and Activation Permissions, Limits and Defaults, on **both** the Ignition host and the OPC server host, via Windows **Component Services**); Ignition (running as SYSTEM) launching a *second* OPC server instance with no config — fix by setting the OPC server's DCOM Identity to **The interactive user**; `E_CLASSNOTREG` = Core Components not installed correctly.

---

## Event Streams (new in 8.3)

Event Streams is a project resource providing a unifying, **subscription/event-driven** (not polling) construct for handling asynchronous data, replacing ad-hoc scripts scattered across subsystems. Built and edited in the Designer.

### Stage pipeline: Source → Encoder → Filter → Transform → Encoder → Buffer → Handler(s) → Error Handler

1. **Source** — origin of data. Types: **Kafka** (needs Kafka module), **HTTP Endpoint** (needs Web Dev module), **Event Listener**, **Tag Event**. (An **Alarm** event type also exists, driven through the Alarm Notification pipeline's **Event Stream Source block** combined with an Event Listener source, not a standalone source type.)
2. **Event objects** = the payload flowing through the stream, split into **primary data** (any Java object, usually `byte[]`/`String`) and **metadata** (source-specific, e.g. Kafka topic/partition/offset).
3. **Encoder** (appears twice: after Source, and after Transform if enabled) — converts data to **String**, **JsonObject**, or **Byte[]**; default is JSON. Includes a character-encoding table (UTF-8/UTF-16/BASE_64). *Not* a substitute for Transform.
4. **Filter** (optional script) — takes `event` (`data`, `metadata`) and `state` (`lastEvent`, `lastEmittedEvent`, plus any user-added keys) and returns a boolean; `False` drops the event silently.
5. **Transform** (optional script) — takes the same `event`/`state` args, returns a new object that becomes the payload going forward; used for data prep before handling.
6. **Buffer** — batches events before they reach handlers. Properties: **Debounce** (ms to wait for another event before flushing; resets on each new event; default 100), **Max Wait** (hard flush ceiling, ms; default 1000), **Max Queue Size** (0 = unlimited), **Overflow** (`DROP_OLDEST` / `DROP_NEWEST` once Max Queue Size is hit — dropped events are *not* forwarded). Buffer won't release queued events while a handler is still processing a previous batch.
7. **Handler(s)** — one or more, run sequentially, individually reorderable/enable-able. Types: **Kafka** (needs Kafka module), **Database** (needs SQL Bridge), **HTTP**, **Gateway Event**, **Gateway Message**, **Logger**, **Script**, **Tag**.
8. **Error Handler** — final catch-all script, invoked when a handler throws and that handler's Failure Mode is `ABORT`.

### Handler expressions (extracting data/metadata into a handler field)

Use curly-brace dot notation inside expression-language fields: `{event.metadata.topic}`, `{event.data.name}`, etc. — see the **Source Data and Metadata** reference below for what each source exposes.

### Common handler settings

- **Enabled** — per-handler toggle.
- **Failure Handling** modes: `IGNORE` (log, continue to next handler, tell source it succeeded), `ABORT` (log, stop the chain, tell source it failed, triggers Error Handler), `RETRY` (log + retry after a delay). RETRY sub-properties: **Retry Strategy** (fixed/exponential), **Retry Count** (default 1), **Retry Delay** (seconds, default 1 — initial delay if exponential), **Multiplier** (exponential only, default 1), **Max Delay** (ms, exponential only), **Retry Failure** behavior once retries exhausted (`IGNORE`/`ABORT`).

### Source types

| Source | Requires | Notes |
|---|---|---|
| **Kafka** | Kafka module | Data arrives as `byte[]`, re-encodable downstream. |
| **HTTP Endpoint** | Web Dev module | Auto-mounted at `/system/eventstream/{projectName}/{resourcePath}`; accepts POST/PUT. |
| **Event Listener** | — | Not configurable. Receives payloads relayed from Gateway Messages or another event stream's **Gateway Event** handler. |
| **Tag Event** | — | Payload = Java object; can publish scalar-only or the full qualified value. |

**Kafka source properties**: Subscription Type (**Consumer Group** — uses Group ID + Offset Reset [`Latest`/`Earliest`/`None`], or **Partition** — uses Partition + Offset), Connector (which Kafka Connector), Topic (dropdown, or a regex expression to subscribe to multiple topics), Group ID, Partition, Max Records per poll (500), Poll Timeout (100 ms), Offset Reset, Offset, Additional Consumer Properties (key=value pairs — see [Kafka's consumer configs](https://kafka.apache.org/documentation/#consumerconfigs)).

**HTTP Endpoint source properties**: Require HTTPS (true default), Require Authentication (false), User Source (if auth required), Required Roles, Max Auth Retries.

**Tag Event source properties**: Value/Quality/Timestamp trigger toggles (all true default — any of these changing fires the stream), Skip Initial Value (false — whether values captured on config-save trigger the stream), Tag Path(s) (one per line; supports folder- and tag-level [wildcards](../platform/tags/tag-paths/wildcards-in-tag-paths.md)). **8.3.2+**: subscribing to [Alarm Metrics](../platform/tags/tag-properties/tag-alarm-properties/tag-alarm-properties.md#runtime-alarm-metrics-properties) in the tag path always triggers on initialization (they start NULL), ignoring Skip Initial Value.

### Source Data/Metadata extractable fields (via `{event.data.X}` / `{event.metadata.X}`)

- **Kafka** — metadata only: `topic`, `partition`, `offset`, `headers`, `key`. (No pre-existing data fields — user-supplied.)
- **HTTP** — metadata only: `method`, `headers`, `parameters`, `scheme`, `remoteAddr`, `remoteHost`.
- **Alarm** — data only: `eventId` (UUID), `source` (qualified path), `displayPath`, `priority` (int 0–4: Diagnostic/Low/Medium/High/Critical) + `priorityReadable` (string), `eventType` (int 0–3: Cleared&Ack/Cleared&Unack/Active&Unack/Active&Ack) + `eventTypeReadable`, `eventFlags` (bitmask), `eventTime`.
- **Tag Event** — data: `value`, `quality`, `timestamp`. Metadata: `tagPath`, `isInitial` (bool), `previousValue` (qualified: value+quality+timestamp).

### Handler types and their properties

| Handler | Requires | Purpose |
|---|---|---|
| **Kafka** | Kafka module | Publish the event to a Kafka topic. |
| **Database** | SQL Bridge module | INSERT or UPDATE a SQL table. |
| **HTTP** | — | Fire a POST/PUT to an external URL. |
| **Gateway Event** | — | Forward to another event stream (same or a different project/Gateway). |
| **Gateway Message** | — | Send a Gateway Message (same mechanism as `system.util.sendMessage`). |
| **Logger** | — | Write a log entry. |
| **Script** | — | Run arbitrary Python; output becomes a `PyObject`. |
| **Tag** | — | Write value/quality/timestamp to a tag. |

Per-handler properties:

- **Kafka** — Connector, Topic, Partition, Timestamp, Key, Value, Headers (dict), Additional Producer Properties (dict; see [Kafka's producer configs](https://kafka.apache.org/documentation/#producerconfigs)).
- **Database** — Database (connection dropdown), **Mode** (`INSERT` uses the Column Mapping table; `UPDATE` uses the Where Clause Configuration table), Table Name (dropdown or new name), Automatically Create Table (true), Store timestamp to (column), **Bypass Store and Forward** (false — enabling skips the [Store and Forward](../platform/store-and-forward/store-and-forward.md) system entirely), Column Mapping (column name + SQL type + value), Where Clause Configuration (column + operator + value).
- **HTTP** — URL, Type (`POST`/`PUT`), HTTP Version (`HTTP/2` default), Headers (list of key/value pairs), Body (byte payload, expression-evaluated), Connect Timeout (30,000 ms), Cookies Enabled (true).
- **Gateway Event** — Project (dropdown or expression), Path (target event stream — **must** have an Event Listener source configured; dropdown or expression, so you can fan out to different streams dynamically), Payload (dict, expression-capable), Remote Gateway Name.
- **Gateway Message** — Project, Message Handler (name), Payload (dict), Properties (`scope`, `clientSessionID`, `user`, `hasRole`, `hostName`, `remoteServers` — same parameter set as [`system.util.sendMessage`](../appendix/scripting-functions/system-util/system-util-sendMessage.md#parameters)).
- **Logger** — Name (string or expression), Log Level (`TRACE`/`DEBUG`/`INFO`/`WARN`/`ERROR`), Messages (string or expression).
- **Script** — free-form; no configurable properties beyond the script body.
- **Tag** — Tag Path (expression-capable, dynamic per event), Value (expression, typically pulled from the payload), Quality (string or int — see [Quality Codes](../platform/tags/quality-codes-and-overlays/quality-codes-and-overlays.md#quality-code-reference-table)), Timestamp (expression).

### Testing and monitoring

**Test Controls panel** (toggle via the Test Panels icon in the Designer):

| Property | Description |
|---|---|
| Source Object | Test with the most-recent live source object, or manually input data. |
| Encoder | `String`, `ByteArray (Base64)`, or `JsonObject` for the test payload. |
| Dry Run | Runs the event down the stream normally but does **not** persist it as a real immutable event. |
| Run All | Runs the full stream, or use the dropdown arrow to stop after just Filter or Transform. |

Per-stage test states after a run: `Disabled`, `Error` (processed, hit an issue), `Faulted` (compilation error — no test events processed at all), `Good`, `Ready`.

**Status panel** (right side of the Designer, live) reports:

| Metric | Description |
|---|---|
| Events Received | Total events the stream has received. |
| Events Filtered | Events that passed the filter stage. |
| Filter Execution | Time per event through Filter (avg / max / most-recent). |
| Transform Execution | Time per event through Transform (avg / max / most-recent). |
| Handler Execution | Time per event through each handler — one row per handler. |

The **Project Browser** shows live status icons next to each event stream's name (running/modified/disabled/failed — hover for a tooltip), and the **Gateway's Services page** lists every project's event streams with the same throughput metrics for Gateway-level monitoring (no Designer session required).

`system.eventstream.*` is the scripting namespace for interacting with event streams from code; consult the appendix scripting-functions reference for the full function list — it was not itself enumerated on the pages read for this reference.

### Worked pattern — Kafka topic to a tag write

A common Event Streams composition, combining several of the pieces above:

1. **Source**: Kafka, Subscription Type = Consumer Group, Topic = `sensors.telemetry`, Group ID = `ignition-consumer-1`, Offset Reset = `Latest`.
2. **Encoder**: `JsonObject` — the Kafka payload's `byte[]` is parsed into a JSON structure.
3. **Filter** (optional): drop events where a required field is missing, e.g. `return 'deviceId' in event['data']`.
4. **Transform** (optional): normalize/flatten the payload into the exact shape the handler needs.
5. **Buffer**: Debounce 100 ms / Max Wait 1000 ms to coalesce a burst of rapid Kafka messages into fewer downstream writes.
6. **Handler — Tag**: Tag Path = `[default]Sensors/{event.data.deviceId}/Value` (expression-built dynamic path), Value = `{event.data.reading}`, Quality = `Good`, Timestamp = `{event.metadata.timestamp}` (if present) or left to Ignition's own clock.
7. **Error Handler**: log the failure via `system.util.getLogger("KafkaIngest").error(...)` so a bad payload doesn't silently vanish.

Swap the Kafka source for an **HTTP Endpoint** source and this same pattern becomes a webhook receiver that turns POSTed JSON into tag writes, with **Require Authentication** protecting the endpoint.

---

## Cloud connectors

### Kafka Connector

Distributed event-streaming: **producers** publish records to **topics** (split into partitions) on a **broker**; **consumers** (optionally grouped into **consumer groups**, one consumer per partition per group) **pull** data, tracked by **offset**. Pull-based design lets consumers batch-optimize their own read rate. Bundled with Cloud Edition; add-on for standard Ignition; **not available on Edge**.

**Connection settings** (`Connections > Service Connectors > Connections > Create Connection > Kafka Connector`):

- Main: Name, Description, Enabled, **Bootstrap Servers** (`host:port` list — connect to *multiple* brokers for redundancy, not just one), SASL Mechanism (default GSSAPI), Security Protocol (`PLAINTEXT` default / `SSL` / `SASL_PLAINTEXT` / `SASL_SSL`), Username, Password (None/Embedded/Referenced), Custom Client Properties (key=value lines; custom truststore path via `ssl.truststore.location=...`).
- TLS/SSL: Protocol, Key Password, Keystore Type, Keystore Password, Keystore Key, Truststore Password.
- Additional: Custom Consumer Properties, Custom Producer Properties (both override Custom Client Properties on key collision).

Used via **Event Streams** (Kafka source/handler — see above) or directly via **`system.kafka`** scripting functions (poll, send records, list info). Not available on Edge.

### MongoDB Connector

Non-relational JSON-document store; Ignition's Tag system, Python scripting, and Perspective data map naturally onto documents. Bundled with Cloud Edition; add-on for standard Ignition; **not available on Edge or Maker Edition**.

**Connection settings**: General (Name, Description, Enabled); Connection (Connection Scheme — `mongodb` default, use `mongodb+srv` for Atlas; Connection Hosts comma-list, default port 27017 if unspecified; Database; Username; Password [None/Embedded/Referenced]; Connection Properties — TLS defaults **on** for `mongodb+srv`, **off** for `mongodb`; trusted certs work automatically, custom/self-signed need manual config).

Connecting to **Atlas** specifically: Database → Connect → Connect your application → driver **Java** latest → copy the `mongodb+srv://<user>:<pass>@<cluster>/?retryWrites=true&w=majority` URL and map its pieces to the Gateway fields (Connection Scheme, Connection Hosts = the cluster hostname, Username, Password, Connection Properties = the query string). Get the database name from **Deployment > Database > Browse Collections**.

Access via **`system.mongodb`** functions (read/update/delete/aggregate collections — write access is *only* here, not through the binding) or the read-only **MongoDB Perspective binding** (Find / FindOne / Aggregate query types).

---

## Web Dev module

Lets you host static or dynamic web content and REST APIs directly from the Ignition Gateway's web server, using Python + static resources. Requires specialized web-programming knowledge; Inductive Automation support is limited to basic module functionality, not site-building advice.

### Resource types (right-click "Web Dev" in Designer's Project Browser)

- **Python Resource** — dynamic; the script re-runs on every request. Stored as `.json`/`.py` on the Gateway filesystem.
- **File Resource** — static binary (e.g. image); must be **re-imported** if the source file changes.
- **Text Resource** — static, directly editable in the Designer (HTML/CSS/JS).
- **Mounted Folder** — exposes a Gateway filesystem folder as an endpoint tree, e.g. folder `assets` → `/opt/public/` makes `/opt/public/a.jpg` reachable at `.../assets/a.jpg`. Filenames need URL-encoding for special characters; avoid `'`, `,`, `/`, `?`, `#`, `%`, `&` in filenames inside mounted folders. A Mounted Folder placed inside a Project Browser folder adds that folder name to the URL path too.

### Python resource HTTP methods

`doGet`, `doPost`, `doPut`, `doDelete`, `doHead`, `doOptions`, `doTrace`, `doPatch` — most resources implement just `doGet`/`doPost`.

### Return value dict keys (evaluated in this priority order; `contentType` can override any of them)

| Key | Behavior |
|---|---|
| `html` | String → `text/html`. |
| `json` | String (valid JSON) or Python object (auto-encoded) → `application/json`. |
| `file` | Path to a server-filesystem file; content type auto-probed via `java.nio.Files.probeContentType` if not set; missing file → HTTP 404. |
| `bytes` | Byte array → `application/octet-stream` unless overridden. |
| `response` | Fallback: stringified → `text/plain`. |
| `contentType` | Mime override, combinable with any key above. |

Returning a dict with none of these keys → HTTP 500. Returning `None` → no auto-response (assumes you used `request['servletResponse']` directly). Default encoding for html/json/response is UTF-8.

### `request` object

| Key | Type | Description |
|---|---|---|
| `context` | object | Gateway `GatewayContext` reference (SDK). |
| `data` | dict/text/bytes | Parsed JSON dict if `Content-Type: application/json`, else text or raw bytes. |
| `postData` | dict/string | `doPost` only — parsed JSON dict, or raw text if `Content-Type` starts with `text/`. |
| `headers` | dict | Header→value(s); repeated headers become a tuple. |
| `params` | dict | URL query params, e.g. `?param1=value` → `{'param1':'value'}`. |
| `remainingPath` | string/None | Path segment after the resource name (`.../foo/bar` on resource `foo` → `/bar`). |
| `remoteAddr` / `remoteHost` | string | Client IP / fully-qualified hostname (from the web server's perspective — NAT can distort this). |
| `scheme` | string | `http` or `https`. |
| `servletRequest` / `servletResponse` | object | Underlying Java `HttpServletRequest`/`HttpServletResponse` for low-level control. |

### `session` object

A per-client Python dict (requires cookies) persisting across calls to the same or different Python Resources within the project — any serializable Python type. If Require Authentication is on, gets a `user` attribute (authenticated user info) and `retryAttempts`.

### URL routing

Base path: `/system/webdev/<projectName>/<resourcePath>`, nested folders add path segments. Resources may include a file extension directly in the name (e.g. `my_image.png`). A request to the project root (`/system/webdev/<projectName>`, or via the shortcut `/system/<projectName>`) looks for a resource literally named **`index.html`**; missing → 404.

### Security settings (per Python resource, per HTTP method)

- **Enabled** — toggles that method.
- **Require HTTPS** — non-secure requests get redirected to the Gateway's SSL port (Gateway SSL must be enabled).
- **Require Authentication** — HTTP BASIC auth (pair with Require HTTPS so credentials aren't sent in the clear) against a chosen User Source; supports comma-separated acceptable roles (need at least one); missing creds → 401 w/ `WWW-Authenticate`; wrong creds → 403. Authenticated user object lands in `session['user']`; subsequent requests on the same cookie-backed session skip re-auth.

### Worked example — simple test server

Create a Web Dev folder (e.g. `testServer`) → New Python Resource → set method `doPost` (or `doGet`), Enabled. POST example script reads `request['data']['names']`/`['values']`, logs via `system.util.getLogger(...).infof(...)`, returns `{'html': ...}`. Client side in Perspective: `system.net.httpClient().post(url, data=system.util.jsonEncode(params), headers={"Content-Type":"application/json"})`. GET example just returns a static `{'html': ...}` string, reachable directly in a browser at `http://host:port/system/webdev/<project>/<folder>/<resource>`.

---

## JDBC drivers

Ignition bundles three JDBC drivers as their own **modules** (in addition to the built-in, module-less **SQLite** driver):

| Module | Driver version | Notes |
|---|---|---|
| **MariaDB JDBC Driver** | 3.3.3 | Type 4 driver; lightweight; **also provides the MySQL driver**. |
| **MSSQL JDBC Driver** | 9.4.0.jre11 | For SQL Server / SQL Server Express / Azure SQL. |
| **PostgreSQL JDBC Driver** | 42.7.2 | |

Packaging as modules means driver upgrades ride along with Ignition/module upgrades instead of manual jar management — but also means **removing the module removes the driver**, and a disabled/faulted module faults the driver.

- Driver JARs live under `/data/config/resources/core/ignition/database-driver` (resource-collection system).
- Once installed, drivers auto-populate **Connections > Database > Settings**, ready to connect immediately.
- **Custom configuration**: edit the driver on the Database Settings page (3-dot menu → Edit). Edits create a **core-level** definition that overrides the module's **system-level** one (as long as the driver name is unchanged) — the page will flag "drivers with multiple definitions" and offer **Show All** to see both.
- **Upgrade behavior**: choosing **Keep as-is** for a driver module during an Ignition upgrade pins that driver's version instead of taking the new bundled one.
- For anything beyond these three (Oracle, DB2, etc.), add a JDBC driver manually via **JDBC Drivers and Translators** — not covered by these bundled modules.

---

## Redundancy & failover cheat sheet

Redundancy terminology is used inconsistently across features — this table disambiguates it:

| Feature | Term | What it means |
|---|---|---|
| OPC UA server (Ignition as server) | **Read-only When Inactive Node** | The Gateway's own OPC UA server setting; server switches to read-only while its Gateway is the inactive node in a redundant Ignition pair. |
| OPC UA server (Ignition as server) | **ServiceLevel** node | Read via OPC Quick Client under **Server**: `255` = active master, `254` = active backup, `1` = inactive. Use this to script/verify which node is currently live. |
| OPC UA client connection (Ignition → 3rd-party UA server) | **Failover** properties | For a *pair of redundant 3rd-party UA servers* behind one Ignition client connection. Sticky: once switched to the Failover server, stays there until it also fails. |
| Kepware OPC UA connection specifically | **Backup** properties (Backup Discovery/Endpoint URL) | For *a pair of redundant Ignition Gateways* pointed at the **same** Kepware server — not device failover. Distinct from the generic Failover properties above. |
| BACnet local device | **Backup Device Number** | Device number the local device uses on the Ignition redundant **backup** node — must differ from the primary's device number. |
| SFC charts | Pause-on-shutdown / resume-on-startup | Charts survive a Gateway restart and support redundant Ignition setups so a chart keeps running if the primary Gateway fails. |
| DNP3 (current driver) | Buffered Events / Sequence of Events | Not Gateway redundancy — device-side event buffering via Tag Group **Queue Size**, replayed on reconnect. |

Quick decision guide: "I have two OPC UA *servers* and one Ignition client" → **Failover** properties on the OPC UA connection. "I have two Ignition *Gateways* and one Kepware server" → **Backup** properties. "I need to know which Ignition Gateway is currently active" → read **ServiceLevel** via the OPC Quick Client.

---

## Gotchas and 8.3 notes

Explicitly called out as **NEW in 8.3** on the pages read:

- **Event Streams module** — entirely new in 8.3: Source→Filter→Transform→Buffer→Handler pipeline, `system.eventstream.*`, Kafka/HTTP/Event Listener/Tag Event sources, 8 handler types.
- **Cloud Connector Modules** (Kafka, MongoDB) as a distinct module category, designed to integrate with Event Streams.
- **JDBC Driver Modules** — MariaDB/MSSQL/PostgreSQL drivers repackaged as modules (previously manual jar installs in older Ignition versions).
- **DNP3 Driver** (non-legacy) is new/current — adds event-based polling and unsolicited messaging beyond what DNP3 Legacy offered, and is the default on new installs; Legacy is explicitly deprecated with no further updates.
- **Historian Core module** (renamed/restructured "Tag Historian" concept) — pluggable API supporting Core Historian and Internal Historian (Legacy) as backends, with **SQL Historian** as an add-on option layered on top.
- **Alarm Metrics subscription behavior in Tag Event source** — introduced in **8.3.2**: Alarm Metrics values start NULL and always trigger the event stream on initialization, so `Skip Initial Value` is ignored for tag paths that include them.
- **IEC 61850 Functional Constraint (FC) addressing** — attributes with multiple FCs now browse as separate `[FC]`-suffixed OPC nodes instead of collapsing to one; an upgrade migrates NodeIds and stale unsuffixed tags report `Bad_NodeIdUnknown` until re-addressed.
- **OPC UA server diagnostics role requirement** — a **Milo 1.1.6** library upgrade (landing with **8.3.9**) now requires `ConfigureAdmin` or `SecurityAdmin` role to enable Server Diagnostics on an OPC connection; new 8.3.9+ installs auto-grant `ConfigureAdmin` to `opcuauser`, but upgrades from ≤8.3.8 must add the role manually and reconnect.
- **Siemens Enhanced Driver `Secure Connection Mode`** — replaces the old boolean **Force Secure Connection** property (auto-migrated: enabled→`REQUIRED`, disabled→`PREFERRED`); also, **8.3.3+** updated the AGLink library for S7-1200 G2 support, which raises the GLIBC requirement (≥2.34 x64 / ≥2.17 ARM) and **breaks the driver on Ubuntu 20.04 and Debian 10/11** (x64).
- **Autobackup default changed** — `localdb.autobackup.delay` (relevant to IEC 61850 buffered-report `config.idb` churn) is **now disabled by default**; previously active by default.

Explicitly called out as **REMOVED / deprecated** on the pages read:

- **DNP3 Driver (Legacy)** — "no longer actively supported with updates or fixes"; migration path is delete/rename the legacy device, create a new DNP3 Driver device reusing the old name, and re-review settings (the two drivers' configuration/polling models differ).
- **Allen-Bradley CompactLogix/ControlLogix (Legacy) drivers** — capped at firmware ≤ v20.18; the **Logix** driver is the forward path for v21+ (works on older firmware too, just "with significantly reduced performance").

Cross-cutting behavioral notes worth flagging to developers migrating in:

- The **OPC UA server's own diagnostics gating on roles** (above) is easy to miss when scripting Gateway setup — a fresh 8.3.9+ install "just works," but an in-place upgrade from 8.3.8 silently leaves Enable Server Diagnostics non-functional until a role is manually granted.
- **Event Streams' Buffer stage silently drops events** (not queues them) once `Max Queue Size` is exceeded — there's no backpressure signal to the source; size the queue and Debounce/Max Wait deliberately for bursty sources like Kafka.
- Several drivers (Modbus, Siemens absolute addressing, TCP/UDP raw) **do not support tag browsing at all** — plan for either manual OPC Item Path authoring or an Address Mapping/CSV workflow up front; this is a common integration-time surprise for teams used to Allen-Bradley/BACnet-style browsing.
