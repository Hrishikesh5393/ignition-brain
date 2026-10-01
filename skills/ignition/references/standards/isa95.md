# ISA-95 Equipment Hierarchy

**Standard:** ANSI/ISA-95 (Enterprise-Control System Integration), published internationally as
IEC 62264. Part 1 defines models and terminology; Part 2 defines the object attributes; Part 3
covers activities of manufacturing operations management. The equipment hierarchy model is in
ISA-95 Part 1 (see Part 1 §5, "Hierarchy models", and the equipment model in Part 1 §6 /
IEC 62264-1).

This doc is the **global / universal** layer: it states the model and the options. The ISA-95
levels *this* deployment actually models, and the concrete tag-path / UDT mapping, live in
the project equipment hierarchy.

---

## The role-based equipment hierarchy

ISA-95 Part 1 defines a hierarchy of **equipment** grouped by the role it plays in operations.
Top three levels are common to every industry; the lower levels have three parallel variants
depending on the production style.

| Level | Name | Meaning | Typical granularity |
|-------|------|---------|---------------------|
| 1 | **Enterprise** | The company / legal entity. Sets what products are made and where. | One per business |
| 2 | **Site** | A physical or geographic location (a plant, a campus). Production scheduling boundary. | A factory, a substation campus, a wind farm |
| 3 | **Area** | A physical/logical subdivision of a site by major function. | "Utilities", "Packaging", "Water treatment", "Block A" |
| 4 | **Work Center** | Where work happens; the operational rollup unit. Variants below. | A line, a cell, a unit |
| 5 | **Work Unit** | The lowest-level equipment that does the work. Variants below. | A machine, a pump skid, an inverter |

### Level 4 / 5 variants (ISA-95 Part 1 equipment model)

| Production style | Level 4 (Work Center) | Level 5 (Work Unit) | Example |
|-----------------|-----------------------|---------------------|---------|
| **Continuous / process** | Process Cell | Unit | Distillation train → reboiler unit |
| **Batch** (aligns with ISA-88) | Process Cell | Unit | Reactor cell → reactor unit |
| **Discrete / repetitive** | Production Line | Work Cell → (Production) Unit | Bottling line → capper cell |
| **Storage / movement** | Storage Zone | Storage Unit | Tank farm → tank |

"Work Center" is the generic ISA-95 term; "Process Cell", "Production Line", "Storage Zone" are
its specialisations. A site may mix styles across areas.

Additional levels *below* Work Unit (**Equipment Module**, **Control Module**) come from ISA-88
and are used for batch; ISA-95 lets you nest equipment freely under Work Unit for this.

---

## Equipment hierarchy vs physical asset hierarchy

These are **two different trees over the same plant** and must not be conflated:

| | Equipment (operational) hierarchy | Physical asset hierarchy |
|--|-----------------------------------|--------------------------|
| Groups by | Role in production / the operational rollup | Physical containment, maintenance, P&ID |
| Answers | "What is this line's OEE / state / alarm rollup?" | "What spare part, what work order, what loop drawing?" |
| Owner | Operations, MES, SCADA | Maintenance / CMMS / EAM, engineering |
| Reference | ISA-95 Part 1 equipment model | ISO 14224 / a plant breakdown structure, the P&ID |

A pump that feeds two work centers appears **once** physically but its *measurements* may roll
up into two operational parents. Model the equipment hierarchy for SCADA; reference asset IDs
as attributes, don't reshape the tree around them.

---

## Mapping onto an Ignition deployment — principle

The ISA-95 hierarchy is the backbone for how tags, UDTs and views are organised. State the
principle here; the concrete scheme is in
the project equipment hierarchy and
the project naming convention.

| ISA-95 concept | Ignition mechanism | Principle |
|----------------|--------------------|-----------|
| Enterprise / Site | **Tag provider** choice, or the top folder(s) | A provider boundary usually tracks a site or a gateway's span of control; multi-site fleets often get a provider per site or use the gateway network. |
| Area → Work Center → Work Unit | **Tag folder depth** | Folder nesting mirrors the hierarchy levels the project adopts — one folder segment per modelled level, consistently, so an indirect binding can walk the path. |
| Work Unit (and equipment modules under it) | **UDT instance**; nested UDTs for sub-equipment | A Work Unit = one UDT instance. Sub-equipment (a VFD inside a pump skid) = a nested UDT member, not a flattened prefix. |
| Level path to an instance | **UDT parameters** (`Area`, `Line`, `Equipment`) + indirect tag bindings | The path is carried as parameters so views bind indirectly (`[default]{Area}/{Line}/{Equipment}/...`) rather than hard-coding. |
| Work Center / Area | **Perspective page & view hierarchy**, view params | Page URL structure and view nesting follow the same levels; an Area overview embeds Work Center views, which embed Work Unit views. |
| Operational rollup (state, alarm summary, OEE) | Roll-up tags / expression tags at the Work Center and Area folders | Each level above Work Unit gets summary tags aggregating its children. |

Depth guidance: model every level that carries meaning for *this* site and skip none of them
inconsistently. A level with only one child today is still worth a folder if the site plans to
add siblings.

---

## When ISA-95 applies

> **Applies to essentially every Ignition deployment.** Any SCADA/HMI system that models plant
> equipment benefits from the role hierarchy for tag/UDT/view organisation and for MES/ERP
> integration. It is *most* load-bearing when: the gateway integrates with an MES or ERP;
> multiple sites or areas roll up to enterprise KPIs; OEE / batch / genealogy is in scope.
> Even a single-skid project should pick its levels deliberately rather than inventing an
> ad-hoc tree.

---

## agent rules

> - **Read the project equipment hierarchy
>   before creating tag folders, UDTs, or view structure.** It names the levels this site
>   models and the exact path shape. Do not invent a hierarchy.
> - **One folder segment per modelled level, every time.** Don't skip Area for some equipment
>   and include it for others.
> - **The hierarchy lives in folder structure + UDT parameters, never only in the tag name.**
>   `PUMP_101_UTIL_AREA2_RUN` as a flat name in the root folder is a smell.
> - **A Work Unit is a UDT instance; its sub-equipment are nested UDT members.** Don't flatten
>   sub-equipment into member-name prefixes.
> - **Carry the level path as UDT parameters** so views bind indirectly.
> - **Model the operational rollup, not the P&ID.** Reference asset/loop numbers as attributes.
> - Cross-check datatypes against [`iec-61131.md`](./iec-61131.md), UDT patterns against
>   [`udt-design.md`](./udt-design.md), naming against [`tag-naming.md`](./tag-naming.md).

---

## Smells

| Smell | Why it bites |
|-------|--------------|
| Hierarchy encoded only in tag names (flat folder, long delimited names) | Indirect bindings can't walk it; renames are global find-replace; UDT reuse is impossible. |
| Levels skipped inconsistently (Area present for line 1, absent for line 2) | Every generic browse / rollup / binding needs special-casing; MES mapping breaks. |
| Equipment model mirrors the P&ID / physical containment instead of the operational rollup | Alarm and state rollups don't match how operators think; OEE aggregation lands on the wrong nodes. |
| Sub-equipment flattened into prefixes (`VFD_Pump1_...`) instead of nested UDTs | No type reuse for the VFD; can't roll up "all VFDs". |
| One giant UDT per Work Center instead of a Work Unit UDT reused N times | Parameter explosion, no instance-level overrides, unmaintainable. |
| Tag provider boundary drawn on a whim rather than a site / span-of-control boundary | Confusing cross-provider references, backup/restore and security scoping get messy. |

---

## See also

- Siblings: [`iec-61131.md`](./iec-61131.md) · [`iec-61850.md`](./iec-61850.md) ·
  [`iec-62443.md`](./iec-62443.md) · [`tag-naming.md`](./tag-naming.md) ·
  [`udt-design.md`](./udt-design.md)
- Project layer: the project equipment hierarchy ·
  the project naming convention ·
  the project UDT catalogue
