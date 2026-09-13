# Ignition Perspective Components - Complete Index
**Master Reference | Ignition 8.3 | 67 Components Organized by Category**

See also: [README](README.md) · [↑ Back to KB INDEX](../00-INDEX.md)

> **Quick Navigation:** Use folder structure to find components by type. Each component has detailed documentation in its own `.md` file.

> **Linkage note (2026-07-13):** Table entries below now link to their actual `.md` files. 8 entries (Moving Analog Indicator, Dashboard, Flex Repeater, Accordion, Carousel, View Canvas, View Object, Report Viewer) are listed here but have **no backing file yet** — marked 🚧. Also: [Display/Charts/PieChart.md](Display/Charts/PieChart.md) duplicates [Display/Charts/Pie-Chart.md](Display/Charts/Pie-Chart.md) (content overlap — Pie-Chart.md is canonical; consolidate later). Component count above (67) includes the 8 undocumented items; **60 unique components have real files** (62 file paths, 2 of which are Gauge/Simple-Gauge intentionally cross-listed under both Charts and Industrial).

---

## Component Categories Overview

### INPUT COMPONENTS (18 total)
User interaction and data entry components for forms and user input.

**Location:** `/Input/`

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Button**](Input/Button.md) | Trigger actions on click | Form submission, action buttons |
| 2. [**Checkbox**](Input/Checkbox.md) | Binary selection (on/off) | Feature toggles, multiple selections |
| 3. [**DateTime Input**](Input/DateTimeInput.md) | Date selection from popup | Forms, date filtering |
| 4. [**DateTime Picker**](Input/DateTimePicker.md) | Date and time selection | Appointments, timestamps |
| 5. [**Dropdown**](Input/Dropdown.md) | Select from list in limited space | Option selection, menus |
| 6. [**Text Field**](Input/TextField.md) | Single-line text input | Name entry, search fields |
| 7. [**Text Area**](Input/TextArea.md) | Multi-line text input | Comments, long text |
| 8. [**Numeric Entry Field**](Input/NumericEntryField.md) | Specialized numeric input | Quantities, calculations |
| 9. [**Slider**](Input/Slider.md) | Range selection via drag | Volume, values between min/max |
| 10. [**Radio Group**](Input/RadioGroup.md) | Single-option selection group | Mutually exclusive choices |
| 11. [**Toggle Switch**](Input/ToggleSwitch.md) | Binary on/off toggle | Feature enable/disable |
| 12. [**Password Field**](Input/PasswordField.md) | Masked text input | Credentials, passwords |
| 13. [**File Upload**](Input/FileUpload.md) | File selection and upload | Document upload, media files |
| 14. [**Barcode Scanner Input**](Input/BarcodeScannerInput.md) | Input from barcode devices | Product scanning, asset tracking |
| 15. [**Multi-State Button**](Input/MultiStateButton.md) | Multiple buttons in row/column | State selection, option groups |
| 16. [**One-Shot Button**](Input/OneShotButton.md) | Send write request and wait | Command execution, data writes |
| 17. [**Signature Pad**](Input/SignaturePad.md) | Digital signature capture | Document signing, approvals |
| 18. [**Form**](Input/Form.md) | Form container and submission | Multi-field data entry |

---

### DISPLAY COMPONENTS (26 total)
Information presentation without user interaction.

**Location:** `/Display/`

#### Display - General (20 components)

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Label**](Display/Label.md) | Text display with styling | Information display, titles |
| 2. [**Table**](Display/Table.md) | Data table with columns | Data browsing, sorted displays |
| 3. [**Image**](Display/Image.md) | Vector/raster image display | Logo rendering, galleries |
| 4. [**Icon**](Display/Icon.md) | SVG icon access | UI iconography, status indicators |
| 5. [**Markdown**](Display/Markdown.md) | Formatted text display | Rich text, documentation |
| 6. [**Progress**](Display/Progress.md) | Task progress visualization | Completion indicators, bars |
| 7. [**Badge/LED Display**](Display/Badge-LED-Display.md) | Numeric/alphanumeric display | Digital readouts, counters |
| 8. [**Barcode**](Display/Barcode.md) | Text as barcode format | Product codes, tracking |
| 9. [**Audio**](Display/Audio.md) | Audio playback | Alerts, notifications |
| 10. [**Video Player**](Display/Video-Player.md) | Video/live feed embedding | Media playback, monitoring |
| 11. [**PDF Viewer**](Display/PDF-Viewer.md) | PDF document viewing | Reports, documents |
| 12. [**Inline Frame**](Display/Inline-Frame.md) | Webpage within component | External content |
| 13. [**Drawing**](Display/Drawing.md) | Vector drawing capabilities | Schematics, custom graphics |
| 14. [**Tree**](Display/Tree.md) | Hierarchical tree view | Nested browsing, hierarchies |
| 15. [**Tag Browse Tree**](Display/Tag-Browse-Tree.md) | Tag navigation hierarchy | Tag structure browsing |
| 16. [**Alarm Journal Table**](Display/Alarm-Journal-Table.md) | Alarm event history | Historical alarm tracking |
| 17. [**Alarm Status Table**](Display/Alarm-Status-Table.md) | Current alarm statuses | Real-time monitoring |
| 18. [**Equipment Schedule**](Display/Equipment-Schedule.md) | Scheduling visualization | Maintenance, downtime |
| 19. [**Linear Scale**](Display/Linear-Scale.md) | Tick marks and labels | Scale references, ranges |
| 20. [**Sparkline**](Display/Sparkline.md) | Minimalistic inline chart | Quick trend visualization |

#### Display - Mapping (2 components)

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 21. [**Map**](Display/Mapping/Map.md) | Map visualization | Location display, asset mapping |
| 22. [**Google Map**](Display/Mapping/Google-Map.md) | Google Maps integration | Geographic data, tracking |

#### Display - Industrial Visualization (4 components)

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 23. [**Gauge**](Display/Industrial/Gauge.md) | Real-time value in range | KPIs, sensor readings |
| 24. [**Simple Gauge**](Display/Industrial/Simple-Gauge.md) | Simplified gauge | Quick value display |
| 25. [**Thermometer**](Display/Industrial/Thermometer.md) | Temperature display | Thermal monitoring, HVAC |
| 26. **Moving Analog Indicator** 🚧 *(not yet documented)* | Analog value display | Gauge-like displays |
| 27. [**Cylindrical Tank**](Display/Industrial/Cylindrical-Tank.md) | 3D tank liquid visualization | Fluid level monitoring |
| 28. **Dashboard** 🚧 *(not yet documented)* | Dashboard container | Multi-component layouts |

---

### CHART COMPONENTS (7 total)
Data visualization and real-time value displays.

**Location:** `/Display/Charts/`

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Pie Chart**](Display/Charts/Pie-Chart.md) | Proportion-based visualization | Market share, budget allocation |
| 2. [**Time Series Chart**](Display/Charts/Time-Series-Chart.md) | Temporal data visualization | Trend analysis, historical data |
| 3. [**XY Chart**](Display/Charts/XY-Chart.md) | Cartesian coordinate plotting | Correlation, scatter plots |
| 4. [**Power Chart**](Display/Charts/Power-Chart.md) | Pen-based data collection | Multi-parameter trends |
| 5. [**Gauge**](Display/Charts/Gauge.md) | Real-time range display | Dynamic KPIs, metrics |
| 6. [**Simple Gauge**](Display/Charts/Simple-Gauge.md) | Simplified range display | Quick monitoring |
| 7. [**Chart Range Selector**](Display/Charts/Chart-Range-Selector.md) | Interactive time-range selection | Report periods, data filtering |

---

### CONTAINER COMPONENTS (6 total)
Layout and organizational structure for views.

**Location:** `/Containers/`

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Flex Container**](Containers/FlexContainer.md) | Responsive flexbox layout | Modern responsive designs |
| 2. [**Coordinate Container**](Containers/CoordinateContainer.md) | Absolute positioning (default) | Pixel-precise layouts |
| 3. [**Column Container**](Containers/ColumnContainer.md) | Single/multiple column layout | Multi-column data, forms |
| 4. [**Breakpoint Container**](Containers/BreakpointContainer.md) | Responsive breakpoint-based | Mobile-responsive dashboards |
| 5. [**Tab Container**](Containers/TabContainer.md) | Tabbed panel interface | Multi-panel organization |
| 6. [**Split Container**](Containers/SplitContainer.md) | Resizable split panels | Master-detail layouts |

---

### EMBEDDING COMPONENTS (5 total)
View composition and dynamic content embedding.

**Location:** `/Containers/` (Embedded/Reusable)

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Embedded View**](Misc/EmbeddedView.md) | Include entire view as component | View reuse, modular design |
| 2. **Flex Repeater** 🚧 *(not yet documented)* | Multiple view instances | Dynamic lists, data-driven |
| 3. **Accordion** 🚧 *(not yet documented)* | Collapsible panel organization | Content grouping, space-saving |
| 4. **Carousel** 🚧 *(not yet documented)* | Rotating view display | Slideshow, rotating content |
| 5. **View Canvas** 🚧 *(not yet documented)* | Dynamic view rendering | Runtime management, flexibility |

---

### NAVIGATION COMPONENTS (3 total)
User navigation within Perspective applications.

**Location:** `/Navigation/`

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. [**Link**](Navigation/Link.md) | Hyperlink navigation | View links, external resources |
| 2. [**Horizontal Menu**](Navigation/HorizontalMenu.md) | Top-level horizontal menu | Primary navigation bars |
| 3. [**Menu Tree**](Navigation/MenuTree.md) | Tree-based navigation | Hierarchical menus |

---

### SPECIAL / MISC COMPONENTS (2 total)
Special-purpose components and view configuration.

**Location:** `/Misc/`

| Component | Purpose | Key Use Cases |
|-----------|---------|---|
| 1. **View Object** 🚧 *(not yet documented)* | Base view container | View configuration, properties |
| 2. **Report Viewer** 🚧 *(not yet documented)* | Embed Reporting Module reports | Report viewing, integration |

---

## Quick Reference: Components by Palette

### By Ignition Default Palettes

**Chart Palette (7):**
- Chart Range Selector, Gauge, Pie Chart, Power Chart, Simple Gauge, Time Series Chart, XY Chart

**Container Palette (6):**
- Breakpoint Container, Column Container, Coordinate Container, Flex Container, Tab Container, Split Container

**Display Palette (26):**
- Alarm Journal Table, Alarm Status Table, Audio, Barcode, Cylindrical Tank, Dashboard, Drawing, Equipment Schedule, Google Map, Icon, Image, Inline Frame, Label, LED Display, Linear Scale, Map, Markdown, Moving Analog Indicator, PDF Viewer, Progress, Sparkline, Table, Tag Browse Tree, Thermometer, Tree, Video Player

**Input Palette (18):**
- Barcode Scanner Input, Button, Checkbox, DateTime Input, DateTime Picker, Dropdown, File Upload, Form, Multi-State Button, Numeric Entry Field, One-Shot Button, Password Field, Radio Group, Signature Pad, Slider, Text Area, Text Field, Toggle Switch

**Navigation Palette (3):**
- Horizontal Menu, Link, Menu Tree

**Embedding Palette (5):**
- Accordion, Carousel, Embedded View, Flex Repeater, View Canvas

**Special Components (2):**
- Report Viewer, View Object

---

## Component Selection by Use Case

### Data Entry & Forms
**Best Components:** Text Field, Text Area, Numeric Entry Field, Dropdown, DateTime Input, Checkbox, Radio Group, Form

### Data Display & Visualization
**Best Components:** Table, Label, Charts (Pie, Time Series, XY), Progress, Gauge, Thermometer

### User Actions & Navigation
**Best Components:** Button, Link, Horizontal Menu, Menu Tree, Multi-State Button

### Layout & Organization
**Best Components:** Flex Container, Tab Container, Accordion, Embedded View, Flex Repeater

### Real-time Monitoring
**Best Components:** Gauge, Simple Gauge, Progress, Alarm Status Table, Time Series Chart

### Reports & Documents
**Best Components:** Report Viewer, PDF Viewer, Table, Markdown, Image

---

## Component Statistics

- **Total Components:** 67
- **Input Components:** 18 (27%)
- **Display Components:** 26 (39%)
- **Chart Components:** 7 (10%)
- **Container Components:** 6 (9%)
- **Embedding Components:** 5 (7%)
- **Navigation Components:** 3 (4%)
- **Special Components:** 2 (3%)

---

## How to Use This Organization

1. **By Function:** Navigate to the appropriate folder (Input, Display, Containers, etc.)
2. **By Type:** Look within subfolders (e.g., Charts under Display)
3. **By Use Case:** Reference quick reference tables above
4. **Detailed Documentation:** Each component has its own `.md` file with:
   - Purpose & description
   - All properties with types and defaults
   - Common bindings and event handlers
   - Code examples
   - When to use vs. alternatives

---

**Last Updated:** 2026-07-13  
**Version:** 1.0  
**Reference:** Ignition 8.3 Perspective Component Documentation
