---
title: Security Model
description: Authentication, authorization, roles
---

> **Skill level:** 100 · **Read first:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 50-SECURITY-MODEL

# Security

User management and permission control.

## Authentication

**Local Users:**
- Created in gateway
- Passwords hashed, stored locally
- Default: admin/password

**LDAP/AD:**
- Sync with company directory
- Single sign-on via Active Directory

**OAuth:**
- Third-party provider (Google, GitHub, etc.)
- Configure in Admin Console

## Roles

**Role** = Named set of permissions.

**Assign permissions to role:**
- Can read/write specific tags
- Can access specific views
- Can execute specific actions

**Assign user to role:**
- User inherits all role permissions

**Built-in roles:**
- Administrator (full access)
- User (limited access, configurable)

## Tag Permissions

Tag can have read/write permissions by role:

```
Tag: [default]PayrollData
- Administrators: Read + Write
- HR: Read + Write
- Users: No access
```

Set in Designer → Tag Bindings → Permissions

## View Permissions

Lock views to roles:

```
View: /admin/GatewayConfig
- Visible to: Administrators only
- Edit mode: Administrators only
```

Users without permission see "Access Denied"

## Component Security

Hide/disable components based on role:

```javascript
// In component binding:
{expr: "if({user.roles} contains 'admin', true, false)"}

// Or in script:
if "admin" in system.user.getRoles(system.user.getUser()):
    self.props.visible = true
```

## Current User

**Get logged-in user:**
```python
user = system.user.getUser()
username = user.name
fullname = user.fullName
roles = user.roles
```

## Session Security

**Timeout:**
- Configurable idle timeout (default 30 min)
- User logged out automatically

**HTTPS:**
- Recommended for production
- Encrypt traffic between client and gateway

**CORS:**
- Restrict cross-origin requests
- Configure in gateway security settings

## Password Policy

Set in Admin Console:
- Minimum length
- Complexity requirements (uppercase, number, special char)
- Password expiration (days)
- Failed login lockout

---
**Best Practice:** Always use HTTPS in production + enable SSL certificate.

---

## See Also

**Prerequisites:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

**Builds toward:** [51-PLATFORM-SECURITY-COMPLETE](51-PLATFORM-SECURITY-COMPLETE.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)

**Related:** [51-PLATFORM-SECURITY-COMPLETE](51-PLATFORM-SECURITY-COMPLETE.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
