> **Skill level:** 100 · **Read first:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 03-PLATFORM-CORE-CONCEPTS

# Ignition Platform Core Concepts (v8.3)

> Comprehensive reference for Ignition platform architecture, core components, and fundamental development concepts.

---

## Table of Contents
1. [Platform Overview](#platform-overview)
2. [Gateway & Core Services](#gateway--core-services)
3. [Designer & Project Development](#designer--project-development)
4. [Project Structure & Organization](#project-structure--organization)
5. [Licensing Model](#licensing-model)
6. [Module System Architecture](#module-system-architecture)
7. [Tags & Data Integration](#tags--data-integration)
8. [Client Deployment Models](#client-deployment-models)
9. [Key Architectural Patterns](#key-architectural-patterns)

---

## Platform Overview

### What is Ignition?

Ignition is a unified industrial software platform that provides core foundational capabilities for building SCADA/HMI applications. The platform delivers:

- **Cross-platform compatibility** (Windows, Linux, macOS)
- **Modular extensibility** for customized deployments
- **Server-based architecture** with web-based gateway
- **Unlimited client connections** per server license
- **Real-time data integration** with devices and databases
- **RESTful API** using OpenAPI standards for external system integration

### Core Platform Functions

| Function | Description |
|----------|-------------|
| Device Connectivity | Connects to PLCs, sensors, and industrial controllers via OPC and native protocols |
| Data Management | Central tag system storing all application data with historical logging |
| Application Runtime | Hosts Perspective web applications and Vision desktop applications |
| Module Management | Coordinates execution of optional modules for extended functionality |
| Configuration Hub | Single point for licensing, users, authentication, and security settings |
| Licensing & Activation | Manages module licenses and feature availability |
| Database Integration | Supports SQL queries, transaction groups, and data logging |

### Architecture Layers

```
┌─────────────────────────────────────┐
│   User Application Layer            │  (Perspective Web Apps, Vision Clients)
├─────────────────────────────────────┤
│   HMI/SCADA Module Layer            │  (Vision, Perspective, SQL Bridge, etc.)
├─────────────────────────────────────┤
│   Platform Core Layer               │  (Tags, Gateway, Licensing, Security)
├─────────────────────────────────────┤
│   Operating System Layer            │  (Windows, Linux, macOS)
└─────────────────────────────────────┘
```

---

## Gateway & Core Services

### Primary Role

The Gateway is "the primary software service that drives everything in Ignition." It operates as a persistent background web service managing all platform operations.

### Gateway Access

- **Default URL**: `http://localhost:8088` (local access)
- **Remote Access**: `http://{IP-or-hostname}:8088`
- **Example**: `http://10.0.28.30:8088`
- **Access Method**: Standard web browser on any operating system

### Key Responsibilities

The Gateway manages:

1. **Data Integration**
   - Connects to external data sources (databases, OPCs, devices)
   - Maintains real-time data synchronization
   - Logs historical data to Tag Historian

2. **Module Execution**
   - Runs Perspective application servers
   - Manages Vision client communication
   - Coordinates third-party module functionality

3. **Client Communication**
   - Hosts Designer for project development
   - Delivers Perspective web applications to browsers
   - Manages Vision Client connections
   - Handles authentication and authorization

4. **Configuration Management**
   - Licensing and activation
   - Database connection management
   - Security policies and user management
   - Alarm pipeline configuration
   - OPC server and device connections

### Operational Control

The Gateway service can be controlled through:

- **Operating System Services** (Windows Service Manager, Linux systemctl)
- **Batch Scripts** (startup.bat, shutdown.bat in installation directory)
- **Gateway Command-line Utility** (gwcmd) for administrative tasks
- **Web Console** at Platform > System > Services

### Installation Requirements

- **JRE/JDK**: Java 11 or later
- **Database**: PostgreSQL (included), or external database for production
- **Ports**: 8088 (HTTP), 8089 (HTTPS), 7211 (OPC-UA)
- **Memory**: Scales with tag count, client connections, and module load

---

## Designer & Project Development

### Overview

The Designer is Ignition's primary development environment for creating user interfaces and application logic. It combines visual design tools with scripting capabilities for rapid application development.

### Designer Access

1. **Installation**: Designer Launcher application installed on development workstation
2. **Discovery**: Automatically detects local and remote Gateways
3. **Launch Method**: 
   - Launcher application selects appropriate OS-specific client
   - Web-based launch technology
   - Creates desktop shortcuts for projects

### Project Creation Workflow

#### Step 1: Open/Create Project Dialog

The Designer launches with project management window offering:
- Create new project
- Import existing projects
- Open recent projects
- Access project templates

#### Step 2: Configuration

When creating a new project, configure:

| Setting | Options |
|---------|---------|
| **Project Name** | Alphanumeric + underscores only (used internally) |
| **Project Title** | Display name for end users |
| **Project Type** | Perspective (web-based) or Vision (desktop) |
| **Templates** | Pre-configured starter templates |
| **Authentication** | Database, Directory, Gateway default, etc. |
| **Tag Provider** | Internal default or remote provider |
| **Database** | Configure SQL connections if needed |

### Development Interface

#### Main Workspace Components

```
┌──────────────────────────────────────────────────┐
│  Menu Bar (File, Edit, View, Tools, Help)        │
├──────┬───────────────────────┬──────────────────┤
│      │                       │                  │
│  Project  │   Canvas/Editor  │ Properties       │
│  Browser  │   (Drag-drop     │ Inspector        │
│           │    components)   │                  │
│           │                  │ Binding Config   │
├──────┴───────────────────────┴──────────────────┤
│  Output Console (Errors, Warnings, Info)        │
└──────────────────────────────────────────────────┘
```

#### Design Mode vs. Preview Mode

- **Design Mode**: Edit properties, configure bindings, arrange components
- **Preview Mode**: Toggle button to test application behavior in real-time

### Core Development Features

#### 1. Component Palette
Pre-built UI elements for rapid screen construction:
- Buttons, text fields, tables, charts, graphs
- Containers, layouts, navigation components
- Specialized industrial controls (gauges, sliders, etc.)

#### 2. Data Binding
Direct connection of UI components to data sources:
```
Component → Tag Binding → OPC Value
Component → Expression Binding → Calculated Values
Component → Database Query → SQL Results
```

#### 3. Event Scripting
Python-based scripting for business logic:
- Component event handlers (mouseClicked, valueChanged, etc.)
- Gateway event scripts (startup, shutdown, system events)
- User-defined functions in shared libraries

#### 4. Supporting Tools

| Tool | Purpose |
|------|---------|
| **Output Console** | View Python errors and print statements |
| **Script Console** | Test Python code snippets interactively |
| **Database Query Browser** | Write and test SQL queries |
| **Translation Manager** | Configure multi-language support |
| **Project Import/Export** | Package projects as .zip files |

### Concurrent Development

#### Lock-Free Strategy
- Multiple designers can edit the same project simultaneously
- No resource-level locking prevents collaboration
- Conflicts resolved at save time through visual dialogs

#### Conflict Resolution Process
When save conflicts occur:
1. System presents conflict dialog showing affected lines
2. Developer chooses:
   - Accept own changes
   - Accept peer's changes
   - Cancel save to coordinate externally

### Project Organization

#### Component Structure

Projects contain:
- **Views** (screens/pages displayed to end users)
- **Templates** (reusable view components)
- **Components** (custom UI building blocks)
- **Styles** (CSS and theme definitions)
- **Resources** (shared images, scripts, constants)

#### Naming Conventions

Follow these conventions for maintainability:
- Views: `PascalCase` (e.g., `MainDashboard`, `InventoryPage`)
- Tags: `descriptive_name` (e.g., `Motor_3_Amps`, `Tank_Level`)
- Functions: `camelCase` (e.g., `calculateRuntime`, `fetchOrderData`)
- Constants: `UPPER_CASE` (e.g., `MAX_TANK_LEVEL`, `ALERT_THRESHOLD`)

---

## Project Structure & Organization

### What is a Project?

An Ignition project is a configuration and design unit containing all application-specific elements. Each project represents a complete, deployable application.

### Project Components

#### 1. Views (User Interface)
- Screens displayed to end users through Perspective or Vision clients
- Hierarchical organization (parent views, child views)
- Template-based for consistency
- Responsive design support (Perspective)

#### 2. Templates
- Reusable view components containing preconfigured layout and logic
- Support parameterization for flexibility
- Reduce development time and maintenance burden
- Example: A "Temperature Tank" template with built-in gauges and controls

#### 3. Resources
- **Images & Media**: PNG, JPG, SVG files
- **Scripts**: Python libraries, functions, classes
- **Constants**: Shared configuration values
- **Themes**: CSS styling and appearance definitions

#### 4. Transaction Groups
- Scheduled database write operations
- Support complex multi-step transactions
- Timestamp and log historical data
- Example: Log production counts every 30 seconds

#### 5. Reports
- PDF generation from Reporting Module
- Template-based report design
- Scheduled or on-demand generation
- Parameterized reports for flexibility

#### 6. Alarm Pipelines
- Custom alarming logic and escalation
- Event-driven pipeline architecture
- Integration with notification systems
- Alert routing and acknowledgment workflows

#### 7. Sequential Function Charts
- Graphical state machine programming
- Industrial control sequences
- Transitions based on conditions
- Integration with tag system

### Gateway Resources vs. Project Resources

#### Shared (Gateway-Level)
- Database connections
- OPC/device connections
- Tag providers
- Users and roles
- Authentication configurations
- License settings

#### Project-Specific
- Views and templates
- Scripts and functions
- Resources (images, themes)
- Project authentication (independent role sets)
- Project-level database selections

#### Deployment Model

```
Project Export → .zip file (project components only)
      ↓
Project Import → Merge into Gateway
      ↓
Runtime Clients → Access via Designer/Vision/Perspective
```

### Project Settings

#### Authentication Configuration

Each project independently configures:
- **Authentication Source**: Database users, LDAP directory, SSO
- **Role Sets**: Custom roles for authorization
- **Permissions**: View/edit access controls
- **Session Management**: Login timeouts, concurrent session limits

#### Database Configuration

Projects can:
- Reference Gateway database connections
- Configure connection pooling
- Set query timeouts
- Implement connection pooling for performance

#### Export/Import

- **Export**: Package as .zip containing project-specific resources only
- **Import**: Merge into existing Gateway with options to:
  - Rename conflicting projects
  - Overwrite existing projects
  - Review import summary

---

## Licensing Model

### Core Principles

1. **Server-Based**: One license per Gateway handles unlimited client connections
2. **Module-Based**: Purchase only functionality you need
3. **No Per-User Licensing**: Clients don't require individual licenses
4. **No Tag Limits**: License based on features, not tag count

### License Types

#### Standard Licenses (6-Character Keys)

Traditional perpetual licenses with flexible activation:
- **Online Activation**: Real-time verification via internet
- **Offline Activation**: Request/response files for air-gapped environments
- **Transferable**: Unactivate on one server, reactivate on another

**Activation Process:**
1. Navigate to Gateway → Platform > System > Licensing
2. Enter 6-character license key
3. Activate online or offline
4. License persists across Gateway restarts

#### Leased Licenses (8-Character Keys)

Cloud-optimized licenses with additional token requirements:
- **Use Cases**: Docker containers, Kubernetes pods, cloud deployments
- **Requirements**: License key + activation token
- **Renewal**: Automatic renewal via activation server
- **Duration**: Typically annual

### Trial Mode

#### Evaluation Period
- **Duration**: 2-hour countdown timer
- **Reset**: Can be reset unlimited times
- **Application**: Unlicensed modules operate in trial mode
- **Display**: Trial banner on:
  - Gateway web console
  - Vision Client interface
  - Perspective application status bar

#### Licensed vs. Trial Modules
- **Licensed Modules**: Never timeout, run indefinitely
- **Trial Modules**: 2-hour limit per session until purchased

### License Management

#### Key Operations

| Operation | Purpose |
|-----------|---------|
| **Transfer License** | Move between servers (unactivate → reactivate) |
| **Multiple Licenses** | Support multiple license keys per Gateway (one per platform version) |
| **Emergency Activation** | 7-day temporary access if hardware fails |
| **License Details** | View applied and effective licenses in console |

#### License Status Indicators

Each module displays:
- **Activated**: Licensed and fully functional
- **Trial**: Operating in evaluation mode
- **Free**: Always available (e.g., Platform Core)
- **Inactive**: Not yet activated

### Solution Suites

Inductive Automation offers bundled module packages:

| Suite | Includes | Use Case |
|-------|----------|----------|
| **Application Building** | Perspective, Reporting | Web applications, reporting |
| **Industrial Operations** | Tag Historian, Alarm Notification | Data logging, alerting |
| **Analytics** | SQL Bridge, Tag Historian, Perspective | Data analysis, dashboards |

#### Upgrade Protection

Optional subscription adding:
- New modules automatically included
- Feature updates without additional cost
- Annual renewal option

### Example License Scenarios

#### Scenario 1: Small Manufacturing Site
```
Hardware: Single server
License: Platform + Perspective + SQL Bridge
Cost: 3 module licenses
Clients: Unlimited Vision/Perspective
```

#### Scenario 2: Multi-Site Enterprise
```
Deployment: 5 servers, each with platform instance
Licensing: One Platform license per server
Modules: Perspective, SQL Bridge, Historian (all servers)
Remote Access: Through Perspective web application
```

#### Scenario 3: Cloud/Container Deployment
```
Infrastructure: Kubernetes cluster
License: Leased license with activation token
Modules: Platform + Perspective
Scaling: Add/remove pods without relicensing
```

---

## Module System Architecture

### Module Overview

Modules extend Ignition's functionality through a pluggable architecture. Each module is a self-contained component providing specific capabilities.

**Module Analogy**: "Similar to applications for a smartphone in how they are seamlessly integrated and provide additional capabilities."

### Core Modules (Platform Base)

All Ignition installations include:

| Module | Purpose | Always Free |
|--------|---------|-------------|
| **Platform Core** | Tag system, database, security, gateway | Yes |
| **OPC-UA** | Native OPC-UA server/client | Yes |
| **Database Connectivity** | SQL database integration | Yes |

### Optional Modules

#### User Interface Frameworks

**Perspective Module**
- Modern web-based application framework
- Browser-based clients (Chrome, Safari, Firefox, Edge)
- Mobile-responsive design support
- Two-factor authentication support
- Touch-friendly controls
- Real-time data updates via WebSocket

**Vision Module**
- Traditional desktop application framework
- Native Windows/Mac/Linux clients
- Multi-monitor support
- High-performance graphics
- Desktop integration (system tray, native dialogs)
- Offline capability

#### Data & Analytics

**SQL Bridge Module**
- Scheduled queries with logging
- Real-time database synchronization
- Transaction groups for atomic operations
- Query results → tags or database writes
- Report generation integration

**Tag Historian Module**
- Historical data storage for tags
- Configurable logging (value change, sampling, etc.)
- High-performance time-series database
- Query builder and data export
- Integration with Perspective charts

**Reporting Module**
- PDF report generation
- Template-based design
- Parameterized reports
- Scheduled execution
- Email delivery integration

#### Operations & Connectivity

**Alarm Notification Module**
- Email, SMS, mobile push notifications
- Escalation pipelines
- Alarm routing and filtering
- Integration with popular platforms

**MQTT Module**
- Publish/subscribe messaging
- MQTT client connectivity
- Bi-directional data synchronization
- IoT integration

**OPC-DA Module**
- Legacy OPC-DA protocol support
- Windows-only connectivity
- Backwards compatibility

#### Development & Administration

**SFC Module**
- Sequential Function Charts
- State machine development
- Industrial control sequences
- Graphical programming

**Mobile Module**
- iOS app development (if applicable)
- Native mobile capabilities

### Module Architecture

#### Runtime Execution Model

```
┌─────────────────────────────────────┐
│   Gateway JVM Process               │
├─────────────────────────────────────┤
│   Module Container (Thread Pool)    │
├─────────────────────────────────────┤
│   ┌───────────┐  ┌──────────┐      │
│   │ Perspective│  │SQL Bridge│      │
│   │ Module    │  │Module    │      │
│   └───────────┘  └──────────┘      │
├─────────────────────────────────────┤
│   Tag Engine (Shared)               │
├─────────────────────────────────────┤
│   Database & OPC Connectivity       │
└─────────────────────────────────────┘
```

#### Module Lifecycle

1. **Installation**: Download and extract module package
2. **Configuration**: Module settings in Gateway console
3. **Activation**: Module requires license key to run
4. **Execution**: Module thread pool in Gateway JVM
5. **Monitoring**: Gateway dashboard shows module status
6. **Updates**: Upgrade available modules independently

### Module Integration Points

#### 1. Tag System (All Modules)
Modules read/write tags for data exchange:
- Perspective components → tag bindings → display real-time data
- SQL Bridge → tags → trigger notifications
- Historian → tags → historical queries

#### 2. Event System (All Modules)
Modules subscribe to platform events:
- Tag value changes
- Client connection/disconnection
- Gateway startup/shutdown
- Scheduled events

#### 3. Database Connectivity (Optional Modules)
Modules access databases through:
- Named connections defined in Gateway
- Connection pooling for performance
- Query execution with parameters

#### 4. Authentication/Authorization (All Modules)
Modules respect:
- User authentication configuration
- Role-based access control
- Project-level permissions

### Third-Party Modules

Inductive Automation supports third-party module development:
- Custom modules extend platform functionality
- Module SDK available to partners
- Marketplace for community modules
- Integration through standard APIs

### Module Status Monitoring

In Gateway console (Platform > Modules):
- View all installed modules
- Check activation status
- Monitor module health/uptime
- View resource consumption
- Access module-specific configuration

---

## Tags & Data Integration

### What Are Tags?

Tags are the fundamental data model in Ignition. They represent real-time and historical values throughout the system.

**Definition**: "Tags provide a consistent data model throughout Ignition" for status monitoring, control, and data logging.

### Core Characteristics

| Aspect | Description |
|--------|-------------|
| **Scope** | Global across Gateway (visible to all projects) |
| **Performance** | Handles millions of tags with thousands of changes/second |
| **History** | Can be logged for time-series analysis |
| **Binding** | Direct drag-drop binding to UI components |
| **Alarming** | Supports dynamic alarm configuration |
| **UDTs** | Support object-oriented tag design |

### Tag Types

#### 1. Memory Tags
- Stored in Gateway memory
- No external data source
- Useful for calculations, temporary data
- Fast read/write performance

#### 2. OPC Tags
- Linked to OPC data source (OPC-UA or OPC-DA)
- Real-time updates from industrial devices
- Automatic polling/subscription
- Example: `[OPC Server].[Device Name].Motor_Speed`

#### 3. Expression Tags
- Derived from formulas
- Automatically recalculate when dependencies change
- Example: `{Tank_Level} / 1000 * 100` (percentage)

#### 4. Query Tags
- Results from SQL queries
- Execute on interval or on-demand
- Example: SELECT COUNT(*) FROM orders WHERE status='pending'

#### 5. Reference Tags
- Link to other tags
- Simplify hierarchical access
- Create aliases for clarity

### Tag Organization

#### Hierarchical Structure

Tags are organized in folders for clarity:

```
Root/
├── Tanks/
│   ├── Tank1/
│   │   ├── Level
│   │   ├── Temperature
│   │   └── Pressure
│   └── Tank2/
│       ├── Level
│       └── Temperature
├── Motors/
│   ├── Motor1/
│   │   ├── Speed
│   │   └── Current
│   └── Motor2/
└── System/
    ├── ProductionCount
    └── ShiftHours
```

#### Naming Conventions

**Rules**:
- First character: Letter, number, or underscore
- Subsequent characters: Letters, numbers, underscores, spaces, `'`, `-`, `:`, `(`, `)`
- No duplicate names within same folder

**Best Practices**:
- Use descriptive names reflecting the physical quantity
- Example: `Motor_3_Speed_RPM` rather than `M3_S`
- Use underscores or spaces for readability
- Avoid abbreviations that create confusion

#### Planning Importance

> **Critical**: Renaming or moving tags breaks all bindings in views. Plan tag structure upfront to avoid widespread breakage.

### Tag Providers

#### Internal Provider (Default)
- Built-in tag database within Gateway
- Stored in PostgreSQL
- Recommended for most installations
- No additional configuration required

#### Remote Provider
- Link to tags on another Ignition installation
- Enables distributed SCADA architectures
- Supports multi-site synchronization
- Example: Regional gateways reporting to central hub

### User Defined Types (UDTs)

Object-oriented tag design for complex structures:

```
UDT: Motor
├── Speed (int)
├── Current (float)
├── Temperature (float)
└── Status (string)

Instance: Motor_1
├── Motor_1.Speed
├── Motor_1.Current
├── Motor_1.Temperature
└── Motor_1.Status
```

**Benefits**:
- Reuse common structures
- Consistency across similar devices
- Template-based configuration
- Easier maintenance and updates

### Data Binding to Components

#### Binding Types

| Binding Type | Source | Use Case |
|--------------|--------|----------|
| **Tag Binding** | `{TagPath}` | Direct tag value display |
| **Expression Binding** | `{tag1} + {tag2} * 2` | Calculated displays |
| **Property Binding** | Link component property to tag | Dynamic styling |
| **Script Binding** | Python expression | Complex logic |

#### Example: Tank Level Display

```
Component: Label
Property: text
Binding: {Tanks/Tank1/Level}
Result: Label displays current tank level value
```

### Integration with External Systems

#### OPC-UA Connectivity
- Gateway hosts OPC-UA server
- External systems subscribe to tags
- Industrial devices publish via OPC-UA client

#### Database Integration
- Tags read from SQL queries
- Tags write to databases via transaction groups
- Historian stores historical data

#### REST API
- External systems query tags via HTTP
- JSON response format
- OpenAPI standard

---

## Client Deployment Models

### Client Types

#### 1. Designer (Development)
- Development and testing environment
- Project creation and editing
- Testing and debugging
- Deployed on developer workstations only

#### 2. Perspective Workstation (Production)
- Web-based client accessible from browsers
- Modern, mobile-responsive applications
- Access from any device with internet connection
- No client installation required

**Deployment**:
- Browser at `http://{gateway}:8088/{project-name}`
- Mobile-friendly responsive design
- Touch-optimized controls

#### 3. Vision Client (Production)
- Desktop application for specific workstations
- High-performance graphics rendering
- Multi-monitor support
- Offline capability

**Deployment**:
- Vision Client Launcher discovers and launches projects
- Creates local desktop shortcuts
- Automatic updates from Gateway

### Launching Clients from Gateway

#### Discovery Process

The Gateway maintains a list of available projects. Clients connect and:
1. Download project metadata
2. Verify licensing
3. Authenticate user
4. Load application

#### Auto-Launch Configuration

Projects can be configured to auto-launch in:
- Startup views on client connection
- Specific project on application start
- Predefined user on login

### Mobile & Responsive Design

#### Perspective Capabilities
- Responsive grid layouts
- Touch gesture support (swipe, pinch, drag)
- Mobile-optimized components
- iOS and Android browser support
- Native app option with cordova

#### Vision Limitations
- Desktop-only application
- Not optimized for mobile
- Requires Windows/Mac/Linux workstation

### Performance Considerations

#### Tag Subscription Model
- Clients only receive tags they display
- Reduces network bandwidth
- Minimizes server load
- Automatic subscription management

#### Data Refresh Rates
- Configurable per binding
- Default: real-time updates via WebSocket (Perspective)
- Polling interval: Vision (configurable)
- Expression tags recalculate on dependency change

---

## Key Architectural Patterns

### Pattern 1: Tag-Driven Architecture

**Design Principle**: All data flows through tags.

```
Data Source → OPC/Database → Tags → UI Bindings → User Display
User Input → Component Event → Script → Tag Write → System Update
```

**Benefits**:
- Decouples data from presentation
- Enables real-time updates
- Supports alarming and logging
- Facilitates testing

### Pattern 2: Centralized Gateway

**Design Principle**: Single Gateway manages all platform services.

```
┌────────────────────────────────┐
│   Ignition Gateway             │
│   - Tag Engine                 │
│   - Perspective Renderer       │
│   - Module Executor            │
│   - Database Connections       │
│   - Authentication             │
└────────────────────────────────┘
     ↓            ↓            ↓
  Designer    Perspective   Vision
  Clients     Browsers      Clients
```

**Implications**:
- Gateway failure affects all users
- Central point for licensing
- Simplified administration
- Single performance bottleneck

### Pattern 3: Module Composition

**Design Principle**: Extend functionality through discrete modules.

```
Core Platform
    ↓
Perspective (UI) + SQL Bridge (Data) + Historian (Logging)
    ↓
Third-Party Modules (Custom Extensions)
    ↓
User Applications
```

**Benefits**:
- Pay only for needed features
- Independent module updates
- Reduce deployment complexity
- Support custom requirements

### Pattern 4: Multi-Project Isolation

**Design Principle**: Each project is independent and self-contained.

```
Single Gateway
├─ Project A (Role Set A, Auth A)
├─ Project B (Role Set B, Auth B)
└─ Project C (Role Set C, Auth C)

Shared Resources:
├─ Tag Providers
├─ Database Connections
└─ OPC Connections
```

**Considerations**:
- Projects share Gateway resources
- Isolated role sets and authentication
- Independent project deployment
- Resource contention possible

### Pattern 5: Hierarchical Tag Organization

**Design Principle**: Organize tags logically by function/location.

```
/Manufacturing/
├─ /Assembly/Motors/
├─ /Assembly/Pumps/
├─ /Packaging/Motors/
├─ /Packaging/Conveyers/
└─ /System/Health/
```

**Impact**:
- Easier navigation and discovery
- Improved performance (folder-level subscriptions)
- Consistent naming across organization
- Enables security at folder level

### Pattern 6: Stateless Client Applications

**Design Principle**: Clients display Gateway state, not maintain local state.

```
Client View = f(Gateway Tags, Expressions)
Client Actions → Gateway Changes → Auto-Update Display
```

**Benefits**:
- Multiple clients always synchronized
- Stateless horizontal scaling (future)
- Simplified debugging
- Reliable data consistency

---

## Summary

The Ignition platform provides a unified, modular architecture for industrial applications:

1. **Gateway Core**: Centralized service managing all platform operations
2. **Designer**: Visual development environment for rapid application creation
3. **Modular Extensibility**: Choose only modules needed for your deployment
4. **Tag-Driven Data Model**: Consistent data integration across all components
5. **Flexible Deployment**: Support for traditional and cloud-based architectures
6. **Server-Based Licensing**: Unlimited clients with single platform license
7. **Real-Time Capabilities**: High-performance data binding and updates

### Recommended Reading Sequence

For new users:
1. Start with Gateway overview and web console navigation
2. Learn tag system and data organization
3. Explore Designer and basic view creation
4. Study component bindings and data flow
5. Progress to event scripting and complex applications
6. Study module-specific documentation (Perspective, Vision, SQL Bridge, etc.)

### Key Resources

- **Gateway Web Console**: `http://localhost:8088` — administration hub
- **Designer Application**: Development environment for project creation
- **Official Documentation**: docs.inductiveautomation.com/docs/8.3/
- **Ignition Forum**: Community support and knowledge base
- **Expression Reference**: Built-in to Designer (Help menu)

---

**Document Version**: 8.3  
**Last Updated**: 2026-07-13  
**Content Source**: docs.inductiveautomation.com/docs/8.3/platform

---

## See Also

**Prerequisites:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md)

**Builds toward:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Related:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [60-INSTALLATION-SETUP](60-INSTALLATION-SETUP.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
