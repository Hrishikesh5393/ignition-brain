---
title: Perspective Component Palettes
description: All component categories and primary components in each
---

> **Skill level:** 100 · **Read first:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 11-COMPONENTS-PALETTES

# Perspective Component Palettes

Ignition Perspective provides 50+ components organized into palettes.

## Palette Overview

### 1. Chart Palette (Data Visualization)
Components for graphing, charts, trends.

**Primary:**
- **XY Chart** - 2D scatter, line, area plots
- **Time Series Chart** - Over-time data with timeline axis
- **Pie Chart** - Proportion breakdown
- **Bar Chart** - Categories vs. values
- **Heat Map** - 2D grid color intensity
- **Gauge** - Radial or linear (needle/arc)
- **Sparkling** - Compact mini-charts

**Props:**
- `data` (dataset) - Data to plot
- `series` (array) - Which columns to visualize
- `xAxis`, `yAxis` - Scale, label, formatting
- `legend` - Show/hide legend
- `tooltip` - Hover info

### 2. Container Palette (Layout)
Structural elements for organizing layouts.

**Primary:**
- **Container** - Basic rectangular container (flex layout)
- **Flex Container** - Flexbox layout (rows/columns)
- **Grid Container** - CSS grid layout
- **Tabs** - Tabbed interface
- **Accordion** - Collapsible sections
- **Repeater** - Loop component over array/dataset
- **Carousel** - Slide through views/components
- **Break** - Spacer/separator

**Props:**
- `direction` - row, column (flex)
- `gap` - Space between children
- `justify`, `align` - Flex alignment
- `visible`, `disabled` - Show/enable

### 3. Display Palette (Info)
Components for showing information.

**Primary:**
- **Label** - Static/dynamic text
- **Image** - Display image (URL or upload)
- **Icon** - SVG icon or glyph
- **Progress Bar** - Linear progress indicator
- **Circular Progress** - Rotating progress
- **Badge** - Small labeled indicator
- **Tooltip** - Hover-reveal text
- **Divider** - Visual separator
- **Link** - Clickable URL

**Props:**
- `text` - Content to display
- `visible` - Show/hide
- `style` - CSS for appearance
- `color`, `fontSize` - Typography

### 4. Input Palette (User Input)
Components for data entry.

**Primary:**
- **Text Input** - Single-line text field
- **Text Area** - Multi-line text
- **Numeric Input** - Number entry with validation
- **Checkbox** - Toggle bool
- **Radio Button** - Mutually exclusive choice
- **Dropdown/Select** - Choose from list
- **Slider** - Range selector
- **Date Picker** - Date input
- **Time Picker** - Time input
- **Switch** - Toggle ON/OFF
- **File Upload** - Upload file

**Props:**
- `value` - Current value (bind to tag)
- `options` - Available choices (dropdown/radio)
- `required` - Mandatory field
- `disabled` - Disabled state
- `validation` - Input validation regex/function

### 5. Navigation Palette (Routing)
Components for view/page navigation.

**Primary:**
- **Link** - Navigate to view/URL
- **Breadcrumb** - Show current path
- **Tab** - Tabbed navigation
- **Menu** - Horizontal/vertical menu
- **List** - Menu list

**Props:**
- `path` - Target view path
- `params` - Pass data to next view
- `replace` - Replace history (no back)

### 6. Embedding Palette (External Content)
Components for embedding external content.

**Primary:**
- **Iframe** - Embed external webpage
- **Embedded View** - Nest another view
- **Report Viewer** - Display report
- **Markdown** - Render markdown

**Props:**
- `viewPath` - View to embed
- `params` - Parameters to pass
- `source` - Report path, URL, etc.

### 7. Symbols Palette (Icons/Shapes)
Graphics and symbol components.

**Primary:**
- **SVG Icon** - Scalable vector
- **Shape** - Rectangle, circle, line, polygon
- **Symbol** - Reusable custom graphic
- **Analog Clock** - Clock display
- **Digital Clock** - Time display

### 8. Special Components

**View (Container)**
- Root element of every view
- Properties control view-level behavior
- `viewPath` - Full path to this view

**Popup/Modal**
- Display over content
- Blocks interaction until closed
- `title`, `message`, `buttons` props

---

## Common Props (All Components)

| Prop | Type | Purpose |
|------|------|---------|
| `visible` | bool | Show/hide component |
| `disabled` | bool | Disable interaction |
| `style` | object | CSS styling |
| `custom.property` | any | Custom metadata |
| `transform` | string | CSS transform (rotate, scale) |
| `tooltip` | string | Hover help text |

## Event Handlers (All Interactable Components)

| Event | When | Use Case |
|-------|------|----------|
| `onClick` | User clicks | Action on click |
| `onChange` | Value changes | Update tag, validate |
| `onFocus` | Component focused | Show help, highlight |
| `onBlur` | Component unfocused | Validation, save |
| `onMouseEnter` | Hover start | Highlight, show info |
| `onMouseLeave` | Hover end | Hide, reset |
| `onKeyUp` | Key released | Shortcut, search |
| `onKeyDown` | Key pressed | Navigation |

## Binding Patterns

**Direct Tag Binding:**
```javascript
// Bind component.value to tag
{tag: "[default]Production/Speed"}
```

**Expression:**
```javascript
// Conditional
{expr: "if({tag} > 100, 'FAST', 'SLOW')"}

// Math
{expr: "{temp} * 9/5 + 32"}  // C to F

// String concat
{expr: "concat({first}, ' ', {last})"}
```

**Script Transform:**
```javascript
// In component event handler script:
self.parent.getChild("output").props.text = f"Result: {value * 2}"
```

---
**Reference:** See [[12-COMPONENT-REFERENCE]] for individual component property details.

---

## See Also

**Prerequisites:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

**Builds toward:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](14-APPENDIX-COMPONENTS-DETAILED.md), [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md)

**Related:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](14-APPENDIX-COMPONENTS-DETAILED.md), [Components/README](Components/README.md), [21-BINDINGS](21-BINDINGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
