> **Skill level:** 300 · **Read first:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 15-PERSPECTIVE-ADVANCED-COMPLETE

# Ignition Perspective: Complete Advanced Features Reference

**Version**: Ignition 8.3  
**Last Updated**: 2026-07-13  
**Scope**: Advanced topics for production Perspective applications

---

## Table of Contents

1. [Session Management](#session-management)
2. [View Parameters & Communication](#view-parameters--communication)
3. [Message Handling](#message-handling)
4. [CSS Theming & Styling](#css-theming--styling)
5. [Resource Files & Assets](#resource-files--assets)
6. [View Navigation](#view-navigation)
7. [Perspective API (system.perspective.*)](#perspective-api)
8. [Mobile Considerations](#mobile-considerations)
9. [Performance & Optimization](#performance--optimization)
10. [Advanced Bindings](#advanced-bindings)

---

## Session Management

### Overview

Sessions represent individual user connections to a Perspective application. Each session maintains its own state, properties, and lifecycle. Sessions remain open until they time out, close programmatically, or the browser tab closes (then timeout occurs).

### Session Lifecycle

#### Startup Event

Executes when a session initializes, providing centralized access to the complete session object.

**Scope**: Gateway scope (runs on server)

**Available Properties**:
```python
session.props.id           # Unique session identifier
session.props.userName     # Authenticated user name
session.props.clientIp     # Client IP address
session.custom             # Custom session properties
```

**Example - Database Session Tracking**:
```python
# Gateway Startup Event Script
queryParams = {
    'sessionID': session.props.id,
    'userName': session.props.userName,
    'clientIP': session.props.clientIp
}
system.db.runNamedQuery('MyProject', 'InsertSessionStart', queryParams)
```

**SQL Insert Query**:
```sql
INSERT INTO session_tracking (session_id, user_name, client_ip, start_time)
VALUES (:sessionID, :userName, :clientIP, CURRENT_TIMESTAMP)
```

#### Shutdown Event

Executes when sessions terminate through:
- Session timeout (configured in Project Properties)
- User authorization loss
- Gateway redundancy failover
- Licensing restrictions
- Project deletion or becoming unrunnable

**Critical Note**: Closing a browser tab does NOT immediately close the session. Session remains open until timeout occurs.

**Example - Session Termination Logging**:
```python
# Gateway Shutdown Event Script
queryParams = {'sessionID': session.props.id}
system.db.runNamedQuery('MyProject', 'UpdateSessionEnd', queryParams)

# Optional: Send notification
notificationParams = {
    'sessionID': session.props.id,
    'reason': 'Session timeout',
    'duration': system.date.getElapsed(session.props.startTime)
}
system.db.runNamedQuery('MyProject', 'LogSessionTermination', notificationParams)
```

### Session Properties

Session properties are session-scoped variables accessible across all views and pages within a session. Critical for:
- Passing authenticated user data between views
- Maintaining application state
- Avoiding cross-session data pollution (tag values are shared across sessions)

**Property Categories**:

| Category | Description |
|----------|-------------|
| **Props** | Built-in session properties (id, userName, clientIp) |
| **Custom** | User-defined properties for application state |
| **Params** | Session-level parameters |

**Example - Custom Session Properties**:
```python
# In Startup Event - Initialize custom properties
session.custom.userRole = session.props.userName  # Assign role
session.custom.selectedEquipment = None
session.custom.filterCriteria = {}
session.custom.lastActivity = system.date.now()
```

**Accessing in Views**:
```python
# In any view's script
userRole = self.session.custom.userRole
selectedEquipment = self.session.custom.selectedEquipment

# Update in message handler or event script
self.session.custom.selectedEquipment = equipmentID
self.session.custom.lastActivity = system.date.now()
```

### Session Persistence

Sessions must be logged to persistent storage for audit trails and system management.

**Best Practice Structure**:
```sql
CREATE TABLE sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255),
    client_ip VARCHAR(45),
    start_time TIMESTAMP,
    end_time TIMESTAMP NULL,
    duration_seconds INT,
    session_status VARCHAR(50)
);
```

**Session Event Handler Pattern**:
```python
# Startup
try:
    system.db.runNamedQuery('MyProject', 'InsertSessionStart', 
                          {'sessionID': session.props.id})
except:
    system.util.getLogger('SessionManagement').error('Failed to log session start')

# Shutdown  
try:
    duration = system.date.getElapsed(session.props.startTime)
    system.db.runNamedQuery('MyProject', 'UpdateSessionEnd',
                          {'sessionID': session.props.id, 'duration': duration})
except:
    system.util.getLogger('SessionManagement').error('Failed to log session end')
```

### Session Timeout Configuration

Configured in **Project Properties > Session > Session Duration**. Default is typically 30 minutes.

**Production Recommendations**:
- Administrator dashboards: 4-8 hours (reduced logout frequency)
- Production operator stations: 2-4 hours (security balance)
- Mobile applications: 30 minutes - 1 hour (device security)

---

## View Parameters & Communication

### View Parameter Types

Views exchange data through parameterized properties. Parameters control bidirectional or unidirectional data flow.

#### Input Parameters

Receive data from external sources (parent views, pages). NOT bindable within view configuration but appear as bindable properties when embedded.

**Use Case**: Passing context (equipment ID, date range) into reusable view

**Example Definition**:
```
Parameter Name: equipmentID
Type: int
Default Value: 0
```

**Accessing in View**:
```python
# In script or binding
equipmentID = self.params.equipmentID
```

#### Output Parameters

Bindable only within view's internal configuration. Appear read-only from outside (embedding view).

**Use Case**: Returning selected values or computed results to parent

**Example Definition**:
```
Parameter Name: selectedValue
Type: string
Default Value: ""
```

**Setting in View**:
```python
# In message handler or event
self.params.selectedValue = "SelectedOption1"
```

#### In/Out Parameters (Bidirectional)

Bidirectionally bindable—acts as "decorator around an input" where data mirrors across view boundaries.

**Use Case**: Editable form data that updates both child and parent

**Example Definition**:
```
Parameter Name: formData
Type: object
Default Value: {}
```

### Custom View Properties

Internal variables accessible to all child components. Different from params—not exposed to embeddings.

**Pattern**:
```python
# Define in view's Custom properties section
view.custom.selectedRow = None
view.custom.filterText = ""
view.custom.isLoading = False
```

**Access**:
```python
# In child components
selectedRow = self.parent.custom.selectedRow

# In sibling components
self.parent.custom.selectedRow = newValue
```

### Embedded View Data Flow

**Container Pattern - Passing Data to Embedded View**:
```
Coordinate Container (Parent)
├── Text Field (source)
└── Embedded View (EmbeddedViewComponent)
    └── Label (displays param)
```

**Binding the Embedded View Parameter**:
1. Select Embedded View component
2. In Properties > params > myParam
3. Bind to `{../../TextField.props.text}` (relative path)

**Best Practice - Using Message Handlers**:
```python
# Parent view - Button onClick
system.perspective.sendMessage('child-update', 
    {'newValue': self.getSibling('TextField').props.text},
    scope='view')

# Embedded view - Message Handler
# Listen for 'child-update' message
self.params.displayValue = payload['newValue']
```

---

## Message Handling

### Message Handler Architecture

Message handlers are user-created scripting events enabling decoupled communication between components. Preferred approach for passing parameters between views/components, avoiding brittle object traversal.

### Message Types

String identifiers for handlers (case-sensitive):
- `foo`, `Foo`, `FOO` are distinct
- Use descriptive naming: `reset-form`, `equipment-selected`, `data-updated`
- Recommended: kebab-case or snake_case

### Message Scopes

Define communication range and receiver visibility.

| Scope | Range | Use Case |
|-------|-------|----------|
| **View** | Components in originating view only | Local component communication |
| **Page** | All views on same page (including docked, popups) | Page-level coordination |
| **Session** | All workspace tabs/pages | Global application events |

### Creating Message Handlers

**Step-by-step**:

1. Select receiving component
2. Right-click → **Configure Scripts**
3. Double-click **Add handler...**
4. Set **Message Type** (e.g., `equipment-selected`)
5. Configure **Listen Scopes** (View/Page/Session)
6. Write handler script (automatic `payload` variable)
7. Click **OK**

### Sending Messages

**Basic Send**:
```python
system.perspective.sendMessage('equipment-selected')
```

**Send with Payload** (Button onClick):
```python
# Prepare data
equipmentID = self.getSibling('EquipmentDropdown').props.value
timestamp = system.date.format(system.date.now(), 'HH:mm:ss')

# Send message with payload
payload = {
    'equipmentID': equipmentID,
    'selectedTime': timestamp,
    'userID': self.session.props.userName
}
system.perspective.sendMessage('equipment-selected', payload, scope='page')
```

**Receiving Handler** (Label or other component):
```python
# Message Handler: 'equipment-selected'
# payload variable available automatically
self.props.text = 'Selected: %s at %s' % (
    payload['equipmentID'], 
    payload['selectedTime']
)

# Update session state
self.session.custom.selectedEquipment = payload['equipmentID']
```

### Asynchronous Behavior

**Critical**: Message handlers execute asynchronously (separate thread).

```python
# Sender script
system.perspective.sendMessage('update-data')
system.perspective.print('This likely prints BEFORE handler completes')

# Handler executes in parallel, not sequentially
```

**Implications**:
- Don't depend on handler completion for subsequent operations
- Use structured data in payloads; avoid complex coordination
- For sequential operations, implement completion callbacks via return messages

### Advanced Pattern - Handler-to-Handler Communication

Create bi-directional communication between components:

```python
# Component A - Initiates request
payload = {'requestID': 'req_001', 'action': 'fetch-data'}
system.perspective.sendMessage('process-request', payload, scope='page')

# Component B - Message Handler 'process-request'
# Process and send response back
response = {
    'requestID': payload['requestID'],
    'status': 'complete',
    'result': {'data': [...]}
}
system.perspective.sendMessage('process-response', response, scope='page')

# Component A - Message Handler 'process-response'
if payload['requestID'] == 'req_001':
    self.props.text = "Data: " + str(payload['result'])
```

### Best Practices

1. **Use message handlers instead of object traversal**
   - ❌ Bad: `self.getSibling('parent').getSibling('TextField').props.value`
   - ✅ Good: Send message to Text Field's handler

2. **Descriptive message types and payloads**
   ```python
   # ✅ Clear intent
   payload = {
       'action': 'filter-applied',
       'criteria': {'equipment': 'Pump-01', 'status': 'Active'},
       'timestamp': system.date.now()
   }
   ```

3. **Scope appropriately**
   - Use `view` for local component interaction
   - Use `page` for multi-view coordination
   - Use `session` sparingly (performance impact)

4. **Avoid storing in tags**
   - ❌ `system.tag.write('[default]selectedEquipment', value)` # Affects ALL sessions
   - ✅ `self.session.custom.selectedEquipment = value` # Session-specific

5. **Error handling in handlers**
   ```python
   # Message Handler with error handling
   try:
       value = payload['expectedKey']
       self.props.text = str(value)
   except KeyError:
       system.util.getLogger('MessageHandler').warning('Missing payload key')
       self.props.text = 'Error: Invalid message format'
   ```

---

## CSS Theming & Styling

### Theme Architecture

Custom themes enable centralized styling. Theme consists of:

```
custom-theme/
├── index.css              # Main entry point
├── config.json            # Theme metadata
├── resource.json          # Resource declarations
└── variables.css          # Optional: CSS variables
```

### Theme Configuration

**config.json Structure**:
```json
{
  "entrypoint": "index.css",
  "isPrivate": false
}
```

**entrypoint**: Configurable CSS file (default: index.css)  
**isPrivate**: When true, theme hidden from theme selector

### CSS Variables Pattern

Centralize color and sizing decisions using CSS custom properties.

**variables.css**:
```css
:root {
  /* Brand Colors */
  --primary-color: #2196F3;
  --secondary-color: #FF9800;
  --accent-color: #4CAF50;
  
  /* Semantic Colors */
  --error-color: #F44336;
  --warning-color: #FFC107;
  --success-color: #4CAF50;
  --info-color: #2196F3;
  
  /* Neutral Palette */
  --background-light: #F5F5F5;
  --background-dark: #424242;
  --text-primary: #212121;
  --text-secondary: #757575;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-family-base: 'Roboto', sans-serif;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
}
```

**Using Variables**:
```css
.button {
  background-color: var(--primary-color);
  color: white;
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
  border-radius: 4px;
}

.button:hover {
  background-color: var(--secondary-color);
}

.error-message {
  color: var(--error-color);
  font-weight: bold;
}
```

### ABEM Naming Convention

Atomic Block Element Modifier (ABEM) syntax for component selectors:

```
atomicPrefix_blockName__elementName--modifierName
```

**Examples**:
```css
/* Cylindrical Tank Component */
ia_cylindricalTankComponent__liquid--animation
ia_cylindricalTankComponent__outline
ia_cylindricalTankComponent__label

/* Gauge Component */
ia_gaugeComponent__needle
ia_gaugeComponent__scale
ia_gaugeComponent__value--warning
```

**Benefits**:
- Prevents CSS class name conflicts
- Provides direct access to component internals
- Enables component-specific overrides

### Light/Dark Theme Support

**config.json for Theme Variants**:
```json
{
  "entrypoint": "index.css",
  "isPrivate": false,
  "variants": ["light", "dark"]
}
```

**CSS Media Query Approach**:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --background-light: #1E1E1E;
    --text-primary: #FFFFFF;
  }
}

@media (prefers-color-scheme: light) {
  :root {
    --background-light: #F5F5F5;
    --text-primary: #212121;
  }
}
```

### Custom Font Implementation

**Step-by-step**:

1. Create fonts directory:
   ```
   %IgnitionInstallationDirectory%\data\config\resources\core\com.inductiveautomation.perspective\fonts
   ```

2. Add `.ttf` or `.woff` font files

3. Create `fonts.css`:
   ```css
   @font-face {
     font-family: 'CustomFont';
     src: url('./CustomFont-Regular.ttf') format('truetype');
     font-weight: normal;
     font-style: normal;
   }

   @font-face {
     font-family: 'CustomFont';
     src: url('./CustomFont-Bold.ttf') format('truetype');
     font-weight: bold;
     font-style: normal;
   }
   ```

4. Create `config.json`:
   ```json
   {}
   ```

5. Create `resource.json`:
   ```json
   {
     "files": [
       "CustomFont-Regular.ttf",
       "CustomFont-Bold.ttf",
       "fonts.css"
     ]
   }
   ```

6. Restart Gateway or rescan file system

7. Reference in theme:
   ```css
   @import "fonts.css";
   
   body {
     font-family: 'CustomFont', sans-serif;
   }
   ```

### Inline Styling (Not Recommended)

While possible via component inline styles, centralized CSS is preferred:

```python
# ❌ Avoid - Difficult to maintain
component.props.style.backgroundColor = '#FF0000'
component.props.style.padding = '10px'

# ✅ Preferred - Use CSS classes
component.props.className = 'highlight-box'
```

### Theme Overrides Pattern

Add custom CSS after theme imports:

```css
@import "./light/index.css"           /* Base theme */
@import "./custom/overrides.css"      /* Your customizations */

/* Custom overrides execute last */
.ia_button {
  border-radius: 8px;  /* Override default border radius */
}

.ia_cylindricalTankComponent__liquid {
  animation: pulse 2s infinite;  /* Custom animation */
}
```

### Creating Themes via API

**POST to Gateway**:
```bash
curl -X POST http://localhost:8088/data/api/v1/resources/com.inductiveautomation.perspective/themes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-dark",
    "collection": "core",
    "enabled": true,
    "description": "Custom dark theme for production",
    "config": {
      "entrypoint": "index.css"
    }
  }'
```

**Update theme CSS**:
```bash
curl -X PUT http://localhost:8088/data/api/v1/resources/datafile/com.inductiveautomation.perspective/themes/custom-dark/index.css \
  -H "Content-Type: text/css" \
  --data-binary @custom-dark.css
```

### Best Practices

1. **Base on existing themes**
   - Derivative themes (light-cool, dark-warm) vs. light base
   - Ensures all component styling inherits properly

2. **CSS cascade order**
   - Base theme → Imports → Overrides → Inline
   - Later rules override earlier ones

3. **Variable centralization**
   - All colors and sizes in `variables.css`
   - Single source of truth for branding

4. **Production deployments**
   - Test theme on multiple browsers
   - Verify light/dark mode switching
   - Cache-bust CSS after updates (timestamp or hash)

5. **Avoid component element manipulation**
   - Don't hardcode ABEM selectors in components
   - Use theme-based styling exclusively

---

## Resource Files & Assets

### Image Management

Perspective supports: PNG, JPG, JPEG, GIF, and SVG formats.

#### Import Methods

**1. Image Management Tool**:
- Gateway: **System > Tools > Image Management**
- Organize into folders for reuse
- Reference with `/system/images/` prefix
- Right-click → "Copy Path" for reference

**Path Format**:
```
/system/images/logo.png
/system/images/equipment/pump-01.svg
/system/images/icons/alert-red.png
```

**2. Drag & Drop into View**:
- **Save and link**: Stores in Image Management (recommended)
- **Embed image**: Directly embeds into view (degrades performance if >100KB)

**3. External Web URLs**:
```python
# Directly in Image component
self.props.source = "https://example.com/images/logo.png"
```

### Icon System

#### Built-in Icon Libraries

| Library | Source | Path Format |
|---------|--------|-------------|
| **Material** | Google Material Design | `material/location_on`, `material/settings` |
| **Ignition** | Inductive Automation | `ignition/logo` |
| **Sample** | Example components | `sample-component/...` |

#### Custom Icon Repository

**Directory Structure** (Windows):
```
C:\Program Files\Inductive Automation\Ignition\data\config\resources\core\
com.inductiveautomation.perspective\icons\
├── custom-icons.svg
├── config.json
└── resource.json
```

**custom-icons.svg**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <!-- Each icon is an SVG symbol -->
  <symbol id="pump-active" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="#4CAF50"/>
    <path d="..." fill="white"/>
  </symbol>
  
  <symbol id="pump-inactive" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" fill="#BDBDBD"/>
    <path d="..." fill="white"/>
  </symbol>
</svg>
```

**config.json**:
```json
{
  "entrypoint": "custom-icons.svg"
}
```

**resource.json**:
```json
{
  "files": ["custom-icons.svg", "config.json"]
}
```

**Usage**:
```python
# In Icon component source property
"custom-icons/pump-active"
"custom-icons/pump-inactive"
```

**Restart Designer** or **Platform > Overview > Scan File System** to recognize new icons.

### Stylesheet Resources

CSS files managed as project resources for modular styling.

**Creating Stylesheet**:
1. Project Browser → **Resources**
2. Right-click → **New Resource** → **Stylesheet**
3. Enter name: `app-styles.css`

**Usage in Theme**:
```css
@import "/resources/app-styles.css";
```

**Stylesheet Content Example**:
```css
/* Component-specific styles */
.data-table {
  background-color: var(--background-light);
  border-collapse: collapse;
}

.data-table td {
  padding: var(--spacing-md);
  border: 1px solid #E0E0E0;
}

/* Override Perspective style classes */
.ia_label {
  font-size: var(--font-size-lg);
  font-weight: 500;
}
```

### SVG Components

Convert SVG-based components to drawings for direct manipulation:

**Convert Process**:
1. Insert SVG-based component (e.g., Cylindrical Tank)
2. Right-click → **Convert to Drawing**
3. Properties change from semantic (capacity, liquidColor) to structural (viewBox, elements)

**Original Properties**:
```python
self.props.capacity = 1000
self.props.liquidValue = 750
self.props.liquidColor = '#2196F3'
```

**After Conversion to Drawing**:
```python
# Direct SVG element manipulation
self.props.elements[0].props.stroke = '#FF0000'
self.props.viewBox = '0 0 100 100'
```

### Asset Caching

Perspective caches assets (CSS, JS, fonts, images) to reduce subsequent load times.

**Cache Invalidation**:
```python
# Add timestamp to URL for cache busting
timestamp = floor(toMillis(now()) * 0.00001)
imageSource = 'http://example.com/image.png?t=' + str(int(timestamp))
```

### Resource Performance

**Guidelines**:
- Images <100KB: Safe to embed
- Images >100KB: Use "Save and link" (Image Management)
- SVG assets: Optimize for file size before import
- Fonts: Use WOFF format for better browser support
- CSS: Modularize via `@import` for maintainability

---

## View Navigation

### Navigation Basics

Navigate between pages, views, and external URLs using `system.perspective.navigate()`.

### navigate() Function Syntax

```python
system.perspective.navigate(
    page=None,           # Page URL path (leading slash optional)
    url=None,            # External URL (requires scheme)
    view=None,           # View to display (doesn't change URL)
    params=None,         # Dictionary of parameters
    sessionId=None,      # Target session (optional)
    pageId=None,         # Target page (required with sessionId)
    newTab=False         # Open in new tab
)
```

### Page Navigation

Navigate to a mounted Perspective page.

**Syntax**:
```python
# Both forms equivalent
system.perspective.navigate('/dashboard')
system.perspective.navigate('dashboard')

# With parameters
system.perspective.navigate('/equipment-detail', params={'equipmentID': 'PUMP-001'})
```

**Browser Behavior**:
- Updates browser address bar
- Adds entry to browser history
- Back button works

### View Navigation

Display specific view without changing page URL.

**Syntax**:
```python
system.perspective.navigate(view='views/EquipmentDetail', 
                           params={'equipmentID': 'PUMP-001'})
```

**Behavior**:
- Does NOT change browser URL
- Back button does NOT navigate back to previous view
- Useful for view-switching within page context

### External URL Navigation

Navigate to external websites or trigger special protocols.

**Web URLs**:
```python
system.perspective.navigate(url='http://docs.inductiveautomation.com')
system.perspective.navigate(url='https://example.com')
```

**Special Protocols**:
```python
# Telephone
system.perspective.navigate(url='tel:+1-800-555-1234')

# Email
system.perspective.navigate(url='mailto:support@example.com?subject=Help%20Request')

# SMS
system.perspective.navigate(url='sms:+1-800-555-1234?body=Message%20text')
```

### Parameter Passing

Pass data to views via params dictionary.

**Example Pattern**:
```python
# Source view - Button onClick
equipmentID = self.getSibling('EquipmentList').props.selectedValue
equipmentName = self.getSibling('EquipmentList').props.selectedLabel

system.perspective.navigate(
    page='/equipment-dashboard',
    params={
        'equipmentID': equipmentID,
        'equipmentName': equipmentName,
        'timestamp': system.date.now()
    }
)
```

**Destination view**:
```python
# Define input parameters
# Parameter: equipmentID (type: string)
# Parameter: equipmentName (type: string)
# Parameter: timestamp (type: date)

# Access in scripts/bindings
currentEquipment = self.params.equipmentID
self.props.text = self.params.equipmentName
```

### Cross-Session Navigation

Navigate to different session (Gateway scope only).

```python
# From gateway script
sessionId = 'session_12345'
pageId = 'page_67890'

system.perspective.navigate(
    page='/admin-panel',
    sessionId=sessionId,
    pageId=pageId
)
```

### New Tab Navigation

Open navigation target in new browser tab.

```python
system.perspective.navigate(
    page='/report-viewer',
    params={'reportID': 'monthly-summary'},
    newTab=True
)
```

### Navigation Scoping

**Session Scope** (from Perspective view):
```python
# Current session, current page
system.perspective.navigate('/new-page')
```

**Gateway Scope** (from server script):
```python
# Must specify target session and page
system.perspective.navigate(
    page='/target-page',
    sessionId='target_session_id',
    pageId='target_page_id'
)
```

### Best Practices

1. **Validate parameters before navigation**
   ```python
   if equipmentID and len(equipmentID) > 0:
       system.perspective.navigate(page='/equipment-detail', 
                                   params={'equipmentID': equipmentID})
   else:
       system.perspective.print('Error: No equipment selected')
   ```

2. **Use pages for structural navigation** (updates URL, back button works)
   - Top-level dashboard → Detailed view
   - Multi-step wizards

3. **Use views for contextual switching** (within same page)
   - Tab-like behavior without URL change
   - Modal-like overlays

4. **Consistent parameter naming**
   ```python
   # ✓ Consistent across app
   params = {
       'equipmentID': value,
       'equipmentName': name,
       'timestamp': time
   }
   ```

5. **Handle navigation completion**
   ```python
   # Messages after navigation completion
   def onNavigationComplete():
       system.perspective.sendMessage('view-loaded', 
                                     scope='page')
   
   # Call in target view's startup
   onNavigationComplete()
   ```

---

## Perspective API

### system.perspective Module

Complete reference of gateway and perspective-scoped functions.

### Navigation Functions

#### navigate()

Navigate to pages, views, or external URLs.

**Signature**:
```python
system.perspective.navigate(
    page=None, url=None, view=None, params=None, 
    sessionId=None, pageId=None, newTab=False
)
```

**Return**: None

**Example**:
```python
system.perspective.navigate(
    page='/dashboard',
    params={'view': 'overview'},
    newTab=False
)
```

---

### Popup Management

#### openPopup()

Display floating popup view over page.

**Signature**:
```python
system.perspective.openPopup(
    id,                    # Unique popup identifier
    view,                  # View path to display
    params=None,           # Dictionary of parameters
    title=None,            # Popup title
    position=None,         # Position dict (x, y)
    showCloseIcon=False,   # Show close button
    draggable=False,       # Allow drag
    resizable=False,       # Allow resize
    modal=False,           # Modal behavior
    overlayDismiss=False,  # Dismiss on overlay click
    sessionId=None,        # Target session (Gateway scope)
    pageId=None,           # Target page (Gateway scope)
    viewportBound=True     # Constrain to viewport
)
```

**Return**: None

**Example**:
```python
system.perspective.openPopup(
    id='equipmentSettings',
    view='popups/EquipmentConfig',
    params={'equipmentID': 'PUMP-001'},
    title='Equipment Settings',
    showCloseIcon=True,
    draggable=True,
    resizable=True,
    modal=True
)
```

#### closePopup()

Close popup by identifier.

**Signature**:
```python
system.perspective.closePopup(
    id,              # Popup identifier to close
    sessionId=None,  # Target session (Gateway scope)
    pageId=None      # Target page (Gateway scope)
)
```

**Return**: None

**Example**:
```python
system.perspective.closePopup('equipmentSettings')
```

#### togglePopup()

Open or close popup based on current state.

**Signature**:
```python
system.perspective.togglePopup(
    id,              # Popup identifier
    view=None,       # View path (required for first open)
    params=None,     # Parameters for view
    sessionId=None,
    pageId=None
)
```

**Return**: None

---

### Message Communication

#### sendMessage()

Send asynchronous message to handler within session.

**Signature**:
```python
system.perspective.sendMessage(
    messageType,     # Message type string
    payload=None,    # Data dictionary
    scope='session', # 'view', 'page', or 'session'
    sessionId=None,  # Target session (Gateway scope)
    pageId=None      # Target page (Gateway scope)
)
```

**Return**: None

**Example**:
```python
payload = {
    'equipmentID': 'PUMP-001',
    'status': 'running',
    'temperature': 65.5
}
system.perspective.sendMessage('equipment-updated', payload, scope='page')
```

---

### Session Management

#### getSessionInfo()

Retrieve metadata about one or more sessions.

**Signature**:
```python
system.perspective.getSessionInfo(
    sessionId=None,  # Specific session (None = all)
    allSessions=False
)
```

**Return**: List of session info dictionaries or single session

**Example**:
```python
# Get all sessions
allSessions = system.perspective.getSessionInfo()
for session in allSessions:
    print("Session %s - User: %s" % (session.id, session.userName))

# Get specific session
sessionInfo = system.perspective.getSessionInfo(sessionId='session_abc123')
print("Last activity: %s" % sessionInfo.lastActivity)
```

#### closeSession()

Terminate a session.

**Signature**:
```python
system.perspective.closeSession(sessionId=None)
```

**Return**: None

**Example**:
```python
# Close current session
system.perspective.closeSession()

# Close specific session (Gateway scope)
system.perspective.closeSession(sessionId='session_abc123')
```

---

### Authentication

#### authenticationChallenge()

Trigger authentication challenge (e.g., MFA).

**Signature**:
```python
system.perspective.authenticationChallenge()
```

**Return**: AuthenticationChallengeResult

**Result Methods**:
```python
result.isSuccess()           # Boolean
result.getAsSuccess()        # Returns WebAuthSuccessContext
result.isError()             # Boolean
result.getAsError()          # Returns WebAuthErrorContext

# On success
context = result.getAsSuccess().getContext()
user = context.user          # WebAuthUser object
user.id                      # Unique identifier
user.userName               # Login name
user.firstName              # First name
user.lastName               # Last name
user.email                  # Email address
user.roles                  # Array of role strings
context.securityZones       # Array of zone strings
```

**Example**:
```python
result = system.perspective.authenticationChallenge()

if result.isSuccess():
    context = result.getAsSuccess().getContext()
    user = context.user
    
    if "supervisor" in user.roles:
        system.perspective.navigate(page='/admin-panel')
    else:
        system.perspective.print('User not authorized')
else:
    error = result.getAsError()
    if error.isGeneric():
        msg = error.getAsGeneric().getMessage()
        system.perspective.print('Auth failed: ' + msg)
    elif error.isTimeout():
        timeout = error.getAsTimeout().getTimeout()
        system.perspective.print('Timeout: %d minutes' % timeout)
```

#### isAuthorized()

Check if current user authorized against security levels.

**Signature**:
```python
system.perspective.isAuthorized(
    securityLevels  # String or list of level names
)
```

**Return**: Boolean

**Example**:
```python
if system.perspective.isAuthorized(['admin', 'supervisor']):
    showAdminPanel()
else:
    system.perspective.print('Access denied')
```

#### logout()

Trigger user logout event.

**Signature**:
```python
system.perspective.logout()
```

**Return**: None

---

### UI Control

#### print()

Print message to browser console (Perspective) or gateway logs (Gateway).

**Signature**:
```python
system.perspective.print(message)
```

**Return**: None

**Example**:
```python
system.perspective.print('Debug: Equipment ID = PUMP-001')
# Appears in browser DevTools Console or gateway logs
```

#### refresh()

Refresh current page.

**Signature**:
```python
system.perspective.refresh()
```

**Return**: None

**Example**:
```python
# After data sync
system.perspective.refresh()
```

#### setTheme()

Change theme for current page.

**Signature**:
```python
system.perspective.setTheme(theme)
```

**Return**: None

**Example**:
```python
system.perspective.setTheme('dark')
system.perspective.setTheme('light-cool')
```

---

### Dock Management

#### openDocked()

Open docked view on page.

**Signature**:
```python
system.perspective.openDocked(
    view,           # View path
    position,       # 'top', 'bottom', 'left', 'right'
    params=None,    # View parameters
    sessionId=None,
    pageId=None
)
```

**Return**: None

#### closeDocked()

Close docked view.

**Signature**:
```python
system.perspective.closeDocked(
    view,           # View path
    sessionId=None,
    pageId=None
)
```

**Return**: None

#### toggleDocked()

Toggle docked view visibility.

**Signature**:
```python
system.perspective.toggleDocked(
    view,
    position=None,
    sessionId=None,
    pageId=None
)
```

**Return**: None

---

### Mobile Functions

#### vibrateDevice()

Trigger device vibration (mobile app only).

**Signature**:
```python
system.perspective.vibrateDevice(
    duration=200  # Milliseconds
)
```

**Return**: None

**Example**:
```python
# Alert vibration on error
if errorOccurred:
    system.perspective.vibrateDevice(duration=500)
```

---

### Project Information

#### getProjectInfo()

Retrieve project metadata.

**Signature**:
```python
system.perspective.getProjectInfo()
```

**Return**: Dictionary with project metadata

**Example**:
```python
info = system.perspective.getProjectInfo()
print("Project: %s" % info.projectName)
print("Version: %s" % info.projectVersion)
```

#### getSessionInfo()

See [Session Management](#getSessionInfo)

---

## Mobile Considerations

### Responsive Design Principles

Perspective is mobile-responsive, adapting automatically to screen size and orientation changes.

### Layout Strategies

#### Flex Container (Recommended)

Flexible layout adapting to available space.

**Properties**:
```python
self.props.flow = 'row'           # 'row' or 'column'
self.props.justifyContent = 'center'  # flex alignment
self.props.alignItems = 'stretch'
self.props.gap = 10               # spacing between children
```

**Responsive Approach**:
```python
# Binding expression for flow direction
if self.width < 768:
    'column'  # Stack vertically on small screens
else:
    'row'     # Arrange horizontally on large screens
```

#### Coordinate Container (Specific Positioning)

Fixed positioning for precise control (less mobile-friendly).

**Usage**: Desktop dashboards, engineering visualizations

#### Repeater Container

Display arrays of components with responsive row sizing.

```python
self.props.elementWidth = 200
self.props.elementHeight = 150
self.props.wrap = True            # Wrap items
```

### Mobile Input Handling

#### Touch Events

Components respond to touch events on mobile devices.

**Configuration**:
- Long-press support (like right-click)
- Swipe gestures (configurable)
- Multi-touch (pinch-zoom on maps)

#### Keyboard Considerations

Mobile devices show soft keyboard for text inputs.

**Best Practice**:
```python
# Use appropriate input types
self.props.type = 'email'   # Shows email keyboard
self.props.type = 'number'  # Shows numeric keyboard
self.props.type = 'tel'     # Shows phone keyboard
self.props.type = 'text'    # Shows text keyboard
```

### Breakpoint Strategy

Design for common device widths:

| Breakpoint | Width | Device Type |
|-----------|-------|-------------|
| **Mobile** | <576px | Phones, small tablets |
| **Tablet** | 576px-992px | Tablets, large phones |
| **Desktop** | >992px | Monitors, laptops |

**Expression Binding Approach**:
```python
# In component style or visibility
self.width < 576 ? 'mobile' : (self.width < 992 ? 'tablet' : 'desktop')

# Adapt layout
if self.width < 576:
    # Hide secondary panels
    visible = False
else:
    visible = True
```

### Mobile Performance

#### Lazy Loading

Load views on-demand rather than all at initialization.

```python
# Load chart only when tab selected
if tabSelected == 'analytics':
    system.perspective.navigate(view='views/AnalyticsChart')
```

#### Virtual Scrolling

For large lists, only render visible items:

**Table Component**:
```python
# Properties for efficient rendering
self.props.enableVirtualScrolling = True
self.props.virtualHeight = 400
```

### Mobile Optimization Patterns

#### Simplified Navigation

Reduce menu depth on mobile.

```python
# Mobile: Hamburger menu with drawer
# Desktop: Sidebar with all options visible

if self.width < 768:
    showHamburger = True
else:
    showSidebar = True
```

#### Larger Touch Targets

Mobile users need larger buttons (minimum 44x44px).

```python
# Mobile-optimized button
self.props.height = self.width < 768 ? 44 : 36
self.props.width = '100%'          # Full width on mobile
```

#### Minimal Scrolling

Prevent excessive horizontal/vertical scrolling.

```python
# Stack vertically on mobile
self.props.flow = self.width < 768 ? 'column' : 'row'
self.props.wrap = True
```

### Mobile App Considerations

When using Perspective Mobile App:

1. **Offline Support**: Sessions continue in background
2. **Barcode Scanning**: Integrated scanner support
3. **NFC Tags**: Near-Field Communication reading
4. **Accelerometer**: Motion/orientation data available
5. **Notifications**: Push notifications supported

---

## Performance & Optimization

### Loading Optimization

#### View Load Caching

Perspective caches view structures after first load.

**Impact**: Subsequent loads significantly faster

**Cache Invalidation**: 
- Manual refresh: `system.perspective.refresh()`
- Timestamp approach for dynamic content

#### Async Resource Loading

Load dependencies asynchronously.

```python
# In async property binding
if isReady:
    loadData()  # Only after prerequisites loaded
else:
    null        # Deferred loading
```

### Binding Performance

#### Expression Binding Optimization

Complex expressions impact refresh performance.

**Anti-patterns**:
```python
# ❌ Complex nested conditionals (slow)
if a and b and c and d and e then f else (if x then y else z)

# ✓ Simpler expressions (faster)
a && b ? f : y
```

**Optimization Strategy**:
```python
# Break complex logic into components
self.custom.isReady = a && b && c        # Computed property
self.custom.resultValue = isReady ? f : y

# Use computed value in bindings
display = self.custom.resultValue
```

#### Binding Count Limits

Minimize binding count per component.

**Guideline**: <10 active bindings per component

```python
# ❌ Avoid excessive bindings
component.props.text = binding1
component.props.color = binding2
component.props.visible = binding3
component.props.enabled = binding4
# ... more bindings

# ✓ Consolidate where possible
component.props.style = {
    'color': colorBinding,
    'opacity': opacityBinding
}
```

### Memory Management

#### Component Cleanup

Ensure proper cleanup when components destroyed.

```python
# In Shutdown event
# Clean up large objects
self.custom.largeDataset = None
self.custom.cache.clear()
```

#### Query Performance

Limit query result sets.

```python
# ❌ Avoid selecting all data
SELECT * FROM large_table

# ✓ Limit and paginate
SELECT * FROM large_table 
ORDER BY date DESC
LIMIT 100
OFFSET (pageNumber * 100)
```

### Network Optimization

#### Consolidate Queries

Batch database operations.

```python
# ❌ Multiple round trips
temp1 = system.db.runQuery(query1)
temp2 = system.db.runQuery(query2)
temp3 = system.db.runQuery(query3)

# ✓ Single query with JOIN
result = system.db.runQuery(combinedQuery)
```

#### Tag Scan Rate

Control tag polling frequency.

**Binding Scan Rate**: Set in tag properties
- High frequency tags: 100ms
- Normal tags: 1s
- Slow tags: 5s+

### Component Optimization

#### Conditional Rendering

Hide vs. disable components based on visibility.

```python
# ❌ Rendered but hidden (still consuming resources)
self.props.visible = False

# ✓ Not rendered at all (preferred)
# Use container condition for rendering child components
```

#### Large Lists

Use virtual scrolling or pagination.

```python
# Table with virtual scrolling
self.props.enableVirtualScrolling = True
self.props.virtualHeight = 500

# Or pagination
totalPages = ceil(totalRows / pageSize)
currentPage = 1
```

### CSS/Styling Performance

#### Minimize CSS Specificity

Reduce selector complexity.

```css
/* ❌ High specificity (slow) */
div.container > div.row > div.cell > span.label { ... }

/* ✓ Low specificity (fast) */
.cell-label { ... }
```

#### Avoid Animation on Large Datasets

Animations consume resources.

```python
# ❌ Animate list of 1000 items
container.props.animation = 'slide'
for item in largeList:
    addComponent(item)

# ✓ Animate only visible items
for item in visibleItems:  # Maybe 20 items
    addComponent(item)
    applyAnimation(item)
```

### Monitoring Performance

#### Browser DevTools

Inspect performance in modern browsers:
- Performance tab: Measure load time
- Network tab: Monitor asset loading
- Console tab: Check for errors/warnings

#### Gateway Logs

Monitor server-side performance:

```python
import time
start = time.time()

# Operation to measure
system.db.runQuery(largeQuery)

elapsed = time.time() - start
system.util.getLogger('Performance').info('Query took %.2fs' % elapsed)
```

### Production Best Practices

1. **Profile before optimization**
   - Use browser DevTools to identify bottlenecks
   - Don't optimize prematurely

2. **Cache frequently accessed data**
   ```python
   # Cache in session
   if not hasattr(self.session.custom, 'equipmentCache'):
       self.session.custom.equipmentCache = loadEquipmentData()
   ```

3. **Limit real-time updates**
   - Use appropriate tag scan rates
   - Debounce frequent value changes

4. **Test on target devices**
   - Mobile devices may be slower
   - Test on slow network connections

5. **Monitor production**
   - Set up alerts for performance degradation
   - Track session count impact

---

## Advanced Bindings

### Binding Types Overview

Perspective supports multiple binding approaches for dynamic property updates.

| Binding Type | Purpose | Bidirectional |
|--------------|---------|---------------|
| **Tag** | Bind to OPC/system tags | Yes (with checkbox) |
| **Property** | Link component properties | Yes |
| **Expression** | Use formulas | No |
| **Query** | Database result | No |
| **Tag History** | Historical tag data | No |
| **HTTP** | Web service data | No |
| **MongoDB** | NoSQL database | No |

### Tag Bindings

Connect component properties to PLC tags.

**Basic Syntax**:
```
[default]Temperature
[default]Area Name/Tag Name
```

**Bidirectional Configuration**:
1. Select component property
2. Create binding to tag
3. Check "Bidirectional" checkbox
4. Optionally enable "Coalesce"

**Example**:
```python
# Two-way binding on input component
# binding: [default]SetpointValue

# When user modifies input, tag updates
# When tag updates from PLC, input reflects change
```

**Coalesce Option**:
```python
# With Coalesce ON: Batches nested property writes
# Example: user updates object properties
self.props.settings.temperature = 65
self.props.settings.pressure = 100

# Single tag writeback instead of two separate writes
```

### Property Bindings

Link properties between components.

**Binding Syntax**:
```
{../Label.props.text}          # Sibling component
{../../Container.props.visible} # Up one level
{#view.custom.selectedValue}    # View custom property
{#session.custom.userName}      # Session property
```

**Navigation Paths**:
- `..` - Parent container
- `../` - Sibling component
- `#view` - Current view
- `#session` - Current session
- `#page` - Current page

**Example**:
```python
# Bind dropdown to table selection
# Target: Dropdown.props.value
# Binding: {../Table.props.selectedRow.equipmentID}

# When table row selected, dropdown updates
```

### Expression Bindings

Use formulas to calculate property values.

**Syntax**:
```python
# Simple arithmetic
{sum([default]Sensor1, [default]Sensor2) / 2}

# Conditional logic
{if([default]Status == 1, 'Running', 'Stopped')}

# String formatting
{'Temperature: ' + str([default]Temp) + ' °C'}

# Date operations
{dateAdd(now(), 'day', 7)}

# Complex expressions
{if(
    [default]Pressure > 100,
    'High',
    if([default]Pressure > 50, 'Normal', 'Low')
)}
```

**Available Functions**:
- Math: `sum()`, `abs()`, `min()`, `max()`, `pow()`
- Logic: `if()`, `and()`, `or()`, `not()`
- String: `str()`, `concat()`, `len()`, `substring()`
- Date: `now()`, `dateAdd()`, `dateSubtract()`, `daysBetween()`
- Array: `getLength()`, `elementAt()`, `contains()`
- System: `runScript()`, `getSystemTag()`

**Performance Considerations**:
```python
# ✓ Simple expressions (fast)
{[default]Value * 1.8 + 32}  # Fahrenheit conversion

# ⚠ Complex expressions (slower)
{if(complex_condition, then_complex_calc, else_complex_calc)}
```

### Expression Structure Bindings

Create data structures with expressions.

**Example**:
```
# Bind to array or object with individual expressions
devices = [
  {
    id: expression_for_id,
    name: expression_for_name,
    status: expression_for_status
  }
]
```

**Configuration**:
1. Set binding mode to Expression Structure
2. Define structure shape (array/object)
3. Assign expression to each property

**Use Case**:
```python
# Build dataset from multiple sources
# id: expression -> {#view.custom.selectedID}
# name: expression -> {[default]EquipmentName}
# value: expression -> {[default]Sensor1}
# timestamp: expression -> {now()}

# Result: Array of objects with mixed data sources
```

### Tag History Bindings

Access historical tag data for trending.

**Configuration**:
1. Select component (usually Chart, Table)
2. Create Tag History binding
3. Specify tag path, date range, aggregation

**Example** (Chart):
```
Tag: [default]Temperature
Start Date: {dateAdd(now(), 'day', -7)}
End Date: {now()}
Aggregation: Average
Polling Interval: 1 minute
```

**Result**: Chart displays 7-day average temperature history

### Query Bindings

Execute database queries to populate properties.

**Configuration**:
1. Select Named Query or SQL Query
2. Map parameters to properties/values
3. Set polling interval (optional)

**Example**:
```python
# Named Query: GetEquipmentDetails
# Parameter: equipmentID = {../EquipmentDropdown.props.value}
# Returns: Dataset with equipment info

# Bind component property to query result
Table.props.data = queryResult
```

**Refresh Pattern**:
```python
# Manual refresh when dependency changes
def onEquipmentSelected():
    system.perspective.sendMessage('refresh-equipment-data')

# Message handler in component
system.db.runNamedQuery('MyProject', 'GetEquipmentDetails', params)
```

### Computed Properties Pattern

Simulate computed properties using view custom properties.

**Pattern**:
```python
# View custom properties
view.custom.temp_celsius = None      # Source
view.custom.temp_fahrenheit = None   # Computed

# In view startup or binding
# Bind temp_celsius to tag: {[default]Temperature}
# Bind temp_fahrenheit to expression: 
#   {#view.custom.temp_celsius * 1.8 + 32}

# Now temp_fahrenheit automatically updates when celsius changes
```

### Watched Properties Pattern

Respond to property changes without message handlers.

**Pattern**:
```python
# In view startup
def setupWatchers():
    # Monitor property changes
    self.custom.watchedValue = None
    
    # Use expression binding to detect change
    # Bind component visible to: {#view.custom.watchedValue != null}

# When property changes, visibility updates automatically
```

### Bidirectional Binding Example

Two-way synchronization between components.

**Setup**:
```
Component A (Input Field)
├── Property: value
└── Binding: {../ComponentB.props.value}
    └── Bidirectional: ON

Component B (Slider)
├── Property: value
└── Binding: {../ComponentA.props.value}
    └── Bidirectional: ON
```

**Behavior**:
- User changes input → Slider updates
- User moves slider → Input updates
- Both components in sync

### Transform Bindings

Modify binding values before property assignment.

**Expression Transform**:
```python
# Input: {[default]Pressure}
# Transform: int(value) * 1.5
# Output: Doubled pressure value

# Use case: Unit conversion, rounding, formatting
```

**Script Transform**:
```python
# More complex transformations
def transformData(value):
    if value > 100:
        return value * 0.9  # Scale down high values
    else:
        return value

# Apply to binding output
```

### Binding Best Practices

1. **Use structured bindings for maintainability**
   ```python
   # ✓ Clear, reusable
   def getEquipmentStatus():
       return [default]Status == 1 ? 'Running' : 'Stopped'
   
   # Bind to: {getEquipmentStatus()}
   ```

2. **Minimize binding complexity**
   ```python
   # ❌ Avoid deeply nested conditionals
   {if(a, if(b, if(c, if(d, e, f), g), h), i)}
   
   # ✓ Use computed properties instead
   view.custom.complexLogic = calculated_value
   # Bind to: {#view.custom.complexLogic}
   ```

3. **Cache frequently accessed values**
   ```python
   # Cache query result in session
   self.session.custom.equipmentCache = queryResult
   
   # Bind to cache instead of re-querying
   {#session.custom.equipmentCache[0].name}
   ```

4. **Test bindings for circular dependencies**
   ```python
   # ❌ Circular binding (A depends on B, B depends on A)
   A binding: {../B.props.value}
   B binding: {../A.props.value}
   
   # ✓ One-way flow
   A binding: {../B.props.value}  # B → A only
   ```

5. **Use appropriate polling rates**
   ```python
   # High-frequency tags: 100-500ms
   # Normal: 1-2s
   # Low-frequency: 5-10s
   # Status checks: 30-60s
   ```

---

## Summary

This comprehensive reference covers all advanced Perspective features for production deployments:

- **Session Management**: Lifecycle, properties, persistence
- **View Parameters**: Input/output parameters, custom properties, data flow
- **Message Handling**: Decoupled component communication patterns
- **CSS Theming**: ABEM naming, CSS variables, dark/light support
- **Resource Management**: Images, icons, fonts, stylesheets
- **Navigation**: Pages, views, parameters, history
- **Perspective API**: Complete system.perspective.* function reference
- **Mobile Optimization**: Responsive design, touch handling, performance
- **Performance**: Binding optimization, memory management, caching
- **Advanced Bindings**: Expression, property, tag, query binding patterns

All sections include production-ready examples and best practices for building scalable, maintainable Perspective applications.

---

## Additional Resources

- [Inductive Automation Official Documentation](https://www.docs.inductiveautomation.com/docs/8.3/)
- [Ignition Perspective GitHub Examples](https://github.com/inductiveautomation)
- [Inductive Automation Community Forum](https://forum.inductiveautomation.com)

---

**Document Version**: 1.0  
**Last Updated**: 2026-07-13  
**Author**: Claude AI Assistant  
**Status**: Complete Reference

---

## See Also

**Prerequisites:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md), [30-SCRIPTING-OVERVIEW](30-SCRIPTING-OVERVIEW.md)

**Builds toward:** [92-MOBILE-MODULE-PERSPECTIVE](92-MOBILE-MODULE-PERSPECTIVE.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

**Related:** [13-TEMPLATES-REUSE](13-TEMPLATES-REUSE.md), [92-MOBILE-MODULE-PERSPECTIVE](92-MOBILE-MODULE-PERSPECTIVE.md), [50-SECURITY-MODEL](50-SECURITY-MODEL.md), [83-PERFORMANCE-TUNING](83-PERFORMANCE-TUNING.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
