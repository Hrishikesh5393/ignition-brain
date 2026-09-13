---
title: Component Reference - Properties & Bindings
description: Individual components, all properties, common bindings
---

> **Skill level:** 200 · **Read first:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [21-BINDINGS](21-BINDINGS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 12-COMPONENT-REFERENCE

# Component Reference

## Label Component

**Purpose:** Display static or dynamic text.

**Props:**
- `text` (string) - Text content
- `visible` (bool) - Show/hide
- `disabled` (bool) - Grayed out
- `fontSize` (int) - Font size in pixels
- `fontColor` (color) - Text color
- `fontSize` (int) - Font size px
- `horizontalAlignment` - left, center, right
- `verticalAlignment` - top, center, bottom
- `margin` - Padding around text
- `padding` - Space inside container
- `tooltip` - Hover text
- `style.classes` - CSS class list
- `style.colors` - Text color by state

**Common Bindings:**
```javascript
// Display tag value
{tag: "[default]ProductionCount"}

// Dynamic text
{expr: "concat('Status: ', {[default]Status})"}

// Conditional display
{expr: "{[default]Temperature} > 80 ? 'HOT' : 'NORMAL'"}
```

## Text Input Component

**Purpose:** Single-line text entry.

**Props:**
- `value` (string) - Current input value
- `placeholder` (string) - Hint text when empty
- `disabled` (bool) - Disable input
- `readOnly` (bool) - Display only, no edit
- `clearable` (bool) - Show clear button
- `validation` - Regex pattern or function

**Events:**
- `onChange` - When value changes
- `onFocus` - When focused
- `onBlur` - When unfocused

**Common Script:**
```python
# In onChange event:
value = self.props.value
if value.isdigit():
    system.tag.write("[default]InputValue", int(value))
else:
    self.props.customMessage = "Must be number"
```

## Numeric Input Component

**Purpose:** Number entry with validation.

**Props:**
- `value` (number) - Current value
- `min`, `max` - Range bounds
- `step` - Increment/decrement step
- `decimal` - Number of decimal places
- `unit` - Unit display (e.g., "°C")
- `disabled`, `readOnly` - States

**Binding:**
```javascript
{tag: "[default]Temperature"}
```

## Checkbox Component

**Purpose:** Toggle true/false.

**Props:**
- `value` (bool) - Checked state
- `label` (string) - Checkbox label
- `disabled` (bool)

**Script:**
```python
# In onChange event:
system.tag.write("[default]PowerOn", self.props.value)
```

## Button Component

**Purpose:** Clickable action trigger.

**Props:**
- `text` (string) - Button label
- `primary` (bool) - Style as primary
- `disabled` (bool) - Disabled state
- `iconUrl` (string) - Icon image

**Events:**
- `onClick` - When clicked

**Script:**
```python
# In onClick:
system.tag.write("[default]RunButton", 1)
system.perspective.sendMessage("action", {"cmd": "run"})
```

## Dropdown/Select Component

**Purpose:** Choose from list.

**Props:**
- `value` - Selected value
- `options` (array) - [{"label": "Option 1", "value": 1}, ...]
- `multiple` (bool) - Multi-select
- `clearable` (bool)
- `searchable` (bool)

**Binding Options:**
```javascript
// Static list:
[{"label": "ON", "value": 1}, {"label": "OFF", "value": 0}]

// Dynamic from tag (dataset):
{tag: "[default]StatusList"}
```

## Table Component

**Purpose:** Display/edit tabular data.

**Props:**
- `data` (dataset) - Table rows
- `columns` - Column definitions [{"field": "name", "header": "Name", "editable": true}, ...]
- `selection` (array) - Selected row indices
- `sortColumn`, `sortOrder` - Sort state
- `pageSize` - Rows per page
- `virtualized` (bool) - Virtual scrolling (large datasets)

**Events:**
- `onSelectionChange` - Row selection changed
- `onRowDoubleClick` - Row double-clicked
- `onCellEdited` - Cell value changed

**Binding:**
```javascript
// Bind to dataset query result:
{tag: "[sql]Reports/ProductionData"}
```

## Chart Components (XY, TimeSeries, Pie, Bar)

**Purpose:** Visualize data trends, comparisons.

**XY Chart:**
- `data` (dataset) - X, Y columns
- `series` - Which columns to plot
- `xAxis`, `yAxis` - Scale, labels
- `legend` - Show legend

**TimeSeries Chart:**
- `data` (dataset) - timestamp, value columns
- `range` - Time range (last hour, day, etc.)
- `xAxis.dateFormat` - Timestamp format

**Pie Chart:**
- `data` (dataset) - category, value columns
- `labelFormat` - % or count
- `colors` - Segment colors

**Binding:**
```javascript
// Historical temperature data
{tag: "[sql]Reports/TempHistory"}
```

## Progress Bar Component

**Purpose:** Show percentage complete.

**Props:**
- `value` (number) - 0-100
- `min`, `max` - Range
- `showLabel` (bool) - Show percentage
- `labelFormat` - "80%", "80/100"
- `color` - Bar color

**Binding:**
```javascript
{expr: "{[default]Completed} / {[default]Total} * 100"}
```

## Container Component

**Purpose:** Organize child components.

**Props:**
- `visible`, `disabled`
- `style` - CSS styling
- `gap` - Space between children
- `padding`, `margin`

**Layout:** Flex (row/column)

## Flex Container

**Purpose:** Flexible layout (rows/columns).

**Props:**
- `direction` - row or column
- `justifyContent` - Spacing (flex-start, center, space-between)
- `alignItems` - Alignment (flex-start, center, stretch)
- `gap` - Space between children
- `wrap` (bool) - Wrap to next line

**Pattern:**
```
Flex Container (direction: column, gap: 10)
├── Header Label
├── Input Field
├── Button
└── Result Label
```

## Tabs Component

**Purpose:** Tabbed interface.

**Props:**
- `selectedTab` - Active tab index
- `tabs` - Tab definitions [{"label": "Tab 1", "path": "view/tab1"}, ...]

**Events:**
- `onTabChanged` - Tab selection changed

## Popup/Modal

**Purpose:** Modal dialog over content.

**Props:**
- `title`, `message` - Dialog text
- `buttons` - Action buttons [{"text": "OK", "action": "ok"}, ...]
- `visible` (bool) - Show/hide

**Script:**
```python
# Show popup
popup = self.parent.getChild("popup")
popup.props.visible = True
popup.props.message = "Confirm delete?"
```

## Repeater Component

**Purpose:** Loop component over data.

**Props:**
- `instances` (int) - Number of repeats
- `dataset` - Data rows (one component per row)
- `index` - Current index variable

**Pattern:**
```
Repeater (dataset: {tag: "[sql]Users"})
└── User Card View (embedded view)
    Receives: row data via prop binding
```

---
**Property Binding Pattern:** Any prop can be bound to tag/expression:
```javascript
visible: {expr: "{[default]ShowElement} == 'yes'"}
color: {expr: "{[default]Status} == 'error' ? '#FF0000' : '#00FF00'"}
text: {tag: "[default]MessageText"}
```

**See:** Individual component docs at docs.inductiveautomation.com/docs/8.3/appendix/components/perspective-components

---

## See Also

**Prerequisites:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [21-BINDINGS](21-BINDINGS.md)

**Builds toward:** [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md), [14-APPENDIX-COMPONENTS-DETAILED](14-APPENDIX-COMPONENTS-DETAILED.md), [Components/README](Components/README.md)

**Related:** [14-APPENDIX-COMPONENTS-DETAILED](14-APPENDIX-COMPONENTS-DETAILED.md), [Components/README](Components/README.md), [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [22-EXPRESSIONS](22-EXPRESSIONS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
