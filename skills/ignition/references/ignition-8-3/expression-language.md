# Ignition 8.3 — Expression language

Compact reference built from the live Ignition 8.3 docs (docs.inductiveautomation.com/docs/8.3). Covers syntax/semantics, all 130 documented expression functions across 14 categories, date/number format strings, cron syntax, and common gotchas.

## Syntax and semantics

Source: `platform/expression-language-and-syntax`.

#### What an expression is

Everything in the expression language *is* an expression — it always evaluates to a value. `5`, `5+1`, `{MyTags/TankLevel}`, and `{MyTags/TankLevel}+1` are all expressions and can be freely combined. Formally, an expression is one of: a number, boolean, string, bound tag, bound property, function call, dataset access, or an equation involving any of these.

#### Literals

- **Numbers**: integers, floats, hex with a `0x` prefix (`0xFFC2`), and scientific notation (`1.3e5`).
- **Strings**: single or double quotes; backslash-escape quotes inside a string. Escape sequences: `\n` (newline), `\t` (tab), `\r` (carriage return).
- **Booleans**: `True`/`False`, case-insensitive (`true`, `tRuE`, `TRUE` all work) — `True`/`False` is the recommended casing since it matches Python.
- **Null**: `null`, `None`, or `none` — all equivalent.

#### Operators (by category, not strict precedence table in the docs)

| Operator | Name | Notes |
|---|---|---|
| `//` | Comment | Rest of the line is ignored |
| `-` | Unary minus / subtraction | Negates if no left operand, else subtracts |
| `!` | Not | Logical negation of a boolean |
| `^` | Power | Exponentiation |
| `%` | Modulus | Remainder of `a÷b` |
| `*`, `/` | Multiply, Divide | |
| `+` | Add / concatenation | Adds if both operands are numbers, otherwise concatenates as strings (`2 + 'Alarms'` → `"2Alarms"`) |
| `~` | Bitwise NOT | Flips each bit |
| `&` | Bitwise AND | |
| `\|` | Bitwise OR | |
| `xor` | Bitwise XOR | |
| `<<`, `>>` | Left/right shift | Signed bitwise shift |
| `>`, `<`, `>=`, `<=` | Comparisons | Return boolean |
| `=`, `!=` | Equal, Not equal | |
| `&&` | Logical AND | |
| `\|\|` | Logical OR | |
| `like` | Fuzzy string match | Pattern may use `%`, `*`, `?` wildcards |

Whitespace (spaces, tabs, newlines) is ignored, so expressions are commonly split across multiple lines for readability, with `//` comments annotating arguments.

#### Type coercion

The `+` operator is the main implicit-coercion case: numeric operands add, anything else concatenates as strings. Beyond that, the language leans on explicit **type-casting functions** (`toInt`, `toString`, `toDate`, `toColor`, etc. — see Type Casting category) rather than implicit coercion, particularly for dataset column values, since the expression system cannot infer a column's datatype: `toInt({Root Container.Table.data}[6, "ProductCode"])`.

#### Null and quality handling

- A bound tag or property value carries a **quality** (Good/Uncertain/Bad/Error) alongside its value. The Logic category provides direct quality tests: `isGood`, `isBad`, `isUncertain`, `isError`, `isBadOrError`, plus `isNull` for a literal null value.
- `coalesce(value, [value, ...])` returns the first non-null argument (returns null if all are null) — the standard null-fallback idiom.
- `try(expression, failover)` swallows any error thrown while evaluating `expression` and substitutes `failover`, whose quality is then applied to the result.
- `forceQuality(value, [qualityCode])` and `qualifiedValue(value, level, [subcode], [diagnosticMessage])` let an expression manufacture or override a value's quality explicitly — useful for surfacing a "not applicable" or diagnostic state through a binding instead of a raw value.
- `qualityOf(value)` and `timestampOf(value)` extract the quality code / last-update timestamp from a qualified value.

#### Comments

`//` starts a comment that runs to the end of the line. Since whitespace/newlines are ignored, this is commonly used to annotate individual arguments of a multi-line function call:

```
if( {Root Container.UseTagValueOption.selected},
    {MyTags/SomeValue}, // Use the tag value.
    "Not Selected"      // Use default value if the user doesn't check the box.
)
```

#### Referencing tags and properties

Bound values are paths enclosed in braces `{...}` and appear red in the Expression Editor.

- **Tag reference**: `{[default]Path/To/Tag}` — the `[provider]` prefix selects the tag provider; omitting it uses the default/contextual provider. Special path notation (`~`, `[.]`) is documented on the Tag Paths page.
- **Property reference**: `{Root Container.Label.text}` — a dot-path to another component's property.
- The **Insert Property** and **Insert Tag** icons in the Expression Editor build these references for you.

#### Dataset, collection, and map access

```
Dataset_Expression["Column_Name"]                 // first row, given column name
Dataset_Expression[Column_Index]                  // first row, given column index
Dataset_Expression[Row_Index, "Column_Name"]      // given row + column name
Dataset_Expression[Row_Index, Column_Index]       // given row + column index
{An Array}[2]                                      // 3rd element of a sequence
{A Map}["myKey"]                                   // value at key "myKey" in a dict/JSON object
```

#### Function call syntax

```
functionName(expression1, expression2, ...)
```
Any argument can itself be an arbitrary (nested) expression, including another function call.

#### Binding-scope differences

The same expression syntax is shared across contexts, but **what you can reference** and where the expression runs differs:

- **Vision Expression Binding**: can reference both tag values (`{[default]Path}`) and component/window properties (`{Root Container.Label.text}`).
- **Perspective Expression Binding**: same brace syntax for tags and properties; some functions are Perspective-only (e.g. `property()`) or behave differently there — e.g. `color()` and `toColor()` were designed for Vision's Java `Color` objects and do **not** work in Perspective bindings, which should instead bind color properties directly to hex strings like `"#00FF00"`.
- **Expression Tags**: can *only* reference other tag values — not component/window properties, since a tag has no notion of a UI component.
- **Alarm / Transaction Group expressions**: run in the Gateway scope. Functions like `hasRole()` require all parameters (username, usersource) explicitly there, since there's no "current session user" context the way there is in a Vision/Perspective client. `hasChanged()` is restricted to Transaction Group Expression Items and Expression Tags specifically, where it compares against the value at the last group/tag execution.
- **Identity Provider expressions** (Security Level Rules, User Attribute Mapping): a distinct sub-scope with its own functions (`containsAll`, `containsAny`) that read special bound objects like `{security-zones}` or `{idp-attribute:X}` — these functions are *not* usable in ordinary component/tag expressions.


## Functions by category

#### Advanced

### columnRearrange
*Category: Advanced*  
`columnRearrange(dataset[, col...])`

Returns a view of the given dataset with the given columns in the order specified.

**Params:** dataset (Dataset): The starting dataset.; col (String): Optional. Any number of column names, in the order that they sh...

**Returns:** **DataSet** - A new dataset with columns in the order specified.

**Example:** `columnRearrange({Root Container.fiveColDataset.data}, "secondCol", "thirdCol", "firstCol")`

### columnRename
*Category: Advanced*  
`columnRename(dataset[, newName...])`

Returns a view of the given dataset with the columns renamed.

**Params:** dataset (Dataset): The starting dataset.; newName (String): Optional. Any number of new column names. The columns speci...

**Returns:** **DataSet** - A new dataset with new column names.

**Example:** `columnRename(twoColDataset, "colOne", "colTwo") // returns a Dataset with columns ["colOne", "colTwo"]`

### forceQuality
*Category: Advanced*  
`forceQuality(value[, qualityCode])`

Returns the given value, but overwrites the quality of that value.

**Params:** value (Object): The value to force a quality on.; qualityCode (Integer): Optional. The qualityCode to force on the value.

**Returns:** **Object** - The value with a forced quality.

**Example:** `forceQuality({Tanks/Tank15}) //returns the value of the Tank15 tag, but always with a good quality code.`

**Note:** [caution] Be aware the quality codes linked in the description above access the 7.9 quality codes, which are the codes the forceQuality function uses. For an option us...

### property
*Category: Advanced*  
`property(propertyPath)`

Returns an object representing the value of the property at the path specified. It takes a single string as an argument and attempts to lookup the property v...

**Params:** propertyPath (String): The property path to the property.

**Returns:** **Object** - The value of the property.

**Example:** `property("this.custom." + {view.params.ControlType})`

**Note:** [caution] Perspective Only The property() expression function is only accessible in Perspective.

### qualifiedValue
*Category: Advanced*  
`qualifiedValue(value, level, [subcode], [diagnosticMessage])`

Returns the given value, but overwrites the quality of that value.

**Params:** value (Object): The value to force a quality on.; level (Object): The level to force on the value. Possible levels are Good or ...; subcode (Object): The subcode to include with the quality level. See Quality ...; diagnosticMessage (Object): The diagnostic message to add to the quality. [op...

**Returns:** **QualifiedValue** - The value with a forced quality, formatted as a QualifiedValue.

**Example:** `qualifiedValue(1, 'bad', 515, 'New Quality') //Returns the value 1 but with a quality of Bad_Disabled("New ...`

### qualityOf
*Category: Advanced*  
`qualityOf(value)`

Returns the QualityCode of a qualified value.

**Params:** value (Object): The value for which you want to find the quality.

**Returns:** **QualityCode** - Returns the code associated with the quality. For more information on quality codes, including a list of available code...

**Example:** `qualityOf({[default]Sensor 1/Reading}) //Returns the quality code of the tag's value`

### runScript
*Category: Advanced*  
Runs a single line of Python code as an expression.

**Example:** `def myFunc(text="Hello World!", moreText="Good bye"): return text`

**Note:** [note] Normally expressions execute fairly quickly when compared to a script. However, calling runScript will mitigate the speed advantage of an expression. In most...

### sortDataset
*Category: Advanced*  
`sortDataset(dataset, colIndex, [ascending], [naturalOrdering]) (index)`  
`sortDataset(dataset, colName, [ascending], [naturalOrdering]) (name)`

Returns a new dataset based on the rows in the given dataset.

**Params:** dataset (Dataset): The starting dataset.; colIndex (Integer): The index of the column to sort on.; ascending (Boolean): A flag indicating whether or not to sort ascending. Defa...; naturalOrdering (Boolean): A flag indicating the ordering method. True for na...; colName (String): The name of the column to sort on.

**Returns:** **DataSet** - A sorted dataset.

**Example:** `sortDataset(dataset, 0, true) // returns a Dataset sorted ascending on column 0.`

### tag
*Category: Advanced*  
`tag(tagPath)`

Returns an object representing the value of the Tag at the path specified.

**Params:** tagPath (String): The tag path to the tag.

**Returns:** **Object** - The value of the tag. The object returned by the function may need to be converted to a standard data type using one of the ...

**Example:** `tag("Tanks/Tank5") //returns Tank5's value.`

**Note:** [note] When using the tag() function in a logic function, the tag value will remain subscribed to, even if the logic function chooses a different outcome. This can ...

### timestampOf
*Category: Advanced*  
`timestampOf(value)`

Returns the timestamp of a qualified value.

**Params:** value (Object): The value for which you want to find the timestamp.

**Returns:** **Date** - Returns the timestamp of the value's last update.

**Example:** `timestampOf({[default]Sensor 1/Reading}) //Returns the timestamp of the tag's last value update`

### typeOf
*Category: Advanced*  
`typeOf(value)`

Returns the simple name of the Java type.

**Params:** value (Any): The object for which you want to find the Java type.

**Returns:** **String** - Returns the simple name of the Java type.

**Example:** `typeOf("My String")`

#### Aggregates

### groupConcat
*Category: Aggregates*  
`groupConcat(dataset, columnIndex, separator) (index)`  
`groupConcat(dataset, columnName, separator) (name)`  
`groupConcat(collection, separator) (collection)`

Concatenates all of the values in a specified column or collection into a string, with each value separated by the string separator.

**Params:** dataset (Dataset): The starting dataset.; columnIndex (Integer): The index of the column to concatenate.; separator (String): What will be used to separate each of the values.; columnName (String): The name of the column to concatenate.; collection (Collection): The starting list, tuple, or set to use.

**Returns:** **String** - A string with every value in the specified column of the specified dataset separated by the separator value. / **String** - A string with every value in the specified collection separated by the separator value.

**Example:** `groupConcat({Root Container.Table.data}, 1, " / ")`

### max
*Category: Aggregates*  
`max(dataset, columnIndex) (index)`  
`max(dataset, columnName) (name)`  
`max(value[, value...])`  
`max(sequence)`

Finds and returns the maximum value in the given column of the given dataset, or the max value in a series of numbers specified as arguments.

**Params:** dataset (Dataset): The dataset to search through.; columnIndex (Integer): The index of the column to search through. Must be a c...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer** - The maximum value in that column. / **Integer** - The maximum value in the list of values.

**Example:** `max({Root Container.Table.data}, 1) //would return 380`

### maxDate
*Category: Aggregates*  
`maxDate(dataset, columnIndex) (index)`  
`maxDate(dataset, columnName) (name)`  
`maxDate(date[, date]) (date)`

Finds and returns the maximum date in the given column of the given dataset, or the max value in a series of dates specified as arguments.

**Params:** dataset (Dataset): The starting dataset to search.; columnIndex (Integer): The index of the column to search for the max date. Mu...; columnName (String): The name of the column to search for the max date. Must ...; date (Date): A date. Can be as many dates as needed.

**Returns:** **Date** - The maximum date of the given date column in the given dataset. / **Date** - The maximum date of the given dates.

**Example:** `maxDate({Root Container.Table.data}, "AlarmTime") //You could use this expression to get the date and time ...`

### mean
*Category: Aggregates*  
`mean(dataset, columnIndex) (index)`  
`mean(dataset, columnName) (name)`  
`mean(value[, value...]) (value)`  
`mean(sequence) (sequence)`

Calculates the mean (a.k.a average) for the numbers in the given column of the given dataset or the mean of a series of numbers specified as arguments.

**Params:** dataset (Dataset): The dataset to use.; columnIndex (Integer): The index of the column to use. Must be a column index...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer/Float** - The mean of the values in that column. / **Integer/Float** - The mean of the values.

**Example:** `mean({Root Container.Table.data}, "Weight") //... would return 5.58675`

### median
*Category: Aggregates*  
`median(dataset, columnIndex) (index)`  
`median(dataset, columnName) (name)`  
`median(value[, value...]) (value)`  
`median(sequence) (sequence)`

Calculates the median for the numbers in the given column of the given dataset or the median of a series of numbers specified as arguments.

**Params:** dataset (Dataset): The dataset to search through.; columnIndex (Integer): The index of the column to search through. Must be a c...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer/Float** - The median value in that column. / **Integer/Float** - The median value in the list of values.

**Example:** `median({Root Container.Table.data}, "Weight") //... would return 5.566 median(1,2,3,3,10) //... would return 3`

### min
*Category: Aggregates*  
`min(dataset, columnIndex) (index)`  
`min(dataset, columnName) (name)`  
`min(value[, value...]) (value)`  
`min(sequence) (sequence)`

Finds and returns the minimum value in the given column of the given dataset, or the min value in a series of numbers specified as arguments.

**Params:** dataset (Dataset): The dataset to search through.; columnIndex (Integer): The index of the column to search through. Must be a c...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer** - The minimum value in that column. / **Integer** - The minimum value in the list of values.

**Example:** `min({Root Container.Table.data}, 1) //... would return 120`

### minDate
*Category: Aggregates*  
`minDate(dataset, columnIndex) (index)`  
`minDate(dataset, columnName) (name)`  
`minDate(date[, date]) (date)`

Finds and returns the minimum date in the given column of the given dataset, or the min value in a series of dates specified as arguments.

**Params:** dataset (Dataset): The starting dataset to search.; columnIndex (Integer): The index of the column to search for the min date. Mu...; columnName (String): The name of the column to search for the min date. Must ...; date (Date): A date. Can be as many dates as needed.

**Returns:** **Date** - The minimum date of the given date column in the given dataset. / **Date** - The minimum date of the given dates.

**Example:** `minDate({Root Container.Table.data}, "AlarmTime") //You could use this expression to get the date and time ...`

### stdDev
*Category: Aggregates*  
`stdDev(dataset, columnIndex) (index)`  
`stdDev(dataset, columnName) (name)`  
`stdDev(value, [value, ...]) (value)`  
`stdDev(sequence) (sequence)`

Calculates the sample standard deviation of the values in the given column of the given dataset, or the standard deviation for a series of numbers specified ...

**Params:** dataset (Dataset): The starting dataset to search.; columnIndex (Integer): The index of the column to search through. Must be a c...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer/Float** - The standard deviation of the values in that column. / **Integer/Float** - The standard deviation of the values in the list of values.

**Example:** `stdDev({Root Container.Table.data}, "Weight") //... would return 4.00532`

### sum
*Category: Aggregates*  
`sum(dataset, columnIndex) (index)`  
`sum(dataset, columnName) (name)`  
`sum(value, [value, ...]) (value)`  
`sum(sequence) (sequence)`

Calculates the sum of the values in the given column of the given dataset, or the sum for a series of numbers specified as arguments.

**Params:** dataset (Dataset): The dataset to use.; columnIndex (Integer): The index of the column to use. Must be a column index...; columnName (String): The name of the column to search through. Must match a c...; value (Integer/Float): A number. Can be as many values as needed. Can be eith...; sequence (Sequence): A list, tuple, array, or set of numerical values.

**Returns:** **Integer/Float** - The sum of the values in that column. / **Integer/Float** - The sum of the values.

**Example:** `sum({Root Container.Table.data}, 1) //... would return 947`

#### Alarming

### isAlarmActive
*Category: Alarming*  
`isAlarmActive(tagPath, [alarmName], [pollRate])`

Returns whether there are active alarms that match the provided criteria.

**Params:** tagPath (String): The Tag path to search for active alarms. Supports the wild...; alarmName (String): The name of the alarm to search for. Supports the wildcar...; pollRate (Integer): The poll rate in milliseconds. Only applicable in Vision ...

**Returns:** **Boolean** - True if an alarm is active, False if no active alarms were found.

**Example:** `isAlarmActive("[default]Tanks/Temp", "[default]Tank_Temp_High") //when the Tank_Temp_High alarm is active t...`

### isAlarmActiveFiltered
*Category: Alarming*  
`isAlarmActiveFiltered(tagPath, alarmName, displayPath, minPriority, maxPriority, allowCleared, allowAcked, allowShelved, [pollRate])`

Returns whether there are active alarms that match the provided criteria.

**Params:** tagPath (String): The tag path to search for active alarms. Accepts the wildc...; alarmName (String): The alarm name to search for active alarms. Accepts the w...; displayPath (String): The display path to search for active alarms. Accepts t...; minPriority (Integer): The minimum priority of alarms to accept. 0 is Diagnos...; maxPriority (Integer): The maximum priority of alarms to accept. 0 is Diagnos...; allowCleared (Boolean): A flag that indicates whether to accept cleared alarms.; allowAcked (Boolean): A flag that indicates whether to accept acknowledged al...; allowShelved (Boolean): A flag that indicates whether to accept shelved alarms.; pollRate (Integer): The poll rate of the function in milliseconds. Only appli...

**Returns:** **Boolean** - True if there are active alarms, False if there are not.

**Example:** `isAlarmActiveFiltered("*", "*", "*", 4, 4, 0, 1, 0) //when any critical alarm is active, even if acknowledg...`

#### Colors

### brighter
*Category: Colors*  
`brighter(color)`

Returns a color that is one shade brighter than the color given as an argument.

**Params:** color (Color): A color to make brighter. Can use the [color](appendix/express...

**Returns:** **Color** - A color that is one shade brighter than the color passed in.

**Example:** `brighter(color(100,150,250)) //returns the color (142,214,255)`

### color
*Category: Colors*  
`color(red, green, blue[, alpha])`

Creates a color using the given red, green, and blue amounts, which are integers between 0-255.

**Params:** red (Integer): The intensity of red, between 0 - 255.; green (Integer): The intensity of green, between 0 - 255.; blue (Integer): The intensity of blue, between 0 - 255.; alpha (Integer): The amount of transparency, between 0 - 255. [optional]

**Returns:** **Color** - Returns a color with the given RGB value.

**Note:** [note] This function was designed to return color objects to Vision bindings, and will not work with Perspective bindings. Instead, Perspective color properties can...

### darker
*Category: Colors*  
`darker(color)`

Returns a color that is one shade darker than the color given as an argument.

**Params:** color (Color): A color to make darker. Can use the [color](color.md) function...

**Returns:** **Color** - A color that is one shade darker than the color passed in.

**Example:** `darker(color(100,150,250)) //returns the color (70,105,175)`

### gradient
*Category: Colors*  
`gradient(value, low, high, lowColor, highColor)`

Calculates a percentage given the three numeric arguments number, low, and high.

**Params:** value (Integer): The value used to determine the percentage between the low a...; low (Integer): The low value to use to calculate the percentage.; high (Integer): The high value to use to calculate the percentage.; lowColow (Color): The color that will match 0%.; highColor (Color): The color that will match 100%.

**Returns:** **Color** - A color that is a mix of the two given colors based on the percentage.

**Example:** `gradient(0, 0, 100, toColor("red"), toColor("blue")) //returns red.`

#### Date and Time

### add*
*Category: Date and Time* — family: addMillis, addSeconds, addMinutes, addHours, addDays, addWeeks, addMonths, addYears  
`add*(date, value)`

Add or subtract an amount to a given date and time

**Params:** date (Date): The starting date.; value (Integer): The amount of units to change the date by, where the units d...

**Returns:** **Date** - A new date that has been adjusted by the specified amount.

**Example:** `addWeeks(now(), 2) //Adds 2 weeks to the current time`

### *Between
*Category: Date and Time* — family: millisBetween, secondsBetween, minutesBetween, hoursBetween, daysBetween, weeksBetween, monthsBetween, yearsBetween  
`*Between(date1, date2)`

Calculates the amount of time between two dates

**Params:** date1 (Date): The first date to compare.; date2 (Date): The second date to compare.

**Returns:** **Integer** - The number of units between the two dates. The units are determined by the specific function used.

**Example:** `daysBetween(toDate("2017-04-28 00:00:00"), toDate("2017-03-22 00:00:00")) //This will print -37.`

### dateArithmetic
*Category: Date and Time*  
`dateArithmetic(date, value, field)`

Adds or subtracts some amount of time from a date, returning the resulting date.

**Params:** date (Date): The starting date.; value (Integer): The amount to add or subtract from the given date.; field (String): The units of the value.

**Returns:** **Date** - A new date that has been altered by the specified amount of time units.

**Example:** `dateArithmetic(toDate("2010-01-04 8:00:00"), 5, "hour") //returns the date '2010-01-04 13:00:00'`

### dateDiff
*Category: Date and Time*  
`dateDiff(date1, date2, field)`

Calculates the difference between the two dates, returning the result as a floating point value in the units specified by field

**Params:** date1 (Date): The first date.; date2 (Date): The second date.; field (String): The units for the difference.

**Returns:** **Float** - The difference between the two dates in the units specified.

**Example:** `dateDiff(toDate("2008-2-24 8:00:00"), toDate("2008-2-24 8:15:30"), "minute") //returns 15.5`

### dateExtract
*Category: Date and Time*  
`dateExtract(date, field)`

Returns an integer value that is the value of the specified date field within the given date.

**Params:** date (Date): The given date to extract the field from.; field (String): The field to extract.

**Returns:** **Integer** - The value of the specified field within the given date. Note that months are zero-indexed, meaning January is 0, February i...

**Example:** `dateExtract(toDate("2003-9-14 8:00:00"), "year") //returns 2003`

**Note:** [note] Months are returned zero-indexed. That is, January is month 0, February is month 1, and so on. To get a month index starting at 1, simply add 1 to the functi...

### dateFormat
*Category: Date and Time*  
`dateFormat(date, pattern)`

Returns the given date as a string, formatted according to a pattern.

**Params:** date (Date): The starting date to format.; pattern (String): The pattern to format the given date.

**Returns:** **String** - The given date formatted according to the specified pattern.

**Example:** `dateFormat(toDate("2003-9-14 8:00:00"), "yyyy-MM-dd HH:mm:ss") //returns the string "2003-09-14 08:00:00" T...`

**Note:** [tip] Expert Tip This function uses the Java class java.text.SimpleDateFormat.

### dateIsAfter
*Category: Date and Time*  
`dateIsAfter(date1, date2)`

Compares two dates to see if date1 is after date2.

**Params:** date1 (Date): The first date to compare.; date2 (Date): The second date to compare.

**Returns:** **Boolean** - Returns true if date1 is after date2. Returns false if date1 is the same as or before date2.

**Example:** `dateIsAfter(now(), toDate("2016-04-12 00:00:00"))`

### dateIsBefore
*Category: Date and Time*  
`dateIsBefore(date1, date2)`

Compares two dates to see if date1 is before date2

**Params:** date1 (Date): The first date to compare.; date2 (Date): The second date to compare.

**Returns:** **Boolean** - Returns true if date1 is before date2. Returns false if date1 is the same as or after date2.

**Example:** `dateIsBefore(now(), toDate("2016-04-12 00:00:00"))`

### dateIsBetween
*Category: Date and Time*  
`dateIsBetween(targetDate, startDate, endDate)`

Compares two dates to see if a target date is between two other dates.

**Params:** targetDate (Date): The date to compare.; startDate (Date): The start of the date range.; endDate (Date): The end of the date range. This date must be after the start ...

**Returns:** **Boolean** - Returns true if the targetDate is between (or equal to) the startDate and endDate. Returns false otherwise.

**Example:** `dateIsBetween(now(), toDate("2016-06-12 00:00:00"), toDate("2016-06-19 00:00:00"))`

### dateIsDaylight
*Category: Date and Time*  
`dateIsDaylight([date])`

Checks to see if the current timezone is using daylight savings time during the date specified.

**Params:** date (Date): The date to use for the check. If omitted, the current date will...

**Returns:** **Boolean** - Returns true if the current time zone is using Daylight Saving Time during the specified date, or false otherwise.

**Example:** `dateIsDaylight(toDate("2007-06-28 00:00:00")) // Will return True in the US/Pacific Timezone, due to that t...`

### fromMillis
*Category: Date and Time*  
`fromMillis(millis)`

Creates a date object given a millisecond value.

**Params:** millis (Integer): The number of milliseconds since Unix epoch time (1 January...

**Returns:** **Date** - A date object representing the given number of milliseconds since epoch time.

**Example:** `fromMillis(1503092125000)//This example will print out the date "Fri Aug 18 14:35:25 PDT 2017"`

### get*
*Category: Date and Time* — family: getMillis, getSecond, getMinute, getHour12, getHour24, getDayOfWeek, getDayOfMonth, getDayOfYear, getMonth, getQuarter, getYear, getAMorPM  
`get*(date)`

Extracts a unit of time from a date

**Params:** date (Date): The date to extract from.

**Returns:** **Float** - The value of the specific unit of time extracted from the date. The unit is determined by the specific function used.

**Example:** `getMonth(now()) //This returns the current month.`

### getDate
*Category: Date and Time*  
`getDate(year, month, day)`

Creates a new Date object given a year, month and a day.

**Params:** year (Integer): The year to set for the date.; month (Integer): The month to set for the date. The month is zero-based, so J...; day (Integer): The day to set for the date. The day is one-based, so the firs...

**Returns:** **Date** - A date object created from the specified year, month, and day, with the time set to midnight of that day.

**Example:** `getDate(2016, 11, 1) //This example will create a new date object set to December 1st, 2016.`

### getTimezone
*Category: Date and Time*  
`getTimezone()`

Returns the ID of the current timezone depending on the scope in which it is called.

**Returns:** **String** - The ID of the current timezone.

### getTimezoneOffset
*Category: Date and Time*  
`getTimezoneOffset([date])`

Returns the current timezone's offset versus UTC for a given instant, taking Daylight Savings Time into account.

**Params:** date (Date): A specified date to compare the current timezone to UTC. If omit...

**Returns:** **Float** - The offset of the current timezone from UTC, considering Daylight Saving Time if applicable.

**Example:** `getTimezoneOffset(getDate(2017, 1, 22)) //Returns -8.0, if you are in Pacific Time.`

### getTimezoneRawOffset
*Category: Date and Time*  
`getTimezoneRawOffset()`

Returns the current timezone offset versus UTC, not taking daylight savings into account.

**Returns:** **Float** - The offset of the current timezone from UTC, without considering Daylight Saving Time.

**Example:** `getTimezoneRawOffset() //Returns -8.0 if you are in the Pacific Timezone, regardless of time of year.`

### midnight
*Category: Date and Time*  
`midnight(date)`

Returns a copy of a date with the hour, minute, second, and millisecond fields set to zero.

**Params:** date (Date): The date to set to midnight.

**Returns:** **Date** - A new date with the hour, minute, second, and millisecond fields set to zero.

**Example:** `midnight(now()) //This will take the current date and set the time to midnight`

### now
*Category: Date and Time*  
`now([pollRate])`

Returns the current time.

**Params:** pollRate (Integer): The poll rate in milliseconds to update the time. Default...

**Returns:** **Date** - The current time, based on the host computer's system clock. If a poll rate is specified, the returned time will update at the...

**Example:** `now() //Returns the current time, updates every second.`

### setTime
*Category: Date and Time*  
`setTime(date, hour, minute, second)`

Takes in a date, and returns a copy of it with the time fields set as specified.

**Params:** date (Date): A starting date.; hour (Integer): The value to set the hour field to.; minute (Integer): The value to set the minute field to.; second (Integer): The value to set the second field to.

**Returns:** **Date** - A new date with the time fields set as specified. The millisecond field is not preserved.

**Example:** `setTime({Root Container.Calendar.date}, 1, 37, 44) //This example will set the date object to the current d...`

### timeBetween
*Category: Date and Time*  
`timeBetween(date, startDate, endDate)`

Checks to see if the given time is between the start and end times.

**Params:** date (Date/String): The date or time to compare. Can be a Date object or a st...; startDate (Date/String): The start date or time. Can be a Date object or a st...; endDate (Date/String): The end date or time. Can be a Date object or a string.

**Returns:** **Boolean** - Returns true if the given date or time is between the startDate and endDate, or false if it is not.

**Example:** `timeBetween(toDate("2003-9-14 12:00:00"), toDate("2003-9-14 8:00:00"),toDate("2003-9-14 18:00:00")) //Retur...`

**Note:** [note] Dates will be parsed according to the default system culture.

### toMillis
*Category: Date and Time*  
`toMillis(date)`

Converts a Date object to its millisecond value elapsed since January 1, 1970, 00:00:00 UTC (GMT)

**Params:** date (Date): The date to convert to milliseconds since epoch time.

**Returns:** **Integer** - The number of milliseconds since January 1, 1970, 00:00:00 UTC (GMT) for the given date.

**Example:** `toMillis(setTime(getDate(2017, 6, 22), 16, 45, 34))`

#### Identity Provider

### containsAll
*Category: Identity Provider*  
`containsAll(collection, element0, [elementN])`

This function checks to see if all of the listed elements are present in the collection object. Requires at least a collection and one element.

**Params:** collection (Object): A collection of values. Typically from the `{security-zo...; element (String): One or more comma-separated elements to look for in the col...

**Returns:** **Boolean** - Returns true if the collection contains all of the listed elements, or false otherwise.

**Example:** `containsAll({attribute-source:idTokenClaims:roles}, 'Administrator', 'Operator')`

**Note:** [note] This function is only available for Security Level Rules and User Attribute Mapping.

### containsAny
*Category: Identity Provider*  
`containsAny(collection, element0, [elementN])`

This function checks to see if any of the listed elements are present in the collection object. Requires at least a collection and one element.

**Params:** collection (Object): A collection of values. Typically from the `{security-zo...; element (String): One or more comma-separated elements to look for in the col...

**Returns:** **Boolean** - Returns true if the collection contains any of the listed elements, or false otherwise.

**Example:** `containsAny({attribute-source:idTokenClaims:roles}, 'Administrator', 'Operator')`

**Note:** [note] This function is only available for Security Level Rules and User Attribute Mapping.

#### JSON

### jsonFormat
*Category: JSON*  
`jsonFormat(string)`

Takes a string, and returns a prettyprints string

**Params:** string (String): The string to format. The string must be in a JSON-friendly ...

**Returns:** **String** - A prettyprint string of the specified string.

**Example:** `jsonFormat("{item1:10,item2:20}")`

### jsonGet
*Category: JSON*  
`jsonGet(json, path)`

Takes a JSON friendly string and a path string, and returns the value of that path.

**Params:** json (String): The JSON string. The string must be in a JSON-friendly format.; path (String): The path to look for in the JSON string.

**Returns:** **Object** - The value at the path.

**Example:** `jsonGet("{'item':{'firstThing':1, 'secondThing':2}}", "item.secondThing")`

### jsonSet
*Category: JSON*  
`jsonSet(json, path, value)`

Takes a JSON friendly string, a path string, and value, and will return a new JSON friendly string with the provided path set to the provided value.

**Params:** json (String): The JSON string. The string must be in a JSON friendly format.; path (String): The path string.; value (Object): The replacement for the value at the path.

**Returns:** **String** - A JSON friendly string with a new value set at the specified path.

**Example:** `jsonSet("{'item':{'firstThing':1, 'secondThing':2}}", "item.secondThing", 5)`

#### Logic

### binEnc
*Category: Logic*  
`binEnc(value, [value, ...])`

Takes a list of booleans and treats them like the bits in a binary number.

**Params:** value (Boolean): A value that represents a bit. Each argument can be either 0...

**Returns:** Integer - integer representation when ≤32 args; Long - when 33-64 args.

**Example:** `binEnc(0,0,1,0) //returns 4 (the value of 0100)`

### binEnum
*Category: Logic*  
`binEnum(value, [value, ...])`

Takes a list of booleans, and returns the index (starting at 1) of the first parameter that evaluates to true.

**Params:** value (Boolean): A value that represents a bit. Each argument can be either `...

**Returns:** **Integer** - The index (starting at 1) of the first value that evaluates to true. If no value evaluates to true, the result is 0.

**Example:** `binEnum(0, 1, 0) //returns 2`

### case
*Category: Logic*  
`case(value, case, return[, case, return...], returnDefault)`

This function acts like the switch statement in C-like programming languages (order differs from switch()).

**Params:** value (Object): The value to compare against each case.; case (Object): A case to match the `value` to.; return (Object): The value to return if the corresponding `case` is matched.; returnDefault (Object): The default return value if no `case` arguments are m...

**Returns:** **Object** - The return value for the matched case, or the returnDefault value if no case was matched.

**Example:** `case(15, /*value*/ 1, 44, /*case1,ret1*/ 24, 45, /*case2,ret2*/ 15, 46, /*case3,ret3*/ -1) //returns 46`

### coalesce
*Category: Logic*  
`coalesce(value, [value, ...])`

Evaluates any number of arguments in order, and returns the first non-null argument.

**Params:** value (Object): Any number of values to evaluate in order.

**Returns:** **Object** - The first non-null argument. If all arguments are null, the result is null.

**Example:** `coalesce(null, "abc") //would return "abc"`

### getBit
*Category: Logic*  
`getBit(number, position)`

Returns the bit value (0 or 1) in the number at position, according to its binary representation.

**Params:** number (Integer): The number whose binary representation will be checked.; position (Integer): The bit position to evaluate, where 0 is the least signif...

**Returns:** **Integer** - Returns 0 or 1, depending on the bit value at the specified position.

**Example:** `getBit(0,0) //would return 0`

### hasChanged
*Category: Logic*  
`hasChanged(value, [includeQuality], [pollRate])`

Returns true if the given value has changed since the last time the Expression Item was run.

**Params:** value (Object): The value to check for changes.; includeQuality (Boolean): A flag that indicates if a quality change will also...; pollRate (Integer): The poll rate in milliseconds. Only applicable on Express...

**Returns:** **Boolean** - Returns true if the value has changed since the last evaluation, or false otherwise.

**Example:** `hasChanged({[default]Station 1/Status},True)`

**Note:** [note] Only available in Transaction Group Expression Items and Expression Tags; measures change since last group execution.

### if
*Category: Logic*  
`if(condition, trueReturn, falseReturn)`

Evaluates condition, and returns trueReturn or falseReturn depending on the boolean value of condition.

**Params:** condition (Boolean): A boolean expression that determines which return value ...; trueReturn (Object): The value returned if the condition evaluates to true.; falseReturn (Object): The value returned if the condition evaluates to false.

**Returns:** **Object** - Returns the trueReturn value if the condition is true, or the falseReturn value if the condition is false.

**Example:** `if(1, "Yes", "No") //would return "Yes"`

### indexOf
*Category: Logic*  
`indexOf(string, substring)`

Searches for the first occurrence of substring inside string; returns the index found, or -1 if not found.

**Params:** string (String or List): The string to search through. This parameter also ac...; substring (String): The string to search for.

**Returns:** **Integer** - The index where the substring was first found in the string. Returns -1 if the substring is not found.

**Example:** `indexOf("Hamburger", "urge") //Returns 4.`

### isBad
*Category: Logic*  
`isBad(value)`

Tests to see whether or not the given value's quality is bad.

**Params:** value (Object): A value to check if its quality is bad.

**Returns:** **Boolean** - Returns true if the value's quality is bad, or false if it is not.

**Example:** `isBad({path/to/myTag}) //Returns True if the value's quality is bad, False otherwise.`

### isBadOrError
*Category: Logic*  
`isBadOrError(value)`

Tests to see whether or not the given value's quality is either bad or error.

**Params:** value (Object): A value to check if its quality is either bad or error.

**Returns:** **Boolean** - Returns true if the value's quality is either bad or error, or false if it is not.

**Example:** `isBadOrError({path/to/myTag}) //Returns 1 if the value's quality is bad or error, 0 otherwise.`

### isError
*Category: Logic*  
`isError(value)`

Tests to see whether or not the given value's quality is error.

**Params:** value (Object): A value to check if its quality is error.

**Returns:** **Boolean** - Returns `true` if the value's quality is error, or `false` if it is not.

**Example:** `isError({path/to/myTag}) //Returns True if the value's quality is error, False otherwise.`

### isGood
*Category: Logic*  
`isGood(value)`

Tests to see whether or not the given value is good quality.

**Params:** value (Object): A value to check if its quality is good.

**Returns:** **Boolean** - Returns true if the value's quality is good, or false if it is not.

**Example:** `isGood({path/to/myTag}) //Returns True if the value's quality is good, False otherwise.`

### isNull
*Category: Logic*  
`isNull(value)`

Tests to see whether or not the argument value is null

**Params:** value (Object): A value to check if it is null.

**Returns:** **Boolean** - Returns true if the value is null, or false if it is not.

**Example:** `if(isNull({Root Container.MyProperty}), "Value is Null", {Root Container.MyProperty})`

### isUncertain
*Category: Logic*  
`isUncertain(value)`

Tests to see whether or not the given value's quality is Uncertain.

**Params:** value (Object): A value to check if its quality is uncertain.

**Returns:** **Boolean** - Returns true if the value's quality is uncertain, or false if it is not.

**Example:** `isUncertain({path/to/myTag}) //Returns True if the value's quality is uncertain, False otherwise.`

### lastIndexOf
*Category: Logic*  
`lastIndexOf(string, substring)`

Searches for the last occurrence of the substring inside of string.

**Params:** string (String or List): The string to search through. This parameter also ac...; substring (String): The string to search for.

**Returns:** **Integer** - The index where the substring was last found in the string. Returns -1 if the substring is not found.

**Example:** `lastIndexOf("Hamburger", "urge") //Returns 4.`

### len
*Category: Logic*  
`len(value)`

Returns the length of the argument, which may be a string or a dataset.

**Params:** value (Object): The object whose length is being evaluated.

**Returns:** **Integer** - The length of the provided object (number of characters, rows, or elements depending on the type).

**Example:** `len("Hello World") //Returns 11.`

### lookup
*Category: Logic*  
`lookup(dataset, lookupValue, noMatchValue, [lookupColumn], [resultColumn])`

Looks for lookupValue in the lookupColumn of dataset and returns the value from resultColumn.

**Params:** dataset (Dataset): A dataset to search through.; lookupValue (Object): The value to look for in the dataset.; noMatchValue (Object): The value to return if no match is found.; lookupColumn (Object): The column to search for the lookup value. Can be the ...; resultColumn (Object): The column to retrieve the result value from. Can be t...

**Returns:** **Object** - The value in the result column of the same row where the lookupValue was found, or the noMatchValue if no match was found.

**Example:** `lookup({Root Container.Table.data}, "Carrots", -1.0) //returns 3.50`

**Note:** [note] The type of the value returned will always be coerced to be the same type as the noMatchValue.

### switch
*Category: Logic*  
`switch(value, case, [caseN, ...], return, [returnN, ...], returnDefault)`

This function acts like the switch statement in C-like programming languages.

**Params:** value (Object): The value to check against the case values.; case (Object): A value to check against. Can include any number of case values.; return (Object): A value to return for the matching case. Must match the numb...; returnDefault (Object): The default value to return if no case is matched.

**Returns:** **Object** - The return value for the case that matched the value, or the returnDefault value if no matches were found.

**Example:** `switch(15, /*value*/ 1, 24, 15, /*cases*/ 44, 45, 46, /*returns*/ -1) //returns 46`

### try
*Category: Logic*  
`try(expression, failover)`

Used to swallow errors caused by other expressions.

**Params:** expression (Object): An expression that can evaluate to any supported data type.; failover (Object): The value to return if an error occurs while evaluating **...

**Returns:** **Object** - The result of the evaluated expression, or the failover value if an error occurs.

**Example:** `try(toInteger("boom"), -1) // returns -1 with a quality code of 192 (good)`

#### Math

### abs
*Category: Math*  
`abs(number)`

Returns the absolute value of number.

**Params:** number (Integer/Float): The number to get the absolute value of.

**Returns:** **Integer/Float** - The absolute value of the number provided.

**Example:** `abs(-4) //returns 4`

### acos
*Category: Math*  
`acos(number)`

Returns the arc cosine of number

**Params:** number (Float): The number to get the arc cosine of. Must be a value between ...

**Returns:** **Float** - The arc cosine of the value provided.

**Example:** `acos(.38) //returns 1.181`

### asin
*Category: Math*  
`asin(number)`

Returns the arc sine of number

**Params:** number (Float): The number to get the arc sine of. Must be a value between -1...

**Returns:** **Float** - The arc sine of the value provided.

**Example:** `asin(.38) //returns 0.3898`

### atan
*Category: Math*  
`atan(number)`

Returns the arc tangent of number

**Params:** number (Float): The number to get the arc tangent of.

**Returns:** **Float** - The arc tangent of the value provided.

**Example:** `atan(.38) //returns 0.3631`

### ceil
*Category: Math*  
`ceil(number)`

Returns the smallest floating point value that is ≥ the argument and equal to a mathematical integer.

**Params:** number (Float): The number to get the ceiling of.

**Returns:** **Float** - The ceiling of the value provided.

**Example:** `ceil(2.38) //returns 3.0`

### cos
*Category: Math*  
`cos(number)`

Returns the trigonometric cosine of number

**Params:** number (Integer/Float): The number to get the cosine of.

**Returns:** **Float** - The cosine of the number provided.

**Example:** `cos(1.89) //returns -0.31381`

### exp
*Category: Math*  
`exp(number)`

Returns Euler's number e raised to the power of the argument number.

**Params:** number (Integer/Float): The exponent value to raise e to the power of.

**Returns:** **Integer/Float** - The value of e to the power of the value provided.

**Example:** `exp(5) //returns 148.4`

### floor
*Category: Math*  
`floor(number)`

Returns the largest floating point value that is ≤ the argument and equal to a mathematical integer.

**Params:** number (Float): The number to get the floor of.

**Returns:** **Float** - The floor of the number provided.

**Example:** `floor(2.72) //returns 2.0`

### log
*Category: Math*  
`log(number)`

Returns the natural logarithm (base e) of a number.

**Params:** number (Integer/Float): The number to get the log of.

**Returns:** **Float** - The log of the number provided.

**Example:** `log(28) //returns 3.332`

### log10
*Category: Math*  
`log10(number)`

Returns the logarithm (base 10) of a number.

**Params:** number (Integer/Float): The number to get the log base 10 of.

**Returns:** **Float** - The log base 10 of the number provided.

**Example:** `log10(28) // returns 1.447`

### pow
*Category: Math*  
`pow(number, power)`

Returns a number raised to a power.

**Params:** number (Integer/Float): The number to raise to the provided power.; power (Integer/Float): The power value to raise the number value to.

**Returns:** **Integer/Float** - The result of the number provided raised to the power provided.

**Example:** `pow(2,3) //returns 8`

### round
*Category: Math*  
`round(number, [decimals])`

Rounds a floating point number.

**Params:** number (Float): The number to round.; decimals (Integer): The number of decimal places to round to. Defaults to 0. ...

**Returns:** **Integer/Float** - The value provided rounded to the specified decimal places.

**Example:** `round(3.829839, 2) //returns 3.83`

### sin
*Category: Math*  
`sin(number)`

Returns the trigonometric sine of a number

**Params:** number (Integer/Float): The number to get the sine of.

**Returns:** **Integer/Float** - The sine of the number provided.

**Example:** `sin(1.89) //returns 0.9495`

### sqrt
*Category: Math*  
`sqrt(number)`

Returns the square root of the argument number

**Params:** number (Integer/Float): The number to get the square root of.

**Returns:** **Float** - The square root of the number provided.

**Example:** `sqrt(64) //returns 8.0`

### tan
*Category: Math*  
`tan(number)`

Returns the trigonometric tangent of a number

**Params:** number (Integer/Float): The number to get the tangent of.

**Returns:** **Float** - The tangent of the number provided.

**Example:** `tan(1.89) //returns -3.026`

### todegrees
*Category: Math*  
`todegrees(number)`

Converts an angle measured in radians to an equivalent angle measured in degrees

**Params:** number (Integer/Float): The number of radians.

**Returns:** **Integer/Float** - The degree equivalent of the radians provided.

**Example:** `todegrees(3.14) //returns 179.9088`

### toradians
*Category: Math*  
`toradians(number)`

Converts an angle measured in degrees to an equivalent angle measured in radians

**Params:** number (Integer/Float): The number of degrees.

**Returns:** **Integer/Float** - The radian equivalent of the degrees provided.

**Example:** `toradians(180) //returns 3.141592653589793`

#### MongoDB

### maxKey
*Category: MongoDB*  
`maxKey()`

Returns org.bson.types.MaxKey, used in filters for the MongoDB Perspective binding expression.

**Returns:** **MaxKey** - A special data type that will match with document fields of the same MaxKey type.

**Example:** `maxKey() // binding will return entire document(s) where maxKey is found`

### minKey
*Category: MongoDB*  
`minKey()`

Returns org.bson.types.MinKey, used in filters for the MongoDB Perspective binding expression.

**Returns:** **MinKey** - A special data type that will match with document fields of the same MinKey type.

**Example:** `minKey() // binding will return entire document(s) where minKey is found`

### toObjectId
*Category: MongoDB*  
`toObjectId(stringId)`

Converts String to org.bson.types.ObjectId.

**Params:** stringId (String): A unique, 24 character string identifier that matches with...

**Returns:** **ObjectId** - A unique, 12 byte identifier that matches with an id of an existing document of a collection in both value and data type.

**Example:** `toObjectId("5553a998e4b02cf7151190b8") // binding will return entire document of the matching _id`

#### String

### char
*Category: String*  
`char(code)`

Takes a Unicode character code (as an integer), and returns the Unicode character as a string.

**Params:** code (Integer): The character code for a Unicode character.

**Returns:** **String** - The corresponding Unicode character, as a one-character string.

**Example:** `char(88) //Returns "X".`

**Note:** [note] This function can work for ASCII conversions as well, since Unicode and ASCII character codes match for all ASCII characters.

### concat
*Category: String*  
`concat(string, [string, ...])`

Concatenates all of the strings passed in as arguments together.

**Params:** string (String): Any number of string values to concatenate together.

**Returns:** **String** - A string that is all of the strings provided concatenated together.

**Example:** `concat("The answer is: ", "42") //returns "The answer is: 42"`

### escapeSQL
*Category: String*  
`escapeSQL(string)`

Returns the given string with special SQL characters escaped.

**Params:** string (String): The starting string.

**Returns:** **String** - A string with single quotes replaced by two single quotes, and backslashes escaped.

**Example:** `"SELECT * FROM mytable WHERE option = '" + escapeSQL("Jim's Settings") + "'"`

### escapeXML
*Category: String*  
`escapeXML(string)`

Returns the given string after being escaped to be valid for inclusion in XML.

**Params:** string (String): The starting string.

**Returns:** **String** - A string that has been escaped for XML.

**Example:** `escapeXML("Use Navigate > PB to get to the Pork&Beans section.")`

### fromBinary
*Category: String*  
`fromBinary(string)`

Returns an integer value of the binary formatted string argument.

**Params:** string (String): A string representation of a binary.

**Returns:** **Integer** - The integer value of the specified binary.

**Example:** `fromBinary("1111") //returns 15`

### fromHex
*Category: String*  
`fromHex(string)`

Returns an integer value of the hex formatted string argument.

**Params:** string (String): A string representation of a hex value.

**Returns:** **Integer** - The integer of the hex value.

**Example:** `fromHex("ff") //returns 255`

### fromOctal
*Category: String*  
`fromOctal(string)`

Returns an integer value of the octal formatted string argument.

**Params:** string (String): A string representation of an octal.

**Returns:** **Integer** - The integer of the octal value.

**Example:** `fromOctal("77") //returns 63`

### left
*Category: String*  
`left(string, charCount)`

Returns count characters from the left side of string.

**Params:** string (String): The starting string.; charCount (Integer): The number of characters to return.

**Returns:** **String** - A string that is the first charCount number of characters of the specified string.

**Example:** `left("hello", 2) //returns "he"`

### lower
*Category: String*  
`lower(string)`

Takes a string and returns a lower-case version of it.

**Params:** string (String): The string to make lowercase.

**Returns:** **String** - The starting string with all characters lowercase.

**Example:** `lower("Hello World") // returns "hello world"`

### numberFormat
*Category: String*  
`numberFormat(number, pattern)`

Returns a string version of the number argument, formatted as specified by the pattern string.

**Params:** number (Float): The number to format.; pattern (String): The format pattern (see Number Format Reference).

**Returns:** **String** - The string representation of the number formatted according to the pattern provided.

**Example:** `numberFormat(34.8, "#0.00'%'") //returns the string "34.80%"`

### ordinal
*Category: String*  
`ordinal(string)`

Takes a Unicode character (as a string), and returns the corresponding character code, as an integer.

**Params:** string (String): A string containing a single Unicode character.

**Returns:** **Integer** - The character code associated with the Unicode character.

**Example:** `ordinal("a") //Returns 97.`

**Note:** [note] This function can work for ASCII conversions as well, since Unicode and ASCII character codes match for all ASCII characters.

### repeat
*Category: String*  
`repeat(string, count)`

Repeats the given string some number of times.

**Params:** string (String): The string to repeat.; count (Integer): The number of times to repeat the string.

**Returns:** **String** - The given string repeated the given number of times.

**Example:** `repeat("hello", 2) //returns "hellohello"`

### replace
*Category: String*  
`replace(string, substring, replacementString)`

Finds all occurrences of a substring inside of a source string, and replaces them with the replacement string.

**Params:** string (String): The starting string.; substring (String): The string to search for.; replacementString (String): The string to replace any instances of the substr...

**Returns:** **String** - The starting string with all instances of the substring replaced by the replacementString.

**Example:** `replace("XYZ", "Y", "and") //returns "XandZ"`

### right
*Category: String*  
`right(string, charCount)`

Returns count number of characters starting from the right side of string.

**Params:** string (String): The starting string.; charCount (String): The number of characters to return.

**Returns:** **String** - A string of the number of characters specified in the charCount from the specified string.

**Example:** `right("hello", 2) //returns "lo"`

### split
*Category: String*  
`split(string, regex, [limit])`

Takes the starting string and splits it into substrings

**Params:** string (String): The starting string.; regex (String): The string to split on.; limit (Integer): Optional. The max number of splits to make. Default 0.

**Returns:** **Dataset** - The split string, with a single column called parts, where each row is a new part of the string.

**Example:** `split("hello,world", ",") //returns dataset ["hello", "world"]`

### stringFormat
*Category: String*  
`stringFormat(format, [args, ...])`

Returns a formatted string using the specified format string and arguments; used for building dynamic string objects.

**Params:** format (String): A string that contains formatting elements in it (%s, %d, %i).; args (String): The arguments to use in the format. Must match the number of f...

**Returns:** **String** - The new formatted string.

**Example:** `stringFormat("The boolean value is: %b", null) //Returns The boolean value is: False.`

### substring
*Category: String*  
`substring(string, startIndex[, endIndex])`

Returns the portion of the string from the startIndex to the endIndex, or end of the string if endIndex is not specified

**Params:** string (String): The starting string.; startIndex (Integer): The index to start the substring at.; endIndex (Integer): Optional. The end index of the substring.

**Returns:** **String** - The substring from the start to end indexes of the specified string.

**Example:** `substring("unhappy", 2) //returns "happy"`

### toBinary
*Category: String*  
`toBinary(number)`

Returns a binary formatted string representing the unsigned integer argument.

**Params:** number (Integer): The value to convert to binary.

**Returns:** **String** - The string form of the binary representation of the specified number.

**Example:** `toBinary(255) //returns "11111111"`

### toHex
*Category: String*  
`toHex(number)`

Returns a hex formatted string representing the unsigned integer argument (also accepts a Color).

**Params:** number (Integer): The number to convert to hex.

**Returns:** **String** - A string that is the hex value of the specified value.

**Example:** `toHex(255) //returns "FF"`

### toOctal
*Category: String*  
`toOctal(number)`

Returns an octal formatted string representing the unsigned integer argument.

**Params:** number (Integer): The value to convert to octal.

**Returns:** **String** - A string that is the octal of the specified value.

**Example:** `toOctal(255) //returns "377"`

### trim
*Category: String*  
`trim(string)`

Trims any leading and/or trailing whitespace from string.

**Params:** string (String): The starting string.

**Returns:** **String** - The starting string with leading/trailing whitespace removed.

**Example:** `trim("Hello Dave ") //returns "Hello Dave"`

### upper
*Category: String*  
`upper(string)`

Takes a string and returns an uppercase version of it.

**Params:** string (String): The string to make uppercase.

**Returns:** **String** - The starting string with all characters uppercase.

**Example:** `upper("Hello World") //returns "HELLO WORLD"`

### urlEncode
*Category: String*  
`urlEncode(string, [usePercentEscape])`

Enables users to create an HTTP binding's URL on the fly.

**Params:** url (String): The URL to encode.; usePercentEscape (Boolean): False or blank indicates to use query parameter s...

**Returns:** **String** - The encoded URL.

**Example:** `urlEncode("Hello World") //Yields "Hello+World".`

#### Translation

### translate
*Category: Translation*  
`translate(stringKey, [languageString])`

Returns a translated string, based on the current locale.

**Params:** stringKey (String): The starting string to translate.; languageString (String): The language or locale to translate against, such as...

**Returns:** **String** - The starting string translated based on the specified locale, or the current locale if none was given. If the translation do...

#### Type Casting

### toBoolean
*Category: Type Casting*  
`toBoolean(value[, failover])`

Tries to convert value to a boolean

**Params:** value (object): The value to type cast.; failover (object): The failover value if type casting fails. [optional]

**Returns:** **Bool** - The value type cast as a bool.

**Example:** `toBoolean(1) //returns true`

### toBorder
*Category: Type Casting*  
`toBorder(value, [failover])`

Used specifically when binding a Border property on a component (typically Container or Label).

**Params:** value (String): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Border** - The value type cast as a border object.

**Example:** `toBorder("paneltitled; title; style; mainColor; bgColor; shadowSize; fontJustification; fontPosition; fontC...`

**Note:** [info] Be Mindful of Style Configurations: use of toBorder can conflict with Styles configured on the component.

### toColor
*Category: Type Casting*  
`toColor(value, [failover])`

Tries to convert value to a color from a name, hex string, or list of 3-4 RGB(A) integers.

**Params:** value (String): The color value as a string.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Color** - The value type cast as a color object.

**Example:** `toColor("red") toColor("#FF0000") toColor("255,0,0")`

**Note:** [note] Designed to return color objects to Vision bindings; will not work with Perspective bindings, which should use hex string colors directly. [note] Both 'Grey' and 'Gray' spellings (and their compounds) are accepted.

### toDataSet
*Category: Type Casting*  
`toDataSet(value[, failover])`

Tries to coerce value into a dataset.

**Params:** value (Object): The value to type cast, typically a DataSet or PyDataSet.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Dataset** - The value type cast as a dataset.

**Example:** `toDataSet(runScript("app.funcs.runSomeFunction()")) //coerces the value returned by a project scripting fun...`

### toDate
*Category: Type Casting*  
`toDate(value, [failover])`

Tries to coerce value into a Date.

**Params:** value (Object): The value to type cast into a date.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Date** - The value type cast as a date.

**Example:** `toDate("2007-04-12 16:28:22") //returns April 12th, 2007, 4:28:22 PM`

### toDouble
*Category: Type Casting*  
`toDouble(value, [failover])`

Tries to coerce value into a double (64-bit floating point value).

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Double** - The value type cast as a double.

**Example:** `toDouble("38.772") //returns 38.772`

### toFloat
*Category: Type Casting*  
`toFloat(value[, failover])`

Tries to coerce value into a float (32-bit floating point value).

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Float** - The value type cast as a float.

**Example:** `toFloat("38.772") //returns 38.772`

### toFont
*Category: Type Casting*  
`toFont(value, [failover])`

Coerces a string into a font.

**Params:** value (String): The value to type cast to a font.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Font** - The value type cast as a font.

**Example:** `toFont("font(Dialog,Bold,12)") //returns the standard font used in most clients.`

### toInt
*Category: Type Casting*  
`toInt(value, [failover])`

Tries to coerce value into an integer (32-bit integer).

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Integer** - The value type cast as an int.

**Example:** `toInt("38") //returns 38`

### toInteger
*Category: Type Casting*  
`toInteger(value, [failover])`

Identical to the toInt expression function.

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Integer** - The value type cast as an int.

**Example:** `toInteger("38") //returns 38`

### toLong
*Category: Type Casting*  
`toLong(value, [failover])`

Tries to coerce value into a long (64-bit integer).

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **Long** - The value type cast as a long.

**Example:** `toLong("38") //returns 38`

### toStr
*Category: Type Casting*  
`toStr(value, [failover])`

Identical to the toString expression function.

**Params:** value (Object): The value to type cast, typically a DataSet or PyDataSet.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **String** - The value type cast as a string.

**Example:** `toStr(1/3.0) // returns "0.3333333333333333"`

### toString
*Category: Type Casting*  
`toString(value, [failover])`

Represents the value as a string. Will succeed for any type of value.

**Params:** value (Object): The value to type cast.; failover (Object): The failover value if type casting fails. [optional]

**Returns:** **String** - The value type cast as a string.

**Example:** `toString(1/3.0) // returns "0.3333333333333333"`

#### Users

### hasRole
*Category: Users*  
`hasRole(role[, username][, usersource])`

Returns true if the user has the given role. username and usersource are optional in Client scope, required in Gateway scope.

**Params:** role (String): The name of a role.; username (String): A username. Defaults to the current user. [optional]; usersource (String): The usersource of the username. Defaults to the usersour...

**Returns:** **Boolean** - True if the specified user has the specified role, False if not.

**Example:** `hasRole("Administrator")`

**Note:** [note] When using Perspective, all parameters are required since it's in the Gateway scope; for some apps prefer isAuthorized() instead.

### isAuthorized
*Category: Users*  
`isAuthorized(isAllOf, securityLevel[, securityLevelN...])`

Returns a qualified boolean true if the user in the current Session is authorized against the given security level path(s).

**Params:** isAllOf (Boolean): True if the current user must have all of the given securi...; securityLevel (String): One or more String paths, represented by `securityLev...

**Returns:** **Boolean** - True if the user is authorized (per isAllOf semantics), false otherwise.

**Example:** `isAuthorized(true, 'Authenticated/Roles/Administrator', 'Foo/Bar/Baz')`

## Date/number format strings

Source: `appendix/reference-pages/data-type-formatting-reference`.

#### Date format (used by `dateFormat`, `system.date.format`, `system.dataset.formatDates`)

Pattern placeholders are case-sensitive and repeatable for different verbosity (`M`→1-12, `MM`→01-12, `MMM`→Jan-Dec, `MMMM`→January-December). Backed by Java's `SimpleDateFormat`.

| Symbol | Meaning | Example |
|---|---|---|
| `a` | AM/PM marker | `PM` |
| `D` | Day in year | `189` |
| `d` | Day in month | `10` |
| `E` | Day name in week | `EEEE=Tuesday; E=Tue` |
| `F` | Day of week in month | `2` (2nd Sunday) |
| `G` | Era designator | `AD` |
| `H` | Hour in day (0-23) | `0` |
| `h` | Hour in am/pm (1-12) | `12` |
| `k` | Hour in day (1-24) | `24` |
| `K` | Hour in am/pm (0-11) | `0` |
| `M` | Month in year | `MMMM=July; MMM=Jul; MM=07` |
| `m` | Minute in hour | `30` |
| `s` | Second in minute | `55` |
| `S` | Millisecond | `978` |
| `u` | Day number of week | `1` (1=Mon...7=Sun) |
| `w` | Week in year | `27` |
| `W` | Week in month | `2` |
| `X` | Time zone (ISO 8601) | `X=-08; XX=-0800; XXX=-08:00` |
| `y` | Year | `yyyy=1996; yy=96` |
| `Y` | Week year | `YYYY=2009` (week-based year) |
| `z` | Time zone (general) | `zzzz=Pacific Standard Time; z=PST` |
| `Z` | Time zone (RFC 822) | `-0800` |

#### Number format (used by `numberFormat`)

Backed by Java's `DecimalFormat`.

| Symbol | Meaning |
|---|---|
| `0` | Required digit |
| `#` | Optional digit |
| `,` | Grouping separator |
| `.` | Decimal separator |
| `-` | Minus sign |
| `E` | Scientific notation |
| `;` | Separates positive/negative subpatterns |
| `%` | ×100 and show as percent |
| `'` | Quotes literal characters |

Examples: `5` with `00.0` → `05.0`; `1337.57` with `#,##0.#` → `1,337.6`; `-1234` with `#,##0;(#)` → `(1,234)`; `4096` with `0.###E0` → `4.096E3`; `.348` with `#.00%` → `34.80%`; `34.8` with `#0.00'%'` → `34.80%`.

#### String format (used by `stringFormat`)

Date/time element suffixes: `H`/`I` hour (24h/12h, 2-digit), `k`/`k` hour (24h/12h, unpadded — note the docs list both as `k`), `m` minute, `S` seconds, `L` millisecond, `B`/`b` full/abbreviated month name, `A`/`a` full/abbreviated weekday name, `Y`/`y` 4-digit/2-digit year, `j` day-of-year, `M` month (2-digit), `d`/`e` day-of-month (2-digit/unpadded).

Conversion characters: `b`/`B` boolean (null → `False`), `s`/`S` string, `c`/`C` unicode character, `d` integer, `f` floating point, `t`/`T` date/time prefix.

## Cron syntax

Source: `appendix/reference-pages/crontab-formatting-reference`. Used by Gateway scheduled backups, Gateway Scheduled Scripts, and Report schedules.

```
* * * * *
| | | | |
| | | | ----day of the week   (0-6, 0=Sunday)
| | | ----month                (1-12)
| | ----day of the month        (1-31)
| ----hour                       (0-23)
----minute                        (0-59)
```

| Character | Meaning | Example |
|---|---|---|
| `*` | Any value | `* 2 * * *` — every minute from 2:00-2:59 AM |
| `,` | List of values | `0,25 * * * *` — top of every hour and at :25 |
| `-` | Range | `0-6 2 * * *` — every minute from 2:00-2:06 AM |
| `L` | Last (days field only) | `59 23 L * *` — 11:59 PM on the last day of the month |
| `/#` | Step | `*/3 * * * *` — every 3 minutes |

## Gotchas and 8.3 notes

- **Individual function pages carry no explicit "new/changed/removed in 8.3" callouts.** The functions documented here (including the JSON, Identity Provider, and MongoDB-binding categories) are simply the current 8.3 function set as published; no per-function version-delta markers were present in the harvested docs.
- **`if()` — check both-branches evaluation on your own build.** The docs describe `if(condition, trueReturn, falseReturn)` as returning one branch's value based on `condition`, but do not explicitly state whether the *other* branch is still evaluated (and thus can still throw/subscribe) under the hood — treat both branches as potentially live (e.g. avoid put both a safe and unsafe division in the two branches and assuming the unsafe one is never touched); use `try()` to guard a branch that might error.
- **Null propagation**: use `isNull()`/`coalesce()` deliberately — arithmetic and string operators do not appear to auto-skip nulls the way SQL does; `coalesce(null, "abc")` is the documented way to fall back.
- **Quality overlays**: `forceQuality()` and `qualifiedValue()` only *display*/*propagate* a quality — they don't change the underlying value. `try()`'s failover value gets a quality code of 192 (good) per its own example, which is worth remembering when chaining further quality checks downstream.
- **Case sensitivity**: date-format pattern letters are case-sensitive (`M` ≠ `m`) and repeat-count sensitive (`M` vs `MM` vs `MMM` vs `MMMM` all differ). Function *names* themselves are case-sensitive too (e.g. `toInt` vs a stray `ToInt` will not resolve). Boolean literals are the one deliberate case-insensitive exception (`true` = `True` = `TRUE`).
- **Zero-indexed months**: `dateExtract(date, "year")`-style field extraction and the `get*` family return **zero-indexed months** (January = 0). Add 1 if you need a human month number. `getDate(year, month, day)` also takes a zero-based month when *constructing* a date.
- **`switch()` vs `case()`**: functionally similar (C-style switch semantics) but the **argument order differs** — `switch(value, case1..N, return1..N, returnDefault)` puts all cases before all returns, while `case(value, case1, return1, ..., returnDefault)` interleaves case/return pairs. Easy to mix up when porting between them.
- **`color()`/`toColor()` are Vision-only.** In Perspective, bind color properties directly to hex strings (`"#00FF00"`) instead — these two functions were designed to return Vision's `Color` objects and are documented as not working with Perspective bindings.
- **`property()` is Perspective-only** (the inverse restriction) — it looks up a Perspective component property by a (potentially dynamic) string path; it has no meaning in Vision.
- **`hasRole()` scope quirk**: `username`/`usersource` are optional in Client scope (defaults to the current user) but *required* in Gateway scope — and Perspective always runs in Gateway scope, so all three parameters must be supplied there, or use `isAuthorized()` instead.
- **`runScript()` costs the speed advantage of an expression** — it's documented as materially slower than normal expression evaluation since it invokes the Python engine; use sparingly, e.g. not in a tight polling loop.
- **`tag()` inside a logic function stays subscribed** even if that logic function's outcome ends up not using the value — worth knowing for performance/subscription-count reasons when a `tag()` call sits inside an unused branch of `if`/`switch`/`case`.
- **`containsAll`/`containsAny` are IdP-scoped only** — restricted to Security Level Rules and User Attribute Mapping expressions; they operate on collection-like bound objects such as `{security-zones}` or `{idp-attribute:X}`, not on arbitrary datasets or Perspective/Vision bindings.
- **`lookup()` result is coerced to the type of `noMatchValue`** — the returned column value's type follows the failover argument's type, not necessarily the source column's native type.
