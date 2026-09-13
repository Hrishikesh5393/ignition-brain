---
name: project-ignition-component-library
description: "Custom Ignition Perspective component library built via the Module SDK - build/sign toolchain, the two-layer design method, and which components are locked"
metadata: 
  node_type: memory
  type: project
  originSessionId: 73fda676-3a9b-4234-851f-8c4403970773
  modified: 2026-08-07T20:10:51.967Z
---

Building a custom Perspective component library as real Java SDK modules (not templates), started 2026-08-07. Goal is industrial symbols Ignition doesn't ship.

**Toolchain (all working, all free):**
- SDK examples cloned at `C:\ignsdk\ignition-sdk-examples`, working project is `perspective-component-minimal`. Cloned to a SHORT path on purpose - Windows MAX_PATH breaks the clone under a deep temp dir.
- JDK: Temurin 17 at `C:\Program Files\Eclipse Adoptium\jdk-17.0.20.8-hotspot` (matches the gateway's own JVM). Must set `JAVA_HOME` per shell; POSIX-style path in bash.
- Self-signed cert at `C:\ignsdk\private\` (`mykeys.p12` + `certificates.p7b`, alias `ahu_dev_module`, pass `changeit`). Generated free with keytool + openssl.
- Build: `./gradlew clean signModule --keystoreFile=... --keystorePassword=... --certFile=... --certAlias=... --certPassword=...` - the Gradle plugin wants **CLI flags**, it ignores the `sign.props` file the README describes. Task is `signModule`, not `buildModule`. Also had to flip `skipModlSigning.set(false)` in `build.gradle.kts`.
- Output `.modl` copied to Desktop; user installs via Gateway → Config → Modules. Cert trusted once, quiet upgrades after.
- One `.modl` holds many components - register each `ComponentDescriptor` in both the gateway and designer hooks, plus a `ComponentMeta` in the JS.

**The design method that works - two explicit renderer layers:**
1. *Engineering geometry* - real catalogue dimensions, decides what is TRUE, drives all proportions.
2. *Visual identity* - decides what is DRAWN. Working parts forward, structure ghosted. "You draw an engine by its crankshaft, not its block."

Research process: manufacturer **datasheet PDFs** are the goldmine (pypdf extracts them fine). CAD/STEP/DWG/Revit are binary and unusable; section drawings are raster inside PDFs. Generic web images produce plausible-but-wrong geometry - every time I skipped the datasheets the proportions were badly off.

**Archive lives at `C:\docs\ignition\` (README carries every verified spec table).** Module rebuilt 2026-08-08: 5 components registered (Image, Damper, HeatingCoil, Filter, WindTurbine), shared 440x340 canvas + palette + type scale, nav-tree icons (see [[feedback_ignition_component_icons]]), one shared 3D render kit in the JS. Verify the component JS offline with `node C:/docs/ignition/component-library/generators/render_module.js` - it runs the real module javascript against the real props schemas and exits non-zero on a throw.

**Locked component drafts:**
- Damper - Ruskin CD36 / Nailor 2000 specs. 5" hat channel, 6" blades on 5.5" centres, hex axles, concealed linkage.
- Heating coil - 5/8" tube, 1.5" centres, 1.299" staggered rows (= 1.5 × cos30). Serpentine forward, fin pack ghosted.
- Filter - per-class ΔP thresholds (G4 0.12→1.00", F7 0.27→1.50", HEPA 1.00→2.00"), dust loading visual.
- Wind turbine - real power curve, spin duration is literally `60/rpm` seconds.

**Open decisions deferred to the module rebuild:** shared design system (canvas/palette/type scale - user flagged inconsistency), and whether the turbine's power-curve inset ships in the component.

**Ruled out deliberately:** fan (its tags ARE motor tags - `ia.symbol.motor` covers it), humidifier (≈ valve), VFD (≈ motor), silencer/casing (no signal). User's rule: don't build anything without a real tag behind it. See [[feedback_ignition_check_gateway_logs]].
