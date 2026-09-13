---
title: Alarm Notification Pipeline - Schema Truth
description: The real PipelineDescriptor/block schema, verified from alarm-notification-common-7.3.7.jar
---

> **Skill level:** 200 · **Read first:** [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md), [04-RESOURCE-MODEL](04-RESOURCE-MODEL.md)
> **You are here:** [00-INDEX](00-INDEX.md) > 41-ALARM-PIPELINE-SCHEMA-TRUTH

# Alarm Notification Pipeline - Schema Truth

Install-verified 2026-08-15 against `data\jar-cache\com.inductiveautomation.alarm-notification\*-alarm-notification-common-7.3.7.jar` (`javap -p`), a **real Designer-built pipeline** (`AHU_AlarmLog`, Start -> Script block, built by the user), and a **real reference pipeline from Inductive Automation's own IADemo demo project** (`Pipeline`, Start -> Notification block, Email profile). Both decoded with the same `XMLDeserializer`/`XMLSerializer` tooling built for the Reporting module. Everything marked "confirmed" below is observed-on-disk, not inferred from bean names.

## Format: XML via `ignition.common.xmlserialization` - CORRECTED 2026-08-15, do not hand-author

**This was wrong when first written.** The original research pass found no Gson usage anywhere in the alarm-notification jars and concluded "must be plain JSON, same safe category as Perspective." That reasoning was incomplete - it never actually traced the real load call. A live hand-authored `pipeline.json` was deployed, and Ignition threw `SerializationException: ... SAXParseException; Premature end of file` trying to load it - a dead giveaway an XML parser was handed non-XML.

Traced properly this time: `AlarmPipelineManagerImpl.class` (in `alarm-notification-gateway-7.3.7.jar`) calls
`XMLDeserializer.deserialize([B)` directly on the pipeline resource's bytes (`com.inductiveautomation.ignition.common.xmlserialization.deserialization.XMLDeserializer` - confirmed via `javap -p -c`, with an adjacent string constant `"Error deserializing PipelineDescriptor from ProjectResource '%s'."` pinning the call to pipeline loading specifically). **This is the exact same framework used by Reporting and Transaction Groups** - alarm pipelines belong in that same "do not hand-author, build in Designer" category, not the safe plain-JSON category.

**Lesson for next time:** "no Gson found" only rules out one serialization mechanism. This platform has at least two generic, non-Gson serialization frameworks in active use (`ignition.common.xmlserialization`, and whatever Reporting-adjacent binary path was found earlier) - the only way to actually confirm a format is to trace the real load call (`grep` the loading class for `XMLDeserializer`/`ObjectInputStream`/`Gson` usage, `javap -c` it, follow the bytecode), the way the Transaction Group research correctly did and this alarm-pipeline research initially did not. A absence-of-evidence conclusion ("didn't find X, so it must be Y") is not the same as tracing the real path - the whole point of this session's methodology, missed once here.

## Resource type

`com.inductiveautomation.ignition.alarming.common.pipelines.PipelineDescriptor` (fuller package path than first recorded - confirmed from the real decoded root class), resource type `com.inductiveautomation.alarm-notification` / `alarm-pipelines`. On disk: `<Project>/com.inductiveautomation.alarm-notification/alarm-pipelines/<PipelineName>/`, `resource.json` + **`data.bin`** (confirmed real filename from a live example - the earlier `pipeline.json` guess was wrong).

## Real structure: not plain bean fields - a generic property-bag config object

`PipelineDescriptor` does not persist as simple named fields. It has one real field, `rawValueMap: Map<String, Object>`, and everything lives in there as `com.inductiveautomation.ignition.common.config.BasicProperty`/`BasicPropertySet` entries - the same generic `Property<T>` config system used elsewhere on the platform. Top-level keys observed in a real pipeline: `startingBlock`, `blocks`, `enabled`, `ui-size` (canvas dimensions, e.g. `800x600` - canvas layout IS persisted, just not as a dedicated bean field, correcting the earlier "no canvas-position fields found" note below). `dropoutConditions`/`fallbackPipeline`/`projectName` were not present in this simple pipeline - likely omitted-when-default rather than always-required.

**`startingBlock` is a full embedded `BasicPropertySet` object, not a UUID reference** (closes the earlier open question - both were plausible, this is the real answer). It carries its own `ui-location` (canvas point) and `outputId` (UUID) - the Start node is a real persisted object whose only job is to point at the first real block via `outputId`.

**`blocks` is an array of `BasicPropertySet` objects**, one per block. Each carries `blockId` (UUID), `ui-location` (canvas point - **confirmed real**, contradicting the earlier note that no position data existed on these beans; it's just stored generically, invisible to a plain `javap -p` scan), `factoryId` (confirmed matches the constant table below exactly, e.g. `com.inductiveautomation.scriptableBlockFactory`), and whatever type-specific properties that block has (e.g. `script` for a Script block).

**Linking is confirmed**: `startingBlock`'s `outputId` UUID matches the first block's `blockId` UUID exactly - a real linked graph via UUID reference, as suspected, now confirmed on real data.

**Script block body is confirmed body-only, no `def` line** - the exact same convention as Perspective event scripts and script transforms (a cross-module consistency worth remembering): a script pasted as
```python
def handleAlarm(self, event):
	logger = system.util.getLogger("AHU.Alarms")
	logger.info(...)
```
persists with only the two indented body lines, `def handleAlarm(self, event):` stripped entirely. The handler re-adds the signature at execution time.

## Common block properties (every block has these)

`factoryId` (String - the block-type discriminator, confirmed real via the decoded example), `blockId` (UUID), `outputId` (UUID pointing at the next block's `blockId`), `ui-location` (canvas point, confirmed real).

## The real block types - exhaustive as of 8.3.7, ten total

Block registration is generic (`ReflectionLookupPipelineBlockFactory(String id, Class<...> blockClazz)`), so `factoryId` is a free-form registry key in principle, but these ten are the complete real list shipped in this module - **nothing else exists**:

| Block | `factoryId` | Extra properties |
|---|---|---|
| Notification | `com.inductiveautomation.notificationBlockFactory` | `blockVersion` (int), `throttlingEnabled`, `throttlingDelay`, `throttlingFrequency`, `rosterType`, `roster` (String roster name - real key, corrects an earlier `onCallRoster` guess), `ignoreSchedule`, `notificationProfiles` (String[], confirmed real - the plural form), `timeBetweenNotifications`, `settingsFor_<ProfileName>` (per-profile settings, confirmed real - see example below) |
| Delay | `com.inductiveautomation.delayBlockFactory` | `delay` (Long, ms) |
| Expression | `com.inductiveautomation.expressionBlockFactory` | `expression`, plus its own `trueOutput`/`trueOutputId` and `falseOutput`/`falseOutputId` - branches independently of the common `outputId` |
| Switch | `com.inductiveautomation.switchBlockFactory` | `mode` (enum `SwitchMode`), `expression`, `outputTable` (case -> outputId mapping), default case key literal `_default_` |
| Jump | `com.inductiveautomation.jumpBlockFactory` | `pipelineName` - jumps to a different pipeline |
| Property Setter | `com.inductiveautomation.propertySetterBlockFactory` | `propertyId`, `expression`, `scope` (enum `PropertyScope`) |
| Script | `com.inductiveautomation.scriptableBlockFactory` | `script` (String) - fixed handler function name **`handleAlarm`** |
| Splitter | `com.inductiveautomation.splitterBlockFactory` | `outputCount` (Integer) - fans out to N outputs |
| Event Stream | `com.inductiveautomation.eventStreamBlockFactory` | `eventStreamPath`, `message` |
| No-Op (Start) | (no separate properties class; has a hardcoded static `BLOCK_ID`) | none - the implicit entry block the Designer's "Start" node represents |

**Confirmed NOT real** (don't reach for these - they don't exist in 8.3.7, despite being plausible-sounding): "On/Off Ramp Filter" block, "Add Note" block, "Shelve" block (shelving exists only as the `DropoutCondition.OnShelve` enum value on the pipeline itself, not as a pipeline block).

## Practical gotcha: notification profiles are a separate prerequisite

A `NotificationBlock` references a profile by name (`notificationProfile`/`notificationProfiles`) but does not create one. Check `data\email-profiles\` and the gateway's `com.inductiveautomation.alarm-notification` config namespace before assuming a Notification block has anywhere to actually send - on a fresh gateway this is commonly empty, and the block will have nothing real to reference until a profile is configured separately.

## Real NotificationBlock example (from Inductive Automation's own IADemo reference project, `Pipeline`)

Decoded a second real pipeline, this one with an actual `NotificationBlock`. Corrects one guessed field name and reveals a real pattern that wasn't guessable from bean names alone:

- `roster` (String, e.g. `"Operators"`) - **not** `onCallRoster` as originally guessed from the bean's getter/setter name. `rosterType`/`throttlingEnabled`/`ignoreSchedule`/`timeBetweenNotifications` were all absent in this example - likely default-omitted, still real fields per the bean scan, just not exercised here.
- `notificationProfiles` = `["Email"]` (String array, confirmed the plural form is what's actually used).
- `blockVersion` = `2` (int).
- **`settingsFor_<ProfileName>`** - a dynamically-keyed property (e.g. `settingsFor_Email`) holding a nested `BasicPropertySet` of per-profile field overrides. Each entry is keyed by a `BasicNotificationProfileProperty` (itself carrying `name`, `displayName` (`LocalizedString`), `category`, `defaultValue`, `clazz`) mapped to the actual override value - e.g. `fromAddress` -> `"alarms@inductiveautomation.com"`. This is how a Notification block's per-profile settings (From Address, etc.) are actually stored - one property key per configured profile, not a flat/fixed field set.

## What's still unverified

- `outputTable`'s exact serialized shape for `SwitchBlock` (no example with a Switch block decoded yet).
- Whether a multi-block pipeline's `blocks` array entries reference each other purely by `outputId` -> `blockId`, or whether branch-heavy blocks (Expression/Switch/Splitter) add anything beyond their own extra output-id-shaped properties - only a single-block pipeline has been decoded so far.
- The exact `BasicProperty`/`BasicPropertySet` XML tag grammar in general (`<o-ctor>`, `<o-c m="put">`, `<point>`, `<uuid>`, `<dim>` etc were all observed and are usable as a template, but the full generic grammar of this config system wasn't independently re-derived from the shared platform code, only read off this one real example).

**Still build pipelines in the Designer**, even though the format is no longer a mystery. This is XML through the same generic `ignition.common.xmlserialization` framework as Reporting and Transaction Groups - decoding a real example (as done here) is reliable, but hand-*writing* a new one from this template carries the same category of risk that caused real failures on the Reporting side. The tables above are for reading Designer output and understanding what a pipeline contains, not yet proven safe for writing from scratch.

---

## See Also

**Prerequisites:** [40-ALARMS-FUNDAMENTALS](40-ALARMS-FUNDAMENTALS.md), [04-RESOURCE-MODEL](04-RESOURCE-MODEL.md)

[Back to INDEX](00-INDEX.md) - [Knowledge Graph](KNOWLEDGE-GRAPH.md)
