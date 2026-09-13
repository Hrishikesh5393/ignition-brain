> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Video Player

**Category:** Display / General | **Ignition:** ia.display.videoPlayer

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| source | string | "" | ✓ | Video file path/URL or stream URL |
| liveFeed | boolean | false | ✓ | Set `true` for a live camera feed — hides `poster`/`controls`/`status`/`controlStyle` (they only apply to non-live playback) |
| poster | string | "" | ✓ | Background image shown before playback starts (non-live only) |
| autohideControls | boolean | false | ✓ | Auto-hide controls when not hovering (non-live only) |
| controls.autoplay | boolean | false | ✓ | Autoplay on load (starts muted per browser policy) |
| controls.loop | boolean | false | ✓ | Loop playback |
| controls.mute | boolean | false | ✓ | Mute toggle |
| controls.play | boolean | false | ✓ | Play/pause toggle — no 3-state `playbackState` string |
| controls.seek | number | 0 | ✓ | Set to jump playback position (seconds) |
| controls.volume | number | 75 | ✓ | 0–100 (percentage, not 0.0–1.0) |
| controls.playRate | number | 1 | ✓ | Playback speed multiplier |
| status.playing / .paused / .ended / .waiting / .seeking | boolean (read) | false | ✓ | Read-only playback state flags |
| status.progress | number (read) | 0 | ✓ | Current playback position in seconds (read this, don't read `currentTime`) |
| status.loadedData | boolean (read) | false | ✓ | First frame has loaded |
| controlStyle | object | {} | ✓ | Style for the transport controls (non-live only) |
| style | object | {} | ✓ | Container CSS |

There is no `playbackState` (use boolean `controls.play`), no top-level `muted`/`volume`/`loop` (they're all under `controls.*`), no `showControls` toggle, and no `currentTime` (reading position is `status.progress`; setting/seeking position is `controls.seek`).

## Data Binding Examples

```javascript
// Static training video resource
source: "Videos/lockout-tagout-training.mp4"

// Live camera stream URL from a tag (RTSP-to-HLS gateway proxy URL typically required)
source: {tag: "[default]Cameras/Line1/StreamUrl"}
liveFeed: true

// Auto-play a safety video (muted, per browser policy) when a station's door interlock opens
controls.autoplay: {expr: "{Root.Door.open}"}
controls.mute: true

// Read playback position for a synced progress bar elsewhere in the view
// (status.progress is read-only; use controls.seek to programmatically jump position)
```

## Common Gotchas
- `controls.play` is a plain boolean, not a 3-state `playbackState` string — there's no separate "stopped" state distinct from paused-at-zero.
- `controls.volume` is 0–100 (percentage), not 0.0–1.0.
- Playback position is split: `status.progress` is the read-only current position; `controls.seek` is what you write to jump to a position — there's no single bidirectional `currentTime`.
- `poster`, `autohideControls`, `controls.*`, `status.*`, and `controlStyle` are all hidden/inactive when `liveFeed: true` — a live camera feed has no scrubber/poster/loop concept.
- Same autoplay-with-sound restriction as the Audio component — browsers require a user gesture before unmuted autoplay succeeds; pair `controls.autoplay: true` with `controls.mute: true` if autoplay on view-load is required.
- Raw RTSP camera streams are **not** directly playable in-browser — they must be transcoded/proxied (e.g. through a media server producing HLS/mp4) before the URL is usable in `source`.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
