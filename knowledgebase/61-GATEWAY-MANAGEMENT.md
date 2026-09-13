---
title: Gateway Management
description: Configuration, diagnostics, maintenance
---

> **Skill level:** 200 · **Read first:** [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 61-GATEWAY-MANAGEMENT

# Gateway Management

Central hub at localhost:8088.

## Access

**Admin Console:**
```
http://localhost:8088/web/admin
```
- Login with gateway admin credentials
- Configure modules, databases, devices, users

**Status Page:**
```
http://localhost:8088/web/home
```
- View system health
- Active modules, sessions, tag count

## Key Configuration Areas

**Modules:**
- Enable/disable modules (OPC-UA, SQL, Reporting, etc.)
- Module-specific settings

**Database Connections:**
- Add datasources (MySQL, MSSQL, PostgreSQL, Oracle)
- Test connection, verify credentials

**Security:**
- User authentication (local, LDAP, OAuth)
- Roles and permissions
- SSL/TLS certificates

**Devices (OPC-UA):**
- Add OPC servers
- Configure browse settings
- Test connectivity

**Alarms:**
- Escalation settings
- Notification email/webhook

**Gateway Network:**
- Master-Backup failover (HA setup)
- Security policies (IP whitelist, etc.)

## Restart Gateway

**Via Admin Console:**
```
Config → System → Restart Ignition
```

**Via command line:**
```bash
# Windows
net stop "Ignition"
net start "Ignition"

# Linux
sudo systemctl stop ignition
sudo systemctl start ignition
```

**Warning:** Stops all clients, clears memory tags.

## Backup/Restore

**Manual backup:**
```
Backup gateway state: Data folder → .zip
Location: C:\Program Files\Inductive Automation\Ignition\data\
```

**Automated:**
- Schedule regular backups (config stored in gateway.xml)
- Export to cloud/remote storage

## Memory/Performance

**View memory usage:**
```
Admin Console → Status → Memory
```

**If approaching limit:**
- Restart gateway (clears memory)
- Review queries/scripts (may be leaking memory)
- Increase heap size (advanced)

**Heap config:**
Edit: `ignition.conf` → `wrapper.java.maxmemory=3072M` (3GB)

## Database Verification

**Check connection:**
```
Admin Console → Datasources → Test Connection
```

**Verify historical data:**
- Use Named Query to test SELECT
- Check query performance

## Certificate/SSL

**For HTTPS:**
```
Config → Security → Certificates → Import/Create
```

**Self-signed (dev only):**
Generated automatically on first startup.

**Production:**
Use trusted CA certificate.

## Restart Without Losing Data

**Graceful restart:**
1. Block new connections (Config → Security)
2. Wait for existing sessions to timeout
3. Restart

**Or manually:**
1. Stop Ignition service
2. Data persists in files
3. Restart service (loads data)

---
**Maintenance Checklist:**
- [ ] Verify DB connection weekly
- [ ] Review logs for ERROR lines
- [ ] Check memory usage (< 80% of max)
- [ ] Test backup restore monthly
- [ ] Update modules quarterly

---

## See Also

**Prerequisites:** [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

**Builds toward:** [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md), [51-PLATFORM-SECURITY-COMPLETE](51-PLATFORM-SECURITY-COMPLETE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
