> **Skill level:** 200 · **Read first:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 14-APPENDIX-COMPONENTS-DETAILED

# Ignition Perspective Components - Detailed Reference
**Ignition 8.3 | Complete Component Catalog**

---

## Table of Contents

1. [Chart Palette](#chart-palette)
2. [Container Palette](#container-palette)
3. [Display Palette](#display-palette)
4. [Input Palette](#input-palette)
5. [Navigation Palette](#navigation-palette)
6. [Embedding Palette](#embedding-palette)
7. [Special Components](#special-components)

---

## Chart Palette

**Purpose:** Components for data visualization and real-time value display across various chart types.

### Chart Components Overview

| Component | Purpose |
|-----------|---------|
| Chart Range Selector | Interactive time-range selection with visual data representation |
| Gauge | Real-time value display within a defined range |
| Pie Chart | Proportion-based visualization (parts of a whole) |
| Power Chart | Pen-based data collection and visualization system |
| Simple Gauge | Simplified alternative to standard Gauge component |
| Time Series Chart | Temporal data visualization across multiple sources |
| XY Chart | Cartesian coordinate system data visualization |

### Detailed Component Specifications

#### **1. Chart Range Selector**
- **Category:** Chart / Interactive
- **Purpose:** Allows operators to select a time range based on visualizing existing data
- **Use Cases:** 
  - Time period selection for reports
  - Dynamic data filtering
  - Historical data range specification
- **Key Features:**
  - Visual recreation of chart data
  - Interactive range handles
  - Real-time feedback of selected period

#### **2. Gauge**
- **Category:** Chart / Real-time Display
- **Purpose:** Provides a way to show real-time values in a range as they change
- **Use Cases:**
  - Displaying dynamic KPIs
  - Real-time sensor readings
  - Performance metrics monitoring
- **Key Features:**
  - Dynamic value updates
  - Configurable range limits
  - Visual needle indicator

#### **3. Pie Chart**
- **Category:** Chart / Categorical Distribution
- **Purpose:** Displays a list of named items, each with a value that is part of a total
- **Use Cases:**
  - Market share visualization
  - Budget allocation display
  - Category distribution analysis
- **Key Features:**
  - Proportional segment sizing
  - Named categories
  - Total value calculation

#### **4. Power Chart**
- **Category:** Chart / Pen-based
- **Purpose:** Collects and displays data based on configured pens
- **Use Cases:**
  - Multi-parameter trend analysis
  - Pen-based data logging
  - Historical data visualization
- **Key Features:**
  - Pen-based data collection
  - Multiple data series support
  - Configurable pens

#### **5. Simple Gauge**
- **Category:** Chart / Real-time Display
- **Purpose:** Simplified alternative to standard Gauge component
- **Use Cases:**
  - Quick value display
  - Simplified dashboards
  - Lightweight monitoring displays
- **Key Features:**
  - Reduced complexity
  - Optimized performance
  - Real-time value updates

#### **6. Time Series Chart**
- **Category:** Chart / Temporal Data
- **Purpose:** Provides an efficient way to visualize data from various data sources as chart data
- **Use Cases:**
  - Trend analysis over time
  - Multi-source temporal visualization
  - Historical data trending
- **Key Features:**
  - Multiple data source support
  - Efficient temporal rendering
  - Time-based axis

#### **7. XY Chart**
- **Category:** Chart / Cartesian
- **Purpose:** Cartesian coordinate system data visualization
- **Use Cases:**
  - Correlation analysis
  - Scatter plot visualization
  - X-Y relationship mapping
- **Key Features:**
  - Two-axis plotting
  - Point-based data representation
  - Coordinate mapping

---

## Container Palette

**Purpose:** Provide layout and organizational structure for Perspective components within views.

### Container Components Overview

| Component | Purpose |
|-----------|---------|
| Breakpoint Container | Responsive layout with breakpoint-based display |
| Column Container | Single or multiple column layout structure |
| Coordinate Container | Absolute positioning layout (default for new views) |
| Flex Container | Flexible box-based responsive layout |
| Tab Container | Tabbed interface with multiple panels |
| Split Container | Resizable split panel layout |

### Detailed Component Specifications

#### **Container Design Principles**

All container components enable:
- **Responsive Design:** Supporting different layout strategies
- **Multi-screen Compatibility:** Display information across varied screen sizes and orientations
- **Component Organization:** Hierarchical organization of perspective components

**Important:** Once a container type is selected as the root container when creating a new view, it cannot be changed after view creation. The system remembers your last-used container type for subsequent view creations.

#### **1. Breakpoint Container**
- **Category:** Container / Responsive
- **Purpose:** Responsive layout that adapts based on configured breakpoints
- **Use Cases:**
  - Mobile-responsive dashboards
  - Multi-device applications
  - Dynamic layout adaptation
- **Key Features:**
  - Breakpoint-based display logic
  - Responsive component positioning
  - Conditional layout switching
- **Common Properties:**
  - Breakpoint configurations
  - Layout rules per breakpoint
  - Component visibility settings

#### **2. Column Container**
- **Category:** Container / Structured Layout
- **Purpose:** Organize components into single or multiple column layouts
- **Use Cases:**
  - Multi-column data displays
  - Form layouts
  - Dashboard organization
- **Key Features:**
  - Configurable column counts
  - Component column assignment
  - Consistent alignment
- **Common Properties:**
  - Number of columns
  - Column width settings
  - Gap between columns

#### **3. Coordinate Container**
- **Category:** Container / Absolute Positioning
- **Purpose:** Absolute positioning layout system (default for new views)
- **Use Cases:**
  - Pixel-precise component positioning
  - Custom layout designs
  - Legacy-compatible layouts
- **Key Features:**
  - Absolute X, Y positioning
  - Z-index layering
  - Precise dimension control
- **Common Properties:**
  - Position (x, y)
  - Dimensions (width, height)
  - Z-order index

#### **4. Flex Container**
- **Category:** Container / Responsive
- **Purpose:** Flexible box-based responsive layout system
- **Use Cases:**
  - Modern responsive designs
  - Adaptive component layouts
  - Complex responsive grids
- **Key Features:**
  - Flex direction (row/column)
  - Alignment and distribution options
  - Responsive growth/shrink
- **Common Properties:**
  - flexDirection (row, column)
  - justifyContent, alignItems
  - flex-grow, flex-shrink properties

#### **5. Tab Container**
- **Category:** Container / Tabbed Interface
- **Purpose:** Organize components into tabbed panels
- **Use Cases:**
  - Multi-panel interfaces
  - Feature grouping
  - Space-saving layouts
- **Key Features:**
  - Tab creation and management
  - Tab panel switching
  - Dynamic tab configuration
- **Common Properties:**
  - tabList (active tab)
  - Tabs array (tab definitions)
  - Tab styling options

#### **6. Split Container**
- **Category:** Container / Resizable
- **Purpose:** Resizable split panel layout
- **Use Cases:**
  - Draggable panel layouts
  - Master-detail interfaces
  - Flexible workspace divisions
- **Key Features:**
  - Resizable divider
  - Two primary panels
  - Dynamic size adjustment
- **Common Properties:**
  - Divider position
  - Min/max panel sizes
  - Orientation (horizontal/vertical)

---

## Display Palette

**Purpose:** Components for visual information presentation and data display without user interaction.

### Display Components Overview

| Component | Purpose |
|-----------|---------|
| Alarm Journal Table | Display alarm event history |
| Alarm Status Table | Show current alarm statuses |
| Audio | Audio playback functionality |
| Barcode | Display text as barcode format |
| Cylindrical Tank | 3D cylindrical tank with liquid visualization |
| Dashboard | Dashboard display container |
| Drawing | Vector drawing capabilities |
| Equipment Schedule | Scheduling visualization |
| Google Map | Map integration component |
| Icon | SVG image icon collection access |
| Image | Vector or raster image display |
| Inline Frame | Display webpage within component |
| Label | Text display with customization |
| LED Display | Stylized numeric/alphanumeric display |
| Linear Scale | Tick marks and labels display |
| Map | Map visualization component |
| Markdown | Formatted text display |
| Moving Analog Indicator | Analog value display |
| PDF Viewer | PDF document viewing |
| Progress | Task progress visual indicator |
| Sparkline | Minimalistic line-chart history |
| Table | Data table display |
| Tag Browse Tree | Tag navigation hierarchy |
| Thermometer | Temperature value display |
| Tree | Hierarchical tree view |
| Video Player | Video/live feed embedding |

### Detailed Component Specifications

#### **1. Alarm Journal Table**
- **Category:** Display / Monitoring
- **Purpose:** Displays alarm event history with timestamp and details
- **Use Cases:**
  - Alarm event logs
  - Historical alarm tracking
  - Incident analysis
- **Key Features:**
  - Time-sorted alarm events
  - Alarm severity indicators
  - Event timestamp display

#### **2. Alarm Status Table**
- **Category:** Display / Monitoring
- **Purpose:** Shows current active alarms and their statuses
- **Use Cases:**
  - Real-time alarm monitoring
  - System health dashboards
  - Alert overview
- **Key Features:**
  - Current alarm listing
  - Severity-based highlighting
  - Status indication

#### **3. Audio**
- **Category:** Display / Multimedia
- **Purpose:** Audio playback functionality
- **Use Cases:**
  - Alert audio notifications
  - Media content playback
  - Sound feedback
- **Key Features:**
  - Audio file support
  - Playback controls
  - Volume management

#### **4. Barcode**
- **Category:** Display / Identification
- **Purpose:** Enables display of text as barcode
- **Use Cases:**
  - Product barcode display
  - Item identification
  - Tracking number visualization
- **Key Features:**
  - Text-to-barcode conversion
  - Barcode format options
  - Scalable rendering

#### **5. Cylindrical Tank**
- **Category:** Display / Industrial Visualization
- **Purpose:** 3D cylindrical tank with liquid visualization
- **Use Cases:**
  - Fluid level monitoring
  - Tank content display
  - Volume visualization
- **Key Features:**
  - 3D rendering
  - Liquid level animation
  - Capacity indication

#### **6. Dashboard**
- **Category:** Display / Container
- **Purpose:** Dashboard display container
- **Use Cases:**
  - Multi-component dashboard layout
  - Information aggregation
  - KPI presentations
- **Key Features:**
  - Component grouping
  - Layout management
  - Customizable display

#### **7. Drawing**
- **Category:** Display / Graphics
- **Purpose:** Vector drawing capabilities
- **Use Cases:**
  - Custom graphics rendering
  - Schematic diagrams
  - Visual representations
- **Key Features:**
  - Vector drawing support
  - Shape rendering
  - Custom graphics

#### **8. Equipment Schedule**
- **Category:** Display / Scheduling
- **Purpose:** Scheduling visualization
- **Use Cases:**
  - Equipment maintenance schedules
  - Downtime visualization
  - Timeline displays
- **Key Features:**
  - Schedule representation
  - Timeline visualization
  - Status indication

#### **9. Google Map**
- **Category:** Display / Mapping
- **Purpose:** Map integration component
- **Use Cases:**
  - Location visualization
  - Geographic data display
  - Asset tracking maps
- **Key Features:**
  - Google Maps integration
  - Marker placement
  - Zoom and pan controls

#### **10. Icon**
- **Category:** Display / Graphics
- **Purpose:** Provides access to SVG image collection
- **Use Cases:**
  - UI iconography
  - Status indicators
  - Visual elements
- **Key Features:**
  - SVG icon library access
  - Scalable graphics
  - Color customization

#### **11. Image**
- **Category:** Display / Media
- **Purpose:** Displays vector or raster images (JPEG, GIF, PNG, SVG)
- **Use Cases:**
  - Image display
  - Logo rendering
  - Picture galleries
- **Key Features:**
  - Multiple format support
  - Scaling options
  - Aspect ratio preservation

#### **12. Inline Frame**
- **Category:** Display / Embedding
- **Purpose:** Enables display of webpage within component
- **Use Cases:**
  - External content embedding
  - Web page integration
  - Iframe-based content
- **Key Features:**
  - Webpage embedding
  - Source URL configuration
  - Responsive sizing

#### **13. Label**
- **Category:** Display / Text
- **Purpose:** Displays text with customization
- **Use Cases:**
  - Text labels
  - Information display
  - Dynamic text output
- **Key Features:**
  - Text content display
  - Font customization
  - Color and style options

#### **14. LED Display**
- **Category:** Display / Industrial
- **Purpose:** Stylized numeric and/or alphanumeric label
- **Use Cases:**
  - Digital readouts
  - Numeric displays
  - Counter displays
- **Key Features:**
  - LED-style rendering
  - Numeric/alphanumeric support
  - Customizable styling

#### **15. Linear Scale**
- **Category:** Display / Measurement
- **Purpose:** Displays series of tick marks and labels
- **Use Cases:**
  - Scale visualization
  - Measurement reference
  - Range indication
- **Key Features:**
  - Tick mark generation
  - Label placement
  - Scale configuration

#### **16. Map**
- **Category:** Display / Mapping
- **Purpose:** Map visualization component
- **Use Cases:**
  - Location display
  - Geographic visualization
  - Asset mapping
- **Key Features:**
  - Map rendering
  - Marker support
  - Zoom/pan controls

#### **17. Markdown**
- **Category:** Display / Text Formatting
- **Purpose:** Formatted text display
- **Use Cases:**
  - Rich text content
  - Documentation display
  - Formatted instructions
- **Key Features:**
  - Markdown parsing
  - Rich text rendering
  - Format support

#### **18. Moving Analog Indicator**
- **Category:** Display / Measurement
- **Purpose:** Analog value display
- **Use Cases:**
  - Gauge-like displays
  - Analog readings
  - Value indication
- **Key Features:**
  - Needle/pointer animation
  - Range visualization
  - Smooth value updates

#### **19. PDF Viewer**
- **Category:** Display / Document
- **Purpose:** PDF document viewing
- **Use Cases:**
  - PDF document display
  - Report viewing
  - Document presentation
- **Key Features:**
  - PDF rendering
  - Navigation controls
  - Zoom functionality

#### **20. Progress**
- **Category:** Display / Feedback
- **Purpose:** Visually indicates progress of a task
- **Use Cases:**
  - Progress bars
  - Completion indicators
  - Status visualization
- **Key Features:**
  - Progress percentage display
  - Bar visualization
  - Animated progression

#### **21. Sparkline**
- **Category:** Display / Chart
- **Purpose:** Minimalistic line-chart history for a single datapoint
- **Use Cases:**
  - Trend sparklines
  - Inline charts
  - Quick trend visualization
- **Key Features:**
  - Compact chart rendering
  - Single datapoint support
  - Inline display

#### **22. Table**
- **Category:** Display / Data
- **Purpose:** Data table display
- **Use Cases:**
  - Tabular data presentation
  - Data browsing
  - Information organization
- **Key Features:**
  - Column-based layout
  - Row data display
  - Sorting and filtering

#### **23. Tag Browse Tree**
- **Category:** Display / Navigation
- **Purpose:** Tag navigation hierarchy
- **Use Cases:**
  - Tag structure browsing
  - Hierarchical tag selection
  - Tag navigation
- **Key Features:**
  - Tag tree structure
  - Expandable nodes
  - Tag path navigation

#### **24. Thermometer**
- **Category:** Display / Industrial
- **Purpose:** Displays temperature value as mercury thermometer level
- **Use Cases:**
  - Temperature monitoring
  - Thermal display
  - HVAC visualization
- **Key Features:**
  - Mercury-style visualization
  - Temperature scaling
  - Visual level indication

#### **25. Tree**
- **Category:** Display / Navigation
- **Purpose:** Hierarchical tree view
- **Use Cases:**
  - Hierarchical data display
  - Tree structure visualization
  - Nested item browsing
- **Key Features:**
  - Expandable/collapsible nodes
  - Hierarchical structure
  - Tree navigation

#### **26. Video Player**
- **Category:** Display / Multimedia
- **Purpose:** Enables embedding video or live feed
- **Use Cases:**
  - Video content playback
  - Live feed monitoring
  - Media presentation
- **Key Features:**
  - Video file support
  - Live stream support
  - Playback controls

---

## Input Palette

**Purpose:** Components for user interaction and data entry.

### Input Components Overview

| Component | Purpose |
|-----------|---------|
| Barcode Scanner Input | Input from barcode scanner devices |
| Button | Initiate actions on press |
| Checkbox | Binary state selection (on/off) |
| DateTime Input | Date selection via popup calendar |
| DateTime Picker | Combined date and time selection |
| Dropdown | Display list of choices in limited space |
| File Upload | File selection and upload |
| Form | Form container and submission |
| Multi-State Button | Multiple button series (column/row) |
| Numeric Entry Field | Specialized numeric input |
| One-Shot Button | Send write request and wait for response |
| Password Field | Masked text input |
| Radio Group | Multiple radio buttons in container |
| Signature Pad | Digital signature capture |
| Slider | Drag indicator along scale |
| Text Area | Multi-line text input/display |
| Text Field | Single-line text input |
| Toggle Switch | Binary state selection (on/off) |

### Detailed Component Specifications

#### **1. Barcode Scanner Input**
- **Category:** Input / Specialized
- **Purpose:** Awaits input from barcode scanner devices
- **Use Cases:**
  - Product scanning
  - Asset scanning
  - Barcode data entry
- **Key Features:**
  - Barcode scanner support
  - Input capture
  - Validation options
- **Common Bindings:**
  - Scanned value binding
  - Validation rules

#### **2. Button**
- **Category:** Input / Action
- **Purpose:** Used to initiate some sort of action in response to being pressed
- **Use Cases:**
  - Form submission
  - Action triggering
  - Event initiation
- **Key Features:**
  - Click event handling
  - Label customization
  - Disabled state support
- **Common Bindings:**
  - onClick event handler
  - Enabled/disabled state

#### **3. Checkbox**
- **Category:** Input / Selection
- **Purpose:** Represents a bit - either on (selected) or off (not selected)
- **Use Cases:**
  - Boolean selection
  - Feature toggles
  - Multiple option selection
- **Key Features:**
  - Binary state management
  - Label support
  - Indeterminate state option
- **Common Bindings:**
  - Checked state binding
  - Change event handler
- **Common Properties:**
  - value (boolean)
  - label (string)
  - disabled (boolean)

#### **4. DateTime Input**
- **Category:** Input / Date-Time
- **Purpose:** Easy way to select a date from popup calendar
- **Use Cases:**
  - Date selection forms
  - Date filtering
  - Date picker interface
- **Key Features:**
  - Calendar popup
  - Date validation
  - Format options
- **Common Bindings:**
  - Selected date value
  - Change event handler
- **Common Properties:**
  - value (date)
  - format (string)
  - disabled (boolean)

#### **5. DateTime Picker**
- **Category:** Input / Date-Time
- **Purpose:** Uses calendar to select date and time
- **Use Cases:**
  - Date and time selection
  - Appointment scheduling
  - Timestamp input
- **Key Features:**
  - Combined date/time selection
  - Calendar interface
  - Time picker
- **Common Bindings:**
  - DateTime value binding
  - Change event handler
- **Common Properties:**
  - value (datetime)
  - format (string)
  - disabled (boolean)

#### **6. Dropdown**
- **Category:** Input / Selection
- **Purpose:** Display list of choices in limited amount of space
- **Use Cases:**
  - Option selection
  - Menu-based choices
  - Value selection
- **Key Features:**
  - Collapsible list
  - Option selection
  - Dynamic option binding
- **Common Bindings:**
  - Selected value
  - Option list source
  - Change event handler
- **Common Properties:**
  - value (selected option)
  - options (array of choices)
  - disabled (boolean)

#### **7. File Upload**
- **Category:** Input / File
- **Purpose:** File selection and upload
- **Use Cases:**
  - File submission
  - Document upload
  - Media file selection
- **Key Features:**
  - File selection dialog
  - Upload handling
  - File type restrictions
- **Common Bindings:**
  - Selected file binding
  - Upload event handler

#### **8. Form**
- **Category:** Input / Container
- **Purpose:** Form container and submission
- **Use Cases:**
  - Data entry forms
  - Form-based interfaces
  - Multi-field input
- **Key Features:**
  - Form field grouping
  - Submission handling
  - Validation support
- **Common Bindings:**
  - Form data binding
  - Submit handler

#### **9. Multi-State Button**
- **Category:** Input / Action
- **Purpose:** Series of two or more buttons arranged in column or row
- **Use Cases:**
  - Multiple action options
  - State selection buttons
  - Option grouping
- **Key Features:**
  - Multiple button support
  - Row/column arrangement
  - State management
- **Common Bindings:**
  - Selected button state
  - Button click handlers

#### **10. Numeric Entry Field**
- **Category:** Input / Numeric
- **Purpose:** Specialized for use with numbers
- **Use Cases:**
  - Numeric data entry
  - Quantity input
  - Numeric calculations
- **Key Features:**
  - Number-only input
  - Min/max validation
  - Decimal support
- **Common Bindings:**
  - Numeric value binding
  - Change event handler
- **Common Properties:**
  - **inputBounds:**
    - **min:** Minimum numeric value
    - **max:** Maximum numeric value
  - step (increment value)
  - value (number)
  - disabled (boolean)
- **Validation:**
  - Range checking (min/max)
  - Decimal places control

#### **11. One-Shot Button**
- **Category:** Input / Action
- **Purpose:** Designed to send off a write request and wait for response
- **Use Cases:**
  - Command execution
  - Data write operations
  - Confirmable actions
- **Key Features:**
  - Write request initiation
  - Response waiting
  - Action confirmation
- **Common Bindings:**
  - Write target binding
  - Response handler

#### **12. Password Field**
- **Category:** Input / Text
- **Purpose:** Similar to Text Field component but with masked input
- **Use Cases:**
  - Password entry
  - Credential input
  - Secure text input
- **Key Features:**
  - Masked character display
  - Password validation
  - Security options
- **Common Bindings:**
  - Password value binding
  - Change event handler
- **Common Properties:**
  - value (string)
  - placeholder (string)
  - disabled (boolean)

#### **13. Radio Group**
- **Category:** Input / Selection
- **Purpose:** Create multiple radio buttons in single container
- **Use Cases:**
  - Single option selection
  - Mutually exclusive choices
  - Option grouping
- **Key Features:**
  - Radio button grouping
  - Single selection enforcement
  - Option labeling
- **Common Bindings:**
  - Selected value binding
  - Change event handler
- **Common Properties:**
  - value (selected option)
  - options (array of choices)
  - disabled (boolean)

#### **14. Signature Pad**
- **Category:** Input / Capture
- **Purpose:** Digital signature capture
- **Use Cases:**
  - Signature collection
  - Document signing
  - Approval capture
- **Key Features:**
  - Touch/mouse drawing
  - Signature capture
  - Image export

#### **15. Slider**
- **Category:** Input / Numeric
- **Purpose:** Drag indicator along scale to choose value in range
- **Use Cases:**
  - Range selection
  - Volume control
  - Value adjustment
- **Key Features:**
  - Draggable handle
  - Range visualization
  - Numeric value output
- **Common Bindings:**
  - Slider value binding
  - Change event handler
- **Common Properties:**
  - value (number)
  - min (minimum)
  - max (maximum)
  - step (increment)

#### **16. Text Area**
- **Category:** Input / Text
- **Purpose:** Suitable for multi-line text display and editing
- **Use Cases:**
  - Long text input
  - Comments/notes
  - Multi-line content
- **Key Features:**
  - Multi-line support
  - Text editing
  - Scrolling support
- **Common Bindings:**
  - Text value binding
  - Change event handler
- **Common Properties:**
  - value (string)
  - placeholder (string)
  - rows (height)
  - disabled (boolean)

#### **17. Text Field**
- **Category:** Input / Text
- **Purpose:** Used for input of any single-line text
- **Use Cases:**
  - Text input
  - Search fields
  - Name/email entry
- **Key Features:**
  - Single-line text entry
  - Text validation
  - Format options
- **Common Bindings:**
  - Text value binding
  - Change event handler
- **Common Properties:**
  - value (string)
  - placeholder (string)
  - disabled (boolean)
  - type (email, password, etc.)

#### **18. Toggle Switch**
- **Category:** Input / Selection
- **Purpose:** Represents a bit: on (selected) or off (not selected)
- **Use Cases:**
  - Boolean toggle
  - Feature enable/disable
  - On/off switches
- **Key Features:**
  - Binary state toggle
  - Visual on/off indication
  - Labeled options
- **Common Bindings:**
  - Toggle state binding
  - Change event handler
- **Common Properties:**
  - value (boolean)
  - disabled (boolean)

---

## Navigation Palette

**Purpose:** Components for designing user navigation within Perspective applications.

### Navigation Components Overview

| Component | Purpose |
|-----------|---------|
| Horizontal Menu | Horizontal menu navigation |
| Link | Hyperlink navigation to pages/views/resources |
| Menu Tree | Tree-based navigation menu |

### Detailed Component Specifications

#### Navigation Design Principles

A solid navigation design is critical so users understand:
- Their current location within the application
- Navigation history and how they got there
- Available paths forward and navigation options

#### **1. Horizontal Menu**
- **Category:** Navigation / Menu
- **Purpose:** Horizontal menu navigation component
- **Use Cases:**
  - Top navigation bars
  - Horizontal menu structures
  - Primary navigation
- **Key Features:**
  - Horizontal item layout
  - Menu structure support
  - Active state indication
- **Common Properties:**
  - Menu items configuration
  - Active item highlighting
  - Selection handling

#### **2. Link**
- **Category:** Navigation / Hyperlink
- **Purpose:** Allows users to create a hyperlink that points to a destination such as a page, view, resource, or mount path
- **Use Cases:**
  - View navigation
  - External link navigation
  - Resource access
  - Page jumping
- **Key Features:**
  - Multiple destination types support
  - Click-based navigation
  - URL/path support
- **Common Bindings:**
  - Destination link
  - Click event handler
- **Common Properties:**
  - text (link label)
  - url (destination)
  - disabled (boolean)

#### **3. Menu Tree**
- **Category:** Navigation / Menu
- **Purpose:** Tree-based navigation menu
- **Use Cases:**
  - Hierarchical navigation
  - Tree menu structures
  - Multi-level navigation
- **Key Features:**
  - Expandable/collapsible nodes
  - Hierarchical structure
  - Selection handling
- **Common Properties:**
  - Tree structure configuration
  - Active item highlighting
  - Node selection

---

## Embedding Palette

**Purpose:** Components for embedding and repeating views within other views, enabling modular and reusable interface construction.

### Embedding Components Overview

| Component | Purpose |
|-----------|---------|
| Accordion | Content organization in collapsible panels |
| Carousel | Rotating view display |
| Embedded View | Include entire view inside another |
| Flex Repeater | Create multiple instances of views |
| View Canvas | Dynamic view rendering |

### Detailed Component Specifications

#### **General Characteristic:**
Each embedding component can be embedded in multiple views of a project, enabling reusable, modular interface construction.

#### **1. Accordion**
- **Category:** Embedding / Container
- **Purpose:** Component for organizing content hierarchically in collapsible panels
- **Use Cases:**
  - Content organization
  - Space-saving layouts
  - Expandable sections
- **Key Features:**
  - Collapsible panels
  - Hierarchical organization
  - Single/multiple expansion modes
- **Common Properties:**
  - Panel configuration
  - Expansion state
  - Active panel tracking

#### **2. Carousel**
- **Category:** Embedding / Display
- **Purpose:** Allows you to display a selection of rotating views
- **Use Cases:**
  - Rotating content display
  - Slideshow functionality
  - View rotation
- **Key Features:**
  - Cyclic view presentation
  - Multiple view support
  - Rotation controls
- **Common Properties:**
  - View list
  - Rotation timing
  - Navigation controls

#### **3. Embedded View**
- **Category:** Embedding / View Container
- **Purpose:** Allows you to include an entire view inside another
- **Key Use Case:** Instantiates a view as a reusable component within parent views
- **Functionality:** Supports view composition and modular interface design
- **Use Cases:**
  - View reuse
  - Component encapsulation
  - Modular interface design
- **Key Features:**
  - View instantiation
  - Parameter passing
  - Reusable view components
- **Common Bindings:**
  - View path binding
  - Parameter bindings
- **Common Properties:**
  - view (view path)
  - params (object)
  - instanceId (unique identifier)

#### **4. Flex Repeater**
- **Category:** Embedding / Repeater
- **Purpose:** Lets you easily create multiple instances of views for display in another view
- **Key Feature:** Generates duplicated component instances maintaining the same look, feel, and functionality
- **Use Cases:**
  - Dynamic list generation
  - Repeated component instantiation
  - Data-driven view creation
- **Key Features:**
  - Multiple view instances
  - Consistent appearance/functionality
  - Data-driven instantiation
- **Common Bindings:**
  - Data source array binding
  - Instance parameter bindings
- **Common Properties:**
  - instances (array data)
  - view (template view path)
  - instanceId (identifier)

#### **5. View Canvas**
- **Category:** Embedding / Dynamic Rendering
- **Purpose:** Component for dynamic view rendering and management
- **Use Cases:**
  - Dynamic view rendering
  - Runtime view management
  - Flexible view loading
- **Key Features:**
  - Dynamic view rendering
  - Runtime view switching
  - Flexible view management
- **Common Properties:**
  - View configuration
  - Rendering options
  - Dynamic switching

---

## Special Components

**Purpose:** Special-purpose components that don't fit standard palettes.

### Special Components Overview

| Component | Purpose |
|-----------|---------|
| Report Viewer | Embed reports from Reporting Module |
| View Object | Base container for all Perspective content |

### Detailed Component Specifications

#### **1. Report Viewer**
- **Category:** Special / Reporting
- **Purpose:** Allows embedding reports from the Reporting Module into a Perspective view
- **Use Cases:**
  - Report viewing in views
  - Report embedding
  - Integrated report display
- **Key Properties:**

| Property | Type | Description |
|----------|------|-------------|
| **source** | string | Path to report from Reporting Module (case-sensitive), e.g., "Folder/ReportName" |
| **params** | object | Report parameters override defaults; names must match report parameters exactly |
| **page** | numeric | Current page displayed; updates as users navigate |
| **pageCount** | numeric | Read-only property showing total number of pages |
| **zoomLevel** | numeric | Zoom percentage relative to report width; 1 = "Fit Panel" |
| **allowDownload** | boolean | Enables PDF download icon (disabled on mobile apps) |
| **downloadFilename** | string | Custom filename for downloads; defaults to report name if blank |
| **allowOpenInTab** | boolean | Enables icon to open report in new tab (disabled on Workstation/mobile) |
| **controlStyle** | object | CSS styling for control bar and bottom controls |
| **style** | object | CSS styling for component background |

- **Interface Controls:**
  - **Zoom:** Adjusts PDF view magnification
  - **Pager:** Displays current page; allows page navigation
  - **Download:** Exports report as PDF
  - **Popout:** Opens report in separate window

- **Configuration Essentials:**
  1. Copy report path via right-click in Project Browser
  2. Set `source` property with copied path
  3. Define parameters under `params` object matching report definitions
  4. Parameters override default report values when specified

- **Common Bindings:**
  - Source property for dynamic report selection
  - Params object for dynamic parameter binding

#### **2. View Object**
- **Category:** Special / View Container
- **Purpose:** The view itself - serves as container foundation managing view size, tag drop behavior, and client-side loading configurations
- **Key Properties:**

| Property | Type | Function |
|----------|------|----------|
| **defaultSize** | numeric | Controls view dimensions (width/height, default 800px each) |
| **dropConfig** | object | Configures automatic view instantiation via tag drops |
| **loading** | object | Manages view load strategy (blocking/non-blocking modes) |
| **inputBehavior** | object | Determines parameter merging vs. replacement behavior |

- **Tag Handling (dropConfig):**

  Supports two tag scenarios:
  
  1. **UDT Instances:** Associates view with User-Defined Types; parameters pass UDT member values into view
  2. **Standard Tags:** Links views to regular tag data types; passes tag path strings or binding references
  
  Each supports either "bind" mode (automatic tag binding) or "path" mode (tag path string passing)

- **Loading Options:**

  Two modes optimize performance:
  - **Blocking:** For simpler views
  - **Non-blocking:** For high-component views (allows up to five seconds before timeout)

- **Parameter Behavior:**

  The `inputBehavior` property controls how supplied parameters interact with defaults:
  - **Merge:** Combines supplied parameters with defaults
  - **Replace:** Replaces entire parameter object

- **Access:** Accessed via Project Browser; controls view properties that affect component behavior

---

## Quick Reference: Common Property Types

### Binding Types
- **Simple Binding:** Direct tag or component property reference
- **Expression Binding:** Formula-based calculations
- **Script Binding:** Python-based dynamic values
- **Indirect Binding:** Tag path in property value

### Common Data Types
- **string:** Text values
- **numeric:** Integer or decimal numbers
- **boolean:** True/False binary values
- **object:** Complex nested property structures
- **array:** Indexed collections of values
- **date/datetime:** Date and timestamp values

### Common Events
- **onClick:** Triggered on component click
- **onChange:** Triggered on value change
- **onMouseEnter/Exit:** Triggered on mouse hover
- **onFocus/Blur:** Triggered on focus state change
- **onSubmit:** Triggered on form submission

---

## Component Selection Guide

### When to Use Each Category

| Category | Best For | Examples |
|----------|----------|----------|
| **Chart** | Data visualization and trending | KPIs, trends, historical data |
| **Container** | Layout and organization | Dashboards, forms, grid layouts |
| **Display** | Information presentation | Metrics, alarms, reports, media |
| **Input** | User data entry | Forms, selections, configurations |
| **Navigation** | Movement between views | Menus, links, hierarchical navigation |
| **Embedding** | View composition | Reusable components, dynamic lists |
| **Special** | Reports and view configuration | Report viewing, view setup |

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-13  
**Reference:** Ignition 8.3 Perspective Component Documentation

---

## See Also

**Prerequisites:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md)

**Builds toward:** [Components/README](Components/README.md)

**Related:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [Components/README](Components/README.md), [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
