# TOC: references/ignition-8-3/scripting-model-and-designer.md

709 lines, ~21.3k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L7-14 (0.3k) ## Execution scopes
  L15-40 (0.4k) ### How scope is enforced
  L41-65 (0.5k) ### What's available where (by the numbers)
  L66-77 (0.4k) ### Threading model
L78-98 (0.3k) ## Python / Jython in Ignition
  L99-119 (0.7k) ### Coming from CPython 3 — what trips people up
  L120-133 (0.8k) ### Built-in data structures at a glance
  L134-153 (0.4k) ### Control flow and built-ins quick reference
  L154-194 (0.6k) ### User-defined functions and scope
  L195-213 (0.7k) ### JSON in Ignition
L214-217 (0.0k) ## Where scripts live
  L218-224 (0.4k) ### Project Library (`shared`/project scripts)
  L225-240 (0.7k) ### Gateway Event Scripts
  L241-258 (0.5k) ### Client / Session event scripts
  L259-261 (0.1k) ### Component event handlers
  L262-264 (0.1k) ### Tag event scripts
  L265-276 (0.4k) ### Expression vs script (choosing the right tool)
  L277-283 (0.3k) ### Other scripting touchpoints
  L284-288 (0.2k) ### The Script Console
L289-318 (0.5k) ## Message handlers
L319-320 (0.0k) ## Named resources and project structure
  L321-334 (0.3k) ### The `resource.json` file
  L335-337 (0.2k) ### Resource types & where they live on disk
  L338-340 (0.2k) ### 8.3's biggest structural change: Gateway config is now files too
  L341-347 (0.4k) ### Project export and import
  L348-352 (0.3k) ### Project inheritance
  L353-360 (0.3k) ### What this means for git / version control
L361-362 (0.0k) ## Designer
  L363-365 (0.2k) ### Layout & docking
  L366-368 (0.1k) ### Project Browser
  L369-371 (0.0k) ### Tag Browser
  L372-374 (0.2k) ### Comm Mode (Designer/Client data safety switch)
  L375-377 (0.2k) ### Resource locking / concurrent editing & designer communication
  L378-389 (0.4k) ### Designer tool inventory
  L390-408 (0.3k) ### Keyboard shortcuts worth knowing (developer-relevant subset)
  L409-411 (0.1k) ### Symbol reference
  L412-421 (0.3k) ### Saving, updating, and resolving conflicts
  L422-435 (0.4k) ### Project properties reference (Designer → Project → Project Properties)
  L436-438 (0.2k) ### Project templates
  L439-441 (0.1k) ### Concurrent editing in practice: what actually gets checked
  L442-456 (0.5k) ### Designer Diagnostics (Help → Diagnostics)
L457-458 (0.0k) ## Localization and languages
  L459-464 (0.2k) ### Model
  L465-467 (0.1k) ### Key naming best practice
  L468-485 (0.3k) ### Locale string formats — the thing most likely to bite a developer
  L486-490 (0.4k) ### Translation Manager workflow
  L491-494 (0.1k) ### Switching language at runtime
  L495-502 (0.2k) ### Vision-specific extras
L503-504 (0.0k) ## Practical guidance
  L505-528 (0.4k) ### Error handling
  L529-540 (0.3k) ### Logging
  L541-555 (0.5k) ### Performance rules
  L556-563 (0.4k) ### Testing / debugging technique
  L564-587 (0.5k) ### Worked troubleshooting example (the docs' own walkthrough)
  L588-657 (1.0k) ### Common scripting recipes (grounded in the docs' own examples)
L658-673 (0.6k) ## Scripting object quick reference
L674-693 (2.1k) ## Tutorials worth knowing
L694-709 (0.8k) ## Gotchas and 8.3 notes
