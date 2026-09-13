---
title: Installation & Setup
description: System requirements, installation steps, commissioning
---

> **Skill level:** 100 · **Read first:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 60-INSTALLATION-SETUP

# Installation & Setup

## System Requirements

**Windows:**
- Windows Server 2016+ or Windows 10+
- 4GB RAM minimum, 8GB+ recommended
- 20GB disk space

**Linux:**
- Ubuntu 18.04+, CentOS 7+, etc.
- Java 11+ pre-installed
- 4GB RAM minimum

**macOS:**
- macOS 10.13+ (Intel)
- Java 11+

## Installation Steps

**Windows:**
1. Download from inductiveautomation.com
2. Run installer: `Ignition-8.3.x-windows-x86_64.exe`
3. Choose install path (default: `C:\Program Files\Inductive Automation\Ignition\`)
4. Select components to install (default: all)
5. Complete installation
6. Gateway starts automatically at `localhost:8088`

**Linux:**
```bash
# Download
wget https://...Ignition-8.3.x-linux-x86_64.tar.gz

# Extract
tar -xzf Ignition-8.3.x-linux-x86_64.tar.gz

# Install (run as root)
cd ignition
sudo ./install.sh

# Start service
sudo systemctl start ignition
```

**macOS:**
1. Download `.dmg` file
2. Open DMG file
3. Drag Ignition to Applications
4. Run from Applications

## First-Time Setup

**Gateway Console:**
```
http://localhost:8088/
```

**Welcome page:**
- Configure license (online or offline activation)
- Create admin account
- Select edition (Standard, Professional, Edge)
- Enable modules needed

**Module Selection:**
- Check boxes for: Perspective, OPC-UA, SQL, Reporting, etc.
- Download enabled modules (1-2 min)

## License Activation

**Online (recommended):**
- Gateway connects to license server automatically
- No action needed

**Offline:**
- Get activation code from gateway
- Visit: inductiveautomation.com/license
- Upload activation code
- Download license file
- Upload license file to gateway

## Create First Project

**Designer:**
```
Gateway → Projects → New Project
Name: MyProject
Description: Initial project
Template: Choose or start blank
```

**First View:**
- Designer opens project
- Right-click → Create View
- Add components (Label, Button, etc.)
- Save project

## Configure Database (Optional)

**Admin Console:**
```
Config → Databases → New Datasource
Name: production_db
Type: MySQL/MSSQL/PostgreSQL
Host: db.company.local
Port: 3306
Database: production
Username/Password: credentials
Test Connection → OK
```

## Configure OPC Device (Optional)

**Admin Console:**
```
Config → Devices → New Device
Type: OPC-UA Server (or driver-specific)
Name: PLC01
Server URL: opc.tcp://192.168.1.100:4840
[Test Connection]
Browse → See available tags
```

## Backup Configuration

**Initial backup (recommended):**
```
C:\Program Files\Inductive Automation\Ignition\data\
→ ZIP entire folder
→ Store externally
```

**Restore if needed:**
1. Stop Ignition service
2. Replace data folder with backup
3. Start Ignition service

## Verify Installation

**Check status:**
```
Admin Console → Gateway Status
- Check all modules loaded
- Check database connection OK
- Check license valid
```

**Test first project:**
```
http://localhost:8088/data/perspectives/MyProject/
```

## Upgrade from 8.1 to 8.3

1. **Backup** current installation
2. **Download** 8.3 installer
3. **Stop** Ignition service
4. **Run** installer (detects existing version)
5. **Migrate** database schema automatically
6. **Restart** Ignition
7. **Verify** projects load correctly

**Data persists** across upgrade (projects, tags, configuration).

## Default Credentials

| Component | Default |
|-----------|---------|
| Admin Console | admin / password |
| Gateway | admin / password |

**CHANGE immediately in production.**

## Troubleshooting Installation

**Gateway won't start:**
- Check Java installed: `java -version`
- Check port 8088 available: `netstat -an | grep 8088`
- Check logs: `logs/wrapper.log`

**License activation fails:**
- Check internet connection (if online license)
- Verify activation code correct
- Contact support if persistent

**Can't access gateway:**
- Verify URL: `http://localhost:8088`
- Check service running: `sudo systemctl status ignition`
- Firewall blocking? Open port 8088

---
**Post-Install Checklist:**
- [ ] Change default admin password
- [ ] Configure SSL certificate (if production)
- [ ] Set up database connection
- [ ] Create first project
- [ ] Configure OPC devices
- [ ] Test tag reading
- [ ] Schedule backups

---

## See Also

**Prerequisites:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md)

**Builds toward:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md)

**Related:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md), [02-SYSTEM-ARCHITECTURES](02-SYSTEM-ARCHITECTURES.md), [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
