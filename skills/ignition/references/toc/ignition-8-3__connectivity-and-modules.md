# TOC: references/ignition-8-3/connectivity-and-modules.md

692 lines, ~18.9k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L7-10 (0.1k) ## Module catalog
  L11-29 (0.8k) ### Core modules
  L30-39 (0.2k) ### Additional modules
  L40-46 (0.2k) ### Cloud Connector modules
  L47-59 (0.2k) ### "Which module do I need for X?" quick answers
L60-63 (0.1k) ## OPC UA
  L64-70 (0.2k) ### Ignition as OPC UA client vs. server
  L71-91 (0.4k) ### Ignition's OPC UA Server settings (**Connections > OPC > OPC UA Server Settings**)
  L92-142 (0.9k) ### OPC UA Connections (Ignition as client) — `Connections > OPC > Connections`
  L143-146 (0.1k) ### OPC UA Security (`Connections > OPC > Security Settings`)
  L147-151 (0.2k) ### Discovery, browsing, and the OPC Quick Client
  L152-175 (0.4k) ### Subscriptions, sampling, and diagnostic tags
L176-179 (0.1k) ## Device drivers
  L180-199 (0.4k) ### Quick reference — port, OS and browsability by driver
  L200-237 (0.8k) ### Allen-Bradley (EtherNet/IP)
  L238-269 (1.1k) ### Siemens (S7 protocol over TCP/IP)
  L270-325 (1.1k) ### Modbus (TCP, RTU over TCP, RTU)
  L326-343 (0.8k) ### BACnet (BACnet/IP over UDP; router needed for other media)
  L344-364 (0.8k) ### DNP3 (two drivers, water/electric-utility protocol)
  L365-378 (0.7k) ### IEC 61850 (substation / MMS client — no GOOSE/SV)
  L379-390 (0.6k) ### Mitsubishi (MELSEC via TCP, SLMP)
  L391-400 (0.6k) ### Omron — two drivers
  L401-408 (0.3k) ### Programmable Device Simulator
  L409-416 (0.4k) ### UDP and TCP Driver (raw stream ingestion — not a PLC protocol driver)
  L417-420 (0.1k) ### Simulators / testing without hardware
  L421-427 (0.5k) ### Third-party OPC servers
L428-431 (0.1k) ## Event Streams (new in 8.3)
  L432-442 (0.5k) ### Stage pipeline: Source → Encoder → Filter → Transform → Encoder → Buffer → Handler(s) → Error Handler
  L443-446 (0.1k) ### Handler expressions (extracting data/metadata into a handler field)
  L447-451 (0.1k) ### Common handler settings
  L452-466 (0.5k) ### Source types
  L467-473 (0.2k) ### Source Data/Metadata extractable fields (via `{event.data.X}` / `{event.metadata.X}`)
  L474-497 (0.7k) ### Handler types and their properties
  L498-524 (0.4k) ### Testing and monitoring
  L525-540 (0.3k) ### Worked pattern — Kafka topic to a tag write
L541-542 (0.0k) ## Cloud connectors
  L543-554 (0.3k) ### Kafka Connector
  L555-566 (0.3k) ### MongoDB Connector
L567-570 (0.1k) ## Web Dev module
  L571-577 (0.2k) ### Resource types (right-click "Web Dev" in Designer's Project Browser)
  L578-581 (0.0k) ### Python resource HTTP methods
  L582-594 (0.2k) ### Return value dict keys (evaluated in this priority order; `contentType` can override any of them)
  L595-608 (0.2k) ### `request` object
  L609-612 (0.1k) ### `session` object
  L613-616 (0.1k) ### URL routing
  L617-622 (0.2k) ### Security settings (per Python resource, per HTTP method)
  L623-628 (0.2k) ### Worked example — simple test server
L629-648 (0.4k) ## JDBC drivers
L649-666 (0.5k) ## Redundancy & failover cheat sheet
L667-692 (1.0k) ## Gotchas and 8.3 notes
