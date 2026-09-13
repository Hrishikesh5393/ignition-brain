---
title: Perspective - Modern Web UI System
description: Browser-based, responsive, mobile-capable visualization
---

> **Skill level:** 100 · **Read first:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 10-PERSPECTIVE-OVERVIEW

# Perspective (Modern Web UI System)

Perspective is Ignition's modern web-based visualization platform. Browser-based, responsive, mobile-optimized.

## Why Perspective?

- **Responsive** - Adapts desktop, tablet, phone automatically
- **Browser-based** - Access from any device, any browser
- **Mobile** - iOS/Android native support
- **Modern** - Updated components, clean design patterns
- **Easy** - Drag-drop component building in Designer

**When NOT to use:** Legacy systems, heavy Vision-specific features, Windows-only requirements

## Architecture

**Designer** → Creates .view files (XML)
→ **Gateway** stores projects
→ **Browser** (Client) requests view
→ **Perspective runs** (web session per browser)

```
Browser connects to Gateway:8088/data/perspectives/[ProjectName]/[ViewName]
                 ↓
        Ignition serves Perspective engine
                 ↓
        Engine loads .view file from project
                 ↓
        Engine renders components, binds tags
                 ↓
        User interacts, script executes, tags update
```

## View Hierarchy

**Views** = Container for components. Reusable, can nest.

```
Root View
├── Header View (component)
├── Menu View (component)
├── Main Content
│   ├── Chart Component
│   ├── Table Component
│   └── Input Component
└── Footer View (component)
```

## Component Structure

Every component has:
- **Props** - Input properties (text, color, visibility, etc.)
- **Bindings** - Link props to tags or expressions
- **Events** - Trigger scripts on user action
- **Style** - CSS for appearance
- **Children** - Nested components (for containers)

```
Component
├── Props: text, visible, enabled, etc.
├── Bindings: prop → tag/expression
├── Events: onClick, onChange, onFocus, etc.
├── Style: CSS classes/inline
└── Children: nested components
```

## Communication

**Tag Binding** (most common)
```javascript
// In component prop:
{tag:"[default]MyTag"}
```

**Expression Binding**
```javascript
// Math:
{expr:"{tag1} + {tag2}"}

// Conditional:
{expr:"if({tag1} > 100, 'High', 'Normal')"}

// Date:
{expr:"now()"}
```

**Message** (Perspective to Perspective)
```python
# Send message from script:
system.perspective.sendMessage("myMessage", {"value": 123})

# Receive in messageHandler event
```

**HTTP** (to external APIs)
```python
import json
response = system.net.httpPost("https://api.example.com/data", {})
data = json.loads(response)
```

## Session & Context

**Session** = One browser connection. Maintains state, tags, scripts.

**sessionInfo** available in scripts:
```python
info = system.perspective.getSessionInfo()
username = info['user']['name']
roles = info['user']['roles']
```

## Performance Notes

- **Bindings** are efficient - optimized for updates
- **Scripts on change** can be slow if many bindings update simultaneously
- **Table/Tree with many rows** - virtualization helps
- **Polling vs. Push** - Tags push updates, scripts should debounce

## Responsive Design

Perspective automatically responds to screen size:

**Design for breakpoints:**
- Desktop: >1200px
- Tablet: 768-1200px
- Mobile: <768px

Use **Breakpoint Container** or CSS media queries for layout changes.

---
**Key Files:**
- Views stored in: `[Gateway]/data/projects/[ProjectName]/views/`
- Perspective config: `[Gateway]/data/projects/[ProjectName]/project.json`

---

## See Also

**Prerequisites:** [01-ARCHITECTURE-OVERVIEW](01-ARCHITECTURE-OVERVIEW.md), [03-PLATFORM-CORE-CONCEPTS](03-PLATFORM-CORE-CONCEPTS.md)

**Builds toward:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [12-COMPONENT-REFERENCE](12-COMPONENT-REFERENCE.md), [15-PERSPECTIVE-ADVANCED-COMPLETE](15-PERSPECTIVE-ADVANCED-COMPLETE.md)

**Related:** [11-COMPONENTS-PALETTES](11-COMPONENTS-PALETTES.md), [34-APPENDIX-VISION-MODULE](34-APPENDIX-VISION-MODULE.md), [21-BINDINGS](21-BINDINGS.md), [92-MOBILE-MODULE-PERSPECTIVE](92-MOBILE-MODULE-PERSPECTIVE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
