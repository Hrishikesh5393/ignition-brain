> **Component category:** Display · **Index:** [Component Index](../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

# Audio (Player)

**Category:** Display / General | **Ignition:** ia.display.audioPlayer

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`) — the actual runtime schema, not just written docs.

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| source | string | "" | ✓ | Audio file path/URL |
| play | boolean | false | ✓ (bidirectional) | Toggle to start/pause playback — there is no 3-state `playing`/`paused`/`stopped` string |
| loop | boolean | false | ✓ | Loop playback |
| volume | number | 100 | ✓ | 0–100 (a percentage, not a 0.0–1.0 fraction) |
| playbackRate | number | 1 | ✓ | Playback speed multiplier |
| display | boolean | — | ✓ | Component visibility |
| allowDownload | boolean | false | ✓ | Allow the browser's download control on the player |
| style | object | {} | ✓ | Container CSS |

There is no `playbackState`, `muted`, `showControls`, or `currentTime` property — playback is controlled with the boolean `play`, volume is 0–100 not 0.0–1.0, and there's no exposed mute toggle or seek/currentTime readback.

## Data Binding Examples

```javascript
// Static alarm sound resource
source: "Sounds/alarm-horn.mp3"

// Trigger playback from an alarm active tag via a script
self.getSibling("Audio").props.play = True

// Volume tied to an operator-adjustable setting
volume: {tag: "[default]UI/Settings/AlarmVolume"}
```

## Common Gotchas
- `play` is a plain boolean toggle, not a 3-state string — flip it `true` to start, `false` to pause. There's no `stopped` state distinct from `false`/paused-at-zero.
- `volume` is 0–100 (percentage), not 0.0–1.0 — setting `volume: 0.5` expecting half volume actually sets it to ~0.5%.
- Browsers block **autoplay with sound** until the user has interacted with the page at least once — a binding that flips `play` to `true` on view load may be silently blocked; require a user gesture (e.g. an "Enable Sound" button) first for reliable alarm-sound UX.
- Looping alarm sounds (`loop: true`) need an explicit stop condition tied back to the alarm/tag going inactive, or the sound plays indefinitely even after the operator navigates away in some session configurations.
- Supported formats depend on the client browser's codec support — MP3 is safest for cross-browser compatibility; OGG may not play in all Safari versions.

---

## See Also

**Category index:** [Component Index](../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../21-BINDINGS.md)

[↑ Back to Component Index](../00-Component-Index.md) · [↑ Back to KB INDEX](../../00-INDEX.md)
