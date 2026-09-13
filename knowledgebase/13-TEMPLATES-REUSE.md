---
title: Templates & Component Reuse
description: Embedded views, parameterized components, patterns
---

> **Skill level:** 200 · **Read first:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 13-TEMPLATES-REUSE

# Templates & Reusable Components

Build once, use everywhere.

## Embedded Views

**View** = Reusable container with parameters.

**Create:**
```
Designer → Right-click → New View
Name: CardTemplate
Purpose: Reusable card component
```

**Add parameters:**
```
View → Configure View
Parameters:
- title (string)
- value (number)
- color (string)
- status (string)
```

**Add components:**
```
Container
├── Label (text: {view.params.title})
├── Label (text: {view.params.value})
│   style.color: {view.params.color}
└── Label (text: {view.params.status})
```

**Use in parent view:**
```
Designer → Drag Embedded View onto canvas
Select: CardTemplate
Properties → Bind parameters:
- title: "Production Count"
- value: {[default]DailyCount}
- color: {[default]Status} == 'ok' ? 'green' : 'red'
- status: {[default]Status}
```

**Reuse multiple times:**
```
Row 1: Card (Production)
Row 2: Card (Quality)
Row 3: Card (Temperature)
Row 4: Card (Pressure)
```

All cards use same CardTemplate layout, different data.

## Repeater with Embedded View

**Repeat component over dataset:**
```
Repeater Component
├── dataset: {tag: "[sql]ProductionLines"}
└── Embedded View: LineCard
    - Receives row: {data[0], data[1], data[2], ...}
```

**LineCard view:**
```
Container (flex column)
├── Label (text: {view.parent.data.line_name})
├── Progress Bar (value: {view.parent.data.production_pct})
└── Label (text: {view.parent.data.status})
```

**Result:** One card per production line, auto-generated.

## Parameterized Components

**Input component with validation:**
```
Numeric Input
Props:
- value: {tag: "[default]Setpoint"}
- min: 0
- max: 100
- step: 5
- unit: "°C"

Events:
- onChange: 
  if self.props.value > 80:
      system.alarm.acknowledge(...)
```

**Use pattern:**
Template once, bind different tags in each view.

## Template Library

**Best practice:** Create folder of templates
```
Project Structure:
├── templates/
│   ├── CardTemplate
│   ├── DataTableTemplate
│   ├── AlarmPanelTemplate
│   └── HeaderTemplate
├── views/
│   ├── DashboardHome
│   ├── Production
│   ├── Quality
│   └── Reports
```

**Consistency:** All dashboards use same header, styling, layout.

## Parameterized Scripts

**Reusable script function:**

```python
def format_status(value):
    if value > 100:
        return "CRITICAL"
    elif value > 80:
        return "WARNING"
    else:
        return "OK"

# Call from component binding:
{expr: "formatStatus({[default]Sensor})"}
```

## Inheritance Pattern

**Parent view → Child views inherit common elements:**

```
BaseView (header, menu, footer)
├── DashboardView (extends BaseView)
│   ├── ProductionCard
│   ├── QualityCard
│   └── AlarmPanel
└── ReportView (extends BaseView)
    ├── TableComponent
    ├── FilterPanel
    └── ExportButton
```

**Implementation:** Embedded view of BaseView, then add custom content.

## CSS/Styling Reuse

**Shared CSS classes:**
```css
/* In view style properties */
.card {
  background: #f0f0f0;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.status-ok {
  color: #00cc00;
}

.status-alarm {
  color: #ff0000;
}
```

**Apply to components:**
```
Label
├── style.classes: ["card-title"]

Indicator
├── style.classes: {[default]Status} == "ok" ? ["status-ok"] : ["status-alarm"]
```

---
**Golden Rule:** If writing same component 3+ times, make template.

---

## See Also

**Prerequisites:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [10-PERSPECTIVE-OVERVIEW](10-PERSPECTIVE-OVERVIEW.md)

**Builds toward:** [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)

**Related:** [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md), [27-PLATFORM-UDTS-QUERIES](27-PLATFORM-UDTS-QUERIES.md), [21-BINDINGS](21-BINDINGS.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
