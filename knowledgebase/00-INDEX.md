---
title: Ignition 8.3 Knowledge Base - Index
description: Complete Ignition 8.3 reference for development, debugging, deployment
---

# Ignition 8.3 Complete Knowledge Base

**Status:** Building comprehensive AI-readable reference
**Coverage:** Components, Scripting, Platform, Architecture, Debugging, Deployment, Modules

See also: [[README]] (project overview) · [[KNOWLEDGE-GRAPH]] (learning paths, glossary, use-case chains)

## Navigation

### Core Architecture
- [[01-ARCHITECTURE-OVERVIEW]] - Platform layers, design patterns, data flow
- [[02-SYSTEM-ARCHITECTURES]] - Deployment models (Basic, Hub-Spoke, Enterprise, Cloud, Edge)
- [[84-CLUSTERING-HA-ARCHITECTURE]] - Master/Backup redundancy, failover, state sync, network topology
- [[85-CLUSTERING-HA-CONFIGURATION]] - Cluster setup, tag sync, DB failover, DR procedures
- [[04-RESOURCE-MODEL]] - **Verified from the install.** Every project resource type, its module id, its on-disk files, `resource.json` and `project.json` format, and how to re-derive the registry

### Components & UI
- [[16-PERSPECTIVE-SCHEMA-TRUTH]] - **Verified from the install.** Where the shipped schemas live, the style precedence chain, the flex prop-to-CSS map, binding and transform schemas, session props, and the full 82-component inventory
- [[10-PERSPECTIVE-OVERVIEW]] - Modern web-based UI system, responsive design
- [[11-COMPONENTS-PALETTES]] - Component categories (Chart, Container, Display, Input, etc.)
- [[12-COMPONENT-REFERENCE]] - 15+ component types with props, bindings, events
- [Component Index](Components/00-Component-Index.md) - Per-component deep-dive docs (56 of the 82 shipped components; gaps listed in 16-PERSPECTIVE-SCHEMA-TRUTH)
- [[13-TEMPLATES-REUSE]] - Embedded views, parameterized components, reusable patterns

### Tags & Data
- [[20-TAGS-FUNDAMENTALS]] - Tag types (Standard, OPC, Expression, SQL, Memory)
- [[21-BINDINGS]] - Property bindings, tag references, dynamic updates, events
- [[22-EXPRESSIONS]] - Expression language syntax, operators, functions
- [[23-DATABASE-INTEGRATION]] - SQL queries, prepared statements, transactions, optimization
- [[24-OPC-UA-DEVICES]] - OPC protocol, device communication, tag quality
- [[27-PLATFORM-UDTS-QUERIES]] - User-Defined Types, UDT instances, Named Queries, query composition, parameterization
- [[90-DATABASE-ADVANCED-OPTIMIZATION]] - Query tuning, indexing, connection pooling, historian optimization, per-database tuning
- [[91-DATABASE-FAILOVER-REPLICATION]] - Master-slave redundancy, failover automation, read replicas, sync monitoring

### Scripting & Automation
- [[30-SCRIPTING-OVERVIEW]] - Python scripting scopes (Gateway, Vision, Perspective)
- [[31-SYSTEM-FUNCTIONS]] - 40+ system.* categories (database, tags, network, alarms, users, etc.)
- [[32-SCRIPTING-PATTERNS]] - Common patterns, batch operations, error handling, async code

### Alarming & Monitoring
- [[40-ALARMS-FUNDAMENTALS]] - Alarm creation, escalation, acknowledgment, notification
- [[41-ALARM-PIPELINE-SCHEMA-TRUTH]] - **Verified from the install.** Real `PipelineDescriptor` schema, the 10 real block types, and 2 guessed-but-nonexistent block types to stop reaching for

### Security & User Management
- [[50-SECURITY-MODEL]] - Authentication, authorization, roles, permissions, SSL/TLS
- [[KNOWLEDGE-GRAPH]] - Document relationship map and navigation guide

### Installation & Operations
- [[60-INSTALLATION-SETUP]] - Installation steps, system requirements, first-time setup
- [[61-GATEWAY-MANAGEMENT]] - User/role management, licensing, backup/restore, monitoring
- [[51-PLATFORM-SECURITY-COMPLETE]] - Lockout policies, session timeout, API keys, audit logging, auth sources, certificates
- [[87-GATEWAY-OPERATIONS-RUNBOOK]] - Startup/shutdown, log rotation, backup verification, diagnostics, upgrades, emergency restart
- [[62-LOGGING-DIAGNOSTICS]] - Log locations, reading logs, common errors, debugging
- [[83-PERFORMANCE-TUNING]] - Query optimization, caching, monitoring bottlenecks

### Modules & Extensions
- [[70a-MODULES-OVERVIEW]] - All modules (Perspective, OPC-UA, SQL, Reporting, MES, MQTT)
- [[70b-MODULES-INDEX-MASTER]] - Canonical module catalog with dependencies & licensing
- [[71-REPORTING-MODULE]] - Report design, parameters, data sources, export formats
- [[72-REPORTING-SHAPE-MODEL]] - **Verified from the install.** The ReportMill shape/XML architecture behind the report canvas: tag registry, universal shape attributes, table/chart shapes, the annotation-driven property-panel layer
- [[88-OPC-UA-SERVER-CONFIGURATION]] - Running Ignition as OPC-UA server, namespaces, methods, security policies, endpoint config
- [[89-OPC-UA-ADVANCED-PATTERNS]] - Certificates, redundancy, aggregation, PubSub, large-scale subscriptions, troubleshooting
- [[92-MOBILE-MODULE-PERSPECTIVE]] - Mobile Perspective architecture, responsive design, touch interactions, offline, sensors, notifications, distribution
- [[93-MOBILE-MODULE-OPERATIONS]] - Install/update, enrollment, performance, security, troubleshooting, push notifications, testing

### Troubleshooting & Optimization
- [[81-GOTCHAS-BUGS]] - Common mistakes, workarounds, scope violations, performance pitfalls
- [[82-DEBUGGING-GUIDE]] - Systematic debugging, finding root causes, tools, solutions

### Quick Reference
- [[QUICK-REFERENCE]] - Copy-paste code snippets for most common tasks

## Quick Refs
- Function quick lookup: See [[31-SYSTEM-FUNCTIONS]]
- Component properties: See [[12-COMPONENT-REFERENCE]]
- Expression syntax: See [[22-EXPRESSIONS]]
- Common errors: See [[82-DEBUGGING-GUIDE]]

---

## Meta / Build Process (not Ignition content - KB maintainers only)

These describe how the KB itself was built, not Ignition. An AI learning Ignition should not traverse into this section; kept here only so nothing is a true orphan.

- [[PROGRESS]] - Build status, session log
- [Components/ORGANIZATION_SUMMARY](Components/ORGANIZATION_SUMMARY.md) - How the Components/ folder was organized
- [Components/_COMPONENT_TEMPLATE](Components/_COMPONENT_TEMPLATE.md) - Template for authoring new component docs
- [LINKAGE-REPAIR-PLAN.json](LINKAGE-REPAIR-PLAN.json) - Source data for [[KNOWLEDGE-GRAPH]] generation

---
**Last Updated:** 2026-08-15 (install-verified pass: +41-ALARM-PIPELINE-SCHEMA-TRUTH (real block registry, 10 confirmed types); corrections to 28-PLATFORM-TRANSACTIONS-SFCS (SFC/Transaction Group payloads are XML not JSON, real 15-value ChartStateEnum, real `system.sfc.startChart` replacing the invented `runChart`). Previous pass 2026-08-14: +04-RESOURCE-MODEL, +16-PERSPECTIVE-SCHEMA-TRUTH, +72-REPORTING-SHAPE-MODEL, corrections to FlexContainer, CoordinateContainer, and 71-REPORTING-MODULE; component count corrected 81 -> 82 for the Reporting module's Report Viewer)
**Source:** the local Ignition 8.3.7 install (jars, client bundle, project folders) + docs.inductiveautomation.com/docs/8.3 + local research
**Coverage:** ~90% complete (enterprise-critical gaps filled)
