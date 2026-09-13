> **Skill level:** 200 · **Read first:** [22-EXPRESSIONS](22-EXPRESSIONS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 25a-APPENDIX-EXPRESSIONS-EXTENDED

# Ignition 8.3 Expression Language & Functions - Extended Reference

> **Source**: Ignition 8.3 Official Documentation
> **Last Updated**: Ignition 8.3 Platform Documentation
> **URL**: https://www.docs.inductiveautomation.com/docs/8.3/appendix/expression-functions

---

## Table of Contents

1. [Expression Language Overview](#expression-language-overview)
2. [Operators & Precedence](#operators--precedence)
3. [Literal Values & Type Coercion](#literal-values--type-coercion)
4. [Expression Functions by Category](#expression-functions-by-category)
5. [Common Expression Examples](#common-expression-examples)

---

## Expression Language Overview

The expression language is used to define dynamic values for component properties and expression tags in Ignition. Expressions support:

- **Arithmetic operations**: Mathematical calculations
- **String operations**: Text manipulation and concatenation
- **Logical operations**: Conditional evaluations (AND, OR, NOT)
- **Type coercion**: Automatic or explicit type conversion
- **Comments**: Using `//` to annotate expressions
- **Conditional logic**: Using `if()` function for ternary-like behavior

**Key Rule**: Expressions are evaluated left-to-right with operator precedence rules applied.

---

## Operators & Precedence

### Arithmetic Operators

| Operator | Operation | Example | Notes |
|----------|-----------|---------|-------|
| `-` | Unary minus or subtraction | `-5` or `10 - 3` | Unary: negates value; Binary: subtracts |
| `^` | Exponentiation (power) | `2 ^ 3` returns `8` | Right-associative |
| `*` | Multiplication | `4 * 5` returns `20` | |
| `/` | Division | `20 / 4` returns `5` | Returns floating point |
| `%` | Modulus (remainder) | `10 % 3` returns `1` | Works with integers |
| `+` | Addition or concatenation | `5 + 3` or `"Hello" + " World"` | Type-dependent; string concatenation when non-numeric |

### Comparison Operators

| Operator | Condition | Example | Returns |
|----------|-----------|---------|---------|
| `=` | Equality | `5 = 5` | `true` |
| `!=` | Not equal | `5 != 3` | `true` |
| `>` | Greater than | `10 > 5` | `true` |
| `<` | Less than | `3 < 10` | `true` |
| `>=` | Greater than or equal | `10 >= 10` | `true` |
| `<=` | Less than or equal | `5 <= 10` | `true` |

### Logical Operators

| Operator | Operation | Example | Notes |
|----------|-----------|---------|-------|
| `!` | Logical NOT | `!true` returns `false` | Negates boolean value |
| `&&` | Logical AND | `true && false` returns `false` | Short-circuit evaluation |
| `\|\|` | Logical OR | `true \|\| false` returns `true` | Short-circuit evaluation |

**Type Coercion in Logic**: Anything non-zero is considered `true`; zero and `null` are `false`.

### Bitwise Operators

| Operator | Operation | Example | Notes |
|----------|-----------|---------|-------|
| `&` | Bitwise AND | `5 & 3` returns `1` | Binary: `101 & 011 = 001` |
| `\|` | Bitwise OR | `5 \| 3` returns `7` | Binary: `101 \| 011 = 111` |
| `xor` | Bitwise XOR | `5 xor 3` returns `6` | Binary: `101 xor 011 = 110` |
| `~` | Bitwise NOT | `~5` returns `-6` | Two's complement |
| `<<` | Left shift | `5 << 1` returns `10` | Shifts bits left, fills with 0 |
| `>>` | Right shift | `10 >> 1` returns `5` | Shifts bits right |

### Special Operators

| Operator | Purpose | Example | Notes |
|----------|---------|---------|-------|
| `like` | Fuzzy string matching | `"hello" like "h*o"` | Wildcards: `%`, `*`, `?` |
| `//` | Comment | `value // this is a comment` | Remainder of line ignored |

### Operator Precedence (Highest to Lowest)

1. **Parentheses**: `()`
2. **Unary NOT & Negation**: `!`, `-`
3. **Exponentiation**: `^`
4. **Multiplicative**: `*`, `/`, `%`
5. **Additive**: `+`, `-`
6. **Bitwise Shifts**: `<<`, `>>`
7. **Relational**: `<`, `>`, `<=`, `>=`
8. **Equality**: `=`, `!=`
9. **Bitwise AND**: `&`
10. **Bitwise XOR**: `xor`
11. **Bitwise OR**: `|`
12. **Logical AND**: `&&`
13. **Logical OR**: `||`

**Note**: Use parentheses to override precedence: `2 + 3 * 4` equals `14`, but `(2 + 3) * 4` equals `20`.

---

## Literal Values & Type Coercion

### Literal Value Types

| Type | Format | Examples | Notes |
|------|--------|----------|-------|
| **Integer** | Decimal or hex | `42`, `0xFF`, `0x10` | Standard integer literal |
| **Float** | Decimal with point | `3.14`, `2.5e-3` | Supports scientific notation |
| **String** | Single or double quotes | `'hello'`, `"world"` | Escape sequences: `\n`, `\t`, `\\`, `\"`, `\'` |
| **Boolean** | Case-insensitive | `True`, `False`, `true`, `false` | Any case accepted |
| **Null** | Lowercase or capitalized | `null`, `None`, `none` | All three forms valid |

### Type Coercion Rules

- **Addition (`+`)**: 
  - Numbers: arithmetic addition
  - Strings or mixed: string concatenation
  - Example: `5 + 3` → `8`, but `"value: " + 5` → `"value: 5"`

- **String Conversion**: Use `toString()` or `toStr()` to explicitly convert any type to string

- **Comparison**: Values are compared with type consideration; `5 = "5"` may coerce types depending on context

- **Logical Operations**: Non-zero values are `true`; zero and `null` are `false`

---

## Expression Functions by Category

### Math Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `abs` | `abs(number)` | Absolute value | `abs(-5)` → `5` |
| `ceil` | `ceil(number)` | Smallest integer ≥ argument | `ceil(3.2)` → `4` |
| `floor` | `floor(number)` | Largest integer ≤ argument | `floor(3.8)` → `3` |
| `round` | `round(number)` | Round to nearest integer | `round(3.5)` → `4` |
| `pow` | `pow(base, exponent)` | Base raised to power | `pow(2, 3)` → `8` |
| `sqrt` | `sqrt(number)` | Square root | `sqrt(16)` → `4` |
| `exp` | `exp(number)` | e raised to power | `exp(1)` → `2.718...` |
| `log` | `log(number)` | Natural logarithm (base e) | `log(2.718)` → `1` |
| `log10` | `log10(number)` | Logarithm base 10 | `log10(100)` → `2` |
| `sin` | `sin(number)` | Sine (radians) | `sin(0)` → `0` |
| `cos` | `cos(number)` | Cosine (radians) | `cos(0)` → `1` |
| `tan` | `tan(number)` | Tangent (radians) | `tan(0)` → `0` |
| `asin` | `asin(number)` | Arc sine | `asin(1)` → `1.5708...` |
| `acos` | `acos(number)` | Arc cosine | `acos(1)` → `0` |
| `atan` | `atan(number)` | Arc tangent | `atan(1)` → `0.7854...` |
| `toradians` | `toradians(degrees)` | Degrees to radians | `toradians(180)` → `3.14159...` |
| `todegrees` | `todegrees(radians)` | Radians to degrees | `todegrees(3.14159)` → `180` |

### String Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `concat` | `concat(str1, str2, ...)` | Concatenate strings | `concat("Hello", " ", "World")` → `"Hello World"` |
| `len` | `len(string or dataset)` | String length or dataset row count | `len("hello")` → `5` |
| `lower` | `lower(string)` | Convert to lowercase | `lower("HELLO")` → `"hello"` |
| `upper` | `upper(string)` | Convert to uppercase | `upper("hello")` → `"HELLO"` |
| `trim` | `trim(string)` | Remove leading/trailing whitespace | `trim("  hello  ")` → `"hello"` |
| `left` | `left(string, count)` | First N characters | `left("hello", 3)` → `"hel"` |
| `right` | `right(string, count)` | Last N characters | `right("hello", 2)` → `"lo"` |
| `substring` | `substring(string, startIdx, endIdx)` | Extract substring | `substring("hello", 1, 4)` → `"ell"` |
| `split` | `split(string, delimiter)` | Split into array | `split("a,b,c", ",")` → `["a", "b", "c"]` |
| `replace` | `replace(source, find, replacement)` | Replace all occurrences | `replace("hello", "l", "L")` → `"heLLo"` |
| `indexOf` | `indexOf(string, substring)` | Find first occurrence | `indexOf("hello", "l")` → `2` |
| `lastIndexOf` | `lastIndexOf(string, substring)` | Find last occurrence | `lastIndexOf("hello", "l")` → `3` |
| `repeat` | `repeat(string, count)` | Repeat string N times | `repeat("ab", 3)` → `"ababab"` |
| `char` | `char(unicode_code)` | Unicode code to character | `char(65)` → `"A"` |
| `ordinal` | `ordinal(character)` | Character to Unicode code | `ordinal("A")` → `65` |
| `toHex` | `toHex(integer)` | Integer to hex string | `toHex(255)` → `"FF"` |
| `toBinary` | `toBinary(integer)` | Integer to binary string | `toBinary(5)` → `"101"` |
| `toOctal` | `toOctal(integer)` | Integer to octal string | `toOctal(8)` → `"10"` |
| `fromHex` | `fromHex(hex_string)` | Hex string to integer | `fromHex("FF")` → `255` |
| `fromBinary` | `fromBinary(binary_string)` | Binary string to integer | `fromBinary("101")` → `5` |
| `fromOctal` | `fromOctal(octal_string)` | Octal string to integer | `fromOctal("10")` → `8` |
| `stringFormat` | `stringFormat(format, args...)` | Format string with arguments | `stringFormat("%.2f", 3.14159)` → `"3.14"` |
| `numberFormat` | `numberFormat(number, format)` | Format number as string | `numberFormat(1234.5, "#,###.00")` → `"1,234.50"` |
| `escapeSQL` | `escapeSQL(string)` | Escape SQL special characters | `escapeSQL("O'Brien")` → `"O''Brien"` |
| `escapeXML` | `escapeXML(string)` | Escape XML special characters | `escapeXML("<tag>")` → `"&lt;tag&gt;"` |
| `urlEncode` | `urlEncode(string)` | URL-encode string | `urlEncode("hello world")` → `"hello%20world"` |

### Date and Time Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `now` | `now()` | Current date and time | `now()` → Current timestamp |
| `fromMillis` | `fromMillis(milliseconds)` | Milliseconds since epoch to date | `fromMillis(1609459200000)` → Date object |
| `toMillis` | `toMillis(date)` | Date to milliseconds since epoch | `toMillis(now())` → Long integer |
| `getDate` | `getDate(year, month, day)` | Create date object | `getDate(2024, 1, 15)` → Jan 15, 2024 |
| `dateFormat` | `dateFormat(date, pattern)` | Format date as string | `dateFormat(now(), "yyyy-MM-dd")` → `"2024-01-15"` |
| `dateExtract` | `dateExtract(date, field)` | Extract date component | `dateExtract(now(), "year")` → `2024` |
| `get*` | `get[Year\|Month\|Day\|Hour\|Minute\|Second](date)` | Extract time unit | `getYear(now())` → `2024` |
| `dateArithmetic` | `dateArithmetic(date, amount, unit)` | Add/subtract time | `dateArithmetic(now(), 1, "day")` → Tomorrow |
| `add*` | `add[Years\|Months\|Days\|Hours\|Minutes\|Seconds](date, amount)` | Add time units | `addDays(now(), 7)` → One week from now |
| `dateDiff` | `dateDiff(date1, date2, unit)` | Difference between dates | `dateDiff(now(), futureDate, "hours")` → Hours between |
| `timeBetween` | `timeBetween(time, startTime, endTime)` | Check if time is in range | `timeBetween(now(), "09:00:00", "17:00:00")` → Boolean |
| `dateIsBefore` | `dateIsBefore(date1, date2)` | Is date1 before date2? | `dateIsBefore(now(), futureDate)` → `true` |
| `dateIsAfter` | `dateIsAfter(date1, date2)` | Is date1 after date2? | `dateIsAfter(now(), pastDate)` → `true` |
| `dateIsBetween` | `dateIsBetween(target, start, end)` | Is target between start and end? | `dateIsBetween(now(), startDate, endDate)` → Boolean |
| `midnight` | `midnight(date)` | Set time to 00:00:00 | `midnight(now())` → Today at midnight |
| `setTime` | `setTime(date, hr, min, sec)` | Set time portion | `setTime(now(), 14, 30, 0)` → 2:30 PM today |
| `getTimezone` | `getTimezone()` | Current timezone ID | `getTimezone()` → `"America/New_York"` |
| `getTimezoneOffset` | `getTimezoneOffset(date)` | Timezone offset from UTC (DST-aware) | `getTimezoneOffset(now())` → milliseconds |
| `getTimezoneRawOffset` | `getTimezoneRawOffset()` | Timezone offset from UTC (no DST) | `getTimezoneRawOffset()` → milliseconds |
| `dateIsDaylight` | `dateIsDaylight(date)` | Is daylight saving time active? | `dateIsDaylight(now())` → Boolean |

### Logic Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `if` | `if(condition, trueValue, falseValue)` | Conditional return | `if(temp > 100, "Hot", "Cold")` |
| `case` | `case(value, case1, return1, ..., default)` | Switch-like logic | `case(status, "OK", 1, "ERROR", 2, 0)` |
| `switch` | `switch(value, case1, return1, ..., default)` | Alternative to case | Same as `case()` |
| `coalesce` | `coalesce(value1, value2, ...)` | Return first non-null | `coalesce(null, null, "found")` → `"found"` |
| `try` | `try(expression, default)` | Catch errors | `try(1/0, "error")` → `"error"` |
| `hasChanged` | `hasChanged(value)` | Has value changed since last run? | `hasChanged(tag.value)` → Boolean |
| `binEnc` | `binEnc(bool1, bool2, ...)` | Booleans to binary number | `binEnc(1, 0, 1)` → `5` (binary 101) |
| `binEnum` | `binEnum(bool1, bool2, ...)` | Index of first true value | `binEnum(false, true, false)` → `2` |
| `getBit` | `getBit(number, position)` | Get bit at position | `getBit(5, 0)` → `1` (5 = binary 101) |
| `isNull` | `isNull(value)` | Is value null? | `isNull(null)` → `true` |
| `isGood` | `isGood(value)` | Is quality good? | `isGood(tag)` → `true` if good quality |
| `isBad` | `isBad(value)` | Is quality bad? | `isBad(tag)` → `true` if bad quality |
| `isError` | `isError(value)` | Is error state? | `isError(tag)` → `true` if error |
| `isBadOrError` | `isBadOrError(value)` | Is bad or error? | `isBadOrError(tag)` → Boolean |
| `isUncertain` | `isUncertain(value)` | Is uncertain quality? | `isUncertain(tag)` → Boolean |
| `lookup` | `lookup(dataset, column, searchValue, returnColumn)` | Look up value in dataset | `lookup(tableData, "ID", 5, "Name")` |
| `indexOf` | `indexOf(string, substring)` | First occurrence index | `indexOf("hello", "l")` → `2` |
| `lastIndexOf` | `lastIndexOf(string, substring)` | Last occurrence index | `lastIndexOf("hello", "l")` → `3` |

### Type Casting Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `toString` | `toString(value)` | Convert to string | `toString(42)` → `"42"` |
| `toStr` | `toStr(value)` | Alias for toString | `toStr(3.14)` → `"3.14"` |
| `toInt` | `toInt(value)` | Convert to 32-bit integer | `toInt("42")` → `42` |
| `toInteger` | `toInteger(value)` | Alias for toInt | `toInteger(3.9)` → `3` |
| `toLong` | `toLong(value)` | Convert to 64-bit integer | `toLong("9999999999")` → `9999999999L` |
| `toFloat` | `toFloat(value)` | Convert to 32-bit float | `toFloat("3.14")` → `3.14f` |
| `toDouble` | `toDouble(value)` | Convert to 64-bit float | `toDouble("3.14159")` → `3.14159` |
| `toBoolean` | `toBoolean(value)` | Convert to boolean | `toBoolean(1)` → `true`, `toBoolean(0)` → `false` |
| `toDate` | `toDate(value)` | Convert to date | `toDate("2024-01-15")` → Date object |
| `toColor` | `toColor(value)` | Convert to color | `toColor("#FF0000")` → Red color |
| `toBorder` | `toBorder(value)` | Convert to border | For component binding |
| `toFont` | `toFont(string)` | Convert to font | `toFont("Arial-BOLD-12")` → Font object |
| `toDataSet` | `toDataSet(value)` | Convert to dataset | Coerce value into dataset format |

### Aggregate Functions

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `sum` | `sum(dataset, column)` or `sum(num1, num2, ...)` | Sum of values | `sum(table, "amount")` or `sum(1, 2, 3)` → `6` |
| `mean` | `mean(dataset, column)` or `mean(num1, num2, ...)` | Average/mean | `mean(table, "value")` → Average |
| `median` | `median(dataset, column)` or `median(num1, num2, ...)` | Median value | `median(5, 10, 15)` → `10` |
| `min` | `min(dataset, column)` or `min(num1, num2, ...)` | Minimum value | `min(table, "score")` or `min(5, 2, 8)` → `2` |
| `minDate` | `minDate(dataset, column)` or `minDate(date1, date2, ...)` | Minimum date | `minDate(dates)` → Earliest date |
| `max` | `max(dataset, column)` or `max(num1, num2, ...)` | Maximum value | `max(table, "score")` or `max(5, 2, 8)` → `8` |
| `maxDate` | `maxDate(dataset, column)` or `maxDate(date1, date2, ...)` | Maximum date | `maxDate(dates)` → Latest date |
| `stdDev` | `stdDev(dataset, column)` or `stdDev(num1, num2, ...)` | Standard deviation | `stdDev(table, "data")` → Std dev |
| `groupConcat` | `groupConcat(dataset, column, separator)` | Concatenate with separator | `groupConcat(table, "name", ", ")` → Comma-separated names |

### Aggregate Functions (Dataset Operations)

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `max` | `max(dataset, column)` | Maximum in column | `max(MyDataset, "Temperature")` |
| `min` | `min(dataset, column)` | Minimum in column | `min(MyDataset, "Pressure")` |
| `mean` | `mean(dataset, column)` | Average of column | `mean(MyDataset, "Flow")` |
| `median` | `median(dataset, column)` | Median of column | `median(MyDataset, "Values")` |
| `stdDev` | `stdDev(dataset, column)` | Std deviation of column | `stdDev(MyDataset, "Readings")` |
| `sum` | `sum(dataset, column)` | Sum of column | `sum(MyDataset, "Amount")` |

---

## Common Expression Examples

### Conditional Logic

```javascript
// Simple conditional
if({Sensor/Temperature} > 100, "ALARM", "OK")

// Multi-level conditional
if({Status} = "Running", "Green", 
   if({Status} = "Stopping", "Yellow", "Red"))

// Using case for multiple conditions
case({Mode}, 
  "Heat", "Heating Mode",
  "Cool", "Cooling Mode",
  "Off", "Standby",
  "Unknown Mode")
```

### String Operations

```javascript
// Concatenate multiple values
concat("Current Value: ", {Sensor/Pressure}, " PSI")

// Extract first 5 characters
left({TagName}, 5)

// Replace all underscores with spaces
replace({Label}, "_", " ")

// Format with units
stringFormat("%.2f %s", {Temperature}, "°C")
```

### Math Calculations

```javascript
// Percentage calculation
({Production/Completed} / {Production/Total}) * 100

// Absolute deviation
abs({Setpoint} - {Actual})

// Power calculation (e.g., squared)
pow({Value}, 2)

// Square root
sqrt({AreaValue})

// Logarithmic scale
log10({SignalStrength})
```

### Date and Time Operations

```javascript
// Days since event
dateDiff(now(), {Event/Timestamp}, "days")

// Format current date
dateFormat(now(), "yyyy-MM-dd HH:mm:ss")

// Add days to a date
addDays({StartDate}, 30)

// Check if time is within business hours
timeBetween(now(), "09:00:00", "17:00:00")

// Get day of year
dateExtract(now(), "dayofyear")
```

### Quality and Null Checking

```javascript
// Use value only if good quality
if(isGood({Sensor}), {Sensor}, "No Data")

// Fallback to alternate value if null
coalesce({PrimaryValue}, {BackupValue}, 0)

// Check for errors
if(isBadOrError({Temperature}), "Error", {Temperature})
```

### Dataset Operations

```javascript
// Find maximum value in dataset column
max({DataSource}, "Value")

// Calculate average with fallback
if(len({Results}) > 0, mean({Results}, "Score"), "No Data")

// Look up value in table
lookup({Configuration}, "ParameterName", "Temperature", "DefaultValue")

// Sum all amounts
sum({Transactions}, "Amount")
```

### Type Conversion

```javascript
// String to number
toInt({TextValue}) + 10

// Number to string with formatting
numberFormat(toDouble({Input}), "#,###.00")

// Boolean conversion
toBoolean({BitFlag})

// Date parsing
toDate({DateString})
```

### Complex Multi-Step

```javascript
// Temperature with alarm thresholds and quality check
if(isBad({Sensor/Temp}), "ERROR",
   if({Sensor/Temp} > {Setpoint/High}, "HIGH ALARM",
      if({Sensor/Temp} < {Setpoint/Low}, "LOW ALARM",
         stringFormat("%.1f°C", {Sensor/Temp}))))

// Calculate efficiency percentage with validation
if(and({Production/Total} > 0, isGood({Production/Actual})),
   numberFormat(({Production/Actual} / {Production/Total}) * 100, "##0.00"),
   "N/A")
```

### Bitwise Operations

```javascript
// Extract specific bits
getBit({Flags}, 3)  // Get 4th bit (0-indexed)

// Combine boolean flags into binary
binEnc({Bit0}, {Bit1}, {Bit2}, {Bit3})

// Find first true flag
binEnum({Flag0}, {Flag1}, {Flag2})
```

---

## Expression Best Practices

1. **Use Parentheses**: Clarify intent in complex expressions
2. **Handle Nulls**: Use `coalesce()` or `isNull()` to prevent errors
3. **Check Quality**: Use `isGood()` or `isBad()` for tag values
4. **Format Output**: Use `numberFormat()` or `dateFormat()` for presentation
5. **Keep it Simple**: Complex expressions are harder to debug
6. **Comments**: Use `//` for documentation
7. **Type Safety**: Cast types explicitly when uncertain
8. **Test Edge Cases**: Nulls, zeros, and boundary values

---

## Related Resources

- Ignition 8.3 Documentation: https://www.docs.inductiveautomation.com/docs/8.3/
- Expression Functions: https://www.docs.inductiveautomation.com/docs/8.3/appendix/expression-functions/
- Expression Bindings (Vision): https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/vision/binding-types-in-vision/expression-binding-in-vision/
- Expression Bindings (Perspective): https://www.docs.inductiveautomation.com/docs/8.3/ignition-modules/perspective/working-with-perspective-components/bindings-in-perspective/expression-bindings-in-perspective/

---

## See Also

**Prerequisites:** [22-EXPRESSIONS](22-EXPRESSIONS.md)

**Builds toward:** [36-COMPLETE-EXPRESSION-FUNCTIONS](36-COMPLETE-EXPRESSION-FUNCTIONS.md)

**Related:** [22-EXPRESSIONS](22-EXPRESSIONS.md), [36-COMPLETE-EXPRESSION-FUNCTIONS](36-COMPLETE-EXPRESSION-FUNCTIONS.md), [21-BINDINGS](21-BINDINGS.md), [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
