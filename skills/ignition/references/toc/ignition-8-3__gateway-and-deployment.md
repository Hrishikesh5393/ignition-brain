# TOC: references/ignition-8-3/gateway-and-deployment.md

702 lines, ~19.9k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L7-30 (1.2k) ## Gateway architecture
  L31-43 (0.9k) ### Gateway Backup and Restore
L44-53 (0.2k) ## 8.3 configuration model
  L54-62 (0.3k) ### Two config files, two purposes — don't confuse them
  L63-71 (0.4k) ### The resource collection model: system → external → core → local
  L72-79 (0.1k) ### Resource types
  L80-94 (0.5k) ### Gateway Deployment Modes (new in 8.3)
  L95-116 (0.6k) ### On-disk layout (from the Gateway Folder Structure reference)
  L117-122 (0.3k) ### What this replaces from the old web-UI/IDB model
  L123-136 (0.4k) ### The Gateway REST API and config-as-code (`/openapi`)
  L137-146 (0.3k) ### Implications for containerized / IaC deployments
L147-148 (0.0k) ## Installation and upgrade
  L149-177 (0.7k) ### Installing
  L178-185 (0.3k) ### Installing / upgrading modules
  L186-200 (0.5k) ### ZIP-file installation and pre-configured (cloned) Gateway deployment
  L201-204 (0.1k) ### Ports (see Reference tables for the full table)
  L205-214 (0.3k) ### Upgrading
  L215-240 (1.1k) ### 8.1 → 8.3: what breaks / requires action (see also Gotchas section below for a consolidated list)
L241-244 (0.2k) ## Projects
  L245-248 (0.2k) ### On-disk model
  L249-259 (0.4k) ### Project Inheritance
  L260-267 (0.2k) ### Project properties / settings
  L268-273 (0.4k) ### Import / export
  L274-279 (0.1k) ### Project templates
L280-287 (0.3k) ## Gateway Network
  L288-308 (0.4k) ### General Settings (Network > Gateway Network > Settings)
  L309-312 (0.1k) ### What travels over the GAN
  L313-316 (0.1k) ### Queue management and proxy rules
  L317-322 (0.1k) ### Security Zones / Service Security
L323-326 (0.1k) ## Redundancy
  L327-332 (0.2k) ### Node roles and communication
  L333-338 (0.2k) ### Configuration sync vs. runtime state sync
  L339-347 (0.4k) ### Failover behavior
  L348-351 (0.1k) ### What is/isn't replicated
  L352-359 (0.1k) ### Database considerations for redundancy
L360-363 (0.1k) ## Store and Forward
  L364-371 (0.1k) ### Data flow
  L372-375 (0.1k) ### 8.3 change: multi-threaded engine
  L376-385 (0.2k) ### Engine tuning (per Database Connection: Platform > System > Store & Forward > Edit)
  L386-389 (0.1k) ### Quarantine
  L390-394 (0.1k) ### Disk cache management
  L395-400 (0.1k) ### Legacy data conversion (8.1→8.3)
L401-402 (0.0k) ## Licensing, activation, editions
  L403-406 (0.1k) ### Licensing model
  L407-412 (0.1k) ### Standard (six-character key) licenses
  L413-416 (0.3k) ### Leased licenses (eight-character key)
  L417-420 (0.1k) ### Multiple licenses / Effective vs. Applied
  L421-424 (0.1k) ### Solution Suites
  L425-428 (0.1k) ### Emergency Activation Mode
  L429-439 (0.3k) ### Editions (Standard / Edge / Maker / Cloud)
L440-443 (0.1k) ## Audit log and profiles
  L444-451 (0.2k) ### Profile types
  L452-455 (0.1k) ### Querying the log
  L456-459 (0.1k) ### 8.3 schema note
  L460-465 (0.3k) ### Auditing Actions Reference (selected categories)
L466-469 (0.1k) ## Launchers and Workstation
  L470-479 (0.3k) ### Settings storage
  L480-492 (0.3k) ### Deep links and file associations (new in 8.3)
  L493-496 (0.1k) ### Certificates
  L497-502 (0.1k) ### Pre-configured / deployed launchers
L503-504 (0.0k) ## Reference tables
  L505-529 (0.4k) ### Gateway Port Reference
  L530-552 (0.5k) ### Platform environment variables (subset — see appendix page for full authoritative list)
  L553-556 (0.1k) ### Gateway folder structure (see Configuration model above for the full annotated table)
  L557-585 (0.5k) ### gwcmd (Gateway Command-line Utility) — full option table
  L586-589 (0.2k) ### Docker module identifiers (subset — see appendix page for the full table)
  L590-613 (0.5k) ### Ignition Database Table Reference (condensed)
  L614-624 (0.2k) ### Config file locations, one-line summary
L625-702 (2.1k) ## Gotchas and 8.3 notes
