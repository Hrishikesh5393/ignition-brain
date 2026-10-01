# TOC: references/gateway/resource-formats.md

537 lines, ~6.7k tokens. Line ranges are 1-based inclusive; `Read` with offset=start, limit=end-start+1.

L12-38 (0.4k) ## 1. Where a project lives
L39-77 (0.5k) ## 2. `resource.json` — the resource manifest
L78-91 (0.1k) ## 3. `project.json`
L92-128 (0.5k) ## 4. Perspective view — `com.inductiveautomation.perspective/views/<Name>/`
L129-169 (0.4k) ## 5. `page-config` — `com.inductiveautomation.perspective/page-config/config.json`
L170-204 (0.4k) ## 6. Perspective binding JSON
  L205-231 (0.3k) ### 6a. `query` binding
  L232-260 (0.3k) ### 6b. `http` binding
  L261-311 (0.5k) ### 6c. `tag-history` binding
L312-335 (0.4k) ## 7. WebDev python resource — `com.inductiveautomation.webdev/resources/<route>/`
L336-397 (0.9k) ## 8. Gateway timer script — `ignition/timer/<Name>/`
L398-412 (0.1k) ## 9. The project-relative view-path rule
L413-442 (0.4k) ## 10. THE FSYNC TRAP (critical — read before any gateway-side write)
  L443-450 (0.1k) ### Gateway file locks
L451-497 (0.7k) ## 11. Write protocol (summary — full loop in `workflow.md`)
L498-520 (0.3k) ## 12. Named query — `ignition/named-query/<Name>/`
L521-537 (0.3k) ## 13. Alarm notification pipeline — `com.inductiveautomation.alarm-notification/alarm-pipelines/<Name>/`
