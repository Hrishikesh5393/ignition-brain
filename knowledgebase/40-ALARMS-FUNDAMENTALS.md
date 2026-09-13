---
title: Alarms
description: Alarm creation, escalation, acknowledgment, journaling
---

> **Skill level:** 100 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [22-EXPRESSIONS](22-EXPRESSIONS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 40-ALARMS-FUNDAMENTALS

# Alarms

Tag-based alerts. Trigger when expression true, escalate on priority.

## Alarm Definition

Create alarm on tag or event:

**Properties:**
- **Name** - Alarm identifier
- **Enabled** - On/off
- **Expression** - When to trigger (`{tag} > 100`)
- **Priority** - Low, Medium, High, Critical
- **Delay** - Seconds before alarm fires (prevent flicker)
- **Duration** - Auto-clear after X seconds (or manual ack)
- **Message** - Description displayed to user

## Alarm States

| State | Meaning |
|-------|---------|
| **Active** | Expression true, not yet acknowledged |
| **Acknowledged** | Active but user clicked "ack" |
| **Cleared** | Expression false (back to normal) |
| **Shelved** | Temporarily suppressed |

## Escalation

**Path:**
1. Alarm active
2. Auto-escalate to higher priority if expression stays true
3. Trigger notifications (email, SMS, etc.)
4. Show in alarm table
5. User acknowledges or expires

**Config:**
- Escalation delay (minutes until step 2)
- Escalation priority (bump to Critical after 5 min)
- Escalation action (send email, call script)

## Alarm Events

Alarm can trigger scripts when:
- **Active** - Alarm first fires
- **Escalate** - Alarm escalates
- **Clear** - Expression becomes false
- **Acknowledge** - User clicks ack button

```python
# In Alarm Active event:
# Escalate to higher priority after 5 min
system.alarm.query(...escalate logic...)
```

## Alarm Acknowledgment

**Manual (UI):**
User clicks "Acknowledge" in alarm table or popup.

**Programmatic:**
```python
system.alarm.acknowledge(alarmId, notes="Maintenance in progress")
```

## Alarm Table Component

**Perspective component displays active/cleared alarms.**

**Config:**
- Filter by priority, source, state
- Show columns: time, message, priority, status
- Double-click to see details
- Right-click to acknowledge

```javascript
// Bind alarm table data:
// Defaults to all alarms, filter in expression if needed
```

## Alarm Journal

**Persistent log of all alarm events.**

Query programmatically:
```python
# Get alarm history
alarms = system.alarm.journal(
    filters={"priority": "High"},
    limit=100  # last 100 events
)
```

**Used for:**
- Compliance (audit trail)
- Trending (frequency analysis)
- Historical review

## Notification

Alarms can notify via:
- **Email** - SMTP configured on gateway
- **SMS/Twilio** - Optional module
- **Webhook** - POST to external system
- **Script** - Custom logic in alarm event handler

**Config in alarm event:**
```python
system.net.sendEmail(
    smtp="mail.company.com",
    port=25,
    fromAddr="ignition@company.com",
    toAddrs=["ops@company.com"],
    subject="ALARM: High Temperature",
    body=f"Temperature reached {value} C"
)
```

## Common Patterns

**High-Temp Alarm:**
```
Expression: {[default]Temperature} > 80
Priority: High
Message: "Temperature exceeds safe limit"
Escalation: After 5 min, escalate to Critical + email ops
```

**Equipment Offline:**
```
Expression: {[opc]Device/Status} == "DISCONNECTED"
Priority: Critical
Message: "Device not responding"
Duration: None (manual ack required)
```

**Production Count Goal:**
```
Expression: {[default]DailyOutput} < {[default]Target}
Priority: Medium
Message: "Below daily target"
Active Event: Alert supervisor
```

---
**See:** [[41-PLATFORM-ALARMS-COMPLETE]]

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [22-EXPRESSIONS](22-EXPRESSIONS.md)

**Builds toward:** [41-PLATFORM-ALARMS-COMPLETE](41-PLATFORM-ALARMS-COMPLETE.md)

**Related:** [41-PLATFORM-ALARMS-COMPLETE](41-PLATFORM-ALARMS-COMPLETE.md), [50-SECURITY-MODEL](50-SECURITY-MODEL.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [62-LOGGING-DIAGNOSTICS](62-LOGGING-DIAGNOSTICS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
