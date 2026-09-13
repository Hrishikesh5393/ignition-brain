---
title: Ignition Expression Language
description: Expression syntax, operators, functions
---

> **Skill level:** 100 · **Read first:** [21-BINDINGS](21-BINDINGS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 22-EXPRESSIONS

# Expression Language

Expressions for dynamic calculations in bindings, tags, alarms.

## Syntax

**Tag reference:**
```
{[default]TagName}
{[opc]Device/Temp}
```

**Literals:**
```
123 (int)
3.14 (float)
"string"
true, false (bool)
today(), now() (date)
```

## Operators

**Math:**
```
+ - * / %  (add, subtract, multiply, divide, modulo)
pow(base, exp)
sqrt(value)
```

**Compare:**
```
== != < > <= >=
```

**Logic:**
```
&& (AND)
|| (OR)
! (NOT)
```

**Ternary:**
```
condition ? true_value : false_value
{tag} > 100 ? "HIGH" : "LOW"
```

**String:**
```
+ (concatenate)
concat(str1, str2, ...)
len(str)
upper(str), lower(str)
contains(str, substr)
substring(str, start, end)
```

## Functions

**Date/Time:**
```
now() - current date/time
today() - current date (00:00:00)
dateArithmetic(date, number, unit) - add/subtract
hour(date), minute(date), second(date)
dayOfWeek(date)
```

**Math:**
```
round(value, decimals)
floor(value), ceil(value)
abs(value)
min(v1, v2), max(v1, v2)
pow(base, exp), sqrt(value)
```

**Logic:**
```
if(condition, true_val, false_val)
isNull(value)
isBool(value), isInt(value), isFloat(value)
```

**Text:**
```
concat(str1, str2, ...)
len(str)
upper(str), lower(str)
contains(str, substr)
substring(str, start, end)
split(str, delimiter)
```

**Conversion:**
```
toString(value)
toInt(value)
toFloat(value)
toBool(value)
```

## Examples

**Basic:**
```
{[default]Temperature} * 1.8 + 32  // C to F
```

**Conditional:**
```
if({[default]Status} == "ON", "Active", "Inactive")
```

**Complex:**
```
{[default]Pressure} > 50 && {[default]Temp} < 80 ? "NORMAL" : "ALARM"
```

**Date:**
```
concat("Today is: ", today())
hour(now()) >= 8 && hour(now()) < 17 ? "Work Hours" : "Off Hours"
```

**Aggregate (in tag expression):**
```
round({[default]Value1} + {[default]Value2} / 2, 2)
```

---
**See:** docs.inductiveautomation.com/docs/8.3/appendix/expressions

---

## See Also

**Prerequisites:** [21-BINDINGS](21-BINDINGS.md)

**Builds toward:** [25a-APPENDIX-EXPRESSIONS-EXTENDED](25a-APPENDIX-EXPRESSIONS-EXTENDED.md), [36-COMPLETE-EXPRESSION-FUNCTIONS](36-COMPLETE-EXPRESSION-FUNCTIONS.md), [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md)

**Related:** [25a-APPENDIX-EXPRESSIONS-EXTENDED](25a-APPENDIX-EXPRESSIONS-EXTENDED.md), [36-COMPLETE-EXPRESSION-FUNCTIONS](36-COMPLETE-EXPRESSION-FUNCTIONS.md), [21-BINDINGS](21-BINDINGS.md), [81-GOTCHAS-BUGS](81-GOTCHAS-BUGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
