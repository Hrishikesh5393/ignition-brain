> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Map

**Category:** Display / Mapping | **Ignition:** ia.map.map

## Properties

**Verified against:** `perspective-map.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs. This is a Leaflet-based open-tile map, distinct from the Google Map component.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| init.center.lat / init.center.lng | number | — | ✓ | Initial map center (load-time only) |
| init.zoom | number\|null | null | ✓ | Initial zoom level (load-time only) |
| location.enabled | boolean | false | ✓ | Use browser geolocation |
| location.showHeadingIndicator | boolean | true | ✓ | Show device heading indicator |
| zoom.controls | boolean | true | ✓ | Show zoom UI control |
| zoom.min / zoom.max | number\|null | null / null | ✓ | Zoom bounds |
| zoom.delta / zoom.snap | number | 1 / 1 | ✓ | Zoom step size / snap-to-multiple |
| zoom.onScrollWheel / zoom.onDoubleClick / zoom.onBoxZoom | boolean | true / true / true | ✓ | Interaction toggles for zoom gestures |
| customControls | array | [] | ✓ | Custom view-based controls anchored to a map corner: `{path, params, position, enabled}` |
| attribution | boolean | true | ✓ | Show tile-provider attribution control |
| closePopupsOnClick | boolean | true | ✓ | Close open popups when the map is clicked |
| trackResize | boolean | false | ✓ | Auto-adjust on browser window resize |
| keyboardNav | boolean | true | ✓ | Arrow-key/+/- keyboard navigation |
| keyboardPanDelta | number | 80 | ✓ | Pixels panned per arrow-key press |
| dragging | boolean | true | ✓ | Mouse/touch drag-to-pan |
| maxBounds.corner1 / maxBounds.corner2 | object `{lat,lng}` | — | ✓ | Restricts pannable area to a bounding box |
| fadeAnimation | boolean | true | ✓ | Tile fade-in animation |
| layers.raster.tile | array | [] | ✓ | Tile layer(s), e.g. `{url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}` |
| layers.vector.polygon / .polyline / .rectangle / .circle | array | [] | ✓ | Vector shape overlay layers |
| layers.ui.marker | array | [] | ✓ | Marker layer(s) — this is where marker data actually lives |
| layers.ui.popup / layers.ui.view | array | [] | ✓ | Popup / embedded-view overlay layers |
| layers.other.geoJSON | array | [] | ✓ | GeoJSON feature layers (good candidate for an HTTP binding) |
| hideViewMarkersOnZoom | boolean | true | ✓ | Hide view-layer markers while repositioning during zoom |
| style | object | {} | ✓ | Container CSS |

There is no top-level `markers`, `polygons`, `polylines`, or `center` property. Initial center/zoom are under `init`; all overlay data (markers, polygons, polylines, tiles) lives under `layers.*`, mirroring the Google Map component's `layers` structure. There is also no dedicated `selection` object — read marker interaction state via the marker layer's own item config, not a component-level `selection.data`.

## Data Binding Examples

```javascript
// Initial view — load-time only
init: {center: {lat: 39.8, lng: -98.5}, zoom: 4}

// Tile provider
layers.raster.tile: [{url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"}]

// Plot facility locations from a query, inside the marker layer
layers.ui.marker: {query: {
  sql: "SELECT site_name AS label, latitude AS lat, longitude AS lng, site_id FROM sites",
  database: "default"
}, transform: "script: wrapAsMarkerLayerItems"}
```

## Common Gotchas
- No `apiKey`/billing dependency (unlike Google Map) — this is the offline/open-tile-provider option, but you must supply your own `layers.raster.tile` URL template (e.g. OpenStreetMap) since none is set by default.
- `init.center`/`init.zoom` only apply on load — there's no live "recenter" property; recentering at runtime needs a client-side script call, not a property write.
- Marker, polygon, polyline, and tile data all live under `layers.*` (raster/vector/ui/other), not as flat top-level properties — binding to a nonexistent top-level `markers` prop silently does nothing.
- Vector layer point arrays (`layers.vector.polygon`/`.polyline`) must be closed/ordered correctly or the shape renders self-intersecting/garbled — validate geometry server-side rather than hand-building coordinate arrays.
- Large marker counts (thousands) in `layers.ui.marker` without clustering can degrade pan/zoom performance.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
