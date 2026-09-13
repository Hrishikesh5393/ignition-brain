---
title: Quick Reference - Most Used
description: Copy-paste code snippets for common tasks
---

# Quick Reference

## Read Tag

```python
value = system.tag.read("[default]MyTag").value
```

## Write Tag

```python
system.tag.write("[default]MyTag", 42)
```

## Read Multiple Tags

```python
results = system.tag.readAll(["[default]Tag1", "[default]Tag2"])
values = [r.value for r in results]
```

## Tag Binding (Component)

```javascript
{tag: "[default]MyTag"}
{expr: "{[default]Temp} > 80 ? 'HOT' : 'COOL'"}
```

## Database Query

```python
result = system.db.runPreparedQuery(
    "SELECT * FROM table WHERE id = ?",
    [user_id]
)
```

## Database Insert

```python
system.db.runUpdateQuery(
    "INSERT INTO table (name, value) VALUES (?, ?)",
    ["John", 100]
)
```

## Send Email

```python
system.net.sendEmail(
    smtp="mail.example.com",
    port=25,
    fromAddr="ignition@example.com",
    toAddrs=["user@example.com"],
    subject="Alert",
    body="Something happened"
)
```

## HTTP GET

```python
response = system.net.httpGet("https://api.example.com/data")
```

## HTTP POST

```python
response = system.net.httpPost(
    "https://api.example.com/data",
    {"key": "value"}
)
```

## Log Message

```python
logger = system.util.getLogger("MyScript")
logger.info("Message")
logger.error("Error occurred")
```

## Date Operations

```python
now = system.date.now()
yesterday = system.date.addDays(now, -1)
formatted = system.date.format(now, "yyyy-MM-dd HH:mm:ss")
```

## Send Message (Perspective)

```python
system.perspective.sendMessage("msgName", {"data": 123})
```

## Get Current User

```python
user = system.user.getUser()
username = user.name
roles = user.roles
```

## Acknowledge Alarm

```python
system.alarm.acknowledge([alarmId], "Acknowledged by user")
```

## Component Event Handler

```python
# In component onChange event:
value = self.props.value
parent = self.parent
sibling = self.parent.getChild("other")
```

## Thread Pool (Async)

```python
def slow_operation():
    # Long operation here
    pass

system.util.threadPool.execute(slow_operation)
```

---
**Tag Path Format:** `[provider]folder/subfolder/tagName`
- `[default]` - standard, expression, memory tags
- `[opc]` - OPC-UA device tags
- `[sql]` - SQL query tags

**Expressions:** `{[default]MyTag}` in binding = tag reference
