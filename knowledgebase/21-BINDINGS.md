---
title: Bindings - Property Updates
description: Dynamic tag/expression bindings to component properties
---

> **Skill level:** 100 · **Read first:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 21-BINDINGS

# Bindings

Link component property to tag or expression. Updates automatically when source changes.

## Types

### Tag Binding
```javascript
{tag: "[default]MyTag"}
```
Reads tag value continuously. Updates component when tag changes.

### Expression Binding
```javascript
{expr: "{[default]Tag1} + {[default]Tag2}"}
{expr: "if({[default]Status} == 'ON', 'Active', 'Inactive')"}
{expr: "now()"}  // current time
{expr: "{tag1} * 9/5 + 32"}  // C to F conversion
```

### Script Binding
```python
# In binding script context
if {[default]Temperature} > 80:
    return "HOT"
else:
    return "COLD"
```

### Keyframe Animation
Animated property change over time.

## Common Props to Bind

| Component | Property | Bind To |
|-----------|----------|---------|
| Label | text | tag/expression |
| Progress Bar | value | tag |
| Checkbox | value | bool tag |
| Input | value | editable tag |
| Image | source | URL tag/expression |
| Container | visible | condition expression |
| Indicator | color | status tag |

## Expression Syntax

**Tags in expressions:**
```
{[default]TagName}
{[opc]Device/Temperature}
{[sql]Query/Result}
```

**Operators:**
```
+ - * / %  (math)
> < >= <= == !=  (compare)
&& || !  (logic)
? :  (ternary: condition ? true_val : false_val)
```

**Functions:**
```
if(cond, true_val, false_val)
concat(str1, str2, ...)
len(string)
upper(string), lower(string)
contains(string, substring)
now(), today()
hour(), minute(), second() (from date)
round(number, decimals)
max(v1, v2), min(v1, v2)
```

## Event Handlers (Scripts)

Runs on component event (click, change, focus, etc.)

```python
# In onClick event handler:
system.tag.write("[default]Counter", {[default]Counter} + 1)

# In onChange event handler:
if self.props.value > 100:
    system.perspective.sendMessage("alert", {"msg": "Over limit"})

# In custom script:
logger = system.util.getLogger("MyScript")
logger.info(f"User clicked: {self.props.value}")
```

**self** = current component reference
- `self.props` - read/modify properties
- `self.parent` - parent component
- `self.parent.getChild("childName")` - sibling access

## Binding Priority

When multiple bindings compete on same property:
1. Script binding (highest - overwrites)
2. Expression binding
3. Tag binding
4. Manual prop value (lowest)

---
**Common Mistakes:**
- Forgetting tag provider: `{MyTag}` → `{[default]MyTag}`
- Case sensitivity: `{mytag}` ≠ `{MyTag}`
- Circular: Tag1 = Tag2 + 1, Tag2 = Tag1 → loop
- Missing braces: `expr: Tag1 + Tag2` → should be `{[default]Tag1} + {[default]Tag2}`

---

## See Also

**Prerequisites:** [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

**Builds toward:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [22-EXPRESSIONS](22-EXPRESSIONS.md), [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md)

**Related:** [22-EXPRESSIONS](22-EXPRESSIONS.md), [20-TAGS-FUNDAMENTALS](20-TAGS-FUNDAMENTALS.md), [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
