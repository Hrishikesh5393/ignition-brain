> **Skill level:** 200 · **Read first:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 92-MOBILE-MODULE-PERSPECTIVE

# Ignition 8.3 Mobile Module & Perspective Mobile Development

## 1. Overview: What "Mobile" Means in Ignition 8.3

Ignition does not ship a separate "Mobile Module" the way it ships the Vision or Perspective modules — that naming persists from Ignition 7.x, where the legacy Mobile Module rendered a cut-down Vision-style client for phones. In 8.3, all mobile delivery runs through the **Perspective Module**, which is inherently responsive and device-aware. When people say "the Mobile Module" today in an 8.x context, they mean:

1. **Perspective Sessions in a mobile browser** — any phone/tablet browser hitting a Perspective page URL.
2. **Perspective Workstation** — the desktop kiosk-style native wrapper (not mobile, but often confused with it).
3. **The native mobile experience** — Perspective rendered inside a WebView-based wrapper, distributed as an installable app via a Mobile Device Management (MDM) tool or manually sideloaded, OR accessed as a pinned/installed **Progressive Web App (PWA)**.

There is no Ignition-signed native iOS/Android binary in the App Store or Play Store. "Native app" delivery in Ignition means one of:

- **PWA install** — the end user's mobile browser (Chrome, Safari) offers "Add to Home Screen," which installs a standalone, full-screen, offline-capable web app icon backed by a service worker. This is the primary supported mobile path and requires no app-store review.
- **WebView wrapper** — a thin native shell (Android WebView / iOS WKWebView) pointed at the Gateway's Perspective page URL, built with a tool like Cordova, Capacitor, or a custom Kotlin/Swift shell, then distributed via MDM (Intune, Jamf, VMware Workspace ONE) or, less commonly, through the App Store/Play Store as a branded client. Inductive Automation does not officially publish or support a generic wrapper; system integrators build these themselves when a client needs an icon on the home screen with none of the "type in a URL" friction, or needs access to native device APIs Perspective doesn't expose to the browser (e.g., certain barcode scanner SDKs, some BLE peripherals).
- **Kiosk MDM profile** — Android Enterprise / Apple Configurator profile that locks a device into a single Chrome/Safari tab pointed at the Gateway, common on wall-mounted operator tablets and handheld scanners (Zebra TC-series, Honeywell CT-series).

Gotcha: teams repeatedly go looking for "Mobile Module" in the Gateway's module list and don't find it — because Perspective *is* the mobile module. If a client specifically asks "do we need to buy the Mobile Module," the answer is: they need Perspective licensed (session-based licensing, see Operations doc), not a separate SKU.

## 2. Perspective Session Types and Mobile Detection

A Perspective Session is created per browser tab/app instance and carries a `session.props.device` object populated at connect time from the User-Agent and viewport:

- `session.props.device.type` — `"desktop"`, `"tablet"`, or `"mobile"` (Perspective's own heuristic, not a hard OS check)
- `session.props.device.touchscreen` — boolean
- `session.props.device.userAgent` — raw string, useful for edge-case sniffing (e.g., detecting a Zebra scanner's embedded browser)
- `session.props.view.width` / `session.props.view.height` — live viewport pixels, updates on rotation/resize

Scripts and bindings can branch on `{session.props.device.type}` to swap views, hide desktop-only components (multi-column trend pens, wide alarm tables), or resize touch targets. This is the mechanism underneath every "make this page mobile-friendly" task — there is no separate "Mobile View" designer mode; you design one Perspective project and make it adapt.

## 3. Responsive Design Patterns

### 3.1 The Coordinate Container trap
New Perspective builders default to Coordinate Containers because they mirror Vision's absolute-positioning muscle memory. Coordinate Containers do **not** reflow — components keep their pixel X/Y regardless of viewport size, so a page built at 1920×1080 clips or overlaps badly on a 390×844 phone. For any view that must run on mobile, avoid Coordinate Containers as the root except for fixed-overlay elements (a floating action button, a persistent header logo).

### 3.2 Containers that actually respond
- **Flex Container** — the workhorse. Set `direction: column` for phone portrait, `direction: row` for tablet landscape, driven by a binding on `{session.props.device.type}` or `{session.props.view.width}`. `wrap: wrap` lets a grid of KPI tiles reflow from 4-across on a tablet to 1-across on a phone without manual breakpoints per component.
- **Breakpoint Container** — purpose-built for this exact problem: define named breakpoints (e.g., `phone < 600px`, `tablet 600–1024px`, `desktop > 1024px`) and swap entire child layouts per breakpoint. This is the closest Perspective gets to CSS media queries and is the recommended container for top-level page shells that must serve phone, tablet, and desktop from one view.
- **Column Container / Tab Container** — good for turning a desktop's side-by-side panels into swipeable/stacked tabs on mobile; wrap a Tab Container's tab strip switch in a device-type binding so tablets show tabs across the top while phones might show them as a bottom nav bar instead (custom styling via CSS classes).

### 3.3 View sizing modes
Each Perspective View has a Size Behavior: `Fixed`, `Percent`, `Min`, or `Auto`. For mobile pages, prefer `Percent` or `Auto` root behavior so the view fills the viewport rather than centering a fixed-pixel canvas inside a phone browser with letterboxing — a very common first mobile bug report ("the app looks tiny with big black bars").

### 3.4 One-page-set, three-breakpoint pattern
The pattern that scales best across projects: build a single set of top-level "shell" views (Nav shell, Content shell) using Breakpoint Containers, and author individual content Views to be layout-agnostic (Flex-based, no hardcoded widths). Avoid duplicating whole page trees per device — duplication guarantees drift, where a tag binding gets fixed on the desktop version and the mobile duplicate quietly keeps the bug. This mirrors the general KB guidance on hunting down page-local style overrides before trusting a shared style class actually reaches every page — the same discipline applies to duplicated mobile view trees.

### 3.5 Style classes over inline styles
Define reusable style classes (`.mobile-touch-target`, `.compact-table-row`) in the project's Perspective Style Classes and toggle them via `session.props.device.type` bindings on a component's `style.classes` property, rather than hardcoding pixel values per-component. This keeps a global fix (e.g., "bump all buttons to 44px on touch devices") to one edit instead of a grep-and-fix sweep across dozens of views.

## 4. Touch Interactions

### 4.1 Tap targets
Apple's Human Interface Guidelines and Android's Material Design both recommend a minimum **44×44pt (iOS) / 48×48dp (Android)** touch target. Perspective components styled for desktop mouse use (dense icon buttons, small checkbox hit-areas, narrow table row-action icons) routinely fall under this on a phone. Practical fix: apply a `min-height`/`min-width` style rule of at least 44px to interactive components inside any style class applied when `device.touchscreen === true`, and increase `padding` rather than shrinking the icon, so the visual size stays consistent while the hit-area grows.

### 4.2 Gestures Perspective supports natively
- **Tap** — standard `onClick` / `onActionPerformed` events fire from touch the same as click.
- **Long-press** — not a first-class Perspective event; simulate with a Pointer Down/Up time-delta calculated in a `onMouseDown`/`onMouseUp` (Perspective maps touch to pointer events) pair of scripts, or use a component's built-in `onClick` combined with a Timer component armed on press.
- **Swipe** — Tab Containers and the Carousel-style patterns built from Flex Containers do not natively swipe; swipe gestures generally require custom JavaScript embedded via an Iframe or the community "Perspective Swipe" style components, since core Perspective components listen for pointer/click, not swipe deltas, out of the box.
- **Pinch-to-zoom** — supported natively on components that embed images/SVGs/maps (the Perspective Map component, the built-in Image component with pan/zoom enabled) but not general-purpose across the canvas; the page itself should have `user-scalable=no` considerations handled via the viewport meta tag Perspective sets automatically to avoid the whole page zooming when a user pinches a chart.
- **Pull-to-refresh** — not native; must be built manually (scroll-position listener + threshold + a script call to re-run bindings) or omitted in favor of an explicit refresh button, which is the more common integrator choice because native pull-to-refresh conflicts with the browser's own pull-to-refresh gesture on some Android Chrome versions, causing accidental double-refresh or page reloads that drop session state.

### 4.3 Gotcha: double-tap-to-zoom vs. double-click bindings
If a component has an `onDoubleClick` script action, mobile Safari's double-tap-to-zoom gesture competes with it — the first tap may register as a zoom rather than firing the second click of the pair. Explicitly disabling page zoom (viewport `maximum-scale=1`) resolves this but also disables legitimate pinch-zoom on maps/trends elsewhere on the page — a trade-off, not a free fix. Decide per-project whether any view uses double-click actions before disabling zoom globally.

## 5. Offline Capability & Synchronization

Perspective is fundamentally a thin client over a WebSocket to the Gateway — there is no local database or local scripting runtime. **True offline operation (create/edit records with no connectivity) is not a built-in Perspective capability.** What Perspective mobile *does* offer:

- **Service worker asset caching** — once a PWA is installed, the service worker caches the compiled JS/CSS/fonts, so the shell loads instantly and shows a "reconnecting" state instead of a blank white screen when Wi-Fi drops, rather than true offline data entry.
- **Session reconnect / resilience** — Perspective's WebSocket auto-reconnects when connectivity returns, and the Gateway restores session state (open views, prop values) rather than forcing a full re-login, so a brief tunnel/elevator/warehouse dead-zone doesn't lose the operator's place.
- **Read-only cached views (custom)** — some integrators pre-fetch key tag values into `session.props` or `page.props` and rely on the browser's in-memory state to keep the last-known values visible while disconnected, with an explicit "stale data — last updated HH:MM" banner driven off a timestamp prop. This is the most common practical "offline" pattern: not writing while offline, just tolerating brief network loss without a blank/broken UI.
- **Local storage for form drafts** — a script can write partially-filled form data to browser `localStorage` (via a Message Handler calling into a JS interop, or the community Web Dev module) so an in-progress work order survives a reload/reconnect, then syncs (writes to tags/DB) once connectivity is confirmed live.

Gotcha: clients coming from a Vision or a legacy "ruggedized MES app" background often assume Perspective mobile behaves like a native offline-first app (think: fill in a batch record in a Faraday-caged area, sync later). That is **not** what ships out of the box — it requires either a genuinely separate native app with local storage (outside Ignition) talking to the Gateway's REST/webservice endpoints when back online, or accepting the caching/localStorage-draft pattern above with its limits (data loss risk if the browser tab is force-closed before a reconnect flushes the draft). Set this expectation with the client during scoping, not after a plant-floor pilot with dead zones.

## 6. Camera & Device Sensor Access

Perspective exposes camera and sensor access through a small set of components/scripts backed by browser Web APIs (`getUserMedia`, `DeviceOrientationEvent`, Geolocation API), which means capability depends entirely on the mobile browser/OS granting permission — not on an Ignition-side driver.

- **Barcode/QR Scanner component** — see Section 7, camera-backed.
- **File Upload component with camera capture** — on mobile browsers, a File Upload component's `accept="image/*"` combined with the `capture` attribute (configurable in recent 8.1/8.3 builds) opens the native camera directly rather than a file picker, letting an operator snap a photo of a nameplate or defect and attach it to a work order.
- **Device orientation/motion** — accessible via a script calling into the browser's `DeviceOrientationEvent`/`DeviceMotionEvent` through Perspective's JavaScript interop (Message Handlers triggering client-side JS, or community-built components); not a first-class Perspective property panel item as of 8.3, so expect to write custom interop for tilt-based UI (e.g., auto-rotating a gauge dashboard).
- **Microphone** — same `getUserMedia` path as camera, generally used for voice-note attachments; requires HTTPS (mobile browsers refuse camera/mic access on plain HTTP, which trips up integrators testing against an internal Gateway without a valid TLS cert — see Operations doc for the HTTPS requirement).

Gotcha: iOS Safari requires the camera/mic permission prompt to originate from a **direct user gesture** (a tap handler), not a script fired by a timer or a tag-change binding. A "silently open camera when tag X goes true" pattern that works fine on desktop Chrome will be blocked outright on iOS Safari; the workaround is always routing through an explicit button tap.

## 7. Barcode/QR Scanning Integration

Perspective 8.1+ ships a dedicated **Barcode Reader / Scanner component** in the component palette that:

- Opens the device camera in a live-preview overlay and decodes 1D barcodes (Code128, EAN, UPC) and 2D codes (QR, Data Matrix) client-side in the browser, firing an `onDecode` (or equivalent) event with the decoded string.
- Requires HTTPS (camera permission gate, same as above) and an explicit tap to launch, for the same iOS-gesture reason.
- Works acceptably on modern phone cameras but is noticeably slower/less reliable in low light or on damaged/curved labels compared to a purpose-built hardware scanner engine.

For serious industrial scanning (warehouse pick lines, high-volume receiving), the more robust pattern is **hardware scanner emulation**: a Zebra/Honeywell handheld configured in "keyboard wedge" mode injects scanned characters as if typed, landing directly in a focused Perspective Text Field bound to a tag or a script — this avoids the camera-decode component entirely and is dramatically faster and more reliable, at the cost of needing dedicated hardware rather than a BYOD phone. Many production deployments use the in-browser Barcode component for occasional/BYOD scans and keyboard-wedge hardware scanners for high-throughput stations.

Gotcha: the camera-based Barcode component competing for the same camera hardware as a WebView wrapper's native scanner SDK (if a client built a custom wrapper with a faster native decode library) can cause permission conflicts — pick one scanning path per app and don't mix.

## 8. Location Services & Geofencing

- **Geolocation** — Perspective can request the browser's Geolocation API (`navigator.geolocation`) via script/JS interop to get lat/long, typically wired into a Map component to show "you are here" alongside asset pins, or logged to a tag/DB for field-technician location stamping on work orders.
- **Accuracy caveat**: browser geolocation on mobile is GPS-backed outdoors (a few meters) but degrades sharply indoors/underground (Wi-Fi/cell-tower triangulation, tens to hundreds of meters) — a plant-floor "which zone is this operator in" use case built on browser geolocation alone is usually not accurate enough; indoor use cases typically pair it with BLE beacons or a manual zone-select dropdown instead.
- **Geofencing** — not a native Perspective feature; there is no built-in "fire an alarm when device exits polygon X." It's built manually: periodically poll geolocation (script + timer, mindful of battery drain — see Operations doc), compute point-in-polygon against a stored geofence boundary (Gateway-side scripting, since the math is easier server-side with the full boundary dataset), and raise a tag/alarm on transition. Treat this as a custom scripting project, not a checkbox feature.
- **Permission timing**: same iOS-gesture rule as camera — request location access from a tap, and expect users to decline the permission prompt a meaningful percentage of the time; always design a graceful fallback (manual entry) rather than a hard block on location.

## 9. Device Notifications

- **Browser Push (Web Push API)** — Perspective does not ship first-class push notification configuration in the Designer as of 8.3; achieving push-to-phone typically means either (a) the PWA's service worker subscribing to Web Push (requires a backend push service — Gateway scripting calling a provider like Firebase Cloud Messaging, plus VAPID key setup — entirely custom integration work), or (b) routing alerting through **Ignition's existing Alarm Notification Pipelines** using SMS/email/voice-call notification profiles (Twilio, SMTP) rather than a true OS-level push banner. Most production deployments use (b) because it reuses the mature Alarm Notification system rather than building custom Web Push infrastructure.
- **In-app toast/banner components** — Perspective's Message/Alarm/Notification-style components (or a custom banner built from a Popup/View) can surface a visible in-session alert while the app is open and foregrounded, but these do not fire if the app/tab is backgrounded or closed — a fundamental limitation of browser-based delivery versus a true native push notification.
- **Native wrapper push** — a custom WebView-wrapped app (Section 1) *can* integrate true native push (APNs/FCM) because it's a real native shell, but that's outside Perspective itself and is bespoke per-project engineering.

Gotcha: clients frequently ask for "push a notification to the operator's phone when the alarm fires" expecting an OS banner like a consumer app. The honest answer in stock Ignition 8.3 is: email/SMS via Alarm Notification Pipelines gets there reliably; true silent-app push requires either FCM/Web-Push custom integration or a native wrapper — set that expectation early in scoping.

## 10. App Distribution (iOS, Android, Web)

- **Web (all platforms)** — simplest path: publish the Gateway's Perspective project URL (behind a reverse proxy/VPN as appropriate for the network) and users bookmark it in any mobile browser. No install, no app-store review, instant updates on every page load (subject to service-worker cache invalidation, see Operations doc).
- **PWA install (recommended "app-like" path)** — ensure the Perspective project has a valid web app manifest (name, icons, `display: standalone`, theme color — configurable in Gateway/Project properties for Perspective) and is served over HTTPS; Chrome/Edge on Android and Safari on iOS 16.4+ then offer "Add to Home Screen," producing a full-screen icon with no browser chrome. This is Inductive Automation's actual supported "mobile app" story for 8.3 — no code signing, no app-store account, no review process.
- **Android sideload / MDM push** — for a genuine `.apk`, a custom WebView wrapper (Section 1) is built (Capacitor/Cordova are common choices since they're well-documented for wrapping a URL), then distributed via an MDM (Intune, Workspace ONE, SOTI MobiControl) that silently pushes the app to enrolled company devices — no Play Store listing needed for internal-only fleets, though a private/internal Play Store track is also viable for larger fleets.
- **iOS enterprise distribution** — same WebView-wrapper concept, distributed via Apple Business Manager + MDM (no public App Store listing required for internal apps), which requires an active Apple Developer Enterprise Program membership — a real annual cost and approval process integrators should budget for early if a client insists on a native-feeling iOS icon rather than a PWA.
- **App Store / Play Store public listing** — rare for industrial Ignition deployments (these are almost always internal operator/technician tools, not consumer apps) but technically possible with the same WebView-wrapper approach plus standard store review; mentioned for completeness, not commonly chosen.

Gotcha: whichever distribution path is chosen, the wrapper/PWA is still just pointing at a Gateway URL — every device still needs real network reachability to that Gateway (VPN, site-to-site, or public-facing reverse proxy with proper auth). "Installing the app" does not embed any offline application logic; it is fundamentally the same thin client discussed in Section 5, just with a nicer icon and fuller-screen chrome.

---

## See Also

**Prerequisites:** [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)

**Builds toward:** [93-MOBILE-MODULE-OPERATIONS](93-MOBILE-MODULE-OPERATIONS.md)

**Related:** [93-MOBILE-MODULE-OPERATIONS](93-MOBILE-MODULE-OPERATIONS.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md), [70b-MODULES-INDEX-MASTER](70b-MODULES-INDEX-MASTER.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
