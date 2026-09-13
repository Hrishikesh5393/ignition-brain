> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Google Map

**Category:** Display / Mapping | **Ignition:** ia.map.google-map

## Properties

**Verified against:** `perspective-googlemap.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| init.center.lat / init.center.lng | number\|null | null / null | ✓ | Initial map center (only applied on load, not a live re-center control) |
| init.zoom | number\|null | null | ✓ | Initial zoom level |
| backgroundColor | string (color) | "" | ✓ | Background shown while tiles load |
| clickableIcons | boolean | true | ✓ | Allow map POI icons to be clickable |
| cursor.draggable / cursor.dragging | string | "" / "" | ✓ | CSS cursor name/URL for drag states |
| controlSize | number\|null | null | ✓ | Pixel size of on-map UI controls |
| disableDefaultUI | boolean | false | ✓ | Disable all default UI buttons (keyboard/gesture controlled separately) |
| fullscreen.controls | boolean\|null | true | ✓ | Show fullscreen control |
| gestureHandling | string | "auto" | ✓ | `cooperative`, `greedy`, `none`, `auto` |
| heading | number\|null | null | ✓ | Aerial imagery heading (degrees from North) |
| isFractionalZoomEnabled | boolean\|null | null | ✓ | Allow fractional zoom levels |
| keyboardShortcuts | boolean | true | ✓ | Allow keyboard map control |
| layers.marker[] | array | [] | ✓ | Marker layer(s) — each entry configures `markers[]`, clustering, icon, popup, tooltip |
| layers.circle[] / .polygon[] / .polyline[] / .rectangle[] | array | [] | ✓ | Shape overlay layers |
| layers.overlayView[] / .groundOverlay[] | array | [] | ✓ | Custom/ground image overlay layers |
| layers.traffic.enabled / .bicycling.enabled / .transit.enabled | boolean | false | ✓ | Built-in Google layer toggles |
| layers.kml[] | array | [] | ✓ | KML document layers (`url` per entry) |
| mapId | string | "" | ✓ | Google Cloud-console Map ID (for cloud-based styling) |
| mapType.id | string | "roadmap" | ✓ | `roadmap`, `satellite`, `hybrid`, `terrain` |
| mapType.controls | boolean\|null | true | ✓ | Show map-type switcher control |
| restriction.bounds | object | — | ✓ | `{north, south, east, west}` — restricts pan/zoom to bounds |
| rotate.controls | boolean\|null | true | ✓ | Show rotate control |
| scale.controls | boolean\|null | true | ✓ | Show scale control |
| tilt | 0\|45\|null | null | ✓ | Camera tilt angle |
| zoom.min / zoom.max | number\|null | null / null | ✓ | Zoom bounds |
| zoom.controls | boolean\|null | true | ✓ | Show zoom control |
| style | object | {} | ✓ | Container CSS |

There is no top-level `markers`, `center`, or `apiKey` property. Initial center/zoom live under `init`; ongoing marker data lives under `layers.marker[].markers[]`; the API key is a **project/Gateway-level config**, not a component property at all (see Gotchas).

## Data Binding Examples

```javascript
// Initial view — only applied once, on load
init: {center: {lat: 40.7128, lng: -74.0060}, zoom: 17}
mapType.id: "satellite"

// Plot delivery vehicle GPS positions inside a marker layer
layers.marker: [
  {
    enabled: true,
    markers: {tag: "[default]Fleet/VehiclePositions", transform: "script: mapVehicleArray"}
  }
]
```

## Common Gotchas
- `init.center`/`init.zoom` are load-time only — there's no live "recenter the map" property; recentering at runtime requires a client-side script call against the map's JS instance, not a property binding.
- The Google Maps API key is configured once at the project or Gateway level (Perspective project properties), not as a per-component property — there is no `apiKey` prop to bind.
- Without a valid API key with the Maps JavaScript API enabled and billing active on the Google Cloud project, the map renders a "For development purposes only" watermark or fails to load — this is a Google-side licensing requirement, not an Ignition bug.
- Marker data lives inside `layers.marker[].markers`, one level deeper than commonly assumed — binding directly to a flat top-level `markers` property does nothing since it doesn't exist.
- Satellite/hybrid `mapType.id` imagery is subject to Google's usage terms and additional cost tiers — verify licensing before defaulting production dashboards to satellite view at scale.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
