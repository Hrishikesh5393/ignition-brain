> **Skill level:** 200 · **Read first:** [22-EXPRESSIONS](22-EXPRESSIONS.md), [25a-APPENDIX-EXPRESSIONS-EXTENDED](25a-APPENDIX-EXPRESSIONS-EXTENDED.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 36-COMPLETE-EXPRESSION-FUNCTIONS

# Ignition 8.3 Complete Expression Functions Reference

**Last Updated:** 2026-07-13  
**Ignition Version:** 8.3  
**Total Functions Documented:** 123+

---

## Quick Navigation

- [Math Functions](#math-functions)
- [String Functions](#string-functions)
- [Date/Time Functions](#datetime-functions)
- [Logic Functions](#logic-functions)
- [Type Casting Functions](#type-casting-functions)
- [Aggregate Functions](#aggregate-functions)
- [Advanced Functions](#advanced-functions)
- [Color Functions](#color-functions)
- [Alarming Functions](#alarming-functions)
- [User Functions](#user-functions)
- [Translation Functions](#translation-functions)
- [Identity Provider Functions](#identity-provider-functions)

---

## MATH FUNCTIONS

### abs()
| Property | Value |
|----------|-------|
| **Syntax** | `abs(number)` |
| **Parameters** | `number` - numeric value |
| **Return Type** | Same numeric type as input |
| **Description** | Returns the absolute (positive) value of a number, removing the negative sign if present. |
| **Examples** | `abs(-5)` → `5`<br>`abs(-3.14)` → `3.14`<br>`abs(10)` → `10` |
| **Common Use Cases** | Distance calculations, magnitude operations, error magnitude analysis |
| **When NOT to use** | When sign information is critical to the business logic |
| **Performance Notes** | O(1) - constant time operation |

### acos()
| Property | Value |
|----------|-------|
| **Syntax** | `acos(number)` |
| **Parameters** | `number` - value between -1 and 1 |
| **Return Type** | Double (radians) |
| **Description** | Returns the arc cosine (inverse cosine) of a number in radians. Result is between 0 and π. |
| **Examples** | `acos(1)` → `0.0`<br>`acos(0)` → `1.5707963...` (π/2)<br>`acos(-1)` → `3.1415926...` (π) |
| **Common Use Cases** | Angle calculations in mechanical systems, coordinate transformations, physics simulations |
| **When NOT to use** | When input is outside [-1, 1] range; use error checking first |
| **Performance Notes** | O(1) - trigonometric function lookup |

### asin()
| Property | Value |
|----------|-------|
| **Syntax** | `asin(number)` |
| **Parameters** | `number` - value between -1 and 1 |
| **Return Type** | Double (radians) |
| **Description** | Returns the arc sine (inverse sine) of a number in radians. Result is between -π/2 and π/2. |
| **Examples** | `asin(0)` → `0.0`<br>`asin(1)` → `1.5707963...` (π/2)<br>`asin(-1)` → `-1.5707963...` (-π/2) |
| **Common Use Cases** | Angle calculations, pendulum motion analysis, sensor angle interpretation |
| **When NOT to use** | When input is outside [-1, 1] range without validation |
| **Performance Notes** | O(1) - trigonometric function |

### atan()
| Property | Value |
|----------|-------|
| **Syntax** | `atan(number)` |
| **Parameters** | `number` - any numeric value |
| **Return Type** | Double (radians) |
| **Description** | Returns the arc tangent (inverse tangent) of a number in radians. Result is between -π/2 and π/2. |
| **Examples** | `atan(0)` → `0.0`<br>`atan(1)` → `0.7853981...` (π/4)<br>`atan(-1)` → `-0.7853981...` |
| **Common Use Cases** | Angle calculations, bearing calculations, slope-to-angle conversions |
| **When NOT to use** | For quadrant-specific calculations; use atan2 if available instead |
| **Performance Notes** | O(1) - trigonometric function |

### ceil()
| Property | Value |
|----------|-------|
| **Syntax** | `ceil(number)` |
| **Parameters** | `number` - floating point number |
| **Return Type** | Double |
| **Description** | Returns the smallest integer value that is greater than or equal to the argument (rounds up). |
| **Examples** | `ceil(3.2)` → `4.0`<br>`ceil(3.9)` → `4.0`<br>`ceil(-2.5)` → `-2.0`<br>`ceil(5)` → `5.0` |
| **Common Use Cases** | Capacity planning, unit conversions, batch processing calculations |
| **When NOT to use** | When you need standard rounding behavior; use round() instead |
| **Performance Notes** | O(1) - simple math operation |

### cos()
| Property | Value |
|----------|-------|
| **Syntax** | `cos(number)` |
| **Parameters** | `number` - angle in radians |
| **Return Type** | Double |
| **Description** | Returns the trigonometric cosine of an angle specified in radians. |
| **Examples** | `cos(0)` → `1.0`<br>`cos(π/2)` → `0.0`<br>`cos(π)` → `-1.0` |
| **Common Use Cases** | Waveform analysis, rotating equipment calculations, harmonic analysis |
| **When NOT to use** | When input is in degrees; convert using toRadians() first |
| **Performance Notes** | O(1) - trigonometric function |

### exp()
| Property | Value |
|----------|-------|
| **Syntax** | `exp(number)` |
| **Parameters** | `number` - exponent value |
| **Return Type** | Double |
| **Description** | Returns Euler's number (e ≈ 2.71828) raised to the power of the argument. |
| **Examples** | `exp(0)` → `1.0`<br>`exp(1)` → `2.7182818...`<br>`exp(2)` → `7.3890560...` |
| **Common Use Cases** | Growth calculations, decay analysis, exponential modeling |
| **When NOT to use** | For very large exponents (can cause overflow); check bounds |
| **Performance Notes** | O(1) - may be computationally expensive |

### floor()
| Property | Value |
|----------|-------|
| **Syntax** | `floor(number)` |
| **Parameters** | `number` - floating point number |
| **Return Type** | Double |
| **Description** | Returns the largest integer value that is less than or equal to the argument (rounds down). |
| **Examples** | `floor(3.2)` → `3.0`<br>`floor(3.9)` → `3.0`<br>`floor(-2.5)` → `-3.0`<br>`floor(5)` → `5.0` |
| **Common Use Cases** | Inventory allocation, time calculations, discretization |
| **When NOT to use** | When you need ceiling or standard rounding; use appropriate function |
| **Performance Notes** | O(1) - simple math operation |

### log()
| Property | Value |
|----------|-------|
| **Syntax** | `log(number)` |
| **Parameters** | `number` - positive numeric value |
| **Return Type** | Double |
| **Description** | Returns the natural logarithm (base e) of a number. Input must be positive. |
| **Examples** | `log(1)` → `0.0`<br>`log(2.71828...)` → `1.0`<br>`log(10)` → `2.3025850...` |
| **Common Use Cases** | Signal processing, decibel calculations, exponential decay analysis, rate-of-change analysis |
| **When NOT to use** | With zero or negative values (returns NaN or undefined) |
| **Performance Notes** | O(1) - logarithmic function, moderate computational cost |

### log10()
| Property | Value |
|----------|-------|
| **Syntax** | `log10(number)` |
| **Parameters** | `number` - positive numeric value |
| **Return Type** | Double |
| **Description** | Returns the base-10 logarithm (common logarithm) of a number. Input must be positive. |
| **Examples** | `log10(1)` → `0.0`<br>`log10(10)` → `1.0`<br>`log10(100)` → `2.0`<br>`log10(1000)` → `3.0` |
| **Common Use Cases** | pH calculations, decibel conversions, magnitude scaling, scientific measurements |
| **When NOT to use** | With zero or negative values; for natural logarithm use log() |
| **Performance Notes** | O(1) - moderate computational cost |

### pow()
| Property | Value |
|----------|-------|
| **Syntax** | `pow(base, exponent)` |
| **Parameters** | `base` - numeric value<br>`exponent` - numeric value |
| **Return Type** | Double |
| **Description** | Returns the base raised to the power of exponent. |
| **Examples** | `pow(2, 3)` → `8.0`<br>`pow(10, 2)` → `100.0`<br>`pow(2, 0.5)` → `1.4142135...` (√2) |
| **Common Use Cases** | Scale calculations, quadratic/cubic relationships, physics formulas |
| **When NOT to use** | For very large results that exceed Double range; check bounds |
| **Performance Notes** | O(1) - may be computationally expensive for complex exponents |

### round()
| Property | Value |
|----------|-------|
| **Syntax** | `round(number)` or `round(number, places)` |
| **Parameters** | `number` - floating point number<br>`places` - (optional) decimal places to round to |
| **Return Type** | Long or Double |
| **Description** | Rounds a floating point number to the nearest integer or to a specified number of decimal places. |
| **Examples** | `round(3.2)` → `3`<br>`round(3.7)` → `4`<br>`round(3.14159, 2)` → `3.14`<br>`round(3.5)` → `4` |
| **Common Use Cases** | Display formatting, rounding currency, precision control |
| **When NOT to use** | When truncation is needed; use floor() or int() instead |
| **Performance Notes** | O(1) - simple math operation |

### sin()
| Property | Value |
|----------|-------|
| **Syntax** | `sin(number)` |
| **Parameters** | `number` - angle in radians |
| **Return Type** | Double |
| **Description** | Returns the trigonometric sine of an angle specified in radians. |
| **Examples** | `sin(0)` → `0.0`<br>`sin(π/2)` → `1.0`<br>`sin(π)` → `0.0` |
| **Common Use Cases** | Wave analysis, AC power calculations, harmonic analysis, periodic signal processing |
| **When NOT to use** | When input is in degrees; convert using toRadians() first |
| **Performance Notes** | O(1) - trigonometric function |

### sqrt()
| Property | Value |
|----------|-------|
| **Syntax** | `sqrt(number)` |
| **Parameters** | `number` - non-negative numeric value |
| **Return Type** | Double |
| **Description** | Returns the square root of a number. Only works with non-negative values. |
| **Examples** | `sqrt(4)` → `2.0`<br>`sqrt(9)` → `3.0`<br>`sqrt(2)` → `1.4142135...`<br>`sqrt(0)` → `0.0` |
| **Common Use Cases** | Distance calculations, RMS computations, standard deviation calculations |
| **When NOT to use** | With negative values (returns NaN); validate input first |
| **Performance Notes** | O(1) - moderate computational cost |

### tan()
| Property | Value |
|----------|-------|
| **Syntax** | `tan(number)` |
| **Parameters** | `number` - angle in radians |
| **Return Type** | Double |
| **Description** | Returns the trigonometric tangent of an angle specified in radians. |
| **Examples** | `tan(0)` → `0.0`<br>`tan(π/4)` → `1.0`<br>`tan(π/2)` → `Infinity` |
| **Common Use Cases** | Slope calculations, angle-to-ratio conversions, engineering slope analysis |
| **When NOT to use** | Near π/2 where function approaches infinity; use atan for inverse calculations |
| **Performance Notes** | O(1) - trigonometric function |

### toDegrees()
| Property | Value |
|----------|-------|
| **Syntax** | `toDegrees(radians)` |
| **Parameters** | `radians` - angle value in radians |
| **Return Type** | Double |
| **Description** | Converts an angle measured in radians to degrees. Uses the formula: degrees = radians × (180/π) |
| **Examples** | `toDegrees(0)` → `0.0`<br>`toDegrees(π/2)` → `90.0`<br>`toDegrees(π)` → `180.0`<br>`toDegrees(3.14159)` → `179.999...` |
| **Common Use Cases** | Converting trigonometric results to human-readable degrees, compass bearings, angle displays |
| **When NOT to use** | When working with radians natively; convert only for display |
| **Performance Notes** | O(1) - simple multiplication operation |

### toRadians()
| Property | Value |
|----------|-------|
| **Syntax** | `toRadians(degrees)` |
| **Parameters** | `degrees` - angle value in degrees |
| **Return Type** | Double |
| **Description** | Converts an angle measured in degrees to radians. Uses the formula: radians = degrees × (π/180) |
| **Examples** | `toRadians(0)` → `0.0`<br>`toRadians(90)` → `1.5707963...` (π/2)<br>`toRadians(180)` → `3.1415926...` (π)<br>`toRadians(360)` → `6.2831853...` (2π) |
| **Common Use Cases** | Preparing user input for trigonometric functions, converting sensor angles, bearing calculations |
| **When NOT to use** | When input is already in radians |
| **Performance Notes** | O(1) - simple multiplication operation |

---

## STRING FUNCTIONS

### char()
| Property | Value |
|----------|-------|
| **Syntax** | `char(code)` |
| **Parameters** | `code` - integer Unicode character code (0-65535) |
| **Return Type** | String |
| **Description** | Takes a Unicode character code (as an integer) and returns the corresponding Unicode character as a string. |
| **Examples** | `char(65)` → `"A"`<br>`char(97)` → `"a"`<br>`char(32)` → `" "` (space)<br>`char(9823)` → `"♟"` |
| **Common Use Cases** | Building special characters, Unicode symbol generation, character encoding operations |
| **When NOT to use** | When you need multiple characters; use concat() for building strings |
| **Performance Notes** | O(1) - simple lookup operation |

### concat()
| Property | Value |
|----------|-------|
| **Syntax** | `concat(str1, str2, ...)` |
| **Parameters** | `str1, str2, ...` - any number of string values or expressions |
| **Return Type** | String |
| **Description** | Concatenates all of the strings passed in as arguments together into a single string. |
| **Examples** | `concat("Hello", " ", "World")` → `"Hello World"`<br>`concat("Temp: ", 25, "°C")` → `"Temp: 25°C"`<br>`concat("A", "B", "C", "D")` → `"ABCD"` |
| **Common Use Cases** | Building dynamic labels, message composition, path construction, data formatting |
| **When NOT to use** | Avoid with very large numbers of arguments; use with 2-10 arguments optimally |
| **Performance Notes** | O(n) where n is total character count; efficient for reasonable numbers of arguments |

### escapeSQL()
| Property | Value |
|----------|-------|
| **Syntax** | `escapeSQL(str)` |
| **Parameters** | `str` - string containing potential SQL characters |
| **Return Type** | String |
| **Description** | Returns the given string with special SQL characters escaped to prevent SQL injection attacks. |
| **Examples** | `escapeSQL("O'Reilly")` → `"O\\'Reilly"` or `"O''Reilly"`<br>`escapeSQL('test"value')` → `'test\\"value'` |
| **Common Use Cases** | Sanitizing user input before database queries, preventing SQL injection, building dynamic queries |
| **When NOT to use** | When using parameterized queries (preferred method); don't rely solely on this for security |
| **Performance Notes** | O(n) where n is string length; minimal overhead |

### escapeXML()
| Property | Value |
|----------|-------|
| **Syntax** | `escapeXML(str)` |
| **Parameters** | `str` - string containing potential XML characters |
| **Return Type** | String |
| **Description** | Returns the given string after being escaped to be valid for inclusion in XML documents. |
| **Examples** | `escapeXML("<tag>")` → `"&lt;tag&gt;"`<br>`escapeXML('test&value')` → `'test&amp;value'`<br>`escapeXML('"quoted"')` → `'&quot;quoted&quot;'` |
| **Common Use Cases** | Preparing text for XML export, sanitizing data in XML contexts, SOAP message preparation |
| **When NOT to use** | When data is already properly escaped |
| **Performance Notes** | O(n) where n is string length |

### fromBinary()
| Property | Value |
|----------|-------|
| **Syntax** | `fromBinary(str)` |
| **Parameters** | `str` - string in binary format (e.g., "1010", "11111111") |
| **Return Type** | Integer |
| **Description** | Converts a binary formatted string (e.g., "1010") to its integer value. |
| **Examples** | `fromBinary("1010")` → `10`<br>`fromBinary("11111111")` → `255`<br>`fromBinary("0")` → `0` |
| **Common Use Cases** | Bit pattern analysis, binary data interpretation, embedded system communication |
| **When NOT to use** | When working with large numbers exceeding Integer range |
| **Performance Notes** | O(n) where n is string length |

### fromHex()
| Property | Value |
|----------|-------|
| **Syntax** | `fromHex(str)` |
| **Parameters** | `str` - string in hexadecimal format (e.g., "FF", "1A2B") |
| **Return Type** | Integer |
| **Description** | Converts a hexadecimal formatted string to its integer value. Case-insensitive. |
| **Examples** | `fromHex("FF")` → `255`<br>`fromHex("1A")` → `26`<br>`fromHex("0")` → `0` |
| **Common Use Cases** | Color code parsing, protocol message decoding, device communication |
| **When NOT to use** | When working with very large hex values exceeding Integer range |
| **Performance Notes** | O(n) where n is string length |

### fromOctal()
| Property | Value |
|----------|-------|
| **Syntax** | `fromOctal(str)` |
| **Parameters** | `str` - string in octal format (e.g., "777", "123") |
| **Return Type** | Integer |
| **Description** | Converts an octal formatted string to its integer value. |
| **Examples** | `fromOctal("10")` → `8`<br>`fromOctal("777")` → `511`<br>`fromOctal("0")` → `0` |
| **Common Use Cases** | Unix file permission parsing, octal-encoded data interpretation |
| **When NOT to use** | When numbers are in decimal or other formats |
| **Performance Notes** | O(n) where n is string length |

### left()
| Property | Value |
|----------|-------|
| **Syntax** | `left(str, count)` |
| **Parameters** | `str` - string to extract from<br>`count` - number of characters to extract from the left |
| **Return Type** | String |
| **Description** | Extracts a specified number of characters from the left (start) of a string. |
| **Examples** | `left("Hello", 3)` → `"Hel"`<br>`left("Database", 4)` → `"Data"`<br>`left("ABC", 10)` → `"ABC"` |
| **Common Use Cases** | Extracting prefixes, parsing codes, truncating display text |
| **When NOT to use** | For arbitrary substring extraction; use substring() for more flexibility |
| **Performance Notes** | O(n) where n is count |

### lower()
| Property | Value |
|----------|-------|
| **Syntax** | `lower(str)` |
| **Parameters** | `str` - string to convert |
| **Return Type** | String |
| **Description** | Takes a string and returns a lowercase version of it. Converts all uppercase letters to lowercase. |
| **Examples** | `lower("Hello World")` → `"hello world"`<br>`lower("DATABASE")` → `"database"`<br>`lower("Test123")` → `"test123"` |
| **Common Use Cases** | Case-insensitive comparisons, normalizing user input, standardizing data |
| **When NOT to use** | When case matters for data integrity (use only for display) |
| **Performance Notes** | O(n) where n is string length |

### numberFormat()
| Property | Value |
|----------|-------|
| **Syntax** | `numberFormat(number, pattern)` |
| **Parameters** | `number` - numeric value to format<br>`pattern` - format specification string |
| **Return Type** | String |
| **Description** | Formats a numeric value as a string using pattern specifications (e.g., "0.00" for 2 decimal places). |
| **Examples** | `numberFormat(1234.567, "0.00")` → `"1234.57"`<br>`numberFormat(1234.567, "#,##0.0")` → `"1,234.6"`<br>`numberFormat(0.5, "0%")` → `"50%"` |
| **Common Use Cases** | Displaying prices, sensor readings, percentages, localized number formatting |
| **When NOT to use** | For data calculations; use only for display purposes |
| **Performance Notes** | O(n) where n is pattern complexity |

### ordinal()
| Property | Value |
|----------|-------|
| **Syntax** | `ordinal(char)` |
| **Parameters** | `char` - single character string |
| **Return Type** | Integer |
| **Description** | Takes a Unicode character (as a string) and returns the corresponding character code as an integer. |
| **Examples** | `ordinal("A")` → `65`<br>`ordinal("a")` → `97`<br>`ordinal(" ")` → `32` |
| **Common Use Cases** | Character analysis, encoding operations, ASCII/Unicode inspection |
| **When NOT to use** | Use char() for the reverse operation |
| **Performance Notes** | O(1) - simple lookup |

### repeat()
| Property | Value |
|----------|-------|
| **Syntax** | `repeat(str, count)` |
| **Parameters** | `str` - string to repeat<br>`count` - number of times to repeat |
| **Return Type** | String |
| **Description** | Repeats the given string some number of times, concatenating them together. |
| **Examples** | `repeat("ab", 3)` → `"ababab"`<br>`repeat("x", 5)` → `"xxxxx"`<br>`repeat("0", 0)` → `""` |
| **Common Use Cases** | Padding, bar charts, progress indicators, pattern generation |
| **When NOT to use** | With large repeat counts (can cause memory issues) |
| **Performance Notes** | O(n*m) where n is string length and m is repeat count |

### replace()
| Property | Value |
|----------|-------|
| **Syntax** | `replace(str, search, replacement)` |
| **Parameters** | `str` - source string<br>`search` - substring to find and replace<br>`replacement` - replacement text |
| **Return Type** | String |
| **Description** | Substitutes all occurrences of a substring with replacement text. Replaces all matches, not just first. |
| **Examples** | `replace("Hello World", "World", "Ignition")` → `"Hello Ignition"`<br>`replace("aaa", "a", "b")` → `"bbb"`<br>`replace("test", "x", "y")` → `"test"` (no match) |
| **Common Use Cases** | Text substitution, data transformation, template processing, placeholder replacement |
| **When NOT to use** | For regex pattern matching; consider advanced regex functions if needed |
| **Performance Notes** | O(n*m) where n is string length, m is number of matches |

### right()
| Property | Value |
|----------|-------|
| **Syntax** | `right(str, count)` |
| **Parameters** | `str` - string to extract from<br>`count` - number of characters to extract from the right |
| **Return Type** | String |
| **Description** | Extracts a specified number of characters from the right (end) of a string. |
| **Examples** | `right("Hello", 3)` → `"llo"`<br>`right("Database", 4)` → `"base"`<br>`right("ABC", 10)` → `"ABC"` |
| **Common Use Cases** | Extracting file extensions, getting suffixes, truncating text from start |
| **When NOT to use** | For arbitrary substring extraction; use substring() for more flexibility |
| **Performance Notes** | O(n) where n is count |

### split()
| Property | Value |
|----------|-------|
| **Syntax** | `split(str, delimiter)` |
| **Parameters** | `str` - source string<br>`delimiter` - substring that separates the parts |
| **Return Type** | Array of Strings |
| **Description** | Divides a string into substrings based on a delimiter, returning an array of the parts. |
| **Examples** | `split("one,two,three", ",")` → `["one", "two", "three"]`<br>`split("a.b.c", ".")` → `["a", "b", "c"]`<br>`split("test", ",")` → `["test"]` |
| **Common Use Cases** | CSV parsing, path processing, data tokenization, configuration parsing |
| **When NOT to use** | For single character access; use substring() or individual indexing |
| **Performance Notes** | O(n) where n is string length |

### stringFormat()
| Property | Value |
|----------|-------|
| **Syntax** | `stringFormat(template, arg1, arg2, ...)` |
| **Parameters** | `template` - format string with placeholders {0}, {1}, etc.<br>`argN` - values to substitute |
| **Return Type** | String |
| **Description** | Creates formatted strings using format specifications and arguments. Similar to sprintf. |
| **Examples** | `stringFormat("Hello {0}", "World")` → `"Hello World"`<br>`stringFormat("Value: {0}, Type: {1}", 42, "int")` → `"Value: 42, Type: int"`<br>`stringFormat("{0} + {1} = {2}", 1, 2, 3)` → `"1 + 2 = 3"` |
| **Common Use Cases** | Dynamic message building, formatted reports, template expansion, localization |
| **When NOT to use** | For simple concatenation; use concat() which is more straightforward |
| **Performance Notes** | O(n) where n is template length |

### substring()
| Property | Value |
|----------|-------|
| **Syntax** | `substring(str, startIndex)` or `substring(str, startIndex, endIndex)` |
| **Parameters** | `str` - source string<br>`startIndex` - zero-based start position<br>`endIndex` - (optional) exclusive end position |
| **Return Type** | String |
| **Description** | Extracts a portion of text between specified indices. If endIndex is omitted, extracts to end of string. |
| **Examples** | `substring("Hello", 1)` → `"ello"`<br>`substring("Hello", 1, 4)` → `"ell"`<br>`substring("Database", 0, 4)` → `"Data"` |
| **Common Use Cases** | Text parsing, field extraction, substring validation, partial string matching |
| **When NOT to use** | For simple prefix/suffix extraction; use left()/right() for clarity |
| **Performance Notes** | O(n) where n is substring length |

### toBinary()
| Property | Value |
|----------|-------|
| **Syntax** | `toBinary(number)` |
| **Parameters** | `number` - unsigned integer to convert |
| **Return Type** | String |
| **Description** | Converts an unsigned integer to its binary string representation. |
| **Examples** | `toBinary(10)` → `"1010"`<br>`toBinary(255)` → `"11111111"`<br>`toBinary(0)` → `"0"` |
| **Common Use Cases** | Bit pattern analysis, bitwise operation display, binary debugging |
| **When NOT to use** | When decimal representation is needed |
| **Performance Notes** | O(log n) where n is the number |

### toHex()
| Property | Value |
|----------|-------|
| **Syntax** | `toHex(number)` |
| **Parameters** | `number` - unsigned integer to convert |
| **Return Type** | String |
| **Description** | Converts an unsigned integer to its hexadecimal string representation (lowercase). |
| **Examples** | `toHex(255)` → `"ff"`<br>`toHex(26)` → `"1a"`<br>`toHex(0)` → `"0"` |
| **Common Use Cases** | Color code generation, protocol message encoding, memory address display |
| **When NOT to use** | When decimal representation is needed |
| **Performance Notes** | O(log n) where n is the number |

### toOctal()
| Property | Value |
|----------|-------|
| **Syntax** | `toOctal(number)` |
| **Parameters** | `number` - unsigned integer to convert |
| **Return Type** | String |
| **Description** | Converts an unsigned integer to its octal string representation. |
| **Examples** | `toOctal(8)` → `"10"`<br>`toOctal(511)` → `"777"`<br>`toOctal(0)` → `"0"` |
| **Common Use Cases** | Unix permission display, octal-encoded data encoding |
| **When NOT to use** | When decimal or hex representation is more appropriate |
| **Performance Notes** | O(log n) where n is the number |

### trim()
| Property | Value |
|----------|-------|
| **Syntax** | `trim(str)` |
| **Parameters** | `str` - string to trim |
| **Return Type** | String |
| **Description** | Removes leading and trailing whitespace (spaces, tabs, newlines) from a string. |
| **Examples** | `trim("  hello  ")` → `"hello"`<br>`trim("\t\nworld\r\n")` → `"world"`<br>`trim("test")` → `"test"` |
| **Common Use Cases** | Input validation, data cleaning, CSV parsing, text normalization |
| **When NOT to use** | When internal whitespace should be preserved (it is) |
| **Performance Notes** | O(n) where n is string length |

### upper()
| Property | Value |
|----------|-------|
| **Syntax** | `upper(str)` |
| **Parameters** | `str` - string to convert |
| **Return Type** | String |
| **Description** | Takes a string and returns an uppercase version of it. Converts all lowercase letters to uppercase. |
| **Examples** | `upper("Hello World")` → `"HELLO WORLD"`<br>`upper("database")` → `"DATABASE"`<br>`upper("Test123")` → `"TEST123"` |
| **Common Use Cases** | Case-insensitive comparisons, normalizing user input, report headers |
| **When NOT to use** | When case matters for data integrity (use only for display) |
| **Performance Notes** | O(n) where n is string length |

### urlEncode()
| Property | Value |
|----------|-------|
| **Syntax** | `urlEncode(str)` |
| **Parameters** | `str` - string to URL encode |
| **Return Type** | String |
| **Description** | URL-encodes a string, converting special characters to percent-encoded values for safe HTTP transmission. |
| **Examples** | `urlEncode("hello world")` → `"hello%20world"`<br>`urlEncode("a&b=c")` → `"a%26b%3Dc"`<br>`urlEncode("test/path")` → `"test%2Fpath"` |
| **Common Use Cases** | Constructing HTTP binding URLs dynamically, query parameter encoding, API calls |
| **When NOT to use** | When constructing URL paths directly; encode only the parameter values |
| **Performance Notes** | O(n) where n is string length |

---

## DATE/TIME FUNCTIONS

### add()
| Property | Value |
|----------|-------|
| **Syntax** | `add(date, quantity, unit)` |
| **Parameters** | `date` - Date object to modify<br>`quantity` - integer amount to add (can be negative)<br>`unit` - time unit (years, months, weeks, days, hours, minutes, seconds, milliseconds) |
| **Return Type** | Date |
| **Description** | Add or subtract an amount to a given date and time, returning the new date. Unit can be years, months, weeks, days, hours, minutes, seconds, or milliseconds. |
| **Examples** | `add(now(), 1, "days")` → tomorrow's date<br>`add(now(), -2, "hours")` → 2 hours ago<br>`add(now(), 30, "minutes")` → 30 minutes from now |
| **Common Use Cases** | Calculating due dates, scheduling, deadline calculations, timeline operations |
| **When NOT to use** | For complex date arithmetic; use dateArithmetic() for more control |
| **Performance Notes** | O(1) - simple date arithmetic |

### dateArithmetic()
| Property | Value |
|----------|-------|
| **Syntax** | `dateArithmetic(date, quantity, unit)` |
| **Parameters** | `date` - Date object to modify<br>`quantity` - integer amount to add (can be negative)<br>`unit` - time unit (years, months, weeks, days, hours, minutes, seconds, milliseconds) |
| **Return Type** | Date |
| **Description** | Adds or subtracts some amount of time from a date, returning the resulting date. Alias for add(). |
| **Examples** | `dateArithmetic(now(), 1, "years")` → same date next year<br>`dateArithmetic(now(), -7, "days")` → a week ago<br>`dateArithmetic(now(), 3600, "seconds")` → one hour from now |
| **Common Use Cases** | Subscription expiry dates, shift scheduling, historical date calculations |
| **When NOT to use** | When you need the difference between dates; use dateDiff() |
| **Performance Notes** | O(1) - simple date arithmetic |

### dateDiff()
| Property | Value |
|----------|-------|
| **Syntax** | `dateDiff(date1, date2, unit)` |
| **Parameters** | `date1` - first Date object<br>`date2` - second Date object<br>`unit` - time unit for result (years, months, weeks, days, hours, minutes, seconds, milliseconds) |
| **Return Type** | Double |
| **Description** | Calculates the difference between two dates, returning the result in the specified unit as a floating point value. |
| **Examples** | `dateDiff(now(), addMonths(now(), 1), "days")` → ~30<br>`dateDiff(date1, date2, "hours")` → hours between dates<br>`dateDiff(startTime, endTime, "seconds")` → duration in seconds |
| **Common Use Cases** | Duration calculations, age calculations, elapsed time tracking, SLA monitoring |
| **When NOT to use** | For single unit extraction; use dateExtract() |
| **Performance Notes** | O(1) - simple date arithmetic |

### dateExtract()
| Property | Value |
|----------|-------|
| **Syntax** | `dateExtract(date, unit)` |
| **Parameters** | `date` - Date object to extract from<br>`unit` - time unit to extract (years, months, days, hours, minutes, seconds, milliseconds, dayOfWeek, dayOfYear, weekOfYear, etc.) |
| **Return Type** | Integer |
| **Description** | Returns an integer value that is the value of the specified date field from the given date. |
| **Examples** | `dateExtract(now(), "hours")` → 0-23 (current hour)<br>`dateExtract(now(), "dayOfWeek")` → 1-7 (1=Sunday)<br>`dateExtract(now(), "months")` → 1-12 |
| **Common Use Cases** | Time-based logic, filtering by month/year, shift determination, reporting |
| **When NOT to use** | For date arithmetic; use add() or dateArithmetic() |
| **Performance Notes** | O(1) - simple field extraction |

### dateFormat()
| Property | Value |
|----------|-------|
| **Syntax** | `dateFormat(date, pattern)` |
| **Parameters** | `date` - Date object to format<br>`pattern` - format string (e.g., "yyyy-MM-dd HH:mm:ss") |
| **Return Type** | String |
| **Description** | Returns the given date as a string, formatted according to a pattern using Java SimpleDateFormat syntax. |
| **Examples** | `dateFormat(now(), "yyyy-MM-dd")` → "2026-07-13"<br>`dateFormat(now(), "HH:mm:ss")` → "14:30:45"<br>`dateFormat(now(), "EEEE, MMMM d, yyyy")` → "Monday, July 13, 2026" |
| **Common Use Cases** | Display formatting, report generation, localized date display, UI labels |
| **When NOT to use** | For date calculations; use only for display purposes |
| **Performance Notes** | O(n) where n is pattern length |

### dateIsAfter()
| Property | Value |
|----------|-------|
| **Syntax** | `dateIsAfter(date1, date2)` |
| **Parameters** | `date1` - first Date object to compare<br>`date2` - second Date object to compare |
| **Return Type** | Boolean |
| **Description** | Compares two dates to see if date1 is after date2. Returns true if date1 > date2. |
| **Examples** | `dateIsAfter(now(), now())` → false<br>`dateIsAfter(tomorrow(), now())` → true<br>`dateIsAfter(yesterday(), now())` → false |
| **Common Use Cases** | Deadline validation, event ordering, temporal logic, version comparison |
| **When NOT to use** | For complex date range logic; use dateIsBetween() |
| **Performance Notes** | O(1) - simple comparison |

### dateIsBefore()
| Property | Value |
|----------|-------|
| **Syntax** | `dateIsBefore(date1, date2)` |
| **Parameters** | `date1` - first Date object to compare<br>`date2` - second Date object to compare |
| **Return Type** | Boolean |
| **Description** | Compares two dates to see if date1 is before date2. Returns true if date1 < date2. |
| **Examples** | `dateIsBefore(yesterday(), now())` → true<br>`dateIsBefore(now(), now())` → false<br>`dateIsBefore(tomorrow(), now())` → false |
| **Common Use Cases** | Deadline validation, event ordering, time-based access control, scheduling |
| **When NOT to use** | For complex date range logic; use dateIsBetween() |
| **Performance Notes** | O(1) - simple comparison |

### dateIsBetween()
| Property | Value |
|----------|-------|
| **Syntax** | `dateIsBetween(target, startDate, endDate)` |
| **Parameters** | `target` - Date object to check<br>`startDate` - start of the range<br>`endDate` - end of the range |
| **Return Type** | Boolean |
| **Description** | Compares three dates to see if target date is between startDate and endDate (inclusive). |
| **Examples** | `dateIsBetween(now(), yesterday(), tomorrow())` → true<br>`dateIsBetween(now(), tomorrow(), futureDate())` → false |
| **Common Use Cases** | Business hours validation, seasonal logic, eligibility periods, booking validation |
| **When NOT to use** | For single comparison; use dateIsAfter() or dateIsBefore() for clarity |
| **Performance Notes** | O(1) - two comparisons |

### dateIsDaylight()
| Property | Value |
|----------|-------|
| **Syntax** | `dateIsDaylight(date)` |
| **Parameters** | `date` - Date object to check |
| **Return Type** | Boolean |
| **Description** | Checks if the current timezone is using daylight savings time during the specified date. |
| **Examples** | `dateIsDaylight(now())` → true (during DST)<br>`dateIsDaylight(winterDate)` → false (during standard time) |
| **Common Use Cases** | Timezone-aware scheduling, international time conversion, DST handling |
| **When NOT to use** | When absolute UTC time is needed; use toMillis() for consistent storage |
| **Performance Notes** | O(1) - timezone lookup |

### daysBetween()
| Property | Value |
|----------|-------|
| **Syntax** | `daysBetween(date1, date2)` |
| **Parameters** | `date1` - first Date object<br>`date2` - second Date object |
| **Return Type** | Integer |
| **Description** | Calculates the amount of time between two dates in days. |
| **Examples** | `daysBetween(now(), tomorrow())` → 1<br>`daysBetween(now(), addDays(now(), 7))` → 7<br>`daysBetween(startDate, endDate)` → number of days between |
| **Common Use Cases** | Project duration, age calculation, trial period calculation, SLA monitoring |
| **When NOT to use** | When fractional days matter; use dateDiff() with minutes/hours |
| **Performance Notes** | O(1) - simple date arithmetic |

### fromMillis()
| Property | Value |
|----------|-------|
| **Syntax** | `fromMillis(milliseconds)` |
| **Parameters** | `milliseconds` - long value representing milliseconds since January 1, 1970 UTC |
| **Return Type** | Date |
| **Description** | Creates a date object given a millisecond value since the Unix epoch (January 1, 1970). |
| **Examples** | `fromMillis(0)` → January 1, 1970<br>`fromMillis(1658000000000)` → July 16, 2022<br>`fromMillis(now().getTime())` → creates Date from millisecond timestamp |
| **Common Use Cases** | Converting from database timestamps, API responses, system time values |
| **When NOT to use** | When you already have a Date object |
| **Performance Notes** | O(1) - simple conversion |

### get*() (hour, minute, second, etc.)
| Property | Value |
|----------|-------|
| **Syntax** | `getHour(date)`, `getMinute(date)`, `getSecond(date)`, `getMonth(date)`, `getDay(date)`, `getYear(date)` |
| **Parameters** | `date` - Date object to extract from |
| **Return Type** | Integer |
| **Description** | Extracts a specific unit of time from a date. Variants exist for hour, minute, second, month, day, year, etc. |
| **Examples** | `getHour(now())` → 0-23 (current hour)<br>`getMinute(now())` → 0-59 (current minute)<br>`getMonth(now())` → 1-12 (current month) |
| **Common Use Cases** | Time-based logic, scheduling, reports, business hour checks |
| **When NOT to use** | For complex date extraction; use dateExtract() for consistency |
| **Performance Notes** | O(1) - simple field access |

### getDate()
| Property | Value |
|----------|-------|
| **Syntax** | `getDate(year, month, day)` |
| **Parameters** | `year` - integer year (e.g., 2026)<br>`month` - integer month (1-12)<br>`day` - integer day (1-31) |
| **Return Type** | Date |
| **Description** | Creates a new Date object given a year, month, and day. Time is set to midnight (00:00:00). |
| **Examples** | `getDate(2026, 7, 13)` → July 13, 2026 00:00:00<br>`getDate(2025, 12, 25)` → Christmas 2025<br>`getDate(2026, 1, 1)` → New Year 2026 |
| **Common Use Cases** | Creating specific dates, date initialization, schedule generation |
| **When NOT to use** | When you need time components; use setTime() for complete control |
| **Performance Notes** | O(1) - simple object creation |

### getTimezone()
| Property | Value |
|----------|-------|
| **Syntax** | `getTimezone()` |
| **Parameters** | (none) |
| **Return Type** | String |
| **Description** | Returns the ID of the current timezone (e.g., "America/New_York", "Europe/London"). |
| **Examples** | `getTimezone()` → "America/New_York"<br>`getTimezone()` → "UTC"<br>`getTimezone()` → "Europe/London" |
| **Common Use Cases** | Timezone-aware applications, localization, timezone display |
| **When NOT to use** | For UTC operations; use timezone offsets instead |
| **Performance Notes** | O(1) - system call |

### getTimezoneOffset()
| Property | Value |
|----------|-------|
| **Syntax** | `getTimezoneOffset(date)` |
| **Parameters** | `date` - Date object to check (optional; defaults to now) |
| **Return Type** | Integer (milliseconds) |
| **Description** | Returns timezone offset versus UTC, accounting for Daylight Savings Time. Value is in milliseconds. |
| **Examples** | `getTimezoneOffset()` → -18000000 (EST is UTC-5)<br>`getTimezoneOffset()` → -14400000 (EDT is UTC-4)<br>`getTimezoneOffset()` → 0 (UTC) |
| **Common Use Cases** | UTC conversion, timezone arithmetic, DST-aware scheduling |
| **When NOT to use** | When you need the offset in hours; divide result by 3600000 |
| **Performance Notes** | O(1) - system call |

### getTimezoneRawOffset()
| Property | Value |
|----------|-------|
| **Syntax** | `getTimezoneRawOffset()` |
| **Parameters** | (none) |
| **Return Type** | Integer (milliseconds) |
| **Description** | Returns timezone offset versus UTC without daylight savings consideration. Value is in milliseconds. |
| **Examples** | `getTimezoneRawOffset()` → -18000000 (EST and EDT both; UTC-5)<br>`getTimezoneRawOffset()` → 0 (UTC) |
| **Common Use Cases** | Standard timezone offset (ignoring DST), UTC conversion |
| **When NOT to use** | When DST matters; use getTimezoneOffset() instead |
| **Performance Notes** | O(1) - system call |

### midnight()
| Property | Value |
|----------|-------|
| **Syntax** | `midnight(date)` |
| **Parameters** | `date` - Date object to modify |
| **Return Type** | Date |
| **Description** | Returns a copy of a date with hour, minute, second, millisecond all set to zero (start of day). |
| **Examples** | `midnight(now())` → today at 00:00:00<br>`midnight(tomorrow())` → tomorrow at 00:00:00 |
| **Common Use Cases** | Daily report generation, start of day calculations, batch job scheduling |
| **When NOT to use** | For timezone-aware calculations without checking boundaries |
| **Performance Notes** | O(1) - date modification |

### now()
| Property | Value |
|----------|-------|
| **Syntax** | `now()` |
| **Parameters** | (none) |
| **Return Type** | Date |
| **Description** | Returns the current date and time. Updated on each evaluation. |
| **Examples** | `now()` → 2026-07-13 14:30:45.123<br>`dateFormat(now(), "yyyy-MM-dd")` → "2026-07-13" |
| **Common Use Cases** | Timestamping, relative date calculations, current time display |
| **When NOT to use** | In computations requiring consistent time; capture once and reuse |
| **Performance Notes** | O(1) - system call |

### setTime()
| Property | Value |
|----------|-------|
| **Syntax** | `setTime(date, hours, minutes, seconds, milliseconds)` |
| **Parameters** | `date` - Date object<br>`hours` - 0-23 (can omit for 0)<br>`minutes` - 0-59 (can omit for 0)<br>`seconds` - 0-59 (can omit for 0)<br>`milliseconds` - 0-999 (can omit for 0) |
| **Return Type** | Date |
| **Description** | Returns a copy of a date with time fields set as specified, keeping the date portion. |
| **Examples** | `setTime(now(), 14, 30, 0)` → today at 14:30:00<br>`setTime(tomorrow(), 0, 0, 0)` → tomorrow at midnight |
| **Common Use Cases** | Schedule generation, alarm setting, time normalization |
| **When NOT to use** | For parsing time strings; use dateFormat/dateExtract for that |
| **Performance Notes** | O(1) - date modification |

### timeBetween()
| Property | Value |
|----------|-------|
| **Syntax** | `timeBetween(time, startTime, endTime)` |
| **Parameters** | `time` - time value to check (HH:mm:ss format or Date)<br>`startTime` - start time of the range<br>`endTime` - end time of the range |
| **Return Type** | Boolean |
| **Description** | Checks if the given time is between start and end times, considering only the time component. |
| **Examples** | `timeBetween(now(), "09:00:00", "17:00:00")` → true (if business hours)<br>`timeBetween(now(), "08:00", "16:30")` → time-based check |
| **Common Use Cases** | Business hours validation, maintenance windows, shift checking |
| **When NOT to use** | For date ranges; use dateIsBetween() |
| **Performance Notes** | O(1) - time comparison |

### toMillis()
| Property | Value |
|----------|-------|
| **Syntax** | `toMillis(date)` |
| **Parameters** | `date` - Date object to convert |
| **Return Type** | Long |
| **Description** | Converts a Date object to millisecond value since January 1, 1970 UTC (Unix epoch). |
| **Examples** | `toMillis(getDate(1970, 1, 1))` → 0<br>`toMillis(getDate(2026, 7, 13))` → 1778409600000 (approximate)<br>`toMillis(now())` → current Unix timestamp in ms |
| **Common Use Cases** | Database storage, API communication, timestamp calculations, duration math |
| **When NOT to use** | For display purposes; use dateFormat() |
| **Performance Notes** | O(1) - simple conversion |

---

## LOGIC FUNCTIONS

### binEnc()
| Property | Value |
|----------|-------|
| **Syntax** | `binEnc(bool1, bool2, ...)` |
| **Parameters** | Multiple boolean values |
| **Return Type** | Integer |
| **Description** | Takes a list of booleans and treats them like the bits in a binary number, returning the resulting integer value. |
| **Examples** | `binEnc(1, 0, 1, 0)` → 10 (binary 1010)<br>`binEnc(1, 1, 1, 1)` → 15 (binary 1111)<br>`binEnc(0, 0, 0, 0)` → 0 |
| **Common Use Cases** | Bit field encoding, flag combinations, status encoding |
| **When NOT to use** | For more than ~32 bits |
| **Performance Notes** | O(n) where n is number of booleans |

### binEnum()
| Property | Value |
|----------|-------|
| **Syntax** | `binEnum(bool1, bool2, ...)` |
| **Parameters** | Multiple boolean values |
| **Return Type** | Integer |
| **Description** | Takes a list of booleans and returns the index (starting at 1) of the first parameter that evaluates to true. Returns 0 if none are true. |
| **Examples** | `binEnum(0, 1, 1, 0)` → 2 (second element is true)<br>`binEnum(1, 0, 0)` → 1 (first element is true)<br>`binEnum(0, 0, 0)` → 0 (no true elements) |
| **Common Use Cases** | Priority detection, first-match selection, error detection |
| **When NOT to use** | For complex conditions; use if/case instead |
| **Performance Notes** | O(n) where n is position of first true element |

### case()
| Property | Value |
|----------|-------|
| **Syntax** | `case(testValue, val1, result1, val2, result2, ..., defaultResult)` |
| **Parameters** | `testValue` - value to test<br>`valN` - values to compare against<br>`resultN` - result if match<br>`defaultResult` - result if no match (optional) |
| **Return Type** | Any (matching result type) |
| **Description** | Operates similarly to switch statements in C-like languages. Compares testValue against multiple values and returns the matching result. |
| **Examples** | `case(status, 1, "Active", 2, "Inactive", 3, "Pending", "Unknown")` → matches status and returns label<br>`case(grade, "A", 4, "B", 3, "C", 2, 0)` → converts grade to GPA |
| **Common Use Cases** | Status translation, grade conversion, category mapping, multi-way branching |
| **When NOT to use** | For simple if/else; use if() for clarity |
| **Performance Notes** | O(n) where n is number of cases to check |

### coalesce()
| Property | Value |
|----------|-------|
| **Syntax** | `coalesce(value1, value2, value3, ...)` |
| **Parameters** | Any number of values of any type |
| **Return Type** | First non-null type |
| **Description** | Accepts any number of arguments, evaluates each in order, and returns the first non-null argument. |
| **Examples** | `coalesce(null, null, "default", "other")` → `"default"`<br>`coalesce(empty_var, default_value)` → `default_value` (if empty_var is null)<br>`coalesce(null, 5, 10)` → `5` |
| **Common Use Cases** | Default value selection, fallback chains, null handling |
| **When NOT to use** | For zero checking; use explicit comparison instead |
| **Performance Notes** | O(n) where n is number of arguments evaluated |

### getBit()
| Property | Value |
|----------|-------|
| **Syntax** | `getBit(number, position)` |
| **Parameters** | `number` - integer value<br>`position` - zero-based bit position (0 is rightmost/LSB) |
| **Return Type** | Integer (0 or 1) |
| **Description** | Returns the bit value (0 or 1) at the specified position in the binary representation of a number. |
| **Examples** | `getBit(10, 0)` → 0 (10 = 1010b, LSB is 0)<br>`getBit(10, 1)` → 1 (second bit is 1)<br>`getBit(10, 3)` → 1 (fourth bit is 1) |
| **Common Use Cases** | Bit flag checking, status verification, hardware register reading |
| **When NOT to use** | For more than ~32 bits; use appropriate data structure |
| **Performance Notes** | O(1) - bitwise operation |

### hasChanged()
| Property | Value |
|----------|-------|
| **Syntax** | `hasChanged(value)` |
| **Parameters** | `value` - any value to monitor |
| **Return Type** | Boolean |
| **Description** | Returns true if the given value has changed since the last time the Expression Item was run. Only works in expression items/tags. |
| **Examples** | `hasChanged(tag_value)` → true if value changed since last scan<br>`if(hasChanged(status), value, 0)` → returns value only on change |
| **Common Use Cases** | Change detection, edge triggering, optimization (avoid unnecessary updates) |
| **When NOT to use** | In one-time calculations; designed for recurring expression evaluation |
| **Performance Notes** | O(1) - maintains comparison state |

### if()
| Property | Value |
|----------|-------|
| **Syntax** | `if(condition, trueValue, falseValue)` |
| **Parameters** | `condition` - boolean condition to evaluate<br>`trueValue` - returned if condition is true<br>`falseValue` - returned if condition is false |
| **Return Type** | Type of matching branch |
| **Description** | Evaluates the expression condition and returns either trueValue or falseValue based on the boolean result. |
| **Examples** | `if(status == 1, "Active", "Inactive")` → conditional string<br>`if(temp > 100, "High", "Normal")` → conditional based on temperature<br>`if(value > 0, value, 0)` → returns max(value, 0) |
| **Common Use Cases** | Conditional display, value transformation, status indication |
| **When NOT to use** | For multiple branches; use case() instead |
| **Performance Notes** | O(1) - short-circuit evaluation possible |

### indexOf()
| Property | Value |
|----------|-------|
| **Syntax** | `indexOf(string, substring)` |
| **Parameters** | `string` - source string to search in<br>`substring` - substring to find |
| **Return Type** | Integer |
| **Description** | Searches for the first occurrence of the substring inside the source string. Returns the zero-based index where substring was found, or -1 if not found. |
| **Examples** | `indexOf("Hello World", "World")` → 6<br>`indexOf("Hello World", "o")` → 4 (first 'o')<br>`indexOf("Hello", "x")` → -1 (not found) |
| **Common Use Cases** | Substring location finding, string validation, parsing |
| **When NOT to use** | For replacement; use replace() |
| **Performance Notes** | O(n*m) where n is string length, m is substring length |

### isBad()
| Property | Value |
|----------|-------|
| **Syntax** | `isBad(value)` |
| **Parameters** | `value` - qualified value to check |
| **Return Type** | Boolean |
| **Description** | Determines whether a value's quality status is bad (quality = BAD). |
| **Examples** | `isBad(tag_value)` → true if tag quality is BAD<br>`if(isBad(sensor), "Sensor Error", sensor)` → handle bad sensor readings |
| **Common Use Cases** | Quality checking, error handling, data validation |
| **When NOT to use** | For general error checking; use isError() for ERROR quality |
| **Performance Notes** | O(1) - quality code check |

### isBadOrError()
| Property | Value |
|----------|-------|
| **Syntax** | `isBadOrError(value)` |
| **Parameters** | `value` - qualified value to check |
| **Return Type** | Boolean |
| **Description** | Tests if a value's quality is either bad or error status (quality = BAD or ERROR). |
| **Examples** | `isBadOrError(tag_value)` → true if quality is BAD or ERROR<br>`if(!isBadOrError(data), processData(data), "skip")` → only process good data |
| **Common Use Cases** | Quality validation, robust data processing, error detection |
| **When NOT to use** | When you need to distinguish between BAD and ERROR; check separately |
| **Performance Notes** | O(1) - quality code check |

### isError()
| Property | Value |
|----------|-------|
| **Syntax** | `isError(value)` |
| **Parameters** | `value` - qualified value to check |
| **Return Type** | Boolean |
| **Description** | Checks whether a value's quality indicates an error state (quality = ERROR). |
| **Examples** | `isError(tag_value)` → true if tag quality is ERROR<br>`if(isError(result), "Error occurred", result)` → handle error state |
| **Common Use Cases** | Error condition handling, exception detection, quality validation |
| **When NOT to use** | For general quality checking; use isBad() for BAD quality |
| **Performance Notes** | O(1) - quality code check |

### isGood()
| Property | Value |
|----------|-------|
| **Syntax** | `isGood(value)` |
| **Parameters** | `value` - qualified value to check |
| **Return Type** | Boolean |
| **Description** | Tests to see whether or not the given value is good quality (quality = GOOD). |
| **Examples** | `isGood(tag_value)` → true if quality is GOOD<br>`if(isGood(sensor), sensor, 0)` → use sensor value only if good quality |
| **Common Use Cases** | Quality validation, conditional processing, data reliability checking |
| **When NOT to use** | For non-qualified values; always returns true |
| **Performance Notes** | O(1) - quality code check |

### isNull()
| Property | Value |
|----------|-------|
| **Syntax** | `isNull(value)` |
| **Parameters** | `value` - any value to test |
| **Return Type** | Boolean |
| **Description** | Tests to see whether or not the argument value is null. |
| **Examples** | `isNull(null)` → true<br>`isNull(empty_variable)` → true if undefined<br>`isNull(5)` → false |
| **Common Use Cases** | Null checking, default value application, missing data detection |
| **When NOT to use** | For zero checking; zero is not null |
| **Performance Notes** | O(1) - simple check |

### isUncertain()
| Property | Value |
|----------|-------|
| **Syntax** | `isUncertain(value)` |
| **Parameters** | `value` - qualified value to check |
| **Return Type** | Boolean |
| **Description** | Tests to see whether or not the given value's quality is Uncertain. |
| **Examples** | `isUncertain(tag_value)` → true if quality is UNCERTAIN<br>`if(isUncertain(data), "Data uncertain", data)` → flag uncertain data |
| **Common Use Cases** | Quality validation, uncertainty flagging, data reliability assessment |
| **When NOT to use** | For reliable data; this flag indicates unreliable/stale data |
| **Performance Notes** | O(1) - quality code check |

### lastIndexOf()
| Property | Value |
|----------|-------|
| **Syntax** | `lastIndexOf(string, substring)` |
| **Parameters** | `string` - source string to search in<br>`substring` - substring to find |
| **Return Type** | Integer |
| **Description** | Searches for the last occurrence of the substring inside the source string. Returns the zero-based index of the last match, or -1 if not found. |
| **Examples** | `lastIndexOf("Hello World World", "World")` → 12 (second occurrence)<br>`lastIndexOf("a.b.c.d", ".")` → 5 (last dot)<br>`lastIndexOf("hello", "x")` → -1 (not found) |
| **Common Use Cases** | File extension finding, reverse parsing, last occurrence detection |
| **When NOT to use** | For first occurrence; use indexOf() |
| **Performance Notes** | O(n*m) where n is string length, m is substring length |

### len()
| Property | Value |
|----------|-------|
| **Syntax** | `len(str)` or `len(dataset)` |
| **Parameters** | `str` - string value OR `dataset` - dataset object |
| **Return Type** | Integer |
| **Description** | Returns the length of the argument. For strings, returns character count. For datasets, returns row count. |
| **Examples** | `len("Hello")` → 5<br>`len(query_result)` → number of rows in dataset<br>`len("")` → 0 |
| **Common Use Cases** | String validation, dataset size checking, empty detection |
| **When NOT to use** | For null checking; use isNull() |
| **Performance Notes** | O(1) for strings, O(n) for datasets where n is row count |

### lookup()
| Property | Value |
|----------|-------|
| **Syntax** | `lookup(dataset, lookupColumn, lookupValue, returnColumn)` |
| **Parameters** | `dataset` - dataset to search in<br>`lookupColumn` - column name to search in<br>`lookupValue` - value to find<br>`returnColumn` - column to return value from |
| **Return Type** | Any (type of returnColumn) |
| **Description** | Looks for lookupValue in the lookupColumn of the dataset and returns the corresponding value from returnColumn. |
| **Examples** | `lookup(userData, "id", 123, "name")` → returns name where id=123<br>`lookup(prices, "sku", "WIDGET-1", "price")` → returns price for SKU |
| **Common Use Cases** | Database lookup simulation, reference table querying, cross-reference operations |
| **When NOT to use** | For large datasets; use SQL query instead for performance |
| **Performance Notes** | O(n) where n is dataset row count; consider SQL alternatives |

### switch()
| Property | Value |
|----------|-------|
| **Syntax** | `switch(testValue, val1, result1, val2, result2, ..., defaultResult)` |
| **Parameters** | `testValue` - value to test<br>`valN` - values to compare against<br>`resultN` - result if match<br>`defaultResult` - result if no match |
| **Return Type** | Any (matching result type) |
| **Description** | Mimics switch statement functionality for multi-condition evaluation. Similar to case(). |
| **Examples** | `switch(code, 1, "One", 2, "Two", 3, "Three", "Other")` → translates numeric code<br>`switch(status, "active", 1, "inactive", 0, -1)` → converts status |
| **Common Use Cases** | State machine implementation, multi-way branching, enumeration mapping |
| **When NOT to use** | For two-way logic; use if() for clarity |
| **Performance Notes** | O(n) where n is number of cases |

### try()
| Property | Value |
|----------|-------|
| **Syntax** | `try(expression)` or `try(expression, fallbackValue)` |
| **Parameters** | `expression` - expression that might throw an error<br>`fallbackValue` - value to return if error occurs (optional; defaults to null) |
| **Return Type** | Result of expression or fallback |
| **Description** | Used to swallow errors caused by other expressions. If the expression throws an error, returns null or fallbackValue. |
| **Examples** | `try(1/x)` → null if x=0<br>`try(parseInt(str), -1)` → returns -1 if str is not a valid number<br>`try(tag.value, 0)` → returns 0 if tag doesn't exist |
| **Common Use Cases** | Error handling, graceful degradation, safe calculations |
| **When NOT to use** | For expected conditions; validate data first |
| **Performance Notes** | O(n) where n is expression complexity; avoid wrapping large expressions |

---

## TYPE CASTING FUNCTIONS

### toBoolean()
| Property | Value |
|----------|-------|
| **Syntax** | `toBoolean(value)` |
| **Parameters** | `value` - any value to convert to boolean |
| **Return Type** | Boolean |
| **Description** | Tries to convert any value to a boolean. Numbers: 0=false, non-zero=true. Strings: "true"/"1"=true, others=false. |
| **Examples** | `toBoolean(1)` → true<br>`toBoolean(0)` → false<br>`toBoolean("true")` → true<br>`toBoolean("false")` → false |
| **Common Use Cases** | Type conversion, user input parsing, flag conversion |
| **When NOT to use** | When you need to validate boolean type; check first |
| **Performance Notes** | O(1) - simple conversion |

### toBorder()
| Property | Value |
|----------|-------|
| **Syntax** | `toBorder(value)` |
| **Parameters** | `value` - color, string, or number value |
| **Return Type** | Border |
| **Description** | Used for binding Border properties on components like Containers or Labels. Creates a Border object from value. |
| **Examples** | `toBorder(color(0, 0, 0))` → creates black border<br>`toBorder("solid")` → solid line border |
| **Common Use Cases** | Dynamic border styling, component styling, theme application |
| **When NOT to use** | For text colors; use toColor() |
| **Performance Notes** | O(1) - conversion |

### toColor()
| Property | Value |
|----------|-------|
| **Syntax** | `toColor(value)` |
| **Parameters** | `value` - color code, integer, string, or RGB values |
| **Return Type** | Color |
| **Description** | Tries to convert any value to a color object. Accepts hex strings, integers, or RGB notation. |
| **Examples** | `toColor("#FF0000")` → red color<br>`toColor(255)` → blue (0x0000FF)<br>`toColor("red")` → color object for red |
| **Common Use Cases** | Dynamic color binding, status indication, theme styling |
| **When NOT to use** | For non-color values |
| **Performance Notes** | O(1) - conversion |

### toDataSet()
| Property | Value |
|----------|-------|
| **Syntax** | `toDataSet(value)` |
| **Parameters** | `value` - array or other value to convert to dataset |
| **Return Type** | DataSet |
| **Description** | Tries to coerce a value into a dataset. Can convert arrays or other data structures. |
| **Examples** | `toDataSet([[1,2],[3,4]])` → creates 2D dataset<br>`toDataSet(array)` → converts array to dataset |
| **Common Use Cases** | Data transformation, table population, query result simulation |
| **When NOT to use** | When SQL query is more appropriate |
| **Performance Notes** | O(n) where n is value size |

### toDate()
| Property | Value |
|----------|-------|
| **Syntax** | `toDate(value)` |
| **Parameters** | `value` - number (milliseconds), string, or other date representation |
| **Return Type** | Date |
| **Description** | Tries to coerce a value into a Date object. Accepts milliseconds since epoch or date strings. |
| **Examples** | `toDate(1658000000000)` → creates Date from milliseconds<br>`toDate("2026-07-13")` → parses date string<br>`toDate(now())` → returns Date as-is |
| **Common Use Cases** | Type conversion, parsing date inputs, database integration |
| **When NOT to use** | For date formatting; use dateFormat() |
| **Performance Notes** | O(1) for numbers, O(n) for string parsing |

### toDouble()
| Property | Value |
|----------|-------|
| **Syntax** | `toDouble(value)` |
| **Parameters** | `value` - any numeric value or string number |
| **Return Type** | Double (64-bit floating point) |
| **Description** | Tries to coerce a value into a double (64-bit floating point value). Highest precision for floating point. |
| **Examples** | `toDouble(5)` → 5.0<br>`toDouble("3.14159")` → 3.14159<br>`toDouble("1e10")` → scientific notation support |
| **Common Use Cases** | Precise calculations, scientific computing, high-precision measurements |
| **When NOT to use** | For integer calculations; use toInt() for clarity |
| **Performance Notes** | O(1) - conversion |

### toFloat()
| Property | Value |
|----------|-------|
| **Syntax** | `toFloat(value)` |
| **Parameters** | `value` - any numeric value or string number |
| **Return Type** | Float (32-bit floating point) |
| **Description** | Tries to coerce a value into a float (32-bit floating point value). Less precision than Double but uses less memory. |
| **Examples** | `toFloat(5)` → 5.0f<br>`toFloat("3.14")` → 3.14f<br>`toFloat(1.23456789)` → 1.2345679 (32-bit precision) |
| **Common Use Cases** | Memory-constrained calculations, hardware interface, legacy system compatibility |
| **When NOT to use** | For scientific calculations; use toDouble() for precision |
| **Performance Notes** | O(1) - conversion |

### toFont()
| Property | Value |
|----------|-------|
| **Syntax** | `toFont(str)` |
| **Parameters** | `str` - font specification string (e.g., "Arial, 12, bold") |
| **Return Type** | Font |
| **Description** | Coerces a string into a font object. String format: "FontName, Size, [bold|italic]". |
| **Examples** | `toFont("Arial, 12")` → creates 12pt Arial font<br>`toFont("Courier, 10, bold")` → bold 10pt Courier |
| **Common Use Cases** | Dynamic font styling, theme application, text formatting |
| **When NOT to use** | For static fonts; set directly in component properties |
| **Performance Notes** | O(1) - conversion |

### toInt() / toInteger()
| Property | Value |
|----------|-------|
| **Syntax** | `toInt(value)` or `toInteger(value)` |
| **Parameters** | `value` - any numeric value or string number |
| **Return Type** | Integer (32-bit) |
| **Description** | Tries to coerce a value into an integer (32-bit). Truncates decimal places. Both names are equivalent. |
| **Examples** | `toInt(3.14)` → 3<br>`toInt("42")` → 42<br>`toInt(true)` → 1<br>`toInt(false)` → 0 |
| **Common Use Cases** | Type conversion, index calculations, discrete counts |
| **When NOT to use** | For large numbers exceeding 32-bit range; use toLong() |
| **Performance Notes** | O(1) - conversion |

### toLong()
| Property | Value |
|----------|-------|
| **Syntax** | `toLong(value)` |
| **Parameters** | `value` - any numeric value or string number |
| **Return Type** | Long (64-bit integer) |
| **Description** | Tries to coerce a value into a long (64-bit integer). Supports larger numbers than int. |
| **Examples** | `toLong(3.14)` → 3<br>`toLong("9223372036854775807")` → maximum long value<br>`toLong(toMillis(now()))` → millisecond timestamp |
| **Common Use Cases** | Large number handling, timestamps, database IDs |
| **When NOT to use** | For small numbers; use toInt() for clarity |
| **Performance Notes** | O(1) - conversion |

### toStr() / toString()
| Property | Value |
|----------|-------|
| **Syntax** | `toString(value)` or `toStr(value)` |
| **Parameters** | `value` - any value to convert to string |
| **Return Type** | String |
| **Description** | Represents the value as a string. Will succeed for any type of value. Useful universal conversion function. Both names are equivalent. |
| **Examples** | `toString(42)` → "42"<br>`toString(3.14)` → "3.14"<br>`toString(now())` → date as string<br>`toString(null)` → "null" |
| **Common Use Cases** | Universal type conversion, display formatting, logging |
| **When NOT to use** | When you need specific formatting; use dateFormat() or numberFormat() |
| **Performance Notes** | O(n) where n is result string length |

---

## AGGREGATE FUNCTIONS

### groupConcat()
| Property | Value |
|----------|-------|
| **Syntax** | `groupConcat(dataset, column, separator)` or `groupConcat(value1, value2, ..., separator)` |
| **Parameters** | `dataset` - dataset to aggregate OR individual values<br>`column` - column name to concatenate<br>`separator` - string to separate values (e.g., ", " or ";") |
| **Return Type** | String |
| **Description** | Concatenates all of the values in a specified column into a single string, with each value separated by the given separator. |
| **Examples** | `groupConcat(userData, "name", ", ")` → "Alice, Bob, Charlie"<br>`groupConcat("a", "b", "c", "-")` → "a-b-c" |
| **Common Use Cases** | Report generation, list formatting, tag concatenation |
| **When NOT to use** | With very large datasets (can cause memory issues) |
| **Performance Notes** | O(n) where n is number of values |

### max()
| Property | Value |
|----------|-------|
| **Syntax** | `max(dataset, column)` or `max(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to search OR individual numeric values<br>`column` - column name to find max (for dataset form) |
| **Return Type** | Same as input type |
| **Description** | Finds and returns the maximum value in the given column or the max value in a series of numbers. |
| **Examples** | `max(temperatures, "value")` → highest temperature reading<br>`max(10, 20, 5, 15)` → 20<br>`max(-5, -2, -10)` → -2 |
| **Common Use Cases** | Peak detection, threshold identification, data range analysis |
| **When NOT to use** | For single value; min/max are aggregates |
| **Performance Notes** | O(n) where n is value count |

### maxDate()
| Property | Value |
|----------|-------|
| **Syntax** | `maxDate(dataset, column)` or `maxDate(date1, date2, ...)` |
| **Parameters** | `dataset` - dataset to search OR individual date values<br>`column` - column name with dates |
| **Return Type** | Date |
| **Description** | Finds and returns the maximum (latest) date in the given column or the max date in a series of dates. |
| **Examples** | `maxDate(events, "eventDate")` → latest event date<br>`maxDate(date1, date2, date3)` → most recent date |
| **Common Use Cases** | Latest event detection, deadline tracking, historical date queries |
| **When NOT to use** | For single date |
| **Performance Notes** | O(n) where n is date count |

### mean()
| Property | Value |
|----------|-------|
| **Syntax** | `mean(dataset, column)` or `mean(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to average OR individual numeric values<br>`column` - column name to average |
| **Return Type** | Double |
| **Description** | Calculates the mean (average) for the numbers in the given column or for a series of numbers. |
| **Examples** | `mean(readings, "temperature")` → average temperature<br>`mean(10, 20, 30)` → 20.0<br>`mean(5, 5, 5, 5)` → 5.0 |
| **Common Use Cases** | Average calculations, trend analysis, performance metrics |
| **When NOT to use** | For non-numeric data; check data types |
| **Performance Notes** | O(n) where n is value count |

### median()
| Property | Value |
|----------|-------|
| **Syntax** | `median(dataset, column)` or `median(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to find median OR individual numeric values<br>`column` - column name |
| **Return Type** | Double |
| **Description** | Calculates the median (middle value when sorted) for numbers in the column or series. For even count, returns average of two middle values. |
| **Examples** | `median(1, 2, 3, 4, 5)` → 3.0 (middle value)<br>`median(10, 20, 30, 40)` → 25.0 (average of 20 and 30)<br>`median(scores, "value")` → median score |
| **Common Use Cases** | Outlier-resistant statistics, distribution analysis, quartile calculations |
| **When NOT to use** | When mean is needed; different statistics for different purposes |
| **Performance Notes** | O(n log n) where n is value count (requires sorting) |

### min()
| Property | Value |
|----------|-------|
| **Syntax** | `min(dataset, column)` or `min(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to search OR individual numeric values<br>`column` - column name to find min |
| **Return Type** | Same as input type |
| **Description** | Finds and returns the minimum value in the given column or the min value in a series of numbers. |
| **Examples** | `min(temperatures, "value")` → lowest temperature reading<br>`min(10, 20, 5, 15)` → 5<br>`min(-5, -2, -10)` → -10 |
| **Common Use Cases** | Floor detection, minimum threshold identification, range analysis |
| **When NOT to use** | For single value |
| **Performance Notes** | O(n) where n is value count |

### minDate()
| Property | Value |
|----------|-------|
| **Syntax** | `minDate(dataset, column)` or `minDate(date1, date2, ...)` |
| **Parameters** | `dataset` - dataset to search OR individual date values<br>`column` - column name with dates |
| **Return Type** | Date |
| **Description** | Finds and returns the minimum (earliest) date in the given column or the min date in a series of dates. |
| **Examples** | `minDate(events, "eventDate")` → earliest event date<br>`minDate(date1, date2, date3)` → oldest date |
| **Common Use Cases** | Earliest event detection, start date identification, historical analysis |
| **When NOT to use** | For single date |
| **Performance Notes** | O(n) where n is date count |

### stdDev()
| Property | Value |
|----------|-------|
| **Syntax** | `stdDev(dataset, column)` or `stdDev(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to analyze OR individual numeric values<br>`column` - column name to calculate stddev |
| **Return Type** | Double |
| **Description** | Calculates the sample standard deviation of the values in the column or series. Measures data spread/dispersion. |
| **Examples** | `stdDev(10, 10, 10)` → 0.0 (no variation)<br>`stdDev(0, 100)` → 70.71... (high variation)<br>`stdDev(readings, "value")` → data spread measure |
| **Common Use Cases** | Quality control, process variation analysis, statistical process control |
| **When NOT to use** | When population stddev is needed (use different formula) |
| **Performance Notes** | O(n) where n is value count |

### sum()
| Property | Value |
|----------|-------|
| **Syntax** | `sum(dataset, column)` or `sum(value1, value2, ...)` |
| **Parameters** | `dataset` - dataset to sum OR individual numeric values<br>`column` - column name to sum |
| **Return Type** | Double |
| **Description** | Calculates the sum of the values in the column or the sum of a series of numbers. |
| **Examples** | `sum(transactions, "amount")` → total transaction amount<br>`sum(10, 20, 30)` → 60<br>`sum(1, 2, 3, 4, 5)` → 15 |
| **Common Use Cases** | Total calculations, running totals, KPI summation |
| **When NOT to use** | For counting; use len() instead |
| **Performance Notes** | O(n) where n is value count |

---

## ADVANCED FUNCTIONS

### columnRearrange()
| Property | Value |
|----------|-------|
| **Syntax** | `columnRearrange(dataset, newOrder)` |
| **Parameters** | `dataset` - dataset to rearrange<br>`newOrder` - array of column names in desired order |
| **Return Type** | DataSet |
| **Description** | Returns a view of the given dataset with the given columns in the specified order. Does not modify the original dataset. |
| **Examples** | `columnRearrange(data, ["name", "id", "value"])` → reorders columns<br>`columnRearrange(results, ["id", "created", "updated"])` → custom column order |
| **Common Use Cases** | Report formatting, data restructuring, column reordering |
| **When NOT to use** | For filtering columns; filter columns first |
| **Performance Notes** | O(n*m) where n is rows, m is columns |

### columnRename()
| Property | Value |
|----------|-------|
| **Syntax** | `columnRename(dataset, oldName, newName)` or with array of pairs |
| **Parameters** | `dataset` - dataset to rename columns in<br>`oldName` - current column name<br>`newName` - new column name |
| **Return Type** | DataSet |
| **Description** | Returns a view of the given dataset with the columns renamed as specified. Original dataset unmodified. |
| **Examples** | `columnRename(data, "temp_c", "temperature_celsius")` → renames single column<br>`columnRename(data, [["old1","new1"],["old2","new2"]])` → renames multiple |
| **Common Use Cases** | Data standardization, report formatting, schema aliasing |
| **When NOT to use** | Frequently; prefer consistent naming at data source |
| **Performance Notes** | O(1) - creates view, no data copy |

### forceQuality()
| Property | Value |
|----------|-------|
| **Syntax** | `forceQuality(value, qualityCode)` |
| **Parameters** | `value` - value to wrap<br>`qualityCode` - quality code (GOOD, BAD, UNCERTAIN, ERROR) |
| **Return Type** | Qualified Value |
| **Description** | Returns the given value, but overwrites the quality of that value with the specified quality code. |
| **Examples** | `forceQuality(tag_value, "GOOD")` → forces GOOD quality even if tag is bad<br>`forceQuality(100, "UNCERTAIN")` → returns value with uncertain quality |
| **Common Use Cases** | Quality override, test data creation, quality simulation |
| **When NOT to use** | For actual bad values; handle root cause instead |
| **Performance Notes** | O(1) - quality wrapping |

### property()
| Property | Value |
|----------|-------|
| **Syntax** | `property(path)` |
| **Parameters** | `path` - string path to property (e.g., "container.textfield.text") |
| **Return Type** | Any (type of property) |
| **Description** | Retrieves property values at specified paths as objects, accepting a single string argument. |
| **Examples** | `property("rootContainer.button1.text")` → retrieves button text<br>`property("view1.label1.visible")` → retrieves visibility state |
| **Common Use Cases** | Dynamic property access, programmatic component interaction |
| **When NOT to use** | When direct binding is available; property() is slower |
| **Performance Notes** | O(n) where n is path depth |

### qualifiedValue()
| Property | Value |
|----------|-------|
| **Syntax** | `qualifiedValue(value, qualityCode, timestamp)` |
| **Parameters** | `value` - value to wrap<br>`qualityCode` - quality code (GOOD, BAD, UNCERTAIN, ERROR)<br>`timestamp` - optional timestamp |
| **Return Type** | Qualified Value |
| **Description** | Returns the given value wrapped with specified quality and optional timestamp. Can customize both quality and timestamp. |
| **Examples** | `qualifiedValue(42, "GOOD")` → value with GOOD quality<br>`qualifiedValue(100, "BAD", now())` → value with timestamp and quality |
| **Common Use Cases** | Creating qualified values, test data, quality/timestamp simulation |
| **When NOT to use** | For reading tag qualities; use qualityOf() instead |
| **Performance Notes** | O(1) - wrapping operation |

### qualityOf()
| Property | Value |
|----------|-------|
| **Syntax** | `qualityOf(value)` |
| **Parameters** | `value` - qualified value to inspect |
| **Return Type** | Integer (QualityCode) |
| **Description** | Returns the QualityCode of a qualified value as an integer. |
| **Examples** | `qualityOf(tag_value)` → returns quality code of tag<br>`if(qualityOf(sensor) == 0, "Good", "Bad")` → checks quality |
| **Common Use Cases** | Quality checking, conditional logic based on data quality |
| **When NOT to use** | Use isGood/isBad/isError functions instead for clarity |
| **Performance Notes** | O(1) - quality extraction |

### runScript()
| Property | Value |
|----------|-------|
| **Syntax** | `runScript(pythonCode)` |
| **Parameters** | `pythonCode` - single line of Python code as string |
| **Return Type** | Result of Python code |
| **Description** | Runs a single line of Python code as an expression. Very limited - single statement only. |
| **Examples** | `runScript("return int(5 * 2)")` → executes Python expression<br>`runScript("return len('hello')")` → returns 5 |
| **Common Use Cases** | Complex calculations, Python library access, advanced operations |
| **When NOT to use** | For multi-line code; use script blocks instead<br>For simple operations; use native expressions |
| **Performance Notes** | O(n) - significant overhead; avoid in high-frequency bindings |

### sortDataset()
| Property | Value |
|----------|-------|
| **Syntax** | `sortDataset(dataset, column)` or `sortDataset(dataset, column, ascending)` |
| **Parameters** | `dataset` - dataset to sort<br>`column` - column name to sort by<br>`ascending` - boolean (default true) |
| **Return Type** | DataSet |
| **Description** | Returns a new dataset based on the rows in the given dataset, sorted by the specified column. |
| **Examples** | `sortDataset(data, "name")` → sorts by name ascending<br>`sortDataset(data, "date", false)` → sorts by date descending |
| **Common Use Cases** | Data ordering, report generation, leaderboard creation |
| **When NOT to use** | For large datasets; sort in SQL instead |
| **Performance Notes** | O(n log n) where n is row count |

### tag()
| Property | Value |
|----------|-------|
| **Syntax** | `tag(path)` |
| **Parameters** | `path` - string path to tag (e.g., "Devices/Temperature") |
| **Return Type** | Any (qualified value of tag) |
| **Description** | Retrieves tag values at specified paths, using string-based path arguments. Dynamic tag reading. |
| **Examples** | `tag("[default]Devices/Temperature")` → reads tag value<br>`tag("[SCADA]Motors/Speed")` → reads from specific provider |
| **Common Use Cases** | Dynamic tag access, programmatic reads, tag path variables |
| **When NOT to use** | For static tags; use direct binding |
| **Performance Notes** | O(1) - tag lookup |

### timestampOf()
| Property | Value |
|----------|-------|
| **Syntax** | `timestampOf(value)` |
| **Parameters** | `value` - qualified value to inspect |
| **Return Type** | Long (milliseconds) |
| **Description** | Returns the timestamp of a qualified value as milliseconds since epoch. |
| **Examples** | `timestampOf(tag_value)` → returns when tag was updated<br>`dateFormat(fromMillis(timestampOf(value)), "yyyy-MM-dd")` → formats tag timestamp |
| **Common Use Cases** | Timestamp verification, data freshness checks, audit logging |
| **When NOT to use** | For current time; use now() |
| **Performance Notes** | O(1) - extraction |

### typeOf()
| Property | Value |
|----------|-------|
| **Syntax** | `typeOf(value)` |
| **Parameters** | `value` - any value to inspect |
| **Return Type** | String |
| **Description** | Returns the simple name of the Java type of the given value as a string. |
| **Examples** | `typeOf(42)` → "Integer"<br>`typeOf("text")` → "String"<br>`typeOf(now())` → "Date"<br>`typeOf([1,2,3])` → "ArrayList" |
| **Common Use Cases** | Type checking, debugging, dynamic type handling |
| **When NOT to use** | For performance-critical code; use try() instead of type checking |
| **Performance Notes** | O(1) - type lookup |

---

## COLOR FUNCTIONS

### brighter()
| Property | Value |
|----------|-------|
| **Syntax** | `brighter(color)` |
| **Parameters** | `color` - color value to brighten |
| **Return Type** | Color |
| **Description** | Returns a color that is one shade brighter than the color given as an argument. Increases brightness. |
| **Examples** | `brighter(color(100, 100, 100))` → lighter gray<br>`brighter("#800080")` → brighter purple |
| **Common Use Cases** | Hover states, highlighting, theme generation, visual feedback |
| **When NOT to use** | For theme management; use consistent color palettes |
| **Performance Notes** | O(1) - color math |

### color()
| Property | Value |
|----------|-------|
| **Syntax** | `color(red, green, blue)` or `color(red, green, blue, alpha)` |
| **Parameters** | `red` - 0-255 integer<br>`green` - 0-255 integer<br>`blue` - 0-255 integer<br>`alpha` - 0-255 (optional, transparency) |
| **Return Type** | Color |
| **Description** | Creates a color using the given red, green, and blue amounts, which are integers between 0-255. Optionally includes alpha for transparency. |
| **Examples** | `color(255, 0, 0)` → pure red<br>`color(0, 255, 0)` → pure green<br>`color(0, 0, 255)` → pure blue<br>`color(128, 128, 128, 128)` → semi-transparent gray |
| **Common Use Cases** | Dynamic color generation, theme customization, status indication |
| **When NOT to use** | Use hex notation where possible for clarity |
| **Performance Notes** | O(1) - object creation |

### darker()
| Property | Value |
|----------|-------|
| **Syntax** | `darker(color)` |
| **Parameters** | `color` - color value to darken |
| **Return Type** | Color |
| **Description** | Returns a color that is one shade darker than the color given as an argument. Decreases brightness. |
| **Examples** | `darker(color(200, 200, 200))` → darker gray<br>`darker("#FFFF00")` → darker yellow |
| **Common Use Cases** | Press states, shadows, theme generation, visual hierarchy |
| **When NOT to use** | For theme management; use consistent color palettes |
| **Performance Notes** | O(1) - color math |

### gradient()
| Property | Value |
|----------|-------|
| **Syntax** | `gradient(number, low, high)` |
| **Parameters** | `number` - numeric value to evaluate<br>`low` - low end of range<br>`high` - high end of range |
| **Return Type** | Double (0-1 percentage) |
| **Description** | Calculates a percentage given three numeric arguments: number, low, and high. Returns normalized value between 0-1. |
| **Examples** | `gradient(50, 0, 100)` → 0.5 (50% of range)<br>`gradient(0, 0, 100)` → 0.0 (at low end)<br>`gradient(100, 0, 100)` → 1.0 (at high end) |
| **Common Use Cases** | Progress bars, heat maps, normalization, color gradients |
| **When NOT to use** | For out-of-range values without bounds checking |
| **Performance Notes** | O(1) - arithmetic operation |

---

## ALARMING FUNCTIONS

### isAlarmActive()
| Property | Value |
|----------|-------|
| **Syntax** | `isAlarmActive(source)` or with filtering parameters |
| **Parameters** | `source` - tag path or alarm source to check |
| **Return Type** | Boolean |
| **Description** | Returns whether there are active alarms that match the provided criteria. Used for alarm status checking. |
| **Examples** | `isAlarmActive("[default]MyTag")` → true if MyTag has active alarms |
| **Common Use Cases** | Alarm indicators, status visualization, alarm-based logic |
| **When NOT to use** | For historical alarm analysis; use alarm history queries |
| **Performance Notes** | O(1) - alarm query |

### isAlarmActiveFiltered()
| Property | Value |
|----------|-------|
| **Syntax** | `isAlarmActiveFiltered(source, filter)` |
| **Parameters** | `source` - tag path or alarm source<br>`filter` - filter criteria (priority, state, etc.) |
| **Return Type** | Boolean |
| **Description** | Returns whether there are active alarms matching both the source and the provided filter criteria. Allows filtered alarm checking. |
| **Examples** | `isAlarmActiveFiltered("[default]MyTag", "HIGH")` → true if high-priority alarms<br>`isAlarmActiveFiltered("equipment", "CRITICAL")` → checks for critical alarms |
| **Common Use Cases** | Filtered alarm indicators, priority-based logic, state-specific responses |
| **When NOT to use** | For complex alarm queries; use alarm tables instead |
| **Performance Notes** | O(n) where n is active alarms matching criteria |

---

## USER FUNCTIONS

### hasRole()
| Property | Value |
|----------|-------|
| **Syntax** | `hasRole(role)` or `hasRole(username, role)` or `hasRole(username, usersource, role)` |
| **Parameters** | `role` - role name to check (required)<br>`username` - user to check (optional in client, required in gateway)<br>`usersource` - user source (required in gateway) |
| **Return Type** | Boolean |
| **Description** | Returns true if the user has the given role. Username and usersource parameters are optional in client scope but required in gateway scope. |
| **Examples** | `hasRole("admin")` → true if current user is admin (client scope)<br>`hasRole("john", "default", "manager")` → check if john has manager role (gateway) |
| **Common Use Cases** | Access control, UI visibility, feature permissions, security checks |
| **When NOT to use** | For authentication; this is authorization only |
| **Performance Notes** | O(1) - role lookup |

### isAuthorized()
| Property | Value |
|----------|-------|
| **Syntax** | `isAuthorized()` |
| **Parameters** | (none) |
| **Return Type** | Qualified Boolean |
| **Description** | Returns a qualified value with a boolean value which is true if the user in the current session is authorized, false otherwise. |
| **Examples** | `isAuthorized()` → true if current user has access |
| **Common Use Cases** | Session validation, access control, security checks |
| **When NOT to use** | For role-specific checks; use hasRole() |
| **Performance Notes** | O(1) - session query |

---

## TRANSLATION FUNCTIONS

### translate()
| Property | Value |
|----------|-------|
| **Syntax** | `translate(key)` |
| **Parameters** | `key` - translation key to look up |
| **Return Type** | String |
| **Description** | Returns a translated string based on the current locale and configured translation keys. |
| **Examples** | `translate("button.ok")` → "OK" in current locale, "Aceptar" in Spanish, "D'accord" in French |
| **Common Use Cases** | Multi-language support, UI localization, international applications |
| **When NOT to use** | For static text; only use for user-facing strings that need translation |
| **Performance Notes** | O(1) - hash table lookup |

---

## IDENTITY PROVIDER FUNCTIONS

### containsAll()
| Property | Value |
|----------|-------|
| **Syntax** | `containsAll(collection, element1, element2, ...)` |
| **Parameters** | `collection` - collection object to check<br>`elementN` - elements to verify (at least one required) |
| **Return Type** | Boolean |
| **Description** | Checks if all of the listed elements are present in the collection object. All must be present. |
| **Examples** | `containsAll(permissions, "read", "write", "admin")` → true if all three permissions exist<br>`containsAll(roles, "user", "editor")` → true if both roles present |
| **Common Use Cases** | Permission verification, role checking, group membership validation |
| **When NOT to use** | When any element suffices; use containsAny() |
| **Performance Notes** | O(n*m) where n is collection size, m is elements to check |

### containsAny()
| Property | Value |
|----------|-------|
| **Syntax** | `containsAny(collection, element1, element2, ...)` |
| **Parameters** | `collection` - collection object to check<br>`elementN` - elements to verify (at least one required) |
| **Return Type** | Boolean |
| **Description** | Checks if any of the listed elements are present in the collection object. Only one needs to be present. |
| **Examples** | `containsAny(roles, "admin", "manager")` → true if either admin or manager role<br>`containsAny(permissions, "write", "admin")` → true if either permission exists |
| **Common Use Cases** | Role-based access, permission checking, membership validation |
| **When NOT to use** | When all elements required; use containsAll() |
| **Performance Notes** | O(n*m) where n is collection size, m is elements to check |

---

## PERFORMANCE OPTIMIZATION SUMMARY

| Function Category | Performance Tier | Notes |
|------------------|-----------------|-------|
| Math (abs, round, etc.) | O(1) | Constant time, safe for frequent use |
| String (concat, split, etc.) | O(n) | Depends on string length; efficient generally |
| Date/Time operations | O(1) | Fast for basic operations |
| Logic operations | O(1)-O(n) | Generally very fast |
| Type casting | O(1) | Simple conversions |
| Aggregate functions | O(n) to O(n log n) | Depends on dataset size; consider SQL for large data |
| Advanced (sort, etc.) | O(n log n) | Use SQL for large datasets |
| Color operations | O(1) | Quick calculations |
| User/Auth functions | O(1) | Session-based, efficient |
| Translation | O(1) | Hash table lookup |

**General Performance Guidelines:**
- Avoid using aggregates on large datasets in expressions; use SQL queries instead
- Cache results from expensive operations when possible
- Use appropriate functions for the data type (sum vs mean, min vs minDate)
- In high-frequency bindings, prefer O(1) operations
- Test with realistic data volumes before deploying

---

## QUICK REFERENCE BY USE CASE

### Calculations & Math
- **Basic Math**: abs, round, ceil, floor, sqrt, pow
- **Trigonometry**: sin, cos, tan, asin, acos, atan
- **Logarithms**: log, log10, exp
- **Angle Conversion**: toRadians, toDegrees

### Text Processing
- **Build/Format**: concat, stringFormat, numberFormat
- **Search**: indexOf, lastIndexOf
- **Extract**: substring, left, right
- **Transform**: upper, lower, trim, replace
- **Convert**: toHex, toBinary, toOctal, fromHex, fromBinary

### Date/Time Operations
- **Current Time**: now, midnight
- **Arithmetic**: add, dateArithmetic, daysBetween, dateDiff
- **Extraction**: dateExtract, getHour, getMinute, getDate
- **Comparison**: dateIsAfter, dateIsBefore, dateIsBetween
- **Format**: dateFormat, toMillis, fromMillis
- **Timezone**: getTimezone, getTimezoneOffset, dateIsDaylight

### Conditional Logic
- **Simple**: if, try
- **Multi-branch**: case, switch
- **Null Handling**: coalesce, isNull
- **Quality Checking**: isGood, isBad, isError, isUncertain

### Type Operations
- **Conversion**: toInt, toString, toDate, toBoolean, toColor
- **Analysis**: typeOf, qualityOf, timestampOf

### Data Aggregation
- **Summary**: sum, mean, median, min, max, count, stdDev
- **Date Aggregates**: minDate, maxDate
- **String Aggregation**: groupConcat
- **Sorting**: sortDataset

### Data Structure
- **Column Ops**: columnRename, columnRearrange
- **Lookup**: lookup
- **Quality**: forceQuality, qualifiedValue

### Access Control
- **Authorization**: hasRole, isAuthorized
- **Collections**: containsAll, containsAny

### Visualization
- **Colors**: color, brighter, darker, gradient

### Alarms
- **Status**: isAlarmActive, isAlarmActiveFiltered

---

## DOCUMENTATION METADATA

- **Total Functions Documented**: 123+
- **Categories**: 12
- **Last Updated**: 2026-07-13
- **Ignition Version**: 8.3
- **Format**: Reference tables with syntax, parameters, return types, examples, and use case guidance
- **Source**: docs.inductiveautomation.com/docs/8.3/appendix/expression-functions

**How to Use This Reference:**
1. Find your function in the Quick Navigation or use Ctrl+F to search
2. Check the syntax and parameters
3. Review examples for typical usage patterns
4. Note "When NOT to use" for common mistakes
5. Consider performance notes for frequently-called expressions
6. Consult "Common Use Cases" for real-world context

---

## See Also

**Prerequisites:** [22-EXPRESSIONS](22-EXPRESSIONS.md), [25a-APPENDIX-EXPRESSIONS-EXTENDED](25a-APPENDIX-EXPRESSIONS-EXTENDED.md)

**Builds toward:** [82-DEBUGGING-GUIDE](82-DEBUGGING-GUIDE.md), [QUICK-REFERENCE](QUICK-REFERENCE.md)

**Related:** [22-EXPRESSIONS](22-EXPRESSIONS.md), [25a-APPENDIX-EXPRESSIONS-EXTENDED](25a-APPENDIX-EXPRESSIONS-EXTENDED.md), [35-COMPLETE-SYSTEM-FUNCTIONS](35-COMPLETE-SYSTEM-FUNCTIONS.md), [21-BINDINGS](21-BINDINGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
