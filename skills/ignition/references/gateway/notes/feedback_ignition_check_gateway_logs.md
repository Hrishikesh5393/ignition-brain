---
name: feedback-ignition-check-gateway-logs
description: "Always check Ignition gateway logs (get_gateway_logs) proactively during Ignition work, not just when something visibly breaks"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 73fda676-3a9b-4234-851f-8c4403970773
  modified: 2026-08-07T08:19:35.713Z
---

Make a habit of checking the Ignition gateway logger (`mcp__ignition-mcp__get_gateway_logs`, WARN level is a good default) proactively while doing Ignition work - not only when something visibly fails.

**Why:** During the AHU_Control_Demo session, checking logs on request (rather than only reacting to visible symptoms) surfaced two real issues that weren't otherwise obvious: (1) a `dataType` value ("Int4" vs the correct "Integer") silently warned instead of erroring on UDT parameter writes, self-corrected but would've gone unnoticed; (2) historian INSERT batches taking 2-4+ minutes on `sqlt_data_*`/`alarm_event_data` tables - a real performance problem invisible from the Designer/Perspective UI. The gateway logs full stack traces (a `stack` field, not just `message`) even for WebDev/script errors that return an empty HTTP body to the client - this was the only way earlier in the session to diagnose a `StackOverflowError` in `org.json.JSONObject.populateMap` that no amount of guessing at API usage would have found.

**How to apply:** After any batch of tag/UDT/project edits via `edit_tags`/`create_tags`/`set_project_resource`, or when a live query/script/webdev call returns an ambiguous result, pull recent WARN-level logs and actually read the `stack` field on suspicious entries, not just `message`. Treat "it returned Good/200" as necessary but not sufficient - cross-check the log for warnings the API call itself didn't surface.
