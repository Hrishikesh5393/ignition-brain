# TOC: references/ignition-8-3/tags-alarms-historian.md

716 lines, ~23.1k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L7-8 (0.0k) ## Tag system model
  L9-22 (0.2k) ### What a tag is
  L23-40 (0.6k) ### Tag Providers (realtime vs. historical)
  L41-54 (0.4k) ### Tag types (Value Source)
  L55-87 (0.6k) ### Tag paths — the `[provider]Folder/Tag` syntax
  L88-96 (0.3k) ### Data types
  L97-120 (0.7k) ### Tag properties (complete reference)
  L121-204 (1.5k) ### Quality / QualifiedValue model
  L205-222 (0.6k) ### Scan classes / tag groups (execution model)
  L223-247 (0.7k) ### System tags
  L248-255 (0.4k) ### Tag Browser / Tag Editor UI
  L256-261 (0.2k) ### Creating tags and addressing individual bits
  L262-292 (0.7k) ### Exporting and importing tags
  L293-300 (0.5k) ### Tag Diagnostics and the Tag Reference Tracker
  L301-306 (0.3k) ### Tag Report Tool
L307-310 (0.1k) ## UDTs
  L311-318 (0.2k) ### Definition vs. instance workflow
  L319-322 (0.1k) ### Root Node properties
  L323-338 (0.6k) ### Inheritance vs. nesting — different concepts
  L339-345 (0.2k) ### What breaks when you edit a Definition in place
  L346-412 (1.0k) ### Parameters
  L413-421 (0.2k) ### Designing UDTs well (patterns pulled from the docs)
L422-425 (0.1k) ## Tag events and scripting
  L426-437 (0.3k) ### The `event` object / script arguments
  L438-448 (0.2k) ### Gateway tag change scripts vs. tag event scripts
  L449-456 (0.2k) ### Threading / performance rules
L457-458 (0.0k) ## Tag historian
  L459-469 (0.5k) ### Storage pipeline (how a value becomes a history record)
  L470-481 (0.3k) ### Deadband styles (Discrete vs. Analog compression)
  L482-489 (0.4k) ### Interpolation, seed values, raw queries
  L490-509 (1.1k) ### History providers ("Historians")
  L510-517 (0.3k) ### Querying / API surface
  L518-521 (0.2k) ### Aggregation modes
  L522-527 (0.2k) ### Pruning
  L528-538 (0.5k) ### 8.3 historian changes
L539-540 (0.0k) ## Alarming
  L541-544 (0.1k) ### Alarm sources
  L545-571 (1.0k) ### Configuration properties on tags (full set)
  L572-582 (0.6k) ### Alarm states and lifecycle (Active/Clear/Ack)
  L583-588 (0.1k) ### Priorities, shelving
  L589-600 (0.6k) ### Alarm journal
  L601-604 (0.2k) ### Alarming schedules
  L605-610 (0.2k) ### Alarm expressions / bindings
L611-614 (0.1k) ## Alarm notification
  L615-618 (0.1k) ### Notification contact info
  L619-622 (0.3k) ### Defining a Twilio account
  L623-636 (0.7k) ### Pipelines
  L637-661 (1.0k) ### Pipeline block types
  L662-665 (0.1k) ### On-call rosters
  L666-676 (0.9k) ### Notification profile types
  L677-683 (0.4k) ### Worked pipeline patterns
  L684-691 (0.3k) ### Escalation and the two-way ack flow
L692-716 (1.7k) ## Gotchas and 8.3 notes
