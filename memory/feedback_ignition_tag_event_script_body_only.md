---
name: feedback-ignition-tag-event-script-body-only
description: "When configuring Ignition tag eventScripts via system.tag.configure/tagConfig API, only pass the function BODY, not the def line"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c00a8add-3c58-428d-a8b3-a0258dba70b7
  modified: 2026-07-24T11:38:21.190Z
---

Ignition's tag config schema (`eventScripts: [{"eventid": "valueChanged", "script": "..."}]`) already wraps the script in `def valueChanged(tag, tagPath, previousValue, currentValue, initialChange, missedEvents):` internally. The `script` string must contain only the indented body - never include the `def ...():` line itself.

**Why:** User caught this directly after testing on the local Ignition 8.3 gateway ([[project_photonic_barcode_lookup]]) - sending the full file (with `def valueChanged(...):` included) as the eventScripts payload would double-wrap or break the script.

**How to apply:** When writing any tag-event/valueChanged script destined for `system.tag.configure`'s `eventScripts` property (via API/WebDev, not pasted manually in Designer's Tag Editor UI), strip the `def valueChanged(...):` line and pass only the indented body underneath it.
