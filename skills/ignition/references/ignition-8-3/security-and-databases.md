# Ignition 8.3 — Security, identity and databases

Compiled from the live Ignition 8.3 documentation (docs.inductiveautomation.com/docs/8.3), covering `platform/security/*` (~47 pages), `platform/database-connections/*` (~18 pages), `platform/sql-in-ignition/*` (~27 pages), and the appendix Database Table Reference.

---

## Security model overview

Ignition 8.3 security has two independent, largely non-overlapping **authentication strategies**, and understanding which one governs a given scope is the single most important mental model for this whole area:

| Strategy | Governs | Core concept |
|---|---|---|
| **Classic Authentication Strategy** | Designer, Vision Client (and Gateway, if selected) | **User Source** (users + roles + metadata), checked directly against a login form |
| **Identity Provider (IdP) Authentication Strategy** | Perspective Session, and optionally Designer/Vision/Gateway | An external or internal **Identity Provider** authenticates the user; Ignition then maps IdP response data to **Security Levels** via rules |

The docs state this explicitly and repeatedly: *"If you have Ignition 8.3 with the Perspective module, authentication is handled instead by the Identity Provider Authentication Strategy."* Perspective **cannot** use Classic Authentication — it is IdP-only. Vision and the Designer can use **either** strategy (selectable per-Gateway under **General Security Settings**), but Classic is their traditional default.

This is a major conceptual shift from 8.1, where "User Sources + roles" was the single unifying security model across all modules. In 8.3:

- **Classic Authentication Strategy** = User Sources (Internal / Database / Active Directory / hybrids / Fallback Cache) + Roles. Roles are flat strings checked against Designer/Vision permission fields.
- **Identity Provider Authentication Strategy** = IdPs (Internal / OpenID Connect 1.0 / SAML 2.0) + **Security Levels** (a *tree*, not a flat list) + **Security Level Rules** (expressions) + **User Grants** (per-user overrides) + **Security Zones** (network/location-based) + **Service Security** (per-service policy on a zone).

A **User Source** can still back an **Internal Ignition IdP** (the IdP delegates authentication of username/password to a User Source), so the two systems interlock — but the *authorization* model (roles vs. Security Levels) is different depending on which strategy is actually presenting the login challenge.

### The full picture, piece by piece

- **Identity Providers (IdP)** — Internal, OpenID Connect 1.0, or SAML 2.0. Configured at the Gateway level (`Platform > Security > Identity Providers`). An IdP authenticates the user and returns a **response document** (JSON for Ignition/OIDC, XML for SAML) containing claims/attributes.
- **User sources** — used by (a) Classic Authentication Strategy directly, and (b) as the backing store for an Internal Ignition IdP. Types: Internal, Database, Active Directory, AD/Internal Hybrid, AD/Database Hybrid, Fallback Cache.
- **User Attribute Mapping** — maps fields from the IdP response document (username, email, first/last name, roles) into normalized Ignition user attributes usable elsewhere (Session Properties, Security Level Rules).
- **Security Levels** — a hierarchical tree (`Platform > Security > Security Levels`) that Perspective (and IdP-mode Vision/Designer) actually checks for authorization. Reserved levels: `Public`, `Authenticated`, `Authenticated/Roles`, `SecurityZones`.
- **Security Level Rules** — expressions attached to *custom* Security Levels that return True/False to decide whether a user falls into that level. Can reference IdP response attributes, mapped user attributes, tag values, and Security Zones.
- **User Grants** — a manual override table that assigns specific Security Levels to specific users (by username or IdP-provided ID), bypassing the Security Level Rules entirely.
- **Security Zones** — group Gateways/computers/IP addresses on the Gateway Network into named zones with priority ordering; used for **location-based** (not identity-based) access control.
- **Service Security (Policies)** — per-Security-Zone policies gating specific Gateway *services*: Alarm Journal, Alarm Notification, Alarm Status, Audit Log, Diagnostic Services, EAM License Management, History Provider, Secret Provider, Tag Access.
- **Secrets Management** — a new-in-8.3 layered encryption system (Root Key → Key Encryption Key set → per-secret encryption) with pluggable **Secret Providers** (Internal, Remote, File) as an alternative to "Embedded" (in-place encrypted) passwords.

### How each surface authenticates/authorizes

| Surface | Authentication | Authorization |
|---|---|---|
| **Perspective Session** | IdP only (Internal/OIDC/SAML) | Security Levels (via Security Level Rules + User Grants); `system.perspective.login/logout/isAuthorized` |
| **Vision Client** | Classic (User Source) **or** IdP, selectable | Classic: Roles. IdP: auth token generated on login, stored in Client memory (not Gateway-backup-persisted); roles from IdP mapped under `Authenticated/Roles` |
| **Designer** | Classic **or** IdP, selectable at `Platform > Security > General Settings > Designer Authentication Strategy` | Classic: `System User Source` + required Role(s). IdP: `Permissions` (Security Levels, any/all match), plus per-project Designer Roles/Permissions (View/Save/Delete/Protect Resources) |
| **Gateway web UI** | System Identity Provider (drives Designer/Gateway config UI login) or Classic | Gateway Read/Write/Access Permissions (Security Levels, any/all match) |
| **Gateway REST/HTTP API** | API Keys (`X-Ignition-API-Token` header) | Security Levels assigned to the key |
| **Service-to-service (Gateway Network)** | N/A (network identity) | Security Zones + Service Security policies |

---

## Identity Providers

### Types and the authentication workflow

Three IdP types: **Internal** (Ignition acts as its own IdP, backed by a User Source), **OpenID Connect 1.0**, and **SAML 2.0**. All are configured at `Platform > Security > Identity Providers > Create Identity Provider +`.

Registering the Gateway with a third-party IdP requires a **redirect URI** (same URI is used for login and logout):
```
http://yourGatewayAddress:Port/data/federate/callback/oidc   # OIDC
http://yourGatewayAddress:Port/data/federate/callback/saml   # SAML
```
Always use HTTPS versions of these URIs in production (requires SSL/TLS enabled with a valid certificate on the Gateway).

**Workflow**: (1) user attempts login to Gateway/Perspective/Designer/Vision → (2) Ignition detects IdP auth is required → (3) redirect to IdP → (4) IdP authenticates (username/password, MFA, etc.) → (5) user responds to challenge → (6) IdP redirects back to Ignition with a response document → (7) Ignition maps the user to Security Levels using that document.

IdPs can be **imported/exported** as JSON files (three-dots menu). 8.1 Gateway IdP exports import cleanly onto 8.3 as of 8.3.3+ (not supported prior).

### Internal Ignition IdP

Delegates credential checking to a configured **User Source**. Properties: `User Source`, `Session Inactivity Timeout`, `Session Expiration`, `Remember Me Expiration`, `Authentication Methods` (username/password and/or Badge). Built-in expression attributes: `auth_time` (last-auth timestamp), `challenged` (bool — did the user actually re-enter credentials on last login, vs. resuming an existing session).

**Remember Me** caveats: broken by a Gateway version upgrade (some versions), and overridden entirely by the "Always ask the IdP to re-authenticate users by default" setting on General Security Settings.

### OpenID Connect 1.0 Providers

Preferred setup is **Import from URL** (`.../.well-known/openid-configuration`) or **Import From File** (JSON, per OpenID Connect Discovery 1.0 §3). After import you still manually enter **Client ID** / **Client Secret** obtained by registering Ignition as an application with the IdP.

Key properties: Authorization URL, Token URL, Logout URL (optional), JSON Web Keys URL (or static JWK set), User Info URL + HTTP method, Authorization Response Mode, Issuer, Supported ID Token Signing Algorithms, **Scope** (e.g. `email`, `profile` — controls what claims come back), JSON Web Key Config.

### SAML 2.0 Providers

Import via URL/XML metadata document (SAML 2.0 metadata schema). Ignition's SP metadata is served at:
```
http://<ip>:<port>/data/saml/metadata/sp
```
ACS (Assertion Consumer Service) callback: `http://<ip>:<port>/data/federate/callback/saml`. Ignition's SP implementation accepts both line-wrapped and non-line-wrapped Base64 SAML Responses.

Key properties: IdP Entity ID, SP Entity ID (auto-generated from hostname by default), ACS Binding, Name ID Format, SSO Service URL + Binding, Force Authn, Validate Response/Assertion Signatures, IdP Metadata URL (or static keys/certs).

### Redundancy

Both OIDC and SAML configs contain a **"Provider Metadata for Redundant Backup"** section. By default the backup Gateway node reuses the master's IdP settings; you can instead define separate backup-node metadata.

### User Attribute Mapping

Maps fields from the IdP response document into normalized attributes (ID, Username, First/Last Name, Email, Roles), which become Perspective **Session Properties**. Configured per-IdP at `Identity Providers > [IdP] > User Attribute Mapping`.

Two mapping types:

- **Direct**: pick a `Source` (a named part of the response document) + `Path` (slash-delimited path within that source).
- **Expression**: full Expression Language access, plus special built-in reference objects:
  ```
  {<Attribute Type>:<Attribute Source>:<Attribute Path>}
  ```
  - Attribute Type: `attribute-source` (single value) or `multi-attribute-source` (collection, e.g. roles).
  - Attribute Source names vary by IdP type: Ignition/OIDC → `idTokenClaims` (default), `tokenEndpointResponse`, `userInfo` (OIDC only, requires User Info URL configured); SAML → `authnResponse` (must be stated explicitly).
  - Attribute Path: JSON Path for JSON sources (Ignition/OIDC), **XPath 1.0** for XML sources (SAML).

Example — extracting roles from a SAML XML AttributeStatement via XPath:
```
{multi-attribute-source:authnResponse:/saml2p:Response/saml2:Assertion/saml2:AttributeStatement/saml2:Attribute[@Name="Role"]/saml2:AttributeValue/text()}
```

Example — deriving first name by splitting a full-name claim:
```
split({attribute-source:idTokenClaims:name}, ' ')[0,0]
```

Roles mapping via `runScript` must return a Java `ArrayList`, not a Jython list:
```python
import java.util.ArrayList as ArrayList
roles = ArrayList()
roles.add("Operator")
```

Tag values can also feed a mapping (evaluated only at login time, not live): `{[default]A_Folder/A_Tag.value}`.

### Security Levels

A **tree** defined at `Platform > Security > Security Levels`. Each child level inherits its parent's security. Four **reserved** levels (cannot be renamed/deleted, no custom rules allowed):

- **Public** — granted to every session, authenticated or not; root ancestor of the tree; "guest" access.
- **Authenticated** — granted once the session successfully authenticates against the configured IdP.
- **Authenticated/Roles** — non-configurable placeholder parent; custom levels nested one level directly under it map by **exact name match** to roles returned by the IdP. A fresh Gateway auto-creates an `Administrator` role here.
- **SecurityZones** — non-configurable placeholder; auto-populated to mirror all Security Zones on the Gateway. Provides location-based permission modeling.

Only roles under `Authenticated/Roles` work with the **Classic** Authentication Strategy. **Custom Security Levels elsewhere in the tree do not work with Classic** — they're IdP-only. Placement matters: custom levels under `Public` (outside `Authenticated`) don't require the user to be logged in; custom levels *inside* `Authenticated` require login even if their rule expression doesn't reference IdP data.

Deleting a level cascades to all its children. Security Level configuration can be **imported/exported** as JSON.

### Security Level Rules

Defined per custom Security Level as an expression returning True/False (`Identity Providers > [IdP] three-dots > Security Level Rules`). Full Expression Language available, plus special objects only available in this context:

| Reference | Meaning |
|---|---|
| `{user:id}`, `{user:userName}`, `{user:firstName}`, `{user:lastName}`, `{user:email}`, `{user:roles}` | Mapped User Attributes (require User Attribute Mapping configured) |
| `{security-zones}` | Collection of zones the connection currently falls into |
| `{security-level-name}` | Name of the level being configured, e.g. `"Administrator"` |
| `{security-level-path}` | Full path, e.g. `"Authenticated/PlantA/Administrator"` |
| Response Attributes | Same `{attribute-source:...}` / `{multi-attribute-source:...}` syntax as User Attribute Mapping |

Special functions (not available in normal expression bindings): `containsAll(collection, el0, ..., elN)` and `containsAny(collection, el0, ..., elN)` — the idiomatic way to test zone/role membership:
```
containsAny({security-zones}, 'PlantA', 'Floor1', 'Press Room')
containsAll({idp-attributes:amr}, 'uname', 'pwd')
```

Response/User Attributes are **only available to levels within the `Authenticated` branch** — a level outside `Authenticated` can only see tag values and Security Zones. Security Levels are evaluated **once, at initial login**; a rule referencing a tag value won't retroactively update already-logged-in sessions if the tag changes.

The `amr` attribute (Ignition IdP) reports how the user authenticated: `["uname","pwd"]`, `["badge"]`, or `["badge","pwd"]` — usable to gate levels by authentication method strength.

### User Grants

Manual overrides that assign Security Levels to a specific user **regardless of** whether their Security Level Rules would grant it (`Identity Providers > [IdP] > User Grants`). Users identified by username or IdP-provided ID — entered **exactly**, case-sensitive, with **no validation** against the actual IdP (a typo silently grants nothing). Grants can target levels outside the `Authenticated` branch and only take effect once the user actually authenticates.

### Test Login and Logout

`Identity Providers > [IdP] three-dots > Test Login` walks the real IdP redirect flow and shows: raw **IdP Response Data**, **Mapped User Attributes**, and **Security Level Grants** for the test session. Essential for debugging attribute-mapping paths and rule expressions before shipping. `Test Logout` also logs out of the upstream IdP where supported (Ignition IdP always; OIDC only if a Logout URL is configured).

### IdP expression functions & troubleshooting quick reference

Common failure → fix table (from Troubleshooting Identity Providers):

| Symptom | Likely cause / fix |
|---|---|
| Save Changes button disabled | A required field (marked `*`) is empty — enter placeholder values for Client ID/Secret if not yet known |
| Metadata file import doesn't populate fields | File isn't valid JSON, or import URL is wrong — re-import |
| IdP login page never appears | Client ID / Client Secret incorrect |
| Login accepted but redirect back to Ignition fails (HTTP 500, OIDC) | Check Supported ID Token Signing Algorithm Values, Token URL, JSON Web Keys URL, Issuer URL — re-import metadata after each fix |
| Test succeeds but no username/email in results | Add fields to **Scope** |
| Not redirected back after successful login | Verify Authorization URL, re-import metadata |

### Auth Token Connection Recovery

On IdP login, a Gateway-issued auth token is cached in Designer/Vision Client **instance memory** (never in Gateway Backups — a restore clears all existing tokens). On a dropped-then-recovered connection, the client resumes the session by presenting this token instead of re-authenticating. Tunable via `User Inactivity Timeout` / `Time-To-Live (TTL)` — Designer settings live on **General Security Settings**; Vision Client settings live in **Project Properties > Vision > Login**. In a redundant pair, Vision auth tokens sync Master→Backup so failover doesn't force re-login.

---

## User sources and roles

**Classic Authentication Strategy** — Designer and Vision Client only (in 8.3, if Perspective is licensed, Perspective *cannot* use Classic).

### Types

| Type | Users managed | Roles managed | Notes |
|---|---|---|---|
| **Internal** | In Gateway | In Gateway | Included in Gateway Backups; no external system needed; supports password policy enforcement |
| **Database** | In external SQL DB | In external SQL DB | **Automatic mode**: Ignition creates/manages tables (prefix configurable). **Manual mode**: you supply every query (Authentication, Badge Auth, List Roles, User's Roles, Find User, List Users, Contact Info, Schedule Adjustment, Extra Properties) |
| **Active Directory** | In AD (LDAP) | AD **Groups** = Ignition roles | Not manageable in Ignition at all; supports SASL |
| **AD/Internal Hybrid** | AD (credentials) | Internal (roles, contact info, schedules) | "Best of both worlds" — AD validates login, Ignition owns role assignment without IT involvement |
| **AD/Database Hybrid** | AD (credentials) | External DB (roles etc.) | Same idea, roles live in SQL instead |
| **Fallback Cache** | N/A — auto-populated | N/A | Only works with **Classic** strategy and **Local (Vision) Client Fallback**; caches credentials pulled from a remote User Source over the Gateway Network so a Vision Client can still authenticate when disconnected. Not compatible with the IdP strategy. |

Shared functionality across all types: **Failover Source** (secondary User Source consulted on outage, with **Hard** = only on unreachable vs **Soft** = also on bad credentials), **Schedule Restrictions** (block login outside an assigned schedule), account **Lockout** (attempts/window, default 5 attempts / 15-minute window; a negative value disables it entirely), **Cache Validation Timeout** (default 15 min).

### Active Directory specifics

Auth over LDAP; supports SSL (`ldaps://`, port 636 vs plaintext 389), SASL, nested-group lookups, badge-based auth (via `Badge Attribute` + `Badge Search Filter`). **`Allow Anonymous` is a real security risk if left enabled** — the docs flag it explicitly: some AD configurations accept blank-password binds as valid when Security Authentication is `NONE` or `SIMPLE`, even for a non-existent username. `SSO Enabled` for AD was **deprecated and disabled by default since 8.1.17** over a security vulnerability; it can still be forced on with a system property but this is explicitly not recommended.

Filters like **User List Filter** only control what's *displayed* in pickers — they are not an authentication boundary. A filtered-out user can still log in. Project security must independently restrict access.

### Database user source — password handling

Automatic mode encrypts stored passwords with **SHA1**. Scripted password-change pattern:
```python
from com.inductiveautomation.ignition.common.util import SecurityUtils
encryptPass = SecurityUtils.sha1String(newPass)
system.db.runPrepUpdate("UPDATE scada_users SET passwd = ? WHERE username = ?",
                         (encryptPass, username), 'database_connection')
```
Recommended pattern validates current credentials first via `system.security.validateUser(username, password)` before allowing the change.

### Managing users and roles

Gateway path: `Platform > Security > User Sources > [source] three-dots > Manage Users`. Also available inside Designer/Client via the Vision **User Management** component — but by default it **cannot** modify the Gateway system user source (prevents users locking themselves out); enable `Allow User Administration` on General Security Settings to allow it.

**Role hierarchy is manual**: Ignition doesn't nest Classic roles — you approximate a hierarchy by assigning a "senior" role plus all the roles it should imply (e.g., grant Supervisor *both* Administration and Maintenance).

> **Danger, quoted directly**: role-based project security stores the role **name as a string**. Renaming a role in the Gateway does **not** propagate — the project keeps searching for the old name and access silently breaks.

### Verify a User on a User Source

`User Sources > Verify User Source` — pick a profile, enter username/password, `Test Login`. Confirms credential validity and dumps user roles/metadata without needing a live client.

---

## Security zones and service security

### Security Zones

A named group of Gateways/computers/IP addresses on the **Gateway Network**, used to apply **location-based** policy (as distinct from Security Levels, which are identity-based). `Platform > Security > Security Zones`.

- **Priority**: when a connection matches multiple zones, the **highest-priority zone's policy wins** entirely (not merged).
- **Identifiers** (any one match is sufficient to enter a zone): IP Addresses (comma list, `*` wildcard, ranges like `100.100.1-100.0-255`), Host Names (wildcard supported), Gateway Names (note: when identifying through a proxy Gateway, IP = the proxy's IP, but Gateway Name = the actual target Gateway's name).
- **Qualifiers** (ALL must pass): Require Secure Connection, Direct Connection Required, Allow Client/Designer/Gateway Scope.
- A special **Default** zone always exists, can't be modified, and catches anything matching no other zone.
- Project-stored zone names have the same fragility as role names — renaming a zone breaks zone-based project security silently (explicit `caution` in the docs).

### Service Security (Policies)

Defined per Security Zone (`three-dots > Manage Policy`); the **Default Security Zone cannot have a custom policy** (fixed defaults: allow Alarm Ack, query-only History, read-only Tags, no Notification Pipelines).

Services gated: **Alarm Journal Access**, **Alarm Notification**, **Alarm Status**, **Audit Log Access**, **Diagnostic Services**, **EAM License Management**, **History Provider Access**, **Secret Provider Access**, **Tag Access**. Every service has a master `Service Access: Allow/Deny` switch — Deny overrides all other settings for that service in that zone regardless.

Notable **Tag Access** properties:
- `Trust Remote Security Levels` — if checked, a remote Gateway's own Security Levels (passed over the Gateway Network) are honored for local tag access decisions. If unchecked, the remote's Security **Zone** + an **Impersonation Role Name** are used instead.
- Access Level per Tag Provider: `ReadWriteEdit` / `ReadWrite` / `ReadOnly` / `None` / `Inherited` (falls back to Default Provider Access Level — **not recommended to leave at Inherited**, since new providers/journals/history providers are auto-added with `Inherited`, silently exposing new resources under whatever the default happens to be).

---

## Secrets management

New/substantially expanded system in 8.3. Two parallel mechanisms:

### Embedded secrets (default, always available)

Every fresh install ships a **default shared encryption key** — every Ignition installation starts out with the *same* key, so it is not a secure baseline on its own. Embedded secrets replace plain password fields Gateway-wide: choose **None** / **Embedded** / **Referenced** wherever a Gateway system needs a credential. An Embedded secret, once saved, is encrypted and **cannot be viewed again** by any user — only reset via "Update Password".

### Customized Secrets Management system (opt-in, recommended for production)

You must explicitly **opt in** (via the CLI tool) to move beyond the default shared key. Layering, root → leaf:

1. **Root Key** — encrypted, stored as `root.json`.
2. **Encryption Key Set** (3 rotatable keys) — stored as `kek.json`, itself encrypted by the Root Key.
3. **Environment password** — decrypts `root.json`; deliberately kept **out of the system by default**, supplied only via environment variables:

   | Variable | Purpose |
   |---|---|
   | `IGNITION_ROOT_KEY_PASSWORD_FILE` | Path to a file holding the password |
   | `IGNITION_ROOT_KEY_PASSWORD` | The password directly |

Startup sequence, verified on **every** Gateway boot: (1) `/data/config/ignition/keys` must contain `root.json` and `kek.json`; (2) env password decrypts `root.json`; (3) Root Key decrypts `kek.json`. If the directory is absent but an env password *is* set, a brand-new Root Key + Key Set are generated automatically. Losing the environment password means **nothing can be decrypted** and the Gateway fails startup verification.

**Redundancy gotcha (explicit caution in docs)**: `root.json` and `kek.json` must be applied to **both** Master and Backup nodes — otherwise embedded secrets encrypted on one node won't decrypt on the other.

### Secret Provider types (for "Referenced" secrets)

| Type | Behavior |
|---|---|
| **Internal** | Ignition-managed, file-backed, embedded-secrets strategy under the hood; named secrets can be reused across multiple configs by referencing the same name |
| **Remote** | Reads secrets from a Secret Provider on another Gateway over the **Gateway Network**. Defaults to **deny**; must be explicitly allowed via the target zone's **Secret Provider Access** service policy |
| **File** | Reads from a file on disk. **Cleartext** = raw file bytes, no trailing newline (works well with orchestrated secret mounts — Kubernetes Secrets, HashiCorp Vault, AWS/Azure Secrets Manager). **Ciphertext** = a JSON Web Encryption blob, same format as embedded secrets, producible via `system.secrets.encrypt` or the `/data/api/v1/encryption/encrypt` REST endpoint — if shared between systems, both must hold the same encryption key |

Switching an existing Embedded password to Referenced later is a simple Edit-panel change — no need to plan Secret Providers up front.

### Secrets Management Key CLI Tool

Shipped with every install: `ignition-secrets-tool.bat` (Windows) / `ignition-secrets-tool.sh` (*NIX). Subcommands generate/reset/rotate the Root Key and Key Encryption Key sets. Common flags: `-f/--force` (overwrite), `-p/--password[=<pass>]`, `-r/--root=<value>`.

### system.secrets scripting

Secret Providers support scripted `system.secrets` functions to encrypt/decrypt data, browse configured providers, and list secrets by provider — useful for programmatically referencing secrets rather than hardcoding.

---

## Designer and gateway security

### Gateway General Security Settings (`Platform > Security > General Settings`)

- **System Identity Provider** — the IdP controlling the Gateway web config UI and (if selected) the Designer. Can force "always re-authenticate" (disables SSO).
- **Designer Authentication Strategy** — `Classic` (embedded login form against the System User Source + required Role(s)) or `Identity Provider` (browser redirect; governed by the same Permissions/Security-Level model as Perspective, with its own Auth Token Inactivity Timeout / TTL).
- **User Inactivity Timeout** — Gateway web session timeout (≤0 disables).
- **Allow User Administration** — required before the Vision User Management component, or any script, can alter the Gateway's system user source/roles. Default **false**.
- **Gateway Read/Write/Access Permissions** — Security-Level-gated. Write ⊇ Read ⊇ Access implicitly (granting Write also grants Read; granting Read also grants Access) regardless of individual field settings. `Public` = everyone.
- The **Create Project Permission** setting was **deprecated in 8.3.7**, folded into the Designer Roles/Permissions model.

### Project Security in the Designer

Per-project **Required Designer Roles**, set in `Project > Properties > Permissions`: **View**, **Save**, **Delete**, **Protect Resources** — each a comma-separated role list, at-least-one-match semantics. The Designer does **not poll for role changes** — a user whose roles change mid-session must relaunch the Designer.

**Resource protection**: right-click any Project Browser resource → **Protect**. Protected resources can only be edited by users holding the roles named under "Protect Resources" — this restricts Designer-side editing only, has no effect on Clients, and is commonly used to freeze finished Templates/Alarm Pipelines while still allowing them to be *used*.

### API Keys

Bearer-style credential for the Gateway's HTTP API, distinct from IdP/user auth. `Platform > Security > API Keys`. The Gateway stores only a **hash** of the key; the raw value is shown **exactly once** at creation and cannot be retrieved again. Each key carries its own Security Level assignment (default: `Authenticated`, non-removable).

> **Caution, quoted directly**: *"API Keys grant full access to the Gateway's HTTP API routes, including the ability to modify configuration, tags, and projects."*

Usage: `X-Ignition-API-Token: <token>` header. Required for the newer resource-config routes (`/data/api/v1/resources`, `/data/api/v1/sync`, `/data/api/v1/modes`). Mutative calls (POST/PUT/DELETE) are audit-logged with user, IP, and key identity — **GET requests are never audited**, a gap worth knowing if you're relying on the audit log for full API visibility.

### OAuth 2.0 Clients

Distinct from IdPs — OAuth2 Clients are consumed by OAuth2 Email Profiles (SMTP auth via access token instead of a fixed password), configured at `Platform > Security > OAuth2 Clients`. One Client can back multiple Email Profiles. Redirect URI pattern: `http://host:port/data/oauth2/client/{name}/authorize/callback`. Supports the standard Authorization Code, Client Credentials, and Refresh Token grants, each independently testable via **Verify Authorization** / **Verify Token** panels before wiring into a real profile.

### Security Certificates

SSL/TLS is used throughout Ignition (Gateway web server, Gateway Network, OPC UA), but **certificate stores are per-feature and don't share configuration** even when features share a port — e.g. Gateway Network certs and Web Server certs must each be configured separately. Self-signed certs work everywhere as a stopgap; trusted-CA certs (internal or public) avoid browser/client warnings. Supplemental client-role trust certs (e.g. for a database or device the Gateway connects *out* to) are dropped into:
```
%gateway_install%/data/certificates/supplemental
```
(DER binary X.509 or Base64/PEM X.509) — Gateway restart required to pick them up.

---

## Database connections

### Supported databases (Full Support tier)

| Database | Driver | Translator | Min version |
|---|---|---|---|
| IBM DB2 | IBM DB2 (install required) | IBM DB2 | 9.5+ |
| MariaDB | Built-in / MariaDB module | MYSQL | All MariaDB, MySQL 5.5.3+ |
| MySQL | Built-in / MariaDB module | MYSQL | 5.0+ full; 4.x limited |
| MS SQL Server (Express incl.) | MSSQL module | MSSQL | 2005–2022 |
| Oracle | Install required | ORACLE | 10g/11g/12c (full & XE) |
| PostgreSQL | Built-in / module | POSTGRES | 8.0+ |
| Firebird | Install required | FIREBIRD | All |
| SQLite | Built-in | SQLITE | File- or memory-backed |

Any other JDBC-capable database has "Limited Support" — connect by adding your own JDBC driver + (if needed) a custom Translator.

Ignition upgrades **never modify manually-added JDBC drivers**; restoring a Gateway Backup **does** overwrite them with whatever was in the backup — you'll need to re-upgrade drivers post-restore. As of **8.3.2**, JAR file management for a driver moved from the Edit panel to a dedicated **Manage JAR Files** action; earlier 8.3.0/8.3.1 still use the old Edit-panel flow. Default JAR upload size cap is 128 MB (raised from 20 MB), tunable via `max-file-size` in `web.xml`.

### Connection configuration reference

**General properties**: Name (unique), Username, Password (None/Embedded/Referenced), Description, JDBC Driver (fixed post-creation), Connect URL, Extra Connection Properties (driver-specific — e.g. MSSQL requires `databaseName=` here), Enabled, **Failover Datasource** + **Failover Mode** (`STANDARD` = auto-reverts to primary once healthy; `STICKY` = stays on failover until *it* fails or Gateway restarts), Slow Query Log Threshold (default 60,000 ms), Validation Timeout (default 10,000 ms).

**Connection pooling** (Advanced): Initial Size (0), Max Active (8), Max Idle (8), Min Idle (0), Max Wait (5,000 ms, `-1` = wait forever).

**Connection testing**: Validation Query (must be a SELECT returning ≥1 row; default `SELECT 1`), Test on Borrow (true), Test on Return (false), Test While Idle (false), Eviction Rate (`-1` = evictor thread disabled), Eviction Tests (3), Eviction Time (1,800,000 ms).

**Connection Initialization**: arbitrary per-connection init commands (one per line, run on every pool checkout — e.g. Snowflake needs `USE DATABASE ...` / `USE SCHEMA ...` here for Tag History to store correctly), and Default Transaction Isolation Level.

### Per-database quirks worth remembering

- **MSSQL**: named-instance connections need the **SQL Server Browser** service running; Windows-Auth connections need the vendor `sqljdbc_auth.dll` copied into the Gateway's `lib` dir (`.../lib/core/gateway` does **not** survive upgrades — put it in `.../lib` instead) and the Ignition service's logon account changed. Extra Connection Properties: `databaseName=X` (SQL auth) or `databaseName=X;integratedSecurity=true` (Windows auth, blank username/password). Newer JDBC drivers (10.2+/11.2+) commonly need `trustServerCertificate=true`.
- **Azure SQL**: same MSSQL driver. Port 1433 = "Proxy" routing (simpler firewall, higher latency); port 3306 = "Redirect" (direct, lower latency, more open ports/IPs needed).
- **Oracle Express**: connection user **must** have `CREATE TRIGGER` and `CREATE SEQUENCE` grants, or the Historian, Audit Log, and any manual sequence-based inserts fail.
- **SQLite**: single connection at a time — the Gateway holds it continuously, blocking other clients. **Not recommended for production Historian use.** Connect URL keywords `${data}` and `${local}` resolve to Gateway data/local dirs; files under `${local}` are **excluded from Gateway Backups** — use `${data}` if you need the SQLite file backed up.
- **Snowflake**: does **not** support the Historian. Needs `--add-opens=java.base/java.nio=ALL-UNNAMED` added to Java startup args (Java 17 compatibility). Custom Translator required; blank many driver fields and rely on the translator.
- **MySQL**: prefer the built-in **MariaDB** driver even for MySQL 8 — avoids manually sourcing the official Connector/J JAR.

### JDBC drivers and translators

A **Translator** normalizes vendor SQL syntax differences (auto-increment syntax, quoting, LIMIT/TOP/ROWNUM placement, etc.) so the rest of Ignition can emit portable pseudo-SQL. Managed at `Connections > Databases > Settings`, Drivers and Translators tabs respectively. You only need a **new** Translator when adding a JDBC driver for a database that shares no syntax with an existing translator.

Translator token reference: `{tablename}`, `{indexname}`, `{primarykeydef}`, `{creationdef}`, `{alterdef}`, `{columnname}`, `{type}`, `{limit}`. Other settings: **Limit Position** (`Front`=after SELECT / `Back`=end of query / `Wrap`=e.g. Oracle's `rownum<=`), **Column Quote Character**, **Supports Returning Auto-generated Keys?** (if false, a `Fetch Key Query` is used instead).

Default translator cheat-sheet (Limit syntax / Auto-increment / Quote char):

| DB | Limit | Auto-increment | Quote |
|---|---|---|---|
| MySQL/MariaDB | `LIMIT {limit}` (Back) | `{type} NOT NULL AUTO_INCREMENT` | `` ` `` |
| MSSQL | `TOP {limit}` (Front) | `{type} IDENTITY(1,1)` | `"` |
| Oracle | `rownum<={limit}` (Wrap) | `{type} NOT NULL` + explicit sequence/trigger | `"` |
| PostgreSQL | `LIMIT {limit}` (Back) | `SERIAL NOT NULL` | `"` |
| IBM DB2 | `FETCH FIRST {limit} ROWS ONLY` (Back) | `{type} GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | `"` |
| Snowflake | `LIMIT {limit}` (Back) | `{type} NOT NULL AUTOINCREMENT` | (blank) |

### Monitoring & the internal database

`Connections > Databases > Connections` shows valid/errored connection counts, per-connection throughput, and (via **View Details**) active queries, longest-running queries, and connection-scoped log activity. Unavailable connections are retried every 10 seconds automatically. The **internal (embedded) database** is what a fresh Ignition install uses out of the box for its own metadata needs — separate from any project database connections you add.

---

## SQL in Ignition

### Where SQL shows up

Bindings (Named Query, DB Browse, straight SQL Query), Query Tags, Reports (Named Query Data Source), Transaction Groups (Expression Items and Stored Procedure Groups), scripting (`system.db.*`), and the Database Query Browser (Designer `Tools` menu — the standard place to test a query in isolation before wiring it into a resource).

Auto-generated-query systems (Historian, Alarm Journal, Database User Source) build and run their own queries against tables **you can still hand-query** — see the table reference below.

### Named Queries

The **default recommended mechanism** for any SQL a project needs. Conceptually parallel to Project Scripts: authored once in a dedicated Designer workspace, called by name (path) from anywhere. Execution **always happens on the Gateway** — the Client only ever sends a query name + parameter values, never SQL text, which is the core of why Named Queries are considered the most secure query mechanism in the platform.

**Workspace tabs**:
- **Settings** — `Enabled`, `Security` (rows of Security-Zone × Role combinations; blank Zone or blank Role, but not both, means "any"; a request matching none of the rows is refused outright — even a configured `Fallback` value on a ScalarQuery is **not** returned in that case, since the query never executes), `Description`, `Caching`.
- **Authoring** — Database Connection (`<Default>` / `<Parameter>` / a named connection — `<Parameter>` auto-exposes a special **Database**-type parameter, no manual creation needed), **Query Type** (`Query` = SELECT returning a dataset; `ScalarQuery` = SELECT returning one cell, supports a `Fallback` value on error; `UpdateQuery` = INSERT/UPDATE/DELETE, returns affected-row count), Parameters table, Query text field (with right-click **Parameterize > Make Value / Make QueryString**, and **Insert Parameter**), Table Browser (drag tables in, right-click **Create SELECT Statement**), and the **Query Builder** launcher (disabled when connection = `<Parameter>`).
- **Testing** — manual parameter values, **Use Sample Size Limit** (also caps that query's results everywhere else it's called from the Designer), **Execute Query**, **Export to CSV**.

**Parameter types**:
- **Value** — prepared-statement-style, referenced `:paramName`; cannot parameterize identifiers (table/column names); SQL-injection-safe by construction.
- **QueryString** — text-substituted, referenced `{paramName}`; *can* parameterize identifiers but values are **never sanitized** — explicitly flagged as injection-risky; avoid exposing these to free-text user input.
- **Database** — auto-created only via the `<Parameter>` Database Connection setting; not referenced in the query body at all, just selects which connection runs it.

File storage on the Gateway:
```
%installDir%/data/projects/<PROJECT>/ignition/named-query/<QUERYNAME>
```
(SQL + JSON metadata files.)

**Caching**: opt-in per query, disabled by default. A cache-hit returns without touching the database at all; separate cache entries are created per distinct parameter value combination (a query parameterized on `now()`-style expressions effectively never caches usefully, since every call gets a "new" timestamp). Update Queries **cannot** cache (their whole point is mutation). Designer-side test executions **never** use or populate the cache. Saving a change to a Named Query invalidates **all** its caches immediately, everywhere. Manual invalidation: `system.db.clearQueryCache`.

**Converting a SQL Query binding → Named Query**: the "Convert to Named Query" button on any SQL Query binding. All parameters come across as **QueryString** type by default — the docs strongly recommend manually converting each to a proper Value-type parameter afterward (removing surrounding quote marks in the query text, since Value params are pre-quoted like any prepared statement).

### Query bindings compared

| Binding | Security | Best for |
|---|---|---|
| **Named Query** | Zone/Role-gated on the Gateway; query text never leaves the Gateway | Anything reusable, anything security-sensitive, anything cacheable |
| **DB Browse** | None beyond the DB connection itself | Non-SQL-literate users building a simple table-driven query |
| **SQL Query** | None — full SQL text lives in the project, editable by anyone with Designer access | One-off / prototyping; convertible to Named Query later |

### Queries in scripting (`system.db`)

Prefer, in priority order: **Named Query execution** > **Prepared Statements** (`runPrepQuery`/`runPrepUpdate`, `?` placeholders) > raw string-built SQL (**avoid**).

```python
# Named Query — preferred; parameters passed as a dict
system.db.execUpdate("Add New Order", {"accountId": 123, "productName": "Bananas"})

# Prepared statement — safe, parameterized
query = "INSERT INTO orders (account_id, product_name) VALUES (?, ?)"
system.db.runPrepUpdate(query, [123, "Bananas"])

# NEVER build SQL by string concatenation with untrusted input:
# query = "SELECT * FROM users WHERE name = '" + userInput + "'"   # SQL injection
```

Function cheat sheet:

| Function | Use for |
|---|---|
| `system.db.execQuery` / `system.db.execUpdate` | Run a previously authored **Named Query** by name |
| `system.db.runPrepQuery` | Ad-hoc parameterized **SELECT**, returns a dataset (read-only) |
| `system.db.runPrepUpdate` | Ad-hoc parameterized **INSERT/UPDATE/DELETE**; returns affected-row count (or, per docs, can return the auto-generated key from an insert) |
| `system.db.createSProcCall` + `system.db.execSProcCall` | Stored procedure calls — the **recommended** approach over using `runPrepQuery`/`runPrepUpdate` for procedures |
| `system.db.beginTransaction` / `beginNamedQueryTransaction` | Open a transaction, get a `tx` id |
| `system.db.commitTransaction` / `rollbackTransaction` | End the transaction, apply or discard |
| `system.db.closeTransaction` | Invalidate the `tx` id (always call, even after commit/rollback) |
| `system.db.execUpdateAsync` / `runSFPrepUpdate` | Route writes through **Store and Forward** for resilience to transient DB/network outages |
| `system.db.refresh` | Force a bound component's data property to re-query |
| `system.db.clearQueryCache` | Invalidate one or all cached Named Query results |

**Transaction pattern**:
```python
transactionId = system.db.beginTransaction(timeout=5000)
query = "INSERT INTO orders (account_id, product_name) VALUES (?, ?)"
system.db.runPrepUpdate(query, [123, "Bananas"], tx=transactionId)
# ... more statements against the same tx id ...
system.db.commitTransaction(transactionId)   # or rollbackTransaction(transactionId)
system.db.closeTransaction(transactionId)
```
Statements inside an open transaction are **invisible to other connections** until committed.

**Stored procedure pattern**:
```python
myCall = system.db.createSProcCall("insert_new_order")
myCall.registerInParam(1, system.db.INTEGER, 123)
myCall.registerInParam(2, system.db.VARCHAR, "Bananas")
system.db.execSProcCall(myCall)
# result_set = myCall.getResultSet()   # if the procedure returns rows
```
Call syntax at the raw-SQL level is vendor-specific: SQL Server uses `EXEC dbo.myProc @param = value`; MySQL uses `CALL myProc(value)` (parens required even with zero params). **Postgres gotcha**: the JDBC connection string needs `escapeSyntaxCallMode=callIfNoReturn` or `execSProcCall`/Stored-Procedure-Transaction-Groups fail outright — otherwise fall back to a raw `CALL` query. **MySQL aliased-column gotcha**: a stored procedure returning aliased column names may come back with the *original* names unless the connection's Extra Connection Properties include `useOldAliasMetadataBehavior=true`.

### Query Builder

A drag-and-drop SQL builder (third-party, "Active Query Builder") reachable from Named Queries and Report Data. Understands multiple **Syntax Parsers** (per-vendor dialect, or "Universal") — opening a query written for MySQL's `LIMIT` while the parser is set to a dialect that doesn't recognize `LIMIT` throws a parse error; switch dialects or edit the offending line. Join creation is drag-a-column-onto-another-column; right-click a join line for JOIN-type properties (LEFT/RIGHT via "select all rows from" one side). The Columns Table supports per-column Aggregate (Avg/Count/Max/Min/Sum, optionally `Distinct`), Alias, Sort Type/Order, and Grouping with a Criteria-for-Values-vs-Groups toggle (the latter effectively becomes a `HAVING` clause).

### SQL query types (syntax reference)

**Core statements** — `SELECT`, `WHERE` (`=`,`<>`,`>`,`<`,`>=`,`<=`), `INSERT INTO ... VALUES (...)`, `UPDATE ... SET ... WHERE ...`, `DELETE FROM ... WHERE ...`. The docs are blunt about the two classic footguns: an `UPDATE`/`DELETE` with no `WHERE` clause touches **every row**; most DB management tools refuse to run one without a WHERE.

**WHERE clause operators**: `AND`/`OR` (AND binds tighter — use parentheses to force evaluation order), `NOT`, `BETWEEN x AND y` (inclusive both ends), `LIKE` with wildcards `%` (any run of characters) and `_` (exactly one character), `IN (...)` (shorthand for repeated `OR =`, and can wrap a subquery: `WHERE country IN (SELECT country FROM users)`).

**SELECT refinements**: static-value columns (`SELECT col1, 10 FROM table` — every row gets literal `10`), `SELECT DISTINCT`, `ORDER BY col [ASC|DESC]` (multi-column, evaluated left to right), row-limiting is **vendor-specific**: MSSQL/Access `SELECT TOP n` (also supports `TOP n PERCENT`), MySQL `LIMIT n`, Oracle `WHERE ROWNUM <= n`. Aliases via `AS` (multi-word aliases need quotes). `UNION` combines two SELECTs with matching column count/type (distinct rows only, name taken from the first SELECT); `UNION ALL` keeps duplicates.

**JOINs**: always qualify column names (`table.column` or an alias) once more than one table is in play. `JOIN ... ON a.col = b.col` (= INNER JOIN, only rows matching in both tables). `LEFT JOIN` keeps every row from the left table, NULLing right-side columns with no match. `RIGHT JOIN` is the mirror. `FULL JOIN` keeps unmatched rows from both sides — **MySQL has no FULL JOIN keyword**; emulate with `LEFT JOIN ... UNION ALL ... RIGHT JOIN ... WHERE <left-key> IS NULL`.

**Aggregate/GROUP BY**: `SELECT SUM(col1) FROM table GROUP BY col2` — an aggregate function paired with non-aggregated selected columns generally needs those columns in the `GROUP BY` list.

**Common functions** (availability varies by vendor — always check target DB docs): numeric `ABS`, `AVG`, `CEILING`, `COUNT`, `FLOOR`, `MAX`, `MIN`, `ROUND(val, places)`, `SUM`; string `CONCAT`, `LOWER`/`UPPER`, `LTRIM`/`RTRIM`/`TRIM`, `REPLACE(orig, target, repl)`, `SUBSTRING(str, startIdx[, len])` (1-based index); date `CURRENT_TIMESTAMP()`, `TIMEDIFF(newer, older)`; logic `COALESCE(v1,...,vN)` (first non-null), `ISNULL(expr)`, `NULLIF(e1, e2)` (returns NULL if equal, else `e1`).

**Comments**: `-- single line`, `/* multi\nline */`.

### Common task patterns

**Dynamic WHERE clause driven by a Dropdown** (Named Query parameter bound to a component property):
```sql
-- "0" reserved as the "all" sentinel value
SELECT * FROM machines WHERE area_number = :dropdownValue OR 0 = :dropdownValue
```
Bind the Named Query's `dropdownValue` parameter to the Dropdown's Selected Value, and turn **Polling Mode off** on the data binding so it only re-queries when the dropdown changes (not on a timer).

**Insert on button press** (Vision and Perspective use the same Named Query, different sibling-lookup syntax):
```python
# Vision
areaNum = event.source.parent.getComponent('Dropdown').selectedValue
machineName = event.source.parent.getComponent('Text Field').text
system.db.execUpdate("Insert Values", {"machineName": machineName, "areaNumber": areaNum})

# Perspective
areaNum = self.getSibling("Dropdown").props.value
machineName = self.getSibling("TextField").props.text
system.db.execUpdate("Insert Values", {"machineName": machineName, "areaNumber": areaNum})
```

**Refreshing a query after a write** — three different mechanisms depending on context:
```python
system.vision.refresh(component, "propertyName")      # Vision, force re-poll a specific binding
system.vision.refreshBinding(component, "data")        # Vision, alternate form used post-CRUD
self.refreshBinding("props.data")                       # Perspective component method — system.vision.refresh does NOT work here
```

**Deleting multi-selected table rows** — `getSelectedRows()` on Table/Power Table returns row indexes as a Python list:
```python
selRows = event.source.parent.getComponent('Power Table').getSelectedRows()
if len(selRows) > 0:
    if system.vision.showConfirm("Delete %d row(s)?" % len(selRows), "Are You Sure?", 0):
        for row in selRows:
            rowId = event.source.parent.getComponent('Power Table').data.getValueAt(row, "id")
            system.db.runNamedQuery("Delete Rows", {"rowID": rowId})
        system.vision.refreshBinding(event.source.parent.getComponent('Power Table'), "data")
```

**Editable Power Table writing straight back to the database** (`onCellEdited` extension function — requires **Legacy Database Access** Client Permission, off by default):
```python
id = self.data.getValueAt(rowIndex, 'id')
query = "UPDATE users SET %s = ? WHERE id = ?" % (colName)   # colName supplied by the extension function
system.db.runPrepUpdate(query, [newValue, id])
system.db.refresh(self, "data")
```

**Storing/retrieving binary files** (PDF, images) — pick the DB's binary column type (`LongBlob` on MySQL, `Varbinary` on MSSQL) and write the raw bytes from a File Upload component's `onFileReceived` event:
```python
fileName = event.file.name
fileBytes = event.file.getBytes()
system.db.runPrepUpdate(
    "INSERT INTO files (fileName, fileBytes) VALUES (?, ?)",
    [fileName, fileBytes]
)
```

### SQL troubleshooting workflow

1. **Read the Details tab of the error dialog**, not just the headline — look for the (often repeated) string `caused by`; there are typically two: one Gateway-side, one database-side. The database-side `caused by` message pinpoints the actual SQL problem (e.g., a stray comma right before `FROM` for a syntax error, or a misspelled column/table name for "unknown column"/"unknown table").
2. **Check the Database Connection's health first** — `Connections > Databases > Connections` shows valid/errored state and per-connection throughput before you dig into a specific query.
3. **Reproduce the query in the Database Query Browser** (Designer `Tools` menu) to confirm expected results independent of the binding/component that's failing.
4. **For a slow query**: identify which component/binding is slow (usually visible as a delayed data load on window open) → run the *same* query directly in the database's own management tool, outside Ignition. If it's fast there, the bottleneck is Ignition-side — check the connection's `Max Active`/`Max Wait` pool settings and the Active/Longest-Running Queries panel for pool exhaustion. If it's *also* slow in the native tool, the query itself needs work (missing index, needs to be broken into smaller queries, or the underlying hardware needs more resources) — Ignition cannot make an inherently slow query faster.
5. **Reduce query volume before tuning individual queries**: switch frequently-polled/shared results to a cached Named Query; consolidate multiple same-table lookups (e.g. several Numeric Labels reading one row) into a single dataset fetch plus Expression Language extraction (`{dataset}[row,col]` or `lookup({dataset}, key, fallback)`); collapse per-UDT-instance Query Tags into one provider-level Query Tag fanned out via Expression Tags.

### Safe scripting patterns

- Prefer Named Queries; if raw SQL from a script is unavoidable, always use `runPrepQuery`/`runPrepUpdate` with `?` placeholders — never format/concatenate untrusted strings into SQL text.
- QueryString-type Named Query parameters are for identifiers you control (table/column selection from a fixed allow-list), never for values a user typed freely — they bypass sanitization entirely.
- Wrap multi-statement writes in an explicit transaction (`beginTransaction` → statements with `tx=` → `commitTransaction`/`rollbackTransaction` → `closeTransaction`) so partial failures don't leave inconsistent data.
- For high-fan-out reads (the same query needed by many clients/components), enable **Named Query Caching** instead of letting every SQL Query / DB Browse binding hit the database independently — a poll-driven binding fires once **per open instance of the window**, so 50 open clients means 50 independent polling queries unless you cache.
- For UDTs with **Query Tags**: one Query Tag per UDT *instance* × scan rate = one query per instance per tick. Pull the data with a **single** Query Tag at the provider/folder level instead, and use per-instance **Expression Tags** (with UDT parameters as row/column lookups) to fan the cached dataset out to instances — collapses N queries/tick down to 1.
- Always add a database index on columns used in frequent `WHERE` filtering (Ignition does this automatically for its own Historian/Transaction Group tables) — but remember every index adds write-time overhead, so index selectively.
- Client-scripted `runPrepUpdate` in Vision requires the right Vision **Client Permission** enabled (Legacy Database Access) — a common silent-failure trap when porting scripts between projects with different permission profiles.

---

## Internal database tables

Ignition auto-creates and manages these tables when the corresponding subsystem is configured against a database connection. Table/column names below are **defaults** — most are renameable via the owning subsystem's settings (prefix for auth tables, table names for Journal/Audit).

### Tag History (external SQL historian)

| Table | Purpose |
|---|---|
| `sqlt_data_X_X` | Raw tag values, one table per `{driverId}_{year}_{month}` (or `_{yearMonthDay}` for daily partitions). Columns: `tagid`, `intvalue`/`floatvalue`/`stringvalue`/`datevalue` (only the one matching the tag's `datatype` is populated), `dataintegrity` (192 = Good), `t_stamp` (unix ms), `vtype` (pre-processed-partition metadata). Indexed on `tagid`, `t_stamp`. |
| `sqlth_1_data` | Same schema as above, used only when a provider has partitioning **disabled** (single-partition mode). |
| `sqlth_te` | Tag metadata: `id`, `tagpath`, `scid` (→ `sqlth_scinfo.id`), `datatype` (0=int,1=float,2=string,3=datetime — determines which `sqlt_data_*` column holds the value), `querymode` (0=Discrete deadband, 3=Analog compression), `created`, `retired` (NULL = active; set on rename/delete/scan-class-change/datatype-change). |
| `sqlth_scinfo` | Tag Group (scan class) info: `id`, `scname` ("exempt" = execution rate not recorded), `drvid` (→ `sqlth_drv.id`). |
| `sqlth_sce` | Tag Group execution windows: `scid`, `start_time`, `end_time`, `rate` (ms). |
| `sqlth_partitions` | Partition bookkeeping: `pname`, `drvid`, `start_time`, `end_time`, `blocksize`, `flags` (bit 1 = disables seed queries). |
| `sqlth_drv` | Driver registry: `id`, `name` (Gateway system name), `provider` (Tag Provider name). |
| `sqlth_annotations` | User/Power-Chart annotations: `id`, `tagid`, `start_time`, `end_time`, `type` ("note"), `datavalue`, `annotationid` (UUID, cross-Gateway sync). |

### Tag History (internal / SQLite-backed historian)

Stored in an IDB file under `.../data/var/com.inductiveautomation.historian/internalhistorian` — requires a SQLite viewer, not a project database connection.

| Table | Purpose |
|---|---|
| `annotations` | `id`, `tagid`, `type`, `rangestart`, `rangeend`, `data`, `syncid`, `annotationid`, `deleted`. |
| `schema_info` | `version` (typically `4`), `created`, `flags` (tracks e.g. 8.1→8.3 schema upgrade). Usually one row. |
| `tagdata` | `tagid`, `numvalue`, `strvalue`, `quality`, `t_stamp`, `syncid`. |
| `tagdetails` | `id`, `tagid`, `created`, `retired`, `datatype`, `syncid`, `tagpath`, `metadata`. |
| `tagproperties` | `tagid`, `name`, `value`, `datatype`. |

### Alarm Journal

| Table | Purpose |
|---|---|
| `alarm_events` | One row per alarm state change. `id` (PK), `eventid` (groups active/cleared/ack rows for one occurrence), `source`, `displayPath`, `priority` (0 Diag–4 Critical), `eventtype` (0 Active/1 Cleared/2 Ack/4 Enabled/5 Disabled), `eventflags` (bitmask: bit0 System Event, bit1 Shelved, bit2 System-Ack-on-overflow, bit3 Acked-at-event-time, bit4 Cleared-at-event-time, bit5 Enabled-state-changed), `eventtime`. |
| `alarm_events_data` | Per-event custom properties, one row each (e.g. `AckUser`, `Notes`, `IsShelved`). `id` (→ `alarm_events.id`), `propname`, `dtype` (0 Int/1 Float/2 String), `intvalue`/`floatvalue`/`strvalue`. |

### Authentication (Database User Source, default prefix `scada_`)

| Table | Purpose |
|---|---|
| `scada_users` | `id`, `username`, `password` (encrypted hash), `firstname`, `lastname`, `schedule`, `notes`. |
| `scada_roles` | `id`, `name`. |
| `scada_user_rl` | Many-to-many user↔role: `user_id`, `role_id`. |
| `scada_user_sa` | Per-user schedule adjustments: `id`, `user_id`, `starttime`, `endtime`, `type`. |
| `scada_user_ci` | Per-user contact info (Email/SMS): `id`, `user_id`, `type`, `value`. |
| `scada_user_ex` | Per-user extra properties, one row per name/value pair (e.g. Voice Notification Security PIN): `id`, `user_id`, `name`, `value`. |

### Audit Log

| Table | Purpose |
|---|---|
| `audit_events` | `audit_events_id` (PK; Oracle uses sequence `audit_events_seq` — must be accounted for if the table is manually dropped/renamed on Oracle), `event_timestamp`, `actor`, `actor_host`, `action`, `action_target`, `action_value`, `status_code` (32-bit bitmask, see `AuditStatus.SubCode` javadoc), `originating_system`, `originating_context` (1=Gateway, 2=Designer, 4=Client). Column/table names are **lowercase** — case-sensitive DBs need exact-case queries. |

---

## Gotchas and 8.3 notes

**NEW in 8.3**
- **Perspective is IdP-only.** There is no Classic Authentication path for Perspective at all — a project that needs to keep supporting Classic auth for some clients (Vision) while running Perspective must configure and maintain *both* strategies side by side.
- **Security Levels + Security Level Rules + User Grants + Security Zones** as a combined authorization model, replacing flat role-checks for anything under the IdP strategy.
- **Secrets Management system** (Root Key / Key Encryption Key sets / environment password / pluggable Secret Providers) is new; prior versions only had "embedded" password fields.
- **API Keys** as a first-class Gateway HTTP API credential type, separate from user login.
- **OAuth 2.0 Clients** as a first-class Gateway resource (for OAuth2 SMTP email auth).
- **JDBC driver JAR management moved to a "Manage JAR Files" action starting in 8.3.2** — 8.3.0/8.3.1 still edit the JAR inline on the driver's Edit panel.
- **Create Project Permission setting deprecated in 8.3.7**, superseded by Designer Roles/Permissions.
- **8.1 → 8.3 Identity Provider import support arrived in 8.3.3** — earlier 8.3 releases couldn't import an 8.1 IdP export.
- Active Directory gained an explicit **Legacy Naming Enabled** toggle to control 8.1-vs-8.3 parsing of user/role search-base entries during migration (defaults true when upgrading *from* 8.1, false on upgrades between 8.3 versions).

**CHANGED / migration-relevant**
- **AD SSO is disabled and deprecated (since 8.1.17)** over a security vulnerability; still visible in the UI but requires a special system property to force on — explicitly not recommended.
- Role-based (Classic) and Security-Level-based (IdP) permission trees are **separate, non-syncing entity sets** — a role created under Users/Roles does not appear under Security Levels and vice versa; each must be maintained independently even when conceptually "the same" role.
- Renaming a **role** or a **Security Zone** referenced by project security silently breaks that check, because the project stores the name as a plain string, not an ID — the docs flag both with explicit warnings.

**Security anti-patterns called out directly in the docs, or clearly implied**
- **String-built SQL from user input** — the docs' own "never do this" example is `UPDATE table SET column = 'This was a horrible mistake'` (no WHERE) and repeated warnings to prefer prepared statements/Named Queries; QueryString-type Named Query parameters are explicitly flagged as injection-prone and should not carry free-typed user input.
- **Leaving `Allow Anonymous` enabled on an AD User Source** — can let any username (even nonexistent) bind with a blank password under `NONE`/`SIMPLE` Security Authentication.
- **Over-broad API Keys** — a key with no scoping grants full Gateway HTTP API access (config, tags, projects); the docs recommend issuing keys only to trusted systems and applying the narrowest workable Security Level.
- **Leaving Service Security's Default Profile/Provider Access Level at "Inherited"** — new History Providers, Audit Profiles, and Secret Providers are auto-added to a zone's policy with `Inherited` access, so an over-permissive Default silently grants access to every newly created resource of that kind.
- **Plaintext secrets in Extra Connection Properties or hardcoded in scripts** instead of using Embedded/Referenced secrets or a Secret Provider — the whole point of the 8.3 Secrets Management system is to eliminate this pattern.
- **Running with the factory default (shared) encryption key in production** — every fresh Ignition install starts on the same default key; the docs recommend opting into a customized Root Key/Key Set for anything beyond testing.
