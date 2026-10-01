# Ignition 8.3 — component scripting APIs

## How component scripting works

Both Perspective and Vision let you call methods directly on a live component instance from a script — separate from the property-binding/expression system. The two environments get a component *reference* very differently, and calling the wrong idiom in the wrong place is the most common mistake.

**Perspective** (event scripts and message handlers run in the Gateway/session scope, not per-component):
- `self` — inside a component's own event script, refers to that component.
- `self.getSibling("ComponentName")` — from one component's event script, get another component in the same container.
- `self.getChild("ComponentName")` — get a descendant component by name (containers only).
- `self.parent` — the immediate parent container of the current component.
- `event.source` — inside a component event (e.g. `onActionPerformed`), the component that raised the event.
- View/page/session scripting: `self.view`, `self.session`, `self.page` give access to the surrounding view, session, and page objects and their own scripting/properties.
- Perspective methods are called as `<componentRef>.methodName(args)`, e.g. `self.getSibling('Table').expandSubviews([1,3])`.
- Perspective extension functions are configured in the Designer's **Scripting** tab of the component and are *empty by default* — Perspective does not auto-generate a stub the way Vision does; nothing happens until you write code in them.

**Vision** (window/component event scripts run directly on the AWT/Swing component tree):
- `event.source` — inside a component event handler, the component that raised the event.
- `<component>.parent` — the immediate parent container; chain `.parent.parent...` to walk up to the window.
- `event.source.parent.getComponent("Name")` — the classic Vision idiom for reaching a sibling component by name from a container.
- `system.gui.getWindow("Window Name")` and then `.getComponent("Name")` — reach into another open window from anywhere.
- The **Window object** itself exposes scripting methods (see the Window Object section below) — obtained via `system.nav.openWindow(...)`'s return value, `event.source.parent...` chains, or `system.gui.getWindow(...)`.
- Vision **extension functions** (`configureCell`, `onMousePress`, `isCellEditable`, etc.) are pre-declared stub methods visible in the Designer's Scripting tab for each component; they are **no-ops until you implement them** — this is the single most common source of "nothing happens" bug reports on Vision components.
- Common object types passed into Vision scripts/extension functions (Dataset, QualifiedValue, QualityCode, PyAlarmEvent, SProcCall, etc.) are documented on the [Scripting Object Reference](appendix/reference-pages/scripting-object-reference.md) page, not on individual component pages.

Both environments distinguish:
- **Methods** — you call these; they run immediately and (usually) return a value.
- **Extension functions** — the platform calls these at defined lifecycle/interaction points; you implement them to inject custom behavior. They are documented on each component's page with an explicit *(extension function)* label below.

## Perspective component methods

### Breakpoint Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Column Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Coordinate Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Flex Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Split Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Tab Container

#### `.getChildren()`
Returns an ArrayList, which contains references to all components inside of the container.

**Parameters:** none

**Returns:** Array List — An ArrayList of components in the container. The resulting ArrayList can be iterated over via a for…


### Alarm Journal Table

#### `.refreshData()`
Refreshes the data on the Alarm Journal Table.

**Parameters:** none

**Returns:** Nothing

**Extension functions:**

#### `.filterAlarm(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called for each event before it is displayed in the table, allowing you to hide or show each alarm event (row) in the table. Provides an opportunity to write a more complex filter than what's normally provided to the co…

**Parameters:**
- ComponentModelScriptWrapper.SafetyWrapper `self` — A reference to the component that is invoking this function.
- PyAlarmEvent `alarmEvent` — The alarm event itself. Call `alarmEvent.get('propertyName')` to inspect proper…

**Returns:** Boolean — The function must return either a True or False for every alarm event in the table. True will show …


### Alarm Status Table

#### `.refreshData()`
Refreshes the data on the Alarm Status Table.

**Parameters:** none

**Returns:** Nothing

**Extension functions:**

#### `.filterAlarm(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called for each event before it is displayed in the table, allowing you to hide or show each alarm event (row) in the table. Provides an opportunity to write a more complex filter than what's normally provided to the co…

**Parameters:**
- ComponentModelScriptWrapper.SafetyWrapper `self` — A reference to the component that is invoking this function.
- PyAlarmEvent `alarmEvent` — The alarm event itself. Call `alarmEvent.get('propertyName')` to inspect proper…

**Returns:** Boolean — The function must return either a True or False for every alarm event in the table. True will show …

#### `.filterShelvedAlarm(self, shelvedAlarmEvent)` *(extension function — implement to override; no-op by default)*
Called for each event before it is displayed in the shelved tab of the table, allowing you to hide or show each alarm event (row) in the table. Return False to exclude a shelved alarm event from the table.

**Parameters:**
- ComponentModelScriptWrapper.SafetyWrapper `self` — A reference to the component that is invoking this function.
- PyAlarmEvent `shelvedAlarmEvent` — The shelved alarm event. Call `shelvedAlarmEvent.get('propertyName')` to inspec…

**Returns:** Boolean — The function must return either a True or False for every alarm event in the table. True will show …


### Audio

#### `.play()`
Plays the media file, triggering the onPlay component event.

**Parameters:** none

**Returns:** Nothing

#### `.pause()`
Pauses the media file, triggering the onPause component event.

**Parameters:** none

**Returns:** Nothing

#### `.replay()`
Replays the media file from the beginning.

**Parameters:** none

**Returns:** Nothing


### Drawing

_No component-specific methods or extension functions documented beyond component events._


### Equipment Schedule

_No component-specific methods or extension functions documented beyond component events._


### Google Map

#### `fitBounds(latLngBounds, padding)`
Sets the viewport to contain the given bounds. When the map is set to display none, the fitBounds function reads the map's size as 0x0 and does not do anything.

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects. The LatLng objects combined repr…
- Numeric `padding` — Padding in pixels. The value represents the same padding for all four sides of …

**Returns:** None

#### `panBy(x, y)`
Changes the center of the map by the given distance in pixels. If the distance is less than both the width and height of the map, the transition will be smoothly animated. Note that the map coordinate system increases f…

**Parameters:**
- Numeric `x` — Number of pixels to move the map in the x direction.
- Numeric `y` — Number of pixels to move the map in the y direction.

**Returns:** None

#### `panTo(latLng)`
Pans the map to a given center. If the change is less than both the width and height of the map, the transition will be smoothly animated.

**Parameters:**
- Dictionary `latLng` — The geographic point to pan to.

**Returns:** None

#### `panToBounds(latLngBounds, padding)`
Pans the map by the minimum amount necessary to contain the given LatLngBounds so that the map will be panned to show as much of the bounds as possible inside `{currentMapSizeInPx}` - `{padding}`. The map's zoom, tilt, …

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects. The LatLng objects combined repr…
- Numeric `padding` — Padding in pixels. The value represents the same padding for all four sides of …

**Returns:** None

#### `setCenter(latLngBounds)`
Sets the geographical center of the map in latitude and longitude.

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects as `{ lat: number, lng: number }`.

**Returns:** None

#### `setClickableIcons(value)`
Controls whether the map icons are clickable or not. A map icon represents a point of interest (POI).

**Parameters:**
- Boolean `value` — True to enable clickable map icons, false to disable the clickability of map ic…

**Returns:** None

#### `setHeading(heading)`
Sets the compass heading for map measured in degrees from cardinal direction North. This method only applies to aerial imagery.

**Parameters:**
- Numeric `heading` — The numerical value in degrees to set the compass heading for the map.

**Returns:** None

#### `setMapTypeId(mapTypeId)`
Sets the type of map tiles to display (e.g. roadmap, satellite, hybrid, terrain).

**Parameters:**
- String `mapTypeId` — A string identifier that is used to associate a MapType with a unique value.

**Returns:** None

#### `setTilt(tilt)`
Controls the automatic switching behavior for the angle of incidence of the map. The only allowed values are 0 (default overhead view) and 45. A 45 degree tilt angle will automatically switch to 45 whenever 45° imagery …

**Parameters:**
- Numeric `tilt` — The numerical value of the tilt angle.

**Returns:** None

#### `setZoom(zoom)`
Sets the zoom of the map.

**Parameters:**
- Numeric `zoom` — The numerical value to increase the zoom by. Larger zoom values correspond to a…

**Returns:** None


### Map

#### `.getCenter()`
Returns the geographical center of the map in latitude and longitude.

**Parameters:** none

**Returns:** LatLng — Returns the geographical center of the map view as `{"lat": number, "lng": number}`.

#### `.getZoom()`
Returns the current zoom level of the map view as a number.

**Parameters:** none

**Returns:** Returns the current zoom level of the map view as a number.

#### `.getBounds()`
Returns the geographical bounds of the map as a dictionary.

**Parameters:** none

**Returns:** Dictionary — Contains keys `north`, `northEast`, `east`, `southEast`, `south`, `southWest`, `west`, `northWest`.

#### `.getBoundsAsBBoxString()`
Returns a string with bounding box coordinates in a 'South West longitude, South West latitude, North East longitude, North East latitude' format.

**Parameters:** none

**Returns:** Returns the bounding box of the map as a string.

#### `.zoomIn([delta, options])`
Increases the zoom of the map by delta.

**Parameters:**
- Numeric `delta` — The numerical value to increase the zoom by. If omitted, uses the value of prop…
- Dictionary `options` — A dictionary of parameters to use during the zoom, typically containing a singl…

**Returns:** Nothing

#### `.zoomOut([delta, options])`
Decreases the zoom of the map by delta.

**Parameters:**
- Numeric `delta` — The numerical value to increase the zoom by. If omitted, uses the value of prop…
- Dictionary `options` — A dictionary of parameters to use during the zoom, typically containing a singl…

**Returns:** Nothing

#### `.setZoomAround(point, zoom, [options])`
Zooms the map while keeping a specified geographical point on the map stationary (e.g. used internally for scroll zoom and double-click zoom).

**Parameters:**
- Dictionary `point` — The geographic point that the map will zoom around.
- Numeric `zoom` — The numerical value to increase the zoom by. If omitted, uses the value of prop…
- Dictionary `options` — A dictionary of parameters to use during the zoom, typically containing a singl…

**Returns:** Nothing

#### `.fitBounds(latLngBounds, [options])`
Sets a map view that contains the given geographical bounds with the maximum zoom level possible.

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects. The LatLng objects combined repr…
- Dictionary `options` — A dictionary of parameters used to manipulate the FitBound settings.

**Returns:** Nothing

#### `.fitWorld([options])`
Sets a map view that mostly contains the whole world with the maximum zoom level possible.

**Parameters:**
- Dictionary `options` — A dictionary of parameters used to manipulate the FitBound settings.

**Returns:** Nothing

#### `.panTo(latLng, [options])`
Pans the map to a given center.

**Parameters:**
- Dictionary `latLng` — The geographic point to pan to. [required]
- Dictionary `options` — A dictionary of parameters used to modify the panning behavior.

**Returns:** Nothing

#### `.panBy(point, [options])`
Pans the map by a given number of pixels (animated).

**Parameters:**
- Dictionary `point` — The geographic point to pan to. The dictionary should contain an 'x' and 'y' ke…
- Dictionary `options` — A dictionary of parameters used to modify the panning behavior.

**Returns:** Nothing

#### `.flyTo(latLng, [zoom, options])`
Sets the view of the map (geographical center and zoom) performing a smooth pan-zoom animation.

**Parameters:**
- Dictionary `latLng` — A Python dictionary representing the coordinates to fly to. [required]
- Numeric `zoom` — Sets the zoom level to transition to during the flight. If omitted, uses the va…
- Dictionary `options` — A dictionary of panning options to use.

**Returns:** Nothing

#### `.flyToBounds(latLngBounds, [options])`
Sets the view of the map with a smooth animation like flyTo, but takes a bounds parameter like FitBounds.

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects. The LatLng objects combined repr…
- Dictionary `options` — A dictionary of panning options to use.

**Returns:** Nothing

#### `.panInsideBounds(latLngBounds, [options])`
Pans the map to the closest view that would lie inside the given bounds (if it's not already), controlling the animation using the options specific, if any.

**Parameters:**
- Dictionary `latLngBounds` — A dictionary consisting of two LatLng objects. The LatLng objects combined repr…
- Dictionary `options` — A dictionary of panning options to use.

**Returns:** Nothing

#### `.panInside(latLng, [options])`
Pans the map the minimum amount to make the latLng visible.

**Parameters:**
- Dictionary `latLng` — A Python dictionary representing the coordinates to pan to. [required]
- Dictionary `options` — A dictionary of panning options to use.

**Returns:** Nothing

#### `.getSize()`
Returns height and width of the Map component.

**Parameters:** none

**Returns:** JSON Object — Returns a Python dictionary. Contains two items: height and width.


### PDF Viewer

#### `.reload()`
This function will reload the PDF in the PDF Viewer component.

**Parameters:**
- String `name` — The name of the PDF.

**Returns:** Nothing


### Table

#### `.collapseSubviews()`
This function will collapse the specified row subviews. If no parameter is specified, this function will collapse all expanded subviews on the current page.

**Parameters:**
- array `rows` — An optional array of indices of rows to collapse. Any argument that is not a li…

**Returns:** Nothing

#### `.expandSubviews()`
This function will expand the specified row subviews. This will only expand rows that are visible on the current page.

**Parameters:**
- array `rows` — An array of indices of rows to expand. Any argument that is not a list will thr…

**Returns:** Nothing


### Tag Browse Tree

**Extension functions:**

#### `filterBrowseNode(self, node)` *(extension function — implement to override; no-op by default)*
Called for each Tag before it is displayed in the Tag Browse Tree. Provides an opportunity to create a complex filter for the Tags in the Tag Browse Tree. filerBrowseNode is best used alongside the Tag Browse Tree's roo…

**Parameters:**
- ComponentModelScriptWrapper.SafetyWrapper `self` — A reference to the component that is invoking this function.
- NodeBrowseInfo `node` — The Tag returned as type NodeBrowseInfo. See the Ignition JavaDocs for usage.

**Returns:** Boolean — The function must return either a True or False.

```python
# This example will filter out any nodes (both Tags and folders included) that do not match the string Ramp.
if node.name == "Ramp":
    return True
else:
    return False
```


### Tree

_No component-specific methods or extension functions documented beyond component events._


### Accordion

_No component-specific methods or extension functions documented beyond component events._


### View Canvas

_No component-specific methods or extension functions documented beyond component events._


### File Upload

#### `.clearUploads()`
Resets the File Upload component to its default state.

**Parameters:** none

**Returns:** Nothing


### Form

_No component-specific methods or extension functions documented beyond component events._


### Signature Pad

#### `.clearSignature()`
Clears the current signature on the component.

**Parameters:** none

**Returns:** Nothing

#### `.submitSignature()`
Submits the signature, triggering the onSignatureSubmitted component event.

**Parameters:** none

**Returns:** Nothing


### Horizontal Menu

_No component-specific methods or extension functions documented beyond component events._


### Menu Tree

_No component-specific methods or extension functions documented beyond component events._

## Vision component methods and extension functions

### Roster Management

**Extension functions:**

#### `filterRoster(self, roster)` *(extension function — implement to override; no-op by default)*
Called for each roster loaded into the management table. Return false to hide this roster from the management table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- User Object `roster` — The name of the roster.

**Returns:** Boolean

#### `filterAvailableUser(self, roster, userSource, user)` *(extension function — implement to override; no-op by default)*
Called for each user in a user source to be shown as an available user for the roster currently being edited. Return false to hide this user so that it cannot be added to the roster. This code is executed in a backgroun…

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- String `roster` — The name of the roster being edited.
- String `userSource` — The name of the user source being used to populate the list of available users.
- User Object `user` — The user object itself. Call user.get('propertyName') to inspect. Common proper…

**Returns:** Boolean

#### `onSaveRoster(self, saveContext, rosterName)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when editing a roster. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…
- String `rosterName` — The name of the roster being edited.

**Returns:** None

#### `onCreateRoster(self, createContext, rosterName)` *(extension function — implement to override; no-op by default)*
Called when the add button is pressed. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `createContext` — An object that can be used to reject the edit by calling createContext.rejectCr…
- String `rosterName` — The name of the roster being created.

**Returns:** None

#### `onDeleteRoster(self, deleteContext, rosterNames)` *(extension function — implement to override; no-op by default)*
Called when the delete button is pressed. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `deleteContext` — An object that can be used to reject the edit by calling deleteContext.rejectDe…
- String `rosterNames` — A list of the roster names being deleted.

**Returns:** None


### Schedule Management

**Extension functions:**

#### `filterSchedule(self, schedule)` *(extension function — implement to override; no-op by default)*
Called for each schedule loaded into the management table. Return false to hide this schedule from the management table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- String `schedule` — The schedule name

**Returns:** Boolean

#### `filterHoliday(self, holiday)` *(extension function — implement to override; no-op by default)*
Called for each holiday loaded into the management table. Return false to hide this holiday from the management table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- String `holiday` — The holiday name.

**Returns:** Boolean

#### `onCreateSchedule(self, saveContext)` *(extension function — implement to override; no-op by default)*
Called when the add button is pressed when adding a schedule. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the add by calling saveContect.rejectSave(…

**Returns:** None

#### `onDeleteSchedule(self, saveContext, name)` *(extension function — implement to override; no-op by default)*
Called when the delete button is pressed for one or more schedules. This code is executed in a background thread, once for each schedule to be deleted.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the add by calling saveContext.rejectSave(…
- String `name` — The name of the schedule to be deleted.

**Returns:** None

#### `onSaveSchedule(self, saveContext, oldName, newName)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when adding or editing a schedule. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContect.rejectSave…
- String `oldName` — The schedule name before editing. Will be None for a schedule being added.
- String `newName` — The new name of the edited schedule.

**Returns:** None

#### `onCreateHoliday(self, saveContext)` *(extension function — implement to override; no-op by default)*
Called when the add button is pressed when to add a holiday. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…

**Returns:** None

#### `onDeleteHoliday(self, saveContext, name)` *(extension function — implement to override; no-op by default)*
Called when the delete button is pressed for one or more holidays. This code is executed in a background thread, once for each holiday to be deleted.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the add by calling saveContext.rejectSave(…
- String `name` — The name of the holiday to be deleted.

**Returns:** None

#### `onSaveHoliday(self, saveContext, oldName, newName)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when adding or editing a holiday. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…
- String `oldName` — The holiday name before editing. Will be None for a holiday being added.
- String `newName` — The new name of the edited holiday.

**Returns:** None


### User Management

**Extension functions:**

#### `filterUser(self, user)` *(extension function — implement to override; no-op by default)*
Called for each user loaded into the management table. Return false to hide this user from the management table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- User Object `user` — The user object itself. Call user.get('propertyName') to inpsect. Common proper…

**Returns:** Boolean

#### `filterRole(self, role)` *(extension function — implement to override; no-op by default)*
Called for each role loaded into the management table. Return false to hide this role from the management table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- String `role` — The role name.

**Returns:** Boolean

#### `filterSchedule(self, schedule)` *(extension function — implement to override; no-op by default)*
Called for each schedule loaded into the schedule dropdown in the edit user panel. Return false to hide this schedule from the dropdown. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- String `schedule` — The schedule name.

**Returns:** Boolean

#### `onCreateUser(self, saveContext)` *(extension function — implement to override; no-op by default)*
Called when the add button is pressed in the users table.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the add by calling saveContext.rejectSave(…

**Returns:** None

#### `onDeleteUser(self, saveContext, user)` *(extension function — implement to override; no-op by default)*
Called when the delete button is pressed in the users table. This code is executed in the background thread and is called once for each user selected.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…
- Object `user` — The user that is trying to be deleted. Call user.get('propertyName') to inspect…

**Returns:** None

#### `onSaveUser(self, saveContext, user)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when adding or editing a user. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…
- User Object `user` — The user that is trying to be saved. Call user.get('propertyName') to inspect. …

**Returns:** None

#### `onCreateRole(self, saveContext)` *(extension function — implement to override; no-op by default)*
Called when the add button is pressed in the roles table.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the add by calling saveContext.rejectSave(…

**Returns:** None

#### `onDeleteRole(self, saveContext, name)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when adding or editing a role. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContext.rejectSave…
- String `name` — The role name that is being deleted.

**Returns:** None

#### `onSaveRole(self, saveContext, oldName, newName)` *(extension function — implement to override; no-op by default)*
Called when the save button is pressed when adding or editing a role. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `saveContext` — An object that can be used to reject the edit by calling saveContect.rejectSave…
- String `oldName` — The role name before editing. Will be None for a role being added.
- String `newName` — The new name of the edited role.

**Returns:** None


### Alarm Journal Table

#### `.print(fitWidth, headerFormat, footerFormat, showDialog, landscape)`
This specialized print function will paginate the table onto multiple pages. This function accepts keyword-style invocation.

**Parameters:**
- boolean `fitWidth` — If true, the table's width will be stretched to fit across one page's width. Ro… *(keyword, optional)*
- String `headerFormat` — A string to use as the table's page header. The substring "{0}" will be replace… *(keyword, optional)*
- String `footerFormat` — A string to use as the table's page footer. The substring "{0}" will be replace… *(keyword, optional)*
- boolean `showDialog` — Whether or not the print dialog should be shown to the user. Default is true. [… *(keyword, optional)*
- boolean `landscape` — Used to specify portrait (0) or landscape (1) mode. Default is portrait (0). [o… *(keyword, optional)*

**Returns:** boolean — True if the print job was successful.

#### `.getAlarms()`
Returns a dataset of the alarms currently displayed in the Alarm Journal Table component. The columns will be: EventId, Source, DisplayPath, EventTime, State, Priority and IsSystemEvent.

**Parameters:** none

**Returns:** Dataset — A dataset of alarms.

**Extension functions:**

#### `createPopupMenu(self, selectedAlarmEvents)` *(extension function — implement to override; no-op by default)*
Returns a popup menu that will be displayed when the user triggers a popup menu (right-click) in the table. Use `system.vision.createPopupMenu()` to build the returned menu.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `selectedAlarmEvents` — The alarm events selected on the Alarm Status Table. For an individual alarmEve…

**Returns:** JPopupMenu — A popup menu that was created with `system.vision.createPopupMenu()`.

#### `filterAlarm(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called for each event loaded into the alarm status table. Return false to hide this event from the table. This code is executed in a background thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Alarm Event `alarmEvent` — The alarm event itself. Call alarmEvent.get('propertyName') to inspect. Common …

**Returns:** Boolean

#### `onDoubleClicked(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called when an alarm is double-clicked on to provide custom functionality. Does not return a value.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Alarm Event `alarmEvent` — The alarm event itself. Call alarmEvent.get('propertyName') to inspect. Common …

**Returns:** None

### Alarm Status Table

#### `.print(fitWidth, headerFormat, footerFormat, showDialog, landscape)`
This specialized print function will paginate the table onto multiple pages. This function accepts keyword-style invocation.

**Parameters:**
- boolean `fitWidth` — If true, the table's width will be stretched to fit across one page's width. Ro… *(keyword, optional)*
- string `headerFormat` — A string to use as the table's page header. The substring "{0}" will be replace… *(keyword, optional)*
- string `footerFormat` — A string to use as the table's page footer. The substring "{0}" will be replace… *(keyword, optional)*
- boolean `showDialog` — Whether or not the print dialog should be shown to the user. Default is true. [… *(keyword, optional)*
- boolean `landscape` — Used to specify portrait (0) or landscape (1) mode. Default is portrait (0). [o… *(keyword, optional)*

**Returns:** Boolean — True if the print job was successful.

#### `.getAlarms()`
Returns a dataset of the alarms currently displayed in the Alarm Status Table component. The columns will be: EventId, Source, DisplayPath, EventTime, State, and Priority.

**Parameters:** none

**Returns:** Dataset — A dataset of alarms.

**Extension functions:**

#### `createPopupMenu(self, selectedAlarmEvents)` *(extension function — implement to override; no-op by default)*
Returns a popup menu that will be displayed when the user triggers a popup menu (right click) in the table. Use `system.vision.createPopupMenu()` to build the returned menu.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `selectedAlarmEvents` — The alarm events selected on the Alarm Status Table. For an individual alarm Ev…

**Returns:** Object — The popup menu, created by `system.vision.createPopupMenu`, to display.

#### `filterAlarm(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called for each event loaded into the alarm status table. Return false to hide this event from the table. This code is executed in a background thread so it has a minimal impact on client performance.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- PyAlarmEvent `alarmEvent` — The alarm event itself. Call alarmEvent.get('propertyName') to inspect. Common …

**Returns:** Boolean — Returns true or false for every alarm event in the table. True will show the alarm. False will not …

```python
group = alarmEvent.get("Group")
if group == "Production":
    return True
return False        # It is important to always include logic where False can be returned for alarm events that don't match your criteria
```

#### `isAcknowledgeEnabled(self, selectedAlarmEvents)` *(extension function — implement to override; no-op by default)*
Returns a boolean that represents whether the selected alarm can be acknowledged.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `selectedAlarmEvents` — The alarm events selected on the Alarm Status Table. For an individual alarmEve…

**Returns:** Boolean — Returns true or false for every alarm event in the table.

#### `isShelvedEnabled(self, selectedAlarmEvents)` *(extension function — implement to override; no-op by default)*
Returns a boolean that represents whether the selected alarm can be shelved.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `selectedAlarmEvents` — The alarm events selected on the Alarm Status Table. For an individual alarmEve…

**Returns:** Boolean — Returns true or false for every alarm event in the table.

#### `onDoubleClicked(self, alarmEvent)` *(extension function — implement to override; no-op by default)*
Called when an alarm is double-clicked on to provide custom functionality.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Alarm Event `alarmEvent` — The alarm event that was double clicked. For an individual alarmEvent, call ala…

**Returns:** None

#### `onAcknowledge(self, alarms)` *(extension function — implement to override; no-op by default)*
Called when the Acknowledge button is pressed; the script runs before the ack happens. Return False to abort the acknowledgement, return True to continue as normal.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `alarms` — A list of the alarms to be acknowledged.

**Returns:** Boolean — Returns true or false for every alarm event that is selected.

#### `onShelve(self, alarms)` *(extension function — implement to override; no-op by default)*
Called when the Apply button is pressed on the Shelving panel; the script runs before the shelving happens. Return False to abort shelving, return True to continue as normal.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `alarms` — A list of the alarms to be shelved.

**Returns:** Boolean — Returns true or false for every alarm event that is selected.


### Button

#### `.doClick()`
Programmatically fires the button's click event, as if the user had clicked it. Client scope only.

**Parameters:** none

**Returns:** None


### Date Range

#### `.setRange(start, end)`
Sets the selected range. The outer range will move if needed. Note: the start and end times are determined based on the zoom level and may not move (or may move farther than intended) if the component is zoomed out too …

**Parameters:**
- Date `start` — The starting date for the new selection.
- Date `end` — The ending date for the new selection.

**Returns:** Nothing

#### `.setOuterRange(start, end)`
Sets the outer range. The selected range will move if needed. Note: the start and end times are determined based on the zoom level and may not move (or may move farther than intended) if the component is zoomed out too …

**Parameters:**
- Date `start` — The starting date for the new outer range.
- Date `end` — The ending date for the new outer range.

**Returns:** Nothing


### Bar Chart

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None

#### `getBarColor(self, series, category, value, defaultColor)` *(extension function — implement to override; no-op by default)*
Provides a chance to override the color of each bar. Can be used to have bar colors changed based upon bar value. Returning the value None will use the default bar color for the series.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `series` — The series index for this bar.
- int `category` — The category index for this bar.
- int `value` — The value (a number) of this bar.
- Color `defaultColor` — The color that the bar would be if this function wasn't invoked.

**Returns:** Color


### Chart

#### `getPlotProperties()`
Retrieves the value of the selected PlotProperty objects that define background color and weight of each plot.

**Parameters:** none

**Returns:** List

#### `getProperties()`
Retrieves the value of custom properties added to the Chart.

**Parameters:** none

**Returns:** List

#### `getSelectedData()`
Returns the value of the selected chart entity as a string.

**Parameters:** none

**Returns:** String

#### `getSelectedEntity()`
Returns the selected chart entity directly.

**Parameters:** none

**Returns:** ChartEntity

#### `getSubplotMode()`
Retrieves the subplot mode currently in use: 0 = Shared Domain, 1 = Shared Range.

**Parameters:** none

**Returns:** Int

#### `getXAxes()`
Returns a dictionary of the related rendering properties.

**Parameters:** none

**Returns:** Dictionary<String, AxisConfig>

#### `getYAxes()`
Returns a dictionary of the related rendering properties.

**Parameters:** none

**Returns:** Dictionary<String, AxisConfig>

#### `refreshChart(subplotIndex, dataSetIndex)`
Refreshes the dataset for the specified subplot and dataset.

**Parameters:**
- int `subplotIndex`
- int `dataSetIndex`

**Returns:** None

#### `setDatasetEnabled(dataSetName, isEnabled)`
Sets a dataset to be enabled or not enabled.

**Parameters:**
- string `dataSetName`
- boolean `isEnabled` — Whether the dataset is enabled.

**Returns:** None

#### `setDatasetPlotNumber(dataSetName, plotNumber)`
Sets a dataset's plot number.

**Parameters:**
- string `dataSetName`
- int `plotNumber`

**Returns:** None

#### `setDatasetXAxis(dataSetName, axisName)`
Sets a dataset's X axis name.

**Parameters:**
- string `dataSetName`
- string `axisName`

**Returns:** None

#### `setDatasetYAxis(dataSetName, axisName)`
Sets a dataset's Y axis name.

**Parameters:**
- string `dataSetName`
- string `axisName`

**Returns:** None

#### `setSubplotMode(mode)`
Sets the subplot mode to be used when there is more than one subplot.

**Parameters:**
- int `mode` — 0 = Shared Domain, 1 = Shared Range.

**Returns:** None

#### `setXAxes(axisConfigMap)`
Sets defined rendering properties using AxisConfig objects.

**Parameters:**
- Dictionary `axisConfigMap` — String keys to AxisConfig objects.

**Returns:** None

#### `setYAxes(axisConfigMap)`
Sets defined rendering properties using AxisConfig objects.

**Parameters:**
- Dictionary `axisConfigMap` — String keys to AxisConfig objects.

**Returns:** None

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None

#### `getXTraceLabel(self, chart, penName, yValue)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to configure the x-trace label. Return a string to override the default label.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.
- String `penName` — The name of the pen the x-trace label applies to.
- int `yValue` — The y-value of the pen at the x-trace location.

**Returns:** None


### Easy Chart

#### `exportExcel(filename)`
This function saves the chart's datasets as an Excel file. Returns a String of the complete file path chosen by the user, or None if the user canceled the save.

**Parameters:** none

**Returns:** String

#### `print()`
This function will print the chart.

**Parameters:** none

**Returns:** None

#### `setMode(mode)`
Sets the current mode for the chart.

**Parameters:**
- Integer `mode` — 0 = Zoom Mode (default; drag to draw a zoom rectangle), 1 = Pan Mode (drag to p…

**Returns:** None

#### `exportDatasets()`
Returns an Array List of datasets, representing the time series data of each type of pen.

**Parameters:** none

**Returns:** Array List — Each dataset represents timeseries data for a set of pens.

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting. Doesn't return anything.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None

#### `getXTraceLabel(self, chart, penName, yValue)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to configure the x-trace label. Return a string to override the default label.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.
- String `penName` — The name of the pen the x-trace label applies to.
- Integer `yValue` — The y-value of the pen at the x-trace location.

**Returns:** None

#### `onPowerTableRowsDropped(self, sourceTable, rows, rowData)` *(extension function — implement to override; no-op by default)*
Called when the user has dropped rows from a power table on the chart. The source table must have dragging enabled.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Component `sourceTable` — A reference to the table that the rows were dragged from.
- List `rows` — An array of the row indicies that were dragged, in the order they were selected.
- Dataset `rowData` — A dataset containing the rows that were dragged.

**Returns:** None

#### `onTagsDropped(self, paths)` *(extension function — implement to override; no-op by default)*
Called when the user has dropped tags from the tag tree onto the chart. Normally, the chart will add pens automatically when tags are dropped, but this default behavior will be suppressed if this extension function is i…

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- List `paths` — A list of the tag paths that were dropped on the chart.

**Returns:** None

### Equipment Schedule

#### `.getDateAt(event)`
Returns a date time representing a point in time at the mouse event position.

**Parameters:**
- Event Object `event` — A mouse event object.

**Returns:** Date — A datetime, representing a point in time on the chart where the mouse event occurred.

**Extension functions:**

#### `onBackgroundDragged(self, itemID, startDate, endDate, event)` *(extension function — implement to override; no-op by default)*
Called when the user drags a segment on the schedule background.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `itemID` — The ID of the equipment item of the row where the user dragged.
- Date `startDate` — The datetime corresponding to where the user started dragging.
- Date `endDate` — The datetime corresponding to where the user ended dragging.
- Event Object `event` — The mouse event.

**Returns:** None

#### `onEventClicked(self, itemID, eventId, event)` *(extension function — implement to override; no-op by default)*
Called when the user clicks on a scheduled event. Use event.clickCount to detect double clicks.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `itemID` — The ID of the equipment item of the event that was clicked on.
- int `eventId` — The ID of the event that was clicked on.
- Event Object `event` — The mouse event.

**Returns:** None

#### `onEventDropped(self, eventId, oldItemId, newItemId, oldStartDate, newStartDate, newEndDate)` *(extension function — implement to override; no-op by default)*
Called when the user drags and drops a scheduled event. It is up to this script to actually alter the underlying data to reflect the schedule change.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `eventId` — The ID of the scheduled event that was moved.
- int `oldItemId` — The ID of the item this event was originally correlated against.
- int `newItemId` — The ID of the item whose schedule the event was dropped on.
- Date `oldStartDate` — The original starting datetime of the event.
- Date `newStartDate` — The new starting datetime of the event.
- Date `newEndDate` — The new ending datetime of the event.

**Returns:** None

#### `onEventPopupTrigger(self, itemId, eventId, event)` *(extension function — implement to override; no-op by default)*
Called when the user right-clicks on a scheduled event. This would be the appropriate time to create and display a popup menu.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `itemId` — The ID of the equipment item of the event that was right-clicked on.
- int `eventId` — The ID of the event that was right-clicked on.
- Event Object `event` — The mouse event that caused the popup trigger.

**Returns:** None

#### `onEventResized(self, eventId, itemId, oldStartDate, oldEndDate, newStartDate, newEndDate)` *(extension function — implement to override; no-op by default)*
Called when the user drags the edge of an event to resize its time span. It is up to this script to actually alter the underlying data to reflect the schedule change.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `eventId` — The ID of the scheduled event that was resized.
- int `itemId` — The ID of the item this event is correlated against.
- Date `oldStartDate` — The original starting datetime of the event.
- Date `oldEndDate` — The original ending datetime of the event.
- Date `newStartDate` — The new starting datetime of the event.
- Date `newEndDate` — The new ending datetime of the event.

**Returns:** None

#### `onPopupTrigger(self, itemId, event)` *(extension function — implement to override; no-op by default)*
Called when the user right-clicks outside of an event. This would be the appropriate time to create and display a popup menu.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `itemId` — The item ID of the equipment line that was clicked on (if any).
- Event Object `event` — The mouse event that caused the popup trigger.

**Returns:** None


### Gantt Chart

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None


### Pie Chart

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None


### Status Chart

**Extension functions:**

#### `configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further chart configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None

#### `getToolTip(self, seriesIndex, selectedTimeStamp, timeDiff, seletedStatus, data, properties, defaultString)` *(extension function — implement to override; no-op by default)*
Return a formatted tool tip String.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `seriesIndex` — The series index corresponding to the column in the series dataset.
- int `selectedTimeStamp` — The time stamp corresponding to the x value of the displayed tooltip.
- int `timeDiff` — The width of the current status interval measured in seconds since the epoch.
- int `seletedStatus` — The status value corresponding to the x value of the displayed tooltip.
- PyDataset `data` — The series dataset as a PyDataset.
- PyDataset `properties` — The series properties dataset as a PyDataset.
- string `defaultString` — The default tooltip string.

**Returns:** String — The (possibly overridden) tooltip string; defaults to `defaultString`.


### Template Canvas

#### `.getAllTemplates()`
Returns a list of the templates that comprise the template canvas.

**Parameters:** none

**Returns:** List — A list of VisionTemplate definitions. Each instance in the canvas will return its definition's nam…

#### `.getTemplate(name)`
Obtains the designated template object from the template canvas.

**Parameters:**
- String `name` — The name of the template as defined by the "name" column of the dataset populat…

**Returns:** VisionTemplate — Returns the template instance. Properties on the instance can be accessed by calling .propertyName

**Extension functions:**

#### `initializeTemplate(self, template)` *(extension function — implement to override; no-op by default)*
This will be called once per template that is loaded. This is a good chance to do any custom initialization or setting parameters on the template.

**Parameters:**
- Component `self` — A reference to the component invoking this function.
- Vision Template `template` — The template. The name of the template in the dataset will be available as temp…

**Returns:** None


### Template Repeater

#### `.getLoadedTemplates()`
Returns a list of templates loaded into the Template Repeater. Properties on the components within each instance can be referenced by calling getComponent().

**Parameters:** none

**Returns:** List of Templates


### Compass

**Extension functions:**

#### `.configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None


### Meter

**Extension functions:**

#### `.configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None


### Thermometer

**Extension functions:**

#### `.configureChart(self, chart)` *(extension function — implement to override; no-op by default)*
Provides an opportunity to perform further configuration via scripting.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JFreeChart `chart` — A JFreeChart object. Refer to the JFreeChart documentation for API details.

**Returns:** None


### Numeric Text Field

#### `getSelectedText()`
Returns the currently selected or highlighted text in the field. Client scope only.

**Parameters:** none

**Returns:** String


### Text Field

#### `getSelectedText()`
Returns the currently selected or highlighted text in the text field.

**Parameters:** none

**Returns:** String — Returns the currently selected or highlighted text in the text field.


### Web Browser

#### `.getBrowser()`
This function will return the underlying browser object. See the JxBrowser guidelines for more information.

**Parameters:** none

**Returns:** Object — The Browser Object.

#### `.executeJavaScript(javaScript)`
This function allows users to execute arbitrary JavaScript on the loaded page.

**Parameters:**
- String `javaScript` — The code to execute on the page.

**Returns:** None

#### `.getImage()`
This function will return a byte array screenshot of the current browser window, in JPEG format.

**Parameters:** none

**Returns:** ByteArray — The current browser window, rendered as a JPEG, in binary format.

#### `.back()`
This function navigates one page back in the browser history.

**Parameters:** none

**Returns:** None

#### `.forward()`
This function navigates one page forward in the browser history.

**Parameters:** none

**Returns:** None

#### `.refresh()`
This function refreshes the current page.

**Parameters:** none

**Returns:** None

**Extension functions:**

#### `initialize(self, browser, browserView)` *(extension function — implement to override; no-op by default)*
Called when the Web Browser component is initialized. Provides a chance to initialize the browser further. Enabling or disabling this function will cause the Web Browser component to re-initialize.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- JxBrowser `browser` — The underlying JxBrowser instance of the Browser class.
- BrowserView `browserView` — The underlying rendering class that contains the Browser instance.

**Returns:** Nothing


### PDF Viewer

#### `.loadPDFBytes(bytes, name)`
This function will pass in the bytes of a PDF and load them into the PDF Viewer component.

**Parameters:**
- string `bytes` — The bytes of the PDF to be displayed on the component.
- string `name` — The name of the PDF.

**Returns:** None

#### `.print(showDialog)`
This function will print the PDF.

**Parameters:**
- boolean `showDialog` — If true, shows the user a print dialog. Default is true. [optional]

**Returns:** None

#### `.setZoomFactor(zoom)`
This function will set the current zoom level of the PDF, adjusted to stay within the minimum/maximum zoom range. Will zoom in on center of page.

**Parameters:**
- float `zoom` — Zoom factor to use. 1.0 is no zoom.

**Returns:** None


### Report Viewer

#### `.print(printerName, showDialog)`
Uses the named printer and determines if the print dialog window should appear or not.

**Parameters:**
- String `printerName` — The name of the printer the report should be sent to. Will use the default prin…
- Boolean `showDialog` — True if the dialog window should appear, False if the dialog window should be s…

**Returns:** None

```python
#calls print on a Report Viewer component located in the same window
reportViewer = event.source.parent.getComponent('Report Viewer')
reportViewer.print()
```

#### `getBytesPDF()`
Return the bytes of the generated report in the Report Viewer using PDF format.

**Parameters:** none

**Returns:** Byte Array — The bytes of the report in PDF format.

#### `getBytesPNG()`
Return the bytes of the generated report in the Report Viewer using PNG format.

**Parameters:** none

**Returns:** Byte Array — The bytes of the report in PNG format.

#### `saveAsPDF(fileName)`
Prompts the user to save a copy of the report as a PDF. Shows a file selection window with the extension set to PDF.

**Parameters:**
- String `fileName` — A suggested filename to save the report as.

**Returns:** None

```python
#Saves the file as a PDF to a user selected location.
reportViewer = event.source.parent.getComponent('Report Viewer')
reportViewer.saveAsPDF("Daily Report")
```

#### `saveAsXls(fileName)`
Prompts the user to save a copy of the report as an XLS file. Shows a file selection window with the extension set to XLS.

**Parameters:**
- String `fileName` — A suggested filename to save the report as. *(keyword, optional)*

**Returns:** None

**Extension functions:**

#### `onReportGenerated(self, pdfBytes)` *(extension function — implement to override; no-op by default)*
Called when the Report generation process has been completed.

**Parameters:**
- Component `self` — A reference to the component invoking this method.
- Byte Array `pdfBytes` — The PDF formatted bytes generated by the Report.

**Returns:** None


### Comments Panel

**Extension functions:**

#### `insertNote(self, note, filename, sticky)` *(extension function — implement to override; no-op by default)*
Called when a note is added.

**Parameters:**
- component `self` — A reference to the component that is invoking this function.
- string `note` — The text contents of the note.
- string `filename` — The full filepath to the attachment.
- string `sticky` — A boolean indicating whether this note should be flagged as stickied.

**Returns:** None

#### `deleteNote(self, id)` *(extension function — implement to override; no-op by default)*
Called when a user clicks the 'delete' link on a note.

**Parameters:**
- component `self` — A reference to the component that is invoking this function.
- integer `id` — The id of the note.

**Returns:** None

#### `unstickNote(self, id)` *(extension function — implement to override; no-op by default)*
Called when a user clicks the 'unstick' link on a note.

**Parameters:**
- component `self` — A reference to the component that is invoking this function.
- integer `id` — The id of the note.

**Returns:** None

#### `downloadAttachment(self, id)` *(extension function — implement to override; no-op by default)*
Called when a user attempts to download an attachment from a note.

**Parameters:**
- component `self` — A reference to the component that is invoking this function.
- integer `id` — The id of the note.

**Returns:** None

#### `canDelete(self, id)` *(extension function — implement to override; no-op by default)*
Returns whether or not a note with the given id can be deleted. Notes that return True will show a 'delete' link.

**Parameters:**
- component `self` — A reference to the component that is invoking this function.
- integer `id` — The id of the note.

**Returns:** boolean — Notes with a True return can be deleted by the user, False return can not be deleted.


### List

#### `.addSelectionInterval(start, end)`
Adds the options at indexes start through end (inclusive) to the selected options.

**Parameters:**
- int `start` — The first index (starting at 0) to add to the selection.
- int `end` — The last index (starting at 0) to add to the selection.

**Returns:** None

#### `.clearSelection()`
Clears the current selection, making nothing selected.

**Parameters:** none

**Returns:** None

#### `.getSelectedIndices()`
Returns a list of the selected indices in increasing order. Returns an empty list if nothing is selected.

**Parameters:** none

**Returns:** List of Integers

#### `.getSelectedValue()`
Returns the currently selected value, or None if the selection is empty.

**Parameters:** none

**Returns:** Object

#### `.getSelectedValues()`
Returns a list of the currently selected values. Returns an empty list if the selection is empty.

**Parameters:** none

**Returns:** Object[]

#### `.isSelectedIndex(index)`
Checks whether or not the given index is currently selected.

**Parameters:**
- int `index`

**Returns:** boolean

#### `.isSelectionEmpty()`
Checks to see if anything is selected in the list or not.

**Parameters:** none

**Returns:** boolean

#### `.setSelectedValue(value)`
Sets the currently selected value to the argument, if found in the list.

**Parameters:**
- Object `value`

**Returns:** None

#### `.setSelectedValues(valueList)`
Sets the currently selected values in the component, selecting multiple options. The options selected are determined by the valueList parameter, which is expected to be a list of literal values that map to options in th…

**Parameters:**
- Object `valueList` — Python list containing values that should map to options in the component.

**Returns:** None

### Power Table

#### `.getSelectedColumns()`
Returns a list of ints representing the currently selected columns.

**Parameters:** none

**Returns:** Object of Integers — An object containing integers that represent the indices of the selected columns. Can be iterated o…

#### `.getSelectedRows()`
Returns a list of ints representing the currently selected rows.

**Parameters:** none

**Returns:** Object of Integers — An object containing integers that represent the indices of the selected rows. Can be iterated over…

#### `.print([fitWidth] [, headerFormat] [, footerFormat] [, showDialog] [, landscape])`
This specialized print function will paginate the table onto multiple pages. This function accepts keyword-style invocation.

**Parameters:**
- boolean `fitWidth` — If true, the table's width will be stretched to fit across one page's width. Ro… *(keyword, optional)*
- String `headerFormat` — A string to use as the table's page header. The substring "{0}" will be replace… *(keyword, optional)*
- String `footerFormat` — A string to use as the table's page footer. The substring "{0}" will be replace… *(keyword, optional)*
- boolean `showDialog` — Used to determine if the print dialog should be shown to the user. Default is t… *(keyword, optional)*
- boolean `landscape` — Used to specify portrait (0) or landscape (1) mode. Default is portrait (0). [o… *(keyword, optional)*

**Returns:** boolean — True if the print job was successful.

#### `.setColumnWidth(column, width)`
Used to set a column's width at runtime.

**Parameters:**
- int `column` — Column to adjust.
- int `width` — Width in pixels.

**Returns:** None

**Extension functions:**

#### `configureCell(self, value, textValue, selected, rowIndex, colIndex, colName, rowView, colView)` *(extension function — implement to override; no-op by default)*
Provides a chance to configure the contents of each cell. Returns a dictionary of name-value pairs with the desired attributes. Available attributes (and their Java types) include: 'background' (color), 'border' (border…

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Object `value` — The value in the dataset at this cell.
- string `textValue` — The text the table expects to display at this cell (may be overriden by includi…
- boolean `selected` — A boolean indicating whether this cell is currently selected.
- int `rowIndex` — The index of the row in the underlying dataset.
- int `colIndex` — The index of the column in the underlying dataset.
- string `colName` — The name of the column in the underlying dataset.
- int `rowView` — The index of the row, as it appears in the table view (affected by sorting).
- int `colView` — The index of the column, as it appears in the table view (affected by column re…

**Returns:** Dictionary of Attributes

#### `configureEditor(self, colIndex, colName)` *(extension function — implement to override; no-op by default)*
Provides a chance to configure how each column is edited. Returns a dictionary of name-value pairs with desired editor attributes.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `colIndex` — The index of the column in the underlying dataset.
- string `colName` — The name of the column in the underlying dataset.

**Returns:** Dictionary of name value pairs

```python
return {'options': [(0, 'Option A'), (1, 'Option B')], 'rowHeight':100}
```

#### `configureHeaderStyle(self, colIndex, colName)` *(extension function — implement to override; no-op by default)*
Provides a chance to configure the style of each column header. Return a dictionary of name-value pairs with the desired attributes.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `colIndex` — The index of the column in the underlying dataset.
- string `colName` — The name of the column in the underlying dataset.

**Returns:** Dictionary of name value pairs

#### `initialize(self)` *(extension function — implement to override; no-op by default)*
Called when the window containing this table is opened, or the template containing it is loaded. Provides a chance to initialize the table further, for example, selecting a specific row.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.

**Returns:** None

#### `isCellEditable(self, rowIndex, colIndex, colName, value)` *(extension function — implement to override; no-op by default)*
Returns a boolean that determines whether or not the current cell is editable.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row that was edited, relative to the underlying dataset.
- int `colIndex` — Index of the column that was edited, relative to the underlying dataset.
- string `colName` — Name of the column in the underlying dataset.
- Object `value` — The value at the cell location.

**Returns:** boolean

#### `onCellEdited(self, rowIndex, colIndex, colName, oldValue, newValue)` *(extension function — implement to override; no-op by default)*
Called when the user has edited a cell in the table. It is up to the implementation of this function to alter the underlying data that drives the table — either altering the dataset directly, or running a SQL UPDATE.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row that was edited, relative to the underlying dataset.
- int `colIndex` — Index of the column that was edited, relative to the underlying dataset.
- string `colName` — Name of the column in the underlying dataset.
- Object `oldValue` — The old value at the location, before it was edited.
- Object `newValue` — The new value input by the user.

**Returns:** None

```python
def myFunction():
    # Do your work here
    system.vision.showMessage("Assuming you don't change focus outside of this script\nYou will only see this message once per cell edit")
system.vision.invokeLater(myFunction)
```

#### `onMousePress(self, rowIndex, colIndex, value, event)` *(extension function — implement to override; no-op by default)*
Called when the user clicks on a table cell.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row, starting at 0, relative to the underlying dataset.
- int `colIndex` — Index of the column starting at 0, relative to the underlying dataset.
- Object `value` — The value at the location clicked on.
- MouseEvent `event` — The MouseEvent object that caused this click event.

**Returns:** None

#### `onMouseRelease(self, rowIndex, colIndex, value, event)` *(extension function — implement to override; no-op by default)*
Called when the user releases the mouse button on a table cell.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row, starting at 0, relative to the underlying dataset.
- int `colIndex` — Index of the column starting at 0, relative to the underlying dataset.
- Object `value` — The value at the location that the mouse is released on.
- MouseEvent `event` — The MouseEvent object that caused this released event.

**Returns:** None

#### `onMouseClick(self, rowIndex, colIndex, value, event)` *(extension function — implement to override; no-op by default)*
Called when the user clicks on a table cell.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row, starting at 0, relative to the underlying dataset.
- int `colIndex` — Index of the column starting at 0, relative to the underlying dataset.
- Object `value` — The value at the location clicked on.
- MouseEvent `event` — The MouseEvent object that caused this click event.

**Returns:** None

#### `onDoubleClick(self, rowIndex, colIndex, value, event)` *(extension function — implement to override; no-op by default)*
Called when the user double-clicks on a table cell.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row, starting at 0, relative to the underlying dataset.
- int `colIndex` — Index of the column starting at 0, relative to the underlying dataset.
- Object `value` — The value at the location clicked on.
- MouseEvent `event` — The MouseEvent object that caused this double-click event.

**Returns:** None

#### `onPopupTrigger(self, rowIndex, colIndex, colName, value, event)` *(extension function — implement to override; no-op by default)*
Called when the user right-clicks on a table cell. This would be the appropriate time to create and display a popup menu.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `rowIndex` — Index of the row, starting at 0, relative to the underlying dataset.
- int `colIndex` — Index of the column starting at 0, relative to the underlying dataset.
- string `colName` — Name of the column in the underlying dataset.
- Object `value` — The value at the location clicked on.
- MouseEvent `event` — The MouseEvent object that caused this popup trigger event.

**Returns:** None

#### `onRowsDropped(self, sourceTable, rows, rowData, dropIndexLocation)` *(extension function — implement to override; no-op by default)*
Called when the user has dropped rows on this table. Note that the rows may have come from this table or another table. The source table must have dragging enabled.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Component `sourceTable` — A reference to the table that the rows were dragged and dropped in the same tab…
- list `rows` — An array of the row indices that were dragged, in the order they were selected.
- Dataset `rowData` — A dataset containing the rows that were dragged.
- int `dropIndexLocation` — Row index where the rows were dropped.

**Returns:** None

### Table

#### `.addRow(newRow)`
Adds a new row to the end of the table's dataset.

**Parameters:**
- PySequence `newRow` — A sequence containing the values for the new row. The length of the sequence mu…

**Returns:** None

#### `.deleteRow(rowIndex)`
Deletes a row from the table's dataset.

**Parameters:**
- int `rowIndex` — The index of the row to delete.

**Returns:** None

#### `.exportCSV(filename, showHeaders)`
Prompts the user to save the table's data as a CSV file.

**Parameters:**
- String `filename` — A suggested filename for the user. For example: "table_data.csv"
- boolean `showHeaders` — If true, include headers in CSV file.

**Returns:** String — The path to the saved file, or null if the operation was cancelled.

#### `.getDataAsHTML(title, width)`
Creates an HTML page as a string in memory. This can then be written to a file, a database, emailed, etc.

**Parameters:**
- String `title` — The title for the HTML page.
- int `width` — The width (in pixels) for the "table" element in the resulting html page.

**Returns:** String — A string containing an HTML-formatted version of the table's data.

#### `.getRowsInViewOrder()`
Returns a list of ints that represent the underlying dataset's rows as they appear in the current sort order that the user is viewing.

**Parameters:** none

**Returns:** List of Integers

#### `.getSelectedColumn()`
Returns the index of the currently selected column, or -1 if none is selected.

**Parameters:** none

**Returns:** int

#### `.getSelectedColumnCount()`
Returns the number of columns that are currently selected.

**Parameters:** none

**Returns:** int

#### `.getSelectedRow()`
Returns the index of the currently selected row, or -1 if none is selected.

**Parameters:** none

**Returns:** int

#### `.getSelectedRows()`
Returns a list of the indexes of the selected rows, or None if none is selected.

**Parameters:** none

**Returns:** List, None

#### `.getSelectedRowCount()`
Returns the number of rows that are currently selected.

**Parameters:** none

**Returns:** int

#### `.isCellSelected(row, column)`
Tests whether the cell at the given row and column is currently selected or not.

**Parameters:**
- int `row` — The row to test.
- int `column` — The column to test.

**Returns:** boolean

#### `.isColumnSelected(column)`
Tests whether the given column is currently selected or not.

**Parameters:**
- int `column` — The column to test.

**Returns:** boolean

#### `.isRowSelected(row)`
Tests whether the given row is currently selected or not.

**Parameters:**
- int `row` — The row to test.

**Returns:** boolean

#### `.print(fitWidth, headerFormat, footerFormat, showDialog, landscape)`
This specialized print function will paginate the table onto multiple pages. This function accepts keyword-style invocation.

**Parameters:**
- boolean `fitWidth` — If true, the table's width will be stretched to fit across one page's width. Ro… *(keyword, optional)*
- string `headerFormat` — A string to use as the table's page header. The substring "{0}" will be replace… *(keyword, optional)*
- string `footerFormat` — A string to use as the table's page footer. The substring "{0}" will be replace… *(keyword, optional)*
- boolean `showDialog` — Whether or not the print dialog should be shown to the user. Default is true. [… *(keyword, optional)*
- boolean `landscape` — Used to specify portrait (0) or landscape (1) mode. Default is portrait (0). [o… *(keyword, optional)*

**Returns:** boolean — True if the print job was successful.

#### `.setColumnLabel(column, label)`
Used to set a column's header label to a new string at runtime.

**Parameters:**
- int `column` — The column index that will get a new header label.
- String `label` — The new header label.

**Returns:** None

#### `.setColumnSelectionInterval(index0, index1)`
Sets the given range of columns to be selected. If index0==index1, it will select a single column.

**Parameters:**
- int `index0` — The first index.
- int `index1` — The second index.

**Returns:** boolean — True if selection range is valid.

#### `.setColumnWidth(column, width)`
Used to set a column's width at runtime.

**Parameters:**
- int `column` — The index of the column.
- int `width` — The width to set it at in pixels.

**Returns:** None

#### `.setRowSelectionInterval(index0, index1)`
Sets the given range of rows to be selected. If index0==index1, it will select a single row.

**Parameters:**
- int `index0` — The first index.
- int `index1` — The second index.

**Returns:** boolean — True if selection range is valid.

#### `.setSelectedColumn(column)`
Sets the given column to be the selected column.

**Parameters:**
- int `column` — Column to select.

**Returns:** None

#### `.setSelectedRow(row)`
Sets the given row to be the selected row.

**Parameters:**
- int `row` — Row to select.

**Returns:** None

#### `.setValue(row, column, value)`
Sets the value in the specified cell, altering the table's Data property. Will fire a propertyChange event for the "data" property, as well as a cellEdited event.

**Parameters:**
- int `row` — The index of the row to set the value at.
- int `column` — The index or name of the column to set a value at.
- PyObject `value` — The new value to use at the given row/column location.

**Returns:** None

#### `.sortByColumn(columnName [, asc])`
Instructs the table to sort the data by the named column.

**Parameters:**
- String `columnName` — The name of the column.
- boolean `asc` — 1 means ascending, 0 means descending. (default = 1) [optional]

**Returns:** None

#### `.sortOriginal()`
Instructs the table to clear any custom sort columns and display the data as it is sorted in the underlying dataset.

**Parameters:** none

**Returns:** None

#### `.updateRow(rowIndex, changes)`
Updates an entire row of the table's dataset.

**Parameters:**
- int `rowIndex` — The index of the row to update.
- PyDictionary `changes` — A dictionary containing the updated values for the row.

**Returns:** None

**Extension functions:**

#### `getBackgroundAt(self, row, col, isSelected, value, defaultColor)` *(extension function — implement to override; no-op by default)*
Called for each cell, returns the appropriate background color. Do not block, sleep, or execute any I/O; called on the painting thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `row` — The row index of the cell.
- int `col` — The column index of the cell.
- boolean `isSelected` — Whether the cell is currently selected.
- Object `value` — The value in the table's dataset at index [row, col].
- Color `defaultColor` — The color the table would have chosen if this function was not implemented.

**Returns:** Color

#### `getForegroundAt(self, row, col, isSelected, value, defaultColor)` *(extension function — implement to override; no-op by default)*
Called for each cell, returns the appropriate foreground (text) color. Do not block, sleep, or execute any I/O; called on the painting thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `row` — The row index of the cell.
- int `col` — The column index of the cell.
- boolean `isSelected` — Whether the cell is currently selected.
- Object `value` — The value in the table's dataset at index [row, col].
- Color `defaultColor` — The color the table would have chosen if this function was not implemented.

**Returns:** Color

#### `getDisplayTextAt(self, row, col, isSelected, value, defaultText)` *(extension function — implement to override; no-op by default)*
Called for each cell, returns a String which will be used as the text of the cell. Do not block, sleep or execute any I/O; called on the painting thread.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- int `row` — The row index of the cell.
- int `col` — The column index of the cell.
- boolean `isSelected` — Whether the cell is currently selected.
- Object `value` — The value in the table's dataset at index [row, col].
- String `defaultText` — The string the table would have chosen if this function was not implemented.

**Returns:** String


### Tag Browse Tree

**Extension functions:**

#### `filterTag(self, tag)` *(extension function — implement to override; no-op by default)*
Called for each tag loaded into tag browse tree. Return false to hide this tag from the tree. Note that this is called for each Tag, not any folders that appear in the component.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Tag Object `tag` — The tag itself.

**Returns:** Boolean

#### `createPopupMenu(self, clickedTag, selectedTags)` *(extension function — implement to override; no-op by default)*
Returns a popup menu that will be displayed when the user triggers a popup menu (right click) on the tree. Use `system.vision.createPopupMenu` to build it.

**Parameters:**
- Component `self` — A reference to the component that is invoking this function.
- Tag Object `clickedTag` — The tag of the clicked-on tree path.
- List `selectedTags` — The tags of the selected paths of the tree.

**Returns:** JPopupMenu


### Tree View

#### `.clearSelection()`
Clears the current selection.

**Parameters:** none

**Returns:** Nothing

#### `.collapseAll()`
Collapses all nodes in the tree.

**Parameters:** none

**Returns:** Nothing

#### `.expandAll()`
Expands all nodes in the tree.

**Parameters:** none

**Returns:** Nothing

#### `.getSelectedItems()`
Returns a list of the selected items' indexes. These are the row indexes that the selected tree nodes were found in the underlying dataset. Implicitly created folder nodes that have no index will not be included.

**Parameters:** none

**Returns:** List of Integers

#### `.getSelectedPaths()`
Returns a list of the selected items' paths. A path to an item is the path to its parent plus its normal (non-selected) text.

**Parameters:** none

**Returns:** List of Strings


### The Window Object

#### `.getRootContainer()`
Returns a reference to the Root Container in the window.

**Parameters:** none

**Returns:** Object — A reference to the Root Container, which is functionally just a Vision Container.

#### `.getComponentForPath(path)`
Returns a reference to a component. The path parameter allows you to specify the full path to the component as a string.

**Parameters:**
- String `path` — The path to the component, using a period as a delimiter, such as "Root Contain…

**Returns:** Object — The component specified, or None if there is a typo in the path.


## Gotchas

- **Extension functions are silent no-ops until implemented.** Every extension function listed above (`configureCell`, `filterAlarm`, `onCellEdited`, `configureChart`, `initialize`, etc.) exists as an empty stub. If you expect custom filtering, coloring, or validation and nothing happens, check whether the function body is actually empty — this is the single most common "it's not working" report for both Vision and Perspective components.
- **Perspective vs. Vision component references are not interchangeable.** `self.getSibling(...)` / `self.getChild(...)` only work in Perspective; `event.source.parent.getComponent(...)` only works in Vision. Copy-pasting an idiom from one environment into the other fails silently or throws immediately.
- **`row` vs `rowIndex` (Perspective Table).** `row` is the row's true index in the underlying data (stable under sorting/paging/searching); `rowIndex` is the visual index in the current view (affected by sorting/paging/searching). Passing a `rowIndex` where the API expects `row` silently operates on the wrong record.
- **Admin-panel extension functions (Roster/Schedule/User Management) run on a background thread.** `onSaveUser`, `onCreateRoster`, `onDeleteSchedule`, etc. are *not* called on the UI/EDT thread. Reject an edit via the passed `saveContext`/`createContext`/`deleteContext` object rather than raising an exception, and don't touch Swing components directly from inside them.
- **Vision cell-rendering extension functions must not block.** `getBackgroundAt`, `getForegroundAt`, and `getDisplayTextAt` (Table) are called on the painting thread — no sleeping, blocking I/O, or database calls, or the whole UI will stutter/freeze.
- **`onCellEdited`/`onMousePress`-style extension functions that need to touch other components must use `system.vision.invokeLater(...)`.** Editing a cell and immediately trying to show a dialog or update another component directly from the callback can misbehave; wrap the follow-up work in a function and pass it to `invokeLater`.
- **Some methods are Client-scope only** (e.g. `Button.doClick()`, `Numeric Text Field.getSelectedText()`, `Text Field.getSelectedText()`). Calling them from a Gateway-scoped script (a tag change script, scheduled script, etc.) will fail because there's no live Swing component to act on.
- **Chart-family Vision components (Bar/Gantt/Pie/Compass/Meter/Thermometer/Status Chart) mostly expose only `configureChart(self, chart)`,** not direct getter/setter methods — you configure appearance by manipulating the raw `JFreeChart` object handed to you, not through component methods.
- **Several Perspective components have no component-specific methods or extension functions at all** (Drawing, Equipment Schedule, Tree, Accordion, View Canvas, Form, Horizontal Menu, Menu Tree, as harvested here) — all scripting on them happens through Component Events instead. Don't go looking for a `.method()` that doesn't exist; check the component's **Component Events** section instead.
- **Component object types passed into scripts (Dataset, QualifiedValue, QualityCode, PyAlarmEvent, SProcCall, tag `Results`, etc.) are documented separately** on the [Scripting Object Reference](appendix/reference-pages/scripting-object-reference.md) page — not repeated per-component. When a parameter or return type here just says "Alarm Event" or "QualifiedValue", look there for its full attribute/method list.
- **`.print(...)` on table-family components (Table, Power Table, Alarm Journal/Status Table) takes keyword-style arguments** (`fitWidth`, `headerFormat`, `footerFormat`, `showDialog`, `landscape`) — passing them positionally in the wrong order is a common mistake; prefer calling with explicit keyword arguments.
