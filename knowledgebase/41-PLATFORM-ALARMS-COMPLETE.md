> **Skill level:** 300 · **Read first:** [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 41-PLATFORM-ALARMS-COMPLETE

# Ignition Alarming Platform - Complete Reference
**Ignition 8.3 | Platform Alarms**

---

## 1. Alarm Configuration & Creation

### Tag-Level Configuration
Alarms are configured directly in the **Tag Editor's Alarm settings**. Each tag can have **multiple alarms** with independent properties.

**Configuration Features:**
- Alarm setpoints defined per alarm condition
- Dynamic property assignment (values can be bound or scripted)
- Display Path customization for descriptive messaging (default: tag path)
- Properties captured at event creation time for audit trail

### UDT Template Support
Alarms added to **User-Defined Tags (UDTs)** automatically propagate to all instances—enabling template-based alarm standardization across similar equipment.

### Alarm Mode
Determines how source tag values trigger alarm states:
- Based on setpoint comparison (numeric or state-based)
- Supports multiple simultaneous alarms per tag
- Each alarm maintains distinct configuration

---

## 2. Alarm Types & Priorities

### Four-State Event Model
Alarms use a **two-condition system** creating four possible states:

#### Condition 1: Active/Cleared
- **Active**: Value on source tag meets the setpoint
- **Cleared**: Value no longer meets setpoint condition

#### Condition 2: Acknowledged/Unacknowledged
- **Acknowledged**: User-applied flag indicating handling in progress
- **Unacknowledged**: Default state; waiting for response

### State Combinations
| Active | Acknowledged | State |
|--------|--------------|-------|
| Yes | No | Active & Unacknowledged |
| Yes | Yes | Active & Acknowledged |
| No | No | Cleared & Unacknowledged |
| No | Yes | Cleared & Acknowledged |

### Event Lifecycle
- **No direct transition** from Cleared → Active
- New event is created when condition re-triggers
- Each event maintains separate historical record
- Timestamp and property snapshot captured per event

---

## 3. Escalation Strategies

### Multi-Level Notification Pipeline
Escalation logic is implemented through **Notification Pipelines** with conditional routing:

**Three-Stage Example:**
1. **Initial Route**: On-Call Rosters filter users by active schedules
2. **Timeout Re-Route**: No acknowledgment after N seconds → resend to primary roster
3. **Escalation**: After 3 failed attempts → route to secondary pipeline (supervisor/manager)

### Delivery Channels
- Email
- SMS
- Voice (call)

### Implementation Approach
- Use **Pipelines** for conditional logic
- Leverage **Schedules** (On-Call Rosters) to filter recipients
- Implement timeout handlers to trigger re-routing
- Support multiple escalation levels in single pipeline

### Acknowledgment Timeout
Critical for escalation:
- Timeout duration configurable per alarm
- Triggers if no acknowledgment received
- Can automatically escalate to next notification tier

---

## 4. Notification & Event Handlers

### System Functions

#### Query Alarm Status
```
system.alarm.queryStatus(alarmName=None, state=None, path=None)
```
- Retrieves real-time alarm statuses
- Filter by alarm name, state, or tag path
- Returns active alarm list with current properties

#### Programmatic Acknowledgment
```
system.alarm.acknowledge(eventId, notes=None)
```
- Acknowledges alarm event programmatically
- Optional notes capture acknowledgment reason
- Triggers acknowledgment event in alarm history

### Display Components

#### Alarm Status Table (Vision & Perspective)
- Real-time alarm list display
- Filterable by path, name, or state
- User-interactive acknowledgment buttons
- Binds to `queryStatus()` data

#### Alarm Journal Table (Vision & Perspective)
- Historical alarm event records
- All state transitions displayed
- Associated metadata (timestamp, user, notes)
- Links to external SQL history database

### Event Handler Integration
- Alarms fire events captured in Notification Pipelines
- Pipeline condition logic routes based on state, priority, or custom properties
- Handlers trigger notifications or system actions

---

## 5. Alarm Acknowledgment Workflow

### Multi-Operator Coordination Model
Acknowledgment signals to other operators that an event is being handled.

### Implementation Methods

**1. Component-Based UI**
- Vision Alarm Status Table with built-in acknowledge buttons
- Perspective Alarm Status Table with interactive actions
- One-click acknowledgment from client

**2. Programmatic Acknowledgment**
- Call `system.alarm.acknowledge(eventId)` from scripts
- Useful for automated workflows or integration
- Captures acknowledgment with timestamp

**3. Operator Communication**
- Acknowledgment reflects in real-time views across all clients
- Prevents duplicate work (operator A sees operator B acknowledged)
- Notes field documents acknowledgment reason

### No Automatic Acknowledgment
- Alarms remain unacknowledged by default
- Manual action required (user or script)
- Supports escalation until acknowledged

---

## 6. Alarm History & Analytics

### Alarm Journal Profile
**Gateway Configuration Required**: Create **Alarm Journal Profile** to enable history persistence.

### Captured Data

**Per Event:**
- Source tag path
- Alarm event timestamp
- Event state (Active, Cleared)
- Acknowledgment status and timestamp
- Acknowledgment user and notes
- Associated alarm properties at time of event

**All Status Transitions:**
- Complete audit trail to external SQL database
- Enables historical analysis
- Supports compliance and troubleshooting

### Access Methods

**Vision/Perspective Alarm Journal Table**
- Displays historical records from SQL database
- Filterable by date range, tag, state, user
- Exports available for reporting

**Direct SQL Query**
- Query alarm history table directly
- Custom analytics queries possible
- Integration with BI tools

### Analytics Use Cases
- Alarm frequency analysis (which tags most problematic?)
- MTTR (Mean Time To Repair) calculations
- Operator performance tracking (acknowledgment speed)
- Pattern detection (recurring alarms)
- Compliance documentation

---

## 7. Alarm Performance Considerations

### Gateway-Scoped Processing
- **Alarms are Gateway-scoped**: centralized processing on Ignition Gateway
- Real-time alarm values can be monitored from client applications
- Reduces client-side computation burden

### System Monitoring Tags
**Location**: `Gateway > Alarming` folder

Four system tags track alarm counts by state:
- `AlarmCount_Active_Acknowledged`
- `AlarmCount_Active_Unacknowledged`
- `AlarmCount_Cleared_Acknowledged`
- `AlarmCount_Cleared_Unacknowledged`

**Quick Status Binding**: Simple label bindings show alarm summary without querying database.

### Component Filtering Efficiency

**Supported Filter Syntax:**
- Wildcards: `sensors/*` (all sensors subtree)
- Comma-delimited: `temp,pressure,flow` (specific alarms)
- Dynamic binding: Paths updated at runtime if tag structure changes

**Performance Impact:**
- Filtering reduces data transfer to clients
- Use specific paths when possible
- Avoid excessive wildcard patterns

### Shelving for Maintenance
```
system.alarm.shelve(path, duration=seconds, note=string)
```

**Purpose**: Temporarily ignore alarms during maintenance windows

**Behavior:**
- Suppresses alarm notifications
- Does not create alarm events
- Automatic unshelving after duration
- Maintains audit trail

**Use Cases:**
- Equipment downtime
- System maintenance
- False alarm suppression (known issues)

### Optimization Best Practices

1. **Use Alarm Status Tables** instead of custom querying—optimized components
2. **Archive Alarm Journal regularly**—prevents database bloat
3. **Filter appropriately**—specific paths > wildcard patterns
4. **Monitor Gateway CPU/Memory**—large numbers of alarms impact gateway performance
5. **Use Shelving wisely**—prevent notification spam during known issues
6. **Batch query calls**—avoid repeated `queryStatus()` calls in loops
7. **Implement notification rate limiting**—prevent alert fatigue

---

## Summary Reference

| Aspect | Key Point |
|--------|-----------|
| **Creation** | Configure in Tag Editor; propagate via UDTs |
| **States** | 4-state model (Active/Cleared × Acknowledged/Unacknowledged) |
| **Escalation** | Multi-tier pipelines with timeout-based routing |
| **Notification** | Email, SMS, Voice via Notification Pipelines |
| **Acknowledgment** | Manual via UI or programmatic via system.alarm.acknowledge() |
| **History** | SQL journal with complete audit trail |
| **Performance** | Gateway-scoped; optimize with filtering & shelving |

---

**Last Updated**: 2026-07-13  
**Source**: docs.inductiveautomation.com/docs/8.3/platform/alarming  
**Ignition Version**: 8.3+

---

## See Also

**Prerequisites:** [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md)

**Builds toward:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [93-MOBILE-MODULE-OPERATIONS](93-MOBILE-MODULE-OPERATIONS.md)

**Related:** [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [51-PLATFORM-SECURITY-COMPLETE](51-PLATFORM-SECURITY-COMPLETE.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
