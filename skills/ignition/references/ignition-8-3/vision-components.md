# Ignition 8.3 — Vision component reference

## How Vision components work

**Windows vs. templates.** In Vision, a *window* is the top-level unit of design — identified by its full folder path (e.g. `OptionsWindows/UserOptions`) — and every window has exactly one un-deletable **Root Container**, which is functionally an ordinary Container component that happens to be the window's outermost component. All other components live inside the Root Container or nested containers within it. There is really only one kind of window object in Vision; "Main," "Popup," "Docked," and "Sidebar" window *types* (see the Window Types doc) are just the same window object configured with different titlebar/border/dock/cache properties. A *template*, by contrast, is a reusable group of components with its own parameter set, defined once and then instantiated many times — via drag-and-drop, `system.nav` calls, the **Template Canvas**, or the **Template Repeater** (see the Containers section below) — so the same screen layout (e.g. one row per piece of equipment) doesn't have to be rebuilt by hand for every instance.

**The property model.** Every component exposes a fixed set of *properties* (Background Color, Font, Value, etc.), shown in the Designer's Property Editor and listed per-component below. Each property has:
- a **display name** (what you see in the Property Editor, e.g. "Foreground Color"),
- a **scripting name**, the dotted attribute used in Python/Jython (e.g. `.foreground`), always accessed off the component reference (`event.source.foreground`, `self.value`, etc.),
- a **type** (String, int, boolean, Color, Font, Border, Dataset, QualityCode, Date, …), and
- a **category** (Common, Appearance, Behavior, Layout, Data, …) that groups it in the Property Editor.

A property is either **static** (a fixed value typed into the Property Editor, with no live data behind it) or **bound**. A bound property's value comes from outside the component and is recalculated automatically as its source changes; bound properties are marked with a small chain-link icon in the Designer. Almost every property can be bound, and most components additionally expose read-only, binding-only properties for internal state (e.g. `Quality`, `Selected Row`, `Properties Loading`) that report on the component itself rather than configuring it.

**Property bindings.** Vision supports five kinds of binding, chosen from the binding-type dropdown in the Property Editor:
- **Tag** — binds directly to a Tag's value (optionally its quality or timestamp), polling or subscribing depending on the Tag provider.
- **Indirect Tag** — builds the Tag path from other component/window properties using `{}` placeholders, so the same binding can point at a different Tag depending on runtime context (e.g. per-equipment screens driven by a template parameter).
- **Expression** — a formula written in Ignition's expression language, referencing other bindings, Tags, or values through expression functions; recalculates whenever an input changes.
- **SQL Query** — runs a parameterized SQL query against a configured database connection and binds the result (scalar, one-column, or full Dataset) to the property; can be polled or run once.
- **Property** — binds to another property on the same window, a different component, or a client/session/global property, letting values propagate between components without scripting.

Bindings marked *bidirectional* (tag and some property bindings) also write back to their source when the user changes the value at runtime, e.g. typing into a Numeric Text Field bound bidirectionally to a Tag.

**Event handlers vs. extension functions.** These are the two ways a component runs Jython code, and they're not interchangeable:
- **Event handlers** are attached in the Property Editor's Event Handlers panel (or via right-click → Scripting) and fire on generic UI/lifecycle events that (almost) every component shares — `mouseClicked`, `mousePressed`, `actionPerformed`, `propertyChange`, `focusGained`/`focusLost`, `keyPressed`, and, for windows specifically, `internalFrameOpened`/`internalFrameActivated`/`internalFrameClosing`/`internalFrameDeactivated`/`internalFrameClosed` plus the Vision-specific `visionWindowOpened` and `visionWindowClosed`. The full generic event catalog lives on the Component Events page (linked from every component's Scripting section) rather than being repeated per component here.
- **Extension functions** (marked `[ext]` throughout this reference) are pre-defined callback stubs specific to one component — e.g. the Power Table's `configureCell`/`onCellEdited`, the Alarm Status Table's `onAcknowledge`, the Admin components' `onSaveUser`/`onCreateRole`, or a chart's `configureChart`. They're reached via the component's right-click **Scripting** menu, are disabled (no-op) until you add code, and exist specifically so the component can ask "what should happen here?" at a well-defined point in its own logic, with a fixed function signature and, often, an expected return value (a color, a boolean, a dict of overrides) that the component then acts on.

**The component scripting object model.** At runtime, every component is a live Python-accessible object: `self` inside its own event handlers/extension functions, or `event.source` inside a fired event, or the object returned by `system.gui.getWindow(path).getRootContainer().getComponent("Name")`. Reading `someComponent.someProperty` gets a property's current value using its scripting name; setting it (where not read-only) triggers the same recalculation a binding change would. Beyond properties, most components also expose **component functions** (called as methods, e.g. `table.sortByColumn("Name")`, `easyChart.exportExcel(path)`, `powerTable.getSelectedRows()`) which are listed per-component below alongside the extension functions. Objects returned by many of these functions and by `system.*` scripting calls more broadly — Datasets/PyDatasets, QualityCode, AlarmQueryResult, and similar — are documented centrally on the **Scripting Object Reference** page rather than per component.

**Layout: anchored vs. relative.** Containers position their children one of two ways:
- **Anchored (absolute) layout** — the default for a plain Container/Root Container — places each component at a fixed `x, y, width, height`, with optional anchor points (left/right/top/bottom) that determine how it moves or stretches when its parent container is resized. This is the classic Vision approach: pixel-precise, but layouts don't reflow gracefully.
- **Relative layout**, enabled per-container, instead positions children by percentage of the container's current size, so the whole screen scales proportionally as the window is resized — closer to a fluid layout, at the cost of exact pixel control.
Template Canvas and Template Repeater add their own layout behavior on top of this (canvas-style placement, or flow/grid repetition — see the Containers section) for arranging many template instances at once.

## Components by category

## Admin
### SFC Monitor
Admin — A component to monitor SFC performance.

**Properties**
- Border (Border, .border) — The border surrounding this component. Options are No border, Etche...
- Instance ID (String, .instanceId) — The UUID of the sequential function chart to monitor.
- Instance List Visible (boolean, .instanceListVisible) — Shows or hides the list of SFC instances on the left.
- Legend Visible (boolean, .legendVisible) — Shows or hides the step and transition state legend.
- Name (String, .name) — The name of this component.
- Scope Dataset (Dataset, .scopeDataset) — Dataset containing the variables in chart scope.
- Scope Table Visible (boolean, .scopeTableVisible) — Shows or hides the chart scope inspection table.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Zoom (float, .zoom) — The zoom multiplier to display the chart's status at.

### Roster Management
Admin — The user management panel provides a built-in way to edit rosters from a client.

**Properties**
- Border (Border, .border) — The border surrounding this component. Options are No border, Etche...
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — The data quality code for any Tag bindings on this component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Table Color (Color, .tableBackground) — Changes the background color of the table rows. When a row is selec...
- Table Header Color (Color, .tableHeaderBackground) — Changes the background color of the table headers.
- Table Header Text Color (Color, .tableHeaderForeground) — Changes the text color of the table headers.
- Table Text Color (Color, .tableForeground) — Changes the text color of the table rows. When a row is selected, i...
- User Source (String, .addFromUserSource) — The user source to manage users in. If blank, uses the project's de...
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Window Color (Color, .windowBackground) — Changes the background color of the window.
- Window Header Color (Color, .windowHeaderBackground) — Changes the background color of the window header.
- Window Header Save Button Background (Color, .windowHeaderSaveButtonBackground) — Changes the background color of the window header save button.
- Window Header Save Button Text Color (Color, .windowHeaderSaveButtonForeground) — Changes the text color of the window header save button.
- Window Header Text Color (Color, .windowHeaderForeground) — Changes the window header text color.
- Window Text Color (Color, .windowForeground) — Changes the window header text color.

**Scripting / extension functions**
- [ext] filterRoster — Called for each roster loaded into the management table. Return false to hide this roster from the table.
- [ext] filterAvailableUser — Called for each user in a user source to be shown as an available user for the roster currently being edited.
- [ext] onSaveRoster — Called when the save button is pressed when editing a roster. Runs in a background thread.
- [ext] onCreateRoster — Called when the add button is pressed. Runs in a background thread.
- [ext] onDeleteRoster — Called when the delete button is pressed. Runs in a background thread.

**Notes**
- The Alarm Notification module is required in order to use the Roster Management component.

### Schedule Management
Admin — This component allows for management of schedules.

**Properties**
- Border (Border, .border) — The border surrounding this component. Options are No border, Etche...
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — The data quality code for any Tag bindings on this component.
- Schedule Available Color (Color, .schedulePreviewAvailableColor) — Changes the color of the available times in the schedule.
- Schedule Available Text Color (Color, .eventForeground) — Changes the text color of events on the schedule preview.
- Styles (Dataset, .styles) — Contains the component's styles.
- Table Color (Color, .tableBackground) — Changes the background color of the tables, User Roles and Role Mem...
- Table Header Color (Color, .tableHeaderBackground) — Changes the background color of the table headers.
- Table Header Text Color (Color, .tableHeaderTextColor) — Changes the text color of the table headers.
- Table Text Color (Color, .tableForeground) — Changes the text color of the tables. When a row is selected...
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is ...
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Window Color (Color, .windowBackground) — Changes the window background color.
- Window Header Color (Color, .windowHeaderBackground) — Changes the window header background color.
- Window Header Save Button Background Color (Color, .windowHeaderSaveButtonBackground) — Changes the window header save button background color.
- Window Header Save Button Text Color (Color, .windowHeaderSaveButtonForeground) — Changes the window header save button text color.
- Window Header Text Color (Color, .windowHeaderForeground) — Changes the window header text color.
- Window Text Color (Color, .windowForeground) — Changes the text color of the window.

**Scripting / extension functions**
- [ext] filterSchedule — Called for each schedule loaded into the management table. Return false to hide it.
- [ext] filterHoliday — Called for each holiday loaded into the management table. Return false to hide it.
- [ext] onCreateSchedule — Called when the add button is pressed when adding a schedule. Runs in a background thread.
- [ext] onDeleteSchedule — Called when the delete button is pressed for one or more schedules. Runs in a background thread.
- [ext] onSaveSchedule — Called when the save button is pressed when adding or editing a schedule.
- [ext] onCreateHoliday — Called when the add button is pressed when adding a holiday.
- [ext] onDeleteHoliday — Called when the delete button is pressed for one or more holidays.
- [ext] onSaveHoliday — Called when the save button is pressed when adding or editing a holiday.

**Notes**
- Making changes to users from a client with this component requires the User Management permissions.

### User Management
Admin — The User Management panel provides a built-in way to edit users and roles from a client.

**Properties**
- Border (Border, .border) — The border surrounding this component. Options are No border, Etche...
- Contact Info Editing Enabled (boolean, .allowContactInfoEditing) — If true, a user's contact info will be editable.
- Editing Schedule Available Color (Color, .schedulePreviewAvailableColor) — Changes the color of the available times in the schedule.
- Editing Schedule Available Text Color (Color, .eventForeground) — Changes the text color of events on the schedule preview.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of the text on this component.
- Mode (int, .mode) — Affects what mode the user management component runs in (Manage Users, Edit User, etc.).
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — The data quality code for any Tag bindings on this component.
- Role Assigning Enabled (boolean, .allowRoleAssigning) — If true, a user's roles will be editable.
- Role Management Enabled (boolean, .allowRoleManagement) — If true, role management is available.
- Row Height (int, .rowHeight) — Alter the size of the rows in the component's tables.
- Schedule Adjustments Enabled (boolean, .allowScheduleModifications) — If true, a user's schedule adjustments will be editable.
- Show Contact Info Column (boolean, .columnContactInfo) — Controls whether the user table shows the contact info column.
- Show Name Column (boolean, .columnName) — Controls whether the user table shows the name column.
- Show Roles Column (boolean, .columnRoles) — Controls whether the user table shows the roles column.
- Show Schedule Column (boolean, .columnSchedule) — Controls whether the user table shows the schedule column.
- Show Username Column (boolean, .columnUsername) — Controls whether the user table shows the username column.
- Styles (Dataset, .styles) — Contains the component's styles.
- Table Color (Color, .tableBackground) — Changes the background color of the tables.
- Table Header Color (Color, .tableHeaderBackground) — Changes the background color of the table headers.
- Table Header Text Color (Color, .tableHeaderTextColor) — Changes the text color of the table headers.
- Table Text Color (Color, .tableForeground) — Changes the text color of the tables.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- User Source (String, .userProfile) — The user source to manage users in. If blank, uses the project's default.
- Username (String, .username) — The name of the user being edited. Read-only except when mode is Edit.
- Username Editing Enabled (boolean, .allowUsernameEditing) — If true, usernames will be editable.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Window Color (Color, .windowBackground) — Changes the window background color.
- Window Header Color (Color, .windowHeaderBackground) — Changes the window header background color.
- Window Header Save Button Background Color (Color, .windowHeaderSaveButtonBackground) — Changes the window header save button background color.
- Window Header Save Button Text Color (Color, .windowHeaderSaveButtonForeground) — Changes the window header save button text color.
- Window Header Text Color (Color, .windowHeaderForeground) — Changes the window header text color.
- Window Text Color (Color, .windowForeground) — Changes the text color of the window.

**Scripting / extension functions**
- [ext] filterUser — Called for each user loaded into the management table. Return false to hide it.
- [ext] filterRole — Called for each role loaded into the management table. Return false to hide it.
- [ext] filterSchedule — Called for each schedule loaded into the schedule dropdown in the edit user panel.
- [ext] onCreateUser — Called when the add button is pressed in the users table.
- [ext] onDeleteUser — Called when the delete button is pressed in the users table.
- [ext] onSaveUser — Called when the save button is pressed when adding or editing a user.
- [ext] onCreateRole — Called when the add button is pressed in the roles table.
- [ext] onDeleteRole — Called when the delete button is pressed in the roles table.
- [ext] onSaveRole — Called when the save button is pressed when adding or editing a role.

**Notes**
- Be careful to only expose this component to users who should have the privileges to alter other users; access should be restricted via the "Manage Users" permission.
## Alarming
### Alarm Journal Table
Alarming — The alarm journal table provides a built-in view to explore alarm history that has been stored in an alarm journal.

**Properties**
- Acked Events (boolean, .includeAckedEvents) — Show acked events.
- Active Events (boolean, .includeActiveEvents) — Show active events.
- Border (Border, .border) — The border surrounding this component.
- Cleared Events (boolean, .includeClearedEvents) — Show cleared events.
- Date Format (String, .dateFormat) — A date format pattern used to format dates in the table.
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.
- Disabled Events (boolean, .includeDisabledEvents) — If enabled, shows events created by alarms being disabled.
- Display Path Filter (String, .displayPathFilter) — Filter alarms by alarm display path, falling back to source path.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Enabled Events (boolean, .includeEnabledEvents) — If enabled, shows events created by alarms being enabled.
- End Date (Date, .endDate) — The ending date for the displayed history range.
- Is Filtered (boolean, .isFiltered) — True if the results are filtered. (Read-only)
- Journal Name (String, .journalName) — The name of the alarm journal to query.
- Max Priority (int, .maximumPriority) — The maximum priority to display.
- Min Priority (int, .minimumPriority) — The minimum priority to display.
- Name (String, .name) — The name of this component.
- Notes Area Border (Border, .notesAreaBorder) — The border surrounding the notes area.
- Notes Area Font (Font, .notesAreaFont) — The font for the notes area.
- Notes Area Location (int, .notesAreaLocation) — The location of the notes display area.
- Notes Area Size (int, .notesAreaSize) — The size of the notes area, in pixels.
- Number Format (String, .numberFormat) — A number format string to control the format of the value column.
- Order by Ascending (boolean, .orderByEventTimeAsc) — Sorts alarms by event time ascending/descending.
- Quality (QualityCode, .quality) — The data quality code for any Tag bindings on this component.
- Read Timeout (int, .readTimeout) — The timeout, in ms, for running the alarm history query.
- Row Height (int, .rowHeight) — The height, in pixels, for each row of the table.
- Row Styles (Dataset, .rowStyles) — A dataset containing the different styles configured for different states.
- Search String (String, .searchString) — Filter alarms by searching for a string in source/display path.
- Selected Alarms (Dataset, .selectedAlarms) — A dataset containing each selected alarm. (Read-only)
- Selection Color (Color, .selectionColor) — The color of the selection border.
- Selection Thickness (int, .selectionThickness) — The size of the selection border.
- Show Table Header (boolean, .showTableHeader) — Toggles visibility of the table's header.
- Source Filter (String, .sourceFilter) — Filter alarms by alarm source path; multiple paths comma-separated.
- Start Date (Date, .startDate) — The starting date for the displayed history range.
- System Events (boolean, .includeSystemEvents) — Show system events such as startup and shutdown.
- Table Background (Color, .tableBackground) — The background of the alarm table.
- Table Font (Font, .font) — The font for the Alarm Journal's rows.
- Table Header Font (Font, .tableHeaderFont) — The font for the table header rows.
- Table Header Alignment (int, .headerAlignment) — The alignment for each column in the table header.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .print(fitWidth, headerFormat, footerFormat, showDialog, landscape) — Paginates the table onto multiple pages for printing.
- .getAlarms() — Returns a dataset of the alarms currently displayed in the table.
- [ext] createPopupMenu — Returns a popup menu displayed on right-click in the table.
- [ext] filterAlarm — Called for each event loaded into the table. Return false to hide it.
- [ext] onDoubleClicked — Called when an alarm is double-clicked, for custom functionality.

### Alarm Status Table
Alarming — The alarm status table displays the current state of the alarm system: active, unacknowledged, cleared, and acknowledged alarms. By default it shows all non-cleared/non-ack'ed alarms.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Chart Resolution (int, .chartResolution) — The resolution for the ad-hoc historian chart.
- Date Format (String, .dateFormat) — A date format pattern used to format dates in the table.
- Data Quality (int, .dataQuality) — The data quality code for any tag bindings on this component.
- Display Path Filter (String, .displayPathFilter) — Filter alarms by alarm display path, falling back to source path.
- Duration Format (int, .durationFormat) — Format style for fields like Active and Ack durations (Long/Short).
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Flash Interval (int, .flashInterval) — The time interval to use for flashing row styles.
- Journal Name (String, .alarmJournalName) — The name of the alarm journal to query for the chart's annotations.
- Marquee Mode (boolean, .marqueeMode) — Turn the table into a scrolling marquee.
- Min Priority (int, .minPriority) — The minimum priority alarm to be displayed by this table.
- Multi Select (boolean, .multiSelect) — Allow multi select; shows/hides the checkbox column.
- Name (String, .name) — The name of this component.
- Notes Area Border (Border, .notesAreaBorder) — The border surrounding the notes area.
- Notes Area Font (Font, .notesAreaFont) — The font for the notes area.
- Notes Area Location (int, .notesAreaLocation) — The location of the notes display area.
- Notes Area Size (int, .notesAreaSize) — The size of the notes area, in pixels.
- Number Format (String, .numberFormat) — A number format string to control the format of the value column.
- Provider Filter (String, .providerFilter) — Filter alarms by Tag Provider; multiple providers comma-separated.
- Quality (QualityCode, .quality) — The data quality code for any tag bindings on this component.
- Refresh Rate (long, .refreshRate) — The rate at which this table polls changes to the alarm status.
- Row Height (int, .rowHeight) — The height, in pixels, for each row of the table.
- Row Styles (Dataset, .rowStyles) — A dataset containing the different styles configured for different states.
- Scroll Delay (int, .scrollDelay) — The time in ms to wait between each step in a scroll.
- Selected Alarms (Dataset, .selectedAlarms) — A dataset containing each selected alarm. (Read-only)
- Selection Color (Color, .selectionColor) — The color of the selection border.
- Selection Thickness (int, .selectionThickness) — The size of the selection border.
- Shelving Times (Dataset, .shelvingTimes) — Holds the suggested times when shelving an alarm.
- Show Ack Button (boolean, .showAck) — Show the acknowledge button on the footer panel.
- Show Active and Acked (boolean, .activeAndAcked) — Show alarms that are active and acknowledged.
- Show Active and Unacked (boolean, .activeAndUnacked) — Show alarms that are active and unacknowledged.
- Show Chart Button (boolean, .showChart) — Show the chart button on the footer panel.
- Show Clear and Acked (boolean, .clearAndAcked) — Show alarms that are cleared and acknowledged.
- Show Clear and Unacked (boolean, .clearAndUnacked) — Show alarms that are cleared and unacknowledged.
- Show Details Button (boolean, .showDetails) — Show the view details button on the footer panel.
- Show Footer (boolean, .showFooterPanel) — Show a footer with acknowledge and shelf functions.
- Show Header Popup (boolean, .showTableHeaderPopup) — Toggles the table header's built-in column selection popup.
- Show Manage Shelf Button (boolean, .showManageShelf) — Show the manage shelf button on the footer panel.
- Show Shelve Button (boolean, .showShelve) — Show the shelve button on the footer panel.
- Show Table Header (boolean, .showTableHeader) — Toggles visibility of the table's header.
- Sort Oldest First (boolean, .sortOldestFirst) — Sort times by oldest first.
- Sort Order (int, .sortOrder) — The default sort order for alarms in the status table.
- Source Filter (String, .sourceFilter) — Filter alarms by alarm source path.
- Stay Delay (int, .stayDelay) — The time (ms) to wait between scrolls.
- Table Background (Color, .tableBackground) — The background of the alarm table.
- Table Font (Font, .font) — The font for the table rows.
- Table Header Alignment (int, .headerAlignment) — The alignment for each column in the table header.
- Table Header Font (Font, .tableHeaderFont) — The font for the table header.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .print(fitWidth, headerFormat, footerFormat, showDialog, landscape) — Paginates the table onto multiple pages for printing.
- .getAlarms() — Returns a dataset of the alarms currently displayed in the table.
- [ext] createPopupMenu — Returns a popup menu displayed on right-click in the table.
- [ext] filterAlarm — Called for each event loaded into the table. Return false to hide it.
- [ext] isAcknowledgeEnabled — Returns whether the selected alarm can be acknowledged.
- [ext] isShelvedEnabled — Returns whether the selected alarm can be shelved.
- [ext] onDoubleClicked — Called when an alarm is double-clicked, for custom functionality.
- [ext] onAcknowledge — Called before the Acknowledge button's ack happens; return False to cancel.
- [ext] onShelve — Called before the Shelving panel's Apply happens; return False to cancel.

**Notes**
- Selection supports individual alarm, multiple alarms, or Select All in the header; filter settings live in the Property Editor if displayed alarms don't match expected associated data.
## Buttons
_The following components give you push-button options for displaying and writing values._

### Button
Buttons — The Button component can be configured to open and/or close windows, write to tags, and run scripts when triggered by an event handler.

**Properties**
- Background Color (Color, .buttonBG) — The background color of the button.
- Border (Border, .border) — The border surrounding this component (unaffected by rotation).
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Default Button (boolean, .defaultBtn) — If true, activated when the user presses Enter on the window.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Area? (boolean, .contentAreaFilled) — Controls whether the button's internal area is filled.
- Focusable (boolean, .focusable) — If false, the button can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to image.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between icon and text.
- Image Path (String, .path) — The relative path of the image.
- Margin (Insets, .margin) — The space between a button's text and its borders.
- Mnemonic (String, .mnemonicChar) — A letter that activates the button via ALT-mnemonic.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to image.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any tag bindings on this component.
- Opaque (boolean, .opaque) — If true, button will be opaque. Default is false.

**Scripting / extension functions**
- .doClick() — Virtually "clicks" the button; runs its actionPerformed event handler.

### Check Box
Buttons — A CheckBox represents a bit — on (selected) or off (not selected). Functionally equivalent to the Toggle Button component.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Background (boolean, .fillBackground) — If true, the label's background color is drawn.
- Focusable (boolean, .focusable) — If false, can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Margin (Insets, .margin) — Internal margin padding the contents.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Selected (boolean, .selected) — The current state of the checkbox.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — The text displayed on the checkbox.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Momentary Button
Buttons — Sets a value for either a fixed amount of time, or however long the button remains held down, whichever is longer.

**Properties**
- Background Color (Color, .buttonBG) — The background color of the button.
- Border (Border, .border) — The border surrounding this component.
- Control Value (int, .controlValue) — Bind to the tag you want to control.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Area? (boolean, .contentAreaFilled) — Controls whether the button's internal area is filled.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to image.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between icon and text.
- Image Path (String, .path) — The relative path of the image.
- Indicator Value (int, .indicatorValue) — Bind to the tag that indicates the current state of the control.
- Indicator Width (int, .indicatorWidth) — Width of the indication border showing the indicator state.
- Max Hold Time (int, .maxOnTime) — Maximum time to keep the control value at the "On Value."
- Min Hold Time (int, .onTime) — Minimum time to keep the control value at the "On Value."
- Mnemonic (String, .mnemonicChar) — A letter that activates the button via ALT-mnemonic.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Off Color (Color, .offColor) — Color of the indicator border when the indicator value is off.
- Off Value (int, .offValue) — Value written to the Control Value on mouse-up.
- On Color (Color, .onColor) — Color of the indicator border when the indicator value is on.
- On Value (int, .onValue) — Value written to the Control Value on mouse-down.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover? (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to image.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Multi-State Button
Buttons — Two or more buttons arranged in a column, row, or grid.

**Properties**
- Confirm Text (string, .confirmText) — Message shown in a confirmation box if Confirm? is true.
- Confirm? (boolean, .confirm) — If true, a confirmation box will be shown.
- Control Value (int, .controlValue) — Value that controls the state; typically bound to the same tag as Indicator Value.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Display Style (int, .displayStyle) — The display style (rows or columns) for this N-state button.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Focusable (boolean, .focusableEnabled) — If false, users cannot interact via the keyboard.
- Font (Font, .font) — Font of text on this component.
- Grid Cols (int, .gridCols) — Number of columns if Display Style is "Grid."
- Grid Rows (int, .gridRows) — Number of rows if Display Style is "Grid."
- Horizontal Gap (int, .hGap) — Horizontal spacing between buttons.
- Indicator Value (int, .indicatorValue) — Value that indicates the current state.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any tag bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- States (Dataset, .states) — A Dataset storing the information for the different states.
- Vertical Gap (int, .vGap) — Vertical spacing between buttons.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any tag bindings on this component.

### One-Shot Button
Buttons — Writes a value once and waits for it to be reset by the PLC before it's available again — good for telling a PLC to do something.

**Properties**
- Background Color (Color, .buttonBG) — The background color of the button.
- Border (Border, .border) — The border surrounding this component.
- Confirm Text (String, .confirmText) — Message asked of the user if confirmation is turned on.
- Confirm? (boolean, .confirm) — If true, a confirmation box will be shown.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disable While Writing (boolean, .disableWhileWriting) — If true, the button is disabled while it is writing.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Area? (boolean, .contentAreaFilled) — Controls whether the button's internal area is filled.
- Focusable (boolean, .focusable) — If false, can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to image.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between icon and text.
- Idle Text (String, .normalText) — Text of the button while its value is not being written.
- Image Path (String, .path) — The relative path of the image.
- Margin (Insets, .margin) — The space between a button's text and its borders.
- Mnemonic (String, .mnemonicChar) — A letter that activates the button via ALT-mnemonic.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Set Value (int, .setValue) — The value to set the control value to when the button is pushed.
- Styles (Dataset, .styles) — Contains the component's styles.
- Value (int, .value) — Current value; should be bound bi-directionally to a tag.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to image.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Writing Text (String, .writePendingText) — Text of the button while its value is being written.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.
- Opaque (boolean, .opaque) — If true, button will be opaque. Default is false.

**Notes**
- Considered safer than the Momentary Button because it receives positive feedback from the PLC that the signal was received, avoiding stuck/lost writes.

### Radio Button
Buttons — Similar to CheckBox, except all radio buttons in the same Container (including the Root Container) are automatically mutually exclusive.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Background (boolean, .fillBackground) — If true, the label's background color is drawn.
- Focusable (boolean, .focusable) — If false, can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Margin (Insets, .margin) — Internal margin padding the contents.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Selected (boolean, .selected) — The current state of the Radio Button.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### 2 State Toggle
Buttons — Similar to the basic Toggle Button but tuned for realistic controls environments; toggles a value between two states (On/Off, Stop/Run, etc.).

**Properties**
- Background Color (Color, .buttonBG) — The background color of the button.
- Border (Border, .border) — The border surrounding this component.
- Confirm Text (String, .confirmText) — Message shown in the confirmation box if Confirm? is true.
- Confirm? (boolean, .confirm) — If true, a confirmation box will be shown.
- Control Value (int, .controlValue) — Bind to the tag that controls the state.
- Current State (int, .state) — Read-only property showing the button's current state (0 or 1).
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Area? (boolean, .contentAreaFilled) — Controls whether the button's internal area is filled.
- Focusable (boolean, .focusable) — If false, can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Horizontal alignment of the button's contents.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to image.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between icon and text.
- Image Path (String, .path) — The relative path of the image.
- Indicator Value (int, .indicatorValue) — Bind to the tag that indicates the current state.
- Margin (Insets, .margin) — The space between a button's text and its borders.
- Mnemonic (String, .mnemonicChar) — A letter that activates the button via ALT-mnemonic.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- State 1 Value (int, .state1Value) — Value written to controlValue when the button is pressed to state 1.
- State 2 Value (int, .state2Value) — Value written to controlValue when the button is pressed to state 2.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Vertical Alignment (int, .verticalAlignment) — Vertical alignment of the button's contents.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to image.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.
- Opaque (boolean, .opaque) — If true, button will be opaque. Default is false.

### Tab Strip
Buttons — A single-selection multiple-choice component, typically used to select between windows or containers to display.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Intertab Space (int, .interTabSpace) — Amount of space between each tab.
- Name (String, .name) — The name of this component.
- Navigation Mode (int, .navigationMode) — Disabled/Swap/etc. behavior when a tab is pressed.
- Orientation (int, .orientation) — Orientation of the tab strip.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Renderer (int, .renderer) — The renderer to use when rendering tabs.
- Rounding Radius (int, .roundingRadius) — Rounding radius for the tab corners.
- Selected Tab (String, .selectedTab) — Name of the selected tab (also the window name it may show).
- Separator Color (Color, .separatorColor) — Color of the line drawn across the bottom and around each tab.
- Separator Thickness (float, .separatorThickness) — Thickness of the line drawn across the bottom/around each tab.
- Size Mode (int, .sizeMode) — Sizing mode tabs use when deciding their size (Automatic, etc.).
- Styles (Dataset, .styles) — Contains the component's styles.
- Tab Data (Dataset, .tabData) — Tab data to be displayed.
- Text Alignment (int, .textAlignment) — Alignment of the tab text.
- Text Offset (int) — Padding on the left/right side of a tab's text, depending on alignment.
- Text Padding (int, .textPadding) — Padding on each side of the text inside a tab.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Toggle Button
Buttons — Represents a bit: on (selected) or off (not selected).

**Properties**
- Background Color (Color, .buttonBG) — The background color of the button.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Area? (boolean, .contentAreaFilled) — Controls whether the button's internal area is filled.
- Focusable (boolean, .focusable) — If false, can't be tabbed to or interacted with via keyboard.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Image Path (String, .path) — The relative path of the image.
- Label (String, .text) — Text displayed on this button.
- Margin (Insets, .margin) — The space between a button's text and its borders.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — Set false if you want the button to be completely opaque (sic, per docs).
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rollover? (boolean, .rolloverEnabled) — If true, the button indicates mouse hover.
- Selected (boolean, .selected) — State of this toggle button.
- Selected Image Path (String, .selectedPath) — Path of the image shown when this component is selected.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Notes**
- For controls screens the 2 State Toggle is usually preferred over the plain Toggle Button.
## Calendar
### Calendar
Calendar — Displays a calendar and time input directly embedded in your window.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Date (immediate) (Date, .date) — The date as it is selected right now.
- Date (latched) (Date, .latchedDate) — The date the last time "OK" was pressed.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Format String (String, .format) — Date formatting pattern used to format the string versions of the date.
- Formatted Date (String, .formattedDate) — The date property, as formatted by the format string.
- Formatted Latched Date (String, .formattedLatchedDate) — The latched date property, formatted by the format string.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Border (Border, .selectedBorder) — The border for the selected day indicator.
- Show OK Button (boolean, .showOkButton) — Turn off to hide the OK button; latched date won't update without it.
- Show Time (boolean, .showTime) — Turn off to hide the time panel.
- Styles (Dataset, .styles) — Contains the component's styles.
- Time Display Format (int, .timeDisplayFormat) — Format for displaying time in the panel.
- Time Style (int, .timeStyle) — How this calendar should treat the time portion of the date.
- Title Background (Color, .titleBackground) — The background of the title bar.
- Today Background (Color, .todayBackground) — Background color for the today indicator.
- Today Foreground (Color, .todayForeground) — Foreground color for the today indicator.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Weekend Background (Color, .weekendBackground) — Background color for the weekend indicators.
- Weekend Foreground (Color, .weekendForeground) — Foreground color for the weekend indicators.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Date Range
Calendar — Provides an intuitive, drag-and-drop way to select a contiguous range of time.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Box Fill (Color, .boxFill) — The fill color for the selection box.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data Density (Dataset, .densityData) — A dataset used to calculate a histogram of data density.
- Date Style (int, .dateStyle) — The style to display dates in (international support).
- Editor Background (Color, .editorBackground) — Background color of the textual date range editor portion.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- End Date (Date, .endDate) — The ending date of the currently selected range.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- High Density Color (Color, .highDensityColor) — Color used to indicate high data density.
- Max Selection (String, .maxSelectionSize) — Maximum size of the selected date range.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Outer Range End (Date, .outerRangeEndDate) — The ending date of the available outer range.
- Outer Range Start (Date, .outerRangeStartDate) — The starting date of the available outer range.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selection Highlight (Color, .selectionHighlight) — Focus highlight color for the selection box.
- Start Date (Date, .startDate) — The starting date of the currently selected range.
- Startup Mode (int, .startupMode) — Whether this date range auto-assigns itself a range at startup.
- Startup Range (String, .startupRange) — Starting range of time if Startup Mode is Automatic.
- Startup Selection (String, .startupSelection) — Starting selected range if Startup Mode is Automatic.
- Styles (Dataset, .styles) — Contains the component's styles.
- Tick Density (float, .tickDensity) — Multiplied by width to determine the current ideal tick spacing.
- Time Style (int, .timeStyle) — Style to display times of day (international support).
- Today Color (Color, .todayIndicatorColor) — Color of the "Today Arrow" indicator.
- Track Margin (int, .trackMargin) — Room on either side of the slider track.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- .setRange(start, end) — Sets the selected range; the outer range moves if needed.
- .setOuterRange(start, end) — Sets the outer range; the selected range moves if needed.

**Notes**
- Start/End and Outer Start/End dates are ignored when the window opens unless Startup Mode is set to "None."
- Timestamps must be ordered by date (ascending) to display correctly.

### Day View
Calendar — Displays a timeline for a single day, similar to a personal planner/organizer.

**Properties**
- 24 Hour Format (boolean, .twentyFourHour) — Whether to show 24 hour or 12 hour format.
- Border (Border, .border) — The border surrounding this component.
- Calendar Background Color (Color, .calendarBackground) — Color of the calendar's background.
- Calendar events (Dataset, .events) — Contains the calendar events.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Day (int, .day) — Set the calendar's day.
- Day Outline Color (Color, .boxOutline) — The color of the day's outline.
- Event Font (Font, .eventFont) — The font for all calendar events.
- Grid marks (int, .gridMarks) — Set the amount of grid lines.
- Hour Font (Font, .hourFont) — The font for the hour of the day.
- Hour Foreground Color (Color, .hourForeground) — Foreground color for hours in a day.
- Hover Background Color (Color, .hoverBackground) — Background color of the hovered time.
- Hovered Event (int, .hoveredEvent) — The calendar's hovered event.
- Hovered Time (String, .hoveredTime) — The calendar's hovered time.
- Month (int, .month) — Set the calendar's month.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Non-Working Hours Background Color (Color, .nonWorkingHourBackground) — Background color for non-working hours.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Event (int, .selectedEvent) — The calendar's selected event.
- Styles (Dataset, .styles) — Contains the component's styles.
- Today's Background Color (Color, .todayBackground) — Color of today's background.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Week Day Background Color (Color, .weekDaysBackground) — Color of the week day's background.
- Week Day Font (Font, .weekdayFont) — Font of the week day's text.
- Week Day Foreground Color (Color, .weekDaysForeground) — Color of the week day's text.
- Working End Hour (int, .workingEndHour) — The end hour of a working day.
- Working Start Hour (int, .workingStartHour) — The start hour of a working day.
- Year (int, .year) — Set the calendar's year.
- Zoom (boolean, .autoZoom) — Zooms into the specified zoom time range.
- Zoomed End Hour (int, .autoZoomEndHour) — The end hour zoomed in.
- Zoomed Start Hour (int, .autoZoomStartHour) — The start hour zoomed in.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Month View
Calendar — Displays events for an entire month.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Calendar Background Color (Color, .calendarBackground) — Color of the calendar's background.
- Calendar events (Dataset, .events) — Contains the calendar events.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Day Font (Font, .dayFont) — Font for the number representing the day of the month.
- Day Foreground Color (Color, .dayOfMonthForeground) — Foreground color for days in this month.
- Day Other Foreground Color (Color, .dayOfMonthOtherForeground) — Foreground color for days not in this month.
- Day Outline Color (Color, .boxOutline) — The color of the day's outline.
- Event Background Color (Color, .itemSelBackground) — Background color of the selected event.
- Event Display Mode (int, .displayMode) — How events are displayed (Standard/Highlight modes).
- Event Font (Font, .eventFont) — The font for all calendar events.
- Event Highlight Background (Color, .highlightBackground) — Background color of a day with events (highlight mode).
- Header Background Color (Color, .monthHeaderBackground) — Color of the header's background.
- Header Font (Font, .headerFont) — Font of the header's text.
- Header Foreground Color (Color, .monthHeaderForeground) — Color of the header's text.
- Hover Background Color (Color, .hoverBackground) — Background color of the hovered day.
- Hovered Day (String, .hoveredDay) — The calendar's hovered day.
- Month (int, .month) — Set the calendar's month.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Background Color (Color, .selectedBackground) — Color of the selected day's background.
- Selected Day (String, .selectedDay) — The calendar's selected day.
- Selected Event (int, .selectedEvent) — The calendar's selected event.
- Styles (Dataset, .styles) — Contains the component's styles.
- Today's Background Color (Color, .todayBackground) — Color of today's background.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Week Day Background Color (Color, .weekDaysBackground) — Color of the week day's background.
- Week Day Font (Font, .weekdayFont) — Font of the week day's text.
- Week Day Foreground Color (Color, .weekDaysForeground) — Color of the week day's text.
- Year (int, .year) — Set the calendar's year.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Popup Calendar
Calendar — A popular way to provide date/time choosing controls on a window.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Calendar Background (Color, .calendarBackground) — The background color for the popup calendar.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Date (Date, .date) — The date that this component represents.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Format String (String, .format) — Date formatting pattern used to display this date.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Border (Border, .selectedBorder) — The border for the selected day indicator.
- Show Navigation (boolean, .showNavigation) — Turn off to hide the year and month navigation controls.
- Show OK Button (boolean, .showOkButton) — Turn off to hide the OK button; latched date won't update without it.
- Show Time (boolean, .showTime) — Turn off to hide the time panel.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — The displayed text of the date (depends on the format string).
- Time Display Format (int, .timeDisplayFormat) — Format for displaying time in the panel.
- Time Style (int, .timeStyle) — How this calendar should treat the time portion of the date.
- Title Background (Color, .titleBackground) — The background of the title bar.
- Today Background (Color, .todayBackground) — Background color for the today indicator.
- Today Foreground (Color, .todayForeground) — Foreground color for the today indicator.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Weekend Background (Color, .weekendBackground) — Background color for the weekend indicators.
- Weekend Foreground (Color, .weekendForeground) — Foreground color for the weekend indicators.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Week View
Calendar — Displays a full week's worth of events on a calendar.

**Properties**
- 24 Hour Format (boolean, .twentyFourHour) — Whether to show 24 hour or 12 hour format.
- Border (Border, .border) — The border surrounding this component.
- Calendar Background Color (Color, .calendarBackground) — Color of the calendar's background.
- Calendar events (Dataset, .events) — Contains the calendar events.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Day (int, .day) — Set the calendar's day.
- Day Outline Color (Color, .boxOutline) — The color of the day's outline.
- Event Font (Font, .eventFont) — The font for all calendar events.
- Grid marks (int, .gridMarks) — Set the amount of grid lines.
- Hour Font (Font, .hourFont) — The font for the hour of the day.
- Hour Foreground Color (Color, .hourForeground) — Foreground color for hours in a day.
- Hover Background Color (Color, .hoverBackground) — Background color of the hovered day and time.
- Hovered Day (String, .hoveredDay) — The calendar's hovered day.
- Hovered Event (int, .hoveredEvent) — The calendar's hovered event.
- Hovered Time (String, .hoveredTime) — The calendar's hovered time.
- Month (int, .month) — Set the calendar's month.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Non-Working Hours Background Color (Color, .nonWorkingHourBackground) — Background color for non-working hours.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Background Color (Color, .selectedBackground) — Color of the selected day's background.
- Selected Day (String, .selectedDay) — The calendar's selected day.
- Selected Event (int, .selectedEvent) — The calendar's selected event.
- Show Event Time? (boolean, .showEventTime) — Whether to show the event time.
- Show Weekend? (boolean, .showWeekend) — Whether to show Saturday and Sunday.
- Styles (Dataset, .styles) — Contains the component's styles.
- Today's Background Color (Color, .todayBackground) — Color of today's background.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Week Day Background Color (Color, .weekDaysBackground) — Color of the week day's background.
- Week Day Font (Font, .weekdayFont) — Font of the week day's text.
- Week Day Foreground Color (Color, .weekDaysForeground) — Color of the week day's text.
- Working End Hour (int, .workingEndHour) — The end hour of a working day.
- Working Start Hour (int, .workingStartHour) — The start hour of a working day.
- Year (int, .year) — Set the calendar's year.
- Zoom (boolean, .autoZoom) — Zooms into the specified zoom time range.
- Zoomed End Hour (int, .autoZoomEndHour) — The end hour zoomed in.
- Zoomed Start Hour (int, .autoZoomStartHour) — The start hour zoomed in.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.
## Charts
### Bar Chart
Charts — An easy-to-use chart that provides a familiar bar representation of any numeric values.

**Properties**
- Bar Label Color (Color, .barLabelColor) — The color for the bar labels.
- Bar Label Font (Font, .barLabelFont) — The font for the bar labels.
- Bar Label Offset (double, .barLabelOffset) — The offset between the bar and the bar label.
- Border (Border, .border) — The border surrounding this component.
- Category Axis Label (String, .categoryLabel) — The label for the category axis.
- Category Axis Label Angle (int, .catAxisLabelPosition) — The angle for the value axis' labels.
- Category Axis Label Color (Color, .catAxisLabelColor) — The color for the category axis label.
- Category Axis Label Font (Font, .catAxisLabelFont) — The font for the category axis label.
- Category Axis Lower Margin (double, .catAxisLowerMargin) — Lower margin, as a percentage, of the category axis.
- Category Axis Tick Color (Color, .catAxisTickColor) — The color for the category axis' ticks.
- Category Axis Tick Font (Font, .catAxisTickFont) — The font for the category axis' ticks.
- Category Axis Upper Margin (double, .catAxisUpperMargin) — Upper margin, as a percentage, of the category axis.
- Category Margin (double, .categoryMargin) — Margin between categories as a fraction of the total space.
- Chart Title (String, .title) — Optional title at the top of the chart.
- Chart Type (int, .rendererType) — Controls how the bar chart is displayed.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data driving the chart.
- Extract Order (int, .extractOrder) — Whether the first row defines categories or the series.
- Foreground Transparency (float, .foregroundAlpha) — Transparency of the bars (useful for 3D bars).
- Gradient bars? (boolean, .gradient) — If true, bars are painted with a gradient 'shine'.
- Item Margin (double, .itemMargin) — Margin between bars in a category as a fraction.
- Labels? (boolean, .labels) — Always display labels?
- Legend Font (Font, .legendFont) — The font for the legend items.
- Legend? (boolean, .legend) — If true, show a legend for the chart.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Plot Background (Color, .plotBackground) — The background color for the plot.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Series Colors (Color[], .seriesColors) — Sequence of colors used for series in the bar chart.
- Shadows? (boolean, .shadows) — If true, bars have a drop-shadow beneath them.
- Title Font (Font, .titleFont) — The font for the chart's title.
- Tooltips? (boolean, .tooltips) — If true, show tooltips.
- Value Axis Auto-Range (boolean, .valAxisAutoRange) — If true, value axis range is determined automatically.
- Value Axis Label (String, .valueLabel) — The label for the value axis.
- Value Axis Label Color (Color, .valAxisLabelColor) — The color for the value axis label.
- Value Axis Label Font (Font, .valAxisLabelFont) — The font for the value axis label.
- Value Axis Lower Bound (double, .valAxisLowerBound) — Lower bound of the value axis (used only when auto-range is false).
- Value Axis Tick Color (Color, .valAxisTickColor) — The color for the value axis' ticks.
- Value Axis Tick Font (Font, .valAxisTickFont) — The font for the value axis' ticks.
- Value Axis Upper Bound (double, .valAxisUpperBound) — Upper bound of the value axis (used only when auto-range is false).
- Value Axis Upper Margin (double, .valAxisUpperMargin) — Upper margin, as a percentage, of the value axis.
- Vertical (boolean, .vertical) — Vertical (true) or horizontal orientation.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.
- [ext] getBarColor — Opportunity to override the color of each bar, e.g. based on value.

**Notes**
- If columns define categories and rows define series, set Extract Order to "By Column."
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).

### Box and Whisker Chart
Charts — Displays pertinent statistical information about sets of data.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Category Axis Title (String, .categoryAxisTitle) — A text label to display on the category axis.
- Chart Title (String, .title) — Optional title at the top of the chart.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data driving the chart.
- Fill Boxes? (boolean, .fillBoxes) — Fill the boxes with their color?
- Font (Font, .font) — Font of text on this component.
- Legend? (boolean, .legend) — Show a legend on the chart?
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Plot Background (Color, .plotBackground) — The background color for the plot.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Series Colors (Color[], .seriesColors) — Colors to paint each box in a series.
- Tooltips? (boolean, .tooltips) — Show tooltips on tasks?
- Value Axis Title (String, .valueAxisTitle) — A text label to display on the value axis.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).

### Chart
Charts — Also called the Classic Chart (vs. the Easy Chart); a flexible way to display timeseries or X-Y charts powered by any number of datasets.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Chart Orientation (int, .orientation) — The orientation of the domain axis of the chart.
- Chart Title (String, .title) — Optional title at the top of the chart.
- Chart Type (int, .chartType) — XY (Numeric X-axis) or Category (String X-axis).
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Extract Order (int, .extractOrder) — How category datasets should be interpreted.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Plot Background (Color, .plotBackground) — Background color for all plots, unless overridden.
- Properties Loading (int, .propertiesLoading) — Number of properties currently being loaded. (Read only.)
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Selected Datapoint (String, .selectedData) — The currently selected datapoint. (Read only.)
- Selected X Value (String, .selectedXValue) — The selected domain axis value for X-Trace/Mark modes. (Read only.)
- Selection Enabled? (boolean, .selectionEnabled) — If true, the user can select datapoints on the chart.
- Selection Highlight Color (Color, .selectionHighlightColor) — The color of the selection highlight.
- Selection Highlight Width (float, .selectionHighlightWidth) — The line width of the selection highlight.
- Show Legend? (boolean, .legend) — If true, a legend is shown for the series displayed.
- Show Popup? (boolean, .showPopup) — If true, a popup menu is shown on right-click.
- Show Tooltips? (boolean, .tooltips) — If true, tooltips showing point values are displayed.
- Subplot Mode (int, .subplotMode) — The axis subplots share if more than one subplot.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- getPlotProperties() — Retrieves the values of selected PlotProperty objects (background color, weight, etc.).
- getProperties() — Retrieves the value of custom properties added to the Chart.
- getSelectedData() — Returns the value of the selected chart entity as a string.
- getSelectedEntity() — Returns the selected chart entity directly.
- getSubplotMode() — Retrieves the subplot mode currently in use.
- getXAxes() — Returns a dictionary of the related X axis rendering properties.
- getYAxes() — Returns a dictionary of the related Y axis rendering properties.
- refreshChart() — Refreshes the dataset for the specified subplot and dataset.
- setDatasetEnabled() — Sets a dataset to be enabled or not enabled.
- setDatasetPlotNumber() — Sets a dataset's plot number.
- setDatasetXAxis() — Sets a dataset's X axis name.
- setDatasetYAxis() — Sets a dataset's Y axis name.
- setSubplotMode() — Sets the subplot mode used when there is more than one subplot.
- setXAxes() — Sets defined rendering properties using AxisConfig objects.
- setYAxes() — Sets defined rendering properties using AxisConfig objects.
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.
- [ext] getXTraceLabel — Opportunity to configure the x-trace label; return a string to override the default.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).
- Not all Renderer properties are available for each axis type; some customizer properties are axis-type-specific.

### Easy Chart
Charts — Used to make runtime-configurable time-series charts, with built-in tag/database pen management, date range controls, and user pen configuration.

**Properties**
- 3D X Offset (int, .xOffset3D) — Offset in the x direction for the '3D Line' pen style.
- 3D Y Offset (int, .yOffset3D) — Offset in the y direction for the '3D Line' pen style.
- Allow Color Changes (boolean, .allowColorChanges) — If true, pen colors can be set to different values.
- Allow Tag History Interpolation (boolean, tagHistoryAllowInterpolation) — Interpolates data when query mode is not raw.
- Auto Apply (boolean, .autoApply) — If true, user changes to pen visibility occur immediately.
- Auto Axis Positioning (boolean, .autoPositionAxes) — If true, axes alternate automatically between left and right.
- Auto Color List (Color[], .autoColorList) — Colors to use if auto pen coloring is enabled.
- Auto Pen Coloring (boolean, .autoColorPens) — If true, pens are assigned different colors automatically.
- Axes (Dataset, .axes) — Defines all axes that can be used by the pens.
- Axis Font (Font, .axisLabelFont) — The font for axis labels.
- Background Color (Color, .background) — The background color of the component.
- Bar Margin (double, .barMargin) — Margin to use for the 'Bar' pen style.
- Border (Border, .border) — The border surrounding this component.
- Box Fill (Color, .boxFill) — Historical-mode date range selection box fill color.
- Button Size (int, .utilityButtonSize) — The size of the utility button icons.
- Bypass Tag History Cache (boolean, .tagHistoryBypassCache) — If true, tag history queries don't use the client history cache.
- Calculated Pens (Dataset, .calcPens) — Defines the calculated pens for the chart.
- Chart Border (Border, .chartBorder) — The border for the chart itself.
- Chart Mode (int, .chartMode) — Manual, Historical, or Realtime mode.
- Chart Title (String, .title) — Optional title displayed above the chart.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- DB Pens (Dataset, .pens) — Defines all of the database pens for the chart.
- Date Editor Background (Color, .editorBackgroundColor) — The background color for the date editor.
- Date Editor Foreground (Color, .editorForegroundColor) — The foreground color for the date editor.
- Date Range (int, .dateRangeLocation) — Position of the date range control.
- Date Range Border (Border, .dateRangeBorder) — The border for the date range control, if visible.
- Date Style (int, .dateStyle) — Style to display dates in (international support).
- Digital Gap (double, .digitalGap) — Size of the gap to use between digital pens.
- Empty Group Name (String, .emptyGroupName) — Group name for pens not in a pen group.
- End Date (Date, .endDate) — Manual-mode end date for selecting pen data.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Gap Threshold (double, .gapThreshold) — Relative threshold used for determining continuity breaks.
- Gridline Color (Color, .gridlineColor) — The color of the gridlines.
- Gridline Dash Pattern (String, .gridlineDashPattern) — Comma-delimited numbers indicating the gridline stroke dash pattern.
- Gridline Width (float, .gridlineWidth) — The width (thickness) of the gridlines.
- Group Pens (boolean, .penGrouping) — If true, pens are grouped by their group name.
- High Density Color (Color, .highDensityColor) — Historical-mode: color used to indicate high data density.
- Horiz Gap (int, .hGap) — Horizontal spacing to use for the pen checkboxes.
- Ignore Bad Quality Data (boolean, tagHistoryIgnoreBadData) — If true, ignores bad quality data.
- Invert Time Axis (boolean, .invertTimeAxis) — If true, time axis increases right to left instead of left to right.
- Legend (int, .legend) — Where the legend appears, if any.
- Max Selection (String, .maxSelectionSize) — Historical-mode: maximum size of the selected date range.
- Maximize Plot (boolean, .currentlyMaximized) — If true, displays a maximized plot.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Outer Range End (Date, .outerRangeEnd) — Historical-mode: end date for the outer range.
- Outer Range Start (Date, .outerRangeStart) — Historical-mode: start date for the outer range.
- Pen Control Border (Border, .penBorder) — The border for the pen control panel, if visible.
- Pen Control Mode (int, .penControlMode) — Style in which the pen control panel alters the chart configuration.
- Pen Control? (boolean, .allowPenManipulation) — Controls whether end-users can turn pens on/off.
- Plot Background (Color, .plotBackground) — Background color for all plots, unless overridden.
- Plot Orientation (int, .plotOrientation) — The plot orientation for all plots.
- Plot Outline (Color, .plotOutlineColor) — The color to use for the plot outline.
- Poll Rate (int, .pollRate) — The rate (ms) at which this chart's queries poll.
- Properties Loading (int, .propertiesLoading) — Number of properties currently being loaded. (Read only.)
- Realtime Text (String, .rtLabel) — Realtime-mode: text to display on the realtime date range control.
- Selected X Value (String, .selectedXValue) — The selected domain axis value for X-Trace/Mark modes. (Read only.)
- Selection Highlight (Color, .selectionHighlight) — Historical-mode: focus highlight color for the selection box.
- Show Density (boolean, .showHistogram) — Historical-mode: shows a data density histogram.
- Show Loading (boolean, .showLoading) — If true, shows an animated indicator when data is loading.
- Show Maximize Button? (boolean, .showMaximize) — If true, shows a small maximize button next to the chart.
- Show Popup? (boolean, .showPopup) — If true, shows a popup menu on right-click.
- Show Print Button? (boolean, .showPrint) — If true, shows a small print button next to the chart.
- Show Save Button? (boolean, .showSave) — If true, shows a small save button next to the chart.
- Show Tooltips? (boolean, .tooltips) — If true, shows tooltips with point values.
- Show Warnings (boolean, .showWarnings) — If true, prints warnings generated during chart configuration.
- Sort Pens (boolean, .alphabetizePens) — If true, pen visibility checkboxes are sorted.
- Start Date (Date, .startDate) — Manual-mode start date for selecting pen data.
- Startup Range (String, .startupRange) — Historical-mode: starting range of time.
- Startup Selection (String, .startupSelection) — Historical-mode: starting selected range.
- Subplot Gap (double, .subplotGap) — The gap between subplots.
- Subplots (Dataset, .subplots) — Defines all subplots' relative size and color.
- Tag History Resolution (int, .tagHistoryResolution) — Used when Resolution Mode is "Fixed."
- Tag History Resolution Mode (int, tagHistoryResolutionMode) — Mode used for the number of requested points.
- Tag Pens (Dataset, .tagPens) — Defines all of the Tag History pens for the chart.
- Tick Density (float, .tickDensity) — Historical-mode: multiplied by width to compute ideal tick spacing.
- Tick Font (Font, .axisTickLabelFont) — The font for tick labels.
- Time Style (int, .timeStyle) — Style to display times of day (international support).
- Title Font (Font, .titleFont) — The font for the optional chart title.
- Today Color (Color, .todayIndicatorColor) — Historical-mode: color of the "Today Arrow" indicator.
- Total Datapoints (int, .datapoints) — Number of datapoints displayed by the graph. (Read only.)
- Track Margin (int, .trackMargin) — Historical-mode: room on either side of the slider track.
- Unit (int, .unit) — Realtime-mode: selected unit of the realtime date range.
- Unit Count (int, .unitCount) — Realtime-mode: number of units back to display.
- Validate Scan Class Executions (boolean, tagHistoryValidateScanclass) — Verifies the scan class execution record.
- Vert Gap (int, .vGap) — Vertical spacing to use for the pen checkboxes.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Where Clause (String, .globalWhereClause) — A where-clause snippet applied to all database pens.
- X Axis AutoRange? (boolean, .xAxisAutoRange) — If true, the X axis automatically fits the range of available data.
- X Axis Label (String, .xAxisLabel) — The label shown on the X Axis (time axis).
- X Axis Margin (double, .xAxisMargin) — Margin for the upper and lower ends of the x axis.
- X Axis Visible (boolean, .xAxisVisible) — Should the x-axis be displayed?
- X-Trace Large Number Format (String, .xTraceLargeNumberFormat) — Large decimal format for the x-trace value.
- X-Trace Number Format Threshold (double, .xTraceNumberFormatThreshold) — Threshold below which the small number format is used.
- X-Trace Small Number Format (String, .xTraceSmallNumberFormat) — Small decimal format for the x-trace value.
- X-Trace Track Mouse (boolean, .XTraceTrackMouse) — If enabled in X-Trace mode, the X-Trace follows the mouse.

**Scripting / extension functions**
- exportExcel(filename) — Saves the chart's datasets as an Excel file; returns the complete file path.
- print() — Prints the chart.
- setMode(mode) — Sets the current mode for the chart.
- exportDatasets() — Returns an ArrayList of datasets representing the time series data of each pen type.
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.
- [ext] getXTraceLabel — Opportunity to configure the x-trace label; return a string to override the default.
- [ext] onPowerTableRowsDropped — Called when rows are dropped from a Power Table onto the chart.
- [ext] onTagsDropped — Called when tags are dropped from the tag tree onto the chart.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).
### Equipment Schedule
Charts — A mix between the Status Chart, Gantt Chart, and Calendar components, for visualizing equipment/item downtime and scheduled events.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Break Events (Dataset, .breakEvents) — Scheduled breaks, which appear as downtime for all items.
- Current Time Color (Color, .nowColor) — The color of the current time indicator.
- Downtime Events (Dataset, .downtimeEvents) — Downtime events correlated to a specific item.
- Drag Enabled (boolean, .dragEnabled) — Whether scheduled events can be dragged for rescheduling.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- End Date (Date, .endDate) — The end of the time range to display.
- Event Border (Border, .eventBorder) — The normal border for a scheduled event.
- Event Font (Font, .eventFont) — The font to use for the event labels.
- Event Margin (int, .scheduledEventMargin) — Margin to leave visible above and below a scheduled event.
- Header Background (Color, .headerBackground) — Background color for the header timeline.
- Header Font (Font, .headerFont) — The font of the text in the header timeline.
- Header Item Font (Font, .itemFont) — The font to use for the header items' labels.
- Header Text Color (Color, .headerTextColor) — The color of the text in the header timeline.
- Items (Dataset, .items) — The cells, or equipment items, to have their schedules displayed.
- Line Color (Color, .lineColor) — The color of separating lines in the schedule.
- Name (String, .name) — The name of this component.
- Progress Bar Background (Color, .progressBackground) — Background color for the event progress bars.
- Progress Bar Border (Color, .progressBorder) — Border color for the event progress bars.
- Progress Bar Fill (Color, .progressFill) — Color for the 'done' portion of event progress bars.
- Resize Enabled (boolean, .resizeEnabled) — Whether scheduled events can be resized for duration changes.
- Row Height (int, .lineHeight) — The height of each event's schedule row.
- Schedule Background (Color, .scheduleBackground) — The background color of the schedule area.
- Scheduled Events (Dataset, .scheduledEvents) — The scheduled events for all configured items.
- Selected Event Border (Border, .selectedEventBorder) — The border for a selected scheduled event.
- Selected Event ID (String, .selectedEvent) — The ID of the selected event.
- Start Date (Date, .startDate) — The beginning of the time range to display.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .getDateAt(event) — Returns a date/time representing a point in time at the mouse event position.
- [ext] onBackgroundDragged — Called when the user drags a segment on the schedule background.
- [ext] onEventClicked — Called when the user clicks a scheduled event (use event.clickCount for double clicks).
- [ext] onEventDropped — Called when the user drags and drops a scheduled event; script must alter the data.
- [ext] onEventPopupTrigger — Called when the user right-clicks a scheduled event (build a context menu here).
- [ext] onEventResized — Called when the user drags an event's edge to resize its time span.
- [ext] onPopupTrigger — Called when the user right-clicks outside of an event.

### Gantt Chart
Charts — Task scheduling chart: a list of named tasks each with a start date, end date, and percent complete.

**Properties**
- Axis Font (Font, .axisLabelFont) — The font for axis labels.
- Border (Border, .border) — The border surrounding this component.
- Chart Title (String, .title) — Optional title at the top of the chart.
- Complete Color (Color, .completeColor) — The color to draw the amount completed in.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data driving the chart.
- Date Axis Title (String, .dateAxisTitle) — A date label to display on the axis title.
- Incomplete Color (Color, .incompleteColor) — The color to draw the amount remaining to do in.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Plot Background (Color, .plotBackground) — The background color for the plot.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Task Axis Title (String, .taskAxisTitle) — A task label to display on the axis title.
- Task Color (Color, .taskColor) — The main color to draw tasks.
- Tick Font (Font, .axisTickLabelFont) — The font for tick labels.
- Title Font (Font, .titleFont) — The font for the optional chart title.
- Tooltips? (boolean, .tooltips) — Show tooltips on tasks?
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).

### Pie Chart
Charts — A pie chart: a list of named items, each with a value that's part of a total.

**Properties**
- 3D Depth Factor (double, .depthFactor) — The depth of a 3D pie as a factor of chart height.
- Border (Border, .border) — The border surrounding this component.
- Chart Title (String, .title) — Optional title at the top of the chart.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data driving the chart.
- Enforce Circularity? (boolean, .circular) — If true, the pie can't be an oval even if the chart is.
- Extract Order (int, .extractOrder) — Whether the pie plot views columns as pies, or rows.
- Foreground Transparency (double, .foregroundAlpha) — Transparency of the pie (useful for 3D pies).
- Label Font (Font, .labelFont) — The font for labels, if there are labels.
- Label Format (String, .labelFormat) — Formatting string: {0}=wedge name, {1}=value, {2}=percent.
- Labels? (boolean, .labels) — Should labels be displayed near sections?
- Legend Font (Font, .legendFont) — The font for legend items, if there is a legend.
- Legend? (boolean, .legend) — Should there be an item legend below the chart?
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Outline Colors (Color[], .outlineColors) — Colors to use for the pie wedge outlines.
- Outline Visible (boolean, .outlineVisible) — Whether to display an outline around the pie chart.
- Outline Stroke (float, .outlineStroke) — The width for the section outline stroke.
- Plot Background (Color, .plotBackground) — Background color for all plots, unless overridden.
- Plot Insets (int, .plotInsets) — Padding to use around the actual plot rendering area.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .rotation) — Draw wedges clockwise or counter-clockwise from the starting angle.
- Section Colors (Color[], .sectionColors) — Colors to use for the pie wedge fills.
- Selected Wedge (String, .selectedData) — The currently selected wedge. (Read only.)
- Selection Enabled? (boolean, .selectionEnabled) — If true, the user can select wedges on the chart.
- Selection Highlight Color (Color, .selectionHighlightColor) — The color of the selection highlight.
- Selection Highlight Width (float, .selectionHighlightWidth) — The line width of the selection highlight.
- Starting Angle (int, .startAngle) — The start angle to draw the pie wedges.
- Style (int, .style) — Style of pie chart: standard, 3D, or ring.
- Title Font (Font, .titleFont) — The font for the chart's title.
- Tooltip Format (String, .tooltipFormat) — Formatting string: {0}=wedge name, {1}=value, {2}=percent.
- Tooltips? (boolean, .tooltips) — Should tooltips display when the mouse hovers over sections?
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).

### Radar Chart
Charts — Also called web/spider chart; displays a dataset as a two-dimensional polygon, comparing "actual" vs "desired" shapes.

**Properties**
- Actual Fill Color (Color, .actualFillColor) — Fill color for the actual polygon.
- Actual Stroke Color (Color, .actualStrokeColor) — Stroke color for the actual polygon.
- Actual Stroke Width (float, .actualStrokeWidth) — Stroke width for the actual polygon.
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Border Inset (double, .borderInset) — Area the chart should be inset from the component's border.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — Datapoints for the radar plot; each row represents a spoke.
- Desired Fill Color (Color, .desiredFillColor) — Fill color for the desired polygon.
- Desired Stroke Color (Color, .desiredStrokeColor) — Stroke color for the desired polygon.
- Desired Stroke Width (float, .desiredStrokeWidth) — Stroke width for the desired polygon.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Show Desired Shape (boolean, .showDesiredShape) — Display the desired shape on the chart.
- Spoke Color (Color, .foreground) — The color to use for the chart's spokes and exterior ring.
- Spoke Width (float, .strokeWidth) — The line width for the chart's spokes and exterior ring.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Sparkline Chart
Charts — A minimalistic chart that displays a line-chart history for a single datapoint, with optional markers and a desired range band.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Border Inset (double, .borderInset) — Space to inset the chart inside its border.
- Chart Max (Double, .chartMax) — Value at the upper edge of the chart. (Read only.)
- Chart Min (Double, .chartMin) — Value at the lower edge of the chart. (Read only.)
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The history data to draw in the sparkline chart.
- Desired High (Double, .desiredHi) — High value of the desired operating range (blank disables it).
- Desired Low (Double, .desiredLo) — Low value of the desired operating range (blank disables it).
- Desired Range Color (Color, .desiredRangeColor) — Color of the desired operating range band.
- First Marker Color (Color, .firstMarkerColor) — The color of the first value marker.
- First Marker Size (double, .firstMarkerSize) — The size of the first value marker.
- First Marker Style (int, .firstMarkerStyle) — The style of the first value marker.
- First Value (Double, .firstValue) — First (oldest) value in the dataset. (Read only.)
- High Marker Color (Color, .hiMarkerColor) — The color of the high value marker.
- High Marker Size (double, .hiMarkerSize) — The size of the high value marker.
- High Marker Style (int, .hiMarkerStyle) — The style of the high value marker.
- Last Marker Color (Color, .lastMarkerColor) — The color of the last value marker.
- Last Marker Size (double, .lastMarkerSize) — The size of the last value marker.
- Last Marker Style (int, .lastMarkerStyle) — The style of the last value marker.
- Last Value (Double, .lastValue) — Last (most recent) value in the dataset. (Read only.)
- Line Color (Color, .foreground) — The color of the sparkline.
- Line Width (float, .lineWidth) — The width of the sparkline.
- Low Marker Color (Color, .loMarkerColor) — The color of the low value marker.
- Low Marker Size (double, .loMarkerSize) — The size of the low value marker.
- Low Marker Style (int, .loMarkerStyle) — The style of the low value marker.
- Max Value (Double, .maxValue) — Largest value in the dataset. (Read only.)
- Min Value (Double, .minValue) — Smallest value in the dataset. (Read only.)
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (int, .quality) — Data quality code for any Tag bindings on this component.
- Range High (Double, .rangeHi) — Fixed value for the upper edge of the chart (blank = auto).
- Range Low (Double, .rangeLo) — Fixed value for the lower edge of the chart (blank = auto).
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Status Chart
Charts — Visualizes the status of one or more discrete datapoints over a time range as colored status bands.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Chart Title (String, .chartTitle) — Title of this chart.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data Format (int, .dataFormat) — Format of the incoming data ("wide" vs "tall").
- Date Style (int, .dateStyle) — Style to display dates in (international support).
- Domain Axis Color (Color, .domainAxisColor) — Color used on the domain axis.
- Domain Axis Font (Font, .domainAxisFont) — Font used on the domain axis.
- Domain Axis Label (String, .domainAxisLabel) — Label on the domain axis.
- Domain Axis Location (int, .domainAxisLocation) — Location of the domain axis.
- Legend (dataset, .legend) — Maps chart colors to descriptions.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Properties Loading (int, .propertiesLoading) — Number of properties currently being loaded. (Read only.)
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Range Axis Color (Color, .rangeAxisColor) — Color used on the range axis.
- Range Axis Font (Font, .rangeAxisFont) — Font used on the range axis.
- Range Axis Label (String, .rangeAxisLabel) — Label on the range axis.
- Range Axis Location (int, .rangeAxisLocation) — Location of the range axis.
- Range Axis Lower Margin (double, .rangeAxisLowerMargin) — Lower margin of the range axis.
- Range Axis Upper Margin (double, .rangeAxisUpperMargin) — Upper margin of the range axis.
- Series Data (Dataset, .data) — Data about each series ("wide" or "tall" format).
- Series Properties Data (Dataset, .properties) — Properties for each series.
- Series Spacing (double, .seriesSpacing) — Spacing between series (0.0–1.0).
- Show Domain Axis (boolean, .domainAxisVisible) — Whether the domain axis is visible.
- Show Range Axis (boolean, .rangeAxisVisible) — Whether the range axis is visible.
- Time Style (int, .timeStyle) — Style to display times of day (international support).
- Title Color (Color, .titleColor) — Color of the chart title.
- Title Font (Font, .titleFont) — Font on the chart title.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- [ext] configureChart — Opportunity to perform further chart configuration via scripting.
- [ext] getToolTip — Return a formatted tooltip String.

**Notes**
- Supports the shared chart right-click context menu (see Charting - Right Click Menu reference).
## Containers
### Container
Containers — All components are always inside of a container, except for the special Root Container of each window.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Combine Repaints (boolean, .combineRepaints) — Set true for containers with many sub-components needing frequent repaints, to combine them.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Font (Font, .font) — Font of text on this component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Texture (String, .texturePath) — Background texture image for this container.
- Tile Optimized (boolean, .optimizedDrawingEnabled) — If true, children never overlap, improving redraw performance.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Notes**
- To move a container around on a window in the Designer, hold Alt while clicking and dragging.

### Template Canvas
Containers — Similar to the Template Repeater but gives more fine-grained control over where and how each template instance is placed (per-instance layout constraints rather than a single flow/grid).

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Layout Constraints (String, .layoutConstraints) — The overall layout constraints for the canvas.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Scroll Behavior (int, .scrollBehavior) — Controls which direction(s) the canvas scrolls in.
- Show Loading (boolean, .showLoading) — If false, the loading indicator is never shown.
- Templates (Dataset, .templates) — A dataset containing a row per template to instantiate.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .getAllTemplates() — Returns a list of the templates that comprise the template canvas.
- .getTemplate(name) — Obtains the designated template object from the template canvas.
- [ext] initializeTemplate — Called once per template loaded; a good place for custom initialization.

### Template Repeater
Containers — Repeats instances of a template any number of times, arranged vertically, horizontally, or in a flow layout, with a scrollbar if they don't fit — an easy way to build screens representing many similar pieces of equipment.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Flow Alignment (int, .flowAlignment) — Alignment for "Flow" layout style (Left/Top, Right/Bottom, Center).
- Flow Direction (int, .flowDirection) — When layout style is flow, controls the direction components flow.
- Horizontal Gap (int, .horizontalGap) — The gap size to use for horizontal gaps.
- Index Parameter Name (String, .indexParamName) — Name of an integer template parameter set to each instance's index.
- Layout Style (int, .layoutStyle) — Controls how repeated template instances are laid out.
- Marquee Mode (boolean, .marqueeMode) — Turns the repeater into a scrolling marquee.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Repeat Behavior (int, .repeatBehavior) — "Count" repeats the template a fixed number of times; other modes derive count from data.
- Repeat Count (int, .repeatCount) — Number of repeats when Repeat Behavior is "Count."
- Scroll Delay (int, .scrollDelay) — Time (ms) to wait between marquee scroll steps.
- Stay Delay (int, .stayDelay) — Time (ms) to wait between scrolls.
- Template Parameters (Dataset, .templateParams) — Controls the number of templates and their parameter values.
- Template Path (String, .templatePath) — The path to the template that this container will repeat.
- Vertical Gap (int, .verticalGap) — The gap size to use for vertical gaps.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .getLoadedTemplates() — Returns a list of templates loaded into the Template Repeater.

**Notes**
- The live docs' page frontmatter/description for this component is mis-copied from the Report Viewer page; the description above uses the page body text instead.
## Display
### LED Display
Display — A stylized numeric or alphanumeric label rendered as lit/unlit LED segments.

**Properties**
- Background Color (Color, .background) — The color of the background.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the display's contents along the X axis.
- LED Lit (Color, .glyphForeground) — The color of lit LED segments.
- LED Unlit (Color, .glyphBackground) — The color of unlit LED segments.
- Letter Gap (float, .gap) — Percentage of height used as inter-character spacing.
- Margin (Insets, .margin) — The margin for the interior of the display.
- Mode (int, .mode) — The mode of the display (Numeric/Alphanumeric).
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Number Format Pattern (String, .numberFormat) — Number formatting string used to format the value.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Style (int, .style) — The visual style of the display.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text value of the display, used when Mode is Alphanumeric.
- Value (double, .value) — Numeric value of the display, used when Mode is Numeric.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Barcode
Display — Displays text as a barcode (1D or 2D, including QR codes).

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Barcode Background (Color, .barcodeBackground) — The background color of the actual barcode.
- Barcode Format (int, .barcodeType) — The barcode format to display.
- Barcode Height (int, .barcodeHeight) — The height of the barcode.
- Border (Border, .border) — The border surrounding this component.
- Check Digit (boolean, .checkDigit) — Include Check Digit?
- Code (String, .code) — The code string converted into a barcode.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Narrowest Bar Width (int, .narrowestBarWidth) — Width (px) of the narrowest bar.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .angleDegrees) — The angle of rotation in degrees.
- QRCode Error Correction Level (int, .qrEcLevel) — QR code error correction level.
- QRCode Version (int, .qrCodeVersion) — QR code version to use.
- Show Text? (boolean, .showText) — If true, shows the code as human-readable text beneath the barcode.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Compass
Display — Displays up to three needles at once on a cardinal direction compass.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Center Color (Color, .centerColor) — The center color of the compass.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Label Font (Font, .labelFont) — The font to use for the compass's labels.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rose Color (Color, .roseColor) — The background color of the rose.
- Rose Highlight (Color, .roseHighlightColor) — The highlight color of the rose.
- Styles (Dataset, .styles) — Contains the component's styles.
- Value 1 (double, .value1) — Value 1 for the compass.
- Value 1 Color (Color, .value1Color) — Main color for Value 1's needle.
- Value 1 Needle (int, .value1Needle) — Needle type for Value 1.
- Value 1 Outline (Color, .value1OutlineColor) — Outline color for Value 1's needle.
- Value 2 (double, .value2) — Value 2 for the compass.
- Value 2 Color (Color, .value2Color) — Main color for Value 2's needle.
- Value 2 Needle (int, .value2Needle) — Needle type for Value 2.
- Value 2 Outline (Color, .value2OutlineColor) — Outline color for Value 2's needle.
- Value 3 (double, .value3) — Value 3 for the compass.
- Value 3 Color (Color, .value3Color) — Main color for Value 3's needle.
- Value 3 Needle (int, .value3Needle) — Needle type for Value 3.
- Value 3 Outline (Color, .value3OutlineColor) — Outline color for Value 3's needle.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- [ext] configureChart(self, chart) — Opportunity to perform further configuration via scripting.

### Cylindrical Tank
Display — A 3D-styled cylindrical tank with liquid rendered inside based on a level/percentage.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Capacity (double, .capacity) — Total capacity of the tank.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Font (Font, .font) — Font of text on this component.
- Font Color (Color, .fontColor) — The color of the value and/or percentage labels.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Liquid Color (Color, .liquidColor) — Color of the filled tank section.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Percent Format (String, .percentFormat) — Format string used for the percentage.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .rotation) — The angle of rotation in degrees.
- Show Percentage (boolean, .showPercent) — Shows the percentage of tank filled when enabled.
- Show Value (boolean, .showValue) — Shows numeric value, capacity, and units when enabled.
- Styles (Dataset, .styles) — Contains the component's styles.
- Tank Color (Color, .tankColor) — Color of the non-filled tank section.
- Units (String, .units) — Units of measure for tank contents.
- Value (double, .value) — Numeric value of the tank's level.
- Value Format (String, .valueFormat) — Format string used for the value.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Image
Display — Displays images; unlike Label, adds rotation, flip, color-swap and tint filters, and stretch modes.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Color Swap Filter (boolean, .useColorSwap) — Swap a specific color to another.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Flip Horizontal (boolean, .flipHorizontal) — Flip (mirror) the image horizontally.
- Flip Vertical (boolean, .flipVertical) — Flip (mirror) the image vertically.
- Image Path (String, .path) — The relative path of the image.
- Load In Background (boolean, .loadInBackground) — Whether image loading happens off the UI thread.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .rotation) — The angle of rotation in degrees.
- Stretch Height (int, .stretchHeight) — Stretched height when Stretch Mode is "Parameters."
- Stretch Mode (int, .stretchMode) — The stretch mode for this image.
- Stretch Width (int, .stretchWidth) — Stretched width when Stretch Mode is "Parameters."
- Styles (Dataset, .styles) — Contains the component's styles.
- Swap From (Color, .swapFromColor) — Color changed to Swap To when Color Swap Filter is on.
- Swap Threshold (int, .swapThreshold) — Threshold (0-255) for swap-from color matching.
- Swap To (Color, .swapToColor) — Color the Swap From color is changed to.
- Tint Color (Color, .tintColor) — Color of the tint, when Tint Filter is on.
- Tint Filter (boolean, .useTint) — Tint the entire image a color (best with greyscale images).
- Use Cache (boolean, .useCache) — If false, bypasses the client image cache and reloads the image.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### IP Camera Viewer
Display — Displays a video stream from a network camera directly in a window.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Camera Buffer Size (int, .cameraBufferSize) — Size of the video buffer in bytes.
- Connection Retries (int, .connectRetries) — Number of times to attempt to connect to the stream.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Password (String, .password) — The password to authenticate with.
- Refresh Rate (int, .refreshRate) — Rate (ms) to poll the image if mode is 'JPEG Stills'.
- Retry Delay (int, .retryDelay) — Delay (ms) to wait between connection attempts.
- Scale Mode (int, .scaleMode) — The scaling performance hint to use.
- Scale Video (boolean, .scaleVideo) — Scales the video to the viewer's size (CPU-intensive).
- Show Stats (boolean, .showStats) — If true, overlays fps and Kbps statistics on the video.
- URL (String, .url) — The HTTP URL of the video stream to display.
- Use Authentication? (boolean, .useAuthentication) — If true, authenticates the URL connection with the given credentials.
- User-Agent (String, .userAgent) — If non-empty, the HTTP User-Agent to spoof.
- Username (String, .username) — The username to authenticate with.
- Video Mode (int, .mode) — The type of video stream the URL points to.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Label
Display — Displays text, images, or both; text can be HTML-formatted and bound to dynamic properties.

**Properties**
- Background Color (Color, .background) — The background color of the label, if Fill Background is true.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Background (boolean, .fillBackground) — If true, the label's background color is drawn.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The color of the label's text.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to its icon.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between the icon and the text.
- Image Path (String, .path) — The relative path of the image.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .rotation) — The angle of rotation in degrees.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this Label.
- Vertical Alignment (int, .verticalAlignment) — Alignment of the label's contents along the Y axis.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to its icon.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.
### Level Indicator
Display — Filled with liquid that rises and falls as Value changes; can be placed behind a symbol/factory object with a cutout for a custom shape.

**Properties**
- Background Color (Color, .background) — The color of the background.
- Border (Border, .border) — The border surrounding this component.
- Capacity (double, .capacity) — Total capacity of the tank.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Filled Color (Color, .foreground) — Color of the filled portion.
- Font (Font, .font) — Font of text on this component.
- Font Color (Color, .fontColor) — The foreground color of the component.
- Gradient (boolean, .gradient) — Whether the level is drawn as a 3D gradient.
- Liquid Waves (boolean, .waves) — Whether liquid waves are drawn.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Orientation (int, .orientation) — Direction the level "grows" for an increase in value.
- Percent Format (String, .percentFormat) — Format string used for the percentage.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Show Percentage (boolean, .showPercent) — Whether the percentage filled is displayed.
- Show Value (boolean, .showValue) — Whether the numeric value, capacity, and units are displayed.
- Styles (Dataset, .styles) — Contains the component's styles.
- Units (String, .units) — Units of measure for tank contents.
- Value (double, .value) — Numeric value of the tank's level.
- Value Format (String, .valueFormat) — Format string used for the value.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Wave Height (int, .waveHeight) — The height of each wave.
- Wave Length (int, .waveLength) — The length of each wave.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Linear Scale
Display — Displays tick marks and labels representing a linear range, plus indicators positioned along the scale.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Fine Tick Color (Color, .fineTickColor) — The line color for fine ticks.
- Fine Tick Length (double, .fineTickLength) — The line length for fine ticks, in pixels.
- Fine Tick Span (double, .fineTickSpan) — Span length for fine ticks (factor of major/minor span).
- Fine Tick Thickness (float, .fineTickStroke) — The line thickness for fine ticks, in pixels.
- Indicators (Dataset, .indicators) — Stores the indicators (if any) for the scale.
- Label Angle (int, .labelAngle) — The angle that the labels are drawn at.
- Label Color (Color, .majorTickLabelColor) — Color used for drawing tick labels.
- Label Font (Font, .majorTickFont) — Font used for drawing tick labels.
- Label Format (String, .majorTickLabelFormat) — The label format string, e.g. "%.1f".
- Major Tick Color (Color, .majorTickColor) — The line color for major ticks.
- Major Tick Length (double, .majorTickLength) — The line length for major ticks, in pixels.
- Major Tick Span (double, .majorTickSpan) — Span length for major ticks (multiple of minor tick span).
- Major Tick Thickness (float, .majorTickStroke) — The line thickness for major ticks, in pixels.
- Margin (double, .margin) — Margin to leave blank as a percentage of total height/width.
- Max Value (double, .maxValue) — The upper bound of the scale.
- Min Value (double, .minValue) — The lower bound of the scale.
- Minor Tick Color (Color, .minorTickColor) — The line color for minor ticks.
- Minor Tick Length (double, .minorTickLength) — The line length for minor ticks, in pixels.
- Minor Tick Span (double, .minorTickSpan) — Span length for minor ticks (factor of major tick span).
- Minor Tick Thickness (float, .minorTickStroke) — The line thickness for minor ticks, in pixels.
- Mirror (boolean, .mirror) — Mirror the scale so it paints against the opposite edge.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reverse Range (boolean, .reverseRange) — Reverse the scale so values go high to low instead of low to high.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Meter
Display — Shows a value on a needle-gauge, with up to five configurable colored interval arcs.

**Properties**
- Arc Width (float, .arcWidth) — The width of the colored interval arcs.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Dial Background (Color, .dialBackground) — The background color of the dial face.
- Dial Shape (int, .dialType) — The shape of the dial (how the dial face looks).
- Interval 1-5 Background (Color, .interval{N}Background) — Fill color for the wedge of each interval.
- Interval 1-5 High/Low (double, .interval{N}High/Low) — Upper/lower bound of each interval.
- Interval 1-5 Outline (Color, .interval{N}Outline) — Color to paint the arc of each interval.
- Meter Angle (int, .meterAngle) — The angle in degrees of the meter's centerpoint (90 = straight up).
- Meter Angle Extent (int, .meterAngleExtent) — The extent, in degrees, of the entire meter.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Needle Color (Color, .needleColor) — The color of the meter's needle.
- Needle Size (float, .needleSize) — The size of the base of the needle.
- Needle Stroke Color (Color, .needleStrokeColor) — The color of the needle's stroke.
- Needle Stroke Size (float, .needleStrokeSize) — The size of the needle's stroke.
- Overall High Bound (double, .overallHigh) — High bound for the whole meter.
- Overall Low Bound (double, .overallLow) — Lower bound for the whole meter.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reverse Range? (boolean, .reverseRange) — If true, right-to-left needle movement counts as positive.
- Show Tick Labels? (boolean, .ticks) — If true, value is shown at interval-boundary ticks.
- Styles (Dataset, .styles) — Contains the component's styles.
- Tick Color (Color, .tickColor) — The color of tick marks.
- Tick Format (String, .tickLabelFormat) — Number format for the tick labels.
- Tick Label Color (Color, .tickLabelColor) — The color of the tick labels.
- Tick Label Font (Font, .labelFont) — The font for tick labels.
- Tick Size (double, .tickSize) — Distance between ticks.
- Units (String, .units) — Describes the units for the current value label.
- Value (double, .value) — The value shown by the needle and current-value label.
- Value Color (Color, .valueColor) — The color of the meter's current value label.
- Value Format (String, .valueLabelFormat) — Number format for the value label.
- Value Label Font (Font, .valueFont) — The font for the current value label.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- [ext] configureChart(self, chart) — Opportunity to perform further configuration via scripting.

### Moving Analog Indicator
Display — Shows an analog value in context (setpoint, alarm bands, interlocks, desired range) so you can quickly see whether it's in the normal range.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Desired High/Low (Double, .desiredHi/.desiredLo) — Bounds of the desired operating range.
- Desired Range Color (Color, .desiredRangeColor) — Color of the desired range band.
- High Alarm (Double, .hiAlarm) — Value above which is a high alarm.
- High High Alarm (Double, .hihiAlarm) — Value above which is a high-high alarm.
- High Interlock (Double, .hiInterlock) — Value above which an interlock is activated.
- Inactive Alarm Color (Color, .inactiveAlarmColor) — Color of inactive alarm range.
- Interlock Color (Color, .interlockColor) — Color of the interlock range.
- Level 1 Alarm Color (Color, .level1AlarmColor) — Color of an active level 1 alarm (Hi-Hi or Lo-Lo).
- Level 2 Alarm Color (Color, .level2AlarmColor) — Color of an active level 2 alarm (Hi or Lo).
- Low Alarm (Double, .loAlarm) — Value below which is a low alarm.
- Low Interlock (Double, .loInterlock) — Value below which an interlock is activated.
- Low Low Alarm (Double, .loloAlarm) — Value below which is a low-low alarm.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Process Value (Double, .processValue) — The current value of the process.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Range Fill (Color, .rangeFill) — Background color of the range strip.
- Range High/Low (double, .rangeHi/.rangeLo) — Overall high/low value for the display.
- Range Stroke (Color, .rangeStroke) — Stroke color for the range strip.
- Reverse Indicator (boolean, .reverseIndicatorLocation) — Put the indicator triangle on the other side of the track.
- Setpoint Fill (Color, .setpointFill) — Fill color of the setpoint indicator.
- Setpoint Stroke (Color, .setpointStroke) — Stroke color of the setpoint indicator.
- Setpoint Value (Double, .setpointValue) — The current value of the setpoint.
- Show Value (boolean, .showValue) — Show the current value above/beneath the value indicator.
- Stroke Width (float, .strokeWidth) — Stroke width for lines drawn.
- Styles (Dataset, .styles) — Contains the component's styles.
- Value Color (Color, .color) — The color of the value label.
- Value Font (Font, .font) — The font for the value label.
- Value Format (String, .valueFormat) — String format for the value, if shown.
- Value Indicator Fill (Color, .valueFill) — Fill color of the value indicator.
- Value Indicator Stroke (Color, .valueStroke) — Stroke color of the value indicator.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Multi-State Indicator
Display — A specialized label used to display a discrete state.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to its icon.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between the icon and the text.
- Image Path (String, .path) — The relative path of the image.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- State (int, .state) — The current state of the component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this Label.
- Vertical Alignment (int, .verticalAlignment) — Alignment of the label's contents along the Y axis.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to its icon.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Numeric Label
Display — A specialized label designed to display a number with prefix/suffix/units and a numeric format pattern.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Disabled Image Path (String, .disabledPath) — Path of the image shown when this component is not enabled.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Fill Background (boolean, .fillBackground) — If true, the label's background color is drawn.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Horizontal Text Position (int, .horizontalTextPosition) — Horizontal position of text relative to its icon.
- Icon-Text Spacing (int, .iconTextGap) — Space (px) between the icon and the text.
- Image Path (String, .path) — The relative path of the image.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Number Format Pattern (String, .pattern) — The number formatting string used to format the value.
- Prefix (String, .prefix) — A string placed before the number.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Rotation (int, .rotation) — The angle of rotation in degrees.
- Styles (Dataset, .styles) — Contains the component's styles.
- Suffix (String, .suffix) — A string placed after the number, and before the units.
- Units (String, .units) — Engineering units to display after the number.
- Value (double, .value) — The numeric value of this label.
- Vertical Alignment (int, .verticalAlignment) — Alignment of the label's contents along the Y axis.
- Vertical Text Position (int, .verticalTextPosition) — Vertical position of text relative to its icon.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Progress Bar
Display — Visually indicates progress of a task, or displays any value with an upper and lower bound.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Direction (int, .direction) — The direction of progress for this progress bar.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal? (boolean, .horizontal) — If true, displays horizontally, else vertically.
- Indeterminate? (boolean, .indeterminate) — When true, shows animation indicating unknown-duration progress.
- Maximum (int, .maximum) — The maximum value this progress bar will reach.
- Minimum (int, .minimum) — The minimum value this progress bar will reach.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Show Percentage? (boolean, .stringPainted) — If true, displays its percentage as text.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text Color (Color, .textColor) — The color of the text on the progress bar.
- Value (int, .value) — The current state of the Progress Bar.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Thermometer
Display — Displays a temperature value as a mercury level, with up to three colored interval bands.

**Properties**
- Axis Label Color (Color, .axisColor) — The color of the meter's y-axis label.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Follow data in ranges (boolean, .followDataInSubranges) — If true, Y axis scales to zoom in on active data ranges.
- Interval 1-3 Color (Color, .interval{N}Color) — The color of each interval.
- Interval 1-3 High/Low (double, .interval{N}High/Low) — Upper/lower bound of each interval.
- Mercury Color (Color, .mercuryColor) — The default color of the mercury.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Overall High/Low Bound (double, .overallHigh/.overallLow) — High/low bound for the whole thermometer.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Thermometer Color (Color, .thermometerColor) — The color of the outline of the thermometer.
- Thermometer Width (int, .strokeWidth) — The width of the lines used to draw the thermometer.
- Units (int, .units) — Describes the units for the current value label.
- Use Range Color (boolean, .useSubrangePaint) — Whether mercury color changes based on the interval range.
- Value (double, .value) — The value shown by the mercury level and value label.
- Value Color (Color, .valueColor) — The color of the current value label.
- Value Label Font (Font, .valueFont) — The font for the current value label.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- [ext] configureChart(self, chart) — Opportunity to perform further configuration via scripting.
## Input
### Dropdown List
Input — Displays a list of choices in a limited space; shows the current selection, presenting choices only when the dropdown is clicked.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — Dataset containing the list of choices in the dropdown.
- Dropdown Display Mode (int, .mode) — Changes the dropdown's display (list vs table style).
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Hide Table Columns? (String, .hideTableColumns) — Comma-separated list of columns to hide from the dropdown table.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the contents along the X axis.
- Max Row Count (int, .maximumRowCount) — Rows shown before a scrollbar appears.
- Max Table Height (int, .maxTableHeight) — Max height for the dropdown table (table mode only).
- Max Table Width (int, .maxTableWidth) — Max width for the dropdown table (table mode only).
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- No Selection Label (String, .noSelectionLabel) — Label to display when nothing is selected.
- No Selection String (String, .noSelectionString) — String value when nothing is selected.
- No Selection Value (int, .noSelectionValue) — Value when nothing is selected.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Row Height (int, .rowHeight) — Height of each item in the dropdown list.
- Selected Index (int, .selectedIndex) — Index of the selected item. (Read only.)
- Selected Label (String, .selectedLabel) — The currently selected label.
- Selected String Value (String, .selectedStringValue) — Currently selected value, if the value column is a string.
- Selected Value (Integer, .selectedValue) — The currently selected value.
- Selection Background (Color, .selectionBackground) — Background color of a selected cell in the dropdown list.
- Selection Mode (int, .selectionMode) — Determines the behavior/style of the dropdown selection.
- Show Table Header? (boolean, .showTableHeader) — Whether the dropdown table header is displayed (table mode only).
- Styles (Dataset, .styles) — Contains the component's styles.
- Vertical Alignment (int, .verticalAlignment) — Alignment of the contents along the Y axis.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Formatted Text Field
Input — A specialized text field for alphanumeric input that must match a pattern or be formatted a specific way (regex or mask validation).

**Properties**
- Allows Invalid Text (boolean, .allowsInvalid) — Allows invalid text to commit.
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Commit While Typing (boolean, .commitsOnValidEdit) — Commits valid text while the user is typing.
- Committed Value (String, .committedValue) — Committed text value.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Focus Lost Behavior (int, .focusLostBehavior) — Controls how a transaction can be committed.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Formatted Mask Pattern (String, .formattedMaskPattern) — Formatted mask validation pattern.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Overwrites Text (boolean, .overwriteMode) — Overwrites text while typing.
- Reg Ex Pattern (String, .validationPattern) — Regular expression validation pattern.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Contents of this Text Field.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Touchscreen Keyboard Layout (String, .keyboardName) — Touchscreen keyboard layout to use for this component.
- Validation Mode (int, .validationMode) — Regex or mask-driven field validation.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Language Selector
Input — Sets the user's locale to control display of dates, times, numbers, and the language used for translations.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Selected Locale (String, .selectedLocale) — Display name of the currently selected locale. (Read only.)
- Selection Background (Color, .selectionBackground) — Background color of a selected cell in the dropdown list.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Numeric Text Field
Input — Like the Text Field but specialized for numbers, with bounds, formatting, and Integer/Double/Float/Long value properties.

**Properties**
- Background (Color, .editableBackground) — The background color of the text box (when editable).
- Border (Border, .border) — The border surrounding this component.
- Commit On Focus Loss (boolean, .commitOnFocusLost) — If true, a pending edit takes effect on focus loss.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Decimal Format (String, .decimalFormat) — Formatting string used for displaying numbers.
- Defer Updates (boolean, .deferUpdates) — If true, value properties don't fire updates while typing.
- Editable? (boolean, .editable) — If true, an input box; if false, display-only.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Error on Out-of-Bounds (boolean, .errorOnOutOfBounds) — Show an error message if the user's input is out-of-bounds.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Maximum (double, .maximum) — Maximum value (inclusive), if Use Bounds is true.
- Minimum (double, .minimum) — Minimum value (inclusive), if Use Bounds is true.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Non-Editable Background (Color, .nonEditableBackground) — Background color when this text box is non-editable.
- Number Type (int, .mode) — What type of numbers this field should accept.
- Out Of Bounds Message (String, .outOfBoundsMessage) — Error message to display if input is out-of-bounds.
- Protected Mode? (boolean, .protectedMode) — If true, users must double-click to edit.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reject Updates During Edit (boolean, .rejectUpdatesDuringEdit) — If true, rejects external updates while being edited.
- Styles (Dataset, .styles) — Contains the component's styles.
- Suffix (String, .suffix) — A string to display after the value.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Use Bounds? (boolean, .useBounds) — Only allows user-entered values between Minimum and Maximum.
- Value (Double) (double, .doubleValue) — Value as a double (use the property matching Number Type).
- Value (Float) (float, .floatValue) — Value as a float (use the property matching Number Type).
- Value (Integer) (int, .intValue) — Value as an integer (use the property matching Number Type).
- Value (Long) (long, .longValue) — Value as a long (use the property matching Number Type).
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- getSelectedText() — Returns the currently selected or highlighted text in the field.

### Password Field
Input — Like a text field that doesn't display the text being edited; the echo character can be customized.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Echo Character (String, .echoCharacter) — The character displayed instead of the real ones.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reject Updates During Edit (boolean, .rejectUpdatesDuringEdit) — If true, rejects external updates while being edited.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Touchscreen Keyboard Layout (String, .keyboardName) — Touchscreen keyboard layout to use for this component.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Slider
Input — Lets the user drag an indicator along a scale to choose a value; can orient horizontally or vertically.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Defer Updates (boolean, .deferred) — Only publish value updates when not actively being changed.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Slider (boolean, .horizontal) — If true, horizontal; otherwise vertical.
- Inverted? (boolean, .inverted) — Reverses the value range shown for the slider.
- Major Tick Spacing (int, .majorTickSpacing) — Distance, in values, between major tick marks.
- Maximum Value (int, .maximum) — The value when the slider is all the way right/up.
- Minimum Value (int, .minimum) — The value when the slider is all the way left/down.
- Minor Tick Spacing (int, .minorTickSpacing) — Distance, in values, between minor tick marks.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Paint Labels? (boolean, .paintLabels) — If true, value labels are shown.
- Paint Ticks? (boolean, .paintTicks) — If true, value tick marks are shown.
- Paint Track? (boolean, .paintTrack) — If true, the slider's track is shown.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Snap To Ticks? (boolean, .snapToTicks) — Only allows selection of values at the tick marks.
- Styles (Dataset, .styles) — Contains the component's styles.
- Value (int, .value) — The current value of the slider.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Spinner
Input — Represents a value that's part of a series of values, such as numbers and dates.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Date Format (String, .dateFormat) — Date format pattern used when the spinner is in date mode.
- Date in Milliseconds (long, .dateInMillis) — The date in ms from epoch. (Read only.)
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Number Format (String, .numberFormat) — Number format pattern used when the spinner is in numeric mode.
- Numeric Maximum (double, .maxValue) — Maximum value this spinner accepts in 'Integer'/'Double' mode.
- Numeric Minimum (double, .minValue) — Minimum value this spinner accepts in 'Integer'/'Double' mode.
- Numeric Step Size (double, .stepSize) — Step size when in 'Integer'/'Double' mode.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Spinner Mode (int, .spinnerMode) — Which data type this spinner accepts.
- Styles (Dataset, .styles) — Contains the component's styles.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Value (Date) (Date, .dateValue) — Current value if mode is 'Date'.
- Value (Double) (double, .doubleValue) — Current value if mode is 'Double'.
- Value (Integer) (int, .intValue) — Current value if mode is 'Integer'.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Text Area
Input — For multi-line plain text (no HTML/styling); scrolls vertically on demand and horizontally if line wrap is off.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Columns (int, .columns) — Number of columns you expect to display (scrollbar sizing hint).
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Defer Updates (boolean, .deferUpdates) — If true, the text property doesn't fire updates while typing.
- Editable (boolean, .editable) — Whether the user can edit the text.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Line Wrap (boolean, .lineWrap) — Should this area wrap lines?
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reject Updates During Edit (boolean, .rejectUpdatesDuringEdit) — If true, rejects external updates while being edited.
- Rows (int, .rows) — Number of rows you expect to display (scrollbar sizing hint).
- Styles (Dataset, .styles) — Contains the component's styles.
- Tab Size (int, .tabSize) — Adjusts the default size of tab characters.
- Text (String, .text) — Text of this component.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Touchscreen Keyboard Layout (String, .keyboardName) — Touchscreen keyboard layout to use for this component.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

### Text Field
Input — For any single-line alphanumeric text input.

**Properties**
- Background (Color, .editableBackground) — The background color of the text box (when editable).
- Border (Border, .border) — The border surrounding this component.
- Commit On Focus Loss (boolean, .commitOnFocusLost) — If true, a pending edit takes effect on focus loss.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Defer Updates (boolean, .deferUpdates) — If true, the text property doesn't fire updates while typing.
- Editable? (boolean, .editable) — If true, an input box; if false, display-only.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Horizontal Alignment (int, .horizontalAlignment) — Alignment of the label's contents along the X axis.
- Maximum Characters (int, .maxChars) — Character limit for the text box; -1 for unlimited.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Non-Editable Background (Color, .nonEditableBackground) — Background color when this text box is non-editable.
- Protected Mode? (boolean, .protectedMode) — If true, users must double-click to edit.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Reject Updates During Edit (boolean, .rejectUpdatesDuringEdit) — If true, rejects external updates while being edited.
- Styles (Dataset, .styles) — Contains the component's styles.
- Text (String, .text) — Text of this component.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Touchscreen Keyboard Layout (String, .keyboardName) — Touchscreen keyboard layout to use for this component.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- getSelectedText() — Returns the currently selected or highlighted text in the field.
## Misc
### Line
Misc — Displays a straight line; can run north-south, east-west, or diagonally, with optional arrowheads and sine-wave rendering.

**Properties**
- Color (Color, .foreground) — The color of the line.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Dash Pattern (String, .strokePattern) — Comma-delimited numbers indicating the stroke dash pattern.
- Left Arrow (boolean, .leftArrow) — Draw an arrow head on the left/top of the line?
- Left Arrow Size (int, .leftArrowSize) — The size of the left arrow, if present.
- Line Mode (int, .lineMode) — Where in the rectangle the line is drawn.
- Line Style (int, .lineStyle) — The shape of the line (straight, sine, etc.).
- Line Width (int, .lineWidth) — The width of the line in pixels.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Right Arrow (boolean, .rightArrow) — Draw an arrow head on the right/bottom of the line?
- Right Arrow Size (int, .rightArrowSize) — The size of the right arrow, if present.
- Sine Height (int, .sineHeight) — The amplitude of the sine wave to be drawn.
- Sine Length (int, .sineLength) — The wavelength of the sine wave to be drawn.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Paintable Canvas
Misc — A canvas that can be custom-painted using Jython scripting; an advanced, powerful but not beginner-friendly component.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Focusable (boolean, .focusable) — If focusable, receives keyboard input and key events.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Notes**
- An advanced component for users comfortable with scripting: not beginner-friendly, but extraordinarily powerful for fully custom-drawn graphics.

### Pipe Joint
Misc — A joint used to visually connect two or more Pipe Segments, with configurable outlets on each side.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Bottom? (boolean, .bottom) — Whether the joint has an outlet at the bottom.
- Center Fill (Color, .mainColor) — The center color of the fill gradient.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Edge Fill (Color, .secondaryColor) — The edge color of the fill gradient.
- Left? (boolean, .left) — Whether the joint has an outlet at the left.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Outline Color (Color, .outlineColor) — The color of the outline border.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Right? (boolean, .right) — Whether the joint has an outlet at the right.
- Styles (Dataset, .styles) — Contains the component's styles.
- Top? (boolean, .top) — Whether the joint has an outlet at the top.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Pipe Segment
Misc — Displays a quasi-3D pipe segment, meant to be combined with Pipe Joints to build piping diagrams.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Center Fill (Color, .mainColor) — The center color of the fill gradient.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Edge Fill (Color, .secondaryColor) — The edge color of the fill gradient.
- End 1 Bottom? / Cap? / Top? (boolean, .end1Bottom/.end1Cap/.end1Top) — Whether to draw the border at end #1's bottom, cap, or top.
- End 2 Bottom? / Cap? / Top? (boolean, .end2Bottom/.end2Cap/.end2Top) — Whether to draw the border at end #2's bottom, cap, or top.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Outline Color (Color, .outlineColor) — The color of the outline border.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

### Signal Generator
Misc — Like the Timer, but its value follows a configurable waveform (sine, square, etc.) rather than a simple counter — useful for demos/simulation.

**Properties**
- Lower Bound (double, .lower) — The lower bound of the signal value.
- Name (String, .name) — The name of this component.
- Period (int, .period) — The period of the signal in milliseconds.
- Running? (boolean, .running) — Whether the signal is being generated.
- Signal Type (int, .signalType) — The shape of the signal (sine, square, triangle, etc.).
- Upper Bound (double, .upper) — The upper bound of the signal value.
- Value (double, .value) — The current value of this signal generator.
- Values/Period (int, .valuesPerPeriod) — The number of value changes per period.

### Sound Player
Misc — An invisible component that facilitates audio clip playback in the client.

**Properties**
- Loop Count (int, .loopCount) — The "N" when Loop Mode is "Loop N Times."
- Loop Mode (int, .loopMode) — How many times the sound plays when triggered.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Mute (boolean, .mute) — If true, the clip is muted during playback.
- Name (String, .name) — The name of this component.
- Play Mode (int, .playMode) — Whether the sound plays automatically or on trigger.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Sound Data (byte[], .soundData) — The clip that this component plays.
- Trigger (boolean, .trigger) — Plays the clip when true, if Play Mode is trigger-based.
- Volume (double, .volume) — Playback volume, from 0.0 to 1.0.

### Timer
Misc — An invisible component used to create repeated events (a counter that fires on an interval) in a window.

**Properties**
- Bound (int, .max) — The value is always guaranteed to be less than this upper bound.
- Delay (ms) (int, .delay) — Delay in milliseconds between timer events.
- Initial Delay (ms) (int, .initialDelay) — Delay in milliseconds before the first event once running.
- Name (String, .name) — The name of this component.
- Running? (boolean, .running) — Whether the timer sends timer events.
- Step by (int, .step) — Amount added to the value each time the timer fires.
- Value (int, .value) — The current counter value; increments each iteration.

### Web Browser
Misc — Embeds a full web browser (JxBrowser-based) inside an Ignition Client, with proxy configuration and scripting control.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- FTP/HTTP/HTTPS Proxy Port/Server (int/String) — Proxy host/port settings for FTP, HTTP, and HTTPS connections.
- Mode (int, .mode) — Data source for the browser (Starting URL vs Starting HTML).
- Name (String, .name) — The name of this component.
- Popups Allowed (boolean, .popupsAllowed) — Allows popups in the displayed web page.
- Proxy Exceptions (String, .proxyExceptions) — Comma-delimited rules for sites bypassing the proxy.
- Proxy Password (String, .proxyPassword) — Password for proxy authentication.
- Proxy Username (String, .proxyUsername) — Username for proxy authentication.
- SOCKS Proxy Port/Server (int/String) — Host/port for SOCKS proxies.
- Show Navigation Buttons (boolean, .showNavigation) — Shows navigation buttons at the top of the frame.
- Starting HTML (String, .startingHtml) — Initial HTML displayed when Mode is HTML.
- Starting URL (String, .startingUrl) — Initial URL displayed when Mode is URL.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this component responds if touchscreen mode is enabled.
- Use Proxies (boolean, .useProxies) — If checked, uses the proxy settings.
- Use Proxy Authentication (boolean, .useProxyAuthentication) — If checked, uses the proxy username/password.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Zoom Level (double, .zoomLevel) — Zoom level for the displayed page (0.0 = normal).

**Scripting / extension functions**
- .getBrowser() — Returns the underlying JxBrowser browser object.
- .executeJavaScript() — Executes arbitrary JavaScript on the loaded page.
- .getImage() — Returns a byte-array JPEG screenshot of the current browser window.
- .back() — Navigates one page back in browser history.
- .forward() — Navigates one page forward in browser history.
- .refresh() — Refreshes the current page.
- [ext] initialize() — Called when the component is initialized; a chance to initialize the browser.

**Notes**
- Using proxy switches directly is considered unsupported since they can drastically change component behavior; use with care.
## Reporting Components
### Column Selector
Reporting Components — Conceptually similar to the Row Selector, but filters columns from its output dataset instead of rows.

**Properties**
- Alphabetize (Boolean, .alphabetize) — If true, checkboxes are ordered alphabetically by their text.
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (Int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data In (Dataset, .Data_in) — Input dataset (default binding target when dropped).
- Data Out (Dataset, .Data_out) — Output dataset (default binding target when dropped).
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Group By Dataset (Boolean, .grouping) — If true, checkboxes are grouped by their dataset.
- Horizontal Gap (Int, .hGap) — Horizontal gap between checkboxes or grouping panels.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Normalize Widths (Boolean, .normalizeWidths) — If true, all checkboxes get the same width.
- Vertical Gap (Int, .vGap) — Vertical gap between checkboxes and grouping panels.
- Visible (Boolean, .visible) — If disabled, the component will be hidden.

### File Explorer
Reporting Components — Displays a filesystem tree to the user; can be rooted at any folder, including network folders.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Enabled (boolean, .componentEnabled) — If disabled, the component can't be used.
- File extension filter (String, .fileFilter) — Semi-colon-separated list of extensions to filter out.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Root Directory (String, .rootDir) — A directory to act as the root of the file explorer.
- Selected Path (String, .selectedPath) — The selected file or folder's path.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Notes**
- Setting Root Directory to a network folder gives all clients access to everything within it — restrict permissions accordingly.

### PDF Viewer
Reporting Components — Displays a PDF from a file path or a URL.

**Properties**
- Border (Border, .border) — The border surrounding this component.
- File Path (String, .filePath) — Path to the .pdf file to be displayed.
- Footer Visible (Boolean, .footerVisible) — If false, the footer is not displayed.
- Name (String, .name) — The name of this component.
- Page Fit Mode (Integer, .pageFitMode) — Mode to fit the document within the viewer.
- Page View Mode (Integer, .pageViewMode) — How to display the PDF (One Page, One Column, Two Page, etc.).
- Toolbar Visible (Boolean, .toolBarVisible) — Shows the top PDF control toolbar.
- Utility Visible (Boolean, .utilityPaneVisible) — Shows the Utility Sidebar.
- Visible (Boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .loadPDFBytes(bytes, name) — Passes in the bytes of a PDF and loads them into the viewer.
- .print(showDialog) — Prints the PDF.
- .setZoomFactor(zoom) — Sets the current zoom level, clamped to the min/max allowed.

**Notes**
- Clicking Save in the runtime saves a copy to the client computer, not the Ignition Gateway.

### Report Viewer
Reporting Components — Runs and displays Reports (from the Reporting module) inside Vision windows.

**Properties**
- Background Color (Color, .background) — Color that lays underneath the report.
- Border (Border, .border) — The border surrounding this component.
- Current Page (Int, .currentPage) — Current page in the report being viewed.
- Fit Panel (Boolean, .fitPanel) — Ignores zoom and fits the report to the component.
- Foreground Color (Color, .foreground) — The foreground color of labels on the component.
- Name (String, .name) — The name of this component.
- Page Count (Int, .pageCount) — Number of pages in the report.
- Report Loading (Boolean, reportLoading) — True while the report is loading (read only at runtime).
- Report Path (String, .reportPath) — Path in the Project to the Report to view.
- Show Controls (Boolean, .showControls) — Shows the bar with page and zoom controls.
- Suggested Filename (String, .suggestedFilename) — Default filename offered when the user saves the report.
- Visible (Boolean, .visible) — If disabled, the component will be hidden.
- Zoom Factor (Float, .zoomFactor) — Zoom factor for the rendered report.

**Scripting / extension functions**
- .print(printerName, showDialog) — Prints via the named printer, optionally showing the print dialog.
- getBytesPDF() — Returns the generated report's bytes as PDF.
- getBytesPNG() — Returns the generated report's bytes as PNG.
- saveAsPDF(fileName) — Prompts the user to save a copy of the report as PDF.
- saveAsXls(fileName) — Prompts the user to save a copy of the report as XLS.
- [ext] onReportGenerated — Called when report generation completes.

**Notes**
- Print methods only work once the report has finished loading in the viewer.

### Row Selector
Reporting Components — A visual filter-tree component for datasets: builds a tree of filter nodes and outputs the filtered rows.

**Properties**
- All Data Node Text (String, .allDataNodeText) — Text for the "All Data" node, if displayed.
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (Cursor, .cursor) — The mouse cursor to use when hovering over this component.
- Data In (Dataset, .dataIn) — Input of the row selection tree; the filter tree is built from this.
- Data Out (Dataset, .dataOut) — Output of the row selection tree, changes based on user selection.
- Expand All Data Node (boolean, .expandAllDataNode) — If true, the "All Data" root node starts expanded and selected.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Mouseover Text (String, .tooltiptext) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Selection Background (Color, .selectionBackground) — The background color of the selected node.
- Show All Data Node (boolean, .showAllDataNode) — Whether the "All Data" root node is shown.
- Show Node Size (boolean, .showNodeSize) — If true, shows the number of rows in each node.
- Show Root Handles (boolean, .showRootHandles) — Whether root-level nodes have collapse handles.
- Unknown Node Icon (String, .unknownIconPath) — Icon for "Unknown" nodes (rows that didn't match a filter).
- Unknown Node Text (String, .unknownNodeText) — Text for "Unknown" nodes.
- Visible (Boolean, .visible) — If disabled, the component will be hidden.

**Notes**
- The default "Unknown" nodes for date filters are expected until those filters are configured; ignore them until then.
- Only the Data Out table typically needs to be shown in a report window — Data In doesn't require its own visible component.
## Tables
### Comments Panel
Tables — Powers a blog-style comments system, with optional file attachments and "sticky" notes.

**Properties**
- Add Note Text (String, .addNoteText) — Text for the "Add Note" button.
- Attach File Text (String, .attachText) — Text for the "Attach File" link.
- Attachments Enabled (boolean, .attachmentsEnabled) — Whether files can be attached to notes.
- Border (Border, .border) — The border surrounding this component.
- Cancel Text (String, .cancelText) — Text for the "Cancel" button.
- Data (Dataset, .data) — Notes for the desired entity (id, note text, author, timestamp, etc.).
- Database Connection (String, .datasource) — Database connection to run queries against; blank uses the project default.
- Date Format (String, .dateFormat) — Format string for the date of the note.
- Display Mode (int, .displayMode) — Horizontal vs other comment header layout.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Header Color (Color, .headersColor) — Background color of the header notes.
- Maximum Attachment Size (long, .maxAttachmentSize) — Maximum accepted attachment size in bytes.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Note Color (Color, .noteColor) — Background color for notes.
- Padding (int, .padding) — Padding between the notes.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Skip Audit (boolean, .skipAudit) — If true, update queries from this component skip the audit log.
- Sticky Header Color (Color, .stickyHeaderColor) — Background color of the header for sticky notes.
- Sticky Note Color (Color, .stickyNoteColor) — Background color for sticky notes.
- Sticky Text (String, .stickyText) — Text for the "Sticky" checkbox.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this input component responds if touchscreen mode is enabled.
- Touchscreen Keyboard Layout (String, .keyboardName) — Touchscreen keyboard layout to use for this component.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- [ext] insertNote — Called when a note is added.
- [ext] deleteNote — Called when a user clicks 'delete' on a note.
- [ext] unstickNote — Called when a user clicks 'unstick' on a note.
- [ext] downloadAttachment — Called when a user attempts to download an attachment from a note.
- [ext] canDelete — Returns whether a note with a given id can be deleted.

**Notes**
- Default configuration disables all Extension Functions on the component; examples in the docs assume a MySQL-backed schema and may need adaptation.

### List
Tables — Displays a list of options for freeform single or multiple selection.

**Properties**
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The dataset backing the list; if multiple columns, later columns define display text.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Layout Orientation (int, .layoutOrientation) — The orientation of the list elements.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Row Height (int, .rowHeight) — Row height, or -1 for automatic.
- Selected Background (Color, .selectedBackground) — Background color of selected cell(s).
- Selected Focus Border (Border, .selectedFocusBorder) — Border for the selected, focused cell.
- Selected Foreground (Color, .selectedForeground) — Foreground color of selected cell(s).
- Selected Index (int, .selectedIndex) — Index of the selected cell, or -1 if none.
- Selection Mode (int, .selectionMode) — Whether one cell, contiguous, or multiple intervals can be selected.
- Styles (Dataset, .styles) — Contains the component's styles.
- Visible (boolean, .visible) — If disabled, the component will be hidden.
- Visible Row Count (int, .visibleRowCount) — Preferred number of rows to display without scrolling.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- .addSelectionInterval(start, end) — Adds options at indexes start through end to the selection.
- .clearSelection() — Clears the current selection.
- .getSelectedIndices() — Returns the selected indices in increasing order (or empty list).
- .getSelectedValue() — Returns the currently selected value, or None.
- .getSelectedValues() — Returns a list of the currently selected values.
- .isSelectedIndex(index) — Whether the given index is currently selected.
- .isSelectionEmpty() — Whether anything is selected.
- .setSelectedValue(value) — Sets the currently selected value, if found in the list.
- .setSelectedValues(valueList) — Selects multiple options matching the given list.

### Power Table
Tables — A more customizable version of the Table, with drag-and-drop rows, multi-column sorting, column filtering, and cell-spanning.

**Properties**
- Auto Row Height (boolean, .rowResizeEnabled) — Enables automatic row height resizing.
- Auto-Resize Mode (int, .autoResizeMode) — How the table resizes columns.
- Background Color (Color, .background) — The background color of the component.
- Cell Span Data (Dataset, .cellSpanData) — Information about how cells span multiple rows/columns.
- Column Attributes Data (Dataset, .columnAttributesData) — Dataset describing column attributes.
- Column Chooser Menu (boolean, .headerColumnChooserMenus) — Right-click header menu for showing/hiding columns.
- Column Resize Menu (boolean, .headerResizeMenus) — Right-click header menu for resizing columns.
- Column Selection Allowed (boolean, .columnSelectionAllowed) — Used with Row Selection Allowed to control selection granularity.
- Column Sizing (String, .defaultColumnView) — Column sizing/position, preserving user-selected order and widths.
- Columns Re-Orderable (boolean, .columnReorderingAllowed) — Enables reordering columns by dragging headers.
- Columns Resizable (boolean, .columnResizingAllowed) — Enables resizing columns by dragging header margins.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data for this table.
- Edit Click Count (int, .clickCountToStart) — Number of clicks required to start editing a cell.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Grid Line Color (Color, .gridColor) — The color used to draw grid lines.
- Header Font (Font, .headerFont) — Font of the table's header text.
- Header Visible (boolean, .headerVisible) — Allows hiding the table's header.
- Inter Cell Spacing (Dimension, .interCellSpacing) — Space (px) between cells.
- Name (String, .name) — The name of this component.
- Non-Contiguous Selection (boolean, .nonContiguousCellSelection) — Enables non-contiguous cell selection.
- Properties Loading (int, .propertiesLoading) — Number of properties currently being loaded. (Read only.)
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Row Dragging Enabled (boolean, .rowDragEnabled) — Enables drag-and-drop reordering of rows.
- Row Height (int, .rowHeight) — Row height when row resizing is disabled.
- Row Selection Allowed (boolean, .rowSelectionAllowed) — Used with Column Selection Allowed to control selection granularity.
- Selected Column (int, .selectedColumn) — Index of the first selected column, or -1.
- Selected Row (int, .selectedRow) — Index of the first selected row, or -1.
- Selection Background (Color, .selectionBackground) — Default background color of selected cells.
- Selection Foreground (Color, .selectionForeground) — Default foreground color of selected cells.
- Selection Mode (int, .selectionMode) — Whether one row/cell/column, or multiple, can be selected.
- Show Horizontal Grid Lines? (boolean, .showHorizontalLines) — Shows horizontal grid lines.
- Show Vertical Grid Lines? (boolean, .showVerticalLines) — Shows vertical grid lines.
- Sorting Enabled (boolean, .sortingEnabled) — Enables click/Ctrl-click multi-column sorting.
- TestData (boolean, .test) — Fills the table's data with random data.
- View Dataset (Dataset, .viewDataset) — Read-only copy of the data as currently shown on screen (post sort/filter).
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .getSelectedColumns() — Returns the currently selected column indexes.
- .getSelectedRows() — Returns the currently selected row indexes.
- .print([fitWidth][, headerFormat][, footerFormat][, showDialog][, landscape]) — Paginates the table for printing.
- .setColumnWidth(column, width) — Sets a column's width at runtime.
- [ext] configureCell — Configures the contents of each cell; returns a dict of name/value pairs.
- [ext] configureEditor — Configures how each column is edited; returns a dict of name/value pairs.
- [ext] configureHeaderStyle — Configures the style of each column header; returns a dict of name/value pairs.
- [ext] initialize — Called when the window/template containing this table opens/loads.
- [ext] isCellEditable — Returns whether the current cell is editable.
- [ext] onCellEdited — Called when the user has edited a cell; must handle the actual data update.
- [ext] onMousePress / onMouseRelease / onMouseClick / onDoubleClick — Called on the corresponding mouse events over a table cell.
- [ext] onPopupTrigger — Called on right-click on a table cell (build a context menu here).
- [ext] onRowsDropped — Called when rows are dropped on this table (may be from this table or another).

**Notes**
- Even when a column is editable, the actual edit must be handled by onCellEdited; nothing happens if that extension function isn't implemented.
- If onCellEdited causes the Power Table to lose focus (e.g. system.vision.showXxx calls), the cell commit can occur twice.
- Be careful comparing across a table with non-numeric columns — comparisons can give unexpected results.

### Table
Tables — Powerful and easy to configure; flexibly displays tabular data.

**Properties**
- Auto-Resize Mode (int, .autoResizeMode) — How the table resizes columns.
- Background Color (Color, .background) — The background color of the component.
- Background Mode (int, .backgroundColorMode) — The color mode for cell backgrounds.
- Border (Border, .border) — The border surrounding this component.
- Column Attributes Data (Dataset, .columnAttributesData) — Dataset describing column attributes.
- Column Selection Allowed (boolean, .columnSelectionAllowed) — Used with Row Selection Allowed to control selection granularity.
- Cursor (int, .cursorCode) — The mouse cursor to use when hovering over this component.
- Data (Dataset, .data) — The data for this table.
- Edit Click Count (int, .clickCountToStart) — Number of clicks required to start editing a cell.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Foreground Color (Color, .foreground) — The foreground color of the component.
- Grid Line Color (Color, .gridColor) — The color used to draw grid lines.
- Header Font (Font, .headerFont) — Font of the table's header text.
- Header Foreground Color (Color, .headerForeground) — Foreground color of the table's header.
- Header Visible (boolean, .headerVisible) — Whether the table header is visible.
- Initially Selected Row (int, .initialRowSelection) — Index of the row selected by default.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Odd Row Background (Color, .oddBackground) — Color for odd rows when background mode is 'Alternating.'
- Opaque (boolean, .opaque) — If false, backgrounds are not drawn.
- Properties Loading (int, .propertiesLoading) — Number of properties currently being loaded. (Read only.)
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Resizing Allowed (boolean, .resizingAllowed) — Whether users can resize table headers.
- Row Height (int, .rowHeight) — The height of each row, in pixels.
- Row Selection Allowed (boolean, .rowSelectionAllowed) — Used with Column Selection Allowed to control selection granularity.
- Selected Column (int, .selectedColumn) — Index of the first selected column, or -1.
- Selected Row (int, .selectedRow) — Index of the first selected row, or -1.
- Selection Background (Color, .selectionBackground) — Background color of a selected cell.
- Selection Foreground (Color, .selectionForeground) — Foreground color of a selected cell.
- Selection Mode (int, .selectionMode) — Whether one row/cell/column, or multiple, can be selected.
- Show Horizontal Grid Lines? (boolean, .showHorizontalLines) — Shows horizontal grid lines.
- Show Vertical Grid Lines? (boolean, .showVerticalLines) — Shows vertical grid lines.
- TestData (boolean, .test) — Fills the table's data with random data.
- Touchscreen Mode (int, .touchscreenMode) — Controls when this table component responds if touchscreen mode is enabled.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Scripting / extension functions**
- .addRow(newRow) — Adds a new row to the end of the table's dataset.
- .deleteRow(rowIndex) — Deletes a row from the table's dataset.
- .exportCSV(filename, showHeaders) — Prompts the user to save the table's data as a CSV file.
- .getDataAsHTML(title, width) — Creates an HTML page as a string in memory (write to file/db/email).
- .getRowsInViewOrder() — Returns underlying dataset row indexes in current view order (post sort).
- .getSelectedColumn() / .getSelectedColumnCount() — Index/count of currently selected column(s).
- .getSelectedRow() / .getSelectedRows() / .getSelectedRowCount() — Index/list/count of currently selected row(s).
- .isCellSelected(row, column) / .isColumnSelected(column) / .isRowSelected(row) — Whether the given cell/column/row is selected.
- .print(fitWidth, headerFormat, footerFormat, showDialog, landscape) — Paginates the table for printing.
- .setColumnLabel(column, label) — Sets a column's header label at runtime.
- .setColumnSelectionInterval(index0, index1) / .setRowSelectionInterval(index0, index1) — Selects the given range of columns/rows.
- .setColumnWidth(column, width) — Sets a column's width at runtime.
- .setSelectedColumn(column) / .setSelectedRow(row) — Sets the selected column/row.
- .setValue(row, column, value) — Sets a cell's value, altering the Data property (fires propertyChange).
- .sortByColumn(columnName[, asc]) — Sorts the data by the named column.
- .sortOriginal() — Clears custom sort and displays data in its original order.
- .updateRow(rowIndex, changes) — Updates an entire row of the table's dataset.
- [ext] getBackgroundAt / getForegroundAt / getDisplayTextAt — Called per cell to return its background color / foreground color / display text (must not block or run queries).

### Tag Browse Tree
Tables — Similar to the Designer's Tag Browser; browses tags in Designer and Client, and lets tags be dragged onto other components (e.g. the Easy Chart).

**Properties**
- Border (Border, .border) — The border surrounding this component.
- Font (Font, .font) — Font of text on this component.
- Include Historical Tags (boolean, .showHistorical) — Whether to display historical tags.
- Include Realtime Tags (boolean, .showRealtime) — Whether to display non-historical tags.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Root Node Path (String, .rootNodePath) — Path of the root of this tree structure, or "" for none.
- Selected Paths (Dataset, .selectedPaths) — Paths that should be selected on the tree.
- Selection Mode (int, .selectionMode) — What kind of selection regions the tree allows.
- Show Root Handles (boolean, .showRootNodeHandles) — Whether to show handles next to parent nodes.
- Show Root Node (boolean, .showRootNode) — Whether to show the root node of the tree.
- Tag Tree Mode (int, .treeMode) — Whether the tree is built from the default provider or another source.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- [ext] filterTag — Called for each tag loaded into the tree; return false to hide it.
- [ext] createPopupMenu — Returns a popup menu displayed on right-click in the tree.

### Tree View
Tables — Displays any tree hierarchy, configured by filling in a dataset.

**Properties**
- Auto Expand (boolean, .autoExpand) — Automatically expand the tree up to a given depth.
- Auto Expansion Level (int, .autoExpansionLevel) — Depth level to auto-expand, if Auto Expand is true.
- Auto Sort (boolean, .autoSort) — Whether to automatically sort the tree.
- Background Color (Color, .background) — The background color of the component.
- Border (Border, .border) — The border surrounding this component.
- Default Closed Icon (String, .defaultClosedIconPath) — Default closed icon if no icon is set.
- Default Leaf Icon (String, .defaultLeafIconPath) — Default leaf icon if no icon is set.
- Default Node Background (Color, .defaultBackground) — Default node background if none is set.
- Default Node Border (Border, .defaultBorder) — Default node border if none is set.
- Default Node Foreground (Color, .defaultForeground) — Default node foreground if none is set.
- Default Node Selected Background (Color, .defaultSelectedBackground) — Default selected background if none is set.
- Default Node Selected Border (Border, .defaultSelectedBorder) — Default selected border if none is set.
- Default Node Selected Foreground (Color, .defaultSelectedForeground) — Default selected foreground if none is set.
- Default Open Icon (String, .defaultOpenIconPath) — Default open icon if no icon is set.
- Enabled (boolean, .componentEnabled) — If disabled, a component cannot be used.
- Font (Font, .font) — Font of text on this component.
- Full Width Selection (boolean, .fullWidthSelection) — Paints selection across the full width of the tree.
- Items (Dataset, .data) — Contains the items of the tree view.
- Line Style (int, .lineStyle) — The tree's line style.
- Mouseover Text (String, .toolTipText) — Tooltip text shown on mouseover.
- Name (String, .name) — The name of this component.
- Quality (QualityCode, .quality) — Data quality code for any Tag bindings on this component.
- Row Height (int, .rowHeight) — The height of each row in the tree.
- Selected Item (int, .selectedItem) — Index of the currently selected item, or -1.
- Selected Path (String, .selectedPath) — Path of the currently selected item, or "".
- Selection Fill Color (Color, .selectionFillColor) — Background color to fill the selection width with.
- Selection Mode (int, .selectionMode) — What kind of selection regions the tree allows.
- Separation Character (String, .separationCharacter) — Separation character for the path.
- Show Root Handles (boolean, .showRootHandles) — Whether to show handles next to parent nodes.
- Visible (boolean, .visible) — If disabled, the component will be hidden.

**Deprecated properties**
- Data Quality (int, .dataQuality) — The data quality code for any Tag bindings on this component.

**Scripting / extension functions**
- .clearSelection() — Clears the current selection.
- .collapseAll() / .expandAll() — Collapses/expands all nodes in the tree.
- .getSelectedItems() — Returns the selected items' row indexes.
- .getSelectedPaths() — Returns the selected items' paths (parent path plus own name).
## Gotchas and 8.3 notes

- **Vision's status relative to Perspective.** Vision remains a fully supported, first-class Ignition module in 8.3 — it is not deprecated and existing Vision projects keep working — but Inductive Automation's active new-feature investment is concentrated on Perspective. No new Vision component types have been introduced in recent 8.x releases; 8.3-era changes to Vision are mostly maintenance, bug fixes, and small property/behavior additions to existing components rather than new palette entries. Plan new mobile/web-first HMI work in Perspective; keep Vision for existing desktop/kiosk deployments or where Vision-only components (e.g. Report Viewer running Reporting-module reports directly in a window, PDF Viewer, the admin panels) are required.
- **`Data Quality` (int) is deprecated almost everywhere in favor of `Quality` (QualityCode).** Nearly every component in this reference carries a **Deprecated properties** entry for `.dataQuality` (an int) alongside a current `Quality` property (`.quality`, a QualityCode object). Existing scripts/bindings using the int form keep working, but new work should bind/read `Quality` and inspect it via the QualityCode scripting object (see Scripting Object Reference) rather than comparing raw ints.
- **Extension functions are no-ops until you touch them.** Every extension function (marked `[ext]` above) ships disabled — e.g. the Button's page explicitly notes "this component does not have any extension functions associated with it" until code is added via right-click → Scripting → \<function\>. For components like the Power Table, this is a real trap: setting a column "editable" does *nothing* unless you also implement `onCellEdited` to write the change back into the bound Dataset.
- **Table edits are never automatic.** For Table and Power Table, marking a column editable only lets the user type into a cell — the component does not mutate its `Data`/bound dataset itself. You must implement `onCellEdited` (Power Table) or otherwise update the data yourself; skipping this silently discards edits.
- **`configureChart`/`configureCell`/etc. extension functions must not block.** Chart, cell-rendering, and similar per-item extension functions (`getBackgroundAt`, `getForegroundAt`, `getDisplayTextAt` on Table; `configureCell` on Power Table) run on the UI thread for every cell/item — the docs explicitly warn not to block, sleep, or run queries inside them, since that will freeze the UI.
- **Losing focus during a cell-edit callback can double-commit.** The Power Table docs call out that if an `onCellEdited` script itself causes the table to lose focus (e.g. by calling `system.vision.showXxx` from inside the handler), the cell's edit can commit twice — worth guarding against with idempotent update logic.
- **Generic events are documented once, not per component.** Nearly every component's Scripting section just links to the shared Component Events page rather than listing `mouseClicked`, `propertyChange`, etc. again — this reference follows the same convention (see "Event handlers vs. extension functions" above) rather than repeating the same event list under all 77 components.
- **Windows fire event handlers in a specific, easy-to-get-wrong order.** On open: `visionWindowOpened` (before bindings evaluate) → `internalFrameOpened` (skipped on a cached re-open) → `internalFrameActivated` (re-fires on refocus). On close: `internalFrameClosing` (window still technically open — do cleanup here) → `visionWindowClosed` → `internalFrameDeactivated` (also fires on plain focus loss, not just closing) → `internalFrameClosed`. Putting cleanup logic in the wrong one of these is a common source of bugs.
- **Window `Cache Policy` changes correctness, not just performance.** `Auto` (default) keeps a closed window's bindings/scripts suspended in memory for fast reopen; `Never` deserializes a fresh copy every open (handy to reset a data-entry screen's leftover values); `Always` keeps it permanently cached (fastest, but memory scales with how many large windows you do this to).
- **Live-docs data quality caveat:** the Template Repeater page's frontmatter/summary description on the live 8.3 docs is mis-copied from the Report Viewer page (`"The Report Viewer component provides a way to run and view Reports in Vision windows."` used as the Template Repeater's one-line description). This reference uses the Template Repeater's actual body text instead — worth knowing if you diff against the raw page.
- **Touchscreen Mode is pervasive but component-specific.** Most input-family and several table/alarm components expose a `Touchscreen Mode` property (and sometimes a `Touchscreen Keyboard Layout`) controlling whether/when an on-screen keyboard or touch-specific interaction kicks in — it's not a single global setting, so it must be configured per component if you're targeting touch panels.
- **Deprecated ≠ removed.** Deprecated properties (chiefly the `Data Quality` int pattern above, plus a handful of component-specific ones like the Button/One-Shot Button/2 State Toggle's `Opaque`) still function in 8.3 for backward compatibility with pre-existing projects; they're simply hidden from "recommended" documentation/UI guidance and shouldn't be used in new work.
- **Scripting names are the source of truth for code, not the display names.** The Property Editor shows friendly names ("Foreground Color"), but scripts must use the dotted scripting name (`.foreground`) — the tables above list both explicitly (`Display Name (Type, .scriptingName) — note`) since the two often diverge (e.g. Table's "Odd Row Background" is `.oddBackground`; Tab Strip's "Text Offset" has no scripting name documented at all on its page).
