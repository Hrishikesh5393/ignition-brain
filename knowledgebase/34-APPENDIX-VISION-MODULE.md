> **Skill level:** 200 · **Read first:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 34-APPENDIX-VISION-MODULE

# Vision Module Reference | Ignition 8.3

**Version**: 8.3  
**Module Type**: Desktop Client Application UI Framework  
**Status**: Mature, Stable  
**Documentation**: docs.inductiveautomation.com/docs/8.3/appendix/components/vision-components

---

## Quick Reference

| Aspect | Details |
|--------|---------|
| **Primary Use** | Building rich desktop SCADA/HMI applications on Java Swing |
| **Deployment** | Vision Client (Java desktop application) - installed locally on workstations |
| **Component Palettes** | 12 (Display, Input, Buttons, Tables, Charts, Containers, Admin, Alarming, Misc, Calendar, Reporting, Window Object) |
| **Scripting** | Jython (Python 2.7 compatible) in event handlers and property bindings |
| **Comparison** | Vision = Desktop-focused, feature-rich. Perspective = Web-based, responsive, modern |

---

## 1. Vision Module Overview

### What is Vision?

Vision is Ignition's **desktop client framework** for building industrial automation interfaces. It provides a component-based, drag-and-drop development environment with rich UI components optimized for SCADA, HMI, and operations screens.

### Vision vs. Perspective

| Feature | Vision | Perspective |
|---------|--------|-------------|
| **Platform** | Desktop (Java Swing) | Web browser (HTML5) |
| **Client Type** | Installed application | Web client, responsive design |
| **Performance** | Excellent for complex UIs, rich interactivity | Good, lighter weight, mobile-ready |
| **Graphics** | Native Swing components, shapes, drawing | SVG, web-based graphics |
| **Use Case** | Control rooms, complex operator screens | Remote access, mobile, modern UIs |
| **Component Count** | Extensive, highly specialized | Modern, browser-compatible |

### When to Use Vision

✓ **Choose Vision If:**
- Building desktop SCADA applications with complex UIs
- Requiring high-performance graphics and animations
- Need rich shape/drawing capabilities (rotatable shapes, pipes, custom paint)
- Deploying to controlled, managed workstations (not public web)
- Integrating with legacy Vision applications
- Need advanced table features (Power Table)

✗ **Use Perspective Instead If:**
- Remote or web-based access required
- Mobile/tablet support needed
- Cross-platform browser deployment
- Modern responsive design expected
- Cloud/SaaS deployment model

### Vision Architecture

```
Vision Client (Java Desktop Application)
  ↓
Local Workstations (Windows, Linux, Mac)
  ↓
Ignition Gateway
  ↓
Devices/PLCs (OPC-UA, Modbus, etc.)
```

---

## 2. Vision Components Reference

### Component Palettes Overview

| Palette | Purpose | Primary Use |
|---------|---------|-------------|
| **Display** | Information presentation | Labels, images, gauges, indicators |
| **Input** | Data entry & selection | Text fields, sliders, dropdowns |
| **Buttons** | User interaction | Buttons, toggles, radio buttons |
| **Tables** | Data grids & hierarchies | Tabular data display and editing |
| **Charts** | Data visualization | Real-time trends, statistical charts |
| **Containers** | Layout & structure | Panels, templates, windows |
| **Admin** | System administration | User/roster/schedule management |
| **Alarming** | Alarm display | Alarm status, alarm journal |
| **Misc** | Utilities & interactivity | Canvas, shapes, timers, sound |
| **Calendar** | Date/time selection | Date pickers (if available) |
| **Reporting** | Report integration | Report viewing/scheduling |
| **Window Object** | Window control | Properties, methods for window management |

---

## 3. Vision Components by Category

### 3.1 Display Components

Used to show information to the operator in various visual formats.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Label** | Text and image display | Text (plain or HTML), image support, color/font customization |
| **Numeric Label** | Numeric value display | Specialized for numbers, formatting options |
| **Multi-State Indicator** | Discrete state display | Shows different appearances for different values |
| **LED Display** | LED-style numeric display | Alphanumeric, mimics LED appearance |
| **Moving Analog Indicator** | Analog gauge | Shows value, displays normal range context |
| **Image** | Image display | Multiple display options beyond basic image rendering |
| **Progress Bar** | Task progress visualization | Bounded value display, % completion |
| **Cylindrical Tank** | 3D tank level display | Realistic 3D cylindrical tank visualization |
| **Level Indicator** | Liquid level display | Rises/falls with value changes |
| **Linear Scale** | Range/scale display | Tick marks, labels, value indicators on scale |
| **Barcode** | Barcode rendering | Text to barcode conversion (1D barcodes) |
| **Meter** | Analog meter gauge | (See detailed specs in Ignition docs) |
| **Compass** | Directional indicator | (See detailed specs in Ignition docs) |
| **Thermometer** | Temperature display | Thermometer-style visualization |
| **IP Camera Viewer** | Video stream display | Real-time camera feed embedding |

### 3.2 Input Components

Used to collect data from operators or provide user interaction.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Text Field** | Single-line text input | Basic text entry, binding support |
| **Numeric Text Field** | Numeric value input | Input validation, numeric-only |
| **Spinner** | Series value selection | Increment/decrement buttons, supports numbers/dates |
| **Formatted Text Field** | Pattern-based text input | Regex validation, format masking |
| **Password Field** | Secure password input | Masked input, customizable echo character |
| **Text Area** | Multi-line text input | Vertical scrolling, word wrap |
| **Dropdown List** | Single-choice selection | Compact space usage, dynamic options |
| **Slider** | Range value selection | Horizontal or vertical, draggable |
| **Language Selector** | Locale selection | Date/time/number formats, UI translations |

### 3.3 Button Components

Used for user actions and state toggling.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Button** | Push-button action | Display/write values, standard button behavior |
| **2 State Toggle** | On/Off switching | Toggle between two states (Stop/Run, Off/On) |
| **Multi-State Button** | Multiple options | Column/row/grid arrangement of buttons |
| **One-Shot Button** | Single trigger action | Writes value, waits for PLC reset before reuse |
| **Momentary Button** | Timed action | Holds value for fixed time or while held |
| **Toggle Button** | Bit state control | Selected (1) / Unselected (0) appearance |
| **Check Box** | Boolean selection | Standard checkbox for on/off states |
| **Radio Button** | Mutually exclusive choice | Auto-exclusive within container |
| **Tab Strip** | Window/view switcher | Single-selection multiple-choice component |

### 3.4 Table Components

Used for displaying and managing tabular data.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Table** | Standard data grid | Row/column display, scrollable |
| **Power Table** | Enhanced data grid | Advanced features (sorting, filtering, editing) |
| **List** | Vertical item list | Single-column list display |
| **Tree View** | Hierarchical data | Parent/child node display, expandable |
| **Comments Panel** | Comment management | Comment display and management interface |
| **Tag Browse Tree** | Tag hierarchy browser | Specialized tree for browsing Ignition tag providers |

### 3.5 Chart Components

Used for data visualization and trend analysis.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Sparkline Chart** | Compact trend sparkline | Single datapoint history, minimal display |
| **Radar Chart** | Multi-dimensional data | Spider/web chart for comparative analysis |
| **Box and Whisker Chart** | Statistical distribution | Shows mean, quartiles, outliers |
| **Easy Chart** | General-purpose charting | Flexible data visualization |
| **Chart** | Standard chart component | Core charting functionality |
| **Bar Chart** | Categorical data bars | Vertical/horizontal bar visualization |
| **Status Chart** | Status-based visualization | Status-indexed data display |
| **Pie Chart** | Proportional data | Pie slice visualization |
| **Equipment Schedule** | Timeline visualization | Equipment timeline display |
| **Gantt Chart** | Project timeline | Scheduling and Gantt visualization |

### 3.6 Container Components

Used for layout, grouping, and structural organization.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Container** | Generic grouping/layout | All components must be in container, supports nesting |
| **Template Repeater** | Repeating template instances | Dynamic template repetition |
| **Template Canvas** | Template display canvas | Canvas-based template rendering |

### 3.7 Miscellaneous Components

Specialized tools for graphics, animation, and interaction.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Paintable Canvas** | Custom graphics rendering | Jython script painting, pixel-level control |
| **Line** | Vector line drawing | N-S, E-W, or diagonal; stroke customization |
| **Pipe Segment** | 3D pipe visualization | Quasi-3D pipe rendering |
| **Pipe Joint** | Pipe connector | 3D joint visualization between pipes |
| **Sound Player** | Audio playback | Invisible component for audio events |
| **Timer** | Timed event trigger | Invisible, creates repeated events |
| **Signal Generator** | Value generation | Generates repeating values beyond counting |
| **Web Browser** | Embedded web content | HTML/web content embedding |

### 3.8 Admin Components

Used for system administration tasks.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Roster Management** | User/resource roster admin | Administrative interface |
| **User Management** | User account admin | User creation, roles, permissions |
| **Schedule Management** | Schedule admin | Schedule creation and editing |
| **SFC Monitor** | SFC performance monitoring | Sequential Function Chart monitoring |

### 3.9 Alarming Components

Used for alarm display and monitoring.

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Alarm Status Table** | Current alarm display | Real-time active alarms |
| **Alarm Journal Table** | Alarm history | Historical alarm events |

---

## 4. Vision Scripting & Scripting APIs

### Scripting Language

- **Language**: Jython (Python 2.7-compatible subset)
- **Context**: Event handlers, property bindings, gateway scripts
- **Module Access**: system.* functions for gateway operations

### Vision System Functions (system.vision.*)

| Function | Purpose | Syntax |
|----------|---------|--------|
| `system.vision.openWindow()` | Open Vision window | `system.vision.openWindow(path, title, [params])` |
| `system.vision.closeWindow()` | Close Vision window | `system.vision.closeWindow(window)` |
| `system.vision.setWindowProperty()` | Modify window property | `system.vision.setWindowProperty(window, name, value)` |
| `system.vision.getWindowProperty()` | Read window property | `system.vision.getWindowProperty(window, name)` |
| `system.vision.getOpenedWindows()` | List open windows | `system.vision.getOpenedWindows()` |
| `system.vision.getActiveWindow()` | Get focused window | `system.vision.getActiveWindow()` |

### Common Vision Event Handlers

| Event | Fired When | Access | Typical Use |
|-------|-----------|--------|------------|
| `onActionPerformed` | Button clicked / component action | Component scripts | Trigger actions |
| `onMouseClick` | Mouse click on component | Component scripts | Handle clicks |
| `onMouseEnter` | Mouse enters component | Component scripts | Hover effects |
| `onMouseExit` | Mouse leaves component | Component scripts | Cleanup hover |
| `onMouseMove` | Mouse moves over component | Component scripts | Track movement |
| `onKeyPress` | Key pressed while focused | Component scripts | Keyboard input |
| `onPropertyChange` | Property value changes | Window scripts | React to changes |
| `onFocusGained` | Component receives focus | Component scripts | Setup |
| `onFocusLost` | Component loses focus | Component scripts | Validation/cleanup |
| `onWindowOpen` | Window opens | Window scripts | Initialization |
| `onWindowClose` | Window closes | Window scripts | Cleanup |

### Window Object Properties & Methods

#### Common Window Properties
```python
window.title              # Window title (string)
window.width             # Window width in pixels
window.height            # Window height in pixels
window.visible           # Window visibility (boolean)
window.resizable         # Allow resize (boolean)
window.alwaysOnTop       # Always on top (boolean)
window.params            # Custom parameters passed to window
window.name              # Window name/identifier
```

#### Common Window Methods
```python
# Window control
window.closeWindow()                           # Close the window
window.setTitle(title)                         # Update title
window.maximize()                              # Maximize window
window.minimize()                              # Minimize window
window.focus()                                 # Bring to front
window.showData(data)                          # Pass data to window

# Component access
window.rootContainer.getComponent('name')      # Get component by name
window.getRootContainer()                      # Get root container
window.getComponentForPath('path.to.component')# Get component by path
```

### Vision Property Binding Syntax

#### Expression Binding
```python
{path.to.tag}              # Tag binding (most common)
{pow(2, 3)}                # Expression evaluation
{now()}                    # System time functions
{if(condition, true, false)}  # Conditional expression
```

#### Bidirectional Binding
- **Property Write**: `writeableTagPath`
- **Writable**: Select target tag for writes when component value changes

### Vision Scripting Best Practices

| Practice | Reason | Example |
|----------|--------|---------|
| Use tag bindings | Reactive updates, automatic sync | `{tagPath}` vs. script loops |
| Scope context | Avoid undefined reference errors | `event.source.parent` vs `window` |
| Handle exceptions | Prevent silent failures | `try/except` in event handlers |
| Use system functions | Gateway integration | `system.alarm.*`, `system.db.*` |
| Avoid long scripts | Maintainability, performance | Move complex logic to named queries |

---

## 5. Vision Client Deployment

### Client Installation Methods

#### 1. **Web Launch** (Recommended)
- Users navigate to: `http://gateway-ip:8088/`
- Auto-download and launch Vision client from browser
- Automatic updates
- No manual installation

#### 2. **Launcher Application**
- Standalone launcher.exe/launcher.jnlp
- Users run to launch any gateway application
- Supports multiple gateway connections
- Persistent local installation

#### 3. **Manual Desktop Shortcut**
- Administrators create shortcuts to `.jnlp` files
- Direct launch of specific gateway project
- Central management possible

### Client Deployment Architecture

```
Ignition Gateway (Port 8088, 8043)
    ↓
JNLP/Web Distribution
    ↓
Vision Client JAR Download
    ↓
Local Workstation (Windows/Linux/Mac)
    ↓
Vision Application Runtime
    ↓
OPC-UA, Modbus, Database Connections
```

### Client Requirements

| Requirement | Details |
|------------|---------|
| **Java Runtime** | Java 8+ (1.8 minimum), usually bundled |
| **Network** | TCP/IP connectivity to Ignition Gateway |
| **Ports** | 8088 (HTTP), 8043 (HTTPS), custom OPC ports |
| **OS Support** | Windows (XP SP3+), Linux, macOS |
| **Memory** | 256MB minimum, 512MB+ recommended |

### Client Configuration

#### Gateway Connection
```
File → Properties → Gateway Connection
```
- Gateway hostname/IP
- Port (default 8088)
- SSL/TLS options
- Proxy settings (if needed)

#### User Authentication
- Username/password authentication
- LDAP/Active Directory (if configured)
- Session timeout settings
- Automatic login (not recommended)

### Deployment Best Practices

| Best Practice | Implementation |
|---------------|-----------------|
| **HTTPS/SSL** | Enable SSL on gateway, auto-download updates securely |
| **Version Control** | Archive project versions, tag releases |
| **Change Notification** | Document updates, notify users before deployment |
| **Rollback Plan** | Keep previous version ready |
| **Staging Deployment** | Test in dev/test before production release |
| **Auto-Update** | Enable auto-update in client, stagger updates |

---

## 6. Vision Graphics & Drawing Tools

### Drawing Components

| Component | Use | Capabilities |
|-----------|-----|--------------|
| **Line** | Linear elements | Direction (N-S, E-W, diagonal), color, thickness |
| **Pipe Segment** | 3D piping diagrams | Horizontal/vertical pipes, 3D appearance |
| **Pipe Joint** | Pipe connections | Angles, T-joints, X-joints |
| **Paintable Canvas** | Custom graphics | Jython script rendering, pixel-level control |
| **Shape Objects** | Basic shapes | Rectangle, circle, polygon, etc. (configurable) |

### Jython Painting Script Example

```python
# Paintable Canvas onPaint event
def paint(self, graphics):
    # Draw custom graphics using Java Graphics2D
    from java.awt import Color, BasicStroke
    
    # Draw rectangle
    graphics.setColor(Color.blue)
    graphics.fillRect(10, 10, 100, 50)
    
    # Draw circle
    graphics.setColor(Color.red)
    graphics.fillOval(120, 10, 50, 50)
    
    # Draw line
    graphics.setStroke(BasicStroke(2.0))
    graphics.drawLine(0, 0, 200, 100)
```

### Rotation & Transformation

Vision shapes support:
- **Rotation**: Any angle
- **Z-Index**: Layering/stacking
- **Opacity**: Alpha transparency
- **Color**: Full RGB + transparency
- **Binding**: Dynamic property binding for animation

### Animation Techniques

1. **Property Binding Animation**
   ```python
   # Rotating component based on tag value
   Rotation: {tagValue * 3.6}  # 0-100 → 0-360°
   ```

2. **Timer Component Script Loop**
   ```python
   def onActionPerformed(self, event):
       # Timer fires repeatedly
       event.source.parent.rootContainer.getComponent('gauge').rotation += 1
   ```

3. **Transition/Easing**
   ```python
   # Smooth transition using property scripts
   from javax.swing import Timer
   # Implement easing over time intervals
   ```

---

## 7. Vision vs. Perspective: Feature Comparison

### Vision Advantages

| Feature | Vision | Perspective |
|---------|--------|-------------|
| **Graphics/Shapes** | Native rotation, custom paint | Limited, browser SVG |
| **Performance (complex UI)** | Excellent (native Swing) | Good (HTML5) |
| **Component richness** | 50+ specialized components | Modular, fewer specialized |
| **Legacy support** | Stable, proven | Newer, evolving |
| **Customization** | Unlimited scripting (Jython) | JavaScript limited |

### Perspective Advantages

| Feature | Vision | Perspective |
|---------|--------|-------------|
| **Web/Remote** | Requires desktop install | Instant browser access |
| **Mobile** | Desktop only | Responsive, mobile-ready |
| **Modern Design** | Java Swing look | Modern web UI components |
| **Cloud Deployment** | Workstation-based | SaaS-ready |
| **Cross-platform** | Desktop variations | Consistent browser rendering |

---

## 8. Legacy & Migration Guidance

### Vision Lifecycle Status

- **Status**: Mature, stable, legacy
- **New Projects**: Consider Perspective for new work
- **Existing Projects**: Vision remains fully supported
- **Deprecation Timeline**: None announced; long-term support planned

### Migration from Vision to Perspective

#### Challenges
1. **Component Parity**: Not all Vision components have Perspective equivalents
   - Power Table → Table component (different API)
   - IP Camera Viewer → Web component with embedded video
   - Pipe components → SVG drawing
   
2. **Scripting Model**: Jython (Python 2.7) → JavaScript
   - Syntax differences
   - Library incompatibilities
   
3. **Deployment Model**: Desktop application → Web-based
   - Network requirements change
   - Security model differs

#### Migration Strategy
```
Phase 1: Assess Component Usage
  ├─ Identify Perspective-compatible components
  ├─ Flag custom painting/scripting
  └─ Document Vision-specific features

Phase 2: Prototype Perspective Equivalent
  ├─ Redesign UI for responsive web
  ├─ Adapt scripting to JavaScript
  └─ Test on target browsers

Phase 3: Parallel Deployment
  ├─ Run Vision + Perspective versions
  ├─ Transition users gradually
  └─ Support both during transition

Phase 4: Decommission Vision
  ├─ Retire Vision application
  ├─ Archive project for reference
  └─ Document lessons learned
```

### Vision Components Without Perspective Equivalents

| Vision Component | Migration Path |
|-----------------|----------------|
| **Pipe Segment/Joint** | Use SVG shapes or custom components |
| **Power Table (advanced features)** | Use Table component + custom scripts |
| **IP Camera Viewer (MJPEG)** | Use HTML5 `<video>` or embedded web component |
| **Paintable Canvas** | Custom React component or Canvas element |
| **Moving Analog Indicator** | Custom gauge component |
| **Cylindrical Tank** | SVG 3D simulation or image-based |

---

## 9. Common Vision Recipes

### Opening a Window with Parameters

```python
params = {'deviceID': 12345, 'mode': 'view'}
system.vision.openWindow('GE_Main_Screen', params=params)
```

### Closing All Open Windows

```python
windows = system.vision.getOpenedWindows()
for window in windows:
    system.vision.closeWindow(window)
```

### Reading Component Value in Script

```python
value = event.source.parent.getComponent('TextFieldName').value
print("Current value: " + str(value))
```

### Conditional Component Visibility

```python
# Component Custom Method property
event.source.visible = {tagPath} > 100  # Shows if tag > 100
```

### Timer-Based Polling

```python
# Timer component onActionPerformed
event.source.parent.getComponent('label').text = \
    str(system.tag.read('[default]DeviceStatus').value)
```

---

## 10. Troubleshooting & Performance

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **Window won't open** | Path incorrect | Verify path in Designer, check window exists |
| **Slow UI response** | Complex binding/scripts | Optimize queries, use caching |
| **Component not updating** | Binding not configured | Check binding path, confirm tag exists |
| **Memory leak** | Unclosed resources | Implement cleanup in onWindowClose |
| **Script errors in console** | Undefined variables | Check scope, use `self` for components |

### Performance Tuning

| Optimization | Impact | Implementation |
|--------------|--------|-----------------|
| **Reduce binding frequency** | Moderate | Increase update rate if acceptable |
| **Use property bindings** | High | Avoid script loops; use expressions |
| **Cache static data** | High | Load once onWindowOpen, not per update |
| **Limit table rows** | High | Implement pagination/filtering |
| **Async processing** | Moderate | Move long operations to named queries |

---

## 11. Resources & References

### Official Documentation
- **Main**: docs.inductiveautomation.com/docs/8.3/
- **Appendix**: docs.inductiveautomation.com/docs/8.3/appendix/components/vision-components/
- **Scripting**: docs.inductiveautomation.com/docs/8.3/appendix/system-functions/

### Related Ignition Modules
- **Perspective**: Modern web-based UI alternative
- **Reporting**: Report generation and scheduling
- **OPC-UA**: Device connectivity standard
- **Database**: SQL query and data management

### External Resources
- **Jython Documentation**: wiki.python.org/jython/
- **Java Swing API**: Oracle Java Swing Tutorial
- **Inductive Automation Forums**: forum.inductiveautomation.com/

---

**Document Version**: 1.0  
**Last Updated**: July 2026  
**Compiled From**: Ignition 8.3 Official Documentation, User Manual, Appendix References

---

## See Also

**Prerequisites:** [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Builds toward:** [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md)

**Related:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [70a-MODULES-OVERVIEW](70a-MODULES-OVERVIEW.md), [31-SYSTEM-FUNCTIONS](31-SYSTEM-FUNCTIONS.md), [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
