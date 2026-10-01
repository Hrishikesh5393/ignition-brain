# TOC: references/ignition-8-3/security-and-databases.md

676 lines, ~15.6k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L7-24 (0.5k) ## Security model overview
  L25-36 (0.5k) ### The full picture, piece by piece
  L37-49 (0.3k) ### How each surface authenticates/authorizes
L50-51 (0.0k) ## Identity Providers
  L52-66 (0.3k) ### Types and the authentication workflow
  L67-72 (0.2k) ### Internal Ignition IdP
  L73-78 (0.2k) ### OpenID Connect 1.0 Providers
  L79-88 (0.2k) ### SAML 2.0 Providers
  L89-92 (0.1k) ### Redundancy
  L93-126 (0.4k) ### User Attribute Mapping
  L127-139 (0.3k) ### Security Levels
  L140-161 (0.4k) ### Security Level Rules
  L162-165 (0.1k) ### User Grants
  L166-169 (0.1k) ### Test Login and Logout
  L170-182 (0.2k) ### IdP expression functions & troubleshooting quick reference
  L183-188 (0.2k) ### Auth Token Connection Recovery
L189-192 (0.0k) ## User sources and roles
  L193-205 (0.4k) ### Types
  L206-211 (0.2k) ### Active Directory specifics
  L212-222 (0.1k) ### Database user source — password handling
  L223-230 (0.2k) ### Managing users and roles
  L231-236 (0.1k) ### Verify a User on a User Source
L237-238 (0.0k) ## Security zones and service security
  L239-248 (0.3k) ### Security Zones
  L249-260 (0.3k) ### Service Security (Policies)
L261-264 (0.0k) ## Secrets management
  L265-268 (0.1k) ### Embedded secrets (default, always available)
  L269-285 (0.3k) ### Customized Secrets Management system (opt-in, recommended for production)
  L286-295 (0.3k) ### Secret Provider types (for "Referenced" secrets)
  L296-299 (0.1k) ### Secrets Management Key CLI Tool
  L300-305 (0.1k) ### system.secrets scripting
L306-307 (0.0k) ## Designer and gateway security
  L308-316 (0.3k) ### Gateway General Security Settings (`Platform > Security > General Settings`)
  L317-322 (0.2k) ### Project Security in the Designer
  L323-330 (0.2k) ### API Keys
  L331-334 (0.1k) ### OAuth 2.0 Clients
  L335-344 (0.2k) ### Security Certificates
L345-346 (0.0k) ## Database connections
  L347-363 (0.3k) ### Supported databases (Full Support tier)
  L364-373 (0.3k) ### Connection configuration reference
  L374-382 (0.4k) ### Per-database quirks worth remembering
  L383-399 (0.4k) ### JDBC drivers and translators
  L400-405 (0.1k) ### Monitoring & the internal database
L406-407 (0.0k) ## SQL in Ignition
  L408-413 (0.1k) ### Where SQL shows up
  L414-437 (0.8k) ### Named Queries
  L438-445 (0.1k) ### Query bindings compared
  L446-497 (0.8k) ### Queries in scripting (`system.db`)
  L498-501 (0.2k) ### Query Builder
  L502-517 (0.6k) ### SQL query types (syntax reference)
  L518-575 (0.7k) ### Common task patterns
  L576-583 (0.5k) ### SQL troubleshooting workflow
  L584-595 (0.5k) ### Safe scripting patterns
L596-599 (0.1k) ## Internal database tables
  L600-612 (0.4k) ### Tag History (external SQL historian)
  L613-624 (0.2k) ### Tag History (internal / SQLite-backed historian)
  L625-631 (0.2k) ### Alarm Journal
  L632-642 (0.2k) ### Authentication (Database User Source, default prefix `scada_`)
  L643-650 (0.1k) ### Audit Log
L651-676 (0.9k) ## Gotchas and 8.3 notes
