# Ignition 8.3 — Platform overview and architecture

*Distilled from the live Ignition 8.3 User Manual (docs.inductiveautomation.com/docs/8.3), covering the intro, getting-started, other-editions, scopes, and system-architectures sections. Written as an orientation reference for someone who needs to understand the system, not as marketing copy.*

## What Ignition is

Ignition is Inductive Automation's SCADA/HMI/MES platform, built around three ideas that differentiate it from traditional industrial software: unlimited licensing, a server-centric architecture, and a modular, web-deployed design.

**Unlimited licensing.** A single server license covers the Gateway and gives you unlimited Clients, Sessions, tags, projects, and Designers. There is no per-seat or per-tag pricing — you pay once for the server, and every additional client, screen, or data point is free. This is the single biggest structural difference from legacy SCADA vendors and shapes how organizations plan rollouts (scale first, ask questions never, because there is no licensing penalty for scaling).

**Server-centric ("everything talks to the Gateway").** One Ignition Gateway is the single install that controls everything: it holds the tags, the projects, the database and device connections, security, and configuration. Designers, Vision Clients, and Perspective Sessions are all just runtimes that connect to a Gateway to pull data and push changes back — none of them store their own copy of the system of record. This means there's no "merge" step between developers' local copies; everyone edits against the live Gateway (with conflict detection), and every client always sees current data.

**Module system.** Ignition's functionality is delivered as modules — Perspective, Vision, SQL Bridge, OPC UA, Alarm Notification, Reporting, SFC, and so on — that plug into the Gateway and add Designer workspaces, Gateway settings, and drivers. You license only what you need; modules can be added, removed, enabled, or disabled independently (each of those actions requires a Gateway restart to take full effect, except enabling/disabling a Perspective Session doesn't require a Designer/Vision Client restart the way installing/uninstalling a whole module does). Third parties (Sepasoft for MES, Cirrus Link for MQTT, and community authors via the Module Showcase) can build modules against the public Module SDK.

**Web-deployed clients.** Perspective Sessions run in a browser (or as a native mobile app) with zero client install. Vision Clients and the Designer are downloaded via lightweight native launchers (Designer Launcher, Vision Client Launcher, Perspective Workstation) that manage their own embedded Java runtime — you do not need Java installed anywhere, on the server or the clients. Updating a project is a single save on the Gateway; every connected runtime picks up the change without a separate deployment step.

**Cross-platform by construction.** Ignition is built on Java (bundled JRE — Java 17.0.13 as of 8.3) and runs identically on Windows, macOS, and Linux, with native builds for both x86 and ARM (including Apple Silicon as of 8.3.0). Gateway backups are cross-platform too — a backup taken on Windows restores cleanly onto Linux or macOS.

### New in Ignition 8.3, at a glance

8.3 is described in the docs as "a major update across all subsystems and modules." The headline additions:

- **Core Historian** — a new time-series storage engine powered by QuestDB, sitting alongside (not replacing) the Internal Historian (Legacy). Auto-partitions data by table on a configurable interval, and skips the Store and Forward queue entirely when there are no pending writes (rather than always routing through it).
- **Secrets Management** — a first-class system for encrypting credentials, API tokens, and private keys, with pluggable Secret Providers and a dedicated command-line tool for key management and scripted operations.
- **Event Streams** — a new project-resource type (its own module) for staged, subscription-driven data pipelines (Source → Encoder → Filter → Transform → Buffer → Handler → Error Handler), aimed at systems like Kafka that push data rather than waiting to be polled.
- **Deep Links and File Associations** — launch a Designer/Vision Client/Perspective Workstation project directly from a URL (`perspective://host:port/ProjectName`) or a double-clicked file (`.designer`, `.vision`, `.perspective`), skipping the launcher's own UI entirely.
- **Rewritten Store and Forward engine** — multi-threaded (separate lanes per data type), Protobuf-based instead of Java-serialization-based, JSON quarantine exports.
- **Perspective Drawing component** — freehand/vector drawing plus SVG/GIF/JPEG/PNG import, closing a long-standing gap with Vision's drawing tools.
- **Perspective Form component** — a purpose-built data-entry component with dynamic field visibility and validation rules.
- **Gateway Deployment Modes** — named, swappable bundles of Gateway resource/property overrides, switched via the Gateway configuration file, letting one Gateway represent multiple named runtime configurations.
- **`system.vision` and `system.historian` scripting namespaces** — consolidating and replacing older, scattered `system.file`/`system.gui`/`system.nav`/`system.net`/`system.print`/`system.security`/`system.util` functions and the old `system.tag.*History*` functions, respectively.
- **Scripting autocomplete improvements** — hints now surface system library constants and flag deprecated functions inline.
- New **Siemens Enhanced**, **Event Streams**, **Kafka Connector**, **MariaDB/MSSQL/PostgreSQL JDBC Driver**, and **SQL Historian** modules ship as part of the base 8.3 module catalog.
- **Reporting** gained a new **Radar Chart** component, and Barcode/Bar/Pie/Radar/Timeseries/XY chart components can now render as either raster or vector images.
- A new **ModuleVersions** System Tags folder helps EAM Controllers monitor module versions across connected Agents at a glance.
- The deprecated `forceQuality` expression function is replaced by `qualifiedValue`; the Designer's Perspective-specific Identity Provider project property is deprecated in favor of the general Project Properties > Project > General Identity Provider setting; and the Perspective Table's `pager.initialOption` property is replaced by `option` (which, unlike its predecessor, honors external writes after the table has already loaded).

### Where to go deeper

The manual itself points to four places once this overview isn't enough: the **Appendix** (exhaustive references for every Component, Expression function, and Scripting function), **New in this Version** (a running changelog per release, including 8.3.x point releases beyond what's captured here), the **Ignition Module SDK docs** (for building custom modules — third-party module development is explicitly scoped to Standard Ignition; other editions require contacting Inductive Automation directly), and **Inductive University** (inductiveuniversity.com — free video training plus a certification/credential program). Security-specific channels also exist separately: a **Trust Center** for vulnerability/security news subscriptions, and a dedicated `security@inductiveautomation.com` address (with a published PGP key) for reporting vulnerabilities.

## Core concepts and vocabulary

**Gateway.** The single server install and the source of truth for the whole system. It hosts the Gateway Webpage (browser-based admin UI, default ports 8088 HTTP / 8043 HTTPS / 8060 Gateway Network), stores projects, tags, device and database connections, security configuration, and runs Gateway-scoped scripts. Everything else in an Ignition deployment — Designers, Clients, Sessions, other Gateways — talks to a Gateway rather than to each other directly.

**Designer.** The engineering/development application where projects are built: dragging components onto views/windows, writing scripts, configuring tags, building reports and alarm pipelines. Multiple Designers can connect to the same Gateway concurrently; Ignition uses a lock-free conflict-detection model (not exclusive locks) so several people can edit a project at once, with the system flagging conflicts at save time rather than blocking edits up front.

**Client / Session.** A "Client" is a Vision runtime (a full Java desktop application); a "Session" is the equivalent concept in Perspective (a browser tab or native-app instance). Both are unlimited under the base license and both talk directly to the Gateway for live data — there's no client-side data cache that can drift out of sync.

**Project.** A named container of resources (views/windows, tags references, scripts, alarm pipelines, reports) on a Gateway. Projects support inheritance: a project can have a parent project and inherit (and optionally override) its resources, letting you build shared template hierarchies. Any project can launch as a Vision Client, a Perspective Session, or both, depending on which visualization module(s) are used.

**Tag.** The fundamental unit of live or historical data in Ignition — an addressable named value with a type, a quality, and a timestamp. Tags can be OPC tags (backed by a live device connection), Memory tags (server-side values you define), expression tags, or derived/UDT-instance tags. Tags are the binding target for almost everything a component displays.

**Tag provider.** A named namespace/source that holds a set of tags — the default local Realtime Tag Provider, a Remote Tag Provider (pointing at another Gateway's tags over the Gateway Network), or a Historical Provider (for queryable tag history). A Gateway can host multiple tag providers; Ignition Edge is restricted to a single active Realtime Tag Provider.

**Module.** A pluggable unit of Ignition functionality (see "module system" above) — installed, licensed, enabled/disabled, and versioned independently on the Gateway's Modules page (**Platform > System > Modules**). A module's middle version digit must match the platform's middle version digit or it will show as **Faulted**.

**Scope.** The runtime context a piece of scripting/logic executes in — Gateway, Designer, Vision Client, or Perspective Session — each exposing a different subset of the `system.*` scripting API (see "Execution scopes" below). Choosing the right scope for a script determines what it can access and where the load falls.

**Device connection.** A live link from the Gateway (via the OPC UA module) to a PLC or other industrial device — Allen-Bradley, Siemens, Modbus, BACnet, DNP3, Omron, Mitsubishi, IEC 61850, or generic UDP/TCP — that populates OPC tags with live values.

**OPC UA server/client.** Ignition ships a built-in OPC UA server (so any OPC UA client can browse/subscribe to Ignition's tags) and an OPC UA client (so Ignition can connect outbound to third-party OPC UA servers). This dual role makes Ignition function as a general OPC UA hub, not just a consumer.

**Historian.** The subsystem that records tag values over time for later querying/charting. 8.3 introduces the **Core Historian** (powered by QuestDB, auto-partitioning, high-performance time-series storage) alongside the pre-existing **Internal Historian (Legacy)** (SQLite-based) and the **SQL Historian** (stores history into any SQL database you connect). The Historian Core module provides the pluggable API all of these implement.

**Store and forward.** The buffering system that sits in front of historian, alarm, audit, and transaction-group writes so that a lost database/network connection doesn't lose data — values queue locally and flush once connectivity returns. In 8.3 the engine was rewritten to be multi-threaded (separate queues for Alarming, Auditing, Scripting, SECS/GEM, Tag history, and Transaction Group data) and switched its wire format from Java serialization to Google Protobuf. The **Primary Store Maintenance Value** (formerly "Max Records" in 8.1) now defaults to zero, meaning the local disk cache holds an unlimited number of pending points rather than capping and dropping.

### Module catalog

Modules are how Ignition's feature set is assembled. The manual groups them into three families:

**Core modules** (the modules most installations run at least one of):
- **Perspective** — mobile-responsive, HTML5/CSS3 web visualization; runs as Sessions in any browser or as a native iOS/Android app; themable via CSS, touch-first, supports Offline Mode.
- **Vision** — the original Java-based desktop HMI/SCADA visualization system; unlimited Clients per server; drag-and-drop Designer, vector 2D drawing tools, a ~4,000-symbol Symbol Factory library, template-based rapid development, Python scripting.
- **SQL Bridge** — bidirectional OPC-to-SQL "transaction group" engine: logs data, synchronizes PLC state with database rows, and can drive recipe/batching systems and process sequencing. A **SQL Bridge Limited** tier exists for basic historical logging at lower cost.
- **Historian Core** — the tag-history engine; one-click history enablement, automatic table management (schema, indexing, partitioning, retirement), pluggable storage backends (Core Historian, Internal Historian Legacy).
- **SQL Historian** — an add-on to Historian Core that stores tag history in any connected SQL database instead of (or alongside) the Core/Internal historians — best for shops that need long-term storage integrated with existing reporting/BI tools.
- **Reporting** — drag-and-drop PDF/HTML/CSV/RTF report design, pulling from SQL, Tag Historian, and the alarm journal; supports scheduled (cron-like) or event-triggered execution and automatic delivery (print, email, file server, FTP, or scripted). A **Reporting Limited** tier exists for a handful of scheduled reports.
- **OPC UA** — turns the Gateway into a cross-platform OPC UA server *and* client simultaneously, with a pluggable driver API and Ignition Redundancy integration built in with no extra config.
- **Alarm Notification** — configurable alarm-notification pipelines (Delay, Escalation, Consolidation, Selection blocks) built visually, On-Call Rosters with per-user schedules, two-way email acknowledgment.
- **Event Streams** *(new in 8.3)* — project resources that pull data from a source, run it through optional filter/transform stages, batch it in a buffer, and hand it to one or more handlers, with a final error-handler catch-all stage. Built for subscription/event-driven data (e.g. Kafka) rather than polled SQL.
- **SMS Notification** — text-message alarm notification/acknowledgment; requires the Alarm Notification module plus a cellular modem.
- **Sequential Function Charts (SFC)** — IEC 61131-3-style visual logic programming (Steps, Directed Links, Transitions, Parallel Branches/Syncs, Jumps); charts can run for very long periods, survive a Gateway restart (pause on shutdown, resume on startup), support multiple independent instances, and work under Ignition Redundancy.
- **Web Dev** — lets you hand-build and host web pages/REST endpoints directly against the Gateway's built-in web server using Python plus static assets (HTML/CSS/JS/images) — used both for custom UI and for exposing APIs to external systems like ERP/SAP.
- **Enterprise Administration Module (EAM)** — designates a Controller Gateway that can push module/license changes, coordinate backups/disaster recovery, and monitor health across any number of Agent Gateways over the Gateway Network.
- **JDBC Driver modules** — MariaDB (3.3.3), MSSQL (9.4.0.jre11), and PostgreSQL (42.7.2) drivers ship as their own installable modules in 8.3 (previously bundled differently), auto-registering connection configs once installed.

**Additional modules** (more specialized, opt-in add-ons):
- **Voice Notification** — text-to-speech phone-call alarm notification over SIP/VoIP, with two-way key-press acknowledgment and audit-log integration; requires Alarm Notification plus a SIP-compatible VoIP service.
- **OPC COM** — bridges to legacy ("classic") COM-based OPC DA 2.0/3.0 servers, mainly for local Windows connections (subject to DCOM security quirks and requiring the OPC Foundation's OPC Core Components package).
- **OPC COM Tunneller** — exposes an OPC COM connection to Ignition's OPC UA server over TCP (with encryption/auth), avoiding Remote DCOM for accessing a remote classic OPC server; requires OPC COM to also be installed.
- **Twilio Notification** — SMS, Voice, and WhatsApp alarm notification/acknowledgment via Twilio's cloud API (`system.twilio` scripting functions); no physical hardware/modem required, but needs Alarm Notification installed.
- **SECS/GEM** — host-side SECS-II/GEM/HSMS communication with semiconductor fab equipment, over Ethernet (HSMS) or serial (SECS-I); includes equipment simulators for testing, and scripting to start/stop processing, set parameters, collect data, and select recipes.

**Connector modules** (a.k.a. "Cloud Connectors" — bundled free with Cloud Edition, available as a paid add-on for Standard, and **not available on Edge**):
- **MongoDB Connector** — connects Ignition to a MongoDB NoSQL deployment; `system.mongodb` scripting functions for insert/update/delete/query, plus a native Perspective **MongoDB binding type** (Find / FindOne / Aggregate) for pulling document data straight into components.
- **Kafka Connector** — produces/consumes Kafka topic records (`system.kafka` functions), typically paired with the Event Streams module for filtering/transforming streamed data as it moves in or out of Kafka.

## Driver modules (OPC UA device connectivity)

The OPC UA module's device drivers are themselves installed as modules. As of 8.3, the built-in driver catalog covers:

- **Allen-Bradley**: a legacy **Allen-Bradley driver** (CompactLogix/ControlLogix firmware v20 and earlier, MicroLogix 1100/1200/1400/1500, PLC5 and SLC 5/05 over Ethernet), a **Logix driver** (Logix-series with firmware v21+), and a **Micro800 driver** (Micro820/850/870).
- **Siemens**: legacy **S7-300/400/1200/1500 drivers** (absolute addressing only via TCP/IP), plus a new 8.3 **Siemens Enhanced driver** (absolute addressing on S7-300/400, absolute *or* symbolic tag access on S7-1200/1500).
- **Modbus**: Modbus TCP or Modbus RTU-over-TCP, direct or through a gateway device.
- **BACnet**: BACnet/IP.
- **DNP3**: a current **DNP3 driver** (event-based polling, unsolicited messaging, explicit reads) and a deprecated **Legacy DNP3 driver** (unsolicited messaging and explicit reads only, no longer supported).
- **IEC 61850**: MMS-protocol communication, built on the Triangle Microworks library, Windows/Linux x64 only.
- **Mitsubishi**: MELSEC protocol over TCP.
- **Omron**: an **Omron NJ driver** (FINS-based) and a separate **Omron FINS driver**.
- **Generic protocols**: a **UDP driver** (passively listens on configured ports) and a **TCP driver** (actively connects and can write back), both with configurable parsing of raw incoming data.

## Administration, security, and licensing

A handful of Gateway-level concepts recur across almost every other topic in the manual and are worth understanding on their own:

**Identity Providers vs. User Sources.** User Sources (Internal, Active Directory, Database, Hybrid) are the underlying pool of user records; an **Identity Provider** is what actually authenticates a login against one (or, via SAML/OpenID Connect, against an external IdP) and is what a project or the Gateway itself is configured to use. Ignition can also *act as* an Identity Provider for other systems. On any 7.9/8.0→8.1 upgrade, a new Ignition Identity Provider is auto-created pointing at the existing System User Source so login keeps working without manual setup — but it depends on that User Source being able to enumerate its full user list (Active Directory search/filter settings, Hybrid's "List Users from Active Directory" toggle, or a Database User Source's "List Users Query" all need to actually return every expected user, or some accounts silently can't log in post-upgrade).

**Security Zones and Security Levels.** Security Zones classify *where a connection is coming from* (network/IP-based) and drive per-zone policy — including, as of 8.3, **service security** settings (query/storage access for remote history, audit, and Alarm Journal requests), configured via each zone's "Manage Policy" action. Security Levels (introduced in Ignition 8) are abstract access tiers assignable by role, zone, or an expression combining both, used to gate access to parts of a project independent of the coarser page/role permission system.

**Gateway-page role gating (new emphasis in 8.3).** Gateway webpages now operate on a required-role basis by default — unauthenticated or under-permissioned users are blocked from pages/actions rather than merely hidden from a menu. Permission grants do not automatically carry forward across a major-version upgrade (8.1 → 8.3 specifically) and must be reassigned.

**Gateway Deployment Modes** *(new in 8.3)* let one Gateway hold multiple named configurations of its own resources/properties, switched through the Gateway Configuration File; they inherit the same role-based access rules as everything else, and can also be hand-edited on the filesystem (with changes only picked up on the next file-system scan).

**Secrets Management** *(new in 8.3)* encrypts credentials, API tokens, and private keys via pluggable Secret Providers, with a dedicated command-line key-management tool for scripted/headless key operations — replacing ad hoc plaintext credential storage in scripts or database-connection configs.

**Licensing mechanics.** One server license activates the Gateway and, by extension, every module you've purchased — module licensing itself is centralized on **Platform > System > Licensing**, independent from the Modules page's install/enable status (a module can be installed-but-unlicensed, showing partial functionality or a trial state). 8.3 added support for managing **leased licenses** (8-character license keys) from an EAM Controller, including last-renewal timestamp/result and remote activate/update/unactivate tasks. Reduced-cost tiers exist for several modules when full functionality isn't needed: **Vision Limited** (fewer concurrent Clients), **SQL Bridge Limited** (historical logging only, no full transaction groups), **Reporting Limited** (a handful of scheduled reports), and a cheaper **Backup-specific** license for a dedicated redundant-pair backup machine.

**Designer concurrency.** Multiple Designers can connect to the same Gateway and edit the same project at once — Ignition uses lock-free conflict detection rather than exclusive checkout locks, notifying you if someone else is editing the same resource and only surfacing an actual conflict (with a resolve/keep-mine/take-theirs choice) at save time if both of you changed the same thing.

**Redundancy mechanics.** A redundant pair has a **Master** and a **Backup** node, linked via a Gateway Network connection (not a separate proprietary channel, as of Ignition 8) configured from the Backup side toward the Master. **Recovery Mode** (Automatic vs. Manual) controls whether the Master resumes control automatically once it's back online after a failover, or waits for an administrator to explicitly hit **Assume Control** — Manual is the recommended setting while performing a controlled upgrade of a redundant pair specifically so the newly-upgraded Master doesn't yank control back before you're ready.

**Gateway backups** (`.gwbk` files) are the standard unit of full-system portability — they capture projects, tags, and Gateway configuration as a structured zip, can be restored during installation (skipping first-run commissioning) or later via the Gateway webpage or `gwcmd --restore`, and — critically for upgrades — restoring a backup (like running the installer) triggers an automatic resource-upgrade check that plain project/tag *imports* do not, so backups are the recommended vehicle for moving resources across major versions rather than hand-importing individual projects.

## Execution scopes

Ignition scripting is scoped — the same `system.*` API surface is not identical everywhere a script can run. The docs publish an exact function count per scope (an auto-generated index of every `system.*` function available there), which is a useful proxy for "how much can this context actually do":

| Scope | Function count | What runs there |
|---|---|---|
| **Gateway** | 367 | Server-side scripts (Gateway Event Scripts, Tag Event Scripts, scheduled/startup/shutdown scripts) execute directly on the Gateway process. This is the only scope with device/driver management (`system.device.*`), datasource administration (`system.db.addDatasource`/`removeDatasource`/etc.), EAM functions (`system.eam.*`), and protocol-specific functions like `system.bacnet.*` and `system.dnp3.*`. It's the largest surface because it includes every server-only administrative capability. |
| **Vision Client** | 356 | Scripts running inside a Vision Client (a Java desktop runtime). Second largest — Vision, being the older native-client technology, retains legacy client-side capabilities (direct window/component manipulation, `system.gui.*`-era functions) that don't apply to a browser-hosted session. |
| **Perspective Session** | 332 | Scripts running inside a user's Perspective Session (browser or native app). Smallest of the three documented scopes: it omits Gateway-only administrative functions but adds Perspective-specific session functions (`system.perspective.*`) for browser/session interaction, navigation, popups, and messaging that have no Vision equivalent. |
| **Designer** | *(not separately enumerated in this section of the docs)* | The Designer itself is effectively a superset development-time context, since it can preview/test Gateway, Vision, and Perspective scripts, but the manual's per-scope function-count pages only publish Gateway, Vision Client, and Perspective Session as the three scoped runtime targets. |

The practical takeaway: **put administrative/device logic in Gateway scope**, **put UI-interaction logic in the client scope that owns the UI (Vision vs. Perspective)**, and don't assume a function available in one scope exists in another — the docs' own scope-by-scope function lists are the authoritative way to check.

## Perspective vs Vision

Ignition ships two separate, first-class visualization modules, and 8.3's own guidance ("Perspective and Vision — Which Visualization System is Best for Me?") is direct about when to use each rather than treating one as legacy.

**Recommendation for new projects:** the docs recommend Perspective for "almost all new projects." Both support 2FA and federated identity security, so security posture doesn't favor either.

**When to use Perspective:**
- The application needs to run on iOS/Android or in a web browser on desktop.
- Mobile responsiveness matters — Perspective containers auto-adapt to any screen size/orientation.
- You want device-sensor access (camera for photo/QR capture, GPS tagging) or touch-first interaction.
- You need Perspective Workstation's Kiosk full-screen mode for a distraction-free operator UI.
- You want built-in **Offline Mode** (new capability, not exclusive to 8.3 but expanded): a Session keeps working with cached data if it loses the network, then syncs once reconnected (realtime tag/alarm/query values, Gateway/database event scripts, and not-yet-loaded views are unavailable while offline).

**When to use Vision:**
- The application needs OS-level resources: file access, serial port access, or custom Java code running in the client.
- It's a traditional plant-floor/desktop screen or standalone HMI.
- You're maintaining an established Vision codebase — Vision got a major refresh in Ignition 8 and remains fully supported, not deprecated.

**Mixing both:** nothing stops a single Gateway from running both Vision and Perspective projects simultaneously; they're just two modules on the same server, sharing the same tags/database/device connections underneath. Ignition Edge Panel is the one place this is *not* possible — Edge Panel runs one visualization module at a time (Vision *or* Perspective), switchable in settings but never concurrent.

**What Perspective still can't do (per the docs' own framing):** anything requiring direct OS resource access, file-system access, serial ports, or custom Java code embedded in the client — that remains Vision's territory. Practically, a "Client" in Vision terms is a "Session" in Perspective terms; the tech stacks are parallel (OS → Java runtime/VM for Vision, OS → web browser for Perspective → the module itself on top), and Perspective is architecturally "just another module," installed into the Gateway exactly like any other.

**Behind the scenes, the stacks mirror each other layer for layer.** At the Gateway: OS → Java runtime/VM → the Ignition platform (tags, projects, database connections, Gateway Network) → modules on top (device drivers, alarm notification, reporting, and — for Vision specifically — the module that lets it run Vision Clients). On the client side: for Vision, OS → Java runtime/VM (the client's own execution environment) → the Vision Client application; for Perspective, OS → web browser (playing the same "execution environment" role a runtime/VM plays for Vision) → the Perspective Session application, with additional OSes available (Android and iOS) that Vision's Java-based runtime cannot target at all. In early Ignition 8 benchmark testing, a single Gateway simultaneously and easily launched 200 Perspective Sessions.

## System architectures

Ignition documents a defined set of reference architectures. All are described as starting points meant to be combined and scaled, not rigid prescriptions.

### Basic Architecture
A single Gateway connects to multiple PLCs, databases, and clients under one license. Supports dual-NIC deployment so one Gateway can bridge a corporate network and an isolated control network, with security settings restricting project/asset access by network location and role. This is the default starting point for almost every other architecture on this list.

### Scale-Out Architecture
Splits a single large system into a **back-end Gateway** (owns PLC/device communication, executes tags, records history, shares tags out via a Remote Tag Provider) and one or more **front-end Gateways** (host the Clients/Sessions, query data from the back-end). Connected via the Gateway Network. Choose this over Hub and Spoke when you have one large system, not multiple distinct sites. A Load Balancer (e.g. nginx, HAProxy — not AWS's own load balancer, which lacks sticky-session support on AWS Outposts) can front multiple front-end Gateways as client count grows; sticky sessions are required.

### Hub and Spoke Architecture
Multiple independent Ignition installations (spokes) forward data to a centralized installation (the hub) via the Gateway Network. Good fit for geographically distributed sites that each need local autonomy. Reliable remote logging uses SQL Bridge or Historian Core plus Store and Forward so unreliable WAN links don't lose data; data can also be queried live via the built-in OPC UA server or database-backed tags rather than only historized. A variant splits tag history so each spoke stores locally *as well as* at the hub — redundant copies protect against a single drive failure at either end. Adding the Vision module at each spoke enables **local Client fallback** — sites keep running at full efficiency (never losing visibility) if the hub connection drops; a **Vision Limited** license helps keep spoke costs down. It's generally better to configure Alarm Notification *at each spoke* rather than centrally, so a lost hub connection doesn't also silence local alarming. **8.3 caution:** an 8.3 hub cannot store data (remote history, audit, Alarm Journal, Edge Sync Services) to a remote 8.1 spoke — upgrade the hub to 8.3 first.

### Enterprise Architecture
Adds the Enterprise Administration Module (EAM) on top of any multi-Gateway architecture: one Gateway is designated the EAM Controller, others are Agents, connected via the Gateway Network. Centralizes monitoring/alarming on Agent health, and lets the Controller push synchronized projects/resources out to Agents (useful anywhere multiple Gateways need a consistent look-and-feel, e.g. atop a Hub-and-Spoke deployment).

### Redundancy Architecture
Any single Gateway in any of these architectures can be replaced with a redundant pair — if the primary (Master) fails, the Backup takes over, clients redirect, and history keeps logging, with roughly a 20-second failover (vs. multi-minute cold-start failover typical of cloud-provider-level redundancy). A dedicated backup machine can use a cheaper Backup-specific license. In Scale-Out with a load balancer, redundancy is *not* applied to front-end Gateways (the load balancer handles that); instead add an extra front-end as failover capacity.

### Cloud Based Architecture
Ignition itself can be hosted on any general-purpose cloud VM (AWS EC2, Azure, etc. — Inductive Automation doesn't host it for you outside of Cloud Edition). Typical pattern: Ignition and the database run on *separate* cloud services (compute vs. managed-DB offerings), with an Ignition Edge instance placed local to the PLCs to forward data to the cloud server. Good fit for smaller orgs that don't want to run their own server/IT staff. If using redundancy in the cloud, both nodes should be co-located (both cloud or both on-prem) — otherwise an internet outage can take out both at once.

### Edge Architectures
Ignition Edge (Panel and/or IIoT) plugs into any of the above architectures as a local presence: Edge Panel as a standalone screen or as local-Client-fallback paired with a central Gateway; Edge IIoT as a standalone MQTT publisher or combined with Edge Panel for a local client plus MQTT publishing. Both Edge products sync tag history/Alarm Journal/audit data to a central Gateway over the Gateway Network with Store-and-Forward buffering, and can run as EAM agents.

### IIoT Architecture
Basic Architecture extended with MQTT: field devices (Ignition Edge MQTT, an Ignition server with MQTT Transmission, or a third-party Sparkplug-compliant device) publish to an MQTT broker (Ignition Gateway with MQTT Distributor, or a third-party broker), and a subscriber Gateway (MQTT Engine module) consumes that data for use anywhere in Ignition — historized via Vision or reported via Reporting.

### AWS Outposts Architecture
Runs the Basic/Scale-Out/Redundancy patterns on AWS-managed on-prem hardware (Outposts) for low-latency access to local systems plus native AWS APIs (VPC, EC2, EBS, RDS — RDS limited to MySQL/PostgreSQL on Outposts). Notably: AWS's own Load Balancer doesn't support sticky sessions on Outposts, so HA front-ends there require nginx/HAProxy instead.

Documented variants: **Standard** (single on-prem server + RDS + PLCs/clients), **Standard with Redundancy**, **Scale-Out**, **Scale-Out with Redundancy**, and an **AWS Connected Factory** pattern (Cirrus Link MQTT modules + Sparkplug SiteWise Bridge auto-discovering assets/properties/hierarchy and streaming tag data into AWS IoT SiteWise with no coding, only configuration). Typical deployment path: create a VPC with public/private subnets, add a NAT Gateway if instances need outbound internet, spin up an EC2 instance (Windows Server 2019 Base or Ubuntu Server 20.04 LTS recommended; minimum 4 vCPUs / 8 GiB memory — real deployments commonly use m5/c5/r5 `.xlarge`/`.2xlarge` instance types with EBS-backed storage), restrict security groups to ports 22/8088/8043/3306-or-5432, provision a MySQL/PostgreSQL RDS instance (self-managed EC2 database is possible but RDS is recommended), then install and connect Ignition. Inductive Automation's Sales Engineering team carries AWS Solution Architect Associate certification and is available to help architect Outposts deployments.

### Security Architecture
A cross-cutting overlay, not a standalone topology: consumers of each traffic class should only talk to Ignition Gateways, never to each other directly (users ↔ Ignition, Ignition ↔ PLCs, Ignition ↔ databases, Gateway ↔ Gateway). Recommends ISA 62443 zones-and-conduits / Zero Trust / NIST or ISO segmentation, HTTPS with 2-way certificate trust over the Gateway Network (port 8060, configurable), and separating "stateless" front-end Gateways (Perspective/Vision/Reporting, scale via load balancer) from "stateful" I/O Gateways (tag systems, PLC/DB connections, historians — scale by adding distinct-content Gateways, protect with Ignition redundancy, keep off direct end-user/internet access).

## Editions

| Edition | Positioning | Key limits / licensing |
|---|---|---|
| **Standard** | The full commercial platform. | Unlimited tags, Clients/Sessions, database connections; one server license; choose your own module set. |
| **Ignition Edge** | Lightweight edition for field devices/OEM hardware at the network edge (Linux/Windows/macOS, ARM-compatible — e.g. Raspberry Pi). Two product tiers: **Edge IIoT** (MQTT publishing + OPC UA server exposure) and **Edge Panel** (adds local visualization: Vision *or* Perspective, one at a time). | Unlimited tags but only **two** Clients/Sessions (one local + one remote on Edge Panel); **no database connectivity** (queries/bindings needing a DB fail); single Realtime Tag Provider and single Historian Provider (Internal Historian Legacy only); 35 days/10M points local tag history, 7 days local Alarm Journal/audit; single project (can't be removed, can be renamed); third-party modules only run if explicitly Edge-compatible; can sync history/alarms/audit to a central Gateway and act as an EAM agent. |
| **Ignition Maker Edition** | Free, community edition for personal, non-commercial home-automation projects (not for classrooms/commercial use — IA has separate options for those). | Free license via IA account; max 10 Perspective Sessions; no Perspective Workstation; max 10,000 tags; redundancy limited to Independent mode; only a defined allow-list of modules run (Perspective, Vision-adjacent drivers like Allen-Bradley/Modbus/Omron/Siemens, Historian, SQL Bridge/Historian, Alarm Notification, Event Streams, Kafka Connector, Reporting, SFC, Web Dev, Twilio, serial support, UDP/TCP driver, OPC UA) — others are stripped during commissioning. |
| **Ignition Cloud Edition** | Cloud-marketplace-distributed edition (AWS Marketplace image or AWS EKS container product; also an Azure image) — prominent, purpose-built product in 8.3, not just "Ignition on a VM." | Licensed automatically by running in a paid marketplace image/container (no manual license key) — EKS container billed hourly by base rate + CPU cores + heap memory GB. No industrial device drivers (architecturally, cloud shouldn't talk directly to PLCs) — device data arrives via MQTT (bundled Cirrus Link MQTT Distributor/Engine/Transmission modules) instead. Fixed module bundle (can't cherry-pick modules like Standard) that notably **excludes Vision** (Perspective is the intended visualization layer) but includes Perspective, OPC UA (server/client, no device drivers), SQL Bridge, SQL/Core Historian, EAM, Event Streams, Kafka Connector, MongoDB Connector, Reporting, SFC, Symbol Factory, Twilio, Web Dev, Alarm Notification. Redundancy only fails over to another Cloud Edition Gateway (recommended across separate Availability Zones). Default web ports differ from on-prem Ignition: **80/443** instead of 8088/8043 (Gateway Network still uses 8060). Distinct blue-branded Gateway UI. AWS also offers pre-built "Partner Solution" reference deployments (Standalone and Cluster). |

### Cloud Edition: how it's actually deployed

Because Cloud Edition is prominent in 8.3, it's worth knowing the deployment mechanics beyond just "it's licensed automatically":

- **AWS path**: launch the official Cloud Edition AMI from the AWS Marketplace (or via the EC2 service directly), which boots a headless Ubuntu instance. Prerequisites before first boot: correct VPC/Subnet, **Auto-assign public IP** enabled, and a security group with an inbound **HTTP** rule opening port **80** (the default unencrypted Gateway access port — not 8088). First access is `http://<public-ipv4>:80`, which walks you through the same admin-user commissioning as any other edition. AWS also publishes ready-made **Partner Solution** reference deployments (Standalone and Cluster) with security, Gateway connections, and DB connectivity pre-wired.
- **Azure path**: mirrors AWS conceptually — launch the official Cloud Edition image from the Azure Marketplace into a new or existing Virtual Network, with a Network Security Group and a Public IP configured, then commission over HTTP/80 the same way.
- **Networking building blocks** you're responsible for either way: a VPC/VNet, a subnet, IP addressing, route tables, and (AWS) an Internet Gateway or (Azure) equivalent public-IP routing — plus opening the Gateway Network port (**8060**, custom TCP) if you intend to link this Cloud Edition Gateway to others.
- **Upgrading a running Cloud Edition instance** is done by SSHing into the underlying Ubuntu OS (EC2 Instance Connect in-browser on AWS, or a third-party SSH client like PuTTY on Azure with the platform's default `ubuntu`/`azureuser` account), `wget`-ing the latest **Cloud** Linux installer from the Downloads page, `chmod 700`-ing it, and running it interactively — the installer detects the existing `/usr/local/bin/ignition` install and offers to upgrade in place, including per-module upgrade prompts.
- **Container option**: besides the VM image, Cloud Edition ships as an EKS-deployable container product, billed hourly on a base rate plus detected CPU cores plus heap memory (GB) — CPU/memory limits come from the container's own resource limits, visible on its Diagnostics Overview page. Restoring a Gateway backup into a Cloud Edition container always runs it *as* Cloud Edition, regardless of what edition the backup itself came from.
- **A quiet trap on Ubuntu 24.04+**: `unattended-upgrades` plus `needrestart` will auto-restart the Ignition service whenever a related OS package is patched, unless you add an explicit exception in `/etc/needrestart/needrestart.conf` (`qr(^ignition\.service$) => 0` under `$nrconf{override_rc}`).

## Startup path for a new developer

Condensed from the 8.3 Startup Guide (Downloading and Installing Ignition → Designing a Project), as an ordered checklist:

1. **Check system requirements** — dual-core CPU (32/64-bit), 4 GB RAM, 10 GB free disk, admin privileges to run the installer.
2. **Download and run the installer** for your OS from the Downloads page. Choose **Typical** install (a curated set of common modules) unless you specifically need **Custom** module selection — you can always add/remove modules later without reinstalling.
3. **Pick an edition at commissioning**: Standard (unlimited, commercial), Edge (lightweight/field), or Maker (free, personal/non-commercial). This choice happens during first-run commissioning, not at download time.
4. **Complete Gateway commissioning**: set the Gateway Network / HTTP / HTTPS ports (defaults 8060 / 8088 / 8043 — clean installs auto-increment if a default is taken; upgrades do not, and will fault instead), create the first admin user (this is the *only* full-privilege account created for you — remember the credentials or you'll need a `gwcmd` password reset), and for Maker Edition supply the License Key + Activation Token from your IA account.
5. **Decide on Quick Start**: opting in (only available on a brand-new commissioning, not later) auto-creates an internal SQLite database connection, a Programmable Device Simulator with tags already imported, an internal Alarm Journal, and a sample project — the fastest path to a working demo environment. This is a one-time choice; you can't turn it on retroactively without restoring a Quick-Start Gateway backup.
6. **Install the launchers you need**: Designer Launcher (to build), and either Vision Client Launcher or Perspective Workstation (to run projects as an operator would) — all downloaded from the Gateway Webpage's Downloads section.
7. **Connect a device**: in the Designer's Tag Browser, use **Add > Browse Devices** to pull tags from an OPC UA device connection (the Quick Start Device Simulator, or a real PLC connection you've configured under OPC UA). Alternatively, create your own **Memory tag** for values you want to define yourself rather than pull from a device.
8. **Turn on tag history** where you want trending: set **History Enabled = true** on a tag and pick a **Storage Provider** (a configured historian — for development, Quick Start's SQLite historian works, but a real external SQL database is recommended for production, since SQLite isn't built for concurrent production read/write loads).
9. **Build a first Perspective view**: create a view (choosing a root container type, e.g. Coordinate Container), drag components onto it (displays, inputs, charts), and **bind** their properties to tags — a direct Tag binding for live values (optionally **bidirectional** if the component should write back, e.g. a Slider), and a **Tag History** binding (Time Range = Historical) for trend charts.
10. **Configure alarming** (optional but standard for a real project): create an **On-Call Roster** (who gets notified) under Gateway **Services > Alarming > Rosters**, create a **Notification Profile** (how — e.g. Email) under **Services > Alarming > Notification**, add matching contact info to the roster's users, then in the Designer build an **Alarm Notification Pipeline** (wires roster + profile together) and attach it to a tag's alarm configuration (mode, setpoint, active pipeline). Add an **Alarm Journal Table** component to a view to surface alarm history.
11. **Preview and launch**: use the Designer's **Preview Mode** to interact with the project without leaving the Designer, the **Tools > Launch Perspective...** menu to open a live Session, or open the project through **Perspective Workstation** — the last of these is the closest simulation of how an actual operator will launch and use the application, so it's worth testing there before calling a project "done."

### Installation mechanics worth knowing up front

- **Graphical vs. headless install.** The same installer runs graphically or headlessly. On headless Linux, download via `wget` (no browser needed), install the `fontconfig` package first on Debian/Ubuntu (some features depend on it), `chmod +x` the `.run` file, then execute it. Command-line arguments (`unattended=graphical|minimal|text|none`, `textMode`, `location`, `logLevel`, `user`, `serviceName`, `autoStart`) let you script fully unattended installs and upgrades — useful for pushing the same install out to many machines via configuration management.
- **ZIP installs** are the alternative to the graphical installer — unzip and follow the included README. They're the required path for upgrading ARM installs, and are also the basis for "preconfiguring" a Gateway (build and commission one instance, capture its EULA-acceptance hash and a Gateway backup, then edit `ignition.conf`/`commissioning.json` in a ZIP-extracted base directory so new deployments boot already-commissioned, bypassing the interactive wizard entirely — handy for fleet provisioning).
- **Default install directories**: `C:\Program Files\Inductive Automation\Ignition` (Windows), `/usr/local/ignition` (macOS), `/usr/local/bin/ignition` (Linux).
- **Default ports**: HTTP 8088, HTTPS 8043, Gateway Network 8060 (Cloud Edition differs — see Editions table). Linux blocks binding under port 1024 by default; binding to something like port 80 requires adding the `CAP_NET_BIND_SERVICE` capability to the systemd service override.
- **Verifying authenticity**: installers are code-signed (Windows shows this in the installer's Properties > Digital Signatures tab; macOS via `codesign -dvv`; Linux has no OS-level verification, so compare the SHA-256 hash published on the Downloads page against `sha256sum`/`Get-FileHash` on the downloaded file). Individual `.modl` module files are also code-signed (PKCS#7 certificate chain + per-file signatures, verifiable manually with `openssl`), and the Gateway includes a Software Bill of Materials (`SBOM.txt`, SPDX 2.2/JSON) plus `Notice.txt` for third-party license text.
- **Modules are managed centrally** at **Platform > System > Modules**: install/upgrade by uploading a `.modl` (or manually dropping it into `user-lib/modules` and registering it in `data/modules.json`), disable/enable (takes effect after a Gateway restart, shown via a "Gateway Restart Required" banner), or uninstall. Installing/uninstalling a module requires connected Vision Clients and Designers to restart (Perspective Sessions do not need to restart). A module whose **middle version digit doesn't match the platform's** shows **Faulted** — fix by downloading the version-matched module and restarting. Modules can also be **quarantined** (unsigned/unreviewed certificate, licensing issues) and manually trusted from the three-dot menu.
- **Uninstalling Ignition** removes all projects/Gateway config — take a backup first. **Rolling back** to an older version isn't a supported upgrade path; instead do a clean reinstall and restore an old Gateway backup.

## Gotchas and 8.3 notes

These are points the docs themselves flag as places people get tripped up, drawn mainly from the 8.1→8.3 Upgrade Guide and the platform pages.

**Upgrade path is not optional-skip.** You cannot go directly from 7.9 to 8.3 — you must land on 8.1 first (Gateway Network, serialization, and data-sync changes make a direct 7.9→8.3 jump unsupported). 7.9's Long-Term Support ended June 30, 2025, so anything still on 7.9 is unsupported regardless.

**8.3's serialization switch breaks cross-version data storage.** Because 8.3 replaced Java serialization with Protobuf for Gateway Network traffic, **an 8.3 Gateway cannot store data to an 8.1 Gateway** over the network — this covers Edge Sync Services, remote History Providers, remote Alarm Journals, and remote Audit Profiles. Rule of thumb: **upgrade the central/hub Gateway to 8.3 before any remote/Edge Gateway that feeds it.** (The reverse — old data reads — is fine; it's specifically writes from a newer to an older Gateway that fail.) An 8.3 Gateway will refuse to add Java-serialization-only Gateways as peers unless "Allow Java Serialization" is explicitly enabled (it auto-enables on upgrade/restore, with a warning banner).

**Gateway Network Two-Way Authentication now defaults on.** Upgrading Gateways must explicitly approve each other's certificates (Outgoing Connections page on one side, Incoming Connections page on the other) or the connection won't establish — this is a manual step after upgrade, not automatic.

**OPC UA now defaults to locked-down anonymous access (UA 1.05).** Anonymous OPC UA clients get browse+read only by default after upgrade; write/call access requires either an authenticated client or an explicit custom permission mapping on the device/Tag Provider. If a system depended on anonymous write access, it will silently stop working post-upgrade unless someone re-grants it.

**Gateway security is now role-gated by default, and permissions don't roll over.** 8.3 Gateway webpages require signed-in users with correct roles for many pages/actions; 8.1 permissions are **not** automatically carried forward and must be reassigned after upgrade. Some setting names changed too.

**Audit table casing changed** (`AUDIT_EVENTS` → `audit_events` etc.) — an 8.3 install pointed at an existing 8.1-created audit database needs the old (uppercase) profile config preserved during an in-place upgrade; a *fresh* 8.3 install talking to an old 8.1 audit schema can break on the casing mismatch.

**Hot-swapping modules is gone.** Installing or upgrading any module now always requires a full Gateway restart in 8.3 (previously some modules could hot-swap).

**Historical path syntax changed** for the new Core Historian: 8.1 used `drv:Gateway:Provider`; 8.3 uses separate `sys:Gateway` and `prov:Provider` segments. (SQL Historian paths still use the old `drv` syntax, and old `drv` paths generally still resolve.)

**Scripting namespace consolidation**: 8.3 introduces `system.vision.*` (replacing scattered functions from `system.file`, `system.gui`, `system.nav`, `system.net`, `system.print`, `system.security`, `system.util`) and `system.historian.*` (replacing `system.tag.query/browse/store*History*` functions). Old functions mostly still work but are deprecated — worth grepping existing scripts for these before/after an upgrade rather than assuming silent compatibility forever.

**Windows path-length limits are a recurring theme**, not new to 8.3 — Windows' 255-character path limit can bite both on Gateway backups and (newly, in 8.3) on the deeper tag-definition JSON file paths introduced by the file-system changes.

**JDBC drivers don't auto-upgrade with Ignition**, and in 8.3 specifically MariaDB/MSSQL/PostgreSQL drivers became their own installable *modules* (previously bundled differently) — Docker/container deployments using the old `GATEWAY_MODULES_ENABLED` env-var flag need the new module identifiers added explicitly post-upgrade.

**EAM Remote Upgrade cannot cross the Apple-Silicon architecture boundary.** Upgrading an agent from 8.1.x (x86-only) to 8.3.x (which added native Apple M-series builds) via EAM Remote Upgrade doesn't work for Mac agents — that first hop has to be a manual in-place upgrade; subsequent EAM-driven upgrades (e.g. 8.3.0 → 8.3.1) work normally afterward.

**Perspective File Upload got a hard 20 MB cap** in 8.3 regardless of the component's own `fileSizeLimit` property — raising it now requires an additional `web.xml` `max-file-size` change, not just the component property.

**Quick Start can only be enabled at first commissioning** — there's no later opt-in; the only way to retroactively get Quick Start's sample resources is restoring a Gateway backup that already has them (Inductive Automation publishes a reference Quick-Start backup file for this purpose).

**Cloud Edition on Ubuntu 24.04+ can auto-restart itself.** Ubuntu 24.04's default `unattended-upgrades` + `needrestart` combination will restart the Ignition service whenever a related package patches, unless you explicitly add an exception (`needrestart.conf` override) — worth doing proactively on any Cloud Edition VM you don't want randomly bounced.

**Redundancy upgrade order matters.** When upgrading a redundant pair, upgrade the **Backup** first (with Master's Recovery Mode set to Manual so it doesn't auto-resume), force failover to the newly-upgraded Backup, then upgrade the Master, confirm connectivity, and only then reassert Master control — upgrading in the wrong order risks a window with no valid failover target.

**Quarantine exports switched to JSON.** 8.3 Store and Forward quarantine exports are JSON, not XML — an 8.1 quarantine export **cannot** be imported into an 8.3 Gateway. Leftover un-migrated quarantine data lands as an HSQL file that must be manually moved to `data/local/store-forward/quarantined-databases/` after upgrade.

**Tags: `Alarms` folder → `Alarm Metrics` folder.** The Tag Browser's alarm-bearing-tags folder was replaced with a new `Alarm Metrics` folder (better performance, new scripting/monitoring metrics). Old scripts/bindings referencing the deprecated `Alarms` folder keep working, but new development should target `Alarm Metrics`.

**Custom Perspective themes need restructuring.** 8.1's filesystem-only theme authorship (a root-level entry CSS file) is replaced by an 8.3 config/resource model: each theme needs its own `config.json` (with `isPrivate` and `entrypoint` properties) and an `index.css` entrypoint. Themes that followed IA's built-in theme structure migrate automatically; custom ones may need import paths manually fixed (originals are preserved in a `.migrated-themes-TIMESTAMP` directory for reference).

**Duplicate usernames block the 8.3 upgrade outright.** Ignition 8.3 disallows duplicate usernames across Internal/AD-Internal-Hybrid User Sources on one Gateway. If an 8.1 Gateway has them, the migration will skip (not corrupt) affected User Sources and log the conflict — you must remove duplicates on 8.1 *before* upgrading, or restore the 8.1 backup, dedupe, and retry.

**Legacy 7.9→8.1 context worth knowing even now** (most 8.3 shops still trace their lineage through this jump): Vision Mobile Module was discontinued in favor of Perspective; Java Web Start-based launching was replaced by the still-current Designer/Vision Client Launchers with embedded, self-managed JREs; the Tag system was rebuilt around JSON definitions (`system.tag.configure` replaced the old `editTag`/`addTag` functions, `browseConfiguration` was replaced by `getConfiguration`); "Scan Classes" were renamed "Tag Groups" and "LastChanged" became "Timestamp"; UDT parameter references changed from string-interpolation style (`"{ParamRef}"`) to explicit `concat()` expressions; the old "global" project concept became true project inheritance, with 7.9's `[global]` shared scripts/templates auto-migrated into a new inheritable `global` project; and OPC UA certificates went from implicitly-trusted to requiring explicit trust on both client and server sides (all secured connections other than loopback fault on upgrade until certificates are approved) — the same certificate-trust pattern 8.3 repeats for its own new client/server certificates.

**Tag Historian licensing has changed vocabulary twice.** 8.1 separated "read-only" historian licensing (for front-end Gateways in a Scale-Out setup, eliminating a spurious "Partially licensed" message) from full read/write licensing. 8.3 goes further and replaces the "Tag Historian" license line item entirely with separate **Historian Core** and **SQL Historian** items; Serial Support Client/Gateway got folded into the base platform, and the old Web Browser module got folded into Vision (now under the Misc component category).

**Gateway project directory scan rate is 5 minutes by default** (was 10 seconds pre-8.1, which was resource-intensive) — relevant for anyone driving project changes through an external version-control checkout rather than the Designer, since a VCS-triggered file change can take up to 5 minutes to be picked up. It's configurable back down via `-Dignition.projects.scanFrequency=10` in `ignition.conf` if faster reaction is worth the overhead.
