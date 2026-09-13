> **Component category:** Display · **Index:** [Component Index](../../00-Component-Index.md)
> **Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

# Moving Analog Indicator

**Category:** Display / Industrial | **Ignition:** `ia.display.moving-analog-indicator`

## Overview

A vertical/horizontal scale showing a process value indicator alongside setpoint and alarm-limit markers — richer than Linear Scale, with dedicated properties for setpoint, desired-range band, and up to two-level high/low alarm and interlock limits (modeled on classic DCS/SCADA analog indicator faceplates).

## Properties

**Verified against:** `ia.components.json` (Ignition 8.3.7, `data\jar-cache\com.inductiveautomation.perspective`).

| Property Name | Type | Default | Bindable | Purpose |
|---|---|---|---|---|
| processValue | number | 50 | ✓ | Current process value shown by the indicator |
| setpointValue | number\|null | null | ✓ | Setpoint marker position |
| minValue / maxValue | number | 0 / 100 | ✓ | Scale bounds |
| desiredLow / desiredHigh | number | — | ✓ | Bounds of the "desired" (normal) band |
| lowAlarm / highAlarm | number\|null | — | ✓ | Level-1 (single) alarm limits |
| lowLowAlarm / highHighAlarm | number\|null | — | ✓ | Level-2 (double) alarm limits |
| lowInterlock / highInterlock | number\|null | — | ✓ | Interlock trip limits |
| desiredRangeColor | string (color) | "" | ✓ | Color of the desired-range band |
| defaultRangeColor | string (color) | "" | ✓ | Color of area outside any defined range |
| level1AlarmColor / level2AlarmColor | string (color) | "" | ✓ | Colors for active level-1/level-2 alarm zones |
| inactiveAlarmColor | string (color) | "" | ✓ | Color for a configured-but-inactive alarm zone |
| interlockColor | string (color) | "" | ✓ | Color for the interlock zone |
| indicatorColor | string (color) | "" | ✓ | Process-value indicator color |
| setpointColor | string (color) | "" | ✓ | Setpoint marker color |
| label.visible | boolean | false | ✓ | Show the numeric value label |
| label.format | string | "#,##0" | ✓ | Number format for the label |
| sectionOutline.color / .width | string / number | "" / 2 | ✓ | Border around each range section |
| reverseIndicator | boolean | false | ✓ | Place the process-value indicator on the opposite side of the scale |
| style | object | {} | ✓ | Container CSS |

## Common Gotchas
- Unlike Thermometer/Linear Scale's single `intervals`/`ranges` array, alarm zones here are individually-named properties (`lowAlarm`, `highAlarm`, `lowLowAlarm`, etc.) with dedicated colors — there's no generic band array to configure arbitrarily many zones.
- Level-2 alarms (`lowLowAlarm`/`highHighAlarm`) and interlocks (`lowInterlock`/`highInterlock`) are independent of level-1 alarms — setting only `highAlarm` leaves `highHighAlarm`/`highInterlock` unset (`null`), meaning no level-2/interlock zone renders at all.
- `setpointValue` and `processValue` are two separate markers on the same scale — don't confuse the setpoint marker with the live value indicator when wiring bindings.

---

## See Also

**Category index:** [Component Index](../../00-Component-Index.md)

**Core KB:** [12-COMPONENT-REFERENCE](../../../12-COMPONENT-REFERENCE.md), [14-APPENDIX-COMPONENTS-DETAILED](../../../14-APPENDIX-COMPONENTS-DETAILED.md), [21-BINDINGS](../../../21-BINDINGS.md)

[↑ Back to Component Index](../../00-Component-Index.md) · [↑ Back to KB INDEX](../../../00-INDEX.md)
