---
title: Ignition Modules Master Index
description: Complete reference of all Ignition modules, capabilities, dependencies, and licensing
version: 8.3+
---

> **Skill level:** 200 · **Read first:** [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 70b-MODULES-INDEX-MASTER

# Ignition Modules: Complete Master Index

Comprehensive reference for all Ignition modules across the platform. Each module adds specific capabilities to your Ignition gateway.

**Last Updated:** 2026-07-13  
**Ignition Version:** 8.3+  
**Status:** Master Reference

---

## Quick Module Summary Table

| Module | Category | Purpose | License | Since |
|--------|----------|---------|---------|-------|
| **Perspective** | UI/UX | Modern web-based HMI & dashboards | Standard | 8.0 |
| **Vision** | UI/UX | Legacy desktop SCADA client | Standard | All |
| **OPC-UA** | Connectivity | Industrial device communication | Standard | All |
| **SQL Bridge** | Data | Database connectivity & queries | Standard | All |
| **Tag Historian** | Data | Time-series historical logging | Standard | All |
| **Reporting** | Reports | PDF/Excel/HTML report generation | Standard | 7.9+ |
| **MQTT Transmission** | Connectivity | MQTT pub/sub messaging | Optional | 7.9+ |
| **MES (Sepasoft)** | Manufacturing | Production tracking & OEE | Professional | 7.9+ |
| **Mobile Module** | UI/UX | Native iOS/Android applications | Professional | 7.8+ |
| **Compute (Edge)** | Gateway | Lightweight gateway for edge | Professional | 8.0+ |
| **Sequential Function Charts** | Logic | SFC workflow automation | Professional | 7.9+ |
| **Perspective Workstation** | UI/UX | Kiosk/workstation application | Professional | 8.1+ |
| **Cirrus Link MQTT** | Connectivity | MQTT Edge Intelligence (Sparkplug) | Premium | 7.8+ |
| **MEE (Mobile Edge Engine)** | Gateway | Mobile field service edge gateway | Premium | 8.1+ |
| **Transaction Groups** | Data | Scheduled data collection & logging | Standard | All |

---

## Core Modules (Included Standard)

### 1. Perspective Module

**Overview**
- Modern, responsive web-based user interface (UX/UI framework)
- Default choice for new projects (8.0+)
- Replaced Vision as primary UI platform

**Key Features**
- Responsive web design (desktop, tablet, mobile)
- Real-time data binding
- Built-in component library (70+ components)
- Template system for reusability
- Embedded reporting
- Mobile browser support
- Theme customization (light/dark)
- Session management & user authentication

**Capabilities**
- HMI dashboards & SCADA screens
- Real-time charts & trending
- Alarms & notifications
- Data input forms
- Mobile-responsive layouts
- SVG graphics
- Embedded videos & media
- Dropdown menus & navigation
- Tables with sorting/filtering

**When to Use**
- ✅ New projects
- ✅ Web-based access required
- ✅ Mobile dashboard access
- ✅ Multi-site remote viewing
- ✅ Cloud deployments
- ❌ Legacy desktop-only solutions
- ❌ Highly specialized custom visualizations

**Performance Characteristics**
- Memory: ~50-150 MB per active session (varies by complexity)
- Browser support: Chrome, Firefox, Safari, Edge
- Latency: <100ms for typical bindings
- Max sessions: Limited by gateway RAM (typically 50-200 concurrent)

**Dependencies**
- None (core module)

**Licensing**
- **Included:** Standard edition and above
- **Cost:** Part of Standard subscription
- **Limit:** Unlimited projects, users
- **Sessions:** Based on gateway license tier

**Deployment Modes**
| Mode | Usage | Notes |
|------|-------|-------|
| Browser | Web application | No client install needed |
| Mobile Browser | iOS/Android | Responsive design |
| Workstation App | Kiosk/dedicated | Native app wrapper |
| Embedded | In other UI frameworks | Via iframe or API |

**Common Integrations**
- Reporting Module (embedded reports)
- Tag Historian (trend visualization)
- Mobile Module (native sync)
- SQL Bridge (data queries)
- MQTT (live data feeds)

**Documentation Links**
- Perspective User Manual: docs.inductiveautomation.com/docs/8.3/perspective/
- Component Reference: docs.inductiveautomation.com/docs/8.3/perspective/reference/
- Bindings Guide: docs.inductiveautomation.com/docs/8.3/perspective/data-binding/

---

### 2. Vision Module

**Overview**
- Legacy desktop SCADA client (pre-Perspective)
- Still supported but not recommended for new projects
- Native Windows/Linux desktop application

**Key Features**
- Traditional SCADA visualization
- ActiveX component support
- Drawing tools & graphics
- Script execution on client side
- Legacy compatibility
- Offline mode support
- Plugin extensibility

**Capabilities**
- Static and dynamic graphics
- Real-time data visualization
- Animated objects
- Alarms display
- Data entry forms
- Report viewing
- Popup windows
- Keyboard shortcuts

**When to Use**
- ✅ Legacy system maintenance
- ✅ Existing Vision projects (migration path)
- ✅ Desktop-only deployments
- ✅ Needs ActiveX controls
- ❌ New projects
- ❌ Mobile access required
- ❌ Browser-based access
- ❌ Cloud deployments

**Performance Characteristics**
- Memory: ~100-200 MB per client
- Network: TCP/IP, LAN preferred
- Latency: 50-200ms typical
- Max concurrent: Limited by system resources

**Dependencies**
- None (core module)
- Requires Windows/Linux client installation

**Licensing**
- **Included:** All editions
- **Cost:** Part of license
- **Deprecation:** No longer actively developed
- **Support:** Maintenance only

**Deployment Modes**
| Mode | Usage | Notes |
|------|-------|-------|
| Installed Client | Desktop app | Windows/Linux install |
| Citrix/RDP | Remote desktop | Via terminal server |
| Web Launch | Browser launched | JNLP file download |

**Migration Path**
- Vision → Perspective (recommended)
- Conversion tools available
- Gradual migration possible (run both)

**Documentation Links**
- Vision User Manual: docs.inductiveautomation.com/docs/8.3/vision/ (legacy)
- Migration Guide: Contact Inductive Automation

---

### 3. OPC-UA Module

**Overview**
- Industrial device communication protocol (OPC-UA = OLE for Process Control, Unified Architecture)
- Standard for factory floor connectivity
- Secure, time-series enabled, firewall-friendly

**Key Features**
- OPC-UA client & server
- Modbus TCP/RTU support
- EtherCAT support
- PROFINET support
- BACnet/IP support
- Allen-Bradley CompactLogix/ControlLogix
- Siemens S7 (native TCP)
- Temperature probe drivers
- HTTP/HTTPS device access

**Capabilities**
- Connect 100+ PLC brands
- Real-time tag subscription
- Alarm/event streaming
- Historical data collection
- Method execution (RPC)
- Certificate-based security
- Redundancy & failover
- Multi-protocol bridging

**When to Use**
- ✅ Any industrial device connection
- ✅ PLC communication
- ✅ Sensor data collection
- ✅ Remote site connectivity
- ✅ Secure device communication
- ✅ Enterprise firewall deployments
- ❌ Local file system only
- ❌ No devices to connect

**Performance Characteristics**
- Max devices: 100+ (limited by gateway RAM)
- Tag polling: <100ms typical
- Concurrent connections: 50-200
- Bandwidth: 50-500 Kbps per device (varies by scan rate)
- Latency: 5-50ms per tag

**Dependencies**
- None (core module)
- Device-specific drivers available separately

**Licensing**
- **Included:** Standard edition and above
- **Cost:** Part of license
- **Drivers:** Most standard (Modbus, S7, EtherCAT included)
- **Specialized:** Some drivers require additional cost

**Supported Device Types**

| Manufacturer | Protocol | Support | Notes |
|--------------|----------|---------|-------|
| Allen-Bradley | CompactLogix | Native | Ethernet I/P |
| Allen-Bradley | ControlLogix | Native | Ethernet I/P |
| Siemens | S7-1200/1500 | Native | TCP-based |
| Siemens | S7-300/400 | Native | TCP-based |
| Beckhoff | TwinCAT | EtherCAT | Industrial EtherCAT |
| Beckhoff | PLC | Native | AMS over TCP |
| Modbus | Any device | TCP/RTU | Universal protocol |
| BACnet | HVAC/Building | BACnet/IP | Facility automation |
| Generic | HTTP/HTTPS | Web services | REST device integration |
| Temperature | Multiple brands | Modbus | Sensors, probes |

**Common Integrations**
- SQL Bridge (store readings)
- Tag Historian (trend data)
- Perspective (real-time display)
- Reporting (device metrics)
- MQTT (edge distribution)

**Documentation Links**
- OPC-UA Module Guide: docs.inductiveautomation.com/docs/8.3/opcua/
- Device Driver List: docs.inductiveautomation.com/docs/8.3/opcua/device-drivers/

---

### 4. SQL Bridge Module

**Overview**
- Database connectivity & query engine
- Execute SQL on-demand or scheduled
- Execute stored procedures
- Transaction support
- Connection pooling & optimization

**Key Features**
- Support for major databases (MySQL, MSSQL, PostgreSQL, Oracle)
- Connection pooling
- Parameterized queries (SQL injection prevention)
- Transaction groups (see separate module)
- Named queries (reusable parameterized SQL)
- Query profiling
- Connection troubleshooting tools
- Scripting access (system.db namespace)

**Capabilities**
- Real-time data retrieval
- Insert/update/delete operations
- Stored procedure execution
- Multi-database support
- Batch operations
- Connection switching
- Query result binding
- Dynamic SQL construction
- Database diagnostics

**When to Use**
- ✅ Any database integration
- ✅ Historical data storage
- ✅ Compliance/audit logging
- ✅ Report data queries
- ✅ Multi-system data consolidation
- ❌ File-based only systems
- ❌ No persistent storage needed

**Performance Characteristics**
- Max connections: 20-100 (configurable per database)
- Query latency: 5-500ms (varies by query complexity)
- Throughput: 100-1000 queries/second (depends on DB)
- Connection pool: Reduces latency 10-50x
- Timeout: Configurable per query

**Dependencies**
- None (core module)
- Requires database server (external)

**Licensing**
- **Included:** Standard edition and above
- **Cost:** Part of license
- **Database:** Bring your own (MySQL free, MSSQL/Oracle licensed)

**Supported Databases**

| Database | Versions | License | Status | Notes |
|----------|----------|---------|--------|-------|
| MySQL | 5.7+ | Free/GPL | Stable | Recommended for small-medium |
| MariaDB | 10.3+ | Free/GPL | Stable | MySQL drop-in replacement |
| PostgreSQL | 9.6+ | Free | Stable | Excellent choice |
| MSSQL | 2012+ | Licensed | Stable | Enterprise SQL Server |
| Oracle | 11g+ | Licensed | Stable | Enterprise database |
| H2 Database | 1.4+ | Free | Embedded | Built-in test DB |
| SQLite | 3.0+ | Free | Basic | File-based, limited concurrency |

**Named Queries Pattern**
```
SELECT * FROM machines WHERE plant_id = ?
(Parameterized for reuse in scripts/UI)
```

**Common Integrations**
- Tag Historian (store tag history)
- Reporting (data source)
- Perspective (populate tables/forms)
- Transaction Groups (batch logging)
- OPC-UA (device data storage)

**Documentation Links**
- SQL Bridge Guide: docs.inductiveautomation.com/docs/8.3/sql/
- Database Setup: docs.inductiveautomation.com/docs/8.3/sql/database-setup/
- Named Queries: docs.inductiveautomation.com/docs/8.3/sql/named-queries/

---

### 5. Tag Historian Module

**Overview**
- Time-series historical data logging
- Automatic tag value recording
- Optimized for trending & analysis
- Compliance & audit trail
- Data retention policies

**Key Features**
- Automatic tag value logging
- Configurable storage (database or built-in)
- Trend data aggregation
- Data retention policies
- Alarm event logging
- Manual data archival
- Storage partitioning
- Data compression options

**Capabilities**
- Continuous data recording
- Historical data retrieval
- Trend charting (with Perspective)
- Spike/anomaly detection
- SPC (Statistical Process Control)
- Compliance reporting
- Audit trails
- Data export

**When to Use**
- ✅ Production tracking
- ✅ Compliance/audit requirements
- ✅ Trend analysis
- ✅ Equipment diagnostics
- ✅ Energy monitoring
- ✅ Quality metrics
- ❌ Real-time only (no history needed)
- ❌ Lightweight edge deployments

**Performance Characteristics**
- Storage: ~1 KB per tag per day (varies by data type)
- Max tags: 1000+ (limited by gateway)
- Sample rates: 1 Hz to once per day
- Query latency: 10-100ms for historical ranges
- Disk I/O: 10-100 writes/second typical

**Dependencies**
- SQL Bridge (required, uses database)
- Database connection configured

**Licensing**
- **Included:** Standard edition and above
- **Cost:** Part of license
- **Retention:** Typically 1-5 years (configurable)

**Storage Options**

| Option | Storage | Performance | Cost | Best For |
|--------|---------|-------------|------|----------|
| Database (default) | RDBMS | Good | Low (DB cost) | Standard deployments |
| Built-in H2 | Embedded DB | Fast | None | Small deployments |
| Archive | File system | Slower | Low | Long-term retention |
| Cloud (via API) | External | Network dependent | High | Hybrid/cloud |

**Data Retention Policies**

```
Example:
- Keep 1-minute data for 30 days
- Keep 1-hour aggregates for 1 year
- Keep daily aggregates forever
(Automatic compression)
```

**Common Integrations**
- SQL Bridge (underlying database)
- Perspective (trend charts)
- Reporting (historical reports)
- Alarms (event logging)
- OPC-UA (device data source)

**Documentation Links**
- Historian Setup: docs.inductiveautomation.com/docs/8.3/historian/
- Data Retention: docs.inductiveautomation.com/docs/8.3/historian/retention/

---

## Optional Modules (Licensed Add-ons)

### 6. Reporting Module

**Overview**
- Professional report generation
- PDF, Excel, HTML export
- Scheduled report distribution
- Embedded in Perspective
- Full data source integration

**Key Features**
- Visual report designer
- Charts, tables, graphs
- Parameterized reports
- Email distribution
- Schedule-based generation
- Multi-page layouts
- Logo/branding
- Drilldown capability
- Barcode support

**Capabilities**
- PDF generation
- Excel export with formatting
- HTML output
- Report scheduling
- Email automation
- Report archival
- Compliance documentation
- Custom layouts

**When to Use**
- ✅ Production reports
- ✅ Compliance documentation
- ✅ Daily/weekly summaries
- ✅ Email distribution
- ✅ Regulatory reporting
- ✅ OEE/KPI dashboards
- ❌ Real-time only displays
- ❌ Simple tabular views (use Perspective Table)

**Performance Characteristics**
- Generation time: 1-30 seconds (varies by size)
- Max file size: 100MB+ (varies by system)
- Concurrent reports: 5-10 recommended
- Email delivery: Asynchronous

**Dependencies**
- SQL Bridge (for data)
- Optional: Perspective (for embedding)

**Licensing**
- **Included:** Most Standard+ licenses
- **Cost:** Check license agreement
- **Distribution:** Email/web delivery

**Report Types**

| Type | Use Case | Output |
|------|----------|--------|
| Operational | Daily production summary | PDF/Excel |
| Regulatory | Compliance/audit trail | PDF signed |
| KPI Dashboard | Performance metrics | HTML interactive |
| OEE Report | Overall Equipment Effectiveness | PDF/Excel |
| Bill of Materials | Manufacturing | PDF |
| Batch History | Genealogy/traceability | PDF |

**Common Integrations**
- SQL Bridge (query data)
- Tag Historian (trending data)
- Perspective (embedded reports)
- MES (production data)
- Email (via system.net.sendEmail)

**Documentation Links**
- Reporting Module Guide: docs.inductiveautomation.com/docs/8.3/reporting/

---

### 7. MQTT Transmission Module

**Overview**
- MQTT broker & client connectivity
- Publish/subscribe messaging
- IoT/edge device integration
- Lightweight protocol (good for constrained devices)
- Sparkplug protocol support (via Cirrus Link)

**Key Features**
- Built-in MQTT broker
- MQTT client connections
- Topic-based pub/sub
- Persistent sessions
- QoS levels (0, 1, 2)
- Retained message support
- Last-will & testament
- Authentication & TLS/SSL
- Ignition tag ↔ MQTT bridge

**Capabilities**
- Send data to cloud platforms (AWS, Azure, Google Cloud)
- Receive commands from remote systems
- Lightweight IoT device connectivity
- Message persistence
- Topic wildcards
- Multi-site message relay
- Device telemetry
- Distributed event handling

**When to Use**
- ✅ IoT device networks
- ✅ Edge processing
- ✅ Cloud integration (AWS/Azure/GCP)
- ✅ Multi-site data distribution
- ✅ Lightweight device communication
- ✅ SCADA telemetry to cloud
- ❌ High-frequency real-time (<100ms)
- ❌ Binary protocol requirements

**Performance Characteristics**
- Throughput: 1000+ messages/second
- Latency: 50-500ms typical (network dependent)
- Max topics: 10,000+
- Max subscribers: 100+
- Message size: Up to 256MB
- Bandwidth: 10-100 Kbps typical

**Dependencies**
- None (standalone)

**Licensing**
- **Included:** Many Standard+ licenses
- **Cost:** Check agreement
- **Cloud:** Additional cloud gateway cost for AWS/Azure

**MQTT Topics Pattern**

```
plant/line1/machine1/temperature
plant/line1/machine1/pressure
plant/line2/*/status
alerts/production/downtime
commands/restart/line1
```

**QoS Levels**

| QoS | Guarantee | Latency | Use Case |
|-----|-----------|---------|----------|
| 0 | Fire & forget | Low | Status updates, telemetry |
| 1 | At least once | Medium | Important messages |
| 2 | Exactly once | High | Financial, critical |

**Common Integrations**
- AWS IoT Core (cloud data)
- Azure IoT Hub (cloud data)
- Google Cloud Pub/Sub (cloud data)
- Perspective (MQTT source tag binding)
- OPC-UA (relay device data)
- Edge/Compute Module (edge processing)

**Documentation Links**
- MQTT Transmission Guide: docs.inductiveautomation.com/docs/8.3/mqtt/

---

### 8. Mobile Module

**Overview**
- Native iOS & Android applications
- Mobile-specific UI (not browser)
- Offline capability
- Camera/GPS integration
- Push notifications
- App Store/Play Store deployment

**Key Features**
- Native iOS/Android apps
- Touch-optimized UI
- Offline data caching
- Push notifications
- Camera integration
- GPS/location services
- Biometric auth (fingerprint, face)
- App preferences storage
- Geo-fencing

**Capabilities**
- Mobile dashboards
- Work order execution
- Field service applications
- Mobile data collection
- Real-time notifications
- Offline forms
- Camera capture (inspection photos)
- Location tracking
- Sensor data (GPS, accelerometer)

**When to Use**
- ✅ Field service applications
- ✅ Mobile dashboards (not web)
- ✅ Offline capability needed
- ✅ App Store deployment
- ✅ Biometric authentication
- ✅ Camera/GPS integration
- ❌ Browser access sufficient
- ❌ Low deployment complexity needed

**Performance Characteristics**
- App size: 20-50 MB
- Memory: 100-200 MB active
- Battery: Moderate to high drain
- Offline storage: 10-100 MB configurable
- Network: Works on 3G/4G/WiFi

**Dependencies**
- Perspective Module (backend)
- Ignition gateway (authentication)
- Cloud gateway (optional for Ignition Cloud)

**Licensing**
- **Included:** Professional edition
- **Cost:** Additional for Standard
- **Deployment:** Via Apple/Google app stores
- **Users:** Per-device or per-user licensing

**Platform Support**

| Platform | Version | Status | Notes |
|----------|---------|--------|-------|
| iOS | 12.0+ | Supported | iPhone/iPad |
| Android | 6.0+ (API 23+) | Supported | Phones/tablets |
| Huawei | EMUI 5.0+ | Supported | Huawei App Gallery |

**Common Integrations**
- Perspective (backend API)
- Tag Historian (mobile dashboards)
- Reporting (mobile reports)
- Push notifications (gateway-initiated)
- OPC-UA (real-time data)

**Documentation Links**
- Mobile Module Guide: docs.inductiveautomation.com/docs/8.3/mobile/

---

### 9. MES Module (Sepasoft)

**Overview**
- Manufacturing Execution System
- Production tracking & scheduling
- OEE calculation (Overall Equipment Effectiveness)
- Genealogy/traceability
- Batch management
- Quality tracking
- Work order integration

**Key Features**
- Production scheduling
- Work order tracking
- Batch genealogy
- OEE metrics
- Equipment history
- Production analytics
- Quality defects tracking
- Downtime analysis
- Personnel tracking

**Capabilities**
- Real-time production dashboards
- Equipment efficiency metrics
- Batch traceability
- Quality management
- Production planning
- Downtime root cause
- Operator management
- Shift reporting
- Compliance documentation

**When to Use**
- ✅ Manufacturing facilities
- ✅ Batch traceability required
- ✅ OEE/KPI tracking
- ✅ Quality compliance
- ✅ Production optimization
- ✅ Large-scale manufacturing
- ❌ Simple monitoring only
- ❌ Single machine tracking

**Performance Characteristics**
- Data retention: 1-5 years typical
- Concurrent batches: 100-1000+
- Dashboard latency: 100-500ms
- Report generation: 5-30 seconds
- Scaling: Excellent to 1000+ machines

**Dependencies**
- Tag Historian (data storage)
- SQL Bridge (queries)
- OPC-UA (device data)

**Licensing**
- **Included:** No (separate purchase)
- **Cost:** Significant (per-facility or per-line)
- **Support:** Sepasoft support required
- **Implementation:** Usually requires partner

**OEE Formula**

```
OEE = Availability × Performance × Quality

Where:
- Availability = Production Time / Planned Time
- Performance = Actual Cycles / Theoretical Cycles
- Quality = Good Parts / Total Parts
```

**Common Integrations**
- OPC-UA (device signals)
- SQL Bridge (data storage)
- Reporting (OEE reports)
- Perspective (dashboards)
- Mobile (field apps)

**Documentation Links**
- MES Module: Contact Sepasoft/Inductive Automation

---

### 10. Sequential Function Charts (SFC) Module

**Overview**
- Visual workflow automation
- State-machine execution
- Step-based processes
- Transition conditions
- Action execution
- Graphical programming (IEC 61131-3 standard)

**Key Features**
- Graphical SFC designer
- Steps & transitions
- Actions & activities
- Simultaneous paths
- Macro steps
- Action qualifiers
- Diagnostics
- Validation tools

**Capabilities**
- Batch process automation
- Equipment sequencing
- Conditional workflows
- Parallel processes
- Error recovery
- Operator interactions
- State tracking
- Audit logging

**When to Use**
- ✅ Batch processes
- ✅ Equipment sequencing
- ✅ Complex conditional logic
- ✅ Multi-step workflows
- ✅ Safety-critical automation
- ❌ Simple on/off control
- ❌ Continuous monitoring only

**Performance Characteristics**
- Execution rate: 100 Hz typical
- Max steps: Unlimited
- Parallel paths: Unlimited
- Latency: <10ms typical
- Memory: ~100 KB per SFC instance

**Dependencies**
- None (standalone)
- Works with OPC-UA (device control)

**Licensing**
- **Included:** Professional edition+
- **Cost:** Check license
- **Development:** IEC 61131-3 compliant

**SFC Element Types**

| Element | Purpose | Example |
|---------|---------|---------|
| Step | State or action | "Mixing", "Heating" |
| Transition | Decision point | "Temperature > 100°C" |
| Action | Execute something | "Start motor", "Log data" |
| Parallel | Simultaneous paths | Multi-chamber parallel |
| Jump | Skip to step | Error recovery |

**Common Integrations**
- OPC-UA (device control)
- SQL Bridge (state logging)
- Perspective (UI interaction)
- Alarms (status monitoring)
- Reporting (process history)

**Documentation Links**
- SFC Module: docs.inductiveautomation.com/docs/8.3/sfc/

---

### 11. Transaction Groups Module

**Overview**
- Scheduled data collection & logging
- Batch insert operations
- OPC read/write synchronization
- Database transaction handling
- Group-based organization

**Key Features**
- Grouping of OPC/SQL operations
- Timed execution (interval-based)
- Triggered execution (on-demand)
- Transaction scoping (all-or-nothing)
- Error handling & retry
- Read/write sequencing
- Audit logging

**Capabilities**
- Batch tag reads
- Batch database inserts
- Synchronized tag writes
- Error-safe operations
- Scheduled collection
- Event-driven collection
- Complex workflows
- Compliance audit trails

**When to Use**
- ✅ Batch data collection
- ✅ Periodic reads & logs
- ✅ Tag ↔ database sync
- ✅ Compliance logging
- ✅ High-frequency collection
- ❌ Real-time streaming (use Historian)
- ❌ Simple one-off queries

**Performance Characteristics**
- Groups: 100-1000+ per gateway
- Execution: Sub-second intervals
- Throughput: 1000+ transactions/second
- Latency: 1-10ms typical
- Error recovery: Automatic retry

**Dependencies**
- OPC-UA (read device data)
- SQL Bridge (write to database)

**Licensing**
- **Included:** Standard edition+
- **Cost:** Part of license
- **Scaling:** Excellent for distributed collection

**Transaction Group Types**

| Type | Trigger | Use |
|------|---------|-----|
| Interval | Time-based | Periodic reads every 60s |
| Event | Tag change | On alarm trigger |
| Scheduled | Cron-like | Daily batch export |
| Query | Database | Sync query results |

**Common Integrations**
- OPC-UA (source of data)
- SQL Bridge (destination)
- Historian (time-series storage)
- Alarms (event-triggered collection)

**Documentation Links**
- Transaction Groups: docs.inductiveautomation.com/docs/8.3/transaction-groups/

---

### 12. Compute Module (Edge Gateway)

**Overview**
- Lightweight Ignition gateway for edge deployments
- Designed for remote sites / IoT edge
- Lower resource footprint than full gateway
- All-in-one edge processing
- MQTT communication to primary

**Key Features**
- Minimal installation (~100 MB)
- Lower system requirements
- MQTT uplink to primary gateway
- Local OPC-UA/device connectivity
- Local tag processing
- Offline capability
- Status reporting
- Remote management

**Capabilities**
- Edge data collection
- Local tag processing
- Device connectivity (OPC-UA)
- MQTT uplink
- Alarm filtering
- Data aggregation
- Failover operation
- Remote diagnostics

**When to Use**
- ✅ Remote sites (limited compute)
- ✅ Edge processing
- ✅ Distributed architectures
- ✅ Bandwidth-constrained sites
- ✅ IoT gateways
- ✅ Redundancy nodes
- ❌ UI hosting needed
- ❌ Complex database operations

**Performance Characteristics**
- Memory: 200-500 MB (vs 2-4 GB for full gateway)
- CPU: Modest (Raspberry Pi capable)
- Network: Asynchronous communication
- Latency: 100-500ms to primary
- Concurrent devices: 10-50

**Dependencies**
- MQTT Module (uplink communication)
- Java runtime (same as gateway)

**Licensing**
- **Included:** Professional+
- **Cost:** Per-gateway
- **Deployment:** Unlimited instances

**Compute vs. Full Gateway**

| Feature | Full Gateway | Compute Edge |
|---------|--------------|---------------|
| Perspective | Yes | No (uplink only) |
| Database | Yes | Limited |
| OPC-UA | Yes | Yes |
| MQTT | Yes | Yes (uplink) |
| Reports | Yes | No |
| Resources | 2-4 GB RAM | 200-500 MB RAM |
| Use Case | Enterprise | Edge/Remote |

**Common Integrations**
- MQTT (uplink to primary)
- OPC-UA (local devices)
- SQL Bridge (local queries)
- Perspective (via primary gateway)

**Documentation Links**
- Compute Module: docs.inductiveautomation.com/docs/8.3/compute-edge/

---

### 13. Perspective Workstation Module

**Overview**
- Kiosk/workstation application
- Standalone executable (no browser needed)
- Full-screen HMI application
- Touch-optimized
- Offline support
- Application isolation

**Key Features**
- Standalone app (Windows/Linux/macOS)
- Full-screen kiosk mode
- No browser toolbar/address bar
- Touch gestures optimized
- Session persistence
- Offline mode
- Camera/USB integration
- Print preview built-in

**Capabilities**
- Dedicated HMI workstations
- Operator control panels
- Kiosk deployments
- Touch screens
- Production floor displays
- Meeting room displays
- Emergency access panels

**When to Use**
- ✅ Dedicated workstation
- ✅ Kiosk application
- ✅ Production floor display
- ✅ Touch screen interface
- ✅ Full-screen HMI
- ❌ Multi-user web access
- ❌ Browser-based access needed

**Performance Characteristics**
- Memory: 200-500 MB
- Startup time: <5 seconds
- Display: Multi-monitor support
- Resolution: Up to 4K
- Refresh rate: 60 FPS typical

**Dependencies**
- Perspective Module (backend)
- Ignition gateway (connection)

**Licensing**
- **Included:** Professional 8.1+
- **Cost:** Per-workstation or per-license
- **Deployment:** Downloadable installer

**Common Integrations**
- Perspective (UI backend)
- OPC-UA (real-time data)
- Mobile (sync offline data)
- Reporting (local reports)

**Documentation Links**
- Workstation: docs.inductiveautomation.com/docs/8.3/perspective-workstation/

---

## Premium/Specialized Modules

### 14. Cirrus Link MQTT (Enterprise)

**Overview**
- Advanced MQTT with Sparkplug protocol
- Industrial-grade MQTT Edge Intelligence
- Real-time edge metrics
- Gateway redundancy
- Hierarchical topics
- Certificate management

**Key Features**
- Sparkplug B protocol (industrial MQTT standard)
- Edge node architecture
- Real-time system metrics
- Device inventory
- Automatic rebirth handling
- Certificate pinning
- Multi-site mesh
- Cloud compatibility

**Use Cases**
- Multi-site operations
- Cloud-to-edge integration
- Industrial IoT networks
- Real-time analytics
- Predictive maintenance
- Distributed manufacturing

**When to Use**
- ✅ Enterprise MQTT
- ✅ Sparkplug requirement
- ✅ Multi-site operations
- ✅ Cloud integration
- ❌ Simple MQTT sufficient

**Licensing**
- **Cost:** Premium add-on
- **Support:** Cirrus Link support
- **Deployment:** Unlimited

**Documentation Links**
- Cirrus Link: www.cirrus-link.com/

---

### 15. MEE (Mobile Edge Engine)

**Overview**
- Mobile field service edge gateway
- Smartphone/tablet-based gateway
- Offline-first architecture
- Cloud sync capability

**Use Cases**
- Field service technicians
- Mobile field operations
- Disconnected operations
- Remote site management

**Licensing**
- **Cost:** Premium add-on
- **Deployment:** Per device

---

## Module Dependencies Matrix

```
┌─────────────────────────────────────────────┐
│ DEPENDENCY HIERARCHY (Bottom-up)            │
├─────────────────────────────────────────────┤
│ Core Gateway (required for all)             │
│         ↓                                    │
│ ├─ Perspective (UI)                        │
│ ├─ Vision (Legacy UI)                      │
│ ├─ OPC-UA (Devices)                        │
│ ├─ SQL Bridge (Database)                   │
│ │   ├─ Tag Historian (requires SQL)        │
│ │   └─ Transaction Groups (requires OPC)   │
│ ├─ Reporting (requires Perspective)        │
│ ├─ MQTT Transmission (standalone)          │
│ ├─ Mobile (requires Perspective backend)   │
│ ├─ MES (requires Historian + SQL)          │
│ ├─ SFC (standalone, uses OPC-UA output)    │
│ ├─ Compute/Edge (standalone + MQTT)        │
│ ├─ Perspective Workstation (requires Perspective)   │
│ └─ Cirrus Link (advanced MQTT)             │
└─────────────────────────────────────────────┘
```

**Hard Dependencies**
- Tag Historian → SQL Bridge (must have SQL configured)
- Reporting → Perspective (for embedding)
- Mobile → Perspective backend
- MES → SQL Bridge + Tag Historian
- Perspective Workstation → Perspective Module

**Optional Integration** (works best with but not required)
- All modules → OPC-UA (optional, for device data)
- All modules → SQL Bridge (optional, for data storage)
- All modules → Tag Historian (optional, for trending)

---

## Module Selection Guide

### Scenario: Simple Monitoring Dashboard
```
Required:
- Perspective (UI)
- OPC-UA (devices) — optional if no devices

Optional:
- SQL Bridge (store readings)
- Reporting (periodic snapshots)
```

### Scenario: Production Tracking
```
Required:
- Perspective (UI)
- OPC-UA (devices)
- SQL Bridge (data storage)
- Tag Historian (trending)

Optional:
- Reporting (production reports)
- MES (advanced tracking)
- Mobile (field access)
```

### Scenario: Manufacturing Facility
```
Required:
- Perspective (UI)
- OPC-UA (device network)
- SQL Bridge (data)
- Tag Historian (history)
- Reporting (compliance)

Optional:
- MES (production management)
- Mobile (field service)
- MQTT (cloud integration)
- SFC (batch automation)
```

### Scenario: Multi-Site Enterprise
```
Required:
- Perspective (central UI)
- OPC-UA (primary gateway)
- SQL Bridge (central database)
- Tag Historian (enterprise history)
- Reporting (enterprise reports)

Recommended:
- Compute/Edge (remote sites)
- MQTT (inter-site communication)
- Mobile (field operations)
- Cirrus Link (enterprise MQTT)
- MES (production optimization)
```

### Scenario: Edge/IoT Deployment
```
Required:
- Compute Module (lightweight edge)
- OPC-UA (local device connectivity)
- MQTT (cloud communication)

Optional:
- SQL Bridge (local data)
- Perspective (via primary gateway)
```

---

## License Tier Comparison

| Module | Standard | Professional | Enterprise |
|--------|----------|--------------|------------|
| Perspective | ✅ | ✅ | ✅ |
| Vision | ✅ | ✅ | ✅ |
| OPC-UA | ✅ | ✅ | ✅ |
| SQL Bridge | ✅ | ✅ | ✅ |
| Tag Historian | ✅ | ✅ | ✅ |
| Reporting | ✅ | ✅ | ✅ |
| MQTT Transmission | ✅ | ✅ | ✅ |
| Transaction Groups | ✅ | ✅ | ✅ |
| Mobile Module | ❌ | ✅ | ✅ |
| MES (Sepasoft) | ❌ | ❌ | License+ |
| SFC | ❌ | ✅ | ✅ |
| Compute/Edge | ❌ | ✅ | ✅ |
| Perspective Workstation | ❌ | ✅ (8.1+) | ✅ |
| Cirrus Link | ❌ | ❌ | License+ |

**Note:** Check specific license agreement for exact inclusions.

---

## Module Management in Gateway

### Enable/Disable Module
```
1. Admin Console (gateway port 8088)
2. Config → Modules
3. Find module name
4. Check box to enable / uncheck to disable
5. Gateway downloads & restarts (1-2 min)
6. Verify in Status → Modules
```

### Monitor Module Status
```
Admin Console → Status → Modules
- Shows: Name, Version, License Status
- Can enable/disable from here
- Shows any errors or warnings
```

### Check Module Version
```
Admin Console → Status → Modules → [Module Name]
- Version: Shows installed version (e.g., 8.3.5)
- Compare with docs.inductiveautomation.com for latest
```

### Troubleshoot Module Issues
```
Admin Console → Status → Diagnostics → Module Issues
- Check logs (Logs → Wrapper.log, System.log)
- Restart module via Admin Console
- Check system resources (RAM, disk)
- Verify license status
```

---

## Module Performance & Resource Impact

### Gateway Memory Requirements

| Configuration | RAM | Modules Loaded |
|---------------|-----|---|
| Minimal | 1 GB | Perspective, OPC-UA |
| Small | 2 GB | + SQL Bridge, Historian |
| Medium | 4 GB | + Reporting, MQTT |
| Large | 8 GB | + MES, Mobile, SFC |
| Enterprise | 16+ GB | All modules, 1000+ tags |

**Rule of Thumb:** 
- Each OPC-UA device: ~5-10 MB
- Each Historian-logged tag: ~1-5 KB/day
- Each active session: ~50-100 MB
- Each module (avg): ~50-100 MB

### Startup Time Impacts

| Configuration | Startup Time |
|---------------|---|
| Perspective + OPC-UA | ~30-60 sec |
| + Historian | ~60-90 sec |
| + Reporting | ~90-120 sec |
| + MES | ~120-180 sec |
| Full (all modules) | ~180-240 sec |

---

## Module Update & Maintenance

### Checking for Updates
```
Admin Console → Config → Modules
- System checks automatically (weekly)
- Shows available updates with version number
- Can update individual modules without restart (usually)
```

### Module Update Procedure
```
1. Note current version
2. Admin Console → Config → Modules
3. Click [Update] if available
4. Gateway may restart (~2 min)
5. Verify new version in Status → Modules
```

### Version Compatibility
- All modules must be same Ignition version (8.3.x)
- Older modules with newer gateway not supported
- Must update modules with gateway updates

---

## Cloud & Hybrid Deployment

### MQTT to Cloud
- Perspective → local gateway
- MQTT Transmission → AWS IoT, Azure IoT Hub, Google Cloud
- Lightweight cloud integration

### Ignition Cloud
- Hosted Ignition gateway (Inductive Automation cloud)
- Perspective accessible globally
- No firewall ports needed
- Monthly subscription

### Hybrid Architecture
```
          Cloud (Ignition Cloud)
                  ↓
        Primary Ignition Gateway
          /        |        \
    Perspective  MQTT     OPC-UA
        |           |        |
    Browser    Compute    Devices
              Module
```

---

## Best Practices

1. **Enable only needed modules** (reduces memory, startup time)
2. **Monitor module resource usage** (Admin Console → Status)
3. **Keep modules updated** (with gateway updates)
4. **Test module upgrades** in dev environment first
5. **Document module dependencies** in your architecture
6. **Verify licensing** annually (Status → Licensing)
7. **Archive old modules** if migrating (e.g., Vision → Perspective)

---

## Additional Resources

- **Official Docs:** docs.inductiveautomation.com/docs/8.3/
- **Modules List:** Admin Console → Status → Modules
- **License Check:** Admin Console → Status → Licensing
- **Community:** inductiveautomation.com/community
- **Support:** inductiveautomation.com/support

---

**Document Version:** 2.0  
**Last Updated:** 2026-07-13  
**Ignition Version:** 8.3+  
**Format:** Markdown reference guide

---

## See Also

**Prerequisites:** [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md)

**Builds toward:** [71-REPORTING-MODULE](71-REPORTING-MODULE.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md), [92-MOBILE-MODULE-PERSPECTIVE](92-MOBILE-MODULE-PERSPECTIVE.md), [28-PLATFORM-TRANSACTIONS-SFCS](28-PLATFORM-TRANSACTIONS-SFCS.md)

**Related:** [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md), [79-MODULES-ARCHITECTURE](79-MODULES-ARCHITECTURE.md), [71-REPORTING-MODULE](71-REPORTING-MODULE.md), [34-APPENDIX-VISION-MODULE](34-APPENDIX-VISION-MODULE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
