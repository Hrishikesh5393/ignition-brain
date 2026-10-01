# Ignition 8.3 — what changed from 8.1

> **Sources.** Everything below is taken from the live Inductive Automation
> user manual at `https://www.docs.inductiveautomation.com/docs/8.3/...`,
> its 8.1 counterpart at `/docs/8.1/...`, and the Deprecated manual at
> `/docs/deprecated/...`. Primary pages: `new-in-this-version`,
> `getting-started/installing-and-upgrading/ignition-8-upgrade-guide/81to83-upgrade-guide`,
> `platform/gateway/web-interface/platform/gateway-deployment-modes`,
> `platform/gateway/openapi`, `platform/security/secrets-management`,
> `platform/security/api-keys`, `ignition-modules/event-streams`,
> `ignition-modules/tag-historian/tag-history-providers`,
> `platform/store-and-forward`, `platform/gateway-network`,
> `appendix/reference-pages/gateway-folder-structure`,
> `tutorials/version-control-guide`, `other-editions/ignition-cloud-edition`.
> Docs snapshot taken 2026-09-22; latest release documented at that time is **8.3.9**.

---

## Executive summary

* **Gateway configuration left the internal database and became files on disk.**
  The version-control guide calls this out in so many words: *"One of the most
  transformative changes in Ignition 8.3 is the migration from a SQLite
  database-driven configuration to a file system based configuration."*
  Everything — database connections, device connections, tags, alarm pipelines,
  Gateway-scoped resources — now lives under `data/config`, human-readable and
  diffable.

* **Gateway Deployment Modes are the new environment story.** A Gateway can
  carry dev/staging/prod variants of the same resource and pick one at start-up
  via a Java parameter (`-Dignition.config.mode=<NAME>`). Resources resolve
  through a collection hierarchy: `system` → `external` → `core` → `{mode}`,
  plus a machine-specific `local` collection.

* **There is a real, documented Gateway REST API.** `/openapi` serves an
  interactive spec and `/openapi.json` the machine-readable one. Configuration
  resources are exposed under `/data/api/v1/resources`, with `/data/api/v1/sync`
  and `/data/api/v1/modes` alongside. This is the IaC / GitOps entry point.

* **API Keys are a first-class security object.** Created at
  **Platform > Security > API Keys**, passed as the `X-Ignition-API-Token`
  header, hashed at rest, shown exactly once.

* **The Tag Historian became "the Historian", and gained a new default engine.**
  The Core Historian (QuestDB-backed, formerly called the Power Historian)
  is embedded, partitioned, deduplicating, archiving, with native aggregation —
  and it **bypasses Store and Forward** when there is nothing pending.

* **Historical path syntax changed.** `drv:<gw>:<provider>` became
  `sys:<gw>:/prov:<provider>` for the Core Historian. SQL Historian still
  accepts the old `drv` form.

* **Tag history scripting moved namespace.** `system.tag.queryTagHistory` and
  seven siblings are deprecated in favour of `system.historian.*`.
  `system.tag.queryTagDensity` has **no replacement**.

* **Vision-only functions were collected under `system.vision`.** Functions
  from `system.gui`, `system.nav`, `system.file`, `system.net`, `system.print`,
  `system.security`, `system.util` and `system.dataset` were re-homed; the old
  names still work but are deprecated. `system.gui` and `system.nav` no longer
  exist as current namespaces at all.

* **Event Streams are a new project resource type** — a seven-stage
  source → encoder → filter → transform → buffer → handler → error-handler
  pipeline, with Kafka / HTTP / Tag / Event Listener sources.

* **Secrets Management ships in the platform.** Embedded secrets (encrypted by
  a Gateway key set) plus referenced secrets via Internal / Remote / File
  Secret Providers, a `root.json` + `kek.json` key hierarchy, an environment
  password, and a dedicated CLI tool.

* **Gateway pages are now permission-gated.** *"8.3 Gateway webpages now
  operate on a required role basis"* — and, critically, *"permissions granted
  in 8.1 will not automatically roll over into 8.3, and must be reassigned."*

* **Gateway Network moved from Java serialization to Protobuf.** Consequence:
  *"8.3 Gateways are not able to store data to 8.1 Gateways over the Gateway
  Network."* This dictates upgrade order in any multi-gateway system.

* **Two-way Gateway Network auth defaults to on.** *"The **Require Two-Way
  Authentication** property now also defaults to `True`."*

* **Store and Forward is multi-threaded** across six data types, and
  **Primary Store Maintenance Value** (8.1's Max Records) defaults to 0 =
  unlimited on upgrade. Quarantine exports switched XML → JSON and are **not**
  cross-importable from 8.1.

* **Hot swapping modules is gone.** *"Hot swapping modules is no longer
  supported in Ignition 8.3. You will need to restart your Gateway if you want
  to install or upgrade a module."*

* **OPC UA moved to 1.05 with role-based access**, and anonymous clients lose
  write/call by default on upgrade.

* **Ignition Cloud Edition is a documented edition**, bought through cloud
  marketplaces (AWS AMI, and as of 8.3.5 an EKS container product), with no
  Vision module and no PLC drivers.

* **New modules shipped:** Event Streams, Kafka Connector, MariaDB / MSSQL /
  PostgreSQL JDBC drivers, Siemens Enhanced, SQL Historian.
  **Modules absorbed:** Serial Support (Client + Gateway) into the platform,
  Web Browser into Vision.

* **Perspective gained Drawing, Form, and Offline Mode**; Vision gained the
  Web Browser component and retarget-preserving client settings.

* **Scripting-function counts, from the docs' own "Functions by Scope" index:**
  Gateway 338 → 367, Perspective Session 325 → 332, Vision Client 351 → 356.

---

## Headline features

### 1. File-based Gateway configuration

In 8.1, Gateway configuration lived in an internal SQLite database (the IDB).
In 8.3 it lives in `data/config` as readable files. The upgrade guide is blunt
about the consequence: *"the file system in Ignition 8.3 is drastically
different, so without the updates and checks, legacy resources may not work
without user intervention."*

The layout (from `appendix/reference-pages/gateway-folder-structure`):

| Path | What lives there | In `.gwbk`? | Synced to redundant backup? |
|---|---|---|---|
| `/data/config/resources/external` | Resource-collection files, read-only within the Gateway (VCS / container volumes drop them here) | No | No |
| `/data/config/resources/core` | Resource-collection files, editable from the Gateway | Yes | Yes |
| `/data/config/resources/local` | Machine-specific resource-collection files | Yes (separate `/local-backup`) | No |
| `/data/config/resources/{mode}` | Per-deployment-mode resource definitions | Yes | Yes |
| `/data/config/ignition` | Platform config identical on master/backup (e.g. OAuth2 email tokens) | Yes | Depends on provider |
| `/data/config/{module-id}` | Module config identical on master/backup (e.g. OPC UA trust store) | Yes | Depends on provider |
| `/data/config/local/ignition` | Platform config that must differ master vs backup (hostname certs) | Yes (`/local-backup`) | Depends |
| `/data/var/ignition` | Transient platform data — Designer auth tokens, internal Alarm Journal, internal Audit Log, licensing, Store and Forward engine | **No** | Depends |
| `/data/var/{module-id}` | Transient module data — **Core Historian data**, Perspective/Vision auth tokens, SFC state, Internal Historian (Legacy) | **No** | Depends |
| `/data/projects` | Projects | Yes | Yes |

Practical fallout:

* **Tags are files now.** *"tag JSON files are now stored with the path that's
  shown in the Tag Browser following `C:\Ignition\8.3.0\data\config\resources\core\ignition\tag-definition`."*
  Deep UDT/folder hierarchies can therefore blow past Windows' 255-character
  path limit — the docs added a whole `tutorials/.../working-with-long-paths`
  page for this.
* **File naming is validated.** Backtick, `/`, `\`, `?`, `*`, `:`, `|`, `"`,
  `<`, `>` are illegal; space and period are illegal as first/last character;
  hyphen is illegal as first character. During migration *"some resources may
  need to be renamed to comply with our naming validation schema"* — which can
  silently break intra-project references.
* **The old IDB is not deleted.** *"During the upgrade process, Ignition
  migrates resources from the internal database (IDB) to the new file system.
  The deprecated IDB is not removed after upgrading, but will not affect your
  system as it is no longer used."*
* **A migration log is written** as a Markdown file under `data/config`,
  listing tables migrated, duration, strategy, and anything left behind.

### 2. Gateway Deployment Modes and resource collections

**Collections** are groupings of Gateway resources, arranged in an inheritance
chain. All deployment modes are collections; not all collections are deployment
modes.

| Collection | Mutable? | Purpose |
|---|---|---|
| `system` | No — immutable | Built-in configuration Ignition injects (e.g. the MariaDB JDBC driver). Can be *overridden*, not edited. |
| `external` | Not from the Gateway UI | Centrally managed config placed by the file system / VCS. *"if you are using a version control system (VCS), this collection is where your VCS should place any relevant resources."* |
| `core` | Yes | The default. A fresh Gateway with no deployment modes runs in `core`. |
| `local` | Yes | Host-specific data (certificates). Overrides here **do not carry to a backup Gateway**. |
| `{mode}` | Yes | User-created deployment modes, inheriting from `core`. |

**Switching modes is a config-file operation, not a UI one.** Add to
`data/ignition.conf`:

```
wrapper.java.additional.x=-Dignition.config.mode=DEPLOYMENT_MODE_NAME_HERE
```

and restart the service. *"Only one deployment mode can be active at any given
time."*

**Redundancy caveat, verbatim:** *"When using Gateway Redundancy, deployment
mode configuration is stored in the 'ignition.conf' file and does not sync
between the primary and backup Gateways. To avoid issues where a failover could
result in the backup using different device or database connections than
expected, ensure both Gateways are configured with the same
`-Dignition.config.mode` value and restart both services after making any
changes."*

**Resource types:** *named* (device connections — a list), *singleton*
(Gateway Network Settings — one page, one resource definition), and *system*
(immutable, override-only).

**Cannot be overridden:** Deployment Modes, Modules, Projects, Licenses.

Resource definitions are created by manual creation with a deployment-mode
dropdown, by **override** (same name, mode-scoped), or by **duplicate**
(new name, mode-scoped). Deleting a deployment mode deletes its resource
definitions.

Supporting additions: a `deploymentMode` **System Tag** (8.3.3) exposing the
active mode, and — from 8.3.8 — *"The active deployment mode will now be logged
during Gateway startup."*

### 3. Gateway REST API and the Infrastructure-as-Code story

The Gateway serves a live OpenAPI spec:

| Format | URL |
|---|---|
| Interactive docs | `http[s]://<gateway-host>:<port>/openapi` |
| Raw JSON spec | `http[s]://<gateway-host>:<port>/openapi.json` |

*"As of version 8.3, many configuration elements in Ignition are exposed as
**resources** using a standardized format."* Routes live under
`/data/api/v1/resources`, e.g.

* `GET /data/api/v1/resources/list/<moduleId>/<typeId>`
* `POST /data/api/v1/resources/<moduleId>/<typeId>`
* `DELETE /data/api/v1/resources/<moduleId>/<typeId>/<name>/<signature>`

API Keys also unlock `/data/api/v1/sync` and `/data/api/v1/modes`.

**Authentication:** `X-Ignition-API-Token: <your-api-token>`. Keys are created
at **Platform > Security > API Keys**, are hashed on storage, and *"The key
itself is only visible to the user at the time of creation."* Type is currently
Basic Token only; "Require secure connections for API Keys" is on by default;
keys carry security levels (Authenticated is mandatory and unremovable).

**Auditing gap worth knowing:** *"Mutative rest API requests (such as POST,
PUT, and DELETE) are recorded in audit logs with the user, IP address, and API
key. **GET requests are not recorded in audit logs.**"*

The version-control guide ties it together: *"Infrastructure-as-code tools such
as Ansible, Terraform, or custom Python scripts can use this interface to audit,
apply, or roll back changes as part of a continuous deployment pipeline."*

**Version control guidance from the docs:**
* Switch Vision project encoding from binary to XML for diffability. *"By
  default, Vision projects are encoded as Java `.bin` files. This change will be
  implemented for existing windows incrementally as you modify and save
  individual windows."*
* `.gitignore` these, still `.bin`-encoded: Transaction Groups, Client Tags,
  Reports, Alarm Pipelines.
* Two documented approaches: full data-directory versioning, and "curated
  configuration mounts" (additive, via the `external` collection).

Complementary 8.3 scripting: a whole **`system.config`** namespace (added
8.3.8) — `copy`, `create`, `delete`, `move`, `rename`, `replace`,
`getResource`, `getResources`, `getResourceTypes`, `getModes`,
`getActiveMode` — so resource manipulation is scriptable in-Gateway as well as
over REST.

### 4. Core Historian

Introduced in 8.3.0 as *"an additional historical provider option for
time-series data"*, and described as: *"This new Historian, initially referred
to as the Power Historian, is powered by QuestDB and optimized for storing
time-series data."*

Key behaviours:

* **Store and Forward bypass.** *"The Core Historian writes directly to disk
  using a high-performance write-ahead log (WAL) system. It does **not** use
  Store and Forward, so it bypasses the buffering and retry mechanisms used by
  other historian types."* The upgrade guide phrases it slightly more softly:
  *"the Core Historian will only use the Store and Forward system if there are
  pending writes to the database. If there are no pending writes, the Core
  Historian will skip the Store and Forward system entirely."*
* **Partitioning** by Week / Month / Year, configured on the provider.
* **Maintenance modes:** `None`, `Prune` (default), `Archive` (moves partitions
  to an Archive Folder). Maintenance Age must be a whole-number multiple of the
  Partition Interval.
* **Metadata storage** (tag path, data type, units, scaling) in system-managed
  tables, surviving tag deletion; requires `Include Metadata` = true in the Tag
  Editor's History section. Required for annotations, aggregates and
  `system.historian` functions. Available only for Core and Internal (Legacy).
* **Memory:** *"The default memory allocation for the Core Historian is 10% of
  the total system memory when enabled."*
* **From 8.3.4**, `server.conf` and `log.conf` are auto-created at
  `%IgnitionInstallationDirectory%/data/var/com.inductiveautomation.historian/corehistorian/conf/`
  covering RAM, Cairo, Materialized View, WAL, HTTP, PG Wire, Metrics and
  Logging. *"The `server.conf` file should now be used to change any of these
  Core Historian settings as it supersedes the system properties"* — but legacy
  properties like `historian.questdb.httpServerEnabled` still win where they
  conflict.
* Two system properties added in 8.3.0 *"that enable the ability to query the
  Core Historian directly using Postgres"* (PG Wire).

**Historical path syntax change** (this breaks stored paths):

```python
# 8.1 Historical Path Syntax
histprov:Sample_DB:/drv:myGateway:My_Provider:/tag:My_Folder/Another_Folder

# 8.3 Historical Path Syntax
histprov:Sample_DB:/sys:myGateway:/prov:My_Provider:/tag:My_Folder/Another_Folder
```

*"Note that the SQL Historian still requires the `drv` key-value pair syntax,
and any `drv` syntax used in Ignition 8.1 will still work in 8.3."*

**Provider line-up in 8.3** (`ignition-modules/tag-historian/tag-history-providers`,
now at **Services > Historians > Historians**): CSV (read-only), Historian
Splitter, DB Table (read-only), **Core**, Internal (Legacy, SQLite), OPC HDA
(read-only, Windows + OPC COM), Remote, Simulator, **SQL Historian** (separate
module, required in addition to Historian Core).

**Licensing:** *"The Tag Historian license item has been replaced by the
Historian Core and SQL Historian license items."*

Seed values got real controls in 8.3.8: a **Number of past partitions queried
for seed values** setting, where `0` disables seed queries globally and a
negative number searches every partition.

### 5. Event Streams

New in 8.3.0 as project resources: *"Event streams are project resources in
Ignition that aim to allow users to have a unifying construct for handling
asynchronous events... This helps eliminate the complexity of configuring
multiple scripts on separate subsystems."*

Stages:

| Stage | Description |
|---|---|
| Source | Origin of the data. Kafka (Kafka module), HTTP Endpoint (Web Dev module), Event Listener, Tag Event. |
| Encoder | String / JsonObject / Byte[]; character encoding UTF-8, UTF-16, BASE_64. JSON by default. Runs after Source and again after Transform. |
| Filter | Optional script `(event, state) -> bool`. False drops the event. |
| Transform | Optional script returning a replacement payload. |
| Buffer | Debounce (default 100 ms), Max Wait (default 1000 ms), Max Queue Size (0 = unlimited), Overflow (`DROP_OLDEST` / `DROP_NEWEST`). |
| Handler | Kafka, Database (SQL Bridge), HTTP (Web Dev), Gateway Event, Gateway Message, Logger, Script, Tag. Multiple handlers run sequentially. |
| Error Handler | Catch-all, invoked when a handler with `ABORT` failure mode throws. |

Handler **failure modes**: `IGNORE`, `ABORT`, `RETRY` (with fixed or
exponential Retry Strategy, Retry Count, Retry Delay, Multiplier, Max Delay,
and a Retry Failure fallback of IGNORE or ABORT).

Handler expressions can dig into the event object with dot notation in braces:
`{event.metadata.topic}`, `{event.data.name}`.

Scripting: `system.eventstream.getDiagnostics`, `.listEventStreams`,
`.publishEvent`. Gateway-side metrics live on the **Services** page.

Later additions: numeric quality codes for tag handlers and Alarm Metrics
subscriptions in Tag Event sources (8.3.2); `previousValue` metadata, an
`HTTP Version` property (HTTP/1.1 vs HTTP/2), and a `Ready` stage state
(8.3.5); Project Browser status icons for running / modified / disabled /
failed (8.3.8).

### 6. Secrets Management

*"Implemented a Secrets Management system that provides support for encrypting
secrets like credentials, API tokens, and private keys."*

Password fields across the Gateway are replaced by a three-way choice:

* **None** — no password required.
* **Embedded** — value encrypted by Ignition's system encryption service; once
  saved it *"is encrypted and cannot be made visible to any user."*
* **Referenced** — points at a Secret Provider + secret name.

**Key hierarchy:** environment password → `root.json` (Root Key) →
`kek.json` (Encryption Key Set, three rotatable keys) → secrets. All under
`/data/config/ignition/keys`.

**Environment variables:**

| Variable | Description |
|---|---|
| `IGNITION_ROOT_KEY_PASSWORD_FILE` | Path to a file holding the root key password |
| `IGNITION_ROOT_KEY_PASSWORD` | The key itself |

*"Fresh Ignition installations are packaged with a default encryption key"* —
which is the same on every install, so the docs recommend customising. Doing so
is **opt-in and irreversible in responsibility terms**: *"You must opt in to
the Secrets Management system complete functionality... it will be the user's
responsibility to maintain the system once it has been customized."*

The system is verified on **every** Gateway startup, whether or not any secrets
are configured.

**Secret Provider types:** Internal (8.3.0), **Remote** (8.3.3 — reads another
Gateway's provider over the Gateway Network; access defaults to *deny* and must
be granted in the Security Zone's Manage Policy → Secret Provider Access),
**File** (8.3.5 — `CLEARTEXT` or `CIPHERTEXT` on disk; cleartext is
Kubernetes/Vault/Azure/AWS-mount friendly; ciphertext is a flat JWE made by
`system.secrets.encrypt` or `POST /data/api/v1/encryption/encrypt`).

**CLI tool:** `ignition-secrets-tool.bat` (Windows) / `ignition-secrets-tool.sh`
(*nix) — generate, reset, remove, rotate keys.

**Redundancy:** *"Make sure that the `root` and `KEK` JSON files are applied to
both the Master and Backup nodes in a redundant configuration. If not, the
embedded secrets and Internal Provider secrets encrypted on one will not decrypt
on the other."*

**Scripting:** `system.secrets.encrypt`, `.decrypt`, `.getProviders`,
`.getSecrets`, `.readSecretValue`, plus (8.3.8)
`.createEmbeddedSecretConfig`, `.createReferencedSecretConfig`,
`.readConfiguredSecretValue`. A new `PyPlaintext` class arrived in 8.3.1.

### 7. Security and Identity Provider rework

**Gateway pages are role-gated.** *"8.3 Gateway webpages now operate on a
required role basis. Certain pages and actions will not be available if a user
is not signed in, or does not have the correct roles or permissions.
Additionally, permissions granted in 8.1 will not automatically roll over into
8.3, and must be reassigned."*

The new **Roles and Permissions** section on **Platform > Security > General
Settings** defines three tiers, each configured as a set of security levels
plus an any/all match rule:

| Permission | Grants |
|---|---|
| Gateway Write | Interact with all Gateway pages and settings. Implies Read. |
| Gateway Read | View all Gateway pages and settings. Implies Access. |
| Gateway Access | View Home-section pages only, except Perspective Sessions and Brand Settings. |

Only **Home** is visible without login (minus Perspective Sessions and Brand
Settings). If a user has no permissions the Gateway search bar does not appear
at all.

Other security changes:

* **Service Security merged into Security Zones.** *"Service security settings
  are now part of Security Zone configurations."* You reach them via the three
  dots menu on a zone → **Manage Policy**. The 8.1 page `platform/security/service-security`
  was titled "Service Security"; 8.3 retitles it **Service Security Policies**
  and adds per-service policy sections: Alarm Journal Access, Alarm
  Notification, Alarm Status, Audit Log Access, Diagnostic Services, EAM License
  Management, History Provider Access, **Secret Provider Access**, Tag Access.
  *"If you have a policy defined on the `default` security zone, it will be
  brought in as part of the Gateway Deployment Mode's core collection for that
  zone."*
* **IdP export format changed.** *"The shape of an exported JSON file for an
  Identity Provider on the Gateway has changed from 8.1 to 8.3, which means
  importing Identity Providers from 8.1 Gateways onto 8.3 Gateways is currently
  not supported."* **Fixed in 8.3.3:** *"Added the ability to import 8.1 Gateway
  Identity Provider exports to 8.3 Gateways."*
* IdP **User Attribute Mapping**, **User Grants** and **Security Levels** became
  configurable on overridden Identity Providers within mutable collections
  (8.3.1) — i.e. per deployment mode.
* The **Administrator** role is now auto-listed under Authenticated/Roles
  security level on a fresh Gateway.
* Internal Authentication gained **Prohibit Password**, **Prohibit Username**,
  and **Maximum Consecutive Repeated Characters** password policies.
* AD / AD-Database Hybrid / AD-Internal Hybrid user sources gained extra LDAP
  attributes, nested group membership lookup, group role attributes, a
  **Connect Timeout** (8.3.2), and a **Legacy Naming Enabled** property (8.3.7)
  *"to improve migration during upgrades from 8.1."*
* An **Identity Provider** setting was added to Project Settings (8.3.2) to
  match the Designer's project-creation flow.

### 8. Ignition Cloud Edition

Documented as a distinct edition at `other-editions/ignition-cloud-edition`.
*"Cloud Edition is available through major cloud computing marketplaces such as
**Amazon Web Services (AWS)**."*

* **Licensing is implicit.** *"Cloud Edition will instead detect that it is
  running in a paid image or container, and therefore already be licensed."*
  It does not appear in the normal commissioning edition picker.
* **8.3.5 added an EKS container product.** Billed hourly on three factors: a
  base rate, CPU cores detected, and heap memory in GB. *"When the container is
  started with a Gateway backup restore, the Gateway runs as Cloud Edition
  regardless of the edition associated with the backup."*
* **No Vision module** — *"The nature of Cloud Edition makes Perspective's
  web-based visualization system more suitable for cloud-based infrastructure
  and helps mitigate potential security risks."*
* **No PLC drivers.** *"Cloud Edition does not include any industrial device
  drivers to connect directly to PLCs."* MQTT is the ingress path.
* **Cloud Connectors** are a new module class: **MongoDB** and **Kafka**.
* Redundancy only between two Cloud Edition Gateways; recommended across
  Availability Zones.
* IA modules not bundled cannot be licensed on Cloud Edition; third-party
  modules can.
* Ubuntu 24.04+ gotcha: `unattended-upgrades` + `needrestart` will auto-restart
  the Ignition service unless you add
  `qr(^ignition\service$) => 0` to `$nrconf{override_rc}`.

### 9. Store and Forward

* **Multi-threaded engine.** Database connections pool eight connections;
  *"if the Store and Forward engine is storing a particular type of data, such
  as tag history, that action will not block the engine from concurrently
  storing a different type of data."* Six data types can go in parallel:
  Alarming, Auditing, Scripting, SECS/GEM, Tag history, Transaction Group.
* **Upgrade default change.** *"the Store and Forward **Primary Store
  Maintenance Value** property (known in 8.1 as Max Records) will be set to zero
  by default. This means that the local disk cache is configured to store an
  unlimited number of data points."*
* **Quarantine export format changed.** *"Quarantine exports have also been
  changed to use JSON rather than XML. This means that quarantine exports from
  8.1 Gateways cannot be imported into 8.3 Gateways."*
* **Legacy data conversion runs automatically at engine startup.** Leftovers
  stay as an `.hsql` file and *"should be moved to
  `%IgnitionInstallationDirectory%/data/local/store-forward/quarantined-databases/`."*
* **Cross-version forwarding is blocked:** *"Due to serialization updates, 8.3
  Gateways will not be able to forward data to a remote 8.1 Gateway."*
* The whole topic moved out of `platform/database-connections/` into a
  top-level `platform/store-and-forward/`.

### 10. Gateway Network

* **Protobuf replaces Java serialization.** *"Due to security and configuration
  persistence updates, Ignition 8.3 no longer uses Java serialization to convert
  your data to a saveable state, but instead relies on Protobuf."*
* **`Allow Java Serialization` setting.** Default on a *new* 8.3 install:
  disabled. Default after an *upgrade* from 8.1: enabled, with a banner warning.
  The settings table is explicit: *"If true, Java Serialization with known
  security vulnerabilities will be enabled. This setting is required for
  connectivity with legacy Ignition versions."*
* **`Require Two Way Auth` now defaults to True.** Certificates must be approved
  on both ends — outgoing side accepts on Outgoing Connections, receiving side
  accepts on Incoming Connections. Certificates come from the metro KeyStore at
  `<install>\data\config\local\ignition\gateway-network\keystore`
  (password `metro`, alias `metro-key`), trusted into
  `data\config\local\ignition\gateway-network\client\security\pki\trusted\certs`.
* **Its own thread pool.** 8.3.2 added **Data Channel Queue Size** (default 50)
  and **Data Channel Thread Pool Max Size** (default 100). *"Users who have
  previously adjusted the `gateway.maxThreads` property found in the
  `gateway.xml` file, especially those using large Hub and Spoke Architectures,
  should now configure these settings instead."*
* **Enumeration is event-based** as of 8.3.4, replacing the 60-second polling
  call.
* **Remote Gateways tab** added on the Connections page (8.3.5).
* **Version span:** *"Ignition 8.3 Gateways can only communicate with other 8.3
  or 8.1 Gateways, even if you are using proxies."*

### 11. Perspective, Vision, Launchers

**Perspective**
* **Drawing component** — SVG vector graphics authored in the Designer;
  imports SVG, GIF, JPEG, PNG. F1–F10 tool shortcuts (8.3.1), ⌘+Drag pans on
  macOS, `typeAttr` element property (8.3.4), `onElementClicked` event (8.3.5).
* **Form component** — dynamic validation, conditional fields, submission
  handling, plus a **Form Submission** Session Event handled on the Gateway.
  Widgets grew over 8.3.x: number `step` value `any` (8.3.4); Dropdown widget
  gained `search`, `showClearIcon`, `allowCustomOptions`, and a File Upload
  widget arrived (8.3.8).
* **Offline Mode** (Perspective App only, opt-in in Perspective Project
  Properties). Unavailable while offline: realtime tag/alarm/query values,
  Gateway Event or database scripts, previously unloaded views. User input is
  cached and flushed on reconnect.
* **Themes moved to the resource model.** *"In 8.1, theme authorship relied
  solely on the filesystem. In 8.3, the new config and resource collection model
  required the existing theme structure to conform to this new model."* Each
  theme now gets a `config.json` with `isPrivate` and `entrypoint` (usually
  `index.css`). Migrated originals are kept in
  `.migrated-themes-TIMESTAMP` under `data/modules/com.inductiveautomation.perspective`.
* **File Upload hard cap.** *"The File Upload component will now only accept
  files smaller than 20 MB, regardless of the `fileSizeLimit` property."*
  Raise it via `max-file-size` in `web.xml` (whose default itself went 20 MB →
  128 MB in 8.3.9, for JDBC driver uploads).
* Minimum browser versions raised. `Intl.NumberFormat` replaced Numeral.js
  (8.3.3) — locale-dependent number formatting output can shift.
* Page Details (page counts, latency, uptime) in the Session Status Popup.

**Vision**
* **Web Browser component** folded in from the retired Web Browser module,
  now under **Misc** in the Vision components panel.
* Client settings propagate across retargets (launch modes, screens, etc.).
* **Resource Encoding** project property extended to Vision Client tags (8.3.2).
* **Auto-Redirect** login option for IdP-strategy Vision Clients (8.3.1).

**Launchers and Workstation**
* **Deep links:** `%LauncherType%://%GatewayAddress%/%ProjectName%`, e.g.
  `perspective://localhost:8088/MyPerspectiveProject`.
* **File associations:** `.perspective`, `.vision`, `.designer` (JSON files).
  JVM arguments supported in file associations from 8.3.1.
* **macOS is Apple Silicon only.** *"Updated Launcher supported architecture for
  Mac to Apple Silicon, x86 Mac is no longer supported."*
* New `allow.uri.schemes` launcher JSON setting.

### 12. Other notable platform work

* **Docker / Kubernetes.** The Docker page moved under
  `platform/advanced-deployments/`, module identifiers became fully-qualified
  IDs, two new environment variables automate third-party module acceptance, and
  the image is OpenShift 4 `restricted`-SCC compatible. `jq` was added in 8.3.5;
  8.3.9 added a runtime argument to restore local-only config files from a
  backup. A brand-new **Kubernetes** page documents the official Helm chart at
  `https://charts.ia.io/`.
* **OPC UA.** Upgraded to **OPC UA 1.05** with role-based access control;
  new Permissions tab on the OPC UA Server Settings page; GDS Push support
  (`gdsPushEnabled`, requires a `SecurityAdmin` role that *"does not exist by
  default and will need to be created"*); OPC Quick Client on the Gateway
  (8.3.3); Anonymous and Certificate authentication types for client
  connections (8.3.3); Timestamp Source property (8.3.1). 8.3.9 raised Eclipse
  Milo to 1.1.6, which now *"requires a `ConfigureAdmin` or `SecurityAdmin` role
  to enable server diagnostics."*
* **Siemens Enhanced driver** (new module) with browsing and symbolic access for
  S7-1200 / S7-1500; S7-1200 G2 support added in 8.3.3; PLC symbol export in
  8.3.7; `Secure Connection Mode` replaced `Force Secure Connection` in 8.3.4.
* **Redundancy.** Backup version configurations can now override master
  configurations; `-Dignition.redundancy.syncMaxAttempts` caps sync attempts;
  General Gateway Network settings became editable on a backup node (8.3.3);
  the Redundancy page became readable with read permissions (8.3.9).
* **Alarming.** Runtime Alarm Metric properties at folder level and on all UDT
  instances, plus 15 aggregated metrics; new **When True** / **When False** tag
  alarm modes; Twilio **Voice** and **WhatsApp** notification profiles.
* **Reporting.** New **Radar Chart**; a `hidden` property on Page Object;
  copy-and-paste images; Barcode / Bar / Pie / Radar / Timeseries / XY charts
  usable as raster **or** vector.
* **Tags.** New `ModuleVersions` System Tags folder for EAM controllers; Memory
  tag **Default Value** and **Value Persistence**; **Preserve Source Timestamp**
  on Derived tags (8.3.1); a **Qualified Value** Tag Event Script trigger
  (8.3.2); wildcards in tag paths for Tag Event sources and Gateway Tag Change
  Scripts (8.3.4); an **Alarm Metrics** folder at provider level in the Tag
  Browser (8.3.9).
* **Gateway UI.** Sidebar navigation rebuilt around Home / Platform /
  Connections / Network / Services / Diagnostics; a search bar (`CTRL` + `/`);
  a **Gateway Restart Required** banner; accessibility work on contrast and
  shape distinction (8.3.2); System Name validation rejecting `|` (8.3.2).
* **Scripting.** Autocomplete now lists system library constants and flags
  deprecated functions. `system.db.execScalar` added. Jython 2.7.3 → **2.7.4**
  (8.3.8). `system.serial` migrated into the platform.

---

## Removed and deprecated / Renamed / moved

Moved to [`8.1-to-8.3-traps.md`](8.1-to-8.3-traps.md) (removed features, deprecated-function → replacement table,
silent behaviour changes, renames, doc-path moves, new namespaces). Read it before trusting 8.1-era knowledge.


---

## Upgrade path and compatibility

### Prerequisites

* **You cannot go 7.9 → 8.3 directly.** *"Gateways running on Ignition versions
  earlier than 8.1 cannot be directly upgraded to 8.3. They must first be
  upgraded to 8.1, and then upgraded to 8.3. This limitation also applies to
  restoring Gateway backups, where you will first need to upgrade the Gateway
  backup to version 8.1, then restore the 8.1 Gateway backup onto your 8.3
  Gateway."* The docs list the specific breakages: Gateway Network,
  serialization, and data syncing/communication/storage.
* **Get to the latest 8.1 first.** *"It is **strongly advised** to first upgrade
  your Gateway to the latest version of 8.1, if you have not already."*
* **Check your license.** *"Before upgrading, check your license to ensure it is
  compatible with 8.3. If your license is not 8.3 ready, contact your Sales
  Representative."*
* **Remove duplicate usernames** from Internal and AD/Internal Hybrid user
  sources *before* upgrading.
* **Verify third-party module compatibility.** *"any third party modules will
  need to be checked to ensure they are compatible with 8.3."*
* **Take a Gateway backup**, and upgrade dev/test on similar hardware first.

### Installer vs fresh install

The installer is the recommended route. Importing projects/tags into a fresh
8.3 install is explicitly discouraged:

> *"a Gateway Backup triggers an upgrade check that makes modifications to the
> resources so they run as expected on the Ignition 8.3 system. The same check
> is triggered when running the installer. Project and tag imports do **not**
> trigger this check."*

Concretely, *"Your 8.1 tags are likely using an old name, where a freshly
installed Gateway is using the new name. Therefore, tags imported from an
Ignition 8.1 file will likely break upon import due to name mismatches."*

From **8.3.8**, the installer itself has an optional **Restore from Backup**
step, so a fresh install can be seeded from a `.gwbk` on first startup.

ARM installations must upgrade via the **ZIP installer**, not the installer.

### Recommended upgrade order in a multi-gateway system

This is the single most consequential operational change. Because 8.3 uses
Protobuf and *"8.3 Gateways are not able to store data to 8.1 Gateways over the
Gateway Network"*, data-receiving Gateways must go first.

1. **Upgrade the central Gateway that hosts the data first** — *"the central
   Gateway hosting the data **must** be upgraded to 8.3 first. This includes
   Gateways where the main Alarm Journal, audit profile, and history provider
   are configured."* Then verify it is running correctly.
2. **Then upgrade remote and Edge Gateways** that use data-storing services.

The affected services, named explicitly: Edge Sync Services, Remote History
Providers, Remote Alarm Journals, Remote Audit Profiles.

3. **Enable `Allow Java Serialization`** on 8.3 Gateways for as long as any 8.1
   Gateway remains in the architecture (auto-enabled on upgrade, **not** on a
   fresh 8.3 install). A banner appears on the Gateway expecting the incoming
   connection while it is on.
4. **Re-approve Gateway Network certificates** now that two-way auth is on by
   default.

### Redundant pairs

From `installing-and-upgrading#upgrading-a-redundant-pair` — upgrade the
**Backup first**:

1. Master Gateway → **Platform > System > Redundancy**.
2. **Configure Redundancy** → Master Node Settings → Recovery Mode = **Manual**.
3. **Save Changes**, **Confirm**.
4. Upgrade and start the **Backup** Gateway.
5. Back on the Master's Redundancy page, select **Force Failover** (Backup
   becomes active).
6. Upgrade and start the **Master** Gateway.
7. Confirm both are connected.
8. Select **Assume Control** to return the Master to active.

*"This procedure applies to both upgrades between minor versions and upgrades
between major versions, such as 8.1 to 8.3."*

Extra redundancy caveats: a **new-install backup node must be set to match the
master's `Require Two-Way Authentication` value** or it will never connect;
`-Dignition.config.mode` does **not** sync and must be set identically on both
nodes; `root.json` and `kek.json` must exist on both nodes.

### Cross-version compatibility matrix

| Pairing | Supported? | Source |
|---|---|---|
| 8.3 Gateway ↔ 8.3 Gateway | Yes | — |
| 8.3 Gateway ↔ 8.1 Gateway (Gateway Network) | Yes, with `Allow Java Serialization` enabled | *"Ignition 8.3 Gateways can only communicate with other 8.3 or 8.1 Gateways, even if you are using proxies."* |
| 8.3 Gateway ↔ 7.9 Gateway | **No** | Same passage |
| 8.3 → store data to 8.1 over Gateway Network | **No** | *"8.3 Gateways are not able to store data to 8.1 Gateways over the Gateway Network."* |
| 8.3 launcher / Workstation → 8.1 Gateway | Yes | *"Application launchers and Perspective Workstation running 8.3 are backwards compatible with 8.1."* |
| 8.1 launcher / Workstation → 8.3 Gateway | **No** | *"8.1 launchers and Perspective Workstation are not forward compatible with 8.3."* |
| 8.1 Designer editing tags on an 8.3 remote provider | **No** | Throws `GatewayException` / `UndeclaredThrowableException` |
| 8.1 IdP JSON export → 8.3 Gateway | Not at 8.3.0; **yes from 8.3.3** | 8.3.3 release note |
| 8.1 Store & Forward quarantine export (XML) → 8.3 | **No** | Format changed to JSON |
| EAM 8.3 controller → 8.1 agent, Send Project / Send Project Resources | Partial | *"some resources, such as Gateway Event Scripts and Perspective Event Scripts, cannot be sent from an 8.3 EAM controller to an 8.1 agent."* |
| EAM Remote Upgrade 8.1.x → 8.3.x on Apple M-series | **No** | Architecture change (x86 → native ARM) isn't handled; do an in-place upgrade to 8.3.0 first, after which EAM upgrades work |
| 7.9 or 8.0 `.gwbk` restored onto 8.3 | **No** | Must be upgraded to 8.1 first |

### Post-upgrade actions

* **Project migration icon.** Projects using Gateway or Client Event Scripts get
  an icon in the Designer. *"The scripts that have this warning are still fully
  functional and will continue to work without needing any immediate action. The
  warning will also disappear when you select the resource in the Designer, as
  the platform will finish migrating that specific resource."* Migrated Gateway
  Event Scripts land at
  `%IgnitionInstallationDirectory%/data/projects/%ProjectName%/Ignition/%GatewayEvent%/`
  as `.py`; migrated Client Event Scripts at
  `.../Ignition/script-python/%ScriptName%/`.
* **Re-check renamed resources** against the file-naming schema and fix inbound
  references.
* **Reassign Gateway permissions.**
* **Re-trust OPC UA certs**; test anonymous *and* authenticated OPC UA clients
  for browse/read/write/call.
* **Reactivate the license** if modules show Trial when Activated is expected.
* **Fix themes.** Old `@import "./light.css"` becomes
  `@import "../light/index.css"` in the new entrypoint; external imports must
  move into the entrypoint; originals are kept in
  `.migrated-themes-TIMESTAMP`.
* **Check Diagnostics > Overview**, confirm history is still being stored, and
  confirm projects work.
* **JDBC drivers are not upgraded by the installer** — deliberately: *"you
  should only need to change the JDBC driver if you upgrade your database."*

### Where to look when it goes wrong

| Log directory | Log | What it tells you |
|---|---|---|
| `%IgnitionInstallationDirectory%/logs/` | Wrapper | Gateway, subsystems, Gateway-scoped resource errors |
| `%IgnitionInstallationDirectory%/logs/` | Tag-migration | Per-Tag-Provider JSON with migration metrics and affected tag paths |
| `%IgnitionInstallationDirectory%/logs/` | `install_{YYYYMMDD-HHmm}` | Installer extraction/replacement of the 8.3 file system |
| `%IgnitionInstallationDirectory%/data/config/resources/` | migration-log | Summary of IDB → file-system migration, incl. tables that failed or are pending |
| `%IgnitionInstallationDirectory%/data/projects/` | Conversion-report | Project-resource conversion |

### Rollback

There isn't one. *"Downgrading Ignition is not a supported use case of the
Ignition upgrade, and can lead to unexpected problems."* The documented recovery
is: uninstall the service, delete the install directory, reinstall the old
version, restore a backup taken **from that version or older**.

---

## Version-specific changes within 8.3

Only items the docs attribute to a specific 8.3.x release. Compiled from
`new-in-this-version`, the Deprecated manual's "Deprecated Functionality by
version" section, and in-page "as of / starting in" notes.

| Version | Area | Change |
|---|---|---|
| 8.3.0 | Gateway | Gateway Deployment Modes introduced |
| 8.3.0 | Gateway | `/openapi` API documentation page added |
| 8.3.0 | Gateway | Gateway sidebar navigation rebuilt |
| 8.3.0 | Gateway | Roles & Permissions section added to Security > General Settings |
| 8.3.0 | Gateway | Gateway Restart Required banner added |
| 8.3.0 | Gateway | `-Dignition.gateway.externalModulesFolder`, `-Dignition.gateway.rpcErrorDetailSuppression` added |
| 8.3.0 | Gateway | Two system properties enabling direct Postgres query of the Core Historian |
| 8.3.0 | Gateway | OPC UA Server Settings gained a Permissions tab |
| 8.3.0 | Gateway | Serialization Format setting (Protobuf default, Java Serialization for legacy) |
| 8.3.0 | Historian | **Core Historian** added |
| 8.3.0 | Security | **Secrets Management** system implemented |
| 8.3.0 | Security | Administrator role auto-listed under Authenticated/Roles on fresh installs |
| 8.3.0 | Security | Extra LDAP attributes, nested group membership, group role attributes for AD sources; 3 new Internal Auth password policies |
| 8.3.0 | Event Streams | Event Streams available as project resources |
| 8.3.0 | Drivers | Siemens Enhanced driver (new module); MariaDB/MSSQL/PostgreSQL JDBC drivers bundled |
| 8.3.0 | Perspective | Drawing component, Form component, Form Submission session event, Offline Mode |
| 8.3.0 | Perspective | Theme API / `config-perspective-themes` resource type |
| 8.3.0 | Perspective | File Upload hard-capped at 20 MB regardless of `fileSizeLimit` |
| 8.3.0 | Perspective | Minimum browser versions raised; react-pdf → 7.7.3 |
| 8.3.0 | Reporting | Radar Chart; Page Object `hidden`; raster-or-vector chart components; paste images |
| 8.3.0 | Scripting | `system.vision` and `system.historian` namespaces; `system.db.execScalar`; `system.serial` moved into the platform |
| 8.3.0 | Scripting | `system.gui.convertPointToScreen`, `system.gui.getQuality`, `system.dataset.toPyDataSet` deprecated |
| 8.3.0 | Scripting | `system.db.clearAllNamedQueryCaches` / `clearNamedQueryCache` replaced by `system.db.clearQueryCache` |
| 8.3.0 | Tags | `ModuleVersions` System Tags folder; Memory tag Default Value + Value Persistence |
| 8.3.0 | Tags | Multi-Instance Wizard "List of Names" pattern type **removed** |
| 8.3.0 | Alarming | Folder-level and UDT-instance Runtime Alarm Metrics + 15 aggregated metrics; When True / When False alarm modes; Twilio Voice and WhatsApp profiles |
| 8.3.0 | Launchers | Deep links and file associations; Mac → Apple Silicon only; `allow.uri.schemes` |
| 8.3.0 | Vision | Web Browser component included in Vision; client settings propagate on retarget |
| 8.3.0 | EAM | Leased Licenses (eight-character keys) usable for EAM activation |
| 8.3.0 | Redundancy | `-Dignition.redundancy.syncMaxAttempts`; Backup version configurations |
| 8.3.0 | Designer | `-Dignition.designer.websocketMaxBinaryMessageSize` added |
| 8.3.0 | Docker | Fully-qualified module identifiers; 2 new env vars; OpenShift 4 `restricted` SCC compatibility |
| 8.3.0 | JxBrowser | Upgraded to 8.5.0 |
| 8.3.1 | Gateway | Endpoints editable for overridden OPC UA Connections across deployment modes |
| 8.3.1 | OPC UA | `.getDescription()` on `system.opc.browseServer`; independent read/write max holding register; Timestamp Source property |
| 8.3.1 | Perspective | Markdown lib → 5.0.3 (CVE-2020-7753); Drawing F1–F10 shortcuts; ⌘ shortcuts, ⌘+Drag pans |
| 8.3.1 | Scripting | `PyPlaintext` class and `system.secrets` functions added |
| 8.3.1 | Security | User Attribute Mapping / User Grants / Security Levels configurable on overridden IdPs in mutable collections; Netty → 4.1.127 |
| 8.3.1 | Tags | Preserve Source Timestamp on Derived tags; hide Alarm Metrics in Tag Browser |
| 8.3.1 | Vision | Auto-Redirect for IdP-strategy Vision Clients |
| 8.3.1 | Launchers | JVM arguments supported in File Associations |
| 8.3.2 | Gateway | System Name validation (rejects `|`); Quarantined Module resolve/delete actions; UI contrast/shape accessibility pass |
| 8.3.2 | Gateway Network | Data Channel Queue Size + Thread Pool Max Size added; supersedes `gateway.maxThreads` tuning |
| 8.3.2 | Gateway | Manage JAR Files option on the JDBC Drivers page; Identity Provider setting in Project Settings |
| 8.3.2 | Event Streams | Numeric quality codes for tag handlers; Alarm Metrics subscriptions in Tag Event source; Tag Browser icon on tag handler form |
| 8.3.2 | Drivers | Mitsubishi Max Gap Size default → -1 |
| 8.3.2 | EAM | Agent Send Stats Interval 30 s → 45 s |
| 8.3.2 | Security | Connect Timeout added to AD / AD-DB Hybrid / AD-Internal Hybrid user sources |
| 8.3.2 | Tags | Qualified Value option for Tag Event Scripts |
| 8.3.2 | Vision | Resource Encoding project property extended to Vision Client tags |
| 8.3.2 | Reporting | Improved vector settings and print quality |
| 8.3.3 | OPC UA | Anonymous and Certificate authentication types; OPC Quick Client on the Gateway; S7-1200 G2 support |
| 8.3.3 | Perspective | `Intl.NumberFormat` replaces Numeral.js; Table `canceledValue` / `originalValue` script params; Toggle Switch `color.disabled` |
| 8.3.3 | Security | **8.1 IdP exports can now be imported into 8.3**; Remote Secret Provider added |
| 8.3.3 | Redundancy | General Gateway Network settings editable on a backup Gateway |
| 8.3.3 | Reporting | Shift+right-click → Copy XML To Clipboard / Set XML From Clipboard |
| 8.3.3 | Scripting | `sizeCutoff` and `timeoutMs` on `system.kafka.pollPartition` / `pollTopic` |
| 8.3.3 | SECS/GEM | SECS/GEM Gateway pages available when the module is installed |
| 8.3.3 | Tags | `deploymentMode` System Tag added |
| 8.3.4 | Gateway | `route-actor` MDC key on log messages; `ignition.resources.digest.pruning` system property |
| 8.3.4 | Gateway Network | 60-second enumeration call replaced by an event-based system |
| 8.3.4 | Historian | Core Historian `server.conf` and `log.conf` auto-created |
| 8.3.4 | JxBrowser | → 8.16.0; `ignition.jxBrowser.sandboxMode` system property |
| 8.3.4 | OPC UA | Force Secure Connection → **Secure Connection Mode** (Siemens Enhanced) |
| 8.3.4 | Perspective | Drawing `typeAttr`; read-only `currentBreakpoint` on Breakpoint/Column containers; Form number `step: any` |
| 8.3.4 | Tags | DNP3 / DNP3 (Legacy) IIN diagnostic tags; wildcards in Tag Event source and Gateway Tag Change script paths |
| 8.3.4 | User Sources | Upgrade detects duplicate users, logs, and **skips** migration |
| 8.3.5 | Cloud Edition | Available as an **AWS Marketplace container product** via EKS |
| 8.3.5 | Docker | `jq` added to the image |
| 8.3.5 | Event Streams | `Ready` stage state; `previousValue` in Tag Event metadata; `HTTP Version` handler property |
| 8.3.5 | Gateway Network | Remote Gateways tab on the Connections page |
| 8.3.5 | Leased Licensing | Activation tokens accepted even when pasted wrapped in quotes |
| 8.3.5 | OPC UA | GDS Push Enabled property on Ignition's OPC UA Server |
| 8.3.5 | Perspective | File Upload `enabled`; Drawing `onElementClicked`; Radio Group `enabled`/`style`; **XY Chart `bullets.height`/`width` removed, replaced by `bullets.radius`** |
| 8.3.5 | Scripting | New param on `system.tag.getConfiguration` for overridden UDT member properties; `system.historian.types.*` builders |
| 8.3.5 | Security | **File Secret Provider** added |
| 8.3.6 | — | *"Ignition version 8.3.6 only contains a patch for an issue found in 8.3.5."* |
| 8.3.7 | Alarming | Consolidation section on Simple One-Way Email profiles; automatic Twilio reconnection |
| 8.3.7 | Designer | `-Dignition.designer.websocketMaxBinaryMessageSize` default 2048 KB → **4096 KB** |
| 8.3.7 | OPC UA | PLC symbol export from Siemens Enhanced symbolic connections |
| 8.3.7 | Perspective | Expressions usable as dynamic Query Binding paths |
| 8.3.7 | SFC | Dedicated Notes tab for Transitions, Parallels, Actions, Assertions, Enclosings |
| 8.3.7 | Security | **Create Project Permission deprecated** |
| 8.3.7 | User Sources | Legacy Naming Enabled property on AD-family user sources, to improve 8.1 migration |
| 8.3.8 | Event Streams | Project Browser status icons (running / modified / disabled / failed) |
| 8.3.8 | Gateway | Optional **Restore from Backup** step in the installer |
| 8.3.8 | Gateway | Active deployment mode logged at startup |
| 8.3.8 | Gateway | Redundant internal-DB automatic backup and VACUUM disabled for faster startup; resizable large text boxes |
| 8.3.8 | Historian | "Number of past partitions queried for seed values" setting |
| 8.3.8 | Perspective | Form Dropdown widget gains `search` / `showClearIcon` / `allowCustomOptions`; Form File Upload widget |
| 8.3.8 | Scripting | Jython **2.7.3 → 2.7.4** |
| 8.3.8 | Scripting | **`system.config` namespace added** (copy/create/delete/move/rename/replace/retrieve Gateway resource configs) |
| 8.3.8 | Scripting | `system.secrets.createEmbeddedSecretConfig`, `createReferencedSecretConfig`, `readConfiguredSecretValue` |
| 8.3.8 | SFC | Expression language + Insert Tag/Operators/Functions buttons on Parallel Element Cancel Condition |
| 8.3.9 | BACnet | System property controlling concurrent manifest reads |
| 8.3.9 | Docker | Runtime argument to restore local-only config files from a Gateway backup |
| 8.3.9 | Embedded Java | Java Service Wrapper 3.5.60 → **3.6.5** |
| 8.3.9 | Gateway | Redundancy page accessible with read permissions |
| 8.3.9 | Gateway | System property to opt out of automatic gzip on Designer/Vision↔Gateway RPC |
| 8.3.9 | Gateway | System property to choose module-bundled vs host OpenSSL for IEC 61850 |
| 8.3.9 | Gateway | `web.xml` `max-file-size` default **20 MB → 128 MB** |
| 8.3.9 | OPC UA | Eclipse Milo → **1.1.6**; server diagnostics now need `ConfigureAdmin` or `SecurityAdmin` |
| 8.3.9 | OPC UA | Sampling tags for the Siemens Enhanced driver |
| 8.3.9 | OPC UA | **IEC 61850 addressing changed** — shared-FC attributes get separate nodes with `[FC]` suffix; *"Tags on affected addresses must be re-addressed after upgrading."* |
| 8.3.9 | Scripting | **Parameter syntax updated** for `system.historian.queryAggregatedPoints`, `queryRawPoints`, `browse` |
| 8.3.9 | Tag Browser | Alarm Metrics folder at the tag-provider level |
| 8.3.9 | Tag Browser | Multi-Instance Wizard **"List of Names" pattern type restored** (removed in 8.3.0) |

---

## Confidence notes

Everything above is quoted or paraphrased from the 8.3 / 8.1 / deprecated
manuals. The following are inferences, judgement calls, or known gaps —
flagged so they are not mistaken for verbatim doc statements.

1. **The `system.gui` → `system.vision` rename map is reconstructed, not
   quoted.** The manual states the *principle* (the `system.vision` namespace
   replaces Vision-scoped functions from `system.gui`, `system.nav`,
   `system.file`, `system.net`, `system.print`, `system.security`,
   `system.util`, `system.dataset`, `system.tag`, `system.db`) and the
   Deprecated manual gives explicit `system.tag`, `system.dataset` and
   `system.db` mappings. The per-function `system.gui` / `system.nav` table was
   built by diffing the 8.1 and 8.3 sitemaps: every `system-gui-*` /
   `system-nav-*` page present only in 8.1 was matched to its
   `system-vision-*` counterpart present only in 8.3. The re-homings with
   identical leaf names are near-certain. The **renames** (`messageBox` →
   `showMessage`, `errorBox` → `showError`, `warningBox` → `showWarning`,
   `confirm` → `showConfirm`, `inputBox` → `showInput`, `passwordBox` →
   `showPasswordInput`, `chooseColor` → `showColorInput`, `openDiagnostics` →
   `showDiagnostics`, `isTouchscreenModeEnabled` → `isTouchscreenMode`,
   `setTouchscreenModeEnabled` → `setTouchscreenMode`, `getOpenWindowNames` →
   `getOpenedWindowNames`, `getOpenWindows` → `getOpenedWindows`) are inferred
   from name correspondence and are highly likely but were not individually
   verified against each function page. One rename **was** verified directly:
   `system.db.refresh` → `system.vision.refreshBinding`, whose page carries a
   Backwards Compatibility callout saying so.

2. **`system.db.clearCache` vs `system.db.clearQueryCache` is a doc
   inconsistency, not a finding.** The 8.1→8.3 upgrade guide's table says
   `clearCache`; the New-in-this-Version page and the Deprecated manual both
   say `clearQueryCache`; only `system-db-clearQueryCache` exists as a page in
   the 8.3 tree. I have recommended `clearQueryCache` on that basis. Verify
   against your actual build.

3. **Store and Forward vs the Core Historian.** Two pages phrase this
   differently. `tag-history-providers` says the Core Historian *"does **not**
   use Store and Forward"* flatly; the upgrade guide says it *"will only use the
   Store and Forward system if there are pending writes."* I have reported both
   rather than reconciling them. Do not rely on Store-and-Forward buffering
   semantics for Core Historian writes.

4. **The `scopes` pages carry no prose.** `/docs/8.3/scopes` and its three
   children render as a client-side "Functions by Scope" index with no
   Markdown mirror (the `.md` endpoints 404). The scope counts quoted in the
   executive summary (Gateway 338→367, Perspective Session 325→332, Vision
   Client 351→356) were read from the rendered pages at `/docs/8.1/scopes` and
   `/docs/8.3/scopes` on 2026-09-22. They are a coarse signal only — the 8.3
   number counts deprecated-but-present functions alongside new ones, so it is
   **not** a count of net-new functions.

5. **The path diff counts are sitemap-based.** 1,519 (8.1) vs 1,574 (8.3),
   169 only-8.1 and 224 only-8.3, from
   `https://www.docs.inductiveautomation.com/sitemap.xml`. A page can be
   restructured without changing its path, so the diff undercounts content
   change; conversely a pure URL reshuffle shows up as both a removal and an
   addition. The "moved" table pairs them by judgement, not by any redirect
   map the site publishes.

6. **Heading-diff limits.** For ~25 concept pages I compared H1–H4 sets between
   `/docs/8.1/<path>.md` and `/docs/8.3/<path>.md`. Several pages
   (`ignition-modules/perspective`, `ignition-modules/vision`,
   `platform/alarming`, `platform/tags`, `platform/projects`,
   `platform/designer`, `platform/scripting`,
   `platform/security/identity-provider-authentication-strategy`) came back with
   **identical headings and near-identical byte counts** — meaning the overview
   prose is essentially unchanged in 8.3, with the substance of the change
   living on child pages. Absence of a heading diff is therefore not evidence
   that a subsystem is unchanged.

7. **Web search was used only for orientation.** Searches surfaced Inductive
   Automation's release-notes pages (8.3.0 through 8.3.9), the 8.3 launch
   announcement, the "Ignition 8.3" what's-new marketing page and two ICC 2024
   sessions. **No claim in this document rests on those pages** — every item is
   grounded in the docs site. Anything the release notes or marketing pages
   assert that the manual does not (for example exact GA dates, performance
   figures, or module pricing) is deliberately absent here and should be treated
   as unconfirmed.

8. **Deliberately not covered in depth**, because the manual does not frame them
   as 8.1→8.3 changes: the per-component Perspective and Vision property
   inventories (in the sibling `perspective-components.md` /
   `vision-components.md` references), the full expression-function list, and
   SFC / Reporting internals beyond what the changelog names.

9. **"Latest version" is a moving target.** This document reflects the docs as
   of **2026-09-22**, with **8.3.9** the newest release documented. The
   `new-in-this-version` page is versioned and grows; re-read it before
   targeting a build newer than 8.3.9.

10. **The Deprecated manual is the authority for removals.** It states its own
    contract: *"Deprecated functionality is still available inside Ignition to
    maintain backwards compatibility, but may otherwise be hidden... Other
    features, such as the Tag Editor or the Alarming system, have been reworked
    in a way that when the Ignition version is updated, the old functionality is
    completely removed."* Where I have listed something as "removed" rather than
    "deprecated", it is because a 8.3 page says so explicitly (hot swapping,
    Agent Recovery, the Serial and Web Browser modules, XY Chart bullet
    height/width, the old theme entry-point files, x86 Mac launchers). Treat
    everything else in the Deprecated manual as still functional but unsupported
    for new development.

---

## Verification pass — corrections (2026-09-22)

An adversarial re-check against the live manual corrected five claims that appear
above (and are widely repeated elsewhere). Where this section disagrees with the
body above, **this section is correct**.

1. **`system.gui` / `system.nav` are deprecated, not removed.** Their 8.3 manual
   pages 404 (they live in the deprecated docs version), but the functions still
   run: *"Many of the replaced system functions are still functional, but it is
   recommended to utilize the `system.vision` namespace instead."*
   `system.vision` absorbed functions from **seven** namespaces — `system.file`,
   `system.gui`, `system.nav`, `system.net`, `system.print`, `system.security`,
   `system.util`. Two have **no replacement**: `system.gui.convertPointToScreen`
   and `system.gui.getQuality`.
   Source: `getting-started/installing-and-upgrading/ignition-8-upgrade-guide/81to83-upgrade-guide`.

2. **Historical path syntax — full form.** The recommended form is
   `histprov:<provider>:/sys:<gateway>:/prov:<tagProvider>:/tag:<folder/tag>`.
   The SQL Historian does not merely "still accept" the `drv` form — it
   **requires** it: *"this format will not work for the SQL Historian, as this
   historian requires the `drv` key-value pair to be used."*
   SQL form: `histprov:Sample_DB:/drv:myGateway:myProvider:/tag:Folder/New_Folder`.
   Source: `appendix/scripting-functions/system-historian`.

3. **Resource collection order.** Inheritance runs
   `system` → `external` → `core` → `{deployment mode}`. The `local` collection is
   **not** the last link in that chain — it is a sibling holding host-specific
   data (certificates, Gateway Network UUID): *"Your deployment modes will not
   inherit anything from the local collection, but will use the data within the
   local collection to function properly on each respective machine."* Overrides
   placed in `local` do not carry to a redundant backup.
   Mode is set with `wrapper.java.additional.x=-Dignition.config.mode=<NAME>` in
   `data/ignition.conf`, and requires a Gateway service restart.
   Source: `platform/gateway/web-interface/platform/gateway-deployment-modes`.

4. **Perspective Session is a distinct scope, not Gateway scope.** Perspective
   scripts do execute on the Gateway rather than in the browser, but the manual is
   explicit that *"this scope is still distinct from the Gateway scope"* — the
   available function sets differ (Perspective Session 332 vs Gateway 367).
   Source: `platform/scripting/scripting-in-ignition`.

5. **7.9 → 8.3 is strongly discouraged, not formally unsupported.** The docs say
   it is *"strongly advised"* to upgrade to the latest 8.1 first, and that there
   *"will be compatibility issues"* if going directly (Gateway Network,
   serialization, data syncing/communication/storage). The only "not a supported
   use case" language in this area concerns **downgrading**.
   Source: `81to83-upgrade-guide`, `getting-started/installing-and-upgrading`.

Additional details confirmed in the same pass:

- Mixed 8.3/8.1 Gateway Network fleets rely on the webserver's
  **Allow Java Serialization** property, which is auto-enabled on upgrade or
  restore and must stay enabled while any 8.1 peer remains.
- `Require Two-Way Authentication` defaults to `true` **for new installs**.
- `system.dataset.toPyDataSet` is deprecated (page 404s); `toDataSet` is now
  spelled `system.dataset.toDataset` with a single syntax.
- Scope function counts confirmed from `appendix/scripting-functions`
  ("Functions by Scope"): Gateway 367, Vision Client 356, Perspective Session 332.
- `system.tag.readBlocking` timeout defaults to 45000 ms.
- `system.eventstream` is Gateway-scope only, with `getDiagnostics`,
  `listEventStreams`, `publishEvent`. The Kafka source needs the Kafka module;
  the HTTP source needs Web Dev.
