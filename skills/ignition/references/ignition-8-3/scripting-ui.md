# Ignition 8.3 — UI scripting functions (system.perspective, system.vision, system.gui, system.nav, system.print)

Intro: In 8.3, UI scripting is split by client type. `system.perspective` functions only run in **Perspective Session scope** (browser/mobile/Workstation sessions, plus some in Gateway scope for cross-session calls). `system.vision`, and the legacy `system.gui`/`system.nav`/`system.security` UI namespaces, only run in **Vision Client scope** — as of 8.3 `system.gui`, `system.nav`, and the UI-facing pieces of `system.security` no longer have their own documentation pages; their functions have been renamed and consolidated under `system.vision` (old names remain as working aliases for backwards compatibility — see Gotchas). `system.print` is the exception: its two functions run in Gateway, Vision Client, **and** Perspective Session scope. When writing a script module meant to be shared between Perspective and Vision, never call a Vision-only or Perspective-only function directly — branch on `system.util.getSessionInfo()` / project type, or keep the UI call in a client-specific event handler, or the script will throw a scope error on the client that lacks that namespace at runtime.

## system.perspective
`system.perspective` functions target a Session, a Page, or (for popups/docks) a specific view instance. Most functions accept optional `sessionId`/`pageId` keyword arguments: omitted, they default to the caller's own session/page; supplied, the call can be dispatched from Gateway-scoped code (timer scripts, tag change scripts, message handlers) at a different session — but most of these functions only work from Gateway scope when **both** `sessionId` and `pageId` are supplied together. `system.perspective.sendMessage` is the standard way to pass data into a running session/page/view from a script, and pairs with a Message Handler component/session/page event. Several async/UI actions (`navigate`, `openPopup`, `print`, etc.) queue work on the client and return immediately — do not assume the UI update has completed when the next script line runs.

### system.perspective.alterDock
`system.perspective.alterDock(dockId, [config], [sessionId], [pageId])`
Changes configuration of a specified dock on a Perspective page.
- **Params:** String dockId — The unique identifier of the dock to be modified. If no dock with the specified ID exists…; Dictionary config — A dictionary containing the dock configuration to be applied when the script is run. If o…; String sessionId — The ID of the session in which the dock modification is applied. If omitted, the modifica…; String pageId — The ID of the page where the dock is located. If omitted, the modification applies to the…
- **Returns:** Nothing
- **Scope:** Perspective Session

### system.perspective.alterLogging
`system.perspective.alterLogging([remoteLoggingEnabled], [level], [remoteLoggingLevel], [sessionId], [pageId])`
Changes Perspective Session logging attributes and levels.
- **Params:** Boolean remoteLoggingEnabled — Will enable remote logging if True. Remote logging will send log events from the Session …; String level — The desired Session logging level. Possible values are: all, trace, debug, info, warn, er…; String remoteLoggingLevel — The desired remote logging level. Possible values are: all, trace, debug, info, warn, err…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current Page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.authenticationChallenge
`system.perspective.authenticationChallenge([sessionId], [pageId], [idp], [forceAuth], [timeout], [payload], [framing])`
Triggers an authentication challenge action.
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used. [optional]; String idp — The name of the IdP to use for this authentication challenge. If omitted, the Project def…; Boolean forceAuth — True if Ignition should ask the IdP to re-authenticate the user, even if the user is alre…; Integer timeout — the number of minutes the system will wait in between the authentication request and the …; Any payload — An opaque payload object that may contain any information. This object will be passed to …; String framing — A string representing the type of framing that should be used. **self**: Indicates that t…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.closeDock
`system.perspective.closeDock(id, [sessionId], [pageId])`
Closes a docked view.
- **Params:** String id — The unique, preconfigured dock ID for the docked view. Is specified when a view is assign…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.closePage
`system.perspective.closePage([message], [sessionId], [pageID])`
Closes the page with the given page id or the current page if no page id is provided.
- **Params:** String message — The message to display when the page closes. If omitted, the default message (set in the …; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to be closed. If omitted, the current pageId is used. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.closePopup
`system.perspective.closePopup(id, [sessionId], [pageId])`
Closes a popup view.
- **Params:** String id — The unique identifier for the popup, given to the popup when first opened. If given an em…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current Page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.closeSession
`system.perspective.closeSession([message], [sessionId])`
Closes the Perspective Session with the given sessionID or the current Session if no ID is provided.
- **Params:** String message — The message to display when the Session closes. If omitted, the default message (set in t…; String sessionId — Identifier of the Session to be closed. If omitted, the current sessionId is used. [optio…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.download
`system.perspective.download(filename, data, [contentType], sessionId, [pageId])`
`system.perspective.download(filename, data, [contentType], [sessionId], [pageId])`
Downloads data from the Gateway to a device running a Session.
- **Params:** String filename — Suggested name for the downloaded file.; String data — The data to be downloaded. May be a string, a byte[], or an InputStream. Strings will be …; String contentType — Value for the "Content-Type" header, for example: "text/plain; charset=utf-8". [optional]; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session / Perspective Session

### system.perspective.getProjectInfo
`system.perspective.getProjectInfo()`
Returns a dictionary of meta data from a Perspective Project.
- **Params:** None
- **Returns:** **Dictionary [String, Any]** - A dictionary of project meta data. See the table in the description for a listing of keys.
- **Scope:** Perspective Session

### system.perspective.getSessionInfo
`system.perspective.getSessionInfo([usernameFilter], [projectFilter])`
Returns information about one or more Perspective Sessions.
- **Params:** String usernameFilter — A filter based on logged in user. [optional]; String projectFilter — A filter based on the project name. [optional]
- **Returns:** **List** - A list of objects ([PyJsonObjectAdapter](https://sdk.inductiveautomation.com/javadoc/ignition83/8.3.1/com/inductiveautomation/ignition/com…
- **Scope:** Gateway, Perspective Session

### system.perspective.isAuthorized
`system.perspective.isAuthorized(isAllOf, securityLevels, [sessionID])`
Checks if the user in the current Session is authorized against a target collection of security levels.
- **Params:** Boolean isAllOf — True if the current user must have all of the given security levels to be authorized. Fal…; List[String] securityLevels — An array of string paths to a security level node in the form of "Path/To/Node". Each lev…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…
- **Returns:** True if the user logged into the specified session is authorized, false otherwise.
- **Scope:** Gateway, Perspective Session

### system.perspective.login
`system.perspective.login([sessionId], [pageId], [forceAuth])`
Triggers a login event that will allow the user to log in with the project's configured Identity Provider (IdP).
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the Page to target. If omitted, the current Page will be used automatically…; Boolean forceAuth — Determines if Ignition should ask the IdP to re-authenticate the user, even if the user i…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.logout
`system.perspective.logout([sessionId], [pageId], [message])`
Triggers a logout event, which will log the user out.
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the Page to target. If omitted, the current Page will be used automatically…; String message — The message to display when the user logs out of their session. This message is only show…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.navigate
`system.perspective.navigate(page, url, view, [params], [sessionId], [pageId], [newTab])`
Navigate a Session to a specified view or mounted page.
- **Params:** String page — The URL of a Perspective page to navigate to. The path can include an optional leading sl…; String url — The URL of a web address to navigate to. If the `page` or `view` parameters are specified…; String view — If specified, will navigate to a specific view. Navigating to a view with this parameter …; Dictionary[String, String] params — Used only in conjunction with the view parameter, Dictionary of values to pass to any par…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…; Boolean newTab — If True, opens the contents in a new tab. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.navigateBack
`system.perspective.navigateBack([sessionId], [pageId])`
Navigate the session to a specified view or mounted page.
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.navigateForward
`system.perspective.navigateForward([sessionId], [pageId])`
Navigate the session to a specified view or mounted page. This is similar to a browser's "forward" function.
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.openDock
`system.perspective.openDock(id, [sessionId], [pageId])`
Opens a docked View. Requires the preconfigured dock ID for the view.
- **Params:** String id — The unique, preconfigured dock ID for the docked View. Is specified when a View is assign…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the Page to target. If omitted, the current Page will be used automatically…; Dictionary[String, String] params — Parameters that can be passed into the docked view. Must match the docked views View Para…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.openPopup
`system.perspective.openPopup(id, view, [params], [title], [position], [showCloseIcon], [draggable], [resizable], [modal], [overlayDismiss], [sessionId], [pageId], [viewportBound])`
Open a popup view over the given page.
- **Params:** String id — A unique popup string. Will be used to close the popup from other popup or script actions.; String view — The path to the View to use in the popup.; Dictionary[String, Any] params — Dictionary of key-value pairs to use as input parameters to the View. [optional]; String title — Text to display in the title bar. Defaults to an empty string. [optional]; Dictionary[String, Integer] position — Dictionary of key-value pairs to use for position. Possible position keys are: left, top,…; Boolean showCloseIcon — Shows the close icon if True. Defaults to True. [optional]; Boolean draggable — Allows the popup to be dragged if True. Defaults to True. [optional]; Boolean resizable — Allows the popup to be resized if True. Defaults to False. [optional]; Boolean modal — Makes the popup modal if True. A modal popup is the only view the user can interact with.…; Boolean overlayDismiss — Allows the user to dismiss and close a modal popup by clicking outside of it if True. Def…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the Page to target. If omitted, the current Page will be used automatically…; Boolean viewportBound — If True, popups will be "shifted" to always open within the bounds of the viewport. If th…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.print
`system.perspective.print([message], [sessionId], [pageId], [destination])`
Prints the supplied message to the local console or the gateway logs, as appropriate.
- **Params:** String message — The print statement that will be displayed on the console. [optional]; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current Page will be used automatically…; String destination — Where the message should be printed. If specified, must be "client", "gateway", or "all".…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.refresh
`system.perspective.refresh([sessionId], [pageId])`
Triggers a refresh of the page.
- **Params:** String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current Page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.sendMessage
`system.perspective.sendMessage(messageType, payload, [scope], [sessionId], [pageId])`
Send a message to a message handler within the same session.
- **Params:** String messageType — The message type that will be invoked. Message handlers configured within the project are…; Dictionary[String, String] payload — A Python dictionary representing any parameters that will be passed to the message handle…; String scope — The scope that the message should be delivered to. Valid values are "session", "page", or…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used. [optional]
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.setTheme
`system.perspective.setTheme(name, [sessionId], [pageId])`
Changes the theme in a page to the specified theme.
- **Params:** String name — The theme name to switch to. Possible values are "dark" or "light".; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current page will be used automatically…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.toggleDock
`system.perspective.toggleDock(id, [sessionId], [pageId])`
Toggles a docked view.
- **Params:** String id — The unique, preconfigured 'Dock ID' for the docked view. Is specified when a view is assi…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the Page to target. If omitted, the current Page will be used automatically…; Dictionary[String, String] params — Parameters that can be passed into the docked view. Must match the docked views View Para…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.togglePopup
`system.perspective.togglePopup(id, view, [params], [title], [position], [showCloseIcon], [draggable], [resizable], [modal], [overlayDismiss], [sessionId], [pageId], [viewportBound])`
Opens or closes a popup view.
- **Params:** String id — A unique popup string. Will be used to close the popup from other popup or script actions.; String view — The path to the view to use in the popup.; String title — Text to display in the title bar. Defaults to an empty string. [optional]; Dictionary[String, Integer] position — Dictionary of key-value pairs to use for position. Possible position keys are: left, top,…; Boolean showCloseIcon — Will show the close icon if True. Defaults to True. [optional]; Boolean draggable — Will allow the popup to be dragged if True. Defaults to True. [optional]; Boolean resizable — Will allow the popup to be resized if True. Defaults to False. [optional]; Boolean modal — Will make the popup modal if True. A modal popup is the only view the user can interact w…; Boolean overlayDismiss — Will allow the user to dismiss and close a modal popup by clicking outside of it if True.…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…; String pageId — Identifier of the page to target. If omitted, the current Page will be used automatically…; Boolean viewportBound — If True, popups will be "shifted" to open within the bounds of the viewport. If the popup…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.vibrateDevice
`system.perspective.vibrateDevice(integer, [sessionId])`
Cause a device running the Perspective Mobile App to vibrate.
- **Params:** String duration — The duration in milliseconds to vibrate the device.**Note:** iOS vibration duration is fi…; String sessionId — Identifier of the Session to target. If omitted, the current Session will be used automat…
- **Returns:** Nothing
- **Scope:** Gateway, Perspective Session

### system.perspective.workstation.exit
`system.perspective.workstation.exit()`
When called from a session running in Workstation, this function will close Workstation.
- **Params:** None
- **Returns:** Nothing
- **Scope:** Perspective Session

### system.perspective.workstation.toKiosk
`system.perspective.workstation.toKiosk()`
Attempts to put Workstation into Kiosk mode.
- **Params:** None
- **Returns:** Nothing
- **Scope:** Perspective Session

### system.perspective.workstation.toWindowed
`system.perspective.workstation.toWindowed()`
Attempts to put Workstation into Windowed mode.
- **Params:** None
- **Returns:** Nothing
- **Scope:** Perspective Session


## system.vision
`system.vision` is the Vision Client scripting namespace: every function below only runs inside a running Vision Client (Designer preview counts as a Vision Client for most of these). Many functions take a `window`/`windowPath` or a component `event` object to resolve which window/component to operate on; navigation functions (`swapTo`, `swapWindow`, `goBack`/`goForward`/`goHome`) assume the Typical Navigation Strategy layout convention (main-screen window + popups). A large share of this namespace exists only for backwards compatibility: in 8.3 the historic `system.gui.*`, `system.nav.*`, and `system.security.switchUser`/`unlockScreen` functions were renamed onto `system.vision.*` (old call sites still work unmodified — see Gotchas for the full rename list).

### system.vision.beep
`system.vision.beep()`
Tells the computer where the script is running to make a "beep" sound.
- **Params:** None
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.centerWindow
`system.vision.centerWindow(windowPath)`
`system.vision.centerWindow(window)`
Given a window path, or a reference to a window itself, it will center the window.
- **Params:** String windowPath — The path of the window to center.; FPMIWindow window — A reference to the window to center.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.closeDesktop
`system.vision.closeDesktop(handle)`
Allows you to close any of the open desktops associated with the current client.
- **Params:** String handle — The handle for the desktop to close. The screen index cast as a string may be used instea…
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.closeParentWindow
`system.vision.closeParentWindow(event)`
Closes the parent window given a component event object.
- **Params:** EventObject event — A component event object. The enclosing window for the component will be closed. Refer to…
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.closeWindow
`system.vision.closeWindow(window)`
`system.vision.closeWindow(windowPath)`
Given a window path, or a reference to a window itself, it will close the window.
- **Params:** FPMIWindow window — A reference to the window to close.; String windowPath — The path of a window to close.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.color
`system.vision.color(color)`
`system.vision.color(red, green, blue, [alpha])`
Creates a new color object, either by parsing a string or by having the RGB[A] channels specified explicitly.
- **Params:** String color — A string that will be coerced into a color. Can accept many formats, such as "red" or "#F…; Integer red — The red component of the color, an integer 0-255.; Integer green — The green component of the color, an integer 0-255.; Integer blue — The blue component of the color, an integer 0-255.; Integer alpha — The alpha component of the color, an integer 0-255. [optional]
- **Returns:** **Color** - The newly created color.
- **Scope:** Vision Client

### system.vision.createImage
`system.vision.createImage(component)`
Takes a snapshot of a component and creates a Java BufferedImage out of it.
- **Params:** Component component — The component to render.
- **Returns:** `BufferedImage` - A [java.awt.image.BufferedImage](https://docs.oracle.com/en/java/javase/11/docs/api/java.desktop/java/awt/image/BufferedImage.html)…
- **Scope:** Vision Client

### system.vision.createPopupMenu
`system.vision.createPopupMenu(itemNames, itemFunctions)`
Creates a new popup menu, which can then be shown over a component on a mouse event.
- **Params:** List[String] itemNames — A list of names to create popup menu items with.; List[String] itemFunctions — A list of functions to match up with the names. Passing in a None object will cause a sep…
- **Returns:** **JPopupMenu** - The [javax.swing.JPopupMenu](https://docs.oracle.com/en/java/javase/11/docs/api/java.desktop/javax/swing/JPopupMenu.html) that was c…
- **Scope:** Vision Client

### system.vision.createPrintJob
`system.vision.createPrintJob(component)`
Provides a general printing facility for printing the contents of a window or component to a printer.
- **Params:** Component component — The component that you'd like to print.
- **Returns:** **JythonPrintJob** - A print job that can then be customized and started. To start the print job, use .print(). Refer to [JythonPrintJob](https://sdk…
- **Scope:** Vision Client

### system.vision.desktop
`system.vision.desktop(handle)`
Allows for invoking system.vision functions on a specific desktop.
- **Params:** String handle — The handle for the desktop to use. The screen index cast as a string may be used instead …
- **Returns:** **VisionUtilities** - A copy of [system.vision](system-vision.md) ([VisionUtilities](https://sdk.inductiveautomation.com/javadoc/ignition83/latest/co…
- **Scope:** Vision Client

### system.vision.exit
`system.vision.exit([force])`
Exits the running Client, as long as the shutdown intercept script doesn't cancel the shutdown event.
- **Params:** Boolean force — If true (1), the shutdown-intercept script will be skipped. Default is false (0). [option…
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.exportCSV
`system.vision.exportCSV(filename, showHeaders, dataset)`
Exports the contents of a dataset as a CSV file, prompting the user to save the file to disk.
- **Params:** String filename — A suggested filename to save as.; Boolean showHeaders — If true, the CSV file will include a header row.; Dataset dataset — The dataset to export.
- **Returns:** **String** - The path to the saved file, or None if the action was canceled by the user.
- **Scope:** Vision Client

### system.vision.exportExcel
`system.vision.exportExcel(filename, showHeaders, dataset, [nullsEmpty])`
Exports the contents of a dataset as an Excel spreadsheet, prompting the user to save the file to disk.
- **Params:** String filename — A suggested filename to save as.; Boolean showHeaders — If true, the spreadsheet will include a header row.; Dataset \ List[Dataset] dataset — Either a single dataset, or a list of datasets. When passing a list, each element represe…; Boolean nullsEmpty — If True, the spreadsheet will leave cells with NULL values empty, instead of allowing Exc…
- **Returns:** **String** - The path to the saved file, or None if the action was canceled by the user.
- **Scope:** Vision Client

### system.vision.exportHTML
`system.vision.exportHTML(filename, showHeaders, dataset, title)`
Exports the contents of a dataset to an HTML page. Prompts the user to save the file to disk.
- **Params:** String filename — A suggested filename to save as.; Boolean showHeaders — If true, the HTML table will include a header row.; Dataset / PyDataset dataset — The dataset to export.; String title — The title for the HTML page.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.findWindow
`system.vision.findWindow(path)`
Finds and returns a list of windows with the given path.
- **Params:** String path — The path of the window to search for.
- **Returns:** **List** - A list of [window objects](appendix\components\vision-components\vision-window-object\vision-window-object.md). May be empty if window is …
- **Scope:** Vision Client

### system.vision.getAvailableLocales
`system.vision.getAvailableLocales()`
Returns a collection of the locales defined on the system, as strings.
- **Params:** None
- **Returns:** **List** - A list of strings, each representing a locale defined in the translation system. :::note Locale Format The returned strings use the legacy…
- **Scope:** Vision Client

### system.vision.getAvailableTerms
`system.vision.getAvailableTerms()`
Returns a collection of available terms defined in the translation system.
- **Params:** None
- **Returns:** **List** - A list of all of the terms available from the translation manager, as strings.
- **Scope:** Vision Client

### system.vision.getClientId
`system.vision.getClientId()`
Returns a hex-string that represents a number unique to the running Client's session.
- **Params:** None
- **Returns:** **String** - A special code representing the Client's session in a unique way.
- **Scope:** Vision Client

### system.vision.getConnectTimeout
`system.vision.getConnectTimeout()`
Returns the connect timeout in milliseconds for all Client-to-Gateway communication.
- **Params:** None
- **Returns:** **Integer** - The current connect timeout, in milliseconds. Default is 10,000 (ten seconds)
- **Scope:** Vision Client

### system.vision.getConnectionMode
`system.vision.getConnectionMode()`
Retrieves this Client session's current connection mode.
- **Params:** None
- **Returns:** **Integer** - The current connection mode for the Client.
- **Scope:** Vision Client

### system.vision.getCurrentDesktop
`system.vision.getCurrentDesktop()`
Returns the handle of the desktop this function was called from.
- **Params:** None
- **Returns:** **String** - The handle of the current desktop.
- **Scope:** Vision Client

### system.vision.getCurrentWindow
`system.vision.getCurrentWindow()`
Returns the path of the current "main screen" window, which is defined as the maximized window.
- **Params:** None
- **Returns:** **String** - The path of the current "main screen" window - the maximized window.
- **Scope:** Vision Client

### system.vision.getDesktopHandles
`system.vision.getDesktopHandles()`
Gets a list of all secondary handles of the open desktops associated with the current client.
- **Params:** None
- **Returns:** **List[Any]** - A Python list of unicode strings, representing the handle of all secondary desktop frames.
- **Scope:** Vision Client

### system.vision.getEdition
`system.vision.getEdition()`
Returns the edition of the Vision Client.
- **Params:** None
- **Returns:** **String** - The edition of the Vision module that is running the Client.
- **Scope:** Vision Client

### system.vision.getExternalIpAddress
`system.vision.getExternalIpAddress()`
Returns the Client's IP address, as it is detected by the Gateway.
- **Params:** None
- **Returns:** **String** - A text representation of the client's IP address, as detected by the Gateway
- **Scope:** Vision Client

### system.vision.getGatewayAddress
`system.vision.getGatewayAddress()`
Returns the address of the Gateway that the Client is currently communicating with.
- **Params:** None
- **Returns:** **String** - The address of the Gateway with which the Client is communicating.
- **Scope:** Vision Client

### system.vision.getInactivitySeconds
`system.vision.getInactivitySeconds()`
Returns the number of seconds since any keyboard or mouse activity.
- **Params:** None
- **Returns:** **Integer** - The number of seconds the mouse and keyboard have been inactive for this client.
- **Scope:** Vision Client

### system.vision.getKeyboardLayouts
`system.vision.getKeyboardLayouts()`
Returns a list of keyboard layouts available on this system.
- **Params:** None
- **Returns:** None
- **Scope:** Vision Client

### system.vision.getLocale
`system.vision.getLocale()`
Returns the current string representing the user's Locale, such as 'en' for English.
- **Params:** None
- **Returns:** **String** - String representing the user's Locale, such as 'en' for English. :::note Locale Format When the locale includes a region, this string us…
- **Scope:** Vision Client

### system.vision.getOpenedWindowNames
`system.vision.getOpenedWindowNames()`
Finds all of the currently open windows and returns a tuple of their paths.
- **Params:** None
- **Returns:** **Tuple** - A tuple of strings, representing the path of each window that is open. Printing the return value will display results in the Vision Clien…
- **Scope:** Vision Client

### system.vision.getOpenedWindows
`system.vision.getOpenedWindows()`
Finds all of the currently open windows and returns a tuple of references to them.
- **Params:** None
- **Returns:** **Tuple** - A tuple of the opened windows, not their names, but the actual [window](appendix\components\vision-components\vision-window-object\vision…
- **Scope:** Vision Client

### system.vision.getParentWindow
`system.vision.getParentWindow(event)`
Finds the parent (enclosing) window for the component that fired an event and returns a reference to it.
- **Params:** EventObject event — A component event object.
- **Returns:** **FPMIWindow** - The [window](appendix\components\vision-components\vision-window-object\vision-window-object.md) that contains the component that fi…
- **Scope:** Vision Client

### system.vision.getReadTimeout
`system.vision.getReadTimeout()`
Returns the read timeout in milliseconds for all client-to-gateway communication.
- **Params:** None
- **Returns:** **Integer** - The current read timeout, in milliseconds. Default is 60,000 (one minute)
- **Scope:** Vision Client

### system.vision.getRoles
`system.vision.getRoles()`
Finds the roles that the currently logged in user has, returns them as a Python tuple of strings.
- **Params:** None
- **Returns:** **Tuple** - A list of the roles (strings) that are assigned to the current user.
- **Scope:** Vision Client

### system.vision.getScreenIndex
`system.vision.getScreenIndex()`
Returns an integer value representing the current screen index based on the screen from which this function was called.
- **Params:** None
- **Returns:** **Integer** - The screen from which the function was called.
- **Scope:** Vision Client

### system.vision.getScreens
`system.vision.getScreens()`
Get a list of all the monitors on the computer this client is open on.
- **Params:** None
- **Returns:** **List[Tuple[String, Integer, Integer]]** - A sequence of tuples of the form (index, width, height) for each screen device (monitor) available.
- **Scope:** Vision Client

### system.vision.getSibling
`system.vision.getSibling(event, name)`
Given a component event object, looks up a sibling component.
- **Params:** EventObject event — A component event object.; String name — The name of the sibling component.
- **Returns:** **VisionComponent** - Returns reference to the sibling component. See [VisionComponent](https://sdk.inductiveautomation.com/javadoc/ignition83/latest…
- **Scope:** Vision Client

### system.vision.getSystemFlags
`system.vision.getSystemFlags()`
Returns an integer that represents a bit field containing information about the currently running system.
- **Params:** None
- **Returns:** **Integer** - A total of all the bits that are currently active. A full-screen Client launched from the Gateway webpage with no SSL will have a value…
- **Scope:** Vision Client

### system.vision.getUsername
`system.vision.getUsername()`
Returns the currently logged-in username.
- **Params:** None
- **Returns:** **String** - The current username.
- **Scope:** Vision Client

### system.vision.getWindow
`system.vision.getWindow(name)`
Finds a reference to an open window with the given name.
- **Params:** String name — The path to the window to field.
- **Returns:** **Window** - A reference to the [window](appendix\components\vision-components\vision-window-object\vision-window-object.md) object, if it was open.
- **Scope:** Vision Client

### system.vision.getWindowNames
`system.vision.getWindowNames()`
Returns a list of the paths of all windows in the current project, sorted alphabetically.
- **Params:** None
- **Returns:** **Tuple** - A tuple of strings, representing the path of each window defined in the current project.
- **Scope:** Vision Client

### system.vision.goBack
`system.vision.goBack()`
When using the Typical Navigation Strategy, this function will navigate back to the previous main screen window.
- **Params:** None
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client

### system.vision.goForward
`system.vision.goForward()`
Navigates "forward" to the last main-screen window the user was on when they executed a system.vision.goBack().
- **Params:** None
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client

### system.vision.goHome
`system.vision.goHome()`
When using the Typical Navigation Strategy, this function will navigate to the "home" window.
- **Params:** None
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client

### system.vision.invokeLater
`system.vision.invokeLater(function, [delay])`
Invokes (calls) the given Python function object after all of the currently processing and pending events are done being processed, or afte…
- **Params:** Callable function — A Python function object that will be invoked later, on the GUI, or event-dispatch, threa…; Integer delay — A delay, in milliseconds, to wait before the function is invoked. The default is 0, which…
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.isOverlaysEnabled
`system.vision.isOverlaysEnabled()`
Returns whether or not the current client's quality overlay system is currently enabled.
- **Params:** None
- **Returns:** **Boolean** - True if overlays are currently enabled.
- **Scope:** Vision Client

### system.vision.isScreenLocked
`system.vision.isScreenLocked()`
Returns whether or not the screen is currently locked.
- **Params:** None
- **Returns:** **Boolean** - A flag indicating whether or not the screen is currently locked.
- **Scope:** Vision Client

### system.vision.isTouchscreenMode
`system.vision.isTouchscreenMode()`
Checks whether or not the running Client's Touch Screen mode is currently enabled.
- **Params:** None
- **Returns:** **Boolean** - True if the Client currently has Touch Screen mode activated.
- **Scope:** Vision Client

### system.vision.lockScreen
`system.vision.lockScreen([obscure])`
Used to put a running client in lock-screen mode.
- **Params:** Boolean obscure — If true(1), the locked screen will be opaque, otherwise it will be partially visible. [op…
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.logout
`system.vision.logout()`
Logs out of the client for the current user and brings the client to the login screen.
- **Params:** None
- **Returns:** Nothing
- **Scope:** All

### system.vision.openDesktop
`system.vision.openDesktop([screen], [handle], [title], [width], [height], [x], [y], [windows])`
Creates an additional Desktop in a new frame.
- **Params:** Integer screen — The screen index of which screen to place the new frame on. If omitted, screen 0 will be …; String handle — A name for the desktop. If omitted, the screen index will be used. [optional]; String title — The title for the new frame. If omitted, the index handle will be used. If the handle and…; Integer width — The width for the new desktop's frame. If omitted, frame will become maximized on the spe…; Integer height — The height for the new desktop's frame. If omitted, frame will become maximized on the sp…; Integer x — The x coordinate for the new desktop's frame. Only used if both width and height are spec…; Integer y — The y coordinate for the new desktop's frame. Only used if both width and height are spec…; PySequence windows — A list of window paths to open in the new Desktop frame. If omitted, the desktop will ope…
- **Returns:** **JFrame** - A reference to the new [Desktop frame](https://docs.oracle.com/en/java/javase/11/docs/api/java.desktop/javax/swing/JFrame.html) object.
- **Scope:** Vision Client
- **Note:** Backwards Compatibility: replaces system.gui.openDesktop; legacy calls still work.

### system.vision.openFile
`system.vision.openFile([extension], [defaultLocation])`
Shows an Open File dialog box, prompting the user to choose a file to open.
- **Params:** String extension — A file extension, such as "pdf", to try to open. [optional]; String defaultLocation — A folder location, such as "C:\MyFiles", to use as the default folder to store in. [optio…
- **Returns:** **String** - The path to the selected file, or Nothing if canceled.
- **Scope:** Vision Client

### system.vision.openFiles
`system.vision.openFiles([extension], [defaultLocation])`
Shows an Open File dialog box, prompting the user to choose a file or files to open.
- **Params:** String extension — A file extension, such as "pdf", to try to open. [optional]; String defaultLocation — A folder location, such as "C:\MyFiles", to use as the default folder to store in. [optio…
- **Returns:** **List** - The paths to the selected files, or None if canceled.
- **Scope:** Vision Client

### system.vision.openURL
`system.vision.openURL(url)`
Opens the given URL or URI scheme outside of the currently running Client in whatever application the host operating system deems appropria…
- **Params:** String url — The URL to open in a web browser or other appropriate application.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.openWindow
`system.vision.openWindow(path, [params])`
Opens the window with the given path.
- **Params:** String path — The path to the window to open.; Dictionary[String, Any] params — A dictionary of parameters to pass into the window. The keys in the dictionary must match…
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client

### system.vision.openWindowInstance
`system.vision.openWindowInstance(path, [params])`
Operates exactly like system.vision.openWindow, except that if the named window is already open, then an additional instance of the window …
- **Params:** String path — The path to the window to open.; Dictionary[String, Any] params — A dictionary of parameters to pass into the window. The keys in the dictionary must match…
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client

### system.vision.playSoundClip
`system.vision.playSoundClip(wavBytes, [volume], [wait])`
`system.vision.playSoundClip(wavFile [, volume] [, wait])`
Plays a sound clip from a wav file to the system's default audio device.
- **Params:** List[Byte] wavBytes — A byte list of a wav file.; Float volume — The clip's volume, represented as a floating point number between 0.0 and 1.0. [optional]; Boolean wait — A boolean flag indicating whether or not the call to playSoundClip should block further s…; String wavFile — A filepath or URL that represents a wav file.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.printToImage
`system.vision.printToImage(component [, filename])`
This function prints the given component (such as a graph, container, entire window, etc) to an image file, and saves the file where ever t…
- **Params:** Component component — The component to render.; String filename — A filename to save the image as. [optional]
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.refreshBinding
`system.vision.refreshBinding(component, propertyName)`
This function will programmatically cause a SQL Query or DB Browse property binding to execute immediately.
- **Params:** JComponent component — The component whose property you want to refresh.; String propertyName — The name of the property that has a SQL Query binding that needs to be refreshed.
- **Returns:** **Boolean** - True if the property was found and refreshed successfully.
- **Scope:** Vision Client
- **Note:** Backwards Compatibility: replaces system.db.refresh; legacy calls still work. Page path is 'system-vision-refresh' but function is renamed refreshBinding.

### system.vision.retarget
`system.vision.retarget(project, [addresses], [params], [windows])`
This function allows you to programmatically 'retarget' a Vision Client to a different project and/or different Gateway.
- **Params:** String project — The name of the project to retarget to.; String or List addresses — The address of the Gateway that the project resides on. If omitted, the current Gateway w…; Dictionary[String, Any] params — A dictionary of parameters that will be passed to the new project. They will be set as gl…; List[String] windows — A list of window paths to use as the startup windows. If omitted, the project's normal st…
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** You cannot retarget across different major Ignition versions, such as 8.1 to 8.3.

### system.vision.saveFile
`system.vision.saveFile(filename)`
`system.vision.saveFile(filename, [extension], [typeDesc])`
Prompts the user to save a new file named filename.
- **Params:** String filename — A file name to suggest to the user.; String extension — The appropriate file extension, like "jpeg", for the file. [optional]; String typeDesc — A description of the extension, like "JPEG Image". [optional]
- **Returns:** **String** - The path to the file that the user decided to save to, or None if they canceled.
- **Scope:** Vision Client

### system.vision.setConnectTimeout
`system.vision.setConnectTimeout(connectTimeout)`
Sets the connect timeout for Client-to-Gateway communication.
- **Params:** Integer connectTimeout — The new connect timeout, specified in milliseconds.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setConnectionMode
`system.vision.setConnectionMode(mode)`
Sets the connection mode for the Client session.
- **Params:** Integer mode — The new connection mode. 1 = Disconnected, 2 = Read-only, 3 = Read/Write.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setLocale
`system.vision.setLocale(locale)`
Sets the user's current Locale.
- **Params:** Object locale — A locale code, such as "en_US" for US English, or a java.util.Locale object.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setOverlaysEnabled
`system.vision.setOverlaysEnabled(enabled)`
Enables or disables the component quality overlay system.
- **Params:** Boolean enabled — True to turn on tag overlays; false to turn them off.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setReadTimeout
`system.vision.setReadTimeout(readTimeout)`
Sets the read timeout for Client-to-Gateway communication.
- **Params:** Integer readTimeout — The new read timeout, specified in milliseconds.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setScreenIndex
`system.vision.setScreenIndex(index)`
Moves an open client to a specific monitor.
- **Params:** Integer index — The new monitor index for this client to move to. 0 based.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.setTouchscreenMode
`system.vision.setTouchscreenMode(enabled)`
Alters a running Client's Touch Screen mode on the fly.
- **Params:** Boolean enabled — The new value for Touch Screen mode being enabled.
- **Returns:** Nothing
- **Scope:** Vision Client

### system.vision.showColorInput
`system.vision.showColorInput(initialColor, [dialogTitle])`
Prompts the user to pick a color using the default color-chooser dialog box.
- **Params:** Color initialColor — A color to use as a starting point in the color choosing popup.; String dialogTitle — The title for the color choosing popup. Defaults to "Choose Color". [optional]
- **Returns:** **Color** - The new color chosen by the user.
- **Scope:** Vision Client

### system.vision.showConfirm
`system.vision.showConfirm(message, [title], [allowCancel])`
Displays a confirmation dialog box to the user with Yes and No options, and a custom message.
- **Params:** String message — The message to show in the confirmation dialog.; String title — The title for the confirmation dialog. [optional]; Boolean allowCancel — Show a cancel button in the dialog. [optional]
- **Returns:** **Boolean** - True if the user selected **Yes**; false if the user selected **No**. None if the user selected **Cancel**.
- **Scope:** Vision Client
- **Note:** Replaces system.gui.confirm (8.1). Legacy calls still work.

### system.vision.showDiagnostics
`system.vision.showDiagnostics()`
Opens the client runtime diagnostics window, which provides information regarding performance, logging, active threads, connection status, …
- **Params:** None
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** Replaces system.gui.openDiagnostics (8.1). Legacy calls still work.

### system.vision.showError
`system.vision.showError(message, [title])`
Displays an error-style message box to the user.
- **Params:** String message — The message to display in an error box. Will accept HTML formatting.; String title — The title for the error box. [optional]
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** Replaces system.gui.errorBox (8.1). Legacy calls still work.

### system.vision.showInput
`system.vision.showInput(message, defaultText)`
Opens up a popup input dialog box.
- **Params:** String message — The message to display for the input box. Will accept HTML formatting.; String defaultText — The default text to initialize the input box with.
- **Returns:** **String** - The string value that was entered in the input box.
- **Scope:** Vision Client
- **Note:** Replaces system.gui.inputBox (8.1). Legacy calls still work.

### system.vision.showMessage
`system.vision.showMessage(message, title)`
Displays an informational-style message popup box to the user.
- **Params:** String message — The message to display. Will accept HTML formatting.; String title — A title for the message box. [optional]
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** Replaces system.gui.messageBox (8.1). Legacy calls still work.

### system.vision.showNumericKeypad
`system.vision.showNumericKeypad(initialValue, [fontSize], [usePasswordMode])`
Displays a modal on-screen numeric keypad, allowing for arbitrary numeric entry using the mouse, or a finger on a touchscreen monitor.
- **Params:** Number initialValue — The value to start the on-screen keypad with.; Integer fontSize — The font size to display in the keypad. [optional]; Boolean usePasswordMode — If True, display a `*` for each digit. [optional]
- **Returns:** **Number** - The value that was entered in the keypad.
- **Scope:** Vision Client
- **Note:** Replaces system.gui.showNumericKeypad (8.1). Legacy calls still work.

### system.vision.showPasswordInput
`system.vision.showPasswordInput(message, [title], [echoChar])`
Pops up a special input box that uses a password field, so the text isn't echoed back in clear-text to the user.
- **Params:** String message — The message for the password prompt. Will accept HTML formatting.; String title — A title for the password prompt. [optional]; String echoChar — A custom echo character. Defaults to: `*` [optional]
- **Returns:** **String** - The password that was entered, or None if the prompt was canceled.
- **Scope:** Vision Client
- **Note:** Replaces system.gui.passwordBox (8.1). Legacy calls still work.

### system.vision.showTouchscreenKeyboard
`system.vision.showTouchscreenKeyboard(initialText, [fontSize], [passwordMode])`
Displays a modal on-screen keyboard, allowing for arbitrary text entry using the mouse, or a finger on a touchscreen monitor.
- **Params:** String initialText — The text to start the on-screen keyboard with.; Integer fontSize — The font size to display in the keyboard. [optional]; Boolean passwordMode — A True value will activate password mode, where the text entered is not echoed back in cl…
- **Returns:** **String** - The text that was entered in the on-screen keyboard.
- **Scope:** Vision Client
- **Note:** Replaces system.gui.showTouchscreenKeyboard (8.1). Legacy calls still work.

### system.vision.showWarning
`system.vision.showWarning(message, [title])`
Displays a message to the user in a warning style popup dialog.
- **Params:** String message — The message to display in the warning. Will accept HTML formatting if the message paramet…; String title — The title for the warning. [optional]
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** Replaces system.gui.warningBox (8.1). Legacy calls still work.

### system.vision.swapTo
`system.vision.swapTo(path, [params])`
Performs a window swap from the current main screen window to the window specified.
- **Params:** String path — The path of a window to swap to.; Dictionary[String, Any] params — A dictionary of parameters to pass into the window. The keys in the dictionary must match…
- **Returns:** **Window** - A reference to window that was navigated to. Refer to the list of [window](appendix\components\vision-components\vision-window-object\vi…
- **Scope:** Vision Client
- **Note:** Replaces system.nav.swapTo (8.1). Legacy calls still work.

### system.vision.swapWindow
`system.vision.swapWindow(swapFromPath, swapToPath, [params])`
`system.vision.swapWindow(event, swapToPath, [params])`
Performs a window swap.
- **Params:** String swapFromPath — The path of the window to swap from. Must be a currently open window, otherwise this will…; String swapToPath — The name of the window to swap to.; Dictionary[String, Any] params — A dictionary of parameters to pass into the window. The keys in the dictionary must match…; EventObject event — A component event whose enclosing window will be used as the "swap-from" window.
- **Returns:** **Window** - A reference to the swapped-to window.
- **Scope:** Vision Client
- **Note:** Replaces system.nav.swapWindow (8.1). Legacy calls still work.

### system.vision.switchUser
`system.vision.switchUser(username, password, [event], [hideError])`
Attempts to switch the current user on the fly.
- **Params:** String username — The username to try and switch to.; String password — The password to authenticate with.; EventObject event — If specified, the enclosing window for this event's component will be closed in the switc…; Boolean hideError — If true (1), no error will be shown if the switch user function fails. Default is False. …
- **Returns:** **Boolean** - False if the switch user operation failed, True otherwise.
- **Scope:** Vision Client
- **Note:** Replaces system.security.switchUser (8.1). Legacy calls still work.

### system.vision.transform
`system.vision.transform(component, [newX], [newY], [newWidth], [newHeight], [duration], [callback], [framesPerSecond], [acceleration], [coordSpace])`
Sets a component's position and size at runtime.
- **Params:** JComponent component — The component to move or resize.; Integer newX — An x-coordinate to move to, relative to the upper-left corner of the component's parent c…; Integer newY — A y-coordinate to move to, relative to the upper-left corner of the component's parent co…; Integer newWidth — A width for the component. [optional]; Integer newHeight — A height for the component. [optional]; Integer duration — A duration over which the transformation will take place. If omitted or 0, the transform …; Callable callback — Function to be called when the transformation is complete. [optional]; Integer framesPerSecond — Frame rate argument which dictates how often the transformation updates over the given du…; Integer acceleration — An optional modifier to the acceleration of the transformation over the given duration. S…; Integer coordSpace — The coordinate space to use. When the default screen coordinates are used, the given size…
- **Returns:** Animator `animation` - An object that contains pause(), resume(), and cancel() methods, allowing for a script to interrupt the animation. See [Animat…
- **Scope:** Vision Client
- **Note:** Replaces system.gui.transform (8.1). Legacy calls still work.

### system.vision.unlockScreen
`system.vision.unlockScreen()`
Unlocks the client, if it is currently in lock-screen mode.
- **Params:** None
- **Returns:** Nothing
- **Scope:** Vision Client
- **Note:** Replaces system.security.unlockScreen (8.1). Legacy calls still work.

### system.vision.updateProject
`system.vision.updateProject()`
Updates the Vision Client project with saved changes.
- **Params:** None
- **Returns:** None
- **Scope:** Vision Client


## system.gui / system.nav / system.print
As of Ignition 8.3, `system.gui` and `system.nav` have **no functions of their own** — every function that used to live there now lives under `system.vision` (see the rename table in Gotchas). Old scripts using `system.gui.*` / `system.nav.*` continue to work unchanged; new scripts should use the `system.vision.*` names shown above. `system.print` is a small, separate two-function namespace usable from any client type or the Gateway:

### system.print.getDefaultPrinterName
`system.print.getDefaultPrinterName()`
Obtains the local default printer.
- **Params:** None
- **Returns:** **String** - A string that represents the default printer. Returns null if there is no default printer.
- **Scope:** Gateway, Vision Client, Perspective Session

### system.print.getPrinterNames
`system.print.getPrinterNames()`
Lists the available local printers.
- **Params:** None
- **Returns:** **List** - A list of strings that contain the names of local printers. Returns an empty list if there are no available local printers.
- **Scope:** Gateway, Vision Client, Perspective Session


## Gotchas and 8.3 notes

- **`system.gui` and `system.nav` are gone as namespaces, not as functionality.** The docs urls83.txt list has zero pages under `appendix/scripting-functions/system-gui/` or `system-nav/` — every function that used to live there is now a `system.vision.*` function. Old `system.gui.*`/`system.nav.*` call sites in existing projects keep working (documented as "backwards compatibility"), but do not write new code against those names.
- **Rename map observed in the 8.3 docs** (old → new, all Vision Client scope, old names still work):
  `system.gui.confirm` → `system.vision.showConfirm`; `system.gui.errorBox` → `system.vision.showError`; `system.gui.inputBox` → `system.vision.showInput`; `system.gui.messageBox` → `system.vision.showMessage`; `system.gui.warningBox` → `system.vision.showWarning`; `system.gui.passwordBox` → `system.vision.showPasswordInput`; `system.gui.openDiagnostics` → `system.vision.showDiagnostics`; `system.gui.openDesktop` → `system.vision.openDesktop`; `system.gui.transform` → `system.vision.transform`; `system.gui.showNumericKeypad`/`showTouchscreenKeyboard` → `system.vision.showNumericKeypad`/`showTouchscreenKeyboard`; `system.gui.desktop` → `system.vision.desktop`; `system.nav.swapTo` → `system.vision.swapTo`; `system.nav.swapWindow` → `system.vision.swapWindow`; `system.security.switchUser` → `system.vision.switchUser`; `system.security.unlockScreen` → `system.vision.unlockScreen`; `system.db.refresh` → `system.vision.refreshBinding` (note: the live doc page is still served at the URL path `system-vision-refresh`, but the function itself is named `refreshBinding`).
- **`system.perspective.retarget`-style version limits apply to Vision, not Perspective:** `system.vision.retarget` explicitly cannot retarget a Client across major Ignition versions (e.g. 8.1 → 8.3).
- **Gateway-scope calls into a specific Perspective session require both IDs.** Functions like `navigate`, `alterLogging`, `download`, `refresh`, `closePage`/`closeSession`, `login`/`logout` are listed with `Scope: Gateway, Perspective Session`, but the Gateway path only works when **both** `sessionId` and `pageId` are supplied — a Gateway timer/tag script that supplies only `sessionId` will silently fail to act on that session's UI.
- **`system.perspective.download` has two distinct overloads with different scope rules**: called from Gateway scope, `sessionId` is required (not optional); called from Session scope, it's optional and defaults to the current session.
- **Common cross-scope mistake:** calling any `system.vision.*` function from a Perspective session script, or any `system.perspective.*` function from a Vision Client script, throws at runtime — these are two mutually exclusive scripting environments even though both are "the UI client." Shared/common script modules meant to run in both projects must not call either namespace directly.
- **`system.perspective.vibrateDevice`** only affects devices running the Perspective Mobile App; iOS enforces a fixed vibration duration regardless of the requested value.
- **`system.perspective.download`** (Session-scope path) requires Ignition Perspective App v1.0.2+ to actually save the file to a mobile device.
- **Workstation-only functions:** `system.perspective.workstation.exit/toKiosk/toWindowed` are no-ops (or errors) unless the session is actually running in Perspective Workstation — they are not general Perspective Session functions.
- **`system.perspective.getSessionInfo`** and **`system.vision.getScreens`/`getSystemFlags`** return structured objects (`PyJsonObjectAdapter`, tuples of tuples, bit-fields) rather than simple scalars — treat the "Returns" line above as a summary, not a full schema.
