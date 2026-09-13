# Ignition Perspective Components Knowledge Base

**Complete Reference | Ignition 8.3 | 67 Components**

---

## Overview

This folder contains comprehensive documentation for all 67 Perspective components in Ignition 8.3, organized by category with individual reference files for each component.

### Folder Structure

```
Components/
├── 00-Component-Index.md          (Master index - START HERE)
├── _COMPONENT_TEMPLATE.md         (Template for creating new component docs)
├── README.md                      (This file)
│
├── Input/                         (18 components)
│   ├── Button.md                  ✓ Detailed
│   ├── TextField.md               ✓ Detailed
│   ├── Checkbox.md                ✓ Detailed
│   ├── TextArea.md
│   ├── NumericEntryField.md
│   ├── Slider.md
│   ├── DateTimeInput.md
│   ├── DateTimePicker.md
│   ├── Dropdown.md
│   ├── RadioGroup.md
│   ├── ToggleSwitch.md
│   ├── PasswordField.md
│   ├── FileUpload.md
│   ├── BarcodeScanner.md
│   ├── MultiStateButton.md
│   ├── OneShotButton.md
│   ├── SignaturePad.md
│   └── Form.md
│
├── Display/                       (26 components)
│   ├── Label.md
│   ├── Table.md                   ✓ Detailed
│   ├── Image.md
│   ├── Icon.md
│   ├── Markdown.md
│   ├── Progress.md
│   ├── LEDDisplay.md
│   ├── Barcode.md
│   ├── Audio.md
│   ├── VideoPlayer.md
│   ├── PDFViewer.md
│   ├── InlineFrame.md
│   ├── Drawing.md
│   ├── Tree.md
│   ├── TagBrowseTree.md
│   ├── AlarmJournalTable.md
│   ├── AlarmStatusTable.md
│   ├── EquipmentSchedule.md
│   ├── LinearScale.md
│   ├── Sparkline.md
│   ├── Dashboard.md
│   ├── Mapping/
│   │   ├── Map.md
│   │   └── GoogleMap.md
│   ├── Industrial/
│   │   ├── Gauge.md
│   │   ├── SimpleGauge.md
│   │   ├── Thermometer.md
│   │   ├── MovingAnalogIndicator.md
│   │   └── CylindricalTank.md
│   └── Charts/                    (See below)
│
├── Display/Charts/                (7 components)
│   ├── PieChart.md                ✓ Detailed
│   ├── TimeSeriesChart.md
│   ├── XYChart.md
│   ├── PowerChart.md
│   ├── Gauge.md                   (Shared with Display/Industrial)
│   ├── SimpleGauge.md             (Shared with Display/Industrial)
│   └── ChartRangeSelector.md
│
├── Containers/                    (11 components)
│   ├── FlexContainer.md           ✓ Detailed
│   ├── CoordinateContainer.md
│   ├── ColumnContainer.md
│   ├── BreakpointContainer.md
│   ├── TabContainer.md
│   ├── SplitContainer.md
│   ├── Accordion.md
│   ├── Carousel.md
│   ├── EmbeddedView.md
│   ├── FlexRepeater.md
│   └── ViewCanvas.md
│
├── Navigation/                    (3 components)
│   ├── Link.md                    ✓ Detailed
│   ├── HorizontalMenu.md
│   └── MenuTree.md
│
└── Misc/                          (2 components)
    ├── ViewObject.md
    └── ReportViewer.md
```

---

## Component Status Summary

**All 67 components documented** (2026-07-13 verification pass). Every component doc's property table has been cross-checked against the actual runtime schemas extracted from `data\jar-cache\com.inductiveautomation.perspective\*.jar` (Ignition 8.3.7) — not just written against generic Ignition knowledge. Docs that had invented/incorrect property names (a significant fraction of the "detailed" tier, especially Table, chart, map, and alarm-table components) were rewritten from the real schema; docs that were already accurate (containers, most simple Input/Display components) were left as-is.

Six components that had no doc at all were added: **Accordion, Carousel, Dashboard, FlexRepeater, MovingAnalogIndicator, ViewCanvas**.

A duplicate `PieChart.md` (which self-flagged as non-canonical) was deleted in favor of the canonical `Pie-Chart.md`.

### Template Available
- `_COMPONENT_TEMPLATE.md` - Use this template to create additional component documentation

### If Ignition Version Changes
Re-run the schema extraction against the new `perspective-common`/`perspective-amcharts`/`perspective-map`/`perspective-googlemap`/`perspective-timeseries`/pdf-viewer/barcode component jars in the new install's `data\jar-cache\com.inductiveautomation.perspective\` folder (`unzip -p` the `*.components.json` and `barcode.component.json` files — they're plain JSON, no decompiler needed) and diff property names against the docs before trusting a version bump.

---

## How to Use This Knowledge Base

### Quick Start

1. **Start Here:** Read `00-Component-Index.md` for overview of all 67 components
2. **Find Component:** Look in appropriate folder (Input, Display, Containers, etc.)
3. **Read Documentation:** Each component file contains:
   - Purpose & description
   - Common use cases
   - Complete properties reference
   - Common bindings and event handlers
   - Code examples and patterns
   - When to use vs. alternatives
   - Performance considerations
   - Accessibility features
   - Common errors & solutions
   - Related components

### By Use Case

#### Data Entry & Forms
- **Input components** folder
- Recommended: TextField, TextArea, NumericEntryField, Checkbox, Dropdown, RadioGroup

#### Data Display & Visualization
- **Display/** and **Display/Charts/** folders
- Recommended: Table, Label, PieChart, TimeSeriesChart, Gauge, Progress

#### Page Layout & Organization
- **Containers/** folder
- Recommended: FlexContainer (most versatile), TabContainer, FlexRepeater, EmbeddedView

#### Navigation & User Flow
- **Navigation/** folder
- Recommended: Link, HorizontalMenu, MenuTree

---

## Creating Additional Component Documentation

### Using the Template

1. Copy `_COMPONENT_TEMPLATE.md`
2. Replace placeholders with component-specific information
3. Save in appropriate folder with component name (e.g., `Dropdown.md`)
4. Update `00-Component-Index.md` to mark as documented

### Template Sections to Fill

```markdown
# [COMPONENT NAME] Component

**Category:** [Category] / [Subcategory]
**Ignition Version:** 8.3+
**Palette:** [Palette Name]

---

## Purpose & Description
[1-2 sentence description]

### Key Characteristics
- [Feature 1]
- [Feature 2]
- [Feature 3]
- [Feature 4]

## Common Use Cases
1. [Use Case 1]
2. [Use Case 2]
3. [Use Case 3]

## Properties Reference
[Create table of properties]

## Common Bindings
[JavaScript binding examples]

## Event Handlers
[JavaScript event handler examples]

## Common Patterns & Examples
[Code examples for real-world usage]

## When to Use vs. Alternatives
[Component comparison guide]

## Performance Considerations
[Optimization tips]

## Accessibility Features
[A11y considerations]

## Common Errors & Solutions
[Troubleshooting guide]

## Related Components
[Cross-references]
```

---

## Component Properties Format

Each component documentation includes detailed properties in this table format:

```markdown
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| **propertyName** | string/numeric/boolean/object/array | default_value | What the property does |
```

### Common Property Types

- **string** - Text values
- **numeric** - Numbers (integer or decimal)
- **boolean** - True/False
- **object** - Complex nested structures
- **array** - Collections of values
- **date/datetime** - Date and time values
- **function** - JavaScript functions

---

## Common Binding Patterns

All component documentation includes these binding examples:

### Value Bindings
```javascript
property: {tag: "Path/To/Tag"}
property: {expr: "conditional_expression"}
property: {query: {sql: "SELECT ...", database: "default"}}
```

### Event Handlers
```javascript
onClick: function(self, event) { /* handler code */ }
onChange: function(self, value) { /* handler code */ }
onKeyUp: function(self, event) { /* handler code */ }
```

---

## Navigation Tips

### Finding Components by Type

**Input Components:**
- Text: TextField, TextArea, PasswordField
- Numeric: NumericEntryField, Slider
- Selection: Checkbox, RadioGroup, ToggleSwitch, Dropdown
- Date/Time: DateTimeInput, DateTimePicker
- File: FileUpload, BarcodeScanner
- Action: Button, MultiStateButton, OneShotButton

**Display Components:**
- Text: Label, Markdown
- Data: Table, Tree, TagBrowseTree
- Media: Image, Icon, Audio, VideoPlayer, PDFViewer
- Industrial: Gauge, Thermometer, CylindricalTank
- Alarms: AlarmStatusTable, AlarmJournalTable
- Charts: PieChart, TimeSeriesChart, XYChart, etc.

**Container Components:**
- Layout: FlexContainer, CoordinateContainer, ColumnContainer
- Responsive: BreakpointContainer
- Organization: TabContainer, SplitContainer, Accordion
- Reusable: EmbeddedView, FlexRepeater, Carousel

**Navigation Components:**
- Link, HorizontalMenu, MenuTree

---

## Best Practices for Component Documentation

When adding new component documentation:

1. **Accuracy:** Reference Ignition 8.3 official documentation
2. **Completeness:** Include all major properties and events
3. **Examples:** Provide real-world code examples
4. **Clarity:** Use clear, concise language
5. **Organization:** Follow template structure consistently
6. **Related Components:** Cross-reference similar components

---

## Updating the Master Index

When adding new component documentation:

1. Update `00-Component-Index.md` to mark component as "✓ Detailed"
2. Add component to appropriate category table
3. Update component statistics at bottom of index file

Example update:
```markdown
| 15. **NewComponent** | Description of purpose | Use case 1, Use case 2 |
```

---

## Quick Reference: Component Palettes

### By Ignition Palette

**Chart Palette (7):**
Chart Range Selector, Gauge, Pie Chart, Power Chart, Simple Gauge, Time Series Chart, XY Chart

**Container Palette (6):**
Breakpoint Container, Column Container, Coordinate Container, Flex Container, Tab Container, Split Container

**Display Palette (26):**
Alarm Journal Table, Alarm Status Table, Audio, Barcode, Cylindrical Tank, Dashboard, Drawing, Equipment Schedule, Google Map, Icon, Image, Inline Frame, Label, LED Display, Linear Scale, Map, Markdown, Moving Analog Indicator, PDF Viewer, Progress, Sparkline, Table, Tag Browse Tree, Thermometer, Tree, Video Player

**Input Palette (18):**
Barcode Scanner Input, Button, Checkbox, DateTime Input, DateTime Picker, Dropdown, File Upload, Form, Multi-State Button, Numeric Entry Field, One-Shot Button, Password Field, Radio Group, Signature Pad, Slider, Text Area, Text Field, Toggle Switch

**Navigation Palette (3):**
Horizontal Menu, Link, Menu Tree

**Embedding Palette (5):**
Accordion, Carousel, Embedded View, Flex Repeater, View Canvas

**Special Components (2):**
Report Viewer, View Object

---

## Component Count by Category

| Category | Count | Percentage |
|----------|-------|-----------|
| Input | 18 | 27% |
| Display | 26 | 39% |
| Containers (including Embedding) | 11 | 16% |
| Charts | 7 | 10% |
| Navigation | 3 | 4% |
| Special/Misc | 2 | 3% |
| **TOTAL** | **67** | **100%** |

---

## Version History

- **v1.0** (2026-07-13) - Initial organization with 7 detailed components and master index
  - Created folder structure with 5 main categories
  - 7 comprehensive component documentation files
  - Master index with all 67 components listed
  - Template file for creating additional documentation
  - README with navigation and best practices
- **v2.0** (2026-07-13) - Schema-verified pass: all 67 components documented and cross-checked against extracted Ignition 8.3.7 runtime schemas
  - Rewrote property tables for ~25 docs that had invented/incorrect property names (Table, PieChart, GoogleMap, Map, EquipmentSchedule, alarm tables, chart family, several simple Display components)
  - Added the 6 previously-missing component docs (Accordion, Carousel, Dashboard, FlexRepeater, MovingAnalogIndicator, ViewCanvas)
  - Removed duplicate PieChart.md in favor of canonical Pie-Chart.md

---

## Related Resources

- **Source:** `14-APPENDIX-COMPONENTS-DETAILED.md` (original component appendix)
- **Ignition Docs:** https://docs.inductiveautomation.com/docs/8.3/
- **Component Reference:** Ignition Designer > Help > Component Reference

---

## Contact & Updates

For questions about component documentation or to suggest improvements:
- Refer to component's "Related Components" section
- Check official Ignition documentation
- Review code examples in documentation

---

**Knowledge Base Version:** 2.0  
**Last Updated:** 2026-07-13  
**Total Components:** 67  
**Documented:** 67 (all, schema-verified against Ignition 8.3.7 runtime jar-cache)  
**Ignition Version:** 8.3.7 (verified against `lib\install-info.txt`)
