# Ignition 8.3 — Platform scripting functions (alarm, user, roster, security, groups, eam, net, file, report, twilio, sfc, eventstream)

This reference covers the Ignition 8.3 platform scripting namespaces that manage alarms, identity/user data, scheduling, gateway networking, host file I/O, reporting, SMS/voice/WhatsApp messaging (Twilio), Sequential Function Charts, and the new Event Streams module. These are mostly Gateway-administration and integration APIs rather than UI-building APIs: most of them touch server-side resources (user sources, rosters, the Gateway file system, remote Gateways, external services) and many are restricted to specific scopes. Ignition 8.3 significantly reworked how authentication works when the Perspective module is installed — see `system.security`/`system.user` vs. Perspective auth below and the Gotchas section — and introduced the Event Streams module (`system.eventstream`) as a new unifying construct for event-driven data handling. Signatures below list every published overload; parameter descriptions are trimmed to fit — see the live docs for full text and code samples.

## system.alarm

Alarm querying, acknowledgement, and shelving against the Alarming system, plus a legacy alarm-notification "Roster" API. Use `queryStatus` for current alarm state and `queryJournal` for historical events — they return similarly-shaped `AlarmQueryResult`/`PyAlarmEvent` objects but are not interchangeable (journal splits active/ack/clear into separate rows; status combines them). `system.alarm.createRoster`/`getRosters` are the **Vision-only** counterparts to `system.roster`'s Gateway/Perspective versions — see Gotchas.

### system.alarm.acknowledge
`system.alarm.acknowledge(alarmIds, [notes])`
`system.alarm.acknowledge(alarmIds, notes, username)`

Acknowledges any number of alarms, specified by their event ids. The event id is generated for an alarm when it becomes active, and it is used to identify a particular event from other events for the same source. The alarms will be acknowledged by the logged…

**Syntax - Client Scripts**
**Params:** String[] alarmIds — List of alarm event ids (uuids) to acknowledge.; String notes — A string that will be used as the Ack Note on each acknowledged alarm event. If set to No…
**Returns:** List[String] `almIds` - List of alarm event ids (UUIDs) that were unable to be acknowledged successfully.
**Scope:** Vision Client

**Syntax - Gateway Scripts**
**Params:** List[String] alarmIds — List of alarm event ids (UUIDs) to acknowledge.; String notes — A string that will be used as the Ack Note on each acknowledged alarm event. If set to No…; String username — The user that acknowledged the alarm.
**Returns:** List[String] `almIds` - List of alarm event ids (UUIDs) that were unable to be acknowledged successfully.
**Scope:** Gateway, Perspective Session

### system.alarm.cancel
`system.alarm.cancel(alarmIds)`

Cancels any number of alarm pipelines, specified by their event ids. Event ids can be obtains from the system.alarm.queryStatus function. Canceling a pipeline will not impact the alarm that triggered the pipeline. The alarm will still be active, but will drop…

**Params:** List[String] alarmIds — List of alarm pipeline event ids (UUIDs) to cancel.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.createRoster
`system.alarm.createRoster(name, description)`

This function creates a new roster. Users may be added to the roster through the Gateway or the Roster Management component

**Params:** String name — The name for the new roster; String description — A description for the new roster. Required, but can be blank.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.getRosters
`system.alarm.getRosters()`

This function returns a mapping of roster names to a list of usernames contained in the roster.

**Params:** none
**Returns:** Dictionary[String, List[String]] - A dictionary that maps roster names to a list of usernames in the roster. The list of usernames will be empty if n…
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.getShelvedPaths
`system.alarm.getShelvedPaths()`

Returns a list of ShelvedPath objects, which each represent a shelved alarm.

**Params:** none
**Returns:** List[ShelvedPath] - A list of ShelvedPath objects. See Scripting Object Reference.
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.listPipelines
`system.alarm.listPipelines([projectName])`

Will return a list of the available Alarm Notification Pipelines in a project. The order of the returned list is not guaranteed.

**Params:** String projectName — The project to check alarm pipelines for. If omitted, will look for a project named "alar… (opt)
**Returns:** List[String] - A list of pipeline names. The list will be empty if no pipelines exist. Unsaved name changes will not be reflected in the list.
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.queryJournal
`system.alarm.queryJournal([startDate], [endDate], [journalName], [priority], [state], [path], [source], [displaypath], [all_properties], [any_properties], [defined], [includeData], [includeSystem], [includeShelved], [isSystem], [provider])`

Queries the specified journal for historical alarm events. The result is a list of alarm events, which can be parsed for individual properties. Click here for more information on alarm properties.

**Params:** Date startDate — The start of the time range to query. Defaults to 8 hours previous to now if omitted. Tim… (opt); Date endDate — The end of the time range to query. Defaults to "now" if omitted. (opt); String journalName — The journal name to query. If only one journal exists on the Gateway, can be omitted. (opt); List[Integer / String] priority — A list of possible priorities to match. Priorities can be specified by name or number, wi… (opt); List[Integer / String] state — A list of event states to match. Valid values can either be integers or strings, represen… (opt); List[String] path — A list of possible source paths to search at. The wildcard "*" may be used. (opt); List[String] source — A list of possible source paths to search at. The wildcard "*" may be used. (opt); List[String] displaypath — A list of display paths to search at. Display paths are separated by "/", and if a path e… (opt); List[Tuple[String, String, Any]] all_properties — A set of property conditions, all of which must be met for the condition to pass. This pa… (opt); List[Tuple[String, String, Any]] any_properties — A set of property conditions, any of which will cause the overall condition to pass. This… (opt); List[String] defined — A list of string property names, all of which must be present on an event for it to pass. (opt); Boolean includeData — Whether or not event data should be included in the return. If True, returns Python dicti… (opt); Boolean includeSystem — Specifies whether system events are included in the return. (opt); Boolean includeShelved — A flag indicating whether shelved events should be included in the results. Defaults to f… (opt); Boolean isSystem — Specifies whether the returned event must or must not be a system event. (opt); List[String] provider — A list of tag providers to include in the query. Omitting this parameter will query all p… (opt)
**Returns:** AlarmQueryResult - The AlarmQueryResult object is a list of PyAlarmEvent objects. See Scripting Object Reference. Additionally, each PyAlarmEvent ins…
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.queryStatus
`system.alarm.queryStatus([priority], [state], [path], [source], [displaypath], [all_properties], [any_properties], [defined], [includeShelved], [provider])`

Queries the current state of alarms. The result is a list of alarm events, which can be parsed for individual properties. The results provided by this function represent the current state of alarms, in contrast to the historical alarm events retrieved by the…

**Params:** List[Integer / String] priority — A list of possible priorities to match. Priorities can be specified by name or number, wi… (opt); List[Integer / String] state — A list of states to allow. See State Values for a list of options. (opt); List[String] path — A list of possible source paths to search at. The wildcard "*" may be used. Works the sam… (opt); List[String] source — A list of possible source paths to search at. The wildcard "*" may be used. Works the sam… (opt); List[String] displaypath — A list of display paths to search at. Display paths are separated by "/", and if a path e… (opt); List[Tuple[String, String, Any] all_properties — A set of property conditions, all of which must be met for the condition to pass. This pa… (opt); List[Tuple[String, String, Any] any_properties — A set of property conditions, any of which will cause the overall condition to pass. This… (opt); List[String] defined — A list of string property names, all of which must be present on an event for it to pass. (opt); Boolean includeShelved — A flag indicating whether shelved events should be included in the results. Defaults to f… (opt); List[String] provider — A list of tag providers to include in the query. Omitting this parameter will query all p… (opt)
**Returns:** AlarmQueryResult - The AlarmQueryResult object is a list of PyAlarmEvent objects with some additional helper methods, see Scripting Object Reference.…
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.shelve
`system.alarm.shelve(path, [timeoutSeconds], [timeoutMinutes])`

This function shelves the specified alarms for the specified amount of time. The time can be specified in minutes (timeoutMinutes) or seconds (timeoutSeconds). If an alarm is already shelved, this will overwrite the remaining time. If no timeout is specified,…

**Params:** List[String] path — A list of possible source paths to search at. If a path ends in "/*", the results will in…; Integer timeoutSeconds — The amount of time to shelve the matching alarms for, specified in seconds. Setting this… (opt); Integer timeoutMinutes — The amount of time to shelve the matching alarms for, specified in minutes. Setting this… (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.alarm.unshelve
`system.alarm.unshelve(path)`

Unshelves a list of alarms based on the source paths provided.

**Params:** List[String] path — A list of possible source paths to search at. If a path ends in "/*", the results will in…
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session
## system.user

Manages Users, Roles, Schedules (including Composite Schedules and one-off Schedule Adjustments), and Holidays stored in a **User Source** — the data backing Ignition's Classic Authentication Strategy. In 8.3, when the Perspective module is installed, a Perspective Session's own login is handled by the **Identity Provider (IdP) Authentication Strategy** instead (see Gotchas) — `system.user` still manages the underlying User Source records used by Vision/Designer auth, Gateway-side role/schedule lookups, and data an IdP's "User Attribute Mapping" can read from. Nearly every mutating call (`addUser`, `editUser`, `addRole`, …) returns a **UIResponse** with `getErrors()`/`getWarns()`/`getInfos()` instead of raising on partial failure — always check it. Editing the built-in Gateway System User Source requires "Allow User Admin" to be enabled on that profile.

### system.user.addCompositeSchedule
`system.user.addCompositeSchedule(name, scheduleOne, scheduleTwo, [description])`

Allows two schedules to be combined into a composite schedule.

**Params:** String name — The name of the new composite schedule.; String scheduleOne — The first schedule to combine.; String scheduleTwo — The second schedule to combine.; String description — Description of the new combined schedule. (opt)
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the add. The contents of the lists are acce…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.addHoliday
`system.user.addHoliday(holiday)`

Allows a holiday to be added.

**Params:** HolidayModel holiday — The holiday to add, as a HolidayModel object.
**Returns:** UIResponse - A UIResponse object with lists of warning, errors and info about the success or failure of the add. The contents of the lists are access…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.addRole
`system.user.addRole(userSource, role)`

Adds a role to the specified user source. When altering the Gateway System User Source, the Allow User Admin setting must be enabled.

**Params:** String userSource — The user source to add a role to. Blank will use the default user source.; String role — The role to add. Role must not be blank and must not already exist.
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the add. The contents of the lists are acce…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.addSchedule
`system.user.addSchedule(schedule)`

Adds a schedule.

**Params:** ScheduleModel schedule — The schedule to add. Can be a BasicScheduleModel or CompositeScheduleModel object (or any…
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the add. The contents of the lists are acce…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.addUser
`system.user.addUser(userSource, user)`

Adds a new user to a user source. Used in combination with getNewUser to create new user.

**Params:** String userSource — The user source to add a user to. If set to an empty string, the function will attempt to…; User user — The user to add, as a User object. Refer also to the PyUser class.
**Returns:** UIResponse - A UIResponse object which contains lists of the errors, warnings, and information returned after the add attempt. The contents of the li…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.createScheduleAdjustment
`system.user.createScheduleAdjustment(startDate, endDate, isAvailable, note)`

Creates a schedule adjustment.

**Params:** Date startDate — The starting date of the schedule adjustment.; Date endDate — The ending date of the schedule adjustment.; Boolean isAvailable — True if the user is available during this schedule adjustment.; String note — A note about the schedule adjustment.
**Returns:** Schedule Adjustment - A ScheduleAdjustment object that can be added to a user.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.editHoliday
`system.user.editHoliday(holidayName, holiday)`

Allows a holiday to be edited.

**Params:** String holidayName — The name of the holiday to edit. Name is case-sensitive.; HolidayModel holiday — The edited holiday, as a HolidayModel object.
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the edit. The contents of the lists are acc…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.editRole
`system.user.editRole(userSource, oldName, newName)`

Renames a role in the specified user source. When altering the Gateway System User Source, the Allow User Admin setting must be enabled.

**Params:** String userSource — The user source in which the role is found. Blank will use the default user source.; String oldName — The role to edit. Role must not be blank and must exist.; String newName — The new name for the role. Must not be blank.
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the edit. The contents of the lists are acc…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.editSchedule
`system.user.editSchedule(scheduleName, schedule)`

Allows a schedule to be edited.

**Params:** String scheduleName — The name of the schedule to edit. Name is case-sensitive.; ScheduleModel schedule — The schedule to add. Can be a BasicScheduleModel or CompositeScheduleModel object (or any…
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and info about the success or failure of the edit. The contents of the lists are acc…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.editUser
`system.user.editUser(userSource, user)`

Alters a specific user in a user source, replacing the previous data with the new data passed in.

**Params:** String userSource — The user source in which the user is found. Blank will use the default user source.; User user — The user to update, as a User object. Refer also to the PyUser class.
**Returns:** A UIResponse object with lists of warnings, errors, and information returned after the edit attempt. The contents of the lists are accessible from th…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getHoliday
`system.user.getHoliday(holidayName)`

Returns a specific holiday.

**Params:** String holidayName — The name of the holiday to return. Case-sensitive
**Returns:** HolidayModel - The holiday, as a HolidayModel object, or None if not found. Add holidays using the system.user.addHoliday function.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getHolidayNames
`system.user.getHolidayNames()`

Returns a collection of Strings of all holiday names.

**Params:** none
**Returns:** List - A list of all holiday names, or an empty list if no holidays are defined. Add holidays using the system.user.addHoliday function.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getHolidays
`system.user.getHolidays()`

Returns a sequence of all of the holidays available.

**Params:** none
**Returns:** List - A list of holidays, as HolidayModel objects. Add holidays using the system.user.addHoliday function.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getNewUser
`system.user.getNewUser(userSource, username)`

Creates a new user object. The user will not be added to the user source until addUser is called.

**Params:** String userSource — The name of the user source in which to create a user.; String username — The username for the new user. Does not check if the username already exists or is valid.
**Returns:** User - The new user, as a User object. Refer also to the PyUser class.
**Scope:** Gateway, Vision Client, Perspective Session
### system.user.getRoles
`system.user.getRoles(userSource)`

Returns a sequence of strings representing all of the roles configured in a specific user source.

**Params:** String userSource — The user source to fetch the roles for.
**Returns:** List - A List of strings that holds all the roles in the user source.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getSchedule
`system.user.getSchedule(scheduleName)`

Returns a specific schedule.

**Params:** String scheduleName — The name of the schedule to return. Case-sensitive
**Returns:** ScheduleModel - The schedule, which can be a BasicScheduleModel object, CompositeScheduleModel object, or another type registered by a module. If a s…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getScheduleNames
`system.user.getScheduleNames()`

Returns a sequence of strings representing the names of all of the schedules available.

**Params:** none
**Returns:** List - A List of Strings that holds the names of all the available schedules.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getScheduledUsers
`system.user.getScheduledUsers(userSource, [date])`

Returns a list of users that are scheduled. If no users are scheduled, it will return an empty list.

**Params:** String userSource — The name of the user source to check for scheduled users.; Date date — The date to check schedules for. May be a Java Date or Unix Time in ms. If omitted, the c… (opt)
**Returns:** List - List of all users (as User objects) scheduled for the given date, taking schedule adjustments into account. Refer also to the PyUser class.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getSchedules
`system.user.getSchedules()`

Returns a sequence of all available schedule models, which can be used to return configuration information on the schedule, such as time for each day of the week.

**Params:** none
**Returns:** List - A list of schedules. Each schedule can be a BasicScheduleModel object, CompositeScheduleModel object, or another type registered by a module.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getUser
`system.user.getUser(userSource, username)`

Looks up a specific user in a user source, by username. The full User object is returned except for the user's password.

**Params:** String userSource — The name of the user source to search for the user in. Can be a blank string to use the V…; String username — The username of the user to search for.
**Returns:** User - The user, as a User object.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getUserSources
`system.user.getUserSources()`

Returns a sequence of objects representing all of the user source profiles configured in the Gateway. Each object has a "name" property, a "description" property, and a "type" property.

**Params:** none
**Returns:** List - A List of all user source profiles configured in the system in ascending order by their names.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.getUsers
`system.user.getUsers(userSource)`

Retrieves the list of users in a specific user source. The "User" objects that are returned contain all of the information about that user, except for the user's password.

**Params:** String userSource — The name of the user source to find the users in.
**Returns:** List - A List of User objects.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.isUserScheduled
`system.user.isUserScheduled(user, [date])`

Will check if a specified User is scheduled currently or on a specified date/time.

**Params:** User user — The user object to check the schedule for.; Date / Integer date — The date to check schedules for. May be a Java Date or Unix Time in ms. If omitted, the c… (opt)
**Returns:** Boolean - True if the user is scheduled for the specified date; false if not.
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.removeHoliday
`system.user.removeHoliday(holidayName)`

Allows a holiday to be deleted.

**Params:** String holidayName — The name of the holiday to delete. Case-sensitive.
**Returns:** UIResponse - A list of UIResponse objects with lists of warnings, errors, and info about the success or failure of the deletion. The contents of the…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.removeRole
`system.user.removeRole(userSource, role)`

Removes a role from the specified user source. When altering the Gateway System User Source, the Allow User Admin setting must be enabled.

**Params:** String userSource — The user source in which the role is found. Blank will use the default user source.; String role — The role to remove. The role must exist.
**Returns:** UIResponse - A list of UIResponse objects with lists of warnings, errors, and info about the success or failure of the deletion. The contents of the…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.removeSchedule
`system.user.removeSchedule(scheduleName)`

Allows a schedule to be deleted. Note that schedules which are used in Composite Schedules can not be deleted until they are removed from the Composite Schedule.

**Params:** String scheduleName — The name of the schedule to delete. Case-sensitive.
**Returns:** UIResponse - A list of UIResponse objects with lists of warnings, errors, and info about the success or failure of the deletion. The contents of the…
**Scope:** Gateway, Vision Client, Perspective Session

### system.user.removeUser
`system.user.removeUser(userSource, username)`

Removes a specific user from the a user source based on username. When altering the Gateway System User Source, the Allow User Admin setting must be enabled.

**Params:** String userSource — The user source in which the user is found. Blank will use the default user source.; String username — The username of the user to remove.
**Returns:** UIResponse - A UIResponse object with lists of warnings, errors, and information returned after the removal attempt. The contents of the lists are ac…
**Scope:** Gateway, Vision Client, Perspective Session
## system.roster

The Gateway/Perspective-native roster API — rosters are named lists of `User` objects (e.g., for on-call/notification lists), functionally parallel to `system.alarm`'s roster functions but scoped to **Gateway and Perspective Session only**. The docs explicitly say to use `system.alarm.createRoster`/`getRosters` instead from a **Vision Client** — the two roster APIs manage the same underlying concept but are not scope-interchangeable (see Gotchas).

### system.roster.addUsers
`system.roster.addUsers(rosterName, [users])`

Adds a list of users to an existing roster. Users are always appended to the end of the roster.

**Params:** String rosterName — The name of the roster to modify.; List users — A list of User objects that will be added to the end of the roster. User objects can be c…
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

### system.roster.createRoster
`system.roster.createRoster(name, description)`

This function was designed to run in the Gateway and in Perspective sessions. If creating rosters from Vision clients, use system.alarm.createRoster instead

**Params:** String name — The name of the roster to create.; String description — The description for the roster. May be None, but the parameter is mandatory.
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

### system.roster.deleteRoster
`system.roster.deleteRoster(rosterName)`

Deletes a roster with the given name.

**Params:** String name — The name of the roster to delete.
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

### system.roster.getRoster
`system.roster.getRoster(rosterName)`

Returns the roster corresponding to the given name. You can call getUsers() to access a list of User objects in the RosterModel. Call getDescription() to access the Description field of the specified roster.

**Params:** String name — The name of the roster to get the RosterModel object from.
**Returns:** RosterModel - The RosterModel object of the given roster name.
**Scope:** Gateway, Perspective Session

### system.roster.getRosterNames
`system.roster.getRosterNames()`

Returns a list of roster names.

**Params:** none
**Returns:** List[String] - List of rosters on the Gateway.
**Scope:** Gateway, Perspective Session

### system.roster.getRosters
`system.roster.getRosters()`

This function was designed to run in the Gateway and in Perspective sessions. If creating rosters from Vision clients, use system.alarm.getRosters instead.

**Params:** none
**Returns:** Dictionary[String, List[String]] - A dictionary that maps roster names to a list of usernames in the roster. The list of usernames may be empty if no…
**Scope:** Gateway, Perspective Session

### system.roster.getUsers
`system.roster.getUsers(rosterName)`

Returns the list of users corresponding to the given rosterName.

**Params:** String rosterName — The name of the roster to get a list of users from.
**Returns:** List[String] - List of users within the specified roster.
**Scope:** Gateway, Perspective Session

### system.roster.removeUsers
`system.roster.removeUsers(rosterName, users)`

Removes one or more users from an existing roster.

**Params:** String rosterName — The name of the roster to modify.; List users — A list of User objects that will be removed from the roster. User objects can be created…
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

## system.security

Only two functions: `getUserRoles` and `validateUser`, both of which test a username/password against a named **authentication profile** (a Classic Authentication Strategy user source), returning roles or a pass/fail boolean. Useful for a script-driven "re-authenticate this specific user" or "check someone else's credentials" pattern — **not** for reading who is logged into the current Perspective Session or driving Perspective's own login (that's the IdP strategy and `system.perspective.login`/`logout`/`isAuthorized`, which are out of scope for this reference — see Gotchas).

### system.security.getUserRoles
`system.security.getUserRoles(username, password, [authProfile], [timeout])`
`system.security.getUserRoles(username, password, [authProfile])`

Fetches the roles for a user from the Gateway. This may not be the currently logged in user. Requires the password for that user. If the authentication profile name is omitted, then the current project's default authentication profile is used.

**Syntax - Vision**
**Params:** String username — The username to fetch roles for; String password — The password for the user; String authProfile — The name of the authentication profile to run against. Optional. Leaving this out will us… (opt); Integer timeout — Timeout for client-to-gateway communication. Default is 60,000ms. (opt)
**Returns:** Tuple - A list of the roles that this user has, if the user authenticates successfully. Otherwise, returns None.
**Scope:** Vision Client

**Syntax - Gateway and Perspective**
**Params:** String username — The username to fetch roles for.; String password — The password for the user.; String authProfile — The name of the authentication profile to run against. Leaving this out will use the proj… (opt)
**Returns:** Tuple - A list of the roles that this user has, if the user authenticates successfully. Otherwise, returns None.
**Scope:** Gateway, Perspective Session

### system.security.validateUser
`system.security.validateUser(username, password, [authProfile], [timeout])`
`system.security.validateUser(username, password, [authProfile])`

Tests credentials (username and password) against an authentication profile. Returns a boolean based upon whether or not the authentication profile accepts the credentials. If the authentication profile name is omitted, then the current project's default auth…

**Syntax (Client)**
**Params:** String username — The username to validate; String password — The password for the user; String authProfile — The name of the authentication profile to run against. Leaving this out will use the proj… (opt); Integer timeout — Timeout for Client-to-Gateway communication. Default is 60,000ms. (opt)
**Returns:** Boolean - False if the user failed to authenticate; True if the username/password was a valid combination.
**Scope:** Vision Client

**Syntax (Gateway)**
**Params:** String username — The username to validate.; String password — The password for the user.; String authProfile — The name of the authentication profile to run against. Optional. Leaving this out will us… (opt)
**Returns:** Boolean - False if the user failed to authenticate; True if the username/password was a valid combination.
**Scope:** Gateway, Perspective Session

## system.groups

Legacy SQL Bridge **Transaction Groups** management — just two functions for bulk-loading a group configuration from an XML/CSV export (`loadFromFile`) and removing groups by path (`removeGroups`). The small surface area reflects Transaction Groups being a maintenance-mode legacy feature by 8.3, not an area of new investment.

### system.groups.loadFromFile
`system.groups.loadFromFile(filePath, projectName, mode)`

Loads a transaction group configuration from an xml export, into the specified project (creating the project if necessary). The mode parameter dictates how overwrites occur.

**Params:** String filePath — The path to a valid transaction group xml or csv file.; String projectName — The name of the project to load into.; int mode — How duplicates will be handled. 0 = Overwrite, 1 = Ignore, 2 = Replace the existing proje…
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

### system.groups.removeGroups
`system.groups.removeGroups(projectName, paths)`

Removes the specified groups from the project. The group paths are `Folder/Path/To/GroupName`, separated by forward slashes.

**Params:** String projectName — The project to remove from. If the project does not exist, throws an IllegalArgumentExcep…; List[String] paths — A list of paths to remove. Group paths are the full path to the resource, separated by fo…
**Returns:** Nothing
**Scope:** Gateway, Perspective Session

## system.eam

Enterprise Administration Module scripting — query and control remote **Agent** Gateways from the **Controller** Gateway. Every function in this namespace is Controller-only and throws if called from an Agent Gateway; there is no scripting equivalent for an Agent to call back into the Controller.

### system.eam.getGroups
`system.eam.getGroups()`

Returns the names of the defined agent organizational groups in the Gateway. This function can only be called from the Controller. If called from an Agent, this function will return an exception.

**Params:** none
**Returns:** A list of group names.
**Scope:** Gateway, Vision Client, Perspective Session

### system.eam.queryAgentHistory
`system.eam.queryAgentHistory(groupIds, agentIds, startDate, endDate, limit)`

Returns a list of the most recent agent events. This function can only be called from the Controller. If called from an Agent, this function will return an exception.

**Params:** List groupIds — A list of groups to restrict the results to. If not specified, all groups will be include…; List agentIds — A list of agent names to restrict the results to. If not specified, all agents will be al…; Date startDate — The starting time for history events. If null, defaults to 8 hours previous to now.; Date endDate — The ending time for the query range. If null, defaults to "now".; int limit — The limit of results to return. Defaults to 100. A value of 0 means "no limit".
**Returns:** Dataset - A dataset with columns id, agent_name, agent_role, event_time, event_category, event_type, event_source, event_level, event_level_int, and…
**Scope:** Gateway, Vision Client, Perspective Session

### system.eam.queryAgentStatus
`system.eam.queryAgentStatus(groupIds, agentIds, isConnected)`

Returns the current state of the matching agents. This function can only be called from the Controller. If called from an Agent, this function will return an exception.

**Params:** List groupIds — A list of groups to restrict the results to. If not specified, all groups will be include…; List agentIds — A list of agent names to restrict the results to. If not specified, all agents will be al…; Boolean isConnected — If True, only returns agents that are currently connected. If False, only agents that are…
**Returns:** Dataset - A dataset with columns AgentName, NodeRole, AgentGroup, LastCommunication, IsConnected, IsRunning, RunningState, RunningStateInt, LicenseKe…
**Scope:** Gateway, Vision Client, Perspective Session

### system.eam.runTask
`system.eam.runTask(taskname)`

Takes the name of a task as an argument as a string (must be configured on the Controller before hand), attempts to execute the task. This function can only be called from the Controller. If called from an Agent, this function will return an exception. To run…

**Params:** String taskname — Name of the task to run. If more than one task has this name, an error will be returned.
**Returns:** A `UIResponse` with a list of infos, errors, and warnings. The UIResponse object is functionally a list of runTask objects.
**Scope:** Gateway, Vision Client, Perspective Session
## system.net

Networking utilities: local hostname/IP lookup, discovering visible Gateway Network servers, a general-purpose `system.net.httpClient` wrapper around Java's `HttpClient`, and `system.net.sendEmail`. Email is always relayed through the Gateway, so a Vision Client machine needs no direct network path to the SMTP server. `httpClient` instances are explicitly flagged as heavyweight — see Gotchas before creating one per call.

### system.net.getHostName
`system.net.getHostName()`

Returns the host name of the computer that the script was ran on. When run in the Gateway scope, returns the Gateway hostname. When run in the Client scope, returns the Client hostname. On Windows, this is typically the "computer name."

**Params:** none
**Returns:** String - The hostname of the local machine.
**Scope:** Gateway, Vision Client, Perspective Session

### system.net.getIpAddress
`system.net.getIpAddress()`

Returns the IP address of the computer that the script was ran on. When run in the Gateway scope, returns the Gateway IP address. When run in the Client scope, returns the Client IP address.

**Params:** none
**Returns:** String - Returns the IP address of the local machine, as it sees it.
**Scope:** Gateway, Vision Client, Perspective Session

### system.net.getRemoteServers
`system.net.getRemoteServers([runningOnly])`

This function returns a list of Gateway Network servers that are visible from the local Gateway.

**Params:** Boolean runningOnly — If set to true, only servers on the Gateway Network that are running will be returned. Se… (opt)
**Returns:** List[String] - A list of strings representing Gateway Network server IDs.
**Scope:** Gateway, Vision Client, Perspective Session

### system.net.httpClient
`system.net.httpClient([timeout], [bypass_cert_validation], [username], [password], [proxy], [cookie_policy], [redirect_policy], [version], [customizer])`

Provides a general use object that can be used to send and receive HTTP requests. The object created by this function is a wrapper around Java's HttpClient class. Usage requires creating a `JythonHttpClient` object with a call to `system.net.httpClient`, then calling one of its methods to send a request.

**Params:** Integer timeout — A value, in milliseconds, to set the client's connect timeout setting to. Defaults to 100… (opt); Boolean bypass_cert_validation — A boolean indicating whether the client should attempt to validate the certificates of re… (opt); String username — A string indicating the username to use for authentication if the remote server requests… (opt); String password — A string indicating the password to use for authentication. Defaults to None. (opt); String proxy — The address of a proxy server, which will be used for HTTP and HTTPS traffic. If a port i… (opt); String cookie_policy — A string representing this client's cookie policy. Accepts values "ACCEPT_ALL", "ACCEPT_N…; String redirect_policy — A string representing this client's redirect policy. Acceptable values are listed below.… (opt); String version — A string specifying either HTTP_2 or HTTP_1_1 for the HTTP protocol version. (opt); Callable customizer — A reference to a function. This function will be called with one argument (an instance of… (opt)
**Returns:** JythonHttpClient - An object wrapped around an instance of Java's HttpClient class. The httpClient object has methods that can be called to execute H…
**Scope:** Gateway, Vision Client, Perspective Session
**Note:** [caution] Be aware that httpClient instances are heavyweight, so they should be created sparingly and reused as much as possible. For ease of reuse, consider instantiating a new httpClient at the module level and reusing it across script calls.

### system.net.sendEmail
`system.net.sendEmail(smtp, fromAddr, [subject], [body], [html], to, [attachmentNames], [attachmentData], [timeout], [username], [password], [priority], [smtpProfile], [cc], [bcc], [retries], [replyTo])`

Sends an email through the given SMTP server. Note that this email is relayed first through the Gateway; the Client host machine doesn't need network access to the SMTP server. You can use this function to send emails as text messages via most phone service SMS gateways.

**Params:** String smtp — The address of an SMTP server to send the email through, like `mail.example.com`. A port…; String fromAddr — An email address to have the email come from.; String subject — The subject line for the email. (opt); String body — The body text of the email. (opt); Boolean html — A flag indicating whether or not to send the email as an HTML email. Will auto-detect if… (opt); List[String] to — A list of email addresses to send to. Note: This parameter becomes optional if either the…; List[String] attachmentNames — A list of attachment names. Attachment names must have the correct extension for the file… (opt); List[Byte] attachmentData — A list of attachment data, in binary format. (opt); Integer timeout — A timeout for the email, specified in milliseconds. Defaults to 300,000 milliseconds (5 m… (opt); String username — If specified, will be used to authenticate with the SMTP host. (opt); String password — If specified, will be used to authenticate with the SMTP host. (opt); String priority — Priority for the message, from "1" to "5", with "1" being highest priority. Defaults to "… (opt); String smtpProfile — If specified, the named SMTP profile defined in the Gateway will be used. If this keyword… (opt); List[String] cc — A list of email addresses to carbon copy. Only available if an smtpProfile is used. (opt); List[String] bcc — A list of email addresses to blind carbon copy. Only available if an smtpProfile is used. (opt); Integer retries — The number of additional times to retry sending on failure. Defaults to 0. Only available… (opt); List[String] replyTo — An optional list of addresses to have the recipients reply to. If omitted, this defaults… (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

## system.file

Basic file I/O: existence checks, temp files, and reading/writing bytes or strings. **Scope trap:** every function lists the identical scope line "Gateway, Vision Client, Perspective Session," but the filesystem it actually touches differs by scope. From a Gateway script *or* a Perspective Session script, the path resolves against the **Gateway host's filesystem**, because all Perspective session scripts execute server-side on the Gateway. From a Vision Client script, the path resolves against the **local desktop machine's filesystem**. A path that works from Perspective will not exist on the end user's PC, and vice versa — this is called out explicitly on `writeFile`'s doc page and applies to the whole namespace.

### system.file.fileExists
`system.file.fileExists(filepath)`

Checks to see if a file or folder at a given path exists.

**Params:** String filepath — The path of the file or folder to check.
**Returns:** Boolean - True if the file/folder exists, false otherwise.
**Scope:** Gateway, Vision Client, Perspective Session

### system.file.getTempFile
`system.file.getTempFile(extension)`

Creates a new temp file on the host machine with a certain extension, returning the path to the file. The file is marked to be removed when the Java VM exits.

**Params:** String extension — An extension, like ".txt", to append to the end of the temporary file.
**Returns:** String - The path to the newly created temp file.
**Scope:** Gateway, Vision Client, Perspective Session

### system.file.readFileAsBytes
`system.file.readFileAsBytes(filepath)`

Opens the file found at path filename, and reads the entire file. Returns the file as an array of bytes. Commonly this array of bytes is uploaded to a database table with a column of type BLOB (Binary Large OBject), via an INSERT/UPDATE query.

**Params:** String filepath — The path of the file to read.
**Returns:** List[Byte] - The contents of the file as an array of bytes.
**Scope:** Gateway, Vision Client, Perspective Session

### system.file.readFileAsString
`system.file.readFileAsString(filepath, [encoding])`

Opens the file found at path filename, and reads the entire file. Returns the file as a string. Common uses: loading it into a component's text property, uploading it to a database table, or saving it to another file with system.file.writeFile.

**Params:** String filepath — The path of the file to read.; String encoding — The character encoding of the file to be read. Will throw an exception if the string does… (opt)
**Returns:** String - The contents of the file as a string.
**Scope:** Gateway, Vision Client, Perspective Session

### system.file.writeFile
`system.file.writeFile(filepath, charData, [append], [encoding])`
`system.file.writeFile(filepath, data, [append], [encoding])`

Writes the given data to the file at file path filename. If the file exists, the append argument determines whether or not it is overwritten (the default) or appended to. The data argument can be either a string or an array of bytes (commonly retrieved from a BLOB in a database or read from another file using system.file.readFileAsBytes).

**Note:** [note] This function is scoped for Perspective Sessions, but since all scripts in Perspective run on the Gateway, the file must be located on the Gateway's file system.

**Syntax (charData param)**
**Params:** String filepath — The path of the file to write to.; String charData — The character content to write to the file.; Boolean append — If true, the file will be appended to if it already exists. If false, the file will be ov… (opt); String encoding — The character encoding of the file to write. Will throw an exception if the string does n… (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

**Syntax (data param)**
**Params:** String filepath — The path of the file to write to.; Byte[] data — The binary content to write to the file.; Boolean append — If true, the file will be appended to if it already exists. If false, the file will be ov… (opt); String encoding — The character encoding of the file to write. Will throw an exception if the string does n… (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

## system.report

Reporting Module scripting: run a report and get raw bytes back (`executeReport`), run-and-send through a configured distribution action (`executeAndDistribute`), and enumerate the reports available in a project (`getReportNamesAsDataset`/`AsList`). `project` is optional when called from Vision/Perspective client scope (it can infer the current project) but required from Gateway scope.

### system.report.executeAndDistribute
`system.report.executeAndDistribute(path, project, [parameters], action, [actionSettings])`

Executes and distributes a report. Similar to scheduling a report to execute, except a schedule is not required to utilize this function. This is a great way to distribute the report on demand from a Client.

**Params:** String path — The path to the existing report.; String project — The name of the project where the report is located. Optional in client scope.; Dictionary[String, Integer] parameters — A dictionary of parameter overrides, in the form name:value pairs. (opt); String action — The name of the distribution action to use.; Dictionary[List, Any] actionSettings — A dictionary of settings particular to the action. Missing values will use the default va… (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.report.executeReport
`system.report.executeReport(path, project, [parameters], fileType)`

Immediately executes an existing report and returns a List[Byte] of the output. Throws an IllegalArgumentException when the file type is not recognized, path does not exist, or project does not exist.

**Params:** String path — The path to the existing report.; String project — The name of the project where the report is located. Optional in client scope.; Dictionary[String, Integer] parameters — A dictionary of parameter overrides, in the form name:value. (opt); String fileType — The file type the resulting byte array should represent. Defaults to "pdf". Not case-sens…
**Returns:** List[Byte] - A byte array of the resulting report.
**Scope:** Gateway, Vision Client, Perspective Session

### system.report.getReportNamesAsDataset
`system.report.getReportNamesAsDataset([project], [includeReportName])`

Gets a dataset of all reports for a project. Throws an IllegalArgumentException if the project name is omitted in the Gateway scope, or the project does not exist.

**Params:** String project — The name of the project where the reports are located. Optional in client scope.; Boolean includeReportName — When set to False, the end of Path does not include the report name. Default is True. (opt)
**Returns:** Dataset - A dataset of report paths and names for the project. Returns an empty dataset if the project has no reports.
**Scope:** Gateway, Vision Client, Perspective Session

### system.report.getReportNamesAsList
`system.report.getReportNamesAsList(project)`

Gets a list of all reports for a project. Throws an IllegalArgumentException if the project name is omitted in the Gateway scope or if the project does not exist.

**Params:** String project — The name of the project where the reports are located. Optional in Client scope and Persp…
**Returns:** List - A list of report paths for the project. Returns an empty list if the project has no reports.
**Scope:** Gateway, Vision Client, Perspective Session
## system.twilio

Scripting for the Twilio integration module: send SMS, place voice calls (with text-to-speech and optional recording), and send WhatsApp messages — both free-form (only valid inside a 24-hour session the recipient opened) and pre-approved templates. All calls target a named Twilio account configured in the Gateway; phone numbers come from Twilio, not from Ignition users.

### system.twilio.getAccounts
`system.twilio.getAccounts()`

Returns a list of Twilio account names that have been configured in the Gateway.

**Params:** none
**Returns:** List[String] - A list of configured Twilio account names.
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.getAccountsDataset
`system.twilio.getAccountsDataset()`

Returns a list of Twilio account names that have been configured in the Gateway as a single-column Dataset.

**Params:** none
**Returns:** Dataset - A list of configured Twilio accounts as a single-column Dataset.
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.getActiveCall
`system.twilio.getActiveCall(accountName)`

Returns a list of configurations for currently active Twilio voice calls. This only applies to synchronous calls that use the reverse-proxy system to call back into Ignition for authentication and alarm acknowledgements.

**Params:** String accountName — The Twilio account to use for the calls.
**Returns:** CallView - An array of CallView objects (sid, status, direction, etc. properties).
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.getPhoneNumbers
`system.twilio.getPhoneNumbers(accountName)`

Returns a list of outgoing phone numbers for a Twilio account. Note that these numbers are supplied by Twilio, and are not defined on a user in Ignition.

**Params:** String accountName — The Twilio account to retrieve phone numbers for
**Returns:** List[String] - A list of phone numbers for the given Twilio account
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.getPhoneNumbersDataset
`system.twilio.getPhoneNumbersDataset(accountName)`

Returns a list of outgoing phone numbers for a Twilio account as a single-column Dataset. Note that these numbers are supplied by Twilio, and are not defined on a user in Ignition.

**Params:** String accountName — The Twilio account for which to retrieve phone numbers.
**Returns:** Dataset - A list of phone numbers for the given Twilio account as a single-column Dataset
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.sendFreeformWhatsApp
`system.twilio.sendFreeformWhatsApp(accountName, fromNumber, toNumber, message)`

Sends a free-form WhatsApp message. WhatsApp considers any message that is not a pre-approved template a free-form message. Free-form messages can only be sent after a 24-hour Session opens (opened by the user sending a message to the number first).

**Params:** String accountName — The Twilio account to send from.; String fromNumber — The phone number configured with Twilio to use for making the calls.; String toNumber — The phone number of the recipient.; String message — The body of the free-form WhatsApp message.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.sendPhoneCall
`system.twilio.sendPhoneCall(accountName, fromNumber, toNumber, message, voice, language, recordCall)`

Sends a phone call to a specific phone number. Requires a Twilio account configured in the Gateway with a valid number configured for use with Twilio Voice.

**Params:** String accountName — The Twilio account to use for the calls.; String fromNumber — The phone number configured with Twilio to use for making the calls.; String toNumber — The phone number of the recipient.; String message — The message text to use in the call.; String voice — The voice-to-text algorithm to use ("man"/"woman" are basic options). (opt); String language — The language code for the language to use for text-to-speech generation. Defaults to en-U… (opt); Boolean recordCall — Whether to record the calls. Defaults to false. (opt)
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.sendSms
`system.twilio.sendSms(accountName, fromNumber, toNumber, message)`

Sends an SMS message.

**Params:** String accountName — The Twilio account to send the SMS from.; String fromNumber — The outbound phone number belonging to the Twilio account to use.; String toNumber — The phone number of the recipient.; String message — The body of the SMS.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.twilio.sendWhatsAppTemplate
`system.twilio.sendWhatsAppTemplate(accountName, userNumber, whatsAppService, whatsAppTemplate, templateParameters)`

Sends a WhatsApp template message. Template messages are configurable messages on Twilio that can be sent to users via Twilio WhatsApp.

**Params:** String accountName — The Twilio account to send from.; String userNumber — The phone number of the recipient.; String whatsAppService — The Twilio Messaging Service SID configured to send WhatsApp Messages.; String whatsAppTemplate — The Twilio Content Template SID.; String templateParameters — A list of values to pass into the Twilio Content Template as parameters.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session
## system.sfc

Sequential Function Chart control from script: start a chart instance (must be set to "Callable" execution mode), pause/resume/cancel a running instance by ID, read or set chart- and step-scoped variables, and force a redundancy checkpoint so a failover can resume mid-chart. For `setVariable`/`setVariables`, omitting `stepId` targets a chart-scoped variable; supplying it targets a step-scoped variable on the currently active step only.

### system.sfc.cancelChart
`system.sfc.cancelChart(id)`

Cancels the execution of a running chart instance. Any running steps will be told to stop, and the SFC chart will enter Canceling state. Will throw a KeyError if the ID does not match any running chart instance.

**Params:** String id — The ID of the chart instance to cancel.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.getRunningCharts
`system.sfc.getRunningCharts([chartPath])`

Retrieves information about running charts. Can search all running charts, or filter to charts at a specific path. This function will also return charts that are in a Paused state.

**Params:** String chartPath — The path to a chart to filter on: i.e., "folder/chartName". If specified, only charts at…
**Returns:** Dataset - A dataset with information on the active chart (instanceId, chartPath, project, status, etc. columns).
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.getVariables
`system.sfc.getVariables(instanceId)`

Get the variables in a chart instance's scope. Commonly used to check the value of a Chart Parameter, or determine how long the chart has been running for.

**Params:** String instanceId — The instance identifier of the chart.
**Returns:** PyChartScope - Effectively a Python dictionary of variables; Step scopes for active steps are found under the "activeSteps" key.
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.pauseChart
`system.sfc.pauseChart(id)`

Pauses a running chart instance. Any running steps will be told to pause, and the chart will enter Pausing state. Will throw a KeyError if the ID does not match any running chart instance.

**Params:** String id — The ID of the chart instance to pause
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.redundantCheckpoint
`system.sfc.redundantCheckpoint(instanceId)`

Synchronizes chart and step variables of the specified chart instance across a redundant cluster, allowing the chart instance to continue where it left off if a redundant failover occurs.

**Params:** String instanceId — The instance identifier of the chart.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.resumeChart
`system.sfc.resumeChart(id)`

Resumes a chart that was paused. Steps which were previously paused will be resumed, and the chart will enter Resuming state. Will throw a KeyError if the ID does not match any running chart instance.

**Params:** String id — The ID of the chart instance to resume.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.setVariable
`system.sfc.setVariable(instanceId, [stepId], variableName, variableValue)`

Sets a variable inside a currently running SFC chart. Omitting stepId targets a chart-scoped variable; supplying it targets a step-scoped variable, and the referenced step must be the currently active step.

**Params:** String instanceId — The instance identifier of the chart.; String stepId — The id for a step inside of a chart. If omitted the function will target a chart scoped v… (opt); String variableName — The name of the variable to set.; Object variableValue — The value for the variable to be set to.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.setVariables
`system.sfc.setVariables(instanceId, [stepId], variableMap)`

Sets any number of variables inside a currently running chart. Same chart-scope vs step-scope stepId rule as setVariable.

**Params:** String instanceId — The instance identifier of the chart.; String stepId — The id for a step inside of a cart. If omitted the function will target a chart scoped va… (opt); Dictionary[String, Any] variablesMap — A dictionary containing the name:value pairs of the variables to set.
**Returns:** Nothing
**Scope:** Gateway, Vision Client, Perspective Session

### system.sfc.startChart
`system.sfc.startChart(projectName, chartPath, parameters)`

Starts a new instance of a chart. The chart must be set to "Callable" execution mode.

**Params:** String projectName — The name of the project that the chart was created in.; String chartPath — The path to the chart, for example "ChartFolder/ChartName".; Dictionary[String, Any] parameters — A dictionary of arguments. Each key-value pair becomes a variable in the chart's scope.
**Returns:** String - The unique ID of this chart instance.
**Scope:** Gateway, Vision Client, Perspective Session

## system.eventstream

**New in Ignition 8.3.** Scripting companion to the new **Event Streams** module/core module, which adds "event stream" as a project resource built in the Designer: a **Source** stage (Kafka — requires the Kafka module, HTTP Endpoint — requires the Web Dev module, Event Listener, or Tag Event), optional **Filter**/**Transform** stages, and a **Handler**. Event streams are event-driven/subscription-based rather than polled, and are meant to replace hand-rolled combinations of message handlers and gateway scripts for reacting to asynchronous data. All three scripting functions are **Gateway scope only** — there is no Vision Client or Perspective Session scope, so a Perspective component script cannot call `system.eventstream.*` directly; it must go through a Gateway-side script (e.g., a message handler or gateway event script) if it needs to trigger one. `publishEvent` is how a script pushes a message into an "Event Listener" source, either on the local Gateway or a named remote Gateway (`gatewayName`), with an optional acknowledge/blocking handshake.

### system.eventstream.getDiagnostics
`system.eventstream.getDiagnostics(project, path)`

Retrieves diagnostics for an event stream.

**Params:** String project — The project the event stream belongs to.; String path — The path to the event stream resource.
**Returns:** Nothing (diagnostics are typically logged/returned as a dictionary of stream status)
**Scope:** Gateway

### system.eventstream.listEventStreams
`system.eventstream.listEventStreams(project)`

Lists event stream resource paths that are part of the specified project.

**Params:** String project — The project the event stream(s) belong to.
**Returns:** List - A list of event stream resources within the specified project.
**Scope:** Gateway

### system.eventstream.publishEvent
`system.eventstream.publishEvent(project, path, message, acknowledge, [gatewayName])`

Publishes a message to a Gateway Event Source. Can publish to the local Gateway, or to a remote Gateway (via gatewayName).

**Params:** String project — The project the event stream(s) belong to.; String path — The path to the event stream resource.; String message — The string message to send.; Boolean acknowledge — If True, further messages will be blocked until the receiving Gateway Event Listener sour…; String gatewayName — The Gateway Name of the remote Gateway to send the message to. Omitting or None sends to t… (opt)
**Returns:** PyDictionary - A dictionary of key/value status pairs from publishing (errorMessage, stage, status keys).
**Scope:** Gateway
## Gotchas and 8.3 notes

- **Classic auth vs. Perspective's Identity Provider auth (8.3 reworked security).** `system.security.validateUser`/`getUserRoles` and the credential-facing parts of `system.user` operate against the **Classic Authentication Strategy** (a User Source + an authentication profile) — this is what the Designer and Vision Client authenticate against. The live docs state explicitly: *"If you have Ignition 8.3 with the Perspective module, authentication is handled instead by the Identity Provider Authentication Strategy."* A Perspective Session's own login/logout/authorization is driven by an IdP (Internal, OpenID Connect 1.0, or SAML 2.0), Security Levels, and User Grants — via `system.perspective.login`, `logout`, `isAuthorized`, and `authenticationChallenge` (outside this reference's function set), not `system.security`. Don't assume `system.security.validateUser` tells you anything about who is logged into the current Perspective Session, and don't expect `system.user`'s User Source roles to be the roles an IdP-authenticated Perspective user actually has (those come from the IdP's grants/claims).
- **Duplicate roster APIs, split by scope.** `system.alarm.createRoster`/`getRosters` (Vision Client, Gateway, Perspective Session) and `system.roster.createRoster`/`getRosters` (Gateway, Perspective Session only) manage the *same underlying roster concept* with near-identical signatures. The docs say in plain text to use the `system.roster` versions from Gateway/Perspective and fall back to `system.alarm`'s versions only from a Vision Client. Mixing them up compiles fine and fails at runtime/scope-check time, not at write time.
- **`system.file` scope line is misleading.** Every function claims "Gateway, Vision Client, Perspective Session" scope, but Gateway and Perspective Session both mean the **Gateway host's filesystem** (Perspective scripts always execute server-side), while Vision Client means the **end user's desktop filesystem**. A hardcoded path that works in one context will silently fail — or worse, resolve to a different real file — in another.
- **`system.net.httpClient` instances are heavyweight** — the docs caution against creating one per call; instantiate once (e.g., at module scope) and reuse it across requests.
- **`system.eam` is Controller-only.** All four functions throw when called from an Agent Gateway; there's no way for an Agent to call back symmetrically.
- **`system.eventstream` is Gateway-scope only**, with no Vision Client or Perspective Session variants — new in 8.3 alongside the Event Streams module. A Perspective view can't call it directly from component/session scripts; route through a Gateway-side script instead.
- **UIResponse pattern, not exceptions, for most `system.user` mutations.** `addUser`, `editUser`, `addRole`, `editRole`, `addSchedule`, `addHoliday`, etc. return a `UIResponse` object with `getErrors()`/`getWarns()`/`getInfos()` rather than raising on a partial or full failure — code that ignores the return value can fail silently.
- **No explicit "Deprecated"/"Removed"/"New in 8.3" tags on individual function pages.** Across all 88 pages in this set, the only doc-level admonitions found were a `caution` on `system.net.httpClient` (heavyweight, reuse it) and a `note` on `system.file.writeFile` (Gateway filesystem for Perspective). The 8.3-specific story here is structural — the new Event Streams module and the Classic-vs-IdP auth split — rather than per-function changelog callouts; don't rely on the function pages themselves to flag breaking changes.
- **Naming inconsistency:** the doc URL slug is `system-twilio-getActiveCalls` (plural) but the published function name/H1 is `system.twilio.getActiveCall` (singular). Use the documented singular name in scripts.
- **`system.groups` (Transaction Groups/SQL Bridge) is down to two functions** (`loadFromFile`, `removeGroups`) — reflecting that Transaction Groups is a legacy, maintenance-mode feature by 8.3 rather than an area of active development.
