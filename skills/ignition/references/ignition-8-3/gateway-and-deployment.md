# Ignition 8.3 — Gateway, configuration and deployment

Source: live Ignition 8.3 documentation (docs.inductiveautomation.com/docs/8.3), ~87 pages under Platform > Gateway, Gateway Network, Redundancy, Store and Forward, Licensing, Audit Log, Projects, Launchers/Workstation, Installing/Upgrading, and the Appendix reference pages. Grounded directly in doc text; direct 8.3 change callouts are quoted briefly where the docs state them explicitly.

---

## Gateway architecture

**What the Gateway is.** The Ignition Gateway is "the primary software service that drives everything in Ignition... a single application that runs as a web server and is accessed through a web browser." It connects to data sources and PLCs, executes modules, and communicates with clients (Designer, Vision Clients, Perspective Sessions). All shared configuration — database connections, device connections, tags, security — lives on the Gateway; **projects** hold the designed, user-facing elements (windows/views, transaction groups, templates, reports, scripts, alarm pipelines, SFCs).

**Process/service model.** The Gateway runs as an OS service (Windows service, or via `ignition.sh` on Mac/Linux, both wrapping the Java Service Wrapper by Tanuki Software). Start/stop:
- Windows: `net start Ignition` / `net stop Ignition`, or `start-ignition.bat` / `stop-ignition.bat`
- Linux: `/usr/local/bin/ignition/ignition.sh start|stop|restart`, or `service Ignition-Gateway start|stop`
- Mac: `/usr/local/ignition/ignition.sh start|stop|restart`

The wrapper checks `ignition.conf` at startup for JVM/service parameters — **changes to that file only take effect on Gateway restart.**

**Scopes.** Ignition resources and code execute in distinct scopes: **Gateway** (server-side — Gateway Event Scripts, Alarm Pipelines, SFCs, Transaction Groups all run here, once, regardless of how many clients connect), **Designer** (authoring-time), **Vision Client** (per-launched client instance — Client Event Scripts), and **Perspective Session** (per browser/Workstation session). Project resources described as "runnable" (Gateway Event Scripts, Alarm Notification Pipelines, SFCs, Transaction Groups) execute once per **leaf project** in an inheritance chain — see Project Inheritance below, since duplicate leaf projects mean duplicate executions.

**Modules.** Ignition is modular; functionality (Perspective, Vision, SQL Bridge, OPC UA, drivers, Historian, etc.) is delivered as `.modl` files loaded at startup from `user-lib/modules` (built-in) or a third-party/external modules folder (`data/local/modl` by default, or `data/var/ignition/modl` in the Docker image; configurable via the `ignition.gateway.externalModulesFolder` system property). **Hot swapping modules is no longer supported in 8.3** — installing or upgrading a module requires a Gateway restart (a change from 8.1). Modules are matched to a specific Ignition edition/license; JDBC drivers (MariaDB, MSSQL, PostgreSQL) are now delivered as modules rather than being bundled, which matters for `GATEWAY_MODULES_ENABLED` allow-lists in containers.

**The Gateway web interface** is organized into top-level sections: **Home** (per-visualization-type launch pages — Designer, Perspective, Vision), **Config**/**Platform** (System settings: Redundancy, Store & Forward, Projects, Modes, Licensing, Gateway Settings, Backup & Restore), **Network** (Gateway Network, Email, Web Server), **Security** (Users, Audit Profiles, Security Zones), and **Diagnostics** (Logs, Threads, Scripts, System Performance, Metrics Dashboard, Execution). Access to Gateway webpages is role-gated: **"8.3 Gateway webpages now operate on a required role basis... permissions granted in 8.1 will not automatically roll over into 8.3, and must be reassigned."**

**Status/diagnostics pages** (Diagnostics tab):
- **Logs** — live Gateway log stream (Logger/Time/Message, filterable by date range and Min Level: All/Trace/Debug/Info/Warn/Error), with per-logger level overrides and **Mapped Diagnostic Context (MDC) Keys** to set a whole functional area's loggers at once. Logs downloadable from the page. Scripts can write to this log via `system.util.getLogger("name")`.
- **Threads** — live thread dump viewer; **Automatic Thread Dump Sample Rate** is configurable (`-Dignition.automaticThreadDump.sampleRate`, default 1000ms, min 500ms).
- **Metrics Dashboard**, **System Performance**, **Scripts**, **Execution** — runtime/JVM/system health views.

**Logging pipeline.** Ignition logs to **stdout**, which the Java Service Wrapper captures into the **wrapper log** files (`logs/wrapper.log`, `wrapper.log.1`, `.2`, ... — higher number = older; ~6 files on a mature install). Wrapper logs are the *first place to check* if the Gateway fails to start, since they capture pre-startup issues the in-Gateway Logs page cannot show. Log persistence/rotation and Gateway-internal (audit-style) log storage is governed by `logback.xml` (see Configuration model below). In Docker, wrapper.log is instead emitted to container stdout for the container runtime's own logging driver — Ignition does not rotate it itself in that mode, so container log-size limits must be configured externally.

### Gateway Backup and Restore

A **Gateway Backup** (`.gwbk`) is the all-inclusive snapshot mechanism — distinct from a per-project **Project Export** (see Projects, below). It typically completes in under a minute and includes essentially everything visible in the Gateway Webpage: all projects, Gateway/Web Server/Gateway Network/Email settings, auth profiles, User Sources, IdP configs, Security Levels/Zones, all Alarming config (Journals, Notification Profiles, on-call rosters, schedules), SECS/GEM equipment config, Tag History Providers and all Tag Providers (tags, UDTs, Tag Groups), device and OPC UA connections/settings, BACnet local device config, EAM settings, SFC settings, database connections, and JDBC drivers. **Not included**: data in external systems (SQL databases, PLC programs), files manually added to the install directory, and — critically — **Modules, license information/grants, Redundancy settings, and the Tag Reference Store are never changed by restoring a backup onto an existing Gateway.**

- **Take it from**: Gateway Webpage (Platform > System > Backup & Restore > Download Backup) or `gwcmd -b <path>`. Default filename pattern: `GatewayName_Ignition-backup-YYYYMMDD-HHMM.gwbk` (customizable — see Scheduled Backups below).
- **Redundant pairs** get a **Download with Peer Data** option (includes the redundant peer's local files, e.g. SSL cert details) vs. **Download without Peer Data** (normal contents only).
- **Restoring** is destructive by design: "**ALL** of the server's current configuration will be permanently lost... There is no merge option." Options at restore time: **Restore Disabled** (import everything but leave it disabled), **Disable Temp Project Backup**, **Override Gateway Name** (+ New Gateway Name — caution: renaming after initial setup can break dependencies; see System Name Usage Reference in Gotchas). A backup can also be applied **during installation** via the installer's optional restore-from-backup step.
- **Restore Disabled** specifically affects (leaves disabled): EAM Backup/Restore tasks, Projects, Store and Forward engines, Audit Profiles, Security Zones (except default), API keys, select device settings/connections (AB CompactLogix Legacy, BACnet/IP, Programmable Device Simulator), Database Translator settings, database connections, select OPC connections (Ignition OPC UA, Kepware OPC UA), Classic SMTP email settings, Gateway Network settings + outgoing connections, Realtime Tag Providers (default + Sample_Tags), Remote Tag Providers, Historians, Alarm Journals/Notification Profiles/Rosters/Pipelines (pipelines need all dependent components re-enabled to function), and Alarm Scheduling (Holidays schedule only).
- **Command line**: `gwcmd -s <backup file path>` to restore, with `-o <name>` to override the Gateway name (`-y` skips the override-name prompt), `-d` to apply Restore Disabled, `-m` to stage without contacting a running Gateway.
- **Scheduled Backups** (Platform > System > Gateway Settings): cron-style **Backup Schedule** (UNIX crontab format), destination **Backup Folder** (local path or UNC network path — mapped network drives are **not** supported, and the Gateway service account needs write permission), **Retention Count** (oldest backups pruned automatically), and a **Filename Pattern** supporting `${os}`, `${version}`, `${gatewayName}`, `${edition}`, `${timestamp}` placeholders (default: `${gatewayName}_Ignition-backup-${edition}${timestamp}.gwbk`).

---

## 8.3 configuration model

This is the single biggest architectural change from 8.1 to 8.3: **Ignition 8.3 moved Gateway configuration out of the internal database (IDB) and into a file-based, resource-collection configuration system.** Several docs pages state this directly:

> "Prior to 8.3.8, a VACUUM operation would execute against the internal database upon Gateway startup. However, **since Gateway configuration now lives in the file-based config system**, this is no longer as necessary and is disabled by default."

> "During the upgrade process, Ignition migrates resources from the internal database (IDB) to the new file system. **The deprecated IDB is not removed after upgrading, but will not affect your system as it is no longer used.**"

> "In 8.1, theme authorship relied solely on the filesystem. In 8.3, **the new config and resource collection model** required the existing theme structure to conform to this new model."

### Two config files, two purposes — don't confuse them

| File | Purpose | Location | When it's read |
|---|---|---|---|
| **`ignition.conf`** | The **wrapper/JVM launch configuration** — heap size, JVM system properties (`wrapper.java.additional.#`), deployment-mode selection, and dozens of documented `-D` system-property overrides. | `%IgnitionInstallationDirectory%/data/ignition.conf` | Only at Gateway **startup** — edits require a restart to take effect. |
| **`gateway.xml`** | A small, mostly-networking property file — HTTP/HTTPS/GAN ports, public address, cipher suites, webserver thread count, `config.idb` legacy autobackup settings. | `%IgnitionInstallationDirectory%/data/gateway.xml` | At Gateway startup; most of these same settings are also editable from **Web Server settings** in the Gateway UI. |

Neither of these is the *resource* configuration (tags, device connections, projects, etc.) — that lives in the file-based **resource collection** system described next.

### The resource collection model: system → external → core → local

8.3 organizes every Gateway resource (device connections, database connections, tag providers, security settings, etc.) into a layered set of **collections**. Deployment Modes (new in 8.3) are user-defined collections built on top of this hierarchy:

- **system** collection (top) — built-in, **immutable** resources the platform injects (e.g. the MariaDB JDBC driver). You can still create a resource *override* from a system resource, which becomes a resource definition in whatever collection you're working in.
- **external** collection — resources that live in Ignition's external file system (`data/config/resources/external`) and are **read-only from the Gateway UI**. Intended for centrally managed configuration and as the target for version-control-managed resources — "if you are using a version control system (VCS), this collection is where your VCS should place any relevant resources."
- **core** collection — child of external; resources here **are** configurable through the Gateway Webpage. A freshly installed Gateway, or one with no deployment modes configured, runs in **core** by default. Deployment modes and resource overrides are typically created starting from core.
- **local** collection — host-specific data (e.g. certificate details) that never propagates to a redundant peer or is inherited by deployment modes, but is used at runtime on that specific machine. Local can also hold resource-definition overrides, but again these are **not** synced to a backup Gateway.

### Resource types

- **Named resources** — individually listed and independently named (e.g. a device connection). Multiple named resources of the same type can coexist.
- **Singleton resources** — a bundle of properties saved as one resource definition (e.g. the Gateway Network Settings page — the whole page is one resource).
- **System resources** — immutable, from the system collection; can be overridden but not edited directly.

Everything except **Deployment Modes, Modules, Projects, and Licenses** can have resource overrides created against it.

### Gateway Deployment Modes (new in 8.3)

Deployment Modes let you define alternate sets of resource values (e.g., Dev vs. Prod database connections) that live side-by-side and are switched by **which mode the Gateway is currently running in** — not by editing resources directly.

- Created/edited on **Platform > System > Modes** (name, title, description).
- Resource definitions are assigned to a mode by **overriding** an existing named/singleton resource, **duplicating** a named resource (optionally under a new name and/or into a different mode — three distinct duplication semantics are supported: new-name/different-mode, new-name/same-mode, same-name/different-mode), or **manually creating** a new resource and choosing a target mode from a dropdown at creation time.
- **Changing the active mode cannot be done from the Gateway UI.** It requires an additional Java parameter in `ignition.conf`:
  ```
  wrapper.java.additional.4=-Dignition.config.mode=DEPLOYMENT_MODE_NAME_HERE
  ```
  followed by a Gateway restart. Only one mode is active at a time.
- **Redundancy caveat:** "deployment mode configuration is stored in the `ignition.conf` file and **does not sync** between the primary and backup Gateways. To avoid issues where a failover could result in the backup using different device or database connections than expected, ensure both Gateways are configured with the same `-Dignition.config.mode` value and restart both services."
- Modes also enforce Gateway security/role logic — unauthorized users can't see mode-specific resources without the right roles.
- Modes can be manipulated directly via the file system (useful for IaC/GitOps) but the Gateway won't pick up out-of-band file changes automatically — click **Scan File System** on the Modes page, or POST to `{{gateway_address}}/data/api/v1/scan/config` (see [OpenAPI](https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi) at `{{gateway_address}}/openapi#tag/config-management`). The docs explicitly discourage this as anything but a last resort: **"this is not recommended and should only be used as a last resort."**

### On-disk layout (from the Gateway Folder Structure reference)

Under `%IgnitionInstallationDirectory%/data/`:

| Path | Contents | In `.gwbk`? | Synced to redundant backup? |
|---|---|---|---|
| `config/resources/external` | Read-only resource-collection files (e.g. Docker volume-mounted resources) | No | No |
| `config/resources/core` | Core-collection resource files | Yes | Yes |
| `config/resources/local` | Machine-specific resource-collection files (e.g. local system properties) | Yes (separate `/local-backup` folder for redundancy) | No |
| `config/resources/{mode}` | Deployment-mode-specific resource files | Yes | Yes |
| `config/ignition` | Platform files identical across master/backup (e.g. OAuth2 email token files) | Yes | Depends on redundancy provider |
| `config/{module-id}` | Module-owned files identical across master/backup (e.g. OPC UA trust store) | Yes | Depends on redundancy provider |
| `config/local/ignition` | Platform files that **should differ** master vs. backup (e.g. hostname-specific certs) | Yes (separate `/local-backup`) | Depends |
| `config/local/{module-id}` | Module files that should differ master vs. backup | Yes (separate `/local-backup`) | Depends |
| `var/ignition` | Transient, non-backed-up platform data (Designer auth tokens, internal Alarm Journal, internal Audit Log, licensing, Store and Forward engine state) | **No** | Depends |
| `var/{module-id}` | Transient module data (Perspective/Vision auth tokens, Core Historian data, SFC state) | **No** | Depends |
| `projects` | Project resources | Yes | Yes |

Tag JSON definitions specifically now live at paths like `data/config/resources/core/ignition/tag-definition/...`, which — combined with 8.3's longer resource-collection paths generally — can trip the **255-character path limit on Windows**; see the "Working with Long File Paths" caution repeated across multiple pages.

**File-naming rules** (Gateway Folder Structure reference): most Unicode letters/numbers/punctuation are fine as file/resource names; space and period are disallowed as first/last character; hyphen disallowed as first character; the characters `` ` / \ ? * : | " < > `` are never allowed. Renaming during 8.1→8.3 migration can force some project resources (e.g. migrated Gateway/Client Event Scripts) into new names if the old ones don't comply — watch for a migration-needed icon next to affected resources in the Designer after upgrade.

### What this replaces from the old web-UI/IDB model

- The legacy **`config.idb`** internal database is **still present after an 8.1→8.3 upgrade but unused** — it is not deleted, but nothing reads or writes it going forward. `gateway.xml`'s `localdb.autobackup.*` settings, which govern `config.idb` autobackups, changed default: **`localdb.autobackup.count` default changed from 5 to 0 in 8.3.8+, disabling automatic `config.idb` backups by default.**
- Custom Perspective **themes** had to be restructured: 8.1 themes relied purely on loose files at the theme folder root; 8.3 requires each theme to have a `config.json` (with `isPrivate` and `entrypoint` properties) to conform to the resource-collection model. Migrated originals are preserved in a `.migrated-themes-TIMESTAMP` directory under `data/modules/com.inductiveautomation.perspective` for reference.
- A **migration log** (Markdown) is written to the `config` folder during upgrade, detailing which tables were migrated, migration duration/timestamps/strategies, and any tables not yet moved.

### The Gateway REST API and config-as-code (`/openapi`)

As of 8.3, "many configuration elements in Ignition are exposed as **resources** using a standardized format" — a direct consequence of the resource-collection model — and are automatically surfaced as REST endpoints under `/data/api/v1/resources`, discoverable at `/openapi` (interactive Swagger-style UI) or `/openapi.json` (raw spec, importable for SDK generation). Representative routes:
- `GET /data/api/v1/resources/list/<moduleId>/<typeId>` — list all resources of a type.
- `POST /data/api/v1/resources/<moduleId>/<typeId>` — create a resource.
- `DELETE /data/api/v1/resources/<moduleId>/<typeId>/<name>/<signature>` — delete a named resource.
- `POST /data/api/v1/scan/config` — force a file-system rescan for out-of-band resource/Deployment-Mode changes (same endpoint referenced under Deployment Modes above).

Authentication is via an **API Token** (Platform > Security > API Keys), passed as the `X-Ignition-API-Token` header:
```bash
curl -H "X-Ignition-API-Token: YOUR_TOKEN" https://<gateway-host>:8088/data/mymodule/api/v1/getItem/abc-123
```
**Mutating requests (POST/PUT/DELETE) are recorded in the audit log** with user, IP, and API key — but **GET requests are not audited**. The docs explicitly flag this API as an IaC/orchestration surface: "these resource routes are useful for Infrastructure-as-code workflows, Third party orchestration tools, Remote configuration management, Automating Gateway setup in containerized or cloud environments" — while also cautioning that misuse "may result in the loss of configuration, tags, projects, or other critical resources" and recommending it be restricted to trusted clients.

### Implications for containerized / IaC deployments

- Treat `config/resources/external` as the mount point for GitOps-managed resource files — it's explicitly designed as the VCS target and is read-only from the UI, preventing UI drift.
- `config/resources/core` and `config/resources/local` are the natural targets for `.gwbk`-restorable, UI-editable state; `var/` is scratch/runtime state that should **not** be treated as durable configuration (it's excluded from Gateway backups).
- Because config now lives in files rather than a DB, **Docker/Kubernetes volume strategy matters more than in 8.1**: mount `data/config` (and `data/projects`) as persistent volumes; anything under `data/var` can be treated as ephemeral/scratch.
- Environment-variable-driven bootstrap (see Reference tables below) still works for initial commissioning and ongoing GAN/leasing config — this is unchanged in spirit from 8.1, just layered on top of the new file model.
- `wrapper.java.additional.#` parameters (in `ignition.conf`) remain the mechanism for supplemental JVM/system-property configuration; in Docker these can be supplied as post-double-hyphen runtime arguments and are merged with the file's contents.

---

## Installation and upgrade

### Installing

Installers are available per-OS (Windows/Mac/Linux) plus ZIP-file installs (for headless/no-installer scenarios) and a Docker image. Minimum requirements are published on the Downloads page. Installs include a **Software Bill of Materials** (SPDX 2.2 JSON, `SBOM.txt`) and `Notice.txt` (third-party licenses) in the install directory.

**Default install directories:**
- Windows: `C:\Program Files\Inductive Automation\Ignition`
- macOS: `/usr/local/ignition`
- Linux: `/usr/local/bin/ignition`

Mac/Linux installs also contain `ignition.sh` and `ignition-util.sh` (not meant to be edited — use `ignition.conf` for configuration changes), and the installer creates a sudoers file at `/etc/sudoers.d/99-<serviceName>` so the service can restart without an interactive login.

**Headless Linux install:** download via `wget --referer=https://inductiveautomation.com/downloads/ignition <release-url>`; install `fontconfig` first on Debian/Ubuntu (`sudo apt-get install fontconfig`) — some Ignition features depend on it.

**Command-line / unattended install arguments** (passed after the platform-specific arg delimiter — Windows `--%`, Mac `open -a ... --args`, Linux `--`):

| Argument | Values | Purpose |
|---|---|---|
| `unattended` | `graphical`, `minimal`, `text`, `none` | Controls interaction level. Unattended **upgrades** remove deprecated built-in modules, leave third-party modules as-is, upgrade currently installed bundled modules, and do **not** auto-start the service afterward — a user/script must start it. |
| `textMode` | `true` | Force text-mode install even with GUI support (overridden by `unattended`). |
| `location` | path | Override install directory. |
| `logLevel` | `trace`/`debug`/`info`/`warn`/`error` | Installer log verbosity. |
| `user` | username | OS owner of the install. |
| `serviceName` | string | Overrides default `Ignition` service name; combined with `unattended` during upgrade, replaces the Windows service. |
| `autoStart` | `true`/`false` | Whether to start the Gateway automatically post-install/upgrade. |

**Quick Start** (new-install only): opt-in wizard that creates an internal SQLite DB connection, a Programmable Device Simulator connection with tags, an internal alarm journal, and a sample project. Can be disabled globally via the `DISABLE_QUICKSTART` environment variable.

**System Commissioning** (post-install/upgrade, or re-triggerable via `gwcmd` password reset): choose edition (Standard / Edge / Maker), set Gateway Network port (auto-iterates if the default is taken, but only for **clean** installs — existing/upgraded Gateways fault instead of searching), activate a license (Maker requires an 8-char key + activation token, free from account.inductiveautomation.com), create the initial admin user, and set HTTP/HTTPS ports (defaults 8088/8043).

### Installing / upgrading modules

Module management lives at Platform > System > Modules — install, upgrade, enable/disable, uninstall, or view fault/license status. **Installing or uninstalling a module forces connected Vision Clients and Designers to restart; Perspective Sessions do not restart.** Two supported install paths:
1. **Via the Gateway UI**: Install or Upgrade Module + > Choose File (`.modl`) > Install.
2. **Manual file-system installation** (useful for scripted/IaC provisioning): drop the `.modl` into `%IgnitionInstallationDirectory%/user-lib/modules`, then add a matching entry to `%IgnitionInstallationDirectory%/data/modules.json` (module name, filename/path, `onStartup` and `certFingerprint` mirrored from an existing entry), then restart the Gateway service. This is the same file Docker's `GATEWAY_MODULES_ENABLED` allow-listing interacts with.

A module that shows **Faulted** after installation, or requires **Trusted Module** verification, or lands in a **Quarantined** state (untrusted cert not yet accepted) are each called out as distinct troubleshooting states on the Modules page — see `ACCEPT_MODULE_LICENSES` / `ACCEPT_MODULE_CERTS` environment variables (Reference tables) for automating quarantine/EULA acceptance in headless deployments.

### ZIP-file installation and pre-configured (cloned) Gateway deployment

ZIP installs are the alternative to the graphical/interactive installer, driven by an included README. **On upgrade via ZIP, do not overwrite `ignition.conf`** — doing so can break the upgrade. On Linux, a service-installed Gateway must be removed first (`./ignition.sh remove`) before upgrading to a different edition and reinstalling the service.

For mass/scripted provisioning, the docs describe a **pre-configured deployment pattern** that skips interactive commissioning entirely:
1. On a reference Gateway that has already completed commissioning (accepted the EULA), read the EULA acceptance hash from `%installDirectory%/data/commissioning.json` (`eulaSetup.eula` key) — this file only exists post-commissioning.
2. Take a **Gateway Backup** from that reference system to carry over an initial user account (and any other desired resources) into the new deployment.
3. Extract the ZIP installer on each target system, inject the saved EULA hash and the reference `.gwbk` into the new install's expected locations/arguments per the documented example, and start the service — the Gateway comes up already commissioned, with no manual walk-through required per node.

This pattern is the documented alternative to Docker/Kubernetes for teams standing up many Gateways from bare ZIP installs (e.g. on hardware where a container runtime isn't available), and it composes with the environment-variable-based commissioning (`GATEWAY_ADMIN_USERNAME`, `IGNITION_LICENSE_KEY`, etc.) used elsewhere for the same "skip interactive commissioning" goal.

:::note
Ignition Gateway and Perspective Sessions run on ARM (e.g. Raspberry Pi), but the **Designer, Vision Client, and Perspective Workstation cannot run on ARM-based Linux** — those must run from an Intel-based machine against the ARM Gateway.
:::

### Ports (see Reference tables for the full table)

Core listening ports: **8088** (HTTP), **8043** (HTTPS), **8060** (Gateway Network/GAN, SSL by default), plus MQTT (1883/8883), OPC UA (62541, legacy 4096), multicast discovery (4445/4446), and Vision Local Client Fallback (6501).

### Upgrading

Run the 8.3 installer over an existing install — it detects the prior install and offers an upgrade wizard, structurally identical to the install wizard (module selection screen included, covering both bundled and third-party/additional modules). **Take a Gateway backup first.** Also plan to upgrade Launchers — a Gateway ahead of its Launcher version triggers an update prompt in the Launcher.

- **JDBC drivers are not upgraded automatically** — only change them if you upgrade the underlying database.
- **You cannot go directly from pre-8.1 to 8.3** — must hit 8.1 first, including for Gateway Backup restores (upgrade the backup to 8.1, then restore onto 8.3).
- **Modules cannot be hot-swapped in 8.3** — installing/upgrading modules always requires a restart.
- **Redundant pair upgrade procedure:** upgrade the Backup first (Master stays active); once Backup is back online, use **Force Failover** so Backup becomes active; then upgrade Master; once both reconnect, **Assume Control** to hand responsibility back to Master. Set Master's **Recovery Mode** to **Manual** beforehand so it doesn't auto-reclaim control mid-procedure.
- **Rolling back:** see "System Rollback" section of the Installing and Upgrading page (not deeply detailed in the crawled set beyond the section existing).

### 8.1 → 8.3: what breaks / requires action (see also Gotchas section below for a consolidated list)

The dedicated **8.1 to 8.3 Upgrade Guide** page is the single richest source in this doc set. Key **required-action** items:

- **Audit Profile table/column names changed case** — 8.1 `AUDIT_EVENTS`/`AUDIT_EVENTS_ID` become 8.3 `audit_events`/`audit_events_id`. In-place upgrades keep working; new 8.3 installs pointed at an *existing 8.1 database* can break on case-sensitive SQL.
- **Gateway Network serialization moved from Java serialization to Protobuf.** 8.3 Gateways cannot store data to 8.1 Gateways over the network (Edge Sync, Remote History, Remote Alarm Journals, Remote Audit Profiles) — the Gateway hosting the actual data store **must be upgraded to 8.3 first**, then remotes/Edges after. Editing an 8.3-remote-provider's tags from an 8.1 Designer will throw (`GatewayException`/`UndeclaredThrowableException`) — not supported.
- **Require Two-Way Authentication now defaults to `true`** on the Gateway Network — both ends must explicitly trust each other's certificate (approve on Outgoing Connections page on one side, Incoming Connections page on the other), or communication fails after upgrade.
- **Allow Java Serialization is auto-enabled during 8.1→8.3 upgrades/restores** (disabled by default on fresh 8.3 installs) purely to preserve interop with remaining 8.1 Gateways during a mixed-version transition period — a banner appears on the Gateway expecting the incoming connection. Treat this as **temporary**; disable once all Gateways are 8.3.
- **JDBC driver modules (MariaDB/MSSQL/PostgreSQL) are now modules** — Docker containers using `GATEWAY_MODULES_ENABLED` in 8.1 must add the new module identifiers post-upgrade or DB connections silently fail to start.
- **OPC UA 1.05**, new client/server certs generated on upgrade requiring re-trust on both ends; **anonymous OPC UA clients lose write/call access by default** (browse/read only) — any device/tag provider lacking explicit role mappings needs custom permission mappings restored post-upgrade if anonymous write/call is required.
- **User Sources with duplicate usernames block migration** — must dedupe on the 8.1 side before upgrading (8.3 disallows duplicate usernames in Internal/AD-Internal-Hybrid sources); migration now detects and skips such User Sources rather than corrupting them.
- **Identity Provider JSON export format changed** — 8.1 IdP exports cannot be imported into 8.3.
- **Service Security settings moved into Security Zone configuration** (Manage Policy from the zone's three-dot menu); a policy on the `default` zone migrates into that zone's core collection.
- **Store and Forward Primary Store Maintenance Value defaults to 0 (unlimited)** post-upgrade (was "Max Records" in 8.1) — because the S&F engine is now multi-threaded (parallel storing across Alarming/Auditing/Scripting/SECS-GEM/Tag History/Transaction Group), and **quarantine exports switched from XML to JSON** — 8.1 quarantine exports cannot be imported into 8.3.
- **Historical path syntax changed** for non-SQL historians: `drv:` → `sys:`/`prov:` key-value pairs (SQL Historian still uses `drv:` unchanged).
- **Tag JSON storage path changed** (see folder structure above) — long-path risk on Windows.
- **File Upload component now caps at 20MB** by default regardless of the component's `fileSizeLimit` — raise via `web.xml`'s `max-file-size`.
- Several **`system.*` functions deprecated** in favor of `system.vision.*`, `system.historian.*`, and reworked `system.db.*` — see the deprecation table under Gotchas below.
- **Hot swapping modules removed.**
- **EAM Agent Recovery task removed**; EAM Remote Upgrade **cannot** cross-upgrade 8.1.x→8.3.x on Apple M-series Macs (architecture change) — must do an in-place upgrade first, then subsequent EAM remote upgrades work.
- **Custom Perspective themes need restructuring** to the new `config.json`/`entrypoint` model (see Configuration model above).

Post-upgrade, review `%IgnitionInstallationDirectory%/logs/` (wrapper logs, `tag-migration` per-provider JSON logs, `install_{timestamp}` installer logs) and `%IgnitionInstallationDirectory%/data/config/resources/migration-log` for migration status/failures.

---

## Projects

A **project** is Ignition's unit of visualization/configuration authorship: windows/views, transaction groups, templates, reports, scripts, alarm pipelines, SFCs, and general settings — everything *except* shared Gateway-level resources (database/device connections, tags, users), which live outside any project. Projects are authored in the Designer and consumed at runtime by Vision Clients or Perspective Sessions (with optional **Offline Mode** for Perspective Mobile App users disconnected from the Gateway). There is no hard limit on the number of projects per Gateway; each runtime Client/Session/Designer operates on exactly one project at a time (Vision **Retargeting** allows seamless in-place project switching within a client).

### On-disk model

Project resources are stored under `data/projects/` and are part of a Gateway Backup. **Project versioning is explicitly left to external tooling**: "Project versioning is handled outside of Ignition. The file system that stores data in Ignition stores everything as a series of files. You can use any tool you'd like... including versioning software" — i.e., Ignition does not provide built-in VCS, but the file-per-resource model (reinforced by 8.3's resource-collection format) is designed to be Git-friendly. The **Ignored Project Directory Files** system property (`-Dignition.projects.ignoredFiles=Folder1:Folder2:...`) lets the Gateway skip scanning specific folder names (default: `.git`, `.svn`, `.hg`) — useful to keep a project-local VCS checkout from being treated as project content, but be careful: a project sharing the excluded folder's *name* is itself excluded.

### Project Inheritance

One project (the **parent**, flagged **Inheritable**) can share resources (views, windows, scripts, templates, pipelines) with **child** projects that set it as their **Parent Project**. Key mechanics:
- Enabling Inheritable on a project sets **Allow Overrides** by default on all its resources, propagating them to children.
- An Inheritable project **cannot be launched standalone** — attempting to run it directly gives a "Project Not Runnable" error.
- Inherited resources show grayed-out in the child's Designer tree with an **Inherited Resource** icon; editing requires **Override Resource**, which recreates the resource locally in the child and decouples it from future parent changes (until **Discard Overrides** reverts it).
- Renaming an inherited resource in the parent does **not** rename the child's copy — Ignition detects the "missing" original and re-propagates it under the old name, so you can end up with both old and new resources.
- Named Queries support **Open read-only** to inspect an inherited query's Settings/Authoring/Testing tabs without triggering an override.
- Inheritance chains can nest arbitrarily (a project can be both a child and, itself, inheritable to further children).
- **"Runnable" resources — Gateway Event Scripts, Alarm Notification Pipelines, SFCs, Transaction Groups — execute once per *leaf* project** in the inheritance chain. If two leaf projects both inherit a runnable resource from the same parent, it executes **twice**, concurrently. The documented mitigation: move runnable resources into a dedicated standalone (non-inheriting, non-inherited) project.

### Project properties / settings

Configurable per-project from **Platform > System > Projects > Edit** (or Designer Project Properties):
- **Project Settings**: Name (immutable outside the explicit Rename flow — which triggers a project shutdown/restart and can break shortcuts referencing the old name), Description, **Title** (safe to change; used on launch pages — prefer changing Title over Name), Enabled, Inheritable, Parent Project.
- **Security Settings**: User Source, Identity Provider.
- **Connections**: Default Database, Default Tag Provider.
- Management actions from the three-dot menu: **Edit, Rename, Duplicate, Export, Disable, Delete.** None of these can be performed from the Gateway while the project is open in a Designer.

### Import / export

Project export/import is distinct from a full **Gateway Backup**: export is per-project, faster/smaller, and includes only project-scoped resources — **Alarm Pipelines, Named Queries, Perspective Properties/Views, Project Properties, Reports, SFCs, Transaction Groups, Vision Client Tags, Vision Windows/Templates, Client Event Scripts, Gateway Event Scripts.** It explicitly **excludes** Gateway-level resources (device/database connections, Tag Providers, tags themselves — tags require the separate Exporting/Importing Tags workflow). Export is available from both the Gateway Webpage (whole-project `.zip`) and the Designer (selected resources only). Import merges into the target Gateway, offering rename-or-overwrite if a same-named project already exists. EAM's **Send Project** agent task automates this between Gateways.

**Version-control implication:** because project export/import is resource-granular and file-based, and because 8.1→8.3 tag/script migrations are only reliably applied via Gateway Backup restore or the installer's upgrade check (project/tag *imports* do **not** trigger that migration check), teams doing VCS-based project promotion across major versions should prefer Gateway Backup-based promotion for the upgrade itself, then return to file/`.zip`-based project promotion for day-to-day changes once both environments are on the same major version.

### Project templates

Ship-in Perspective templates: **Web Nav**, **Perspective Menu Nav** (page config/properties are editable post-creation). Vision templates: **Tab Nav**, **2-Tier Tab Nav**, **Tree Nav** — supporting adding windows into the chosen navigation structure after creation.

---

## Gateway Network

The Gateway Network (GAN) connects multiple Gateways over WAN/LAN and underlies EAM, remote tag/history/alarm providers, and remote alarm notification. Key concepts:

- **Outgoing vs. Incoming connections**: an outgoing connection is configured on the initiating machine; the remote machine auto-creates a corresponding incoming connection (subject to its security policy). Only one connection object is needed per Gateway pair — "outgoing" vs. "incoming" is just a label for where it was configured, and Ignition treats A→B and B→A configuration as equivalent.
- **Server propagation**: connecting to GatewayB also surfaces GatewayB's awareness of GatewayC (even with no direct A↔C link) — EAM and similar modules can use this transitively.
- Each Gateway has a **UUID** at `data/config/local/ignition/gateway-network/uuid.txt`, regenerated whenever a Gateway is cloned from a backup — intentionally, to avoid GAN collisions between clones. To preserve the UUID (e.g. deliberately reconstituting a specific node), enable **Restore local-only Configuration Files** during a Gateway restore.

### General Settings (Network > Gateway Network > Settings)

**Main:**
| Setting | Default | Notes |
|---|---|---|
| Enabled | — | Disables GAN entirely if unchecked. |
| Require SSL | true | Incoming connections only. |
| Require Two Way Auth | **true** for new 8.3 installs | Requires manual certificate trust on both ends (see keystore paths below). Defaulted to false in 8.1; flipping this is one of the headline 8.1→8.3 upgrade gotchas. |
| Allow Java Serialization | false on fresh 8.3, **true** after an 8.1→8.3 upgrade | Legacy-interop only; disable once all peers are 8.3. |
| Data Channel Queue Size | 50 | Increase for high-throughput production GANs. |
| Data Channel Thread Pool Max Size | 100 | As above. |
| Websocket Idle Timeout | — | Must exceed configured ping rates. |
| Temp File Max Retention Age | — | 0 disables cleanup. |
| Proxy Service Call Intercept | false | Caches service-enumeration responses on a proxy Gateway. |

**Security:** Allow Incoming Connections (bool); **Connection Policy** = `ApprovedOnly` (default — manual approval per connection), `Unrestricted`, or `SpecifiedList` (comma-separated allowed Gateway names); Allowed Proxy Hops.

**Incoming Connection Settings:** Ping Rate (default 5000ms), Incoming Ping Timeout (default 300ms), Missed Pings (default 12).

Certificates: default metro keystore at `data/config/local/ignition/gateway-network/keystore` (password `metro`, alias `metro-key`); trusted-cert import target: `data/config/local/ignition/gateway-network/client/security/pki/trusted/certs`.

### What travels over the GAN

Remote Realtime and Historical Tag Providers, Remote Alarming/Notification, EAM message and file transfer + connection-availability monitoring (alarms + system tags on loss), and general Gateway Network proxying. Port: **8088 without SSL, 8060 with SSL** (`metroSSLPort` in `gateway.xml`), always initiated *from backup to master* for redundancy traffic specifically.

### Queue management and proxy rules

The Connections page (Network > Gateway Network > Connections) has tabs for **Outgoing Connections**, **Incoming Connections**, **Remote Gateways**, **Queue Management** (per-connection queue settings, adjustable message capacity), and **Proxy Rules** (rules for which Gateways a given node will proxy traffic to/from, subject to the `-Dignition.gan.maxproxydepth` hop limit, default 2 hops).

### Security Zones / Service Security

Security Zones can restrict which parts of a Gateway are reachable via GAN. In 8.3, **Service Security settings moved into Security Zone configuration** (accessed via a zone's three-dot menu > Manage Policy) rather than being a separate top-level page as in 8.1.

---

## Redundancy

A 2-node **master/backup** model. The master normally owns the canonical configuration and replicates it to the backup; **Backup Version** configuration overrides let a specific resource differ intentionally between the two nodes (three-dot menu > **Add Backup Version** on any resource).

### Node roles and communication

- **Mode**: Independent (no redundancy), Master, or Backup — set per-node; there should be exactly one of each in a pair.
- Communication is **always backup → master**, over the Gateway Network (port 8088 without SSL / 8060 with SSL on the master), so the master's firewall must allow inbound TCP on that port.
- Disabling Gateway Network on the master disables it on the backup too; both nodes' **Enabled** setting must be re-checked to restore the link (the General GAN settings page *can* be edited from a backup node for this purpose — other GAN general settings on the backup are overwritten by master settings on next sync).

### Configuration sync vs. runtime state sync

- **Configuration**: queued on the master, pulled by backup on connect (or full backup transfer if too far out of sync); either transfer type triggers a **soft reboot**.
- **Runtime state** (e.g. current alarm states): synced differentially, does **not** trigger a restart; a full state transfer happens on first connection or after falling too far behind.
- **Conflict resolution**: on reconnect, the backup drops conflicting data in favor of the master's — unless **Use Active Uptime to Resolve Conflicts** is enabled, in which case whichever node has the longer active-uptime wins (which can mean the master overwrites its own data with the backup's).

### Failover behavior

- **Standby Activity Level**: **Cold** (connects to OPC servers but doesn't subscribe tags — slower failover, less device/network load) or **Warm** (runs fully except logging/writing — faster failover).
- **Recovery Mode** (master-only setting): **Automatic** (master reclaims control immediately when it comes back) or **Manual** (backup stays active until a user forces a switchover — the documented setting to use during a redundant-pair upgrade).
- **Startup Connection Allowance** (default 30000ms): the window a node waits at startup before deciding active/standby; setting this too low defeats Manual recovery mode, since the master will always claim active status before even attempting to connect to the backup.
- **Historical Logging** — two modes for the backup: **Full** (backup logs directly to DB while active, risking duplicate entries if the master was merely unreachable rather than actually down) or **Partial** (backup caches history locally until reconnecting with master, then forwards only the data collected during confirmed master downtime — avoids duplicates at the cost of delayed availability).
- **Client Failover** is allowed **across differing platform versions**, specifically so clients stay connected to at least one node during a redundant-pair upgrade.
- The **Designer can never be opened against a Backup node**, even if the Master is offline.

### What is/isn't replicated

Replicated: full resource configuration (subject to core/local collection rules — see Configuration model), runtime alarm/session state (differentially). **Not replicated**: anything in `data/local` scoped strictly to one machine (certs, UUID), Deployment Mode selection in `ignition.conf` (must be manually matched on both nodes — see Gotchas), and — per the Backup & Restore page — Modules, license grants, and redundancy settings themselves are never touched by a `.gwbk` restore on an existing Gateway.

### Database considerations for redundancy

- Database connections used by both redundancy nodes should point at the **same physical database** (single shared server) or a properly **clustered/replicated** set, since both master and (in Full history mode) backup write concurrently.
- **Failover Data Source** setting on a database connection provides connection-level failover independent of Ignition redundancy.
- **History Mode** (per the Backup Node Settings table above) directly interacts with database load/consistency during split-brain windows.

---

## Store and Forward

Store and Forward (S&F) is the reliability layer under Tag History, Alarming, Auditing, Scripting, SECS/GEM, and Transaction Groups (SQL Bridge) — anything writing to a database goes through it. **An S&F engine is automatically created per Database Connection.**

### Data flow

1. Data generated by a subsystem → placed in an **in-memory buffer**.
2. If not drained per the Store Settings (Time Threshold, Data Threshold, Batch Size), it's written to the **local disk cache**.
3. A data sink pulls from disk cache then memory buffer, at the configured **Forward Rate**.
4. On forward failure, data returns to buffer/cache; repeated failures **quarantine** the data.
5. Quarantined data is manually managed (retry, delete, export) from the Gateway.

### 8.3 change: multi-threaded engine

**"The Store and Forward engine is multi-threaded, meaning the engine can take advantage of more than one of [the connection pool's 8 default] connections at a time."** Up to **6 data types** (Alarming, Auditing, Scripting, SECS/GEM, Tag history, Transaction Group) can store/forward concurrently without blocking each other — a change from 8.1's single-threaded-per-connection model. A legacy-emulation escape hatch exists: `-Dignition.sf.legacy.forwarderThreads=true` forces the old single-connection-at-a-time behavior for constrained hardware.

### Engine tuning (per Database Connection: Platform > System > Store & Forward > Edit)

**Engine Settings**: Forward Rate (ms, default 1000), Schedule Pattern (comma-separated time ranges, e.g. `9:00-15:00`).

**Store Settings** (memory → disk threshold): Time Threshold (ms, default 30000), Data Threshold (default 10000), Batch Size (default 10000).

**Maintenance Settings** (primary/secondary store caps): Maintenance **Value** (0 = unlimited, default 0 — note this default changed from 8.1's finite "Max Records"), Maintenance **Type** (`TIME_DURATION`/`COUNT`/`FILE_SIZE`, default `COUNT`), Maintenance **Action** (`EVICT_OLDEST_DATA` or `PREVENT_NEW_DATA`, default `PREVENT_NEW_DATA`).

**Advanced Settings**: Forwarding Policy (`ALL`/`PRIMARY_ONLY`/`SECONDARY_ONLY`, default `ALL`), Engine Scan Rate (ms, default 100).

### Quarantine

Quarantined data is held **indefinitely** until manually resolved. Per-record or bulk (checkbox-select) actions: **Retry**, **Delete**, **Export** (downloads as JSON — a change from **8.1's XML quarantine export format**; 8.1 quarantine exports cannot be imported into 8.3). Common root cause: invalid destination-table schema.

### Disk cache management

- **Archive Disk Cache**: locks and shuts down the active cache, moves it to `data/var/ignition/store-forward/.archives/{database name}_{timestamp}`, then starts a fresh cache — incoming data may be blocked/lost during the operation.
- **Load Disk Cache**: overwrites the current cache with a previously archived one (choose from multiple archives if present).

### Legacy data conversion (8.1→8.3)

On upgrade, S&F automatically converts old serialized data at engine startup; any data left unconverted lands as an `.hsql` file that must be manually relocated to `data/local/store-forward/quarantined-databases/`.

---

## Licensing, activation, editions

### Licensing model

Ignition licenses the **server**, not clients — unlimited clients/tags/projects per license; you pay for which modules/suites are enabled. Built-in **Trial mode**: 2 hours per reset, unlimited resets, only unlicensed modules affected (Gateway Webpage and Designer are never trial-gated); different runtimes surface the trial timer differently (Gateway banner w/ Reset Trial button, Vision Client banner — Vision requires logout/login to fully re-arm after reset, Perspective Session Status bar, Designer lower-right corner).

### Standard (six-character key) licenses

- **Online activation**: Platform > System > Licensing > Activate a License, enter key, choose Online — requires outbound TCP to `https://api.inductiveautomation.com/activation/activate`.
- **Offline activation**: generates `activation_message.txt` → upload at `https://links.inductiveautomation.com/activation` on a networked machine → download `license.ipl` → upload back on the offline Gateway.
- Unactivating and reusing a key to move it between Gateways is fully supported (see Reference tables / gwcmd `-u`/`-w` flags).

### Leased licenses (eight-character key)

Used for containerized/cloud deployments (Docker, Kubernetes) and Maker Edition. Require both an 8-char **license key** and a long **activation token**. Activation endpoints: `https://licensing.inductiveautomation.com/v1-activation/leased/activate` and `.../v1-activation/leased/nonce` (HTTP POST, whitelist both for outbound-only environments). Multiple leased keys can be supplied comma-delimited via `IGNITION_LICENSE_KEY` / `IGNITION_ACTIVATION_TOKEN` env vars, and changes to those env vars **update the running leased-activation configuration post-commissioning** (not just at first boot). Two dedicated JVM parameters govern session termination behavior on shutdown: `-Dignition.license.leased-activation-session-termination-timeout-ms` (default 7.5s) and `-Dignition.license.leased-activation-terminate-sessions-on-shutdown` (default false) — relevant because leased sessions must be explicitly returned to the activation server or they leak until timeout.

### Multiple licenses / Effective vs. Applied

A Gateway can hold multiple license keys (e.g. one platform license plus third-party module licenses), but **only one license with a platform grant per Gateway** — activating a second platform-bearing license overwrites the first. **Applied Licenses** = what's been activated; **Effective Licenses** = the resulting summary of which modules are actually active (accounting for multiple licenses and, for Edge, "synthetic" product→module translation) — a module only appears here if it's also installed.

### Solution Suites

Pre-packaged module bundles: **Application Building** (Perspective + Reporting), **Industrial Historian** (Historian + SQL Historian), **Enterprise Integration** (MongoDB, Kafka, MQTT Transmission, MQTT Engine), **Alarm Management** (Alarm/Voice/SMS/Twilio Notification), **DataOps** (SQL Bridge, Web Dev, Event Streams). Individual modules within a suite can't be removed but more can be layered on top; Upgrade Protection auto-adds new suite modules at no extra cost.

### Emergency Activation Mode

A degraded/limited-functionality mode the Gateway enters when licensing/activation state can't be verified — the docs frame this as a disaster-recovery trigger with a documented "Quick Disaster Recovery Plan" / "Emergency Restore Steps" flow (exact restore steps not captured in this pass — consult the live Emergency Activation page for the step list).

### Editions (Standard / Edge / Maker / Cloud)

The dedicated per-edition pages (`other-editions/...`) were outside this doc's crawled page set, but cross-references establish:
- **Standard Edition** — unlimited commercial edition.
- **Edge Edition** — lightweight, edge-of-network installs; shown distinctly (green icon) on the Gateway Network Diagram; supported by Redundancy.
- **Maker Edition** — free, non-commercial, always uses leased (8-char) licensing, requires the free key+token pair from account.inductiveautomation.com even for otherwise-free use.
- **Cloud Edition** — uses ports 80/443 by default for Gateway access rather than 8088/8043 (per the Port Reference table); shown distinctly (blue icon) on the Gateway Network Diagram; supported by Redundancy under standard/leased licensing.
- `IGNITION_EDITION` env var / `-Dedition=standard|edge|maker` JVM property select edition at commissioning time; changing edition on an already-licensed Gateway can invalidate the license — unactivate first.

---

## Audit log and profiles

Auditing automatically records actions (tag writes, user auth, config changes, etc.) into a SQL table, gated by two independent switches: an **Audit Profile** must exist, and auditing must be **enabled** for the specific scope (Gateway-scoped actions, and/or per-project).

### Profile types

- **Database Audit Profile**: Name, Description, Retention (days, default 90, ≤0 disables pruning), Enabled; Database Settings: target Database connection, Auto Create (default true — auto-verifies/creates schema), Pruning Enabled (default **false** — retention is ignored unless this is on), Table Name (default `AUDIT_EVENTS`).
- **Internal Audit Profile**: stores audit records without an external DB — same Name/Description/Retention/Enabled properties, backed by Ignition's internal storage.
- **Remote Gateway Audit Profile**: forwards audit events to another Gateway's own Audit Profile over the GAN.

Enabling requires two separate steps documented on the page: **Enabling Auditing for Gateway-Scoped Actions** (system-level) and **Enabling Auditing in a Project** (per-project), independently.

### Querying the log

Three supported access paths: Vision/Perspective table components bound to the audit table (Perspective via a Named Query or the `system.util.queryAuditLog` scripting function), the Gateway's own **Database Query Browser**, or directly on the **Gateway** UI's audit log viewer.

### 8.3 schema note

Table/column names are **lowercase** in 8.3 (`audit_events`, `audit_events_id`) vs. 8.1's uppercase (`AUDIT_EVENTS`, `AUDIT_EVENTS_ID`) — a documented gotcha for hand-written SQL querying the audit table across versions; in-place upgraded profiles keep working, only *new* 8.3 installs pointed at an old-schema DB are affected. On Oracle specifically, watch for the `audit_events_seq` sequence if manually dropping/renaming the table.

### Auditing Actions Reference (selected categories)

Gateway Audit Actions are grouped by subsystem: Project System, Gateway (General/Restore), Licensing Changes, Redundancy, Web Server Page, Gateway Network, Email Settings, Audit Profile (self-referential), User Sources, Service Security, Identity Providers, Security Levels/Zones, Database Connections/Drivers, Store and Forward, Alarming (General/Journal/Notification), Schedules, Tags (Realtime/Historical), OPC Client/UA Device/Server settings, Enterprise Administration (+ sub-categories for Event Thresholds, Controller/Agent Settings, Agent Management, License Management, Agent Tasks), Sequential Function Charts, and manual record addition. Separately: **Perspective Auditing Actions**, **Vision Auditing Actions** (Tags, Tag Writes, Component DB Writes, User Login/Logout, Database Query Browser, Scripting), **Designer** (Login/Closing, Database Query Browser), **Alarm Notification** (attempts), and **Reporting Module** (report execution).

---

## Launchers and Workstation

Three launcher applications, sharing common infrastructure: **Designer Launcher**, **Vision Client Launcher**, **Perspective Workstation** (standalone desktop Perspective runtime). An "application" within a launcher = a saved (Gateway, project) pairing.

### Settings storage

Per-user JSON config files at:
- Linux/Mac: `~/.ignition/clientlauncher-data`
- Windows: `C:\Users\<username>\.ignition\clientlauncher-data` (or under `AppData\Roaming\Inductive Automation\` for all-users installs)

Notable JSON-only (no GUI equivalent) settings: `lock.configuration` (locks the Settings menu and app management from end users — also suppresses saving the Gateway address on deep-link launches), `version.updates.prompt` / `version.updates.revision.diff` (controls the Launcher-vs-Gateway version-mismatch upgrade nag; default diff threshold 3 minor revisions), `trust.store` (`system`/`user`/`jvm` — maps to OS keystores on Windows/Mac, `ca-certificates` on Linux, or Java's internal cacerts; default `jvm`), and `allow.uri.schemes` (Workstation-only — whitelists which deep-link URI protocols the OS will hand to Workstation: `perspective`, `vision`, `designer`, `tel`, `sms`, `mailto`).

Common GUI-exposed property settings (General tab, shared across all three launchers): Default Application, Logging Level, Multicast Address/Port (Gateway discovery), Auto Exit on Launch. Designer/Vision-specific Default settings: Timeout, Retries (`-1` = infinite, `0` = none, N = N retries), Initial/Max Heap, JVM Arguments (`-D...;-D...`).

### Deep links and file associations (new in 8.3)

Launch without opening the launcher UI first, if URL-protocol/file-extension association was enabled at launcher install time:
```
designer://Gateway            # choose project interactively
designer://Gateway/projectName
vision://Gateway/projectName
perspective://Gateway/projectName
```
HTTPS is assumed by default — append `?insecure=true` for HTTP. Query-arg support: `insecure` (all launchers); Workstation-only `mode=windowed|fullscreen|kiosk` and `display${index}`; Vision-only `mode=windowed|fullscreen`, `screen=<index>`, and Vision Client Tag overrides via `tag.${urlEncodedName}=${urlEncodedValue}`. File Associations use per-launcher-type JSON files (`.perspective`, `.vision`, `.designer` extensions) as an alternative trigger mechanism.

First contact with an unknown Gateway via deep link shows a **Trust and Launch** warning; trusted addresses are recorded in `.ignition/clientlauncher-data/shared/known-gateways.txt` (shared across all three launchers). Set `IGNITION_KNOWN_GATEWAYS=all` to blanket-trust and suppress the prompt (e.g. for kiosk provisioning).

### Certificates

Trust store selection (`trust.store`) determines which OS/JVM certificate store the launcher uses at runtime; changing it requires the launcher to be closed, a JSON edit, and (on Windows/Mac) reinstalling the cert into the OS-native store, or (Linux, `ca-certificates` value) `sudo apt-get install -y ca-certificates && sudo cp local-ca.crt /usr/local/share/ca-certificates && sudo update-ca-certificates`. `ca-certificates` mode additionally supports `-Dignition.net.ssl.certDir` (OpenSSL-style cert directory) and `-Dignition.net.ssl.pemBundle` (PEM bundle) system properties.

### Pre-configured / deployed launchers

Launchers can be pre-configured (embed a known application/Gateway, lock configuration) and packaged as a ZIP for mass deployment, with dedicated guidance on redundancy behavior, CA-signed vs. self-signed cert handling, and locking the configuration so end users can't add/remove applications.

---

## Reference tables

### Gateway Port Reference

**Ignition ports:**

| Port | Direction | Protocol | Configurable | Purpose |
|---|---|---|---|---|
| 80 | In | TCP | Yes | HTTP — **Cloud Edition** default |
| 443 | In | TCP | Yes | HTTPS — **Cloud Edition** default |
| 1883 | In | TCP | No | MQTT (unencrypted) |
| 4096 | In | TCP | Yes | Legacy OPC UA server port (7.9 and earlier; used transiently when upgrading from Ignition 7) |
| 4445 | Out | UDP/bcast | Yes | Multicast Gateway-discovery send |
| 4446 | In | UDP/bcast | Yes | Multicast Gateway-discovery receive |
| 6501 | In | TCP | No | Vision Local Client Fallback |
| 8043 | In | TCP | Yes | Gateway HTTPS |
| 8060 | In | TCP | Yes | Gateway Network SSL (`metroSSLPort`) |
| 8088 | In | TCP | Yes | Gateway HTTP; also GAN non-SSL |
| 8883 | In | TCP | No | MQTT SSL/TLS |
| 17341 | Out | UDP | No | SMS alarming send |
| 17342 | In | UDP | No | SMS alarming receive |
| 62541 | In | TCP | Yes | OPC UA server (default) |

**Common third-party/device ports** (verify against each vendor's docs): 102 (Siemens S7), 135 (DCOM/legacy OPC-DA), 389 (AD), 465 (SMTP over TLS — alarming), 502 (Modbus), 1433 (MSSQL), 1521 (Oracle), 2222 (Allen-Bradley EtherNet/IP I/O), 3050 (Firebird), 3306 (MySQL), 5060 (SIP), 5432 (PostgreSQL), 8000 (SIP RTP), 9600 (Omron FINS TCP+UDP), 44818 (Allen-Bradley EtherNet/IP symbolic), 47808 (BACnet), 49320 (Kepware), 50000 (IBM DB2).

**Activation URLs:** 6-char keys → `https://api.inductiveautomation.com/activation/activate`; 8-char/leased → `https://licensing.inductiveautomation.com/v1-activation/leased/{activate,nonce}`.

### Platform environment variables (subset — see appendix page for full authoritative list)

| Variable | Purpose |
|---|---|
| `TZ` | IANA timezone name. |
| `ACCEPT_IGNITION_EULA=Y` | Auto-accept EULA (headless/Docker). |
| `GATEWAY_ADMIN_USERNAME` / `GATEWAY_ADMIN_PASSWORD` | Initial commissioning admin credentials. |
| `GATEWAY_HTTP_PORT` / `GATEWAY_HTTPS_PORT` / `GATEWAY_GAN_PORT` | Default 8088 / 8043 / 8060. |
| `IGNITION_EDITION` | `standard` / `edge` / `maker`. |
| `IGNITION_LICENSE_KEY` / `IGNITION_ACTIVATION_TOKEN` | Leased licensing — comma-delimited for multiple; **live-updates the running config post-commissioning**, not just at first boot. |
| `GATEWAY_NETWORK_#_HOST/PORT/PINGRATE/PINGMAXMISSED/ENABLED/ENABLESSL/WEBSOCKETTIMEOUT/DESCRIPTION` | Per-connection outgoing GAN definition, `#` = index. |
| `GATEWAY_NETWORK_ENABLED/REQUIRESSL/REQUIRETWOWAYAUTH/SENDTHREADS/RECEIVETHREADS/RECEIVEMAX/ALLOWINCOMING/SECURITYPOLICY/WHITELIST/ALLOWEDPROXYHOPS/WEBSOCKETSESSIONIDLETIMEOUT/ALLOWJAVASERIALIZATION` | Global GAN settings — env-var mirror of the General Settings UI page. |
| `EAM_SETUP_INSTALLSELECTION` / `EAM_AGENT_*` / `EAM_CONTROLLER_*` | EAM agent/controller bootstrap. |
| `GATEWAY_MODULES_ENABLED` | Comma-delimited module allow-list; critical in Docker for restricting which modules survive container re-creation. |
| `DISABLE_QUICKSTART` | Skip the Quick Start prompt. |
| `ACCEPT_MODULE_LICENSES` / `ACCEPT_MODULE_CERTS` | Auto-accept third-party module EULAs/certs on startup. |
| `IGNITION_ROOT_KEY_PASSWORD` / `_FILE` | Custom root/encryption key for Gateway startup. |
| Any var + `_FILE` suffix | Loads the value from a file path instead of the raw env value — for keeping secrets out of `docker inspect`. |

Setting instructions per-OS are documented (Windows: System Properties > Environment Variables; Mac: `export VAR=value`; Linux: `/etc/environment` for system-wide).

**Docker-only env vars:** `GATEWAY_RESTORE_DISABLED` (disable restored `.gwbk` resources on startup), `IGNITION_UID`/`IGNITION_GID` (run as non-root, auto-`chown`s the install on startup).

### Gateway folder structure (see Configuration model above for the full annotated table)

Root data dirs: `data/config/resources/{external,core,local,<mode>}`, `data/config/{ignition,<module-id>}`, `data/config/local/{ignition,<module-id>}`, `data/var/{ignition,<module-id>}`, `data/projects`.

### gwcmd (Gateway Command-line Utility) — full option table

Located at the install root; requires admin/elevated shell, and must be run from the install directory.

| Flag | Purpose |
|---|---|
| `-a, --activate <key>` | Generate `activation_request.txt` for a 6-char key (8-char keys can't activate via gwcmd). |
| `-b, --backup <path>` | Download a `.gwbk` to the given path. |
| `-c, --clearks` | Clear SSL/TLS keystore setup; immediately drops the SSL connector. |
| `-d, --disabled` | With `--restore`: disable all restored items. |
| `-e, --exportks <path>` | Export SSL keystore as PKCS#12. |
| `-f, --exportpk <path>` | Export SSL private key as PEM. |
| `-g, --reloadks` | Reload keystore from disk (applies to new connections). |
| `-h, --help` | Usage. |
| `-i, --info` | Server status/port info (Gateway must be running). |
| `-k, --port <port>` | Change HTTP port. |
| `-l, --sslport <port>` | Change HTTPS port. |
| `-m, --skip-gateway-contact` | With `--restore`: stage the restore without contacting a running Gateway. |
| `-n, --nocrypt` | With export-private-key: don't encrypt the exported key. |
| `-o, --name <name>` | Override Gateway name during restore; combine with `-y` to skip the name-override prompt. |
| `-p, --passwd` | Trigger password reset (temp user, requires restart to take effect). |
| `-r, --restart` | Restart the Gateway. |
| `-s, --restore <path>` | Restore from a `.gwbk`. |
| `-t, --tdump` | Print a thread dump to stdout. |
| `-u, --unactivate` | Generate `unactivation_message.txt` (primary), or `-u XXX-XXX` for a 6-char supplemental license's `unactivation_request.txt`. |
| `-w, --uselicense <license.ipl>` | Apply a downloaded offline-activation license file. |
| `-y, --promptyes` | Auto-answer yes to all prompts. |
| `-z, --timeout <seconds>` | Backup-generation timeout, default 60s. |

### Docker module identifiers (subset — see appendix page for the full table)

Format: `com.inductiveautomation.<module>`. Examples: `alarm-notification`, `opcua`, `opcua.drivers.{ablegacy,bacnet,dnp3,dnp3v2,iec61850,logix,micro800,mitsubishi,modbus,omron,siemens,siemens-symbolic}`, `eam`, `eventstream`, `historian`, `historian.sql`, `connectors.kafka`, `connectors.mongodb`, `perspective`, `reporting`, `sfc`, `sms-notification`, `sqlbridge`, `symbol-factory`, `opcua.drivers.tcpudp`, `vision`, `phone-notification`, `webdev`, `jdbc.{postgresql,mariadb,mssql}`. Solution Suite identifiers: `suite.{application,historian,dataops,enterprise,alarms}`. Built-in modules live at `user-lib/modules`; third-party modules save to `data/local/modl` (path overridable via `-Dignition.gateway.externalModulesFolder`).

### Ignition Database Table Reference (condensed)

**Tag History (external SQL historian) — 8 tables:**
| Table | Purpose |
|---|---|
| `sqlt_data_X_X` | Raw tag values, partitioned per driver-id/year/month. |
| `sqlth_1_data` | Raw tag values when partitioning is disabled. |
| `sqlth_te` | Tag metadata; new row per historical-config change (rename, datatype change, etc.) — old rows "retire." |
| `sqlth_scinfo` | Tag Group info (execution rate, driver). |
| `sqlth_sce` | Tag Group execution start/end windows. |
| `sqlth_partitions` | Start/end times per `sqlt_data` partition table. |
| `sqlth_drv` | Historian "driver" (Gateway system-name + Tag Provider) registry — **the table affected by system-name changes**, see Gotchas. |
| `sqlth_annotations` | User-created annotations on historical data (e.g. from Power Chart). |

**Internal History Provider (SQLite, `data/var/com.inductiveautomation.historian/internalhistorian`) — 5 tables:** `annotations`, `schema_info`, `tagdata` (values + sync id), `tagdetails` (tag registry, no scan-class tracking), `tagproperties` (per-tag datatype/interpolation etc.).

**Alarm Journal — 2 tables:** `alarm_events` (one row per state change: active/cleared/acknowledged), `alarm_events_data` (one row per custom property per event).

**Authentication (Internal User Source) — 6 tables:** `scada_users`, `scada_roles`, `scada_user_rl` (user↔role), `scada_user_sa` (schedule overrides), `scada_user_ci` (contact info), `scada_user_ex` (module-specific extra properties, e.g. Voice Notification PINs).

**Audit Log — 1 table:** `audit_events` — columns `audit_events_id` (PK), `event_timestamp`, `actor`, `actor_host`, `action`, `action_target`, `action_value`, `status_code` (bitmask), `originating_system`, `originating_context` (1=Gateway, 2=Designer, 4=Client). **All lowercase in 8.3** (was uppercase in 8.1). Oracle uses sequence `audit_events_seq`.

All table/column names above are the *defaults* — most are renameable in their respective profile/provider settings.

### Config file locations, one-line summary

| File | Path | Governs |
|---|---|---|
| `ignition.conf` | `data/ignition.conf` | JVM/wrapper args, `wrapper.java.additional.#` system properties, deployment mode selection |
| `gateway.xml` | `data/gateway.xml` | Core networking properties (ports, public address, cipher lists, `config.idb` autobackup) |
| `logback.xml` | `data/logback.xml` | Internal Gateway log-database maintenance (entryLimit, vacuum frequency, max DB size) and logger routing |
| `web.xml` | `<install>/webserver/webapps/main/WEB-INF/web.xml` | Jetty servlet container — session timeout/cookies, filters, servlet mappings, multipart upload limits (`max-file-size` default 128MB as of 8.3.9, was 20MB before; `max-request-size` default 418MB; `file-size-threshold` default 1MB) |

---

## Gotchas and 8.3 notes

Consolidated, explicitly version-tagged changes pulled from across the doc set. **NEW** = introduced in 8.3, **CHANGED** = behavior/default differs from 8.1, **REMOVED** = no longer available in 8.3.

**Configuration model**
- **CHANGED** — Gateway configuration moved from the internal database (IDB) to a file-based resource-collection system (system/external/core/local + Deployment Modes). The IDB is retained post-upgrade but unused.
- **NEW** — Gateway Deployment Modes, switched only via `-Dignition.config.mode=<name>` in `ignition.conf` + restart; **not synced between redundant nodes** — must be manually matched on both, or failover can activate the wrong resource set.
- **CHANGED** — `config.idb` autobackup default: `localdb.autobackup.count` default is now **0** (disabled) as of 8.3.8+, was 5 in 8.1.
- **CHANGED** — Internal-database VACUUM-on-startup is now disabled by default (`-Dignition.skipConfigDbVacuum=false` to re-enable) as of 8.3.8, since the IDB is no longer load-bearing.
- **CHANGED** — Perspective custom theme structure requires a `config.json` (`isPrivate`, `entrypoint`) per theme; old flat-file themes migrate automatically but originals must be reconciled from a `.migrated-themes-TIMESTAMP` backup folder if imports don't resolve.
- **CHANGED** — Tag JSON definitions moved to longer resource-collection paths (`data/config/resources/core/ignition/tag-definition/...`) — Windows 255-char path-limit risk.

**Gateway Network**
- **CHANGED** — Serialization moved Java serialization → **Protobuf**. 8.3 cannot store data to 8.1 over GAN; upgrade order matters (data-hosting Gateway first).
- **CHANGED** — **Require Two-Way Authentication now defaults to `true`** for new installs (was `false` in 8.1) — mutual cert trust required or connections silently fail post-upgrade.
- **CHANGED** — `gateway.maxThreads` **no longer applies to the Gateway Network** as of 8.3.2 — GAN now has its own dedicated thread pool, fixing a class of Gateway-unresponsive-under-GAN-load issues.
- **TEMPORARY, upgrade-only** — `Allow Java Serialization` auto-enables during 8.1→8.3 upgrade/restore for interop; disable once fully migrated.

**Store and Forward**
- **CHANGED** — Engine is now **multi-threaded** across 6 data types (previously serialized through fewer connections); legacy single-threaded behavior recoverable via `-Dignition.sf.legacy.forwarderThreads=true`.
- **CHANGED** — **Primary Store Maintenance Value defaults to 0 (unlimited)** post-upgrade, vs. 8.1's finite "Max Records" default — disk usage should be actively monitored post-upgrade if this wasn't explicitly re-tuned.
- **CHANGED** — Quarantine exports are now **JSON**, not XML; 8.1 exports are not importable into 8.3.

**Licensing**
- **CHANGED** — Tag Historian license item replaced by **Historian Core** + **SQL Historian** items; Serial Support Client/Gateway bundled into the platform; Web Browser module bundled into Vision (now under Misc components).
- **CHANGED** — Individual JDBC drivers now appear on the Modules page, licensed as "Free" rather than "Activated."

**Security / Auth**
- **CHANGED** — Gateway webpages now require roles/permissions explicitly; **8.1 permissions do not roll forward** and must be reassigned post-upgrade.
- **CHANGED** — Identity Provider JSON export format changed; 8.1 IdP JSON is not importable into 8.3.
- **CHANGED** — Service Security settings moved **into** Security Zone configuration (previously a separate settings surface).
- **CHANGED** — Internal/AD-Internal-Hybrid User Sources can no longer contain duplicate usernames; migration **skips** (does not corrupt) User Sources with duplicates — must be manually deduped pre-upgrade.
- **NEW** — Secrets Management system (encrypt credentials/tokens/keys) + a dedicated Secrets Management Key CLI tool.

**OPC UA**
- **CHANGED** — Now OPC UA **1.05**; new certs generated on upgrade (both directions need re-trust); **anonymous clients lose write/call access by default** — only browse/read — any device/provider lacking explicit role mappings needs those restored manually if anonymous write/call was relied on.

**Modules / platform**
- **REMOVED** — **Hot swapping modules.** Every module install/upgrade now requires a Gateway restart.
- **CHANGED** — MariaDB/MSSQL/PostgreSQL JDBC drivers are now delivered as **modules**, not bundled — Docker `GATEWAY_MODULES_ENABLED` allow-lists from 8.1 need the new module identifiers added post-upgrade.
- **REMOVED** — EAM **Agent Recovery** task.
- **BROKEN, workaround exists** — EAM Remote Upgrade cannot cross 8.1.x→8.3.x on Apple M-series Macs (arch change); do one in-place upgrade to 8.3.0 manually, then EAM remote upgrades resume working.

**Scripting**
- **NEW** namespaces: `system.vision.*` (replaces much of `system.file`, `system.gui`, `system.nav`, `system.net`, `system.print`, `system.security`, `system.util`) and `system.historian.*` (replaces `system.tag.browseHistoricalTags`→`browse`, `queryTagHistory`→`queryRawPoints`, `queryTagCalculations`→`queryAggregatedPoints`, `queryAnnotations`, `storeTagHistory`→`storeDataPoints`, `storeAnnotations`, `deleteAnnotations`; `queryTagDensity` has **no replacement**).
- **CHANGED** `system.db.*` overhaul: `clearAllNamedQueryCaches`/`clearNamedQueryCache`→`clearCache`; `dateFormat`→`system.date.format`; `refresh`→`system.vision.refreshBinding`; `runNamedQuery`→`execQuery`/`execUpdate`; `runQuery`→`execQuery`/`runPrepQuery`; `runScalarQuery`→`execScalar`/`runScalarPrepQuery`; `runSFNamedQuery`→`execQuery`; `runSFUpdateQuery`→`execUpdateAsync`/`runSFPrepUpdate`; `runUpdateQuery`→`execUpdate`/`runPrepUpdate`.
- **CHANGED** `system.net.http*` functions deprecated in favor of `system.net.httpClient`.
- **DEPRECATED, no replacement**: `system.gui.convertPointToScreen`, `system.gui.getQuality`, `system.dataset.toPyDataSet` (PyDataset wrapping no longer needed); `system.dataset.toDataSet` (8.1) collapses to a single-syntax `system.dataset.toDataset` in 8.3.
- **DEPRECATED** expression function `forceQuality` → use `qualifiedValue`.

**Historian**
- **NEW** — **Core Historian** (QuestDB-backed, auto-partitioning, skips Store & Forward entirely when there are no pending writes).
- **CHANGED** — Historical path syntax for non-SQL historians: `drv:` → `sys:`/`prov:` (SQL Historian keeps `drv:` unchanged, and 8.1 `drv:` paths still work in 8.3 generally).
- **DEPRECATED** — Custom Tag History Aggregates (tied to legacy `queryTagHistory`/`queryTagCalculations`).

**Perspective**
- **CHANGED** — File Upload component capped at **20MB** regardless of component `fileSizeLimit`, overridable via `web.xml`'s `max-file-size` (itself defaulting to 128MB as of 8.3.9 — was 20MB in earlier 8.3 releases — this is the *global* Jetty-level cap, separate from the component property).
- **CHANGED** — Minimum supported browser versions changed from 8.1 — verify against current Browser Version Requirements before upgrading.
- **DEPRECATED** — Table component's `pager.initialOption` → use `option`.
- **NEW** components: Drawing, Form; **NEW** Offline Mode for Perspective Mobile App.

**Designer**
- **DEPRECATED** — Project Properties > Perspective > General > Identity Provider setting → use Project Properties > Project > General > Identity Provider.

**Launchers**
- **NEW** — Deep Links (`designer://`, `vision://`, `perspective://`) and JSON File Associations (`.designer`/`.vision`/`.perspective`).
- **COMPAT NOTE** — 8.3 launchers/Workstation are backward-compatible with 8.1 Gateways; **8.1 launchers/Workstation are NOT forward-compatible with 8.3** Gateways.

**Tags**
- **CHANGED** — Tag Browser's `Alarms` folder replaced by **Alarm Metrics** (old `Alarms` folder still works for existing scripts/bindings but is deprecated).
- **NEW** — `ModuleVersions` System Tags folder (EAM controller module-version monitoring).

**Call/notification scripting**
- **CHANGED** — VOIP call-script locale serialization switched from Apache Commons Locale serialization to Java's built-in language tags — can cause **migration name collisions** where two distinct 8.1 locales resolve to the same 8.3 language tag (e.g. `nn_NO_NY` and `nn_NO` both → `nn-NO`); one record fails to migrate in that case.

**Redundancy**
- No structural change documented in this crawl beyond the Deployment Mode non-sync caveat above and the multi-version client-failover behavior (explicitly designed to ease redundant-pair upgrades).
