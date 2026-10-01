# Security Model & Roles

The Ignition security mechanism and how to design a least-privilege role set on it.
Universal layer. The roles / security levels / zones / IdP **this deployment defines**
are in the project gateway profile. The standard this maps to is
**`skill/references/standards/iec-62443.md`** (zones & conduits, SL-T, foundational
requirements).

Mechanism claims verified live and from decompiled bytecode
(`ReservedSecurityLevel`, `SecurityZoneManager`, `IdentityProviderManager`); baseline in
`references/VERIFIED.md`.

## The pieces

| Piece | What it is | Verified |
|---|---|---|
| **Identity Provider (IdP)** | Authenticates a login and returns a user identity + attributes. Ignition IdP, or federated (OIDC/SAML). | `IdentityProviderManager` present, one running IdP |
| **User Source** | A directory of users/roles (Internal, Database, AD, AD/Internal hybrid). Backs the Ignition IdP. | `UserSourceManagerImpl` present |
| **Role** | A named group membership carried by the user (`Administrator`, `Operator`, …). Flat string. | — |
| **Security Level** | A node in a **tree** that a user either has or doesn't, derived by **rules** from identity + zone. Roles are one built-in branch. | `ReservedSecurityLevel`: `Authenticated`, `Authenticated/Roles`, `SecurityZones` |
| **Security Level Path** | The address of a level: `Authenticated`, `Authenticated/Roles/Operator`, `SecurityZones/PlantFloor`. | verified path arrays in `ReservedSecurityLevel` |
| **Security Zone** | A classification of *where a connection comes from* on the gateway network, matched by traits (IP/host/gateway name). | `SecurityZoneManager`, trait-based |

### Roles vs Security Levels — the distinction

- A **role** is an attribute of the *user* ("this person is an Operator").
- A **security level** is a *computed grant* ("this session satisfies
  `Authenticated/Roles/Operator` **and** `SecurityZones/PlantFloor`").
- Resources are protected by **security levels**, not roles directly — so you can
  require *role AND zone* (`Operator` from the plant-floor subnet), which a bare role
  check cannot express.
- `Authenticated/Roles/<role>` is auto-populated from the user's roles; you add
  custom levels with rules for anything finer.

## Security zones (gateway network)

- Defined on the gateway, matched by connection **traits**: IP-address pattern,
  hostname, originating gateway name.
- A remote gateway / designer / client connection lands in zero or more zones.
- Combined with roles in security-level rules to enforce *"config changes only from
  the engineering VLAN"* — an IEC 62443 zones-and-conduits control
  (`skill/references/standards/iec-62443.md`).

## Resource protection

| Resource | Mechanism |
|---|---|
| **Perspective page** | Page-level security in the page config — required security levels to view/mount |
| **Perspective view / component** | `meta.security` / component-event scripts gated on `system.perspective.isAuthorized(securityLevels)` |
| **Project** | Project properties: required roles/levels to open; **inheritance** — a child project inherits the parent's security unless overridden |
| **Tag** | `readPermissions` / `writePermissions` / `editPermissions` on the tag or provider (`type: "AllOf"/"AnyOf"`, `securityLevels: [...]`) — verified keys in the `default` provider config |
| **Gateway config pages** | Gateway-scoped roles (the classic `Administrator` etc.) |
| **Named query / DB** | Query-level access + the DB connection's own auth |

Design: protect at the **highest** level that works (page > view > component), and
keep the check declarative (security levels) rather than scripted where possible.

## API keys & scopes (verified)

- The `ignition-mcp` server authenticates with header
  **`X-Ignition-API-Token: <keyName>:<secret>`** (the full `keyName:secret` value).
- The key must be granted **admin scope** in Gateway → Security → API Keys, or
  **every** REST endpoint returns **403** (`memory/ignition-mcp-setup.md`).
- Native REST (`/data/api/v1/...`) and the WebDev-backed tools both rely on this key.
- Treat the key like a root credential: it is in `~/ignition-mcp/.env` and the
  `~/.claude.json` env block, never commit it, never log it.

**agent rule:** if a call fails for lack of scope/permission, **report it** to
your supervisor — do **not** broaden the key's scope or a role's grants to unblock yourself.

## Mapping IEC 62443 foundational requirements onto these mechanisms

| 62443 FR / SR (see `iec-62443.md`) | Ignition mechanism |
|---|---|
| FR1 Identification & Authentication Control | IdP + User Source; federated OIDC/SAML for SSO/MFA |
| FR2 Use Control (authorised actions only) | Security levels on pages/views/tags; least-privilege roles |
| FR2 + zones | Security zones × role in security-level rules (config from engineering zone only) |
| FR3 System Integrity | Signed modules (`allowUnsignedModules=false` — verified), project inheritance, resource protection |
| FR4 Data Confidentiality | TLS on the gateway, DB connection encryption, secret store (`system.secrets`) for credentials |
| FR5 Restricted Data Flow (conduits) | Gateway network zones + one-way / filtered connections |
| FR6 Timely Response to Events | Audit log, gateway logs, alarm journal |
| FR7 Resource Availability | Redundancy role (verified `Independent`), gateway backups |

## Designing a least-privilege role set

1. Start from **operator tasks**, not org chart: `View`, `Operate`, `Acknowledge`,
   `Configure`, `Administer`.
2. One role per capability band; compose, don't create `Operator_LineA_Night`.
3. Default deny — a new page/view requires an explicit level.
4. Separate **view** from **operate** from **configure**; separate **runtime** from
   **gateway admin**.
5. Bind sensitive actions to *role AND zone*.
6. Service accounts (like the MCP key) get exactly the scope they need — here that is
   unavoidably admin, so it is guarded as a secret, not shared.
7. Record the final set in the project gateway profile with the level paths.

## agent rules

1. Protect resources with **security levels**, not raw role strings; require role AND
   zone for config-class actions.
2. Never hardcode a username/password/API key in a script, resource, or binding —
   use `system.secrets` / the gateway's credential store.
3. Never broaden an API-key scope or add a role grant to get past a `403`/permission
   error — stop and report to your supervisor.
4. Protect at the highest resource level that works (page before component).
5. Prefer declarative security-level checks over scripted `if role == ...`.
6. New Perspective pages/views are **deny by default** until a level is assigned.
7. Take the concrete role/level/zone names from the project gateway profile;
   don't invent them.
8. Keep `allowUnsignedModules=false`.

## Reading the live security config (native REST, found 2026-09-22)

The gateway's `GET /openapi.json` documents native REST list/find/CRUD
endpoints for security zones and user sources — useful when a task needs to
know what's actually configured before wiring a `security.props`/role check
into a view, instead of guessing role names:

| Endpoint | Purpose |
|---|---|
| `GET /data/api/v1/resources/list/ignition/security-zone` | List configured security zones |
| `GET /data/api/v1/resources/find/ignition/security-zone/{name}` | Read one zone's config |
| `GET /data/api/v1/resources/list/ignition/user-source` | List configured user sources (identity providers) |
| `GET /data/api/v1/resources/find/ignition/user-source/{name}` | Read one user source's config |
| `GET /data/api/v1/resources/singleton/ignition/security-levels` | The project's security-level tree (used by resource-protection rules) |

Auth: `X-Ignition-API-Token` header, same as every native call
(`mcp-tool-map.md`). Schema-confirmed against the live gateway's OpenAPI spec;
not yet exercised end-to-end. Read-only use case — check these before authoring
a security-scoped screen rather than assuming role/zone names from a
the project conventions doc that may be stale.

## Smells

- A view that checks `if 'Administrator' in session.props.auth.user.roles` inline
  instead of a page-level security-level requirement.
- Credentials in a binding, a named query, or a script constant.
- One mega-role that every user gets.
- Roles encoding site + shift + line (`Op_L1_Night`) instead of composing role + zone.
- Widening the MCP key or a role to clear a permission error.
- Config endpoints reachable from the plant-floor / client subnet.
- Child project silently inheriting (or overriding) parent security without anyone
  deciding it.
- `system.secrets` unused; secrets pasted into `.env` files that get committed.
