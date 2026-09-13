> **Skill level:** 300 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 25-PLATFORM-TAGS-ARCHITECTURE

# Ignition 8.3 Platform Tags Architecture

## Overview
Tags are the fundamental data structures in Ignition, representing real-time and historical data points that flow through the system. They serve as the core mechanism for storing, retrieving, and distributing values across your automation environment. Tags operate across a distributed architecture supporting thousands of value changes per second and millions of individual tags.

---

## 1. Tag Engine Architecture

### Distributed Tag System
Ignition implements a two-tier tag architecture:

#### Gateway Level (Server-Side)
- Central tag storage and execution occurs at the Gateway
- Tag Providers manage collections of tags (tag databases)
- Realtime Providers enable local tag storage and remote sharing
- Gateway supports:
  - Unlimited custom Tag Providers
  - Automatic default Standard provider created on installation
  - System Tag Provider (Managed type, read-only)
  - Remote Tag Providers for external Gateway connections

#### Designer/Client Level (Consumer-Side)
- Tags are imported and accessed within Designer for use in screens and views
- Drag-and-drop binding to components
- Tag subscriptions pull real-time data from Gateway

### Performance Characteristics
- **Gateway Capacity**: Support for many thousands of value changes per second
- **Tag Scale**: Millions of tags manageable in a single system
- **Runtime Efficiency**: Lightweight subscription architecture improves efficiency
- **Distributed Execution**: Remote providers handle PLC writes, alarms, and historical storage on their source Gateway

---

## 2. Tag Types

### Standard Tag Types

#### Memory Tags
- **Purpose**: Internal data storage without external device connection
- **Value Source**: User-defined or configured default values
- **Data Types**: Supports all Ignition data types
- **Persistence Options**:
  - **None**: Reverts to configuration value on Gateway restart
  - **Database**: Persists to local SQLite database
  - **Configuration**: Value survives tag edits and restarts
- **Use Case**: Temporary variables, system state, calculations, workflow status

#### OPC Tags
- **Purpose**: Real-time data from external devices via OPC UA or legacy OPC
- **Data Source**: Device-specific addressing (Modbus, ControlLogix, Siemens, etc.)
- **Item Path**: Device-specific syntax for addressing points
- **Bit-Level Addressing**: Individual bits addressable with syntax:
  - Micrologix: `[device]N7:1/0`
  - ControlLogix: `[device]Folder/Tag.0`
  - Siemens: `[device]I0.0`
- **Configuration**: Created via Connected Devices window or manual tag creation
- **Character Restrictions**: Invalid chars `! @ # $ ^ & * + [ ]` replaced with underscores

#### Expression Tags
- **Purpose**: Dynamic values calculated from expressions and other tags
- **Evaluation**: Recalculates when input tag values change or on schedule
- **Binding**: Supports tag binding and expression functions
- **Use Case**: Derived calculations, conditional logic, unit conversion

#### Query Tags
- **Purpose**: Values retrieved from SQL database queries
- **Execution**: Query runs on schedule (periodic mode)
- **Data Source**: Any configured database connection
- **Result Binding**: Binds query result to tag value
- **Use Case**: Database-driven data, batch lookups, aggregations

#### Reference Tags
- **Purpose**: Aliases to other tags within the system
- **Redirection**: Point to another tag's value without duplication
- **Use Case**: Simplify navigation, organize by context, reduce storage

#### Derived Tags
- **Purpose**: Tags derived from other tags with custom processing
- **Calculation**: User-defined logic applied to source values
- **Use Case**: Advanced transformations, filtering, conditional derivation

---

## 3. Tag Configuration Properties

### Basic Properties
- **Name**: 
  - Max 256 characters
  - Valid characters: letters, digits, underscores, spaces, parentheses, quotes, dashes, colons
  - First character: letter, number, or underscore
  - Invalid for OPC tags: `! @ # $ ^ & * + [ ]` (replaced with underscores)

- **Tag Group**: Determines execution rate and evaluation conditions
- **Enabled**: Boolean flag enabling/disabling tag evaluation and updates

### Value Properties
- **Value Source**: Selection determines tag type (Memory, OPC, Expression, Query, Derived, Reference)
- **Data Type**: Integer, Float, String, Boolean, DateTime, Dataset, etc.
- **Default Value**: Initial value for Memory tags (persists based on value persistence setting)
- **Current Value**: Read/write runtime value (write access controlled by permissions)

### Numeric Properties (Scaling & Conversion)
- **Scale Mode**: 
  - Off
  - Linear: `scaled = (raw - raw_min) / (raw_max - raw_min) * (scaled_max - scaled_min) + scaled_min`
  - Square Root
  - Exponential Filter
  - Bit Inversion

- **Raw Value Range**: Min and max values from device
- **Scaled Value Range**: Min and max engineering units
- **Clamp Mode**: Behavior for out-of-range values (clip, scaled, raw)
- **Deadband**: Prevents updates from minor value fluctuations
  - **Deadband Mode**: Absolute, Percent, or Off
  - **Deadband Style** (History): Auto, Analog, or Discrete

- **Engineering Units**: Display string (e.g., "°C", "PSI", "RPM")
- **Engineering Limits**: Expected min/max operational values
- **Format String**: Number display formatting (e.g., "0.00")

### Security Properties
- **Read Permissions**: Security levels required to read tag value
  - Defined as comma-separated paths or security level references
- **Write Permissions**: Security levels required to write tag value
- **Tag Edit Permissions**: Security levels required to modify tag configuration
- **Read Only**: Boolean override preventing all write operations
- **Permission Type**: Evaluation logic
  - **AnyOf**: Single matching security level sufficient
  - **AllOf**: All listed security levels required

### History Properties

**Verified against real bytecode string constants** (Ignition 8.3.7, `lib\core\common\common.jar` → `com/inductiveautomation/ignition/common/tags/config/properties/TagHistoryProps.class`) — these are the actual flat, top-level JSON keys on a tag object (siblings of `dataType`/`alarms`/`expression`, **not** nested under a `"history": {...}` sub-object):

| UI Label | Real JSON key | Type | Notes |
|---|---|---|---|
| History Enabled | `historyEnabled` | Boolean | default `true` |
| Storage Provider | `historyProvider` | String | **not** `storageProvider` — common guess, wrong |
| Sample Mode | `sampleMode` | enum `SampleMode` | `OnChange` / `Periodic` / `TagGroup`, default `OnChange`. **Must be set to `Periodic` for `historySampleRate` to take effect** — leaving it at the `OnChange` default silently ignores the rate field |
| Sample Rate | `historySampleRate` | Integer | unit-less number |
| Sample Rate Units | `historySampleRateUnits` | enum `TimeUnits` | `MS` / `SEC` / `MIN` / `HOUR` / `DAY` / `WEEK` / `MONTH` / `YEAR` — short codes, not full words like `SECONDS` |
| Deadband value | `historicalDeadband` | Double | |
| Deadband Mode | `historicalDeadbandMode` | enum `DeadbandMode` | `Absolute` / `Percent` / `Off`, default `Absolute` |
| Deadband Style | `historicalDeadbandStyle` | enum `InterpolationMode` | `Auto` / `Analog` / `Analog_Deadband` / `Analog_Compressed` / `Discrete`, default `Auto` |
| Historical Tag Group | `historyTagGroup` | String | used when `sampleMode: "TagGroup"`, default `"Default Historical"` |
| Max Time Between Samples | `historyMaxAge` + `historyMaxAgeUnits` | Integer + `TimeUnits` | units default `HOUR` |
| Min Time Between Samples | `historyTimeDeadband` + `historyTimeDeadbandUnits` | numeric + `TimeUnits` | |
| (undocumented in UI) | `includeMetadata` | Boolean | exists as a real property, purpose not confirmed |

Gotcha confirmed live in `AHU_Control_Demo`: setting `historyEnabled`/`historySampleRate`/`historySampleRateUnits` via `system.tag.configure` without also setting `sampleMode: "Periodic"` has no effect — the tag keeps logging on every value change under the `OnChange` default, silently ignoring the configured rate.

### Runtime Properties (Read-Only)
- **CanRead**: Boolean reflecting current security context read capability
- **CanWrite**: Boolean reflecting current security context write capability
- **Quality**: Current tag quality status (see Quality Codes section)

### Advanced Properties
- **Custom Properties**: User-defined key-value attributes
  - Accessible in scripts and bindings
  - Inherited by UDT instances

---

## 4. Tag Quality & Status

### Quality Indicators
Tags include quality metadata indicating data validity and source status:

- **Quality Code**: Numeric value indicating tag state
  - Good: Data is current and reliable
  - Unknown: Initial state or source status unknown
  - Bad: Data unreliable or source disconnected
  - Stale: Data hasn't updated within expected timeframe

### Quality Drivers
- **OPC Quality**: Inherited from external device via OPC connection
- **Expression Evaluation**: Quality reflects dependency tags
- **Query Execution**: Quality reflects database availability
- **Alarms**: Can overlay custom quality states
- **Stale Detection**: Quality degrades if update interval exceeds configured threshold

### Tag Event Scripts
Quality changes trigger event handlers:

```
onQualityChange(tag, quality):
  # Execute custom logic when quality changes
  # Log quality degradation
  # Trigger alerts
  # Update dependent tags
```

### Visual Indicators in Tag Browser
Icons displayed next to tag names indicate:
- Scaling mode configured
- Alarms configured
- Historical logging enabled
- Event scripts assigned
- Security permissions set
- UDT inheritance
- Property overrides

---

## 5. Tag Path Conventions

### Hierarchical Organization
Tags are organized in a tree structure using folders:

```
[ProviderName]/FolderName/Subfolder/TagName
```

### Naming Rules
- **Path Separator**: Forward slash `/`
- **Valid Characters**: Letters, digits, underscores, spaces, dashes, colons, parentheses, quotes
- **Invalid First Character**: Special characters (except underscore/letter/digit)
- **Reserved Characters in OPC**: `! @ # $ ^ & * + [ ]` (converted to underscores)
- **Max Name Length**: 256 characters per component

### Path Examples
```
Processes/Tank_A/Temperature
Devices/PLC_Main/Motor_Speed
System/Counters/ProductCount
Reports/Daily/Timestamp
```

### Provider Naming
- Multiple providers allowed per Gateway
- Default provider: `default`
- System provider: `_system_` (managed, read-only)
- Custom naming: User-defined identifiers
- Best Practice: Avoid naming providers identically to database connections (prevents query failures)

### Folder Organization Best Practices
- **By Area**: Organize by physical location or production line
- **By Device**: Group tags from same PLC or sensor network
- **By Process**: Organize by manufacturing/control process
- **By Function**: Group by data type (measurement, setpoint, alarm)
- **Hierarchical Depth**: Balance between organization clarity and navigation overhead

---

## 6. Tag Browser Usage

### Overview
The Tag Browser is the central hub for all tag management in Designer, accessible from the left panel.

### Core Features

#### Tree Navigation
- Expandable/collapsible folder structure
- View nested tags and properties
- Tooltips display configured tag descriptions on hover
- Search highlighting for located tags

#### Toolbar Operations
1. **Add Tag/Folder**: Create new tags, folders, UDT instances, or definitions
2. **Browse Devices**: Connect to external OPC servers or PLC devices
3. **Find/Replace**: Search tags across system using text matching
4. **Refresh Providers**: Update tag information from all providers
5. **Provider Selector**: Switch between different tag providers

#### Advanced Management
- **Tag Groups Editor**: Configure execution rates and evaluation conditions
- **Import/Export**: Bulk operations using JSON format
- **Column Customization**: Display additional metadata columns
- **Tag Report Tool**: Advanced search by path, quality, type, traits
- **Alarm Metrics**: Toggle visibility of alarm information

#### Right-Click Context Menu
- **Edit Tag**: Open tag editor (standard or raw JSON view)
- **Diagnostics**: View active subscriptions and tag state
- **Rename**: Change tag identifier
- **Delete**: Remove tag (with confirmation)
- **Cut/Copy/Paste**: Bulk tag operations
- **Create UDT Instance**: Instantiate UDT definitions
- **Restart Tag**: Force refresh of value and configuration

### Drag-and-Drop Operations

#### Component Binding
- Drag tags directly onto Designer windows/views
- Automatically creates bound components (labels, numeric displays, gauges)
- Component type selected based on tag data type
- Binding scope: Current window or container

#### Quick Binding
- Drag tag to existing component property
- Updates component binding expression
- Multiple tags can update same component via complex bindings

#### Multi-Select Operations
- Ctrl+Click: Select multiple individual tags
- Shift+Click: Select tag range
- Drag selection to component or folder
- Batch operations (cut, copy, delete)

---

## 7. Real-Time Tag Updates

### Update Mechanisms

#### Subscription Architecture
- **Lightweight Model**: Clients subscribe to tag changes rather than polling
- **Event-Driven**: Updates trigger on value change or schedule
- **Bandwidth Efficient**: Only changed values transmitted
- **Latency**: Minimal delay from source update to client receipt

#### Update Triggers

1. **On Change**: Immediate update when value differs
   - Applies to: Memory, OPC, Expression tags
   - Deadband prevents minor fluctuations from triggering updates

2. **Periodic Sampling**: Updates on fixed schedule
   - Applies to: Query, Expression, OPC tags
   - Sample rate: Configurable in milliseconds to hours
   - Min/max time between samples prevents log spam or stale data

3. **Tag Group Execution**: Groups of tags evaluated together
   - Batch execution improves Gateway efficiency
   - Tag Group defines execution rate
   - Multiple rate profiles can coexist (50ms, 500ms, 1000ms groups)

#### Quality Overlay
- Quality status transmitted with value updates
- Quality changes trigger onQualityChange event scripts
- Historical quality recorded with historical samples

### Performance Optimization

#### Deadband Configuration
- **Absolute Deadband**: Minimum value change to trigger update (e.g., 1.5 units)
- **Percent Deadband**: Change threshold as percentage (e.g., 2% of range)
- **Deadband Mode Off**: Every update sent regardless of change
- **Benefit**: Reduces unnecessary network traffic for slowly-changing values

#### Sample Rate Throttling
- **Sample Rate**: Base execution frequency (50ms to hours)
- **Min Time Between Samples**: Fastest update frequency
- **Max Time Between Samples**: Maximum interval before forced update (prevents stale data)
- **Benefit**: Balances responsiveness with system load

#### Historical Data Handling
- **Backfill Data Acceptance**: Out-of-order historical data stored without affecting real-time processing
- **Stale Data Detection**: Quality degrades if real-time update intervals exceed threshold
- **Dual Timestamp**: Separate system timestamp and source timestamp for distributed systems

### Gateway-Level Performance

#### Concurrent Processing
- Multiple value changes per millisecond supported
- Execution prioritized by tag group rate
- Expression tag dependencies evaluated in proper order
- OPC subscriptions batched to reduce device traffic

#### Remote Provider Execution
- Remote Gateway executes PLC writes (reduces local Gateway load)
- Alarms evaluated at source (distributed processing)
- Historical storage at source (reduces network bandwidth)
- Local Gateway caches frequently-accessed values

#### System Tag Provider
- Automatic monitoring of Gateway health metrics
- CPU load, memory usage, message queue depth
- Connection status for devices and databases
- Available for real-time dashboards without custom polling

---

## 8. Tag Providers Configuration

### Provider Types

#### Standard Tag Provider
- **Scope**: Local Gateway management and execution
- **Storage**: Local SQLite database (default provider)
- **Features**: Full read/write capability, unlimited custom instances
- **Exposure**: Optionally shared to other Gateways via OPC UA
- **Scaling**: Supports millions of tags

#### Remote Tag Provider
- **Scope**: External Gateway tag connections
- **Execution**: Remote Gateway handles all operations
- **Permissions**: Read-only by default under Default Security Zone
- **Latency**: Network latency applies to all operations
- **Use Case**: Federated architectures, multi-facility systems

#### System Tag Provider
- **Type**: Managed (read-only, cannot be modified)
- **Scope**: System status and health information
- **Feature Toggle**: "Allow Back-fill Data" for out-of-order acceptance
- **Content**: Gateway metrics, connection status, performance indicators

### Provider Configuration

#### Security Controls (Three Dimensions)
1. **Read Permissions**: Who can view tag values
   - Comma-separated security level paths
   - AND/OR logic evaluation options
   - Default: Unrestricted

2. **Write Permissions**: Who can modify tag values
   - Granular control per tag
   - Can be more restrictive than read
   - Default: Unrestricted

3. **Edit Permissions**: Who can modify tag configuration
   - Prevent accidental/malicious tag edits
   - Separate from read/write value access
   - Default: Administrator-only

#### Value Persistence (Memory Tags Only)
- **None**: Default value loaded on restart, no persistent storage
- **Database**: SQLite persistence (survives tag edits, restarts, crashes)
- **Configuration**: Value stored in configuration, loaded on restart

#### Back-fill Data Setting
- **Enabled**: Accept out-of-order historical data
- **Behavior**: Stored in historian without blocking real-time updates
- **Use Case**: Distributed systems with variable latency, multi-gateway synchronization

---

## Tag Path Examples and Best Practices

### Recommended Folder Hierarchy

```
[Provider]
├── Devices/
│   ├── PLC_Main/
│   │   ├── Motor_Speed
│   │   ├── Pressure_Setpoint
│   │   └── Temperature_Raw
│   ├── PLC_Secondary/
│   └── VFD_Controllers/
├── Processes/
│   ├── Line_A/
│   │   ├── Status
│   │   ├── Production_Count
│   │   └── Cycle_Time
│   └── Line_B/
├── Alarms/
│   ├── Active
│   └── History
├── Reports/
│   ├── Daily_Summary
│   └── Shift_Totals
└── System/
    ├── Timestamps
    └── Configuration
```

### Naming Conventions
- **PLC Tags**: `[Device]_[Variable]` (e.g., `PLC01_MotorSpeed`)
- **Calculated Values**: Descriptive name with units (e.g., `Pressure_PSI_Scaled`)
- **Status Flags**: `Is_[State]` or `[State]_Active` (e.g., `Is_Running`)
- **Setpoints**: `[Variable]_Setpoint` (e.g., `Temperature_Setpoint`)
- **Counters**: `[Item]_Count` (e.g., `ProductCount_Total`)

---

## Common Tag Configuration Scenarios

### Real-Time Production Monitoring
```
Tag Type: OPC
Value Source: PLC connection
Scale Mode: Linear (raw 0-4095 → 0-100 units)
Deadband: 0.5 (prevent minor noise)
Sample Rate: 100ms
History: Enabled (Periodic, 1s rate)
Quality: Inherited from OPC source
```

### Calculated KPI
```
Tag Type: Expression
Expression: totalProduced / totalCycles
Dependencies: Tag bindings to counters
Sample Rate: Tag Group (1000ms)
Quality: Good if all dependencies good
History: Enabled (OnChange)
```

### Setpoint Storage
```
Tag Type: Memory
Data Type: Float
Default Value: 50.0
Persistence: Database
Write Permissions: Operator level
History: Enabled (OnChange)
Description: "Production line target temperature"
```

### External Database Lookup
```
Tag Type: Query
Query: SELECT value FROM config WHERE id = 'shift_start'
Database Connection: Production_DB
Sample Rate: 3600000ms (hourly)
Value Type: DateTime
History: Disabled (slow-changing)
```

---

## Summary Table: Tag Types Comparison

| Feature | Memory | OPC | Expression | Query | Reference | Derived |
|---------|--------|-----|------------|-------|-----------|---------|
| **Real-Time Source** | User Set | Device | Calculated | Database | Another Tag | Custom Logic |
| **Writeable** | Yes | Yes* | No | No | Yes | No |
| **External Data** | No | Yes | No | Yes | No | No |
| **Persistence** | Optional | No | No | No | No | No |
| **Typical Rate** | OnChange | Device | Variable | Periodic | OnChange | Variable |
| **Calculation** | No | No | Yes | Yes | No | Yes |
| **Storage** | Local | None | None | None | Reference | None |

*OPC writeable depends on device permissions

---

## References
- Ignition Documentation: https://docs.inductiveautomation.com/docs/8.3/platform/tags
- Tag Provider Configuration: Gateway Services → Tag Providers
- Tag Browser: Designer → left panel
- Expression Language: Ignition Expression Reference (available in Designer)

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md)

**Builds toward:** [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md), [85-CLUSTERING-HA-CONFIGURATION](85-CLUSTERING-HA-CONFIGURATION.md)

**Related:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [26-PLATFORM-DATABASE-HISTORIAN](26-PLATFORM-DATABASE-HISTORIAN.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
